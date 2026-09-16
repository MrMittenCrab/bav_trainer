"""CLI tests for validate-source and reconcile."""

from __future__ import annotations

import copy
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


def test_reconcile_help_lists_admit_period():
    completed = _run("reconcile", "--help")
    assert completed.returncode == 0
    assert "--admit-period" in completed.stdout


def test_reconcile_rejects_invalid_admit_period_before_write(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    out = tmp_path / "reconciled"
    completed = _run(
        "reconcile",
        str(extracted),
        "--source-root",
        str(source_root),
        "-o",
        str(out),
        "--admit-period",
        "not-a-date",
    )
    assert completed.returncode != 0
    assert "invalid --admit-period" in completed.stdout
    assert not out.exists() or not any(out.iterdir())


def test_validate_and_reconcile_reject_non_string_kpi_label_at_parse(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    payload = json.loads((extracted / "FY2025.json").read_text(encoding="utf-8"))
    payload["note_facts"] = [
        {
            "fact_type": "kpi.operating.store_count.company_operated",
            "period": "2025-12-31",
            "value": 655,
            "status": "reported",
            "unit": "stores",
            "source": {"page": 7, "note": "Company-Operated Stores", "label": 123},
            "presentation_role": "current_period",
        }
    ]
    original = copy.deepcopy(payload)
    (extracted / "FY2025.json").write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "reconciled"
    bad_validate = _run(
        "validate-source",
        str(extracted),
        "--source-root",
        str(source_root),
    )
    assert bad_validate.returncode != 0
    assert "missing reported label" in bad_validate.stdout
    assert "error:" in bad_validate.stdout
    assert "invalid_operating_kpi" not in bad_validate.stdout
    bad_reconcile = _run(
        "reconcile",
        str(extracted),
        "--source-root",
        str(source_root),
        "-o",
        str(out),
    )
    assert bad_reconcile.returncode != 0
    assert "missing reported label" in bad_reconcile.stdout
    assert "error:" in bad_reconcile.stdout
    assert "invalid_operating_kpi" not in bad_reconcile.stdout
    assert "wrote no artifacts" not in bad_reconcile.stdout
    assert json.loads((extracted / "FY2025.json").read_text(encoding="utf-8")) == original
    assert not out.exists() or not any(out.iterdir())


def test_reconcile_rejects_unsupported_admit_period_before_write(tmp_path: Path):
    extracted, source_root = _write_fixture(tmp_path)
    out = tmp_path / "reconciled"
    completed = _run(
        "reconcile",
        str(extracted),
        "--source-root",
        str(source_root),
        "-o",
        str(out),
        "--admit-period",
        "2019-01-01",
    )
    assert completed.returncode != 0
    assert "unsupported comparative period 2019-01-01" in completed.stdout
    assert not out.exists() or not any(out.iterdir())


def test_reconcile_serializes_management_identity_assessments(tmp_path: Path):
    from core.ingestion.management_kpi_identity import (
        PEER_COMPARISON_REASONS,
        REASON_NO_DISTINCT_PEER,
        REQUIRED_COMPARISON_REASONS,
    )
    from core.tests.test_management_kpi_admission import (
        ANNUAL_NAMES,
        EXTRACTED,
        MANAGEMENT_NAMES,
        SOURCE,
        _bytes_by_name,
        _canonicalize,
        _copy_json,
    )
    from core.tests.test_management_kpi_identity import FALSE_POSITIVE_METRIC_IDS

    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_out = tmp_path / "mixed-out"
    annual_out = tmp_path / "annual-out"
    mixed_run = _run(
        "reconcile",
        str(mixed),
        "--source-root",
        str(SOURCE),
        "--admit-period",
        "2022-01-30",
        "-o",
        str(mixed_out),
    )
    annual_run = _run(
        "reconcile",
        str(annual),
        "--source-root",
        str(SOURCE),
        "--admit-period",
        "2022-01-30",
        "-o",
        str(annual_out),
    )
    assert mixed_run.returncode == 0, mixed_run.stdout + mixed_run.stderr
    assert annual_run.returncode == 0, annual_run.stdout + annual_run.stderr
    admission = json.loads(
        (mixed_out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    assert admission["reported_observation_count"] == 135
    assert len(admission["assessments"]["items"]) == 135
    assert admission["assessments"]["canonical_selection"] == "deferred"
    assert admission["assessments"]["supported_count"] == 28
    assert admission["assessments"]["outside_scope_count"] == 107
    recon = admission["reconciliation"]
    assert recon["canonical_selection"] == "deferred"
    assert recon["outcome_counts"]["agreeing_duplicate"] == 0
    assert recon["outcome_counts"]["conflicting_candidate"] == 0
    assert recon["outcome_counts"]["outside_scope"] == 107
    assert recon["outcome_counts"]["singleton"] == 6
    pair_locators = [
        tuple(item["locators"])
        for item in recon["items"]
        if item["kind"] == "pair"
    ]
    assert pair_locators == [tuple(sorted(item)) for item in pair_locators]
    assert all(left != right for left, right in pair_locators)
    counts = admission["assessments"]["comparability_counts"]
    assert counts["comparable"] == 0
    assert counts["not_comparable"] == 22
    assert counts["unresolved"] == 6
    assert counts["outside_scope"] == 107
    reported = {
        item["locator"]: item
        for item in admission["observations"]
        if item["kind"] == "reported_kpi"
    }
    false_positives = [
        item
        for item in admission["assessments"]["items"]
        if reported[item["locator"]]["metric_id"] in FALSE_POSITIVE_METRIC_IDS
    ]
    assert len(false_positives) == 6
    for item in false_positives:
        assert item["comparability"] == "unresolved"
        assert REASON_NO_DISTINCT_PEER in item["unresolved_reasons"]
        assert item["peer_locators"] == []
        assert item["locator"] not in item["peer_locators"]
    for item in admission["assessments"]["items"]:
        if item["comparability"] == "comparable":
            reasons = set(item["unresolved_reasons"])
            assert not set(REQUIRED_COMPARISON_REASONS) & reasons
            assert not set(PEER_COMPARISON_REASONS) & reasons
            assert item["peer_locators"]
            assert str(item["evidence"]["calendar_reporting_basis"]).strip()
        elif item["status"] == "supported" and item["comparability"] == "unresolved":
            assert item["unresolved_reasons"]
        assert item["locator"] not in item["peer_locators"]
    outside = [
        item
        for item in admission["assessments"]["items"]
        if item["status"] == "outside_scope"
    ]
    assert len(outside) == 107
    assert all(item["comparability"] == "outside_scope" for item in outside)
    assert not (annual_out / "management_kpi_admission.json").exists()
    mixed_std = json.loads((mixed_out / "standardized.json").read_text(encoding="utf-8"))
    annual_std = json.loads((annual_out / "standardized.json").read_text(encoding="utf-8"))
    assert _canonicalize(mixed_std) == _canonicalize(annual_std)
    assert "assessments" not in json.loads(
        (mixed_out / "conflicts.json").read_text(encoding="utf-8")
    )
    assert _bytes_by_name(EXTRACTED) == before
