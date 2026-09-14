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
