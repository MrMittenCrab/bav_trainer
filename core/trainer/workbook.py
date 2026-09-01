"""Training workbook generator — uses runtime SemanticMap as single source of truth."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

from ..engine.reference_model import ReferenceModelBuilder
from ..engine.semantic_map import ResolvedComponent, SemanticMap
from .semantic_io import component_map_path_for, load_semantic_map

TRAINER_META_SHEET = "_TrainerMeta"
REF_FORMULAS_SHEET = "_RefFormulas"
REF_VALUES_SHEET = "_RefValues"
HINT_FILL = PatternFill("solid", start_color="FFF9E6")
PRACTICE_FILL = PatternFill("solid", start_color="E8F4FD")
REVEALED_FILL = PatternFill("solid", start_color="E6F4EA")
DONE_FILL = PatternFill("solid", start_color="C8E6C9")


class TrainingWorkbookGenerator:
    """Generate a practice workbook from a completed reference model + semantic map."""

    def __init__(self, reference_path: Path, semantic_map: SemanticMap | None = None):
        self.reference_path = reference_path
        self.semantic_map = semantic_map or load_semantic_map(reference_path)

    def generate(self, output_path: Path) -> Path:
        shutil.copy2(self.reference_path, output_path)
        # Copy component map sidecar alongside training workbook
        ref_sidecar = component_map_path_for(self.reference_path)
        out_sidecar = component_map_path_for(output_path)
        if ref_sidecar.exists():
            shutil.copy2(ref_sidecar, out_sidecar)

        wb = load_workbook(output_path)
        self._create_hidden_reference_sheets(wb)
        self._create_trainer_meta(wb)
        self._strip_practice_formulas(wb)
        self._add_trainer_ui(wb)
        wb.save(output_path)

        meta_path = output_path.with_suffix(".trainer.json")
        meta_path.write_text(
            json.dumps([c.to_dict() for c in self.semantic_map.all_ordered()], indent=2) + "\n",
            encoding="utf-8",
        )
        return output_path

    def _create_hidden_reference_sheets(self, wb) -> None:
        for name in (REF_FORMULAS_SHEET, REF_VALUES_SHEET):
            if name in wb.sheetnames:
                del wb[name]

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

        for i, comp in enumerate(self.semantic_map.all_ordered(), start=2):
            ref_ws.cell(row=i, column=1, value=comp.id)
            ref_ws.cell(row=i, column=2, value=comp.tab)
            ref_ws.cell(row=i, column=3, value=comp.cell)
            ref_ws.cell(row=i, column=4, value=comp.formula)
            val_ws.cell(row=i, column=1, value=comp.id)
            val_ws.cell(row=i, column=2, value=comp.expected_value)
            val_ws.cell(row=i, column=3, value=comp.tolerance)

    def _create_trainer_meta(self, wb) -> None:
        if TRAINER_META_SHEET in wb.sheetnames:
            del wb[TRAINER_META_SHEET]
        ws = wb.create_sheet(TRAINER_META_SHEET)
        ws.sheet_state = "hidden"
        headers = [
            "id", "order", "tab", "cell", "title", "short_hint",
            "hint_level", "max_hints", "status", "category",
            "expected_value", "tolerance", "depends_on", "hints",
        ]
        for j, h in enumerate(headers, start=1):
            ws.cell(row=1, column=j, value=h).font = Font(bold=True)
        for i, comp in enumerate(self.semantic_map.all_ordered(), start=2):
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
            ws.cell(row=i, column=11, value=comp.expected_value)
            ws.cell(row=i, column=12, value=comp.tolerance)
            ws.cell(row=i, column=13, value=",".join(comp.depends_on))
            ws.cell(row=i, column=14, value="|".join(comp.hints))

    def _strip_practice_formulas(self, wb) -> None:
        for comp in self.semantic_map.all_ordered():
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            row, col = _cell_to_rc(comp.cell)
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
            "Complete components in dependency order. Use Check / Hint / Reveal buttons "
            "(TrainerMacros.bas) or python -m core check|hint|reveal."
        )
        headers = ["Order", "Component", "Tab", "Cell", "Status", "Depends on"]
        for j, h in enumerate(headers, start=1):
            ws.cell(row=4, column=j, value=h).font = Font(bold=True)
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 36
        ws.column_dimensions["C"].width = 22
        ws.column_dimensions["D"].width = 8
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 24

        for i, comp in enumerate(self.semantic_map.all_ordered(), start=5):
            ws.cell(row=i, column=1, value=comp.order)
            ws.cell(row=i, column=2, value=comp.title)
            ws.cell(row=i, column=3, value=comp.tab)
            ws.cell(row=i, column=4, value=comp.cell)
            ws.cell(row=i, column=5, value="pending")
            deps = ", ".join(comp.depends_on) if comp.depends_on else "—"
            ws.cell(row=i, column=6, value=deps)

        ws["A2"].font = Font(size=10)
        note_row = 5 + len(self.semantic_map.all_ordered()) + 2
        ws.cell(row=note_row, column=1, value="Select a row, then run CheckActive / HintActive / RevealActive macros.")


def _cell_to_rc(cell_ref: str) -> tuple[int, int]:
    from openpyxl.utils import column_index_from_string

    col = "".join(c for c in cell_ref if c.isalpha())
    row = int("".join(c for c in cell_ref if c.isdigit()))
    return row, column_index_from_string(col)


def build_training_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
) -> Path:
    """End-to-end: standardized data → reference model → training workbook."""
    ref_path = output_path.with_name(output_path.stem + "_reference.xlsx")
    builder = ReferenceModelBuilder(financials, assumptions)
    semantic_map = builder.build(ref_path)
    TrainingWorkbookGenerator(ref_path, semantic_map).generate(output_path)
    return output_path
