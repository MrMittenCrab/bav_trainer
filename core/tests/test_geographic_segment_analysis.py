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
    _itemized_values,
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


def _pp(numerator: float, denominator: float):
    raw = ratio_or_na(numerator, denominator)
    return 100.0 * raw if isinstance(raw, float) else raw


def _delta(current, prior, *, opening: bool):
    if opening:
        return None
    if (
        current is None
        or prior is None
        or current == SOURCE_UNAVAILABLE
        or prior == SOURCE_UNAVAILABLE
    ):
        return SOURCE_UNAVAILABLE
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _independent_from_snapshots(axis: list[date], snapshots: dict):
    """Recompute mix/growth/margins/bridges from snapshot values only."""
    expected = {}
    prior = None
    prior_cons = None
    prior_ifop = None
    prior_cons_ifop = None
    prior_recon_sum = None
    prior_cs = None
    prior_b = None
    prior_m = None
    prior_share = None
    prior_seg_m = None
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
                "contrib": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "cons_growth": None if opening else SOURCE_UNAVAILABLE,
                "residual": None if opening else SOURCE_UNAVAILABLE,
                "margin": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "cs": {name: SOURCE_UNAVAILABLE for name in SEGMENTS},
                "b": SOURCE_UNAVAILABLE,
                "m": SOURCE_UNAVAILABLE,
                "e": SOURCE_UNAVAILABLE,
                "dcs": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "db": None if opening else SOURCE_UNAVAILABLE,
                "dm": None if opening else SOURCE_UNAVAILABLE,
                "de": None if opening else SOURCE_UNAVAILABLE,
                "mix": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "within": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "mix_res": None if opening else SOURCE_UNAVAILABLE,
                "dp": (
                    {name: None for name in SEGMENTS}
                    if opening
                    else {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
                ),
                "dbr": None if opening else SOURCE_UNAVAILABLE,
                "dpc": None if opening else SOURCE_UNAVAILABLE,
                "dpr": None if opening else SOURCE_UNAVAILABLE,
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
            prior_cons = None
            prior_ifop = None
            prior_cons_ifop = None
            prior_recon_sum = None
            prior_cs = None
            prior_b = None
            prior_m = None
            prior_share = None
            prior_seg_m = None
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
            contrib = {name: None for name in SEGMENTS}
            cons_growth = None
            residual = None
        elif prior is None or prior_cons is None:
            growth = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            contrib = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            cons_growth = SOURCE_UNAVAILABLE
            residual = SOURCE_UNAVAILABLE
        else:
            growth = {
                name: ratio_or_na(revenue[name] - prior[name], prior[name])
                for name in SEGMENTS
            }
            contrib = {}
            for name in SEGMENTS:
                raw = ratio_or_na(revenue[name] - prior[name], prior_cons)
                contrib[name] = 100.0 * raw if isinstance(raw, float) else raw
            cons_growth = ratio_or_na(cons_rev - prior_cons, prior_cons)
            if cons_growth == SOURCE_UNAVAILABLE or any(
                value == SOURCE_UNAVAILABLE for value in contrib.values()
            ):
                residual = SOURCE_UNAVAILABLE
            elif cons_growth == UNDEFINED_RATIO or any(
                value == UNDEFINED_RATIO for value in contrib.values()
            ):
                residual = UNDEFINED_RATIO
            else:
                residual = 100.0 * cons_growth - sum(contrib[name] for name in SEGMENTS)
        cs = {name: _pp(ifop[name], cons_rev) for name in SEGMENTS}
        b = _pp(sum(amount for _, amount in signed), cons_rev)
        m = _pp(cons_ifop, cons_rev)
        if (
            m == SOURCE_UNAVAILABLE
            or b == SOURCE_UNAVAILABLE
            or any(value == SOURCE_UNAVAILABLE for value in cs.values())
        ):
            e = SOURCE_UNAVAILABLE
        elif (
            m == UNDEFINED_RATIO
            or b == UNDEFINED_RATIO
            or any(value == UNDEFINED_RATIO for value in cs.values())
        ):
            e = UNDEFINED_RATIO
        else:
            e = float(m) - sum(float(cs[name]) for name in SEGMENTS) - float(b)
        if opening:
            dcs = {name: None for name in SEGMENTS}
            db = None
            dm = None
            de = None
        elif prior_cs is None or prior_b is None or prior_m is None:
            dcs = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            db = SOURCE_UNAVAILABLE
            dm = SOURCE_UNAVAILABLE
            de = SOURCE_UNAVAILABLE
        else:
            dcs = {
                name: _delta(cs[name], prior_cs[name], opening=False)
                for name in SEGMENTS
            }
            db = _delta(b, prior_b, opening=False)
            dm = _delta(m, prior_m, opening=False)
            if (
                dm == SOURCE_UNAVAILABLE
                or db == SOURCE_UNAVAILABLE
                or any(value == SOURCE_UNAVAILABLE for value in dcs.values())
            ):
                de = SOURCE_UNAVAILABLE
            elif (
                dm == UNDEFINED_RATIO
                or db == UNDEFINED_RATIO
                or any(value == UNDEFINED_RATIO for value in dcs.values())
            ):
                de = UNDEFINED_RATIO
            else:
                de = float(dm) - sum(float(dcs[name]) for name in SEGMENTS) - float(db)
        share = {name: ratio_or_na(revenue[name], cons_rev) for name in SEGMENTS}
        seg_m = {name: ratio_or_na(ifop[name], revenue[name]) for name in SEGMENTS}
        if opening:
            mix = {name: None for name in SEGMENTS}
            within = {name: None for name in SEGMENTS}
            mix_res = None
        elif prior_share is None or prior_seg_m is None:
            mix = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            within = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            mix_res = SOURCE_UNAVAILABLE
        else:
            mix = {}
            within = {}
            for name in SEGMENTS:
                inputs = (share[name], prior_share[name], seg_m[name], prior_seg_m[name])
                if any(value == SOURCE_UNAVAILABLE for value in inputs):
                    mix[name] = SOURCE_UNAVAILABLE
                    within[name] = SOURCE_UNAVAILABLE
                elif any(value == UNDEFINED_RATIO for value in inputs):
                    mix[name] = UNDEFINED_RATIO
                    within[name] = UNDEFINED_RATIO
                else:
                    mix[name] = (
                        100.0
                        * (float(share[name]) - float(prior_share[name]))
                        * (float(seg_m[name]) + float(prior_seg_m[name]))
                        / 2.0
                    )
                    within[name] = (
                        100.0
                        * (float(seg_m[name]) - float(prior_seg_m[name]))
                        * (float(share[name]) + float(prior_share[name]))
                        / 2.0
                    )
            mix_inputs = (dm, db, *mix.values(), *within.values())
            if any(
                value is None or value == SOURCE_UNAVAILABLE for value in mix_inputs
            ):
                mix_res = SOURCE_UNAVAILABLE
            elif any(value == UNDEFINED_RATIO for value in mix_inputs):
                mix_res = UNDEFINED_RATIO
            else:
                mix_res = (
                    float(dm)
                    - sum(float(mix[name]) for name in SEGMENTS)
                    - sum(float(within[name]) for name in SEGMENTS)
                    - float(db)
                )
        recon_sum = sum(amount for _, amount in signed)
        if opening:
            dp = {name: None for name in SEGMENTS}
            dbr = None
            dpc = None
            dpr = None
        elif prior_ifop is None or prior_cons_ifop is None or prior_recon_sum is None:
            dp = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}
            dbr = SOURCE_UNAVAILABLE
            dpc = SOURCE_UNAVAILABLE
            dpr = SOURCE_UNAVAILABLE
        else:
            dp = {
                name: _delta(ifop[name], prior_ifop[name], opening=False)
                for name in SEGMENTS
            }
            dbr = _delta(recon_sum, prior_recon_sum, opening=False)
            dpc = _delta(cons_ifop, prior_cons_ifop, opening=False)
            if (
                dpc == SOURCE_UNAVAILABLE
                or dbr == SOURCE_UNAVAILABLE
                or any(value == SOURCE_UNAVAILABLE for value in dp.values())
            ):
                dpr = SOURCE_UNAVAILABLE
            elif (
                dpc == UNDEFINED_RATIO
                or dbr == UNDEFINED_RATIO
                or any(value == UNDEFINED_RATIO for value in dp.values())
            ):
                dpr = UNDEFINED_RATIO
            else:
                dpr = float(dpc) - sum(float(dp[name]) for name in SEGMENTS) - float(dbr)
        expected[period] = {
            "family": snapshot.presentation_family,
            "revenue": revenue,
            "ifop": ifop,
            "share": {name: ratio_or_na(revenue[name], cons_rev) for name in SEGMENTS},
            "growth": growth,
            "contrib": contrib,
            "cons_growth": cons_growth,
            "residual": residual,
            "margin": {name: ratio_or_na(ifop[name], revenue[name]) for name in SEGMENTS},
            "cs": cs,
            "b": b,
            "m": m,
            "e": e,
            "dcs": dcs,
            "db": db,
            "dm": dm,
            "de": de,
            "mix": mix,
            "within": within,
            "mix_res": mix_res,
            "dp": dp,
            "dbr": dbr,
            "dpc": dpc,
            "dpr": dpr,
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
        prior_cons = cons_rev
        prior_ifop = ifop
        prior_cons_ifop = cons_ifop
        prior_recon_sum = recon_sum
        prior_cs = cs
        prior_b = b
        prior_m = m
        prior_share = share
        prior_seg_m = seg_m
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
        assert series.revenue_growth_contribution[period] == row["contrib"]
        assert series.consolidated_revenue_growth[period] == row["cons_growth"]
        assert series.revenue_growth_contribution_residual[period] == row["residual"]
        assert series.reported_operating_margin[period] == row["margin"]
        assert series.operating_margin_contribution[period] == row["cs"]
        assert series.reconciling_operating_margin_contribution[period] == row["b"]
        assert series.consolidated_operating_margin[period] == row["m"]
        assert series.operating_margin_contribution_residual[period] == row["e"]
        assert series.operating_margin_contribution_change[period] == row["dcs"]
        assert series.reconciling_operating_margin_contribution_change[period] == row["db"]
        assert series.consolidated_operating_margin_change[period] == row["dm"]
        assert series.operating_margin_contribution_change_residual[period] == row["de"]
        assert series.operating_margin_mix_effect[period] == row["mix"]
        assert series.operating_margin_within_segment_effect[period] == row["within"]
        assert series.operating_margin_mix_within_residual[period] == row["mix_res"]
        assert series.operating_profit_amount_change[period] == row["dp"]
        assert series.reconciling_operating_profit_amount_change[period] == row["dbr"]
        assert series.consolidated_operating_profit_amount_change[period] == row["dpc"]
        assert series.operating_profit_amount_change_residual[period] == row["dpr"]
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
        contrib = row["contrib"]
        cons_growth = row["cons_growth"]
        residual = row["residual"]
        if (
            isinstance(cons_growth, float)
            and all(isinstance(value, float) for value in contrib.values())
            and isinstance(residual, float)
        ):
            reconstructed = 100.0 * cons_growth - sum(contrib.values())
            assert abs(reconstructed - residual) <= GEOGRAPHIC_RATIO_TOLERANCE
        cs = row["cs"]
        b = row["b"]
        m = row["m"]
        e = row["e"]
        if (
            isinstance(m, float)
            and isinstance(b, float)
            and isinstance(e, float)
            and all(isinstance(value, float) for value in cs.values())
        ):
            reconstructed_e = m - sum(cs.values()) - b
            assert abs(reconstructed_e - e) <= GEOGRAPHIC_RATIO_TOLERANCE
        dcs = row["dcs"]
        db = row["db"]
        dm = row["dm"]
        de = row["de"]
        if (
            isinstance(dm, float)
            and isinstance(db, float)
            and isinstance(de, float)
            and all(isinstance(value, float) for value in dcs.values())
        ):
            reconstructed_de = dm - sum(dcs.values()) - db
            assert abs(reconstructed_de - de) <= GEOGRAPHIC_RATIO_TOLERANCE
        mix = row["mix"]
        within = row["within"]
        mix_res = row["mix_res"]
        if (
            isinstance(dm, float)
            and isinstance(db, float)
            and isinstance(mix_res, float)
            and all(isinstance(value, float) for value in mix.values())
            and all(isinstance(value, float) for value in within.values())
        ):
            reconstructed_mix_res = (
                dm - sum(mix.values()) - sum(within.values()) - db
            )
            assert abs(reconstructed_mix_res - mix_res) <= GEOGRAPHIC_RATIO_TOLERANCE
            assert abs(mix_res - de) <= GEOGRAPHIC_RATIO_TOLERANCE
            for name in SEGMENTS:
                if isinstance(dcs[name], float):
                    assert abs(
                        float(mix[name]) + float(within[name]) - float(dcs[name])
                    ) <= GEOGRAPHIC_RATIO_TOLERANCE
        dp = row["dp"]
        dbr = row["dbr"]
        dpc = row["dpc"]
        dpr = row["dpr"]
        if (
            isinstance(dpc, float)
            and isinstance(dbr, float)
            and isinstance(dpr, float)
            and all(isinstance(value, float) for value in dp.values())
        ):
            reconstructed_dpr = dpc - sum(dp.values()) - dbr
            assert abs(reconstructed_dpr - dpr) <= GEOGRAPHIC_RATIO_TOLERANCE


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
    assert series.revenue_growth_contribution[P1]["americas"] is None
    assert series.consolidated_revenue_growth[P1] is None
    assert series.revenue_growth_contribution_residual[P1] is None
    assert series.operating_margin_contribution[P1]["americas"] == pytest.approx(40.0)
    assert series.operating_margin_contribution[P1]["china_mainland"] == pytest.approx(20.0)
    assert series.operating_margin_contribution[P1]["rest_of_world"] == pytest.approx(10.0)
    assert series.reconciling_operating_margin_contribution[P1] == pytest.approx(-15.0)
    assert series.consolidated_operating_margin[P1] == pytest.approx(55.0)
    assert series.operating_margin_contribution_residual[P1] == pytest.approx(0.0)
    assert series.operating_margin_contribution_change[P1]["americas"] is None
    assert series.consolidated_operating_margin_change[P1] is None
    assert series.operating_margin_contribution_change_residual[P1] is None
    assert series.operating_margin_mix_effect[P1]["americas"] is None
    assert series.operating_margin_within_segment_effect[P1]["americas"] is None
    assert series.operating_margin_mix_within_residual[P1] is None
    assert series.operating_profit_amount_change[P1]["americas"] is None
    assert series.consolidated_operating_profit_amount_change[P1] is None
    assert series.operating_profit_amount_change_residual[P1] is None
    assert series.revenue_growth_contribution[P2]["americas"] == pytest.approx(30.0)
    assert series.revenue_growth_contribution[P2]["china_mainland"] == pytest.approx(-5.0)
    assert series.revenue_growth_contribution[P2]["rest_of_world"] == pytest.approx(-5.0)
    assert series.consolidated_revenue_growth[P2] == pytest.approx(0.2)
    assert series.revenue_growth_contribution_residual[P2] == pytest.approx(0.0)
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
    assert series.revenue_growth_contribution[P0]["americas"] is None
    assert series.consolidated_revenue_growth[P0] is None
    assert series.net_revenue[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_share[P1]["china_mainland"] == SOURCE_UNAVAILABLE
    assert series.reported_operating_margin[P1]["rest_of_world"] == SOURCE_UNAVAILABLE
    assert series.signed_reconciling_contributions[P1] == SOURCE_UNAVAILABLE
    assert series.revenue_growth[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_growth[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_growth_contribution[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_growth_contribution[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.consolidated_revenue_growth[P2] == SOURCE_UNAVAILABLE
    assert series.revenue_growth_contribution_residual[P2] == SOURCE_UNAVAILABLE
    assert series.operating_margin_contribution[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.reconciling_operating_margin_contribution[P1] == SOURCE_UNAVAILABLE
    assert series.consolidated_operating_margin[P1] == SOURCE_UNAVAILABLE
    assert series.operating_margin_contribution_change[P0]["americas"] is None
    assert series.operating_margin_contribution_change[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_margin_contribution_change[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_margin_contribution_change_residual[P2] == SOURCE_UNAVAILABLE
    assert series.operating_margin_mix_effect[P0]["americas"] is None
    assert series.operating_margin_mix_effect[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_margin_mix_effect[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_margin_within_segment_effect[P2]["china_mainland"] == SOURCE_UNAVAILABLE
    assert series.operating_margin_mix_within_residual[P2] == SOURCE_UNAVAILABLE
    assert series.operating_profit_amount_change[P0]["americas"] is None
    assert series.operating_profit_amount_change[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_profit_amount_change[P2]["americas"] == SOURCE_UNAVAILABLE
    assert series.operating_profit_amount_change_residual[P2] == SOURCE_UNAVAILABLE
    assert series.operating_margin_contribution[P2]["americas"] == pytest.approx(
        100.0 * 40.0 / 140.0
    )
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
    assert series.operating_margin_contribution[P1]["americas"] == pytest.approx(0.0)
    assert series.operating_margin_contribution[P2]["china_mainland"] == pytest.approx(
        100.0 * 8.0 / 60.0
    )
    assert series.operating_margin_contribution[P2]["americas"] == pytest.approx(
        100.0 * -2.0 / 60.0
    )
    assert series.operating_margin_mix_effect[P2]["americas"] == UNDEFINED_RATIO
    assert series.operating_margin_within_segment_effect[P2]["americas"] == UNDEFINED_RATIO
    assert series.operating_margin_mix_effect[P2]["rest_of_world"] == pytest.approx(
        100.0 * (50.0 / 60.0 - 0.5) * (0.0 + -0.1) / 2.0
    )
    assert series.operating_margin_within_segment_effect[P2]["rest_of_world"] == pytest.approx(
        100.0 * (0.0 - -0.1) * (50.0 / 60.0 + 0.5) / 2.0
    )
    assert series.operating_margin_mix_within_residual[P2] == UNDEFINED_RATIO
    assert series.operating_profit_amount_change[P2]["americas"] == pytest.approx(-2.0)
    assert series.operating_profit_amount_change[P2]["china_mainland"] == pytest.approx(-2.0)
    assert series.operating_profit_amount_change[P2]["rest_of_world"] == pytest.approx(5.0)
    assert series.reconciling_operating_profit_amount_change[P2] == pytest.approx(-1.0)
    assert series.consolidated_operating_profit_amount_change[P2] == pytest.approx(0.0)
    assert series.operating_profit_amount_change_residual[P2] == pytest.approx(0.0)
    assert series.revenue_growth[P2]["americas"] == UNDEFINED_RATIO
    assert series.revenue_growth[P2]["china_mainland"] == -1.0
    assert series.revenue_growth_contribution[P2]["americas"] == pytest.approx(10.0)
    assert series.revenue_growth_contribution[P2]["china_mainland"] == pytest.approx(-50.0)
    assert series.revenue_growth_contribution[P2]["rest_of_world"] == pytest.approx(0.0)
    assert series.consolidated_revenue_growth[P2] == pytest.approx(-0.4)
    assert series.revenue_growth_contribution_residual[P2] == pytest.approx(0.0)
    assert REPORTED_OPERATING_MARGIN_BASIS == "income_from_operations / net_revenue"
    assert "nopat" not in REPORTED_OPERATING_MARGIN_BASIS.lower()
    assert not hasattr(series, "nopat_margin")


def test_growth_contributions_zero_consolidated_offsetting_and_singleton():
    zero_cons = _snapshot(
        P0,
        values=_corp_values(rev=(0.0, 0.0, 0.0), ifop=(0.0, 0.0, 0.0), corporate=0.0),
    )
    later = _snapshot(
        P1,
        values=_corp_values(rev=(10.0, 20.0, 30.0), ifop=(4.0, 5.0, 6.0), corporate=-3.0),
    )
    zero_fin = _fin_with_segment(zero_cons, later, extra_periods=[P0, P1])
    zero_series = compute_geographic_segment_series(zero_fin)
    _assert_series_matches(
        zero_series,
        _independent_from_snapshots(
            [P0, P1],
            {snap.period: snap for snap in zero_fin.historical_segment.periods},
        ),
    )
    assert zero_series.consolidated_revenue_growth[P1] == UNDEFINED_RATIO
    assert zero_series.revenue_growth_contribution[P1]["americas"] == UNDEFINED_RATIO
    assert zero_series.revenue_growth_contribution_residual[P1] == UNDEFINED_RATIO
    assert zero_series.revenue_growth[P1]["americas"] == UNDEFINED_RATIO
    assert zero_series.operating_margin_contribution[P0]["americas"] == UNDEFINED_RATIO
    assert zero_series.reconciling_operating_margin_contribution[P0] == UNDEFINED_RATIO
    assert zero_series.consolidated_operating_margin[P0] == UNDEFINED_RATIO
    assert zero_series.operating_margin_contribution_residual[P0] == UNDEFINED_RATIO
    assert zero_series.operating_margin_contribution_change[P1]["americas"] == UNDEFINED_RATIO
    assert zero_series.operating_margin_contribution_change_residual[P1] == UNDEFINED_RATIO
    assert zero_series.operating_margin_mix_effect[P1]["americas"] == UNDEFINED_RATIO
    assert zero_series.operating_margin_within_segment_effect[P1]["china_mainland"] == UNDEFINED_RATIO
    assert zero_series.operating_margin_mix_within_residual[P1] == UNDEFINED_RATIO
    assert zero_series.operating_profit_amount_change[P1]["americas"] == pytest.approx(4.0)
    assert zero_series.operating_profit_amount_change[P1]["china_mainland"] == pytest.approx(5.0)
    assert zero_series.operating_profit_amount_change[P1]["rest_of_world"] == pytest.approx(6.0)
    assert zero_series.reconciling_operating_profit_amount_change[P1] == pytest.approx(-3.0)
    assert zero_series.consolidated_operating_profit_amount_change[P1] == pytest.approx(12.0)
    assert zero_series.operating_profit_amount_change_residual[P1] == pytest.approx(0.0)

    offsetting = _fin_with_segment(
        _snapshot(P1, values=_corp_values(rev=(50.0, 30.0, 20.0))),
        _snapshot(P2, values=_corp_values(rev=(60.0, 20.0, 20.0))),
    )
    offset_series = compute_geographic_segment_series(offsetting)
    _assert_series_matches(
        offset_series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in offsetting.historical_segment.periods},
        ),
    )
    assert offset_series.consolidated_revenue_growth[P2] == pytest.approx(0.0)
    assert offset_series.revenue_growth_contribution[P2]["americas"] == pytest.approx(10.0)
    assert offset_series.revenue_growth_contribution[P2]["china_mainland"] == pytest.approx(-10.0)
    assert offset_series.revenue_growth_contribution[P2]["rest_of_world"] == pytest.approx(0.0)
    assert offset_series.revenue_growth_contribution_residual[P2] == pytest.approx(0.0)

    singleton = _fin_with_segment(_snapshot(P2))
    single_series = compute_geographic_segment_series(singleton)
    assert single_series.revenue_growth_contribution[P2]["americas"] is None
    assert single_series.consolidated_revenue_growth[P2] is None
    assert single_series.revenue_growth_contribution_residual[P2] is None
    assert single_series.operating_margin_contribution_change[P2]["americas"] is None
    assert single_series.consolidated_operating_margin_change[P2] is None
    assert single_series.operating_margin_contribution_change_residual[P2] is None
    assert single_series.operating_margin_mix_effect[P2]["americas"] is None
    assert single_series.operating_margin_within_segment_effect[P2]["rest_of_world"] is None
    assert single_series.operating_margin_mix_within_residual[P2] is None
    assert single_series.operating_profit_amount_change[P2]["americas"] is None
    assert single_series.reconciling_operating_profit_amount_change[P2] is None
    assert single_series.consolidated_operating_profit_amount_change[P2] is None
    assert single_series.operating_profit_amount_change_residual[P2] is None
    assert single_series.operating_margin_contribution[P2]["americas"] == pytest.approx(
        100.0 * 50.0 / 120.0
    )


def test_operating_margin_bridge_offsetting_losses_and_family_transition():
    opening = _snapshot(
        P1,
        family=FAMILY_ITEMIZED,
        values=_itemized_values(),
    )
    later = _snapshot(
        P2,
        family=FAMILY_CORPORATE,
        values=_corp_values(ifop=(60.0, 10.0, -5.0), corporate=-15.0),
    )
    fin = _fin_with_segment(opening, later)
    series = compute_geographic_segment_series(fin)
    _assert_series_matches(
        series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in fin.historical_segment.periods},
        ),
    )
    assert series.operating_margin_contribution[P2]["rest_of_world"] == pytest.approx(
        100.0 * -5.0 / 120.0
    )
    assert series.reconciling_operating_margin_contribution[P2] == pytest.approx(
        100.0 * -15.0 / 120.0
    )
    assert series.operating_margin_contribution_residual[P1] == pytest.approx(0.0)
    assert series.operating_margin_contribution_residual[P2] == pytest.approx(0.0)
    assert series.operating_margin_contribution_change_residual[P2] == pytest.approx(0.0)
    assert series.operating_margin_mix_within_residual[P2] == pytest.approx(0.0)
    assert series.operating_profit_amount_change[P2]["americas"] == pytest.approx(20.0)
    assert series.operating_profit_amount_change[P2]["china_mainland"] == pytest.approx(-10.0)
    assert series.operating_profit_amount_change[P2]["rest_of_world"] == pytest.approx(-15.0)
    assert series.reconciling_operating_profit_amount_change[P2] == pytest.approx(0.0)
    assert series.consolidated_operating_profit_amount_change[P2] == pytest.approx(-5.0)
    assert series.operating_profit_amount_change_residual[P2] == pytest.approx(0.0)
    assert series.presentation_family[P1] == FAMILY_ITEMIZED
    assert series.presentation_family[P2] == FAMILY_CORPORATE


def test_mix_within_unchanged_shares_margins_offsetting_and_nonzero_residual():
    unchanged_margin = _fin_with_segment(
        _snapshot(
            P1,
            values=_corp_values(rev=(50.0, 30.0, 20.0), ifop=(10.0, 6.0, 4.0), corporate=-5.0),
        ),
        _snapshot(
            P2,
            values=_corp_values(rev=(60.0, 24.0, 16.0), ifop=(12.0, 4.8, 3.2), corporate=-5.0),
        ),
    )
    margin_series = compute_geographic_segment_series(unchanged_margin)
    _assert_series_matches(
        margin_series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in unchanged_margin.historical_segment.periods},
        ),
    )
    assert margin_series.operating_margin_within_segment_effect[P2]["americas"] == pytest.approx(0.0)
    assert margin_series.operating_margin_mix_effect[P2]["americas"] == pytest.approx(2.0)
    assert margin_series.operating_profit_amount_change[P2]["americas"] == pytest.approx(2.0)
    assert margin_series.operating_profit_amount_change[P2]["china_mainland"] == pytest.approx(-1.2)
    assert margin_series.operating_profit_amount_change[P2]["rest_of_world"] == pytest.approx(-0.8)
    assert margin_series.reconciling_operating_profit_amount_change[P2] == pytest.approx(0.0)
    assert margin_series.consolidated_operating_profit_amount_change[P2] == pytest.approx(0.0)
    assert margin_series.operating_profit_amount_change_residual[P2] == pytest.approx(0.0)
    assert margin_series.operating_margin_mix_effect[P2]["americas"] + (
        margin_series.operating_margin_within_segment_effect[P2]["americas"]
    ) == pytest.approx(margin_series.operating_margin_contribution_change[P2]["americas"])

    unchanged_share = _fin_with_segment(
        _snapshot(
            P1,
            values=_corp_values(rev=(50.0, 30.0, 20.0), ifop=(10.0, 6.0, 4.0), corporate=-5.0),
        ),
        _snapshot(
            P2,
            values=_corp_values(rev=(50.0, 30.0, 20.0), ifop=(15.0, 6.0, 4.0), corporate=-5.0),
        ),
    )
    share_series = compute_geographic_segment_series(unchanged_share)
    _assert_series_matches(
        share_series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in unchanged_share.historical_segment.periods},
        ),
    )
    assert share_series.operating_margin_mix_effect[P2]["americas"] == pytest.approx(0.0)
    assert share_series.operating_margin_within_segment_effect[P2]["americas"] == pytest.approx(5.0)

    offsetting = _fin_with_segment(
        _snapshot(
            P1,
            values=_corp_values(rev=(50.0, 30.0, 20.0), ifop=(20.0, 6.0, 4.0), corporate=-10.0),
        ),
        _snapshot(
            P2,
            values=_corp_values(rev=(60.0, 24.0, 16.0), ifop=(12.0, 9.6, 6.4), corporate=-10.0),
        ),
    )
    offset_series = compute_geographic_segment_series(offsetting)
    _assert_series_matches(
        offset_series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in offsetting.historical_segment.periods},
        ),
    )
    amer_mix = offset_series.operating_margin_mix_effect[P2]["americas"]
    amer_within = offset_series.operating_margin_within_segment_effect[P2]["americas"]
    assert amer_mix > 0
    assert amer_within < 0
    assert amer_mix + amer_within == pytest.approx(
        offset_series.operating_margin_contribution_change[P2]["americas"]
    )
    assert offset_series.operating_margin_mix_within_residual[P2] == pytest.approx(
        offset_series.operating_margin_contribution_change_residual[P2]
    )

    nonzero = _fin_with_segment(
        _snapshot(P1, family=FAMILY_ITEMIZED, values=_itemized_values()),
        _snapshot(
            P2,
            family=FAMILY_CORPORATE,
            values=_corp_values(ifop=(60.0, 10.0, -5.0), corporate=-15.0),
        ),
    )
    # Existing validation admits a signed reconstructed-vs-reported difference of 0
    # on these fixtures; a nonzero mix residual is admitted when ΔM/ΔB identity holds.
    nonzero_series = compute_geographic_segment_series(nonzero)
    _assert_series_matches(
        nonzero_series,
        _independent_from_snapshots(
            [P1, P2],
            {snap.period: snap for snap in nonzero.historical_segment.periods},
        ),
    )
    assert nonzero_series.operating_margin_contribution[P2]["rest_of_world"] == pytest.approx(
        100.0 * -5.0 / 120.0
    )
    assert nonzero_series.operating_margin_mix_within_residual[P2] == pytest.approx(
        nonzero_series.operating_margin_contribution_change_residual[P2]
    )


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
    assert series.operating_profit_amount_change[ADMIT_2022]["americas"] is None
    assert series.reconciling_operating_profit_amount_change[ADMIT_2022] is None
    assert series.consolidated_operating_profit_amount_change[ADMIT_2022] is None
    assert series.operating_profit_amount_change_residual[ADMIT_2022] is None
    fy2024 = date(2024, 1, 28)
    fy2025 = date(2025, 2, 2)
    for current, prior in ((fy2024, date(2023, 1, 29)), (FY2026, fy2025)):
        curr_snap = snapshots[current]
        prior_snap = snapshots[prior]
        independent = {
            name: (
                float(curr_snap.values[f"income_from_operations.{name}"])
                - float(prior_snap.values[f"income_from_operations.{name}"])
            )
            for name in SEGMENTS
        }
        curr_recon = sum(amount for _, amount in series.signed_reconciling_contributions[current])
        prior_recon = sum(amount for _, amount in series.signed_reconciling_contributions[prior])
        independent_recon = curr_recon - prior_recon
        independent_cons = (
            float(curr_snap.values["income_from_operations.consolidated"])
            - float(prior_snap.values["income_from_operations.consolidated"])
        )
        independent_residual = (
            independent_cons - sum(independent.values()) - independent_recon
        )
        for name in SEGMENTS:
            assert series.operating_profit_amount_change[current][name] == pytest.approx(
                independent[name]
            )
        assert series.reconciling_operating_profit_amount_change[current] == pytest.approx(
            independent_recon
        )
        assert series.consolidated_operating_profit_amount_change[current] == pytest.approx(
            independent_cons
        )
        assert series.operating_profit_amount_change_residual[current] == pytest.approx(
            independent_residual
        )
        delta_diff = (
            series.consolidated_operating_profit_difference[current]
            - series.consolidated_operating_profit_difference[prior]
        )
        assert series.operating_profit_amount_change_residual[current] == pytest.approx(
            -delta_diff
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
