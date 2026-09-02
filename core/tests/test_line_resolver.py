"""Canonical financial-line resolver tests (Step 2B)."""

from __future__ import annotations

from datetime import date

import pytest

from core.data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    LineItem,
    StandardizedFinancials,
)
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.financial_math import compute_anchor
from core.model.line_resolver import AmbiguousLineError, MissingLineError, resolve_line

ROOT = __file__
DEMO_JSON = __import__("pathlib").Path(__file__).resolve().parents[2] / "example" / "DEMO_HK_Standardized.json"

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _item(label: str, v1: float, v2: float, concept: str = "") -> LineItem:
    return LineItem(label=label, values={P1: v1, P2: v2}, concept=concept)


def _periods() -> list[FinancialPeriod]:
    return [
        FinancialPeriod(end_date=P1, label="FY2024"),
        FinancialPeriod(end_date=P2, label="FY2025"),
    ]


def test_demo_tax_regression_nopat_uses_income_tax_expense_not_pretax():
    """Must fail on pre-2B resolver that selects 'Profit before tax' as tax expense."""
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    periods = data.fiscal_years() or data.period_dates()
    last = periods[-1]

    pretax = next(i for i in data.income_statement if i.label == "Profit before tax")
    tax = next(i for i in data.income_statement if i.label == "Income tax expense")
    ni = next(i for i in data.income_statement if i.label == "Profit for the year")
    ie = next(i for i in data.income_statement if i.label == "Finance costs")
    ii = next(i for i in data.income_statement if i.label == "Finance income")

    # Independent fixture arithmetic — does not use the production resolver.
    net_int = -(float(ie.values[last]) + float(ii.values[last]))
    etr = -float(tax.values[last]) / float(pretax.values[last])
    niat = net_int * (1.0 - etr)
    expected_nopat = float(ni.values[last]) + niat

    tax_resolved = resolve_line(data.income_statement, "tax_expense")
    assert tax_resolved.item is not None
    assert tax_resolved.item.label == "Income tax expense"

    pretax_resolved = resolve_line(data.income_statement, "pretax_income")
    assert pretax_resolved.item is not None
    assert pretax_resolved.item.label == "Profit before tax"

    anchor = compute_anchor(data, periods)
    assert anchor.nopat == pytest.approx(expected_nopat, rel=1e-9)
    assert abs(anchor.nopat - 4262.0) > 1.0  # old buggy value


def test_misleading_labels_and_row_order():
    items = [
        _item("Cost of sales", -100, -110),
        _item("Profit before tax", 500, 600),
        _item("Income tax expense", -80, -90),
        _item("Revenue", 1000, 1100),
    ]
    tax = resolve_line(items, "tax_expense")
    rev = resolve_line(items, "revenue")
    assert tax.item is not None and tax.item.label == "Income tax expense"
    assert rev.item is not None and rev.item.label == "Revenue"
    assert tax.index == 2
    assert rev.index == 3


def test_explicit_concept_outranks_label():
    items = [
        _item("Income tax expense", -10, -12),
        _item("Something else", -99, -99, concept="tax_expense"),
    ]
    resolved = resolve_line(items, "tax_expense")
    assert resolved.item is not None
    assert resolved.item.label == "Something else"
    assert resolved.index == 1


def test_ambiguity_raises():
    items = [
        _item("Income tax expense", -10, -11),
        _item("Tax expense", -12, -13),
    ]
    with pytest.raises(AmbiguousLineError):
        resolve_line(items, "tax_expense", required=True)


def test_missing_required_raises():
    with pytest.raises(MissingLineError):
        resolve_line([_item("Other", 1, 2)], "net_income", required=True)


def test_optional_missing_returns_none():
    resolved = resolve_line([_item("Revenue", 1, 2)], "interest_income", required=False)
    assert resolved.item is None and resolved.index is None
