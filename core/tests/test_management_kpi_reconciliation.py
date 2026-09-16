"""Pairwise duplicate/conflict reconciliation for supported management KPIs."""

from __future__ import annotations

import copy
import json
import shutil
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
    OUTCOME_AGREEING_DUPLICATE,
    OUTCOME_CONFLICTING_CANDIDATE,
    OUTCOME_INCOMPATIBLE,
    OUTCOME_UNRESOLVED,
    REASON_MISSING_VALUE,
)
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
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
        else:
            assert len(item["locators"]) == 1
            assert item["locators"][0] == item["occurrences"][0]["locator"]
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
