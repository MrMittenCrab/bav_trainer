"""Model-facing geographic segment contract and fail-closed validation."""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable

from .interface import HistoricalSegmentData, HistoricalSegmentPeriod, LineItem, StandardizedFinancials

GEOGRAPHIC_SEGMENT_NAMESPACE = "segment.geo.q4_2023"
SEGMENT_BRIDGE_TOLERANCE = 0.0

FAMILY_CORPORATE = "corporate_column"
FAMILY_ITEMIZED = "itemized_reconciling"
SUPPORTED_FAMILIES = frozenset({FAMILY_CORPORATE, FAMILY_ITEMIZED})

OP_ADD = "add"
OP_SUBTRACT = "subtract"
SUPPORTED_OPERATIONS = frozenset({OP_ADD, OP_SUBTRACT})

SEGMENTS = ("americas", "china_mainland", "rest_of_world")
REVENUE_SEGMENTS = tuple(f"net_revenue.{name}" for name in SEGMENTS)
IFOP_SEGMENTS = tuple(f"income_from_operations.{name}" for name in SEGMENTS)
REVENUE_CONSOLIDATED = "net_revenue.consolidated"
REVENUE_SEGMENT_TOTAL = "net_revenue.segment_total"
IFOP_CONSOLIDATED = "income_from_operations.consolidated"
IFOP_SEGMENT_TOTAL = "income_from_operations.segment_total"
IFOP_CORPORATE = "income_from_operations.corporate_unallocated"

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

REQUIRED_REVENUE = (*REVENUE_SEGMENTS, REVENUE_CONSOLIDATED)
REQUIRED_IFOP = (*IFOP_SEGMENTS, IFOP_CONSOLIDATED)
_PREFIX = GEOGRAPHIC_SEGMENT_NAMESPACE + "."


def geographic_identity(fact_type: str) -> str:
    """Return the local identity; reject non-Q4-2023 geographic namespaces."""
    if fact_type.startswith("segment.") and not fact_type.startswith(_PREFIX):
        raise ValueError(
            "incompatible segment definition mixed with "
            f"{GEOGRAPHIC_SEGMENT_NAMESPACE}: {fact_type!r}"
        )
    if not fact_type.startswith(_PREFIX):
        raise ValueError(
            f"unknown {GEOGRAPHIC_SEGMENT_NAMESPACE} identity: {fact_type!r}"
        )
    identity = fact_type[len(_PREFIX) :]
    if identity not in ALLOWED_IDENTITIES:
        raise ValueError(
            f"unknown {GEOGRAPHIC_SEGMENT_NAMESPACE} identity: {fact_type!r}"
        )
    return identity


def require_finite_number(identity: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"geographic identity {identity} has a non-numeric value")
    amount = float(value)
    if not math.isfinite(amount):
        raise ValueError(f"geographic identity {identity} has a non-finite value")
    return amount


def expected_bridge_operations(
    family: str,
    identities: Iterable[str],
) -> dict[str, str]:
    present = set(identities)
    if family == FAMILY_CORPORATE:
        if IFOP_CORPORATE not in present:
            raise ValueError("incomplete geographic IFOP bridge group")
        if present & ITEMIZED_RECONCILERS:
            raise ValueError(
                "corporate double counting: corporate_unallocated IFOP and "
                "itemized reconciling items are both present"
            )
        return {IFOP_CORPORATE: OP_ADD}
    if family == FAMILY_ITEMIZED:
        reconcilers = present & ITEMIZED_RECONCILERS
        if not reconcilers:
            raise ValueError("incomplete geographic IFOP bridge group")
        if IFOP_CORPORATE in present:
            raise ValueError(
                "corporate double counting: corporate_unallocated IFOP and "
                "itemized reconciling items are both present"
            )
        return {name: OP_SUBTRACT for name in sorted(reconcilers)}
    raise ValueError(f"unsupported geographic presentation_family: {family!r}")


def _within_tolerance(left: float, right: float) -> bool:
    return abs(left - right) <= SEGMENT_BRIDGE_TOLERANCE


def _require_complete_group(values: dict[str, float], *, period: date) -> None:
    missing = [name for name in (*REQUIRED_REVENUE, *REQUIRED_IFOP) if name not in values]
    if missing:
        raise ValueError(
            f"incomplete geographic bridge group for {period.isoformat()}: "
            + ", ".join(missing)
        )


def _apply_operations(
    snapshot: HistoricalSegmentPeriod,
    base: float,
) -> float:
    total = base
    for identity, operation in snapshot.bridge_operations.items():
        if identity not in snapshot.values:
            raise ValueError(
                f"geographic bridge operation {identity} missing a reported value "
                f"for {snapshot.period.isoformat()}"
            )
        if operation not in SUPPORTED_OPERATIONS:
            raise ValueError(
                f"unsupported geographic bridge operation {operation!r} for {identity}"
            )
        amount = snapshot.values[identity]
        if operation == OP_ADD:
            total += amount
        else:
            total -= amount
    return total


def _validate_bridges(snapshot: HistoricalSegmentPeriod) -> None:
    revenue_sum = sum(snapshot.values[name] for name in REVENUE_SEGMENTS)
    consolidated_rev = snapshot.values[REVENUE_CONSOLIDATED]
    if not _within_tolerance(revenue_sum, consolidated_rev):
        raise ValueError(
            f"geographic revenue bridge mismatch for "
            f"{snapshot.period.isoformat()}: {revenue_sum} != {consolidated_rev}"
        )
    if REVENUE_SEGMENT_TOTAL in snapshot.values:
        segment_rev = snapshot.values[REVENUE_SEGMENT_TOTAL]
        if not _within_tolerance(revenue_sum, segment_rev):
            raise ValueError(
                f"geographic revenue segment_total mismatch for "
                f"{snapshot.period.isoformat()}"
            )

    segment_ifop = sum(snapshot.values[name] for name in IFOP_SEGMENTS)
    consolidated_ifop = snapshot.values[IFOP_CONSOLIDATED]
    if IFOP_SEGMENT_TOTAL in snapshot.values:
        reported_total = snapshot.values[IFOP_SEGMENT_TOTAL]
        if not _within_tolerance(segment_ifop, reported_total):
            raise ValueError(
                f"geographic IFOP segment_total mismatch for "
                f"{snapshot.period.isoformat()}"
            )
    bridged = _apply_operations(snapshot, segment_ifop)
    if not _within_tolerance(bridged, consolidated_ifop):
        raise ValueError(
            f"geographic IFOP bridge mismatch for "
            f"{snapshot.period.isoformat()}: {bridged} != {consolidated_ifop}"
        )


def _concept_value(items: list[LineItem], concept: str, period: date) -> float:
    matches = [item for item in items if (item.concept or "") == concept]
    if len(matches) != 1:
        raise ValueError(
            f"geographic IS cross-check requires exactly one selected "
            f"{concept} fact for {period.isoformat()}"
        )
    if period not in matches[0].values:
        raise ValueError(
            f"geographic IS cross-check missing {concept} for {period.isoformat()}"
        )
    return require_finite_number(concept, matches[0].values[period])


def _cross_check_is(snapshot: HistoricalSegmentPeriod, income_statement: list[LineItem]) -> None:
    note_rev = snapshot.values[REVENUE_CONSOLIDATED]
    note_ifop = snapshot.values[IFOP_CONSOLIDATED]
    is_rev = _concept_value(income_statement, "revenue", snapshot.period)
    is_ifop = _concept_value(income_statement, "operating_income", snapshot.period)
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


def _validate_snapshot(
    snapshot: HistoricalSegmentPeriod,
    *,
    model_periods: set[date],
    seen_periods: set[date],
    income_statement: list[LineItem],
) -> None:
    if not isinstance(snapshot.period, date):
        raise ValueError("historical_segment period must be a date")
    if snapshot.period in seen_periods:
        raise ValueError(
            f"duplicate geographic period {snapshot.period.isoformat()}"
        )
    seen_periods.add(snapshot.period)
    if snapshot.period not in model_periods:
        raise ValueError(
            f"geographic period {snapshot.period.isoformat()} is outside the model axis"
        )
    if snapshot.presentation_family not in SUPPORTED_FAMILIES:
        raise ValueError(
            "unsupported geographic presentation_family: "
            f"{snapshot.presentation_family!r}"
        )
    if not isinstance(snapshot.values, dict) or not snapshot.values:
        raise ValueError(
            f"geographic values missing for {snapshot.period.isoformat()}"
        )
    if not isinstance(snapshot.bridge_operations, dict):
        raise ValueError(
            f"geographic bridge_operations must be an object for "
            f"{snapshot.period.isoformat()}"
        )
    checked: dict[str, float] = {}
    for identity, value in snapshot.values.items():
        if identity not in ALLOWED_IDENTITIES:
            raise ValueError(
                f"unknown {GEOGRAPHIC_SEGMENT_NAMESPACE} identity: {identity!r}"
            )
        if identity in checked:
            raise ValueError(
                f"duplicate geographic identity {identity} for "
                f"{snapshot.period.isoformat()}"
            )
        checked[identity] = require_finite_number(identity, value)
    expected = expected_bridge_operations(snapshot.presentation_family, checked)
    if dict(snapshot.bridge_operations) != expected:
        raise ValueError(
            "geographic bridge operations contradict presentation family "
            f"for {snapshot.period.isoformat()}"
        )
    _require_complete_group(checked, period=snapshot.period)
    normalized = HistoricalSegmentPeriod(
        period=snapshot.period,
        presentation_family=snapshot.presentation_family,
        values=checked,
        bridge_operations=dict(expected),
    )
    _validate_bridges(normalized)
    _cross_check_is(normalized, income_statement)


def validate_historical_segment_data(
    data: HistoricalSegmentData,
    *,
    model_periods: Iterable[date],
    income_statement: list[LineItem],
) -> None:
    """Reject malformed supplied geographic payloads; absence is handled by callers."""
    if data.namespace != GEOGRAPHIC_SEGMENT_NAMESPACE:
        raise ValueError(
            f"unsupported geographic namespace: {data.namespace!r}"
        )
    if not isinstance(data.periods, list) or not data.periods:
        raise ValueError("historical_segment.periods must be a non-empty list")
    axis = set(model_periods)
    seen: set[date] = set()
    for snapshot in data.periods:
        if not isinstance(snapshot, HistoricalSegmentPeriod):
            raise ValueError("historical_segment.periods entries must be snapshots")
        _validate_snapshot(
            snapshot,
            model_periods=axis,
            seen_periods=seen,
            income_statement=income_statement,
        )


def validate_historical_segment(fin: StandardizedFinancials) -> None:
    """Validate a supplied segment payload against the parent financials."""
    if fin.historical_segment is None:
        return
    validate_historical_segment_data(
        fin.historical_segment,
        model_periods=fin.period_dates(),
        income_statement=fin.income_statement,
    )
