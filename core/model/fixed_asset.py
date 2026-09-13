"""Historical PP&E / D&A asset-intensity diagnostics (Step 9K.1).

Mechanical context only. Does not invent capex, does not treat combined D&A as a
pure PP&E depreciation rate, and does not label capital intensity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .line_resolver import resolve_line
from .ratio_values import ratio_or_na
from .source_values import required_period_value


@dataclass(frozen=True)
class FixedAssetAvailability:
    ppe: bool
    depreciation_amortization: bool


@dataclass(frozen=True)
class FixedAssetSeries:
    ppe: tuple[float, ...]
    depreciation_amortization: tuple[float, ...]
    average_ppe: tuple[float | None, ...]
    ppe_turnover: tuple[float | str | None, ...]
    ppe_intensity: tuple[float | str | None, ...]
    ppe_change: tuple[float | None, ...]
    da_to_revenue: tuple[float | str, ...]
    da_to_average_ppe: tuple[float | str | None, ...]


def fixed_asset_availability(
    financials: StandardizedFinancials,
) -> FixedAssetAvailability:
    """Report whether PP&E and D&A lines resolve (ambiguity propagates)."""
    ppe = resolve_line(
        financials.balance_sheet,
        "property_plant_equipment",
        required=False,
    ).item
    da = resolve_line(
        financials.cash_flow,
        "depreciation_amortization",
        required=False,
    ).item
    return FixedAssetAvailability(
        ppe=ppe is not None,
        depreciation_amortization=da is not None,
    )


def fixed_asset_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present only when both PP&E and D&A resolve."""
    availability = fixed_asset_availability(financials)
    return availability.ppe and availability.depreciation_amortization


def compute_fixed_asset_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> FixedAssetSeries:
    """Compute PP&E / D&A intensity diagnostics for modeled periods."""
    ppe_item = resolve_line(
        financials.balance_sheet,
        "property_plant_equipment",
        required=True,
    ).item
    assert ppe_item is not None
    da_item = resolve_line(
        financials.cash_flow,
        "depreciation_amortization",
        required=True,
    ).item
    assert da_item is not None

    n = len(periods)
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    if len(revenue) != n:
        raise ValueError(
            "fixed-asset period axis must match AnchorMetrics historical revenue length"
        )

    ppe_vals = tuple(
        required_period_value(ppe_item, period, field="property_plant_equipment")
        for period in periods
    )
    da_vals = tuple(
        required_period_value(
            da_item, period, field="depreciation_amortization"
        )
        for period in periods
    )

    average_ppe: list[float | None] = [None]
    ppe_turnover: list[float | str | None] = [None]
    ppe_intensity: list[float | str | None] = [None]
    ppe_change: list[float | None] = [None]
    da_to_average_ppe: list[float | str | None] = [None]
    da_to_revenue = tuple(
        ratio_or_na(da_vals[j], revenue[j]) for j in range(n)
    )

    for j in range(1, n):
        average = (ppe_vals[j - 1] + ppe_vals[j]) / 2.0
        average_ppe.append(average)
        ppe_turnover.append(ratio_or_na(revenue[j], average))
        ppe_intensity.append(ratio_or_na(average, revenue[j]))
        ppe_change.append(ppe_vals[j] - ppe_vals[j - 1])
        da_to_average_ppe.append(ratio_or_na(da_vals[j], average))

    return FixedAssetSeries(
        ppe=ppe_vals,
        depreciation_amortization=da_vals,
        average_ppe=tuple(average_ppe),
        ppe_turnover=tuple(ppe_turnover),
        ppe_intensity=tuple(ppe_intensity),
        ppe_change=tuple(ppe_change),
        da_to_revenue=da_to_revenue,
        da_to_average_ppe=tuple(da_to_average_ppe),
    )
