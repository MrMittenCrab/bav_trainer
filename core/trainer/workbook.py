"""Training workbook generator — uses runtime SemanticMap as single source of truth."""

from __future__ import annotations

import shutil
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill

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
    REVENUE_DRIVER_COMPONENT_CATALOG,
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
from .semantic_io import company_stem_from_output, load_semantic_map, resolve_pair_paths

COMPONENT_MAP_SHEET = "_ComponentMap"
NOTE_AUTHOR = "BAV"
JUDGMENT_FIRST_DATA_ROW = 5
JUDGMENT_RESPONSE_COLS = (6, 7, 8)
BAV_OPENING_SHEET = "Overview"
_SELECTED_FALLBACK_SCHEDULES = (
    "Income Statement",
    "Balance Sheet",
    "Cash Flow Statement",
    "Condensed Financials",
    "ALT DuPont",
    "Geographic Segment Analysis",
    "Store Count Analysis",
    "Revenue Driver Analysis",
)

_TRAINER_SIDECAR_SUFFIXES = (
    ".component_map.json",
    ".trainer.json",
    ".assumptions.json",
)


def _is_primary_bav_path(path: Path) -> bool:
    stem = Path(path).stem
    return stem.endswith("_BAV") and not stem.endswith("_BAV_Trainer")


def remove_trainer_sidecars(trainer_path: Path) -> None:
    """Delete stale Trainer-only answer-bearing sidecars (idempotent)."""
    trainer_path = Path(trainer_path)
    if _is_primary_bav_path(trainer_path):
        return
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
    "Check. Compare them with the matching BAV."
)


def _judgment_case_rows(ws):
    """Yield data rows that look like judgment cases (not the zero-case message)."""
    for row in range(JUDGMENT_FIRST_DATA_ROW, (ws.max_row or 0) + 1):
        order = ws.cell(row=row, column=1).value
        label = ws.cell(row=row, column=2).value
        if isinstance(order, int) and order >= 1 and label not in (None, ""):
            yield row


class TrainingWorkbookGenerator:
    """Finalize a professional BAV and optionally derive a sanitized Trainer."""

    def __init__(
        self,
        answer_key_path: Path,
        semantic_map: SemanticMap | None = None,
        financials=None,
    ):
        self.answer_key_path = Path(answer_key_path)
        self.bav_path = self.answer_key_path
        self.semantic_map = semantic_map or load_semantic_map(self.bav_path)
        self.financials = financials

    def finalize_bav(self) -> Path:
        """Write formulas, Notes, opening and metadata into the BAV only."""
        if self.financials is None:
            self.financials = self._financials_for_opening()
        wb = load_workbook(self.bav_path)
        self._add_bav_opening(wb)
        from ..build_status import add_build_status
        add_build_status(wb, self.semantic_map)
        self._apply_minimal_style(wb)
        self._decorate_answer_key_practice_cells(wb)
        self._decorate_answer_key_judgment_cells(wb)
        self._decorate_answer_key_normalization_judgment_cells(wb)
        wb.save(self.bav_path)
        wb.close()
        return self.bav_path

    def derive_trainer(self, trainer_path: Path) -> Path:
        """Copy the finalized BAV and sanitize a Trainer without mutating the BAV."""
        trainer_path = Path(trainer_path)
        shutil.copy2(self.bav_path, trainer_path)
        wb = load_workbook(trainer_path)
        self._add_trainer_ui(wb)
        self._apply_minimal_style(wb)
        self._blank_trainer_practice_cells(wb)
        self._blank_trainer_judgment_cells(wb)
        self._blank_trainer_normalization_judgment_cells(wb)
        self._sanitize_trainer_answer_stores(wb)
        wb.save(trainer_path)
        wb.close()
        remove_trainer_sidecars(trainer_path)
        return trainer_path

    def generate(self, trainer_path: Path) -> tuple[Path, Path]:
        """Finalize the BAV, then derive a sanitized Trainer from that completed model."""
        self.finalize_bav()
        self.derive_trainer(trainer_path)
        return trainer_path, self.bav_path

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

    def _financials_for_opening(self):
        if self.financials is not None:
            return self.financials
        from .check_context import load_check_context
        from ..data.standardized_io import standardized_from_payload

        return standardized_from_payload(load_check_context(self.bav_path).source_payload)

    def _add_bav_opening(self, wb) -> None:
        """Professional cover: identity, source-backed interpretation, navigation."""
        for name in (BAV_OPENING_SHEET, "Trainer"):
            if name in wb.sheetnames:
                del wb[name]
        fin = self._financials_for_opening()
        periods = list(fin.periods or [])
        labels = []
        for period in periods:
            label = (getattr(period, "label", None) or "").strip()
            end = getattr(period, "end_date", None)
            if label:
                labels.append(label)
            elif end is not None:
                labels.append(end.isoformat() if hasattr(end, "isoformat") else str(end))
        if labels:
            coverage = (
                labels[0]
                if len(labels) == 1
                else f"{labels[0]} – {labels[-1]} ({len(labels)} periods)"
            )
        else:
            coverage = "No admitted historical periods"
        company = (fin.company_name or fin.ticker or "Company").strip()
        ticker = (fin.ticker or "").strip()
        identity = f"{company} ({ticker})" if ticker and ticker.casefold() != company.casefold() else company
        currency = (fin.currency or "").strip() or "unspecified currency"
        units = (fin.units or "").strip() or "unspecified units"
        structure = [
            title
            for title in wb.sheetnames
            if not title.startswith(_HIDDEN_PREFIX)
            and title != "Build Status"
            and wb[title].sheet_state == "visible"
        ]
        from ..model.revenue_strategy_synthesis import (
            PROFESSIONAL_FALLBACK,
            compute_historical_strategy_synthesis,
            strategy_synthesis_applicable,
        )

        ws = wb.create_sheet(BAV_OPENING_SHEET, 0)
        ws.sheet_view.showGridLines = False
        wrap = Alignment(wrap_text=True, vertical="top")
        label_width = 28.0
        narrative_width = 88.0
        ws.column_dimensions["A"].width = label_width
        ws.column_dimensions["B"].width = narrative_width

        def _wrapped_height(text: str, *, width: float) -> float:
            chars_per_line = max(24, int(width * 0.9))
            paragraphs = str(text or "").splitlines() or [""]
            lines = 0
            for paragraph in paragraphs:
                length = max(len(paragraph), 1)
                lines += max(1, (length + chars_per_line - 1) // chars_per_line)
            return max(18.0, 15.0 * lines + 8.0)

        def _raise_row(row: int, height: float) -> None:
            current = ws.row_dimensions[row].height
            ws.row_dimensions[row].height = max(float(current or 0), height)

        def _write(row: int, column: int, text: str, *, width: float) -> None:
            cell = ws.cell(row=row, column=column, value=text)
            cell.alignment = wrap
            if text:
                _raise_row(row, _wrapped_height(text, width=width))

        def _label(row: int, text: str) -> None:
            _write(row, 1, text, width=label_width)

        def _narrative(row: int, text: str) -> None:
            _write(row, 2, text, width=narrative_width)
            label = ws.cell(row=row, column=1).value
            if isinstance(label, str) and label:
                _raise_row(row, _wrapped_height(label, width=label_width))

        def _wide(row: int, text: str) -> None:
            cell = ws.cell(row=row, column=1, value=text)
            cell.alignment = wrap
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
            _raise_row(row, _wrapped_height(text, width=label_width + narrative_width))

        _wide(1, "BAV")
        _wide(2, identity)
        _wide(3, f"Historical coverage: {coverage}")
        _wide(4, f"Units: {currency}; {units}")

        cursor = 6
        navigation: list[str] = []
        if strategy_synthesis_applicable(fin):
            synthesis = compute_historical_strategy_synthesis(fin)
            _label(cursor, "Historical reading")
            _narrative(cursor, synthesis.lead)
            cursor += 2
            limits = " ".join(
                part
                for part in (
                    synthesis.limits,
                    synthesis.productivity_gap,
                    synthesis.untested,
                )
                if part
            )
            _label(cursor, "Evidence limits")
            _narrative(cursor, limits)
            cursor += 2
            navigation = [
                name for name in synthesis.navigation if name in structure
            ]
        else:
            _label(cursor, "Historical reading")
            _narrative(cursor, PROFESSIONAL_FALLBACK)
            cursor += 2

        if not navigation:
            navigation = [
                name for name in _SELECTED_FALLBACK_SCHEDULES if name in structure
            ]
        if not navigation:
            navigation = list(structure)[:8]
        _wide(cursor, "Supporting schedules")
        cursor += 1
        for name in navigation:
            cell = ws.cell(row=cursor, column=1, value=name)
            cell.alignment = wrap
            if name in wb.sheetnames:
                cell.hyperlink = f"#'{name}'!A1"
            cursor += 1
        cell = ws.cell(row=cursor, column=1, value="Build Status")
        cell.alignment = wrap
        cell.hyperlink = "#'Build Status'!A1"

    def _add_trainer_ui(self, wb) -> None:
        if "Trainer" in wb.sheetnames:
            del wb["Trainer"]
        ws = wb.create_sheet("Trainer", 0)
        ws.sheet_view.showGridLines = False
        ws["A1"] = "BAV Excel Trainer"
        ws["A2"] = TRAINER_INDEX_INSTRUCTION
        if "Build Status" in wb.sheetnames:
            ws["G1"] = "Current Progress"
            ws["G1"].hyperlink = "#'Build Status'!A1"
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
    family_meta.update({f.id: f for f in REVENUE_DRIVER_COMPONENT_CATALOG})
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


def build_bav_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
    *,
    current_snapshot: bool = False,
) -> Path:
    """End-to-end: standardized data → professional BAV. Does not derive a Trainer."""
    validate_financials_identities(financials)

    report = reconcile_financials(financials)
    failed = [name for name, ok in report.checksums.items() if ok is False]
    if failed:
        details = "; ".join(failed)
        warnings = "; ".join(report.warnings) if report.warnings else details
        raise ValueError(
            f"Source statement checksum failed ({details}). "
            f"Refuse BAV build. {warnings}"
        )

    _, bav_path = resolve_pair_paths(output_path)
    builder = ReferenceModelBuilder(financials, assumptions, current_snapshot=current_snapshot)
    semantic_map = builder.build(bav_path)
    TrainingWorkbookGenerator(
        bav_path,
        semantic_map,
        financials=financials,
    ).finalize_bav()
    return bav_path


def derive_trainer_workbook(bav_path: Path, trainer_path: Path | None = None) -> Path:
    """Derive a Trainer from a completed BAV without mutating the BAV."""
    bav_path = Path(bav_path)
    if trainer_path is None:
        trainer_path, _ = resolve_pair_paths(bav_path)
    generator = TrainingWorkbookGenerator(bav_path)
    return generator.derive_trainer(trainer_path)


def build_training_workbook(
    financials,
    output_path: Path,
    assumptions: dict | None = None,
    *,
    current_snapshot: bool = False,
) -> tuple[Path, Path]:
    """Existing interface: professional BAV plus optional Trainer derivation.

    Returns ``(trainer_path, bav_path)``.
    """
    bav_path = build_bav_workbook(
        financials,
        output_path,
        assumptions,
        current_snapshot=current_snapshot,
    )
    trainer_path, resolved_bav = resolve_pair_paths(output_path)
    output_path = Path(output_path)
    company = company_stem_from_output(output_path.stem)
    suffix = output_path.suffix or ".xlsx"
    protected = {bav_path.resolve(), resolved_bav.resolve()}
    for stale in (
        trainer_path,
        output_path,
        output_path.with_name(f"{company}_Trainer{suffix}"),
        output_path.with_name(f"{company}_BAV_Trainer{suffix}"),
    ):
        if stale.resolve() in protected:
            continue
        remove_trainer_sidecars(stale)
    derive_trainer_workbook(bav_path, trainer_path)
    return trainer_path, bav_path
