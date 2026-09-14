#!/usr/bin/env python3
"""Stage-by-stage audit of the Fast Retailing benchmark against the current engine.

Writes BASELINE.md. Does not patch production accounting logic.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
BENCH = ROOT / "benchmark" / "fast_retailing"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"
MANIFEST = BENCH / "source_manifest.json"
BASELINE = BENCH / "BASELINE.md"
EXPECTED_PRACTICE_TOTAL = 491
EXPECTED_BLANK_CHECK = (0, 0, EXPECTED_PRACTICE_TOTAL, EXPECTED_PRACTICE_TOTAL)
EXPECTED_FILLED_CHECK = (EXPECTED_PRACTICE_TOTAL, 0, 0, EXPECTED_PRACTICE_TOTAL)


@dataclass
class StageResult:
    stage: str
    status: str  # pass | fail | skipped
    exception_type: str = ""
    message: str = ""


def _load_payload(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or STD_JSON).read_text(encoding="utf-8"))


SOURCE_STATEMENT_SHEETS: tuple[tuple[str, str], ...] = (
    ("Income Statement", "income_statement"),
    ("Balance Sheet", "balance_sheet"),
    ("Cash Flow Statement", "cash_flow"),
)
SOURCE_HEADER_ROW = 6
SOURCE_START_ROW = 7
PER_SHARE_SHEET = "Per Share Analysis"
PER_SHARE_HEADER_ROW = 4
PER_SHARE_SHARES_ROW = 7
PER_SHARE_SHARES_LABEL = "Diluted Weighted-Average Shares"
DEFERRED_TAB_NAMES = ("Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary")
LEASE_INTEREST_LABEL = "Lease interest expense (reported note)"
JUDGMENT_SHEETS = ("Accounting Judgment", "Normalization Judgment")
JUDGMENT_RESPONSE_COLS = (6, 7, 8)


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _copy_release_pair_to_temp(
    trainer_path: Path,
    answer_key_path: Path,
    tmp: Path,
) -> tuple[Path, Path]:
    """Copy Trainer/Answer Key and Answer Key sidecars for mutating Check ops."""
    trainer_copy = tmp / trainer_path.name
    answer_copy = tmp / answer_key_path.name
    shutil.copy2(trainer_path, trainer_copy)
    shutil.copy2(answer_key_path, answer_copy)
    for suffix in (".component_map.json", ".assumptions.json", ".trainer.json"):
        sidecar = answer_key_path.with_suffix(suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, tmp / sidecar.name)
    return trainer_copy, answer_copy


def _cell_addr(row: int, col: int) -> str:
    from openpyxl.utils import get_column_letter

    return f"{get_column_letter(col)}{row}"


def _as_date(value: Any):
    from datetime import date, datetime

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _color_token(color) -> str:
    if color is None:
        return ""
    rgb = getattr(color, "rgb", None)
    if rgb is not None:
        return f"rgb:{str(rgb).upper()}"
    theme = getattr(color, "theme", None)
    if theme is not None:
        tint = getattr(color, "tint", 0.0) or 0.0
        return f"theme:{theme}:{tint}"
    indexed = getattr(color, "indexed", None)
    if indexed is not None:
        return f"indexed:{indexed}"
    auto = getattr(color, "auto", None)
    if auto:
        return "auto"
    return ""


def _border_token(border) -> tuple:
    if border is None:
        return ()
    sides = []
    for name in ("left", "right", "top", "bottom", "diagonal"):
        side = getattr(border, name, None)
        if side is None:
            sides.append((name, None, ""))
        else:
            sides.append((name, side.style, _color_token(side.color)))
    return tuple(sides)


def _format_signature(cell) -> tuple:
    font = cell.font
    fill = cell.fill
    alignment = cell.alignment
    protection = cell.protection
    fill_type = fill.fill_type if fill is not None else None
    fg = ""
    if fill is not None and fill_type == "solid":
        fg = _color_token(fill.fgColor) or _color_token(fill.start_color)
    return (
        font.name if font else None,
        font.size if font else None,
        bool(font.bold) if font else False,
        bool(font.italic) if font else False,
        _color_token(font.color) if font else "",
        fill_type,
        fg,
        cell.number_format,
        alignment.horizontal if alignment else None,
        alignment.vertical if alignment else None,
        bool(protection.locked) if protection else True,
        _border_token(cell.border),
    )


def _comment_text(cell) -> str:
    if cell.comment is None:
        return ""
    return str(cell.comment.text or "")


def _is_formula(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("=")


def _source_failure(
    workbook: str,
    sheet: str,
    row: int,
    col: int,
    source_identity: str,
    period: Any,
    expected: Any,
    actual: Any,
    reason: str = "",
) -> ValueError:
    period_s = "" if period is None else str(period)
    detail = reason or "value mismatch"
    return ValueError(
        f"{detail}: workbook={workbook} sheet={sheet!r} cell={_cell_addr(row, col)} "
        f"source_identity={source_identity!r} period={period_s!r} "
        f"expected={expected!r} actual={actual!r}"
    )


def _canonical_periods(fin) -> list:
    from core.model.period_axis import canonical_fiscal_periods

    return canonical_fiscal_periods(fin)


def _verify_period_headers(
    ws,
    *,
    workbook: str,
    sheet: str,
    header_row: int,
    periods: list,
    start_col: int = 2,
) -> None:
    for j, expected in enumerate(periods):
        col = start_col + j
        actual = ws.cell(row=header_row, column=col).value
        actual_date = _as_date(actual)
        if actual_date != expected:
            raise _source_failure(
                workbook,
                sheet,
                header_row,
                col,
                "period_header",
                expected,
                expected,
                actual,
                reason="period header mismatch",
            )


def _verify_source_value(
    cell,
    *,
    workbook: str,
    sheet: str,
    row: int,
    col: int,
    source_identity: str,
    period: Any,
    expected: Any,
) -> None:
    actual = cell.value
    if _is_formula(actual):
        raise _source_failure(
            workbook,
            sheet,
            row,
            col,
            source_identity,
            period,
            expected,
            actual,
            reason="source fact replaced by formula",
        )
    if expected is None:
        if actual is not None:
            raise _source_failure(
                workbook,
                sheet,
                row,
                col,
                source_identity,
                period,
                None,
                actual,
                reason="missing source fact blanked incorrectly",
            )
        return
    if actual is None:
        raise _source_failure(
            workbook,
            sheet,
            row,
            col,
            source_identity,
            period,
            expected,
            actual,
            reason="required source fact blanked",
        )
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if float(actual) != float(expected):
            raise _source_failure(
                workbook,
                sheet,
                row,
                col,
                source_identity,
                period,
                expected,
                actual,
            )
        return
    if actual != expected:
        raise _source_failure(
            workbook,
            sheet,
            row,
            col,
            source_identity,
            period,
            expected,
            actual,
        )


def _verify_statement_sheet(ws, items, periods, *, workbook: str, sheet: str) -> None:
    from core.data.line_identity import line_identity

    _verify_period_headers(
        ws,
        workbook=workbook,
        sheet=sheet,
        header_row=SOURCE_HEADER_ROW,
        periods=periods,
    )
    for idx, item in enumerate(items):
        row = SOURCE_START_ROW + idx
        identity = line_identity(item).key()
        label_cell = ws.cell(row=row, column=1)
        if label_cell.value != item.label:
            raise _source_failure(
                workbook,
                sheet,
                row,
                1,
                identity,
                None,
                item.label,
                label_cell.value,
                reason="source row label mismatch",
            )
        for j, period in enumerate(periods):
            col = 2 + j
            expected = item.values.get(period)
            _verify_source_value(
                ws.cell(row=row, column=col),
                workbook=workbook,
                sheet=sheet,
                row=row,
                col=col,
                source_identity=identity,
                period=period,
                expected=expected,
            )


def _verify_workbook_source_fidelity(wb, fin, *, workbook: str) -> None:
    periods = _canonical_periods(fin)
    statement_attrs = {
        "Income Statement": fin.income_statement,
        "Balance Sheet": fin.balance_sheet,
        "Cash Flow Statement": fin.cash_flow,
    }
    for sheet, _attr in SOURCE_STATEMENT_SHEETS:
        if sheet not in wb.sheetnames:
            raise ValueError(
                f"missing required source sheet: workbook={workbook} sheet={sheet!r}"
            )
        ws = wb[sheet]
        expected_units = f"Units: {fin.units}"
        actual_units = ws.cell(row=3, column=1).value
        if actual_units != expected_units:
            raise _source_failure(
                workbook,
                sheet,
                3,
                1,
                "units",
                None,
                expected_units,
                actual_units,
                reason="units mismatch",
            )
        _verify_statement_sheet(
            ws,
            statement_attrs[sheet],
            periods,
            workbook=workbook,
            sheet=sheet,
        )
        if sheet == "Income Statement" and fin.historical_lease is not None:
            lease_row = None
            for row in range(SOURCE_START_ROW, (ws.max_row or SOURCE_START_ROW) + 1):
                if ws.cell(row=row, column=1).value == LEASE_INTEREST_LABEL:
                    lease_row = row
                    break
            if lease_row is None:
                raise ValueError(
                    f"missing lease interest source row: workbook={workbook} "
                    f"sheet={sheet!r} source_identity={LEASE_INTEREST_LABEL!r}"
                )
            for j, period in enumerate(periods):
                col = 2 + j
                expected = fin.historical_lease.lease_interest_expense.get(period)
                expected = None if expected is None else float(expected)
                _verify_source_value(
                    ws.cell(row=lease_row, column=col),
                    workbook=workbook,
                    sheet=sheet,
                    row=lease_row,
                    col=col,
                    source_identity="historical_lease.lease_interest_expense",
                    period=period,
                    expected=expected,
                )

    if fin.historical_shares is None:
        return
    if PER_SHARE_SHEET not in wb.sheetnames:
        raise ValueError(
            f"missing required source sheet: workbook={workbook} "
            f"sheet={PER_SHARE_SHEET!r}"
        )
    ws = wb[PER_SHARE_SHEET]
    _verify_period_headers(
        ws,
        workbook=workbook,
        sheet=PER_SHARE_SHEET,
        header_row=PER_SHARE_HEADER_ROW,
        periods=periods,
    )
    label = ws.cell(row=PER_SHARE_SHARES_ROW, column=1).value
    if label != PER_SHARE_SHARES_LABEL:
        raise _source_failure(
            workbook,
            PER_SHARE_SHEET,
            PER_SHARE_SHARES_ROW,
            1,
            "historical_shares.diluted_weighted_average",
            None,
            PER_SHARE_SHARES_LABEL,
            label,
            reason="historical shares label mismatch",
        )
    for j, period in enumerate(periods):
        col = 2 + j
        expected = fin.historical_shares.diluted_weighted_average.get(period)
        _verify_source_value(
            ws.cell(row=PER_SHARE_SHARES_ROW, column=col),
            workbook=workbook,
            sheet=PER_SHARE_SHEET,
            row=PER_SHARE_SHARES_ROW,
            col=col,
            source_identity="historical_shares.diluted_weighted_average",
            period=period,
            expected=expected,
        )


def _comparable_sheet_names(wb) -> list[str]:
    """Non-metadata sheets in workbook order (includes deferred placeholders)."""
    return [name for name in wb.sheetnames if not name.startswith("_")]


def _requires_visible(name: str) -> bool:
    return not name.startswith("_") and name not in DEFERRED_TAB_NAMES


def _verify_required_visibility(wb, *, workbook: str) -> None:
    for sheet, _attr in SOURCE_STATEMENT_SHEETS:
        if sheet not in wb.sheetnames:
            raise ValueError(
                f"missing required source sheet: workbook={workbook} sheet={sheet!r}"
            )
    for name in wb.sheetnames:
        if not _requires_visible(name):
            continue
        state = wb[name].sheet_state
        if state != "visible":
            raise ValueError(
                f"required historical/practice sheet hidden: workbook={workbook} "
                f"sheet={name!r} sheet_state={state!r}"
            )


def _dim_hidden(dimension) -> bool:
    return bool(getattr(dimension, "hidden", False))


def _verify_visible_layout_parity(wb_t, wb_a, practice_coords: set[tuple[str, int, int]]) -> None:
    from openpyxl.utils import get_column_letter

    comparable_t = _comparable_sheet_names(wb_t)
    comparable_a = _comparable_sheet_names(wb_a)
    if comparable_t != comparable_a:
        raise ValueError(
            f"sheet order/state mismatch: trainer={comparable_t} answer={comparable_a}"
        )
    for name in comparable_t:
        if wb_t[name].sheet_state != wb_a[name].sheet_state:
            raise ValueError(
                f"sheet_state mismatch for {name!r}: "
                f"trainer={wb_t[name].sheet_state!r} answer={wb_a[name].sheet_state!r}"
            )

    visible = [
        name
        for name in comparable_t
        if wb_t[name].sheet_state == "visible" and wb_a[name].sheet_state == "visible"
    ]
    for name in visible:
        ws_t = wb_t[name]
        ws_a = wb_a[name]
        if (ws_t.max_row, ws_t.max_column) != (ws_a.max_row, ws_a.max_column):
            raise ValueError(
                f"visible dimensions mismatch on {name!r}: "
                f"trainer={(ws_t.max_row, ws_t.max_column)} "
                f"answer={(ws_a.max_row, ws_a.max_column)}"
            )
        if ws_t.freeze_panes != ws_a.freeze_panes:
            raise ValueError(
                f"freeze_panes mismatch on {name!r}: "
                f"trainer={ws_t.freeze_panes!r} answer={ws_a.freeze_panes!r}"
            )
        if list(ws_t.merged_cells.ranges) != list(ws_a.merged_cells.ranges):
            raise ValueError(f"merged ranges mismatch on {name!r}")
        max_row = max(ws_t.max_row or 1, ws_a.max_row or 1)
        max_col = max(ws_t.max_column or 1, ws_a.max_column or 1)
        for row in range(1, max_row + 1):
            if _dim_hidden(ws_t.row_dimensions[row]) != _dim_hidden(
                ws_a.row_dimensions[row]
            ):
                raise ValueError(f"row hidden mismatch on {name!r} row={row}")
            if ws_t.row_dimensions[row].height != ws_a.row_dimensions[row].height:
                raise ValueError(f"row height mismatch on {name!r} row={row}")
        for col in range(1, max_col + 1):
            letter = get_column_letter(col)
            if _dim_hidden(ws_t.column_dimensions[letter]) != _dim_hidden(
                ws_a.column_dimensions[letter]
            ):
                raise ValueError(f"column hidden mismatch on {name!r} col={letter}")
            if ws_t.column_dimensions[letter].width != ws_a.column_dimensions[letter].width:
                raise ValueError(f"column width mismatch on {name!r} col={letter}")
        for row in range(1, max_row + 1):
            for col in range(1, max_col + 1):
                ct = ws_t.cell(row=row, column=col)
                ca = ws_a.cell(row=row, column=col)
                allowed_content_diff = (name, row, col) in practice_coords or (
                    name in JUDGMENT_SHEETS and col in JUDGMENT_RESPONSE_COLS
                )
                if not allowed_content_diff:
                    if ct.value != ca.value:
                        raise ValueError(
                            f"non-practice value mismatch: sheet={name!r} "
                            f"cell={_cell_addr(row, col)} "
                            f"trainer={ct.value!r} answer={ca.value!r}"
                        )
                    if _comment_text(ct) != _comment_text(ca):
                        raise ValueError(
                            f"non-practice Note mismatch: sheet={name!r} "
                            f"cell={_cell_addr(row, col)}"
                        )
                if _format_signature(ct) != _format_signature(ca):
                    raise ValueError(
                        f"effective formatting mismatch: sheet={name!r} "
                        f"cell={_cell_addr(row, col)}"
                    )


def _verify_practice_contract(wb_t, wb_a, comps) -> None:
    from core.trainer.semantic_io import parse_cell_ref

    for comp in comps:
        row, col = parse_cell_ref(comp.cell)
        tc = wb_t[comp.tab].cell(row=row, column=col)
        ac = wb_a[comp.tab].cell(row=row, column=col)
        if tc.value is not None:
            raise ValueError(f"Trainer practice cell {comp.tab}!{comp.cell} not blank")
        if tc.comment is not None:
            raise ValueError(f"Trainer practice cell {comp.tab}!{comp.cell} has Note")
        if _fill_rgb(tc) != "FFFF00":
            raise ValueError(f"Trainer practice cell {comp.tab}!{comp.cell} not yellow")
        if not (isinstance(ac.value, str) and ac.value.startswith("=")):
            raise ValueError(f"Answer Key {comp.tab}!{comp.cell} missing formula")
        if ac.value != comp.formula:
            raise ValueError(
                f"Answer Key {comp.tab}!{comp.cell} formula != semantic map"
            )
        if ac.comment is None or not str(ac.comment.text or "").strip():
            raise ValueError(
                f"Answer Key {comp.tab}!{comp.cell} missing non-empty Note"
            )
        if _fill_rgb(ac) != "FFFF00":
            raise ValueError(
                f"Answer Key practice cell {comp.tab}!{comp.cell} not yellow"
            )


def _verify_release_pair_contract(
    trainer_path: Path,
    answer_key_path: Path,
    fin,
) -> str:
    """Source fidelity, practice contract, visibility, and visible structural parity."""
    from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
    from openpyxl import load_workbook

    smap = load_semantic_map(answer_key_path)
    comps = smap.all_ordered()
    if len(comps) != EXPECTED_PRACTICE_TOTAL:
        raise ValueError(
            f"semantic practice cells={len(comps)} != {EXPECTED_PRACTICE_TOTAL}"
        )
    practice_coords = {
        (comp.tab, *parse_cell_ref(comp.cell)) for comp in comps
    }

    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    try:
        _verify_workbook_source_fidelity(wb_t, fin, workbook="Trainer")
        _verify_workbook_source_fidelity(wb_a, fin, workbook="Answer Key")
        _verify_required_visibility(wb_t, workbook="Trainer")
        _verify_required_visibility(wb_a, workbook="Answer Key")
        _verify_visible_layout_parity(wb_t, wb_a, practice_coords)
        _verify_practice_contract(wb_t, wb_a, comps)
    finally:
        wb_t.close()
        wb_a.close()
    return (
        f"practice_cells={len(comps)} source_fidelity=ok "
        f"visibility=ok layout_parity=ok"
    )


def _module_applicability(fin, anchor=None) -> dict[str, Any]:
    from core.model.earnings_quality import earnings_quality_availability
    from core.model.deferred_tax import (
        deferred_tax_applicable,
        deferred_tax_availability,
    )
    from core.model.fixed_asset import fixed_asset_applicable
    from core.model.goodwill_intangibles import (
        goodwill_intangibles_applicable,
        goodwill_intangibles_availability,
    )
    from core.model.lease_liability import (
        lease_liability_applicable,
        lease_liability_availability,
    )
    from core.model.lease_rou import (
        lease_rou_applicable,
        lease_rou_availability,
    )
    from core.model.ownership_attribution import (
        ownership_attribution_applicable,
        ownership_attribution_availability,
    )
    from core.model.per_share import per_share_available
    from core.model.working_capital import working_capital_applicable

    lease_avail = lease_liability_availability(fin)
    lease_rou_avail = lease_rou_availability(fin)
    ownership_avail = ownership_attribution_availability(fin)
    gi_avail = goodwill_intangibles_availability(fin)
    deferred_tax_avail = deferred_tax_availability(fin)
    eq = earnings_quality_availability(fin)
    wc_applicable: bool | None
    if anchor is None:
        wc_applicable = None
    else:
        wc_applicable = working_capital_applicable(anchor)
    return {
        "earnings_quality": {
            "applicable": bool(eq.operating_cash_flow),
            "detail": asdict(eq),
        },
        "working_capital": {
            "applicable": wc_applicable,
            "detail": "requires AnchorMetrics; filled after successful builder"
            if anchor is None
            else "",
        },
        "fixed_asset": {"applicable": fixed_asset_applicable(fin)},
        "lease_liability": {
            "applicable": lease_liability_applicable(fin),
            "availability": asdict(lease_avail),
        },
        "lease_rou": {
            "applicable": lease_rou_applicable(fin),
            "availability": asdict(lease_rou_avail),
        },
        "ownership_attribution": {
            "applicable": ownership_attribution_applicable(fin),
            "availability": asdict(ownership_avail),
        },
        "goodwill_intangibles": {
            "applicable": goodwill_intangibles_applicable(fin),
            "availability": asdict(gi_avail),
        },
        "deferred_tax": {
            "applicable": deferred_tax_applicable(fin),
            "availability": asdict(deferred_tax_avail),
        },
        "per_share": {"applicable": per_share_available(fin)},
        "normalization": {
            "applicable": False,
            "detail": "no normalization assumptions supplied for benchmark audit",
        },
    }


def run_audit(
    *,
    standardized_json: Path | None = None,
    provenance_json: Path | None = None,
    conflicts_json: Path | None = None,
    trainer_path: Path | None = None,
    answer_key_path: Path | None = None,
    require_check_counts: bool | None = None,
    verify_release_pair: bool = False,
) -> dict[str, Any]:
    """Run the Fast Retailing stage audit.

    Default call with no arguments preserves the historical temporary-workbook
    interface used by existing tests. Pass explicit release workbook paths and
    generated standardized JSON to verify a persisted pair without regenerating
    substitute workbooks.
    """
    std_path = Path(standardized_json) if standardized_json else STD_JSON
    explicit_pair = trainer_path is not None or answer_key_path is not None
    if explicit_pair:
        if trainer_path is None or answer_key_path is None:
            raise ValueError("trainer_path and answer_key_path must be provided together")
        trainer_path = Path(trainer_path)
        answer_key_path = Path(answer_key_path)
        if require_check_counts is None:
            require_check_counts = True
    elif require_check_counts is None:
        require_check_counts = False

    stages: list[StageResult] = []
    context: dict[str, Any] = {
        "modules": {},
        "first_failure": None,
        "workbook_paths": {},
        "release_fingerprints_before": {},
        "release_fingerprints_after": {},
        "standardized_json": str(std_path),
        "provenance_json": str(provenance_json or PROV_JSON),
        "conflicts_json": str(conflicts_json or CONFLICTS_JSON),
    }

    def _fingerprint(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    release_files: list[Path] = []
    if explicit_pair:
        release_files = [
            trainer_path,
            answer_key_path,
            answer_key_path.with_suffix(".component_map.json"),
        ]
        for path in (trainer_path, answer_key_path):
            if not path.is_file():
                stages.append(
                    StageResult(
                        "1_source_fixture_load",
                        "fail",
                        "FileNotFoundError",
                        f"missing release artifact: {path}",
                    )
                )
                context["first_failure"] = stages[-1]
                for name in (
                    "2_identity_validation",
                    "3_reconciliation",
                    "4_reference_model_builder",
                    "5_workbook_generation",
                    "6_blank_check",
                    "7_filled_check",
                ):
                    stages.append(
                        StageResult(name, "skipped", message="prior stage failed")
                    )
                return {"stages": stages, "context": context}
        context["release_fingerprints_before"] = {
            str(p): _fingerprint(p) for p in release_files if p.is_file()
        }

    # Stage 1
    try:
        if not std_path.is_file():
            raise FileNotFoundError(f"missing standardized input: {std_path}")
        payload = _load_payload(std_path)
        assert payload["ticker"] == "6288.HK"
        assert payload.get("company_name") == "FAST RETAILING CO., LTD."
        assert [p["end_date"] for p in payload["periods"]] == [
            "2021-08-31",
            "2022-08-31",
            "2023-08-31",
            "2024-08-31",
            "2025-08-31",
        ]
        stages.append(StageResult("1_source_fixture_load", "pass", message="loaded"))
    except Exception as exc:  # noqa: BLE001 — audit must capture all failures
        stages.append(
            StageResult(
                "1_source_fixture_load",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        context["first_failure"] = stages[-1]
        for name in (
            "2_identity_validation",
            "3_reconciliation",
            "4_reference_model_builder",
            "5_workbook_generation",
            "6_blank_check",
            "7_filled_check",
        ):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        return {"stages": stages, "context": context}

    from core.data.standardized_io import standardized_from_payload

    fin = standardized_from_payload(payload)

    # Stage 2
    try:
        from core.data.line_identity import validate_financials_identities

        validate_financials_identities(fin)
        stages.append(StageResult("2_identity_validation", "pass"))
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult("2_identity_validation", "fail", type(exc).__name__, str(exc))
        )
        context["first_failure"] = stages[-1]
        for name in (
            "3_reconciliation",
            "4_reference_model_builder",
            "5_workbook_generation",
            "6_blank_check",
            "7_filled_check",
        ):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        context["modules"] = _module_applicability(fin)
        return {"stages": stages, "context": context}

    # Stage 3
    try:
        from core.ingestion.reconciler import reconcile_financials

        report = reconcile_financials(fin)
        if not all(report.checksums.values()):
            raise ValueError(
                f"reconciliation checksums={report.checksums} warnings={report.warnings}"
            )
        stages.append(StageResult("3_reconciliation", "pass"))
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult("3_reconciliation", "fail", type(exc).__name__, str(exc))
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        # Continue measuring later stages where possible — identity already passed.
        # But workbook generation may still be attempted; mark dependent skips only
        # if builder cannot run. We still try builder for gap visibility.

    context["modules"] = _module_applicability(fin)

    # Stage 4
    builder = None
    try:
        from core.engine.reference_model import ReferenceModelBuilder

        builder = ReferenceModelBuilder(fin)
        stages.append(
            StageResult(
                "4_reference_model_builder",
                "pass",
                message=(
                    f"expected_specs={len(builder.expected_specs)} "
                    f"lease_specs={len(builder.lease_liability_specs)} "
                    f"lease_rou_specs={len(builder.lease_rou_specs)} "
                    f"ownership_specs={len(builder.ownership_attribution_specs)} "
                    f"per_share_specs={len(builder.per_share_specs)} "
                    f"per_share_attribution_specs={len(builder.per_share_attribution_specs)} "
                    f"fixed_asset_specs={len(builder.fixed_asset_specs)} "
                    f"goodwill_intangibles_specs={len(builder.goodwill_intangibles_specs)} "
                    f"deferred_tax_specs={len(builder.deferred_tax_specs)} "
                    f"capex_specs={len(builder.capex_specs)}"
                ),
            )
        )
        context["modules"] = _module_applicability(fin, builder.anchor)
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult(
                "4_reference_model_builder",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        for name in ("5_workbook_generation", "6_blank_check", "7_filled_check"):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        return {"stages": stages, "context": context}

    # Stage 5–7: either use persisted release pair or generate temporary workbooks.
    try:
        from core.trainer.checker import check_workbook
        from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
        from openpyxl import load_workbook

        with tempfile.TemporaryDirectory(prefix="fr_bench_") as tmp:
            tmp_path = Path(tmp)
            if explicit_pair:
                assert trainer_path is not None and answer_key_path is not None
                if verify_release_pair:
                    contract_msg = _verify_release_pair_contract(
                        trainer_path, answer_key_path, fin
                    )
                else:
                    contract_msg = "release pair supplied"
                # Mutating Check / fill on copies only.
                trainer, answer = _copy_release_pair_to_temp(
                    trainer_path, answer_key_path, tmp_path
                )
                context["workbook_paths"] = {
                    "trainer": str(trainer_path),
                    "answer": str(answer_key_path),
                    "check_copies": str(tmp_path),
                    "note": "persisted release pair; Check used temporary copies",
                    "contract": contract_msg,
                }
                stages.append(
                    StageResult(
                        "5_workbook_generation",
                        "pass",
                        message="persisted release pair (not regenerated)",
                    )
                )
            else:
                from core.trainer.workbook import build_training_workbook

                trainer, answer = build_training_workbook(
                    fin, tmp_path / "FastRetailing_Trainer.xlsx"
                )
                context["workbook_paths"] = {
                    "trainer": str(trainer),
                    "answer": str(answer),
                    "note": "temporary only; not committed",
                }
                stages.append(StageResult("5_workbook_generation", "pass"))

            # Stage 6
            try:
                summary = check_workbook(trainer)
                blank_tuple = (
                    summary.correct,
                    summary.incorrect,
                    summary.blank,
                    summary.total,
                )
                if require_check_counts and blank_tuple != EXPECTED_BLANK_CHECK:
                    raise ValueError(
                        f"pristine Check counts {blank_tuple} != {EXPECTED_BLANK_CHECK}"
                    )
                stages.append(
                    StageResult(
                        "6_blank_check",
                        "pass",
                        message=(
                            f"correct={summary.correct} incorrect={summary.incorrect} "
                            f"blank={summary.blank} total={summary.total}"
                        ),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                stages.append(
                    StageResult("6_blank_check", "fail", type(exc).__name__, str(exc))
                )
                if context["first_failure"] is None:
                    context["first_failure"] = stages[-1]
                stages.append(
                    StageResult("7_filled_check", "skipped", message="prior stage failed")
                )
                if explicit_pair:
                    context["release_fingerprints_after"] = {
                        str(p): _fingerprint(p)
                        for p in release_files
                        if p.is_file()
                    }
                return {"stages": stages, "context": context}

            # Stage 7
            try:
                smap = load_semantic_map(answer)
                wb = load_workbook(trainer, data_only=False)
                for comp in smap.all_ordered():
                    row, col = parse_cell_ref(comp.cell)
                    wb[comp.tab].cell(row=row, column=col).value = comp.formula
                wb.save(trainer)
                wb.close()
                filled = check_workbook(trainer)
                filled_tuple = (
                    filled.correct,
                    filled.incorrect,
                    filled.blank,
                    filled.total,
                )
                if require_check_counts:
                    if filled_tuple != EXPECTED_FILLED_CHECK:
                        raise ValueError(
                            f"filled Check counts {filled_tuple} != {EXPECTED_FILLED_CHECK}"
                        )
                elif filled.incorrect or filled.blank:
                    raise ValueError(
                        f"filled check incomplete: correct={filled.correct} "
                        f"incorrect={filled.incorrect} blank={filled.blank}"
                    )
                stages.append(
                    StageResult(
                        "7_filled_check",
                        "pass",
                        message=f"correct={filled.correct} total={filled.total}",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                stages.append(
                    StageResult("7_filled_check", "fail", type(exc).__name__, str(exc))
                )
                if context["first_failure"] is None:
                    context["first_failure"] = stages[-1]
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult(
                "5_workbook_generation",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        for name in ("6_blank_check", "7_filled_check"):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))

    if explicit_pair:
        context["release_fingerprints_after"] = {
            str(p): _fingerprint(p) for p in release_files if p.is_file()
        }
        before = context["release_fingerprints_before"]
        after = context["release_fingerprints_after"]
        if before and after and before != after:
            stages.append(
                StageResult(
                    "8_release_pristine",
                    "fail",
                    "AssertionError",
                    "release artifacts mutated during verification",
                )
            )
            if context["first_failure"] is None:
                context["first_failure"] = stages[-1]
        elif before:
            stages.append(
                StageResult(
                    "8_release_pristine",
                    "pass",
                    message="release fingerprints unchanged",
                )
            )

    return {"stages": stages, "context": context}


def write_baseline(result: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    provenance = json.loads(PROV_JSON.read_text(encoding="utf-8"))
    conflicts = (
        json.loads(CONFLICTS_JSON.read_text(encoding="utf-8"))
        if CONFLICTS_JSON.is_file()
        else {}
    )
    stages: list[StageResult] = result["stages"]
    ctx = result["context"]
    overlap = conflicts.get(
        "overlap_conflict_count", provenance.get("overlap_conflict_count", 0)
    )
    supplemental = conflicts.get(
        "supplemental_conflict_count",
        provenance.get("supplemental_conflict_count", 0),
    )
    lines = [
        "# Fast Retailing Benchmark Baseline (Step 9M.7)",
        "",
        "- Accounting engine phase: Step 9M.7 (deferred-tax balance diagnostics on 9M.6 base)",
        "- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/`",
        "- Benchmark phase: measurement only — G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed",
        "- Five fiscal periods: 2021-08-31 … 2025-08-31",
        "",
        "## Source hashes",
        "",
    ]
    for src in manifest["sources"]:
        lines.append(
            f"- FY{src['fiscal_year']}: `{src['sha256']}` ({src['bytes']} bytes)"
        )
    lines.extend(
        [
            "",
            f"- Overlap conflicts recorded in conflicts.json: **{overlap}**",
            f"- Supplemental conflicts recorded in conflicts.json: **{supplemental}**",
            f"- Standardized payload: `{STD_JSON.relative_to(ROOT)}`",
            "- Supplemental provenance source-bound: yes",
            "- Portable source-path validation: yes",
            "- Silent repeated-share overwrite removed: yes",
            "- G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed; G7 disagreements retained with verified deterministic selection and provenance.",
            "",
            "## Stage results",
            "",
            "| Stage | Status | Detail |",
            "|---|---|---|",
        ]
    )
    for stage in stages:
        detail = stage.message or stage.exception_type
        detail = detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {stage.stage} | {stage.status} | {detail} |")

    first = ctx.get("first_failure")
    lines.extend(["", "## First failure", ""])
    if first is None:
        lines.append("None — all stages passed.")
    else:
        lines.append(f"- Stage: `{first.stage}`")
        lines.append(f"- Status: `{first.status}`")
        lines.append(f"- Exception: `{first.exception_type}`")
        lines.append(f"- Message: {first.message}")

    lines.extend(["", "## Module applicability (source fixture)", ""])
    for name, info in (ctx.get("modules") or {}).items():
        applicable = info.get("applicable")
        lines.append(f"- **{name}**: {'applicable' if applicable else 'omitted/not applicable'}")
        if name == "lease_liability":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: lease_liability={avail.get('lease_liability')} "
                f"ambiguous={avail.get('ambiguous')}"
            )
        if name == "lease_rou":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: right_of_use_assets={avail.get('right_of_use_assets')} "
                f"ambiguous={avail.get('ambiguous')}"
            )
        if name == "ownership_attribution":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: available={avail.get('available')} "
                f"partial={avail.get('partial')} ambiguous={avail.get('ambiguous')}"
            )
        if name == "goodwill_intangibles":
            avail = info.get("availability") or {}
            lines.append(
                "  - availability: "
                f"goodwill={avail.get('goodwill')} "
                f"intangible_assets={avail.get('intangible_assets')} "
                f"goodwill_and_intangibles={avail.get('goodwill_and_intangibles')} "
                f"payments={avail.get('payments_for_intangible_assets')}"
            )
        if name == "deferred_tax":
            avail = info.get("availability") or {}
            lines.append(
                "  - availability: "
                f"deferred_tax_assets={avail.get('deferred_tax_assets')} "
                f"deferred_tax_liabilities={avail.get('deferred_tax_liabilities')} "
                f"ambiguous={avail.get('ambiguous')}"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Temporary Trainer/Answer Key artifacts are not committed.",
            "- Synthetic DEMO / cross-company surfaces remain unchanged.",
            "- Forecasting / valuation remain deferred.",
            "- Comparable diluted-WAS axis (financial-statement units): "
            "306.871785, 306.969624, 307.13887, 307.231804, 307.247804 "
            "(basis=split_adjusted; FY2021 factor=3; FY2022–FY2025 factor=1).",
            "- Raw extracted share facts and G7 conflicts preserved unchanged.",
            "",
        ]
    )
    BASELINE.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--standardized-json",
        type=Path,
        help="Generated standardized.json (default: benchmark reconciled fixture)",
    )
    parser.add_argument("--provenance-json", type=Path)
    parser.add_argument("--conflicts-json", type=Path)
    parser.add_argument("--trainer", type=Path, help="Persisted Trainer workbook")
    parser.add_argument("--answer-key", type=Path, help="Persisted Answer Key workbook")
    parser.add_argument(
        "--require-check-counts",
        action="store_true",
        help="Require pristine (0,0,491,491) and filled (491,0,0,491) Check counts",
    )
    parser.add_argument(
        "--verify-release-pair",
        action="store_true",
        help="Verify practice contract and structural parity on the persisted pair",
    )
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="Skip writing benchmark/fast_retailing/BASELINE.md",
    )
    args = parser.parse_args(argv)

    result = run_audit(
        standardized_json=args.standardized_json,
        provenance_json=args.provenance_json,
        conflicts_json=args.conflicts_json,
        trainer_path=args.trainer,
        answer_key_path=args.answer_key,
        require_check_counts=True if args.require_check_counts else None,
        verify_release_pair=args.verify_release_pair,
    )
    if not args.no_baseline:
        write_baseline(result)
        print(f"wrote {BASELINE.relative_to(ROOT)}")
    for stage in result["stages"]:
        print(f"{stage.stage}: {stage.status}")
        if stage.message:
            print(f"  {stage.message[:300]}")
        if stage.exception_type and stage.status == "fail":
            print(f"  {stage.exception_type}: {stage.message[:300]}")
    failed = any(s.status == "fail" for s in result["stages"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
