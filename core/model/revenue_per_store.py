"""Generic historical Revenue per Store from admitted revenue and store counts.

Optional, source-gated module. Present only when company-operated store-count
observations are supplied. Consumes admitted consolidated revenue and
period-end company-operated store history after existing contract validation.

Period-end Revenue per Store is consolidated revenue divided by the same-period
company-operated period-end store count. Average-store Revenue per Store is
consolidated revenue divided by the average of the current and immediately
prior admitted period-end counts. The two denominators are distinct identities.
Neither is substituted for the other. Average-store results require both
adjacent admitted counts and are never inferred from a single snapshot.

Total-company revenue divided by company-operated stores includes revenue
outside those stores. The ratio is not store-only productivity, sales per
square foot, or comparable sales.

Missing, incompatible, or non-numeric inputs yield ``SOURCE_UNAVAILABLE``.
A zero denominator yields ``UNDEFINED_RATIO``. Opening average-store,
adjacent-change, and growth results are absent. Gaps are never compressed
or substituted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .line_resolver import MissingLineError, resolve_line
from .operating_kpi import compute_operating_kpi_series, operating_kpi_applicable
from .operating_kpi_relationships import (
    CALCULATION_KIND,
    REASON_MISSING_PRIOR_REVENUE,
    REASON_MISSING_PRIOR_STORE_COUNT,
    REASON_MISSING_REVENUE,
    REASON_MISSING_STORE_COUNT,
    REVENUE_CONCEPT,
    REVENUE_INPUT_LABEL,
    STORE_COUNT_INPUT_LABEL,
    _require_annual_axis,
    _revenue_amount,
)
from .period_axis import canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable, ratio_or_na

REVENUE_PER_STORE_RATIO_TOLERANCE = 1e-12
PERIOD_END_DENOMINATOR_LABEL = "period-end company-operated stores"
AVERAGE_STORE_DENOMINATOR_LABEL = (
    "average of adjacent period-end company-operated stores"
)
SCOPE_NOTE = (
    "Total-company consolidated revenue divided by company-operated stores "
    "includes revenue outside those stores. The ratio is not store-only "
    "productivity, sales per square foot, or comparable sales. Period-end and "
    "average-store denominators are distinct and are never substituted."
)


@dataclass(frozen=True)
class RevenuePerStoreSeries:
    """Historical Revenue per Store keyed by canonical fiscal periods."""

    periods: tuple[date, ...]
    currency: str
    monetary_scale: str
    revenue_input_label: str
    store_count_input_label: str
    period_end_denominator_label: str
    average_store_denominator_label: str
    calculation_kind: str
    scope_note: str
    revenue: dict[date, float | str]
    period_end_store_count: dict[date, float | str]
    average_store_count: dict[date, float | str | None]
    period_end_revenue_per_store: dict[date, float | str]
    average_store_revenue_per_store: dict[date, float | str | None]
    period_end_change: dict[date, float | str | None]
    period_end_growth: dict[date, float | str | None]
    unavailable_reasons: dict[date, tuple[str, ...] | None]


def revenue_per_store_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when store-count observations are supplied."""
    return operating_kpi_applicable(financials)


def _count_amount(value: float | str) -> float | None:
    if is_source_unavailable(value):
        return None
    return float(value)


def _ratio(numerator: float | None, denominator: float | None) -> float | str:
    if numerator is None or denominator is None:
        return SOURCE_UNAVAILABLE
    return ratio_or_na(numerator, denominator)


def compute_revenue_per_store_series(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> RevenuePerStoreSeries:
    """Compute period-end and average-store Revenue per Store on the canonical axis."""
    if not revenue_per_store_applicable(financials):
        raise MissingLineError("operating KPI revenue per store sources not available")

    _require_annual_axis(
        financials,
        message="operating KPI revenue per store requires annual fiscal periods",
    )
    store_series = compute_operating_kpi_series(financials, periods)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError(
            "operating KPI revenue per store must use the canonical fiscal axis"
        )

    revenue_line = resolve_line(
        financials.income_statement, REVENUE_CONCEPT, required=False
    ).item

    revenue: dict[date, float | str] = {}
    period_end_store_count: dict[date, float | str] = {}
    average_store_count: dict[date, float | str | None] = {}
    period_end_revenue_per_store: dict[date, float | str] = {}
    average_store_revenue_per_store: dict[date, float | str | None] = {}
    period_end_change: dict[date, float | str | None] = {}
    period_end_growth: dict[date, float | str | None] = {}
    unavailable_reasons: dict[date, tuple[str, ...] | None] = {}
    numeric_period_end: dict[date, float] = {}

    for index, period in enumerate(axis):
        opening = index == 0
        prior_period = None if opening else axis[index - 1]
        current_revenue = _revenue_amount(revenue_line, period)
        current_count = _count_amount(store_series.period_end_count[period])
        prior_count = (
            None
            if prior_period is None
            else _count_amount(store_series.period_end_count[prior_period])
        )
        revenue[period] = (
            SOURCE_UNAVAILABLE if current_revenue is None else current_revenue
        )
        period_end_store_count[period] = store_series.period_end_count[period]
        period_end = _ratio(current_revenue, current_count)
        period_end_revenue_per_store[period] = period_end
        if isinstance(period_end, float):
            numeric_period_end[period] = period_end

        reasons: list[str] = []
        if current_revenue is None:
            reasons.append(REASON_MISSING_REVENUE)
        if current_count is None:
            reasons.append(REASON_MISSING_STORE_COUNT)

        if opening:
            average_store_count[period] = None
            average_store_revenue_per_store[period] = None
            period_end_change[period] = None
            period_end_growth[period] = None
            unavailable_reasons[period] = tuple(reasons) if reasons else None
            continue

        if current_count is None or prior_count is None:
            average_store_count[period] = SOURCE_UNAVAILABLE
            average_store_revenue_per_store[period] = SOURCE_UNAVAILABLE
            if prior_count is None:
                reasons.append(REASON_MISSING_PRIOR_STORE_COUNT)
        else:
            average = (current_count + prior_count) / 2.0
            average_store_count[period] = average
            average_store_revenue_per_store[period] = _ratio(current_revenue, average)

        prior_rps = numeric_period_end.get(prior_period) if prior_period else None
        current_rps = numeric_period_end.get(period)
        if current_rps is None or prior_rps is None:
            period_end_change[period] = SOURCE_UNAVAILABLE
            period_end_growth[period] = SOURCE_UNAVAILABLE
            if prior_period is not None:
                prior_revenue = _revenue_amount(revenue_line, prior_period)
                if prior_revenue is None:
                    reasons.append(REASON_MISSING_PRIOR_REVENUE)
                if prior_count is None and REASON_MISSING_PRIOR_STORE_COUNT not in reasons:
                    reasons.append(REASON_MISSING_PRIOR_STORE_COUNT)
        else:
            period_end_change[period] = current_rps - prior_rps
            period_end_growth[period] = ratio_or_na(current_rps - prior_rps, prior_rps)

        change = period_end_change[period]
        if is_source_unavailable(period_end) or is_source_unavailable(change):
            unavailable_reasons[period] = tuple(dict.fromkeys(reasons)) or None
        else:
            unavailable_reasons[period] = None

    return RevenuePerStoreSeries(
        periods=store_series.periods,
        currency=financials.currency,
        monetary_scale=financials.units,
        revenue_input_label=REVENUE_INPUT_LABEL,
        store_count_input_label=STORE_COUNT_INPUT_LABEL,
        period_end_denominator_label=PERIOD_END_DENOMINATOR_LABEL,
        average_store_denominator_label=AVERAGE_STORE_DENOMINATOR_LABEL,
        calculation_kind=CALCULATION_KIND,
        scope_note=SCOPE_NOTE,
        revenue=revenue,
        period_end_store_count=dict(store_series.period_end_count),
        average_store_count=average_store_count,
        period_end_revenue_per_store=period_end_revenue_per_store,
        average_store_revenue_per_store=average_store_revenue_per_store,
        period_end_change=period_end_change,
        period_end_growth=period_end_growth,
        unavailable_reasons=unavailable_reasons,
    )
