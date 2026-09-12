"""Historical ROE operating / financing attribution (Step 9D.1)."""

from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .profitability_change import compute_profitability_change_series
from .ratio_values import UNDEFINED_RATIO


@dataclass(frozen=True)
class ROEAttributionSeries:
    financing_contribution_to_roe: tuple[float | str | None, ...]
    roe_change: tuple[float | str | None, ...]
    operating_effect_on_roe_change: tuple[float | str | None, ...]
    leverage_effect_on_roe_change: tuple[float | str | None, ...]
    spread_effect_on_roe_change: tuple[float | str | None, ...]
    financing_effect_on_roe_change: tuple[float | str | None, ...]
    roe_change_from_drivers: tuple[float | str | None, ...]


def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _product_or_na(left, right) -> float | str:
    if left == UNDEFINED_RATIO or right == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(left) * float(right)


def compute_roe_attribution_series(
    anchor: AnchorMetrics,
) -> ROEAttributionSeries:
    """Attribute decomposed ROE to operating vs financing drivers."""
    profitability_change = compute_profitability_change_series(anchor)
    rnoa = tuple(anchor.dupont["RNOA"])
    flev = tuple(anchor.dupont["FLEV"])
    spread = tuple(anchor.dupont["Spread"])
    roe = tuple(anchor.dupont["ROE (decomposed)"])

    lengths = {
        "RNOA": len(rnoa),
        "FLEV": len(flev),
        "Spread": len(spread),
        "ROE (decomposed)": len(roe),
        "RNOA change": len(profitability_change.rnoa_change),
    }
    if len(set(lengths.values())) != 1 or lengths["RNOA"] == 0:
        raise ValueError(
            "ROE-attribution series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    n = len(rnoa)
    financing_contribution: list[float | str | None] = [None] * n
    roe_change: list[float | str | None] = [None] * n
    operating_effect: list[float | str | None] = [None] * n
    leverage_effect: list[float | str | None] = [None] * n
    spread_effect: list[float | str | None] = [None] * n
    financing_effect: list[float | str | None] = [None] * n
    driver_change: list[float | str | None] = [None] * n

    for i in range(1, n):
        contribution = _product_or_na(flev[i], spread[i])
        financing_contribution[i] = contribution

        if contribution != UNDEFINED_RATIO:
            if rnoa[i] == UNDEFINED_RATIO or roe[i] == UNDEFINED_RATIO:
                raise ValueError(
                    "ROE financing contribution is numeric while level ROE identity "
                    f"is undefined: period_index={i} contribution={contribution}"
                )
            level_roe = float(rnoa[i]) + float(contribution)
            if abs(level_roe - float(roe[i])) > 1e-9:
                raise ValueError(
                    "ROE operating/financing level bridge does not reconcile: "
                    f"period_index={i} direct={roe[i]} bridge={level_roe}"
                )

    for i in range(2, n):
        direct_delta = _difference_or_na(roe[i], roe[i - 1])
        operating = profitability_change.rnoa_change[i]
        assert operating is not None

        roe_change[i] = direct_delta
        operating_effect[i] = operating

        required_financing = (
            flev[i],
            flev[i - 1],
            spread[i],
            spread[i - 1],
        )
        if any(value == UNDEFINED_RATIO for value in required_financing):
            leverage_effect[i] = UNDEFINED_RATIO
            spread_effect[i] = UNDEFINED_RATIO
            financing_effect[i] = UNDEFINED_RATIO
        else:
            leverage_value = (
                (float(flev[i]) - float(flev[i - 1]))
                * (float(spread[i]) + float(spread[i - 1]))
                / 2.0
            )
            spread_value = (
                (float(spread[i]) - float(spread[i - 1]))
                * (float(flev[i]) + float(flev[i - 1]))
                / 2.0
            )
            financing_value = leverage_value + spread_value

            leverage_effect[i] = leverage_value
            spread_effect[i] = spread_value
            financing_effect[i] = financing_value

            current_contribution = financing_contribution[i]
            prior_contribution = financing_contribution[i - 1]
            assert current_contribution is not None
            assert prior_contribution is not None
            if (
                current_contribution != UNDEFINED_RATIO
                and prior_contribution != UNDEFINED_RATIO
            ):
                direct_financing_change = (
                    float(current_contribution) - float(prior_contribution)
                )
                if abs(float(financing_effect[i]) - direct_financing_change) > 1e-9:
                    raise ValueError(
                        "ROE financing-effect attribution does not reconcile: "
                        f"period_index={i} direct={direct_financing_change} "
                        f"driver={financing_effect[i]}"
                    )

        if operating == UNDEFINED_RATIO or financing_effect[i] == UNDEFINED_RATIO:
            driver_change[i] = UNDEFINED_RATIO
        else:
            driver_change[i] = float(operating) + float(financing_effect[i])

        if driver_change[i] != UNDEFINED_RATIO and driver_change[i] is not None:
            if direct_delta == UNDEFINED_RATIO:
                raise ValueError(
                    "ROE driver attribution is numeric while direct ROE change is "
                    f"undefined: period_index={i} driver={driver_change[i]}"
                )
            if abs(float(driver_change[i]) - float(direct_delta)) > 1e-9:
                raise ValueError(
                    "ROE operating/financing change attribution does not reconcile: "
                    f"period_index={i} direct={direct_delta} driver={driver_change[i]}"
                )

    return ROEAttributionSeries(
        financing_contribution_to_roe=tuple(financing_contribution),
        roe_change=tuple(roe_change),
        operating_effect_on_roe_change=tuple(operating_effect),
        leverage_effect_on_roe_change=tuple(leverage_effect),
        spread_effect_on_roe_change=tuple(spread_effect),
        financing_effect_on_roe_change=tuple(financing_effect),
        roe_change_from_drivers=tuple(driver_change),
    )
