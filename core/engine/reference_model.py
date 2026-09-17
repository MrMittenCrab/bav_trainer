"""Build the complete reference BAV workbook and semantic component map."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from ..data.historical_segments import (
    IFOP_SEGMENT_TOTAL,
    OP_ADD,
    OP_SUBTRACT,
    REVENUE_SEGMENT_TOTAL,
)
from ..data.interface import LineItem, StandardizedFinancials
from ..data.line_identity import line_identity
from ..model.classification import BALANCE_SHEET_CATEGORIES
from ..model.financial_math import compute_anchor
from ..model.earnings_quality import (
    compute_earnings_quality_series,
    earnings_quality_availability,
    resolve_sbc_source,
)
from ..model.earnings_quality_change import compute_earnings_quality_change_series
from ..model.fixed_asset import (
    compute_fixed_asset_series,
    fixed_asset_applicable,
)
from ..model.geographic_segment import (
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from ..model.operating_kpi import (
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from ..model.operating_kpi_relationships import (
    COMPARABLE_SALES_SCOPE_NOTE,
    SCOPE_NOTE,
    compute_operating_kpi_revenue_comparable_sales_relationship,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_comparable_sales_relationship_applicable,
)
from ..model.goodwill_intangibles import (
    compute_goodwill_intangibles_series,
    goodwill_intangibles_applicable,
    goodwill_intangibles_availability,
    resolve_goodwill_intangibles_sources,
)
from ..model.lease_liability import (
    compute_lease_liability_series,
    lease_liability_applicable,
    resolve_lease_liability_source,
)
from ..model.deferred_tax import (
    compute_deferred_tax_series,
    deferred_tax_applicable,
    resolve_deferred_tax_sources,
)
from ..model.acquisition_cash import (
    compute_acquisition_cash_series,
    acquisition_cash_applicable,
    resolve_acquisition_cash_source,
)
from ..model.share_repurchase import (
    compute_share_repurchase_series,
    share_repurchase_applicable,
    resolve_share_repurchase_source,
)
from ..model.cash_rollforward import (
    BEGINNING_CONCEPT,
    CHANGE_CONCEPT,
    ENDING_CONCEPT,
    FINANCING_CONCEPT,
    FX_CONCEPT,
    INVESTING_CONCEPT,
    OPERATING_CONCEPT,
    compute_cash_rollforward_series,
    cash_rollforward_applicable,
    cash_ending_difference_applicable,
    cash_ending_from_flows_applicable,
    cash_movement_difference_applicable,
    resolve_cash_rollforward_sources,
)
from ..model.reported_margin import (
    GROSS_PROFIT_CONCEPT,
    OPERATING_PROFIT_CONCEPT,
    REVENUE_CONCEPT,
    compute_reported_margin_series,
    gross_margin_applicable,
    gross_margin_change_applicable,
    net_operating_expense_burden_applicable,
    net_operating_expense_burden_change_applicable,
    reconstructed_operating_margin_change_applicable,
    reported_margin_applicable,
    reported_operating_margin_applicable,
    resolve_reported_margin_sources,
)
from ..model.inventory_analysis import (
    CHANGE_IN_INVENTORIES_CONCEPT,
    INVENTORIES_CONCEPT,
    compute_inventory_analysis_series,
    inventory_analysis_applicable,
    inventory_balance_implied_cf_adjustment_applicable,
    inventory_cf_adjustment_difference_applicable,
    inventory_change_applicable,
    inventory_intensity_applicable,
    inventory_intensity_effect_applicable,
    inventory_revenue_scale_effect_applicable,
    reconstructed_inventory_change_applicable,
    resolve_inventory_analysis_sources,
)
from ..model.capex import (
    compute_capex_series,
    capex_applicable,
    resolve_capex_source,
    resolve_operating_cash_source,
)
from ..model.lease_repayment import (
    compute_lease_repayment_series,
    lease_repayment_applicable,
    resolve_lease_repayment_source,
)
from ..model.lease_rou import (
    compute_lease_rou_series,
    lease_rou_applicable,
    resolve_lease_rou_source,
)
from ..model.ownership_attribution import (
    compute_ownership_attribution_series,
    ownership_attribution_applicable,
)
from ..model.judgment import JudgmentCase, classification_judgment_cases
from ..model.line_resolver import resolve_line, workbook_row_for
from ..model.normalization import (
    NormalizationCase,
    compute_normalization_series,
    normalization_cases,
)
from ..model.period_axis import canonical_fiscal_periods
from ..model.normalized_per_share import compute_normalized_per_share_series
from ..model.per_share import compute_per_share_series, per_share_available
from ..model.per_share_attribution import compute_per_share_attribution_series
from ..model.profitability_change import compute_profitability_change_series
from ..model.profitability_drivers import compute_profitability_driver_series
from ..model.ratio_values import SOURCE_UNAVAILABLE, is_source_unavailable
from ..model.roe_attribution import compute_roe_attribution_series
from ..model.ri_engine import run_scenario, weighted_ivps
from ..model.source_availability import (
    assess_interest_availability,
    availability_payload,
    filter_available_specs,
)
from ..model.working_capital import (
    compute_working_capital_series,
    working_capital_applicable,
)
from .component_catalog import (
    DEFERRED_COMPONENT_SPECS,
    GEOGRAPHIC_SEGMENT_IDENTITIES,
    GEOGRAPHIC_SHEET_NAME,
    expand_acquisition_cash_specs,
    expand_share_repurchase_specs,
    expand_cash_rollforward_specs,
    expand_reported_margin_specs,
    expand_inventory_analysis_specs,
    expand_geographic_segment_specs,
    expand_store_count_source_specs,
    expand_store_count_specs,
    expand_revenue_store_source_specs,
    expand_revenue_store_specs,
    expand_comparable_sales_source_specs,
    expand_comparable_sales_specs,
    expand_capex_specs,
    geographic_component_id,
    geographic_identity_label,
    geographic_spec_identity,
    STORE_COUNT_POPULATION_LABEL,
    STORE_COUNT_SHEET_NAME,
    STORE_COUNT_SOURCE_FAMILY_ID,
    REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    REVENUE_STORE_GROWTH_FAMILY_ID,
    REVENUE_STORE_SOURCE_FAMILY_ID,
    COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
    COMPARABLE_SALES_PCT_FORMAT,
    COMPARABLE_SALES_SHEET_NAME,
    COMPARABLE_SALES_SOURCE_FAMILY_ID,
    StoreCountSourceRef,
    SemanticCellRef,
    comparable_sales_identity_label,
    comparable_sales_identity_token,
    comparable_sales_source_component_id,
    resolve_revenue_comparable_sales_difference_formula,
    resolve_revenue_store_difference_formula,
    resolve_revenue_store_growth_formula,
    resolve_store_count_growth_formula,
    resolve_store_count_net_change_formula,
    revenue_store_component_id,
    revenue_store_source_component_id,
    store_count_component_id,
    store_count_source_component_id,
    store_count_source_map_formula,
    expand_fixed_asset_specs,
    expand_goodwill_intangibles_specs,
    expand_historical_specs,
    expand_lease_liability_specs,
    expand_deferred_tax_specs,
    expand_lease_repayment_specs,
    expand_lease_rou_specs,
    expand_ownership_attribution_specs,
    expand_normalization_specs,
    expand_normalized_per_share_specs,
    expand_per_share_attribution_specs,
    expand_per_share_specs,
    expand_profitability_change_specs,
    expand_profitability_driver_specs,
    expand_quality_change_specs,
    expand_quality_specs,
    expand_roe_attribution_specs,
    expand_working_capital_specs,
)
from .map_embed import embed_component_map_sheet
from .semantic_map import SemanticMap
from .build_contract import (
    complete_build_modules, prepare_complete_build, write_complete_build,
    verify_complete_build,
)
from ..model.historical_expected import (
    historical_expected_series,
    per_share_expected_series,
    profitability_change_expected_series,
    profitability_driver_expected_series,
    roe_attribution_expected_series,
)

NUM_FMT = "#,##0;(#,##0)"
PCT_FMT = "0.0%"
SOURCE_START_ROW = 7
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
ORANGE = PatternFill("solid", start_color="FCE5CD")
YELLOW = PatternFill("solid", start_color="FFF2CC")
GREEN = PatternFill("solid", start_color="D9EAD3")
PRACTICE_YELLOW = PatternFill("solid", start_color="FFFF00")

DEFERRED_TAB_NAMES = ("Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary")
DEFERRED_PLACEHOLDER = "Deferred from historical-only v1"

JUDGMENT_SHEET = "Accounting Judgment"
NORMALIZATION_JUDGMENT_SHEET = "Normalization Judgment"
EARNINGS_NORMALIZATION_SHEET = "Earnings Normalization"
EARNINGS_QUALITY_SHEET = "Earnings Quality"
WORKING_CAPITAL_SHEET = "Working Capital Analysis"
PER_SHARE_SHEET = "Per Share Analysis"
OWNERSHIP_ATTRIBUTION_SHEET = "Ownership Attribution"
GEOGRAPHIC_SHEET = GEOGRAPHIC_SHEET_NAME
STORE_COUNT_SHEET = STORE_COUNT_SHEET_NAME
COMPARABLE_SALES_SHEET = COMPARABLE_SALES_SHEET_NAME
JUDGMENT_INSTRUCTION = (
    "The supplied treatment is the model's reference treatment, not a universal "
    "accounting truth. Compare it with the listed alternative(s), choose the "
    "treatment you would defend, and explain the economic consequence."
)
JUDGMENT_STEP_NOTE = (
    "Choose a treatment in column F only. That choice drives the matching Condensed "
    "Financials classification and downstream historical schedules; leaving F blank "
    "uses the supplied reference treatment. Columns D:E are display context and must "
    "not be edited. Enter your rationale and economic consequence in G:H. Formula Check "
    "grades formula cells against the treatment currently selected in F and validates "
    "that the generated classification links remain intact; it does not grade the "
    "judgment response itself. Do not edit the linked Condensed Financials "
    "classification cell directly."
)
NORMALIZATION_JUDGMENT_INSTRUCTION = (
    "The supplied treatment is the model's reference convention, not a universal "
    "truth. Decide whether each supplied candidate should remain in recurring "
    "earnings or be normalized out."
)
NORMALIZATION_JUDGMENT_STEP_NOTE = (
    "Choose the treatment in column F. Blank F uses the supplied reference treatment. "
    "G:H are ungraded reasoning. Do not edit the generated Earnings Normalization "
    "treatment link directly."
)


def _geographic_expand_inputs(series) -> tuple[
    tuple[date, ...],
    dict[date, tuple[str, ...]],
    dict[date, tuple[str, ...]],
]:
    available: list[date] = []
    growth_identities: dict[date, tuple[str, ...]] = {}
    bridge_identities: dict[date, tuple[str, ...]] = {}
    for period in series.periods:
        if is_source_unavailable(series.presentation_family[period]):
            continue
        available.append(period)
        growth_ids = tuple(
            name
            for name in GEOGRAPHIC_SEGMENT_IDENTITIES
            if series.revenue_growth[period][name] is not None
            and not is_source_unavailable(series.revenue_growth[period][name])
        )
        if growth_ids:
            growth_identities[period] = growth_ids
        contributions = series.signed_reconciling_contributions[period]
        if not is_source_unavailable(contributions):
            bridge_identities[period] = tuple(name for name, _ in contributions)
    return tuple(available), growth_identities, bridge_identities


def _store_count_expand_inputs(
    series,
) -> tuple[tuple[date, ...], tuple[date, ...], tuple[date, ...]]:
    source_periods: list[date] = []
    change_periods: list[date] = []
    growth_periods: list[date] = []
    for period in series.periods:
        count = series.period_end_count[period]
        if count is not None and not is_source_unavailable(count):
            source_periods.append(period)
        change = series.net_count_change[period]
        if change is not None and not is_source_unavailable(change):
            change_periods.append(period)
        growth = series.growth[period]
        if growth is not None and not is_source_unavailable(growth):
            growth_periods.append(period)
    return tuple(source_periods), tuple(change_periods), tuple(growth_periods)


def _revenue_store_expand_inputs(
    relationship,
) -> tuple[tuple[date, ...], tuple[date, ...], tuple[date, ...]]:
    source_periods: list[date] = []
    growth_periods: list[date] = []
    difference_periods: list[date] = []
    for period in relationship.periods:
        revenue = relationship.revenue[period]
        if revenue is not None and not is_source_unavailable(revenue):
            source_periods.append(period)
        growth = relationship.revenue_growth[period]
        if growth is not None and not is_source_unavailable(growth):
            growth_periods.append(period)
        difference = relationship.growth_difference_pp[period]
        if difference is not None and not is_source_unavailable(difference):
            difference_periods.append(period)
    return tuple(source_periods), tuple(growth_periods), tuple(difference_periods)


def _shared_revenue_expand_inputs(
    periods: tuple[date, ...],
    revenue: dict[date, float | str],
    revenue_growth: dict[date, float | str | None],
) -> tuple[tuple[date, ...], tuple[date, ...]]:
    source_periods: list[date] = []
    growth_periods: list[date] = []
    for period in periods:
        current = revenue[period]
        if current is not None and not is_source_unavailable(current):
            source_periods.append(period)
        growth = revenue_growth[period]
        if growth is not None and not is_source_unavailable(growth):
            growth_periods.append(period)
    return tuple(source_periods), tuple(growth_periods)


def _comparable_sales_expand_inputs(
    relationship,
) -> tuple[dict[str, tuple[date, ...]], dict[str, tuple[date, ...]]]:
    source_periods: dict[str, tuple[date, ...]] = {}
    difference_periods: dict[str, tuple[date, ...]] = {}
    for identity in relationship.identities:
        series = relationship.series[identity]
        sources: list[date] = []
        differences: list[date] = []
        for period in relationship.periods:
            compsales = series.comparable_sales_growth[period]
            if compsales is not None and not is_source_unavailable(compsales):
                sources.append(period)
            difference = series.growth_difference_pp[period]
            if difference is not None and not is_source_unavailable(difference):
                differences.append(period)
        source_periods[identity] = tuple(sources)
        difference_periods[identity] = tuple(differences)
    return source_periods, difference_periods


class ReferenceModelBuilder:
    """Construct reference workbook and populate SemanticMap at build time."""

    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
        *,
        include_deferred_forecast: bool = False,
    ):
        self.fin = financials
        self.periods = canonical_fiscal_periods(financials)
        self.include_deferred_forecast = include_deferred_forecast
        self.assumptions = dict(assumptions or {})
        self.assumptions.setdefault("classificationOverrides", {})
        self.assumptions.setdefault("normalizationCandidates", [])
        self.rowmap: dict[str, Any] = {}
        self.build_modules = complete_build_modules(financials)
        self.expected_specs = prepare_complete_build(self)
        self.semantic_map = SemanticMap(expected_specs=self.expected_specs)
        self._deferred_spec_index = {c.id: c for c in DEFERRED_COMPONENT_SPECS}
        self._judgment_row_by_identity = {
            case.line_identity: 4 + case.order
            for case in self.judgment_cases
        }
        self._judgment_case_by_identity = {
            case.line_identity: case for case in self.judgment_cases
        }
        self._n = len(self.periods)
        self._last_fy_col = 2 + self._n - 1
        self._first_fc_col = 2 + self._n
        self._scenario_results: dict[str, Any] = {}
        self._base_result = None

        if self.include_deferred_forecast:
            # Internal/legacy path only — never enabled by normal v1 build.
            if "scenarios" not in self.assumptions or "marketData" not in self.assumptions:
                defaults = self._default_assumptions()
                for key, value in defaults.items():
                    self.assumptions.setdefault(key, value)
            shares = self.assumptions["marketData"]["dilutedShares"]
            self._scenario_results = {
                name: run_scenario(
                    self.assumptions["scenarios"][name],
                    self.anchor,
                    shares,
                )
                for name in ("Bear", "Base", "Bull")
            }
            self._base_result = self._scenario_results["Base"]

    def _prepare_historical(self, start_order: int):
        self.historical_specs = expand_historical_specs(self.periods)
        overrides = self.assumptions.get("classificationOverrides") or {}
        self.anchor = compute_anchor(
            self.fin,
            self.periods,
            classification_overrides=overrides,
        )
        self.interest_availability = assess_interest_availability(
            self.fin, self.periods
        )
        self.rowmap["interest_availability"] = availability_payload(
            self.interest_availability
        )

        self.historical_specs = filter_available_specs(
            self.historical_specs,
            historical_expected_series(self.anchor),
        )
        self.judgment_cases: tuple[JudgmentCase, ...] = classification_judgment_cases(
            self.fin,
            self.periods,
            self.anchor.reformulation,
        )
        return self.historical_specs

    def _prepare_normalization(self, start_order: int):
        self.normalization_cases: tuple[NormalizationCase, ...] = normalization_cases(
            self.fin,
            self.periods,
            self.assumptions,
        )
        self.normalization_specs = (
            expand_normalization_specs(
                self.periods,
                start_order=start_order,
            )
            if self.normalization_cases
            else ()
        )
        if self.normalization_specs:
            self.normalization_specs = filter_available_specs(
                self.normalization_specs,
                {"normalized_nopat": tuple(self.anchor.historical.nopat)},
            )
        self.normalization_series = (
            compute_normalization_series(
                self.fin,
                self.periods,
                self.anchor,
                self.normalization_cases,
            )
            if self.normalization_cases
            else None
        )
        return self.normalization_specs

    def _prepare_quality(self, start_order: int):
        self.quality_availability = earnings_quality_availability(self.fin)
        if self.quality_availability.operating_cash_flow:
            self.quality_series = compute_earnings_quality_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.quality_specs = expand_quality_specs(
                self.periods,
                start_order=start_order,
                include_asset_scaled=self.quality_availability.total_assets,
                include_sbc=(
                    self.quality_series.operating_cash_flow_less_sbc is not None
                ),
            )
        else:
            self.quality_series = None
            self.quality_specs = ()
        return self.quality_specs

    def _prepare_working_capital(self, start_order: int):
        if working_capital_applicable(self.anchor):
            self.working_capital_series = compute_working_capital_series(self.anchor)
            self.working_capital_specs = expand_working_capital_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.working_capital_series = None
            self.working_capital_specs = ()
        return self.working_capital_specs

    def _prepare_profitability_driver(self, start_order: int):
        self.profitability_driver_series = compute_profitability_driver_series(self.anchor)
        self.profitability_driver_specs = filter_available_specs(
            expand_profitability_driver_specs(
                self.periods,
                start_order=start_order,
            ),
            profitability_driver_expected_series(self.anchor),
        )
        return self.profitability_driver_specs

    def _prepare_profitability_change(self, start_order: int):
        self.profitability_change_series = compute_profitability_change_series(self.anchor)
        self.profitability_change_specs = filter_available_specs(
            expand_profitability_change_specs(
                self.periods,
                start_order=start_order,
            ),
            profitability_change_expected_series(self.anchor),
        )
        return self.profitability_change_specs

    def _prepare_roe_attribution(self, start_order: int):
        self.roe_attribution_series = compute_roe_attribution_series(self.anchor)
        self.roe_attribution_specs = filter_available_specs(
            expand_roe_attribution_specs(
                self.periods,
                start_order=start_order,
            ),
            roe_attribution_expected_series(self.anchor),
        )
        return self.roe_attribution_specs

    def _prepare_quality_change(self, start_order: int):
        if self.quality_series is not None:
            self.quality_change_series = compute_earnings_quality_change_series(
                self.quality_series
            )
            self.quality_change_specs = expand_quality_change_specs(
                self.periods,
                start_order=start_order,
                include_asset_scaled=self.quality_availability.total_assets,
            )
        else:
            self.quality_change_series = None
            self.quality_change_specs = ()
        return self.quality_change_specs

    def _prepare_per_share(self, start_order: int):
        if per_share_available(self.fin):
            self.per_share_series = compute_per_share_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.per_share_specs = filter_available_specs(
                expand_per_share_specs(
                    self.periods,
                    start_order=start_order,
                ),
                per_share_expected_series(self.per_share_series),
            )
        else:
            self.per_share_series = None
            self.per_share_specs = ()
        return self.per_share_specs

    def _prepare_per_share_attribution(self, start_order: int):
        if self.per_share_series is not None:
            self.per_share_attribution_series = compute_per_share_attribution_series(
                self.anchor,
                self.per_share_series,
            )
            self.per_share_attribution_specs = expand_per_share_attribution_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.per_share_attribution_series = None
            self.per_share_attribution_specs = ()
        return self.per_share_attribution_specs

    def _prepare_normalized_per_share(self, start_order: int):
        if self.per_share_series is not None and self.normalization_cases:
            self.normalized_per_share_specs = expand_normalized_per_share_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.normalized_per_share_specs = ()
        if (
            self.normalized_per_share_specs
            and self.normalization_series is not None
            and self.per_share_series is not None
        ):
            self.normalized_per_share_series = compute_normalized_per_share_series(
                self.normalization_series,
                self.per_share_series,
            )
        else:
            self.normalized_per_share_series = None
        return self.normalized_per_share_specs

    def _prepare_fixed_asset(self, start_order: int):
        if fixed_asset_applicable(self.fin):
            self.fixed_asset_series = compute_fixed_asset_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.fixed_asset_specs = expand_fixed_asset_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.fixed_asset_series = None
            self.fixed_asset_specs = ()
        return self.fixed_asset_specs

    def _prepare_lease_liability(self, start_order: int):
        if lease_liability_applicable(self.fin):
            self.lease_liability_series = compute_lease_liability_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_liability_specs = expand_lease_liability_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.lease_liability_series = None
            self.lease_liability_specs = ()
        return self.lease_liability_specs

    def _prepare_ownership_attribution(self, start_order: int):
        if ownership_attribution_applicable(self.fin):
            self.ownership_attribution_series = compute_ownership_attribution_series(
                self.fin,
                self.periods,
            )
            self.ownership_attribution_specs = expand_ownership_attribution_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.ownership_attribution_series = None
            self.ownership_attribution_specs = ()
        return self.ownership_attribution_specs

    def _prepare_goodwill_intangibles(self, start_order: int):
        self.goodwill_intangibles_availability = goodwill_intangibles_availability(
            self.fin
        )
        if goodwill_intangibles_applicable(self.fin):
            self.goodwill_intangibles_series = compute_goodwill_intangibles_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.goodwill_intangibles_specs = expand_goodwill_intangibles_specs(
                self.periods,
                start_order=start_order,
                availability=self.goodwill_intangibles_availability,
            )
        else:
            self.goodwill_intangibles_series = None
            self.goodwill_intangibles_specs = ()
        return self.goodwill_intangibles_specs

    def _prepare_lease_rou(self, start_order: int):
        if lease_rou_applicable(self.fin):
            self.lease_rou_series = compute_lease_rou_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_rou_specs = expand_lease_rou_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.lease_rou_series = None
            self.lease_rou_specs = ()
        return self.lease_rou_specs

    def _prepare_deferred_tax(self, start_order: int):
        if deferred_tax_applicable(self.fin):
            self.deferred_tax_series = compute_deferred_tax_series(
                self.fin,
                self.periods,
            )
            self.deferred_tax_specs = expand_deferred_tax_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.deferred_tax_series = None
            self.deferred_tax_specs = ()
        return self.deferred_tax_specs

    def _prepare_capex(self, start_order: int):
        if capex_applicable(self.fin):
            self.capex_series = compute_capex_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.capex_specs = expand_capex_specs(
                self.periods,
                start_order=start_order,
                include_operating_cash=(
                    self.capex_series.cash_after_ppe_capex is not None
                ),
            )
        else:
            self.capex_series = None
            self.capex_specs = ()
        return self.capex_specs

    def _prepare_lease_repayment(self, start_order: int):
        if lease_repayment_applicable(self.fin):
            self.lease_repayment_series = compute_lease_repayment_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_repayment_specs = expand_lease_repayment_specs(
                self.periods,
                start_order=start_order,
            )
        else:
            self.lease_repayment_series = None
            self.lease_repayment_specs = ()
        return self.lease_repayment_specs

    def _prepare_acquisition_cash(self, start_order: int):
        if acquisition_cash_applicable(self.fin):
            self.acquisition_cash_series = compute_acquisition_cash_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.acquisition_cash_specs = expand_acquisition_cash_specs(
                self.periods,
                start_order=start_order,
                include_cash_after_capex=(
                    self.acquisition_cash_series.cash_after_ppe_capex_and_acquisitions
                    is not None
                ),
            )
        else:
            self.acquisition_cash_series = None
            self.acquisition_cash_specs = ()
        return self.acquisition_cash_specs

    def _prepare_share_repurchase(self, start_order: int):
        if share_repurchase_applicable(self.fin):
            self.share_repurchase_series = compute_share_repurchase_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.share_repurchase_specs = expand_share_repurchase_specs(
                self.periods,
                start_order=start_order,
                include_residual=(
                    self.share_repurchase_series.cash_after_ppe_capex_acquisitions_and_repurchases
                    is not None
                ),
            )
        else:
            self.share_repurchase_series = None
            self.share_repurchase_specs = ()
        return self.share_repurchase_specs

    def _prepare_cash_rollforward(self, start_order: int):
        if cash_rollforward_applicable(self.fin):
            self.cash_rollforward_series = compute_cash_rollforward_series(
                self.fin,
                self.periods,
            )
            self.cash_rollforward_specs = expand_cash_rollforward_specs(
                self.periods,
                start_order=start_order,
                include_movement_difference=cash_movement_difference_applicable(
                    self.fin
                ),
                include_ending_from_flows=cash_ending_from_flows_applicable(self.fin),
                include_ending_difference=cash_ending_difference_applicable(self.fin),
            )
        else:
            self.cash_rollforward_series = None
            self.cash_rollforward_specs = ()
        return self.cash_rollforward_specs

    def _prepare_reported_margin(self, start_order: int):
        if reported_margin_applicable(self.fin):
            self.reported_margin_series = compute_reported_margin_series(
                self.fin,
                self.periods,
            )
            self.reported_margin_specs = expand_reported_margin_specs(
                self.periods,
                start_order=start_order,
                include_gross_margin=gross_margin_applicable(self.fin),
                include_operating_margin=reported_operating_margin_applicable(
                    self.fin
                ),
                include_burden=net_operating_expense_burden_applicable(self.fin),
                include_gross_margin_change=gross_margin_change_applicable(self.fin),
                include_burden_change=net_operating_expense_burden_change_applicable(
                    self.fin
                ),
                include_reconstructed=reconstructed_operating_margin_change_applicable(
                    self.fin
                ),
            )
        else:
            self.reported_margin_series = None
            self.reported_margin_specs = ()
        return self.reported_margin_specs

    def _prepare_inventory_analysis(self, start_order: int):
        if inventory_analysis_applicable(self.fin):
            self.inventory_analysis_series = compute_inventory_analysis_series(
                self.fin,
                self.periods,
            )
            self.inventory_analysis_specs = expand_inventory_analysis_specs(
                self.periods,
                start_order=start_order,
                include_intensity=inventory_intensity_applicable(self.fin),
                include_change=inventory_change_applicable(self.fin),
                include_revenue_scale=inventory_revenue_scale_effect_applicable(
                    self.fin
                ),
                include_intensity_effect=inventory_intensity_effect_applicable(
                    self.fin
                ),
                include_reconstructed=reconstructed_inventory_change_applicable(
                    self.fin
                ),
                include_balance_implied=inventory_balance_implied_cf_adjustment_applicable(
                    self.fin
                ),
                include_cf_difference=inventory_cf_adjustment_difference_applicable(
                    self.fin
                ),
            )
        else:
            self.inventory_analysis_series = None
            self.inventory_analysis_specs = ()
        return self.inventory_analysis_specs

    def _prepare_geographic(self, start_order: int):
        if geographic_segment_applicable(self.fin):
            self.geographic_series = compute_geographic_segment_series(
                self.fin,
                self.periods,
            )
            available_periods, growth_identities, bridge_identities = (
                _geographic_expand_inputs(self.geographic_series)
            )
            self.geographic_specs = expand_geographic_segment_specs(
                self.periods,
                start_order=start_order,
                available_periods=available_periods,
                growth_identities=growth_identities,
                bridge_identities=bridge_identities,
            )
        else:
            self.geographic_series = None
            self.geographic_specs = ()
        return self.geographic_specs

    def _prepare_operating_kpi(self, start_order: int):
        self.operating_kpi_series = None
        self.operating_kpi_relationship = None
        self.operating_kpi_compsales_relationship = None
        specs: list = []
        order = start_order
        revenue_registered = False

        if operating_kpi_applicable(self.fin):
            self.operating_kpi_series = compute_operating_kpi_series(
                self.fin,
                self.periods,
            )
            self.operating_kpi_relationship = (
                compute_operating_kpi_revenue_store_relationship(
                    self.fin,
                    self.periods,
                )
            )
            source_periods, change_periods, growth_periods = _store_count_expand_inputs(
                self.operating_kpi_series
            )
            revenue_source_periods, revenue_growth_periods, difference_periods = (
                _revenue_store_expand_inputs(self.operating_kpi_relationship)
            )
            units = {
                period: str(self.operating_kpi_series.unit[period])
                for period in source_periods
                if not is_source_unavailable(self.operating_kpi_series.unit[period])
            }
            source_specs = expand_store_count_source_specs(
                self.periods,
                start_order=order,
                source_periods=source_periods,
                units=units,
            )
            order += len(source_specs)
            revenue_source_specs = expand_revenue_store_source_specs(
                self.periods,
                start_order=order,
                source_periods=revenue_source_periods,
            )
            order += len(revenue_source_specs)
            practice_specs = expand_store_count_specs(
                self.periods,
                start_order=order,
                change_periods=change_periods,
                growth_periods=growth_periods,
            )
            order += len(practice_specs)
            relationship_specs = expand_revenue_store_specs(
                self.periods,
                start_order=order,
                growth_periods=revenue_growth_periods,
                difference_periods=difference_periods,
            )
            order += len(relationship_specs)
            specs.extend(
                source_specs
                + revenue_source_specs
                + practice_specs
                + relationship_specs
            )
            revenue_registered = True

        if operating_kpi_revenue_comparable_sales_relationship_applicable(self.fin):
            self.operating_kpi_compsales_relationship = (
                compute_operating_kpi_revenue_comparable_sales_relationship(
                    self.fin,
                    self.periods,
                )
            )
            compsales = self.operating_kpi_compsales_relationship
            source_by_identity, difference_by_identity = (
                _comparable_sales_expand_inputs(compsales)
            )
            if not revenue_registered:
                first = compsales.series[compsales.identities[0]]
                revenue_source_periods, revenue_growth_periods = (
                    _shared_revenue_expand_inputs(
                        compsales.periods,
                        first.revenue,
                        first.revenue_growth,
                    )
                )
                revenue_source_specs = expand_revenue_store_source_specs(
                    self.periods,
                    start_order=order,
                    source_periods=revenue_source_periods,
                )
                order += len(revenue_source_specs)
                growth_specs = expand_revenue_store_specs(
                    self.periods,
                    start_order=order,
                    growth_periods=revenue_growth_periods,
                    difference_periods=(),
                )
                order += len(growth_specs)
                specs.extend(revenue_source_specs + growth_specs)
            compsales_source_specs = expand_comparable_sales_source_specs(
                self.periods,
                start_order=order,
                identities=compsales.identities,
                source_periods_by_identity=source_by_identity,
            )
            order += len(compsales_source_specs)
            compsales_practice_specs = expand_comparable_sales_specs(
                self.periods,
                start_order=order,
                identities=compsales.identities,
                difference_periods_by_identity=difference_by_identity,
            )
            specs.extend(compsales_source_specs + compsales_practice_specs)

        self.operating_kpi_specs = tuple(specs)
        return self.operating_kpi_specs

    def _default_assumptions(self) -> dict[str, Any]:
        anchor_rev = 1000.0
        if self.fin.income_statement and self.periods:
            rev_item = resolve_line(
                self.fin.income_statement, "revenue", required=True
            ).item
            assert rev_item is not None
            anchor_rev = rev_item.values.get(self.periods[-1]) or 1000.0
        growth = [0.10] * 10
        margin = [0.15] * 10
        nowc = [0.05] * 10
        nola = [0.50] * 10
        return {
            "schemaVersion": 2,
            "ticker": self.fin.ticker,
            "company": self.fin.company_name,
            "marketData": {
                "price": 50.0,
                "priceDate": date.today().isoformat(),
                "dilutedShares": 1000.0,
                "riskFreeRate": 0.04,
                "equityRiskPremium": 0.05,
            },
            "scenarios": {
                name: {
                    "probability": prob,
                    "beta": beta,
                    "costOfEquity": 0.04 + beta * 0.05,
                    "taxRate": 0.165,
                    "terminalGrowth": 0.03,
                    "growthVector": growth,
                    "marginVector": margin,
                    "nowcRatioVector": nowc,
                    "nolaRatioVector": nola,
                }
                for name, prob, beta in (
                    ("Bear", 0.25, 1.3),
                    ("Base", 0.50, 1.15),
                    ("Bull", 0.25, 1.05),
                )
            },
            "classificationOverrides": {},
            "meta": {"anchorRevenue": anchor_rev, "currency": self.fin.units},
        }

    def build(self, output_path: Path) -> SemanticMap:
        wb = Workbook()
        write_complete_build(self, wb)
        if self.include_deferred_forecast:
            for scenario in ("Bear", "Base", "Bull"):
                self._build_model_tab(wb, scenario)
            self._build_scenario_summary(wb)
        else:
            for name in DEFERRED_TAB_NAMES:
                ws = wb.create_sheet(name)
                ws["A1"] = DEFERRED_PLACEHOLDER
                ws.sheet_state = "hidden"

        self._apply_source_unavailable_display(wb)
        errors = self.semantic_map.validate_complete()
        if errors:
            raise ValueError("Component map validation failed:\n" + "\n".join(errors))

        if not self.include_deferred_forecast:
            verify_complete_build(self.expected_specs, self.semantic_map)

        embed_component_map_sheet(wb, self.semantic_map)
        from ..trainer.check_context import build_check_context, embed_check_context_sheet

        context = build_check_context(
            self.fin,
            self.periods,
            self.assumptions,
            self.judgment_cases,
            self.normalization_cases,
        )
        embed_check_context_sheet(wb, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)

        sidecar = output_path.with_suffix(".component_map.json")
        self.semantic_map.save_json(sidecar)
        assumptions_path = output_path.with_suffix(".assumptions.json")
        assumptions_path.write_text(json.dumps(self.assumptions, indent=2) + "\n", encoding="utf-8")
        rowmap_path = output_path.parent / "rowmap.json"
        rowmap_path.write_text(
            json.dumps({**self.rowmap, **self.semantic_map.rowmap}, indent=2) + "\n",
            encoding="utf-8",
        )
        return self.semantic_map

    def _col(self, idx: int) -> str:
        return get_column_letter(idx)

    def _stamp_unavailable(self, ws, row: int, col: int, expected) -> None:
        if not is_source_unavailable(expected):
            return
        cell = ws.cell(row=row, column=col)
        cell.value = SOURCE_UNAVAILABLE
        cell.number_format = "General"

    def _apply_source_unavailable_display(self, wb: Workbook) -> None:
        """Replace gated outputs with a consistent source-unavailable status."""
        hist = self.anchor.historical
        dup = self.anchor.dupont
        condensed = wb["Condensed Financials"]
        dupont = wb["ALT DuPont"]
        for key, concept_avail in (
            (
                "condensed_interest_expense_row",
                self.interest_availability.interest_expense,
            ),
            (
                "condensed_interest_income_row",
                self.interest_availability.interest_income,
            ),
        ):
            row = self.rowmap.get(key)
            if row is None:
                continue
            for j, period in enumerate(self.periods):
                if not concept_avail.available_on(period):
                    self._stamp_unavailable(
                        condensed, row, 2 + j, SOURCE_UNAVAILABLE
                    )
        for j in range(self._n):
            col = 2 + j
            self._stamp_unavailable(
                condensed, self.rowmap["condensed_net_interest_row"], col, hist.net_interest[j]
            )
            self._stamp_unavailable(
                condensed, self.rowmap["condensed_niat_row"], col, hist.net_interest_after_tax[j]
            )
            self._stamp_unavailable(
                condensed, self.rowmap["condensed_nopat_row"], col, hist.nopat[j]
            )
            self._stamp_unavailable(
                dupont, self.rowmap["dupont_nopat_margin_row"], col, dup["NOPAT Margin"][j]
            )
            self._stamp_unavailable(dupont, self.rowmap["dupont_rnoa_row"], col, dup["RNOA"][j])
            self._stamp_unavailable(
                dupont, self.rowmap["dupont_after_tax_cod_row"], col, dup["After-tax CoD"][j]
            )
            self._stamp_unavailable(
                dupont, self.rowmap["dupont_spread_row"], col, dup["Spread"][j]
            )
            self._stamp_unavailable(
                dupont, self.rowmap["dupont_roe_decomp_row"], col, dup["ROE (decomposed)"][j]
            )
            drivers = self.profitability_driver_series
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_driver_rnoa_row"],
                col,
                drivers.rnoa_from_margin_turnover[j],
            )
            if is_source_unavailable(drivers.rnoa_from_margin_turnover[j]) or is_source_unavailable(
                dup["RNOA"][j]
            ):
                self._stamp_unavailable(
                    dupont,
                    self.rowmap["dupont_driver_check_row"],
                    col,
                    SOURCE_UNAVAILABLE,
                )
            changes = self.profitability_change_series
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_margin_change_row"],
                col,
                changes.nopat_margin_change[j],
            )
            self._stamp_unavailable(
                dupont, self.rowmap["dupont_direct_rnoa_change_row"], col, changes.rnoa_change[j]
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_margin_effect_row"],
                col,
                changes.margin_effect_on_rnoa[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_turnover_effect_row"],
                col,
                changes.turnover_effect_on_rnoa[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_rnoa_change_from_drivers_row"],
                col,
                changes.rnoa_change_from_drivers[j],
            )
            if is_source_unavailable(changes.rnoa_change_from_drivers[j]) or is_source_unavailable(
                changes.rnoa_change[j]
            ):
                self._stamp_unavailable(
                    dupont,
                    self.rowmap["dupont_rnoa_change_check_row"],
                    col,
                    SOURCE_UNAVAILABLE,
                )
            attribution = self.roe_attribution_series
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_financing_contribution_row"],
                col,
                attribution.financing_contribution_to_roe[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_direct_roe_change_row"],
                col,
                attribution.roe_change[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_operating_roe_effect_row"],
                col,
                attribution.operating_effect_on_roe_change[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_leverage_roe_effect_row"],
                col,
                attribution.leverage_effect_on_roe_change[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_spread_roe_effect_row"],
                col,
                attribution.spread_effect_on_roe_change[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_financing_roe_effect_row"],
                col,
                attribution.financing_effect_on_roe_change[j],
            )
            self._stamp_unavailable(
                dupont,
                self.rowmap["dupont_driver_roe_change_row"],
                col,
                attribution.roe_change_from_drivers[j],
            )
            if is_source_unavailable(attribution.financing_contribution_to_roe[j]) or is_source_unavailable(
                dup["ROE (decomposed)"][j]
            ):
                self._stamp_unavailable(
                    dupont,
                    self.rowmap["dupont_roe_level_attribution_check_row"],
                    col,
                    SOURCE_UNAVAILABLE,
                )
            if is_source_unavailable(attribution.roe_change_from_drivers[j]) or is_source_unavailable(
                attribution.roe_change[j]
            ):
                self._stamp_unavailable(
                    dupont,
                    self.rowmap["dupont_roe_change_attribution_check_row"],
                    col,
                    SOURCE_UNAVAILABLE,
                )
        if self.per_share_series is not None and "Per Share Analysis" in wb.sheetnames:
            ps = wb["Per Share Analysis"]
            for j in range(self._n):
                col = 2 + j
                self._stamp_unavailable(
                    ps,
                    self.rowmap["per_share_nopat_row"],
                    col,
                    hist.nopat[j],
                )
                self._stamp_unavailable(
                    ps,
                    self.rowmap["per_share_nopat_ps_row"],
                    col,
                    self.per_share_series.nopat_per_diluted_share[j],
                )
        if self.normalization_cases and "Earnings Normalization" in wb.sheetnames:
            from ..model.normalization import compute_normalization_series

            series = compute_normalization_series(
                self.fin,
                self.periods,
                self.anchor,
                self.normalization_cases,
            )
            ws = wb["Earnings Normalization"]
            for j in range(self._n):
                col = 3 + j
                self._stamp_unavailable(
                    ws, self.rowmap["earnings_norm_nopat_row"], col, series.normalized_nopat[j]
                )
                self._stamp_unavailable(
                    ws, self.rowmap["earnings_norm_reported_nopat_row"], col, hist.nopat[j]
                )
                if is_source_unavailable(series.normalized_nopat[j]) or is_source_unavailable(
                    hist.nopat[j]
                ):
                    self._stamp_unavailable(
                        ws,
                        self.rowmap["earnings_norm_check_row"],
                        col,
                        SOURCE_UNAVAILABLE,
                    )

    def _register_historical(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._historical_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_normalization(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._normalization_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_quality(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._quality_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_quality_change(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._quality_change_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_per_share(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._per_share_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_per_share_attribution(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._per_share_attribution_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_normalized_per_share(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._normalized_per_share_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_working_capital(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._working_capital_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_profitability_driver(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._profitability_driver_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_profitability_change(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._profitability_change_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_roe_attribution(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if is_source_unavailable(expected):
            return
        spec = self._roe_attribution_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_fixed_asset(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._fixed_asset_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_lease_liability(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._lease_liability_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_ownership_attribution(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._ownership_attribution_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_goodwill_intangibles(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._goodwill_intangibles_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_lease_rou(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._lease_rou_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_deferred_tax(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._deferred_tax_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_capex(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._capex_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_lease_repayment(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._lease_repayment_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_acquisition_cash(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._acquisition_cash_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_share_repurchase(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._share_repurchase_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_cash_rollforward(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._cash_rollforward_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_reported_margin(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._reported_margin_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_inventory_analysis(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._inventory_analysis_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_geographic(
        self,
        family_id: str,
        period_index: int,
        identity: str,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._geographic_spec_index[(family_id, period_index, identity)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_operating_kpi(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
        identity: str = "",
    ) -> None:
        spec = self._operating_kpi_spec_index[(family_id, period_index, identity)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_deferred(
        self,
        spec_id: str,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if spec_id not in self._deferred_spec_index:
            raise KeyError(f"Unknown deferred component spec: {spec_id}")
        spec = self._deferred_spec_index[spec_id]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _resolved_source_row(self, items: list[LineItem], concept: str, *, required: bool = False) -> int | None:
        """Workbook row for a canonical concept — same LineItem as compute_anchor()."""
        return workbook_row_for(
            resolve_line(items, concept, required=required),
            start_row=SOURCE_START_ROW,
        )

    def _header_block(self, ws, statement: str) -> None:
        ws["A1"] = f"Company: {self.fin.company_name} ({self.fin.ticker})"
        ws["A2"] = f"Statement: {statement}"
        ws["A3"] = f"Units: {self.fin.units}"
        ws["A4"] = f"Source: manual ingestion ({self.fin.jurisdiction})"
        ws["A6"] = "Line Item"
        ws["A6"].font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=6, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        ws.column_dimensions["A"].width = 48
        for j in range(self._n):
            ws.column_dimensions[self._col(2 + j)].width = 16

    def _fill_statement(self, ws, items: list[LineItem], start_row: int = 7) -> int:
        r = start_row
        sheet = ws.title
        for item in items:
            ws.cell(row=r, column=1, value=item.label)
            for j, pd in enumerate(self.periods):
                val = item.values.get(pd)
                c = ws.cell(row=r, column=2 + j, value=val)
                c.number_format = NUM_FMT
            self.rowmap[f"{sheet}!{line_identity(item).key()}"] = r
            r += 1
        return r

    def _build_source_tabs(self, wb: Workbook) -> None:
        ws = wb.active
        ws.title = "Income Statement"
        self._header_block(ws, "Income Statement")
        next_row = self._fill_statement(ws, self.fin.income_statement)
        if self.fin.historical_lease is not None:
            next_row += 1
            ws.cell(row=next_row, column=1, value="SUPPLEMENTAL DISCLOSURES").font = BOLD
            next_row += 1
            ws.cell(
                row=next_row,
                column=1,
                value="Lease interest expense (reported note)",
            )
            for j, pd in enumerate(self.periods):
                raw = self.fin.historical_lease.lease_interest_expense.get(pd)
                c = ws.cell(
                    row=next_row,
                    column=2 + j,
                    value=None if raw is None else float(raw),
                )
                c.number_format = NUM_FMT
            self.rowmap["supplemental_lease_interest_expense_row"] = next_row
        ws = wb.create_sheet("Balance Sheet")
        self._header_block(ws, "Balance Sheet")
        self._fill_statement(ws, self.fin.balance_sheet)
        ws = wb.create_sheet("Cash Flow Statement")
        self._header_block(ws, "Cash Flow Statement")
        self._fill_statement(ws, self.fin.cash_flow)

    def _build_condensed(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Condensed Financials")
        ws["A1"] = f"{self.fin.company_name} ({self.fin.ticker}) — Condensed Financials"
        ws.column_dimensions["A"].width = 42
        ws.column_dimensions["B"].width = 32

        r = 4
        ws.cell(row=r, column=1, value="BALANCE SHEET CLASSIFICATION").font = BOLD
        r += 1
        ws.cell(row=r, column=1, value="Line Item").font = BOLD
        ws.cell(row=r, column=2, value="Classification").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=3 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
            ws.column_dimensions[self._col(3 + j)].width = 14
        r += 1

        notes_col = 3 + self._n
        ws.cell(row=r - 1, column=notes_col, value="Notes").font = BOLD
        ws.column_dimensions[self._col(notes_col)].width = 42

        class_start = r
        classification_row_by_identity: dict[str, int] = {}
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(BALANCE_SHEET_CATEGORIES)}"',
            allow_blank=False,
        )
        ws.add_data_validation(dv)
        # Shared decisions drive defaults; SUMIF stays on-sheet for live reclassification.
        reform = self.anchor.reformulation
        for idx in reform.detail_indices:
            item = self.fin.balance_sheet[idx]
            decision = reform.decisions[idx]
            identity = line_identity(item).key()
            ws.cell(row=r, column=1, value=item.label)
            judgment_case = self._judgment_case_by_identity.get(identity)
            if judgment_case is not None:
                # Non-practice formula: learner edits Accounting Judgment!F only.
                from ..trainer.check_context import live_classification_formula

                formula = live_classification_formula(
                    4 + judgment_case.order,
                    judgment_case.supplied_treatment,
                )
                ws.cell(row=r, column=2, value=formula)
            else:
                cat_cell = ws.cell(row=r, column=2, value=decision.category)
                dv.add(cat_cell)
            classification_row_by_identity[identity] = r
            for j, pd in enumerate(self.periods):
                c = ws.cell(row=r, column=3 + j, value=item.values.get(pd))
                c.number_format = NUM_FMT
            note_parts: list[str] = []
            if decision.ambiguous:
                note_parts.append(f"⚠ Review: {decision.reason or 'judgment required'}")
            if decision.overridden:
                note_parts.append(f"Override → {decision.category}")
            if note_parts:
                ws.cell(row=r, column=notes_col, value="; ".join(note_parts))
            r += 1
        class_end = r - 1
        self.rowmap["condensed_class_start"] = class_start
        self.rowmap["condensed_class_end"] = class_end
        self.rowmap["condensed_class_value_col0"] = 3

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED INCOME STATEMENT").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        r += 1

        ni_src = self._resolved_source_row(self.fin.income_statement, "net_income", required=True)
        rev_src = self._resolved_source_row(self.fin.income_statement, "revenue", required=True)
        pretax_src = self._resolved_source_row(
            self.fin.income_statement, "pretax_income", required=True
        )
        tax_src = self._resolved_source_row(
            self.fin.income_statement, "tax_expense", required=True
        )
        int_exp_src = self._resolved_source_row(
            self.fin.income_statement, "interest_expense", required=False
        )
        int_inc_src = self._resolved_source_row(
            self.fin.income_statement, "interest_income", required=False
        )
        equity_src = self._resolved_source_row(self.fin.balance_sheet, "total_equity")
        row_nums: dict[str, int] = {}
        hist = self.anchor.historical
        for label, src_row, bold, family_id, expected_series in [
            ("Revenue", rev_src, False, "revenue_link", hist.revenue),
            ("Net Income", ni_src, False, "net_income_link", hist.net_income),
            ("Pretax Income", pretax_src, False, None, None),
            ("Tax Expense", tax_src, False, None, None),
            ("Interest Expense", int_exp_src, False, None, None),
            ("Interest Income", int_inc_src, False, None, None),
        ]:
            if src_row is None:
                continue
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            concept_avail = {
                "Interest Expense": self.interest_availability.interest_expense,
                "Interest Income": self.interest_availability.interest_income,
            }.get(label)
            for j in range(self._n):
                col = self._col(2 + j)
                if concept_avail is not None and not concept_avail.available_on(
                    self.periods[j]
                ):
                    ws.cell(row=r, column=2 + j, value=SOURCE_UNAVAILABLE)
                    continue
                formula = f"='Income Statement'!{col}{src_row}"
                ws.cell(row=r, column=2 + j, value=formula)
                if family_id is not None and expected_series is not None:
                    self._register_historical(
                        family_id,
                        j,
                        "Condensed Financials",
                        r,
                        2 + j,
                        formula,
                        expected_series[j],
                    )
            row_nums[label] = r
            if label == "Net Income":
                self.rowmap["condensed_ni_row"] = r
            if label == "Revenue":
                self.rowmap["condensed_revenue_row"] = r
            if label == "Interest Expense":
                self.rowmap["condensed_interest_expense_row"] = r
            if label == "Interest Income":
                self.rowmap["condensed_interest_income_row"] = r
            r += 1

        lease_interest_src = self.rowmap.get("supplemental_lease_interest_expense_row")
        if lease_interest_src is not None:
            ws.cell(row=r, column=1, value="Lease Interest Expense (disclosed)")
            for j in range(self._n):
                col = self._col(2 + j)
                formula = f"='Income Statement'!{col}{lease_interest_src}"
                ws.cell(row=r, column=2 + j, value=formula)
            row_nums["Lease Interest Expense (disclosed)"] = r
            r += 1

        etr_row = r
        ws.cell(row=r, column=1, value="Effective Tax Rate")
        pretax_r = row_nums["Pretax Income"]
        tax_r = row_nums["Tax Expense"]
        for j in range(self._n):
            col = self._col(2 + j)
            formula = f"=IF({col}{pretax_r}=0,NA(),-{col}{tax_r}/{col}{pretax_r})"
            ws.cell(row=r, column=2 + j, value=formula).number_format = PCT_FMT
            self._register_historical(
                "effective_tax_rate_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.effective_tax_rate[j],
            )
        row_nums["Effective Tax Rate"] = etr_row
        self.rowmap["condensed_etr_row"] = etr_row
        r += 1

        # Net interest uses Interest Expense / Interest Income; when disclosed lease
        # interest exists, subtract it only under uniform operating lease treatment.
        net_int_row = r
        ws.cell(row=r, column=1, value="Net Interest")
        lease_source = resolve_lease_liability_source(self.fin)
        lease_class_refs: list[str] = []
        if (
            lease_interest_src is not None
            and lease_source is not None
            and "Lease Interest Expense (disclosed)" in row_nums
        ):
            for item in lease_source.items:
                identity = line_identity(item).key()
                class_row = classification_row_by_identity.get(identity)
                if class_row is None:
                    raise KeyError(
                        f"Missing condensed classification row for lease source {identity!r}"
                    )
                lease_class_refs.append(f"$B${class_row}")
        for j in range(self._n):
            col = self._col(2 + j)
            if is_source_unavailable(hist.net_interest[j]) or not (
                "Interest Expense" in row_nums and "Interest Income" in row_nums
            ):
                ws.cell(row=r, column=2 + j, value=SOURCE_UNAVAILABLE)
                continue
            reported = (
                f"-({col}{row_nums['Interest Expense']}"
                f"+{col}{row_nums['Interest Income']})"
            )
            if not lease_class_refs:
                f = f"={reported}"
            else:
                lease_cell = f"{col}{row_nums['Lease Interest Expense (disclosed)']}"
                op_tests = ",".join(
                    f'{ref}="Operating Long-Term Liability"' for ref in lease_class_refs
                )
                fin_tests = ",".join(
                    f'{ref}="Financial Liability"' for ref in lease_class_refs
                )
                if len(lease_class_refs) == 1:
                    op_cond = op_tests
                    fin_cond = fin_tests
                else:
                    op_cond = f"AND({op_tests})"
                    fin_cond = f"AND({fin_tests})"
                f = (
                    f"={reported}"
                    f"-IF({op_cond},{lease_cell},"
                    f"IF({fin_cond},0,NA()))"
                )
            ws.cell(row=r, column=2 + j, value=f).number_format = NUM_FMT
            self._register_historical(
                "net_interest_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                f,
                hist.net_interest[j],
            )
        row_nums["Net Interest"] = net_int_row
        self.rowmap["condensed_net_interest_row"] = net_int_row
        r += 1

        niat_row = r
        ws.cell(row=r, column=1, value="Net Interest After Tax")
        for j in range(self._n):
            col = self._col(2 + j)
            if is_source_unavailable(hist.net_interest_after_tax[j]):
                ws.cell(row=r, column=2 + j, value=SOURCE_UNAVAILABLE)
                continue
            formula = (
                f"=IF({col}{net_int_row}=0,0,"
                f"IF(ISNA({col}{etr_row}),NA(),{col}{net_int_row}*(1-{col}{etr_row})))"
            )
            ws.cell(row=r, column=2 + j, value=formula).number_format = NUM_FMT
            self._register_historical(
                "net_interest_after_tax_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.net_interest_after_tax[j],
            )
        row_nums["Net Interest After Tax"] = niat_row
        self.rowmap["condensed_niat_row"] = niat_row
        r += 1

        nopat_row = r
        ws.cell(row=r, column=1, value="NOPAT").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if is_source_unavailable(hist.nopat[j]):
                ws.cell(row=r, column=2 + j, value=SOURCE_UNAVAILABLE)
                continue
            formula = f"={col}{row_nums['Net Income']}+{col}{niat_row}"
            c = ws.cell(row=r, column=2 + j, value=formula)
            c.fill = GREEN
            c.number_format = NUM_FMT
            self._register_historical(
                "nopat_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.nopat[j],
            )
        r += 1
        self.rowmap["condensed_nopat_row"] = nopat_row

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED BALANCE SHEET").font = BOLD
        r += 1

        def _class_sumif(category: str, value_col: str) -> str:
            return (
                f'SUMIF($B${class_start}:$B${class_end},"{category}",'
                f"{value_col}${class_start}:{value_col}${class_end})"
            )

        def _fill_sumif_row(label: str, category: str, *, bold: bool = False) -> int:
            nonlocal r
            row = r
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(self._n):
                vcol = self._col(3 + j)
                formula = f"={_class_sumif(category, vcol)}"
                c = ws.cell(row=r, column=2 + j, value=formula)
                c.number_format = NUM_FMT
            r += 1
            return row

        cat_totals = self.anchor.reformulation.category_totals
        reform = self.anchor.reformulation

        def _register_all_periods(
            family_id: str, row: int, expected_series: list[float]
        ) -> None:
            for j in range(self._n):
                self._register_historical(
                    family_id,
                    j,
                    "Condensed Financials",
                    row,
                    2 + j,
                    str(ws.cell(row=row, column=2 + j).value),
                    expected_series[j],
                )

        owca_row = _fill_sumif_row(
            "Operating Working Capital Assets", "Operating Working Capital Asset"
        )
        _register_all_periods(
            "owca_agg", owca_row, cat_totals["Operating Working Capital Asset"]
        )
        owcl_row = _fill_sumif_row(
            "Operating Working Capital Liabilities",
            "Operating Working Capital Liability",
        )
        _register_all_periods(
            "owcl_agg", owcl_row, cat_totals["Operating Working Capital Liability"]
        )

        nowc_row = r
        ws.cell(row=r, column=1, value="NOWC").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{owca_row}-{col}{owcl_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("nowc_agg", nowc_row, list(reform.nowc))

        olta_row = _fill_sumif_row(
            "Operating Long-Term Assets", "Operating Long-Term Asset"
        )
        _register_all_periods(
            "olta_agg", olta_row, cat_totals["Operating Long-Term Asset"]
        )
        oltl_row = _fill_sumif_row(
            "Operating Long-Term Liabilities", "Operating Long-Term Liability"
        )
        _register_all_periods(
            "oltl_agg", oltl_row, cat_totals["Operating Long-Term Liability"]
        )

        nola_row = r
        ws.cell(row=r, column=1, value="NOLA").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{olta_row}-{col}{oltl_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("nola_agg", nola_row, list(reform.nola))

        noa_row = r
        ws.cell(row=r, column=1, value="NOA").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{nowc_row}+{col}{nola_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("noa_agg", noa_row, list(reform.noa))

        fa_row = _fill_sumif_row("Financial Assets", "Financial Asset")
        _register_all_periods("financial_assets_agg", fa_row, cat_totals["Financial Asset"])
        fl_row = _fill_sumif_row("Financial Liabilities", "Financial Liability")
        _register_all_periods(
            "financial_liabilities_agg", fl_row, cat_totals["Financial Liability"]
        )

        nd_row = r
        ws.cell(row=r, column=1, value="Net Debt").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{fl_row}-{col}{fa_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("net_debt", nd_row, list(reform.net_debt))

        equity_row = r
        ws.cell(row=r, column=1, value="Equity (NOA - Net Debt)").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{noa_row}-{col}{nd_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods(
            "equity_reformulated_fy", equity_row, list(reform.implied_equity)
        )

        reported_eq_row = r
        ws.cell(row=r, column=1, value="Reported Equity").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if equity_src:
                f: str | None = f"='Balance Sheet'!{col}{equity_src}"
            else:
                f = None
            c = ws.cell(row=r, column=2 + j, value=f)
            c.number_format = NUM_FMT
        r += 1

        total_cap_row = r
        ws.cell(row=r, column=1, value="Total Capital").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{nd_row}+{col}{equity_row}")
            c.number_format = NUM_FMT
        r += 1

        check_row = r
        ws.cell(row=r, column=1, value="CHECK").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if equity_src:
                f = (
                    f'=IF(ABS({col}{equity_row}-{col}{reported_eq_row})<1,"OK","CHECK")'
                )
            else:
                f = '="UNVERIFIED"'
            ws.cell(row=r, column=2 + j, value=f)
        r += 1

        self.rowmap["condensed_owca_row"] = owca_row
        self.rowmap["condensed_owcl_row"] = owcl_row
        self.rowmap["condensed_nowc_row"] = nowc_row
        self.rowmap["condensed_nola_row"] = nola_row
        self.rowmap["condensed_noa_row"] = noa_row
        self.rowmap["condensed_nd_row"] = nd_row
        self.rowmap["condensed_equity_row"] = equity_row
        self.rowmap["condensed_reported_equity_row"] = reported_eq_row
        self.rowmap["condensed_total_capital_row"] = total_cap_row
        self.rowmap["condensed_check_row"] = check_row
        self.rowmap["condensed_nola_via_noa"] = True

    def _build_dupont(self, wb: Workbook) -> None:
        ws = wb.create_sheet("ALT DuPont")
        ws["A1"] = f"{self.fin.company_name} — DuPont Decomposition"
        ws["A2"] = "ROE = RNOA + FLEV × Spread"
        ws.column_dimensions["A"].width = 42
        r_hdr = 4
        ws.cell(row=r_hdr, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r_hdr, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        nopat_r = self.rowmap["condensed_nopat_row"]
        niat_r = self.rowmap["condensed_niat_row"]
        noa_r = self.rowmap["condensed_noa_row"]
        nd_r = self.rowmap["condensed_nd_row"]
        eq_r = self.rowmap["condensed_equity_row"]
        ni_r = self.rowmap["condensed_ni_row"]
        rev_r = self.rowmap["condensed_revenue_row"]

        metrics = [
            "Sales Growth",
            "NOPAT Margin",
            "RNOA",
            "After-tax CoD",
            "Spread",
            "FLEV",
            "ROE (decomposed)",
            "Actual ROE",
        ]
        metric_rows: dict[str, int] = {}
        r = r_hdr + 1
        for metric in metrics:
            ws.cell(row=r, column=1, value=metric)
            metric_rows[metric] = r
            r += 1

        sales_row = metric_rows["Sales Growth"]
        margin_row = metric_rows["NOPAT Margin"]
        rnoa_row = metric_rows["RNOA"]
        cod_row = metric_rows["After-tax CoD"]
        spread_row = metric_rows["Spread"]
        flev_row = metric_rows["FLEV"]
        roe_row = metric_rows["ROE (decomposed)"]
        actual_row = metric_rows["Actual ROE"]
        self.rowmap["dupont_sales_growth_row"] = sales_row
        self.rowmap["dupont_nopat_margin_row"] = margin_row
        self.rowmap["dupont_rnoa_row"] = rnoa_row
        self.rowmap["dupont_after_tax_cod_row"] = cod_row
        self.rowmap["dupont_spread_row"] = spread_row
        self.rowmap["dupont_flev_row"] = flev_row
        self.rowmap["dupont_roe_decomp_row"] = roe_row
        self.rowmap["dupont_actual_roe_row"] = actual_row

        dup = self.anchor.dupont
        na = "N/A"

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            src_col = self._col(2 + j)
            src_prev = self._col(2 + j - 1) if j > 0 else None

            # NOPAT Margin — all periods
            margin_f = (
                f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                f"'Condensed Financials'!{src_col}{nopat_r}/"
                f"'Condensed Financials'!{src_col}{rev_r})"
            )
            cell = ws.cell(row=margin_row, column=out_col_idx, value=margin_f)
            cell.number_format = PCT_FMT
            self._register_historical(
                "nopat_margin",
                j,
                "ALT DuPont",
                margin_row,
                out_col_idx,
                margin_f,
                dup["NOPAT Margin"][j],
            )

            if j == 0:
                for row in (
                    sales_row,
                    rnoa_row,
                    cod_row,
                    spread_row,
                    flev_row,
                    roe_row,
                    actual_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            assert src_prev is not None
            sales_f = (
                f"=IF('Condensed Financials'!{src_prev}{rev_r}=0,NA(),"
                f"'Condensed Financials'!{src_col}{rev_r}/"
                f"'Condensed Financials'!{src_prev}{rev_r}-1)"
            )
            ws.cell(row=sales_row, column=out_col_idx, value=sales_f).number_format = PCT_FMT
            self._register_historical(
                "sales_growth",
                j,
                "ALT DuPont",
                sales_row,
                out_col_idx,
                sales_f,
                dup["Sales Growth"][j],
            )

            rnoa_f = (
                f"=IF((('Condensed Financials'!{src_col}{noa_r}+"
                f"'Condensed Financials'!{src_prev}{noa_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{nopat_r}/"
                f"(('Condensed Financials'!{src_col}{noa_r}+"
                f"'Condensed Financials'!{src_prev}{noa_r})/2))"
            )
            ws.cell(row=rnoa_row, column=out_col_idx, value=rnoa_f).number_format = PCT_FMT
            self._register_historical(
                "rnoa",
                j,
                "ALT DuPont",
                rnoa_row,
                out_col_idx,
                rnoa_f,
                dup["RNOA"][j],
            )

            cod_f = (
                f"=IF((('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{niat_r}/"
                f"(('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2))"
            )
            ws.cell(row=cod_row, column=out_col_idx, value=cod_f).number_format = PCT_FMT
            self._register_historical(
                "after_tax_cod",
                j,
                "ALT DuPont",
                cod_row,
                out_col_idx,
                cod_f,
                dup["After-tax CoD"][j],
            )

            spread_f = f"={out_col}{rnoa_row}-{out_col}{cod_row}"
            ws.cell(row=spread_row, column=out_col_idx, value=spread_f).number_format = PCT_FMT
            self._register_historical(
                "spread",
                j,
                "ALT DuPont",
                spread_row,
                out_col_idx,
                spread_f,
                dup["Spread"][j],
            )

            flev_f = (
                f"=IF((('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2)=0,NA(),"
                f"(('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2)/"
                f"(('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2))"
            )
            ws.cell(row=flev_row, column=out_col_idx, value=flev_f)
            self._register_historical(
                "flev",
                j,
                "ALT DuPont",
                flev_row,
                out_col_idx,
                flev_f,
                dup["FLEV"][j],
            )

            roe_f = f"={out_col}{rnoa_row}+{out_col}{flev_row}*({out_col}{spread_row})"
            ws.cell(row=roe_row, column=out_col_idx, value=roe_f).number_format = PCT_FMT
            self._register_historical(
                "roe_decomp",
                j,
                "ALT DuPont",
                roe_row,
                out_col_idx,
                roe_f,
                dup["ROE (decomposed)"][j],
            )

            actual_f = (
                f"=IF((('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{ni_r}/"
                f"(('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2))"
            )
            ws.cell(row=actual_row, column=out_col_idx, value=actual_f).number_format = PCT_FMT
            self._register_historical(
                "actual_roe",
                j,
                "ALT DuPont",
                actual_row,
                out_col_idx,
                actual_f,
                dup["Actual ROE"][j],
            )

        # RNOA margin / turnover driver decomposition (Step 9C.1)
        drivers = self.profitability_driver_series
        driver_section_row = actual_row + 2
        average_noa_row = driver_section_row + 1
        turnover_row = driver_section_row + 2
        intensity_row = driver_section_row + 3
        driver_rnoa_row = driver_section_row + 4
        driver_check_row = driver_section_row + 5

        ws.cell(
            row=driver_section_row, column=1, value="RNOA DRIVER DECOMPOSITION"
        ).font = BOLD
        ws.cell(row=average_noa_row, column=1, value="Average NOA")
        ws.cell(row=turnover_row, column=1, value="NOA Turnover")
        ws.cell(row=intensity_row, column=1, value="NOA Intensity")
        ws.cell(row=driver_rnoa_row, column=1, value="RNOA from Margin × Turnover")
        ws.cell(row=driver_check_row, column=1, value="RNOA DRIVER CHECK").font = BOLD

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            src_col = self._col(2 + j)
            if j == 0:
                for row in (
                    average_noa_row,
                    turnover_row,
                    intensity_row,
                    driver_rnoa_row,
                    driver_check_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            src_prev = self._col(2 + j - 1)
            average_f = (
                f"=('Condensed Financials'!{src_prev}{noa_r}+"
                f"'Condensed Financials'!{src_col}{noa_r})/2"
            )
            turnover_f = (
                f"=IF({out_col}{average_noa_row}=0,NA(),"
                f"'Condensed Financials'!{src_col}{rev_r}/{out_col}{average_noa_row})"
            )
            intensity_f = (
                f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                f"{out_col}{average_noa_row}/'Condensed Financials'!{src_col}{rev_r})"
            )
            driver_rnoa_f = f"={out_col}{margin_row}*{out_col}{turnover_row}"
            driver_check = (
                f'=IF(ISNA({out_col}{driver_rnoa_row}),"N/A",'
                f'IF(ISNA({out_col}{rnoa_row}),"CHECK",'
                f'IF(ABS({out_col}{driver_rnoa_row}-{out_col}{rnoa_row})<0.0000001,'
                f'"OK","CHECK")))'
            )

            c = ws.cell(row=average_noa_row, column=out_col_idx, value=average_f)
            c.number_format = NUM_FMT
            c = ws.cell(row=turnover_row, column=out_col_idx, value=turnover_f)
            c.number_format = "0.00x"
            c = ws.cell(row=intensity_row, column=out_col_idx, value=intensity_f)
            c.number_format = "0.00x"
            c = ws.cell(row=driver_rnoa_row, column=out_col_idx, value=driver_rnoa_f)
            c.number_format = PCT_FMT
            ws.cell(row=driver_check_row, column=out_col_idx, value=driver_check)

            assert drivers.average_noa[j] is not None
            self._register_profitability_driver(
                "average_noa",
                j,
                "ALT DuPont",
                average_noa_row,
                out_col_idx,
                average_f,
                float(drivers.average_noa[j]),
            )
            turnover_expected = drivers.noa_turnover[j]
            assert turnover_expected is not None
            self._register_profitability_driver(
                "noa_turnover",
                j,
                "ALT DuPont",
                turnover_row,
                out_col_idx,
                turnover_f,
                turnover_expected
                if isinstance(turnover_expected, str)
                else float(turnover_expected),
            )
            intensity_expected = drivers.noa_intensity[j]
            assert intensity_expected is not None
            self._register_profitability_driver(
                "noa_intensity",
                j,
                "ALT DuPont",
                intensity_row,
                out_col_idx,
                intensity_f,
                intensity_expected
                if isinstance(intensity_expected, str)
                else float(intensity_expected),
            )
            driver_expected = drivers.rnoa_from_margin_turnover[j]
            assert driver_expected is not None
            self._register_profitability_driver(
                "rnoa_margin_turnover",
                j,
                "ALT DuPont",
                driver_rnoa_row,
                out_col_idx,
                driver_rnoa_f,
                driver_expected
                if isinstance(driver_expected, str)
                else float(driver_expected),
            )

        self.rowmap["dupont_average_noa_row"] = average_noa_row
        self.rowmap["dupont_noa_turnover_row"] = turnover_row
        self.rowmap["dupont_noa_intensity_row"] = intensity_row
        self.rowmap["dupont_driver_rnoa_row"] = driver_rnoa_row
        self.rowmap["dupont_driver_check_row"] = driver_check_row

        # RNOA change attribution: Margin vs Turnover (Step 9C.2)
        changes = self.profitability_change_series
        change_section_row = driver_check_row + 2
        margin_change_row = change_section_row + 1
        turnover_change_row = change_section_row + 2
        direct_rnoa_change_row = change_section_row + 3
        margin_effect_row = change_section_row + 4
        turnover_effect_row = change_section_row + 5
        driver_change_row = change_section_row + 6
        change_check_row = change_section_row + 7

        ws.cell(
            row=change_section_row, column=1, value="RNOA CHANGE ATTRIBUTION"
        ).font = BOLD
        ws.cell(row=margin_change_row, column=1, value="Change in NOPAT Margin")
        ws.cell(row=turnover_change_row, column=1, value="Change in NOA Turnover")
        ws.cell(row=direct_rnoa_change_row, column=1, value="Direct Change in RNOA")
        ws.cell(row=margin_effect_row, column=1, value="Margin Effect on RNOA Change")
        ws.cell(
            row=turnover_effect_row, column=1, value="Turnover Effect on RNOA Change"
        )
        ws.cell(row=driver_change_row, column=1, value="RNOA Change from Drivers")
        ws.cell(
            row=change_check_row, column=1, value="RNOA CHANGE DRIVER CHECK"
        ).font = BOLD

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            if j < 2:
                for row in (
                    margin_change_row,
                    turnover_change_row,
                    direct_rnoa_change_row,
                    margin_effect_row,
                    turnover_effect_row,
                    driver_change_row,
                    change_check_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            prev_col = self._col(2 + j - 1)
            margin_change_f = f"={out_col}{margin_row}-{prev_col}{margin_row}"
            turnover_change_f = f"={out_col}{turnover_row}-{prev_col}{turnover_row}"
            direct_rnoa_change_f = f"={out_col}{rnoa_row}-{prev_col}{rnoa_row}"
            margin_effect_f = (
                f"={out_col}{margin_change_row}*"
                f"(({out_col}{turnover_row}+{prev_col}{turnover_row})/2)"
            )
            turnover_effect_f = (
                f"={out_col}{turnover_change_row}*"
                f"(({out_col}{margin_row}+{prev_col}{margin_row})/2)"
            )
            driver_change_f = (
                f"={out_col}{margin_effect_row}+{out_col}{turnover_effect_row}"
            )
            change_check_f = (
                f'=IF(OR(ISNA({out_col}{driver_change_row}),'
                f'ISNA({out_col}{direct_rnoa_change_row})),"N/A",'
                f'IF(ABS({out_col}{driver_change_row}-{out_col}{direct_rnoa_change_row})'
                f'<0.0000001,"OK","CHECK"))'
            )

            c = ws.cell(row=margin_change_row, column=out_col_idx, value=margin_change_f)
            c.number_format = PCT_FMT
            c = ws.cell(
                row=turnover_change_row, column=out_col_idx, value=turnover_change_f
            )
            c.number_format = "0.00x"
            c = ws.cell(
                row=direct_rnoa_change_row, column=out_col_idx, value=direct_rnoa_change_f
            )
            c.number_format = PCT_FMT
            c = ws.cell(row=margin_effect_row, column=out_col_idx, value=margin_effect_f)
            c.number_format = PCT_FMT
            c = ws.cell(
                row=turnover_effect_row, column=out_col_idx, value=turnover_effect_f
            )
            c.number_format = PCT_FMT
            c = ws.cell(row=driver_change_row, column=out_col_idx, value=driver_change_f)
            c.number_format = PCT_FMT
            ws.cell(row=change_check_row, column=out_col_idx, value=change_check_f)

            margin_change_expected = changes.nopat_margin_change[j]
            assert margin_change_expected is not None
            self._register_profitability_change(
                "nopat_margin_change",
                j,
                "ALT DuPont",
                margin_change_row,
                out_col_idx,
                margin_change_f,
                margin_change_expected
                if isinstance(margin_change_expected, str)
                else float(margin_change_expected),
            )
            turnover_change_expected = changes.noa_turnover_change[j]
            assert turnover_change_expected is not None
            self._register_profitability_change(
                "noa_turnover_change",
                j,
                "ALT DuPont",
                turnover_change_row,
                out_col_idx,
                turnover_change_f,
                turnover_change_expected
                if isinstance(turnover_change_expected, str)
                else float(turnover_change_expected),
            )
            rnoa_change_expected = changes.rnoa_change[j]
            assert rnoa_change_expected is not None
            self._register_profitability_change(
                "rnoa_change",
                j,
                "ALT DuPont",
                direct_rnoa_change_row,
                out_col_idx,
                direct_rnoa_change_f,
                rnoa_change_expected
                if isinstance(rnoa_change_expected, str)
                else float(rnoa_change_expected),
            )
            margin_effect_expected = changes.margin_effect_on_rnoa[j]
            assert margin_effect_expected is not None
            self._register_profitability_change(
                "rnoa_margin_effect",
                j,
                "ALT DuPont",
                margin_effect_row,
                out_col_idx,
                margin_effect_f,
                margin_effect_expected
                if isinstance(margin_effect_expected, str)
                else float(margin_effect_expected),
            )
            turnover_effect_expected = changes.turnover_effect_on_rnoa[j]
            assert turnover_effect_expected is not None
            self._register_profitability_change(
                "rnoa_turnover_effect",
                j,
                "ALT DuPont",
                turnover_effect_row,
                out_col_idx,
                turnover_effect_f,
                turnover_effect_expected
                if isinstance(turnover_effect_expected, str)
                else float(turnover_effect_expected),
            )
            driver_change_expected = changes.rnoa_change_from_drivers[j]
            assert driver_change_expected is not None
            self._register_profitability_change(
                "rnoa_change_from_drivers",
                j,
                "ALT DuPont",
                driver_change_row,
                out_col_idx,
                driver_change_f,
                driver_change_expected
                if isinstance(driver_change_expected, str)
                else float(driver_change_expected),
            )

        self.rowmap["dupont_margin_change_row"] = margin_change_row
        self.rowmap["dupont_turnover_change_row"] = turnover_change_row
        self.rowmap["dupont_direct_rnoa_change_row"] = direct_rnoa_change_row
        self.rowmap["dupont_margin_effect_row"] = margin_effect_row
        self.rowmap["dupont_turnover_effect_row"] = turnover_effect_row
        self.rowmap["dupont_rnoa_change_from_drivers_row"] = driver_change_row
        self.rowmap["dupont_rnoa_change_check_row"] = change_check_row

        # ROE operating / financing attribution (Step 9D.1)
        attribution = self.roe_attribution_series
        roe_section_row = change_check_row + 2
        financing_contribution_row = roe_section_row + 1
        roe_level_check_row = roe_section_row + 2
        roe_change_section_row = roe_section_row + 4
        direct_roe_change_row = roe_change_section_row + 1
        operating_effect_row = roe_change_section_row + 2
        leverage_effect_row = roe_change_section_row + 3
        spread_effect_row = roe_change_section_row + 4
        financing_effect_row = roe_change_section_row + 5
        driver_roe_change_row = roe_change_section_row + 6
        roe_change_check_row = roe_change_section_row + 7

        ws.cell(
            row=roe_section_row,
            column=1,
            value="ROE OPERATING / FINANCING ATTRIBUTION",
        ).font = BOLD
        ws.cell(
            row=financing_contribution_row,
            column=1,
            value="Financing Contribution to ROE",
        )
        ws.cell(
            row=roe_level_check_row, column=1, value="ROE LEVEL ATTRIBUTION CHECK"
        ).font = BOLD
        ws.cell(
            row=roe_change_section_row, column=1, value="ROE CHANGE ATTRIBUTION"
        ).font = BOLD
        ws.cell(
            row=direct_roe_change_row, column=1, value="Direct Change in Decomposed ROE"
        )
        ws.cell(
            row=operating_effect_row, column=1, value="Operating Effect on Change in ROE"
        )
        ws.cell(
            row=leverage_effect_row, column=1, value="Leverage Effect on Change in ROE"
        )
        ws.cell(row=spread_effect_row, column=1, value="Spread Effect on Change in ROE")
        ws.cell(
            row=financing_effect_row, column=1, value="Financing Effect on Change in ROE"
        )
        ws.cell(row=driver_roe_change_row, column=1, value="Change in ROE from Drivers")
        ws.cell(
            row=roe_change_check_row, column=1, value="ROE CHANGE ATTRIBUTION CHECK"
        ).font = BOLD

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            change_rows = (
                direct_roe_change_row,
                operating_effect_row,
                leverage_effect_row,
                spread_effect_row,
                financing_effect_row,
                driver_roe_change_row,
                roe_change_check_row,
            )
            if j == 0:
                ws.cell(row=financing_contribution_row, column=out_col_idx, value=na)
                ws.cell(row=roe_level_check_row, column=out_col_idx, value=na)
                for row in change_rows:
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            financing_contribution_f = f"={out_col}{flev_row}*{out_col}{spread_row}"
            level_check = (
                f'=IF(OR(ISNA({out_col}{rnoa_row}),'
                f'ISNA({out_col}{financing_contribution_row}),'
                f'ISNA({out_col}{roe_row})),"N/A",'
                f'IF(ABS({out_col}{rnoa_row}+{out_col}{financing_contribution_row}'
                f'-{out_col}{roe_row})<0.0000001,"OK","CHECK"))'
            )
            c = ws.cell(
                row=financing_contribution_row,
                column=out_col_idx,
                value=financing_contribution_f,
            )
            c.number_format = PCT_FMT
            ws.cell(row=roe_level_check_row, column=out_col_idx, value=level_check)

            fin_expected = attribution.financing_contribution_to_roe[j]
            assert fin_expected is not None
            self._register_roe_attribution(
                "financing_contribution_to_roe",
                j,
                "ALT DuPont",
                financing_contribution_row,
                out_col_idx,
                financing_contribution_f,
                fin_expected if isinstance(fin_expected, str) else float(fin_expected),
            )

            if j < 2:
                for row in change_rows:
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            prev_col = self._col(2 + j - 1)
            direct_roe_change_f = f"={out_col}{roe_row}-{prev_col}{roe_row}"
            operating_effect_f = f"={out_col}{direct_rnoa_change_row}"
            leverage_effect_f = (
                f"=({out_col}{flev_row}-{prev_col}{flev_row})*"
                f"(({out_col}{spread_row}+{prev_col}{spread_row})/2)"
            )
            spread_effect_f = (
                f"=({out_col}{spread_row}-{prev_col}{spread_row})*"
                f"(({out_col}{flev_row}+{prev_col}{flev_row})/2)"
            )
            financing_effect_f = (
                f"={out_col}{leverage_effect_row}+{out_col}{spread_effect_row}"
            )
            driver_roe_change_f = (
                f"={out_col}{operating_effect_row}+{out_col}{financing_effect_row}"
            )
            roe_change_check_f = (
                f'=IF(OR(ISNA({out_col}{driver_roe_change_row}),'
                f'ISNA({out_col}{direct_roe_change_row})),"N/A",'
                f'IF(ABS({out_col}{driver_roe_change_row}-{out_col}{direct_roe_change_row})'
                f'<0.0000001,"OK","CHECK"))'
            )

            for row, formula in (
                (direct_roe_change_row, direct_roe_change_f),
                (operating_effect_row, operating_effect_f),
                (leverage_effect_row, leverage_effect_f),
                (spread_effect_row, spread_effect_f),
                (financing_effect_row, financing_effect_f),
                (driver_roe_change_row, driver_roe_change_f),
            ):
                c = ws.cell(row=row, column=out_col_idx, value=formula)
                c.number_format = PCT_FMT
            ws.cell(row=roe_change_check_row, column=out_col_idx, value=roe_change_check_f)

            registrations = (
                ("roe_change", direct_roe_change_row, direct_roe_change_f, attribution.roe_change[j]),
                (
                    "operating_effect_on_roe_change",
                    operating_effect_row,
                    operating_effect_f,
                    attribution.operating_effect_on_roe_change[j],
                ),
                (
                    "leverage_effect_on_roe_change",
                    leverage_effect_row,
                    leverage_effect_f,
                    attribution.leverage_effect_on_roe_change[j],
                ),
                (
                    "spread_effect_on_roe_change",
                    spread_effect_row,
                    spread_effect_f,
                    attribution.spread_effect_on_roe_change[j],
                ),
                (
                    "financing_effect_on_roe_change",
                    financing_effect_row,
                    financing_effect_f,
                    attribution.financing_effect_on_roe_change[j],
                ),
                (
                    "roe_change_from_drivers",
                    driver_roe_change_row,
                    driver_roe_change_f,
                    attribution.roe_change_from_drivers[j],
                ),
            )
            for family_id, row, formula, expected in registrations:
                assert expected is not None
                self._register_roe_attribution(
                    family_id,
                    j,
                    "ALT DuPont",
                    row,
                    out_col_idx,
                    formula,
                    expected if isinstance(expected, str) else float(expected),
                )

        self.rowmap["dupont_financing_contribution_row"] = financing_contribution_row
        self.rowmap["dupont_roe_level_attribution_check_row"] = roe_level_check_row
        self.rowmap["dupont_direct_roe_change_row"] = direct_roe_change_row
        self.rowmap["dupont_operating_roe_effect_row"] = operating_effect_row
        self.rowmap["dupont_leverage_roe_effect_row"] = leverage_effect_row
        self.rowmap["dupont_spread_roe_effect_row"] = spread_effect_row
        self.rowmap["dupont_financing_roe_effect_row"] = financing_effect_row
        self.rowmap["dupont_driver_roe_change_row"] = driver_roe_change_row
        self.rowmap["dupont_roe_change_attribution_check_row"] = roe_change_check_row

        next_section_after = roe_change_check_row
        if self.fixed_asset_series is not None:
            series = self.fixed_asset_series
            ppe_src = self._resolved_source_row(
                self.fin.balance_sheet, "property_plant_equipment", required=True
            )
            da_src = self._resolved_source_row(
                self.fin.cash_flow, "depreciation_amortization", required=True
            )
            assert ppe_src is not None and da_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            fa_section_row = next_section_after + 2
            ppe_row = fa_section_row + 1
            da_row = fa_section_row + 2
            avg_ppe_row = fa_section_row + 3
            turnover_row = fa_section_row + 4
            intensity_row = fa_section_row + 5
            change_row = fa_section_row + 6
            da_rev_row = fa_section_row + 7
            da_avg_row = fa_section_row + 8
            fa_check_row = fa_section_row + 9

            ws.cell(
                row=fa_section_row, column=1, value="FIXED-ASSET INTENSITY CONTEXT"
            ).font = BOLD
            ws.cell(row=ppe_row, column=1, value="Property, Plant & Equipment")
            ws.cell(row=da_row, column=1, value="Depreciation & Amortisation")
            ws.cell(row=avg_ppe_row, column=1, value="Average PP&E")
            ws.cell(row=turnover_row, column=1, value="PP&E Turnover")
            ws.cell(row=intensity_row, column=1, value="PP&E Intensity")
            ws.cell(row=change_row, column=1, value="Change in PP&E")
            ws.cell(row=da_rev_row, column=1, value="D&A / Revenue")
            ws.cell(row=da_avg_row, column=1, value="D&A / Average PP&E")
            ws.cell(
                row=fa_check_row, column=1, value="FIXED-ASSET INTENSITY CHECK"
            ).font = BOLD

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)

                ppe_f = f"='Balance Sheet'!{src_col}{ppe_src}"
                da_f = f"='Cash Flow Statement'!{src_col}{da_src}"
                da_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{da_row}/'Condensed Financials'!{src_col}{rev_r})"
                )

                c = ws.cell(row=ppe_row, column=out_col_idx, value=ppe_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=da_row, column=out_col_idx, value=da_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=da_rev_row, column=out_col_idx, value=da_rev_f)
                c.number_format = PCT_FMT

                self._register_fixed_asset(
                    "ppe_source_link",
                    j,
                    "ALT DuPont",
                    ppe_row,
                    out_col_idx,
                    ppe_f,
                    float(series.ppe[j]),
                )
                self._register_fixed_asset(
                    "da_source_link",
                    j,
                    "ALT DuPont",
                    da_row,
                    out_col_idx,
                    da_f,
                    float(series.depreciation_amortization[j]),
                )
                self._register_fixed_asset(
                    "da_to_revenue",
                    j,
                    "ALT DuPont",
                    da_rev_row,
                    out_col_idx,
                    da_rev_f,
                    series.da_to_revenue[j]
                    if isinstance(series.da_to_revenue[j], str)
                    else float(series.da_to_revenue[j]),
                )

                if j == 0:
                    for row in (
                        avg_ppe_row,
                        turnover_row,
                        intensity_row,
                        change_row,
                        da_avg_row,
                        fa_check_row,
                    ):
                        ws.cell(row=row, column=out_col_idx, value=na)
                    continue

                prev_col = self._col(2 + j - 1)
                avg_f = f"=({prev_col}{ppe_row}+{out_col}{ppe_row})/2"
                turnover_f = (
                    f"=IF({out_col}{avg_ppe_row}=0,NA(),"
                    f"'Condensed Financials'!{src_col}{rev_r}/{out_col}{avg_ppe_row})"
                )
                intensity_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{avg_ppe_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                change_f = f"={out_col}{ppe_row}-{prev_col}{ppe_row}"
                da_avg_f = (
                    f"=IF({out_col}{avg_ppe_row}=0,NA(),"
                    f"{out_col}{da_row}/{out_col}{avg_ppe_row})"
                )
                check_f = (
                    f'=IF(OR(ISNA({out_col}{turnover_row}),'
                    f'ISNA({out_col}{intensity_row})),"N/A",'
                    f'IF(ABS({out_col}{turnover_row}*{out_col}{intensity_row}-1)'
                    f'<0.0000001,"OK","CHECK"))'
                )

                c = ws.cell(row=avg_ppe_row, column=out_col_idx, value=avg_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=turnover_row, column=out_col_idx, value=turnover_f)
                c.number_format = "0.00x"
                c = ws.cell(row=intensity_row, column=out_col_idx, value=intensity_f)
                c.number_format = PCT_FMT
                c = ws.cell(row=change_row, column=out_col_idx, value=change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=da_avg_row, column=out_col_idx, value=da_avg_f)
                c.number_format = PCT_FMT
                ws.cell(row=fa_check_row, column=out_col_idx, value=check_f)

                registrations = (
                    ("average_ppe", avg_ppe_row, avg_f, series.average_ppe[j]),
                    ("ppe_turnover", turnover_row, turnover_f, series.ppe_turnover[j]),
                    ("ppe_intensity", intensity_row, intensity_f, series.ppe_intensity[j]),
                    ("ppe_change", change_row, change_f, series.ppe_change[j]),
                    (
                        "da_to_average_ppe",
                        da_avg_row,
                        da_avg_f,
                        series.da_to_average_ppe[j],
                    ),
                )
                for family_id, row, formula, expected in registrations:
                    assert expected is not None
                    self._register_fixed_asset(
                        family_id,
                        j,
                        "ALT DuPont",
                        row,
                        out_col_idx,
                        formula,
                        expected if isinstance(expected, str) else float(expected),
                    )

            self.rowmap["dupont_ppe_source_row"] = ppe_row
            self.rowmap["dupont_da_source_row"] = da_row
            self.rowmap["dupont_average_ppe_row"] = avg_ppe_row
            self.rowmap["dupont_ppe_turnover_row"] = turnover_row
            self.rowmap["dupont_ppe_intensity_row"] = intensity_row
            self.rowmap["dupont_ppe_change_row"] = change_row
            self.rowmap["dupont_da_to_revenue_row"] = da_rev_row
            self.rowmap["dupont_da_to_average_ppe_row"] = da_avg_row
            self.rowmap["dupont_fixed_asset_check_row"] = fa_check_row
            next_section_after = fa_check_row

        if self.lease_liability_series is not None:
            lease_series = self.lease_liability_series
            lease_source = resolve_lease_liability_source(self.fin)
            assert lease_source is not None
            source_rows = [SOURCE_START_ROW + idx for idx in lease_source.indices]
            rev_r = self.rowmap["condensed_revenue_row"]

            lease_section_row = next_section_after + 2
            lease_row = lease_section_row + 1
            lease_rev_row = lease_section_row + 2
            lease_change_row = lease_section_row + 3
            lease_growth_row = lease_section_row + 4

            ws.cell(
                row=lease_section_row, column=1, value="LEASE LIABILITY CONTEXT"
            ).font = BOLD
            ws.cell(row=lease_row, column=1, value="Lease Liability")
            ws.cell(row=lease_rev_row, column=1, value="Lease Liability / Revenue")
            ws.cell(row=lease_change_row, column=1, value="Change in Lease Liability")
            ws.cell(row=lease_growth_row, column=1, value="Lease Liability Growth")

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)

                if len(source_rows) == 1:
                    lease_f = f"='Balance Sheet'!{src_col}{source_rows[0]}"
                else:
                    refs = [f"'Balance Sheet'!{src_col}{row}" for row in source_rows]
                    lease_f = "=" + "+".join(refs)
                lease_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{lease_row}/'Condensed Financials'!{src_col}{rev_r})"
                )

                c = ws.cell(row=lease_row, column=out_col_idx, value=lease_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=lease_rev_row, column=out_col_idx, value=lease_rev_f)
                c.number_format = PCT_FMT

                self._register_lease_liability(
                    "lease_liability_source_link",
                    j,
                    "ALT DuPont",
                    lease_row,
                    out_col_idx,
                    lease_f,
                    float(lease_series.lease_liability[j]),
                )
                self._register_lease_liability(
                    "lease_liability_to_revenue",
                    j,
                    "ALT DuPont",
                    lease_rev_row,
                    out_col_idx,
                    lease_rev_f,
                    lease_series.lease_liability_to_revenue[j]
                    if isinstance(lease_series.lease_liability_to_revenue[j], str)
                    else float(lease_series.lease_liability_to_revenue[j]),
                )

                if j == 0:
                    ws.cell(row=lease_change_row, column=out_col_idx, value=na)
                    ws.cell(row=lease_growth_row, column=out_col_idx, value=na)
                    continue

                prev_col = self._col(2 + j - 1)
                change_f = f"={out_col}{lease_row}-{prev_col}{lease_row}"
                growth_f = (
                    f"=IF({prev_col}{lease_row}=0,NA(),"
                    f"{out_col}{lease_row}/{prev_col}{lease_row}-1)"
                )
                c = ws.cell(row=lease_change_row, column=out_col_idx, value=change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=lease_growth_row, column=out_col_idx, value=growth_f)
                c.number_format = PCT_FMT

                change_exp = lease_series.lease_liability_change[j]
                growth_exp = lease_series.lease_liability_growth[j]
                assert change_exp is not None and growth_exp is not None
                self._register_lease_liability(
                    "lease_liability_change",
                    j,
                    "ALT DuPont",
                    lease_change_row,
                    out_col_idx,
                    change_f,
                    float(change_exp),
                )
                self._register_lease_liability(
                    "lease_liability_growth",
                    j,
                    "ALT DuPont",
                    lease_growth_row,
                    out_col_idx,
                    growth_f,
                    growth_exp if isinstance(growth_exp, str) else float(growth_exp),
                )

            self.rowmap["dupont_lease_liability_row"] = lease_row
            self.rowmap["dupont_lease_liability_to_revenue_row"] = lease_rev_row
            self.rowmap["dupont_lease_liability_change_row"] = lease_change_row
            self.rowmap["dupont_lease_liability_growth_row"] = lease_growth_row
            next_section_after = lease_growth_row

        if self.lease_rou_series is not None:
            rou_series = self.lease_rou_series
            rou_item = resolve_lease_rou_source(self.fin)
            assert rou_item is not None
            rou_src = self._resolved_source_row(
                self.fin.balance_sheet, "right_of_use_assets", required=True
            )
            assert rou_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            rou_section_row = next_section_after + 2
            rou_level_row = rou_section_row + 1
            rou_change_row = rou_section_row + 2
            rou_growth_row = rou_section_row + 3
            rou_avg_row = rou_section_row + 4
            rou_intensity_row = rou_section_row + 5

            ws.cell(
                row=rou_section_row, column=1, value="LEASE ROU-ASSET CONTEXT"
            ).font = BOLD
            ws.cell(row=rou_level_row, column=1, value="Right-of-use Assets")
            ws.cell(row=rou_change_row, column=1, value="Change in Right-of-use Assets")
            ws.cell(row=rou_growth_row, column=1, value="Right-of-use Assets Growth")
            ws.cell(row=rou_avg_row, column=1, value="Average Right-of-use Assets")
            ws.cell(
                row=rou_intensity_row,
                column=1,
                value="Average Right-of-use Assets / Revenue",
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                level_f = f"='Balance Sheet'!{src_col}{rou_src}"
                c = ws.cell(row=rou_level_row, column=out_col_idx, value=level_f)
                c.number_format = NUM_FMT

                if j == 0:
                    continue

                prev_col = self._col(2 + j - 1)
                change_f = f"={out_col}{rou_level_row}-{prev_col}{rou_level_row}"
                growth_f = (
                    f"=IF({prev_col}{rou_level_row}=0,NA(),"
                    f"{out_col}{rou_level_row}/{prev_col}{rou_level_row}-1)"
                )
                avg_f = f"=({prev_col}{rou_level_row}+{out_col}{rou_level_row})/2"
                intensity_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{rou_avg_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=rou_change_row, column=out_col_idx, value=change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=rou_growth_row, column=out_col_idx, value=growth_f)
                c.number_format = PCT_FMT
                c = ws.cell(row=rou_avg_row, column=out_col_idx, value=avg_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=rou_intensity_row, column=out_col_idx, value=intensity_f)
                c.number_format = PCT_FMT

                change_exp = rou_series.rou_assets_change[j]
                growth_exp = rou_series.rou_assets_growth[j]
                avg_exp = rou_series.average_rou_assets[j]
                intensity_exp = rou_series.rou_assets_to_revenue[j]
                assert change_exp is not None and growth_exp is not None
                assert avg_exp is not None and intensity_exp is not None
                self._register_lease_rou(
                    "rou_assets_change",
                    j,
                    "ALT DuPont",
                    rou_change_row,
                    out_col_idx,
                    change_f,
                    float(change_exp),
                )
                self._register_lease_rou(
                    "rou_assets_growth",
                    j,
                    "ALT DuPont",
                    rou_growth_row,
                    out_col_idx,
                    growth_f,
                    growth_exp if isinstance(growth_exp, str) else float(growth_exp),
                )
                self._register_lease_rou(
                    "average_rou_assets",
                    j,
                    "ALT DuPont",
                    rou_avg_row,
                    out_col_idx,
                    avg_f,
                    float(avg_exp),
                )
                self._register_lease_rou(
                    "rou_assets_to_revenue",
                    j,
                    "ALT DuPont",
                    rou_intensity_row,
                    out_col_idx,
                    intensity_f,
                    intensity_exp
                    if isinstance(intensity_exp, str)
                    else float(intensity_exp),
                )

            self.rowmap["dupont_rou_assets_row"] = rou_level_row
            self.rowmap["dupont_rou_assets_change_row"] = rou_change_row
            self.rowmap["dupont_rou_assets_growth_row"] = rou_growth_row
            self.rowmap["dupont_average_rou_assets_row"] = rou_avg_row
            self.rowmap["dupont_rou_assets_to_revenue_row"] = rou_intensity_row
            next_section_after = rou_intensity_row

        if self.deferred_tax_series is not None:
            dt_series = self.deferred_tax_series
            dt_sources = resolve_deferred_tax_sources(self.fin)
            assert dt_sources is not None
            dta_src = self._resolved_source_row(
                self.fin.balance_sheet, "deferred_tax_assets", required=True
            )
            dtl_src = self._resolved_source_row(
                self.fin.balance_sheet, "deferred_tax_liabilities", required=True
            )
            assert dta_src is not None and dtl_src is not None

            dt_section_row = next_section_after + 2
            dta_level_row = dt_section_row + 1
            dtl_level_row = dt_section_row + 2
            net_row = dt_section_row + 3
            dta_change_row = dt_section_row + 4
            dtl_change_row = dt_section_row + 5
            net_change_row = dt_section_row + 6

            ws.cell(
                row=dt_section_row, column=1, value="DEFERRED-TAX BALANCE CONTEXT"
            ).font = BOLD
            ws.cell(row=dta_level_row, column=1, value="Deferred Tax Assets")
            ws.cell(row=dtl_level_row, column=1, value="Deferred Tax Liabilities")
            ws.cell(
                row=net_row,
                column=1,
                value="Net Deferred-Tax Asset Position (DTA − DTL)",
            )
            ws.cell(row=dta_change_row, column=1, value="Change in Deferred Tax Assets")
            ws.cell(
                row=dtl_change_row, column=1, value="Change in Deferred Tax Liabilities"
            )
            ws.cell(
                row=net_change_row,
                column=1,
                value="Change in Net Deferred-Tax Asset Position",
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                dta_f = f"='Balance Sheet'!{src_col}{dta_src}"
                dtl_f = f"='Balance Sheet'!{src_col}{dtl_src}"
                c = ws.cell(row=dta_level_row, column=out_col_idx, value=dta_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=dtl_level_row, column=out_col_idx, value=dtl_f)
                c.number_format = NUM_FMT

                net_f = f"={out_col}{dta_level_row}-{out_col}{dtl_level_row}"
                c = ws.cell(row=net_row, column=out_col_idx, value=net_f)
                c.number_format = NUM_FMT
                self._register_deferred_tax(
                    "net_deferred_tax_position",
                    j,
                    "ALT DuPont",
                    net_row,
                    out_col_idx,
                    net_f,
                    float(dt_series.net_deferred_tax_position[j]),
                )

                if j == 0:
                    continue

                prev_col = self._col(2 + j - 1)
                dta_change_f = f"={out_col}{dta_level_row}-{prev_col}{dta_level_row}"
                dtl_change_f = f"={out_col}{dtl_level_row}-{prev_col}{dtl_level_row}"
                net_change_f = f"={out_col}{net_row}-{prev_col}{net_row}"
                c = ws.cell(row=dta_change_row, column=out_col_idx, value=dta_change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=dtl_change_row, column=out_col_idx, value=dtl_change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=net_change_row, column=out_col_idx, value=net_change_f)
                c.number_format = NUM_FMT

                dta_change_exp = dt_series.deferred_tax_assets_change[j]
                dtl_change_exp = dt_series.deferred_tax_liabilities_change[j]
                net_change_exp = dt_series.net_deferred_tax_position_change[j]
                assert dta_change_exp is not None
                assert dtl_change_exp is not None
                assert net_change_exp is not None
                self._register_deferred_tax(
                    "deferred_tax_assets_change",
                    j,
                    "ALT DuPont",
                    dta_change_row,
                    out_col_idx,
                    dta_change_f,
                    float(dta_change_exp),
                )
                self._register_deferred_tax(
                    "deferred_tax_liabilities_change",
                    j,
                    "ALT DuPont",
                    dtl_change_row,
                    out_col_idx,
                    dtl_change_f,
                    float(dtl_change_exp),
                )
                self._register_deferred_tax(
                    "net_deferred_tax_position_change",
                    j,
                    "ALT DuPont",
                    net_change_row,
                    out_col_idx,
                    net_change_f,
                    float(net_change_exp),
                )

            self.rowmap["dupont_deferred_tax_assets_row"] = dta_level_row
            self.rowmap["dupont_deferred_tax_liabilities_row"] = dtl_level_row
            self.rowmap["dupont_net_deferred_tax_position_row"] = net_row
            self.rowmap["dupont_deferred_tax_assets_change_row"] = dta_change_row
            self.rowmap["dupont_deferred_tax_liabilities_change_row"] = dtl_change_row
            self.rowmap["dupont_net_deferred_tax_position_change_row"] = net_change_row
            next_section_after = net_change_row

        if self.capex_series is not None:
            capex_series = self.capex_series
            pay_item = resolve_capex_source(self.fin)
            assert pay_item is not None
            pay_src = self._resolved_source_row(
                self.fin.cash_flow, "payments_for_ppe", required=True
            )
            assert pay_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            capex_section_row = next_section_after + 2
            reported_row = capex_section_row + 1
            payments_row = capex_section_row + 2
            payments_rev_row = capex_section_row + 3

            ws.cell(row=capex_section_row, column=1, value="PP&E CAPEX CONTEXT").font = (
                BOLD
            )
            ws.cell(
                row=reported_row,
                column=1,
                value="Payments for Property, Plant & Equipment (reported)",
            )
            ws.cell(row=payments_row, column=1, value="PP&E Capex (−reported)")
            ws.cell(row=payments_rev_row, column=1, value="PP&E Capex / Revenue")

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                reported_f = f"='Cash Flow Statement'!{src_col}{pay_src}"
                payments_f = f"=-{out_col}{reported_row}"
                payments_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{payments_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=reported_row, column=out_col_idx, value=reported_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=payments_row, column=out_col_idx, value=payments_f)
                c.number_format = NUM_FMT
                c = ws.cell(
                    row=payments_rev_row, column=out_col_idx, value=payments_rev_f
                )
                c.number_format = PCT_FMT

                pay_exp = capex_series.ppe_capex[j]
                pay_rev_exp = capex_series.ppe_capex_to_revenue[j]
                self._register_capex(
                    "ppe_capex",
                    j,
                    "ALT DuPont",
                    payments_row,
                    out_col_idx,
                    payments_f,
                    float(pay_exp),
                )
                self._register_capex(
                    "ppe_capex_to_revenue",
                    j,
                    "ALT DuPont",
                    payments_rev_row,
                    out_col_idx,
                    payments_rev_f,
                    pay_rev_exp
                    if isinstance(pay_rev_exp, str)
                    else float(pay_rev_exp),
                )

            self.rowmap["dupont_ppe_capex_reported_row"] = reported_row
            self.rowmap["dupont_ppe_capex_row"] = payments_row
            self.rowmap["dupont_ppe_capex_to_revenue_row"] = payments_rev_row
            next_section_after = payments_rev_row

            if capex_series.cash_after_ppe_capex is not None:
                assert capex_series.cash_after_ppe_capex_to_revenue is not None
                cfo_item = resolve_operating_cash_source(self.fin)
                assert cfo_item is not None
                cfo_src = self._resolved_source_row(
                    self.fin.cash_flow, "operating_cash_flow", required=True
                )
                assert cfo_src is not None
                cash_section_row = next_section_after + 2
                cfo_row = cash_section_row + 1
                cash_after_row = cash_section_row + 2
                cash_after_rev_row = cash_section_row + 3

                ws.cell(
                    row=cash_section_row,
                    column=1,
                    value="OPERATING CASH AFTER PP&E CAPEX",
                ).font = BOLD
                ws.cell(
                    row=cfo_row,
                    column=1,
                    value="Operating Cash Flow (reported)",
                )
                ws.cell(
                    row=cash_after_row,
                    column=1,
                    value="Operating cash after PP&E capex",
                )
                ws.cell(
                    row=cash_after_rev_row,
                    column=1,
                    value="Operating cash after PP&E capex / Revenue",
                )

                for j in range(self._n):
                    out_col_idx = 2 + j
                    out_col = self._col(out_col_idx)
                    src_col = self._col(2 + j)
                    cfo_f = f"='Cash Flow Statement'!{src_col}{cfo_src}"
                    cash_after_f = f"={out_col}{cfo_row}-{out_col}{payments_row}"
                    cash_after_rev_f = (
                        f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                        f"{out_col}{cash_after_row}/"
                        f"'Condensed Financials'!{src_col}{rev_r})"
                    )
                    c = ws.cell(row=cfo_row, column=out_col_idx, value=cfo_f)
                    c.number_format = NUM_FMT
                    c = ws.cell(
                        row=cash_after_row, column=out_col_idx, value=cash_after_f
                    )
                    c.number_format = NUM_FMT
                    c = ws.cell(
                        row=cash_after_rev_row,
                        column=out_col_idx,
                        value=cash_after_rev_f,
                    )
                    c.number_format = PCT_FMT

                    cash_exp = capex_series.cash_after_ppe_capex[j]
                    cash_rev_exp = capex_series.cash_after_ppe_capex_to_revenue[j]
                    self._register_capex(
                        "cash_after_ppe_capex",
                        j,
                        "ALT DuPont",
                        cash_after_row,
                        out_col_idx,
                        cash_after_f,
                        float(cash_exp),
                    )
                    self._register_capex(
                        "cash_after_ppe_capex_to_revenue",
                        j,
                        "ALT DuPont",
                        cash_after_rev_row,
                        out_col_idx,
                        cash_after_rev_f,
                        cash_rev_exp
                        if isinstance(cash_rev_exp, str)
                        else float(cash_rev_exp),
                    )

                self.rowmap["dupont_operating_cash_flow_reported_row"] = cfo_row
                self.rowmap["dupont_cash_after_ppe_capex_row"] = cash_after_row
                self.rowmap[
                    "dupont_cash_after_ppe_capex_to_revenue_row"
                ] = cash_after_rev_row
                next_section_after = cash_after_rev_row

        if self.lease_repayment_series is not None:
            lease_repayment_series = self.lease_repayment_series
            repay_item = resolve_lease_repayment_source(self.fin)
            assert repay_item is not None
            repay_src = self._resolved_source_row(
                self.fin.cash_flow, "repayments_of_lease_liabilities", required=True
            )
            assert repay_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            lease_repay_section_row = next_section_after + 2
            reported_row = lease_repay_section_row + 1
            repayments_row = lease_repay_section_row + 2
            repayments_rev_row = lease_repay_section_row + 3

            ws.cell(
                row=lease_repay_section_row,
                column=1,
                value="LEASE REPAYMENT CONTEXT",
            ).font = BOLD
            ws.cell(
                row=reported_row,
                column=1,
                value="Repayments of Lease Liabilities (reported)",
            )
            ws.cell(
                row=repayments_row, column=1, value="Lease Repayments (−reported)"
            )
            ws.cell(
                row=repayments_rev_row, column=1, value="Lease Repayments / Revenue"
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                reported_f = f"='Cash Flow Statement'!{src_col}{repay_src}"
                repayments_f = f"=-{out_col}{reported_row}"
                repayments_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{repayments_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=reported_row, column=out_col_idx, value=reported_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=repayments_row, column=out_col_idx, value=repayments_f)
                c.number_format = NUM_FMT
                c = ws.cell(
                    row=repayments_rev_row, column=out_col_idx, value=repayments_rev_f
                )
                c.number_format = PCT_FMT

                repay_exp = lease_repayment_series.lease_repayments[j]
                repay_rev_exp = lease_repayment_series.lease_repayments_to_revenue[j]
                self._register_lease_repayment(
                    "lease_repayments",
                    j,
                    "ALT DuPont",
                    repayments_row,
                    out_col_idx,
                    repayments_f,
                    float(repay_exp),
                )
                self._register_lease_repayment(
                    "lease_repayments_to_revenue",
                    j,
                    "ALT DuPont",
                    repayments_rev_row,
                    out_col_idx,
                    repayments_rev_f,
                    repay_rev_exp
                    if isinstance(repay_rev_exp, str)
                    else float(repay_rev_exp),
                )

            self.rowmap["dupont_lease_repayments_reported_row"] = reported_row
            self.rowmap["dupont_lease_repayments_row"] = repayments_row
            self.rowmap["dupont_lease_repayments_to_revenue_row"] = repayments_rev_row
            next_section_after = repayments_rev_row

        if self.acquisition_cash_series is not None:
            acq_series = self.acquisition_cash_series
            acq_item = resolve_acquisition_cash_source(self.fin)
            assert acq_item is not None
            acq_src = self._resolved_source_row(
                self.fin.cash_flow, "acquisition_net_of_cash_acquired", required=True
            )
            assert acq_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            acq_section_row = next_section_after + 2
            reported_row = acq_section_row + 1
            outflow_row = acq_section_row + 2
            outflow_rev_row = acq_section_row + 3

            ws.cell(
                row=acq_section_row,
                column=1,
                value="ACQUISITION CASH CONTEXT",
            ).font = BOLD
            ws.cell(
                row=reported_row,
                column=1,
                value="Acquisition, net of cash acquired (reported)",
            )
            ws.cell(
                row=outflow_row,
                column=1,
                value="Acquisition cash outflow (−reported)",
            )
            ws.cell(
                row=outflow_rev_row,
                column=1,
                value="Acquisition cash / Revenue",
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                reported_f = f"='Cash Flow Statement'!{src_col}{acq_src}"
                outflow_f = f"=-{out_col}{reported_row}"
                outflow_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{outflow_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=reported_row, column=out_col_idx, value=reported_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=outflow_row, column=out_col_idx, value=outflow_f)
                c.number_format = NUM_FMT
                c = ws.cell(
                    row=outflow_rev_row, column=out_col_idx, value=outflow_rev_f
                )
                c.number_format = PCT_FMT

                outflow_exp = acq_series.acquisition_cash_outflow[j]
                outflow_rev_exp = acq_series.acquisition_cash_to_revenue[j]
                self._register_acquisition_cash(
                    "acquisition_cash_outflow",
                    j,
                    "ALT DuPont",
                    outflow_row,
                    out_col_idx,
                    outflow_f,
                    float(outflow_exp),
                )
                self._register_acquisition_cash(
                    "acquisition_cash_to_revenue",
                    j,
                    "ALT DuPont",
                    outflow_rev_row,
                    out_col_idx,
                    outflow_rev_f,
                    outflow_rev_exp
                    if isinstance(outflow_rev_exp, str)
                    else float(outflow_rev_exp),
                )

            self.rowmap["dupont_acquisition_cash_reported_row"] = reported_row
            self.rowmap["dupont_acquisition_cash_outflow_row"] = outflow_row
            self.rowmap["dupont_acquisition_cash_to_revenue_row"] = outflow_rev_row
            next_section_after = outflow_rev_row

            if acq_series.cash_after_ppe_capex_and_acquisitions is not None:
                cfo_row = self.rowmap.get("dupont_operating_cash_flow_reported_row")
                ppe_row = self.rowmap.get("dupont_ppe_capex_row")
                assert cfo_row is not None
                assert ppe_row is not None
                residual_section_row = next_section_after + 2
                residual_row = residual_section_row + 1

                ws.cell(
                    row=residual_section_row,
                    column=1,
                    value="CASH AFTER PP&E CAPEX AND ACQUISITIONS",
                ).font = BOLD
                ws.cell(
                    row=residual_row,
                    column=1,
                    value="Operating cash after PP&E capex and acquisitions",
                )

                for j in range(self._n):
                    out_col_idx = 2 + j
                    out_col = self._col(out_col_idx)
                    residual_f = (
                        f"={out_col}{cfo_row}-{out_col}{ppe_row}-{out_col}{outflow_row}"
                    )
                    c = ws.cell(
                        row=residual_row, column=out_col_idx, value=residual_f
                    )
                    c.number_format = NUM_FMT
                    residual_exp = (
                        acq_series.cash_after_ppe_capex_and_acquisitions[j]
                    )
                    self._register_acquisition_cash(
                        "cash_after_ppe_capex_and_acquisitions",
                        j,
                        "ALT DuPont",
                        residual_row,
                        out_col_idx,
                        residual_f,
                        float(residual_exp),
                    )

                self.rowmap[
                    "dupont_cash_after_ppe_capex_and_acquisitions_row"
                ] = residual_row
                next_section_after = residual_row

        if self.share_repurchase_series is not None:
            rp_series = self.share_repurchase_series
            rp_item = resolve_share_repurchase_source(self.fin)
            assert rp_item is not None
            rp_src = self._resolved_source_row(
                self.fin.cash_flow, "repurchase_of_common_stock", required=True
            )
            assert rp_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            rp_section_row = next_section_after + 2
            reported_row = rp_section_row + 1
            outflow_row = rp_section_row + 2
            outflow_rev_row = rp_section_row + 3

            ws.cell(
                row=rp_section_row,
                column=1,
                value="SHARE REPURCHASE CONTEXT",
            ).font = BOLD
            ws.cell(
                row=reported_row,
                column=1,
                value="Repurchase of common stock (reported)",
            )
            ws.cell(
                row=outflow_row,
                column=1,
                value="Share-repurchase outflow (−reported)",
            )
            ws.cell(
                row=outflow_rev_row,
                column=1,
                value="Share-repurchase / Revenue",
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                reported_f = f"='Cash Flow Statement'!{src_col}{rp_src}"
                outflow_f = f"=-{out_col}{reported_row}"
                outflow_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{outflow_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=reported_row, column=out_col_idx, value=reported_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=outflow_row, column=out_col_idx, value=outflow_f)
                c.number_format = NUM_FMT
                c = ws.cell(
                    row=outflow_rev_row, column=out_col_idx, value=outflow_rev_f
                )
                c.number_format = PCT_FMT

                outflow_exp = rp_series.share_repurchase_outflow[j]
                outflow_rev_exp = rp_series.share_repurchase_to_revenue[j]
                self._register_share_repurchase(
                    "share_repurchase_outflow",
                    j,
                    "ALT DuPont",
                    outflow_row,
                    out_col_idx,
                    outflow_f,
                    float(outflow_exp),
                )
                self._register_share_repurchase(
                    "share_repurchase_to_revenue",
                    j,
                    "ALT DuPont",
                    outflow_rev_row,
                    out_col_idx,
                    outflow_rev_f,
                    outflow_rev_exp
                    if isinstance(outflow_rev_exp, str)
                    else float(outflow_rev_exp),
                )

            self.rowmap["dupont_share_repurchase_reported_row"] = reported_row
            self.rowmap["dupont_share_repurchase_outflow_row"] = outflow_row
            self.rowmap["dupont_share_repurchase_to_revenue_row"] = outflow_rev_row
            next_section_after = outflow_rev_row

            if rp_series.cash_after_ppe_capex_acquisitions_and_repurchases is not None:
                cfo_row = self.rowmap.get("dupont_operating_cash_flow_reported_row")
                ppe_row = self.rowmap.get("dupont_ppe_capex_row")
                acq_outflow_row = self.rowmap.get("dupont_acquisition_cash_outflow_row")
                assert cfo_row is not None
                assert ppe_row is not None
                assert acq_outflow_row is not None
                residual_section_row = next_section_after + 2
                residual_row = residual_section_row + 1

                ws.cell(
                    row=residual_section_row,
                    column=1,
                    value="CASH AFTER PP&E CAPEX, ACQUISITIONS AND REPURCHASES",
                ).font = BOLD
                ws.cell(
                    row=residual_row,
                    column=1,
                    value="Operating cash after PP&E capex, acquisitions and repurchases",
                )

                for j in range(self._n):
                    out_col_idx = 2 + j
                    out_col = self._col(out_col_idx)
                    residual_f = (
                        f"={out_col}{cfo_row}-{out_col}{ppe_row}"
                        f"-{out_col}{acq_outflow_row}-{out_col}{outflow_row}"
                    )
                    c = ws.cell(
                        row=residual_row, column=out_col_idx, value=residual_f
                    )
                    c.number_format = NUM_FMT
                    residual_exp = (
                        rp_series.cash_after_ppe_capex_acquisitions_and_repurchases[j]
                    )
                    self._register_share_repurchase(
                        "cash_after_ppe_capex_acquisitions_and_repurchases",
                        j,
                        "ALT DuPont",
                        residual_row,
                        out_col_idx,
                        residual_f,
                        float(residual_exp),
                    )

                self.rowmap[
                    "dupont_cash_after_ppe_capex_acquisitions_and_repurchases_row"
                ] = residual_row
                next_section_after = residual_row

        if self.cash_rollforward_series is not None:
            cr_series = self.cash_rollforward_series
            cr_sources = resolve_cash_rollforward_sources(self.fin)
            assert cr_sources.operating is not None
            assert cr_sources.investing is not None
            assert cr_sources.financing is not None
            assert cr_sources.fx is not None
            operating_src = self._resolved_source_row(
                self.fin.cash_flow, OPERATING_CONCEPT, required=True
            )
            investing_src = self._resolved_source_row(
                self.fin.cash_flow, INVESTING_CONCEPT, required=True
            )
            financing_src = self._resolved_source_row(
                self.fin.cash_flow, FINANCING_CONCEPT, required=True
            )
            fx_src = self._resolved_source_row(
                self.fin.cash_flow, FX_CONCEPT, required=True
            )
            assert operating_src is not None
            assert investing_src is not None
            assert financing_src is not None
            assert fx_src is not None

            cr_section_row = next_section_after + 2
            operating_row = cr_section_row + 1
            investing_row = cr_section_row + 2
            financing_row = cr_section_row + 3
            fx_row = cr_section_row + 4
            movement_row = cr_section_row + 5
            cursor = movement_row

            ws.cell(
                row=cr_section_row,
                column=1,
                value="CASH ROLL-FORWARD CONTEXT",
            ).font = BOLD
            ws.cell(
                row=operating_row,
                column=1,
                value="Net cash from operating activities (reported)",
            )
            ws.cell(
                row=investing_row,
                column=1,
                value="Net cash from investing activities (reported)",
            )
            ws.cell(
                row=financing_row,
                column=1,
                value="Net cash from financing activities (reported)",
            )
            ws.cell(
                row=fx_row,
                column=1,
                value="Effect of FX on cash (reported)",
            )
            ws.cell(
                row=movement_row,
                column=1,
                value="Cash movement from flows",
            )

            change_row = None
            movement_diff_row = None
            beginning_row = None
            ending_from_flows_row = None
            ending_row = None
            ending_diff_row = None

            if cr_series.cash_movement_difference is not None:
                change_src = self._resolved_source_row(
                    self.fin.cash_flow, CHANGE_CONCEPT, required=True
                )
                assert change_src is not None
                assert cr_sources.change is not None
                change_row = cursor + 1
                movement_diff_row = cursor + 2
                cursor = movement_diff_row
                ws.cell(row=change_row, column=1, value="Reported cash change")
                ws.cell(
                    row=movement_diff_row,
                    column=1,
                    value="Cash movement difference",
                )

            if cr_series.cash_ending_from_flows is not None:
                beginning_src = self._resolved_source_row(
                    self.fin.cash_flow, BEGINNING_CONCEPT, required=True
                )
                assert beginning_src is not None
                assert cr_sources.beginning is not None
                beginning_row = cursor + 1
                ending_from_flows_row = cursor + 2
                cursor = ending_from_flows_row
                ws.cell(
                    row=beginning_row,
                    column=1,
                    value="Cash beginning (reported)",
                )
                ws.cell(
                    row=ending_from_flows_row,
                    column=1,
                    value="Cash ending from flows",
                )

            if cr_series.cash_ending_difference is not None:
                ending_src = self._resolved_source_row(
                    self.fin.cash_flow, ENDING_CONCEPT, required=True
                )
                assert ending_src is not None
                assert cr_sources.ending is not None
                assert ending_from_flows_row is not None
                ending_row = cursor + 1
                ending_diff_row = cursor + 2
                cursor = ending_diff_row
                ws.cell(row=ending_row, column=1, value="Cash ending (reported)")
                ws.cell(
                    row=ending_diff_row,
                    column=1,
                    value="Cash ending difference",
                )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                operating_f = f"='Cash Flow Statement'!{src_col}{operating_src}"
                investing_f = f"='Cash Flow Statement'!{src_col}{investing_src}"
                financing_f = f"='Cash Flow Statement'!{src_col}{financing_src}"
                fx_f = f"='Cash Flow Statement'!{src_col}{fx_src}"
                movement_f = (
                    f"={out_col}{operating_row}+{out_col}{investing_row}"
                    f"+{out_col}{financing_row}+{out_col}{fx_row}"
                )
                for row, formula in (
                    (operating_row, operating_f),
                    (investing_row, investing_f),
                    (financing_row, financing_f),
                    (fx_row, fx_f),
                    (movement_row, movement_f),
                ):
                    c = ws.cell(row=row, column=out_col_idx, value=formula)
                    c.number_format = NUM_FMT
                self._register_cash_rollforward(
                    "cash_movement_from_flows",
                    j,
                    "ALT DuPont",
                    movement_row,
                    out_col_idx,
                    movement_f,
                    float(cr_series.cash_movement_from_flows[j]),
                )
                if (
                    cr_series.cash_movement_difference is not None
                    and change_row is not None
                    and movement_diff_row is not None
                ):
                    change_src = self._resolved_source_row(
                        self.fin.cash_flow, CHANGE_CONCEPT, required=True
                    )
                    assert change_src is not None
                    change_f = f"='Cash Flow Statement'!{src_col}{change_src}"
                    diff_f = f"={out_col}{movement_row}-{out_col}{change_row}"
                    c = ws.cell(row=change_row, column=out_col_idx, value=change_f)
                    c.number_format = NUM_FMT
                    c = ws.cell(
                        row=movement_diff_row, column=out_col_idx, value=diff_f
                    )
                    c.number_format = NUM_FMT
                    self._register_cash_rollforward(
                        "cash_movement_difference",
                        j,
                        "ALT DuPont",
                        movement_diff_row,
                        out_col_idx,
                        diff_f,
                        float(cr_series.cash_movement_difference[j]),
                    )
                if (
                    cr_series.cash_ending_from_flows is not None
                    and beginning_row is not None
                    and ending_from_flows_row is not None
                ):
                    beginning_src = self._resolved_source_row(
                        self.fin.cash_flow, BEGINNING_CONCEPT, required=True
                    )
                    assert beginning_src is not None
                    beginning_f = f"='Cash Flow Statement'!{src_col}{beginning_src}"
                    ending_flows_f = (
                        f"={out_col}{beginning_row}+{out_col}{movement_row}"
                    )
                    c = ws.cell(
                        row=beginning_row, column=out_col_idx, value=beginning_f
                    )
                    c.number_format = NUM_FMT
                    c = ws.cell(
                        row=ending_from_flows_row,
                        column=out_col_idx,
                        value=ending_flows_f,
                    )
                    c.number_format = NUM_FMT
                    self._register_cash_rollforward(
                        "cash_ending_from_flows",
                        j,
                        "ALT DuPont",
                        ending_from_flows_row,
                        out_col_idx,
                        ending_flows_f,
                        float(cr_series.cash_ending_from_flows[j]),
                    )
                if (
                    cr_series.cash_ending_difference is not None
                    and ending_row is not None
                    and ending_diff_row is not None
                    and ending_from_flows_row is not None
                ):
                    ending_src = self._resolved_source_row(
                        self.fin.cash_flow, ENDING_CONCEPT, required=True
                    )
                    assert ending_src is not None
                    ending_f = f"='Cash Flow Statement'!{src_col}{ending_src}"
                    ending_diff_f = (
                        f"={out_col}{ending_from_flows_row}-{out_col}{ending_row}"
                    )
                    c = ws.cell(row=ending_row, column=out_col_idx, value=ending_f)
                    c.number_format = NUM_FMT
                    c = ws.cell(
                        row=ending_diff_row, column=out_col_idx, value=ending_diff_f
                    )
                    c.number_format = NUM_FMT
                    self._register_cash_rollforward(
                        "cash_ending_difference",
                        j,
                        "ALT DuPont",
                        ending_diff_row,
                        out_col_idx,
                        ending_diff_f,
                        float(cr_series.cash_ending_difference[j]),
                    )

            self.rowmap["dupont_cash_operating_reported_row"] = operating_row
            self.rowmap["dupont_cash_investing_reported_row"] = investing_row
            self.rowmap["dupont_cash_financing_reported_row"] = financing_row
            self.rowmap["dupont_cash_fx_reported_row"] = fx_row
            self.rowmap["dupont_cash_movement_from_flows_row"] = movement_row
            if change_row is not None:
                self.rowmap["dupont_cash_reported_change_row"] = change_row
            if movement_diff_row is not None:
                self.rowmap["dupont_cash_movement_difference_row"] = movement_diff_row
            if beginning_row is not None:
                self.rowmap["dupont_cash_beginning_reported_row"] = beginning_row
            if ending_from_flows_row is not None:
                self.rowmap["dupont_cash_ending_from_flows_row"] = ending_from_flows_row
            if ending_row is not None:
                self.rowmap["dupont_cash_ending_reported_row"] = ending_row
            if ending_diff_row is not None:
                self.rowmap["dupont_cash_ending_difference_row"] = ending_diff_row
            next_section_after = cursor

        if self.reported_margin_series is not None:
            rm_series = self.reported_margin_series
            rm_sources = resolve_reported_margin_sources(self.fin)
            assert rm_sources.revenue is not None
            revenue_src = self._resolved_source_row(
                self.fin.income_statement, REVENUE_CONCEPT, required=True
            )
            assert revenue_src is not None

            rm_section_row = next_section_after + 2
            revenue_row = rm_section_row + 1
            cursor = revenue_row
            ws.cell(
                row=rm_section_row,
                column=1,
                value="REPORTED MARGIN BRIDGE CONTEXT",
            ).font = BOLD
            ws.cell(row=revenue_row, column=1, value="Revenue (reported)")

            gross_row = None
            operating_row = None
            gross_margin_row = None
            operating_margin_row = None
            burden_row = None
            gross_margin_change_row = None
            burden_change_row = None
            reconstructed_row = None

            if rm_series.gross_profit is not None:
                gp_src = self._resolved_source_row(
                    self.fin.income_statement, GROSS_PROFIT_CONCEPT, required=True
                )
                assert gp_src is not None
                assert rm_sources.gross_profit is not None
                gross_row = cursor + 1
                cursor = gross_row
                ws.cell(row=gross_row, column=1, value="Gross profit (reported)")
            if rm_series.operating_profit is not None:
                op_src = self._resolved_source_row(
                    self.fin.income_statement, OPERATING_PROFIT_CONCEPT, required=True
                )
                assert op_src is not None
                assert rm_sources.operating_profit is not None
                operating_row = cursor + 1
                cursor = operating_row
                ws.cell(
                    row=operating_row,
                    column=1,
                    value="Operating profit (reported)",
                )
            if rm_series.gross_margin is not None:
                assert gross_row is not None
                gross_margin_row = cursor + 1
                cursor = gross_margin_row
                ws.cell(row=gross_margin_row, column=1, value="Gross margin")
            if rm_series.reported_operating_margin is not None:
                assert operating_row is not None
                operating_margin_row = cursor + 1
                cursor = operating_margin_row
                ws.cell(
                    row=operating_margin_row,
                    column=1,
                    value="Reported operating margin",
                )
            if rm_series.net_operating_expense_burden is not None:
                assert gross_row is not None and operating_row is not None
                burden_row = cursor + 1
                cursor = burden_row
                ws.cell(
                    row=burden_row,
                    column=1,
                    value="Net operating expense burden",
                )
            if rm_series.gross_margin_change is not None and self._n > 1:
                assert gross_margin_row is not None
                gross_margin_change_row = cursor + 1
                cursor = gross_margin_change_row
                ws.cell(
                    row=gross_margin_change_row,
                    column=1,
                    value="Change in gross margin",
                )
            if rm_series.net_operating_expense_burden_change is not None and self._n > 1:
                assert burden_row is not None
                burden_change_row = cursor + 1
                cursor = burden_change_row
                ws.cell(
                    row=burden_change_row,
                    column=1,
                    value="Change in net operating expense burden",
                )
            if rm_series.reconstructed_operating_margin_change is not None and self._n > 1:
                assert (
                    gross_margin_change_row is not None
                    and burden_change_row is not None
                )
                reconstructed_row = cursor + 1
                cursor = reconstructed_row
                ws.cell(
                    row=reconstructed_row,
                    column=1,
                    value="Reconstructed change in reported operating margin",
                )

            def _margin_expected(value: float | str | None) -> float | str:
                assert value is not None
                return value if isinstance(value, str) else float(value)

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                revenue_f = f"='Income Statement'!{src_col}{revenue_src}"
                c = ws.cell(row=revenue_row, column=out_col_idx, value=revenue_f)
                c.number_format = NUM_FMT
                if gross_row is not None:
                    gp_src = self._resolved_source_row(
                        self.fin.income_statement, GROSS_PROFIT_CONCEPT, required=True
                    )
                    assert gp_src is not None
                    gp_f = f"='Income Statement'!{src_col}{gp_src}"
                    c = ws.cell(row=gross_row, column=out_col_idx, value=gp_f)
                    c.number_format = NUM_FMT
                if operating_row is not None:
                    op_src = self._resolved_source_row(
                        self.fin.income_statement,
                        OPERATING_PROFIT_CONCEPT,
                        required=True,
                    )
                    assert op_src is not None
                    op_f = f"='Income Statement'!{src_col}{op_src}"
                    c = ws.cell(row=operating_row, column=out_col_idx, value=op_f)
                    c.number_format = NUM_FMT
                if gross_margin_row is not None and gross_row is not None:
                    gm_f = (
                        f"=IF({out_col}{revenue_row}=0,NA(),"
                        f"{out_col}{gross_row}/{out_col}{revenue_row})"
                    )
                    c = ws.cell(
                        row=gross_margin_row, column=out_col_idx, value=gm_f
                    )
                    c.number_format = PCT_FMT
                    assert rm_series.gross_margin is not None
                    self._register_reported_margin(
                        "gross_margin",
                        j,
                        "ALT DuPont",
                        gross_margin_row,
                        out_col_idx,
                        gm_f,
                        _margin_expected(rm_series.gross_margin[j]),
                    )
                if operating_margin_row is not None and operating_row is not None:
                    om_f = (
                        f"=IF({out_col}{revenue_row}=0,NA(),"
                        f"{out_col}{operating_row}/{out_col}{revenue_row})"
                    )
                    c = ws.cell(
                        row=operating_margin_row, column=out_col_idx, value=om_f
                    )
                    c.number_format = PCT_FMT
                    assert rm_series.reported_operating_margin is not None
                    self._register_reported_margin(
                        "reported_operating_margin",
                        j,
                        "ALT DuPont",
                        operating_margin_row,
                        out_col_idx,
                        om_f,
                        _margin_expected(rm_series.reported_operating_margin[j]),
                    )
                if (
                    burden_row is not None
                    and gross_row is not None
                    and operating_row is not None
                ):
                    burden_f = (
                        f"=IF({out_col}{revenue_row}=0,NA(),"
                        f"({out_col}{gross_row}-{out_col}{operating_row})/"
                        f"{out_col}{revenue_row})"
                    )
                    c = ws.cell(row=burden_row, column=out_col_idx, value=burden_f)
                    c.number_format = PCT_FMT
                    assert rm_series.net_operating_expense_burden is not None
                    self._register_reported_margin(
                        "net_operating_expense_burden",
                        j,
                        "ALT DuPont",
                        burden_row,
                        out_col_idx,
                        burden_f,
                        _margin_expected(rm_series.net_operating_expense_burden[j]),
                    )
                if j == 0:
                    continue
                prev_col = self._col(2 + j - 1)
                if (
                    gross_margin_change_row is not None
                    and gross_margin_row is not None
                ):
                    gm_change_f = (
                        f"={out_col}{gross_margin_row}-{prev_col}{gross_margin_row}"
                    )
                    c = ws.cell(
                        row=gross_margin_change_row,
                        column=out_col_idx,
                        value=gm_change_f,
                    )
                    c.number_format = PCT_FMT
                    assert rm_series.gross_margin_change is not None
                    self._register_reported_margin(
                        "gross_margin_change",
                        j,
                        "ALT DuPont",
                        gross_margin_change_row,
                        out_col_idx,
                        gm_change_f,
                        _margin_expected(rm_series.gross_margin_change[j]),
                    )
                if burden_change_row is not None and burden_row is not None:
                    burden_change_f = (
                        f"={out_col}{burden_row}-{prev_col}{burden_row}"
                    )
                    c = ws.cell(
                        row=burden_change_row,
                        column=out_col_idx,
                        value=burden_change_f,
                    )
                    c.number_format = PCT_FMT
                    assert rm_series.net_operating_expense_burden_change is not None
                    self._register_reported_margin(
                        "net_operating_expense_burden_change",
                        j,
                        "ALT DuPont",
                        burden_change_row,
                        out_col_idx,
                        burden_change_f,
                        _margin_expected(
                            rm_series.net_operating_expense_burden_change[j]
                        ),
                    )
                if (
                    reconstructed_row is not None
                    and gross_margin_change_row is not None
                    and burden_change_row is not None
                ):
                    reconstructed_f = (
                        f"={out_col}{gross_margin_change_row}-"
                        f"{out_col}{burden_change_row}"
                    )
                    c = ws.cell(
                        row=reconstructed_row,
                        column=out_col_idx,
                        value=reconstructed_f,
                    )
                    c.number_format = PCT_FMT
                    assert (
                        rm_series.reconstructed_operating_margin_change is not None
                    )
                    self._register_reported_margin(
                        "reconstructed_operating_margin_change",
                        j,
                        "ALT DuPont",
                        reconstructed_row,
                        out_col_idx,
                        reconstructed_f,
                        _margin_expected(
                            rm_series.reconstructed_operating_margin_change[j]
                        ),
                    )

            self.rowmap["dupont_reported_margin_revenue_row"] = revenue_row
            if gross_row is not None:
                self.rowmap["dupont_reported_margin_gross_profit_row"] = gross_row
            if operating_row is not None:
                self.rowmap["dupont_reported_margin_operating_profit_row"] = (
                    operating_row
                )
            if gross_margin_row is not None:
                self.rowmap["dupont_gross_margin_row"] = gross_margin_row
            if operating_margin_row is not None:
                self.rowmap["dupont_reported_operating_margin_row"] = (
                    operating_margin_row
                )
            if burden_row is not None:
                self.rowmap["dupont_net_operating_expense_burden_row"] = burden_row
            if gross_margin_change_row is not None:
                self.rowmap["dupont_gross_margin_change_row"] = (
                    gross_margin_change_row
                )
            if burden_change_row is not None:
                self.rowmap["dupont_net_operating_expense_burden_change_row"] = (
                    burden_change_row
                )
            if reconstructed_row is not None:
                self.rowmap["dupont_reconstructed_operating_margin_change_row"] = (
                    reconstructed_row
                )
            next_section_after = cursor

        if self.inventory_analysis_series is not None:
            inv_series = self.inventory_analysis_series
            inv_sources = resolve_inventory_analysis_sources(self.fin)
            assert inv_sources.inventories is not None
            inventory_src = self._resolved_source_row(
                self.fin.balance_sheet, INVENTORIES_CONCEPT, required=True
            )
            assert inventory_src is not None

            inv_section_row = next_section_after + 2
            inventory_row = inv_section_row + 1
            cursor = inventory_row
            ws.cell(
                row=inv_section_row,
                column=1,
                value="INVENTORY GROWTH AND INTENSITY CONTEXT",
            ).font = BOLD
            ws.cell(row=inventory_row, column=1, value="Inventory (reported)")

            revenue_row = None
            intensity_row = None
            change_row = None
            scale_row = None
            intensity_effect_row = None
            reconstructed_row = None

            if inv_series.revenue is not None:
                revenue_src = self._resolved_source_row(
                    self.fin.income_statement, REVENUE_CONCEPT, required=True
                )
                assert revenue_src is not None
                assert inv_sources.revenue is not None
                revenue_row = cursor + 1
                cursor = revenue_row
                ws.cell(row=revenue_row, column=1, value="Revenue (reported)")
            if inv_series.inventory_intensity is not None:
                assert revenue_row is not None
                intensity_row = cursor + 1
                cursor = intensity_row
                ws.cell(row=intensity_row, column=1, value="Inventory intensity")
            if inv_series.inventory_change is not None and self._n > 1:
                change_row = cursor + 1
                cursor = change_row
                ws.cell(row=change_row, column=1, value="Change in inventory")
            if (
                inv_series.inventory_revenue_scale_effect is not None
                and self._n > 1
            ):
                assert intensity_row is not None and revenue_row is not None
                scale_row = cursor + 1
                cursor = scale_row
                ws.cell(
                    row=scale_row,
                    column=1,
                    value="Revenue-scale effect on inventory",
                )
            if inv_series.inventory_intensity_effect is not None and self._n > 1:
                assert intensity_row is not None and revenue_row is not None
                intensity_effect_row = cursor + 1
                cursor = intensity_effect_row
                ws.cell(
                    row=intensity_effect_row,
                    column=1,
                    value="Intensity effect on inventory",
                )
            if (
                inv_series.reconstructed_inventory_change is not None
                and self._n > 1
            ):
                assert scale_row is not None and intensity_effect_row is not None
                reconstructed_row = cursor + 1
                cursor = reconstructed_row
                ws.cell(
                    row=reconstructed_row,
                    column=1,
                    value="Reconstructed change in inventory",
                )

            cf_row = None
            implied_row = None
            cf_diff_row = None
            cf_src = None
            if inv_series.change_in_inventories is not None:
                cf_src = self._resolved_source_row(
                    self.fin.cash_flow,
                    CHANGE_IN_INVENTORIES_CONCEPT,
                    required=True,
                )
                assert cf_src is not None
                assert inv_sources.change_in_inventories is not None
                cf_row = cursor + 1
                cursor = cf_row
                ws.cell(
                    row=cf_row,
                    column=1,
                    value="Inventory CF adjustment (reported)",
                )
            if (
                inv_series.inventory_balance_implied_cf_adjustment is not None
                and self._n > 1
            ):
                implied_row = cursor + 1
                cursor = implied_row
                ws.cell(
                    row=implied_row,
                    column=1,
                    value="Balance-implied inventory CF adjustment",
                )
            if (
                inv_series.inventory_cf_adjustment_difference is not None
                and self._n > 1
            ):
                assert cf_row is not None and implied_row is not None
                cf_diff_row = cursor + 1
                cursor = cf_diff_row
                ws.cell(
                    row=cf_diff_row,
                    column=1,
                    value="Unexplained inventory CF difference",
                )

            def _inv_expected(value: float | str | None) -> float | str:
                assert value is not None
                return value if isinstance(value, str) else float(value)

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                inv_f = f"='Balance Sheet'!{src_col}{inventory_src}"
                c = ws.cell(row=inventory_row, column=out_col_idx, value=inv_f)
                c.number_format = NUM_FMT
                if revenue_row is not None:
                    revenue_src = self._resolved_source_row(
                        self.fin.income_statement, REVENUE_CONCEPT, required=True
                    )
                    assert revenue_src is not None
                    rev_f = f"='Income Statement'!{src_col}{revenue_src}"
                    c = ws.cell(row=revenue_row, column=out_col_idx, value=rev_f)
                    c.number_format = NUM_FMT
                if intensity_row is not None and revenue_row is not None:
                    intensity_f = (
                        f"=IF({out_col}{revenue_row}=0,NA(),"
                        f"{out_col}{inventory_row}/{out_col}{revenue_row})"
                    )
                    c = ws.cell(
                        row=intensity_row, column=out_col_idx, value=intensity_f
                    )
                    c.number_format = PCT_FMT
                    assert inv_series.inventory_intensity is not None
                    self._register_inventory_analysis(
                        "inventory_intensity",
                        j,
                        "ALT DuPont",
                        intensity_row,
                        out_col_idx,
                        intensity_f,
                        _inv_expected(inv_series.inventory_intensity[j]),
                    )
                if cf_row is not None and cf_src is not None:
                    cf_f = f"='Cash Flow Statement'!{src_col}{cf_src}"
                    c = ws.cell(row=cf_row, column=out_col_idx, value=cf_f)
                    c.number_format = NUM_FMT
                if j == 0:
                    continue
                prev_col = self._col(2 + j - 1)
                if change_row is not None:
                    change_f = (
                        f"={out_col}{inventory_row}-{prev_col}{inventory_row}"
                    )
                    c = ws.cell(
                        row=change_row, column=out_col_idx, value=change_f
                    )
                    c.number_format = NUM_FMT
                    assert inv_series.inventory_change is not None
                    self._register_inventory_analysis(
                        "inventory_change",
                        j,
                        "ALT DuPont",
                        change_row,
                        out_col_idx,
                        change_f,
                        _inv_expected(inv_series.inventory_change[j]),
                    )
                if (
                    scale_row is not None
                    and intensity_row is not None
                    and revenue_row is not None
                ):
                    scale_f = (
                        f"={prev_col}{intensity_row}*"
                        f"({out_col}{revenue_row}-{prev_col}{revenue_row})"
                    )
                    c = ws.cell(row=scale_row, column=out_col_idx, value=scale_f)
                    c.number_format = NUM_FMT
                    assert inv_series.inventory_revenue_scale_effect is not None
                    self._register_inventory_analysis(
                        "inventory_revenue_scale_effect",
                        j,
                        "ALT DuPont",
                        scale_row,
                        out_col_idx,
                        scale_f,
                        _inv_expected(
                            inv_series.inventory_revenue_scale_effect[j]
                        ),
                    )
                if (
                    intensity_effect_row is not None
                    and intensity_row is not None
                    and revenue_row is not None
                ):
                    intensity_effect_f = (
                        f"={out_col}{revenue_row}*"
                        f"({out_col}{intensity_row}-{prev_col}{intensity_row})"
                    )
                    c = ws.cell(
                        row=intensity_effect_row,
                        column=out_col_idx,
                        value=intensity_effect_f,
                    )
                    c.number_format = NUM_FMT
                    assert inv_series.inventory_intensity_effect is not None
                    self._register_inventory_analysis(
                        "inventory_intensity_effect",
                        j,
                        "ALT DuPont",
                        intensity_effect_row,
                        out_col_idx,
                        intensity_effect_f,
                        _inv_expected(inv_series.inventory_intensity_effect[j]),
                    )
                if (
                    reconstructed_row is not None
                    and scale_row is not None
                    and intensity_effect_row is not None
                ):
                    reconstructed_f = (
                        f"={out_col}{scale_row}+{out_col}{intensity_effect_row}"
                    )
                    c = ws.cell(
                        row=reconstructed_row,
                        column=out_col_idx,
                        value=reconstructed_f,
                    )
                    c.number_format = NUM_FMT
                    assert inv_series.reconstructed_inventory_change is not None
                    self._register_inventory_analysis(
                        "reconstructed_inventory_change",
                        j,
                        "ALT DuPont",
                        reconstructed_row,
                        out_col_idx,
                        reconstructed_f,
                        _inv_expected(
                            inv_series.reconstructed_inventory_change[j]
                        ),
                    )
                if implied_row is not None and change_row is not None:
                    implied_f = f"=-{out_col}{change_row}"
                    c = ws.cell(
                        row=implied_row, column=out_col_idx, value=implied_f
                    )
                    c.number_format = NUM_FMT
                    assert inv_series.inventory_balance_implied_cf_adjustment is not None
                    self._register_inventory_analysis(
                        "inventory_balance_implied_cf_adjustment",
                        j,
                        "ALT DuPont",
                        implied_row,
                        out_col_idx,
                        implied_f,
                        _inv_expected(
                            inv_series.inventory_balance_implied_cf_adjustment[j]
                        ),
                    )
                if (
                    cf_diff_row is not None
                    and cf_row is not None
                    and implied_row is not None
                ):
                    cf_diff_f = f"={out_col}{cf_row}-{out_col}{implied_row}"
                    c = ws.cell(
                        row=cf_diff_row, column=out_col_idx, value=cf_diff_f
                    )
                    c.number_format = NUM_FMT
                    assert inv_series.inventory_cf_adjustment_difference is not None
                    self._register_inventory_analysis(
                        "inventory_cf_adjustment_difference",
                        j,
                        "ALT DuPont",
                        cf_diff_row,
                        out_col_idx,
                        cf_diff_f,
                        _inv_expected(
                            inv_series.inventory_cf_adjustment_difference[j]
                        ),
                    )

            self.rowmap["dupont_inventory_reported_row"] = inventory_row
            if revenue_row is not None:
                self.rowmap["dupont_inventory_revenue_row"] = revenue_row
            if intensity_row is not None:
                self.rowmap["dupont_inventory_intensity_row"] = intensity_row
            if change_row is not None:
                self.rowmap["dupont_inventory_change_row"] = change_row
            if scale_row is not None:
                self.rowmap["dupont_inventory_revenue_scale_effect_row"] = (
                    scale_row
                )
            if intensity_effect_row is not None:
                self.rowmap["dupont_inventory_intensity_effect_row"] = (
                    intensity_effect_row
                )
            if reconstructed_row is not None:
                self.rowmap["dupont_reconstructed_inventory_change_row"] = (
                    reconstructed_row
                )
            if cf_row is not None:
                self.rowmap["dupont_inventory_cf_adjustment_reported_row"] = cf_row
            if implied_row is not None:
                self.rowmap["dupont_inventory_balance_implied_cf_adjustment_row"] = (
                    implied_row
                )
            if cf_diff_row is not None:
                self.rowmap["dupont_inventory_cf_adjustment_difference_row"] = (
                    cf_diff_row
                )
            next_section_after = cursor

        if self.goodwill_intangibles_series is None:
            return

        series = self.goodwill_intangibles_series
        avail = self.goodwill_intangibles_availability
        sources = resolve_goodwill_intangibles_sources(self.fin)
        rev_r = self.rowmap["condensed_revenue_row"]

        gi_section_row = next_section_after + 2
        row_cursor = gi_section_row + 1
        ws.cell(
            row=gi_section_row, column=1, value="GOODWILL & INTANGIBLES CONTEXT"
        ).font = BOLD

        def _populate_balance_block(
            *,
            label: str,
            family_prefix: str,
            balance,
            source_row: int | None,
            combined_left_row: int | None = None,
            combined_right_row: int | None = None,
        ) -> int:
            nonlocal row_cursor
            level_row = row_cursor
            change_row = row_cursor + 1
            growth_row = row_cursor + 2
            avg_row = row_cursor + 3
            intensity_row = row_cursor + 4
            row_cursor += 5

            ws.cell(row=level_row, column=1, value=label)
            ws.cell(row=change_row, column=1, value=f"Change in {label}")
            ws.cell(row=growth_row, column=1, value=f"{label} Growth")
            ws.cell(row=avg_row, column=1, value=f"Average {label}")
            ws.cell(row=intensity_row, column=1, value=f"Average {label} / Revenue")

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                if source_row is not None:
                    level_f = f"='Balance Sheet'!{src_col}{source_row}"
                else:
                    assert (
                        combined_left_row is not None
                        and combined_right_row is not None
                    )
                    level_f = (
                        f"={out_col}{combined_left_row}+{out_col}{combined_right_row}"
                    )
                c = ws.cell(row=level_row, column=out_col_idx, value=level_f)
                c.number_format = NUM_FMT

                if j == 0:
                    continue

                prev_col = self._col(2 + j - 1)
                change_f = f"={out_col}{level_row}-{prev_col}{level_row}"
                growth_f = (
                    f"=IF({prev_col}{level_row}=0,NA(),"
                    f"{out_col}{level_row}/{prev_col}{level_row}-1)"
                )
                avg_f = f"=({prev_col}{level_row}+{out_col}{level_row})/2"
                intensity_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{avg_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=change_row, column=out_col_idx, value=change_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=growth_row, column=out_col_idx, value=growth_f)
                c.number_format = PCT_FMT
                c = ws.cell(row=avg_row, column=out_col_idx, value=avg_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=intensity_row, column=out_col_idx, value=intensity_f)
                c.number_format = PCT_FMT

                change_exp = balance.change[j]
                growth_exp = balance.growth[j]
                avg_exp = balance.average[j]
                intensity_exp = balance.to_revenue[j]
                assert change_exp is not None and growth_exp is not None
                assert avg_exp is not None and intensity_exp is not None
                self._register_goodwill_intangibles(
                    f"{family_prefix}_change",
                    j,
                    "ALT DuPont",
                    change_row,
                    out_col_idx,
                    change_f,
                    float(change_exp),
                )
                self._register_goodwill_intangibles(
                    f"{family_prefix}_growth",
                    j,
                    "ALT DuPont",
                    growth_row,
                    out_col_idx,
                    growth_f,
                    growth_exp if isinstance(growth_exp, str) else float(growth_exp),
                )
                self._register_goodwill_intangibles(
                    f"average_{family_prefix}",
                    j,
                    "ALT DuPont",
                    avg_row,
                    out_col_idx,
                    avg_f,
                    float(avg_exp),
                )
                self._register_goodwill_intangibles(
                    f"{family_prefix}_to_revenue",
                    j,
                    "ALT DuPont",
                    intensity_row,
                    out_col_idx,
                    intensity_f,
                    intensity_exp
                    if isinstance(intensity_exp, str)
                    else float(intensity_exp),
                )
            return level_row

        gw_level_row = None
        ia_level_row = None
        if avail.goodwill and series.goodwill is not None and sources.goodwill is not None:
            gw_src = self._resolved_source_row(
                self.fin.balance_sheet, "goodwill", required=True
            )
            assert gw_src is not None
            gw_level_row = _populate_balance_block(
                label="Goodwill",
                family_prefix="goodwill",
                balance=series.goodwill,
                source_row=gw_src,
            )
            self.rowmap["dupont_goodwill_row"] = gw_level_row

        if (
            avail.intangible_assets
            and series.intangible_assets is not None
            and sources.intangible_assets is not None
        ):
            ia_src = self._resolved_source_row(
                self.fin.balance_sheet, "intangible_assets", required=True
            )
            assert ia_src is not None
            ia_level_row = _populate_balance_block(
                label="Intangible Assets",
                family_prefix="intangible_assets",
                balance=series.intangible_assets,
                source_row=ia_src,
            )
            self.rowmap["dupont_intangible_assets_row"] = ia_level_row

        if (
            avail.goodwill_and_intangibles
            and series.goodwill_and_intangibles is not None
            and gw_level_row is not None
            and ia_level_row is not None
        ):
            comb_level = _populate_balance_block(
                label="Goodwill & Intangibles",
                family_prefix="goodwill_and_intangibles",
                balance=series.goodwill_and_intangibles,
                source_row=None,
                combined_left_row=gw_level_row,
                combined_right_row=ia_level_row,
            )
            self.rowmap["dupont_goodwill_and_intangibles_row"] = comb_level

        if (
            avail.payments_for_intangible_assets
            and series.intangible_payments is not None
            and series.intangible_payments_to_revenue is not None
            and series.payments_reported is not None
            and sources.payments_for_intangible_assets is not None
        ):
            pay_src = self._resolved_source_row(
                self.fin.cash_flow, "payments_for_intangible_assets", required=True
            )
            assert pay_src is not None
            reported_row = row_cursor
            payments_row = row_cursor + 1
            payments_rev_row = row_cursor + 2
            row_cursor += 3

            ws.cell(
                row=reported_row,
                column=1,
                value="Payments for Intangible Assets (reported)",
            )
            ws.cell(row=payments_row, column=1, value="Intangible Payments (−reported)")
            ws.cell(
                row=payments_rev_row, column=1, value="Intangible Payments / Revenue"
            )

            for j in range(self._n):
                out_col_idx = 2 + j
                out_col = self._col(out_col_idx)
                src_col = self._col(2 + j)
                reported_f = f"='Cash Flow Statement'!{src_col}{pay_src}"
                payments_f = f"=-{out_col}{reported_row}"
                payments_rev_f = (
                    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                    f"{out_col}{payments_row}/'Condensed Financials'!{src_col}{rev_r})"
                )
                c = ws.cell(row=reported_row, column=out_col_idx, value=reported_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=payments_row, column=out_col_idx, value=payments_f)
                c.number_format = NUM_FMT
                c = ws.cell(
                    row=payments_rev_row, column=out_col_idx, value=payments_rev_f
                )
                c.number_format = PCT_FMT

                pay_exp = series.intangible_payments[j]
                pay_rev_exp = series.intangible_payments_to_revenue[j]
                self._register_goodwill_intangibles(
                    "intangible_payments",
                    j,
                    "ALT DuPont",
                    payments_row,
                    out_col_idx,
                    payments_f,
                    float(pay_exp),
                )
                self._register_goodwill_intangibles(
                    "intangible_payments_to_revenue",
                    j,
                    "ALT DuPont",
                    payments_rev_row,
                    out_col_idx,
                    payments_rev_f,
                    pay_rev_exp
                    if isinstance(pay_rev_exp, str)
                    else float(pay_rev_exp),
                )

            self.rowmap["dupont_intangible_payments_reported_row"] = reported_row
            self.rowmap["dupont_intangible_payments_row"] = payments_row
            self.rowmap["dupont_intangible_payments_to_revenue_row"] = payments_rev_row

    def _build_accounting_judgment(self, wb: Workbook) -> None:
        ws = wb.create_sheet(JUDGMENT_SHEET)
        ws["A1"] = "Accounting Judgment"
        ws["A1"].font = BOLD
        ws["A2"] = JUDGMENT_INSTRUCTION
        ws["A3"] = JUDGMENT_STEP_NOTE
        headers = [
            "Order",
            "Line item",
            "Topic",
            "Supplied reference treatment",
            "Alternative(s) to evaluate",
            "Treatment to defend",
            "Rationale",
            "Economic consequence",
        ]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = BOLD
        widths = (8, 32, 36, 28, 32, 28, 40, 44)
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[self._col(idx)].width = width

        if not self.judgment_cases:
            ws.cell(
                row=5,
                column=1,
                value=(
                    "No supported guided classification judgments were identified "
                    "from the supplied company data."
                ),
            )
            return

        for case in self.judgment_cases:
            row = 4 + case.order
            options = (case.supplied_treatment,) + case.alternatives
            ws.cell(row=row, column=1, value=case.order)
            ws.cell(row=row, column=2, value=case.label)
            ws.cell(row=row, column=3, value=case.topic)
            ws.cell(row=row, column=4, value=case.supplied_treatment)
            ws.cell(row=row, column=5, value=", ".join(case.alternatives))
            treatment = ws.cell(row=row, column=6, value=case.supplied_treatment)
            rationale = ws.cell(row=row, column=7, value=case.model_rationale)
            consequence = ws.cell(row=row, column=8, value=case.model_consequence)
            wrap = Alignment(wrap_text=True, vertical="top")
            for cell in (treatment, rationale, consequence):
                cell.fill = PRACTICE_YELLOW
                cell.alignment = wrap
            dv = DataValidation(
                type="list",
                formula1='"' + ",".join(options) + '"',
                allow_blank=True,
            )
            ws.add_data_validation(dv)
            dv.add(treatment)

    def _build_ownership_attribution(self, wb: Workbook) -> None:
        if self.ownership_attribution_series is None:
            raise RuntimeError(
                "ownership_attribution_series required when building Ownership Attribution"
            )

        series = self.ownership_attribution_series
        parent_profit_src = self._resolved_source_row(
            self.fin.income_statement,
            "profit_attributable_to_owners",
            required=True,
        )
        nci_profit_src = self._resolved_source_row(
            self.fin.income_statement,
            "profit_attributable_to_nci",
            required=True,
        )
        total_profit_src = self._resolved_source_row(
            self.fin.income_statement,
            "net_income",
            required=True,
        )
        parent_equity_src = self._resolved_source_row(
            self.fin.balance_sheet,
            "equity_attributable_to_owners",
            required=True,
        )
        nci_equity_src = self._resolved_source_row(
            self.fin.balance_sheet,
            "noncontrolling_interests",
            required=True,
        )
        total_equity_src = self._resolved_source_row(
            self.fin.balance_sheet,
            "total_equity",
            required=True,
        )
        assert parent_profit_src is not None
        assert nci_profit_src is not None
        assert total_profit_src is not None
        assert parent_equity_src is not None
        assert nci_equity_src is not None
        assert total_equity_src is not None

        ws = wb.create_sheet(OWNERSHIP_ATTRIBUTION_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Ownership Attribution"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Parent / NCI profit and equity bridges and parent ROE. Consolidated "
            "DuPont / NOA / Net Debt remain unchanged; parent ROE is a separate "
            "shareholder-attribution diagnostic."
        )
        ws.column_dimensions["A"].width = 40

        header_row = 4
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        parent_profit_row = 5
        nci_profit_row = 6
        total_profit_row = 7
        profit_gap_row = 8
        parent_equity_row = 10
        nci_equity_row = 11
        total_equity_row = 12
        equity_gap_row = 13
        parent_roe_row = 15

        ws.cell(row=parent_profit_row, column=1, value="Parent Profit")
        ws.cell(row=nci_profit_row, column=1, value="NCI Profit")
        ws.cell(row=total_profit_row, column=1, value="Total Profit")
        ws.cell(row=profit_gap_row, column=1, value="Profit Attribution Gap")
        ws.cell(row=parent_equity_row, column=1, value="Parent Equity")
        ws.cell(row=nci_equity_row, column=1, value="NCI Equity")
        ws.cell(row=total_equity_row, column=1, value="Total Equity")
        ws.cell(row=equity_gap_row, column=1, value="Equity Attribution Gap")
        ws.cell(row=parent_roe_row, column=1, value="Parent ROE")

        for j in range(self._n):
            col = self._col(2 + j)
            out_col_idx = 2 + j

            parent_profit_f = f"='Income Statement'!{col}{parent_profit_src}"
            nci_profit_f = f"='Income Statement'!{col}{nci_profit_src}"
            total_profit_f = f"='Income Statement'!{col}{total_profit_src}"
            profit_gap_f = (
                f"={col}{parent_profit_row}+{col}{nci_profit_row}-{col}{total_profit_row}"
            )
            parent_equity_f = f"='Balance Sheet'!{col}{parent_equity_src}"
            nci_equity_f = f"='Balance Sheet'!{col}{nci_equity_src}"
            total_equity_f = f"='Balance Sheet'!{col}{total_equity_src}"
            equity_gap_f = (
                f"={col}{parent_equity_row}+{col}{nci_equity_row}-{col}{total_equity_row}"
            )

            for row, formula in (
                (parent_profit_row, parent_profit_f),
                (nci_profit_row, nci_profit_f),
                (total_profit_row, total_profit_f),
                (profit_gap_row, profit_gap_f),
                (parent_equity_row, parent_equity_f),
                (nci_equity_row, nci_equity_f),
                (total_equity_row, total_equity_f),
                (equity_gap_row, equity_gap_f),
            ):
                c = ws.cell(row=row, column=out_col_idx, value=formula)
                c.number_format = NUM_FMT

            self._register_ownership_attribution(
                "parent_profit_source_link",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                parent_profit_row,
                out_col_idx,
                parent_profit_f,
                float(series.parent_profit[j]),
            )
            self._register_ownership_attribution(
                "nci_profit_source_link",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                nci_profit_row,
                out_col_idx,
                nci_profit_f,
                float(series.nci_profit[j]),
            )
            self._register_ownership_attribution(
                "profit_attribution_gap",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                profit_gap_row,
                out_col_idx,
                profit_gap_f,
                float(series.profit_attribution_gap[j]),
            )
            self._register_ownership_attribution(
                "parent_equity_source_link",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                parent_equity_row,
                out_col_idx,
                parent_equity_f,
                float(series.parent_equity[j]),
            )
            self._register_ownership_attribution(
                "nci_equity_source_link",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                nci_equity_row,
                out_col_idx,
                nci_equity_f,
                float(series.nci_equity[j]),
            )
            self._register_ownership_attribution(
                "equity_attribution_gap",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                equity_gap_row,
                out_col_idx,
                equity_gap_f,
                float(series.equity_attribution_gap[j]),
            )

            if j == 0:
                ws.cell(row=parent_roe_row, column=out_col_idx, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            parent_roe_f = (
                f"=IF(({col}{parent_equity_row}+{prev_col}{parent_equity_row})=0,NA(),"
                f"{col}{parent_profit_row}/"
                f"(({col}{parent_equity_row}+{prev_col}{parent_equity_row})/2))"
            )
            c = ws.cell(row=parent_roe_row, column=out_col_idx, value=parent_roe_f)
            c.number_format = PCT_FMT
            roe_exp = series.parent_roe[j]
            assert roe_exp is not None
            self._register_ownership_attribution(
                "parent_roe",
                j,
                OWNERSHIP_ATTRIBUTION_SHEET,
                parent_roe_row,
                out_col_idx,
                parent_roe_f,
                roe_exp if isinstance(roe_exp, str) else float(roe_exp),
            )

        self.rowmap["ownership_parent_profit_row"] = parent_profit_row
        self.rowmap["ownership_nci_profit_row"] = nci_profit_row
        self.rowmap["ownership_total_profit_row"] = total_profit_row
        self.rowmap["ownership_profit_gap_row"] = profit_gap_row
        self.rowmap["ownership_parent_equity_row"] = parent_equity_row
        self.rowmap["ownership_nci_equity_row"] = nci_equity_row
        self.rowmap["ownership_total_equity_row"] = total_equity_row
        self.rowmap["ownership_equity_gap_row"] = equity_gap_row
        self.rowmap["ownership_parent_roe_row"] = parent_roe_row

    def _build_normalization_judgment(self, wb: Workbook) -> None:
        ws = wb.create_sheet(NORMALIZATION_JUDGMENT_SHEET)
        ws["A1"] = "Normalization Judgment"
        ws["A1"].font = BOLD
        ws["A2"] = NORMALIZATION_JUDGMENT_INSTRUCTION
        ws["A3"] = NORMALIZATION_JUDGMENT_STEP_NOTE
        headers = [
            "Order",
            "Line item",
            "Scope",
            "Supplied reference treatment",
            "Alternative to evaluate",
            "Treatment to defend",
            "Rationale",
            "Economic consequence",
        ]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = BOLD
        widths = (8, 32, 36, 28, 32, 28, 40, 44)
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[self._col(idx)].width = width

        for case in self.normalization_cases:
            row = 4 + case.order
            options = (case.reference_treatment,) + case.alternatives
            ws.cell(row=row, column=1, value=case.order)
            ws.cell(row=row, column=2, value=case.label)
            ws.cell(row=row, column=3, value=case.scope)
            ws.cell(row=row, column=4, value=case.reference_treatment)
            ws.cell(row=row, column=5, value=", ".join(case.alternatives))
            treatment = ws.cell(row=row, column=6, value=case.reference_treatment)
            rationale = ws.cell(row=row, column=7, value=case.model_rationale)
            consequence = ws.cell(row=row, column=8, value=case.model_consequence)
            wrap = Alignment(wrap_text=True, vertical="top")
            for cell in (treatment, rationale, consequence):
                cell.fill = PRACTICE_YELLOW
                cell.alignment = wrap
            dv = DataValidation(
                type="list",
                formula1='"' + ",".join(options) + '"',
                allow_blank=True,
            )
            ws.add_data_validation(dv)
            dv.add(treatment)

    def _build_earnings_normalization(self, wb: Workbook) -> None:
        from ..trainer.check_context import live_normalization_treatment_formula

        if self.normalization_series is None:
            raise RuntimeError("normalization_series required when building Earnings Normalization")

        ws = wb.create_sheet(EARNINGS_NORMALIZATION_SHEET)
        ws["A1"] = "Earnings Normalization"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Reported statements stay unchanged. Bridge reported NOPAT / Net Income to "
            "normalized earnings using the treatments chosen on Normalization Judgment."
        )
        ws.column_dimensions["A"].width = 40
        ws.column_dimensions["B"].width = 18

        header_row = 4
        ws.cell(row=header_row, column=1, value="Line item").font = BOLD
        ws.cell(row=header_row, column=2, value="Treatment").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=3 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(3 + j)].width = 14

        detail_start = header_row + 1
        for case in self.normalization_cases:
            row = header_row + case.order
            source_row = self.rowmap[f"Income Statement!{case.line_identity}"]
            ws.cell(row=row, column=1, value=case.label)
            formula = live_normalization_treatment_formula(
                4 + case.order,
                case.reference_treatment,
            )
            ws.cell(row=row, column=2, value=formula)
            for j in range(self._n):
                src_col = self._col(2 + j)
                cell = ws.cell(
                    row=row,
                    column=3 + j,
                    value=f"='Income Statement'!{src_col}{source_row}",
                )
                cell.number_format = NUM_FMT
        detail_end = header_row + len(self.normalization_cases)

        bridge_start = detail_end + 2
        nopat_r = self.rowmap["condensed_nopat_row"]
        ni_r = self.rowmap["condensed_ni_row"]
        etr_r = self.rowmap["condensed_etr_row"]
        series = self.normalization_series

        reported_nopat_row = bridge_start
        reported_ni_row = bridge_start + 1
        pretax_row = bridge_start + 2
        etr_row = bridge_start + 3
        after_tax_row = bridge_start + 4
        norm_nopat_row = bridge_start + 5
        norm_ni_row = bridge_start + 6
        check_row = bridge_start + 7

        bridge_labels = (
            (reported_nopat_row, "Reported NOPAT"),
            (reported_ni_row, "Reported Net Income"),
            (pretax_row, "Pretax Normalization Adjustment"),
            (etr_row, "Effective Tax Rate"),
            (after_tax_row, "After-tax Normalization Adjustment"),
            (norm_nopat_row, "Normalized NOPAT"),
            (norm_ni_row, "Normalized Net Income"),
            (check_row, "NORMALIZATION CHECK"),
        )
        for row, label in bridge_labels:
            font = BOLD if label in {"NORMALIZATION CHECK"} else None
            cell = ws.cell(row=row, column=1, value=label)
            if font is not None:
                cell.font = font

        treat_range = f"$B${detail_start}:$B${detail_end}"
        for j in range(self._n):
            period_col = self._col(3 + j)
            condensed_col = self._col(2 + j)
            value_range = f"{period_col}${detail_start}:{period_col}${detail_end}"

            reported_nopat = (
                f"='Condensed Financials'!{condensed_col}{nopat_r}"
            )
            reported_ni = f"='Condensed Financials'!{condensed_col}{ni_r}"
            pretax = f'=-SUMIF({treat_range},"Non-recurring",{value_range})'
            etr = f"='Condensed Financials'!{condensed_col}{etr_r}"
            after_tax = (
                f"=IF({period_col}{pretax_row}=0,0,"
                f"IF(ISNA({period_col}{etr_row}),NA(),"
                f"{period_col}{pretax_row}*(1-{period_col}{etr_row})))"
            )
            norm_nopat = f"={period_col}{reported_nopat_row}+{period_col}{after_tax_row}"
            norm_ni = f"={period_col}{reported_ni_row}+{period_col}{after_tax_row}"
            check = (
                f'=IF(AND(ABS(({period_col}{norm_nopat_row}-{period_col}{reported_nopat_row})'
                f"-{period_col}{after_tax_row})<0.01,"
                f"ABS(({period_col}{norm_ni_row}-{period_col}{reported_ni_row})"
                f"-{period_col}{after_tax_row})<0.01),\"OK\",\"CHECK\")"
            )

            for row, formula, fmt in (
                (reported_nopat_row, reported_nopat, NUM_FMT),
                (reported_ni_row, reported_ni, NUM_FMT),
                (pretax_row, pretax, NUM_FMT),
                (etr_row, etr, PCT_FMT),
                (after_tax_row, after_tax, NUM_FMT),
                (norm_nopat_row, norm_nopat, NUM_FMT),
                (norm_ni_row, norm_ni, NUM_FMT),
                (check_row, check, None),
            ):
                cell = ws.cell(row=row, column=3 + j, value=formula)
                if fmt is not None:
                    cell.number_format = fmt

            self._register_normalization(
                "pretax_normalization_adjustment",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                pretax_row,
                3 + j,
                pretax,
                series.pretax_adjustment[j],
            )
            self._register_normalization(
                "after_tax_normalization_adjustment",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                after_tax_row,
                3 + j,
                after_tax,
                series.after_tax_adjustment[j],
            )
            self._register_normalization(
                "normalized_nopat",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                norm_nopat_row,
                3 + j,
                norm_nopat,
                series.normalized_nopat[j],
            )
            self._register_normalization(
                "normalized_net_income",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                norm_ni_row,
                3 + j,
                norm_ni,
                series.normalized_net_income[j],
            )

        self.rowmap["earnings_norm_detail_start"] = detail_start
        self.rowmap["earnings_norm_detail_end"] = detail_end
        self.rowmap["earnings_norm_pretax_row"] = pretax_row
        self.rowmap["earnings_norm_after_tax_row"] = after_tax_row
        self.rowmap["earnings_norm_reported_nopat_row"] = reported_nopat_row
        self.rowmap["earnings_norm_nopat_row"] = norm_nopat_row
        self.rowmap["earnings_norm_ni_row"] = norm_ni_row
        self.rowmap["earnings_norm_check_row"] = check_row

    def _build_earnings_quality(self, wb: Workbook) -> None:
        if self.quality_series is None:
            raise RuntimeError("quality_series required when building Earnings Quality")

        ws = wb.create_sheet(EARNINGS_QUALITY_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Earnings Quality"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Historical cash-conversion and accrual diagnostics. These are mechanical "
            "diagnostics, not an automatic quality score."
        )
        ws.column_dimensions["A"].width = 42

        header_row = 4
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        cfo_src = self._resolved_source_row(
            self.fin.cash_flow, "operating_cash_flow", required=True
        )
        assert cfo_src is not None
        ni_r = self.rowmap["condensed_ni_row"]
        series = self.quality_series

        cfo_row = 5
        ni_row = 6
        conversion_row = 7
        accruals_row = 8

        ws.cell(row=cfo_row, column=1, value="Operating Cash Flow")
        ws.cell(row=ni_row, column=1, value="Reported Net Income")
        ws.cell(row=conversion_row, column=1, value="Cash Conversion Ratio")
        ws.cell(row=accruals_row, column=1, value="Total Accruals (Net Income - CFO)")

        for j in range(self._n):
            col = self._col(2 + j)
            cfo_formula = f"='Cash Flow Statement'!{col}{cfo_src}"
            ni_formula = f"='Condensed Financials'!{col}{ni_r}"
            conversion_formula = (
                f"=IF({col}{ni_row}=0,NA(),{col}{cfo_row}/{col}{ni_row})"
            )
            accruals_formula = f"={col}{ni_row}-{col}{cfo_row}"

            c = ws.cell(row=cfo_row, column=2 + j, value=cfo_formula)
            c.number_format = NUM_FMT
            c = ws.cell(row=ni_row, column=2 + j, value=ni_formula)
            c.number_format = NUM_FMT
            c = ws.cell(row=conversion_row, column=2 + j, value=conversion_formula)
            c.number_format = "0.00x"
            c = ws.cell(row=accruals_row, column=2 + j, value=accruals_formula)
            c.number_format = NUM_FMT

            self._register_quality(
                "operating_cash_flow_link",
                j,
                EARNINGS_QUALITY_SHEET,
                cfo_row,
                2 + j,
                cfo_formula,
                series.operating_cash_flow[j],
            )
            self._register_quality(
                "cash_conversion_ratio",
                j,
                EARNINGS_QUALITY_SHEET,
                conversion_row,
                2 + j,
                conversion_formula,
                series.cash_conversion_ratio[j],
            )
            self._register_quality(
                "total_accruals",
                j,
                EARNINGS_QUALITY_SHEET,
                accruals_row,
                2 + j,
                accruals_formula,
                series.total_accruals[j],
            )

        self.rowmap["quality_cfo_row"] = cfo_row
        self.rowmap["quality_ni_row"] = ni_row
        self.rowmap["quality_conversion_row"] = conversion_row
        self.rowmap["quality_accruals_row"] = accruals_row

        assets_row = None
        avg_assets_row = None
        accrual_ratio_row = None

        if self.quality_availability.total_assets:
            assets_src = self._resolved_source_row(
                self.fin.balance_sheet, "total_assets", required=True
            )
            assert assets_src is not None
            assets_row = 10
            avg_assets_row = 11
            accrual_ratio_row = 12
            ws.cell(row=assets_row, column=1, value="Total Assets")
            ws.cell(row=avg_assets_row, column=1, value="Average Total Assets")
            ws.cell(row=accrual_ratio_row, column=1, value="Accrual Ratio")

            for j in range(self._n):
                col = self._col(2 + j)
                assets_formula = f"='Balance Sheet'!{col}{assets_src}"
                c = ws.cell(row=assets_row, column=2 + j, value=assets_formula)
                c.number_format = NUM_FMT

                if j == 0:
                    ws.cell(row=avg_assets_row, column=2 + j, value=None)
                    ws.cell(row=accrual_ratio_row, column=2 + j, value=None)
                    continue

                prev_col = self._col(2 + j - 1)
                avg_formula = f"=({prev_col}{assets_row}+{col}{assets_row})/2"
                ratio_formula = (
                    f"=IF({col}{avg_assets_row}=0,NA(),"
                    f"{col}{accruals_row}/{col}{avg_assets_row})"
                )
                c = ws.cell(row=avg_assets_row, column=2 + j, value=avg_formula)
                c.number_format = NUM_FMT
                c = ws.cell(row=accrual_ratio_row, column=2 + j, value=ratio_formula)
                c.number_format = PCT_FMT

                assert series.average_total_assets[j] is not None
                assert series.accrual_ratio[j] is not None
                self._register_quality(
                    "average_total_assets",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    avg_assets_row,
                    2 + j,
                    avg_formula,
                    float(series.average_total_assets[j]),
                )
                accrual_expected = series.accrual_ratio[j]
                self._register_quality(
                    "accrual_ratio",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    accrual_ratio_row,
                    2 + j,
                    ratio_formula,
                    accrual_expected
                    if isinstance(accrual_expected, str)
                    else float(accrual_expected),
                )

            self.rowmap["quality_assets_row"] = assets_row
            self.rowmap["quality_avg_assets_row"] = avg_assets_row
            self.rowmap["quality_accrual_ratio_row"] = accrual_ratio_row

        # Cash-conversion / accrual trend diagnostics (Step 9E.1)
        if self.quality_change_series is None:
            raise RuntimeError(
                "quality_change_series required when building Earnings Quality trends"
            )
        changes = self.quality_change_series
        na = "N/A"
        trend_section_row = 14
        cfo_change_row = 15
        conversion_change_row = 16
        accruals_change_row = 17
        accrual_ratio_change_row = 18
        change_check_row = 19

        ws.cell(
            row=trend_section_row,
            column=1,
            value="EARNINGS QUALITY TREND DIAGNOSTICS",
        ).font = BOLD
        ws.cell(row=cfo_change_row, column=1, value="Change in Operating Cash Flow")
        ws.cell(
            row=conversion_change_row, column=1, value="Change in Cash Conversion Ratio"
        )
        ws.cell(row=accruals_change_row, column=1, value="Change in Total Accruals")
        ws.cell(row=accrual_ratio_change_row, column=1, value="Change in Accrual Ratio")
        ws.cell(
            row=change_check_row, column=1, value="EARNINGS QUALITY CHANGE CHECK"
        ).font = BOLD

        for j in range(self._n):
            out_col_idx = 2 + j
            col = self._col(out_col_idx)
            if j == 0:
                for row in (
                    cfo_change_row,
                    conversion_change_row,
                    accruals_change_row,
                    accrual_ratio_change_row,
                    change_check_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            prev_col = self._col(2 + j - 1)
            cfo_change_f = f"={col}{cfo_row}-{prev_col}{cfo_row}"
            conversion_change_f = f"={col}{conversion_row}-{prev_col}{conversion_row}"
            accruals_change_f = f"={col}{accruals_row}-{prev_col}{accruals_row}"
            change_check_f = (
                f'=IF(ABS({col}{accruals_change_row}-'
                f'(({col}{ni_row}-{prev_col}{ni_row})-{col}{cfo_change_row}))'
                f'<0.01,"OK","CHECK")'
            )

            c = ws.cell(row=cfo_change_row, column=out_col_idx, value=cfo_change_f)
            c.number_format = NUM_FMT
            c = ws.cell(
                row=conversion_change_row, column=out_col_idx, value=conversion_change_f
            )
            c.number_format = "0.00x"
            c = ws.cell(
                row=accruals_change_row, column=out_col_idx, value=accruals_change_f
            )
            c.number_format = NUM_FMT
            ws.cell(row=change_check_row, column=out_col_idx, value=change_check_f)

            cfo_expected = changes.operating_cash_flow_change[j]
            assert cfo_expected is not None
            self._register_quality_change(
                "operating_cash_flow_change",
                j,
                EARNINGS_QUALITY_SHEET,
                cfo_change_row,
                out_col_idx,
                cfo_change_f,
                float(cfo_expected),
            )
            conv_expected = changes.cash_conversion_ratio_change[j]
            assert conv_expected is not None
            self._register_quality_change(
                "cash_conversion_ratio_change",
                j,
                EARNINGS_QUALITY_SHEET,
                conversion_change_row,
                out_col_idx,
                conversion_change_f,
                conv_expected if isinstance(conv_expected, str) else float(conv_expected),
            )
            accruals_expected = changes.total_accruals_change[j]
            assert accruals_expected is not None
            self._register_quality_change(
                "total_accruals_change",
                j,
                EARNINGS_QUALITY_SHEET,
                accruals_change_row,
                out_col_idx,
                accruals_change_f,
                float(accruals_expected),
            )

            if not self.quality_availability.total_assets or j < 2:
                ws.cell(row=accrual_ratio_change_row, column=out_col_idx, value=na)
            else:
                assert accrual_ratio_row is not None
                accrual_ratio_change_f = (
                    f"={col}{accrual_ratio_row}-{prev_col}{accrual_ratio_row}"
                )
                c = ws.cell(
                    row=accrual_ratio_change_row,
                    column=out_col_idx,
                    value=accrual_ratio_change_f,
                )
                c.number_format = PCT_FMT
                ar_expected = changes.accrual_ratio_change[j]
                assert ar_expected is not None
                self._register_quality_change(
                    "accrual_ratio_change",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    accrual_ratio_change_row,
                    out_col_idx,
                    accrual_ratio_change_f,
                    ar_expected if isinstance(ar_expected, str) else float(ar_expected),
                )

        # When assets are absent, mark accrual-ratio change N/A for period 0 too
        # (already handled above for all j when assets absent / j<2).
        if not self.quality_availability.total_assets:
            ws.cell(row=accrual_ratio_change_row, column=2, value=na)

        self.rowmap["quality_change_cfo_row"] = cfo_change_row
        self.rowmap["quality_change_conversion_row"] = conversion_change_row
        self.rowmap["quality_change_accruals_row"] = accruals_change_row
        self.rowmap["quality_change_accrual_ratio_row"] = accrual_ratio_change_row
        self.rowmap["quality_change_check_row"] = change_check_row

        if series.operating_cash_flow_less_sbc is not None:
            assert series.sbc_to_revenue is not None
            assert series.sbc_to_operating_cash_flow is not None
            assert series.stock_based_compensation is not None
            sbc_item = resolve_sbc_source(self.fin)
            assert sbc_item is not None
            sbc_src = self._resolved_source_row(
                self.fin.cash_flow, "stock_based_compensation", required=True
            )
            assert sbc_src is not None
            rev_r = self.rowmap["condensed_revenue_row"]

            sbc_section_row = change_check_row + 2
            sbc_reported_row = sbc_section_row + 1
            sbc_rev_row = sbc_section_row + 2
            sbc_cfo_row = sbc_section_row + 3
            cfo_less_sbc_row = sbc_section_row + 4

            ws.cell(
                row=sbc_section_row,
                column=1,
                value="STOCK-BASED COMPENSATION CASH DIAGNOSTICS",
            ).font = BOLD
            ws.cell(
                row=sbc_reported_row,
                column=1,
                value="Stock-based compensation (reported)",
            )
            ws.cell(row=sbc_rev_row, column=1, value="SBC / Revenue")
            ws.cell(row=sbc_cfo_row, column=1, value="SBC / Operating Cash Flow")
            ws.cell(
                row=cfo_less_sbc_row,
                column=1,
                value="Reported CFO less SBC add-back",
            )

            for j in range(self._n):
                col = self._col(2 + j)
                sbc_f = f"='Cash Flow Statement'!{col}{sbc_src}"
                sbc_rev_f = (
                    f"=IF('Condensed Financials'!{col}{rev_r}=0,NA(),"
                    f"{col}{sbc_reported_row}/'Condensed Financials'!{col}{rev_r})"
                )
                sbc_cfo_f = (
                    f"=IF({col}{cfo_row}=0,NA(),"
                    f"{col}{sbc_reported_row}/{col}{cfo_row})"
                )
                cfo_less_f = f"={col}{cfo_row}-{col}{sbc_reported_row}"

                c = ws.cell(row=sbc_reported_row, column=2 + j, value=sbc_f)
                c.number_format = NUM_FMT
                c = ws.cell(row=sbc_rev_row, column=2 + j, value=sbc_rev_f)
                c.number_format = PCT_FMT
                c = ws.cell(row=sbc_cfo_row, column=2 + j, value=sbc_cfo_f)
                c.number_format = PCT_FMT
                c = ws.cell(row=cfo_less_sbc_row, column=2 + j, value=cfo_less_f)
                c.number_format = NUM_FMT

                sbc_rev_exp = series.sbc_to_revenue[j]
                sbc_cfo_exp = series.sbc_to_operating_cash_flow[j]
                cfo_less_exp = series.operating_cash_flow_less_sbc[j]
                self._register_quality(
                    "sbc_to_revenue",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    sbc_rev_row,
                    2 + j,
                    sbc_rev_f,
                    sbc_rev_exp if isinstance(sbc_rev_exp, str) else float(sbc_rev_exp),
                )
                self._register_quality(
                    "sbc_to_operating_cash_flow",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    sbc_cfo_row,
                    2 + j,
                    sbc_cfo_f,
                    sbc_cfo_exp if isinstance(sbc_cfo_exp, str) else float(sbc_cfo_exp),
                )
                self._register_quality(
                    "operating_cash_flow_less_sbc",
                    j,
                    EARNINGS_QUALITY_SHEET,
                    cfo_less_sbc_row,
                    2 + j,
                    cfo_less_f,
                    float(cfo_less_exp),
                )

            self.rowmap["quality_sbc_reported_row"] = sbc_reported_row
            self.rowmap["quality_sbc_to_revenue_row"] = sbc_rev_row
            self.rowmap["quality_sbc_to_cfo_row"] = sbc_cfo_row
            self.rowmap["quality_cfo_less_sbc_row"] = cfo_less_sbc_row

    def _build_working_capital_analysis(self, wb: Workbook) -> None:
        if self.working_capital_series is None:
            raise RuntimeError(
                "working_capital_series required when building Working Capital Analysis"
            )

        ws = wb.create_sheet(WORKING_CAPITAL_SHEET)
        ws["A1"] = "Working Capital Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Relate classified operating working capital to Revenue and identify how "
            "much incremental NOWC accompanies changes in sales."
        )
        ws["A3"] = (
            "These are diagnostics, not automatic judgments. Positive Change in NOWC "
            "is an operating cash use; negative Change in NOWC is a release. Annual "
            "data alone does not prove seasonality or deterioration."
        )
        ws.column_dimensions["A"].width = 48

        header_row = 5
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        rev_r = self.rowmap["condensed_revenue_row"]
        owca_r = self.rowmap["condensed_owca_row"]
        owcl_r = self.rowmap["condensed_owcl_row"]
        nowc_r = self.rowmap["condensed_nowc_row"]
        series = self.working_capital_series

        rev_row = 6
        owca_row = 7
        owcl_row = 8
        nowc_row = 9
        owca_ratio_row = 11
        owcl_ratio_row = 12
        nowc_ratio_row = 13
        rev_chg_row = 14
        nowc_chg_row = 15
        incr_row = 16

        ws.cell(row=rev_row, column=1, value="Revenue")
        ws.cell(row=owca_row, column=1, value="Operating Working Capital Assets")
        ws.cell(row=owcl_row, column=1, value="Operating Working Capital Liabilities")
        ws.cell(row=nowc_row, column=1, value="NOWC")
        ws.cell(row=owca_ratio_row, column=1, value="OWCA / Revenue")
        ws.cell(row=owcl_ratio_row, column=1, value="OWCL / Revenue")
        ws.cell(row=nowc_ratio_row, column=1, value="NOWC / Revenue")
        ws.cell(row=rev_chg_row, column=1, value="Change in Revenue")
        ws.cell(row=nowc_chg_row, column=1, value="Change in NOWC")
        ws.cell(row=incr_row, column=1, value="Incremental NOWC / Change in Revenue")

        for j in range(self._n):
            col = self._col(2 + j)
            for row, src in (
                (rev_row, rev_r),
                (owca_row, owca_r),
                (owcl_row, owcl_r),
                (nowc_row, nowc_r),
            ):
                formula = f"='Condensed Financials'!{col}{src}"
                c = ws.cell(row=row, column=2 + j, value=formula)
                c.number_format = NUM_FMT

            owca_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{owca_row}/{col}{rev_row})"
            owcl_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{owcl_row}/{col}{rev_row})"
            nowc_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{nowc_row}/{col}{rev_row})"
            for row, formula in (
                (owca_ratio_row, owca_ratio),
                (owcl_ratio_row, owcl_ratio),
                (nowc_ratio_row, nowc_ratio),
            ):
                c = ws.cell(row=row, column=2 + j, value=formula)
                c.number_format = PCT_FMT

            self._register_working_capital(
                "owca_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                owca_ratio_row,
                2 + j,
                owca_ratio,
                series.owca_to_revenue[j],
            )
            self._register_working_capital(
                "owcl_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                owcl_ratio_row,
                2 + j,
                owcl_ratio,
                series.owcl_to_revenue[j],
            )
            self._register_working_capital(
                "nowc_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_ratio_row,
                2 + j,
                nowc_ratio,
                series.nowc_to_revenue[j],
            )

            if j == 0:
                ws.cell(row=rev_chg_row, column=2 + j, value="N/A")
                ws.cell(row=nowc_chg_row, column=2 + j, value="N/A")
                ws.cell(row=incr_row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            rev_chg = f"={col}{rev_row}-{prev_col}{rev_row}"
            nowc_chg = f"={col}{nowc_row}-{prev_col}{nowc_row}"
            incr = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{nowc_chg_row}/{col}{rev_chg_row})"
            )
            c = ws.cell(row=rev_chg_row, column=2 + j, value=rev_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=nowc_chg_row, column=2 + j, value=nowc_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=incr_row, column=2 + j, value=incr)
            c.number_format = PCT_FMT

            assert series.revenue_change[j] is not None
            assert series.nowc_change[j] is not None
            assert series.incremental_nowc_to_revenue_change[j] is not None
            self._register_working_capital(
                "revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                rev_chg_row,
                2 + j,
                rev_chg,
                float(series.revenue_change[j]),
            )
            self._register_working_capital(
                "nowc_change",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_chg_row,
                2 + j,
                nowc_chg,
                float(series.nowc_change[j]),
            )
            incr_expected = series.incremental_nowc_to_revenue_change[j]
            self._register_working_capital(
                "incremental_nowc_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incr_row,
                2 + j,
                incr,
                incr_expected
                if isinstance(incr_expected, str)
                else float(incr_expected),
            )

        # Driver decomposition section (Step 9B.2)
        section_row = 18
        owca_change_row = 19
        owcl_change_row = 20
        nowc_bridge_row = 21
        incremental_owca_row = 22
        incremental_owcl_row = 23
        driver_check_row = 24

        ws.cell(row=section_row, column=1, value="WORKING-CAPITAL DRIVER DECOMPOSITION").font = BOLD
        ws.cell(row=owca_change_row, column=1, value="Change in OWCA")
        ws.cell(row=owcl_change_row, column=1, value="Change in OWCL")
        ws.cell(row=nowc_bridge_row, column=1, value="Change in NOWC from Components")
        ws.cell(
            row=incremental_owca_row,
            column=1,
            value="Incremental OWCA / Change in Revenue",
        )
        ws.cell(
            row=incremental_owcl_row,
            column=1,
            value="Incremental OWCL / Change in Revenue",
        )
        ws.cell(row=driver_check_row, column=1, value="DRIVER DECOMPOSITION CHECK").font = BOLD

        for j in range(self._n):
            col = self._col(2 + j)
            if j == 0:
                for row in (
                    owca_change_row,
                    owcl_change_row,
                    nowc_bridge_row,
                    incremental_owca_row,
                    incremental_owcl_row,
                    driver_check_row,
                ):
                    ws.cell(row=row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            owca_chg = f"={col}{owca_row}-{prev_col}{owca_row}"
            owcl_chg = f"={col}{owcl_row}-{prev_col}{owcl_row}"
            nowc_bridge = f"={col}{owca_change_row}-{col}{owcl_change_row}"
            incr_owca = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{owca_change_row}/{col}{rev_chg_row})"
            )
            incr_owcl = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{owcl_change_row}/{col}{rev_chg_row})"
            )
            driver_check = (
                f'=IF(ABS({col}{nowc_bridge_row}-{col}{nowc_chg_row})<0.01,'
                f'"OK","CHECK")'
            )

            c = ws.cell(row=owca_change_row, column=2 + j, value=owca_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=owcl_change_row, column=2 + j, value=owcl_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=nowc_bridge_row, column=2 + j, value=nowc_bridge)
            c.number_format = NUM_FMT
            c = ws.cell(row=incremental_owca_row, column=2 + j, value=incr_owca)
            c.number_format = PCT_FMT
            c = ws.cell(row=incremental_owcl_row, column=2 + j, value=incr_owcl)
            c.number_format = PCT_FMT
            ws.cell(row=driver_check_row, column=2 + j, value=driver_check)

            assert series.owca_change[j] is not None
            assert series.owcl_change[j] is not None
            assert series.nowc_change_from_components[j] is not None
            self._register_working_capital(
                "owca_change",
                j,
                WORKING_CAPITAL_SHEET,
                owca_change_row,
                2 + j,
                owca_chg,
                float(series.owca_change[j]),
            )
            self._register_working_capital(
                "owcl_change",
                j,
                WORKING_CAPITAL_SHEET,
                owcl_change_row,
                2 + j,
                owcl_chg,
                float(series.owcl_change[j]),
            )
            self._register_working_capital(
                "nowc_change_from_components",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_bridge_row,
                2 + j,
                nowc_bridge,
                float(series.nowc_change_from_components[j]),
            )
            incr_owca_expected = series.incremental_owca_to_revenue_change[j]
            assert incr_owca_expected is not None
            self._register_working_capital(
                "incremental_owca_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incremental_owca_row,
                2 + j,
                incr_owca,
                incr_owca_expected
                if isinstance(incr_owca_expected, str)
                else float(incr_owca_expected),
            )
            incr_owcl_expected = series.incremental_owcl_to_revenue_change[j]
            assert incr_owcl_expected is not None
            self._register_working_capital(
                "incremental_owcl_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incremental_owcl_row,
                2 + j,
                incr_owcl,
                incr_owcl_expected
                if isinstance(incr_owcl_expected, str)
                else float(incr_owcl_expected),
            )

        self.rowmap["wc_revenue_row"] = rev_row
        self.rowmap["wc_owca_row"] = owca_row
        self.rowmap["wc_owcl_row"] = owcl_row
        self.rowmap["wc_nowc_row"] = nowc_row
        self.rowmap["wc_owca_change_row"] = owca_change_row
        self.rowmap["wc_owcl_change_row"] = owcl_change_row
        self.rowmap["wc_nowc_bridge_row"] = nowc_bridge_row
        self.rowmap["wc_incremental_owca_row"] = incremental_owca_row
        self.rowmap["wc_incremental_owcl_row"] = incremental_owcl_row
        self.rowmap["wc_driver_check_row"] = driver_check_row

    def _build_per_share_analysis(self, wb: Workbook) -> None:
        if self.per_share_series is None:
            raise RuntimeError(
                "per_share_series required when building Per Share Analysis"
            )

        ws = wb.create_sheet(PER_SHARE_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Per Share Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Historical per-share diagnostics using supplied diluted "
            "weighted-average shares. Share counts are source inputs, not "
            "practice cells."
        )
        ws.column_dimensions["A"].width = 48

        header_row = 4
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        ni_src = self.rowmap["condensed_ni_row"]
        nopat_src = self.rowmap["condensed_nopat_row"]
        series = self.per_share_series
        use_parent_profit = self.ownership_attribution_series is not None
        parent_profit_src: int | None = None
        if use_parent_profit:
            parent_profit_src = self._resolved_source_row(
                self.fin.income_statement,
                "profit_attributable_to_owners",
                required=True,
            )
            assert parent_profit_src is not None

        ni_row = 5
        nopat_row = 6
        shares_row = 7
        eps_row = 9
        nopat_ps_row = 10
        eps_chg_row = 12
        shares_chg_row = 13

        share_fmt = "#,##0.0;(#,##0.0)"
        per_share_fmt = "0.000"

        ws.cell(
            row=ni_row,
            column=1,
            value=(
                "Parent-Attributable Profit"
                if use_parent_profit
                else "Reported Net Income"
            ),
        )
        ws.cell(row=nopat_row, column=1, value="NOPAT")
        ws.cell(row=shares_row, column=1, value="Diluted Weighted-Average Shares")
        share_basis = "reported"
        if self.fin.historical_shares is not None and self.fin.historical_shares.basis:
            share_basis = self.fin.historical_shares.basis
        basis_label = (
            "Share Basis: Split-adjusted comparable basis"
            if share_basis == "split_adjusted"
            else "Share Basis: Reported basis"
        )
        ws.cell(row=8, column=1, value=basis_label)
        ws.cell(row=eps_row, column=1, value="Diluted EPS (Comparable Basis)")
        ws.cell(row=nopat_ps_row, column=1, value="NOPAT per Diluted Share")
        ws.cell(row=eps_chg_row, column=1, value="Change in Diluted EPS")
        ws.cell(
            row=shares_chg_row,
            column=1,
            value="Change in Diluted Weighted-Average Shares",
        )

        for j in range(self._n):
            col = self._col(2 + j)
            if use_parent_profit:
                ni_formula = f"='Income Statement'!{col}{parent_profit_src}"
            else:
                ni_formula = f"='Condensed Financials'!{col}{ni_src}"
            c = ws.cell(row=ni_row, column=2 + j, value=ni_formula)
            c.number_format = NUM_FMT
            nopat_formula = f"='Condensed Financials'!{col}{nopat_src}"
            c = ws.cell(row=nopat_row, column=2 + j, value=nopat_formula)
            c.number_format = NUM_FMT

            share_val = series.diluted_weighted_average_shares[j]
            c = ws.cell(row=shares_row, column=2 + j, value=float(share_val))
            c.number_format = share_fmt

            reported_eps = (
                f"=IF({col}{shares_row}<=0,NA(),{col}{ni_row}/{col}{shares_row})"
            )
            nopat_per_share = (
                f"=IF({col}{shares_row}<=0,NA(),{col}{nopat_row}/{col}{shares_row})"
            )
            c = ws.cell(row=eps_row, column=2 + j, value=reported_eps)
            c.number_format = per_share_fmt
            c = ws.cell(row=nopat_ps_row, column=2 + j, value=nopat_per_share)
            c.number_format = per_share_fmt

            self._register_per_share(
                "reported_diluted_eps",
                j,
                PER_SHARE_SHEET,
                eps_row,
                2 + j,
                reported_eps,
                series.reported_diluted_eps[j],
            )
            nopat_expected = series.nopat_per_diluted_share[j]
            self._register_per_share(
                "nopat_per_diluted_share",
                j,
                PER_SHARE_SHEET,
                nopat_ps_row,
                2 + j,
                nopat_per_share,
                nopat_expected
                if isinstance(nopat_expected, str)
                else float(nopat_expected),
            )

            if j == 0:
                ws.cell(row=eps_chg_row, column=2 + j, value="N/A")
                ws.cell(row=shares_chg_row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            eps_change = f"={col}{eps_row}-{prev_col}{eps_row}"
            shares_change = f"={col}{shares_row}-{prev_col}{shares_row}"
            c = ws.cell(row=eps_chg_row, column=2 + j, value=eps_change)
            c.number_format = per_share_fmt
            c = ws.cell(row=shares_chg_row, column=2 + j, value=shares_change)
            c.number_format = share_fmt

            assert series.diluted_eps_change[j] is not None
            assert series.diluted_share_count_change[j] is not None
            self._register_per_share(
                "diluted_eps_change",
                j,
                PER_SHARE_SHEET,
                eps_chg_row,
                2 + j,
                eps_change,
                float(series.diluted_eps_change[j]),
            )
            self._register_per_share(
                "diluted_share_count_change",
                j,
                PER_SHARE_SHEET,
                shares_chg_row,
                2 + j,
                shares_change,
                float(series.diluted_share_count_change[j]),
            )

        # Diluted EPS change attribution (Step 9F.2)
        if self.per_share_attribution_series is None:
            raise RuntimeError(
                "per_share_attribution_series required when building "
                "Per Share Analysis attribution"
            )
        attribution = self.per_share_attribution_series

        section_row = 15
        net_income_change_row = 16
        earnings_effect_row = 17
        share_count_effect_row = 18
        driver_eps_change_row = 19
        attribution_check_row = 20

        ws.cell(
            row=section_row, column=1, value="DILUTED EPS CHANGE ATTRIBUTION"
        ).font = BOLD
        ws.cell(
            row=net_income_change_row,
            column=1,
            value="Change in Per-Share Earnings Numerator",
        )
        ws.cell(
            row=earnings_effect_row,
            column=1,
            value="Earnings Effect on Change in Diluted EPS",
        )
        ws.cell(
            row=share_count_effect_row,
            column=1,
            value="Share-Count Effect on Change in Diluted EPS",
        )
        ws.cell(
            row=driver_eps_change_row,
            column=1,
            value="Diluted EPS Change from Drivers",
        )
        ws.cell(
            row=attribution_check_row,
            column=1,
            value="DILUTED EPS CHANGE ATTRIBUTION CHECK",
        ).font = BOLD

        for j in range(self._n):
            col = self._col(2 + j)
            if j == 0:
                for row in (
                    net_income_change_row,
                    earnings_effect_row,
                    share_count_effect_row,
                    driver_eps_change_row,
                    attribution_check_row,
                ):
                    ws.cell(row=row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            net_income_change_f = f"={col}{ni_row}-{prev_col}{ni_row}"
            earnings_effect_f = (
                f"={col}{net_income_change_row}*"
                f"((1/{col}{shares_row}+1/{prev_col}{shares_row})/2)"
            )
            share_count_effect_f = (
                f"=((1/{col}{shares_row})-(1/{prev_col}{shares_row}))*"
                f"(({col}{ni_row}+{prev_col}{ni_row})/2)"
            )
            driver_eps_change_f = (
                f"={col}{earnings_effect_row}+{col}{share_count_effect_row}"
            )
            attribution_check_f = (
                f'=IF(ABS({col}{driver_eps_change_row}-{col}{eps_chg_row})'
                f'<0.0000001,"OK","CHECK")'
            )

            c = ws.cell(
                row=net_income_change_row, column=2 + j, value=net_income_change_f
            )
            c.number_format = NUM_FMT
            c = ws.cell(row=earnings_effect_row, column=2 + j, value=earnings_effect_f)
            c.number_format = per_share_fmt
            c = ws.cell(
                row=share_count_effect_row, column=2 + j, value=share_count_effect_f
            )
            c.number_format = per_share_fmt
            c = ws.cell(
                row=driver_eps_change_row, column=2 + j, value=driver_eps_change_f
            )
            c.number_format = per_share_fmt
            ws.cell(
                row=attribution_check_row, column=2 + j, value=attribution_check_f
            )

            assert attribution.reported_net_income_change[j] is not None
            assert attribution.earnings_effect_on_diluted_eps_change[j] is not None
            assert attribution.share_count_effect_on_diluted_eps_change[j] is not None
            assert attribution.diluted_eps_change_from_drivers[j] is not None

            self._register_per_share_attribution(
                "reported_net_income_change",
                j,
                PER_SHARE_SHEET,
                net_income_change_row,
                2 + j,
                net_income_change_f,
                float(attribution.reported_net_income_change[j]),
            )
            self._register_per_share_attribution(
                "earnings_effect_on_diluted_eps_change",
                j,
                PER_SHARE_SHEET,
                earnings_effect_row,
                2 + j,
                earnings_effect_f,
                float(attribution.earnings_effect_on_diluted_eps_change[j]),
            )
            self._register_per_share_attribution(
                "share_count_effect_on_diluted_eps_change",
                j,
                PER_SHARE_SHEET,
                share_count_effect_row,
                2 + j,
                share_count_effect_f,
                float(attribution.share_count_effect_on_diluted_eps_change[j]),
            )
            self._register_per_share_attribution(
                "diluted_eps_change_from_drivers",
                j,
                PER_SHARE_SHEET,
                driver_eps_change_row,
                2 + j,
                driver_eps_change_f,
                float(attribution.diluted_eps_change_from_drivers[j]),
            )

        self.rowmap["per_share_ni_row"] = ni_row
        self.rowmap["per_share_nopat_row"] = nopat_row
        self.rowmap["per_share_shares_row"] = shares_row
        self.rowmap["per_share_eps_row"] = eps_row
        self.rowmap["per_share_nopat_ps_row"] = nopat_ps_row
        self.rowmap["per_share_eps_chg_row"] = eps_chg_row
        self.rowmap["per_share_shares_chg_row"] = shares_chg_row
        self.rowmap["per_share_attribution_net_income_change_row"] = (
            net_income_change_row
        )
        self.rowmap["per_share_attribution_earnings_effect_row"] = earnings_effect_row
        self.rowmap["per_share_attribution_share_count_effect_row"] = (
            share_count_effect_row
        )
        self.rowmap["per_share_attribution_driver_eps_change_row"] = (
            driver_eps_change_row
        )
        self.rowmap["per_share_attribution_check_row"] = attribution_check_row

        if self.normalized_per_share_series is None:
            return

        after_tax_src = self.rowmap["earnings_norm_after_tax_row"]
        normalized_ni_src = self.rowmap["earnings_norm_ni_row"]
        nps = self.normalized_per_share_series

        section_row = 22
        after_tax_adjustment_row = 23
        normalized_ni_row = 24
        adjustment_ps_row = 25
        normalized_eps_row = 26
        level_check_row = 27
        normalized_eps_change_row = 29
        normalization_effect_row = 30
        change_check_row = 31

        ws.cell(
            row=section_row, column=1, value="NORMALIZED DILUTED EPS BRIDGE"
        ).font = BOLD
        ws.cell(
            row=after_tax_adjustment_row,
            column=1,
            value="After-Tax Normalization Adjustment",
        )
        ws.cell(row=normalized_ni_row, column=1, value="Normalized Net Income")
        ws.cell(
            row=adjustment_ps_row,
            column=1,
            value="Normalization Adjustment per Diluted Share",
        )
        ws.cell(row=normalized_eps_row, column=1, value="Normalized Diluted EPS")
        ws.cell(
            row=level_check_row, column=1, value="NORMALIZED EPS LEVEL CHECK"
        ).font = BOLD
        ws.cell(
            row=normalized_eps_change_row,
            column=1,
            value="Change in Normalized Diluted EPS",
        )
        ws.cell(
            row=normalization_effect_row,
            column=1,
            value="Normalization Effect on Change in Diluted EPS",
        )
        ws.cell(
            row=change_check_row, column=1, value="NORMALIZED EPS CHANGE CHECK"
        ).font = BOLD

        for j in range(self._n):
            col = self._col(2 + j)
            norm_col = self._col(3 + j)
            after_tax_link = (
                f"='Earnings Normalization'!{norm_col}{after_tax_src}"
            )
            normalized_ni_link = (
                f"='Earnings Normalization'!{norm_col}{normalized_ni_src}"
            )
            c = ws.cell(
                row=after_tax_adjustment_row, column=2 + j, value=after_tax_link
            )
            c.number_format = NUM_FMT
            c = ws.cell(row=normalized_ni_row, column=2 + j, value=normalized_ni_link)
            c.number_format = NUM_FMT

            adjustment_ps_f = (
                f"=IF({col}{shares_row}<=0,NA(),"
                f"{col}{after_tax_adjustment_row}/{col}{shares_row})"
            )
            normalized_eps_f = (
                f"=IF({col}{shares_row}<=0,NA(),"
                f"{col}{normalized_ni_row}/{col}{shares_row})"
            )
            level_check_f = (
                f'=IF(OR(ISNA({col}{adjustment_ps_row}),ISNA({col}{normalized_eps_row})),'
                f'"N/A",IF(ABS({col}{eps_row}+{col}{adjustment_ps_row}-'
                f'{col}{normalized_eps_row})<0.0000001,"OK","CHECK"))'
            )
            c = ws.cell(row=adjustment_ps_row, column=2 + j, value=adjustment_ps_f)
            c.number_format = per_share_fmt
            c = ws.cell(row=normalized_eps_row, column=2 + j, value=normalized_eps_f)
            c.number_format = per_share_fmt
            ws.cell(row=level_check_row, column=2 + j, value=level_check_f)

            adj_expected = nps.normalization_adjustment_per_diluted_share[j]
            self._register_normalized_per_share(
                "normalization_adjustment_per_diluted_share",
                j,
                PER_SHARE_SHEET,
                adjustment_ps_row,
                2 + j,
                adjustment_ps_f,
                adj_expected
                if isinstance(adj_expected, str)
                else float(adj_expected),
            )
            n_eps_expected = nps.normalized_diluted_eps[j]
            self._register_normalized_per_share(
                "normalized_diluted_eps",
                j,
                PER_SHARE_SHEET,
                normalized_eps_row,
                2 + j,
                normalized_eps_f,
                n_eps_expected
                if isinstance(n_eps_expected, str)
                else float(n_eps_expected),
            )

            if j == 0:
                ws.cell(row=normalized_eps_change_row, column=2 + j, value="N/A")
                ws.cell(row=normalization_effect_row, column=2 + j, value="N/A")
                ws.cell(row=change_check_row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            normalized_eps_change_f = (
                f"={col}{normalized_eps_row}-{prev_col}{normalized_eps_row}"
            )
            normalization_effect_f = (
                f"={col}{adjustment_ps_row}-{prev_col}{adjustment_ps_row}"
            )
            change_check_f = (
                f'=IF(OR(ISNA({col}{normalized_eps_change_row}),'
                f'ISNA({col}{normalization_effect_row})),"N/A",'
                f'IF(ABS({col}{eps_chg_row}+{col}{normalization_effect_row}-'
                f'{col}{normalized_eps_change_row})<0.0000001,"OK","CHECK"))'
            )
            c = ws.cell(
                row=normalized_eps_change_row,
                column=2 + j,
                value=normalized_eps_change_f,
            )
            c.number_format = per_share_fmt
            c = ws.cell(
                row=normalization_effect_row,
                column=2 + j,
                value=normalization_effect_f,
            )
            c.number_format = per_share_fmt
            ws.cell(row=change_check_row, column=2 + j, value=change_check_f)

            n_chg = nps.normalized_diluted_eps_change[j]
            effect = nps.normalization_effect_on_diluted_eps_change[j]
            assert n_chg is not None
            assert effect is not None
            self._register_normalized_per_share(
                "normalized_diluted_eps_change",
                j,
                PER_SHARE_SHEET,
                normalized_eps_change_row,
                2 + j,
                normalized_eps_change_f,
                n_chg if isinstance(n_chg, str) else float(n_chg),
            )
            self._register_normalized_per_share(
                "normalization_effect_on_diluted_eps_change",
                j,
                PER_SHARE_SHEET,
                normalization_effect_row,
                2 + j,
                normalization_effect_f,
                effect if isinstance(effect, str) else float(effect),
            )

        self.rowmap["normalized_per_share_after_tax_row"] = after_tax_adjustment_row
        self.rowmap["normalized_per_share_ni_row"] = normalized_ni_row
        self.rowmap["normalized_per_share_adjustment_ps_row"] = adjustment_ps_row
        self.rowmap["normalized_per_share_eps_row"] = normalized_eps_row
        self.rowmap["normalized_per_share_level_check_row"] = level_check_row
        self.rowmap["normalized_per_share_eps_change_row"] = normalized_eps_change_row
        self.rowmap["normalized_per_share_effect_row"] = normalization_effect_row
        self.rowmap["normalized_per_share_change_check_row"] = change_check_row

    def _build_geographic_segment(self, wb: Workbook) -> None:
        if self.geographic_series is None:
            raise RuntimeError(
                "geographic_series required when building Geographic Segment Analysis"
            )
        if self.fin.historical_segment is None:
            raise RuntimeError("historical_segment required when building geographic schedule")

        series = self.geographic_series
        snapshots = {snap.period: snap for snap in self.fin.historical_segment.periods}
        ws = wb.create_sheet(GEOGRAPHIC_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Geographic Segment Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Source-supported geographic revenue mix, adjacent-period growth, "
            "reported operating margins, and consolidated bridges. Reported "
            "operating margin is distinct from BAV NOPAT margin."
        )
        ws["A3"] = f"Units: {self.fin.units}"
        ws["A4"] = (
            "Calculated segment totals are distinct from any reported segment_total. "
            "Sparse unavailable amounts remain unavailable; opening growth is not "
            "practiced."
        )
        ws.column_dimensions["A"].width = 56

        header_row = 6
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 16

        def _section(row: int, title: str) -> None:
            ws.cell(row=row, column=1, value=title).font = BOLD

        def _label(row: int, text: str) -> None:
            ws.cell(row=row, column=1, value=text)

        def _geo_expected(value: float | str | None) -> float | str:
            assert value is not None
            return value if isinstance(value, str) else float(value)

        def _put_number(row: int, col_idx: int, value: float) -> None:
            cell = ws.cell(row=row, column=col_idx, value=float(value))
            cell.number_format = NUM_FMT

        def _put_formula(row: int, col_idx: int, formula: str, *, pct: bool = False):
            cell = ws.cell(row=row, column=col_idx, value=formula)
            cell.number_format = PCT_FMT if pct else NUM_FMT
            return cell

        def _ratio_formula(num_ref: str, den_ref: str) -> str:
            return f"=IF({den_ref}=0,NA(),{num_ref}/{den_ref})"

        def _growth_formula(curr_ref: str, prev_ref: str) -> str:
            return f"=IF({prev_ref}=0,NA(),({curr_ref}-{prev_ref})/{prev_ref})"

        def _register(
            family_id: str,
            period_index: int,
            identity: str,
            row: int,
            col_idx: int,
            formula: str,
            expected: float | str | None,
        ) -> None:
            self._register_geographic(
                family_id,
                period_index,
                identity,
                GEOGRAPHIC_SHEET,
                row,
                col_idx,
                formula,
                _geo_expected(expected),
            )

        cursor = 8
        _section(cursor, "NET REVENUE")
        family_row = cursor + 1
        rev_rows = {}
        cursor = family_row
        _label(family_row, "Presentation family")
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            cursor += 1
            rev_rows[identity] = cursor
            _label(cursor, f"{geographic_identity_label(identity)} net revenue")
        cursor += 1
        rev_total_row = cursor
        _label(rev_total_row, "Calculated segment revenue total")
        cursor += 1
        rev_reported_total_row = cursor
        _label(rev_reported_total_row, "Reported segment revenue total")
        cursor += 1
        rev_cons_row = cursor
        _label(rev_cons_row, "Reported consolidated revenue")
        cursor += 1
        rev_diff_row = cursor
        _label(rev_diff_row, "Difference vs reported consolidated revenue")

        cursor += 2
        _section(cursor, "REVENUE MIX")
        share_rows = {}
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            cursor += 1
            share_rows[identity] = cursor
            _label(cursor, f"{geographic_identity_label(identity)} revenue mix")

        cursor += 2
        _section(cursor, "ADJACENT-PERIOD REVENUE GROWTH")
        growth_rows = {}
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            cursor += 1
            growth_rows[identity] = cursor
            _label(
                cursor,
                f"{geographic_identity_label(identity)} adjacent-period revenue growth",
            )

        cursor += 2
        _section(cursor, "INCOME FROM OPERATIONS")
        ifop_rows = {}
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            cursor += 1
            ifop_rows[identity] = cursor
            _label(
                cursor,
                f"{geographic_identity_label(identity)} income from operations",
            )
        cursor += 1
        ifop_total_row = cursor
        _label(ifop_total_row, "Calculated segment operating-profit total")
        cursor += 1
        ifop_reported_total_row = cursor
        _label(ifop_reported_total_row, "Reported segment operating-profit total")
        cursor += 1
        ifop_cons_row = cursor
        _label(ifop_cons_row, "Reported consolidated operating profit")

        cursor += 2
        _section(cursor, "REPORTED OPERATING MARGIN")
        margin_rows = {}
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            cursor += 1
            margin_rows[identity] = cursor
            _label(
                cursor,
                f"{geographic_identity_label(identity)} reported operating margin",
            )

        all_bridges = sorted(
            {
                name
                for contrib in series.signed_reconciling_contributions.values()
                if not isinstance(contrib, str)
                for name, _ in contrib
            }
        )
        cursor += 2
        _section(cursor, "RECONCILING ITEMS AND CONSOLIDATED BRIDGE")
        bridge_source_rows: dict[str, int] = {}
        bridge_signed_rows: dict[str, int] = {}
        for identity in all_bridges:
            cursor += 1
            bridge_source_rows[identity] = cursor
            _label(cursor, f"{geographic_identity_label(identity)} (reported)")
            cursor += 1
            bridge_signed_rows[identity] = cursor
            _label(
                cursor,
                f"{geographic_identity_label(identity)} signed contribution",
            )
        cursor += 1
        reconstructed_row = cursor
        _label(reconstructed_row, "Reconstructed consolidated operating profit")
        cursor += 1
        ifop_diff_row = cursor
        _label(
            ifop_diff_row,
            "Difference vs reported consolidated operating profit",
        )

        self.rowmap["geographic_header_row"] = header_row
        self.rowmap["geographic_revenue_rows"] = dict(rev_rows)
        self.rowmap["geographic_ifop_rows"] = dict(ifop_rows)

        for j, period in enumerate(self.periods):
            col_idx = 2 + j
            col = self._col(col_idx)
            snapshot = snapshots.get(period)
            unavailable = snapshot is None or is_source_unavailable(
                series.presentation_family[period]
            )
            if unavailable:
                for row in (
                    family_row,
                    *rev_rows.values(),
                    rev_total_row,
                    rev_reported_total_row,
                    rev_cons_row,
                    rev_diff_row,
                    *share_rows.values(),
                    *growth_rows.values(),
                    *ifop_rows.values(),
                    ifop_total_row,
                    ifop_reported_total_row,
                    ifop_cons_row,
                    *margin_rows.values(),
                    *bridge_source_rows.values(),
                    *bridge_signed_rows.values(),
                    reconstructed_row,
                    ifop_diff_row,
                ):
                    if j == 0 and row in growth_rows.values():
                        ws.cell(row=row, column=col_idx, value="N/A")
                    else:
                        self._stamp_unavailable(
                            ws, row, col_idx, SOURCE_UNAVAILABLE
                        )
                continue

            ws.cell(row=family_row, column=col_idx, value=snapshot.presentation_family)
            for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
                _put_number(
                    rev_rows[identity],
                    col_idx,
                    float(series.net_revenue[period][identity]),
                )
                _put_number(
                    ifop_rows[identity],
                    col_idx,
                    float(series.income_from_operations[period][identity]),
                )

            rev_total_f = "=" + "+".join(
                f"{col}{rev_rows[name]}" for name in GEOGRAPHIC_SEGMENT_IDENTITIES
            )
            _put_formula(rev_total_row, col_idx, rev_total_f)
            _register(
                "geographic_calculated_segment_revenue_total",
                j,
                "",
                rev_total_row,
                col_idx,
                rev_total_f,
                series.calculated_segment_revenue_total[period],
            )
            if REVENUE_SEGMENT_TOTAL in snapshot.values:
                _put_number(
                    rev_reported_total_row,
                    col_idx,
                    float(snapshot.values[REVENUE_SEGMENT_TOTAL]),
                )
            _put_number(
                rev_cons_row,
                col_idx,
                float(series.reported_consolidated_revenue[period]),
            )
            rev_diff_f = f"={col}{rev_total_row}-{col}{rev_cons_row}"
            _put_formula(rev_diff_row, col_idx, rev_diff_f)
            _register(
                "geographic_consolidated_revenue_difference",
                j,
                "",
                rev_diff_row,
                col_idx,
                rev_diff_f,
                series.consolidated_revenue_difference[period],
            )

            for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
                share_f = _ratio_formula(
                    f"{col}{rev_rows[identity]}", f"{col}{rev_cons_row}"
                )
                _put_formula(share_rows[identity], col_idx, share_f, pct=True)
                _register(
                    "geographic_revenue_share",
                    j,
                    identity,
                    share_rows[identity],
                    col_idx,
                    share_f,
                    series.revenue_share[period][identity],
                )
                margin_f = _ratio_formula(
                    f"{col}{ifop_rows[identity]}", f"{col}{rev_rows[identity]}"
                )
                _put_formula(margin_rows[identity], col_idx, margin_f, pct=True)
                _register(
                    "geographic_reported_operating_margin",
                    j,
                    identity,
                    margin_rows[identity],
                    col_idx,
                    margin_f,
                    series.reported_operating_margin[period][identity],
                )

            ifop_total_f = "=" + "+".join(
                f"{col}{ifop_rows[name]}" for name in GEOGRAPHIC_SEGMENT_IDENTITIES
            )
            _put_formula(ifop_total_row, col_idx, ifop_total_f)
            _register(
                "geographic_calculated_segment_operating_profit_total",
                j,
                "",
                ifop_total_row,
                col_idx,
                ifop_total_f,
                series.calculated_segment_operating_profit_total[period],
            )
            if IFOP_SEGMENT_TOTAL in snapshot.values:
                _put_number(
                    ifop_reported_total_row,
                    col_idx,
                    float(snapshot.values[IFOP_SEGMENT_TOTAL]),
                )
            _put_number(
                ifop_cons_row,
                col_idx,
                float(series.reported_consolidated_operating_profit[period]),
            )

            for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
                growth_value = series.revenue_growth[period][identity]
                growth_row = growth_rows[identity]
                if j == 0 or growth_value is None:
                    ws.cell(row=growth_row, column=col_idx, value="N/A")
                    continue
                if is_source_unavailable(growth_value):
                    self._stamp_unavailable(ws, growth_row, col_idx, SOURCE_UNAVAILABLE)
                    continue
                prev_col = self._col(col_idx - 1)
                growth_f = _growth_formula(
                    f"{col}{rev_rows[identity]}",
                    f"{prev_col}{rev_rows[identity]}",
                )
                _put_formula(growth_row, col_idx, growth_f, pct=True)
                _register(
                    "geographic_revenue_growth",
                    j,
                    identity,
                    growth_row,
                    col_idx,
                    growth_f,
                    growth_value,
                )

            signed_refs: list[str] = []
            contributions = series.signed_reconciling_contributions[period]
            present = {
                name: amount
                for name, amount in (
                    contributions if not isinstance(contributions, str) else ()
                )
            }
            for identity in all_bridges:
                source_row = bridge_source_rows[identity]
                signed_row = bridge_signed_rows[identity]
                if identity not in snapshot.bridge_operations:
                    continue
                amount = float(snapshot.values[identity])
                _put_number(source_row, col_idx, amount)
                operation = snapshot.bridge_operations[identity]
                source_ref = f"{col}{source_row}"
                if operation == OP_ADD:
                    signed_f = f"={source_ref}"
                elif operation == OP_SUBTRACT:
                    signed_f = f"=-{source_ref}"
                else:
                    raise ValueError(
                        f"unsupported geographic bridge operation {operation!r}"
                    )
                _put_formula(signed_row, col_idx, signed_f)
                _register(
                    "geographic_signed_reconciling_contribution",
                    j,
                    identity,
                    signed_row,
                    col_idx,
                    signed_f,
                    present[identity],
                )
                signed_refs.append(f"{col}{signed_row}")

            recon_f = f"={col}{ifop_total_row}"
            if signed_refs:
                recon_f += "+" + "+".join(signed_refs)
            _put_formula(reconstructed_row, col_idx, recon_f)
            _register(
                "geographic_reconstructed_consolidated_operating_profit",
                j,
                "",
                reconstructed_row,
                col_idx,
                recon_f,
                series.reconstructed_consolidated_operating_profit[period],
            )
            ifop_diff_f = f"={col}{reconstructed_row}-{col}{ifop_cons_row}"
            _put_formula(ifop_diff_row, col_idx, ifop_diff_f)
            _register(
                "geographic_consolidated_operating_profit_difference",
                j,
                "",
                ifop_diff_row,
                col_idx,
                ifop_diff_f,
                series.consolidated_operating_profit_difference[period],
            )

    def _store_count_source_placement(
        self, period_index: int, default_row: int, default_col: int
    ) -> tuple[int, int]:
        """Return the worksheet row/column for one store-count source cell.

        Default layout keeps sources on the count row at consecutive period
        columns. Tests may override this hook to relocate sources before
        registration and formula resolution.
        """
        return default_row, default_col

    def _revenue_store_source_placement(
        self, period_index: int, default_row: int, default_col: int
    ) -> tuple[int, int]:
        """Return the worksheet row/column for one consolidated-revenue source cell.

        Default layout keeps sources on the revenue row at consecutive period
        columns. Tests may override this hook to relocate sources before
        registration and formula resolution.
        """
        return default_row, default_col

    def _comparable_sales_source_placement(
        self,
        identity: str,
        period_index: int,
        default_row: int,
        default_col: int,
    ) -> tuple[int, int] | tuple[int, int, str]:
        """Return the worksheet placement for one reported comparable-sales source.

        Default layout keeps sources on the identity source row at consecutive
        period columns. Tests may override this hook to relocate sources,
        including nonadjacent columns and another existing sheet, before
        registration and formula resolution.
        """
        return default_row, default_col

    def _normalize_source_placement(
        self,
        placed: tuple[int, int] | tuple[int, int, str],
        default_tab: str,
    ) -> tuple[int, int, str]:
        if len(placed) == 2:
            return placed[0], placed[1], default_tab
        if len(placed) == 3:
            return placed[0], placed[1], placed[2]
        raise ValueError("source placement must be (row, col) or (row, col, tab)")

    def _build_store_count(self, wb: Workbook) -> None:
        if self.operating_kpi_series is None:
            raise RuntimeError(
                "operating_kpi_series required when building Store Count Analysis"
            )
        if self.operating_kpi_relationship is None:
            raise RuntimeError(
                "operating_kpi_relationship required when building Store Count Analysis"
            )

        series = self.operating_kpi_series
        relationship = self.operating_kpi_relationship
        ws = wb.create_sheet(STORE_COUNT_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Store Count Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Source-supported company-operated period-end store counts with "
            "adjacent net count change and count growth. Changes are net "
            "count changes, not openings or closures."
        )
        ws["A3"] = (
            f"Count units are independent of monetary scale ({self.fin.units})."
        )
        ws["A4"] = (
            "Opening change and growth are not practiced. A missing adjacent "
            "snapshot remains unavailable. Count units stay independent of "
            "monetary scale."
        )
        ws["A5"] = relationship.scope_note
        ws.column_dimensions["A"].width = 56
        if relationship.scope_note != SCOPE_NOTE:
            raise RuntimeError("revenue/store scope note drifted from the accepted API")

        header_row = 6
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 16

        def _section(row: int, title: str) -> None:
            ws.cell(row=row, column=1, value=title).font = BOLD

        def _label(row: int, text: str) -> None:
            ws.cell(row=row, column=1, value=text)

        def _store_expected(value: float | str | None) -> float | str:
            assert value is not None
            return value if isinstance(value, str) else float(value)

        def _put_number(
            row: int, col_idx: int, value: float, *, ws=ws
        ) -> None:
            cell = ws.cell(row=row, column=col_idx, value=float(value))
            cell.number_format = NUM_FMT

        def _put_formula(
            row: int,
            col_idx: int,
            formula: str,
            *,
            pct: bool = False,
            points: bool = False,
        ):
            cell = ws.cell(row=row, column=col_idx, value=formula)
            if pct:
                cell.number_format = PCT_FMT
            elif points:
                cell.number_format = "0.00"
            else:
                cell.number_format = NUM_FMT
            return cell

        def _register(
            family_id: str,
            period_index: int,
            row: int,
            col_idx: int,
            formula: str,
            expected: float | str | None,
            *,
            tab: str = STORE_COUNT_SHEET,
        ) -> None:
            self._register_operating_kpi(
                family_id,
                period_index,
                tab,
                row,
                col_idx,
                formula,
                _store_expected(expected),
            )

        def _source_ref(period: date) -> StoreCountSourceRef:
            source_id = store_count_source_component_id(period)
            mapped = self.semantic_map.get(source_id)
            unit = series.unit[period]
            return StoreCountSourceRef(
                id=mapped.id,
                semantic_key=mapped.semantic_key,
                period_end=mapped.period_end,
                cell=mapped.cell,
                unit="" if is_source_unavailable(unit) else str(unit),
                population=STORE_COUNT_POPULATION_LABEL,
            )

        def _mapped_ref(component_id: str) -> SemanticCellRef:
            mapped = self.semantic_map.get(component_id)
            return SemanticCellRef(
                id=mapped.id,
                semantic_key=mapped.semantic_key,
                period_end=mapped.period_end,
                cell=mapped.cell,
                tab=mapped.tab,
            )

        cursor = 8
        _section(cursor, "COMPANY-OPERATED STORE COUNTS")
        cursor += 1
        population_row = cursor
        _label(population_row, "Population")
        cursor += 1
        count_row = cursor
        _label(count_row, "Company-operated period-end store count")
        cursor += 1
        unit_row = cursor
        _label(unit_row, "Count unit")

        cursor += 2
        _section(cursor, "NET COUNT CHANGE")
        cursor += 1
        change_row = cursor
        _label(change_row, "Net count change")

        cursor += 2
        _section(cursor, "STORE-COUNT GROWTH")
        cursor += 1
        growth_row = cursor
        _label(growth_row, "Store-count growth")

        cursor += 2
        _section(cursor, "CONSOLIDATED REVENUE")
        cursor += 1
        revenue_row = cursor
        _label(revenue_row, "Consolidated revenue")

        cursor += 2
        _section(cursor, "CONSOLIDATED REVENUE GROWTH")
        cursor += 1
        revenue_growth_row = cursor
        _label(revenue_growth_row, "Consolidated revenue growth (statement-derived)")

        cursor += 2
        _section(cursor, "REVENUE VS STORE-COUNT GROWTH")
        cursor += 1
        difference_row = cursor
        _label(
            difference_row,
            "Growth difference (analyst-derived, percentage points)",
        )

        self.rowmap["store_count_header_row"] = header_row
        self.rowmap["store_count_count_row"] = count_row
        self.rowmap["store_count_change_row"] = change_row
        self.rowmap["store_count_growth_row"] = growth_row
        self.rowmap["revenue_store_revenue_row"] = revenue_row
        self.rowmap["revenue_store_growth_row"] = revenue_growth_row
        self.rowmap["revenue_store_difference_row"] = difference_row

        for j, period in enumerate(self.periods):
            col_idx = 2 + j
            count = series.period_end_count[period]
            unit = series.unit[period]
            ws.cell(
                row=population_row,
                column=col_idx,
                value=STORE_COUNT_POPULATION_LABEL,
            )
            source_row, source_col = self._store_count_source_placement(
                j, count_row, col_idx
            )
            if is_source_unavailable(count):
                self._stamp_unavailable(ws, source_row, source_col, SOURCE_UNAVAILABLE)
            else:
                _put_number(source_row, source_col, float(count))
                _register(
                    STORE_COUNT_SOURCE_FAMILY_ID,
                    j,
                    source_row,
                    source_col,
                    store_count_source_map_formula(float(count)),
                    float(count),
                )
            if is_source_unavailable(unit):
                self._stamp_unavailable(ws, unit_row, col_idx, SOURCE_UNAVAILABLE)
            else:
                ws.cell(row=unit_row, column=col_idx, value=unit)

        for j, period in enumerate(self.periods):
            col_idx = 2 + j
            revenue = relationship.revenue[period]
            revenue_row_idx, revenue_col, revenue_tab = self._normalize_source_placement(
                self._revenue_store_source_placement(j, revenue_row, col_idx),
                STORE_COUNT_SHEET,
            )
            revenue_ws = ws if revenue_tab == STORE_COUNT_SHEET else wb[revenue_tab]
            if is_source_unavailable(revenue):
                self._stamp_unavailable(
                    revenue_ws, revenue_row_idx, revenue_col, SOURCE_UNAVAILABLE
                )
            else:
                _put_number(revenue_row_idx, revenue_col, float(revenue), ws=revenue_ws)
                _register(
                    REVENUE_STORE_SOURCE_FAMILY_ID,
                    j,
                    revenue_row_idx,
                    revenue_col,
                    store_count_source_map_formula(float(revenue)),
                    float(revenue),
                    tab=revenue_tab,
                )

        for j, period in enumerate(self.periods):
            col_idx = 2 + j
            change = series.net_count_change[period]
            growth = series.growth[period]
            if j == 0 or change is None:
                ws.cell(row=change_row, column=col_idx, value="N/A")
            elif is_source_unavailable(change):
                self._stamp_unavailable(ws, change_row, col_idx, SOURCE_UNAVAILABLE)
            else:
                current = _source_ref(period)
                prior = _source_ref(self.periods[j - 1])
                change_f = resolve_store_count_net_change_formula(current, prior)
                _put_formula(change_row, col_idx, change_f)
                _register(
                    "store_count_net_change",
                    j,
                    change_row,
                    col_idx,
                    change_f,
                    change,
                )

            if j == 0 or growth is None:
                ws.cell(row=growth_row, column=col_idx, value="N/A")
            elif is_source_unavailable(growth):
                self._stamp_unavailable(ws, growth_row, col_idx, SOURCE_UNAVAILABLE)
            else:
                current = _source_ref(period)
                prior = _source_ref(self.periods[j - 1])
                growth_f = resolve_store_count_growth_formula(current, prior)
                _put_formula(growth_row, col_idx, growth_f, pct=True)
                _register(
                    "store_count_growth",
                    j,
                    growth_row,
                    col_idx,
                    growth_f,
                    growth,
                )

        for j, period in enumerate(self.periods):
            col_idx = 2 + j
            revenue_growth = relationship.revenue_growth[period]
            difference = relationship.growth_difference_pp[period]
            if j == 0 or revenue_growth is None:
                ws.cell(row=revenue_growth_row, column=col_idx, value="N/A")
            elif is_source_unavailable(revenue_growth):
                self._stamp_unavailable(
                    ws, revenue_growth_row, col_idx, SOURCE_UNAVAILABLE
                )
            else:
                current = _mapped_ref(revenue_store_source_component_id(period))
                prior = _mapped_ref(
                    revenue_store_source_component_id(self.periods[j - 1])
                )
                growth_f = resolve_revenue_store_growth_formula(
                    current, prior, from_tab=STORE_COUNT_SHEET
                )
                _put_formula(revenue_growth_row, col_idx, growth_f, pct=True)
                _register(
                    REVENUE_STORE_GROWTH_FAMILY_ID,
                    j,
                    revenue_growth_row,
                    col_idx,
                    growth_f,
                    revenue_growth,
                )

            if j == 0 or difference is None:
                ws.cell(row=difference_row, column=col_idx, value="N/A")
            elif is_source_unavailable(difference):
                self._stamp_unavailable(
                    ws, difference_row, col_idx, SOURCE_UNAVAILABLE
                )
            else:
                revenue_growth_ref = _mapped_ref(
                    revenue_store_component_id(
                        REVENUE_STORE_GROWTH_FAMILY_ID, period
                    )
                )
                store_growth_ref = _mapped_ref(
                    store_count_component_id("store_count_growth", period)
                )
                difference_f = resolve_revenue_store_difference_formula(
                    revenue_growth_ref,
                    store_growth_ref,
                    from_tab=STORE_COUNT_SHEET,
                )
                _put_formula(difference_row, col_idx, difference_f, points=True)
                _register(
                    REVENUE_STORE_DIFFERENCE_FAMILY_ID,
                    j,
                    difference_row,
                    col_idx,
                    difference_f,
                    difference,
                )

    def _build_comparable_sales(self, wb: Workbook) -> None:
        if self.operating_kpi_compsales_relationship is None:
            raise RuntimeError(
                "operating_kpi_compsales_relationship required when building "
                "Comparable Sales Analysis"
            )
        relationship = self.operating_kpi_compsales_relationship
        if relationship.scope_note != COMPARABLE_SALES_SCOPE_NOTE:
            raise RuntimeError(
                "revenue/comparable-sales scope note drifted from the accepted API"
            )
        ws = wb.create_sheet(COMPARABLE_SALES_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Comparable Sales Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Source-supported reported global comparable-sales percentages "
            "compared with statement-derived consolidated revenue growth. "
            "Full management identities stay isolated."
        )
        ws["A3"] = (
            f"Currency {relationship.currency}; monetary scale "
            f"{relationship.monetary_scale}. Reported comparable-sales remain "
            "in percent units (2 means 2%)."
        )
        ws["A4"] = (
            "Opening difference is not practiced. A missing current "
            "comparable-sales or revenue input remains unavailable. A missing "
            "prior comparable-sales observation does not suppress a current "
            "comparison."
        )
        ws["A5"] = relationship.scope_note
        ws.column_dimensions["A"].width = 64

        header_row = 6
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 16

        def _section(row: int, title: str) -> None:
            ws.cell(row=row, column=1, value=title).font = BOLD

        def _label(row: int, text: str) -> None:
            ws.cell(row=row, column=1, value=text)

        def _expected(value: float | str | None) -> float | str:
            assert value is not None
            return value if isinstance(value, str) else float(value)

        def _target_sheet(tab: str):
            if tab == COMPARABLE_SALES_SHEET:
                return ws
            if tab not in wb.sheetnames:
                raise RuntimeError(
                    f"comparable-sales source tab {tab!r} does not exist"
                )
            return wb[tab]

        def _put_number(
            row: int,
            col_idx: int,
            value: float,
            *,
            tab: str = COMPARABLE_SALES_SHEET,
            percent: bool = False,
        ) -> None:
            cell = _target_sheet(tab).cell(row=row, column=col_idx, value=float(value))
            cell.number_format = COMPARABLE_SALES_PCT_FORMAT if percent else NUM_FMT

        def _put_formula(
            row: int,
            col_idx: int,
            formula: str,
            *,
            pct: bool = False,
            points: bool = False,
        ):
            cell = ws.cell(row=row, column=col_idx, value=formula)
            if pct:
                cell.number_format = PCT_FMT
            elif points:
                cell.number_format = "0.00"
            else:
                cell.number_format = NUM_FMT
            return cell

        def _register(
            family_id: str,
            period_index: int,
            row: int,
            col_idx: int,
            formula: str,
            expected: float | str | None,
            *,
            tab: str = COMPARABLE_SALES_SHEET,
            identity: str = "",
        ) -> None:
            self._register_operating_kpi(
                family_id,
                period_index,
                tab,
                row,
                col_idx,
                formula,
                _expected(expected),
                identity=identity,
            )

        def _mapped_ref(component_id: str) -> SemanticCellRef:
            mapped = self.semantic_map.get(component_id)
            return SemanticCellRef(
                id=mapped.id,
                semantic_key=mapped.semantic_key,
                period_end=mapped.period_end,
                cell=mapped.cell,
                tab=mapped.tab,
            )

        def _format_qualifiers(value: dict[str, str] | str) -> str:
            if is_source_unavailable(value):
                return SOURCE_UNAVAILABLE
            assert isinstance(value, dict)
            return json.dumps(value, sort_keys=True, separators=(",", ":"))

        first = relationship.series[relationship.identities[0]]
        place_shared_revenue = self.operating_kpi_relationship is None

        cursor = 8
        revenue_row = None
        revenue_growth_row = None
        if place_shared_revenue:
            _section(cursor, "CONSOLIDATED REVENUE")
            cursor += 1
            revenue_row = cursor
            _label(revenue_row, "Consolidated revenue (reported source)")
            cursor += 2
            _section(cursor, "CONSOLIDATED REVENUE GROWTH")
            cursor += 1
            revenue_growth_row = cursor
            _label(
                revenue_growth_row,
                "Consolidated revenue growth (statement-derived)",
            )
            cursor += 2

        identity_layout: dict[str, dict[str, int]] = {}
        for identity in relationship.identities:
            series = relationship.series[identity]
            _section(
                cursor,
                "COMPARABLE SALES — "
                + comparable_sales_identity_label(
                    entity_ticker=series.entity_ticker,
                    entity_company=series.entity_company,
                    geography=series.geography,
                    population=series.population,
                    unit=series.unit,
                    basis=series.basis,
                    comparison=series.comparison,
                ),
            )
            cursor += 1
            rows = {
                "family": cursor,
                "entity_ticker": cursor + 1,
                "entity_company": cursor + 2,
                "geography": cursor + 3,
                "population": cursor + 4,
                "unit": cursor + 5,
                "basis": cursor + 6,
                "comparison": cursor + 7,
                "definition": cursor + 8,
                "period_kind": cursor + 9,
                "calendar_week": cursor + 10,
                "calendar_basis": cursor + 11,
                "qualifiers": cursor + 12,
                "source": cursor + 13,
                "difference": cursor + 14,
            }
            _label(rows["family"], "Family (reported)")
            _label(rows["entity_ticker"], "Entity ticker")
            _label(rows["entity_company"], "Entity company")
            _label(rows["geography"], "Geography")
            _label(rows["population"], "Population")
            _label(rows["unit"], "Unit")
            _label(rows["basis"], "Reporting basis")
            _label(rows["comparison"], "Comparison")
            _label(rows["definition"], "Definition")
            _label(rows["period_kind"], "Period kind")
            _label(rows["calendar_week"], "Calendar week adjustment")
            _label(rows["calendar_basis"], "Calendar reporting basis")
            _label(rows["qualifiers"], "Qualifiers")
            _label(
                rows["source"],
                "Reported comparable-sales growth (percent; 2 means 2%)",
            )
            _label(
                rows["difference"],
                "Growth difference (analyst-derived, percentage points)",
            )
            identity_layout[identity] = rows
            cursor = rows["difference"] + 2

        self.rowmap["comparable_sales_header_row"] = header_row
        if revenue_row is not None:
            self.rowmap["comparable_sales_revenue_row"] = revenue_row
        if revenue_growth_row is not None:
            self.rowmap["comparable_sales_growth_row"] = revenue_growth_row
        self.rowmap["comparable_sales_identity_rows"] = {
            identity: dict(rows) for identity, rows in identity_layout.items()
        }

        if place_shared_revenue:
            assert revenue_row is not None and revenue_growth_row is not None
            for j, period in enumerate(self.periods):
                col_idx = 2 + j
                revenue = first.revenue[period]
                revenue_row_idx, revenue_col, revenue_tab = (
                    self._normalize_source_placement(
                        self._revenue_store_source_placement(j, revenue_row, col_idx),
                        COMPARABLE_SALES_SHEET,
                    )
                )
                if is_source_unavailable(revenue):
                    self._stamp_unavailable(
                        _target_sheet(revenue_tab),
                        revenue_row_idx,
                        revenue_col,
                        SOURCE_UNAVAILABLE,
                    )
                else:
                    _put_number(
                        revenue_row_idx,
                        revenue_col,
                        float(revenue),
                        tab=revenue_tab,
                    )
                    _register(
                        REVENUE_STORE_SOURCE_FAMILY_ID,
                        j,
                        revenue_row_idx,
                        revenue_col,
                        store_count_source_map_formula(float(revenue)),
                        float(revenue),
                        tab=revenue_tab,
                    )

            for j, period in enumerate(self.periods):
                col_idx = 2 + j
                revenue_growth = first.revenue_growth[period]
                if j == 0 or revenue_growth is None:
                    ws.cell(row=revenue_growth_row, column=col_idx, value="N/A")
                elif is_source_unavailable(revenue_growth):
                    self._stamp_unavailable(
                        ws, revenue_growth_row, col_idx, SOURCE_UNAVAILABLE
                    )
                else:
                    current = _mapped_ref(revenue_store_source_component_id(period))
                    prior = _mapped_ref(
                        revenue_store_source_component_id(self.periods[j - 1])
                    )
                    growth_f = resolve_revenue_store_growth_formula(
                        current, prior, from_tab=COMPARABLE_SALES_SHEET
                    )
                    _put_formula(revenue_growth_row, col_idx, growth_f, pct=True)
                    _register(
                        REVENUE_STORE_GROWTH_FAMILY_ID,
                        j,
                        revenue_growth_row,
                        col_idx,
                        growth_f,
                        revenue_growth,
                    )

        for identity in relationship.identities:
            series = relationship.series[identity]
            rows = identity_layout[identity]
            token = comparable_sales_identity_token(identity)
            for j, period in enumerate(self.periods):
                col_idx = 2 + j
                compsales = series.comparable_sales_growth[period]
                source_row, source_col, source_tab = self._normalize_source_placement(
                    self._comparable_sales_source_placement(
                        identity,
                        j,
                        rows["source"],
                        col_idx,
                    ),
                    COMPARABLE_SALES_SHEET,
                )
                if is_source_unavailable(compsales):
                    for key in (
                        "family",
                        "entity_ticker",
                        "entity_company",
                        "geography",
                        "population",
                        "unit",
                        "basis",
                        "comparison",
                        "definition",
                        "period_kind",
                        "calendar_week",
                        "calendar_basis",
                        "qualifiers",
                    ):
                        self._stamp_unavailable(
                            ws, rows[key], col_idx, SOURCE_UNAVAILABLE
                        )
                    self._stamp_unavailable(
                        _target_sheet(source_tab),
                        source_row,
                        source_col,
                        SOURCE_UNAVAILABLE,
                    )
                else:
                    ws.cell(row=rows["family"], column=col_idx, value=series.family)
                    ws.cell(
                        row=rows["entity_ticker"],
                        column=col_idx,
                        value=series.entity_ticker,
                    )
                    ws.cell(
                        row=rows["entity_company"],
                        column=col_idx,
                        value=series.entity_company,
                    )
                    ws.cell(row=rows["geography"], column=col_idx, value=series.geography)
                    ws.cell(
                        row=rows["population"], column=col_idx, value=series.population
                    )
                    ws.cell(row=rows["unit"], column=col_idx, value=series.unit)
                    ws.cell(row=rows["basis"], column=col_idx, value=series.basis)
                    ws.cell(
                        row=rows["comparison"], column=col_idx, value=series.comparison
                    )
                    ws.cell(
                        row=rows["definition"],
                        column=col_idx,
                        value=series.definition_text[period],
                    )
                    ws.cell(
                        row=rows["period_kind"],
                        column=col_idx,
                        value=series.period_kind[period],
                    )
                    ws.cell(
                        row=rows["calendar_week"],
                        column=col_idx,
                        value=series.calendar_week_adjustment[period],
                    )
                    ws.cell(
                        row=rows["calendar_basis"],
                        column=col_idx,
                        value=series.calendar_reporting_basis[period],
                    )
                    ws.cell(
                        row=rows["qualifiers"],
                        column=col_idx,
                        value=_format_qualifiers(series.qualifiers[period]),
                    )
                    _put_number(
                        source_row,
                        source_col,
                        float(compsales),
                        tab=source_tab,
                        percent=True,
                    )
                    _register(
                        COMPARABLE_SALES_SOURCE_FAMILY_ID,
                        j,
                        source_row,
                        source_col,
                        store_count_source_map_formula(float(compsales)),
                        float(compsales),
                        tab=source_tab,
                        identity=token,
                    )

                difference = series.growth_difference_pp[period]
                if j == 0 or difference is None:
                    ws.cell(row=rows["difference"], column=col_idx, value="N/A")
                elif is_source_unavailable(difference):
                    self._stamp_unavailable(
                        ws, rows["difference"], col_idx, SOURCE_UNAVAILABLE
                    )
                else:
                    revenue_growth_ref = _mapped_ref(
                        revenue_store_component_id(
                            REVENUE_STORE_GROWTH_FAMILY_ID, period
                        )
                    )
                    compsales_ref = _mapped_ref(
                        comparable_sales_source_component_id(period, identity)
                    )
                    difference_f = resolve_revenue_comparable_sales_difference_formula(
                        revenue_growth_ref,
                        compsales_ref,
                        from_tab=COMPARABLE_SALES_SHEET,
                    )
                    _put_formula(
                        rows["difference"], col_idx, difference_f, points=True
                    )
                    _register(
                        COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
                        j,
                        rows["difference"],
                        col_idx,
                        difference_f,
                        difference,
                        identity=token,
                    )

    def _build_model_tab(self, wb: Workbook, scenario: str) -> None:
        ws = wb.create_sheet(f"Model_{scenario}")
        sc = self.assumptions["scenarios"][scenario]
        result = self._scenario_results[scenario]
        ws["A1"] = f"{self.fin.company_name} — {scenario} Scenario"
        ws.freeze_panes = "B1"
        ws.column_dimensions["A"].width = 42

        ws["A5"] = "Cost of Equity (Ke)"
        ws["B5"] = sc["costOfEquity"]
        ws["B5"].font = BLUE
        ws["B5"].number_format = PCT_FMT
        ws["A6"] = "Tax rate"
        ws["B6"] = sc.get("taxRate", 0.165)
        ws["B6"].number_format = PCT_FMT
        # Historical average is already after-tax — use directly; do not tax again.
        ws["A7"] = "After-tax CoD"
        ws["B7"] = self.anchor.hist_avg_after_tax_cod
        ws["B7"].number_format = PCT_FMT
        ws["A8"] = "Financial leverage"
        ws["B8"] = self.anchor.leverage
        ws["B8"].number_format = PCT_FMT
        ws["A9"] = "Terminal growth (g)"
        ws["B9"] = sc["terminalGrowth"]
        ws["B9"].font = BLUE
        ws["B9"].number_format = PCT_FMT

        fc = self._first_fc_col
        anchor_col = self._col(self._last_fy_col)
        rev_row = self._resolved_source_row(
            self.fin.income_statement, "revenue", required=True
        )
        nowc_hist = self.rowmap["condensed_nowc_row"]
        noa_hist = self.rowmap["condensed_noa_row"]
        nd_hist = self.rowmap["condensed_nd_row"]
        # NOLA_hist = NOA - NOWC for Y1 bridge
        nola_hist_formula = (
            f"='Condensed Financials'!{anchor_col}{noa_hist}"
            f"-'Condensed Financials'!{anchor_col}{nowc_hist}"
        )

        sales_row, margin_row = 21, 22
        nowc_row, nola_row, nd_row, eq_row = 23, 24, 25, 26
        nopat_row, ni_row, ae_row = 27, 28, 29
        disc_row, pv_ae_row = 30, 31
        sum_pv_ae_row, tv_row, tv_pv_row = 35, 36, 37
        iv_row, shares_row, ivps_row = 38, 39, 40

        ws.cell(row=20, column=1, value="FORECAST BLOCK").font = BOLD
        for t in range(10):
            ws.cell(row=20, column=fc + t, value=f"Y{t + 1}").font = BOLD
            ws.column_dimensions[self._col(fc + t)].width = 14

        labels = {
            sales_row: "Sales",
            margin_row: "NOPAT Margin",
            nowc_row: "NOWC",
            nola_row: "NOLA",
            nd_row: "Net Debt",
            eq_row: "Book Equity",
            nopat_row: "NOPAT",
            ni_row: "Net Income",
            ae_row: "Abnormal Earnings",
            disc_row: "Discount Factor",
            pv_ae_row: "PV Abnormal Earnings",
        }
        for row, label in labels.items():
            ws.cell(row=row, column=1, value=label)

        ws.cell(row=sum_pv_ae_row, column=1, value="Sum PV Abnormal Earnings")
        ws.cell(row=tv_row, column=1, value="Terminal Value")
        ws.cell(row=tv_pv_row, column=1, value="PV Terminal Value")
        ws.cell(row=iv_row, column=1, value="Intrinsic Value")
        ws.cell(row=shares_row, column=1, value="Diluted Shares")
        ws.cell(row=ivps_row, column=1, value="Intrinsic Value per Share")

        for t in range(10):
            col_i = fc + t
            col = self._col(col_i)
            prev = self._col(col_i - 1) if t > 0 else None
            g = sc["growthVector"][t]
            m = sc["marginVector"][t]
            nowc_ratio = sc["nowcRatioVector"][t]
            nola_ratio = sc["nolaRatioVector"][t]

            if t == 0:
                sales_f = f"='Income Statement'!{anchor_col}{rev_row}*(1+{g})"
            else:
                sales_f = f"={prev}{sales_row}*(1+{g})"
            ws.cell(row=sales_row, column=col_i, value=sales_f).number_format = NUM_FMT

            mc = ws.cell(row=margin_row, column=col_i, value=m)
            mc.font = BLUE
            mc.number_format = PCT_FMT

            if t == 0:
                ws.cell(
                    row=nowc_row,
                    column=col_i,
                    value=f"='Condensed Financials'!{anchor_col}{nowc_hist}",
                ).number_format = NUM_FMT
                ws.cell(row=nola_row, column=col_i, value=nola_hist_formula).number_format = NUM_FMT
                ws.cell(
                    row=nd_row,
                    column=col_i,
                    value=f"='Condensed Financials'!{anchor_col}{nd_hist}",
                ).number_format = NUM_FMT
            else:
                ws.cell(
                    row=nowc_row,
                    column=col_i,
                    value=f"={col}{sales_row}*{nowc_ratio}",
                ).number_format = NUM_FMT
                ws.cell(
                    row=nola_row,
                    column=col_i,
                    value=f"={col}{sales_row}*{nola_ratio}",
                ).number_format = NUM_FMT
                ws.cell(
                    row=nd_row,
                    column=col_i,
                    value=f"=($B$8)*({col}{nowc_row}+{col}{nola_row})",
                ).number_format = NUM_FMT

            ws.cell(
                row=eq_row,
                column=col_i,
                value=f"={col}{nowc_row}+{col}{nola_row}-{col}{nd_row}",
            ).number_format = NUM_FMT
            ws.cell(
                row=nopat_row,
                column=col_i,
                value=f"={col}{sales_row}*{col}{margin_row}",
            ).number_format = NUM_FMT
            if scenario == "Base" and t == 0:
                ws.cell(row=nopat_row, column=col_i).fill = GREEN

            # After-tax CoD in B7 already after-tax — apply once.
            ws.cell(
                row=ni_row,
                column=col_i,
                value=f"={col}{nopat_row}-{col}{nd_row}*$B$7",
            ).number_format = NUM_FMT
            ws.cell(
                row=ae_row,
                column=col_i,
                value=f"={col}{ni_row}-$B$5*{col}{eq_row}",
            ).number_format = NUM_FMT
            if scenario == "Base" and t == 0:
                ws.cell(row=ae_row, column=col_i).fill = GREEN

            ws.cell(
                row=disc_row,
                column=col_i,
                value=f"=1/(1+$B$5)^{t + 1}",
            ).number_format = "0.0000"
            ws.cell(
                row=pv_ae_row,
                column=col_i,
                value=f"={col}{ae_row}*{col}{disc_row}",
            ).number_format = NUM_FMT

        last_fc = self._col(fc + 9)
        first_fc = self._col(fc)
        sum_pv = f"=SUM({first_fc}{pv_ae_row}:{last_fc}{pv_ae_row})"
        ws.cell(row=sum_pv_ae_row, column=fc, value=sum_pv).number_format = NUM_FMT

        tv_formula = f"={last_fc}{ae_row}*(1+$B$9)/($B$5-$B$9)"
        ws.cell(row=tv_row, column=fc + 9, value=tv_formula).number_format = NUM_FMT

        tv_pv_formula = f"={last_fc}{tv_row}*{last_fc}{disc_row}"
        ws.cell(row=tv_pv_row, column=fc, value=tv_pv_formula).number_format = NUM_FMT

        iv_formula = f"={first_fc}{eq_row}+{first_fc}{sum_pv_ae_row}+{first_fc}{tv_pv_row}"
        ws.cell(row=iv_row, column=fc, value=iv_formula).number_format = NUM_FMT

        shares_cell = ws.cell(
            row=shares_row,
            column=fc,
            value=self.assumptions["marketData"]["dilutedShares"],
        )
        shares_cell.font = BLUE
        shares_cell.number_format = NUM_FMT

        ivps_formula = f"={first_fc}{iv_row}/{first_fc}{shares_row}"
        ivps_cell = ws.cell(row=ivps_row, column=fc, value=ivps_formula)
        ivps_cell.number_format = "0.0000"
        if scenario == "Base":
            ivps_cell.fill = GREEN

        self.rowmap[f"model_{scenario}_ivps_row"] = ivps_row
        self.rowmap[f"model_{scenario}_fc_col"] = fc
        self.rowmap[f"model_{scenario}_ae_row"] = ae_row
        self.rowmap[f"model_{scenario}_disc_row"] = disc_row
        self.rowmap[f"model_{scenario}_tv_row"] = tv_row
        self.rowmap[f"model_{scenario}_sales_row"] = sales_row

        if scenario == "Base":
            sales_y1 = str(ws.cell(row=sales_row, column=fc).value)
            nopat_y1 = str(ws.cell(row=nopat_row, column=fc).value)
            ae_y1 = str(ws.cell(row=ae_row, column=fc).value)
            self._register_deferred(
                "model_sales_y1",
                f"Model_{scenario}",
                sales_row,
                fc,
                sales_y1,
                result.sales_y1,
            )
            self._register_deferred(
                "model_nopat_y1",
                f"Model_{scenario}",
                nopat_row,
                fc,
                nopat_y1,
                result.nopat_y1,
            )
            self._register_deferred(
                "model_ae_y1",
                f"Model_{scenario}",
                ae_row,
                fc,
                ae_y1,
                result.abnormal_earnings_y1,
            )
            self._register_deferred(
                "model_tv",
                f"Model_{scenario}",
                tv_pv_row,
                fc,
                tv_pv_formula,
                result.terminal_value_pv,
            )
            self._register_deferred(
                "model_ivps",
                f"Model_{scenario}",
                ivps_row,
                fc,
                ivps_formula,
                result.ivps,
            )

    def _build_scenario_summary(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Scenario_Summary")
        ws["A1"] = f"{self.fin.company_name} — Scenario Summary"
        for j, h in enumerate(["Scenario", "Probability", "IVPS"], start=1):
            ws.cell(row=3, column=j, value=h).font = BOLD
        for i, name in enumerate(("Bear", "Base", "Bull"), start=4):
            sc = self.assumptions["scenarios"][name]
            ivps_row = self.rowmap[f"model_{name}_ivps_row"]
            fc = self.rowmap[f"model_{name}_fc_col"]
            ws.cell(row=i, column=1, value=name)
            ws.cell(row=i, column=2, value=sc["probability"])
            ws.cell(row=i, column=2).font = BLUE
            ws.cell(row=i, column=2).number_format = PCT_FMT
            ws.cell(row=i, column=3, value=f"='Model_{name}'!{self._col(fc)}{ivps_row}")
        weighted_row = 8
        weighted_col = 5
        weighted_formula = "=SUMPRODUCT(B4:B6,C4:C6)"
        ws.cell(row=weighted_row, column=1, value="Weighted IVPS")
        ws.cell(row=weighted_row, column=weighted_col, value=weighted_formula)
        ws.cell(row=weighted_row, column=weighted_col).fill = GREEN
        w_ivps = weighted_ivps(self._scenario_results, self.assumptions["scenarios"])
        self._register_deferred(
            "scenario_weighted",
            "Scenario_Summary",
            weighted_row,
            weighted_col,
            weighted_formula,
            w_ivps,
        )
