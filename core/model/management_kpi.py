"""Source-supported historical management-KPI analytical series.

Optional, source-gated module. Consumes only validated
``StandardizedFinancials.historical_operating_kpis.management_observations``.
Absent, null, or store-only payloads make the module absent. The store-count
applicability and series API are unchanged.

Computes identity-specific reported histories aligned to the canonical fiscal
axis. Adjacent-period comparisons require immediately adjacent canonical
periods with the same full identity and exactly matching definition text,
period kind, calendar week adjustment, reporting basis, and qualifier
mappings. Differences are not normalized and equivalence is not inferred.

Comparable-sales growth retains signed reported percentages and computes
adjacent percentage-point change as current minus prior; growth of a growth
rate is not computed. Sales per square foot retains reported
``USD_per_square_foot``, adjacent absolute change, and fractional growth
``(current - previous) / previous``. Zero priors use ``UNDEFINED_RATIO``.
No financial-statement monetary scaling is applied.

Reported values are retained across gaps and semantic discontinuities.
Dependent comparisons are ``SOURCE_UNAVAILABLE`` with explicit reasons that
distinguish missing observations from semantic changes. Opening comparisons
are ``None``. Gaps are never compressed, carried forward, or substituted.
Source and audit evidence remain outside model-facing outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.historical_operating_kpis import (
    FAMILY_SALES_PER_SQUARE_FOOT,
    MANAGEMENT_IDENTITY_FIELDS,
    encode_metric_identity,
    management_identity_fields,
    validate_historical_operating_kpis,
)
from ..data.interface import HistoricalManagementKpiObservation, StandardizedFinancials
from .line_resolver import MissingLineError
from .period_axis import canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, ratio_or_na

MANAGEMENT_KPI_RATIO_TOLERANCE = 1e-12
REASON_MISSING_OBSERVATION = "missing_observation"
REASON_MISSING_PRIOR_OBSERVATION = "missing_prior_observation"
REASON_DEFINITION_MISMATCH = "definition_mismatch"
REASON_PERIOD_KIND_MISMATCH = "period_kind_mismatch"
REASON_CALENDAR_WEEK_MISMATCH = "calendar_week_adjustment"
REASON_CALENDAR_REPORTING_MISMATCH = "calendar_reporting_basis"
REASON_QUALIFIER_MISMATCH = "qualifier_mismatch"

_SEMANTIC_GATES = (
    ("definition_text", REASON_DEFINITION_MISMATCH),
    ("period_kind", REASON_PERIOD_KIND_MISMATCH),
    ("calendar_week_adjustment", REASON_CALENDAR_WEEK_MISMATCH),
    ("calendar_reporting_basis", REASON_CALENDAR_REPORTING_MISMATCH),
)


@dataclass(frozen=True)
class ManagementKpiIdentitySeries:
    """One full-identity reported history and adjacent-period analytics."""

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
    reported_value: dict[date, float | str]
    reported_unit: dict[date, str]
    definition_text: dict[date, str]
    period_kind: dict[date, str]
    calendar_week_adjustment: dict[date, str]
    calendar_reporting_basis: dict[date, str]
    qualifiers: dict[date, dict[str, str] | str]
    adjacent_change: dict[date, float | str | None]
    growth: dict[date, float | str | None]
    unavailable_reasons: dict[date, tuple[str, ...] | None]


@dataclass(frozen=True)
class ManagementKpiSeries:
    """Deterministic management-KPI analytics keyed by full identity."""

    periods: tuple[date, ...]
    identities: tuple[str, ...]
    series: dict[str, ManagementKpiIdentitySeries]


def management_kpi_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when management-KPI observations are supplied."""
    data = financials.historical_operating_kpis
    return data is not None and bool(data.management_observations)


def _identity_index(
    financials: StandardizedFinancials,
) -> tuple[
    dict[str, dict[date, HistoricalManagementKpiObservation]],
    dict[str, dict[str, str]],
]:
    assert financials.historical_operating_kpis is not None
    grouped: dict[str, dict[date, HistoricalManagementKpiObservation]] = {}
    fields_by_identity: dict[str, dict[str, str]] = {}
    for item in financials.historical_operating_kpis.management_observations:
        fields = management_identity_fields(item)
        identity = encode_metric_identity(fields)
        fields_by_identity.setdefault(identity, dict(fields))
        grouped.setdefault(identity, {})[item.period] = item
    return grouped, fields_by_identity


def _comparison_reasons(
    current: HistoricalManagementKpiObservation,
    prior: HistoricalManagementKpiObservation,
) -> tuple[str, ...]:
    reasons: list[str] = []
    for field, reason in _SEMANTIC_GATES:
        if getattr(current, field) != getattr(prior, field):
            reasons.append(reason)
    if dict(current.qualifiers) != dict(prior.qualifiers):
        reasons.append(REASON_QUALIFIER_MISMATCH)
    return tuple(reasons)


def _unavailable_semantics() -> dict[str, str]:
    return {
        "reported_unit": SOURCE_UNAVAILABLE,
        "definition_text": SOURCE_UNAVAILABLE,
        "period_kind": SOURCE_UNAVAILABLE,
        "calendar_week_adjustment": SOURCE_UNAVAILABLE,
        "calendar_reporting_basis": SOURCE_UNAVAILABLE,
    }


def _identity_series(
    *,
    identity: str,
    fields: dict[str, str],
    axis: list[date],
    observations: dict[date, HistoricalManagementKpiObservation],
) -> ManagementKpiIdentitySeries:
    family = fields["family"]
    compute_growth = family == FAMILY_SALES_PER_SQUARE_FOOT
    reported_value: dict[date, float | str] = {}
    reported_unit: dict[date, str] = {}
    definition_text: dict[date, str] = {}
    period_kind: dict[date, str] = {}
    calendar_week_adjustment: dict[date, str] = {}
    calendar_reporting_basis: dict[date, str] = {}
    qualifiers: dict[date, dict[str, str] | str] = {}
    adjacent_change: dict[date, float | str | None] = {}
    growth: dict[date, float | str | None] = {}
    unavailable_reasons: dict[date, tuple[str, ...] | None] = {}

    for index, period in enumerate(axis):
        opening = index == 0
        current = observations.get(period)
        prior = None if opening else observations.get(axis[index - 1])
        if current is None:
            missing = _unavailable_semantics()
            reported_value[period] = SOURCE_UNAVAILABLE
            reported_unit[period] = missing["reported_unit"]
            definition_text[period] = missing["definition_text"]
            period_kind[period] = missing["period_kind"]
            calendar_week_adjustment[period] = missing["calendar_week_adjustment"]
            calendar_reporting_basis[period] = missing["calendar_reporting_basis"]
            qualifiers[period] = SOURCE_UNAVAILABLE
            if opening:
                adjacent_change[period] = None
                growth[period] = None
                unavailable_reasons[period] = None
            else:
                adjacent_change[period] = SOURCE_UNAVAILABLE
                growth[period] = None if not compute_growth else SOURCE_UNAVAILABLE
                unavailable_reasons[period] = (REASON_MISSING_OBSERVATION,)
            continue

        value = float(current.value)
        reported_value[period] = value
        reported_unit[period] = current.unit
        definition_text[period] = current.definition_text
        period_kind[period] = current.period_kind
        calendar_week_adjustment[period] = current.calendar_week_adjustment
        calendar_reporting_basis[period] = current.calendar_reporting_basis
        qualifiers[period] = dict(current.qualifiers)
        if opening:
            adjacent_change[period] = None
            growth[period] = None
            unavailable_reasons[period] = None
            continue
        if prior is None:
            adjacent_change[period] = SOURCE_UNAVAILABLE
            growth[period] = None if not compute_growth else SOURCE_UNAVAILABLE
            unavailable_reasons[period] = (REASON_MISSING_PRIOR_OBSERVATION,)
            continue
        reasons = _comparison_reasons(current, prior)
        if reasons:
            adjacent_change[period] = SOURCE_UNAVAILABLE
            growth[period] = None if not compute_growth else SOURCE_UNAVAILABLE
            unavailable_reasons[period] = reasons
            continue
        change = value - float(prior.value)
        adjacent_change[period] = change
        unavailable_reasons[period] = None
        if compute_growth:
            growth[period] = ratio_or_na(change, float(prior.value))
        else:
            growth[period] = None

    return ManagementKpiIdentitySeries(
        identity=identity,
        family=family,
        entity_ticker=fields["entity_ticker"],
        entity_company=fields["entity_company"],
        geography=fields["geography"],
        population=fields["population"],
        unit=fields["unit"],
        basis=fields["basis"],
        comparison=fields["comparison"],
        periods=tuple(axis),
        reported_value=reported_value,
        reported_unit=reported_unit,
        definition_text=definition_text,
        period_kind=period_kind,
        calendar_week_adjustment=calendar_week_adjustment,
        calendar_reporting_basis=calendar_reporting_basis,
        qualifiers=qualifiers,
        adjacent_change=adjacent_change,
        growth=growth,
        unavailable_reasons=unavailable_reasons,
    )


def compute_management_kpi_series(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> ManagementKpiSeries:
    """Compute identity-specific reported series and adjacent-period changes."""
    if not management_kpi_applicable(financials):
        raise MissingLineError("management KPI sources not available")

    validate_historical_operating_kpis(financials)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError("management KPI series must use the canonical fiscal axis")

    grouped, fields_by_identity = _identity_index(financials)
    ordered = sorted(
        fields_by_identity,
        key=lambda key: tuple(
            fields_by_identity[key][field] for field in MANAGEMENT_IDENTITY_FIELDS
        ),
    )
    series = {
        identity: _identity_series(
            identity=identity,
            fields=fields_by_identity[identity],
            axis=axis,
            observations=grouped[identity],
        )
        for identity in ordered
    }
    return ManagementKpiSeries(
        periods=tuple(axis),
        identities=tuple(ordered),
        series=series,
    )
