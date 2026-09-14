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


def test_curly_apostrophe_equity_alias_resolves():
    items = [_item("Shareholders\u2019 equity", 100, 110)]
    resolved = resolve_line(items, "total_equity", required=True)
    assert resolved.item is not None
    assert resolved.item.label == "Shareholders\u2019 equity"


def test_operating_cash_flow_aliases_and_non_alias():
    assert resolve_line(
        [_item("Net cash from operating activities", 1, 2)],
        "operating_cash_flow",
    ).item is not None
    assert (
        resolve_line(
            [_item("Cash generated from operations", 1, 2)],
            "operating_cash_flow",
            required=False,
        ).item
        is None
    )


def test_ppe_and_da_aliases_and_concepts():
    ppe = resolve_line(
        [_item("Property, plant and equipment", 100, 110)],
        "property_plant_equipment",
        required=True,
    )
    assert ppe.item is not None
    assert ppe.item.label == "Property, plant and equipment"

    ppe_concept = resolve_line(
        [_item("Fixed assets", 100, 110, concept="property_plant_equipment")],
        "property_plant_equipment",
        required=True,
    )
    assert ppe_concept.item is not None
    assert ppe_concept.item.label == "Fixed assets"

    da = resolve_line(
        [_item("Depreciation and amortisation", -10, -12)],
        "depreciation_amortization",
        required=True,
    )
    assert da.item is not None
    assert da.item.label == "Depreciation and amortisation"

    da_us = resolve_line(
        [_item("Depreciation and amortization", -10, -12)],
        "depreciation_amortization",
        required=True,
    )
    assert da_us.item is not None

    assert (
        resolve_line(
            [_item("Depreciation", -1, -2)],
            "depreciation_amortization",
            required=False,
        ).item
        is None
    )
    assert (
        resolve_line(
            [_item("Equipment", 1, 2)],
            "property_plant_equipment",
            required=False,
        ).item
        is None
    )


def test_ppe_property_plant_and_equipment_concept_alias():
    """Alias concept resolves at P1; stored concept is left unchanged."""
    items = [
        _item(
            "Neutral carrying label",
            100,
            110,
            concept="property_plant_and_equipment",
        )
    ]
    resolved = resolve_line(items, "property_plant_equipment", required=True)
    assert resolved.item is not None
    assert resolved.index == 0
    assert resolved.item.label == "Neutral carrying label"
    assert resolved.item.concept == "property_plant_and_equipment"


def test_ppe_net_balance_label_aliases():
    for label in (
        "Property and equipment, net",
        "Property plant and equipment, net",
        "Property and equipment net",
        "Property plant and equipment net",
    ):
        resolved = resolve_line(
            [_item(label, 100, 110)],
            "property_plant_equipment",
            required=True,
        )
        assert resolved.item is not None
        assert resolved.item.label == label


def test_ppe_explicit_concept_outranks_label():
    items = [
        _item("Property and equipment, net", 1, 2),
        _item("Other carrying amount", 100, 110, concept="property_plant_equipment"),
    ]
    resolved = resolve_line(items, "property_plant_equipment", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Other carrying amount"


def test_ppe_canonical_and_alias_concepts_are_ambiguous_together():
    items = [
        _item("First", 1, 2, concept="property_plant_equipment"),
        _item("Second", 3, 4, concept="property_plant_and_equipment"),
    ]
    with pytest.raises(AmbiguousLineError):
        resolve_line(items, "property_plant_equipment", required=False)


def test_ppe_movement_labels_are_not_near_matches():
    for label in (
        "Purchases of property and equipment",
        "Proceeds from sale of property and equipment",
        "Depreciation of property and equipment",
        "Impairment of property and equipment",
        "Purchase of property and equipment",
        "Property and equipment additions",
        "Property and equipment disposals",
        "Property and equipment payments",
        "Property and equipment sales",
        "Property and equipment changes",
        "Purchases of property, plant and equipment",
        "Property, plant and equipment additions",
        "Accounts payable for property and equipment",
        "Property and equipment payable",
    ):
        assert (
            resolve_line(
                [_item(label, 1, 2)],
                "property_plant_equipment",
                required=False,
            ).item
            is None
        )


def test_lease_liability_aggregate_aliases_and_ambiguity():
    lease = resolve_line(
        [_item("Operating lease liabilities", 100, 120)],
        "lease_liability",
        required=True,
    )
    assert lease.item is not None
    assert lease.item.label == "Operating lease liabilities"

    by_concept = resolve_line(
        [_item("Total lease balance", 100, 120, concept="lease_liability")],
        "lease_liability",
        required=True,
    )
    assert by_concept.item is not None
    assert by_concept.item.label == "Total lease balance"

    assert (
        resolve_line(
            [_item("Current lease liabilities", 40, 50)],
            "lease_liability",
            required=False,
        ).item
        is None
    )
    assert (
        resolve_line(
            [_item("Non-current lease liabilities", 60, 70)],
            "lease_liability",
            required=False,
        ).item
        is None
    )

    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("Current lease liabilities", 40, 50, concept="lease_liability"),
                _item(
                    "Non-current lease liabilities", 60, 70, concept="lease_liability"
                ),
            ],
            "lease_liability",
            required=False,
        )


@pytest.mark.parametrize(
    "concept",
    (
        "goodwill",
        "intangible_assets",
        "payments_for_intangible_assets",
        "payments_for_ppe",
        "repayments_of_lease_liabilities",
    ),
)
def test_goodwill_intangible_explicit_concept_only(concept):
    by_concept = resolve_line(
        [_item("Unrelated label", 10, 12, concept=concept)],
        concept,
        required=True,
    )
    assert by_concept.item is not None
    assert by_concept.item.label == "Unrelated label"
    assert by_concept.index == 0

    label_only = resolve_line(
        [_item(concept.replace("_", " ").title(), 10, 12)],
        concept,
        required=False,
    )
    assert label_only.item is None and label_only.index is None

    with pytest.raises(MissingLineError):
        resolve_line(
            [_item(concept.replace("_", " ").title(), 10, 12)],
            concept,
            required=True,
        )

    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept=concept),
                _item("Second", 3, 4, concept=concept),
            ],
            concept,
            required=False,
        )
