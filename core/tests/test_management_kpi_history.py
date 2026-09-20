"""Ordinary-path handoff of evidenced selected management-KPI histories."""

from __future__ import annotations

import copy
import json
import shutil
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from core.data.historical_operating_kpis import UNIT_PERCENT, UNIT_USD_PER_SQUARE_FOOT
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import standardize_reconciled
from core.ingestion.management_kpi import management_admission_payload
from core.ingestion.management_kpi_history import (
    deferred_management_kpi_disagreements,
    selected_management_kpi_histories,
)
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    REASON_CALENDAR_REPORTING,
    REASON_CALENDAR_WEEK,
)
from core.ingestion.management_kpi_reconciliation import (
    REASON_ORDINARY_DISAGREEMENT,
    SELECTION_DEFERRED,
    SELECTION_SELECTED,
)
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.line_resolver import MissingLineError
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    SOURCE,
    _bytes_by_name,
    _canonicalize,
    _copy_json,
)
from core.tests.test_management_kpi_identity import (
    AFFIRMATIVE_COMPSALES_DEFINITION,
    AFFIRMATIVE_SPSF_DEFINITION,
    REPORTING_BASIS_52,
    REPORTING_BASIS_53,
    _apply_affirmative_compsales,
    _apply_affirmative_spsf,
    _set_reporting_basis,
    _write_json,
)
from core.tests.test_management_kpi_reconciliation import (
    FAMILIES,
    SHARED_PERIOD,
    _apply_same_period,
    _assert_deferred_group,
    _attach_family_evidence,
    _attach_family_revision,
    _clear_week_adjustment,
    _cli_validate_and_reconcile,
    _family_period_group,
    _write_audited_revised_family_pair,
    _write_family_pair,
    _write_ordinary_agreeing_pair,
    _write_revised_family_pair,
    _write_three_peer,
    write_incoming_ambiguous_fixture,
)
from core.tests.test_operating_kpi_analysis import _assert_series_matches, _independent_from_counts
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2023,
    P2024,
    P2025,
    _prepare_augmented,
)
from core.tests.test_operating_kpi_management_history import _assert_export_reload_export
from core.model.period_axis import canonical_fiscal_periods

OFF_AXIS_PERIOD = "2022-01-30"
DEF_A = AFFIRMATIVE_COMPSALES_DEFINITION
DEF_B = AFFIRMATIVE_COMPSALES_DEFINITION + " later calendar"
SPSF_DEF_B = AFFIRMATIVE_SPSF_DEFINITION + " later calendar"


def _reconcile(dest: Path, *, admit=None):
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    return reconcile_filings(validated, admit_periods=admit)


def _snapshot(reconciled) -> dict:
    return {
        "status": reconciled.management_admission.status,
        "admission": copy.deepcopy(
            management_admission_payload(reconciled.management_admission)
        ),
        "stores": tuple(
            (item.period, item.value, item.metric, item.population)
            for item in reconciled.selected_operating_kpi_facts
        ),
    }


def _deferred_rows(fin, *, family: str | None = None, period: str | None = None):
    data = fin.historical_operating_kpis
    if data is None:
        return []
    payload = standardized_to_payload(fin)["historical_operating_kpis"]
    rows = payload.get("deferred_disagreements", [])
    if family is not None:
        rows = [row for row in rows if row["family"] == family]
    if period is not None:
        rows = [row for row in rows if row["period"] == period]
    return rows


def _management_rows(fin, *, family: str | None = None, period: str | None = None):
    data = fin.historical_operating_kpis
    if data is None:
        return []
    payload = standardized_to_payload(fin)["historical_operating_kpis"]
    rows = payload.get("management_observations", [])
    if family is not None:
        rows = [row for row in rows if row["family"] == family]
    if period is not None:
        rows = [row for row in rows if row["period"] == period]
    return rows


def _write_both_selected(
    dest: Path,
    *,
    period: str = SHARED_PERIOD,
    compsales=(10, 11),
    spsf=(1400, 1426),
) -> None:
    left = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    right = json.loads((EXTRACTED / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    left = _apply_affirmative_spsf(_apply_affirmative_compsales(left))
    right = _apply_affirmative_spsf(_apply_affirmative_compsales(right))
    left = _apply_same_period(
        left, FAMILY_COMPARABLE_SALES_GROWTH, period=period, value=compsales[0]
    )
    right = _apply_same_period(
        right, FAMILY_COMPARABLE_SALES_GROWTH, period=period, value=compsales[1]
    )
    left = _apply_same_period(
        left, FAMILY_SALES_PER_SQUARE_FOOT, period=period, value=spsf[0]
    )
    right = _apply_same_period(
        right, FAMILY_SALES_PER_SQUARE_FOOT, period=period, value=spsf[1]
    )
    right = _attach_family_revision(right, left, FAMILY_COMPARABLE_SALES_GROWTH)
    right = _attach_family_revision(right, left, FAMILY_SALES_PER_SQUARE_FOOT)
    right = _attach_family_evidence(
        right, FAMILY_COMPARABLE_SALES_GROWTH, status="audited"
    )
    right = _attach_family_evidence(
        right, FAMILY_SALES_PER_SQUARE_FOOT, status="audited"
    )
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)


def _ensure_family_metric(payload: dict, family: str) -> dict:
    from core.tests.test_management_kpi_identity import _family_metric_id
    from core.tests.test_management_kpi_admission import _metric_items

    payload = copy.deepcopy(payload)
    metric_id = _family_metric_id(family)
    if _metric_items(payload, metric_id):
        return payload
    donor = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    reported = copy.deepcopy(_metric_items(donor, metric_id)[0])
    definition = copy.deepcopy(
        next(
            item
            for item in donor["kpi_definitions"]
            if item.get("metric_id") == metric_id
        )
    )
    unique_id = f"{metric_id}_fy{payload['report']['fiscal_year']}_injected"
    definition["definition_id"] = unique_id
    reported["definition_id"] = unique_id
    payload["reported_kpis"].append(reported)
    payload["kpi_definitions"].insert(0, definition)
    return payload


def _write_selected_on_docs(
    dest: Path,
    family: str,
    left_name: str,
    right_name: str,
    *,
    period: str,
    values: tuple[object, object],
    definition: str,
    week: bool,
    reporting_basis: str,
) -> None:
    from core.tests.test_management_kpi_identity import _family_metric_id

    left = _ensure_family_metric(
        json.loads((dest / left_name).read_text(encoding="utf-8")), family
    )
    right = _ensure_family_metric(
        json.loads((dest / right_name).read_text(encoding="utf-8")), family
    )
    apply_family = (
        _apply_affirmative_compsales
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else _apply_affirmative_spsf
    )
    left = apply_family(left, week=week)
    right = apply_family(right, week=week)
    left = _apply_same_period(left, family, period=period, value=values[0])
    right = _apply_same_period(right, family, period=period, value=values[1])
    metric_id = _family_metric_id(family)
    for payload in (left, right):
        for item in payload["kpi_definitions"]:
            if item.get("metric_id") == metric_id:
                item["definition"] = definition
        payload["report"]["reporting_basis"] = reporting_basis
    right = _attach_family_revision(right, left, family)
    right = _attach_family_evidence(right, family, status="audited")
    _write_json(dest / left_name, left)
    _write_json(dest / right_name, right)


def _reverse_reported(dest: Path) -> None:
    for name in MANAGEMENT_NAMES:
        path = dest / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["reported_kpis"] = list(reversed(payload["reported_kpis"]))
        _write_json(path, payload)


def _assert_handoff_diagnostic(admission, *, selected: int) -> None:
    assert admission.status == "admitted_unreconciled"
    payload = management_admission_payload(admission)
    assert payload["status"] == "admitted_unreconciled"
    assert payload["canonical_selection"] == "deferred"
    codes = {item.code for item in admission.diagnostics}
    assert "deferred_canonical_selection" in codes
    handoff = next(
        item
        for item in admission.diagnostics
        if item.code == "management_kpi_history_handoff"
    )
    assert f"{selected} evidenced selected occurrence(s)" in handoff.message
    assert "remain audit-only" in handoff.message
    deferred = next(
        item
        for item in admission.diagnostics
        if item.code == "deferred_canonical_selection"
    )
    assert "not complete" in deferred.message
    assert len(handoff.occurrences) == selected


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("values", [(10, 11), (10, 10), (10, 0), (8, -3)])
def test_selected_occurrence_reaches_standardized_history(
    tmp_path: Path, family: str, values: tuple[object, object]
):
    if family == FAMILY_SALES_PER_SQUARE_FOOT and any(
        isinstance(value, (int, float)) and value < 0 for value in values
    ):
        values = (1400, 0)
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "sel")
    _write_audited_revised_family_pair(
        dest, family, left_value=values[0], right_value=values[1]
    )
    reconciled = _reconcile(dest)
    before = _snapshot(reconciled)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=1)
    fin = standardize_reconciled(reconciled)
    assert _snapshot(reconciled) == before
    rows = _management_rows(fin, family=family, period=SHARED_PERIOD)
    assert len(rows) == 1
    assert rows[0]["value"] == values[1]
    assert rows[0]["period_kind"] == "date"
    assert rows[0]["unit"] == (
        UNIT_PERCENT if family == FAMILY_COMPARABLE_SALES_GROWTH else UNIT_USD_PER_SQUARE_FOOT
    )
    group = _family_period_group(
        management_admission_payload(reconciled.management_admission), family
    )
    reviser = next(
        occ for occ in group["occurrences"] if occ["locator"] == group["selected"]["locator"]
    )
    superseded = next(
        occ for occ in group["occurrences"] if occ["locator"] == group["superseded"]["locator"]
    )
    assert rows[0]["definition_text"] == reviser["definition"]["text"]
    assert rows[0]["calendar_week_adjustment"] == reviser["evidence"]["calendar_week_adjustment"]
    assert rows[0]["calendar_reporting_basis"] == reviser["evidence"]["calendar_reporting_basis"]
    if values[0] != values[1]:
        assert not any(row["value"] == values[0] for row in rows)
    serialized = json.dumps(standardized_to_payload(fin)["historical_operating_kpis"])
    assert "source_file" not in serialized
    assert "assurance" not in serialized
    assert "revision" not in serialized
    assert superseded["bound_source_file"]
    assert _assert_export_reload_export(fin)


@pytest.mark.parametrize("family", FAMILIES)
def test_ordinary_singleton_reaches_standardized_history(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "ord-hist")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    payload = (
        _apply_affirmative_compsales(payload)
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else _apply_affirmative_spsf(payload)
    )
    payload = _apply_same_period(payload, family, period=SHARED_PERIOD, value=12)
    payload = _attach_family_evidence(payload, family, role="current")
    _write_json(dest / MANAGEMENT_NAMES[1], payload)
    reconciled = _reconcile(dest)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=1)
    fin = standardize_reconciled(reconciled)
    rows = _management_rows(fin, family=family, period=SHARED_PERIOD)
    assert len(rows) == 1
    assert rows[0]["value"] == 12
    assert rows[0]["period_kind"] == "date"
    serialized = json.dumps(standardized_to_payload(fin)["historical_operating_kpis"])
    assert "source_file" not in serialized
    assert "assurance" not in serialized
    assert "revision" not in serialized
    _assert_export_reload_export(fin)


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(
    "mutate_left,reason",
    [
        (True, REASON_CALENDAR_REPORTING),
        (False, REASON_CALENDAR_WEEK),
    ],
)
def test_ordinary_repeat_missing_evidence_does_not_reach_standardized(
    tmp_path: Path, family: str, mutate_left: bool, reason: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "miss-hist")
    other = (
        FAMILY_SALES_PER_SQUARE_FOOT
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_COMPARABLE_SALES_GROWTH
    )
    if reason == REASON_CALENDAR_REPORTING:
        def extra(payload, blank=None):
            return _set_reporting_basis(payload, blank)
    else:
        extra = _clear_week_adjustment(family)
    _write_ordinary_agreeing_pair(
        dest,
        family,
        left_extra=extra if mutate_left else None,
        right_extra=extra if not mutate_left else None,
    )
    singleton_name = MANAGEMENT_NAMES[2] if mutate_left else MANAGEMENT_NAMES[1]
    payload_doc = json.loads((dest / singleton_name).read_text(encoding="utf-8"))
    apply_other = (
        _apply_affirmative_spsf
        if other == FAMILY_SALES_PER_SQUARE_FOOT
        else _apply_affirmative_compsales
    )
    payload_doc = apply_other(payload_doc)
    payload_doc = _apply_same_period(
        payload_doc, other, period=SHARED_PERIOD, value=12
    )
    payload_doc = _attach_family_evidence(payload_doc, other, role="current")
    _write_json(dest / singleton_name, payload_doc)
    reconciled = _reconcile(dest)
    payload = management_admission_payload(reconciled.management_admission)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, reason)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=1)
    fin = standardize_reconciled(reconciled)
    assert _management_rows(fin, family=family, period=SHARED_PERIOD) == []
    other_rows = _management_rows(fin, family=other, period=SHARED_PERIOD)
    assert len(other_rows) == 1
    assert other_rows[0]["value"] == 12
    _assert_export_reload_export(fin)


def test_both_families_share_a_period_and_round_trip(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "both")
    _write_both_selected(dest, compsales=(-3, 0), spsf=(1407.5, 1426))
    reconciled = _reconcile(dest)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=2)
    fin = standardize_reconciled(reconciled)
    payload = _assert_export_reload_export(fin)
    rows = payload["historical_operating_kpis"]["management_observations"]
    assert {row["family"] for row in rows} == {
        FAMILY_COMPARABLE_SALES_GROWTH,
        FAMILY_SALES_PER_SQUARE_FOOT,
    }
    assert {row["period"] for row in rows} == {SHARED_PERIOD}
    by_family = {row["family"]: row for row in rows}
    assert by_family[FAMILY_COMPARABLE_SALES_GROWTH]["value"] == 0
    assert by_family[FAMILY_SALES_PER_SQUARE_FOOT]["value"] == 1426
    restored = standardized_from_payload(copy.deepcopy(payload))
    assert standardized_to_payload(restored) == payload
    assert operating_kpi_applicable(fin) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(fin)


def test_permutation_of_reported_rows_is_deterministic(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "perm")
    _write_both_selected(dest, compsales=(2, 4), spsf=(100, 200))
    first = standardized_to_payload(standardize_reconciled(_reconcile(dest)))
    _reverse_reported(dest)
    second = standardized_to_payload(standardize_reconciled(_reconcile(dest)))
    assert (
        first["historical_operating_kpis"]["management_observations"]
        == second["historical_operating_kpis"]["management_observations"]
    )


def test_sparse_histories_and_calendar_changes_do_not_gap_fill(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "sparse")
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[0],
        MANAGEMENT_NAMES[1],
        period=P2023.isoformat(),
        values=(1, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[2],
        MANAGEMENT_NAMES[3],
        period=P2025.isoformat(),
        values=(3, 4),
        definition=DEF_B,
        week=True,
        reporting_basis=REPORTING_BASIS_53,
    )
    reconciled = _reconcile(dest, admit=ADMIT_2022)
    fin = standardize_reconciled(reconciled)
    rows = _management_rows(fin, family=FAMILY_COMPARABLE_SALES_GROWTH)
    periods = [row["period"] for row in rows]
    assert periods == [P2023.isoformat(), P2025.isoformat()]
    assert P2024.isoformat() not in periods
    assert rows[0]["definition_text"] == DEF_A
    assert rows[1]["definition_text"] == DEF_B
    assert rows[0]["calendar_week_adjustment"] != rows[1]["calendar_week_adjustment"]
    assert rows[0]["calendar_reporting_basis"] != rows[1]["calendar_reporting_basis"]
    assert {period.isoformat() for period in fin.period_dates()} >= {
        P2023.isoformat(),
        P2024.isoformat(),
        P2025.isoformat(),
    }


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(
    "builder",
    [
        "unaudited",
        "unknown",
        "missing_revision",
        "singleton_pair_absent",
        "incompatible",
        "missing_value",
        "three",
        "ambiguous",
    ],
)
def test_deferred_groups_are_absent_from_histories(
    tmp_path: Path, family: str, builder: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / builder)
    if builder == "unaudited":
        dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "u")
        _write_revised_family_pair(
            dest,
            family,
            right_mutate=lambda payload: _attach_family_evidence(
                payload, family, status="unaudited"
            ),
        )
    elif builder == "unknown":
        dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "k")
        _write_revised_family_pair(dest, family)
    elif builder == "missing_revision":
        dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "m")
        _write_family_pair(dest, family, left_value=10, right_value=11)
    elif builder == "singleton_pair_absent":
        dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "s")
        payload = _apply_affirmative_compsales(
            json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
        ) if family == FAMILY_COMPARABLE_SALES_GROWTH else _apply_affirmative_spsf(
            json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
        )
        payload = _apply_same_period(payload, family, period=SHARED_PERIOD, value=10)
        _write_json(dest / MANAGEMENT_NAMES[1], payload)
    elif builder == "incompatible":
        dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "i")
        changed = DEF_B if family == FAMILY_COMPARABLE_SALES_GROWTH else SPSF_DEF_B

        def mutate_right(payload: dict) -> dict:
            payload = copy.deepcopy(payload)
            payload["kpi_definitions"][
                0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
            ]["definition"] = changed
            return payload

        _write_audited_revised_family_pair(dest, family, right_mutate=mutate_right)
    elif builder == "missing_value":
        dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "v")
        _write_audited_revised_family_pair(dest, family, left_value=10, right_value=None)
    elif builder == "three":
        _write_three_peer(dest, family, values=(10, 10, None))
        first = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
        second = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
        second = _attach_family_revision(second, first, family)
        second = _attach_family_evidence(second, family, status="audited")
        _write_json(dest / MANAGEMENT_NAMES[2], second)
    else:
        write_incoming_ambiguous_fixture(dest, family, target="superseded")
    reconciled = _reconcile(dest)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=0)
    fin = standardize_reconciled(reconciled)
    assert fin.historical_operating_kpis is None
    assert "historical_operating_kpis" not in standardized_to_payload(fin)


@pytest.mark.parametrize("family", FAMILIES)
def test_tampered_selections_fail_closed_and_leave_inputs(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "tamp")
    _write_audited_revised_family_pair(dest, family)
    reconciled = _reconcile(dest)
    before = _snapshot(reconciled)
    admission = reconciled.management_admission
    groups = list(admission.group_selections)
    idx = next(i for i, item in enumerate(groups) if item.status == SELECTION_SELECTED)
    selected = groups[idx]
    groups[idx] = replace(
        selected,
        selected=replace(selected.selected, locator="missing-locator"),
    )
    tampered = replace(
        reconciled,
        management_admission=replace(admission, group_selections=tuple(groups)),
    )
    tampered_before = _snapshot(tampered)
    with pytest.raises(ValueError, match="stale or inconsistent"):
        standardize_reconciled(tampered)
    assert _snapshot(reconciled) == before
    assert _snapshot(tampered) == tampered_before
    empty = replace(
        reconciled,
        management_admission=replace(admission, group_selections=()),
    )
    with pytest.raises(ValueError, match="stale or inconsistent"):
        standardize_reconciled(empty)
    deferred_idx = next(
        i for i, item in enumerate(admission.group_selections) if item.status == SELECTION_DEFERRED
    )
    deferred = admission.group_selections[deferred_idx]
    promoted = list(admission.group_selections)
    promoted[deferred_idx] = replace(deferred, status=SELECTION_SELECTED, reasons=())
    with pytest.raises(ValueError, match="stale or inconsistent"):
        standardize_reconciled(
            replace(
                reconciled,
                management_admission=replace(
                    admission, group_selections=tuple(promoted)
                ),
            )
        )
    assert _snapshot(reconciled) == before


def test_off_axis_selected_period_is_rejected(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "axis")
    left, right = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8")), json.loads(
        (EXTRACTED / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8")
    )
    left = _apply_affirmative_compsales(left)
    right = _apply_affirmative_compsales(right)
    left = _apply_same_period(
        left, FAMILY_COMPARABLE_SALES_GROWTH, period=OFF_AXIS_PERIOD, value=10
    )
    right = _apply_same_period(
        right, FAMILY_COMPARABLE_SALES_GROWTH, period=OFF_AXIS_PERIOD, value=11
    )
    right = _attach_family_revision(right, left, FAMILY_COMPARABLE_SALES_GROWTH)
    right = _attach_family_evidence(
        right, FAMILY_COMPARABLE_SALES_GROWTH, status="audited"
    )
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    reconciled = _reconcile(dest)
    before = _snapshot(reconciled)
    assert OFF_AXIS_PERIOD not in {period.isoformat() for period in reconciled.periods}
    with pytest.raises(ValueError, match="outside the model axis"):
        standardize_reconciled(reconciled)
    assert _snapshot(reconciled) == before


def test_negative_spsf_selected_value_is_rejected(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "neg")
    _write_audited_revised_family_pair(
        dest, FAMILY_SALES_PER_SQUARE_FOOT, left_value=10, right_value=-1
    )
    reconciled = _reconcile(dest)
    before = _snapshot(reconciled)
    with pytest.raises(ValueError, match="non-negative"):
        standardize_reconciled(reconciled)
    assert _snapshot(reconciled) == before


def test_supplied_inputs_still_have_no_management_history(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_rec = _reconcile(mixed, admit=ADMIT_2022)
    annual_rec = _reconcile(annual, admit=ADMIT_2022)
    mixed_fin = standardize_reconciled(mixed_rec)
    annual_fin = standardize_reconciled(annual_rec)
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None
    mixed_payload = standardized_to_payload(mixed_fin)
    annual_payload = standardized_to_payload(annual_fin)
    assert _canonicalize(mixed_payload) == _canonicalize(annual_payload)
    _assert_handoff_diagnostic(mixed_rec.management_admission, selected=0)
    assert _bytes_by_name(EXTRACTED) == before


def test_mixed_store_histories_preserve_growth(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    for name in MANAGEMENT_NAMES:
        shutil.copy2(EXTRACTED / name, dest / name)
    _write_both_selected(dest, compsales=(2, 4), spsf=(100, 200))
    reconciled = _reconcile(dest, admit=ADMIT_2022)
    store_fin = standardize_reconciled(
        replace(reconciled, management_admission=None)
    )
    mixed_fin = standardize_reconciled(reconciled)
    assert operating_kpi_applicable(store_fin) is True
    assert operating_kpi_applicable(mixed_fin) is True
    store_series = compute_operating_kpi_series(store_fin)
    mixed_series = compute_operating_kpi_series(mixed_fin)
    for period in canonical_fiscal_periods(store_fin):
        assert mixed_series.period_end_count[period] == store_series.period_end_count[period]
        left = mixed_series.growth[period]
        right = store_series.growth[period]
        if isinstance(left, float) and isinstance(right, float):
            assert abs(left - right) <= OPERATING_KPI_RATIO_TOLERANCE
        else:
            assert left == right
    expected = _independent_from_counts(
        canonical_fiscal_periods(mixed_fin), INDEPENDENT_STORE_TOTALS
    )
    _assert_series_matches(mixed_series, expected)
    rows = _management_rows(mixed_fin)
    assert {row["family"] for row in rows} == {
        FAMILY_COMPARABLE_SALES_GROWTH,
        FAMILY_SALES_PER_SQUARE_FOOT,
    }
    payload = _assert_export_reload_export(mixed_fin)
    assert payload["historical_operating_kpis"]["observations"]
    assert payload["historical_operating_kpis"]["management_observations"]


def test_cli_both_family_handoff_and_reload(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli")
    _write_both_selected(dest, compsales=(2, 4), spsf=(100, 200))
    out = tmp_path / "out"
    validate, reconcile = _cli_validate_and_reconcile(dest, out)
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert reconcile.returncode == 0, reconcile.stdout + reconcile.stderr
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    assert admission["status"] == "admitted_unreconciled"
    assert admission["reconciliation"]["selected_count"] == 2
    standardized = json.loads((out / "standardized.json").read_text(encoding="utf-8"))
    rows = standardized["historical_operating_kpis"]["management_observations"]
    by_family = {row["family"]: row for row in rows}
    assert by_family[FAMILY_COMPARABLE_SALES_GROWTH]["value"] == 4
    assert by_family[FAMILY_SALES_PER_SQUARE_FOOT]["value"] == 200
    restored = standardized_from_payload(copy.deepcopy(standardized))
    assert standardized_to_payload(restored)["historical_operating_kpis"] == standardized[
        "historical_operating_kpis"
    ]
    extracted_copy = {path.name: path.read_bytes() for path in dest.glob("*.json")}
    validate2, reconcile2 = _cli_validate_and_reconcile(dest, tmp_path / "out2")
    assert validate2.returncode == 0
    assert reconcile2.returncode == 0
    after = {path.name: path.read_bytes() for path in dest.glob("*.json")}
    assert after == extracted_copy


def test_none_admission_returns_no_management_histories():
    axis = (date(2024, 1, 28),)
    assert selected_management_kpi_histories(None, model_periods=axis) == []
    assert deferred_management_kpi_disagreements(None, model_periods=axis) == []


def _mutate_family_definition(payload: dict, family: str, text: str) -> dict:
    payload = copy.deepcopy(payload)
    payload["kpi_definitions"][
        0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
    ]["definition"] = text
    return payload


@pytest.mark.parametrize("family", FAMILIES)
def test_ordinary_definition_disagreement_is_handed_off_without_admission(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "def-hand")
    other = (
        FAMILY_SALES_PER_SQUARE_FOOT
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_COMPARABLE_SALES_GROWTH
    )
    changed = (
        AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else AFFIRMATIVE_SPSF_DEFINITION + " changed"
    )
    _write_ordinary_agreeing_pair(
        dest,
        family,
        right_extra=lambda payload: _mutate_family_definition(payload, family, changed),
    )
    singleton_name = MANAGEMENT_NAMES[1]
    payload_doc = json.loads((dest / singleton_name).read_text(encoding="utf-8"))
    apply_other = (
        _apply_affirmative_spsf
        if other == FAMILY_SALES_PER_SQUARE_FOOT
        else _apply_affirmative_compsales
    )
    payload_doc = apply_other(payload_doc)
    payload_doc = _apply_same_period(payload_doc, other, period=SHARED_PERIOD, value=12)
    payload_doc = _attach_family_evidence(payload_doc, other, role="current")
    _write_json(dest / singleton_name, payload_doc)
    reconciled = _reconcile(dest)
    payload = management_admission_payload(reconciled.management_admission)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, "definition_mismatch", REASON_ORDINARY_DISAGREEMENT)
    _assert_handoff_diagnostic(reconciled.management_admission, selected=1)
    fin = standardize_reconciled(reconciled)
    assert _management_rows(fin, family=family, period=SHARED_PERIOD) == []
    other_rows = _management_rows(fin, family=other, period=SHARED_PERIOD)
    assert len(other_rows) == 1
    assert other_rows[0]["value"] == 12
    deferred = _deferred_rows(fin, family=family, period=SHARED_PERIOD)
    assert len(deferred) == 1
    record = deferred[0]
    assert "definition_mismatch" in record["reasons"]
    assert REASON_ORDINARY_DISAGREEMENT in record["reasons"]
    assert len(record["members"]) == 2
    texts = {member["definition_text"] for member in record["members"]}
    assert changed in texts
    locators = {member["locator"] for member in record["members"]}
    assert locators == set(group["locators"])
    serialized = json.dumps(standardized_to_payload(fin)["historical_operating_kpis"])
    assert "source_file" not in serialized
    assert "assurance" not in serialized
    assert "revision" not in serialized
    _assert_export_reload_export(fin)


@pytest.mark.parametrize("family", FAMILIES)
def test_value_only_ordinary_disagreement_is_not_handed_off_as_definition_conflict(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "val-hand")
    other = (
        FAMILY_SALES_PER_SQUARE_FOOT
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_COMPARABLE_SALES_GROWTH
    )
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=11,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="current"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="comparative"
        ),
    )
    singleton_name = MANAGEMENT_NAMES[1]
    payload_doc = json.loads((dest / singleton_name).read_text(encoding="utf-8"))
    apply_other = (
        _apply_affirmative_spsf
        if other == FAMILY_SALES_PER_SQUARE_FOOT
        else _apply_affirmative_compsales
    )
    payload_doc = apply_other(payload_doc)
    payload_doc = _apply_same_period(payload_doc, other, period=SHARED_PERIOD, value=12)
    payload_doc = _attach_family_evidence(payload_doc, other, role="current")
    _write_json(dest / singleton_name, payload_doc)
    reconciled = _reconcile(dest)
    payload = management_admission_payload(reconciled.management_admission)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, REASON_ORDINARY_DISAGREEMENT)
    assert "definition_mismatch" not in group["reasons"]
    fin = standardize_reconciled(reconciled)
    assert _management_rows(fin, family=family, period=SHARED_PERIOD) == []
    assert _deferred_rows(fin, family=family, period=SHARED_PERIOD) == []
    assert _management_rows(fin, family=other, period=SHARED_PERIOD)


@pytest.mark.parametrize("family", FAMILIES)
def test_revision_incompatible_definition_mismatch_is_not_ordinary_disagreement_handoff(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rev-hand")
    other = (
        FAMILY_SALES_PER_SQUARE_FOOT
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_COMPARABLE_SALES_GROWTH
    )
    changed = (
        AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else AFFIRMATIVE_SPSF_DEFINITION + " changed"
    )

    def mutate_right(payload: dict) -> dict:
        return _mutate_family_definition(payload, family, changed)

    _write_audited_revised_family_pair(dest, family, right_mutate=mutate_right)
    singleton_name = MANAGEMENT_NAMES[1]
    payload_doc = json.loads((dest / singleton_name).read_text(encoding="utf-8"))
    apply_other = (
        _apply_affirmative_spsf
        if other == FAMILY_SALES_PER_SQUARE_FOOT
        else _apply_affirmative_compsales
    )
    payload_doc = apply_other(payload_doc)
    payload_doc = _apply_same_period(payload_doc, other, period=SHARED_PERIOD, value=12)
    payload_doc = _attach_family_evidence(payload_doc, other, role="current")
    _write_json(dest / singleton_name, payload_doc)
    reconciled = _reconcile(dest)
    payload = management_admission_payload(reconciled.management_admission)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, "definition_mismatch")
    assert REASON_ORDINARY_DISAGREEMENT not in group["reasons"]
    fin = standardize_reconciled(reconciled)
    assert _management_rows(fin, family=family, period=SHARED_PERIOD) == []
    assert _deferred_rows(fin, family=family, period=SHARED_PERIOD) == []


def test_ordinary_repeat_missing_evidence_does_not_hand_off_disagreement(
    tmp_path: Path,
):
    family = FAMILY_SALES_PER_SQUARE_FOOT
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "miss-def")
    extra = _clear_week_adjustment(family)
    _write_ordinary_agreeing_pair(dest, family, right_extra=extra)
    payload_doc = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    payload_doc = _apply_affirmative_compsales(payload_doc)
    payload_doc = _apply_same_period(
        payload_doc, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=12
    )
    payload_doc = _attach_family_evidence(
        payload_doc, FAMILY_COMPARABLE_SALES_GROWTH, role="current"
    )
    _write_json(dest / MANAGEMENT_NAMES[1], payload_doc)
    reconciled = _reconcile(dest)
    payload = management_admission_payload(reconciled.management_admission)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, REASON_CALENDAR_WEEK)
    fin = standardize_reconciled(reconciled)
    assert _deferred_rows(fin, family=family, period=SHARED_PERIOD) == []
    assert _management_rows(fin, family=FAMILY_COMPARABLE_SALES_GROWTH)
