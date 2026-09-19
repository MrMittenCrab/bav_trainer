"""Enrich working-copy management-KPI documents from bound source PDFs.

Protected extracts are never written. Original observation values, labels and
provenance stay in place; only supported admission fields are filled when the
bound PDF and document header evidence them.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .management_kpi import KIND_MANAGEMENT_KPI, classify_extracted_payload
from .management_kpi_identity import (
    FAMILY_SALES_PER_SQUARE_FOOT,
    SUPPORTED_METRIC_MAPPINGS,
)

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
_SHIFT_RULE_RE = re.compile(
    r"year following a 53-?week year.{0,80}shifted by one week",
    re.IGNORECASE,
)
_WINDOW_RE = re.compile(
    r"(\d+)\s+weeks ended\s+([A-Za-z]+\s+\d+,?\s+\d{4})\s+are compared to the\s+"
    r"(\d+)\s+weeks ended\s+([A-Za-z]+\s+\d+,?\s+\d{4})"
    r"(?:\s+rather than\s+([A-Za-z]+\s+\d+,?\s+\d{4}))?",
    re.IGNORECASE,
)
_SPSF_LEVEL_SERIES_RE = re.compile(
    r"sales per square foot was\s+\$([0-9,]+),\s+\$([0-9,]+),\s+and\s+\$([0-9,]+)"
    r"\s+for\s+(\d{4}),\s+(\d{4}),\s+and\s+(\d{4})",
    re.IGNORECASE,
)
_SPSF_TWO_LEVEL_RE = re.compile(
    r"sales per square foot (?:was|were)\s+\$([0-9,]+)\s+and\s+\$([0-9,]+)"
    r"\s+for\s+(\d{4})\s+and\s+(\d{4})",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_ENCODED_DOLLAR_RE = re.compile(r"[\x03$]\s*(\d{1,3})\s+(\d{3})(?!\d)")
_ENCODED_PERCENT_RE = re.compile(r"(\d)\s*\x04")
_MONTH_DAY_YEAR_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},?\s+\d{4}",
    re.IGNORECASE,
)
_INTRO_DATE_MARKERS = (
    "sunday closest to january 31",
    "typically resulting in a 52-week year",
    "components of management",
    "components of this md",
    "social impact",
    "we have contributed",
)
_DATE_SUPPORT_PHRASES = (
    "fiscal year ended",
    "weeks ended",
    "number of company-operated stores",
)
_COMPARISON_PHRASES = (
    "comparable sales",
    "comparable store sales",
    "total comparable sales",
)
CAUSE_SOURCE_ABSENCE = "genuine_source_absence"
CAUSE_AMBIGUITY = "documentary_ambiguity"
CAUSE_SELECTION = "selection_limitation"
CAUSE_IMPLEMENTATION = "implementation_defect"
CAUSE_ACCESS = "unavailable_access"
DEFINITION_EQUIVALENT = "equivalent"
DEFINITION_DIFFERENT = "different"
DEFINITION_UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class SourceInspection:
    source_file: str
    physical_to_printed: dict[int, int]
    printed_to_physical: dict[int, int]
    fifty_three_week_years: tuple[int, ...]
    fifty_two_week_years: tuple[int, ...]
    fiscal_calendar_evidenced: bool
    page_texts: dict[int, str]


@dataclass(frozen=True)
class CalendarYearEvidence:
    fiscal_year: int
    fifty_three_week: bool
    source_file: str
    physical_page: int
    passage: str
    cross_filing: bool


@dataclass(frozen=True)
class ComparisonWindowEvidence:
    label: str
    current_weeks: str = ""
    prior_weeks: str = ""
    not_compared_to: str = ""
    subsequent_year_shift_rule: bool = False
    source_file: str = ""
    physical_pages: tuple[int, ...] = ()
    passage: str = ""


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


def normalize_filing_amounts(text: str) -> str:
    """Recover `$1,574` and `4%` from leftover Identity-H marks."""
    return _ENCODED_PERCENT_RE.sub(r"\1%", _ENCODED_DOLLAR_RE.sub(r"$\1,\2", text))


def decode_filing_text(text: str) -> str:
    """Return readable filing text; Identity-H pages are decoded when needed."""
    if not text:
        return ""
    lowered = text.lower()
    readable = (
        "comparable" in lowered or "fiscal year" in lowered or "square foot" in lowered
    )
    candidate = text
    if not readable:
        decoded = _decode_identity_h(text)
        decoded_low = decoded.lower()
        if (
            "comparable" in decoded_low
            or "fiscal" in decoded_low
            or "square foot" in decoded_low
        ):
            candidate = decoded
    return normalize_filing_amounts(candidate)


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


def _collapsed(text: str) -> str:
    return " ".join(text.split())


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT_RE.split(_collapsed(text)) if part.strip()]


def _line_candidates(text: str) -> list[str]:
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    return [line for line in lines if line]


def _passage_matching(
    texts: Iterable[str],
    needles: Iterable[str],
    *,
    max_len: int = 420,
    reject: Iterable[str] = (),
) -> str:
    """Return a complete sentence or table row that contains every required needle."""
    required = [needle.lower() for needle in needles if needle]
    if not required:
        return ""
    blocked = [marker.lower() for marker in reject if marker]
    matches: list[str] = []
    for text in texts:
        candidates = _sentences(text) + _line_candidates(text)
        for candidate in candidates:
            lowered = candidate.lower()
            if blocked and any(marker in lowered for marker in blocked):
                continue
            if all(needle in lowered for needle in required):
                clipped = candidate[:max_len]
                if all(needle in clipped.lower() for needle in required):
                    matches.append(clipped)
                elif len(candidate) <= 800:
                    matches.append(candidate)
    if not matches:
        return ""
    return min(matches, key=len)


def _page_texts(
    inspection: SourceInspection, physical_pages: Iterable[int]
) -> list[str]:
    texts: list[str] = []
    for physical in physical_pages:
        text = inspection.page_texts.get(physical, "")
        if text:
            texts.append(text)
    return texts


def format_physical_page_mapping(
    printed_pages: Iterable[int], physical_pages: Iterable[int]
) -> str:
    """Deterministic printed→physical mapping consumed by admission."""
    pairs = list(zip(tuple(printed_pages), tuple(physical_pages)))
    if not pairs:
        return ""
    return ";".join(f"{printed}→{physical}" for printed, physical in pairs)


def validate_physical_page_binding(
    inspection: SourceInspection,
    printed_pages: Iterable[int],
    claimed_physical_pages: Iterable[int],
) -> tuple[int, ...]:
    """Return PDF-validated physical pages, or empty when the claim is unsupported."""
    printed = tuple(printed_pages)
    claimed = tuple(int(page) for page in claimed_physical_pages)
    resolved = tuple(
        inspection.printed_to_physical.get(page) for page in printed
    )
    if not printed or any(page is None for page in resolved):
        return ()
    resolved_pages = tuple(int(page) for page in resolved if page is not None)
    if claimed and claimed != resolved_pages:
        return ()
    for physical in resolved_pages:
        footer = inspection.physical_to_printed.get(physical)
        if footer is None:
            return ()
    return resolved_pages


def definition_features(text: str) -> dict[str, str]:
    """Documentary features used for equivalence; original text is not rewritten."""
    lowered = " ".join(text.lower().split())
    if not lowered:
        return {}
    features: dict[str, str] = {}
    if "e-commerce" in lowered or "ecommerce" in lowered:
        features["channel_population"] = "company_operated_stores_and_ecommerce"
    elif "direct to consumer" in lowered or "direct-to-consumer" in lowered:
        features["channel_population"] = "company_operated_stores_and_direct_to_consumer"
    elif "company-operated store" in lowered or "comparable store" in lowered:
        features["channel_population"] = "company_operated_stores"
    if "average ending square footage" in lowered:
        features["square_footage_basis"] = "average_ending"
    elif "average store square footage" in lowered or "average square footage" in lowered:
        features["square_footage_basis"] = "average_during_period"
    if "12 full fiscal month" in lowered:
        features["store_tenure"] = "12_full_fiscal_months"
    if "53rd week" in lowered and "excluded" in lowered:
        features["excludes_53rd_week_rule"] = "true"
    return features


def assess_definition_equivalence(left: str, right: str) -> str:
    """Compare disclosed definition features without overwriting either text."""
    if not str(left).strip() or not str(right).strip():
        return DEFINITION_UNRESOLVED
    if str(left).strip() == str(right).strip():
        return DEFINITION_EQUIVALENT
    left_features = definition_features(left)
    right_features = definition_features(right)
    if not left_features or not right_features:
        return DEFINITION_UNRESOLVED
    shared = set(left_features) & set(right_features)
    if not shared:
        return DEFINITION_UNRESOLVED
    if any(left_features[key] != right_features[key] for key in shared):
        return DEFINITION_DIFFERENT
    return DEFINITION_EQUIVALENT


def _year_length_passage(text: str, year: int, *, fifty_three: bool) -> str:
    week = "53-week" if fifty_three else "52-week"
    listed = _passage_matching(
        [text],
        ("were each 52-week", str(year)),
        reject=_INTRO_DATE_MARKERS,
    )
    if listed:
        return listed
    passage = _passage_matching(
        [text],
        (f"fiscal {year}", week),
        reject=_INTRO_DATE_MARKERS,
    )
    if passage:
        return passage
    return _passage_matching(
        [text],
        (str(year), week),
        reject=_INTRO_DATE_MARKERS,
    )


def _year_length_page(inspection: SourceInspection, year: int) -> int | None:
    year_text = str(year)
    for physical in sorted(inspection.page_texts):
        text = inspection.page_texts[physical]
        fifty_three = _FIFTY_THREE_YEAR_RE.search(text)
        if fifty_three and fifty_three.group(1) == year_text:
            return physical
        fifty_two_list = _FIFTY_TWO_LIST_RE.search(text)
        if fifty_two_list and year_text in fifty_two_list.group(1):
            return physical
        fifty_two_year = _FIFTY_TWO_YEAR_RE.search(text)
        if fifty_two_year and fifty_two_year.group(1) == year_text:
            return physical
    for physical in sorted(inspection.page_texts):
        text = inspection.page_texts[physical]
        if year_text not in text:
            continue
        if year in inspection.fifty_two_week_years or year in inspection.fifty_three_week_years:
            if "52-week" in text.lower() or "53-week" in text.lower():
                return physical
    return None


def collect_calendar_corpus(
    inspections: dict[str, SourceInspection],
) -> dict[int, CalendarYearEvidence]:
    """Index 52/53-week year disclosures across all inspected filings."""
    corpus: dict[int, CalendarYearEvidence] = {}
    for source_file, inspection in inspections.items():
        for year in inspection.fifty_three_week_years:
            page = _year_length_page(inspection, year)
            if page is None:
                continue
            passage = _year_length_passage(
                inspection.page_texts.get(page, ""), year, fifty_three=True
            )
            corpus.setdefault(
                year,
                CalendarYearEvidence(
                    fiscal_year=year,
                    fifty_three_week=True,
                    source_file=source_file,
                    physical_page=page,
                    passage=passage,
                    cross_filing=False,
                ),
            )
        for year in inspection.fifty_two_week_years:
            if year in corpus:
                continue
            page = _year_length_page(inspection, year)
            if page is None:
                continue
            passage = _year_length_passage(
                inspection.page_texts.get(page, ""), year, fifty_three=False
            )
            corpus[year] = CalendarYearEvidence(
                fiscal_year=year,
                fifty_three_week=False,
                source_file=source_file,
                physical_page=page,
                passage=passage,
                cross_filing=False,
            )
    return corpus


def extract_comparison_window(
    inspection: SourceInspection,
) -> ComparisonWindowEvidence | None:
    """Return the disclosed comparison window; do not infer it from year length."""
    shift_pages: list[int] = []
    window_pages: list[int] = []
    window_match = None
    shift_passage = ""
    window_passage = ""
    for physical, text in inspection.page_texts.items():
        collapsed = _collapsed(text)
        if _SHIFT_RULE_RE.search(collapsed):
            shift_pages.append(physical)
            if not shift_passage:
                shift_passage = _passage_matching([collapsed], ("shifted by one week",))
        found = _WINDOW_RE.search(collapsed)
        if found:
            window_pages.append(physical)
            window_match = found
            window_passage = found.group(0)
    if window_match is None and not shift_pages:
        return None
    label = ""
    current_weeks = ""
    prior_weeks = ""
    not_compared_to = ""
    if window_match is not None:
        current_weeks = f"{window_match.group(1)} weeks ended {window_match.group(2)}"
        prior_weeks = f"{window_match.group(3)} weeks ended {window_match.group(4)}"
        not_compared_to = window_match.group(5) or ""
        label = f"{current_weeks} vs {prior_weeks}"
        if not_compared_to:
            label = f"{label} (not {not_compared_to})"
    return ComparisonWindowEvidence(
        label=label,
        current_weeks=current_weeks,
        prior_weeks=prior_weeks,
        not_compared_to=not_compared_to,
        subsequent_year_shift_rule=bool(shift_pages),
        source_file=inspection.source_file,
        physical_pages=tuple(sorted(set(shift_pages + window_pages))),
        passage=window_passage or shift_passage,
    )


def extract_spsf_prior_period_levels(
    inspection: SourceInspection,
) -> list[dict[str, Any]]:
    """Record repeated SPSF levels as documentary occurrences, not revisions."""
    occurrences: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int, str]] = set()
    for physical, text in inspection.page_texts.items():
        collapsed = _collapsed(text)
        triples = _SPSF_LEVEL_SERIES_RE.search(collapsed)
        pairs = _SPSF_TWO_LEVEL_RE.search(collapsed)
        match = triples or pairs
        if match is None:
            continue
        if triples is not None:
            values = [int(part.replace(",", "")) for part in match.group(1, 2, 3)]
            years = [int(part) for part in match.group(4, 5, 6)]
        else:
            values = [int(part.replace(",", "")) for part in match.group(1, 2)]
            years = [int(part) for part in match.group(3, 4)]
        for index, (year, value) in enumerate(zip(years, values)):
            key = (year, value, physical, "current" if index == 0 else "prior")
            if key in seen:
                continue
            seen.add(key)
            occurrences.append(
                {
                    "period_label": str(year),
                    "value": value,
                    "presentation_role": "current" if index == 0 else "prior",
                    "physical_page": physical,
                    "source_file": inspection.source_file,
                    "passage": match.group(0),
                }
            )
    return occurrences


def _value_needles(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        amount = float(value)
        if amount.is_integer():
            whole = int(amount)
            if abs(whole) < 100:
                if whole < 0:
                    return [f"{whole}%", f"decreased {abs(whole)}%"]
                return [f"{whole}%", f"increased {whole}%"]
            return [f"{whole:,}", str(whole), f"${whole:,}"]
        return [str(value)]
    return [str(value)]


def _metric_value_phrases(metric_id: str) -> tuple[str, ...]:
    if "sales_per_square_foot" in metric_id:
        return ("sales per square foot",)
    if "store_sales" in metric_id:
        return ("comparable store sales",)
    if "total_comparable" in metric_id:
        return ("total comparable sales",)
    return _COMPARISON_PHRASES


def _value_passage(texts: Iterable[str], item: MappingLike) -> str:
    metric = str(item.get("metric_id") or "")
    phrases = _metric_value_phrases(metric)
    amounts = _value_needles(item.get("value"))
    if not phrases or not amounts:
        return ""
    for phrase in phrases:
        for amount in amounts:
            found = _passage_matching(texts, (phrase, amount))
            if found:
                return found
    return ""


def _format_iso_date(value: str) -> tuple[str, ...]:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return ()
    month = parsed.strftime("%B")
    return (
        f"{month} {parsed.day}, {parsed.year}",
        f"{month} {parsed.day} {parsed.year}",
    )


def _date_passage(
    *,
    inspection: SourceInspection,
    texts: Iterable[str],
    fiscal_year_end: str,
    comparison_window: ComparisonWindowEvidence | None,
) -> str:
    if comparison_window is not None and comparison_window.current_weeks:
        window_texts = [comparison_window.passage] if comparison_window.passage else []
        found = _passage_matching(
            window_texts or texts,
            ("weeks ended",),
            reject=_INTRO_DATE_MARKERS,
        )
        if found and _MONTH_DAY_YEAR_RE.search(found):
            return found
    formatted = _format_iso_date(fiscal_year_end)
    search_texts = list(texts) + [
        inspection.page_texts[page] for page in sorted(inspection.page_texts)
    ]
    for form in formatted:
        for phrase in _DATE_SUPPORT_PHRASES:
            found = _passage_matching(
                search_texts,
                (phrase, form),
                reject=_INTRO_DATE_MARKERS,
            )
            if found and _MONTH_DAY_YEAR_RE.search(found):
                return found
    for text in search_texts:
        for candidate in _sentences(text) + _line_candidates(text):
            lowered = candidate.lower()
            if any(marker in lowered for marker in _INTRO_DATE_MARKERS):
                continue
            if not any(phrase in lowered for phrase in _DATE_SUPPORT_PHRASES):
                continue
            dates = _MONTH_DAY_YEAR_RE.findall(candidate)
            if len(dates) >= 2:
                return candidate[:420]
    return ""


def field_supporting_passages(
    *,
    inspection: SourceInspection,
    physical_pages: Iterable[int],
    extra_texts: Iterable[str] = (),
    item: MappingLike,
    comparison_window: ComparisonWindowEvidence | None,
    calendar: CalendarYearEvidence | None,
    fiscal_year_end: str = "",
) -> dict[str, str]:
    texts = _page_texts(inspection, physical_pages)
    texts.extend(extra_texts)
    metric = str(item.get("metric_id") or "")
    spsf = "sales_per_square_foot" in metric
    definition_needles = (
        ("sales per square foot is calculated", "average ending square footage")
        if spsf
        else ("comparable sales includes",)
    )
    if not spsf and "store_sales" in metric:
        definition_needles = ("comparable store sales reflects",)
    presentation_needles = (
        ("we use sales per square foot",)
        if spsf
        else ("we use comparable sales",)
    )
    date_passage = _date_passage(
        inspection=inspection,
        texts=texts,
        fiscal_year_end=fiscal_year_end or str(item.get("period") or ""),
        comparison_window=comparison_window,
    )
    calendar_passage = ""
    if calendar is not None and calendar.passage:
        calendar_passage = calendar.passage
    else:
        calendar_passage = _passage_matching(texts, ("52-week", "fiscal")) or _passage_matching(
            texts, ("53-week", "fiscal")
        )
    window_passage = ""
    if comparison_window is not None and comparison_window.current_weeks:
        window_passage = comparison_window.passage
    passages = {
        "value": _value_passage(texts, item),
        "dates": date_passage,
        "definition": _passage_matching(texts, definition_needles)
        or (
            _passage_matching(texts, ("comparable store sales", "direct to consumer"))
            if "total_comparable" in metric
            else ""
        ),
        "calendar": calendar_passage,
        "presentation": _passage_matching(texts, presentation_needles),
        "comparison_window": window_passage,
        "assurance": "",
        "revision": "",
    }
    return {key: value for key, value in passages.items() if value}


def _focus_item(item: MappingLike) -> bool:
    return isinstance(item.get("metric_id"), str) and item["metric_id"] in SUPPORTED_METRIC_MAPPINGS


MappingLike = dict[str, Any]


def _calendar_week_for_year(fiscal_year: int, inspection: SourceInspection) -> bool | None:
    if fiscal_year in inspection.fifty_three_week_years:
        return True
    if fiscal_year in inspection.fifty_two_week_years:
        return False
    return None


def _calendar_for_year(
    fiscal_year: int,
    inspection: SourceInspection,
    corpus: dict[int, CalendarYearEvidence],
) -> CalendarYearEvidence | None:
    own = _calendar_week_for_year(fiscal_year, inspection)
    if own is not None:
        page = _year_length_page(inspection, fiscal_year)
        hit = corpus.get(fiscal_year)
        return CalendarYearEvidence(
            fiscal_year=fiscal_year,
            fifty_three_week=own,
            source_file=inspection.source_file,
            physical_page=page or (hit.physical_page if hit is not None else 0),
            passage=(
                hit.passage
                if hit is not None and hit.source_file == inspection.source_file
                else _year_length_passage(
                    inspection.page_texts.get(page, "") if page else "",
                    fiscal_year,
                    fifty_three=own,
                )
            ),
            cross_filing=False,
        )
    hit = corpus.get(fiscal_year)
    if hit is None:
        return None
    return CalendarYearEvidence(
        fiscal_year=hit.fiscal_year,
        fifty_three_week=hit.fifty_three_week,
        source_file=hit.source_file,
        physical_page=hit.physical_page,
        passage=hit.passage,
        cross_filing=hit.source_file != inspection.source_file,
    )


def _definition_pages_and_text(
    payload: dict[str, Any],
    inspection: SourceInspection,
    metric_id: str,
) -> tuple[tuple[int, ...], str]:
    pages: list[int] = []
    text = ""
    for definition in payload.get("kpi_definitions") or []:
        if not isinstance(definition, dict):
            continue
        if definition.get("metric_id") != metric_id:
            continue
        source = definition.get("source") or {}
        pages.extend(resolve_physical_pages(str(source.get("page_reference") or ""), inspection))
        text = str(definition.get("definition") or "")
    return tuple(dict.fromkeys(pages)), text


def _existing_spsf_periods(items: Iterable[MappingLike]) -> set[str]:
    keys: set[str] = set()
    for item in items:
        if item.get("metric_id") != "sales_per_square_foot":
            continue
        keys.add(str(item.get("period") or ""))
        label = str(item.get("original_period_label") or "")
        if label:
            keys.add(label)
        period = str(item.get("period") or "")
        if period.startswith("FY"):
            keys.add(period)
    return keys


def _append_traced_spsf_occurrences(
    payload: dict[str, Any],
    levels: Sequence[dict[str, Any]],
    *,
    fiscal_year: int,
    year_end_map: Mapping[int, str],
    calendar_corpus: dict[int, CalendarYearEvidence],
    inspection: SourceInspection,
) -> list[dict[str, Any]]:
    """Add prior-period SPSF levels as documentary occurrences; do not invent revisions."""
    from copy import deepcopy

    items = payload.setdefault("reported_kpis", [])
    template = next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("metric_id") == "sales_per_square_foot"
        ),
        None,
    )
    if template is None:
        return []
    existing = _existing_spsf_periods(items)
    added: list[dict[str, Any]] = []
    for level in levels:
        year = int(level["period_label"])
        if year == fiscal_year:
            continue
        period = year_end_map.get(year, "")
        fy_label = f"FY{year}"
        if not period:
            continue
        if period in existing or fy_label in existing or str(year) in existing:
            continue
        item = deepcopy(template)
        item["period"] = period
        item["original_period_label"] = fy_label
        item["value"] = level["value"]
        item.pop("comparison", None)
        item.pop("revision", None)
        item.pop("revises", None)
        item.pop("supporting_evidence", None)
        source = dict(item.get("source") or {})
        source["source_file"] = inspection.source_file
        item["source"] = source
        calendar = calendar_corpus.get(year)
        qualifiers = dict(item.get("qualifiers") or {})
        if calendar is not None:
            qualifiers["excludes_53rd_week"] = calendar.fifty_three_week
        item["qualifiers"] = qualifiers
        item["presentation"] = {
            "role": level["presentation_role"],
            "evidence": level["passage"],
            "source": {
                "section": source.get("section", ""),
                "page_reference": source.get("page_reference", ""),
                "source_file": inspection.source_file,
            },
        }
        item["traced_prior_period"] = True
        items.append(item)
        existing.add(period)
        existing.add(fy_label)
        added.append(item)
    return added


def enrich_management_payload(
    payload: dict[str, Any],
    inspection: SourceInspection,
    *,
    extraction_document: str,
    calendar_corpus: dict[int, CalendarYearEvidence] | None = None,
    year_end_map: Mapping[int, str] | None = None,
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
    corpus = calendar_corpus or collect_calendar_corpus({inspection.source_file: inspection})
    calendar = _calendar_for_year(fiscal_year, inspection, corpus)
    week_excluded = None if calendar is None else calendar.fifty_three_week
    comparison_window = extract_comparison_window(inspection)
    spsf_levels = extract_spsf_prior_period_levels(inspection)
    _append_traced_spsf_occurrences(
        enriched,
        spsf_levels,
        fiscal_year=fiscal_year,
        year_end_map=year_end_map or {},
        calendar_corpus=corpus,
        inspection=inspection,
    )
    fields: list[dict[str, Any]] = []
    for item in enriched["reported_kpis"]:
        if not _focus_item(item):
            continue
        source = item.get("source") or {}
        page_reference = str(source.get("page_reference") or "")
        physical_pages = resolve_physical_pages(page_reference, inspection)
        printed = printed_pages_from_reference(page_reference)
        definition_pages, definition_text = _definition_pages_and_text(
            enriched, inspection, str(item["metric_id"])
        )
        extra_pages = list(definition_pages)
        if calendar is not None and calendar.source_file == inspection.source_file:
            extra_pages.append(calendar.physical_page)
        if comparison_window is not None:
            extra_pages.extend(comparison_window.physical_pages)
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
        extra_texts = _page_texts(inspection, extra_pages)
        if calendar is not None and calendar.cross_filing:
            extra_texts.append(calendar.passage)
        passages = field_supporting_passages(
            inspection=inspection,
            physical_pages=physical_pages,
            extra_texts=extra_texts,
            item=item,
            comparison_window=comparison_window,
            calendar=calendar,
            fiscal_year_end=str(item.get("period") or fiscal_year_end),
        )
        mapping = format_physical_page_mapping(printed, physical_pages)
        supporting = {
            "printed_pages": list(printed),
            "physical_pages": list(physical_pages),
            "source_file": inspection.source_file,
            "page_mapping": mapping,
            "passages": passages,
            "fiscal_year_length_weeks": (
                53 if calendar is not None and calendar.fifty_three_week else
                52 if calendar is not None else None
            ),
            "metric_excludes_53rd_week": week_excluded,
            "comparison_window": (
                None
                if comparison_window is None
                else {
                    "label": comparison_window.label,
                    "current_weeks": comparison_window.current_weeks,
                    "prior_weeks": comparison_window.prior_weeks,
                    "not_compared_to": comparison_window.not_compared_to,
                    "subsequent_year_shift_rule": (
                        comparison_window.subsequent_year_shift_rule
                    ),
                    "source_file": comparison_window.source_file,
                    "physical_pages": list(comparison_window.physical_pages),
                    "passage": comparison_window.passage,
                }
            ),
            "calendar_provenance": (
                None
                if calendar is None
                else {
                    "source_file": calendar.source_file,
                    "physical_page": calendar.physical_page,
                    "cross_filing": calendar.cross_filing,
                    "passage": calendar.passage,
                    "fifty_three_week": calendar.fifty_three_week,
                }
            ),
            "definition_features": definition_features(definition_text),
            "prior_period_levels": (
                spsf_levels
                if item["metric_id"] in SUPPORTED_METRIC_MAPPINGS
                and SUPPORTED_METRIC_MAPPINGS[item["metric_id"]].family
                == FAMILY_SALES_PER_SQUARE_FOOT
                else []
            ),
        }
        item["supporting_evidence"] = supporting
        presentation_passage = passages.get("presentation") or ""
        if item.get("traced_prior_period") and not presentation_passage:
            presentation_passage = next(
                (
                    str(level["passage"])
                    for level in spsf_levels
                    if level["value"] == item.get("value")
                    and level["presentation_role"] == "prior"
                ),
                "",
            )
        if presentation_passage and "presentation" not in item:
            item["presentation"] = {
                "role": "prior" if item.get("traced_prior_period") else "current",
                "evidence": presentation_passage,
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
                "page_mapping": mapping,
                "supporting_passages": passages,
                "calendar_week_excluded": week_excluded,
                "fiscal_year_length_weeks": supporting["fiscal_year_length_weeks"],
                "comparison_window": supporting["comparison_window"],
                "calendar_provenance": supporting["calendar_provenance"],
                "definition_features": supporting["definition_features"],
                "prior_period_levels": supporting["prior_period_levels"],
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
    calendar_corpus = collect_calendar_corpus(inspections)
    year_end_map: dict[int, str] = {}
    for path in sorted(extracted.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if classify_extracted_payload(payload, path=path) != KIND_MANAGEMENT_KPI:
            continue
        report = payload.get("report") or {}
        try:
            year_end_map[int(report["fiscal_year"])] = str(report["fiscal_year_end"])
        except (KeyError, TypeError, ValueError):
            continue
    for path in sorted(extracted.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if classify_extracted_payload(payload, path=path) != KIND_MANAGEMENT_KPI:
            continue
        source_file = str(payload.get("report", {}).get("source_file") or "")
        enriched, record = enrich_management_payload(
            payload,
            inspections[source_file],
            extraction_document=path.name,
            calendar_corpus=calendar_corpus,
            year_end_map=year_end_map,
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


_FAILURE_REMAINING = {
    "calendar_mismatch": (
        "calendar",
        CAUSE_AMBIGUITY,
        "aligned fiscal-year length and metric-specific 53rd-week treatment across the comparison pair",
    ),
    "comparison_window_mismatch": (
        "comparison_window",
        CAUSE_AMBIGUITY,
        "the same disclosed comparison window, or an explicit statement that no completed window applies",
    ),
    "calendar_reporting_mismatch": (
        "calendar_reporting_basis",
        CAUSE_AMBIGUITY,
        "the same documentary fiscal-calendar reporting basis",
    ),
    "definition_mismatch": (
        "definition",
        CAUSE_AMBIGUITY,
        "documentary equivalence of store-only, total-comparable, geographic, population and currency bases",
    ),
    "population_mismatch": (
        "definition",
        CAUSE_AMBIGUITY,
        "the same disclosed population basis",
    ),
    "missing_comparison": (
        "historical_comparison",
        CAUSE_SOURCE_ABSENCE,
        "a disclosed historical comparison observation with its actual comparison window",
    ),
    "peer_missing_comparison": (
        "historical_comparison",
        CAUSE_SOURCE_ABSENCE,
        "a peer occurrence that itself discloses a historical comparison window",
    ),
    "no_distinct_peer": (
        "historical_comparison",
        CAUSE_AMBIGUITY,
        "a distinct same-identity peer year with aligned calendar, window and definition evidence",
    ),
    "period_date": (
        "period_date",
        CAUSE_SOURCE_ABSENCE,
        "a complete documentary period-end date sentence or table row",
    ),
    "calendar_week_adjustment": (
        "calendar_week_adjustment",
        CAUSE_SOURCE_ABSENCE,
        "a disclosed 52/53-week treatment for this fiscal year",
    ),
    "presentation_role": (
        "presentation",
        CAUSE_SOURCE_ABSENCE,
        "a documentary presentation-role passage bound to this occurrence",
    ),
    "assurance": (
        "assurance",
        CAUSE_SELECTION,
        "documentary audited KPI assurance; annual-report placement is not sufficient",
    ),
    "revision": (
        "revision",
        CAUSE_SELECTION,
        "a documentary revision link; repetition of a prior-period level is not a revision",
    ),
    "canonical_selection": (
        "canonical_selection",
        CAUSE_SELECTION,
        "later-audited two-occurrence revision group with a documentary revision link",
    ),
}


def _supporting_dict(observation: Any) -> dict[str, Any]:
    supporting: dict[str, Any] = {}
    for key, raw in getattr(observation, "supporting_evidence", ()):
        try:
            supporting[key] = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            supporting[key] = raw
    return supporting


def _document_pages(supporting: Mapping[str, Any]) -> list[int]:
    pages = [int(page) for page in supporting.get("physical_pages") or []]
    provenance = supporting.get("calendar_provenance") or {}
    if provenance.get("physical_page"):
        pages.append(int(provenance["physical_page"]))
    window = supporting.get("comparison_window") or {}
    pages.extend(int(page) for page in window.get("physical_pages") or [])
    return pages


def _failure_record(
    *,
    requirement: str,
    cause: str,
    remaining: str,
    locator: str = "",
    peer: str = "",
    document: str = "",
    pages: Iterable[int] = (),
    passage: str = "",
    detail: str = "",
) -> dict[str, Any]:
    record = {
        "requirement": requirement,
        "cause": cause,
        "remaining_requirement": remaining,
        "detail": detail,
    }
    if locator:
        record["locator"] = locator
    if peer:
        record["comparison_pair"] = [locator, peer] if locator else [peer]
    if document:
        record["document"] = document
    if pages:
        record["pages"] = sorted(set(int(page) for page in pages))
    if passage:
        record["passage"] = passage
    return record


def build_group_decisions(
    group_selections: Iterable[Any],
    assessments: Iterable[Any],
    observations: Iterable[Any],
) -> tuple[dict[str, Any], ...]:
    """Reproducible per-group documentary decisions for admission review."""
    from .management_kpi_identity import (
        COMPARISON_CONFLICT_REASONS,
        FAMILY_SALES_PER_SQUARE_FOOT,
        HISTORICAL_COMPARISON_ELIGIBLE,
        LEVEL_ADMITTED,
        REASON_MISSING_COMPARISON,
    )
    from .management_kpi_reconciliation import (
        REASON_MISSING_REVISION_LINK,
        REASON_SINGLETON,
        REASON_UNAUDITED_REVISER,
        REASON_UNKNOWN_ASSURANCE,
        SELECTION_SELECTED,
    )

    by_locator = {item.locator: item for item in observations}
    by_assessment = {item.locator: item for item in assessments}
    decisions: list[dict[str, Any]] = []
    for group in group_selections:
        locators = [item.locator for item in group.occurrences]
        consumed: list[str] = []
        satisfied: list[str] = []
        pages: list[int] = []
        failures: list[dict[str, Any]] = []
        seen_failures: set[tuple[str, str, str]] = set()
        level_states: list[str] = []
        comparison_states: list[str] = []
        for locator in locators:
            observation = by_locator.get(locator)
            assessment = by_assessment.get(locator)
            if observation is None:
                continue
            consumed.append(locator)
            supporting = _supporting_dict(observation)
            occurrence_pages = _document_pages(supporting)
            pages.extend(occurrence_pages)
            passages = supporting.get("passages") or {}
            document = observation.extraction_document
            unresolved_obs = set(getattr(observation, "unresolved", ()) or ())
            if assessment is not None:
                evidence = dict(assessment.evidence)
                if evidence.get("period_kind") == "date":
                    satisfied.append("period_date")
                if evidence.get("calendar_week_adjustment"):
                    satisfied.append("calendar_week_adjustment")
                if evidence.get("calendar_reporting_basis"):
                    satisfied.append("calendar_reporting_basis")
                if evidence.get("definition_text"):
                    satisfied.append("definition")
                if getattr(observation.source, "physical_page_mapping", "") not in (
                    "",
                    "unresolved",
                ):
                    satisfied.append("physical_page_mapping")
                if assessment.level_admission == LEVEL_ADMITTED:
                    satisfied.append("level_admission")
                level_states.append(assessment.level_admission)
                comparison_states.append(assessment.historical_comparison)
                peers = list(assessment.peer_locators)
                for reason in assessment.unresolved_reasons:
                    mapped = _FAILURE_REMAINING.get(reason)
                    if mapped is None and reason in COMPARISON_CONFLICT_REASONS:
                        mapped = (
                            reason,
                            CAUSE_AMBIGUITY,
                            "aligned documentary evidence for this comparison pair",
                        )
                    if mapped is None:
                        continue
                    requirement, cause, remaining = mapped
                    key = (locator, requirement, reason)
                    if key in seen_failures:
                        continue
                    seen_failures.add(key)
                    passage = ""
                    if requirement == "comparison_window":
                        passage = str(passages.get("comparison_window") or "")
                    elif requirement == "calendar":
                        passage = str(passages.get("calendar") or "")
                    elif requirement == "definition":
                        passage = str(passages.get("definition") or "")
                    elif requirement == "period_date":
                        passage = str(passages.get("dates") or "")
                    elif requirement == "historical_comparison":
                        passage = str(passages.get("value") or "")
                    failures.append(
                        _failure_record(
                            requirement=requirement,
                            cause=cause,
                            remaining=remaining,
                            locator=locator,
                            peer=peers[0] if peers else "",
                            document=document,
                            pages=occurrence_pages,
                            passage=passage,
                            detail=reason,
                        )
                    )
            for reason in ("presentation_role", "assurance", "revision"):
                if reason not in unresolved_obs:
                    continue
                mapped = _FAILURE_REMAINING[reason]
                key = (locator, mapped[0], reason)
                if key in seen_failures:
                    continue
                seen_failures.add(key)
                failures.append(
                    _failure_record(
                        requirement=mapped[0],
                        cause=mapped[1],
                        remaining=mapped[2],
                        locator=locator,
                        document=document,
                        pages=occurrence_pages,
                        passage=str(passages.get(mapped[0], "")),
                        detail=reason,
                    )
                )
        reasons = list(group.reasons)
        additional = ""
        unresolved_decision = ""
        primary = ""
        if group.status != SELECTION_SELECTED:
            selection_hit = {
                REASON_UNAUDITED_REVISER,
                REASON_UNKNOWN_ASSURANCE,
                REASON_MISSING_REVISION_LINK,
                REASON_SINGLETON,
            } & set(reasons)
            if selection_hit or reasons:
                primary = CAUSE_SELECTION
                unresolved_decision = _FAILURE_REMAINING["canonical_selection"][2]
                failures.append(
                    _failure_record(
                        requirement="canonical_selection",
                        cause=CAUSE_SELECTION,
                        remaining=unresolved_decision,
                        detail=", ".join(reasons),
                        pages=pages,
                    )
                )
        comparison_missing = any(
            REASON_MISSING_COMPARISON
            in getattr(by_assessment.get(locator), "unresolved_reasons", ())
            for locator in locators
        )
        if comparison_missing and group.family == FAMILY_SALES_PER_SQUARE_FOOT:
            additional = _FAILURE_REMAINING["missing_comparison"][2]
            if not any(
                item["requirement"] == "historical_comparison"
                and item.get("cause") == CAUSE_SOURCE_ABSENCE
                for item in failures
            ):
                failures.append(
                    _failure_record(
                        requirement="historical_comparison",
                        cause=CAUSE_SOURCE_ABSENCE,
                        remaining=additional,
                        detail=REASON_MISSING_COMPARISON,
                        pages=pages,
                    )
                )
            if not primary:
                primary = CAUSE_SOURCE_ABSENCE
        if not primary and group.status != SELECTION_SELECTED:
            primary = CAUSE_AMBIGUITY
            unresolved_decision = "group remains deferred"
        level_eligibility = (
            LEVEL_ADMITTED
            if level_states and all(state == LEVEL_ADMITTED for state in level_states)
            else "deferred"
        )
        comparison_eligibility = (
            HISTORICAL_COMPARISON_ELIGIBLE
            if comparison_states
            and all(state == HISTORICAL_COMPARISON_ELIGIBLE for state in comparison_states)
            else "ineligible"
        )
        if comparison_eligibility == HISTORICAL_COMPARISON_ELIGIBLE:
            conflict_failures = [
                item
                for item in failures
                if item["requirement"] in {"calendar", "comparison_window", "definition"}
            ]
            if conflict_failures:
                comparison_eligibility = "ineligible"
        satisfied = sorted(set(satisfied))
        if comparison_eligibility != HISTORICAL_COMPARISON_ELIGIBLE:
            satisfied = [item for item in satisfied if item != "historical_comparison"]
        decisions.append(
            {
                "family": group.family,
                "metric_identity": group.metric_identity,
                "period": group.period,
                "status": group.status,
                "canonical_selection": group.status,
                "level_eligibility": level_eligibility,
                "comparison_eligibility": comparison_eligibility,
                "locators": locators,
                "evidence_consumed": consumed,
                "requirements_satisfied": satisfied,
                "remaining_failures": failures,
                "cause": primary or CAUSE_SELECTION,
                "pages_searched": sorted(set(pages)),
                "additional_evidence_needed": additional,
                "unresolved_decision": unresolved_decision,
                "selection_reasons": reasons,
            }
        )
    decisions.sort(
        key=lambda item: (
            item["family"],
            item["metric_identity"],
            item["period"],
            tuple(item["locators"]),
        )
    )
    return tuple(decisions)
