"""Historical cash roll-forward from reported cash-flow totals.

Optional, source-gated module. Resolves unique explicit CF operating,
investing and financing totals, FX effect, opening cash, closing cash and
reported cash change. Stored concepts, values, signs, and provenance are
left unchanged. No label fallback, no balance-sheet cash substitution, and
no competing-alias merge.

Computes ``cash_movement_from_flows = CFO + CFI + CFF + FX`` when those
four unique sources resolve. ``cash_movement_difference`` additionally
requires unique reported cash change. ``cash_ending_from_flows``
additionally requires unique opening cash. ``cash_ending_difference``
additionally requires unique closing cash. Absent or ambiguous sources omit
only dependent families. Missing required-period values fail closed.
Reported zeros and signed flows are preserved.

Differences are calculated minus reported, in statement units. Nonzero
gaps remain visible; the module does not insert a balancing plug, assert a
cause, substitute balance-sheet cash, or infer debt funding.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .source_values import required_period_value

OPERATING_CONCEPT = "net_cash_from_operating_activities"
INVESTING_CONCEPT = "net_cash_from_investing_activities"
FINANCING_CONCEPT = "net_cash_from_financing_activities"
FX_CONCEPT = "effect_of_fx_on_cash"
BEGINNING_CONCEPT = "cash_beginning"
ENDING_CONCEPT = "cash_ending"
CHANGE_CONCEPT = "change_in_cash"


@dataclass(frozen=True)
class CashRollforwardAvailability:
    operating: bool
    operating_ambiguous: bool
    investing: bool
    investing_ambiguous: bool
    financing: bool
    financing_ambiguous: bool
    fx: bool
    fx_ambiguous: bool
    beginning: bool
    beginning_ambiguous: bool
    ending: bool
    ending_ambiguous: bool
    change: bool
    change_ambiguous: bool


@dataclass(frozen=True)
class CashRollforwardSources:
    operating: LineItem | None
    investing: LineItem | None
    financing: LineItem | None
    fx: LineItem | None
    beginning: LineItem | None
    ending: LineItem | None
    change: LineItem | None


@dataclass(frozen=True)
class CashRollforwardSeries:
    operating: tuple[float, ...]
    investing: tuple[float, ...]
    financing: tuple[float, ...]
    fx: tuple[float, ...]
    cash_movement_from_flows: tuple[float, ...]
    cash_movement_difference: tuple[float, ...] | None = None
    cash_ending_from_flows: tuple[float, ...] | None = None
    cash_ending_difference: tuple[float, ...] | None = None
    reported_cash_change: tuple[float, ...] | None = None
    cash_beginning: tuple[float, ...] | None = None
    cash_ending: tuple[float, ...] | None = None


def _resolve_unique_cf(
    financials: StandardizedFinancials, concept: str
) -> tuple[LineItem | None, bool]:
    try:
        resolved = resolve_line(financials.cash_flow, concept, required=False)
    except AmbiguousLineError:
        return None, True
    return resolved.item, False


def cash_rollforward_availability(
    financials: StandardizedFinancials,
) -> CashRollforwardAvailability:
    """Report unique CF roll-forward source resolution without mutating rows."""
    operating, operating_ambiguous = _resolve_unique_cf(financials, OPERATING_CONCEPT)
    investing, investing_ambiguous = _resolve_unique_cf(financials, INVESTING_CONCEPT)
    financing, financing_ambiguous = _resolve_unique_cf(financials, FINANCING_CONCEPT)
    fx, fx_ambiguous = _resolve_unique_cf(financials, FX_CONCEPT)
    beginning, beginning_ambiguous = _resolve_unique_cf(financials, BEGINNING_CONCEPT)
    ending, ending_ambiguous = _resolve_unique_cf(financials, ENDING_CONCEPT)
    change, change_ambiguous = _resolve_unique_cf(financials, CHANGE_CONCEPT)
    return CashRollforwardAvailability(
        operating=operating is not None,
        operating_ambiguous=operating_ambiguous,
        investing=investing is not None,
        investing_ambiguous=investing_ambiguous,
        financing=financing is not None,
        financing_ambiguous=financing_ambiguous,
        fx=fx is not None,
        fx_ambiguous=fx_ambiguous,
        beginning=beginning is not None,
        beginning_ambiguous=beginning_ambiguous,
        ending=ending is not None,
        ending_ambiguous=ending_ambiguous,
        change=change is not None,
        change_ambiguous=change_ambiguous,
    )


def resolve_cash_rollforward_sources(
    financials: StandardizedFinancials,
) -> CashRollforwardSources:
    """Return unique explicit CF roll-forward lines; ambiguous sources are None."""
    operating, _ = _resolve_unique_cf(financials, OPERATING_CONCEPT)
    investing, _ = _resolve_unique_cf(financials, INVESTING_CONCEPT)
    financing, _ = _resolve_unique_cf(financials, FINANCING_CONCEPT)
    fx, _ = _resolve_unique_cf(financials, FX_CONCEPT)
    beginning, _ = _resolve_unique_cf(financials, BEGINNING_CONCEPT)
    ending, _ = _resolve_unique_cf(financials, ENDING_CONCEPT)
    change, _ = _resolve_unique_cf(financials, CHANGE_CONCEPT)
    return CashRollforwardSources(
        operating=operating,
        investing=investing,
        financing=financing,
        fx=fx,
        beginning=beginning,
        ending=ending,
        change=change,
    )


def cash_movement_from_flows_applicable(financials: StandardizedFinancials) -> bool:
    """Movement requires unique CFO, CFI, CFF, and FX."""
    avail = cash_rollforward_availability(financials)
    return (
        avail.operating
        and not avail.operating_ambiguous
        and avail.investing
        and not avail.investing_ambiguous
        and avail.financing
        and not avail.financing_ambiguous
        and avail.fx
        and not avail.fx_ambiguous
    )


def cash_movement_difference_applicable(financials: StandardizedFinancials) -> bool:
    """Difference requires movement sources plus unique reported cash change."""
    avail = cash_rollforward_availability(financials)
    return (
        cash_movement_from_flows_applicable(financials)
        and avail.change
        and not avail.change_ambiguous
    )


def cash_ending_from_flows_applicable(financials: StandardizedFinancials) -> bool:
    """Ending from flows requires movement sources plus unique opening cash."""
    avail = cash_rollforward_availability(financials)
    return (
        cash_movement_from_flows_applicable(financials)
        and avail.beginning
        and not avail.beginning_ambiguous
    )


def cash_ending_difference_applicable(financials: StandardizedFinancials) -> bool:
    """Ending difference requires ending-from-flows sources plus unique closing cash."""
    avail = cash_rollforward_availability(financials)
    return (
        cash_ending_from_flows_applicable(financials)
        and avail.ending
        and not avail.ending_ambiguous
    )


def cash_rollforward_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when cash movement from flows can be computed."""
    return cash_movement_from_flows_applicable(financials)


def compute_cash_rollforward_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> CashRollforwardSeries:
    """Read reported cash-flow totals and compute roll-forward diagnostics."""
    if not cash_movement_from_flows_applicable(financials):
        raise MissingLineError("cash roll-forward movement sources not available")

    sources = resolve_cash_rollforward_sources(financials)
    assert sources.operating is not None
    assert sources.investing is not None
    assert sources.financing is not None
    assert sources.fx is not None

    operating = tuple(
        required_period_value(sources.operating, period, field=OPERATING_CONCEPT)
        for period in periods
    )
    investing = tuple(
        required_period_value(sources.investing, period, field=INVESTING_CONCEPT)
        for period in periods
    )
    financing = tuple(
        required_period_value(sources.financing, period, field=FINANCING_CONCEPT)
        for period in periods
    )
    fx = tuple(
        required_period_value(sources.fx, period, field=FX_CONCEPT)
        for period in periods
    )
    cash_movement_from_flows = tuple(
        operating[j] + investing[j] + financing[j] + fx[j]
        for j in range(len(periods))
    )

    reported_cash_change: tuple[float, ...] | None = None
    cash_movement_difference: tuple[float, ...] | None = None
    if cash_movement_difference_applicable(financials):
        assert sources.change is not None
        reported_cash_change = tuple(
            required_period_value(sources.change, period, field=CHANGE_CONCEPT)
            for period in periods
        )
        cash_movement_difference = tuple(
            cash_movement_from_flows[j] - reported_cash_change[j]
            for j in range(len(periods))
        )

    cash_beginning: tuple[float, ...] | None = None
    cash_ending_from_flows: tuple[float, ...] | None = None
    if cash_ending_from_flows_applicable(financials):
        assert sources.beginning is not None
        cash_beginning = tuple(
            required_period_value(sources.beginning, period, field=BEGINNING_CONCEPT)
            for period in periods
        )
        cash_ending_from_flows = tuple(
            cash_beginning[j] + cash_movement_from_flows[j]
            for j in range(len(periods))
        )

    cash_ending: tuple[float, ...] | None = None
    cash_ending_difference: tuple[float, ...] | None = None
    if cash_ending_difference_applicable(financials):
        assert sources.ending is not None
        assert cash_ending_from_flows is not None
        cash_ending = tuple(
            required_period_value(sources.ending, period, field=ENDING_CONCEPT)
            for period in periods
        )
        cash_ending_difference = tuple(
            cash_ending_from_flows[j] - cash_ending[j] for j in range(len(periods))
        )

    return CashRollforwardSeries(
        operating=operating,
        investing=investing,
        financing=financing,
        fx=fx,
        cash_movement_from_flows=cash_movement_from_flows,
        cash_movement_difference=cash_movement_difference,
        cash_ending_from_flows=cash_ending_from_flows,
        cash_ending_difference=cash_ending_difference,
        reported_cash_change=reported_cash_change,
        cash_beginning=cash_beginning,
        cash_ending=cash_ending,
    )
