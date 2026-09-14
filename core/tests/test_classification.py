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
from core.data.validators import validate_balance_sheet
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
from core.model.judgment import classification_judgment_cases
from core.trainer.workbook import build_training_workbook

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _li(label: str, v1: float, v2: float, *, concept: str = "") -> LineItem:
    return LineItem(label=label, concept=concept, values={P1: v1, P2: v2})


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


def test_redeemable_preferred_stock_concept_does_not_force_equity():
    item = LineItem(
        label="Long-term debt",
        concept="PreferredStockSubjectToMandatoryRedemption",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Liability"


def test_redeemable_common_stock_concept_does_not_force_equity():
    item = LineItem(
        label="Long-term debt",
        concept="CommonStockSubjectToRedemption",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Liability"


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
    assert abs(reform.asset_detail_gap[1]) == 30.0
    assert abs(reform.liability_detail_gap[1]) == 30.0
    # Two asset + two liability detail rows → envelope 0.5*(2+1)=1.5; 30 ≫ 1.5.
    assert abs(reform.asset_detail_gap[1]) > 1.5
    assert abs(reform.liability_detail_gap[1]) > 1.5
    with pytest.raises(ReformulationIntegrityError):
        check_reformulation_integrity(reform, periods)


def _asset_rounding_fin(total_assets: float) -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="ROUND-A",
        company_name="Rounded Assets",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 10, 10),
            _li("Trade receivables", 10, 10),
            _li("Inventories", 10, 10),
            _li("Prepaid expenses", 10, 10),
            _li("Total assets", total_assets, total_assets, concept="total_assets"),
        ],
        cash_flow=[],
    )


def _liability_rounding_fin(total_liabilities: float) -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="ROUND-L",
        company_name="Rounded Liabilities",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Trade payables", 10, 10),
            _li("Accrued expenses", 10, 10),
            _li("Bank borrowings", 10, 10),
            _li("Lease liabilities", 10, 10),
            _li(
                "Total liabilities",
                total_liabilities,
                total_liabilities,
                concept="total_liabilities",
            ),
        ],
        cash_flow=[],
    )


def _equity_rounding_fin(total_equity: float) -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="ROUND-E",
        company_name="Rounded Equity",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Trade receivables", 10, 10),
            _li("Property, plant and equipment", 20, 20),
            _li("Trade payables", 5, 5),
            _li("Bank borrowings", 5, 5),
            _li("Total equity", total_equity, total_equity, concept="total_equity"),
        ],
        cash_flow=[],
    )


def test_reformulation_integrity_accepts_count_bounded_asset_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(42), periods)
    assert reform.asset_detail_gap == (-2.0, -2.0)
    check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_rejects_asset_gap_above_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(43), periods)
    assert reform.asset_detail_gap == (-3.0, -3.0)
    with pytest.raises(ReformulationIntegrityError, match="asset-detail gap"):
        check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_accepts_count_bounded_liability_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_liability_rounding_fin(42), periods)
    assert reform.liability_detail_gap == (-2.0, -2.0)
    check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_rejects_liability_gap_above_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_liability_rounding_fin(43), periods)
    assert reform.liability_detail_gap == (-3.0, -3.0)
    with pytest.raises(ReformulationIntegrityError, match="liability-detail gap"):
        check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_accepts_count_bounded_equity_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_equity_rounding_fin(18), periods)
    assert reform.implied_equity == (20.0, 20.0)
    assert reform.equity_gap == (2.0, 2.0)
    check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_rejects_equity_gap_above_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_equity_rounding_fin(17), periods)
    assert reform.equity_gap == (3.0, 3.0)
    with pytest.raises(ReformulationIntegrityError, match="equity gap"):
        check_reformulation_integrity(reform, periods)


def test_reformulation_integrity_explicit_tolerance_remains_floor():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(46), periods)
    assert reform.asset_detail_gap == (-6.0, -6.0)
    with pytest.raises(ReformulationIntegrityError):
        check_reformulation_integrity(reform, periods)
    check_reformulation_integrity(reform, periods, tolerance=6.0)


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


def test_lease_liability_judgment_code_label_and_concept():
    by_label = classify_balance_sheet_line(_li("Operating lease liabilities", 50, 60))
    assert by_label.ambiguous is True
    assert by_label.category == "Operating Long-Term Liability"
    assert by_label.judgment_code == "lease_liability_operating_vs_financing"

    by_concept = classify_balance_sheet_line(
        LineItem(
            label="Lease liabilities",
            concept="lease_liability",
            values={P1: 50, P2: 60},
        )
    )
    assert by_concept.ambiguous is True
    assert by_concept.category == "Operating Long-Term Liability"
    assert by_concept.judgment_code == "lease_liability_operating_vs_financing"


def test_associate_investment_judgment_code_label_and_concept():
    by_label = classify_balance_sheet_line(_li("Investment in associates", 50, 60))
    assert by_label.ambiguous is True
    assert by_label.category == "Operating Long-Term Asset"
    assert by_label.judgment_code == "associate_investment_operating_vs_financial"

    by_jv_label = classify_balance_sheet_line(_li("Investment in joint venture", 50, 60))
    assert by_jv_label.judgment_code == "associate_investment_operating_vs_financial"

    by_concept = classify_balance_sheet_line(
        LineItem(
            label="Strategic holding",
            concept="EquityMethodInvestments",
            values={P1: 50, P2: 60},
        )
    )
    assert by_concept.ambiguous is True
    assert by_concept.category == "Operating Long-Term Asset"
    assert by_concept.judgment_code == "associate_investment_operating_vs_financial"


def test_supported_judgment_codes_for_pension_and_short_term_investment():
    pension = classify_balance_sheet_line(_li("Pension obligations", 50, 60))
    assert pension.ambiguous is True
    assert pension.category == "Operating Long-Term Liability"
    assert pension.judgment_code == "pension_obligation_operating_vs_financing"

    sti = classify_balance_sheet_line(_li("Short-term investments", 50, 60))
    assert sti.ambiguous is True
    assert sti.category == "Financial Asset"
    assert sti.judgment_code == "short_term_investment_financial_vs_operating"


def test_deferred_tax_and_rou_ambiguous_without_judgment_code():
    dta = classify_balance_sheet_line(_li("Deferred tax assets", 50, 60))
    assert dta.ambiguous is True
    assert dta.judgment_code is None

    dtl = classify_balance_sheet_line(_li("Deferred tax liabilities", 50, 60))
    assert dtl.ambiguous is True
    assert dtl.judgment_code is None

    rou = classify_balance_sheet_line(_li("Right-of-use assets", 50, 60))
    assert rou.ambiguous is True
    assert rou.judgment_code is None

    dta_concept = classify_balance_sheet_line(
        LineItem(
            label="Deferred tax",
            concept="DeferredTaxAsset",
            values={P1: 50, P2: 60},
        )
    )
    assert dta_concept.ambiguous is True
    assert dta_concept.judgment_code is None


def test_override_suppresses_judgment_code():
    decision = classify_balance_sheet_line(
        _li("Operating lease liabilities", 50, 60),
        override="Financial Liability",
    )
    assert decision.overridden is True
    assert decision.ambiguous is False
    assert decision.judgment_code is None


def test_bs_detail_and_optional_totals_period_completeness():
    from core.model.source_values import MissingHistoricalValueError

    periods = [P1, P2]
    # Complete detail + absent totals still works.
    fin = StandardizedFinancials(
        ticker="BS",
        company_name="BS Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=P1, label="FY2024"),
            FinancialPeriod(end_date=P2, label="FY2025"),
        ],
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Share capital and reserves", 330, 355),
        ],
        cash_flow=[],
    )
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.total_assets == (None, None)
    assert reform.category_totals["Financial Asset"][0] == pytest.approx(100.0)

    # Explicit zero detail accepted.
    fin_zero = StandardizedFinancials(
        ticker="BS0",
        company_name="BS Zero",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=fin.periods,
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 0, 0),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Share capital and reserves", 230, 245),
        ],
        cash_flow=[],
    )
    reform_zero = reformulate_balance_sheet(fin_zero, periods)
    assert reform_zero.category_totals["Financial Asset"][0] == 0.0

    # Missing detail period fails.
    fin_miss = StandardizedFinancials(
        ticker="BSM",
        company_name="BS Miss",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=fin.periods,
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Share capital and reserves", 330, 355),
        ],
        cash_flow=[],
    )
    del fin_miss.balance_sheet[0].values[P2]
    with pytest.raises(MissingHistoricalValueError, match="balance_sheet detail"):
        reformulate_balance_sheet(fin_miss, periods)

    # Present but incomplete Total Assets fails.
    fin_ta = StandardizedFinancials(
        ticker="TA",
        company_name="TA Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=fin.periods,
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Total assets", 580, 620),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Share capital and reserves", 330, 355),
        ],
        cash_flow=[],
    )
    del fin_ta.balance_sheet[3].values[P2]
    with pytest.raises(MissingHistoricalValueError, match="total_assets"):
        reformulate_balance_sheet(fin_ta, periods)

    for concept, label in (
        ("total_liabilities", "Total liabilities"),
        ("total_equity", "Total equity"),
    ):
        fin_tot = StandardizedFinancials(
            ticker="TOT",
            company_name="Tot Co",
            currency="HKD",
            units="mn",
            jurisdiction="HK",
            periods=fin.periods,
            income_statement=[],
            balance_sheet=[
                _li("Cash and cash equivalents", 100, 110),
                _li("Trade receivables", 80, 90),
                _li("Property, plant and equipment", 400, 420),
                _li("Trade payables", 50, 55),
                _li("Bank borrowings", 200, 210),
                _li("Share capital and reserves", 330, 355),
                _li(label, 250, 265),
            ],
            cash_flow=[],
        )
        fin_tot.balance_sheet[-1].values[P1] = None
        with pytest.raises(MissingHistoricalValueError, match=concept):
            reformulate_balance_sheet(fin_tot, periods)


def _sparse_balanced_fin(
    liability_values: dict[date, float | None],
) -> StandardizedFinancials:
    """Minimal BS where sparse liability absence reconciles when non-contributing."""
    return StandardizedFinancials(
        ticker="SPARSE",
        company_name="Sparse Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 100),
            _li("Trade receivables", 50, 50),
            _li("Property, plant and equipment", 50, 50),
            LineItem(
                label="Total assets",
                concept="total_assets",
                values={P1: 200.0, P2: 200.0},
            ),
            _li("Trade payables", 40, 40),
            LineItem(
                label="Non-current income taxes payable",
                concept="non_current_income_taxes_payable",
                values=dict(liability_values),
            ),
            _li("Bank borrowings", 60, 60),
            LineItem(
                label="Total liabilities",
                concept="total_liabilities",
                values={P1: 100.0, P2: 100.0},
            ),
            _li("Share capital and reserves", 100, 100),
            LineItem(
                label="Total equity",
                concept="total_equity",
                values={P1: 100.0, P2: 100.0},
            ),
        ],
        cash_flow=[],
    )


@pytest.mark.parametrize(
    "liability_values",
    [
        {P1: None, P2: 0.0},  # leading absence
        {P1: 0.0, P2: None},  # trailing absence
        {P1: None, P2: None},  # both periods absent
    ],
)
def test_sparse_explicit_absence_reconciles_when_evidence_gate_passes(liability_values):
    periods = [P1, P2]
    fin = _sparse_balanced_fin(liability_values)
    before = [dict(item.values) for item in fin.balance_sheet]
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.asset_detail_gap == (0.0, 0.0)
    assert reform.liability_detail_gap == (0.0, 0.0)
    assert reform.equity_gap == (0.0, 0.0)
    check_reformulation_integrity(reform, periods)
    # Source nulls preserved; reported zeros remain distinct.
    sparse = next(
        item
        for item in fin.balance_sheet
        if item.concept == "non_current_income_taxes_payable"
    )
    assert sparse.values == liability_values
    assert [dict(item.values) for item in fin.balance_sheet] == before
    # Reported zero remains a numeric contribution; explicit None does not.
    assert None not in (
        reform.category_totals["Operating Working Capital Liability"][0],
        reform.category_totals["Operating Working Capital Liability"][1],
    )


def test_sparse_interior_absence_with_neighboring_reported_zero():
    """Three-period row: value / None / reported zero — null stays non-invented."""
    p0 = date(2023, 12, 31)
    periods = [p0, P1, P2]
    fin = StandardizedFinancials(
        ticker="INT",
        company_name="Interior Sparse",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p0, label="FY2023"),
            FinancialPeriod(end_date=P1, label="FY2024"),
            FinancialPeriod(end_date=P2, label="FY2025"),
        ],
        income_statement=[],
        balance_sheet=[
            LineItem(
                label="Cash and cash equivalents",
                values={p0: 100.0, P1: 100.0, P2: 100.0},
            ),
            LineItem(
                label="Total assets",
                concept="total_assets",
                values={p0: 100.0, P1: 100.0, P2: 100.0},
            ),
            LineItem(
                label="Non-current income taxes payable",
                concept="non_current_income_taxes_payable",
                values={p0: 25.0, P1: None, P2: 0.0},
            ),
            LineItem(
                label="Bank borrowings",
                values={p0: 75.0, P1: 100.0, P2: 100.0},
            ),
            LineItem(
                label="Total liabilities",
                concept="total_liabilities",
                values={p0: 100.0, P1: 100.0, P2: 100.0},
            ),
            LineItem(
                label="Share capital and reserves",
                values={p0: 0.0, P1: 0.0, P2: 0.0},
            ),
            LineItem(
                label="Total equity",
                concept="total_equity",
                values={p0: 0.0, P1: 0.0, P2: 0.0},
            ),
        ],
        cash_flow=[],
    )
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.liability_detail_gap == (0.0, 0.0, 0.0)
    check_reformulation_integrity(reform, periods)
    sparse = next(
        item
        for item in fin.balance_sheet
        if item.concept == "non_current_income_taxes_payable"
    )
    assert sparse.values[p0] == 25.0
    assert sparse.values[P1] is None
    assert sparse.values[P2] == 0.0
    assert reform.category_totals["Operating Working Capital Liability"] == (
        25.0,
        0.0,
        0.0,
    )


def test_sparse_absence_fails_without_independent_totals():
    from core.model.source_values import MissingHistoricalValueError

    periods = [P1, P2]
    fin = StandardizedFinancials(
        ticker="NOTOT",
        company_name="No Totals",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            LineItem(
                label="Deferred tax liability",
                concept="deferred_tax_liability",
                values={P1: 10.0, P2: None},
            ),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Share capital and reserves", 340, 355),
        ],
        cash_flow=[],
    )
    with pytest.raises(MissingHistoricalValueError, match="2025-12-31"):
        reformulate_balance_sheet(fin, periods)


def test_sparse_absence_fails_when_total_row_null():
    from core.model.source_values import MissingHistoricalValueError

    periods = [P1, P2]
    fin = _sparse_balanced_fin({P1: 0.0, P2: None})
    # Independent total present as a row but null for the sparse period.
    total_liab = next(
        item for item in fin.balance_sheet if item.concept == "total_liabilities"
    )
    total_liab.values[P2] = None
    with pytest.raises(MissingHistoricalValueError, match="total_liabilities"):
        reformulate_balance_sheet(fin, periods)


def test_sparse_absence_fails_on_contradictory_gap():
    """Explicit None that would leave a material liability gap fails closed."""
    from core.model.source_values import MissingHistoricalValueError

    periods = [P1, P2]
    fin = _sparse_balanced_fin({P1: 0.0, P2: None})
    # Reported total still includes the omitted amount → contradictory evidence.
    total_liab = next(
        item for item in fin.balance_sheet if item.concept == "total_liabilities"
    )
    total_liab.values[P2] = 140.0
    total_eq = next(
        item for item in fin.balance_sheet if item.concept == "total_equity"
    )
    total_eq.values[P2] = 60.0
    with pytest.raises(MissingHistoricalValueError, match="2025-12-31"):
        reformulate_balance_sheet(fin, periods)


def test_sparse_missing_key_still_fails_closed():
    from core.model.source_values import MissingHistoricalValueError

    periods = [P1, P2]
    fin = _sparse_balanced_fin({P1: 0.0, P2: 0.0})
    sparse = next(
        item
        for item in fin.balance_sheet
        if item.concept == "non_current_income_taxes_payable"
    )
    del sparse.values[P2]
    with pytest.raises(MissingHistoricalValueError, match="balance_sheet detail"):
        reformulate_balance_sheet(fin, periods)


def test_complete_rows_unchanged_with_sparse_neighbor():
    periods = [P1, P2]
    fin = _sparse_balanced_fin({P1: 0.0, P2: None})
    reform = reformulate_balance_sheet(fin, periods)
    assert reform.category_totals["Financial Asset"] == (100.0, 100.0)
    assert reform.category_totals["Operating Working Capital Asset"] == (50.0, 50.0)
    assert reform.category_totals["Financial Liability"] == (60.0, 60.0)


def test_classification_curly_apostrophe_equity_alias_consistent():
    from core.model.classification import _norm

    assert _norm("Shareholders' equity") == _norm("Shareholders\u2019 equity")
    assert _norm("Owners' equity") == _norm("Owners\u2019 equity")

    # Override matching treats curly/straight apostrophe labels consistently.
    owners_straight = classify_balance_sheet_line(
        LineItem(label="Owners' residual interest", values={P1: 10, P2: 11}),
        override="Equity",
    )
    owners_curly = classify_balance_sheet_line(
        LineItem(label="Owners\u2019 residual interest", values={P1: 10, P2: 11}),
        override="Equity",
    )
    assert owners_straight.category == "Equity"
    assert owners_curly.category == "Equity"


def _balance_sheet_identity_fin(residual: float) -> StandardizedFinancials:
    assets = 100.0
    liabilities = 60.0
    equity = 40.0 - residual
    return StandardizedFinancials(
        ticker="ROUND",
        company_name="Rounding Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Total assets", assets, assets),
            _li("Total liabilities", liabilities, liabilities),
            _li("Total equity", equity, equity),
        ],
        cash_flow=[],
    )


@pytest.mark.parametrize(
    ("residual", "expected"),
    [
        (0.0, True),
        (0.5, True),
        (1.0, True),
        (1.01, False),
    ],
)
def test_balance_sheet_rounding_tolerance(residual, expected):
    fin = _balance_sheet_identity_fin(residual)
    before = [dict(item.values) for item in fin.balance_sheet]
    result = validate_balance_sheet(fin)
    assert set(result.values()) == {expected}
    assert [dict(item.values) for item in fin.balance_sheet] == before


def test_reconciliation_accepts_one_unit_but_rejects_larger_residual():
    accepted = reconcile_financials(_balance_sheet_identity_fin(1.0))
    assert accepted.checksums["balance_sheet"] is True
    assert "Balance sheet does not balance for one or more periods" not in accepted.warnings

    rejected = reconcile_financials(_balance_sheet_identity_fin(1.01))
    assert rejected.checksums["balance_sheet"] is False
    assert "Balance sheet does not balance for one or more periods" in rejected.warnings


@pytest.mark.parametrize(
    ("label", "concept", "category", "code"),
    [
        (
            "Other financial assets",
            "other_financial_assets_current",
            "Financial Asset",
            "financial_asset_current_financial_vs_operating",
        ),
        (
            "Financial assets",
            "financial_assets_noncurrent",
            "Financial Asset",
            "financial_asset_noncurrent_financial_vs_operating",
        ),
        (
            "Derivative financial assets",
            "derivative_financial_assets_current",
            "Financial Asset",
            "financial_asset_current_financial_vs_operating",
        ),
        (
            "Derivative financial assets",
            "derivative_financial_assets_noncurrent",
            "Financial Asset",
            "financial_asset_noncurrent_financial_vs_operating",
        ),
        (
            "Other financial liabilities",
            "other_financial_liabilities_current",
            "Financial Liability",
            "financial_liability_current_financial_vs_operating",
        ),
        (
            "Financial liabilities",
            "financial_liabilities_noncurrent",
            "Financial Liability",
            "financial_liability_noncurrent_financial_vs_operating",
        ),
        (
            "Derivative financial liabilities",
            "derivative_financial_liabilities_current",
            "Financial Liability",
            "financial_liability_current_financial_vs_operating",
        ),
        (
            "Derivative financial liabilities",
            "derivative_financial_liabilities_noncurrent",
            "Financial Liability",
            "financial_liability_noncurrent_financial_vs_operating",
        ),
    ],
)
def test_generic_financial_concepts_become_guided_judgments(
    label, concept, category, code
):
    decision = classify_balance_sheet_line(
        LineItem(label=label, concept=concept, values={P1: 10, P2: 12})
    )
    assert decision.category == category
    assert decision.ambiguous is True
    assert decision.judgment_code == code
    assert decision.reason


def test_generic_financial_label_without_side_concept_still_fails_closed():
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(
            LineItem(
                label="Other financial assets",
                concept="",
                values={P1: 10, P2: 12},
            )
        )


def test_generic_financial_concept_does_not_override_specific_existing_rules():
    cash = classify_balance_sheet_line(
        LineItem(
            label="Cash and cash equivalents",
            concept="financial_assets_current",
            values={P1: 10, P2: 12},
        )
    )
    assert cash.category == "Financial Asset"
    assert cash.ambiguous is False

    debt = classify_balance_sheet_line(
        LineItem(
            label="Bank borrowings",
            concept="financial_liabilities_noncurrent",
            values={P1: 10, P2: 12},
        )
    )
    assert debt.category == "Financial Liability"
    assert debt.ambiguous is False

    short_term_investment = classify_balance_sheet_line(
        LineItem(
            label="Short-term investments",
            concept="financial_assets_current",
            values={P1: 10, P2: 12},
        )
    )
    assert short_term_investment.judgment_code == (
        "short_term_investment_financial_vs_operating"
    )


def _generic_financial_judgment_fin() -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="GFIN",
        company_name="Generic Financial Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            LineItem(
                label="Other financial assets",
                concept="other_financial_assets_current",
                values={P1: 10, P2: 11},
            ),
            LineItem(
                label="Financial assets",
                concept="financial_assets_noncurrent",
                values={P1: 20, P2: 21},
            ),
            LineItem(
                label="Other financial liabilities",
                concept="other_financial_liabilities_current",
                values={P1: 5, P2: 6},
            ),
            LineItem(
                label="Financial liabilities",
                concept="financial_liabilities_noncurrent",
                values={P1: 7, P2: 8},
            ),
            LineItem(
                label="Share capital and reserves",
                concept="retained_earnings",
                values={P1: 18, P2: 18},
            ),
        ],
        cash_flow=[],
    )


def test_generic_financial_judgment_cases_and_override():
    fin = _generic_financial_judgment_fin()
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    assert len(cases) == 4

    expected = {
        "Other financial assets": (
            "Financial Asset",
            ("Operating Working Capital Asset",),
        ),
        "Financial assets": (
            "Financial Asset",
            ("Operating Long-Term Asset",),
        ),
        "Other financial liabilities": (
            "Financial Liability",
            ("Operating Working Capital Liability",),
        ),
        "Financial liabilities": (
            "Financial Liability",
            ("Operating Long-Term Liability",),
        ),
    }
    by_label = {case.label: case for case in cases}
    assert set(by_label) == set(expected)
    for label, (supplied, alts) in expected.items():
        case = by_label[label]
        assert case.supplied_treatment == supplied
        assert case.alternatives == alts
        assert case.override_selector.startswith("identity:")
        assert case.line_identity == case.override_selector.removeprefix("identity:")
        assert case.model_rationale
        assert case.model_consequence

    case = by_label["Other financial assets"]
    before_values = [dict(item.values) for item in fin.balance_sheet]
    reform_alt = reformulate_balance_sheet(
        fin,
        periods,
        overrides={case.override_selector: case.alternatives[0]},
    )
    # Selected detail decision changes to the alternative category.
    detail_idx = next(
        idx
        for idx in reform_alt.detail_indices
        if fin.balance_sheet[idx].label == case.label
    )
    assert reform_alt.decisions[detail_idx].category == case.alternatives[0]
    assert [dict(item.values) for item in fin.balance_sheet] == before_values
    assert reform_alt.implied_equity == reform.implied_equity
    # Financial-asset -> operating WC raises NOA and Net Debt together.
    assert reform_alt.noa[0] > reform.noa[0]
    assert reform_alt.net_debt[0] > reform.net_debt[0]


@pytest.mark.parametrize(
    ("label", "concept", "category", "judgment_code"),
    [
        (
            "Other assets",
            "other_current_assets",
            "Operating Working Capital Asset",
            "other_current_asset_operating_vs_financial",
        ),
        (
            "Other assets",
            "other_noncurrent_assets",
            "Operating Long-Term Asset",
            "other_noncurrent_asset_operating_vs_financial",
        ),
        (
            "Other liabilities",
            "other_current_liabilities",
            "Operating Working Capital Liability",
            "other_current_liability_operating_vs_financial",
        ),
        (
            "Other liabilities",
            "other_noncurrent_liabilities",
            "Operating Long-Term Liability",
            "other_noncurrent_liability_operating_vs_financial",
        ),
    ],
)
def test_explicit_other_balance_concepts_become_guided_judgments(
    label, concept, category, judgment_code
):
    item = _li(label, 10, 12, concept=concept)
    decision = classify_balance_sheet_line(item)
    assert decision.category == category
    assert decision.ambiguous is True
    assert decision.judgment_code == judgment_code
    assert decision.reason


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Other assets", ""),
        ("Other liabilities", ""),
        ("Other assets", "other_assets"),
        ("Other liabilities", "other_liabilities"),
        ("Other assets", "miscellaneous_current_asset"),
        ("Other liabilities", "miscellaneous_noncurrent_liability"),
    ],
)
def test_other_balance_without_explicit_side_concept_still_fails_closed(label, concept):
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 10, 12, concept=concept))


def test_other_balance_concept_does_not_override_specific_cash_label():
    decision = classify_balance_sheet_line(
        _li("Cash and cash equivalents", 10, 12, concept="other_current_assets")
    )
    assert decision.category == "Financial Asset"
    assert decision.judgment_code != "other_current_asset_operating_vs_financial"
    assert decision.ambiguous is False


def _residual_other_balance_fin() -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="OTHER",
        company_name="Other Balance Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Other current assets", 10, 11, concept="other_current_assets"),
            _li("Other non-current assets", 20, 21, concept="other_noncurrent_assets"),
            _li(
                "Other current liabilities",
                5,
                6,
                concept="other_current_liabilities",
            ),
            _li(
                "Other non-current liabilities",
                7,
                8,
                concept="other_noncurrent_liabilities",
            ),
            _li("Share capital and reserves", 18, 18, concept="retained_earnings"),
        ],
        cash_flow=[],
    )


def test_other_balance_judgment_cases_and_consequence_directions():
    fin = _residual_other_balance_fin()
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    assert {case.label for case in cases} >= {
        "Other current assets",
        "Other non-current assets",
        "Other current liabilities",
        "Other non-current liabilities",
    }

    expected = {
        "Other current assets": (
            "Operating Working Capital Asset",
            "Financial Asset",
            "down",
        ),
        "Other non-current assets": (
            "Operating Long-Term Asset",
            "Financial Asset",
            "down",
        ),
        "Other current liabilities": (
            "Operating Working Capital Liability",
            "Financial Liability",
            "up",
        ),
        "Other non-current liabilities": (
            "Operating Long-Term Liability",
            "Financial Liability",
            "up",
        ),
    }
    by_label = {case.label: case for case in cases}
    for label, (supplied, alt, direction) in expected.items():
        case = by_label[label]
        assert case.supplied_treatment == supplied
        assert case.alternatives == (alt,)
        assert case.model_rationale
        assert case.consequence_prompt
        assert case.model_consequence
        assert case.override_selector.startswith("identity:")

        reform_alt = reformulate_balance_sheet(
            fin,
            periods,
            overrides={case.override_selector: case.alternatives[0]},
        )
        assert reform_alt.implied_equity == reform.implied_equity
        if direction == "down":
            assert reform_alt.noa[0] < reform.noa[0]
            assert reform_alt.net_debt[0] < reform.net_debt[0]
        else:
            assert reform_alt.noa[0] > reform.noa[0]
            assert reform_alt.net_debt[0] > reform.net_debt[0]


@pytest.mark.parametrize(
    ("label", "concept", "expected_category"),
    [
        (
            "Current tax liabilities",
            "current_tax_liabilities",
            "Operating Working Capital Liability",
        ),
        (
            "Provisions",
            "provisions_current",
            "Operating Working Capital Liability",
        ),
        (
            "Provisions",
            "provisions_noncurrent",
            "Operating Long-Term Liability",
        ),
        (
            "Capital stock",
            "capital_stock",
            "Equity",
        ),
        (
            "Capital surplus",
            "capital_surplus",
            "Equity",
        ),
        (
            "Other components of equity",
            "other_components_of_equity",
            "Equity",
        ),
        (
            "Non-controlling interests",
            "noncontrolling_interests",
            "Equity",
        ),
    ],
)
def test_exact_standard_accounting_concepts_classify_deterministically(
    label, concept, expected_category
):
    decision = classify_balance_sheet_line(_li(label, 10, 12, concept=concept))
    assert decision.category == expected_category
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.reason


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Miscellaneous balance", "current_tax_liabilities"),
        ("Miscellaneous balance", "provisions_current"),
        ("Miscellaneous balance", "provisions_noncurrent"),
        ("Miscellaneous balance", "capital_stock"),
        ("Miscellaneous balance", "capital_surplus"),
        ("Miscellaneous balance", "other_components_of_equity"),
        ("Miscellaneous balance", "noncontrolling_interests"),
    ],
)
def test_exact_standard_accounting_concepts_require_compatible_labels(label, concept):
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 10, 12, concept=concept))


def test_exact_standard_accounting_concepts_do_not_displace_existing_rules():
    cash = classify_balance_sheet_line(_li("Cash and cash equivalents", 10, 12, concept="cash"))
    assert cash.category == "Financial Asset"

    payables = classify_balance_sheet_line(
        _li("Trade and other payables", 10, 12, concept="trade_and_other_payables")
    )
    assert payables.category == "Operating Working Capital Liability"

    deferred = classify_balance_sheet_line(
        _li("Deferred tax liabilities", 10, 12, concept="deferred_tax_liabilities")
    )
    assert deferred.category == "Operating Long-Term Liability"
    assert deferred.ambiguous is True

    lease = classify_balance_sheet_line(
        _li("Lease liabilities", 10, 12, concept="lease_liability_current")
    )
    assert lease.category == "Operating Long-Term Liability"
    assert lease.judgment_code == "lease_liability_operating_vs_financing"



def test_deterministic_standard_accounting_concepts_create_no_judgment_cases():
    fin = StandardizedFinancials(
        ticker="DET",
        company_name="Deterministic Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Current tax liabilities", 3, 4, concept="current_tax_liabilities"),
            _li("Provisions", 5, 6, concept="provisions_current"),
            _li("Provisions", 7, 8, concept="provisions_noncurrent"),
            _li("Capital stock", 10, 10, concept="capital_stock"),
            _li("Capital surplus", 11, 11, concept="capital_surplus"),
            _li(
                "Other components of equity",
                2,
                2,
                concept="other_components_of_equity",
            ),
            _li(
                "Non-controlling interests",
                4,
                4,
                concept="noncontrolling_interests",
            ),
            _li("Cash and cash equivalents", 20, 21, concept="cash"),
            _li("Trade and other payables", 8, 9, concept="trade_and_other_payables"),
        ],
        cash_flow=[],
    )
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    forbidden_labels = {
        "Current tax liabilities",
        "Provisions",
        "Capital stock",
        "Capital surplus",
        "Other components of equity",
        "Non-controlling interests",
    }
    assert not any(case.label in forbidden_labels for case in cases)


# --- Customer prepayment / gift-card / deferred-revenue liabilities (G1) ---


@pytest.mark.parametrize(
    ("label", "concept", "expected_category"),
    [
        (
            "Unredeemed gift card liability",
            "unredeemed_gift_card_liability",
            "Operating Working Capital Liability",
        ),
        (
            "Gift card liability",
            "gift_card_liability",
            "Operating Working Capital Liability",
        ),
        (
            "Gift-card liability",
            "gift_card_liability",
            "Operating Working Capital Liability",
        ),
        (
            "Gift card liabilities",
            "",
            "Operating Working Capital Liability",
        ),
        (
            "Gift-card liabilities",
            "gift_card_liabilities",
            "Operating Working Capital Liability",
        ),
        (
            "Gift cards liabilities",
            "",
            "Operating Working Capital Liability",
        ),
        (
            "Noncurrent gift-cards liabilities",
            "noncurrent_gift_cards_liabilities",
            "Operating Long-Term Liability",
        ),
        (
            "Unearned revenue",
            "unearned_revenue",
            "Operating Working Capital Liability",
        ),
        (
            "Deferred revenue",
            "deferred_revenue",
            "Operating Working Capital Liability",
        ),
        (
            "Contract liabilities",
            "contract_liabilities",
            "Operating Working Capital Liability",
        ),
        (
            "Deferred revenue",
            "",
            "Operating Working Capital Liability",
        ),
        (
            "Contract liability",
            "",
            "Operating Working Capital Liability",
        ),
        (
            "Unredeemed gift card liability",
            "",
            "Operating Working Capital Liability",
        ),
        (
            "Current deferred revenue",
            "current_deferred_revenue",
            "Operating Working Capital Liability",
        ),
        (
            "Non-current deferred revenue",
            "noncurrent_deferred_revenue",
            "Operating Long-Term Liability",
        ),
        (
            "Noncurrent contract liabilities",
            "noncurrent_contract_liabilities",
            "Operating Long-Term Liability",
        ),
        (
            "Long-term unearned revenue",
            "long_term_deferred_revenue",
            "Operating Long-Term Liability",
        ),
        (
            "Deferred revenue",
            "noncurrent_deferred_revenue",
            "Operating Long-Term Liability",
        ),
    ],
)
def test_customer_prepayment_liabilities_classify_deterministically(
    label, concept, expected_category
):
    decision = classify_balance_sheet_line(_li(label, 10, 12, concept=concept))
    assert decision.category == expected_category
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.overridden is False
    assert "prepayment" in decision.reason.lower() or "deferred" in decision.reason.lower()


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Gift cards", "gift_cards"),
        ("Gift", "gift"),
        ("Revenue", "revenue"),
        ("Contract", "contract"),
        ("Card liability", "card_liability"),
        ("Miscellaneous balance", "unredeemed_gift_card_liability"),
        ("Miscellaneous balance", "deferred_revenue"),
        ("Contract asset", "contract_asset"),
        ("Contract assets", "contract_assets"),
        ("Gift card receivable", "gift_card_receivable"),
        (
            "Derecognition of unredeemed gift card liability",
            "derecognition_of_unredeemed_gift_card_liability",
        ),
        (
            "Unredeemed gift card liability",
            "change_in_unredeemed_gift_card_liability",
        ),
        (
            "Change in unredeemed gift card liability",
            "unredeemed_gift_card_liability",
        ),
    ],
)
def test_customer_prepayment_unsupported_pairs_fail_closed_or_safe(label, concept):
    """Unsupported / contradictory pairs must not use the new liability rule."""
    try:
        decision = classify_balance_sheet_line(_li(label, 10, 12, concept=concept))
    except UnclassifiedBalanceSheetLineError:
        return
    # Safe existing classification only — never the prepayment liability reason.
    assert "Customer prepayment" not in decision.reason


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        # Reported failing plural label (empty concept) escapes via other-current fallback.
        ("Recognition of gift card liabilities within other current liabilities", ""),
        # Singular/plural card and liability wording; spaced/hyphenated forms.
        ("Recognition of gift card liabilities", ""),
        ("Recognition of gift-card liabilities", ""),
        ("Recognition of gift cards liabilities", ""),
        ("Recognition of gift-cards liabilities", ""),
        ("Derecognition of gift card liabilities", ""),
        ("Change in gift-card liabilities", ""),
        ("Increase in gift cards liabilities", ""),
        ("Decrease in gift-cards liabilities", ""),
        ("Amortization of gift card liabilities", ""),
        ("Additions to gift-card liabilities", ""),
        ("Reductions in gift cards liabilities", ""),
        # Current / noncurrent / other-liability / long-term fallback contexts.
        ("Change in gift-card liabilities in other current liability", ""),
        ("Increase in gift cards liabilities within other non-current liabilities", ""),
        ("Decrease in gift-cards liabilities within long-term liabilities", ""),
        ("Recognition of gift card liabilities within other noncurrent liabilities", ""),
        ("Additions to gift card liabilities in long-term liability", ""),
        # Movement labels with supported balance concepts.
        ("Recognition of gift card liabilities", "gift_card_liabilities"),
        ("Change in gift-card liabilities", "gift_card_liability"),
        ("Increase in gift cards liabilities", "gift_cards_liabilities"),
        # Movement concepts with balance labels.
        (
            "Gift card liabilities",
            "recognition_of_gift_card_liabilities",
        ),
        (
            "Gift-card liabilities",
            "change_in_gift_card_liabilities",
        ),
        (
            "Gift cards liabilities",
            "amortization_of_gift_cards_liabilities",
        ),
        # Empty and unrelated concepts still raise when label is a plural movement.
        ("Recognition of gift card liabilities", "miscellaneous_balance"),
        ("Change in gift-cards liabilities", "other_current_liabilities"),
        # Liability-fallback escapes with plural gift-card topic + movement.
        ("Recognition of other current liabilities", "gift_card_liabilities"),
        ("Change in other non-current liability", "gift_cards_liabilities"),
        ("Increase in long-term liabilities", "gift_card_liabilities"),
        ("Decrease in other noncurrent liabilities", "gift_card_liability"),
    ],
)
def test_plural_gift_card_movements_raise_unclassified(label, concept):
    """Plural gift-card movements must raise — not classify via liability fallbacks."""
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 10, 12, concept=concept))


def test_plural_gift_card_reported_row_override_still_wins():
    item = _li(
        "Recognition of gift card liabilities within other current liabilities",
        10,
        12,
        concept="",
    )
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(item)

    overridden = classify_balance_sheet_line(
        item, override="Operating Working Capital Liability"
    )
    assert overridden.category == "Operating Working Capital Liability"
    assert overridden.overridden is True
    assert overridden.reason == "User override"


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        # Label-only movement wording (empty concept).
        ("Recognition of deferred revenue", ""),
        ("Derecognition of unearned revenue", ""),
        ("Change in gift card liability", ""),
        ("Increase in contract liability", ""),
        ("Decrease in deferred revenue", ""),
        ("Amortization of unearned revenue", ""),
        ("Additions to contract liabilities", ""),
        ("Reductions in gift-card liability", ""),
        # Movement labels with supported balance concepts.
        ("Recognition of deferred revenue", "deferred_revenue"),
        ("Change in unredeemed gift card liability", "unredeemed_gift_card_liability"),
        ("Increase in unearned revenue", "unearned_revenue"),
        ("Decrease in contract liability", "contract_liability"),
        ("Amortization of deferred revenue", "deferred_revenue"),
        ("Additions to gift card liability", "gift_card_liability"),
        ("Reductions in contract liabilities", "contract_liabilities"),
        # Movement concepts with balance labels.
        (
            "Deferred revenue",
            "recognition_of_deferred_revenue",
        ),
        (
            "Unredeemed gift card liability",
            "change_in_unredeemed_gift_card_liability",
        ),
        (
            "Unearned revenue",
            "increase_in_unearned_revenue",
        ),
        (
            "Contract liability",
            "decrease_in_contract_liability",
        ),
        (
            "Gift card liability",
            "amortization_of_gift_card_liability",
        ),
        (
            "Contract liabilities",
            "additions_to_contract_liabilities",
        ),
        (
            "Deferred revenue",
            "reductions_in_deferred_revenue",
        ),
        (
            "Unredeemed gift card liability",
            "derecognition_of_unredeemed_gift_card_liability",
        ),
        # Noncurrent / long-term / other-liability labels that reach broad fallbacks.
        ("Recognition of non-current deferred revenue", ""),
        ("Recognition of non-current contract liability", ""),
        ("Change in long-term unearned revenue", ""),
        ("Change in other non-current liability", "deferred_revenue"),
        ("Increase in long-term liabilities", "contract_liability"),
        ("Decrease in other noncurrent liabilities", "gift_card_liability"),
        ("Recognition of other current liabilities", "deferred_revenue"),
        ("Change in other current liability", "unearned_revenue"),
        ("Additions to other current liabilities", "contract_liability"),
        ("Reductions in long-term liabilities", "deferred_revenue"),
        ("Amortization of long-term deferred revenue", "deferred_revenue"),
    ],
)
def test_customer_prepayment_movements_raise_unclassified(label, concept):
    """Excluded prepayment movements must raise — not classify via liability fallbacks."""
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 10, 12, concept=concept))


def test_customer_prepayment_movement_override_still_wins():
    item = _li(
        "Recognition of deferred revenue",
        10,
        12,
        concept="deferred_revenue",
    )
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(item)

    overridden = classify_balance_sheet_line(
        item, override="Operating Working Capital Liability"
    )
    assert overridden.category == "Operating Working Capital Liability"
    assert overridden.overridden is True
    assert overridden.reason == "User override"


def test_customer_prepayment_does_not_create_judgment_cases():
    fin = StandardizedFinancials(
        ticker="PREPAY",
        company_name="Prepayment Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li(
                "Unredeemed gift card liability",
                8,
                9,
                concept="unredeemed_gift_card_liability",
            ),
            _li("Deferred revenue", 5, 6, concept="deferred_revenue"),
            _li(
                "Non-current deferred revenue",
                3,
                4,
                concept="noncurrent_deferred_revenue",
            ),
            _li("Cash and cash equivalents", 40, 42, concept="cash"),
            _li("Share capital and reserves", 24, 23, concept="retained_earnings"),
        ],
        cash_flow=[],
    )
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    forbidden = {
        "Unredeemed gift card liability",
        "Deferred revenue",
        "Non-current deferred revenue",
    }
    assert not any(case.label in forbidden for case in cases)


def test_customer_prepayment_override_still_wins():
    item = _li(
        "Unredeemed gift card liability",
        10,
        12,
        concept="unredeemed_gift_card_liability",
    )
    default = classify_balance_sheet_line(item)
    assert default.category == "Operating Working Capital Liability"
    assert default.overridden is False

    overridden = classify_balance_sheet_line(item, override="Financial Liability")
    assert overridden.category == "Financial Liability"
    assert overridden.overridden is True
    assert overridden.reason == "User override"


def test_customer_prepayment_preserves_deferred_tax_lease_and_equity():
    dtl = classify_balance_sheet_line(
        _li("Deferred tax liabilities", 10, 12, concept="deferred_tax_liabilities")
    )
    assert dtl.category == "Operating Long-Term Liability"
    assert dtl.ambiguous is True

    lease = classify_balance_sheet_line(
        _li("Lease liabilities", 10, 12, concept="lease_liability_current")
    )
    assert lease.category == "Operating Long-Term Liability"
    assert lease.judgment_code == "lease_liability_operating_vs_financing"

    equity = classify_balance_sheet_line(
        _li("Share capital", 10, 12, concept="share_capital")
    )
    assert equity.category == "Equity"

    cash = classify_balance_sheet_line(
        _li("Cash and cash equivalents", 10, 12, concept="cash")
    )
    assert cash.category == "Financial Asset"


def test_customer_prepayment_reformulation_reduces_nowc_and_nola_not_net_debt():
    """Current prepayments cut NOWC; noncurrent cut NOLA; neither raises Net Debt."""
    fin = StandardizedFinancials(
        ticker="GC",
        company_name="Gift Card Co",
        currency="USD",
        units="USD in Thousands",
        jurisdiction="US",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110, concept="cash"),
            _li("Accounts receivable", 40, 42, concept="accounts_receivable"),
            _li("Property, plant and equipment", 80, 85, concept="ppe"),
            _li("Accounts payable", 15, 16, concept="accounts_payable"),
            _li(
                "Unredeemed gift card liability",
                20,
                22,
                concept="unredeemed_gift_card_liability",
            ),
            _li(
                "Non-current deferred revenue",
                10,
                11,
                concept="noncurrent_deferred_revenue",
            ),
            _li("Long-term debt", 30, 28, concept="long_term_debt"),
            _li("Share capital and reserves", 145, 160, concept="retained_earnings"),
            _li("Total assets", 220, 237, concept="total_assets"),
            _li("Total liabilities", 75, 77, concept="total_liabilities"),
            _li("Total equity", 145, 160, concept="total_equity"),
        ],
        cash_flow=[],
    )
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    check_reformulation_integrity(reform, periods)

    # NOWC = AR - AP - gift card = 40-15-20 = 5 ; 42-16-22 = 4
    assert reform.nowc == (5.0, 4.0)
    # NOLA = PPE - noncurrent deferred = 80-10 = 70 ; 85-11 = 74
    assert reform.nola == (70.0, 74.0)
    # Net Debt = LT debt - cash = 30-100 = -70 ; 28-110 = -82
    assert reform.net_debt == (-70.0, -82.0)
    assert reform.implied_equity == reform.reported_equity

    without_prepay = reformulate_balance_sheet(
        StandardizedFinancials(
            ticker="GC",
            company_name="Gift Card Co",
            currency="USD",
            units="USD in Thousands",
            jurisdiction="US",
            periods=_periods(),
            income_statement=[],
            balance_sheet=[
                _li("Cash and cash equivalents", 100, 110, concept="cash"),
                _li("Accounts receivable", 40, 42, concept="accounts_receivable"),
                _li("Property, plant and equipment", 80, 85, concept="ppe"),
                _li("Accounts payable", 15, 16, concept="accounts_payable"),
                _li("Long-term debt", 30, 28, concept="long_term_debt"),
                _li(
                    "Share capital and reserves",
                    175,
                    193,
                    concept="retained_earnings",
                ),
            ],
            cash_flow=[],
        ),
        periods,
    )
    assert reform.nowc[0] < without_prepay.nowc[0]
    assert reform.nola[0] < without_prepay.nola[0]
    assert reform.net_debt[0] == without_prepay.net_debt[0]


# --- Generic property-and-equipment balance classification (G2) ---


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Property and equipment, net", "property_plant_and_equipment"),
        ("Property and equipment, net", ""),
        ("Property and equipment", ""),
        ("Property, plant and equipment", ""),
        ("Property plant and equipment", ""),
        ("Property, plant & equipment", ""),
        ("Property plant & equipment", ""),
        ("Property, plant, and equipment", ""),
        ("Net property and equipment", ""),
        ("Property and equipment net", ""),
        ("Net property, plant and equipment", ""),
        ("Property plant and equipment net", ""),
        ("Property plant & equipment, net", ""),
        ("Net property, plant, and equipment", ""),
        ("Miscellaneous balance", "property_plant_equipment"),
        ("Miscellaneous balance", "property_plant_and_equipment"),
        ("Property and equipment, net", "property_plant_equipment"),
    ],
)
def test_ppe_balances_classify_as_operating_long_term_asset(label, concept):
    decision = classify_balance_sheet_line(_li(label, 100, 110, concept=concept))
    assert decision.category == "Operating Long-Term Asset"
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.overridden is False
    assert "property and equipment" in decision.reason.lower()


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Accounts payable for property and equipment", ""),
        ("Accounts payable for property and equipment", "unrelated_xyz"),
        ("Accounts payable for property and equipment", "accounts_payable"),
        ("Property and equipment payable", ""),
        ("Property and equipment payable", "unrelated_xyz"),
        ("Property and equipment payable", "accounts_payable"),
    ],
)
def test_ppe_payable_labels_remain_operating_wc_liability(label, concept):
    decision = classify_balance_sheet_line(_li(label, 100, 110, concept=concept))
    assert decision.category == "Operating Working Capital Liability"
    assert decision.overridden is False


_PPE_PUNCTUATION_MOVEMENT_CONCEPTS = ("", "unrelated_xyz", "property_plant_equipment", "property_plant_and_equipment")


@pytest.mark.parametrize("concept", _PPE_PUNCTUATION_MOVEMENT_CONCEPTS)
@pytest.mark.parametrize(
    "label",
    [
        "Property plant & equipment additions",
        "Property, plant, and equipment disposals",
    ],
)
def test_ppe_punctuation_reported_movements_fail_closed(label, concept):
    """Public classifier rejects ampersand / Oxford-comma movement labels."""
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 100, 110, concept=concept))


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Purchases of property and equipment", ""),
        ("Purchase of property and equipment", ""),
        ("Proceeds from sale of property and equipment", ""),
        ("Depreciation of property and equipment", ""),
        ("Impairment of property and equipment", ""),
        ("Additions to property and equipment", ""),
        ("Payments for property and equipment", ""),
        ("Change in property and equipment", ""),
        ("Property and equipment additions", ""),
        ("Property and equipment disposals", ""),
        ("Property and equipment payments", ""),
        ("Property and equipment sales", ""),
        ("Property and equipment changes", ""),
        ("Purchases of property, plant and equipment", ""),
        ("Property, plant and equipment additions", ""),
        ("Additions to property, plant and equipment", ""),
        # Punctuation-normalized topic + leading/trailing movement markers.
        ("Property plant & equipment additions", ""),
        ("Property plant & equipment disposals", ""),
        ("Property plant & equipment payments", ""),
        ("Property plant & equipment sales", ""),
        ("Property plant & equipment changes", ""),
        ("Additions to property plant & equipment", ""),
        ("Disposals of property plant & equipment", ""),
        ("Payments for property plant & equipment", ""),
        ("Sales of property plant & equipment", ""),
        ("Changes in property plant & equipment", ""),
        ("Property, plant, and equipment additions", ""),
        ("Property, plant, and equipment disposals", ""),
        ("Property, plant, and equipment payments", ""),
        ("Property, plant, and equipment sales", ""),
        ("Property, plant, and equipment changes", ""),
        ("Additions to property, plant, and equipment", ""),
        ("Disposals of property, plant, and equipment", ""),
        ("Payments for property, plant, and equipment", ""),
        ("Sales of property, plant, and equipment", ""),
        ("Changes in property, plant, and equipment", ""),
        ("Property and equipment additions", "unrelated_xyz"),
        ("Property and equipment additions", "property_plant_equipment"),
        ("Property and equipment additions", "property_plant_and_equipment"),
        ("Property plant & equipment additions", "unrelated_xyz"),
        ("Property plant & equipment additions", "property_plant_equipment"),
        ("Property plant & equipment additions", "property_plant_and_equipment"),
        ("Property, plant, and equipment disposals", "unrelated_xyz"),
        ("Property, plant, and equipment disposals", "property_plant_equipment"),
        (
            "Property, plant, and equipment disposals",
            "property_plant_and_equipment",
        ),
        ("Purchases of property, plant and equipment", "property_plant_equipment"),
        (
            "Property and equipment, net",
            "purchases_of_property_plant_equipment",
        ),
        (
            "Property and equipment, net",
            "proceeds_from_property_plant_and_equipment",
        ),
        (
            "Property and equipment, net",
            "depreciation_of_property_plant_equipment",
        ),
        (
            "Property and equipment, net",
            "impairment_of_property_plant_and_equipment",
        ),
        (
            "Property and equipment, net",
            "additions_to_property_plant_equipment",
        ),
        ("Miscellaneous balance", "purchases_of_property_plant_equipment"),
        ("Miscellaneous balance", "additions_to_property_plant_and_equipment"),
    ],
)
def test_ppe_movement_rows_do_not_classify_as_ppe_balances(label, concept):
    item = _li(label, 100, 110, concept=concept)
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(item)


def test_ppe_override_still_wins():
    item = _li(
        "Property and equipment, net",
        100,
        110,
        concept="property_plant_and_equipment",
    )
    default = classify_balance_sheet_line(item)
    assert default.category == "Operating Long-Term Asset"
    assert default.overridden is False

    overridden = classify_balance_sheet_line(item, override="Financial Asset")
    assert overridden.category == "Financial Asset"
    assert overridden.overridden is True
    assert overridden.reason == "User override"

    rejected = _li("Property and equipment additions", 100, 110, concept="")
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(rejected)
    forced = classify_balance_sheet_line(
        rejected, override="Operating Long-Term Asset"
    )
    assert forced.category == "Operating Long-Term Asset"
    assert forced.overridden is True

    punct_rejected = _li(
        "Property plant & equipment additions", 100, 110, concept=""
    )
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(punct_rejected)
    punct_forced = classify_balance_sheet_line(
        punct_rejected, override="Operating Long-Term Asset"
    )
    assert punct_forced.category == "Operating Long-Term Asset"
    assert punct_forced.overridden is True


def test_ppe_preserves_existing_plant_wording_and_unrelated_rows():
    plant = classify_balance_sheet_line(
        _li("Property, plant and equipment", 100, 110, concept="")
    )
    assert plant.category == "Operating Long-Term Asset"

    # Plant-wording movements fail closed (no legacy PPE asset fallthrough).
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(
            _li("Purchases of property, plant and equipment", 100, 110, concept="")
        )

    cash = classify_balance_sheet_line(
        _li("Cash and cash equivalents", 10, 12, concept="cash")
    )
    assert cash.category == "Financial Asset"

    payable = classify_balance_sheet_line(
        _li("Accounts payable", 10, 12, concept="accounts_payable")
    )
    assert payable.category == "Operating Working Capital Liability"

    bare_ppe = classify_balance_sheet_line(_li("PPE", 10, 12, concept=""))
    assert bare_ppe.category == "Operating Long-Term Asset"


def test_ppe_balance_has_no_judgment_case():
    fin = StandardizedFinancials(
        ticker="PPE",
        company_name="PPE Co",
        currency="USD",
        units="USD",
        jurisdiction="US",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 40, 42, concept="cash"),
            _li(
                "Property and equipment, net",
                100,
                110,
                concept="property_plant_and_equipment",
            ),
            _li("Accounts payable", 8, 9, concept="accounts_payable"),
            _li("Share capital and reserves", 132, 143, concept="retained_earnings"),
        ],
        cash_flow=[],
    )
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    assert not any(case.label == "Property and equipment, net" for case in cases)
    idx = next(
        i
        for i, item in enumerate(fin.balance_sheet)
        if item.label == "Property and equipment, net"
    )
    assert reform.decisions[idx].category == "Operating Long-Term Asset"
    assert reform.decisions[idx].judgment_code is None


# --- Generic ordinary common-stock equity classification (G3) ---


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Common stock", "common_stock"),
        ("Common stock", ""),
        ("Common stock", "unrelated_xyz"),
        ("common stock", "common_stock"),
        ("COMMON STOCK", ""),
        ("  Common   stock  ", ""),
        ("Miscellaneous balance", "common_stock"),
        ("Equity residual", "common_stock"),
    ],
)
def test_common_stock_balances_classify_as_equity(label, concept):
    decision = classify_balance_sheet_line(_li(label, 100, 110, concept=concept))
    assert decision.category == "Equity"
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.overridden is False
    assert "common-stock" in decision.reason.lower() or "common stock" in decision.reason.lower()


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        # Excluded concepts paired with whole-label Common stock.
        ("Common stock", "redeemable_common_stock"),
        ("Common stock", "common_stock_subject_to_redemption"),
        ("Common stock", "mandatorily_redeemable_common_stock"),
        ("Common stock", "preferred_stock"),
        ("Common stock", "preference_shares"),
        ("Common stock", "investment_in_common_stock"),
        ("Common stock", "common_stock_investment"),
        ("Common stock", "issuance_of_common_stock"),
        ("Common stock", "proceeds_from_issuance_of_common_stock"),
        ("Common stock", "repurchase_of_common_stock"),
        ("Common stock", "payments_for_repurchase_of_common_stock"),
        ("Common stock", "purchase_of_common_stock"),
        # Excluded labels paired with exact common_stock concept.
        ("Redeemable common stock", "common_stock"),
        ("Mandatorily redeemable common stock", "common_stock"),
        ("Common stock subject to mandatory redemption", "common_stock"),
        ("Preferred stock", "common_stock"),
        ("Investment in common stock", "common_stock"),
        ("Issuance of common stock", "common_stock"),
        ("Proceeds from issuance of common stock", "common_stock"),
        ("Repurchase of common stock", "common_stock"),
        ("Payments for repurchase of common stock", "common_stock"),
        ("Purchase of common stock", "common_stock"),
        # Label-only / empty-concept excluded forms.
        ("Redeemable common stock", ""),
        ("Preferred stock", ""),
        ("Repurchase of common stock", ""),
        ("Issuance of common stock", ""),
        ("Proceeds from issuance of common stock", ""),
    ],
)
def test_common_stock_excluded_pairs_do_not_use_equity_rule(label, concept):
    """Excluded instruments/movements must not enter the ordinary-equity rule."""
    item = _li(label, 100, 110, concept=concept)
    try:
        decision = classify_balance_sheet_line(item)
    except UnclassifiedBalanceSheetLineError:
        return
    assert "Ordinary common-stock" not in decision.reason


@pytest.mark.parametrize(
    ("label", "concept", "category", "judgment_code"),
    [
        ("Long-term debt", "common_stock", "Financial Liability", None),
        ("Accounts payable", "common_stock", "Operating Working Capital Liability", None),
        ("Notes payable", "common_stock", "Financial Liability", None),
        (
            "Accrued expenses",
            "common_stock",
            "Operating Working Capital Liability",
            None,
        ),
        (
            "Pension obligations",
            "common_stock",
            "Operating Long-Term Liability",
            "pension_obligation_operating_vs_financing",
        ),
        (
            "Retirement benefit obligations",
            "common_stock",
            "Operating Long-Term Liability",
            "pension_obligation_operating_vs_financing",
        ),
        (
            "Post-employment benefits",
            "common_stock",
            "Operating Long-Term Liability",
            "pension_obligation_operating_vs_financing",
        ),
        (
            "Other current liabilities",
            "common_stock",
            "Operating Working Capital Liability",
            None,
        ),
        (
            "Other non-current liabilities",
            "common_stock",
            "Operating Long-Term Liability",
            None,
        ),
        (
            "Other noncurrent liabilities",
            "common_stock",
            "Operating Long-Term Liability",
            None,
        ),
    ],
)
def test_common_stock_concept_with_supported_liability_labels(
    label, concept, category, judgment_code
):
    """Liability labels paired with common_stock keep supported liability categories."""
    decision = classify_balance_sheet_line(_li(label, 100, 110, concept=concept))
    assert decision.category == category
    assert decision.judgment_code == judgment_code
    assert decision.ambiguous is (judgment_code is not None)
    assert "Ordinary common-stock" not in decision.reason


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Common stock", "accounts_payable"),
        ("Common stock", "other_current_liabilities"),
        ("Common stock", "other_noncurrent_liabilities"),
        ("Common stock", "miscellaneous_liability"),
        ("Miscellaneous liability", "common_stock"),
        ("Liability balance", "common_stock"),
        # Contradictory liability concepts on ordinary Common stock balances.
        ("Common stock", "pension_obligation"),
        ("Common stock", "accrued_expenses"),
        ("Common stock", "retirement_benefit_obligation"),
        ("Common stock", "post_employment_benefits"),
        ("Common stock", "retirement_benefits"),
        ("Common stock", "postemployment_obligation"),
    ],
)
def test_common_stock_unsupported_liability_contradictions_raise(label, concept):
    """Unsupported liability/common-stock contradictions fail closed."""
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 100, 110, concept=concept))


def test_common_stock_label_with_debt_concept_remains_financial_liability():
    """Decisive debt concepts still win over whole-label Common stock."""
    decision = classify_balance_sheet_line(
        _li("Common stock", 100, 110, concept="long_term_debt")
    )
    assert decision.category == "Financial Liability"
    assert "Ordinary common-stock" not in decision.reason


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Cash paid for common stock", "common_stock"),
        ("Common stock", "cash_paid_for_common_stock"),
        ("Cash paid for common stock", ""),
        ("Cash paid for common stock", "unrelated_xyz"),
        ("cash paid for common stock", ""),
        ("CASH PAID FOR COMMON STOCK", ""),
        ("  Cash   paid  for  common   stock  ", ""),
        ("Cash-paid for common stock", "common_stock"),
        ("Cash-paid-for common-stock", ""),
        ("Cash-paid-for common-stock", "common_stock"),
        ("Cash paid—for common stock", ""),
        ("Cash paid—for common stock", "common_stock"),
        ("Paid-for common stock", ""),
        ("Paid-for common stock", "common_stock"),
        ("Cash paid for common stock.", "common_stock"),
        ("Cash paid for common stock", "cash"),
        ("Cash paid for common stock", "accounts_payable"),
        ("Cash paid for common stock payable", "common_stock"),
        ("Cash paid for common stock in retained earnings", ""),
        ("Cash paid for common stock from paid-in capital", ""),
        ("Payments for common stock", ""),
        ("Payment for common stock", "common_stock"),
        ("Common stock", "paid_for_common_stock"),
        # paidin substring must not suppress genuine payment detection
        ("Common stock", "common_stock_paid_in_cash"),
        ("Common stock", "paid_in_cash"),
        ("Common stock", "CommonStockPaidInCash"),
        ("Common stock", "common_stock_paid_in_cash_for_shares"),
        # paidincapital must not suppress co-occurring paid-in-cash wording
        ("Common stock", "common_stock_paid_in_cash_from_paid_in_capital"),
        ("Common stock", "CommonStockPaidInCashFromPaidInCapital"),
        ("Common stock", "common-stock-paid-in-cash-from-paid-in-capital"),
        ("Common stock", "common_stock.paid_in_cash.from_paid_in_capital"),
        ("Common stock", "paid_in_cash_from_paid_in_capital"),
        ("Common stock", "paid_in_cash_from_additional_paid_in_capital"),
        ("Common stock", "from_paid_in_capital_paid_in_cash"),
        ("Common stock", "from_additional_paid_in_capital_common_stock_paid_in_cash"),
        # Payment stems still reject when paid-in-capital wording co-occurs
        ("Common stock", "cash_paid_from_paid_in_capital"),
        ("Common stock", "paid_for_from_additional_paid_in_capital"),
        ("Common stock", "cash_paid_for_common_stock_from_paid_in_capital"),
    ],
)
def test_common_stock_payment_movements_raise_unclassified(label, concept):
    """Payment movements fail closed before cash/liability/equity fallbacks."""
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, 100, 110, concept=concept))


@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Common stock", "paid_in_capital"),
        ("Common stock", "additional_paid_in_capital"),
        ("Paid-in capital", "paid_in_capital"),
        ("Additional paid-in capital", "additional_paid_in_capital"),
        ("Paid-in capital", "common_stock"),
        ("Additional paid-in capital", "common_stock"),
    ],
)
def test_common_stock_paid_in_capital_balances_remain_equity(label, concept):
    """Paid-in-capital balances stay non-ambiguous Equity (not payment movements)."""
    decision = classify_balance_sheet_line(_li(label, 100, 110, concept=concept))
    assert decision.category == "Equity"
    assert decision.ambiguous is False
    assert decision.judgment_code is None


def test_common_stock_investment_retains_financial_asset_behavior():
    decision = classify_balance_sheet_line(
        _li("Investment in common stock", 100, 110, concept="common_stock")
    )
    assert decision.category == "Financial Asset"
    assert "Ordinary common-stock" not in decision.reason


def test_common_stock_redeemable_with_debt_label_remains_liability():
    decision = classify_balance_sheet_line(
        LineItem(
            label="Long-term debt",
            concept="CommonStockSubjectToRedemption",
            values={P1: 10, P2: 12},
        )
    )
    assert decision.category == "Financial Liability"
    assert "Ordinary common-stock" not in decision.reason


def test_common_stock_override_still_wins():
    item = _li("Common stock", 100, 110, concept="common_stock")
    default = classify_balance_sheet_line(item)
    assert default.category == "Equity"
    assert default.overridden is False

    overridden = classify_balance_sheet_line(item, override="Exclude")
    assert overridden.category == "Exclude"
    assert overridden.overridden is True
    assert overridden.reason == "User override"

    rejected = _li("Repurchase of common stock", 100, 110, concept="common_stock")
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(rejected)
    forced = classify_balance_sheet_line(rejected, override="Equity")
    assert forced.category == "Equity"
    assert forced.overridden is True

    payment = _li("Cash paid for common stock", 100, 110, concept="common_stock")
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(payment)
    payment_forced = classify_balance_sheet_line(payment, override="Equity")
    assert payment_forced.category == "Equity"
    assert payment_forced.overridden is True


def test_common_stock_preserves_existing_equity_components_and_g1_g2():
    retained = classify_balance_sheet_line(
        _li("Retained earnings", 100, 110, concept="retained_earnings")
    )
    assert retained.category == "Equity"

    share_capital = classify_balance_sheet_line(
        _li("Share capital", 100, 110, concept="share_capital")
    )
    assert share_capital.category == "Equity"

    paid_in = classify_balance_sheet_line(
        _li("Paid-in capital", 100, 110, concept="")
    )
    assert paid_in.category == "Equity"
    assert "Ordinary common-stock" not in paid_in.reason

    additional_paid_in = classify_balance_sheet_line(
        _li("Additional paid-in capital", 100, 110, concept="")
    )
    assert additional_paid_in.category == "Equity"

    gift = classify_balance_sheet_line(
        _li(
            "Unredeemed gift card liability",
            10,
            12,
            concept="unredeemed_gift_card_liability",
        )
    )
    assert gift.category == "Operating Working Capital Liability"

    ppe = classify_balance_sheet_line(
        _li(
            "Property and equipment, net",
            100,
            110,
            concept="property_plant_and_equipment",
        )
    )
    assert ppe.category == "Operating Long-Term Asset"

    equity_method = classify_balance_sheet_line(
        LineItem(
            label="Investment in associate",
            concept="EquityMethodInvestments",
            values={P1: 10, P2: 12},
        )
    )
    assert equity_method.category == "Operating Long-Term Asset"


def test_common_stock_balance_has_no_judgment_case():
    fin = StandardizedFinancials(
        ticker="CS",
        company_name="Common Stock Co",
        currency="USD",
        units="USD",
        jurisdiction="US",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 40, 42, concept="cash"),
            _li("Common stock", 100, 110, concept="common_stock"),
            _li("Accounts payable", 8, 9, concept="accounts_payable"),
            _li("Retained earnings", 32, 43, concept="retained_earnings"),
        ],
        cash_flow=[],
    )
    periods = [P1, P2]
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    assert not any(case.label == "Common stock" for case in cases)
    idx = next(
        i for i, item in enumerate(fin.balance_sheet) if item.label == "Common stock"
    )
    assert reform.decisions[idx].category == "Equity"
    assert reform.decisions[idx].judgment_code is None
    assert reform.decisions[idx].ambiguous is False
