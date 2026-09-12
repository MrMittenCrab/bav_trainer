"""Shared historical ratio helpers — exact-zero denominator yields #N/A."""

from __future__ import annotations

UNDEFINED_RATIO = "#N/A"


def ratio_or_na(numerator: float, denominator: float) -> float | str:
    """Return a historical ratio, or #N/A when its denominator is exactly zero."""
    if denominator == 0.0:
        return UNDEFINED_RATIO
    return float(numerator) / float(denominator)
