"""Model-only StandardizedFinancials JSON round-trip (no provenance/paths/formulas)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .interface import FinancialPeriod, LineItem, StandardizedFinancials


def _date_key(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _parse_date(value: str) -> date:
    return date.fromisoformat(str(value)[:10])


def _serialize_line(item: LineItem) -> dict[str, Any]:
    return {
        "label": item.label,
        "concept": item.concept or "",
        "values": {
            _date_key(period): (None if amount is None else float(amount))
            for period, amount in item.values.items()
        },
    }


def _deserialize_line(payload: dict[str, Any]) -> LineItem:
    values = {
        _parse_date(period): (None if amount is None else float(amount))
        for period, amount in (payload.get("values") or {}).items()
    }
    return LineItem(
        label=str(payload.get("label") or ""),
        concept=str(payload.get("concept") or ""),
        values=values,
    )


def standardized_to_payload(fin: StandardizedFinancials) -> dict:
    """Serialize model-relevant fields only (no source paths, provenance, or hints)."""
    return {
        "ticker": fin.ticker,
        "company_name": fin.company_name,
        "currency": fin.currency,
        "units": fin.units,
        "jurisdiction": fin.jurisdiction,
        "stock_code": fin.stock_code or "",
        "periods": [
            {
                "end_date": _date_key(period.end_date),
                "label": period.label,
                "is_interim": bool(period.is_interim),
            }
            for period in fin.periods
        ],
        "income_statement": [_serialize_line(item) for item in fin.income_statement],
        "balance_sheet": [_serialize_line(item) for item in fin.balance_sheet],
        "cash_flow": [_serialize_line(item) for item in fin.cash_flow],
    }


def standardized_from_payload(payload: dict) -> StandardizedFinancials:
    """Reconstruct StandardizedFinancials from a model-only payload."""
    periods = [
        FinancialPeriod(
            end_date=_parse_date(entry["end_date"]),
            label=str(entry.get("label") or ""),
            is_interim=bool(entry.get("is_interim", False)),
        )
        for entry in payload.get("periods") or []
    ]
    return StandardizedFinancials(
        ticker=str(payload.get("ticker") or ""),
        company_name=str(payload.get("company_name") or ""),
        currency=str(payload.get("currency") or ""),
        units=str(payload.get("units") or ""),
        jurisdiction=str(payload.get("jurisdiction") or ""),
        stock_code=str(payload.get("stock_code") or ""),
        periods=periods,
        income_statement=[_deserialize_line(item) for item in payload.get("income_statement") or []],
        balance_sheet=[_deserialize_line(item) for item in payload.get("balance_sheet") or []],
        cash_flow=[_deserialize_line(item) for item in payload.get("cash_flow") or []],
    )
