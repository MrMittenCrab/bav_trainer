"""Optional historical operating-KPI contract and fail-closed validation."""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable

from .filing import PresentationRole, SupplementalFact
from .interface import (
    HistoricalOperatingKpiData,
    HistoricalOperatingKpiObservation,
    StandardizedFinancials,
)

KPI_NAMESPACE = "kpi.operating"
KPI_PREFIX = KPI_NAMESPACE + "."
METRIC_STORE_COUNT = "store_count"
POPULATION_COMPANY_OPERATED = "company_operated"
STORE_COUNT_FACT_TYPE = (
    f"{KPI_NAMESPACE}.{METRIC_STORE_COUNT}.{POPULATION_COMPANY_OPERATED}"
)
ALLOWED_METRICS = frozenset({METRIC_STORE_COUNT})
ALLOWED_POPULATIONS = frozenset({POPULATION_COMPANY_OPERATED})
ALLOWED_UNITS = frozenset({"stores", "ones"})
ALLOWED_FACT_TYPES = frozenset({STORE_COUNT_FACT_TYPE})
_VALID_ROLES = {role.value for role in PresentationRole}


def is_operating_kpi_fact_type(fact_type: str) -> bool:
    return fact_type.startswith(KPI_PREFIX)


def split_operating_kpi_identity(fact_type: str) -> tuple[str, str]:
    """Return (metric, population) for a supported operating-KPI fact_type."""
    if not is_operating_kpi_fact_type(fact_type):
        raise ValueError(f"not an operating-KPI fact_type: {fact_type!r}")
    if fact_type not in ALLOWED_FACT_TYPES:
        raise ValueError(f"unknown {KPI_NAMESPACE} identity: {fact_type!r}")
    remainder = fact_type[len(KPI_PREFIX) :]
    metric, separator, population = remainder.partition(".")
    if not separator or metric not in ALLOWED_METRICS:
        raise ValueError(f"unknown {KPI_NAMESPACE} identity: {fact_type!r}")
    if population not in ALLOWED_POPULATIONS:
        raise ValueError(f"unknown {KPI_NAMESPACE} identity: {fact_type!r}")
    return metric, population


def require_count_value(identity: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"operating-KPI {identity} has a non-numeric value")
    amount = float(value)
    if not math.isfinite(amount):
        raise ValueError(f"operating-KPI {identity} has a non-finite value")
    if amount < 0 or not amount.is_integer():
        raise ValueError(
            f"operating-KPI {identity} must be a non-negative integer count"
        )
    return amount


def require_kpi_unit(identity: str, unit: object) -> str:
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError(f"operating-KPI {identity} missing an explicit unit")
    normalized = unit.strip()
    if normalized not in ALLOWED_UNITS:
        raise ValueError(
            f"operating-KPI {identity} has unsupported unit: {unit!r}"
        )
    return normalized


def require_reported_label(identity: str, label: object) -> str:
    """Require a reported source label; note text is not a substitute."""
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"operating-KPI {identity} missing reported label")
    return label


def validate_operating_kpi_fact(fact: SupplementalFact) -> tuple[str, str]:
    """Reject malformed store-KPI supplemental facts; return metric, population."""
    metric, population = split_operating_kpi_identity(fact.fact_type)
    identity = fact.fact_type
    if fact.status != "reported":
        raise ValueError(f"operating-KPI {identity} must have status=reported")
    if fact.source.page <= 0:
        raise ValueError(f"operating-KPI {identity} missing positive source page")
    require_reported_label(identity, fact.source.label)
    if fact.presentation_role not in _VALID_ROLES:
        raise ValueError(
            f"operating-KPI {identity} missing valid presentation_role"
        )
    require_count_value(identity, fact.value)
    require_kpi_unit(identity, fact.unit)
    return metric, population


def validate_historical_operating_kpi_data(
    data: HistoricalOperatingKpiData,
    *,
    model_periods: Iterable[date],
) -> None:
    """Reject malformed supplied KPI payloads; absence is handled by callers."""
    if not isinstance(data.observations, list) or not data.observations:
        raise ValueError("historical_operating_kpis.observations must be a non-empty list")
    axis = set(model_periods)
    seen: set[tuple[str, str, date]] = set()
    for item in data.observations:
        if not isinstance(item, HistoricalOperatingKpiObservation):
            raise ValueError(
                "historical_operating_kpis.observations entries must be KPI observations"
            )
        if item.metric not in ALLOWED_METRICS:
            raise ValueError(f"unknown {KPI_NAMESPACE} metric: {item.metric!r}")
        if item.population not in ALLOWED_POPULATIONS:
            raise ValueError(
                f"unknown {KPI_NAMESPACE} population: {item.population!r}"
            )
        if not isinstance(item.period, date):
            raise ValueError("historical_operating_kpis period must be a date")
        if item.period not in axis:
            raise ValueError(
                f"operating-KPI period {item.period.isoformat()} is outside the model axis"
            )
        key = (item.metric, item.population, item.period)
        if key in seen:
            raise ValueError(
                "duplicate operating-KPI identity "
                f"{item.metric}/{item.population} for {item.period.isoformat()}"
            )
        seen.add(key)
        identity = f"{KPI_NAMESPACE}.{item.metric}.{item.population}"
        require_count_value(identity, item.value)
        require_kpi_unit(identity, item.unit)


def validate_historical_operating_kpis(fin: StandardizedFinancials) -> None:
    """Validate a supplied operating-KPI payload against the parent financials."""
    if fin.historical_operating_kpis is None:
        return
    validate_historical_operating_kpi_data(
        fin.historical_operating_kpis,
        model_periods=fin.period_dates(),
    )
