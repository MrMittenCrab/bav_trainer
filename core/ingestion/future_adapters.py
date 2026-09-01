"""Future automated source adapters — stub implementations.

Implement DataSourceAdapter for each jurisdiction. The BAV engine and trainer
layers consume StandardizedFinancials only; adapters are swappable.
"""

from __future__ import annotations

from ..data.interface import DataSourceAdapter, DocumentManifest, ReconciliationReport, StandardizedFinancials
from .reconciler import reconcile_financials


class HKEXAdapter(DataSourceAdapter):
    """Future: HKEXnews automated filing fetch. Not implemented in v1."""

    jurisdiction = "HK"

    def ingest(self, manifest: list[DocumentManifest]) -> StandardizedFinancials:
        raise NotImplementedError(
            "HKEX automated scraping is not available in v1. "
            "Use HKManualDocumentAdapter with transcribed JSON/Excel."
        )

    def reconcile(self, data: StandardizedFinancials) -> ReconciliationReport:
        return reconcile_financials(data)


class SECAdapter(DataSourceAdapter):
    """Future: wrap existing edgartools pipeline behind StandardizedFinancials."""

    jurisdiction = "US"

    def ingest(self, manifest: list[DocumentManifest]) -> StandardizedFinancials:
        raise NotImplementedError(
            "Use the existing bav-pipeline Stage 2 Assembler for SEC tickers. "
            "This adapter will bridge edgartools output to StandardizedFinancials."
        )

    def reconcile(self, data: StandardizedFinancials) -> ReconciliationReport:
        return reconcile_financials(data)


class SGXAdapter(DataSourceAdapter):
    """Future: SGX automated filing fetch."""

    jurisdiction = "SG"

    def ingest(self, manifest: list[DocumentManifest]) -> StandardizedFinancials:
        raise NotImplementedError("SGX adapter not implemented.")

    def reconcile(self, data: StandardizedFinancials) -> ReconciliationReport:
        return reconcile_financials(data)
