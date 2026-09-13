"""Historical lease-liability intensity / trend diagnostics (Step 9L.1 / 9M.3A / 9M.3B).

Uses one uniquely resolvable aggregate lease-liability source line, or exactly
one ``lease_liability_current`` plus one ``lease_liability_noncurrent`` pair
summed period-by-period. Does not invent ROU assets, lease payments, discount
rates, or amortisation. Does not promote note aggregates or plug rounding gaps.

Step 9M.3B adds treatment resolution for disclosed lease interest: operating
treatment removes reported lease interest from financing net interest; financial
treatment leaves reported net interest unchanged; mixed treatment fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ..data.interface import LineItem, StandardizedFinancials
from .classification import BalanceSheetReformulation
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

if TYPE_CHECKING:
    from .financial_math import AnchorMetrics


class InconsistentLeaseTreatmentError(ValueError):
    """Resolved lease rows do not share one supported operating/financial treatment."""


@dataclass(frozen=True)
class LeaseLiabilityAvailability:
    lease_liability: bool
    ambiguous: bool


@dataclass(frozen=True)
class LeaseLiabilitySource:
    mode: str  # "aggregate" | "split"
    items: tuple[LineItem, ...]
    indices: tuple[int, ...]


@dataclass(frozen=True)
class LeaseLiabilitySeries:
    lease_liability: tuple[float, ...]
    lease_liability_to_revenue: tuple[float | str, ...]
    lease_liability_change: tuple[float | None, ...]
    lease_liability_growth: tuple[float | str | None, ...]


@dataclass(frozen=True)
class _LeaseResolveState:
    source: LeaseLiabilitySource | None
    ambiguous: bool


def _concept_key(item: LineItem) -> str:
    return (item.concept or "").strip().lower()


def _indices_with_concept(
    items: list[LineItem], concept: str
) -> list[tuple[int, LineItem]]:
    key = concept.strip().lower()
    return [(idx, item) for idx, item in enumerate(items) if _concept_key(item) == key]


def _resolve_lease_liability_state(
    financials: StandardizedFinancials,
) -> _LeaseResolveState:
    """Shared aggregate-or-split decision for availability, math, and workbooks."""
    bs = financials.balance_sheet
    aggregates = _indices_with_concept(bs, "lease_liability")
    currents = _indices_with_concept(bs, "lease_liability_current")
    noncurrents = _indices_with_concept(bs, "lease_liability_noncurrent")

    if len(aggregates) > 1:
        return _LeaseResolveState(source=None, ambiguous=True)
    if len(aggregates) == 1:
        idx, item = aggregates[0]
        return _LeaseResolveState(
            source=LeaseLiabilitySource(
                mode="aggregate",
                items=(item,),
                indices=(idx,),
            ),
            ambiguous=False,
        )

    if currents or noncurrents:
        if len(currents) > 1 or len(noncurrents) > 1:
            return _LeaseResolveState(source=None, ambiguous=True)
        if len(currents) == 1 and len(noncurrents) == 1:
            cur_idx, cur_item = currents[0]
            non_idx, non_item = noncurrents[0]
            return _LeaseResolveState(
                source=LeaseLiabilitySource(
                    mode="split",
                    items=(cur_item, non_item),
                    indices=(cur_idx, non_idx),
                ),
                ambiguous=False,
            )
        # Partial split: one side only — unavailable, not zero-filled.
        return _LeaseResolveState(source=None, ambiguous=False)

    # No explicit lease concepts — preserve legacy aggregate label-alias path.
    try:
        resolved = resolve_line(bs, "lease_liability", required=False)
    except AmbiguousLineError:
        return _LeaseResolveState(source=None, ambiguous=True)
    if resolved.item is None or resolved.index is None:
        return _LeaseResolveState(source=None, ambiguous=False)
    return _LeaseResolveState(
        source=LeaseLiabilitySource(
            mode="aggregate",
            items=(resolved.item,),
            indices=(resolved.index,),
        ),
        ambiguous=False,
    )


def resolve_lease_liability_source(
    financials: StandardizedFinancials,
) -> LeaseLiabilitySource | None:
    """Return the shared aggregate or split lease-liability source, if usable."""
    return _resolve_lease_liability_state(financials).source


def lease_liability_availability(
    financials: StandardizedFinancials,
) -> LeaseLiabilityAvailability:
    """Report whether a unique aggregate or valid current/non-current split resolves."""
    state = _resolve_lease_liability_state(financials)
    return LeaseLiabilityAvailability(
        lease_liability=state.source is not None,
        ambiguous=state.ambiguous,
    )


def lease_liability_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when a unique aggregate or valid split source resolves."""
    availability = lease_liability_availability(financials)
    return availability.lease_liability and not availability.ambiguous


def lease_liability_treatment(
    financials: StandardizedFinancials,
    reformulation: BalanceSheetReformulation,
) -> str | None:
    """Return 'operating', 'financial', or None; raise for mixed/unsupported treatment."""
    source = resolve_lease_liability_source(financials)
    if source is None:
        return None
    categories = {
        reformulation.decisions[idx].category for idx in source.indices
    }
    if categories == {"Operating Long-Term Liability"}:
        return "operating"
    if categories == {"Financial Liability"}:
        return "financial"
    raise InconsistentLeaseTreatmentError(
        "Resolved lease-liability rows do not share one supported "
        f"operating/financial treatment; categories={sorted(categories)}"
    )


def compute_lease_liability_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: "AnchorMetrics",
) -> LeaseLiabilitySeries:
    """Compute lease-liability intensity / change diagnostics for modeled periods."""
    source = resolve_lease_liability_source(financials)
    if source is None:
        raise MissingLineError("lease liability source not available")

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "lease-liability period axis must match AnchorMetrics historical "
            "revenue length"
        )

    lease_vals = tuple(
        sum(
            required_period_value(item, period, field="lease_liability")
            for item in source.items
        )
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
