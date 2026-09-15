"""Geographic Q4-2023 segment fact extraction and supplemental selection."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.filing import (
    ExtractedStatementRow,
    FilingValue,
    PresentationRole,
    SourceRef,
    SupplementalFact,
)
from core.data.standardized_io import standardized_from_payload
from core.ingestion.filing_json import extracted_filing_to_payload, load_extracted_filing
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.filing_validator import validate_extracted_filing
from core.ingestion.geographic_segment import GEO_BRIDGE_TOLERANCE, GEO_NAMESPACE
from core.tests.test_filing_reconciler import _filing, _validated

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RECONCILED = BENCH / "reconciled"
NS = GEO_NAMESPACE

P2024 = date(2024, 12, 31)
P2025 = date(2025, 12, 31)


def _geo(
    identity: str,
    period: date,
    value: float,
    *,
    page: int = 80,
    role: PresentationRole = PresentationRole.CURRENT_PERIOD,
    label: str = "",
) -> SupplementalFact:
    return SupplementalFact(
        fact_type=f"{NS}.{identity}",
        period=period,
        value=value,
        status="reported",
        source=SourceRef(
            page=page,
            note="23 Segmented Information",
            label=label or identity,
        ),
        presentation_role=role.value,
    )


def _opinc(values: dict[date, tuple[float, PresentationRole]]) -> ExtractedStatementRow:
    return ExtractedStatementRow(
        label="Income from operations",
        section="",
        suggested_concept="operating_income",
        values={
            period: FilingValue(value=value, presentation_role=role)
            for period, (value, role) in values.items()
        },
        source=SourceRef(page=1, statement="Income Statement"),
    )


def _column_facts(
    period: date,
    *,
    page: int,
    role: PresentationRole,
    rev: tuple[int, int, int],
    ifop: tuple[int, int, int],
    corporate: int,
) -> tuple[SupplementalFact, ...]:
    a, cm, row = rev
    ia, icm, irow = ifop
    return (
        _geo("net_revenue.americas", period, a, page=page, role=role),
        _geo("net_revenue.china_mainland", period, cm, page=page, role=role),
        _geo("net_revenue.rest_of_world", period, row, page=page, role=role),
        _geo("net_revenue.segment_total", period, a + cm + row, page=page, role=role),
        _geo("net_revenue.consolidated", period, a + cm + row, page=page, role=role),
        _geo("income_from_operations.americas", period, ia, page=page, role=role),
        _geo("income_from_operations.china_mainland", period, icm, page=page, role=role),
        _geo("income_from_operations.rest_of_world", period, irow, page=page, role=role),
        _geo(
            "income_from_operations.segment_total",
            period,
            ia + icm + irow,
            page=page,
            role=role,
        ),
        _geo(
            "income_from_operations.corporate_unallocated",
            period,
            corporate,
            page=page,
            role=role,
        ),
        _geo(
            "income_from_operations.consolidated",
            period,
            ia + icm + irow + corporate,
            page=page,
            role=role,
        ),
    )


def _itemized_facts(period: date, *, page: int, role: PresentationRole) -> tuple[SupplementalFact, ...]:
    return (
        _geo("net_revenue.americas", period, 50, page=page, role=role),
        _geo("net_revenue.china_mainland", period, 30, page=page, role=role),
        _geo("net_revenue.rest_of_world", period, 20, page=page, role=role),
        _geo("net_revenue.consolidated", period, 100, page=page, role=role),
        _geo("income_from_operations.americas", period, 40, page=page, role=role),
        _geo("income_from_operations.china_mainland", period, 20, page=page, role=role),
        _geo("income_from_operations.rest_of_world", period, 10, page=page, role=role),
        _geo("income_from_operations.segment_total", period, 70, page=page, role=role),
        _geo("income_from_operations.consolidated", period, 55, page=page, role=role),
        _geo("ifop_reconciling.general_corporate_expenses", period, 12, page=page, role=role),
        _geo("ifop_reconciling.amortization_of_intangible_assets", period, 3, page=page, role=role),
    )


def test_empty_note_facts_skip_geographic_selection(tmp_path: Path):
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (110.0, PresentationRole.CURRENT_PERIOD)},
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    assert reconciled.note_facts == ()
    assert reconciled.selected_geographic_facts == ()
    provenance = reconciliation_provenance_payload(reconciled)
    assert "selected_geographic_segment_facts" not in provenance
    assert provenance["note_facts"] == []


def test_lease_and_share_facts_unchanged_with_empty_geo(tmp_path: Path):
    lease = SupplementalFact(
        fact_type="lease_interest_expense",
        period=P2025,
        value=12.0,
        status="reported",
        source=SourceRef(page=14, note="17 Leases"),
    )
    share = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=P2025,
        value=100.0,
        status="reported",
        source=SourceRef(page=18, note="EPS"),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(lease,),
        share_facts=(share,),
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    assert len(reconciled.note_facts) == 1
    assert reconciled.note_facts[0].fact.fact_type == "lease_interest_expense"
    assert len(reconciled.share_facts) == 1
    assert reconciled.selected_geographic_facts == ()
    assert reconciled.supplemental_conflicts == ()


def test_latest_source_precedence_and_retained_losers(tmp_path: Path):
    early = _column_facts(
        P2024,
        page=84,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(70, 20, 10),
        ifop=(40, 15, 5),
        corporate=-20,
    )
    later = _column_facts(
        P2024,
        page=80,
        role=PresentationRole.COMPARATIVE,
        rev=(70, 20, 10),
        ifop=(41, 15, 5),
        corporate=-20,
    )
    later_current = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={P2024: (100.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2024: (40.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=early,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            P2024: (100.0, PresentationRole.COMPARATIVE),
            P2025: (120.0, PresentationRole.CURRENT_PERIOD),
        },
        extra_rows=(
            _opinc(
                {
                    P2024: (41.0, PresentationRole.COMPARATIVE),
                    P2025: (50.0, PresentationRole.CURRENT_PERIOD),
                }
            ),
        ),
        note_facts=later + later_current,
    )
    order_a = [
        _validated(tmp_path, f2024, b"2024"),
        _validated(tmp_path, f2025, b"2025"),
    ]
    order_b = list(reversed(order_a))
    first = reconcile_filings(order_a)
    second = reconcile_filings(order_b)
    assert first.selected_geographic_facts == second.selected_geographic_facts
    selected_2024 = [
        item
        for item in first.selected_geographic_facts
        if item.period == P2024 and item.fact_type.endswith("income_from_operations.americas")
    ]
    assert len(selected_2024) == 1
    assert selected_2024[0].value == 41
    assert selected_2024[0].filing_year == 2025
    assert selected_2024[0].selection_reason == "later_audited_presentation"
    assert selected_2024[0].presentation_basis == PresentationRole.COMPARATIVE.value
    losers = [
        obs
        for obs in first.note_facts
        if obs.fact.fact_type.endswith("income_from_operations.americas")
        and obs.fact.period == P2024
    ]
    assert {obs.filing_year for obs in losers} == {2024, 2025}
    assert any(obs.fact.value == 40 for obs in losers)


def test_overlapping_equal_observations_still_keep_losers(tmp_path: Path):
    facts_2024 = _column_facts(
        P2024,
        page=84,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(70, 20, 10),
        ifop=(40, 15, 5),
        corporate=-20,
    )
    facts_2025 = _column_facts(
        P2024,
        page=80,
        role=PresentationRole.COMPARATIVE,
        rev=(70, 20, 10),
        ifop=(40, 15, 5),
        corporate=-20,
    ) + _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={P2024: (100.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2024: (40.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts_2024,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            P2024: (100.0, PresentationRole.COMPARATIVE),
            P2025: (120.0, PresentationRole.CURRENT_PERIOD),
        },
        extra_rows=(
            _opinc(
                {
                    P2024: (40.0, PresentationRole.COMPARATIVE),
                    P2025: (50.0, PresentationRole.CURRENT_PERIOD),
                }
            ),
        ),
        note_facts=facts_2025,
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    assert reconciled.supplemental_conflicts == ()
    selected = [
        item
        for item in reconciled.selected_geographic_facts
        if item.period == P2024 and item.fact_type.endswith("net_revenue.americas")
    ][0]
    assert selected.value == 70
    assert selected.filing_year == 2025
    assert selected.selection_reason == "later_audited_presentation"
    assert (
        sum(
            1
            for obs in reconciled.note_facts
            if obs.fact.fact_type.endswith("net_revenue.americas") and obs.fact.period == P2024
        )
        == 2
    )


def test_missing_segment_fails_closed(tmp_path: Path):
    facts = list(
        _column_facts(
            P2025,
            page=80,
            role=PresentationRole.CURRENT_PERIOD,
            rev=(80, 25, 15),
            ifop=(50, 18, 7),
            corporate=-25,
        )
    )
    facts = [f for f in facts if not f.fact_type.endswith("net_revenue.americas")]
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=tuple(facts),
    )
    with pytest.raises(ValueError, match="incomplete geographic bridge group"):
        reconcile_filings([_validated(tmp_path, f2025, b"2025")])


def test_mixed_channel_definition_fails_closed(tmp_path: Path):
    facts = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    ) + (
        SupplementalFact(
            fact_type="segment.channel.net_revenue.stores",
            period=P2025,
            value=40,
            status="reported",
            source=SourceRef(page=78, note="22"),
            presentation_role=PresentationRole.CURRENT_PERIOD.value,
        ),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts,
    )
    with pytest.raises(ValueError, match="incompatible segment definition"):
        reconcile_filings([_validated(tmp_path, f2025, b"2025")])


def test_unknown_identity_and_invalid_value_fail_closed(tmp_path: Path):
    unknown = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    ) + (
        _geo("net_revenue.americas.millions", P2025, 80),
    )
    f_unknown = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=unknown,
    )
    with pytest.raises(ValueError, match="unknown"):
        reconcile_filings([_validated(tmp_path, f_unknown, b"2025")])

    complete = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    missing_role = SupplementalFact(
        fact_type=f"{NS}.net_revenue.americas",
        period=P2025,
        value=80,
        status="reported",
        source=SourceRef(page=80, note="23 Segmented Information", label="Americas"),
    )
    facts = tuple(
        missing_role if f.fact_type.endswith("net_revenue.americas") else f
        for f in complete
    )
    f_role = _filing(
        year=2025,
        source_file="b2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts,
    )
    with pytest.raises(ValueError, match="presentation_role"):
        reconcile_filings([_validated(tmp_path, f_role, b"2025b")])


def test_corporate_double_counting_fails_closed(tmp_path: Path):
    facts = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    ) + (
        _geo("ifop_reconciling.general_corporate_expenses", P2025, 25),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts,
    )
    with pytest.raises(ValueError, match="corporate double counting"):
        reconcile_filings([_validated(tmp_path, f2025, b"2025")])


def test_bridge_mismatch_fails_closed(tmp_path: Path):
    facts = list(
        _column_facts(
            P2025,
            page=80,
            role=PresentationRole.CURRENT_PERIOD,
            rev=(80, 25, 15),
            ifop=(50, 18, 7),
            corporate=-25,
        )
    )
    facts = [
        _geo("net_revenue.consolidated", P2025, 999)
        if f.fact_type.endswith("net_revenue.consolidated")
        else f
        for f in facts
    ]
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (120.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=tuple(facts),
    )
    with pytest.raises(ValueError, match="revenue bridge mismatch"):
        reconcile_filings([_validated(tmp_path, f2025, b"2025")])


def test_equal_priority_contradiction_fails_closed(tmp_path: Path):
    facts_a = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    facts_b = _column_facts(
        P2025,
        page=81,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(81, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    f_a = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (121.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts_a,
    )
    f_b = _filing(
        year=2025,
        source_file="b2025.pdf",
        revenue_values={P2025: (121.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts_b,
    )
    with pytest.raises(ValueError, match="equal-priority"):
        reconcile_filings(
            [
                _validated(tmp_path, f_a, b"2025a"),
                _validated(tmp_path, f_b, b"2025b"),
            ]
        )


def test_failure_does_not_emit_partial_selection(tmp_path: Path):
    facts = _column_facts(
        P2025,
        page=80,
        role=PresentationRole.CURRENT_PERIOD,
        rev=(80, 25, 15),
        ifop=(50, 18, 7),
        corporate=-25,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (999.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (50.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts,
    )
    with pytest.raises(ValueError, match="disagrees with IS revenue"):
        reconcile_filings([_validated(tmp_path, f2025, b"2025")])


def test_itemized_bridge_and_no_statement_promotion(tmp_path: Path):
    facts = _itemized_facts(P2025, page=84, role=PresentationRole.CURRENT_PERIOD)
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={P2025: (100.0, PresentationRole.CURRENT_PERIOD)},
        extra_rows=(_opinc({P2025: (55.0, PresentationRole.CURRENT_PERIOD)}),),
        note_facts=facts,
    )
    reconciled = reconcile_filings([_validated(tmp_path, f2025, b"2025")])
    assert any(
        item.presentation_family == "itemized_reconciling"
        for item in reconciled.selected_geographic_facts
    )
    fin = standardize_reconciled(reconciled)
    assert all(
        not (item.concept or "").startswith("segment.geo")
        for item in (*fin.income_statement, *fin.balance_sheet, *fin.cash_flow)
    )
    provenance = reconciliation_provenance_payload(reconciled)
    assert provenance["selected_geographic_segment_facts"]
    assert GEO_BRIDGE_TOLERANCE == 0.0


def test_lululemon_extracted_filings_round_trip_and_five_period_bridges():
    fy2022 = load_extracted_filing(EXTRACTED / "LULU_FY2022.json")
    fy2023 = load_extracted_filing(EXTRACTED / "LULU_FY2023.json")
    fy2024 = load_extracted_filing(EXTRACTED / "LULU_FY2024.json")
    fy2025 = load_extracted_filing(EXTRACTED / "LULU_FY2025.json")
    assert fy2022.note_facts == ()
    assert extracted_filing_to_payload(fy2023)["note_facts"]
    assert extracted_filing_to_payload(fy2024)["note_facts"]
    assert extracted_filing_to_payload(fy2025)["note_facts"]

    validated = []
    for filing in (fy2022, fy2023, fy2024, fy2025):
        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        validated.append((filing, report))
    reconciled = reconcile_filings(
        validated,
        admit_periods=(date(2022, 1, 30),),
    )
    assert GEO_BRIDGE_TOLERANCE == 0.0
    selected = reconciled.selected_geographic_facts
    by_period = {}
    for item in selected:
        by_period.setdefault(item.period, []).append(item)

    expected_sources = {
        date(2022, 1, 30): (2023, "itemized_reconciling"),
        date(2023, 1, 29): (2024, "corporate_column"),
        date(2024, 1, 28): (2025, "corporate_column"),
        date(2025, 2, 2): (2025, "corporate_column"),
        date(2026, 2, 1): (2025, "corporate_column"),
    }
    assert set(by_period) == set(expected_sources)
    for period, (year, family) in expected_sources.items():
        sample = by_period[period][0]
        assert sample.filing_year == year
        assert sample.presentation_family == family

    current = {
        item.fact_type.replace(f"{NS}.", ""): item.value
        for item in by_period[date(2026, 2, 1)]
    }
    assert current["income_from_operations.americas"] == 2560658
    assert current["income_from_operations.china_mainland"] == 701123
    assert current["income_from_operations.rest_of_world"] == 345901
    assert current["income_from_operations.segment_total"] == 3607682
    assert current["income_from_operations.corporate_unallocated"] == -1397067
    assert current["income_from_operations.consolidated"] == 2210615
    assert (
        current["income_from_operations.segment_total"]
        + current["income_from_operations.corporate_unallocated"]
        == current["income_from_operations.consolidated"]
    )

    fy2023_2022 = [
        obs
        for obs in reconciled.note_facts
        if obs.filing_year == 2023 and obs.fact.period == date(2024, 1, 28)
    ]
    fy2025_2022 = [
        obs
        for obs in reconciled.note_facts
        if obs.filing_year == 2025 and obs.fact.period == date(2024, 1, 28)
    ]
    assert fy2023_2022 and fy2025_2022

    fin = standardize_reconciled(reconciled)
    assert all(
        "segment.geo" not in (item.concept or "")
        for item in (*fin.income_statement, *fin.balance_sheet, *fin.cash_flow)
    )
    committed_std = json.loads((RECONCILED / "standardized.json").read_text())
    from core.data.standardized_io import standardized_to_payload

    assert standardized_to_payload(fin) == committed_std
    committed_conflicts = json.loads((RECONCILED / "conflicts.json").read_text())
    live_conflicts = reconciliation_conflicts_payload(reconciled)
    assert live_conflicts == committed_conflicts
    provenance = reconciliation_provenance_payload(reconciled)
    assert provenance["selected_geographic_segment_facts"]
    assert provenance["note_facts"]
    assert fy2022.filing.source_sha256 == hashlib.sha256(
        (SOURCE / fy2022.filing.source_file).read_bytes()
    ).hexdigest()
