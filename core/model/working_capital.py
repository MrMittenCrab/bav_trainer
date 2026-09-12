"""Historical working-capital intensity and incremental diagnostics (Step 9B.1)."""

from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .ratio_values import ratio_or_na


@dataclass(frozen=True)
class WorkingCapitalSeries:
    owca_to_revenue: tuple[float | str, ...]
    owcl_to_revenue: tuple[float | str, ...]
    nowc_to_revenue: tuple[float | str, ...]
    revenue_change: tuple[float | None, ...]
    nowc_change: tuple[float | None, ...]
    incremental_nowc_to_revenue_change: tuple[float | str | None, ...]


def _source_series(anchor: AnchorMetrics) -> tuple[
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
]:
    revenue = tuple(float(v) for v in anchor.historical.revenue)
    owca = tuple(
        float(v)
        for v in anchor.reformulation.category_totals[
            "Operating Working Capital Asset"
        ]
    )
    owcl = tuple(
        float(v)
        for v in anchor.reformulation.category_totals[
            "Operating Working Capital Liability"
        ]
    )
    nowc = tuple(float(v) for v in anchor.reformulation.nowc)
    lengths = {
        "revenue": len(revenue),
        "owca": len(owca),
        "owcl": len(owcl),
        "nowc": len(nowc),
    }
    if len(set(lengths.values())) != 1 or lengths["revenue"] == 0:
        raise ValueError(
            "working-capital diagnostic series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )
    return revenue, owca, owcl, nowc


def working_capital_applicable(anchor: AnchorMetrics) -> bool:
    """True when at least one modeled-period OWCA or OWCL balance is nonzero."""
    _, owca, owcl, _ = _source_series(anchor)
    return any(v != 0.0 for v in owca) or any(v != 0.0 for v in owcl)


def compute_working_capital_series(anchor: AnchorMetrics) -> WorkingCapitalSeries:
    """Compute working-capital intensity and incremental diagnostics from AnchorMetrics."""
    revenue, owca, owcl, nowc = _source_series(anchor)
    n = len(revenue)

    owca_to_revenue = tuple(ratio_or_na(owca[i], revenue[i]) for i in range(n))
    owcl_to_revenue = tuple(ratio_or_na(owcl[i], revenue[i]) for i in range(n))
    nowc_to_revenue = tuple(ratio_or_na(nowc[i], revenue[i]) for i in range(n))

    revenue_change: list[float | None] = [None]
    nowc_change: list[float | None] = [None]
    incremental: list[float | str | None] = [None]
    for i in range(1, n):
        delta_revenue = revenue[i] - revenue[i - 1]
        delta_nowc = nowc[i] - nowc[i - 1]
        revenue_change.append(delta_revenue)
        nowc_change.append(delta_nowc)
        incremental.append(ratio_or_na(delta_nowc, delta_revenue))

    return WorkingCapitalSeries(
        owca_to_revenue=owca_to_revenue,
        owcl_to_revenue=owcl_to_revenue,
        nowc_to_revenue=nowc_to_revenue,
        revenue_change=tuple(revenue_change),
        nowc_change=tuple(nowc_change),
        incremental_nowc_to_revenue_change=tuple(incremental),
    )
