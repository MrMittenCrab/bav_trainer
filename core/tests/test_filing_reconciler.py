"""Tests for cross-filing reconciliation and standardization."""

from __future__ import annotations

import copy
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
    balance_sheet_rows: tuple[ExtractedStatementRow, ...] = (),
    cash_flow_rows: tuple[ExtractedStatementRow, ...] = (),
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
        balance_sheet=balance_sheet_rows,
        cash_flow=cash_flow_rows,
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


def test_complete_bound_source_registry_retains_losers_and_supplemental_only(
    tmp_path: Path,
):
    """Every validated bound filing stays in the registry, even without selections."""
    # All of FY2024's statement observations lose to FY2025; note fact remains.
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            date(2024, 12, 31): (90.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(
            SupplementalFact(
                fact_type="lease_liability_total",
                period=date(2024, 12, 31),
                value=10.0,
                status="reported",
                source=SourceRef(page=7, note="17 Leases"),
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
    )
    pair_2024 = _validated(tmp_path, f2024, b"2024")
    pair_2025 = _validated(tmp_path, f2025, b"2025")
    reconciled = reconcile_filings([pair_2024, pair_2025])

    assert {(s.filing_year, s.source_file) for s in reconciled.source_files} == {
        (2024, "a2024.pdf"),
        (2025, "a2025.pdf"),
    }
    assert all(s.source_sha256 for s in reconciled.source_files)

    selected_files = {v.selected.source_file for v in reconciled.values}
    assert selected_files == {"a2025.pdf"}
    assert any(obs.source_file == "a2024.pdf" for obs in reconciled.note_facts)

    provenance = reconciliation_provenance_payload(reconciled)
    registry = {
        (item["filing_year"], item["source_file"], item["source_sha256"])
        for item in provenance["source_files"]
    }
    expected = {
        (bound.filing_year, bound.source_file, bound.source_sha256)
        for bound in reconciled.source_files
    }
    assert registry == expected
    assert len(provenance["source_files"]) == 2
    for item in provenance["source_files"]:
        assert item["filing_year"]
        assert item["source_file"]
        assert item["source_sha256"]
    # Selected-only reconstruction would omit a2024.pdf entirely.
    assert "a2024.pdf" not in selected_files


def _assert_observation_fields(obs, *, filing_year, source_file, source_sha256, pdf_page, role, value):
    assert obs.filing_year == filing_year
    assert obs.source_file == source_file
    assert obs.source_sha256 == source_sha256
    assert obs.pdf_page == pdf_page
    assert obs.presentation_role == role
    assert obs.value == value


def _assert_observation_payload(payload, *, filing_year, source_file, source_sha256, pdf_page, role, value):
    assert payload["filing_year"] == filing_year
    assert payload["source_file"] == source_file
    assert payload["source_sha256"] == source_sha256
    assert payload["pdf_page"] == pdf_page
    assert payload["presentation_role"] == role
    assert payload["value"] == value


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
    pair_2024 = _validated(tmp_path, f2024, b"2024")
    pair_2025 = _validated(tmp_path, f2025, b"2025")
    sha_2024 = pair_2024[1].computed_source_sha256
    sha_2025 = pair_2025[1].computed_source_sha256

    def _check(order):
        reconciled = reconcile_filings(order)
        conflict = next(c for c in reconciled.conflicts if c.period == date(2024, 12, 31))
        assert conflict.selected.value == 101.0
        assert conflict.reason == "later_audited_presentation"
        assert len(conflict.observations) == 2
        by_year = {o.filing_year: o for o in conflict.observations}
        _assert_observation_fields(
            by_year[2024],
            filing_year=2024,
            source_file="a2024.pdf",
            source_sha256=sha_2024,
            pdf_page=1,
            role=PresentationRole.CURRENT_PERIOD,
            value=100.0,
        )
        _assert_observation_fields(
            by_year[2025],
            filing_year=2025,
            source_file="a2025.pdf",
            source_sha256=sha_2025,
            pdf_page=1,
            role=PresentationRole.COMPARATIVE,
            value=101.0,
        )
        _assert_observation_fields(
            conflict.selected,
            filing_year=2025,
            source_file="a2025.pdf",
            source_sha256=sha_2025,
            pdf_page=1,
            role=PresentationRole.COMPARATIVE,
            value=101.0,
        )

        conflicts_payload = reconciliation_conflicts_payload(reconciled)
        provenance = reconciliation_provenance_payload(reconciled)
        conflict_json = next(
            c for c in conflicts_payload["conflicts"] if c["period"] == "2024-12-31"
        )
        assert conflict_json["reason"] == "later_audited_presentation"
        assert conflict_json["selected"]["value"] == 101
        by_year_json = {o["filing_year"]: o for o in conflict_json["observations"]}
        _assert_observation_payload(
            by_year_json[2024],
            filing_year=2024,
            source_file="a2024.pdf",
            source_sha256=sha_2024,
            pdf_page=1,
            role="current_period",
            value=100,
        )
        _assert_observation_payload(
            by_year_json[2025],
            filing_year=2025,
            source_file="a2025.pdf",
            source_sha256=sha_2025,
            pdf_page=1,
            role="comparative",
            value=101,
        )
        prov_key = next(
            k
            for k, v in provenance["values"].items()
            if v.get("period") == "2024-12-31" and "revenue" in v.get("row_identity", "")
        )
        prov_row = provenance["values"][prov_key]
        assert prov_row["selection_rule"] == "later_audited_presentation"
        assert prov_row["selected"]["value"] == 101
        assert len(prov_row["observations"]) == 2

        conflicts_before = reconciled.conflicts
        observations_before = next(
            v.observations
            for v in reconciled.values
            if v.period == date(2024, 12, 31) and "revenue" in v.row_identity
        )
        fin = standardize_reconciled(reconciled)
        revenue = next(item for item in fin.income_statement if item.concept == "revenue")
        assert revenue.values[date(2024, 12, 31)] == 101.0
        assert revenue.values[date(2025, 12, 31)] == 110.0
        assert reconciled.conflicts == conflicts_before
        assert (
            next(
                v.observations
                for v in reconciled.values
                if v.period == date(2024, 12, 31) and "revenue" in v.row_identity
            )
            == observations_before
        )
        return conflicts_payload, provenance, conflict.selected, conflict.observations

    forward = _check([pair_2024, pair_2025])
    reversed_order = _check([pair_2025, pair_2024])
    assert forward[0] == reversed_order[0]
    assert forward[1] == reversed_order[1]
    assert forward[2] == reversed_order[2]
    assert forward[3] == reversed_order[3]


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
    pair_2024 = _validated(tmp_path, f2024, b"2024")
    pair_2025 = _validated(tmp_path, f2025, b"2025")
    pair_restated = _validated(tmp_path, f2025_restated, b"2025b")
    sha_2024 = pair_2024[1].computed_source_sha256
    sha_2025 = pair_2025[1].computed_source_sha256
    sha_restated = pair_restated[1].computed_source_sha256

    def _check(order):
        reconciled = reconcile_filings(order)
        conflict = next(c for c in reconciled.conflicts if c.period == date(2024, 12, 31))
        assert conflict.selected.value == 99.0
        assert conflict.reason == "restated_comparative_precedence"
        assert len(conflict.observations) == 3
        by_file = {(o.filing_year, o.source_file): o for o in conflict.observations}
        _assert_observation_fields(
            by_file[(2024, "a2024.pdf")],
            filing_year=2024,
            source_file="a2024.pdf",
            source_sha256=sha_2024,
            pdf_page=1,
            role=PresentationRole.CURRENT_PERIOD,
            value=100.0,
        )
        _assert_observation_fields(
            by_file[(2025, "a2025.pdf")],
            filing_year=2025,
            source_file="a2025.pdf",
            source_sha256=sha_2025,
            pdf_page=1,
            role=PresentationRole.COMPARATIVE,
            value=101.0,
        )
        _assert_observation_fields(
            by_file[(2025, "a2025b.pdf")],
            filing_year=2025,
            source_file="a2025b.pdf",
            source_sha256=sha_restated,
            pdf_page=1,
            role=PresentationRole.RESTATED_COMPARATIVE,
            value=99.0,
        )
        _assert_observation_fields(
            conflict.selected,
            filing_year=2025,
            source_file="a2025b.pdf",
            source_sha256=sha_restated,
            pdf_page=1,
            role=PresentationRole.RESTATED_COMPARATIVE,
            value=99.0,
        )

        conflicts_payload = reconciliation_conflicts_payload(reconciled)
        provenance = reconciliation_provenance_payload(reconciled)
        conflict_json = next(
            c for c in conflicts_payload["conflicts"] if c["period"] == "2024-12-31"
        )
        assert conflict_json["reason"] == "restated_comparative_precedence"
        assert conflict_json["selected"]["value"] == 99
        by_file_json = {
            (o["filing_year"], o["source_file"]): o for o in conflict_json["observations"]
        }
        _assert_observation_payload(
            by_file_json[(2024, "a2024.pdf")],
            filing_year=2024,
            source_file="a2024.pdf",
            source_sha256=sha_2024,
            pdf_page=1,
            role="current_period",
            value=100,
        )
        _assert_observation_payload(
            by_file_json[(2025, "a2025.pdf")],
            filing_year=2025,
            source_file="a2025.pdf",
            source_sha256=sha_2025,
            pdf_page=1,
            role="comparative",
            value=101,
        )
        _assert_observation_payload(
            by_file_json[(2025, "a2025b.pdf")],
            filing_year=2025,
            source_file="a2025b.pdf",
            source_sha256=sha_restated,
            pdf_page=1,
            role="restated_comparative",
            value=99,
        )
        prov_key = next(
            k
            for k, v in provenance["values"].items()
            if v.get("period") == "2024-12-31" and "revenue" in v.get("row_identity", "")
        )
        prov_row = provenance["values"][prov_key]
        assert prov_row["selection_rule"] == "restated_comparative_precedence"
        assert prov_row["selected"]["value"] == 99
        assert len(prov_row["observations"]) == 3

        conflicts_before = reconciled.conflicts
        values_before = reconciled.values
        fin = standardize_reconciled(reconciled)
        revenue = next(item for item in fin.income_statement if item.concept == "revenue")
        assert revenue.values[date(2024, 12, 31)] == 99.0
        assert revenue.values[date(2025, 12, 31)] == 110.0
        assert reconciled.conflicts == conflicts_before
        assert reconciled.values == values_before
        return conflicts_payload, provenance, conflict.selected, conflict.observations

    forward = _check([pair_2024, pair_2025, pair_restated])
    reversed_order = _check([pair_restated, pair_2025, pair_2024])
    assert forward[0] == reversed_order[0]
    assert forward[1] == reversed_order[1]
    assert forward[2] == reversed_order[2]
    assert forward[3] == reversed_order[3]


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


def _bs_row(
    *,
    label: str,
    concept: str,
    section: str,
    values: dict[date, tuple[float, PresentationRole]],
) -> ExtractedStatementRow:
    return ExtractedStatementRow(
        label=label,
        section=section,
        suggested_concept=concept,
        values={
            period: FilingValue(value=value, presentation_role=role)
            for period, (value, role) in values.items()
        },
        source=SourceRef(page=2, statement="Balance Sheet"),
    )


def test_standardize_retains_sparse_balance_sheet_facts(tmp_path: Path):
    """Sparse BS rows stay on the model axis; IS incompletes remain omitted."""
    from core.data.standardized_io import (
        standardized_from_payload,
        standardized_to_payload,
    )

    p2023 = date(2023, 12, 31)
    p2024 = date(2024, 12, 31)
    p2025 = date(2025, 12, 31)
    p2026 = date(2026, 12, 31)

    # Trailing absence + explicit zero: present 2023/2024/2025(0), absent 2026.
    trailing = _bs_row(
        label="Sparse Trailing",
        concept="sparse_trailing",
        section="non-current liabilities",
        values={
            p2023: (10.0, PresentationRole.CURRENT_PERIOD),
            p2024: (20.0, PresentationRole.COMPARATIVE),
            p2025: (0.0, PresentationRole.COMPARATIVE),
        },
    )
    # Leading absence: absent 2023, present 2024/2025/2026.
    leading = _bs_row(
        label="Sparse Leading",
        concept="sparse_leading",
        section="non-current liabilities",
        values={
            p2024: (1.0, PresentationRole.CURRENT_PERIOD),
            p2025: (2.0, PresentationRole.COMPARATIVE),
            p2026: (3.0, PresentationRole.COMPARATIVE),
        },
    )
    # Interior absence: present 2023/2025, absent 2024/2026.
    interior = _bs_row(
        label="Sparse Interior",
        concept="sparse_interior",
        section="non-current liabilities",
        values={
            p2023: (7.0, PresentationRole.CURRENT_PERIOD),
            p2025: (9.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    # Complete BS row across the full axis.
    complete = _bs_row(
        label="Complete Liability",
        concept="complete_liability",
        section="non-current liabilities",
        values={
            p2023: (100.0, PresentationRole.CURRENT_PERIOD),
            p2024: (110.0, PresentationRole.COMPARATIVE),
            p2025: (120.0, PresentationRole.COMPARATIVE),
            p2026: (130.0, PresentationRole.COMPARATIVE),
        },
    )
    # Incomplete IS row must remain omitted.
    only_is = ExtractedStatementRow(
        label="Only IS 2025",
        section="",
        suggested_concept="only_is_2025",
        values={p2025: FilingValue(5.0, PresentationRole.CURRENT_PERIOD)},
        source=SourceRef(page=1, statement="Income Statement"),
    )

    filings = [
        _filing(
            year=2023,
            source_file="a2023.pdf",
            revenue_values={p2023: (100.0, PresentationRole.CURRENT_PERIOD)},
            balance_sheet_rows=(
                _bs_row(
                    label=trailing.label,
                    concept=trailing.suggested_concept,
                    section=trailing.section,
                    values={p2023: (10.0, PresentationRole.CURRENT_PERIOD)},
                ),
                _bs_row(
                    label=interior.label,
                    concept=interior.suggested_concept,
                    section=interior.section,
                    values={p2023: (7.0, PresentationRole.CURRENT_PERIOD)},
                ),
                _bs_row(
                    label=complete.label,
                    concept=complete.suggested_concept,
                    section=complete.section,
                    values={p2023: (100.0, PresentationRole.CURRENT_PERIOD)},
                ),
            ),
        ),
        _filing(
            year=2024,
            source_file="a2024.pdf",
            revenue_values={
                p2023: (100.0, PresentationRole.COMPARATIVE),
                p2024: (110.0, PresentationRole.CURRENT_PERIOD),
            },
            balance_sheet_rows=(
                _bs_row(
                    label=trailing.label,
                    concept=trailing.suggested_concept,
                    section=trailing.section,
                    values={
                        p2023: (10.0, PresentationRole.COMPARATIVE),
                        p2024: (20.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _bs_row(
                    label=leading.label,
                    concept=leading.suggested_concept,
                    section=leading.section,
                    values={p2024: (1.0, PresentationRole.CURRENT_PERIOD)},
                ),
                _bs_row(
                    label=complete.label,
                    concept=complete.suggested_concept,
                    section=complete.section,
                    values={
                        p2023: (100.0, PresentationRole.COMPARATIVE),
                        p2024: (110.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
        ),
        _filing(
            year=2025,
            source_file="a2025.pdf",
            revenue_values={
                p2024: (110.0, PresentationRole.COMPARATIVE),
                p2025: (120.0, PresentationRole.CURRENT_PERIOD),
            },
            extra_rows=(only_is,),
            balance_sheet_rows=(
                _bs_row(
                    label=trailing.label,
                    concept=trailing.suggested_concept,
                    section=trailing.section,
                    values={
                        p2024: (20.0, PresentationRole.COMPARATIVE),
                        p2025: (0.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _bs_row(
                    label=leading.label,
                    concept=leading.suggested_concept,
                    section=leading.section,
                    values={
                        p2024: (1.0, PresentationRole.COMPARATIVE),
                        p2025: (2.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _bs_row(
                    label=interior.label,
                    concept=interior.suggested_concept,
                    section=interior.section,
                    values={p2025: (9.0, PresentationRole.CURRENT_PERIOD)},
                ),
                _bs_row(
                    label=complete.label,
                    concept=complete.suggested_concept,
                    section=complete.section,
                    values={
                        p2024: (110.0, PresentationRole.COMPARATIVE),
                        p2025: (120.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
        ),
        _filing(
            year=2026,
            source_file="a2026.pdf",
            revenue_values={
                p2025: (120.0, PresentationRole.COMPARATIVE),
                p2026: (130.0, PresentationRole.CURRENT_PERIOD),
            },
            balance_sheet_rows=(
                _bs_row(
                    label=leading.label,
                    concept=leading.suggested_concept,
                    section=leading.section,
                    values={
                        p2025: (2.0, PresentationRole.COMPARATIVE),
                        p2026: (3.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _bs_row(
                    label=complete.label,
                    concept=complete.suggested_concept,
                    section=complete.section,
                    values={
                        p2025: (120.0, PresentationRole.COMPARATIVE),
                        p2026: (130.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
        ),
    ]
    reconciled = reconcile_filings(
        [_validated(tmp_path, f, str(f.filing.fiscal_year).encode()) for f in filings]
    )
    fin = standardize_reconciled(reconciled)
    by_concept = {item.concept: item for item in fin.balance_sheet}

    assert by_concept["sparse_trailing"].values == {
        p2023: 10.0,
        p2024: 20.0,
        p2025: 0.0,
        p2026: None,
    }
    assert by_concept["sparse_leading"].values == {
        p2023: None,
        p2024: 1.0,
        p2025: 2.0,
        p2026: 3.0,
    }
    assert by_concept["sparse_interior"].values == {
        p2023: 7.0,
        p2024: None,
        p2025: 9.0,
        p2026: None,
    }
    assert by_concept["complete_liability"].values == {
        p2023: 100.0,
        p2024: 110.0,
        p2025: 120.0,
        p2026: 130.0,
    }
    # Latest available model-period observation supplies label/concept.
    assert by_concept["sparse_trailing"].label == "Sparse Trailing"
    assert by_concept["sparse_trailing"].concept == "sparse_trailing"

    assert all(item.concept != "only_is_2025" for item in fin.income_statement)
    provenance = reconciliation_provenance_payload(reconciled)
    assert any(
        item["status"] == "omitted_incomplete_axis"
        and "only_is_2025" in item["row_identity"]
        for item in provenance["omitted_incomplete_axis"]
    )
    retained = {
        item["suggested_concept"]: item for item in provenance["retained_sparse_axis"]
    }
    assert set(retained) == {"sparse_trailing", "sparse_leading", "sparse_interior"}
    assert retained["sparse_trailing"]["missing_periods"] == [p2026.isoformat()]
    assert "complete_liability" not in retained

    trailing_key = (
        "balance_sheet|"
        f"{next(v.row_identity for v in reconciled.values if v.suggested_concept == 'sparse_trailing')}|"
        f"{p2026.isoformat()}"
    )
    assert provenance["values"][trailing_key]["status"] == "missing_period"
    assert provenance["values"][trailing_key]["selected"] is None

    zero_key = (
        "balance_sheet|"
        f"{next(v.row_identity for v in reconciled.values if v.suggested_concept == 'sparse_trailing')}|"
        f"{p2025.isoformat()}"
    )
    assert provenance["values"][zero_key]["status"] == "selected"
    assert provenance["values"][zero_key]["selected"]["value"] == 0

    payload = standardized_to_payload(fin)
    reloaded = standardized_from_payload(payload)
    re_by = {item.concept: item for item in reloaded.balance_sheet}
    assert re_by["sparse_trailing"].values == by_concept["sparse_trailing"].values
    assert re_by["sparse_trailing"].values[p2026] is None
    assert re_by["sparse_trailing"].values[p2025] == 0.0
    assert re_by["sparse_trailing"].label == "Sparse Trailing"
    assert re_by["sparse_trailing"].concept == "sparse_trailing"


def test_standardize_folds_sparse_income_statement_components(tmp_path: Path):
    """Disclosed IS components stay sparse; label changes fold; other IS gaps omit."""
    from core.data.standardized_io import (
        standardized_from_payload,
        standardized_to_payload,
    )

    p2023 = date(2023, 12, 31)
    p2024 = date(2024, 12, 31)
    p2025 = date(2025, 12, 31)

    def _is_row(label: str, concept: str, values: dict[date, tuple[float, PresentationRole]]):
        return ExtractedStatementRow(
            label=label,
            section="",
            suggested_concept=concept,
            values={
                period: FilingValue(value=value, presentation_role=role)
                for period, (value, role) in values.items()
            },
            source=SourceRef(page=2, statement="Income Statement"),
        )

    def _complete_bs(year: int, amount: float) -> ExtractedStatementRow:
        end = date(year, 12, 31)
        return _bs_row(
            label="Complete Liability",
            concept="complete_liability",
            section="non-current liabilities",
            values={end: (amount, PresentationRole.CURRENT_PERIOD)},
        )

    filings = [
        _filing(
            year=2023,
            source_file="c2023.pdf",
            revenue_values={p2023: (100.0, PresentationRole.CURRENT_PERIOD)},
            extra_rows=(
                _is_row(
                    "Impairment of goodwill and other assets",
                    "impairment_and_restructuring",
                    {
                        p2023: (40.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _is_row(
                    "Acquisition-related expenses",
                    "acquisition_related_expenses",
                    {p2023: (5.0, PresentationRole.CURRENT_PERIOD)},
                ),
                _is_row(
                    "Gain on disposal of assets",
                    "gain_on_disposal_of_assets",
                    {p2023: (0.0, PresentationRole.CURRENT_PERIOD)},
                ),
            ),
            balance_sheet_rows=(_complete_bs(2023, 10.0),),
        ),
        _filing(
            year=2024,
            source_file="c2024.pdf",
            revenue_values={
                p2023: (100.0, PresentationRole.COMPARATIVE),
                p2024: (110.0, PresentationRole.CURRENT_PERIOD),
            },
            extra_rows=(
                _is_row(
                    "Impairment of goodwill and other assets, restructuring costs",
                    "impairment_and_restructuring",
                    {
                        p2023: (40.0, PresentationRole.COMPARATIVE),
                        p2024: (0.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _is_row(
                    "Acquisition-related expenses",
                    "acquisition_related_expenses",
                    {
                        p2023: (5.0, PresentationRole.COMPARATIVE),
                        p2024: (0.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
                _is_row(
                    "Only later year",
                    "only_later_is",
                    {p2024: (1.0, PresentationRole.CURRENT_PERIOD)},
                ),
            ),
            balance_sheet_rows=(
                _bs_row(
                    label="Complete Liability",
                    concept="complete_liability",
                    section="non-current liabilities",
                    values={
                        p2023: (10.0, PresentationRole.COMPARATIVE),
                        p2024: (11.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
        ),
        _filing(
            year=2025,
            source_file="c2025.pdf",
            revenue_values={
                p2024: (110.0, PresentationRole.COMPARATIVE),
                p2025: (120.0, PresentationRole.CURRENT_PERIOD),
            },
            extra_rows=(
                _is_row(
                    "Impairment of assets and restructuring costs",
                    "impairment_and_restructuring",
                    {
                        p2024: (0.0, PresentationRole.COMPARATIVE),
                        p2025: (0.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
            balance_sheet_rows=(
                _bs_row(
                    label="Complete Liability",
                    concept="complete_liability",
                    section="non-current liabilities",
                    values={
                        p2024: (11.0, PresentationRole.COMPARATIVE),
                        p2025: (12.0, PresentationRole.CURRENT_PERIOD),
                    },
                ),
            ),
        ),
    ]
    reconciled = reconcile_filings(
        [_validated(tmp_path, filing, str(filing.filing.fiscal_year).encode()) for filing in filings]
    )
    fin = standardize_reconciled(reconciled)
    by_concept = {item.concept: item for item in fin.income_statement}
    assert set(by_concept) == {
        "revenue",
        "impairment_and_restructuring",
        "acquisition_related_expenses",
        "gain_on_disposal_of_assets",
    }
    assert by_concept["impairment_and_restructuring"].values == {
        p2023: 40.0,
        p2024: 0.0,
        p2025: 0.0,
    }
    assert by_concept["impairment_and_restructuring"].label == (
        "Impairment of assets and restructuring costs"
    )
    assert by_concept["acquisition_related_expenses"].values == {
        p2023: 5.0,
        p2024: 0.0,
        p2025: None,
    }
    assert by_concept["gain_on_disposal_of_assets"].values == {
        p2023: 0.0,
        p2024: None,
        p2025: None,
    }
    assert "only_later_is" not in by_concept
    provenance = reconciliation_provenance_payload(reconciled)
    assert any(
        item["status"] == "omitted_incomplete_axis" and "only_later_is" in item["row_identity"]
        for item in provenance["omitted_incomplete_axis"]
    )
    retained = {
        item["suggested_concept"]
        for item in provenance["retained_sparse_axis"]
        if item["statement"] == "income_statement"
    }
    assert "acquisition_related_expenses" in retained
    assert "gain_on_disposal_of_assets" in retained
    assert "impairment_and_restructuring" in retained
    restored = standardized_from_payload(standardized_to_payload(fin))
    re_by = {item.concept: item for item in restored.income_statement}
    assert re_by["gain_on_disposal_of_assets"].values[p2024] is None
    assert re_by["gain_on_disposal_of_assets"].values[p2023] == 0.0
    assert re_by["impairment_and_restructuring"].concept == "impairment_and_restructuring"


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


def test_supplemental_observations_retain_source_binding(tmp_path: Path):
    note = SupplementalFact(
        fact_type="lease_liability_total",
        period=date(2025, 12, 31),
        value=500.0,
        status="reported",
        source=SourceRef(page=14, note="17 Leases", label="Total"),
    )
    share = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2025, 12, 31),
        value=100.0,
        status="reported",
        source=SourceRef(page=18, note="EPS", label="Diluted WAS"),
    )
    derived = SupplementalFact(
        fact_type="lease_liability_total_derived",
        period=date(2025, 12, 31),
        value=501.0,
        status="derived",
        source=SourceRef(page=14, note="17 Leases"),
        derivation="current + noncurrent",
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(
            SupplementalFact(
                fact_type="lease_liability_total",
                period=date(2024, 12, 31),
                value=400.0,
                status="reported",
                source=SourceRef(page=12, note="17 Leases"),
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
        note_facts=(note, derived),
        share_facts=(share,),
    )
    pair_2024 = _validated(tmp_path, f2024, b"2024")
    pair_2025 = _validated(tmp_path, f2025, b"2025")
    reconciled = reconcile_filings([pair_2024, pair_2025])

    assert len(reconciled.note_facts) == 3
    assert len(reconciled.share_facts) == 1
    for obs in (*reconciled.note_facts, *reconciled.share_facts):
        assert obs.filing_year in {2024, 2025}
        assert obs.source_file in {"a2024.pdf", "a2025.pdf"}
        assert obs.source_sha256
        assert obs.fact.source.page > 0
    sha_2025 = pair_2025[1].computed_source_sha256
    share_obs = reconciled.share_facts[0]
    assert share_obs.filing_year == 2025
    assert share_obs.source_file == "a2025.pdf"
    assert share_obs.source_sha256 == sha_2025
    assert share_obs.fact.source.page == 18
    assert share_obs.fact.source.note == "EPS"

    provenance = reconciliation_provenance_payload(reconciled)
    for section in ("note_facts", "share_facts"):
        assert provenance[section]
        for item in provenance[section]:
            assert item["filing_year"]
            assert item["source_file"]
            assert item["source_sha256"]
            assert item["fact_type"]
            assert item["period"]
            assert "value" in item
            assert item["status"]
            assert item["source"]["page"] > 0
    derived_payload = next(
        n
        for n in provenance["note_facts"]
        if n["fact_type"] == "lease_liability_total_derived"
    )
    assert derived_payload["derivation"] == "current + noncurrent"
    assert derived_payload["source_file"] == "a2025.pdf"
    assert derived_payload["source_sha256"] == sha_2025


def test_equal_repeated_share_facts_agree(tmp_path: Path):
    share_2024 = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2024, 12, 31),
        value=90.0,
        status="reported",
        source=SourceRef(page=18, note="EPS"),
    )
    share_2024_cmp = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2024, 12, 31),
        value=90.0,
        status="reported",
        source=SourceRef(page=19, note="EPS"),
    )
    share_2025 = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2025, 12, 31),
        value=100.0,
        status="reported",
        source=SourceRef(page=19, note="EPS"),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        unit_scale="ones",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        share_facts=(share_2024,),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        unit_scale="ones",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=(share_2024_cmp, share_2025),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    assert len(reconciled.share_facts) == 3
    assert reconciled.supplemental_conflicts == ()
    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is not None
    assert fin.historical_shares.scale_basis == "financial_statement_units"
    assert fin.historical_shares.basis == "reported"
    assert fin.historical_shares.diluted_weighted_average == {
        date(2024, 12, 31): 90.0,
        date(2025, 12, 31): 100.0,
    }


def test_disagreeing_repeated_share_facts_block_promotion(tmp_path: Path):
    share_2024 = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2024, 12, 31),
        value=90.0,
        status="reported",
        source=SourceRef(page=18, note="EPS"),
    )
    share_2024_cmp = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2024, 12, 31),
        value=91.0,
        status="reported",
        source=SourceRef(page=19, note="EPS"),
    )
    share_2025 = SupplementalFact(
        fact_type="diluted_weighted_average_shares",
        period=date(2025, 12, 31),
        value=100.0,
        status="reported",
        source=SourceRef(page=19, note="EPS"),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        unit_scale="ones",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        share_facts=(share_2024,),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        unit_scale="ones",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=(share_2024_cmp, share_2025),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    assert len(reconciled.share_facts) == 3
    assert len(reconciled.supplemental_conflicts) == 1
    conflict = reconciled.supplemental_conflicts[0]
    assert conflict.kind == "share"
    assert conflict.fact_type == "diluted_weighted_average_shares"
    assert conflict.period == date(2024, 12, 31)
    assert conflict.reason == "cross_filing_supplemental_disagreement"
    assert len(conflict.observations) == 2
    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is None


def test_split_anchor_with_contradictory_presentation_blocks_shares(
    tmp_path: Path,
):
    """Valid EPS/WAS split anchor plus a contradictory same-period WAS fails closed."""
    p2021 = date(2021, 12, 31)
    p2022 = date(2022, 12, 31)
    p2023 = date(2023, 12, 31)

    def _eps_row(
        values: dict[date, tuple[float, PresentationRole]],
    ) -> ExtractedStatementRow:
        return ExtractedStatementRow(
            label="Diluted EPS",
            section="diluted",
            suggested_concept="diluted_eps",
            values={
                period: FilingValue(value=value, presentation_role=role)
                for period, (value, role) in values.items()
            },
            source=SourceRef(page=10, statement="Income Statement", note="EPS"),
        )

    f2021 = _filing(
        year=2021,
        source_file="a2021.pdf",
        unit_scale="ones",
        revenue_values={p2021: (80.0, PresentationRole.CURRENT_PERIOD)},
        share_facts=(
            SupplementalFact(
                fact_type="diluted_weighted_average_shares",
                period=p2021,
                value=90.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            # Contradictory pre-anchor presentation of FY2022 (should be 100).
            SupplementalFact(
                fact_type="diluted_weighted_average_shares",
                period=p2022,
                value=90.0,
                status="reported",
                source=SourceRef(page=19, note="EPS"),
            ),
        ),
        extra_rows=(_eps_row({p2021: (25.0, PresentationRole.CURRENT_PERIOD)}),),
    )
    f2022 = _filing(
        year=2022,
        source_file="a2022.pdf",
        unit_scale="ones",
        revenue_values={
            p2021: (80.0, PresentationRole.COMPARATIVE),
            p2022: (100.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=(
            SupplementalFact(
                fact_type="diluted_weighted_average_shares",
                period=p2022,
                value=100.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            SupplementalFact(
                fact_type="basic_weighted_average_shares",
                period=p2022,
                value=95.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            SupplementalFact(
                fact_type="dilutive_shares",
                period=p2022,
                value=5.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
        ),
        extra_rows=(
            _eps_row(
                {
                    p2021: (25.0, PresentationRole.COMPARATIVE),
                    p2022: (30.0, PresentationRole.CURRENT_PERIOD),
                }
            ),
        ),
    )
    f2023 = _filing(
        year=2023,
        source_file="a2023.pdf",
        unit_scale="ones",
        revenue_values={
            p2021: (80.0, PresentationRole.COMPARATIVE),
            p2022: (100.0, PresentationRole.COMPARATIVE),
            p2023: (120.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=(
            SupplementalFact(
                fact_type="diluted_weighted_average_shares",
                period=p2022,
                value=300.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            SupplementalFact(
                fact_type="basic_weighted_average_shares",
                period=p2022,
                value=285.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            SupplementalFact(
                fact_type="dilutive_shares",
                period=p2022,
                value=15.0,
                status="reported",
                source=SourceRef(page=18, note="EPS"),
            ),
            SupplementalFact(
                fact_type="diluted_weighted_average_shares",
                period=p2023,
                value=330.0,
                status="reported",
                source=SourceRef(page=19, note="EPS"),
            ),
        ),
        extra_rows=(
            _eps_row(
                {
                    p2022: (10.0, PresentationRole.RESTATED_COMPARATIVE),
                    p2023: (11.0, PresentationRole.CURRENT_PERIOD),
                }
            ),
        ),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2021, b"2021"),
            _validated(tmp_path, f2022, b"2022"),
            _validated(tmp_path, f2023, b"2023"),
        ]
    )
    share_facts_before = reconciled.share_facts
    conflicts_before = reconciled.conflicts
    supplemental_before = reconciled.supplemental_conflicts

    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is None
    assert len(fin.income_statement) >= 1
    revenue = next(item for item in fin.income_statement if item.concept == "revenue")
    assert revenue.values == {p2021: 80.0, p2022: 100.0, p2023: 120.0}

    # Reconciliation artifacts remain immutable through standardization.
    assert reconciled.share_facts == share_facts_before
    assert reconciled.conflicts == conflicts_before
    assert reconciled.supplemental_conflicts == supplemental_before
    assert len(reconciled.share_facts) >= 8
    assert any(
        c.fact_type == "diluted_weighted_average_shares" and c.period == p2022
        for c in reconciled.supplemental_conflicts
    )


def test_complete_axis_share_promotion_ignores_derived(tmp_path: Path):
    shares_2024 = (
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2024, 12, 31),
            value=90.0,
            status="reported",
            source=SourceRef(page=18, note="EPS"),
        ),
    )
    shares_2025 = (
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2025, 12, 31),
            value=100.0,
            status="reported",
            source=SourceRef(page=19, note="EPS"),
        ),
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2024, 12, 31),
            value=999.0,
            status="derived",
            source=SourceRef(page=19, note="EPS"),
            derivation="invented for test",
        ),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        unit_scale="ones",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        share_facts=shares_2024,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        unit_scale="ones",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=shares_2025,
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    assert reconciled.supplemental_conflicts == ()
    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is not None
    assert fin.historical_shares.diluted_weighted_average[date(2024, 12, 31)] == 90.0
    assert fin.historical_shares.diluted_weighted_average[date(2025, 12, 31)] == 100.0


def test_historical_shares_unit_scale_millions_conversion(tmp_path: Path):
    shares_2024 = (
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2024, 12, 31),
            value=307_247_804.0,
            status="reported",
            source=SourceRef(page=18, note="EPS"),
        ),
    )
    shares_2025 = (
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2025, 12, 31),
            value=307_247_804.0,
            status="reported",
            source=SourceRef(page=19, note="EPS"),
        ),
        SupplementalFact(
            fact_type="diluted_weighted_average_shares",
            period=date(2024, 12, 31),
            value=307_247_804.0,
            status="reported",
            source=SourceRef(page=19, note="EPS"),
        ),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        unit_scale="millions",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
        share_facts=shares_2024,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        unit_scale="millions",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        share_facts=shares_2025,
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ]
    )
    fin = standardize_reconciled(reconciled)
    assert fin.historical_shares is not None
    assert fin.historical_shares.scale_basis == "financial_statement_units"
    assert fin.historical_shares.diluted_weighted_average[date(2024, 12, 31)] == pytest.approx(
        307.247804
    )
    assert fin.historical_shares.diluted_weighted_average[date(2025, 12, 31)] == pytest.approx(
        307.247804
    )


def test_note_fact_disagreement_is_recorded_not_promoted(tmp_path: Path):
    note_a = SupplementalFact(
        fact_type="lease_liability_total",
        period=date(2025, 12, 31),
        value=500.0,
        status="reported",
        source=SourceRef(page=14, note="17 Leases"),
    )
    note_b = SupplementalFact(
        fact_type="lease_liability_total",
        period=date(2025, 12, 31),
        value=501.0,
        status="reported",
        source=SourceRef(page=15, note="17 Leases"),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={date(2024, 12, 31): (100.0, PresentationRole.CURRENT_PERIOD)},
    )
    f2025a = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(note_a,),
    )
    f2025b = _filing(
        year=2025,
        source_file="a2025b.pdf",
        revenue_values={
            date(2024, 12, 31): (100.0, PresentationRole.COMPARATIVE),
            date(2025, 12, 31): (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=(note_b,),
    )
    reconciled = reconcile_filings(
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025a, b"2025"),
            _validated(tmp_path, f2025b, b"2025b"),
        ]
    )
    conflicts = [
        c
        for c in reconciled.supplemental_conflicts
        if c.fact_type == "lease_liability_total" and c.period == date(2025, 12, 31)
    ]
    assert len(conflicts) == 1
    assert conflicts[0].kind == "note"
    assert conflicts[0].reason == "cross_filing_supplemental_disagreement"
    assert len(conflicts[0].observations) == 2
    fin = standardize_reconciled(reconciled)
    assert fin.balance_sheet == []
    payload = reconciliation_conflicts_payload(reconciled)
    assert "supplemental_conflicts" in payload
    assert payload["supplemental_conflict_count"] == len(reconciled.supplemental_conflicts)
    assert payload["overlap_conflict_count"] == len(reconciled.conflicts)
    supp = next(
        c
        for c in payload["supplemental_conflicts"]
        if c["fact_type"] == "lease_liability_total"
    )
    assert supp["reason"] == "cross_filing_supplemental_disagreement"
    for obs in supp["observations"]:
        assert obs["filing_year"]
        assert obs["source_file"]
        assert obs["source_sha256"]
        assert obs["source"]["page"] > 0


def test_historical_lease_payload_round_trip_and_null():
    from core.data.interface import HistoricalLeaseData
    from core.data.standardized_io import (
        standardized_from_payload,
        standardized_to_payload,
    )

    payload = {
        "ticker": "T",
        "company_name": "Co",
        "currency": "HKD",
        "units": "HKD in Millions",
        "jurisdiction": "HK",
        "stock_code": "",
        "periods": [
            {"end_date": "2024-12-31", "label": "FY2024", "is_interim": False},
            {"end_date": "2025-12-31", "label": "FY2025", "is_interim": False},
        ],
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
    }
    fin = standardized_from_payload(payload)
    assert fin.historical_lease is None

    payload["historical_lease"] = None
    assert standardized_from_payload(payload).historical_lease is None

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    fin.historical_lease = HistoricalLeaseData(
        lease_interest_expense={p1: 10.0, p2: 12.0}
    )
    out = standardized_to_payload(fin)
    assert out["historical_lease"]["lease_interest_expense"] == {
        p1.isoformat(): 10.0,
        p2.isoformat(): 12.0,
    }
    restored = standardized_from_payload(out)
    assert restored.historical_lease == fin.historical_lease

    with pytest.raises(ValueError, match="historical_lease must be an object"):
        standardized_from_payload({**payload, "historical_lease": "bad"})
    with pytest.raises(ValueError, match="lease_interest_expense must be an object"):
        standardized_from_payload(
            {**payload, "historical_lease": {"lease_interest_expense": []}}
        )


def test_historical_lease_complete_axis_promotion(tmp_path: Path):
    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    notes_2024 = (
        SupplementalFact(
            fact_type="lease_interest_expense",
            period=p1,
            value=10.0,
            status="reported",
            source=SourceRef(page=14, note="17 Leases"),
        ),
    )
    notes_2025 = (
        SupplementalFact(
            fact_type="lease_interest_expense",
            period=p1,
            value=10.0,
            status="reported",
            source=SourceRef(page=14, note="17 Leases"),
        ),
        SupplementalFact(
            fact_type="lease_interest_expense",
            period=p2,
            value=12.0,
            status="reported",
            source=SourceRef(page=14, note="17 Leases"),
        ),
    )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={p1: (100.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=notes_2024,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            p1: (100.0, PresentationRole.COMPARATIVE),
            p2: (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=notes_2025,
    )
    reconciled = reconcile_filings(
        [_validated(tmp_path, f2024, b"2024"), _validated(tmp_path, f2025, b"2025")]
    )
    fin = standardize_reconciled(reconciled)
    assert fin.historical_lease is not None
    assert fin.historical_lease.lease_interest_expense == {p1: 10.0, p2: 12.0}


@pytest.mark.parametrize(
    "notes_2024,notes_2025",
    [
        # missing one modeled period
        (
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
        ),
        # derived-only for one period
        (
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2025, 12, 31),
                    value=12.0,
                    status="derived",
                    source=SourceRef(page=14, note="17"),
                    derivation="inferred",
                ),
            ),
        ),
        # disagreeing reported observations
        (
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
            (
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2024, 12, 31),
                    value=11.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
                SupplementalFact(
                    fact_type="lease_interest_expense",
                    period=date(2025, 12, 31),
                    value=12.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
        ),
        # differently named supplemental fact only
        (
            (
                SupplementalFact(
                    fact_type="lease_liability_total",
                    period=date(2024, 12, 31),
                    value=10.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
            (
                SupplementalFact(
                    fact_type="lease_liability_total",
                    period=date(2025, 12, 31),
                    value=12.0,
                    status="reported",
                    source=SourceRef(page=14, note="17"),
                ),
            ),
        ),
    ],
)
def test_historical_lease_fail_closed_gating(tmp_path: Path, notes_2024, notes_2025):
    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={p1: (100.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=notes_2024,
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            p1: (100.0, PresentationRole.COMPARATIVE),
            p2: (110.0, PresentationRole.CURRENT_PERIOD),
        },
        note_facts=notes_2025,
    )
    reconciled = reconcile_filings(
        [_validated(tmp_path, f2024, b"2024"), _validated(tmp_path, f2025, b"2025")]
    )
    fin = standardize_reconciled(reconciled)
    assert fin.historical_lease is None


def _cf_row(
    *,
    label: str,
    concept: str,
    section: str,
    values: dict[date, tuple[float, PresentationRole]],
) -> ExtractedStatementRow:
    return ExtractedStatementRow(
        label=label,
        section=section,
        suggested_concept=concept,
        values={
            period: FilingValue(value=value, presentation_role=role)
            for period, (value, role) in values.items()
        },
        source=SourceRef(page=3, statement="Cash Flow"),
    )


def _three_statement_pair(
    tmp_path: Path,
    *,
    comparative_bs: bool = True,
    comparative_ar_change: bool = True,
    fy2025_comparative_revenue: float = 100.0,
):
    """Two annual filings with a complete 2023 comparative on IS/CF and optional BS."""
    p_comp = date(2023, 12, 31)
    p2024 = date(2024, 12, 31)
    p2025 = date(2025, 12, 31)
    cash_2024 = _cf_row(
        label="Net cash from operations",
        concept="operating_cash_flow",
        section="operating",
        values={
            p_comp: (8.0, PresentationRole.COMPARATIVE),
            p2024: (9.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    cash_2025 = _cf_row(
        label="Net cash from operations",
        concept="operating_cash_flow",
        section="operating",
        values={
            p2024: (9.0, PresentationRole.COMPARATIVE),
            p2025: (11.0, PresentationRole.CURRENT_PERIOD),
        },
    )
    ar_2024_values = {p2024: (1.0, PresentationRole.CURRENT_PERIOD)}
    if comparative_ar_change:
        ar_2024_values[p_comp] = (0.5, PresentationRole.COMPARATIVE)
    ar_2024 = _cf_row(
        label="Accounts receivable, net",
        concept="change_in_accounts_receivable",
        section="operating",
        values=ar_2024_values,
    )
    ar_2025 = _cf_row(
        label="Accounts receivable, net",
        concept="change_in_accounts_receivable",
        section="operating",
        values={
            p2024: (1.0, PresentationRole.COMPARATIVE),
            p2025: (1.5, PresentationRole.CURRENT_PERIOD),
        },
    )
    bs_2024 = []
    if comparative_bs:
        bs_2024.append(
            _bs_row(
                label="Cash",
                concept="cash",
                section="current assets",
                values={
                    p_comp: (40.0, PresentationRole.COMPARATIVE),
                    p2024: (50.0, PresentationRole.CURRENT_PERIOD),
                },
            )
        )
    else:
        bs_2024.append(
            _bs_row(
                label="Cash",
                concept="cash",
                section="current assets",
                values={p2024: (50.0, PresentationRole.CURRENT_PERIOD)},
            )
        )
    f2024 = _filing(
        year=2024,
        source_file="a2024.pdf",
        revenue_values={
            p_comp: (90.0, PresentationRole.COMPARATIVE),
            p2024: (100.0, PresentationRole.CURRENT_PERIOD),
        },
        balance_sheet_rows=tuple(bs_2024),
        cash_flow_rows=(cash_2024, ar_2024),
    )
    f2025 = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={
            p2024: (fy2025_comparative_revenue, PresentationRole.COMPARATIVE),
            p2025: (110.0, PresentationRole.CURRENT_PERIOD),
        },
        balance_sheet_rows=(
            _bs_row(
                label="Cash",
                concept="cash",
                section="current assets",
                values={
                    p2024: (50.0, PresentationRole.COMPARATIVE),
                    p2025: (60.0, PresentationRole.CURRENT_PERIOD),
                },
            ),
        ),
        cash_flow_rows=(cash_2025, ar_2025),
    )
    return (
        p_comp,
        p2024,
        p2025,
        [
            _validated(tmp_path, f2024, b"2024"),
            _validated(tmp_path, f2025, b"2025"),
        ],
    )


def test_default_reconciliation_keeps_filing_year_ends(tmp_path: Path):
    p_comp, p2024, p2025, pairs = _three_statement_pair(tmp_path)
    reconciled = reconcile_filings(pairs)
    assert reconciled.periods == (p2024, p2025)
    assert reconciled.requested_admit_periods == ()
    assert reconciled.admitted_comparative_periods == ()
    assert reconciled.excluded_comparative_periods == (p_comp,)
    provenance = reconciliation_provenance_payload(reconciled)
    assert "admitted_comparative_periods" not in provenance
    assert provenance["periods"] == [p2024.isoformat(), p2025.isoformat()]
    outside = [
        item
        for item in provenance["values"].values()
        if item["status"] == "outside_model_axis" and item["period"] == p_comp.isoformat()
    ]
    assert outside
    fin = standardize_reconciled(reconciled)
    assert [period.end_date for period in fin.periods] == [p2024, p2025]


def test_explicit_admission_adds_complete_comparative(tmp_path: Path):
    p_comp, p2024, p2025, pairs = _three_statement_pair(tmp_path)
    default = reconcile_filings(pairs)
    admitted = reconcile_filings(pairs, admit_periods=(p_comp,))
    assert default.periods == (p2024, p2025)
    assert admitted.periods == (p_comp, p2024, p2025)
    assert admitted.requested_admit_periods == (p_comp,)
    assert admitted.admitted_comparative_periods == (p_comp,)
    assert admitted.excluded_comparative_periods == ()
    revenue = next(
        value
        for value in admitted.values
        if value.period == p_comp and value.suggested_concept == "revenue"
    )
    assert revenue.selected.value == 90.0
    cash = next(
        value
        for value in admitted.values
        if value.period == p_comp and value.suggested_concept == "cash"
    )
    assert cash.selected.value == 40.0
    provenance = reconciliation_provenance_payload(admitted)
    assert provenance["admitted_comparative_periods"] == [p_comp.isoformat()]
    assert provenance["excluded_comparative_periods"] == []
    assert provenance["periods"] == [
        p_comp.isoformat(),
        p2024.isoformat(),
        p2025.isoformat(),
    ]
    fin = standardize_reconciled(admitted)
    rev_line = next(item for item in fin.income_statement if item.concept == "revenue")
    assert rev_line.values[p_comp] == 90.0
    assert rev_line.values[p2024] == 100.0
    cash_line = next(item for item in fin.balance_sheet if item.concept == "cash")
    assert cash_line.values[p_comp] == 40.0


def test_admission_rejects_missing_statement_and_unsupported_date(tmp_path: Path):
    p_comp, p2024, p2025, pairs = _three_statement_pair(
        tmp_path, comparative_bs=False
    )
    with pytest.raises(
        ValueError,
        match="cannot admit comparative period 2023-12-31: missing selected balance_sheet coverage",
    ):
        reconcile_filings(pairs, admit_periods=(p_comp,))
    ok_root = tmp_path / "ok"
    ok_root.mkdir()
    complete = _three_statement_pair(ok_root)[3]
    with pytest.raises(
        ValueError,
        match="unsupported comparative period 2019-01-01: not present in documentary observations",
    ):
        reconcile_filings(complete, admit_periods=(date(2019, 1, 1),))
    # Filing year-end requests are ignored; default axis is unchanged.
    already = reconcile_filings(complete, admit_periods=(p2024,))
    assert already.periods == (p2024, p2025)
    assert already.admitted_comparative_periods == ()


def test_admission_preserves_precedence_and_omits_incomplete_cf_row(tmp_path: Path):
    p_comp, p2024, p2025, pairs = _three_statement_pair(
        tmp_path,
        comparative_ar_change=False,
        fy2025_comparative_revenue=101.0,
    )
    reconciled = reconcile_filings(pairs, admit_periods=(p_comp,))
    fy2024_rev = next(
        value
        for value in reconciled.values
        if value.period == p2024 and value.suggested_concept == "revenue"
    )
    assert fy2024_rev.selected.value == 101.0
    assert fy2024_rev.selected.presentation_role == PresentationRole.COMPARATIVE
    assert fy2024_rev.selected.filing_year == 2025
    conflict = next(c for c in reconciled.conflicts if c.period == p2024)
    assert conflict.reason == "later_audited_presentation"
    assert {obs.value for obs in fy2024_rev.observations} == {100.0, 101.0}

    fin = standardize_reconciled(reconciled)
    cf_concepts = {item.concept for item in fin.cash_flow}
    assert "operating_cash_flow" in cf_concepts
    assert "change_in_accounts_receivable" not in cf_concepts
    ar_line = next(
        (
            item
            for item in fin.cash_flow
            if item.concept == "change_in_accounts_receivable"
        ),
        None,
    )
    assert ar_line is None
    provenance = reconciliation_provenance_payload(reconciled)
    omitted = [
        item
        for item in provenance["omitted_incomplete_axis"]
        if item["suggested_concept"] == "change_in_accounts_receivable"
    ]
    assert len(omitted) == 1
    assert p_comp.isoformat() not in omitted[0]["available_periods"]
    assert p2024.isoformat() in omitted[0]["available_periods"]
    omitted_values = [
        item
        for item in provenance["values"].values()
        if item["suggested_concept"] == "change_in_accounts_receivable"
        and item["status"] == "omitted_incomplete_axis"
    ]
    assert omitted_values
    assert all(
        item["selected"] is not None and item["period"] != p_comp.isoformat()
        for item in omitted_values
    )
    assert not any(
        item["period"] == p_comp.isoformat()
        and item["suggested_concept"] == "change_in_accounts_receivable"
        and item["status"] == "selected"
        for item in provenance["values"].values()
    )


def test_admission_round_trip_identity_survives(tmp_path: Path):
    from core.data.standardized_io import (
        standardized_from_payload,
        standardized_to_payload,
    )

    p_comp, p2024, p2025, pairs = _three_statement_pair(tmp_path)
    reconciled = reconcile_filings(pairs, admit_periods=(p_comp,))
    fin = standardize_reconciled(reconciled)
    restored = standardized_from_payload(standardized_to_payload(fin))
    assert [period.end_date for period in restored.periods] == [p_comp, p2024, p2025]
    revenue = next(item for item in restored.income_statement if item.concept == "revenue")
    assert revenue.concept == "revenue"
    assert revenue.values == {p_comp: 90.0, p2024: 100.0, p2025: 110.0}
    cash = next(item for item in restored.balance_sheet if item.concept == "cash")
    assert cash.concept == "cash"
    assert cash.values[p_comp] == 40.0


def test_operating_kpi_missing_label_cannot_reconcile(tmp_path: Path):
    from core.data.historical_operating_kpis import STORE_COUNT_FACT_TYPE

    period = date(2025, 12, 31)
    missing_label = SupplementalFact(
        fact_type=STORE_COUNT_FACT_TYPE,
        period=period,
        value=811,
        status="reported",
        source=SourceRef(page=7, note="Company-Operated Stores", label=""),
        presentation_role=PresentationRole.CURRENT_PERIOD.value,
        unit="stores",
    )
    filing = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(missing_label,),
    )
    _write_source(tmp_path, filing.filing.source_file, b"2025")
    original = copy.deepcopy(filing)
    report = validate_extracted_filing(filing, source_root=tmp_path / "source")
    assert not report.ok
    assert any(
        issue.code == "invalid_operating_kpi"
        and "missing reported label" in issue.message
        for issue in report.errors
    )
    with pytest.raises(ValueError, match="cannot reconcile filings with validation errors"):
        reconcile_filings([(filing, report)])
    assert filing == original


def test_operating_kpi_shared_validation_after_valid_report(tmp_path: Path):
    from core.data.historical_operating_kpis import STORE_COUNT_FACT_TYPE
    from dataclasses import replace

    period = date(2025, 12, 31)
    good = SupplementalFact(
        fact_type=STORE_COUNT_FACT_TYPE,
        period=period,
        value=811,
        status="reported",
        source=SourceRef(
            page=7,
            note="Company-Operated Stores",
            label="Total company-operated stores",
        ),
        presentation_role=PresentationRole.CURRENT_PERIOD.value,
        unit="stores",
    )
    filing, report = _validated(
        tmp_path,
        _filing(
            year=2025,
            source_file="a2025.pdf",
            revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
            note_facts=(good,),
        ),
        b"2025",
    )
    assert report.ok
    original = copy.deepcopy(filing)
    invalid = replace(
        good,
        source=SourceRef(page=7, note="Company-Operated Stores", label=""),
    )
    mutated = replace(filing, note_facts=(invalid,))
    with pytest.raises(ValueError, match="missing reported label"):
        reconcile_filings([(mutated, report)])
    assert filing == original
    assert filing.note_facts[0].source.label == "Total company-operated stores"


@pytest.mark.parametrize(
    "label",
    [123, 1.5, 0, True, False, {"x": 1}, {}, [1], []],
)
def test_operating_kpi_non_string_label_cannot_reconcile(tmp_path: Path, label):
    from core.data.historical_operating_kpis import STORE_COUNT_FACT_TYPE

    period = date(2025, 12, 31)
    bad_label = SupplementalFact(
        fact_type=STORE_COUNT_FACT_TYPE,
        period=period,
        value=811,
        status="reported",
        source=SourceRef(page=7, note="Company-Operated Stores", label=label),
        presentation_role=PresentationRole.CURRENT_PERIOD.value,
        unit="stores",
    )
    filing = _filing(
        year=2025,
        source_file="a2025.pdf",
        revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
        note_facts=(bad_label,),
    )
    _write_source(tmp_path, filing.filing.source_file, b"2025")
    original = copy.deepcopy(filing)
    report = validate_extracted_filing(filing, source_root=tmp_path / "source")
    assert not report.ok
    assert any(
        issue.code == "invalid_operating_kpi"
        and "missing reported label" in issue.message
        for issue in report.errors
    )
    with pytest.raises(ValueError, match="cannot reconcile filings with validation errors"):
        reconcile_filings([(filing, report)])
    assert filing == original


@pytest.mark.parametrize("label", [123, True, {"x": 1}, [1]])
def test_operating_kpi_shared_validation_rejects_non_string_superseded(
    tmp_path: Path, label
):
    from core.data.historical_operating_kpis import STORE_COUNT_FACT_TYPE
    from dataclasses import replace

    period = date(2025, 12, 31)
    good = SupplementalFact(
        fact_type=STORE_COUNT_FACT_TYPE,
        period=period,
        value=811,
        status="reported",
        source=SourceRef(
            page=7,
            note="Company-Operated Stores",
            label="Total company-operated stores",
        ),
        presentation_role=PresentationRole.CURRENT_PERIOD.value,
        unit="stores",
    )
    filing, report = _validated(
        tmp_path,
        _filing(
            year=2025,
            source_file="a2025.pdf",
            revenue_values={period: (110.0, PresentationRole.CURRENT_PERIOD)},
            note_facts=(good,),
        ),
        b"2025",
    )
    assert report.ok
    original = copy.deepcopy(filing)
    superseded = replace(
        good,
        value=700,
        presentation_role=PresentationRole.PRIOR_PRESENTATION.value,
        source=SourceRef(page=7, note="Company-Operated Stores", label=label),
    )
    mutated = replace(filing, note_facts=(good, superseded))
    with pytest.raises(ValueError, match="missing reported label"):
        reconcile_filings([(mutated, report)])
    assert filing == original
    assert filing.note_facts[0].source.label == "Total company-operated stores"

