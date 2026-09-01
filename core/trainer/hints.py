"""Progressive hint system driven by SemanticMap metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

from .semantic_io import get_component, load_semantic_map, parse_cell_ref

HINT_FILL = PatternFill("solid", start_color="FFF9E6")
REVEALED_FILL = PatternFill("solid", start_color="E6F4EA")
META_SHEET = "_TrainerMeta"


@dataclass
class HintResult:
    component_id: str
    level: int
    max_level: int
    hint_text: str
    related_cells: list[str]
    exhausted: bool


def _find_meta_row(wb, component_id: str) -> int | None:
    if META_SHEET not in wb.sheetnames:
        return None
    ws = wb[META_SHEET]
    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == component_id:
            return r
    return None


def _sync_trainer_sheet_status(wb, comp, status: str) -> None:
    if META_SHEET in wb.sheetnames:
        meta_row = _find_meta_row(wb, comp.id)
        if meta_row:
            wb[META_SHEET].cell(row=meta_row, column=9, value=status)
    if "Trainer" in wb.sheetnames:
        for r in range(5, wb["Trainer"].max_row + 1):
            if wb["Trainer"].cell(row=r, column=4).value == comp.cell:
                if wb["Trainer"].cell(row=r, column=3).value == comp.tab:
                    wb["Trainer"].cell(row=r, column=5, value=status)
                    break


def show_hint(workbook_path: Path, component_id: str) -> HintResult:
    """Reveal the next progressive hint and update metadata."""
    comp = get_component(workbook_path, component_id)
    wb = load_workbook(workbook_path)
    meta_row = _find_meta_row(wb, component_id)
    level = 0
    if meta_row:
        level = int(wb[META_SHEET].cell(row=meta_row, column=7).value or 0)

    if level >= len(comp.hints):
        hint_text = comp.short_hint + " (all detailed hints shown)"
        exhausted = True
    else:
        hint_text = comp.hints[level]
        exhausted = False
        level += 1
        if meta_row:
            wb[META_SHEET].cell(row=meta_row, column=7, value=level)

    if comp.tab in wb.sheetnames:
        row, col = parse_cell_ref(comp.cell)
        hint_cell = wb[comp.tab].cell(row=row, column=col + 1)
        prefix = f"[Hint {level}/{len(comp.hints)}] "
        hint_cell.value = prefix + hint_text
        hint_cell.fill = HINT_FILL
        hint_cell.font = Font(italic=True, size=9)

    wb.save(workbook_path)
    wb.close()

    return HintResult(
        component_id=component_id,
        level=level,
        max_level=len(comp.hints),
        hint_text=hint_text,
        related_cells=comp.related_cells,
        exhausted=exhausted,
    )


def reveal_answer(workbook_path: Path, component_id: str) -> str:
    """Insert the reference formula from SemanticMap into the practice cell."""
    comp = get_component(workbook_path, component_id)
    if not comp.formula:
        raise ValueError(f"No reference formula for {component_id}")

    wb = load_workbook(workbook_path)
    row, col = parse_cell_ref(comp.cell)
    cell = wb[comp.tab].cell(row=row, column=col)
    cell.value = comp.formula
    cell.fill = REVEALED_FILL

    _sync_trainer_sheet_status(wb, comp, "revealed")

    wb.save(workbook_path)
    wb.close()
    return comp.formula
