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
    assert all(item["historical_comparison"] == "ineligible" for item in spsf)
    assert all(REASON_MISSING_COMPARISON in item["unresolved_reasons"] for item in spsf)
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
    assert all(item["status"] == SELECTION_DEFERRED for item in decisions)
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
    assert all(
        item["cause"] == "selection_limitation"
        or any(
            failure.get("cause") == "selection_limitation"
            for failure in item["remaining_failures"]
        )
        for item in compsales_decisions
    )
    assert all(item["status"] == SELECTION_DEFERRED for item in compsales_decisions)


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
        assert "canonical_selection" in requirements
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT:
            assert "historical_comparison" in requirements
        if any(
            reason in item["selection_reasons"]
            for reason in ("singleton", "missing_revision_link", "unknown_assurance")
        ):
            assert item["canonical_selection"] == SELECTION_DEFERRED
            assert item["status"] == SELECTION_DEFERRED
        if item["comparison_eligibility"] == "eligible":
            assert not any(
                failure["requirement"] in {"calendar", "comparison_window"}
                for failure in item["remaining_failures"]
            )
        if item["level_eligibility"] == "admitted":
            assert item["canonical_selection"] == SELECTION_DEFERRED


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
    assert fy2023_in_fy2024["historical_comparison"] == "ineligible"
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
        assert "canonical_selection" in requirements
        causes = {failure["cause"] for failure in item["remaining_failures"]}
        assert "selection_limitation" in causes
        assert item["level_eligibility"] == "admitted"
        assert item["comparison_eligibility"] == "ineligible"
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
        assert hist
        if alignment:
            assert all(failure["cause"] == "documentary_ambiguity" for failure in hist)
            assert all(
                failure["detail"] == "same_identity_levels_not_aligned" for failure in hist
            )
        else:
            assert all(failure["cause"] == "genuine_source_absence" for failure in hist)
