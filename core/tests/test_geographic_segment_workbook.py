"""Step 9M.2.4.1.1.1.35 — geographic workbook schedules and learner/Check."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.historical_segments import (
    FAMILY_CORPORATE,
    FAMILY_ITEMIZED,
    GEOGRAPHIC_SEGMENT_NAMESPACE,
    IFOP_CORPORATE,
    OP_ADD,
    OP_SUBTRACT,
    SEGMENTS,
)
from core.data.interface import DocumentManifest, DocumentType, FinancialPeriod, HistoricalSegmentData, LineItem
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.engine.component_catalog import (
    GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG,
    GEOGRAPHIC_SHEET_NAME,
    expand_geographic_segment_specs,
    geographic_component_id,
)
from core.engine.reference_model import GEOGRAPHIC_SHEET, ReferenceModelBuilder
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import standardize_reconciled
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.data.interface import DocumentManifest, DocumentType
from core.model.geographic_segment import (
    GEOGRAPHIC_RATIO_TOLERANCE,
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from core.model.historical_expected import geographic_expected_value_for_component
from core.model.line_resolver import MissingLineError
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO
from core.tests.test_capex import P1, P2, _tiny
from core.tests.test_geographic_segment_analysis import (
    ADMIT_2022,
    FY2026,
    _assert_series_matches,
    _independent_from_snapshots,
    _reload_admitted_lululemon,
)
from core.tests.test_geographic_segment_facts import _mutate_fy2025_prior_2025
from core.tests.test_historical_segment import (
    _corp_values,
    _itemized_values,
    _snapshot,
)
from core.tests.test_normalization import _inject_formula_and_cached_value
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
LULU_JSON = ROOT / "benchmark" / "lululemon" / "reconciled" / "standardized.json"
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"
P0 = date(2023, 12, 31)
LEASE_DT_LULULEMON_SPECS = 486
FAST_RETAILING_SPECS = 577


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _attach_geo(fin, *snapshots):
    fin.historical_segment = HistoricalSegmentData(
        namespace=GEOGRAPHIC_SEGMENT_NAMESPACE,
        periods=list(snapshots),
    )
    return fin


def _geo_tiny(*snapshots, extra_opening: date | None = None):
    fin = _tiny(with_payments=False)
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
    if snapshots:
        _attach_geo(fin, *snapshots)
        revenue = next(item for item in fin.income_statement if item.concept == "revenue")
        ifop_values: dict[date, float] = {}
        for snap in snapshots:
            revenue.values[snap.period] = float(snap.values["net_revenue.consolidated"])
            ifop_values[snap.period] = float(
                snap.values["income_from_operations.consolidated"]
            )
        if extra_opening is not None and P1 in ifop_values:
            ifop_values[extra_opening] = ifop_values[P1]
        fin.income_statement.insert(
            1,
            LineItem(
                label="Income from operations",
                concept="operating_income",
                values=ifop_values,
            ),
        )
    return fin


def _row_by_label(ws, label: str) -> int:
    for row in range(1, (ws.max_row or 1) + 1):
        if ws.cell(row, 1).value == label:
            return row
    raise AssertionError(f"missing geographic label {label!r}")


def test_catalog_orders_and_expand_identities():
    assert GEOGRAPHIC_SHEET == GEOGRAPHIC_SHEET_NAME
    assert [family.order for family in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG] == list(
        range(152, 161)
    )
    assert [family.id for family in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG] == [
        "geographic_revenue_share",
        "geographic_revenue_growth",
        "geographic_reported_operating_margin",
        "geographic_calculated_segment_revenue_total",
        "geographic_calculated_segment_operating_profit_total",
        "geographic_signed_reconciling_contribution",
        "geographic_reconstructed_consolidated_operating_profit",
        "geographic_consolidated_revenue_difference",
        "geographic_consolidated_operating_profit_difference",
    ]
    specs = expand_geographic_segment_specs(
        [P1, P2],
        start_order=10,
        available_periods=(P1, P2),
        growth_identities={P2: SEGMENTS},
        bridge_identities={
            P1: (
                "ifop_reconciling.amortization_of_intangible_assets",
                "ifop_reconciling.general_corporate_expenses",
            ),
            P2: (IFOP_CORPORATE,),
        },
    )
    assert geographic_component_id("geographic_revenue_share", P1, "americas") in {
        s.id for s in specs
    }
    assert not any(
        s.family_id == "geographic_revenue_growth" and s.period_end == P1.isoformat()
        for s in specs
    )
    signed = [
        s
        for s in specs
        if s.family_id == "geographic_signed_reconciling_contribution"
    ]
    assert {s.id for s in signed} == {
        geographic_component_id(
            "geographic_signed_reconciling_contribution",
            P1,
            "ifop_reconciling.amortization_of_intangible_assets",
        ),
        geographic_component_id(
            "geographic_signed_reconciling_contribution",
            P1,
            "ifop_reconciling.general_corporate_expenses",
        ),
        geographic_component_id(
            "geographic_signed_reconciling_contribution",
            P2,
            IFOP_CORPORATE,
        ),
    }
    with pytest.raises(ValueError, match="duplicate fiscal periods"):
        expand_geographic_segment_specs(
            [P1, P1],
            start_order=1,
            available_periods=(P1,),
            growth_identities={},
            bridge_identities={},
        )
    with pytest.raises(ValueError, match="strictly chronological"):
        expand_geographic_segment_specs(
            [P2, P1],
            start_order=1,
            available_periods=(P1, P2),
            growth_identities={},
            bridge_identities={},
        )


def test_absent_null_payloads_add_no_schedule_or_practice(tmp_path):
    absent = _tiny(with_payments=False)
    assert not geographic_segment_applicable(absent)
    builder = ReferenceModelBuilder(absent)
    assert builder.geographic_series is None
    assert builder.geographic_specs == ()
    trainer, answer = build_training_workbook(absent, tmp_path / "GEO_ABSENT.xlsx")
    for path in (trainer, answer):
        wb = load_workbook(path)
        assert GEOGRAPHIC_SHEET not in wb.sheetnames
        wb.close()
    smap = load_semantic_map(answer)
    assert not any(c.category == "geographic_segment" for c in smap.all_ordered())

    payload = standardized_to_payload(_tiny(with_payments=False))
    payload["historical_segment"] = None
    nulled = standardized_from_payload(payload)
    assert nulled.historical_segment is None
    assert ReferenceModelBuilder(nulled).geographic_specs == ()


def test_invalid_contract_fails_closed_without_mutation():
    fin = _geo_tiny(_snapshot(P1), _snapshot(P2))
    original = copy.deepcopy(fin.historical_segment)
    fin.historical_segment.periods[0].bridge_operations = {IFOP_CORPORATE: OP_SUBTRACT}
    mutated = copy.deepcopy(fin.historical_segment)
    with pytest.raises(ValueError):
        ReferenceModelBuilder(fin)
    assert fin.historical_segment == mutated
    fin.historical_segment = copy.deepcopy(original)
    with pytest.raises(MissingLineError):
        compute_geographic_segment_series(_tiny(with_payments=False))


def test_workbook_gating_formulas_notes_check_and_families(tmp_path):
    fin = _geo_tiny(
        _snapshot(P1, family=FAMILY_ITEMIZED, values=_itemized_values()),
        _snapshot(P2, family=FAMILY_CORPORATE, values=_corp_values()),
    )
    builder = ReferenceModelBuilder(fin)
    assert builder.geographic_series is not None
    geo_ids = {s.family_id for s in builder.geographic_specs}
    assert geo_ids == {f.id for f in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG}
    existing = [
        s.id
        for s in builder.expected_specs
        if s.category != "geographic_segment"
    ]
    assert existing
    trainer, answer = build_training_workbook(fin, tmp_path / "GEO_BASE.xlsx")
    smap = load_semantic_map(answer)
    geo_comps = [
        c for c in smap.all_ordered() if c.category == "geographic_segment"
    ]
    assert {c.id for c in geo_comps} == {s.id for s in builder.geographic_specs}
    assert not any(
        c.family_id == "geographic_revenue_growth" and c.period_index == 0
        for c in geo_comps
    )

    awb = load_workbook(answer, data_only=False)
    twb = load_workbook(trainer, data_only=False)
    assert GEOGRAPHIC_SHEET in awb.sheetnames
    assert GEOGRAPHIC_SHEET in twb.sheetnames
    aws = awb[GEOGRAPHIC_SHEET]
    tws = twb[GEOGRAPHIC_SHEET]
    assert "Americas" in str(aws.cell(_row_by_label(aws, "Americas net revenue"), 1).value)
    assert "China Mainland" in str(
        aws.cell(_row_by_label(aws, "China Mainland net revenue"), 1).value
    )
    assert "Rest of World" in str(
        aws.cell(_row_by_label(aws, "Rest of World net revenue"), 1).value
    )
    assert "NOPAT" in str(aws["A2"].value)
    assert str(aws["A3"].value).startswith("Units:")
    family_row = _row_by_label(aws, "Presentation family")
    assert aws.cell(family_row, 2).value == FAMILY_ITEMIZED
    assert aws.cell(family_row, 3).value == FAMILY_CORPORATE

    americas_rev = _row_by_label(aws, "Americas net revenue")
    assert aws.cell(americas_rev, 2).value == 50.0
    assert tws.cell(americas_rev, 2).value == 50.0
    calc_rev = _row_by_label(aws, "Calculated segment revenue total")
    assert str(aws.cell(calc_rev, 2).value).startswith("=")
    assert tws.cell(calc_rev, 2).value in (None, "")
    growth_row = _row_by_label(aws, "Americas adjacent-period revenue growth")
    assert aws.cell(growth_row, 2).value == "N/A"
    assert tws.cell(growth_row, 2).value == "N/A"
    assert str(aws.cell(growth_row, 3).value).startswith("=")
    assert "NA()" in str(aws.cell(growth_row, 3).value)

    itemized_signed = _row_by_label(
        aws, "Amortization Of Intangible Assets signed contribution"
    )
    assert str(aws.cell(itemized_signed, 2).value).replace(" ", "").startswith("=-")
    assert aws.cell(itemized_signed, 3).value in (None, "")
    corp_signed = _row_by_label(aws, "Corporate Unallocated signed contribution")
    assert str(aws.cell(corp_signed, 3).value).replace(" ", "") == (
        f"={chr(67)}{_row_by_label(aws, 'Corporate Unallocated (reported)')}"
    ).replace(" ", "") or str(aws.cell(corp_signed, 3).value).startswith("=")
    corp_formula = str(aws.cell(corp_signed, 3).value).replace(" ", "")
    assert corp_formula.startswith("=") and not corp_formula.startswith("=-")
    recon = _row_by_label(aws, "Reconstructed consolidated operating profit")
    assert "+" in str(aws.cell(recon, 2).value)
    margin_row = _row_by_label(aws, "Americas reported operating margin")
    note = (aws.cell(margin_row, 2).comment.text or "") if aws.cell(margin_row, 2).comment else ""
    assert "NOPAT" in note
    mix_row = _row_by_label(aws, "Americas revenue mix")
    mix_note = (aws.cell(mix_row, 2).comment.text or "") if aws.cell(mix_row, 2).comment else ""
    assert "mix" in mix_note.lower()
    assert tws.cell(mix_row, 2).comment is None
    assert tws.cell(mix_row, 2).value is None
    awb.close()
    twb.close()

    for comp in geo_comps:
        looked = geographic_expected_value_for_component(
            builder.geographic_series, comp
        )
        if isinstance(looked, float) and isinstance(comp.expected_value, float):
            assert looked == pytest.approx(comp.expected_value, abs=GEOGRAPHIC_RATIO_TOLERANCE)
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

    bad = next(c for c in geo_comps if c.family_id == "geographic_revenue_share")
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
    assert "Americas revenue mix" not in dumped
    assert "0.5" not in dumped


def test_sparse_undefined_negative_reorder_and_source_edit(tmp_path):
    zero_itemized = _itemized_values()
    zero_itemized["net_revenue.americas"] = 0.0
    zero_itemized["net_revenue.consolidated"] = 50.0
    neg_corp = _corp_values(ifop=(-4.0, 2.0, 1.0), corporate=-10.0)
    fin = _geo_tiny(
        _snapshot(P1, family=FAMILY_ITEMIZED, values=zero_itemized),
        _snapshot(P2, family=FAMILY_CORPORATE, values=neg_corp),
        extra_opening=P0,
    )
    builder = ReferenceModelBuilder(fin)
    series = builder.geographic_series
    assert series is not None
    axis = canonical_fiscal_periods(fin)
    assert axis[0] == P0
    assert series.presentation_family[P0] == SOURCE_UNAVAILABLE
    assert series.revenue_share[P0]["americas"] == SOURCE_UNAVAILABLE
    assert series.revenue_growth[P0]["americas"] is None
    assert series.revenue_growth[P1]["americas"] == SOURCE_UNAVAILABLE
    assert series.reported_operating_margin[P1]["americas"] == UNDEFINED_RATIO
    assert series.income_from_operations[P2]["americas"] == -4.0
    assert not any(
        s.period_end == P0.isoformat() for s in builder.geographic_specs
    )
    assert not any(
        s.family_id == "geographic_revenue_growth" and s.period_end == P1.isoformat()
        for s in builder.geographic_specs
    )

    reversed_snaps = (
        _snapshot(P2, family=FAMILY_CORPORATE, values=neg_corp),
        _snapshot(P1, family=FAMILY_ITEMIZED, values=zero_itemized),
    )
    reordered = _geo_tiny(*reversed_snaps, extra_opening=P0)
    reordered.historical_segment.periods = list(
        reversed(list(reordered.historical_segment.periods))
    )
    restored = standardized_from_payload(standardized_to_payload(reordered))
    rebuilt = compute_geographic_segment_series(restored)
    assert rebuilt.reported_operating_margin[P1]["americas"] == UNDEFINED_RATIO
    assert rebuilt.income_from_operations[P2]["americas"] == -4.0

    trainer, answer = build_training_workbook(fin, tmp_path / "GEO_SPARSE.xlsx")
    smap = load_semantic_map(answer)
    geo_comps = [
        c for c in smap.all_ordered() if c.category == "geographic_segment"
    ]
    awb = load_workbook(answer, data_only=False)
    aws = awb[GEOGRAPHIC_SHEET]
    share_row = _row_by_label(aws, "Americas revenue mix")
    assert SOURCE_UNAVAILABLE in {
        aws.cell(share_row, 2).value,
        aws.cell(_row_by_label(aws, "Americas net revenue"), 2).value,
    }
    growth_row = _row_by_label(aws, "Americas adjacent-period revenue growth")
    assert aws.cell(growth_row, 2).value == "N/A"
    assert aws.cell(growth_row, 3).value == SOURCE_UNAVAILABLE
    margin_row = _row_by_label(aws, "Americas reported operating margin")
    assert "NA()" in str(aws.cell(margin_row, 3).value)
    awb.close()

    source_row = _row_by_label(
        load_workbook(answer, data_only=False)[GEOGRAPHIC_SHEET],
        "Americas net revenue",
    )
    wb = load_workbook(trainer, data_only=False)
    wb[GEOGRAPHIC_SHEET].cell(source_row, 3).value = 1
    wb.save(trainer)
    wb.close()
    with pytest.raises(
        ValueError,
        match="Trusted workbook cell was modified: Geographic Segment Analysis",
    ):
        check_workbook(trainer)

    trainer2, _answer2 = build_training_workbook(fin, tmp_path / "GEO_RELOC.xlsx")
    smap2 = load_semantic_map(_answer2)
    share = next(
        c
        for c in smap2.all_ordered()
        if c.family_id == "geographic_revenue_share" and "americas" in c.id
    )
    wb = load_workbook(trainer2, data_only=False)
    row, col = parse_cell_ref(share.cell)
    wb[share.tab].cell(row=row, column=col).value = share.formula
    wb.save(trainer2)
    wb.close()
    relocated = check_workbook(trainer2)
    assert relocated.incorrect == 0
    assert geo_comps


def test_committed_lululemon_and_fast_retailing_identities_unchanged():
    lulu = standardized_from_payload(
        json.loads(LULU_JSON.read_text(encoding="utf-8"))
    )
    assert lulu.historical_segment is None
    lulu_builder = ReferenceModelBuilder(lulu)
    assert lulu_builder.geographic_specs == ()
    assert len(lulu_builder.expected_specs) == LEASE_DT_LULULEMON_SPECS

    fr = standardized_from_payload(json.loads(FR_JSON.read_text(encoding="utf-8")))
    assert fr.historical_segment is None
    fr_builder = ReferenceModelBuilder(fr)
    assert fr_builder.geographic_specs == ()
    assert len(fr_builder.expected_specs) == FAST_RETAILING_SPECS

    demo = HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )
    assert not geographic_segment_applicable(demo)
    assert ReferenceModelBuilder(demo).geographic_specs == ()


def test_lululemon_five_period_temporary_pair_matches_selected_facts(tmp_path):
    _reconciled, _fin, restored = _reload_admitted_lululemon()
    snapshots = {snap.period: snap for snap in restored.historical_segment.periods}
    series = compute_geographic_segment_series(restored)
    expected = _independent_from_snapshots(list(series.periods), snapshots)
    _assert_series_matches(series, expected)
    assert 3607682 - 1397067 == 2210615
    assert series.calculated_segment_operating_profit_total[FY2026] == 3607682
    assert series.signed_reconciling_contributions[FY2026] == (
        (IFOP_CORPORATE, -1397067.0),
    )
    assert series.reconstructed_consolidated_operating_profit[FY2026] == 2210615

    builder = ReferenceModelBuilder(restored)
    geo_n = len(builder.geographic_specs)
    assert geo_n > 0
    preserved = [
        s
        for s in builder.expected_specs
        if s.category != "geographic_segment"
    ]
    assert len(preserved) == LEASE_DT_LULULEMON_SPECS
    assert {s.id for s in preserved} == {
        s.id
        for s in ReferenceModelBuilder(
            standardized_from_payload(
                json.loads(LULU_JSON.read_text(encoding="utf-8"))
            )
        ).expected_specs
    }

    trainer, answer = build_training_workbook(
        restored, tmp_path / "LULU_GEO_TMP.xlsx"
    )
    smap = load_semantic_map(answer)
    geo_comps = [
        c for c in smap.all_ordered() if c.category == "geographic_segment"
    ]
    assert len(geo_comps) == geo_n
    assert len(smap.all_ordered()) == LEASE_DT_LULULEMON_SPECS + geo_n

    awb = load_workbook(answer, data_only=False)
    aws = awb[GEOGRAPHIC_SHEET]
    twb = load_workbook(trainer, data_only=False)
    tws = twb[GEOGRAPHIC_SHEET]
    americas_rev = _row_by_label(aws, "Americas net revenue")
    china_rev = _row_by_label(aws, "China Mainland net revenue")
    row_rev = _row_by_label(aws, "Rest of World net revenue")
    cons_rev = _row_by_label(aws, "Reported consolidated revenue")
    fy2026_col = 6
    assert aws.cell(americas_rev, fy2026_col).value == snapshots[FY2026].values[
        "net_revenue.americas"
    ]
    assert tws.cell(americas_rev, fy2026_col).value == aws.cell(
        americas_rev, fy2026_col
    ).value
    mix = next(
        c
        for c in geo_comps
        if c.family_id == "geographic_revenue_share"
        and c.period_end == FY2026.isoformat()
        and "americas" in c.id
    )
    assert "NA()" in mix.formula
    assert mix.formula.replace(" ", "") == (
        f"=IF({chr(64 + fy2026_col)}{cons_rev}=0,NA(),"
        f"{chr(64 + fy2026_col)}{americas_rev}/{chr(64 + fy2026_col)}{cons_rev})"
    ).replace(" ", "")
    corp_signed = next(
        c
        for c in geo_comps
        if c.family_id == "geographic_signed_reconciling_contribution"
        and c.period_end == FY2026.isoformat()
    )
    assert corp_signed.expected_value == -1397067.0
    assert corp_signed.formula.replace(" ", "").startswith("=")
    assert not corp_signed.formula.replace(" ", "").startswith("=-")
    recon = next(
        c
        for c in geo_comps
        if c.family_id == "geographic_reconstructed_consolidated_operating_profit"
        and c.period_end == FY2026.isoformat()
    )
    assert recon.expected_value == 2210615.0
    assert "+" in recon.formula
    itemized = next(
        c
        for c in geo_comps
        if c.family_id == "geographic_signed_reconciling_contribution"
        and c.period_end == ADMIT_2022.isoformat()
        and "acquisition_related_expenses" in c.id
    )
    assert itemized.formula.replace(" ", "").startswith("=-")
    for period in series.periods:
        assert series.consolidated_revenue_difference[period] == 0.0
        assert series.consolidated_operating_profit_difference[period] == 0.0
    for comp in geo_comps:
        row, col = parse_cell_ref(comp.cell)
        trainer_cell = tws.cell(row=row, column=col) if comp.tab == GEOGRAPHIC_SHEET else twb[comp.tab].cell(row=row, column=col)
        answer_cell = aws.cell(row=row, column=col) if comp.tab == GEOGRAPHIC_SHEET else awb[comp.tab].cell(row=row, column=col)
        if comp.tab == GEOGRAPHIC_SHEET:
            trainer_cell = twb[comp.tab].cell(row=row, column=col)
            answer_cell = awb[comp.tab].cell(row=row, column=col)
        assert trainer_cell.value is None
        assert trainer_cell.comment is None
        assert _fill_rgb(trainer_cell) == "FFFF00"
        assert answer_cell.value == comp.formula
        assert answer_cell.comment is not None
        assert (answer_cell.comment.text or "").strip()
        assert "cause" not in (answer_cell.comment.text or "").lower()
    awb.close()
    twb.close()

    blank = check_workbook(trainer)
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


def test_prior_presentation_mutation_survives_workbook_series():
    from core.ingestion.filing_json import load_extracted_filing
    from core.ingestion.filing_validator import validate_extracted_filing
    from core.tests.test_geographic_segment_analysis import EXTRACTED, SOURCE
    from core.tests.test_geographic_segment_analysis import FY2025_AMERICAS

    _baseline_reconciled, _baseline_fin, baseline = _reload_admitted_lululemon()
    fy2022 = load_extracted_filing(EXTRACTED / "LULU_FY2022.json")
    fy2023 = load_extracted_filing(EXTRACTED / "LULU_FY2023.json")
    fy2024 = load_extracted_filing(EXTRACTED / "LULU_FY2024.json")
    fy2025 = _mutate_fy2025_prior_2025(
        load_extracted_filing(EXTRACTED / "LULU_FY2025.json")
    )
    validated = []
    for filing in (fy2022, fy2023, fy2024, fy2025):
        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        validated.append((filing, report))
    reconciled = reconcile_filings(validated, admit_periods=(ADMIT_2022,))
    restored = standardized_from_payload(
        json.loads(json.dumps(standardized_to_payload(standardize_reconciled(reconciled))))
    )
    series = compute_geographic_segment_series(restored)
    baseline_series = compute_geographic_segment_series(baseline)
    assert series.net_revenue[FY2025_AMERICAS]["americas"] == 7928156
    assert (
        series.net_revenue[FY2025_AMERICAS]["americas"]
        == baseline_series.net_revenue[FY2025_AMERICAS]["americas"]
    )
    payload = standardized_to_payload(restored)
    assert "7928256" not in json.dumps(payload.get("historical_segment"))
    builder = ReferenceModelBuilder(restored)
    assert builder.geographic_series.net_revenue[FY2025_AMERICAS]["americas"] == 7928156
    assert any(
        s.family_id == "geographic_calculated_segment_revenue_total"
        and s.period_end == FY2025_AMERICAS.isoformat()
        for s in builder.geographic_specs
    )
