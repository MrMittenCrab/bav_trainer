"""Hong Kong manual document input adapter (v1).

Accepts:
  1. Structured JSON/YAML mapping files with extracted line items
  2. Excel workbooks with IS/BS/CF tabs (annual/interim reports transcribed)
  3. Document manifest listing PDFs/HTML for human-or-LLM-assisted extraction

No automatic HKEX scraping in v1 — documents are manually supplied. The adapter
normalizes into StandardizedFinancials behind the common interface.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from ..data.interface import (
    DocumentManifest,
    DocumentType,
    FinancialPeriod,
    LineItem,
    StandardizedFinancials,
)
from ..data.schema import normalize_label
from .base import BaseIngestionAdapter
from .excel_import import ExcelExportAdapter


def _parse_date(raw: str | date) -> date:
    if isinstance(raw, date):
        return raw
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {raw!r}")


def _load_structured_json(path: Path) -> StandardizedFinancials:
    payload = json.loads(path.read_text(encoding="utf-8"))
    periods = [
        FinancialPeriod(
            end_date=_parse_date(p["end_date"]),
            label=p.get("label", ""),
            is_interim=p.get("is_interim", False),
        )
        for p in payload["periods"]
    ]
    period_dates = [p.end_date for p in periods]

    def load_items(key: str) -> list[LineItem]:
        items: list[LineItem] = []
        for row in payload.get(key, []):
            values = {}
            for pd in period_dates:
                raw = row.get("values", {}).get(pd.isoformat())
                if raw is None:
                    raw = row.get("values", {}).get(str(pd.year))
                values[pd] = raw
            items.append(
                LineItem(
                    label=normalize_label(row["label"]),
                    values=values,
                    concept=row.get("concept", ""),
                    source_doc=str(path),
                    source_page=row.get("page", ""),
                )
            )
        return items

    return StandardizedFinancials(
        ticker=payload["ticker"],
        company_name=payload.get("company_name", payload["ticker"]),
        currency=payload.get("currency", "HKD"),
        units=payload.get("units", "HKD in Millions"),
        jurisdiction="HK",
        stock_code=payload.get("stock_code", ""),
        periods=periods,
        income_statement=load_items("income_statement"),
        balance_sheet=load_items("balance_sheet"),
        cash_flow=load_items("cash_flow"),
        metadata=payload.get("metadata", {}),
        provenance=[{"source": str(path), "type": "structured_json"}],
    )


class HKManualDocumentAdapter(BaseIngestionAdapter):
    """Manual HK document ingestion — structured JSON, Excel, or manifest-driven."""

    jurisdiction = "HK"

    def ingest(self, manifest: list[DocumentManifest]) -> StandardizedFinancials:
        if not manifest:
            raise ValueError("At least one document is required")

        result: StandardizedFinancials | None = None
        excel_adapter = ExcelExportAdapter()

        for doc in manifest:
            path = Path(doc.path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {path}")

            if path.suffix.lower() in (".json",):
                data = _load_structured_json(path)
            elif path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
                data = excel_adapter.ingest([doc])
            elif path.suffix.lower() in (".yaml", ".yml"):
                try:
                    import yaml  # optional dependency
                except ImportError as exc:
                    raise ImportError("PyYAML required for YAML manifests: pip install pyyaml") from exc
                payload = yaml.safe_load(path.read_text(encoding="utf-8"))
                tmp = path.with_suffix(".json")
                tmp.write_text(json.dumps(payload), encoding="utf-8")
                try:
                    data = _load_structured_json(tmp)
                finally:
                    tmp.unlink(missing_ok=True)
            elif doc.doc_type in (
                DocumentType.ANNUAL_REPORT,
                DocumentType.INTERIM_REPORT,
                DocumentType.RESULTS_ANNOUNCEMENT,
            ):
                raise ValueError(
                    f"PDF/HTML extraction not automated in v1: {path.name}. "
                    "Transcribe into structured JSON or Excel first, or use Claude "
                    "with the bav-trainer skill to assist extraction."
                )
            else:
                raise ValueError(f"Unsupported document type: {path}")

            if result is None:
                result = data
            else:
                from .reconciler import merge_documents
                merge_documents(result, data, str(path))

        assert result is not None
        return result
