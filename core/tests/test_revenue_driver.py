"""Disclosure-led historical revenue-driver tests and workbook presentation."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.historical_strategy import (
    ROLE_OBJECTIVE,
    ROLE_OPERATING_USE,
    ROLE_STRATEGY,
    THEME_COMPARABLE_SALES,
    THEME_GEOGRAPHIC_GROWTH,
    THEME_PRODUCTIVITY,
    THEME_STORE_EXPANSION,
    HistoricalStrategyData,
    HistoricalStrategyDisclosure,
    load_strategy_disclosures,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.engine.component_catalog import (
    REVENUE_DRIVER_COMPSALES_DIFFERENCE_FAMILY_ID,
    REVENUE_DRIVER_COMPSALES_FAMILY_ID,
    REVENUE_DRIVER_COMPONENT_CATALOG,
    REVENUE_DRIVER_GEO_CONTRIBUTION_FAMILY_ID,
    REVENUE_DRIVER_REVENUE_GROWTH_FAMILY_ID,
    REVENUE_DRIVER_RPS_FAMILY_ID,
    REVENUE_DRIVER_SHEET_NAME,
    REVENUE_DRIVER_STORE_DIFFERENCE_FAMILY_ID,
    REVENUE_DRIVER_STORE_GROWTH_FAMILY_ID,
    SemanticCellRef,
    expand_revenue_driver_specs,
    resolve_revenue_driver_link_formula,
    revenue_driver_component_id,
)
from core.engine.reference_model import ReferenceModelBuilder
from core.model.line_resolver import MissingLineError
from core.model.period_axis import PeriodAxisError
from core.model.revenue_driver import (
    ADDITIONAL_SPSF,
    FAILED_COMPSALES,
    FAILED_SPSF_GROWTH,
    FAILED_STORE_GROWTH,
    SCOPE_NOTE,
    VERDICT_CONTRADICTED,
    VERDICT_INSUFFICIENT,
    VERDICT_MIXED,
    VERDICT_SUPPORTED,
    compute_revenue_driver_analysis,
    revenue_driver_applicable,
)
from core.tests.test_capex import P1, P2, _tiny
from core.tests.test_historical_segment import _corp_values, _snapshot
from core.tests.test_learner_ready_presentation import (
    _assert_answer_key_no_yellow,
    assert_bav_has_no_exercise_framing,
)
from core.tests.test_operating_kpi_facts import _kpi_model_observation
from core.tests.test_operating_kpi_management_history import _compsales
from core.tests.test_operating_kpi_relationships import _fin_with_relationship
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map
from core.trainer.workbook import build_training_workbook, derive_trainer_workbook

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
LULU_JSON = ROOT / "benchmark" / "lululemon" / "reconciled" / "standardized.json"
LULU_DISCLOSURES = (
    ROOT / "core" / "tests" / "fixtures" / "strategy" / "lululemon_management_disclosures.json"
)
P0 = date(2023, 12, 31)


def _disclosure(
    theme: str,
    *,
    role: str = ROLE_STRATEGY,
    text: str = "We open stores.",
    period: date = P2,
) -> HistoricalStrategyDisclosure:
    return HistoricalStrategyDisclosure(
        theme=theme,
        role=role,
        text=text,
        period=period,
        source_file="example.pdf",
        page_reference="Form 10-K p. 1",
        section="Item 1",
    )


def _with_strategy(fin, *disclosures: HistoricalStrategyDisclosure):
    fin.historical_strategy = HistoricalStrategyData(disclosures=disclosures)
    return fin


def _store_fin(
    counts: dict[date, float],
    revenue: dict[date, float | None],
    *disclosures: HistoricalStrategyDisclosure,
    management=None,
):
    observations = tuple(
        _kpi_model_observation(period, value) for period, value in counts.items()
    )
    fin = _fin_with_relationship(
        *observations,
        revenue=revenue,
        extra_periods=list(counts),
        management=management,
    )
    return _with_strategy(fin, *disclosures)


def test_catalog_orders_and_link_formulas():
    assert REVENUE_DRIVER_SHEET_NAME == "Revenue Driver Analysis"
    assert [family.order for family in REVENUE_DRIVER_COMPONENT_CATALOG] == list(
        range(177, 184)
    )
    assert [family.id for family in REVENUE_DRIVER_COMPONENT_CATALOG] == [
        REVENUE_DRIVER_STORE_GROWTH_FAMILY_ID,
        REVENUE_DRIVER_REVENUE_GROWTH_FAMILY_ID,
        REVENUE_DRIVER_STORE_DIFFERENCE_FAMILY_ID,
        REVENUE_DRIVER_COMPSALES_FAMILY_ID,
        REVENUE_DRIVER_COMPSALES_DIFFERENCE_FAMILY_ID,
        REVENUE_DRIVER_RPS_FAMILY_ID,
        REVENUE_DRIVER_GEO_CONTRIBUTION_FAMILY_ID,
    ]
    source = SemanticCellRef(
        id="src",
        semantic_key="operating_kpi.store_count.growth.2025-12-31",
        period_end=P2.isoformat(),
        cell="C12",
        tab="Store Count Analysis",
    )
    assert (
        resolve_revenue_driver_link_formula(source, from_tab=REVENUE_DRIVER_SHEET_NAME)
        == "='Store Count Analysis'!C12"
    )
    specs = expand_revenue_driver_specs(
        [P1, P2],
        start_order=1,
        store_growth_periods=(P2,),
    )
    assert [spec.id for spec in specs] == [
        revenue_driver_component_id(REVENUE_DRIVER_STORE_GROWTH_FAMILY_ID, P2)
    ]


def test_missing_disclosures_skip_analysis():
    fin = _fin_with_relationship(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 12),
        revenue={P1: 100.0, P2: 130.0},
    )
    assert fin.historical_strategy is None
    assert not revenue_driver_applicable(fin)
    with pytest.raises(MissingLineError, match="revenue-driver disclosures"):
        compute_revenue_driver_analysis(fin)
    payload = standardized_to_payload(fin)
    assert "historical_strategy" not in payload
    restored = standardized_from_payload(payload)
    assert restored.historical_strategy is None


def test_store_expansion_supported_mixed_contradicted_and_insufficient():
    supported = _store_fin(
        {P0: 10, P1: 12, P2: 15},
        {P0: 100.0, P1: 130.0, P2: 160.0},
        _disclosure(THEME_STORE_EXPANSION, role=ROLE_OBJECTIVE, text="We plan to open stores."),
    )
    result = compute_revenue_driver_analysis(supported)
    assert result.scope_note == SCOPE_NOTE
    assert result.calculation_kind == "analyst-derived"
    test = result.tests[0]
    assert test.theme == THEME_STORE_EXPANSION
    assert test.verdict == VERDICT_SUPPORTED
    assert test.sample_size == 2
    assert test.failed_requirement == ""
    assert any(item.role == ROLE_OBJECTIVE for item in test.disclosures)
    assert "not treated as achieved historical outcomes" in " ".join(test.limitations)
    assert "descriptive" in " ".join(test.limitations).lower()
    assert "divided by company-operated stores" in " ".join(test.identity_notes).lower()
    notes = " ".join(item.note for item in test.observations)
    assert "Both consolidated revenue and company-operated store counts grew." in notes

    mixed = _store_fin(
        {P0: 10, P1: 12, P2: 15},
        {P0: 100.0, P1: 130.0, P2: 120.0},
        _disclosure(THEME_STORE_EXPANSION),
    )
    mixed_test = compute_revenue_driver_analysis(mixed).tests[0]
    assert mixed_test.verdict == VERDICT_MIXED
    assert mixed_test.sample_size == 2
    assert any(
        "did not" in item.note for item in mixed_test.observations if item.consistent is False
    )

    contradicted = _store_fin(
        {P1: 10, P2: 12},
        {P1: 130.0, P2: 100.0},
        _disclosure(THEME_STORE_EXPANSION),
    )
    contradicted_test = compute_revenue_driver_analysis(contradicted).tests[0]
    assert contradicted_test.verdict == VERDICT_CONTRADICTED
    assert contradicted_test.sample_size == 1

    missing_history = _with_strategy(
        _tiny(with_payments=False),
        _disclosure(THEME_STORE_EXPANSION),
    )
    missing_test = compute_revenue_driver_analysis(missing_history).tests[0]
    assert missing_test.verdict == VERDICT_INSUFFICIENT
    assert missing_test.sample_size == 0
    assert missing_test.failed_requirement == FAILED_STORE_GROWTH


def test_missing_adjacent_inputs_do_not_force_a_verdict():
    fin = _store_fin(
        {P1: 10, P2: 12},
        {P1: 100.0, P2: None},
        _disclosure(THEME_STORE_EXPANSION),
    )
    test = compute_revenue_driver_analysis(fin).tests[0]
    assert test.verdict == VERDICT_INSUFFICIENT
    assert test.sample_size == 0
    assert test.observations[0].consistent is None
    assert test.failed_requirement == FAILED_STORE_GROWTH


def test_comparable_sales_keeps_identities_and_descriptive_differences():
    fin = _store_fin(
        {P1: 10, P2: 12},
        {P1: 100.0, P2: 130.0},
        _disclosure(THEME_COMPARABLE_SALES, role=ROLE_OPERATING_USE),
        management=[
            _compsales(period=P1, value=4.0, geography="global", basis="reported"),
            _compsales(period=P2, value=5.0, geography="global", basis="reported"),
            _compsales(period=P2, value=1.5, geography="global", basis="constant_dollar"),
        ],
    )
    test = compute_revenue_driver_analysis(fin).tests[0]
    assert test.theme == THEME_COMPARABLE_SALES
    assert test.verdict == VERDICT_SUPPORTED
    identities = {item.inputs["identity"] for item in test.observations if item.inputs.get("identity")}
    assert identities
    bases = {item.inputs.get("basis") for item in test.observations if item.consistent is not None}
    assert "reported" in bases
    assert "constant_dollar" not in bases
    assert "ineligible" in " ".join(test.limitations).lower()
    assert "not new-store contribution" in " ".join(test.limitations).lower()
    round_trip = standardized_from_payload(standardized_to_payload(fin))
    assert round_trip.historical_strategy == fin.historical_strategy

    absent = _store_fin(
        {P1: 10, P2: 12},
        {P1: 100.0, P2: 130.0},
        _disclosure(THEME_COMPARABLE_SALES),
    )
    absent_test = compute_revenue_driver_analysis(absent).tests[0]
    assert absent_test.verdict == VERDICT_INSUFFICIENT
    assert absent_test.failed_requirement == FAILED_COMPSALES


def test_productivity_insufficient_without_adjacent_spsf_growth():
    fin = _store_fin(
        {P1: 10, P2: 12},
        {P1: 100.0, P2: 130.0},
        _disclosure(THEME_PRODUCTIVITY, role=ROLE_OPERATING_USE),
    )
    test = compute_revenue_driver_analysis(fin).tests[0]
    assert test.verdict == VERDICT_INSUFFICIENT
    assert test.failed_requirement == FAILED_SPSF_GROWTH
    assert ADDITIONAL_SPSF in test.additional_evidence
    assert "divided by company-operated stores" in " ".join(test.identity_notes).lower()


def test_geographic_mixed_when_a_segment_subtracts():
    from core.tests.test_geographic_segment_workbook import _geo_tiny

    fin = _geo_tiny(
        _snapshot(P1, values=_corp_values(rev=(80.0, 25.0, 15.0))),
        _snapshot(P2, values=_corp_values(rev=(110.0, 15.0, 15.0))),
    )
    _with_strategy(fin, _disclosure(THEME_GEOGRAPHIC_GROWTH))
    test = compute_revenue_driver_analysis(fin).tests[0]
    assert test.theme == THEME_GEOGRAPHIC_GROWTH
    assert test.verdict == VERDICT_MIXED
    assert test.sample_size == 1
    assert "not organic, constant-currency, or causal" in " ".join(test.limitations)
    assert any("negatively" in item.note for item in test.observations)


def test_interim_axis_is_rejected_when_operating_history_exists():
    fin = _store_fin(
        {P1: 10, P2: 12},
        {P1: 100.0, P2: 130.0},
        _disclosure(THEME_STORE_EXPANSION),
    )
    for period in fin.periods:
        period.is_interim = True
    with pytest.raises(PeriodAxisError, match="annual fiscal periods"):
        compute_revenue_driver_analysis(fin)


def test_workbook_links_notes_trainer_check_and_skips_without_disclosures(tmp_path):
    fin = _tiny(with_payments=False)
    fin.historical_operating_kpis = _store_fin(
        {P1: 10, P2: 12},
        {P1: 1000.0, P2: 1100.0},
        _disclosure(THEME_STORE_EXPANSION, role=ROLE_OBJECTIVE),
        _disclosure(THEME_PRODUCTIVITY, role=ROLE_OPERATING_USE),
    ).historical_operating_kpis
    fin.historical_strategy = HistoricalStrategyData(
        disclosures=(
            _disclosure(THEME_STORE_EXPANSION, role=ROLE_OBJECTIVE),
            _disclosure(THEME_PRODUCTIVITY, role=ROLE_OPERATING_USE),
        )
    )
    trainer, answer = build_training_workbook(fin, tmp_path / "DRIVER.xlsx")
    smap = load_semantic_map(answer)
    families = {comp.family_id for comp in smap.all_ordered()}
    assert REVENUE_DRIVER_STORE_GROWTH_FAMILY_ID in families
    assert REVENUE_DRIVER_REVENUE_GROWTH_FAMILY_ID in families
    assert REVENUE_DRIVER_STORE_DIFFERENCE_FAMILY_ID in families
    assert REVENUE_DRIVER_RPS_FAMILY_ID in families
    awb = load_workbook(answer, data_only=False)
    assert REVENUE_DRIVER_SHEET_NAME in awb.sheetnames
    sheet = awb[REVENUE_DRIVER_SHEET_NAME]
    values = " ".join(
        str(cell.value or "")
        for row in sheet.iter_rows()
        for cell in row
    )
    assert "Analyst hypothesis" in values
    assert "Management statement" in values
    assert "We plan to open stores." not in values or "objective" in values.lower()
    assert "descriptive" in values.lower()
    assert "NOTES" in values
    assert "not new-store contribution" in values.lower() or "causal attribution" in values.lower()
    assert any(
        isinstance(cell.value, str) and cell.value.startswith("=")
        for row in sheet.iter_rows()
        for cell in row
    )
    awb.close()
    _assert_answer_key_no_yellow(answer)
    assert_bav_has_no_exercise_framing(answer)
    before = answer.read_bytes()
    derive_trainer_workbook(answer, trainer)
    assert answer.read_bytes() == before
    twb = load_workbook(trainer, data_only=False)
    tsheet = twb[REVENUE_DRIVER_SHEET_NAME]
    driver_comps = [c for c in smap.all_ordered() if c.family_id.startswith("revenue_driver_")]
    for comp in driver_comps:
        cell = twb[comp.tab][comp.cell]
        assert cell.value is None
        assert cell.comment is None
        assert cell.fill.fgColor.rgb in ("00FFFF00", "FFFFFF00")
    assert tsheet["A1"].value is not None
    twb.close()
    blank = check_workbook(trainer)
    assert blank.incorrect == 0
    assert blank.correct == 0
    assert blank.blank == blank.total

    skipped = ReferenceModelBuilder(_tiny(with_payments=False))
    assert skipped.revenue_driver_schedule is False
    assert skipped.revenue_driver_specs == ()


def test_protected_standardized_payloads_do_not_carry_strategy():
    lulu = standardized_from_payload(json.loads(LULU_JSON.read_text(encoding="utf-8")))
    fr = standardized_from_payload(json.loads(FR_JSON.read_text(encoding="utf-8")))
    assert lulu.historical_strategy is None
    assert fr.historical_strategy is None
    assert not revenue_driver_applicable(lulu)
    assert not revenue_driver_applicable(fr)
    assert ReferenceModelBuilder(fr).revenue_driver_schedule is False
    assert ReferenceModelBuilder(fr).revenue_driver_specs == ()


def test_lululemon_ordinary_disclosures_test_admitted_history(tmp_path):
    from core.current_build import prepare_company_input, resolve_company

    company = resolve_company("Lululemon")
    fin = prepare_company_input(company, tmp_path)
    fixture = load_strategy_disclosures(LULU_DISCLOSURES)
    assert fin.historical_strategy == fixture
    analysis = compute_revenue_driver_analysis(fin)
    by_theme = {test.theme: test for test in analysis.tests}
    assert set(by_theme) == {
        THEME_STORE_EXPANSION,
        THEME_COMPARABLE_SALES,
        THEME_PRODUCTIVITY,
        THEME_GEOGRAPHIC_GROWTH,
    }
    store = by_theme[THEME_STORE_EXPANSION]
    assert store.verdict == VERDICT_SUPPORTED
    assert store.sample_size == 4
    assert [period.isoformat() for period in store.periods_tested] == [
        "2023-01-29",
        "2024-01-28",
        "2025-02-02",
        "2026-02-01",
    ]
    latest = next(item for item in store.observations if item.period.isoformat() == "2026-02-01")
    assert latest.consistent is True
    assert "Store-count growth exceeded revenue growth" in latest.note
    assert "Period-end Revenue per Store declined" in latest.note
    assert any(item.role == ROLE_OBJECTIVE for item in store.disclosures)
    compsales = by_theme[THEME_COMPARABLE_SALES]
    assert compsales.verdict in {VERDICT_SUPPORTED, VERDICT_MIXED}
    assert "ineligible" in " ".join(compsales.limitations)
    identities = {
        str(item.inputs.get("identity"))
        for item in compsales.observations
        if item.inputs.get("identity")
    }
    assert any("store" in identity.lower() or "dtc" in identity.lower() or identity for identity in identities)
    productivity = by_theme[THEME_PRODUCTIVITY]
    assert productivity.verdict == VERDICT_INSUFFICIENT
    assert productivity.failed_requirement == FAILED_SPSF_GROWTH
    geographic = by_theme[THEME_GEOGRAPHIC_GROWTH]
    assert geographic.verdict == VERDICT_MIXED
    assert geographic.sample_size >= 1
    builder = ReferenceModelBuilder(fin)
    assert builder.revenue_driver_schedule is True
    assert builder.revenue_driver_specs
    exported = standardized_from_payload(standardized_to_payload(fin))
    assert exported.historical_strategy == fin.historical_strategy
