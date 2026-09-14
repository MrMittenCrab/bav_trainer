"""Historical lease-repayment CF source resolution, sign contract, and revenue intensity.

Optional, source-gated module. Resolves CF ``repayments_of_lease_liabilities`` via
unique exact concept only. Preserves reported cash-flow signs and converts to
analytical lease repayments as ``lease_repayments = -reported_repayments``.
Computes ``lease_repayments_to_revenue`` from resolved historical revenue.

Activation is independent of lease-liability balances, ROU balances, and
lease-interest disclosures. Does not infer repayments from balance changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

_CONCEPT = "repayments_of_lease_liabilities"


@dataclass(frozen=True)
class LeaseRepaymentAvailability:
    repayments_of_lease_liabilities: bool
    ambiguous: bool


@dataclass(frozen=True)
class LeaseRepaymentSeries:
    repayments_reported: tuple[float, ...]
    lease_repayments: tuple[float, ...]
    lease_repayments_to_revenue: tuple[float | str, ...]


def resolve_lease_repayment_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique exact-concept CF repayments line, or None if unavailable."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return None
    return resolved.item


def lease_repayment_availability(
    financials: StandardizedFinancials,
) -> LeaseRepaymentAvailability:
    """Report whether a unique exact-concept CF repayments line resolves."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return LeaseRepaymentAvailability(
            repayments_of_lease_liabilities=False, ambiguous=True
        )
    return LeaseRepaymentAvailability(
        repayments_of_lease_liabilities=resolved.item is not None,
        ambiguous=False,
    )


def lease_repayment_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique exact-concept CF repayments line resolves."""
    availability = lease_repayment_availability(financials)
    return (
        availability.repayments_of_lease_liabilities and not availability.ambiguous
    )


def compute_lease_repayment_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> LeaseRepaymentSeries:
    """Read reported repayments and convert to analytical lease repayments."""
    item = resolve_lease_repayment_source(financials)
    if item is None:
        raise MissingLineError("repayments_of_lease_liabilities source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "lease-repayment period axis must match AnchorMetrics historical "
            "revenue length"
        )

    repayments_reported = tuple(
        required_period_value(item, period, field=_CONCEPT) for period in periods
    )
    # Signed cash-flow contract: negate reported values; never abs() or infer sign.
    lease_repayments = tuple(-v for v in repayments_reported)
    lease_repayments_to_revenue = tuple(
        ratio_or_na(lease_repayments[j], revenue[j]) for j in range(n)
    )
    return LeaseRepaymentSeries(
        repayments_reported=repayments_reported,
        lease_repayments=lease_repayments,
        lease_repayments_to_revenue=lease_repayments_to_revenue,
    )
