"""Canonical fiscal-period axis for historical multi-period modeling."""

from __future__ import annotations

from datetime import date

from ..data.interface import StandardizedFinancials


class PeriodAxisError(ValueError):
    """Historical fiscal-period axis is not suitable for comparative modeling."""


def canonical_fiscal_periods(
    financials: StandardizedFinancials,
) -> list[date]:
    """Return unique chronological fiscal period-end dates for model construction.

    Prefers non-interim periods. Does not mutate ``financials.periods``.
    Annual histories must be year-contiguous for growth/DuPont comparatives.
    """
    annual = [p.end_date for p in financials.periods if not p.is_interim]
    raw = annual or [p.end_date for p in financials.periods]
    if not raw:
        raise PeriodAxisError("No fiscal periods available for historical modeling")

    if len(raw) != len(set(raw)):
        raise PeriodAxisError(
            "duplicate fiscal period-end dates are not allowed on the historical axis"
        )

    ordered = sorted(raw)
    if annual:
        for previous, current in zip(ordered, ordered[1:]):
            if current.year != previous.year + 1:
                raise PeriodAxisError(
                    "contiguous annual fiscal periods are required for multi-period "
                    f"growth/DuPont calculations; found gap between {previous} and {current}"
                )
    return ordered
