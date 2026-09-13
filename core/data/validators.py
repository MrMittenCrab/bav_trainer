"""Arithmetic checksum validators for standardized statements."""

from __future__ import annotations

from datetime import date

from .interface import StandardizedFinancials
from ..model.line_resolver import resolve_line


def _val_item(item, period: date) -> float | None:
    if item is None:
        return None
    return item.values.get(period)


def validate_income_statement(data: StandardizedFinancials) -> dict[date, bool]:
    results: dict[date, bool] = {}
    rev = resolve_line(data.income_statement, "revenue", required=False).item
    ni = resolve_line(data.income_statement, "net_income", required=False).item
    for period in data.period_dates():
        ok = True
        if rev is not None and ni is not None:
            if _val_item(rev, period) is None or _val_item(ni, period) is None:
                ok = False
        results[period] = ok
    return results


BALANCE_SHEET_TOLERANCE = 1.0


def validate_balance_sheet(
    data: StandardizedFinancials,
    *,
    tolerance: float = BALANCE_SHEET_TOLERANCE,
) -> dict[date, bool]:
    results: dict[date, bool] = {}
    ta = resolve_line(data.balance_sheet, "total_assets", required=False).item
    tl = resolve_line(data.balance_sheet, "total_liabilities", required=False).item
    te = resolve_line(data.balance_sheet, "total_equity", required=False).item
    for period in data.period_dates():
        ok = True
        if ta is not None and tl is not None and te is not None:
            a = _val_item(ta, period)
            l = _val_item(tl, period)
            e = _val_item(te, period)
            if None in (a, l, e):
                ok = False
            elif abs(float(a) - (float(l) + float(e))) > tolerance:
                ok = False
        results[period] = ok
    return results


def validate_cash_flow(data: StandardizedFinancials) -> dict[date, bool]:
    results: dict[date, bool] = {}
    items = data.cash_flow

    def _find(keywords: tuple[str, ...]):
        for item in items:
            low = item.label.lower()
            if any(k in low for k in keywords):
                return item
        return None

    cfo = _find(("operating activities", "cash from operating"))
    cfi = _find(("investing activities",))
    cff = _find(("financing activities",))
    net = _find(("net change", "increase in cash"))
    for period in data.period_dates():
        ok = True
        if cfo and cfi and cff and net:
            values = [_val_item(x, period) for x in (cfo, cfi, cff)]
            net_value = _val_item(net, period)
            if any(value is None for value in values) or net_value is None:
                ok = False
            else:
                total = sum(float(value) for value in values)
                ok = abs(total - float(net_value)) <= 1.0
        results[period] = ok
    return results
