"""Historical RNOA change attribution: Margin vs NOA Turnover (Step 9C.2)."""

from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .profitability_drivers import compute_profitability_driver_series
from .ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable


@dataclass(frozen=True)
class ProfitabilityChangeSeries:
    nopat_margin_change: tuple[float | str | None, ...]
    noa_turnover_change: tuple[float | str | None, ...]
    rnoa_change: tuple[float | str | None, ...]
    margin_effect_on_rnoa: tuple[float | str | None, ...]
    turnover_effect_on_rnoa: tuple[float | str | None, ...]
    rnoa_change_from_drivers: tuple[float | str | None, ...]


def _difference_or_na(current, prior) -> float | str:
    if is_source_unavailable(current) or is_source_unavailable(prior):
        return SOURCE_UNAVAILABLE
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def compute_profitability_change_series(
    anchor: AnchorMetrics,
) -> ProfitabilityChangeSeries:
    """Attribute period-to-period RNOA change to Margin vs Turnover midpoints."""
    drivers = compute_profitability_driver_series(anchor)
    margin = tuple(anchor.dupont["NOPAT Margin"])
    turnover = tuple(drivers.noa_turnover)
    direct_rnoa = tuple(anchor.dupont["RNOA"])

    lengths = {
        "NOPAT Margin": len(margin),
        "NOA Turnover": len(turnover),
        "RNOA": len(direct_rnoa),
    }
    if len(set(lengths.values())) != 1 or lengths["RNOA"] == 0:
        raise ValueError(
            "profitability-change series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    n = len(direct_rnoa)
    margin_change: list[float | str | None] = [None] * n
    turnover_change: list[float | str | None] = [None] * n
    rnoa_change: list[float | str | None] = [None] * n
    margin_effect: list[float | str | None] = [None] * n
    turnover_effect: list[float | str | None] = [None] * n
    driver_change: list[float | str | None] = [None] * n

    for i in range(2, n):
        margin_delta = _difference_or_na(margin[i], margin[i - 1])
        turnover_delta = _difference_or_na(turnover[i], turnover[i - 1])
        direct_delta = _difference_or_na(direct_rnoa[i], direct_rnoa[i - 1])

        margin_change[i] = margin_delta
        turnover_change[i] = turnover_delta
        rnoa_change[i] = direct_delta

        required = (
            margin[i],
            margin[i - 1],
            turnover[i],
            turnover[i - 1],
        )
        if any(is_source_unavailable(value) for value in required):
            margin_effect[i] = SOURCE_UNAVAILABLE
            turnover_effect[i] = SOURCE_UNAVAILABLE
            driver_change[i] = SOURCE_UNAVAILABLE
        elif any(value == UNDEFINED_RATIO for value in required):
            margin_effect[i] = UNDEFINED_RATIO
            turnover_effect[i] = UNDEFINED_RATIO
            driver_change[i] = UNDEFINED_RATIO
        else:
            margin_effect_value = (
                (float(margin[i]) - float(margin[i - 1]))
                * (float(turnover[i]) + float(turnover[i - 1]))
                / 2.0
            )
            turnover_effect_value = (
                (float(turnover[i]) - float(turnover[i - 1]))
                * (float(margin[i]) + float(margin[i - 1]))
                / 2.0
            )
            driver_delta = margin_effect_value + turnover_effect_value

            margin_effect[i] = margin_effect_value
            turnover_effect[i] = turnover_effect_value
            driver_change[i] = driver_delta

            if is_source_unavailable(direct_delta):
                raise ValueError(
                    "RNOA change attribution is numeric while direct RNOA change is "
                    f"source-unavailable: period_index={i} driver={driver_change[i]}"
                )
            if direct_delta == UNDEFINED_RATIO:
                raise ValueError(
                    "RNOA change attribution is numeric while direct RNOA change is undefined: "
                    f"period_index={i} driver={driver_change[i]}"
                )
            if abs(float(driver_change[i]) - float(direct_delta)) > 1e-9:
                raise ValueError(
                    "RNOA change attribution does not reconcile: "
                    f"period_index={i} direct={direct_delta} driver={driver_change[i]}"
                )

    return ProfitabilityChangeSeries(
        nopat_margin_change=tuple(margin_change),
        noa_turnover_change=tuple(turnover_change),
        rnoa_change=tuple(rnoa_change),
        margin_effect_on_rnoa=tuple(margin_effect),
        turnover_effect_on_rnoa=tuple(turnover_effect),
        rnoa_change_from_drivers=tuple(driver_change),
    )
