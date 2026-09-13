"""Historical goodwill / intangible-asset intensity & change diagnostics (Step 9M.5).

Optional, source-gated module. Resolves BS balances and optional CF payments via
explicit concept only. Does not invent acquisition cash, goodwill impairment
attribution, or acquired-vs-internally-developed splits.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value

_CONCEPT_GOODWILL = "goodwill"
_CONCEPT_INTANGIBLES = "intangible_assets"
_CONCEPT_PAYMENTS = "payments_for_intangible_assets"


@dataclass(frozen=True)
class GoodwillIntangiblesAvailability:
    goodwill: bool
    intangible_assets: bool
    goodwill_and_intangibles: bool
    payments_for_intangible_assets: bool


@dataclass(frozen=True)
class GoodwillIntangiblesSources:
    goodwill: LineItem | None
    intangible_assets: LineItem | None
    payments_for_intangible_assets: LineItem | None


@dataclass(frozen=True)
class _BalanceFamilySeries:
    level: tuple[float, ...]
    change: tuple[float | None, ...]
    growth: tuple[float | str | None, ...]
    average: tuple[float | None, ...]
    to_revenue: tuple[float | str | None, ...]


@dataclass(frozen=True)
class GoodwillIntangiblesSeries:
    goodwill: _BalanceFamilySeries | None
    intangible_assets: _BalanceFamilySeries | None
    goodwill_and_intangibles: _BalanceFamilySeries | None
    payments_reported: tuple[float, ...] | None
    intangible_payments: tuple[float, ...] | None
    intangible_payments_to_revenue: tuple[float | str, ...] | None


def _try_resolve(items: list[LineItem], concept: str):
    try:
        return resolve_line(items, concept, required=False)
    except AmbiguousLineError:
        return "ambiguous"


def resolve_goodwill_intangibles_sources(
    financials: StandardizedFinancials,
) -> GoodwillIntangiblesSources:
    """Resolve optional GW / intangibles / payment lines independently."""
    gw = _try_resolve(financials.balance_sheet, _CONCEPT_GOODWILL)
    ia = _try_resolve(financials.balance_sheet, _CONCEPT_INTANGIBLES)
    pay = _try_resolve(financials.cash_flow, _CONCEPT_PAYMENTS)
    return GoodwillIntangiblesSources(
        goodwill=None if gw == "ambiguous" or gw.item is None else gw.item,
        intangible_assets=None if ia == "ambiguous" or ia.item is None else ia.item,
        payments_for_intangible_assets=(
            None if pay == "ambiguous" or pay.item is None else pay.item
        ),
    )


def goodwill_intangibles_availability(
    financials: StandardizedFinancials,
) -> GoodwillIntangiblesAvailability:
    """Report which balance / payment families can emit independently."""
    sources = resolve_goodwill_intangibles_sources(financials)
    gw = sources.goodwill is not None
    ia = sources.intangible_assets is not None
    return GoodwillIntangiblesAvailability(
        goodwill=gw,
        intangible_assets=ia,
        goodwill_and_intangibles=gw and ia,
        payments_for_intangible_assets=sources.payments_for_intangible_assets is not None,
    )


def goodwill_intangibles_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when at least one BS goodwill/intangibles concept resolves."""
    availability = goodwill_intangibles_availability(financials)
    return availability.goodwill or availability.intangible_assets


def _balance_family_series(
    levels: tuple[float, ...],
    revenue: tuple[float, ...],
) -> _BalanceFamilySeries:
    n = len(levels)
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
    return _BalanceFamilySeries(
        level=levels,
        change=tuple(change),
        growth=tuple(growth),
        average=tuple(average),
        to_revenue=tuple(to_revenue),
    )


def compute_goodwill_intangibles_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> GoodwillIntangiblesSeries:
    """Compute gated goodwill / intangible diagnostics for modeled periods."""
    if not goodwill_intangibles_applicable(financials):
        raise MissingLineError("goodwill / intangible-asset balances not available")

    sources = resolve_goodwill_intangibles_sources(financials)
    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "goodwill-intangibles period axis must match AnchorMetrics historical "
            "revenue length"
        )

    gw_series = None
    if sources.goodwill is not None:
        gw_levels = tuple(
            required_period_value(sources.goodwill, period, field=_CONCEPT_GOODWILL)
            for period in periods
        )
        gw_series = _balance_family_series(gw_levels, revenue)

    ia_series = None
    if sources.intangible_assets is not None:
        ia_levels = tuple(
            required_period_value(
                sources.intangible_assets, period, field=_CONCEPT_INTANGIBLES
            )
            for period in periods
        )
        ia_series = _balance_family_series(ia_levels, revenue)

    combined = None
    if gw_series is not None and ia_series is not None:
        combined_levels = tuple(
            gw_series.level[j] + ia_series.level[j] for j in range(n)
        )
        combined = _balance_family_series(combined_levels, revenue)

    payments_reported = None
    intangible_payments = None
    payments_to_revenue = None
    if sources.payments_for_intangible_assets is not None:
        payments_reported = tuple(
            required_period_value(
                sources.payments_for_intangible_assets,
                period,
                field=_CONCEPT_PAYMENTS,
            )
            for period in periods
        )
        # Present as −reported consistently (outflow magnitude when reported negative).
        intangible_payments = tuple(-v for v in payments_reported)
        payments_to_revenue = tuple(
            ratio_or_na(intangible_payments[j], revenue[j]) for j in range(n)
        )

    return GoodwillIntangiblesSeries(
        goodwill=gw_series,
        intangible_assets=ia_series,
        goodwill_and_intangibles=combined,
        payments_reported=payments_reported,
        intangible_payments=intangible_payments,
        intangible_payments_to_revenue=payments_to_revenue,
    )
