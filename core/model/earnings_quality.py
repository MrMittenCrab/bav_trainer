"""Historical earnings-quality diagnostics: cash conversion and accruals (Step 9A).

Definitions (mechanical diagnostics, not automatic quality judgments):

    Cash conversion ratio = CFO / Reported Net Income
    Total accruals         = Reported Net Income - CFO
    Accrual ratio          = Total accruals / Average Total Assets
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
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


def _required_period_value(
    item: LineItem,
    period: date,
    *,
    concept: str,
) -> float:
    """Return an explicitly supplied period value; never invent zero for missing data."""
    raw = item.values.get(period)
    if raw is None:
        raise ValueError(
            f"{concept} line {item.label!r} has no supplied value "
            f"for modeled period {period.isoformat()}"
        )
    return float(raw)


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

    Requires a resolvable operating-cash-flow line. A resolved CFO or Total Assets
    line must supply an explicit value for every modeled period; missing period
    values raise ``ValueError`` rather than fabricating zeros. A completely absent
    Total Assets line omits only the asset-scaled extension.
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
        cfo = _required_period_value(
            cfo_item,
            period,
            concept="operating_cash_flow",
        )
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

    asset_values = [
        _required_period_value(
            assets_item,
            period,
            concept="total_assets",
        )
        for period in periods
    ]

    avg_assets: list[float | None] = [None]
    ratios: list[float | None] = [None]
    for j in range(1, n):
        average = (asset_values[j - 1] + asset_values[j]) / 2.0
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
