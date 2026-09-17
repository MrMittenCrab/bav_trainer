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
class HistoricalShareData:
    """Explicit historical share-count inputs used by per-share schedules."""

    scale_basis: str = ""
    diluted_weighted_average: dict[date, float | None] = field(default_factory=dict)
    basis: str = "reported"  # "reported" | "split_adjusted"
    adjustment_factors: dict[date, float] = field(default_factory=dict)


@dataclass
class HistoricalLeaseData:
    """Explicit reported historical lease-note inputs used by lease treatment."""

    lease_interest_expense: dict[date, float | None] = field(default_factory=dict)


@dataclass
class HistoricalSegmentPeriod:
    """One admitted period's reported geographic snapshot."""

    period: date
    presentation_family: str = ""
    values: dict[str, float] = field(default_factory=dict)
    bridge_operations: dict[str, str] = field(default_factory=dict)


@dataclass
class HistoricalSegmentData:
    """Optional geographic-segment inputs used by historical analysis."""

    namespace: str = ""
    periods: list[HistoricalSegmentPeriod] = field(default_factory=list)


@dataclass
class HistoricalOperatingKpiObservation:
    """One source-grounded historical operating-KPI observation."""

    metric: str
    population: str
    period: date
    value: float
    unit: str


@dataclass
class HistoricalManagementKpiObservation:
    """One validated model-facing management-KPI history observation."""

    family: str
    entity_ticker: str
    entity_company: str
    geography: str
    population: str
    unit: str
    basis: str
    comparison: str
    period: date
    value: float
    definition_text: str
    period_kind: str
    calendar_week_adjustment: str
    calendar_reporting_basis: str
    qualifiers: dict[str, str] = field(default_factory=dict)


@dataclass
class HistoricalOperatingKpiData:
    """Optional historical operating-KPI inputs used by later analysis."""

    observations: list[HistoricalOperatingKpiObservation] = field(default_factory=list)
    management_observations: list[HistoricalManagementKpiObservation] = field(
        default_factory=list
    )


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
    historical_shares: HistoricalShareData | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: list[dict[str, str]] = field(default_factory=list)
    historical_lease: HistoricalLeaseData | None = None
    historical_segment: HistoricalSegmentData | None = None
    historical_operating_kpis: HistoricalOperatingKpiData | None = None

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
