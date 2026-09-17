"""Pairwise duplicate/conflict reconciliation for supported management KPIs."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import pytest

from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import reconciliation_management_admission_payload
from core.ingestion.management_kpi_identity import (
    COMPARABILITY_COMPARABLE,
    COMPARABILITY_NOT_COMPARABLE,
    COMPARABILITY_UNRESOLVED,
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    REASON_CALENDAR_REPORTING,
    REASON_CALENDAR_WEEK,
    REASON_MISSING_COMPARISON,
    REASON_PERIOD_MISMATCH,
    REQUIRED_COMPARISON_REASONS,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED_VARIANT,
    peer_gap_reason,
)
from core.ingestion.management_kpi_reconciliation import (
    KIND_OUTSIDE_SCOPE,
    KIND_PAIR,
    KIND_SINGLETON,
    KIND_UNSUPPORTED_VARIANT,
    NAMED_PRESENTATION_COMBINATIONS,
    OUTCOME_AGREEING_DUPLICATE,
    OUTCOME_CONFLICTING_CANDIDATE,
    OUTCOME_INCOMPATIBLE,
    OUTCOME_UNRESOLVED,
    PRESENTATION_RELATIONSHIP_ROLES,
    PRESENTATION_ROLE_COMBINATIONS,
    REASON_MISSING_VALUE,
    REASON_MISSING_TARGET,
    REASON_MISSING_EVIDENCE,
    REASON_AMBIGUOUS_TARGET,
    REASON_OUTSIDE_SCOPE_TARGET,
    REASON_RECIPROCAL,
    REASON_CYCLIC,
    REASON_SINGLETON,
    REASON_GROUP_LARGER_THAN_TWO,
    REASON_MISSING_REVISION_LINK,
    REASON_COMPETING_DIRECTION,
    REASON_MISSING_REVISER_VALUE,
    REASON_UNKNOWN_ASSURANCE,
    REASON_UNAUDITED_REVISER,
    RELATIONSHIP_INCOMPATIBLE,
    RELATIONSHIP_RECOGNIZED,
    RELATIONSHIP_UNRESOLVED,
    SELECTION_DEFERRED,
    SELECTION_SELECTED,
    presentation_role_combination,
)
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    ROOT,
    SOURCE,
    _bytes_by_name,
    _copy_json,
)
from core.tests.test_management_kpi_identity import (
    AFFIRMATIVE_COMPSALES_DEFINITION,
    AFFIRMATIVE_SPSF_DEFINITION,
    FALSE_POSITIVE_METRIC_IDS,
    REPORTING_BASIS_52,
    REPORTING_BASIS_53,
    _admission,
    _affirmative_family_pair,
    _family_metric_id,
    _set_reporting_basis,
    _write_json,
)

FAMILIES = (FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT)
SHARED_PERIOD = "2024-01-28"


def _pairs(payload: dict) -> list[dict]:
    return [
        item
        for item in payload["reconciliation"]["items"]
        if item["kind"] == KIND_PAIR
    ]


def _coverage(payload: dict, kind: str) -> list[dict]:
    return [
        item
        for item in payload["reconciliation"]["items"]
        if item["kind"] == kind
    ]


def _metric_pairs(payload: dict, family: str) -> list[dict]:
    locators = set(_family_metric_locators(payload, family))
    return [
        item
        for item in _pairs(payload)
        if set(item["locators"]) <= locators
    ]


def _pair_key(item: dict) -> frozenset[str]:
    return frozenset(item["locators"])


def _pair_by_locators(items: list[dict], locators: Iterable[str] | frozenset[str]) -> dict:
    key = frozenset(locators)
    matches = [item for item in items if _pair_key(item) == key]
    assert len(matches) == 1
    return matches[0]


def _family_metric_locators(payload: dict, family: str) -> list[str]:
    metric_id = _family_metric_id(family)
    return [
        item["locator"]
        for item in payload["observations"]
        if item["kind"] == "reported_kpi" and item["metric_id"] == metric_id
    ]


def _assessment(payload: dict, locator: str) -> dict:
    return next(
        item for item in payload["assessments"]["items"] if item["locator"] == locator
    )


def _apply_same_period(
    payload: dict,
    family: str,
    *,
    period: str,
    value: object | None = Ellipsis,
) -> dict:
    payload = copy.deepcopy(payload)
    metric_id = _family_metric_id(family)
    for item in payload["reported_kpis"]:
        if item.get("metric_id") == metric_id:
            item["period"] = period
            if value is not Ellipsis:
                item["value"] = value
    return payload


def _write_family_pair(
    dest: Path,
    family: str,
    *,
    left_value: object | None = Ellipsis,
    right_value: object | None = Ellipsis,
    left_mutate=None,
    right_mutate=None,
) -> None:
    left, right = _affirmative_family_pair(family)
    left = _apply_same_period(left, family, period=SHARED_PERIOD, value=left_value)
    right = _apply_same_period(right, family, period=SHARED_PERIOD, value=right_value)
    if left_mutate is not None:
        left = left_mutate(left)
    if right_mutate is not None:
        right = right_mutate(right)
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)


def _write_three_peer(
    dest: Path,
    family: str,
    *,
    values: tuple[object, object, object] = (10, 10, 10),
    third_mutate=None,
) -> None:
    first, second = _affirmative_family_pair(family)
    third = json.loads((EXTRACTED / MANAGEMENT_NAMES[3]).read_text(encoding="utf-8"))
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        from core.tests.test_management_kpi_identity import _apply_affirmative_compsales

        third = _apply_affirmative_compsales(third)
    else:
        from core.tests.test_management_kpi_identity import _apply_affirmative_spsf

        third = _apply_affirmative_spsf(third)
    payloads = [
        _apply_same_period(first, family, period=SHARED_PERIOD, value=values[0]),
        _apply_same_period(second, family, period=SHARED_PERIOD, value=values[1]),
        _apply_same_period(third, family, period=SHARED_PERIOD, value=values[2]),
    ]
    if third_mutate is not None:
        payloads[2] = third_mutate(payloads[2])
    for name, payload in zip(MANAGEMENT_NAMES[1:4], payloads):
        _write_json(dest / name, payload)


def _mutate_metric(payload: dict, family: str, mutate) -> dict:
    payload = copy.deepcopy(payload)
    metric_id = _family_metric_id(family)
    for item in payload["reported_kpis"]:
        if item.get("metric_id") == metric_id:
            mutate(item)
    return payload


def _assert_pair_members(item: dict) -> None:
    assert item["kind"] == KIND_PAIR
    assert len(item["locators"]) == 2
    assert item["locators"][0] != item["locators"][1]
    assert item["locators"] == sorted(item["locators"])
    assert [occ["locator"] for occ in item["occurrences"]] == item["locators"]
    assert item["canonical_selection"] == "deferred"
    left, right = item["occurrences"]
    assert left["locator"] != right["locator"]
    assert left["occurrence_identity"]
    assert right["occurrence_identity"]
    assert left["source"]["page_reference"]
    assert right["source"]["page_reference"]
    assert "physical_page_mapping" in left["source"]
    assert left["bound_source_file"].endswith(".pdf")
    fields = item["metric_identity_fields"]
    assert left["evidence"]["basis"] == fields["basis"]
    assert right["evidence"]["basis"] == fields["basis"]
    assert left["evidence"]["geography"] == fields["geography"]
    assert right["evidence"]["geography"] == fields["geography"]
    rel = item["presentation_relationship"]
    assert rel["status"] in {
        RELATIONSHIP_RECOGNIZED,
        RELATIONSHIP_UNRESOLVED,
        RELATIONSHIP_INCOMPATIBLE,
    }
    assert rel["combination"] in PRESENTATION_ROLE_COMBINATIONS.values()
    assert [member["locator"] for member in rel["members"]] == item["locators"]
    for member, occ in zip(rel["members"], item["occurrences"]):
        assert member["occurrence_identity"] == occ["occurrence_identity"]
        assert member["role"] == occ["presentation_evidence"]["role"]
        assert member["role"] in PRESENTATION_RELATIONSHIP_ROLES
        assert "revision_evidence" in occ
    for key in (
        "revises",
        "revision",
        "revision_link",
        "equivalent",
        "equivalence",
        "preferred",
        "precedence",
        "winner",
        "superseded",
        "chronology",
    ):
        assert key not in rel
    assert "revision_link" not in item
    assert "revision_links" not in item


def _assert_relationship(
    item: dict, *, status: str, combination: str, roles: set[str]
) -> None:
    _assert_pair_members(item)
    rel = item["presentation_relationship"]
    assert rel["status"] == status
    assert rel["combination"] == combination
    assert {member["role"] for member in rel["members"]} == roles


def _unordered_role_pairs() -> list[tuple[str, str]]:
    pairs = []
    for index, left in enumerate(PRESENTATION_RELATIONSHIP_ROLES):
        for right in PRESENTATION_RELATIONSHIP_ROLES[index:]:
            pairs.append((left, right))
    return pairs


def _assert_affirmative_duplicate(item: dict, *, values: tuple[object, object]) -> None:
    _assert_pair_members(item)
    assert item["outcome"] == OUTCOME_AGREEING_DUPLICATE
    assert {occ["value"] for occ in item["occurrences"]} == set(values)
    assert all(occ["period"] == SHARED_PERIOD for occ in item["occurrences"])
    assert all(occ["period_kind"] == "date" for occ in item["occurrences"])
    assert REASON_PERIOD_MISMATCH not in item["reasons"]
    assert REASON_MISSING_VALUE not in item["reasons"]
    assert peer_gap_reason(REASON_MISSING_VALUE) not in item["reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_same_period_agreeing_and_conflicting_pairs(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "agree")
    _write_family_pair(dest, family, left_value=10, right_value=10)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    assert len(locators) == 2
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_affirmative_duplicate(pair, values=(10, 10))
    for locator in locators:
        assert _assessment(payload, locator)["comparability"] == COMPARABILITY_COMPARABLE

    _write_family_pair(dest, family, left_value=10, right_value=11)
    conflicted = _admission(dest)
    locators = _family_metric_locators(conflicted, family)
    pair = _pair_by_locators(_metric_pairs(conflicted, family), locators)
    _assert_pair_members(pair)
    assert pair["outcome"] == OUTCOME_CONFLICTING_CANDIDATE
    assert {occ["value"] for occ in pair["occurrences"]} == {10, 11}
    assert pair["canonical_selection"] == "deferred"
    assert "preferred" not in pair
    years = {
        item["filing_year"]
        for item in conflicted["observations"]
        if item["locator"] in locators
    }
    assert years == {2023, 2024}
    for locator in locators:
        assert _assessment(conflicted, locator)["comparability"] == COMPARABILITY_COMPARABLE


@pytest.mark.parametrize("family", FAMILIES)
def test_missing_value_is_not_zero_and_does_not_conflict(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "zero")
    _write_family_pair(dest, family, left_value=None, right_value=0)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_pair_members(pair)
    assert pair["outcome"] == OUTCOME_UNRESOLVED
    values = [occ["value"] for occ in pair["occurrences"]]
    assert None in values
    assert 0 in values
    assert REASON_MISSING_VALUE in pair["reasons"] or peer_gap_reason(
        REASON_MISSING_VALUE
    ) in pair["reasons"]
    assert pair["outcome"] != OUTCOME_AGREEING_DUPLICATE
    assert pair["outcome"] != OUTCOME_CONFLICTING_CANDIDATE


@pytest.mark.parametrize("family", FAMILIES)
def test_different_periods_are_incompatible_not_duplicates(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "period")
    left, right = _affirmative_family_pair(family)
    metric_id = _family_metric_id(family)
    for payload in (left, right):
        for item in payload["reported_kpis"]:
            if item.get("metric_id") == metric_id:
                item["value"] = 10
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_pair_members(pair)
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    assert REASON_PERIOD_MISMATCH in pair["reasons"]
    periods = {occ["period"] for occ in pair["occurrences"]}
    assert len(periods) == 2
    for locator in locators:
        item = _assessment(payload, locator)
        assert item["comparability"] == COMPARABILITY_COMPARABLE
        assert REASON_PERIOD_MISMATCH not in item["unresolved_reasons"]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("blank", [None, "", " ", " \t "])
def test_blank_evidence_never_agrees_or_conflicts(
    tmp_path: Path, family: str, blank: str | None
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "blank")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        right_mutate=lambda payload: _set_reporting_basis(payload, blank),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    assert pair["outcome"] == OUTCOME_UNRESOLVED
    assert pair["outcome"] not in {
        OUTCOME_AGREEING_DUPLICATE,
        OUTCOME_CONFLICTING_CANDIDATE,
    }
    assert "calendar_reporting_mismatch" not in pair["reasons"]
    reasons = pair["reasons"]
    assert REASON_CALENDAR_REPORTING in reasons or peer_gap_reason(
        REASON_CALENDAR_REPORTING
    ) in reasons
    blank_repr = "" if blank is None else blank
    evidences = [occ["evidence"]["calendar_reporting_basis"] for occ in pair["occurrences"]]
    assert blank_repr in evidences or any(not str(item).strip() for item in evidences)
    for locator in locators:
        assert _assessment(payload, locator)["comparability"] == COMPARABILITY_UNRESOLVED


@pytest.mark.parametrize("family", FAMILIES)
def test_definition_and_calendar_conflicts_are_not_value_conflicts(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "conf")
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_definition(payload: dict) -> dict:
        payload = copy.deepcopy(payload)
        payload["kpi_definitions"][0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1][
            "definition"
        ] = changed
        return payload

    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        right_mutate=mutate_definition,
    )
    defined = _admission(dest)
    locators = _family_metric_locators(defined, family)
    pair = _pair_by_locators(_metric_pairs(defined, family), locators)
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    assert "definition_mismatch" in pair["reasons"]
    assert {occ["value"] for occ in pair["occurrences"]} == {10}

    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _set_reporting_basis(payload, REPORTING_BASIS_52),
        right_mutate=lambda payload: _set_reporting_basis(payload, REPORTING_BASIS_53),
    )
    calendar = _admission(dest)
    locators = _family_metric_locators(calendar, family)
    pair = _pair_by_locators(_metric_pairs(calendar, family), locators)
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    assert "calendar_reporting_mismatch" in pair["reasons"]
    for locator in locators:
        assert _assessment(calendar, locator)["comparability"] == COMPARABILITY_NOT_COMPARABLE


@pytest.mark.parametrize("family", FAMILIES)
def test_three_peer_incomplete_does_not_suppress_affirmative_pair(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three-gap")

    def drop_week(payload: dict) -> dict:
        return _mutate_metric(payload, family, lambda item: item.pop("qualifiers", None))

    _write_three_peer(dest, family, third_mutate=drop_week)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    assert len(locators) == 3
    pairs = _metric_pairs(payload, family)
    assert len(pairs) == 3
    assert { _pair_key(item) for item in pairs } == {
        frozenset(combo)
        for combo in (
            (locators[0], locators[1]),
            (locators[0], locators[2]),
            (locators[1], locators[2]),
        )
    }
    complete = [
        locator
        for locator in locators
        if str(_assessment(payload, locator)["evidence"]["calendar_week_adjustment"]).strip()
    ]
    incomplete = [locator for locator in locators if locator not in complete]
    assert len(complete) == 2
    assert len(incomplete) == 1
    affirmative = _pair_by_locators(pairs, complete)
    _assert_affirmative_duplicate(affirmative, values=(10, 10))
    for locator in complete:
        other = incomplete[0]
        gap_pair = _pair_by_locators(pairs, (locator, other))
        assert gap_pair["outcome"] == OUTCOME_UNRESOLVED
        assert REASON_CALENDAR_WEEK in gap_pair["reasons"] or peer_gap_reason(
            REASON_CALENDAR_WEEK
        ) in gap_pair["reasons"]
        assert gap_pair["outcome"] != OUTCOME_AGREEING_DUPLICATE
    for locator in locators:
        item = _assessment(payload, locator)
        if locator in incomplete:
            assert item["comparability"] == COMPARABILITY_UNRESOLVED
        else:
            assert item["comparability"] == COMPARABILITY_UNRESOLVED
            assert peer_gap_reason(REASON_CALENDAR_WEEK) in item["unresolved_reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_three_peer_incompatible_does_not_create_transitive_equivalence(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three-inc")
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_definition(payload: dict) -> dict:
        payload = copy.deepcopy(payload)
        payload["kpi_definitions"][0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1][
            "definition"
        ] = changed
        return payload

    _write_three_peer(
        dest, family, values=(10, 10, 11), third_mutate=mutate_definition
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pairs = _metric_pairs(payload, family)
    assert len(pairs) == 3
    incompatible_text = {
        occ["locator"]
        for item in pairs
        if item["outcome"] == OUTCOME_INCOMPATIBLE
        for occ in item["occurrences"]
        if occ["definition"]["text"] == changed
    }
    assert len(incompatible_text) == 1
    third = next(iter(incompatible_text))
    complete = [locator for locator in locators if locator != third]
    affirmative = _pair_by_locators(pairs, complete)
    _assert_affirmative_duplicate(affirmative, values=(10, 10))
    for locator in complete:
        other = _pair_by_locators(pairs, (locator, third))
        assert other["outcome"] == OUTCOME_INCOMPATIBLE
        assert "definition_mismatch" in other["reasons"]
        assert other["outcome"] != OUTCOME_AGREEING_DUPLICATE
    for locator in locators:
        item = _assessment(payload, locator)
        assert item["comparability"] == COMPARABILITY_NOT_COMPARABLE


@pytest.mark.parametrize("family", FAMILIES)
def test_three_complete_peers_evaluate_pairs_not_transitivity(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three-val")
    _write_three_peer(dest, family, values=(10, 10, 11))
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pairs = _metric_pairs(payload, family)
    outcomes = {item["outcome"] for item in pairs}
    assert outcomes == {OUTCOME_AGREEING_DUPLICATE, OUTCOME_CONFLICTING_CANDIDATE}
    agreeing = [item for item in pairs if item["outcome"] == OUTCOME_AGREEING_DUPLICATE]
    conflicting = [
        item for item in pairs if item["outcome"] == OUTCOME_CONFLICTING_CANDIDATE
    ]
    assert len(agreeing) == 1
    assert len(conflicting) == 2
    assert {occ["value"] for occ in agreeing[0]["occurrences"]} == {10}
    for item in conflicting:
        assert {occ["value"] for occ in item["occurrences"]} == {10, 11}
    for locator in locators:
        assert _assessment(payload, locator)["comparability"] == COMPARABILITY_COMPARABLE


def test_singleton_self_exclusion_and_distinct_identical_values(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "single")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    payload = json.loads(json.dumps(payload))
    from core.tests.test_management_kpi_identity import _apply_affirmative_compsales

    payload = _apply_affirmative_compsales(payload)
    original = next(
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") == "comparable_sales_growth"
    )
    original["period"] = payload["report"]["fiscal_year_end"]
    singleton_payload = copy.deepcopy(payload)
    _write_json(dest / MANAGEMENT_NAMES[1], singleton_payload)
    singleton = _admission(dest)
    locators = _family_metric_locators(singleton, FAMILY_COMPARABLE_SALES_GROWTH)
    assert len(locators) == 1
    assert _pairs(singleton) == []
    coverage = _coverage(singleton, KIND_SINGLETON)
    assert any(item["locators"] == locators for item in coverage)
    assert locators[0] not in _assessment(singleton, locators[0])["peer_locators"]
    assert all("presentation_relationship" not in item for item in coverage)

    duplicate = copy.deepcopy(original)
    payload["reported_kpis"].append(duplicate)
    _write_json(dest / MANAGEMENT_NAMES[1], payload)
    doubled = _admission(dest)
    locators = _family_metric_locators(doubled, FAMILY_COMPARABLE_SALES_GROWTH)
    assert len(locators) == 2
    assert locators[0] != locators[1]
    pair = _pair_by_locators(_metric_pairs(doubled, FAMILY_COMPARABLE_SALES_GROWTH), locators)
    _assert_affirmative_duplicate(pair, values=(original["value"], original["value"]))
    observations = [
        item
        for item in doubled["observations"]
        if item["locator"] in locators
    ]
    assert len(observations) == 2
    assert {item["value"] for item in observations} == {original["value"]}


def test_geography_and_basis_are_not_paired_together():
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE))
    )
    for item in _pairs(payload):
        left, right = item["occurrences"]
        assert left["evidence"]["geography"] == right["evidence"]["geography"]
        assert left["evidence"]["basis"] == right["evidence"]["basis"]
        assert left["evidence"]["population"] == right["evidence"]["population"]
        parsed = json.loads(item["metric_identity"])
        assert parsed["geography"] == left["evidence"]["geography"]
        assert parsed["basis"] == left["evidence"]["basis"]


def test_renamed_and_reversed_inputs_preserve_pair_semantics(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    reversed_dir = tmp_path / "reversed"
    reversed_dir.mkdir()
    renamed = tmp_path / "renamed"
    renamed.mkdir()
    for index, name in enumerate(reversed(ANNUAL_NAMES + MANAGEMENT_NAMES)):
        shutil.copy2(EXTRACTED / name, reversed_dir / name)
        shutil.copy2(EXTRACTED / name, renamed / f"{index:02d}-{name}")
    mixed_payload = _admission(mixed)
    reversed_payload = _admission(reversed_dir)
    renamed_payload = _admission(renamed)

    def signatures(payload: dict) -> list[tuple]:
        rows = []
        for item in payload["reconciliation"]["items"]:
            occs = tuple(
                sorted(
                    (
                        occ["occurrence_identity"],
                        occ["value"],
                        occ["period"],
                        occ["definition"]["text"],
                        occ["bound_source_file"],
                        tuple(occ["required_reasons"]),
                    )
                    for occ in item["occurrences"]
                )
            )
            gaps = set()
            conflicts = []
            gap_reasons = set(REQUIRED_COMPARISON_REASONS) | {REASON_MISSING_VALUE}
            for reason in item["reasons"]:
                base = reason[5:] if reason.startswith("peer_") else reason
                if base in gap_reasons:
                    gaps.add(base)
                else:
                    conflicts.append(reason)
            rows.append(
                (
                    item["kind"],
                    item["outcome"],
                    item["metric_identity"],
                    tuple(conflicts),
                    tuple(sorted(gaps)),
                    occs,
                    item.get("presentation_relationship", {}).get("status"),
                    item.get("presentation_relationship", {}).get("combination"),
                    tuple(
                        sorted(
                            member["role"]
                            for member in item.get("presentation_relationship", {}).get(
                                "members", ()
                            )
                        )
                    ),
                )
            )
        return sorted(rows)

    assert signatures(mixed_payload) == signatures(reversed_payload)
    assert signatures(mixed_payload) == signatures(renamed_payload)
    mixed_locators = {
        occ["locator"]
        for item in mixed_payload["reconciliation"]["items"]
        for occ in item["occurrences"]
    }
    renamed_locators = {
        occ["locator"]
        for item in renamed_payload["reconciliation"]["items"]
        for occ in item["occurrences"]
    }
    assert mixed_locators.isdisjoint(renamed_locators)
    assert mixed_payload["reconciliation"]["outcome_counts"] == renamed_payload[
        "reconciliation"
    ]["outcome_counts"]
    assert mixed_payload["reconciliation"]["revision_links"] == []
    assert renamed_payload["reconciliation"]["revision_links"] == []
    assert reversed_payload["reconciliation"]["revision_links"] == []
    assert mixed_payload["assessments"]["comparability_counts"] == renamed_payload[
        "assessments"
    ]["comparability_counts"]
    assert _bytes_by_name(EXTRACTED) == before


def test_supplied_inputs_have_no_invented_duplicates_or_conflicts():
    before = _bytes_by_name(EXTRACTED)
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE))
    )
    recon = payload["reconciliation"]
    counts = recon["outcome_counts"]
    assert payload["status"] == "admitted_unreconciled"
    assert recon["canonical_selection"] == "deferred"
    assert recon["selected_count"] == 0
    assert recon["superseded_count"] == 0
    assert recon["group_selection_counts"][SELECTION_SELECTED] == 0
    assert recon["group_selection_counts"][SELECTION_DEFERRED] == len(
        recon["group_selections"]
    )
    assert recon["group_selections"]
    for item in recon["group_selections"]:
        assert item["kind"] == "group_selection"
        assert item["status"] == SELECTION_DEFERRED
        assert item["selected"] is None
        assert item["superseded"] is None
        assert item["revision"] is None
        assert "canonical_selection" not in item
        assert item["reasons"]
    assert payload["assessments"]["comparability_counts"]["comparable"] == 0
    assert payload["assessments"]["comparability_counts"]["not_comparable"] == 22
    assert payload["assessments"]["comparability_counts"]["unresolved"] == 6
    assert payload["assessments"]["comparability_counts"]["outside_scope"] == 107
    supported = [
        item
        for item in payload["assessments"]["items"]
        if item["status"] == STATUS_SUPPORTED
    ]
    groups: dict[str, list[str]] = {}
    for item in supported:
        groups.setdefault(item["metric_identity"], []).append(item["locator"])
    expected_pairs = sum(len(items) * (len(items) - 1) // 2 for items in groups.values())
    expected_singletons = sum(1 for items in groups.values() if len(items) == 1)
    assert recon["pair_count"] == expected_pairs
    assert counts[KIND_SINGLETON] == expected_singletons
    assert expected_singletons == 6
    assert counts[OUTCOME_AGREEING_DUPLICATE] == 0
    assert counts[OUTCOME_CONFLICTING_CANDIDATE] == 0
    assert counts[KIND_OUTSIDE_SCOPE] == 107
    assert counts[KIND_UNSUPPORTED_VARIANT] == 0
    assert (
        counts[OUTCOME_INCOMPATIBLE] + counts[OUTCOME_UNRESOLVED]
        == recon["pair_count"]
    )
    pair_keys = [_pair_key(item) for item in _pairs(payload)]
    assert len(pair_keys) == len(set(pair_keys))
    covered = {
        occ["locator"]
        for item in recon["items"]
        for occ in item["occurrences"]
    }
    reported = {
        item["locator"]
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
    }
    assert covered == reported
    assert len(reported) == 135
    false_positives = [
        item
        for item in payload["assessments"]["items"]
        if next(
            obs
            for obs in payload["observations"]
            if obs["locator"] == item["locator"]
        )["metric_id"]
        in FALSE_POSITIVE_METRIC_IDS
    ]
    assert len(false_positives) == 6
    singleton_locators = {
        occ["locator"]
        for item in _coverage(payload, KIND_SINGLETON)
        for occ in item["occurrences"]
    }
    assert singleton_locators == {item["locator"] for item in false_positives}
    for item in recon["items"]:
        if item["kind"] == KIND_PAIR:
            _assert_pair_members(item)
            assert item["outcome"] in {OUTCOME_INCOMPATIBLE, OUTCOME_UNRESOLVED}
            assert item["locators"][0] not in [item["locators"][1]]
            assert item["presentation_relationship"]["status"] != RELATIONSHIP_RECOGNIZED
            assert item["presentation_relationship"]["combination"] == "unknown_unknown"
        else:
            assert len(item["locators"]) == 1
            assert item["locators"][0] == item["occurrences"][0]["locator"]
            assert "presentation_relationship" not in item
    outside = _coverage(payload, KIND_OUTSIDE_SCOPE)
    assert len(outside) == 107
    assert all(item["outcome"] == KIND_OUTSIDE_SCOPE for item in outside)
    assert _bytes_by_name(EXTRACTED) == before


def test_unsupported_variant_is_coverage_not_a_self_pair(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[:1] + MANAGEMENT_NAMES[:1], tmp_path / "var")
    payload = json.loads((dest / MANAGEMENT_NAMES[0]).read_text(encoding="utf-8"))
    payload["reported_kpis"][0]["metric_id"] = "digital_comparable_sales_growth"
    payload["reported_kpis"][0]["category"] = "comparable_sales"
    (dest / MANAGEMENT_NAMES[0]).write_text(json.dumps(payload), encoding="utf-8")
    admission = _admission(dest)
    variants = _coverage(admission, KIND_UNSUPPORTED_VARIANT)
    assert variants
    for item in variants:
        assert item["kind"] == KIND_UNSUPPORTED_VARIANT
        assert len(item["locators"]) == 1
        assert item["metric_identity"] == ""
        assessment = _assessment(admission, item["locators"][0])
        assert assessment["status"] == STATUS_UNSUPPORTED_VARIANT
        assert "presentation_relationship" not in item
    assert all(
        item["kind"] != KIND_PAIR or "digital_comparable_sales_growth" not in str(item)
        for item in admission["reconciliation"]["items"]
    )


def test_spsf_missing_comparison_pair_stays_unresolved(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "spsf-gap")
    left, right = _affirmative_family_pair(FAMILY_SALES_PER_SQUARE_FOOT)
    left = _apply_same_period(left, FAMILY_SALES_PER_SQUARE_FOOT, period=SHARED_PERIOD, value=10)
    right = _apply_same_period(
        right, FAMILY_SALES_PER_SQUARE_FOOT, period=SHARED_PERIOD, value=10
    )
    left = _mutate_metric(left, FAMILY_SALES_PER_SQUARE_FOOT, lambda item: item.__setitem__("comparison", ""))
    right = _mutate_metric(
        right, FAMILY_SALES_PER_SQUARE_FOOT, lambda item: item.__setitem__("comparison", "")
    )
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, FAMILY_SALES_PER_SQUARE_FOOT)
    pair = _pair_by_locators(_metric_pairs(payload, FAMILY_SALES_PER_SQUARE_FOOT), locators)
    assert pair["outcome"] == OUTCOME_UNRESOLVED
    assert REASON_MISSING_COMPARISON in pair["reasons"]
    assert peer_gap_reason(REASON_MISSING_COMPARISON) in pair["reasons"]
    assert "comparison_mismatch" not in pair["reasons"]
    for locator in locators:
        assert _assessment(payload, locator)["comparability"] == COMPARABILITY_UNRESOLVED


def test_incompatible_plus_gap_retains_both_reasons(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "both")

    def mutate(payload: dict) -> dict:
        payload = _set_reporting_basis(payload, REPORTING_BASIS_53)
        return _mutate_metric(
            payload,
            FAMILY_COMPARABLE_SALES_GROWTH,
            lambda item: item.pop("qualifiers", None),
        )

    _write_family_pair(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _set_reporting_basis(payload, REPORTING_BASIS_52),
        right_mutate=mutate,
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, FAMILY_COMPARABLE_SALES_GROWTH)
    pair = _pair_by_locators(
        _metric_pairs(payload, FAMILY_COMPARABLE_SALES_GROWTH), locators
    )
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    assert "calendar_reporting_mismatch" in pair["reasons"]
    assert REASON_CALENDAR_WEEK in pair["reasons"] or peer_gap_reason(
        REASON_CALENDAR_WEEK
    ) in pair["reasons"]
    for locator in locators:
        item = _assessment(payload, locator)
        assert item["comparability"] == COMPARABILITY_NOT_COMPARABLE
        assert "calendar_reporting_mismatch" in item["unresolved_reasons"]


def _attach_family_evidence(
    payload: dict,
    family: str,
    *,
    role: str | None = None,
    status: str | None = None,
) -> dict:
    from core.tests.test_management_kpi_admission import (
        _attach_assurance,
        _attach_presentation,
        _metric_items,
    )

    payload = copy.deepcopy(payload)
    metric_id = _family_metric_id(family)
    for item in _metric_items(payload, metric_id):
        if role is not None:
            _attach_presentation(item, role)
        if status is not None:
            _attach_assurance(item, status)
    return payload


@pytest.mark.parametrize("family", FAMILIES)
def test_pair_members_keep_occurrence_local_presentation_and_assurance(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "ev")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="current", status="audited"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="restated", status="unaudited"
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_affirmative_duplicate(pair, values=(10, 10))
    left, right = pair["occurrences"]
    roles = {left["presentation_evidence"]["role"], right["presentation_evidence"]["role"]}
    statuses = {
        left["assurance_evidence"]["status"],
        right["assurance_evidence"]["status"],
    }
    assert roles == {"current", "restated"}
    assert statuses == {"audited", "unaudited"}
    assert left["presentation_evidence"]["locator"] != right["presentation_evidence"]["locator"]
    assert left["assurance_evidence"]["locator"] != right["assurance_evidence"]["locator"]
    assert left["presentation_evidence"]["evidence"]
    assert right["assurance_evidence"]["source"]["physical_page_mapping"] == "unresolved"
    for locator in locators:
        assert _assessment(payload, locator)["comparability"] == COMPARABILITY_COMPARABLE
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination=presentation_role_combination("current", "restated"),
        roles={"current", "restated"},
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_presentation_evidence_does_not_change_pair_outcomes(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "nope")
    _write_family_pair(dest, family, left_value=10, right_value=11)
    baseline = _admission(dest)
    locators = _family_metric_locators(baseline, family)
    baseline_pair = _pair_by_locators(_metric_pairs(baseline, family), locators)
    assert baseline_pair["outcome"] == OUTCOME_CONFLICTING_CANDIDATE

    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=11,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="current", status="audited"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="prior", status="unaudited"
        ),
    )
    evidenced = _admission(dest)
    locators = _family_metric_locators(evidenced, family)
    pair = _pair_by_locators(_metric_pairs(evidenced, family), locators)
    assert pair["outcome"] == OUTCOME_CONFLICTING_CANDIDATE
    assert pair["reasons"] == baseline_pair["reasons"]
    assert pair["canonical_selection"] == "deferred"
    roles = {
        occ["presentation_evidence"]["role"] for occ in pair["occurrences"]
    }
    assert roles == {"current", "prior"}
    assert "prior" in roles
    periods = {occ["period"] for occ in pair["occurrences"]}
    assert periods == {SHARED_PERIOD}
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination=presentation_role_combination("current", "prior"),
        roles={"current", "prior"},
    )
    assert baseline_pair["presentation_relationship"]["status"] == RELATIONSHIP_UNRESOLVED
    assert baseline_pair["presentation_relationship"]["combination"] == "unknown_unknown"


@pytest.mark.parametrize("family", FAMILIES)
def test_three_peer_evidence_does_not_transfer(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "peer-ev")
    _write_three_peer(
        dest,
        family,
        values=(10, 10, 10),
        third_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="comparative", status="audited"
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pairs = _metric_pairs(payload, family)
    assert len(pairs) == 3
    assert {item["outcome"] for item in pairs} == {OUTCOME_AGREEING_DUPLICATE}
    evidenced = [
        item
        for item in payload["observations"]
        if item["locator"] in locators and item["presentation_role"] == "comparative"
    ]
    unknown = [
        item
        for item in payload["observations"]
        if item["locator"] in locators and item["presentation_role"] == "unknown"
    ]
    assert len(evidenced) == 1
    assert len(unknown) == 2
    assert all(item["assurance"] == "unknown" for item in unknown)
    assert evidenced[0]["assurance"] == "audited"
    for item in pairs:
        roles = {occ["presentation_evidence"]["role"] for occ in item["occurrences"]}
        if evidenced[0]["locator"] in item["locators"]:
            assert roles == {"comparative", "unknown"}
            _assert_relationship(
                item,
                status=RELATIONSHIP_UNRESOLVED,
                combination=presentation_role_combination("comparative", "unknown"),
                roles={"comparative", "unknown"},
            )
        else:
            assert roles == {"unknown"}
            _assert_relationship(
                item,
                status=RELATIONSHIP_UNRESOLVED,
                combination="unknown_unknown",
                roles={"unknown"},
            )


def test_supplied_pairs_keep_unknown_presentation_and_assurance():
    before = _bytes_by_name(EXTRACTED)
    payload = reconciliation_management_admission_payload(
        reconcile_filings(load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE))
    )
    recon = payload["reconciliation"]
    assert payload["assessments"]["comparability_counts"]["comparable"] == 0
    assert payload["assessments"]["comparability_counts"]["not_comparable"] == 22
    assert payload["assessments"]["comparability_counts"]["unresolved"] == 6
    assert payload["assessments"]["comparability_counts"]["outside_scope"] == 107
    assert recon["pair_count"] == 24
    assert recon["outcome_counts"][OUTCOME_INCOMPATIBLE] == 24
    assert recon["outcome_counts"][OUTCOME_AGREEING_DUPLICATE] == 0
    assert recon["outcome_counts"][OUTCOME_CONFLICTING_CANDIDATE] == 0
    for item in payload["observations"]:
        assert item["presentation_role"] == "unknown"
        assert item["assurance"] == "unknown"
        assert "assurance" in item["unresolved"]
        assert "presentation_role" in item["unresolved"]
        assert "revision" in item["unresolved"]
        assert item["revision_evidence"]["revises"] is None
    for item in recon["items"]:
        for occ in item["occurrences"]:
            assert occ["presentation_evidence"]["role"] == "unknown"
            assert occ["assurance_evidence"]["status"] == "unknown"
            assert occ["presentation_evidence"]["source"] is None
            assert occ["assurance_evidence"]["source"] is None
            assert occ["revision_evidence"]["revises"] is None
        if item["kind"] == KIND_PAIR:
            _assert_relationship(
                item,
                status=RELATIONSHIP_INCOMPATIBLE,
                combination="unknown_unknown",
                roles={"unknown"},
            )
            assert item["presentation_relationship"]["status"] != RELATIONSHIP_RECOGNIZED
        else:
            assert "presentation_relationship" not in item
    assert recon["revision_links"] == []
    assert recon["revision_link_counts"]["recognized"] == 0
    assert "presentation_role" in payload["unresolved"]
    assert "assurance" in payload["unresolved"]
    assert "revision" in payload["unresolved"]
    assert _bytes_by_name(EXTRACTED) == before


def test_renamed_inputs_preserve_local_evidence_locators(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "ren-src")
    _write_family_pair(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, FAMILY_COMPARABLE_SALES_GROWTH, role="current"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, FAMILY_COMPARABLE_SALES_GROWTH, role="comparative"
        ),
    )
    renamed = tmp_path / "renamed"
    renamed.mkdir()
    for index, name in enumerate(sorted(path.name for path in dest.glob("*.json"))):
        shutil.copy2(dest / name, renamed / f"{index:02d}-{name}")
    original = _admission(dest)
    renamed_payload = _admission(renamed)
    orig_pair = _metric_pairs(original, FAMILY_COMPARABLE_SALES_GROWTH)[0]
    renamed_pair = _metric_pairs(renamed_payload, FAMILY_COMPARABLE_SALES_GROWTH)[0]
    assert orig_pair["outcome"] == renamed_pair["outcome"] == OUTCOME_AGREEING_DUPLICATE
    orig_roles = sorted(
        occ["presentation_evidence"]["role"] for occ in orig_pair["occurrences"]
    )
    renamed_roles = sorted(
        occ["presentation_evidence"]["role"] for occ in renamed_pair["occurrences"]
    )
    assert orig_roles == renamed_roles == ["comparative", "current"]
    orig_locators = {occ["presentation_evidence"]["locator"] for occ in orig_pair["occurrences"]}
    renamed_locators = {
        occ["presentation_evidence"]["locator"] for occ in renamed_pair["occurrences"]
    }
    assert orig_locators.isdisjoint(renamed_locators)
    assert any("00-" in locator or "01-" in locator or "02-" in locator or "03-" in locator for locator in renamed_locators)
    _assert_relationship(
        orig_pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    _assert_relationship(
        renamed_pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )


def test_presentation_role_combination_table_covers_unordered_roles():
    expected = {}
    for index, left in enumerate(PRESENTATION_RELATIONSHIP_ROLES):
        for right in PRESENTATION_RELATIONSHIP_ROLES[index:]:
            ordered = (left, right)
            expected[ordered] = NAMED_PRESENTATION_COMBINATIONS.get(
                ordered, f"{left}_{right}"
            )
    assert PRESENTATION_ROLE_COMBINATIONS == expected
    assert len(PRESENTATION_ROLE_COMBINATIONS) == 15
    assert presentation_role_combination("comparative", "current") == "current_comparative"
    assert presentation_role_combination("prior", "restated") == "restated_prior"
    assert presentation_role_combination("unknown", "unknown") == "unknown_unknown"
    assert presentation_role_combination("current", "current") == "current_current"
    assert presentation_role_combination("restated", "current") == "current_restated"


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("left_role,right_role", _unordered_role_pairs())
def test_role_pair_matrix_is_evidence_grounded(
    tmp_path: Path, family: str, left_role: str, right_role: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "roles")
    left_mutate = (
        None
        if left_role == "unknown"
        else (lambda payload, role=left_role: _attach_family_evidence(payload, family, role=role))
    )
    right_mutate = (
        None
        if right_role == "unknown"
        else (
            lambda payload, role=right_role: _attach_family_evidence(payload, family, role=role)
        )
    )
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=left_mutate,
        right_mutate=right_mutate,
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    expected_status = (
        RELATIONSHIP_UNRESOLVED
        if left_role == "unknown" or right_role == "unknown"
        else RELATIONSHIP_RECOGNIZED
    )
    _assert_relationship(
        pair,
        status=expected_status,
        combination=presentation_role_combination(left_role, right_role),
        roles={left_role, right_role},
    )
    assert pair["outcome"] == OUTCOME_AGREEING_DUPLICATE
    swapped = tmp_path / "swapped"
    swapped.mkdir()
    for name in ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3]:
        shutil.copy2(dest / name, swapped / name)
    _write_family_pair(
        swapped,
        family,
        left_value=10,
        right_value=10,
        left_mutate=right_mutate,
        right_mutate=left_mutate,
    )
    reversed_payload = _admission(swapped)
    reversed_pair = _pair_by_locators(
        _metric_pairs(reversed_payload, family),
        _family_metric_locators(reversed_payload, family),
    )
    assert reversed_pair["presentation_relationship"]["combination"] == pair[
        "presentation_relationship"
    ]["combination"]
    assert reversed_pair["presentation_relationship"]["status"] == pair[
        "presentation_relationship"
    ]["status"]
    assert {member["role"] for member in reversed_pair["presentation_relationship"]["members"]} == {
        left_role,
        right_role,
    }


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(
    "left_role,right_role,combination",
    [
        ("current", "comparative", "current_comparative"),
        ("comparative", "current", "current_comparative"),
        ("restated", "prior", "restated_prior"),
        ("prior", "restated", "restated_prior"),
    ],
)
def test_named_role_combinations_are_explicit_and_unordered(
    tmp_path: Path,
    family: str,
    left_role: str,
    right_role: str,
    combination: str,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "named")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=11,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role=left_role
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role=right_role
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    assert pair["outcome"] == OUTCOME_CONFLICTING_CANDIDATE
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination=combination,
        roles={left_role, right_role},
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_missing_comparison_evidence_keeps_relationship_unresolved(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "gap")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="current"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            _set_reporting_basis(payload, None), family, role="comparative"
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    assert pair["outcome"] == OUTCOME_UNRESOLVED
    _assert_relationship(
        pair,
        status=RELATIONSHIP_UNRESOLVED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    assert REASON_CALENDAR_REPORTING in pair["presentation_relationship"][
        "reasons"
    ] or peer_gap_reason(REASON_CALENDAR_REPORTING) in pair["presentation_relationship"][
        "reasons"
    ]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("conflict", ["definition", "calendar", "period", "qualifier"])
def test_evidenced_dimension_conflicts_make_relationship_incompatible(
    tmp_path: Path, family: str, conflict: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / conflict)
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_right(payload: dict) -> dict:
        payload = _attach_family_evidence(payload, family, role="prior")
        if conflict == "definition":
            payload = copy.deepcopy(payload)
            payload["kpi_definitions"][
                0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
            ]["definition"] = changed
            return payload
        if conflict == "calendar":
            return _set_reporting_basis(payload, REPORTING_BASIS_53)
        if conflict == "period":
            payload = copy.deepcopy(payload)
            metric_id = _family_metric_id(family)
            for item in payload["reported_kpis"]:
                if item.get("metric_id") == metric_id:
                    item["period"] = "2023-01-29"
            return payload
        return _mutate_metric(
            payload,
            family,
            lambda item: item.__setitem__(
                "qualifiers",
                {"excludes_53rd_week": False, "channel_mix": "stores_and_digital"},
            ),
        )

    def mutate_left(payload: dict) -> dict:
        if conflict == "calendar":
            payload = _set_reporting_basis(payload, REPORTING_BASIS_52)
        elif conflict == "qualifier":
            payload = _mutate_metric(
                payload,
                family,
                lambda item: item.__setitem__(
                    "qualifiers",
                    {"excludes_53rd_week": False, "channel_mix": "stores_only"},
                ),
            )
        return _attach_family_evidence(payload, family, role="restated")

    left, right = _affirmative_family_pair(family)
    if conflict == "period":
        metric_id = _family_metric_id(family)
        for payload in (left, right):
            for item in payload["reported_kpis"]:
                if item.get("metric_id") == metric_id:
                    item["value"] = 10
        left = _attach_family_evidence(left, family, role="restated")
        right = mutate_right(right)
        _write_json(dest / MANAGEMENT_NAMES[1], left)
        _write_json(dest / MANAGEMENT_NAMES[2], right)
    else:
        _write_family_pair(
            dest,
            family,
            left_value=10,
            right_value=10,
            left_mutate=mutate_left,
            right_mutate=mutate_right,
        )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    _assert_relationship(
        pair,
        status=RELATIONSHIP_INCOMPATIBLE,
        combination="restated_prior",
        roles={"restated", "prior"},
    )
    expected_reason = {
        "definition": "definition_mismatch",
        "calendar": "calendar_reporting_mismatch",
        "period": REASON_PERIOD_MISMATCH,
        "qualifier": "qualifier_mismatch",
    }[conflict]
    assert expected_reason in pair["presentation_relationship"]["reasons"]
    assert "revises" not in pair["presentation_relationship"]


@pytest.mark.parametrize("family", FAMILIES)
def test_missing_and_equal_values_do_not_invent_relationships(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "vals")
    _write_family_pair(dest, family, left_value=10, right_value=10)
    equal = _admission(dest)
    locators = _family_metric_locators(equal, family)
    equal_pair = _pair_by_locators(_metric_pairs(equal, family), locators)
    assert equal_pair["outcome"] == OUTCOME_AGREEING_DUPLICATE
    _assert_relationship(
        equal_pair,
        status=RELATIONSHIP_UNRESOLVED,
        combination="unknown_unknown",
        roles={"unknown"},
    )

    _write_family_pair(
        dest,
        family,
        left_value=None,
        right_value=0,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="current"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="comparative"
        ),
    )
    missing = _admission(dest)
    locators = _family_metric_locators(missing, family)
    missing_pair = _pair_by_locators(_metric_pairs(missing, family), locators)
    assert missing_pair["outcome"] == OUTCOME_UNRESOLVED
    _assert_relationship(
        missing_pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    assert REASON_MISSING_VALUE not in missing_pair["presentation_relationship"]["reasons"]
    assert peer_gap_reason(REASON_MISSING_VALUE) not in missing_pair[
        "presentation_relationship"
    ]["reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_assurance_filenames_and_older_period_do_not_create_relationships(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "infer")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, status="audited"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, status="unaudited"
        ),
    )
    assured = _admission(dest)
    locators = _family_metric_locators(assured, family)
    pair = _pair_by_locators(_metric_pairs(assured, family), locators)
    statuses = {occ["assurance_evidence"]["status"] for occ in pair["occurrences"]}
    assert statuses == {"audited", "unaudited"}
    _assert_relationship(
        pair,
        status=RELATIONSHIP_UNRESOLVED,
        combination="unknown_unknown",
        roles={"unknown"},
    )

    left, right = _affirmative_family_pair(family)
    metric_id = _family_metric_id(family)
    for payload in (left, right):
        for item in payload["reported_kpis"]:
            if item.get("metric_id") == metric_id:
                item["value"] = 10
    left = _attach_family_evidence(left, family, role="current")
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    older = _admission(dest)
    locators = _family_metric_locators(older, family)
    older_pair = _pair_by_locators(_metric_pairs(older, family), locators)
    roles = {
        occ["presentation_evidence"]["role"] for occ in older_pair["occurrences"]
    }
    assert roles == {"current", "unknown"}
    assert "prior" not in roles
    assert "comparative" not in roles
    _assert_relationship(
        older_pair,
        status=RELATIONSHIP_INCOMPATIBLE,
        combination=presentation_role_combination("current", "unknown"),
        roles={"current", "unknown"},
    )
    assert REASON_PERIOD_MISMATCH in older_pair["presentation_relationship"]["reasons"]


def test_spsf_comparison_conflict_is_incompatible_relationship(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "spsf-cmp")
    _write_family_pair(
        dest,
        FAMILY_SALES_PER_SQUARE_FOOT,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, FAMILY_SALES_PER_SQUARE_FOOT, role="current"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            _mutate_metric(
                payload,
                FAMILY_SALES_PER_SQUARE_FOOT,
                lambda item: item.__setitem__("comparison", "year_over_year"),
            ),
            FAMILY_SALES_PER_SQUARE_FOOT,
            role="comparative",
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, FAMILY_SALES_PER_SQUARE_FOOT)
    pair = _pair_by_locators(
        _metric_pairs(payload, FAMILY_SALES_PER_SQUARE_FOOT), locators
    )
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE
    _assert_relationship(
        pair,
        status=RELATIONSHIP_INCOMPATIBLE,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    assert "comparison_mismatch" in pair["presentation_relationship"]["reasons"]


def test_unit_basis_and_scope_conflicts_do_not_acquire_pair_relationships(
    tmp_path: Path,
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "dims")
    fy2023, fy2024 = _affirmative_family_pair(FAMILY_COMPARABLE_SALES_GROWTH)
    fy2023 = _apply_same_period(
        fy2023, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    fy2024 = _apply_same_period(
        fy2024, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    cases = {
        "unit": lambda item: item.__setitem__("unit", "USD"),
        "basis": lambda item: item.__setitem__("basis", "constant_dollar"),
        "scope": lambda item: item.__setitem__("scope", {"geography": "Americas"}),
    }
    for kind, mutate in cases.items():
        left = copy.deepcopy(fy2023)
        right = _mutate_metric(copy.deepcopy(fy2024), FAMILY_COMPARABLE_SALES_GROWTH, mutate)
        _write_json(dest / MANAGEMENT_NAMES[1], left)
        _write_json(dest / MANAGEMENT_NAMES[2], right)
        payload = _admission(dest)
        mutated = next(
            item
            for item in payload["assessments"]["items"]
            if item["status"] == STATUS_UNSUPPORTED_VARIANT
        )
        coverage = [
            item
            for item in payload["reconciliation"]["items"]
            if mutated["locator"] in item["locators"]
        ]
        assert coverage
        assert all(item["kind"] != KIND_PAIR for item in coverage)
        assert all("presentation_relationship" not in item for item in coverage)
        assert kind in {"unit", "basis", "scope"}


def test_same_document_repeated_occurrences_keep_local_relationships(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:2] + MANAGEMENT_NAMES[1:2], tmp_path / "repeat")
    payload = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    from core.tests.test_management_kpi_identity import _apply_affirmative_compsales
    from core.tests.test_management_kpi_admission import _attach_presentation

    payload = _apply_affirmative_compsales(payload)
    original = next(
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") == "comparable_sales_growth"
    )
    original["period"] = SHARED_PERIOD
    original["value"] = 10
    duplicate = copy.deepcopy(original)
    _attach_presentation(original, "current")
    _attach_presentation(duplicate, "comparative")
    payload["reported_kpis"].append(duplicate)
    _write_json(dest / MANAGEMENT_NAMES[1], payload)
    admitted = _admission(dest)
    locators = _family_metric_locators(admitted, FAMILY_COMPARABLE_SALES_GROWTH)
    assert len(locators) == 2
    pair = _pair_by_locators(
        _metric_pairs(admitted, FAMILY_COMPARABLE_SALES_GROWTH), locators
    )
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    sources = {occ["bound_source_file"] for occ in pair["occurrences"]}
    assert len(sources) == 1


def test_cli_serializes_recognized_and_unknown_relationships(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli")
    _write_family_pair(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, FAMILY_COMPARABLE_SALES_GROWTH, role="current", status="audited"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, FAMILY_COMPARABLE_SALES_GROWTH, role="comparative", status="unaudited"
        ),
    )
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
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    matches = [
        item
        for item in _metric_pairs(admission, FAMILY_COMPARABLE_SALES_GROWTH)
        if {occ["presentation_evidence"]["role"] for occ in item["occurrences"]}
        == {"current", "comparative"}
    ]
    assert len(matches) == 1
    pair = matches[0]
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="current_comparative",
        roles={"current", "comparative"},
    )
    statuses = {occ["assurance_evidence"]["status"] for occ in pair["occurrences"]}
    assert statuses == {"audited", "unaudited"}
    for occ in pair["occurrences"]:
        assert occ["presentation_evidence"]["source"]["physical_page_mapping"] == (
            "unresolved"
        )
    for item in admission["reconciliation"]["items"]:
        if item["kind"] == KIND_PAIR:
            assert "presentation_relationship" in item
        else:
            assert "presentation_relationship" not in item


def _family_items(payload: dict, family: str) -> list[dict]:
    from core.tests.test_management_kpi_admission import _metric_items

    return _metric_items(payload, _family_metric_id(family))


def _attach_family_revision(
    reviser_payload: dict,
    target_payload: dict,
    family: str,
    **target_overrides: str,
) -> dict:
    from core.tests.test_management_kpi_admission import (
        _attach_revision,
        _revision_target,
    )

    reviser_payload = copy.deepcopy(reviser_payload)
    target_item = _family_items(target_payload, family)[0]
    for item in _family_items(reviser_payload, family):
        _attach_revision(
            item,
            _revision_target(
                target_item,
                target_payload["report"]["source_file"],
                **target_overrides,
            ),
            source_file=reviser_payload["report"]["source_file"],
        )
    return reviser_payload


def _write_revised_family_pair(
    dest: Path,
    family: str,
    *,
    left_value: object | None = 10,
    right_value: object | None = 10,
    left_mutate=None,
    right_mutate=None,
    reviser: str = "right",
) -> tuple[dict, dict]:
    left, right = _affirmative_family_pair(family)
    left = _apply_same_period(left, family, period=SHARED_PERIOD, value=left_value)
    right = _apply_same_period(right, family, period=SHARED_PERIOD, value=right_value)
    if left_mutate is not None:
        left = left_mutate(left)
    if right_mutate is not None:
        right = right_mutate(right)
    if reviser in {"right", "both"}:
        right = _attach_family_revision(right, left, family)
    if reviser in {"left", "both"}:
        left = _attach_family_revision(left, right, family)
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    return left, right


def _set_family_revision_evidence(payload: dict, family: str, blank: object) -> dict:
    payload = copy.deepcopy(payload)
    for item in _family_items(payload, family):
        revision = item.get("revision")
        if not isinstance(revision, dict):
            continue
        if blank is Ellipsis:
            revision.pop("evidence", None)
        else:
            revision["evidence"] = blank
    return payload


def _assert_revision_link(
    payload: dict,
    *,
    status: str,
    reviser_year: int,
    revised_year: int,
    family: str,
    require_evidence: bool = True,
) -> dict:
    links = payload["reconciliation"]["revision_links"]
    assert links
    metric_id = _family_metric_id(family)
    observations = {
        item["locator"]: item
        for item in payload["observations"]
        if item["kind"] == "reported_kpi" and item["metric_id"] == metric_id
    }
    matches = []
    for link in links:
        reviser = observations[link["reviser"]["locator"]]
        revised = (
            None
            if link["revised"] is None
            else observations.get(link["revised"]["locator"])
        )
        if (
            reviser["filing_year"] == reviser_year
            and revised is not None
            and revised["filing_year"] == revised_year
        ):
            matches.append(link)
    assert len(matches) == 1
    link = matches[0]
    assert link["kind"] == "revision_link"
    assert link["status"] == status
    assert link["canonical_selection"] == "deferred"
    if require_evidence:
        assert link["evidence"]
    assert link["source"]["physical_page_mapping"] == "unresolved"
    assert link["named_target"]["source_file"].endswith(".pdf")
    assert "value" not in link["named_target"]
    assert "preferred" not in link
    assert "winner" not in link
    assert "superseded" not in link
    reviser = observations[link["reviser"]["locator"]]
    revised = observations[link["revised"]["locator"]]
    assert link["reviser"]["occurrence_identity"] == reviser["identity"]
    assert link["revised"]["occurrence_identity"] == revised["identity"]
    assert link["named_target"]["metric_id"] == metric_id
    assert link["named_target"]["period"] == revised["period"]
    assert link["named_target"]["page_reference"] == revised["source"]["page_reference"]
    return link


def _write_audited_revised_family_pair(
    dest: Path,
    family: str,
    *,
    left_value: object | None = 10,
    right_value: object | None = 10,
    left_mutate=None,
    right_mutate=None,
    reviser: str = "right",
) -> tuple[dict, dict]:
    def compose(mutate, audit: bool):
        def inner(payload: dict) -> dict:
            if mutate is not None:
                payload = mutate(payload)
            if audit:
                payload = _attach_family_evidence(payload, family, status="audited")
            return payload

        return inner

    return _write_revised_family_pair(
        dest,
        family,
        left_value=left_value,
        right_value=right_value,
        left_mutate=compose(left_mutate, reviser in {"left", "both"}),
        right_mutate=compose(right_mutate, reviser in {"right", "both"}),
        reviser=reviser,
    )


def _group_selections(payload: dict) -> list[dict]:
    return list(payload["reconciliation"]["group_selections"])


def _family_period_group(
    payload: dict, family: str, *, period: str = SHARED_PERIOD
) -> dict:
    metric_id = _family_metric_id(family)
    locators = {
        item["locator"]
        for item in payload["observations"]
        if item["kind"] == "reported_kpi"
        and item["metric_id"] == metric_id
        and item["period"] == period
        and _assessment(payload, item["locator"])["status"] == STATUS_SUPPORTED
    }
    matches = [
        item for item in _group_selections(payload) if set(item["locators"]) == locators
    ]
    assert locators
    assert len(matches) == 1
    return matches[0]


def _assert_selected_group(group: dict, *, reviser_locator: str, superseded_locator: str) -> None:
    assert group["kind"] == "group_selection"
    assert group["status"] == SELECTION_SELECTED
    assert "canonical_selection" not in group
    assert group["reasons"] == []
    assert group["selected"]["locator"] == reviser_locator
    assert group["superseded"]["locator"] == superseded_locator
    assert group["selected"]["locator"] != group["superseded"]["locator"]
    assert group["revision"]["reviser"]["locator"] == reviser_locator
    assert group["revision"]["revised"]["locator"] == superseded_locator
    assert group["revision"]["evidence"]
    assert "canonical_selection" not in group["revision"]
    assert group["assurance_evidence"]["status"] == "audited"
    assert group["assurance_evidence"]["evidence"]
    assert group["assurance_evidence"]["locator"]
    assert group["assurance_evidence"]["source"]["page_reference"]
    by_locator = {occ["locator"]: occ for occ in group["occurrences"]}
    assert reviser_locator in by_locator
    assert superseded_locator in by_locator
    superseded = by_locator[superseded_locator]
    reviser = by_locator[reviser_locator]
    assert superseded["source"]["page_reference"]
    assert superseded["bound_source_file"].endswith(".pdf")
    assert superseded["definition"]["text"]
    assert reviser["value"] is not None
    assert reviser["assurance_evidence"]["status"] == "audited"


def _assert_deferred_group(group: dict, *needles: str) -> None:
    assert group["kind"] == "group_selection"
    assert group["status"] == SELECTION_DEFERRED
    assert group["selected"] is None
    assert group["superseded"] is None
    assert group["revision"] is None
    assert group["assurance_evidence"] is None
    assert "canonical_selection" not in group
    assert group["reasons"]
    for needle in needles:
        assert needle in group["reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_explicit_revision_links_are_directed_and_gated(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "rev")
    _write_revised_family_pair(dest, family)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_affirmative_duplicate(pair, values=(10, 10))
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    assert payload["reconciliation"]["revision_link_counts"]["recognized"] == 1
    assert link["reviser"]["locator"] != link["revised"]["locator"]
    roles = {occ["presentation_evidence"]["role"] for occ in pair["occurrences"]}
    assert roles == {"unknown"}
    assert pair["canonical_selection"] == "deferred"


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("blank", [Ellipsis, None, "", " ", " \t "])
def test_named_target_blank_evidence_keeps_bound_revision_unresolved(
    tmp_path: Path, family: str, blank: object
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "blank")
    _left, right = _write_revised_family_pair(dest, family)
    recognized = _admission(dest)
    _assert_revision_link(
        recognized,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    right = _set_family_revision_evidence(right, family, blank)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_affirmative_duplicate(pair, values=(10, 10))
    expected_evidence = "" if blank in {Ellipsis, None} else blank
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_UNRESOLVED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
        require_evidence=False,
    )
    assert link["evidence"] == expected_evidence
    assert REASON_MISSING_EVIDENCE in link["reasons"]
    assert payload["reconciliation"]["revision_link_counts"]["recognized"] == 0
    assert all(
        item["status"] != RELATIONSHIP_RECOGNIZED
        for item in payload["reconciliation"]["revision_links"]
    )
    reviser = next(
        item
        for item in payload["observations"]
        if item["locator"] == link["reviser"]["locator"]
    )
    assert reviser["revision_evidence"]["revises"] == link["named_target"]
    assert reviser["revision_evidence"]["source"]["page_reference"]
    assert "revision" in reviser["unresolved"]


@pytest.mark.parametrize("family", FAMILIES)
def test_blank_evidence_retains_comparison_failures_without_recognizing(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "gap")
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_right(payload: dict) -> dict:
        payload = copy.deepcopy(payload)
        payload["kpi_definitions"][
            0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
        ]["definition"] = changed
        return payload

    _left, right = _write_revised_family_pair(
        dest, family, right_mutate=mutate_right
    )
    right = _set_family_revision_evidence(right, family, "")
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_UNRESOLVED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
        require_evidence=False,
    )
    assert link["evidence"] == ""
    assert "definition_mismatch" in link["reasons"]
    assert REASON_MISSING_EVIDENCE in link["reasons"]
    assert payload["reconciliation"]["revision_link_counts"].get("recognized", 0) == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_restated_roles_and_equal_values_do_not_invent_revision_links(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "roles")
    _write_family_pair(
        dest,
        family,
        left_value=10,
        right_value=10,
        left_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="prior", status="audited"
        ),
        right_mutate=lambda payload: _attach_family_evidence(
            payload, family, role="restated", status="unaudited"
        ),
    )
    payload = _admission(dest)
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    _assert_relationship(
        pair,
        status=RELATIONSHIP_RECOGNIZED,
        combination="restated_prior",
        roles={"restated", "prior"},
    )
    assert payload["reconciliation"]["revision_links"] == []
    years = {
        item["filing_year"]
        for item in payload["observations"]
        if item["locator"] in locators
    }
    assert years == {2023, 2024}


@pytest.mark.parametrize("family", FAMILIES)
def test_revision_direction_survives_reordering_and_renaming(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "dir")
    _write_revised_family_pair(dest, family, reviser="right")
    original = _admission(dest)
    original_link = _assert_revision_link(
        original,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )

    swapped = tmp_path / "swapped"
    swapped.mkdir()
    for name in ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3]:
        shutil.copy2(dest / name, swapped / name)
    _write_revised_family_pair(swapped, family, reviser="left")
    reversed_payload = _admission(swapped)
    reversed_link = _assert_revision_link(
        reversed_payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2023,
        revised_year=2024,
        family=family,
    )
    assert (
        reversed_link["named_target"]["source_file"]
        != original_link["named_target"]["source_file"]
    )

    renamed = tmp_path / "renamed"
    renamed.mkdir()
    for index, name in enumerate(sorted(path.name for path in dest.glob("*.json"))):
        shutil.copy2(dest / name, renamed / f"{index:02d}-{name}")
    renamed_payload = _admission(renamed)
    renamed_link = _assert_revision_link(
        renamed_payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    assert renamed_link["named_target"] == original_link["named_target"]
    assert renamed_link["reviser"]["locator"] != original_link["reviser"]["locator"]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("conflict", ["definition", "calendar", "period", "qualifier"])
def test_revision_links_use_existing_comparison_gates(
    tmp_path: Path, family: str, conflict: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / conflict)
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_left(payload: dict) -> dict:
        if conflict == "calendar":
            return _set_reporting_basis(payload, REPORTING_BASIS_52)
        if conflict == "qualifier":
            return _mutate_metric(
                payload,
                family,
                lambda item: item.__setitem__(
                    "qualifiers",
                    {"excludes_53rd_week": False, "channel_mix": "stores_only"},
                ),
            )
        return payload

    def mutate_right(payload: dict) -> dict:
        if conflict == "definition":
            payload = copy.deepcopy(payload)
            payload["kpi_definitions"][
                0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
            ]["definition"] = changed
            return payload
        if conflict == "calendar":
            return _set_reporting_basis(payload, REPORTING_BASIS_53)
        if conflict == "period":
            payload = copy.deepcopy(payload)
            metric_id = _family_metric_id(family)
            for item in payload["reported_kpis"]:
                if item.get("metric_id") == metric_id:
                    item["period"] = "2023-01-29"
            return payload
        return _mutate_metric(
            payload,
            family,
            lambda item: item.__setitem__(
                "qualifiers",
                {"excludes_53rd_week": False, "channel_mix": "stores_and_digital"},
            ),
        )

    if conflict == "period":
        left, right = _affirmative_family_pair(family)
        metric_id = _family_metric_id(family)
        for payload in (left, right):
            for item in payload["reported_kpis"]:
                if item.get("metric_id") == metric_id:
                    item["value"] = 10
        right = mutate_right(right)
        right = _attach_family_revision(right, left, family)
        _write_json(dest / MANAGEMENT_NAMES[1], left)
        _write_json(dest / MANAGEMENT_NAMES[2], right)
    else:
        _write_revised_family_pair(
            dest,
            family,
            left_mutate=mutate_left,
            right_mutate=mutate_right,
        )
    payload = _admission(dest)
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_INCOMPATIBLE,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    expected = {
        "definition": "definition_mismatch",
        "calendar": "calendar_reporting_mismatch",
        "period": REASON_PERIOD_MISMATCH,
        "qualifier": "qualifier_mismatch",
    }[conflict]
    assert expected in link["reasons"]
    locators = _family_metric_locators(payload, family)
    pair = _pair_by_locators(_metric_pairs(payload, family), locators)
    assert pair["outcome"] == OUTCOME_INCOMPATIBLE


@pytest.mark.parametrize("family", FAMILIES)
def test_missing_comparison_evidence_keeps_revision_unresolved(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "gap")
    _write_revised_family_pair(
        dest,
        family,
        right_mutate=lambda payload: _set_reporting_basis(payload, None),
    )
    payload = _admission(dest)
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_UNRESOLVED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    assert REASON_CALENDAR_REPORTING in link["reasons"] or peer_gap_reason(
        REASON_CALENDAR_REPORTING
    ) in link["reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_agreeing_conflicting_and_missing_values_do_not_create_revision_links(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "vals")
    _write_family_pair(dest, family, left_value=10, right_value=11)
    conflicted = _admission(dest)
    assert conflicted["reconciliation"]["revision_links"] == []
    _write_revised_family_pair(dest, family, left_value=None, right_value=0)
    missing = _admission(dest)
    link = _assert_revision_link(
        missing,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    locators = _family_metric_locators(missing, family)
    pair = _pair_by_locators(_metric_pairs(missing, family), locators)
    assert pair["outcome"] == OUTCOME_UNRESOLVED
    assert REASON_MISSING_VALUE not in link["reasons"]


@pytest.mark.parametrize("family", FAMILIES)
def test_three_peer_revision_is_not_transitive(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three")
    first, second = _affirmative_family_pair(family)
    third = json.loads((EXTRACTED / MANAGEMENT_NAMES[3]).read_text(encoding="utf-8"))
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        from core.tests.test_management_kpi_identity import _apply_affirmative_compsales

        third = _apply_affirmative_compsales(third)
    else:
        from core.tests.test_management_kpi_identity import _apply_affirmative_spsf

        third = _apply_affirmative_spsf(third)
    payloads = [
        _apply_same_period(first, family, period=SHARED_PERIOD, value=10),
        _apply_same_period(second, family, period=SHARED_PERIOD, value=10),
        _apply_same_period(third, family, period=SHARED_PERIOD, value=10),
    ]
    payloads[1] = _attach_family_revision(payloads[1], payloads[0], family)
    for name, payload in zip(MANAGEMENT_NAMES[1:4], payloads):
        _write_json(dest / name, payload)
    admitted = _admission(dest)
    links = admitted["reconciliation"]["revision_links"]
    assert len(links) == 1
    assert links[0]["status"] == RELATIONSHIP_RECOGNIZED
    locators = _family_metric_locators(admitted, family)
    assert len(locators) == 3
    third_locator = [
        item["locator"]
        for item in admitted["observations"]
        if item["locator"] in locators and item["filing_year"] == 2025
    ][0]
    assert third_locator not in {
        links[0]["reviser"]["locator"],
        links[0]["revised"]["locator"],
    }


@pytest.mark.parametrize("family", FAMILIES)
def test_reciprocal_and_cyclic_revisions_are_diagnosed_without_precedence(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "recip")
    _write_revised_family_pair(dest, family, reviser="both")
    reciprocal = _admission(dest)
    links = reciprocal["reconciliation"]["revision_links"]
    assert len(links) == 2
    assert {link["status"] for link in links} == {RELATIONSHIP_RECOGNIZED}
    for link in links:
        assert REASON_RECIPROCAL in link["reasons"]
        assert "preferred" not in link
        assert "winner" not in link
        assert "superseded" not in link

    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "cycle")
    first, second = _affirmative_family_pair(family)
    third = json.loads((EXTRACTED / MANAGEMENT_NAMES[3]).read_text(encoding="utf-8"))
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        from core.tests.test_management_kpi_identity import _apply_affirmative_compsales

        third = _apply_affirmative_compsales(third)
    else:
        from core.tests.test_management_kpi_identity import _apply_affirmative_spsf

        third = _apply_affirmative_spsf(third)
    payloads = [
        _apply_same_period(first, family, period=SHARED_PERIOD, value=10),
        _apply_same_period(second, family, period=SHARED_PERIOD, value=10),
        _apply_same_period(third, family, period=SHARED_PERIOD, value=10),
    ]
    payloads[1] = _attach_family_revision(payloads[1], payloads[0], family)
    payloads[2] = _attach_family_revision(payloads[2], payloads[1], family)
    payloads[0] = _attach_family_revision(payloads[0], payloads[2], family)
    for name, payload in zip(MANAGEMENT_NAMES[1:4], payloads):
        _write_json(dest / name, payload)
    cyclic = _admission(dest)
    links = cyclic["reconciliation"]["revision_links"]
    assert len(links) == 3
    assert {link["status"] for link in links} == {RELATIONSHIP_RECOGNIZED}
    for link in links:
        assert REASON_CYCLIC in link["reasons"]
        assert "preferred" not in link
        assert "superseded" not in link


def test_outside_scope_and_json_filename_targets_stay_unresolved(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "out")
    left, right = _affirmative_family_pair(FAMILY_COMPARABLE_SALES_GROWTH)
    left = _apply_same_period(
        left, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    right = _apply_same_period(
        right, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    target = next(
        item for item in left["reported_kpis"] if item.get("metric_id") == "net_revenue"
    )
    from core.tests.test_management_kpi_admission import (
        _attach_revision,
        _revision_target,
    )

    for item in _family_items(right, FAMILY_COMPARABLE_SALES_GROWTH):
        _attach_revision(
            item,
            _revision_target(target, left["report"]["source_file"]),
            source_file=right["report"]["source_file"],
        )
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    outside = _admission(dest)
    links = outside["reconciliation"]["revision_links"]
    assert len(links) == 1
    assert links[0]["status"] == RELATIONSHIP_UNRESOLVED
    assert REASON_OUTSIDE_SCOPE_TARGET in links[0]["reasons"]
    assert links[0]["revised"] is not None

    for item in _family_items(right, FAMILY_COMPARABLE_SALES_GROWTH):
        _attach_revision(
            item,
            _revision_target(
                _family_items(left, FAMILY_COMPARABLE_SALES_GROWTH)[0],
                MANAGEMENT_NAMES[1],
            ),
            source_file=right["report"]["source_file"],
        )
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    named_json = _admission(dest)
    links = named_json["reconciliation"]["revision_links"]
    assert len(links) == 1
    assert links[0]["revised"] is None
    assert REASON_MISSING_TARGET in links[0]["reasons"]
    assert links[0]["named_target"]["source_file"] == MANAGEMENT_NAMES[1]


def test_cli_serializes_directed_revision_links(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli")
    _write_revised_family_pair(dest, FAMILY_COMPARABLE_SALES_GROWTH)
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
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    link = _assert_revision_link(
        admission,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=FAMILY_COMPARABLE_SALES_GROWTH,
    )
    assert admission["status"] == "admitted_unreconciled"
    assert admission["reconciliation"]["canonical_selection"] == "deferred"
    assert "superseded" not in link
    pair = [
        item
        for item in _metric_pairs(admission, FAMILY_COMPARABLE_SALES_GROWTH)
        if {occ["period"] for occ in item["occurrences"]} == {SHARED_PERIOD}
    ]
    assert pair
    assert pair[0]["outcome"] == OUTCOME_AGREEING_DUPLICATE


def _cli_validate_and_reconcile(dest: Path, out: Path):
    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "core",
            "validate-source",
            str(dest),
            "--source-root",
            str(SOURCE),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    reconcile = subprocess.run(
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
    return validate, reconcile


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("blank", [Ellipsis, None, "", " ", " \t "])
def test_cli_serializes_named_target_blank_evidence_as_unresolved(
    tmp_path: Path, family: str, blank: object
):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli-blank")
    _left, right = _write_revised_family_pair(dest, family)
    right = _set_family_revision_evidence(right, family, blank)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    out = tmp_path / "out"
    validate, reconcile = _cli_validate_and_reconcile(dest, out)
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert reconcile.returncode == 0, reconcile.stdout + reconcile.stderr
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    expected_evidence = "" if blank in {Ellipsis, None} else blank
    link = _assert_revision_link(
        admission,
        status=RELATIONSHIP_UNRESOLVED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
        require_evidence=False,
    )
    assert link["evidence"] == expected_evidence
    assert REASON_MISSING_EVIDENCE in link["reasons"]
    assert admission["reconciliation"]["revision_link_counts"]["recognized"] == 0
    assert admission["status"] == "admitted_unreconciled"


def _selected_locators(payload: dict, family: str) -> tuple[str, str, dict]:
    link = _assert_revision_link(
        payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    return link["reviser"]["locator"], link["revised"]["locator"], link


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(
    ("left_value", "right_value"),
    [(10, 10), (10, 11), (None, 10), (10, 0)],
)
def test_audited_reviser_is_selected_and_original_survives(
    tmp_path: Path, family: str, left_value: object, right_value: object
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "sel")
    _write_audited_revised_family_pair(
        dest, family, left_value=left_value, right_value=right_value
    )
    payload = _admission(dest)
    assert payload["status"] == "admitted_unreconciled"
    assert payload["canonical_selection"] == "deferred"
    assert payload["reconciliation"]["canonical_selection"] == "deferred"
    reviser, superseded, link = _selected_locators(payload, family)
    group = _family_period_group(payload, family)
    _assert_selected_group(group, reviser_locator=reviser, superseded_locator=superseded)
    by_locator = {occ["locator"]: occ for occ in group["occurrences"]}
    assert by_locator[reviser]["value"] == right_value
    assert by_locator[superseded]["value"] == left_value
    assert payload["reconciliation"]["selected_count"] >= 1
    assert payload["reconciliation"]["superseded_count"] >= 1
    pair = _pair_by_locators(_metric_pairs(payload, family), group["locators"])
    assert pair["canonical_selection"] == "deferred"
    assert "selected" not in pair
    assert "superseded" not in pair
    if left_value is None:
        assert pair["outcome"] == OUTCOME_UNRESOLVED
    elif left_value == right_value:
        assert pair["outcome"] == OUTCOME_AGREEING_DUPLICATE
    else:
        assert pair["outcome"] == OUTCOME_CONFLICTING_CANDIDATE
    assert link["canonical_selection"] == "deferred"
    assert "superseded" not in link


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("status", [None, "unknown", "unaudited"])
def test_unknown_or_unaudited_reviser_defers_selection(
    tmp_path: Path, family: str, status: str | None
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "asr")
    if status is None:
        _write_revised_family_pair(dest, family)
        expected = REASON_UNKNOWN_ASSURANCE
    else:
        _write_revised_family_pair(
            dest,
            family,
            right_mutate=lambda payload: _attach_family_evidence(
                payload, family, status=status
            ),
        )
        expected = (
            REASON_UNAUDITED_REVISER if status == "unaudited" else REASON_UNKNOWN_ASSURANCE
        )
    payload = _admission(dest)
    assert payload["status"] == "admitted_unreconciled"
    _assert_revision_link(
        payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2024,
        revised_year=2023,
        family=family,
    )
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, expected)
    assert payload["reconciliation"]["selected_count"] == 0
    assert payload["reconciliation"]["superseded_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("blank", [Ellipsis, None, "", " ", " \t "])
def test_blank_revision_evidence_defers_selection_without_rejecting(
    tmp_path: Path, family: str, blank: object
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "blank-sel")
    _left, right = _write_audited_revised_family_pair(dest, family)
    right = _set_family_revision_evidence(right, family, blank)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    assert payload["status"] == "admitted_unreconciled"
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, REASON_MISSING_EVIDENCE, REASON_MISSING_REVISION_LINK)
    assert payload["reconciliation"]["selected_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_missing_reviser_value_defers_selection(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "miss")
    _write_audited_revised_family_pair(dest, family, left_value=10, right_value=None)
    payload = _admission(dest)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, REASON_MISSING_REVISER_VALUE)
    assert payload["reconciliation"]["selected_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_incompatible_revision_defers_selection(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "inc")
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_right(payload: dict) -> dict:
        payload = copy.deepcopy(payload)
        payload["kpi_definitions"][
            0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
        ]["definition"] = changed
        return payload

    _write_audited_revised_family_pair(dest, family, right_mutate=mutate_right)
    payload = _admission(dest)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, "definition_mismatch", REASON_MISSING_REVISION_LINK)
    assert payload["reconciliation"]["selected_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_third_peer_prevents_subset_selection(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three-sel")
    _write_three_peer(dest, family, values=(10, 10, None))
    first = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    second = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    second = _attach_family_revision(second, first, family)
    second = _attach_family_evidence(second, family, status="audited")
    _write_json(dest / MANAGEMENT_NAMES[2], second)
    payload = _admission(dest)
    group = _family_period_group(payload, family)
    assert len(group["occurrences"]) == 3
    _assert_deferred_group(group, REASON_GROUP_LARGER_THAN_TWO)
    assert payload["reconciliation"]["selected_count"] == 0
    assert {occ["value"] for occ in group["occurrences"]} == {10, None}


@pytest.mark.parametrize("family", FAMILIES)
def test_incompatible_third_peer_is_not_filtered_away(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "three-inc")
    changed = AFFIRMATIVE_COMPSALES_DEFINITION + " changed"
    if family == FAMILY_SALES_PER_SQUARE_FOOT:
        changed = AFFIRMATIVE_SPSF_DEFINITION + " changed"

    def mutate_third(payload: dict) -> dict:
        payload = copy.deepcopy(payload)
        payload["kpi_definitions"][
            0 if family == FAMILY_COMPARABLE_SALES_GROWTH else 1
        ]["definition"] = changed
        return payload

    _write_three_peer(dest, family, values=(10, 11, 12), third_mutate=mutate_third)
    first = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    second = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    second = _attach_family_revision(second, first, family)
    second = _attach_family_evidence(second, family, status="audited")
    _write_json(dest / MANAGEMENT_NAMES[2], second)
    payload = _admission(dest)
    group = _family_period_group(payload, family)
    assert len(group["occurrences"]) == 3
    _assert_deferred_group(group, REASON_GROUP_LARGER_THAN_TWO)
    assert payload["reconciliation"]["selected_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_reciprocal_revision_defers_competing_selection(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "recip-sel")
    _write_audited_revised_family_pair(dest, family, reviser="both")
    payload = _admission(dest)
    group = _family_period_group(payload, family)
    _assert_deferred_group(group, REASON_RECIPROCAL, REASON_COMPETING_DIRECTION)
    assert payload["reconciliation"]["selected_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_independent_groups_do_not_lend_selection(tmp_path: Path, family: str):
    other = (
        FAMILY_SALES_PER_SQUARE_FOOT
        if family == FAMILY_COMPARABLE_SALES_GROWTH
        else FAMILY_COMPARABLE_SALES_GROWTH
    )
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "indep")
    left, right = _write_audited_revised_family_pair(dest, family)
    from core.tests.test_management_kpi_identity import (
        _apply_affirmative_compsales,
        _apply_affirmative_spsf,
    )

    apply_other = (
        _apply_affirmative_spsf
        if other == FAMILY_SALES_PER_SQUARE_FOOT
        else _apply_affirmative_compsales
    )
    left = apply_other(json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8")))
    right = apply_other(json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8")))
    left = _apply_same_period(left, other, period=SHARED_PERIOD, value=20)
    right = _apply_same_period(right, other, period=SHARED_PERIOD, value=21)
    left = _apply_same_period(left, family, period=SHARED_PERIOD, value=10)
    right = _apply_same_period(right, family, period=SHARED_PERIOD, value=10)
    right = _attach_family_revision(right, left, family)
    right = _attach_family_evidence(right, family, status="audited")
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    selected = _family_period_group(payload, family)
    deferred = _family_period_group(payload, other)
    reviser, superseded, _link = _selected_locators(payload, family)
    _assert_selected_group(
        selected, reviser_locator=reviser, superseded_locator=superseded
    )
    _assert_deferred_group(deferred, REASON_MISSING_REVISION_LINK)
    other_locators = set(deferred["locators"])
    assert reviser not in other_locators
    assert superseded not in other_locators


def test_geographic_variant_is_an_independent_group(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "geo")
    _write_audited_revised_family_pair(dest, FAMILY_COMPARABLE_SALES_GROWTH)
    left = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    right = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    for payload, value in ((left, 8), (right, 9)):
        for item in payload["reported_kpis"]:
            if item.get("metric_id") == "americas_comparable_sales_growth":
                item["period"] = SHARED_PERIOD
                item["value"] = value
                item["qualifiers"] = {"excludes_53rd_week": False}
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    admitted = _admission(dest)
    global_group = _family_period_group(admitted, FAMILY_COMPARABLE_SALES_GROWTH)
    reviser, superseded, _link = _selected_locators(
        admitted, FAMILY_COMPARABLE_SALES_GROWTH
    )
    _assert_selected_group(
        global_group, reviser_locator=reviser, superseded_locator=superseded
    )
    americas = [
        item
        for item in _group_selections(admitted)
        if item["metric_identity_fields"].get("geography") == "americas"
        and item["period"] == SHARED_PERIOD
        and item["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    ]
    assert len(americas) == 1
    _assert_deferred_group(americas[0], REASON_MISSING_REVISION_LINK)
    assert set(americas[0]["locators"]).isdisjoint(global_group["locators"])


@pytest.mark.parametrize("family", FAMILIES)
def test_selection_follows_documentary_direction_not_order(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "dir-sel")
    _write_audited_revised_family_pair(dest, family, reviser="right")
    original = _admission(dest)
    orig_reviser, orig_superseded, orig_link = _selected_locators(original, family)
    _assert_selected_group(
        _family_period_group(original, family),
        reviser_locator=orig_reviser,
        superseded_locator=orig_superseded,
    )

    swapped = tmp_path / "swapped-sel"
    swapped.mkdir()
    for name in ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3]:
        shutil.copy2(dest / name, swapped / name)
    _write_audited_revised_family_pair(swapped, family, reviser="left")
    reversed_payload = _admission(swapped)
    reversed_link = _assert_revision_link(
        reversed_payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2023,
        revised_year=2024,
        family=family,
    )
    reversed_group = _family_period_group(reversed_payload, family)
    _assert_selected_group(
        reversed_group,
        reviser_locator=reversed_link["reviser"]["locator"],
        superseded_locator=reversed_link["revised"]["locator"],
    )
    assert reversed_link["named_target"]["source_file"] != orig_link["named_target"]["source_file"]

    renamed = tmp_path / "renamed-sel"
    renamed.mkdir()
    for index, name in enumerate(sorted(path.name for path in dest.glob("*.json"))):
        shutil.copy2(dest / name, renamed / f"{index:02d}-{name}")
    renamed_payload = _admission(renamed)
    renamed_reviser, renamed_superseded, renamed_link = _selected_locators(
        renamed_payload, family
    )
    _assert_selected_group(
        _family_period_group(renamed_payload, family),
        reviser_locator=renamed_reviser,
        superseded_locator=renamed_superseded,
    )
    assert renamed_link["named_target"] == orig_link["named_target"]
    assert renamed_reviser != orig_reviser


def test_outside_scope_and_unsupported_are_not_selected(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES[1:3] + MANAGEMENT_NAMES[1:3], tmp_path / "out-sel")
    left, right = _affirmative_family_pair(FAMILY_COMPARABLE_SALES_GROWTH)
    left = _apply_same_period(
        left, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    right = _apply_same_period(
        right, FAMILY_COMPARABLE_SALES_GROWTH, period=SHARED_PERIOD, value=10
    )
    target = next(
        item for item in left["reported_kpis"] if item.get("metric_id") == "net_revenue"
    )
    from core.tests.test_management_kpi_admission import (
        _attach_revision,
        _revision_target,
        _attach_assurance,
    )

    for item in _family_items(right, FAMILY_COMPARABLE_SALES_GROWTH):
        _attach_revision(
            item,
            _revision_target(target, left["report"]["source_file"]),
            source_file=right["report"]["source_file"],
        )
        _attach_assurance(item, "audited", source_file=right["report"]["source_file"])
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    payload = _admission(dest)
    group = _family_period_group(payload, FAMILY_COMPARABLE_SALES_GROWTH)
    _assert_deferred_group(group, REASON_OUTSIDE_SCOPE_TARGET, REASON_MISSING_REVISION_LINK)
    assert payload["reconciliation"]["selected_count"] == 0
    locators = {occ["locator"] for item in _group_selections(payload) for occ in item["occurrences"]}
    outside = [
        item["locator"]
        for item in payload["observations"]
        if item["metric_id"] == "net_revenue"
    ]
    assert not set(outside) & locators


@pytest.mark.parametrize("family", FAMILIES)
def test_cli_serializes_selected_and_deferred_groups(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli-sel")
    _write_audited_revised_family_pair(dest, family)
    out = tmp_path / "out"
    validate, reconcile = _cli_validate_and_reconcile(dest, out)
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert reconcile.returncode == 0, reconcile.stdout + reconcile.stderr
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    assert admission["status"] == "admitted_unreconciled"
    assert admission["canonical_selection"] == "deferred"
    assert admission["reconciliation"]["canonical_selection"] == "deferred"
    reviser, superseded, link = _selected_locators(admission, family)
    group = _family_period_group(admission, family)
    _assert_selected_group(group, reviser_locator=reviser, superseded_locator=superseded)
    assert link["canonical_selection"] == "deferred"
    assert "superseded" not in link
    assert admission["reconciliation"]["selected_count"] >= 1
    assert admission["reconciliation"]["superseded_count"] >= 1
    standardized = json.loads((out / "standardized.json").read_text(encoding="utf-8"))
    assert "historical_operating_kpis" not in standardized or standardized.get(
        "historical_operating_kpis"
    ) in {None, []}
    before = _bytes_by_name(EXTRACTED)
    assert _bytes_by_name(EXTRACTED) == before
    extracted_copy = {
        path.name: path.read_bytes()
        for path in dest.glob("*.json")
        if path.name in set(ANNUAL_NAMES + MANAGEMENT_NAMES)
    }
    validate2, reconcile2 = _cli_validate_and_reconcile(dest, tmp_path / "out2")
    assert validate2.returncode == 0
    assert reconcile2.returncode == 0
    after_copy = {
        path.name: path.read_bytes()
        for path in dest.glob("*.json")
        if path.name in extracted_copy
    }
    assert after_copy == extracted_copy


def test_cli_supplied_inputs_select_nothing(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli-none")
    out = tmp_path / "out"
    validate, reconcile = _cli_validate_and_reconcile(dest, out)
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert reconcile.returncode == 0, reconcile.stdout + reconcile.stderr
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    recon = admission["reconciliation"]
    assert recon["canonical_selection"] == "deferred"
    assert recon["selected_count"] == 0
    assert recon["superseded_count"] == 0
    assert recon["revision_links"] == []
    assert recon["group_selection_counts"][SELECTION_SELECTED] == 0
    for item in recon["group_selections"]:
        _assert_deferred_group(item)
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    annual_out = tmp_path / "annual-out"
    _validate, annual_run = _cli_validate_and_reconcile(annual, annual_out)
    assert annual_run.returncode == 0
    mixed_std = json.loads((out / "standardized.json").read_text(encoding="utf-8"))
    annual_std = json.loads((annual_out / "standardized.json").read_text(encoding="utf-8"))
    from core.tests.test_management_kpi_admission import _canonicalize

    assert _canonicalize(mixed_std) == _canonicalize(annual_std)
    assert not (annual_out / "management_kpi_admission.json").exists()
    assert _bytes_by_name(EXTRACTED) == before


def _pair_document_names(reviser: str) -> tuple[str, str]:
    if reviser == "right":
        return MANAGEMENT_NAMES[1], MANAGEMENT_NAMES[2]
    if reviser == "left":
        return MANAGEMENT_NAMES[2], MANAGEMENT_NAMES[1]
    raise ValueError(reviser)


def _bind_intra_revision_with_unit(
    dest: Path, family: str, *, reviser: str = "right"
) -> tuple[dict, dict]:
    left = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
    right = json.loads((dest / MANAGEMENT_NAMES[2]).read_text(encoding="utf-8"))
    if reviser in {"right", "both"}:
        unit = _family_items(left, family)[0]["unit"]
        right = _attach_family_revision(right, left, family, unit=unit)
    if reviser in {"left", "both"}:
        unit = _family_items(right, family)[0]["unit"]
        left = _attach_family_revision(left, right, family, unit=unit)
    _write_json(dest / MANAGEMENT_NAMES[1], left)
    _write_json(dest / MANAGEMENT_NAMES[2], right)
    return left, right


def _append_unsupported_family_duplicate(payload: dict, family: str) -> dict:
    payload = copy.deepcopy(payload)
    original = _family_items(payload, family)[0]
    duplicate = copy.deepcopy(original)
    duplicate["unit"] = "not-a-mapped-unit"
    duplicate.pop("revision", None)
    duplicate.pop("assurance", None)
    duplicate.pop("presentation", None)
    payload["reported_kpis"].append(duplicate)
    return payload


def _append_net_revenue_duplicate(payload: dict) -> dict:
    payload = copy.deepcopy(payload)
    revenue = next(
        item
        for item in payload["reported_kpis"]
        if item.get("metric_id") == "net_revenue"
    )
    payload["reported_kpis"].append(copy.deepcopy(revenue))
    return payload


def _affirmative_incoming_document(dest: Path, family: str) -> dict:
    from core.tests.test_management_kpi_identity import (
        _apply_affirmative_compsales,
        _apply_affirmative_spsf,
    )

    third = json.loads((dest / MANAGEMENT_NAMES[3]).read_text(encoding="utf-8"))
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        return _apply_affirmative_compsales(third)
    return _apply_affirmative_spsf(third)


def _attach_incoming_revision(
    dest: Path, family: str, target_payload: dict, *, named_overrides: dict | None = None
) -> dict:
    from core.tests.test_management_kpi_admission import (
        _attach_revision,
        _revision_target,
    )

    third = _affirmative_incoming_document(dest, family)
    target_item = (
        _family_items(target_payload, family)[0]
        if named_overrides is None
        else next(
            item
            for item in target_payload["reported_kpis"]
            if item.get("metric_id") == named_overrides.get("metric_id")
        )
    )
    named = _revision_target(
        target_item,
        target_payload["report"]["source_file"],
        **(named_overrides or {}),
    )
    for item in _family_items(third, family):
        _attach_revision(
            item,
            named,
            source_file=third["report"]["source_file"],
        )
    _write_json(dest / MANAGEMENT_NAMES[3], third)
    return third


def write_incoming_ambiguous_fixture(
    dest: Path,
    family: str,
    *,
    target: str = "superseded",
    include_incoming: bool = True,
    reviser: str = "right",
) -> None:
    _write_audited_revised_family_pair(dest, family, reviser=reviser)
    _bind_intra_revision_with_unit(dest, family, reviser=reviser)
    superseded_name, reviser_name = _pair_document_names(reviser)
    if target == "outside":
        left = json.loads((dest / MANAGEMENT_NAMES[1]).read_text(encoding="utf-8"))
        left = _append_net_revenue_duplicate(left)
        _write_json(dest / MANAGEMENT_NAMES[1], left)
        if include_incoming:
            _attach_incoming_revision(
                dest,
                family,
                left,
                named_overrides={"metric_id": "net_revenue"},
            )
        else:
            _write_json(
                dest / MANAGEMENT_NAMES[3],
                _affirmative_incoming_document(dest, family),
            )
        return
    target_name = superseded_name if target == "superseded" else reviser_name
    target_payload = json.loads((dest / target_name).read_text(encoding="utf-8"))
    target_payload = _append_unsupported_family_duplicate(target_payload, family)
    _write_json(dest / target_name, target_payload)
    if include_incoming:
        _attach_incoming_revision(dest, family, target_payload)
    else:
        _write_json(
            dest / MANAGEMENT_NAMES[3],
            _affirmative_incoming_document(dest, family),
        )


def _incoming_ambiguous_link(payload: dict, group: dict) -> dict:
    matches = [
        item
        for item in payload["reconciliation"]["revision_links"]
        if item["revised"] is None
        and REASON_AMBIGUOUS_TARGET in item["reasons"]
        and item["reviser"]["locator"] not in group["locators"]
    ]
    assert len(matches) == 1
    return matches[0]


def _assert_eligible_members_survive(
    group: dict, *, reviser_locator: str, superseded_locator: str
) -> None:
    assert len(group["occurrences"]) == 2
    assert len(set(group["locators"])) == 2
    by_locator = {occ["locator"]: occ for occ in group["occurrences"]}
    reviser = by_locator[reviser_locator]
    superseded = by_locator[superseded_locator]
    for occ in (reviser, superseded):
        assert occ["locator"]
        assert occ["occurrence_identity"]
        assert occ["source"]["page_reference"]
        assert occ["bound_source_file"].endswith(".pdf")
        assert occ["definition"]["text"]
    assert reviser["value"] is not None
    assert reviser["assurance_evidence"]["status"] == "audited"
    assert reviser["assurance_evidence"]["evidence"]
    assert reviser["assurance_evidence"]["locator"]
    assert reviser["revision_evidence"]["revises"]
    assert reviser["revision_evidence"]["evidence"]
    assert superseded["source"]["page_reference"]
    assert reviser["occurrence_identity"] != superseded["occurrence_identity"]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("target", ["superseded", "reviser"])
def test_incoming_ambiguous_candidate_defers_otherwise_eligible_group(
    tmp_path: Path, family: str, target: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "in")
    write_incoming_ambiguous_fixture(dest, family, target=target)
    payload = _admission(dest)
    assert payload["status"] == "admitted_unreconciled"
    assert payload["canonical_selection"] == "deferred"
    reviser, superseded, link = _selected_locators(payload, family)
    group = _family_period_group(payload, family)
    assert len(group["occurrences"]) == 2
    incoming = _incoming_ambiguous_link(payload, group)
    involved = superseded if target == "superseded" else reviser
    assert incoming["status"] == RELATIONSHIP_UNRESOLVED
    assert incoming["revised"] is None
    assert involved in incoming["candidate_locators"]
    assert len(incoming["candidate_locators"]) == 2
    assert reviser not in incoming["candidate_locators"] or target == "reviser"
    assert superseded not in incoming["candidate_locators"] or target == "superseded"
    assert link["revised"]["locator"] == superseded
    assert link["reviser"]["locator"] == reviser
    assert "candidate_locators" not in link
    _assert_deferred_group(group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET)
    _assert_eligible_members_survive(
        group, reviser_locator=reviser, superseded_locator=superseded
    )
    duplicate = next(
        locator
        for locator in incoming["candidate_locators"]
        if locator not in group["locators"]
    )
    assert _assessment(payload, duplicate)["status"] == STATUS_UNSUPPORTED_VARIANT
    assert payload["reconciliation"]["selected_count"] == 0
    assert payload["reconciliation"]["superseded_count"] == 0


@pytest.mark.parametrize("family", FAMILIES)
def test_removing_incoming_ambiguous_assertion_selects(tmp_path: Path, family: str):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "rm")
    write_incoming_ambiguous_fixture(
        dest, family, target="superseded", include_incoming=False
    )
    payload = _admission(dest)
    reviser, superseded, _link = _selected_locators(payload, family)
    group = _family_period_group(payload, family)
    assert len(group["occurrences"]) == 2
    _assert_selected_group(group, reviser_locator=reviser, superseded_locator=superseded)
    assert payload["reconciliation"]["selected_count"] >= 1


@pytest.mark.parametrize("family", FAMILIES)
def test_unrelated_ambiguous_candidates_do_not_block_selection(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "out")
    write_incoming_ambiguous_fixture(dest, family, target="outside")
    payload = _admission(dest)
    reviser, superseded, _link = _selected_locators(payload, family)
    group = _family_period_group(payload, family)
    assert len(group["occurrences"]) == 2
    incoming = _incoming_ambiguous_link(payload, group)
    assert incoming["status"] == RELATIONSHIP_UNRESOLVED
    assert set(incoming["candidate_locators"]).isdisjoint(group["locators"])
    _assert_selected_group(group, reviser_locator=reviser, superseded_locator=superseded)


@pytest.mark.parametrize("family", FAMILIES)
def test_incoming_ambiguous_candidate_is_permutation_invariant(
    tmp_path: Path, family: str
):
    dest = _copy_json(ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4], tmp_path / "perm")
    write_incoming_ambiguous_fixture(dest, family, target="superseded")
    original = _admission(dest)
    orig_group = _family_period_group(original, family)
    orig_incoming = _incoming_ambiguous_link(original, orig_group)
    orig_reviser, orig_superseded, orig_link = _selected_locators(original, family)
    _assert_deferred_group(orig_group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET)

    swapped = tmp_path / "swapped"
    swapped.mkdir()
    for name in ANNUAL_NAMES[1:4] + MANAGEMENT_NAMES[1:4]:
        shutil.copy2(dest / name, swapped / name)
    write_incoming_ambiguous_fixture(
        swapped, family, target="superseded", reviser="left"
    )
    reversed_payload = _admission(swapped)
    reversed_link = _assert_revision_link(
        reversed_payload,
        status=RELATIONSHIP_RECOGNIZED,
        reviser_year=2023,
        revised_year=2024,
        family=family,
    )
    reversed_group = _family_period_group(reversed_payload, family)
    reversed_incoming = _incoming_ambiguous_link(reversed_payload, reversed_group)
    _assert_deferred_group(
        reversed_group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET
    )
    assert reversed_incoming["revised"] is None
    assert reversed_link["named_target"]["source_file"] != orig_link["named_target"][
        "source_file"
    ]
    assert reversed_link["revised"]["locator"] in reversed_incoming["candidate_locators"]
    assert len(reversed_group["occurrences"]) == 2

    renamed = tmp_path / "renamed"
    renamed.mkdir()
    for index, name in enumerate(sorted(path.name for path in dest.glob("*.json"))):
        shutil.copy2(dest / name, renamed / f"{index:02d}-{name}")
    renamed_payload = _admission(renamed)
    renamed_group = _family_period_group(renamed_payload, family)
    renamed_incoming = _incoming_ambiguous_link(renamed_payload, renamed_group)
    renamed_reviser, renamed_superseded, renamed_link = _selected_locators(
        renamed_payload, family
    )
    _assert_deferred_group(
        renamed_group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET
    )
    _assert_eligible_members_survive(
        renamed_group,
        reviser_locator=renamed_reviser,
        superseded_locator=renamed_superseded,
    )
    assert renamed_incoming["named_target"] == orig_incoming["named_target"]
    assert renamed_link["named_target"] == orig_link["named_target"]
    assert renamed_reviser != orig_reviser
    assert renamed_superseded != orig_superseded
    assert orig_superseded in orig_incoming["candidate_locators"]
    assert renamed_superseded in renamed_incoming["candidate_locators"]
    before = _bytes_by_name(EXTRACTED)
    assert _bytes_by_name(EXTRACTED) == before


@pytest.mark.parametrize("family", FAMILIES)
def test_cli_serializes_incoming_ambiguous_candidate_deferral(
    tmp_path: Path, family: str
):
    before = _bytes_by_name(EXTRACTED)
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "cli-in")
    write_incoming_ambiguous_fixture(dest, family, target="superseded")
    admitted = _admission(dest)
    out = tmp_path / "out"
    validate, reconcile = _cli_validate_and_reconcile(dest, out)
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert reconcile.returncode == 0, reconcile.stdout + reconcile.stderr
    admission = json.loads(
        (out / "management_kpi_admission.json").read_text(encoding="utf-8")
    )
    assert admission["status"] == "admitted_unreconciled"
    group = _family_period_group(admission, family)
    admitted_group = _family_period_group(admitted, family)
    incoming = _incoming_ambiguous_link(admission, group)
    admitted_incoming = _incoming_ambiguous_link(admitted, admitted_group)
    _assert_deferred_group(group, RELATIONSHIP_UNRESOLVED, REASON_AMBIGUOUS_TARGET)
    assert group["status"] == admitted_group["status"]
    assert group["reasons"] == admitted_group["reasons"]
    assert group["selected"] is None
    assert group["superseded"] is None
    assert incoming == admitted_incoming
    assert incoming["revised"] is None
    assert incoming["candidate_locators"]
    assert admission["reconciliation"]["selected_count"] == 0
    extracted_copy = {
        path.name: path.read_bytes()
        for path in dest.glob("*.json")
        if path.name in set(ANNUAL_NAMES + MANAGEMENT_NAMES)
    }
    validate2, reconcile2 = _cli_validate_and_reconcile(dest, tmp_path / "out2")
    assert validate2.returncode == 0
    assert reconcile2.returncode == 0
    after_copy = {
        path.name: path.read_bytes()
        for path in dest.glob("*.json")
        if path.name in extracted_copy
    }
    assert after_copy == extracted_copy
    assert _bytes_by_name(EXTRACTED) == before
