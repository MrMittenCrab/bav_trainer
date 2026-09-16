"""Mixed-directory management-KPI admission and source-binding controls."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_json import load_extracted_filing, load_extracted_json_object
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_management_admission_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.management_kpi import (
    KIND_ANNUAL_FILING,
    KIND_MANAGEMENT_KPI,
    classify_extracted_payload,
    load_management_kpi_document,
)
from core.model.operating_kpi import compute_operating_kpi_series
from core.model.period_axis import canonical_fiscal_periods
from core.tests.test_operating_kpi_analysis import _independent_from_counts
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2022,
    P2023,
    P2024,
    P2025,
    P2026,
    _prepare_augmented,
    _validated_augmented,
)

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
ANNUAL_NAMES = (
    "LULU_FY2022.json",
    "LULU_FY2023.json",
    "LULU_FY2024.json",
    "LULU_FY2025.json",
)
MANAGEMENT_NAMES = (
    "LULU_FY2022_management_kpis.json",
    "LULU_FY2023_management_kpis.json",
    "LULU_FY2024_management_kpis.json",
    "LULU_FY2025_management_kpis.json",
)
REPORTED_COUNTS = {2022: 29, 2023: 36, 2024: 37, 2025: 33}
STORE_TOTALS = {2022: 655, 2023: 711, 2024: 767, 2025: 811}


def _copy_json(names: tuple[str, ...], dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(EXTRACTED / name, dest / name)
    return dest


def _bytes_by_name(directory: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(directory.glob("*.json"))
    }


def _canonicalize(payload: dict) -> dict:
    comparable = dict(payload)
    comparable.pop("historical_segment", None)
    comparable.pop("historical_operating_kpis", None)
    return comparable


def _statement_provenance(payload: dict) -> dict:
    comparable = dict(payload)
    comparable["note_facts"] = []
    comparable.pop("selected_geographic_segment_facts", None)
    comparable.pop("selected_operating_kpi_facts", None)
    return comparable


def test_directory_loader_no_longer_misparses_management_documents():
    for name in MANAGEMENT_NAMES:
        path = EXTRACTED / name
        payload = load_extracted_json_object(path)
        assert classify_extracted_payload(payload, path=path) == KIND_MANAGEMENT_KPI
        with pytest.raises(ValueError, match="company object is required"):
            load_extracted_filing(path)
        document = load_management_kpi_document(path)
        assert document.ticker == "LULU"
        assert document.fiscal_year == int(name.replace("LULU_FY", "").split("_")[0])

    mixed = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    assert len(mixed) == 4
    assert len(mixed.management_documents) == 4
    years = {filing.filing.fiscal_year for filing, _ in mixed}
    assert years == {2022, 2023, 2024, 2025}
    reported = []
    for bound in mixed.management_documents:
        reported.append(len(bound.document.reported))
        assert bound.ok
        assert bound.bound_source_sha256
        assert bound.bound_source_file.endswith("_Annual_Report.pdf")
    assert reported == [29, 36, 37, 33]


def test_dispatch_is_content_based_not_filename(tmp_path: Path):
    dest = tmp_path / "renamed"
    dest.mkdir()
    mapping = {
        "a-mgmt.json": MANAGEMENT_NAMES[0],
        "z-annual.json": ANNUAL_NAMES[0],
        "mid-mgmt.json": MANAGEMENT_NAMES[1],
        "mid-annual.json": ANNUAL_NAMES[1],
    }
    for dest_name, source_name in mapping.items():
        shutil.copy2(EXTRACTED / source_name, dest / dest_name)
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    assert {filing.filing.fiscal_year for filing, _ in validated} == {2022, 2023}
    assert {item.document.fiscal_year for item in validated.management_documents} == {
        2022,
        2023,
    }
    for bound in validated.management_documents:
        assert bound.document.extraction_document.endswith(".json")
        assert bound.bound_source_file.startswith("LULU_FY")


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda p: p.__setitem__("schema_version", "2.0"), "schema_version"),
        (lambda p: p.pop("reported_kpis"), "malformed management-KPI schema"),
        (lambda p: p.__setitem__("company", {"name": "x"}), "ambiguous"),
        (lambda p: p.__setitem__("filing", {"fiscal_year": 2022}), "ambiguous"),
    ],
)
def test_unknown_ambiguous_and_malformed_schemas_fail_closed(
    tmp_path: Path, mutate, match
):
    payload = json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    mutate(payload)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        classify_extracted_payload(load_extracted_json_object(path), path=path)
        load_management_kpi_document(path)
    assert json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8")) == original


def test_unknown_schema_fails_closed(tmp_path: Path):
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps({"schema_version": "1.0", "x": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown extracted schema"):
        classify_extracted_payload(load_extracted_json_object(path), path=path)


def test_malformed_values_and_dangling_definitions_fail_closed(tmp_path: Path):
    payload = json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    payload["reported_kpis"][0]["value"] = "655"
    path = tmp_path / "bad-value.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="must be numeric"):
        load_management_kpi_document(path)

    payload = copy.deepcopy(original)
    payload["reported_kpis"][0]["definition_id"] = "missing_definition"
    path = tmp_path / "dangling.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="dangling definition_id"):
        load_management_kpi_document(path)
    assert json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8")) == original


def test_orphan_and_conflicting_bindings_fail_closed(tmp_path: Path):
    extracted = _copy_json(ANNUAL_NAMES[:1] + MANAGEMENT_NAMES[:1], tmp_path / "orphan")
    payload = json.loads((extracted / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    payload["ticker"] = "OTHER"
    (extracted / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="orphan management-KPI"):
        load_and_validate_extracted_dir(extracted, source_root=SOURCE)

    payload = copy.deepcopy(original)
    payload["report"]["fiscal_year_end"] = "2023-01-30"
    (extracted / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="conflicting management-KPI binding"):
        load_and_validate_extracted_dir(extracted, source_root=SOURCE)

    payload = copy.deepcopy(original)
    payload["report"]["source_file"] = "../escaped.pdf"
    (extracted / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="conflicting management-KPI binding"):
        load_and_validate_extracted_dir(extracted, source_root=SOURCE)


def test_source_hash_failure_on_bound_filing_fails_closed(tmp_path: Path):
    extracted = _copy_json(ANNUAL_NAMES[:1] + MANAGEMENT_NAMES[:1], tmp_path / "hash")
    payload = json.loads((extracted / ANNUAL_NAMES[0]).read_text(encoding="utf-8"))
    original_mgmt = (extracted / MANAGEMENT_NAMES[0]).read_bytes()
    payload["filing"]["source_sha256"] = "1" * 64
    (extracted / ANNUAL_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    validated = load_and_validate_extracted_dir(extracted, source_root=SOURCE)
    assert not validated[0][1].ok
    assert any(issue.code == "source_hash_mismatch" for issue in validated[0][1].errors)
    assert (extracted / MANAGEMENT_NAMES[0]).read_bytes() == original_mgmt


def test_mixed_directory_admits_all_135_observations(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    annual_only = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    reversed_dir = tmp_path / "reversed"
    reversed_dir.mkdir()
    for index, name in enumerate(reversed(ANNUAL_NAMES + MANAGEMENT_NAMES)):
        shutil.copy2(EXTRACTED / name, reversed_dir / f"{index:02d}-{name}")

    annual_validated = load_and_validate_extracted_dir(annual_only, source_root=SOURCE)
    mixed_validated = load_and_validate_extracted_dir(mixed, source_root=SOURCE)
    reversed_validated = load_and_validate_extracted_dir(reversed_dir, source_root=SOURCE)

    annual_reconciled = reconcile_filings(annual_validated, admit_periods=ADMIT_2022)
    mixed_reconciled = reconcile_filings(mixed_validated, admit_periods=ADMIT_2022)
    reversed_reconciled = reconcile_filings(reversed_validated, admit_periods=ADMIT_2022)

    annual_fin = standardize_reconciled(annual_reconciled)
    mixed_fin = standardize_reconciled(mixed_reconciled)
    reversed_fin = standardize_reconciled(reversed_reconciled)
    assert _canonicalize(standardized_to_payload(annual_fin)) == _canonicalize(
        standardized_to_payload(mixed_fin)
    )
    assert _canonicalize(standardized_to_payload(mixed_fin)) == _canonicalize(
        standardized_to_payload(reversed_fin)
    )
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None

    annual_prov = reconciliation_provenance_payload(annual_reconciled)
    mixed_prov = reconciliation_provenance_payload(mixed_reconciled)
    assert _statement_provenance(annual_prov) == _statement_provenance(mixed_prov)
    assert "management_kpi_admission" not in mixed_prov
    assert reconciliation_conflicts_payload(annual_reconciled) == (
        reconciliation_conflicts_payload(mixed_reconciled)
    )

    admission = mixed_reconciled.management_admission
    assert admission is not None
    assert admission.status == "admitted_unreconciled"
    reported = [item for item in admission.observations if item.kind == "reported_kpi"]
    assert len(reported) == 135
    counts = {}
    for item in reported:
        counts[item.filing_year] = counts.get(item.filing_year, 0) + 1
    assert counts == REPORTED_COUNTS
    assert len(admission.definitions) == 9
    targets = [item for item in admission.observations if item.kind == "management_target"]
    assert len(targets) == 3
    assert all(item.historical_role == "nonhistorical" for item in targets)
    totals = {
        item.filing_year: item.value
        for item in admission.observations
        if item.kind == "store_count_total"
    }
    assert totals == STORE_TOTALS
    for item in admission.observations:
        assert item.assurance == "unknown"
        assert item.presentation_role == "unknown"
        assert item.source.physical_page_mapping == "unresolved"
        assert "p." in item.source.page_reference or "pp." in item.source.page_reference
        assert item.bound_source_sha256
        assert item.bound_source_file.endswith(".pdf")
        assert "physical_page_mapping" in item.unresolved
        assert "canonical_selection" in item.unresolved
    payload = reconciliation_management_admission_payload(mixed_reconciled)
    assert payload["reported_observation_count"] == 135
    assert payload["status"] == "admitted_unreconciled"
    assert payload["canonical_selection"] == "deferred"
    assert len(payload["assessments"]["items"]) == 135
    assert payload["assessments"]["reported_observation_count"] == 135
    assert payload["assessments"]["canonical_selection"] == "deferred"
    assert payload["assessments"]["supported_count"] == 28
    assert payload["assessments"]["outside_scope_count"] == 107
    assert payload["assessments"]["comparability_counts"]["comparable"] == 0
    assert payload["assessments"]["comparability_counts"]["not_comparable"] == 22
    assert payload["assessments"]["comparability_counts"]["unresolved"] == 6
    assert payload["assessments"]["comparability_counts"]["outside_scope"] == 107
    recon = payload["reconciliation"]
    assert recon["canonical_selection"] == "deferred"
    assert recon["outcome_counts"]["agreeing_duplicate"] == 0
    assert recon["outcome_counts"]["conflicting_candidate"] == 0
    assert recon["outcome_counts"]["outside_scope"] == 107
    assert recon["outcome_counts"]["singleton"] == 6
    assert recon["outcome_counts"]["unsupported_variant"] == 0
    assert (
        recon["outcome_counts"]["incompatible"] + recon["outcome_counts"]["unresolved"]
        == recon["pair_count"]
    )
    covered = {
        occ["locator"]
        for item in recon["items"]
        for occ in item["occurrences"]
    }
    reported_locators = {
        item["locator"] for item in payload["observations"] if item["kind"] == "reported_kpi"
    }
    assert covered == reported_locators
    assert all(
        item["evidence"]["calendar_reporting_basis"]
        for item in payload["assessments"]["items"]
        if item["status"] == "supported"
    )
    assert all(
        "calendar_reporting_basis" not in item["unresolved_reasons"]
        for item in payload["assessments"]["items"]
        if item["status"] == "supported"
    )
    assert payload["assessments"]["supported_count"] + payload["assessments"][
        "outside_scope_count"
    ] + payload["assessments"]["unsupported_variant_count"] == 135
    assert any(
        item["code"] == "deferred_canonical_selection" for item in payload["diagnostics"]
    )
    reversed_payload = reconciliation_management_admission_payload(reversed_reconciled)
    assert reversed_payload["reconciliation"]["outcome_counts"] == recon["outcome_counts"]
    assert [item["identity"] for item in payload["observations"]] == [
        item["identity"] for item in reversed_payload["observations"]
    ]
    assert payload["reported_observation_count"] == reversed_payload["reported_observation_count"]
    assert _bytes_by_name(EXTRACTED) == before


def test_reversed_observations_keep_identities(tmp_path: Path):
    payload = json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    payload["reported_kpis"] = list(reversed(payload["reported_kpis"]))
    dest = _copy_json(ANNUAL_NAMES[:1], tmp_path / "obs")
    (dest / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    identities = [
        item.identity
        for item in reconciled.management_admission.observations
        if item.kind == "reported_kpi"
    ]
    assert len(identities) == 29
    assert len(set(identities)) == 29
    assert json.loads((EXTRACTED / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8")) == original


def test_agreeing_and_conflicting_store_duplicates(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[:1] + MANAGEMENT_NAMES[:1], tmp_path / "dup")
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    codes = {item.code for item in reconciled.management_admission.diagnostics}
    assert "agreeing_duplicate" in codes
    assert "deferred_canonical_selection" in codes

    payload = json.loads((dest / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    payload["store_counts_by_market"]["total"] = 1
    (dest / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    assert any(
        item.code == "conflicting_candidate"
        for item in reconciled.management_admission.diagnostics
    )
    selected = reconcile_filings(validated).selected_operating_kpi_facts
    assert selected == ()


def test_constant_dollar_and_bounds_are_not_collapsed():
    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    reported = [
        item
        for item in reconciled.management_admission.observations
        if item.kind == "reported_kpi"
    ]
    bases = {(item.metric_id, item.period, item.basis) for item in reported}
    assert any(basis == "constant_dollar" for _, _, basis in bases)
    assert any(basis == "reported" for _, _, basis in bases)
    identities = [item.identity for item in reported]
    assert len(identities) == len(set(identities))
    bounded = [item for item in reported if dict(item.qualifiers).get("operator") == "greater_than"]
    assert bounded
    assert all("greater_than" in item.identity for item in bounded)


def test_mixed_with_temporary_store_facts_preserves_analytics(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    before_extracted = _bytes_by_name(EXTRACTED)
    for name in MANAGEMENT_NAMES:
        shutil.copy2(EXTRACTED / name, dest / name)
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    assert len(validated) == 4
    assert len(validated.management_documents) == 4
    forward = list(validated)
    reversed_order = list(reversed(validated))
    for order in (forward, reversed_order):
        reconciled = reconcile_filings(
            order,
            admit_periods=ADMIT_2022,
            management_documents=validated.management_documents,
        )
        assert {
            item.period: item.value for item in reconciled.selected_operating_kpi_facts
        } == INDEPENDENT_STORE_TOTALS
        assert len(reconciled.selected_geographic_facts) == 56
        americas = [
            item
            for item in reconciled.selected_geographic_facts
            if item.period == P2025 and item.fact_type.endswith("net_revenue.americas")
        ]
        assert americas[0].value == 7928156
        fin = standardize_reconciled(reconciled)
        restored = standardized_from_payload(standardized_to_payload(fin))
        assert restored.historical_operating_kpis == fin.historical_operating_kpis
        series = compute_operating_kpi_series(restored)
        axis = canonical_fiscal_periods(restored)
        expected = _independent_from_counts(axis, INDEPENDENT_STORE_TOTALS)
        assert [period.isoformat() for period in axis] == [
            P2022.isoformat(),
            P2023.isoformat(),
            P2024.isoformat(),
            P2025.isoformat(),
            P2026.isoformat(),
        ]
        counts = [series.period_end_count[period] for period in axis]
        changes = [series.net_count_change[period] for period in axis]
        for period in axis:
            assert series.period_end_count[period] == expected[period]["count"]
            assert series.net_count_change[period] == expected[period]["change"]
            growth = series.growth[period]
            expected_growth = expected[period]["growth"]
            if isinstance(growth, float) and isinstance(expected_growth, float):
                assert abs(growth - expected_growth) < 1e-12
            else:
                assert growth == expected_growth
        assert counts == [574, 655, 711, 767, 811]
        assert changes == [None, 81, 56, 56, 44]
        reported = [
            item
            for item in reconciled.management_admission.observations
            if item.kind == "reported_kpi"
        ]
        assert len(reported) == 135
        assert any(
            item.code == "agreeing_duplicate"
            and "selected_operating_kpi" in item.identity
            for item in reconciled.management_admission.diagnostics
        )
    assert _bytes_by_name(EXTRACTED) == before_extracted


def test_cli_mixed_directory_writes_separate_admission_artifact(tmp_path: Path):
    import subprocess
    import sys

    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_out = tmp_path / "mixed-out"
    annual_out = tmp_path / "annual-out"
    before = _bytes_by_name(EXTRACTED)
    mixed_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(mixed),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(mixed_out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    annual_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(annual),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(annual_out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert mixed_run.returncode == 0, mixed_run.stdout + mixed_run.stderr
    assert annual_run.returncode == 0, annual_run.stdout + annual_run.stderr
    assert (mixed_out / "management_kpi_admission.json").is_file()
    assert not (annual_out / "management_kpi_admission.json").exists()
    mixed_std = json.loads((mixed_out / "standardized.json").read_text(encoding="utf-8"))
    annual_std = json.loads((annual_out / "standardized.json").read_text(encoding="utf-8"))
    assert _canonicalize(mixed_std) == _canonicalize(annual_std)
    admission = json.loads(
        (mixed_out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    assert admission["reported_observation_count"] == 135
    assert admission["document_count"] == 4
    assert len(admission["assessments"]["items"]) == 135
    assert admission["assessments"]["canonical_selection"] == "deferred"
    assert admission["reconciliation"]["canonical_selection"] == "deferred"
    assert admission["reconciliation"]["outcome_counts"]["agreeing_duplicate"] == 0
    assert admission["reconciliation"]["outcome_counts"]["conflicting_candidate"] == 0
    assert admission["status"] == "admitted_unreconciled"
    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "validate-source",
            str(mixed),
            "--source-root",
            str(SOURCE),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "management-kpi documents: 4" in validate.stdout
    assert "validated 4 filing(s)" in validate.stdout
    assert _bytes_by_name(EXTRACTED) == before


def test_printed_page_is_not_coerced_to_pdf_page():
    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    for item in reconciled.management_admission.observations:
        assert item.source.physical_page_mapping == "unresolved"
        assert "Form 10-K" in item.source.page_reference or "Annual Report" in item.source.page_reference
        payload = item.to_payload()
        assert payload["source"]["physical_page_mapping"] == "unresolved"
        assert "pdf_page" not in payload
        assert payload["assurance"] == "unknown"
        digest = hashlib.sha256((SOURCE / item.bound_source_file).read_bytes()).hexdigest()
        assert item.bound_source_sha256 == digest
