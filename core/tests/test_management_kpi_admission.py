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
BENCH = ROOT / "build" / "input" / "lululemon"
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
        assert item.revision_record.revises == ()
        if item.kind == "reported_kpi":
            assert "revision" not in item.unresolved
        else:
            assert "revision" in item.unresolved
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
    assert recon["revision_links"] == []
    assert recon["selected_count"] == 0
    assert recon["superseded_count"] == 0
    assert recon["group_selection_counts"]["selected"] == 0
    assert recon["revision_link_counts"]["recognized"] == 0
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
    assert admission["reconciliation"]["selected_count"] == 0
    assert admission["reconciliation"]["superseded_count"] == 0
    assert admission["reconciliation"]["group_selection_counts"]["selected"] == 0
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
        assert payload["presentation_role"] == "unknown"
        assert payload["assurance_evidence"]["status"] == "unknown"
        assert payload["presentation_evidence"]["role"] == "unknown"
        assert payload["assurance_evidence"]["source"] is None
        assert payload["presentation_evidence"]["source"] is None
        digest = hashlib.sha256((SOURCE / item.bound_source_file).read_bytes()).hexdigest()
        assert item.bound_source_sha256 == digest


SUPPORTED_EVIDENCE_METRIC_IDS = (
    "comparable_sales_growth",
    "comparable_sales_growth_constant_dollar",
    "americas_comparable_sales_growth",
    "sales_per_square_foot",
)
PRESENTATION_ROLES = ("current", "comparative", "restated", "prior")
ASSURANCE_STATUSES = ("audited", "unaudited")
PRESENTATION_EVIDENCE = "MD&A presents this KPI in the stated role."
ASSURANCE_EVIDENCE = "The filing states this KPI's assurance in the cited section."
REVISION_EVIDENCE = "The later filing restates this previously reported KPI."


def _metric_items(payload: dict, metric_id: str) -> list[dict]:
    return [
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") == metric_id
    ]


def _printed_source(item: dict, source_file: str | None = None) -> dict:
    source = {
        "section": item["source"]["section"],
        "page_reference": item["source"]["page_reference"],
    }
    if source_file is not None:
        source["source_file"] = source_file
    return source


def _attach_presentation(
    item: dict,
    role: str | None,
    *,
    evidence: object = PRESENTATION_EVIDENCE,
    source_file: str | None = None,
    include_source: bool = True,
) -> dict:
    payload: dict[str, object] = {}
    if role is not None:
        payload["role"] = role
    if evidence is not Ellipsis:
        payload["evidence"] = evidence
    if include_source:
        payload["source"] = _printed_source(item, source_file)
    item["presentation"] = payload
    return item


def _attach_assurance(
    item: dict,
    status: str | None,
    *,
    evidence: object = ASSURANCE_EVIDENCE,
    source_file: str | None = None,
    include_source: bool = True,
) -> dict:
    payload: dict[str, object] = {}
    if status is not None:
        payload["status"] = status
    if evidence is not Ellipsis:
        payload["evidence"] = evidence
    if include_source:
        payload["source"] = _printed_source(item, source_file)
    item["assurance"] = payload
    return item


def _revision_target(item: dict, source_file: str, **overrides: str) -> dict[str, str]:
    target = {
        "metric_id": item["metric_id"],
        "period": item["period"],
        "source_file": source_file,
        "page_reference": item["source"]["page_reference"],
    }
    target.update(overrides)
    return target


def _attach_revision(
    item: dict,
    revises: dict | None,
    *,
    evidence: object = REVISION_EVIDENCE,
    source_file: str | None = None,
    include_source: bool = True,
) -> dict:
    payload: dict[str, object] = {}
    if revises is not None:
        payload["revises"] = revises
    if evidence is not Ellipsis:
        payload["evidence"] = evidence
    if include_source:
        payload["source"] = _printed_source(item, source_file)
    item["revision"] = payload
    return item


def _admit_mutated(tmp_path: Path, mutate, *, years: slice = slice(1, 2)) -> dict:
    dest = _copy_json(ANNUAL_NAMES[years] + MANAGEMENT_NAMES[years], tmp_path / "admit")
    original = json.loads(
        (EXTRACTED / MANAGEMENT_NAMES[years][0]).read_text(encoding="utf-8")
    )
    payload = mutate(copy.deepcopy(original))
    (dest / MANAGEMENT_NAMES[years][0]).write_text(json.dumps(payload), encoding="utf-8")
    admitted = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    assert json.loads(
        (EXTRACTED / MANAGEMENT_NAMES[years][0]).read_text(encoding="utf-8")
    ) == original
    return admitted


def _observation(payload: dict, metric_id: str) -> dict:
    matches = [
        item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi" and item["metric_id"] == metric_id
    ]
    assert matches
    return matches[0]


@pytest.mark.parametrize("metric_id", SUPPORTED_EVIDENCE_METRIC_IDS)
@pytest.mark.parametrize("role", PRESENTATION_ROLES)
def test_supported_presentation_roles_are_occurrence_bound(
    tmp_path: Path, metric_id: str, role: str
):
    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, metric_id):
            _attach_presentation(item, role, source_file=payload["report"]["source_file"])
        return payload

    admitted = _admit_mutated(tmp_path, mutate)
    item = _observation(admitted, metric_id)
    assert item["presentation_role"] == role
    assert item["presentation_evidence"]["role"] == role
    assert item["presentation_evidence"]["evidence"] == PRESENTATION_EVIDENCE
    assert item["presentation_evidence"]["locator"].endswith(".presentation")
    assert item["presentation_evidence"]["source"]["physical_page_mapping"] == "unresolved"
    assert item["presentation_evidence"]["source"]["page_reference"]
    assert "pdf_page" not in item["presentation_evidence"]["source"]
    assert "presentation_role" not in item["unresolved"]
    assert item["assurance"] == "unknown"
    assert "assurance" in item["unresolved"]
    assert "assurance" in admitted["unresolved"]
    assert "presentation_role" in admitted["unresolved"]
    assert "precedence" in admitted["unresolved"]
    assert "physical_page_mapping" in admitted["unresolved"]


@pytest.mark.parametrize("metric_id", SUPPORTED_EVIDENCE_METRIC_IDS)
@pytest.mark.parametrize("status", ASSURANCE_STATUSES)
def test_supported_assurance_statuses_are_occurrence_bound(
    tmp_path: Path, metric_id: str, status: str
):
    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, metric_id):
            _attach_assurance(item, status, source_file=payload["report"]["source_file"])
        return payload

    admitted = _admit_mutated(tmp_path, mutate)
    item = _observation(admitted, metric_id)
    assert item["assurance"] == status
    assert item["assurance_evidence"]["status"] == status
    assert item["assurance_evidence"]["evidence"] == ASSURANCE_EVIDENCE
    assert item["assurance_evidence"]["locator"].endswith(".assurance")
    assert item["presentation_role"] == "unknown"
    assert "assurance" not in item["unresolved"]
    assert "presentation_role" in item["unresolved"]
    assert status != "unknown"


def test_dimensions_are_independent_and_blank_evidence_stays_unknown(tmp_path: Path):
    admitted = _admit_mutated(
        tmp_path,
        lambda payload: payload,
    )
    item = _observation(admitted, "comparable_sales_growth")
    assert item["presentation_role"] == "unknown"
    assert item["assurance"] == "unknown"
    assert "presentation_role" in item["unresolved"]
    assert "assurance" in item["unresolved"]

    def only_presentation(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            _attach_presentation(item, "current")
        return payload

    presented = _admit_mutated(tmp_path / "pres", only_presentation)
    item = _observation(presented, "comparable_sales_growth")
    assert item["presentation_role"] == "current"
    assert item["assurance"] == "unknown"
    assert "assurance" in item["unresolved"]
    assert "presentation_role" not in item["unresolved"]

    def only_assurance(payload: dict) -> dict:
        for item in _metric_items(payload, "sales_per_square_foot"):
            _attach_assurance(item, "unaudited")
        return payload

    assured = _admit_mutated(tmp_path / "asr", only_assurance)
    item = _observation(assured, "sales_per_square_foot")
    assert item["assurance"] == "unaudited"
    assert item["presentation_role"] == "unknown"
    assert item["assurance"] != "unknown"

    def explicit_unknown(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            item["presentation"] = {"role": "unknown"}
            item["assurance"] = {"status": "unknown"}
        return payload

    unknown = _admit_mutated(tmp_path / "unk", explicit_unknown)
    item = _observation(unknown, "comparable_sales_growth")
    assert item["presentation_role"] == "unknown"
    assert item["assurance"] == "unknown"
    assert "presentation_role" in item["unresolved"]
    assert "assurance" in item["unresolved"]

    def null_dimensions(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            item["presentation"] = None
            item["assurance"] = None
        return payload

    nulled = _admit_mutated(tmp_path / "null", null_dimensions)
    item = _observation(nulled, "comparable_sales_growth")
    assert item["presentation_role"] == "unknown"
    assert item["assurance"] == "unknown"


@pytest.mark.parametrize("blank", [None, "", " ", " \t "])
@pytest.mark.parametrize("dimension", ["presentation", "assurance"])
def test_blank_or_absent_evidence_does_not_assert_a_role(
    tmp_path: Path, blank: str | None, dimension: str
):
    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            if dimension == "presentation":
                item["presentation"] = {"evidence": blank}
            else:
                item["assurance"] = {"evidence": blank}
        return payload

    admitted = _admit_mutated(tmp_path, mutate)
    item = _observation(admitted, "comparable_sales_growth")
    assert item["presentation_role"] == "unknown"
    assert item["assurance"] == "unknown"
    if dimension == "presentation":
        assert item["presentation_evidence"]["evidence"] == ("" if blank is None else blank)
        assert "presentation_role" in item["unresolved"]
    else:
        assert item["assurance_evidence"]["evidence"] == ("" if blank is None else blank)
        assert "assurance" in item["unresolved"]


@pytest.mark.parametrize(
    "mutate,match",
    [
        (
            lambda item: item.__setitem__("presentation", "current"),
            "presentation must be an object",
        ),
        (
            lambda item: item.__setitem__("assurance", "unaudited"),
            "assurance must be an object",
        ),
        (
            lambda item: _attach_presentation(item, "current_period"),
            "invalid",
        ),
        (
            lambda item: _attach_assurance(item, "reviewed"),
            "invalid",
        ),
        (
            lambda item: _attach_presentation(item, True),
            "must be a string",
        ),
        (
            lambda item: _attach_presentation(item, "current", evidence=""),
            "nonblank documentary evidence",
        ),
        (
            lambda item: _attach_presentation(item, "current", evidence=" \t "),
            "nonblank documentary evidence",
        ),
        (
            lambda item: _attach_presentation(
                item, "current", evidence=PRESENTATION_EVIDENCE, include_source=False
            ),
            "source bound to the observation document",
        ),
        (
            lambda item, payload=None: _attach_presentation(
                item,
                "prior",
                source_file="LULU_FY2024_Annual_Report.pdf",
            ),
            "not bound to the observation source document",
        ),
        (
            lambda item: item.__setitem__(
                "presentation",
                {
                    "role": "current",
                    "evidence": PRESENTATION_EVIDENCE,
                    "source": {
                        "section": item["source"]["section"],
                        "page_reference": item["source"]["page_reference"],
                        "physical_page_mapping": "12",
                    },
                },
            ),
            "cannot certify a PDF page",
        ),
        (
            lambda item: (
                _attach_presentation(item, "current"),
                item.__setitem__("presentation_role", "prior"),
            ),
            "contradictory presentation_role",
        ),
        (
            lambda item: item.__setitem__("presentation_role", "current"),
            "without documentary evidence",
        ),
        (
            lambda item: _attach_presentation(item, "current"),
            "unsupported observation",
        ),
        (
            lambda item: item.__setitem__("revision", "restated"),
            "revision must be an object",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                include_source=False,
            ),
            "source bound to the observation document",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                source_file="LULU_FY2024_Annual_Report.pdf",
            ),
            "not bound to the observation source document",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2023_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
            ),
            "self-referential",
        ),
        (
            lambda item: item.__setitem__(
                "revision",
                {
                    "revises": {
                        "metric_id": item["metric_id"],
                        "period": item["period"],
                        "source_file": "LULU_FY2022_Annual_Report.pdf",
                        "page_reference": item["source"]["page_reference"],
                    },
                    "evidence": REVISION_EVIDENCE,
                    "source": {
                        "section": item["source"]["section"],
                        "page_reference": item["source"]["page_reference"],
                        "physical_page_mapping": "12",
                    },
                },
            ),
            "cannot certify a PDF page",
        ),
        (
            lambda item: (
                _attach_revision(
                    item,
                    {
                        "metric_id": item["metric_id"],
                        "period": item["period"],
                        "source_file": "LULU_FY2022_Annual_Report.pdf",
                        "page_reference": item["source"]["page_reference"],
                    },
                ),
                item.__setitem__(
                    "revises",
                    {
                        "metric_id": item["metric_id"],
                        "period": "2022-01-30",
                        "source_file": "LULU_FY2022_Annual_Report.pdf",
                        "page_reference": item["source"]["page_reference"],
                    },
                ),
            ),
            "contradictory revises",
        ),
        (
            lambda item: item.__setitem__(
                "revises",
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
            ),
            "without documentary evidence",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                    "value": "10",
                },
            ),
            "unexpected fields",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                evidence="",
                include_source=False,
            ),
            "source bound to the observation document",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                evidence=" \t ",
                source_file="LULU_FY2024_Annual_Report.pdf",
            ),
            "not bound to the observation source document",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2023_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                evidence="",
            ),
            "self-referential",
        ),
        (
            lambda item: (
                _attach_revision(
                    item,
                    {
                        "metric_id": item["metric_id"],
                        "period": item["period"],
                        "source_file": "LULU_FY2022_Annual_Report.pdf",
                        "page_reference": item["source"]["page_reference"],
                    },
                    evidence=None,
                ),
                item.__setitem__(
                    "revises",
                    {
                        "metric_id": item["metric_id"],
                        "period": "2022-01-30",
                        "source_file": "LULU_FY2022_Annual_Report.pdf",
                        "page_reference": item["source"]["page_reference"],
                    },
                ),
            ),
            "contradictory revises",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
                evidence="",
            ),
            "unsupported observation",
        ),
        (
            lambda item: _attach_revision(
                item,
                {
                    "metric_id": item["metric_id"],
                    "period": item["period"],
                    "source_file": "LULU_FY2022_Annual_Report.pdf",
                    "page_reference": item["source"]["page_reference"],
                },
            ),
            "unsupported observation",
        ),
    ],
)
def test_malformed_contradictory_and_unbound_evidence_fail_closed(
    tmp_path: Path, mutate, match: str
):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "bad")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    before = _bytes_by_name(EXTRACTED)
    target_id = (
        "net_revenue" if "unsupported" in match else "comparable_sales_growth"
    )
    for item in _metric_items(payload, target_id):
        mutate(item)
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_and_validate_extracted_dir(dest, source_root=SOURCE)
    assert _bytes_by_name(EXTRACTED) == before


def test_prior_is_not_inferred_from_an_older_period_or_filename(tmp_path: Path):
    admitted = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE))
    )
    older = [
        item
        for item in admitted["observations"]
        if item["kind"] == "reported_kpi" and item["filing_year"] == 2022
    ]
    assert older
    assert all(item["presentation_role"] == "unknown" for item in older)
    assert all(item["assurance"] == "unknown" for item in older)
    assert all(
        item["bound_source_file"].endswith("FY2022_Annual_Report.pdf") for item in older
    )

    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            item["period"] = "2022-01-30"
            _attach_presentation(item, "current")
        return payload

    current = _admit_mutated(tmp_path, mutate)
    item = _observation(current, "comparable_sales_growth")
    assert item["period"] == "2022-01-30"
    assert item["filing_year"] == 2023
    assert item["presentation_role"] == "current"
    assert item["presentation_role"] != "prior"
    assert item["presentation_role"] != "comparative"


def test_unknown_assurance_is_not_unaudited(tmp_path: Path):
    unknown = _observation(
        _admit_mutated(tmp_path, lambda payload: payload),
        "sales_per_square_foot",
    )
    assert unknown["assurance"] == "unknown"
    assert unknown["assurance"] != "unaudited"

    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, "sales_per_square_foot"):
            _attach_assurance(item, "unaudited")
        return payload

    explicit = _observation(_admit_mutated(tmp_path / "unau", mutate), "sales_per_square_foot")
    assert explicit["assurance"] == "unaudited"
    assert explicit["assurance"] != "unknown"
    assert "assurance" not in explicit["unresolved"]


def test_repeated_same_document_occurrences_keep_local_evidence(tmp_path: Path):
    def mutate(payload: dict) -> dict:
        original = next(
            item
            for item in payload["reported_kpis"]
            if item.get("metric_id") == "comparable_sales_growth"
        )
        left = copy.deepcopy(original)
        right = copy.deepcopy(original)
        _attach_presentation(left, "current")
        _attach_assurance(left, "audited")
        _attach_presentation(right, "restated")
        _attach_assurance(right, "unaudited")
        payload["reported_kpis"] = [
            item
            for item in payload["reported_kpis"]
            if item.get("metric_id") != "comparable_sales_growth"
        ] + [left, right]
        return payload

    admitted = _admit_mutated(tmp_path, mutate)
    items = [
        item
        for item in admitted["observations"]
        if item["kind"] == "reported_kpi" and item["metric_id"] == "comparable_sales_growth"
    ]
    assert len(items) == 2
    roles = {item["presentation_role"] for item in items}
    assurances = {item["assurance"] for item in items}
    assert roles == {"current", "restated"}
    assert assurances == {"audited", "unaudited"}
    locators = {item["presentation_evidence"]["locator"] for item in items}
    assert len(locators) == 2


def test_cli_serializes_occurrence_evidence(tmp_path: Path):
    import subprocess
    import sys

    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    for item in payload["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            _attach_presentation(item, "comparative")
            _attach_assurance(item, "audited")
        if item.get("metric_id") == "sales_per_square_foot":
            _attach_presentation(item, "prior")
            _attach_assurance(item, "unaudited")
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "out"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "reconcile",
            str(dest),
            "--source-root",
            str(SOURCE),
            "--admit-period",
            "2022-01-30",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    admission = json.loads((out / "management_kpi_admission.json").read_text(encoding="utf-8"))
    compsales = next(
        item
        for item in admission["observations"]
        if item["kind"] == "reported_kpi"
        and item["metric_id"] == "comparable_sales_growth"
        and item["filing_year"] == 2023
    )
    spsf = next(
        item
        for item in admission["observations"]
        if item["kind"] == "reported_kpi"
        and item["metric_id"] == "sales_per_square_foot"
        and item["filing_year"] == 2023
    )
    assert compsales["presentation_role"] == "comparative"
    assert compsales["assurance"] == "audited"
    assert spsf["presentation_role"] == "prior"
    assert spsf["assurance"] == "unaudited"
    assert spsf["presentation_role"] != "comparative"
    for item in admission["reconciliation"]["items"]:
        for occ in item["occurrences"]:
            assert "presentation_evidence" in occ
            assert "assurance_evidence" in occ
            assert "revision_evidence" in occ
        if item["kind"] == "pair":
            rel = item["presentation_relationship"]
            assert rel["combination"]
            assert [member["locator"] for member in rel["members"]] == item["locators"]
            for member, occ in zip(rel["members"], item["occurrences"]):
                assert member["role"] == occ["presentation_evidence"]["role"]
                assert member["occurrence_identity"] == occ["occurrence_identity"]
        else:
            assert "presentation_relationship" not in item
    assert all(
        item["assurance"] == "unknown" and item["presentation_role"] == "unknown"
        for item in admission["documents"]
    )
    assert admission["reconciliation"]["revision_links"] == []
    assert admission["reconciliation"]["revision_link_counts"]["recognized"] == 0


@pytest.mark.parametrize(
    "metric_id",
    ("comparable_sales_growth", "sales_per_square_foot"),
)
def test_revision_contract_admits_explicit_named_targets(
    tmp_path: Path, metric_id: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rev")
    left = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    right = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    target = next(item for item in left["reported_kpis"] if item.get("metric_id") == metric_id)
    reviser = next(item for item in right["reported_kpis"] if item.get("metric_id") == metric_id)
    reviser["period"] = target["period"]
    named = _revision_target(target, left["report"]["source_file"])
    _attach_revision(
        reviser,
        named,
        source_file=right["report"]["source_file"],
    )
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(left), encoding="utf-8")
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(right), encoding="utf-8")
    admitted = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    item = next(
        row
        for row in admitted["observations"]
        if row["kind"] == "reported_kpi"
        and row["metric_id"] == metric_id
        and row["filing_year"] == 2024
    )
    assert item["revision_evidence"]["revises"] == named
    assert item["revision_evidence"]["evidence"] == REVISION_EVIDENCE
    assert item["revision_evidence"]["locator"].endswith(".revision")
    assert item["revision_evidence"]["source"]["page_reference"]
    assert item["revision_evidence"]["source"]["physical_page_mapping"] == "unresolved"
    assert item["bound_source_file"] == right["report"]["source_file"]
    assert "revision" not in item["unresolved"]
    assert not any(
        row["code"] in {"revision_target_missing", "revision_target_ambiguous"}
        for row in admitted["diagnostics"]
        if item["locator"] in row["occurrences"]
    )


@pytest.mark.parametrize("blank", [None, "", " ", " \t "])
def test_blank_revision_evidence_stays_unresolved(tmp_path: Path, blank: str | None):
    def mutate(payload: dict) -> dict:
        for item in _metric_items(payload, "comparable_sales_growth"):
            item["revision"] = {"evidence": blank}
        return payload

    admitted = _admit_mutated(tmp_path, mutate)
    item = _observation(admitted, "comparable_sales_growth")
    assert item["revision_evidence"]["revises"] is None
    assert item["revision_evidence"]["evidence"] == ("" if blank is None else blank)
    assert "revision" in item["unresolved"]
    assert admitted["reconciliation"]["revision_links"] == []


def _set_named_revision_evidence(item: dict, blank: object) -> None:
    revision = item["revision"]
    if blank is Ellipsis:
        revision.pop("evidence", None)
    else:
        revision["evidence"] = blank


@pytest.mark.parametrize(
    "metric_id",
    ("comparable_sales_growth", "sales_per_square_foot"),
)
@pytest.mark.parametrize("blank", [Ellipsis, None, "", " ", " \t "])
def test_named_target_blank_evidence_admits_unresolved_revision(
    tmp_path: Path, metric_id: str, blank: object
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "blank")
    left = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    right = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    target = next(item for item in left["reported_kpis"] if item.get("metric_id") == metric_id)
    reviser = next(item for item in right["reported_kpis"] if item.get("metric_id") == metric_id)
    reviser["period"] = target["period"]
    named = _revision_target(target, left["report"]["source_file"])
    _attach_revision(
        reviser,
        named,
        source_file=right["report"]["source_file"],
    )
    _set_named_revision_evidence(reviser, blank)
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(left), encoding="utf-8")
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(right), encoding="utf-8")
    admitted = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    item = next(
        row
        for row in admitted["observations"]
        if row["kind"] == "reported_kpi"
        and row["metric_id"] == metric_id
        and row["filing_year"] == 2024
    )
    expected_evidence = "" if blank in {Ellipsis, None} else blank
    assert item["revision_evidence"]["revises"] == named
    assert item["revision_evidence"]["evidence"] == expected_evidence
    assert item["revision_evidence"]["locator"].endswith(".revision")
    assert item["revision_evidence"]["source"]["page_reference"]
    assert item["revision_evidence"]["source"]["physical_page_mapping"] == "unresolved"
    assert item["bound_source_file"] == right["report"]["source_file"]
    assert "revision" in item["unresolved"]
    links = admitted["reconciliation"]["revision_links"]
    assert len(links) == 1
    link = links[0]
    assert link["status"] == "unresolved"
    assert link["named_target"] == named
    assert link["evidence"] == expected_evidence
    assert link["source"]["page_reference"]
    assert link["reviser"]["locator"] == item["locator"]
    assert link["revised"] is not None
    assert link["revised"]["locator"] != item["locator"]
    assert "missing_evidence" in link["reasons"]
    assert admitted["reconciliation"]["revision_link_counts"]["recognized"] == 0
    assert all(row["status"] != "recognized" for row in links)


def test_missing_and_ambiguous_revision_targets_do_not_select(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "miss")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    original = next(
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") == "comparable_sales_growth"
    )
    missing_item = copy.deepcopy(original)
    _attach_revision(
        missing_item,
        _revision_target(
            original,
            payload["report"]["source_file"],
            page_reference="Form 10-K p. 999",
        ),
        source_file=payload["report"]["source_file"],
    )
    payload["reported_kpis"] = [
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") != "comparable_sales_growth"
    ] + [missing_item]
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload), encoding="utf-8")
    missing = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    assert any(item["code"] == "revision_target_missing" for item in missing["diagnostics"])
    assert all(
        link["revised"] is None and "missing_target" in link["reasons"]
        for link in missing["reconciliation"]["revision_links"]
    )
    assert all(
        link["status"] != "recognized"
        for link in missing["reconciliation"]["revision_links"]
    )

    first = copy.deepcopy(original)
    first.pop("revision", None)
    second = copy.deepcopy(first)
    third = copy.deepcopy(first)
    third["source"] = dict(first["source"])
    third["source"]["page_reference"] = "Form 10-K p. 40-unique"
    _attach_revision(
        third,
        _revision_target(first, payload["report"]["source_file"]),
        source_file=payload["report"]["source_file"],
    )
    payload["reported_kpis"] = [
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") != "comparable_sales_growth"
    ] + [first, second, third]
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload), encoding="utf-8")
    ambiguous = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    ambiguous_diag = [
        item
        for item in ambiguous["diagnostics"]
        if item["code"] == "revision_target_ambiguous"
    ]
    assert len(ambiguous_diag) == 1
    assert len(ambiguous_diag[0]["occurrences"]) == 3
    links = ambiguous["reconciliation"]["revision_links"]
    assert len(links) == 1
    assert links[0]["revised"] is None
    assert links[0]["status"] == "unresolved"
    assert "ambiguous_target" in links[0]["reasons"]
    assert len(links[0]["candidate_locators"]) == 2
    assert "preferred" not in links[0]
    assert "winner" not in links[0]
    assert "superseded" not in links[0]


@pytest.mark.parametrize(
    "family",
    (
        "comparable_sales_growth",
        "sales_per_square_foot",
    ),
)
@pytest.mark.parametrize("target", ["superseded", "reviser"])
def test_ordinary_admission_incoming_ambiguous_candidate_defers(
    tmp_path: Path, family: str, target: str
):
    from core.ingestion.management_kpi_identity import (
        FAMILY_COMPARABLE_SALES_GROWTH,
        FAMILY_SALES_PER_SQUARE_FOOT,
        STATUS_UNSUPPORTED_VARIANT,
    )
    from core.ingestion.management_kpi_reconciliation import (
        REASON_AMBIGUOUS_TARGET,
        RELATIONSHIP_UNRESOLVED,
    )
    from core.tests.test_management_kpi_reconciliation import (
        _admission,
        _assert_deferred_group,
        _assert_eligible_members_survive,
        _family_period_group,
        _incoming_ambiguous_link,
        _selected_locators,
        write_incoming_ambiguous_fixture,
    )

    family = (
        FAMILY_COMPARABLE_SALES_GROWTH
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_SALES_PER_SQUARE_FOOT
    )
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "admit-in")
    write_incoming_ambiguous_fixture(dest, family, target=target)
    admitted = _admission(dest)
    assert admitted["status"] == "admitted_unreconciled"
    reviser, superseded, link = _selected_locators(admitted, family)
    group = _family_period_group(admitted, family)
    incoming = _incoming_ambiguous_link(admitted, group)
    involved = superseded if target == "superseded" else reviser
    assert incoming["status"] == RELATIONSHIP_UNRESOLVED
    assert incoming["revised"] is None
    assert involved in incoming["candidate_locators"]
    assert len(incoming["candidate_locators"]) == 2
    assert link["revised"]["locator"] == superseded
    _assert_deferred_group(group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET)
    _assert_eligible_members_survive(
        group, reviser_locator=reviser, superseded_locator=superseded
    )
    duplicate = next(
        locator
        for locator in incoming["candidate_locators"]
        if locator not in group["locators"]
    )
    assert _assessments_status(admitted, duplicate) == STATUS_UNSUPPORTED_VARIANT


def _assessments_status(payload: dict, locator: str) -> str:
    return next(
        item["status"]
        for item in payload["assessments"]["items"]
        if item["locator"] == locator
    )

