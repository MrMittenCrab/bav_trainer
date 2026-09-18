"""Treatment-conditioned historical expected values for Formula Check."""

from __future__ import annotations

from datetime import date

from ..engine.component_catalog import (
    ACQUISITION_CASH_COMPONENT_CATALOG,
    CASH_ROLLFORWARD_COMPONENT_CATALOG,
    GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG,
    STORE_COUNT_COMPONENT_CATALOG,
    REVENUE_STORE_COMPONENT_CATALOG,
    REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    REVENUE_STORE_GROWTH_FAMILY_ID,
    COMPARABLE_SALES_CHANGE_FAMILY_ID,
    COMPARABLE_SALES_COMPONENT_CATALOG,
    COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG,
    SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    comparable_sales_identity_from_component,
    INVENTORY_ANALYSIS_COMPONENT_CATALOG,
    REPORTED_MARGIN_COMPONENT_CATALOG,
    SHARE_REPURCHASE_COMPONENT_CATALOG,
    CAPEX_COMPONENT_CATALOG,
    COMPONENT_CATALOG,
    DEFERRED_TAX_COMPONENT_CATALOG,
    FIXED_ASSET_COMPONENT_CATALOG,
    GOODWILL_INTANGIBLES_COMPONENT_CATALOG,
    LEASE_LIABILITY_COMPONENT_CATALOG,
    LEASE_REPAYMENT_COMPONENT_CATALOG,
    LEASE_ROU_COMPONENT_CATALOG,
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
from .acquisition_cash import AcquisitionCashSeries
from .cash_rollforward import CashRollforwardSeries
from .inventory_analysis import InventoryAnalysisSeries
from .reported_margin import ReportedMarginSeries
from .share_repurchase import ShareRepurchaseSeries
from .capex import CapexSeries
from .earnings_quality import EarningsQualitySeries
from .earnings_quality_change import compute_earnings_quality_change_series
from .deferred_tax import DeferredTaxSeries
from .financial_math import AnchorMetrics
from .fixed_asset import FixedAssetSeries
from .geographic_segment import GeographicSegmentSeries
from .management_kpi import ManagementKpiSeries
from .operating_kpi import OperatingKpiSeries
from .operating_kpi_relationships import (
    OperatingKpiRevenueComparableSalesRelationship,
    OperatingKpiRevenueSalesPerSquareFootRelationship,
    OperatingKpiRevenueStoreRelationship,
)
from .goodwill_intangibles import (
    GoodwillIntangiblesAvailability,
    GoodwillIntangiblesSeries,
)
from .lease_liability import LeaseLiabilitySeries
from .lease_repayment import LeaseRepaymentSeries
from .lease_rou import LeaseRouSeries
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

_QUALITY_BASE_FAMILY_SERIES = (
    "operating_cash_flow_link",
    "cash_conversion_ratio",
    "total_accruals",
    "average_total_assets",
    "accrual_ratio",
)

_QUALITY_SBC_FAMILY_SERIES = (
    "sbc_to_revenue",
    "sbc_to_operating_cash_flow",
    "operating_cash_flow_less_sbc",
)

_QUALITY_FAMILY_SERIES = _QUALITY_BASE_FAMILY_SERIES + _QUALITY_SBC_FAMILY_SERIES

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

_LEASE_ROU_FAMILY_SERIES = (
    "rou_assets_change",
    "rou_assets_growth",
    "average_rou_assets",
    "rou_assets_to_revenue",
)

_DEFERRED_TAX_FAMILY_SERIES = (
    "net_deferred_tax_position",
    "deferred_tax_assets_change",
    "deferred_tax_liabilities_change",
    "net_deferred_tax_position_change",
)

_CAPEX_FAMILY_SERIES = (
    "ppe_capex",
    "ppe_capex_to_revenue",
    "cash_after_ppe_capex",
    "cash_after_ppe_capex_to_revenue",
)
_CAPEX_BASE_FAMILY_SERIES = (
    "ppe_capex",
    "ppe_capex_to_revenue",
)
_CAPEX_CASH_AFTER_FAMILY_SERIES = (
    "cash_after_ppe_capex",
    "cash_after_ppe_capex_to_revenue",
)

_LEASE_REPAYMENT_FAMILY_SERIES = (
    "lease_repayments",
    "lease_repayments_to_revenue",
)

_ACQUISITION_CASH_FAMILY_SERIES = (
    "acquisition_cash_outflow",
    "acquisition_cash_to_revenue",
    "cash_after_ppe_capex_and_acquisitions",
)
_ACQUISITION_CASH_BASE_FAMILY_SERIES = (
    "acquisition_cash_outflow",
    "acquisition_cash_to_revenue",
)
_ACQUISITION_CASH_RESIDUAL_FAMILY_SERIES = (
    "cash_after_ppe_capex_and_acquisitions",
)

_SHARE_REPURCHASE_FAMILY_SERIES = (
    "share_repurchase_outflow",
    "share_repurchase_to_revenue",
    "cash_after_ppe_capex_acquisitions_and_repurchases",
)
_SHARE_REPURCHASE_BASE_FAMILY_SERIES = (
    "share_repurchase_outflow",
    "share_repurchase_to_revenue",
)
_SHARE_REPURCHASE_RESIDUAL_FAMILY_SERIES = (
    "cash_after_ppe_capex_acquisitions_and_repurchases",
)

_CASH_ROLLFORWARD_FAMILY_SERIES = (
    "cash_movement_from_flows",
    "cash_movement_difference",
    "cash_ending_from_flows",
    "cash_ending_difference",
)
_CASH_ROLLFORWARD_BASE_FAMILY_SERIES = ("cash_movement_from_flows",)

_REPORTED_MARGIN_FAMILY_SERIES = (
    "gross_margin",
    "reported_operating_margin",
    "net_operating_expense_burden",
    "gross_margin_change",
    "net_operating_expense_burden_change",
    "reconstructed_operating_margin_change",
)
_INVENTORY_ANALYSIS_FAMILY_SERIES = (
    "inventory_intensity",
    "inventory_change",
    "inventory_revenue_scale_effect",
    "inventory_intensity_effect",
    "reconstructed_inventory_change",
    "inventory_balance_implied_cf_adjustment",
    "inventory_cf_adjustment_difference",
)
_GEOGRAPHIC_FAMILY_SERIES = (
    "geographic_revenue_share",
    "geographic_revenue_growth",
    "geographic_reported_operating_margin",
    "geographic_calculated_segment_revenue_total",
    "geographic_calculated_segment_operating_profit_total",
    "geographic_signed_reconciling_contribution",
    "geographic_reconstructed_consolidated_operating_profit",
    "geographic_consolidated_revenue_difference",
    "geographic_consolidated_operating_profit_difference",
    "geographic_revenue_growth_contribution",
    "geographic_consolidated_revenue_growth",
    "geographic_revenue_growth_contribution_residual",
    "geographic_operating_margin_contribution",
    "geographic_reconciling_operating_margin_contribution",
    "geographic_consolidated_operating_margin",
    "geographic_operating_margin_contribution_residual",
    "geographic_operating_margin_contribution_change",
    "geographic_reconciling_operating_margin_contribution_change",
    "geographic_consolidated_operating_margin_change",
    "geographic_operating_margin_contribution_change_residual",
    "geographic_operating_margin_mix_effect",
    "geographic_operating_margin_within_segment_effect",
    "geographic_operating_margin_mix_within_residual",
    "geographic_operating_profit_amount_change",
    "geographic_reconciling_operating_profit_amount_change",
    "geographic_consolidated_operating_profit_amount_change",
    "geographic_operating_profit_amount_change_residual",
    "geographic_operating_profit_revenue_effect",
    "geographic_operating_profit_margin_effect",
)
_OPERATING_KPI_FAMILY_SERIES = (
    "store_count_net_change",
    "store_count_growth",
    REVENUE_STORE_GROWTH_FAMILY_ID,
    REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
    COMPARABLE_SALES_CHANGE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
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

_GOODWILL_INTANGIBLES_FAMILY_SERIES = (
    "goodwill_change",
    "goodwill_growth",
    "average_goodwill",
    "goodwill_to_revenue",
    "intangible_assets_change",
    "intangible_assets_growth",
    "average_intangible_assets",
    "intangible_assets_to_revenue",
    "goodwill_and_intangibles_change",
    "goodwill_and_intangibles_growth",
    "average_goodwill_and_intangibles",
    "goodwill_and_intangibles_to_revenue",
    "intangible_payments",
    "intangible_payments_to_revenue",
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
    series: dict[str, tuple[float | str | None, ...]] = {
        "operating_cash_flow_link": earnings_quality.operating_cash_flow,
        "cash_conversion_ratio": earnings_quality.cash_conversion_ratio,
        "total_accruals": earnings_quality.total_accruals,
        "average_total_assets": earnings_quality.average_total_assets,
        "accrual_ratio": earnings_quality.accrual_ratio,
    }
    if earnings_quality.operating_cash_flow_less_sbc is not None:
        if (
            earnings_quality.sbc_to_revenue is None
            or earnings_quality.sbc_to_operating_cash_flow is None
        ):
            raise ValueError(
                "SBC ratio series are required when "
                "operating_cash_flow_less_sbc is present"
            )
        series["sbc_to_revenue"] = earnings_quality.sbc_to_revenue
        series["sbc_to_operating_cash_flow"] = (
            earnings_quality.sbc_to_operating_cash_flow
        )
        series["operating_cash_flow_less_sbc"] = (
            earnings_quality.operating_cash_flow_less_sbc
        )
    catalog_ids = {family.id for family in QUALITY_COMPONENT_CATALOG}
    required = set(_QUALITY_BASE_FAMILY_SERIES)
    if earnings_quality.operating_cash_flow_less_sbc is not None:
        required |= set(_QUALITY_SBC_FAMILY_SERIES)
    if set(series) != required or not required <= catalog_ids:
        missing = sorted(required - set(series))
        extra = sorted(set(series) - required)
        raise ValueError(
            f"earnings_quality_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _QUALITY_FAMILY_SERIES
        if family_id in series
    }


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


def lease_rou_expected_series(
    lease_rou: LeaseRouSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map lease-ROU diagnostic families from a LeaseRouSeries."""
    series = {
        "rou_assets_change": lease_rou.rou_assets_change,
        "rou_assets_growth": lease_rou.rou_assets_growth,
        "average_rou_assets": lease_rou.average_rou_assets,
        "rou_assets_to_revenue": lease_rou.rou_assets_to_revenue,
    }
    expected_ids = {family.id for family in LEASE_ROU_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "lease_rou_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _LEASE_ROU_FAMILY_SERIES}


def deferred_tax_expected_series(
    deferred_tax: DeferredTaxSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map deferred-tax diagnostic families from a DeferredTaxSeries."""
    series = {
        "net_deferred_tax_position": deferred_tax.net_deferred_tax_position,
        "deferred_tax_assets_change": deferred_tax.deferred_tax_assets_change,
        "deferred_tax_liabilities_change": (
            deferred_tax.deferred_tax_liabilities_change
        ),
        "net_deferred_tax_position_change": (
            deferred_tax.net_deferred_tax_position_change
        ),
    }
    expected_ids = {family.id for family in DEFERRED_TAX_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "deferred_tax_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id] for family_id in _DEFERRED_TAX_FAMILY_SERIES
    }


def capex_expected_series(
    capex: CapexSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map capex practice families from a CapexSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {
        "ppe_capex": capex.ppe_capex,
        "ppe_capex_to_revenue": capex.ppe_capex_to_revenue,
    }
    if capex.cash_after_ppe_capex is not None:
        if capex.cash_after_ppe_capex_to_revenue is None:
            raise ValueError(
                "cash_after_ppe_capex_to_revenue is required when "
                "cash_after_ppe_capex is present"
            )
        series["cash_after_ppe_capex"] = capex.cash_after_ppe_capex
        series["cash_after_ppe_capex_to_revenue"] = (
            capex.cash_after_ppe_capex_to_revenue
        )
    catalog_ids = {family.id for family in CAPEX_COMPONENT_CATALOG}
    required = set(_CAPEX_BASE_FAMILY_SERIES)
    if capex.cash_after_ppe_capex is not None:
        required |= set(_CAPEX_CASH_AFTER_FAMILY_SERIES)
    if set(series) != required or not required <= catalog_ids:
        missing = sorted(required - set(series))
        extra = sorted(set(series) - required)
        raise ValueError(
            "capex_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _CAPEX_FAMILY_SERIES
        if family_id in series
    }


def lease_repayment_expected_series(
    lease_repayment: LeaseRepaymentSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map lease-repayment practice families from a LeaseRepaymentSeries."""
    series = {
        "lease_repayments": lease_repayment.lease_repayments,
        "lease_repayments_to_revenue": lease_repayment.lease_repayments_to_revenue,
    }
    expected_ids = {family.id for family in LEASE_REPAYMENT_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "lease_repayment_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id] for family_id in _LEASE_REPAYMENT_FAMILY_SERIES
    }


def acquisition_cash_expected_series(
    acquisition_cash: AcquisitionCashSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map acquisition-cash practice families from an AcquisitionCashSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {
        "acquisition_cash_outflow": acquisition_cash.acquisition_cash_outflow,
        "acquisition_cash_to_revenue": acquisition_cash.acquisition_cash_to_revenue,
    }
    if acquisition_cash.cash_after_ppe_capex_and_acquisitions is not None:
        series["cash_after_ppe_capex_and_acquisitions"] = (
            acquisition_cash.cash_after_ppe_capex_and_acquisitions
        )
    catalog_ids = {family.id for family in ACQUISITION_CASH_COMPONENT_CATALOG}
    required = set(_ACQUISITION_CASH_BASE_FAMILY_SERIES)
    if acquisition_cash.cash_after_ppe_capex_and_acquisitions is not None:
        required |= set(_ACQUISITION_CASH_RESIDUAL_FAMILY_SERIES)
    if set(series) != required or not required <= catalog_ids:
        missing = sorted(required - set(series))
        extra = sorted(set(series) - required)
        raise ValueError(
            "acquisition_cash_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _ACQUISITION_CASH_FAMILY_SERIES
        if family_id in series
    }


def share_repurchase_expected_series(
    share_repurchase: ShareRepurchaseSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map share-repurchase practice families from a ShareRepurchaseSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {
        "share_repurchase_outflow": share_repurchase.share_repurchase_outflow,
        "share_repurchase_to_revenue": share_repurchase.share_repurchase_to_revenue,
    }
    if share_repurchase.cash_after_ppe_capex_acquisitions_and_repurchases is not None:
        series["cash_after_ppe_capex_acquisitions_and_repurchases"] = (
            share_repurchase.cash_after_ppe_capex_acquisitions_and_repurchases
        )
    catalog_ids = {family.id for family in SHARE_REPURCHASE_COMPONENT_CATALOG}
    required = set(_SHARE_REPURCHASE_BASE_FAMILY_SERIES)
    if share_repurchase.cash_after_ppe_capex_acquisitions_and_repurchases is not None:
        required |= set(_SHARE_REPURCHASE_RESIDUAL_FAMILY_SERIES)
    if set(series) != required or not required <= catalog_ids:
        missing = sorted(required - set(series))
        extra = sorted(set(series) - required)
        raise ValueError(
            "share_repurchase_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _SHARE_REPURCHASE_FAMILY_SERIES
        if family_id in series
    }


def cash_rollforward_expected_series(
    cash_rollforward: CashRollforwardSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map cash-roll-forward practice families from a CashRollforwardSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {
        "cash_movement_from_flows": cash_rollforward.cash_movement_from_flows,
    }
    if cash_rollforward.cash_movement_difference is not None:
        series["cash_movement_difference"] = cash_rollforward.cash_movement_difference
    if cash_rollforward.cash_ending_from_flows is not None:
        series["cash_ending_from_flows"] = cash_rollforward.cash_ending_from_flows
    if cash_rollforward.cash_ending_difference is not None:
        series["cash_ending_difference"] = cash_rollforward.cash_ending_difference
    catalog_ids = {family.id for family in CASH_ROLLFORWARD_COMPONENT_CATALOG}
    required = set(_CASH_ROLLFORWARD_BASE_FAMILY_SERIES)
    if cash_rollforward.cash_movement_difference is not None:
        required.add("cash_movement_difference")
    if cash_rollforward.cash_ending_from_flows is not None:
        required.add("cash_ending_from_flows")
    if cash_rollforward.cash_ending_difference is not None:
        required.add("cash_ending_difference")
    if set(series) != required or not required <= catalog_ids:
        missing = sorted(required - set(series))
        extra = sorted(set(series) - required)
        raise ValueError(
            "cash_rollforward_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _CASH_ROLLFORWARD_FAMILY_SERIES
        if family_id in series
    }


def reported_margin_expected_series(
    reported_margin: ReportedMarginSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map reported-margin practice families from a ReportedMarginSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {}
    if reported_margin.gross_margin is not None:
        series["gross_margin"] = reported_margin.gross_margin
    if reported_margin.reported_operating_margin is not None:
        series["reported_operating_margin"] = reported_margin.reported_operating_margin
    if reported_margin.net_operating_expense_burden is not None:
        series["net_operating_expense_burden"] = (
            reported_margin.net_operating_expense_burden
        )
    if reported_margin.gross_margin_change is not None:
        series["gross_margin_change"] = reported_margin.gross_margin_change
    if reported_margin.net_operating_expense_burden_change is not None:
        series["net_operating_expense_burden_change"] = (
            reported_margin.net_operating_expense_burden_change
        )
    if reported_margin.reconstructed_operating_margin_change is not None:
        series["reconstructed_operating_margin_change"] = (
            reported_margin.reconstructed_operating_margin_change
        )
    catalog_ids = {family.id for family in REPORTED_MARGIN_COMPONENT_CATALOG}
    if not set(series) <= catalog_ids:
        extra = sorted(set(series) - catalog_ids)
        raise ValueError(
            "reported_margin_expected_series family mismatch; "
            f"extra={extra}"
        )
    if not series:
        raise ValueError("reported_margin_expected_series has no applicable families")
    return {
        family_id: series[family_id]
        for family_id in _REPORTED_MARGIN_FAMILY_SERIES
        if family_id in series
    }


def inventory_analysis_expected_series(
    inventory_analysis: InventoryAnalysisSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map inventory-analysis practice families from an InventoryAnalysisSeries."""
    series: dict[str, tuple[float | str | None, ...]] = {
        "inventory_change": inventory_analysis.inventory_change,
        "inventory_balance_implied_cf_adjustment": (
            inventory_analysis.inventory_balance_implied_cf_adjustment
        ),
    }
    if inventory_analysis.inventory_intensity is not None:
        series["inventory_intensity"] = inventory_analysis.inventory_intensity
    if inventory_analysis.inventory_revenue_scale_effect is not None:
        series["inventory_revenue_scale_effect"] = (
            inventory_analysis.inventory_revenue_scale_effect
        )
    if inventory_analysis.inventory_intensity_effect is not None:
        series["inventory_intensity_effect"] = (
            inventory_analysis.inventory_intensity_effect
        )
    if inventory_analysis.reconstructed_inventory_change is not None:
        series["reconstructed_inventory_change"] = (
            inventory_analysis.reconstructed_inventory_change
        )
    if inventory_analysis.inventory_cf_adjustment_difference is not None:
        series["inventory_cf_adjustment_difference"] = (
            inventory_analysis.inventory_cf_adjustment_difference
        )
    catalog_ids = {family.id for family in INVENTORY_ANALYSIS_COMPONENT_CATALOG}
    if not set(series) <= catalog_ids:
        extra = sorted(set(series) - catalog_ids)
        raise ValueError(
            "inventory_analysis_expected_series family mismatch; "
            f"extra={extra}"
        )
    if not series:
        raise ValueError("inventory_analysis_expected_series has no applicable families")
    return {
        family_id: series[family_id]
        for family_id in _INVENTORY_ANALYSIS_FAMILY_SERIES
        if family_id in series
    }


def _geographic_component_identity(component_id: str) -> str:
    parts = component_id.split("__")
    if len(parts) == 2:
        return ""
    if len(parts) != 3:
        raise ValueError(f"malformed geographic component id {component_id!r}")
    return parts[1]


def geographic_expected_value_for_component(
    geographic: GeographicSegmentSeries,
    component: ResolvedComponent,
) -> float | str | None:
    """Look up one geographic practice expected from the validated series."""
    catalog_ids = {family.id for family in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG}
    if component.family_id not in catalog_ids:
        raise ValueError(
            f"geographic_expected_value_for_component unknown family "
            f"{component.family_id!r}"
        )
    if not component.period_end:
        raise ValueError(
            f"geographic component {component.id!r} is missing period_end"
        )
    period = date.fromisoformat(component.period_end)
    identity = _geographic_component_identity(component.id)
    family_id = component.family_id
    if family_id == "geographic_revenue_share":
        return geographic.revenue_share[period][identity]
    if family_id == "geographic_revenue_growth":
        return geographic.revenue_growth[period][identity]
    if family_id == "geographic_reported_operating_margin":
        return geographic.reported_operating_margin[period][identity]
    if family_id == "geographic_calculated_segment_revenue_total":
        return geographic.calculated_segment_revenue_total[period]
    if family_id == "geographic_calculated_segment_operating_profit_total":
        return geographic.calculated_segment_operating_profit_total[period]
    if family_id == "geographic_signed_reconciling_contribution":
        contributions = geographic.signed_reconciling_contributions[period]
        if isinstance(contributions, str):
            return contributions
        for name, amount in contributions:
            if name == identity:
                return amount
        raise ValueError(
            f"geographic signed contribution {identity!r} missing for "
            f"{period.isoformat()}"
        )
    if family_id == "geographic_reconstructed_consolidated_operating_profit":
        return geographic.reconstructed_consolidated_operating_profit[period]
    if family_id == "geographic_consolidated_revenue_difference":
        return geographic.consolidated_revenue_difference[period]
    if family_id == "geographic_consolidated_operating_profit_difference":
        return geographic.consolidated_operating_profit_difference[period]
    if family_id == "geographic_revenue_growth_contribution":
        return geographic.revenue_growth_contribution[period][identity]
    if family_id == "geographic_consolidated_revenue_growth":
        return geographic.consolidated_revenue_growth[period]
    if family_id == "geographic_revenue_growth_contribution_residual":
        return geographic.revenue_growth_contribution_residual[period]
    if family_id == "geographic_operating_margin_contribution":
        return geographic.operating_margin_contribution[period][identity]
    if family_id == "geographic_reconciling_operating_margin_contribution":
        return geographic.reconciling_operating_margin_contribution[period]
    if family_id == "geographic_consolidated_operating_margin":
        return geographic.consolidated_operating_margin[period]
    if family_id == "geographic_operating_margin_contribution_residual":
        return geographic.operating_margin_contribution_residual[period]
    if family_id == "geographic_operating_margin_contribution_change":
        return geographic.operating_margin_contribution_change[period][identity]
    if family_id == "geographic_reconciling_operating_margin_contribution_change":
        return geographic.reconciling_operating_margin_contribution_change[period]
    if family_id == "geographic_consolidated_operating_margin_change":
        return geographic.consolidated_operating_margin_change[period]
    if family_id == "geographic_operating_margin_contribution_change_residual":
        return geographic.operating_margin_contribution_change_residual[period]
    if family_id == "geographic_operating_margin_mix_effect":
        return geographic.operating_margin_mix_effect[period][identity]
    if family_id == "geographic_operating_margin_within_segment_effect":
        return geographic.operating_margin_within_segment_effect[period][identity]
    if family_id == "geographic_operating_margin_mix_within_residual":
        return geographic.operating_margin_mix_within_residual[period]
    if family_id == "geographic_operating_profit_amount_change":
        return geographic.operating_profit_amount_change[period][identity]
    if family_id == "geographic_reconciling_operating_profit_amount_change":
        return geographic.reconciling_operating_profit_amount_change[period]
    if family_id == "geographic_consolidated_operating_profit_amount_change":
        return geographic.consolidated_operating_profit_amount_change[period]
    if family_id == "geographic_operating_profit_amount_change_residual":
        return geographic.operating_profit_amount_change_residual[period]
    if family_id == "geographic_operating_profit_revenue_effect":
        return geographic.operating_profit_revenue_effect[period][identity]
    if family_id == "geographic_operating_profit_margin_effect":
        return geographic.operating_profit_margin_effect[period][identity]
    raise ValueError(f"Unknown geographic family {family_id!r}")


def operating_kpi_expected_value_for_component(
    operating_kpi: OperatingKpiSeries | None,
    component: ResolvedComponent,
    *,
    operating_kpi_relationship: OperatingKpiRevenueStoreRelationship | None = None,
    operating_kpi_compsales_relationship: (
        OperatingKpiRevenueComparableSalesRelationship | None
    ) = None,
    operating_kpi_spsf_relationship: (
        OperatingKpiRevenueSalesPerSquareFootRelationship | None
    ) = None,
    management_kpi: ManagementKpiSeries | None = None,
) -> float | str | None:
    """Look up one store-count, revenue/store, or management-KPI expected."""
    store_ids = {family.id for family in STORE_COUNT_COMPONENT_CATALOG}
    relationship_ids = {family.id for family in REVENUE_STORE_COMPONENT_CATALOG}
    compsales_ids = {family.id for family in COMPARABLE_SALES_COMPONENT_CATALOG}
    spsf_management_ids = {
        SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    }
    management_ids = {
        COMPARABLE_SALES_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    }
    if not component.period_end:
        raise ValueError(
            f"operating KPI component {component.id!r} is missing period_end"
        )
    period = date.fromisoformat(component.period_end)
    if component.family_id == SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID:
        if operating_kpi_spsf_relationship is None:
            raise ValueError(
                f"Operating-KPI family {component.family_id!r} requires an "
                "OperatingKpiRevenueSalesPerSquareFootRelationship"
            )
        identity = comparable_sales_identity_from_component(
            component, operating_kpi_spsf_relationship.identities
        )
        return operating_kpi_spsf_relationship.series[identity].growth_difference_pp[
            period
        ]
    if component.family_id in management_ids or component.family_id in spsf_management_ids:
        if management_kpi is None:
            raise ValueError(
                f"Operating-KPI family {component.family_id!r} requires a "
                "ManagementKpiSeries"
            )
        identity = comparable_sales_identity_from_component(
            component, management_kpi.identities
        )
        series = management_kpi.series[identity]
        if component.family_id in {
            COMPARABLE_SALES_CHANGE_FAMILY_ID,
            SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        }:
            return series.adjacent_change[period]
        if component.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID:
            return series.growth[period]
        raise ValueError(f"Unknown operating KPI family {component.family_id!r}")
    if component.family_id in compsales_ids:
        if operating_kpi_compsales_relationship is None:
            raise ValueError(
                f"Operating-KPI family {component.family_id!r} requires an "
                "OperatingKpiRevenueComparableSalesRelationship"
            )
        identity = comparable_sales_identity_from_component(
            component, operating_kpi_compsales_relationship.identities
        )
        if component.family_id == COMPARABLE_SALES_DIFFERENCE_FAMILY_ID:
            return operating_kpi_compsales_relationship.series[identity].growth_difference_pp[
                period
            ]
        raise ValueError(f"Unknown operating KPI family {component.family_id!r}")
    if component.family_id in relationship_ids:
        if component.family_id == REVENUE_STORE_GROWTH_FAMILY_ID:
            if operating_kpi_relationship is not None:
                return operating_kpi_relationship.revenue_growth[period]
            if operating_kpi_compsales_relationship is not None:
                first = operating_kpi_compsales_relationship.series[
                    operating_kpi_compsales_relationship.identities[0]
                ]
                return first.revenue_growth[period]
            if operating_kpi_spsf_relationship is not None:
                first = operating_kpi_spsf_relationship.series[
                    operating_kpi_spsf_relationship.identities[0]
                ]
                return first.revenue_growth[period]
            raise ValueError(
                f"Operating-KPI family {component.family_id!r} requires a "
                "revenue-growth relationship"
            )
        if component.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID:
            if operating_kpi_relationship is None:
                raise ValueError(
                    f"Operating-KPI family {component.family_id!r} requires an "
                    "OperatingKpiRevenueStoreRelationship"
                )
            return operating_kpi_relationship.growth_difference_pp[period]
        raise ValueError(f"Unknown operating KPI family {component.family_id!r}")
    if component.family_id not in store_ids:
        raise ValueError(
            f"operating_kpi_expected_value_for_component unknown family "
            f"{component.family_id!r}"
        )
    if operating_kpi is None:
        raise ValueError(
            f"Operating-KPI family {component.family_id!r} requires an OperatingKpiSeries"
        )
    family_id = component.family_id
    if family_id == "store_count_net_change":
        return operating_kpi.net_count_change[period]
    if family_id == "store_count_growth":
        return operating_kpi.growth[period]
    raise ValueError(f"Unknown operating KPI family {family_id!r}")


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


def goodwill_intangibles_expected_series(
    goodwill_intangibles: GoodwillIntangiblesSeries,
    availability: GoodwillIntangiblesAvailability,
) -> dict[str, tuple[float | str | None, ...]]:
    """Map available goodwill/intangibles families from a series + availability."""
    series: dict[str, tuple[float | str | None, ...]] = {}
    if availability.goodwill and goodwill_intangibles.goodwill is not None:
        gw = goodwill_intangibles.goodwill
        series.update(
            {
                "goodwill_change": gw.change,
                "goodwill_growth": gw.growth,
                "average_goodwill": gw.average,
                "goodwill_to_revenue": gw.to_revenue,
            }
        )
    if (
        availability.intangible_assets
        and goodwill_intangibles.intangible_assets is not None
    ):
        ia = goodwill_intangibles.intangible_assets
        series.update(
            {
                "intangible_assets_change": ia.change,
                "intangible_assets_growth": ia.growth,
                "average_intangible_assets": ia.average,
                "intangible_assets_to_revenue": ia.to_revenue,
            }
        )
    if (
        availability.goodwill_and_intangibles
        and goodwill_intangibles.goodwill_and_intangibles is not None
    ):
        comb = goodwill_intangibles.goodwill_and_intangibles
        series.update(
            {
                "goodwill_and_intangibles_change": comb.change,
                "goodwill_and_intangibles_growth": comb.growth,
                "average_goodwill_and_intangibles": comb.average,
                "goodwill_and_intangibles_to_revenue": comb.to_revenue,
            }
        )
    if (
        availability.payments_for_intangible_assets
        and goodwill_intangibles.intangible_payments is not None
        and goodwill_intangibles.intangible_payments_to_revenue is not None
    ):
        series.update(
            {
                "intangible_payments": goodwill_intangibles.intangible_payments,
                "intangible_payments_to_revenue": (
                    goodwill_intangibles.intangible_payments_to_revenue
                ),
            }
        )

    catalog_ids = {family.id for family in GOODWILL_INTANGIBLES_COMPONENT_CATALOG}
    if not set(series).issubset(catalog_ids):
        extra = sorted(set(series) - catalog_ids)
        raise ValueError(
            "goodwill_intangibles_expected_series family mismatch; "
            f"extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _GOODWILL_INTANGIBLES_FAMILY_SERIES
        if family_id in series
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
    lease_rou: LeaseRouSeries | None = None,
    deferred_tax: DeferredTaxSeries | None = None,
    ownership_attribution: OwnershipAttributionSeries | None = None,
    goodwill_intangibles: GoodwillIntangiblesSeries | None = None,
    goodwill_intangibles_availability: GoodwillIntangiblesAvailability | None = None,
    capex: CapexSeries | None = None,
    lease_repayment: LeaseRepaymentSeries | None = None,
    acquisition_cash: AcquisitionCashSeries | None = None,
    share_repurchase: ShareRepurchaseSeries | None = None,
    cash_rollforward: CashRollforwardSeries | None = None,
    reported_margin: ReportedMarginSeries | None = None,
    inventory_analysis: InventoryAnalysisSeries | None = None,
    geographic: GeographicSegmentSeries | None = None,
    operating_kpi: OperatingKpiSeries | None = None,
    operating_kpi_relationship: OperatingKpiRevenueStoreRelationship | None = None,
    operating_kpi_compsales_relationship: (
        OperatingKpiRevenueComparableSalesRelationship | None
    ) = None,
    operating_kpi_spsf_relationship: (
        OperatingKpiRevenueSalesPerSquareFootRelationship | None
    ) = None,
    management_kpi: ManagementKpiSeries | None = None,
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

    if family_id in _GOODWILL_INTANGIBLES_FAMILY_SERIES:
        if goodwill_intangibles is None or goodwill_intangibles_availability is None:
            raise ValueError(
                f"Goodwill/intangibles family {family_id!r} requires a "
                "GoodwillIntangiblesSeries and availability"
            )
        series = goodwill_intangibles_expected_series(
            goodwill_intangibles, goodwill_intangibles_availability
        )
    elif family_id in _OWNERSHIP_ATTRIBUTION_FAMILY_SERIES:
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
    elif family_id in _LEASE_ROU_FAMILY_SERIES:
        if lease_rou is None:
            raise ValueError(
                f"Lease-ROU family {family_id!r} requires a LeaseRouSeries"
            )
        series = lease_rou_expected_series(lease_rou)
    elif family_id in _DEFERRED_TAX_FAMILY_SERIES:
        if deferred_tax is None:
            raise ValueError(
                f"Deferred-tax family {family_id!r} requires a DeferredTaxSeries"
            )
        series = deferred_tax_expected_series(deferred_tax)
    elif family_id in _CAPEX_FAMILY_SERIES:
        if capex is None:
            raise ValueError(f"Capex family {family_id!r} requires a CapexSeries")
        series = capex_expected_series(capex)
        if family_id not in series:
            raise ValueError(
                f"Capex family {family_id!r} requires unambiguous operating cash flow"
            )
    elif family_id in _LEASE_REPAYMENT_FAMILY_SERIES:
        if lease_repayment is None:
            raise ValueError(
                f"Lease-repayment family {family_id!r} requires a LeaseRepaymentSeries"
            )
        series = lease_repayment_expected_series(lease_repayment)
    elif family_id in _ACQUISITION_CASH_FAMILY_SERIES:
        if acquisition_cash is None:
            raise ValueError(
                f"Acquisition-cash family {family_id!r} requires an "
                "AcquisitionCashSeries"
            )
        series = acquisition_cash_expected_series(acquisition_cash)
        if family_id not in series:
            raise ValueError(
                f"Acquisition-cash family {family_id!r} requires unambiguous "
                "operating cash flow and PP&E capex"
            )
    elif family_id in _SHARE_REPURCHASE_FAMILY_SERIES:
        if share_repurchase is None:
            raise ValueError(
                f"Share-repurchase family {family_id!r} requires a "
                "ShareRepurchaseSeries"
            )
        series = share_repurchase_expected_series(share_repurchase)
        if family_id not in series:
            raise ValueError(
                f"Share-repurchase family {family_id!r} requires unambiguous "
                "operating cash flow, PP&E capex, and acquisition cash"
            )
    elif family_id in _CASH_ROLLFORWARD_FAMILY_SERIES:
        if cash_rollforward is None:
            raise ValueError(
                f"Cash-roll-forward family {family_id!r} requires a "
                "CashRollforwardSeries"
            )
        series = cash_rollforward_expected_series(cash_rollforward)
        if family_id not in series:
            raise ValueError(
                f"Cash-roll-forward family {family_id!r} requires its unique "
                "source dependencies"
            )
    elif family_id in _REPORTED_MARGIN_FAMILY_SERIES:
        if reported_margin is None:
            raise ValueError(
                f"Reported-margin family {family_id!r} requires a "
                "ReportedMarginSeries"
            )
        series = reported_margin_expected_series(reported_margin)
        if family_id not in series:
            raise ValueError(
                f"Reported-margin family {family_id!r} requires its unique "
                "source dependencies"
            )
    elif family_id in _INVENTORY_ANALYSIS_FAMILY_SERIES:
        if inventory_analysis is None:
            raise ValueError(
                f"Inventory-analysis family {family_id!r} requires an "
                "InventoryAnalysisSeries"
            )
        series = inventory_analysis_expected_series(inventory_analysis)
        if family_id not in series:
            raise ValueError(
                f"Inventory-analysis family {family_id!r} requires its unique "
                "source dependencies"
            )
    elif family_id in _GEOGRAPHIC_FAMILY_SERIES:
        if geographic is None:
            raise ValueError(
                f"Geographic family {family_id!r} requires a GeographicSegmentSeries"
            )
        return geographic_expected_value_for_component(geographic, component)
    elif family_id in _OPERATING_KPI_FAMILY_SERIES:
        compsales_ids = {family.id for family in COMPARABLE_SALES_COMPONENT_CATALOG}
        relationship_ids = {family.id for family in REVENUE_STORE_COMPONENT_CATALOG}
        spsf_management_ids = {
            SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
            SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        }
        management_ids = {
            COMPARABLE_SALES_CHANGE_FAMILY_ID,
            SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
            SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        }
        if family_id == SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID:
            if operating_kpi_spsf_relationship is None:
                raise ValueError(
                    f"Operating-KPI family {family_id!r} requires an "
                    "OperatingKpiRevenueSalesPerSquareFootRelationship"
                )
            return operating_kpi_expected_value_for_component(
                operating_kpi,
                component,
                operating_kpi_spsf_relationship=operating_kpi_spsf_relationship,
            )
        if family_id in management_ids or family_id in spsf_management_ids:
            if management_kpi is None:
                raise ValueError(
                    f"Operating-KPI family {family_id!r} requires a "
                    "ManagementKpiSeries"
                )
            return operating_kpi_expected_value_for_component(
                operating_kpi,
                component,
                management_kpi=management_kpi,
            )
        if family_id in compsales_ids:
            if operating_kpi_compsales_relationship is None:
                raise ValueError(
                    f"Operating-KPI family {family_id!r} requires an "
                    "OperatingKpiRevenueComparableSalesRelationship"
                )
            return operating_kpi_expected_value_for_component(
                operating_kpi,
                component,
                operating_kpi_compsales_relationship=(
                    operating_kpi_compsales_relationship
                ),
            )
        if family_id in relationship_ids:
            if (
                operating_kpi_relationship is None
                and operating_kpi_compsales_relationship is None
                and operating_kpi_spsf_relationship is None
            ):
                raise ValueError(
                    f"Operating-KPI family {family_id!r} requires a "
                    "revenue-growth relationship"
                )
            if family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID and operating_kpi is None:
                raise ValueError(
                    f"Operating-KPI family {family_id!r} requires an OperatingKpiSeries"
                )
            return operating_kpi_expected_value_for_component(
                operating_kpi,
                component,
                operating_kpi_relationship=operating_kpi_relationship,
                operating_kpi_compsales_relationship=(
                    operating_kpi_compsales_relationship
                ),
                operating_kpi_spsf_relationship=operating_kpi_spsf_relationship,
            )
        if operating_kpi is None:
            raise ValueError(
                f"Operating-KPI family {family_id!r} requires an OperatingKpiSeries"
            )
        return operating_kpi_expected_value_for_component(operating_kpi, component)
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
