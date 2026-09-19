"""Historical Revenue per Store calculations and production integration."""

from __future__ import annotations

from datetime import date

import pytest

from core.engine.component_catalog import (
    REVENUE_PER_STORE_AVERAGE_FAMILY_ID,
    REVENUE_PER_STORE_CHANGE_FAMILY_ID,
    REVENUE_PER_STORE_COMPONENT_CATALOG,
    REVENUE_PER_STORE_GROWTH_FAMILY_ID,
    REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
    REVENUE_PER_STORE_SHEET_NAME,
    SemanticCellRef,
    expand_revenue_per_store_specs,
    resolve_revenue_per_store_average_formula,
    resolve_revenue_per_store_change_formula,
    resolve_revenue_per_store_growth_formula,
    resolve_revenue_per_store_period_end_formula,
    revenue_per_store_adjacent_ratio_ids,
    revenue_per_store_average_dependency_ids,
    revenue_per_store_component_id,
    revenue_per_store_period_end_dependency_ids,
)
from core.engine.reference_model import ReferenceModelBuilder
from core.model.historical_expected import operating_kpi_expected_value_for_component
from core.model.line_resolver import MissingLineError
from core.model.operating_kpi_relationships import (
    CALCULATION_KIND,
    REASON_MISSING_PRIOR_STORE_COUNT,
    REASON_MISSING_REVENUE,
    REASON_MISSING_STORE_COUNT,
    REVENUE_INPUT_LABEL,
    STORE_COUNT_INPUT_LABEL,
)
from core.model.period_axis import PeriodAxisError
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO
from core.model.revenue_per_store import (
    AVERAGE_STORE_DENOMINATOR_LABEL,
    PERIOD_END_DENOMINATOR_LABEL,
    REVENUE_PER_STORE_RATIO_TOLERANCE,
    SCOPE_NOTE,
    compute_revenue_per_store_series,
    revenue_per_store_applicable,
)
from core.tests.test_lululemon_benchmark import REVENUE_ANCHORS
from core.tests.test_operating_kpi_analysis import _reload_admitted_store_histories
from core.tests.test_operating_kpi_facts import (
    INDEPENDENT_STORE_TOTALS,
    P2022,
    P2023,
    P2024,
    P2025,
    P2026,
    _fin_with_operating_kpis,
    _kpi_model_observation,
    _validated_augmented,
)
from core.tests.test_operating_kpi_relationships import _fin_with_relationship
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.model.period_axis import canonical_fiscal_periods

P0 = date(2023, 12, 31)
P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)
AXIS = (P2022, P2023, P2024, P2025, P2026)


def _assert_close(left, right) -> None:
    if isinstance(left, float) and isinstance(right, float):
        assert abs(left - right) <= REVENUE_PER_STORE_RATIO_TOLERANCE
    else:
        assert left == right


def _independent_rps(axis, revenues, counts):
    expected = {}
    numeric = {}
    for index, period in enumerate(axis):
        opening = index == 0
        current_rev = revenues.get(period)
        current_count = counts.get(period)
        prior = None if opening else axis[index - 1]
        prior_count = None if prior is None else counts.get(prior)
        prior_rev = None if prior is None else revenues.get(prior)
        if current_rev is None or current_count is None:
            period_end = SOURCE_UNAVAILABLE
        elif current_count == 0:
            period_end = UNDEFINED_RATIO
        else:
            period_end = current_rev / current_count
            numeric[period] = period_end
        if opening:
            average = None
            change = None
            growth = None
        else:
            if current_count is None or prior_count is None:
                average = SOURCE_UNAVAILABLE
            elif current_rev is None:
                average = SOURCE_UNAVAILABLE
            else:
                denom = (current_count + prior_count) / 2.0
                average = UNDEFINED_RATIO if denom == 0 else current_rev / denom
            current_rps = numeric.get(period)
            prior_rps = numeric.get(prior)
            if current_rps is None or prior_rps is None:
                change = SOURCE_UNAVAILABLE
                growth = SOURCE_UNAVAILABLE
            else:
                change = current_rps - prior_rps
                growth = (
                    UNDEFINED_RATIO if prior_rps == 0 else (current_rps - prior_rps) / prior_rps
                )
        expected[period] = {
            "revenue": SOURCE_UNAVAILABLE if current_rev is None else current_rev,
            "count": SOURCE_UNAVAILABLE if current_count is None else current_count,
            "period_end": period_end,
            "average": average,
            "change": change,
            "growth": growth,
        }
        _ = prior_rev
    return expected


def test_catalog_orders_formulas_and_identities():
    assert REVENUE_PER_STORE_SHEET_NAME == "Revenue per Store Analysis"
    assert [family.order for family in REVENUE_PER_STORE_COMPONENT_CATALOG] == [
        173,
        174,
        175,
        176,
    ]
    assert [family.id for family in REVENUE_PER_STORE_COMPONENT_CATALOG] == [
        REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
        REVENUE_PER_STORE_AVERAGE_FAMILY_ID,
        REVENUE_PER_STORE_CHANGE_FAMILY_ID,
        REVENUE_PER_STORE_GROWTH_FAMILY_ID,
    ]
    revenue = SemanticCellRef(
        id="rev",
        semantic_key="operating_kpi.revenue_store.source",
        period_end=P2.isoformat(),
        cell="C20",
        tab="Store Count Analysis",
    )
    current = SemanticCellRef(
        id="cur",
        semantic_key="operating_kpi.store_count.source",
        period_end=P2.isoformat(),
        cell="C10",
        tab="Store Count Analysis",
    )
    prior = SemanticCellRef(
        id="pri",
        semantic_key="operating_kpi.store_count.source",
        period_end=P1.isoformat(),
        cell="B10",
        tab="Store Count Analysis",
    )
    assert resolve_revenue_per_store_period_end_formula(
        revenue, current, from_tab=REVENUE_PER_STORE_SHEET_NAME
    ) == "=IF('Store Count Analysis'!C10=0,NA(),'Store Count Analysis'!C20/'Store Count Analysis'!C10)"
    assert resolve_revenue_per_store_average_formula(
        revenue, current, prior, from_tab=REVENUE_PER_STORE_SHEET_NAME
    ) == (
        "=IF((('Store Count Analysis'!C10+'Store Count Analysis'!B10)/2)=0,NA(),"
        "'Store Count Analysis'!C20/(('Store Count Analysis'!C10+'Store Count Analysis'!B10)/2))"
    )
    local = SemanticCellRef(
        id="rps",
        semantic_key="operating_kpi.revenue_per_store.period_end",
        period_end=P2.isoformat(),
        cell="C9",
        tab=REVENUE_PER_STORE_SHEET_NAME,
    )
    prior_rps = SemanticCellRef(
        id="rps_p",
        semantic_key="operating_kpi.revenue_per_store.period_end",
        period_end=P1.isoformat(),
        cell="B9",
        tab=REVENUE_PER_STORE_SHEET_NAME,
    )
    assert resolve_revenue_per_store_change_formula(
        local, prior_rps, from_tab=REVENUE_PER_STORE_SHEET_NAME
    ) == "=C9-B9"
    assert resolve_revenue_per_store_growth_formula(
        local, prior_rps, from_tab=REVENUE_PER_STORE_SHEET_NAME
    ) == "=IF(B9=0,NA(),(C9-B9)/B9)"
    assert revenue_per_store_period_end_dependency_ids(P2) == (
        "operating_kpi_revenue_source__20251231",
        "store_count_source__20251231",
    )
    assert revenue_per_store_average_dependency_ids([P1, P2], P2) == (
        "operating_kpi_revenue_source__20251231",
        "store_count_source__20251231",
        "store_count_source__20241231",
    )
    with pytest.raises(ValueError, match="opening revenue-per-store"):
        revenue_per_store_average_dependency_ids([P1, P2], P1)
    with pytest.raises(ValueError, match="opening revenue-per-store"):
        revenue_per_store_adjacent_ratio_ids([P1, P2], P1)
    specs = expand_revenue_per_store_specs(
        [P1, P2],
        start_order=1,
        period_end_periods=(P1, P2),
        average_periods=(P2,),
        change_periods=(P2,),
        growth_periods=(P2,),
    )
    assert [s.family_id for s in specs] == [
        REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
        REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
        REVENUE_PER_STORE_AVERAGE_FAMILY_ID,
        REVENUE_PER_STORE_CHANGE_FAMILY_ID,
        REVENUE_PER_STORE_GROWTH_FAMILY_ID,
    ]
    assert specs[0].id == revenue_per_store_component_id(
        REVENUE_PER_STORE_PERIOD_END_FAMILY_ID, P1
    )


def test_absent_null_and_storeless_payloads_are_inapplicable():
    from core.tests.test_historical_segment import _base_payload

    payload = _base_payload()
    absent = standardized_from_payload(payload)
    assert revenue_per_store_applicable(absent) is False
    with pytest.raises(MissingLineError, match="revenue per store sources not available"):
        compute_revenue_per_store_series(absent)

    payload["historical_operating_kpis"] = None
    null = standardized_from_payload(payload)
    assert revenue_per_store_applicable(null) is False
    with pytest.raises(MissingLineError, match="revenue per store sources not available"):
        compute_revenue_per_store_series(null)

    management_only = _fin_with_operating_kpis(management=[])
    management_only.historical_operating_kpis.observations = []
    assert revenue_per_store_applicable(management_only) is False


def test_supported_periods_and_missing_incompatible_inputs():
    fin = _fin_with_relationship(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 12),
        revenue={P1: 1000.0, P2: 1500.0},
    )
    assert revenue_per_store_applicable(fin) is True
    result = compute_revenue_per_store_series(fin)
    assert result.scope_note == SCOPE_NOTE
    assert "includes revenue outside those stores" in result.scope_note
    assert "sales per square foot" in result.scope_note
    assert "comparable sales" in result.scope_note
    assert result.period_end_denominator_label == PERIOD_END_DENOMINATOR_LABEL
    assert result.average_store_denominator_label == AVERAGE_STORE_DENOMINATOR_LABEL
    assert result.calculation_kind == CALCULATION_KIND
    assert result.revenue_input_label == REVENUE_INPUT_LABEL
    assert result.store_count_input_label == STORE_COUNT_INPUT_LABEL
    assert result.monetary_scale == "USD in Thousands"
    _assert_close(result.period_end_revenue_per_store[P1], 100.0)
    _assert_close(result.period_end_revenue_per_store[P2], 125.0)
    assert result.average_store_revenue_per_store[P1] is None
    _assert_close(result.average_store_revenue_per_store[P2], 1500.0 / 11.0)
    assert result.period_end_change[P1] is None
    _assert_close(result.period_end_change[P2], 25.0)
    _assert_close(result.period_end_growth[P2], 0.25)

    missing_rev = _fin_with_relationship(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 12),
        revenue={P1: 1000.0},
    )
    gap = compute_revenue_per_store_series(missing_rev)
    assert gap.period_end_revenue_per_store[P2] == SOURCE_UNAVAILABLE
    assert gap.average_store_revenue_per_store[P2] == SOURCE_UNAVAILABLE
    assert REASON_MISSING_REVENUE in (gap.unavailable_reasons[P2] or ())

    missing_prior = _fin_with_relationship(
        _kpi_model_observation(P2, 12),
        extra_periods=[P1, P2],
        revenue={P1: 1000.0, P2: 1500.0},
    )
    prior_gap = compute_revenue_per_store_series(missing_prior)
    assert prior_gap.period_end_revenue_per_store[P1] == SOURCE_UNAVAILABLE
    assert prior_gap.average_store_revenue_per_store[P2] == SOURCE_UNAVAILABLE
    assert prior_gap.period_end_change[P2] == SOURCE_UNAVAILABLE
    assert REASON_MISSING_PRIOR_STORE_COUNT in (prior_gap.unavailable_reasons[P2] or ())
    assert REASON_MISSING_STORE_COUNT in (prior_gap.unavailable_reasons[P1] or ())

    zero = _fin_with_relationship(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 0),
        revenue={P1: 1000.0, P2: 1500.0},
    )
    undefined = compute_revenue_per_store_series(zero)
    assert undefined.period_end_revenue_per_store[P1] == UNDEFINED_RATIO
    assert undefined.average_store_revenue_per_store[P2] == UNDEFINED_RATIO
    assert undefined.period_end_growth[P2] == SOURCE_UNAVAILABLE

    interim = _fin_with_relationship(
        _kpi_model_observation(P2, 12),
        revenue={P2: 1500.0},
        interim=True,
    )
    with pytest.raises(PeriodAxisError, match="annual fiscal periods"):
        compute_revenue_per_store_series(interim)


def test_period_end_and_average_are_never_substituted():
    fin = _fin_with_relationship(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 20),
        revenue={P1: 1000.0, P2: 1500.0},
    )
    result = compute_revenue_per_store_series(fin)
    assert result.period_end_revenue_per_store[P2] != result.average_store_revenue_per_store[P2]
    _assert_close(result.period_end_revenue_per_store[P2], 75.0)
    _assert_close(result.average_store_revenue_per_store[P2], 100.0)
    assert result.average_store_count[P2] == 15.0
    assert result.period_end_store_count[P2] == 20.0


def test_lululemon_supported_periods_match_independent_anchors(tmp_path):
    _dest, validated = _validated_augmented(tmp_path)
    _reconciled, _fin, restored = _reload_admitted_store_histories(validated)[0]
    axis = canonical_fiscal_periods(restored)
    assert tuple(axis) == AXIS
    result = compute_revenue_per_store_series(restored)
    expected = _independent_rps(axis, REVENUE_ANCHORS, INDEPENDENT_STORE_TOTALS)
    assert result.scope_note == SCOPE_NOTE
    assert result.monetary_scale == restored.units
    for period in axis:
        row = expected[period]
        _assert_close(result.revenue[period], row["revenue"])
        _assert_close(result.period_end_store_count[period], row["count"])
        _assert_close(result.period_end_revenue_per_store[period], row["period_end"])
        _assert_close(result.average_store_revenue_per_store[period], row["average"])
        _assert_close(result.period_end_change[period], row["change"])
        _assert_close(result.period_end_growth[period], row["growth"])
    payload = standardized_to_payload(restored)
    again = standardized_from_payload(payload)
    reloaded = compute_revenue_per_store_series(again)
    for period in axis:
        _assert_close(
            reloaded.period_end_revenue_per_store[period],
            result.period_end_revenue_per_store[period],
        )
        _assert_close(
            reloaded.average_store_revenue_per_store[period],
            result.average_store_revenue_per_store[period],
        )

    builder = ReferenceModelBuilder(restored)
    assert builder.revenue_per_store_schedule is True
    rps_specs = [
        spec
        for spec in builder.operating_kpi_specs
        if spec.family_id
        in {
            REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
            REVENUE_PER_STORE_AVERAGE_FAMILY_ID,
            REVENUE_PER_STORE_CHANGE_FAMILY_ID,
            REVENUE_PER_STORE_GROWTH_FAMILY_ID,
        }
    ]
    assert len(rps_specs) == 17
    assert {spec.tab_template for spec in rps_specs} == {REVENUE_PER_STORE_SHEET_NAME}
    looked = operating_kpi_expected_value_for_component(
        builder.operating_kpi_series,
        type(
            "C",
            (),
            {
                "family_id": REVENUE_PER_STORE_PERIOD_END_FAMILY_ID,
                "period_end": P2026.isoformat(),
                "id": "x",
            },
        )(),
        revenue_per_store=result,
    )
    _assert_close(looked, result.period_end_revenue_per_store[P2026])


def test_build_status_lists_revenue_per_store_once_from_emitted_families():
    from types import SimpleNamespace

    from core.build_status import ACTIVE, UNAVAILABLE, status_rows

    class Map:
        def all_ordered(self):
            families = (
                (REVENUE_PER_STORE_PERIOD_END_FAMILY_ID, 5),
                (REVENUE_PER_STORE_AVERAGE_FAMILY_ID, 4),
                (REVENUE_PER_STORE_CHANGE_FAMILY_ID, 4),
                (REVENUE_PER_STORE_GROWTH_FAMILY_ID, 4),
            )
            return [
                SimpleNamespace(
                    family_id=family_id,
                    tab=REVENUE_PER_STORE_SHEET_NAME,
                )
                for family_id, count in families
                for _ in range(count)
            ]

    rows = status_rows(Map())
    rps = [row for row in rows if row["family"] == REVENUE_PER_STORE_SHEET_NAME]
    assert len(rps) == 1
    assert rps[0]["group"] == "Operating KPIs"
    assert rps[0]["status"] == ACTIVE
    assert rps[0]["cells"] == 17
    by_family = {row["family"]: row for row in rows}
    assert by_family["Comparable Sales Analysis"]["status"] == UNAVAILABLE
    assert by_family["Sales per Square Foot Analysis"]["status"] == UNAVAILABLE
