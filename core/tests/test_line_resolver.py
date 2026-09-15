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
        "Property plant & equipment additions",
        "Property, plant, and equipment disposals",
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


def test_pretax_income_canonical_and_income_before_tax_alias():
    """Canonical pretax_income and supplied income_before_tax both resolve at P1."""
    canonical = resolve_line(
        [_item("Carrying label", 100, 110, concept="pretax_income")],
        "pretax_income",
        required=True,
    )
    assert canonical.item is not None
    assert canonical.index == 0
    assert canonical.item.concept == "pretax_income"

    alias = resolve_line(
        [_item("Income before income tax expense", 100, 110, concept="income_before_tax")],
        "pretax_income",
        required=True,
    )
    assert alias.item is not None
    assert alias.index == 0
    assert alias.item.concept == "income_before_tax"
    assert alias.item.label == "Income before income tax expense"


def test_pretax_income_normalized_label_fallback():
    """Exact supplied label resolves when explicit concept identity is unavailable."""
    resolved = resolve_line(
        [_item("Income before income tax expense", 100, 110)],
        "pretax_income",
        required=True,
    )
    assert resolved.item is not None
    assert resolved.item.label == "Income before income tax expense"
    assert resolved.item.concept == ""


def test_pretax_income_explicit_concept_outranks_label():
    items = [
        _item("Income before income tax expense", 1, 2),
        _item("Other pretax carrying amount", 100, 110, concept="income_before_tax"),
    ]
    resolved = resolve_line(items, "pretax_income", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Other pretax carrying amount"
    assert resolved.item.concept == "income_before_tax"


def test_pretax_income_canonical_and_alias_concepts_are_ambiguous_together():
    items = [
        _item("First", 1, 2, concept="pretax_income"),
        _item("Second", 3, 4, concept="income_before_tax"),
    ]
    with pytest.raises(AmbiguousLineError):
        resolve_line(items, "pretax_income", required=False)


def test_pretax_income_missing_required_and_nearby_nonmatching_labels():
    with pytest.raises(MissingLineError):
        resolve_line([_item("Other", 1, 2)], "pretax_income", required=True)

    for label in (
        "Income tax expense",
        "Income from operations",
        "Income before extraordinary items",
        "Provision for income taxes",
    ):
        assert (
            resolve_line(
                [_item(label, 1, 2)],
                "pretax_income",
                required=False,
            ).item
            is None
        )


def test_pretax_label_does_not_resolve_as_tax_expense():
    """Supplied pretax label must stay distinct from tax_expense (pre-repair P3 leak)."""
    pretax_only = [_item("Income before income tax expense", 100, 110)]
    assert resolve_line(pretax_only, "tax_expense", required=False).item is None
    with pytest.raises(MissingLineError):
        resolve_line(pretax_only, "tax_expense", required=True)

    both = [
        _item("Income before income tax expense", 100, 110, concept="income_before_tax"),
        _item("Income tax expense", -30, -33, concept="income_tax_expense"),
    ]
    pretax = resolve_line(both, "pretax_income", required=True)
    tax = resolve_line(both, "tax_expense", required=True)
    assert pretax.item is not None and pretax.index == 0
    assert tax.item is not None and tax.index == 1
    assert tax.item.label == "Income tax expense"


def test_income_before_tax_alias_removal_fails_closed(monkeypatch):
    """Parity regressions detect removal of the income_before_tax explicit alias."""
    from core.model import line_resolver as lr

    items = [
        _item("Income before income tax expense", 100, 110, concept="income_before_tax"),
        _item("Income tax expense", -30, -33),
    ]
    assert resolve_line(items, "pretax_income", required=True).item is not None

    monkeypatch.setattr(
        lr,
        "_EXPLICIT_CONCEPT_ALIASES",
        {**lr._EXPLICIT_CONCEPT_ALIASES, "pretax_income": frozenset({"pretax income"})},
    )
    monkeypatch.setattr(
        lr,
        "_EXACT_ALIASES",
        {
            **lr._EXACT_ALIASES,
            "pretax_income": lr._EXACT_ALIASES["pretax_income"]
            - {"income before income tax expense"},
        },
    )
    with pytest.raises(MissingLineError, match="pretax_income"):
        resolve_line(items, "pretax_income", required=True)


def test_payments_for_ppe_canonical_and_capital_expenditures_alias():
    """Canonical payments_for_ppe and supplied capital_expenditures both resolve at P1."""
    canonical = resolve_line(
        [_item("Carrying label", -100, -110, concept="payments_for_ppe")],
        "payments_for_ppe",
        required=True,
    )
    assert canonical.item is not None
    assert canonical.index == 0
    assert canonical.item.concept == "payments_for_ppe"

    alias = resolve_line(
        [_item("Purchase of property and equipment", -100, -110, concept="capital_expenditures")],
        "payments_for_ppe",
        required=True,
    )
    assert alias.item is not None
    assert alias.index == 0
    assert alias.item.concept == "capital_expenditures"
    assert alias.item.label == "Purchase of property and equipment"
    assert alias.item.values == {P1: -100, P2: -110}


def test_payments_for_ppe_rejects_unsupported_label_only_inputs():
    """Capex remains explicit-concept; nearby labels do not activate the contract."""
    for label in (
        "Purchase of property and equipment",
        "Payments for property, plant and equipment",
        "Capital expenditures",
        "Payments for PPE",
        "Purchase of fixed assets",
    ):
        assert (
            resolve_line(
                [_item(label, -100, -110)],
                "payments_for_ppe",
                required=False,
            ).item
            is None
        )
    with pytest.raises(MissingLineError):
        resolve_line(
            [_item("Purchase of property and equipment", -100, -110)],
            "payments_for_ppe",
            required=True,
        )


def test_payments_for_ppe_explicit_concept_outranks_label():
    items = [
        _item("Purchase of property and equipment", -1, -2),
        _item("Other capex carrying amount", -100, -110, concept="capital_expenditures"),
    ]
    resolved = resolve_line(items, "payments_for_ppe", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Other capex carrying amount"
    assert resolved.item.concept == "capital_expenditures"


def test_payments_for_ppe_canonical_and_alias_concepts_are_ambiguous_together():
    items = [
        _item("First", -1, -2, concept="payments_for_ppe"),
        _item("Second", -3, -4, concept="capital_expenditures"),
    ]
    with pytest.raises(AmbiguousLineError):
        resolve_line(items, "payments_for_ppe", required=False)


def test_capital_expenditures_alias_removal_fails_closed(monkeypatch):
    """Capex coverage fails closed if the capital_expenditures explicit alias is removed."""
    from core.model import line_resolver as lr

    items = [
        _item(
            "Purchase of property and equipment",
            -100,
            -110,
            concept="capital_expenditures",
        )
    ]
    assert resolve_line(items, "payments_for_ppe", required=True).item is not None

    monkeypatch.setattr(
        lr,
        "_EXPLICIT_CONCEPT_ALIASES",
        {
            k: v
            for k, v in lr._EXPLICIT_CONCEPT_ALIASES.items()
            if k != "payments_for_ppe"
        },
    )
    with pytest.raises(MissingLineError, match="payments_for_ppe"):
        resolve_line(items, "payments_for_ppe", required=True)


_ROU_DT_ALIAS_CASES = (
    (
        "right_of_use_assets",
        "right_of_use_lease_asset",
        "Right-of-use lease assets",
        ("Right-of-use assets", "Right of use lease assets", "ROU assets"),
    ),
    (
        "deferred_tax_assets",
        "deferred_tax_asset",
        "Deferred income tax assets",
        ("Deferred tax assets", "Deferred tax asset", "Income tax assets"),
    ),
    (
        "deferred_tax_liabilities",
        "deferred_tax_liability",
        "Deferred income tax liabilities",
        ("Deferred tax liabilities", "Deferred tax liability", "Income tax liabilities"),
    ),
)


@pytest.mark.parametrize(
    "canonical, alias, alias_label, nearby_labels",
    _ROU_DT_ALIAS_CASES,
)
def test_rou_deferred_tax_canonical_and_explicit_concept_alias(
    canonical, alias, alias_label, nearby_labels
):
    """Canonical and supplied alias both resolve at P1; stored identity is unchanged."""
    canon_item = _item("Carrying label", 100, 110, concept=canonical)
    resolved_canon = resolve_line([canon_item], canonical, required=True)
    assert resolved_canon.item is not None
    assert resolved_canon.index == 0
    assert resolved_canon.item.concept == canonical

    alias_item = _item(alias_label, 100, 110, concept=alias)
    resolved_alias = resolve_line([alias_item], canonical, required=True)
    assert resolved_alias.item is not None
    assert resolved_alias.index == 0
    assert resolved_alias.item.concept == alias
    assert resolved_alias.item.label == alias_label
    assert resolved_alias.item.values == {P1: 100, P2: 110}


@pytest.mark.parametrize(
    "canonical, alias, alias_label, nearby_labels",
    _ROU_DT_ALIAS_CASES,
)
def test_rou_deferred_tax_rejects_unsupported_label_only_inputs(
    canonical, alias, alias_label, nearby_labels
):
    """Lease ROU and deferred-tax remain explicit-concept; nearby labels do not activate."""
    for label in (alias_label, *nearby_labels):
        assert (
            resolve_line([_item(label, 100, 110)], canonical, required=False).item
            is None
        )
    with pytest.raises(MissingLineError):
        resolve_line([_item(alias_label, 100, 110)], canonical, required=True)


@pytest.mark.parametrize(
    "canonical, alias, alias_label, nearby_labels",
    _ROU_DT_ALIAS_CASES,
)
def test_rou_deferred_tax_explicit_concept_outranks_label(
    canonical, alias, alias_label, nearby_labels
):
    items = [
        _item(alias_label, -1, -2),
        _item("Misleading carrying amount", 100, 110, concept=alias),
    ]
    resolved = resolve_line(items, canonical, required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Misleading carrying amount"
    assert resolved.item.concept == alias


@pytest.mark.parametrize(
    "canonical, alias, alias_label, nearby_labels",
    _ROU_DT_ALIAS_CASES,
)
def test_rou_deferred_tax_canonical_and_alias_concepts_are_ambiguous_together(
    canonical, alias, alias_label, nearby_labels
):
    items = [
        _item("First", 1, 2, concept=canonical),
        _item("Second", 1, 2, concept=alias),
    ]
    with pytest.raises(AmbiguousLineError):
        resolve_line(items, canonical, required=False)


@pytest.mark.parametrize(
    "canonical, alias, alias_label, nearby_labels",
    _ROU_DT_ALIAS_CASES,
)
def test_rou_deferred_tax_alias_removal_fails_closed(
    monkeypatch, canonical, alias, alias_label, nearby_labels
):
    from core.model import line_resolver as lr

    items = [_item(alias_label, 100, 110, concept=alias)]
    assert resolve_line(items, canonical, required=True).item is not None

    monkeypatch.setattr(
        lr,
        "_EXPLICIT_CONCEPT_ALIASES",
        {k: v for k, v in lr._EXPLICIT_CONCEPT_ALIASES.items() if k != canonical},
    )
    with pytest.raises(MissingLineError, match=canonical):
        resolve_line(items, canonical, required=True)


def test_acquisition_net_of_cash_acquired_rejects_unsupported_label_only_inputs():
    """Acquisition cash remains explicit-concept; nearby labels do not activate."""
    for label in (
        "Acquisition, net of cash acquired",
        "Acquisitions",
        "Business acquisitions",
        "Payments for acquisition of right-of-use assets",
        "Payments for intangible assets",
    ):
        assert (
            resolve_line(
                [_item(label, -100, -110)],
                "acquisition_net_of_cash_acquired",
                required=False,
            ).item
            is None
        )
    with pytest.raises(MissingLineError):
        resolve_line(
            [_item("Acquisition, net of cash acquired", -100, -110)],
            "acquisition_net_of_cash_acquired",
            required=True,
        )


def test_acquisition_net_of_cash_acquired_explicit_concept_outranks_label():
    items = [
        _item("Acquisition, net of cash acquired", -1, -2),
        _item(
            "Other acquisition carrying amount",
            -100,
            -110,
            concept="acquisition_net_of_cash_acquired",
        ),
    ]
    resolved = resolve_line(items, "acquisition_net_of_cash_acquired", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Other acquisition carrying amount"
    assert resolved.item.concept == "acquisition_net_of_cash_acquired"


def test_repurchase_of_common_stock_rejects_unsupported_label_only_inputs():
    """Share-repurchase cash remains explicit-concept; nearby labels do not activate."""
    for label in (
        "Repurchase of common stock",
        "Payments for repurchase of common stock",
        "Treasury stock",
        "Stock-based compensation expense",
        "Proceeds from settlement of stock-based compensation",
        "Shares withheld related to net share settlement",
        "Dividends paid",
    ):
        assert (
            resolve_line(
                [_item(label, -100, -110)],
                "repurchase_of_common_stock",
                required=False,
            ).item
            is None
        )
    with pytest.raises(MissingLineError):
        resolve_line(
            [_item("Repurchase of common stock", -100, -110)],
            "repurchase_of_common_stock",
            required=True,
        )


def test_repurchase_of_common_stock_explicit_concept_outranks_label():
    items = [
        _item("Repurchase of common stock", -1, -2),
        _item(
            "Other repurchase carrying amount",
            -100,
            -110,
            concept="repurchase_of_common_stock",
        ),
    ]
    resolved = resolve_line(items, "repurchase_of_common_stock", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.label == "Other repurchase carrying amount"
    assert resolved.item.concept == "repurchase_of_common_stock"


def test_cash_rollforward_explicit_aliases_and_label_only_rejection():
    operating = resolve_line(
        [_item("Neutral", 1, 2, concept="net_cash_from_operating_activities")],
        "net_cash_from_operating_activities",
        required=True,
    )
    assert operating.item is not None
    assert operating.item.concept == "net_cash_from_operating_activities"

    alias_operating = resolve_line(
        [_item("Neutral FR", 1, 2, concept="operating_cash_flow")],
        "net_cash_from_operating_activities",
        required=True,
    )
    assert alias_operating.item is not None
    assert alias_operating.item.concept == "operating_cash_flow"

    investing = resolve_line(
        [_item("Neutral", 1, 2, concept="investing_cash_flow")],
        "net_cash_from_investing_activities",
        required=True,
    )
    assert investing.item is not None
    assert investing.item.concept == "investing_cash_flow"

    financing = resolve_line(
        [_item("Neutral", 1, 2, concept="financing_cash_flow")],
        "net_cash_from_financing_activities",
        required=True,
    )
    assert financing.item is not None

    fx = resolve_line(
        [_item("Neutral", 1, 2, concept="effect_of_exchange_rate_on_cash")],
        "effect_of_fx_on_cash",
        required=True,
    )
    assert fx.item is not None
    assert fx.item.concept == "effect_of_exchange_rate_on_cash"

    change = resolve_line(
        [_item("Neutral", 1, 2, concept="net_change_in_cash")],
        "change_in_cash",
        required=True,
    )
    assert change.item is not None
    assert change.item.concept == "net_change_in_cash"

    for concept, label in (
        ("net_cash_from_operating_activities", "Net cash from operating activities"),
        ("net_cash_from_operating_activities", "Cash generated from operations"),
        ("effect_of_fx_on_cash", "Effect of foreign currency exchange rate changes"),
        ("effect_of_fx_on_cash", "Foreign exchange losses/(gains)"),
        ("change_in_cash", "Increase (decrease) in cash and cash equivalents"),
        ("cash_beginning", "Cash and cash equivalents, beginning of period"),
        ("cash_ending", "Cash and cash equivalents, end of period"),
        ("cash_beginning", "Cash and cash equivalents"),
    ):
        assert (
            resolve_line([_item(label, 1, 2)], concept, required=False).item is None
        )


def test_cash_rollforward_competing_aliases_are_ambiguous():
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="effect_of_fx_on_cash"),
                _item("Second", 3, 4, concept="effect_of_exchange_rate_on_cash"),
            ],
            "effect_of_fx_on_cash",
            required=False,
        )
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="change_in_cash"),
                _item("Second", 3, 4, concept="net_change_in_cash"),
            ],
            "change_in_cash",
            required=False,
        )
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="net_cash_from_operating_activities"),
                _item("Second", 3, 4, concept="operating_cash_flow"),
            ],
            "net_cash_from_operating_activities",
            required=False,
        )


def test_cash_rollforward_explicit_concept_outranks_label():
    items = [
        _item("Net cash from operating activities", 1, 2),
        _item("Other operating total", 80, 90, concept="operating_cash_flow"),
    ]
    resolved = resolve_line(items, "net_cash_from_operating_activities", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.concept == "operating_cash_flow"


def test_reported_margin_explicit_aliases_and_label_only_rejection():
    gross = resolve_line(
        [_item("Neutral", 1, 2, concept="gross_profit")],
        "gross_profit",
        required=True,
    )
    assert gross.item is not None
    assert gross.item.concept == "gross_profit"

    operating = resolve_line(
        [_item("Neutral", 1, 2, concept="operating_profit")],
        "operating_profit",
        required=True,
    )
    assert operating.item is not None
    assert operating.item.concept == "operating_profit"

    alias_operating = resolve_line(
        [_item("Neutral LULU", 1, 2, concept="operating_income")],
        "operating_profit",
        required=True,
    )
    assert alias_operating.item is not None
    assert alias_operating.item.concept == "operating_income"

    for concept, label in (
        ("gross_profit", "Gross profit"),
        ("operating_profit", "Operating profit"),
        ("operating_profit", "Income from operations"),
        ("operating_profit", "Operating income"),
    ):
        assert resolve_line([_item(label, 1, 2)], concept, required=False).item is None


def test_reported_margin_competing_aliases_are_ambiguous():
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="operating_profit"),
                _item("Second", 3, 4, concept="operating_income"),
            ],
            "operating_profit",
            required=False,
        )
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="gross_profit"),
                _item("Second", 3, 4, concept="gross_profit"),
            ],
            "gross_profit",
            required=False,
        )


def test_reported_margin_explicit_concept_outranks_label():
    items = [
        _item("Operating profit", 1, 2),
        _item("Other operating result", 80, 90, concept="operating_income"),
    ]
    resolved = resolve_line(items, "operating_profit", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.concept == "operating_income"


def test_inventories_explicit_concept_and_label_only_rejection():
    inventories = resolve_line(
        [_item("Neutral", 1, 2, concept="inventories")],
        "inventories",
        required=True,
    )
    assert inventories.item is not None
    assert inventories.item.concept == "inventories"
    for label in ("Inventories", "Inventory", "Merchandise inventories"):
        assert resolve_line([_item(label, 1, 2)], "inventories", required=False).item is None


def test_inventories_competing_concepts_are_ambiguous():
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="inventories"),
                _item("Second", 3, 4, concept="inventories"),
            ],
            "inventories",
            required=False,
        )


def test_inventories_explicit_concept_outranks_label():
    items = [
        _item("Inventories", 1, 2),
        _item("Other stock", 80, 90, concept="inventories"),
    ]
    resolved = resolve_line(items, "inventories", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.concept == "inventories"


def test_change_in_inventories_explicit_concept_and_label_only_rejection():
    change = resolve_line(
        [_item("Neutral", 1, 2, concept="change_in_inventories")],
        "change_in_inventories",
        required=True,
    )
    assert change.item is not None
    assert change.item.concept == "change_in_inventories"
    for label in (
        "Inventories",
        "(Increase)/decrease in inventories",
        "Change in inventories",
    ):
        assert (
            resolve_line(
                [_item(label, 1, 2)], "change_in_inventories", required=False
            ).item
            is None
        )


def test_change_in_inventories_competing_concepts_are_ambiguous():
    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _item("First", 1, 2, concept="change_in_inventories"),
                _item("Second", 3, 4, concept="change_in_inventories"),
            ],
            "change_in_inventories",
            required=False,
        )


def test_change_in_inventories_explicit_concept_outranks_label():
    items = [
        _item("(Increase)/decrease in inventories", 1, 2),
        _item("Other inventory movement", 80, 90, concept="change_in_inventories"),
    ]
    resolved = resolve_line(items, "change_in_inventories", required=True)
    assert resolved.item is not None
    assert resolved.index == 1
    assert resolved.item.concept == "change_in_inventories"

