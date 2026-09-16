"""Identity and comparability assessments for supported management KPIs."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from core.data.standardized_io import standardized_to_payload
from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_management_admission_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.management_kpi_identity import (
    COMPARABILITY_COMPARABLE,
    COMPARABILITY_NOT_COMPARABLE,
    COMPARABILITY_OUTSIDE_SCOPE,
    COMPARABILITY_UNRESOLVED,
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    STATUS_OUTSIDE_SCOPE,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED_VARIANT,
    SUPPORTED_METRIC_MAPPINGS,
    encode_metric_identity,
)
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    REPORTED_COUNTS,
    SOURCE,
    _bytes_by_name,
    _canonicalize,
    _copy_json,
    _statement_provenance,
)


def _assessments_by_locator(payload: dict) -> dict[str, dict]:
    return {item["locator"]: item for item in payload["assessments"]["items"]}


def _supported_items(payload: dict) -> list[dict]:
    return [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == STATUS_SUPPORTED
    ]


def test_metric_identity_is_delimiter_safe_and_order_independent():
    fields = {
        "comparison": "year_over_year",
        "family": FAMILY_COMPARABLE_SALES_GROWTH,
        "entity_company": 'lulu|inc "quoted"',
        "entity_ticker": "LULU",
        "geography": "americas",
        "population": "company_operated_stores_and_ecommerce",
        "unit": "percent",
        "basis": "reported",
    }
    reversed_fields = dict(reversed(list(fields.items())))
    first = encode_metric_identity(fields)
    second = encode_metric_identity(reversed_fields)
    assert first == second
    assert "|" in fields["entity_company"]
    parsed = json.loads(first)
    assert parsed["entity_company"] == fields["entity_company"]
    assert list(parsed) == sorted(parsed)


def test_supplied_families_receive_identities_and_outside_scope_is_explicit():
    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    reconciled = reconcile_filings(validated)
    payload = reconciliation_management_admission_payload(reconciled)
    reported = [
        item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
    ]
    items = payload["assessments"]["items"]
    assert payload["reported_observation_count"] == 135
    assert len(items) == 135
    assert payload["assessments"]["reported_observation_count"] == 135
    assert [item["locator"] for item in items] == [
        item["locator"] for item in reported
    ]
    locators = {item["locator"] for item in items}
    assert locators == {item["locator"] for item in reported}
    for item in items:
        if item["status"] == STATUS_OUTSIDE_SCOPE:
            assert item["comparability"] == COMPARABILITY_OUTSIDE_SCOPE
            assert item["metric_identity"] == ""
            assert "outside_supported_families" in item["unresolved_reasons"]
            assert item["family"] == ""
        elif item["status"] == STATUS_SUPPORTED:
            assert item["family"] in {
                FAMILY_COMPARABLE_SALES_GROWTH,
                FAMILY_SALES_PER_SQUARE_FOOT,
            }
            assert item["metric_identity"]
            assert item["comparability"] in {
                COMPARABILITY_COMPARABLE,
                COMPARABILITY_NOT_COMPARABLE,
                COMPARABILITY_UNRESOLVED,
            }
            assert item["definition"]["text"]
            assert item["definition"]["extraction_document"]
            assert item["definition"]["definition_id"]
        else:
            assert item["status"] == STATUS_UNSUPPORTED_VARIANT
            assert item["comparability"] == COMPARABILITY_UNRESOLVED
    mapped = {
        item["locator"]: item
        for item in reported
        if item["metric_id"] in SUPPORTED_METRIC_MAPPINGS
    }
    by_locator = _assessments_by_locator(payload)
    for locator, observation in mapped.items():
        assessment = by_locator[locator]
        assert assessment["status"] == STATUS_SUPPORTED
        fields = assessment["metric_identity_fields"]
        assert fields["unit"] == observation["unit"]
        assert fields["basis"] == observation["basis"]
        assert fields["comparison"] == observation.get("comparison", "")
        parsed = json.loads(assessment["metric_identity"])
        assert parsed == fields
    outside = [
        item
        for item in reported
        if item["metric_id"] not in SUPPORTED_METRIC_MAPPINGS
    ]
    assert outside
    for observation in outside:
        assessment = by_locator[observation["locator"]]
        assert assessment["status"] == STATUS_OUTSIDE_SCOPE
    assert payload["assessments"]["supported_count"] == len(mapped)
    assert payload["assessments"]["outside_scope_count"] == len(outside)
    assert payload["assessments"]["unsupported_variant_count"] == 0
    assert payload["assessments"]["canonical_selection"] == "deferred"


def test_reported_versus_constant_dollar_and_geography_are_separate_identities():
    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    payload = reconciliation_management_admission_payload(reconcile_filings(validated))
    supported = _supported_items(payload)
    reported = [
        item
        for item in supported
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"]["geography"] == "china_mainland"
        and item["metric_identity_fields"]["basis"] == "reported"
    ]
    constant = [
        item
        for item in supported
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"]["geography"] == "china_mainland"
        and item["metric_identity_fields"]["basis"] == "constant_dollar"
    ]
    assert reported
    assert constant
    assert {item["metric_identity"] for item in reported}.isdisjoint(
        {item["metric_identity"] for item in constant}
    )
    geographies = {
        (
            item["metric_identity_fields"]["geography"],
            item["metric_identity_fields"]["population"],
        )
        for item in supported
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"]["basis"] == "reported"
        and item["evidence"]["period"] in {"FY2023", "FY2024", "FY2025"}
        and item["metric_identity_fields"]["population"]
        == "company_operated_stores_and_ecommerce"
    }
    assert geographies == {
        ("global", "company_operated_stores_and_ecommerce"),
        ("americas", "company_operated_stores_and_ecommerce"),
        ("china_mainland", "company_operated_stores_and_ecommerce"),
        ("rest_of_world", "company_operated_stores_and_ecommerce"),
    }
    fy2022_store = [
        item
        for item in supported
        if item["metric_identity_fields"]["population"]
        == "company_operated_stores"
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    fy2022_total = [
        item
        for item in supported
        if item["metric_identity_fields"]["population"]
        == "company_operated_stores_and_direct_to_consumer"
    ]
    assert fy2022_store
    assert fy2022_total
    assert {item["metric_identity"] for item in fy2022_store}.isdisjoint(
        {item["metric_identity"] for item in fy2022_total}
    )


def test_definition_changes_and_missing_definitions_are_conservative(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[:2] + MANAGEMENT_NAMES[:2], tmp_path / "defs")
    payload_2023 = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    original_text = payload_2023["kpi_definitions"][0]["definition"]
    payload_2022 = json.loads((dest / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    payload_2022["kpi_definitions"][0]["definition_id"] = "comparable_sales_shared"
    payload_2022["kpi_definitions"][0]["reported_label"] = "Comparable sales"
    for item in payload_2022["reported_kpis"]:
        if item.get("definition_id") == "comparable_store_sales_fy2022":
            item["definition_id"] = "comparable_sales_shared"
    payload_2023["kpi_definitions"][0]["definition_id"] = "comparable_sales_shared"
    payload_2023["kpi_definitions"][0]["reported_label"] = "Comparable sales"
    for item in payload_2023["reported_kpis"]:
        if item.get("definition_id") == "comparable_sales_fy2023":
            item["definition_id"] = "comparable_sales_shared"
    (dest / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload_2022), encoding="utf-8")
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload_2023), encoding="utf-8")
    validated = load_and_validate_extracted_dir(dest, source_root=SOURCE)
    payload = reconciliation_management_admission_payload(reconcile_filings(validated))
    compsales = [
        item
        for item in _supported_items(payload)
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["definition"]["definition_id"] == "comparable_sales_shared"
    ]
    assert compsales
    assert all(item["definition"]["text"] for item in compsales)
    # Matching IDs and labels do not make FY2022 store compsales comparable
    # to FY2023 company+ecomm compsales: populations differ.
    populations = {item["metric_identity_fields"]["population"] for item in compsales}
    assert len(populations) == 2

    payload_2023["kpi_definitions"][0]["definition"] = original_text + " mutated"
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload_2023), encoding="utf-8")
    mutated = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    mutated_items = [
        item
        for item in mutated["assessments"]["items"]
        if item["definition"]["definition_id"] == "comparable_sales_shared"
        and item["status"] == STATUS_SUPPORTED
    ]
    assert any("mutated" in item["definition"]["text"] for item in mutated_items)

    missing = copy.deepcopy(payload_2023)
    for item in missing["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["definition_id"] = ""
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(missing), encoding="utf-8")
    missing_payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    missing_item = next(
        item
        for item in missing_payload["assessments"]["items"]
        if item["evidence"]["period"] == "FY2023"
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
    )
    assert missing_item["comparability"] == COMPARABILITY_UNRESOLVED
    assert "missing_definition" in missing_item["unresolved_reasons"]
    assert missing_item["definition"]["text"] == ""


def test_calendar_and_period_discontinuities_are_not_comparable(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "cal")
    fy2023 = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    fy2024 = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    baseline_text = fy2023["kpi_definitions"][0]["definition"]
    fy2024["kpi_definitions"][0]["definition"] = baseline_text
    fy2024["report"]["reporting_basis"] = fy2023["report"]["reporting_basis"]
    for item in fy2024["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(fy2024), encoding="utf-8")
    aligned = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    aligned_items = [
        item
        for item in _supported_items(aligned)
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"]["geography"] == "global"
        and item["metric_identity_fields"]["basis"] == "reported"
        and item["metric_identity_fields"]["population"]
        == "company_operated_stores_and_ecommerce"
    ]
    assert len(aligned_items) == 2
    assert {item["comparability"] for item in aligned_items} == {
        COMPARABILITY_COMPARABLE
    }

    fy2024["report"]["reporting_basis"] = "FY2024 contains 53 weeks."
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(fy2024), encoding="utf-8")
    calendar = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    calendar_items = [
        item
        for item in _supported_items(calendar)
        if item["metric_identity"] == aligned_items[0]["metric_identity"]
    ]
    assert {item["comparability"] for item in calendar_items} == {
        COMPARABILITY_NOT_COMPARABLE
    }
    assert any(
        "calendar_mismatch" in item["unresolved_reasons"] for item in calendar_items
    )

    fy2024["report"]["reporting_basis"] = fy2023["report"]["reporting_basis"]
    fy2024["kpi_definitions"][0]["definition"] = baseline_text + " shifted weeks"
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(fy2024), encoding="utf-8")
    defined = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    defined_items = [
        item
        for item in _supported_items(defined)
        if item["metric_identity"] == aligned_items[0]["metric_identity"]
    ]
    assert {item["comparability"] for item in defined_items} == {
        COMPARABILITY_NOT_COMPARABLE
    }
    assert any(
        "definition_mismatch" in item["unresolved_reasons"] for item in defined_items
    )


def test_mutations_cannot_silently_preserve_comparability(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "mut")
    fy2023 = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    fy2024 = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    fy2024["kpi_definitions"][0]["definition"] = fy2023["kpi_definitions"][0][
        "definition"
    ]
    fy2024["report"]["reporting_basis"] = fy2023["report"]["reporting_basis"]
    for item in fy2024["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(fy2024), encoding="utf-8")
    baseline = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    identity = next(
        item["metric_identity"]
        for item in _supported_items(baseline)
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["evidence"]["period"] == "FY2023"
        and item["metric_identity_fields"]["geography"] == "global"
        and item["metric_identity_fields"]["basis"] == "reported"
    )
    assert all(
        item["comparability"] == COMPARABILITY_COMPARABLE
        for item in _supported_items(baseline)
        if item["metric_identity"] == identity
    )

    cases = []
    definition_mut = copy.deepcopy(fy2024)
    definition_mut["kpi_definitions"][0]["definition"] += " changed"
    cases.append(("definition", definition_mut))
    scope_mut = copy.deepcopy(fy2024)
    for item in scope_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["scope"] = {"geography": "Americas"}
    cases.append(("scope", scope_mut))
    unit_mut = copy.deepcopy(fy2024)
    for item in unit_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["unit"] = "USD"
    cases.append(("unit", unit_mut))
    calendar_mut = copy.deepcopy(fy2024)
    for item in calendar_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["qualifiers"] = {"excludes_53rd_week": True}
    cases.append(("calendar", calendar_mut))

    for kind, mutated in cases:
        (dest / MANAGEMENT_NAMES[2]).write_text(json.dumps(mutated), encoding="utf-8")
        payload = reconciliation_management_admission_payload(
            reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
        )
        fy2024_locator = next(
            item["locator"]
            for item in payload["observations"]
            if item["kind"] == "reported_kpi"
            and item["metric_id"] == "comparable_sales_growth"
            and item["period"] == "FY2024"
        )
        fy2024_item = next(
            item
            for item in payload["assessments"]["items"]
            if item["locator"] == fy2024_locator
        )
        if kind == "scope":
            assert fy2024_item["status"] == STATUS_UNSUPPORTED_VARIANT
            assert "contradictory_geography" in fy2024_item["unresolved_reasons"]
            assert fy2024_item["metric_identity"] != identity
        elif kind == "unit":
            assert fy2024_item["status"] == STATUS_UNSUPPORTED_VARIANT
            assert "contradictory_unit" in fy2024_item["unresolved_reasons"]
            assert fy2024_item["comparability"] == COMPARABILITY_UNRESOLVED
        else:
            assert fy2024_item["status"] == STATUS_SUPPORTED
            assert fy2024_item["comparability"] == COMPARABILITY_NOT_COMPARABLE
            assert fy2024_item["metric_identity"] == identity


def test_unknown_variant_is_retained_with_reason(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[:1] + MANAGEMENT_NAMES[:1], tmp_path / "var")
    payload = json.loads((dest / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    payload["reported_kpis"][0]["metric_id"] = "digital_comparable_sales_growth"
    payload["reported_kpis"][0]["category"] = "comparable_sales"
    (dest / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    admission = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    variant = next(
        item
        for item in admission["assessments"]["items"]
        if item["status"] == STATUS_UNSUPPORTED_VARIANT
    )
    assert variant["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    assert "unknown_variant" in variant["unresolved_reasons"]
    assert variant["comparability"] == COMPARABILITY_UNRESOLVED
    assert variant["metric_identity"] == ""
    observation = next(
        item
        for item in admission["observations"]
        if item["locator"] == variant["locator"]
    )
    assert observation["metric_id"] == "digital_comparable_sales_growth"
    assert observation["value"] == payload["reported_kpis"][0]["value"]


def test_duplicate_supported_observations_are_retained(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "dup")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    original = copy.deepcopy(payload["reported_kpis"][2])
    duplicate = copy.deepcopy(original)
    duplicate["value"] = original["value"] + 1
    payload["reported_kpis"].append(duplicate)
    (dest / MANAGEMENT_NAMES[1]).write_text(json.dumps(payload), encoding="utf-8")
    admission = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )
    compsales = [
        item
        for item in admission["observations"]
        if item["kind"] == "reported_kpi"
        and item["metric_id"] == "comparable_sales_growth"
    ]
    assert len(compsales) == 2
    values = {item["value"] for item in compsales}
    assert values == {original["value"], original["value"] + 1}
    assessments = [
        item
        for item in admission["assessments"]["items"]
        if item["locator"] in {obs["locator"] for obs in compsales}
    ]
    assert len(assessments) == 2
    assert assessments[0]["metric_identity"] == assessments[1]["metric_identity"]
    assert set(assessments[0]["peer_locators"]) == {
        obs["locator"] for obs in compsales
    }


def test_renamed_reordered_inputs_preserve_semantic_assessments(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    renamed = tmp_path / "renamed"
    renamed.mkdir()
    mapping = {}
    for index, name in enumerate(reversed(ANNUAL_NAMES + MANAGEMENT_NAMES)):
        dest_name = f"{index:02d}-{name}"
        shutil.copy2(EXTRACTED / name, renamed / dest_name)
        mapping[name] = dest_name
    mixed_payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(mixed, source_root=SOURCE))
    )
    renamed_payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(renamed, source_root=SOURCE))
    )
    mixed_supported = sorted(
        (
            item["metric_identity"],
            item["comparability"],
            item["status"],
            item["evidence"]["period"],
            item["evidence"]["bound_source_file"],
            item["definition"]["text"],
        )
        for item in mixed_payload["assessments"]["items"]
        if item["status"] == STATUS_SUPPORTED
    )
    renamed_supported = sorted(
        (
            item["metric_identity"],
            item["comparability"],
            item["status"],
            item["evidence"]["period"],
            item["evidence"]["bound_source_file"],
            item["definition"]["text"],
        )
        for item in renamed_payload["assessments"]["items"]
        if item["status"] == STATUS_SUPPORTED
    )
    assert mixed_supported == renamed_supported
    assert mixed_payload["assessments"]["supported_count"] == renamed_payload[
        "assessments"
    ]["supported_count"]
    mixed_locators = {item["locator"] for item in mixed_payload["assessments"]["items"]}
    renamed_locators = {
        item["locator"] for item in renamed_payload["assessments"]["items"]
    }
    assert mixed_locators.isdisjoint(renamed_locators)
    for item in renamed_payload["assessments"]["items"]:
        assert any(name in item["locator"] for name in mapping.values())
        assert item["evidence"]["bound_source_file"].endswith("_Annual_Report.pdf")
    assert _bytes_by_name(EXTRACTED) == before


def test_ordinary_admission_keeps_canonical_payloads_unchanged(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual_rec = reconcile_filings(
        load_and_validate_extracted_dir(annual, source_root=SOURCE)
    )
    mixed_rec = reconcile_filings(
        load_and_validate_extracted_dir(mixed, source_root=SOURCE)
    )
    assert _canonicalize(standardized_to_payload(standardize_reconciled(annual_rec))) == (
        _canonicalize(standardized_to_payload(standardize_reconciled(mixed_rec)))
    )
    assert _statement_provenance(reconciliation_provenance_payload(annual_rec)) == (
        _statement_provenance(reconciliation_provenance_payload(mixed_rec))
    )
    assert reconciliation_conflicts_payload(annual_rec) == (
        reconciliation_conflicts_payload(mixed_rec)
    )
    mixed_payload = reconciliation_management_admission_payload(mixed_rec)
    assert mixed_payload["canonical_selection"] == "deferred"
    assert mixed_payload["assessments"]["canonical_selection"] == "deferred"
    assert "canonical_identity" not in mixed_payload["unresolved"]
    assert "comparability" not in mixed_payload["unresolved"]
    targets = [
        item
        for item in mixed_payload["observations"]
        if item["kind"] == "management_target"
    ]
    assert len(targets) == 3
    assert all(item["historical_role"] == "nonhistorical" for item in targets)
    market = [
        item
        for item in mixed_payload["observations"]
        if item["kind"].startswith("store_count_")
    ]
    assert market
    assessed_locators = {item["locator"] for item in mixed_payload["assessments"]["items"]}
    assert not {item["locator"] for item in targets} & assessed_locators
    assert not {item["locator"] for item in market} & assessed_locators
    counts = {}
    for item in mixed_payload["observations"]:
        if item["kind"] == "reported_kpi":
            counts[item["filing_year"]] = counts.get(item["filing_year"], 0) + 1
    assert counts == REPORTED_COUNTS
    assert _bytes_by_name(EXTRACTED) == before
