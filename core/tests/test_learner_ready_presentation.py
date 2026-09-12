"""Step 9I.1 — learner-ready presentation contract (style + root README)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.interface import DocumentManifest, DocumentType
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.tests.test_per_share import DEMO_ASSUMPTIONS, DEMO_JSON
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook, group_components_by_family

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_FILLS = {"FFFFFF", "FFFF00"}
FORBIDDEN_README_TERMS = (
    "bavgems",
    "bav pipeline",
    "gemini",
    "gemini gems",
    "legacy/",
    "coverage/",
    "sentinel",
    "edgar pipeline",
    "/bav-pipeline",
    "/bav-update",
    "/bav-news",
    "/bav-brief",
    "claude code plugin",
    "hint",
    "reveal",
)


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _font_color_is_black(font) -> bool:
    color = font.color
    if color is None or color.type is None:
        return True
    if color.type == "rgb" and color.rgb:
        return str(color.rgb).upper().endswith("000000")
    if color.type == "theme":
        # Default theme index 1 is typically black/dark text in Excel.
        return color.theme in (0, 1)
    return False


def _cell_participates(cell) -> bool:
    return cell.value is not None or cell.comment is not None or cell.has_style


def _assert_fresh_visible_style(path: Path, *, practice_cells: set[tuple[str, str]] | None = None) -> None:
    wb = load_workbook(path, data_only=False)
    practice_cells = practice_cells or set()
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        max_row = ws.max_row or 1
        max_col = ws.max_column or 1
        for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
            for cell in row:
                if not _cell_participates(cell):
                    continue
                font = cell.font
                assert font.name == "Aptos Narrow"
                assert font.size == 11
                assert font.bold is False
                assert font.italic is False
                assert font.underline in (None, "none")
                assert _font_color_is_black(font)

                for side in (
                    cell.border.left,
                    cell.border.right,
                    cell.border.top,
                    cell.border.bottom,
                    cell.border.diagonal,
                ):
                    style = None if side is None else side.style
                    assert style is None

                fill = _fill_rgb(cell)
                if fill:
                    assert fill in ALLOWED_FILLS
                key = (ws.title, cell.coordinate)
                if key in practice_cells:
                    assert fill == "FFFF00"
    wb.close()


def _build_canonical(tmp_path):
    data = HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )
    assumptions = json.loads(DEMO_ASSUMPTIONS.read_text(encoding="utf-8"))
    return build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
        assumptions,
    )


def _practice_cell_keys(answer: Path) -> set[tuple[str, str]]:
    smap = load_semantic_map(answer)
    return {(comp.tab, comp.cell) for comp in smap.all_ordered()}


def test_fresh_visible_workbook_uses_minimal_white_yellow_style(tmp_path):
    trainer, answer = _build_canonical(tmp_path)
    practice = _practice_cell_keys(answer)
    _assert_fresh_visible_style(trainer, practice_cells=practice)
    _assert_fresh_visible_style(answer, practice_cells=practice)

    smap = load_semantic_map(answer)
    assert len(group_components_by_family(smap)) == 66
    assert len(smap.all_ordered()) == 279
    summary = check_workbook(trainer)
    assert (summary.correct, summary.incorrect, summary.blank) == (0, 0, 279)


def test_check_colors_are_functional_exception_not_base_style(tmp_path):
    trainer, answer = _build_canonical(tmp_path)
    smap = load_semantic_map(answer)
    comps = [c for c in smap.all_ordered() if isinstance(c.expected_value, (int, float))]
    assert len(comps) >= 2
    filled, blank = comps[0], comps[1]

    wb = load_workbook(trainer, data_only=False)
    row, col = parse_cell_ref(filled.cell)
    wb[filled.tab].cell(row=row, column=col).value = filled.formula
    wb.save(trainer)
    wb.close()

    summary = check_workbook(trainer)
    assert summary.correct >= 1
    assert summary.blank >= 1

    wb = load_workbook(trainer, data_only=False)
    assert _fill_rgb(wb[filled.tab].cell(row, col)) == "C8E6C9"
    blank_row, blank_col = parse_cell_ref(blank.cell)
    assert wb[blank.tab].cell(blank_row, blank_col).value is None
    assert _fill_rgb(wb[blank.tab].cell(blank_row, blank_col)) == "FFFF00"

    # Non-practice visible cells remain white (sample a known label cell).
    label = wb[filled.tab].cell(row=row, column=1)
    if label.value is not None:
        assert _fill_rgb(label) in {"", "FFFFFF"}

    font = wb[filled.tab].cell(row, col).font
    assert font.name == "Aptos Narrow"
    assert font.size == 11
    assert font.bold is False
    for side in (
        wb[filled.tab].cell(row, col).border.left,
        wb[filled.tab].cell(row, col).border.right,
        wb[filled.tab].cell(row, col).border.top,
        wb[filled.tab].cell(row, col).border.bottom,
    ):
        style = None if side is None else side.style
        assert style is None
    wb.close()


def test_committed_canonical_pair_matches_minimal_style_contract():
    trainer = ROOT / "example" / "DEMO_HK_Trainer.xlsx"
    answer = ROOT / "example" / "DEMO_HK_Answer_Key.xlsx"
    practice = _practice_cell_keys(answer)
    _assert_fresh_visible_style(trainer, practice_cells=practice)
    _assert_fresh_visible_style(answer, practice_cells=practice)
    smap = load_semantic_map(answer)
    assert len(group_components_by_family(smap)) == 66
    assert len(smap.all_ordered()) == 279
    assert (check_workbook(trainer).correct, check_workbook(trainer).incorrect, check_workbook(trainer).blank) == (
        0,
        0,
        279,
    )
    for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
        assert not trainer.with_suffix(suffix).exists()


def test_root_readme_is_practical_trainer_guide():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in (
        "# BAV Excel Trainer — Hong Kong Edition",
        "## What works now",
        "## Quick start",
        "## How to practice",
        "## Inputs and scope",
        "## Planned",
    ):
        assert heading in text

    lowered = text.lower()
    for term in FORBIDDEN_README_TERMS:
        # Allow "Hint" only if somehow in Answer Key prose — plan forbids Hint/Reveal commands.
        assert term not in lowered, f"forbidden term present: {term!r}"

    assert "python -m core build" in text
    assert "python -m core list" in text
    assert "python -m core check" in text
    assert re.search(r"\bhint\b", lowered) is None
    assert re.search(r"\breveal\b", lowered) is None
