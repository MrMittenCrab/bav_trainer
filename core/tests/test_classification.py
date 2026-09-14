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
