"""Parent / NCI ownership-attribution diagnostics (Step 9M.3C).

Optional module: requires a complete, unambiguous set of reported parent and NCI
profit and equity lines. Does not invent missing components from totals.
Consolidated BAV DuPont / NOA / Net Debt remain unchanged; parent ROE is a
separate shareholder-attribution diagnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_series

# Two displayed components vs one displayed total → 0.5 * (2 + 1) reporting units.
OWNERSHIP_BRIDGE_TOLERANCE = 1.5

_PROFIT_OWNER = "profit_attributable_to_owners"
_PROFIT_NCI = "profit_attributable_to_nci"
_EQUITY_OWNER = "equity_attributable_to_owners"
_EQUITY_NCI = "noncontrolling_interests"


class OwnershipAttributionIntegrityError(ValueError):
    """Ownership attribution is incomplete, ambiguous, or outside rounding envelope."""


@dataclass(frozen=True)
class OwnershipAttributionAvailability:
    available: bool
    partial: bool
    ambiguous: bool


@dataclass(frozen=True)
class OwnershipAttributionSeries:
    parent_profit: tuple[float, ...]
    nci_profit: tuple[float, ...]
    profit_attribution_gap: tuple[float, ...]
    parent_equity: tuple[float, ...]
    nci_equity: tuple[float, ...]
    equity_attribution_gap: tuple[float, ...]
    parent_roe: tuple[float | str | None, ...]


def _try_resolve(items, concept: str):
    try:
        return resolve_line(items, concept, required=False)
    except AmbiguousLineError:
        return "ambiguous"


def ownership_attribution_availability(
    financials: StandardizedFinancials,
) -> OwnershipAttributionAvailability:
    """Report whether a complete unique parent/NCI attribution set is present."""
    checks = (
        (_try_resolve(financials.income_statement, _PROFIT_OWNER),),
        (_try_resolve(financials.income_statement, _PROFIT_NCI),),
        (_try_resolve(financials.balance_sheet, _EQUITY_OWNER),),
        (_try_resolve(financials.balance_sheet, _EQUITY_NCI),),
    )
    if any(result == "ambiguous" for (result,) in checks):
        return OwnershipAttributionAvailability(
            available=False, partial=False, ambiguous=True
        )

    present = 0
    for (resolved,) in checks:
        if resolved.item is not None:
            present += 1

    if present == 0:
        return OwnershipAttributionAvailability(
            available=False, partial=False, ambiguous=False
        )
    if present == 4:
        return OwnershipAttributionAvailability(
            available=True, partial=False, ambiguous=False
        )
    return OwnershipAttributionAvailability(
        available=False, partial=True, ambiguous=False
    )


def ownership_attribution_applicable(financials: StandardizedFinancials) -> bool:
    availability = ownership_attribution_availability(financials)
    return (
        availability.available
        and not availability.partial
        and not availability.ambiguous
    )


def compute_ownership_attribution_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> OwnershipAttributionSeries:
    """Compute parent/NCI bridges and parent ROE for modeled periods."""
    availability = ownership_attribution_availability(financials)
    if availability.ambiguous:
        raise OwnershipAttributionIntegrityError(
            "ownership attribution lines are ambiguous"
        )
    if availability.partial or not availability.available:
        raise OwnershipAttributionIntegrityError(
            "ownership attribution requires a complete parent/NCI profit and equity set"
        )

    parent_profit_item = resolve_line(
        financials.income_statement, _PROFIT_OWNER, required=True
    ).item
    nci_profit_item = resolve_line(
        financials.income_statement, _PROFIT_NCI, required=True
    ).item
    total_profit_item = resolve_line(
        financials.income_statement, "net_income", required=True
    ).item
    parent_equity_item = resolve_line(
        financials.balance_sheet, _EQUITY_OWNER, required=True
    ).item
    nci_equity_item = resolve_line(
        financials.balance_sheet, _EQUITY_NCI, required=True
    ).item
    total_equity_item = resolve_line(
        financials.balance_sheet, "total_equity", required=True
    ).item
    assert parent_profit_item is not None
    assert nci_profit_item is not None
    assert total_profit_item is not None
    assert parent_equity_item is not None
    assert nci_equity_item is not None
    assert total_equity_item is not None

    parent_profit = required_period_series(
        parent_profit_item, periods, field=_PROFIT_OWNER
    )
    nci_profit = required_period_series(nci_profit_item, periods, field=_PROFIT_NCI)
    total_profit = required_period_series(
        total_profit_item, periods, field="net_income"
    )
    parent_equity = required_period_series(
        parent_equity_item, periods, field=_EQUITY_OWNER
    )
    nci_equity = required_period_series(nci_equity_item, periods, field=_EQUITY_NCI)
    total_equity = required_period_series(
        total_equity_item, periods, field="total_equity"
    )

    profit_gap = tuple(
        parent_profit[i] + nci_profit[i] - total_profit[i] for i in range(len(periods))
    )
    equity_gap = tuple(
        parent_equity[i] + nci_equity[i] - total_equity[i] for i in range(len(periods))
    )
    for i, pd in enumerate(periods):
        if abs(profit_gap[i]) > OWNERSHIP_BRIDGE_TOLERANCE:
            raise OwnershipAttributionIntegrityError(
                f"{pd.isoformat()}: profit attribution gap={profit_gap[i]:.4g} "
                f"exceeds reporting-unit envelope {OWNERSHIP_BRIDGE_TOLERANCE}"
            )
        if abs(equity_gap[i]) > OWNERSHIP_BRIDGE_TOLERANCE:
            raise OwnershipAttributionIntegrityError(
                f"{pd.isoformat()}: equity attribution gap={equity_gap[i]:.4g} "
                f"exceeds reporting-unit envelope {OWNERSHIP_BRIDGE_TOLERANCE}"
            )

    parent_roe: list[float | str | None] = [None]
    for i in range(1, len(periods)):
        avg_equity = (parent_equity[i - 1] + parent_equity[i]) / 2.0
        parent_roe.append(ratio_or_na(parent_profit[i], avg_equity))

    return OwnershipAttributionSeries(
        parent_profit=parent_profit,
        nci_profit=nci_profit,
        profit_attribution_gap=profit_gap,
        parent_equity=parent_equity,
        nci_equity=nci_equity,
        equity_attribution_gap=equity_gap,
        parent_roe=tuple(parent_roe),
    )


def per_share_earnings_numerator(
    financials: StandardizedFinancials,
    periods: list[date],
    fallback_total_profit: tuple[float, ...],
) -> tuple[float, ...]:
    """Return parent profit when ownership is complete; else consolidated profit."""
    availability = ownership_attribution_availability(financials)
    if availability.ambiguous or availability.partial:
        raise OwnershipAttributionIntegrityError(
            "per-share earnings numerator cannot use consolidated profit when "
            "parent/NCI attribution evidence is partial or ambiguous"
        )
    if not availability.available:
        if len(fallback_total_profit) != len(periods):
            raise ValueError(
                "fallback_total_profit length must match modeled periods"
            )
        return tuple(float(v) for v in fallback_total_profit)
    series = compute_ownership_attribution_series(financials, periods)
    return series.parent_profit
