"""Historical earnings-quality cash-conversion trend diagnostics (Step 9E.1)."""

from __future__ import annotations

from dataclasses import dataclass

from .earnings_quality import EarningsQualitySeries
from .ratio_values import UNDEFINED_RATIO


@dataclass(frozen=True)
class EarningsQualityChangeSeries:
    operating_cash_flow_change: tuple[float | None, ...]
    cash_conversion_ratio_change: tuple[float | str | None, ...]
    total_accruals_change: tuple[float | None, ...]
    accrual_ratio_change: tuple[float | str | None, ...]


def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def compute_earnings_quality_change_series(
    earnings_quality: EarningsQualitySeries,
) -> EarningsQualityChangeSeries:
    """Compute period-to-period CFO / conversion / accrual trend diagnostics."""
    cfo = tuple(earnings_quality.operating_cash_flow)
    conversion = tuple(earnings_quality.cash_conversion_ratio)
    accruals = tuple(earnings_quality.total_accruals)
    accrual_ratio = tuple(earnings_quality.accrual_ratio)

    lengths = {
        "operating_cash_flow": len(cfo),
        "cash_conversion_ratio": len(conversion),
        "total_accruals": len(accruals),
        "accrual_ratio": len(accrual_ratio),
    }
    if len(set(lengths.values())) != 1 or lengths["operating_cash_flow"] == 0:
        raise ValueError(
            "earnings-quality change series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    n = len(cfo)
    cfo_change: list[float | None] = [None] * n
    conversion_change: list[float | str | None] = [None] * n
    accruals_change: list[float | None] = [None] * n
    accrual_ratio_change: list[float | str | None] = [None] * n

    for i in range(1, n):
        cfo_change[i] = float(cfo[i]) - float(cfo[i - 1])
        conversion_change[i] = _difference_or_na(conversion[i], conversion[i - 1])
        accruals_change[i] = float(accruals[i]) - float(accruals[i - 1])

    has_accrual_ratio = any(value is not None for value in accrual_ratio[1:])
    if has_accrual_ratio:
        for i in range(2, n):
            current = accrual_ratio[i]
            prior = accrual_ratio[i - 1]
            if current is None or prior is None:
                raise ValueError(
                    "earnings-quality accrual-ratio change requires consecutive "
                    "comparable values: "
                    f"period_index={i} current={current!r} prior={prior!r}"
                )
            accrual_ratio_change[i] = _difference_or_na(current, prior)

    return EarningsQualityChangeSeries(
        operating_cash_flow_change=tuple(cfo_change),
        cash_conversion_ratio_change=tuple(conversion_change),
        total_accruals_change=tuple(accruals_change),
        accrual_ratio_change=tuple(accrual_ratio_change),
    )
