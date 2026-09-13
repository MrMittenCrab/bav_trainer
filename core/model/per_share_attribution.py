"""Historical diluted-EPS earnings / share-count attribution (Step 9F.2)."""

from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .per_share import PerShareSeries


@dataclass(frozen=True)
class PerShareAttributionSeries:
    reported_net_income_change: tuple[float | None, ...]
    earnings_effect_on_diluted_eps_change: tuple[float | None, ...]
    share_count_effect_on_diluted_eps_change: tuple[float | None, ...]
    diluted_eps_change_from_drivers: tuple[float | None, ...]


def compute_per_share_attribution_series(
    anchor: AnchorMetrics,
    per_share: PerShareSeries,
) -> PerShareAttributionSeries:
    """Attribute diluted EPS change to earnings vs share-count midpoint effects."""
    net_income = tuple(float(v) for v in per_share.earnings_numerator)
    shares = tuple(float(v) for v in per_share.diluted_weighted_average_shares)
    direct_eps = tuple(float(v) for v in per_share.reported_diluted_eps)
    direct_eps_change = tuple(per_share.diluted_eps_change)

    lengths = {
        "net_income": len(net_income),
        "diluted_weighted_average_shares": len(shares),
        "reported_diluted_eps": len(direct_eps),
        "diluted_eps_change": len(direct_eps_change),
    }
    if len(set(lengths.values())) != 1 or lengths["net_income"] == 0:
        raise ValueError(
            "per-share attribution series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    for i, value in enumerate(shares):
        if value <= 0.0:
            raise ValueError(
                "per-share attribution requires positive diluted weighted-average "
                f"shares: period_index={i} shares={value}"
            )

    n = len(net_income)
    for i in range(n):
        recomputed = net_income[i] / shares[i]
        if abs(recomputed - direct_eps[i]) > 1e-9:
            raise ValueError(
                "reported diluted EPS level does not reconcile before attribution: "
                f"period_index={i} direct={direct_eps[i]} recomputed={recomputed}"
            )

    net_income_change: list[float | None] = [None] * n
    earnings_effect: list[float | None] = [None] * n
    share_count_effect: list[float | None] = [None] * n
    driver_change: list[float | None] = [None] * n

    for i in range(1, n):
        prior = i - 1
        current_inverse_shares = 1.0 / shares[i]
        prior_inverse_shares = 1.0 / shares[prior]

        ni_delta = net_income[i] - net_income[prior]
        earnings_value = (
            ni_delta * (current_inverse_shares + prior_inverse_shares) / 2.0
        )
        share_value = (
            (current_inverse_shares - prior_inverse_shares)
            * (net_income[i] + net_income[prior])
            / 2.0
        )
        driver_value = earnings_value + share_value

        direct = direct_eps_change[i]
        if direct is None:
            raise ValueError(
                "per-share attribution requires comparable diluted EPS change: "
                f"period_index={i}"
            )
        if abs(driver_value - float(direct)) > 1e-9:
            raise ValueError(
                "diluted EPS earnings/share-count attribution does not reconcile: "
                f"period_index={i} direct={direct} driver={driver_value}"
            )

        net_income_change[i] = ni_delta
        earnings_effect[i] = earnings_value
        share_count_effect[i] = share_value
        driver_change[i] = driver_value

    return PerShareAttributionSeries(
        reported_net_income_change=tuple(net_income_change),
        earnings_effect_on_diluted_eps_change=tuple(earnings_effect),
        share_count_effect_on_diluted_eps_change=tuple(share_count_effect),
        diluted_eps_change_from_drivers=tuple(driver_change),
    )
