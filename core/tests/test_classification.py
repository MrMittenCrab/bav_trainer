"""Tests for BAVGEM Stage-3 balance-sheet classification / reformulation."""

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
from core.ingestion.reconciler import reconcile_financials
from core.model.classification import (
    BALANCE_SHEET_CATEGORIES,
    InvalidClassificationOverrideError,
    ReformulationIntegrityError,
    UnclassifiedBalanceSheetLineError,
    check_reformulation_integrity,
    classify_balance_sheet_line,
    reformulate_balance_sheet,
)
from core.model.financial_math import compute_anchor
from core.trainer.workbook import build_training_workbook

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _li(label: str, v1: float, v2: float) -> LineItem:
    return LineItem(label=label, values={P1: v1, P2: v2})


def _periods() -> list[FinancialPeriod]:
    return [
        FinancialPeriod(end_date=P1, label="FY2024"),
        FinancialPeriod(end_date=P2, label="FY2025"),
    ]


def test_bav_categories_are_exact_eight():
    assert BALANCE_SHEET_CATEGORIES == (
        "Operating Working Capital Asset",
        "Operating Working Capital Liability",
        "Operating Long-Term Asset",
        "Operating Long-Term Liability",
        "Financial Asset",
        "Financial Liability",
        "Equity",
        "Exclude",
    )
    assert not any(c.startswith("Ambiguous") for c in BALANCE_SHEET_CATEGORIES)


def test_equity_components_classify_as_equity():
    d = classify_balance_sheet_line(_li("Share capital and reserves", 100, 110))
    assert d.category == "Equity"
    assert d.ambiguous is False


def test_other_noncurrent_defaults():
    a = classify_balance_sheet_line(_li("Other non-current assets", 1, 2))
    l = classify_balance_sheet_line(_li("Other non-current liabilities", 1, 2))
    assert a.category == "Operating Long-Term Asset"
    assert l.category == "Operating Long-Term Liability"


def test_debt_security_concept_does_not_become_financial_liability():
    item = LineItem(
        label="Marketable securities",
        concept="DebtSecuritiesAvailableForSale",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Asset"


def test_equity_method_concept_does_not_become_equity():
    item = LineItem(
        label="Investment in associate",
        concept="EquityMethodInvestments",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Operating Long-Term Asset"


def test_cash_flow_hedge_reserve_concept_does_not_become_financial_asset():
    item = LineItem(
        label="Other comprehensive income reserve",
        concept="CashFlowHedgeReserve",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Equity"


def test_ambiguous_item_has_real_default_and_flag():
    d = classify_balance_sheet_line(_li("Operating lease liabilities", 50, 60))
    assert d.category in BALANCE_SHEET_CATEGORIES
    assert d.category != "Exclude"
    assert not d.category.startswith("Ambiguous")
    assert d.ambiguous is True
    assert d.reason


def test_unknown_line_requires_override():
    item = _li("Zyzzyx contingent remeasurement pocket", 10, 12)
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(item)
    d = classify_balance_sheet_line(item, override="Exclude")
    assert d.category == "Exclude"
    assert d.overridden is True


def test_invalid_override_rejected():
    with pytest.raises(InvalidClassificationOverrideError):
        classify_balance_sheet_line(
            _li("Cash and cash equivalents", 1, 2),
            override="Ambiguous — Operating",
        )


def test_reformulation_detects_equal_asset_liability_omissions():
    """A=L+E can hold while classified detail omits the same amount on both sides."""
    periods = [P1, P2]
    fin = StandardizedFinancials(
        ticker="GAP",
        company_name="Gap Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[
            _li("Revenue", 100, 110),
            _li("Profit before tax", 20, 22),
            _li("Income tax expense", -3, -3),
            _li("Profit for the year", 17, 19),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 40, 40),
            _li("Trade receivables", 30, 30),
            # Missing other assets of 30 — Total assets still 100
            _li("Total assets", 100, 100),
            _li("Trade payables", 20, 20),
            _li("Bank borrowings", 30, 30),
            # Missing other liabilities of 30 — Total liabilities still 80
            _li("Total liabilities", 80, 80),
            _li("Share capital and reserves", 20, 20),
            _li("Total equity", 20, 20),
        ],
        cash_flow=[
            _li("Net cash from operating activities", 10, 10),
            _li("Net cash used in investing activities", -4, -4),
            _li("Net cash from financing activities", -1, -1),
            _li("Net change in cash and cash equivalents", 5, 5),
        ],
    )
    # Reported equation balances
    assert fin.balance_sheet[2].values[P2] == (
        fin.balance_sheet[5].values[P2] + fin.balance_sheet[7].values[P2]
    )
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.asset_detail_gap[1] is not None
    assert reform.liability_detail_gap[1] is not None
    assert abs(reform.asset_detail_gap[1]) > 1.0
    assert abs(reform.liability_detail_gap[1]) > 1.0
    with pytest.raises(ReformulationIntegrityError):
        check_reformulation_integrity(reform, periods)


def test_demo_reformulation_reconciles_all_years():
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    periods = data.fiscal_years() or data.period_dates()
    reform = reformulate_balance_sheet(data, periods)
    for i in range(len(periods)):
        assert reform.asset_detail_gap[i] is not None
        assert reform.liability_detail_gap[i] is not None
        assert reform.equity_gap[i] is not None
        assert abs(reform.asset_detail_gap[i]) <= 1.0
        assert abs(reform.liability_detail_gap[i]) <= 1.0
        assert abs(reform.equity_gap[i]) <= 1.0
    check_reformulation_integrity(reform, periods)
    anchor = compute_anchor(data, periods)
    assert abs(anchor.equity - (anchor.noa - anchor.net_debt)) < 1e-9


def test_demo_reconciliation_report_passes():
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    report = reconcile_financials(data)
    assert report.checksums["income_statement"] is True
    assert report.checksums["balance_sheet"] is True
    assert report.checksums["cash_flow"] is True
