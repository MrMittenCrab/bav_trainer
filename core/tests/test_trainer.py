"""Tests for BAV Excel Trainer."""

import json
from pathlib import Path

from core.data.interface import DocumentManifest, DocumentType
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"


def test_ingest_demo_json():
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    assert data.ticker == "DEMO"
    assert len(data.periods) == 5
    assert len(data.income_statement) >= 5
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
    meta = out.with_suffix(".trainer.json")
    assert meta.exists()
    components = json.loads(meta.read_text())
    assert len(components) >= 10


def test_cli_list():
    from core.__main__ import main
    assert main(["list"]) == 0
