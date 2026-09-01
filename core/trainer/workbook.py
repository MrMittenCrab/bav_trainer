"""Training workbook generator — hides reference formulas, exposes practice cells."""

from __future__ import annotations

import json
import shutil
from copy import copy
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Protection
from openpyxl.utils import column_index_from_string, get_column_letter

from ..engine.components import TRAINER_COMPONENTS, TrainerComponent
from ..engine.reference_model import ReferenceModelBuilder

TRAINER_META_SHEET = "_TrainerMeta"
REF_FORMULAS_SHEET = "_RefFormulas"
REF_VALUES_SHEET = "_RefValues"
HINT_FILL = PatternFill("solid", start_color="FFF9E6")
PRACTICE_FILL = PatternFill("solid", start_color="E8F4FD")
DONE_FILL = PatternFill("solid", start_color="E6F4EA")


class TrainingWorkbookGenerator:
    """Generate a practice workbook from a completed reference model."""

    def __init__(self, reference_path: Path):
        self.reference_path = reference_path

    def generate(self, output_path: Path) -> Path:
        shutil.copy2(self.reference_path, output_path)
        wb = load_workbook(output_path)

        self._create_hidden_reference_sheets(wb)
        self._create_trainer_meta(wb)
        self._strip_practice_formulas(wb)
        self._add_trainer_ui(wb)

        wb.save(output_path)
        meta_path = output_path.with_suffix(".trainer.json")
        meta_path.write_text(
            json.dumps(self._export_component_meta(), indent=2) + "\n",
            encoding="utf-8",
        )
        return output_path

    def _parse_cell(self, cell_ref: str) -> tuple[str, int, int]:
        col = "".join(c for c in cell_ref if c.isalpha())
        row = int("".join(c for c in cell_ref if c.isdigit()))
        return cell_ref, column_index_from_string(col), row

    def _create_hidden_reference_sheets(self, wb) -> None:
        if REF_FORMULAS_SHEET in wb.sheetnames:
            del wb[REF_FORMULAS_SHEET]
        if REF_VALUES_SHEET in wb.sheetnames:
            del wb[REF_VALUES_SHEET]

        ref_ws = wb.create_sheet(REF_FORMULAS_SHEET)
        val_ws = wb.create_sheet(REF_VALUES_SHEET)
        ref_ws.sheet_state = "hidden"
        val_ws.sheet_state = "hidden"

        ref_ws["A1"] = "component_id"
        ref_ws["B1"] = "tab"
        ref_ws["C1"] = "cell"
        ref_ws["D1"] = "formula"
        val_ws["A1"] = "component_id"
        val_ws["B1"] = "expected_value"
        val_ws["C1"] = "tolerance"

        for i, comp in enumerate(TRAINER_COMPONENTS, start=2):
            tab = comp.tab
            if tab not in wb.sheetnames:
                continue
            ws = wb[tab]
            _, col, row = self._parse_cell(comp.cell)
            cell = ws.cell(row=row, column=col)
            formula = cell.value if isinstance(cell.value, str) and cell.value.startswith("=") else ""
            ref_ws.cell(row=i, column=1, value=comp.id)
            ref_ws.cell(row=i, column=2, value=tab)
            ref_ws.cell(row=i, column=3, value=comp.cell)
            ref_ws.cell(row=i, column=4, value=formula)
            val_ws.cell(row=i, column=1, value=comp.id)
            val_ws.cell(row=i, column=3, value=comp.tolerance)

    def _create_trainer_meta(self, wb) -> None:
        if TRAINER_META_SHEET in wb.sheetnames:
            del wb[TRAINER_META_SHEET]
        ws = wb.create_sheet(TRAINER_META_SHEET)
        ws.sheet_state = "hidden"
        headers = [
            "id", "order", "tab", "cell", "title", "short_hint",
            "hint_level", "max_hints", "status", "category",
        ]
        for j, h in enumerate(headers, start=1):
            ws.cell(row=1, column=j, value=h).font = Font(bold=True)
        for i, comp in enumerate(TRAINER_COMPONENTS, start=2):
            ws.cell(row=i, column=1, value=comp.id)
            ws.cell(row=i, column=2, value=comp.order)
            ws.cell(row=i, column=3, value=comp.tab)
            ws.cell(row=i, column=4, value=comp.cell)
            ws.cell(row=i, column=5, value=comp.title)
            ws.cell(row=i, column=6, value=comp.short_hint)
            ws.cell(row=i, column=7, value=0)
            ws.cell(row=i, column=8, value=len(comp.hints))
            ws.cell(row=i, column=9, value="pending")
            ws.cell(row=i, column=10, value=comp.category)

    def _strip_practice_formulas(self, wb) -> None:
        for comp in TRAINER_COMPONENTS:
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            _, col, row = self._parse_cell(comp.cell)
            cell = ws.cell(row=row, column=col)
            cell.value = None
            cell.fill = PRACTICE_FILL
            hint_cell = ws.cell(row=row, column=col + 1)
            hint_cell.value = comp.short_hint
            hint_cell.fill = HINT_FILL
            hint_cell.font = Font(italic=True, size=9)

    def _add_trainer_ui(self, wb) -> None:
        if "Trainer" in wb.sheetnames:
            del wb["Trainer"]
        ws = wb.create_sheet("Trainer", 0)
        ws["A1"] = "BAV Excel Trainer"
        ws["A1"].font = Font(bold=True, size=14)
        ws["A2"] = (
            "Complete each component in dependency order. Enter formulas in the "
            "highlighted blue cells on each tab, then use Check / Hint / Reveal."
        )
        ws["A4"] = "Component"
        ws["B4"] = "Tab"
        ws["C4"] = "Cell"
        ws["D4"] = "Status"
        ws["E4"] = "Actions"
        for j in range(1, 6):
            ws.cell(row=4, column=j).font = Font(bold=True)
        ws.column_dimensions["A"].width = 36
        ws.column_dimensions["B"].width = 22
        ws.column_dimensions["C"].width = 8
        ws.column_dimensions["D"].width = 12
        ws.column_dimensions["E"].width = 40

        for i, comp in enumerate(TRAINER_COMPONENTS, start=5):
            ws.cell(row=i, column=1, value=comp.title)
            ws.cell(row=i, column=2, value=comp.tab)
            ws.cell(row=i, column=3, value=comp.cell)
            ws.cell(row=i, column=4, value="pending")
            ws.cell(
                row=i,
                column=5,
                value=f"CLI: bav-trainer check {comp.id} | hint {comp.id} | reveal {comp.id}",
            )

        ws["A30"] = "Python CLI (from workbook directory):"
        ws["A31"] = "  python -m core check --workbook FILE.xlsx --component ID"
        ws["A32"] = "  python -m core hint --workbook FILE.xlsx --component ID"
        ws["A33"] = "  python -m core reveal --workbook FILE.xlsx --component ID"
        ws["A35"] = "Import TrainerMacros.bas for one-click Excel buttons (see core/templates/)."

    def _export_component_meta(self) -> list[dict]:
        return [
            {
                "id": c.id,
                "order": c.order,
                "tab": c.tab,
                "cell": c.cell,
                "title": c.title,
                "short_hint": c.short_hint,
                "hints": c.hints,
                "related_cells": c.related_cells,
                "tolerance": c.tolerance,
                "category": c.category,
            }
            for c in TRAINER_COMPONENTS
        ]


def build_training_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
) -> Path:
    """End-to-end: standardized data → reference model → training workbook."""
    ref_path = output_path.with_name(output_path.stem + "_reference.xlsx")
    ReferenceModelBuilder(financials, assumptions).build(ref_path)
    TrainingWorkbookGenerator(ref_path).generate(output_path)
    return output_path
