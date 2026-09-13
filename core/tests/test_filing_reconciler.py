"""Tests for cross-filing reconciliation and standardization."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import pytest

from core.data.filing import (
    ExtractedFiling,
    ExtractedStatementRow,
    FilingMetadata,
    FilingValue,
    PresentationRole,
    SourceRef,
    SupplementalFact,
)
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.filing_validator import FilingValidationReport, validate_extracted_filing


def _write_source(tmp_path: Path, name: str, payload: bytes) -> str:
    root = tmp_path / "source"
    root.mkdir(exist_ok=True)
    (root / name).write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _filing(
    *,
    year: int,
    source_file: str,
    revenue_values: dict[date, tuple[float, PresentationRole]],
    company_name: str = "ACME",
    ticker: str = "ACME",
    stock_code: str = "ACME",
    jurisdiction: str = "HK",
    currency: str = "HKD",
    unit_scale: str = "millions",
    note_facts: tuple[SupplementalFact, ...] = (),
    share_facts: tuple[SupplementalFact, ...] = (),
    extra_rows: tuple[ExtractedStatementRow, ...] = (),
) -> ExtractedFiling:
    period_end = date(year, 12, 31)
    return ExtractedFiling(
        schema_version="1.0",
        company_name=company_name,
        ticker=ticker,
        stock_code=stock_code,
        jurisdiction=jurisdiction,
        filing=FilingMetadata(
            document_type="annual_report",
            fiscal_year=year,
            period_end=period_end,
            currency=currency,
            unit_scale=unit_scale,
            source_file=source_file,
        ),
        income_statement=(
            ExtractedStatementRow(
                label="Revenue",
                section="",
                suggested_concept="revenue",
                values={
                    period: FilingValue(value=value, presentation_role=role)
                    for period, (value, role) in revenue_values.items()
                },
                source=SourceRef(page=1, statement="Income Statement"),
            ),
            *extra_rows,
        ),
        balance_sheet=(),
        cash_flow=(),
        note_facts=note_facts,
        share_facts=share_facts,
    )


def _validated(tmp_path: Path, filing: ExtractedFiling, blob: bytes):
    _write_source(tmp_path, filing.filing.source_file, blob)
    report = validate_extracted_filing(filing, source_root=tmp_path / "source")
    assert report.ok
    return filing, report


def test_matching_comparative_no_conflict(tmp_path: Path):
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fy2024 = next(
        v
        for v in reconciled.values
        if v.period == date(2024, 12, 31) and "revenue" in v.row_identity
    )
    assert fy2024.selected.value == 100.0
    assert len(fy2024.observations) == 2
    assert reconciled.conflicts == ()


def test_later_comparative_conflict(tmp_path: Path):
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (101.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    conflicts = [c for c in reconciled.conflicts if c.period == date(2024, 12, 31)]
    assert len(conflicts) == 1
    assert conflicts[0].selected.value == 101.0
    assert conflicts[0].reason == "later_audited_presentation"


def test_restated_comparative_precedence(tmp_path: Path):
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (101.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    # Inject restated observation via a third overlapping role on same filing by
    # using an additional validated filing year that carries restated_comparative.
    f2025_restated = _filing(
        year=2025,
        source_file="a2025b.pdf",
        revenue_values={
            date(2024, 12, 31): (99.0, PresentationRole.RESTATED_COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
            _validated(tmp_path, f2025_restated, b"2025b"),
        ]
    )
    conflict = next(c for c in reconciled.conflicts if c.period == date(2024, 12, 31))
    assert conflict.selected.value == 99.0
    assert conflict.reason == "restated_comparative_precedence"


def test_prior_presentation_never_overrides(tmp_path: Path):
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (999.0, PresentationRole.PRIOR_PRESENTATION),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fy2024 = next(v for v in reconciled.values if v.period == date(2024, 12, 31))
    assert fy2024.selected.value == 100.0
    assert fy2024.selected.presentation_role == PresentationRole.CURRENT_PERIOD


def test_metadata_incompatibility(tmp_path: Path):
    base = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
    )
    other = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        currency="USD",
    )
    with pytest.raises(ValueError, match="currency"):
        reconcile_filings(
            [
                _validated(tmp_path, base, b"2024"),
                _validated(tmp_path, other, b"2025"),
            ]
        )


def test_standardize_complete_axis_and_omission(tmp_path: Path):
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD),
        },
        extra_rows=(
            ExtractedStatementRow(
                label="Only 2024",
                section="",
                suggested_concept="only_2024",
                values={
                    date(2024, 12, 31): FilingValue(
                        1.0, PresentationRole.CURRENT_PERIOD
                    )
                },
                source=SourceRef(page=2),
            ),
        ),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        extra_rows=(
            ExtractedStatementRow(
                label="Only 2025",
                section="",
                suggested_concept="only_2025",
                values={
                    date(2025, 12, 31): FilingValue(
                        2.0, PresentationRole.CURRENT_PERIOD
                    )
                },
                source=SourceRef(page=2),
            ),
        ),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fin = standardize_reconciled(reconciled)
    assert len(fin.income_statement) == 1
    revenue = fin.income_statement[0]
    assert revenue.concept == "revenue"
    assert revenue.label == "Revenue"
    assert revenue.values == {
        date(2024, 12, 31): 100.0,
        date(2025, 12, 31): 110.0,
    }
    provenance = reconciliation_provenance_payload(reconciled)
    assert any(
        item["status"] == "omitted_incomplete_axis"
        and "only_2025" in item["row_identity"]
        for item in provenance["omitted_incomplete_axis"]
    )


def test_note_facts_not_promoted(tmp_path: Path):
    note = SupplementalFact(
        fact_type="lease_liability_total",
        period=date(2025, 12, 31),
        value=513501,
        status="reported",
        source=SourceRef(page=14, note="17 Leases", label="Total"),
    )
    derived = SupplementalFact(
        fact_type="lease_liability_total_derived",
        period=date(2025, 12, 31),
        value=999,
        status="derived",
        source=SourceRef(page=14, note="17 Leases"),
        derivation="current + noncurrent",
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(note, derived),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fin = standardize_reconciled(reconciled)
    assert fin.balance_sheet == []
    assert all(item.concept != "lease_liability_total" for item in fin.balance_sheet)
    provenance = reconciliation_provenance_payload(reconciled)
    assert any(f["fact_type"] == "lease_liability_total" for f in provenance["note_facts"])


def test_historical_share_gating(tmp_path: Path):
    shares = (
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2025, 12, 31),
            value=100.0,
            status="reported",
            source=SourceRef(page=18, note="EPS"),
        ),
        SupplementalFact(
            fact_type="basic_weighted_average_shares",
            period=date(2024, 12, 31),
            value=90.0,
            status="reported",
            source=SourceRef(page=18, note="EPS"),
        ),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=shares,
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is None
    conflicts = reconciliation_conflicts_payload(reconciled)
    assert conflicts["overlap_conflict_count"] == 0
