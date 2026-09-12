"""Historical normalized diluted EPS bridge (Step 9F.3)."""

from __future__ import annotations

from dataclasses import dataclass

from .normalization import NormalizationSeries
from .per_share import PerShareSeries
from .ratio_values import UNDEFINED_RATIO, ratio_or_na


@dataclass(frozen=True)
class NormalizedPerShareSeries:
    normalization_adjustment_per_diluted_share: tuple[float | str, ...]
    normalized_diluted_eps: tuple[float | str, ...]
    normalized_diluted_eps_change: tuple[float | str | None, ...]
    normalization_effect_on_diluted_eps_change: tuple[float | str | None, ...]


def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def compute_normalized_per_share_series(
    normalization: NormalizationSeries,
    per_share: PerShareSeries,
) -> NormalizedPerShareSeries:
    """Bridge reported diluted EPS to normalized diluted EPS via share-scaled adjustments."""
    shares = tuple(float(v) for v in per_share.diluted_weighted_average_shares)
    reported_eps = tuple(float(v) for v in per_share.reported_diluted_eps)
    reported_eps_change = tuple(per_share.diluted_eps_change)
    after_tax = tuple(normalization.after_tax_adjustment)
    normalized_ni = tuple(normalization.normalized_net_income)

    lengths = {
        "shares": len(shares),
        "reported_eps": len(reported_eps),
        "reported_eps_change": len(reported_eps_change),
        "after_tax_adjustment": len(after_tax),
        "normalized_net_income": len(normalized_ni),
    }
    if len(set(lengths.values())) != 1 or lengths["shares"] == 0:
        raise ValueError(
            "normalized-per-share series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )
    for i, value in enumerate(shares):
        if value <= 0.0:
            raise ValueError(
                "normalized per-share analysis requires positive diluted shares: "
                f"period_index={i} shares={value}"
            )

    adjustment_ps = tuple(
        ratio_or_na(after_tax[i], shares[i]) for i in range(len(shares))
    )
    normalized_eps = tuple(
        ratio_or_na(normalized_ni[i], shares[i]) for i in range(len(shares))
    )

    for i in range(len(shares)):
        if (adjustment_ps[i] == UNDEFINED_RATIO) != (
            normalized_eps[i] == UNDEFINED_RATIO
        ):
            raise ValueError(
                "normalized diluted EPS undefined state is inconsistent: "
                f"period_index={i} adjustment={adjustment_ps[i]} "
                f"normalized={normalized_eps[i]}"
            )
        if (
            adjustment_ps[i] != UNDEFINED_RATIO
            and normalized_eps[i] != UNDEFINED_RATIO
        ):
            bridge = reported_eps[i] + float(adjustment_ps[i])
            if abs(bridge - float(normalized_eps[i])) > 1e-9:
                raise ValueError(
                    "normalized diluted EPS level bridge does not reconcile: "
                    f"period_index={i} bridge={bridge} normalized={normalized_eps[i]}"
                )

    n = len(shares)
    normalized_change: list[float | str | None] = [None] * n
    normalization_effect: list[float | str | None] = [None] * n

    for i in range(1, n):
        norm_chg = _difference_or_na(normalized_eps[i], normalized_eps[i - 1])
        effect = _difference_or_na(adjustment_ps[i], adjustment_ps[i - 1])
        normalized_change[i] = norm_chg
        normalization_effect[i] = effect

        if (norm_chg == UNDEFINED_RATIO) != (effect == UNDEFINED_RATIO):
            raise ValueError(
                "normalized diluted EPS change undefined state is inconsistent: "
                f"period_index={i} normalized_change={norm_chg} effect={effect}"
            )
        if norm_chg == UNDEFINED_RATIO:
            continue

        reported_change = reported_eps_change[i]
        if reported_change is None:
            raise ValueError(
                "normalized per-share analysis requires comparable reported EPS change: "
                f"period_index={i}"
            )
        bridge = float(reported_change) + float(effect)
        if abs(bridge - float(norm_chg)) > 1e-9:
            raise ValueError(
                "normalized diluted EPS change bridge does not reconcile: "
                f"period_index={i} bridge={bridge} normalized={norm_chg}"
            )

    return NormalizedPerShareSeries(
        normalization_adjustment_per_diluted_share=adjustment_ps,
        normalized_diluted_eps=normalized_eps,
        normalized_diluted_eps_change=tuple(normalized_change),
        normalization_effect_on_diluted_eps_change=tuple(normalization_effect),
    )
