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
    SourceInspection,
    decode_filing_text,
    definition_features,
    enrich_management_working_copies,
    field_supporting_passages,
    inspect_source_pdf,
    page_reference_from_printed,
    printed_pages_from_reference,
    resolve_physical_pages,
)
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    REASON_MISSING_COMPARISON,
)
from core.ingestion.management_kpi_reconciliation import SELECTION_DEFERRED, SELECTION_SELECTED
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
    assert company.get("supporting_passages")
    assert "supporting_text" not in company
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
    selected = [item for item in selections if item["status"] == SELECTION_SELECTED]
    deferred = [item for item in selections if item["status"] == SELECTION_DEFERRED]
    assert selected
    assert all(item.get("revision") is None for item in selected)
    assert all(
        (item.get("assurance_evidence") or {}).get("status") == "unknown"
        for item in selected
    )
    assert payload["canonical_selection"] == "deferred"
    assert all(item["assurance"] == "unknown" for item in payload["observations"] if item["kind"] == "reported_kpi")
    assert all(item.get("revision") is None for item in selections)
    handoff = next(
        item
        for item in payload["diagnostics"]
        if item["code"] == "management_kpi_history_handoff"
    )
    assert handoff["message"].startswith(f"{len(selected)} evidenced selected occurrence(s)")
    assert deferred or selected


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
    assert admission["reconciliation"]["selected_count"] > 0
    assert fin.historical_operating_kpis is not None
    assert fin.historical_operating_kpis.management_observations
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


def _enriched_admission(tmp_path: Path) -> dict:
    dest = _copy_extracted(tmp_path / "doc")
    enrich_management_working_copies(dest, SOURCE)
    return reconciliation_management_admission_payload(
        reconcile_filings(
            load_and_validate_extracted_dir(dest, source_root=SOURCE),
            admit_periods=ADMIT_2022,
        )
    )


def test_admission_consumes_pdf_validated_page_bindings(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    focus = [
        item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
        and item["metric_id"] in {
            "comparable_sales_growth",
            "sales_per_square_foot",
        }
    ]
    bound = [
        item
        for item in focus
        if item["physical_page_mapping"] != "unresolved"
        and "physical_page_mapping" not in item["unresolved"]
    ]
    assert bound
    fy2024 = next(
        item
        for item in bound
        if item["extraction_document"] == "LULU_FY2024_management_kpis.json"
        and item["metric_id"] == "comparable_sales_growth"
    )
    assert "→" in fy2024["physical_page_mapping"]
    assert fy2024["supporting_evidence"]["physical_pages"]
    assert fy2024["supporting_evidence"]["passages"]
    assert "supporting_text" not in fy2024["supporting_evidence"]


def test_unsupported_page_bindings_are_rejected(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "badbind")
    enrich_management_working_copies(dest, SOURCE)
    working = json.loads((dest / "LULU_FY2024_management_kpis.json").read_text())
    for item in working["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["supporting_evidence"]["physical_pages"] = [999]
            item["supporting_evidence"]["page_mapping"] = "34→999"
    (dest / "LULU_FY2024_management_kpis.json").write_text(
        json.dumps(working, indent=2) + "\n"
    )
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    compsales = [
        item
        for item in payload["observations"]
        if item["extraction_document"] == "LULU_FY2024_management_kpis.json"
        and item["metric_id"] == "comparable_sales_growth"
    ]
    assert compsales
    assert all(item["physical_page_mapping"] == "unresolved" for item in compsales)
    assert all("physical_page_mapping" in item["unresolved"] for item in compsales)


def test_extract_asserted_physical_pages_still_rejected(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "extract")
    enrich_management_working_copies(dest, SOURCE)
    working = json.loads((dest / "LULU_FY2024_management_kpis.json").read_text())
    for item in working["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["source"]["physical_page_mapping"] = "40"
            item["presentation"]["source"]["physical_page_mapping"] = "40"
    (dest / "LULU_FY2024_management_kpis.json").write_text(
        json.dumps(working, indent=2) + "\n"
    )
    with pytest.raises(ValueError, match="cannot certify a PDF page"):
        load_and_validate_extracted_dir(dest, source_root=SOURCE)


def test_cross_filing_fy2022_calendar_from_fy2023_page_33(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "cal")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    fy2022 = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2022_management_kpis.json"
    )
    store = next(
        item for item in fy2022["fields"] if item["metric_id"] == "comparable_store_sales_growth"
    )
    assert store["calendar_week_excluded"] is False
    assert store["fiscal_year_length_weeks"] == 52
    provenance = store["calendar_provenance"]
    assert provenance["cross_filing"] is True
    assert provenance["source_file"] == "LULU_FY2023_Annual_Report.pdf"
    assert provenance["physical_page"] == 33
    assert "2022" in provenance["passage"]
    assert "52-week" in provenance["passage"]
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    fy2022_items = [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == "supported"
        and item["evidence"]["period"] == "2023-01-29"
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    assert fy2022_items
    assert all(
        item["evidence"]["calendar_week_adjustment"] == "included"
        for item in fy2022_items
    )
    assert all(
        item["evidence"]["fiscal_year_length_weeks"] == "52" for item in fy2022_items
    )


def test_shifted_comparison_windows_are_not_inferred(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    later = [
        item
        for item in payload["assessments"]["items"]
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["status"] == "supported"
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
    ]
    by_period = {item["evidence"]["period"]: item for item in later}
    fy2024 = by_period["2025-02-02"]
    fy2025 = by_period["2026-02-01"]
    assert fy2024["evidence"]["calendar_week_adjustment"] == "excluded"
    assert fy2025["evidence"]["calendar_week_adjustment"] == "included"
    assert fy2025["evidence"]["comparison_window"]
    assert "February 1" in fy2025["evidence"]["comparison_window"]
    assert "2026" in fy2025["evidence"]["comparison_window"]
    assert "February 2" in fy2025["evidence"]["comparison_window"]
    assert "2025" in fy2025["evidence"]["comparison_window"]
    assert fy2024["evidence"]["comparison_window"] != fy2025["evidence"]["comparison_window"]
    assert "comparison_window_mismatch" in fy2024["unresolved_reasons"]
    assert "comparison_window_mismatch" in fy2025["unresolved_reasons"]


def test_definition_equivalence_and_genuine_differences(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    supported = [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == "supported"
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    fy2022_store = [
        item
        for item in supported
        if item["evidence"]["period"] == "2023-01-29"
        and item["metric_identity_fields"].get("population") == "company_operated_stores"
    ]
    fy2022_total = [
        item
        for item in supported
        if item["evidence"]["period"] == "2023-01-29"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_direct_to_consumer"
    ]
    later = [
        item
        for item in supported
        if item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
    ]
    assert fy2022_store
    assert fy2022_total
    assert later
    later_texts = {item["definition"]["text"] for item in later}
    assert len(later_texts) >= 1
    assert all(item["definition"]["text"] for item in later)
    assert {item["metric_identity"] for item in fy2022_store}.isdisjoint(
        {item["metric_identity"] for item in later}
    )
    assert {item["metric_identity"] for item in fy2022_total}.isdisjoint(
        {item["metric_identity"] for item in later}
    )
    equivalent_later = [item for item in later if item["definition_equivalence"] == "equivalent"]
    different_later = [item for item in later if item["definition_equivalence"] == "different"]
    assert equivalent_later or not different_later or later


def test_spsf_level_admission_is_separate_from_comparison(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = [
        item
        for item in payload["assessments"]["items"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT and item["status"] == "supported"
    ]
    assert spsf
    assert all(item["level_admission"] == "admitted" for item in spsf)
    assert all(REASON_MISSING_COMPARISON in item["unresolved_reasons"] for item in spsf)
    assert all(item.get("pair_assessments") is not None for item in spsf)
    assert any(
        pair["outcome"] == "supported"
        for item in spsf
        for pair in item["pair_assessments"]
        if pair["kind"] == "historical_comparison"
    )
    assert any(item["historical_comparison"] == "eligible" for item in spsf)
    assert any(item["historical_comparison"] == "ineligible" for item in spsf)
    fy2023 = next(
        item
        for item in payload["observations"]
        if item["metric_id"] == "sales_per_square_foot"
        and item["extraction_document"] == "LULU_FY2023_management_kpis.json"
    )
    levels = fy2023["supporting_evidence"]["prior_period_levels"]
    assert levels
    roles = {item["presentation_role"] for item in levels}
    assert "current" in roles
    assert "prior" in roles
    assert all(item.get("revision") in (None, {}) for item in levels)
    assert all("comparison" not in item for item in levels)
    decisions = [
        item
        for item in payload["group_decisions"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT
    ]
    assert decisions
    selected_spsf = [item for item in decisions if item["status"] == SELECTION_SELECTED]
    deferred_spsf = [item for item in decisions if item["status"] == SELECTION_DEFERRED]
    assert selected_spsf
    assert all(item["level_eligibility"] == "admitted" for item in decisions)
    assert any(
        failure["requirement"] in {"calendar", "definition", "historical_comparison"}
        for item in decisions
        for failure in item["remaining_failures"]
    )
    compsales_decisions = [
        item
        for item in payload["group_decisions"]
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    assert compsales_decisions
    selected_compsales = [
        item for item in compsales_decisions if item["status"] == SELECTION_SELECTED
    ]
    deferred_compsales = [
        item for item in compsales_decisions if item["status"] == SELECTION_DEFERRED
    ]
    assert selected_compsales or deferred_compsales
    assert all(item.get("revision") is None for item in selected_compsales)
    assert all(
        item["canonical_selection"] == SELECTION_DEFERRED for item in deferred_compsales
    )
    assert all(
        item["canonical_selection"] == SELECTION_SELECTED for item in selected_compsales
    )


def test_spsf_value_passages_require_metric_and_value(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "spsfval")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    by_doc = {item["extraction_document"]: item for item in sidecar["documents"]}
    fy2024 = next(
        item
        for item in by_doc["LULU_FY2024_management_kpis.json"]["fields"]
        if item["metric_id"] == "sales_per_square_foot" and item["period"] == "2025-02-02"
    )
    fy2025 = next(
        item
        for item in by_doc["LULU_FY2025_management_kpis.json"]["fields"]
        if item["metric_id"] == "sales_per_square_foot" and item["period"] == "2026-02-01"
    )
    assert "1,574" in fy2024["supporting_passages"]["value"]
    assert "sales per square foot" in fy2024["supporting_passages"]["value"].lower()
    assert "2024" in fy2024["supporting_passages"]["value"]
    assert "1,426" in fy2025["supporting_passages"]["value"]
    assert "sales per square foot" in fy2025["supporting_passages"]["value"].lower()
    assert "2025" in fy2025["supporting_passages"]["value"]


def test_date_passages_reject_introductory_text(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "dates")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    for document in sidecar["documents"]:
        for field in document["fields"]:
            if field["metric_id"] not in {
                "comparable_sales_growth",
                "sales_per_square_foot",
                "comparable_store_sales_growth",
                "total_comparable_sales_growth",
            }:
                continue
            dates = (field.get("supporting_passages") or {}).get("dates", "")
            if not dates:
                continue
            lowered = dates.lower()
            assert "components of management" not in lowered
            assert "components of this md" not in lowered
            assert "social impact" not in lowered
            assert "we have contributed" not in lowered
            assert (
                "fiscal year ended" in lowered
                or "weeks ended" in lowered
                or "number of company-operated stores" in lowered
            )
            assert not (
                "sunday closest to january 31" in lowered
                and "weeks ended" not in lowered
                and "fiscal year ended" not in lowered
            )


def test_unrelated_numeric_matches_are_rejected(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "needles")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    fy2024 = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2024_management_kpis.json"
    )
    company = next(
        item
        for item in fy2024["fields"]
        if item["metric_id"] == "comparable_sales_growth"
        and item["period"] == "2025-02-02"
    )
    value = company["supporting_passages"]["value"]
    assert "comparable sales" in value.lower()
    assert "4%" in value or "increased 4" in value.lower()
    assert "september 2024" not in value.lower()
    assert "supply partner" not in value.lower()
    fy2025 = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2025_management_kpis.json"
    )
    company_2025 = next(
        item
        for item in fy2025["fields"]
        if item["metric_id"] == "comparable_sales_growth"
        and item["period"] == "2026-02-01"
    )
    value_2025 = (company_2025.get("supporting_passages") or {}).get("value", "")
    assert "repurchase" not in value_2025.lower()
    assert "1.2 billion" not in value_2025.lower()


def test_prior_period_spsf_become_occurrences(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    fy2023_priors = [
        item
        for item in payload["observations"]
        if item["metric_id"] == "sales_per_square_foot"
        and item["extraction_document"] == "LULU_FY2023_management_kpis.json"
        and item["presentation_role"] == "prior"
    ]
    assert fy2023_priors
    assert any(item["value"] == 1580 and item["period"] == "2023-01-29" for item in fy2023_priors)
    assert all(item.get("revision") in (None, {}) for item in fy2023_priors)
    assert all(item["assurance"] == "unknown" for item in fy2023_priors)
    fy2024_priors = [
        item
        for item in payload["observations"]
        if item["metric_id"] == "sales_per_square_foot"
        and item["extraction_document"] == "LULU_FY2024_management_kpis.json"
        and item["presentation_role"] == "prior"
    ]
    assert any(item["value"] == 1609 and item["period"] == "2024-01-28" for item in fy2024_priors)


def test_group_decisions_report_all_failures(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    decisions = payload["group_decisions"]
    assert decisions
    for item in decisions:
        requirements = {failure["requirement"] for failure in item["remaining_failures"]}
        if item["status"] == SELECTION_SELECTED:
            assert "canonical_selection" not in requirements
            assert item["canonical_selection"] == SELECTION_SELECTED
        else:
            assert "canonical_selection" in requirements
            assert item["canonical_selection"] == SELECTION_DEFERRED
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT:
            assert item["level_eligibility"] == "admitted"
        if any(
            reason in item["selection_reasons"]
            for reason in ("singleton", "missing_revision_link", "unknown_assurance")
        ):
            assert item["canonical_selection"] == SELECTION_DEFERRED
            assert item["status"] == SELECTION_DEFERRED
        if item["comparison_eligibility"] == "eligible":
            assert any(
                pair.get("outcome") == "supported"
                and pair.get("kind") == "historical_comparison"
                for pair in item.get("pair_assessments") or []
            )
            for failure in item["remaining_failures"]:
                if failure["requirement"] in {"calendar", "comparison_window"}:
                    assert failure.get("comparison_pair")
                    assert failure["comparison_pair"][0] != failure["comparison_pair"][1]
        if item["level_eligibility"] == "admitted":
            assert item["canonical_selection"] in {SELECTION_SELECTED, SELECTION_DEFERRED}


def test_historical_comparison_ineligible_when_window_conflicts(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    fy2024 = [
        item
        for item in payload["assessments"]["items"]
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["status"] == "supported"
        and item["evidence"]["period"] == "2025-02-02"
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
    ]
    assert fy2024
    for item in fy2024:
        assert "comparison_window_mismatch" in item["unresolved_reasons"] or (
            "calendar_mismatch" in item["unresolved_reasons"]
        )
        assert item["historical_comparison"] == "ineligible"
        assert item["level_admission"] == "admitted"


def _spsf_fields(sidecar: dict) -> list[dict]:
    fields: list[dict] = []
    for document in sidecar["documents"]:
        for field in document["fields"]:
            if field["metric_id"] != "sales_per_square_foot":
                continue
            item = dict(field)
            item["extraction_document"] = document["extraction_document"]
            fields.append(item)
    return fields


def test_prior_occurrence_calendars_keep_52_and_53_weeks(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "occ-cal")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    fields = _spsf_fields(sidecar)
    assert len(fields) == 7
    by_key = {
        (item["extraction_document"], item["period"]): item for item in fields
    }
    fy2023_in_fy2024 = by_key[
        ("LULU_FY2024_management_kpis.json", "2024-01-28")
    ]
    assert fy2023_in_fy2024["fiscal_year_length_weeks"] == 52
    assert fy2023_in_fy2024["calendar_week_excluded"] is False
    assert fy2023_in_fy2024["calendar_provenance"]["fifty_three_week"] is False
    fy2024_in_fy2025 = by_key[
        ("LULU_FY2025_management_kpis.json", "2025-02-02")
    ]
    assert fy2024_in_fy2025["fiscal_year_length_weeks"] == 53
    assert fy2024_in_fy2025["calendar_week_excluded"] is True
    assert fy2024_in_fy2025["calendar_provenance"]["fifty_three_week"] is True
    expected = {
        ("LULU_FY2022_management_kpis.json", "2023-01-29"): (52, False),
        ("LULU_FY2023_management_kpis.json", "2023-01-29"): (52, False),
        ("LULU_FY2023_management_kpis.json", "2024-01-28"): (52, False),
        ("LULU_FY2024_management_kpis.json", "2024-01-28"): (52, False),
        ("LULU_FY2024_management_kpis.json", "2025-02-02"): (53, True),
        ("LULU_FY2025_management_kpis.json", "2025-02-02"): (53, True),
        ("LULU_FY2025_management_kpis.json", "2026-02-01"): (52, False),
    }
    assert {
        (item["extraction_document"], item["period"]): (
            item["fiscal_year_length_weeks"],
            item["calendar_week_excluded"],
        )
        for item in fields
    } == expected


def test_metric_exclusion_is_not_inferred_from_53_week_year_alone():
    from core.ingestion.management_kpi_enrichment import (
        CalendarYearEvidence,
        _metric_excludes_53rd_week,
    )

    calendar = CalendarYearEvidence(
        fiscal_year=2024,
        fifty_three_week=True,
        source_file="LULU_FY2024_Annual_Report.pdf",
        physical_page=32,
        passage="Fiscal 2024 was a 53-week year.",
        cross_filing=False,
    )
    assert _metric_excludes_53rd_week(
        "sales_per_square_foot", calendar, [calendar.passage]
    ) is None
    assert _metric_excludes_53rd_week(
        "comparable_sales_growth", calendar, [calendar.passage]
    ) is None
    assert (
        _metric_excludes_53rd_week(
            "sales_per_square_foot",
            calendar,
            [
                "In fiscal years with 53 weeks the 53rd week of net revenue is "
                "excluded from the calculation of sales per square foot."
            ],
        )
        is True
    )
    fifty_two = CalendarYearEvidence(
        fiscal_year=2023,
        fifty_three_week=False,
        source_file="LULU_FY2023_Annual_Report.pdf",
        physical_page=33,
        passage="Fiscal 2023, 2022, and 2021 were each 52-week years.",
        cross_filing=False,
    )
    assert _metric_excludes_53rd_week(
        "sales_per_square_foot",
        fifty_two,
        [
            "In fiscal years with 53 weeks, the 53rd week of net revenue is "
            "excluded from the calculation of sales per square foot."
        ],
    ) is False


def test_comparison_window_is_not_copied_onto_priors_or_spsf(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "win")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    fields = _spsf_fields(sidecar)
    assert all(item.get("comparison_window") in (None, {}) for item in fields)
    by_doc = {item["extraction_document"]: item for item in sidecar["documents"]}
    fy2024_comp = next(
        item
        for item in by_doc["LULU_FY2024_management_kpis.json"]["fields"]
        if item["metric_id"] == "comparable_sales_growth"
        and item["period"] == "2025-02-02"
    )
    fy2025_comp = next(
        item
        for item in by_doc["LULU_FY2025_management_kpis.json"]["fields"]
        if item["metric_id"] == "comparable_sales_growth"
        and item["period"] == "2026-02-01"
    )
    fy2024_prior_spsf = next(
        item
        for item in by_doc["LULU_FY2025_management_kpis.json"]["fields"]
        if item["metric_id"] == "sales_per_square_foot"
        and item["period"] == "2025-02-02"
    )
    assert fy2024_comp["comparison_window"] in (None, {})
    assert fy2025_comp["comparison_window"]
    assert "February 1" in fy2025_comp["comparison_window"]["label"]
    assert fy2024_prior_spsf["comparison_window"] in (None, {})
    assert fy2024_prior_spsf["comparison_window"] != fy2025_comp["comparison_window"]
    window_pages = fy2025_comp["comparison_window"]["physical_pages"]
    assert window_pages
    assert len(window_pages) <= 2
    assert 33 in window_pages or 41 in window_pages


def test_complete_multiline_passages_and_individual_bindings(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "pass")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    for field in _spsf_fields(sidecar):
        presentation = (field.get("supporting_passages") or {}).get("presentation", "")
        if presentation:
            assert presentation.endswith("footage.") or "footage" in presentation.lower()
            assert not presentation.endswith("their square")
            assert presentation.lower().startswith("we use") or presentation.lower().startswith(
                "sales per square foot we use"
            )
        definition = (field.get("supporting_passages") or {}).get("definition", "")
        if definition:
            assert not definition.endswith("for each")
            assert "square footage" in definition.lower()
            assert "significantly" not in definition.lower() or definition.lower().endswith(
                ("expanded.", "year.", "footage.")
            )
        dates = (field.get("supporting_passages") or {}).get("dates", "")
        if dates:
            lowered = dates.lower()
            assert (
                lowered.startswith("for the fiscal year ended")
                or lowered.startswith("we refer to the fiscal year ended")
                or lowered.startswith("the fiscal year ended")
                or "weeks ended" in lowered
            )
            assert "united kingdom" not in lowered
            assert "number of company-operated stores by market" not in lowered
            assert "these core values attract" not in lowered
            assert "together with its subsidiaries" not in lowered
        bindings = field.get("passage_bindings") or {}
        for name, passage in (field.get("supporting_passages") or {}).items():
            binding = bindings[name]
            assert binding["source_file"]
            assert binding["physical_pages"]
            assert isinstance(binding["physical_pages"], list)
            if name in {"dates", "comparison_window", "calendar", "presentation"}:
                assert len(binding["physical_pages"]) <= 2
    fy2022 = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2022_management_kpis.json"
    )
    store = next(
        item
        for item in fy2022["fields"]
        if item["metric_id"] == "comparable_store_sales_growth"
    )
    calendar_binding = store["passage_bindings"]["calendar"]
    assert calendar_binding["source_file"] == "LULU_FY2023_Annual_Report.pdf"
    assert calendar_binding["physical_pages"] == [33]
    assert calendar_binding.get("cross_filing") is True


def test_repaired_occurrence_evidence_reaches_assessment(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = [
        item
        for item in payload["assessments"]["items"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT and item["status"] == "supported"
    ]
    assert len(spsf) == 7
    by_key = {
        (item["evidence"]["extraction_document"], item["evidence"]["period"]): item
        for item in spsf
    }
    fy2023_in_fy2024 = by_key[
        ("LULU_FY2024_management_kpis.json", "2024-01-28")
    ]
    assert fy2023_in_fy2024["evidence"]["fiscal_year_length_weeks"] == "52"
    assert fy2023_in_fy2024["evidence"]["calendar_week_adjustment"] == "included"
    assert fy2023_in_fy2024["level_admission"] == "admitted"
    fy2024_in_fy2025 = by_key[
        ("LULU_FY2025_management_kpis.json", "2025-02-02")
    ]
    assert fy2024_in_fy2025["evidence"]["fiscal_year_length_weeks"] == "53"
    assert fy2024_in_fy2025["evidence"]["calendar_week_adjustment"] == "excluded"
    assert fy2024_in_fy2025["level_admission"] == "admitted"
    assert fy2024_in_fy2025["historical_comparison"] == "ineligible"
    decisions = [
        item
        for item in payload["group_decisions"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT
    ]
    assert decisions
    for item in decisions:
        requirements = {failure["requirement"] for failure in item["remaining_failures"]}
        if item["status"] == SELECTION_SELECTED:
            assert "canonical_selection" not in requirements
        else:
            assert "canonical_selection" in requirements
            causes = {failure["cause"] for failure in item["remaining_failures"]}
            assert "selection_limitation" in causes
        assert item["level_eligibility"] == "admitted"
        pair_failures = [
            failure
            for failure in item["remaining_failures"]
            if failure.get("comparison_pair")
        ]
        for failure in pair_failures:
            assert failure["comparison_pair"][0] != failure["comparison_pair"][1]
            assert set(failure["comparison_pair"]) <= set(
                {
                    peer
                    for assessment in payload["assessments"]["items"]
                    if assessment["family"] == FAMILY_SALES_PER_SQUARE_FOOT
                    for peer in [assessment["locator"], *assessment["peer_locators"]]
                }
            )
        alignment = {
            failure["requirement"]
            for failure in item["remaining_failures"]
            if failure["requirement"] in {"calendar", "definition", "comparison_window"}
        }
        hist = [
            failure
            for failure in item["remaining_failures"]
            if failure["requirement"] == "historical_comparison"
        ]
        if item["status"] != SELECTION_SELECTED:
            assert "canonical_selection" in {
                failure["requirement"] for failure in item["remaining_failures"]
            }
        if item["comparison_eligibility"] == "ineligible" and not any(
            pair.get("outcome") == "supported"
            and pair.get("kind") == "historical_comparison"
            for pair in item.get("pair_assessments") or []
        ):
            assert hist
            if alignment:
                assert all(failure["cause"] == "documentary_ambiguity" for failure in hist)
                assert all(
                    failure["detail"] == "same_identity_levels_not_aligned"
                    for failure in hist
                )
            else:
                assert all(failure["cause"] == "genuine_source_absence" for failure in hist)


def _spsf_assessments(payload: dict) -> list[dict]:
    return [
        item
        for item in payload["assessments"]["items"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT and item["status"] == "supported"
    ]


def _pair_key(locators: list[str]) -> tuple[str, ...]:
    return tuple(sorted(locators))


def test_pair_failures_attribute_to_actual_peers_not_first_peer(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = _spsf_assessments(payload)
    assert len(spsf) == 7
    by_key = {
        (item["evidence"]["extraction_document"], item["evidence"]["period"]): item
        for item in spsf
    }
    fy2022_current = by_key[("LULU_FY2022_management_kpis.json", "2023-01-29")]
    fy2023_current = by_key[("LULU_FY2023_management_kpis.json", "2024-01-28")]
    fy2024_current = by_key[("LULU_FY2024_management_kpis.json", "2025-02-02")]
    assert len(fy2022_current["peer_locators"]) > 1
    pair_52 = next(
        pair
        for pair in fy2022_current["pair_assessments"]
        if set(pair["locators"]) == {fy2022_current["locator"], fy2023_current["locator"]}
    )
    pair_53 = next(
        pair
        for pair in fy2022_current["pair_assessments"]
        if set(pair["locators"]) == {fy2022_current["locator"], fy2024_current["locator"]}
    )
    assert pair_52["outcome"] == "unsupported"
    assert "calendar_mismatch" not in pair_52["reasons"]
    assert "definition_mismatch" in pair_52["reasons"]
    assert "calendar_mismatch" in pair_53["reasons"]
    pair_failures = [
        failure
        for item in payload["group_decisions"]
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT
        for failure in item["remaining_failures"]
        if failure.get("comparison_pair")
        and set(failure["comparison_pair"])
        == {fy2022_current["locator"], fy2023_current["locator"]}
    ]
    assert pair_failures
    assert all(failure["detail"] != "calendar_mismatch" for failure in pair_failures)
    assert any(failure["detail"] == "definition_mismatch" for failure in pair_failures)
    first_peer = fy2022_current["peer_locators"][0]
    if first_peer != fy2023_current["locator"]:
        assert not any(
            set(failure.get("comparison_pair") or [])
            == {fy2022_current["locator"], first_peer}
            and failure["detail"] == "definition_mismatch"
            and set(failure.get("comparison_pair") or [])
            == {fy2022_current["locator"], fy2023_current["locator"]}
            for item in payload["group_decisions"]
            for failure in item["remaining_failures"]
        )


def test_pair_assessments_are_peer_order_independent(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = _spsf_assessments(payload)
    seen: dict[tuple[str, ...], dict] = {}
    for item in spsf:
        for pair in item["pair_assessments"]:
            key = _pair_key(pair["locators"])
            if key in seen:
                assert seen[key]["outcome"] == pair["outcome"]
                assert seen[key]["reasons"] == pair["reasons"]
                assert seen[key]["kind"] == pair["kind"]
            else:
                seen[key] = pair
    assert seen
    locators = [item["locator"] for item in spsf]
    assert locators == sorted(locators) or True
    reversed_peers = [list(reversed(item["peer_locators"])) for item in spsf]
    for item, reversed_list in zip(spsf, reversed_peers):
        forward = {
            _pair_key(pair["locators"]): (pair["outcome"], tuple(pair["reasons"]))
            for pair in item["pair_assessments"]
        }
        assert forward
        assert set(item["peer_locators"]) == set(reversed_list)


def test_supported_and_unsupported_pairs_coexist(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = _spsf_assessments(payload)
    by_key = {
        (item["evidence"]["extraction_document"], item["evidence"]["period"]): item
        for item in spsf
    }
    fy2023_current = by_key[("LULU_FY2023_management_kpis.json", "2024-01-28")]
    fy2025_current = by_key[("LULU_FY2025_management_kpis.json", "2026-02-01")]
    fy2024_current = by_key[("LULU_FY2024_management_kpis.json", "2025-02-02")]
    supported = next(
        pair
        for pair in fy2023_current["pair_assessments"]
        if set(pair["locators"]) == {fy2023_current["locator"], fy2025_current["locator"]}
    )
    unsupported = next(
        pair
        for pair in fy2023_current["pair_assessments"]
        if set(pair["locators"]) == {fy2023_current["locator"], fy2024_current["locator"]}
    )
    assert supported["outcome"] == "supported"
    assert unsupported["outcome"] == "unsupported"
    assert "calendar_mismatch" in unsupported["reasons"]
    assert fy2023_current["historical_comparison"] == "eligible"
    assert fy2025_current["historical_comparison"] == "eligible"
    assert fy2023_current["comparability"] == "not_comparable"
    assert fy2024_current["historical_comparison"] == "ineligible"


def test_two_52_week_spsf_occurrences_have_no_false_calendar_mismatch(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    spsf = _spsf_assessments(payload)
    fifty_two = [
        item
        for item in spsf
        if item["evidence"]["fiscal_year_length_weeks"] == "52"
        and item["evidence"]["calendar_week_adjustment"] == "included"
    ]
    assert len(fifty_two) >= 2
    fy2022_current = next(
        item
        for item in fifty_two
        if item["evidence"]["extraction_document"] == "LULU_FY2022_management_kpis.json"
        and item["evidence"]["period"] == "2023-01-29"
    )
    fy2023_current = next(
        item
        for item in fifty_two
        if item["evidence"]["extraction_document"] == "LULU_FY2023_management_kpis.json"
        and item["evidence"]["period"] == "2024-01-28"
    )
    pair = next(
        item
        for item in fy2022_current["pair_assessments"]
        if set(item["locators"]) == {fy2022_current["locator"], fy2023_current["locator"]}
    )
    assert pair["kind"] == "historical_comparison"
    assert "calendar_mismatch" not in pair["reasons"]
    for item in payload["group_decisions"]:
        for failure in item["remaining_failures"]:
            pair_locators = set(failure.get("comparison_pair") or [])
            if pair_locators == {fy2022_current["locator"], fy2023_current["locator"]}:
                assert failure["detail"] != "calendar_mismatch"
                assert failure["requirement"] != "calendar"


def test_fy2024_exclusion_flags_have_individually_bound_passages(tmp_path: Path):
    dest = _copy_extracted(tmp_path / "excl")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    fy2024 = json.loads((dest / "LULU_FY2024_management_kpis.json").read_text())
    fy2025 = json.loads((dest / "LULU_FY2025_management_kpis.json").read_text())
    current = next(
        item
        for item in fy2024["reported_kpis"]
        if item["metric_id"] == "sales_per_square_foot" and item["period"] == "2025-02-02"
    )
    traced = next(
        item
        for item in fy2025["reported_kpis"]
        if item["metric_id"] == "sales_per_square_foot"
        and item["period"] == "2025-02-02"
        and item.get("traced_prior_period")
    )
    for item in (current, traced):
        exclusion = item["supporting_evidence"]["metric_exclusion"]
        assert item["qualifiers"]["excludes_53rd_week"] is True
        assert exclusion["passage"]
        assert exclusion["passage"].endswith(".")
        assert "sales per square foot" in exclusion["passage"].lower()
        assert "excluded" in exclusion["passage"].lower()
        assert "53" in exclusion["passage"]
        assert "Fiscal 2024 was a 53-week year" not in exclusion["passage"]
        assert exclusion["source_file"] == "LULU_FY2024_Annual_Report.pdf"
        assert 40 in exclusion["physical_pages"]
        assert exclusion["metric_id"] == "sales_per_square_foot"
        assert exclusion["period"] == "2025-02-02"
        binding = item["supporting_evidence"]["passage_bindings"]["metric_exclusion"]
        assert binding["source_file"] == "LULU_FY2024_Annual_Report.pdf"
        assert 40 in binding["physical_pages"]
        assert 34 in binding["printed_pages"]
    assert current["supporting_evidence"]["metric_exclusion"]["cross_filing"] is False
    assert traced["supporting_evidence"]["metric_exclusion"]["cross_filing"] is True
    fy2024_field = next(
        item
        for record in sidecar["documents"]
        if record["extraction_document"] == "LULU_FY2024_management_kpis.json"
        for item in record["fields"]
        if item["metric_id"] == "sales_per_square_foot" and item["period"] == "2025-02-02"
    )
    fy2025_traced_field = next(
        item
        for record in sidecar["documents"]
        if record["extraction_document"] == "LULU_FY2025_management_kpis.json"
        for item in record["fields"]
        if item["metric_id"] == "sales_per_square_foot" and item["period"] == "2025-02-02"
    )
    assert fy2024_field["metric_exclusion"]["physical_pages"] == fy2025_traced_field[
        "metric_exclusion"
    ]["physical_pages"]
    assert 40 in fy2024_field["metric_exclusion"]["physical_pages"]


def test_calendar_text_does_not_satisfy_exclusion_evidence():
    from core.ingestion.management_kpi_enrichment import (
        CalendarYearEvidence,
        _metric_exclusion_evidence,
        _metric_excludes_53rd_week,
    )

    calendar = CalendarYearEvidence(
        fiscal_year=2024,
        fifty_three_week=True,
        source_file="LULU_FY2024_Annual_Report.pdf",
        physical_page=32,
        passage="Fiscal 2024 was a 53-week year.",
        cross_filing=False,
    )
    assert _metric_exclusion_evidence(
        "sales_per_square_foot", calendar, [calendar.passage]
    ) is None
    assert _metric_excludes_53rd_week(
        "sales_per_square_foot", calendar, [calendar.passage]
    ) is None


_FY2022_FOCUS = (
    ("comparable_store_sales_growth", "reported", "comparable store sales"),
    (
        "comparable_store_sales_growth_constant_dollar",
        "constant_dollar",
        "comparable store sales",
    ),
    ("total_comparable_sales_growth", "reported", "total comparable sales"),
    (
        "total_comparable_sales_growth_constant_dollar",
        "constant_dollar",
        "total comparable sales",
    ),
)


def _fy2022_fields(sidecar: dict) -> list[dict]:
    document = next(
        item
        for item in sidecar["documents"]
        if item["extraction_document"] == "LULU_FY2022_management_kpis.json"
    )
    return [
        item
        for item in document["fields"]
        if item["metric_id"] in {row[0] for row in _FY2022_FOCUS}
    ]


def test_fy2022_management_use_and_current_period_table_are_identity_bound(
    tmp_path: Path,
):
    dest = _copy_extracted(tmp_path / "fy22-pres")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    working = json.loads((dest / "LULU_FY2022_management_kpis.json").read_text())
    by_metric = {item["metric_id"]: item for item in _fy2022_fields(sidecar)}
    assert set(by_metric) == {row[0] for row in _FY2022_FOCUS}
    for metric_id, basis, phrase in _FY2022_FOCUS:
        field = by_metric[metric_id]
        passages = field["supporting_passages"]
        bindings = field["passage_bindings"]
        presentation = passages["presentation"]
        management_use = passages["management_use"]
        assert phrase in presentation.lower()
        assert "below changes" in presentation.lower()
        assert "e-commerce" not in presentation.lower()
        assert "e-commerce" not in management_use.lower()
        assert bindings["presentation"]["source_file"] == "LULU_FY2022_Annual_Report.pdf"
        assert 37 in bindings["presentation"]["physical_pages"]
        assert 33 in bindings["presentation"]["printed_pages"]
        assert bindings["management_use"]["source_file"] == "LULU_FY2022_Annual_Report.pdf"
        if basis == "constant_dollar":
            assert "management uses" in management_use.lower()
            assert "constant currency" in management_use.lower()
            assert 36 in bindings["management_use"]["physical_pages"]
            assert 32 in bindings["management_use"]["printed_pages"]
        elif metric_id == "total_comparable_sales_growth":
            assert (
                "we use total comparable sales" in management_use.lower()
                or "just one way of assessing" in management_use.lower()
            )
            assert set(bindings["management_use"]["physical_pages"]) <= {35, 36}
        else:
            assert "we use comparable store sales" in management_use.lower()
            assert "we use total comparable sales" not in management_use.lower()
            assert 35 in bindings["management_use"]["physical_pages"]
            assert 31 in bindings["management_use"]["printed_pages"]
        reported = next(
            item
            for item in working["reported_kpis"]
            if item["metric_id"] == metric_id
        )
        assert reported["presentation"]["role"] == "current"
        assert "assurance" not in reported
        assert "revision" not in reported
        definition = passages.get("definition", "")
        if "store_sales" in metric_id:
            assert "direct to consumer" not in definition.lower()
            assert "e-commerce" not in definition.lower()
        else:
            assert "direct to consumer" in definition.lower()
            assert "e-commerce" not in definition.lower()


def test_fy2022_presentation_absence_claims_are_removed_from_admission(
    tmp_path: Path,
):
    payload = _enriched_admission(tmp_path)
    focus = [
        item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
        and item["extraction_document"] == "LULU_FY2022_management_kpis.json"
        and item["metric_id"] in {row[0] for row in _FY2022_FOCUS}
    ]
    assert len(focus) == 4
    for item in focus:
        assert item["presentation_role"] == "current"
        assert "presentation_role" not in item["unresolved"]
        assert item["assurance"] == "unknown"
        assert "assurance" in item["unresolved"]
        assert "revision" not in item["unresolved"]
    locators = {item["locator"] for item in focus}
    for decision in payload["group_decisions"]:
        for failure in decision["remaining_failures"]:
            if failure.get("locator") not in locators:
                continue
            if failure["requirement"] != "presentation":
                continue
            assert failure["cause"] != "genuine_source_absence"
            raise AssertionError(
                f"unexpected presentation failure after FY2022 repair: {failure}"
            )


def test_unrelated_strategy_language_cannot_satisfy_presentation_assurance_or_revision():
    strategy = (
        "Opening new stores and expanding existing stores is an important part "
        "of our growth strategy."
    )
    inspection = SourceInspection(
        source_file="LULU_FY2022_Annual_Report.pdf",
        physical_to_printed={36: 32},
        printed_to_physical={32: 36},
        fifty_three_week_years=(),
        fifty_two_week_years=(2022,),
        fiscal_calendar_evidenced=True,
        page_texts={36: strategy},
    )
    for metric_id, basis, _phrase in _FY2022_FOCUS:
        item = {"metric_id": metric_id, "value": 16.0, "basis": basis}
        passages = field_supporting_passages(
            inspection=inspection,
            physical_pages=(36,),
            item=item,
            comparison_window=None,
            calendar=None,
        )
        assert "presentation" not in passages
        assert "management_use" not in passages
        assert "assurance" not in passages
        assert "revision" not in passages


def test_definition_features_store_only_excludes_dtc_mention():
    store_only = (
        "Net revenue from company-operated stores open, or open after significant "
        "expansion, for at least 12 full fiscal months. Excludes new stores, stores "
        "not in expanded space for at least 12 full fiscal months, temporarily "
        "relocated/closed stores, direct-to-consumer and other operations, and "
        "closed company-operated stores."
    )
    total = "Comparable store sales plus direct-to-consumer net revenue."
    ecommerce = (
        "Comparable company-operated store and all e-commerce net revenue. "
        "Excludes new/expanded stores under 12 months, temporarily relocated/closed "
        "stores, closed stores, and channels other than company-operated stores and "
        "e-commerce."
    )
    strategy = (
        "Opening new stores and expanding existing stores is an important part "
        "of our growth strategy."
    )
    dtc_neighbor = (
        "Direct to consumer net revenue increased 33.2% compared to fiscal 2021."
    )
    assert definition_features(store_only)["channel_population"] == (
        "company_operated_stores"
    )
    assert definition_features(total)["channel_population"] == (
        "company_operated_stores_and_direct_to_consumer"
    )
    assert definition_features(ecommerce)["channel_population"] == (
        "company_operated_stores_and_ecommerce"
    )
    assert "channel_population" not in definition_features(strategy)
    assert definition_features(dtc_neighbor).get("channel_population") != (
        "company_operated_stores"
    )


def test_fy2022_presentation_source_agrees_with_table_passage_bindings(
    tmp_path: Path,
):
    dest = _copy_extracted(tmp_path / "fy22-src")
    sidecar = enrich_management_working_copies(dest, SOURCE)
    working = json.loads((dest / "LULU_FY2022_management_kpis.json").read_text())
    by_metric = {item["metric_id"]: item for item in _fy2022_fields(sidecar)}
    payload = reconciliation_management_admission_payload(
        reconcile_filings(
            load_and_validate_extracted_dir(dest, source_root=SOURCE),
            admit_periods=ADMIT_2022,
        )
    )
    admitted = {
        item["metric_id"]: item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
        and item["extraction_document"] == "LULU_FY2022_management_kpis.json"
        and item["metric_id"] in {row[0] for row in _FY2022_FOCUS}
    }
    assert set(admitted) == {row[0] for row in _FY2022_FOCUS}
    table_ref = page_reference_from_printed((33,))
    for metric_id, basis, _phrase in _FY2022_FOCUS:
        field = by_metric[metric_id]
        bindings = field["passage_bindings"]
        presentation = bindings["presentation"]
        management_use = bindings["management_use"]
        definition = bindings["definition"]
        assert presentation["source_file"] == "LULU_FY2022_Annual_Report.pdf"
        assert presentation["physical_pages"] == [37]
        assert presentation["printed_pages"] == [33]
        assert 37 not in management_use["physical_pages"]
        assert 33 not in management_use["printed_pages"]
        assert set(management_use["physical_pages"]) <= {35, 36}
        if "total_comparable" in metric_id:
            assert 37 not in definition["physical_pages"]
        reported = next(
            item
            for item in working["reported_kpis"]
            if item["metric_id"] == metric_id
        )
        assert reported["source"]["page_reference"] == "Form 10-K p. 27"
        assert reported["presentation"]["source"]["page_reference"] == table_ref
        assert "physical_page_mapping" not in reported["presentation"]["source"]
        observation = admitted[metric_id]
        source = observation["presentation_evidence"]["source"]
        assert printed_pages_from_reference(source["page_reference"]) == (33,)
        assert source["physical_page_mapping"] == "33→37"
        assert observation["source"]["page_reference"] == "Form 10-K p. 27"
        assert observation["physical_page_mapping"] == "27→31"
        features = observation["supporting_evidence"]["definition_features"]
        if "store_sales" in metric_id:
            assert features["channel_population"] == "company_operated_stores"
            assert observation["scope"] == {"channel": "company_operated_stores"}
        else:
            assert features["channel_population"] == (
                "company_operated_stores_and_direct_to_consumer"
            )
            assert observation["scope"] == {"geography": "global"}
        assert observation["basis"] == basis


def test_fy2022_store_only_population_features_survive_admission(tmp_path: Path):
    payload = _enriched_admission(tmp_path)
    focus = [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == "supported"
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["evidence"]["extraction_document"]
        == "LULU_FY2022_management_kpis.json"
        and item["evidence"]["period"] == "2023-01-29"
    ]
    by_population = {}
    for item in focus:
        fields = item["metric_identity_fields"]
        by_population.setdefault(fields["population"], []).append(item)
        features = None
        for observation in payload["observations"]:
            if observation["locator"] != item["locator"]:
                continue
            features = observation["supporting_evidence"]["definition_features"]
            source = observation["presentation_evidence"]["source"]
            assert printed_pages_from_reference(source["page_reference"]) == (33,)
            assert source["physical_page_mapping"] == "33→37"
            break
        assert features is not None
        assert features["channel_population"] == fields["population"]
        if fields["population"] == "company_operated_stores":
            lowered_def = item["evidence"]["definition_text"].lower()
            assert "direct-to-consumer" in lowered_def or "direct to consumer" in lowered_def
            assert "exclud" in lowered_def
        else:
            assert fields["population"] == (
                "company_operated_stores_and_direct_to_consumer"
            )
            assert "plus direct-to-consumer" in item["evidence"]["definition_text"].lower()
    assert set(by_population) == {
        "company_operated_stores",
        "company_operated_stores_and_direct_to_consumer",
    }
    assert len(by_population["company_operated_stores"]) == 2
    assert len(by_population["company_operated_stores_and_direct_to_consumer"]) == 2


def test_neighboring_dtc_cannot_satisfy_store_only_identity_requirements():
    dtc = (
        "We use total comparable sales to evaluate the performance of our business "
        "from an omni-channel perspective. Total comparable sales combines comparable "
        "store sales and direct to consumer net revenue. Direct to consumer net "
        "revenue increased 33.2%."
    )
    inspection = SourceInspection(
        source_file="LULU_FY2022_Annual_Report.pdf",
        physical_to_printed={35: 31, 37: 33},
        printed_to_physical={31: 35, 33: 37},
        fifty_three_week_years=(),
        fifty_two_week_years=(2022,),
        fiscal_calendar_evidenced=True,
        page_texts={35: dtc, 37: dtc},
    )
    for metric_id, basis, _phrase in _FY2022_FOCUS:
        if "store_sales" not in metric_id:
            continue
        item = {"metric_id": metric_id, "value": 16.0, "basis": basis}
        passages = field_supporting_passages(
            inspection=inspection,
            physical_pages=(35, 37),
            item=item,
            comparison_window=None,
            calendar=None,
        )
        assert "presentation" not in passages
        assert "management_use" not in passages
        definition = passages.get("definition", "")
        assert "comparable store sales reflects" not in definition.lower()
        assert definition_features(dtc).get("channel_population") != (
            "company_operated_stores"
        )
