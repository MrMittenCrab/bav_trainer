"""Optional historical geographic segment analytical series."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.historical_segments import (
    FAMILY_CORPORATE,
    FAMILY_ITEMIZED,
    IFOP_CORPORATE,
    OP_ADD,
    OP_SUBTRACT,
    SEGMENTS,
    SEGMENT_BRIDGE_TOLERANCE,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_json import load_extracted_filing
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.filing_validator import validate_extracted_filing
from core.model.geographic_segment import (
    GEOGRAPHIC_RATIO_TOLERANCE,
    REPORTED_OPERATING_MARGIN_BASIS,
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from core.model.line_resolver import MissingLineError
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, ratio_or_na
from core.tests.test_geographic_segment_facts import (
    _lululemon_validated,
    _mutate_fy2025_prior_2025,
)
from core.tests.test_historical_segment import (
    _base_payload,
    _corp_values,
    _fin_with_segment,
    _snapshot,
)

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT / "benchmark" / "lululemon" / "extracted"
SOURCE = ROOT / "benchmark" / "lululemon" / "source"
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
P0 = date(2023, 12, 31)
P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)
ADMIT_2022 = date(2022, 1, 30)
FY2025_AMERICAS = date(2025, 2, 2)
FY2026 = date(2026, 2, 1)


def _independent_from_snapshots(axis: list[date], snapshots: dict):
    """Recompute mix/growth/margins/bridges from snapshot values only."""
    expected = {}
    prior = None
    for index, period in enumerate(axis):
        snapshot = snapshots.get(period)
        opening = index == 0
        if snapshot is None:
            expected[period] = {
                "family": SOURCE_UNAVAILABLE,
                "revenue": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "ifop": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "share": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "growth": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "margin": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "rev_total": SOURCE_UNAVAILABLE,
                "ifop_total": SOURCE_UNAVAILABLE,
                "signed": SOURCE_UNAVAILABLE,
                "reconstructed": SOURCE_UNAVAILABLE,
                "cons_rev": SOURCE_UNAVAILABLE,
                "cons_ifop": SOURCE_UNAVAILABLE,
                "rev_diff": SOURCE_UNAVAILABLE,
                "ifop_diff": SOURCE_UNAVAILABLE,
            }
            prior = None
            continue
        revenue = {name: float(snapshot.values[f"net_revenue.{name}"]) for name in SEGMENTS}
        ifop = {
            name: float(snapshot.values[f"income_from_operations.{name}"])
            for name in SEGMENTS
        }
        cons_rev = float(snapshot.values["net_revenue.consolidated"])
        cons_ifop = float(snapshot.values["income_from_operations.consolidated"])
        rev_total = sum(revenue[name] for name in SEGMENTS)
        ifop_total = sum(ifop[name] for name in SEGMENTS)
        signed = []
        for identity in sorted(snapshot.bridge_operations):
            operation = snapshot.bridge_operations[identity]
            amount = float(snapshot.values[identity])
            signed.append((identity, amount if operation == OP_ADD else -amount))
        reconstructed = ifop_total + sum(amount for _, amount in signed)
        if opening:
            growth = {name: None for name in SEGMENTS}
        elif prior is None:
            growth = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
        else:
            growth = {
                name: ratio_or_na(revenue[name] - prior[name], prior[name])
                for name in SEGMENTS
            }
        expected[period] = {
            "family": snapshot.presentation_family,
            "revenue": revenue,
            "ifop": ifop,
            "share": {name: ratio_or_na(revenue[name], cons_rev) for name in SEGMENTS},
            "growth": growth,
            "margin": {name: ratio_or_na(ifop[name], revenue[name]) for name in SEGMENTS},
            "rev_total": rev_total,
            "ifop_total": ifop_total,
            "signed": tuple(signed),
            "reconstructed": reconstructed,
            "cons_rev": cons_rev,
            "cons_ifop": cons_ifop,
            "rev_diff": rev_total - cons_rev,
            "ifop_diff": reconstructed - cons_ifop,
        }
        prior = revenue
    return expected


def _assert_series_matches(series, expected) -> None:
    assert series.periods == tuple(expected)
    assert series.identities == SEGMENTS
    for period, row in expected.items():
        assert series.presentation_family[period] == row["family"]
        assert series.net_revenue[period] == row["revenue"]
        assert series.income_from_operations[period] == row["ifop"]
        assert series.revenue_share[period] == row["share"]
        assert series.revenue_growth[period] == row["growth"]
        assert series.reported_operating_margin[period] == row["margin"]
        assert series.calculated_segment_revenue_total[period] == row["rev_total"]
        assert series.calculated_segment_operating_profit_total[period] == row["ifop_total"]
        assert series.signed_reconciling_contributions[period] == row["signed"]
        assert series.reconstructed_consolidated_operating_profit[period] == row["reconstructed"]
        assert series.reported_consolidated_revenue[period] == row["cons_rev"]
        assert series.reported_consolidated_operating_profit[period] == row["cons_ifop"]
        assert series.consolidated_revenue_difference[period] == row["rev_diff"]
        assert series.consolidated_operating_profit_difference[period] == row["ifop_diff"]
        if all(isinstance(value, float) for value in row["share"].values()):
            assert abs(sum(row["share"].values()) - 1.0) <= GEOGRAPHIC_RATIO_TOLERANCE
        if isinstance(row["rev_diff"], float):
            assert abs(row["rev_diff"]) <= SEGMENT_BRIDGE_TOLERANCE
        if isinstance(row["ifop_diff"], float):
            assert abs(row["ifop_diff"]) <= SEGMENT_BRIDGE_TOLERANCE


def test_absent_and_null_payloads_make_module_absent():
    payload = _base_payload()
    absent = standardized_from_payload(payload)
    assert geographic_segment_applicable(absent) is False
    with pytest.raises(MissingLineError, match="geographic segment sources not available"):
        compute_geographic_segment_series(absent)

    payload["historical_segment"] = None
    null = standardized_from_payload(payload)
    assert geographic_segment_applicable(null) is False
    with pytest.raises(MissingLineError, match="geographic segment sources not available"):
        compute_geographic_segment_series(null)


def test_legacy_fast_retailing_payload_omits_segment_module():
    payload = json.loads(FR_JSON.read_text(encoding="utf-8"))
    assert "historical_segment" not in payload
    fin = standardized_from_payload(payload)
    assert fin.historical_segment is None
    assert geographic_segment_applicable(fin) is False
    with pytest.raises(MissingLineError, match="geographic segment sources not available"):
        compute_geographic_segment_series(fin)
    assert "historical_segment" not in standardized_to_payload(fin)


def test_both_presentation_families_and_reordered_inputs():
    itemized = _snapshot(P1, family=FAMILY_ITEMIZED)
    corporate = _snapshot(P2)
    fin = _fin_with_segment(itemized, corporate)
    before = copy.deepcopy(fin.historical_segment)
    series = compute_geographic_segment_series(fin)
    expected = _independent_from_snapshots(
        canonical_fiscal_periods(fin),
        {snap.period: snap for snap in fin.historical_segment.periods},
    )
    _assert_series_matches(series, expected)
    assert series.presentation_family[P1] == FAMILY_ITEMIZED
    assert series.presentation_family[P2] == FAMILY_CORPORATE
    assert series.revenue_growth[P1]["americas"] is None
    assert series.signed_reconciling_contributions[P1] == (
        ("ifop_reconciling.amortization_of_intangible_assets", -3.0),
        ("ifop_reconciling.general_corporate_expenses", -12.0),
    )
    assert series.signed_reconciling_contributions[P2] == ((IFOP_CORPORATE, -25.0),)
    assert fin.historical_segment == before

    fin.historical_segment.periods = list(reversed(list(fin.historical_segment.periods)))
    reordered = compute_geographic_segment_series(fin)
    assert reordered == series
    assert [snap.period for snap in fin.historical_segment.periods] == [P2, P1]


def test_sparse_snapshots_do_not_compress_or_substitute_periods():
    fin = _fin_with_segment(
        _snapshot(P0),
        _snapshot(P2, values=_corp_values(rev=(90.0, 30.0, 20.0), ifop=(40.0, 12.0, 8.0))),
        extra_periods=[P0, P1, P2],
    )
    series = compute_geographic_segment_series(fin)
    expected = _independent_from_snapshots(
        [P0, P1, P2],
        {snap.period: snap for snap in fin.historical_segment.periods},
    )
    _assert_series_matches(series, expected)
    assert series.periods == (P0, P1, P2)
    assert series.revenue_growth[P0]["americas"] is None
    assert series.net_revenue[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_share[P1]["china_mainland"] == SOURCE_UNAVAILABLE
    assert series.reported_operating_margin[P1]["rest_of_world"] == SOURCE_UNAVAILABLE
    assert series.signed_reconciling_contributions[P1] == SOURCE_UNAVAILABLE
    assert series.revenue_growth[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_growth[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.net_revenue[P2]["americas"] == 90.0
    p0_rev = series.net_revenue[P0]["americas"]
    p2_rev = series.net_revenue[P2]["americas"]
    assert p0_rev != SOURCE_UNAVAILABLE and p2_rev != SOURCE_UNAVAILABLE
    skipped = ratio_or_na(p2_rev - p0_rev, p0_rev)
    assert series.revenue_growth[P2]["americas"] != skipped


def test_zero_denominators_zero_numerators_and_negative_profits():
    opening = _snapshot(
        P1,
        values=_corp_values(rev=(0.0, 50.0, 50.0), ifop=(0.0, 10.0, -5.0), corporate=-5.0),
    )
    later = _snapshot(
        P2,
        values=_corp_values(rev=(10.0, 0.0, 50.0), ifop=(-2.0, 8.0, 0.0), corporate=-6.0),
    )
    fin = _fin_with_segment(opening, later)
    series = compute_geographic_segment_series(fin)
    expected = _independent_from_snapshots(
        [P1, P2],
        {snap.period: snap for snap in fin.historical_segment.periods},
    )
    _assert_series_matches(series, expected)
    assert series.net_revenue[P1]["americas"] == 0.0
    assert series.income_from_operations[P1]["americas"] == 0.0
    assert series.revenue_share[P1]["americas"] == 0.0
    assert series.reported_operating_margin[P1]["americas"] == UNDEFINED_RATIO
    assert series.reported_operating_margin[P1]["rest_of_world"] == -0.1
    assert series.income_from_operations[P2]["americas"] == -2.0
    assert series.reported_operating_margin[P2]["americas"] == -0.2
    assert series.net_revenue[P2]["china_mainland"] == 0.0
    assert series.reported_operating_margin[P2]["china_mainland"] == UNDEFINED_RATIO
    assert series.income_from_operations[P2]["rest_of_world"] == 0.0
    assert series.reported_operating_margin[P2]["rest_of_world"] == 0.0
    assert series.revenue_growth[P2]["americas"] == UNDEFINED_RATIO
    assert series.revenue_growth[P2]["china_mainland"] == -1.0
    assert REPORTED_OPERATING_MARGIN_BASIS == "income_from_operations / net_revenue"
    assert "nopat" not in REPORTED_OPERATING_MARGIN_BASIS.lower()
    assert not hasattr(series, "nopat_margin")


def test_invalid_contracts_fail_closed_without_mutation():
    fin = _fin_with_segment(_snapshot(P2))
    original = copy.deepcopy(fin.historical_segment)

    fin.historical_segment.periods[0].bridge_operations = {IFOP_CORPORATE: OP_SUBTRACT}
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError, match="bridge operations contradict"):
        compute_geographic_segment_series(fin)
    assert fin.historical_segment == mutated

    fin.historical_segment = copy.deepcopy(original)
    fin.historical_segment.periods[0].values["net_revenue.americas"] += 10
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError, match="revenue bridge mismatch"):
        compute_geographic_segment_series(fin)
    assert fin.historical_segment == mutated

    fin.historical_segment = copy.deepcopy(original)
    fin.historical_segment.periods[0].values["net_revenue.prc"] = 1.0
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError, match="unknown"):
        compute_geographic_segment_series(fin)
    assert fin.historical_segment == mutated

    fin.historical_segment = copy.deepcopy(original)
    fin.historical_segment.periods[0].values["channel.ecomm"] = 1.0
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError, match="unknown"):
        compute_geographic_segment_series(fin)
    assert fin.historical_segment == mutated

    fin.historical_segment = copy.deepcopy(original)
    fin.historical_segment.namespace = "segment.geo.other"
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError, match="unsupported geographic namespace"):
        compute_geographic_segment_series(fin)
    assert fin.historical_segment == mutated

    fin.historical_segment = copy.deepcopy(original)
    with pytest.raises(ValueError, match="canonical fiscal axis"):
        compute_geographic_segment_series(fin, [P2, P1])
    assert fin.historical_segment == original


def _reload_admitted_lululemon():
    reconciled = reconcile_filings(
        _lululemon_validated(),
        admit_periods=(ADMIT_2022,),
    )
    fin = standardize_reconciled(reconciled)
    restored = standardized_from_payload(
        json.loads(json.dumps(standardized_to_payload(fin)))
    )
    return reconciled, fin, restored


def test_lululemon_five_period_json_reload_matches_independent_calculation():
    reconciled, fin, restored = _reload_admitted_lululemon()
    assert restored.historical_segment == fin.historical_segment
    prefix = "segment.geo.q4_2023."
    selected_on_axis = {
        (item.period, item.fact_type[len(prefix) :]): item.value
        for item in reconciled.selected_geographic_facts
        if item.period in set(reconciled.periods)
    }
    model_values = {
        (snap.period, identity): value
        for snap in restored.historical_segment.periods
        for identity, value in snap.values.items()
    }
    assert model_values == selected_on_axis
    assert len(model_values) == 56

    axis = canonical_fiscal_periods(restored)
    assert axis == [
        date(2022, 1, 30),
        date(2023, 1, 29),
        date(2024, 1, 28),
        date(2025, 2, 2),
        date(2026, 2, 1),
    ]
    snapshots = {snap.period: snap for snap in restored.historical_segment.periods}
    assert set(snapshots) == set(axis)
    series = compute_geographic_segment_series(restored)
    expected = _independent_from_snapshots(axis, snapshots)
    _assert_series_matches(series, expected)

    assert series.presentation_family[ADMIT_2022] == FAMILY_ITEMIZED
    for period in axis[1:]:
        assert series.presentation_family[period] == FAMILY_CORPORATE
    fy2026 = snapshots[FY2026]
    assert fy2026.values["income_from_operations.segment_total"] == 3607682
    assert fy2026.values[IFOP_CORPORATE] == -1397067
    assert fy2026.values["income_from_operations.consolidated"] == 2210615
    assert 3607682 - 1397067 == 2210615
    assert series.calculated_segment_operating_profit_total[FY2026] == 3607682
    assert series.signed_reconciling_contributions[FY2026] == ((IFOP_CORPORATE, -1397067.0),)
    assert series.reconstructed_consolidated_operating_profit[FY2026] == 2210615
    assert series.consolidated_operating_profit_difference[FY2026] == 0.0
    assert series.consolidated_revenue_difference[FY2026] == 0.0
    for period in axis:
        assert series.consolidated_revenue_difference[period] == 0.0
        assert series.consolidated_operating_profit_difference[period] == 0.0
        assert series.revenue_growth[period]["americas"] is None or isinstance(
            series.revenue_growth[period]["americas"], float
        )


def test_prior_presentation_mutation_keeps_selected_americas_and_series():
    original_fy2025 = json.loads(
        (EXTRACTED / "LULU_FY2025.json").read_text(encoding="utf-8")
    )
    baseline_reconciled, _, baseline = _reload_admitted_lululemon()
    baseline_series = compute_geographic_segment_series(baseline)

    fy2022 = load_extracted_filing(EXTRACTED / "LULU_FY2022.json")
    fy2023 = load_extracted_filing(EXTRACTED / "LULU_FY2023.json")
    fy2024 = load_extracted_filing(EXTRACTED / "LULU_FY2024.json")
    fy2025 = _mutate_fy2025_prior_2025(load_extracted_filing(EXTRACTED / "LULU_FY2025.json"))
    validated = []
    for filing in (fy2022, fy2023, fy2024, fy2025):
        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        validated.append((filing, report))
    for order in (validated, list(reversed(validated))):
        reconciled = reconcile_filings(order, admit_periods=(ADMIT_2022,))
        americas = [
            item
            for item in reconciled.selected_geographic_facts
            if item.period == FY2025_AMERICAS
            and item.fact_type.endswith("net_revenue.americas")
        ]
        assert len(americas) == 1
        assert americas[0].value == 7928156
        superseded = [
            obs
            for obs in reconciled.note_facts
            if obs.fact.period == FY2025_AMERICAS
            and obs.fact.fact_type.endswith("net_revenue.americas")
            and obs.filing_year == 2025
        ]
        assert len(superseded) == 1
        assert superseded[0].fact.value == 7928256
        provenance = reconciliation_provenance_payload(reconciled)
        assert any(
            obs["value"] == 7928256 and obs["presentation_role"] == "prior_presentation"
            for obs in provenance["note_facts"]
            if obs["period"] == FY2025_AMERICAS.isoformat()
            and obs["fact_type"].endswith("net_revenue.americas")
        )
        restored = standardized_from_payload(
            json.loads(json.dumps(standardized_to_payload(standardize_reconciled(reconciled))))
        )
        series = compute_geographic_segment_series(restored)
        assert series.net_revenue[FY2025_AMERICAS]["americas"] == 7928156
        assert 7928256 not in {
            series.net_revenue[period][name]
            for period in series.periods
            for name in SEGMENTS
        }
        assert series == baseline_series
        payload = standardized_to_payload(restored)
        assert "7928256" not in json.dumps(payload["historical_segment"])
    reloaded = json.loads((EXTRACTED / "LULU_FY2025.json").read_text(encoding="utf-8"))
    assert reloaded == original_fy2025
    assert len(baseline_reconciled.selected_geographic_facts) >= 56
