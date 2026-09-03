"""Python-side financial computations — authoritative expected values for trainer Check."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .classification import (
    BalanceSheetReformulation,
    check_reformulation_integrity,
    reformulate_balance_sheet,
)
from .line_resolver import resolve_line


def _val(item: LineItem | None, period: date) -> float:
    if item is None:
        return 0.0
    v = item.values.get(period)
    return float(v) if v is not None else 0.0


@dataclass
class AnchorMetrics:
    revenue: float
    nowc: float
    nola: float
    net_debt: float
    nopat: float
    equity: float
    noa: float
    leverage: float
    hist_avg_after_tax_cod: float  # already after-tax; do not multiply by (1 − tax) again
    effective_tax_rate: float
    net_interest: float
    net_interest_after_tax: float
    dupont: dict[str, list[float | str | None]]
    reformulation: BalanceSheetReformulation


def compute_anchor(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    classification_overrides: dict[str, str] | None = None,
    enforce_integrity: bool = True,
    tolerance: float = 1.0,
) -> AnchorMetrics:
    """Compute anchor and historical metrics from standardized financials."""
    is_items = fin.income_statement
    n = len(periods)
    if n < 1:
        raise ValueError("At least one period required")

    reform = reformulate_balance_sheet(
        fin, periods, overrides=classification_overrides
    )
    if enforce_integrity:
        check_reformulation_integrity(reform, periods, tolerance=tolerance)

    rev_item = resolve_line(is_items, "revenue", required=True).item
    ni_item = resolve_line(is_items, "net_income", required=True).item
    pretax_item = resolve_line(is_items, "pretax_income", required=False).item
    tax_item = resolve_line(is_items, "tax_expense", required=False).item
    int_exp_item = resolve_line(is_items, "interest_expense", required=False).item
    int_inc_item = resolve_line(is_items, "interest_income", required=False).item

    revenues = [_val(rev_item, p) for p in periods]
    ni = [_val(ni_item, p) for p in periods]
    int_exp = [_val(int_exp_item, p) for p in periods]
    int_inc = [_val(int_inc_item, p) for p in periods]
    pretax = [_val(pretax_item, p) for p in periods]
    tax = [_val(tax_item, p) for p in periods]

    net_int = [-(ie + ii) for ie, ii in zip(int_exp, int_inc)]
    etr = [(-tax[i] / pretax[i]) if pretax[i] else 0.0 for i in range(n)]
    niat = [net_int[i] * (1 - etr[i]) for i in range(n)]
    nopat = [ni[i] + niat[i] for i in range(n)]

    nowc = list(reform.nowc)
    nola = list(reform.nola)
    noa = list(reform.noa)
    net_debt = list(reform.net_debt)
    equity = list(reform.implied_equity)

    def avg(series: list[float], i: int) -> float:
        if i == 0:
            return series[0]
        return (series[i] + series[i - 1]) / 2

    dupont: dict[str, list[float | str | None]] = {k: [] for k in [
        "Sales Growth", "NOPAT Margin", "RNOA", "After-tax CoD", "Spread",
        "FLEV", "ROE (decomposed)", "Actual ROE",
    ]}
    cod_series: list[float] = []
    for i in range(n):
        if i == 0:
            dupont["Sales Growth"].append(None)
            dupont["NOPAT Margin"].append(nopat[0] / revenues[0] if revenues[0] else 0)
            dupont["RNOA"].append(None)
            dupont["After-tax CoD"].append(None)
            dupont["Spread"].append(None)
            dupont["FLEV"].append(None)
            dupont["ROE (decomposed)"].append(None)
            dupont["Actual ROE"].append(None)
            continue
        rnoa = nopat[i] / avg(noa, i) if avg(noa, i) else 0
        cod = niat[i] / avg(net_debt, i) if avg(net_debt, i) else 0
        cod_series.append(cod)
        flev = avg(net_debt, i) / avg(equity, i) if avg(equity, i) else 0
        spread = rnoa - cod
        decomposed = rnoa + flev * spread
        actual = ni[i] / avg(equity, i) if avg(equity, i) else 0
        dupont["Sales Growth"].append(revenues[i] / revenues[i - 1] - 1 if revenues[i - 1] else 0)
        dupont["NOPAT Margin"].append(nopat[i] / revenues[i] if revenues[i] else 0)
        dupont["RNOA"].append(rnoa)
        dupont["After-tax CoD"].append(cod)
        dupont["Spread"].append(spread)
        dupont["FLEV"].append(flev)
        dupont["ROE (decomposed)"].append(decomposed)
        dupont["Actual ROE"].append(actual)

    hist_avg_cod = sum(cod_series) / len(cod_series) if cod_series else 0.04
    last = n - 1
    total_capital = net_debt[last] + equity[last]
    leverage = net_debt[last] / total_capital if total_capital else 0

    return AnchorMetrics(
        revenue=revenues[last],
        nowc=nowc[last],
        nola=nola[last],
        net_debt=net_debt[last],
        nopat=nopat[last],
        equity=equity[last],
        noa=noa[last],
        leverage=leverage,
        hist_avg_after_tax_cod=hist_avg_cod,
        effective_tax_rate=etr[last],
        net_interest=net_int[last],
        net_interest_after_tax=niat[last],
        dupont=dupont,
        reformulation=reform,
    )
