"""Source-supported historical geographic segment analytical series.

Optional, source-gated module. Consumes only ``StandardizedFinancials.historical_segment``
after existing contract validation. Missing or null payloads make the module
absent. Missing snapshots on an otherwise valid canonical fiscal axis yield
``SOURCE_UNAVAILABLE`` only for dependent outputs; gaps are never compressed
and another period is never substituted.

Computes each Americas / China Mainland / Rest of World segment's revenue share
of consolidated revenue, adjacent-period revenue growth, and reported operating
margin ``income_from_operations / net_revenue``. Reported operating margin is
not BAV NOPAT margin.

Calculated segment revenue and operating-profit totals are identified separately
from any reported ``segment_total``. Explicit bridge operations are applied in
stable identity order, preserving corporate-column versus itemized-reconciling
semantics and reported signs. Opening growth is absent. Later growth requires
both immediately adjacent model-period snapshots. Zero denominators use
``UNDEFINED_RATIO``. Reported zero numerators and negative profits are preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.historical_segments import (
    IFOP_CONSOLIDATED,
    IFOP_SEGMENTS,
    OP_ADD,
    OP_SUBTRACT,
    REVENUE_CONSOLIDATED,
    REVENUE_SEGMENTS,
    SEGMENTS,
    SUPPORTED_OPERATIONS,
    validate_historical_segment,
)
from ..data.interface import HistoricalSegmentPeriod, StandardizedFinancials
from .line_resolver import MissingLineError
from .period_axis import canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, ratio_or_na

GEOGRAPHIC_RATIO_TOLERANCE = 1e-12
REPORTED_OPERATING_MARGIN_BASIS = "income_from_operations / net_revenue"

_UNAVAILABLE_SEGMENTS: dict[str, str] = {name: SOURCE_UNAVAILABLE for name in SEGMENTS}


@dataclass(frozen=True)
class GeographicSegmentSeries:
    """Deterministic geographic economics keyed by canonical fiscal periods."""

    periods: tuple[date, ...]
    identities: tuple[str, ...]
    presentation_family: dict[date, str]
    net_revenue: dict[date, dict[str, float | str]]
    income_from_operations: dict[date, dict[str, float | str]]
    revenue_share: dict[date, dict[str, float | str]]
    revenue_growth: dict[date, dict[str, float | str | None]]
    reported_operating_margin: dict[date, dict[str, float | str]]
    calculated_segment_revenue_total: dict[date, float | str]
    calculated_segment_operating_profit_total: dict[date, float | str]
    signed_reconciling_contributions: dict[
        date, tuple[tuple[str, float], ...] | str
    ]
    reconstructed_consolidated_operating_profit: dict[date, float | str]
    reported_consolidated_revenue: dict[date, float | str]
    reported_consolidated_operating_profit: dict[date, float | str]
    consolidated_revenue_difference: dict[date, float | str]
    consolidated_operating_profit_difference: dict[date, float | str]


def geographic_segment_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when a historical_segment payload is supplied."""
    return financials.historical_segment is not None


def _snapshot_index(
    financials: StandardizedFinancials,
) -> dict[date, HistoricalSegmentPeriod]:
    assert financials.historical_segment is not None
    return {snapshot.period: snapshot for snapshot in financials.historical_segment.periods}


def _segment_amounts(
    snapshot: HistoricalSegmentPeriod,
    identities: tuple[str, ...],
) -> dict[str, float]:
    return {
        short: float(snapshot.values[full])
        for short, full in zip(SEGMENTS, identities, strict=True)
    }


def _signed_amount(operation: str, amount: float) -> float:
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported geographic bridge operation {operation!r}")
    if operation == OP_ADD:
        return float(amount)
    if operation == OP_SUBTRACT:
        return -float(amount)
    raise ValueError(f"unsupported geographic bridge operation {operation!r}")


def _signed_contributions(
    snapshot: HistoricalSegmentPeriod,
) -> tuple[tuple[str, float], ...]:
    ordered: list[tuple[str, float]] = []
    for identity in sorted(snapshot.bridge_operations):
        operation = snapshot.bridge_operations[identity]
        if identity not in snapshot.values:
            raise ValueError(
                f"geographic bridge operation {identity} missing a reported value "
                f"for {snapshot.period.isoformat()}"
            )
        ordered.append(
            (identity, _signed_amount(operation, float(snapshot.values[identity])))
        )
    return tuple(ordered)


def _opening_growth() -> dict[str, None]:
    return {name: None for name in SEGMENTS}


def _unavailable_growth() -> dict[str, str]:
    return {name: SOURCE_UNAVAILABLE for name in SEGMENTS}


def _growth(
    current: dict[str, float],
    prior: dict[str, float] | None,
    *,
    opening: bool,
) -> dict[str, float | str | None]:
    if opening:
        return _opening_growth()
    if prior is None:
        return _unavailable_growth()
    return {
        name: ratio_or_na(current[name] - prior[name], prior[name]) for name in SEGMENTS
    }


def compute_geographic_segment_series(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> GeographicSegmentSeries:
    """Compute mix, growth, reported operating margins, and consolidated bridges."""
    if not geographic_segment_applicable(financials):
        raise MissingLineError("geographic segment sources not available")

    validate_historical_segment(financials)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError("geographic segment series must use the canonical fiscal axis")

    snapshots = _snapshot_index(financials)
    presentation_family: dict[date, str] = {}
    net_revenue: dict[date, dict[str, float | str]] = {}
    income_from_operations: dict[date, dict[str, float | str]] = {}
    revenue_share: dict[date, dict[str, float | str]] = {}
    revenue_growth: dict[date, dict[str, float | str | None]] = {}
    reported_operating_margin: dict[date, dict[str, float | str]] = {}
    calculated_segment_revenue_total: dict[date, float | str] = {}
    calculated_segment_operating_profit_total: dict[date, float | str] = {}
    signed_reconciling_contributions: dict[
        date, tuple[tuple[str, float], ...] | str
    ] = {}
    reconstructed_consolidated_operating_profit: dict[date, float | str] = {}
    reported_consolidated_revenue: dict[date, float | str] = {}
    reported_consolidated_operating_profit: dict[date, float | str] = {}
    consolidated_revenue_difference: dict[date, float | str] = {}
    consolidated_operating_profit_difference: dict[date, float | str] = {}

    prior_revenue: dict[str, float] | None = None
    for index, period in enumerate(axis):
        snapshot = snapshots.get(period)
        opening = index == 0
        if snapshot is None:
            presentation_family[period] = SOURCE_UNAVAILABLE
            net_revenue[period] = dict(_UNAVAILABLE_SEGMENTS)
            income_from_operations[period] = dict(_UNAVAILABLE_SEGMENTS)
            revenue_share[period] = dict(_UNAVAILABLE_SEGMENTS)
            revenue_growth[period] = (
                _opening_growth() if opening else _unavailable_growth()
            )
            reported_operating_margin[period] = dict(_UNAVAILABLE_SEGMENTS)
            calculated_segment_revenue_total[period] = SOURCE_UNAVAILABLE
            calculated_segment_operating_profit_total[period] = SOURCE_UNAVAILABLE
            signed_reconciling_contributions[period] = SOURCE_UNAVAILABLE
            reconstructed_consolidated_operating_profit[period] = SOURCE_UNAVAILABLE
            reported_consolidated_revenue[period] = SOURCE_UNAVAILABLE
            reported_consolidated_operating_profit[period] = SOURCE_UNAVAILABLE
            consolidated_revenue_difference[period] = SOURCE_UNAVAILABLE
            consolidated_operating_profit_difference[period] = SOURCE_UNAVAILABLE
            prior_revenue = None
            continue

        revenue = _segment_amounts(snapshot, REVENUE_SEGMENTS)
        operating_profit = _segment_amounts(snapshot, IFOP_SEGMENTS)
        consolidated_revenue = float(snapshot.values[REVENUE_CONSOLIDATED])
        consolidated_operating_profit = float(snapshot.values[IFOP_CONSOLIDATED])
        revenue_total = sum(revenue[name] for name in SEGMENTS)
        operating_total = sum(operating_profit[name] for name in SEGMENTS)
        contributions = _signed_contributions(snapshot)
        reconstructed = operating_total + sum(amount for _, amount in contributions)

        presentation_family[period] = snapshot.presentation_family
        net_revenue[period] = dict(revenue)
        income_from_operations[period] = dict(operating_profit)
        revenue_share[period] = {
            name: ratio_or_na(revenue[name], consolidated_revenue) for name in SEGMENTS
        }
        revenue_growth[period] = _growth(revenue, prior_revenue, opening=opening)
        reported_operating_margin[period] = {
            name: ratio_or_na(operating_profit[name], revenue[name]) for name in SEGMENTS
        }
        calculated_segment_revenue_total[period] = revenue_total
        calculated_segment_operating_profit_total[period] = operating_total
        signed_reconciling_contributions[period] = contributions
        reconstructed_consolidated_operating_profit[period] = reconstructed
        reported_consolidated_revenue[period] = consolidated_revenue
        reported_consolidated_operating_profit[period] = consolidated_operating_profit
        consolidated_revenue_difference[period] = revenue_total - consolidated_revenue
        consolidated_operating_profit_difference[period] = (
            reconstructed - consolidated_operating_profit
        )
        prior_revenue = revenue

    return GeographicSegmentSeries(
        periods=tuple(axis),
        identities=SEGMENTS,
        presentation_family=presentation_family,
        net_revenue=net_revenue,
        income_from_operations=income_from_operations,
        revenue_share=revenue_share,
        revenue_growth=revenue_growth,
        reported_operating_margin=reported_operating_margin,
        calculated_segment_revenue_total=calculated_segment_revenue_total,
        calculated_segment_operating_profit_total=calculated_segment_operating_profit_total,
        signed_reconciling_contributions=signed_reconciling_contributions,
        reconstructed_consolidated_operating_profit=reconstructed_consolidated_operating_profit,
        reported_consolidated_revenue=reported_consolidated_revenue,
        reported_consolidated_operating_profit=reported_consolidated_operating_profit,
        consolidated_revenue_difference=consolidated_revenue_difference,
        consolidated_operating_profit_difference=consolidated_operating_profit_difference,
    )
