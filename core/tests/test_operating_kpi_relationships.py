"""Consolidated revenue versus company-operated store-count growth relationship."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.interface import FinancialPeriod, LineItem
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.management_kpi import management_admission_payload
from core.model.line_resolver import AmbiguousLineError, MissingLineError
from core.model.management_kpi import compute_management_kpi_series, management_kpi_applicable
from core.model.operating_kpi import (
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.operating_kpi_relationships import (
    CALCULATION_KIND,
    DIFFERENCE_UNIT,
    OPERATING_KPI_RELATIONSHIP_TOLERANCE,
    REASON_MISSING_PRIOR_REVENUE,
    REASON_MISSING_PRIOR_STORE_COUNT,
    REASON_MISSING_REVENUE,
    REASON_MISSING_STORE_COUNT,
    REVENUE_INPUT_LABEL,
    SCOPE_NOTE,
    STORE_COUNT_INPUT_LABEL,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_store_relationship_applicable,
)
from core.model.period_axis import PeriodAxisError, canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, ratio_or_na
from core.tests.test_historical_segment import _base_payload
from core.tests.test_lululemon_benchmark import REVENUE_ANCHORS
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    _bytes_by_name,
    _canonicalize,
    _copy_json,
    _statement_provenance,
)
from core.tests.test_management_kpi_history import _reconcile
from core.tests.test_operating_kpi_analysis import _assert_series_matches, _independent_from_counts
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2022,
    P2023,
    P2024,
    P2025,
    P2026,
    _fin_with_operating_kpis,
    _kpi_model_observation,
    _prepare_augmented,
    _validated_augmented,
)
from core.tests.test_operating_kpi_management_history import _compsales, _spsf

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
P0 = date(2023, 12, 31)
P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _revenue_line(
    values: dict[date, float | None],
    *,
    label: str = "Revenue",
    concept: str = "revenue",
) -> LineItem:
    return LineItem(label=label, concept=concept, values=dict(values))


def _fin_with_relationship(
    *observations,
    revenue: dict[date, float | None] | None = None,
    extra_periods: list[date] | None = None,
    units: str = "USD in Thousands",
    currency: str = "USD",
    management=None,
    income_statement: list[LineItem] | None = None,
    interim: bool = False,
):
    fin = _fin_with_operating_kpis(
        *observations,
        extra_periods=extra_periods,
        units=units,
        management=management,
    )
    fin.currency = currency
    if income_statement is not None:
        fin.income_statement = list(income_statement)
    elif revenue is not None:
        fin.income_statement = [_revenue_line(revenue)]
    if interim:
        fin.periods = [
            FinancialPeriod(end_date=period.end_date, label=period.label, is_interim=True)
            for period in fin.periods
        ]
    return fin


def _independent_relationship(
    axis: list[date],
    revenues: dict[date, float],
    counts: dict[date, float],
) -> dict[date, dict[str, float | str | None | tuple[str, ...] | None]]:
    expected: dict[date, dict[str, float | str | None | tuple[str, ...] | None]] = {}
    for index, period in enumerate(axis):
        opening = index == 0
        current_rev = revenues.get(period)
        current_count = counts.get(period)
        prior_period = None if opening else axis[index - 1]
        prior_rev = None if prior_period is None else revenues.get(prior_period)
        prior_count = None if prior_period is None else counts.get(prior_period)
        if opening:
            rev_growth: float | str | None = None
            store_growth: float | str | None = None
            difference: float | str | None = None
            reasons: tuple[str, ...] | None = None
        else:
            rev_reasons: list[str] = []
            store_reasons: list[str] = []
            if current_rev is None:
                rev_reasons.append(REASON_MISSING_REVENUE)
            if prior_rev is None:
                rev_reasons.append(REASON_MISSING_PRIOR_REVENUE)
            if current_count is None:
                store_reasons.append(REASON_MISSING_STORE_COUNT)
            if prior_count is None:
                store_reasons.append(REASON_MISSING_PRIOR_STORE_COUNT)
            if rev_reasons:
                rev_growth = SOURCE_UNAVAILABLE
            else:
                assert current_rev is not None and prior_rev is not None
                rev_growth = ratio_or_na(current_rev - prior_rev, prior_rev)
            if store_reasons:
                store_growth = SOURCE_UNAVAILABLE
            else:
                assert current_count is not None and prior_count is not None
                store_growth = ratio_or_na(current_count - prior_count, prior_count)
            if rev_growth == SOURCE_UNAVAILABLE or store_growth == SOURCE_UNAVAILABLE:
                difference = SOURCE_UNAVAILABLE
                reasons = tuple(rev_reasons + store_reasons)
            elif rev_growth == UNDEFINED_RATIO or store_growth == UNDEFINED_RATIO:
                difference = UNDEFINED_RATIO
                reasons = None
            else:
                assert isinstance(rev_growth, float) and isinstance(store_growth, float)
                difference = 100.0 * (rev_growth - store_growth)
                reasons = None
        expected[period] = {
            "revenue": SOURCE_UNAVAILABLE if current_rev is None else float(current_rev),
            "count": SOURCE_UNAVAILABLE if current_count is None else float(current_count),
            "revenue_growth": rev_growth,
            "store_growth": store_growth,
            "difference": difference,
            "reasons": reasons,
        }
    return expected


def _assert_close(left, right) -> None:
    if isinstance(left, float) and isinstance(right, float):
        assert abs(left - right) <= OPERATING_KPI_RELATIONSHIP_TOLERANCE
    else:
        assert left == right


def _assert_relationship_matches(result, expected) -> None:
    assert result.periods == tuple(expected)
    assert result.revenue_input_label == REVENUE_INPUT_LABEL
    assert result.store_count_input_label == STORE_COUNT_INPUT_LABEL
    assert result.calculation_kind == CALCULATION_KIND
    assert result.difference_unit == DIFFERENCE_UNIT
    assert result.scope_note == SCOPE_NOTE
    assert "revenue attribution" in result.scope_note
    assert "same-store sales" in result.scope_note
    assert "store productivity" in result.scope_note
    assert "organic growth" in result.scope_note
    assert "causal evidence" in result.scope_note
    assert not hasattr(result, "revenue_per_store")
    for period, row in expected.items():
        _assert_close(result.revenue[period], row["revenue"])
        _assert_close(result.store_count[period], row["count"])
        _assert_close(result.revenue_growth[period], row["revenue_growth"])
        _assert_close(result.store_count_growth[period], row["store_growth"])
        _assert_close(result.growth_difference_pp[period], row["difference"])
        assert result.unavailable_reasons[period] == row["reasons"]


def test_absent_null_and_management_only_have_no_relationship_module():
    payload = _base_payload()
    absent = standardized_from_payload(payload)
    assert operating_kpi_revenue_store_relationship_applicable(absent) is False
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(absent)

    payload["historical_operating_kpis"] = None
    null = standardized_from_payload(payload)
    assert operating_kpi_revenue_store_relationship_applicable(null) is False
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(null)

    management_only = _fin_with_relationship(
        management=[
            _compsales(period=P2, value=2.0),
            _spsf(period=P2, value=1426),
        ],
        revenue={P1: 100.0, P2: 110.0},
        extra_periods=[P1, P2],
    )
    assert operating_kpi_applicable(management_only) is False
    assert management_kpi_applicable(management_only) is True
    assert operating_kpi_revenue_store_relationship_applicable(management_only) is False
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(management_only)


def test_legacy_fast_retailing_payload_omits_relationship_module():
    payload = json.loads(FR_JSON.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    assert fin.historical_operating_kpis is None
    assert operating_kpi_revenue_store_relationship_applicable(fin) is False
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(fin)


def test_positive_negative_and_zero_growth():
    growing = _fin_with_relationship(
        _kpi_model_observation(P1, 100),
        _kpi_model_observation(P2, 110),
        revenue={P1: 200.0, P2: 260.0},
    )
    declining = _fin_with_relationship(
        _kpi_model_observation(P1, 200),
        _kpi_model_observation(P2, 160),
        revenue={P1: 500.0, P2: 400.0},
    )
    flat = _fin_with_relationship(
        _kpi_model_observation(P1, 80),
        _kpi_model_observation(P2, 80),
        revenue={P1: 90.0, P2: 90.0},
    )
    grow = compute_operating_kpi_revenue_store_relationship(growing)
    decline = compute_operating_kpi_revenue_store_relationship(declining)
    zero = compute_operating_kpi_revenue_store_relationship(flat)
    _assert_relationship_matches(
        grow, _independent_relationship([P1, P2], {P1: 200.0, P2: 260.0}, {P1: 100, P2: 110})
    )
    _assert_relationship_matches(
        decline,
        _independent_relationship([P1, P2], {P1: 500.0, P2: 400.0}, {P1: 200, P2: 160}),
    )
    _assert_relationship_matches(
        zero, _independent_relationship([P1, P2], {P1: 90.0, P2: 90.0}, {P1: 80, P2: 80})
    )
    assert grow.revenue_growth[P1] is None
    assert grow.store_count_growth[P1] is None
    assert grow.growth_difference_pp[P1] is None
    assert grow.revenue_growth[P2] == pytest.approx(0.3)
    assert grow.store_count_growth[P2] == pytest.approx(0.1)
    assert grow.growth_difference_pp[P2] == pytest.approx(20.0)
    assert decline.growth_difference_pp[P2] == pytest.approx(
        100.0 * ((400.0 - 500.0) / 500.0 - (160 - 200) / 200)
    )
    assert zero.revenue_growth[P2] == 0.0
    assert zero.store_count_growth[P2] == 0.0
    assert zero.growth_difference_pp[P2] == 0.0


def test_differing_monetary_scales_and_count_units():
    thousands = _fin_with_relationship(
        _kpi_model_observation(P1, 711, unit="stores"),
        _kpi_model_observation(P2, 767, unit="stores"),
        revenue={P1: 100.0, P2: 110.0},
        units="USD in Thousands",
        currency="USD",
    )
    millions = _fin_with_relationship(
        _kpi_model_observation(P1, 711, unit="ones"),
        _kpi_model_observation(P2, 767, unit="ones"),
        revenue={P1: 100.0, P2: 110.0},
        units="USD in Millions",
        currency="HKD",
    )
    left = compute_operating_kpi_revenue_store_relationship(thousands)
    right = compute_operating_kpi_revenue_store_relationship(millions)
    assert left.revenue_growth[P2] == right.revenue_growth[P2]
    assert left.store_count_growth[P2] == right.store_count_growth[P2]
    assert left.growth_difference_pp[P2] == right.growth_difference_pp[P2]
    assert left.currency == "USD"
    assert right.currency == "HKD"
    assert left.monetary_scale == "USD in Thousands"
    assert right.monetary_scale == "USD in Millions"
    assert left.store_count_unit[P1] == "stores"
    assert right.store_count_unit[P1] == "ones"
    store_only = compute_operating_kpi_series(thousands)
    assert left.store_count_growth == store_only.growth
    assert left.store_count == store_only.period_end_count


def test_singleton_and_sparse_histories():
    single = _fin_with_relationship(
        _kpi_model_observation(P2, 811),
        revenue={P2: 111.0},
    )
    sparse = _fin_with_relationship(
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P2, 767),
        revenue={P0: 80.0, P2: 120.0},
        extra_periods=[P0, P1, P2],
    )
    single_result = compute_operating_kpi_revenue_store_relationship(single)
    sparse_result = compute_operating_kpi_revenue_store_relationship(sparse)
    _assert_relationship_matches(
        single_result, _independent_relationship([P2], {P2: 111.0}, {P2: 811})
    )
    _assert_relationship_matches(
        sparse_result,
        _independent_relationship([P0, P1, P2], {P0: 80.0, P2: 120.0}, {P0: 655, P2: 767}),
    )
    assert single_result.growth_difference_pp[P2] is None
    assert sparse_result.revenue[P1] == SOURCE_UNAVAILABLE
    assert sparse_result.store_count[P1] == SOURCE_UNAVAILABLE
    assert sparse_result.revenue_growth[P2] == SOURCE_UNAVAILABLE
    assert sparse_result.store_count_growth[P2] == SOURCE_UNAVAILABLE
    assert sparse_result.growth_difference_pp[P2] == SOURCE_UNAVAILABLE
    skipped = 100.0 * ((120.0 - 80.0) / 80.0 - (767 - 655) / 655)
    assert sparse_result.growth_difference_pp[P2] != skipped
    assert sparse_result.unavailable_reasons[P2] == (
        REASON_MISSING_PRIOR_REVENUE,
        REASON_MISSING_PRIOR_STORE_COUNT,
    )


def test_independently_missing_revenue_and_counts():
    missing_revenue = _fin_with_relationship(
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
        revenue={P0: 80.0, P2: 120.0},
        extra_periods=[P0, P1, P2],
    )
    missing_counts = _fin_with_relationship(
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P2, 767),
        revenue={P0: 80.0, P1: 100.0, P2: 120.0},
        extra_periods=[P0, P1, P2],
    )
    no_revenue_line = _fin_with_relationship(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    rev = compute_operating_kpi_revenue_store_relationship(missing_revenue)
    counts = compute_operating_kpi_revenue_store_relationship(missing_counts)
    absent_line = compute_operating_kpi_revenue_store_relationship(no_revenue_line)
    assert rev.revenue[P1] == SOURCE_UNAVAILABLE
    assert rev.store_count[P1] == 711
    assert rev.revenue_growth[P1] == SOURCE_UNAVAILABLE
    assert rev.store_count_growth[P1] == pytest.approx((711 - 655) / 655)
    assert rev.growth_difference_pp[P1] == SOURCE_UNAVAILABLE
    assert rev.unavailable_reasons[P1] == (REASON_MISSING_REVENUE,)
    assert rev.unavailable_reasons[P2] == (REASON_MISSING_PRIOR_REVENUE,)
    assert counts.revenue_growth[P1] == pytest.approx((100.0 - 80.0) / 80.0)
    assert counts.store_count_growth[P1] == SOURCE_UNAVAILABLE
    assert counts.growth_difference_pp[P1] == SOURCE_UNAVAILABLE
    assert counts.unavailable_reasons[P1] == (REASON_MISSING_STORE_COUNT,)
    assert counts.unavailable_reasons[P2] == (REASON_MISSING_PRIOR_STORE_COUNT,)
    assert absent_line.revenue[P1] == SOURCE_UNAVAILABLE
    assert absent_line.revenue[P2] == SOURCE_UNAVAILABLE
    assert absent_line.store_count[P2] == 767
    assert absent_line.growth_difference_pp[P2] == SOURCE_UNAVAILABLE
    assert absent_line.unavailable_reasons[P2] == (
        REASON_MISSING_REVENUE,
        REASON_MISSING_PRIOR_REVENUE,
    )


def test_zero_denominators_and_missing_precedence():
    zero_revenue = _fin_with_relationship(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 12),
        revenue={P1: 0.0, P2: 50.0},
    )
    zero_stores = _fin_with_relationship(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 10),
        revenue={P1: 80.0, P2: 88.0},
    )
    both_zero = _fin_with_relationship(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 0),
        revenue={P1: 0.0, P2: 0.0},
    )
    mixed = _fin_with_relationship(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 10),
        revenue={P2: 50.0},
        extra_periods=[P1, P2],
    )
    reported_zeros = compute_operating_kpi_revenue_store_relationship(
        _fin_with_relationship(
            _kpi_model_observation(P1, 10),
            _kpi_model_observation(P2, 0),
            revenue={P1: 80.0, P2: 0.0},
        )
    )
    rev = compute_operating_kpi_revenue_store_relationship(zero_revenue)
    stores = compute_operating_kpi_revenue_store_relationship(zero_stores)
    both = compute_operating_kpi_revenue_store_relationship(both_zero)
    mixed_result = compute_operating_kpi_revenue_store_relationship(mixed)
    assert rev.revenue[P1] == 0.0
    assert rev.revenue_growth[P2] == UNDEFINED_RATIO
    assert isinstance(rev.store_count_growth[P2], float)
    assert rev.growth_difference_pp[P2] == UNDEFINED_RATIO
    assert rev.unavailable_reasons[P2] is None
    assert stores.store_count[P1] == 0
    assert stores.store_count_growth[P2] == UNDEFINED_RATIO
    assert stores.growth_difference_pp[P2] == UNDEFINED_RATIO
    assert both.growth_difference_pp[P2] == UNDEFINED_RATIO
    assert mixed_result.revenue_growth[P2] == SOURCE_UNAVAILABLE
    assert mixed_result.store_count_growth[P2] == UNDEFINED_RATIO
    assert mixed_result.growth_difference_pp[P2] == SOURCE_UNAVAILABLE
    assert mixed_result.unavailable_reasons[P2] == (REASON_MISSING_PRIOR_REVENUE,)
    assert reported_zeros.revenue[P2] == 0.0
    assert reported_zeros.store_count[P2] == 0
    assert reported_zeros.revenue_growth[P2] == -1.0
    assert reported_zeros.store_count_growth[P2] == -1.0
    assert reported_zeros.growth_difference_pp[P2] == 0.0


def test_explicit_revenue_concept_precedence_and_ambiguity_rejection():
    precedence = _fin_with_relationship(
        _kpi_model_observation(P1, 100),
        _kpi_model_observation(P2, 110),
        extra_periods=[P1, P2],
        income_statement=[
            _revenue_line({P1: 999.0, P2: 999.0}, label="Revenue", concept=""),
            _revenue_line({P1: 200.0, P2: 220.0}, label="Net sales", concept="revenue"),
        ],
    )
    before = copy.deepcopy(precedence.income_statement)
    result = compute_operating_kpi_revenue_store_relationship(precedence)
    assert result.revenue[P1] == 200.0
    assert result.revenue[P2] == 220.0
    assert result.revenue_growth[P2] == pytest.approx(0.1)
    assert precedence.income_statement == before

    alias = _fin_with_relationship(
        _kpi_model_observation(P1, 100),
        _kpi_model_observation(P2, 110),
        extra_periods=[P1, P2],
        income_statement=[_revenue_line({P1: 50.0, P2: 55.0}, label="Net sales", concept="")],
    )
    alias_result = compute_operating_kpi_revenue_store_relationship(alias)
    assert alias_result.revenue[P2] == 55.0
    assert alias_result.revenue_growth[P2] == pytest.approx(0.1)

    ambiguous = _fin_with_relationship(
        _kpi_model_observation(P1, 100),
        _kpi_model_observation(P2, 110),
        extra_periods=[P1, P2],
        income_statement=[
            _revenue_line({P1: 10.0, P2: 11.0}, label="Revenue", concept="revenue"),
            _revenue_line({P1: 20.0, P2: 22.0}, label="Turnover", concept="revenue"),
        ],
    )
    original = copy.deepcopy(ambiguous)
    with pytest.raises(AmbiguousLineError, match="Ambiguous concept='revenue'"):
        compute_operating_kpi_revenue_store_relationship(ambiguous)
    assert ambiguous.income_statement == original.income_statement
    assert ambiguous.historical_operating_kpis == original.historical_operating_kpis


def test_malformed_interim_and_noncanonical_axes_fail_closed():
    fin = _fin_with_relationship(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
        revenue={P1: 100.0, P2: 110.0},
    )
    original = copy.deepcopy(fin.historical_operating_kpis)
    original_is = copy.deepcopy(fin.income_statement)

    fin.historical_operating_kpis.observations[0].value = -1
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative integer"):
        compute_operating_kpi_revenue_store_relationship(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    with pytest.raises(ValueError, match="canonical fiscal axis"):
        compute_operating_kpi_revenue_store_relationship(fin, [P2, P1])
    assert fin.historical_operating_kpis == original
    assert fin.income_statement == original_is

    interim = _fin_with_relationship(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
        revenue={P1: 100.0, P2: 110.0},
        interim=True,
    )
    interim_before = copy.deepcopy(interim)
    with pytest.raises(PeriodAxisError, match="annual fiscal periods"):
        compute_operating_kpi_revenue_store_relationship(interim)
    assert interim.historical_operating_kpis == interim_before.historical_operating_kpis
    assert interim.income_statement == interim_before.income_statement
    assert [period.is_interim for period in interim.periods] == [True, True]

    success_before = copy.deepcopy(original)
    result = compute_operating_kpi_revenue_store_relationship(fin)
    assert fin.historical_operating_kpis == success_before
    assert fin.income_statement == original_is
    assert result.growth_difference_pp[P2] == pytest.approx(
        100.0 * ((110.0 - 100.0) / 100.0 - (767 - 711) / 711)
    )


def test_shuffled_observations_are_deterministic_and_immutable():
    fin = _fin_with_relationship(
        _kpi_model_observation(P2, 767),
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P1, 711),
        revenue={P2: 120.0, P0: 80.0, P1: 100.0},
        extra_periods=[P0, P1, P2],
    )
    before = copy.deepcopy(fin.historical_operating_kpis)
    first = compute_operating_kpi_revenue_store_relationship(fin)
    second = compute_operating_kpi_revenue_store_relationship(fin)
    _assert_relationship_matches(
        first,
        _independent_relationship(
            [P0, P1, P2], {P0: 80.0, P1: 100.0, P2: 120.0}, {P0: 655, P1: 711, P2: 767}
        ),
    )
    assert first == second
    assert fin.historical_operating_kpis == before
    original_order = [item.period for item in fin.historical_operating_kpis.observations]
    fin.historical_operating_kpis.observations = list(
        reversed(list(fin.historical_operating_kpis.observations))
    )
    reordered = compute_operating_kpi_revenue_store_relationship(fin)
    assert reordered == first
    assert [item.period for item in fin.historical_operating_kpis.observations] == list(
        reversed(original_order)
    )


def test_mixed_histories_preserve_store_and_management_analytics():
    stores = (
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    store_only = _fin_with_relationship(
        *stores, revenue={P0: 80.0, P1: 100.0, P2: 120.0}, extra_periods=[P0, P1, P2]
    )
    mixed = _fin_with_relationship(
        *stores,
        revenue={P0: 80.0, P1: 100.0, P2: 120.0},
        management=[
            _compsales(period=P2, value=-3.0),
            _spsf(period=P2, value=0.0),
        ],
        extra_periods=[P0, P1, P2],
    )
    left = compute_operating_kpi_revenue_store_relationship(store_only)
    right = compute_operating_kpi_revenue_store_relationship(mixed)
    expected = _independent_relationship(
        [P0, P1, P2], {P0: 80.0, P1: 100.0, P2: 120.0}, {P0: 655, P1: 711, P2: 767}
    )
    _assert_relationship_matches(left, expected)
    _assert_relationship_matches(right, expected)
    store_series = compute_operating_kpi_series(mixed)
    expected_stores = _independent_from_counts([P0, P1, P2], {P0: 655, P1: 711, P2: 767})
    _assert_series_matches(store_series, expected_stores)
    assert management_kpi_applicable(store_only) is False
    assert management_kpi_applicable(mixed) is True
    management = compute_management_kpi_series(mixed)
    assert management.series
    restored = standardized_from_payload(standardized_to_payload(mixed))
    reloaded = compute_operating_kpi_revenue_store_relationship(restored)
    _assert_relationship_matches(reloaded, expected)
    assert compute_management_kpi_series(restored) == management


def test_source_grounded_reload_matches_independent_relationship(tmp_path: Path):
    _dest, validated = _validated_augmented(tmp_path)
    outputs = []
    for order in (validated, list(reversed(validated))):
        reconciled = reconcile_filings(order, admit_periods=ADMIT_2022)
        fin = standardize_reconciled(reconciled)
        restored = standardized_from_payload(
            json.loads(json.dumps(standardized_to_payload(fin)))
        )
        outputs.append((reconciled, fin, restored))

    expected_growth = None
    for reconciled, fin, restored in outputs:
        axis = canonical_fiscal_periods(restored)
        assert axis == [P2022, P2023, P2024, P2025, P2026]
        pre = compute_operating_kpi_revenue_store_relationship(fin)
        post = compute_operating_kpi_revenue_store_relationship(restored)
        assert pre == post
        expected = _independent_relationship(axis, REVENUE_ANCHORS, INDEPENDENT_STORE_TOTALS)
        _assert_relationship_matches(post, expected)
        store = compute_operating_kpi_series(restored)
        assert post.store_count == store.period_end_count
        assert post.store_count_growth == store.growth
        assert post.store_count[P2022] == 574
        assert post.store_count[P2023] == 655
        assert post.store_count[P2024] == 711
        assert post.store_count[P2025] == 767
        assert post.store_count[P2026] == 811
        assert post.store_count_growth[P2022] is None
        assert store.net_count_change[P2023] == 81
        assert store.net_count_change[P2024] == 56
        assert store.net_count_change[P2025] == 56
        assert store.net_count_change[P2026] == 44
        assert len(reconciled.selected_geographic_facts) == 56
        americas = [
            item
            for item in reconciled.selected_geographic_facts
            if item.period == P2025 and item.fact_type.endswith("net_revenue.americas")
        ]
        assert len(americas) == 1
        assert americas[0].value == 7928156
        if expected_growth is None:
            expected_growth = post
        else:
            assert post == expected_growth


def test_supplied_deferred_documents_do_not_activate_relationship(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_rec = _reconcile(mixed, admit=ADMIT_2022)
    annual_rec = _reconcile(annual, admit=ADMIT_2022)
    mixed_fin = standardize_reconciled(mixed_rec)
    annual_fin = standardize_reconciled(annual_rec)
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None
    assert operating_kpi_revenue_store_relationship_applicable(mixed_fin) is False
    assert operating_kpi_revenue_store_relationship_applicable(annual_fin) is False
    assert management_kpi_applicable(mixed_fin) is False
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(mixed_fin)
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(mixed_fin)
    assert _canonicalize(standardized_to_payload(mixed_fin)) == _canonicalize(
        standardized_to_payload(annual_fin)
    )
    assert _statement_provenance(reconciliation_provenance_payload(mixed_rec)) == (
        _statement_provenance(reconciliation_provenance_payload(annual_rec))
    )
    assert reconciliation_conflicts_payload(mixed_rec) == reconciliation_conflicts_payload(
        annual_rec
    )
    admission = management_admission_payload(mixed_rec.management_admission)
    assert admission["reported_observation_count"] == 135
    assert admission["reconciliation"]["selected_count"] == 0
    assert _bytes_by_name(EXTRACTED) == before


def test_augmented_mixed_without_selection_keeps_store_relationship(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    for name in MANAGEMENT_NAMES:
        Path(dest / name).write_bytes((EXTRACTED / name).read_bytes())
    reconciled = _reconcile(dest, admit=ADMIT_2022)
    fin = standardize_reconciled(reconciled)
    assert operating_kpi_applicable(fin) is True
    assert management_kpi_applicable(fin) is False
    assert operating_kpi_revenue_store_relationship_applicable(fin) is True
    result = compute_operating_kpi_revenue_store_relationship(fin)
    expected = _independent_relationship(
        canonical_fiscal_periods(fin), REVENUE_ANCHORS, INDEPENDENT_STORE_TOTALS
    )
    _assert_relationship_matches(result, expected)
    assert result.store_count[P2022] == 574
    assert result.store_count[P2023] == 655
    assert result.store_count[P2024] == 711
    assert result.store_count[P2025] == 767
    assert result.store_count[P2026] == 811
    store = compute_operating_kpi_series(fin)
    assert store.net_count_change[P2023] == 81
    assert store.net_count_change[P2024] == 56
    assert store.net_count_change[P2025] == 56
    assert store.net_count_change[P2026] == 44
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(fin)
    restored = standardized_from_payload(standardized_to_payload(fin))
    assert compute_operating_kpi_revenue_store_relationship(restored) == result
