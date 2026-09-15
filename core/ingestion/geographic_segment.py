"""Q4-2023 geographic segment supplemental identities and selection."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from ..data.filing import PresentationRole
from .filing_reconciler import (
    ReconciledValue,
    SelectedGeographicFact,
    SupplementalObservation,
)

GEO_NAMESPACE = "segment.geo.q4_2023"
GEO_PREFIX = GEO_NAMESPACE + "."
GEO_BRIDGE_TOLERANCE = 0.0

SEGMENTS = ("americas", "china_mainland", "rest_of_world")
REVENUE_SEGMENTS = tuple(f"net_revenue.{name}" for name in SEGMENTS)
IFOP_SEGMENTS = tuple(f"income_from_operations.{name}" for name in SEGMENTS)

REVENUE_CONSOLIDATED = "net_revenue.consolidated"
REVENUE_SEGMENT_TOTAL = "net_revenue.segment_total"
IFOP_CONSOLIDATED = "income_from_operations.consolidated"
IFOP_SEGMENT_TOTAL = "income_from_operations.segment_total"
IFOP_CORPORATE = "income_from_operations.corporate_unallocated"

# Reported signs are preserved. The itemized note subtracts each reconciling
# line as printed: positive expenses reduce IFOP; parenthetical gains (negative
# reported values) increase IFOP when subtracted.
ITEMIZED_RECONCILERS = frozenset(
    {
        "ifop_reconciling.general_corporate_expenses",
        "ifop_reconciling.studio_obsolescence_provision",
        "ifop_reconciling.impairment_and_restructuring",
        "ifop_reconciling.amortization_of_intangible_assets",
        "ifop_reconciling.acquisition_related_expenses",
        "ifop_reconciling.gain_on_disposal_of_assets",
    }
)

ALLOWED_IDENTITIES = frozenset(
    {
        *REVENUE_SEGMENTS,
        REVENUE_CONSOLIDATED,
        REVENUE_SEGMENT_TOTAL,
        *IFOP_SEGMENTS,
        IFOP_CONSOLIDATED,
        IFOP_SEGMENT_TOTAL,
        IFOP_CORPORATE,
        *ITEMIZED_RECONCILERS,
    }
)

_REQUIRED_REVENUE = (*REVENUE_SEGMENTS, REVENUE_CONSOLIDATED)
_REQUIRED_IFOP = (*IFOP_SEGMENTS, IFOP_CONSOLIDATED)
_VALID_ROLES = {role.value for role in PresentationRole}


@dataclass(frozen=True)
class _Snapshot:
    period: date
    filing_year: int
    source_file: str
    source_sha256: str
    facts: dict[str, SupplementalObservation]
    family: str


def is_geographic_fact_type(fact_type: str) -> bool:
    return fact_type.startswith(GEO_PREFIX)


def geographic_identity(fact_type: str) -> str:
    if not is_geographic_fact_type(fact_type):
        raise ValueError(f"not a geographic fact_type: {fact_type!r}")
    return fact_type[len(GEO_PREFIX) :]


def _local(obs: SupplementalObservation) -> str:
    return geographic_identity(obs.fact.fact_type)


def _validate_observation(obs: SupplementalObservation) -> str:
    fact = obs.fact
    if not is_geographic_fact_type(fact.fact_type):
        if fact.fact_type.startswith("segment."):
            raise ValueError(
                "incompatible segment definition mixed with "
                f"{GEO_NAMESPACE}: {fact.fact_type!r}"
            )
        raise ValueError(f"not a geographic fact_type: {fact.fact_type!r}")
    identity = geographic_identity(fact.fact_type)
    if identity not in ALLOWED_IDENTITIES:
        raise ValueError(
            f"unknown {GEO_NAMESPACE} identity: {fact.fact_type!r}"
        )
    if fact.status != "reported":
        raise ValueError(
            f"geographic fact {fact.fact_type} must have status=reported"
        )
    if fact.source.page <= 0:
        raise ValueError(
            f"geographic fact {fact.fact_type} missing positive source page"
        )
    if fact.presentation_role not in _VALID_ROLES:
        raise ValueError(
            f"geographic fact {fact.fact_type} missing valid presentation_role"
        )
    if isinstance(fact.value, bool) or not isinstance(fact.value, (int, float)):
        raise ValueError(f"geographic fact {fact.fact_type} has a non-numeric value")
    if not math.isfinite(float(fact.value)):
        raise ValueError(f"geographic fact {fact.fact_type} has a non-finite value")
    return identity


def _signed_reconciler(identity: str, value: float) -> float:
    del identity
    return -float(value)


def _values(snapshot: _Snapshot, identities: Iterable[str]) -> list[float]:
    return [float(snapshot.facts[name].fact.value) for name in identities]


def _within_tolerance(left: float, right: float) -> bool:
    return abs(left - right) <= GEO_BRIDGE_TOLERANCE


def _classify_family(facts: dict[str, SupplementalObservation]) -> str:
    has_corporate = IFOP_CORPORATE in facts
    reconcilers = [name for name in facts if name in ITEMIZED_RECONCILERS]
    if has_corporate and reconcilers:
        raise ValueError(
            "corporate double counting: corporate_unallocated IFOP and "
            "itemized reconciling items are both present"
        )
    if has_corporate:
        return "corporate_column"
    if reconcilers:
        return "itemized_reconciling"
    raise ValueError("incomplete geographic IFOP bridge group")


def _require_complete(facts: dict[str, SupplementalObservation], *, period: date) -> None:
    missing = [
        name
        for name in (*_REQUIRED_REVENUE, *_REQUIRED_IFOP)
        if name not in facts
    ]
    if missing:
        raise ValueError(
            f"incomplete geographic bridge group for {period.isoformat()}: "
            + ", ".join(missing)
        )
    _classify_family(facts)


def _validate_bridges(snapshot: _Snapshot) -> None:
    revenue_sum = sum(_values(snapshot, REVENUE_SEGMENTS))
    consolidated_rev = float(snapshot.facts[REVENUE_CONSOLIDATED].fact.value)
    if not _within_tolerance(revenue_sum, consolidated_rev):
        raise ValueError(
            f"geographic revenue bridge mismatch for "
            f"{snapshot.period.isoformat()}: {revenue_sum} != {consolidated_rev}"
        )
    if REVENUE_SEGMENT_TOTAL in snapshot.facts:
        segment_rev = float(snapshot.facts[REVENUE_SEGMENT_TOTAL].fact.value)
        if not _within_tolerance(revenue_sum, segment_rev):
            raise ValueError(
                f"geographic revenue segment_total mismatch for "
                f"{snapshot.period.isoformat()}"
            )

    segment_ifop = sum(_values(snapshot, IFOP_SEGMENTS))
    consolidated_ifop = float(snapshot.facts[IFOP_CONSOLIDATED].fact.value)
    if IFOP_SEGMENT_TOTAL in snapshot.facts:
        reported_total = float(snapshot.facts[IFOP_SEGMENT_TOTAL].fact.value)
        if not _within_tolerance(segment_ifop, reported_total):
            raise ValueError(
                f"geographic IFOP segment_total mismatch for "
                f"{snapshot.period.isoformat()}"
            )

    if snapshot.family == "corporate_column":
        corporate = float(snapshot.facts[IFOP_CORPORATE].fact.value)
        bridged = segment_ifop + corporate
    else:
        bridged = segment_ifop + sum(
            _signed_reconciler(name, obs.fact.value)
            for name, obs in snapshot.facts.items()
            if name in ITEMIZED_RECONCILERS
        )
    if not _within_tolerance(bridged, consolidated_ifop):
        raise ValueError(
            f"geographic IFOP bridge mismatch for "
            f"{snapshot.period.isoformat()}: {bridged} != {consolidated_ifop}"
        )


def _concept_value(
    values: tuple[ReconciledValue, ...],
    *,
    concept: str,
    period: date,
) -> float:
    matches = [
        row
        for row in values
        if row.suggested_concept == concept and row.period == period
    ]
    if len(matches) != 1:
        raise ValueError(
            f"geographic IS cross-check requires exactly one selected "
            f"{concept} fact for {period.isoformat()}"
        )
    return float(matches[0].selected.value)


def _cross_check_is(
    snapshot: _Snapshot,
    *,
    values: tuple[ReconciledValue, ...],
    model_periods: tuple[date, ...],
) -> None:
    if snapshot.period not in model_periods:
        return
    note_rev = float(snapshot.facts[REVENUE_CONSOLIDATED].fact.value)
    note_ifop = float(snapshot.facts[IFOP_CONSOLIDATED].fact.value)
    is_rev = _concept_value(values, concept="revenue", period=snapshot.period)
    is_ifop = _concept_value(
        values, concept="operating_income", period=snapshot.period
    )
    if not _within_tolerance(note_rev, is_rev):
        raise ValueError(
            f"geographic consolidated revenue {note_rev} disagrees with "
            f"IS revenue {is_rev} for {snapshot.period.isoformat()}"
        )
    if not _within_tolerance(note_ifop, is_ifop):
        raise ValueError(
            f"geographic consolidated IFOP {note_ifop} disagrees with "
            f"IS operating_income {is_ifop} for {snapshot.period.isoformat()}"
        )


def _reason(snapshots: list[_Snapshot], selected: _Snapshot) -> str:
    if len(snapshots) == 1:
        return "sole_source_observation"
    return "later_audited_presentation"


def _selected_payload(
    snapshot: _Snapshot,
    identity: str,
    reason: str,
) -> SelectedGeographicFact:
    obs = snapshot.facts[identity]
    return SelectedGeographicFact(
        fact_type=obs.fact.fact_type,
        period=obs.fact.period,
        value=float(obs.fact.value),
        filing_year=snapshot.filing_year,
        source_file=snapshot.source_file,
        source_sha256=snapshot.source_sha256,
        pdf_page=obs.fact.source.page,
        presentation_basis=obs.fact.presentation_role,
        selection_reason=reason,
        presentation_family=snapshot.family,
        source_note=obs.fact.source.note,
        source_label=obs.fact.source.label,
    )


def select_geographic_segment_facts(
    note_facts: tuple[SupplementalObservation, ...],
    *,
    reconciled_values: tuple[ReconciledValue, ...],
    model_periods: tuple[date, ...],
) -> tuple[SelectedGeographicFact, ...]:
    """Select later-audited Q4-2023 geographic snapshots; fail closed."""
    geo: list[SupplementalObservation] = []
    other_segment: list[SupplementalObservation] = []
    for obs in note_facts:
        fact_type = obs.fact.fact_type
        if is_geographic_fact_type(fact_type):
            _validate_observation(obs)
            geo.append(obs)
        elif fact_type.startswith("segment."):
            other_segment.append(obs)
    if geo and other_segment:
        raise ValueError(
            "incompatible segment definition mixed with "
            f"{GEO_NAMESPACE}: {other_segment[0].fact.fact_type!r}"
        )
    if not geo:
        return ()

    buckets: dict[tuple[date, int, str], list[SupplementalObservation]] = defaultdict(
        list
    )
    for obs in geo:
        buckets[(obs.fact.period, obs.filing_year, obs.source_file)].append(obs)

    snapshots_by_period: dict[date, list[_Snapshot]] = defaultdict(list)
    for (period, filing_year, source_file), items in sorted(buckets.items()):
        facts: dict[str, SupplementalObservation] = {}
        for obs in items:
            identity = _local(obs)
            if identity in facts:
                existing = facts[identity]
                if float(existing.fact.value) != float(obs.fact.value):
                    raise ValueError(
                        "duplicate conflicting geographic identity "
                        f"{obs.fact.fact_type} for {period.isoformat()}"
                    )
                raise ValueError(
                    "duplicate geographic identity "
                    f"{obs.fact.fact_type} for {period.isoformat()}"
                )
            facts[identity] = obs
        _require_complete(facts, period=period)
        family = _classify_family(facts)
        snapshot = _Snapshot(
            period=period,
            filing_year=filing_year,
            source_file=source_file,
            source_sha256=items[0].source_sha256,
            facts=facts,
            family=family,
        )
        _validate_bridges(snapshot)
        snapshots_by_period[period].append(snapshot)

    selected: list[SelectedGeographicFact] = []
    for period in sorted(snapshots_by_period):
        candidates = sorted(
            snapshots_by_period[period],
            key=lambda snap: (snap.filing_year, snap.source_file),
        )
        top_year = max(snap.filing_year for snap in candidates)
        winners = [snap for snap in candidates if snap.filing_year == top_year]
        if len(winners) != 1:
            raise ValueError(
                "unresolved equal-priority geographic contradiction for "
                f"{period.isoformat()}"
            )
        winner = winners[0]
        _cross_check_is(
            winner,
            values=reconciled_values,
            model_periods=model_periods,
        )
        reason = _reason(candidates, winner)
        for identity in sorted(winner.facts):
            selected.append(_selected_payload(winner, identity, reason))
    return tuple(selected)
