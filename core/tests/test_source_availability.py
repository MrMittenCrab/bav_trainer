"""Generic source-availability gating for interest-dependent historical analysis."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.engine.reference_model import ReferenceModelBuilder
from core.model.financial_math import compute_anchor
from core.model.line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, is_source_unavailable
from core.model.source_availability import (
    REASON_ABSENT_LINE,
    REASON_AVAILABLE,
    REASON_MISSING_PERIOD_VALUE,
    assess_concept_availability,
    assess_interest_availability,
    comparable_interest_history_available,
    historical_average_after_tax_cod,
)
from core.model.source_values import MissingHistoricalValueError
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook
from core.tests.test_normalization import _inject_formula_and_cached_value

ROOT = Path(__file__).resolve().parents[2]
LULU_STD = ROOT / "benchmark" / "lululemon" / "reconciled" / "standardized.json"

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)
P3 = date(2026, 12, 31)


def _li(label, v1, v2, concept="", *, v3=None):
    values = {P1: v1, P2: v2}
    if v3 is not None:
        values[P3] = v3
    return LineItem(label=label, values=values, concept=concept)


def _periods(*dates: date) -> list[FinancialPeriod]:
    return [
        FinancialPeriod(end_date=d, label=f"FY{d.year}")
        for d in dates
    ]


def _base_fin(**overrides) -> StandardizedFinancials:
    periods = _periods(P1, P2)
    kwargs = dict(
        ticker="SYN",
        company_name="Synthetic Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=periods,
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", 330, 355),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    kwargs.update(overrides)
    return StandardizedFinancials(**kwargs)


def _labels(ws) -> dict[str, int]:
    return {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}


def test_each_interest_concept_missing_independently_gates(tmp_path: Path):
    periods = [P1, P2]
    missing_expense = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    missing_income = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    for fin, absent in (
        (missing_expense, "interest_expense"),
        (missing_income, "interest_income"),
    ):
        avail = assess_interest_availability(fin, periods)
        assert avail.interest_expense.line_present is (absent != "interest_expense")
        assert avail.interest_income.line_present is (absent != "interest_income")
        for period in periods:
            assert avail.output("net_interest", period).available is False
            assert absent in avail.output("net_interest", period).missing_concepts
            assert avail.output("nopat", period).available is False
        with pytest.raises(MissingLineError, match=absent):
            resolve_line(fin.income_statement, absent, required=True)
        anchor = compute_anchor(fin, periods)
        assert all(is_source_unavailable(v) for v in anchor.historical.net_interest)
        assert all(is_source_unavailable(v) for v in anchor.historical.nopat)
        assert is_source_unavailable(anchor.hist_avg_after_tax_cod)
        assert anchor.historical.revenue == [1000.0, 1100.0]
        assert anchor.historical.net_income == [170.0, 187.0]
        builder = ReferenceModelBuilder(fin)
        _, answer = build_training_workbook(fin, tmp_path / f"Miss_{absent}_Trainer.xlsx")
        wb = load_workbook(answer, data_only=False)
        labels = _labels(wb["Condensed Financials"])
        present = "Interest Income" if absent == "interest_expense" else "Interest Expense"
        missing = "Interest Expense" if absent == "interest_expense" else "Interest Income"
        assert present in labels
        assert missing not in labels
        assert wb["Condensed Financials"].cell(
            row=labels["Net Interest"], column=2
        ).value == SOURCE_UNAVAILABLE
        assert wb["Condensed Financials"].cell(row=labels["NOPAT"], column=2).value == SOURCE_UNAVAILABLE
        families = {s.family_id for s in builder.expected_specs}
        assert "net_interest_fy" not in families
        assert "nopat_fy" not in families
        assert "revenue_link" in families
        assert "flev" in families
        smap = load_semantic_map(answer)
        assert {c.family_id for c in smap.all_ordered()} == families
        wb.close()


def test_both_interest_concepts_absent_gates_dependents(tmp_path: Path):
    fin = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    periods = [P1, P2]
    avail = assess_interest_availability(fin, periods)
    assert avail.interest_expense.line_present is False
    assert avail.interest_income.line_present is False
    assert avail.interest_expense.for_period(P1).reason == REASON_ABSENT_LINE
    anchor = compute_anchor(fin, periods)
    assert anchor.dupont["Sales Growth"][1] == pytest.approx(0.1)
    assert not is_source_unavailable(anchor.dupont["FLEV"][1])
    assert not is_source_unavailable(anchor.dupont["Actual ROE"][1])
    assert is_source_unavailable(anchor.dupont["NOPAT Margin"][0])
    assert is_source_unavailable(anchor.dupont["RNOA"][1])
    assert is_source_unavailable(anchor.dupont["After-tax CoD"][1])
    assert is_source_unavailable(anchor.dupont["Spread"][1])
    assert is_source_unavailable(anchor.dupont["ROE (decomposed)"][1])
    builder = ReferenceModelBuilder(fin)
    trainer, answer = build_training_workbook(fin, tmp_path / "BothAbsent_Trainer.xlsx")
    families = {s.family_id for s in builder.expected_specs}
    for family in (
        "net_interest_fy",
        "net_interest_after_tax_fy",
        "nopat_fy",
        "nopat_margin",
        "rnoa",
        "after_tax_cod",
        "spread",
        "roe_decomp",
        "rnoa_margin_turnover",
    ):
        assert family not in families
    for family in ("revenue_link", "sales_growth", "flev", "actual_roe", "noa_turnover"):
        assert family in families
    blank = check_workbook(trainer)
    assert blank.blank == blank.total
    assert blank.correct == 0
    assert blank.incorrect == 0
    smap = load_semantic_map(answer)
    wb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        from core.trainer.semantic_io import parse_cell_ref

        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    assert filled.incorrect == 0


def test_partial_period_absence_gates_only_dependent_periods(tmp_path: Path):
    fin = _base_fin()
    item = next(i for i in fin.income_statement if i.label == "Finance costs")
    del item.values[P2]
    periods = [P1, P2]
    avail = assess_concept_availability(fin.income_statement, "interest_expense", periods)
    assert avail.available_on(P1) is True
    assert avail.available_on(P2) is False
    assert avail.for_period(P2).reason == REASON_MISSING_PERIOD_VALUE
    anchor = compute_anchor(fin, periods)
    assert anchor.historical.net_interest[0] == pytest.approx(35.0)
    assert is_source_unavailable(anchor.historical.net_interest[1])
    assert not is_source_unavailable(anchor.historical.nopat[0])
    assert is_source_unavailable(anchor.historical.nopat[1])
    assert is_source_unavailable(anchor.hist_avg_after_tax_cod)
    with pytest.raises(MissingHistoricalValueError, match="interest_expense"):
        from core.model.source_values import required_period_value

        required_period_value(item, P2, field="interest_expense")
    builder = ReferenceModelBuilder(fin)
    trainer, answer = build_training_workbook(fin, tmp_path / "Partial_Trainer.xlsx")
    answer_wb = load_workbook(answer, data_only=False)
    labels = _labels(answer_wb["Condensed Financials"])
    ws = answer_wb["Condensed Financials"]
    assert str(ws.cell(row=labels["Net Interest"], column=2).value).startswith("=")
    assert ws.cell(row=labels["Net Interest"], column=3).value == SOURCE_UNAVAILABLE
    answer_wb.close()
    _assert_condensed_interest_not_linked_to_blank(
        trainer,
        answer,
        source_label="Finance costs",
        condensed_label="Interest Expense",
        period_count=2,
    )
    families = {(s.family_id, s.period_index) for s in builder.expected_specs}
    assert ("net_interest_fy", 0) in families
    assert ("net_interest_fy", 1) not in families


def test_reported_zero_is_available_not_gated(tmp_path: Path):
    fin = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", 0, 0),
            _li("Finance income", 0, 0),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    periods = [P1, P2]
    avail = assess_interest_availability(fin, periods)
    assert avail.output("net_interest", P1).available is True
    anchor = compute_anchor(fin, periods)
    assert anchor.historical.net_interest == [0.0, 0.0]
    assert anchor.historical.net_interest_after_tax == [0.0, 0.0]
    assert anchor.historical.nopat == [170.0, 187.0]
    _, answer = build_training_workbook(fin, tmp_path / "Zero_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    labels = _labels(wb["Condensed Financials"])
    assert "Interest Expense" in labels
    assert "Interest Income" in labels
    ws = wb["Condensed Financials"]
    assert ws.cell(row=labels["NOPAT"], column=2).value != SOURCE_UNAVAILABLE
    for label in ("Interest Expense", "Interest Income"):
        for col in (2, 3):
            value = ws.cell(row=labels[label], column=col).value
            assert str(value).startswith("=")
            assert value != SOURCE_UNAVAILABLE
    wb.close()


def test_alias_and_explicit_concept_precedence():
    alias = _base_fin()
    periods = [P1, P2]
    exp = resolve_line(alias.income_statement, "interest_expense", required=True)
    inc = resolve_line(alias.income_statement, "interest_income", required=True)
    assert exp.item is not None and exp.item.label == "Finance costs"
    assert inc.item is not None and inc.item.label == "Finance income"
    explicit = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Non-operating finance line", -40, -50, concept="interest_expense"),
            _li("Non-operating income line", 5, 6, concept="interest_income"),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    exp_x = resolve_line(explicit.income_statement, "interest_expense", required=True)
    assert exp_x.item is not None
    assert exp_x.item.concept == "interest_expense"
    assert exp_x.item.label == "Non-operating finance line"
    mixed = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -1, -1),
            _li("Bond coupon", -40, -50, concept="interest_expense"),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    chosen = resolve_line(mixed.income_statement, "interest_expense", required=True)
    assert chosen.item is not None
    assert chosen.item.concept == "interest_expense"
    assert chosen.item.label == "Bond coupon"
    anchor = compute_anchor(mixed, periods)
    assert anchor.historical.net_interest == [35.0, 44.0]


def test_ambiguity_and_malformed_inputs_still_raise():
    dup = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Interest expense", -10, -12),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    with pytest.raises(AmbiguousLineError):
        assess_concept_availability(dup.income_statement, "interest_expense", [P1, P2])
    with pytest.raises(AmbiguousLineError):
        compute_anchor(dup, [P1, P2])
    malformed = _base_fin()
    item = next(i for i in malformed.income_statement if i.label == "Finance costs")
    item.values[P1] = "not-a-number"  # type: ignore[assignment]
    with pytest.raises(ValueError, match="invalid source value"):
        assess_concept_availability(malformed.income_statement, "interest_expense", [P1, P2])
    with pytest.raises(ValueError, match="invalid source value"):
        compute_anchor(malformed, [P1, P2])


def test_unrelated_required_facts_still_fail_closed():
    fin = _base_fin()
    ni = next(i for i in fin.income_statement if i.label == "Profit for the year")
    del ni.values[P2]
    with pytest.raises(MissingHistoricalValueError, match="net_income"):
        compute_anchor(fin, [P1, P2])
    missing_rev = _base_fin(
        income_statement=[
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    with pytest.raises(MissingLineError, match="revenue"):
        compute_anchor(missing_rev, [P1, P2])


def test_adjacent_period_dependencies_and_undefined_ratio_distinct():
    three = StandardizedFinancials(
        ticker="SYN3",
        company_name="Three Period Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_periods(P1, P2, P3),
        income_statement=[
            _li("Revenue", 1000, 1100, v3=1210),
            _li("Finance costs", -40, -50, v3=-55),
            _li("Finance income", 5, 6, v3=7),
            _li("Profit before tax", 200, 220, v3=240),
            _li("Income tax expense", -30, -33, v3=-36),
            _li("Profit for the year", 170, 187, v3=204),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110, v3=120),
            _li("Trade receivables", 80, 90, v3=100),
            _li("Property, plant and equipment", 400, 420, v3=440),
            _li("Trade payables", 50, 55, v3=60),
            _li("Bank borrowings", 200, 210, v3=220),
            _li("Total equity", 330, 355, v3=380),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60, v3=70)],
    )
    expense = next(i for i in three.income_statement if i.label == "Finance costs")
    del expense.values[P1]
    periods = [P1, P2, P3]
    anchor = compute_anchor(three, periods)
    assert is_source_unavailable(anchor.historical.nopat[0])
    assert not is_source_unavailable(anchor.historical.nopat[1])
    assert not is_source_unavailable(anchor.historical.nopat[2])
    assert is_source_unavailable(anchor.dupont["NOPAT Margin"][0])
    assert not is_source_unavailable(anchor.dupont["RNOA"][1])
    assert not is_source_unavailable(anchor.hist_avg_after_tax_cod)
    avail = assess_interest_availability(three, periods)
    assert avail.output("hist_avg_after_tax_cod").available is True
    assert avail.output("hist_avg_after_tax_cod").reason == REASON_AVAILABLE
    assert P1 not in avail.output("hist_avg_after_tax_cod").missing_periods

    zero_debt = _base_fin(
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 100, 110),
            _li("Total equity", 430, 455),
        ]
    )
    z_anchor = compute_anchor(zero_debt, [P1, P2])
    assert z_anchor.dupont["After-tax CoD"][1] == UNDEFINED_RATIO
    assert not is_source_unavailable(z_anchor.hist_avg_after_tax_cod)
    assert z_anchor.hist_avg_after_tax_cod == pytest.approx(0.04)


def test_python_excel_export_reload_and_check_agreement(tmp_path: Path):
    fin = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    restored = standardized_from_payload(standardized_to_payload(fin))
    periods = canonical_fiscal_periods(restored)
    original = compute_anchor(fin, periods)
    round_trip = compute_anchor(restored, periods)
    assert original.historical.revenue == round_trip.historical.revenue
    assert original.historical.net_interest == round_trip.historical.net_interest
    trainer, answer = build_training_workbook(restored, tmp_path / "Reload_Trainer.xlsx")
    smap = load_semantic_map(answer)
    families = {c.family_id for c in smap.all_ordered()}
    assert "nopat_fy" not in families
    answer_wb = load_workbook(answer, data_only=False)
    trainer_wb = load_workbook(trainer, data_only=False)
    a_labels = _labels(answer_wb["Condensed Financials"])
    t_labels = _labels(trainer_wb["Condensed Financials"])
    assert a_labels["NOPAT"] == t_labels["NOPAT"]
    assert answer_wb["Condensed Financials"].cell(row=a_labels["NOPAT"], column=2).value == SOURCE_UNAVAILABLE
    assert trainer_wb["Condensed Financials"].cell(row=t_labels["NOPAT"], column=2).value == SOURCE_UNAVAILABLE
    for comp in smap.all_ordered():
        assert not is_source_unavailable(comp.expected_value)
        assert str(comp.formula).startswith("=")
    answer_wb.close()
    trainer_wb.close()
    blank = check_workbook(trainer)
    assert blank.blank == blank.total
    filled_wb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        filled_wb[comp.tab].cell(row=row, column=col).value = comp.formula
    filled_wb.save(trainer)
    filled_wb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    target = next(c for c in smap.all_ordered() if c.family_id == "revenue_link")
    _inject_formula_and_cached_value(
        trainer, target.tab, target.cell, formula="=0", cached_value=0.0
    )
    incorrect = check_workbook(trainer)
    assert incorrect.incorrect == 1


def test_lululemon_unchanged_facts_gate_interest_and_keep_supported_outputs(tmp_path: Path):
    payload = json.loads(LULU_STD.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    periods = canonical_fiscal_periods(fin)
    assert periods == [
        date(2022, 1, 30),
        date(2023, 1, 29),
        date(2024, 1, 28),
        date(2025, 2, 2),
        date(2026, 2, 1),
    ]
    assert periods[1:] == [
        date(2023, 1, 29),
        date(2024, 1, 28),
        date(2025, 2, 2),
        date(2026, 2, 1),
    ]
    avail = assess_interest_availability(fin, periods)
    assert avail.interest_expense.line_present is False
    assert avail.interest_income.line_present is False
    with pytest.raises(MissingLineError, match="interest_expense"):
        resolve_line(fin.income_statement, "interest_expense", required=True)
    anchor = compute_anchor(fin, periods)
    assert anchor.historical.revenue == [
        6256617.0,
        8110518.0,
        9619278.0,
        10588126.0,
        11102600.0,
    ]
    assert anchor.historical.revenue[1:] == [8110518.0, 9619278.0, 10588126.0, 11102600.0]
    assert all(is_source_unavailable(v) for v in anchor.historical.net_interest)
    assert all(is_source_unavailable(v) for v in anchor.historical.nopat)
    assert is_source_unavailable(anchor.hist_avg_after_tax_cod)
    ncit = next(
        i for i in fin.balance_sheet if i.concept == "non_current_income_taxes_payable"
    )
    assert ncit.values[date(2022, 1, 30)] == 38074.0
    assert ncit.values[date(2023, 1, 29)] == 28555.0
    assert ncit.values[date(2024, 1, 28)] == 15864.0
    assert ncit.values[date(2025, 2, 2)] == 0.0
    assert ncit.values[date(2026, 2, 1)] is None
    common = next(i for i in fin.balance_sheet if i.label == "Common stock")
    assert common.values[date(2023, 1, 29)] == 611.0
    assert common.values[date(2024, 1, 28)] == 606.0
    assert common.values[date(2025, 2, 2)] == 581.0
    assert common.values[date(2026, 2, 1)] == 557.0
    assert common.values == {
        date(2022, 1, 30): 616.0,
        date(2023, 1, 29): 611.0,
        date(2024, 1, 28): 606.0,
        date(2025, 2, 2): 581.0,
        date(2026, 2, 1): 557.0,
    }
    builder = ReferenceModelBuilder(fin)
    trainer, answer = build_training_workbook(fin, tmp_path / "LululemonAvail")
    assert trainer.exists() and answer.exists()
    families = {s.family_id for s in builder.expected_specs}
    assert "nopat_fy" not in families
    assert "net_interest_fy" not in families
    assert "after_tax_cod" not in families
    assert "revenue_link" in families
    assert "ppe_capex" in families
    assert "cash_after_ppe_capex" in families
    assert "sbc_to_revenue" in families
    assert "sbc_to_operating_cash_flow" in families
    assert "operating_cash_flow_less_sbc" in families
    assert "acquisition_cash_outflow" in families
    assert "acquisition_cash_to_revenue" in families
    assert "cash_after_ppe_capex_and_acquisitions" in families
    assert "share_repurchase_outflow" in families
    assert "share_repurchase_to_revenue" in families
    assert "cash_after_ppe_capex_acquisitions_and_repurchases" in families
    assert "cash_movement_from_flows" in families
    assert "cash_movement_difference" in families
    assert "cash_ending_from_flows" in families
    assert "cash_ending_difference" in families
    assert "gross_margin" in families
    assert "reported_operating_margin" in families
    assert "net_operating_expense_burden" in families
    assert "reconstructed_operating_margin_change" in families
    assert "inventory_intensity" in families
    assert "inventory_change" in families
    assert "inventory_revenue_scale_effect" in families
    assert "inventory_intensity_effect" in families
    assert "reconstructed_inventory_change" in families
    assert "inventory_balance_implied_cf_adjustment" in families
    assert "inventory_cf_adjustment_difference" in families
    wb = load_workbook(answer, data_only=False)
    labels = _labels(wb["Condensed Financials"])
    assert "Interest Expense" not in labels
    assert "Interest Income" not in labels
    assert wb["Condensed Financials"].cell(row=labels["NOPAT"], column=2).value == SOURCE_UNAVAILABLE
    assert ncit.values[date(2026, 2, 1)] is None
    blank = check_workbook(trainer)
    assert blank.blank == blank.total == len(builder.expected_specs)
    assert blank.incorrect == 0
    smap = load_semantic_map(answer)
    twb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        twb[comp.tab].cell(row=row, column=col).value = comp.formula
    twb.save(trainer)
    twb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    wb.close()


def _three_fin() -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="SYN3",
        company_name="Three Period Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_periods(P1, P2, P3),
        income_statement=[
            _li("Revenue", 1000, 1100, v3=1210),
            _li("Finance costs", -40, -50, v3=-55),
            _li("Finance income", 5, 6, v3=7),
            _li("Profit before tax", 200, 220, v3=240),
            _li("Income tax expense", -30, -33, v3=-36),
            _li("Profit for the year", 170, 187, v3=204),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110, v3=120),
            _li("Trade receivables", 80, 90, v3=100),
            _li("Property, plant and equipment", 400, 420, v3=440),
            _li("Trade payables", 50, 55, v3=60),
            _li("Bank borrowings", 200, 210, v3=220),
            _li("Total equity", 330, 355, v3=380),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60, v3=70)],
    )


def _drop_period_value(item: LineItem, period: date, mode: str) -> None:
    if mode == "omitted":
        del item.values[period]
    else:
        item.values[period] = None


def _interest_items(fin: StandardizedFinancials) -> tuple[LineItem, LineItem]:
    expense = next(i for i in fin.income_statement if i.label == "Finance costs")
    income = next(i for i in fin.income_statement if i.label == "Finance income")
    return expense, income


def _assert_python_metadata_hist_avg_agree(fin: StandardizedFinancials, periods: list[date]) -> None:
    avail = assess_interest_availability(fin, periods)
    anchor = compute_anchor(fin, periods)
    hist_avg = avail.output("hist_avg_after_tax_cod")
    python_unavailable = is_source_unavailable(anchor.hist_avg_after_tax_cod)
    assert hist_avg.available is (not python_unavailable)
    shared = historical_average_after_tax_cod(
        [value for value in anchor.dupont["After-tax CoD"] if value is not None],
        interest_history_available=comparable_interest_history_available(
            [value for value in anchor.dupont["After-tax CoD"] if value is not None],
            anchor.historical.net_interest,
        ),
    )
    if python_unavailable:
        assert is_source_unavailable(shared)
    else:
        assert shared == pytest.approx(float(anchor.hist_avg_after_tax_cod))


def _assert_condensed_interest_not_linked_to_blank(
    trainer: Path,
    answer: Path,
    *,
    source_label: str,
    condensed_label: str,
    period_count: int,
) -> None:
    for path in (trainer, answer):
        wb = load_workbook(path, data_only=False)
        src_ws = wb["Income Statement"]
        con_ws = wb["Condensed Financials"]
        src_labels = _labels(src_ws)
        con_labels = _labels(con_ws)
        if condensed_label not in con_labels:
            wb.close()
            continue
        src_row = src_labels[source_label]
        con_row = con_labels[condensed_label]
        for j in range(period_count):
            source_val = src_ws.cell(row=src_row, column=2 + j).value
            condensed_val = con_ws.cell(row=con_row, column=2 + j).value
            if source_val is None:
                assert condensed_val == SOURCE_UNAVAILABLE
                assert not (
                    isinstance(condensed_val, str) and str(condensed_val).startswith("=")
                )
            else:
                assert str(condensed_val).startswith("=")
                assert condensed_val != SOURCE_UNAVAILABLE
        wb.close()


@pytest.mark.parametrize("mode", ["omitted", "none"])
@pytest.mark.parametrize("which", ["expense", "income", "both"])
@pytest.mark.parametrize("slot", ["opening", "interior", "latest"])
def test_interest_missing_independently_or_together_by_slot(
    tmp_path: Path, mode: str, which: str, slot: str
):
    fin = _three_fin()
    periods = [P1, P2, P3]
    target = {"opening": P1, "interior": P2, "latest": P3}[slot]
    expense, income = _interest_items(fin)
    if which in ("expense", "both"):
        _drop_period_value(expense, target, mode)
    if which in ("income", "both"):
        _drop_period_value(income, target, mode)
    avail = assess_interest_availability(fin, periods)
    concept = "interest_expense" if which != "income" else "interest_income"
    row = (
        avail.interest_expense.for_period(target)
        if concept == "interest_expense"
        else avail.interest_income.for_period(target)
    )
    assert row.available is False
    assert row.reason == REASON_MISSING_PERIOD_VALUE
    assert avail.output("net_interest", target).available is False
    hist_avg = avail.output("hist_avg_after_tax_cod")
    if slot == "opening":
        assert hist_avg.available is True
        assert target not in hist_avg.missing_periods
    else:
        assert hist_avg.available is False
        assert target in hist_avg.missing_periods
    _assert_python_metadata_hist_avg_agree(fin, periods)
    restored = standardized_from_payload(standardized_to_payload(fin))
    trainer, answer = build_training_workbook(
        restored, tmp_path / f"Slot_{slot}_{which}_{mode}_Trainer.xlsx"
    )
    _assert_condensed_interest_not_linked_to_blank(
        trainer,
        answer,
        source_label="Finance costs",
        condensed_label="Interest Expense",
        period_count=3,
    )
    _assert_condensed_interest_not_linked_to_blank(
        trainer,
        answer,
        source_label="Finance income",
        condensed_label="Interest Income",
        period_count=3,
    )
    builder = ReferenceModelBuilder(restored)
    families = {(s.family_id, s.period_index) for s in builder.expected_specs}
    slot_index = {"opening": 0, "interior": 1, "latest": 2}[slot]
    assert ("net_interest_fy", slot_index) not in families
    if slot != "opening":
        assert ("after_tax_cod", slot_index) not in families
        assert "after_tax_cod" not in {s.family_id for s in builder.expected_specs if s.period_index == slot_index}
    smap = load_semantic_map(answer)
    assert {c.family_id for c in smap.all_ordered()} == {s.family_id for s in builder.expected_specs}
    blank = check_workbook(trainer)
    assert blank.blank == blank.total
    assert blank.incorrect == 0


def test_opening_only_omission_hist_avg_cod_is_0_374(tmp_path: Path):
    fin = _base_fin()
    expense, _income = _interest_items(fin)
    del expense.values[P1]
    periods = [P1, P2]
    net_int_p2 = -((-50.0) + 6.0)
    etr_p2 = -(-33.0) / 220.0
    niat_p2 = net_int_p2 * (1.0 - etr_p2)
    independent_cod = niat_p2 / 100.0
    assert independent_cod == pytest.approx(0.374)
    avail = assess_interest_availability(fin, periods)
    assert avail.output("hist_avg_after_tax_cod").available is True
    anchor = compute_anchor(fin, periods)
    assert anchor.hist_avg_after_tax_cod == pytest.approx(0.374)
    assert is_source_unavailable(anchor.historical.net_interest[0])
    assert anchor.historical.net_interest[1] == pytest.approx(44.0)
    _assert_python_metadata_hist_avg_agree(fin, periods)
    trainer, answer = build_training_workbook(fin, tmp_path / "OpeningCod_Trainer.xlsx")
    _assert_condensed_interest_not_linked_to_blank(
        trainer,
        answer,
        source_label="Finance costs",
        condensed_label="Interest Expense",
        period_count=2,
    )
    builder = ReferenceModelBuilder(fin)
    families = {(s.family_id, s.period_index) for s in builder.expected_specs}
    assert ("after_tax_cod", 1) in families
    assert ("net_interest_fy", 0) not in families
    assert ("net_interest_fy", 1) in families


def test_mixed_numeric_undefined_comparable_cod_averages_numeric():
    fin = _three_fin()
    cash = next(i for i in fin.balance_sheet if i.label == "Cash and cash equivalents")
    debt = next(i for i in fin.balance_sheet if i.label == "Bank borrowings")
    cash.values = {P1: 100.0, P2: 110.0, P3: 120.0}
    debt.values = {P1: 100.0, P2: 110.0, P3: 220.0}
    equity = next(i for i in fin.balance_sheet if i.label == "Total equity")
    equity.values = {P1: 430.0, P2: 455.0, P3: 380.0}
    periods = [P1, P2, P3]
    anchor = compute_anchor(fin, periods)
    assert anchor.dupont["After-tax CoD"][1] == UNDEFINED_RATIO
    niat_p3 = -((-55.0) + 7.0) * (1.0 - (-(-36.0) / 240.0))
    independent = niat_p3 / 50.0
    assert anchor.dupont["After-tax CoD"][2] == pytest.approx(independent)
    assert anchor.hist_avg_after_tax_cod == pytest.approx(independent)
    avail = assess_interest_availability(fin, periods)
    assert avail.output("hist_avg_after_tax_cod").available is True
    _assert_python_metadata_hist_avg_agree(fin, periods)


def test_missing_comparable_interest_keeps_hist_avg_unavailable():
    fin = _three_fin()
    expense, _income = _interest_items(fin)
    del expense.values[P2]
    periods = [P1, P2, P3]
    avail = assess_interest_availability(fin, periods)
    assert avail.output("after_tax_cod", P2).available is False
    assert avail.output("after_tax_cod", P3).available is True
    assert avail.output("hist_avg_after_tax_cod").available is False
    assert P2 in avail.output("hist_avg_after_tax_cod").missing_periods
    anchor = compute_anchor(fin, periods)
    assert is_source_unavailable(anchor.hist_avg_after_tax_cod)
    assert not is_source_unavailable(anchor.dupont["After-tax CoD"][2])
    _assert_python_metadata_hist_avg_agree(fin, periods)


def test_no_numeric_comparable_cod_uses_fallback_only_when_interest_present():
    zero_debt = _base_fin(
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 100, 110),
            _li("Total equity", 430, 455),
        ]
    )
    periods = [P1, P2]
    z_anchor = compute_anchor(zero_debt, periods)
    assert z_anchor.dupont["After-tax CoD"][1] == UNDEFINED_RATIO
    assert z_anchor.hist_avg_after_tax_cod == pytest.approx(0.04)
    z_avail = assess_interest_availability(zero_debt, periods)
    assert z_avail.output("hist_avg_after_tax_cod").available is True
    _assert_python_metadata_hist_avg_agree(zero_debt, periods)

    missing = _base_fin(
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 100, 110),
            _li("Total equity", 430, 455),
        ]
    )
    expense, _income = _interest_items(missing)
    del expense.values[P2]
    m_anchor = compute_anchor(missing, periods)
    assert is_source_unavailable(m_anchor.hist_avg_after_tax_cod)
    m_avail = assess_interest_availability(missing, periods)
    assert m_avail.output("hist_avg_after_tax_cod").available is False
    _assert_python_metadata_hist_avg_agree(missing, periods)


def test_single_period_history_agrees_on_metadata_and_python(tmp_path: Path):
    present = StandardizedFinancials(
        ticker="SYN1",
        company_name="Single Period Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_periods(P1),
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", 330, 355),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    for item in (*present.income_statement, *present.balance_sheet, *present.cash_flow):
        item.values.pop(P2, None)
    periods = [P1]
    p_anchor = compute_anchor(present, periods)
    assert p_anchor.hist_avg_after_tax_cod == pytest.approx(0.04)
    p_avail = assess_interest_availability(present, periods)
    assert p_avail.output("hist_avg_after_tax_cod").available is True
    _assert_python_metadata_hist_avg_agree(present, periods)

    absent = StandardizedFinancials(
        ticker="SYN1A",
        company_name="Single Period Absent Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_periods(P1),
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", 330, 355),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    for item in (*absent.income_statement, *absent.balance_sheet, *absent.cash_flow):
        item.values.pop(P2, None)
    a_anchor = compute_anchor(absent, periods)
    assert is_source_unavailable(a_anchor.hist_avg_after_tax_cod)
    a_avail = assess_interest_availability(absent, periods)
    assert a_avail.output("hist_avg_after_tax_cod").available is False
    _assert_python_metadata_hist_avg_agree(absent, periods)
    trainer, answer = build_training_workbook(absent, tmp_path / "SingleAbsent_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    labels = _labels(wb["Condensed Financials"])
    assert "Interest Expense" not in labels
    assert wb["Condensed Financials"].cell(row=labels["NOPAT"], column=2).value == SOURCE_UNAVAILABLE
    wb.close()
    builder = ReferenceModelBuilder(absent)
    assert "nopat_fy" not in {s.family_id for s in builder.expected_specs}
    smap = load_semantic_map(answer)
    assert all(not is_source_unavailable(c.expected_value) for c in smap.all_ordered())
