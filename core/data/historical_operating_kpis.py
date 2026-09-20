"""Optional historical operating-KPI contract and fail-closed validation."""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable, Mapping

from ..ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    SUPPORTED_FAMILIES,
    SUPPORTED_METRIC_MAPPINGS,
    encode_metric_identity,
)
from .filing import PresentationRole, SupplementalFact
from .interface import (
    HistoricalManagementKpiDeferredDisagreement,
    HistoricalManagementKpiDeferredMember,
    HistoricalManagementKpiObservation,
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

MANAGEMENT_IDENTITY_FIELDS = (
    "family",
    "entity_ticker",
    "entity_company",
    "geography",
    "population",
    "unit",
    "basis",
    "comparison",
)
MANAGEMENT_PERIOD_KIND_DATE = "date"
UNIT_PERCENT = "percent"
UNIT_USD_PER_SQUARE_FOOT = "USD_per_square_foot"
FAMILY_UNITS = {
    FAMILY_COMPARABLE_SALES_GROWTH: UNIT_PERCENT,
    FAMILY_SALES_PER_SQUARE_FOOT: UNIT_USD_PER_SQUARE_FOOT,
}
SUPPORTED_MANAGEMENT_IDENTITY_KEYS = frozenset(
    (
        mapping.family,
        mapping.geography,
        mapping.population,
        mapping.unit,
        mapping.basis,
        mapping.comparison,
    )
    for mapping in SUPPORTED_METRIC_MAPPINGS.values()
)
_REQUIRED_MANAGEMENT_TEXT_FIELDS = (
    "family",
    "entity_ticker",
    "entity_company",
    "population",
    "unit",
    "basis",
    "definition_text",
    "period_kind",
)
_OPTIONAL_EMPTY_MANAGEMENT_TEXT_FIELDS = (
    "geography",
    "comparison",
    "calendar_week_adjustment",
    "calendar_reporting_basis",
)
MANAGEMENT_TEXT_FIELDS = (
    *_REQUIRED_MANAGEMENT_TEXT_FIELDS,
    *_OPTIONAL_EMPTY_MANAGEMENT_TEXT_FIELDS,
)


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


def reject_non_string_reported_label(identity: str, label: object) -> None:
    """Reject non-string serialized labels before source coercion.

    ``None`` (omitted/null) is left to object-level validation.
    """
    if label is None or isinstance(label, str):
        return
    require_reported_label(identity, label)


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


def _require_management_text(
    identity: str,
    field: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"operating-KPI {identity} {field} must be a string")
    if not allow_empty and not value.strip():
        raise ValueError(f"operating-KPI {identity} missing {field}")
    return value


def require_management_observation_text_fields(
    values: Mapping[str, object],
) -> dict[str, str]:
    """Reject non-string management text before any observation construction."""
    family = values.get("family")
    identity = family if isinstance(family, str) and family.strip() else "management"
    texts: dict[str, str] = {}
    for field in _REQUIRED_MANAGEMENT_TEXT_FIELDS:
        texts[field] = _require_management_text(identity, field, values[field])
    for field in _OPTIONAL_EMPTY_MANAGEMENT_TEXT_FIELDS:
        texts[field] = _require_management_text(
            identity, field, values[field], allow_empty=True
        )
    return texts


def _require_management_number(identity: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"operating-KPI {identity} has a non-numeric value")
    amount = float(value)
    if not math.isfinite(amount):
        raise ValueError(f"operating-KPI {identity} has a non-finite value")
    return amount


def management_identity_fields(
    item: HistoricalManagementKpiObservation,
) -> dict[str, str]:
    return {
        "family": item.family,
        "entity_ticker": item.entity_ticker,
        "entity_company": item.entity_company,
        "geography": item.geography,
        "population": item.population,
        "unit": item.unit,
        "basis": item.basis,
        "comparison": item.comparison,
    }


def management_identity_key(
    item: HistoricalManagementKpiObservation,
) -> tuple[str, date]:
    return encode_metric_identity(management_identity_fields(item)), item.period


def has_store_count_observations(data: HistoricalOperatingKpiData) -> bool:
    return any(
        item.metric == METRIC_STORE_COUNT
        and item.population == POPULATION_COMPANY_OPERATED
        for item in data.observations
    )


def _validate_store_observations(
    observations: list[HistoricalOperatingKpiObservation],
    axis: set[date],
) -> None:
    seen: set[tuple[str, str, date]] = set()
    for item in observations:
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


def _validate_management_observation(
    item: HistoricalManagementKpiObservation,
    *,
    axis: set[date],
    seen: set[tuple[str, date]],
) -> None:
    if not isinstance(item, HistoricalManagementKpiObservation):
        raise ValueError(
            "historical_operating_kpis.management_observations entries must be "
            "management-KPI observations"
        )
    require_management_observation_text_fields(
        {field: getattr(item, field) for field in MANAGEMENT_TEXT_FIELDS}
    )
    if item.family not in SUPPORTED_FAMILIES:
        raise ValueError(f"unsupported management-KPI family: {item.family!r}")
    identity = item.family
    expected_unit = FAMILY_UNITS[item.family]
    if item.unit != expected_unit:
        raise ValueError(
            f"operating-KPI {identity} has unsupported unit: {item.unit!r}"
        )
    combo = (
        item.family,
        item.geography,
        item.population,
        item.unit,
        item.basis,
        item.comparison,
    )
    if combo not in SUPPORTED_MANAGEMENT_IDENTITY_KEYS:
        raise ValueError(
            f"inconsistent management-KPI identity fields for {identity}"
        )
    if item.period_kind != MANAGEMENT_PERIOD_KIND_DATE:
        raise ValueError(
            f"operating-KPI {identity} period_kind must be {MANAGEMENT_PERIOD_KIND_DATE!r}"
        )
    if not isinstance(item.period, date):
        raise ValueError("historical_operating_kpis period must be a date")
    if item.period not in axis:
        raise ValueError(
            f"operating-KPI period {item.period.isoformat()} is outside the model axis"
        )
    amount = _require_management_number(identity, item.value)
    if item.family == FAMILY_SALES_PER_SQUARE_FOOT and amount < 0:
        raise ValueError(
            f"operating-KPI {identity} must be a non-negative {UNIT_USD_PER_SQUARE_FOOT} value"
        )
    if not isinstance(item.qualifiers, dict):
        raise ValueError(f"operating-KPI {identity} qualifiers must be an object")
    for key, value in item.qualifiers.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"operating-KPI {identity} qualifier keys must be strings")
        if not isinstance(value, str):
            raise ValueError(
                f"operating-KPI {identity} qualifier {key!r} must be a string"
            )
    key = management_identity_key(item)
    if key in seen:
        raise ValueError(
            "duplicate management-KPI identity-period "
            f"{key[0]} for {item.period.isoformat()}"
        )
    seen.add(key)


def _validate_management_observations(
    observations: list[HistoricalManagementKpiObservation],
    axis: set[date],
) -> None:
    seen: set[tuple[str, date]] = set()
    for item in observations:
        _validate_management_observation(item, axis=axis, seen=seen)


def _require_deferred_text(identity: str, field: str, value: object) -> str:
    if not isinstance(value, str):
        raise ValueError(
            f"historical_operating_kpis.deferred_disagreements {identity} "
            f"{field} must be a string"
        )
    return value


def _validate_deferred_member(
    item: HistoricalManagementKpiDeferredMember,
    *,
    identity: str,
) -> None:
    if not isinstance(item, HistoricalManagementKpiDeferredMember):
        raise ValueError(
            "historical_operating_kpis.deferred_disagreements members must be "
            "deferred-disagreement members"
        )
    _require_deferred_text(identity, "locator", item.locator)
    if not item.locator.strip():
        raise ValueError(
            f"historical_operating_kpis.deferred_disagreements {identity} "
            "missing locator"
        )
    _require_deferred_text(identity, "extraction_document", item.extraction_document)
    _require_deferred_text(identity, "page_reference", item.page_reference)
    _require_deferred_text(identity, "physical_page_mapping", item.physical_page_mapping)
    _require_deferred_text(identity, "presentation_role", item.presentation_role)
    _require_deferred_text(identity, "definition_text", item.definition_text)
    _require_deferred_text(identity, "population", item.population)
    _require_deferred_text(identity, "unit", item.unit)
    _require_deferred_text(identity, "basis", item.basis)
    _require_deferred_text(
        identity, "calendar_week_adjustment", item.calendar_week_adjustment
    )
    _require_deferred_text(
        identity, "calendar_reporting_basis", item.calendar_reporting_basis
    )
    if item.reported_value is None:
        return
    if isinstance(item.reported_value, bool) or not isinstance(
        item.reported_value, (int, float)
    ):
        raise ValueError(
            f"historical_operating_kpis.deferred_disagreements {identity} "
            "reported_value must be a number or null"
        )
    if not math.isfinite(float(item.reported_value)):
        raise ValueError(
            f"historical_operating_kpis.deferred_disagreements {identity} "
            "reported_value must be finite"
        )


def _validate_deferred_disagreements(
    items: list[HistoricalManagementKpiDeferredDisagreement],
    axis: set[date],
) -> None:
    seen: set[tuple[str, date, tuple[str, ...]]] = set()
    for item in items:
        if not isinstance(item, HistoricalManagementKpiDeferredDisagreement):
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements entries must be "
                "deferred disagreements"
            )
        if item.family not in SUPPORTED_FAMILIES:
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements unsupported "
                f"family: {item.family!r}"
            )
        if not isinstance(item.period, date):
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements period must be a date"
            )
        if item.period not in axis:
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements period "
                f"{item.period.isoformat()} is outside the model axis"
            )
        if not isinstance(item.reasons, list) or not item.reasons:
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements reasons must be "
                "a nonempty list"
            )
        for reason in item.reasons:
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(
                    "historical_operating_kpis.deferred_disagreements reasons "
                    "must be nonempty strings"
                )
        if not isinstance(item.members, list) or len(item.members) < 2:
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements members must "
                "contain at least two occurrences"
            )
        identity = f"{item.family}/{item.period.isoformat()}"
        locators: list[str] = []
        for member in item.members:
            _validate_deferred_member(member, identity=identity)
            locators.append(member.locator)
        if len(set(locators)) != len(locators):
            raise ValueError(
                "historical_operating_kpis.deferred_disagreements duplicate "
                f"locator in {identity}"
            )
        key = (item.family, item.period, tuple(sorted(locators)))
        if key in seen:
            raise ValueError(
                "duplicate deferred disagreement "
                f"{item.family} for {item.period.isoformat()}"
            )
        seen.add(key)


def validate_historical_operating_kpi_data(
    data: HistoricalOperatingKpiData,
    *,
    model_periods: Iterable[date],
) -> None:
    """Reject malformed supplied KPI payloads; absence is handled by callers."""
    if not isinstance(data.observations, list):
        raise ValueError("historical_operating_kpis.observations must be a list")
    if not isinstance(data.management_observations, list):
        raise ValueError(
            "historical_operating_kpis.management_observations must be a list"
        )
    if not isinstance(data.deferred_disagreements, list):
        raise ValueError(
            "historical_operating_kpis.deferred_disagreements must be a list"
        )
    if not data.observations and not data.management_observations:
        raise ValueError(
            "historical_operating_kpis must contain at least one observation"
        )
    axis = set(model_periods)
    _validate_store_observations(data.observations, axis)
    _validate_management_observations(data.management_observations, axis)
    _validate_deferred_disagreements(data.deferred_disagreements, axis)


def validate_historical_operating_kpis(fin: StandardizedFinancials) -> None:
    """Validate a supplied operating-KPI payload against the parent financials."""
    if fin.historical_operating_kpis is None:
        return
    validate_historical_operating_kpi_data(
        fin.historical_operating_kpis,
        model_periods=fin.period_dates(),
    )
