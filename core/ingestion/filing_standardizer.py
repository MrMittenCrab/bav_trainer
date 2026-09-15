"""Convert reconciled documentary facts into model-only StandardizedFinancials."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from ..data.filing import PresentationRole
from ..data.interface import (
    FinancialPeriod,
    HistoricalLeaseData,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
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


def standardize_reconciled(
    reconciled: ReconciledCompanyData,
) -> StandardizedFinancials:
    """Emit model-only StandardizedFinancials from reconciled documentary facts."""
    model_periods = list(reconciled.periods)
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

    return StandardizedFinancials(
        ticker=reconciled.ticker,
        company_name=reconciled.company_name,
        currency=reconciled.currency,
        units=_units_string(reconciled.currency, reconciled.unit_scale),
        jurisdiction=reconciled.jurisdiction,
        stock_code=reconciled.stock_code,
        periods=[
            FinancialPeriod(end_date=period, label=f"FY{period.year}")
            for period in model_periods
        ],
        income_statement=statements["income_statement"],
        balance_sheet=statements["balance_sheet"],
        cash_flow=statements["cash_flow"],
        historical_shares=historical_shares,
        historical_lease=historical_lease,
    )


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
    if reconciled.requested_admit_periods:
        payload["admitted_comparative_periods"] = [
            period.isoformat() for period in reconciled.admitted_comparative_periods
        ]
        payload["excluded_comparative_periods"] = [
            period.isoformat() for period in reconciled.excluded_comparative_periods
        ]
    return payload


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
