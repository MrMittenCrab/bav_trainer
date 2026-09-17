"""Source-supported historical company-operated store-count analytical series.

Optional, source-gated module. Consumes only
``StandardizedFinancials.historical_operating_kpis`` after existing contract
validation. Missing or null payloads make the module absent. Missing
observations on an otherwise valid canonical fiscal axis yield
``SOURCE_UNAVAILABLE`` only for dependent outputs; gaps are never compressed
and another period is never substituted.

Computes period-end company-operated store counts, adjacent-period net count
change ``current - previous``, and count growth
``(current - previous) / previous``. Changes are net count changes, not gross
openings or closures. The series does not derive same-store sales,
revenue-per-store, geographic allocation, or operating causality.

Accepted ``stores`` and ``ones`` are count units independent of monetary
scale. Opening change/growth is absent. Later comparisons require both
immediately adjacent model-period observations. Zero denominators use
``UNDEFINED_RATIO``. Reported zero counts and negative net changes are
preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.historical_operating_kpis import (
    METRIC_STORE_COUNT,
    POPULATION_COMPANY_OPERATED,
    has_store_count_observations,
    validate_historical_operating_kpis,
)
from ..data.interface import HistoricalOperatingKpiObservation, StandardizedFinancials
from .line_resolver import MissingLineError
from .period_axis import canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, ratio_or_na

OPERATING_KPI_RATIO_TOLERANCE = 1e-12


@dataclass(frozen=True)
class OperatingKpiSeries:
    """Deterministic store-count analytics keyed by canonical fiscal periods."""

    periods: tuple[date, ...]
    metric: str
    population: str
    unit: dict[date, str]
    period_end_count: dict[date, float | str]
    net_count_change: dict[date, float | str | None]
    growth: dict[date, float | str | None]


def operating_kpi_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when store-count observations are supplied."""
    data = financials.historical_operating_kpis
    return data is not None and has_store_count_observations(data)


def _store_observation_index(
    financials: StandardizedFinancials,
) -> dict[date, HistoricalOperatingKpiObservation]:
    assert financials.historical_operating_kpis is not None
    return {
        item.period: item
        for item in financials.historical_operating_kpis.observations
        if item.metric == METRIC_STORE_COUNT
        and item.population == POPULATION_COMPANY_OPERATED
    }


def compute_operating_kpi_series(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> OperatingKpiSeries:
    """Compute period-end counts, adjacent net changes, and count growth."""
    if not operating_kpi_applicable(financials):
        raise MissingLineError("operating KPI sources not available")

    validate_historical_operating_kpis(financials)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError("operating KPI series must use the canonical fiscal axis")

    observations = _store_observation_index(financials)
    unit: dict[date, str] = {}
    period_end_count: dict[date, float | str] = {}
    net_count_change: dict[date, float | str | None] = {}
    growth: dict[date, float | str | None] = {}

    for index, period in enumerate(axis):
        opening = index == 0
        current = observations.get(period)
        prior = None if opening else observations.get(axis[index - 1])
        if current is None:
            unit[period] = SOURCE_UNAVAILABLE
            period_end_count[period] = SOURCE_UNAVAILABLE
            net_count_change[period] = None if opening else SOURCE_UNAVAILABLE
            growth[period] = None if opening else SOURCE_UNAVAILABLE
            continue

        count = float(current.value)
        unit[period] = current.unit
        period_end_count[period] = count
        if opening:
            net_count_change[period] = None
            growth[period] = None
        elif prior is None:
            net_count_change[period] = SOURCE_UNAVAILABLE
            growth[period] = SOURCE_UNAVAILABLE
        else:
            change = count - float(prior.value)
            net_count_change[period] = change
            growth[period] = ratio_or_na(change, float(prior.value))

    return OperatingKpiSeries(
        periods=tuple(axis),
        metric=METRIC_STORE_COUNT,
        population=POPULATION_COMPANY_OPERATED,
        unit=unit,
        period_end_count=period_end_count,
        net_count_change=net_count_change,
        growth=growth,
    )
