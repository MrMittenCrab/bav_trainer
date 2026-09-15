"""Source-supported reported gross and operating-margin bridge.

Optional, source-gated module. Resolves unique explicit IS ``gross_profit`` and
``operating_profit`` / ``operating_income``, and uses existing revenue
resolution. Stored concepts, values, signs, and provenance are left unchanged.
No label fallback for profit lines, no competing-alias merge, and no
wrong-statement substitutes.

Computes ``gross_margin = gross_profit / revenue`` when unique gross profit and
revenue resolve. ``reported_operating_margin = operating_profit / revenue`` when
unique operating profit and revenue resolve. ``net_operating_expense_burden =
(gross_profit − operating_profit) / revenue`` when both unique profit lines and
revenue resolve. Adjacent-period families compute gross-margin change, burden
change, and reconstructed operating-margin change = gross-margin change −
burden change. Opening-period change exercises are omitted.

Absent or ambiguous sources omit only dependent families. Missing required
period values fail closed. Reported zeros remain valid. Zero revenue yields the
existing undefined-ratio result with downstream propagation. The reconstructed
change reconciles to the adjacent reported-operating-margin difference when
both sides are defined.

Do not infer price, mix, or cost causes, or normalized earnings. Reported
operating margin is distinct from BAV NOPAT margin. Gross profit minus
operating profit includes net intervening operating items; it is not
necessarily SG&A. A positive burden change reduces operating margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
from .source_values import required_period_value

GROSS_PROFIT_CONCEPT = "gross_profit"
OPERATING_PROFIT_CONCEPT = "operating_profit"
REVENUE_CONCEPT = "revenue"


@dataclass(frozen=True)
class ReportedMarginAvailability:
    revenue: bool
    revenue_ambiguous: bool
    gross_profit: bool
    gross_profit_ambiguous: bool
    operating_profit: bool
    operating_profit_ambiguous: bool


@dataclass(frozen=True)
class ReportedMarginSources:
    revenue: LineItem | None
    gross_profit: LineItem | None
    operating_profit: LineItem | None


@dataclass(frozen=True)
class ReportedMarginSeries:
    revenue: tuple[float, ...]
    gross_profit: tuple[float, ...] | None = None
    operating_profit: tuple[float, ...] | None = None
    gross_margin: tuple[float | str, ...] | None = None
    reported_operating_margin: tuple[float | str, ...] | None = None
    net_operating_expense_burden: tuple[float | str, ...] | None = None
    gross_margin_change: tuple[float | str | None, ...] | None = None
    net_operating_expense_burden_change: tuple[float | str | None, ...] | None = None
    reconstructed_operating_margin_change: tuple[float | str | None, ...] | None = (
        None
    )


def _resolve_unique_is(
    financials: StandardizedFinancials, concept: str
) -> tuple[LineItem | None, bool]:
    try:
        resolved = resolve_line(financials.income_statement, concept, required=False)
    except AmbiguousLineError:
        return None, True
    return resolved.item, False


def reported_margin_availability(
    financials: StandardizedFinancials,
) -> ReportedMarginAvailability:
    """Report unique IS source resolution without mutating rows."""
    revenue, revenue_ambiguous = _resolve_unique_is(financials, REVENUE_CONCEPT)
    gross_profit, gross_profit_ambiguous = _resolve_unique_is(
        financials, GROSS_PROFIT_CONCEPT
    )
    operating_profit, operating_profit_ambiguous = _resolve_unique_is(
        financials, OPERATING_PROFIT_CONCEPT
    )
    return ReportedMarginAvailability(
        revenue=revenue is not None,
        revenue_ambiguous=revenue_ambiguous,
        gross_profit=gross_profit is not None,
        gross_profit_ambiguous=gross_profit_ambiguous,
        operating_profit=operating_profit is not None,
        operating_profit_ambiguous=operating_profit_ambiguous,
    )


def resolve_reported_margin_sources(
    financials: StandardizedFinancials,
) -> ReportedMarginSources:
    """Return unique IS margin lines; ambiguous sources are None."""
    revenue, _ = _resolve_unique_is(financials, REVENUE_CONCEPT)
    gross_profit, _ = _resolve_unique_is(financials, GROSS_PROFIT_CONCEPT)
    operating_profit, _ = _resolve_unique_is(financials, OPERATING_PROFIT_CONCEPT)
    return ReportedMarginSources(
        revenue=revenue,
        gross_profit=gross_profit,
        operating_profit=operating_profit,
    )


def _revenue_ready(avail: ReportedMarginAvailability) -> bool:
    return avail.revenue and not avail.revenue_ambiguous


def gross_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Gross margin requires unique revenue and unique explicit gross profit."""
    avail = reported_margin_availability(financials)
    return (
        _revenue_ready(avail)
        and avail.gross_profit
        and not avail.gross_profit_ambiguous
    )


def reported_operating_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Reported operating margin requires unique revenue and unique operating profit."""
    avail = reported_margin_availability(financials)
    return (
        _revenue_ready(avail)
        and avail.operating_profit
        and not avail.operating_profit_ambiguous
    )


def net_operating_expense_burden_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Burden requires unique revenue plus unique gross and operating profit."""
    return gross_margin_applicable(financials) and reported_operating_margin_applicable(
        financials
    )


def gross_margin_change_applicable(financials: StandardizedFinancials) -> bool:
    return gross_margin_applicable(financials)


def net_operating_expense_burden_change_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return net_operating_expense_burden_applicable(financials)


def reconstructed_operating_margin_change_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return net_operating_expense_burden_applicable(financials)


def reported_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when at least one reported-margin family can be computed."""
    return gross_margin_applicable(financials) or reported_operating_margin_applicable(
        financials
    )


def _difference_or_na(
    current: float | str, prior: float | str
) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _adjacent_changes(
    levels: tuple[float | str, ...],
) -> tuple[float | str | None, ...]:
    n = len(levels)
    changes: list[float | str | None] = [None] * n
    for j in range(1, n):
        changes[j] = _difference_or_na(levels[j], levels[j - 1])
    return tuple(changes)


def compute_reported_margin_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> ReportedMarginSeries:
    """Read reported IS profits and compute margin-bridge diagnostics."""
    if not reported_margin_applicable(financials):
        raise MissingLineError("reported margin sources not available")

    sources = resolve_reported_margin_sources(financials)
    assert sources.revenue is not None
    revenue = tuple(
        required_period_value(sources.revenue, period, field=REVENUE_CONCEPT)
        for period in periods
    )

    gross_profit: tuple[float, ...] | None = None
    gross_margin: tuple[float | str, ...] | None = None
    if gross_margin_applicable(financials):
        assert sources.gross_profit is not None
        gross_profit = tuple(
            required_period_value(
                sources.gross_profit, period, field=GROSS_PROFIT_CONCEPT
            )
            for period in periods
        )
        gross_margin = tuple(
            ratio_or_na(gross_profit[j], revenue[j]) for j in range(len(periods))
        )

    operating_profit: tuple[float, ...] | None = None
    reported_operating_margin: tuple[float | str, ...] | None = None
    if reported_operating_margin_applicable(financials):
        assert sources.operating_profit is not None
        operating_profit = tuple(
            required_period_value(
                sources.operating_profit, period, field=OPERATING_PROFIT_CONCEPT
            )
            for period in periods
        )
        reported_operating_margin = tuple(
            ratio_or_na(operating_profit[j], revenue[j]) for j in range(len(periods))
        )

    net_operating_expense_burden: tuple[float | str, ...] | None = None
    if (
        net_operating_expense_burden_applicable(financials)
        and gross_profit is not None
        and operating_profit is not None
    ):
        net_operating_expense_burden = tuple(
            ratio_or_na(gross_profit[j] - operating_profit[j], revenue[j])
            for j in range(len(periods))
        )

    gross_margin_change: tuple[float | str | None, ...] | None = None
    if gross_margin is not None:
        gross_margin_change = _adjacent_changes(gross_margin)

    net_operating_expense_burden_change: tuple[float | str | None, ...] | None = None
    if net_operating_expense_burden is not None:
        net_operating_expense_burden_change = _adjacent_changes(
            net_operating_expense_burden
        )

    reconstructed_operating_margin_change: tuple[float | str | None, ...] | None = None
    if (
        reconstructed_operating_margin_change_applicable(financials)
        and gross_margin_change is not None
        and net_operating_expense_burden_change is not None
    ):
        reconstructed: list[float | str | None] = [None] * len(periods)
        for j in range(1, len(periods)):
            gm_delta = gross_margin_change[j]
            burden_delta = net_operating_expense_burden_change[j]
            assert gm_delta is not None
            assert burden_delta is not None
            reconstructed[j] = _difference_or_na(gm_delta, burden_delta)
        reconstructed_operating_margin_change = tuple(reconstructed)

    return ReportedMarginSeries(
        revenue=revenue,
        gross_profit=gross_profit,
        operating_profit=operating_profit,
        gross_margin=gross_margin,
        reported_operating_margin=reported_operating_margin,
        net_operating_expense_burden=net_operating_expense_burden,
        gross_margin_change=gross_margin_change,
        net_operating_expense_burden_change=net_operating_expense_burden_change,
        reconstructed_operating_margin_change=reconstructed_operating_margin_change,
    )
