"""Formula-integrity tests for the semantic Answer Key (Step 2)."""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl import load_workbook

from core.data.interface import DocumentManifest, DocumentType
from core.engine.component_catalog import COMPONENT_CATALOG
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.financial_math import compute_anchor
from core.model.ri_engine import run_scenario
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


def test_cli_assumptions_propagate(tmp_path):
    """CLI-supplied assumptions must change a visible model input."""
    data = _ingest_demo()
    # Build default to capture baseline diluted shares / growth path
    _, answer_default = build_training_workbook(data, tmp_path / "Default_Trainer.xlsx")
    smap_default = load_semantic_map(answer_default)

    assumptions = json.loads(
        (ROOT / "example" / "DEMO_HK_Trainer_reference.assumptions.json").read_text(encoding="utf-8")
    )
    assumptions["marketData"]["dilutedShares"] = 2500.0
    assumptions["scenarios"]["Base"]["growthVector"] = [0.25] + [0.10] * 9

    from core.__main__ import main

    out = tmp_path / "Assumed_Trainer.xlsx"
    assumptions_path = tmp_path / "custom.assumptions.json"
    assumptions_path.write_text(json.dumps(assumptions), encoding="utf-8")
    assert main(["build", str(DEMO_JSON), "-o", str(out), "-a", str(assumptions_path)]) == 0

    answer = tmp_path / "Assumed_Answer_Key.xlsx"
    wb = load_workbook(answer, data_only=False)
    ws = wb["Model_Base"]
    smap = load_semantic_map(answer)
    sales = smap.get("model_sales_y1")
    row, col = parse_cell_ref(sales.cell)
    formula = ws.cell(row=row, column=col).value
    assert isinstance(formula, str)
    assert "0.25" in formula.replace(" ", "")
    # Shares cell on model sheet should reflect dilutedShares
    found_shares = False
    for r in range(1, 50):
        if ws.cell(row=r, column=1).value == "Diluted Shares":
            assert ws.cell(row=r, column=col).value == 2500.0
            found_shares = True
            break
    assert found_shares
    assert sales.expected_value != smap_default.get("model_sales_y1").expected_value
    wb.close()


def test_nopat_formula_adds_after_tax_net_interest(tmp_path):
    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    nopat = smap.get("nopat_fy")
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
    from core.model.financial_math import _val

    ni_item = resolve_line(data.income_statement, "net_income", required=True).item
    assert abs(float(nopat.expected_value) - float(_val(ni_item, periods[-1]))) > 1.0
    wb.close()


def test_condensed_aggregates_are_on_sheet_sumif(tmp_path):
    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    for cid in ("nowc_agg", "noa_agg", "net_debt"):
        formula = smap.get(cid).formula
        assert "Balance Sheet" not in formula
        assert "SUMIF" in formula
        assert "$B$" in formula


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
        if condensed.cell(row=r, column=1).value == "Equity"
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
    _, answer = _build_pair(tmp_path)
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
    assert len(smap.all_ordered()) == len(COMPONENT_CATALOG)

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
    nopat = smap.get("nopat_fy")
    assert str(cl["Net Income"]) in nopat.formula
    assert str(cl["Net Interest After Tax"]) in nopat.formula
    assert condensed.cell(row=cl["Net Income"], column=2).value not in (None, "")
    assert condensed.cell(row=cl["Net Interest After Tax"], column=2).value not in (None, "")

    assert "Condensed Financials" in smap.get("rnoa").formula
    assert smap.get("roe_decomp").formula.startswith("=")
    # Spread is local RNOA − CoD on the DuPont sheet
    spread_f = smap.get("spread").formula
    assert spread_f.startswith("=")
    assert "-" in spread_f

    ws = wb["Model_Base"]
    ml = _labels(ws)
    fc = next(c for c in range(2, 30) if ws.cell(row=20, column=c).value == "Y1")
    for label in ("Sales", "NOPAT", "Abnormal Earnings", "Discount Factor"):
        assert ws.cell(row=ml[label], column=fc).value not in (None, "")
    assert ws.cell(row=ml["Abnormal Earnings"], column=fc + 9).value not in (None, "")
    assert ws.cell(row=ml["Discount Factor"], column=fc + 9).value not in (None, "")
    assert ws.cell(row=ml["Terminal Value"], column=fc + 9).value not in (None, "")
    for label in ("PV Terminal Value", "Intrinsic Value", "Intrinsic Value per Share"):
        assert ws.cell(row=ml[label], column=fc).value not in (None, "")
    assert smap.get("scenario_weighted").formula.startswith("=")
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

    _, answer = _build_pair(tmp_path)
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
    smap = load_semantic_map(trainer)
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


def test_missing_interest_income_still_populates_net_interest_chain(tmp_path):
    is_items = [
        _li("Revenue", 1000, 1100),
        _li("Finance costs", -40, -50),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    fin = _base_fin(income_statement=is_items)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert anchor.nopat != 0
    _, answer = build_training_workbook(fin, tmp_path / "MissInc_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    assert "Interest Income" not in labels
    assert "Interest Expense" in labels
    for name in ("Net Interest", "Net Interest After Tax", "NOPAT"):
        row = labels[name]
        assert ws.cell(row=row, column=2).value not in (None, "")
    wb.close()


def test_missing_interest_expense_income_only_case(tmp_path):
    is_items = [
        _li("Revenue", 1000, 1100),
        _li("Finance income", 5, 6),
        _li("Profit before tax", 200, 220),
        _li("Income tax expense", -30, -33),
        _li("Profit for the year", 170, 187),
    ]
    fin = _base_fin(income_statement=is_items)
    periods = [p.end_date for p in fin.periods]
    anchor = compute_anchor(fin, periods)
    assert anchor.nopat != 0
    _, answer = build_training_workbook(fin, tmp_path / "MissExp_Trainer.xlsx")
    wb = load_workbook(answer, data_only=False)
    ws = wb["Condensed Financials"]
    labels = {ws.cell(row=r, column=1).value: r for r in range(1, ws.max_row + 1)}
    assert "Interest Expense" not in labels
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
    eq_row = next(r for r in range(1, ws.max_row + 1) if ws.cell(row=r, column=1).value == "Equity")
    formula = str(ws.cell(row=eq_row, column=3).value)  # latest period col for n=2 is C? periods use col 2+j → col 3 for j=1
    assert "Balance Sheet" in formula
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
    f = str(ws.cell(row=labels["Equity"], column=2).value)
    assert "Balance Sheet" not in f
    assert str(labels["NOA"]) in f and str(labels["Net Debt"]) in f
    wb.close()
