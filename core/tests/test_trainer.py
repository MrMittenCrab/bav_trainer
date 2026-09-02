"""Tests for BAV Excel Trainer."""

import importlib.util
from pathlib import Path

from openpyxl import load_workbook

from core.data.interface import DocumentManifest, DocumentType
from core.engine.component_catalog import COMPONENT_CATALOG
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.trainer.checker import check_component
from core.trainer.hints import reveal_answer
from core.trainer.semantic_io import (
    answer_key_path_for,
    load_semantic_map,
    parse_cell_ref,
    resolve_pair_paths,
)
from core.trainer.workbook import FONT_NAME, build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _ingest_demo():
    adapter = HKManualDocumentAdapter()
    return adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])


def test_legacy_components_module_removed():
    assert importlib.util.find_spec("core.engine.components") is None


def test_no_trainer_components_symbols_in_repo():
    for path in ROOT.rglob("*.py"):
        if ".git" in path.parts or "__pycache__" in path.parts or "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert "TRAINER_COMPONENTS" not in text
        assert "TrainerComponent" not in text
        assert "from core.engine.components" not in text
        assert "from .engine.components" not in text


def test_catalog_has_no_coordinates():
    for spec in COMPONENT_CATALOG:
        assert spec.semantic_key
        assert spec.tab_template or spec.category
        d = spec.__dict__
        assert "cell" not in d
        assert "tab" not in d or spec.tab_template


def test_ingest_demo_json():
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    assert data.ticker == "DEMO"
    assert len(data.periods) == 5
    report = adapter.reconcile(data)
    assert "income_statement" in report.checksums


def test_resolve_pair_paths_appends_and_preserves_trainer_stem(tmp_path):
    trainer, answer = resolve_pair_paths(tmp_path / "DEMO_HK_Trainer.xlsx")
    assert trainer.name == "DEMO_HK_Trainer.xlsx"
    assert answer.name == "DEMO_HK_Answer_Key.xlsx"

    trainer2, answer2 = resolve_pair_paths(tmp_path / "Acme.xlsx")
    assert trainer2.name == "Acme_Trainer.xlsx"
    assert answer2.name == "Acme_Answer_Key.xlsx"


def test_build_paired_trainer_and_answer_key(tmp_path):
    data = _ingest_demo()
    trainer_path, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")

    assert trainer_path.exists()
    assert answer_key_path.exists()
    assert trainer_path.name == "DEMO_HK_Trainer.xlsx"
    assert answer_key_path.name == "DEMO_HK_Answer_Key.xlsx"
    assert not (tmp_path / "DEMO_HK_Trainer_reference.xlsx").exists()
    assert not list(tmp_path.glob("*_reference.xlsx"))

    for path in (trainer_path, answer_key_path):
        smap = load_semantic_map(path)
        assert len(smap.all_ordered()) == len(COMPONENT_CATALOG)
        for spec in COMPONENT_CATALOG:
            comp = smap.get(spec.id)
            assert comp.formula.startswith("=")
            assert comp.expected_value is not None
            assert comp.tab and comp.cell


def test_trainer_practice_cells_blank_yellow_no_notes(tmp_path):
    data = _ingest_demo()
    trainer_path, _ = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    smap = load_semantic_map(trainer_path)
    wb = load_workbook(trainer_path, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        cell = wb[comp.tab].cell(row=row, column=col)
        assert cell.value is None
        assert _fill_rgb(cell) == "FFFF00"
        assert cell.comment is None
        # No adjacent hint-cell text from generation
        adj = wb[comp.tab].cell(row=row, column=col + 1)
        assert adj.value != comp.short_hint
        if isinstance(adj.value, str):
            assert not adj.value.startswith("[Hint")
    wb.close()


def test_answer_key_practice_cells_formula_yellow_legacy_notes(tmp_path):
    data = _ingest_demo()
    _, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    smap = load_semantic_map(answer_key_path)
    wb = load_workbook(answer_key_path, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        cell = wb[comp.tab].cell(row=row, column=col)
        assert isinstance(cell.value, str) and cell.value.startswith("=")
        assert cell.value == comp.formula
        assert _fill_rgb(cell) == "FFFF00"
        assert cell.comment is not None
        expected_hint = (comp.short_hint or "").strip() or (
            comp.hints[0] if comp.hints else comp.title
        )
        assert cell.comment.text == expected_hint
        assert cell.comment.author == "BAV Trainer"
    wb.close()


def test_pair_style_and_structure_parity(tmp_path):
    data = _ingest_demo()
    trainer_path, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    smap = load_semantic_map(trainer_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)

    visible_t = [s for s in wb_t.sheetnames if not s.startswith("_")]
    visible_a = [s for s in wb_a.sheetnames if not s.startswith("_")]
    assert visible_t == visible_a

    for name in visible_t:
        ws_t, ws_a = wb_t[name], wb_a[name]
        assert ws_t.freeze_panes == ws_a.freeze_panes
        assert bool(ws_t.sheet_view.showGridLines) == bool(ws_a.sheet_view.showGridLines)
        assert list(ws_t.merged_cells.ranges) == list(ws_a.merged_cells.ranges)
        for letter in ("A", "B", "C"):
            assert ws_t.column_dimensions[letter].width == ws_a.column_dimensions[letter].width
        for r in range(1, min(8, (ws_t.max_row or 1) + 1)):
            assert ws_t.row_dimensions[r].height == ws_a.row_dimensions[r].height

    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        ct = wb_t[comp.tab].cell(row=row, column=col)
        ca = wb_a[comp.tab].cell(row=row, column=col)
        assert ct.font.name == ca.font.name
        assert ct.font.size == ca.font.size
        assert ct.font.bold == ca.font.bold
        assert ct.border.left.style == ca.border.left.style
        assert ct.alignment.horizontal == ca.alignment.horizontal
        assert ct.alignment.vertical == ca.alignment.vertical
        assert ct.number_format == ca.number_format
        assert bool(ct.protection.locked) == bool(ca.protection.locked)
        assert _fill_rgb(ct) == _fill_rgb(ca) == "FFFF00"

    wb_t.close()
    wb_a.close()


def test_oshkosh_font_conventions(tmp_path):
    data = _ingest_demo()
    trainer_path, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for name in wb.sheetnames:
            if name.startswith("_"):
                continue
            ws = wb[name]
            title = ws["A1"]
            assert title.font.name == FONT_NAME
            assert title.font.size == 20
            assert title.font.bold is True
            # Sample a body label cell when present
            body = ws.cell(row=6, column=1)
            if body.value is not None:
                assert body.font.name == FONT_NAME
                assert body.font.size == 11
        wb.close()


def test_no_adjacent_hint_cells_on_generation(tmp_path):
    data = _ingest_demo()
    trainer_path, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    smap = load_semantic_map(trainer_path)
    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for comp in smap.all_ordered():
            row, col = parse_cell_ref(comp.cell)
            adj = wb[comp.tab].cell(row=row, column=col + 1)
            assert adj.value != comp.short_hint
        wb.close()


def test_cli_list_catalog():
    from core.__main__ import main
    assert main(["list"]) == 0


def test_check_and_reveal_use_semantic_map(tmp_path):
    data = _ingest_demo()
    trainer_path, answer_key_path = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    assert answer_key_path_for(trainer_path) == answer_key_path

    comp = load_semantic_map(trainer_path).get("nopat_fy")
    result = reveal_answer(trainer_path, "nopat_fy")
    assert result == comp.formula
    check = check_component(trainer_path, "nopat_fy")
    assert check.formula_present
    assert check.expected_value == comp.expected_value

    check_ak = check_component(answer_key_path, "nopat_fy")
    assert check_ak.passed
    assert check_ak.formula_present


def test_cli_list_resolved(tmp_path):
    data = _ingest_demo()
    trainer_path, _ = build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")
    from core.__main__ import main
    assert main(["list", "--workbook", str(trainer_path)]) == 0


def test_cli_build_reports_both_paths(tmp_path, capsys):
    from core.__main__ import main

    out = tmp_path / "DEMO_HK_Trainer.xlsx"
    rc = main(["build", str(DEMO_JSON), "-o", str(out)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Trainer workbook:" in captured.out
    assert "Answer Key workbook:" in captured.out
    assert (tmp_path / "DEMO_HK_Trainer.xlsx").exists()
    assert (tmp_path / "DEMO_HK_Answer_Key.xlsx").exists()
