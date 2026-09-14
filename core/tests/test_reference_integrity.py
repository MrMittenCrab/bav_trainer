"""Formula-integrity tests for the semantic Answer Key (Step 2)."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook
import pytest

from core.data.interface import DocumentManifest, DocumentType, LineItem
from core.engine.component_catalog import COMPONENT_CATALOG, concrete_component_id, expand_historical_specs
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.classification import BALANCE_SHEET_CATEGORIES
from core.model.financial_math import compute_anchor
from core.model.line_resolver import resolve_line
from core.model.ri_engine import run_scenario
from core.model.source_values import required_period_value
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"


def _ingest_demo():
    adapter = HKManualDocumentAdapter()
    return adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])


def _build_pair(tmp_path, assumptions=None):
    data = _ingest_demo()
    return build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx", assumptions)


def _latest(smap, family_id: str):
    comps = [c for c in smap.all_ordered() if c.family_id == family_id]
    assert comps, family_id
    return max(comps, key=lambda c: c.period_index or 0)


def _at_period(smap, family_id: str, period_index: int):
    return next(
        c for c in smap.all_ordered()
        if c.family_id == family_id and c.period_index == period_index
    )


def test_normal_v1_build_does_not_call_run_scenario(tmp_path, monkeypatch):
    import core.engine.reference_model as rm

    def fail(*args, **kwargs):
        raise AssertionError("forecast engine executed in historical-only v1")

    monkeypatch.setattr(rm, "run_scenario", fail)

    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
    )

    assert trainer.exists()
    assert answer.exists()


def test_normal_v1_build_requires_no_forecast_assumptions(tmp_path):
    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
        assumptions={"classificationOverrides": {}},
    )
    assert trainer.exists()
    assert answer.exists()
    sidecar = answer.with_suffix(".assumptions.json")
    if sidecar.exists():
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        assert "scenarios" not in payload
        assert "growthVector" not in json.dumps(payload)
        assert "marginVector" not in json.dumps(payload)
        assert "terminalGrowth" not in json.dumps(payload)
        assert "beta" not in json.dumps(payload)
        market = payload.get("marketData") or {}
        assert "dilutedShares" not in market


def test_anchor_exposes_tax_and_interest_expected_values():
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(data, periods)
    last = periods[-1]

    pretax = resolve_line(data.income_statement, "pretax_income", required=True).item
    tax = resolve_line(data.income_statement, "tax_expense", required=True).item
    int_exp = resolve_line(data.income_statement, "interest_expense", required=True).item
    int_inc = resolve_line(data.income_statement, "interest_income", required=True).item
    ni = resolve_line(data.income_statement, "net_income", required=True).item

    from core.model.ratio_values import ratio_or_na

    pretax_v = required_period_value(pretax, last, field="pretax_income")
    tax_v = required_period_value(tax, last, field="tax_expense")
    expected_etr = ratio_or_na(-tax_v, pretax_v)
    expected_net_int = -(
        required_period_value(int_exp, last, field="interest_expense")
        + required_period_value(int_inc, last, field="interest_income")
    )

    assert anchor.effective_tax_rate == pytest.approx(expected_etr)
    assert anchor.net_interest == pytest.approx(expected_net_int)
    assert anchor.net_interest_after_tax == pytest.approx(
        anchor.net_interest * (1 - float(anchor.effective_tax_rate))
    )
    assert anchor.nopat == pytest.approx(
        required_period_value(ni, last, field="net_income")
        + float(anchor.net_interest_after_tax)
    )


def test_anchor_exposes_full_historical_series():
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(data, periods)

    assert len(anchor.historical.revenue) == len(periods)
    assert len(anchor.historical.nopat) == len(periods)
    assert anchor.historical.revenue[-1] == pytest.approx(anchor.revenue)
    assert anchor.historical.net_interest[-1] == pytest.approx(anchor.net_interest)
    assert anchor.historical.effective_tax_rate[-1] == pytest.approx(anchor.effective_tax_rate)
    assert anchor.historical.net_interest_after_tax[-1] == pytest.approx(
        anchor.net_interest_after_tax
    )
    assert anchor.historical.nopat[-1] == pytest.approx(anchor.nopat)

    for j in range(len(periods)):
        etr_j = float(anchor.historical.effective_tax_rate[j])
        niat_j = float(anchor.historical.net_interest_after_tax[j])
        assert niat_j == pytest.approx(anchor.historical.net_interest[j] * (1 - etr_j))
        assert float(anchor.historical.nopat[j]) == pytest.approx(
            anchor.historical.net_income[j] + niat_j
        )

    rev_item = resolve_line(data.income_statement, "revenue", required=True).item
    ni_item = resolve_line(data.income_statement, "net_income", required=True).item
    for j, period in enumerate(periods):
        assert anchor.historical.revenue[j] == pytest.approx(
            required_period_value(rev_item, period, field="revenue")
        )
        assert anchor.historical.net_income[j] == pytest.approx(
            required_period_value(ni_item, period, field="net_income")
        )


HISTORICAL_REFORMULATION_IDS = (
    "effective_tax_rate_fy",
    "net_interest_fy",
    "net_interest_after_tax_fy",
    "nopat_fy",
    "owca_agg",
    "owcl_agg",
    "nowc_agg",
    "olta_agg",
    "oltl_agg",
    "nola_agg",
    "noa_agg",
    "financial_assets_agg",
    "financial_liabilities_agg",
    "net_debt",
    "equity_reformulated_fy",
)

AGGREGATE_SUMIF_IDS = (
    "owca_agg",
    "owcl_agg",
    "olta_agg",
    "oltl_agg",
    "financial_assets_agg",
    "financial_liabilities_agg",
)

DUPONT_IDS = (
    "rnoa",
    "after_tax_cod",
    "spread",
    "flev",
    "roe_decomp",
    "actual_roe",
)


def test_cli_assumptions_propagate(tmp_path):
    """CLI-supplied historical classification overrides must affect reformulation."""
    data = _ingest_demo()
    _, answer_default = build_training_workbook(data, tmp_path / "Default_Trainer.xlsx")
    smap_default = load_semantic_map(answer_default)

    # Move Cash into operating WC so NOA changes without breaking BS integrity.
    assumptions = {
        "classificationOverrides": {
            "label:Cash and cash equivalents": "Operating Working Capital Asset",
        }
    }
    from core.__main__ import main

    out = tmp_path / "Assumed_Trainer.xlsx"
    assumptions_path = tmp_path / "custom.assumptions.json"
    assumptions_path.write_text(json.dumps(assumptions), encoding="utf-8")
    assert main(["build", str(DEMO_JSON), "-o", str(out), "-a", str(assumptions_path)]) == 0

    answer = tmp_path / "Assumed_Answer_Key.xlsx"
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    smap = load_semantic_map(answer)
    found = False
    for r in range(1, 40):
        if ws.cell(row=r, column=1).value == "Cash and cash equivalents":
            assert ws.cell(row=r, column=2).value == "Operating Working Capital Asset"
            found = True
            break
    assert found
    assert _latest(smap, "nowc_agg").expected_value != _latest(
        smap_default, "nowc_agg"
    ).expected_value
    wb.close()


def test_nopat_formula_adds_after_tax_net_interest(tmp_path):
    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    nopat = _latest(smap, "nopat_fy")
    formula = nopat.formula.replace(" ", "")
    assert formula.startswith("=")
    assert "+" in formula
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    assert "Net Interest" in labels
    assert "Net Interest After Tax" in labels
    assert "NOPAT" in labels
    niat_r = labels["Net Interest After Tax"]
    ni_r = labels["Net Income"]
    nopat_r = labels["NOPAT"]
    row, col = parse_cell_ref(nopat.cell)
    cell_formula = str(ws.cell(row=row, column=col).value)
    assert row == nopat_r
    assert str(niat_r) in cell_formula.replace(" ", "")
    assert str(ni_r) in cell_formula.replace(" ", "")
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(data, periods)
    assert nopat.expected_value == anchor.nopat
    from core.model.line_resolver import resolve_line

    ni_item = resolve_line(data.income_statement, "net_income", required=True).item
    assert abs(
        float(nopat.expected_value)
        - float(required_period_value(ni_item, periods[-1], field="net_income"))
    ) > 1.0
    wb.close()


def test_condensed_aggregates_are_on_sheet_sumif(tmp_path):
    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    for family_id in ("nowc_agg", "noa_agg", "net_debt"):
        formula = _latest(smap, family_id).formula
        assert "Balance Sheet" not in formula
    # Category SUMIFs live on the detail aggregate rows that feed NOWC / NOA / Net Debt.
    for label in (
        "Operating Working Capital Assets",
        "Operating Long-Term Assets",
        "Financial Liabilities",
    ):
        f = str(ws.cell(row=labels[label], column=2).value)
        assert "SUMIF" in f and "$B$" in f
    wb.close()


def test_dupont_cod_uses_niat_not_nopat(tmp_path):
    _, answer = _build_pair(tmp_path)
    wb = load_workbook(answer, data_only=False)
    ws = wb["ALT DuPont"]
    cod_row = None
    for r in range(1, 20):
        if ws.cell(row=r, column=1).value == "After-tax CoD":
            cod_row = r
            break
    assert cod_row is not None
    formula = str(ws.cell(row=cod_row, column=5).value)
    assert "NOPAT" not in formula
    condensed = wb["Condensed Financials"]
    niat_row = next(
        r for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "Net Interest After Tax"
    )
    nopat_row = next(
        r for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "NOPAT"
    )
    assert str(niat_row) in formula
    assert str(nopat_row) not in formula.split("/")[0]
    wb.close()


def test_dupont_uses_condensed_equity_not_bs_row_seven(tmp_path):
    _, answer = _build_pair(tmp_path)
    wb = load_workbook(answer, data_only=False)
    ws = wb["ALT DuPont"]
    condensed = wb["Condensed Financials"]
    eq_row = next(
        r for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "Equity (NOA - Net Debt)"
    )
    flev_row = next(r for r in range(1, 20) if ws.cell(row=r, column=1).value == "FLEV")
    actual_row = next(r for r in range(1, 20) if ws.cell(row=r, column=1).value == "Actual ROE")
    flev_f = str(ws.cell(row=flev_row, column=5).value)
    actual_f = str(ws.cell(row=actual_row, column=5).value)
    assert "Balance Sheet" not in flev_f
    assert "Balance Sheet" not in actual_f
    assert "Condensed Financials" in flev_f and str(eq_row) in flev_f
    assert "Condensed Financials" in actual_f and str(eq_row) in actual_f
    wb.close()


def test_ten_year_forecast_chain_populated(tmp_path):
    """Internal deferred-forecast path still builds a full 10-year chain."""
    data = _ingest_demo()
    from core.engine.reference_model import ReferenceModelBuilder

    answer = tmp_path / "Deferred_Answer_Key.xlsx"
    ReferenceModelBuilder(data, include_deferred_forecast=True).build(answer)
    wb = load_workbook(answer, data_only=False)
    for scenario in ("Bear", "Base", "Bull"):
        ws = wb[f"Model_{scenario}"]
        # Locate Sales row and first forecast col from Y1 header
        sales_row = next(r for r in range(1, 50) if ws.cell(row=r, column=1).value == "Sales")
        ae_row = next(
            r for r in range(1, 50) if ws.cell(row=r, column=1).value == "Abnormal Earnings"
        )
        disc_row = next(
            r for r in range(1, 50) if ws.cell(row=r, column=1).value == "Discount Factor"
        )
        tv_row = next(r for r in range(1, 50) if ws.cell(row=r, column=1).value == "Terminal Value")
        # First forecast column: first Y1 header
        fc = next(
            c for c in range(2, 30)
            if ws.cell(row=20, column=c).value == "Y1"
        )
        for t in range(10):
            assert ws.cell(row=sales_row, column=fc + t).value not in (None, "")
            assert ws.cell(row=ae_row, column=fc + t).value not in (None, "")
            assert ws.cell(row=disc_row, column=fc + t).value not in (None, "")
            for label in (
                "NOPAT Margin",
                "NOWC",
                "NOLA",
                "Net Debt",
                "Book Equity",
                "NOPAT",
                "Net Income",
                "PV Abnormal Earnings",
            ):
                row = next(r for r in range(1, 50) if ws.cell(row=r, column=1).value == label)
                assert ws.cell(row=row, column=fc + t).value not in (None, ""), f"{scenario} {label} Y{t+1}"
        # Year-10 TV populated; PV TV references year-10 cells
        tv_cell = ws.cell(row=tv_row, column=fc + 9).value
        assert tv_cell not in (None, "")
        assert str(ae_row) in str(tv_cell)
        pv_tv_row = next(
            r for r in range(1, 50) if ws.cell(row=r, column=1).value == "PV Terminal Value"
        )
        pv_tv = str(ws.cell(row=pv_tv_row, column=fc).value)
        assert str(tv_row) in pv_tv
        assert str(disc_row) in pv_tv
        # No double-tax of after-tax CoD
        assert ws["B8"].value != "=B7*(1-B6)"
        assert ws["A7"].value == "After-tax CoD"
    wb.close()


def test_semantic_formulas_have_no_blank_required_refs(tmp_path):
    import re

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    wb = load_workbook(answer, data_only=False)
    assert len(smap.all_ordered()) == 312
    hist = expand_historical_specs(
        (_ingest_demo().fiscal_years() or _ingest_demo().period_dates())
    )
    assert len(hist) == 118
    assert len(smap.all_ordered()) == 312

    def _labels(ws):
        return {ws.cell(row=r, column=1).value: r for r in range(1, (ws.max_row or 1) + 1)}

    def _a1_refs(formula: str) -> list[tuple[str | None, str]]:
        """Extract optional sheet + A1 refs from a formula (test-only helper)."""
        refs = []
        for m in re.finditer(
            r"(?:'([^']+)'!)?(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)",
            formula,
        ):
            refs.append((m.group(1), m.group(2).replace("$", "")))
        return refs

    def _cell_populated(sheet: str, a1: str) -> bool:
        if ":" in a1:
            # range — check both ends
            start, end = a1.split(":")
            return _cell_populated(sheet, start) and _cell_populated(sheet, end)
        from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

        col_letter, row = coordinate_from_string(a1)
        val = wb[sheet].cell(row=row, column=column_index_from_string(col_letter)).value
        return val not in (None, "")

    for comp in smap.all_ordered():
        assert comp.expected_value is not None
        assert isinstance(comp.formula, str) and comp.formula.startswith("=")
        row, col = parse_cell_ref(comp.cell)
        cell_val = wb[comp.tab].cell(row=row, column=col).value
        assert isinstance(cell_val, str) and cell_val.startswith("=")
        assert cell_val == comp.formula
        for sheet, a1 in _a1_refs(comp.formula):
            target = sheet or comp.tab
            if target.startswith("_"):
                continue
            assert _cell_populated(target, a1.split(":")[0] if ":" in a1 else a1), (
                f"{comp.id} references blank {target}!{a1}"
            )

    condensed = wb["Condensed Financials"]
    cl = _labels(condensed)
    nopat = _latest(smap, "nopat_fy")
    assert str(cl["Net Income"]) in nopat.formula
    assert str(cl["Net Interest After Tax"]) in nopat.formula
    assert condensed.cell(row=cl["Net Income"], column=2).value not in (None, "")
    assert condensed.cell(row=cl["Net Interest After Tax"], column=2).value not in (None, "")

    assert "Condensed Financials" in _latest(smap, "rnoa").formula
    assert _latest(smap, "roe_decomp").formula.startswith("=")
    # Spread is local RNOA − CoD on the DuPont sheet
    spread_f = _latest(smap, "spread").formula
    assert spread_f.startswith("=")
    assert "-" in spread_f

    # Deferred forecast tabs are placeholders, not live practice surfaces.
    for name in ("Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary"):
        ws = wb[name]
        assert ws.sheet_state == "hidden"
        assert ws["A1"].value == "Deferred from historical-only v1"
    wb.close()


def test_python_expected_values_use_corrected_cod(tmp_path):
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(data, periods)
    sc = {
        "costOfEquity": 0.10,
        "terminalGrowth": 0.03,
        "taxRate": 0.165,
        "growthVector": [0.1] * 10,
        "marginVector": [0.15] * 10,
        "nowcRatioVector": [0.05] * 10,
        "nolaRatioVector": [0.5] * 10,
    }
    r_ok = run_scenario(sc, anchor, shares=1000.0)
    taxed_again = anchor.hist_avg_after_tax_cod * (1 - 0.165)
    r_bug = run_scenario(sc, anchor, shares=1000.0, hist_avg_after_tax_cod=taxed_again)
    assert r_ok.abnormal_earnings_y1 != r_bug.abnormal_earnings_y1

    # Internal deferred path still builds live model tabs for legacy isolation.
    from core.engine.reference_model import ReferenceModelBuilder

    answer = tmp_path / "Deferred_Answer_Key.xlsx"
    builder = ReferenceModelBuilder(data, include_deferred_forecast=True)
    builder.build(answer)
    smap = load_semantic_map(answer)
    wb = load_workbook(answer, data_only=False)
    ws = wb["Model_Base"]
    ni_row = next(r for r in range(1, 50) if ws.cell(row=r, column=1).value == "Net Income")
    fc = next(c for c in range(2, 30) if ws.cell(row=20, column=c).value == "Y1")
    ni_f = str(ws.cell(row=ni_row, column=fc).value)
    assert "$B$7" in ni_f
    assert smap.get("model_ae_y1").expected_value is not None
    wb.close()


def test_pair_behavior_still_holds(tmp_path):
    trainer, answer = _build_pair(tmp_path)
    assert trainer.exists() and answer.exists()
    smap = load_semantic_map(answer)
    wb_t = load_workbook(trainer, data_only=False)
    wb_a = load_workbook(answer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        ct = wb_t[comp.tab].cell(row=row, column=col)
        ca = wb_a[comp.tab].cell(row=row, column=col)
        assert ct.value is None
        assert ct.comment is None
        assert isinstance(ca.value, str) and ca.value.startswith("=")
        assert ca.comment is not None and ca.comment.text
    wb_t.close()
    wb_a.close()


# --- Step 2B source-resolution fixtures ---

def _synth_periods():
    from datetime import date
    from core.data.interface import FinancialPeriod

    return [
        FinancialPeriod(end_date=date(2024, 12, 31), label="FY2024"),
        FinancialPeriod(end_date=date(2025, 12, 31), label="FY2025"),
    ]


def _li(label, v1, v2, concept=""):
    from datetime import date
    from core.data.interface import LineItem

    return LineItem(
        label=label,
        values={date(2024, 12, 31): v1, date(2025, 12, 31): v2},
        concept=concept,
    )


def _base_fin(**overrides):
    from core.data.interface import StandardizedFinancials

    periods = _synth_periods()
    is_items = [
        _li("Revenue", 1000, 1100),
        _li("Finance costs", -40, -50),
        _li("Finance income", 5, 6),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    bs_items = [
        _li("Cash and cash equivalents", 100, 110),
        _li("Trade receivables", 80, 90),
        _li("Property, plant and equipment", 400, 420),
        _li("Trade payables", 50, 55),
        _li("Bank borrowings", 200, 210),
        _li("Total equity", 330, 355),
    ]
    cf_items = [_li("Net cash from operating activities", 50, 60)]
    kwargs = dict(
        ticker="SYN",
        company_name="Synthetic Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=periods,
        income_statement=is_items,
        balance_sheet=bs_items,
        cash_flow=cf_items,
    )
    kwargs.update(overrides)
    return StandardizedFinancials(**kwargs)


def test_explicit_zero_interest_income_still_populates_net_interest_chain(tmp_path):
    is_items = [
        _li("Revenue", 1000, 1100),
        _li("Finance costs", -40, -50),
        _li("Finance income", 0, 0),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    fin = _base_fin(income_statement=is_items)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert anchor.nopat != 0
    assert anchor.historical.net_interest == [40.0, 50.0]
    _, answer = build_training_workbook(fin, tmp_path / "ZeroInc_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    assert "Interest Income" in labels
    assert "Interest Expense" in labels
    for name in ("Net Interest", "Net Interest After Tax", "NOPAT"):
        row = labels[name]
        assert ws.cell(row=row, column=2).value not in (None, "")
    wb.close()


def test_explicit_zero_interest_expense_income_only_case(tmp_path):
    is_items = [
        _li("Revenue", 1000, 1100),
        _li("Finance income", 5, 6),
        _li("Finance costs", 0, 0),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    fin = _base_fin(income_statement=is_items)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert anchor.nopat != 0
    assert anchor.historical.net_interest == [-5.0, -6.0]
    _, answer = build_training_workbook(fin, tmp_path / "ZeroExp_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    assert "Interest Expense" in labels
    assert "Interest Income" in labels
    for name in ("Net Interest", "Net Interest After Tax", "NOPAT"):
        assert ws.cell(row=labels[name], column=2).value not in (None, "")
    wb.close()


def test_equity_alias_builds_and_matches_python(tmp_path):
    bs = [
        _li("Cash and cash equivalents", 100, 110),
        _li("Trade receivables", 80, 90),
        _li("Property, plant and equipment", 400, 420),
        _li("Trade payables", 50, 55),
        _li("Bank borrowings", 200, 210),
        _li("Equity attributable to owners of the Company", 330, 355),
    ]
    fin = _base_fin(balance_sheet=bs)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert anchor.equity == 355.0
    _, answer = build_training_workbook(fin, tmp_path / "EqAlias_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    implied = str(ws.cell(row=labels["Equity (NOA - Net Debt)"], column=3).value)
    reported = str(ws.cell(row=labels["Reported Equity"], column=3).value)
    assert "Balance Sheet" not in implied
    assert str(labels["NOA"]) in implied and str(labels["Net Debt"]) in implied
    assert "Balance Sheet" in reported
    wb.close()


def test_equity_absent_fallback_noa_minus_net_debt(tmp_path):
    bs = [
        _li("Cash and cash equivalents", 100, 110),
        _li("Trade receivables", 80, 90),
        _li("Property, plant and equipment", 400, 420),
        _li("Trade payables", 50, 55),
        _li("Bank borrowings", 200, 210),
    ]
    fin = _base_fin(balance_sheet=bs)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert abs(anchor.equity - (anchor.noa - anchor.net_debt)) < 1e-9
    _, answer = build_training_workbook(fin, tmp_path / "EqFallback_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    f = str(ws.cell(row=labels["Equity (NOA - Net Debt)"], column=2).value)
    assert "Balance Sheet" not in f
    assert str(labels["NOA"]) in f and str(labels["Net Debt"]) in f
    check_f = str(ws.cell(row=labels["CHECK"], column=2).value)
    assert "UNVERIFIED" in check_f
    wb.close()


def test_build_rejects_failed_source_checksum(tmp_path):
    data = _ingest_demo()
    # Break CF roll-up while leaving other statements intact.
    for item in data.cash_flow:
        if "operating activities" in item.label.lower():
            for pd in list(item.values):
                item.values[pd] = float(item.values[pd]) + 999.0
    import pytest

    with pytest.raises(ValueError, match="checksum"):
        build_training_workbook(data, tmp_path / "BrokenCF_Trainer.xlsx")


def test_build_rejects_reformulation_gap(tmp_path):
    from datetime import date
    from core.data.interface import FinancialPeriod, StandardizedFinancials
    from core.model.classification import ReformulationIntegrityError
    import pytest

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="GAP",
        company_name="Gap Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 100, 110),
            _li("Finance costs", 0, 0),
            _li("Finance income", 0, 0),
            _li("Profit before tax", 20, 22),
            _li("Income tax expense", -3, -3),
            _li("Profit for the year", 17, 19),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 40, 40),
            _li("Trade receivables", 30, 30),
            _li("Total assets", 100, 100),
            _li("Trade payables", 20, 20),
            _li("Bank borrowings", 30, 30),
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
    with pytest.raises(ReformulationIntegrityError):
        build_training_workbook(fin, tmp_path / "Gap_Trainer.xlsx")


def test_condensed_has_live_reconciliation_rows(tmp_path):
    _, answer = _build_pair(tmp_path)
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    required = [
        "Operating Working Capital Assets",
        "Operating Working Capital Liabilities",
        "NOWC",
        "Operating Long-Term Assets",
        "Operating Long-Term Liabilities",
        "NOLA",
        "NOA",
        "Financial Assets",
        "Financial Liabilities",
        "Net Debt",
        "Equity (NOA - Net Debt)",
        "Reported Equity",
        "Total Capital",
        "CHECK",
    ]
    for name in required:
        assert name in labels, name
    check_f = str(ws.cell(row=labels["CHECK"], column=2).value)
    assert check_f.startswith("=")
    assert "OK" in check_f and "CHECK" in check_f
    wb.close()


def test_classification_table_uses_shared_decisions(tmp_path):
    from core.model.classification import BALANCE_SHEET_CATEGORIES
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.financial_math import compute_anchor
    from core.data.interface import FinancialPeriod, StandardizedFinancials
    from datetime import date

    data = _ingest_demo()
    b = ReferenceModelBuilder(data)
    assumptions = b.assumptions
    assumptions["classificationOverrides"] = {
        "Goodwill": "Operating Long-Term Asset",
    }

    _, answer = build_training_workbook(
        data, tmp_path / "ClassDemo_Trainer.xlsx", assumptions
    )

    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(
        data,
        periods,
        classification_overrides={"Goodwill": "Operating Long-Term Asset"},
    )
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    start = None
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "Line Item":
            start = r + 1
            break
    assert start is not None
    notes_col = 3 + len(periods)
    by_label = {}
    r = start
    while ws.cell(row=r, column=1).value and ws.cell(row=r, column=2).value:
        label = ws.cell(row=r, column=1).value
        if label in ("CONDENSED INCOME STATEMENT", "CONDENSED BALANCE SHEET"):
            break
        by_label[label] = r
        r += 1
    for idx, decision in anchor.reformulation.decisions.items():
        label = data.balance_sheet[idx].label
        row = by_label[label]
        cell_val = ws.cell(row=row, column=2).value
        if isinstance(cell_val, str) and cell_val.startswith("="):
            assert "Accounting Judgment" in cell_val
            assert "$F$" in cell_val
            assert "$D$" not in cell_val
            assert decision.category in str(cell_val)
        else:
            assert cell_val == decision.category
        if decision.overridden:
            note = str(ws.cell(row=row, column=notes_col).value or "")
            assert "Override" in note
    cats = set()
    for dv in ws.data_validations.dataValidation:
        if dv.formula1:
            cats |= {c.strip() for c in dv.formula1.strip('"').split(",")}
    assert cats == set(BALANCE_SHEET_CATEGORIES)
    assert not any(c.startswith("Ambiguous") for c in cats)
    wb.close()

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="AMB",
        company_name="Amb Co",
        currency="HKD",
        units="mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 100, 110),
            _li("Finance costs", 0, 0),
            _li("Finance income", 0, 0),
            _li("Profit before tax", 20, 22),
            _li("Income tax expense", -3, -3),
            _li("Profit for the year", 17, 19),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 40, 40),
            _li("Trade receivables", 30, 30),
            _li("Property, plant and equipment", 30, 30),
            _li("Total assets", 100, 100),
            _li("Trade payables", 20, 20),
            _li("Operating lease liabilities", 30, 30),
            _li("Bank borrowings", 30, 30),
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
    _, answer2 = build_training_workbook(fin, tmp_path / "Amb_Trainer.xlsx")
    wb2 = load_workbook(answer2, data_only=False)
    ws2 = wb2["Condensed Financials"]
    lease_row = next(
        r
        for r in range(1, ws2.max_row + 1)
        if ws2.cell(row=r, column=1).value == "Operating lease liabilities"
    )
    note = str(ws2.cell(row=lease_row, column=5).value or "")
    assert "⚠ Review" in note
    wb2.close()


def test_duPont_uses_implied_equity(tmp_path):
    _, answer = _build_pair(tmp_path)
    wb = load_workbook(answer, data_only=False)
    condensed = wb["Condensed Financials"]
    ws = wb["ALT DuPont"]
    implied_row = next(
        r
        for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "Equity (NOA - Net Debt)"
    )
    reported_row = next(
        r
        for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "Reported Equity"
    )
    flev_row = next(r for r in range(1, 20) if ws.cell(row=r, column=1).value == "FLEV")
    actual_row = next(r for r in range(1, 20) if ws.cell(row=r, column=1).value == "Actual ROE")
    flev_f = str(ws.cell(row=flev_row, column=5).value)
    actual_f = str(ws.cell(row=actual_row, column=5).value)
    assert str(implied_row) in flev_f
    assert str(implied_row) in actual_f
    assert str(reported_row) not in flev_f
    assert str(reported_row) not in actual_f
    wb.close()


def test_historical_reformulation_formulas_match_answer_key_cells(tmp_path):
    trainer_path, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    wb = load_workbook(answer, data_only=False)
    for family_id in HISTORICAL_REFORMULATION_IDS:
        comps = [c for c in smap.all_ordered() if c.family_id == family_id]
        assert len(comps) == 5
        for comp in comps:
            assert comp.formula.startswith("=")
            assert comp.expected_value is not None
            row, col = parse_cell_ref(comp.cell)
            assert wb[comp.tab].cell(row=row, column=col).value == comp.formula
            if family_id in AGGREGATE_SUMIF_IDS:
                assert "SUMIF" in comp.formula
    wb.close()

    # Classification choices remain populated identically in Trainer vs Answer Key.
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer, data_only=False)
    class_start = None
    for r in range(1, 40):
        if wb_a["Condensed Financials"].cell(row=r, column=1).value == "Line Item":
            class_start = r + 1
            break
    assert class_start is not None
    for r in range(class_start, class_start + 50):
        label = wb_a["Condensed Financials"].cell(row=r, column=1).value
        cat = wb_a["Condensed Financials"].cell(row=r, column=2).value
        if not isinstance(label, str) or not label.strip():
            break
        if cat is None:
            continue
        if isinstance(cat, str) and cat.startswith("="):
            assert "Accounting Judgment" in cat
        else:
            assert cat in BALANCE_SHEET_CATEGORIES
        assert (
            wb_t["Condensed Financials"].cell(row=r, column=2).value
            == wb_a["Condensed Financials"].cell(row=r, column=2).value
        )
    wb_t.close()
    wb_a.close()


def test_dupont_chain_registers_all_six_latest_comparable_formulas(tmp_path):
    _, answer = _build_pair(tmp_path)
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    anchor = compute_anchor(data, periods)
    j_last = len(periods) - 1
    smap = load_semantic_map(answer)
    wb = load_workbook(answer, data_only=False)

    expected_map = {
        "rnoa": anchor.dupont["RNOA"][j_last],
        "after_tax_cod": anchor.dupont["After-tax CoD"][j_last],
        "spread": anchor.dupont["Spread"][j_last],
        "flev": anchor.dupont["FLEV"][j_last],
        "roe_decomp": anchor.dupont["ROE (decomposed)"][j_last],
        "actual_roe": anchor.dupont["Actual ROE"][j_last],
    }
    for family_id in DUPONT_IDS:
        comps = [c for c in smap.all_ordered() if c.family_id == family_id]
        assert len(comps) == 4
        comp = _latest(smap, family_id)
        assert comp.formula.startswith("=")
        row, col = parse_cell_ref(comp.cell)
        assert wb[comp.tab].cell(row=row, column=col).value == comp.formula
        assert comp.expected_value == pytest.approx(expected_map[family_id])
    wb.close()

    by_id = {c.id: c for c in COMPONENT_CATALOG}
    for family in COMPONENT_CATALOG:
        for dep in family.depends_on_current + family.depends_on_previous:
            assert by_id[dep].order < family.order


def test_multi_period_practice_surface_for_five_year_demo(tmp_path):
    from core.engine.component_catalog import (
        FIXED_ASSET_COMPONENT_CATALOG,
        LEASE_LIABILITY_COMPONENT_CATALOG,
        QUALITY_COMPONENT_CATALOG,
        QUALITY_CHANGE_COMPONENT_CATALOG,
        WORKING_CAPITAL_COMPONENT_CATALOG,
        PROFITABILITY_DRIVER_COMPONENT_CATALOG,
        PROFITABILITY_CHANGE_COMPONENT_CATALOG,
        ROE_ATTRIBUTION_COMPONENT_CATALOG,
    )

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 312

    families = {c.family_id for c in smap.all_ordered()}
    assert families == (
        {f.id for f in COMPONENT_CATALOG}
        | {f.id for f in QUALITY_COMPONENT_CATALOG}
        | {f.id for f in QUALITY_CHANGE_COMPONENT_CATALOG}
        | {f.id for f in WORKING_CAPITAL_COMPONENT_CATALOG}
        | {f.id for f in PROFITABILITY_DRIVER_COMPONENT_CATALOG}
        | {f.id for f in PROFITABILITY_CHANGE_COMPONENT_CATALOG}
        | {f.id for f in ROE_ATTRIBUTION_COMPONENT_CATALOG}
        | {f.id for f in FIXED_ASSET_COMPONENT_CATALOG}
        | {f.id for f in LEASE_LIABILITY_COMPONENT_CATALOG}
    )

    for family in COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in QUALITY_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in WORKING_CAPITAL_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in PROFITABILITY_DRIVER_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in PROFITABILITY_CHANGE_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        assert family.period_scope == "post_comparable"
        assert len(comps) == 3
    for family in ROE_ATTRIBUTION_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        if family.period_scope == "comparable":
            assert len(comps) == 4
        else:
            assert family.period_scope == "post_comparable"
            assert len(comps) == 3
    for family in FIXED_ASSET_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in LEASE_LIABILITY_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        expected = 5 if family.period_scope == "all" else 4
        assert len(comps) == expected
    for family in QUALITY_CHANGE_COMPONENT_CATALOG:
        comps = [c for c in smap.all_ordered() if c.family_id == family.id]
        if family.period_scope == "comparable":
            assert len(comps) == 4
        else:
            assert family.period_scope == "post_comparable"
            assert len(comps) == 3

    for comp in smap.all_ordered():
        assert comp.formula.startswith("=")
        assert comp.expected_value is not None


def test_multi_period_formula_dependencies_use_current_and_previous(tmp_path):
    _, answer = _build_pair(tmp_path)
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    smap = load_semantic_map(answer)

    # Find FY indices by year labels in period_end
    by_year = {p.year: j for j, p in enumerate(periods)}
    assert 2023 in by_year and 2024 in by_year and 2025 in by_year

    j23, j24, j25 = by_year[2023], by_year[2024], by_year[2025]
    rev23 = _at_period(smap, "revenue_link", j23)
    rev22 = _at_period(smap, "revenue_link", j23 - 1)
    growth23 = _at_period(smap, "sales_growth", j23)
    assert rev23.cell in growth23.formula
    assert rev22.cell in growth23.formula

    nopat24 = _at_period(smap, "nopat_fy", j24)
    noa24 = _at_period(smap, "noa_agg", j24)
    noa23 = _at_period(smap, "noa_agg", j23)
    rnoa24 = _at_period(smap, "rnoa", j24)
    assert nopat24.cell in rnoa24.formula or str(parse_cell_ref(nopat24.cell)[0]) in rnoa24.formula
    assert str(parse_cell_ref(noa24.cell)[0]) in rnoa24.formula
    assert str(parse_cell_ref(noa23.cell)[0]) in rnoa24.formula

    niat25 = _at_period(smap, "net_interest_after_tax_fy", j25)
    nd25 = _at_period(smap, "net_debt", j25)
    nd24 = _at_period(smap, "net_debt", j24)
    cod25 = _at_period(smap, "after_tax_cod", j25)
    assert str(parse_cell_ref(niat25.cell)[0]) in cod25.formula
    assert str(parse_cell_ref(nd25.cell)[0]) in cod25.formula
    assert str(parse_cell_ref(nd24.cell)[0]) in cod25.formula

    eq25 = _at_period(smap, "equity_reformulated_fy", j25)
    eq24 = _at_period(smap, "equity_reformulated_fy", j24)
    flev25 = _at_period(smap, "flev", j25)
    assert str(parse_cell_ref(nd25.cell)[0]) in flev25.formula
    assert str(parse_cell_ref(nd24.cell)[0]) in flev25.formula
    assert str(parse_cell_ref(eq25.cell)[0]) in flev25.formula
    assert str(parse_cell_ref(eq24.cell)[0]) in flev25.formula

    rnoa25 = _at_period(smap, "rnoa", j25)
    spread25 = _at_period(smap, "spread", j25)
    roe25 = _at_period(smap, "roe_decomp", j25)
    assert rnoa25.cell in roe25.formula
    assert spread25.cell in roe25.formula
    assert flev25.cell in roe25.formula

    ni25 = _at_period(smap, "net_income_link", j25)
    actual25 = _at_period(smap, "actual_roe", j25)
    assert str(parse_cell_ref(ni25.cell)[0]) in actual25.formula
    assert str(parse_cell_ref(eq25.cell)[0]) in actual25.formula
    assert str(parse_cell_ref(eq24.cell)[0]) in actual25.formula


# --- Step 7 correction: period-axis integrity ---

def _descending_three_year_fin():
    from datetime import date
    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials

    d25, d24, d23 = date(2025, 12, 31), date(2024, 12, 31), date(2023, 12, 31)

    def li(label, v25, v24, v23, concept=""):
        return LineItem(
            label=label,
            values={d25: v25, d24: v24, d23: v23},
            concept=concept,
        )

    # Newest-to-oldest period list — the defect this correction targets.
    periods = [
        FinancialPeriod(end_date=d25, label="FY2025"),
        FinancialPeriod(end_date=d24, label="FY2024"),
        FinancialPeriod(end_date=d23, label="FY2023"),
    ]
    return StandardizedFinancials(
        ticker="REV",
        company_name="Reverse Chronology Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=periods,
        income_statement=[
            li("Revenue", 1300, 1200, 1000),
            li("Finance costs", -60, -50, -40),
            li("Finance income", 8, 6, 5),
            li("Profit before tax", 260, 220, 200),
            li("Income tax expense", -40, -33, -30),
            li("Profit for the year", 220, 187, 170),
        ],
        balance_sheet=[
            li("Cash and cash equivalents", 120, 110, 100),
            li("Trade receivables", 100, 90, 80),
            li("Property, plant and equipment", 440, 420, 400),
            li("Trade payables", 60, 55, 50),
            li("Bank borrowings", 220, 210, 200),
            li("Total equity", 380, 355, 330),
        ],
        cash_flow=[li("Net cash from operating activities", 70, 60, 50)],
    )


def test_descending_periods_build_chronological_model(tmp_path):
    from datetime import date
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.financial_math import compute_anchor
    from core.model.period_axis import canonical_fiscal_periods

    fin = _descending_three_year_fin()
    assert [p.end_date.year for p in fin.periods] == [2025, 2024, 2023]
    assert canonical_fiscal_periods(fin) == [
        date(2023, 12, 31),
        date(2024, 12, 31),
        date(2025, 12, 31),
    ]

    trainer, answer = build_training_workbook(fin, tmp_path / "Rev_Trainer.xlsx")
    smap = load_semantic_map(answer)
    assert [c.period_end for c in smap.all_ordered() if c.family_id == "revenue_link"] == [
        "2023-12-31",
        "2024-12-31",
        "2025-12-31",
    ]
    assert _at_period(smap, "revenue_link", 0).period_end == "2023-12-31"
    assert _at_period(smap, "revenue_link", 1).period_end == "2024-12-31"
    assert _at_period(smap, "revenue_link", 2).period_end == "2025-12-31"

    wb = load_workbook(answer, data_only=False)
    condensed = wb["Condensed Financials"]
    # Income-statement block date headers sit on the CONDENSED INCOME STATEMENT row.
    hdr = next(
        r for r in range(1, condensed.max_row + 1)
        if condensed.cell(row=r, column=1).value == "CONDENSED INCOME STATEMENT"
    )
    years = [condensed.cell(row=hdr, column=c).value.year for c in range(2, 5)]
    assert years == [2023, 2024, 2025]

    rev23 = _at_period(smap, "revenue_link", 0)
    rev24 = _at_period(smap, "revenue_link", 1)
    rev25 = _at_period(smap, "revenue_link", 2)
    growth24 = _at_period(smap, "sales_growth", 1)
    growth25 = _at_period(smap, "sales_growth", 2)
    assert rev24.cell in growth24.formula and rev23.cell in growth24.formula
    assert rev25.cell in growth25.formula and rev24.cell in growth25.formula

    nopat24 = _at_period(smap, "nopat_fy", 1)
    noa24 = _at_period(smap, "noa_agg", 1)
    noa23 = _at_period(smap, "noa_agg", 0)
    rnoa24 = _at_period(smap, "rnoa", 1)
    assert str(parse_cell_ref(nopat24.cell)[0]) in rnoa24.formula
    assert str(parse_cell_ref(noa24.cell)[0]) in rnoa24.formula
    assert str(parse_cell_ref(noa23.cell)[0]) in rnoa24.formula

    periods = canonical_fiscal_periods(fin)
    anchor = compute_anchor(fin, periods)
    assert growth24.expected_value == pytest.approx(anchor.dupont["Sales Growth"][1])
    assert rnoa24.expected_value == pytest.approx(anchor.dupont["RNOA"][1])
    assert growth24.expected_value == pytest.approx(1200 / 1000 - 1)
    wb.close()


def test_duplicate_fiscal_periods_rejected():
    from datetime import date
    from core.data.interface import FinancialPeriod
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.period_axis import PeriodAxisError

    fin = _descending_three_year_fin()
    d24 = date(2024, 12, 31)
    fin.periods = [
        FinancialPeriod(end_date=d24, label="FY2024a"),
        FinancialPeriod(end_date=d24, label="FY2024b"),
    ]
    with pytest.raises(PeriodAxisError, match="duplicate"):
        ReferenceModelBuilder(fin)


def test_gapped_annual_history_requires_contiguous_periods():
    from datetime import date
    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.period_axis import PeriodAxisError

    d21, d23 = date(2021, 12, 31), date(2023, 12, 31)

    def li(label, v21, v23):
        return LineItem(label=label, values={d21: v21, d23: v23})

    fin = StandardizedFinancials(
        ticker="GAP",
        company_name="Gapped Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=d21, label="FY2021"),
            FinancialPeriod(end_date=d23, label="FY2023"),
        ],
        income_statement=[
            li("Revenue", 1000, 1200),
            li("Finance costs", 0, 0),
            li("Finance income", 0, 0),
            li("Profit before tax", 200, 220),
            li("Income tax expense", -30, -33),
            li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            li("Cash and cash equivalents", 100, 110),
            li("Trade receivables", 80, 90),
            li("Property, plant and equipment", 400, 420),
            li("Trade payables", 50, 55),
            li("Bank borrowings", 200, 210),
            li("Total equity", 330, 355),
        ],
        cash_flow=[li("Net cash from operating activities", 50, 60)],
    )
    with pytest.raises(PeriodAxisError, match="contiguous"):
        ReferenceModelBuilder(fin)


def test_excel_descending_headers_build_chronological_model(tmp_path):
    from datetime import date
    from openpyxl import Workbook
    from core.data.interface import DocumentManifest, DocumentType, LineItem
    from core.ingestion.excel_import import ExcelExportAdapter

    path = tmp_path / "REV_Descending.xlsx"
    wb = Workbook()
    # Newest-to-oldest columns
    headers = ["Line Item", date(2025, 12, 31), date(2024, 12, 31), date(2023, 12, 31)]
    sheets = {
        "Income Statement": [
            ("Revenue", 1300, 1200, 1000),
            ("Finance costs", -60, -50, -40),
            ("Finance income", 8, 6, 5),
            ("Profit before tax", 260, 220, 200),
            ("Income tax expense", -40, -33, -30),
            ("Profit for the year", 220, 187, 170),
        ],
        "Balance Sheet": [
            ("Cash and cash equivalents", 120, 110, 100),
            ("Trade receivables", 100, 90, 80),
            ("Property, plant and equipment", 440, 420, 400),
            ("Trade payables", 60, 55, 50),
            ("Bank borrowings", 220, 210, 200),
            ("Total equity", 380, 355, 330),
        ],
        "Cash Flow Statement": [
            ("Net cash from operating activities", 70, 60, 50),
        ],
    }
    first = True
    for name, rows in sheets.items():
        ws = wb.active if first else wb.create_sheet(name)
        if first:
            ws.title = name
            first = False
        for c, h in enumerate(headers, start=1):
            ws.cell(1, c, value=h)
        for r, row in enumerate(rows, start=2):
            for c, val in enumerate(row, start=1):
                ws.cell(r, c, value=val)
    wb.save(path)
    wb.close()

    adapter = ExcelExportAdapter()
    fin = adapter.ingest(
        [DocumentManifest(path=str(path), doc_type=DocumentType.EXCEL_EXPORT)]
    )
    # Do not manually reorder — ingest preserves workbook column order.
    assert [p.end_date.year for p in fin.periods] == [2025, 2024, 2023]

    _, answer = build_training_workbook(fin, tmp_path / "ExcelRev_Trainer.xlsx")
    smap = load_semantic_map(answer)
    assert [c.period_end[:4] for c in smap.all_ordered() if c.family_id == "revenue_link"] == [
        "2023",
        "2024",
        "2025",
    ]
    growth24 = _at_period(smap, "sales_growth", 1)
    rev23 = _at_period(smap, "revenue_link", 0)
    rev24 = _at_period(smap, "revenue_link", 1)
    assert rev23.cell in growth24.formula and rev24.cell in growth24.formula
    growth25 = _at_period(smap, "sales_growth", 2)
    rev25 = _at_period(smap, "revenue_link", 2)
    assert rev24.cell in growth25.formula and rev25.cell in growth25.formula


def test_guided_classification_judgment_cases_and_suppressions():
    from datetime import date

    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.classification import reformulate_balance_sheet
    from core.model.judgment import (
        CLASSIFICATION_JUDGMENT_TEMPLATES,
        classification_judgment_cases,
    )
    from core.model.period_axis import canonical_fiscal_periods

    assert len(CLASSIFICATION_JUDGMENT_TEMPLATES) == 12
    assert len(set(CLASSIFICATION_JUDGMENT_TEMPLATES)) == 12
    for code, template in CLASSIFICATION_JUDGMENT_TEMPLATES.items():
        assert len(template.options) >= 2
        assert len(set(template.options)) == len(template.options)
        assert all(option in BALANCE_SHEET_CATEGORIES for option in template.options)
        assert template.options[0] in BALANCE_SHEET_CATEGORIES
        assert template.model_rationale
        assert template.model_consequence
        assert template.consequence_prompt
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)

    def li(label, v1, v2, concept=""):
        return LineItem(label=label, concept=concept, values={d1: v1, d2: v2})

    def make_fin(*, lease=50, rou=40, deferred=0, zero_lease=False, override=None):
        periods = [
            FinancialPeriod(end_date=d1, label="FY2024"),
            FinancialPeriod(end_date=d2, label="FY2025"),
        ]
        lease_vals = (0, 0) if zero_lease else (lease, lease + 10)
        fin = StandardizedFinancials(
            ticker="JDG",
            company_name="Judgment Co",
            currency="HKD",
            units="HKD mn",
            jurisdiction="HK",
            periods=periods,
            income_statement=[
                li("Revenue", 1000, 1100),
                li("Finance costs", 0, 0),
                li("Finance income", 0, 0),
                li("Profit before tax", 200, 220),
                li("Income tax expense", -30, -33),
                li("Profit for the year", 170, 187),
            ],
            balance_sheet=[
                li("Cash and cash equivalents", 100, 110),
                li("Trade receivables", 80, 90),
                li("Right-of-use assets", rou, rou + 5),
                li("Deferred tax assets", deferred, deferred),
                li("Property, plant and equipment", 400, 420),
                li("Trade payables", 50, 55),
                li(
                    "Operating lease liabilities",
                    lease_vals[0],
                    lease_vals[1],
                    concept="lease_liability",
                ),
                li("Bank borrowings", 200, 210),
                li("Total equity", 330, 355),
            ],
            cash_flow=[li("Net cash from operating activities", 50, 60)],
        )
        assumptions = {"classificationOverrides": override or {}}
        return fin, assumptions

    fin, _ = make_fin(deferred=25)
    periods = canonical_fiscal_periods(fin)
    reform = reformulate_balance_sheet(fin, periods)
    cases = classification_judgment_cases(fin, periods, reform)
    assert len(cases) == 1
    assert cases[0].label == "Operating lease liabilities"
    assert cases[0].supplied_treatment == "Operating Long-Term Liability"
    assert cases[0].alternatives == ("Financial Liability",)
    assert cases[0].id.startswith("classification::")
    assert "reference model" in cases[0].model_rationale.lower()
    assert cases[0].order == 1

    rou_idx = next(
        i
        for i in reform.detail_indices
        if fin.balance_sheet[i].label == "Right-of-use assets"
    )
    assert reform.decisions[rou_idx].ambiguous is True
    assert reform.decisions[rou_idx].judgment_code is None

    dta_idx = next(
        i
        for i in reform.detail_indices
        if fin.balance_sheet[i].label == "Deferred tax assets"
    )
    assert reform.decisions[dta_idx].ambiguous is True
    assert reform.decisions[dta_idx].judgment_code is None

    fin_zero, _ = make_fin(zero_lease=True)
    reform_zero = reformulate_balance_sheet(fin_zero, canonical_fiscal_periods(fin_zero))
    assert classification_judgment_cases(
        fin_zero, canonical_fiscal_periods(fin_zero), reform_zero
    ) == ()

    fin_ov, assumptions = make_fin(
        override={"label:Operating lease liabilities": "Financial Liability"}
    )
    reform_ov = reformulate_balance_sheet(
        fin_ov,
        canonical_fiscal_periods(fin_ov),
        overrides=assumptions["classificationOverrides"],
    )
    assert classification_judgment_cases(
        fin_ov, canonical_fiscal_periods(fin_ov), reform_ov
    ) == ()
    # Builder also suppresses when override is supplied (use balanced demo-scale path).
    demo = _ingest_demo()
    builder = ReferenceModelBuilder(
        demo,
        {
            "classificationOverrides": {
                "label:Operating lease liabilities": "Financial Liability",
            }
        },
    )
    assert builder.judgment_cases == ()


def test_judgment_cases_use_canonical_periods_not_interim_only_values():
    from datetime import date

    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.period_axis import canonical_fiscal_periods

    annual = date(2024, 12, 31)
    interim = date(2025, 6, 30)

    def li(label, annual_v, interim_v, concept=""):
        return LineItem(
            label=label,
            concept=concept,
            values={annual: annual_v, interim: interim_v},
        )

    fin = StandardizedFinancials(
        ticker="INT",
        company_name="Interim Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=annual, label="FY2024"),
            FinancialPeriod(end_date=interim, label="1H2025", is_interim=True),
        ],
        income_statement=[
            li("Revenue", 1000, 500),
            li("Finance costs", 0, 0),
            li("Finance income", 0, 0),
            li("Profit before tax", 200, 100),
            li("Income tax expense", -30, -15),
            li("Profit for the year", 170, 85),
        ],
        balance_sheet=[
            li("Cash and cash equivalents", 100, 110),
            li("Trade receivables", 80, 90),
            li("Property, plant and equipment", 400, 420),
            li("Trade payables", 50, 55),
            # Zero on the modeled annual axis; non-zero only on interim.
            li(
                "Operating lease liabilities",
                0,
                75,
                concept="lease_liability",
            ),
            li("Bank borrowings", 200, 210),
            li("Total equity", 330, 355),
        ],
        cash_flow=[li("Net cash from operating activities", 50, 60)],
    )
    modeled = canonical_fiscal_periods(fin)
    assert interim not in modeled
    assert annual in modeled
    builder = ReferenceModelBuilder(fin)
    assert builder.periods == modeled
    assert builder.judgment_cases == ()


def test_demo_has_one_lease_judgment_case_and_204_formula_components(tmp_path):
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.classification import check_reformulation_integrity
    from core.model.judgment import CLASSIFICATION_JUDGMENT_TEMPLATES

    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    assert len(CLASSIFICATION_JUDGMENT_TEMPLATES) == 12
    assert len(builder.judgment_cases) == 1
    case = builder.judgment_cases[0]
    assert case.label == "Operating lease liabilities"
    assert case.supplied_treatment == "Operating Long-Term Liability"
    assert case.alternatives == ("Financial Liability",)

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 312
    check_reformulation_integrity(builder.anchor.reformulation, builder.periods)


def test_demo_standardized_payload_round_trip_preserves_identity_and_values():
    from core.data.line_identity import line_identity
    from core.data.standardized_io import standardized_from_payload, standardized_to_payload

    data = _ingest_demo()
    payload = standardized_to_payload(data)
    restored = standardized_from_payload(payload)

    assert [p.end_date for p in restored.periods] == [p.end_date for p in data.periods]
    assert [p.is_interim for p in restored.periods] == [p.is_interim for p in data.periods]
    assert restored.ticker == data.ticker
    assert restored.stock_code == data.stock_code

    for name in ("income_statement", "balance_sheet", "cash_flow"):
        original_rows = getattr(data, name)
        restored_rows = getattr(restored, name)
        assert len(restored_rows) == len(original_rows)
        for left, right in zip(original_rows, restored_rows):
            assert line_identity(left) == line_identity(right)
            assert left.label == right.label
            assert (left.concept or "") == (right.concept or "")
            assert left.values == right.values

    blob = json.dumps(payload)
    assert "/Users/" not in blob
    assert "source_doc" not in blob
    assert "provenance" not in blob


def test_demo_check_context_binding_and_no_answer_leakage(tmp_path):
    from core.engine.reference_model import ReferenceModelBuilder
    from core.trainer.check_context import (
        CHECK_CONTEXT_MAGIC,
        CHECK_CONTEXT_SHEET,
        build_check_context,
        load_check_context,
    )

    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    assert len(builder.judgment_cases) == 1
    case = builder.judgment_cases[0]
    assert case.override_selector.startswith("identity:concept=lease_liability|")

    context = build_check_context(
        data, builder.periods, builder.assumptions, builder.judgment_cases
    )
    assert len(context.judgment_bindings) == 1
    binding = context.judgment_bindings[0]
    assert binding.worksheet_row == 5
    assert binding.override_selector.startswith("identity:concept=lease_liability|")
    assert binding.reference_treatment == "Operating Long-Term Liability"
    assert binding.allowed_treatments == (
        "Operating Long-Term Liability",
        "Financial Liability",
    )

    trainer_path, answer_key_path = _build_pair(tmp_path)
    loaded = load_check_context(answer_key_path)
    assert loaded is not None
    assert loaded.judgment_bindings[0].override_selector.startswith(
        "identity:concept=lease_liability|"
    )

    wb_a = load_workbook(answer_key_path, data_only=False)
    wb_t = load_workbook(trainer_path, data_only=False)
    assert CHECK_CONTEXT_SHEET in wb_a.sheetnames
    assert wb_a[CHECK_CONTEXT_SHEET].sheet_state == "hidden"
    assert wb_a[CHECK_CONTEXT_SHEET]["A1"].value == CHECK_CONTEXT_MAGIC
    assert CHECK_CONTEXT_SHEET not in wb_t.sheetnames

    chunks = []
    row = 2
    while True:
        value = wb_a[CHECK_CONTEXT_SHEET].cell(row=row, column=1).value
        if not value:
            break
        chunks.append(str(value))
        row += 1
    blob = "".join(chunks)
    assert case.model_rationale not in blob
    assert case.model_consequence not in blob

    smap = load_semantic_map(answer_key_path)
    for comp in smap.all_ordered():
        if comp.formula:
            assert comp.formula not in blob
        if comp.short_hint:
            assert comp.short_hint not in blob
        for hint in comp.hints:
            assert str(hint) not in blob
        # expected numeric values as bare strings may collide with source numbers;
        # ensure formula answers themselves are absent (checked above).
    wb_a.close()
    wb_t.close()


def test_judgment_selector_uses_identity_when_present():
    from core.engine.reference_model import ReferenceModelBuilder

    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    case = builder.judgment_cases[0]
    assert case.override_selector.startswith("identity:concept=lease_liability|")
    assert case.line_identity.startswith("concept=lease_liability|")


def test_live_classification_formula_helper_and_validation():
    from core.trainer.check_context import live_classification_formula

    formula = live_classification_formula(5, "Operating Long-Term Liability")
    assert "$F$5" in formula
    assert "$D$5" not in formula
    assert '"Operating Long-Term Liability"' in formula
    assert formula == (
        "=IF('Accounting Judgment'!$F$5=\"\","
        "\"Operating Long-Term Liability\","
        "'Accounting Judgment'!$F$5)"
    )
    with pytest.raises(ValueError):
        live_classification_formula(0, "Operating Long-Term Liability")
    with pytest.raises(ValueError):
        live_classification_formula(5, "")
    with pytest.raises(ValueError):
        live_classification_formula(5, "   ")
    # Escape embedded quotes for a future category edge case.
    quoted = live_classification_formula(6, 'Foo "Bar" Liability')
    assert '"Foo ""Bar"" Liability"' in quoted
    assert "$D$6" not in quoted


def test_live_classification_judgment_link_for_demo_lease(tmp_path):
    from core.engine.reference_model import JUDGMENT_SHEET, ReferenceModelBuilder
    from core.trainer.check_context import live_classification_formula

    trainer_path, answer_key_path = _build_pair(tmp_path)
    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    case = builder.judgment_cases[0]
    expected = live_classification_formula(5, "Operating Long-Term Liability")

    wb_a = load_workbook(answer_key_path, data_only=False)
    wb_t = load_workbook(trainer_path, data_only=False)
    ws_a = wb_a["Condensed Financials"]
    ws_t = wb_t["Condensed Financials"]

    lease_row = None
    bank_row = None
    for row in range(1, (ws_a.max_row or 1) + 1):
        label = ws_a.cell(row=row, column=1).value
        if label == "Operating lease liabilities":
            lease_row = row
        if label == "Bank borrowings":
            bank_row = row
    assert lease_row is not None and bank_row is not None

    lease_formula = ws_a.cell(lease_row, 2).value
    assert lease_formula == expected
    assert "$D$5" not in str(lease_formula)
    assert ws_t.cell(lease_row, 2).value == expected

    bank_val = ws_a.cell(bank_row, 2).value
    assert bank_val == "Financial Liability"
    assert not (isinstance(bank_val, str) and bank_val.startswith("="))

    category_dvs = [
        dv
        for dv in ws_a.data_validations.dataValidation
        if "Operating Working Capital Asset" in str(dv.formula1)
    ]
    assert category_dvs
    category_sqref = " ".join(str(dv.sqref) for dv in category_dvs)
    assert f"B{bank_row}" in category_sqref
    assert f"B{lease_row}" not in category_sqref

    smap = load_semantic_map(answer_key_path)
    practice_cells = {(c.tab, c.cell) for c in smap.all_ordered()}
    assert ("Condensed Financials", f"B{lease_row}") not in practice_cells

    def _rgb(cell):
        fill = cell.fill
        if fill is None or fill.fgColor is None or fill.fgColor.rgb is None:
            return ""
        rgb = fill.fgColor.rgb
        return rgb[-6:] if isinstance(rgb, str) else ""

    assert _rgb(ws_a.cell(lease_row, 2)) != "FFFF00"
    assert _rgb(ws_t.cell(lease_row, 2)) != "FFFF00"
    assert ws_a.cell(lease_row, 2).comment is None
    assert ws_t.cell(lease_row, 2).comment is None

    for wb in (wb_a, wb_t):
        formulas = [str(dv.formula1) for dv in wb[JUDGMENT_SHEET].data_validations.dataValidation]
        assert any(
            "Operating Long-Term Liability" in f and "Financial Liability" in f
            for f in formulas
        )
        assert any(f"F5" in str(dv.sqref) for dv in wb[JUDGMENT_SHEET].data_validations.dataValidation)

    assert case.supplied_treatment == "Operating Long-Term Liability"
    wb_a.close()
    wb_t.close()


def test_live_classification_two_case_judgment_links_without_collision(tmp_path):
    from datetime import date

    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import JUDGMENT_SHEET, ReferenceModelBuilder
    from core.trainer.workbook import TrainingWorkbookGenerator

    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)

    def li(label, v1, v2, concept=""):
        return LineItem(label=label, concept=concept, values={d1: v1, d2: v2})

    # Balanced mini company with two supported guided ambiguities.
    fin = StandardizedFinancials(
        ticker="TWO",
        company_name="Two Case Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=d1, label="FY2024"),
            FinancialPeriod(end_date=d2, label="FY2025"),
        ],
        income_statement=[
            li("Revenue", 1000, 1100),
            li("Finance costs", 0, 0),
            li("Finance income", 0, 0),
            li("Profit before tax", 200, 220),
            li("Income tax expense", -30, -33),
            li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            li("Cash and cash equivalents", 120, 130),
            li("Trade receivables", 80, 90),
            li("Property, plant and equipment", 530, 550),
            li("Total assets", 730, 770),
            li("Trade payables", 50, 55),
            li("Operating lease liabilities", 40, 45, concept="lease_liability"),
            li("Pension obligations", 30, 35),
            li("Bank borrowings", 200, 210),
            li("Total liabilities", 320, 345),
            li("Share capital and reserves", 410, 425),
            li("Total equity", 410, 425),
        ],
        cash_flow=[li("Net cash from operating activities", 50, 60)],
    )
    builder = ReferenceModelBuilder(fin)
    assert len(builder.judgment_cases) == 2
    answer = tmp_path / "Two_Answer_Key.xlsx"
    trainer = tmp_path / "Two_Trainer.xlsx"
    smap = builder.build(answer)
    TrainingWorkbookGenerator(answer, smap).generate(trainer)

    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    links = {}
    for row in range(1, (ws.max_row or 1) + 1):
        label = ws.cell(row=row, column=1).value
        val = ws.cell(row=row, column=2).value
        if label in {"Operating lease liabilities", "Pension obligations"}:
            assert isinstance(val, str) and val.startswith("=")
            if "F$5" in val or "F5" in val.replace("$", ""):
                links[label] = 5
            elif "F$6" in val or "F6" in val.replace("$", ""):
                links[label] = 6
    assert links["Operating lease liabilities"] != links["Pension obligations"]
    assert set(links.values()) == {5, 6}
    wb.close()


def test_historical_expected_covers_catalog_and_matches_reference_components(tmp_path):
    from core.model.earnings_quality import compute_earnings_quality_series
    from core.model.historical_expected import (
        expected_value_for_component,
        historical_expected_series,
    )
    from core.engine.reference_model import ReferenceModelBuilder

    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    series = historical_expected_series(builder.anchor)
    assert set(series) == {f.id for f in COMPONENT_CATALOG}
    quality = compute_earnings_quality_series(data, builder.periods, builder.anchor)

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 312
    for comp in smap.all_ordered():
        expected = expected_value_for_component(
            builder.anchor,
            comp,
            earnings_quality=quality,
            fixed_asset=builder.fixed_asset_series,
            lease_liability=builder.lease_liability_series,
        )
        if isinstance(expected, (int, float)) and isinstance(comp.expected_value, (int, float)):
            assert expected == pytest.approx(comp.expected_value)
        else:
            assert expected == comp.expected_value


def test_alternative_classification_changes_and_invariants():
    from core.model.classification import check_reformulation_integrity
    from core.model.historical_expected import historical_expected_series
    from core.model.period_axis import canonical_fiscal_periods

    data = _ingest_demo()
    periods = canonical_fiscal_periods(data)
    ref = compute_anchor(data, periods)
    alt = compute_anchor(
        data,
        periods,
        classification_overrides={"concept:lease_liability": "Financial Liability"},
    )
    check_reformulation_integrity(alt.reformulation, periods)

    ref_s = historical_expected_series(ref)
    alt_s = historical_expected_series(alt)

    for family in (
        "oltl_agg",
        "financial_liabilities_agg",
        "nola_agg",
        "noa_agg",
        "net_debt",
        "rnoa",
        "after_tax_cod",
        "spread",
        "flev",
    ):
        assert ref_s[family] != alt_s[family], family

    for family in (
        "equity_reformulated_fy",
        "roe_decomp",
        "actual_roe",
        "revenue_link",
        "net_income_link",
        "nopat_fy",
        "sales_growth",
        "nopat_margin",
    ):
        for a, b in zip(ref_s[family], alt_s[family]):
            if a is None and b is None:
                continue
            assert a == pytest.approx(b), family


def test_required_core_income_period_completeness(tmp_path):
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.line_resolver import MissingLineError
    from core.model.source_values import MissingHistoricalValueError

    concepts = (
        ("Revenue", "revenue"),
        ("Profit for the year", "net_income"),
        ("Profit before tax", "pretax_income"),
        ("Income tax expense", "tax_expense"),
        ("Finance costs", "interest_expense"),
        ("Finance income", "interest_income"),
    )
    for label, field in concepts:
        fin = _base_fin()
        # Drop CFO so quality is not the catching component for NI incompleteness.
        fin.cash_flow = [
            LineItem(
                label="Net cash from financing activities",
                values={fin.periods[0].end_date: -1, fin.periods[1].end_date: -1},
            )
        ]
        periods = [p.end_date for p in fin.periods]
        item = next(i for i in fin.income_statement if i.label == label)
        del item.values[periods[1]]
        with pytest.raises(MissingHistoricalValueError, match=field):
            compute_anchor(fin, periods)
        with pytest.raises(MissingHistoricalValueError, match=field):
            ReferenceModelBuilder(fin)
        with pytest.raises(ValueError):
            build_training_workbook(fin, tmp_path / f"Miss_{field}_Trainer.xlsx")

        fin_none = _base_fin()
        fin_none.cash_flow = [
            LineItem(
                label="Net cash from financing activities",
                values={
                    fin_none.periods[0].end_date: -1,
                    fin_none.periods[1].end_date: -1,
                },
            )
        ]
        item_none = next(i for i in fin_none.income_statement if i.label == label)
        item_none.values[periods[0]] = None
        with pytest.raises(MissingHistoricalValueError, match=field):
            compute_anchor(fin_none, periods)

    # Whole required line absent.
    is_no_inc = [
        _li("Revenue", 1000, 1100),
        _li("Finance costs", -40, -50),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    fin_absent = _base_fin(income_statement=is_no_inc)
    with pytest.raises(MissingLineError, match="interest_income"):
        ReferenceModelBuilder(fin_absent)
    with pytest.raises(MissingLineError, match="interest_income"):
        build_training_workbook(fin_absent, tmp_path / "AbsentInc_Trainer.xlsx")


def test_missing_net_income_fails_without_cfo_quality_module(tmp_path):
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.source_values import MissingHistoricalValueError

    fin = _base_fin()
    periods = [p.end_date for p in fin.periods]
    fin.cash_flow = [
        LineItem(
            label="Net cash from financing activities",
            values={periods[0]: -1, periods[1]: -1},
        )
    ]
    ni = next(i for i in fin.income_statement if i.label == "Profit for the year")
    del ni.values[periods[1]]
    with pytest.raises(MissingHistoricalValueError, match="net_income"):
        compute_anchor(fin, periods)
    with pytest.raises(MissingHistoricalValueError, match="net_income"):
        ReferenceModelBuilder(fin)
    with pytest.raises(ValueError):
        build_training_workbook(fin, tmp_path / "NoCFO_MissNI_Trainer.xlsx")


def test_missing_bs_detail_fails_without_reported_totals(tmp_path):
    from core.data.interface import FinancialPeriod, StandardizedFinancials
    from core.model.source_values import MissingHistoricalValueError

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    cash = _li("Cash and cash equivalents", 100, 110)
    del cash.values[p2]
    fin = StandardizedFinancials(
        ticker="DET",
        company_name="Detail Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            cash,
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            # No Total Assets / Liabilities / Equity rows.
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    with pytest.raises(MissingHistoricalValueError, match="balance_sheet detail"):
        build_training_workbook(fin, tmp_path / "MissDetail_Trainer.xlsx")


def test_dupont_undefined_ratio_semantics_and_propagation():
    from core.model.ratio_values import UNDEFINED_RATIO

    # Zero prior revenue -> sales growth #N/A; zero current with nonzero prior -> -1.0
    fin = _base_fin()
    periods = [p.end_date for p in fin.periods]
    rev = next(i for i in fin.income_statement if i.label == "Revenue")
    rev.values[periods[0]] = 0.0
    anchor = compute_anchor(fin, periods)
    assert anchor.dupont["Sales Growth"][0] is None
    assert anchor.dupont["Sales Growth"][1] == UNDEFINED_RATIO

    fin2 = _base_fin()
    rev2 = next(i for i in fin2.income_statement if i.label == "Revenue")
    rev2.values[periods[1]] = 0.0
    anchor2 = compute_anchor(fin2, periods)
    assert anchor2.dupont["Sales Growth"][1] == pytest.approx(-1.0)

    # Zero revenue -> NOPAT Margin #N/A; zero NOPAT with nonzero revenue -> 0.0
    fin3 = _base_fin()
    rev3 = next(i for i in fin3.income_statement if i.label == "Revenue")
    rev3.values[periods[0]] = 0.0
    # Keep NIAT/NOPAT well-defined via complete IS.
    anchor3 = compute_anchor(fin3, periods)
    assert anchor3.dupont["NOPAT Margin"][0] == UNDEFINED_RATIO

    fin4 = _base_fin()
    # Force NOPAT=0 by setting NI = -NIAT via explicit NI mutation after we know NIAT.
    # Simpler: set NI and interest so NI + NIAT = 0 with nonzero revenue.
    # NI=170, interest exp=-40, inc=5 -> net_int=35, etr≈0.15, niat≈29.75, nopat≈199.75
    # Set NI to -niat by iterating: set Profit for year to cancel.
    # Use post-compute approach: mutate historical path inputs so nopat is 0.
    # pretax=200, tax=-30 -> etr=0.15; net_int = -(-40+5)=35; niat=35*0.85=29.75
    # nopat = ni + niat = 0 => ni = -29.75
    ni4 = next(i for i in fin4.income_statement if i.label == "Profit for the year")
    ni4.values[periods[0]] = -29.75
    anchor4 = compute_anchor(fin4, periods)
    assert anchor4.historical.nopat[0] == pytest.approx(0.0)
    assert anchor4.dupont["NOPAT Margin"][0] == pytest.approx(0.0)

    # Zero average Net Debt -> CoD #N/A; Spread/decomposed propagate; Actual ROE may remain numeric
    from core.data.interface import FinancialPeriod, StandardizedFinancials

    p1, p2 = periods
    fin_nd = StandardizedFinancials(
        ticker="ND0",
        company_name="Zero ND Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 200, 210),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", 430, 455),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    anchor_nd = compute_anchor(fin_nd, periods)
    assert anchor_nd.reformulation.net_debt == (0.0, 0.0)
    assert anchor_nd.dupont["After-tax CoD"][1] == UNDEFINED_RATIO
    assert anchor_nd.dupont["Spread"][1] == UNDEFINED_RATIO
    assert anchor_nd.dupont["ROE (decomposed)"][1] == UNDEFINED_RATIO
    assert isinstance(anchor_nd.dupont["Actual ROE"][1], float)

    # Zero average Equity -> FLEV / Actual ROE #N/A
    fin_eq = StandardizedFinancials(
        ticker="EQ0",
        company_name="Zero Equity Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            # NOA = ND => implied equity 0
            _li("Cash and cash equivalents", 100, 110),
            _li("Trade receivables", 50, 55),
            _li("Property, plant and equipment", 150, 155),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 250, 265),
            _li("Total equity", 0, 0),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    anchor_eq = compute_anchor(fin_eq, periods)
    assert anchor_eq.reformulation.implied_equity == (0.0, 0.0)
    assert anchor_eq.dupont["FLEV"][1] == UNDEFINED_RATIO
    assert anchor_eq.dupont["Actual ROE"][1] == UNDEFINED_RATIO
    assert anchor_eq.dupont["ROE (decomposed)"][1] == UNDEFINED_RATIO

    # Zero average NOA -> RNOA #N/A propagates to Spread / decomposed ROE
    fin_noa = StandardizedFinancials(
        ticker="NOA0",
        company_name="Zero NOA Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
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
            _li("Trade receivables", 50, 55),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", -100, -100),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    anchor_noa = compute_anchor(fin_noa, periods)
    assert anchor_noa.reformulation.noa == (0.0, 0.0)
    assert anchor_noa.dupont["RNOA"][1] == UNDEFINED_RATIO
    assert anchor_noa.dupont["Spread"][1] == UNDEFINED_RATIO
    assert anchor_noa.dupont["ROE (decomposed)"][1] == UNDEFINED_RATIO


def test_dupont_na_formulas_and_check_accept_undefined(tmp_path):
    from core.model.ratio_values import UNDEFINED_RATIO
    from core.tests.test_normalization import _inject_formula_and_cached_value
    from core.trainer.checker import check_workbook
    from core.trainer.semantic_io import parse_cell_ref

    # Demo formulas use NA() guards
    data = _ingest_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "DupontNA_Trainer.xlsx")
    smap = load_semantic_map(answer)
    for family_id in (
        "sales_growth",
        "nopat_margin",
        "rnoa",
        "after_tax_cod",
        "flev",
        "actual_roe",
    ):
        comp = next(c for c in smap.all_ordered() if c.family_id == family_id)
        assert "NA()" in comp.formula
        assert ",0," not in comp.formula.replace("NA()", "")
    # Spread / decomposed keep direct formulas (Excel propagates #N/A)
    spread = next(c for c in smap.all_ordered() if c.family_id == "spread")
    assert "NA()" not in spread.formula
    assert "IFERROR" not in spread.formula.upper()

    # Stale optional-interest hint removed
    ni_hint = next(f for f in COMPONENT_CATALOG if f.id == "net_interest_fy")
    assert all("Missing optional interest" not in h for h in ni_hint.hints)
    assert any("explicitly supplied" in h for h in ni_hint.hints)

    # Undefined After-tax CoD fixture: exact / equivalent #N/A green; fabricated 0 red
    from core.data.interface import FinancialPeriod, StandardizedFinancials

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="COD0",
        company_name="Zero CoD Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 200, 210),
            _li("Trade receivables", 80, 90),
            _li("Property, plant and equipment", 400, 420),
            _li("Trade payables", 50, 55),
            _li("Bank borrowings", 200, 210),
            _li("Total equity", 430, 455),
        ],
        cash_flow=[_li("Net cash from operating activities", 50, 60)],
    )
    trainer2, answer2 = build_training_workbook(fin, tmp_path / "ZeroCOD_Trainer.xlsx")
    smap2 = load_semantic_map(answer2)
    comp = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "after_tax_cod" and c.period_index == 1
    )
    assert comp.expected_value == UNDEFINED_RATIO
    assert "NA()" in comp.formula

    wb = load_workbook(trainer2, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer2)
    wb.close()
    assert check_workbook(trainer2).correct == 1

    _inject_formula_and_cached_value(
        trainer2,
        comp.tab,
        comp.cell,
        formula="=NA()",
        cached_value=UNDEFINED_RATIO,
    )
    assert check_workbook(trainer2).correct == 1

    _inject_formula_and_cached_value(
        trainer2,
        comp.tab,
        comp.cell,
        formula="=0",
        cached_value=0.0,
    )
    assert check_workbook(trainer2).incorrect == 1


def test_effective_tax_rate_undefined_when_pretax_zero():
    from core.model.ratio_values import UNDEFINED_RATIO

    fin = _base_fin()
    periods = [p.end_date for p in fin.periods]
    pretax = next(i for i in fin.income_statement if i.label == "Profit before tax")
    tax = next(i for i in fin.income_statement if i.label == "Income tax expense")

    pretax.values[periods[0]] = 0.0
    tax.values[periods[0]] = 0.0
    anchor = compute_anchor(fin, periods)
    assert anchor.historical.effective_tax_rate[0] == UNDEFINED_RATIO

    pretax.values[periods[0]] = 0.0
    tax.values[periods[0]] = -30.0
    anchor2 = compute_anchor(fin, periods)
    assert anchor2.historical.effective_tax_rate[0] == UNDEFINED_RATIO

    pretax.values[periods[0]] = 200.0
    tax.values[periods[0]] = 0.0
    anchor3 = compute_anchor(fin, periods)
    assert anchor3.historical.effective_tax_rate[0] == pytest.approx(0.0)

    pretax.values[periods[0]] = 200.0
    tax.values[periods[0]] = -30.0
    anchor4 = compute_anchor(fin, periods)
    assert anchor4.historical.effective_tax_rate[0] == pytest.approx(0.15)


def test_undefined_etr_niat_nopat_short_circuit_and_propagation():
    from core.data.interface import StandardizedFinancials
    from core.model.ratio_values import UNDEFINED_RATIO

    periods = [p.end_date for p in _synth_periods()]

    # Zero pretax + zero net interest -> ETR #N/A, NIAT 0, numeric NOPAT
    fin_zero_ni = StandardizedFinancials(
        ticker="ETR0",
        company_name="Zero Pretax Zero NI",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_synth_periods(),
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", 0, 0),
            _li("Finance income", 0, 0),
            _li("Profit before tax", 0, 220),
            _li("Income tax expense", 0, -33),
            _li("Profit for the year", 100, 187),
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
    anchor_z = compute_anchor(fin_zero_ni, periods)
    assert anchor_z.historical.effective_tax_rate[0] == UNDEFINED_RATIO
    assert anchor_z.historical.net_interest[0] == pytest.approx(0.0)
    assert anchor_z.historical.net_interest_after_tax[0] == pytest.approx(0.0)
    assert anchor_z.historical.nopat[0] == pytest.approx(100.0)

    # Zero pretax in comparable year + nonzero net interest -> NIAT/NOPAT #N/A;
    # DuPont NOPAT metrics #N/A; Actual ROE may remain numeric.
    fin_ni = StandardizedFinancials(
        ticker="ETR1",
        company_name="Zero Pretax Nonzero NI",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_synth_periods(),
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 200, 0),
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
    anchor = compute_anchor(fin_ni, periods)
    assert anchor.historical.effective_tax_rate[1] == UNDEFINED_RATIO
    assert abs(anchor.historical.net_interest[1]) > 0
    assert anchor.historical.net_interest_after_tax[1] == UNDEFINED_RATIO
    assert anchor.historical.nopat[1] == UNDEFINED_RATIO
    assert anchor.dupont["NOPAT Margin"][1] == UNDEFINED_RATIO
    assert anchor.dupont["RNOA"][1] == UNDEFINED_RATIO
    assert isinstance(anchor.dupont["Actual ROE"][1], float)
    assert isinstance(anchor.historical.effective_tax_rate[0], float)
    assert isinstance(anchor.historical.nopat[0], float)


def test_condensed_etr_niat_formulas_and_check_na(tmp_path):
    from core.data.interface import FinancialPeriod, StandardizedFinancials
    from core.model.ratio_values import UNDEFINED_RATIO
    from core.tests.test_normalization import _inject_formula_and_cached_value
    from core.trainer.checker import check_workbook
    from core.trainer.semantic_io import parse_cell_ref

    data = _ingest_demo()
    _, answer = build_training_workbook(data, tmp_path / "EtrFormula_Trainer.xlsx")
    smap = load_semantic_map(answer)
    etr = next(c for c in smap.all_ordered() if c.family_id == "effective_tax_rate_fy")
    assert "NA()" in etr.formula
    assert ",0," not in etr.formula.replace("NA()", "")
    niat = next(c for c in smap.all_ordered() if c.family_id == "net_interest_after_tax_fy")
    assert "ISNA(" in niat.formula.upper() or "ISNA(" in niat.formula
    assert niat.formula.count("IF(") >= 2
    nopat = next(c for c in smap.all_ordered() if c.family_id == "nopat_fy")
    assert "NA()" not in nopat.formula
    assert "+" in nopat.formula
    # No absent-interest =0 fallback on Condensed net-interest chain
    for family_id in ("net_interest_fy", "net_interest_after_tax_fy", "effective_tax_rate_fy"):
        for comp in (c for c in smap.all_ordered() if c.family_id == family_id):
            assert comp.formula != "=0"

    etr_hint = next(f for f in COMPONENT_CATALOG if f.id == "effective_tax_rate_fy")
    assert any("#N/A" in h for h in etr_hint.hints)
    niat_hint = next(f for f in COMPONENT_CATALOG if f.id == "net_interest_after_tax_fy")
    assert any("zero Net Interest" in h for h in niat_hint.hints)
    nopat_hint = next(f for f in COMPONENT_CATALOG if f.id == "nopat_fy")
    assert any("propagates to NOPAT" in h for h in nopat_hint.hints)

    p1, p2 = date(2024, 12, 31), date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="ETRCK",
        company_name="ETR Check Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=p1, label="FY2024"),
            FinancialPeriod(end_date=p2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -40, -50),
            _li("Finance income", 5, 6),
            _li("Profit before tax", 0, 220),
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
    trainer, answer2 = build_training_workbook(fin, tmp_path / "EtrCheck_Trainer.xlsx")
    smap2 = load_semantic_map(answer2)
    etr0 = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "effective_tax_rate_fy" and c.period_index == 0
    )
    niat0 = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "net_interest_after_tax_fy" and c.period_index == 0
    )
    nopat0 = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "nopat_fy" and c.period_index == 0
    )
    assert etr0.expected_value == UNDEFINED_RATIO
    assert niat0.expected_value == UNDEFINED_RATIO
    assert nopat0.expected_value == UNDEFINED_RATIO
    assert "NA()" in etr0.formula

    for comp in (etr0, niat0, nopat0):
        wb = load_workbook(trainer, data_only=False)
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
        wb.save(trainer)
        wb.close()
        assert check_workbook(trainer).correct >= 1

        _inject_formula_and_cached_value(
            trainer,
            comp.tab,
            comp.cell,
            formula="=NA()",
            cached_value=UNDEFINED_RATIO,
        )
        assert check_workbook(trainer).correct >= 1

        _inject_formula_and_cached_value(
            trainer,
            comp.tab,
            comp.cell,
            formula="=0",
            cached_value=0.0,
        )
        assert check_workbook(trainer).incorrect >= 1


def test_generic_financial_judgment_cases_reach_reference_builder():
    from core.data.interface import StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder

    periods = _synth_periods()
    fin = StandardizedFinancials(
        ticker="GFIN",
        company_name="Generic Financial Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=periods,
        income_statement=[
            _li("Revenue", 100, 110),
            _li("Finance costs", -4, -5),
            _li("Finance income", 1, 1),
            _li("Profit before tax", 20, 22),
            _li("Income tax expense", -3, -3),
            _li("Profit for the year", 17, 19),
        ],
        balance_sheet=[
            _li(
                "Other financial assets",
                10,
                11,
                concept="other_financial_assets_current",
            ),
            _li(
                "Financial assets",
                20,
                21,
                concept="financial_assets_noncurrent",
            ),
            _li(
                "Other financial liabilities",
                5,
                6,
                concept="other_financial_liabilities_current",
            ),
            _li(
                "Financial liabilities",
                7,
                8,
                concept="financial_liabilities_noncurrent",
            ),
            _li(
                "Share capital and reserves",
                18,
                18,
                concept="retained_earnings",
            ),
        ],
        cash_flow=[],
    )
    builder = ReferenceModelBuilder(fin)
    by_label = {case.label: case for case in builder.judgment_cases}
    assert set(by_label) == {
        "Other financial assets",
        "Financial assets",
        "Other financial liabilities",
        "Financial liabilities",
    }
    assert by_label["Other financial assets"].supplied_treatment == "Financial Asset"
    assert by_label["Other financial assets"].alternatives == (
        "Operating Working Capital Asset",
    )
    assert by_label["Financial assets"].supplied_treatment == "Financial Asset"
    assert by_label["Financial assets"].alternatives == ("Operating Long-Term Asset",)
    assert by_label["Other financial liabilities"].supplied_treatment == (
        "Financial Liability"
    )
    assert by_label["Other financial liabilities"].alternatives == (
        "Operating Working Capital Liability",
    )
    assert by_label["Financial liabilities"].supplied_treatment == "Financial Liability"
    assert by_label["Financial liabilities"].alternatives == (
        "Operating Long-Term Liability",
    )


def test_other_balance_judgment_cases_reach_reference_builder():
    from core.data.interface import StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder

    periods = _synth_periods()
    fin = StandardizedFinancials(
        ticker="OTHER",
        company_name="Other Balance Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=periods,
        income_statement=[
            _li("Revenue", 100, 110),
            _li("Finance costs", -4, -5),
            _li("Finance income", 1, 1),
            _li("Profit before tax", 20, 22),
            _li("Income tax expense", -3, -3),
            _li("Profit for the year", 17, 19),
        ],
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
    builder = ReferenceModelBuilder(fin)
    by_code = {case.id.split("::", 1)[-1]: case for case in builder.judgment_cases}
    # Prefer lookup by supplied treatment + label
    by_label = {case.label: case for case in builder.judgment_cases}
    assert set(by_label) == {
        "Other current assets",
        "Other non-current assets",
        "Other current liabilities",
        "Other non-current liabilities",
    }
    assert by_label["Other current assets"].supplied_treatment == (
        "Operating Working Capital Asset"
    )
    assert by_label["Other current assets"].alternatives == ("Financial Asset",)
    assert by_label["Other non-current assets"].supplied_treatment == (
        "Operating Long-Term Asset"
    )
    assert by_label["Other non-current assets"].alternatives == ("Financial Asset",)
    assert by_label["Other current liabilities"].supplied_treatment == (
        "Operating Working Capital Liability"
    )
    assert by_label["Other current liabilities"].alternatives == ("Financial Liability",)
    assert by_label["Other non-current liabilities"].supplied_treatment == (
        "Operating Long-Term Liability"
    )
    assert by_label["Other non-current liabilities"].alternatives == (
        "Financial Liability",
    )

# --- Step 9M.2.4.1.1.1: pretax/ETR coverage matrix + workbook period identity ---

_IS_SOURCE_REF = re.compile(
    r"^=(?:'Income Statement'|\"Income Statement\")!\$?([A-Z]+)\$?(\d+)$",
    re.IGNORECASE,
)
# Strict local contract matching emitted Condensed ETR arithmetic (not a substring check).
_ETR_FORMULA_CONTRACT = re.compile(
    r"^=IF\(([A-Z]+)(\d+)=0,NA\(\),-\1(\d+)/\1\2\)$"
)

_PRETAX_PERIODS = (date(2024, 12, 31), date(2025, 12, 31))
_DEFAULT_PRETAX_LABEL = "Income before income tax expense"
_DEFAULT_TAX_LABEL = "Income tax expense"
_CANON_PRETAX_LABEL = "Carrying pretax amount"


@dataclass(frozen=True)
class _PretaxEtrExpect:
    """Fixture-owned independent expectations — never derived via production helpers."""

    pretax_label: str
    tax_label: str
    period_ends: tuple[date, date]
    pretax_values: tuple[float, float]
    tax_values: tuple[float, float]
    etr_values: tuple[object, object]
    pretax_concept: str


def _independent_etr(tax: float, pretax: float):
    """Test-local ETR arithmetic (zero-denominator → #N/A); not ratio_or_na."""
    if pretax == 0.0:
        return "#N/A"
    return -tax / pretax


def _make_expect(
    *,
    pretax_label: str = _DEFAULT_PRETAX_LABEL,
    tax_label: str = _DEFAULT_TAX_LABEL,
    pretax_values: tuple[float, float] = (400.0, 500.0),
    tax_values: tuple[float, float] = (-60.0, -80.0),
    pretax_concept: str = "income_before_tax",
) -> _PretaxEtrExpect:
    etr_values = (
        _independent_etr(tax_values[0], pretax_values[0]),
        _independent_etr(tax_values[1], pretax_values[1]),
    )
    return _PretaxEtrExpect(
        pretax_label=pretax_label,
        tax_label=tax_label,
        period_ends=_PRETAX_PERIODS,
        pretax_values=pretax_values,
        tax_values=tax_values,
        etr_values=etr_values,
        pretax_concept=pretax_concept,
    )


# Alias fixture: 400/500 pretax, −60/−80 tax, 0.15/0.16 ETR.
_ALIAS_EXPECT = _make_expect()
assert _ALIAS_EXPECT.etr_values == (0.15, 0.16)
_DEFAULT_EXPECT = _ALIAS_EXPECT  # retained name for corruption / zero / alias-removal tests

_CANON_EXPECT = _make_expect(
    pretax_label=_CANON_PRETAX_LABEL,
    pretax_values=(250.0, 310.0),
    tax_values=(-40.0, -55.0),
    pretax_concept="pretax_income",
)
_LABEL_EXPECT = _make_expect(
    pretax_values=(180.0, 210.0),
    tax_values=(-27.0, -42.0),
    pretax_concept="",
)


def _pretax_parity_fin(
    expect: _PretaxEtrExpect,
    *,
    reorder: bool = False,
):
    """Synthetic IS fixture owned by expect; separate from Lululemon."""
    pretax = _li(
        expect.pretax_label,
        expect.pretax_values[0],
        expect.pretax_values[1],
        concept=expect.pretax_concept,
    )
    tax = _li(expect.tax_label, expect.tax_values[0], expect.tax_values[1])
    revenue = _li("Revenue", 1000, 1100)
    ie = _li("Finance costs", -40, -50)
    ii = _li("Finance income", 5, 6)
    ni = _li("Profit for the year", 340, 420)
    filler = _li("Other income", 1, 2)
    if reorder:
        # Pretax after tax and filler so row-index arithmetic alone cannot pass.
        is_items = [revenue, ie, ii, tax, filler, pretax, ni]
    else:
        is_items = [revenue, ie, ii, pretax, tax, ni]
    return _base_fin(income_statement=is_items)


def _assert_fixture_owned_is_rows(fin, expect: _PretaxEtrExpect, *, reorder: bool):
    """Verify labels, concepts, period identities, amounts, and row ordering on the fixture."""
    periods = list(expect.period_ends)
    assert [p.end_date for p in fin.periods] == periods
    pretax_idxs = [
        i for i, item in enumerate(fin.income_statement) if item.label == expect.pretax_label
    ]
    tax_idxs = [
        i for i, item in enumerate(fin.income_statement) if item.label == expect.tax_label
    ]
    assert len(pretax_idxs) == 1 and len(tax_idxs) == 1
    pretax = fin.income_statement[pretax_idxs[0]]
    tax = fin.income_statement[tax_idxs[0]]
    assert pretax.concept == expect.pretax_concept
    assert tax.label == expect.tax_label
    assert pretax.values == {
        periods[0]: expect.pretax_values[0],
        periods[1]: expect.pretax_values[1],
    }
    assert tax.values == {
        periods[0]: expect.tax_values[0],
        periods[1]: expect.tax_values[1],
    }
    if reorder:
        assert pretax_idxs[0] > tax_idxs[0]
    else:
        assert pretax_idxs[0] < tax_idxs[0]


def _condensed_row(ws, label: str) -> int:
    for row in range(1, (ws.max_row or 1) + 1):
        if ws.cell(row=row, column=1).value == label:
            return row
    raise AssertionError(f"missing condensed label {label!r}")


def _col_letter(col: int) -> str:
    return chr(ord("A") + col - 1)


def _as_period_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise AssertionError(f"expected period date/datetime header, got {value!r}")


def _find_row_by_a_value(ws, expected: str) -> int:
    for row in range(1, (ws.max_row or 1) + 1):
        if ws.cell(row=row, column=1).value == expected:
            return row
    raise AssertionError(f"missing row with A={expected!r}")


def _period_headers_from_row(ws, header_row: int, n_periods: int, start_col: int = 2):
    headers = []
    for j in range(n_periods):
        raw = ws.cell(row=header_row, column=start_col + j).value
        headers.append(_as_period_date(raw))
    trailing = ws.cell(row=header_row, column=start_col + n_periods).value
    if trailing not in (None, "Notes"):
        # Allow Notes only for balance-sheet-style headers; condensed IS has None.
        raise AssertionError(
            f"unexpected trailing period header at col {start_col + n_periods}: {trailing!r}"
        )
    return headers


def _income_statement_period_headers(wb, n_periods: int):
    ws = wb["Income Statement"]
    header_row = _find_row_by_a_value(ws, "Line Item")
    return header_row, _period_headers_from_row(ws, header_row, n_periods, start_col=2)


def _condensed_income_period_headers(wb, n_periods: int):
    ws = wb["Condensed Financials"]
    header_row = _find_row_by_a_value(ws, "CONDENSED INCOME STATEMENT")
    return header_row, _period_headers_from_row(ws, header_row, n_periods, start_col=2)


def _resolve_is_formula_to_source(wb, formula: str):
    match = _IS_SOURCE_REF.fullmatch(str(formula).strip())
    if match is None:
        raise AssertionError(f"expected Income Statement source link, got {formula!r}")
    col_letter, row_s = match.group(1).upper(), int(match.group(2))
    src = wb["Income Statement"]
    col = 0
    for i, ch in enumerate(reversed(col_letter)):
        col += (ord(ch) - 64) * (26**i)
    label = src.cell(row=row_s, column=1).value
    value = src.cell(row=row_s, column=col).value
    return label, value, row_s, col


def _expected_etr_formula(col_letter: str, pretax_row: int, tax_row: int) -> str:
    return f"=IF({col_letter}{pretax_row}=0,NA(),-{col_letter}{tax_row}/{col_letter}{pretax_row})"


def _assert_etr_formula_contract(formula: object, col_letter: str, pretax_row: int, tax_row: int):
    expected = _expected_etr_formula(col_letter, pretax_row, tax_row)
    if formula != expected:
        raise AssertionError(
            f"etr formula contract mismatch: got {formula!r}, expected {expected!r}"
        )
    match = _ETR_FORMULA_CONTRACT.fullmatch(str(formula))
    if match is None:
        raise AssertionError(f"etr formula failed local contract regex: {formula!r}")
    if match.group(1) != col_letter:
        raise AssertionError(f"etr formula column mismatch: {formula!r}")
    if int(match.group(2)) != pretax_row or int(match.group(3)) != tax_row:
        raise AssertionError(
            f"etr formula row refs mismatch: {formula!r} "
            f"(pretax={pretax_row}, tax={tax_row})"
        )


def _values_close(got, exp) -> bool:
    if isinstance(exp, float):
        return isinstance(got, (int, float)) and abs(float(got) - exp) < 1e-9
    return got == exp


def _assert_python_pretax_etr(fin, expect: _PretaxEtrExpect):
    """Check compute_anchor against fixture-owned pretax/ETR expectations only."""
    periods = list(expect.period_ends)
    assert [p.end_date for p in fin.periods] == periods
    anchor = compute_anchor(fin, periods)
    for j, exp in enumerate(expect.pretax_values):
        got = anchor.historical.pretax_income[j]
        if not _values_close(got, exp):
            raise AssertionError(
                f"python pretax mismatch period {j}: got {got!r}, expected {exp!r}"
            )
    for j, exp in enumerate(expect.etr_values):
        got = anchor.historical.effective_tax_rate[j]
        if not _values_close(got, exp):
            raise AssertionError(
                f"python etr mismatch period {j}: got {got!r}, expected {exp!r}"
            )
    return anchor


def _build_pretax_answer_key(fin, tmp_path, stem: str) -> Path:
    """Construct Trainer/Answer-Key pair; return Answer-Key path (no validation)."""
    trainer, answer = build_training_workbook(fin, tmp_path / f"{stem}_Trainer.xlsx")
    assert trainer.exists() and answer.exists()
    return answer


def _assert_workbook_period_headers(wb, expect: _PretaxEtrExpect):
    """Check actual saved/reloaded period headers (count, order, identity) on both sheets."""
    n = len(expect.period_ends)
    expected = list(expect.period_ends)
    is_row, is_headers = _income_statement_period_headers(wb, n)
    cond_row, cond_headers = _condensed_income_period_headers(wb, n)
    if len(is_headers) != n:
        raise AssertionError(
            f"Income Statement period header count mismatch: got {len(is_headers)}, expected {n}"
        )
    if len(cond_headers) != n:
        raise AssertionError(
            f"Condensed Financials period header count mismatch: "
            f"got {len(cond_headers)}, expected {n}"
        )
    if is_headers != expected:
        raise AssertionError(
            f"Income Statement period header identity mismatch: "
            f"got {is_headers!r}, expected {expected!r}"
        )
    if cond_headers != expected:
        raise AssertionError(
            f"Condensed Financials period header identity mismatch: "
            f"got {cond_headers!r}, expected {expected!r}"
        )
    return is_row, is_headers, cond_row, cond_headers


def _validate_pretax_etr_parity(answer_path: Path, expect: _PretaxEtrExpect, anchor=None):
    """
    Validate a saved/reloaded Answer Key against independent expectations.

    Inspects formulas, period headers, and evaluates referenced source cells;
    does not Excel-recalculate.
    """
    wb = load_workbook(answer_path, data_only=False)
    try:
        condensed = wb["Condensed Financials"]
        is_ws = wb["Income Statement"]
        pretax_row = _condensed_row(condensed, "Pretax Income")
        tax_row = _condensed_row(condensed, "Tax Expense")
        etr_row = _condensed_row(condensed, "Effective Tax Rate")
        if pretax_row == tax_row:
            raise AssertionError("pretax and tax condensed rows must differ")

        is_header_row, is_headers, cond_header_row, cond_headers = (
            _assert_workbook_period_headers(wb, expect)
        )

        for j, period in enumerate(expect.period_ends):
            col = 2 + j
            col_letter = _col_letter(col)
            pretax_f = condensed.cell(row=pretax_row, column=col).value
            tax_f = condensed.cell(row=tax_row, column=col).value
            etr_f = condensed.cell(row=etr_row, column=col).value

            # Bind condensed column (including ETR) to independently expected period header.
            if cond_headers[j] != period:
                raise AssertionError(
                    f"condensed period identity mismatch period {j}: "
                    f"header {cond_headers[j]!r} != expected {period!r}"
                )
            cond_raw = condensed.cell(row=cond_header_row, column=col).value
            if _as_period_date(cond_raw) != period:
                raise AssertionError(
                    f"condensed period header representation mismatch period {j}: "
                    f"got {cond_raw!r}, expected identity {period!r}"
                )

            pretax_label, pretax_src_val, pretax_src_row, pretax_src_col = (
                _resolve_is_formula_to_source(wb, pretax_f)
            )
            tax_label, tax_src_val, tax_src_row, tax_src_col = _resolve_is_formula_to_source(
                wb, tax_f
            )

            if pretax_label != expect.pretax_label:
                raise AssertionError(
                    f"pretax source label mismatch period {j}: "
                    f"got {pretax_label!r}, expected {expect.pretax_label!r}"
                )
            if tax_label != expect.tax_label:
                raise AssertionError(
                    f"tax source label mismatch period {j}: "
                    f"got {tax_label!r}, expected {expect.tax_label!r}"
                )
            if pretax_label == tax_label:
                raise AssertionError("pretax and tax source labels must differ")
            if pretax_src_row == tax_src_row:
                raise AssertionError("pretax link redirected to tax source row")
            if pretax_src_col != col:
                raise AssertionError(
                    f"pretax link wrong period column {j}: "
                    f"got col {pretax_src_col}, expected {col}"
                )
            if tax_src_col != col:
                raise AssertionError(
                    f"tax link wrong period column {j}: "
                    f"got col {tax_src_col}, expected {col}"
                )

            # Bind each source reference to the IS header period identity (not column alone).
            pretax_period = _as_period_date(
                is_ws.cell(row=is_header_row, column=pretax_src_col).value
            )
            tax_period = _as_period_date(
                is_ws.cell(row=is_header_row, column=tax_src_col).value
            )
            if pretax_period != period:
                raise AssertionError(
                    f"pretax source period identity mismatch period {j}: "
                    f"header {pretax_period!r} != expected {period!r}"
                )
            if tax_period != period:
                raise AssertionError(
                    f"tax source period identity mismatch period {j}: "
                    f"header {tax_period!r} != expected {period!r}"
                )
            if is_headers[j] != period:
                raise AssertionError(
                    f"Income Statement period identity mismatch period {j}: "
                    f"header {is_headers[j]!r} != expected {period!r}"
                )

            if not _values_close(pretax_src_val, expect.pretax_values[j]):
                raise AssertionError(
                    f"pretax source value mismatch period {j}: "
                    f"got {pretax_src_val!r}, expected {expect.pretax_values[j]!r}"
                )
            if not _values_close(tax_src_val, expect.tax_values[j]):
                raise AssertionError(
                    f"tax source value mismatch period {j}: "
                    f"got {tax_src_val!r}, expected {expect.tax_values[j]!r}"
                )
            if _values_close(pretax_src_val, expect.tax_values[j]):
                raise AssertionError(
                    f"pretax source equals tax expectation (wrong-link leak) period {j}"
                )

            _assert_etr_formula_contract(etr_f, col_letter, pretax_row, tax_row)

            evaluated = _independent_etr(float(tax_src_val), float(pretax_src_val))
            if not _values_close(evaluated, expect.etr_values[j]):
                raise AssertionError(
                    f"evaluated etr mismatch period {j}: "
                    f"got {evaluated!r}, expected {expect.etr_values[j]!r}"
                )
            if anchor is not None:
                py_etr = anchor.historical.effective_tax_rate[j]
                if not _values_close(evaluated, py_etr):
                    raise AssertionError(
                        f"evaluated etr != python etr period {j}: "
                        f"{evaluated!r} vs {py_etr!r}"
                    )
                if not _values_close(pretax_src_val, anchor.historical.pretax_income[j]):
                    raise AssertionError(
                        f"pretax source != python pretax period {j}: "
                        f"{pretax_src_val!r} vs {anchor.historical.pretax_income[j]!r}"
                    )
    finally:
        wb.close()


def _maybe_export_reload(fin, *, reload: bool):
    if not reload:
        return fin
    from core.data.standardized_io import standardized_from_payload, standardized_to_payload

    return standardized_from_payload(standardized_to_payload(fin))


def _build_and_validate_pretax_parity(
    fin, tmp_path, stem: str, expect: _PretaxEtrExpect, *, reorder: bool
):
    _assert_fixture_owned_is_rows(fin, expect, reorder=reorder)
    anchor = _assert_python_pretax_etr(fin, expect)
    answer = _build_pretax_answer_key(fin, tmp_path, stem)
    # Reload with formulas retained (construction separated from validation).
    reloaded = tmp_path / f"{stem}_Answer_Key_reloaded.xlsx"
    shutil.copy2(answer, reloaded)
    _validate_pretax_etr_parity(reloaded, expect, anchor=anchor)
    return answer, anchor


# 12 combinations: concept mode × row order × original/export-reload.
_PRETAX_MATRIX_CASES = [
    ("alias-natural-original", _ALIAS_EXPECT, False, False),
    ("alias-reorder-original", _ALIAS_EXPECT, True, False),
    ("alias-natural-reload", _ALIAS_EXPECT, False, True),
    ("alias-reorder-reload", _ALIAS_EXPECT, True, True),
    ("canon-natural-original", _CANON_EXPECT, False, False),
    ("canon-reorder-original", _CANON_EXPECT, True, False),
    ("canon-natural-reload", _CANON_EXPECT, False, True),
    ("canon-reorder-reload", _CANON_EXPECT, True, True),
    ("label-natural-original", _LABEL_EXPECT, False, False),
    ("label-reorder-original", _LABEL_EXPECT, True, False),
    ("label-natural-reload", _LABEL_EXPECT, False, True),
    ("label-reorder-reload", _LABEL_EXPECT, True, True),
]
assert len(_PRETAX_MATRIX_CASES) == 12
assert len({case_id for case_id, *_ in _PRETAX_MATRIX_CASES}) == 12


@pytest.mark.parametrize(
    "case_id,expect,reorder,reload",
    _PRETAX_MATRIX_CASES,
    ids=[c[0] for c in _PRETAX_MATRIX_CASES],
)
def test_pretax_etr_parity_coverage_matrix(tmp_path, case_id, expect, reorder, reload):
    """All 12 concept × order × input-mode combinations with independent expectations."""
    if expect is _ALIAS_EXPECT:
        assert expect.pretax_values == (400.0, 500.0)
        assert expect.tax_values == (-60.0, -80.0)
        assert expect.etr_values == (0.15, 0.16)
        assert expect.pretax_concept == "income_before_tax"
    fin = _pretax_parity_fin(expect, reorder=reorder)
    fin = _maybe_export_reload(fin, reload=reload)
    _assert_fixture_owned_is_rows(fin, expect, reorder=reorder)
    _build_and_validate_pretax_parity(
        fin, tmp_path, f"PRETAX_MATRIX_{case_id}", expect, reorder=reorder
    )


def test_pretax_parity_zero_denominator_emitted_arithmetic(tmp_path):
    """Zero pretax: independent #N/A expectation and emitted zero-guard contract."""
    zero_expect = _make_expect(
        pretax_values=(0.0, 500.0),
        tax_values=(-60.0, -80.0),
    )
    assert zero_expect.etr_values == ("#N/A", 0.16)
    fin = _pretax_parity_fin(zero_expect, reorder=True)
    _build_and_validate_pretax_parity(
        fin, tmp_path, "PRETAX_ZERO", zero_expect, reorder=True
    )


def test_pretax_parity_detects_alias_removal(tmp_path, monkeypatch):
    """Parity coverage fails closed if income_before_tax alias is removed."""
    from core.model import line_resolver as lr
    from core.model.line_resolver import MissingLineError

    fin = _pretax_parity_fin(_ALIAS_EXPECT, reorder=True)
    _build_and_validate_pretax_parity(
        fin, tmp_path, "PRETAX_BASE", _ALIAS_EXPECT, reorder=True
    )

    cleared = {
        k: (frozenset() if k == "pretax_income" else v)
        for k, v in lr._EXPLICIT_CONCEPT_ALIASES.items()
    }
    monkeypatch.setattr(
        lr,
        "_EXPLICIT_CONCEPT_ALIASES",
        {**cleared, "pretax_income": frozenset({"pretax income"})},
    )
    label_aliases = {
        k: (v - {"income before income tax expense"} if k == "pretax_income" else v)
        for k, v in lr._EXACT_ALIASES.items()
    }
    monkeypatch.setattr(lr, "_EXACT_ALIASES", label_aliases)

    with pytest.raises(MissingLineError, match="pretax_income"):
        compute_anchor(fin, list(_ALIAS_EXPECT.period_ends))
    with pytest.raises(MissingLineError, match="pretax_income"):
        build_training_workbook(fin, tmp_path / "PRETAX_NOALIAS_Trainer.xlsx")


def _clean_answer_copy(src: Path, dest: Path) -> Path:
    if dest.exists():
        dest.unlink()
    shutil.copy2(src, dest)
    return dest


def test_pretax_parity_rejects_corrupted_source_links_and_etr(tmp_path):
    """Negative controls: validator rejects saved corrupted Answer-Key copies."""
    fin = _pretax_parity_fin(_ALIAS_EXPECT, reorder=True)
    clean_answer, anchor = _build_and_validate_pretax_parity(
        fin, tmp_path, "PRETAX_CORRUPT_BASE", _ALIAS_EXPECT, reorder=True
    )
    # Baseline on a fresh reload must still pass (construction ≠ validation).
    baseline = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_CORRUPT_baseline.xlsx")
    _validate_pretax_etr_parity(baseline, _ALIAS_EXPECT, anchor=anchor)

    # --- Redirect pretax link to the tax source row ---
    tax_redirect = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_CORRUPT_tax_row.xlsx")
    wb = load_workbook(tax_redirect, data_only=False)
    condensed = wb["Condensed Financials"]
    pretax_row = _condensed_row(condensed, "Pretax Income")
    tax_row = _condensed_row(condensed, "Tax Expense")
    tax_f = condensed.cell(row=tax_row, column=2).value
    condensed.cell(row=pretax_row, column=2).value = tax_f
    wb.save(tax_redirect)
    wb.close()
    with pytest.raises(AssertionError, match="pretax (source label mismatch|link redirected)"):
        _validate_pretax_etr_parity(tax_redirect, _ALIAS_EXPECT, anchor=anchor)

    # --- Redirect pretax link to another period column ---
    wrong_period = _clean_answer_copy(
        clean_answer, tmp_path / "PRETAX_CORRUPT_wrong_period.xlsx"
    )
    wb = load_workbook(wrong_period, data_only=False)
    condensed = wb["Condensed Financials"]
    pretax_row = _condensed_row(condensed, "Pretax Income")
    # Period-0 cell (col B) rewritten to reference period-1 source column (C).
    orig = str(condensed.cell(row=pretax_row, column=2).value)
    match = _IS_SOURCE_REF.fullmatch(orig.strip())
    assert match is not None
    row_s = match.group(2)
    condensed.cell(row=pretax_row, column=2).value = f"='Income Statement'!C{row_s}"
    wb.save(wrong_period)
    wb.close()
    with pytest.raises(AssertionError, match="pretax (link wrong period|source value mismatch)"):
        _validate_pretax_etr_parity(wrong_period, _ALIAS_EXPECT, anchor=anchor)

    # --- ETR mutations: remove minus / reverse ratio / corrupt zero guard ---
    etr_cases = [
        (
            "PRETAX_CORRUPT_etr_no_minus.xlsx",
            lambda col, pr, tr: f"=IF({col}{pr}=0,NA(),{col}{tr}/{col}{pr})",
            "etr formula contract mismatch",
        ),
        (
            "PRETAX_CORRUPT_etr_reversed.xlsx",
            lambda col, pr, tr: f"=IF({col}{pr}=0,NA(),-{col}{pr}/{col}{tr})",
            "etr formula contract mismatch",
        ),
        (
            "PRETAX_CORRUPT_etr_bad_guard.xlsx",
            lambda col, pr, tr: f"=IF({col}{pr}=1,NA(),-{col}{tr}/{col}{pr})",
            "etr formula contract mismatch",
        ),
    ]
    for name, mutator, match_msg in etr_cases:
        corrupted = _clean_answer_copy(clean_answer, tmp_path / name)
        wb = load_workbook(corrupted, data_only=False)
        condensed = wb["Condensed Financials"]
        pretax_row = _condensed_row(condensed, "Pretax Income")
        tax_row = _condensed_row(condensed, "Tax Expense")
        etr_row = _condensed_row(condensed, "Effective Tax Rate")
        col_letter = _col_letter(2)
        # Keep condensed row names and NA() present; only arithmetic/guard is wrong.
        mutated = mutator(col_letter, pretax_row, tax_row)
        assert "NA()" in mutated
        condensed.cell(row=etr_row, column=2).value = mutated
        wb.save(corrupted)
        wb.close()
        with pytest.raises(AssertionError, match=match_msg):
            _validate_pretax_etr_parity(corrupted, _ALIAS_EXPECT, anchor=anchor)


def test_pretax_parity_rejects_corrupted_period_headers(tmp_path):
    """Header-only mutations on each sheet must fail period-identity checks."""
    fin = _pretax_parity_fin(_ALIAS_EXPECT, reorder=True)
    clean_answer, anchor = _build_and_validate_pretax_parity(
        fin, tmp_path, "PRETAX_PERIOD_BASE", _ALIAS_EXPECT, reorder=True
    )
    baseline = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_PERIOD_baseline.xlsx")
    _validate_pretax_etr_parity(baseline, _ALIAS_EXPECT, anchor=anchor)

    period_match = "period (header|identity)"

    # --- Swap Income Statement headers; leave formulas and values unchanged ---
    is_swap = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_PERIOD_is_swap.xlsx")
    wb = load_workbook(is_swap, data_only=False)
    is_ws = wb["Income Statement"]
    is_header_row, _ = _income_statement_period_headers(wb, 2)
    a = is_ws.cell(row=is_header_row, column=2).value
    b = is_ws.cell(row=is_header_row, column=3).value
    is_ws.cell(row=is_header_row, column=2).value = b
    is_ws.cell(row=is_header_row, column=3).value = a
    wb.save(is_swap)
    wb.close()
    with pytest.raises(AssertionError, match=period_match):
        _validate_pretax_etr_parity(is_swap, _ALIAS_EXPECT, anchor=anchor)

    # --- Alter Income Statement header independently ---
    is_alter = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_PERIOD_is_alter.xlsx")
    wb = load_workbook(is_alter, data_only=False)
    is_ws = wb["Income Statement"]
    is_header_row, _ = _income_statement_period_headers(wb, 2)
    is_ws.cell(row=is_header_row, column=2).value = datetime(2099, 1, 1)
    wb.save(is_alter)
    wb.close()
    with pytest.raises(AssertionError, match=period_match):
        _validate_pretax_etr_parity(is_alter, _ALIAS_EXPECT, anchor=anchor)

    # --- Swap Condensed Financials income-section headers only ---
    cond_swap = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_PERIOD_cond_swap.xlsx")
    wb = load_workbook(cond_swap, data_only=False)
    condensed = wb["Condensed Financials"]
    cond_header_row, _ = _condensed_income_period_headers(wb, 2)
    a = condensed.cell(row=cond_header_row, column=2).value
    b = condensed.cell(row=cond_header_row, column=3).value
    condensed.cell(row=cond_header_row, column=2).value = b
    condensed.cell(row=cond_header_row, column=3).value = a
    wb.save(cond_swap)
    wb.close()
    with pytest.raises(AssertionError, match=period_match):
        _validate_pretax_etr_parity(cond_swap, _ALIAS_EXPECT, anchor=anchor)

    # --- Alter Condensed Financials header independently ---
    cond_alter = _clean_answer_copy(clean_answer, tmp_path / "PRETAX_PERIOD_cond_alter.xlsx")
    wb = load_workbook(cond_alter, data_only=False)
    condensed = wb["Condensed Financials"]
    cond_header_row, _ = _condensed_income_period_headers(wb, 2)
    condensed.cell(row=cond_header_row, column=3).value = datetime(2099, 6, 15)
    wb.save(cond_alter)
    wb.close()
    with pytest.raises(AssertionError, match=period_match):
        _validate_pretax_etr_parity(cond_alter, _ALIAS_EXPECT, anchor=anchor)
