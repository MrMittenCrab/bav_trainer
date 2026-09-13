"""Deterministic historical diluted-WAS share-basis resolution (Step 9M.3D).

Builds a complete comparable diluted weighted-average share axis from reconciled
share facts. Accepts reported diluted WAS or derived diluted WAS whose derivation
is exactly ``basic_weighted_average_shares + dilutive_shares``. When the same
historical period is later restated after a stock split, infers one integer split
factor only from overlapping share observations anchored by an audited
``RESTATED_COMPARATIVE`` diluted-EPS selection.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from math import isclose

from ..data.filing import PresentationRole
from .filing_reconciler import ReconciledCompanyData, SupplementalObservation

DERIVED_DILUTED_WAS_DERIVATION = "basic_weighted_average_shares + dilutive_shares"
# Two-decimal EPS presentation can drift slightly vs exact share factor.
_EPS_RATIO_ABS_TOL = 0.05


@dataclass(frozen=True)
class HistoricalShareBasisResolution:
    diluted_weighted_average_actual_shares: dict[date, float]
    applied_adjustment_factors: dict[date, float]
    basis: str  # "reported" | "split_adjusted"
    restatement_anchor_period: date | None
    restatement_filing_year: int | None
    split_factor: float | None


def _share_obs(
    reconciled: ReconciledCompanyData,
    *,
    fact_type: str,
    period: date,
    filing_year: int | None = None,
    status: str | None = None,
) -> list[SupplementalObservation]:
    out: list[SupplementalObservation] = []
    for obs in reconciled.share_facts:
        if obs.kind != "share":
            continue
        if obs.fact.fact_type != fact_type:
            continue
        if obs.fact.period != period:
            continue
        if filing_year is not None and obs.filing_year != filing_year:
            continue
        if status is not None and obs.fact.status != status:
            continue
        out.append(obs)
    return out


def _valid_diluted_was_observation(
    reconciled: ReconciledCompanyData,
    obs: SupplementalObservation,
) -> bool:
    """Return True when a diluted-WAS observation is eligible for the model axis."""
    fact = obs.fact
    if fact.fact_type != "diluted_weighted_average_shares":
        return False
    if fact.status == "reported":
        return True
    if fact.status != "derived":
        return False
    if fact.derivation != DERIVED_DILUTED_WAS_DERIVATION:
        return False
    basics = _share_obs(
        reconciled,
        fact_type="basic_weighted_average_shares",
        period=fact.period,
        filing_year=obs.filing_year,
        status="reported",
    )
    dilutives = _share_obs(
        reconciled,
        fact_type="dilutive_shares",
        period=fact.period,
        filing_year=obs.filing_year,
        status="reported",
    )
    if not basics or not dilutives:
        return False
    basic_vals = {float(item.fact.value) for item in basics}
    dilutive_vals = {float(item.fact.value) for item in dilutives}
    if len(basic_vals) != 1 or len(dilutive_vals) != 1:
        return False
    expected = next(iter(basic_vals)) + next(iter(dilutive_vals))
    return isclose(float(fact.value), expected, rel_tol=0.0, abs_tol=1e-6)


def _diluted_was_by_period(
    reconciled: ReconciledCompanyData,
) -> dict[date, list[SupplementalObservation]] | None:
    """Collect eligible diluted-WAS observations; None if any period is incomplete."""
    by_period: dict[date, list[SupplementalObservation]] = {
        period: [] for period in reconciled.periods
    }
    for obs in reconciled.share_facts:
        if obs.kind != "share":
            continue
        if obs.fact.fact_type != "diluted_weighted_average_shares":
            continue
        if obs.fact.period not in by_period:
            continue
        if not _valid_diluted_was_observation(reconciled, obs):
            # Invalid derived/unsupported observation: treat as unavailable for axis.
            continue
        by_period[obs.fact.period].append(obs)
    for period in reconciled.periods:
        if not by_period[period]:
            return None
    return by_period


def _unique_value(observations: list[SupplementalObservation]) -> float | None:
    values = {float(obs.fact.value) for obs in observations}
    if len(values) != 1:
        return None
    return next(iter(values))


def _integer_factor(old: float, new: float) -> float | None:
    if old <= 0 or new <= 0 or new <= old:
        return None
    ratio = new / old
    rounded = round(ratio)
    if rounded < 2:
        return None
    if not isclose(ratio, float(rounded), rel_tol=0.0, abs_tol=1e-9):
        return None
    return float(rounded)


def _diluted_eps_restatement_anchor(
    reconciled: ReconciledCompanyData,
    period: date,
) -> tuple[float, float, int] | None:
    """Return (old_eps, restated_eps, restatement_filing_year) when anchored."""
    candidates = [
        value
        for value in reconciled.values
        if value.period == period
        and (
            value.suggested_concept == "diluted_eps"
            or value.row_identity.endswith("|diluted_eps")
        )
    ]
    for value in candidates:
        if value.selected.presentation_role != PresentationRole.RESTATED_COMPARATIVE:
            continue
        restated = float(value.selected.value)
        restatement_year = int(value.selected.filing_year)
        priors = [
            obs
            for obs in value.observations
            if obs.filing_year < restatement_year
        ]
        if not priors:
            continue
        current_priors = [
            obs
            for obs in priors
            if obs.presentation_role == PresentationRole.CURRENT_PERIOD
        ]
        old_obs = (
            max(current_priors, key=lambda obs: obs.filing_year)
            if current_priors
            else max(priors, key=lambda obs: obs.filing_year)
        )
        return float(old_obs.value), restated, restatement_year
    return None


def _unique_side_value(values: list[float]) -> float | None:
    distinct = set(values)
    if len(distinct) != 1:
        return None
    return next(iter(distinct))


def _components_support_factor(
    reconciled: ReconciledCompanyData,
    period: date,
    restatement_year: int,
    factor: float,
) -> bool:
    """Require reported basic/dilutive presentations not contradict the diluted factor.

    All available same-side reported values must agree. When both sides exist,
    opposite-side values must reconcile to ``factor``. Zero/zero is allowed;
    zero/nonzero is rejected.
    """
    for fact_type in ("basic_weighted_average_shares", "dilutive_shares"):
        observations = _share_obs(
            reconciled,
            fact_type=fact_type,
            period=period,
            status="reported",
        )
        if not observations:
            continue
        pre = [
            float(obs.fact.value)
            for obs in observations
            if obs.filing_year < restatement_year
        ]
        post = [
            float(obs.fact.value)
            for obs in observations
            if obs.filing_year >= restatement_year
        ]
        if pre:
            old_v = _unique_side_value(pre)
            if old_v is None:
                return False
        else:
            old_v = None
        if post:
            new_v = _unique_side_value(post)
            if new_v is None:
                return False
        else:
            new_v = None
        if old_v is None or new_v is None:
            continue
        if old_v == 0.0 and new_v == 0.0:
            continue
        if old_v <= 0.0 or new_v <= 0.0:
            return False
        if not isclose(new_v / old_v, factor, rel_tol=0.0, abs_tol=1e-9):
            return False
    return True


def _period_sides_support_factor(
    observations: list[SupplementalObservation],
    restatement_year: int,
    factor: float,
) -> bool:
    """Require one consistent pre and post value; when both exist, post = pre × factor."""
    pre = [
        float(obs.fact.value)
        for obs in observations
        if obs.filing_year < restatement_year
    ]
    post = [
        float(obs.fact.value)
        for obs in observations
        if obs.filing_year >= restatement_year
    ]
    pre_v = _unique_side_value(pre) if pre else None
    post_v = _unique_side_value(post) if post else None
    if pre and pre_v is None:
        return False
    if post and post_v is None:
        return False
    if pre_v is not None and post_v is not None:
        return isclose(post_v, pre_v * factor, rel_tol=0.0, abs_tol=1e-9)
    return True


def _eps_supports_factor(old_eps: float, new_eps: float, factor: float) -> bool:
    if new_eps == 0.0:
        return False
    return abs(old_eps / new_eps - factor) <= _EPS_RATIO_ABS_TOL


def resolve_historical_share_basis(
    reconciled: ReconciledCompanyData,
) -> HistoricalShareBasisResolution | None:
    """Resolve a complete comparable diluted-WAS axis, or None if unsupported."""
    by_period = _diluted_was_by_period(reconciled)
    if by_period is None:
        return None

    disagreeing: dict[date, list[SupplementalObservation]] = {}
    unique: dict[date, float] = {}
    for period, observations in by_period.items():
        value = _unique_value(observations)
        if value is None:
            disagreeing[period] = observations
        else:
            unique[period] = value

    if not disagreeing:
        # No split/restatement disagreement — use the unique eligible axis as reported.
        axis = {period: unique[period] for period in reconciled.periods}
        if any(v <= 0.0 for v in axis.values()):
            return None
        return HistoricalShareBasisResolution(
            diluted_weighted_average_actual_shares=axis,
            applied_adjustment_factors={period: 1.0 for period in reconciled.periods},
            basis="reported",
            restatement_anchor_period=None,
            restatement_filing_year=None,
            split_factor=None,
        )

    # Restatement path: one integer factor from audited same-period disagreement(s).
    inferred_factor: float | None = None
    anchor_period: date | None = None
    restatement_year: int | None = None
    restated_was_by_period: dict[date, float] = {}
    pre_restatement_was_by_period: dict[date, float] = {}

    for period, observations in disagreeing.items():
        eps_anchor = _diluted_eps_restatement_anchor(reconciled, period)
        if eps_anchor is None:
            return None
        old_eps, new_eps, filing_year = eps_anchor

        by_year: dict[int, list[float]] = defaultdict(list)
        for obs in observations:
            by_year[obs.filing_year].append(float(obs.fact.value))
        # Collapse to unique value per filing year.
        year_values: dict[int, float] = {}
        for year, vals in by_year.items():
            if len(set(vals)) != 1:
                return None
            year_values[year] = vals[0]

        pre_years = [y for y in year_values if y < filing_year]
        post_years = [y for y in year_values if y >= filing_year]
        if not pre_years or not post_years:
            return None
        pre_vals = {year_values[y] for y in pre_years}
        post_vals = {year_values[y] for y in post_years}
        if len(pre_vals) != 1 or len(post_vals) != 1:
            return None
        old_was = next(iter(pre_vals))
        new_was = next(iter(post_vals))
        factor = _integer_factor(old_was, new_was)
        if factor is None:
            return None
        if not _eps_supports_factor(old_eps, new_eps, factor):
            return None
        if not _components_support_factor(reconciled, period, filing_year, factor):
            return None
        if inferred_factor is None:
            inferred_factor = factor
            anchor_period = period
            restatement_year = filing_year
        elif inferred_factor != factor:
            return None
        elif filing_year != restatement_year:
            # Multiple restatement events / filing anchors are unsupported in 9M.3D.
            return None
        restated_was_by_period[period] = new_was
        pre_restatement_was_by_period[period] = old_was

    if inferred_factor is None or anchor_period is None or restatement_year is None:
        return None

    # Reject any same-period presentation group that contradicts the audited factor
    # before selecting axis values (including restated_was periods).
    for period in reconciled.periods:
        if not _period_sides_support_factor(
            by_period[period], restatement_year, inferred_factor
        ):
            return None
        if not _components_support_factor(
            reconciled, period, restatement_year, inferred_factor
        ):
            return None

    axis: dict[date, float] = {}
    factors: dict[date, float] = {}
    for period in reconciled.periods:
        observations = by_period[period]
        if period in restated_was_by_period:
            axis[period] = restated_was_by_period[period]
            factors[period] = 1.0
            continue

        # Prefer a presentation from the restatement filing year or later.
        post = [
            float(obs.fact.value)
            for obs in observations
            if obs.filing_year >= restatement_year
        ]
        if post:
            post_v = _unique_side_value(post)
            if post_v is None:
                return None
            axis[period] = post_v
            factors[period] = 1.0
            continue

        # Earlier period with only pre-restatement presentation → analytical × factor.
        pre = [
            float(obs.fact.value)
            for obs in observations
            if obs.filing_year < restatement_year
        ]
        if not pre:
            return None
        pre_v = _unique_side_value(pre)
        if pre_v is None:
            return None
        axis[period] = pre_v * inferred_factor
        factors[period] = inferred_factor

    if any(v <= 0.0 for v in axis.values()):
        return None
    if set(axis) != set(reconciled.periods):
        return None

    return HistoricalShareBasisResolution(
        diluted_weighted_average_actual_shares={
            period: axis[period] for period in reconciled.periods
        },
        applied_adjustment_factors={
            period: factors[period] for period in reconciled.periods
        },
        basis="split_adjusted",
        restatement_anchor_period=anchor_period,
        restatement_filing_year=restatement_year,
        split_factor=inferred_factor,
    )


UNIT_SCALE_DIVISORS = {
    "ones": 1.0,
    "thousands": 1_000.0,
    "millions": 1_000_000.0,
    "billions": 1_000_000_000.0,
}


def unit_scale_divisor(unit_scale: str) -> float:
    if unit_scale not in UNIT_SCALE_DIVISORS:
        raise ValueError(f"unsupported unit_scale {unit_scale!r}")
    return UNIT_SCALE_DIVISORS[unit_scale]
