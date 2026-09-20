"""Pairwise duplicate/conflict diagnostics for supported management KPIs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

from .management_kpi_identity import (
    REASON_MISSING_DEFINITION,
    REASON_PERIOD_DATE,
    REASON_UNBOUND_DEFINITION,
    REQUIRED_COMPARISON_REASONS,
    STATUS_OUTSIDE_SCOPE,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED_VARIANT,
    evidenced_conflicts,
    evidenced_period_conflict,
    pair_is_fully_evidenced_same_period,
    peer_gap_reason,
    required_comparison_reasons,
    text_present,
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
REASON_MISSING_TARGET = "missing_target"
REASON_MISSING_EVIDENCE = "missing_evidence"
REASON_AMBIGUOUS_TARGET = "ambiguous_target"
REASON_OUTSIDE_SCOPE_TARGET = "outside_scope_target"
REASON_UNSUPPORTED_TARGET = "unsupported_variant_target"
REASON_SCOPE_MISMATCH = "scope_mismatch"
REASON_RECIPROCAL = "reciprocal_revision"
REASON_CYCLIC = "cyclic_revision"
REASON_SINGLETON = "singleton"
REASON_GROUP_LARGER_THAN_TWO = "group_larger_than_two"
REASON_MISSING_REVISION_LINK = "missing_revision_link"
REASON_COMPETING_DIRECTION = "competing_revision_direction"
REASON_MISSING_REVISER_VALUE = "missing_reviser_value"
REASON_UNKNOWN_ASSURANCE = "unknown_assurance"
REASON_UNAUDITED_REVISER = "unaudited_reviser"
REASON_AMBIGUOUS_OCCURRENCE = "ambiguous_occurrence"
REASON_MISSING_PRESENTATION = "missing_presentation"
REASON_MISSING_PROVENANCE = "missing_provenance"
REASON_ORDINARY_DISAGREEMENT = "ordinary_disagreement"
RELATIONSHIP_RECOGNIZED = "recognized"
RELATIONSHIP_UNRESOLVED = "unresolved"
RELATIONSHIP_INCOMPATIBLE = "incompatible"
SELECTION_SELECTED = "selected"
SELECTION_DEFERRED = "deferred"
PRESENTATION_RELATIONSHIP_ROLES = (
    "current",
    "comparative",
    "restated",
    "prior",
    "unknown",
)
NAMED_PRESENTATION_COMBINATIONS = {
    ("current", "comparative"): "current_comparative",
    ("restated", "prior"): "restated_prior",
}
_KIND_RANK = {
    KIND_PAIR: 0,
    KIND_SINGLETON: 1,
    KIND_UNSUPPORTED_VARIANT: 2,
    KIND_OUTSIDE_SCOPE: 3,
}
_ROLE_RANK = {
    role: index for index, role in enumerate(PRESENTATION_RELATIONSHIP_ROLES)
}


def _ordered_role_pair(left_role: str, right_role: str) -> tuple[str, str]:
    first, second = sorted((left_role, right_role), key=_ROLE_RANK.__getitem__)
    return (first, second)


def _build_presentation_role_combinations() -> dict[tuple[str, str], str]:
    table: dict[tuple[str, str], str] = {}
    for index, left in enumerate(PRESENTATION_RELATIONSHIP_ROLES):
        for right in PRESENTATION_RELATIONSHIP_ROLES[index:]:
            ordered = _ordered_role_pair(left, right)
            table[ordered] = NAMED_PRESENTATION_COMBINATIONS.get(
                ordered, f"{ordered[0]}_{ordered[1]}"
            )
    return table


PRESENTATION_ROLE_COMBINATIONS = _build_presentation_role_combinations()
REVISION_ROUTE_REASONS = frozenset(
    {
        REASON_MISSING_REVISION_LINK,
        REASON_COMPETING_DIRECTION,
        REASON_MISSING_REVISER_VALUE,
        REASON_UNKNOWN_ASSURANCE,
        REASON_UNAUDITED_REVISER,
        REASON_AMBIGUOUS_TARGET,
        REASON_OUTSIDE_SCOPE_TARGET,
        REASON_UNSUPPORTED_TARGET,
        REASON_RECIPROCAL,
        REASON_CYCLIC,
        REASON_GROUP_LARGER_THAN_TWO,
        REASON_MISSING_EVIDENCE,
        REASON_MISSING_TARGET,
        RELATIONSHIP_UNRESOLVED,
        RELATIONSHIP_INCOMPATIBLE,
    }
)


def presentation_role_combination(left_role: str, right_role: str) -> str:
    """Deterministic unordered role-pair label; order does not imply precedence."""
    return PRESENTATION_ROLE_COMBINATIONS[_ordered_role_pair(left_role, right_role)]


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
    presentation_evidence: tuple[tuple[str, Any], ...]
    assurance_evidence: tuple[tuple[str, Any], ...]
    revision_evidence: tuple[tuple[str, Any], ...]

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
            "presentation_evidence": dict(self.presentation_evidence),
            "assurance_evidence": dict(self.assurance_evidence),
            "revision_evidence": dict(self.revision_evidence),
        }


@dataclass(frozen=True)
class ManagementKpiPresentationRelationshipMember:
    locator: str
    occurrence_identity: str
    role: str

    def to_payload(self) -> dict[str, str]:
        return {
            "locator": self.locator,
            "occurrence_identity": self.occurrence_identity,
            "role": self.role,
        }


@dataclass(frozen=True)
class ManagementKpiPresentationRelationship:
    status: str
    combination: str
    members: tuple[ManagementKpiPresentationRelationshipMember, ...]
    reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "combination": self.combination,
            "members": [item.to_payload() for item in self.members],
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class ManagementKpiRevisionMember:
    locator: str
    occurrence_identity: str

    def to_payload(self) -> dict[str, str]:
        return {
            "locator": self.locator,
            "occurrence_identity": self.occurrence_identity,
        }


@dataclass(frozen=True)
class ManagementKpiRevisionLink:
    status: str
    reviser: ManagementKpiRevisionMember
    revised: ManagementKpiRevisionMember | None
    named_target: tuple[tuple[str, str], ...]
    evidence: str
    source: tuple[tuple[str, Any], ...]
    reasons: tuple[str, ...]
    candidate_locators: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": "revision_link",
            "status": self.status,
            "reviser": self.reviser.to_payload(),
            "revised": None if self.revised is None else self.revised.to_payload(),
            "named_target": dict(self.named_target),
            "evidence": self.evidence,
            "source": dict(self.source),
            "reasons": list(self.reasons),
            "canonical_selection": "deferred",
        }
        if self.candidate_locators:
            payload["candidate_locators"] = list(self.candidate_locators)
        return payload


@dataclass(frozen=True)
class ManagementKpiSupportingRevision:
    reviser: ManagementKpiRevisionMember
    revised: ManagementKpiRevisionMember
    evidence: str
    source: tuple[tuple[str, Any], ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "reviser": self.reviser.to_payload(),
            "revised": self.revised.to_payload(),
            "evidence": self.evidence,
            "source": dict(self.source),
        }


@dataclass(frozen=True)
class ManagementKpiGroupSelection:
    status: str
    family: str
    metric_identity: str
    metric_identity_fields: tuple[tuple[str, str], ...]
    period: str
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...]
    reasons: tuple[str, ...]
    selected: ManagementKpiRevisionMember | None = None
    superseded: ManagementKpiRevisionMember | None = None
    revision: ManagementKpiSupportingRevision | None = None
    assurance_evidence: tuple[tuple[str, Any], ...] = ()

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": "group_selection",
            "status": self.status,
            "family": self.family,
            "metric_identity": self.metric_identity,
            "metric_identity_fields": dict(self.metric_identity_fields),
            "period": self.period,
            "occurrences": [item.to_payload() for item in self.occurrences],
            "locators": [item.locator for item in self.occurrences],
            "reasons": list(self.reasons),
            "selected": None if self.selected is None else self.selected.to_payload(),
            "superseded": (
                None if self.superseded is None else self.superseded.to_payload()
            ),
            "revision": None if self.revision is None else self.revision.to_payload(),
            "assurance_evidence": (
                dict(self.assurance_evidence) if self.assurance_evidence else None
            ),
        }
        return payload


@dataclass(frozen=True)
class ManagementKpiReconciliationRecord:
    kind: str
    outcome: str
    family: str
    metric_identity: str
    metric_identity_fields: tuple[tuple[str, str], ...]
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...]
    reasons: tuple[str, ...]
    presentation_relationship: ManagementKpiPresentationRelationship | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
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
        if self.presentation_relationship is not None:
            payload["presentation_relationship"] = (
                self.presentation_relationship.to_payload()
            )
        return payload


def _revision_evidence_payload(observation: Any) -> tuple[tuple[str, Any], ...]:
    record = getattr(observation, "revision_record", None)
    if record is not None and hasattr(record, "to_payload"):
        return tuple(sorted(record.to_payload().items()))
    return (
        ("evidence", ""),
        ("locator", ""),
        ("revises", None),
        ("source", None),
    )


def _dimension_payload(observation: Any, *, attr: str, value_key: str) -> dict[str, Any]:
    record = getattr(observation, attr, None)
    if record is not None and hasattr(record, "to_payload"):
        return dict(record.to_payload(value_key=value_key))
    value = (
        getattr(observation, "presentation_role", "unknown")
        if attr == "presentation_record"
        else getattr(observation, "assurance", "unknown")
    )
    return {
        value_key: value,
        "evidence": "",
        "locator": "",
        "source": None,
    }


def _occurrence_from(
    assessment: Any,
    observation: Any,
) -> ManagementKpiReconciledOccurrence:
    evidence = dict(assessment.evidence)
    presentation = _dimension_payload(
        observation, attr="presentation_record", value_key="role"
    )
    assurance = _dimension_payload(
        observation, attr="assurance_record", value_key="status"
    )
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
        presentation_evidence=tuple(sorted(presentation.items())),
        assurance_evidence=tuple(sorted(assurance.items())),
        revision_evidence=_revision_evidence_payload(observation),
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


def _occurrence_role(occurrence: ManagementKpiReconciledOccurrence) -> str:
    role = dict(occurrence.presentation_evidence).get("role", "unknown")
    return str(role or "unknown")


def _relationship_gate_reasons(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> tuple[str, ...]:
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    local_gaps = set(required_comparison_reasons(left_ev))
    peer_gaps = set(required_comparison_reasons(right_ev))
    reasons: list[str] = []
    for reason in evidenced_conflicts(left_ev, right_ev):
        reasons.append(reason)
    for reason in evidenced_period_conflict(left_ev, right_ev):
        reasons.append(reason)
    for reason in REQUIRED_COMPARISON_REASONS:
        if reason in local_gaps:
            reasons.append(reason)
    for reason in REQUIRED_COMPARISON_REASONS:
        if reason in peer_gaps:
            reasons.append(peer_gap_reason(reason))
    return tuple(reasons)


def _relationship_status(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> str:
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    if evidenced_conflicts(left_ev, right_ev) or evidenced_period_conflict(
        left_ev, right_ev
    ):
        return RELATIONSHIP_INCOMPATIBLE
    if required_comparison_reasons(left_ev) or required_comparison_reasons(right_ev):
        return RELATIONSHIP_UNRESOLVED
    if _occurrence_role(left) == "unknown" or _occurrence_role(right) == "unknown":
        return RELATIONSHIP_UNRESOLVED
    return RELATIONSHIP_RECOGNIZED


def _revision_gate_reasons(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> tuple[str, ...]:
    reasons = list(_relationship_gate_reasons(left, right))
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    if (
        text_present(left_ev.get("geography", ""))
        and text_present(right_ev.get("geography", ""))
        and left_ev.get("geography") != right_ev.get("geography")
        and REASON_SCOPE_MISMATCH not in reasons
    ):
        reasons.append(REASON_SCOPE_MISMATCH)
    if (
        text_present(left_ev.get("scope", ""))
        and text_present(right_ev.get("scope", ""))
        and left_ev.get("scope") != right_ev.get("scope")
        and REASON_SCOPE_MISMATCH not in reasons
    ):
        reasons.append(REASON_SCOPE_MISMATCH)
    return tuple(reasons)


def _revision_status(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> str:
    left_ev = dict(left.evidence)
    right_ev = dict(right.evidence)
    reasons = _revision_gate_reasons(left, right)
    if (
        evidenced_conflicts(left_ev, right_ev)
        or evidenced_period_conflict(left_ev, right_ev)
        or REASON_SCOPE_MISMATCH in reasons
    ):
        return RELATIONSHIP_INCOMPATIBLE
    if required_comparison_reasons(left_ev) or required_comparison_reasons(right_ev):
        return RELATIONSHIP_UNRESOLVED
    return RELATIONSHIP_RECOGNIZED


def _documentary_revision_reasons(evidence: object, *reasons: str) -> tuple[str, ...]:
    out = list(reasons)
    if not text_present(evidence) and REASON_MISSING_EVIDENCE not in out:
        out.append(REASON_MISSING_EVIDENCE)
    return tuple(out)


def _revision_source_payload(observation: Any) -> tuple[tuple[str, Any], ...]:
    record = getattr(observation, "revision_record", None)
    source = getattr(record, "source", None) if record is not None else None
    if source is not None and hasattr(source, "to_payload"):
        payload = dict(source.to_payload())
    else:
        payload = {}
    payload.setdefault("physical_page_mapping", "unresolved")
    return tuple(sorted(payload.items()))


def _revision_member(observation: Any, assessment: Any | None) -> ManagementKpiRevisionMember:
    identity = (
        assessment.occurrence_identity
        if assessment is not None
        else observation.identity
    )
    return ManagementKpiRevisionMember(
        locator=observation.locator,
        occurrence_identity=identity,
    )


def _can_reach(
    graph: dict[str, set[str]],
    start: str,
    goal: str,
    *,
    min_hops: int,
) -> bool:
    stack = [(start, 0)]
    seen: set[str] = set()
    while stack:
        node, hops = stack.pop()
        if hops >= min_hops and node == goal:
            return True
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph.get(node, ()):
            stack.append((nxt, hops + 1))
    return False


def reconcile_revision_links(
    observations: Sequence[Any],
    assessments: Sequence[Any],
) -> tuple[ManagementKpiRevisionLink, ...]:
    """Serialize directed documentary revision links; never select a canonical winner."""
    from .management_kpi import revision_target_matches

    by_assessment = {item.locator: item for item in assessments}
    links: list[ManagementKpiRevisionLink] = []
    for observation in observations:
        named = tuple(getattr(observation.revision_record, "revises", ()) or ())
        if not named:
            continue
        matches = [
            item
            for item in revision_target_matches(observation, observations)
            if item.locator != observation.locator
        ]
        reviser = _revision_member(
            observation, by_assessment.get(observation.locator)
        )
        evidence = getattr(observation.revision_record, "evidence", "")
        source = _revision_source_payload(observation)
        if not matches:
            links.append(
                ManagementKpiRevisionLink(
                    status=RELATIONSHIP_UNRESOLVED,
                    reviser=reviser,
                    revised=None,
                    named_target=named,
                    evidence=evidence,
                    source=source,
                    reasons=_documentary_revision_reasons(
                        evidence, REASON_MISSING_TARGET
                    ),
                )
            )
            continue
        if len(matches) != 1:
            links.append(
                ManagementKpiRevisionLink(
                    status=RELATIONSHIP_UNRESOLVED,
                    reviser=reviser,
                    revised=None,
                    named_target=named,
                    evidence=evidence,
                    source=source,
                    reasons=_documentary_revision_reasons(
                        evidence, REASON_AMBIGUOUS_TARGET
                    ),
                    candidate_locators=tuple(
                        sorted(item.locator for item in matches)
                    ),
                )
            )
            continue
        target = matches[0]
        target_assessment = by_assessment.get(target.locator)
        reviser_assessment = by_assessment.get(observation.locator)
        revised = _revision_member(target, target_assessment)
        if (
            reviser_assessment is None
            or reviser_assessment.status != STATUS_SUPPORTED
            or target_assessment is None
            or target_assessment.status != STATUS_SUPPORTED
        ):
            reason = REASON_OUTSIDE_SCOPE_TARGET
            if (
                target_assessment is not None
                and target_assessment.status == STATUS_UNSUPPORTED_VARIANT
            ) or (
                reviser_assessment is not None
                and reviser_assessment.status == STATUS_UNSUPPORTED_VARIANT
            ):
                reason = REASON_UNSUPPORTED_TARGET
            links.append(
                ManagementKpiRevisionLink(
                    status=RELATIONSHIP_UNRESOLVED,
                    reviser=reviser,
                    revised=revised,
                    named_target=named,
                    evidence=evidence,
                    source=source,
                    reasons=_documentary_revision_reasons(evidence, reason),
                )
            )
            continue
        left = _occurrence_from(reviser_assessment, observation)
        right = _occurrence_from(target_assessment, target)
        reasons = _documentary_revision_reasons(
            evidence, *_revision_gate_reasons(left, right)
        )
        status = _revision_status(left, right)
        if not text_present(evidence):
            status = RELATIONSHIP_UNRESOLVED
        links.append(
            ManagementKpiRevisionLink(
                status=status,
                reviser=reviser,
                revised=revised,
                named_target=named,
                evidence=evidence,
                source=source,
                reasons=reasons,
            )
        )

    bound_edges = [
        (item.reviser.locator, item.revised.locator)
        for item in links
        if item.revised is not None
    ]
    edge_set = set(bound_edges)
    graph: dict[str, set[str]] = {}
    for start, end in edge_set:
        graph.setdefault(start, set()).add(end)
    annotated: list[ManagementKpiRevisionLink] = []
    for item in links:
        reasons = list(item.reasons)
        if item.revised is not None:
            start = item.reviser.locator
            end = item.revised.locator
            if (end, start) in edge_set and REASON_RECIPROCAL not in reasons:
                reasons.append(REASON_RECIPROCAL)
            if (
                _can_reach(graph, end, start, min_hops=2)
                and REASON_CYCLIC not in reasons
            ):
                reasons.append(REASON_CYCLIC)
        annotated.append(
            ManagementKpiRevisionLink(
                status=item.status,
                reviser=item.reviser,
                revised=item.revised,
                named_target=item.named_target,
                evidence=item.evidence,
                source=item.source,
                reasons=tuple(reasons),
                candidate_locators=item.candidate_locators,
            )
        )
    annotated.sort(
        key=lambda item: (
            item.reviser.locator,
            item.revised.locator if item.revised is not None else "",
            tuple(item.named_target),
        )
    )
    return tuple(annotated)


def _occurrence_assurance_status(occurrence: ManagementKpiReconciledOccurrence) -> str:
    status = dict(occurrence.assurance_evidence).get("status", "unknown")
    return str(status or "unknown")


def _reviser_is_audited(occurrence: ManagementKpiReconciledOccurrence) -> bool:
    evidence = dict(occurrence.assurance_evidence)
    if evidence.get("status") != "audited":
        return False
    if not text_present(evidence.get("evidence", "")):
        return False
    if not text_present(evidence.get("locator", "")):
        return False
    source = evidence.get("source")
    if not isinstance(source, dict):
        return False
    return text_present(source.get("page_reference", ""))


def _link_involves(link: ManagementKpiRevisionLink, locators: set[str]) -> bool:
    if link.reviser.locator in locators:
        return True
    if link.revised is not None and link.revised.locator in locators:
        return True
    return bool(locators.intersection(link.candidate_locators))


def _link_is_intra(link: ManagementKpiRevisionLink, locators: set[str]) -> bool:
    return (
        link.revised is not None
        and link.reviser.locator in locators
        and link.revised.locator in locators
    )


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason and reason not in reasons:
        reasons.append(reason)


def _member_from_occurrence(
    occurrence: ManagementKpiReconciledOccurrence,
) -> ManagementKpiRevisionMember:
    return ManagementKpiRevisionMember(
        locator=occurrence.locator,
        occurrence_identity=occurrence.occurrence_identity,
    )


def _occurrence_has_revision_claim(occurrence: ManagementKpiReconciledOccurrence) -> bool:
    revises = dict(occurrence.revision_evidence).get("revises")
    return isinstance(revises, dict) and bool(revises)


def _group_has_revision_assertions(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
    revision_links: Sequence[ManagementKpiRevisionLink],
) -> bool:
    locators = {item.locator for item in occurrences}
    if any(_link_involves(item, locators) for item in revision_links):
        return True
    return any(_occurrence_has_revision_claim(item) for item in occurrences)


def _dimension_is_documented(evidence: Mapping[str, Any] | tuple) -> bool:
    payload = dict(evidence)
    if not text_present(payload.get("evidence", "")):
        return False
    if not text_present(payload.get("locator", "")):
        return False
    source = payload.get("source")
    if not isinstance(source, dict):
        return False
    return text_present(source.get("page_reference", ""))


def _presentation_is_documented(occurrence: ManagementKpiReconciledOccurrence) -> bool:
    evidence = dict(occurrence.presentation_evidence)
    role = str(evidence.get("role") or "unknown")
    if role in {"", "unknown"}:
        return False
    return _dimension_is_documented(evidence)


def _provenance_is_documented(occurrence: ManagementKpiReconciledOccurrence) -> bool:
    if not text_present(occurrence.bound_source_file):
        return False
    if not text_present(occurrence.bound_source_sha256):
        return False
    source = dict(occurrence.source)
    return text_present(source.get("page_reference", ""))


def _ordinary_admission_reasons(
    occurrence: ManagementKpiReconciledOccurrence,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if occurrence.value is None:
        _append_reason(reasons, REASON_MISSING_VALUE)
    if not text_present(occurrence.occurrence_identity):
        _append_reason(reasons, REASON_AMBIGUOUS_OCCURRENCE)
    if not text_present(occurrence.period) or occurrence.period_kind != "date":
        _append_reason(reasons, REASON_PERIOD_DATE)
    evidence = dict(occurrence.evidence)
    if not text_present(occurrence.definition_text):
        if not text_present(evidence.get("definition_id", "")):
            _append_reason(reasons, REASON_MISSING_DEFINITION)
        else:
            _append_reason(reasons, REASON_UNBOUND_DEFINITION)
    if not _presentation_is_documented(occurrence):
        _append_reason(reasons, REASON_MISSING_PRESENTATION)
    if not _provenance_is_documented(occurrence):
        _append_reason(reasons, REASON_MISSING_PROVENANCE)
    return tuple(reasons)


def _ordinary_agreement_reasons(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    identities = [item.occurrence_identity for item in occurrences]
    if len(set(identities)) != len(occurrences):
        _append_reason(reasons, REASON_AMBIGUOUS_OCCURRENCE)
    values = {item.value for item in occurrences}
    if len(values) != 1 or None in values:
        _append_reason(reasons, REASON_ORDINARY_DISAGREEMENT)
    first = occurrences[0]
    first_ev = dict(first.evidence)
    for other in occurrences[1:]:
        other_ev = dict(other.evidence)
        conflicts = evidenced_conflicts(
            {
                "definition_text": first.definition_text,
                "population": first_ev.get("population", ""),
                "unit": first_ev.get("unit", ""),
                "basis": first_ev.get("basis", ""),
                "calendar_week_adjustment": first_ev.get("calendar_week_adjustment", ""),
                "calendar_reporting_basis": first_ev.get("calendar_reporting_basis", ""),
            },
            {
                "definition_text": other.definition_text,
                "population": other_ev.get("population", ""),
                "unit": other_ev.get("unit", ""),
                "basis": other_ev.get("basis", ""),
                "calendar_week_adjustment": other_ev.get("calendar_week_adjustment", ""),
                "calendar_reporting_basis": other_ev.get("calendar_reporting_basis", ""),
            },
        )
        for reason in conflicts:
            _append_reason(reasons, reason)
            _append_reason(reasons, REASON_ORDINARY_DISAGREEMENT)
    return tuple(reasons)


def _ordinary_representative(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
) -> ManagementKpiReconciledOccurrence:
    current = [item for item in occurrences if _occurrence_role(item) == "current"]
    if len(current) == 1:
        return current[0]
    ordered = current or list(occurrences)
    ordered.sort(key=lambda item: item.locator)
    return ordered[0]


def _deferred_selection(reasons: list[str]) -> tuple[
    str,
    tuple[str, ...],
    ManagementKpiRevisionMember | None,
    ManagementKpiRevisionMember | None,
    ManagementKpiSupportingRevision | None,
    tuple[tuple[str, Any], ...],
]:
    return (
        SELECTION_DEFERRED,
        tuple(reasons),
        None,
        None,
        None,
        (),
    )


def _select_ordinary_group(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
) -> tuple[
    str,
    tuple[str, ...],
    ManagementKpiRevisionMember | None,
    ManagementKpiRevisionMember | None,
    ManagementKpiSupportingRevision | None,
    tuple[tuple[str, Any], ...],
]:
    reasons: list[str] = []
    identities = [item.occurrence_identity for item in occurrences]
    if len(set(identities)) != len(occurrences):
        _append_reason(reasons, REASON_AMBIGUOUS_OCCURRENCE)
    for item in occurrences:
        for reason in _ordinary_admission_reasons(item):
            _append_reason(reasons, reason)
    if len(occurrences) > 1:
        for reason in _ordinary_agreement_reasons(occurrences):
            _append_reason(reasons, reason)
    if reasons:
        return _deferred_selection(reasons)
    selected_occ = _ordinary_representative(occurrences)
    return (
        SELECTION_SELECTED,
        (),
        _member_from_occurrence(selected_occ),
        None,
        None,
        selected_occ.assurance_evidence,
    )


def _select_revision_group(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
    revision_links: Sequence[ManagementKpiRevisionLink],
) -> tuple[
    str,
    tuple[str, ...],
    ManagementKpiRevisionMember | None,
    ManagementKpiRevisionMember | None,
    ManagementKpiSupportingRevision | None,
    tuple[tuple[str, Any], ...],
]:
    locators = {item.locator for item in occurrences}
    by_locator = {item.locator: item for item in occurrences}
    reasons: list[str] = []
    identities = [item.occurrence_identity for item in occurrences]
    if len(set(identities)) != len(occurrences):
        _append_reason(reasons, REASON_AMBIGUOUS_OCCURRENCE)
    if len(occurrences) == 1:
        _append_reason(reasons, REASON_SINGLETON)
    elif len(occurrences) > 2:
        _append_reason(reasons, REASON_GROUP_LARGER_THAN_TWO)

    involved = [item for item in revision_links if _link_involves(item, locators)]
    intra = [item for item in involved if _link_is_intra(item, locators)]
    for link in involved:
        for reason in link.reasons:
            _append_reason(reasons, reason)
        if link.status == RELATIONSHIP_UNRESOLVED:
            _append_reason(reasons, RELATIONSHIP_UNRESOLVED)
        elif link.status == RELATIONSHIP_INCOMPATIBLE:
            _append_reason(reasons, RELATIONSHIP_INCOMPATIBLE)

    recognized_intra = [
        item
        for item in intra
        if item.status == RELATIONSHIP_RECOGNIZED
        and REASON_RECIPROCAL not in item.reasons
        and REASON_CYCLIC not in item.reasons
    ]
    if len(involved) > 1:
        _append_reason(reasons, REASON_COMPETING_DIRECTION)
    if len(occurrences) == 2:
        if (
            len(recognized_intra) != 1
            or len(involved) != 1
            or involved[0] is not recognized_intra[0]
        ):
            if not recognized_intra:
                _append_reason(reasons, REASON_MISSING_REVISION_LINK)
            elif len(recognized_intra) > 1:
                _append_reason(reasons, REASON_COMPETING_DIRECTION)

    candidate = recognized_intra[0] if len(recognized_intra) == 1 else None
    if candidate is not None:
        reviser = by_locator.get(candidate.reviser.locator)
        revised = by_locator.get(candidate.revised.locator) if candidate.revised else None
        if reviser is None or revised is None:
            _append_reason(reasons, REASON_MISSING_REVISION_LINK)
            candidate = None
        else:
            if reviser.value is None:
                _append_reason(reasons, REASON_MISSING_REVISER_VALUE)
            assurance = _occurrence_assurance_status(reviser)
            if assurance == "unaudited":
                _append_reason(reasons, REASON_UNAUDITED_REVISER)
            elif not _reviser_is_audited(reviser):
                _append_reason(reasons, REASON_UNKNOWN_ASSURANCE)
            if len(occurrences) == 2:
                gate_status = _revision_status(occurrences[0], occurrences[1])
                if gate_status != RELATIONSHIP_RECOGNIZED:
                    for reason in _revision_gate_reasons(occurrences[0], occurrences[1]):
                        _append_reason(reasons, reason)
                    _append_reason(reasons, gate_status)

    eligible = (
        len(occurrences) == 2
        and len(set(identities)) == 2
        and candidate is not None
        and len(involved) == 1
        and involved[0] is candidate
        and candidate.revised is not None
        and candidate.reviser.locator in by_locator
        and candidate.revised.locator in by_locator
        and by_locator[candidate.reviser.locator].value is not None
        and _reviser_is_audited(by_locator[candidate.reviser.locator])
        and not reasons
    )
    if eligible and candidate is not None and candidate.revised is not None:
        reviser_occ = by_locator[candidate.reviser.locator]
        revised_occ = by_locator[candidate.revised.locator]
        return (
            SELECTION_SELECTED,
            (),
            _member_from_occurrence(reviser_occ),
            _member_from_occurrence(revised_occ),
            ManagementKpiSupportingRevision(
                reviser=candidate.reviser,
                revised=candidate.revised,
                evidence=candidate.evidence,
                source=candidate.source,
            ),
            reviser_occ.assurance_evidence,
        )
    if not reasons:
        _append_reason(reasons, REASON_MISSING_REVISION_LINK)
    return _deferred_selection(reasons)


def _select_group(
    occurrences: tuple[ManagementKpiReconciledOccurrence, ...],
    revision_links: Sequence[ManagementKpiRevisionLink],
) -> tuple[
    str,
    tuple[str, ...],
    ManagementKpiRevisionMember | None,
    ManagementKpiRevisionMember | None,
    ManagementKpiSupportingRevision | None,
    tuple[tuple[str, Any], ...],
]:
    if _group_has_revision_assertions(occurrences, revision_links):
        return _select_revision_group(occurrences, revision_links)
    return _select_ordinary_group(occurrences)


def reconcile_group_selections(
    observations: Sequence[Any],
    assessments: Sequence[Any],
    revision_links: Sequence[ManagementKpiRevisionLink],
) -> tuple[ManagementKpiGroupSelection, ...]:
    """Select ordinary supported disclosures or audited documentary revisers."""
    by_locator = {item.locator: item for item in observations}
    grouped: dict[tuple[str, str, str], list[Any]] = defaultdict(list)
    for assessment in assessments:
        if assessment.status != STATUS_SUPPORTED or not assessment.metric_identity:
            continue
        observation = by_locator.get(assessment.locator)
        if observation is None:
            continue
        grouped[
            (assessment.family, assessment.metric_identity, observation.period)
        ].append(assessment)

    records: list[ManagementKpiGroupSelection] = []
    for (family, identity, period), group in grouped.items():
        ordered = sorted(group, key=lambda item: item.locator)
        occurrences = tuple(
            _occurrence_from(item, by_locator[item.locator]) for item in ordered
        )
        (
            status,
            reasons,
            selected,
            superseded,
            revision,
            assurance_evidence,
        ) = _select_group(occurrences, revision_links)
        records.append(
            ManagementKpiGroupSelection(
                status=status,
                family=family,
                metric_identity=identity,
                metric_identity_fields=ordered[0].metric_identity_fields,
                period=period,
                occurrences=occurrences,
                reasons=reasons,
                selected=selected,
                superseded=superseded,
                revision=revision,
                assurance_evidence=assurance_evidence,
            )
        )
    records.sort(
        key=lambda item: (
            item.family,
            item.metric_identity,
            item.period,
            tuple(occ.locator for occ in item.occurrences),
        )
    )
    return tuple(records)


def _presentation_relationship(
    left: ManagementKpiReconciledOccurrence,
    right: ManagementKpiReconciledOccurrence,
) -> ManagementKpiPresentationRelationship:
    members = (
        ManagementKpiPresentationRelationshipMember(
            locator=left.locator,
            occurrence_identity=left.occurrence_identity,
            role=_occurrence_role(left),
        ),
        ManagementKpiPresentationRelationshipMember(
            locator=right.locator,
            occurrence_identity=right.occurrence_identity,
            role=_occurrence_role(right),
        ),
    )
    return ManagementKpiPresentationRelationship(
        status=_relationship_status(left, right),
        combination=presentation_role_combination(members[0].role, members[1].role),
        members=members,
        reasons=_relationship_gate_reasons(left, right),
    )


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
                    presentation_relationship=_presentation_relationship(left, right),
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
    revision_links: Iterable[ManagementKpiRevisionLink] = (),
    group_selections: Iterable[ManagementKpiGroupSelection] = (),
) -> dict[str, Any]:
    items = list(records)
    links = list(revision_links)
    selections = list(group_selections)
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
    revision_counts = {
        RELATIONSHIP_RECOGNIZED: 0,
        RELATIONSHIP_UNRESOLVED: 0,
        RELATIONSHIP_INCOMPATIBLE: 0,
    }
    for item in links:
        revision_counts[item.status] = revision_counts.get(item.status, 0) + 1
    selection_counts = {
        SELECTION_SELECTED: 0,
        SELECTION_DEFERRED: 0,
    }
    selected_count = 0
    superseded_count = 0
    for item in selections:
        selection_counts[item.status] = selection_counts.get(item.status, 0) + 1
        if item.selected is not None:
            selected_count += 1
        if item.superseded is not None:
            superseded_count += 1
    return {
        "canonical_selection": "deferred",
        "pair_count": pair_count,
        "outcome_counts": outcome_counts,
        "revision_link_counts": revision_counts,
        "revision_links": [item.to_payload() for item in links],
        "group_selection_counts": selection_counts,
        "selected_count": selected_count,
        "superseded_count": superseded_count,
        "group_selections": [item.to_payload() for item in selections],
        "items": [item.to_payload() for item in items],
    }
