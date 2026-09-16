"""Tests for ExtractedFiling JSON loader and source validation."""

from __future__ import annotations

import copy
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


@pytest.mark.parametrize(
    "role",
    [
        PresentationRole.CURRENT_PERIOD.value,
        PresentationRole.COMPARATIVE.value,
        PresentationRole.RESTATED_COMPARATIVE.value,
        PresentationRole.PRIOR_PRESENTATION.value,
    ],
)
def test_geographic_note_fact_round_trip_preserves_presentation_role(
    tmp_path: Path, role: str
):
    payload = _minimal_filing_payload()
    payload["note_facts"] = [
        {
            "fact_type": "segment.geo.q4_2023.net_revenue.americas",
            "period": "2025-08-31",
            "value": 100,
            "status": "reported",
            "source": {"page": 80, "note": "24 Segmented Information", "label": "Americas"},
            "presentation_role": role,
        }
    ]
    path = tmp_path / "geo.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    assert filing.note_facts[0].presentation_role == role
    assert filing.note_facts[0].fact_type.endswith("net_revenue.americas")
    dumped = extracted_filing_to_payload(filing)
    assert dumped["note_facts"][0]["presentation_role"] == role
    round_path = tmp_path / "geo-round.json"
    round_path.write_text(json.dumps(dumped, indent=2) + "\n", encoding="utf-8")
    reloaded = load_extracted_filing(round_path)
    assert extracted_filing_to_payload(reloaded) == dumped


@pytest.mark.parametrize("unit", ["stores", "ones"])
def test_operating_kpi_note_fact_round_trip_preserves_unit(tmp_path: Path, unit: str):
    payload = _minimal_filing_payload()
    payload["note_facts"] = [
        {
            "fact_type": "kpi.operating.store_count.company_operated",
            "period": "2025-08-31",
            "value": 655,
            "status": "reported",
            "unit": unit,
            "source": {
                "page": 7,
                "note": "Company-Operated Stores",
                "label": "Total company-operated stores",
            },
            "presentation_role": "current_period",
        }
    ]
    path = tmp_path / "kpi.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    assert filing.note_facts[0].unit == unit
    assert filing.note_facts[0].value == 655
    dumped = extracted_filing_to_payload(filing)
    assert dumped["note_facts"][0]["unit"] == unit
    assert dumped["note_facts"][0]["value"] == 655
    assert dumped["note_facts"][0]["source"]["label"] == "Total company-operated stores"
    assert dumped["note_facts"][0]["source"]["note"] == "Company-Operated Stores"
    round_path = tmp_path / "kpi-round.json"
    round_path.write_text(json.dumps(dumped, indent=2) + "\n", encoding="utf-8")
    reloaded = load_extracted_filing(round_path)
    assert extracted_filing_to_payload(reloaded) == dumped
    assert reloaded.note_facts[0].source.label == "Total company-operated stores"
    assert reloaded.note_facts[0].source.note == "Company-Operated Stores"
    legacy = _minimal_filing_payload()
    legacy_path = tmp_path / "legacy.json"
    legacy_path.write_text(json.dumps(legacy, indent=2) + "\n", encoding="utf-8")
    legacy_filing = load_extracted_filing(legacy_path)
    legacy_dump = extracted_filing_to_payload(legacy_filing)
    assert all("unit" not in fact for fact in legacy_dump["note_facts"])
    assert legacy_dump["note_facts"] == []


def _write_minimal_source(tmp_path: Path) -> Path:
    source_root = tmp_path / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "Fastretailing_CFS2025.pdf").write_bytes(b"%PDF-kpi-label")
    return source_root


_OMIT = object()
_NON_STRING_LABELS = (
    pytest.param(123, id="int-123"),
    pytest.param(1.5, id="float-1.5"),
    pytest.param(0, id="int-0"),
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param({"x": 1}, id="nonempty-object"),
    pytest.param({}, id="empty-object"),
    pytest.param([1], id="nonempty-array"),
    pytest.param([], id="empty-array"),
)


@pytest.mark.parametrize(
    "label",
    [
        pytest.param(_OMIT, id="omitted"),
        pytest.param(None, id="null"),
        pytest.param("", id="empty"),
        pytest.param(" \t ", id="whitespace"),
    ],
)
@pytest.mark.parametrize(
    "note",
    [
        pytest.param("Company-Operated Stores", id="note-populated"),
        pytest.param(_OMIT, id="note-absent"),
    ],
)
def test_operating_kpi_missing_label_fails_validation_after_reload(
    tmp_path: Path, label, note
):
    source_root = _write_minimal_source(tmp_path)
    payload = _minimal_filing_payload()
    source = {"page": 7}
    if note is not _OMIT:
        source["note"] = note
    if label is not _OMIT:
        source["label"] = label
    payload["note_facts"] = [
        {
            "fact_type": "kpi.operating.store_count.company_operated",
            "period": "2025-08-31",
            "value": 655,
            "status": "reported",
            "unit": "stores",
            "source": source,
            "presentation_role": "current_period",
        }
    ]
    original = copy.deepcopy(payload)
    path = tmp_path / "kpi-missing-label.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert not report.ok
    assert any(
        issue.code == "invalid_operating_kpi"
        and "missing reported label" in issue.message
        for issue in report.errors
    )
    assert json.loads(path.read_text(encoding="utf-8")) == original


def test_operating_kpi_review_reproduction_omits_label_and_note(tmp_path: Path):
    source_root = _write_minimal_source(tmp_path)
    payload = _minimal_filing_payload()
    observation = {
        "fact_type": "kpi.operating.store_count.company_operated",
        "period": "2025-08-31",
        "value": 655,
        "status": "reported",
        "unit": "stores",
        "source": {
            "page": 7,
            "note": "Company-Operated Stores",
            "label": "Total company-operated stores",
        },
        "presentation_role": "current_period",
    }
    observation["source"].pop("label")
    observation["source"].pop("note")
    payload["note_facts"] = [observation]
    original = copy.deepcopy(payload)
    path = tmp_path / "kpi-review-repro.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert not report.ok
    assert any("missing reported label" in issue.message for issue in report.errors)
    assert json.loads(path.read_text(encoding="utf-8")) == original


@pytest.mark.parametrize("label", _NON_STRING_LABELS)
@pytest.mark.parametrize(
    "note",
    [
        pytest.param("Company-Operated Stores", id="note-populated"),
        pytest.param(_OMIT, id="note-absent"),
    ],
)
@pytest.mark.parametrize("bucket", ["note_facts", "share_facts"])
def test_operating_kpi_non_string_label_rejected_before_parse_coercion(
    tmp_path: Path, label, note, bucket
):
    payload = _minimal_filing_payload()
    source = {"page": 7}
    if note is not _OMIT:
        source["note"] = note
    source["label"] = label
    payload[bucket] = [
        {
            "fact_type": "kpi.operating.store_count.company_operated",
            "period": "2025-08-31",
            "value": 655,
            "status": "reported",
            "unit": "stores",
            "source": source,
            "presentation_role": "current_period",
        }
    ]
    original = copy.deepcopy(payload)
    path = tmp_path / "kpi-non-string-label.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing reported label"):
        load_extracted_filing(path)
    assert json.loads(path.read_text(encoding="utf-8")) == original


def test_non_kpi_non_string_label_still_coerced(tmp_path: Path):
    source_root = _write_minimal_source(tmp_path)
    payload = _minimal_filing_payload()
    payload["note_facts"] = [
        {
            "fact_type": "lease_interest_expense",
            "period": "2025-08-31",
            "value": 12,
            "status": "reported",
            "source": {"page": 14, "note": "17 Leases", "label": 123},
        }
    ]
    payload["statements"]["income_statement"][0]["source"]["label"] = 99
    path = tmp_path / "lease-coerced-label.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert report.ok
    assert filing.note_facts[0].source.label == "123"
    assert filing.income_statement[0].source.label == "99"
    dumped = extracted_filing_to_payload(filing)
    assert dumped["note_facts"][0]["source"]["label"] == "123"
    assert dumped["statements"]["income_statement"][0]["source"]["label"] == "99"


def test_unrelated_supplemental_without_label_still_validates(tmp_path: Path):
    source_root = _write_minimal_source(tmp_path)
    payload = _minimal_filing_payload()
    payload["note_facts"] = [
        {
            "fact_type": "lease_interest_expense",
            "period": "2025-08-31",
            "value": 12,
            "status": "reported",
            "source": {"page": 14, "note": "17 Leases"},
        }
    ]
    path = tmp_path / "lease.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    filing = load_extracted_filing(path)
    report = validate_extracted_filing(filing, source_root=source_root)
    assert report.ok
    dumped = extracted_filing_to_payload(filing)
    assert "label" not in dumped["note_facts"][0]["source"]
    assert dumped["note_facts"][0]["source"]["note"] == "17 Leases"
