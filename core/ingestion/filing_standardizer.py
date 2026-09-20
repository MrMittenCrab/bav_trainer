"""Convert reconciled documentary facts into model-only StandardizedFinancials."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from ..data.filing import PresentationRole
from ..data.historical_operating_kpis import validate_historical_operating_kpis
from ..data.historical_segments import (
    GEOGRAPHIC_SEGMENT_NAMESPACE,
    expected_bridge_operations,
    geographic_identity,
    require_finite_number,
    validate_historical_segment,
)
from ..data.interface import (
    FinancialPeriod,
    HistoricalLeaseData,
    HistoricalOperatingKpiData,
    HistoricalOperatingKpiObservation,
    HistoricalSegmentData,
    HistoricalSegmentPeriod,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
)
from ..data.issuer_fiscal import (
    issuer_fiscal_label,
    issuer_fiscal_years_from_reconciled,
)
from .filing_reconciler import (
    ReconciledCompanyData,
    ReconciledValue,
    SupplementalConflict,
    SupplementalObservation,
)

_UNIT_SCALE_LABEL = {
    "ones": "Ones",
    "thousands": "Thousands",
    "millions": "Millions",
    "billions": "Billions",
}


def _units_string(currency: str, unit_scale: str) -> str:
    scale = _UNIT_SCALE_LABEL.get(unit_scale, unit_scale.title())
    return f"{currency} in {scale}"


def _group_by_row(
    reconciled: ReconciledCompanyData,
) -> dict[tuple[str, str], list[ReconciledValue]]:
    grouped: dict[tuple[str, str], list[ReconciledValue]] = defaultdict(list)
    for value in reconciled.values:
        if value.period not in reconciled.periods:
            continue
        grouped[(value.statement, value.row_identity)].append(value)
    return grouped


def _selection_rule(value: ReconciledValue) -> str:
    distinct = {obs.value for obs in value.observations}
    if len(distinct) <= 1:
        return "agreeing_observations"
    if value.selected.presentation_role == PresentationRole.RESTATED_COMPARATIVE:
        return "restated_comparative_precedence"
    return "later_audited_presentation"


def _num(value: float) -> int | float:
    return int(value) if float(value).is_integer() else float(value)


def _observation_payload(obs) -> dict[str, Any]:
    return {
        "filing_year": obs.filing_year,
        "source_file": obs.source_file,
        "source_sha256": obs.source_sha256,
        "pdf_page": obs.pdf_page,
        "presentation_role": obs.presentation_role.value,
        "value": _num(obs.value),
    }


def _source_payload(obs: SupplementalObservation) -> dict[str, Any]:
    src = obs.fact.source
    out: dict[str, Any] = {"page": src.page}
    if src.statement:
        out["statement"] = src.statement
    if src.note:
        out["note"] = src.note
    if src.label:
        out["label"] = src.label
    return out


def _supplemental_observation_payload(obs: SupplementalObservation) -> dict[str, Any]:
    out: dict[str, Any] = {
        "filing_year": obs.filing_year,
        "source_file": obs.source_file,
        "source_sha256": obs.source_sha256,
        "fact_type": obs.fact.fact_type,
        "period": obs.fact.period.isoformat(),
        "value": _num(obs.fact.value),
        "status": obs.fact.status,
        "source": _source_payload(obs),
    }
    if obs.fact.derivation:
        out["derivation"] = obs.fact.derivation
    if obs.fact.presentation_role:
        out["presentation_role"] = obs.fact.presentation_role
    if obs.fact.unit:
        out["unit"] = obs.fact.unit
    return out


def _latest_available_row(
    by_period: dict[date, ReconciledValue],
    model_periods: list[date],
) -> ReconciledValue:
    """Label/concept come from the latest model-period observation that exists."""
    for period in reversed(model_periods):
        row = by_period.get(period)
        if row is not None:
            return row
    raise ValueError("row has no observations on the model axis")


def _line_values_for_axis(
    by_period: dict[date, ReconciledValue],
    model_periods: list[date],
    *,
    allow_sparse: bool,
) -> dict[date, float | None] | None:
    """Build axis values; sparse BS rows use explicit None for unreported periods."""
    if set(by_period) == set(model_periods):
        return {
            period: float(by_period[period].selected.value) for period in model_periods
        }
    if not allow_sparse:
        return None
    if not by_period:
        return None
    return {
        period: (
            float(by_period[period].selected.value)
            if period in by_period
            else None
        )
        for period in model_periods
    }


def _issuer_period_label(period: date, mapping: dict[date, int]) -> str:
    if period in mapping:
        return issuer_fiscal_label(mapping[period])
    if mapping:
        raise ValueError(
            f"issuer fiscal-year mapping missing period-end {period.isoformat()}"
        )
    return f"FY{period.year}"


def standardize_reconciled(
    reconciled: ReconciledCompanyData,
) -> StandardizedFinancials:
    """Emit model-only StandardizedFinancials from reconciled documentary facts."""
    model_periods = list(reconciled.periods)
    mapping = issuer_fiscal_years_from_reconciled(reconciled)
    grouped = _group_by_row(reconciled)

    statements: dict[str, list[LineItem]] = {
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
    }

    for (statement, _ident), rows in sorted(grouped.items(), key=lambda item: item[0]):
        by_period = {row.period: row for row in rows}
        values = _line_values_for_axis(
            by_period,
            model_periods,
            allow_sparse=(statement == "balance_sheet"),
        )
        if values is None:
            continue
        latest = _latest_available_row(by_period, model_periods)
        statements[statement].append(
            LineItem(
                label=latest.label,
                concept=latest.suggested_concept,
                values=values,
            )
        )

    historical_shares = _historical_shares(reconciled)
    historical_lease = _historical_lease(reconciled)
    historical_segment = _historical_segment(reconciled)
    historical_operating_kpis = _historical_operating_kpis(reconciled)

    fin = StandardizedFinancials(
        ticker=reconciled.ticker,
        company_name=reconciled.company_name,
        currency=reconciled.currency,
        units=_units_string(reconciled.currency, reconciled.unit_scale),
        jurisdiction=reconciled.jurisdiction,
        stock_code=reconciled.stock_code,
        periods=[
            FinancialPeriod(end_date=period, label=_issuer_period_label(period, mapping))
            for period in model_periods
        ],
        income_statement=statements["income_statement"],
        balance_sheet=statements["balance_sheet"],
        cash_flow=statements["cash_flow"],
        historical_shares=historical_shares,
        historical_lease=historical_lease,
        historical_segment=historical_segment,
        historical_operating_kpis=historical_operating_kpis,
    )
    validate_historical_segment(fin)
    validate_historical_operating_kpis(fin)
    return fin


def _historical_shares(
    reconciled: ReconciledCompanyData,
) -> HistoricalShareData | None:
    """Emit comparable diluted WAS in financial-statement units when resolvable."""
    from .share_basis import resolve_historical_share_basis, unit_scale_divisor

    resolution = resolve_historical_share_basis(reconciled)
    if resolution is None:
        return None
    divisor = unit_scale_divisor(reconciled.unit_scale)
    return HistoricalShareData(
        scale_basis="financial_statement_units",
        diluted_weighted_average={
            period: actual / divisor
            for period, actual in resolution.diluted_weighted_average_actual_shares.items()
        },
        basis=resolution.basis,
        adjustment_factors=dict(resolution.applied_adjustment_factors),
    )


def _historical_lease(
    reconciled: ReconciledCompanyData,
) -> HistoricalLeaseData | None:
    """Emit lease interest only for a complete unambiguous reported note axis."""
    period_set = set(reconciled.periods)
    series: dict[date, float] = {}
    for period in reconciled.periods:
        observations = [
            obs
            for obs in reconciled.note_facts
            if obs.kind == "note"
            and obs.fact.status == "reported"
            and obs.fact.fact_type == "lease_interest_expense"
            and obs.fact.period == period
        ]
        if not observations:
            return None
        distinct = {float(obs.fact.value) for obs in observations}
        if len(distinct) != 1:
            return None
        series[period] = next(iter(distinct))
    if set(series) != period_set:
        return None
    return HistoricalLeaseData(
        lease_interest_expense={period: series[period] for period in reconciled.periods},
    )


def _snapshot_from_selected(period: date, items: list) -> HistoricalSegmentPeriod:
    families = {item.presentation_family for item in items}
    if len(families) != 1:
        raise ValueError(
            "mixed geographic presentation families for "
            f"{period.isoformat()}"
        )
    family = next(iter(families))
    values: dict[str, float] = {}
    for item in items:
        identity = geographic_identity(item.fact_type)
        amount = require_finite_number(identity, item.value)
        if identity in values:
            if values[identity] != amount:
                raise ValueError(
                    "duplicate conflicting geographic identity "
                    f"{identity} for {period.isoformat()}"
                )
            raise ValueError(
                f"duplicate geographic identity {identity} for {period.isoformat()}"
            )
        values[identity] = amount
    return HistoricalSegmentPeriod(
        period=period,
        presentation_family=family,
        values=values,
        bridge_operations=expected_bridge_operations(family, values),
    )


def _historical_segment(
    reconciled: ReconciledCompanyData,
) -> HistoricalSegmentData | None:
    """Emit selected geographic facts on the admitted model axis only."""
    model_periods = set(reconciled.periods)
    grouped: dict[date, list] = defaultdict(list)
    for item in reconciled.selected_geographic_facts:
        if item.period in model_periods:
            grouped[item.period].append(item)
    if not grouped:
        return None
    snapshots = [
        _snapshot_from_selected(period, grouped[period])
        for period in reconciled.periods
        if period in grouped
    ]
    return HistoricalSegmentData(
        namespace=GEOGRAPHIC_SEGMENT_NAMESPACE,
        periods=snapshots,
    )


def _historical_operating_kpis(
    reconciled: ReconciledCompanyData,
) -> HistoricalOperatingKpiData | None:
    """Emit selected store facts and evidenced management histories on the axis."""
    from .management_kpi_history import (
        deferred_management_kpi_disagreements,
        selected_management_kpi_histories,
    )

    model_periods = set(reconciled.periods)
    observations: list[HistoricalOperatingKpiObservation] = []
    seen: set[tuple[str, str, date]] = set()
    for item in reconciled.selected_operating_kpi_facts:
        if item.period not in model_periods:
            continue
        key = (item.metric, item.population, item.period)
        if key in seen:
            raise ValueError(
                "duplicate operating-KPI identity "
                f"{item.metric}/{item.population} for {item.period.isoformat()}"
            )
        seen.add(key)
        observations.append(
            HistoricalOperatingKpiObservation(
                metric=item.metric,
                population=item.population,
                period=item.period,
                value=float(item.value),
                unit=item.unit,
            )
        )
    management = selected_management_kpi_histories(
        reconciled.management_admission,
        model_periods=reconciled.periods,
    )
    deferred = deferred_management_kpi_disagreements(
        reconciled.management_admission,
        model_periods=reconciled.periods,
    )
    if not observations and not management:
        return None
    observations.sort(key=lambda row: (row.metric, row.population, row.period.isoformat()))
    return HistoricalOperatingKpiData(
        observations=observations,
        management_observations=management,
        deferred_disagreements=deferred,
    )


def reconciliation_provenance_payload(
    reconciled: ReconciledCompanyData,
) -> dict[str, Any]:
    """Deterministic provenance artifact for reconciled documentary facts."""
    model_periods = list(reconciled.periods)
    period_set = set(model_periods)
    grouped = _group_by_row(reconciled)

    values: dict[str, Any] = {}
    omitted: list[dict[str, Any]] = []
    retained_sparse: list[dict[str, Any]] = []

    for (statement, ident), rows in sorted(grouped.items(), key=lambda item: item[0]):
        by_period = {row.period: row for row in rows}
        available = sorted(by_period)
        latest = (
            _latest_available_row(by_period, model_periods)
            if by_period
            else rows[-1]
        )
        label = latest.label
        concept = latest.suggested_concept
        incomplete = set(by_period) != period_set
        retain_sparse = incomplete and statement == "balance_sheet" and bool(by_period)

        if incomplete and not retain_sparse:
            omitted.append(
                {
                    "statement": statement,
                    "row_identity": ident,
                    "label": label,
                    "suggested_concept": concept,
                    "available_periods": [p.isoformat() for p in available],
                    "status": "omitted_incomplete_axis",
                }
            )
            # Still record available period selections for auditability
            for period, row in sorted(by_period.items()):
                key = f"{statement}|{ident}|{period.isoformat()}"
                values[key] = {
                    "statement": statement,
                    "row_identity": ident,
                    "period": period.isoformat(),
                    "label": row.label,
                    "suggested_concept": row.suggested_concept,
                    "selected": _observation_payload(row.selected),
                    "observations": [_observation_payload(o) for o in row.observations],
                    "selection_rule": _selection_rule(row),
                    "status": "omitted_incomplete_axis",
                }
            continue

        if retain_sparse:
            missing = [p for p in model_periods if p not in by_period]
            retained_sparse.append(
                {
                    "statement": statement,
                    "row_identity": ident,
                    "label": label,
                    "suggested_concept": concept,
                    "available_periods": [p.isoformat() for p in available],
                    "missing_periods": [p.isoformat() for p in missing],
                    "status": "retained_sparse_axis",
                }
            )

        for period in model_periods:
            key = f"{statement}|{ident}|{period.isoformat()}"
            if period in by_period:
                row = by_period[period]
                values[key] = {
                    "statement": statement,
                    "row_identity": ident,
                    "period": period.isoformat(),
                    "label": row.label,
                    "suggested_concept": row.suggested_concept,
                    "selected": _observation_payload(row.selected),
                    "observations": [_observation_payload(o) for o in row.observations],
                    "selection_rule": _selection_rule(row),
                    "status": "selected",
                }
            elif retain_sparse:
                values[key] = {
                    "statement": statement,
                    "row_identity": ident,
                    "period": period.isoformat(),
                    "label": label,
                    "suggested_concept": concept,
                    "selected": None,
                    "observations": [],
                    "selection_rule": None,
                    "status": "missing_period",
                }

    # Also retain observations for non-model periods (e.g. FY2020 comparatives)
    for value in reconciled.values:
        if value.period in period_set:
            continue
        key = f"{value.statement}|{value.row_identity}|{value.period.isoformat()}"
        values[key] = {
            "statement": value.statement,
            "row_identity": value.row_identity,
            "period": value.period.isoformat(),
            "label": value.label,
            "suggested_concept": value.suggested_concept,
            "selected": _observation_payload(value.selected),
            "observations": [_observation_payload(o) for o in value.observations],
            "selection_rule": _selection_rule(value),
            "status": "outside_model_axis",
        }

    payload = {
        "company_name": reconciled.company_name,
        "ticker": reconciled.ticker,
        "stock_code": reconciled.stock_code,
        "jurisdiction": reconciled.jurisdiction,
        "currency": reconciled.currency,
        "unit_scale": reconciled.unit_scale,
        "periods": [p.isoformat() for p in model_periods],
        "source_files": [
            {
                "filing_year": bound.filing_year,
                "source_file": bound.source_file,
                "source_sha256": bound.source_sha256,
            }
            for bound in reconciled.source_files
        ],
        "values": values,
        "omitted_incomplete_axis": omitted,
        "retained_sparse_axis": retained_sparse,
        "note_facts": [
            _supplemental_observation_payload(obs) for obs in reconciled.note_facts
        ],
        "share_facts": [
            _supplemental_observation_payload(obs) for obs in reconciled.share_facts
        ],
        "overlap_conflict_count": len(reconciled.conflicts),
        "supplemental_conflict_count": len(reconciled.supplemental_conflicts),
    }
    if reconciled.selected_geographic_facts:
        payload["selected_geographic_segment_facts"] = [
            _selected_geographic_payload(item)
            for item in reconciled.selected_geographic_facts
        ]
    if reconciled.selected_operating_kpi_facts:
        payload["selected_operating_kpi_facts"] = [
            _selected_operating_kpi_payload(item)
            for item in reconciled.selected_operating_kpi_facts
        ]
    if reconciled.requested_admit_periods:
        payload["admitted_comparative_periods"] = [
            period.isoformat() for period in reconciled.admitted_comparative_periods
        ]
        payload["excluded_comparative_periods"] = [
            period.isoformat() for period in reconciled.excluded_comparative_periods
        ]
    return payload


def reconciliation_management_admission_payload(
    reconciled: ReconciledCompanyData,
) -> dict[str, Any] | None:
    """Separate audit artifact for admitted management-KPI observations."""
    if reconciled.management_admission is None:
        return None
    from .management_kpi import management_admission_payload

    return management_admission_payload(reconciled.management_admission)


def reconciliation_conflicts_payload(
    reconciled: ReconciledCompanyData,
) -> dict[str, Any]:
    """Deterministic conflicts artifact (numeric disagreements only)."""
    conflicts = []
    for conflict in sorted(
        reconciled.conflicts,
        key=lambda c: (c.statement, c.row_identity, c.period.isoformat()),
    ):
        conflicts.append(
            {
                "statement": conflict.statement,
                "row_identity": conflict.row_identity,
                "period": conflict.period.isoformat(),
                "observations": [
                    _observation_payload(o) for o in conflict.observations
                ],
                "selected": _observation_payload(conflict.selected),
                "reason": conflict.reason,
            }
        )

    supplemental_conflicts = [
        _supplemental_conflict_payload(conflict)
        for conflict in sorted(
            reconciled.supplemental_conflicts,
            key=lambda c: (c.kind, c.fact_type, c.period.isoformat()),
        )
    ]
    return {
        "company_name": reconciled.company_name,
        "ticker": reconciled.ticker,
        "conflicts": conflicts,
        "overlap_conflict_count": len(conflicts),
        "supplemental_conflicts": supplemental_conflicts,
        "supplemental_conflict_count": len(supplemental_conflicts),
    }


def _selected_operating_kpi_payload(item) -> dict[str, Any]:
    out: dict[str, Any] = {
        "identity": item.fact_type,
        "metric": item.metric,
        "population": item.population,
        "period": item.period.isoformat(),
        "value": _num(item.value),
        "unit": item.unit,
        "filing_year": item.filing_year,
        "source_file": item.source_file,
        "source_sha256": item.source_sha256,
        "pdf_page": item.pdf_page,
        "presentation_basis": item.presentation_basis,
        "selection_reason": item.selection_reason,
    }
    if item.source_note:
        out["source_note"] = item.source_note
    if item.source_label:
        out["source_label"] = item.source_label
    return out


def _selected_geographic_payload(item) -> dict[str, Any]:
    out: dict[str, Any] = {
        "identity": item.fact_type,
        "period": item.period.isoformat(),
        "value": _num(item.value),
        "filing_year": item.filing_year,
        "source_file": item.source_file,
        "source_sha256": item.source_sha256,
        "pdf_page": item.pdf_page,
        "presentation_basis": item.presentation_basis,
        "selection_reason": item.selection_reason,
    }
    if item.presentation_family:
        out["presentation_family"] = item.presentation_family
    if item.source_note:
        out["source_note"] = item.source_note
    if item.source_label:
        out["source_label"] = item.source_label
    return out


def _supplemental_conflict_payload(conflict: SupplementalConflict) -> dict[str, Any]:
    ordered = sorted(
        conflict.observations,
        key=lambda obs: (
            obs.filing_year,
            obs.source_file,
            obs.fact.source.page,
        ),
    )
    return {
        "kind": conflict.kind,
        "fact_type": conflict.fact_type,
        "period": conflict.period.isoformat(),
        "observations": [_supplemental_observation_payload(obs) for obs in ordered],
        "reason": conflict.reason,
    }
