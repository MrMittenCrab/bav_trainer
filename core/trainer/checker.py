"""Validate user formulas by output and behavior, not exact formula text."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

from ..engine.components import TRAINER_COMPONENTS


@dataclass
class CheckResult:
    component_id: str
    passed: bool
    message: str
    user_value: float | str | None = None
    expected_value: float | str | None = None
    formula_present: bool = False


def _component_by_id(component_id: str):
    for c in TRAINER_COMPONENTS:
        if c.id == component_id:
            return c
    raise KeyError(f"Unknown component: {component_id}")


def _parse_cell(cell_ref: str) -> tuple[int, int]:
    col = "".join(c for c in cell_ref if c.isalpha())
    row = int("".join(c for c in cell_ref if c.isdigit()))
    from openpyxl.utils import column_index_from_string

    return row, column_index_from_string(col)


def _load_reference_formula(wb, component_id: str) -> str | None:
    if "_RefFormulas" not in wb.sheetnames:
        return None
    ws = wb["_RefFormulas"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] == component_id:
            return row[3]
    return None


def _load_trainer_meta(wb_path: Path) -> dict:
    sidecar = wb_path.with_suffix(".trainer.json")
    if sidecar.exists():
        return json.loads(sidecar.read_text(encoding="utf-8"))
    return {c["id"]: c for c in []}


def check_component(workbook_path: Path, component_id: str) -> CheckResult:
    """Check user formula by comparing against reference workbook values."""
    comp = _component_by_id(component_id)
    ref_path = workbook_path.with_name(workbook_path.stem.replace("_Trainer", "") + "_reference.xlsx")
    if not ref_path.exists():
        ref_path = workbook_path.parent / (workbook_path.stem + "_reference.xlsx")

    wb_user = load_workbook(workbook_path, data_only=True)
    if comp.tab not in wb_user.sheetnames:
        wb_user.close()
        return CheckResult(component_id, False, f"Tab missing: {comp.tab}")

    row, col = _parse_cell(comp.cell)
    user_cell = wb_user[comp.tab].cell(row=row, column=col)
    user_val = user_cell.value
    wb_user.close()

    wb_formula = load_workbook(workbook_path, data_only=False)
    formula_cell = wb_formula[comp.tab].cell(row=row, column=col)
    formula = formula_cell.value
    formula_present = isinstance(formula, str) and formula.startswith("=")
    wb_formula.close()

    if not formula_present and user_val is None:
        return CheckResult(
            component_id,
            False,
            "Enter a formula in the practice cell before checking.",
            formula_present=False,
        )

    if not ref_path.exists():
        if formula_present:
            return CheckResult(
                component_id,
                True,
                "Formula present (reference workbook unavailable for value check).",
                formula_present=True,
            )
        return CheckResult(component_id, False, "Reference workbook not found for validation.")

    wb_ref = load_workbook(ref_path, data_only=True)
    if comp.tab not in wb_ref.sheetnames:
        wb_ref.close()
        return CheckResult(component_id, False, f"Reference tab missing: {comp.tab}")
    ref_val = wb_ref[comp.tab].cell(row=row, column=col).value
    wb_ref.close()

    if ref_val is None:
        return CheckResult(
            component_id,
            formula_present,
            "Reference value unavailable — open reference workbook in Excel to cache values.",
            user_value=user_val,
            expected_value=ref_val,
            formula_present=formula_present,
        )

    if user_val is None:
        return CheckResult(
            component_id,
            False,
            "Cell has no computed value. Ensure the workbook was saved after entering the formula.",
            expected_value=ref_val,
            formula_present=formula_present,
        )

    try:
        u, e = float(user_val), float(ref_val)
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
        passed = str(user_val).strip().upper() == str(ref_val).strip().upper()
        return CheckResult(
            component_id,
            passed,
            "Match" if passed else f"Expected {ref_val!r}, got {user_val!r}",
            user_value=user_val,
            expected_value=ref_val,
            formula_present=formula_present,
        )


def check_dependencies(workbook_path: Path, component_id: str) -> list[str]:
    """Behavioral check: verify formula references expected precedent cells."""
    comp = _component_by_id(component_id)
    wb = load_workbook(workbook_path, data_only=False)
    if comp.tab not in wb.sheetnames:
        wb.close()
        return ["Tab missing"]
    row, col = _parse_cell(comp.cell)
    formula = wb[comp.tab].cell(row=row, column=col).value
    wb.close()
    if not isinstance(formula, str) or not formula.startswith("="):
        return ["No formula entered"]
    warnings: list[str] = []
    for related in comp.related_cells:
        parts = re.findall(r"'?[\w ]+'?![A-Z]+\d+", related)
        for part in parts:
            if part.replace("'", "") not in formula.replace("'", ""):
                if related not in formula:
                    warnings.append(f"Expected reference to {related} not found in formula")
    return warnings
