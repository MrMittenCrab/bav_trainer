"""Workbook-wide practice-cell validation using the matching Answer Key map."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

from ..data.standardized_io import standardized_from_payload
from ..model.earnings_quality import compute_earnings_quality_series
from ..model.financial_math import compute_anchor
from ..model.historical_expected import expected_value_for_component
from ..model.normalization import NormalizationCase, compute_normalization_series
from ..model.period_axis import canonical_fiscal_periods
from ..engine.component_catalog import (
    ACQUISITION_CASH_COMPONENT_CATALOG,
    CASH_ROLLFORWARD_COMPONENT_CATALOG,
    GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG,
    STORE_COUNT_COMPONENT_CATALOG,
    REVENUE_STORE_COMPONENT_CATALOG,
    COMPARABLE_SALES_COMPONENT_CATALOG,
    is_operating_kpi_source_identity,
    INVENTORY_ANALYSIS_COMPONENT_CATALOG,
    REPORTED_MARGIN_COMPONENT_CATALOG,
    SHARE_REPURCHASE_COMPONENT_CATALOG,
    CAPEX_COMPONENT_CATALOG,
    DEFERRED_TAX_COMPONENT_CATALOG,
    FIXED_ASSET_COMPONENT_CATALOG,
    GOODWILL_INTANGIBLES_COMPONENT_CATALOG,
    LEASE_LIABILITY_COMPONENT_CATALOG,
    LEASE_REPAYMENT_COMPONENT_CATALOG,
    LEASE_ROU_COMPONENT_CATALOG,
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
    OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
)
from ..model.fixed_asset import compute_fixed_asset_series, fixed_asset_applicable
from ..model.acquisition_cash import (
    compute_acquisition_cash_series,
    acquisition_cash_applicable,
)
from ..model.share_repurchase import (
    compute_share_repurchase_series,
    share_repurchase_applicable,
)
from ..model.cash_rollforward import (
    compute_cash_rollforward_series,
    cash_rollforward_applicable,
)
from ..model.reported_margin import (
    compute_reported_margin_series,
    reported_margin_applicable,
)
from ..model.inventory_analysis import (
    compute_inventory_analysis_series,
    inventory_analysis_applicable,
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
    compute_operating_kpi_revenue_comparable_sales_relationship,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_comparable_sales_relationship_applicable,
    operating_kpi_revenue_store_relationship_applicable,
)
from ..model.capex import compute_capex_series, capex_applicable
from ..model.lease_repayment import (
    compute_lease_repayment_series,
    lease_repayment_applicable,
)
from ..model.deferred_tax import (
    compute_deferred_tax_series,
    deferred_tax_applicable,
)
from ..model.goodwill_intangibles import (
    compute_goodwill_intangibles_series,
    goodwill_intangibles_applicable,
    goodwill_intangibles_availability,
)
from ..model.lease_liability import (
    compute_lease_liability_series,
    lease_liability_applicable,
)
from ..model.lease_rou import (
    compute_lease_rou_series,
    lease_rou_applicable,
)
from ..model.ownership_attribution import (
    compute_ownership_attribution_series,
    ownership_attribution_applicable,
)
from ..model.per_share import compute_per_share_series
from .check_context import (
    classification_overrides_for_check,
    load_check_context,
    normalization_treatments_for_check,
    validate_live_model_structure,
)
from .semantic_io import answer_key_path_for, load_semantic_map, parse_cell_ref
from .xlsx_fill_patch import CellFillUpdate, apply_fill_updates


BLANK_RGB = "FFFF00"
CORRECT_RGB = "C8E6C9"
INCORRECT_RGB = "FFC7CE"


def _normalization_cases_from_bindings(context) -> tuple[NormalizationCase, ...]:
    """Rebuild minimal cases from Check bindings (no pedagogical answer text)."""
    cases: list[NormalizationCase] = []
    for binding in context.normalization_bindings:
        alternatives = tuple(
            treatment
            for treatment in binding.allowed_treatments
            if treatment != binding.reference_treatment
        )
        cases.append(
            NormalizationCase(
                id=binding.case_id,
                order=binding.order,
                line_identity=binding.line_identity,
                override_selector=binding.source_selector,
                label="",
                scope=binding.scope,
                topic="",
                reference_treatment=binding.reference_treatment,
                alternatives=alternatives,
                model_rationale="",
                consequence_prompt="",
                model_consequence="",
            )
        )
    return tuple(cases)


@dataclass(frozen=True)
class CheckSummary:
    """Non-disclosing aggregate Check result — no formulas, values, or hints."""

    total: int
    correct: int
    incorrect: int
    blank: int


def _normalize_formula(formula: str) -> str:
    return formula.replace(" ", "").replace("'", "").upper()


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _values_match(user_val, expected, tolerance: float) -> bool:
    try:
        u, e = float(user_val), float(expected)
    except (TypeError, ValueError):
        return str(user_val).strip().upper() == str(expected).strip().upper()
    if e == 0:
        return abs(u - e) <= tolerance
    return abs(u - e) / abs(e) <= tolerance or abs(u - e) <= tolerance


def check_workbook(trainer_path: Path) -> CheckSummary:
    """Scan every practice cell in the Trainer; recolor yellow/green/red only.

    Reference semantics come from the matching Answer Key. Never writes answers,
    formulas, expected values, or hints into the Trainer. Fill updates are applied
    via OOXML so formula cached results survive repeated Checks.
    """
    trainer_path = Path(trainer_path)
    answer_key_path = answer_key_path_for(trainer_path)
    if not answer_key_path.exists():
        raise FileNotFoundError(
            f"Answer Key not found for Trainer {trainer_path.name}: "
            f"expected {answer_key_path}"
        )

    smap = load_semantic_map(answer_key_path)
    comps = [
        comp for comp in smap.all_ordered() if not is_operating_kpi_source_identity(comp)
    ]
    context = load_check_context(answer_key_path)

    wb = load_workbook(trainer_path, data_only=False)
    wb_cached = load_workbook(trainer_path, data_only=True)
    answer_wb = (
        load_workbook(answer_key_path, data_only=False) if context is not None else None
    )
    updates: list[CellFillUpdate] = []
    correct = incorrect = blank = 0
    try:
        dynamic_expected: dict[str, object] | None = None
        if context is not None:
            assert answer_wb is not None
            # Setup integrity before treatments or any fill planning.
            practice_cells = {(comp.tab, comp.cell) for comp in comps}
            validate_live_model_structure(
                wb,
                answer_wb,
                context,
                practice_cells=practice_cells,
            )
            overrides = classification_overrides_for_check(wb, context)
            financials = standardized_from_payload(context.source_payload)
            modeled_periods = tuple(
                date.fromisoformat(str(item)[:10]) for item in context.modeled_periods
            )
            canonical = tuple(canonical_fiscal_periods(financials))
            if modeled_periods != canonical:
                raise ValueError(
                    "Check context modeled_periods do not match canonical_fiscal_periods "
                    f"for reconstructed financials: {list(modeled_periods)} != {list(canonical)}"
                )
            anchor = compute_anchor(
                financials,
                list(modeled_periods),
                classification_overrides=overrides,
            )
            normalization = None
            if context.normalization_bindings:
                treatments = normalization_treatments_for_check(wb, context)
                cases = _normalization_cases_from_bindings(context)
                normalization = compute_normalization_series(
                    financials,
                    list(modeled_periods),
                    anchor,
                    cases,
                    treatments,
                )
            quality_family_ids = {
                family.id
                for family in (
                    *QUALITY_COMPONENT_CATALOG,
                    *QUALITY_CHANGE_COMPONENT_CATALOG,
                )
            }
            earnings_quality = None
            if any(comp.family_id in quality_family_ids for comp in comps):
                earnings_quality = compute_earnings_quality_series(
                    financials,
                    list(modeled_periods),
                    anchor,
                )
            per_share_family_ids = {
                family.id
                for family in (
                    *PER_SHARE_COMPONENT_CATALOG,
                    *PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
                    *NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
                )
            }
            per_share = None
            if any(comp.family_id in per_share_family_ids for comp in comps):
                per_share = compute_per_share_series(
                    financials,
                    list(modeled_periods),
                    anchor,
                )
            fixed_asset_family_ids = {
                family.id for family in FIXED_ASSET_COMPONENT_CATALOG
            }
            fixed_asset = None
            if any(comp.family_id in fixed_asset_family_ids for comp in comps):
                if fixed_asset_applicable(financials):
                    fixed_asset = compute_fixed_asset_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            lease_family_ids = {
                family.id for family in LEASE_LIABILITY_COMPONENT_CATALOG
            }
            lease_liability = None
            if any(comp.family_id in lease_family_ids for comp in comps):
                if lease_liability_applicable(financials):
                    lease_liability = compute_lease_liability_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            lease_rou_family_ids = {
                family.id for family in LEASE_ROU_COMPONENT_CATALOG
            }
            lease_rou = None
            if any(comp.family_id in lease_rou_family_ids for comp in comps):
                if lease_rou_applicable(financials):
                    lease_rou = compute_lease_rou_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            deferred_tax_family_ids = {
                family.id for family in DEFERRED_TAX_COMPONENT_CATALOG
            }
            deferred_tax = None
            if any(comp.family_id in deferred_tax_family_ids for comp in comps):
                if deferred_tax_applicable(financials):
                    deferred_tax = compute_deferred_tax_series(
                        financials,
                        list(modeled_periods),
                    )
            ownership_family_ids = {
                family.id for family in OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG
            }
            ownership_attribution = None
            if any(comp.family_id in ownership_family_ids for comp in comps):
                if ownership_attribution_applicable(financials):
                    ownership_attribution = compute_ownership_attribution_series(
                        financials,
                        list(modeled_periods),
                    )
            gi_family_ids = {
                family.id for family in GOODWILL_INTANGIBLES_COMPONENT_CATALOG
            }
            goodwill_intangibles = None
            gi_availability = None
            if any(comp.family_id in gi_family_ids for comp in comps):
                if goodwill_intangibles_applicable(financials):
                    gi_availability = goodwill_intangibles_availability(financials)
                    goodwill_intangibles = compute_goodwill_intangibles_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            capex_family_ids = {family.id for family in CAPEX_COMPONENT_CATALOG}
            capex = None
            if any(comp.family_id in capex_family_ids for comp in comps):
                if capex_applicable(financials):
                    capex = compute_capex_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            lease_repayment_family_ids = {
                family.id for family in LEASE_REPAYMENT_COMPONENT_CATALOG
            }
            lease_repayment = None
            if any(comp.family_id in lease_repayment_family_ids for comp in comps):
                if lease_repayment_applicable(financials):
                    lease_repayment = compute_lease_repayment_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            acquisition_cash_family_ids = {
                family.id for family in ACQUISITION_CASH_COMPONENT_CATALOG
            }
            acquisition_cash = None
            if any(comp.family_id in acquisition_cash_family_ids for comp in comps):
                if acquisition_cash_applicable(financials):
                    acquisition_cash = compute_acquisition_cash_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            share_repurchase_family_ids = {
                family.id for family in SHARE_REPURCHASE_COMPONENT_CATALOG
            }
            share_repurchase = None
            if any(comp.family_id in share_repurchase_family_ids for comp in comps):
                if share_repurchase_applicable(financials):
                    share_repurchase = compute_share_repurchase_series(
                        financials,
                        list(modeled_periods),
                        anchor,
                    )
            cash_rollforward_family_ids = {
                family.id for family in CASH_ROLLFORWARD_COMPONENT_CATALOG
            }
            cash_rollforward = None
            if any(comp.family_id in cash_rollforward_family_ids for comp in comps):
                if cash_rollforward_applicable(financials):
                    cash_rollforward = compute_cash_rollforward_series(
                        financials,
                        list(modeled_periods),
                    )
            reported_margin_family_ids = {
                family.id for family in REPORTED_MARGIN_COMPONENT_CATALOG
            }
            reported_margin = None
            if any(comp.family_id in reported_margin_family_ids for comp in comps):
                if reported_margin_applicable(financials):
                    reported_margin = compute_reported_margin_series(
                        financials,
                        list(modeled_periods),
                    )
            inventory_analysis_family_ids = {
                family.id for family in INVENTORY_ANALYSIS_COMPONENT_CATALOG
            }
            inventory_analysis = None
            if any(comp.family_id in inventory_analysis_family_ids for comp in comps):
                if inventory_analysis_applicable(financials):
                    inventory_analysis = compute_inventory_analysis_series(
                        financials,
                        list(modeled_periods),
                    )
            geographic_family_ids = {
                family.id for family in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG
            }
            geographic = None
            if any(comp.family_id in geographic_family_ids for comp in comps):
                if geographic_segment_applicable(financials):
                    geographic = compute_geographic_segment_series(
                        financials,
                        list(modeled_periods),
                    )
            operating_kpi_family_ids = {
                family.id for family in STORE_COUNT_COMPONENT_CATALOG
            }
            relationship_family_ids = {
                family.id for family in REVENUE_STORE_COMPONENT_CATALOG
            }
            compsales_family_ids = {
                family.id for family in COMPARABLE_SALES_COMPONENT_CATALOG
            }
            operating_kpi = None
            operating_kpi_relationship = None
            operating_kpi_compsales_relationship = None
            needed_ids = (
                operating_kpi_family_ids
                | relationship_family_ids
                | compsales_family_ids
            )
            if any(comp.family_id in needed_ids for comp in comps):
                if operating_kpi_applicable(financials):
                    operating_kpi = compute_operating_kpi_series(
                        financials,
                        list(modeled_periods),
                    )
                if operating_kpi_revenue_store_relationship_applicable(financials):
                    operating_kpi_relationship = (
                        compute_operating_kpi_revenue_store_relationship(
                            financials,
                            list(modeled_periods),
                        )
                    )
                if operating_kpi_revenue_comparable_sales_relationship_applicable(
                    financials
                ):
                    operating_kpi_compsales_relationship = (
                        compute_operating_kpi_revenue_comparable_sales_relationship(
                            financials,
                            list(modeled_periods),
                        )
                    )
            dynamic_expected = {
                comp.id: expected_value_for_component(
                    anchor,
                    comp,
                    normalization=normalization,
                    earnings_quality=earnings_quality,
                    per_share=per_share,
                    fixed_asset=fixed_asset,
                    lease_liability=lease_liability,
                    lease_rou=lease_rou,
                    deferred_tax=deferred_tax,
                    ownership_attribution=ownership_attribution,
                    goodwill_intangibles=goodwill_intangibles,
                    goodwill_intangibles_availability=gi_availability,
                    capex=capex,
                    lease_repayment=lease_repayment,
                    acquisition_cash=acquisition_cash,
                    share_repurchase=share_repurchase,
                    cash_rollforward=cash_rollforward,
                    reported_margin=reported_margin,
                    inventory_analysis=inventory_analysis,
                    geographic=geographic,
                    operating_kpi=operating_kpi,
                    operating_kpi_relationship=operating_kpi_relationship,
                    operating_kpi_compsales_relationship=(
                        operating_kpi_compsales_relationship
                    ),
                )
                for comp in comps
            }

        for comp in comps:
            if comp.tab not in wb.sheetnames:
                incorrect += 1
                continue
            row, col = parse_cell_ref(comp.cell)
            cell = wb[comp.tab].cell(row=row, column=col)
            formula_val = cell.value

            if _is_blank(formula_val):
                updates.append(CellFillUpdate(comp.tab, comp.cell, BLANK_RGB))
                blank += 1
                continue

            if (
                isinstance(formula_val, str)
                and formula_val.startswith("=")
                and _normalize_formula(formula_val) == _normalize_formula(comp.formula)
            ):
                updates.append(CellFillUpdate(comp.tab, comp.cell, CORRECT_RGB))
                correct += 1
                continue

            expected = (
                dynamic_expected[comp.id]
                if dynamic_expected is not None
                else comp.expected_value
            )
            cached = None
            if comp.tab in wb_cached.sheetnames:
                cached = wb_cached[comp.tab].cell(row=row, column=col).value

            if cached is not None and _values_match(cached, expected, comp.tolerance):
                updates.append(CellFillUpdate(comp.tab, comp.cell, CORRECT_RGB))
                correct += 1
            else:
                updates.append(CellFillUpdate(comp.tab, comp.cell, INCORRECT_RGB))
                incorrect += 1
    finally:
        wb.close()
        wb_cached.close()
        if answer_wb is not None:
            answer_wb.close()

    apply_fill_updates(trainer_path, updates)
    return CheckSummary(
        total=len(comps),
        correct=correct,
        incorrect=incorrect,
        blank=blank,
    )
