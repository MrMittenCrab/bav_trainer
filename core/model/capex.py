"""Historical PP&E capex source resolution, sign contract, and revenue intensity.

Optional, source-gated module. Resolves CF ``payments_for_ppe`` through the
shared line-resolver contract (canonical concept plus the explicit-concept
alias ``capital_expenditures``). Stored concepts, values, signs, and
provenance are left unchanged. Preserves reported cash-flow signs and
converts to analytical PP&E capex as ``ppe_capex = -payments_reported``.
Computes ``ppe_capex_to_revenue`` from resolved historical revenue.

When unambiguous reported operating cash flow also resolves, extends the
schedule with ``cash_after_ppe_capex = CFO − ppe_capex`` and its revenue
margin. Absent or ambiguous CFO omits only that extension; existing capex
exercises remain. Does not infer capex from investing totals, PP&E
movements, D&A, intangible purchases, or lease payments. Label-only capex
inputs remain unsupported. The cash-after extension is not comprehensive
free cash flow and is not a maintenance/growth-capex estimate.
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
_CFO_CONCEPT = "operating_cash_flow"


@dataclass(frozen=True)
class CapexAvailability:
    payments_for_ppe: bool
    ambiguous: bool
    operating_cash_flow: bool
    operating_cash_flow_ambiguous: bool


@dataclass(frozen=True)
class CapexSeries:
    payments_reported: tuple[float, ...]
    ppe_capex: tuple[float, ...]
    ppe_capex_to_revenue: tuple[float | str, ...]
    operating_cash_flow: tuple[float, ...] | None = None
    cash_after_ppe_capex: tuple[float, ...] | None = None
    cash_after_ppe_capex_to_revenue: tuple[float | str, ...] | None = None


def resolve_capex_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique resolved CF payments line, or None if unavailable."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return None
    return resolved.item


def resolve_operating_cash_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique resolved CF operating-cash-flow line, or None."""
    try:
        resolved = resolve_line(
            financials.cash_flow, _CFO_CONCEPT, required=False
        )
    except AmbiguousLineError:
        return None
    return resolved.item


def capex_availability(
    financials: StandardizedFinancials,
) -> CapexAvailability:
    """Report unique CF payments_for_ppe and operating_cash_flow resolution."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        payments_for_ppe = False
        ambiguous = True
    else:
        payments_for_ppe = resolved.item is not None
        ambiguous = False

    try:
        cfo = resolve_line(financials.cash_flow, _CFO_CONCEPT, required=False)
    except AmbiguousLineError:
        operating_cash_flow = False
        operating_cash_flow_ambiguous = True
    else:
        operating_cash_flow = cfo.item is not None
        operating_cash_flow_ambiguous = False

    return CapexAvailability(
        payments_for_ppe=payments_for_ppe,
        ambiguous=ambiguous,
        operating_cash_flow=operating_cash_flow,
        operating_cash_flow_ambiguous=operating_cash_flow_ambiguous,
    )


def capex_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique CF payments_for_ppe line resolves."""
    availability = capex_availability(financials)
    return availability.payments_for_ppe and not availability.ambiguous


def cash_after_ppe_capex_applicable(financials: StandardizedFinancials) -> bool:
    """Extension requires unique capex payments and unique reported CFO."""
    availability = capex_availability(financials)
    return (
        availability.payments_for_ppe
        and not availability.ambiguous
        and availability.operating_cash_flow
        and not availability.operating_cash_flow_ambiguous
    )


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

    operating_cash_flow: tuple[float, ...] | None = None
    cash_after_ppe_capex: tuple[float, ...] | None = None
    cash_after_ppe_capex_to_revenue: tuple[float | str, ...] | None = None
    cfo_item = resolve_operating_cash_source(financials)
    if cfo_item is not None:
        operating_cash_flow = tuple(
            required_period_value(cfo_item, period, field=_CFO_CONCEPT)
            for period in periods
        )
        cash_after_ppe_capex = tuple(
            operating_cash_flow[j] - ppe_capex[j] for j in range(n)
        )
        cash_after_ppe_capex_to_revenue = tuple(
            ratio_or_na(cash_after_ppe_capex[j], revenue[j]) for j in range(n)
        )

    return CapexSeries(
        payments_reported=payments_reported,
        ppe_capex=ppe_capex,
        ppe_capex_to_revenue=ppe_capex_to_revenue,
        operating_cash_flow=operating_cash_flow,
        cash_after_ppe_capex=cash_after_ppe_capex,
        cash_after_ppe_capex_to_revenue=cash_after_ppe_capex_to_revenue,
    )
