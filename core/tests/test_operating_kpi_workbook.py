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
    COMPARABLE_SALES_CHANGE_FAMILY_ID,
    COMPARABLE_SALES_COMPONENT_CATALOG,
    COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
    COMPARABLE_SALES_PRACTICE_CATEGORY,
    COMPARABLE_SALES_SHEET_NAME,
    COMPARABLE_SALES_SOURCE_CATEGORY,
    COMPARABLE_SALES_SOURCE_FAMILY_ID,
    REVENUE_STORE_COMPONENT_CATALOG,
    REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    REVENUE_STORE_GROWTH_FAMILY_ID,
    REVENUE_STORE_PRACTICE_CATEGORY,
    REVENUE_STORE_SOURCE_CATEGORY,
    REVENUE_STORE_SOURCE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG,
    SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    SALES_PER_SQUARE_FOOT_SHEET_NAME,
    STORE_COUNT_COMPONENT_CATALOG,
    STORE_COUNT_POPULATION_LABEL,
    STORE_COUNT_SHEET_NAME,
    STORE_COUNT_SOURCE_CATEGORY,
    STORE_COUNT_SOURCE_FAMILY_ID,
    SemanticCellRef,
    StoreCountSourceRef,
    comparable_sales_change_dependency_ids,
    comparable_sales_component_id,
    comparable_sales_difference_dependency_ids,
    comparable_sales_identity_token,
    comparable_sales_source_component_id,
    comparable_sales_source_semantic_key,
    expand_comparable_sales_change_specs,
    expand_comparable_sales_source_specs,
    expand_comparable_sales_specs,
    expand_sales_per_square_foot_difference_specs,
    expand_sales_per_square_foot_source_specs,
    expand_sales_per_square_foot_specs,
    expand_revenue_store_source_specs,
    expand_revenue_store_specs,
    expand_store_count_source_specs,
    expand_store_count_specs,
    is_comparable_sales_practice_identity,
    is_comparable_sales_source_identity,
    is_operating_kpi_source_identity,
    is_sales_per_square_foot_practice_identity,
    is_sales_per_square_foot_source_identity,
    is_revenue_store_practice_identity,
    is_revenue_store_source_identity,
    is_store_count_practice_identity,
    is_store_count_source_identity,
    operating_kpi_spec_identity,
    resolve_management_kpi_adjacent_change_formula,
    resolve_management_kpi_growth_formula,
    resolve_revenue_comparable_sales_difference_formula,
    resolve_revenue_sales_per_square_foot_difference_formula,
    resolve_revenue_store_difference_formula,
    resolve_revenue_store_growth_formula,
    resolve_store_count_growth_formula,
    resolve_store_count_net_change_formula,
    revenue_store_adjacent_source_ids,
    revenue_store_component_id,
    revenue_store_difference_dependency_ids,
    revenue_store_source_component_id,
    revenue_store_source_semantic_key,
    sales_per_square_foot_difference_dependency_ids,
    sales_per_square_foot_source_component_id,
    sales_per_square_foot_source_semantic_key,
    store_count_adjacent_source_ids,
    store_count_component_id,
    store_count_source_component_id,
    store_count_source_semantic_key,
)
from core.engine.reference_model import (
    COMPARABLE_SALES_SHEET,
    JUDGMENT_SHEET,
    SALES_PER_SQUARE_FOOT_SCOPE_NOTE,
    SALES_PER_SQUARE_FOOT_SHEET,
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
from core.model.line_resolver import AmbiguousLineError, MissingLineError
from core.model.source_values import MissingHistoricalValueError
from core.model.management_kpi import (
    REASON_CALENDAR_REPORTING_MISMATCH,
    REASON_CALENDAR_WEEK_MISMATCH,
    REASON_DEFINITION_MISMATCH,
    REASON_MISSING_OBSERVATION,
    REASON_MISSING_PRIOR_OBSERVATION,
    REASON_QUALIFIER_MISMATCH,
    compute_management_kpi_series,
    management_kpi_applicable,
)
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.operating_kpi_relationships import (
    COMPARABLE_SALES_SCOPE_NOTE,
    OPERATING_KPI_RELATIONSHIP_TOLERANCE,
    SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE,
    SCOPE_NOTE,
    compute_operating_kpi_revenue_comparable_sales_relationship,
    compute_operating_kpi_revenue_sales_per_square_foot_relationship,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_comparable_sales_relationship_applicable,
    operating_kpi_revenue_sales_per_square_foot_relationship_applicable,
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
    assert_bav_has_no_exercise_framing,
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
from core.tests.test_management_kpi_history import (
    DEF_A,
    DEF_B,
    _reconcile,
    _write_selected_on_docs,
)
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
    _prepare_augmented,
    _validated_augmented,
)
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    POP_STORES_AND_DTC,
    POP_STORES_AND_ECOMMERCE,
)
from core.tests.test_lululemon_benchmark import REVENUE_ANCHORS
from core.tests.test_management_kpi_identity import REPORTING_BASIS_52, REPORTING_BASIS_53
from core.tests.test_operating_kpi_management_history import DEF_SPSF, _compsales, _spsf
from core.tests.test_operating_kpi_relationships import (
    _fin_with_relationship,
    _identity_of,
    _independent_compsales_relationship,
    _independent_relationship,
)
from core.trainer.checker import (
    BLANK_RGB,
    CORRECT_RGB,
    INCORRECT_RGB,
    check_workbook,
)
from core.trainer.semantic_io import component_map_path_for, load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "build" / "input" / "fast_retailing" / "reconciled" / "standardized.json"
LULU_JSON = ROOT / "core" / "tests" / "fixtures" / "ordinary_reconcile" / "lululemon" / "standardized.json"
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"
P0 = date(2023, 12, 31)
LEASE_DT_LULULEMON_SPECS = 486
FAST_RETAILING_SPECS = 577
GEOGRAPHIC_LULULEMON_SPECS_BASELINE = 74
GEOGRAPHIC_CONTRIBUTION_SPECS = 20
GEOGRAPHIC_MARGIN_BRIDGE_SPECS = 54
GEOGRAPHIC_MIX_WITHIN_SPECS = 28
GEOGRAPHIC_AMOUNT_CHANGE_SPECS = 24
GEOGRAPHIC_PROFIT_EFFECT_SPECS = 24
GEOGRAPHIC_INCREMENTAL_MARGIN_SPECS = 16
GEOGRAPHIC_PROFIT_GROWTH_SPECS = 24
GEOGRAPHIC_LULULEMON_SPECS = (
    GEOGRAPHIC_LULULEMON_SPECS_BASELINE
    + GEOGRAPHIC_CONTRIBUTION_SPECS
    + GEOGRAPHIC_MARGIN_BRIDGE_SPECS
    + GEOGRAPHIC_MIX_WITHIN_SPECS
    + GEOGRAPHIC_AMOUNT_CHANGE_SPECS
    + GEOGRAPHIC_PROFIT_EFFECT_SPECS
    + GEOGRAPHIC_INCREMENTAL_MARGIN_SPECS
    + GEOGRAPHIC_PROFIT_GROWTH_SPECS
)
STORE_COUNT_LULULEMON_SPECS = 8
STORE_COUNT_LULULEMON_SOURCES = 5
REVENUE_STORE_LULULEMON_SPECS = 8
REVENUE_STORE_LULULEMON_SOURCES = 5
REVENUE_PER_STORE_LULULEMON_SPECS = 17
LULULEMON_STORE_AUGMENTED_PRACTICE = (
    LEASE_DT_LULULEMON_SPECS
    + GEOGRAPHIC_LULULEMON_SPECS
    + STORE_COUNT_LULULEMON_SPECS
)
LULULEMON_UNAVAILABLE_DISPLAYS = 101
DEFAULT_STORE_COUNT_SOURCE_ROW = 10
DEFAULT_REVENUE_STORE_SOURCE_ROW = 20
MOVED_STORE_COUNT_SOURCE_PLACEMENT = {
    0: (32, 2),
    1: (40, 5),
    2: (32, 8),
    3: (40, 11),
    4: (32, 14),
}
MOVED_REVENUE_STORE_SOURCE_PLACEMENT = {
    0: (28, 3),
    1: (36, 6),
    2: (28, 9),
    3: (36, 12),
    4: (28, 15),
}
MOVED_COMPSALES_SOURCE_PLACEMENT = {
    0: (44, 4, "Income Statement"),
    1: (52, 7, "Income Statement"),
    2: (44, 10, "Income Statement"),
    3: (52, 13, "Income Statement"),
    4: (44, 16, "Income Statement"),
}
STORE_A2 = (
    "Source-supported company-operated period-end store counts with "
    "adjacent net count change and count growth. Changes are net "
    "count changes, not openings or closures."
)
STORE_A4 = (
    "Opening change and growth remain unavailable without a prior "
    "period. A missing adjacent snapshot remains unavailable. Count "
    "units stay independent of monetary scale."
)
_DISCLOSED_STORE_ARITHMETIC = (
    "(current − prior) / prior",
    "(current - prior) / prior",
    "gross openings",
    "gross closures",
    "100*(",
    "100 × (",
    "100 x (",
)
REVIEWED_SPSF_A5_DISCLOSURE = (
    "Adjacent change is current minus prior reported sales per square "
    "foot. Growth is (current - prior) / prior. These are analyst-derived "
    "calculations, not causal evidence, and are distinct from comparable-sales "
    "percentage-point change."
)
_DISCLOSED_SPSF_ARITHMETIC = (
    "current minus prior",
    "(current - prior) / prior",
    "(current − prior) / prior",
    "growth is (current",
)
MANAGEMENT_HISTORY_SHEETS = (COMPARABLE_SALES_SHEET, SALES_PER_SQUARE_FOOT_SHEET)


def _practice_components(smap):
    return [c for c in smap.all_ordered() if is_store_count_practice_identity(c)]


def _source_components(smap):
    return [c for c in smap.all_ordered() if is_store_count_source_identity(c)]


def _relationship_practice_components(smap):
    return [c for c in smap.all_ordered() if is_revenue_store_practice_identity(c)]


def _revenue_source_components(smap):
    return [c for c in smap.all_ordered() if is_revenue_store_source_identity(c)]


def _compsales_practice_components(smap):
    return [c for c in smap.all_ordered() if is_comparable_sales_practice_identity(c)]


def _compsales_difference_components(smap):
    return [
        c
        for c in smap.all_ordered()
        if c.family_id == COMPARABLE_SALES_DIFFERENCE_FAMILY_ID
    ]


def _compsales_change_components(smap):
    return [
        c
        for c in smap.all_ordered()
        if c.family_id == COMPARABLE_SALES_CHANGE_FAMILY_ID
    ]


def _compsales_source_components(smap):
    return [c for c in smap.all_ordered() if is_comparable_sales_source_identity(c)]


def _spsf_practice_components(smap):
    return [
        c for c in smap.all_ordered() if is_sales_per_square_foot_practice_identity(c)
    ]


def _spsf_difference_components(smap):
    return [
        c
        for c in smap.all_ordered()
        if c.family_id == SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID
    ]


def _spsf_source_components(smap):
    return [c for c in smap.all_ordered() if is_sales_per_square_foot_source_identity(c)]


def _check_components(smap):
    return [c for c in smap.all_ordered() if not is_operating_kpi_source_identity(c)]


def _practice_specs(specs):
    return [s for s in specs if is_store_count_practice_identity(s)]


def _source_specs(specs):
    return [s for s in specs if is_store_count_source_identity(s)]


def _relationship_practice_specs(specs):
    return [s for s in specs if is_revenue_store_practice_identity(s)]


def _revenue_source_specs(specs):
    return [s for s in specs if is_revenue_store_source_identity(s)]


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


def _assert_spsf_a5_non_disclosing(value: object) -> None:
    assert value == SALES_PER_SQUARE_FOOT_SCOPE_NOTE
    assert value != REVIEWED_SPSF_A5_DISCLOSURE
    lowered = str(value).lower()
    for fragment in _DISCLOSED_SPSF_ARITHMETIC:
        assert fragment not in lowered, (
            f"Sales per Square Foot Analysis!A5 discloses practice arithmetic: {value!r}"
        )
    assert "analyst-derived" in lowered
    assert "comparable-sales" in lowered
    assert "percentage-point" in lowered
    assert "causal" in lowered


def _assert_no_disclosed_spsf_arithmetic(wb, *, include_comments: bool) -> None:
    for sheet, coord, text in _visible_cell_texts(wb):
        if not include_comments and coord.endswith("#comment"):
            continue
        lowered = text.lower()
        if text == REVIEWED_SPSF_A5_DISCLOSURE or lowered == REVIEWED_SPSF_A5_DISCLOSURE.lower():
            raise AssertionError(
                f"{sheet}!{coord} retains the reviewed A5 disclosure: {text!r}"
            )
        for fragment in _DISCLOSED_SPSF_ARITHMETIC:
            assert fragment not in lowered, (
                f"{sheet}!{coord} discloses SPSF practice arithmetic: {text!r}"
            )


def _management_history_explanatory_texts(wb) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for title in MANAGEMENT_HISTORY_SHEETS:
        if title not in wb.sheetnames:
            continue
        ws = wb[title]
        if ws.sheet_state != "visible":
            continue
        for row in range(1, (ws.max_row or 1) + 1):
            cell = ws.cell(row, 1)
            value = cell.value
            if isinstance(value, str) and not value.startswith("="):
                found.append((title, cell.coordinate, value))
    return found


def _assert_management_history_visible_text_undisclosed(wb) -> None:
    texts = _management_history_explanatory_texts(wb)
    assert any(
        sheet == SALES_PER_SQUARE_FOOT_SHEET and coord == "A5"
        for sheet, coord, _text in texts
    )
    for sheet, coord, text in texts:
        lowered = text.lower()
        assert text != REVIEWED_SPSF_A5_DISCLOSURE
        for fragment in _DISCLOSED_SPSF_ARITHMETIC:
            assert fragment not in lowered, (
                f"{sheet}!{coord} discloses management-history practice arithmetic: {text!r}"
            )
    if SALES_PER_SQUARE_FOOT_SHEET in wb.sheetnames:
        _assert_spsf_a5_non_disclosing(wb[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value)


def _spsf_answer_guidance() -> tuple[str, ...]:
    texts: list[str] = []
    for family in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG:
        if family.short_hint:
            texts.append(family.short_hint)
        texts.extend(family.hints)
    return tuple(texts)


def _assert_trainer_management_history_undisclosed(wb) -> None:
    _assert_management_history_visible_text_undisclosed(wb)
    _assert_no_disclosed_spsf_arithmetic(wb, include_comments=True)
    blob = "\n".join(text for _sheet, _coord, text in _visible_cell_texts(wb))
    lowered_blob = blob.lower()
    for guidance in _spsf_answer_guidance():
        assert guidance.lower() not in lowered_blob, (
            f"Trainer visible text discloses Answer-Key SPSF guidance: {guidance!r}"
        )
    for sheet, coord, text in _visible_cell_texts(wb):
        if coord.endswith("#comment"):
            raise AssertionError(
                f"{sheet}!{coord} retains a visible Note on the Trainer: {text!r}"
            )


def _assert_answer_key_management_history_undisclosed(wb) -> None:
    _assert_management_history_visible_text_undisclosed(wb)
    for sheet, coord, text in _visible_cell_texts(wb):
        if sheet not in MANAGEMENT_HISTORY_SHEETS:
            continue
        if coord.endswith("#comment"):
            continue
        lowered = text.lower()
        if text == REVIEWED_SPSF_A5_DISCLOSURE:
            raise AssertionError(
                f"{sheet}!{coord} retains the reviewed A5 disclosure: {text!r}"
            )
        for fragment in _DISCLOSED_SPSF_ARITHMETIC:
            assert fragment not in lowered, (
                f"{sheet}!{coord} discloses SPSF practice arithmetic: {text!r}"
            )


def _reserialize_xlsx(path: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    wb = load_workbook(path, data_only=False)
    wb.save(dest)
    wb.close()
    return dest


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
    assert "Overview" in a_visible
    assert "Trainer" not in a_visible
    assert "Trainer" in t_visible
    assert [title for title in t_visible if title != "Trainer"] == a_visible
    for name in a_visible:
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
    assert mgmt_builder.operating_kpi_relationship is None
    assert mgmt_builder.operating_kpi_compsales_relationship is not None
    assert _source_specs(mgmt_builder.operating_kpi_specs) == []
    trainer, answer = build_training_workbook(
        management_only, tmp_path / "STORE_MGMT.xlsx"
    )
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert STORE_COUNT_SHEET not in wb.sheetnames
        assert "Comparable Sales Analysis" in wb.sheetnames
        wb.close()
    smap = load_semantic_map(answer)
    assert not any(c.category == "store_count" for c in smap.all_ordered())
    assert any(
        c.family_id == "operating_kpi_revenue_comparable_sales_difference"
        for c in smap.all_ordered()
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
        if s.category not in {
            "store_count",
            STORE_COUNT_SOURCE_CATEGORY,
            REVENUE_STORE_PRACTICE_CATEGORY,
            REVENUE_STORE_SOURCE_CATEGORY,
            "revenue_per_store",
        }
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
    assert_bav_has_no_exercise_framing(answer)
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
        if is_operating_kpi_source_identity(comp):
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
        if s.category not in {
            "store_count",
            STORE_COUNT_SOURCE_CATEGORY,
            REVENUE_STORE_PRACTICE_CATEGORY,
            REVENUE_STORE_SOURCE_CATEGORY,
            "revenue_per_store",
        }
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
    all_comps = _check_components(smap)
    store_comps = _practice_components(smap)
    source_comps = _source_components(smap)
    relationship_comps = _relationship_practice_components(smap)
    revenue_sources = _revenue_source_components(smap)
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    assert len(source_comps) == STORE_COUNT_LULULEMON_SOURCES
    assert len(relationship_comps) == REVENUE_STORE_LULULEMON_SPECS
    assert len(revenue_sources) == REVENUE_STORE_LULULEMON_SOURCES
    assert {c.id for c in source_comps} == {s.id for s in source_specs}
    assert len(all_comps) == (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
    )
    practice = {(c.tab, c.cell) for c in all_comps}
    source_cells = {(c.tab, c.cell) for c in source_comps}
    revenue_source_cells = {(c.tab, c.cell) for c in revenue_sources}
    assert source_cells.isdisjoint(practice)
    assert revenue_source_cells.isdisjoint(practice)

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

    assert aws["A5"].value == SCOPE_NOTE
    assert tws["A5"].value == SCOPE_NOTE
    revenue_row = _row_by_label(aws, "Consolidated revenue")
    assert revenue_row == DEFAULT_REVENUE_STORE_SOURCE_ROW
    expected_rel = _independent_relationship(
        axis, REVENUE_ANCHORS, INDEPENDENT_STORE_TOTALS
    )
    revenue_by_period = {c.period_end: c for c in revenue_sources}
    growth_by_period = {
        c.period_end: c
        for c in relationship_comps
        if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID
    }
    difference_by_period = {
        c.period_end: c
        for c in relationship_comps
        if c.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
    }
    store_growth_by_period = {
        c.period_end: c
        for c in store_comps
        if c.family_id == "store_count_growth"
    }
    for period in (P2023, P2024, P2025, P2026):
        prior = axis[axis.index(period) - 1]
        expected_rev_growth = (
            REVENUE_ANCHORS[period] - REVENUE_ANCHORS[prior]
        ) / REVENUE_ANCHORS[prior]
        expected_store_growth = (
            INDEPENDENT_STORE_TOTALS[period] - INDEPENDENT_STORE_TOTALS[prior]
        ) / INDEPENDENT_STORE_TOTALS[prior]
        expected_diff = 100.0 * (expected_rev_growth - expected_store_growth)
        assert expected_rel[period]["revenue_growth"] == pytest.approx(
            expected_rev_growth, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert expected_rel[period]["difference"] == pytest.approx(
            expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        growth_comp = growth_by_period[period.isoformat()]
        diff_comp = difference_by_period[period.isoformat()]
        current_rev = revenue_by_period[period.isoformat()]
        prior_rev = revenue_by_period[prior.isoformat()]
        store_growth_comp = store_growth_by_period[period.isoformat()]
        assert tuple(growth_comp.depends_on) == (current_rev.id, prior_rev.id)
        assert tuple(diff_comp.depends_on) == (
            growth_comp.id,
            store_growth_comp.id,
        )
        current_ref = SemanticCellRef(
            id=current_rev.id,
            semantic_key=current_rev.semantic_key,
            period_end=current_rev.period_end,
            cell=current_rev.cell,
            tab=current_rev.tab,
        )
        prior_ref = SemanticCellRef(
            id=prior_rev.id,
            semantic_key=prior_rev.semantic_key,
            period_end=prior_rev.period_end,
            cell=prior_rev.cell,
            tab=prior_rev.tab,
        )
        growth_ref = SemanticCellRef(
            id=growth_comp.id,
            semantic_key=growth_comp.semantic_key,
            period_end=growth_comp.period_end,
            cell=growth_comp.cell,
            tab=growth_comp.tab,
        )
        store_ref = SemanticCellRef(
            id=store_growth_comp.id,
            semantic_key=store_growth_comp.semantic_key,
            period_end=store_growth_comp.period_end,
            cell=store_growth_comp.cell,
            tab=store_growth_comp.tab,
        )
        assert growth_comp.formula.replace(" ", "") == (
            resolve_revenue_store_growth_formula(
                current_ref, prior_ref, from_tab=STORE_COUNT_SHEET
            ).replace(" ", "")
        )
        assert diff_comp.formula.replace(" ", "") == (
            resolve_revenue_store_difference_formula(
                growth_ref, store_ref, from_tab=STORE_COUNT_SHEET
            ).replace(" ", "")
        )
        assert growth_comp.expected_value == pytest.approx(
            expected_rev_growth, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert diff_comp.expected_value == pytest.approx(
            expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert aws.cell(revenue_row, period_cols[period]).value == REVENUE_ANCHORS[period]
        assert tws.cell(revenue_row, period_cols[period]).value == REVENUE_ANCHORS[period]
        t_growth = twb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        a_growth = awb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        t_diff = twb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
        a_diff = awb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
        t_rev = twb[current_rev.tab].cell(*parse_cell_ref(current_rev.cell))
        a_rev = awb[current_rev.tab].cell(*parse_cell_ref(current_rev.cell))
        assert t_rev.value == a_rev.value == REVENUE_ANCHORS[period]
        assert t_rev.comment is None
        assert a_rev.comment is None
        assert _fill_rgb(t_rev) in WHITE_RGBS
        assert t_growth.value is None
        assert t_diff.value is None
        assert t_growth.comment is None
        assert t_diff.comment is None
        assert _fill_rgb(t_growth) == "FFFF00"
        assert _fill_rgb(t_diff) == "FFFF00"
        assert a_growth.value == growth_comp.formula
        assert a_diff.value == diff_comp.formula
        assert _fill_rgb(a_growth) in WHITE_RGBS
        assert _fill_rgb(a_diff) in WHITE_RGBS
        assert (a_growth.comment.text or "").strip()
        assert (a_diff.comment.text or "").strip()
        assert "attribution" in (a_diff.comment.text or "").lower()

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
    total = (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
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
        trainer, answer, tmp_path / "filled_check"
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
    all_comps = _check_components(smap)
    assert len(source_comps) == STORE_COUNT_LULULEMON_SOURCES
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    assert len(_relationship_practice_components(smap)) == REVENUE_STORE_LULULEMON_SPECS
    assert len(_revenue_source_components(smap)) == REVENUE_STORE_LULULEMON_SOURCES
    source_by_period = {c.period_end: c for c in source_comps}
    serialized_by_id = {row["id"]: row for row in serialized["components"]}
    axis = list(canonical_fiscal_periods(restored))
    practice = {(c.tab, c.cell) for c in all_comps}
    source_cells = {(c.tab, c.cell) for c in source_comps}
    revenue_source_cells = {
        (c.tab, c.cell) for c in _revenue_source_components(smap)
    }
    assert source_cells.isdisjoint(practice)
    assert revenue_source_cells.isdisjoint(practice)

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
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
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
    assert {
        c.family_id
        for c in smap.all_ordered()
        if c.category == REVENUE_STORE_PRACTICE_CATEGORY
    } == {
        REVENUE_STORE_GROWTH_FAMILY_ID,
        REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    }
    assert not any(
        "comparable" in (c.family_id or "") for c in smap.all_ordered()
    )
    assert operating_kpi_revenue_store_relationship_applicable(store_only) is True
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(
        store_only
    ) is False


def test_revenue_store_catalog_orders_and_expand_identities():
    assert [family.order for family in REVENUE_STORE_COMPONENT_CATALOG] == [164, 165]
    assert [family.id for family in REVENUE_STORE_COMPONENT_CATALOG] == [
        REVENUE_STORE_GROWTH_FAMILY_ID,
        REVENUE_STORE_DIFFERENCE_FAMILY_ID,
    ]
    sources = expand_revenue_store_source_specs(
        [P1, P2],
        start_order=1,
        source_periods=(P1, P2),
    )
    assert [s.id for s in sources] == [
        revenue_store_source_component_id(P1),
        revenue_store_source_component_id(P2),
    ]
    assert [s.semantic_key for s in sources] == [
        revenue_store_source_semantic_key(P1),
        revenue_store_source_semantic_key(P2),
    ]
    assert all(s.category == REVENUE_STORE_SOURCE_CATEGORY for s in sources)
    assert all(s.depends_on == () for s in sources)
    assert all(s.family_id == REVENUE_STORE_SOURCE_FAMILY_ID for s in sources)
    specs = expand_revenue_store_specs(
        [P1, P2],
        start_order=10,
        growth_periods=(P2,),
        difference_periods=(P2,),
    )
    assert [s.id for s in specs] == [
        revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, P2),
        revenue_store_component_id(REVENUE_STORE_DIFFERENCE_FAMILY_ID, P2),
    ]
    expected_growth_deps = revenue_store_adjacent_source_ids([P1, P2], P2)
    assert expected_growth_deps == (
        revenue_store_source_component_id(P2),
        revenue_store_source_component_id(P1),
    )
    assert specs[0].depends_on == expected_growth_deps
    assert specs[1].depends_on == revenue_store_difference_dependency_ids(P2)
    assert specs[1].depends_on == (
        revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, P2),
        store_count_component_id("store_count_growth", P2),
    )
    assert not any(s.period_end == P1.isoformat() for s in specs)
    with pytest.raises(ValueError, match="duplicate fiscal periods"):
        expand_revenue_store_specs(
            [P1, P1],
            start_order=1,
            growth_periods=(),
            difference_periods=(),
        )
    with pytest.raises(ValueError, match="strictly chronological"):
        expand_revenue_store_specs(
            [P2, P1],
            start_order=1,
            growth_periods=(P2,),
            difference_periods=(P2,),
        )
    with pytest.raises(ValueError, match="opening revenue/store period"):
        revenue_store_adjacent_source_ids([P1, P2], P1)


def test_revenue_store_formula_resolution_follows_mapped_identities():
    current = SemanticCellRef(
        id=revenue_store_source_component_id(P2),
        semantic_key=revenue_store_source_semantic_key(P2),
        period_end=P2.isoformat(),
        cell="I28",
        tab=STORE_COUNT_SHEET_NAME,
    )
    prior = SemanticCellRef(
        id=revenue_store_source_component_id(P1),
        semantic_key=revenue_store_source_semantic_key(P1),
        period_end=P1.isoformat(),
        cell="C28",
        tab=STORE_COUNT_SHEET_NAME,
    )
    growth = resolve_revenue_store_growth_formula(
        current, prior, from_tab=STORE_COUNT_SHEET_NAME
    )
    assert growth == "=IF(C28=0,NA(),(I28-C28)/C28)"
    reversed_growth = resolve_revenue_store_growth_formula(
        prior, current, from_tab=STORE_COUNT_SHEET_NAME
    )
    assert reversed_growth != growth
    cross_current = SemanticCellRef(
        id=current.id,
        semantic_key=current.semantic_key,
        period_end=current.period_end,
        cell="E7",
        tab="Income Statement",
    )
    cross_prior = SemanticCellRef(
        id=prior.id,
        semantic_key=prior.semantic_key,
        period_end=prior.period_end,
        cell="B7",
        tab="Income Statement",
    )
    cross = resolve_revenue_store_growth_formula(
        cross_current, cross_prior, from_tab=STORE_COUNT_SHEET_NAME
    )
    assert "'Income Statement'!E7" in cross
    assert "'Income Statement'!B7" in cross
    assert "C28" not in cross
    revenue_growth = SemanticCellRef(
        id=revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, P2),
        semantic_key="operating_kpi.revenue_store.revenue_growth",
        period_end=P2.isoformat(),
        cell="C23",
        tab=STORE_COUNT_SHEET_NAME,
    )
    store_growth = SemanticCellRef(
        id=store_count_component_id("store_count_growth", P2),
        semantic_key="operating_kpi.store_count.growth",
        period_end=P2.isoformat(),
        cell="C17",
        tab=STORE_COUNT_SHEET_NAME,
    )
    difference = resolve_revenue_store_difference_formula(
        revenue_growth, store_growth, from_tab=STORE_COUNT_SHEET_NAME
    )
    assert difference == "=100*(C23-C17)"
    with pytest.raises(ValueError, match="mapped coordinate"):
        resolve_revenue_store_growth_formula(
            SemanticCellRef("a", "a", P2.isoformat(), "", STORE_COUNT_SHEET_NAME),
            prior,
            from_tab=STORE_COUNT_SHEET_NAME,
        )


def test_missing_revenue_and_zero_prior_are_not_practiced_or_undefined(tmp_path):
    missing_api = _fin_with_relationship(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
        revenue={P1: 100.0},
    )
    missing_before = copy.deepcopy(missing_api.income_statement)
    missing_rel = compute_operating_kpi_revenue_store_relationship(missing_api)
    assert missing_rel.revenue[P2] == SOURCE_UNAVAILABLE
    assert missing_rel.revenue_growth[P2] == SOURCE_UNAVAILABLE
    assert missing_rel.growth_difference_pp[P2] == SOURCE_UNAVAILABLE
    assert missing_api.income_statement == missing_before

    missing_wb = _store_tiny(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    for item in missing_wb.income_statement:
        if item.concept == "revenue":
            item.values[P2] = None
    original = copy.deepcopy(missing_wb.income_statement)
    original_kpi = copy.deepcopy(missing_wb.historical_operating_kpis)
    with pytest.raises(MissingHistoricalValueError, match="no supplied value"):
        ReferenceModelBuilder(missing_wb)
    assert missing_wb.income_statement == original
    assert missing_wb.historical_operating_kpis == original_kpi

    gap = _store_tiny(
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P2, 767),
        extra_opening=P0,
    )
    gap_builder = ReferenceModelBuilder(gap)
    gap_rel = gap_builder.operating_kpi_relationship
    assert gap_rel is not None
    assert gap_rel.store_count[P1] == SOURCE_UNAVAILABLE
    assert gap_rel.growth_difference_pp[P1] == SOURCE_UNAVAILABLE
    assert gap_rel.growth_difference_pp[P2] == SOURCE_UNAVAILABLE
    assert not any(
        s.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
        for s in _relationship_practice_specs(gap_builder.operating_kpi_specs)
    )
    trainer, answer = build_training_workbook(gap, tmp_path / "REV_GAP.xlsx")
    awb = load_workbook(answer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    diff_row = _row_by_label(
        aws, "Growth difference (analyst-derived, percentage points)"
    )
    assert aws.cell(diff_row, 3).value == SOURCE_UNAVAILABLE
    assert aws.cell(diff_row, 4).value == SOURCE_UNAVAILABLE
    awb.close()

    zero_open = _store_tiny(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    for item in zero_open.income_statement:
        if item.concept == "revenue":
            item.values[P1] = 0.0
            item.values[P2] = 10.0
    zero_builder = ReferenceModelBuilder(zero_open)
    assert zero_builder.operating_kpi_relationship.revenue_growth[P2] == UNDEFINED_RATIO
    assert (
        zero_builder.operating_kpi_relationship.growth_difference_pp[P2]
        == UNDEFINED_RATIO
    )
    zero_trainer, zero_answer = build_training_workbook(
        zero_open, tmp_path / "REV_ZERO.xlsx"
    )
    zawb = load_workbook(zero_answer, data_only=False)
    zaws = zawb[STORE_COUNT_SHEET]
    z_growth = _row_by_label(
        zaws, "Consolidated revenue growth (statement-derived)"
    )
    assert "NA()" in str(zaws.cell(z_growth, 3).value)
    zawb.close()
    decline = _store_tiny(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 655),
    )
    for item in decline.income_statement:
        if item.concept == "revenue":
            item.values[P1] = 200.0
            item.values[P2] = 160.0
    decline_rel = compute_operating_kpi_revenue_store_relationship(decline)
    expected_rev = (160.0 - 200.0) / 200.0
    expected_store = (655 - 711) / 711
    expected_diff = 100.0 * (expected_rev - expected_store)
    assert decline_rel.revenue_growth[P2] == pytest.approx(
        expected_rev, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert decline_rel.growth_difference_pp[P2] == pytest.approx(
        expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    decline_trainer, decline_answer = build_training_workbook(
        decline, tmp_path / "REV_DECLINE.xlsx"
    )
    dmap = load_semantic_map(decline_answer)
    diff = next(
        c
        for c in dmap.all_ordered()
        if c.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
    )
    assert diff.expected_value == pytest.approx(
        expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert Path(trainer).is_file()
    assert Path(zero_trainer).is_file()
    assert Path(decline_trainer).is_file()


def test_ambiguous_revenue_fails_closed_without_mutation():
    fin = _store_tiny(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767))
    fin.income_statement.append(
        copy.deepcopy(fin.income_statement[0])
    )
    fin.income_statement[-1].label = "Turnover"
    original = copy.deepcopy(fin.income_statement)
    original_kpi = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(AmbiguousLineError, match="Ambiguous concept='revenue'"):
        ReferenceModelBuilder(fin)
    assert fin.income_statement == original
    assert fin.historical_operating_kpis == original_kpi


def test_generated_workbooks_follow_moved_revenue_and_count_sources(
    tmp_path, monkeypatch
):
    def _moved_count(self, period_index, default_row, default_col):
        assert (default_row, default_col) == (
            DEFAULT_STORE_COUNT_SOURCE_ROW,
            2 + period_index,
        )
        return MOVED_STORE_COUNT_SOURCE_PLACEMENT[period_index]

    def _moved_revenue(self, period_index, default_row, default_col):
        assert (default_row, default_col) == (
            DEFAULT_REVENUE_STORE_SOURCE_ROW,
            2 + period_index,
        )
        return MOVED_REVENUE_STORE_SOURCE_PLACEMENT[period_index]

    monkeypatch.setattr(
        ReferenceModelBuilder, "_store_count_source_placement", _moved_count
    )
    monkeypatch.setattr(
        ReferenceModelBuilder, "_revenue_store_source_placement", _moved_revenue
    )
    _dest, validated = _validated_augmented(tmp_path)
    reloads = _reload_admitted_store_histories(validated)
    _reconciled, fin, restored = reloads[0]
    series = compute_operating_kpi_series(restored)
    relationship = compute_operating_kpi_revenue_store_relationship(restored)
    expected_rel = _independent_relationship(
        list(canonical_fiscal_periods(restored)),
        REVENUE_ANCHORS,
        INDEPENDENT_STORE_TOTALS,
    )
    trainer, answer = build_training_workbook(
        restored, tmp_path / "LULU_REV_STORE_MOVED.xlsx"
    )
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_rev_moved")
    sidecar = component_map_path_for(answer)
    serialized = json.loads(sidecar.read_text(encoding="utf-8"))
    smap = load_semantic_map(answer)
    store_comps = _practice_components(smap)
    relationship_comps = _relationship_practice_components(smap)
    revenue_sources = _revenue_source_components(smap)
    all_comps = _check_components(smap)
    assert len(store_comps) == STORE_COUNT_LULULEMON_SPECS
    assert len(relationship_comps) == REVENUE_STORE_LULULEMON_SPECS
    assert len(revenue_sources) == REVENUE_STORE_LULULEMON_SOURCES
    serialized_by_id = {row["id"]: row for row in serialized["components"]}
    axis = list(canonical_fiscal_periods(restored))
    practice = {(c.tab, c.cell) for c in all_comps}
    revenue_source_cells = {(c.tab, c.cell) for c in revenue_sources}
    assert revenue_source_cells.isdisjoint(practice)

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[STORE_COUNT_SHEET]
    tws = twb[STORE_COUNT_SHEET]
    _assert_no_disclosed_store_arithmetic(twb)
    assert aws["A5"].value == SCOPE_NOTE

    revenue_by_period = {c.period_end: c for c in revenue_sources}
    for index, period in enumerate(axis):
        row, col = MOVED_REVENUE_STORE_SOURCE_PLACEMENT[index]
        expected_cell = f"{get_column_letter(col)}{row}"
        default_cell = (
            f"{get_column_letter(2 + index)}{DEFAULT_REVENUE_STORE_SOURCE_ROW}"
        )
        mapped = revenue_by_period[period.isoformat()]
        assert mapped.cell == expected_cell
        assert mapped.cell != default_cell
        assert serialized_by_id[mapped.id]["cell"] == expected_cell
        assert aws.cell(row, col).value == REVENUE_ANCHORS[period]
        assert tws.cell(row, col).value == REVENUE_ANCHORS[period]
        assert aws.cell(DEFAULT_REVENUE_STORE_SOURCE_ROW, 2 + index).value in (
            None,
            "",
        )
        assert tws.cell(DEFAULT_REVENUE_STORE_SOURCE_ROW, 2 + index).value in (
            None,
            "",
        )

    growth_by_period = {
        c.period_end: c
        for c in relationship_comps
        if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID
    }
    difference_by_period = {
        c.period_end: c
        for c in relationship_comps
        if c.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
    }
    store_growth_by_period = {
        c.period_end: c
        for c in store_comps
        if c.family_id == "store_count_growth"
    }
    for period in (P2023, P2024, P2025, P2026):
        prior = axis[axis.index(period) - 1]
        expected_rev_growth = (
            REVENUE_ANCHORS[period] - REVENUE_ANCHORS[prior]
        ) / REVENUE_ANCHORS[prior]
        expected_store_growth = series.growth[period]
        expected_diff = 100.0 * (expected_rev_growth - expected_store_growth)
        assert abs(expected_rev_growth - expected_rel[period]["revenue_growth"]) <= (
            OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert abs(expected_diff - expected_rel[period]["difference"]) <= (
            OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert relationship.revenue_growth[period] == pytest.approx(
            expected_rev_growth, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        growth_comp = growth_by_period[period.isoformat()]
        diff_comp = difference_by_period[period.isoformat()]
        current_rev = revenue_by_period[period.isoformat()]
        prior_rev = revenue_by_period[prior.isoformat()]
        store_growth_comp = store_growth_by_period[period.isoformat()]
        assert tuple(growth_comp.depends_on) == (current_rev.id, prior_rev.id)
        assert tuple(diff_comp.depends_on) == (
            growth_comp.id,
            store_growth_comp.id,
        )
        current_ref = SemanticCellRef(
            id=current_rev.id,
            semantic_key=current_rev.semantic_key,
            period_end=current_rev.period_end,
            cell=current_rev.cell,
            tab=current_rev.tab,
        )
        prior_ref = SemanticCellRef(
            id=prior_rev.id,
            semantic_key=prior_rev.semantic_key,
            period_end=prior_rev.period_end,
            cell=prior_rev.cell,
            tab=prior_rev.tab,
        )
        compact_growth = growth_comp.formula.replace(" ", "")
        expected_growth_f = resolve_revenue_store_growth_formula(
            current_ref, prior_ref, from_tab=STORE_COUNT_SHEET
        ).replace(" ", "")
        assert compact_growth == expected_growth_f
        current_row, current_col = parse_cell_ref(current_rev.cell)
        prior_row, prior_col = parse_cell_ref(prior_rev.cell)
        assert current_col != prior_col + 1
        adjacent_prior = f"{get_column_letter(current_col - 1)}{current_row}"
        default_current = (
            f"{get_column_letter(2 + axis.index(period))}"
            f"{DEFAULT_REVENUE_STORE_SOURCE_ROW}"
        )
        default_prior = (
            f"{get_column_letter(2 + axis.index(prior))}"
            f"{DEFAULT_REVENUE_STORE_SOURCE_ROW}"
        )
        assert adjacent_prior not in compact_growth
        assert default_current not in compact_growth
        assert default_prior not in compact_growth
        growth_ref = SemanticCellRef(
            id=growth_comp.id,
            semantic_key=growth_comp.semantic_key,
            period_end=growth_comp.period_end,
            cell=growth_comp.cell,
            tab=growth_comp.tab,
        )
        store_ref = SemanticCellRef(
            id=store_growth_comp.id,
            semantic_key=store_growth_comp.semantic_key,
            period_end=store_growth_comp.period_end,
            cell=store_growth_comp.cell,
            tab=store_growth_comp.tab,
        )
        compact_diff = diff_comp.formula.replace(" ", "")
        assert compact_diff == resolve_revenue_store_difference_formula(
            growth_ref, store_ref, from_tab=STORE_COUNT_SHEET
        ).replace(" ", "")
        assert growth_comp.expected_value == pytest.approx(
            expected_rev_growth, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        assert diff_comp.expected_value == pytest.approx(
            expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
        a_growth = awb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        t_growth = twb[growth_comp.tab].cell(*parse_cell_ref(growth_comp.cell))
        a_diff = awb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
        t_diff = twb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
        assert str(a_growth.value).replace(" ", "") == compact_growth
        assert str(a_diff.value).replace(" ", "") == compact_diff
        assert t_growth.value in (None, "")
        assert t_diff.value in (None, "")
        assert t_growth.comment is None
        assert t_diff.comment is None
        assert _fill_rgb(t_growth) == "FFFF00"
        assert _fill_rgb(t_diff) == "FFFF00"
        assert _fill_rgb(a_growth) in WHITE_RGBS
        assert _fill_rgb(a_diff) in WHITE_RGBS
        assert (a_growth.comment.text or "").strip()
        assert (a_diff.comment.text or "").strip()

    awb.close()
    twb.close()
    _assert_visible_parity(trainer, answer, practice)
    _assert_fresh_visible_style(trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer)

    answer_hash = _sha256(answer)
    blank = check_workbook(trainer)
    total = (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
    )
    assert (blank.total, blank.blank, blank.correct, blank.incorrect) == (
        total,
        total,
        0,
        0,
    )
    dumped_blank = repr(blank)
    assert "100*(" not in dumped_blank
    assert "Growth difference" not in dumped_blank

    filled_trainer, filled_answer = _copy_pair(
        trainer, answer, tmp_path / "rev_moved_filled_check"
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
        filled_trainer, filled_answer, tmp_path / "rev_moved_incorrect_check"
    )
    bad = next(
        c
        for c in relationship_comps
        if c.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
        and c.period_end == P2026.isoformat()
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
        trainer, answer, tmp_path / "rev_moved_tamper"
    )
    moved_row, moved_col = MOVED_REVENUE_STORE_SOURCE_PLACEMENT[0]
    wb = load_workbook(tamper_trainer, data_only=False)
    wb[STORE_COUNT_SHEET].cell(moved_row, moved_col).value = 1
    wb.save(tamper_trainer)
    wb.close()
    with pytest.raises(
        ValueError,
        match="Trusted workbook cell was modified: Store Count Analysis",
    ):
        check_workbook(tamper_trainer)


def _compsales_tiny(*observations, extra_opening: date | None = None, stores=(), **kwargs):
    return _store_tiny(*stores, extra_opening=extra_opening, management=list(observations), **kwargs)


def _write_selected_spsf(
    dest: Path,
    period: str,
    values: tuple[object, object],
    *,
    definition: str,
    week: bool,
    reporting_basis: str,
    left,
    right,
):
    _write_selected_on_docs(
        dest,
        FAMILY_SALES_PER_SQUARE_FOOT,
        left,
        right,
        period=period,
        values=values,
        definition=definition,
        week=week,
        reporting_basis=reporting_basis,
    )


def _write_selected_global_compsales(
    dest: Path,
    period: str,
    values: tuple[object, object],
    *,
    definition: str,
    week: bool,
    reporting_basis: str,
    left,
    right,
):
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        left,
        right,
        period=period,
        values=values,
        definition=definition,
        week=week,
        reporting_basis=reporting_basis,
    )


def test_comparable_sales_catalog_orders_and_expand_identities():
    assert COMPARABLE_SALES_SHEET == COMPARABLE_SALES_SHEET_NAME
    assert [family.order for family in COMPARABLE_SALES_COMPONENT_CATALOG] == [167, 168]
    assert [family.id for family in COMPARABLE_SALES_COMPONENT_CATALOG] == [
        COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
        COMPARABLE_SALES_CHANGE_FAMILY_ID,
    ]
    assert [family.order for family in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG] == [
        170,
        171,
        172,
    ]
    assert [family.id for family in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG] == [
        SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
    ]
    item = _compsales(period=P2, value=2.0)
    identity = _identity_of(item)
    other = _compsales(period=P2, value=6.0, population=POP_STORES_AND_DTC)
    other_id = _identity_of(other)
    assert identity != other_id
    sources = expand_comparable_sales_source_specs(
        [P1, P2],
        start_order=1,
        identities=(identity, other_id),
        source_periods_by_identity={identity: (P2,), other_id: (P1, P2)},
    )
    assert [s.id for s in sources] == [
        comparable_sales_source_component_id(P2, identity),
        comparable_sales_source_component_id(P1, other_id),
        comparable_sales_source_component_id(P2, other_id),
    ]
    assert sources[0].semantic_key == comparable_sales_source_semantic_key(P2, identity)
    assert all(s.category == COMPARABLE_SALES_SOURCE_CATEGORY for s in sources)
    assert all(s.depends_on == () for s in sources)
    specs = expand_comparable_sales_specs(
        [P1, P2],
        start_order=10,
        identities=(identity,),
        difference_periods_by_identity={identity: (P2,)},
    )
    assert [s.id for s in specs] == [
        comparable_sales_component_id(
            COMPARABLE_SALES_DIFFERENCE_FAMILY_ID, P2, identity
        )
    ]
    assert specs[0].depends_on == comparable_sales_difference_dependency_ids(
        P2, identity
    )
    changes = expand_comparable_sales_change_specs(
        [P1, P2],
        start_order=20,
        identities=(identity,),
        change_periods_by_identity={identity: (P2,)},
    )
    assert [s.id for s in changes] == [
        comparable_sales_component_id(
            COMPARABLE_SALES_CHANGE_FAMILY_ID, P2, identity
        )
    ]
    assert changes[0].depends_on == comparable_sales_change_dependency_ids(
        [P1, P2], P2, identity
    )
    spsf_item = _spsf(period=P2, value=1430)
    spsf_id = _identity_of(spsf_item)
    spsf_sources = expand_sales_per_square_foot_source_specs(
        [P1, P2],
        start_order=1,
        identities=(spsf_id,),
        source_periods_by_identity={spsf_id: (P1, P2)},
    )
    assert spsf_sources[0].id == sales_per_square_foot_source_component_id(P1, spsf_id)
    assert spsf_sources[0].semantic_key == sales_per_square_foot_source_semantic_key(
        P1, spsf_id
    )
    spsf_specs = expand_sales_per_square_foot_specs(
        [P1, P2],
        start_order=30,
        identities=(spsf_id,),
        change_periods_by_identity={spsf_id: (P2,)},
        growth_periods_by_identity={spsf_id: (P2,)},
    )
    assert [s.family_id for s in spsf_specs] == [
        SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
    ]
    diffs = expand_sales_per_square_foot_difference_specs(
        [P1, P2],
        start_order=40,
        identities=(spsf_id,),
        difference_periods_by_identity={spsf_id: (P2,)},
    )
    assert [s.family_id for s in diffs] == [SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID]
    assert diffs[0].depends_on == sales_per_square_foot_difference_dependency_ids(
        P2, spsf_id
    )
    assert not any(s.period_end == P1.isoformat() for s in specs)
    with pytest.raises(ValueError, match="duplicate fiscal periods"):
        expand_comparable_sales_specs(
            [P1, P1],
            start_order=1,
            identities=(identity,),
            difference_periods_by_identity={identity: ()},
        )
    with pytest.raises(ValueError, match="strictly chronological"):
        expand_comparable_sales_change_specs(
            [P2, P1],
            start_order=1,
            identities=(identity,),
            change_periods_by_identity={identity: (P2,)},
        )
    with pytest.raises(ValueError, match="duplicate identities"):
        expand_comparable_sales_source_specs(
            [P1, P2],
            start_order=1,
            identities=(identity, identity),
            source_periods_by_identity={identity: (P2,)},
        )
    with pytest.raises(ValueError, match="duplicate identities"):
        expand_sales_per_square_foot_specs(
            [P1, P2],
            start_order=1,
            identities=(spsf_id, spsf_id),
            change_periods_by_identity={spsf_id: ()},
            growth_periods_by_identity={spsf_id: ()},
        )


def test_comparable_sales_formula_resolution_follows_mapped_identities():
    growth = SemanticCellRef(
        id=revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, P2),
        semantic_key="operating_kpi.revenue_store.revenue_growth",
        period_end=P2.isoformat(),
        cell="C12",
        tab=STORE_COUNT_SHEET_NAME,
    )
    compsales = SemanticCellRef(
        id=comparable_sales_source_component_id(P2, "id"),
        semantic_key="operating_kpi.comparable_sales.source",
        period_end=P2.isoformat(),
        cell="I28",
        tab=COMPARABLE_SALES_SHEET_NAME,
    )
    difference = resolve_revenue_comparable_sales_difference_formula(
        growth, compsales, from_tab=COMPARABLE_SALES_SHEET_NAME
    )
    assert difference == "=100*'Store Count Analysis'!C12-I28"
    reversed_difference = resolve_revenue_comparable_sales_difference_formula(
        compsales, growth, from_tab=COMPARABLE_SALES_SHEET_NAME
    )
    assert reversed_difference != difference
    assert "100*(" not in difference
    same_sheet_growth = SemanticCellRef(
        id=growth.id,
        semantic_key=growth.semantic_key,
        period_end=growth.period_end,
        cell="C12",
        tab=COMPARABLE_SALES_SHEET_NAME,
    )
    local = resolve_revenue_comparable_sales_difference_formula(
        same_sheet_growth, compsales, from_tab=COMPARABLE_SALES_SHEET_NAME
    )
    assert local == "=100*C12-I28"
    with pytest.raises(ValueError, match="mapped coordinate"):
        resolve_revenue_comparable_sales_difference_formula(
            SemanticCellRef("a", "a", P2.isoformat(), "", STORE_COUNT_SHEET_NAME),
            compsales,
            from_tab=COMPARABLE_SALES_SHEET_NAME,
        )
    prior = SemanticCellRef(
        id=comparable_sales_source_component_id(P1, "id"),
        semantic_key="operating_kpi.comparable_sales.source",
        period_end=P1.isoformat(),
        cell="D44",
        tab="Income Statement",
    )
    change = resolve_management_kpi_adjacent_change_formula(
        compsales, prior, from_tab=COMPARABLE_SALES_SHEET_NAME
    )
    assert change == "=I28-'Income Statement'!D44"
    spsf_current = SemanticCellRef(
        id=sales_per_square_foot_source_component_id(P2, "id"),
        semantic_key="operating_kpi.sales_per_square_foot.source",
        period_end=P2.isoformat(),
        cell="C28",
        tab=SALES_PER_SQUARE_FOOT_SHEET_NAME,
    )
    spsf_prior = SemanticCellRef(
        id=sales_per_square_foot_source_component_id(P1, "id"),
        semantic_key="operating_kpi.sales_per_square_foot.source",
        period_end=P1.isoformat(),
        cell="G52",
        tab="Income Statement",
    )
    spsf_change = resolve_management_kpi_adjacent_change_formula(
        spsf_current, spsf_prior, from_tab=SALES_PER_SQUARE_FOOT_SHEET_NAME
    )
    spsf_growth = resolve_management_kpi_growth_formula(
        spsf_current, spsf_prior, from_tab=SALES_PER_SQUARE_FOOT_SHEET_NAME
    )
    assert spsf_change == "=C28-'Income Statement'!G52"
    assert spsf_growth == (
        "=IF('Income Statement'!G52=0,NA(),(C28-'Income Statement'!G52)/"
        "'Income Statement'!G52)"
    )
    spsf_diff = resolve_revenue_sales_per_square_foot_difference_formula(
        growth, spsf_current, from_tab=SALES_PER_SQUARE_FOOT_SHEET_NAME
    )
    assert spsf_diff == "=100*('Store Count Analysis'!C12-C28)"


def test_ineligible_histories_do_not_activate_comparable_sales(tmp_path):
    absent = _tiny(with_payments=False)
    trainer, answer = build_training_workbook(absent, tmp_path / "COMP_ABSENT.xlsx")
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert COMPARABLE_SALES_SHEET not in wb.sheetnames
        wb.close()

    spsf_only = _compsales_tiny(_spsf(period=P2, value=1426))
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(spsf_only) is False
    trainer, answer = build_training_workbook(spsf_only, tmp_path / "COMP_SPSF.xlsx")
    smap = load_semantic_map(answer)
    assert COMPARABLE_SALES_SHEET not in load_workbook(answer).sheetnames
    assert SALES_PER_SQUARE_FOOT_SHEET in load_workbook(answer).sheetnames
    assert _spsf_source_components(smap)
    assert not any(is_comparable_sales_practice_identity(c) for c in smap.all_ordered())

    excluded = _compsales_tiny(
        _compsales(period=P2, value=4.0, geography="americas"),
        _compsales(period=P2, value=1.5, geography="global", basis="constant_dollar"),
    )
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(excluded) is False
    trainer, answer = build_training_workbook(excluded, tmp_path / "COMP_EXCL.xlsx")
    smap = load_semantic_map(answer)
    assert COMPARABLE_SALES_SHEET in load_workbook(answer).sheetnames
    assert _compsales_source_components(smap)
    assert _compsales_difference_components(smap) == []
    assert SALES_PER_SQUARE_FOOT_SHEET not in load_workbook(answer).sheetnames

    store_only = _store_tiny(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767))
    trainer, answer = build_training_workbook(store_only, tmp_path / "COMP_STORE.xlsx")
    smap = load_semantic_map(answer)
    assert not any(is_comparable_sales_practice_identity(c) for c in smap.all_ordered())
    wb = load_workbook(answer)
    assert COMPARABLE_SALES_SHEET not in wb.sheetnames
    assert STORE_COUNT_SHEET in wb.sheetnames
    wb.close()


def test_comparable_sales_only_and_mixed_reuse_revenue_growth(tmp_path):
    only = _compsales_tiny(_compsales(period=P1, value=2.0), _compsales(period=P2, value=4.0))
    builder = ReferenceModelBuilder(only)
    assert builder.operating_kpi_series is None
    assert builder.operating_kpi_relationship is None
    trainer, answer = build_training_workbook(only, tmp_path / "COMP_ONLY.xlsx")
    smap = load_semantic_map(answer)
    growth = [c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID]
    diffs = _compsales_difference_components(smap)
    changes = _compsales_change_components(smap)
    sources = _compsales_source_components(smap)
    revenue_sources = _revenue_source_components(smap)
    assert len(growth) == 1
    assert len(diffs) == 1
    assert len(changes) == 1
    assert len(sources) == 2
    assert len(revenue_sources) == 2
    assert growth[0].tab == COMPARABLE_SALES_SHEET
    series = next(iter(builder.operating_kpi_compsales_relationship.series.values()))
    expected_growth = (1100.0 - 1000.0) / 1000.0
    expected_diff = 100.0 * expected_growth - 4.0
    assert series.growth_difference_pp[P2] == pytest.approx(
        expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[COMPARABLE_SALES_SHEET]
    assert aws["A5"].value == COMPARABLE_SALES_SCOPE_NOTE
    source_row = _row_by_label(
        aws, "Reported comparable-sales growth (percent; 2 means 2%)"
    )
    assert aws.cell(source_row, 2).value == 2.0
    assert "%" in str(aws.cell(source_row, 2).number_format)
    diff_comp = diffs[0]
    a_diff = awb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
    t_diff = twb[diff_comp.tab].cell(*parse_cell_ref(diff_comp.cell))
    assert t_diff.value in (None, "")
    assert t_diff.comment is None
    assert _fill_rgb(t_diff) == "FFFF00"
    assert _fill_rgb(a_diff) in WHITE_RGBS
    assert (a_diff.comment.text or "").strip()
    _assert_no_disclosed_store_arithmetic(twb)
    _assert_answer_key_no_yellow(answer)
    awb.close()
    twb.close()
    assert_bav_has_no_exercise_framing(answer)

    mixed = _compsales_tiny(
        _compsales(period=P1, value=2.0),
        _compsales(period=P2, value=4.0),
        stores=(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767)),
    )
    mixed_trainer, mixed_answer = build_training_workbook(
        mixed, tmp_path / "COMP_MIXED.xlsx"
    )
    mmap = load_semantic_map(mixed_answer)
    mixed_growth = [
        c for c in mmap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID
    ]
    store_diffs = [
        c for c in mmap.all_ordered() if c.family_id == REVENUE_STORE_DIFFERENCE_FAMILY_ID
    ]
    compsales_diffs = _compsales_difference_components(mmap)
    compsales_changes = _compsales_change_components(mmap)
    assert len(mixed_growth) == 1
    assert len(store_diffs) == 1
    assert len(compsales_diffs) == 1
    assert len(compsales_changes) == 1
    assert mixed_growth[0].tab == STORE_COUNT_SHEET
    assert compsales_diffs[0].tab == COMPARABLE_SALES_SHEET
    source_comp = next(
        c for c in _compsales_source_components(mmap) if c.period_end == P2.isoformat()
    )
    compact = compsales_diffs[0].formula.replace(" ", "")
    assert compact == resolve_revenue_comparable_sales_difference_formula(
        SemanticCellRef(
            mixed_growth[0].id,
            mixed_growth[0].semantic_key,
            mixed_growth[0].period_end,
            mixed_growth[0].cell,
            mixed_growth[0].tab,
        ),
        SemanticCellRef(
            source_comp.id,
            source_comp.semantic_key,
            source_comp.period_end,
            source_comp.cell,
            source_comp.tab,
        ),
        from_tab=COMPARABLE_SALES_SHEET,
    ).replace(" ", "")
    mwb = load_workbook(mixed_answer)
    assert STORE_COUNT_SHEET in mwb.sheetnames
    assert COMPARABLE_SALES_SHEET in mwb.sheetnames
    mwb.close()
    assert Path(mixed_trainer).is_file()


def test_spsf_only_workbook_supplies_shared_revenue(tmp_path):
    only = _compsales_tiny(_spsf(period=P1, value=1410), _spsf(period=P2, value=1430))
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(only) is False
    assert operating_kpi_revenue_store_relationship_applicable(only) is False
    assert operating_kpi_revenue_sales_per_square_foot_relationship_applicable(only) is True
    builder = ReferenceModelBuilder(only)
    assert builder.operating_kpi_series is None
    assert builder.operating_kpi_relationship is None
    assert builder.operating_kpi_compsales_relationship is None
    trainer, answer = build_training_workbook(only, tmp_path / "SPSF_ONLY.xlsx")
    assert {path.name for path in tmp_path.glob("*.xlsx")} == {
        "SPSF_ONLY_BAV_Trainer.xlsx",
        "SPSF_ONLY_BAV.xlsx",
    }
    smap = load_semantic_map(answer)
    growth = [c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID]
    revenue_sources = _revenue_source_components(smap)
    spsf_sources = _spsf_source_components(smap)
    spsf_diffs = _spsf_difference_components(smap)
    spsf_growth = next(
        c
        for c in _spsf_practice_components(smap)
        if c.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID
    )
    assert len(growth) == 1
    assert len(revenue_sources) == 2
    assert len(spsf_sources) == 2
    assert len(spsf_diffs) == 1
    assert growth[0].tab == SALES_PER_SQUARE_FOOT_SHEET
    expected_rev = (1100.0 - 1000.0) / 1000.0
    expected_spsf = 20.0 / 1410.0
    assert spsf_growth.expected_value == pytest.approx(expected_spsf, abs=1e-12)
    assert spsf_diffs[0].expected_value == pytest.approx(
        100.0 * (expected_rev - expected_spsf),
        abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE,
    )
    compact = spsf_diffs[0].formula.replace(" ", "")
    assert compact == resolve_revenue_sales_per_square_foot_difference_formula(
        SemanticCellRef(
            growth[0].id,
            growth[0].semantic_key,
            growth[0].period_end,
            growth[0].cell,
            growth[0].tab,
        ),
        SemanticCellRef(
            spsf_growth.id,
            spsf_growth.semantic_key,
            spsf_growth.period_end,
            spsf_growth.cell,
            spsf_growth.tab,
        ),
        from_tab=SALES_PER_SQUARE_FOOT_SHEET,
    ).replace(" ", "")
    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[SALES_PER_SQUARE_FOOT_SHEET]
    assert SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE in str(aws["A4"].value)
    assert "without a prior period" in str(aws["A4"].value)
    _assert_spsf_a5_non_disclosing(aws["A5"].value)
    _assert_trainer_management_history_undisclosed(twb)
    _assert_answer_key_management_history_undisclosed(awb)
    a_diff = awb[spsf_diffs[0].tab].cell(*parse_cell_ref(spsf_diffs[0].cell))
    t_diff = twb[spsf_diffs[0].tab].cell(*parse_cell_ref(spsf_diffs[0].cell))
    assert t_diff.value in (None, "")
    assert t_diff.comment is None
    assert _fill_rgb(t_diff) == "FFFF00"
    assert _fill_rgb(a_diff) in WHITE_RGBS
    assert (a_diff.comment.text or "").strip()
    _assert_answer_key_no_yellow(answer)
    awb.close()
    twb.close()
    assert_bav_has_no_exercise_framing(answer)
    assert COMPARABLE_SALES_SHEET not in load_workbook(answer).sheetnames
    assert STORE_COUNT_SHEET not in load_workbook(answer).sheetnames


def test_multiple_isolated_identities_are_not_merged(tmp_path):
    ecom = _compsales(period=P2, value=4.0, population=POP_STORES_AND_ECOMMERCE)
    dtc = _compsales(period=P2, value=6.0, population=POP_STORES_AND_DTC)
    fin = _compsales_tiny(ecom, dtc)
    result = compute_operating_kpi_revenue_comparable_sales_relationship(fin)
    assert len(result.identities) == 2
    trainer, answer = build_training_workbook(fin, tmp_path / "COMP_IDS.xlsx")
    smap = load_semantic_map(answer)
    diffs = _compsales_difference_components(smap)
    sources = _compsales_source_components(smap)
    assert len(diffs) == 2
    assert len(sources) == 2
    expected_growth = (1100.0 - 1000.0) / 1000.0
    expected = {
        _identity_of(ecom): 100.0 * expected_growth - 4.0,
        _identity_of(dtc): 100.0 * expected_growth - 6.0,
    }
    for comp in diffs:
        identity = next(
            item
            for item in result.identities
            if comparable_sales_identity_token(item) == operating_kpi_spec_identity(comp)
        )
        assert comp.expected_value == pytest.approx(
            expected[identity], abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
        )
    assert Path(trainer).is_file()


def test_comparable_sales_sparse_zero_decline_and_percent_scaling(tmp_path):
    singleton = _compsales_tiny(_compsales(period=P2, value=2.0))
    trainer, answer = build_training_workbook(singleton, tmp_path / "COMP_SINGLE.xlsx")
    smap = load_semantic_map(answer)
    assert [c.period_end for c in _compsales_source_components(smap)] == [P2.isoformat()]

    sparse = _compsales_tiny(
        _compsales(period=P0, value=1.0),
        _compsales(period=P2, value=4.0),
        extra_opening=P0,
    )
    sparse_series = next(
        iter(ReferenceModelBuilder(sparse).operating_kpi_compsales_relationship.series.values())
    )
    assert sparse_series.comparable_sales_growth[P1] == SOURCE_UNAVAILABLE
    assert sparse_series.growth_difference_pp[P1] == SOURCE_UNAVAILABLE
    assert sparse_series.comparable_sales_growth[P2] == 4.0

    zero_open = _compsales_tiny(
        _compsales(period=P1, value=2.0), _compsales(period=P2, value=4.0)
    )
    for item in zero_open.income_statement:
        if item.concept == "revenue":
            item.values[P1] = 0.0
            item.values[P2] = 10.0
    zero_series = next(
        iter(ReferenceModelBuilder(zero_open).operating_kpi_compsales_relationship.series.values())
    )
    assert zero_series.revenue_growth[P2] == UNDEFINED_RATIO
    assert zero_series.growth_difference_pp[P2] == UNDEFINED_RATIO
    z_trainer, z_answer = build_training_workbook(zero_open, tmp_path / "COMP_ZERO.xlsx")
    zawb = load_workbook(z_answer, data_only=False)
    z_growth = _row_by_label(
        zawb[COMPARABLE_SALES_SHEET],
        "Consolidated revenue growth (statement-derived)",
    )
    assert "NA()" in str(zawb[COMPARABLE_SALES_SHEET].cell(z_growth, 3).value)
    zawb.close()

    decline = _compsales_tiny(
        _compsales(period=P1, value=-3.0), _compsales(period=P2, value=-1.0)
    )
    for item in decline.income_statement:
        if item.concept == "revenue":
            item.values[P1] = 200.0
            item.values[P2] = 160.0
    decline_series = next(
        iter(compute_operating_kpi_revenue_comparable_sales_relationship(decline).series.values())
    )
    expected_rev = (160.0 - 200.0) / 200.0
    expected_diff = 100.0 * expected_rev - (-1.0)
    assert decline_series.growth_difference_pp[P2] == pytest.approx(
        expected_diff, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )

    fraction = _compsales_tiny(
        _compsales(period=P1, value=0.10), _compsales(period=P2, value=0.08)
    )
    f_trainer, f_answer = build_training_workbook(fraction, tmp_path / "COMP_FRAC.xlsx")
    fawb = load_workbook(f_answer, data_only=False)
    f_source = _row_by_label(
        fawb[COMPARABLE_SALES_SHEET],
        "Reported comparable-sales growth (percent; 2 means 2%)",
    )
    assert fawb[COMPARABLE_SALES_SHEET].cell(f_source, 3).value == 0.08
    fawb.close()
    assert Path(trainer).is_file()
    assert Path(z_trainer).is_file()
    assert Path(f_trainer).is_file()


def test_comparable_sales_missing_revenue_fails_closed_without_mutation():
    missing = _compsales_tiny(
        _compsales(period=P1, value=2.0), _compsales(period=P2, value=4.0)
    )
    for item in missing.income_statement:
        if item.concept == "revenue":
            item.values[P2] = None
    original = copy.deepcopy(missing.income_statement)
    original_kpi = copy.deepcopy(missing.historical_operating_kpis)
    with pytest.raises(MissingHistoricalValueError, match="no supplied value"):
        ReferenceModelBuilder(missing)
    assert missing.income_statement == original
    assert missing.historical_operating_kpis == original_kpi

    api = _fin_with_relationship(
        management=[_compsales(period=P1, value=2.0), _compsales(period=P2, value=4.0)],
        revenue={P1: 100.0},
    )
    before = copy.deepcopy(api.income_statement)
    series = next(
        iter(compute_operating_kpi_revenue_comparable_sales_relationship(api).series.values())
    )
    assert series.revenue[P2] == SOURCE_UNAVAILABLE
    assert series.comparable_sales_growth[P2] == 4.0
    assert api.income_statement == before

    ambiguous = _compsales_tiny(_compsales(period=P2, value=2.0))
    ambiguous.income_statement.append(copy.deepcopy(ambiguous.income_statement[0]))
    ambiguous.income_statement[-1].label = "Turnover"
    original = copy.deepcopy(ambiguous.income_statement)
    original_kpi = copy.deepcopy(ambiguous.historical_operating_kpis)
    with pytest.raises(AmbiguousLineError, match="Ambiguous concept='revenue'"):
        ReferenceModelBuilder(ambiguous)
    assert ambiguous.income_statement == original
    assert ambiguous.historical_operating_kpis == original_kpi


def test_reviewed_spsf_a5_disclosure_fails_before_repair():
    with pytest.raises(AssertionError):
        _assert_spsf_a5_non_disclosing(REVIEWED_SPSF_A5_DISCLOSURE)
    _assert_spsf_a5_non_disclosing(SALES_PER_SQUARE_FOOT_SCOPE_NOTE)
    assert SALES_PER_SQUARE_FOOT_SCOPE_NOTE != REVIEWED_SPSF_A5_DISCLOSURE


def test_selected_document_compsales_workbook_uses_test_augmentation(tmp_path):
    before = _bytes_by_name(EXTRACTED)
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "handoff")
    _write_selected_global_compsales(
        dest,
        P2023.isoformat(),
        (-3, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[0],
        right=MANAGEMENT_NAMES[1],
    )
    _write_selected_global_compsales(
        dest,
        P2024.isoformat(),
        (5, 7),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[2],
        right=MANAGEMENT_NAMES[3],
    )
    _write_selected_spsf(
        dest,
        P2023.isoformat(),
        (1400, 1410),
        definition=DEF_SPSF,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[0],
        right=MANAGEMENT_NAMES[1],
    )
    _write_selected_spsf(
        dest,
        P2024.isoformat(),
        (1410, 1430),
        definition=DEF_SPSF,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[2],
        right=MANAGEMENT_NAMES[3],
    )
    restored = standardized_from_payload(
        standardized_to_payload(
            standardize_reconciled(_reconcile(dest, admit=ADMIT_2022))
        )
    )
    assert operating_kpi_applicable(restored) is False
    series = next(
        iter(compute_operating_kpi_revenue_comparable_sales_relationship(restored).series.values())
    )
    expected_rev_2023 = (
        REVENUE_ANCHORS[P2023] - REVENUE_ANCHORS[P2022]
    ) / REVENUE_ANCHORS[P2022]
    expected_rev_2024 = (
        REVENUE_ANCHORS[P2024] - REVENUE_ANCHORS[P2023]
    ) / REVENUE_ANCHORS[P2023]
    expected_diff_2023 = 100.0 * expected_rev_2023 - 2
    expected_diff_2024 = 100.0 * expected_rev_2024 - 7
    assert abs(series.growth_difference_pp[P2023] - expected_diff_2023) <= (
        OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert abs(series.growth_difference_pp[P2024] - expected_diff_2024) <= (
        OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    management = compute_management_kpi_series(restored)
    compsales_hist = next(
        item
        for item in management.series.values()
        if item.family == FAMILY_COMPARABLE_SALES_GROWTH
        and item.geography == "global"
        and item.basis == "reported"
    )
    spsf_hist = next(
        item
        for item in management.series.values()
        if item.family == FAMILY_SALES_PER_SQUARE_FOOT
    )
    assert compsales_hist.reported_value[P2023] == 2
    assert compsales_hist.reported_value[P2024] == 7
    assert compsales_hist.adjacent_change[P2024] == 5
    assert abs(compsales_hist.adjacent_change[P2024] - (7 - 2)) <= 1e-12
    assert spsf_hist.reported_value[P2023] == 1410
    assert spsf_hist.reported_value[P2024] == 1430
    assert spsf_hist.adjacent_change[P2024] == 20
    assert abs(spsf_hist.growth[P2024] - (20 / 1410)) <= 1e-12
    trainer, answer = build_training_workbook(restored, tmp_path / "COMP_SELECTED.xlsx")
    assert {path.name for path in tmp_path.glob("*.xlsx")} == {
        "COMP_SELECTED_BAV_Trainer.xlsx",
        "COMP_SELECTED_BAV.xlsx",
    }
    twb_before = load_workbook(trainer, data_only=False)
    _assert_trainer_management_history_undisclosed(twb_before)
    a5_before = twb_before[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value
    twb_before.close()
    awb_before = load_workbook(answer, data_only=False)
    _assert_answer_key_management_history_undisclosed(awb_before)
    assert awb_before[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value == a5_before
    awb_before.close()
    reloaded_trainer = _reserialize_xlsx(
        trainer, tmp_path / "reserialized" / trainer.name
    )
    twb_reloaded = load_workbook(reloaded_trainer, data_only=False)
    _assert_trainer_management_history_undisclosed(twb_reloaded)
    assert twb_reloaded[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value == a5_before
    twb_reloaded.close()
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_comp_selected")
    smap = load_semantic_map(answer)
    diffs = _compsales_difference_components(smap)
    changes = _compsales_change_components(smap)
    sources = _compsales_source_components(smap)
    spsf_sources = _spsf_source_components(smap)
    spsf_practice = _spsf_practice_components(smap)
    spsf_diffs = _spsf_difference_components(smap)
    growth = [c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID]
    assert len(sources) == 2
    assert len(diffs) == 2
    assert len(changes) == 1
    assert len(growth) == 4
    assert len(spsf_sources) == 2
    assert len(spsf_practice) == 3
    assert len(spsf_diffs) == 1
    by_period = {c.period_end: c for c in diffs}
    assert by_period[P2023.isoformat()].expected_value == pytest.approx(
        expected_diff_2023, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert by_period[P2024.isoformat()].expected_value == pytest.approx(
        expected_diff_2024, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert changes[0].period_end == P2024.isoformat()
    assert changes[0].expected_value == pytest.approx(5, abs=1e-12)
    spsf_change = next(
        c for c in spsf_practice if c.family_id == SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID
    )
    spsf_growth = next(
        c for c in spsf_practice if c.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID
    )
    assert spsf_change.expected_value == pytest.approx(20, abs=1e-12)
    assert spsf_growth.expected_value == pytest.approx(20 / 1410, abs=1e-12)
    expected_spsf_diff_2024 = 100.0 * (expected_rev_2024 - (20 / 1410))
    assert spsf_diffs[0].period_end == P2024.isoformat()
    assert spsf_diffs[0].expected_value == pytest.approx(
        expected_spsf_diff_2024, abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    compact_spsf = spsf_diffs[0].formula.replace(" ", "")
    revenue_growth_2024 = next(c for c in growth if c.period_end == P2024.isoformat())
    assert compact_spsf == resolve_revenue_sales_per_square_foot_difference_formula(
        SemanticCellRef(
            revenue_growth_2024.id,
            revenue_growth_2024.semantic_key,
            revenue_growth_2024.period_end,
            revenue_growth_2024.cell,
            revenue_growth_2024.tab,
        ),
        SemanticCellRef(
            spsf_growth.id,
            spsf_growth.semantic_key,
            spsf_growth.period_end,
            spsf_growth.cell,
            spsf_growth.tab,
        ),
        from_tab=SALES_PER_SQUARE_FOOT_SHEET,
    ).replace(" ", "")
    practice = {(c.tab, c.cell) for c in _check_components(smap)}
    _assert_visible_parity(trainer, answer, practice)
    _assert_fresh_visible_style(trainer, practice_cells=practice, role="trainer")
    _assert_fresh_visible_style(answer, practice_cells=practice, role="answer_key")
    _assert_answer_key_no_yellow(answer)
    twb = load_workbook(trainer, data_only=False)
    awb = load_workbook(answer, data_only=False)
    _assert_trainer_management_history_undisclosed(twb)
    _assert_answer_key_management_history_undisclosed(awb)
    assert twb[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value == SALES_PER_SQUARE_FOOT_SCOPE_NOTE
    assert awb[SALES_PER_SQUARE_FOOT_SHEET]["A5"].value == SALES_PER_SQUARE_FOOT_SCOPE_NOTE
    assert SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE in str(
        twb[SALES_PER_SQUARE_FOOT_SHEET]["A4"].value
    )
    assert SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE in str(
        awb[SALES_PER_SQUARE_FOOT_SHEET]["A4"].value
    )
    assert awb[COMPARABLE_SALES_SHEET]["A5"].value == COMPARABLE_SALES_SCOPE_NOTE
    change_note = (
        awb[spsf_change.tab].cell(*parse_cell_ref(spsf_change.cell)).comment.text or ""
    )
    growth_note = (
        awb[spsf_growth.tab].cell(*parse_cell_ref(spsf_growth.cell)).comment.text or ""
    )
    assert "minus" in change_note.lower()
    assert "(current - prior) / prior" in growth_note.lower()
    for comp in _check_components(smap):
        tcell = twb[comp.tab].cell(*parse_cell_ref(comp.cell))
        assert tcell.value in (None, "")
        assert tcell.comment is None
        acell = awb[comp.tab].cell(*parse_cell_ref(comp.cell))
        assert (acell.comment.text or "").strip()
    twb.close()
    awb.close()
    blank = check_workbook(trainer)
    assert blank.total == LEASE_DT_LULULEMON_SPECS + GEOGRAPHIC_LULULEMON_SPECS + 4 + 2 + 1 + 3
    assert (blank.blank, blank.correct, blank.incorrect) == (blank.total, 0, 0)
    wb = load_workbook(trainer, data_only=False)
    for comp in _check_components(smap):
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    assert "=100*" not in repr(filled)
    assert _bytes_by_name(EXTRACTED) == before


def test_mixed_selected_sparse_2_and_4_preserves_store_fixture(tmp_path):
    dest = _prepare_augmented(tmp_path)
    for name in MANAGEMENT_NAMES:
        Path(dest / name).write_bytes((EXTRACTED / name).read_bytes())
    _write_selected_global_compsales(
        dest,
        P2023.isoformat(),
        (-3, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[0],
        right=MANAGEMENT_NAMES[1],
    )
    _write_selected_global_compsales(
        dest,
        P2025.isoformat(),
        (3, 4),
        definition=DEF_B,
        week=True,
        reporting_basis=REPORTING_BASIS_53,
        left=MANAGEMENT_NAMES[2],
        right=MANAGEMENT_NAMES[3],
    )
    restored = standardized_from_payload(
        standardized_to_payload(
            standardize_reconciled(_reconcile(dest, admit=ADMIT_2022))
        )
    )
    series = next(
        iter(compute_operating_kpi_revenue_comparable_sales_relationship(restored).series.values())
    )
    expected_rev_2023 = (
        REVENUE_ANCHORS[P2023] - REVENUE_ANCHORS[P2022]
    ) / REVENUE_ANCHORS[P2022]
    expected_rev_2025 = (
        REVENUE_ANCHORS[P2025] - REVENUE_ANCHORS[P2024]
    ) / REVENUE_ANCHORS[P2024]
    assert series.comparable_sales_growth[P2023] == 2
    assert series.comparable_sales_growth[P2024] == SOURCE_UNAVAILABLE
    assert series.comparable_sales_growth[P2025] == 4
    assert abs(series.growth_difference_pp[P2023] - (100.0 * expected_rev_2023 - 2)) <= (
        OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    assert abs(series.growth_difference_pp[P2025] - (100.0 * expected_rev_2025 - 4)) <= (
        OPERATING_KPI_RELATIONSHIP_TOLERANCE
    )
    trainer, answer = build_training_workbook(restored, tmp_path / "COMP_MIXED_SEL.xlsx")
    smap = load_semantic_map(answer)
    assert len(_practice_components(smap)) == STORE_COUNT_LULULEMON_SPECS
    assert len(_source_components(smap)) == STORE_COUNT_LULULEMON_SOURCES
    assert len(_relationship_practice_components(smap)) == REVENUE_STORE_LULULEMON_SPECS
    assert len(_revenue_source_components(smap)) == REVENUE_STORE_LULULEMON_SOURCES
    assert len(_compsales_source_components(smap)) == 2
    assert len(_compsales_difference_components(smap)) == 2
    assert _compsales_change_components(smap) == []
    assert len([
        c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID
    ]) == 4
    total = (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
    ) + 2
    blank = check_workbook(trainer)
    assert (blank.total, blank.blank, blank.correct, blank.incorrect) == (
        total, total, 0, 0
    )
    awb = load_workbook(answer, data_only=False)
    aws = awb[COMPARABLE_SALES_SHEET]
    source_row = _row_by_label(
        aws, "Reported comparable-sales growth (percent; 2 means 2%)"
    )
    axis = list(canonical_fiscal_periods(restored))
    assert aws.cell(source_row, 2 + axis.index(P2023)).value == 2
    assert aws.cell(source_row, 2 + axis.index(P2024)).value == SOURCE_UNAVAILABLE
    assert aws.cell(source_row, 2 + axis.index(P2025)).value == 4
    def_row = _row_by_label(aws, "Definition")
    assert aws.cell(def_row, 2 + axis.index(P2023)).value == DEF_A
    assert aws.cell(def_row, 2 + axis.index(P2025)).value == DEF_B
    basis_row = _row_by_label(aws, "Calendar reporting basis")
    assert aws.cell(basis_row, 2 + axis.index(P2025)).value == REPORTING_BASIS_53
    awb.close()


def test_store_fixture_without_compsales_keeps_576(tmp_path):
    _dest, validated = _validated_augmented(tmp_path)
    restored = _reload_admitted_store_histories(validated)[0][2]
    assert operating_kpi_revenue_comparable_sales_relationship_applicable(restored) is False
    trainer, answer = build_training_workbook(restored, tmp_path / "STORE_NO_COMP.xlsx")
    smap = load_semantic_map(answer)
    assert len(_practice_components(smap)) == STORE_COUNT_LULULEMON_SPECS
    assert len(_source_components(smap)) == STORE_COUNT_LULULEMON_SOURCES
    assert len(_relationship_practice_components(smap)) == REVENUE_STORE_LULULEMON_SPECS
    assert len(_revenue_source_components(smap)) == REVENUE_STORE_LULULEMON_SOURCES
    assert _compsales_practice_components(smap) == []
    blank = check_workbook(trainer)
    assert blank.total == (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
    )
    assert COMPARABLE_SALES_SHEET not in load_workbook(answer).sheetnames
    assert SALES_PER_SQUARE_FOOT_SHEET not in load_workbook(answer).sheetnames
    fr = standardized_from_payload(json.loads(FR_JSON.read_text(encoding="utf-8")))
    _fr_trainer, fr_answer = build_training_workbook(fr, tmp_path / "FR_NO_COMP.xlsx")
    assert len(_check_components(load_semantic_map(fr_answer))) == FAST_RETAILING_SPECS
    assert COMPARABLE_SALES_SHEET not in load_workbook(fr_answer).sheetnames
    assert SALES_PER_SQUARE_FOOT_SHEET not in load_workbook(fr_answer).sheetnames


def test_generated_workbooks_follow_moved_revenue_and_compsales_sources(
    tmp_path, monkeypatch
):
    dest = _prepare_augmented(tmp_path)
    for name in MANAGEMENT_NAMES:
        Path(dest / name).write_bytes((EXTRACTED / name).read_bytes())
    _write_selected_global_compsales(
        dest,
        P2023.isoformat(),
        (-3, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
        left=MANAGEMENT_NAMES[0],
        right=MANAGEMENT_NAMES[1],
    )
    _write_selected_global_compsales(
        dest,
        P2025.isoformat(),
        (3, 4),
        definition=DEF_B,
        week=True,
        reporting_basis=REPORTING_BASIS_53,
        left=MANAGEMENT_NAMES[2],
        right=MANAGEMENT_NAMES[3],
    )
    restored = standardized_from_payload(
        standardized_to_payload(
            standardize_reconciled(_reconcile(dest, admit=ADMIT_2022))
        )
    )
    identity = next(
        iter(compute_operating_kpi_revenue_comparable_sales_relationship(restored).identities)
    )

    def _moved_revenue(self, period_index, default_row, default_col):
        return MOVED_REVENUE_STORE_SOURCE_PLACEMENT[period_index]

    def _moved_compsales(self, moved_identity, period_index, default_row, default_col):
        assert moved_identity == identity
        return MOVED_COMPSALES_SOURCE_PLACEMENT[period_index]

    monkeypatch.setattr(
        ReferenceModelBuilder, "_revenue_store_source_placement", _moved_revenue
    )
    monkeypatch.setattr(
        ReferenceModelBuilder, "_comparable_sales_source_placement", _moved_compsales
    )
    trainer, answer = build_training_workbook(restored, tmp_path / "COMP_MOVED.xlsx")
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_comp_moved")
    sidecar = component_map_path_for(answer)
    serialized = json.loads(sidecar.read_text(encoding="utf-8"))
    smap = load_semantic_map(answer)
    revenue_sources = _revenue_source_components(smap)
    compsales_sources = _compsales_source_components(smap)
    diffs = _compsales_difference_components(smap)
    growth = [c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID]
    serialized_by_id = {row["id"]: row for row in serialized["components"]}
    axis = list(canonical_fiscal_periods(restored))
    revenue_by_period = {c.period_end: c for c in revenue_sources}
    for index, period in enumerate(axis):
        row, col = MOVED_REVENUE_STORE_SOURCE_PLACEMENT[index]
        mapped = revenue_by_period[period.isoformat()]
        assert mapped.cell == f"{get_column_letter(col)}{row}"
        assert mapped.tab == STORE_COUNT_SHEET
        assert serialized_by_id[mapped.id]["cell"] == mapped.cell
    compsales_by_period = {c.period_end: c for c in compsales_sources}
    for period in (P2023, P2025):
        index = axis.index(period)
        row, col, tab = MOVED_COMPSALES_SOURCE_PLACEMENT[index]
        mapped = compsales_by_period[period.isoformat()]
        assert mapped.cell == f"{get_column_letter(col)}{row}"
        assert mapped.tab == tab
        assert mapped.tab != COMPARABLE_SALES_SHEET
        diff = next(c for c in diffs if c.period_end == period.isoformat())
        growth_comp = next(c for c in growth if c.period_end == period.isoformat())
        compact_diff = diff.formula.replace(" ", "")
        assert compact_diff == resolve_revenue_comparable_sales_difference_formula(
            SemanticCellRef(
                growth_comp.id,
                growth_comp.semantic_key,
                growth_comp.period_end,
                growth_comp.cell,
                growth_comp.tab,
            ),
            SemanticCellRef(
                mapped.id,
                mapped.semantic_key,
                mapped.period_end,
                mapped.cell,
                mapped.tab,
            ),
            from_tab=COMPARABLE_SALES_SHEET,
        ).replace(" ", "")
        assert mapped.cell in compact_diff
        adjacent = f"{get_column_letter(col - 1)}{row}"
        assert adjacent not in compact_diff
    awb = load_workbook(answer, data_only=False)
    assert awb[compsales_by_period[P2023.isoformat()].tab].cell(
        *parse_cell_ref(compsales_by_period[P2023.isoformat()].cell)
    ).value == 2
    awb.close()
    _assert_answer_key_no_yellow(answer)
    total = (
        LULULEMON_STORE_AUGMENTED_PRACTICE
        + REVENUE_STORE_LULULEMON_SPECS
        + REVENUE_PER_STORE_LULULEMON_SPECS
    ) + 2
    blank = check_workbook(trainer)
    assert (blank.total, blank.blank) == (total, total)
    filled_trainer, filled_answer = _copy_pair(
        trainer, answer, tmp_path / "comp_moved_filled"
    )
    wb = load_workbook(filled_trainer, data_only=False)
    for comp in _check_components(smap):
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(filled_trainer)
    wb.close()
    filled = check_workbook(filled_trainer)
    assert (filled.total, filled.correct, filled.incorrect, filled.blank) == (
        total, total, 0, 0
    )
    incorrect_trainer, _incorrect_answer = _copy_pair(
        filled_trainer, filled_answer, tmp_path / "comp_moved_incorrect"
    )
    bad = next(c for c in diffs if c.period_end == P2025.isoformat())
    _inject_formula_and_cached_value(
        incorrect_trainer, bad.tab, bad.cell, formula="=999", cached_value=999.0
    )
    bad_summary = check_workbook(incorrect_trainer)
    assert bad_summary.incorrect == 1
    assert "=999" not in repr(bad_summary)
    assert bad.formula not in repr(bad_summary)
    tamper_trainer, _tamper_answer = _copy_pair(
        trainer, answer, tmp_path / "comp_moved_tamper"
    )
    mapped = compsales_by_period[P2023.isoformat()]
    row, col = parse_cell_ref(mapped.cell)
    wb = load_workbook(tamper_trainer, data_only=False)
    wb[mapped.tab].cell(row, col).value = 1
    wb.save(tamper_trainer)
    wb.close()
    with pytest.raises(ValueError, match="Trusted workbook cell was modified"):
        check_workbook(tamper_trainer)


MOVED_SPSF_SOURCE_PLACEMENT = {
    0: (46, 4, "Income Statement"),
    1: (54, 7, "Income Statement"),
}


def test_management_history_workbook_adjacent_change_and_spsf(tmp_path):
    only = _compsales_tiny(
        _compsales(period=P1, value=2.0),
        _compsales(period=P2, value=7.0),
        _spsf(period=P1, value=1410),
        _spsf(period=P2, value=1430),
    )
    before = copy.deepcopy(only.historical_operating_kpis)
    trainer, answer = build_training_workbook(only, tmp_path / "MGMT_BOTH.xlsx")
    assert only.historical_operating_kpis == before
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_mgmt_both")
    smap = load_semantic_map(answer)
    sidecar = json.loads(component_map_path_for(answer).read_text(encoding="utf-8"))
    changes = _compsales_change_components(smap)
    diffs = _compsales_difference_components(smap)
    spsf_practice = _spsf_practice_components(smap)
    assert len(changes) == 1
    assert len(diffs) == 1
    assert len(_spsf_source_components(smap)) == 2
    assert {c.family_id for c in spsf_practice} == {
        SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
    }
    assert changes[0].expected_value == pytest.approx(5, abs=1e-12)
    spsf_change = next(
        c for c in spsf_practice if c.family_id == SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID
    )
    spsf_growth = next(
        c for c in spsf_practice if c.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID
    )
    assert spsf_change.expected_value == pytest.approx(20, abs=1e-12)
    assert spsf_growth.expected_value == pytest.approx(20 / 1410, abs=1e-12)
    spsf_diff = next(
        c
        for c in spsf_practice
        if c.family_id == SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID
    )
    expected_tiny_rev = (1100.0 - 1000.0) / 1000.0
    assert spsf_diff.expected_value == pytest.approx(
        100.0 * (expected_tiny_rev - (20 / 1410)),
        abs=OPERATING_KPI_RELATIONSHIP_TOLERANCE,
    )
    assert sidecar["components"]
    compact = changes[0].formula.replace(" ", "")
    source_p2 = next(
        c for c in _compsales_source_components(smap) if c.period_end == P2.isoformat()
    )
    source_p1 = next(
        c for c in _compsales_source_components(smap) if c.period_end == P1.isoformat()
    )
    assert compact == resolve_management_kpi_adjacent_change_formula(
        SemanticCellRef(
            source_p2.id,
            source_p2.semantic_key,
            source_p2.period_end,
            source_p2.cell,
            source_p2.tab,
        ),
        SemanticCellRef(
            source_p1.id,
            source_p1.semantic_key,
            source_p1.period_end,
            source_p1.cell,
            source_p1.tab,
        ),
        from_tab=COMPARABLE_SALES_SHEET,
    ).replace(" ", "")
    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    aws = awb[COMPARABLE_SALES_SHEET]
    source_row = _row_by_label(
        aws, "Reported comparable-sales growth (percent; 2 means 2%)"
    )
    assert aws.cell(source_row, 2).value == 2.0
    assert "%" in str(aws.cell(source_row, 2).number_format)
    change_row = _row_by_label(aws, "Adjacent reported change (percentage points)")
    assert "N/A" in str(aws.cell(change_row, 2).value)
    spsf_ws = awb[SALES_PER_SQUARE_FOOT_SHEET]
    spsf_source_row = _row_by_label(
        spsf_ws, "Reported sales per square foot (USD_per_square_foot)"
    )
    assert spsf_ws.cell(spsf_source_row, 2).value == 1410
    assert spsf_ws.cell(spsf_source_row, 3).value == 1430
    _assert_trainer_management_history_undisclosed(twb)
    _assert_answer_key_management_history_undisclosed(awb)
    a_spsf_change = awb[spsf_change.tab].cell(*parse_cell_ref(spsf_change.cell))
    a_spsf_growth = awb[spsf_growth.tab].cell(*parse_cell_ref(spsf_growth.cell))
    assert "minus" in (a_spsf_change.comment.text or "").lower()
    assert "(current - prior) / prior" in (a_spsf_growth.comment.text or "").lower()
    a_change = awb[changes[0].tab].cell(*parse_cell_ref(changes[0].cell))
    t_change = twb[changes[0].tab].cell(*parse_cell_ref(changes[0].cell))
    assert t_change.value in (None, "")
    assert t_change.comment is None
    assert _fill_rgb(t_change) == "FFFF00"
    assert (a_change.comment.text or "").strip()
    _assert_answer_key_no_yellow(answer)
    awb.close()
    twb.close()
    blank = check_workbook(trainer)
    assert (blank.blank, blank.correct, blank.incorrect) == (blank.total, 0, 0)
    wb = load_workbook(trainer, data_only=False)
    for comp in _check_components(smap):
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
    filled = check_workbook(trainer)
    assert filled.correct == filled.total
    assert "5" not in repr(filled) or "=I" not in repr(filled)
    incorrect_trainer, _ = _copy_pair(trainer, answer, tmp_path / "mgmt_incorrect")
    _inject_formula_and_cached_value(
        incorrect_trainer,
        changes[0].tab,
        changes[0].cell,
        formula="=999",
        cached_value=999.0,
    )
    bad = check_workbook(incorrect_trainer)
    assert bad.incorrect == 1
    assert "=999" not in repr(bad)
    mixed = _compsales_tiny(
        _compsales(period=P1, value=2.0),
        _compsales(period=P2, value=7.0),
        stores=(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767)),
    )
    mixed_trainer, mixed_answer = build_training_workbook(
        mixed, tmp_path / "MGMT_MIXED.xlsx"
    )
    mmap = load_semantic_map(mixed_answer)
    assert len(_compsales_change_components(mmap)) == 1
    assert len(
        [c for c in mmap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID]
    ) == 1
    assert Path(mixed_trainer).is_file()


def test_management_history_sparse_mismatch_zero_and_identities(tmp_path):
    singleton = _compsales_tiny(_compsales(period=P2, value=2.0), _spsf(period=P2, value=1410))
    trainer, answer = build_training_workbook(singleton, tmp_path / "MGMT_SINGLE.xlsx")
    smap = load_semantic_map(answer)
    assert _compsales_change_components(smap) == []
    assert _spsf_practice_components(smap) == []
    assert [c.period_end for c in _compsales_source_components(smap)] == [P2.isoformat()]
    assert [c.period_end for c in _spsf_source_components(smap)] == [P2.isoformat()]

    sparse = _compsales_tiny(
        _compsales(period=P0, value=1.0),
        _compsales(period=P2, value=4.0),
        extra_opening=P0,
    )
    series = next(
        iter(compute_management_kpi_series(sparse).series.values())
    )
    assert series.adjacent_change[P1] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P1] == (REASON_MISSING_OBSERVATION,)
    assert series.adjacent_change[P2] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P2] == (REASON_MISSING_PRIOR_OBSERVATION,)
    assert series.reported_value[P0] == 1.0
    assert series.reported_value[P2] == 4.0
    sparse_trainer, sparse_answer = build_training_workbook(
        sparse, tmp_path / "MGMT_SPARSE.xlsx"
    )
    assert _compsales_change_components(load_semantic_map(sparse_answer)) == []
    assert Path(sparse_trainer).is_file()

    mismatch_cases = (
        ("definition_text", DEF_B, REASON_DEFINITION_MISMATCH),
        ("calendar_week_adjustment", "excluded", REASON_CALENDAR_WEEK_MISMATCH),
        ("calendar_reporting_basis", REPORTING_BASIS_53, REASON_CALENDAR_REPORTING_MISMATCH),
        ("qualifiers", {"note": "changed"}, REASON_QUALIFIER_MISMATCH),
    )
    for field, value, reason in mismatch_cases:
        kwargs = {field: value}
        fin = _compsales_tiny(
            _compsales(period=P1, value=2.0),
            _compsales(period=P2, value=7.0, **kwargs),
        )
        original = copy.deepcopy(fin.historical_operating_kpis)
        hist = next(iter(compute_management_kpi_series(fin).series.values()))
        assert hist.reported_value[P1] == 2.0
        assert hist.reported_value[P2] == 7.0
        assert hist.adjacent_change[P2] == SOURCE_UNAVAILABLE
        assert hist.unavailable_reasons[P2] == (reason,)
        _trainer, answer = build_training_workbook(fin, tmp_path / f"MGMT_{reason}.xlsx")
        assert _compsales_change_components(load_semantic_map(answer)) == []
        assert fin.historical_operating_kpis == original

    kind = _compsales_tiny(
        _compsales(period=P1, value=2.0),
        _compsales(period=P2, value=7.0, period_kind="fiscal_year"),
    )
    original_kind = copy.deepcopy(kind.historical_operating_kpis)
    with pytest.raises(ValueError, match="period_kind must be"):
        ReferenceModelBuilder(kind)
    assert kind.historical_operating_kpis == original_kind

    ordered = _compsales_tiny(
        _compsales(period=P1, value=2.0, qualifiers={"a": "1", "b": "2"}),
        _compsales(period=P2, value=7.0, qualifiers={"b": "2", "a": "1"}),
    )
    ordered_hist = next(iter(compute_management_kpi_series(ordered).series.values()))
    assert ordered_hist.adjacent_change[P2] == 5
    _ot, ordered_answer = build_training_workbook(ordered, tmp_path / "MGMT_QUAL.xlsx")
    assert len(_compsales_change_components(load_semantic_map(ordered_answer))) == 1

    zero = _compsales_tiny(_spsf(period=P1, value=0.0), _spsf(period=P2, value=20.0))
    zero_hist = next(iter(compute_management_kpi_series(zero).series.values()))
    assert zero_hist.adjacent_change[P2] == 20
    assert zero_hist.growth[P2] == UNDEFINED_RATIO
    _zt, zero_answer = build_training_workbook(zero, tmp_path / "MGMT_ZERO.xlsx")
    growth = next(
        c
        for c in _spsf_practice_components(load_semantic_map(zero_answer))
        if c.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID
    )
    zawb = load_workbook(zero_answer, data_only=False)
    assert "NA()" in str(zawb[growth.tab].cell(*parse_cell_ref(growth.cell)).value)
    zawb.close()

    decline = _compsales_tiny(
        _compsales(period=P1, value=-3.0), _compsales(period=P2, value=-1.0)
    )
    decline_hist = next(iter(compute_management_kpi_series(decline).series.values()))
    assert decline_hist.adjacent_change[P2] == 2
    ecom = _compsales(period=P1, value=2.0, population=POP_STORES_AND_ECOMMERCE)
    dtc = _compsales(period=P1, value=3.0, population=POP_STORES_AND_DTC)
    ecom2 = _compsales(period=P2, value=4.0, population=POP_STORES_AND_ECOMMERCE)
    dtc2 = _compsales(period=P2, value=6.0, population=POP_STORES_AND_DTC)
    multi = _compsales_tiny(ecom, dtc, ecom2, dtc2)
    result = compute_management_kpi_series(multi)
    assert len(result.identities) == 2
    _mt, multi_answer = build_training_workbook(multi, tmp_path / "MGMT_IDS.xlsx")
    mmap = load_semantic_map(multi_answer)
    assert len(_compsales_source_components(mmap)) == 4
    assert len(_compsales_change_components(mmap)) == 2
    expected = {
        _identity_of(ecom): 2.0,
        _identity_of(dtc): 3.0,
    }
    for comp in _compsales_change_components(mmap):
        identity = next(
            item
            for item in result.identities
            if comparable_sales_identity_token(item) == operating_kpi_spec_identity(comp)
        )
        assert comp.expected_value == pytest.approx(expected[identity], abs=1e-12)

    bad = _compsales_tiny(_spsf(period=P2, value=-1))
    original = copy.deepcopy(bad.historical_operating_kpis)
    with pytest.raises(ValueError):
        ReferenceModelBuilder(bad)
    assert bad.historical_operating_kpis == original


def test_generated_workbooks_follow_moved_management_sources(tmp_path, monkeypatch):
    only = _compsales_tiny(
        _compsales(period=P1, value=2.0),
        _compsales(period=P2, value=7.0),
        _spsf(period=P1, value=1410),
        _spsf(period=P2, value=1430),
    )
    management = compute_management_kpi_series(only)
    compsales_id = next(
        identity
        for identity, series in management.series.items()
        if series.family == FAMILY_COMPARABLE_SALES_GROWTH
    )
    spsf_id = next(
        identity
        for identity, series in management.series.items()
        if series.family == FAMILY_SALES_PER_SQUARE_FOOT
    )

    def _moved_compsales(self, moved_identity, period_index, default_row, default_col):
        assert moved_identity == compsales_id
        return MOVED_COMPSALES_SOURCE_PLACEMENT[period_index]

    def _moved_spsf(self, moved_identity, period_index, default_row, default_col):
        assert moved_identity == spsf_id
        return MOVED_SPSF_SOURCE_PLACEMENT[period_index]

    monkeypatch.setattr(
        ReferenceModelBuilder, "_comparable_sales_source_placement", _moved_compsales
    )
    monkeypatch.setattr(
        ReferenceModelBuilder,
        "_sales_per_square_foot_source_placement",
        _moved_spsf,
    )
    trainer, answer = build_training_workbook(only, tmp_path / "MGMT_MOVED.xlsx")
    trainer, answer = _copy_pair(trainer, answer, tmp_path / "reopened_mgmt_moved")
    smap = load_semantic_map(answer)
    sidecar = json.loads(component_map_path_for(answer).read_text(encoding="utf-8"))
    serialized_by_id = {row["id"]: row for row in sidecar["components"]}
    axis = list(canonical_fiscal_periods(only))
    change = _compsales_change_components(smap)[0]
    compsales_sources = {
        c.period_end: c for c in _compsales_source_components(smap)
    }
    for period in (P1, P2):
        index = axis.index(period)
        row, col, tab = MOVED_COMPSALES_SOURCE_PLACEMENT[index]
        mapped = compsales_sources[period.isoformat()]
        assert mapped.cell == f"{get_column_letter(col)}{row}"
        assert mapped.tab == tab
        assert serialized_by_id[mapped.id]["cell"] == mapped.cell
    compact = change.formula.replace(" ", "")
    current = compsales_sources[P2.isoformat()]
    prior = compsales_sources[P1.isoformat()]
    assert compact == resolve_management_kpi_adjacent_change_formula(
        SemanticCellRef(
            current.id, current.semantic_key, current.period_end, current.cell, current.tab
        ),
        SemanticCellRef(
            prior.id, prior.semantic_key, prior.period_end, prior.cell, prior.tab
        ),
        from_tab=COMPARABLE_SALES_SHEET,
    ).replace(" ", "")
    adjacent = f"{get_column_letter(parse_cell_ref(current.cell)[1] - 1)}{parse_cell_ref(current.cell)[0]}"
    assert adjacent not in compact
    spsf_sources = {c.period_end: c for c in _spsf_source_components(smap)}
    spsf_change = next(
        c
        for c in _spsf_practice_components(smap)
        if c.family_id == SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID
    )
    spsf_current = spsf_sources[P2.isoformat()]
    spsf_prior = spsf_sources[P1.isoformat()]
    assert spsf_change.formula.replace(" ", "") == (
        resolve_management_kpi_adjacent_change_formula(
            SemanticCellRef(
                spsf_current.id,
                spsf_current.semantic_key,
                spsf_current.period_end,
                spsf_current.cell,
                spsf_current.tab,
            ),
            SemanticCellRef(
                spsf_prior.id,
                spsf_prior.semantic_key,
                spsf_prior.period_end,
                spsf_prior.cell,
                spsf_prior.tab,
            ),
            from_tab=SALES_PER_SQUARE_FOOT_SHEET,
        ).replace(" ", "")
    )
    spsf_diff = _spsf_difference_components(smap)[0]
    spsf_growth = next(
        c
        for c in _spsf_practice_components(smap)
        if c.family_id == SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID
    )
    revenue_growth = next(
        c for c in smap.all_ordered() if c.family_id == REVENUE_STORE_GROWTH_FAMILY_ID
    )
    compact_diff = spsf_diff.formula.replace(" ", "")
    assert compact_diff == resolve_revenue_sales_per_square_foot_difference_formula(
        SemanticCellRef(
            revenue_growth.id,
            revenue_growth.semantic_key,
            revenue_growth.period_end,
            revenue_growth.cell,
            revenue_growth.tab,
        ),
        SemanticCellRef(
            spsf_growth.id,
            spsf_growth.semantic_key,
            spsf_growth.period_end,
            spsf_growth.cell,
            spsf_growth.tab,
        ),
        from_tab=SALES_PER_SQUARE_FOOT_SHEET,
    ).replace(" ", "")
    adjacent_growth = (
        f"{get_column_letter(parse_cell_ref(spsf_growth.cell)[1] - 1)}"
        f"{parse_cell_ref(spsf_growth.cell)[0]}"
    )
    assert adjacent_growth not in compact_diff
    blank = check_workbook(trainer)
    assert blank.blank == blank.total
    twb = load_workbook(trainer, data_only=False)
    awb = load_workbook(answer, data_only=False)
    _assert_trainer_management_history_undisclosed(twb)
    _assert_answer_key_management_history_undisclosed(awb)
    twb.close()
    awb.close()
    tamper_trainer, _ = _copy_pair(trainer, answer, tmp_path / "mgmt_moved_tamper")
    row, col = parse_cell_ref(spsf_current.cell)
    wb = load_workbook(tamper_trainer, data_only=False)
    wb[spsf_current.tab].cell(row, col).value = 1
    wb.save(tamper_trainer)
    wb.close()
    with pytest.raises(ValueError, match="Trusted workbook cell was modified"):
        check_workbook(tamper_trainer)
