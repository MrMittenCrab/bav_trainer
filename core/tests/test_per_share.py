"""Step 9F.1 — historical diluted per-share foundation."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
)
from core.data.standardized_io import (
    standardized_from_payload,
    standardized_to_payload,
)
from core.engine.component_catalog import (
    PER_SHARE_COMPONENT_CATALOG,
    expand_per_share_specs,
)
from core.engine.reference_model import PER_SHARE_SHEET, ReferenceModelBuilder
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.ingestion.reconciler import merge_documents
from core.model.financial_math import compute_anchor
from core.model.historical_expected import (
    expected_value_for_component,
    per_share_expected_series,
)
from core.model.period_axis import canonical_fiscal_periods
from core.model.per_share import (
    SUPPORTED_SHARE_SCALE_BASIS,
    compute_per_share_series,
    per_share_available,
)
from core.model.ratio_values import UNDEFINED_RATIO
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook, group_components_by_family
from core.tests.test_normalization import _inject_formula_and_cached_value

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
    return adapter.ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )


def _share_enabled_demo():
    data = _ingest_demo()
    periods = list(canonical_fiscal_periods(data))
    data.historical_shares = HistoricalShareData(
        scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
        diluted_weighted_average={
            period: 1000.0 + 25.0 * i for i, period in enumerate(periods)
        },
    )
    return data


def _li(label, values_by_date, concept=""):
    return LineItem(label=label, values=values_by_date, concept=concept)


def _tiny_fin(*, with_shares: bool = True, shares=None, scale_basis=None):
    d1, d2, d3 = date(2023, 12, 31), date(2024, 12, 31), date(2025, 12, 31)

    def vals(a, b, c):
        return {d1: a, d2: b, d3: c}

    hist = None
    if with_shares:
        hist = HistoricalShareData(
            scale_basis=scale_basis or SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average=shares
            if shares is not None
            else {d1: 100.0, d2: 110.0, d3: 120.0},
        )
    return StandardizedFinancials(
        ticker="PS",
        company_name="Per Share Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=d1, label="FY2023"),
            FinancialPeriod(end_date=d2, label="FY2024"),
            FinancialPeriod(end_date=d3, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", vals(1000, 1100, 1200)),
            _li("Finance costs", vals(-10, -11, -12)),
            _li("Finance income", vals(0, 0, 0)),
            _li("Profit before tax", vals(200, 220, 240)),
            _li("Income tax expense", vals(-30, -33, -36)),
            _li("Profit for the year", vals(170, 187, 204)),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", vals(50, 55, 60)),
            _li("Trade receivables", vals(40, 45, 50)),
            _li("Property, plant and equipment", vals(400, 420, 440)),
            _li("Trade payables", vals(30, 35, 40)),
            _li("Bank borrowings", vals(200, 210, 220)),
            _li("Total equity", vals(260, 275, 290)),
        ],
        cash_flow=[_li("Net cash from operating activities", vals(80, 90, 100))],
        historical_shares=hist,
    )


def test_historical_shares_round_trip_and_legacy():
    shares = HistoricalShareData(
        scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
        diluted_weighted_average={
            date(2024, 12, 31): 1000.0,
            date(2025, 12, 31): 1025.0,
        },
    )
    fin = _tiny_fin()
    fin.historical_shares = shares
    payload = standardized_to_payload(fin)
    restored = standardized_from_payload(payload)
    assert restored.historical_shares is not None
    assert restored.historical_shares.scale_basis == SUPPORTED_SHARE_SCALE_BASIS
    assert restored.historical_shares.diluted_weighted_average == {
        date(2024, 12, 31): 1000.0,
        date(2025, 12, 31): 1025.0,
    }

    legacy = _tiny_fin(with_shares=False)
    legacy_payload = standardized_to_payload(legacy)
    assert legacy_payload.get("historical_shares") is None
    restored_legacy = standardized_from_payload(legacy_payload)
    assert restored_legacy.historical_shares is None


def test_structured_json_ingest_historical_shares(tmp_path):
    payload = {
        "ticker": "ING",
        "company_name": "Ingest Co",
        "currency": "HKD",
        "units": "HKD in Millions",
        "periods": [
            {"end_date": "2024-12-31", "label": "FY2024"},
            {"end_date": "2025-12-31", "label": "FY2025"},
        ],
        "income_statement": [
            {
                "label": "Revenue",
                "values": {"2024-12-31": 1000, "2025-12-31": 1100},
            },
            {
                "label": "Finance costs",
                "values": {"2024-12-31": -10, "2025-12-31": -11},
            },
            {
                "label": "Finance income",
                "values": {"2024-12-31": 0, "2025-12-31": 0},
            },
            {
                "label": "Profit before tax",
                "values": {"2024-12-31": 200, "2025-12-31": 220},
            },
            {
                "label": "Income tax expense",
                "values": {"2024-12-31": -30, "2025-12-31": -33},
            },
            {
                "label": "Profit for the year",
                "values": {"2024-12-31": 170, "2025-12-31": 187},
            },
        ],
        "balance_sheet": [
            {
                "label": "Cash and cash equivalents",
                "values": {"2024-12-31": 50, "2025-12-31": 55},
            },
            {
                "label": "Trade receivables",
                "values": {"2024-12-31": 40, "2025-12-31": 45},
            },
            {
                "label": "Property, plant and equipment",
                "values": {"2024-12-31": 400, "2025-12-31": 420},
            },
            {
                "label": "Trade payables",
                "values": {"2024-12-31": 30, "2025-12-31": 35},
            },
            {
                "label": "Bank borrowings",
                "values": {"2024-12-31": 200, "2025-12-31": 210},
            },
            {
                "label": "Total equity",
                "values": {"2024-12-31": 260, "2025-12-31": 275},
            },
        ],
        "cash_flow": [
            {
                "label": "Net cash from operating activities",
                "values": {"2024-12-31": 50, "2025-12-31": 60},
            }
        ],
        "historical_shares": {
            "scale_basis": "financial_statement_units",
            "diluted_weighted_average": {
                "2024-12-31": 1000.0,
                "2025-12-31": 1025.0,
            },
        },
    }
    path = tmp_path / "shares.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    data = HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(path), doc_type=DocumentType.OTHER)]
    )
    assert data.historical_shares is not None
    assert data.historical_shares.scale_basis == SUPPORTED_SHARE_SCALE_BASIS
    assert data.historical_shares.diluted_weighted_average == {
        date(2024, 12, 31): 1000.0,
        date(2025, 12, 31): 1025.0,
    }


def test_merge_historical_shares_newest_wins_and_scale_mismatch():
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)
    base = _tiny_fin(
        shares={d1: 1000.0, d2: 1025.0},
    )
    # Tiny has 3 periods; trim shares merge objects to 2-period supplements
    base.historical_shares = HistoricalShareData(
        scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
        diluted_weighted_average={d1: 1000.0},
    )
    supplement = StandardizedFinancials(
        ticker=base.ticker,
        company_name=base.company_name,
        currency=base.currency,
        units=base.units,
        jurisdiction=base.jurisdiction,
        periods=base.periods,
        income_statement=[],
        balance_sheet=[],
        cash_flow=[],
        historical_shares=HistoricalShareData(
            scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average={d1: 999.0, d2: 1025.0},
        ),
    )
    merge_documents(base, supplement, "share update")
    assert base.historical_shares is not None
    assert base.historical_shares.diluted_weighted_average[d1] == 999.0
    assert base.historical_shares.diluted_weighted_average[d2] == 1025.0

    bad = StandardizedFinancials(
        ticker=base.ticker,
        company_name=base.company_name,
        currency=base.currency,
        units=base.units,
        jurisdiction=base.jurisdiction,
        periods=base.periods,
        income_statement=[],
        balance_sheet=[],
        cash_flow=[],
        historical_shares=HistoricalShareData(
            scale_basis="absolute_shares",
            diluted_weighted_average={d2: 1100.0},
        ),
    )
    with pytest.raises(ValueError, match="scale_basis mismatch"):
        merge_documents(base, bad, "bad scale")


def test_ordinary_per_share_series_and_edges():
    fin = _tiny_fin()
    periods = list(canonical_fiscal_periods(fin))
    anchor = compute_anchor(fin, periods)
    series = compute_per_share_series(fin, periods, anchor)
    assert series.diluted_weighted_average_shares == (100.0, 110.0, 120.0)
    assert series.reported_diluted_eps[0] == pytest.approx(170.0 / 100.0)
    assert series.reported_diluted_eps[1] == pytest.approx(187.0 / 110.0)
    assert series.reported_diluted_eps[2] == pytest.approx(204.0 / 120.0)
    assert series.diluted_eps_change[0] is None
    assert series.diluted_share_count_change[0] is None
    assert series.diluted_eps_change[1] == pytest.approx(
        series.reported_diluted_eps[1] - series.reported_diluted_eps[0]
    )
    assert series.diluted_share_count_change[1] == pytest.approx(10.0)
    assert series.diluted_share_count_change[2] == pytest.approx(10.0)
    for i, nopat in enumerate(anchor.historical.nopat):
        if nopat == UNDEFINED_RATIO:
            assert series.nopat_per_diluted_share[i] == UNDEFINED_RATIO
        else:
            assert series.nopat_per_diluted_share[i] == pytest.approx(
                float(nopat) / series.diluted_weighted_average_shares[i]
            )

    # Unchanged shares -> 0.0 change; negatives retained on NI/EPS
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)
    fin_neg = StandardizedFinancials(
        ticker="NEG",
        company_name="Neg Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=d1, label="FY2024"),
            FinancialPeriod(end_date=d2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", {d1: 1000, d2: 900}),
            _li("Finance costs", {d1: -10, d2: -11}),
            _li("Finance income", {d1: 0, d2: 0}),
            _li("Profit before tax", {d1: -50, d2: -40}),
            _li("Income tax expense", {d1: 5, d2: 4}),
            _li("Profit for the year", {d1: -45, d2: -36}),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", {d1: 50, d2: 55}),
            _li("Trade receivables", {d1: 40, d2: 45}),
            _li("Property, plant and equipment", {d1: 400, d2: 420}),
            _li("Trade payables", {d1: 30, d2: 35}),
            _li("Bank borrowings", {d1: 200, d2: 210}),
            _li("Total equity", {d1: 260, d2: 275}),
        ],
        cash_flow=[_li("Net cash from operating activities", {d1: 10, d2: 12})],
        historical_shares=HistoricalShareData(
            scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average={d1: 100.0, d2: 100.0},
        ),
    )
    periods_n = list(canonical_fiscal_periods(fin_neg))
    series_n = compute_per_share_series(
        fin_neg, periods_n, compute_anchor(fin_neg, periods_n)
    )
    assert series_n.reported_diluted_eps[0] == pytest.approx(-0.45)
    assert series_n.diluted_share_count_change[1] == pytest.approx(0.0)
    assert series_n.diluted_eps_change[1] == pytest.approx(
        series_n.reported_diluted_eps[1] - series_n.reported_diluted_eps[0]
    )


def test_per_share_fail_closed_and_availability():
    assert not per_share_available(_tiny_fin(with_shares=False))
    empty = _tiny_fin()
    empty.historical_shares = HistoricalShareData(
        scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
        diluted_weighted_average={},
    )
    assert not per_share_available(empty)

    fin = _tiny_fin()
    periods = list(canonical_fiscal_periods(fin))
    incomplete = _tiny_fin(
        shares={periods[0]: 100.0, periods[1]: 110.0},
    )
    with pytest.raises(ValueError, match="missing diluted"):
        compute_per_share_series(
            incomplete, periods, compute_anchor(incomplete, periods)
        )

    none_share = _tiny_fin(
        shares={periods[0]: 100.0, periods[1]: 110.0, periods[2]: None},
    )
    with pytest.raises(ValueError, match="missing diluted"):
        compute_per_share_series(
            none_share, periods, compute_anchor(none_share, periods)
        )

    zero = _tiny_fin(
        shares={periods[0]: 100.0, periods[1]: 0.0, periods[2]: 120.0},
    )
    with pytest.raises(ValueError, match="must be > 0"):
        compute_per_share_series(zero, periods, compute_anchor(zero, periods))

    negative = _tiny_fin(
        shares={periods[0]: 100.0, periods[1]: -5.0, periods[2]: 120.0},
    )
    with pytest.raises(ValueError, match="must be > 0"):
        compute_per_share_series(
            negative, periods, compute_anchor(negative, periods)
        )

    bad_scale = _tiny_fin(scale_basis="absolute_shares")
    with pytest.raises(ValueError, match="unsupported historical share scale_basis"):
        compute_per_share_series(
            bad_scale, periods, compute_anchor(bad_scale, periods)
        )


def test_catalog_expand_and_expected_keys():
    periods = [date(y, 12, 31) for y in range(2021, 2026)]
    assert [f.id for f in PER_SHARE_COMPONENT_CATALOG] == [
        "reported_diluted_eps",
        "nopat_per_diluted_share",
        "diluted_eps_change",
        "diluted_share_count_change",
    ]
    assert [f.order for f in PER_SHARE_COMPONENT_CATALOG] == [67, 68, 69, 70]

    specs = expand_per_share_specs(periods, start_order=260)
    assert len(specs) == 18
    by_family = {}
    for spec in specs:
        by_family.setdefault(spec.family_id, []).append(spec.period_index)
    assert by_family["reported_diluted_eps"] == [0, 1, 2, 3, 4]
    assert by_family["nopat_per_diluted_share"] == [0, 1, 2, 3, 4]
    assert by_family["diluted_eps_change"] == [1, 2, 3, 4]
    assert by_family["diluted_share_count_change"] == [1, 2, 3, 4]

    fin = _share_enabled_demo()
    builder = ReferenceModelBuilder(fin)
    assert builder.per_share_series is not None
    assert len(builder.per_share_specs) == 18
    series = per_share_expected_series(builder.per_share_series)
    assert set(series) == {f.id for f in PER_SHARE_COMPONENT_CATALOG}


def test_gating_no_shares_omits_module(tmp_path):
    data = _ingest_demo()
    assert data.historical_shares is None
    builder = ReferenceModelBuilder(data)
    assert builder.per_share_series is None
    assert builder.per_share_specs == ()

    trainer, answer = build_training_workbook(data, tmp_path / "NO_SHARES.xlsx")
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 259
    assert len(group_components_by_family(smap)) == 62
    assert not any(c.category == "per_share" for c in smap.all_ordered())
    wb = load_workbook(answer)
    assert PER_SHARE_SHEET not in wb.sheetnames
    wb.close()
    assert check_workbook(trainer).blank == 259


def test_fail_closed_build_incomplete_and_invalid(tmp_path):
    periods = list(canonical_fiscal_periods(_ingest_demo()))
    incomplete = _ingest_demo()
    incomplete.historical_shares = HistoricalShareData(
        scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
        diluted_weighted_average={periods[0]: 1000.0},
    )
    with pytest.raises(ValueError, match="missing diluted"):
        build_training_workbook(incomplete, tmp_path / "INCOMPLETE.xlsx")

    bad_scale = _share_enabled_demo()
    assert bad_scale.historical_shares is not None
    bad_scale.historical_shares.scale_basis = "absolute_shares"
    with pytest.raises(ValueError, match="unsupported historical share scale_basis"):
        build_training_workbook(bad_scale, tmp_path / "BAD_SCALE.xlsx")

    zero = _share_enabled_demo()
    assert zero.historical_shares is not None
    zero.historical_shares.diluted_weighted_average[periods[2]] = 0.0
    with pytest.raises(ValueError, match="must be > 0"):
        build_training_workbook(zero, tmp_path / "ZERO.xlsx")


def test_share_enabled_demo_surface(tmp_path):
    data = _share_enabled_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "SHARE_BASE.xlsx")
    smap = load_semantic_map(answer)
    assert len(smap.all_ordered()) == 293
    assert len(group_components_by_family(smap)) == 70
    ps = [c for c in smap.all_ordered() if c.category == "per_share"]
    assert len(ps) == 18
    assert {c.family_id for c in ps} == {f.id for f in PER_SHARE_COMPONENT_CATALOG}
    assert all(c.tab == PER_SHARE_SHEET for c in ps)

    wb = load_workbook(answer)
    ws = wb[PER_SHARE_SHEET]
    assert "Per Share Analysis" in str(ws["A1"].value)
    assert ws.cell(4, 1).value == "Metric"
    assert ws.cell(5, 1).value == "Reported Net Income"
    assert ws.cell(6, 1).value == "NOPAT"
    assert ws.cell(7, 1).value == "Diluted Weighted-Average Shares"
    assert ws.cell(9, 1).value == "Reported Diluted EPS"
    assert ws.cell(10, 1).value == "NOPAT per Diluted Share"
    assert ws.cell(12, 1).value == "Change in Diluted EPS"
    assert ws.cell(13, 1).value == "Change in Diluted Weighted-Average Shares"
    assert ws.cell(12, 2).value == "N/A"
    assert ws.cell(13, 2).value == "N/A"
    practice = {(c.tab, c.cell) for c in smap.all_ordered()}
    assert (PER_SHARE_SHEET, "B12") not in practice
    assert (PER_SHARE_SHEET, "B13") not in practice
    assert (PER_SHARE_SHEET, "B7") not in practice

    for j in range(5):
        assert ws.cell(7, 2 + j).value == pytest.approx(1000.0 + 25.0 * j)

    wb_t = load_workbook(trainer)
    ws_t = wb_t[PER_SHARE_SHEET]
    for j in range(5):
        assert ws_t.cell(7, 2 + j).value == pytest.approx(1000.0 + 25.0 * j)
    for comp in ps:
        row, col = parse_cell_ref(comp.cell)
        cell = wb_t[comp.tab].cell(row=row, column=col)
        assert cell.value is None
        assert _fill_rgb(cell) == "FFFF00"
    wb.close()
    wb_t.close()

    summary = check_workbook(trainer)
    assert summary.total == 293
    assert summary.blank == 293

    assumptions = json.loads(DEMO_ASSUMPTIONS.read_text(encoding="utf-8"))
    trainer_n, answer_n = build_training_workbook(
        data, tmp_path / "SHARE_NORM.xlsx", assumptions
    )
    smap_n = load_semantic_map(answer_n)
    assert len(smap_n.all_ordered()) == 313
    assert len(group_components_by_family(smap_n)) == 74
    assert check_workbook(trainer_n).blank == 313


def test_per_share_check_trust_and_dynamic(tmp_path):
    data = _share_enabled_demo()
    trainer, answer = build_training_workbook(data, tmp_path / "PS_Check.xlsx")
    smap = load_semantic_map(answer)
    comp = next(
        c
        for c in smap.all_ordered()
        if c.family_id == "reported_diluted_eps" and c.period_index == 1
    )
    wb = load_workbook(trainer, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    assert check_workbook(trainer).correct == 1

    # Equivalent non-exact formula with matching cached value
    trainer2, answer2 = build_training_workbook(data, tmp_path / "PS_Eq.xlsx")
    smap2 = load_semantic_map(answer2)
    comp2 = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "reported_diluted_eps" and c.period_index == 1
    )
    expected = float(comp2.expected_value)
    _inject_formula_and_cached_value(
        trainer2,
        comp2.tab,
        comp2.cell,
        formula=f"={expected}",
        cached_value=expected,
    )
    assert check_workbook(trainer2).correct == 1

    # Incorrect cached value -> red
    trainer3, answer3 = build_training_workbook(data, tmp_path / "PS_Bad.xlsx")
    smap3 = load_semantic_map(answer3)
    comp3 = next(
        c
        for c in smap3.all_ordered()
        if c.family_id == "reported_diluted_eps" and c.period_index == 1
    )
    _inject_formula_and_cached_value(
        trainer3,
        comp3.tab,
        comp3.cell,
        formula="=1+1",
        cached_value=999.0,
    )
    summary_bad = check_workbook(trainer3)
    assert summary_bad.incorrect == 1

    # Share-row tamper fails before recolor
    trainer4, answer4 = build_training_workbook(data, tmp_path / "PS_Tamper.xlsx")
    smap4 = load_semantic_map(answer4)
    comp4 = next(
        c
        for c in smap4.all_ordered()
        if c.family_id == "reported_diluted_eps" and c.period_index == 1
    )
    wb = load_workbook(trainer4, data_only=False)
    row, col = parse_cell_ref(comp4.cell)
    wb[comp4.tab].cell(row=row, column=col).value = comp4.formula
    wb[PER_SHARE_SHEET].cell(7, 2).value = 1
    wb.save(trainer4)
    wb.close()
    with pytest.raises(
        ValueError, match="Trusted workbook cell was modified: Per Share Analysis"
    ):
        check_workbook(trainer4)
    wb = load_workbook(trainer4, data_only=False)
    assert _fill_rgb(wb[comp4.tab].cell(row=row, column=col)) == "FFFF00"
    wb.close()

    # Live judgment coexistence: EPS unchanged; dynamic Check still green
    trainer5, answer5 = build_training_workbook(data, tmp_path / "PS_Live.xlsx")
    smap5 = load_semantic_map(answer5)
    eps = next(
        c
        for c in smap5.all_ordered()
        if c.family_id == "reported_diluted_eps" and c.period_index == 4
    )
    nopat_ps = next(
        c
        for c in smap5.all_ordered()
        if c.family_id == "nopat_per_diluted_share" and c.period_index == 4
    )
    ref_eps = float(eps.expected_value)
    ref_nopat_ps = float(nopat_ps.expected_value)

    from core.trainer.check_context import (
        classification_overrides_for_check,
        load_check_context,
    )

    wb = load_workbook(trainer5, data_only=False)
    # Demo judgment row 5 is lease-liability style; flip to Financial Liability.
    wb["Accounting Judgment"].cell(5, 6).value = "Financial Liability"
    wb.save(trainer5)
    wb.close()

    ctx = load_check_context(answer5)
    wb = load_workbook(trainer5, data_only=False)
    overrides = classification_overrides_for_check(wb, ctx)
    wb.close()
    fin = standardized_from_payload(ctx.source_payload)
    periods = list(canonical_fiscal_periods(fin))
    alt_anchor = compute_anchor(fin, periods, classification_overrides=overrides)
    alt_ps = compute_per_share_series(fin, periods, alt_anchor)
    assert alt_ps.reported_diluted_eps[4] == pytest.approx(ref_eps)
    # Dynamic expected uses current treatment-conditioned NOPAT
    assert alt_ps.nopat_per_diluted_share[4] == pytest.approx(
        float(alt_anchor.historical.nopat[4])
        / alt_ps.diluted_weighted_average_shares[4]
    )
    # BS classification typically leaves NOPAT unchanged in this model
    assert alt_ps.nopat_per_diluted_share[4] == pytest.approx(ref_nopat_ps)

    _inject_formula_and_cached_value(
        trainer5,
        eps.tab,
        eps.cell,
        formula=eps.formula,
        cached_value=ref_eps,
    )
    _inject_formula_and_cached_value(
        trainer5,
        nopat_ps.tab,
        nopat_ps.cell,
        formula=nopat_ps.formula,
        cached_value=ref_nopat_ps,
    )
    summary_live = check_workbook(trainer5)
    assert summary_live.correct == 2
    assert summary_live.incorrect == 0


def test_nopat_na_propagates_to_per_share(tmp_path):
    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="NA",
        company_name="NA Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[
            FinancialPeriod(end_date=d1, label="FY2024"),
            FinancialPeriod(end_date=d2, label="FY2025"),
        ],
        income_statement=[
            _li("Revenue", {d1: 1000, d2: 1100}),
            _li("Finance costs", {d1: -10, d2: -11}),
            _li("Finance income", {d1: 0, d2: 0}),
            # Pretax zero in period 2 -> ETR/NOPAT #N/A under model rules
            _li("Profit before tax", {d1: 200, d2: 0}),
            _li("Income tax expense", {d1: -30, d2: 0}),
            _li("Profit for the year", {d1: 170, d2: 0}),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", {d1: 50, d2: 55}),
            _li("Trade receivables", {d1: 40, d2: 45}),
            _li("Property, plant and equipment", {d1: 400, d2: 420}),
            _li("Trade payables", {d1: 30, d2: 35}),
            _li("Bank borrowings", {d1: 200, d2: 210}),
            _li("Total equity", {d1: 260, d2: 275}),
        ],
        cash_flow=[_li("Net cash from operating activities", {d1: 50, d2: 60})],
        historical_shares=HistoricalShareData(
            scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average={d1: 100.0, d2: 105.0},
        ),
    )
    periods = [d1, d2]
    anchor = compute_anchor(fin, periods)
    assert anchor.historical.nopat[1] == UNDEFINED_RATIO
    series = compute_per_share_series(fin, periods, anchor)
    assert series.nopat_per_diluted_share[1] == UNDEFINED_RATIO

    trainer, answer = build_training_workbook(fin, tmp_path / "PS_NA.xlsx")
    smap = load_semantic_map(answer)
    nopat_ps = next(
        c
        for c in smap.all_ordered()
        if c.family_id == "nopat_per_diluted_share" and c.period_index == 1
    )
    assert nopat_ps.expected_value == UNDEFINED_RATIO

    _inject_formula_and_cached_value(
        trainer,
        nopat_ps.tab,
        nopat_ps.cell,
        formula="=NA()",
        cached_value=UNDEFINED_RATIO,
    )
    assert check_workbook(trainer).correct == 1

    trainer2, _ = build_training_workbook(fin, tmp_path / "PS_NA_ZERO.xlsx")
    smap2 = load_semantic_map(answer)
    nopat_ps2 = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "nopat_per_diluted_share" and c.period_index == 1
    )
    _inject_formula_and_cached_value(
        trainer2,
        nopat_ps2.tab,
        nopat_ps2.cell,
        formula="=0",
        cached_value=0.0,
    )
    assert check_workbook(trainer2).incorrect == 1


def test_expected_value_requires_per_share_series(tmp_path):
    data = _share_enabled_demo()
    _, answer = build_training_workbook(data, tmp_path / "PS_Req.xlsx")
    smap = load_semantic_map(answer)
    ps_comp = next(c for c in smap.all_ordered() if c.family_id == "reported_diluted_eps")
    builder = ReferenceModelBuilder(data)
    with pytest.raises(ValueError, match="requires a PerShareSeries"):
        expected_value_for_component(builder.anchor, ps_comp, per_share=None)
