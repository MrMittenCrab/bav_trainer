"""Identity and comparability assessments for supported management KPIs."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

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
    REASON_CALENDAR_REPORTING,
    REASON_CALENDAR_WEEK,
    REASON_MISSING_COMPARISON,
    REASON_MISSING_DEFINITION,
    REASON_NO_DISTINCT_PEER,
    REASON_PERIOD_DATE,
    REQUIRED_COMPARISON_REASONS,
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


AFFIRMATIVE_COMPSALES_DEFINITION = (
    "Affirmative comparable-sales definition used only in temporary fixtures."
)
AFFIRMATIVE_SPSF_DEFINITION = (
    "Affirmative sales-per-square-foot definition used only in temporary fixtures."
)
AFFIRMATIVE_REPORTING_BASIS = (
    "Affirmative calendar reporting basis used only in temporary fixtures."
)
AFFIRMATIVE_SPSF_COMPARISON = "not_applicable"
REPORTING_BASIS_52 = "Fiscal calendar contains 52 weeks."
REPORTING_BASIS_53 = "Fiscal calendar contains 53 weeks."
FALSE_POSITIVE_METRIC_IDS = {
    "comparable_store_sales_growth",
    "comparable_store_sales_growth_constant_dollar",
    "total_comparable_sales_growth",
    "total_comparable_sales_growth_constant_dollar",
    "comparable_sales_growth_constant_dollar",
    "americas_comparable_sales_growth_constant_dollar",
}


def _supported_items(payload: dict) -> list[dict]:
    return [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == STATUS_SUPPORTED
    ]


def _admission(dest: Path) -> dict:
    return reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(dest, source_root=SOURCE))
    )


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _global_reported_compsales(items: list[dict]) -> list[dict]:
    return [
        item
        for item in items
        if item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and item["metric_identity_fields"].get("geography") == "global"
        and item["metric_identity_fields"].get("basis") == "reported"
        and item["metric_identity_fields"].get("population")
        == "company_operated_stores_and_ecommerce"
    ]


def _apply_affirmative_compsales(payload: dict, *, week: bool = False) -> dict:
    payload = copy.deepcopy(payload)
    period = payload["report"]["fiscal_year_end"]
    payload["report"]["reporting_basis"] = AFFIRMATIVE_REPORTING_BASIS
    payload["kpi_definitions"][0]["definition"] = AFFIRMATIVE_COMPSALES_DEFINITION
    for item in payload["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["period"] = period
            item["qualifiers"] = {"excludes_53rd_week": week}
    return payload


def _apply_affirmative_spsf(payload: dict, *, week: bool = False) -> dict:
    payload = copy.deepcopy(payload)
    period = payload["report"]["fiscal_year_end"]
    payload["report"]["reporting_basis"] = AFFIRMATIVE_REPORTING_BASIS
    payload["kpi_definitions"][1]["definition"] = AFFIRMATIVE_SPSF_DEFINITION
    for item in payload["reported_kpis"]:
        if item.get("metric_id") == "sales_per_square_foot":
            item["period"] = period
            item["qualifiers"] = {"excludes_53rd_week": week}
            item["comparison"] = AFFIRMATIVE_SPSF_COMPARISON
    return payload


def _spsf_items(items: list[dict]) -> list[dict]:
    return [
        item
        for item in items
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT
    ]


def _family_items(items: list[dict], family: str) -> list[dict]:
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        return _global_reported_compsales(items)
    return _spsf_items(items)


def _affirmative_family_pair(family: str) -> tuple[dict, dict]:
    fy2023 = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    fy2024 = json.loads((EXTRACTED / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        return (
            _apply_affirmative_compsales(fy2023),
            _apply_affirmative_compsales(fy2024),
        )
    return (_apply_affirmative_spsf(fy2023), _apply_affirmative_spsf(fy2024))


def _set_reporting_basis(payload: dict, value: str | None) -> dict:
    payload = copy.deepcopy(payload)
    if value is None:
        payload["report"].pop("reporting_basis", None)
    else:
        payload["report"]["reporting_basis"] = value
    return payload


def _affirmative_pair() -> tuple[dict, dict]:
    fy2023 = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    fy2024 = json.loads((EXTRACTED / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    return (
        _apply_affirmative_compsales(fy2023),
        _apply_affirmative_compsales(fy2024),
    )


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
        assert item["locator"] not in item["peer_locators"]
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
            assert item["evidence"]["calendar_reporting_basis"]
            if item["comparability"] == COMPARABILITY_COMPARABLE:
                assert not set(REQUIRED_COMPARISON_REASONS) & set(
                    item["unresolved_reasons"]
                )
                assert item["peer_locators"]
                assert item["evidence"]["calendar_reporting_basis"]
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


def test_affirmative_evidence_makes_distinct_occurrences_comparable(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "ok")
    fy2023, fy2024 = _affirmative_pair()
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    payload = _admission(dest)
    items = _global_reported_compsales(_supported_items(payload))
    assert len(items) == 2
    assert {item["comparability"] for item in items} == {COMPARABILITY_COMPARABLE}
    for item in items:
        assert item["locator"] not in item["peer_locators"]
        assert item["peer_locators"]
        assert not set(REQUIRED_COMPARISON_REASONS) & set(item["unresolved_reasons"])
        assert item["evidence"]["period_kind"] == "date"
        assert item["evidence"]["calendar_week_adjustment"] == "included"
        assert item["evidence"]["calendar_reporting_basis"] == (
            AFFIRMATIVE_REPORTING_BASIS
        )
        assert item["definition"]["text"] == AFFIRMATIVE_COMPSALES_DEFINITION


def test_affirmative_spsf_distinct_occurrences_are_comparable(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "spsf-ok")
    fy2023, fy2024 = _affirmative_family_pair(FAMILY_SALES_PER_SQUARE_FOOT)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    payload = _admission(dest)
    items = _spsf_items(_supported_items(payload))
    assert len(items) == 2
    assert {item["comparability"] for item in items} == {COMPARABILITY_COMPARABLE}
    for item in items:
        assert item["locator"] not in item["peer_locators"]
        assert item["peer_locators"]
        assert not set(REQUIRED_COMPARISON_REASONS) & set(item["unresolved_reasons"])
        assert item["evidence"]["period_kind"] == "date"
        assert item["evidence"]["calendar_week_adjustment"] == "included"
        assert item["evidence"]["calendar_reporting_basis"] == (
            AFFIRMATIVE_REPORTING_BASIS
        )
        assert item["evidence"]["comparison"] == AFFIRMATIVE_SPSF_COMPARISON
        assert item["definition"]["text"] == AFFIRMATIVE_SPSF_DEFINITION


def test_removing_period_calendar_or_definition_unresolves_comparability(
    tmp_path: Path,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rm")
    fy2023, fy2024 = _affirmative_pair()
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)

    period_mut = copy.deepcopy(fy2024)
    for item in period_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["period"] = "FY2024"
    _write_json(dest / MANAGEMENT_NAMES[2], period_mut)
    period_items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in period_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert any(REASON_PERIOD_DATE in item["unresolved_reasons"] for item in period_items)

    calendar_mut = copy.deepcopy(fy2024)
    for item in calendar_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    _write_json(dest / MANAGEMENT_NAMES[2], calendar_mut)
    calendar_items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in calendar_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert any(
        REASON_CALENDAR_WEEK in item["unresolved_reasons"] for item in calendar_items
    )

    defined_mut = copy.deepcopy(fy2024)
    for item in defined_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["definition_id"] = ""
    _write_json(dest / MANAGEMENT_NAMES[2], defined_mut)
    defined_items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in defined_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert any(
        REASON_MISSING_DEFINITION in item["unresolved_reasons"] for item in defined_items
    )


def test_missing_calendar_on_either_or_both_peers_is_unresolved(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "cal")
    fy2023, fy2024 = _affirmative_pair()

    both_missing = copy.deepcopy(fy2024)
    for payload in (fy2023, both_missing):
        for item in payload["reported_kpis"]:
            if item.get("metric_id") == "comparable_sales_growth":
                item.pop("qualifiers", None)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], both_missing)
    both_items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in both_items} == {COMPARABILITY_UNRESOLVED}
    assert all(REASON_CALENDAR_WEEK in item["unresolved_reasons"] for item in both_items)

    fy2023, fy2024 = _affirmative_pair()
    peer_missing = copy.deepcopy(fy2024)
    for item in peer_missing["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], peer_missing)
    either_items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in either_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert any(
        REASON_CALENDAR_WEEK in item["unresolved_reasons"] for item in either_items
    )
    assert COMPARABILITY_NOT_COMPARABLE not in {
        item["comparability"] for item in either_items
    }


@pytest.mark.parametrize(
    "family",
    [FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT],
)
@pytest.mark.parametrize("empty_repr", [None, ""])
def test_missing_reporting_basis_on_either_or_both_peers_is_unresolved(
    tmp_path: Path,
    family: str,
    empty_repr: str | None,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rb")
    fy2023, fy2024 = _affirmative_family_pair(family)

    both_left = _set_reporting_basis(fy2023, empty_repr)
    both_right = _set_reporting_basis(fy2024, empty_repr)
    _write_json(dest / MANAGEMENT_NAMES[1], both_left)
    _write_json(dest / MANAGEMENT_NAMES[2], both_right)
    both_items = _family_items(_supported_items(_admission(dest)), family)
    assert len(both_items) == 2
    assert {item["comparability"] for item in both_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert all(
        REASON_CALENDAR_REPORTING in item["unresolved_reasons"] for item in both_items
    )
    assert all(
        "calendar_reporting_mismatch" not in item["unresolved_reasons"]
        for item in both_items
    )
    assert all(item["peer_locators"] for item in both_items)
    assert all(REASON_NO_DISTINCT_PEER not in item["unresolved_reasons"] for item in both_items)

    fy2023, fy2024 = _affirmative_family_pair(family)
    either_right = _set_reporting_basis(fy2024, empty_repr)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], either_right)
    either_items = _family_items(_supported_items(_admission(dest)), family)
    assert {item["comparability"] for item in either_items} == {
        COMPARABILITY_UNRESOLVED
    }
    assert any(
        REASON_CALENDAR_REPORTING in item["unresolved_reasons"] for item in either_items
    )
    assert all(
        "calendar_reporting_mismatch" not in item["unresolved_reasons"]
        for item in either_items
    )
    assert COMPARABILITY_NOT_COMPARABLE not in {
        item["comparability"] for item in either_items
    }
    assert all(item["peer_locators"] for item in either_items)

    fy2023, fy2024 = _affirmative_family_pair(family)
    either_left = _set_reporting_basis(fy2023, empty_repr)
    _write_json(dest / MANAGEMENT_NAMES[1], either_left)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    left_items = _family_items(_supported_items(_admission(dest)), family)
    assert {item["comparability"] for item in left_items} == {COMPARABILITY_UNRESOLVED}
    assert any(
        REASON_CALENDAR_REPORTING in item["unresolved_reasons"] for item in left_items
    )
    assert all(
        "calendar_reporting_mismatch" not in item["unresolved_reasons"]
        for item in left_items
    )


@pytest.mark.parametrize(
    "family",
    [FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT],
)
def test_incompatible_reporting_bases_are_not_comparable(
    tmp_path: Path,
    family: str,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rbinc")
    fy2023, fy2024 = _affirmative_family_pair(family)
    fy2023 = _set_reporting_basis(fy2023, REPORTING_BASIS_52)
    fy2024 = _set_reporting_basis(fy2024, REPORTING_BASIS_53)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    items = _family_items(_supported_items(_admission(dest)), family)
    assert {item["comparability"] for item in items} == {COMPARABILITY_NOT_COMPARABLE}
    assert all(
        item["evidence"]["calendar_week_adjustment"] == "included" for item in items
    )
    assert all(
        item["evidence"]["period_kind"] == "date" for item in items
    )
    assert {item["definition"]["text"] for item in items} == {
        AFFIRMATIVE_COMPSALES_DEFINITION
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else AFFIRMATIVE_SPSF_DEFINITION
    }
    assert all(
        "calendar_reporting_mismatch" in item["unresolved_reasons"] for item in items
    )
    assert all("calendar_mismatch" not in item["unresolved_reasons"] for item in items)
    assert all(REASON_CALENDAR_WEEK not in item["unresolved_reasons"] for item in items)
    assert all(REASON_PERIOD_DATE not in item["unresolved_reasons"] for item in items)

    reversed_2023 = _set_reporting_basis(
        _affirmative_family_pair(family)[0], REPORTING_BASIS_53
    )
    reversed_2024 = _set_reporting_basis(
        _affirmative_family_pair(family)[1], REPORTING_BASIS_52
    )
    _write_json(dest / MANAGEMENT_NAMES[1], reversed_2023)
    _write_json(dest / MANAGEMENT_NAMES[2], reversed_2024)
    reversed_items = _family_items(_supported_items(_admission(dest)), family)
    assert {item["comparability"] for item in reversed_items} == {
        COMPARABILITY_NOT_COMPARABLE
    }
    assert all(
        "calendar_reporting_mismatch" in item["unresolved_reasons"]
        for item in reversed_items
    )


@pytest.mark.parametrize(
    "family",
    [FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT],
)
def test_reporting_basis_conflict_with_missing_evidence_stays_not_comparable(
    tmp_path: Path,
    family: str,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rbmix")
    fy2023, fy2024 = _affirmative_family_pair(family)
    fy2024 = _set_reporting_basis(fy2024, REPORTING_BASIS_53)
    metric_id = (
        "comparable_sales_growth"
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else "sales_per_square_foot"
    )
    for item in fy2024["reported_kpis"]:
        if item.get("metric_id") == metric_id:
            item.pop("qualifiers", None)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    items = _family_items(_supported_items(_admission(dest)), family)
    assert {item["comparability"] for item in items} == {COMPARABILITY_NOT_COMPARABLE}
    assert any(
        "calendar_reporting_mismatch" in item["unresolved_reasons"] for item in items
    )
    assert any(REASON_CALENDAR_WEEK in item["unresolved_reasons"] for item in items)


def test_complete_metadata_singleton_is_unresolved(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "one")
    fy2023 = _apply_affirmative_compsales(
        json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    )
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert len(items) == 1
    item = items[0]
    assert item["comparability"] == COMPARABILITY_UNRESOLVED
    assert REASON_NO_DISTINCT_PEER in item["unresolved_reasons"]
    assert item["peer_locators"] == []
    assert item["evidence"]["period_kind"] == "date"
    assert item["definition"]["text"] == AFFIRMATIVE_COMPSALES_DEFINITION
    assert item["evidence"]["calendar_week_adjustment"] == "included"
    assert item["evidence"]["calendar_reporting_basis"] == AFFIRMATIVE_REPORTING_BASIS


def test_unknown_versus_known_metadata_is_not_a_proven_mismatch(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "unk")
    fy2023, fy2024 = _affirmative_pair()
    for item in fy2024["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    items = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in items} == {COMPARABILITY_UNRESOLVED}
    assert all("calendar_mismatch" not in item["unresolved_reasons"] for item in items)


def test_evidenced_incompatibility_is_not_comparable(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "inc")
    fy2023, fy2024 = _affirmative_pair()
    fy2024["kpi_definitions"][0]["definition"] = (
        AFFIRMATIVE_COMPSALES_DEFINITION + " shifted weeks"
    )
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    defined = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in defined} == {COMPARABILITY_NOT_COMPARABLE}
    assert any("definition_mismatch" in item["unresolved_reasons"] for item in defined)

    fy2023, fy2024 = _affirmative_pair()
    fy2024 = _apply_affirmative_compsales(fy2024, week=True)
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    calendar = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in calendar} == {
        COMPARABILITY_NOT_COMPARABLE
    }
    assert any("calendar_mismatch" in item["unresolved_reasons"] for item in calendar)

    fy2023, fy2024 = _affirmative_pair()
    for item in fy2024["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item.pop("qualifiers", None)
    fy2024["kpi_definitions"][0]["definition"] = (
        AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    )
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    mixed = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in mixed} == {COMPARABILITY_NOT_COMPARABLE}
    assert any("definition_mismatch" in item["unresolved_reasons"] for item in mixed)
    assert any(REASON_CALENDAR_WEEK in item["unresolved_reasons"] for item in mixed)


def test_mutations_cannot_silently_preserve_comparability(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "mut")
    fy2023, fy2024 = _affirmative_pair()
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    baseline = _admission(dest)
    identity = next(
        item["metric_identity"]
        for item in _global_reported_compsales(_supported_items(baseline))
    )
    assert all(
        item["comparability"] == COMPARABILITY_COMPARABLE
        for item in _supported_items(baseline)
        if item["metric_identity"] == identity
    )

    period = fy2024["report"]["fiscal_year_end"]
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
    basis_mut = copy.deepcopy(fy2024)
    for item in basis_mut["reported_kpis"]:
        if item.get("metric_id") == "comparable_sales_growth":
            item["basis"] = "constant_dollar"
    cases.append(("basis", basis_mut))
    reporting_mut = copy.deepcopy(fy2024)
    reporting_mut["report"]["reporting_basis"] = REPORTING_BASIS_53
    cases.append(("reporting_basis", reporting_mut))

    for kind, mutated in cases:
        _write_json(dest / MANAGEMENT_NAMES[2], mutated)
        payload = _admission(dest)
        fy2024_item = next(
            item
            for item in payload["assessments"]["items"]
            if item["locator"]
            == next(
                obs["locator"]
                for obs in payload["observations"]
                if obs["kind"] == "reported_kpi"
                and obs["metric_id"] == "comparable_sales_growth"
                and obs["period"] == period
            )
        )
        if kind == "scope":
            assert fy2024_item["status"] == STATUS_UNSUPPORTED_VARIANT
            assert "contradictory_geography" in fy2024_item["unresolved_reasons"]
            assert fy2024_item["metric_identity"] != identity
        elif kind in {"unit", "basis"}:
            assert fy2024_item["status"] == STATUS_UNSUPPORTED_VARIANT
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
    locators = {obs["locator"] for obs in compsales}
    for item in assessments:
        assert item["locator"] not in item["peer_locators"]
        assert set(item["peer_locators"]) == locators - {item["locator"]}


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
    assert len(market) == 107
    assessed_locators = {item["locator"] for item in mixed_payload["assessments"]["items"]}
    assert not {item["locator"] for item in targets} & assessed_locators
    assert not {item["locator"] for item in market} & assessed_locators
    counts = {}
    for item in mixed_payload["observations"]:
        if item["kind"] == "reported_kpi":
            counts[item["filing_year"]] = counts.get(item["filing_year"], 0) + 1
    assert counts == REPORTED_COUNTS
    assert _bytes_by_name(EXTRACTED) == before


def test_supplied_false_positives_remain_unresolved():
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE))
    )
    reported = {
        item["locator"]: item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
    }
    false_positives = [
        item
        for item in payload["assessments"]["items"]
        if reported[item["locator"]]["metric_id"] in FALSE_POSITIVE_METRIC_IDS
    ]
    assert len(false_positives) == 6
    assert {item["comparability"] for item in false_positives} == {
        COMPARABILITY_UNRESOLVED
    }
    for item in false_positives:
        assert not item["peer_locators"]
        assert REASON_NO_DISTINCT_PEER in item["unresolved_reasons"]
        assert REASON_PERIOD_DATE in item["unresolved_reasons"]
        assert item["locator"] not in item["peer_locators"]
    counts = payload["assessments"]["comparability_counts"]
    assert counts[COMPARABILITY_COMPARABLE] == 0
    assert counts[COMPARABILITY_NOT_COMPARABLE] == 22
    assert counts[COMPARABILITY_UNRESOLVED] == 6
    assert counts[COMPARABILITY_OUTSIDE_SCOPE] == 107
    assert payload["assessments"]["supported_count"] == 28
    assert payload["assessments"]["outside_scope_count"] == 107


def test_equal_missing_comparison_cannot_make_spsf_comparable(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "spsf")
    fy2023 = json.loads((EXTRACTED / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    fy2024 = json.loads((EXTRACTED / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    shared = "Affirmative sales-per-square-foot definition for temporary fixtures."
    shared_basis = AFFIRMATIVE_REPORTING_BASIS
    for payload in (fy2023, fy2024):
        payload["report"]["reporting_basis"] = shared_basis
        payload["kpi_definitions"][1]["definition"] = shared
        period = payload["report"]["fiscal_year_end"]
        for item in payload["reported_kpis"]:
            if item.get("metric_id") == "sales_per_square_foot":
                item["period"] = period
                item["qualifiers"] = {"excludes_53rd_week": False}
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    items = [
        item
        for item in _supported_items(_admission(dest))
        if item["family"] == FAMILY_SALES_PER_SQUARE_FOOT
    ]
    assert len(items) == 2
    assert {item["comparability"] for item in items} == {COMPARABILITY_UNRESOLVED}
    assert all(REASON_MISSING_COMPARISON in item["unresolved_reasons"] for item in items)
    assert all(item["peer_locators"] for item in items)


def test_self_exclusion_and_input_order_independent_comparability(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "ord")
    fy2023, fy2024 = _affirmative_pair()
    _write_json(dest / MANAGEMENT_NAMES[1], fy2023)
    _write_json(dest / MANAGEMENT_NAMES[2], fy2024)
    forward = _global_reported_compsales(_supported_items(_admission(dest)))
    reversed_2024 = copy.deepcopy(fy2024)
    reversed_2024["reported_kpis"] = list(reversed(reversed_2024["reported_kpis"]))
    reversed_2023 = copy.deepcopy(fy2023)
    reversed_2023["reported_kpis"] = list(reversed(reversed_2023["reported_kpis"]))
    _write_json(dest / MANAGEMENT_NAMES[1], reversed_2023)
    _write_json(dest / MANAGEMENT_NAMES[2], reversed_2024)
    backward = _global_reported_compsales(_supported_items(_admission(dest)))
    assert {item["comparability"] for item in forward} == {COMPARABILITY_COMPARABLE}
    assert {item["comparability"] for item in backward} == {COMPARABILITY_COMPARABLE}
    assert {item["metric_identity"] for item in forward} == {
        item["metric_identity"] for item in backward
    }
    for item in forward + backward:
        assert item["locator"] not in item["peer_locators"]
        assert len(item["peer_locators"]) == 1
