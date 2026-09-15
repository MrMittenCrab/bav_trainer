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
    expand_acquisition_cash_specs,
    expand_capex_specs,
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
        self.historical_specs = expand_historical_specs(self.periods)
        overrides = self.assumptions.get("classificationOverrides") or {}
        self.anchor = compute_anchor(
            financials,
            self.periods,
            classification_overrides=overrides,
        )
        self.interest_availability = assess_interest_availability(
            financials, self.periods
        )
        self.rowmap["interest_availability"] = availability_payload(
            self.interest_availability
        )
        from ..model.historical_expected import (
            historical_expected_series,
            per_share_expected_series,
            profitability_change_expected_series,
            profitability_driver_expected_series,
            roe_attribution_expected_series,
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
        self.normalization_cases: tuple[NormalizationCase, ...] = normalization_cases(
            self.fin,
            self.periods,
            self.assumptions,
        )
        self.normalization_specs = (
            expand_normalization_specs(
                self.periods,
                start_order=len(self.historical_specs) + 1,
            )
            if self.normalization_cases
            else ()
        )
        if self.normalization_specs:
            self.normalization_specs = filter_available_specs(
                self.normalization_specs,
                {"normalized_nopat": tuple(self.anchor.historical.nopat)},
            )
        self.quality_availability = earnings_quality_availability(self.fin)
        if self.quality_availability.operating_cash_flow:
            self.quality_series = compute_earnings_quality_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.quality_specs = expand_quality_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs) + len(self.normalization_specs) + 1
                ),
                include_asset_scaled=self.quality_availability.total_assets,
                include_sbc=(
                    self.quality_series.operating_cash_flow_less_sbc is not None
                ),
            )
        else:
            self.quality_series = None
            self.quality_specs = ()
        if working_capital_applicable(self.anchor):
            self.working_capital_series = compute_working_capital_series(self.anchor)
            self.working_capital_specs = expand_working_capital_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + 1
                ),
            )
        else:
            self.working_capital_series = None
            self.working_capital_specs = ()
        self.profitability_driver_series = compute_profitability_driver_series(self.anchor)
        self.profitability_driver_specs = filter_available_specs(
            expand_profitability_driver_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + 1
                ),
            ),
            profitability_driver_expected_series(self.anchor),
        )
        self.profitability_change_series = compute_profitability_change_series(self.anchor)
        self.profitability_change_specs = filter_available_specs(
            expand_profitability_change_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + 1
                ),
            ),
            profitability_change_expected_series(self.anchor),
        )
        self.roe_attribution_series = compute_roe_attribution_series(self.anchor)
        self.roe_attribution_specs = filter_available_specs(
            expand_roe_attribution_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + 1
                ),
            ),
            roe_attribution_expected_series(self.anchor),
        )
        if self.quality_series is not None:
            self.quality_change_series = compute_earnings_quality_change_series(
                self.quality_series
            )
            self.quality_change_specs = expand_quality_change_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + 1
                ),
                include_asset_scaled=self.quality_availability.total_assets,
            )
        else:
            self.quality_change_series = None
            self.quality_change_specs = ()
        if per_share_available(self.fin):
            self.per_share_series = compute_per_share_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.per_share_specs = filter_available_specs(
                expand_per_share_specs(
                    self.periods,
                    start_order=(
                        len(self.historical_specs)
                        + len(self.normalization_specs)
                        + len(self.quality_specs)
                        + len(self.working_capital_specs)
                        + len(self.profitability_driver_specs)
                        + len(self.profitability_change_specs)
                        + len(self.roe_attribution_specs)
                        + len(self.quality_change_specs)
                        + 1
                    ),
                ),
                per_share_expected_series(self.per_share_series),
            )
            self.per_share_attribution_series = compute_per_share_attribution_series(
                self.anchor,
                self.per_share_series,
            )
            self.per_share_attribution_specs = expand_per_share_attribution_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + 1
                ),
            )
        else:
            self.per_share_series = None
            self.per_share_specs = ()
            self.per_share_attribution_series = None
            self.per_share_attribution_specs = ()
        if self.per_share_series is not None and self.normalization_cases:
            self.normalized_per_share_specs = expand_normalized_per_share_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + 1
                ),
            )
        else:
            self.normalized_per_share_specs = ()
        if fixed_asset_applicable(self.fin):
            self.fixed_asset_series = compute_fixed_asset_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.fixed_asset_specs = expand_fixed_asset_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + 1
                ),
            )
        else:
            self.fixed_asset_series = None
            self.fixed_asset_specs = ()
        if lease_liability_applicable(self.fin):
            self.lease_liability_series = compute_lease_liability_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_liability_specs = expand_lease_liability_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + 1
                ),
            )
        else:
            self.lease_liability_series = None
            self.lease_liability_specs = ()
        if ownership_attribution_applicable(self.fin):
            self.ownership_attribution_series = compute_ownership_attribution_series(
                self.fin,
                self.periods,
            )
            self.ownership_attribution_specs = expand_ownership_attribution_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + 1
                ),
            )
        else:
            self.ownership_attribution_series = None
            self.ownership_attribution_specs = ()
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
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + 1
                ),
                availability=self.goodwill_intangibles_availability,
            )
        else:
            self.goodwill_intangibles_series = None
            self.goodwill_intangibles_specs = ()
        if lease_rou_applicable(self.fin):
            self.lease_rou_series = compute_lease_rou_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_rou_specs = expand_lease_rou_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + len(self.goodwill_intangibles_specs)
                    + 1
                ),
            )
        else:
            self.lease_rou_series = None
            self.lease_rou_specs = ()
        if deferred_tax_applicable(self.fin):
            self.deferred_tax_series = compute_deferred_tax_series(
                self.fin,
                self.periods,
            )
            self.deferred_tax_specs = expand_deferred_tax_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + len(self.goodwill_intangibles_specs)
                    + len(self.lease_rou_specs)
                    + 1
                ),
            )
        else:
            self.deferred_tax_series = None
            self.deferred_tax_specs = ()
        if capex_applicable(self.fin):
            self.capex_series = compute_capex_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.capex_specs = expand_capex_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + len(self.goodwill_intangibles_specs)
                    + len(self.lease_rou_specs)
                    + len(self.deferred_tax_specs)
                    + 1
                ),
                include_operating_cash=(
                    self.capex_series.cash_after_ppe_capex is not None
                ),
            )
        else:
            self.capex_series = None
            self.capex_specs = ()
        if lease_repayment_applicable(self.fin):
            self.lease_repayment_series = compute_lease_repayment_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.lease_repayment_specs = expand_lease_repayment_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + len(self.goodwill_intangibles_specs)
                    + len(self.lease_rou_specs)
                    + len(self.deferred_tax_specs)
                    + len(self.capex_specs)
                    + 1
                ),
            )
        else:
            self.lease_repayment_series = None
            self.lease_repayment_specs = ()
        if acquisition_cash_applicable(self.fin):
            self.acquisition_cash_series = compute_acquisition_cash_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.acquisition_cash_specs = expand_acquisition_cash_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + len(self.working_capital_specs)
                    + len(self.profitability_driver_specs)
                    + len(self.profitability_change_specs)
                    + len(self.roe_attribution_specs)
                    + len(self.quality_change_specs)
                    + len(self.per_share_specs)
                    + len(self.per_share_attribution_specs)
                    + len(self.normalized_per_share_specs)
                    + len(self.fixed_asset_specs)
                    + len(self.lease_liability_specs)
                    + len(self.ownership_attribution_specs)
                    + len(self.goodwill_intangibles_specs)
                    + len(self.lease_rou_specs)
                    + len(self.deferred_tax_specs)
                    + len(self.capex_specs)
                    + len(self.lease_repayment_specs)
                    + 1
                ),
                include_cash_after_capex=(
                    self.acquisition_cash_series.cash_after_ppe_capex_and_acquisitions
                    is not None
                ),
            )
        else:
            self.acquisition_cash_series = None
            self.acquisition_cash_specs = ()
        self.expected_specs = (
            self.historical_specs
            + self.normalization_specs
            + self.quality_specs
            + self.working_capital_specs
            + self.profitability_driver_specs
            + self.profitability_change_specs
            + self.roe_attribution_specs
            + self.quality_change_specs
            + self.per_share_specs
            + self.per_share_attribution_specs
            + self.normalized_per_share_specs
            + self.fixed_asset_specs
            + self.lease_liability_specs
            + self.ownership_attribution_specs
            + self.goodwill_intangibles_specs
            + self.lease_rou_specs
            + self.deferred_tax_specs
            + self.capex_specs
            + self.lease_repayment_specs
            + self.acquisition_cash_specs
        )
        self.semantic_map = SemanticMap(expected_specs=self.expected_specs)
        self._historical_spec_index = {
            (s.family_id, s.period_index): s for s in self.historical_specs
        }
        self._normalization_spec_index = {
            (s.family_id, s.period_index): s for s in self.normalization_specs
        }
        self._quality_spec_index = {
            (s.family_id, s.period_index): s for s in self.quality_specs
        }
        self._working_capital_spec_index = {
            (s.family_id, s.period_index): s for s in self.working_capital_specs
        }
        self._profitability_driver_spec_index = {
            (s.family_id, s.period_index): s for s in self.profitability_driver_specs
        }
        self._profitability_change_spec_index = {
            (s.family_id, s.period_index): s for s in self.profitability_change_specs
        }
        self._roe_attribution_spec_index = {
            (s.family_id, s.period_index): s for s in self.roe_attribution_specs
        }
        self._quality_change_spec_index = {
            (s.family_id, s.period_index): s for s in self.quality_change_specs
        }
        self._per_share_spec_index = {
            (s.family_id, s.period_index): s for s in self.per_share_specs
        }
        self._per_share_attribution_spec_index = {
            (s.family_id, s.period_index): s
            for s in self.per_share_attribution_specs
        }
        self._normalized_per_share_spec_index = {
            (s.family_id, s.period_index): s
            for s in self.normalized_per_share_specs
        }
        self._fixed_asset_spec_index = {
            (s.family_id, s.period_index): s for s in self.fixed_asset_specs
        }
        self._lease_liability_spec_index = {
            (s.family_id, s.period_index): s for s in self.lease_liability_specs
        }
        self._ownership_attribution_spec_index = {
            (s.family_id, s.period_index): s for s in self.ownership_attribution_specs
        }
        self._goodwill_intangibles_spec_index = {
            (s.family_id, s.period_index): s for s in self.goodwill_intangibles_specs
        }
        self._lease_rou_spec_index = {
            (s.family_id, s.period_index): s for s in self.lease_rou_specs
        }
        self._deferred_tax_spec_index = {
            (s.family_id, s.period_index): s for s in self.deferred_tax_specs
        }
        self._capex_spec_index = {
            (s.family_id, s.period_index): s for s in self.capex_specs
        }
        self._lease_repayment_spec_index = {
            (s.family_id, s.period_index): s for s in self.lease_repayment_specs
        }
        self._acquisition_cash_spec_index = {
            (s.family_id, s.period_index): s for s in self.acquisition_cash_specs
        }
        self._deferred_spec_index = {c.id: c for c in DEFERRED_COMPONENT_SPECS}
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
        self._build_source_tabs(wb)
        self._build_condensed(wb)
        self._build_dupont(wb)
        self._build_accounting_judgment(wb)
        if self.ownership_attribution_series is not None:
            self._build_ownership_attribution(wb)
        if self.normalization_cases:
            self._build_normalization_judgment(wb)
            self._build_earnings_normalization(wb)
        if self.quality_series is not None:
            self._build_earnings_quality(wb)
        if self.working_capital_series is not None:
            self._build_working_capital_analysis(wb)
        if self.per_share_series is not None:
            self._build_per_share_analysis(wb)
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
