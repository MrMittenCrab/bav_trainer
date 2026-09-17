"""Step 9M.2.4.1.1.1.50 — store-count workbook schedule and learner/Check."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from core.data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    HistoricalOperatingKpiData,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.engine.component_catalog import (
    STORE_COUNT_COMPONENT_CATALOG,
    STORE_COUNT_POPULATION_LABEL,
    STORE_COUNT_SHEET_NAME,
    expand_store_count_specs,
    store_count_component_id,
)
from core.engine.reference_model import (
    JUDGMENT_SHEET,
    STORE_COUNT_SHEET,
    ReferenceModelBuilder,
)
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.management_kpi import management_admission_payload
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.historical_expected import operating_kpi_expected_value_for_component
from core.model.line_resolver import MissingLineError
from core.model.management_kpi import compute_management_kpi_series, management_kpi_applicable
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.operating_kpi_relationships import (
    compute_operating_kpi_revenue_comparable_sales_relationship,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_comparable_sales_relationship_applicable,
    operating_kpi_revenue_store_relationship_applicable,
)
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO
from core.tests.test_capex import P1, P2, _tiny
from core.tests.test_learner_ready_presentation import (
    WHITE_RGBS,
    _assert_answer_key_no_yellow,
    _assert_fresh_visible_style,
    _judgment_response_keys,
)
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    _bytes_by_name,
    _canonicalize,
    _copy_json,
    _statement_provenance,
)
from core.tests.test_management_kpi_history import _reconcile
from core.tests.test_normalization import _inject_formula_and_cached_value
from core.tests.test_operating_kpi_analysis import (
    _analysis_management_obs,
    _assert_series_matches,
    _independent_from_counts,
    _reload_admitted_store_histories,
)
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2022,
    P2023,
    P2024,
    P2025,
    P2026,
    _kpi_model_observation,
    _validated_augmented,
)
from core.ingestion.management_kpi_identity import FAMILY_COMPARABLE_SALES_GROWTH
from core.trainer.checker import (
    BLANK_RGB,
    CORRECT_RGB,
    INCORRECT_RGB,
    check_workbook,
)
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
LULU_JSON = ROOT / "benchmark" / "lululemon" / "reconciled" / "standardized.json"
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"
P0 = date(2023, 12, 31)
LEASE_DT_LULULEMON_SPECS = 486
FAST_RETAILING_SPECS = 577
GEOGRAPHIC_LULULEMON_SPECS = 74
STORE_COUNT_LULULEMON_SPECS = 8
LULULEMON_UNAVAILABLE_DISPLAYS = 101
STORE_A2 = (
    "Source-supported company-operated period-end store counts with "
    "adjacent net count change and count growth. Changes are net "
    "count changes, not openings or closures."
)
STORE_A4 = (
    "Opening change and growth are not practiced. A missing adjacent "
    "snapshot remains unavailable. Count units stay independent of "
    "monetary scale."
)
_DISCLOSED_STORE_ARITHMETIC = (
    "(current − prior) / prior",
    "(current - prior) / prior",
    "gross openings",
    "gross closures",
)


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _attach_stores(fin, *observations, management=None):
    fin.historical_operating_kpis = HistoricalOperatingKpiData(
        observations=list(observations),
        management_observations=list(management or ()),
    )
    return fin


def _store_tiny(
    *observations,
    extra_opening: date | None = None,
    management=None,
    units: str | None = None,
    single_period: bool = False,
):
    fin = _tiny(with_payments=False, single_period=single_period)
    if extra_opening is not None:
        fin.periods.insert(
            0, FinancialPeriod(end_date=extra_opening, label="FY2023")
        )
        for item in (
            *fin.income_statement,
            *fin.balance_sheet,
            *fin.cash_flow,
        ):
            first = fin.periods[1].end_date
            if first in item.values:
                item.values[extra_opening] = item.values[first]
    if units is not None:
        fin.units = units
    if observations or management:
        _attach_stores(fin, *observations, management=management)
    return fin


def _row_by_label(ws, label: str) -> int:
    for row in range(1, (ws.max_row or 1) + 1):
        if ws.cell(row, 1).value == label:
            return row
    raise AssertionError(f"missing store-count label {label!r}")


def _visible_cell_texts(wb) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        max_row = ws.max_row or 1
        max_col = ws.max_column or 1
        for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
            for cell in row:
                value = cell.value
                if isinstance(value, str) and not value.startswith("="):
                    found.append((ws.title, cell.coordinate, value))
                comment = cell.comment.text if cell.comment is not None else ""
                if comment:
                    found.append((ws.title, f"{cell.coordinate}#comment", comment))
    return found


def _assert_no_disclosed_store_arithmetic(wb) -> None:
    for sheet, coord, text in _visible_cell_texts(wb):
        lowered = text.lower()
        for fragment in _DISCLOSED_STORE_ARITHMETIC:
            assert fragment not in lowered, (
                f"{sheet}!{coord} discloses store-count practice arithmetic: {text!r}"
            )


def _store_answer_guidance() -> tuple[str, ...]:
    texts: list[str] = []
    for family in STORE_COUNT_COMPONENT_CATALOG:
        if family.short_hint:
            texts.append(family.short_hint)
        texts.extend(family.hints)
    return tuple(texts)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_pair(trainer: Path, answer: Path, dest: Path) -> tuple[Path, Path]:
    dest.mkdir()
    copied_trainer = dest / trainer.name
    copied_answer = dest / answer.name
    shutil.copy2(trainer, copied_trainer)
    shutil.copy2(answer, copied_answer)
    for sidecar in (
        answer.with_suffix(".component_map.json"),
        answer.with_suffix(".assumptions.json"),
        answer.with_suffix(".trainer.json"),
    ):
        if sidecar.is_file():
            shutil.copy2(sidecar, dest / sidecar.name)
    return copied_trainer, copied_answer


def _assert_visible_parity(
    trainer: Path,
    answer: Path,
    practice_cells: set[tuple[str, str]] | None = None,
) -> None:
    twb = load_workbook(trainer, data_only=False)
    awb = load_workbook(answer, data_only=False)
    skip = set(practice_cells or ())
    skip |= _judgment_response_keys(twb)
    skip |= _judgment_response_keys(awb)
    t_visible = [ws.title for ws in twb.worksheets if ws.sheet_state == "visible"]
    a_visible = [ws.title for ws in awb.worksheets if ws.sheet_state == "visible"]
    assert t_visible == a_visible
    for name in t_visible:
        tws = twb[name]
        aws = awb[name]
        max_row = max(tws.max_row or 1, aws.max_row or 1)
        max_col = max(tws.max_column or 1, aws.max_column or 1)
        for row in range(1, max_row + 1):
            for col in range(1, max_col + 1):
                tcell = tws.cell(row, col)
                acell = aws.cell(row, col)
                if (name, tcell.coordinate) in skip:
                    continue
                assert tcell.value == acell.value, f"{name}!{tcell.coordinate}"
                t_note = tcell.comment.text if tcell.comment is not None else None
                a_note = acell.comment.text if acell.comment is not None else None
                assert t_note == a_note, f"{name}!{tcell.coordinate} note"
    twb.close()
    awb.close()


def test_catalog_orders_and_expand_identities():
    assert STORE_COUNT_SHEET == STORE_COUNT_SHEET_NAME
    assert [family.order for family in STORE_COUNT_COMPONENT_CATALOG] == [161, 162]
    assert [family.id for family in STORE_COUNT_COMPONENT_CATALOG] == [
        "store_count_net_change",
        "store_count_growth",
    ]
    specs = expand_store_count_specs(
        [P1, P2],
        start_order=10,
        change_periods=(P2,),
        growth_periods=(P2,),
    )
    assert [s.id for s in specs] == [
        store_count_component_id("store_count_net_change", P2),
        store_count_component_id("store_count_growth", P2),
    ]
    assert not any(s.period_end == P1.isoformat() for s in specs)
    with pytest.raises(ValueError, match="duplicate fiscal periods"):
        expand_store_count_specs(
            [P1, P1],
            start_order=1,
            change_periods=(),
            growth_periods=(),
        )
    with pytest.raises(ValueError, match="strictly chronological"):
        expand_store_count_specs(
            [P2, P1],
            start_order=1,
            change_periods=(P2,),
            growth_periods=(P2,),
        )


def test_absent_null_and_management_only_add_no_schedule(tmp_path):
    absent = _tiny(with_payments=False)
    assert not operating_kpi_applicable(absent)
    builder = ReferenceModelBuilder(absent)
    assert builder.operating_kpi_series is None
    assert builder.operating_kpi_specs == ()
    trainer, answer = build_training_workbook(absent, tmp_path / "STORE_ABSENT.xlsx")
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert STORE_COUNT_SHEET not in wb.sheetnames
        wb.close()
    smap = load_semantic_map(answer)
    assert not any(c.category == "store_count" for c in smap.all_ordered())

    payload = standardized_to_payload(_tiny(with_payments=False))
    payload["historical_operating_kpis"] = None
    nulled = standardized_from_payload(payload)
    assert nulled.historical_operating_kpis is None
    assert ReferenceModelBuilder(nulled).operating_kpi_specs == ()

    management_only = _store_tiny(
        management=[
            _analysis_management_obs(
                family=FAMILY_COMPARABLE_SALES_GROWTH,
                period=P2,
                value=2.0,
            )
        ]
    )
    assert operating_kpi_applicable(management_only) is False
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(
        management_only
    ) is True
    mgmt_builder = ReferenceModelBuilder(management_only)
    assert mgmt_builder.operating_kpi_series is None
    assert mgmt_builder.operating_kpi_specs == ()
    trainer, answer = build_training_workbook(
        management_only, tmp_path / "STORE_MGMT.xlsx"
    )
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert STORE_COUNT_SHEET not in wb.sheetnames
        wb.close()
    assert not any(
        c.category == "store_count" for c in load_semantic_map(answer).all_ordered()
    )


def test_invalid_contract_fails_closed_without_mutation():
    fin = _store_tiny(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767))
    original = copy.deepcopy(fin.historical_operating_kpis)
    fin.historical_operating_kpis.observations[0].value = -1
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative integer"):
        ReferenceModelBuilder(fin)
    assert fin.historical_operating_kpis == mutated
    fin.historical_operating_kpis = copy.deepcopy(original)
    with pytest.raises(ValueError, match="canonical fiscal axis"):
        compute_operating_kpi_series(fin, [P2, P1])
    assert fin.historical_operating_kpis == original
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(_tiny(with_payments=False))


def test_workbook_gating_formulas_notes_check_and_families(tmp_path):
    fin = _store_tiny(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767))
    builder = ReferenceModelBuilder(fin)
    assert builder.operating_kpi_series is not None
    store_ids = {s.family_id for s in builder.operating_kpi_specs}
    assert store_ids == {f.id for f in STORE_COUNT_COMPONENT_CATALOG}
    existing = [
        s.id for s in builder.expected_specs if s.category != "store_count"
    ]
    assert existing
    trainer, answer = build_training_workbook(fin, tmp_path / "STORE_BASE.xlsx")
    smap = load_semantic_map(answer)
    store_comps = [c for c in smap.all_ordered() if c.category == "store_count"]
    assert {c.id for c in store_comps} == {s.id for s in builder.operating_kpi_specs}
    assert not any(c.period_index == 0 for c in store_comps)

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    assert STORE_COUNT_SHEET in awb.sheetnames
    assert STORE_COUNT_SHEET in twb.sheetnames
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    assert aws["A2"].value == STORE_A2
    assert tws["A2"].value == STORE_A2
    assert aws["A4"].value == STORE_A4
    assert tws["A4"].value == STORE_A4
    _assert_no_disclosed_store_arithmetic(twb)
    blob = "\n".join(text for _sheet, _coord, text in _visible_cell_texts(twb))
    for guidance in _store_answer_guidance():
        assert guidance.lower() not in blob.lower()

    count_row = _row_by_label(aws, "Company-operated period-end store count")
    unit_row = _row_by_label(aws, "Count unit")
    pop_row = _row_by_label(aws, "Population")
    change_row = _row_by_label(aws, "Net count change")
    growth_row = _row_by_label(aws, "Store-count growth")
    assert aws.cell(count_row, 2).value == 711
    assert tws.cell(count_row, 2).value == 711
    assert aws.cell(count_row, 3).value == 767
    assert tws.cell(count_row, 3).value == 767
    assert aws.cell(unit_row, 2).value == "stores"
    assert aws.cell(pop_row, 2).value == STORE_COUNT_POPULATION_LABEL
    assert aws.cell(change_row, 2).value == "N/A"
    assert tws.cell(change_row, 2).value == "N/A"
    assert aws.cell(growth_row, 2).value == "N/A"
    assert str(aws.cell(change_row, 3).value).replace(" ", "") == (
        f"={get_column_letter(3)}{count_row}-{get_column_letter(2)}{count_row}"
    ).replace(" ", "")
    assert "NA()" in str(aws.cell(growth_row, 3).value)
    assert tws.cell(change_row, 3).value in (None, "")
    assert tws.cell(growth_row, 3).comment is None
    change_note = (
        aws.cell(change_row, 3).comment.text or ""
        if aws.cell(change_row, 3).comment
        else ""
    )
    assert "net change" in change_note.lower()
    assert "openings" in change_note.lower()
    awb.close()
    twb.close()

    for comp in store_comps:
        looked = operating_kpi_expected_value_for_component(
            builder.operating_kpi_series, comp
        )
        if isinstance(looked, float) and isinstance(comp.expected_value, float):
            assert looked == pytest.approx(
                comp.expected_value, abs=OPERATING_KPI_RATIO_TOLERANCE
            )
        else:
            assert looked == comp.expected_value

    blank = check_workbook(trainer)
    assert blank.incorrect == 0
    assert blank.blank == blank.total
    assert blank.correct == 0

    wb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    assert filled.incorrect == 0
    assert filled.blank == 0

    bad = next(c for c in store_comps if c.family_id == "store_count_net_change")
    _inject_formula_and_cached_value(
        trainer,
        bad.tab,
        bad.cell,
        formula="=999",
        cached_value=999.0,
    )
    bad_summary = check_workbook(trainer)
    assert bad_summary.incorrect >= 1
    dumped = repr(bad_summary)
    assert "=999" not in dumped
    assert "Net count change" not in dumped


def test_sparse_undefined_decline_units_and_source_edit(tmp_path):
    fin = _store_tiny(
        _kpi_model_observation(P0, 0),
        _kpi_model_observation(P2, 10),
        extra_opening=P0,
    )
    builder = ReferenceModelBuilder(fin)
    series = builder.operating_kpi_series
    assert series is not None
    axis = canonical_fiscal_periods(fin)
    assert axis[0] == P0
    expected = _independent_from_counts(axis, {P0: 0, P2: 10})
    _assert_series_matches(series, expected)
    assert series.period_end_count[P1] == SOURCE_UNAVAILABLE
    assert series.net_count_change[P1] == SOURCE_UNAVAILABLE
    assert series.net_count_change[P2] == SOURCE_UNAVAILABLE
    assert series.growth[P1] == SOURCE_UNAVAILABLE
    assert not any(s.period_end == P0.isoformat() for s in builder.operating_kpi_specs)
    assert builder.operating_kpi_specs == ()

    decline = _store_tiny(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 655),
    )
    zero_open = _store_tiny(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 10),
    )
    stores = _store_tiny(
        _kpi_model_observation(P1, 711, unit="stores"),
        _kpi_model_observation(P2, 767, unit="stores"),
        units="USD in Thousands",
    )
    ones = _store_tiny(
        _kpi_model_observation(P1, 711, unit="ones"),
        _kpi_model_observation(P2, 767, unit="ones"),
        units="USD in Millions",
    )
    decline_series = compute_operating_kpi_series(decline)
    zero_series = compute_operating_kpi_series(zero_open)
    assert decline_series.net_count_change[P2] == -56
    assert zero_series.growth[P2] == UNDEFINED_RATIO
    assert compute_operating_kpi_series(stores).period_end_count == (
        compute_operating_kpi_series(ones).period_end_count
    )
    restored_ones = standardized_from_payload(standardized_to_payload(ones))
    assert compute_operating_kpi_series(restored_ones).unit[P1] == "ones"

    trainer, answer = build_training_workbook(fin, tmp_path / "STORE_SPARSE.xlsx")
    awb = load_workbook(answer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    count_row = _row_by_label(aws, "Company-operated period-end store count")
    change_row = _row_by_label(aws, "Net count change")
    growth_row = _row_by_label(aws, "Store-count growth")
    assert aws.cell(count_row, 2).value == 0
    assert aws.cell(count_row, 3).value == SOURCE_UNAVAILABLE
    assert aws.cell(change_row, 2).value == "N/A"
    assert aws.cell(change_row, 3).value == SOURCE_UNAVAILABLE
    assert aws.cell(growth_row, 4).value == SOURCE_UNAVAILABLE
    awb.close()

    zero_trainer, zero_answer = build_training_workbook(
        zero_open, tmp_path / "STORE_ZERO.xlsx"
    )
    zawb = load_workbook(zero_answer, data_only=False)
    zaws = zawb[STORE_COUNT_SHEET]
    z_growth = _row_by_label(zaws, "Store-count growth")
    assert "NA()" in str(zaws.cell(z_growth, 3).value)
    zawb.close()
    decline_trainer, decline_answer = build_training_workbook(
        decline, tmp_path / "STORE_DECLINE.xlsx"
    )
    dmap = load_semantic_map(decline_answer)
    change = next(
        c for c in dmap.all_ordered() if c.family_id == "store_count_net_change"
    )
    assert change.expected_value == -56

    source_row = _row_by_label(
        load_workbook(answer, data_only=False)[STORE_COUNT_SHEET],
        "Company-operated period-end store count",
    )
    wb = load_workbook(trainer, data_only=False)
    wb[STORE_COUNT_SHEET].cell(source_row, 2).value = 1
    wb.save(trainer)
    wb.close()
    with pytest.raises(
        ValueError,
        match="Trusted workbook cell was modified: Store Count Analysis",
    ):
        check_workbook(trainer)

    ones_trainer, ones_answer = build_training_workbook(
        restored_ones, tmp_path / "STORE_ONES.xlsx"
    )
    oawb = load_workbook(ones_answer, data_only=False)
    oaws = oawb[STORE_COUNT_SHEET]
    assert oaws.cell(_row_by_label(oaws, "Count unit"), 2).value == "ones"
    oawb.close()
    assert Path(zero_trainer).is_file()
    assert Path(decline_trainer).is_file()
    assert Path(ones_trainer).is_file()


def test_singleton_history_has_counts_without_practice(tmp_path):
    fin = _store_tiny(_kpi_model_observation(P2, 811), single_period=True)
    builder = ReferenceModelBuilder(fin)
    assert builder.operating_kpi_series is not None
    assert builder.operating_kpi_series.period_end_count[P2] == 811
    assert builder.operating_kpi_series.net_count_change[P2] is None
    assert builder.operating_kpi_specs == ()
    trainer, answer = build_training_workbook(fin, tmp_path / "STORE_SINGLE.xlsx")
    smap = load_semantic_map(answer)
    assert not any(c.category == "store_count" for c in smap.all_ordered())
    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    assert STORE_COUNT_SHEET in awb.sheetnames
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    count_row = _row_by_label(aws, "Company-operated period-end store count")
    assert aws.cell(count_row, 2).value == 811
    assert tws.cell(count_row, 2).value == 811
    assert aws.cell(_row_by_label(aws, "Net count change"), 2).value == "N/A"
    awb.close()
    twb.close()
    blank = check_workbook(trainer)
    assert blank.incorrect == 0


def test_committed_lululemon_and_fast_retailing_identities_unchanged():
    lulu = standardized_from_payload(json.loads(LULU_JSON.read_text(encoding="utf-8")))
    assert lulu.historical_operating_kpis is None
    lulu_builder = ReferenceModelBuilder(lulu)
    assert lulu_builder.operating_kpi_specs == ()
    assert len(lulu_builder.expected_specs) == LEASE_DT_LULULEMON_SPECS

    fr = standardized_from_payload(json.loads(FR_JSON.read_text(encoding="utf-8")))
    assert fr.historical_operating_kpis is None
    fr_builder = ReferenceModelBuilder(fr)
    assert fr_builder.operating_kpi_specs == ()
    assert len(fr_builder.expected_specs) == FAST_RETAILING_SPECS

    demo = HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )
    assert not operating_kpi_applicable(demo)
    assert ReferenceModelBuilder(demo).operating_kpi_specs == ()


def test_source_grounded_reload_workbook_and_check(tmp_path):
    _dest, validated = _validated_augmented(tmp_path)
    reloads = _reload_admitted_store_histories(validated)
    reconciled, fin, restored = reloads[0]
    assert restored.historical_operating_kpis == fin.historical_operating_kpis
    series = compute_operating_kpi_series(restored)
    expected = _independent_from_counts(
        list(series.periods),
        {period: float(value) for period, value in INDEPENDENT_STORE_TOTALS.items()},
    )
    _assert_series_matches(series, expected)
    assert [series.period_end_count[period] for period in series.periods] == [
        574,
        655,
        711,
        767,
        811,
    ]
    assert [series.net_count_change[period] for period in series.periods] == [
        None,
        81,
        56,
        56,
        44,
    ]
    assert len(reconciled.selected_geographic_facts) == 56

    builder = ReferenceModelBuilder(restored)
    store_n = len(builder.operating_kpi_specs)
    assert store_n == STORE_COUNT_LULULEMON_SPECS
    preserved = [s for s in builder.expected_specs if s.category != "store_count"]
    committed = ReferenceModelBuilder(
        standardized_from_payload(json.loads(LULU_JSON.read_text(encoding="utf-8")))
    ).expected_specs
    assert {s.id for s in preserved if s.category != "geographic_segment"} == {
        s.id for s in committed
    }
    geo_n = len([s for s in builder.expected_specs if s.category == "geographic_segment"])
    assert geo_n == GEOGRAPHIC_LULULEMON_SPECS
    assert len(preserved) == LEASE_DT_LULULEMON_SPECS + GEOGRAPHIC_LULULEMON_SPECS

    trainer, answer = build_training_workbook(
        restored, tmp_path / "LULU_STORE_TMP.xlsx"
    )
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened")
    smap = load_semantic_map(answer)
    all_comps = list(smap.all_ordered())
    store_comps = [c for c in all_comps if c.category == "store_count"]
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    assert len(all_comps) == (
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS
    )
    practice = {(c.tab, c.cell) for c in all_comps}

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    assert aws["A2"].value == STORE_A2
    assert tws["A4"].value == STORE_A4
    _assert_no_disclosed_store_arithmetic(twb)
    count_row = _row_by_label(aws, "Company-operated period-end store count")
    period_cols = {period: 2 + index for index, period in enumerate(builder.periods)}
    for period, value in INDEPENDENT_STORE_TOTALS.items():
        col_idx = period_cols[period]
        assert aws.cell(count_row, col_idx).value == value
        assert tws.cell(count_row, col_idx).value == value
    change_row = _row_by_label(aws, "Net count change")
    growth_row = _row_by_label(aws, "Store-count growth")
    assert aws.cell(change_row, period_cols[P2022]).value == "N/A"
    assert tws.cell(growth_row, period_cols[P2022]).value == "N/A"
    for period, change in (
        (P2023, 81),
        (P2024, 56),
        (P2025, 56),
        (P2026, 44),
    ):
        col_idx = period_cols[period]
        col = get_column_letter(col_idx)
        prev = get_column_letter(col_idx - 1)
        change_comp = next(
            c
            for c in store_comps
            if c.family_id == "store_count_net_change"
            and c.period_end == period.isoformat()
        )
        growth_comp = next(
            c
            for c in store_comps
            if c.family_id == "store_count_growth"
            and c.period_end == period.isoformat()
        )
        assert change_comp.expected_value == change
        assert growth_comp.expected_value == pytest.approx(
            series.growth[period], abs=OPERATING_KPI_RATIO_TOLERANCE
        )
        assert change_comp.formula.replace(" ", "") == (
            f"={col}{count_row}-{prev}{count_row}"
        )
        assert growth_comp.formula.replace(" ", "") == (
            f"=IF({prev}{count_row}=0,NA(),({col}{count_row}-{prev}{count_row})/"
            f"{prev}{count_row})"
        )
        t_change = twb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        a_change = awb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        assert t_change.value is None
        assert t_change.comment is None
        assert _fill_rgb(t_change) == "FFFF00"
        assert a_change.value == change_comp.formula
        assert _fill_rgb(a_change) in WHITE_RGBS
        assert (a_change.comment.text or "").strip()
        assert "cause" not in (a_change.comment.text or "").lower()

    awb.close()
    twb.close()
    _assert_visible_parity(trainer, answer, practice)
    _assert_fresh_visible_style(trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer)

    twb = load_workbook(trainer, data_only=False)
    awb = load_workbook(answer, data_only=False)
    assert JUDGMENT_SHEET in twb.sheetnames
    twb.close()
    awb.close()
    assert _count_source_unavailable(trainer) == LULULEMON_UNAVAILABLE_DISPLAYS
    assert _count_source_unavailable(answer) == LULULEMON_UNAVAILABLE_DISPLAYS

    answer_hash = _sha256(answer)
    blank = check_workbook(trainer)
    assert (blank.total, blank.blank, blank.correct, blank.incorrect) == (
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS,
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS,
        0,
        0,
    )
    dumped_blank = repr(blank)
    assert "(current − prior) / prior" not in dumped_blank.lower()
    assert "Net count change" not in dumped_blank

    filled_trainer, filled_answer = _copy_pair(
        trainer, answer, tmp_path / "filled_check"
    )
    wb = load_workbook(filled_trainer, data_only=False)
    for comp in all_comps:
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(filled_trainer)
    wb.close()
    filled = check_workbook(filled_trainer)
    total = (
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS
    )
    assert (filled.total, filled.correct, filled.incorrect, filled.blank) == (
        total,
        total,
        0,
        0,
    )

    incorrect_trainer, _incorrect_answer = _copy_pair(
        filled_trainer, filled_answer, tmp_path / "incorrect_check"
    )
    bad = next(
        c
        for c in store_comps
        if c.family_id == "store_count_growth" and c.period_end == P2026.isoformat()
    )
    _inject_formula_and_cached_value(
        incorrect_trainer,
        bad.tab,
        bad.cell,
        formula="=999",
        cached_value=999.0,
    )
    bad_summary = check_workbook(incorrect_trainer)
    assert bad_summary.incorrect == 1
    assert bad_summary.correct == bad_summary.total - 1
    assert bad_summary.blank == 0
    dumped = repr(bad_summary)
    assert "=999" not in dumped
    assert bad.formula not in dumped
    assert _sha256(answer) == answer_hash
    assert _sha256(filled_answer) == answer_hash


def _count_source_unavailable(path: Path) -> int:
    wb = load_workbook(path, data_only=False)
    n = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value == SOURCE_UNAVAILABLE:
                    n += 1
    wb.close()
    return n


def test_supplied_deferred_documents_do_not_activate_schedule(tmp_path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_rec = _reconcile(mixed, admit=ADMIT_2022)
    annual_rec = _reconcile(annual, admit=ADMIT_2022)
    mixed_fin = standardize_reconciled(mixed_rec)
    annual_fin = standardize_reconciled(annual_rec)
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None
    assert operating_kpi_applicable(mixed_fin) is False
    assert ReferenceModelBuilder(mixed_fin).operating_kpi_specs == ()
    assert ReferenceModelBuilder(annual_fin).operating_kpi_specs == ()
    trainer, answer = build_training_workbook(
        mixed_fin, tmp_path / "STORE_DEFERRED.xlsx"
    )
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert STORE_COUNT_SHEET not in wb.sheetnames
        wb.close()
    admission = management_admission_payload(mixed_rec.management_admission)
    assert admission["reported_observation_count"] == 135
    assert admission["definition_count"] == 9
    assert admission["market_table_observation_count"] == 107
    assert admission["target_count"] == 3
    reported_by_year = [
        sum(
            1
            for item in admission["observations"]
            if item["kind"] == "reported_kpi" and item["filing_year"] == year
        )
        for year in (2022, 2023, 2024, 2025)
    ]
    assert reported_by_year == [29, 36, 37, 33]
    assessments = admission["assessments"]
    assert len(assessments["items"]) == 135
    assert assessments["supported_count"] == 28
    assert assessments["outside_scope_count"] == 107
    assert assessments["unsupported_variant_count"] == 0
    assert assessments["comparability_counts"]["comparable"] == 0
    assert assessments["comparability_counts"]["not_comparable"] == 22
    assert assessments["comparability_counts"]["unresolved"] == 6
    assert assessments["comparability_counts"]["outside_scope"] == 107
    recon = admission["reconciliation"]
    assert recon["pair_count"] == 24
    assert recon["outcome_counts"]["incompatible"] == 24
    assert recon["outcome_counts"]["singleton"] == 6
    assert recon["selected_count"] == 0
    assert recon["revision_links"] == []
    assert _canonicalize(standardized_to_payload(mixed_fin)) == _canonicalize(
        standardized_to_payload(annual_fin)
    )
    assert _statement_provenance(reconciliation_provenance_payload(mixed_rec)) == (
        _statement_provenance(reconciliation_provenance_payload(annual_rec))
    )
    assert reconciliation_conflicts_payload(mixed_rec) == (
        reconciliation_conflicts_payload(annual_rec)
    )
    assert _bytes_by_name(EXTRACTED) == before


def test_management_and_revenue_relationship_apis_unchanged(tmp_path):
    stores = (
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    store_only = _store_tiny(*stores)
    mixed = _store_tiny(
        *stores,
        management=[
            _analysis_management_obs(
                family=FAMILY_COMPARABLE_SALES_GROWTH,
                period=P2,
                value=2.0,
            )
        ],
    )
    assert operating_kpi_applicable(store_only) is True
    assert operating_kpi_revenue_store_relationship_applicable(store_only) is True
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(
        store_only
    ) is False
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(mixed) is True
    assert management_kpi_applicable(store_only) is False
    assert management_kpi_applicable(mixed) is True
    store = compute_operating_kpi_series(store_only)
    assert compute_operating_kpi_series(mixed).period_end_count == store.period_end_count
    compute_operating_kpi_revenue_store_relationship(store_only)
    compute_operating_kpi_revenue_comparable_sales_relationship(mixed)
    compute_management_kpi_series(mixed)
    trainer, answer = build_training_workbook(store_only, tmp_path / "STORE_API.xlsx")
    smap = load_semantic_map(answer)
    assert {c.family_id for c in smap.all_ordered() if c.category == "store_count"} == {
        "store_count_net_change",
        "store_count_growth",
    }
    assert operating_kpi_revenue_store_relationship_applicable(store_only) is True
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(
        store_only
    ) is False
