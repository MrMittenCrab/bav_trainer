"""Shared historical ratio helpers — exact-zero denominator yields #N/A."""

from __future__ import annotations

UNDEFINED_RATIO = "#N/A"


def ratio_or_na(
    numerator: float | str,
    denominator: float | str,
) -> float | str:
    """Return a historical ratio, or #N/A when either input is undefined or the denominator is zero."""
    if numerator == UNDEFINED_RATIO or denominator == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    if float(denominator) == 0.0:
        return UNDEFINED_RATIO
    return float(numerator) / float(denominator)
