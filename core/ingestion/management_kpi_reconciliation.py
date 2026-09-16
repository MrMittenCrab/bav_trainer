"""Pairwise duplicate/conflict diagnostics for supported management KPIs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, Sequence

from .management_kpi_identity import (
    REQUIRED_COMPARISON_REASONS,
    STATUS_OUTSIDE_SCOPE,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED_VARIANT,
    evidenced_conflicts,
    evidenced_period_conflict,
    pair_is_fully_evidenced_same_period,
    peer_gap_reason,
    required_comparison_reasons,
)

KIND_PAIR = "pair"
KIND_SINGLETON = "singleton"
KIND_UNSUPPORTED_VARIANT = "unsupported_variant"
KIND_OUTSIDE_SCOPE = "outside_scope"
OUTCOME_AGREEING_DUPLICATE = "agreeing_duplicate"
OUTCOME_CONFLICTING_CANDIDATE = "conflicting_candidate"
OUTCOME_INCOMPATIBLE = "incompatible"
OUTCOME_UNRESOLVED = "unresolved"
REASON_MISSING_VALUE = "missing_value"
_KIND_RANK = {
    KIND_PAIR: 0,
    KIND_SINGLETON: 1,
    KIND_UNSUPPORTED_VARIANT: 2,
    KIND_OUTSIDE_SCOPE: 3,
}


def _json_num(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if float(value).is_integer() else float(value)


def _source_payload(observation: Any) -> dict[str, Any]:
    source = getattr(observation, "source", None)
    if source is not None and hasattr(source, "to_payload"):
        payload = dict(source.to_payload())
    else:
        payload = {}
    payload.setdefault("physical_page_mapping", "unresolved")
    return payload


@dataclass(frozen=True)
class ManagementKpiReconciledOccurrence:
    locator: str
    occurrence_identity: str
    value: float | None
    period: str
    period_kind: str
    definition_id: str
    definition_document: str
    definition_text: str
    definition_label: str
    source: tuple[tuple[str, Any], ...]
    bound_source_file: str
    bound_source_sha256: str
    extraction_document: str
    evidence: tuple[tuple[str, str], ...]
    required_reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "locator": self.locator,
            "occurrence_identity": self.occurrence_identity,
            "value": _json_num(self.value),
            "period": self.period,
            "period_kind": self.period_kind,
            "definition": {
                "definition_id": self.definition_id,
                "extraction_document": self.definition_document,
                "reported_label": self.definition_label,
                "text": self.definition_text,
            },
            "source": dict(self.source),
            "bound_source_file": self.bound_source_file,
            "bound_source_sha256": self.bound_source_sha256,
            "extraction_document": self.extraction_document,
            "evidence": dict(self.evidence),
            "required_reasons": list(self.required_reasons),
        }


@dataclass(frozen=True)
class ManagementKpiReconciliationRecord:
    kind: str
    outcome: str
    family: str
    metric_identity: str
    metric_identity_fields: tuple[tuple[str, str], ...]
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...]
    reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "outcome": self.outcome,
            "family": self.family,
            "metric_identity": self.metric_identity,
            "metric_identity_fields": dict(self.metric_identity_fields),
            "occurrences": [item.to_payload() for item in self.occurrences],
            "locators": [item.locator for item in self.occurrences],
            "reasons": list(self.reasons),
            "canonical_selection": "deferred",
        }


def _occurrence_from(
    assessment: Any,
    observation: Any,
) -> ManagementKpiReconciledOccurrence:
    evidence = dict(assessment.evidence)
    return ManagementKpiReconciledOccurrence(
        locator=assessment.locator,
        occurrence_identity=assessment.occurrence_identity,
        value=observation.value,
        period=observation.period,
        period_kind=observation.period_kind,
        definition_id=assessment.definition_id,
        definition_document=assessment.definition_document,
        definition_text=assessment.definition_text,
        definition_label=assessment.definition_label,
        source=tuple(sorted(_source_payload(observation).items())),
        bound_source_file=observation.bound_source_file,
        bound_source_sha256=observation.bound_source_sha256,
        extraction_document=observation.extraction_document,
        evidence=tuple(sorted(evidence.items())),
        required_reasons=required_comparison_reasons(evidence),
    )


def _pair_reasons(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> tuple[str, ...]:
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    local_gaps = set(required_comparison_reasons(left_ev))
    peer_gaps = set(required_comparison_reasons(right_ev))
    conflicts = evidenced_conflicts(left_ev, right_ev)
    period_conflicts = evidenced_period_conflict(left_ev, right_ev)
    reasons: list[str] = []
    for reason in conflicts:
        reasons.append(reason)
    for reason in period_conflicts:
        reasons.append(reason)
    for reason in REQUIRED_COMPARISON_REASONS:
        if reason in local_gaps:
            reasons.append(reason)
    for reason in REQUIRED_COMPARISON_REASONS:
        if reason in peer_gaps:
            reasons.append(peer_gap_reason(reason))
    if left.value is None:
        reasons.append(REASON_MISSING_VALUE)
    if right.value is None:
        reasons.append(peer_gap_reason(REASON_MISSING_VALUE))
    return tuple(reasons)


def _pair_outcome(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> str:
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    if evidenced_conflicts(left_ev, right_ev) or evidenced_period_conflict(
        left_ev, right_ev
    ):
        return OUTCOME_INCOMPATIBLE
    if left.value is None or right.value is None:
        return OUTCOME_UNRESOLVED
    if not pair_is_fully_evidenced_same_period(left_ev, right_ev):
        return OUTCOME_UNRESOLVED
    if left.value == right.value:
        return OUTCOME_AGREEING_DUPLICATE
    return OUTCOME_CONFLICTING_CANDIDATE


def _coverage_record(
    *,
    kind: str,
    assessment: Any,
    observation: Any,
) -> ManagementKpiReconciliationRecord:
    occurrence = _occurrence_from(assessment, observation)
    return ManagementKpiReconciliationRecord(
        kind=kind,
        outcome=kind,
        family=assessment.family,
        metric_identity=assessment.metric_identity,
        metric_identity_fields=assessment.metric_identity_fields,
        occurrences=(occurrence,),
        reasons=assessment.unresolved_reasons,
    )


def reconcile_reported_observations(
    observations: Sequence[Any],
    assessments: Sequence[Any],
) -> tuple[ManagementKpiReconciliationRecord, ...]:
    """Emit one unordered pair per supported identity and explicit coverage."""
    by_locator = {item.locator: item for item in observations}
    records: list[ManagementKpiReconciliationRecord] = []
    supported_groups: dict[str, list[Any]] = defaultdict(list)
    for assessment in assessments:
        observation = by_locator.get(assessment.locator)
        if observation is None:
            continue
        if assessment.status == STATUS_SUPPORTED and assessment.metric_identity:
            supported_groups[assessment.metric_identity].append(assessment)
            continue
        if assessment.status == STATUS_UNSUPPORTED_VARIANT:
            records.append(
                _coverage_record(
                    kind=KIND_UNSUPPORTED_VARIANT,
                    assessment=assessment,
                    observation=observation,
                )
            )
            continue
        if assessment.status == STATUS_OUTSIDE_SCOPE:
            records.append(
                _coverage_record(
                    kind=KIND_OUTSIDE_SCOPE,
                    assessment=assessment,
                    observation=observation,
                )
            )

    for identity, group in supported_groups.items():
        ordered = sorted(group, key=lambda item: item.locator)
        if len(ordered) == 1:
            observation = by_locator[ordered[0].locator]
            records.append(
                _coverage_record(
                    kind=KIND_SINGLETON,
                    assessment=ordered[0],
                    observation=observation,
                )
            )
            continue
        fields = ordered[0].metric_identity_fields
        family = ordered[0].family
        for left_assessment, right_assessment in combinations(ordered, 2):
            if left_assessment.locator == right_assessment.locator:
                continue
            left = _occurrence_from(left_assessment, by_locator[left_assessment.locator])
            right = _occurrence_from(
                right_assessment, by_locator[right_assessment.locator]
            )
            if left.locator > right.locator:
                left, right = right, left
            reasons = _pair_reasons(left, right)
            records.append(
                ManagementKpiReconciliationRecord(
                    kind=KIND_PAIR,
                    outcome=_pair_outcome(left, right),
                    family=family,
                    metric_identity=identity,
                    metric_identity_fields=fields,
                    occurrences=(left, right),
                    reasons=reasons,
                )
            )

    records.sort(
        key=lambda item: (
            _KIND_RANK.get(item.kind, 9),
            item.family,
            item.metric_identity,
            tuple(occ.locator for occ in item.occurrences),
        )
    )
    return tuple(records)


def reconciliation_payload(
    records: Iterable[ManagementKpiReconciliationRecord],
) -> dict[str, Any]:
    items = list(records)
    outcome_counts = {
        OUTCOME_AGREEING_DUPLICATE: 0,
        OUTCOME_CONFLICTING_CANDIDATE: 0,
        OUTCOME_INCOMPATIBLE: 0,
        OUTCOME_UNRESOLVED: 0,
        KIND_SINGLETON: 0,
        KIND_UNSUPPORTED_VARIANT: 0,
        KIND_OUTSIDE_SCOPE: 0,
    }
    pair_count = 0
    for item in items:
        if item.kind == KIND_PAIR:
            pair_count += 1
        outcome_counts[item.outcome] = outcome_counts.get(item.outcome, 0) + 1
    return {
        "canonical_selection": "deferred",
        "pair_count": pair_count,
        "outcome_counts": outcome_counts,
        "items": [item.to_payload() for item in items],
    }
