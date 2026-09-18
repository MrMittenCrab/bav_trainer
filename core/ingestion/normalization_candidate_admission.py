"""Opt-in normalization candidate handoff with explicit adoption and treatment gates.

Explicitly invoked. Not wired into the default reconcile/standardize pipeline.
Provisional construction from qualified observations is separate from production
admission. Human grouping and treatment judgments are recorded as supplied
decisions, never as facts established by technical validation.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping, Sequence

from ..data.interface import LineItem, StandardizedFinancials
from ..data.line_identity import line_identity
from ..model.normalization import (
    NORMALIZATION_TREATMENTS,
    SUPPORTED_NORMALIZATION_SCOPE,
)

AUTHORIZED_IS_IDENTITIES: tuple[str, ...] = (
    "income_statement||impairment of goodwill and other assets|impairment_and_restructuring",
    "income_statement||impairment of goodwill and other assets, restructuring costs|impairment_and_restructuring",
    "income_statement||impairment of assets and restructuring costs|impairment_and_restructuring",
)
CF_AUDIT_IDENTITIES: tuple[str, ...] = (
    "cash_flow|cash flows from operating activities|impairment of goodwill and other assets|impairment_and_restructuring",
    "cash_flow|cash flows from operating activities|impairment of goodwill and other assets, restructuring costs|impairment_and_restructuring",
    "cash_flow|cash flows from operating activities|impairment of assets and restructuring costs|impairment_and_restructuring",
)
GEO_AUDIT_IDENTITY = "segment.geo.q4_2023.ifop_reconciling.impairment_and_restructuring"
LEDGER_PERIODS: tuple[str, ...] = (
    "2022-01-30",
    "2023-01-29",
    "2024-01-28",
    "2025-02-02",
    "2026-02-01",
)
ANALYTICAL_CONCEPT = "analytical_is_impairment_restructuring_aggregate"
ANALYTICAL_LABEL = "Impairment and restructuring costs (provisional analytical aggregate)"
ANALYTICAL_SELECTOR = f"concept:{ANALYTICAL_CONCEPT}"
SIGN_TRANSFORMATION = "analytical_amount = -reported_face_expense"
AUTHORIZATION_SYNTHETIC = "synthetic"
AUTHORIZATION_INDEPENDENT = "independently_supplied"
_STUDIO_MARKERS = ("studio", "obsolescence")
_TECHNICAL_EQUIVALENCE_MARKERS = (
    "matching concept",
    "same suggested_concept",
    "agreeing amounts",
    "agreeing overlapping",
    "boolean approval",
)


@dataclass(frozen=True)
class AdoptionRecord:
    """Supplied grouping decision. Technical validation cannot establish it."""

    company: str
    axis: tuple[str, ...]
    member_identities: tuple[str, ...]
    analytical_concept: str
    analytical_label: str
    source_evidence_fingerprints: tuple[str, ...]
    mapping_decision: str
    decision_authority: str
    rationale: str
    analytical_scope: str
    decision_status: str
    authorization_kind: str
    approved: bool | None = None
    equivalent_by_concept: bool = False
    equivalent_by_agreeing_amounts: bool = False


@dataclass(frozen=True)
class TreatmentRecord:
    """Supplied treatment decision required before a candidate configuration."""

    scope: str
    reference_treatment: str
    rationale: str
    consequence_note: str
    aggregate_or_component: str
    cogs_boundary: str
    deductibility: str
    etr_disposition: str
    topic: str = "impairment_and_restructuring"


@dataclass(frozen=True)
class PeriodConstruction:
    period: str
    n_is_observations: int
    row_identities: tuple[str, ...]
    labels: tuple[str, ...]
    sections: tuple[str, ...]
    roles: tuple[str, ...]
    source_files: tuple[str, ...]
    source_hashes: tuple[str, ...]
    physical_pages: tuple[int, ...]
    printed_pages: tuple[Any, ...]
    face_reported_usd_thousands: int
    analytical_amount_usd_thousands: int
    transformation: str
    sign_conversions_applied: int
    face_retained_unchanged: bool
    explicit_nil: bool
    missing: bool
    zero_filled: bool
    observation_fingerprints: tuple[str, ...]
    studio_cogs_included: bool
    grouping_is_accepted_source_fact: bool


@dataclass(frozen=True)
class GateFailure:
    admitted: bool
    gate: str
    reason: str
    period: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConstructionResult:
    constructed: bool
    mapping_status: str
    grouping_is_accepted_source_fact: bool
    production_activation_authorized: bool
    gate: str
    reason: str
    face_series: tuple[int, ...]
    analytical_series: tuple[int, ...]
    periods: tuple[PeriodConstruction, ...]
    member_identities: tuple[str, ...]
    axis: tuple[str, ...]
    line: LineItem | None
    used_fingerprints: tuple[str, ...]
    failure: GateFailure | None = None


@dataclass(frozen=True)
class HandoffResult:
    constructed: bool
    production_admitted: bool
    real_company_acceptance: bool
    mapping_status: str
    grouping_is_accepted_source_fact: bool
    blocked_reason: str | None
    gate: str | None
    face_series: tuple[int, ...]
    analytical_series: tuple[int, ...]
    periods: tuple[PeriodConstruction, ...]
    constructed_line: LineItem | None
    constructed_financials: StandardizedFinancials | None
    candidate_configuration: dict[str, str] | None
    after_tax_available: bool
    authorization_kind: str | None
    tax_disposition: str | None
    note_tax_effects_attributed: bool


def observation_fingerprint(obs: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(obs), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def printed_page_lookup_from_evidence(evidence: Mapping[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for check in evidence.get("pdf_page_checks") or []:
        printed = check.get("printed_page") or {}
        out[(str(check["source_file"]), int(check["physical_page"]))] = {
            "printed_page": printed.get("resolved"),
            "printed_status": printed.get("status"),
        }
    return out


def _attach_pages(
    obs: Mapping[str, Any],
    page_lookup: Mapping[tuple[str, int], Mapping[str, Any]] | None,
) -> dict[str, Any]:
    row = dict(obs)
    lookup = page_lookup or {}
    info = lookup.get((str(obs.get("source_file") or ""), int(obs.get("pdf_page") or 0)), {})
    row["physical_page"] = obs.get("pdf_page")
    row["printed_page"] = info.get("printed_page")
    row["printed_page_status"] = info.get("printed_status")
    return row


def _is_studio(obs: Mapping[str, Any]) -> bool:
    blob = " ".join(
        str(obs.get(key) or "")
        for key in ("row_identity", "label", "suggested_concept", "section")
    ).casefold()
    return all(marker in blob for marker in _STUDIO_MARKERS) or "studio_obsolescence" in blob


def _failure(gate: str, reason: str, period: str | None = None, **detail: Any) -> ConstructionResult:
    fail = GateFailure(admitted=False, gate=gate, reason=reason, period=period, detail=detail)
    return ConstructionResult(
        constructed=False,
        mapping_status="blocked",
        grouping_is_accepted_source_fact=False,
        production_activation_authorized=False,
        gate=gate,
        reason=reason,
        face_series=(),
        analytical_series=(),
        periods=(),
        member_identities=(),
        axis=(),
        line=None,
        used_fingerprints=(),
        failure=fail,
    )


def _membership_set_rejection(
    member_identities: Sequence[str],
    *,
    allow_cf_members: bool,
) -> ConstructionResult | None:
    for ident in member_identities:
        blob = ident.casefold()
        if "studio" in blob and "obsolescence" in blob:
            return _failure(
                "duplicate_use",
                "studio_cogs_excluded",
                unauthorized=[ident],
            )
        if ident.startswith("cash_flow|") and not allow_cf_members:
            return _failure(
                "statement_identity",
                "cash_flow_substitution_forbidden",
                unauthorized=[ident],
            )
        if ident.startswith("segment."):
            return _failure(
                "statement_identity",
                "geographic_reprint_not_a_member",
                unauthorized=[ident],
            )
        if "component" in blob:
            return _failure(
                "duplicate_use",
                "aggregate_and_component_double_count",
                unauthorized=[ident],
            )
        if ident not in AUTHORIZED_IS_IDENTITIES:
            return _failure(
                "unauthorized_identity",
                "unauthorized_identity_membership",
                unauthorized=[ident],
            )
    return None


def _face_amount(value: object) -> int:
    return int(value)


def construct_provisional_candidate(
    observations: Sequence[Mapping[str, Any]],
    *,
    member_identities: Sequence[str] = AUTHORIZED_IS_IDENTITIES,
    axis: Sequence[str] = LEDGER_PERIODS,
    bound_source_hashes: Mapping[str, str],
    page_lookup: Mapping[tuple[str, int], Mapping[str, Any]] | None = None,
    sign_conversion: str = "once",
    allow_cf_members: bool = False,
) -> ConstructionResult:
    """Build the analytical series from qualified observations only.

    Does not fill missing periods, invent chronology, or treat grouping as a
    source fact. Sign conversion is once-only: analytical_amount = -face.
    """
    identities = tuple(member_identities)
    periods_axis = tuple(axis)
    membership_block = _membership_set_rejection(
        identities, allow_cf_members=allow_cf_members
    )
    if membership_block is not None:
        return membership_block

    if sign_conversion == "absent":
        sign_conversions = 0
    elif sign_conversion == "repeated":
        sign_conversions = 2
    elif sign_conversion == "once":
        sign_conversions = 1
    else:
        return _failure("sign_conversion", "absent_sign_conversion", sign_conversions=sign_conversion)

    used: set[str] = set()
    period_rows: list[PeriodConstruction] = []
    fingerprints: list[str] = []
    for period in periods_axis:
        members = [
            _attach_pages(obs, page_lookup)
            for obs in observations
            if obs.get("period") == period and obs.get("row_identity") in identities
        ]
        for obs in members:
            ident = str(obs.get("row_identity") or "")
            if ident.startswith("cash_flow|") and not allow_cf_members:
                return _failure(
                    "statement_identity",
                    "cash_flow_substitution_forbidden",
                    period,
                )
            if ident.startswith("segment.") or obs.get("kind") == "supplemental":
                return _failure(
                    "statement_identity",
                    "geographic_reprint_not_a_member",
                    period,
                )
            if _is_studio(obs):
                return _failure("duplicate_use", "studio_cogs_excluded", period)
            if obs.get("currency") != "USD" or obs.get("unit_scale") != "thousands":
                return _failure(
                    "currency_unit",
                    "currency_or_unit_mismatch",
                    period,
                    currency=obs.get("currency"),
                    unit_scale=obs.get("unit_scale"),
                )
            declared = obs.get("source_sha256_declared")
            expected_hash = bound_source_hashes.get(str(obs.get("source_file") or ""))
            if not expected_hash or declared != expected_hash:
                return _failure(
                    "source_binding",
                    "altered_or_unbound_source_hash",
                    period,
                    source_file=obs.get("source_file"),
                    declared=declared,
                    expected=expected_hash,
                )
            fp = observation_fingerprint(obs)
            if fp in used:
                return _failure(
                    "duplicate_use",
                    "observation_used_more_than_once",
                    period,
                    fingerprint=fp,
                )
            used.add(fp)
            fingerprints.append(fp)

        unauthorized = sorted(
            {
                str(obs.get("row_identity"))
                for obs in members
                if obs.get("row_identity") not in identities
            }
        )
        if unauthorized:
            return _failure(
                "unauthorized_identity",
                "unauthorized_identity_membership",
                period,
                unauthorized=unauthorized,
            )
        if not members:
            return _failure(
                "complete_axis",
                "missing_period_evidence",
                period,
                missing_filled_with_zero=False,
            )
        distinct = sorted({_face_amount(obs["value"]) for obs in members})
        if len(distinct) != 1:
            return _failure(
                "unique_selection",
                "conflicting_overlapping_observations",
                period,
                distinct_values=distinct,
                n_observations=len(members),
            )
        if sign_conversions != 1:
            return _failure(
                "sign_conversion",
                (
                    "absent_sign_conversion"
                    if sign_conversions < 1
                    else "repeated_sign_conversion"
                ),
                period,
                sign_conversions=sign_conversions,
            )
        face = distinct[0]
        analytical = -int(face)
        printed = tuple(
            obs.get("printed_page") for obs in members if obs.get("printed_page") is not None
        )
        period_rows.append(
            PeriodConstruction(
                period=period,
                n_is_observations=len(members),
                row_identities=tuple(sorted({str(obs["row_identity"]) for obs in members})),
                labels=tuple(sorted({str(obs["label"]) for obs in members})),
                sections=tuple(sorted({str(obs.get("section") or "") for obs in members})),
                roles=tuple(sorted({str(obs["presentation_role"]) for obs in members})),
                source_files=tuple(sorted({str(obs["source_file"]) for obs in members})),
                source_hashes=tuple(sorted({str(obs["source_sha256_declared"]) for obs in members})),
                physical_pages=tuple(sorted({int(obs["pdf_page"]) for obs in members})),
                printed_pages=printed,
                face_reported_usd_thousands=face,
                analytical_amount_usd_thousands=analytical,
                transformation=SIGN_TRANSFORMATION,
                sign_conversions_applied=1,
                face_retained_unchanged=True,
                explicit_nil=face == 0,
                missing=False,
                zero_filled=False,
                observation_fingerprints=tuple(observation_fingerprint(obs) for obs in members),
                studio_cogs_included=False,
                grouping_is_accepted_source_fact=False,
            )
        )

    values = {
        date.fromisoformat(row.period): float(row.analytical_amount_usd_thousands)
        for row in period_rows
    }
    line = LineItem(
        label=ANALYTICAL_LABEL,
        concept=ANALYTICAL_CONCEPT,
        values=values,
    )
    return ConstructionResult(
        constructed=True,
        mapping_status="provisional_equivalence_unresolved",
        grouping_is_accepted_source_fact=False,
        production_activation_authorized=False,
        gate="all_passed",
        reason="provisional_technical_feasibility_only",
        face_series=tuple(row.face_reported_usd_thousands for row in period_rows),
        analytical_series=tuple(row.analytical_amount_usd_thousands for row in period_rows),
        periods=tuple(period_rows),
        member_identities=identities,
        axis=periods_axis,
        line=line,
        used_fingerprints=tuple(fingerprints),
    )


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _cites_technical_equivalence(*parts: object) -> bool:
    blob = " ".join(str(part or "") for part in parts).casefold()
    return any(marker in blob for marker in _TECHNICAL_EQUIVALENCE_MARKERS)


def evaluate_adoption(
    adoption: AdoptionRecord | None,
    construction: ConstructionResult,
    financials: StandardizedFinancials,
) -> tuple[str | None, str]:
    """Return (blocked_reason, gate) or (None, passed_gate)."""
    if adoption is None:
        return "absent_adoption", "adoption"
    required = (
        adoption.company,
        adoption.mapping_decision,
        adoption.decision_authority,
        adoption.rationale,
        adoption.decision_status,
        adoption.authorization_kind,
        adoption.analytical_scope,
    )
    if any(_blank(item) for item in required):
        return "absent_adoption", "adoption"
    if not adoption.axis or not adoption.member_identities or not adoption.source_evidence_fingerprints:
        return "absent_adoption", "adoption"
    if adoption.decision_status.casefold() == "provisional":
        return "provisional_adoption", "adoption"
    if adoption.approved is not None:
        return "contradictory_adoption", "adoption"
    if adoption.equivalent_by_concept or adoption.equivalent_by_agreeing_amounts:
        return "contradictory_adoption", "adoption"
    if _cites_technical_equivalence(adoption.mapping_decision, adoption.rationale):
        return "contradictory_adoption", "adoption"
    if adoption.decision_status.casefold() != "adopted":
        return "provisional_adoption", "adoption"
    if "provisional" in adoption.mapping_decision.casefold():
        return "contradictory_adoption", "adoption"
    company_tokens = {
        str(financials.ticker or "").strip(),
        str(financials.company_name or "").strip(),
    }
    if adoption.company not in company_tokens:
        return "mismatched_adoption", "adoption"
    if tuple(adoption.axis) != tuple(construction.axis):
        return "mismatched_adoption", "adoption"
    if tuple(adoption.member_identities) != tuple(construction.member_identities):
        return "mismatched_adoption", "adoption"
    if adoption.analytical_concept != ANALYTICAL_CONCEPT:
        return "mismatched_adoption", "adoption"
    if adoption.analytical_label != ANALYTICAL_LABEL:
        return "mismatched_adoption", "adoption"
    if adoption.analytical_scope != SUPPORTED_NORMALIZATION_SCOPE:
        return "mismatched_adoption", "adoption"
    expected = set(construction.used_fingerprints)
    supplied = set(adoption.source_evidence_fingerprints)
    if supplied != expected:
        if supplied & expected and supplied != expected:
            return "stale_adoption", "adoption"
        return "stale_adoption", "adoption"
    if adoption.authorization_kind not in {AUTHORIZATION_SYNTHETIC, AUTHORIZATION_INDEPENDENT}:
        return "mismatched_adoption", "adoption"
    return None, "adoption_passed"


def evaluate_treatment(
    treatment: TreatmentRecord | None,
    adoption: AdoptionRecord,
) -> tuple[str | None, str, bool]:
    """Return (blocked_reason, gate, after_tax_available)."""
    if treatment is None:
        return "absent_treatment", "treatment", False
    if _blank(treatment.rationale):
        return "missing_treatment_rationale", "treatment", False
    if _blank(treatment.consequence_note):
        return "missing_treatment_consequence", "treatment", False
    if _blank(treatment.scope) or _blank(treatment.reference_treatment):
        return "unresolved_recurring_treatment", "treatment", False
    if _blank(treatment.aggregate_or_component) or _blank(treatment.cogs_boundary):
        return "unresolved_scope", "treatment", False
    if treatment.scope != SUPPORTED_NORMALIZATION_SCOPE:
        return "conflicting_scope", "treatment", False
    if treatment.scope != adoption.analytical_scope:
        return "conflicting_scope", "treatment", False
    if treatment.reference_treatment not in NORMALIZATION_TREATMENTS:
        return "unresolved_recurring_treatment", "treatment", False
    if treatment.aggregate_or_component not in {"aggregate", "component"}:
        return "unresolved_scope", "treatment", False
    if treatment.cogs_boundary not in {"exclude_studio_cogs", "include_studio_cogs"}:
        return "unresolved_scope", "treatment", False
    if treatment.cogs_boundary == "include_studio_cogs":
        return "unresolved_scope", "treatment", False
    if treatment.aggregate_or_component != "aggregate":
        return "unresolved_scope", "treatment", False
    tax_resolved = (
        not _blank(treatment.deductibility)
        and not _blank(treatment.etr_disposition)
        and treatment.deductibility.casefold() != "unresolved"
        and treatment.etr_disposition.casefold() != "unresolved"
    )
    after_tax_available = tax_resolved and treatment.etr_disposition == "operating_etr"
    return None, "treatment_passed", after_tax_available


def _already_contains_analytical_line(financials: StandardizedFinancials) -> bool:
    return any(
        line_identity(item).concept == ANALYTICAL_CONCEPT
        for item in financials.income_statement
    )


def _insert_constructed_line(
    financials: StandardizedFinancials,
    line: LineItem,
) -> StandardizedFinancials:
    isolated = copy.deepcopy(financials)
    isolated.income_statement = list(isolated.income_statement)
    isolated.income_statement.append(
        LineItem(label=line.label, concept=line.concept, values=dict(line.values))
    )
    return isolated


def _candidate_configuration(treatment: TreatmentRecord) -> dict[str, str]:
    return {
        "selector": ANALYTICAL_SELECTOR,
        "referenceTreatment": treatment.reference_treatment,
        "scope": treatment.scope,
        "topic": treatment.topic,
        "referenceRationale": treatment.rationale,
        "consequenceNote": treatment.consequence_note,
    }


def run_normalization_candidate_handoff(
    observations: Sequence[Mapping[str, Any]],
    financials: StandardizedFinancials,
    *,
    bound_source_hashes: Mapping[str, str],
    page_lookup: Mapping[tuple[str, int], Mapping[str, Any]] | None = None,
    member_identities: Sequence[str] = AUTHORIZED_IS_IDENTITIES,
    axis: Sequence[str] = LEDGER_PERIODS,
    sign_conversion: str = "once",
    allow_cf_members: bool = False,
    adoption: AdoptionRecord | None = None,
    treatment: TreatmentRecord | None = None,
) -> HandoffResult:
    """Explicit gated handoff. Mutates neither observations nor ``financials``."""
    original_n = len(financials.income_statement)
    construction = construct_provisional_candidate(
        observations,
        member_identities=member_identities,
        axis=axis,
        bound_source_hashes=bound_source_hashes,
        page_lookup=page_lookup,
        sign_conversion=sign_conversion,
        allow_cf_members=allow_cf_members,
    )
    if not construction.constructed or construction.line is None:
        assert len(financials.income_statement) == original_n
        return HandoffResult(
            constructed=False,
            production_admitted=False,
            real_company_acceptance=False,
            mapping_status="blocked",
            grouping_is_accepted_source_fact=False,
            blocked_reason=construction.reason,
            gate=construction.gate,
            face_series=(),
            analytical_series=(),
            periods=(),
            constructed_line=None,
            constructed_financials=None,
            candidate_configuration=None,
            after_tax_available=False,
            authorization_kind=None,
            tax_disposition=None,
            note_tax_effects_attributed=False,
        )

    if _already_contains_analytical_line(financials):
        assert len(financials.income_statement) == original_n
        return HandoffResult(
            constructed=True,
            production_admitted=False,
            real_company_acceptance=False,
            mapping_status="blocked",
            grouping_is_accepted_source_fact=False,
            blocked_reason="repeated_admission",
            gate="production",
            face_series=construction.face_series,
            analytical_series=construction.analytical_series,
            periods=construction.periods,
            constructed_line=construction.line,
            constructed_financials=None,
            candidate_configuration=None,
            after_tax_available=False,
            authorization_kind=None,
            tax_disposition=None,
            note_tax_effects_attributed=False,
        )

    isolated = _insert_constructed_line(financials, construction.line)
    assert len(financials.income_statement) == original_n

    adoption_block, adoption_gate = evaluate_adoption(adoption, construction, financials)
    if adoption_block is not None:
        return HandoffResult(
            constructed=True,
            production_admitted=False,
            real_company_acceptance=False,
            mapping_status=construction.mapping_status,
            grouping_is_accepted_source_fact=False,
            blocked_reason=adoption_block,
            gate=adoption_gate,
            face_series=construction.face_series,
            analytical_series=construction.analytical_series,
            periods=construction.periods,
            constructed_line=construction.line,
            constructed_financials=isolated,
            candidate_configuration=None,
            after_tax_available=False,
            authorization_kind=getattr(adoption, "authorization_kind", None),
            tax_disposition=None,
            note_tax_effects_attributed=False,
        )

    assert adoption is not None
    treatment_block, treatment_gate, after_tax_available = evaluate_treatment(
        treatment, adoption
    )
    if treatment_block is not None:
        return HandoffResult(
            constructed=True,
            production_admitted=False,
            real_company_acceptance=False,
            mapping_status=construction.mapping_status,
            grouping_is_accepted_source_fact=False,
            blocked_reason=treatment_block,
            gate=treatment_gate,
            face_series=construction.face_series,
            analytical_series=construction.analytical_series,
            periods=construction.periods,
            constructed_line=construction.line,
            constructed_financials=isolated,
            candidate_configuration=None,
            after_tax_available=False,
            authorization_kind=adoption.authorization_kind,
            tax_disposition=getattr(treatment, "etr_disposition", None),
            note_tax_effects_attributed=False,
        )

    assert treatment is not None
    real_acceptance = adoption.authorization_kind == AUTHORIZATION_INDEPENDENT
    mapping_status = (
        "synthetic_test_authorization"
        if adoption.authorization_kind == AUTHORIZATION_SYNTHETIC
        else "independently_supplied_decision"
    )
    return HandoffResult(
        constructed=True,
        production_admitted=True,
        real_company_acceptance=real_acceptance,
        mapping_status=mapping_status,
        grouping_is_accepted_source_fact=False,
        blocked_reason=None,
        gate="production_admitted",
        face_series=construction.face_series,
        analytical_series=construction.analytical_series,
        periods=construction.periods,
        constructed_line=construction.line,
        constructed_financials=isolated,
        candidate_configuration=_candidate_configuration(treatment),
        after_tax_available=after_tax_available,
        authorization_kind=adoption.authorization_kind,
        tax_disposition=treatment.etr_disposition,
        note_tax_effects_attributed=False,
    )
