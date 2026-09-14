"""Load / serialize ExtractedFiling JSON v1.0."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from ..data.filing import (
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_SUPPLEMENTAL_STATUS,
    ALLOWED_UNIT_SCALES,
    SCHEMA_VERSION,
    ExtractedFiling,
    ExtractedStatementRow,
    FilingMetadata,
    FilingValue,
    PresentationRole,
    SourceRef,
    SupplementalFact,
)


def _required_nonempty_str(payload: dict, key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} is required")
    return value


def _optional_str(payload: dict, key: str, *, context: str) -> str:
    value = payload.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{context}.{key} must be a string")
    return value


def _required_positive_int(payload: dict, key: str, *, context: str) -> int:
    if key not in payload:
        raise ValueError(f"{context}.{key} is required")
    value = payload[key]
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{context}.{key} must be a positive integer")
    return value


def _parse_date(value: object, *, context: str = "date") -> date:
    if value is None:
        raise ValueError(f"{context} is required")
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(f"invalid date: {value!r}")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid date: {value!r}") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"invalid date: {value!r}")
    return parsed


def _parse_source(payload: object, *, require_page: bool = True) -> SourceRef:
    if not isinstance(payload, dict):
        raise ValueError("source must be an object")
    page = payload.get("page")
    if require_page and (not isinstance(page, int) or isinstance(page, bool) or page <= 0):
        raise ValueError("statement/supplemental source page must be a positive integer")
    if page is None:
        page = 0
    if not isinstance(page, int) or isinstance(page, bool) or page < 0:
        raise ValueError(f"invalid source page: {page!r}")
    return SourceRef(
        page=int(page),
        statement=str(payload.get("statement") or ""),
        note=str(payload.get("note") or ""),
        label=str(payload.get("label") or ""),
    )


def _parse_values(payload: object) -> dict[date, FilingValue]:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("statement row values must be a non-empty object")
    values: dict[date, FilingValue] = {}
    for raw_period, entry in payload.items():
        period = _parse_date(raw_period)
        if not isinstance(entry, dict):
            raise ValueError(f"statement value for {raw_period} must be an object")
        raw_value = entry.get("value")
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            raise ValueError(f"statement value for {raw_period} must be numeric")
        role_raw = entry.get("presentation_role")
        try:
            role = PresentationRole(str(role_raw))
        except ValueError as exc:
            raise ValueError(f"unknown presentation_role: {role_raw!r}") from exc
        values[period] = FilingValue(value=float(raw_value), presentation_role=role)
    return values


def _parse_statement_row(payload: object) -> ExtractedStatementRow:
    if not isinstance(payload, dict):
        raise ValueError("statement row must be an object")
    label = payload.get("label")
    section = payload.get("section")
    if not isinstance(label, str) or not label:
        raise ValueError("statement row label is required")
    if not isinstance(section, str):
        raise ValueError("statement row section must be a string")
    suggested = payload.get("suggested_concept", "")
    if suggested is None:
        suggested = ""
    if not isinstance(suggested, str):
        raise ValueError("suggested_concept must be a string")
    return ExtractedStatementRow(
        label=label,
        section=section,
        suggested_concept=suggested,
        values=_parse_values(payload.get("values")),
        source=_parse_source(payload.get("source")),
    )


def _parse_supplemental(payload: object) -> SupplementalFact:
    if not isinstance(payload, dict):
        raise ValueError("supplemental fact must be an object")
    fact_type = payload.get("fact_type")
    if not isinstance(fact_type, str) or not fact_type:
        raise ValueError("supplemental fact_type is required")
    status = str(payload.get("status") or "")
    if status not in ALLOWED_SUPPLEMENTAL_STATUS:
        raise ValueError(f"supplemental status outside reported/derived: {status!r}")
    derivation = str(payload.get("derivation") or "")
    if status == "derived" and not derivation.strip():
        raise ValueError("derived supplemental fact requires derivation")
    raw_value = payload.get("value")
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise ValueError("supplemental value must be numeric")
    return SupplementalFact(
        fact_type=fact_type,
        period=_parse_date(payload.get("period"), context="supplemental.period"),
        value=float(raw_value),
        status=status,
        source=_parse_source(payload.get("source")),
        derivation=derivation,
    )


def load_extracted_filing(path: Path) -> ExtractedFiling:
    """Parse one ExtractedFiling JSON v1.0 file."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("extracted filing JSON must be an object")

    schema_version = str(payload.get("schema_version") or "")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {schema_version!r}")

    company = payload.get("company")
    if not isinstance(company, dict):
        raise ValueError("company object is required")
    filing_raw = payload.get("filing")
    if not isinstance(filing_raw, dict):
        raise ValueError("filing object is required")

    document_type = str(filing_raw.get("document_type") or "")
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise ValueError(f"unknown document_type: {document_type!r}")
    unit_scale = str(filing_raw.get("unit_scale") or "")
    if unit_scale not in ALLOWED_UNIT_SCALES:
        raise ValueError(f"unknown unit_scale: {unit_scale!r}")

    company_name = _required_nonempty_str(company, "name", context="company")
    ticker = _required_nonempty_str(company, "ticker", context="company")
    stock_code = _optional_str(company, "stock_code", context="company")
    jurisdiction = _required_nonempty_str(company, "jurisdiction", context="company")
    fiscal_year = _required_positive_int(filing_raw, "fiscal_year", context="filing")
    period_end = _parse_date(filing_raw.get("period_end"), context="filing.period_end")
    currency = _required_nonempty_str(filing_raw, "currency", context="filing")
    source_file = _required_nonempty_str(filing_raw, "source_file", context="filing")
    source_sha256 = _optional_str(filing_raw, "source_sha256", context="filing")

    statements = payload.get("statements")
    if not isinstance(statements, dict):
        raise ValueError("statements object is required")

    def _rows(key: str) -> tuple[ExtractedStatementRow, ...]:
        rows = statements.get(key) or []
        if not isinstance(rows, list):
            raise ValueError(f"statements.{key} must be an array")
        return tuple(_parse_statement_row(row) for row in rows)

    note_facts = payload.get("note_facts") or []
    share_facts = payload.get("share_facts") or []
    if not isinstance(note_facts, list) or not isinstance(share_facts, list):
        raise ValueError("note_facts and share_facts must be arrays")

    return ExtractedFiling(
        schema_version=schema_version,
        company_name=company_name,
        ticker=ticker,
        stock_code=stock_code,
        jurisdiction=jurisdiction,
        filing=FilingMetadata(
            document_type=document_type,
            fiscal_year=fiscal_year,
            period_end=period_end,
            currency=currency,
            unit_scale=unit_scale,
            source_file=source_file,
            source_sha256=source_sha256,
        ),
        income_statement=_rows("income_statement"),
        balance_sheet=_rows("balance_sheet"),
        cash_flow=_rows("cash_flow"),
        note_facts=tuple(_parse_supplemental(item) for item in note_facts),
        share_facts=tuple(_parse_supplemental(item) for item in share_facts),
    )


def extracted_filing_to_payload(filing: ExtractedFiling) -> dict[str, Any]:
    """Serialize ExtractedFiling to the stable v1.0 JSON shape."""

    def _source(src: SourceRef) -> dict[str, Any]:
        out: dict[str, Any] = {"page": src.page}
        if src.statement:
            out["statement"] = src.statement
        if src.note:
            out["note"] = src.note
        if src.label:
            out["label"] = src.label
        return out

    def _num(value: float) -> int | float:
        return int(value) if float(value).is_integer() else float(value)

    def _row(row: ExtractedStatementRow) -> dict[str, Any]:
        return {
            "label": row.label,
            "section": row.section,
            "suggested_concept": row.suggested_concept,
            "values": {
                period.isoformat(): {
                    "value": _num(value.value),
                    "presentation_role": value.presentation_role.value,
                }
                for period, value in sorted(row.values.items())
            },
            "source": _source(row.source),
        }

    def _fact(fact: SupplementalFact) -> dict[str, Any]:
        out: dict[str, Any] = {
            "fact_type": fact.fact_type,
            "period": fact.period.isoformat(),
            "value": _num(fact.value),
            "status": fact.status,
            "source": _source(fact.source),
        }
        if fact.derivation:
            out["derivation"] = fact.derivation
        return out

    meta: dict[str, Any] = {
        "document_type": filing.filing.document_type,
        "fiscal_year": filing.filing.fiscal_year,
        "period_end": filing.filing.period_end.isoformat(),
        "currency": filing.filing.currency,
        "unit_scale": filing.filing.unit_scale,
        "source_file": filing.filing.source_file,
    }
    if filing.filing.source_sha256:
        meta["source_sha256"] = filing.filing.source_sha256

    return {
        "schema_version": filing.schema_version,
        "company": {
            "name": filing.company_name,
            "ticker": filing.ticker,
            "stock_code": filing.stock_code,
            "jurisdiction": filing.jurisdiction,
        },
        "filing": meta,
        "statements": {
            "income_statement": [_row(r) for r in filing.income_statement],
            "balance_sheet": [_row(r) for r in filing.balance_sheet],
            "cash_flow": [_row(r) for r in filing.cash_flow],
        },
        "note_facts": [_fact(f) for f in filing.note_facts],
        "share_facts": [_fact(f) for f in filing.share_facts],
    }
