"""One-year base-case operating forecast from explicit drivers (Step 10A).

Independent of ``ri_engine`` and normal historical workbook generation.
Computes one forecast year for revenue, NOPAT, and NOWC from a verified
historical ``AnchorMetrics`` plus explicit next-year assumptions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Literal, Sequence

from .financial_math import AnchorMetrics
from .ratio_values import UNDEFINED_RATIO, ratio_or_na

AssumptionOrigin = Literal["supplied", "learner"]
_VALID_ORIGINS = frozenset({"supplied", "learner"})


@dataclass(frozen=True)
class ForecastDriverAssumption:
    """One explicit forecast driver with provenance and explanation."""

    value: float
    origin: AssumptionOrigin
    explanation: str


@dataclass(frozen=True)
class OperatingForecastAssumptions:
    """Explicit next-year drivers; never inferred from historical comparators."""

    revenue_growth: ForecastDriverAssumption
    nopat_margin: ForecastDriverAssumption
    nowc_to_revenue: ForecastDriverAssumption


@dataclass(frozen=True)
class HistoricalComparators:
    """Latest historical diagnostics for comparison only (not forecast inputs)."""

    sales_growth: float | str | None
    nopat_margin: float | str | None
    nowc_to_revenue: float | str | None


@dataclass(frozen=True)
class OneYearOperatingForecast:
    """Bounded one-year operating forecast outputs and audit context."""

    historical_period: date
    forecast_period: date
    historical_period_label: str
    forecast_period_label: str
    opening_revenue: float
    opening_nowc: float
    opening_nopat: float | str
    assumptions: OperatingForecastAssumptions
    comparators: HistoricalComparators
    forecast_revenue: float
    forecast_nopat: float
    closing_nowc: float
    change_in_nowc: float


def _require_finite_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _validate_driver(assumption: object, field: str) -> ForecastDriverAssumption:
    if assumption is None:
        raise ValueError(f"missing required forecast assumption: {field}")
    if not isinstance(assumption, ForecastDriverAssumption):
        raise ValueError(f"{field} must be a ForecastDriverAssumption")
    value = _require_finite_number(assumption.value, field)
    if assumption.origin not in _VALID_ORIGINS:
        raise ValueError(
            f"{field} origin must be 'supplied' or 'learner'; "
            f"got {assumption.origin!r}"
        )
    explanation = assumption.explanation
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError(f"{field} explanation must be a non-empty string")
    return ForecastDriverAssumption(
        value=value,
        origin=assumption.origin,
        explanation=explanation,
    )


def _validate_assumptions(
    assumptions: OperatingForecastAssumptions | None,
) -> OperatingForecastAssumptions:
    if assumptions is None:
        raise ValueError("missing required forecast assumptions")
    if not isinstance(assumptions, OperatingForecastAssumptions):
        raise ValueError("assumptions must be an OperatingForecastAssumptions")
    return OperatingForecastAssumptions(
        revenue_growth=_validate_driver(assumptions.revenue_growth, "revenue_growth"),
        nopat_margin=_validate_driver(assumptions.nopat_margin, "nopat_margin"),
        nowc_to_revenue=_validate_driver(
            assumptions.nowc_to_revenue, "nowc_to_revenue"
        ),
    )


def _validate_annual_axis(periods: Sequence[date]) -> tuple[date, ...]:
    if not periods:
        raise ValueError("historical period axis must not be empty")
    ordered = tuple(periods)
    if len(ordered) != len(set(ordered)):
        raise ValueError("duplicate dates are not allowed on the historical axis")
    if list(ordered) != sorted(ordered):
        raise ValueError("historical period axis must be chronological")
    for previous, current in zip(ordered, ordered[1:]):
        if current.year != previous.year + 1:
            raise ValueError(
                "contiguous annual fiscal periods are required for the one-year "
                f"operating forecast; found gap between {previous} and {current}"
            )
    return ordered


def _align_series(anchor: AnchorMetrics, n: int) -> None:
    lengths = {
        "revenue": len(anchor.historical.revenue),
        "nopat": len(anchor.historical.nopat),
        "nowc": len(anchor.reformulation.nowc),
        "Sales Growth": len(anchor.dupont["Sales Growth"]),
        "NOPAT Margin": len(anchor.dupont["NOPAT Margin"]),
    }
    mismatched = {name: length for name, length in lengths.items() if length != n}
    if mismatched:
        detail = ", ".join(f"{name}={length}" for name, length in mismatched.items())
        raise ValueError(
            f"historical series length mismatch versus period axis (n={n}): {detail}"
        )


def _period_label(labels: Sequence[str] | None, index: int, period: date) -> str:
    if labels is None:
        return f"FY{period.year}"
    if len(labels) <= index:
        raise ValueError("historical_period_labels length must match the period axis")
    label = labels[index]
    if not isinstance(label, str) or not label.strip():
        raise ValueError("historical period labels must be non-empty strings")
    return label


def _advance_period(period: date) -> date:
    try:
        return date(period.year + 1, period.month, period.day)
    except ValueError:
        # 29 Feb → 28 Feb in non-leap successor years
        return date(period.year + 1, period.month, period.day - 1)


def _comparator_value(value: object) -> float | str | None:
    if value is None:
        return None
    if value == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return UNDEFINED_RATIO
    number = float(value)
    if not math.isfinite(number):
        return UNDEFINED_RATIO
    return number


def compute_one_year_operating_forecast(
    anchor: AnchorMetrics,
    periods: Sequence[date],
    assumptions: OperatingForecastAssumptions,
    *,
    historical_period_labels: Sequence[str] | None = None,
    forecast_period_label: str | None = None,
) -> OneYearOperatingForecast:
    """Compute one explicit base-case forecast year from historical anchor + drivers.

    Does not mutate ``anchor`` or ``periods``. Historical comparators are recorded
    for pedagogy only and never become forecast assumptions.
    """
    validated = _validate_assumptions(assumptions)
    axis = _validate_annual_axis(periods)
    n = len(axis)
    _align_series(anchor, n)
    if historical_period_labels is not None and len(historical_period_labels) != n:
        raise ValueError("historical_period_labels length must match the period axis")

    last = n - 1
    historical_period = axis[last]
    opening_revenue = _require_finite_number(
        anchor.historical.revenue[last], "opening revenue"
    )
    if opening_revenue <= 0.0:
        raise ValueError("opening revenue must be positive")
    opening_nowc = _require_finite_number(
        anchor.reformulation.nowc[last], "opening NOWC"
    )
    opening_nopat_raw = anchor.historical.nopat[last]
    if opening_nopat_raw == UNDEFINED_RATIO:
        opening_nopat: float | str = UNDEFINED_RATIO
    else:
        opening_nopat = _require_finite_number(opening_nopat_raw, "opening NOPAT")

    growth = validated.revenue_growth.value
    if growth < -1.0:
        raise ValueError("revenue growth must be at least -100%")

    forecast_revenue = opening_revenue * (1.0 + growth)
    forecast_nopat = forecast_revenue * validated.nopat_margin.value
    closing_nowc = forecast_revenue * validated.nowc_to_revenue.value
    change_in_nowc = closing_nowc - opening_nowc
    for name, value in (
        ("forecast revenue", forecast_revenue),
        ("forecast NOPAT", forecast_nopat),
        ("closing NOWC", closing_nowc),
        ("change in NOWC", change_in_nowc),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

    hist_label = _period_label(historical_period_labels, last, historical_period)
    forecast_period = _advance_period(historical_period)
    if forecast_period_label is None:
        out_label = f"FY{forecast_period.year}"
    else:
        if not isinstance(forecast_period_label, str) or not forecast_period_label.strip():
            raise ValueError("forecast_period_label must be a non-empty string")
        out_label = forecast_period_label

    sales_growth = _comparator_value(anchor.dupont["Sales Growth"][last])
    nopat_margin = _comparator_value(anchor.dupont["NOPAT Margin"][last])
    nowc_to_revenue = ratio_or_na(opening_nowc, opening_revenue)
    if nowc_to_revenue == UNDEFINED_RATIO:
        nowc_comparator: float | str | None = UNDEFINED_RATIO
    else:
        nowc_comparator = float(nowc_to_revenue)

    return OneYearOperatingForecast(
        historical_period=historical_period,
        forecast_period=forecast_period,
        historical_period_label=hist_label,
        forecast_period_label=out_label,
        opening_revenue=opening_revenue,
        opening_nowc=opening_nowc,
        opening_nopat=opening_nopat,
        assumptions=validated,
        comparators=HistoricalComparators(
            sales_growth=sales_growth,
            nopat_margin=nopat_margin,
            nowc_to_revenue=nowc_comparator,
        ),
        forecast_revenue=forecast_revenue,
        forecast_nopat=forecast_nopat,
        closing_nowc=closing_nowc,
        change_in_nowc=change_in_nowc,
    )
