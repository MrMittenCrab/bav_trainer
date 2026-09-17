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
    STORE_COUNT_SOURCE_CATEGORY,
    STORE_COUNT_SOURCE_FAMILY_ID,
    StoreCountSourceRef,
    expand_store_count_source_specs,
    expand_store_count_specs,
    is_store_count_practice_identity,
    is_store_count_source_identity,
    resolve_store_count_growth_formula,
    resolve_store_count_net_change_formula,
    store_count_adjacent_source_ids,
    store_count_component_id,
    store_count_source_component_id,
    store_count_source_semantic_key,
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
from core.tests.test_historical_segment import _base_payload
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
from core.trainer.semantic_io import component_map_path_for, load_semantic_map, parse_cell_ref
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
STORE_COUNT_LULULEMON_SOURCES = 5
LULULEMON_UNAVAILABLE_DISPLAYS = 101
DEFAULT_STORE_COUNT_SOURCE_ROW = 10
MOVED_STORE_COUNT_SOURCE_PLACEMENT = {
    0: (32, 2),
    1: (40, 5),
    2: (32, 8),
    3: (40, 11),
    4: (32, 14),
}
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


def _practice_components(smap):
    return [c for c in smap.all_ordered() if is_store_count_practice_identity(c)]


def _source_components(smap):
    return [c for c in smap.all_ordered() if is_store_count_source_identity(c)]


def _practice_specs(specs):
    return [s for s in specs if is_store_count_practice_identity(s)]


def _source_specs(specs):
    return [s for s in specs if is_store_count_source_identity(s)]


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
    sources = expand_store_count_source_specs(
        [P1, P2],
        start_order=1,
        source_periods=(P1, P2),
        units={P1: "stores", P2: "stores"},
    )
    assert [s.id for s in sources] == [
        store_count_source_component_id(P1),
        store_count_source_component_id(P2),
    ]
    assert [s.semantic_key for s in sources] == [
        store_count_source_semantic_key(P1),
        store_count_source_semantic_key(P2),
    ]
    assert all(s.category == STORE_COUNT_SOURCE_CATEGORY for s in sources)
    assert all(s.depends_on == () for s in sources)
    assert all(s.family_id == STORE_COUNT_SOURCE_FAMILY_ID for s in sources)
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
    expected_deps = store_count_adjacent_source_ids([P1, P2], P2)
    assert expected_deps == (
        store_count_source_component_id(P2),
        store_count_source_component_id(P1),
    )
    assert all(s.depends_on == expected_deps for s in specs)
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
    with pytest.raises(ValueError, match="duplicate fiscal periods"):
        expand_store_count_source_specs(
            [P1, P1],
            start_order=1,
            source_periods=(P1,),
        )
    with pytest.raises(ValueError, match="outside the canonical axis"):
        expand_store_count_source_specs(
            [P1, P2],
            start_order=1,
            source_periods=(P0,),
        )
    with pytest.raises(ValueError, match="opening store-count period"):
        store_count_adjacent_source_ids([P1, P2], P1)


def test_formula_resolution_follows_mapped_source_identities():
    current = StoreCountSourceRef(
        id=store_count_source_component_id(P2),
        semantic_key=store_count_source_semantic_key(P2),
        period_end=P2.isoformat(),
        cell="E20",
        unit="stores",
    )
    prior = StoreCountSourceRef(
        id=store_count_source_component_id(P1),
        semantic_key=store_count_source_semantic_key(P1),
        period_end=P1.isoformat(),
        cell="B8",
        unit="stores",
    )
    assert current.cell != prior.cell
    assert current.cell[0] != chr(ord(prior.cell[0]) + 1)
    change = resolve_store_count_net_change_formula(current, prior)
    growth = resolve_store_count_growth_formula(current, prior)
    assert change == "=E20-B8"
    assert growth == "=IF(B8=0,NA(),(E20-B8)/B8)"
    reversed_change = resolve_store_count_net_change_formula(prior, current)
    assert reversed_change != change
    assert change.startswith("=")
    assert current.cell in change and prior.cell in change
    with pytest.raises(ValueError, match="current and prior source cells"):
        resolve_store_count_net_change_formula(
            StoreCountSourceRef("a", "a", P2.isoformat(), ""),
            prior,
        )


def _strict_base_payload() -> dict:
    return copy.deepcopy(_base_payload())


def test_strict_metadata_jurisdiction_fallback_contract():
    demo = json.loads(DEMO_JSON.read_text(encoding="utf-8"))
    demo_original = copy.deepcopy(demo)
    assert "jurisdiction" not in demo
    loaded = standardized_from_payload(demo, strict=True)
    assert loaded.jurisdiction == "HK"
    assert demo == demo_original
    assert loaded.metadata is not demo["metadata"]
    assert loaded.metadata["jurisdiction"] == "HK"
    roundtrip = standardized_from_payload(standardized_to_payload(loaded), strict=True)
    assert any(
        item.concept == "restructuring_expense" for item in roundtrip.income_statement
    )
    assert roundtrip.jurisdiction == "HK"

    explicit = _strict_base_payload()
    explicit["metadata"] = {"jurisdiction": "HK"}
    original = copy.deepcopy(explicit)
    fin = standardized_from_payload(explicit, strict=True)
    assert fin.jurisdiction == "US"
    assert explicit == original

    empty_top = _strict_base_payload()
    empty_top["jurisdiction"] = ""
    empty_top["metadata"] = {"jurisdiction": "HK", "source": "demo"}
    original = copy.deepcopy(empty_top)
    fin = standardized_from_payload(empty_top, strict=True)
    assert fin.jurisdiction == "HK"
    assert empty_top == original
    assert fin.metadata["source"] == "demo"


@pytest.mark.parametrize(
    "fallback",
    ({"code": "HK"}, ["HK"], 1, 0, True, False),
)
def test_strict_rejects_non_string_jurisdiction_fallback(fallback):
    missing_top = _strict_base_payload()
    missing_top.pop("jurisdiction")
    missing_top["metadata"] = {"jurisdiction": fallback}
    original = copy.deepcopy(missing_top)
    with pytest.raises(ValueError, match=r"metadata\.jurisdiction must be str"):
        standardized_from_payload(missing_top, strict=True)
    assert missing_top == original

    empty_top = _strict_base_payload()
    empty_top["jurisdiction"] = ""
    empty_top["metadata"] = {"jurisdiction": fallback}
    original = copy.deepcopy(empty_top)
    with pytest.raises(ValueError, match=r"metadata\.jurisdiction must be str"):
        standardized_from_payload(empty_top, strict=True)
    assert empty_top == original


@pytest.mark.parametrize("fallback", (None, ""))
def test_strict_null_empty_jurisdiction_fallback_stays_required(fallback):
    payload = _strict_base_payload()
    payload.pop("jurisdiction")
    payload["metadata"] = {"jurisdiction": fallback}
    original = copy.deepcopy(payload)
    with pytest.raises(ValueError, match="missing field\\(s\\): jurisdiction"):
        standardized_from_payload(payload, strict=True)
    assert payload == original


def test_strict_missing_metadata_jurisdiction_stays_required():
    payload = _strict_base_payload()
    payload.pop("jurisdiction")
    payload["metadata"] = {"source": "x"}
    original = copy.deepcopy(payload)
    with pytest.raises(ValueError, match="missing field\\(s\\): jurisdiction"):
        standardized_from_payload(payload, strict=True)
    assert payload == original


def test_strict_malformed_top_level_jurisdiction_is_rejected():
    payload = _strict_base_payload()
    payload["jurisdiction"] = 1
    payload["metadata"] = {"jurisdiction": "HK"}
    original = copy.deepcopy(payload)
    with pytest.raises(ValueError, match=r"standardized\.jurisdiction must be str"):
        standardized_from_payload(payload, strict=True)
    assert payload == original

    payload = _strict_base_payload()
    payload["jurisdiction"] = None
    payload["metadata"] = {"jurisdiction": "HK"}
    original = copy.deepcopy(payload)
    with pytest.raises(ValueError, match=r"standardized\.jurisdiction must be str"):
        standardized_from_payload(payload, strict=True)
    assert payload == original


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
    practice_specs = _practice_specs(builder.operating_kpi_specs)
    source_specs = _source_specs(builder.operating_kpi_specs)
    store_ids = {s.family_id for s in practice_specs}
    assert store_ids == {f.id for f in STORE_COUNT_COMPONENT_CATALOG}
    assert {s.family_id for s in source_specs} == {STORE_COUNT_SOURCE_FAMILY_ID}
    assert [s.id for s in source_specs] == [
        store_count_source_component_id(P1),
        store_count_source_component_id(P2),
    ]
    existing = [
        s.id
        for s in builder.expected_specs
        if s.category not in {"store_count", STORE_COUNT_SOURCE_CATEGORY}
    ]
    assert existing
    trainer, answer = build_training_workbook(fin, tmp_path / "STORE_BASE.xlsx")
    smap = load_semantic_map(answer)
    store_comps = _practice_components(smap)
    source_comps = _source_components(smap)
    assert {c.id for c in store_comps} == {s.id for s in practice_specs}
    assert {c.id for c in source_comps} == {s.id for s in source_specs}
    assert not any(c.period_index == 0 for c in store_comps)
    for spec in practice_specs:
        resolved = smap.get(spec.id)
        assert tuple(resolved.depends_on) == spec.depends_on
        assert spec.depends_on == store_count_adjacent_source_ids(
            list(builder.periods), date.fromisoformat(spec.period_end)
        )

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
    source_by_period = {c.period_end: c for c in source_comps}
    current_src = source_by_period[P2.isoformat()]
    prior_src = source_by_period[P1.isoformat()]
    current_ref = StoreCountSourceRef(
        id=current_src.id,
        semantic_key=current_src.semantic_key,
        period_end=current_src.period_end,
        cell=current_src.cell,
    )
    prior_ref = StoreCountSourceRef(
        id=prior_src.id,
        semantic_key=prior_src.semantic_key,
        period_end=prior_src.period_end,
        cell=prior_src.cell,
    )
    assert str(aws.cell(change_row, 3).value).replace(" ", "") == (
        resolve_store_count_net_change_formula(current_ref, prior_ref).replace(" ", "")
    )
    assert str(aws.cell(growth_row, 3).value).replace(" ", "") == (
        resolve_store_count_growth_formula(current_ref, prior_ref).replace(" ", "")
    )
    assert tws.cell(count_row, 2).value == 711
    assert tws.cell(count_row, 3).value == 767
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
        if is_store_count_source_identity(comp):
            continue
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
    assert not any(s.period_end == P0.isoformat() for s in _practice_specs(builder.operating_kpi_specs))
    assert _practice_specs(builder.operating_kpi_specs) == []
    assert [s.period_end for s in _source_specs(builder.operating_kpi_specs)] == [
        P0.isoformat(),
        P2.isoformat(),
    ]

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
    assert _practice_specs(builder.operating_kpi_specs) == []
    source_specs = _source_specs(builder.operating_kpi_specs)
    assert [s.id for s in source_specs] == [store_count_source_component_id(P2)]
    trainer, answer = build_training_workbook(fin, tmp_path / "STORE_SINGLE.xlsx")
    smap = load_semantic_map(answer)
    assert _practice_components(smap) == []
    sources = _source_components(smap)
    assert [c.id for c in sources] == [store_count_source_component_id(P2)]
    assert sources[0].expected_value == 811
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
    practice_specs = _practice_specs(builder.operating_kpi_specs)
    source_specs = _source_specs(builder.operating_kpi_specs)
    store_n = len(practice_specs)
    assert store_n == STORE_COUNT_LULULEMON_SPECS
    assert len(source_specs) == STORE_COUNT_LULULEMON_SOURCES
    assert [s.period_end for s in source_specs] == [
        period.isoformat() for period in series.periods
    ]
    preserved = [
        s
        for s in builder.expected_specs
        if s.category not in {"store_count", STORE_COUNT_SOURCE_CATEGORY}
    ]
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
    all_comps = [
        c for c in smap.all_ordered() if not is_store_count_source_identity(c)
    ]
    store_comps = _practice_components(smap)
    source_comps = _source_components(smap)
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    assert len(source_comps) == STORE_COUNT_LULULEMON_SOURCES
    assert {c.id for c in source_comps} == {s.id for s in source_specs}
    assert len(all_comps) == (
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS
    )
    practice = {(c.tab, c.cell) for c in all_comps}
    source_cells = {(c.tab, c.cell) for c in source_comps}
    assert source_cells.isdisjoint(practice)

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    assert aws["A2"].value == STORE_A2
    assert tws["A4"].value == STORE_A4
    _assert_no_disclosed_store_arithmetic(twb)
    source_by_period = {c.period_end: c for c in source_comps}
    count_row = _row_by_label(aws, "Company-operated period-end store count")
    assert count_row == DEFAULT_STORE_COUNT_SOURCE_ROW
    period_cols = {period: 2 + index for index, period in enumerate(builder.periods)}
    for period, value in INDEPENDENT_STORE_TOTALS.items():
        col_idx = period_cols[period]
        assert aws.cell(count_row, col_idx).value == value
        assert tws.cell(count_row, col_idx).value == value
        mapped = source_by_period[period.isoformat()]
        assert mapped.cell == f"{get_column_letter(col_idx)}{count_row}"
    change_row = _row_by_label(aws, "Net count change")
    growth_row = _row_by_label(aws, "Store-count growth")
    assert aws.cell(change_row, period_cols[P2022]).value == "N/A"
    assert tws.cell(growth_row, period_cols[P2022]).value == "N/A"
    axis = list(builder.periods)
    for period, change in (
        (P2023, 81),
        (P2024, 56),
        (P2025, 56),
        (P2026, 44),
    ):
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
        prior = axis[axis.index(period) - 1]
        current_src = source_by_period[period.isoformat()]
        prior_src = source_by_period[prior.isoformat()]
        assert tuple(change_comp.depends_on) == (
            current_src.id,
            prior_src.id,
        )
        assert tuple(growth_comp.depends_on) == tuple(change_comp.depends_on)
        current_ref = StoreCountSourceRef(
            id=current_src.id,
            semantic_key=current_src.semantic_key,
            period_end=current_src.period_end,
            cell=current_src.cell,
        )
        prior_ref = StoreCountSourceRef(
            id=prior_src.id,
            semantic_key=prior_src.semantic_key,
            period_end=prior_src.period_end,
            cell=prior_src.cell,
        )
        assert change_comp.expected_value == change
        assert growth_comp.expected_value == pytest.approx(
            series.growth[period], abs=OPERATING_KPI_RATIO_TOLERANCE
        )
        assert change_comp.formula.replace(" ", "") == (
            resolve_store_count_net_change_formula(current_ref, prior_ref).replace(
                " ", ""
            )
        )
        assert growth_comp.formula.replace(" ", "") == (
            resolve_store_count_growth_formula(current_ref, prior_ref).replace(
                " ", ""
            )
        )
        assert current_src.cell in change_comp.formula
        assert prior_src.cell in change_comp.formula
        t_change = twb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        a_change = awb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        t_source = twb[current_src.tab].cell(*parse_cell_ref(current_src.cell))
        a_source = awb[current_src.tab].cell(*parse_cell_ref(current_src.cell))
        assert t_source.value == a_source.value == INDEPENDENT_STORE_TOTALS[period]
        assert t_source.comment is None
        assert a_source.comment is None
        assert _fill_rgb(t_source) in WHITE_RGBS
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


def test_generated_workbooks_follow_moved_source_placement(tmp_path, monkeypatch):
    def _moved(self, period_index, default_row, default_col):
        assert (default_row, default_col) == (
            DEFAULT_STORE_COUNT_SOURCE_ROW,
            2 + period_index,
        )
        return MOVED_STORE_COUNT_SOURCE_PLACEMENT[period_index]

    monkeypatch.setattr(
        ReferenceModelBuilder, "_store_count_source_placement", _moved
    )
    _dest, validated = _validated_augmented(tmp_path)
    reloads = _reload_admitted_store_histories(validated)
    _reconciled, fin, restored = reloads[0]
    assert restored.historical_operating_kpis == fin.historical_operating_kpis
    series = compute_operating_kpi_series(restored)
    trainer, answer = build_training_workbook(
        restored, tmp_path / "LULU_STORE_MOVED.xlsx"
    )
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_moved")

    sidecar = component_map_path_for(answer)
    serialized = json.loads(sidecar.read_text(encoding="utf-8"))
    smap = load_semantic_map(answer)
    embedded = load_workbook(answer, data_only=False)
    assert "_ComponentMap" in embedded.sheetnames
    headers = [
        embedded["_ComponentMap"].cell(1, col).value
        for col in range(1, embedded["_ComponentMap"].max_column + 1)
    ]
    id_idx = headers.index("id")
    cell_idx = headers.index("cell")
    formula_idx = headers.index("formula")
    deps_idx = headers.index("depends_on")
    embedded_rows = {}
    for row in range(2, (embedded["_ComponentMap"].max_row or 1) + 1):
        cid = embedded["_ComponentMap"].cell(row, id_idx + 1).value
        if cid:
            embedded_rows[cid] = {
                "cell": embedded["_ComponentMap"].cell(row, cell_idx + 1).value,
                "formula": embedded["_ComponentMap"].cell(row, formula_idx + 1).value,
                "depends_on": embedded["_ComponentMap"].cell(row, deps_idx + 1).value,
            }
    embedded.close()

    source_comps = _source_components(smap)
    store_comps = _practice_components(smap)
    all_comps = [
        c for c in smap.all_ordered() if not is_store_count_source_identity(c)
    ]
    assert len(source_comps) == STORE_COUNT_LULULEMON_SOURCES
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    source_by_period = {c.period_end: c for c in source_comps}
    serialized_by_id = {row["id"]: row for row in serialized["components"]}
    axis = list(canonical_fiscal_periods(restored))
    practice = {(c.tab, c.cell) for c in all_comps}
    source_cells = {(c.tab, c.cell) for c in source_comps}
    assert source_cells.isdisjoint(practice)

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    _assert_no_disclosed_store_arithmetic(twb)

    for index, period in enumerate(axis):
        row, col = MOVED_STORE_COUNT_SOURCE_PLACEMENT[index]
        expected_cell = f"{get_column_letter(col)}{row}"
        default_cell = f"{get_column_letter(2 + index)}{DEFAULT_STORE_COUNT_SOURCE_ROW}"
        mapped = source_by_period[period.isoformat()]
        assert mapped.cell == expected_cell
        assert mapped.cell != default_cell
        assert serialized_by_id[mapped.id]["cell"] == expected_cell
        assert embedded_rows[mapped.id]["cell"] == expected_cell
        value = INDEPENDENT_STORE_TOTALS[period]
        assert aws.cell(row, col).value == value
        assert tws.cell(row, col).value == value
        assert aws.cell(DEFAULT_STORE_COUNT_SOURCE_ROW, 2 + index).value in (None, "")
        assert tws.cell(DEFAULT_STORE_COUNT_SOURCE_ROW, 2 + index).value in (None, "")
        t_source = tws.cell(row, col)
        a_source = aws.cell(row, col)
        assert t_source.comment is None
        assert a_source.comment is None
        assert _fill_rgb(t_source) in WHITE_RGBS
        assert _fill_rgb(a_source) in WHITE_RGBS

    for period, change in (
        (P2023, 81),
        (P2024, 56),
        (P2025, 56),
        (P2026, 44),
    ):
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
        prior = axis[axis.index(period) - 1]
        current_src = source_by_period[period.isoformat()]
        prior_src = source_by_period[prior.isoformat()]
        assert tuple(change_comp.depends_on) == (current_src.id, prior_src.id)
        assert tuple(growth_comp.depends_on) == tuple(change_comp.depends_on)
        serialized_change = serialized_by_id[change_comp.id]
        assert serialized_change["cell"] == change_comp.cell
        assert serialized_change["formula"].replace(" ", "") == change_comp.formula.replace(
            " ", ""
        )
        assert tuple(serialized_change.get("depends_on") or ()) == tuple(
            change_comp.depends_on
        )
        embedded_deps = [
            item
            for item in str(embedded_rows[change_comp.id]["depends_on"] or "").split(",")
            if item
        ]
        assert tuple(embedded_deps) == tuple(change_comp.depends_on)

        current_ref = StoreCountSourceRef(
            id=current_src.id,
            semantic_key=current_src.semantic_key,
            period_end=current_src.period_end,
            cell=current_src.cell,
        )
        prior_ref = StoreCountSourceRef(
            id=prior_src.id,
            semantic_key=prior_src.semantic_key,
            period_end=prior_src.period_end,
            cell=prior_src.cell,
        )
        expected_change = resolve_store_count_net_change_formula(
            current_ref, prior_ref
        ).replace(" ", "")
        expected_growth = resolve_store_count_growth_formula(
            current_ref, prior_ref
        ).replace(" ", "")
        compact_change = change_comp.formula.replace(" ", "")
        compact_growth = growth_comp.formula.replace(" ", "")
        assert compact_change == expected_change
        assert compact_growth == expected_growth
        assert compact_change == f"={current_src.cell}-{prior_src.cell}"
        reversed_change = f"={prior_src.cell}-{current_src.cell}"
        assert compact_change != reversed_change

        current_row, current_col = parse_cell_ref(current_src.cell)
        prior_row, prior_col = parse_cell_ref(prior_src.cell)
        assert current_col != prior_col + 1
        adjacent_prior = f"{get_column_letter(current_col - 1)}{current_row}"
        default_current = f"{get_column_letter(2 + axis.index(period))}{DEFAULT_STORE_COUNT_SOURCE_ROW}"
        default_prior = f"{get_column_letter(2 + axis.index(prior))}{DEFAULT_STORE_COUNT_SOURCE_ROW}"
        assert adjacent_prior not in compact_change
        assert default_current not in compact_change
        assert default_prior not in compact_change
        assert adjacent_prior not in compact_growth
        assert default_current not in compact_growth
        assert default_prior not in compact_growth

        a_current = aws.cell(current_row, current_col).value
        a_prior = aws.cell(prior_row, prior_col).value
        assert a_current == INDEPENDENT_STORE_TOTALS[period]
        assert a_prior == INDEPENDENT_STORE_TOTALS[prior]
        assert a_current - a_prior == change
        assert change_comp.expected_value == change
        assert growth_comp.expected_value == pytest.approx(
            series.growth[period], abs=OPERATING_KPI_RATIO_TOLERANCE
        )

        a_change = awb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        t_change = twb[change_comp.tab].cell(*parse_cell_ref(change_comp.cell))
        a_growth = awb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        t_growth = twb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        assert str(a_change.value).replace(" ", "") == compact_change
        assert str(a_growth.value).replace(" ", "") == compact_growth
        assert t_change.value in (None, "")
        assert t_growth.value in (None, "")
        assert t_change.comment is None
        assert t_growth.comment is None
        assert _fill_rgb(t_change) == "FFFF00"
        assert _fill_rgb(t_growth) == "FFFF00"
        assert _fill_rgb(a_change) in WHITE_RGBS
        assert _fill_rgb(a_growth) in WHITE_RGBS
        assert (a_change.comment.text or "").strip()
        assert (a_growth.comment.text or "").strip()

    awb.close()
    twb.close()
    _assert_visible_parity(trainer, answer, practice)
    _assert_fresh_visible_style(trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer)

    answer_hash = _sha256(answer)
    blank = check_workbook(trainer)
    total = (
        LEASE_DT_LULULEMON_SPECS
        + GEOGRAPHIC_LULULEMON_SPECS
        + STORE_COUNT_LULULEMON_SPECS
    )
    assert (blank.total, blank.blank, blank.correct, blank.incorrect) == (
        total,
        total,
        0,
        0,
    )
    dumped_blank = repr(blank)
    assert "(current − prior) / prior" not in dumped_blank.lower()
    assert "Net count change" not in dumped_blank

    filled_trainer, filled_answer = _copy_pair(
        trainer, answer, tmp_path / "moved_filled_check"
    )
    wb = load_workbook(filled_trainer, data_only=False)
    for comp in all_comps:
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(filled_trainer)
    wb.close()
    filled = check_workbook(filled_trainer)
    assert (filled.total, filled.correct, filled.incorrect, filled.blank) == (
        total,
        total,
        0,
        0,
    )

    incorrect_trainer, _incorrect_answer = _copy_pair(
        filled_trainer, filled_answer, tmp_path / "moved_incorrect_check"
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

    tamper_trainer, _tamper_answer = _copy_pair(
        trainer, answer, tmp_path / "moved_tamper"
    )
    moved_row, moved_col = MOVED_STORE_COUNT_SOURCE_PLACEMENT[0]
    wb = load_workbook(tamper_trainer, data_only=False)
    wb[STORE_COUNT_SHEET].cell(moved_row, moved_col).value = 1
    wb.save(tamper_trainer)
    wb.close()
    with pytest.raises(
        ValueError,
        match="Trusted workbook cell was modified: Store Count Analysis",
    ):
        check_workbook(tamper_trainer)


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
