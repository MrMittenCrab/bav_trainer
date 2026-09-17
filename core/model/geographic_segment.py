"""Source-supported historical geographic segment analytical series.

Optional, source-gated module. Consumes only ``StandardizedFinancials.historical_segment``
after existing contract validation. Missing or null payloads make the module
absent. Missing snapshots on an otherwise valid canonical fiscal axis yield
``SOURCE_UNAVAILABLE`` only for dependent outputs; gaps are never compressed
and another period is never substituted.

Computes each Americas / China Mainland / Rest of World segment's revenue share
of consolidated revenue, adjacent-period revenue growth, reported operating
margin ``income_from_operations / net_revenue``, percentage-point
contributions to consolidated revenue growth, an arithmetic decomposition
of consolidated reported operating margin, a separate midpoint mix and
within-segment decomposition of the adjacent change in that margin, and an
adjacent operating-profit amount-change bridge. Reported operating margin is
not BAV NOPAT margin. Revenue-growth contributions are an arithmetic
decomposition of reported geographic revenue changes, not organic,
constant-currency, or causal growth. Operating-margin contributions use
consolidated revenue as the denominator and remain a direct contribution
bridge, distinct from the mix/within-segment decomposition, the monetary
amount-change bridge, normalization, or causal attribution. Amount changes
are current minus immediately prior reported operating profit, with no
revenue denominator; zero revenue does not suppress available profit changes.

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
from .ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable, ratio_or_na

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
    revenue_growth_contribution: dict[date, dict[str, float | str | None]]
    consolidated_revenue_growth: dict[date, float | str | None]
    revenue_growth_contribution_residual: dict[date, float | str | None]
    reported_operating_margin: dict[date, dict[str, float | str]]
    operating_margin_contribution: dict[date, dict[str, float | str]]
    reconciling_operating_margin_contribution: dict[date, float | str]
    consolidated_operating_margin: dict[date, float | str]
    operating_margin_contribution_residual: dict[date, float | str]
    operating_margin_contribution_change: dict[date, dict[str, float | str | None]]
    reconciling_operating_margin_contribution_change: dict[date, float | str | None]
    consolidated_operating_margin_change: dict[date, float | str | None]
    operating_margin_contribution_change_residual: dict[date, float | str | None]
    operating_margin_mix_effect: dict[date, dict[str, float | str | None]]
    operating_margin_within_segment_effect: dict[date, dict[str, float | str | None]]
    operating_margin_mix_within_residual: dict[date, float | str | None]
    operating_profit_amount_change: dict[date, dict[str, float | str | None]]
    reconciling_operating_profit_amount_change: dict[date, float | str | None]
    consolidated_operating_profit_amount_change: dict[date, float | str | None]
    operating_profit_amount_change_residual: dict[date, float | str | None]
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


def _percentage_points(numerator: float, denominator: float) -> float | str:
    ratio = ratio_or_na(numerator, denominator)
    if isinstance(ratio, str):
        return ratio
    return 100.0 * ratio


def _opening_contributions() -> dict[str, None]:
    return {name: None for name in SEGMENTS}


def _unavailable_contributions() -> dict[str, str]:
    return {name: SOURCE_UNAVAILABLE for name in SEGMENTS}


def _growth_contributions(
    current: dict[str, float],
    prior: dict[str, float] | None,
    prior_consolidated: float | None,
    *,
    opening: bool,
) -> dict[str, float | str | None]:
    if opening:
        return _opening_contributions()
    if prior is None or prior_consolidated is None:
        return _unavailable_contributions()
    return {
        name: _percentage_points(current[name] - prior[name], prior_consolidated)
        for name in SEGMENTS
    }


def _consolidated_growth(
    current_consolidated: float,
    prior_consolidated: float | None,
    *,
    opening: bool,
) -> float | str | None:
    if opening:
        return None
    if prior_consolidated is None:
        return SOURCE_UNAVAILABLE
    return ratio_or_na(current_consolidated - prior_consolidated, prior_consolidated)


def _contribution_residual(
    consolidated_growth: float | str | None,
    contributions: dict[str, float | str | None],
) -> float | str | None:
    if consolidated_growth is None:
        return None
    if is_source_unavailable(consolidated_growth) or any(
        is_source_unavailable(value) for value in contributions.values()
    ):
        return SOURCE_UNAVAILABLE
    if consolidated_growth == UNDEFINED_RATIO or any(
        value == UNDEFINED_RATIO for value in contributions.values()
    ):
        return UNDEFINED_RATIO
    return 100.0 * float(consolidated_growth) - sum(
        float(contributions[name]) for name in SEGMENTS
    )


def _margin_bridge_residual(
    margin: float | str,
    contributions: dict[str, float | str],
    reconciling: float | str,
) -> float | str:
    if (
        is_source_unavailable(margin)
        or is_source_unavailable(reconciling)
        or any(is_source_unavailable(value) for value in contributions.values())
    ):
        return SOURCE_UNAVAILABLE
    if (
        margin == UNDEFINED_RATIO
        or reconciling == UNDEFINED_RATIO
        or any(value == UNDEFINED_RATIO for value in contributions.values())
    ):
        return UNDEFINED_RATIO
    return (
        float(margin)
        - sum(float(contributions[name]) for name in SEGMENTS)
        - float(reconciling)
    )


def _adjacent_delta(
    current: float | str | None,
    prior: float | str | None,
    *,
    opening: bool,
) -> float | str | None:
    if opening:
        return None
    if (
        current is None
        or prior is None
        or is_source_unavailable(current)
        or is_source_unavailable(prior)
    ):
        return SOURCE_UNAVAILABLE
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _adjacent_delta_map(
    current: dict[str, float | str],
    prior: dict[str, float | str] | None,
    *,
    opening: bool,
) -> dict[str, float | str | None]:
    if opening:
        return _opening_contributions()
    if prior is None:
        return _unavailable_contributions()
    return {
        name: _adjacent_delta(current[name], prior[name], opening=False)
        for name in SEGMENTS
    }


def _mix_within_status(
    current_share: float | str,
    prior_share: float | str | None,
    current_margin: float | str,
    prior_margin: float | str | None,
    *,
    opening: bool,
) -> str | None:
    if opening:
        return "opening"
    values = (current_share, prior_share, current_margin, prior_margin)
    if any(value is None or is_source_unavailable(value) for value in values):
        return SOURCE_UNAVAILABLE
    if any(value == UNDEFINED_RATIO for value in values):
        return UNDEFINED_RATIO
    return None


def _mix_effect(
    current_share: float | str,
    prior_share: float | str | None,
    current_margin: float | str,
    prior_margin: float | str | None,
    *,
    opening: bool,
) -> float | str | None:
    status = _mix_within_status(
        current_share,
        prior_share,
        current_margin,
        prior_margin,
        opening=opening,
    )
    if status == "opening":
        return None
    if status is not None:
        return status
    return (
        100.0
        * (float(current_share) - float(prior_share))
        * (float(current_margin) + float(prior_margin))
        / 2.0
    )


def _within_segment_effect(
    current_share: float | str,
    prior_share: float | str | None,
    current_margin: float | str,
    prior_margin: float | str | None,
    *,
    opening: bool,
) -> float | str | None:
    status = _mix_within_status(
        current_share,
        prior_share,
        current_margin,
        prior_margin,
        opening=opening,
    )
    if status == "opening":
        return None
    if status is not None:
        return status
    return (
        100.0
        * (float(current_margin) - float(prior_margin))
        * (float(current_share) + float(prior_share))
        / 2.0
    )


def _mix_within_map(
    current_share: dict[str, float | str],
    prior_share: dict[str, float | str] | None,
    current_margin: dict[str, float | str],
    prior_margin: dict[str, float | str] | None,
    *,
    opening: bool,
    kind: str,
) -> dict[str, float | str | None]:
    if opening:
        return _opening_contributions()
    if prior_share is None or prior_margin is None:
        return _unavailable_contributions()
    compute = _mix_effect if kind == "mix" else _within_segment_effect
    return {
        name: compute(
            current_share[name],
            prior_share[name],
            current_margin[name],
            prior_margin[name],
            opening=False,
        )
        for name in SEGMENTS
    }


def _mix_within_residual(
    margin_change: float | str | None,
    mix_effects: dict[str, float | str | None],
    within_effects: dict[str, float | str | None],
    reconciling_change: float | str | None,
) -> float | str | None:
    if margin_change is None:
        return None
    values = (
        margin_change,
        reconciling_change,
        *mix_effects.values(),
        *within_effects.values(),
    )
    if any(value is None or is_source_unavailable(value) for value in values):
        return SOURCE_UNAVAILABLE
    if any(value == UNDEFINED_RATIO for value in values):
        return UNDEFINED_RATIO
    return (
        float(margin_change)
        - sum(float(mix_effects[name]) for name in SEGMENTS)
        - sum(float(within_effects[name]) for name in SEGMENTS)
        - float(reconciling_change)
    )


def _margin_change_residual(
    margin_change: float | str | None,
    contribution_changes: dict[str, float | str | None],
    reconciling_change: float | str | None,
) -> float | str | None:
    if margin_change is None:
        return None
    if (
        is_source_unavailable(margin_change)
        or reconciling_change is None
        or is_source_unavailable(reconciling_change)
        or any(
            value is None or is_source_unavailable(value)
            for value in contribution_changes.values()
        )
    ):
        return SOURCE_UNAVAILABLE
    if (
        margin_change == UNDEFINED_RATIO
        or reconciling_change == UNDEFINED_RATIO
        or any(value == UNDEFINED_RATIO for value in contribution_changes.values())
    ):
        return UNDEFINED_RATIO
    return (
        float(margin_change)
        - sum(float(contribution_changes[name]) for name in SEGMENTS)
        - float(reconciling_change)
    )


def _reconciling_sum(
    contributions: tuple[tuple[str, float], ...] | str,
) -> float | str:
    if isinstance(contributions, str):
        return contributions
    return sum(amount for _, amount in contributions)


def compute_geographic_segment_series(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> GeographicSegmentSeries:
    """Compute mix, growth, margins, contributions, mix/within, and amount bridges."""
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
    revenue_growth_contribution: dict[date, dict[str, float | str | None]] = {}
    consolidated_revenue_growth: dict[date, float | str | None] = {}
    revenue_growth_contribution_residual: dict[date, float | str | None] = {}
    reported_operating_margin: dict[date, dict[str, float | str]] = {}
    operating_margin_contribution: dict[date, dict[str, float | str]] = {}
    reconciling_operating_margin_contribution: dict[date, float | str] = {}
    consolidated_operating_margin: dict[date, float | str] = {}
    operating_margin_contribution_residual: dict[date, float | str] = {}
    operating_margin_contribution_change: dict[date, dict[str, float | str | None]] = {}
    reconciling_operating_margin_contribution_change: dict[date, float | str | None] = {}
    consolidated_operating_margin_change: dict[date, float | str | None] = {}
    operating_margin_contribution_change_residual: dict[date, float | str | None] = {}
    operating_margin_mix_effect: dict[date, dict[str, float | str | None]] = {}
    operating_margin_within_segment_effect: dict[date, dict[str, float | str | None]] = {}
    operating_margin_mix_within_residual: dict[date, float | str | None] = {}
    operating_profit_amount_change: dict[date, dict[str, float | str | None]] = {}
    reconciling_operating_profit_amount_change: dict[date, float | str | None] = {}
    consolidated_operating_profit_amount_change: dict[date, float | str | None] = {}
    operating_profit_amount_change_residual: dict[date, float | str | None] = {}
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
    prior_consolidated: float | None = None
    prior_operating_profit: dict[str, float] | None = None
    prior_consolidated_ifop: float | None = None
    prior_reconciling_sum: float | None = None
    prior_margin_contrib: dict[str, float | str] | None = None
    prior_reconciling_contrib: float | str | None = None
    prior_consolidated_margin: float | str | None = None
    prior_share: dict[str, float | str] | None = None
    prior_segment_margin: dict[str, float | str] | None = None
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
            revenue_growth_contribution[period] = (
                _opening_contributions() if opening else _unavailable_contributions()
            )
            consolidated_revenue_growth[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            revenue_growth_contribution_residual[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            reported_operating_margin[period] = dict(_UNAVAILABLE_SEGMENTS)
            operating_margin_contribution[period] = dict(_UNAVAILABLE_SEGMENTS)
            reconciling_operating_margin_contribution[period] = SOURCE_UNAVAILABLE
            consolidated_operating_margin[period] = SOURCE_UNAVAILABLE
            operating_margin_contribution_residual[period] = SOURCE_UNAVAILABLE
            operating_margin_contribution_change[period] = (
                _opening_contributions() if opening else _unavailable_contributions()
            )
            reconciling_operating_margin_contribution_change[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            consolidated_operating_margin_change[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            operating_margin_contribution_change_residual[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            operating_margin_mix_effect[period] = (
                _opening_contributions() if opening else _unavailable_contributions()
            )
            operating_margin_within_segment_effect[period] = (
                _opening_contributions() if opening else _unavailable_contributions()
            )
            operating_margin_mix_within_residual[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            operating_profit_amount_change[period] = (
                _opening_contributions() if opening else _unavailable_contributions()
            )
            reconciling_operating_profit_amount_change[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            consolidated_operating_profit_amount_change[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            operating_profit_amount_change_residual[period] = (
                None if opening else SOURCE_UNAVAILABLE
            )
            calculated_segment_revenue_total[period] = SOURCE_UNAVAILABLE
            calculated_segment_operating_profit_total[period] = SOURCE_UNAVAILABLE
            signed_reconciling_contributions[period] = SOURCE_UNAVAILABLE
            reconstructed_consolidated_operating_profit[period] = SOURCE_UNAVAILABLE
            reported_consolidated_revenue[period] = SOURCE_UNAVAILABLE
            reported_consolidated_operating_profit[period] = SOURCE_UNAVAILABLE
            consolidated_revenue_difference[period] = SOURCE_UNAVAILABLE
            consolidated_operating_profit_difference[period] = SOURCE_UNAVAILABLE
            prior_revenue = None
            prior_consolidated = None
            prior_operating_profit = None
            prior_consolidated_ifop = None
            prior_reconciling_sum = None
            prior_margin_contrib = None
            prior_reconciling_contrib = None
            prior_consolidated_margin = None
            prior_share = None
            prior_segment_margin = None
            continue

        revenue = _segment_amounts(snapshot, REVENUE_SEGMENTS)
        operating_profit = _segment_amounts(snapshot, IFOP_SEGMENTS)
        consolidated_revenue = float(snapshot.values[REVENUE_CONSOLIDATED])
        consolidated_operating_profit = float(snapshot.values[IFOP_CONSOLIDATED])
        revenue_total = sum(revenue[name] for name in SEGMENTS)
        operating_total = sum(operating_profit[name] for name in SEGMENTS)
        contributions = _signed_contributions(snapshot)
        reconstructed = operating_total + sum(amount for _, amount in contributions)
        growth_contributions = _growth_contributions(
            revenue,
            prior_revenue,
            prior_consolidated,
            opening=opening,
        )
        cons_growth = _consolidated_growth(
            consolidated_revenue,
            prior_consolidated,
            opening=opening,
        )
        margin_contrib = {
            name: _percentage_points(operating_profit[name], consolidated_revenue)
            for name in SEGMENTS
        }
        reconciling_contrib = _percentage_points(
            sum(amount for _, amount in contributions),
            consolidated_revenue,
        )
        cons_margin = _percentage_points(
            consolidated_operating_profit,
            consolidated_revenue,
        )
        margin_residual = _margin_bridge_residual(
            cons_margin,
            margin_contrib,
            reconciling_contrib,
        )
        margin_contrib_change = _adjacent_delta_map(
            margin_contrib,
            prior_margin_contrib,
            opening=opening,
        )
        reconciling_change = _adjacent_delta(
            reconciling_contrib,
            prior_reconciling_contrib,
            opening=opening,
        )
        cons_margin_change = _adjacent_delta(
            cons_margin,
            prior_consolidated_margin,
            opening=opening,
        )
        margin_change_residual = _margin_change_residual(
            cons_margin_change,
            margin_contrib_change,
            reconciling_change,
        )
        shares = {
            name: ratio_or_na(revenue[name], consolidated_revenue) for name in SEGMENTS
        }
        segment_margins = {
            name: ratio_or_na(operating_profit[name], revenue[name]) for name in SEGMENTS
        }
        mix_effects = _mix_within_map(
            shares,
            prior_share,
            segment_margins,
            prior_segment_margin,
            opening=opening,
            kind="mix",
        )
        within_effects = _mix_within_map(
            shares,
            prior_share,
            segment_margins,
            prior_segment_margin,
            opening=opening,
            kind="within",
        )
        mix_within_residual = _mix_within_residual(
            cons_margin_change,
            mix_effects,
            within_effects,
            reconciling_change,
        )
        recon_sum = _reconciling_sum(contributions)
        profit_amount_change = _adjacent_delta_map(
            operating_profit,
            prior_operating_profit,
            opening=opening,
        )
        reconciling_amount_change = _adjacent_delta(
            recon_sum,
            prior_reconciling_sum,
            opening=opening,
        )
        cons_profit_amount_change = _adjacent_delta(
            consolidated_operating_profit,
            prior_consolidated_ifop,
            opening=opening,
        )
        profit_amount_change_residual = _margin_change_residual(
            cons_profit_amount_change,
            profit_amount_change,
            reconciling_amount_change,
        )

        presentation_family[period] = snapshot.presentation_family
        net_revenue[period] = dict(revenue)
        income_from_operations[period] = dict(operating_profit)
        revenue_share[period] = shares
        revenue_growth[period] = _growth(revenue, prior_revenue, opening=opening)
        revenue_growth_contribution[period] = growth_contributions
        consolidated_revenue_growth[period] = cons_growth
        revenue_growth_contribution_residual[period] = _contribution_residual(
            cons_growth,
            growth_contributions,
        )
        reported_operating_margin[period] = segment_margins
        operating_margin_contribution[period] = margin_contrib
        reconciling_operating_margin_contribution[period] = reconciling_contrib
        consolidated_operating_margin[period] = cons_margin
        operating_margin_contribution_residual[period] = margin_residual
        operating_margin_contribution_change[period] = margin_contrib_change
        reconciling_operating_margin_contribution_change[period] = reconciling_change
        consolidated_operating_margin_change[period] = cons_margin_change
        operating_margin_contribution_change_residual[period] = margin_change_residual
        operating_margin_mix_effect[period] = mix_effects
        operating_margin_within_segment_effect[period] = within_effects
        operating_margin_mix_within_residual[period] = mix_within_residual
        operating_profit_amount_change[period] = profit_amount_change
        reconciling_operating_profit_amount_change[period] = reconciling_amount_change
        consolidated_operating_profit_amount_change[period] = cons_profit_amount_change
        operating_profit_amount_change_residual[period] = profit_amount_change_residual
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
        prior_consolidated = consolidated_revenue
        prior_operating_profit = operating_profit
        prior_consolidated_ifop = consolidated_operating_profit
        prior_reconciling_sum = float(recon_sum)
        prior_margin_contrib = margin_contrib
        prior_reconciling_contrib = reconciling_contrib
        prior_consolidated_margin = cons_margin
        prior_share = shares
        prior_segment_margin = segment_margins

    return GeographicSegmentSeries(
        periods=tuple(axis),
        identities=SEGMENTS,
        presentation_family=presentation_family,
        net_revenue=net_revenue,
        income_from_operations=income_from_operations,
        revenue_share=revenue_share,
        revenue_growth=revenue_growth,
        revenue_growth_contribution=revenue_growth_contribution,
        consolidated_revenue_growth=consolidated_revenue_growth,
        revenue_growth_contribution_residual=revenue_growth_contribution_residual,
        reported_operating_margin=reported_operating_margin,
        operating_margin_contribution=operating_margin_contribution,
        reconciling_operating_margin_contribution=reconciling_operating_margin_contribution,
        consolidated_operating_margin=consolidated_operating_margin,
        operating_margin_contribution_residual=operating_margin_contribution_residual,
        operating_margin_contribution_change=operating_margin_contribution_change,
        reconciling_operating_margin_contribution_change=(
            reconciling_operating_margin_contribution_change
        ),
        consolidated_operating_margin_change=consolidated_operating_margin_change,
        operating_margin_contribution_change_residual=(
            operating_margin_contribution_change_residual
        ),
        operating_margin_mix_effect=operating_margin_mix_effect,
        operating_margin_within_segment_effect=operating_margin_within_segment_effect,
        operating_margin_mix_within_residual=operating_margin_mix_within_residual,
        operating_profit_amount_change=operating_profit_amount_change,
        reconciling_operating_profit_amount_change=(
            reconciling_operating_profit_amount_change
        ),
        consolidated_operating_profit_amount_change=(
            consolidated_operating_profit_amount_change
        ),
        operating_profit_amount_change_residual=operating_profit_amount_change_residual,
        calculated_segment_revenue_total=calculated_segment_revenue_total,
        calculated_segment_operating_profit_total=calculated_segment_operating_profit_total,
        signed_reconciling_contributions=signed_reconciling_contributions,
        reconstructed_consolidated_operating_profit=reconstructed_consolidated_operating_profit,
        reported_consolidated_revenue=reported_consolidated_revenue,
        reported_consolidated_operating_profit=reported_consolidated_operating_profit,
        consolidated_revenue_difference=consolidated_revenue_difference,
        consolidated_operating_profit_difference=consolidated_operating_profit_difference,
    )
