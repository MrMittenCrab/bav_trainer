"""Step 9M.2 — Lululemon real-company benchmark baseline acceptance."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from core.data.standardized_io import standardized_from_payload
from core.ingestion.filing_json import load_extracted_filing
from core.ingestion.filing_validator import validate_extracted_filing
from core.model.classification import (
    UnclassifiedBalanceSheetLineError,
    classify_balance_sheet_line,
    is_balance_sheet_subtotal,
)
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"

SOURCE_PDFS = {
    2022: (
        "LULU_FY2022_Annual_Report.pdf",
        "b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e",
        4913067,
    ),
    2023: (
        "LULU_FY2023_Annual_Report.pdf",
        "cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1",
        5848446,
    ),
    2024: (
        "LULU_FY2024_Annual_Report.pdf",
        "9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec",
        5953217,
    ),
    2025: (
        "LULU_FY2025_Annual_Report.pdf",
        "82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc",
        6590658,
    ),
}

EXPECTED_PERIODS = [
    date(2023, 1, 29),
    date(2024, 1, 28),
    date(2025, 2, 2),
    date(2026, 2, 1),
]

REVENUE_ANCHORS = {
    date(2023, 1, 29): 8110518.0,
    date(2024, 1, 28): 9619278.0,
    date(2025, 2, 2): 10588126.0,
    date(2026, 2, 1): 11102600.0,
}

DILUTED_WAS_ANCHORS = {
    date(2023, 1, 29): 128017.0,
    date(2024, 1, 28): 127060.0,
    date(2025, 2, 2): 123935.0,
    date(2026, 2, 1): 119068.0,
}

BUILD_BLOCKER_LABELS = {
    "Unredeemed gift card liability",
    "Property and equipment, net",
    "Common stock",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_four_filings_validate_and_remain_source_bound():
    files = sorted(EXTRACTED.glob("LULU_FY*.json"))
    assert {int(p.stem.replace("LULU_FY", "")) for p in files} == {2022, 2023, 2024, 2025}

    for fiscal_year, (pdf_name, digest, nbytes) in SOURCE_PDFS.items():
        pdf = SOURCE / pdf_name
        assert pdf.is_file()
        data = pdf.read_bytes()
        assert len(data) == nbytes
        assert hashlib.sha256(data).hexdigest() == digest

        extracted = EXTRACTED / f"LULU_FY{fiscal_year}.json"
        filing = load_extracted_filing(extracted)
        assert filing.schema_version == "1.0"
        assert filing.filing.fiscal_year == fiscal_year
        assert filing.filing.source_file == pdf_name
        assert filing.income_statement
        assert filing.balance_sheet
        assert filing.cash_flow

        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        assert report.computed_source_sha256 == digest
        assert report.warnings == ()


def _reconcile_cmd(out: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "core",
        "reconcile",
        str(EXTRACTED),
        "--source-root",
        str(SOURCE),
        "-o",
        str(out),
    ]


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return env


ARTIFACT_NAMES = ("standardized.json", "provenance.json", "conflicts.json")


def _read_committed_artifacts() -> dict[str, bytes]:
    return {name: (RECONCILED / name).read_bytes() for name in ARTIFACT_NAMES}


def _assert_artifact_sets_match(
    generated: Path,
    expected_bytes: dict[str, bytes],
) -> None:
    """Compare generated artifacts to expected bytes; never write expected paths."""
    mismatches: list[str] = []
    for name in ARTIFACT_NAMES:
        actual = (generated / name).read_bytes()
        if actual != expected_bytes[name]:
            mismatches.append(name)
    if mismatches:
        raise AssertionError(
            "reconciliation artifact mismatch: " + ", ".join(mismatches)
        )


def test_generic_reconcile_is_deterministic(tmp_path: Path):
    committed_before = _read_committed_artifacts()

    out1 = tmp_path / "r1"
    out2 = tmp_path / "r2"
    for out in (out1, out2):
        completed = subprocess.run(
            _reconcile_cmd(out),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            env=_subprocess_env(),
        )
        assert "overlap_conflicts=" in completed.stdout

    for name in ARTIFACT_NAMES:
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()

    _assert_artifact_sets_match(out1, committed_before)
    _assert_artifact_sets_match(out2, committed_before)

    committed_after = _read_committed_artifacts()
    assert committed_after == committed_before


@pytest.mark.parametrize("drifted_name", ARTIFACT_NAMES)
def test_reconcile_drift_is_detected_without_rewriting_expected(
    tmp_path: Path, drifted_name: str
):
    """Altering a temp expected copy must fail comparison and leave that copy intact."""
    expected_dir = tmp_path / "expected"
    expected_dir.mkdir()
    for name in ARTIFACT_NAMES:
        (expected_dir / name).write_bytes((RECONCILED / name).read_bytes())

    drifted_path = expected_dir / drifted_name
    original_expected = drifted_path.read_bytes()
    drifted_path.write_bytes(original_expected + b"\n#drift\n")
    altered_expected = drifted_path.read_bytes()
    assert altered_expected != original_expected

    expected_bytes = {name: (expected_dir / name).read_bytes() for name in ARTIFACT_NAMES}

    out = tmp_path / "generated"
    completed = subprocess.run(
        _reconcile_cmd(out),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert "overlap_conflicts=" in completed.stdout

    with pytest.raises(AssertionError, match=drifted_name):
        _assert_artifact_sets_match(out, expected_bytes)

    assert drifted_path.read_bytes() == altered_expected
    for name in ARTIFACT_NAMES:
        if name == drifted_name:
            continue
        assert (expected_dir / name).read_bytes() == (RECONCILED / name).read_bytes()


def test_reconciled_axis_anchors_and_conflicts():
    payload = _load_json(STD_JSON)
    provenance = _load_json(PROV_JSON)
    conflicts = _load_json(CONFLICTS_JSON)
    fin = standardized_from_payload(payload)

    assert fin.ticker == "LULU"
    assert fin.company_name == "lululemon athletica inc."
    assert fin.currency == "USD"
    assert fin.units == "USD in Thousands"
    assert fin.jurisdiction == "US"
    assert [p.end_date for p in fin.periods] == EXPECTED_PERIODS

    # Four FY2022–FY2025 filing year-ends are on the axis. Earlier comparative
    # IS dates present in extracted filings are not promoted onto the canonical axis.
    assert len(fin.periods) == 4

    revenue = next(item for item in fin.income_statement if item.concept == "revenue")
    assert {p: revenue.values[p] for p in EXPECTED_PERIODS} == REVENUE_ANCHORS

    assert fin.historical_shares is not None
    assert fin.historical_shares.scale_basis == "financial_statement_units"
    assert fin.historical_shares.basis == "reported"
    assert fin.historical_shares.diluted_weighted_average == DILUTED_WAS_ANCHORS

    assert conflicts["overlap_conflict_count"] == 3
    assert conflicts["supplemental_conflict_count"] == 0
    assert len(conflicts["conflicts"]) == 3

    source_files = provenance["source_files"]
    assert len(source_files) == 4
    by_year = {entry["filing_year"]: entry for entry in source_files}
    assert set(by_year) == {2022, 2023, 2024, 2025}
    for year, (pdf_name, digest, _) in SOURCE_PDFS.items():
        assert by_year[year]["source_file"] == pdf_name
        assert by_year[year]["source_sha256"] == digest


def test_build_blocker_is_unclassified_balance_sheet_lines(tmp_path: Path):
    """Current generic build is blocked before any LULU-specific fix.

    First raise is Unredeemed gift card liability; PPE and Common stock also
    fail closed under the same generic classifier.
    """
    fin = standardized_from_payload(_load_json(STD_JSON))

    unclassified = set()
    for item in fin.balance_sheet:
        if is_balance_sheet_subtotal(item):
            continue
        try:
            classify_balance_sheet_line(item)
        except UnclassifiedBalanceSheetLineError:
            unclassified.add(item.label)
    assert unclassified == BUILD_BLOCKER_LABELS

    out = tmp_path / "Lululemon"
    with pytest.raises(UnclassifiedBalanceSheetLineError, match="Unredeemed gift card liability"):
        build_training_workbook(fin, out)


def test_no_lulu_specific_production_branch():
    """Production engine must stay generic — no ticker/issuer hard-codes."""
    core_root = ROOT / "core"
    offenders: list[str] = []
    for path in core_root.rglob("*.py"):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for token in ("LULU", "lululemon", "Lululemon"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")
    assert offenders == []


def test_committed_reconciled_hashes_are_stable():
    """Lock measured baseline artifact digests for Step 9M.2."""
    assert _sha256(STD_JSON) == (
        "ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45"
    )
    assert _sha256(CONFLICTS_JSON) == (
        "d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0"
    )
    # provenance is large; lock size + digest together
    assert PROV_JSON.stat().st_size == 698793
    assert _sha256(PROV_JSON) == (
        "2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269"
    )
