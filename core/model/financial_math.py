"""Python-side financial computations — authoritative expected values for trainer Check."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from ..data.interface import LineItem, StandardizedFinancials
from ..data.schema import normalize_label

CLASSIFICATIONS = {
    "cash": "FA",
    "short-term investment": "FA",
    "accounts receivable": "OWCA",
    "trade receivable": "OWCA",
    "inventory": "OWCA",
    "inventories": "OWCA",
    "prepaid": "OWCA",
    "property": "OLTA",
    "goodwill": "OLTA",
    "intangible": "OLTA",
    "accounts payable": "OWCL",
    "trade payable": "OWCL",
    "accrued": "OWCL",
    "deferred revenue": "OWCL",
    "long-term debt": "FL",
    "bank borrow": "FL",
    "lease": "OLTL",
}

CAT_NAMES = {
    "OWCA": "Operating Working Capital Asset",
    "OWCL": "Operating Working Capital Liability",
    "OLTA": "Operating Long-Term Asset",
    "OLTL": "Operating Long-Term Liability",
    "FA": "Financial Asset",
    "FL": "Financial Liability",
}


def guess_classification(label: str) -> str:
    low = label.lower()
    if "total" in low:
        return ""
    for key, cat in CLASSIFICATIONS.items():
        if key in low:
            return CAT_NAMES[cat]
    return "Ambiguous — Operating"


def _find_line(items: list[LineItem], *fragments: str) -> LineItem | None:
    for item in items:
        low = item.label.lower()
        if any(f in low for f in fragments):
            return item
    return None


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
    dupont: dict[str, list[float | str | None]]


def compute_anchor(fin: StandardizedFinancials, periods: list[date]) -> AnchorMetrics:
    """Compute anchor and historical metrics from standardized financials."""
    is_items = fin.income_statement
    bs_items = fin.balance_sheet
    n = len(periods)
    if n < 1:
        raise ValueError("At least one period required")

    rev_item = _find_line(is_items, "revenue", "turnover", "sales") or is_items[0]
    ni_item = _find_line(is_items, "net income", "profit for the year", "net profit")
    int_exp_item = _find_line(is_items, "interest expense", "finance cost")
    int_inc_item = _find_line(is_items, "interest income", "finance income")
    pretax_item = _find_line(is_items, "pretax", "before tax", "profit before tax")
    tax_item = _find_line(is_items, "tax", "income tax")

    revenues = [_val(rev_item, p) for p in periods]
    ni = [_val(ni_item, p) for p in periods]
    int_exp = [_val(int_exp_item, p) for p in periods]
    int_inc = [_val(int_inc_item, p) for p in periods]
    pretax = [_val(pretax_item, p) for p in periods]
    tax = [_val(tax_item, p) for p in periods]

    # Sign conventions: expenses negative in source data
    net_int = [-(ie + ii) for ie, ii in zip(int_exp, int_inc)]
    etr = [(-tax[i] / pretax[i]) if pretax[i] else 0.0 for i in range(n)]
    niat = [net_int[i] * (1 - etr[i]) for i in range(n)]
    nopat = [ni[i] + niat[i] for i in range(n)]

    # Classify balance sheet
    owca, owcl, olta, oltl, fa, fl = [], [], [], [], [], []
    for item in bs_items:
        if "total" in item.label.lower():
            continue
        cat = guess_classification(item.label)
        vals = [_val(item, p) for p in periods]
        if cat == "Operating Working Capital Asset":
            owca.append(vals)
        elif cat == "Operating Working Capital Liability":
            owcl.append(vals)
        elif cat == "Operating Long-Term Asset":
            olta.append(vals)
        elif cat == "Operating Long-Term Liability":
            oltl.append(vals)
        elif cat == "Financial Asset":
            fa.append(vals)
        elif cat == "Financial Liability":
            fl.append(vals)

    def _sum_rows(rows: list[list[float]]) -> list[float]:
        if not rows:
            return [0.0] * n
        return [sum(r[i] for r in rows) for i in range(n)]

    owca_t = _sum_rows(owca)
    owcl_t = _sum_rows(owcl)
    olta_t = _sum_rows(olta)
    oltl_t = _sum_rows(oltl)
    fa_t = _sum_rows(fa)
    fl_t = _sum_rows(fl)

    nowc = [owca_t[i] - owcl_t[i] for i in range(n)]
    nola = [olta_t[i] - oltl_t[i] for i in range(n)]
    noa = [nowc[i] + nola[i] for i in range(n)]
    net_debt = [fl_t[i] - fa_t[i] for i in range(n)]

    te_item = _find_line(bs_items, "total equity", "shareholders")
    equity = [_val(te_item, p) for p in periods] if te_item else [noa[i] - net_debt[i] for i in range(n)]

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
        dupont=dupont,
    )
