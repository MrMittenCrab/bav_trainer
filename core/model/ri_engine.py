"""Residual-income (abnormal earnings) model engine — shared with bav-pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .financial_math import AnchorMetrics


@dataclass
class ScenarioResult:
    iv: float
    ivps: float
    terminal_rnoa: float
    abnormal_earnings_y1: float
    terminal_value_pv: float
    sales_y1: float
    nopat_y1: float


def run_scenario(
    scenario: dict[str, Any],
    anchor: AnchorMetrics,
    shares: float,
    hist_avg_after_tax_cod: float | None = None,
) -> ScenarioResult:
    """Compute residual-income valuation for one scenario."""
    ke = scenario["costOfEquity"]
    g = scenario["terminalGrowth"]
    tax = scenario.get("taxRate", 0.165)
    cod = (hist_avg_after_tax_cod or anchor.hist_avg_after_tax_cod) * (1 - tax)

    sales: list[float] = []
    prev = anchor.revenue
    for t in range(10):
        prev *= 1 + scenario["growthVector"][t]
        sales.append(prev)

    nowc_v, nola_v, nd_v, eq_v, nopat_v, ni_v, ae_v = [], [], [], [], [], [], []
    for t in range(10):
        if t == 0:
            nowc_t, nola_t, nd_t = anchor.nowc, anchor.nola, anchor.net_debt
        else:
            nowc_t = scenario["nowcRatioVector"][t] * sales[t]
            nola_t = scenario["nolaRatioVector"][t] * sales[t]
            nd_t = anchor.leverage * (nowc_t + nola_t)
        noa_t = nowc_t + nola_t
        eq_t = noa_t - nd_t
        nopat_t = sales[t] * scenario["marginVector"][t]
        ni_t = nopat_t - nd_t * cod
        ae_t = ni_t - ke * eq_t
        nowc_v.append(nowc_t)
        nola_v.append(nola_t)
        nd_v.append(nd_t)
        eq_v.append(eq_t)
        nopat_v.append(nopat_t)
        ni_v.append(ni_t)
        ae_v.append(ae_t)

    pv_ae = sum(ae_v[t] / (1 + ke) ** (t + 1) for t in range(10))
    tv = ae_v[9] * (1 + g) / (ke - g)
    pv_tv = tv / (1 + ke) ** 10
    iv = eq_v[0] + pv_ae + pv_tv
    term_rnoa = nopat_v[9] / (nowc_v[9] + nola_v[9]) if (nowc_v[9] + nola_v[9]) else 0

    return ScenarioResult(
        iv=iv,
        ivps=round(iv / shares, 4),
        terminal_rnoa=round(term_rnoa, 4),
        abnormal_earnings_y1=ae_v[0],
        terminal_value_pv=pv_tv,
        sales_y1=sales[0],
        nopat_y1=nopat_v[0],
    )


def weighted_ivps(
    results: dict[str, ScenarioResult],
    scenarios: dict[str, Any],
) -> float:
    total = sum(scenarios[name]["probability"] * results[name].ivps for name in results)
    return float(Decimal(str(total)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
