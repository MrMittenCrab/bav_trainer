"""Step 9M.8 — PP&E capex source resolution and sign contract."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.interface import (
    FinancialPeriod,
    LineItem,
    StandardizedFinancials,
)
from core.data.standardized_io import standardized_from_payload
from core.model.capex import (
    capex_applicable,
    capex_availability,
    compute_capex_series,
    resolve_capex_source,
)
from core.model.line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from core.model.period_axis import canonical_fiscal_periods
from core.model.source_values import MissingHistoricalValueError

ROOT = Path(__file__).resolve().parents[2]
STD_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _li(label, values, concept=""):
    return LineItem(label=label, values=values, concept=concept)


def _tiny(
    *,
    payments=(-100.0, -120.0),
    with_payments: bool = True,
    label_only: bool = False,
    duplicate: bool = False,
    missing_period: bool = False,
    none_period: bool = False,
    payments_first: bool = False,
    on_balance_sheet: bool = False,
    single_period: bool = False,
):
    if single_period:
        d1 = date(2025, 12, 31)
        periods = [FinancialPeriod(end_date=d1, label="FY2025")]

        def vals(a, b=None):
            return {d1: a}

        pay_vals = (payments[0],)
    else:
        d1, d2 = P1, P2
        periods = [
            FinancialPeriod(end_date=d1, label="FY2024"),
            FinancialPeriod(end_date=d2, label="FY2025"),
        ]

        def vals(a, b=None):
            return {d1: a, d2: b if b is not None else a}

        pay_vals = payments

    concept = "" if label_only else "payments_for_ppe"
    if missing_period and not single_period:
        pay_values = {P1: pay_vals[0]}
    elif none_period and not single_period:
        pay_values = {P1: pay_vals[0], P2: None}
    elif single_period:
        pay_values = vals(pay_vals[0])
    else:
        pay_values = vals(*pay_vals)

    pay_item = _li(
        "Payments for property, plant and equipment",
        pay_values,
        concept=concept,
    )

    bs = [
        _li("Cash and cash equivalents", vals(50, 50)),
        _li("Trade receivables", vals(40, 40)),
        _li("Trade payables", vals(30, 30)),
        _li("Bank borrowings", vals(20, 20)),
        _li("Total equity", vals(40, 40)),
    ]
    cf = [
        _li(
            "Net cash from operating activities",
            vals(80, 90) if not single_period else vals(80),
        ),
    ]
    if with_payments:
        target = bs if on_balance_sheet else cf
        if payments_first:
            target.insert(0, pay_item)
        else:
            target.append(pay_item)
        if duplicate and not on_balance_sheet:
            cf.append(
                _li(
                    "Payments for PPE duplicate",
                    vals(*pay_vals) if not single_period else vals(pay_vals[0]),
                    concept="payments_for_ppe",
                )
            )

    return StandardizedFinancials(
        ticker="CAPEX",
        company_name="Capex Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=periods,
        income_statement=[
            _li(
                "Revenue",
                vals(1000, 1100) if not single_period else vals(1000),
            ),
            _li(
                "Profit for the year",
                vals(170, 187) if not single_period else vals(170),
            ),
        ],
        balance_sheet=bs,
        cash_flow=cf,
    )


def test_unique_concept_resolution_and_renamed_label():
    fin = _tiny()
    item = resolve_capex_source(fin)
    assert item is not None
    assert item.concept == "payments_for_ppe"
    assert item.label == "Payments for property, plant and equipment"
    assert capex_applicable(fin)
    avail = capex_availability(fin)
    assert avail.payments_for_ppe is True and avail.ambiguous is False

    renamed = _tiny()
    renamed.cash_flow[-1] = _li(
        "Purchase of fixed assets (renamed)",
        {P1: -100.0, P2: -120.0},
        concept="payments_for_ppe",
    )
    assert resolve_capex_source(renamed) is not None
    assert resolve_capex_source(renamed).label == "Purchase of fixed assets (renamed)"


def test_reordered_rows_still_resolve():
    first = _tiny(payments_first=True)
    last = _tiny(payments_first=False)
    assert resolve_capex_source(first) is not None
    assert resolve_capex_source(last) is not None
    assert resolve_capex_source(first).values == resolve_capex_source(last).values


def test_absent_label_only_duplicate_wrong_statement():
    absent = _tiny(with_payments=False)
    assert not capex_applicable(absent)
    assert resolve_capex_source(absent) is None
    assert capex_availability(absent).payments_for_ppe is False
    with pytest.raises(MissingLineError):
        compute_capex_series(absent, list(canonical_fiscal_periods(absent)))

    label_only = _tiny(label_only=True)
    assert not capex_applicable(label_only)
    assert resolve_capex_source(label_only) is None
    assert (
        resolve_line(
            label_only.cash_flow, "payments_for_ppe", required=False
        ).item
        is None
    )

    dup = _tiny(duplicate=True)
    avail = capex_availability(dup)
    assert avail.ambiguous is True
    assert avail.payments_for_ppe is False
    assert not capex_applicable(dup)
    assert resolve_capex_source(dup) is None
    with pytest.raises(AmbiguousLineError):
        resolve_line(dup.cash_flow, "payments_for_ppe", required=False)

    wrong = _tiny(on_balance_sheet=True)
    assert not capex_applicable(wrong)
    assert resolve_capex_source(wrong) is None
    # Concept exists on BS but CF resolution stays empty.
    assert (
        resolve_line(wrong.balance_sheet, "payments_for_ppe", required=False).item
        is not None
    )


def test_sign_conversion_negative_positive_mixed_and_zero():
    negative = _tiny(payments=(-50.0, -80.0))
    series_neg = compute_capex_series(
        negative, list(canonical_fiscal_periods(negative))
    )
    assert series_neg.payments_reported == (-50.0, -80.0)
    assert series_neg.ppe_capex == (50.0, 80.0)

    positive = _tiny(payments=(50.0, 80.0))
    series_pos = compute_capex_series(
        positive, list(canonical_fiscal_periods(positive))
    )
    assert series_pos.payments_reported == (50.0, 80.0)
    assert series_pos.ppe_capex == (-50.0, -80.0)

    mixed = _tiny(payments=(-50.0, 80.0))
    series_mix = compute_capex_series(mixed, list(canonical_fiscal_periods(mixed)))
    assert series_mix.payments_reported == (-50.0, 80.0)
    assert series_mix.ppe_capex == (50.0, -80.0)

    zero = _tiny(payments=(0.0, -10.0))
    series_z = compute_capex_series(zero, list(canonical_fiscal_periods(zero)))
    assert series_z.payments_reported == (0.0, -10.0)
    assert series_z.ppe_capex == (0.0, 10.0)


def test_missing_none_period_ordering_and_unchanged_input():
    missing = _tiny(missing_period=True)
    periods = list(canonical_fiscal_periods(missing))
    with pytest.raises(MissingHistoricalValueError):
        compute_capex_series(missing, periods)

    none_period = _tiny(none_period=True)
    with pytest.raises(MissingHistoricalValueError):
        compute_capex_series(none_period, list(canonical_fiscal_periods(none_period)))

    fin = _tiny(payments=(-10.0, -20.0))
    # Request periods in reverse chronological order — values follow request order.
    reverse = [P2, P1]
    series = compute_capex_series(fin, reverse)
    assert series.payments_reported == (-20.0, -10.0)
    assert series.ppe_capex == (20.0, 10.0)

    # Source values must not be mutated.
    before = copy.deepcopy(resolve_capex_source(fin).values)
    compute_capex_series(fin, [P1, P2])
    after = resolve_capex_source(fin).values
    assert after == before


def test_fast_retailing_fy2021_fy2025_capex_anchors():
    payload = json.loads(STD_JSON.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    assert capex_applicable(fin)
    periods = list(canonical_fiscal_periods(fin))
    assert [p.isoformat() for p in periods] == [
        "2021-08-31",
        "2022-08-31",
        "2023-08-31",
        "2024-08-31",
        "2025-08-31",
    ]
    series = compute_capex_series(fin, periods)
    assert series.payments_reported == (
        -56500.0,
        -51271.0,
        -61764.0,
        -73728.0,
        -135535.0,
    )
    assert series.ppe_capex == (56500.0, 51271.0, 61764.0, 73728.0, 135535.0)
