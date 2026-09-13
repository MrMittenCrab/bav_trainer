"""Treatment-conditioned historical expected values for Formula Check."""

from __future__ import annotations

from ..engine.component_catalog import (
    COMPONENT_CATALOG,
    FIXED_ASSET_COMPONENT_CATALOG,
    LEASE_LIABILITY_COMPONENT_CATALOG,
    NORMALIZATION_COMPONENT_CATALOG,
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
    OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    PROFITABILITY_CHANGE_COMPONENT_CATALOG,
    PROFITABILITY_DRIVER_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
    ROE_ATTRIBUTION_COMPONENT_CATALOG,
    WORKING_CAPITAL_COMPONENT_CATALOG,
)
from ..engine.semantic_map import ResolvedComponent
from .earnings_quality import EarningsQualitySeries
from .earnings_quality_change import compute_earnings_quality_change_series
from .financial_math import AnchorMetrics
from .fixed_asset import FixedAssetSeries
from .lease_liability import LeaseLiabilitySeries
from .normalization import NormalizationSeries
from .normalized_per_share import compute_normalized_per_share_series
from .ownership_attribution import OwnershipAttributionSeries
from .per_share import PerShareSeries
from .per_share_attribution import compute_per_share_attribution_series
from .profitability_change import compute_profitability_change_series
from .profitability_drivers import compute_profitability_driver_series
from .roe_attribution import compute_roe_attribution_series
from .working_capital import compute_working_capital_series

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

_NORMALIZATION_FAMILY_SERIES = (
    "pretax_normalization_adjustment",
    "after_tax_normalization_adjustment",
    "normalized_nopat",
    "normalized_net_income",
)

_QUALITY_FAMILY_SERIES = (
    "operating_cash_flow_link",
    "cash_conversion_ratio",
    "total_accruals",
    "average_total_assets",
    "accrual_ratio",
)

_QUALITY_CHANGE_FAMILY_SERIES = (
    "operating_cash_flow_change",
    "cash_conversion_ratio_change",
    "total_accruals_change",
    "accrual_ratio_change",
)

_PER_SHARE_FAMILY_SERIES = (
    "reported_diluted_eps",
    "nopat_per_diluted_share",
    "diluted_eps_change",
    "diluted_share_count_change",
)

_PER_SHARE_ATTRIBUTION_FAMILY_SERIES = (
    "reported_net_income_change",
    "earnings_effect_on_diluted_eps_change",
    "share_count_effect_on_diluted_eps_change",
    "diluted_eps_change_from_drivers",
)

_NORMALIZED_PER_SHARE_FAMILY_SERIES = (
    "normalization_adjustment_per_diluted_share",
    "normalized_diluted_eps",
    "normalized_diluted_eps_change",
    "normalization_effect_on_diluted_eps_change",
)

_FIXED_ASSET_FAMILY_SERIES = (
    "ppe_source_link",
    "da_source_link",
    "average_ppe",
    "ppe_turnover",
    "ppe_intensity",
    "ppe_change",
    "da_to_revenue",
    "da_to_average_ppe",
)

_LEASE_LIABILITY_FAMILY_SERIES = (
    "lease_liability_source_link",
    "lease_liability_to_revenue",
    "lease_liability_change",
    "lease_liability_growth",
)

_OWNERSHIP_ATTRIBUTION_FAMILY_SERIES = (
    "parent_profit_source_link",
    "nci_profit_source_link",
    "profit_attribution_gap",
    "parent_equity_source_link",
    "nci_equity_source_link",
    "equity_attribution_gap",
    "parent_roe",
)

_WORKING_CAPITAL_FAMILY_SERIES = (
    "owca_to_revenue",
    "owcl_to_revenue",
    "nowc_to_revenue",
    "revenue_change",
    "nowc_change",
    "incremental_nowc_to_revenue_change",
    "owca_change",
    "owcl_change",
    "nowc_change_from_components",
    "incremental_owca_to_revenue_change",
    "incremental_owcl_to_revenue_change",
)

_PROFITABILITY_DRIVER_FAMILY_SERIES = (
    "average_noa",
    "noa_turnover",
    "noa_intensity",
    "rnoa_margin_turnover",
)

_PROFITABILITY_CHANGE_FAMILY_SERIES = (
    "nopat_margin_change",
    "noa_turnover_change",
    "rnoa_change",
    "rnoa_margin_effect",
    "rnoa_turnover_effect",
    "rnoa_change_from_drivers",
)

_ROE_ATTRIBUTION_FAMILY_SERIES = (
    "financing_contribution_to_roe",
    "roe_change",
    "operating_effect_on_roe_change",
    "leverage_effect_on_roe_change",
    "spread_effect_on_roe_change",
    "financing_effect_on_roe_change",
    "roe_change_from_drivers",
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
    return {family_id: series[family_id] for family_id in _FAMILY_SERIES}


def normalization_expected_series(
    normalization: NormalizationSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map the four normalization formula families to a NormalizationSeries."""
    series = {
        "pretax_normalization_adjustment": normalization.pretax_adjustment,
        "after_tax_normalization_adjustment": normalization.after_tax_adjustment,
        "normalized_nopat": normalization.normalized_nopat,
        "normalized_net_income": normalization.normalized_net_income,
    }
    expected_ids = {family.id for family in NORMALIZATION_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"normalization_expected_series family mismatch; missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _NORMALIZATION_FAMILY_SERIES}


def earnings_quality_expected_series(
    earnings_quality: EarningsQualitySeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map earnings-quality formula families to an EarningsQualitySeries."""
    series = {
        "operating_cash_flow_link": earnings_quality.operating_cash_flow,
        "cash_conversion_ratio": earnings_quality.cash_conversion_ratio,
        "total_accruals": earnings_quality.total_accruals,
        "average_total_assets": earnings_quality.average_total_assets,
        "accrual_ratio": earnings_quality.accrual_ratio,
    }
    expected_ids = {family.id for family in QUALITY_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"earnings_quality_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _QUALITY_FAMILY_SERIES}


def earnings_quality_change_expected_series(
    earnings_quality: EarningsQualitySeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map earnings-quality-change formula families to trend diagnostics."""
    changes = compute_earnings_quality_change_series(earnings_quality)
    series = {
        "operating_cash_flow_change": changes.operating_cash_flow_change,
        "cash_conversion_ratio_change": changes.cash_conversion_ratio_change,
        "total_accruals_change": changes.total_accruals_change,
        "accrual_ratio_change": changes.accrual_ratio_change,
    }
    expected_ids = {family.id for family in QUALITY_CHANGE_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "earnings_quality_change_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _QUALITY_CHANGE_FAMILY_SERIES
    }


def working_capital_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map working-capital formula families to diagnostics from ``anchor``."""
    wc = compute_working_capital_series(anchor)
    series = {
        "owca_to_revenue": wc.owca_to_revenue,
        "owcl_to_revenue": wc.owcl_to_revenue,
        "nowc_to_revenue": wc.nowc_to_revenue,
        "revenue_change": wc.revenue_change,
        "nowc_change": wc.nowc_change,
        "incremental_nowc_to_revenue_change": wc.incremental_nowc_to_revenue_change,
        "owca_change": wc.owca_change,
        "owcl_change": wc.owcl_change,
        "nowc_change_from_components": wc.nowc_change_from_components,
        "incremental_owca_to_revenue_change": wc.incremental_owca_to_revenue_change,
        "incremental_owcl_to_revenue_change": wc.incremental_owcl_to_revenue_change,
    }
    expected_ids = {family.id for family in WORKING_CAPITAL_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"working_capital_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _WORKING_CAPITAL_FAMILY_SERIES}


def profitability_driver_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map profitability-driver formula families to diagnostics from ``anchor``."""
    drivers = compute_profitability_driver_series(anchor)
    series = {
        "average_noa": drivers.average_noa,
        "noa_turnover": drivers.noa_turnover,
        "noa_intensity": drivers.noa_intensity,
        "rnoa_margin_turnover": drivers.rnoa_from_margin_turnover,
    }
    expected_ids = {family.id for family in PROFITABILITY_DRIVER_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"profitability_driver_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _PROFITABILITY_DRIVER_FAMILY_SERIES
    }


def profitability_change_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map RNOA-change formula families to diagnostics from ``anchor``."""
    changes = compute_profitability_change_series(anchor)
    series = {
        "nopat_margin_change": changes.nopat_margin_change,
        "noa_turnover_change": changes.noa_turnover_change,
        "rnoa_change": changes.rnoa_change,
        "rnoa_margin_effect": changes.margin_effect_on_rnoa,
        "rnoa_turnover_effect": changes.turnover_effect_on_rnoa,
        "rnoa_change_from_drivers": changes.rnoa_change_from_drivers,
    }
    expected_ids = {
        family.id for family in PROFITABILITY_CHANGE_COMPONENT_CATALOG
    }
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "profitability_change_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _PROFITABILITY_CHANGE_FAMILY_SERIES
    }


def roe_attribution_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map ROE-attribution formula families to diagnostics from ``anchor``."""
    values = compute_roe_attribution_series(anchor)
    series = {
        "financing_contribution_to_roe": values.financing_contribution_to_roe,
        "roe_change": values.roe_change,
        "operating_effect_on_roe_change": values.operating_effect_on_roe_change,
        "leverage_effect_on_roe_change": values.leverage_effect_on_roe_change,
        "spread_effect_on_roe_change": values.spread_effect_on_roe_change,
        "financing_effect_on_roe_change": values.financing_effect_on_roe_change,
        "roe_change_from_drivers": values.roe_change_from_drivers,
    }
    expected_ids = {family.id for family in ROE_ATTRIBUTION_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "roe_attribution_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _ROE_ATTRIBUTION_FAMILY_SERIES
    }


def per_share_expected_series(
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map per-share formula families to a PerShareSeries."""
    series = {
        "reported_diluted_eps": per_share.reported_diluted_eps,
        "nopat_per_diluted_share": per_share.nopat_per_diluted_share,
        "diluted_eps_change": per_share.diluted_eps_change,
        "diluted_share_count_change": per_share.diluted_share_count_change,
    }
    expected_ids = {family.id for family in PER_SHARE_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"per_share_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _PER_SHARE_FAMILY_SERIES}


def per_share_attribution_expected_series(
    anchor: AnchorMetrics,
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map diluted-EPS attribution families from PerShareSeries + AnchorMetrics."""
    attribution = compute_per_share_attribution_series(anchor, per_share)
    series = {
        "reported_net_income_change": attribution.reported_net_income_change,
        "earnings_effect_on_diluted_eps_change": (
            attribution.earnings_effect_on_diluted_eps_change
        ),
        "share_count_effect_on_diluted_eps_change": (
            attribution.share_count_effect_on_diluted_eps_change
        ),
        "diluted_eps_change_from_drivers": (
            attribution.diluted_eps_change_from_drivers
        ),
    }
    expected_ids = {
        family.id for family in PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG
    }
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "per_share_attribution_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _PER_SHARE_ATTRIBUTION_FAMILY_SERIES
    }


def normalized_per_share_expected_series(
    normalization: NormalizationSeries,
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map normalized diluted-EPS bridge families from Normalization + PerShare."""
    values = compute_normalized_per_share_series(normalization, per_share)
    series = {
        "normalization_adjustment_per_diluted_share": (
            values.normalization_adjustment_per_diluted_share
        ),
        "normalized_diluted_eps": values.normalized_diluted_eps,
        "normalized_diluted_eps_change": values.normalized_diluted_eps_change,
        "normalization_effect_on_diluted_eps_change": (
            values.normalization_effect_on_diluted_eps_change
        ),
    }
    expected_ids = {family.id for family in NORMALIZED_PER_SHARE_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "normalized_per_share_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _NORMALIZED_PER_SHARE_FAMILY_SERIES
    }


def fixed_asset_expected_series(
    fixed_asset: FixedAssetSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map fixed-asset diagnostic families from a FixedAssetSeries."""
    series = {
        "ppe_source_link": fixed_asset.ppe,
        "da_source_link": fixed_asset.depreciation_amortization,
        "average_ppe": fixed_asset.average_ppe,
        "ppe_turnover": fixed_asset.ppe_turnover,
        "ppe_intensity": fixed_asset.ppe_intensity,
        "ppe_change": fixed_asset.ppe_change,
        "da_to_revenue": fixed_asset.da_to_revenue,
        "da_to_average_ppe": fixed_asset.da_to_average_ppe,
    }
    expected_ids = {family.id for family in FIXED_ASSET_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "fixed_asset_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _FIXED_ASSET_FAMILY_SERIES}


def lease_liability_expected_series(
    lease_liability: LeaseLiabilitySeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map lease-liability diagnostic families from a LeaseLiabilitySeries."""
    series = {
        "lease_liability_source_link": lease_liability.lease_liability,
        "lease_liability_to_revenue": lease_liability.lease_liability_to_revenue,
        "lease_liability_change": lease_liability.lease_liability_change,
        "lease_liability_growth": lease_liability.lease_liability_growth,
    }
    expected_ids = {family.id for family in LEASE_LIABILITY_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "lease_liability_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id] for family_id in _LEASE_LIABILITY_FAMILY_SERIES
    }


def ownership_attribution_expected_series(
    ownership_attribution: OwnershipAttributionSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map ownership-attribution diagnostic families from an OwnershipAttributionSeries."""
    series = {
        "parent_profit_source_link": ownership_attribution.parent_profit,
        "nci_profit_source_link": ownership_attribution.nci_profit,
        "profit_attribution_gap": ownership_attribution.profit_attribution_gap,
        "parent_equity_source_link": ownership_attribution.parent_equity,
        "nci_equity_source_link": ownership_attribution.nci_equity,
        "equity_attribution_gap": ownership_attribution.equity_attribution_gap,
        "parent_roe": ownership_attribution.parent_roe,
    }
    expected_ids = {family.id for family in OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "ownership_attribution_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _OWNERSHIP_ATTRIBUTION_FAMILY_SERIES
    }


def expected_value_for_component(
    anchor: AnchorMetrics,
    component: ResolvedComponent,
    *,
    normalization: NormalizationSeries | None = None,
    earnings_quality: EarningsQualitySeries | None = None,
    per_share: PerShareSeries | None = None,
    fixed_asset: FixedAssetSeries | None = None,
    lease_liability: LeaseLiabilitySeries | None = None,
    ownership_attribution: OwnershipAttributionSeries | None = None,
) -> float | str | None:
    """Return the treatment-conditioned expected value for one practice component."""
    family_id = component.family_id
    if not family_id:
        raise ValueError(f"Component {component.id!r} has no family_id")
    period_index = component.period_index
    if period_index is None:
        raise ValueError(
            f"Component {component.id!r} (family {family_id}) has no period_index"
        )

    if family_id in _OWNERSHIP_ATTRIBUTION_FAMILY_SERIES:
        if ownership_attribution is None:
            raise ValueError(
                f"Ownership-attribution family {family_id!r} requires an "
                "OwnershipAttributionSeries"
            )
        series = ownership_attribution_expected_series(ownership_attribution)
    elif family_id in _LEASE_LIABILITY_FAMILY_SERIES:
        if lease_liability is None:
            raise ValueError(
                f"Lease-liability family {family_id!r} requires a LeaseLiabilitySeries"
            )
        series = lease_liability_expected_series(lease_liability)
    elif family_id in _FIXED_ASSET_FAMILY_SERIES:
        if fixed_asset is None:
            raise ValueError(
                f"Fixed-asset family {family_id!r} requires a FixedAssetSeries"
            )
        series = fixed_asset_expected_series(fixed_asset)
    elif family_id in _NORMALIZED_PER_SHARE_FAMILY_SERIES:
        if normalization is None:
            raise ValueError(
                f"Normalized-per-share family {family_id!r} requires a "
                "NormalizationSeries"
            )
        if per_share is None:
            raise ValueError(
                f"Normalized-per-share family {family_id!r} requires a PerShareSeries"
            )
        series = normalized_per_share_expected_series(normalization, per_share)
    elif family_id in _PER_SHARE_ATTRIBUTION_FAMILY_SERIES:
        if per_share is None:
            raise ValueError(
                f"Per-share-attribution family {family_id!r} requires a PerShareSeries"
            )
        series = per_share_attribution_expected_series(anchor, per_share)
    elif family_id in _PER_SHARE_FAMILY_SERIES:
        if per_share is None:
            raise ValueError(
                f"Per-share family {family_id!r} requires a PerShareSeries"
            )
        series = per_share_expected_series(per_share)
    elif family_id in _ROE_ATTRIBUTION_FAMILY_SERIES:
        series = roe_attribution_expected_series(anchor)
    elif family_id in _PROFITABILITY_CHANGE_FAMILY_SERIES:
        series = profitability_change_expected_series(anchor)
    elif family_id in _PROFITABILITY_DRIVER_FAMILY_SERIES:
        series = profitability_driver_expected_series(anchor)
    elif family_id in _WORKING_CAPITAL_FAMILY_SERIES:
        series = working_capital_expected_series(anchor)
    elif family_id in _QUALITY_CHANGE_FAMILY_SERIES:
        if earnings_quality is None:
            raise ValueError(
                f"Earnings-quality-change family {family_id!r} "
                "requires an EarningsQualitySeries"
            )
        series = earnings_quality_change_expected_series(earnings_quality)
    elif family_id in _QUALITY_FAMILY_SERIES:
        if earnings_quality is None:
            raise ValueError(
                f"Earnings-quality family {family_id!r} requires an EarningsQualitySeries"
            )
        series = earnings_quality_expected_series(earnings_quality)
    elif family_id in _NORMALIZATION_FAMILY_SERIES:
        if normalization is None:
            raise ValueError(
                f"Normalization family {family_id!r} requires a NormalizationSeries"
            )
        series = normalization_expected_series(normalization)
    else:
        series = historical_expected_series(anchor)
        if family_id not in series:
            raise ValueError(f"Unknown historical family {family_id!r}")

    values = series[family_id]
    if period_index < 0 or period_index >= len(values):
        raise ValueError(
            f"period_index {period_index} out of range for family {family_id} "
            f"(len={len(values)})"
        )
    return values[period_index]
