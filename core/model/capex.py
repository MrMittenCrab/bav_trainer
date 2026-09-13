"""Historical PP&E capex source resolution, sign contract, and revenue intensity.

Optional, source-gated module. Resolves CF ``payments_for_ppe`` via unique
exact concept only. Preserves reported cash-flow signs and converts to
analytical PP&E capex as ``ppe_capex = -payments_reported``. Computes
``ppe_capex_to_revenue`` from resolved historical revenue. Does not infer
capex from investing totals, PP&E movements, D&A, intangible purchases, or
lease payments.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

_CONCEPT = "payments_for_ppe"


@dataclass(frozen=True)
class CapexAvailability:
    payments_for_ppe: bool
    ambiguous: bool


@dataclass(frozen=True)
class CapexSeries:
    payments_reported: tuple[float, ...]
    ppe_capex: tuple[float, ...]
    ppe_capex_to_revenue: tuple[float | str, ...]


def resolve_capex_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique exact-concept CF payments line, or None if unavailable."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return None
    return resolved.item


def capex_availability(
    financials: StandardizedFinancials,
) -> CapexAvailability:
    """Report whether a unique exact-concept CF payments_for_ppe line resolves."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return CapexAvailability(payments_for_ppe=False, ambiguous=True)
    return CapexAvailability(
        payments_for_ppe=resolved.item is not None,
        ambiguous=False,
    )


def capex_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique exact-concept CF payments_for_ppe resolves."""
    availability = capex_availability(financials)
    return availability.payments_for_ppe and not availability.ambiguous


def compute_capex_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> CapexSeries:
    """Read reported payments and convert to analytical PP&E capex for periods."""
    item = resolve_capex_source(financials)
    if item is None:
        raise MissingLineError("payments_for_ppe source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "capex period axis must match AnchorMetrics historical revenue length"
        )

    payments_reported = tuple(
        required_period_value(item, period, field=_CONCEPT) for period in periods
    )
    # Signed cash-flow contract: negate reported values; never abs() or infer sign.
    ppe_capex = tuple(-v for v in payments_reported)
    ppe_capex_to_revenue = tuple(
        ratio_or_na(ppe_capex[j], revenue[j]) for j in range(n)
    )
    return CapexSeries(
        payments_reported=payments_reported,
        ppe_capex=ppe_capex,
        ppe_capex_to_revenue=ppe_capex_to_revenue,
    )
