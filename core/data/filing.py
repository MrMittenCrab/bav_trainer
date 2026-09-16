"""Documentary extracted-filing contract (upstream of BAV accounting)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class PresentationRole(str, Enum):
    CURRENT_PERIOD = "current_period"
    COMPARATIVE = "comparative"
    RESTATED_COMPARATIVE = "restated_comparative"
    PRIOR_PRESENTATION = "prior_presentation"


ALLOWED_UNIT_SCALES = frozenset({"ones", "thousands", "millions", "billions"})
ALLOWED_DOCUMENT_TYPES = frozenset(
    {"annual_report", "interim_report", "results_announcement"}
)
ALLOWED_SUPPLEMENTAL_STATUS = frozenset({"reported", "derived"})
SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class FilingValue:
    value: float
    presentation_role: PresentationRole


@dataclass(frozen=True)
class SourceRef:
    page: int
    statement: str = ""
    note: str = ""
    label: str = ""


@dataclass(frozen=True)
class ExtractedStatementRow:
    label: str
    section: str
    suggested_concept: str
    values: dict[date, FilingValue]
    source: SourceRef


@dataclass(frozen=True)
class SupplementalFact:
    fact_type: str
    period: date
    value: float
    status: str
    source: SourceRef
    derivation: str = ""
    presentation_role: str = ""
    unit: str = ""


@dataclass(frozen=True)
class FilingMetadata:
    document_type: str
    fiscal_year: int
    period_end: date
    currency: str
    unit_scale: str
    source_file: str
    source_sha256: str = ""


@dataclass(frozen=True)
class ExtractedFiling:
    schema_version: str
    company_name: str
    ticker: str
    stock_code: str
    jurisdiction: str
    filing: FilingMetadata
    income_statement: tuple[ExtractedStatementRow, ...]
    balance_sheet: tuple[ExtractedStatementRow, ...]
    cash_flow: tuple[ExtractedStatementRow, ...]
    note_facts: tuple[SupplementalFact, ...]
    share_facts: tuple[SupplementalFact, ...]
