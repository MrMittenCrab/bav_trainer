"""Answer-Key Check context: source facts, setup overrides, and judgment bindings."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

from ..data.interface import StandardizedFinancials
from ..data.standardized_io import standardized_to_payload
from ..model.judgment import JudgmentCase
from ..model.normalization import NormalizationCase

CHECK_CONTEXT_SHEET = "_CheckContext"
CHECK_CONTEXT_MAGIC = "BAV_CHECK_CONTEXT_V1"
CHECK_CONTEXT_CHUNK_SIZE = 30000
CHECK_CONTEXT_SCHEMA_VERSION = 2
CHECK_CONTEXT_LEGACY_SCHEMA_VERSION = 1

JUDGMENT_SHEET = "Accounting Judgment"
NORMALIZATION_JUDGMENT_SHEET = "Normalization Judgment"
EARNINGS_NORMALIZATION_SHEET = "Earnings Normalization"


@dataclass(frozen=True)
class JudgmentBinding:
    order: int
    worksheet_row: int
    case_id: str
    line_identity: str
    override_selector: str
    reference_treatment: str
    allowed_treatments: tuple[str, ...]


@dataclass(frozen=True)
class NormalizationBinding:
    order: int
    worksheet_row: int
    case_id: str
    line_identity: str
    source_selector: str
    scope: str
    reference_treatment: str
    allowed_treatments: tuple[str, ...]


@dataclass(frozen=True)
class CheckContext:
    schema_version: int
    source_payload: dict
    modeled_periods: tuple[str, ...]
    base_classification_overrides: dict[str, str]
    judgment_bindings: tuple[JudgmentBinding, ...]
    normalization_bindings: tuple[NormalizationBinding, ...] = ()


def live_classification_formula(
    judgment_row: int,
    reference_treatment: str,
) -> str:
    """System-generated Condensed classification formula driven only by Judgment!F."""
    if judgment_row < 1:
        raise ValueError(f"judgment_row must be >= 1, got {judgment_row}")
    if reference_treatment is None or not str(reference_treatment).strip():
        raise ValueError("reference_treatment must be a non-empty category string")
    escaped = str(reference_treatment).replace('"', '""')
    return (
        f"=IF('{JUDGMENT_SHEET}'!$F${judgment_row}=\"\","
        f"\"{escaped}\","
        f"'{JUDGMENT_SHEET}'!$F${judgment_row})"
    )


def live_normalization_treatment_formula(
    judgment_row: int,
    reference_treatment: str,
) -> str:
    """System-generated Earnings Normalization treatment formula driven only by F."""
    if judgment_row < 1:
        raise ValueError(f"judgment_row must be >= 1, got {judgment_row}")
    if reference_treatment is None or not str(reference_treatment).strip():
        raise ValueError("reference_treatment must be a non-empty treatment string")
    escaped = str(reference_treatment).replace('"', '""')
    return (
        f"=IF('{NORMALIZATION_JUDGMENT_SHEET}'!$F${judgment_row}=\"\","
        f"\"{escaped}\","
        f"'{NORMALIZATION_JUDGMENT_SHEET}'!$F${judgment_row})"
    )


def build_check_context(
    financials: StandardizedFinancials,
    periods: list[date],
    assumptions: dict,
    judgment_cases: tuple[JudgmentCase, ...],
    normalization_cases: tuple[NormalizationCase, ...] = (),
) -> CheckContext:
    """Build a non-answer-bearing context sufficient to recompute expecteds."""
    overrides = dict(assumptions.get("classificationOverrides") or {})
    bindings = tuple(
        JudgmentBinding(
            order=case.order,
            worksheet_row=4 + case.order,
            case_id=case.id,
            line_identity=case.line_identity,
            override_selector=case.override_selector,
            reference_treatment=case.supplied_treatment,
            allowed_treatments=(case.supplied_treatment,) + case.alternatives,
        )
        for case in judgment_cases
    )
    norm_bindings = tuple(
        NormalizationBinding(
            order=case.order,
            worksheet_row=4 + case.order,
            case_id=case.id,
            line_identity=case.line_identity,
            source_selector=case.override_selector,
            scope=case.scope,
            reference_treatment=case.reference_treatment,
            allowed_treatments=(case.reference_treatment,) + case.alternatives,
        )
        for case in normalization_cases
    )
    return CheckContext(
        schema_version=CHECK_CONTEXT_SCHEMA_VERSION,
        source_payload=standardized_to_payload(financials),
        modeled_periods=tuple(period.isoformat() for period in periods),
        base_classification_overrides=overrides,
        judgment_bindings=bindings,
        normalization_bindings=norm_bindings,
    )


def _context_to_json(context: CheckContext) -> str:
    payload = {
        "schema_version": context.schema_version,
        "source_payload": context.source_payload,
        "modeled_periods": list(context.modeled_periods),
        "base_classification_overrides": dict(context.base_classification_overrides),
        "judgment_bindings": [
            {
                **asdict(binding),
                "allowed_treatments": list(binding.allowed_treatments),
            }
            for binding in context.judgment_bindings
        ],
        "normalization_bindings": [
            {
                **asdict(binding),
                "allowed_treatments": list(binding.allowed_treatments),
            }
            for binding in context.normalization_bindings
        ],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def embed_check_context_sheet(wb: Workbook, context: CheckContext) -> None:
    """Embed versioned Check context JSON on a hidden Answer-Key-only sheet."""
    if CHECK_CONTEXT_SHEET in wb.sheetnames:
        del wb[CHECK_CONTEXT_SHEET]
    ws = wb.create_sheet(CHECK_CONTEXT_SHEET)
    ws.sheet_state = "hidden"
    ws["A1"] = CHECK_CONTEXT_MAGIC
    blob = _context_to_json(context)
    if not blob:
        raise ValueError("Check context JSON is empty")
    row = 2
    for start in range(0, len(blob), CHECK_CONTEXT_CHUNK_SIZE):
        ws.cell(row=row, column=1, value=blob[start : start + CHECK_CONTEXT_CHUNK_SIZE])
        row += 1


def _parse_judgment_bindings(raw: Any) -> tuple[JudgmentBinding, ...]:
    if not isinstance(raw, list):
        raise ValueError("Check context judgment_bindings must be a list")
    bindings: list[JudgmentBinding] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError("Check context judgment binding must be an object")
        allowed = entry.get("allowed_treatments")
        if not isinstance(allowed, list) or not allowed:
            raise ValueError("Check context allowed_treatments must be a non-empty list")
        bindings.append(
            JudgmentBinding(
                order=int(entry["order"]),
                worksheet_row=int(entry["worksheet_row"]),
                case_id=str(entry["case_id"]),
                line_identity=str(entry["line_identity"]),
                override_selector=str(entry["override_selector"]),
                reference_treatment=str(entry["reference_treatment"]),
                allowed_treatments=tuple(str(item) for item in allowed),
            )
        )
    return tuple(bindings)


def _parse_normalization_bindings(raw: Any) -> tuple[NormalizationBinding, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ValueError("Check context normalization_bindings must be a list")
    bindings: list[NormalizationBinding] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError("Check context normalization binding must be an object")
        allowed = entry.get("allowed_treatments")
        if not isinstance(allowed, list) or not allowed:
            raise ValueError(
                "Check context normalization allowed_treatments must be a non-empty list"
            )
        bindings.append(
            NormalizationBinding(
                order=int(entry["order"]),
                worksheet_row=int(entry["worksheet_row"]),
                case_id=str(entry["case_id"]),
                line_identity=str(entry["line_identity"]),
                source_selector=str(entry["source_selector"]),
                scope=str(entry["scope"]),
                reference_treatment=str(entry["reference_treatment"]),
                allowed_treatments=tuple(str(item) for item in allowed),
            )
        )
    return tuple(bindings)


def _parse_context_payload(payload: dict[str, Any]) -> CheckContext:
    schema_version = int(payload.get("schema_version") or 0)
    if schema_version not in {
        CHECK_CONTEXT_LEGACY_SCHEMA_VERSION,
        CHECK_CONTEXT_SCHEMA_VERSION,
    }:
        raise ValueError(
            f"Unsupported Check context schema_version {schema_version!r}; "
            f"expected {CHECK_CONTEXT_LEGACY_SCHEMA_VERSION} or {CHECK_CONTEXT_SCHEMA_VERSION}"
        )
    source_payload = payload.get("source_payload")
    if not isinstance(source_payload, dict):
        raise ValueError("Check context source_payload must be an object")
    modeled = payload.get("modeled_periods")
    if not isinstance(modeled, list):
        raise ValueError("Check context modeled_periods must be a list")
    overrides = payload.get("base_classification_overrides")
    if not isinstance(overrides, dict):
        raise ValueError("Check context base_classification_overrides must be an object")
    norm_bindings = ()
    if schema_version >= CHECK_CONTEXT_SCHEMA_VERSION:
        norm_bindings = _parse_normalization_bindings(payload.get("normalization_bindings"))
    elif "normalization_bindings" in payload and payload.get("normalization_bindings"):
        raise ValueError("schema v1 Check context must not carry normalization_bindings")
    return CheckContext(
        schema_version=schema_version,
        source_payload=source_payload,
        modeled_periods=tuple(str(item) for item in modeled),
        base_classification_overrides={str(k): str(v) for k, v in overrides.items()},
        judgment_bindings=_parse_judgment_bindings(payload.get("judgment_bindings")),
        normalization_bindings=norm_bindings,
    )


def load_check_context(answer_key_path: Path) -> CheckContext | None:
    """Load Check context from Answer Key. Missing sheet => None (legacy)."""
    answer_key_path = Path(answer_key_path)
    wb = load_workbook(answer_key_path, data_only=False)
    try:
        if CHECK_CONTEXT_SHEET not in wb.sheetnames:
            return None
        ws = wb[CHECK_CONTEXT_SHEET]
        magic = ws["A1"].value
        if magic != CHECK_CONTEXT_MAGIC:
            raise ValueError(
                f"Malformed Check context magic {magic!r}; expected {CHECK_CONTEXT_MAGIC!r}"
            )
        chunks: list[str] = []
        row = 2
        while True:
            value = ws.cell(row=row, column=1).value
            if value is None or value == "":
                break
            if not isinstance(value, str):
                raise ValueError(
                    f"Check context chunk at A{row} must be text, got {type(value).__name__}"
                )
            chunks.append(value)
            row += 1
        if not chunks:
            raise ValueError("Check context sheet has magic but no JSON payload")
        try:
            payload = json.loads("".join(chunks))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed Check context JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError("Check context JSON root must be an object")
        return _parse_context_payload(payload)
    finally:
        wb.close()


def _validated_treatment_selection(
    selected,
    *,
    reference_treatment: str,
    allowed_treatments: tuple[str, ...],
    sheet_name: str,
    row: int,
) -> str:
    """Map judgment column F to a treatment; exact allowed string or blank only."""
    if selected is None or selected == "":
        return reference_treatment

    if not isinstance(selected, str):
        raise ValueError(
            f"Invalid treatment value on {sheet_name} row {row}: "
            f"expected one of {list(allowed_treatments)}"
        )

    if selected != selected.strip():
        raise ValueError(
            f"Treatment contains surrounding whitespace on {sheet_name} row {row}"
        )

    if selected not in allowed_treatments:
        raise ValueError(
            f"Invalid treatment {selected!r} on {sheet_name} row {row}; "
            f"allowed: {list(allowed_treatments)}"
        )

    return selected


def classification_overrides_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    """Merge base overrides with current Accounting Judgment treatment selections."""
    if JUDGMENT_SHEET not in trainer_wb.sheetnames:
        raise ValueError("Trainer is missing Accounting Judgment sheet required for Check")
    overrides = dict(context.base_classification_overrides)
    ws = trainer_wb[JUDGMENT_SHEET]
    for binding in context.judgment_bindings:
        selected = ws.cell(row=binding.worksheet_row, column=6).value
        treatment = _validated_treatment_selection(
            selected,
            reference_treatment=binding.reference_treatment,
            allowed_treatments=binding.allowed_treatments,
            sheet_name=JUDGMENT_SHEET,
            row=binding.worksheet_row,
        )
        overrides[binding.override_selector] = treatment
    return overrides


def normalization_treatments_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    """Read Normalization Judgment!F selections keyed by case id."""
    if not context.normalization_bindings:
        return {}
    if NORMALIZATION_JUDGMENT_SHEET not in trainer_wb.sheetnames:
        raise ValueError(
            "Trainer is missing Normalization Judgment sheet required for Check"
        )
    ws = trainer_wb[NORMALIZATION_JUDGMENT_SHEET]
    treatments: dict[str, str] = {}
    for binding in context.normalization_bindings:
        selected = ws.cell(row=binding.worksheet_row, column=6).value
        treatments[binding.case_id] = _validated_treatment_selection(
            selected,
            reference_treatment=binding.reference_treatment,
            allowed_treatments=binding.allowed_treatments,
            sheet_name=NORMALIZATION_JUDGMENT_SHEET,
            row=binding.worksheet_row,
        )
    return treatments


def _find_column_b_matches(ws, expected_formula: str) -> list[tuple[int, int]]:
    matches: list[tuple[int, int]] = []
    for row in range(1, (ws.max_row or 0) + 1):
        if ws.cell(row=row, column=2).value == expected_formula:
            matches.append((row, 2))
    return matches


def _judgment_editable_cells(bindings) -> set[str]:
    """F:G:H on numbered judgment case rows from Check bindings."""
    cells: set[str] = set()
    for binding in bindings:
        row = binding.worksheet_row
        for col in (6, 7, 8):
            cells.add(f"{get_column_letter(col)}{row}")
    return cells


def _validate_trusted_sheet_cells(
    trainer_ws,
    answer_ws,
    *,
    sheet_name: str,
    editable_cells: set[str],
) -> None:
    """Require Trainer contents to match Answer Key outside learner-editable cells."""
    max_row = max(trainer_ws.max_row or 0, answer_ws.max_row or 0)
    max_col = max(trainer_ws.max_column or 0, answer_ws.max_column or 0)
    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            coord = f"{get_column_letter(col)}{row}"
            if coord in editable_cells:
                continue
            trainer_value = trainer_ws.cell(row=row, column=col).value
            answer_value = answer_ws.cell(row=row, column=col).value
            if trainer_value != answer_value:
                raise ValueError(
                    f"Trusted workbook cell was modified: {sheet_name}!{coord}"
                )


def validate_live_judgment_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
) -> None:
    """Compatibility wrapper for classification live-link validation only.

    Full trusted-sheet validation requires ``practice_cells`` from Check.
    """
    validate_live_model_structure(trainer_wb, answer_key_wb, context)


def validate_live_model_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
    *,
    practice_cells: set[tuple[str, str]] | None = None,
) -> None:
    """Fail fast if trusted source/setup/model cells or live links were modified.

    When ``practice_cells`` is None, only binding/live-link checks run (compatibility).
    When provided (including empty), full trusted-sheet content validation runs.
    """
    run_trusted_sheets = practice_cells is not None
    practice_cells = practice_cells or set()

    for wb, label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
        if JUDGMENT_SHEET not in wb.sheetnames:
            raise ValueError(f"{label} is missing Accounting Judgment sheet")
        if "Condensed Financials" not in wb.sheetnames:
            raise ValueError(f"{label} is missing Condensed Financials sheet")
        if run_trusted_sheets:
            if "ALT DuPont" not in wb.sheetnames:
                raise ValueError(f"{label} is missing ALT DuPont sheet")
            for sheet in ("Income Statement", "Balance Sheet", "Cash Flow Statement"):
                if sheet not in wb.sheetnames:
                    raise ValueError(f"{label} is missing {sheet} sheet")

    for binding in context.judgment_bindings:
        row = binding.worksheet_row
        expected_alts = ", ".join(binding.allowed_treatments[1:])
        for wb, _label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
            if wb[JUDGMENT_SHEET].cell(row=row, column=4).value != binding.reference_treatment:
                raise ValueError(
                    f"Accounting Judgment reference prompt was modified on row {row}"
                )
            if wb[JUDGMENT_SHEET].cell(row=row, column=5).value != expected_alts:
                raise ValueError(
                    f"Accounting Judgment alternatives prompt was modified on row {row}"
                )
        expected_formula = live_classification_formula(
            binding.worksheet_row,
            binding.reference_treatment,
        )
        ak_matches = _find_column_b_matches(
            answer_key_wb["Condensed Financials"], expected_formula
        )
        if len(ak_matches) != 1:
            raise ValueError(
                "Answer Key live-classification binding is missing/ambiguous "
                f"for judgment row {row}"
            )
        link_row, link_col = ak_matches[0]
        if trainer_wb["Condensed Financials"].cell(row=link_row, column=link_col).value != expected_formula:
            coord = f"{get_column_letter(link_col)}{link_row}"
            raise ValueError(
                f"Linked Condensed Financials classification was modified at {coord}"
            )

    if context.normalization_bindings:
        for wb, label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
            if NORMALIZATION_JUDGMENT_SHEET not in wb.sheetnames:
                raise ValueError(f"{label} is missing Normalization Judgment sheet")
            if EARNINGS_NORMALIZATION_SHEET not in wb.sheetnames:
                raise ValueError(f"{label} is missing Earnings Normalization sheet")

        for binding in context.normalization_bindings:
            row = binding.worksheet_row
            expected_alts = ", ".join(binding.allowed_treatments[1:])
            for wb, _label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
                if (
                    wb[NORMALIZATION_JUDGMENT_SHEET].cell(row=row, column=4).value
                    != binding.reference_treatment
                ):
                    raise ValueError(
                        f"Normalization Judgment reference prompt was modified on row {row}"
                    )
                if (
                    wb[NORMALIZATION_JUDGMENT_SHEET].cell(row=row, column=5).value
                    != expected_alts
                ):
                    raise ValueError(
                        f"Normalization Judgment alternatives prompt was modified on row {row}"
                    )
            expected_formula = live_normalization_treatment_formula(
                binding.worksheet_row,
                binding.reference_treatment,
            )
            ak_matches = _find_column_b_matches(
                answer_key_wb[EARNINGS_NORMALIZATION_SHEET], expected_formula
            )
            if len(ak_matches) != 1:
                raise ValueError(
                    "Answer Key live-normalization binding is missing/ambiguous "
                    f"for judgment row {row}"
                )
            link_row, link_col = ak_matches[0]
            trainer_val = trainer_wb[EARNINGS_NORMALIZATION_SHEET].cell(
                row=link_row, column=link_col
            ).value
            if trainer_val != expected_formula:
                coord = f"{get_column_letter(link_col)}{link_row}"
                raise ValueError(
                    f"Linked Earnings Normalization treatment was modified at {coord}"
                )

    if not run_trusted_sheets:
        return

    for sheet_name in ("Income Statement", "Balance Sheet", "Cash Flow Statement"):
        _validate_trusted_sheet_cells(
            trainer_wb[sheet_name],
            answer_key_wb[sheet_name],
            sheet_name=sheet_name,
            editable_cells=set(),
        )

    _validate_trusted_sheet_cells(
        trainer_wb["Condensed Financials"],
        answer_key_wb["Condensed Financials"],
        sheet_name="Condensed Financials",
        editable_cells={
            cell for tab, cell in practice_cells if tab == "Condensed Financials"
        },
    )
    _validate_trusted_sheet_cells(
        trainer_wb["ALT DuPont"],
        answer_key_wb["ALT DuPont"],
        sheet_name="ALT DuPont",
        editable_cells={cell for tab, cell in practice_cells if tab == "ALT DuPont"},
    )

    if context.normalization_bindings:
        _validate_trusted_sheet_cells(
            trainer_wb[EARNINGS_NORMALIZATION_SHEET],
            answer_key_wb[EARNINGS_NORMALIZATION_SHEET],
            sheet_name=EARNINGS_NORMALIZATION_SHEET,
            editable_cells={
                cell
                for tab, cell in practice_cells
                if tab == EARNINGS_NORMALIZATION_SHEET
            },
        )

    _validate_trusted_sheet_cells(
        trainer_wb[JUDGMENT_SHEET],
        answer_key_wb[JUDGMENT_SHEET],
        sheet_name=JUDGMENT_SHEET,
        editable_cells=_judgment_editable_cells(context.judgment_bindings),
    )
    if context.normalization_bindings:
        _validate_trusted_sheet_cells(
            trainer_wb[NORMALIZATION_JUDGMENT_SHEET],
            answer_key_wb[NORMALIZATION_JUDGMENT_SHEET],
            sheet_name=NORMALIZATION_JUDGMENT_SHEET,
            editable_cells=_judgment_editable_cells(context.normalization_bindings),
        )
