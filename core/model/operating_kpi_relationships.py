"""Optional consolidated-revenue growth relationships.

Separate source-gated APIs. The store-count relationship requires validated
store-count observations. The comparable-sales relationship requires
validated global reported ``comparable_sales_growth`` observations. The
sales-per-square-foot relationship requires validated global reported
company-operated-store ``sales_per_square_foot`` observations. Absent,
null, or store-only histories activate neither management relationship.
Sales-per-square-foot-only histories do not activate the comparable-sales
API. Comparable-sales-only histories do not activate the
sales-per-square-foot API. Deferred management observations are not
promoted.

Aligns reported consolidated revenue to the canonical annual fiscal axis.
Revenue is resolved from income-statement lines with existing
explicit-concept precedence and ambiguity rejection. Currency and
monetary-scale metadata are retained.

The store-count API computes adjacent consolidated revenue growth
``(current - prior) / prior`` and reuses unchanged store-count growth.
When both growth values are numeric, it computes
``100 * (revenue_growth - store_count_growth)`` in percentage points.

The comparable-sales API computes the same statement-derived revenue
growth and reuses the current reported comparable-sales percentage
directly. The descriptive difference is
``100 * revenue_growth - current_reported_comparable_sales_percent``.
It does not compute growth of a growth rate or substitute the adjacent
percentage-point change. Series are keyed by full management identity
and are never selected, merged, or averaged.

The sales-per-square-foot API reuses ``compute_management_kpi_series``
fractional SPSF growth and the same statement-derived revenue growth.
The descriptive difference is ``100 * (revenue_growth - spsf_growth)``
in percentage points. Reported ``USD_per_square_foot`` is retained
without statement monetary scaling. Adjacent SPSF semantic gates are
unchanged. Series stay keyed by full identity and are never merged.

Opening revenue growth and differences are ``None``. Available reported
comparable-sales values remain visible in the opening period. A current
reported comparable-sales observation does not require a prior KPI
observation. Revenue growth requires immediately adjacent canonical
revenue inputs. SPSF growth requires immediately adjacent semantically
compatible reported observations.

Missing required inputs suppress only dependent outputs with
``SOURCE_UNAVAILABLE`` and explicit reasons. Zero prior revenue retains
``UNDEFINED_RATIO``. Missing-input unavailability takes precedence in the
difference. Reported zeros and declines are preserved. Gaps are never
compressed, substituted, annualized, or calendar-adjusted. Existing
semantic-discontinuity gates are unchanged. Malformed contracts,
interim-only histories, and noncanonical requested axes are rejected
without mutation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

from ..data.historical_operating_kpis import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    MANAGEMENT_IDENTITY_FIELDS,
    UNIT_PERCENT,
    UNIT_USD_PER_SQUARE_FOOT,
    encode_metric_identity,
    management_identity_fields,
    validate_historical_operating_kpis,
)
from ..ingestion.management_kpi_identity import POP_COMPANY_OPERATED_STORES
from ..data.interface import (
    HistoricalManagementKpiObservation,
    LineItem,
    StandardizedFinancials,
)
from .line_resolver import MissingLineError, resolve_line
from .management_kpi import (
    REASON_MISSING_OBSERVATION,
    REASON_MISSING_PRIOR_OBSERVATION,
    compute_management_kpi_series,
)
from .operating_kpi import compute_operating_kpi_series, operating_kpi_applicable
from .period_axis import PeriodAxisError, canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable, ratio_or_na

OPERATING_KPI_RELATIONSHIP_TOLERANCE = 1e-12
REVENUE_CONCEPT = "revenue"
REVENUE_INPUT_LABEL = "consolidated revenue"
STORE_COUNT_INPUT_LABEL = "company-operated period-end store count"
COMPARABLE_SALES_INPUT_LABEL = "reported global comparable-sales growth"
SALES_PER_SQUARE_FOOT_INPUT_LABEL = (
    "reported company-operated-store sales per square foot"
)
CALCULATION_KIND = "analyst-derived"
REVENUE_GROWTH_KIND = "statement-derived"
COMPARABLE_SALES_KIND = "reported"
SALES_PER_SQUARE_FOOT_KIND = "reported"
DIFFERENCE_KIND = "analyst-derived"
DIFFERENCE_UNIT = "percentage points"
ELIGIBLE_COMPARABLE_SALES_GEOGRAPHY = "global"
ELIGIBLE_COMPARABLE_SALES_BASIS = "reported"
ELIGIBLE_COMPARABLE_SALES_UNIT = UNIT_PERCENT
ELIGIBLE_COMPARABLE_SALES_COMPARISON = "year_over_year"
ELIGIBLE_SPSF_GEOGRAPHY = ""
ELIGIBLE_SPSF_POPULATION = POP_COMPANY_OPERATED_STORES
ELIGIBLE_SPSF_BASIS = "reported"
ELIGIBLE_SPSF_UNIT = UNIT_USD_PER_SQUARE_FOOT
ELIGIBLE_SPSF_COMPARISON = ""
SCOPE_NOTE = (
    "The difference compares consolidated revenue growth with company-operated "
    "period-end store-count growth. These inputs have distinct scopes. The "
    "difference is not revenue attribution, same-store sales, store "
    "productivity, organic growth, or causal evidence."
)
COMPARABLE_SALES_SCOPE_NOTE = (
    "The difference compares statement-derived consolidated revenue growth "
    "with reported global comparable-sales growth. Consolidated revenue and "
    "the comparable-sales population have distinct scopes. Disclosed calendar "
    "adjustments and reporting-basis differences are retained and are not "
    "normalized. The difference is not new-store contribution, revenue "
    "attribution, organic growth, productivity, or causal evidence."
)
SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE = (
    "The difference compares statement-derived consolidated revenue growth "
    "with disclosed sales-per-square-foot growth. Consolidated revenue and "
    "the disclosed SPSF population have different scopes. The comparison "
    "does not establish revenue attribution, selling-area growth, or causal "
    "effects."
)
REASON_MISSING_REVENUE = "missing_revenue"
REASON_MISSING_PRIOR_REVENUE = "missing_prior_revenue"
REASON_MISSING_STORE_COUNT = "missing_store_count"
REASON_MISSING_PRIOR_STORE_COUNT = "missing_prior_store_count"
REASON_MISSING_COMPARABLE_SALES = "missing_comparable_sales"
REASON_MISSING_SALES_PER_SQUARE_FOOT = "missing_sales_per_square_foot"
REASON_MISSING_PRIOR_SALES_PER_SQUARE_FOOT = "missing_prior_sales_per_square_foot"


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


def _require_annual_axis(
    financials: StandardizedFinancials,
    *,
    message: str = "operating KPI revenue/store relationship requires annual fiscal periods",
) -> None:
    if not any(not period.is_interim for period in financials.periods):
        raise PeriodAxisError(message)


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


@dataclass(frozen=True)
class OperatingKpiRevenueComparableSalesIdentitySeries:
    """One full-identity revenue versus reported comparable-sales comparison."""

    identity: str
    family: str
    entity_ticker: str
    entity_company: str
    geography: str
    population: str
    unit: str
    basis: str
    comparison: str
    periods: tuple[date, ...]
    revenue: dict[date, float | str]
    comparable_sales_growth: dict[date, float | str]
    comparable_sales_unit: dict[date, str]
    definition_text: dict[date, str]
    period_kind: dict[date, str]
    calendar_week_adjustment: dict[date, str]
    calendar_reporting_basis: dict[date, str]
    qualifiers: dict[date, dict[str, str] | str]
    revenue_growth: dict[date, float | str | None]
    growth_difference_pp: dict[date, float | str | None]
    unavailable_reasons: dict[date, tuple[str, ...] | None]


@dataclass(frozen=True)
class OperatingKpiRevenueComparableSalesRelationship:
    """Descriptive revenue-growth versus reported comparable-sales comparisons."""

    periods: tuple[date, ...]
    identities: tuple[str, ...]
    currency: str
    monetary_scale: str
    revenue_input_label: str
    comparable_sales_input_label: str
    revenue_growth_kind: str
    comparable_sales_kind: str
    difference_kind: str
    difference_unit: str
    scope_note: str
    series: dict[str, OperatingKpiRevenueComparableSalesIdentitySeries]


def _is_eligible_global_reported_comparable_sales(
    item: HistoricalManagementKpiObservation,
) -> bool:
    return (
        item.family == FAMILY_COMPARABLE_SALES_GROWTH
        and item.geography == ELIGIBLE_COMPARABLE_SALES_GEOGRAPHY
        and item.basis == ELIGIBLE_COMPARABLE_SALES_BASIS
        and item.unit == ELIGIBLE_COMPARABLE_SALES_UNIT
        and item.comparison == ELIGIBLE_COMPARABLE_SALES_COMPARISON
    )


def _eligible_comparable_sales_observations(
    financials: StandardizedFinancials,
) -> tuple[HistoricalManagementKpiObservation, ...]:
    data = financials.historical_operating_kpis
    if data is None:
        return ()
    return tuple(
        item
        for item in data.management_observations
        if _is_eligible_global_reported_comparable_sales(item)
    )


def operating_kpi_revenue_comparable_sales_relationship_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Module is present only when eligible comparable-sales observations exist."""
    return bool(_eligible_comparable_sales_observations(financials))


def _unavailable_compsales_semantics() -> dict[str, str]:
    return {
        "comparable_sales_unit": SOURCE_UNAVAILABLE,
        "definition_text": SOURCE_UNAVAILABLE,
        "period_kind": SOURCE_UNAVAILABLE,
        "calendar_week_adjustment": SOURCE_UNAVAILABLE,
        "calendar_reporting_basis": SOURCE_UNAVAILABLE,
    }


def _compsales_difference_pp(
    revenue_growth: float | str | None,
    compsales_percent: float | str | None,
    *,
    opening: bool,
) -> float | str | None:
    if opening:
        return None
    if is_source_unavailable(revenue_growth) or is_source_unavailable(compsales_percent):
        return SOURCE_UNAVAILABLE
    if revenue_growth == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    assert isinstance(revenue_growth, (int, float))
    assert isinstance(compsales_percent, (int, float))
    return 100.0 * float(revenue_growth) - float(compsales_percent)


def _resolved_revenue_maps(
    financials: StandardizedFinancials,
    axis: list[date],
) -> tuple[dict[date, float | str], dict[date, float | str | None], dict[date, tuple[str, ...]]]:
    revenue_line = resolve_line(
        financials.income_statement, REVENUE_CONCEPT, required=False
    ).item
    revenue: dict[date, float | str] = {}
    revenue_growth: dict[date, float | str | None] = {}
    revenue_reasons: dict[date, tuple[str, ...]] = {}
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
        current_growth, reasons = _growth_value(
            current_revenue,
            prior_revenue,
            opening=opening,
            missing_current=REASON_MISSING_REVENUE,
            missing_prior=REASON_MISSING_PRIOR_REVENUE,
        )
        revenue_growth[period] = current_growth
        revenue_reasons[period] = reasons
    return revenue, revenue_growth, revenue_reasons


def _compsales_identity_index(
    observations: tuple[HistoricalManagementKpiObservation, ...],
) -> tuple[
    dict[str, dict[date, HistoricalManagementKpiObservation]],
    dict[str, dict[str, str]],
]:
    grouped: dict[str, dict[date, HistoricalManagementKpiObservation]] = {}
    fields_by_identity: dict[str, dict[str, str]] = {}
    for item in observations:
        fields = management_identity_fields(item)
        identity = encode_metric_identity(fields)
        fields_by_identity.setdefault(identity, dict(fields))
        grouped.setdefault(identity, {})[item.period] = item
    return grouped, fields_by_identity


def _compsales_identity_series(
    *,
    identity: str,
    fields: dict[str, str],
    axis: list[date],
    observations: dict[date, HistoricalManagementKpiObservation],
    revenue: dict[date, float | str],
    revenue_growth: dict[date, float | str | None],
    revenue_reasons: dict[date, tuple[str, ...]],
) -> OperatingKpiRevenueComparableSalesIdentitySeries:
    comparable_sales_growth: dict[date, float | str] = {}
    comparable_sales_unit: dict[date, str] = {}
    definition_text: dict[date, str] = {}
    period_kind: dict[date, str] = {}
    calendar_week_adjustment: dict[date, str] = {}
    calendar_reporting_basis: dict[date, str] = {}
    qualifiers: dict[date, dict[str, str] | str] = {}
    growth_difference_pp: dict[date, float | str | None] = {}
    unavailable_reasons: dict[date, tuple[str, ...] | None] = {}

    for index, period in enumerate(axis):
        opening = index == 0
        current = observations.get(period)
        if current is None:
            missing = _unavailable_compsales_semantics()
            comparable_sales_growth[period] = SOURCE_UNAVAILABLE
            comparable_sales_unit[period] = missing["comparable_sales_unit"]
            definition_text[period] = missing["definition_text"]
            period_kind[period] = missing["period_kind"]
            calendar_week_adjustment[period] = missing["calendar_week_adjustment"]
            calendar_reporting_basis[period] = missing["calendar_reporting_basis"]
            qualifiers[period] = SOURCE_UNAVAILABLE
            compsales_reasons: tuple[str, ...] = (
                () if opening else (REASON_MISSING_COMPARABLE_SALES,)
            )
        else:
            comparable_sales_growth[period] = float(current.value)
            comparable_sales_unit[period] = current.unit
            definition_text[period] = current.definition_text
            period_kind[period] = current.period_kind
            calendar_week_adjustment[period] = current.calendar_week_adjustment
            calendar_reporting_basis[period] = current.calendar_reporting_basis
            qualifiers[period] = dict(current.qualifiers)
            compsales_reasons = ()

        difference = _compsales_difference_pp(
            revenue_growth[period],
            comparable_sales_growth[period],
            opening=opening,
        )
        growth_difference_pp[period] = difference
        if is_source_unavailable(difference):
            unavailable_reasons[period] = revenue_reasons[period] + compsales_reasons
        else:
            unavailable_reasons[period] = None

    return OperatingKpiRevenueComparableSalesIdentitySeries(
        identity=identity,
        family=fields["family"],
        entity_ticker=fields["entity_ticker"],
        entity_company=fields["entity_company"],
        geography=fields["geography"],
        population=fields["population"],
        unit=fields["unit"],
        basis=fields["basis"],
        comparison=fields["comparison"],
        periods=tuple(axis),
        revenue=dict(revenue),
        comparable_sales_growth=comparable_sales_growth,
        comparable_sales_unit=comparable_sales_unit,
        definition_text=definition_text,
        period_kind=period_kind,
        calendar_week_adjustment=calendar_week_adjustment,
        calendar_reporting_basis=calendar_reporting_basis,
        qualifiers=qualifiers,
        revenue_growth=dict(revenue_growth),
        growth_difference_pp=growth_difference_pp,
        unavailable_reasons=unavailable_reasons,
    )


def compute_operating_kpi_revenue_comparable_sales_relationship(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> OperatingKpiRevenueComparableSalesRelationship:
    """Compare consolidated revenue growth with reported comparable-sales growth."""
    if not operating_kpi_revenue_comparable_sales_relationship_applicable(financials):
        raise MissingLineError(
            "operating KPI revenue/comparable-sales relationship sources not available"
        )

    validate_historical_operating_kpis(financials)
    _require_annual_axis(
        financials,
        message=(
            "operating KPI revenue/comparable-sales relationship requires "
            "annual fiscal periods"
        ),
    )
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError(
            "operating KPI revenue/comparable-sales relationship must use "
            "the canonical fiscal axis"
        )

    revenue, revenue_growth, revenue_reasons = _resolved_revenue_maps(financials, axis)
    grouped, fields_by_identity = _compsales_identity_index(
        _eligible_comparable_sales_observations(financials)
    )
    ordered = sorted(
        fields_by_identity,
        key=lambda key: tuple(
            fields_by_identity[key][field] for field in MANAGEMENT_IDENTITY_FIELDS
        ),
    )
    series = {
        identity: _compsales_identity_series(
            identity=identity,
            fields=fields_by_identity[identity],
            axis=axis,
            observations=grouped[identity],
            revenue=revenue,
            revenue_growth=revenue_growth,
            revenue_reasons=revenue_reasons,
        )
        for identity in ordered
    }
    return OperatingKpiRevenueComparableSalesRelationship(
        periods=tuple(axis),
        identities=tuple(ordered),
        currency=financials.currency,
        monetary_scale=financials.units,
        revenue_input_label=REVENUE_INPUT_LABEL,
        comparable_sales_input_label=COMPARABLE_SALES_INPUT_LABEL,
        revenue_growth_kind=REVENUE_GROWTH_KIND,
        comparable_sales_kind=COMPARABLE_SALES_KIND,
        difference_kind=DIFFERENCE_KIND,
        difference_unit=DIFFERENCE_UNIT,
        scope_note=COMPARABLE_SALES_SCOPE_NOTE,
        series=series,
    )


@dataclass(frozen=True)
class OperatingKpiRevenueSalesPerSquareFootIdentitySeries:
    """One full-identity revenue versus SPSF-growth comparison."""

    identity: str
    family: str
    entity_ticker: str
    entity_company: str
    geography: str
    population: str
    unit: str
    basis: str
    comparison: str
    periods: tuple[date, ...]
    revenue: dict[date, float | str]
    sales_per_square_foot: dict[date, float | str]
    sales_per_square_foot_unit: dict[date, str]
    definition_text: dict[date, str]
    period_kind: dict[date, str]
    calendar_week_adjustment: dict[date, str]
    calendar_reporting_basis: dict[date, str]
    qualifiers: dict[date, dict[str, str] | str]
    revenue_growth: dict[date, float | str | None]
    spsf_growth: dict[date, float | str | None]
    growth_difference_pp: dict[date, float | str | None]
    unavailable_reasons: dict[date, tuple[str, ...] | None]


@dataclass(frozen=True)
class OperatingKpiRevenueSalesPerSquareFootRelationship:
    """Descriptive revenue-growth versus SPSF-growth comparisons."""

    periods: tuple[date, ...]
    identities: tuple[str, ...]
    currency: str
    monetary_scale: str
    revenue_input_label: str
    sales_per_square_foot_input_label: str
    revenue_growth_kind: str
    sales_per_square_foot_kind: str
    difference_kind: str
    difference_unit: str
    scope_note: str
    series: dict[str, OperatingKpiRevenueSalesPerSquareFootIdentitySeries]


def _is_eligible_global_reported_spsf(
    item: HistoricalManagementKpiObservation,
) -> bool:
    return (
        item.family == FAMILY_SALES_PER_SQUARE_FOOT
        and item.geography == ELIGIBLE_SPSF_GEOGRAPHY
        and item.population == ELIGIBLE_SPSF_POPULATION
        and item.basis == ELIGIBLE_SPSF_BASIS
        and item.unit == ELIGIBLE_SPSF_UNIT
        and item.comparison == ELIGIBLE_SPSF_COMPARISON
    )


def _eligible_spsf_observations(
    financials: StandardizedFinancials,
) -> tuple[HistoricalManagementKpiObservation, ...]:
    data = financials.historical_operating_kpis
    if data is None:
        return ()
    return tuple(
        item
        for item in data.management_observations
        if _is_eligible_global_reported_spsf(item)
    )


def operating_kpi_revenue_sales_per_square_foot_relationship_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Module is present only when eligible SPSF observations exist."""
    return bool(_eligible_spsf_observations(financials))


def _spsf_unavailable_reasons(
    reasons: tuple[str, ...] | None,
) -> tuple[str, ...]:
    if not reasons:
        return ()
    mapped = {
        REASON_MISSING_OBSERVATION: REASON_MISSING_SALES_PER_SQUARE_FOOT,
        REASON_MISSING_PRIOR_OBSERVATION: REASON_MISSING_PRIOR_SALES_PER_SQUARE_FOOT,
    }
    return tuple(mapped.get(reason, reason) for reason in reasons)


def _spsf_identity_series(
    *,
    identity: str,
    management_series,
    axis: list[date],
    revenue: dict[date, float | str],
    revenue_growth: dict[date, float | str | None],
    revenue_reasons: dict[date, tuple[str, ...]],
) -> OperatingKpiRevenueSalesPerSquareFootIdentitySeries:
    growth_difference_pp: dict[date, float | str | None] = {}
    unavailable_reasons: dict[date, tuple[str, ...] | None] = {}
    for index, period in enumerate(axis):
        opening = index == 0
        spsf_growth = management_series.growth[period]
        difference = _difference_pp(
            revenue_growth[period], spsf_growth, opening=opening
        )
        growth_difference_pp[period] = difference
        if is_source_unavailable(difference):
            spsf_reasons = ()
            if not opening and is_source_unavailable(spsf_growth):
                spsf_reasons = _spsf_unavailable_reasons(
                    management_series.unavailable_reasons[period]
                )
            unavailable_reasons[period] = revenue_reasons[period] + spsf_reasons
        else:
            unavailable_reasons[period] = None
    return OperatingKpiRevenueSalesPerSquareFootIdentitySeries(
        identity=identity,
        family=management_series.family,
        entity_ticker=management_series.entity_ticker,
        entity_company=management_series.entity_company,
        geography=management_series.geography,
        population=management_series.population,
        unit=management_series.unit,
        basis=management_series.basis,
        comparison=management_series.comparison,
        periods=tuple(axis),
        revenue=dict(revenue),
        sales_per_square_foot=dict(management_series.reported_value),
        sales_per_square_foot_unit=dict(management_series.reported_unit),
        definition_text=dict(management_series.definition_text),
        period_kind=dict(management_series.period_kind),
        calendar_week_adjustment=dict(management_series.calendar_week_adjustment),
        calendar_reporting_basis=dict(management_series.calendar_reporting_basis),
        qualifiers=dict(management_series.qualifiers),
        revenue_growth=dict(revenue_growth),
        spsf_growth=dict(management_series.growth),
        growth_difference_pp=growth_difference_pp,
        unavailable_reasons=unavailable_reasons,
    )


def compute_operating_kpi_revenue_sales_per_square_foot_relationship(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> OperatingKpiRevenueSalesPerSquareFootRelationship:
    """Compare consolidated revenue growth with SPSF growth."""
    if not operating_kpi_revenue_sales_per_square_foot_relationship_applicable(
        financials
    ):
        raise MissingLineError(
            "operating KPI revenue/sales-per-square-foot relationship sources "
            "not available"
        )

    validate_historical_operating_kpis(financials)
    _require_annual_axis(
        financials,
        message=(
            "operating KPI revenue/sales-per-square-foot relationship requires "
            "annual fiscal periods"
        ),
    )
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError(
            "operating KPI revenue/sales-per-square-foot relationship must use "
            "the canonical fiscal axis"
        )

    revenue, revenue_growth, revenue_reasons = _resolved_revenue_maps(financials, axis)
    management = compute_management_kpi_series(financials, axis)
    eligible = {
        encode_metric_identity(management_identity_fields(item))
        for item in _eligible_spsf_observations(financials)
    }
    ordered = tuple(
        identity for identity in management.identities if identity in eligible
    )
    series = {
        identity: _spsf_identity_series(
            identity=identity,
            management_series=management.series[identity],
            axis=axis,
            revenue=revenue,
            revenue_growth=revenue_growth,
            revenue_reasons=revenue_reasons,
        )
        for identity in ordered
    }
    return OperatingKpiRevenueSalesPerSquareFootRelationship(
        periods=tuple(axis),
        identities=ordered,
        currency=financials.currency,
        monetary_scale=financials.units,
        revenue_input_label=REVENUE_INPUT_LABEL,
        sales_per_square_foot_input_label=SALES_PER_SQUARE_FOOT_INPUT_LABEL,
        revenue_growth_kind=REVENUE_GROWTH_KIND,
        sales_per_square_foot_kind=SALES_PER_SQUARE_FOOT_KIND,
        difference_kind=DIFFERENCE_KIND,
        difference_unit=DIFFERENCE_UNIT,
        scope_note=SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE,
        series=series,
    )
