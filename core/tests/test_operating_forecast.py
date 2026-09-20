"""Step 10A — one-year operating forecast foundation."""

from __future__ import annotations

import copy
import json
import math
from datetime import date
from pathlib import Path

import pytest

from core.data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    LineItem,
    StandardizedFinancials,
)
from core.data.standardized_io import standardized_from_payload
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.financial_math import compute_anchor
from core.model.operating_forecast import (
    ForecastDriverAssumption,
    OperatingForecastAssumptions,
    compute_one_year_operating_forecast,
)
from core.model.period_axis import canonical_fiscal_periods
from core.model.working_capital import compute_working_capital_series

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"
FR_STD = ROOT / "build" / "input" / "fast_retailing" / "reconciled" / "standardized.json"


def _ingest_demo():
    return HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )


def _li(label, v1, v2, concept=""):
    return LineItem(
        label=label,
        values={date(2024, 12, 31): v1, date(2025, 12, 31): v2},
        concept=concept,
    )


def _periods():
    return [
        FinancialPeriod(end_date=date(2024, 12, 31), label="FY2024"),
        FinancialPeriod(end_date=date(2025, 12, 31), label="FY2025"),
    ]


def _base_fin(**overrides):
    kwargs = dict(
        ticker="OF",
        company_name="OF Co",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[
            _li("Revenue", 1000, 1100),
            _li("Finance costs", -10, -11),
            _li("Finance income", 0, 0),
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


def _driver(value: float, *, origin="supplied", explanation="illustrative driver"):
    return ForecastDriverAssumption(
        value=value, origin=origin, explanation=explanation
    )


def _assumptions(
    growth=0.10,
    margin=0.20,
    nowc_ratio=0.05,
    *,
    origin="supplied",
):
    return OperatingForecastAssumptions(
        revenue_growth=_driver(growth, origin=origin, explanation="illustrative growth"),
        nopat_margin=_driver(margin, origin=origin, explanation="illustrative margin"),
        nowc_to_revenue=_driver(
            nowc_ratio, origin=origin, explanation="illustrative NOWC intensity"
        ),
    )


def _anchor(fin=None, *, overrides=None):
    fin = fin or _base_fin()
    periods = list(canonical_fiscal_periods(fin))
    return compute_anchor(
        fin, periods, classification_overrides=overrides
    ), periods, fin


def test_growth_path_independent_calculation():
    anchor, periods, _ = _anchor()
    opening_revenue = anchor.historical.revenue[-1]
    opening_nowc = anchor.reformulation.nowc[-1]
    result = compute_one_year_operating_forecast(
        anchor, periods, _assumptions(growth=0.10, margin=0.20, nowc_ratio=0.05)
    )
    assert result.forecast_revenue == pytest.approx(opening_revenue * 1.10)
    assert result.forecast_nopat == pytest.approx(result.forecast_revenue * 0.20)
    assert result.closing_nowc == pytest.approx(result.forecast_revenue * 0.05)
    assert result.change_in_nowc == pytest.approx(result.closing_nowc - opening_nowc)
    assert result.change_in_nowc > 0  # operating investment
    assert result.historical_period == periods[-1]
    assert result.forecast_period == date(2026, 12, 31)
    assert result.historical_period_label == "FY2025"
    assert result.forecast_period_label == "FY2026"
    assert result.comparators.sales_growth == pytest.approx(
        float(anchor.dupont["Sales Growth"][-1])
    )
    assert result.comparators.nopat_margin == pytest.approx(
        float(anchor.dupont["NOPAT Margin"][-1])
    )
    assert result.comparators.nowc_to_revenue == pytest.approx(
        opening_nowc / opening_revenue
    )


def test_contraction_and_nowc_release():
    anchor, periods, _ = _anchor()
    result = compute_one_year_operating_forecast(
        anchor, periods, _assumptions(growth=-0.20, margin=0.15, nowc_ratio=0.01)
    )
    assert result.forecast_revenue == pytest.approx(anchor.revenue * 0.80)
    assert result.change_in_nowc < 0  # NOWC release


def test_zero_forecast_revenue_allowed():
    anchor, periods, _ = _anchor()
    result = compute_one_year_operating_forecast(
        anchor, periods, _assumptions(growth=-1.0, margin=0.10, nowc_ratio=0.05)
    )
    assert result.forecast_revenue == pytest.approx(0.0)
    assert result.forecast_nopat == pytest.approx(0.0)
    assert result.closing_nowc == pytest.approx(0.0)
    assert result.change_in_nowc == pytest.approx(-anchor.nowc)


def test_negative_margin_and_negative_nowc_intensity():
    anchor, periods, _ = _anchor()
    result = compute_one_year_operating_forecast(
        anchor, periods, _assumptions(growth=0.05, margin=-0.08, nowc_ratio=-0.02)
    )
    assert result.forecast_nopat < 0
    assert result.closing_nowc < 0
    assert result.forecast_nopat == pytest.approx(result.forecast_revenue * -0.08)
    assert result.closing_nowc == pytest.approx(result.forecast_revenue * -0.02)


def test_rejects_growth_below_minus_100_percent():
    anchor, periods, _ = _anchor()
    with pytest.raises(ValueError, match="-100%"):
        compute_one_year_operating_forecast(
            anchor, periods, _assumptions(growth=-1.01)
        )


def test_rejects_nonpositive_opening_revenue():
    fin = _base_fin(
        income_statement=[
            _li("Revenue", 1000, 0),
            _li("Finance costs", -10, -11),
            _li("Finance income", 0, 0),
            _li("Profit before tax", 200, 220),
            _li("Income tax expense", -30, -33),
            _li("Profit for the year", 170, 187),
        ]
    )
    anchor, periods, _ = _anchor(fin)
    with pytest.raises(ValueError, match="opening revenue must be positive"):
        compute_one_year_operating_forecast(anchor, periods, _assumptions())


def test_rejects_missing_and_invalid_assumptions():
    anchor, periods, _ = _anchor()
    with pytest.raises(ValueError, match="missing required forecast assumptions"):
        compute_one_year_operating_forecast(anchor, periods, None)  # type: ignore[arg-type]

    bad = _assumptions()
    object.__setattr__(
        bad,
        "revenue_growth",
        ForecastDriverAssumption(value=float("nan"), origin="supplied", explanation="x"),
    )
    with pytest.raises(ValueError, match="finite"):
        compute_one_year_operating_forecast(anchor, periods, bad)

    empty_expl = OperatingForecastAssumptions(
        revenue_growth=_driver(0.1, explanation="   "),
        nopat_margin=_driver(0.2),
        nowc_to_revenue=_driver(0.05),
    )
    with pytest.raises(ValueError, match="explanation"):
        compute_one_year_operating_forecast(anchor, periods, empty_expl)

    bad_origin = OperatingForecastAssumptions(
        revenue_growth=ForecastDriverAssumption(
            value=0.1, origin="model", explanation="x"  # type: ignore[arg-type]
        ),
        nopat_margin=_driver(0.2),
        nowc_to_revenue=_driver(0.05),
    )
    with pytest.raises(ValueError, match="origin"):
        compute_one_year_operating_forecast(anchor, periods, bad_origin)


def test_rejects_empty_mismatched_and_nonannual_axes():
    anchor, periods, _ = _anchor()
    with pytest.raises(ValueError, match="empty"):
        compute_one_year_operating_forecast(anchor, [], _assumptions())

    with pytest.raises(ValueError, match="length mismatch"):
        compute_one_year_operating_forecast(anchor, periods[:-1], _assumptions())

    gap_year = [date(2024, 12, 31), date(2026, 12, 31)]
    with pytest.raises(ValueError, match="contiguous annual"):
        compute_one_year_operating_forecast(anchor, gap_year, _assumptions())

    same_year = [date(2024, 6, 30), date(2024, 12, 31)]
    with pytest.raises(ValueError, match="contiguous annual"):
        compute_one_year_operating_forecast(anchor, same_year, _assumptions())

    with pytest.raises(ValueError, match="chronological"):
        compute_one_year_operating_forecast(
            anchor, list(reversed(periods)), _assumptions()
        )


def test_unavailable_comparators_preserved():
    # Single annual period: Sales Growth unavailable (None), margin/NOWC available.
    d1 = date(2025, 12, 31)
    fin = StandardizedFinancials(
        ticker="OF1",
        company_name="OF One",
        currency="HKD",
        units="HKD mn",
        jurisdiction="HK",
        periods=[FinancialPeriod(end_date=d1, label="FY2025")],
        income_statement=[
            LineItem(label="Revenue", values={d1: 1000}),
            LineItem(label="Finance costs", values={d1: -10}),
            LineItem(label="Finance income", values={d1: 0}),
            LineItem(label="Profit before tax", values={d1: 200}),
            LineItem(label="Income tax expense", values={d1: -30}),
            LineItem(label="Profit for the year", values={d1: 170}),
        ],
        balance_sheet=[
            LineItem(label="Cash and cash equivalents", values={d1: 100}),
            LineItem(label="Trade receivables", values={d1: 80}),
            LineItem(label="Property, plant and equipment", values={d1: 400}),
            LineItem(label="Trade payables", values={d1: 50}),
            LineItem(label="Bank borrowings", values={d1: 200}),
            LineItem(label="Total equity", values={d1: 330}),
        ],
        cash_flow=[
            LineItem(label="Net cash from operating activities", values={d1: 50})
        ],
    )
    periods = list(canonical_fiscal_periods(fin))
    anchor = compute_anchor(fin, periods)
    result = compute_one_year_operating_forecast(anchor, periods, _assumptions())
    assert result.comparators.sales_growth is None
    assert result.comparators.nopat_margin == pytest.approx(
        float(anchor.dupont["NOPAT Margin"][-1])
    )
    assert result.comparators.nowc_to_revenue == pytest.approx(
        anchor.nowc / anchor.revenue
    )
    # Comparators must not overwrite explicit assumptions
    assert result.assumptions.revenue_growth.value == pytest.approx(0.10)
    assert result.assumptions.nopat_margin.value == pytest.approx(0.20)


def test_period_labels_and_alignment():
    anchor, periods, fin = _anchor()
    labels = [p.label for p in fin.periods]
    result = compute_one_year_operating_forecast(
        anchor,
        periods,
        _assumptions(),
        historical_period_labels=labels,
        forecast_period_label="FY2026E",
    )
    assert result.historical_period_label == "FY2025"
    assert result.forecast_period_label == "FY2026E"
    with pytest.raises(ValueError, match="historical_period_labels"):
        compute_one_year_operating_forecast(
            anchor, periods, _assumptions(), historical_period_labels=labels[:-1]
        )


def test_input_immutability():
    anchor, periods, _ = _anchor()
    before_rev = copy.deepcopy(anchor.historical.revenue)
    before_nowc = copy.deepcopy(list(anchor.reformulation.nowc))
    before_dupont = copy.deepcopy(anchor.dupont)
    before_periods = list(periods)
    compute_one_year_operating_forecast(anchor, periods, _assumptions())
    assert anchor.historical.revenue == before_rev
    assert list(anchor.reformulation.nowc) == before_nowc
    assert anchor.dupont == before_dupont
    assert periods == before_periods


def test_classification_conditioned_opening_nowc():
    fin = _base_fin()
    periods = list(canonical_fiscal_periods(fin))
    base = compute_anchor(fin, periods)
    # Reclassify cash as operating WC asset → higher NOWC
    alt = compute_anchor(
        fin,
        periods,
        classification_overrides={
            "label:Cash and cash equivalents": "Operating Working Capital Asset",
        },
    )
    assert alt.nowc != pytest.approx(base.nowc)
    result_base = compute_one_year_operating_forecast(
        base, periods, _assumptions(nowc_ratio=0.10)
    )
    result_alt = compute_one_year_operating_forecast(
        alt, periods, _assumptions(nowc_ratio=0.10)
    )
    assert result_base.opening_nowc == pytest.approx(base.nowc)
    assert result_alt.opening_nowc == pytest.approx(alt.nowc)
    assert result_alt.change_in_nowc != pytest.approx(result_base.change_in_nowc)


def test_demo_fixture_illustrative_assumptions():
    fin = _ingest_demo()
    periods = list(canonical_fiscal_periods(fin))
    anchor = compute_anchor(fin, periods)
    labels = [p.label for p in fin.periods if p.end_date in set(periods)]
    # Explicit illustrative drivers — not copied from historical comparators.
    assumptions = OperatingForecastAssumptions(
        revenue_growth=_driver(
            0.08,
            origin="supplied",
            explanation="illustrative DEMO next-year revenue growth 8%",
        ),
        nopat_margin=_driver(
            0.30,
            origin="supplied",
            explanation="illustrative DEMO after-tax NOPAT margin 30%",
        ),
        nowc_to_revenue=_driver(
            0.11,
            origin="learner",
            explanation="illustrative DEMO closing NOWC/revenue 11%",
        ),
    )
    result = compute_one_year_operating_forecast(
        anchor,
        periods,
        assumptions,
        historical_period_labels=labels,
    )
    assert result.historical_period_label == "FY2025"
    assert result.forecast_period_label == "FY2026"
    assert result.opening_revenue == pytest.approx(12500.0)
    assert result.forecast_revenue == pytest.approx(12500.0 * 1.08)
    assert result.forecast_nopat == pytest.approx(result.forecast_revenue * 0.30)
    assert result.closing_nowc == pytest.approx(result.forecast_revenue * 0.11)
    wc = compute_working_capital_series(anchor)
    assert result.comparators.nowc_to_revenue == pytest.approx(
        float(wc.nowc_to_revenue[-1])
    )
    assert result.comparators.sales_growth == pytest.approx(
        float(anchor.dupont["Sales Growth"][-1])
    )
    # Historical comparator must differ from explicit growth assumption here
    assert result.assumptions.revenue_growth.value != pytest.approx(
        float(result.comparators.sales_growth)
    )


def test_fast_retailing_fixture_illustrative_assumptions():
    payload = json.loads(FR_STD.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    periods = list(canonical_fiscal_periods(fin))
    anchor = compute_anchor(fin, periods)
    labels = [p.label for p in fin.periods if not p.is_interim]
    assumptions = OperatingForecastAssumptions(
        revenue_growth=_driver(
            0.05,
            origin="supplied",
            explanation="illustrative Fast Retailing next-year revenue growth 5%",
        ),
        nopat_margin=_driver(
            0.12,
            origin="supplied",
            explanation="illustrative Fast Retailing after-tax NOPAT margin 12%",
        ),
        nowc_to_revenue=_driver(
            0.01,
            origin="learner",
            explanation="illustrative Fast Retailing closing NOWC/revenue 1%",
        ),
    )
    result = compute_one_year_operating_forecast(
        anchor,
        periods,
        assumptions,
        historical_period_labels=labels,
    )
    assert result.historical_period == date(2025, 8, 31)
    assert result.forecast_period == date(2026, 8, 31)
    assert result.opening_revenue == pytest.approx(anchor.revenue)
    assert result.forecast_revenue == pytest.approx(anchor.revenue * 1.05)
    assert result.forecast_nopat == pytest.approx(result.forecast_revenue * 0.12)
    assert result.closing_nowc == pytest.approx(result.forecast_revenue * 0.01)
    assert math.isfinite(result.change_in_nowc)
    assert result.comparators.nopat_margin == pytest.approx(
        float(anchor.dupont["NOPAT Margin"][-1])
    )
