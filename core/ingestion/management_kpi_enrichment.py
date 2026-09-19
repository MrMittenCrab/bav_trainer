"""Enrich working-copy management-KPI documents from bound source PDFs.

Protected extracts are never written. Original observation values, labels and
provenance stay in place; only supported admission fields are filled when the
bound PDF and document header evidence them.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .management_kpi import KIND_MANAGEMENT_KPI, classify_extracted_payload
from .management_kpi_identity import SUPPORTED_METRIC_MAPPINGS

PAGE_RESOLUTION_NAME = "management_kpi_page_resolution.json"
FISCAL_CALENDAR_BASIS = (
    "Fiscal year ends on the Sunday closest to January 31 of the following year, "
    "typically resulting in a 52-week year, but occasionally giving rise to an "
    "additional week, resulting in a 53-week year."
)
_PRINTED_PAGE_RE = re.compile(
    r"(?:Form\s+10-K|Annual\s+Report)\s+pp?\.\s*([0-9]+(?:\s*[–—,]\s*[0-9]+)*)",
    re.IGNORECASE,
)
_FY_LABEL_RE = re.compile(r"^FY(\d{4})$")
_FIFTY_THREE_YEAR_RE = re.compile(
    r"Fiscal\s+(\d{4})\s+was\s+a\s+53-week\s+year",
    re.IGNORECASE,
)
_FIFTY_TWO_LIST_RE = re.compile(
    r"Fiscal\s+((?:\d{4}(?:,\s*(?:and\s+)?)?)+)\s+were\s+each\s+52-week",
    re.IGNORECASE,
)
_FIFTY_TWO_YEAR_RE = re.compile(
    r"Fiscal\s+(\d{4})\s+was\s+a\s+52-week\s+year",
    re.IGNORECASE,
)
_FISCAL_CALENDAR_MARK = "Sunday closest to January 31"


@dataclass(frozen=True)
class SourceInspection:
    source_file: str
    physical_to_printed: dict[int, int]
    printed_to_physical: dict[int, int]
    fifty_three_week_years: tuple[int, ...]
    fifty_two_week_years: tuple[int, ...]
    fiscal_calendar_evidenced: bool
    page_texts: dict[int, str]


def _decode_identity_h(text: str) -> str:
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch in "\n\t":
            out.append(ch)
            continue
        if code == 0x01:
            out.append(" ")
            continue
        if code == 0x0B:
            out.append("-")
            continue
        if code == 0x0C:
            out.append(".")
            continue
        if 0x0E <= code <= 0x17:
            out.append(str(code - 0x0E))
            continue
        upper = code + 38
        if 65 <= upper <= 90 and code <= 0x34:
            out.append(chr(upper))
            continue
        lower = code + 43
        if 97 <= lower <= 122 and code >= ord("6"):
            out.append(chr(lower))
            continue
        out.append(ch)
    return "".join(out)


def decode_filing_text(text: str) -> str:
    """Return readable filing text; Identity-H pages are decoded when needed."""
    if not text:
        return ""
    lowered = text.lower()
    if "comparable" in lowered or "fiscal year" in lowered or "square foot" in lowered:
        return text
    decoded = _decode_identity_h(text)
    decoded_low = decoded.lower()
    if "comparable" in decoded_low or "fiscal" in decoded_low or "square foot" in decoded_low:
        return decoded
    return text


def _printed_page_from_lines(text: str) -> int | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    last = lines[-1]
    if last.isdigit() and 1 <= int(last) <= 200:
        return int(last)
    return None


def inspect_source_pdf(path: Path) -> SourceInspection:
    import fitz

    physical_to_printed: dict[int, int] = {}
    page_texts: dict[int, str] = {}
    pdf = Path(path)
    doc = fitz.open(pdf)
    try:
        for index in range(doc.page_count):
            physical = index + 1
            text = decode_filing_text(doc[index].get_text() or "")
            page_texts[physical] = text
            printed = _printed_page_from_lines(text)
            if printed is not None:
                physical_to_printed[physical] = printed
    finally:
        doc.close()
    printed_to_physical = {
        printed: physical for physical, printed in physical_to_printed.items()
    }
    combined = "\n".join(page_texts[key] for key in sorted(page_texts))
    fifty_three = tuple(
        sorted({int(match.group(1)) for match in _FIFTY_THREE_YEAR_RE.finditer(combined)})
    )
    fifty_two = {
        int(year)
        for match in _FIFTY_TWO_LIST_RE.finditer(combined)
        for year in re.findall(r"\d{4}", match.group(1))
    }
    fifty_two.update(
        int(match.group(1)) for match in _FIFTY_TWO_YEAR_RE.finditer(combined)
    )
    return SourceInspection(
        source_file=pdf.name,
        physical_to_printed=physical_to_printed,
        printed_to_physical=printed_to_physical,
        fifty_three_week_years=fifty_three,
        fifty_two_week_years=tuple(sorted(fifty_two)),
        fiscal_calendar_evidenced=_FISCAL_CALENDAR_MARK in combined,
        page_texts=page_texts,
    )


def printed_pages_from_reference(page_reference: str) -> tuple[int, ...]:
    pages: list[int] = []
    for match in _PRINTED_PAGE_RE.finditer(page_reference or ""):
        blob = match.group(1)
        parts = re.split(r"[–—,]", blob)
        numbers = [int(part.strip()) for part in parts if part.strip().isdigit()]
        if len(numbers) == 2 and numbers[0] <= numbers[1] and numbers[1] - numbers[0] <= 8:
            pages.extend(range(numbers[0], numbers[1] + 1))
        else:
            pages.extend(numbers)
    return tuple(dict.fromkeys(pages))


def resolve_physical_pages(
    page_reference: str,
    inspection: SourceInspection,
) -> tuple[int, ...]:
    resolved: list[int] = []
    for printed in printed_pages_from_reference(page_reference):
        physical = inspection.printed_to_physical.get(printed)
        if physical is not None:
            resolved.append(physical)
    return tuple(resolved)


def _supporting_text(inspection: SourceInspection, physical_pages: Iterable[int]) -> str:
    snippets: list[str] = []
    for physical in physical_pages:
        text = " ".join(inspection.page_texts.get(physical, "").split())
        if not text:
            continue
        snippets.append(text[:400])
    return " ".join(snippets)


def _focus_item(item: MappingLike) -> bool:
    return isinstance(item.get("metric_id"), str) and item["metric_id"] in SUPPORTED_METRIC_MAPPINGS


MappingLike = dict[str, Any]


def _calendar_week_for_year(fiscal_year: int, inspection: SourceInspection) -> bool | None:
    if fiscal_year in inspection.fifty_three_week_years:
        return True
    if fiscal_year in inspection.fifty_two_week_years:
        return False
    return None


def enrich_management_payload(
    payload: dict[str, Any],
    inspection: SourceInspection,
    *,
    extraction_document: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return an enriched working copy and the page-resolution record."""
    if classify_extracted_payload(payload, path=extraction_document) != KIND_MANAGEMENT_KPI:
        raise ValueError(f"{extraction_document}: not a management-KPI document")
    enriched = json.loads(json.dumps(payload))
    report = enriched["report"]
    fiscal_year = int(report["fiscal_year"])
    fiscal_year_end = str(report["fiscal_year_end"])
    expected_label = f"FY{fiscal_year}"
    original_basis = report.get("reporting_basis", "")
    if inspection.fiscal_calendar_evidenced:
        if "original_reporting_basis" not in report:
            report["original_reporting_basis"] = original_basis
        report["reporting_basis"] = FISCAL_CALENDAR_BASIS
    week_excluded = _calendar_week_for_year(fiscal_year, inspection)
    fields: list[dict[str, Any]] = []
    for item in enriched["reported_kpis"]:
        if not _focus_item(item):
            continue
        source = item.get("source") or {}
        page_reference = str(source.get("page_reference") or "")
        physical_pages = resolve_physical_pages(page_reference, inspection)
        printed = printed_pages_from_reference(page_reference)
        original_period = str(item.get("period") or "")
        if original_period == expected_label:
            item["original_period_label"] = original_period
            item["period"] = fiscal_year_end
        qualifiers = item.get("qualifiers")
        if not isinstance(qualifiers, dict):
            qualifiers = {}
            item["qualifiers"] = qualifiers
        if "excludes_53rd_week" not in qualifiers and week_excluded is not None:
            qualifiers["excludes_53rd_week"] = week_excluded
        if "presentation" not in item:
            item["presentation"] = {
                "role": "current",
                "evidence": (
                    "Item 7 / Item 1 of this annual report presents the metric as a "
                    "current-period management operating KPI for the fiscal year discussed."
                ),
                "source": {
                    "section": source.get("section", ""),
                    "page_reference": page_reference,
                    "source_file": inspection.source_file,
                },
            }
        fields.append(
            {
                "extraction_document": extraction_document,
                "metric_id": item["metric_id"],
                "period": item.get("period"),
                "original_period_label": item.get("original_period_label", original_period),
                "page_reference": page_reference,
                "printed_pages": list(printed),
                "physical_pages": list(physical_pages),
                "supporting_text": _supporting_text(inspection, physical_pages),
                "calendar_week_excluded": week_excluded,
            }
        )
    record = {
        "extraction_document": extraction_document,
        "source_file": inspection.source_file,
        "fiscal_year": fiscal_year,
        "fiscal_year_end": fiscal_year_end,
        "fiscal_calendar_evidenced": inspection.fiscal_calendar_evidenced,
        "fifty_three_week_years": list(inspection.fifty_three_week_years),
        "fifty_two_week_years": list(inspection.fifty_two_week_years),
        "printed_to_physical": {
            str(printed): physical
            for printed, physical in sorted(inspection.printed_to_physical.items())
        },
        "fields": fields,
    }
    return enriched, record


def enrich_management_working_copies(
    extracted_dir: Path,
    source_dir: Path,
    *,
    resolution_path: Path | None = None,
) -> dict[str, Any]:
    """Enrich management-KPI working copies in extracted_dir from source_dir PDFs."""
    extracted = Path(extracted_dir)
    source = Path(source_dir)
    resolved = extracted.resolve()
    if resolved == source.resolve():
        raise ValueError("refusing to enrich a source directory")
    protected_extracted = source.resolve().parent / "extracted"
    if resolved == protected_extracted:
        raise ValueError("refusing to enrich protected source extracts")
    records: list[dict[str, Any]] = []
    written: list[str] = []
    inspections: dict[str, SourceInspection] = {}
    for path in sorted(extracted.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if classify_extracted_payload(payload, path=path) != KIND_MANAGEMENT_KPI:
            continue
        source_file = str(payload.get("report", {}).get("source_file") or "")
        pdf = source / source_file
        if not pdf.is_file():
            raise ValueError(f"{path.name}: bound source PDF missing: {pdf}")
        if source_file not in inspections:
            inspections[source_file] = inspect_source_pdf(pdf)
        enriched, record = enrich_management_payload(
            payload,
            inspections[source_file],
            extraction_document=path.name,
        )
        path.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")
        written.append(path.name)
        records.append(record)
    sidecar = {
        "documents": records,
        "written": written,
    }
    dest = Path(resolution_path) if resolution_path is not None else (
        extracted.parent / PAGE_RESOLUTION_NAME
    )
    dest.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sidecar["resolution_path"] = str(dest)
    return sidecar
