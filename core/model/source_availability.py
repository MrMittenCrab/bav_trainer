"""Generic concept/period source-availability assessment.

Uses shared resolver precedence and source-value validation. Distinguishes
absent lines and missing period values from reported zero. Ambiguity and
malformed evidence still raise. Mathematically undefined ratios remain
``#N/A`` and are not treated as source-unavailable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Mapping, Sequence, TypeVar

TSpec = TypeVar("TSpec")

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import resolve_line
from .ratio_values import SOURCE_UNAVAILABLE, is_source_unavailable

REASON_AVAILABLE = "available"
REASON_ABSENT_LINE = "absent_line"
REASON_MISSING_PERIOD_VALUE = "missing_period_value"
REASON_DEPENDENT_UNAVAILABLE = "dependent_unavailable"

INTEREST_CONCEPTS = ("interest_expense", "interest_income")
SUPPORTED_UNDEFINED_RATIO_COD_FALLBACK = 0.04


@dataclass(frozen=True)
class PeriodAvailability:
    concept: str
    period: date
    available: bool
    reason: str
    missing_concepts: tuple[str, ...] = ()
    missing_periods: tuple[date, ...] = ()


@dataclass(frozen=True)
class ConceptAvailability:
    concept: str
    line_present: bool
    periods: tuple[PeriodAvailability, ...]

    def for_period(self, period: date) -> PeriodAvailability:
        for row in self.periods:
            if row.period == period:
                return row
        raise KeyError(f"{self.concept}: no availability row for {period.isoformat()}")

    def available_on(self, period: date) -> bool:
        return self.for_period(period).available


@dataclass(frozen=True)
class OutputAvailability:
    output: str
    period: date | None
    available: bool
    reason: str
    missing_concepts: tuple[str, ...] = ()
    missing_periods: tuple[date, ...] = ()


@dataclass(frozen=True)
class InterestAvailability:
    interest_expense: ConceptAvailability
    interest_income: ConceptAvailability
    outputs: tuple[OutputAvailability, ...]

    def output(self, name: str, period: date | None = None) -> OutputAvailability:
        matches = [
            row
            for row in self.outputs
            if row.output == name and row.period == period
        ]
        if not matches:
            raise KeyError(f"No availability row for {name!r} period={period}")
        if len(matches) != 1:
            raise ValueError(f"Ambiguous availability rows for {name!r} period={period}")
        return matches[0]

    def missing_records(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for concept_avail in (self.interest_expense, self.interest_income):
            for row in concept_avail.periods:
                if row.available:
                    continue
                records.append(
                    {
                        "kind": "concept",
                        "concept": row.concept,
                        "period": row.period.isoformat(),
                        "reason": row.reason,
                        "missing_concepts": list(row.missing_concepts),
                        "missing_periods": [p.isoformat() for p in row.missing_periods],
                    }
                )
        for row in self.outputs:
            if row.available:
                continue
            records.append(
                {
                    "kind": "output",
                    "output": row.output,
                    "period": None if row.period is None else row.period.isoformat(),
                    "reason": row.reason,
                    "missing_concepts": list(row.missing_concepts),
                    "missing_periods": [p.isoformat() for p in row.missing_periods],
                }
            )
        return records


def assess_concept_availability(
    items: list[LineItem],
    concept: str,
    periods: list[date],
) -> ConceptAvailability:
    """Assess one concept across modeled periods.

    Ambiguous resolution and invalid stored values raise. A reported zero is
    available. An absent line or a missing/None period value is not.
    """
    resolved = resolve_line(items, concept, required=False)
    if resolved.item is None:
        return ConceptAvailability(
            concept=concept,
            line_present=False,
            periods=tuple(
                PeriodAvailability(
                    concept=concept,
                    period=period,
                    available=False,
                    reason=REASON_ABSENT_LINE,
                    missing_concepts=(concept,),
                    missing_periods=(period,),
                )
                for period in periods
            ),
        )

    rows: list[PeriodAvailability] = []
    for period in periods:
        raw = resolved.item.values.get(period)
        if raw is None:
            rows.append(
                PeriodAvailability(
                    concept=concept,
                    period=period,
                    available=False,
                    reason=REASON_MISSING_PERIOD_VALUE,
                    missing_concepts=(concept,),
                    missing_periods=(period,),
                )
            )
            continue
        try:
            number = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid source value for {concept} period {period.isoformat()}: {raw!r}"
            ) from exc
        if not math.isfinite(number):
            raise ValueError(
                f"invalid source value for {concept} period {period.isoformat()}: {raw!r}"
            )
        rows.append(
            PeriodAvailability(
                concept=concept,
                period=period,
                available=True,
                reason=REASON_AVAILABLE,
            )
        )
    return ConceptAvailability(concept=concept, line_present=True, periods=tuple(rows))


def historical_average_after_tax_cod(
    comparable_cod: Sequence[object],
    *,
    interest_history_available: bool,
) -> float | str:
    """Average comparable after-tax CoD values under shared eligibility.

    Opening-period interest is not a comparable CoD input. Any comparable CoD
    that is source-unavailable makes the aggregate unavailable. Numeric
    comparable ratios are averaged; undefined ratios are skipped. When no
    numeric comparable ratio exists, supported interest history uses the
    existing 4% undefined-ratio fallback; unavailable history does not.
    """
    numeric_cod = [
        value for value in comparable_cod if isinstance(value, (int, float))
    ]
    if any(is_source_unavailable(value) for value in comparable_cod) or (
        not numeric_cod and not interest_history_available
    ):
        return SOURCE_UNAVAILABLE
    if numeric_cod:
        return sum(numeric_cod) / len(numeric_cod)
    return SUPPORTED_UNDEFINED_RATIO_COD_FALLBACK


def comparable_interest_history_available(
    comparable_cod: Sequence[object],
    net_interest: Sequence[object],
) -> bool:
    """Whether required CoD history has interest; opening absence is ignored."""
    series = comparable_cod if comparable_cod else net_interest
    return not any(is_source_unavailable(value) for value in series)


def assess_aggregate_cod_availability(
    comparable_cod: Sequence[OutputAvailability],
    net_interest_by_period: Mapping[date, OutputAvailability],
    periods: Sequence[date],
) -> OutputAvailability:
    """Gate hist-avg CoD by comparable-period interest, not opening absence."""
    if comparable_cod:
        required: Sequence[OutputAvailability] = comparable_cod
    elif periods:
        required = (net_interest_by_period[periods[0]],)
    else:
        return OutputAvailability(
            output="hist_avg_after_tax_cod",
            period=None,
            available=True,
            reason=REASON_AVAILABLE,
        )
    missing_concepts: list[str] = []
    missing_periods: list[date] = []
    reasons: list[str] = []
    for row in required:
        if row.available:
            continue
        missing_concepts.extend(row.missing_concepts)
        missing_periods.extend(row.missing_periods)
        reasons.append(row.reason)
    if not missing_concepts:
        return OutputAvailability(
            output="hist_avg_after_tax_cod",
            period=None,
            available=True,
            reason=REASON_AVAILABLE,
        )
    unique_concepts = tuple(dict.fromkeys(missing_concepts))
    unique_periods = tuple(dict.fromkeys(missing_periods))
    reason = reasons[0] if len(set(reasons)) == 1 else REASON_DEPENDENT_UNAVAILABLE
    return OutputAvailability(
        output="hist_avg_after_tax_cod",
        period=None,
        available=False,
        reason=reason,
        missing_concepts=unique_concepts,
        missing_periods=unique_periods,
    )


def _combine_period_facts(
    output: str,
    period: date | None,
    facts: Sequence[PeriodAvailability],
) -> OutputAvailability:
    missing_concepts: list[str] = []
    missing_periods: list[date] = []
    reasons: list[str] = []
    for fact in facts:
        if fact.available:
            continue
        missing_concepts.extend(fact.missing_concepts)
        missing_periods.extend(fact.missing_periods)
        reasons.append(fact.reason)
    if not missing_concepts:
        return OutputAvailability(
            output=output,
            period=period,
            available=True,
            reason=REASON_AVAILABLE,
        )
    unique_concepts = tuple(dict.fromkeys(missing_concepts))
    unique_periods = tuple(dict.fromkeys(missing_periods))
    reason = reasons[0] if len(set(reasons)) == 1 else REASON_DEPENDENT_UNAVAILABLE
    return OutputAvailability(
        output=output,
        period=period,
        available=False,
        reason=reason,
        missing_concepts=unique_concepts,
        missing_periods=unique_periods,
    )


def assess_interest_availability(
    financials: StandardizedFinancials,
    periods: list[date],
) -> InterestAvailability:
    """Assess interest sources and every interest-dependent historical output."""
    expense = assess_concept_availability(
        financials.income_statement, "interest_expense", periods
    )
    income = assess_concept_availability(
        financials.income_statement, "interest_income", periods
    )
    outputs: list[OutputAvailability] = []
    net_interest_by_period: dict[date, OutputAvailability] = {}
    for period in periods:
        net_interest = _combine_period_facts(
            "net_interest",
            period,
            (expense.for_period(period), income.for_period(period)),
        )
        net_interest_by_period[period] = net_interest
        outputs.append(net_interest)
        niat = OutputAvailability(
            output="net_interest_after_tax",
            period=period,
            available=net_interest.available,
            reason=net_interest.reason,
            missing_concepts=net_interest.missing_concepts,
            missing_periods=net_interest.missing_periods,
        )
        outputs.append(niat)
        nopat = OutputAvailability(
            output="nopat",
            period=period,
            available=net_interest.available,
            reason=(
                REASON_AVAILABLE
                if net_interest.available
                else REASON_DEPENDENT_UNAVAILABLE
            ),
            missing_concepts=net_interest.missing_concepts,
            missing_periods=net_interest.missing_periods,
        )
        outputs.append(nopat)
        outputs.append(
            OutputAvailability(
                output="nopat_margin",
                period=period,
                available=nopat.available,
                reason=nopat.reason,
                missing_concepts=nopat.missing_concepts,
                missing_periods=nopat.missing_periods,
            )
        )

    comparable = periods[1:]
    for period in comparable:
        nopat = next(
            row
            for row in outputs
            if row.output == "nopat" and row.period == period
        )
        niat = next(
            row
            for row in outputs
            if row.output == "net_interest_after_tax" and row.period == period
        )
        for name, parent in (
            ("rnoa", nopat),
            ("after_tax_cod", niat),
        ):
            outputs.append(
                OutputAvailability(
                    output=name,
                    period=period,
                    available=parent.available,
                    reason=parent.reason,
                    missing_concepts=parent.missing_concepts,
                    missing_periods=parent.missing_periods,
                )
            )
        rnoa = outputs[-2]
        cod = outputs[-1]
        spread_available = rnoa.available and cod.available
        spread_missing_c = tuple(
            dict.fromkeys([*rnoa.missing_concepts, *cod.missing_concepts])
        )
        spread_missing_p = tuple(
            dict.fromkeys([*rnoa.missing_periods, *cod.missing_periods])
        )
        spread = OutputAvailability(
            output="spread",
            period=period,
            available=spread_available,
            reason=REASON_AVAILABLE if spread_available else REASON_DEPENDENT_UNAVAILABLE,
            missing_concepts=spread_missing_c,
            missing_periods=spread_missing_p,
        )
        outputs.append(spread)
        outputs.append(
            OutputAvailability(
                output="roe_decomp",
                period=period,
                available=spread.available,
                reason=spread.reason,
                missing_concepts=spread.missing_concepts,
                missing_periods=spread.missing_periods,
            )
        )

    comparable_cod = [row for row in outputs if row.output == "after_tax_cod"]
    outputs.append(
        assess_aggregate_cod_availability(
            comparable_cod, net_interest_by_period, periods
        )
    )
    return InterestAvailability(
        interest_expense=expense,
        interest_income=income,
        outputs=tuple(outputs),
    )


def filter_available_specs(
    specs: Sequence[TSpec],
    series_by_family: Mapping[str, Sequence[object]],
) -> tuple[TSpec, ...]:
    """Drop concrete specs whose expected series value is source-unavailable."""
    kept: list[TSpec] = []
    for spec in specs:
        family_id = getattr(spec, "family_id", None)
        period_index = getattr(spec, "period_index", None)
        if family_id is None or period_index is None:
            kept.append(spec)
            continue
        series = series_by_family.get(family_id)
        if series is None:
            kept.append(spec)
            continue
        if is_source_unavailable(series[period_index]):
            continue
        kept.append(spec)
    return tuple(kept)


def availability_payload(
    availability: InterestAvailability,
) -> dict[str, object]:
    """JSON-ready availability documentation for sidecars."""
    return {
        "source_unavailable_status": SOURCE_UNAVAILABLE,
        "interest_expense": {
            "line_present": availability.interest_expense.line_present,
            "periods": [
                {
                    "period": row.period.isoformat(),
                    "available": row.available,
                    "reason": row.reason,
                    "missing_concepts": list(row.missing_concepts),
                    "missing_periods": [p.isoformat() for p in row.missing_periods],
                }
                for row in availability.interest_expense.periods
            ],
        },
        "interest_income": {
            "line_present": availability.interest_income.line_present,
            "periods": [
                {
                    "period": row.period.isoformat(),
                    "available": row.available,
                    "reason": row.reason,
                    "missing_concepts": list(row.missing_concepts),
                    "missing_periods": [p.isoformat() for p in row.missing_periods],
                }
                for row in availability.interest_income.periods
            ],
        },
        "unavailable": availability.missing_records(),
    }
