"""Historical deferred-tax balance diagnostics (Step 9M.7).

Optional, source-gated module. Resolves BS ``deferred_tax_assets`` and
``deferred_tax_liabilities`` through the shared line-resolver contract
(canonical concepts plus explicit-concept aliases ``deferred_tax_asset``
and ``deferred_tax_liability``). Stored concepts, values, signs, and
provenance are left unchanged. Requires both sources; missing or
ambiguous sources omit the entire module. Preserves reported signs. Does
not infer deferred-tax expense, cash-tax effects, recoverability, or
legal offset eligibility. Label-only inputs remain unsupported.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .source_values import required_period_value

_CONCEPT_DTA = "deferred_tax_assets"
_CONCEPT_DTL = "deferred_tax_liabilities"


@dataclass(frozen=True)
class DeferredTaxAvailability:
    deferred_tax_assets: bool
    deferred_tax_liabilities: bool
    ambiguous: bool


@dataclass(frozen=True)
class DeferredTaxSources:
    deferred_tax_assets: LineItem
    deferred_tax_liabilities: LineItem


@dataclass(frozen=True)
class DeferredTaxSeries:
    deferred_tax_assets: tuple[float, ...]
    deferred_tax_liabilities: tuple[float, ...]
    net_deferred_tax_position: tuple[float, ...]
    deferred_tax_assets_change: tuple[float | None, ...]
    deferred_tax_liabilities_change: tuple[float | None, ...]
    net_deferred_tax_position_change: tuple[float | None, ...]


def _try_resolve(items: list[LineItem], concept: str):
    try:
        return resolve_line(items, concept, required=False)
    except AmbiguousLineError:
        return "ambiguous"


def deferred_tax_availability(
    financials: StandardizedFinancials,
) -> DeferredTaxAvailability:
    """Report whether unique DTA and DTL lines resolve."""
    dta = _try_resolve(financials.balance_sheet, _CONCEPT_DTA)
    dtl = _try_resolve(financials.balance_sheet, _CONCEPT_DTL)
    ambiguous = dta == "ambiguous" or dtl == "ambiguous"
    return DeferredTaxAvailability(
        deferred_tax_assets=(
            False if dta == "ambiguous" or dta.item is None else True
        ),
        deferred_tax_liabilities=(
            False if dtl == "ambiguous" or dtl.item is None else True
        ),
        ambiguous=ambiguous,
    )


def resolve_deferred_tax_sources(
    financials: StandardizedFinancials,
) -> DeferredTaxSources | None:
    """Return both unique resolved DTA/DTL lines, or None if unavailable."""
    availability = deferred_tax_availability(financials)
    if (
        availability.ambiguous
        or not availability.deferred_tax_assets
        or not availability.deferred_tax_liabilities
    ):
        return None
    dta = resolve_line(financials.balance_sheet, _CONCEPT_DTA, required=True).item
    dtl = resolve_line(financials.balance_sheet, _CONCEPT_DTL, required=True).item
    assert dta is not None and dtl is not None
    return DeferredTaxSources(
        deferred_tax_assets=dta,
        deferred_tax_liabilities=dtl,
    )


def deferred_tax_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when both unique DTA and DTL lines resolve."""
    return resolve_deferred_tax_sources(financials) is not None


def compute_deferred_tax_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> DeferredTaxSeries:
    """Compute net deferred-tax position and period changes for modeled periods."""
    sources = resolve_deferred_tax_sources(financials)
    if sources is None:
        raise MissingLineError("deferred-tax balance sources not available")

    dta_levels = tuple(
        required_period_value(
            sources.deferred_tax_assets, period, field=_CONCEPT_DTA
        )
        for period in periods
    )
    dtl_levels = tuple(
        required_period_value(
            sources.deferred_tax_liabilities, period, field=_CONCEPT_DTL
        )
        for period in periods
    )
    net = tuple(dta - dtl for dta, dtl in zip(dta_levels, dtl_levels))

    n = len(periods)
    dta_change: list[float | None] = [None]
    dtl_change: list[float | None] = [None]
    net_change: list[float | None] = [None]
    for j in range(1, n):
        dta_change.append(dta_levels[j] - dta_levels[j - 1])
        dtl_change.append(dtl_levels[j] - dtl_levels[j - 1])
        net_change.append(net[j] - net[j - 1])

    return DeferredTaxSeries(
        deferred_tax_assets=dta_levels,
        deferred_tax_liabilities=dtl_levels,
        net_deferred_tax_position=net,
        deferred_tax_assets_change=tuple(dta_change),
        deferred_tax_liabilities_change=tuple(dtl_change),
        net_deferred_tax_position_change=tuple(net_change),
    )
