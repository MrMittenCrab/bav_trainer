"""CLI tests for validate-source and reconcile."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "core", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    source_root = tmp_path / "source"
    extracted = tmp_path / "extracted"
    source_root.mkdir()
    extracted.mkdir()
    pdf = b"%PDF-fixture"
    (source_root / "demo.pdf").write_bytes(pdf)
    payload = {
        "schema_version": "1.0",
        "company": {
            "name": "DEMO CO",
            "ticker": "DEMO",
            "stock_code": "DEMO",
            "jurisdiction": "HK",
        },
        "filing": {
            "document_type": "annual_report",
            "fiscal_year": 2025,
            "period_end": "2025-12-31",
            "currency": "HKD",
            "unit_scale": "millions",
            "source_file": "demo.pdf",
        },
        "statements": {
            "income_statement": [
                {
                    "label": "Revenue",
                    "section": "",
                    "suggested_concept": "revenue",
                    "values": {
                        "2025-12-31": {
                            "value": 10,
                            "presentation_role": "current_period",
                        }
                    },
                    "source": {"page": 1},
                }
            ],
            "balance_sheet": [],
            "cash_flow": [],
        },
        "note_facts": [],
        "share_facts": [],
    }
    (extracted / "FY2025.json").write_text(json.dumps(payload), encoding="utf-8")
    return extracted, source_root


def test_help_lists_filing_commands():
    completed = _run("--help")
    assert completed.returncode == 0
    for name in ("validate-source", "reconcile", "build", "check", "list", "ingest"):
        assert name in completed.stdout
    assert "extract" not in completed.stdout.split()


def test_validate_source_success_and_hash_mismatch(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    ok = _run(
        "validate-source",
        str(extracted),
        "--source-root",
        str(source_root),
    )
    assert ok.returncode == 0
    expected = hashlib.sha256(b"%PDF-fixture").hexdigest()
    assert expected in ok.stdout

    payload = json.loads((extracted / "FY2025.json").read_text(encoding="utf-8"))
    payload["filing"]["source_sha256"] = "1" * 64
    (extracted / "FY2025.json").write_text(json.dumps(payload), encoding="utf-8")
    bad = _run(
        "validate-source",
        str(extracted),
        "--source-root",
        str(source_root),
    )
    assert bad.returncode != 0
    assert "source_hash_mismatch" in bad.stdout
    # Extracted JSON must not be rewritten by validation
    reloaded = json.loads((extracted / "FY2025.json").read_text(encoding="utf-8"))
    assert reloaded["filing"]["source_sha256"] == "1" * 64


def test_reconcile_writes_three_artifacts(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    out = tmp_path / "reconciled"
    completed = _run(
        "reconcile",
        str(extracted),
        "--source-root",
        str(source_root),
        "-o",
        str(out),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    names = sorted(p.name for p in out.iterdir())
    assert names == ["conflicts.json", "provenance.json", "standardized.json"]
    std = json.loads((out / "standardized.json").read_text(encoding="utf-8"))
    assert std["ticker"] == "DEMO"
    assert std["income_statement"][0]["concept"] == "revenue"


def test_validate_and_reconcile_reject_invalid_source_path(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    outside = tmp_path / "escaped.pdf"
    outside.write_bytes(b"%PDF-escaped-should-not-be-read")

    payload = json.loads((extracted / "FY2025.json").read_text(encoding="utf-8"))
    payload["filing"]["source_file"] = "../escaped.pdf"
    (extracted / "FY2025.json").write_text(json.dumps(payload), encoding="utf-8")

    bad_validate = _run(
        "validate-source",
        str(extracted),
        "--source-root",
        str(source_root),
    )
    assert bad_validate.returncode != 0
    assert "invalid_source_path" in bad_validate.stdout

    out = tmp_path / "reconciled"
    bad_reconcile = _run(
        "reconcile",
        str(extracted),
        "--source-root",
        str(source_root),
        "-o",
        str(out),
    )
    assert bad_reconcile.returncode != 0
    assert "invalid_source_path" in bad_reconcile.stdout
    assert not out.exists() or not any(out.iterdir())
