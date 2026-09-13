"""Convert reconciled documentary facts into model-only StandardizedFinancials."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from ..data.filing import PresentationRole, SupplementalFact
from ..data.interface import (
    FinancialPeriod,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
)
from .filing_reconciler import ReconciledCompanyData, ReconciledValue

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


def _observation_payload(obs) -> dict[str, Any]:
    return {
        "filing_year": obs.filing_year,
        "source_file": obs.source_file,
        "source_sha256": obs.source_sha256,
        "pdf_page": obs.pdf_page,
        "presentation_role": obs.presentation_role.value,
        "value": obs.value if not float(obs.value).is_integer() else int(obs.value),
    }


def standardize_reconciled(
    reconciled: ReconciledCompanyData,
) -> StandardizedFinancials:
    """Emit model-only StandardizedFinancials from reconciled documentary facts."""
    model_periods = list(reconciled.periods)
    period_set = set(model_periods)
    grouped = _group_by_row(reconciled)

    statements: dict[str, list[LineItem]] = {
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
    }

    for (statement, _ident), rows in sorted(grouped.items(), key=lambda item: item[0]):
        by_period = {row.period: row for row in rows}
        if set(by_period) != period_set:
            continue
        # Prefer label/concept from the latest model-period selection
        latest = by_period[model_periods[-1]]
        statements[statement].append(
            LineItem(
                label=latest.label,
                concept=latest.suggested_concept,
                values={period: float(by_period[period].selected.value) for period in model_periods},
            )
        )

    historical_shares = _historical_shares(reconciled)

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
    )


def _historical_shares(
    reconciled: ReconciledCompanyData,
) -> HistoricalShareData | None:
    """Emit historical shares only for a complete reported diluted WAS axis."""
    period_set = set(reconciled.periods)
    series: dict[date, float] = {}
    scale_bases: set[str] = set()
    for fact in reconciled.share_facts:
        if fact.fact_type != "diluted_weighted_average_shares":
            continue
        if fact.status != "reported":
            continue
        if fact.period not in period_set:
            continue
        series[fact.period] = float(fact.value)
        # Optional scale hint lives only in source label text for now.
        scale_bases.add("shares")
    if set(series) != period_set:
        return None
    if len(scale_bases) != 1:
        return None
    return HistoricalShareData(
        scale_basis=next(iter(scale_bases)),
        diluted_weighted_average={period: series[period] for period in reconciled.periods},
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

    for (statement, ident), rows in sorted(grouped.items(), key=lambda item: item[0]):
        by_period = {row.period: row for row in rows}
        available = sorted(by_period)
        label = rows[-1].label
        concept = rows[-1].suggested_concept
        if set(by_period) != period_set:
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
                "status": "selected",
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

    source_files = sorted(
        {
            (
                value.selected.source_file,
                value.selected.source_sha256,
            )
            for value in reconciled.values
        }
    )

    return {
        "company_name": reconciled.company_name,
        "ticker": reconciled.ticker,
        "stock_code": reconciled.stock_code,
        "jurisdiction": reconciled.jurisdiction,
        "currency": reconciled.currency,
        "unit_scale": reconciled.unit_scale,
        "periods": [p.isoformat() for p in model_periods],
        "source_files": [
            {"source_file": name, "source_sha256": sha} for name, sha in source_files
        ],
        "values": values,
        "omitted_incomplete_axis": omitted,
        "note_facts": [_fact_payload(fact) for fact in reconciled.note_facts],
        "share_facts": [_fact_payload(fact) for fact in reconciled.share_facts],
        "overlap_conflict_count": len(reconciled.conflicts),
    }


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
    return {
        "company_name": reconciled.company_name,
        "ticker": reconciled.ticker,
        "conflicts": conflicts,
        "overlap_conflict_count": len(conflicts),
    }


def _fact_payload(fact: SupplementalFact) -> dict[str, Any]:
    out: dict[str, Any] = {
        "fact_type": fact.fact_type,
        "period": fact.period.isoformat(),
        "value": fact.value if not float(fact.value).is_integer() else int(fact.value),
        "status": fact.status,
        "source": {
            "page": fact.source.page,
            **(
                {"statement": fact.source.statement}
                if fact.source.statement
                else {}
            ),
            **({"note": fact.source.note} if fact.source.note else {}),
            **({"label": fact.source.label} if fact.source.label else {}),
        },
    }
    if fact.derivation:
        out["derivation"] = fact.derivation
    return out
