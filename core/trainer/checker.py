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
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
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
    comps = smap.all_ordered()
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
            dynamic_expected = {
                comp.id: expected_value_for_component(
                    anchor,
                    comp,
                    normalization=normalization,
                    earnings_quality=earnings_quality,
                    per_share=per_share,
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
