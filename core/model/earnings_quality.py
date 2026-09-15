"""Historical earnings-quality diagnostics: cash conversion and accruals (Step 9A).

Definitions (mechanical diagnostics, not automatic quality judgments):

    Cash conversion ratio = CFO / Reported Net Income
    Total accruals         = Reported Net Income - CFO
    Accrual ratio          = Total accruals / Average Total Assets

When a unique explicit cash-flow ``stock_based_compensation`` line also
resolves, the schedule extends with:

    SBC / Revenue                  = SBC / Revenue
    SBC / Operating Cash Flow      = SBC / reported CFO
    Reported CFO less SBC add-back = reported CFO − SBC

Zero denominators produce the undefined-ratio sentinel ``#N/A`` (not numeric 0.0).
Absent or ambiguous SBC omits only that extension. Settlement proceeds,
withholding payments, and repurchases are not SBC.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import AmbiguousLineError, resolve_line
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
from .source_values import required_period_value

_SBC_CONCEPT = "stock_based_compensation"
_CFO_CONCEPT = "operating_cash_flow"


@dataclass(frozen=True)
class EarningsQualityAvailability:
    operating_cash_flow: bool
    total_assets: bool
    stock_based_compensation: bool = False
    stock_based_compensation_ambiguous: bool = False


@dataclass(frozen=True)
class EarningsQualitySeries:
    operating_cash_flow: tuple[float, ...]
    cash_conversion_ratio: tuple[float | str, ...]
    total_accruals: tuple[float, ...]
    average_total_assets: tuple[float | None, ...]
    accrual_ratio: tuple[float | str | None, ...]
    stock_based_compensation: tuple[float, ...] | None = None
    sbc_to_revenue: tuple[float | str, ...] | None = None
    sbc_to_operating_cash_flow: tuple[float | str, ...] | None = None
    operating_cash_flow_less_sbc: tuple[float, ...] | None = None


def resolve_sbc_source(
    financials: StandardizedFinancials,
) -> LineItem | None:
    """Return the unique explicit CF stock-based-compensation line, or None."""
    try:
        resolved = resolve_line(
            financials.cash_flow, _SBC_CONCEPT, required=False
        )
    except AmbiguousLineError:
        return None
    return resolved.item


def sbc_diagnostics_applicable(financials: StandardizedFinancials) -> bool:
    """SBC extension requires unique reported CFO and unique explicit SBC."""
    try:
        availability = earnings_quality_availability(financials)
    except AmbiguousLineError:
        return False
    return (
        availability.operating_cash_flow
        and availability.stock_based_compensation
        and not availability.stock_based_compensation_ambiguous
    )


def earnings_quality_availability(
    financials: StandardizedFinancials,
) -> EarningsQualityAvailability:
    """Report whether CFO / total-assets / SBC lines resolve (CFO ambiguity raises)."""
    cfo = resolve_line(
        financials.cash_flow,
        _CFO_CONCEPT,
        required=False,
    ).item
    total_assets = resolve_line(
        financials.balance_sheet,
        "total_assets",
        required=False,
    ).item
    try:
        sbc = resolve_line(
            financials.cash_flow,
            _SBC_CONCEPT,
            required=False,
        )
    except AmbiguousLineError:
        stock_based_compensation = False
        stock_based_compensation_ambiguous = True
    else:
        stock_based_compensation = sbc.item is not None
        stock_based_compensation_ambiguous = False
    return EarningsQualityAvailability(
        operating_cash_flow=cfo is not None,
        total_assets=total_assets is not None,
        stock_based_compensation=stock_based_compensation,
        stock_based_compensation_ambiguous=stock_based_compensation_ambiguous,
    )


def _sbc_extension(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
    cfo_vals: list[float],
) -> tuple[
    tuple[float, ...] | None,
    tuple[float | str, ...] | None,
    tuple[float | str, ...] | None,
    tuple[float, ...] | None,
]:
    item = resolve_sbc_source(financials)
    if item is None:
        return (None, None, None, None)

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "earnings-quality SBC period axis must match AnchorMetrics "
            "historical revenue length"
        )

    sbc_vals = tuple(
        required_period_value(item, period, field=_SBC_CONCEPT)
        for period in periods
    )
    sbc_to_revenue = tuple(
        ratio_or_na(sbc_vals[j], revenue[j]) for j in range(n)
    )
    sbc_to_cfo = tuple(
        ratio_or_na(sbc_vals[j], cfo_vals[j]) for j in range(n)
    )
    cfo_less_sbc = tuple(cfo_vals[j] - sbc_vals[j] for j in range(n))
    return (sbc_vals, sbc_to_revenue, sbc_to_cfo, cfo_less_sbc)


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

    Unique explicit cash-flow ``stock_based_compensation`` adds SBC/revenue,
    SBC/CFO, and reported-CFO-less-SBC series. Absent or ambiguous SBC omits
    only that extension. Missing required SBC period values fail closed.

    Zero denominators yield ``UNDEFINED_RATIO`` (``#N/A``), not numeric ``0.0``.
    """
    cfo_item = resolve_line(
        financials.cash_flow,
        _CFO_CONCEPT,
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
            field=_CFO_CONCEPT,
        )
        ni = net_income_values[j]
        cfo_vals.append(cfo)
        conversion.append(ratio_or_na(cfo, ni))
        accruals.append(ni - cfo)

    sbc_vals, sbc_to_rev, sbc_to_cfo, cfo_less_sbc = _sbc_extension(
        financials, periods, anchor, cfo_vals
    )

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
            stock_based_compensation=sbc_vals,
            sbc_to_revenue=sbc_to_rev,
            sbc_to_operating_cash_flow=sbc_to_cfo,
            operating_cash_flow_less_sbc=cfo_less_sbc,
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
        ratios.append(ratio_or_na(accruals[j], average))

    return EarningsQualitySeries(
        operating_cash_flow=tuple(cfo_vals),
        cash_conversion_ratio=tuple(conversion),
        total_accruals=tuple(accruals),
        average_total_assets=tuple(avg_assets),
        accrual_ratio=tuple(ratios),
        stock_based_compensation=sbc_vals,
        sbc_to_revenue=sbc_to_rev,
        sbc_to_operating_cash_flow=sbc_to_cfo,
        operating_cash_flow_less_sbc=cfo_less_sbc,
    )
