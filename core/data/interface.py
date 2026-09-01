"""Standardized financial data interface.

All ingestion adapters (manual HK documents, Excel exports, future HKEX/SEC
scrapers) must produce ``StandardizedFinancials``. The BAV engine and trainer
layers consume only this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class DocumentType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    INTERIM_REPORT = "interim_report"
    RESULTS_ANNOUNCEMENT = "results_announcement"
    EXCEL_EXPORT = "excel_export"
    BLOOMBERG_EXPORT = "bloomberg_export"
    WIND_EXPORT = "wind_export"
    OTHER = "other"


@dataclass
class DocumentManifest:
    """A manually supplied source document registered for extraction."""

    path: str
    doc_type: DocumentType
    period_end: date | None = None
    language: str = "en"
    notes: str = ""
    page_refs: dict[str, str] = field(default_factory=dict)


@dataclass
class FinancialPeriod:
    end_date: date
    label: str = ""
    is_interim: bool = False


@dataclass
class LineItem:
    label: str
    values: dict[date, float | None]
    concept: str = ""
    source_doc: str = ""
    source_page: str = ""


@dataclass
class StandardizedFinancials:
    """Canonical IS / BS / CF structure expected by the BAV engine."""

    ticker: str
    company_name: str
    currency: str
    units: str  # e.g. "HKD in Millions"
    jurisdiction: str  # e.g. "HK"
    stock_code: str = ""
    periods: list[FinancialPeriod] = field(default_factory=list)
    income_statement: list[LineItem] = field(default_factory=list)
    balance_sheet: list[LineItem] = field(default_factory=list)
    cash_flow: list[LineItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: list[dict[str, str]] = field(default_factory=list)

    def period_dates(self) -> list[date]:
        return [p.end_date for p in self.periods]

    def fiscal_years(self) -> list[date]:
        return [p.end_date for p in self.periods if not p.is_interim]


@dataclass
class ReconciliationReport:
    """Cross-document reconciliation audit trail."""

    conflicts: list[dict[str, Any]] = field(default_factory=list)
    resolutions: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checksums: dict[str, bool] = field(default_factory=dict)


class DataSourceAdapter(ABC):
    """Common adapter interface for all data sources."""

    jurisdiction: str = "HK"

    @abstractmethod
    def ingest(self, manifest: list[DocumentManifest]) -> StandardizedFinancials:
        """Extract and normalize financials from supplied documents."""

    @abstractmethod
    def reconcile(self, data: StandardizedFinancials) -> ReconciliationReport:
        """Validate checksums and resolve cross-document conflicts."""
