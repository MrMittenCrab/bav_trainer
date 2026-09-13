"""Historical lease-liability intensity / trend diagnostics (Step 9L.1).

Uses one uniquely resolvable aggregate lease-liability source line only.
Does not invent ROU assets, lease payments, discount rates, or amortisation.
Does not aggregate split current / non-current lease-liability rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value


@dataclass(frozen=True)
class LeaseLiabilityAvailability:
    lease_liability: bool
    ambiguous: bool


@dataclass(frozen=True)
class LeaseLiabilitySeries:
    lease_liability: tuple[float, ...]
    lease_liability_to_revenue: tuple[float | str, ...]
    lease_liability_change: tuple[float | None, ...]
    lease_liability_growth: tuple[float | str | None, ...]


def lease_liability_availability(
    financials: StandardizedFinancials,
) -> LeaseLiabilityAvailability:
    """Report whether an aggregate lease-liability line resolves uniquely."""
    try:
        resolved = resolve_line(
            financials.balance_sheet,
            "lease_liability",
            required=False,
        )
    except AmbiguousLineError:
        return LeaseLiabilityAvailability(lease_liability=False, ambiguous=True)
    return LeaseLiabilityAvailability(
        lease_liability=resolved.item is not None,
        ambiguous=False,
    )


def lease_liability_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when one unique aggregate lease liability resolves."""
    availability = lease_liability_availability(financials)
    return availability.lease_liability and not availability.ambiguous


def compute_lease_liability_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> LeaseLiabilitySeries:
    """Compute lease-liability intensity / change diagnostics for modeled periods."""
    lease_item = resolve_line(
        financials.balance_sheet,
        "lease_liability",
        required=True,
    ).item
    assert lease_item is not None

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "lease-liability period axis must match AnchorMetrics historical "
            "revenue length"
        )

    lease_vals = tuple(
        required_period_value(lease_item, period, field="lease_liability")
        for period in periods
    )
    lease_to_revenue = tuple(
        ratio_or_na(lease_vals[j], revenue[j]) for j in range(n)
    )

    change: list[float | None] = [None]
    growth: list[float | str | None] = [None]
    for j in range(1, n):
        change.append(lease_vals[j] - lease_vals[j - 1])
        growth.append(ratio_or_na(lease_vals[j] - lease_vals[j - 1], lease_vals[j - 1]))

    return LeaseLiabilitySeries(
        lease_liability=lease_vals,
        lease_liability_to_revenue=lease_to_revenue,
        lease_liability_change=tuple(change),
        lease_liability_growth=tuple(growth),
    )
