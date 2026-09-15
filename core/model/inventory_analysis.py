"""Source-supported inventory growth, intensity, and cash-flow comparison.

Optional, source-gated module. Resolves unique explicit BS ``inventories``,
retaining original-row links and stored values, and uses existing revenue
resolution. Resolves unique explicit CF ``change_in_inventories`` the same
way. Stored concepts, values, signs, and provenance are left unchanged.
No label fallback, no competing-alias merge, and no wrong-statement substitutes.

Computes inventory intensity ``I_t = inventory_t / revenue_t`` when unique
inventory and revenue resolve. Adjacent-period families compute inventory
change; revenue-scale effect ``I_(t−1) × (revenue_t − revenue_(t−1))``;
intensity effect ``revenue_t × (I_t − I_(t−1))``; and reconstructed inventory
change as the sum of both effects.

Balance-implied CF adjustment ``B_t = -(inventory_t - inventory_(t−1))``
gates on unique BS inventory alone and reuses the inventory-change result.
Unexplained difference ``D_t = reported_CF_adjustment_t - B_t`` additionally
requires the unique CF adjustment. Neither comparison family requires
revenue, CFO, or interest. Opening-period comparison exercises are omitted
and no opening inventory is inferred. Available opening-period CF facts
remain populated.

Inventory change and ``B_t`` gate on unique inventory alone. Intensity and
attribution additionally require unique revenue. ``D_t`` additionally
requires unique CF. Absent or ambiguous sources omit only dependent
families. Missing required-period values fail closed. Reported zeros remain
valid. Zero revenue yields the existing undefined-ratio result with
dependency propagation; direct inventory change and ``B_t`` remain available.

The intensity bridge is an arithmetic decomposition under a prior-intensity /
current-revenue convention. It is not inventory days or turnover, and it is
not proof of cash movement, deterioration, seasonality, markdowns, or
management causes. A nonzero ``D_t`` needs further evidence; it does not
establish an error, cash paid for inventory, FX, acquisitions, write-downs,
or another specific cause. No balancing plug is inserted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
from .source_values import required_period_value

INVENTORIES_CONCEPT = "inventories"
REVENUE_CONCEPT = "revenue"
CHANGE_IN_INVENTORIES_CONCEPT = "change_in_inventories"
RECONCILE_TOLERANCE = 1e-8


@dataclass(frozen=True)
class InventoryAnalysisAvailability:
    inventories: bool
    inventories_ambiguous: bool
    revenue: bool
    revenue_ambiguous: bool
    change_in_inventories: bool
    change_in_inventories_ambiguous: bool


@dataclass(frozen=True)
class InventoryAnalysisSources:
    inventories: LineItem | None
    revenue: LineItem | None
    change_in_inventories: LineItem | None


@dataclass(frozen=True)
class InventoryAnalysisSeries:
    inventories: tuple[float, ...]
    inventory_change: tuple[float | None, ...]
    inventory_balance_implied_cf_adjustment: tuple[float | None, ...]
    revenue: tuple[float, ...] | None = None
    inventory_intensity: tuple[float | str, ...] | None = None
    inventory_revenue_scale_effect: tuple[float | str | None, ...] | None = None
    inventory_intensity_effect: tuple[float | str | None, ...] | None = None
    reconstructed_inventory_change: tuple[float | str | None, ...] | None = None
    change_in_inventories: tuple[float | None, ...] | None = None
    inventory_cf_adjustment_difference: tuple[float | None, ...] | None = None


def _resolve_unique(
    items: list[LineItem], concept: str
) -> tuple[LineItem | None, bool]:
    try:
        resolved = resolve_line(items, concept, required=False)
    except AmbiguousLineError:
        return None, True
    return resolved.item, False


def inventory_analysis_availability(
    financials: StandardizedFinancials,
) -> InventoryAnalysisAvailability:
    """Report unique BS inventory, IS revenue, and CF adjustment resolution."""
    inventories, inventories_ambiguous = _resolve_unique(
        financials.balance_sheet, INVENTORIES_CONCEPT
    )
    revenue, revenue_ambiguous = _resolve_unique(
        financials.income_statement, REVENUE_CONCEPT
    )
    change_in_inventories, change_in_inventories_ambiguous = _resolve_unique(
        financials.cash_flow, CHANGE_IN_INVENTORIES_CONCEPT
    )
    return InventoryAnalysisAvailability(
        inventories=inventories is not None,
        inventories_ambiguous=inventories_ambiguous,
        revenue=revenue is not None,
        revenue_ambiguous=revenue_ambiguous,
        change_in_inventories=change_in_inventories is not None,
        change_in_inventories_ambiguous=change_in_inventories_ambiguous,
    )


def resolve_inventory_analysis_sources(
    financials: StandardizedFinancials,
) -> InventoryAnalysisSources:
    """Return unique inventory/revenue/CF lines; ambiguous sources are None."""
    inventories, _ = _resolve_unique(financials.balance_sheet, INVENTORIES_CONCEPT)
    revenue, _ = _resolve_unique(financials.income_statement, REVENUE_CONCEPT)
    change_in_inventories, _ = _resolve_unique(
        financials.cash_flow, CHANGE_IN_INVENTORIES_CONCEPT
    )
    return InventoryAnalysisSources(
        inventories=inventories,
        revenue=revenue,
        change_in_inventories=change_in_inventories,
    )


def inventory_change_applicable(financials: StandardizedFinancials) -> bool:
    """Inventory change requires unique explicit BS inventories."""
    avail = inventory_analysis_availability(financials)
    return avail.inventories and not avail.inventories_ambiguous


def inventory_intensity_applicable(financials: StandardizedFinancials) -> bool:
    """Intensity requires unique inventory and unique revenue."""
    avail = inventory_analysis_availability(financials)
    return (
        inventory_change_applicable(financials)
        and avail.revenue
        and not avail.revenue_ambiguous
    )


def inventory_revenue_scale_effect_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return inventory_intensity_applicable(financials)


def inventory_intensity_effect_applicable(financials: StandardizedFinancials) -> bool:
    return inventory_intensity_applicable(financials)


def reconstructed_inventory_change_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return inventory_intensity_applicable(financials)


def inventory_balance_implied_cf_adjustment_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Balance-implied CF adjustment gates on unique BS inventory alone."""
    return inventory_change_applicable(financials)


def inventory_cf_adjustment_difference_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Unexplained difference additionally requires unique CF adjustment."""
    avail = inventory_analysis_availability(financials)
    return (
        inventory_balance_implied_cf_adjustment_applicable(financials)
        and avail.change_in_inventories
        and not avail.change_in_inventories_ambiguous
    )


def inventory_analysis_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when unique explicit BS inventories resolve."""
    return inventory_change_applicable(financials)


def _difference_or_na(
    current: float | str, prior: float | str
) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _product_or_na(
    left: float | str, right: float | str
) -> float | str:
    if left == UNDEFINED_RATIO or right == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(left) * float(right)


def _sum_or_na(left: float | str, right: float | str) -> float | str:
    if left == UNDEFINED_RATIO or right == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(left) + float(right)


def compute_inventory_analysis_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> InventoryAnalysisSeries:
    """Read reported inventory (and revenue/CF when unique) and compute diagnostics."""
    if not inventory_change_applicable(financials):
        raise MissingLineError("inventory sources not available")

    sources = resolve_inventory_analysis_sources(financials)
    assert sources.inventories is not None
    inventories = tuple(
        required_period_value(
            sources.inventories, period, field=INVENTORIES_CONCEPT
        )
        for period in periods
    )

    n = len(periods)
    inventory_change: list[float | None] = [None] * n
    implied: list[float | None] = [None] * n
    for j in range(1, n):
        inventory_change[j] = inventories[j] - inventories[j - 1]
        implied[j] = -inventory_change[j]

    revenue: tuple[float, ...] | None = None
    inventory_intensity: tuple[float | str, ...] | None = None
    inventory_revenue_scale_effect: tuple[float | str | None, ...] | None = None
    inventory_intensity_effect: tuple[float | str | None, ...] | None = None
    reconstructed_inventory_change: tuple[float | str | None, ...] | None = None

    if inventory_intensity_applicable(financials):
        assert sources.revenue is not None
        revenue = tuple(
            required_period_value(sources.revenue, period, field=REVENUE_CONCEPT)
            for period in periods
        )
        inventory_intensity = tuple(
            ratio_or_na(inventories[j], revenue[j]) for j in range(n)
        )

        scale: list[float | str | None] = [None] * n
        intensity_effect: list[float | str | None] = [None] * n
        reconstructed: list[float | str | None] = [None] * n
        for j in range(1, n):
            prior_intensity = inventory_intensity[j - 1]
            current_intensity = inventory_intensity[j]
            revenue_delta = revenue[j] - revenue[j - 1]
            scale_value = _product_or_na(prior_intensity, revenue_delta)
            intensity_value = _product_or_na(
                revenue[j],
                _difference_or_na(current_intensity, prior_intensity),
            )
            reconstructed_value = _sum_or_na(scale_value, intensity_value)
            if reconstructed_value != UNDEFINED_RATIO:
                direct = inventory_change[j]
                assert direct is not None
                if abs(float(reconstructed_value) - float(direct)) > RECONCILE_TOLERANCE:
                    raise ValueError(
                        "inventory change attribution does not reconcile: "
                        f"period_index={j} direct={direct} "
                        f"reconstructed={reconstructed_value}"
                    )
            scale[j] = scale_value
            intensity_effect[j] = intensity_value
            reconstructed[j] = reconstructed_value
        inventory_revenue_scale_effect = tuple(scale)
        inventory_intensity_effect = tuple(intensity_effect)
        reconstructed_inventory_change = tuple(reconstructed)

    change_in_inventories: tuple[float | None, ...] | None = None
    inventory_cf_adjustment_difference: tuple[float | None, ...] | None = None
    if inventory_cf_adjustment_difference_applicable(financials):
        assert sources.change_in_inventories is not None
        cf_values: list[float | None] = [None] * n
        differences: list[float | None] = [None] * n
        opening = sources.change_in_inventories.values.get(periods[0])
        if opening is not None:
            cf_values[0] = float(opening)
        for j in range(1, n):
            reported = required_period_value(
                sources.change_in_inventories,
                periods[j],
                field=CHANGE_IN_INVENTORIES_CONCEPT,
            )
            cf_values[j] = reported
            implied_value = implied[j]
            assert implied_value is not None
            difference = reported - implied_value
            if abs((implied_value + difference) - reported) > RECONCILE_TOLERANCE:
                raise ValueError(
                    "inventory CF comparison does not reconcile: "
                    f"period_index={j} implied={implied_value} "
                    f"difference={difference} reported={reported}"
                )
            differences[j] = difference
        change_in_inventories = tuple(cf_values)
        inventory_cf_adjustment_difference = tuple(differences)

    return InventoryAnalysisSeries(
        inventories=inventories,
        inventory_change=tuple(inventory_change),
        inventory_balance_implied_cf_adjustment=tuple(implied),
        revenue=revenue,
        inventory_intensity=inventory_intensity,
        inventory_revenue_scale_effect=inventory_revenue_scale_effect,
        inventory_intensity_effect=inventory_intensity_effect,
        reconstructed_inventory_change=reconstructed_inventory_change,
        change_in_inventories=change_in_inventories,
        inventory_cf_adjustment_difference=inventory_cf_adjustment_difference,
    )
