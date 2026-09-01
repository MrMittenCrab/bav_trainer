"""Base ingestion adapter with shared reconciliation hooks."""

from __future__ import annotations

from ..data.interface import (
    DataSourceAdapter,
    DocumentManifest,
    ReconciliationReport,
    StandardizedFinancials,
)
from .reconciler import reconcile_financials


class BaseIngestionAdapter(DataSourceAdapter):
    """Shared reconcile implementation for manual adapters."""

    def reconcile(self, data: StandardizedFinancials) -> ReconciliationReport:
        return reconcile_financials(data)
