"""Arithmetic checksum validators for standardized statements."""

from __future__ import annotations

from datetime import date

from .interface import LineItem, StandardizedFinancials


def _val(items: list[LineItem], label: str, period: date) -> float | None:
    for item in items:
        if item.label == label:
            return item.values.get(period)
    return None


def _find_subtotal(items: list[LineItem], keywords: tuple[str, ...]) -> str | None:
    for item in items:
        low = item.label.lower()
        if any(k in low for k in keywords):
            return item.label
    return None


def validate_income_statement(data: StandardizedFinancials) -> dict[date, bool]:
    results: dict[date, bool] = {}
    items = data.income_statement
    rev_label = _find_subtotal(items, ("revenue", "turnover", "sales"))
    ni_label = _find_subtotal(items, ("net income", "profit for the year", "net profit"))
    for period in data.period_dates():
        ok = True
        if rev_label and ni_label:
            rev = _val(items, rev_label, period)
            ni = _val(items, ni_label, period)
            if rev is None or ni is None:
                ok = False
        results[period] = ok
    return results


def validate_balance_sheet(data: StandardizedFinancials) -> dict[date, bool]:
    results: dict[date, bool] = {}
    items = data.balance_sheet
    ta_label = _find_subtotal(items, ("total assets",))
    tl_label = _find_subtotal(items, ("total liabilities",))
    te_label = _find_subtotal(items, ("total equity", "total shareholders"))
    for period in data.period_dates():
        ok = True
        if ta_label and tl_label and te_label:
            ta = _val(items, ta_label, period)
            tl = _val(items, tl_label, period)
            te = _val(items, te_label, period)
            if None in (ta, tl, te):
                ok = False
            elif abs(ta - (tl + te)) > 0.5:
                ok = False
        results[period] = ok
    return results


def validate_cash_flow(data: StandardizedFinancials) -> dict[date, bool]:
    results: dict[date, bool] = {}
    items = data.cash_flow
    cfo = _find_subtotal(items, ("operating activities", "cash from operating"))
    cfi = _find_subtotal(items, ("investing activities",))
    cff = _find_subtotal(items, ("financing activities",))
    net = _find_subtotal(items, ("net change", "increase in cash"))
    for period in data.period_dates():
        ok = True
        if cfo and cfi and cff and net:
            total = sum(
                _val(items, lbl, period) or 0
                for lbl in (cfo, cfi, cff)
            )
            n = _val(items, net, period)
            if n is None:
                ok = False
            elif abs(total - n) > 1.0:
                ok = False
        results[period] = ok
    return results
