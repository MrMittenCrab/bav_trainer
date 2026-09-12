"""Tests for BAV Excel Trainer — Trainer / Answer Key separation + workbook-wide Check."""

import importlib.util
from pathlib import Path

import pytest
from openpyxl import load_workbook

from core.data.interface import DocumentManifest, DocumentType
from core.engine.component_catalog import (
    COMPONENT_CATALOG,
    DEFERRED_COMPONENT_SPECS,
    expand_historical_specs,
)
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.model.classification import BALANCE_SHEET_CATEGORIES
from core.trainer.checker import check_workbook
from core.trainer.semantic_io import (
    answer_key_path_for,
    load_semantic_map,
    parse_cell_ref,
    resolve_pair_paths,
)
from core.trainer.workbook import (
    FONT_NAME,
    TRAINER_INDEX_INSTRUCTION,
    build_training_workbook,
    group_components_by_family,
)

ROOT = Path(__file__).resolve().parents[2]
DEMO_JSON = ROOT / "example" / "DEMO_HK_Standardized.json"


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _ingest_demo():
    adapter = HKManualDocumentAdapter()
    return adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])


def _build_pair(tmp_path):
    data = _ingest_demo()
    return build_training_workbook(data, tmp_path / "DEMO_HK_Trainer.xlsx")


def test_legacy_components_module_removed():
    assert importlib.util.find_spec("core.engine.components") is None


def test_no_trainer_components_symbols_in_repo():
    for path in ROOT.rglob("*.py"):
        if ".git" in path.parts or "__pycache__" in path.parts or "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert "TRAINER_COMPONENTS" not in text
        assert "TrainerComponent" not in text
        assert "from core.engine.components" not in text
        assert "from .engine.components" not in text


def test_catalog_has_no_coordinates():
    for spec in COMPONENT_CATALOG:
        assert spec.semantic_key
        assert spec.tab_template or spec.category
        d = spec.__dict__
        assert "cell" not in d
        assert "tab" not in d or spec.tab_template


def test_period_aware_catalog_and_expand_historical_specs():
    assert len(COMPONENT_CATALOG) == 25
    assert [f.order for f in COMPONENT_CATALOG] == list(range(1, 26))
    assert len({f.id for f in COMPONENT_CATALOG}) == 25
    assert len({f.semantic_key for f in COMPONENT_CATALOG}) == 25

    deferred_ids = {c.id for c in DEFERRED_COMPONENT_SPECS}
    assert deferred_ids.isdisjoint({f.id for f in COMPONENT_CATALOG})

    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    specs = expand_historical_specs(periods)
    assert len(specs) == 118
    assert [s.order for s in specs] == list(range(1, 119))
    assert len({s.id for s in specs}) == 118
    assert len({s.semantic_key for s in specs}) == 118
    assert len(expand_historical_specs(periods[:3])) == 68  # 25*3 - 7
    assert len(expand_historical_specs(periods[:2])) == 43  # 25*2 - 7

    by_id = {s.id: s for s in specs}
    for spec in specs:
        for dep in spec.depends_on:
            assert dep in by_id
            assert by_id[dep].order < spec.order
        if COMPONENT_CATALOG[[f.id for f in COMPONENT_CATALOG].index(spec.family_id)].period_scope == "comparable":
            assert spec.period_index != 0


def test_catalog_has_21_historical_components_in_dependency_order():
    # Backward-compatible name kept; Step 7 uses 25 conceptual families.
    test_period_aware_catalog_and_expand_historical_specs()


def test_ingest_demo_json():
    adapter = HKManualDocumentAdapter()
    data = adapter.ingest([DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)])
    assert data.ticker == "DEMO"
    assert len(data.periods) == 5
    report = adapter.reconcile(data)
    assert "income_statement" in report.checksums


def test_resolve_pair_paths_appends_and_preserves_trainer_stem(tmp_path):
    trainer, answer = resolve_pair_paths(tmp_path / "DEMO_HK_Trainer.xlsx")
    assert trainer.name == "DEMO_HK_Trainer.xlsx"
    assert answer.name == "DEMO_HK_Answer_Key.xlsx"

    trainer2, answer2 = resolve_pair_paths(tmp_path / "Acme.xlsx")
    assert trainer2.name == "Acme_Trainer.xlsx"
    assert answer2.name == "Acme_Answer_Key.xlsx"


def test_build_paired_trainer_and_answer_key(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)

    assert trainer_path.exists()
    assert answer_key_path.exists()
    assert trainer_path.name == "DEMO_HK_Trainer.xlsx"
    assert answer_key_path.name == "DEMO_HK_Answer_Key.xlsx"
    assert not (tmp_path / "DEMO_HK_Trainer_reference.xlsx").exists()
    assert not list(tmp_path.glob("*_reference.xlsx"))

    smap = load_semantic_map(answer_key_path)
    data = _ingest_demo()
    periods = data.fiscal_years() or data.period_dates()
    from core.engine.component_catalog import (
        expand_quality_specs,
        expand_working_capital_specs,
        expand_profitability_driver_specs,
        expand_profitability_change_specs,
        expand_roe_attribution_specs,
        expand_quality_change_specs,
    )

    hist = expand_historical_specs(periods)
    quality = expand_quality_specs(
        periods, start_order=len(hist) + 1, include_asset_scaled=True
    )
    wc = expand_working_capital_specs(
        periods, start_order=len(hist) + len(quality) + 1
    )
    pd = expand_profitability_driver_specs(
        periods, start_order=len(hist) + len(quality) + len(wc) + 1
    )
    pc = expand_profitability_change_specs(
        periods, start_order=len(hist) + len(quality) + len(wc) + len(pd) + 1
    )
    ra = expand_roe_attribution_specs(
        periods,
        start_order=len(hist) + len(quality) + len(wc) + len(pd) + len(pc) + 1,
    )
    qc = expand_quality_change_specs(
        periods,
        start_order=len(hist) + len(quality) + len(wc) + len(pd) + len(pc) + len(ra) + 1,
        include_asset_scaled=True,
    )
    expected = hist + quality + wc + pd + pc + ra + qc
    assert len(smap.all_ordered()) == len(expected) == 259
    for spec in expected:
        comp = smap.get(spec.id)
        assert comp.formula.startswith("=")
        assert comp.expected_value is not None
        assert comp.tab and comp.cell
        assert comp.family_id == spec.family_id
        assert comp.period_index == spec.period_index


def test_trainer_has_no_answer_bearing_hidden_sheets(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    assert "_RefFormulas" not in wb_t.sheetnames
    assert "_RefValues" not in wb_t.sheetnames
    assert "_TrainerMeta" not in wb_t.sheetnames
    assert "_ComponentMap" not in wb_t.sheetnames
    wb_t.close()


def test_trainer_has_no_answer_sidecars(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    assert not trainer_path.with_suffix(".component_map.json").exists()
    assert not trainer_path.with_suffix(".trainer.json").exists()
    assert answer_key_path.with_suffix(".component_map.json").exists()


def test_trainer_and_answer_key_practice_contract(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        tc = wb_t[comp.tab].cell(row=row, column=col)
        ac = wb_a[comp.tab].cell(row=row, column=col)
        assert tc.value is None
        assert tc.comment is None
        assert _fill_rgb(tc) == "FFFF00"
        assert isinstance(ac.value, str) and ac.value.startswith("=")
        assert ac.value == comp.formula
        assert ac.comment is not None and ac.comment.text.strip()
        assert _fill_rgb(ac) == "FFFF00"
    wb_t.close()
    wb_a.close()


def test_trainer_does_not_leak_answer_metadata(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    wb_t = load_workbook(trainer_path, data_only=False)

    forbidden: list[str] = []
    for comp in smap.all_ordered():
        hint = (comp.short_hint or "").strip()
        if hint:
            forbidden.append(hint)
        for h in comp.hints:
            if h and h.strip():
                forbidden.append(h.strip())
        if comp.formula:
            forbidden.append(comp.formula)

    # Scan answer-bearing locations only: hidden sheets + comments + Trainer index extras
    for name in wb_t.sheetnames:
        if not name.startswith("_") and name != "Trainer":
            continue
        ws = wb_t[name]
        for row in ws.iter_rows(max_row=ws.max_row or 1, max_col=ws.max_column or 1):
            for cell in row:
                val = cell.value
                if not isinstance(val, str):
                    continue
                for needle in forbidden:
                    assert needle not in val, f"leak in {name}: {needle!r}"
                if cell.comment is not None:
                    for needle in forbidden:
                        assert needle not in (cell.comment.text or "")

    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        cell = wb_t[comp.tab].cell(row=row, column=col)
        assert cell.comment is None
        assert cell.value is None

    wb_t.close()


def test_trainer_index_instruction_and_columns(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    wb = load_workbook(trainer_path, data_only=False)
    ws = wb["Trainer"]
    assert ws["A2"].value == TRAINER_INDEX_INSTRUCTION
    headers = [ws.cell(row=4, column=c).value for c in range(1, 7)]
    assert headers == [
        "Order",
        "Schedule",
        "Period scope",
        "Tab",
        "Practice cells",
        "Depends on",
    ]
    assert "Status" not in headers
    text = " ".join(
        str(ws.cell(row=r, column=c).value or "")
        for r in range(1, (ws.max_row or 1) + 1)
        for c in range(1, 7)
    )
    assert "HintActive" not in text
    assert "RevealActive" not in text
    assert "TrainerMacros" not in text
    wb.close()


def test_trainer_index_groups_schedules_not_cells(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    groups = group_components_by_family(smap)
    assert len(groups) == 62

    wb = load_workbook(trainer_path, data_only=False)
    ws = wb["Trainer"]
    index_family_rows = (ws.max_row or 4) - 4
    assert index_family_rows == 62

    by_title = {g["title"]: g for g in groups}
    assert by_title["Revenue historical source link"]["count"] == 5
    assert by_title["NOPAT"]["count"] == 5
    assert by_title["Sales Growth"]["count"] == 4
    assert by_title["Return on Net Operating Assets (RNOA)"]["count"] == 4
    wb.close()


def test_answer_key_practice_cells_formula_yellow_legacy_notes(tmp_path):
    _, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    wb = load_workbook(answer_key_path, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        cell = wb[comp.tab].cell(row=row, column=col)
        assert isinstance(cell.value, str) and cell.value.startswith("=")
        assert cell.value == comp.formula
        assert _fill_rgb(cell) == "FFFF00"
        assert cell.comment is not None
        expected_hint = (comp.short_hint or "").strip() or (
            comp.hints[0] if comp.hints else comp.title
        )
        assert cell.comment.text == expected_hint
        assert cell.comment.author == "BAV Trainer"
    wb.close()


def test_pair_style_and_structure_parity(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)

    visible_t = [s for s in wb_t.sheetnames if not s.startswith("_")]
    visible_a = [s for s in wb_a.sheetnames if not s.startswith("_")]
    assert visible_t == visible_a

    for name in visible_t:
        ws_t, ws_a = wb_t[name], wb_a[name]
        assert ws_t.freeze_panes == ws_a.freeze_panes
        assert bool(ws_t.sheet_view.showGridLines) == bool(ws_a.sheet_view.showGridLines)
        assert list(ws_t.merged_cells.ranges) == list(ws_a.merged_cells.ranges)
        for letter in ("A", "B", "C"):
            assert ws_t.column_dimensions[letter].width == ws_a.column_dimensions[letter].width
        for r in range(1, min(8, (ws_t.max_row or 1) + 1)):
            assert ws_t.row_dimensions[r].height == ws_a.row_dimensions[r].height

    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        ct = wb_t[comp.tab].cell(row=row, column=col)
        ca = wb_a[comp.tab].cell(row=row, column=col)
        assert ct.font.name == ca.font.name
        assert ct.font.size == ca.font.size
        assert ct.font.bold == ca.font.bold
        ct_left = None if ct.border.left is None else ct.border.left.style
        ca_left = None if ca.border.left is None else ca.border.left.style
        assert ct_left == ca_left
        assert ct.alignment.horizontal == ca.alignment.horizontal
        assert ct.alignment.vertical == ca.alignment.vertical
        assert ct.number_format == ca.number_format
        assert bool(ct.protection.locked) == bool(ca.protection.locked)
        assert _fill_rgb(ct) == _fill_rgb(ca) == "FFFF00"

    wb_t.close()
    wb_a.close()


def test_minimal_font_conventions(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for name in wb.sheetnames:
            if name.startswith("_") or wb[name].sheet_state != "visible":
                continue
            ws = wb[name]
            title = ws["A1"]
            assert title.font.name == FONT_NAME
            assert title.font.size == 11
            assert title.font.bold is False
            body = ws.cell(row=6, column=1)
            if body.value is not None:
                assert body.font.name == FONT_NAME
                assert body.font.size == 11
                assert body.font.bold is False
        wb.close()


def test_no_adjacent_hint_cells_on_generation(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for comp in smap.all_ordered():
            row, col = parse_cell_ref(comp.cell)
            adj = wb[comp.tab].cell(row=row, column=col + 1)
            assert adj.value != comp.short_hint
        wb.close()


def test_cli_list_catalog():
    from core.__main__ import main

    assert main(["list"]) == 0


def test_check_scans_all_practice_cells_and_colors_three_states(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comps = smap.all_ordered()

    wb = load_workbook(trainer_path, data_only=False)
    c0 = comps[0]
    r, c = parse_cell_ref(c0.cell)
    wb[c0.tab].cell(r, c).value = c0.formula

    c1 = comps[1]
    r, c = parse_cell_ref(c1.cell)
    wb[c1.tab].cell(r, c).value = "=1+1"
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.total == len(comps)
    assert summary.correct == 1
    assert summary.incorrect == 1
    assert summary.blank == len(comps) - 2

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(c0.cell)
    assert _fill_rgb(wb[c0.tab].cell(r, c)) == "C8E6C9"
    r, c = parse_cell_ref(c1.cell)
    assert _fill_rgb(wb[c1.tab].cell(r, c)) == "FFC7CE"
    for comp in comps[2:]:
        r, c = parse_cell_ref(comp.cell)
        assert _fill_rgb(wb[comp.tab].cell(r, c)) == "FFFF00"
    wb.close()


def test_recheck_refreshes_colors_from_current_contents(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comp = smap.all_ordered()[0]
    row, col = parse_cell_ref(comp.cell)

    wb = load_workbook(trainer_path, data_only=False)
    wb[comp.tab].cell(row, col).value = "=1+1"
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.incorrect >= 1
    wb = load_workbook(trainer_path, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row, col)) == "FFC7CE"

    wb[comp.tab].cell(row, col).value = comp.formula
    wb.save(trainer_path)
    wb.close()
    summary = check_workbook(trainer_path)
    assert summary.correct >= 1
    wb = load_workbook(trainer_path, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row, col)) == "C8E6C9"

    wb[comp.tab].cell(row, col).value = None
    wb.save(trainer_path)
    wb.close()
    summary = check_workbook(trainer_path)
    assert summary.blank == summary.total
    wb = load_workbook(trainer_path, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row, col)) == "FFFF00"
    wb.close()


def test_check_does_not_change_practice_contents_or_add_notes(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comps = smap.all_ordered()

    wb = load_workbook(trainer_path, data_only=False)
    c0 = comps[0]
    r, c = parse_cell_ref(c0.cell)
    wb[c0.tab].cell(r, c).value = c0.formula
    c1 = comps[1]
    r, c = parse_cell_ref(c1.cell)
    wb[c1.tab].cell(r, c).value = "=1+1"
    wb.save(trainer_path)
    wb.close()

    before = {}
    wb = load_workbook(trainer_path, data_only=False)
    for comp in comps:
        r, c = parse_cell_ref(comp.cell)
        before[comp.id] = wb[comp.tab].cell(r, c).value
    wb.close()

    check_workbook(trainer_path)

    wb = load_workbook(trainer_path, data_only=False)
    for comp in comps:
        r, c = parse_cell_ref(comp.cell)
        cell = wb[comp.tab].cell(r, c)
        assert cell.value == before[comp.id]
        assert cell.comment is None
    wb.close()


def test_check_requires_matching_answer_key(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    answer_key_path.unlink()
    answer_key_path.with_suffix(".component_map.json").unlink(missing_ok=True)
    with pytest.raises(FileNotFoundError, match="Answer Key"):
        check_workbook(trainer_path)


def test_cli_check_is_workbook_wide_and_hint_reveal_are_removed(tmp_path, capsys):
    from core.__main__ import main
    import io
    from contextlib import redirect_stdout, redirect_stderr
    from core import __main__ as cli

    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)

    rc = main(["check", "--workbook", str(trainer_path)])
    captured = capsys.readouterr()
    assert rc == 0
    assert f"Checked {len(smap.all_ordered())} practice cells" in captured.out
    assert "blank" in captured.out

    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        try:
            cli.main(["--help"])
        except SystemExit:
            pass
    help_text = buf.getvalue()
    assert "check" in help_text
    # Subcommand names must not include hint/reveal
    assert "\n  hint " not in help_text and not help_text.strip().startswith("hint ")
    assert "  hint\n" not in help_text and "{hint}" not in help_text
    assert "  reveal" not in help_text and "{reveal}" not in help_text
    assert "hint" not in help_text.split("{")[1].split("}")[0] if "{" in help_text else True

    with pytest.raises(SystemExit):
        cli.main(["check", "--workbook", str(trainer_path), "--component", "nopat_fy"])


def test_cli_check_output_does_not_disclose_answers(tmp_path, capsys):
    from core.__main__ import main

    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)

    wb = load_workbook(trainer_path, data_only=False)
    comps = smap.all_ordered()
    r, c = parse_cell_ref(comps[0].cell)
    wb[comps[0].tab].cell(r, c).value = comps[0].formula
    r, c = parse_cell_ref(comps[1].cell)
    wb[comps[1].tab].cell(r, c).value = "=1+1"
    wb.save(trainer_path)
    wb.close()

    main(["check", "--workbook", str(trainer_path)])
    out = capsys.readouterr().out

    for comp in comps:
        assert comp.formula not in out
        if comp.short_hint:
            assert comp.short_hint not in out
        for h in comp.hints:
            assert h not in out
        if comp.expected_value is not None:
            assert str(comp.expected_value) not in out


def test_cli_list_resolved(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    from core.__main__ import main

    assert main(["list", "--workbook", str(trainer_path)]) == 0


def test_cli_build_reports_both_paths(tmp_path, capsys):
    from core.__main__ import main

    out = tmp_path / "DEMO_HK_Trainer.xlsx"
    rc = main(["build", str(DEMO_JSON), "-o", str(out)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Trainer workbook:" in captured.out
    assert "Answer Key workbook:" in captured.out
    assert (tmp_path / "DEMO_HK_Trainer.xlsx").exists()
    assert (tmp_path / "DEMO_HK_Answer_Key.xlsx").exists()


def test_source_data_classifications_and_assumptions_remain_populated(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    practice_coords = {(c.tab, c.cell) for c in smap.all_ordered()}

    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)

    # 1) Source statement values remain identical and non-empty.
    for sheet in ("Income Statement", "Balance Sheet", "Cash Flow Statement"):
        matched = 0
        for row in wb_a[sheet].iter_rows(min_row=7, max_row=40, min_col=2, max_col=6):
            for cell in row:
                if cell.value is None or isinstance(cell.value, str):
                    continue
                tc = wb_t[sheet].cell(row=cell.row, column=cell.column)
                assert tc.value == cell.value
                matched += 1
        assert matched > 0

    # 2) Classification choices remain populated and identical.
    class_start = None
    for r in range(1, 40):
        if wb_a["Condensed Financials"].cell(row=r, column=1).value == "Line Item":
            class_start = r + 1
            break
    assert class_start is not None
    class_count = 0
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
        class_count += 1
        assert ("Condensed Financials", f"B{r}") not in practice_coords
    assert class_count > 0

    wb_t.close()
    wb_a.close()


def test_v1_deferred_tabs_are_hidden_placeholders(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    deferred = {"Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary"}
    smap = load_semantic_map(answer_key_path)

    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for name in deferred:
            ws = wb[name]
            assert ws.sheet_state == "hidden"
            assert ws["A1"].value == "Deferred from historical-only v1"
            assert ws.max_row == 1
            assert ws.max_column == 1
        wb.close()

    for comp in smap.all_ordered():
        for name in deferred:
            assert name not in comp.formula
    assert len(smap.all_ordered()) == 259
    deferred_ids = {
        "model_sales_y1",
        "model_nopat_y1",
        "model_ae_y1",
        "model_tv",
        "model_ivps",
        "scenario_weighted",
    }
    assert deferred_ids.isdisjoint({c.id for c in smap.all_ordered()})


def test_expanded_historical_chain_check_three_states(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    assert len(smap.all_ordered()) == 259

    etr = next(c for c in smap.all_ordered() if c.family_id == "effective_tax_rate_fy")
    owca = next(c for c in smap.all_ordered() if c.family_id == "owca_agg")
    cod = next(c for c in smap.all_ordered() if c.family_id == "after_tax_cod")

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(etr.cell)
    wb[etr.tab].cell(r, c).value = etr.formula
    r, c = parse_cell_ref(owca.cell)
    wb[owca.tab].cell(r, c).value = "=1+1"
    # after_tax_cod left blank
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.total == 259
    assert summary.correct == 1
    assert summary.incorrect == 1
    assert summary.blank == 257

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(etr.cell)
    assert _fill_rgb(wb[etr.tab].cell(r, c)) == "C8E6C9"
    r, c = parse_cell_ref(owca.cell)
    assert _fill_rgb(wb[owca.tab].cell(r, c)) == "FFC7CE"
    r, c = parse_cell_ref(cod.cell)
    assert _fill_rgb(wb[cod.tab].cell(r, c)) == "FFFF00"
    wb.close()

    from core.__main__ import main
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        main(["check", "--workbook", str(trainer_path)])
    out = buf.getvalue()
    for needle in (etr.formula, owca.formula, str(etr.expected_value), etr.short_hint):
        assert needle not in out


def test_hint_reveal_modules_removed():
    assert importlib.util.find_spec("core.trainer.hints") is None
    assert not (ROOT / "core" / "templates" / "TrainerMacros.bas").exists()


_SSML = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
_OD_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _xlsx_sheet_path(zf, sheet_name: str) -> str:
    import xml.etree.ElementTree as ET

    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    sheets = wb.find(f"{{{_SSML}}}sheets")
    if sheets is None:
        raise FileNotFoundError("workbook.xml missing sheets")
    rid = None
    for sheet in sheets:
        if sheet.attrib.get("name") == sheet_name:
            rid = sheet.attrib.get(f"{{{_OD_RELS}}}id")
            break
    if not rid:
        raise FileNotFoundError(f"Sheet not found: {sheet_name}")
    target = None
    for rel in rels:
        if rel.attrib.get("Id") == rid:
            target = rel.attrib.get("Target", "")
            break
    if not target:
        raise FileNotFoundError(f"Relationship missing for sheet {sheet_name}")
    target = target.lstrip("/")
    if not target.startswith("xl/"):
        target = f"xl/{target}"
    return target


def _inject_formula_and_cached_value(
    workbook_path: Path,
    sheet: str,
    cell: str,
    *,
    formula: str,
    cached_value: float,
) -> None:
    """Patch one cell's OOXML <f> and cached <v> without openpyxl rewrite."""
    import os
    import tempfile
    import zipfile
    import xml.etree.ElementTree as ET

    formula_body = formula[1:] if formula.startswith("=") else formula
    workbook_path = Path(workbook_path)

    with zipfile.ZipFile(workbook_path, "r") as zf_in:
        sheet_path = _xlsx_sheet_path(zf_in, sheet)
        sheet_xml = zf_in.read(sheet_path)
        other_members = {
            info.filename: zf_in.read(info.filename)
            for info in zf_in.infolist()
            if info.filename != sheet_path
        }

    root = ET.fromstring(sheet_xml)
    cell_el = None
    for c_el in root.iter(f"{{{_SSML}}}c"):
        if c_el.attrib.get("r") == cell:
            cell_el = c_el
            break
    if cell_el is None:
        raise FileNotFoundError(f"Cell {cell} not found on sheet {sheet}")

    # Replace formula / cached value children; keep style and address.
    for child in list(cell_el):
        if child.tag in {f"{{{_SSML}}}f", f"{{{_SSML}}}v", f"{{{_SSML}}}is"}:
            cell_el.remove(child)
    f_el = ET.SubElement(cell_el, f"{{{_SSML}}}f")
    f_el.text = formula_body
    v_el = ET.SubElement(cell_el, f"{{{_SSML}}}v")
    v_el.text = f"{float(cached_value)}"

    ET.register_namespace("", _SSML)
    new_sheet_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    fd, tmp_name = tempfile.mkstemp(
        suffix=".xlsx", prefix=workbook_path.stem + "_inj_", dir=str(workbook_path.parent)
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        with zipfile.ZipFile(tmp_path, "w") as zf_out:
            for name, data in other_members.items():
                zf_out.writestr(name, data)
            zf_out.writestr(sheet_path, new_sheet_xml)
        tmp_path.replace(workbook_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def test_equivalent_cached_formula_stays_correct_across_repeated_checks(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comp = next(
        c for c in smap.all_ordered() if isinstance(c.expected_value, (int, float))
    )

    _inject_formula_and_cached_value(
        trainer_path,
        comp.tab,
        comp.cell,
        formula=f"={float(comp.expected_value)}",
        cached_value=float(comp.expected_value),
    )

    wb_formula = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    entered_formula = wb_formula[comp.tab].cell(row, col).value
    wb_formula.close()
    assert entered_formula != comp.formula

    first = check_workbook(trainer_path)
    assert first.correct >= 1

    # Check itself must not destroy the cached Excel result.
    wb_cached = load_workbook(trainer_path, data_only=True)
    cached_after_first_check = wb_cached[comp.tab].cell(row, col).value
    wb_cached.close()
    assert cached_after_first_check == pytest.approx(float(comp.expected_value))

    second = check_workbook(trainer_path)
    assert second.correct >= 1

    wb = load_workbook(trainer_path, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row, col)) == "C8E6C9"
    assert wb[comp.tab].cell(row, col).value == entered_formula
    wb.close()


def test_period_aware_semantic_map_round_trip(tmp_path):
    from core.engine.component_catalog import ComponentSpec
    from core.engine.map_embed import embed_component_map_sheet
    from core.engine.semantic_map import SemanticMap
    from openpyxl import Workbook

    specs = (
        ComponentSpec(
            id="nopat_fy__20241231",
            family_id="nopat_fy",
            order=1,
            family_order=6,
            title="NOPAT",
            short_hint="NOPAT hint",
            semantic_key="condensed.nopat.2024-12-31",
            category="accounting",
            tab_template="Condensed Financials",
            period_index=1,
            period_end="2024-12-31",
        ),
        ComponentSpec(
            id="rnoa__20241231",
            family_id="rnoa",
            order=2,
            family_order=20,
            title="RNOA",
            short_hint="RNOA hint",
            semantic_key="dupont.rnoa.2024-12-31",
            category="dupont",
            tab_template="ALT DuPont",
            period_index=1,
            period_end="2024-12-31",
            depends_on=("nopat_fy__20241231",),
        ),
    )
    smap = SemanticMap(expected_specs=specs)
    smap.register(specs[0], "Condensed Financials", 10, 3, "=A1+A2", 100.0)
    smap.register(specs[1], "ALT DuPont", 5, 4, "=B1/B2", 0.12)

    json_path = tmp_path / "map.json"
    smap.save_json(json_path)
    loaded = SemanticMap.load_json(json_path)
    for cid in ("nopat_fy__20241231", "rnoa__20241231"):
        c = loaded.get(cid)
        assert c.family_id in {"nopat_fy", "rnoa"}
        assert c.family_order in {6, 20}
        assert c.period_index == 1
        assert c.period_end == "2024-12-31"

    wb = Workbook()
    embed_component_map_sheet(wb, smap)
    xlsx = tmp_path / "Answer_Key.xlsx"
    wb.save(xlsx)
    wb.close()
    # remove sidecar so from_workbook reads the sheet
    sidecar = xlsx.with_suffix(".component_map.json")
    if sidecar.exists():
        sidecar.unlink()
    from_wb = SemanticMap.from_workbook(xlsx)
    c = from_wb.get("rnoa__20241231")
    assert c.family_id == "rnoa"
    assert c.family_order == 20
    assert c.period_index == 1
    assert c.period_end == "2024-12-31"


def test_multi_period_correction_cycle(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    assert len(smap.all_ordered()) == 259

    nopats = [c for c in smap.all_ordered() if c.family_id == "nopat_fy"]
    assert len(nopats) == 5
    growth = next(c for c in smap.all_ordered() if c.family_id == "sales_growth")

    wb = load_workbook(trainer_path, data_only=False)
    for comp in nopats:
        r, c = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(r, c).value = comp.formula
    r, c = parse_cell_ref(growth.cell)
    wb[growth.tab].cell(r, c).value = "=1+1"
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.total == 259
    assert summary.correct == 5
    assert summary.incorrect == 1
    assert summary.blank == 253

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(growth.cell)
    wb[growth.tab].cell(r, c).value = growth.formula
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.correct == 6
    assert summary.incorrect == 0
    assert summary.blank == 253

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(nopats[0].cell)
    wb[nopats[0].tab].cell(r, c).value = None
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.correct == 5
    assert summary.incorrect == 0
    assert summary.blank == 254

    wb = load_workbook(trainer_path, data_only=False)
    for comp in nopats[1:]:
        r, c = parse_cell_ref(comp.cell)
        assert _fill_rgb(wb[comp.tab].cell(r, c)) == "C8E6C9"
    r, c = parse_cell_ref(growth.cell)
    assert _fill_rgb(wb[growth.tab].cell(r, c)) == "C8E6C9"
    r, c = parse_cell_ref(nopats[0].cell)
    assert _fill_rgb(wb[nopats[0].tab].cell(r, c)) == "FFFF00"
    wb.close()


def test_expand_historical_specs_rejects_non_chronological_periods():
    from datetime import date

    fy2023, fy2024, fy2025 = date(2023, 12, 31), date(2024, 12, 31), date(2025, 12, 31)
    with pytest.raises(ValueError, match="increasing|chronological"):
        expand_historical_specs([fy2025, fy2024])
    with pytest.raises(ValueError, match="duplicate"):
        expand_historical_specs([fy2024, fy2024])
    assert len(expand_historical_specs([fy2023, fy2024, fy2025])) == 68


def test_stale_trainer_sidecars_removed_on_rebuild(tmp_path, capsys):
    from core.__main__ import main

    trainer_path = tmp_path / "DEMO_HK_Trainer.xlsx"
    answer_key_path = tmp_path / "DEMO_HK_Answer_Key.xlsx"
    secret = "SECRET_OLD_FORMULA\nSECRET_OLD_HINT"
    for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
        trainer_path.with_suffix(suffix).write_text(secret, encoding="utf-8")
        assert trainer_path.with_suffix(suffix).exists()

    data = _ingest_demo()
    build_training_workbook(data, trainer_path)

    for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
        assert not trainer_path.with_suffix(suffix).exists()
    assert answer_key_path.with_suffix(".component_map.json").exists()
    assert answer_key_path.with_suffix(".assumptions.json").exists()

    assert main(["list", "--workbook", str(trainer_path)]) == 0
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 62
    assert any("5 cells" in ln for ln in lines)
    assert any("4 cells" in ln for ln in lines)
    assert "SECRET_OLD_FORMULA" not in out
    assert "SECRET_OLD_HINT" not in out


def test_accounting_judgment_sheet_answer_key_and_trainer_contract(tmp_path):
    from core.engine.reference_model import (
        JUDGMENT_INSTRUCTION,
        JUDGMENT_SHEET,
        JUDGMENT_STEP_NOTE,
        ReferenceModelBuilder,
    )

    trainer_path, answer_key_path = _build_pair(tmp_path)
    data = _ingest_demo()
    builder = ReferenceModelBuilder(data)
    assert len(builder.judgment_cases) == 1
    case = builder.judgment_cases[0]

    smap = load_semantic_map(answer_key_path)
    assert len(smap.all_ordered()) == 259

    wb_a = load_workbook(answer_key_path, data_only=False)
    wb_t = load_workbook(trainer_path, data_only=False)
    assert JUDGMENT_SHEET in wb_a.sheetnames and JUDGMENT_SHEET in wb_t.sheetnames
    ws_a = wb_a[JUDGMENT_SHEET]
    ws_t = wb_t[JUDGMENT_SHEET]
    assert ws_a["A1"].value == "Accounting Judgment"
    assert JUDGMENT_INSTRUCTION in str(ws_a["A2"].value)
    assert JUDGMENT_STEP_NOTE in str(ws_a["A3"].value)
    assert "Condensed Financials" in str(ws_a["A3"].value)
    assert "does not grade the judgment response" in str(ws_a["A3"].value).lower()
    assert "drives the matching Condensed Financials" in str(ws_a["A3"].value)
    headers = [ws_a.cell(4, c).value for c in range(1, 9)]
    assert headers == [
        "Order",
        "Line item",
        "Topic",
        "Supplied reference treatment",
        "Alternative(s) to evaluate",
        "Treatment to defend",
        "Rationale",
        "Economic consequence",
    ]
    row = 5
    assert ws_a.cell(row, 1).value == 1
    assert ws_a.cell(row, 2).value == "Operating lease liabilities"
    assert ws_a.cell(row, 4).value == "Operating Long-Term Liability"
    assert ws_a.cell(row, 5).value == "Financial Liability"
    assert ws_a.cell(row, 6).value == case.supplied_treatment
    assert ws_a.cell(row, 7).value == case.model_rationale
    assert ws_a.cell(row, 8).value == case.model_consequence
    for col in (6, 7, 8):
        assert _fill_rgb(ws_a.cell(row, col)) == "FFFF00"
        assert ws_t.cell(row, col).value is None
        assert ws_t.cell(row, col).comment is None
        assert _fill_rgb(ws_t.cell(row, col)) == "FFFF00"
    for col in range(1, 6):
        assert ws_t.cell(row, col).value == ws_a.cell(row, col).value

    formulas = [str(dv.formula1) for dv in ws_a.data_validations.dataValidation]
    assert any(
        "Operating Long-Term Liability" in f and "Financial Liability" in f
        for f in formulas
    )
    trainer_formulas = [str(dv.formula1) for dv in ws_t.data_validations.dataValidation]
    assert any(
        "Operating Long-Term Liability" in f and "Financial Liability" in f
        for f in trainer_formulas
    )

    summary = check_workbook(trainer_path)
    assert summary.total == 259
    assert summary.correct == 0
    assert summary.incorrect == 0
    assert summary.blank == 259

    forbidden = [case.model_rationale, case.model_consequence]
    for name in wb_t.sheetnames:
        ws = wb_t[name]
        for r in ws.iter_rows(max_row=ws.max_row or 1, max_col=ws.max_column or 1):
            for cell in r:
                # Visible judgment response cells must be blank.
                if name == JUDGMENT_SHEET and cell.row == row and cell.column in (6, 7, 8):
                    assert cell.value is None
                    continue
                val = cell.value
                if isinstance(val, str):
                    for needle in forbidden:
                        assert needle not in val
                if cell.comment is not None:
                    for needle in forbidden:
                        assert needle not in (cell.comment.text or "")
    for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
        side = trainer_path.with_suffix(suffix)
        if side.exists():
            text = side.read_text(encoding="utf-8")
            for needle in forbidden:
                assert needle not in text

    wb_a.close()
    wb_t.close()


def test_trainer_instruction_mentions_judgment_not_graded_by_check(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    wb = load_workbook(trainer_path, data_only=False)
    instruction = str(wb["Trainer"]["A2"].value)
    assert instruction == TRAINER_INDEX_INSTRUCTION
    assert "not graded by Check" in instruction
    assert "Condensed Financials" in instruction
    assert "every yellow cell" not in instruction.lower()
    # Accounting Judgment is not an extra formula-family row.
    assert (wb["Trainer"].max_row or 4) - 4 == 62
    wb.close()


def test_direct_constructor_sanitizes_judgment_without_case_objects(tmp_path):
    """Trainer blanking must work from workbook structure alone."""
    from core.engine.reference_model import JUDGMENT_SHEET, ReferenceModelBuilder
    from core.trainer.workbook import TrainingWorkbookGenerator

    data = _ingest_demo()
    answer_key_path = tmp_path / "Direct_Answer_Key.xlsx"
    trainer_path = tmp_path / "Direct_Trainer.xlsx"
    builder = ReferenceModelBuilder(data)
    assert len(builder.judgment_cases) == 1
    case = builder.judgment_cases[0]
    semantic_map = builder.build(answer_key_path)

    # Two-argument constructor — no judgment_cases argument.
    TrainingWorkbookGenerator(answer_key_path, semantic_map).generate(trainer_path)

    wb_t = load_workbook(trainer_path, data_only=False)
    ws = wb_t[JUDGMENT_SHEET]
    for col in (6, 7, 8):
        assert ws.cell(5, col).value is None
        assert ws.cell(5, col).comment is None
        assert _fill_rgb(ws.cell(5, col)) == "FFFF00"
    for needle in (case.model_rationale, case.model_consequence):
        for name in wb_t.sheetnames:
            sheet = wb_t[name]
            for row in sheet.iter_rows(
                max_row=sheet.max_row or 1, max_col=sheet.max_column or 1
            ):
                for cell in row:
                    if isinstance(cell.value, str):
                        assert needle not in cell.value
                    if cell.comment is not None:
                        assert needle not in (cell.comment.text or "")
    wb_t.close()


def test_zero_case_judgment_sheet_is_not_treated_as_response_row(tmp_path):
    from core.engine.reference_model import JUDGMENT_SHEET, ReferenceModelBuilder
    from core.trainer.workbook import TrainingWorkbookGenerator, _judgment_case_rows

    data = _ingest_demo()
    answer_key_path = tmp_path / "Zero_Answer_Key.xlsx"
    trainer_path = tmp_path / "Zero_Trainer.xlsx"
    builder = ReferenceModelBuilder(
        data,
        {
            "classificationOverrides": {
                "label:Operating lease liabilities": "Financial Liability",
            }
        },
    )
    assert builder.judgment_cases == ()
    semantic_map = builder.build(answer_key_path)
    TrainingWorkbookGenerator(answer_key_path, semantic_map).generate(trainer_path)

    wb_a = load_workbook(answer_key_path, data_only=False)
    wb_t = load_workbook(trainer_path, data_only=False)
    assert list(_judgment_case_rows(wb_a[JUDGMENT_SHEET])) == []
    assert list(_judgment_case_rows(wb_t[JUDGMENT_SHEET])) == []
    msg = wb_a[JUDGMENT_SHEET].cell(5, 1).value
    assert isinstance(msg, str) and "No supported" in msg
    assert wb_t[JUDGMENT_SHEET].cell(5, 1).value == msg
    for col in (6, 7, 8):
        # Zero-case message row is not a response row — leave as-is / no forced yellow.
        assert wb_t[JUDGMENT_SHEET].cell(5, col).value is None
    wb_a.close()
    wb_t.close()


def test_check_context_absent_from_trainer(tmp_path):
    from core.trainer.check_context import CHECK_CONTEXT_SHEET, load_check_context

    trainer_path, answer_key_path = _build_pair(tmp_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    assert CHECK_CONTEXT_SHEET not in wb_t.sheetnames
    assert CHECK_CONTEXT_SHEET in wb_a.sheetnames
    assert wb_a[CHECK_CONTEXT_SHEET].sheet_state == "hidden"
    assert load_check_context(answer_key_path) is not None
    wb_t.close()
    wb_a.close()


def test_judgment_link_and_treatment_dropdown_pair_identity(tmp_path):
    from core.engine.reference_model import JUDGMENT_SHEET

    trainer_path, answer_key_path = _build_pair(tmp_path)
    wb_a = load_workbook(answer_key_path, data_only=False)
    wb_t = load_workbook(trainer_path, data_only=False)

    def _lease_b(wb):
        ws = wb["Condensed Financials"]
        for row in range(1, (ws.max_row or 1) + 1):
            if ws.cell(row=row, column=1).value == "Operating lease liabilities":
                return ws.cell(row=row, column=2).value, row
        raise AssertionError("lease row missing")

    formula_a, row = _lease_b(wb_a)
    formula_t, row_t = _lease_b(wb_t)
    assert row == row_t
    assert formula_a == formula_t
    assert isinstance(formula_a, str) and "Accounting Judgment" in formula_a
    assert "$D$" not in formula_a
    assert '"Operating Long-Term Liability"' in formula_a
    assert _fill_rgb(wb_a["Condensed Financials"].cell(row, 2)) != "FFFF00"
    assert _fill_rgb(wb_t["Condensed Financials"].cell(row, 2)) != "FFFF00"

    for wb in (wb_a, wb_t):
        dvs = list(wb[JUDGMENT_SHEET].data_validations.dataValidation)
        assert any("F5" in str(dv.sqref) for dv in dvs)
        assert any(
            "Operating Long-Term Liability" in str(dv.formula1)
            and "Financial Liability" in str(dv.formula1)
            for dv in dvs
        )
    wb_a.close()
    wb_t.close()


def _set_judgment_treatment(trainer_path, treatment):
    wb = load_workbook(trainer_path, data_only=False)
    wb["Accounting Judgment"].cell(5, 6).value = treatment
    wb.save(trainer_path)
    wb.close()


def test_dynamic_check_fresh_reference_parity(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    summary = check_workbook(trainer_path)
    assert summary.total == 259
    assert summary.correct == 0
    assert summary.incorrect == 0
    assert summary.blank == 259


def test_alternative_treatment_exact_formula_is_green(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    from core.data.standardized_io import standardized_from_payload
    from core.model.financial_math import compute_anchor
    from core.model.historical_expected import expected_value_for_component
    from core.model.period_axis import canonical_fiscal_periods
    from core.trainer.check_context import classification_overrides_for_check, load_check_context

    comp = max(
        (c for c in smap.all_ordered() if c.family_id == "net_debt"),
        key=lambda c: c.period_index or 0,
    )
    _set_judgment_treatment(trainer_path, "Financial Liability")

    ctx = load_check_context(answer_key_path)
    wb = load_workbook(trainer_path, data_only=False)
    overrides = classification_overrides_for_check(wb, ctx)
    wb.close()
    fin = standardized_from_payload(ctx.source_payload)
    periods = canonical_fiscal_periods(fin)
    anchor = compute_anchor(fin, periods, classification_overrides=overrides)
    alt_expected = expected_value_for_component(anchor, comp)
    assert alt_expected != pytest.approx(comp.expected_value)

    wb = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.correct == 1
    assert summary.incorrect == 0
    assert summary.blank == 258


def test_alternative_treatment_equivalent_formula_and_stale_reference(tmp_path):
    from core.data.standardized_io import standardized_from_payload
    from core.model.financial_math import compute_anchor
    from core.model.historical_expected import expected_value_for_component
    from core.model.period_axis import canonical_fiscal_periods
    from core.trainer.check_context import classification_overrides_for_check, load_check_context

    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comp = _latest(smap, "net_debt") if False else max(
        (c for c in smap.all_ordered() if c.family_id == "net_debt"),
        key=lambda c: c.period_index or 0,
    )
    _set_judgment_treatment(trainer_path, "Financial Liability")

    ctx = load_check_context(answer_key_path)
    wb = load_workbook(trainer_path, data_only=False)
    overrides = classification_overrides_for_check(wb, ctx)
    wb.close()
    fin = standardized_from_payload(ctx.source_payload)
    periods = canonical_fiscal_periods(fin)
    alt_anchor = compute_anchor(fin, periods, classification_overrides=overrides)
    alt_expected = float(expected_value_for_component(alt_anchor, comp))
    ref_expected = float(comp.expected_value)
    assert alt_expected != pytest.approx(ref_expected)

    # Equivalent non-exact formula with alternative cached value -> green.
    _inject_formula_and_cached_value(
        trainer_path,
        comp.tab,
        comp.cell,
        formula=f"={alt_expected}",
        cached_value=alt_expected,
    )
    summary = check_workbook(trainer_path)
    assert summary.correct == 1
    assert summary.incorrect == 0

    # Repeated Check preserves green + cached value.
    summary2 = check_workbook(trainer_path)
    assert summary2.correct == 1
    wb_cached = load_workbook(trainer_path, data_only=True)
    row, col = parse_cell_ref(comp.cell)
    assert wb_cached[comp.tab].cell(row=row, column=col).value == pytest.approx(alt_expected)
    wb_cached.close()

    # Stale reference cached value under alternative -> red.
    _inject_formula_and_cached_value(
        trainer_path,
        comp.tab,
        comp.cell,
        formula=f"={ref_expected}",
        cached_value=ref_expected,
    )
    summary3 = check_workbook(trainer_path)
    assert summary3.incorrect == 1
    assert summary3.correct == 0


def test_dynamic_check_two_case_combined_state(tmp_path):
    from datetime import date

    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder
    from core.model.financial_math import compute_anchor
    from core.model.historical_expected import expected_value_for_component
    from core.model.period_axis import canonical_fiscal_periods
    from core.trainer.check_context import classification_overrides_for_check, load_check_context
    from core.trainer.workbook import TrainingWorkbookGenerator

    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)

    def li(label, v1, v2, concept=""):
        return LineItem(label=label, concept=concept, values={d1: v1, d2: v2})

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
            li("Finance income", 0, 0),
            li("Profit before tax", 200, 220),
            li("Income tax expense", -30, -33),
            li("Interest expense", -20, -22),
            li("Profit for the year", 150, 165),
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

    wb = load_workbook(trainer, data_only=False)
    wb["Accounting Judgment"].cell(5, 6).value = "Financial Liability"
    wb["Accounting Judgment"].cell(6, 6).value = "Financial Liability"
    wb.save(trainer)
    wb.close()

    ctx = load_check_context(answer)
    wb = load_workbook(trainer, data_only=False)
    overrides = classification_overrides_for_check(wb, ctx)
    wb.close()
    assert overrides["concept:lease_liability"] == "Financial Liability"
    assert any(v == "Financial Liability" for k, v in overrides.items() if "Pension" in k or "pension" in k.lower() or k.startswith("label:"))

    periods = canonical_fiscal_periods(fin)
    combined = compute_anchor(fin, periods, classification_overrides=overrides)
    one_only = compute_anchor(
        fin,
        periods,
        classification_overrides={"concept:lease_liability": "Financial Liability"},
    )
    comp = max(
        (c for c in smap.all_ordered() if c.family_id == "net_debt"),
        key=lambda c: c.period_index or 0,
    )
    combined_expected = float(expected_value_for_component(combined, comp))
    one_expected = float(expected_value_for_component(one_only, comp))
    assert combined_expected != pytest.approx(one_expected)

    _inject_formula_and_cached_value(
        trainer,
        comp.tab,
        comp.cell,
        formula=f"={combined_expected}",
        cached_value=combined_expected,
    )
    summary = check_workbook(trainer)
    assert summary.correct == 1
    assert summary.incorrect == 0


def test_invalid_treatment_raises_before_fill_updates(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    # Enter one exact formula so a successful Check would recolor something.
    smap_path = answer_key_path_for(trainer_path)
    smap = load_semantic_map(smap_path)
    comp = next(c for c in smap.all_ordered())
    wb = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    before_fill = _fill_rgb(wb[comp.tab].cell(row=row, column=col))
    assert before_fill == "FFFF00"
    wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb["Accounting Judgment"].cell(5, 6).value = "Exclude"
    wb.save(trainer_path)
    wb.close()

    with pytest.raises(ValueError, match="Invalid treatment") as excinfo:
        check_workbook(trainer_path)
    msg = str(excinfo.value)
    assert "Exclude" in msg
    assert "5" in msg
    assert comp.formula not in msg

    wb = load_workbook(trainer_path, data_only=False)
    after_fill = _fill_rgb(wb[comp.tab].cell(row=row, column=col))
    assert after_fill == "FFFF00"
    wb.close()

    # Same pair remains usable after the failed attempt.
    _set_judgment_treatment(trainer_path, "Financial Liability")
    summary = check_workbook(trainer_path)
    assert summary.correct == 1
    assert summary.incorrect == 0


def test_legacy_check_context_uses_fixed_expected_values(tmp_path):
    from core.trainer.check_context import CHECK_CONTEXT_SHEET

    trainer_path, answer_key_path = _build_pair(tmp_path)
    # Remove Check context to simulate legacy Answer Key.
    wb = load_workbook(answer_key_path, data_only=False)
    del wb[CHECK_CONTEXT_SHEET]
    wb.save(answer_key_path)
    wb.close()

    smap = load_semantic_map(answer_key_path)
    comp = next(
        c for c in smap.all_ordered() if isinstance(c.expected_value, (int, float))
    )
    _inject_formula_and_cached_value(
        trainer_path,
        comp.tab,
        comp.cell,
        formula=f"={float(comp.expected_value)}",
        cached_value=float(comp.expected_value),
    )
    summary = check_workbook(trainer_path)
    assert summary.correct == 1
    assert summary.incorrect == 0


def _probe_yellow_practice_cell(trainer_path):
    smap = load_semantic_map(answer_key_path_for(trainer_path))
    comp = next(c for c in smap.all_ordered())
    wb = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    assert _fill_rgb(wb[comp.tab].cell(row=row, column=col)) == "FFFF00"
    wb.close()
    return comp


def _assert_probe_still_yellow(trainer_path, comp):
    wb = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    assert _fill_rgb(wb[comp.tab].cell(row=row, column=col)) == "FFFF00"
    wb.close()


def test_judgment_structure_passes_for_blank_and_alternative(tmp_path):
    from core.trainer.check_context import load_check_context, validate_live_judgment_structure

    trainer_path, answer_key_path = _build_pair(tmp_path)
    ctx = load_check_context(answer_key_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    validate_live_judgment_structure(wb_t, wb_a, ctx)
    wb_t["Accounting Judgment"].cell(5, 6).value = "Financial Liability"
    wb_t.save(trainer_path)
    wb_t.close()
    wb_a.close()

    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    validate_live_judgment_structure(wb_t, wb_a, ctx)
    wb_t.close()
    wb_a.close()
    summary = check_workbook(trainer_path)
    assert summary.blank == 259


def test_prompt_modified_d_rejected_before_grading(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    comp = _probe_yellow_practice_cell(trainer_path)
    wb = load_workbook(trainer_path, data_only=False)
    wb["Accounting Judgment"].cell(5, 4).value = "Financial Liability"
    wb.save(trainer_path)
    wb.close()
    with pytest.raises(ValueError, match="reference prompt was modified on row 5"):
        check_workbook(trainer_path)
    _assert_probe_still_yellow(trainer_path, comp)


def test_prompt_modified_e_rejected_before_grading(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    comp = _probe_yellow_practice_cell(trainer_path)
    wb = load_workbook(trainer_path, data_only=False)
    wb["Accounting Judgment"].cell(5, 5).value = "Exclude"
    wb.save(trainer_path)
    wb.close()
    with pytest.raises(ValueError, match="alternatives prompt was modified on row 5"):
        check_workbook(trainer_path)
    _assert_probe_still_yellow(trainer_path, comp)


def test_classification_modified_rejected_before_grading(tmp_path):
    trainer_path, _ = _build_pair(tmp_path)
    comp = _probe_yellow_practice_cell(trainer_path)
    wb = load_workbook(trainer_path, data_only=False)
    ws = wb["Condensed Financials"]
    lease_row = None
    for row in range(1, (ws.max_row or 1) + 1):
        if ws.cell(row=row, column=1).value == "Operating lease liabilities":
            lease_row = row
            break
    assert lease_row is not None
    ws.cell(row=lease_row, column=2).value = "Financial Liability"
    wb.save(trainer_path)
    wb.close()
    with pytest.raises(ValueError, match="Linked Condensed Financials classification was modified"):
        check_workbook(trainer_path)
    _assert_probe_still_yellow(trainer_path, comp)


def test_judgment_structure_two_case_distinct_links(tmp_path):
    from datetime import date

    from core.data.interface import FinancialPeriod, LineItem, StandardizedFinancials
    from core.engine.reference_model import ReferenceModelBuilder
    from core.trainer.check_context import (
        live_classification_formula,
        load_check_context,
        validate_live_judgment_structure,
    )
    from core.trainer.workbook import TrainingWorkbookGenerator

    d1, d2 = date(2024, 12, 31), date(2025, 12, 31)

    def li(label, v1, v2, concept=""):
        return LineItem(label=label, concept=concept, values={d1: v1, d2: v2})

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
            li("Finance income", 0, 0),
            li("Profit before tax", 200, 220),
            li("Income tax expense", -30, -33),
            li("Interest expense", -20, -22),
            li("Profit for the year", 150, 165),
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
    ctx = load_check_context(answer)
    formulas = [
        live_classification_formula(b.worksheet_row, b.reference_treatment)
        for b in ctx.judgment_bindings
    ]
    assert len(set(formulas)) == 2
    wb_t = load_workbook(trainer, data_only=False)
    wb_a = load_workbook(answer, data_only=False)
    validate_live_judgment_structure(wb_t, wb_a, ctx)
    found = []
    for row in range(1, (wb_a["Condensed Financials"].max_row or 1) + 1):
        val = wb_a["Condensed Financials"].cell(row=row, column=2).value
        if val in formulas:
            found.append(val)
    assert sorted(found) == sorted(formulas)
    wb_t.close()
    wb_a.close()
