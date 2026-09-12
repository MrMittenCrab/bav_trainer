"""Historical earnings-quality diagnostics: cash conversion and accruals (Step 9A).

Definitions (mechanical diagnostics, not automatic quality judgments):

    Cash conversion ratio = CFO / Reported Net Income
    Total accruals         = Reported Net Income - CFO
    Accrual ratio          = Total accruals / Average Total Assets

Zero denominators produce the undefined-ratio sentinel ``#N/A`` (not numeric 0.0).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import resolve_line
from .source_values import required_period_value

UNDEFINED_RATIO = "#N/A"


@dataclass(frozen=True)
class EarningsQualityAvailability:
    operating_cash_flow: bool
    total_assets: bool


@dataclass(frozen=True)
class EarningsQualitySeries:
    operating_cash_flow: tuple[float, ...]
    cash_conversion_ratio: tuple[float | str, ...]
    total_accruals: tuple[float, ...]
    average_total_assets: tuple[float | None, ...]
    accrual_ratio: tuple[float | str | None, ...]


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

    Requires a resolvable operating-cash-flow line and explicitly supplied Net
    Income for every modeled period. A resolved CFO or Total Assets line must
    also supply an explicit value for every modeled period; missing period values
    raise ``MissingHistoricalValueError`` rather than fabricating zeros. A
    completely absent Total Assets line omits only the asset-scaled extension.

    Zero denominators yield ``UNDEFINED_RATIO`` (``#N/A``), not numeric ``0.0``.
    """
    cfo_item = resolve_line(
        financials.cash_flow,
        "operating_cash_flow",
        required=True,
    ).item
    assert cfo_item is not None

    net_income_item = resolve_line(
        financials.income_statement,
        "net_income",
        required=True,
    ).item
    assert net_income_item is not None

    n = len(periods)
    hist = anchor.historical
    if len(hist.net_income) != n:
        raise ValueError(
            "earnings-quality period axis must match AnchorMetrics historical series length"
        )

    net_income_values = [
        required_period_value(
            net_income_item,
            period,
            field="net_income",
        )
        for period in periods
    ]
    for j, source_ni in enumerate(net_income_values):
        anchor_ni = float(hist.net_income[j])
        if abs(source_ni - anchor_ni) > 1e-9:
            raise ValueError(
                "earnings-quality reported Net Income does not match AnchorMetrics "
                f"for modeled period {periods[j].isoformat()}"
            )

    cfo_vals: list[float] = []
    conversion: list[float | str] = []
    accruals: list[float] = []
    for j, period in enumerate(periods):
        cfo = required_period_value(
            cfo_item,
            period,
            field="operating_cash_flow",
        )
        ni = net_income_values[j]
        cfo_vals.append(cfo)
        conversion.append(UNDEFINED_RATIO if ni == 0.0 else cfo / ni)
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
        required_period_value(
            assets_item,
            period,
            field="total_assets",
        )
        for period in periods
    ]

    avg_assets: list[float | None] = [None]
    ratios: list[float | str | None] = [None]
    for j in range(1, n):
        average = (asset_values[j - 1] + asset_values[j]) / 2.0
        avg_assets.append(average)
        if average == 0.0:
            ratios.append(UNDEFINED_RATIO)
        else:
            ratios.append(accruals[j] / average)

    return EarningsQualitySeries(
        operating_cash_flow=tuple(cfo_vals),
        cash_conversion_ratio=tuple(conversion),
        total_accruals=tuple(accruals),
        average_total_assets=tuple(avg_assets),
        accrual_ratio=tuple(ratios),
    )
