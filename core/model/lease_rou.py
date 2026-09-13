"""Historical lease ROU-asset intensity / trend diagnostics (Step 9M.6).

Optional, source-gated module. Resolves BS ``right_of_use_assets`` via unique
exact concept only. Independent of lease-liability availability and
classification treatment. Does not invent lease payments, discount rates,
amortization, or liability reconciliations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

if TYPE_CHECKING:
    from .financial_math import AnchorMetrics

_CONCEPT = "right_of_use_assets"


@dataclass(frozen=True)
class LeaseRouAvailability:
    right_of_use_assets: bool
    ambiguous: bool


@dataclass(frozen=True)
class LeaseRouSeries:
    rou_assets: tuple[float, ...]
    rou_assets_change: tuple[float | None, ...]
    rou_assets_growth: tuple[float | str | None, ...]
    average_rou_assets: tuple[float | None, ...]
    rou_assets_to_revenue: tuple[float | str | None, ...]


def resolve_lease_rou_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique exact-concept ROU asset line, or None if unavailable."""
    try:
        resolved = resolve_line(
            financials.balance_sheet, _CONCEPT, required=False
        )
    except AmbiguousLineError:
        return None
    return resolved.item


def lease_rou_availability(
    financials: StandardizedFinancials,
) -> LeaseRouAvailability:
    """Report whether a unique exact-concept ROU asset line resolves."""
    try:
        resolved = resolve_line(
            financials.balance_sheet, _CONCEPT, required=False
        )
    except AmbiguousLineError:
        return LeaseRouAvailability(right_of_use_assets=False, ambiguous=True)
    return LeaseRouAvailability(
        right_of_use_assets=resolved.item is not None,
        ambiguous=False,
    )


def lease_rou_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique exact-concept ROU asset line resolves."""
    availability = lease_rou_availability(financials)
    return availability.right_of_use_assets and not availability.ambiguous


def compute_lease_rou_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: "AnchorMetrics",
) -> LeaseRouSeries:
    """Compute ROU-asset change / intensity diagnostics for modeled periods."""
    item = resolve_lease_rou_source(financials)
    if item is None:
        raise MissingLineError("right_of_use_assets source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "lease-ROU period axis must match AnchorMetrics historical revenue length"
        )

    levels = tuple(
        required_period_value(item, period, field=_CONCEPT) for period in periods
    )

    change: list[float | None] = [None]
    growth: list[float | str | None] = [None]
    average: list[float | None] = [None]
    to_revenue: list[float | str | None] = [None]
    for j in range(1, n):
        delta = levels[j] - levels[j - 1]
        change.append(delta)
        growth.append(ratio_or_na(delta, levels[j - 1]))
        avg = (levels[j - 1] + levels[j]) / 2.0
        average.append(avg)
        to_revenue.append(ratio_or_na(avg, revenue[j]))

    return LeaseRouSeries(
        rou_assets=levels,
        rou_assets_change=tuple(change),
        rou_assets_growth=tuple(growth),
        average_rou_assets=tuple(average),
        rou_assets_to_revenue=tuple(to_revenue),
    )
