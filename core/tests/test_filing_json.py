"""Tests for ExtractedFiling JSON loader and source validation."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.filing import PresentationRole
from core.ingestion.filing_json import extracted_filing_to_payload, load_extracted_filing
from core.ingestion.filing_validator import (
    source_row_identity,
    validate_extracted_filing,
)


def _minimal_filing_payload(**overrides) -> dict:
    payload = {
        "schema_version": "1.0",
        "company": {
            "name": "FAST RETAILING CO., LTD.",
            "ticker": "6288.HK",
            "stock_code": "6288.HK",
            "jurisdiction": "JP",
        },
        "filing": {
            "document_type": "annual_report",
            "fiscal_year": 2025,
            "period_end": "2025-08-31",
            "currency": "JPY",
            "unit_scale": "millions",
            "source_file": "Fastretailing_CFS2025.pdf",
        },
        "statements": {
            "income_statement": [
                {
                    "label": "Revenue",
                    "section": "",
                    "suggested_concept": "revenue",
                    "values": {
                        "2025-08-31": {
                            "value": 3400539,
                            "presentation_role": "current_period",
                        }
                    },
                    "source": {
                        "page": 3,
                        "statement": "Consolidated Statement of Profit or Loss",
                    },
                }
            ],
            "balance_sheet": [
                {
                    "label": "Lease liabilities",
                    "section": "Current liabilities",
                    "suggested_concept": "lease_liability_current",
                    "values": {
                        "2025-08-31": {
                            "value": 126830,
                            "presentation_role": "current_period",
                        }
                    },
                    "source": {
                        "page": 2,
                        "statement": "Consolidated Statement of Financial Position",
                    },
                }
            ],
            "cash_flow": [],
        },
        "note_facts": [],
        "share_facts": [],
    }
    payload.update(overrides)
    return payload


def test_round_trip_omits_source_sha256(tmp_path: Path):
    path = tmp_path / "FY2025.json"
    payload = _minimal_filing_payload()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    filing = load_extracted_filing(path)
    assert filing.schema_version == "1.0"
    assert filing.filing.period_end == date(2025, 8, 31)
    assert filing.income_statement[0].values[date(2025, 8, 31)].value == 3_400_539
    assert filing.balance_sheet[0].section == "Current liabilities"
    assert filing.filing.source_sha256 == ""
    assert extracted_filing_to_payload(filing) == json.loads(path.read_text())


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda p: p.__setitem__("schema_version", "2.0"), "schema_version"),
        (
            lambda p: p["filing"].__setitem__("document_type", "10-K"),
            "document_type",
        ),
        (
            lambda p: p["filing"].__setitem__("unit_scale", "yen"),
            "unit_scale",
        ),
        (
            lambda p: p["filing"].__setitem__("period_end", "31 August 2025"),
            "invalid date",
        ),
        (
            lambda p: p["statements"]["income_statement"][0]["values"][
                "2025-08-31"
            ].__setitem__("presentation_role", "restated"),
            "presentation_role",
        ),
        (
            lambda p: p["statements"]["income_statement"][0]["values"][
                "2025-08-31"
            ].__setitem__("value", "3400539"),
            "numeric",
        ),
        (
            lambda p: p["statements"]["income_statement"][0]["source"].__setitem__(
                "page", 0
            ),
            "page",
        ),
        (
            lambda p: p.__setitem__(
                "note_facts",
                [
                    {
                        "fact_type": "lease_liability_total",
                        "period": "2025-08-31",
                        "value": 513501,
                        "status": "invented",
                        "source": {"page": 14, "note": "17 Leases"},
                    }
                ],
            ),
            "status",
        ),
        (
            lambda p: p.__setitem__(
                "note_facts",
                [
                    {
                        "fact_type": "lease_liability_total",
                        "period": "2025-08-31",
                        "value": 513501,
                        "status": "derived",
                        "source": {"page": 14, "note": "17 Leases"},
                    }
                ],
            ),
            "derivation",
        ),
    ],
)
def test_parser_rejects_malformed_filings(tmp_path: Path, mutate, match):
    payload = _minimal_filing_payload()
    mutate(payload)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_extracted_filing(path)


def test_validate_computes_source_hash(tmp_path: Path):
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_bytes = b"%PDF-fake-fast-retailing"
    (source_root / "Fastretailing_CFS2025.pdf").write_bytes(source_bytes)

    path = tmp_path / "FY2025.json"
    path.write_text(json.dumps(_minimal_filing_payload()), encoding="utf-8")
    filing = load_extracted_filing(path)

    report = validate_extracted_filing(filing, source_root=source_root)
    assert report.ok
    assert report.computed_source_sha256 == hashlib.sha256(source_bytes).hexdigest()


def test_validate_source_hash_mismatch_and_missing(tmp_path: Path):
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "Fastretailing_CFS2025.pdf").write_bytes(b"abc")

    payload = _minimal_filing_payload()
    payload["filing"]["source_sha256"] = "0" * 64
    path = tmp_path / "FY2025.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)

    report = validate_extracted_filing(filing, source_root=source_root)
    assert not report.ok
    assert any(i.code == "source_hash_mismatch" for i in report.errors)

    missing = validate_extracted_filing(
        filing, source_root=tmp_path / "missing_root"
    )
    assert any(i.code == "source_file_missing" for i in missing.errors)


def test_source_row_identity_distinguishes_lease_sections(tmp_path: Path):
    payload = _minimal_filing_payload()
    payload["statements"]["balance_sheet"] = [
        {
            "label": "Lease liabilities",
            "section": "Current liabilities",
            "suggested_concept": "lease_liability_current",
            "values": {
                "2025-08-31": {
                    "value": 126830,
                    "presentation_role": "current_period",
                }
            },
            "source": {"page": 2},
        },
        {
            "label": "Lease liabilities",
            "section": "Non-current liabilities",
            "suggested_concept": "lease_liability_noncurrent",
            "values": {
                "2025-08-31": {
                    "value": 386670,
                    "presentation_role": "current_period",
                }
            },
            "source": {"page": 2},
        },
    ]
    path = tmp_path / "FY2025.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    current = source_row_identity("balance_sheet", filing.balance_sheet[0])
    noncurrent = source_row_identity("balance_sheet", filing.balance_sheet[1])
    assert current != noncurrent
    assert "current liabilities" in current
    assert "non-current liabilities" in noncurrent

    # Duplicate indistinguishable identity
    payload["statements"]["balance_sheet"].append(
        dict(payload["statements"]["balance_sheet"][0])
    )
    path.write_text(json.dumps(payload), encoding="utf-8")
    dup = load_extracted_filing(path)
    report = validate_extracted_filing(dup)
    assert any(i.code == "duplicate_source_row_identity" for i in report.errors)


def test_current_period_consistency(tmp_path: Path):
    payload = _minimal_filing_payload()
    payload["statements"]["income_statement"][0]["values"] = {
        "2024-08-31": {
            "value": 3103836,
            "presentation_role": "current_period",
        }
    }
    path = tmp_path / "bad_period.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing)
    assert any(i.code == "current_period_mismatch" for i in report.errors)

    payload = _minimal_filing_payload()
    payload["statements"]["income_statement"][0]["values"] = {
        "2024-08-31": {
            "value": 3103836,
            "presentation_role": "comparative",
        }
    }
    payload["statements"]["balance_sheet"] = []
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing)
    assert any(i.code == "current_period_missing" for i in report.errors)
    assert filing.income_statement[0].values[
        date(2024, 8, 31)
    ].presentation_role == PresentationRole.COMPARATIVE


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda p: p.pop("company", None), "company"),
        (lambda p: p.__setitem__("company", "not-an-object"), "company"),
        (lambda p: p["company"].__setitem__("name", ""), r"company\.name"),
        (lambda p: p["company"].__setitem__("name", "   "), r"company\.name"),
        (lambda p: p["company"].__setitem__("ticker", ""), "ticker"),
        (lambda p: p["company"].__setitem__("jurisdiction", ""), "jurisdiction"),
        (lambda p: p["filing"].__delitem__("fiscal_year"), "fiscal_year"),
        (lambda p: p["filing"].__setitem__("fiscal_year", True), "fiscal_year"),
        (lambda p: p["filing"].__setitem__("fiscal_year", 0), "fiscal_year"),
        (lambda p: p["filing"].__setitem__("fiscal_year", "2025"), "fiscal_year"),
        (lambda p: p["filing"].__delitem__("period_end"), "period_end"),
        (lambda p: p["filing"].__setitem__("currency", ""), "currency"),
        (lambda p: p["filing"].__setitem__("source_file", ""), "source_file"),
        (lambda p: p["filing"].__setitem__("source_file", "   "), "source_file"),
    ],
)
def test_parser_rejects_missing_required_fields(tmp_path: Path, mutate, match):
    payload = _minimal_filing_payload()
    mutate(payload)
    if isinstance(payload.get("company"), dict):
        # Empty stock_code remains allowed.
        payload["company"]["stock_code"] = ""
    path = tmp_path / "required.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_extracted_filing(path)


@pytest.mark.parametrize(
    "bad_date",
    [
        "2025-08-31junk",
        "2025-08-31T00:00:00",
        "2025/08/31",
        "2025-02-30",
    ],
)
def test_parser_rejects_non_exact_iso_dates(tmp_path: Path, bad_date: str):
    payload = _minimal_filing_payload()
    payload["filing"]["period_end"] = bad_date
    path = tmp_path / "bad_date.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid date"):
        load_extracted_filing(path)


def test_parser_accepts_exact_iso_date(tmp_path: Path):
    payload = _minimal_filing_payload()
    payload["filing"]["period_end"] = "2025-08-31"
    path = tmp_path / "exact_date.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    assert filing.filing.period_end == date(2025, 8, 31)


def test_parser_allows_empty_stock_code(tmp_path: Path):
    payload = _minimal_filing_payload()
    payload["company"]["stock_code"] = ""
    path = tmp_path / "ticker_only.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    assert filing.stock_code == ""
    assert filing.ticker == "6288.HK"


@pytest.mark.parametrize(
    "source_file",
    [
        "/Users/name/report.pdf",
        "../report.pdf",
        "subdir/../../report.pdf",
        r"C:\Users\name\report.pdf",
    ],
)
def test_validate_rejects_escaping_source_paths(tmp_path: Path, source_file: str):
    source_root = tmp_path / "source"
    source_root.mkdir()
    # Place a file outside the root that a naive join might still reach.
    outside = tmp_path / "report.pdf"
    outside.write_bytes(b"%PDF-outside")
    nested = source_root / "subdir"
    nested.mkdir()

    payload = _minimal_filing_payload()
    payload["filing"]["source_file"] = source_file
    path = tmp_path / "escape.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert not report.ok
    assert any(i.code == "invalid_source_path" for i in report.errors)
    assert report.computed_source_sha256 is None


def test_validate_allows_nested_relative_source_path(tmp_path: Path):
    source_root = tmp_path / "source"
    nested = source_root / "annual"
    nested.mkdir(parents=True)
    blob = b"%PDF-nested"
    (nested / "FY2025.pdf").write_bytes(blob)

    payload = _minimal_filing_payload()
    payload["filing"]["source_file"] = "annual/FY2025.pdf"
    path = tmp_path / "nested.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert report.ok
    assert report.computed_source_sha256 == hashlib.sha256(blob).hexdigest()
