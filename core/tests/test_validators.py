"""Cash-flow / statement checksum validators — no missing-to-zero fabrication."""

from __future__ import annotations

from datetime import date

from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
from core.data.validators import validate_cash_flow

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _fin(cf_items: list[LineItem]) -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="CF",
        company_name="CF Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=P1, label="FY2024"),
            FinancialPeriod(end_date=P2, label="FY2025"),
        ],
        income_statement=[LineItem(label="Revenue", values={P1: 1, P2: 1})],
        balance_sheet=[LineItem(label="Cash", values={P1: 1, P2: 1})],
        cash_flow=cf_items,
    )


def _complete_cf(**overrides: dict) -> list[LineItem]:
    values = {
        "cfo": {P1: 80, P2: 90},
        "cfi": {P1: -20, P2: -25},
        "cff": {P1: -10, P2: -15},
        "net": {P1: 50, P2: 50},
    }
    values.update(overrides)
    return [
        LineItem(label="Net cash from operating activities", values=values["cfo"]),
        LineItem(label="Net cash used in investing activities", values=values["cfi"]),
        LineItem(label="Net cash from financing activities", values=values["cff"]),
        LineItem(label="Net change in cash and cash equivalents", values=values["net"]),
    ]


def test_validate_cash_flow_complete_and_explicit_zero():
    results = validate_cash_flow(_fin(_complete_cf()))
    assert results[P1] is True
    assert results[P2] is True

    zero_cfi = _complete_cf(cfi={P1: 0, P2: 0}, net={P1: 70, P2: 75})
    results = validate_cash_flow(_fin(zero_cfi))
    assert results[P1] is True
    assert results[P2] is True


def test_validate_cash_flow_missing_period_values_fail():
    missing_cfi = _complete_cf()
    del missing_cfi[1].values[P2]
    results = validate_cash_flow(_fin(missing_cfi))
    assert results[P1] is True
    assert results[P2] is False

    none_cff = _complete_cf()
    none_cff[2].values[P1] = None
    results = validate_cash_flow(_fin(none_cff))
    assert results[P1] is False
    assert results[P2] is True

    missing_net = _complete_cf()
    del missing_net[3].values[P2]
    results = validate_cash_flow(_fin(missing_net))
    assert results[P1] is True
    assert results[P2] is False
