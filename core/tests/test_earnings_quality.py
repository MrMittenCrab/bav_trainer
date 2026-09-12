"""Step 9A — historical earnings-quality cash conversion and accruals."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    LineItem,
    StandardizedFinancials,
)
from core.engine.component_catalog import (
    QUALITY_COMPONENT_CATALOG,
    expand_quality_specs,
)
from core.engine.reference_model import EARNINGS_QUALITY_SHEET, ReferenceModelBuilder
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.earnings_quality import (
    compute_earnings_quality_series,
    earnings_quality_availability,
)
from core.model.financial_math import compute_anchor
from core.model.historical_expected import expected_value_for_component
from core.model.line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from core.model.period_axis import canonical_fiscal_periods
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook, group_components_by_family

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"
DEMO_ASSUMPTIONS = ROOT / "example" / "DEMO_HK_Assumptions.json"


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _ingest_demo():
    adapter = HKManualDocumentAdapter()
    return adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])


def _li(label, values, *, concept=""):
    return LineItem(label=label, values=values, concept=concept)


def _tiny_fin(*, with_cfo=True, with_assets=True, ambiguous_cfo=False):
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)
    periods = [
        FinancialPeriod(end_date=d1, label="FY2024"),
        FinancialPeriod(end_date=d2, label="FY2025"),
    ]
    income = [
        _li("Revenue", {d1: 1000, d2: 1100}, concept="revenue"),
        _li("Profit before tax", {d1: 200, d2: 220}),
        _li("Income tax expense", {d1: -30, d2: -33}),
        _li("Finance costs", {d1: -10, d2: -11}),
        _li("Profit for the year", {d1: 100, d2: 120}),
    ]
    balance = [
        _li("Cash", {d1: 50, d2: 60}),
        _li("Trade receivables", {d1: 40, d2: 45}),
        _li("Property, plant and equipment", {d1: 200, d2: 210}),
    ]
    if with_assets:
        balance.append(_li("Total assets", {d1: 290, d2: 315}))
    balance.extend(
        [
            _li("Trade payables", {d1: 20, d2: 22}),
            _li("Bank borrowings", {d1: 80, d2: 85}),
            _li("Total equity", {d1: 190, d2: 208}),
        ]
    )
    cash_flow = []
    if with_cfo:
        cash_flow.append(
            _li("Net cash from operating activities", {d1: 80, d2: 90})
        )
    if ambiguous_cfo:
        cash_flow = [
            _li("Net cash from operating activities", {d1: 80, d2: 90}),
            _li("Net cash generated from operating activities", {d1: 70, d2: 75}),
        ]
    if not cash_flow:
        cash_flow.append(_li("Net cash from financing activities", {d1: -10, d2: -12}))
    return StandardizedFinancials(
        ticker="EQ",
        company_name="EQ Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=periods,
        income_statement=income,
        balance_sheet=balance,
        cash_flow=cash_flow,
    )


def test_operating_cash_flow_concept_and_aliases():
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)
    item = resolve_line(
        [_li("Weird label", {d1: 1, d2: 2}, concept="operating_cash_flow")],
        "operating_cash_flow",
    )
    assert item.item is not None
    assert item.item.concept == "operating_cash_flow"

    for label in (
        "Net cash from operating activities",
        "Net cash generated from operating activities",
        "Net cash provided by operating activities",
        "Net cash flow from operating activities",
        "Net cash flows from operating activities",
    ):
        resolved = resolve_line([_li(label, {d1: 1, d2: 2})], "operating_cash_flow")
        assert resolved.item is not None
        assert resolved.item.label == label

    generic = resolve_line(
        [_li("Cash generated from operations", {d1: 1, d2: 2})],
        "operating_cash_flow",
        required=False,
    )
    assert generic.item is None

    with pytest.raises(AmbiguousLineError):
        resolve_line(
            [
                _li("Net cash from operating activities", {d1: 1, d2: 2}),
                _li("Net cash generated from operating activities", {d1: 1, d2: 2}),
            ],
            "operating_cash_flow",
        )


def test_earnings_quality_series_core_cases():
    fin = _tiny_fin()
    periods = canonical_fiscal_periods(fin)
    anchor = compute_anchor(fin, periods)
    series = compute_earnings_quality_series(fin, periods, anchor)
    assert series.operating_cash_flow == (80.0, 90.0)
    assert series.cash_conversion_ratio[0] == pytest.approx(80.0 / 100.0)
    assert series.total_accruals == (20.0, 30.0)
    assert series.average_total_assets[0] is None
    assert series.accrual_ratio[0] is None
    assert series.average_total_assets[1] == pytest.approx((290.0 + 315.0) / 2.0)
    assert series.accrual_ratio[1] == pytest.approx(
        30.0 / series.average_total_assets[1]
    )

    # CFO > NI -> negative accruals
    fin2 = _tiny_fin()
    fin2.income_statement[-1].values[periods[0]] = 50.0
    fin2.cash_flow[0].values[periods[0]] = 80.0
    anchor2 = compute_anchor(fin2, periods)
    series2 = compute_earnings_quality_series(fin2, periods, anchor2)
    assert series2.total_accruals[0] == pytest.approx(-30.0)

    # Zero NI -> conversion 0.0
    fin3 = _tiny_fin()
    fin3.income_statement[-1].values[periods[0]] = 0.0
    anchor3 = compute_anchor(fin3, periods)
    series3 = compute_earnings_quality_series(fin3, periods, anchor3)
    assert series3.cash_conversion_ratio[0] == 0.0


def test_earnings_quality_without_assets_and_missing_cfo():
    fin = _tiny_fin(with_assets=False)
    periods = canonical_fiscal_periods(fin)
    avail = earnings_quality_availability(fin)
    assert avail.operating_cash_flow is True
    assert avail.total_assets is False
    series = compute_earnings_quality_series(fin, periods, compute_anchor(fin, periods))
    assert all(v is None for v in series.average_total_assets)
    assert all(v is None for v in series.accrual_ratio)
    assert series.total_accruals[0] == pytest.approx(20.0)

    fin_no = _tiny_fin(with_cfo=False)
    assert earnings_quality_availability(fin_no).operating_cash_flow is False
    with pytest.raises(MissingLineError):
        compute_earnings_quality_series(
            fin_no, canonical_fiscal_periods(fin_no), compute_anchor(fin_no, canonical_fiscal_periods(fin_no))
        )

    with pytest.raises(AmbiguousLineError):
        earnings_quality_availability(_tiny_fin(ambiguous_cfo=True))


def test_zero_average_assets_accrual_ratio_convention():
    fin = _tiny_fin()
    periods = canonical_fiscal_periods(fin)
    anchor = compute_anchor(fin, periods)
    for item in fin.balance_sheet:
        if item.label == "Total assets":
            item.values[periods[0]] = 0.0
            item.values[periods[1]] = 0.0
    series = compute_earnings_quality_series(fin, periods, anchor)
    assert series.average_total_assets[1] == 0.0
    assert series.accrual_ratio[1] == 0.0


def test_expand_quality_specs_counts_and_gating():
    periods = [date(y, 12, 31) for y in range(2021, 2026)]
    assert len(QUALITY_COMPONENT_CATALOG) == 5
    assert [f.order for f in QUALITY_COMPONENT_CATALOG] == [30, 31, 32, 33, 34]
    full = expand_quality_specs(periods, start_order=119, include_asset_scaled=True)
    assert len(full) == 23
    assert full[0].order == 119
    assert full[-1].order == 141
    core = expand_quality_specs(periods, start_order=119, include_asset_scaled=False)
    assert len(core) == 15
    assert {s.family_id for s in core} == {
        "operating_cash_flow_link",
        "cash_conversion_ratio",
        "total_accruals",
    }


def test_demo_quality_surface_base_and_normalization(tmp_path):
    import json

    data = _ingest_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "BASE_Trainer.xlsx")
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 141
    assert len(group_components_by_family(smap)) == 30
    wb = load_workbook(answer)
    assert EARNINGS_QUALITY_SHEET in wb.sheetnames
    wb.close()
    summary = check_workbook(trainer)
    assert summary.total == 141
    assert summary.blank == 141

    assumptions = json.loads(DEMO_ASSUMPTIONS.read_text(encoding="utf-8"))
    trainer_n, answer_n = build_training_workbook(
        data, tmp_path / "NORM_Trainer.xlsx", assumptions
    )
    smap_n = load_semantic_map(answer_n)
    assert len(smap_n.all_ordered()) == 161
    assert len(group_components_by_family(smap_n)) == 34
    summary_n = check_workbook(trainer_n)
    assert summary_n.total == 161
    assert summary_n.blank == 161


def test_cfo_unavailable_keeps_prior_surface(tmp_path):
    fin = _tiny_fin(with_cfo=False)
    builder = ReferenceModelBuilder(fin)
    assert builder.quality_series is None
    assert builder.quality_specs == ()
    answer = tmp_path / "NoCFO_Answer_Key.xlsx"
    trainer = tmp_path / "NoCFO_Trainer.xlsx"
    smap = builder.build(answer)
    from core.trainer.workbook import TrainingWorkbookGenerator

    TrainingWorkbookGenerator(answer, smap).generate(trainer)
    loaded = load_semantic_map(answer)
    # 2 periods: historical expandable cells only (no quality)
    assert all(c.category != "earnings_quality" for c in loaded.all_ordered())
    wb = load_workbook(answer)
    assert EARNINGS_QUALITY_SHEET not in wb.sheetnames
    wb.close()


def test_cfo_without_assets_omits_scaled_families(tmp_path):
    fin = _tiny_fin(with_assets=False)
    builder = ReferenceModelBuilder(fin)
    assert builder.quality_availability.operating_cash_flow is True
    assert builder.quality_availability.total_assets is False
    family_ids = {s.family_id for s in builder.quality_specs}
    assert family_ids == {
        "operating_cash_flow_link",
        "cash_conversion_ratio",
        "total_accruals",
    }
    answer = tmp_path / "NoAssets_Answer_Key.xlsx"
    smap = builder.build(answer)
    assert "average_total_assets" not in {c.family_id for c in smap.all_ordered()}


def test_quality_exact_and_equivalent_check(tmp_path):
    data = _ingest_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "Q_Trainer.xlsx")
    smap = load_semantic_map(answer)
    comp = next(
        c
        for c in smap.all_ordered()
        if c.family_id == "cash_conversion_ratio" and c.period_end == "2025-12-31"
    )
    wb = load_workbook(trainer, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    summary = check_workbook(trainer)
    assert summary.correct == 1

    # Equivalent cached value
    from core.tests.test_normalization import _inject_formula_and_cached_value

    _inject_formula_and_cached_value(
        trainer,
        comp.tab,
        comp.cell,
        formula=f"={float(comp.expected_value)}",
        cached_value=float(comp.expected_value),
    )
    assert check_workbook(trainer).correct == 1

    _inject_formula_and_cached_value(
        trainer,
        comp.tab,
        comp.cell,
        formula="=0",
        cached_value=0.0,
    )
    assert check_workbook(trainer).incorrect == 1


def test_quality_populated_row_tamper_fails_closed(tmp_path):
    data = _ingest_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "T_Trainer.xlsx")
    smap = load_semantic_map(answer)
    comp = next(c for c in smap.all_ordered() if c.family_id == "total_accruals")
    wb = load_workbook(trainer, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    # Tamper populated Reported Net Income row (row 6).
    wb[EARNINGS_QUALITY_SHEET].cell(6, 2).value = 1
    wb.save(trainer)
    wb.close()
    with pytest.raises(ValueError, match="Trusted workbook cell was modified: Earnings Quality"):
        check_workbook(trainer)
    wb = load_workbook(trainer, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row=row, column=col)) == "FFFF00"
    wb.close()

    trainer2, _ = build_training_workbook(data, tmp_path / "T2_Trainer.xlsx")
    from core.trainer.semantic_io import answer_key_path_for

    smap2 = load_semantic_map(answer_key_path_for(trainer2))
    comp2 = next(c for c in smap2.all_ordered() if c.family_id == "accrual_ratio")
    wb = load_workbook(trainer2, data_only=False)
    row, col = parse_cell_ref(comp2.cell)
    wb[comp2.tab].cell(row=row, column=col).value = comp2.formula
    wb[EARNINGS_QUALITY_SHEET].cell(10, 2).value = 1  # Total Assets populated link
    wb.save(trainer2)
    wb.close()
    with pytest.raises(ValueError, match="Trusted workbook cell was modified: Earnings Quality"):
        check_workbook(trainer2)


def test_quality_composes_with_normalization_and_classification(tmp_path):
    import json

    data = _ingest_demo()
    assumptions = json.loads(DEMO_ASSUMPTIONS.read_text(encoding="utf-8"))
    trainer, answer = build_training_workbook(
        data, tmp_path / "Compose_Trainer.xlsx", assumptions
    )
    smap = load_semantic_map(answer)
    net_debt = max(
        (c for c in smap.all_ordered() if c.family_id == "net_debt"),
        key=lambda c: c.period_index or 0,
    )
    norm = next(
        c
        for c in smap.all_ordered()
        if c.family_id == "pretax_normalization_adjustment"
        and c.period_end == "2023-12-31"
    )
    quality = next(
        c
        for c in smap.all_ordered()
        if c.family_id == "total_accruals" and c.period_end == "2025-12-31"
    )
    wb = load_workbook(trainer, data_only=False)
    wb["Accounting Judgment"].cell(5, 6).value = "Financial Liability"
    wb["Normalization Judgment"].cell(5, 6).value = "Recurring"
    for comp in (net_debt, norm, quality):
        r, c = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=r, column=c).value = comp.formula
    wb.save(trainer)
    wb.close()
    summary = check_workbook(trainer)
    assert summary.correct == 3
    assert summary.incorrect == 0
