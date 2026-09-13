"""Step 9M.0 — Fast Retailing real-company historical benchmark baseline."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.data.standardized_io import standardized_from_payload

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "fast_retailing"
MANIFEST = BENCH / "source_manifest.json"
SOURCE_FACTS = BENCH / "source_facts.json"
STD_JSON = BENCH / "FastRetailing_Standardized.json"
PROV_JSON = BENCH / "provenance.json"
BASELINE = BENCH / "BASELINE.md"
GAPS = BENCH / "GAPS.md"
AUDIT = ROOT / "scripts" / "audit_fast_retailing_benchmark.py"
BUILDER = ROOT / "scripts" / "build_fast_retailing_benchmark.py"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_source_manifest_locks_five_pdfs():
    manifest = _load_json(MANIFEST)
    assert len(manifest["sources"]) == 5
    assert {s["fiscal_year"] for s in manifest["sources"]} == {2021, 2022, 2023, 2024, 2025}
    for entry in manifest["sources"]:
        path = ROOT / entry["path"]
        assert path.is_file()
        data = path.read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]


def test_source_facts_schema_has_page_provenance():
    facts = _load_json(SOURCE_FACTS)
    assert set(facts["filings"]) == {"2021", "2022", "2023", "2024", "2025"}
    allowed_years = set(range(2020, 2026))
    for year, filing in facts["filings"].items():
        assert filing["file"].endswith(f"Fastretailing_CFS{year}.pdf")
        for section in ("income_statement", "balance_sheet", "cash_flow"):
            assert filing[section], f"missing {section} in {year}"
            for row in filing[section]:
                assert isinstance(row.get("pdf_page"), int) and row["pdf_page"] > 0
                assert row.get("statement")
                assert row.get("label")
                assert row.get("values")
                for period in row["values"]:
                    assert period.endswith("-08-31")
                    assert int(period[:4]) in allowed_years
        for row in filing.get("note_facts", []) + filing.get("share_facts", []):
            assert isinstance(row.get("pdf_page"), int) and row["pdf_page"] > 0
            assert row.get("note") or row.get("statement")


def test_builder_is_deterministic_and_round_trips():
    first = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    std_bytes = STD_JSON.read_bytes()
    prov_bytes = PROV_JSON.read_bytes()
    second = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert STD_JSON.read_bytes() == std_bytes
    assert PROV_JSON.read_bytes() == prov_bytes
    assert "overlap_conflicts=" in first.stdout
    assert "overlap_conflicts=" in second.stdout

    payload = _load_json(STD_JSON)
    fin = standardized_from_payload(payload)
    assert fin.ticker == "6288.HK"
    assert fin.company_name == "FAST RETAILING CO., LTD."
    assert fin.currency == "JPY"
    assert fin.units == "JPY in Millions"
    assert fin.jurisdiction == "JP"
    assert [p.end_date.isoformat() for p in fin.periods] == [
        "2021-08-31",
        "2022-08-31",
        "2023-08-31",
        "2024-08-31",
        "2025-08-31",
    ]
    assert fin.historical_shares is None
    assert {item.label for item in fin.income_statement}
    assert any(item.concept == "revenue" for item in fin.income_statement)


def _fy2025_value(fin, *, statement: str, concept: str | None = None, label: str | None = None):
    items = getattr(fin, statement)
    period = fin.periods[-1].end_date
    for item in items:
        if concept is not None and item.concept == concept:
            return item.values[period]
        if label is not None and item.label == label:
            return item.values[period]
    raise AssertionError(f"missing {statement} concept={concept!r} label={label!r}")


def test_fy2025_primary_and_note_anchors():
    payload = _load_json(STD_JSON)
    provenance = _load_json(PROV_JSON)
    fin = standardized_from_payload(payload)

    assert _fy2025_value(fin, statement="income_statement", concept="revenue") == 3_400_539
    assert (
        _fy2025_value(
            fin, statement="income_statement", label="Profit before income taxes"
        )
        == 650_574
    )
    assert _fy2025_value(fin, statement="income_statement", concept="tax_expense") == -191_421
    assert (
        _fy2025_value(fin, statement="income_statement", label="Finance income") == 99_143
    )
    assert (
        _fy2025_value(fin, statement="income_statement", label="Finance costs") == -12_834
    )
    assert (
        _fy2025_value(fin, statement="income_statement", label="Profit for the year")
        == 459_153
    )
    assert (
        _fy2025_value(
            fin,
            statement="income_statement",
            label="Owners of the Parent",
        )
        == 433_009
        or _fy2025_value(
            fin,
            statement="income_statement",
            concept="profit_attributable_to_owners",
        )
        == 433_009
    )

    assert _fy2025_value(fin, statement="balance_sheet", concept="cash") == 893_239
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="property_plant_equipment")
        == 332_351
    )
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="right_of_use_assets")
        == 477_111
    )
    assert _fy2025_value(fin, statement="balance_sheet", concept="goodwill") == 8_092
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="intangible_assets")
        == 91_606
    )
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="lease_liability_current")
        == 126_830
    )
    assert (
        _fy2025_value(
            fin, statement="balance_sheet", concept="lease_liability_noncurrent"
        )
        == 386_670
    )
    assert _fy2025_value(fin, statement="balance_sheet", concept="total_assets") == 3_859_353
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="total_liabilities")
        == 1_531_852
    )
    assert (
        _fy2025_value(
            fin, statement="balance_sheet", concept="equity_attributable_to_owners"
        )
        == 2_273_115
    )
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="noncontrolling_interests")
        == 54_385
    )
    assert _fy2025_value(fin, statement="balance_sheet", concept="total_equity") == 2_327_501

    assert (
        _fy2025_value(fin, statement="cash_flow", concept="operating_cash_flow") == 580_618
    )
    assert (
        _fy2025_value(fin, statement="cash_flow", concept="depreciation_amortization")
        == 216_492
    )
    assert (
        _fy2025_value(
            fin,
            statement="cash_flow",
            label="Payments for property, plant and equipment",
        )
        == -135_535
    )

    anchors = provenance["notes"]["fy2025_anchors"]
    assert anchors["aggregate_lease_liability"] == 513_501
    assert anchors["lease_interest_expense"] == 8_464
    assert anchors["parent_profit_plus_nci_vs_total"]["difference_units"] == 1
    assert anchors["lease_current_plus_noncurrent_vs_note"]["difference_units"] == 1
    assert 459_153 == 433_009 + 26_143 + 1

    # Provenance page references for key anchors
    revenue_key = next(
        k
        for k, v in provenance["values"].items()
        if v.get("concept") == "revenue" and v.get("period") == "2025-08-31"
    )
    assert provenance["values"][revenue_key]["pdf_page"] == 3
    assert "CFS2025.pdf" in provenance["values"][revenue_key]["file"]


def test_audit_script_writes_baseline_and_stage_records():
    completed = subprocess.run(
        [sys.executable, str(AUDIT)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert BASELINE.is_file()
    assert GAPS.is_file()
    text = BASELINE.read_text(encoding="utf-8")
    for stage in (
        "1_source_fixture_load",
        "2_identity_validation",
        "3_reconciliation",
        "4_reference_model_builder",
        "5_workbook_generation",
        "6_blank_check",
        "7_filled_check",
    ):
        assert stage in text
    assert "26f22b7" in text
    assert "pass" in completed.stdout or "fail" in completed.stdout
