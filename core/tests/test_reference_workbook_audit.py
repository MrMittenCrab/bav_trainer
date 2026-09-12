"""Tests for the read-only reference workbook audit utility."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from scripts.audit_reference_workbook import audit_workbook

ROOT = Path(__file__).resolve().parents[2]
GOOGL = ROOT / "example" / "GOOGL_Demo_Integrated_Financials.xlsx"


def test_audit_workbook_synthetic_inventory(tmp_path):
    path = tmp_path / "synthetic.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Income Statement"
    ws["A1"] = "Revenue"
    ws["B1"] = 100
    ws["C1"] = "=B1*1.1"
    hidden = wb.create_sheet("Model_Base")
    hidden["A1"] = "Deferred example"
    hidden.sheet_state = "hidden"
    wb.save(path)
    wb.close()

    before = path.read_bytes()
    result = audit_workbook(path)
    after = path.read_bytes()
    assert before == after

    assert result["workbook"] == path.name
    assert [s["name"] for s in result["sheets"]] == [
        "Income Statement",
        "Model_Base",
    ]
    assert result["sheets"][0]["state"] == "visible"
    assert result["sheets"][1]["state"] == "hidden"
    assert result["sheets"][0]["formula_cells"] == 1
    assert result["sheets"][0]["nonempty_cells"] == 3
    assert result["sheets"][0]["representative_labels"] == ["Revenue"]
    assert result["sheets"][1]["representative_labels"] == ["Deferred example"]
    assert result["sheets"][1]["formula_cells"] == 0
    assert result["sheets"][1]["nonempty_cells"] == 1


def test_googl_reference_workbook_is_auditable_read_only():
    assert GOOGL.is_file()
    before = GOOGL.read_bytes()
    result = audit_workbook(GOOGL)
    after = GOOGL.read_bytes()
    assert before == after
    assert result["workbook"] == GOOGL.name
    assert len(result["sheets"]) >= 1
    names = [s["name"] for s in result["sheets"]]
    assert len(names) == len(set(names))
    for sheet in result["sheets"]:
        assert set(sheet) >= {
            "name",
            "state",
            "max_row",
            "max_column",
            "nonempty_cells",
            "formula_cells",
            "representative_labels",
        }
        assert isinstance(sheet["representative_labels"], list)
        assert len(sheet["representative_labels"]) <= 40
