"""Historical earnings-quality diagnostics: cash conversion and accruals (Step 9A).

Definitions (mechanical diagnostics, not automatic quality judgments):

    Cash conversion ratio = CFO / Reported Net Income
    Total accruals         = Reported Net Income - CFO
    Accrual ratio          = Total accruals / Average Total Assets
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import resolve_line


@dataclass(frozen=True)
class EarningsQualityAvailability:
    operating_cash_flow: bool
    total_assets: bool


@dataclass(frozen=True)
class EarningsQualitySeries:
    operating_cash_flow: tuple[float, ...]
    cash_conversion_ratio: tuple[float, ...]
    total_accruals: tuple[float, ...]
    average_total_assets: tuple[float | None, ...]
    accrual_ratio: tuple[float | None, ...]


def earnings_quality_availability(
    financials: StandardizedFinancials,
) -> EarningsQualityAvailability:
    """Report whether CFO / total-assets lines resolve (ambiguity propagates)."""
    cfo = resolve_line(
        financials.cash_flow,
        "operating_cash_flow",
        required=False,
    ).item
    total_assets = resolve_line(
        financials.balance_sheet,
        "total_assets",
        required=False,
    ).item
    return EarningsQualityAvailability(
        operating_cash_flow=cfo is not None,
        total_assets=total_assets is not None,
    )


def compute_earnings_quality_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> EarningsQualitySeries:
    """Compute cash-conversion and accrual diagnostics for modeled periods.

    Requires a resolvable operating-cash-flow line. Missing CFO raises
    ``MissingLineError`` rather than fabricating values.
    """
    cfo_item = resolve_line(
        financials.cash_flow,
        "operating_cash_flow",
        required=True,
    ).item
    assert cfo_item is not None

    n = len(periods)
    hist = anchor.historical
    if len(hist.net_income) != n:
        raise ValueError(
            "earnings-quality period axis must match AnchorMetrics historical series length"
        )

    cfo_vals: list[float] = []
    conversion: list[float] = []
    accruals: list[float] = []
    for j, period in enumerate(periods):
        raw = cfo_item.values.get(period)
        cfo = 0.0 if raw is None else float(raw)
        ni = float(hist.net_income[j])
        cfo_vals.append(cfo)
        conversion.append(0.0 if ni == 0.0 else cfo / ni)
        accruals.append(ni - cfo)

    assets_item = resolve_line(
        financials.balance_sheet,
        "total_assets",
        required=False,
    ).item
    if assets_item is None:
        none_series = tuple(None for _ in range(n))
        return EarningsQualitySeries(
            operating_cash_flow=tuple(cfo_vals),
            cash_conversion_ratio=tuple(conversion),
            total_accruals=tuple(accruals),
            average_total_assets=none_series,
            accrual_ratio=none_series,
        )

    avg_assets: list[float | None] = [None]
    ratios: list[float | None] = [None]
    for j in range(1, n):
        prev_raw = assets_item.values.get(periods[j - 1])
        cur_raw = assets_item.values.get(periods[j])
        prev = 0.0 if prev_raw is None else float(prev_raw)
        cur = 0.0 if cur_raw is None else float(cur_raw)
        average = (prev + cur) / 2.0
        avg_assets.append(average)
        if average == 0.0:
            ratios.append(0.0)
        else:
            ratios.append(accruals[j] / average)

    return EarningsQualitySeries(
        operating_cash_flow=tuple(cfo_vals),
        cash_conversion_ratio=tuple(conversion),
        total_accruals=tuple(accruals),
        average_total_assets=tuple(avg_assets),
        accrual_ratio=tuple(ratios),
    )
