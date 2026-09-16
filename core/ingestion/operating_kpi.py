"""Source-grounded operating-KPI supplemental identities and selection."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from ..data.filing import PresentationRole
from ..data.historical_operating_kpis import (
    validate_operating_kpi_fact,
    is_operating_kpi_fact_type,
    split_operating_kpi_identity,
)
from .filing_reconciler import (
    ROLE_RANK,
    SelectedOperatingKpiFact,
    SupplementalObservation,
)

_ELIGIBLE_ROLES = {
    PresentationRole.CURRENT_PERIOD.value,
    PresentationRole.COMPARATIVE.value,
    PresentationRole.RESTATED_COMPARATIVE.value,
}
_PRIOR_ROLE = PresentationRole.PRIOR_PRESENTATION.value


def _role_rank(role: str) -> int:
    return ROLE_RANK[PresentationRole(role)]


def _reason(
    observations: list[SupplementalObservation],
    eligible: list[SupplementalObservation],
    selected: SupplementalObservation,
) -> str:
    if (
        selected.fact.presentation_role == PresentationRole.RESTATED_COMPARATIVE.value
        and any(
            obs.fact.presentation_role != selected.fact.presentation_role
            for obs in eligible
        )
    ):
        return "restated_comparative_precedence"
    if any(
        obs.fact.presentation_role == _PRIOR_ROLE
        and obs.filing_year > selected.filing_year
        for obs in observations
    ):
        return "excluded_newer_prior_presentation"
    if len(eligible) == 1:
        return "sole_source_observation"
    values = {float(obs.fact.value) for obs in eligible}
    if len(values) == 1:
        years = {obs.filing_year for obs in eligible}
        if len(years) == 1:
            return "agreeing_observations"
    return "later_audited_presentation"


def _selected_payload(
    obs: SupplementalObservation,
    *,
    reason: str,
) -> SelectedOperatingKpiFact:
    metric, population = split_operating_kpi_identity(obs.fact.fact_type)
    return SelectedOperatingKpiFact(
        fact_type=obs.fact.fact_type,
        metric=metric,
        population=population,
        period=obs.fact.period,
        value=float(obs.fact.value),
        unit=obs.fact.unit,
        filing_year=obs.filing_year,
        source_file=obs.source_file,
        source_sha256=obs.source_sha256,
        pdf_page=obs.fact.source.page,
        presentation_basis=obs.fact.presentation_role,
        selection_reason=reason,
        source_note=obs.fact.source.note,
        source_label=obs.fact.source.label,
    )


def _winner_sort_key(obs: SupplementalObservation) -> tuple:
    return (obs.source_file, obs.fact.source.page, obs.source_sha256)


def _select_eligible(
    observations: list[SupplementalObservation],
    *,
    period: date,
    fact_type: str,
) -> tuple[SupplementalObservation, list[SupplementalObservation], str]:
    eligible = [
        obs
        for obs in observations
        if obs.fact.presentation_role in _ELIGIBLE_ROLES
    ]
    if not eligible:
        raise ValueError(
            "no eligible operating-KPI observation for "
            f"{fact_type} {period.isoformat()}"
        )
    top_rank = max(_role_rank(obs.fact.presentation_role) for obs in eligible)
    ranked = [
        obs for obs in eligible if _role_rank(obs.fact.presentation_role) == top_rank
    ]
    top_year = max(obs.filing_year for obs in ranked)
    winners = [obs for obs in ranked if obs.filing_year == top_year]
    distinct = {float(obs.fact.value) for obs in winners}
    if len(distinct) > 1:
        raise ValueError(
            "unresolved equal-priority operating-KPI contradiction for "
            f"{fact_type} {period.isoformat()}"
        )
    winner = sorted(winners, key=_winner_sort_key)[0]
    return winner, eligible, _reason(observations, eligible, winner)


def select_operating_kpi_facts(
    note_facts: tuple[SupplementalObservation, ...],
) -> tuple[SelectedOperatingKpiFact, ...]:
    """Select eligible operating-KPI observations; fail closed."""
    kpi: list[SupplementalObservation] = []
    seen_in_filing: set[tuple[int, str, str, date]] = set()
    for obs in note_facts:
        if not is_operating_kpi_fact_type(obs.fact.fact_type):
            continue
        validate_operating_kpi_fact(obs.fact)
        key = (
            obs.filing_year,
            obs.source_file,
            obs.fact.fact_type,
            obs.fact.period,
        )
        if key in seen_in_filing:
            raise ValueError(
                "duplicate operating-KPI identity "
                f"{obs.fact.fact_type} for {obs.fact.period.isoformat()}"
            )
        seen_in_filing.add(key)
        kpi.append(obs)
    if not kpi:
        return ()

    buckets: dict[tuple[str, date], list[SupplementalObservation]] = defaultdict(list)
    for obs in kpi:
        buckets[(obs.fact.fact_type, obs.fact.period)].append(obs)

    selected: list[SelectedOperatingKpiFact] = []
    for fact_type, period in sorted(buckets, key=lambda item: (item[0], item[1].isoformat())):
        winner, _eligible, reason = _select_eligible(
            buckets[(fact_type, period)],
            period=period,
            fact_type=fact_type,
        )
        selected.append(_selected_payload(winner, reason=reason))
    return tuple(selected)
