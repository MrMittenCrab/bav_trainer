"""Training workbook generator — uses runtime SemanticMap as single source of truth."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Border, Font, PatternFill, Side

from ..engine.reference_model import ReferenceModelBuilder
from ..engine.semantic_map import SemanticMap
from ..data.line_identity import validate_financials_identities
from ..ingestion.reconciler import reconcile_financials
from .semantic_io import (
    component_map_path_for,
    load_semantic_map,
    resolve_pair_paths,
)

TRAINER_META_SHEET = "_TrainerMeta"
REF_FORMULAS_SHEET = "_RefFormulas"
REF_VALUES_SHEET = "_RefValues"
NOTE_AUTHOR = "BAV Trainer"

PRACTICE_FILL = PatternFill("solid", start_color="FFFF00")
REVEALED_FILL = PatternFill("solid", start_color="E6F4EA")
DONE_FILL = PatternFill("solid", start_color="C8E6C9")

FONT_NAME = "Aptos Narrow"
TITLE_FONT = Font(name=FONT_NAME, size=20, bold=True, color="000000")
BODY_FONT = Font(name=FONT_NAME, size=11, color="000000")
BODY_BOLD_FONT = Font(name=FONT_NAME, size=11, bold=True, color="000000")
WHITE_FILL = PatternFill("solid", start_color="FFFFFF")
THIN_BORDER = Border(
    left=Side(style="thin", color="000000"),
    right=Side(style="thin", color="000000"),
    top=Side(style="thin", color="000000"),
    bottom=Side(style="thin", color="000000"),
)

_HIDDEN_PREFIX = "_"


class TrainingWorkbookGenerator:
    """Generate a matched Trainer / Answer Key pair from a completed model."""

    def __init__(self, answer_key_path: Path, semantic_map: SemanticMap | None = None):
        self.answer_key_path = answer_key_path
        self.semantic_map = semantic_map or load_semantic_map(answer_key_path)

    def generate(self, trainer_path: Path) -> tuple[Path, Path]:
        """Finalize Answer Key in place, then derive the Trainer from it."""
        wb = load_workbook(self.answer_key_path)
        self._apply_oshkosh_style(wb)
        self._create_hidden_reference_sheets(wb)
        self._create_trainer_meta(wb)
        self._add_trainer_ui(wb)
        self._decorate_answer_key_practice_cells(wb)
        wb.save(self.answer_key_path)
        wb.close()

        shutil.copy2(self.answer_key_path, trainer_path)
        ref_sidecar = component_map_path_for(self.answer_key_path)
        out_sidecar = component_map_path_for(trainer_path)
        if ref_sidecar.exists():
            shutil.copy2(ref_sidecar, out_sidecar)

        wb = load_workbook(trainer_path)
        self._blank_trainer_practice_cells(wb)
        wb.save(trainer_path)
        wb.close()

        meta_path = trainer_path.with_suffix(".trainer.json")
        meta_path.write_text(
            json.dumps([c.to_dict() for c in self.semantic_map.all_ordered()], indent=2) + "\n",
            encoding="utf-8",
        )
        return trainer_path, self.answer_key_path

    def _visible_sheets(self, wb):
        return [ws for ws in wb.worksheets if not ws.title.startswith(_HIDDEN_PREFIX)]

    def _apply_oshkosh_style(self, wb) -> None:
        """Apply shared Oshkosh-derived fonts and base styling to visible sheets."""
        for ws in self._visible_sheets(wb):
            ws.sheet_view.showGridLines = False
            max_row = ws.max_row or 1
            max_col = ws.max_column or 1
            for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
                for cell in row:
                    if cell.value is None and (cell.fill is None or cell.fill.fill_type is None):
                        continue
                    is_title = cell.row == 1 and cell.column == 1 and isinstance(cell.value, str)
                    was_bold = bool(cell.font and cell.font.bold)
                    if is_title:
                        cell.font = TITLE_FONT
                    elif was_bold:
                        cell.font = BODY_BOLD_FONT
                    elif cell.value is not None:
                        cell.font = BODY_FONT
                    # White base; practice yellow is applied later
                    if cell.fill and cell.fill.fill_type == "solid":
                        cell.fill = WHITE_FILL

            # Thin borders on header / section / total label rows
            for r in range(1, max_row + 1):
                label = ws.cell(row=r, column=1).value
                if not isinstance(label, str):
                    continue
                upper = label.upper()
                is_section = (
                    upper.isupper() and len(label) > 3 and " " in label
                ) or label.endswith(":")
                is_header = r <= 6 and was_header_row(ws, r)
                is_total = "total" in label.lower() or label.lower().startswith("weighted")
                if is_section or is_header or is_total or (r == 1):
                    for c in range(1, max_col + 1):
                        cell = ws.cell(row=r, column=c)
                        if cell.value is not None or is_header:
                            cell.border = THIN_BORDER

    def _decorate_answer_key_practice_cells(self, wb) -> None:
        for comp in self.semantic_map.all_ordered():
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            row, col = _cell_to_rc(comp.cell)
            cell = ws.cell(row=row, column=col)
            # Retain working formula/input; apply bright yellow + legacy Note
            cell.fill = PRACTICE_FILL
            hint = (comp.short_hint or "").strip()
            if not hint and comp.hints:
                hint = str(comp.hints[0]).strip()
            if not hint:
                hint = comp.title
            cell.comment = Comment(hint, NOTE_AUTHOR)

    def _blank_trainer_practice_cells(self, wb) -> None:
        for comp in self.semantic_map.all_ordered():
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            row, col = _cell_to_rc(comp.cell)
            cell = ws.cell(row=row, column=col)
            # Preserve font, border, alignment, protection, number format
            cell.value = None
            cell.fill = PRACTICE_FILL
            cell.comment = None

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
            ws.cell(row=1, column=j, value=h).font = Font(name=FONT_NAME, bold=True, size=11)
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

    def _add_trainer_ui(self, wb) -> None:
        if "Trainer" in wb.sheetnames:
            del wb["Trainer"]
        ws = wb.create_sheet("Trainer", 0)
        ws.sheet_view.showGridLines = False
        ws["A1"] = "BAV Excel Trainer"
        ws["A1"].font = TITLE_FONT
        ws["A2"] = (
            "Complete yellow practice cells in dependency order. "
            "Open the matching Answer Key for formulas and Notes, "
            "or use optional Check / Hint / Reveal (TrainerMacros.bas / CLI)."
        )
        ws["A2"].font = BODY_FONT
        headers = ["Order", "Component", "Tab", "Cell", "Status", "Depends on"]
        for j, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=j, value=h)
            cell.font = BODY_BOLD_FONT
            cell.border = THIN_BORDER
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 36
        ws.column_dimensions["C"].width = 22
        ws.column_dimensions["D"].width = 8
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 24

        for i, comp in enumerate(self.semantic_map.all_ordered(), start=5):
            ws.cell(row=i, column=1, value=comp.order).font = BODY_FONT
            ws.cell(row=i, column=2, value=comp.title).font = BODY_FONT
            ws.cell(row=i, column=3, value=comp.tab).font = BODY_FONT
            ws.cell(row=i, column=4, value=comp.cell).font = BODY_FONT
            ws.cell(row=i, column=5, value="pending").font = BODY_FONT
            deps = ", ".join(comp.depends_on) if comp.depends_on else "—"
            ws.cell(row=i, column=6, value=deps).font = BODY_FONT

        note_row = 5 + len(self.semantic_map.all_ordered()) + 2
        note = ws.cell(
            row=note_row,
            column=1,
            value="Select a row, then run CheckActive / HintActive / RevealActive macros.",
        )
        note.font = BODY_FONT


def was_header_row(ws, row: int) -> bool:
    """Heuristic: row looks like a column-header band (dates / Metric / Scenario)."""
    vals = [ws.cell(row=row, column=c).value for c in range(1, min(6, (ws.max_column or 1) + 1))]
    texts = [v for v in vals if isinstance(v, str)]
    if not texts:
        return False
    markers = ("line item", "metric", "scenario", "probability", "ivps")
    return any(t.lower() in markers or t.lower().startswith("line") for t in texts)


def _cell_to_rc(cell_ref: str) -> tuple[int, int]:
    from openpyxl.utils import column_index_from_string

    col = "".join(c for c in cell_ref if c.isalpha())
    row = int("".join(c for c in cell_ref if c.isdigit()))
    return row, column_index_from_string(col)


def build_training_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
) -> tuple[Path, Path]:
    """End-to-end: standardized data → Answer Key + Trainer workbook pair.

    Returns ``(trainer_path, answer_key_path)``.
    """
    validate_financials_identities(financials)

    report = reconcile_financials(financials)
    failed = [name for name, ok in report.checksums.items() if ok is False]
    if failed:
        details = "; ".join(failed)
        warnings = "; ".join(report.warnings) if report.warnings else details
        raise ValueError(
            f"Source statement checksum failed ({details}). "
            f"Refuse Trainer / Answer Key build. {warnings}"
        )

    trainer_path, answer_key_path = resolve_pair_paths(output_path)
    builder = ReferenceModelBuilder(financials, assumptions)
    semantic_map = builder.build(answer_key_path)
    TrainingWorkbookGenerator(answer_key_path, semantic_map).generate(trainer_path)
    return trainer_path, answer_key_path
