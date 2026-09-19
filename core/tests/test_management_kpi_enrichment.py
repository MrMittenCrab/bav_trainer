"""Documentary enrichment of working-copy Lululemon management KPIs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from core.current_build import prepare_company_input, resolve_company
from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import reconciliation_management_admission_payload
from core.ingestion.management_kpi_enrichment import (
    FISCAL_CALENDAR_BASIS,
    decode_filing_text,
    enrich_management_working_copies,
    inspect_source_pdf,
    printed_pages_from_reference,
    resolve_physical_pages,
)
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    REASON_MISSING_COMPARISON,
)
from core.ingestion.management_kpi_reconciliation import SELECTION_DEFERRED
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    SOURCE,
    _bytes_by_name,
)
from core.tests.test_operating_kpi_facts import ADMIT_2022, INDEPENDENT_STORE_TOTALS
from core.tests.test_revenue_per_store import REVENUE_ANCHORS

ROOT = Path(__file__).resolve().parents[2]
FY2024_PDF = SOURCE / "LULU_FY2024_Annual_Report.pdf"


def _copy_extracted(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for name in ANNUAL_NAMES + MANAGEMENT_NAMES:
        shutil.copy2(EXTRACTED / name, dest / name)
    return dest


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protected_extracts_are_not_enriched():
    before = _bytes_by_name(EXTRACTED)
    with pytest.raises(ValueError, match="protected source extracts"):
        enrich_management_working_copies(EXTRACTED, SOURCE)
    assert _bytes_by_name(EXTRACTED) == before


def test_fy2024_printed_34_is_physical_40():
    inspection = inspect_source_pdf(FY2024_PDF)
    assert inspection.printed_to_physical[34] == 40
    assert inspection.physical_to_printed[40] == 34
    assert inspection.printed_to_physical[4] == 10
    text = " ".join(decode_filing_text(inspection.page_texts[40]).split())
    assert "Comparable company-operated stores have been open" in text
    assert "53rd week of net revenue is excluded from the calculation of comparable sales" in text
    assert "average ending square footage" in text
    assert inspection.fiscal_calendar_evidenced
    assert 2024 in inspection.fifty_three_week_years
    assert 2023 in inspection.fifty_two_week_years


def test_printed_reference_resolves_without_inventing_pages():
    inspection = inspect_source_pdf(FY2024_PDF)
    assert printed_pages_from_reference("Form 10-K p. 34") == (34,)
    assert printed_pages_from_reference("Form 10-K pp. 33–34") == (33, 34)
    assert resolve_physical_pages("Form 10-K p. 34", inspection) == (40,)
    assert resolve_physical_pages("Form 10-K p. 4", inspection) == (10,)


def test_working_copy_enrichment_maps_period_and_calendar(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "work")
    protected = _bytes_by_name(EXTRACTED)
    sidecar = enrich_management_working_copies(dest, SOURCE)
    assert _bytes_by_name(EXTRACTED) == protected
    assert Path(sidecar["resolution_path"]).is_file()
    fy2024 = json.loads((dest / "LULU_FY2024_management_kpis.json").read_text())
    original = json.loads((EXTRACTED / "LULU_FY2024_management_kpis.json").read_text())
    assert fy2024["report"]["fiscal_year_end"] == "2025-02-02"
    assert fy2024["report"]["reporting_basis"] == FISCAL_CALENDAR_BASIS
    assert fy2024["report"]["original_reporting_basis"] == original["report"]["reporting_basis"]
    compsales = next(
        item
        for item in fy2024["reported_kpis"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    original_comp = next(
        item
        for item in original["reported_kpis"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    assert compsales["period"] == "2025-02-02"
    assert compsales["original_period_label"] == "FY2024"
    assert compsales["value"] == original_comp["value"]
    assert compsales["qualifiers"]["excludes_53rd_week"] is True
    assert compsales["presentation"]["role"] == "current"
    assert "assurance" not in compsales
    assert "revision" not in compsales
    assert "physical_page_mapping" not in compsales.get("source", {})
    spsf = next(
        item for item in fy2024["reported_kpis"] if item["metric_id"] == "sales_per_square_foot"
    )
    assert spsf["period"] == "2025-02-02"
    assert spsf["value"] == 1574
    assert spsf["qualifiers"]["excludes_53rd_week"] is True
    assert spsf.get("comparison") in (None, "")
    fy2025 = json.loads((dest / "LULU_FY2025_management_kpis.json").read_text())
    fy2025_comp = next(
        item
        for item in fy2025["reported_kpis"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    assert fy2025_comp["period"] == "2026-02-01"
    assert fy2025_comp["qualifiers"]["excludes_53rd_week"] is False
    fy2022 = json.loads((dest / "LULU_FY2022_management_kpis.json").read_text())
    store = next(
        item
        for item in fy2022["reported_kpis"]
        if item["metric_id"] == "comparable_store_sales_growth"
    )
    total = next(
        item
        for item in fy2022["reported_kpis"]
        if item["metric_id"] == "total_comparable_sales_growth"
    )
    assert store["period"] == "2023-01-29"
    assert total["period"] == "2023-01-29"
    assert store["metric_id"] != "comparable_sales_growth"
    record = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2024_management_kpis.json"
    )
    company = next(
        item for item in record["fields"] if item["metric_id"] == "comparable_sales_growth"
    )
    assert 40 in company["physical_pages"] or company["physical_pages"] == [33]
    spsf_field = next(
        item for item in record["fields"] if item["metric_id"] == "sales_per_square_foot"
    )
    assert spsf_field["physical_pages"] == [10]


def test_enriched_admission_stays_fail_closed_without_audited_revision(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "admit")
    enrich_management_working_copies(dest, SOURCE)
    payload = reconciliation_management_admission_payload(
        reconcile_filings(
            load_and_validate_extracted_dir(dest, source_root=SOURCE),
            admit_periods=ADMIT_2022,
        )
    )
    focus = [
        item
        for item in payload["assessments"]["items"]
        if item["family"] in {FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT}
        and item["status"] == "supported"
    ]
    assert focus
    assert all(item["evidence"]["period_kind"] == "date" for item in focus)
    assert all(item["evidence"]["calendar_reporting_basis"] == FISCAL_CALENDAR_BASIS for item in focus)
    fy2024_company = [
        item
        for item in focus
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["evidence"]["period"] == "2025-02-02"
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
    ]
    assert fy2024_company
    assert all(
        item["evidence"]["calendar_week_adjustment"] == "excluded"
        for item in fy2024_company
    )
    spsf = [item for item in focus if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT]
    assert spsf
    assert all(REASON_MISSING_COMPARISON in item["unresolved_reasons"] for item in spsf)
    selections = payload["reconciliation"]["group_selections"]
    assert selections
    assert all(item["status"] == SELECTION_DEFERRED for item in selections)
    assert payload["canonical_selection"] == "deferred"
    assert all(item["assurance"] == "unknown" for item in payload["observations"] if item["kind"] == "reported_kpi")
    assert all(item.get("revision") is None for item in selections)
    handoff = next(
        item
        for item in payload["diagnostics"]
        if item["code"] == "management_kpi_history_handoff"
    )
    assert handoff["message"].startswith("0 evidenced selected occurrence(s)")


def test_definition_and_calendar_are_not_collapsed_across_identities(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "ids")
    enrich_management_working_copies(dest, SOURCE)
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    supported = [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == "supported" and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    populations = {
        item["metric_identity_fields"]["population"]
        for item in supported
        if item["evidence"]["period"] == "2023-01-29"
    }
    assert "company_operated_stores" in populations
    assert "company_operated_stores_and_direct_to_consumer" in populations
    later = {
        item["metric_identity_fields"]["population"]
        for item in supported
        if item["evidence"]["period"] == "2025-02-02"
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
    }
    assert later == {"company_operated_stores_and_ecommerce"}
    weeks = {
        (item["evidence"]["period"], item["evidence"]["calendar_week_adjustment"])
        for item in supported
        if item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
    }
    assert ("2025-02-02", "excluded") in weeks
    assert ("2026-02-01", "included") in weeks


def test_ordinary_prepare_writes_resolution_and_keeps_revenue_per_store(tmp_path: Path):
    company = resolve_company("Lululemon")
    staged = tmp_path / "staged"
    fin = prepare_company_input(company, staged)
    resolution = staged / "supporting" / "management_kpi_page_resolution.json"
    assert resolution.is_file()
    sidecar = json.loads(resolution.read_text())
    fy2024 = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2024_management_kpis.json"
    )
    assert fy2024["fiscal_year_end"] == "2025-02-02"
    assert fy2024["printed_to_physical"]["34"] == 40
    protected = EXTRACTED / "LULU_FY2024_management_kpis.json"
    working = staged / "supporting" / "extracted" / "LULU_FY2024_management_kpis.json"
    assert _sha(protected) != _sha(working)
    original_comp = next(
        item
        for item in json.loads(protected.read_text())["reported_kpis"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    assert original_comp["period"] == "FY2024"
    admission = json.loads(
        (staged / "supporting" / "management_kpi_admission.json").read_text()
    )
    assert admission["reconciliation"]["selected_count"] == 0
    assert fin.historical_operating_kpis is not None
    assert fin.historical_operating_kpis.management_observations == []
    stores = {
        item.period: item.value
        for item in fin.historical_operating_kpis.observations
    }
    assert stores == INDEPENDENT_STORE_TOTALS
    from core.model.revenue_per_store import compute_revenue_per_store_series

    series = compute_revenue_per_store_series(fin)
    for period, revenue in REVENUE_ANCHORS.items():
        expected = revenue / INDEPENDENT_STORE_TOTALS[period]
        assert series.period_end_revenue_per_store[period] == pytest.approx(expected)
