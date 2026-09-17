"""Optional consolidated-revenue and store-count growth relationship.

Separate source-gated module. Requires validated store-count observations.
Absent, null, or management-only histories make the module absent. Deferred
management observations are not promoted.

Aligns reported consolidated revenue and period-end company-operated store
counts to the canonical annual fiscal axis. Revenue is resolved from
income-statement lines with existing explicit-concept precedence and
ambiguity rejection. Currency and monetary-scale metadata are retained.

Computes adjacent consolidated revenue growth ``(current - prior) / prior``
and reuses unchanged store-count growth. When both growth values are numeric,
computes ``100 * (revenue_growth - store_count_growth)`` in percentage points.

Inputs are labeled as consolidated revenue and company-operated period-end
store count. Calculations are analyst-derived. The difference compares
distinct scopes and is not revenue attribution, same-store sales, store
productivity, organic growth, or causal evidence. No revenue-per-store
ratio is derived.

Opening comparisons are ``None``. Missing current or prior inputs suppress
only dependent outputs with ``SOURCE_UNAVAILABLE`` and explicit reasons.
Zero denominators retain ``UNDEFINED_RATIO`` and propagate to the difference.
Missing-input unavailability takes precedence when both conditions occur.

Reported zeros and declines are preserved. Gaps are never compressed,
substituted, annualized, or calendar-adjusted. Malformed contracts,
interim-only histories, and noncanonical requested axes are rejected
without mutation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import MissingLineError, resolve_line
from .operating_kpi import compute_operating_kpi_series, operating_kpi_applicable
from .period_axis import PeriodAxisError, canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable, ratio_or_na

OPERATING_KPI_RELATIONSHIP_TOLERANCE = 1e-12
REVENUE_CONCEPT = "revenue"
REVENUE_INPUT_LABEL = "consolidated revenue"
STORE_COUNT_INPUT_LABEL = "company-operated period-end store count"
CALCULATION_KIND = "analyst-derived"
DIFFERENCE_UNIT = "percentage points"
SCOPE_NOTE = (
    "The difference compares consolidated revenue growth with company-operated "
    "period-end store-count growth. These inputs have distinct scopes. The "
    "difference is not revenue attribution, same-store sales, store "
    "productivity, organic growth, or causal evidence."
)
REASON_MISSING_REVENUE = "missing_revenue"
REASON_MISSING_PRIOR_REVENUE = "missing_prior_revenue"
REASON_MISSING_STORE_COUNT = "missing_store_count"
REASON_MISSING_PRIOR_STORE_COUNT = "missing_prior_store_count"


@dataclass(frozen=True)
class OperatingKpiRevenueStoreRelationship:
    """Descriptive revenue-growth versus store-count-growth comparison."""

    periods: tuple[date, ...]
    currency: str
    monetary_scale: str
    revenue_input_label: str
    store_count_input_label: str
    calculation_kind: str
    difference_unit: str
    scope_note: str
    revenue: dict[date, float | str]
    store_count: dict[date, float | str]
    store_count_unit: dict[date, str]
    revenue_growth: dict[date, float | str | None]
    store_count_growth: dict[date, float | str | None]
    growth_difference_pp: dict[date, float | str | None]
    unavailable_reasons: dict[date, tuple[str, ...] | None]


def operating_kpi_revenue_store_relationship_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Module is present only when store-count observations are supplied."""
    return operating_kpi_applicable(financials)


def _require_annual_axis(financials: StandardizedFinancials) -> None:
    if not any(not period.is_interim for period in financials.periods):
        raise PeriodAxisError(
            "operating KPI revenue/store relationship requires annual fiscal periods"
        )


def _revenue_amount(line: LineItem | None, period: date) -> float | None:
    if line is None:
        return None
    raw = line.values.get(period)
    if raw is None:
        return None
    try:
        number = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"invalid source value for {REVENUE_CONCEPT} period {period.isoformat()}: {raw!r}"
        ) from exc
    if not math.isfinite(number):
        raise ValueError(
            f"invalid source value for {REVENUE_CONCEPT} period {period.isoformat()}: {raw!r}"
        )
    return number


def _growth_value(
    current: float | None,
    prior: float | None,
    *,
    opening: bool,
    missing_current: str,
    missing_prior: str,
) -> tuple[float | str | None, tuple[str, ...]]:
    if opening:
        return None, ()
    reasons: list[str] = []
    if current is None:
        reasons.append(missing_current)
    if prior is None:
        reasons.append(missing_prior)
    if reasons:
        return SOURCE_UNAVAILABLE, tuple(reasons)
    assert current is not None and prior is not None
    return ratio_or_na(current - prior, prior), ()


def _difference_pp(
    revenue_growth: float | str | None,
    store_growth: float | str | None,
    *,
    opening: bool,
) -> float | str | None:
    if opening:
        return None
    if is_source_unavailable(revenue_growth) or is_source_unavailable(store_growth):
        return SOURCE_UNAVAILABLE
    if revenue_growth == UNDEFINED_RATIO or store_growth == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    assert isinstance(revenue_growth, (int, float))
    assert isinstance(store_growth, (int, float))
    return 100.0 * (float(revenue_growth) - float(store_growth))


def compute_operating_kpi_revenue_store_relationship(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> OperatingKpiRevenueStoreRelationship:
    """Compare consolidated revenue growth with store-count growth."""
    if not operating_kpi_revenue_store_relationship_applicable(financials):
        raise MissingLineError(
            "operating KPI revenue/store relationship sources not available"
        )

    _require_annual_axis(financials)
    store_series = compute_operating_kpi_series(financials, periods)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError(
            "operating KPI revenue/store relationship must use the canonical fiscal axis"
        )

    revenue_line = resolve_line(
        financials.income_statement, REVENUE_CONCEPT, required=False
    ).item

    revenue: dict[date, float | str] = {}
    revenue_growth: dict[date, float | str | None] = {}
    growth_difference_pp: dict[date, float | str | None] = {}
    unavailable_reasons: dict[date, tuple[str, ...] | None] = {}

    for index, period in enumerate(axis):
        opening = index == 0
        current_revenue = _revenue_amount(revenue_line, period)
        prior_period = None if opening else axis[index - 1]
        prior_revenue = (
            None if prior_period is None else _revenue_amount(revenue_line, prior_period)
        )
        revenue[period] = (
            SOURCE_UNAVAILABLE if current_revenue is None else current_revenue
        )
        current_growth, revenue_reasons = _growth_value(
            current_revenue,
            prior_revenue,
            opening=opening,
            missing_current=REASON_MISSING_REVENUE,
            missing_prior=REASON_MISSING_PRIOR_REVENUE,
        )
        revenue_growth[period] = current_growth

        store_growth = store_series.growth[period]
        store_reasons: tuple[str, ...] = ()
        if not opening and is_source_unavailable(store_growth):
            reasons: list[str] = []
            if is_source_unavailable(store_series.period_end_count[period]):
                reasons.append(REASON_MISSING_STORE_COUNT)
            if is_source_unavailable(store_series.period_end_count[prior_period]):
                reasons.append(REASON_MISSING_PRIOR_STORE_COUNT)
            store_reasons = tuple(reasons)

        difference = _difference_pp(
            current_growth, store_growth, opening=opening
        )
        growth_difference_pp[period] = difference
        if is_source_unavailable(difference):
            unavailable_reasons[period] = revenue_reasons + store_reasons
        else:
            unavailable_reasons[period] = None

    return OperatingKpiRevenueStoreRelationship(
        periods=store_series.periods,
        currency=financials.currency,
        monetary_scale=financials.units,
        revenue_input_label=REVENUE_INPUT_LABEL,
        store_count_input_label=STORE_COUNT_INPUT_LABEL,
        calculation_kind=CALCULATION_KIND,
        difference_unit=DIFFERENCE_UNIT,
        scope_note=SCOPE_NOTE,
        revenue=revenue,
        store_count=dict(store_series.period_end_count),
        store_count_unit=dict(store_series.unit),
        revenue_growth=revenue_growth,
        store_count_growth=dict(store_series.growth),
        growth_difference_pp=growth_difference_pp,
        unavailable_reasons=unavailable_reasons,
    )
