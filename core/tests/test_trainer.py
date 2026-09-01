"""Tests for BAV Excel Trainer."""

import importlib.util
import json
from pathlib import Path

import pytest

from core.data.interface import DocumentManifest, DocumentType
from core.engine.component_catalog import COMPONENT_CATALOG, catalog_by_id
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.trainer.checker import check_component
from core.trainer.hints import reveal_answer
from core.trainer.semantic_io import load_semantic_map
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"


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


def test_build_training_workbook(tmp_path):
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    out = tmp_path / "DEMO_Trainer.xlsx"
    build_training_workbook(data, out)
    assert out.exists()
    ref = tmp_path / "DEMO_Trainer_reference.xlsx"
    assert ref.exists()
    smap = load_semantic_map(ref)
    assert len(smap.all_ordered()) == len(COMPONENT_CATALOG)
    for spec in COMPONENT_CATALOG:
        comp = smap.get(spec.id)
        assert comp.formula.startswith("=")
        assert comp.expected_value is not None
        assert comp.tab and comp.cell


def test_practice_cells_stripped(tmp_path):
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    out = tmp_path / "DEMO_Trainer.xlsx"
    build_training_workbook(data, out)
    smap = load_semantic_map(out)
    from openpyxl import load_workbook
    from core.trainer.semantic_io import parse_cell_ref

    wb = load_workbook(out, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        val = wb[comp.tab].cell(row=row, column=col).value
        assert val is None or (not isinstance(val, str) or not val.startswith("="))
    wb.close()


def test_cli_list_catalog():
    from core.__main__ import main
    assert main(["list"]) == 0


def test_check_and_reveal_use_semantic_map(tmp_path):
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    out = tmp_path / "DEMO_Trainer.xlsx"
    build_training_workbook(data, out)
    comp = load_semantic_map(out).get("nopat_fy")
    result = reveal_answer(out, "nopat_fy")
    assert result == comp.formula
    check = check_component(out, "nopat_fy")
    assert check.formula_present
    assert check.expected_value == comp.expected_value
    ref = tmp_path / "DEMO_Trainer_reference.xlsx"
    check_ref = check_component(ref, "nopat_fy")
    assert check_ref.passed


def test_cli_list_resolved(tmp_path):
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    out = tmp_path / "DEMO_Trainer.xlsx"
    build_training_workbook(data, out)
    from core.__main__ import main
    assert main(["list", "--workbook", str(out)]) == 0
