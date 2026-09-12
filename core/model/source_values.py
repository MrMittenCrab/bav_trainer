"""Shared required historical period-value helpers (no missing-to-zero fallback)."""

from __future__ import annotations

from datetime import date

from ..data.interface import LineItem


class MissingHistoricalValueError(ValueError):
    """A resolved historical source line lacks a required modeled-period value."""


def required_period_value(
    item: LineItem,
    period: date,
    *,
    field: str,
) -> float:
    """Return an explicitly supplied period value; never invent zero for missing data."""
    raw = item.values.get(period)
    if raw is None:
        raise MissingHistoricalValueError(
            f"{field} line {item.label!r} has no supplied value "
            f"for modeled period {period.isoformat()}"
        )
    return float(raw)


def required_period_series(
    item: LineItem,
    periods: list[date],
    *,
    field: str,
) -> tuple[float, ...]:
    """Return required values for every modeled period."""
    return tuple(
        required_period_value(item, period, field=field)
        for period in periods
    )
