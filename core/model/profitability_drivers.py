"""Historical RNOA margin / NOA-turnover driver decomposition (Step 9C.1)."""

from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .ratio_values import UNDEFINED_RATIO, ratio_or_na


@dataclass(frozen=True)
class ProfitabilityDriverSeries:
    average_noa: tuple[float | None, ...]
    noa_turnover: tuple[float | str | None, ...]
    noa_intensity: tuple[float | str | None, ...]
    rnoa_from_margin_turnover: tuple[float | str | None, ...]


def compute_profitability_driver_series(
    anchor: AnchorMetrics,
) -> ProfitabilityDriverSeries:
    """Compute Average NOA, turnover, intensity, and margin×turnover RNOA."""
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    noa = tuple(float(v) for v in anchor.reformulation.noa)
    margin = tuple(anchor.dupont["NOPAT Margin"])
    direct_rnoa = tuple(anchor.dupont["RNOA"])
    lengths = {
        "revenue": len(revenue),
        "noa": len(noa),
        "NOPAT Margin": len(margin),
        "RNOA": len(direct_rnoa),
    }
    if len(set(lengths.values())) != 1 or lengths["revenue"] == 0:
        raise ValueError(
            "profitability-driver series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    average_noa: list[float | None] = [None]
    noa_turnover: list[float | str | None] = [None]
    noa_intensity: list[float | str | None] = [None]
    rnoa_from_margin_turnover: list[float | str | None] = [None]

    for i in range(1, len(revenue)):
        average = (noa[i - 1] + noa[i]) / 2.0
        turnover = ratio_or_na(revenue[i], average)
        intensity = ratio_or_na(average, revenue[i])
        if margin[i] == UNDEFINED_RATIO or turnover == UNDEFINED_RATIO:
            driver_rnoa: float | str = UNDEFINED_RATIO
        else:
            driver_rnoa = float(margin[i]) * float(turnover)

        if driver_rnoa != UNDEFINED_RATIO:
            if direct_rnoa[i] == UNDEFINED_RATIO:
                raise ValueError(
                    "RNOA driver bridge is numeric while direct RNOA is undefined: "
                    f"period_index={i} driver={driver_rnoa}"
                )
            if abs(float(driver_rnoa) - float(direct_rnoa[i])) > 1e-9:
                raise ValueError(
                    "RNOA margin/turnover bridge does not reconcile: "
                    f"period_index={i} direct={direct_rnoa[i]} driver={driver_rnoa}"
                )

        average_noa.append(average)
        noa_turnover.append(turnover)
        noa_intensity.append(intensity)
        rnoa_from_margin_turnover.append(driver_rnoa)

    return ProfitabilityDriverSeries(
        average_noa=tuple(average_noa),
        noa_turnover=tuple(noa_turnover),
        noa_intensity=tuple(noa_intensity),
        rnoa_from_margin_turnover=tuple(rnoa_from_margin_turnover),
    )
