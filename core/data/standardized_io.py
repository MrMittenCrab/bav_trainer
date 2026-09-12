"""Model-only StandardizedFinancials JSON round-trip (no provenance/paths/formulas)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .interface import (
    FinancialPeriod,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
)


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


def _serialize_historical_shares(
    shares: HistoricalShareData | None,
) -> dict[str, Any] | None:
    if shares is None:
        return None
    return {
        "scale_basis": shares.scale_basis,
        "diluted_weighted_average": {
            _date_key(period): (None if value is None else float(value))
            for period, value in shares.diluted_weighted_average.items()
        },
    }


def _deserialize_historical_shares(
    payload: object,
) -> HistoricalShareData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_shares must be an object or null")
    return HistoricalShareData(
        scale_basis=str(payload.get("scale_basis") or ""),
        diluted_weighted_average={
            _parse_date(period): (None if value is None else float(value))
            for period, value in (
                payload.get("diluted_weighted_average") or {}
            ).items()
        },
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
        "historical_shares": _serialize_historical_shares(fin.historical_shares),
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
        income_statement=[
            _deserialize_line(item) for item in payload.get("income_statement") or []
        ],
        balance_sheet=[
            _deserialize_line(item) for item in payload.get("balance_sheet") or []
        ],
        cash_flow=[_deserialize_line(item) for item in payload.get("cash_flow") or []],
        historical_shares=_deserialize_historical_shares(
            payload.get("historical_shares")
        ),
    )
