"""Answer-Key Check context: source facts, setup overrides, and judgment bindings."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook

from ..data.interface import StandardizedFinancials
from ..data.standardized_io import standardized_to_payload
from ..model.judgment import JudgmentCase

CHECK_CONTEXT_SHEET = "_CheckContext"
CHECK_CONTEXT_MAGIC = "BAV_CHECK_CONTEXT_V1"
CHECK_CONTEXT_CHUNK_SIZE = 30000
CHECK_CONTEXT_SCHEMA_VERSION = 1


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
class CheckContext:
    schema_version: int
    source_payload: dict
    modeled_periods: tuple[str, ...]
    base_classification_overrides: dict[str, str]
    judgment_bindings: tuple[JudgmentBinding, ...]


def build_check_context(
    financials: StandardizedFinancials,
    periods: list[date],
    assumptions: dict,
    judgment_cases: tuple[JudgmentCase, ...],
) -> CheckContext:
    """Build a non-answer-bearing context sufficient to recompute historical expecteds."""
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
    return CheckContext(
        schema_version=CHECK_CONTEXT_SCHEMA_VERSION,
        source_payload=standardized_to_payload(financials),
        modeled_periods=tuple(period.isoformat() for period in periods),
        base_classification_overrides=overrides,
        judgment_bindings=bindings,
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


def _parse_context_payload(payload: dict[str, Any]) -> CheckContext:
    schema_version = int(payload.get("schema_version") or 0)
    if schema_version != CHECK_CONTEXT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported Check context schema_version {schema_version!r}; "
            f"expected {CHECK_CONTEXT_SCHEMA_VERSION}"
        )
    bindings_raw = payload.get("judgment_bindings")
    if not isinstance(bindings_raw, list):
        raise ValueError("Check context judgment_bindings must be a list")
    bindings: list[JudgmentBinding] = []
    for entry in bindings_raw:
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
    source_payload = payload.get("source_payload")
    if not isinstance(source_payload, dict):
        raise ValueError("Check context source_payload must be an object")
    modeled = payload.get("modeled_periods")
    if not isinstance(modeled, list):
        raise ValueError("Check context modeled_periods must be a list")
    overrides = payload.get("base_classification_overrides")
    if not isinstance(overrides, dict):
        raise ValueError("Check context base_classification_overrides must be an object")
    return CheckContext(
        schema_version=schema_version,
        source_payload=source_payload,
        modeled_periods=tuple(str(item) for item in modeled),
        base_classification_overrides={str(k): str(v) for k, v in overrides.items()},
        judgment_bindings=tuple(bindings),
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


def classification_overrides_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    """Merge base overrides with current Accounting Judgment treatment selections."""
    sheet_name = "Accounting Judgment"
    if sheet_name not in trainer_wb.sheetnames:
        raise ValueError("Trainer is missing Accounting Judgment sheet required for Check")
    overrides = dict(context.base_classification_overrides)
    ws = trainer_wb[sheet_name]
    for binding in context.judgment_bindings:
        selected = ws.cell(row=binding.worksheet_row, column=6).value
        if selected is None or (isinstance(selected, str) and not selected.strip()):
            treatment = binding.reference_treatment
        else:
            treatment = str(selected).strip()
            if treatment not in binding.allowed_treatments:
                raise ValueError(
                    f"Invalid treatment {treatment!r} on Accounting Judgment row "
                    f"{binding.worksheet_row}; allowed: {list(binding.allowed_treatments)}"
                )
        overrides[binding.override_selector] = treatment
    return overrides


def live_classification_formula(
    judgment_row: int,
    reference_treatment: str,
) -> str:
    """System-generated Condensed classification formula driven only by Judgment!F."""
    if judgment_row < 1:
        raise ValueError(f"judgment_row must be >= 1, got {judgment_row}")
    if reference_treatment is None or not str(reference_treatment).strip():
        raise ValueError("reference_treatment must be a non-empty category string")
    treatment = str(reference_treatment)
    escaped = treatment.replace('"', '""')
    return (
        f"=IF('Accounting Judgment'!$F${judgment_row}=\"\","
        f"\"{escaped}\","
        f"'Accounting Judgment'!$F${judgment_row})"
    )


def _find_condensed_cells_with_formula(ws, expected_formula: str) -> list[tuple[int, int]]:
    matches: list[tuple[int, int]] = []
    for row in range(1, (ws.max_row or 0) + 1):
        value = ws.cell(row=row, column=2).value
        if value == expected_formula:
            matches.append((row, 2))
    return matches


def validate_live_judgment_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
) -> None:
    """Fail fast if generated judgment prompts or live Condensed links were modified."""
    judgment = "Accounting Judgment"
    condensed = "Condensed Financials"
    for wb, label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
        if judgment not in wb.sheetnames:
            raise ValueError(f"{label} is missing Accounting Judgment sheet")
        if condensed not in wb.sheetnames:
            raise ValueError(f"{label} is missing Condensed Financials sheet")

    for binding in context.judgment_bindings:
        row = binding.worksheet_row
        expected_alts = ", ".join(binding.allowed_treatments[1:])
        for wb, label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
            d_val = wb[judgment].cell(row=row, column=4).value
            e_val = wb[judgment].cell(row=row, column=5).value
            if d_val != binding.reference_treatment:
                raise ValueError(
                    f"Accounting Judgment reference prompt was modified on row {row}"
                )
            if e_val != expected_alts:
                raise ValueError(
                    f"Accounting Judgment alternatives prompt was modified on row {row}"
                )

        expected_formula = live_classification_formula(
            binding.worksheet_row,
            binding.reference_treatment,
        )
        ak_matches = _find_condensed_cells_with_formula(
            answer_key_wb[condensed], expected_formula
        )
        if len(ak_matches) != 1:
            raise ValueError(
                "Answer Key live-classification binding is missing/ambiguous "
                f"for judgment row {row}"
            )
        link_row, link_col = ak_matches[0]
        trainer_val = trainer_wb[condensed].cell(row=link_row, column=link_col).value
        if trainer_val != expected_formula:
            from openpyxl.utils import get_column_letter

            coord = f"{get_column_letter(link_col)}{link_row}"
            raise ValueError(
                f"Linked Condensed Financials classification was modified at {coord}"
            )
