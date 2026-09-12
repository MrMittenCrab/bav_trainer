"""Historical diluted per-share diagnostics (Step 9F.1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .ratio_values import UNDEFINED_RATIO, ratio_or_na

SUPPORTED_SHARE_SCALE_BASIS = "financial_statement_units"


@dataclass(frozen=True)
class PerShareSeries:
    diluted_weighted_average_shares: tuple[float, ...]
    reported_diluted_eps: tuple[float, ...]
    nopat_per_diluted_share: tuple[float | str, ...]
    diluted_eps_change: tuple[float | None, ...]
    diluted_share_count_change: tuple[float | None, ...]


def per_share_available(financials: StandardizedFinancials) -> bool:
    """Return True when diluted weighted-average share history is supplied."""
    shares = financials.historical_shares
    return bool(shares is not None and shares.diluted_weighted_average)


def _required_diluted_share_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> tuple[float, ...]:
    shares = financials.historical_shares
    if shares is None or not shares.diluted_weighted_average:
        raise ValueError("diluted weighted-average share history is not supplied")
    if shares.scale_basis != SUPPORTED_SHARE_SCALE_BASIS:
        raise ValueError(
            "unsupported historical share scale_basis "
            f"{shares.scale_basis!r}; expected "
            f"{SUPPORTED_SHARE_SCALE_BASIS!r}"
        )

    values: list[float] = []
    for period in periods:
        if period not in shares.diluted_weighted_average:
            raise ValueError(
                "missing diluted weighted-average shares for modeled period "
                f"{period.isoformat()}"
            )
        raw = shares.diluted_weighted_average[period]
        if raw is None:
            raise ValueError(
                "missing diluted weighted-average shares for modeled period "
                f"{period.isoformat()}"
            )
        value = float(raw)
        if value <= 0.0:
            raise ValueError(
                "diluted weighted-average shares must be > 0 for modeled period "
                f"{period.isoformat()}, got {value}"
            )
        values.append(value)
    return tuple(values)


def compute_per_share_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> PerShareSeries:
    """Compute diluted EPS / NOPAT-per-share and their period changes."""
    shares = _required_diluted_share_series(financials, periods)
    net_income = tuple(float(v) for v in anchor.historical.net_income)
    nopat = tuple(anchor.historical.nopat)

    if len(net_income) != len(periods) or len(nopat) != len(periods):
        raise ValueError(
            "per-share period axis must match AnchorMetrics historical series length"
        )

    eps = tuple(net_income[i] / shares[i] for i in range(len(periods)))
    nopat_per_share = tuple(
        ratio_or_na(nopat[i], shares[i]) for i in range(len(periods))
    )

    eps_change: list[float | None] = [None]
    share_change: list[float | None] = [None]
    for i in range(1, len(periods)):
        eps_change.append(eps[i] - eps[i - 1])
        share_change.append(shares[i] - shares[i - 1])

    return PerShareSeries(
        diluted_weighted_average_shares=shares,
        reported_diluted_eps=eps,
        nopat_per_diluted_share=nopat_per_share,
        diluted_eps_change=tuple(eps_change),
        diluted_share_count_change=tuple(share_change),
    )
