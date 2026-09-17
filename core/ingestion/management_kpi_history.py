"""Transfer evidenced selected management KPIs into model-facing histories."""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from ..data.historical_operating_kpis import (
    MANAGEMENT_IDENTITY_FIELDS,
    validate_historical_operating_kpi_data,
)
from ..data.interface import (
    HistoricalManagementKpiObservation,
    HistoricalOperatingKpiData,
)
from .management_kpi_identity import assess_reported_observations
from .management_kpi_reconciliation import (
    SELECTION_SELECTED,
    reconcile_group_selections,
    reconcile_revision_links,
)


def derive_evidenced_group_selections(admission: Any) -> tuple[Any, ...]:
    """Recompute complete-group selections from bound documents and observations."""
    assessments = assess_reported_observations(
        admission.observations, admission.documents
    )
    revision_links = reconcile_revision_links(admission.observations, assessments)
    return reconcile_group_selections(
        admission.observations, assessments, revision_links
    )


def selected_management_kpi_histories(
    admission: Any | None,
    *,
    model_periods: Iterable[date],
) -> list[HistoricalManagementKpiObservation]:
    """Return unique evidenced selected occurrences on the admitted model axis."""
    if admission is None:
        return []
    axis = tuple(model_periods)
    derived = derive_evidenced_group_selections(admission)
    _require_cached_selections_match(admission, derived)
    observations_by_locator = {item.locator: item for item in admission.observations}
    transferred: list[HistoricalManagementKpiObservation] = []
    seen: set[tuple[str, date]] = set()
    for group in derived:
        if group.status != SELECTION_SELECTED:
            continue
        item = _history_from_selected_group(
            group,
            observations_by_locator=observations_by_locator,
            axis=set(axis),
        )
        key = (group.metric_identity, item.period)
        if key in seen:
            raise ValueError(
                "duplicate management-KPI identity-period "
                f"{group.metric_identity} for {item.period.isoformat()}"
            )
        seen.add(key)
        transferred.append(item)
    if transferred:
        validate_historical_operating_kpi_data(
            HistoricalOperatingKpiData(management_observations=list(transferred)),
            model_periods=axis,
        )
    transferred.sort(
        key=lambda row: tuple(getattr(row, field) for field in MANAGEMENT_IDENTITY_FIELDS)
        + (row.period.isoformat(),)
    )
    return transferred


def _require_cached_selections_match(admission: Any, derived: tuple[Any, ...]) -> None:
    cached = tuple(getattr(admission, "group_selections", ()) or ())
    if _selection_payloads(cached) != _selection_payloads(derived):
        raise ValueError("stale or inconsistent management-KPI group selections")


def _selection_payloads(items: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(item.to_payload() for item in items)


def _history_from_selected_group(
    group: Any,
    *,
    observations_by_locator: dict[str, Any],
    axis: set[date],
) -> HistoricalManagementKpiObservation:
    locators = [item.locator for item in group.occurrences]
    if len(locators) != len(set(locators)):
        raise ValueError("duplicate management-KPI locators in selected group")
    if group.selected is None:
        raise ValueError("missing management-KPI selected occurrence")
    selected_locator = group.selected.locator
    if selected_locator not in locators:
        raise ValueError("incomplete management-KPI group membership")
    by_locator = {item.locator: item for item in group.occurrences}
    selected_occ = by_locator[selected_locator]
    source = observations_by_locator.get(selected_locator)
    if source is None:
        raise ValueError("missing management-KPI selected occurrence")
    if selected_occ.occurrence_identity != group.selected.occurrence_identity:
        raise ValueError("mismatched management-KPI selected identity")
    if selected_occ.period != group.period:
        raise ValueError("mismatched management-KPI selected period")
    if source.period != group.period or source.identity != group.selected.occurrence_identity:
        raise ValueError("mismatched management-KPI selected identity")
    if source.value != selected_occ.value:
        raise ValueError("mismatched management-KPI selected value")
    if selected_occ.value is None:
        raise ValueError("mismatched management-KPI selected value")
    period = _require_axis_date(group.period, axis=axis)
    fields = dict(group.metric_identity_fields)
    missing = [field for field in MANAGEMENT_IDENTITY_FIELDS if field not in fields]
    if missing:
        raise ValueError(
            "missing required management-KPI semantics: " + ", ".join(missing)
        )
    evidence = dict(selected_occ.evidence)
    return HistoricalManagementKpiObservation(
        family=str(fields["family"]),
        entity_ticker=str(fields["entity_ticker"]),
        entity_company=str(fields["entity_company"]),
        geography=str(fields.get("geography", "")),
        population=str(fields["population"]),
        unit=str(fields["unit"]),
        basis=str(fields["basis"]),
        comparison=str(fields.get("comparison", "")),
        period=period,
        value=float(selected_occ.value),
        definition_text=selected_occ.definition_text,
        period_kind=selected_occ.period_kind,
        calendar_week_adjustment=str(evidence.get("calendar_week_adjustment", "")),
        calendar_reporting_basis=str(evidence.get("calendar_reporting_basis", "")),
        qualifiers=dict(source.qualifiers),
    )


def _require_axis_date(value: str, *, axis: set[date]) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(f"operating-KPI period {value!r} is outside the model axis")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"operating-KPI period {value!r} is outside the model axis"
        ) from exc
    if parsed.isoformat() != value:
        raise ValueError(f"operating-KPI period {value!r} is outside the model axis")
    if parsed not in axis:
        raise ValueError(
            f"operating-KPI period {parsed.isoformat()} is outside the model axis"
        )
    return parsed
