"""Formula-integrity tests for the semantic Answer Key (Step 2)."""

from __future__ import annotations

import json
from datetime import date
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
    assert len(smap.all_ordered()) == 222
    hist = expand_historical_specs(
        (_ingest_demo().fiscal_years() or _ingest_demo().period_dates())
    )
    assert len(hist) == 118
    assert len(smap.all_ordered()) == 222

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
        QUALITY_COMPONENT_CATALOG,
        WORKING_CAPITAL_COMPONENT_CATALOG,
        PROFITABILITY_DRIVER_COMPONENT_CATALOG,
        PROFITABILITY_CHANGE_COMPONENT_CATALOG,
    )

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 222

    families = {c.family_id for c in smap.all_ordered()}
    assert families == (
        {f.id for f in COMPONENT_CATALOG}
        | {f.id for f in QUALITY_COMPONENT_CATALOG}
        | {f.id for f in WORKING_CAPITAL_COMPONENT_CATALOG}
        | {f.id for f in PROFITABILITY_DRIVER_COMPONENT_CATALOG}
        | {f.id for f in PROFITABILITY_CHANGE_COMPONENT_CATALOG}
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

    assert len(CLASSIFICATION_JUDGMENT_TEMPLATES) == 4
    assert len(set(CLASSIFICATION_JUDGMENT_TEMPLATES)) == 4
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
    assert len(CLASSIFICATION_JUDGMENT_TEMPLATES) == 4
    assert len(builder.judgment_cases) == 1
    case = builder.judgment_cases[0]
    assert case.label == "Operating lease liabilities"
    assert case.supplied_treatment == "Operating Long-Term Liability"
    assert case.alternatives == ("Financial Liability",)

    _, answer = _build_pair(tmp_path)
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 222
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
    assert case.override_selector == "concept:lease_liability"

    context = build_check_context(
        data, builder.periods, builder.assumptions, builder.judgment_cases
    )
    assert len(context.judgment_bindings) == 1
    binding = context.judgment_bindings[0]
    assert binding.worksheet_row == 5
    assert binding.override_selector == "concept:lease_liability"
    assert binding.reference_treatment == "Operating Long-Term Liability"
    assert binding.allowed_treatments == (
        "Operating Long-Term Liability",
        "Financial Liability",
    )

    trainer_path, answer_key_path = _build_pair(tmp_path)
    loaded = load_check_context(answer_key_path)
    assert loaded is not None
    assert loaded.judgment_bindings[0].override_selector == "concept:lease_liability"

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


def test_judgment_selector_uses_concept_when_present():
    from core.engine.reference_model import ReferenceModelBuilder

    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    case = builder.judgment_cases[0]
    assert case.override_selector == "concept:lease_liability"
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
    assert len(smap.all_ordered()) == 222
    for comp in smap.all_ordered():
        expected = expected_value_for_component(
            builder.anchor, comp, earnings_quality=quality
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
