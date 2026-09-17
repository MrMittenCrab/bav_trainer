"""Training workbook generator — uses runtime SemanticMap as single source of truth."""

from __future__ import annotations

import shutil
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Border, Font, PatternFill

from ..engine.component_catalog import (
    CAPEX_COMPONENT_CATALOG,
    COMPONENT_CATALOG,
    DEFERRED_TAX_COMPONENT_CATALOG,
    FIXED_ASSET_COMPONENT_CATALOG,
    GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG,
    STORE_COUNT_COMPONENT_CATALOG,
    REVENUE_STORE_COMPONENT_CATALOG,
    COMPARABLE_SALES_COMPONENT_CATALOG,
    SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG,
    is_operating_kpi_source_identity,
    GOODWILL_INTANGIBLES_COMPONENT_CATALOG,
    LEASE_LIABILITY_COMPONENT_CATALOG,
    LEASE_REPAYMENT_COMPONENT_CATALOG,
    LEASE_ROU_COMPONENT_CATALOG,
    NORMALIZATION_COMPONENT_CATALOG,
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
    OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    PROFITABILITY_CHANGE_COMPONENT_CATALOG,
    PROFITABILITY_DRIVER_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
    ROE_ATTRIBUTION_COMPONENT_CATALOG,
    WORKING_CAPITAL_COMPONENT_CATALOG,
)
from ..engine.reference_model import (
    JUDGMENT_SHEET,
    NORMALIZATION_JUDGMENT_SHEET,
    ReferenceModelBuilder,
)
from ..engine.semantic_map import ResolvedComponent, SemanticMap
from ..data.line_identity import validate_financials_identities
from ..ingestion.reconciler import reconcile_financials
from .check_context import CHECK_CONTEXT_SHEET
from .semantic_io import load_semantic_map, resolve_pair_paths

COMPONENT_MAP_SHEET = "_ComponentMap"
NOTE_AUTHOR = "BAV Trainer"
JUDGMENT_FIRST_DATA_ROW = 5
JUDGMENT_RESPONSE_COLS = (6, 7, 8)

_TRAINER_SIDECAR_SUFFIXES = (
    ".component_map.json",
    ".trainer.json",
    ".assumptions.json",
)


def remove_trainer_sidecars(trainer_path: Path) -> None:
    """Delete stale Trainer-only answer-bearing sidecars (idempotent)."""
    trainer_path = Path(trainer_path)
    for suffix in _TRAINER_SIDECAR_SUFFIXES:
        trainer_path.with_suffix(suffix).unlink(missing_ok=True)


PRACTICE_FILL = PatternFill("solid", start_color="FFFF00")
WHITE_FILL = PatternFill("solid", start_color="FFFFFF")

FONT_NAME = "Aptos Narrow"
BASE_FONT = Font(
    name=FONT_NAME,
    size=11,
    bold=False,
    italic=False,
    color="000000",
)
CLEAR_BORDER = Border()

_HIDDEN_PREFIX = "_"

TRAINER_INDEX_INSTRUCTION = (
    "Complete each historical model-construction and earnings-quality diagnostic "
    "formula schedule left-to-right in dependency order. "
    "Run Check to validate the yellow formula cells against the treatment currently "
    "selected in Accounting Judgment column F (blank F uses the supplied reference "
    "treatment). Generated Condensed Financials classification links are system-"
    "controlled and validated by Check—do not edit them or columns D:E. When "
    "Normalization Judgment is present, choose Recurring vs Non-recurring in column F "
    "(blank uses the supplied reference); Earnings Normalization formulas are checked "
    "against that choice. Also complete Accounting Judgment and Normalization Judgment "
    "rationale/consequence when cases are present; those responses are not graded by "
    "Check. Compare them with the matching Answer Key."
)


def _judgment_case_rows(ws):
    """Yield data rows that look like judgment cases (not the zero-case message)."""
    for row in range(JUDGMENT_FIRST_DATA_ROW, (ws.max_row or 0) + 1):
        order = ws.cell(row=row, column=1).value
        label = ws.cell(row=row, column=2).value
        if isinstance(order, int) and order >= 1 and label not in (None, ""):
            yield row


class TrainingWorkbookGenerator:
    """Generate a matched Trainer / Answer Key pair from a completed model."""

    def __init__(
        self,
        answer_key_path: Path,
        semantic_map: SemanticMap | None = None,
    ):
        self.answer_key_path = answer_key_path
        self.semantic_map = semantic_map or load_semantic_map(answer_key_path)

    def generate(self, trainer_path: Path) -> tuple[Path, Path]:
        """Finalize Answer Key in place, then derive a sanitized Trainer from it."""
        wb = load_workbook(self.answer_key_path)
        self._add_trainer_ui(wb)
        self._apply_minimal_style(wb)
        self._decorate_answer_key_practice_cells(wb)
        self._decorate_answer_key_judgment_cells(wb)
        self._decorate_answer_key_normalization_judgment_cells(wb)
        wb.save(self.answer_key_path)
        wb.close()

        shutil.copy2(self.answer_key_path, trainer_path)

        wb = load_workbook(trainer_path)
        self._blank_trainer_practice_cells(wb)
        self._blank_trainer_judgment_cells(wb)
        self._blank_trainer_normalization_judgment_cells(wb)
        self._sanitize_trainer_answer_stores(wb)
        wb.save(trainer_path)
        wb.close()

        # Prefer no Trainer semantic sidecar; Check reads the matching Answer Key.
        remove_trainer_sidecars(trainer_path)
        return trainer_path, self.answer_key_path

    def _visible_sheets(self, wb):
        return [
            ws
            for ws in wb.worksheets
            if not ws.title.startswith(_HIDDEN_PREFIX) and ws.sheet_state == "visible"
        ]

    def _apply_minimal_style(self, wb) -> None:
        """Normalize visible sheets to Aptos Narrow 11 with white fill and no borders."""
        for ws in self._visible_sheets(wb):
            ws.sheet_view.showGridLines = False
            max_row = ws.max_row or 1
            max_col = ws.max_column or 1
            for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
                for cell in row:
                    if (
                        cell.value is None
                        and cell.comment is None
                        and not cell.has_style
                    ):
                        continue
                    cell.font = BASE_FONT
                    cell.fill = WHITE_FILL
                    cell.border = CLEAR_BORDER

    def _decorate_answer_key_practice_cells(self, wb) -> None:
        for comp in self.semantic_map.all_ordered():
            if is_operating_kpi_source_identity(comp):
                continue
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            row, col = _cell_to_rc(comp.cell)
            cell = ws.cell(row=row, column=col)
            # Retain working formula/input and Note; ordinary white/no-fill
            cell.fill = WHITE_FILL
            hint = (comp.short_hint or "").strip()
            if not hint and comp.hints:
                hint = str(comp.hints[0]).strip()
            if not hint:
                hint = comp.title
            cell.comment = Comment(hint, NOTE_AUTHOR)

    def _blank_trainer_practice_cells(self, wb) -> None:
        for comp in self.semantic_map.all_ordered():
            if is_operating_kpi_source_identity(comp):
                continue
            if comp.tab not in wb.sheetnames:
                continue
            ws = wb[comp.tab]
            row, col = _cell_to_rc(comp.cell)
            cell = ws.cell(row=row, column=col)
            # Preserve font, border, alignment, protection, number format
            cell.value = None
            cell.fill = PRACTICE_FILL
            cell.comment = None

    def _decorate_answer_key_judgment_cells(self, wb) -> None:
        if JUDGMENT_SHEET not in wb.sheetnames:
            return
        ws = wb[JUDGMENT_SHEET]
        for row in _judgment_case_rows(ws):
            for col in JUDGMENT_RESPONSE_COLS:
                cell = ws.cell(row=row, column=col)
                cell.fill = WHITE_FILL

    def _decorate_answer_key_normalization_judgment_cells(self, wb) -> None:
        if NORMALIZATION_JUDGMENT_SHEET not in wb.sheetnames:
            return
        ws = wb[NORMALIZATION_JUDGMENT_SHEET]
        for row in _judgment_case_rows(ws):
            for col in JUDGMENT_RESPONSE_COLS:
                cell = ws.cell(row=row, column=col)
                cell.fill = WHITE_FILL

    def _blank_trainer_judgment_cells(self, wb) -> None:
        if JUDGMENT_SHEET not in wb.sheetnames:
            return
        ws = wb[JUDGMENT_SHEET]
        for row in _judgment_case_rows(ws):
            for col in JUDGMENT_RESPONSE_COLS:
                cell = ws.cell(row=row, column=col)
                cell.value = None
                cell.fill = PRACTICE_FILL
                cell.comment = None

    def _blank_trainer_normalization_judgment_cells(self, wb) -> None:
        if NORMALIZATION_JUDGMENT_SHEET not in wb.sheetnames:
            return
        ws = wb[NORMALIZATION_JUDGMENT_SHEET]
        for row in _judgment_case_rows(ws):
            for col in JUDGMENT_RESPONSE_COLS:
                cell = ws.cell(row=row, column=col)
                cell.value = None
                cell.fill = PRACTICE_FILL
                cell.comment = None

    def _sanitize_trainer_answer_stores(self, wb) -> None:
        """Remove answer-bearing hidden sheets from the Trainer only."""
        for name in (
            COMPONENT_MAP_SHEET,
            CHECK_CONTEXT_SHEET,
            "_RefFormulas",
            "_RefValues",
            "_TrainerMeta",
        ):
            if name in wb.sheetnames:
                del wb[name]

    def _add_trainer_ui(self, wb) -> None:
        if "Trainer" in wb.sheetnames:
            del wb["Trainer"]
        ws = wb.create_sheet("Trainer", 0)
        ws.sheet_view.showGridLines = False
        ws["A1"] = "BAV Excel Trainer"
        ws["A2"] = TRAINER_INDEX_INSTRUCTION
        headers = ["Order", "Schedule", "Period scope", "Tab", "Practice cells", "Depends on"]
        for j, h in enumerate(headers, start=1):
            ws.cell(row=4, column=j, value=h)
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 36
        ws.column_dimensions["C"].width = 22
        ws.column_dimensions["D"].width = 22
        ws.column_dimensions["E"].width = 28
        ws.column_dimensions["F"].width = 28

        for i, group in enumerate(group_components_by_family(self.semantic_map), start=5):
            ws.cell(row=i, column=1, value=group["family_order"])
            ws.cell(row=i, column=2, value=group["title"])
            ws.cell(row=i, column=3, value=group["period_scope"])
            ws.cell(row=i, column=4, value=group["tab"])
            ws.cell(row=i, column=5, value=group["practice_cells"])
            ws.cell(row=i, column=6, value=group["depends_on"])


def group_components_by_family(smap: SemanticMap) -> list[dict]:
    """Group concrete ResolvedComponents into conceptual schedule rows."""
    by_family: dict[str, list[ResolvedComponent]] = {}
    for comp in smap.all_ordered():
        by_family.setdefault(comp.family_id or comp.id, []).append(comp)

    family_meta = {f.id: f for f in COMPONENT_CATALOG}
    family_meta.update({f.id: f for f in NORMALIZATION_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in QUALITY_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in QUALITY_CHANGE_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in WORKING_CAPITAL_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in PROFITABILITY_DRIVER_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in PROFITABILITY_CHANGE_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in ROE_ATTRIBUTION_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in PER_SHARE_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in NORMALIZED_PER_SHARE_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in FIXED_ASSET_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in LEASE_LIABILITY_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in LEASE_ROU_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in GOODWILL_INTANGIBLES_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in DEFERRED_TAX_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in CAPEX_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in LEASE_REPAYMENT_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in STORE_COUNT_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in REVENUE_STORE_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in COMPARABLE_SALES_COMPONENT_CATALOG})
    family_meta.update({f.id: f for f in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG})
    groups: list[dict] = []
    for family_id, comps in by_family.items():
        comps = [c for c in comps if not is_operating_kpi_source_identity(c)]
        if not comps:
            continue
        comps = sorted(comps, key=lambda c: (c.period_index is None, c.period_index or 0, c.order))
        first = comps[0]
        family = family_meta.get(family_id)
        ends = [c.period_end for c in comps if c.period_end]
        if ends:
            year_span = _period_scope_label(ends, len(comps))
        else:
            year_span = f"{len(comps)} cells"
        dep_ids: list[str] = []
        if family is not None:
            for dep in family.depends_on_current + family.depends_on_previous:
                if dep not in dep_ids:
                    dep_ids.append(dep)
        else:
            for dep in first.depends_on:
                fam = dep.split("__", 1)[0]
                if fam not in dep_ids:
                    dep_ids.append(fam)
        groups.append(
            {
                "family_id": family_id,
                "family_order": first.family_order or first.order,
                "title": first.title,
                "period_scope": year_span,
                "tab": first.tab,
                "practice_cells": _format_practice_cells(comps),
                "depends_on": ", ".join(dep_ids) if dep_ids else "—",
                "count": len(comps),
                "components": comps,
            }
        )
    groups.sort(key=lambda g: g["family_order"])
    return groups


def _period_scope_label(period_ends: list[str], count: int) -> str:
    years = []
    for end in period_ends:
        years.append(end[:4] if len(end) >= 4 else end)
    if len(years) == 1:
        return f"{years[0]} ({count} cells)"
    return f"{years[0]}–{years[-1]} ({count} cells)"


def _format_practice_cells(comps: list[ResolvedComponent]) -> str:
    from openpyxl.utils import column_index_from_string, get_column_letter

    if not comps:
        return "—"
    cells = [c.cell for c in comps]
    if len(cells) == 1:
        return cells[0]

    parsed = []
    for cell in cells:
        col = "".join(ch for ch in cell if ch.isalpha())
        row = int("".join(ch for ch in cell if ch.isdigit()))
        parsed.append((row, column_index_from_string(col), cell))

    rows = {p[0] for p in parsed}
    if len(rows) == 1:
        cols = sorted(p[1] for p in parsed)
        if cols == list(range(cols[0], cols[0] + len(cols))):
            row = next(iter(rows))
            start = f"{get_column_letter(cols[0])}{row}"
            end = f"{get_column_letter(cols[-1])}{row}"
            return f"{start}:{end}"
    return ", ".join(cells)

def _cell_to_rc(cell_ref: str) -> tuple[int, int]:
    from openpyxl.utils import column_index_from_string

    col = "".join(c for c in cell_ref if c.isalpha())
    row = int("".join(c for c in cell_ref if c.isdigit()))
    return row, column_index_from_string(col)


def build_training_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
) -> tuple[Path, Path]:
    """End-to-end: standardized data → Answer Key + Trainer workbook pair.

    Returns ``(trainer_path, answer_key_path)``.
    """
    validate_financials_identities(financials)

    report = reconcile_financials(financials)
    failed = [name for name, ok in report.checksums.items() if ok is False]
    if failed:
        details = "; ".join(failed)
        warnings = "; ".join(report.warnings) if report.warnings else details
        raise ValueError(
            f"Source statement checksum failed ({details}). "
            f"Refuse Trainer / Answer Key build. {warnings}"
        )

    trainer_path, answer_key_path = resolve_pair_paths(output_path)
    remove_trainer_sidecars(trainer_path)
    builder = ReferenceModelBuilder(financials, assumptions)
    semantic_map = builder.build(answer_key_path)
    TrainingWorkbookGenerator(
        answer_key_path,
        semantic_map,
    ).generate(trainer_path)
    remove_trainer_sidecars(trainer_path)
    return trainer_path, answer_key_path
