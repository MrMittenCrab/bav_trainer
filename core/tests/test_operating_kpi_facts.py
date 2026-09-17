"""Company-operated store KPI source-to-model handoff."""

from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from core.data.filing import PresentationRole, SourceRef, SupplementalFact
from core.data.historical_operating_kpis import (
    METRIC_STORE_COUNT,
    POPULATION_COMPANY_OPERATED,
    STORE_COUNT_FACT_TYPE,
)
from core.data.interface import (
    FinancialPeriod,
    HistoricalManagementKpiObservation,
    HistoricalOperatingKpiData,
    HistoricalOperatingKpiObservation,
    StandardizedFinancials,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_json import extracted_filing_to_payload, load_extracted_filing
from core.ingestion.filing_reconciler import SupplementalObservation, reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.filing_validator import validate_extracted_filing
from core.ingestion.operating_kpi import select_operating_kpi_facts
from core.tests.test_filing_reconciler import _filing, _validated

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
FIXTURE = (
    ROOT
    / "core"
    / "tests"
    / "fixtures"
    / "operating_kpis"
    / "lululemon_company_operated_stores.json"
)
PREPARE = ROOT / "scripts" / "prepare_lululemon_operating_kpi_filings.py"

P2022 = date(2022, 1, 30)
P2023 = date(2023, 1, 29)
P2024 = date(2024, 1, 28)
P2025 = date(2025, 2, 2)
P2026 = date(2026, 2, 1)
ADMIT_2022 = (P2022,)

INDEPENDENT_STORE_TOTALS = {
    P2022: 574,
    P2023: 655,
    P2024: 711,
    P2025: 767,
    P2026: 811,
}
EXPECTED_SELECTION = {
    P2022: (2022, "comparative", "sole_source_observation", 7),
    P2023: (2023, "comparative", "later_audited_presentation", 11),
    P2024: (2024, "comparative", "later_audited_presentation", 11),
    P2025: (2025, "comparative", "later_audited_presentation", 11),
    P2026: (2025, "current_period", "sole_source_observation", 11),
}
EXPECTED_SOURCE_NOTES = {
    P2022: "Company-Operated Stores",
    P2023: "Number of company-operated stores by market",
    P2024: "Number of company-operated stores by market",
    P2025: "Number of company-operated stores by market",
    P2026: "Number of company-operated stores by market",
}
REPORTED_STORE_LABEL = "Total company-operated stores"
_OMIT = object()
LABEL_MUTATIONS = (
    pytest.param(_OMIT, id="omitted"),
    pytest.param(None, id="null"),
    pytest.param("", id="empty"),
    pytest.param(" \t ", id="whitespace"),
)
NOTE_CONTEXTS = (
    pytest.param("Company-Operated Stores", id="note-populated"),
    pytest.param(_OMIT, id="note-absent"),
)
NON_STRING_LABELS = (
    pytest.param(123, id="int-123"),
    pytest.param(1.5, id="float-1.5"),
    pytest.param(0, id="int-0"),
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param({"x": 1}, id="nonempty-object"),
    pytest.param({}, id="empty-object"),
    pytest.param([1], id="nonempty-array"),
    pytest.param([], id="empty-array"),
)


def _store(
    period: date,
    value: float,
    *,
    page: int = 7,
    role: PresentationRole = PresentationRole.CURRENT_PERIOD,
    unit: str = "stores",
    label: object = REPORTED_STORE_LABEL,
    note: str = "Company-Operated Stores",
) -> SupplementalFact:
    return SupplementalFact(
        fact_type=STORE_COUNT_FACT_TYPE,
        period=period,
        value=value,
        status="reported",
        source=SourceRef(
            page=page,
            note=note,
            label=label,  # type: ignore[arg-type]
        ),
        presentation_role=role.value,
        unit=unit,
    )


def _label_text(label: object) -> object:
    return "" if label is _OMIT else label


def _note_text(note: object) -> str:
    return "" if note is _OMIT else str(note)


def _mutate_serialized_source(source: dict, *, label: object, note: object) -> dict:
    mutated = dict(source)
    if label is _OMIT:
        mutated.pop("label", None)
    else:
        mutated["label"] = label
    if note is _OMIT:
        mutated.pop("note", None)
    else:
        mutated["note"] = note
    return mutated


def _prepare_augmented(tmp_path: Path) -> Path:
    dest = tmp_path / "augmented"
    completed = subprocess.run(
        [
            sys.executable,
            str(PREPARE),
            "--extracted",
            str(EXTRACTED),
            "--dest",
            str(dest),
            "--facts",
            str(FIXTURE),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return dest


def _validated_augmented(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    validated = []
    for name in (
        "LULU_FY2022.json",
        "LULU_FY2023.json",
        "LULU_FY2024.json",
        "LULU_FY2025.json",
    ):
        filing = load_extracted_filing(dest / name)
        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        validated.append((filing, report))
    return dest, validated


def _kpi_model_observation(
    period: date,
    value: float,
    *,
    unit: str = "stores",
    metric: str = METRIC_STORE_COUNT,
    population: str = POPULATION_COMPANY_OPERATED,
) -> HistoricalOperatingKpiObservation:
    return HistoricalOperatingKpiObservation(
        metric=metric,
        population=population,
        period=period,
        value=value,
        unit=unit,
    )


def _fin_with_operating_kpis(
    *observations: HistoricalOperatingKpiObservation,
    extra_periods: list[date] | None = None,
    units: str = "USD in Thousands",
    include_payload: bool = True,
    management: list[HistoricalManagementKpiObservation] | None = None,
) -> StandardizedFinancials:
    if extra_periods is not None:
        dates = extra_periods
    else:
        dates = []
        seen: set[date] = set()
        for item in (*observations, *(management or ())):
            if item.period not in seen:
                dates.append(item.period)
                seen.add(item.period)
    if not dates:
        dates = [date(2025, 12, 31)]
    payload = (
        HistoricalOperatingKpiData(
            observations=list(observations),
            management_observations=list(management or ()),
        )
        if include_payload
        else None
    )
    return StandardizedFinancials(
        ticker="T",
        company_name="Co",
        currency="USD",
        units=units,
        jurisdiction="US",
        periods=[
            FinancialPeriod(end_date=period, label=f"FY{period.year}")
            for period in dates
        ],
        historical_operating_kpis=payload,
    )


def test_absent_and_null_operating_kpis_are_equivalent():
    from core.tests.test_historical_segment import _base_payload

    payload = _base_payload()
    fin = standardized_from_payload(payload)
    assert fin.historical_operating_kpis is None
    out = standardized_to_payload(fin)
    assert "historical_operating_kpis" not in out
    payload["historical_operating_kpis"] = None
    assert standardized_from_payload(payload).historical_operating_kpis is None
    assert "historical_operating_kpis" not in standardized_to_payload(
        standardized_from_payload(payload)
    )


def test_empty_note_facts_skip_operating_kpi_selection(tmp_path: Path):
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD)},
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    assert reconciled.selected_operating_kpi_facts == ()
    provenance = reconciliation_provenance_payload(reconciled)
    assert "selected_operating_kpi_facts" not in provenance
    fin = standardize_reconciled(reconciled)
    assert fin.historical_operating_kpis is None
    assert "historical_operating_kpis" not in standardized_to_payload(fin)


def test_lease_and_share_facts_unchanged_with_store_kpis(tmp_path: Path):
    period = date(2025, 12, 31)
    lease = SupplementalFact(
        fact_type="lease_interest_expense",
        period=period,
        value=12.0,
        status="reported",
        source=SourceRef(page=14, note="17 Leases"),
    )
    share = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=period,
        value=100.0,
        status="reported",
        source=SourceRef(page=18, note="EPS"),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(lease, _store(period, 811)),
        share_facts=(share,),
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    assert [obs.fact.fact_type for obs in reconciled.note_facts] == [
        STORE_COUNT_FACT_TYPE,
        "lease_interest_expense",
    ]
    assert len(reconciled.share_facts) == 1
    assert reconciled.selected_geographic_facts == ()
    assert len(reconciled.selected_operating_kpi_facts) == 1
    assert reconciled.selected_operating_kpi_facts[0].value == 811
    fin = standardize_reconciled(reconciled)
    assert fin.historical_segment is None
    assert fin.historical_operating_kpis is not None
    assert fin.historical_operating_kpis.observations[0].value == 811
    assert fin.historical_operating_kpis.observations[0].unit == "stores"


def test_shuffled_filings_and_repeated_observations_are_stable(tmp_path: Path):
    early = _store(date(2024, 12, 31), 711, page=11, role=PresentationRole.CURRENT_PERIOD)
    later = _store(date(2024, 12, 31), 711, page=11, role=PresentationRole.COMPARATIVE)
    current = _store(date(2025, 12, 31), 767, page=11, role=PresentationRole.CURRENT_PERIOD)
    repeat = _store(date(2025, 12, 31), 767, page=12, role=PresentationRole.CURRENT_PERIOD)
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(early,),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (120.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(later, current),
    )
    f2025b = _filing(
        year=2025,
        source_file="b2025.pdf",
        revenue_values={date(2025, 12, 31): (120.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(repeat,),
    )
    left = [
        _validated(tmp_path, f2024, b"2024"),
        _validated(tmp_path, f2025, b"2025"),
        _validated(tmp_path, f2025b, b"2025b"),
    ]
    right = list(reversed(left))
    first = reconcile_filings(left)
    second = reconcile_filings(right)
    assert first.selected_operating_kpi_facts == second.selected_operating_kpi_facts
    selected = {item.period: item for item in first.selected_operating_kpi_facts}
    assert selected[date(2024, 12, 31)].value == 711
    assert selected[date(2024, 12, 31)].filing_year == 2025
    assert selected[date(2024, 12, 31)].selection_reason == "later_audited_presentation"
    assert selected[date(2025, 12, 31)].value == 767
    assert selected[date(2025, 12, 31)].selection_reason == "agreeing_observations"
    assert {obs.fact.value for obs in first.note_facts if obs.fact.fact_type == STORE_COUNT_FACT_TYPE} == {
        711.0,
        767.0,
    }


def test_valid_precedence_retains_superseded_observation(tmp_path: Path):
    early = _store(date(2024, 12, 31), 700, page=11, role=PresentationRole.CURRENT_PERIOD)
    later = _store(date(2024, 12, 31), 711, page=11, role=PresentationRole.COMPARATIVE)
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(early,),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (120.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(
            later,
            _store(date(2025, 12, 31), 767, page=11),
        ),
    )
    reconciled = reconcile_filings(
        [_validated(tmp_path, f2024, b"2024"), _validated(tmp_path, f2025, b"2025")]
    )
    selected = next(
        item
        for item in reconciled.selected_operating_kpi_facts
        if item.period == date(2024, 12, 31)
    )
    assert selected.value == 711
    assert selected.selection_reason == "later_audited_presentation"
    assert selected.source_label == REPORTED_STORE_LABEL
    assert selected.source_note == "Company-Operated Stores"
    superseded = [
        obs
        for obs in reconciled.note_facts
        if obs.fact.period == date(2024, 12, 31) and obs.filing_year == 2024
    ]
    assert len(superseded) == 1
    assert superseded[0].fact.value == 700
    assert superseded[0].fact.source.label == REPORTED_STORE_LABEL
    assert superseded[0].fact.source.note == "Company-Operated Stores"
    conflicts = [
        conflict
        for conflict in reconciled.supplemental_conflicts
        if conflict.fact_type == STORE_COUNT_FACT_TYPE
        and conflict.period == date(2024, 12, 31)
    ]
    assert conflicts
    payload = reconciliation_conflicts_payload(reconciled)
    assert payload["supplemental_conflict_count"] >= 1


def test_unresolved_equal_priority_conflict_fails_closed(tmp_path: Path):
    left_fact = _store(date(2025, 12, 31), 767, page=11)
    right_fact = _store(date(2025, 12, 31), 770, page=12)
    left = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(left_fact,),
    )
    right = _filing(
        year=2025,
        source_file="b2025.pdf",
        revenue_values={date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(right_fact,),
    )
    pairs = [
        _validated(tmp_path, left, b"2025a"),
        _validated(tmp_path, right, b"2025b"),
    ]
    with pytest.raises(ValueError, match="unresolved equal-priority operating-KPI"):
        reconcile_filings(pairs)
    assert pairs[0][0].note_facts[0].value == 767
    assert pairs[1][0].note_facts[0].value == 770


def test_units_are_independent_of_monetary_scale(tmp_path: Path):
    period = date(2025, 12, 31)
    thousands = _filing(
        year=2025,
        source_file="a2025.pdf",
        unit_scale="thousands",
        currency="USD",
        revenue_values={period: (10588126.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(_store(period, 767, unit="stores"),),
    )
    ones = _filing(
        year=2024,
        source_file="a2024.pdf",
        unit_scale="thousands",
        currency="USD",
        revenue_values={date(2024, 12, 31): (9619278.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(_store(date(2024, 12, 31), 711, unit="ones"),),
    )
    reconciled = reconcile_filings(
        [_validated(tmp_path, ones, b"2024"), _validated(tmp_path, thousands, b"2025")]
    )
    selected = {item.period: item for item in reconciled.selected_operating_kpi_facts}
    assert selected[period].value == 767
    assert selected[period].unit == "stores"
    assert selected[date(2024, 12, 31)].value == 711
    assert selected[date(2024, 12, 31)].unit == "ones"
    fin = standardize_reconciled(reconciled)
    values = {item.period: item for item in fin.historical_operating_kpis.observations}
    assert values[period].value == 767
    assert values[period].unit == "stores"
    assert values[date(2024, 12, 31)].value == 711
    assert values[date(2024, 12, 31)].unit == "ones"
    assert reconciled.unit_scale == "thousands"


@pytest.mark.parametrize(
    "value,unit,match",
    [
        (True, "stores", "non-numeric"),
        (math.inf, "stores", "non-finite"),
        (-1, "stores", "non-negative integer"),
        (655.5, "stores", "non-negative integer"),
        (655, "thousands", "unsupported unit"),
        (655, "", "missing an explicit unit"),
    ],
)
def test_invalid_store_contracts_fail_without_mutation(tmp_path: Path, value, unit, match):
    period = date(2025, 12, 31)
    good = _store(period, 811)
    bad = replace(good, value=value, unit=unit)
    original = copy.deepcopy(good)
    with pytest.raises(ValueError, match=match):
        select_operating_kpi_facts(
            (
                SupplementalObservation(
                    kind="note",
                    filing_year=2025,
                    source_file="a2025.pdf",
                    source_sha256="abc",
                    fact=bad,
                ),
            )
        )
    assert good == original


def _kpi_observation(fact: SupplementalFact) -> SupplementalObservation:
    return SupplementalObservation(
        kind="note",
        filing_year=2025,
        source_file="a2025.pdf",
        source_sha256="abc",
        fact=fact,
    )


@pytest.mark.parametrize("label", LABEL_MUTATIONS)
@pytest.mark.parametrize("note", NOTE_CONTEXTS)
def test_missing_blank_labels_fail_even_with_note_context(label, note):
    period = date(2025, 12, 31)
    good = _store(period, 811)
    original = copy.deepcopy(good)
    bad = _store(period, 811, label=_label_text(label), note=_note_text(note))
    with pytest.raises(ValueError, match="missing reported label"):
        select_operating_kpi_facts((_kpi_observation(bad),))
    assert good == original
    assert good.source.label == REPORTED_STORE_LABEL
    assert good.source.note == "Company-Operated Stores"


@pytest.mark.parametrize("label", LABEL_MUTATIONS)
@pytest.mark.parametrize("note", NOTE_CONTEXTS)
def test_serialized_label_mutations_fail_filing_validation_and_reconcile(
    tmp_path: Path, label, note
):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    before = {path: path.read_bytes() for path in dest.glob("*.json")}
    payload = json.loads(target.read_text(encoding="utf-8"))
    original_payload = copy.deepcopy(payload)
    stores = [
        fact
        for fact in payload["note_facts"]
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE
    ]
    assert stores
    for fact in stores:
        fact["source"] = _mutate_serialized_source(
            fact["source"], label=label, note=note
        )
    mutated_path = tmp_path / "mutated-fy2025.json"
    mutated_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(mutated_path)
    report = validate_extracted_filing(filing, source_root=SOURCE)
    assert not report.ok
    assert any(
        issue.code == "invalid_operating_kpi"
        and "missing reported label" in issue.message
        for issue in report.errors
    )
    with pytest.raises(ValueError, match="cannot reconcile filings with validation errors"):
        reconcile_filings([(filing, report)])
    assert json.loads(target.read_text(encoding="utf-8")) == original_payload
    assert {path: path.read_bytes() for path in dest.glob("*.json")} == before
    out = tmp_path / "reconciled"
    assert not out.exists()


@pytest.mark.parametrize("label", NON_STRING_LABELS)
@pytest.mark.parametrize("note", NOTE_CONTEXTS)
def test_serialized_non_string_labels_rejected_before_parse_coercion(
    tmp_path: Path, label, note
):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    before = {path: path.read_bytes() for path in dest.glob("*.json")}
    payload = json.loads(target.read_text(encoding="utf-8"))
    original_payload = copy.deepcopy(payload)
    stores = [
        fact
        for fact in payload["note_facts"]
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE
    ]
    assert stores
    for fact in stores:
        fact["source"] = _mutate_serialized_source(
            fact["source"], label=label, note=note
        )
    mutated_path = tmp_path / "mutated-non-string-fy2025.json"
    mutated_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing reported label") as excinfo:
        load_extracted_filing(mutated_path)
    assert "invalid_operating_kpi" not in str(excinfo.value)
    assert json.loads(target.read_text(encoding="utf-8")) == original_payload
    assert {path: path.read_bytes() for path in dest.glob("*.json")} == before
    assert not (tmp_path / "reconciled").exists()


@pytest.mark.parametrize("label", NON_STRING_LABELS)
@pytest.mark.parametrize("note", NOTE_CONTEXTS)
def test_in_memory_non_string_labels_fail_even_with_note_context(label, note):
    period = date(2025, 12, 31)
    good = _store(period, 811)
    original = copy.deepcopy(good)
    bad = _store(period, 811, label=label, note=_note_text(note))
    with pytest.raises(ValueError, match="missing reported label"):
        select_operating_kpi_facts((_kpi_observation(bad),))
    assert good == original
    assert good.source.label == REPORTED_STORE_LABEL
    assert good.source.note == "Company-Operated Stores"


def test_review_reproduction_removes_label_and_note_from_serialized_store(
    tmp_path: Path,
):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    before = target.read_bytes()
    payload = json.loads(before)
    observation = next(
        fact
        for fact in payload["note_facts"]
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE
    )
    assert observation["source"]["label"] == REPORTED_STORE_LABEL
    assert observation["source"]["note"]
    observation["source"].pop("label")
    observation["source"].pop("note")
    mutated_path = tmp_path / "review-repro.json"
    mutated_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    assert target.read_bytes() == before
    filing = load_extracted_filing(mutated_path)
    report = validate_extracted_filing(filing, source_root=SOURCE)
    assert not report.ok
    assert any(
        issue.code == "invalid_operating_kpi"
        and "missing reported label" in issue.message
        for issue in report.errors
    )
    with pytest.raises(ValueError, match="cannot reconcile filings with validation errors"):
        reconcile_filings([(filing, report)])
    assert target.read_bytes() == before


def test_reconcile_revalidates_kpi_fact_after_valid_report(tmp_path: Path):
    period = date(2025, 12, 31)
    good = _store(period, 811)
    filing, report = _validated(
        tmp_path,
        _filing(
            year=2025,
            source_file="a2025.pdf",
            revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
            note_facts=(good,),
        ),
        b"2025",
    )
    assert report.ok
    original_fact = copy.deepcopy(filing.note_facts[0])
    invalid = _store(period, 811, label="", note="Company-Operated Stores")
    mutated = replace(filing, note_facts=(invalid,))
    with pytest.raises(ValueError, match="missing reported label"):
        reconcile_filings([(mutated, report)])
    assert filing.note_facts[0] == original_fact
    assert filing.note_facts[0].source.label == REPORTED_STORE_LABEL
    assert mutated.note_facts[0].source.note == "Company-Operated Stores"


@pytest.mark.parametrize("label", NON_STRING_LABELS)
def test_reconcile_revalidates_non_string_label_after_valid_report(
    tmp_path: Path, label
):
    period = date(2025, 12, 31)
    good = _store(period, 811)
    filing, report = _validated(
        tmp_path,
        _filing(
            year=2025,
            source_file="a2025.pdf",
            revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
            note_facts=(good,),
        ),
        b"2025",
    )
    assert report.ok
    original_fact = copy.deepcopy(filing.note_facts[0])
    superseded = replace(
        good,
        source=replace(good.source, label=label),
        presentation_role=PresentationRole.PRIOR_PRESENTATION.value,
        value=700,
    )
    mutated = replace(filing, note_facts=(good, superseded))
    with pytest.raises(ValueError, match="missing reported label"):
        reconcile_filings([(mutated, report)])
    assert filing.note_facts[0] == original_fact
    assert filing.note_facts[0].source.label == REPORTED_STORE_LABEL


def test_valid_label_without_note_is_accepted(tmp_path: Path):
    period = date(2025, 12, 31)
    fact = _store(period, 811, note="")
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(fact,),
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    selected = reconciled.selected_operating_kpi_facts[0]
    assert selected.value == 811
    assert selected.source_label == REPORTED_STORE_LABEL
    assert selected.source_note == ""
    provenance = reconciliation_provenance_payload(reconciled)
    assert provenance["selected_operating_kpi_facts"][0]["source_label"] == REPORTED_STORE_LABEL
    assert "source_note" not in provenance["selected_operating_kpi_facts"][0]


def test_missing_label_cli_leaves_inputs_and_output_unchanged(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    for fact in payload["note_facts"]:
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE:
            fact["source"].pop("label", None)
            fact["source"].pop("note", None)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in dest.glob("*.json")}
    out = tmp_path / "reconciled"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(dest),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    combined = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert "invalid_operating_kpi" in combined
    assert "missing reported label" in combined
    assert "wrote no artifacts" in combined
    assert {path: path.read_bytes() for path in dest.glob("*.json")} == before
    assert not out.exists() or not any(out.iterdir())


@pytest.mark.parametrize("label", [123, True, {"x": 1}, [1]])
def test_non_string_label_cli_leaves_inputs_and_output_unchanged(
    tmp_path: Path, label
):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    for fact in payload["note_facts"]:
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE:
            fact["source"]["label"] = label
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in dest.glob("*.json")}
    out = tmp_path / "reconciled"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(dest),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    combined = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert "missing reported label" in combined
    assert "error:" in combined
    assert "invalid_operating_kpi" not in combined
    assert "wrote no artifacts" not in combined
    assert {path: path.read_bytes() for path in dest.glob("*.json")} == before
    assert not out.exists() or not any(out.iterdir())


def test_unknown_identity_and_invalid_date_fail_closed(tmp_path: Path):
    period = date(2025, 12, 31)
    unknown = replace(_store(period, 811), fact_type="kpi.operating.square_footage.company_operated")
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(unknown,),
    )
    _write = tmp_path / "source"
    _write.mkdir()
    (_write / "a2025.pdf").write_bytes(b"2025")
    report = validate_extracted_filing(f2025, source_root=_write)
    assert not report.ok
    assert any(issue.code == "invalid_operating_kpi" for issue in report.errors)
    payload = extracted_filing_to_payload(f2025)
    payload["note_facts"][0]["period"] = "2025-02-30"
    path = tmp_path / "bad-date.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid date"):
        load_extracted_filing(path)


def test_sparse_histories_do_not_infer_zero(tmp_path: Path):
    period = date(2025, 12, 31)
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            period: (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(_store(period, 811),),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
    )
    reconciled = reconcile_filings(
        [_validated(tmp_path, f2024, b"2024"), _validated(tmp_path, f2025, b"2025")]
    )
    fin = standardize_reconciled(reconciled)
    periods = {item.period for item in fin.historical_operating_kpis.observations}
    assert periods == {period}
    assert date(2024, 12, 31) not in periods
    payload = standardized_to_payload(fin)
    restored = standardized_from_payload(payload)
    assert restored.historical_operating_kpis == fin.historical_operating_kpis
    assert all(item.value != 0 for item in restored.historical_operating_kpis.observations)


def test_malformed_model_payload_fails_without_mutation():
    from core.tests.test_historical_segment import _base_payload

    payload = _base_payload()
    payload["historical_operating_kpis"] = {
        "observations": [
            {
                "metric": METRIC_STORE_COUNT,
                "population": POPULATION_COMPANY_OPERATED,
                "period": "2025-12-31",
                "value": 811,
                "unit": "stores",
            }
        ]
    }
    original = copy.deepcopy(payload)
    payload["historical_operating_kpis"] = "bad"
    with pytest.raises(ValueError, match="historical_operating_kpis must be an object"):
        standardized_from_payload(payload)
    assert payload["historical_operating_kpis"] == "bad"

    payload = copy.deepcopy(original)
    payload["historical_operating_kpis"]["observations"][0]["period"] = "2020-01-01"
    with pytest.raises(ValueError, match="outside the model axis"):
        standardized_from_payload(payload)
    assert original["historical_operating_kpis"]["observations"][0]["period"] == "2025-12-31"

    payload = copy.deepcopy(original)
    payload["historical_operating_kpis"]["observations"].append(
        copy.deepcopy(payload["historical_operating_kpis"]["observations"][0])
    )
    with pytest.raises(ValueError, match="duplicate operating-KPI identity"):
        standardized_from_payload(payload)


def test_rejected_cli_leaves_inputs_and_output_unchanged(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    target = dest / "LULU_FY2025.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    for fact in payload["note_facts"]:
        if fact.get("fact_type") == STORE_COUNT_FACT_TYPE:
            fact["presentation_role"] = PresentationRole.PRIOR_PRESENTATION.value
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in dest.glob("*.json")}
    out = tmp_path / "reconciled"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(dest),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "no eligible operating-KPI observation" in completed.stdout + completed.stderr
    assert {path: path.read_bytes() for path in dest.glob("*.json")} == before
    assert not out.exists() or not any(out.iterdir())


def test_augmented_lululemon_filings_round_trip_and_selected_totals(tmp_path: Path):
    originals = {
        name: json.loads((EXTRACTED / name).read_text(encoding="utf-8"))
        for name in (
            "LULU_FY2022.json",
            "LULU_FY2023.json",
            "LULU_FY2024.json",
            "LULU_FY2025.json",
        )
    }
    dest, validated = _validated_augmented(tmp_path)
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for name, original in originals.items():
        reloaded = load_extracted_filing(dest / name)
        dumped = extracted_filing_to_payload(reloaded)
        round_path = tmp_path / f"round-{name}"
        round_path.write_text(json.dumps(dumped, indent=2) + "\n", encoding="utf-8")
        again = extracted_filing_to_payload(load_extracted_filing(round_path))
        assert again == dumped
        original_payload = extracted_filing_to_payload(
            load_extracted_filing(EXTRACTED / name)
        )
        assert dumped["statements"] == original_payload["statements"]
        assert dumped["share_facts"] == original_payload["share_facts"]
        assert dumped["filing"]["source_sha256"] == original["filing"]["source_sha256"]
        geo = [
            fact
            for fact in dumped["note_facts"]
            if str(fact["fact_type"]).startswith("segment.geo.")
        ]
        original_geo = [
            fact
            for fact in original_payload["note_facts"]
            if str(fact["fact_type"]).startswith("segment.geo.")
        ]
        assert geo == original_geo
        stores = [
            fact
            for fact in dumped["note_facts"]
            if fact["fact_type"] == STORE_COUNT_FACT_TYPE
        ]
        assert stores == fixture[name]
        assert all(fact["unit"] == "stores" for fact in stores)

    for order in (validated, list(reversed(validated))):
        reconciled = reconcile_filings(order, admit_periods=ADMIT_2022)
        selected = {
            item.period: item for item in reconciled.selected_operating_kpi_facts
        }
        assert set(selected) == set(INDEPENDENT_STORE_TOTALS)
        for period, value in INDEPENDENT_STORE_TOTALS.items():
            item = selected[period]
            year, role, reason, page = EXPECTED_SELECTION[period]
            assert item.value == value
            assert item.unit == "stores"
            assert item.metric == METRIC_STORE_COUNT
            assert item.population == POPULATION_COMPANY_OPERATED
            assert item.filing_year == year
            assert item.presentation_basis == role
            assert item.selection_reason == reason
            assert item.pdf_page == page
            assert item.source_label == REPORTED_STORE_LABEL
            assert item.source_note == EXPECTED_SOURCE_NOTES[period]
            assert item.source_label != item.fact_type

        assert len(reconciled.selected_geographic_facts) == 56
        americas = [
            item
            for item in reconciled.selected_geographic_facts
            if item.period == P2025 and item.fact_type.endswith("net_revenue.americas")
        ]
        assert americas == [
            next(
                item
                for item in reconciled.selected_geographic_facts
                if item.period == P2025
                and item.fact_type.endswith("net_revenue.americas")
            )
        ]
        assert americas[0].value == 7928156

        fin = standardize_reconciled(reconciled)
        restored = standardized_from_payload(standardized_to_payload(fin))
        assert restored.historical_operating_kpis == fin.historical_operating_kpis
        model = {
            item.period: item for item in restored.historical_operating_kpis.observations
        }
        assert set(model) == set(INDEPENDENT_STORE_TOTALS)
        for period, value in INDEPENDENT_STORE_TOTALS.items():
            assert model[period].value == value
            assert model[period].unit == "stores"
        payload = standardized_to_payload(fin)
        kpi_json = json.dumps(payload["historical_operating_kpis"])
        assert "source_sha256" not in kpi_json
        assert "pdf_page" not in kpi_json
        assert "source_label" not in kpi_json
        assert "source_note" not in kpi_json
        assert restored.historical_segment == fin.historical_segment
        assert sum(len(snap.values) for snap in restored.historical_segment.periods) == 56
        provenance = reconciliation_provenance_payload(reconciled)
        assert len(provenance["selected_operating_kpi_facts"]) == 5
        assert all(
            row["unit"] == "stores"
            and row["value"] == INDEPENDENT_STORE_TOTALS[date.fromisoformat(row["period"])]
            and row["source_label"] == REPORTED_STORE_LABEL
            and row["source_note"] == EXPECTED_SOURCE_NOTES[date.fromisoformat(row["period"])]
            for row in provenance["selected_operating_kpi_facts"]
        )

    for name, original in originals.items():
        assert json.loads((EXTRACTED / name).read_text(encoding="utf-8")) == original


def test_outside_axis_store_facts_stay_out_of_model_payload(tmp_path: Path):
    _dest, validated = _validated_augmented(tmp_path)
    reconciled = reconcile_filings(validated)
    assert P2022 not in reconciled.periods
    assert any(
        item.period == P2022 for item in reconciled.selected_operating_kpi_facts
    )
    fin = standardize_reconciled(reconciled)
    model_periods = {item.period for item in fin.historical_operating_kpis.observations}
    assert P2022 not in model_periods
    assert model_periods == {P2023, P2024, P2025, P2026}
    restored = standardized_from_payload(standardized_to_payload(fin))
    assert {item.period for item in restored.historical_operating_kpis.observations} == model_periods
    assert 2021 not in {
        item.period.year for item in reconciled.selected_operating_kpi_facts
    }


def test_standardizer_does_not_promote_empty_kpi_selection(tmp_path: Path):
    _dest, validated = _validated_augmented(tmp_path)
    reconciled = reconcile_filings(validated, admit_periods=ADMIT_2022)
    emptied = replace(reconciled, selected_operating_kpi_facts=())
    fin = standardize_reconciled(emptied)
    assert fin.historical_operating_kpis is None
    assert emptied.note_facts == reconciled.note_facts
    assert emptied.selected_geographic_facts == reconciled.selected_geographic_facts
    assert len(emptied.selected_geographic_facts) == 56
