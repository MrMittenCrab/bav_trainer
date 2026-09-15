"""Shared historical ratio helpers — exact-zero denominator yields #N/A."""

from __future__ import annotations

UNDEFINED_RATIO = "#N/A"
SOURCE_UNAVAILABLE = "Source unavailable"


def is_source_unavailable(value: object) -> bool:
    """True when a computed output is gated by missing source facts."""
    return value == SOURCE_UNAVAILABLE


def ratio_or_na(
    numerator: float | str,
    denominator: float | str,
) -> float | str:
    """Return a historical ratio, or #N/A when either input is undefined or the denominator is zero."""
    if is_source_unavailable(numerator) or is_source_unavailable(denominator):
        return SOURCE_UNAVAILABLE
    if numerator == UNDEFINED_RATIO or denominator == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    if float(denominator) == 0.0:
        return UNDEFINED_RATIO
    return float(numerator) / float(denominator)
