"""Step 9M.1 / 9M.2A — Fast Retailing filing-JSON + build-unblocker acceptance."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from core.data.standardized_io import standardized_from_payload
from core.ingestion.filing_json import load_extracted_filing
from core.ingestion.filing_validator import validate_extracted_filing
from core.ingestion.reconciler import reconcile_financials
from core.engine.reference_model import ReferenceModelBuilder
from core.model.classification import (
    UnclassifiedBalanceSheetLineError,
    check_reformulation_integrity,
    classify_balance_sheet_line,
    is_balance_sheet_subtotal,
    reformulate_balance_sheet,
)
from core.model.financial_math import compute_anchor
from core.model.judgment import classification_judgment_cases
from core.model.lease_liability import (
    compute_lease_liability_series,
    lease_liability_applicable,
    resolve_lease_liability_source,
)
from core.model.period_axis import canonical_fiscal_periods
import pytest
from scripts.audit_fast_retailing_benchmark import run_audit

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "fast_retailing"
MANIFEST = BENCH / "source_manifest.json"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"
BASELINE = BENCH / "BASELINE.md"
GAPS = BENCH / "GAPS.md"
AUDIT = ROOT / "scripts" / "audit_fast_retailing_benchmark.py"

G2_CONCEPT_CODES = {
    "other_financial_assets_current": "financial_asset_current_financial_vs_operating",
    "financial_assets_noncurrent": "financial_asset_noncurrent_financial_vs_operating",
    "derivative_financial_assets_current": "financial_asset_current_financial_vs_operating",
    "derivative_financial_assets_noncurrent": "financial_asset_noncurrent_financial_vs_operating",
    "other_financial_liabilities_current": "financial_liability_current_financial_vs_operating",
    "financial_liabilities_noncurrent": "financial_liability_noncurrent_financial_vs_operating",
    "derivative_financial_liabilities_current": "financial_liability_current_financial_vs_operating",
    "derivative_financial_liabilities_noncurrent": "financial_liability_noncurrent_financial_vs_operating",
}
G2_DEFAULT_CATEGORY = {
    "other_financial_assets_current": "Financial Asset",
    "financial_assets_noncurrent": "Financial Asset",
    "derivative_financial_assets_current": "Financial Asset",
    "derivative_financial_assets_noncurrent": "Financial Asset",
    "other_financial_liabilities_current": "Financial Liability",
    "financial_liabilities_noncurrent": "Financial Liability",
    "derivative_financial_liabilities_current": "Financial Liability",
    "derivative_financial_liabilities_noncurrent": "Financial Liability",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_source_manifest_locks_five_pdfs():
    manifest = _load_json(MANIFEST)
    assert len(manifest["sources"]) == 5
    assert {s["fiscal_year"] for s in manifest["sources"]} == {2021, 2022, 2023, 2024, 2025}
    for entry in manifest["sources"]:
        path = ROOT / entry["path"]
        assert path.is_file()
        data = path.read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]


def test_extracted_filings_are_independent_v1_artifacts():
    years = {2021, 2022, 2023, 2024, 2025}
    files = sorted(EXTRACTED.glob("FY*.json"))
    assert {int(p.stem.replace("FY", "")) for p in files} == years
    for path in files:
        filing = load_extracted_filing(path)
        assert filing.schema_version == "1.0"
        assert filing.filing.source_sha256 == ""
        assert filing.income_statement
        assert filing.balance_sheet
        assert filing.cash_flow
        for row in (
            *filing.income_statement,
            *filing.balance_sheet,
            *filing.cash_flow,
        ):
            assert row.source.page > 0
            assert row.label
            assert row.section is not None
        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        assert report.computed_source_sha256


def test_generic_reconcile_is_deterministic_and_round_trips(tmp_path: Path):
    out1 = tmp_path / "r1"
    out2 = tmp_path / "r2"
    for out in (out1, out2):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "core",
                "reconcile",
                str(EXTRACTED),
                "--source-root",
                str(SOURCE),
                "-o",
                str(out),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "overlap_conflicts=" in completed.stdout

    for name in ("standardized.json", "provenance.json", "conflicts.json"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()

    # Refresh committed reconciled artifacts from the same command path.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(EXTRACTED),
            "--source-root",
            str(SOURCE),
            "-o",
            str(RECONCILED),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = _load_json(STD_JSON)
    fin = standardized_from_payload(payload)
    assert fin.ticker == "6288.HK"
    assert fin.company_name == "FAST RETAILING CO., LTD."
    assert fin.currency == "JPY"
    assert fin.units == "JPY in Millions"
    assert fin.jurisdiction == "JP"
    assert [p.end_date.isoformat() for p in fin.periods] == [
        "2021-08-31",
        "2022-08-31",
        "2023-08-31",
        "2024-08-31",
        "2025-08-31",
    ]
    assert fin.historical_shares is None
    assert {item.label for item in fin.income_statement}
    assert any(item.concept == "revenue" for item in fin.income_statement)


def _fy2025_value(fin, *, statement: str, concept: str | None = None, label: str | None = None):
    items = getattr(fin, statement)
    period = fin.periods[-1].end_date
    for item in items:
        if concept is not None and item.concept == concept:
            return item.values[period]
        if label is not None and item.label == label:
            return item.values[period]
    raise AssertionError(f"missing {statement} concept={concept!r} label={label!r}")


def test_migration_reproduces_fy2025_anchors_and_conflict_parity():
    """Generic pipeline must preserve Step 9M.0 selected anchors and conflicts."""
    payload = _load_json(STD_JSON)
    provenance = _load_json(PROV_JSON)
    conflicts = _load_json(CONFLICTS_JSON)
    fin = standardized_from_payload(payload)

    assert _fy2025_value(fin, statement="income_statement", concept="revenue") == 3_400_539
    assert (
        _fy2025_value(
            fin, statement="income_statement", label="Profit before income taxes"
        )
        == 650_574
    )
    assert _fy2025_value(fin, statement="income_statement", concept="tax_expense") == -191_421
    assert _fy2025_value(fin, statement="balance_sheet", concept="cash") == 893_239
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="property_plant_equipment")
        == 332_351
    )
    assert (
        _fy2025_value(fin, statement="balance_sheet", concept="lease_liability_current")
        == 126_830
    )
    assert (
        _fy2025_value(
            fin, statement="balance_sheet", concept="lease_liability_noncurrent"
        )
        == 386_670
    )
    assert (
        _fy2025_value(fin, statement="cash_flow", concept="operating_cash_flow") == 580_618
    )
    assert (
        _fy2025_value(fin, statement="cash_flow", concept="depreciation_amortization")
        == 216_492
    )
    assert (
        _fy2025_value(
            fin,
            statement="cash_flow",
            label="Payments for property, plant and equipment",
        )
        == -135_535
    )

    assert conflicts["overlap_conflict_count"] == 3
    assert provenance["overlap_conflict_count"] == 3
    assert len(conflicts["conflicts"]) == 3
    assert "supplemental_conflicts" in conflicts
    assert "supplemental_conflict_count" in conflicts
    assert conflicts["supplemental_conflict_count"] == len(
        conflicts["supplemental_conflicts"]
    )

    for section in ("note_facts", "share_facts"):
        for item in provenance[section]:
            assert item["source_file"]
            assert item["source_sha256"]
            assert item["filing_year"]
            assert item["source"]["page"] > 0

    notes = provenance["note_facts"]
    lease_total = next(
        n
        for n in notes
        if n["fact_type"] == "lease_liability_total" and n["period"] == "2025-08-31"
    )
    lease_interest = next(
        n
        for n in notes
        if n["fact_type"] == "lease_interest_expense" and n["period"] == "2025-08-31"
    )
    assert lease_total["value"] == 513_501
    assert lease_interest["value"] == 8_464
    assert lease_total["source_file"]
    assert lease_total["source_sha256"]
    assert lease_total["filing_year"]
    assert 126_830 + 386_670 == 513_500
    assert 459_153 == 433_009 + 26_143 + 1

    revenue_key = next(
        k
        for k, v in provenance["values"].items()
        if v.get("suggested_concept") == "revenue" and v.get("period") == "2025-08-31"
    )
    selected = provenance["values"][revenue_key]["selected"]
    assert selected["pdf_page"] == 3
    assert selected["source_file"] == "Fastretailing_CFS2025.pdf"
    assert selected["source_sha256"]
    assert "CFS2025.pdf" in selected["source_file"]


def test_audit_script_writes_baseline_and_stage_records():
    completed = subprocess.run(
        [sys.executable, str(AUDIT)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert BASELINE.is_file()
    assert GAPS.is_file()
    text = BASELINE.read_text(encoding="utf-8")
    for stage in (
        "1_source_fixture_load",
        "2_identity_validation",
        "3_reconciliation",
        "4_reference_model_builder",
        "5_workbook_generation",
        "6_blank_check",
        "7_filled_check",
    ):
        assert stage in text
    assert "Step 9M.2A" in text or "Step 9M.2B" in text or "Step 9M.2C" in text or "Step 9M.2D" in text or "Step 9M.3A" in text
    assert "pass" in completed.stdout or "fail" in completed.stdout


def test_fast_retailing_g1_balance_sheet_checksum_passes():
    fin = standardized_from_payload(_load_json(STD_JSON))
    report = reconcile_financials(fin)
    assert report.checksums["balance_sheet"] is True
    assert "Balance sheet does not balance for one or more periods" not in report.warnings


def test_fast_retailing_g2_generic_financial_rows_are_guided_judgments():
    fin = standardized_from_payload(_load_json(STD_JSON))
    seen = set()
    for item in fin.balance_sheet:
        concept = (item.concept or "").strip()
        if concept not in G2_CONCEPT_CODES:
            continue
        decision = classify_balance_sheet_line(item)
        assert decision.category == G2_DEFAULT_CATEGORY[concept]
        assert decision.ambiguous is True
        assert decision.judgment_code == G2_CONCEPT_CODES[concept]
        seen.add(concept)
    assert seen, "expected at least one known G2 financial-instrument concept"


OTHER_BALANCE_CONCEPT_CODES = {
    "other_current_assets": (
        "Operating Working Capital Asset",
        "other_current_asset_operating_vs_financial",
    ),
    "other_noncurrent_assets": (
        "Operating Long-Term Asset",
        "other_noncurrent_asset_operating_vs_financial",
    ),
    "other_current_liabilities": (
        "Operating Working Capital Liability",
        "other_current_liability_operating_vs_financial",
    ),
    "other_noncurrent_liabilities": (
        "Operating Long-Term Liability",
        "other_noncurrent_liability_operating_vs_financial",
    ),
}


def test_fast_retailing_other_balance_rows_are_guided_judgments():
    fin = standardized_from_payload(_load_json(STD_JSON))
    seen = set()
    for item in fin.balance_sheet:
        concept = (item.concept or "").strip()
        if concept not in OTHER_BALANCE_CONCEPT_CODES:
            continue
        category, code = OTHER_BALANCE_CONCEPT_CODES[concept]
        decision = classify_balance_sheet_line(item)
        assert decision.category == category
        assert decision.ambiguous is True
        assert decision.judgment_code == code
        seen.add(concept)
    assert seen == set(OTHER_BALANCE_CONCEPT_CODES)


def test_fast_retailing_audit_stages_pass_g1_and_no_longer_fail_on_g2():
    result = run_audit()
    stages = {stage.stage: stage for stage in result["stages"]}
    assert stages["1_source_fixture_load"].status == "pass"
    assert stages["2_identity_validation"].status == "pass"
    assert stages["3_reconciliation"].status == "pass"

    stage4 = stages["4_reference_model_builder"]
    if stage4.status == "fail" and stage4.exception_type == "UnclassifiedBalanceSheetLineError":
        message = stage4.message
        for concept, label_hint in (
            ("other_financial_assets_current", "Other financial assets"),
            ("financial_assets_noncurrent", "Financial assets"),
            ("derivative_financial_assets_current", "Derivative financial assets"),
            ("derivative_financial_assets_noncurrent", "Derivative financial assets"),
            ("other_financial_liabilities_current", "Other financial liabilities"),
            ("financial_liabilities_noncurrent", "Financial liabilities"),
            ("derivative_financial_liabilities_current", "Derivative financial liabilities"),
            ("derivative_financial_liabilities_noncurrent", "Derivative financial liabilities"),
        ):
            assert label_hint not in message, (
                f"Stage 4 still blocked by known G2 row {concept}: {message}"
            )
    elif stage4.status == "fail":
        # Non-G2 failure is acceptable and recorded by the audit; just ensure it is not
        # an UnclassifiedBalanceSheetLineError naming a known G2 concept label.
        assert "financial assets" not in stage4.message.lower() or (
            "Cannot safely classify" not in stage4.message
        )


def test_fast_retailing_audit_no_longer_fails_on_other_assets_or_liabilities():
    result = run_audit()
    stages = {stage.stage: stage for stage in result["stages"]}
    assert stages["3_reconciliation"].status == "pass"
    stage4 = stages["4_reference_model_builder"]
    if stage4.status == "fail" and stage4.exception_type == "UnclassifiedBalanceSheetLineError":
        message = stage4.message
        assert "Other assets" not in message
        assert "Other liabilities" not in message


DETERMINISTIC_FR_CONCEPTS = {
    "current_tax_liabilities": "Operating Working Capital Liability",
    "provisions_current": "Operating Working Capital Liability",
    "provisions_noncurrent": "Operating Long-Term Liability",
    "capital_stock": "Equity",
    "capital_surplus": "Equity",
    "other_components_of_equity": "Equity",
    "noncontrolling_interests": "Equity",
}


def test_fast_retailing_all_balance_sheet_detail_rows_are_classifiable():
    fin = standardized_from_payload(_load_json(STD_JSON))
    unsupported = []
    for item in fin.balance_sheet:
        if is_balance_sheet_subtotal(item):
            continue
        try:
            classify_balance_sheet_line(item)
        except UnclassifiedBalanceSheetLineError as exc:
            unsupported.append((item.label, item.concept, str(exc)))
    assert unsupported == []


def test_fast_retailing_deterministic_accounting_concepts_classify():
    fin = standardized_from_payload(_load_json(STD_JSON))
    seen = set()
    for item in fin.balance_sheet:
        concept = (item.concept or "").strip()
        if concept not in DETERMINISTIC_FR_CONCEPTS:
            continue
        decision = classify_balance_sheet_line(item)
        assert decision.category == DETERMINISTIC_FR_CONCEPTS[concept]
        assert decision.ambiguous is False
        assert decision.judgment_code is None
        seen.add(concept)
    assert seen == set(DETERMINISTIC_FR_CONCEPTS)


def test_fast_retailing_nci_equity_classification_does_not_close_g5():
    fin = standardized_from_payload(_load_json(STD_JSON))
    nci_item = next(
        item
        for item in fin.balance_sheet
        if (item.concept or "").strip() == "noncontrolling_interests"
    )
    decision = classify_balance_sheet_line(nci_item)
    assert decision.category == "Equity"
    # G5 parent/NCI attribution remains a separate product gap; this step only
    # provides structural Equity classification for consolidated reformulation.


def test_fast_retailing_audit_no_longer_fails_on_deterministic_9m2c_rows():
    result = run_audit()
    stages = {stage.stage: stage for stage in result["stages"]}
    assert stages["3_reconciliation"].status == "pass"
    stage4 = stages["4_reference_model_builder"]
    if stage4.status == "fail" and stage4.exception_type == "UnclassifiedBalanceSheetLineError":
        message = stage4.message
        for label in (
            "Current tax liabilities",
            "Provisions",
            "Capital stock",
            "Capital surplus",
            "Other components of equity",
            "Non-controlling interests",
        ):
            assert label not in message, f"Stage 4 still blocked by {label}: {message}"


_ASSET_REFORM_CATS = frozenset(
    {
        "Operating Working Capital Asset",
        "Operating Long-Term Asset",
        "Financial Asset",
    }
)
_LIABILITY_REFORM_CATS = frozenset(
    {
        "Operating Working Capital Liability",
        "Operating Long-Term Liability",
        "Financial Liability",
    }
)


def test_fast_retailing_rounding_envelope_accepts_committed_detail_gaps():
    fin = standardized_from_payload(_load_json(STD_JSON))
    periods = fin.fiscal_years() or fin.period_dates()
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.asset_detail_gap == (-4.0, -8.0, -8.0, -7.0, -8.0)
    assert reform.liability_detail_gap == (-6.0, -5.0, -6.0, -5.0, -6.0)
    assert reform.equity_gap == (2.0, -3.0, -1.0, -1.0, -2.0)

    asset_detail_count = sum(
        1 for d in reform.decisions.values() if d.category in _ASSET_REFORM_CATS
    )
    liability_detail_count = sum(
        1 for d in reform.decisions.values() if d.category in _LIABILITY_REFORM_CATS
    )
    assert asset_detail_count == 16
    assert liability_detail_count == 13

    check_reformulation_integrity(reform, periods)


def test_fast_retailing_audit_stages_pass_through_reformulation_integrity():
    result = run_audit()
    stages = {stage.stage: stage for stage in result["stages"]}
    assert stages["1_source_fixture_load"].status == "pass"
    assert stages["2_identity_validation"].status == "pass"
    assert stages["3_reconciliation"].status == "pass"
    stage4 = stages["4_reference_model_builder"]
    # Step 9M.2C blocker was ReformulationIntegrityError on classified-detail gaps.
    # After the count-derived envelope those gaps must be accepted.
    if stage4.status == "fail":
        assert stage4.exception_type != "ReformulationIntegrityError", (
            f"Stage 4 still fails on reformulation integrity: {stage4.message}"
        )


def test_fast_retailing_split_lease_liability_module_activates():
    """G3: BS current+non-current sum is the diagnostic source; Note 17 stays separate."""
    fin = standardized_from_payload(_load_json(STD_JSON))
    provenance = _load_json(PROV_JSON)
    periods = list(canonical_fiscal_periods(fin))
    fy2025 = periods[-1]

    current = next(
        item
        for item in fin.balance_sheet
        if (item.concept or "").strip() == "lease_liability_current"
    )
    noncurrent = next(
        item
        for item in fin.balance_sheet
        if (item.concept or "").strip() == "lease_liability_noncurrent"
    )
    assert current.values[fy2025] == pytest.approx(126_830.0)
    assert noncurrent.values[fy2025] == pytest.approx(386_670.0)

    source = resolve_lease_liability_source(fin)
    assert source is not None
    assert source.mode == "split"
    assert lease_liability_applicable(fin) is True

    series = compute_lease_liability_series(fin, periods, compute_anchor(fin, periods))
    assert series.lease_liability[-1] == pytest.approx(513_500.0)

    note_total = next(
        n
        for n in provenance["note_facts"]
        if n["fact_type"] == "lease_liability_total" and n["period"] == "2025-08-31"
    )
    assert note_total["value"] == 513_501
    # Contract: diagnostic = BS component sum; note aggregate is independent
    # documentary evidence; one-unit difference is preserved (no plug / substitution).
    assert series.lease_liability[-1] != note_total["value"]

    builder = ReferenceModelBuilder(fin)
    assert builder.lease_liability_series is not None
    assert len(builder.lease_liability_specs) == 18
    assert len(builder.expected_specs) == 312

    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    lease_cases = [c for c in cases if "lease" in c.label.lower()]
    assert len(lease_cases) == 2
    assert lease_cases[0].override_selector != lease_cases[1].override_selector


def test_fast_retailing_audit_stages_include_lease_module():
    result = run_audit()
    stages = {stage.stage: stage for stage in result["stages"]}
    for name in (
        "1_source_fixture_load",
        "2_identity_validation",
        "3_reconciliation",
        "4_reference_model_builder",
        "5_workbook_generation",
        "6_blank_check",
        "7_filled_check",
    ):
        assert stages[name].status == "pass", f"{name}: {stages[name].message}"
    assert "lease_specs=18" in (stages["4_reference_model_builder"].message or "")
    assert "expected_specs=312" in (stages["4_reference_model_builder"].message or "")
    assert "blank=312" in (stages["6_blank_check"].message or "")
    assert "total=312" in (stages["6_blank_check"].message or "")
    assert "correct=312" in (stages["7_filled_check"].message or "")
