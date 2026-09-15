"""Historical share-repurchase source resolution, sign contract, and cash-use.

Optional, source-gated module. Resolves unique explicit CF
``repurchase_of_common_stock`` only. No label fallback and no substitution
from treasury-stock movements, share-count changes, SBC expense, settlement
proceeds, or withholding payments. Stored concepts, values, signs, and
provenance are left unchanged.

Converts reported repurchase cash to analytical outflow as
``share_repurchase_outflow = -reported``. Computes
``share_repurchase_to_revenue`` from resolved historical revenue.

When unambiguous reported operating cash flow, PP&E-capex, and acquisition
sources also resolve, extends the schedule with
``cash_after_ppe_capex_acquisitions_and_repurchases = CFO − ppe_capex −
acquisition_cash_outflow − share_repurchase_outflow``. Absent acquisition
evidence is omitted rather than treated as zero. Absent or ambiguous CFO
or capex omits only that residual. The first two families do not depend on
capex, acquisitions, share history, or SBC.

The residual is a mechanical cash-use diagnostic. A negative residual means
the selected cash uses exceed reported CFO; it does not identify debt
funding, comprehensive free cash flow, or a complete cash reconciliation.
Reported repurchases are not total shareholder distributions or dilution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .acquisition_cash import (
    acquisition_cash_availability,
    cash_after_ppe_capex_and_acquisitions_applicable,
    compute_acquisition_cash_series,
)
from .capex import compute_capex_series
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

_CONCEPT = "repurchase_of_common_stock"


@dataclass(frozen=True)
class ShareRepurchaseAvailability:
    repurchase_of_common_stock: bool
    ambiguous: bool
    operating_cash_flow: bool
    operating_cash_flow_ambiguous: bool
    ppe_capex: bool
    ppe_capex_ambiguous: bool
    acquisition_net_of_cash_acquired: bool
    acquisition_ambiguous: bool


@dataclass(frozen=True)
class ShareRepurchaseSeries:
    payments_reported: tuple[float, ...]
    share_repurchase_outflow: tuple[float, ...]
    share_repurchase_to_revenue: tuple[float | str, ...]
    cash_after_ppe_capex_acquisitions_and_repurchases: (
        tuple[float, ...] | None
    ) = None


def resolve_share_repurchase_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique explicit CF repurchase line, or None if unavailable."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        return None
    return resolved.item


def share_repurchase_availability(
    financials: StandardizedFinancials,
) -> ShareRepurchaseAvailability:
    """Report unique CF repurchase, CFO, PP&E-capex, and acquisition resolution."""
    try:
        resolved = resolve_line(financials.cash_flow, _CONCEPT, required=False)
    except AmbiguousLineError:
        repurchase = False
        ambiguous = True
    else:
        repurchase = resolved.item is not None
        ambiguous = False

    acq = acquisition_cash_availability(financials)
    return ShareRepurchaseAvailability(
        repurchase_of_common_stock=repurchase,
        ambiguous=ambiguous,
        operating_cash_flow=acq.operating_cash_flow,
        operating_cash_flow_ambiguous=acq.operating_cash_flow_ambiguous,
        ppe_capex=acq.ppe_capex,
        ppe_capex_ambiguous=acq.ppe_capex_ambiguous,
        acquisition_net_of_cash_acquired=acq.acquisition_net_of_cash_acquired,
        acquisition_ambiguous=acq.ambiguous,
    )


def share_repurchase_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique explicit CF repurchase line resolves."""
    availability = share_repurchase_availability(financials)
    return availability.repurchase_of_common_stock and not availability.ambiguous


def cash_after_ppe_capex_acquisitions_and_repurchases_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Residual requires unique repurchase, unique CFO, unique PP&E capex, and unique acquisition cash."""
    return (
        share_repurchase_applicable(financials)
        and cash_after_ppe_capex_and_acquisitions_applicable(financials)
    )


def compute_share_repurchase_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> ShareRepurchaseSeries:
    """Read reported repurchase cash and convert to analytical outflow for periods."""
    item = resolve_share_repurchase_source(financials)
    if item is None:
        raise MissingLineError("repurchase_of_common_stock source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "share-repurchase period axis must match AnchorMetrics historical "
            "revenue length"
        )

    payments_reported = tuple(
        required_period_value(item, period, field=_CONCEPT) for period in periods
    )
    # Signed cash-flow contract: negate reported values; never abs() or infer sign.
    share_repurchase_outflow = tuple(-v for v in payments_reported)
    share_repurchase_to_revenue = tuple(
        ratio_or_na(share_repurchase_outflow[j], revenue[j]) for j in range(n)
    )

    residual: tuple[float, ...] | None = None
    if cash_after_ppe_capex_acquisitions_and_repurchases_applicable(financials):
        capex_series = compute_capex_series(financials, periods, anchor)
        acq_series = compute_acquisition_cash_series(financials, periods, anchor)
        assert capex_series.operating_cash_flow is not None
        assert acq_series.acquisition_cash_outflow is not None
        residual = tuple(
            capex_series.operating_cash_flow[j]
            - capex_series.ppe_capex[j]
            - acq_series.acquisition_cash_outflow[j]
            - share_repurchase_outflow[j]
            for j in range(n)
        )

    return ShareRepurchaseSeries(
        payments_reported=payments_reported,
        share_repurchase_outflow=share_repurchase_outflow,
        share_repurchase_to_revenue=share_repurchase_to_revenue,
        cash_after_ppe_capex_acquisitions_and_repurchases=residual,
    )
