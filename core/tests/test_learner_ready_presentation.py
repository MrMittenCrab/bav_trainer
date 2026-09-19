"""Step 9I.1 — learner-ready presentation contract (style + root README)."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from core.data.interface import DocumentManifest, DocumentType
from core.engine.reference_model import JUDGMENT_SHEET, NORMALIZATION_JUDGMENT_SHEET
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.tests.test_per_share import DEMO_ASSUMPTIONS, DEMO_JSON
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import (
    JUDGMENT_RESPONSE_COLS,
    _judgment_case_rows,
    build_training_workbook,
    group_components_by_family,
)

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_FILLS = {"FFFFFF", "FFFF00"}
WHITE_RGBS = {"", "FFFFFF"}
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


def _normalize_rgb(color) -> str:
    if color is None:
        return ""
    rgb = getattr(color, "rgb", None)
    if not rgb or not isinstance(rgb, str):
        return ""
    return str(rgb).upper().lstrip("0")[-6:] if rgb else ""


def _fill_rgb_from_fill(fill) -> str:
    if not fill or fill.fill_type in (None, "none"):
        return ""
    for candidate in (
        getattr(fill, "fgColor", None),
        getattr(fill, "start_color", None),
        getattr(fill, "bgColor", None),
        getattr(fill, "end_color", None),
    ):
        rgb = _normalize_rgb(candidate)
        if rgb:
            return rgb
    return ""


def _fill_rgb(cell) -> str:
    return _fill_rgb_from_fill(getattr(cell, "fill", None))


def _rgb_is_yellow(rgb: str) -> bool:
    from scripts.audit_fast_retailing_benchmark import (
        _rgb_is_yellow as classify_yellow,
    )

    return classify_yellow(rgb)


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


def _judgment_response_keys(wb) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for sheet in (JUDGMENT_SHEET, NORMALIZATION_JUDGMENT_SHEET):
        if sheet not in wb.sheetnames:
            continue
        ws = wb[sheet]
        for row in _judgment_case_rows(ws):
            for col in JUDGMENT_RESPONSE_COLS:
                keys.add((sheet, f"{get_column_letter(col)}{row}"))
    return keys


def _iter_conditional_fills(ws):
    cf = ws.conditional_formatting
    rules_map = getattr(cf, "_cf_rules", None)
    if isinstance(rules_map, dict):
        for _sqref, rules in rules_map.items():
            for rule in rules:
                dxf = getattr(rule, "dxf", None)
                fill = getattr(dxf, "fill", None) if dxf is not None else None
                if fill is not None:
                    yield fill
        return
    try:
        for cf_obj in cf:
            rules = (
                getattr(cf_obj, "cfRule", None)
                or getattr(cf_obj, "rules", None)
                or ()
            )
            for rule in rules:
                dxf = getattr(rule, "dxf", None)
                fill = getattr(dxf, "fill", None) if dxf is not None else None
                if fill is not None:
                    yield fill
    except TypeError:
        return


def _assert_no_yellow_conditional_formatting(wb) -> None:
    for ws in wb.worksheets:
        for fill in _iter_conditional_fills(ws):
            rgb = _fill_rgb_from_fill(fill)
            assert not _rgb_is_yellow(rgb), (
                f"{ws.title} conditional formatting uses yellow fill {rgb!r}"
            )


def _assert_answer_key_no_yellow(path: Path) -> None:
    from scripts.audit_fast_retailing_benchmark import (
        _cell_has_yellow,
        _cell_is_white_or_none,
        _verify_answer_key_no_yellow,
    )

    wb = load_workbook(path, data_only=False)
    try:
        _verify_answer_key_no_yellow(wb)
        for ws in wb.worksheets:
            max_row = ws.max_row or 1
            max_col = ws.max_column or 1
            for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
                for cell in row:
                    assert not _cell_has_yellow(cell), (
                        f"{ws.title}!{cell.coordinate} has yellow fill"
                    )
                    if ws.sheet_state == "visible" and _cell_participates(cell):
                        assert _cell_is_white_or_none(cell), (
                            f"{ws.title}!{cell.coordinate} expected white/no-fill"
                        )
    finally:
        wb.close()


def _assert_fresh_visible_style(
    path: Path,
    *,
    practice_cells: set[tuple[str, str]] | None = None,
    role: str,
) -> None:
    if role not in {"trainer", "answer_key"}:
        raise ValueError(f"unsupported workbook role {role!r}")
    wb = load_workbook(path, data_only=False)
    practice_cells = practice_cells or set()
    learner_editable = set(practice_cells)
    if role == "trainer":
        learner_editable |= _judgment_response_keys(wb)
    _assert_no_yellow_conditional_formatting(wb)
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
                key = (ws.title, cell.coordinate)
                if role == "answer_key":
                    assert fill in WHITE_RGBS, (
                        f"{ws.title}!{cell.coordinate} expected white/no-fill, got {fill!r}"
                    )
                    assert not _rgb_is_yellow(fill)
                    continue
                if key in learner_editable:
                    assert fill == "FFFF00", (
                        f"{ws.title}!{cell.coordinate} expected learner yellow, got {fill!r}"
                    )
                else:
                    assert fill in WHITE_RGBS, (
                        f"{ws.title}!{cell.coordinate} expected white/no-fill, got {fill!r}"
                    )
                    if fill:
                        assert fill in ALLOWED_FILLS
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
    _assert_fresh_visible_style(trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer)

    smap = load_semantic_map(answer)
    assert len(group_components_by_family(smap)) == 78
    assert len(smap.all_ordered()) == 332
    summary = check_workbook(trainer)
    assert (summary.correct, summary.incorrect, summary.blank) == (0, 0, 332)


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


def test_committed_canonical_pair_matches_minimal_style_contract(tmp_path):
    committed_trainer = ROOT / "example" / "DEMO_HK_Trainer.xlsx"
    committed_answer = ROOT / "example" / "DEMO_HK_Answer_Key.xlsx"
    committed_smap = load_semantic_map(committed_answer)
    assert len(group_components_by_family(committed_smap)) == 78
    assert len(committed_smap.all_ordered()) == 332
    for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
        assert not committed_trainer.with_suffix(suffix).exists()

    fresh_trainer, fresh_answer = _build_canonical(tmp_path)
    fresh_smap = load_semantic_map(fresh_answer)
    assert [comp.id for comp in fresh_smap.all_ordered()] == [
        comp.id for comp in committed_smap.all_ordered()
    ]
    practice = {(comp.tab, comp.cell) for comp in fresh_smap.all_ordered()}
    _assert_fresh_visible_style(fresh_trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(fresh_answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(fresh_answer)

    check_dir = tmp_path / "canonical_check_copy"
    check_dir.mkdir()
    check_trainer = check_dir / fresh_trainer.name
    shutil.copy2(fresh_trainer, check_trainer)
    shutil.copy2(fresh_answer, check_dir / fresh_answer.name)
    for sidecar in (
        fresh_answer.with_suffix(".component_map.json"),
        fresh_answer.with_suffix(".assumptions.json"),
        fresh_answer.with_suffix(".trainer.json"),
    ):
        if sidecar.is_file():
            shutil.copy2(sidecar, check_dir / sidecar.name)
    summary = check_workbook(check_trainer)
    assert (summary.correct, summary.incorrect, summary.blank) == (0, 0, 332)


def test_saved_reopened_pair_answer_key_white_with_both_judgment_modules(tmp_path):
    trainer, answer = _build_canonical(tmp_path)
    reopened = tmp_path / "reopened"
    reopened.mkdir()
    trainer_r = reopened / trainer.name
    answer_r = reopened / answer.name
    shutil.copy2(trainer, trainer_r)
    shutil.copy2(answer, answer_r)
    for sidecar in (
        answer.with_suffix(".component_map.json"),
        answer.with_suffix(".assumptions.json"),
        answer.with_suffix(".trainer.json"),
    ):
        if sidecar.is_file():
            shutil.copy2(sidecar, reopened / sidecar.name)
    for path in (trainer_r, answer_r):
        wb = load_workbook(path, data_only=False)
        wb.save(path)
        wb.close()

    smap = load_semantic_map(answer_r)
    practice = {(comp.tab, comp.cell) for comp in smap.all_ordered()}
    _assert_fresh_visible_style(trainer_r, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer_r, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer_r)

    trainer_wb = load_workbook(trainer_r, data_only=False)
    answer_wb = load_workbook(answer_r, data_only=False)
    visible_t = [ws.title for ws in trainer_wb.worksheets if ws.sheet_state == "visible"]
    visible_a = [ws.title for ws in answer_wb.worksheets if ws.sheet_state == "visible"]
    assert "Overview" in visible_a
    assert "Trainer" not in visible_a
    assert "Trainer" in visible_t
    assert [title for title in visible_t if title != "Trainer"] == visible_a
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        trainer_cell = trainer_wb[comp.tab].cell(row=row, column=col)
        answer_cell = answer_wb[comp.tab].cell(row=row, column=col)
        assert trainer_cell.value is None
        assert trainer_cell.comment is None
        assert _fill_rgb(trainer_cell) == "FFFF00"
        assert isinstance(answer_cell.value, str) and answer_cell.value.startswith("=")
        assert answer_cell.value == comp.formula
        assert answer_cell.comment is not None
        assert (answer_cell.comment.text or "").strip()
        assert _fill_rgb(answer_cell) in WHITE_RGBS
        assert trainer_cell.font.name == answer_cell.font.name == "Aptos Narrow"
        assert trainer_cell.font.size == answer_cell.font.size == 11
        assert trainer_cell.font.bold is False
        assert answer_cell.font.bold is False

    for sheet in (JUDGMENT_SHEET, NORMALIZATION_JUDGMENT_SHEET):
        assert sheet in trainer_wb.sheetnames
        assert sheet in answer_wb.sheetnames
        rows = list(_judgment_case_rows(answer_wb[sheet]))
        assert rows, f"expected non-empty cases on {sheet}"
        for row in rows:
            for col in JUDGMENT_RESPONSE_COLS:
                answer_cell = answer_wb[sheet].cell(row, col)
                trainer_cell = trainer_wb[sheet].cell(row, col)
                assert answer_cell.value not in (None, "")
                assert _fill_rgb(answer_cell) in WHITE_RGBS
                assert trainer_cell.value is None
                assert trainer_cell.comment is None
                assert _fill_rgb(trainer_cell) == "FFFF00"
    trainer_wb.close()
    answer_wb.close()


def test_root_readme_is_practical_trainer_guide():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in (
        "# BAV — Hong Kong Edition",
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

    assert "python -m bav build" in text
    assert "python -m bav list" in text
    assert "python -m bav check" in text
    assert re.search(r"\bhint\b", lowered) is None
    assert re.search(r"\breveal\b", lowered) is None
