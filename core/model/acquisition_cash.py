"""Historical acquisition-cash source resolution, sign contract, and cash-use.

Optional, source-gated module. Resolves unique explicit CF
``acquisition_net_of_cash_acquired`` only. No label fallback and no
substitution from goodwill changes, intangible purchases, securities, or
ROU payments. Stored concepts, values, signs, and provenance are left
unchanged.

Converts reported acquisition cash to analytical outflow as
``acquisition_cash_outflow = -reported``. Computes
``acquisition_cash_to_revenue`` from resolved historical revenue.

When unambiguous reported operating cash flow and PP&E-capex sources also
resolve, extends the schedule with
``cash_after_ppe_capex_and_acquisitions = CFO − ppe_capex − outflow``.
Absent or ambiguous CFO or capex omits only that residual. The first two
families do not depend on goodwill/intangible balances or capex.

The residual is a mechanical cash-use diagnostic, not comprehensive free
cash flow, acquisition profitability, purchase-price allocation, or a
goodwill roll-forward.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .capex import (
    cash_after_ppe_capex_applicable,
    compute_capex_series,
)
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

_CONCEPT = "acquisition_net_of_cash_acquired"


@dataclass(frozen=True)
class AcquisitionCashAvailability:
    acquisition_net_of_cash_acquired: bool
    ambiguous: bool
    operating_cash_flow: bool
    operating_cash_flow_ambiguous: bool
    ppe_capex: bool
    ppe_capex_ambiguous: bool


@dataclass(frozen=True)
class AcquisitionCashSeries:
    payments_reported: tuple[float, ...]
    acquisition_cash_outflow: tuple[float, ...]
    acquisition_cash_to_revenue: tuple[float | str, ...]
    cash_after_ppe_capex_and_acquisitions: tuple[float, ...] | None = None


def resolve_acquisition_cash_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique explicit CF acquisition line, or None if unavailable."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return None
    return resolved.item


def acquisition_cash_availability(
    financials: StandardizedFinancials,
) -> AcquisitionCashAvailability:
    """Report unique CF acquisition, operating-cash-flow, and PP&E-capex resolution."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        acquisition = False
        ambiguous = True
    else:
        acquisition = resolved.item is not None
        ambiguous = False

    try:
        cfo = resolve_line(
            financials.cash_flow, "operating_cash_flow", required=False
        )
    except AmbiguousLineError:
        operating_cash_flow = False
        operating_cash_flow_ambiguous = True
    else:
        operating_cash_flow = cfo.item is not None
        operating_cash_flow_ambiguous = False

    try:
        capex = resolve_line(financials.cash_flow, "payments_for_ppe", required=False)
    except AmbiguousLineError:
        ppe_capex = False
        ppe_capex_ambiguous = True
    else:
        ppe_capex = capex.item is not None
        ppe_capex_ambiguous = False

    return AcquisitionCashAvailability(
        acquisition_net_of_cash_acquired=acquisition,
        ambiguous=ambiguous,
        operating_cash_flow=operating_cash_flow,
        operating_cash_flow_ambiguous=operating_cash_flow_ambiguous,
        ppe_capex=ppe_capex,
        ppe_capex_ambiguous=ppe_capex_ambiguous,
    )


def acquisition_cash_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique explicit CF acquisition line resolves."""
    availability = acquisition_cash_availability(financials)
    return (
        availability.acquisition_net_of_cash_acquired and not availability.ambiguous
    )


def cash_after_ppe_capex_and_acquisitions_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Residual requires unique acquisition cash, unique CFO, and unique PP&E capex."""
    return (
        acquisition_cash_applicable(financials)
        and cash_after_ppe_capex_applicable(financials)
    )


def compute_acquisition_cash_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> AcquisitionCashSeries:
    """Read reported acquisition cash and convert to analytical outflow for periods."""
    item = resolve_acquisition_cash_source(financials)
    if item is None:
        raise MissingLineError("acquisition_net_of_cash_acquired source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "acquisition-cash period axis must match AnchorMetrics historical "
            "revenue length"
        )

    payments_reported = tuple(
        required_period_value(item, period, field=_CONCEPT) for period in periods
    )
    # Signed cash-flow contract: negate reported values; never abs() or infer sign.
    acquisition_cash_outflow = tuple(-v for v in payments_reported)
    acquisition_cash_to_revenue = tuple(
        ratio_or_na(acquisition_cash_outflow[j], revenue[j]) for j in range(n)
    )

    residual: tuple[float, ...] | None = None
    if cash_after_ppe_capex_and_acquisitions_applicable(financials):
        capex_series = compute_capex_series(financials, periods, anchor)
        assert capex_series.operating_cash_flow is not None
        residual = tuple(
            capex_series.operating_cash_flow[j]
            - capex_series.ppe_capex[j]
            - acquisition_cash_outflow[j]
            for j in range(n)
        )

    return AcquisitionCashSeries(
        payments_reported=payments_reported,
        acquisition_cash_outflow=acquisition_cash_outflow,
        acquisition_cash_to_revenue=acquisition_cash_to_revenue,
        cash_after_ppe_capex_and_acquisitions=residual,
    )
