"""Treatment-conditioned historical expected values for Formula Check."""

from __future__ import annotations

from ..engine.component_catalog import COMPONENT_CATALOG
from ..engine.semantic_map import ResolvedComponent
from .financial_math import AnchorMetrics

_FAMILY_SERIES = (
    "revenue_link",
    "net_income_link",
    "effective_tax_rate_fy",
    "net_interest_fy",
    "net_interest_after_tax_fy",
    "nopat_fy",
    "owca_agg",
    "owcl_agg",
    "nowc_agg",
    "olta_agg",
    "oltl_agg",
    "nola_agg",
    "noa_agg",
    "financial_assets_agg",
    "financial_liabilities_agg",
    "net_debt",
    "equity_reformulated_fy",
    "sales_growth",
    "nopat_margin",
    "rnoa",
    "after_tax_cod",
    "spread",
    "flev",
    "roe_decomp",
    "actual_roe",
)


def historical_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map each historical formula family to its period series under ``anchor``."""
    reform = anchor.reformulation
    dup = anchor.dupont
    hist = anchor.historical
    series = {
        "revenue_link": tuple(hist.revenue),
        "net_income_link": tuple(hist.net_income),
        "effective_tax_rate_fy": tuple(hist.effective_tax_rate),
        "net_interest_fy": tuple(hist.net_interest),
        "net_interest_after_tax_fy": tuple(hist.net_interest_after_tax),
        "nopat_fy": tuple(hist.nopat),
        "owca_agg": reform.category_totals["Operating Working Capital Asset"],
        "owcl_agg": reform.category_totals["Operating Working Capital Liability"],
        "nowc_agg": reform.nowc,
        "olta_agg": reform.category_totals["Operating Long-Term Asset"],
        "oltl_agg": reform.category_totals["Operating Long-Term Liability"],
        "nola_agg": reform.nola,
        "noa_agg": reform.noa,
        "financial_assets_agg": reform.category_totals["Financial Asset"],
        "financial_liabilities_agg": reform.category_totals["Financial Liability"],
        "net_debt": reform.net_debt,
        "equity_reformulated_fy": reform.implied_equity,
        "sales_growth": tuple(dup["Sales Growth"]),
        "nopat_margin": tuple(dup["NOPAT Margin"]),
        "rnoa": tuple(dup["RNOA"]),
        "after_tax_cod": tuple(dup["After-tax CoD"]),
        "spread": tuple(dup["Spread"]),
        "flev": tuple(dup["FLEV"]),
        "roe_decomp": tuple(dup["ROE (decomposed)"]),
        "actual_roe": tuple(dup["Actual ROE"]),
    }
    expected_ids = {family.id for family in COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"historical_expected_series family mismatch; missing={missing} extra={extra}"
        )
    # Preserve catalog order for deterministic debugging.
    return {family_id: series[family_id] for family_id in _FAMILY_SERIES}


def expected_value_for_component(
    anchor: AnchorMetrics,
    component: ResolvedComponent,
) -> float | str | None:
    """Return the treatment-conditioned expected value for one historical component."""
    family_id = component.family_id
    if not family_id:
        raise ValueError(f"Component {component.id!r} has no family_id")
    series = historical_expected_series(anchor)
    if family_id not in series:
        raise ValueError(f"Unknown historical family {family_id!r}")
    period_index = component.period_index
    if period_index is None:
        raise ValueError(
            f"Component {component.id!r} (family {family_id}) has no period_index"
        )
    values = series[family_id]
    if period_index < 0 or period_index >= len(values):
        raise ValueError(
            f"period_index {period_index} out of range for family {family_id} "
            f"(len={len(values)})"
        )
    return values[period_index]
