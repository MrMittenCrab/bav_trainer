"""Validate user formulas by output and dependencies using SemanticMap."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

from .semantic_io import get_component, load_semantic_map, parse_cell_ref


@dataclass
class CheckResult:
    component_id: str
    passed: bool
    message: str
    user_value: float | str | None = None
    expected_value: float | str | None = None
    formula_present: bool = False


def _normalize_formula(formula: str) -> str:
    return formula.replace(" ", "").replace("'", "").upper()


def check_component(workbook_path: Path, component_id: str) -> CheckResult:
    """Check user formula against build-time expected value from SemanticMap."""
    smap = load_semantic_map(workbook_path)
    comp = smap.get(component_id)

    wb_user = load_workbook(workbook_path, data_only=True)
    if comp.tab not in wb_user.sheetnames:
        wb_user.close()
        return CheckResult(component_id, False, f"Tab missing: {comp.tab}")

    row, col = parse_cell_ref(comp.cell)
    user_val = wb_user[comp.tab].cell(row=row, column=col).value
    wb_user.close()

    wb_formula = load_workbook(workbook_path, data_only=False)
    formula = wb_formula[comp.tab].cell(row=row, column=col).value
    formula_present = isinstance(formula, str) and formula.startswith("=")
    wb_formula.close()

    if not formula_present and user_val is None:
        return CheckResult(
            component_id,
            False,
            "Enter a formula in the practice cell before checking.",
            formula_present=False,
        )

    expected = comp.expected_value
    if expected is None:
        return CheckResult(
            component_id,
            False,
            "No expected value in component map — rebuild the reference workbook.",
            user_value=user_val,
            formula_present=formula_present,
        )

    if user_val is None:
        if formula_present and _normalize_formula(str(formula)) == _normalize_formula(comp.formula):
            user_val = expected
        else:
            return CheckResult(
                component_id,
                False,
                "Cell has no computed value. Save the workbook after entering your formula so Excel recalculates.",
                expected_value=expected,
                formula_present=formula_present,
            )

    try:
        u, e = float(user_val), float(expected)
        tol = comp.tolerance
        if e == 0:
            passed = abs(u - e) <= tol
        else:
            passed = abs(u - e) / abs(e) <= tol or abs(u - e) <= tol
        msg = "Correct!" if passed else f"Value mismatch: got {u:.4g}, expected {e:.4g} (±{tol:.0%})"
        return CheckResult(
            component_id,
            passed,
            msg,
            user_value=u,
            expected_value=e,
            formula_present=formula_present,
        )
    except (TypeError, ValueError):
        passed = str(user_val).strip().upper() == str(expected).strip().upper()
        return CheckResult(
            component_id,
            passed,
            "Match" if passed else f"Expected {expected!r}, got {user_val!r}",
            user_value=user_val,
            expected_value=expected,
            formula_present=formula_present,
        )


def check_dependencies(workbook_path: Path, component_id: str) -> list[str]:
    """Behavioral check: verify formula references expected precedent cells."""
    comp = get_component(workbook_path, component_id)
    wb = load_workbook(workbook_path, data_only=False)
    if comp.tab not in wb.sheetnames:
        wb.close()
        return ["Tab missing"]
    row, col = parse_cell_ref(comp.cell)
    formula = wb[comp.tab].cell(row=row, column=col).value
    wb.close()
    if not isinstance(formula, str) or not formula.startswith("="):
        return ["No formula entered"]

    warnings: list[str] = []
    smap = load_semantic_map(workbook_path)
    for dep_id in comp.depends_on:
        dep = smap.get(dep_id)
        dep_ref = f"{dep.tab}!{dep.cell}".replace("'", "")
        if dep_ref not in formula.replace("'", ""):
            warnings.append(f"Expected reference to dependency {dep_id} ({dep.tab}!{dep.cell})")

    for related in comp.related_cells:
        parts = re.findall(r"'?[\w ]+'?![A-Z]+\d+", related)
        for part in parts:
            if part.replace("'", "") not in formula.replace("'", ""):
                if related not in formula:
                    warnings.append(f"Expected reference to {related} not found in formula")
    return warnings
