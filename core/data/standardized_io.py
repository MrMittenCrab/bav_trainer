"""Model-only StandardizedFinancials JSON round-trip (no provenance/paths/formulas)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .historical_segments import validate_historical_segment
from .interface import (
    FinancialPeriod,
    HistoricalLeaseData,
    HistoricalSegmentData,
    HistoricalSegmentPeriod,
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


def _parse_segment_period(value: object) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(
            "historical_segment period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "historical_segment period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        ) from exc
    if parsed.isoformat() != value:
        raise ValueError(
            "historical_segment period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    return parsed


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
        "basis": shares.basis or "reported",
        "adjustment_factors": {
            _date_key(period): float(value)
            for period, value in (shares.adjustment_factors or {}).items()
        },
    }


def _deserialize_historical_shares(
    payload: object,
) -> HistoricalShareData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_shares must be an object or null")
    raw_factors = payload.get("adjustment_factors") or {}
    if not isinstance(raw_factors, dict):
        raise ValueError("historical_shares.adjustment_factors must be an object")
    return HistoricalShareData(
        scale_basis=str(payload.get("scale_basis") or ""),
        diluted_weighted_average={
            _parse_date(period): (None if value is None else float(value))
            for period, value in (
                payload.get("diluted_weighted_average") or {}
            ).items()
        },
        basis=str(payload.get("basis") or "reported"),
        adjustment_factors={
            _parse_date(period): float(value) for period, value in raw_factors.items()
        },
    )


def _serialize_historical_lease(
    lease: HistoricalLeaseData | None,
) -> dict[str, Any] | None:
    if lease is None:
        return None
    return {
        "lease_interest_expense": {
            _date_key(period): (None if value is None else float(value))
            for period, value in lease.lease_interest_expense.items()
        }
    }


def _deserialize_historical_lease(payload: object) -> HistoricalLeaseData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_lease must be an object or null")
    if "lease_interest_expense" not in payload or payload.get("lease_interest_expense") is None:
        series: object = {}
    else:
        series = payload.get("lease_interest_expense")
    if not isinstance(series, dict):
        raise ValueError("historical_lease.lease_interest_expense must be an object")
    return HistoricalLeaseData(
        lease_interest_expense={
            _parse_date(period): (None if value is None else float(value))
            for period, value in series.items()
        }
    )


def _serialize_historical_segment(
    data: HistoricalSegmentData | None,
) -> dict[str, Any] | None:
    if data is None:
        return None
    return {
        "namespace": data.namespace,
        "periods": [
            {
                "period": _date_key(snapshot.period),
                "presentation_family": snapshot.presentation_family,
                "values": {
                    identity: float(value)
                    for identity, value in sorted(snapshot.values.items())
                },
                "bridge_operations": {
                    identity: operation
                    for identity, operation in sorted(
                        snapshot.bridge_operations.items()
                    )
                },
            }
            for snapshot in data.periods
        ],
    }


def _deserialize_historical_segment_period(entry: object) -> HistoricalSegmentPeriod:
    if not isinstance(entry, dict):
        raise ValueError("historical_segment.periods entries must be objects")
    if "period" not in entry:
        raise ValueError("historical_segment period is required")
    raw_values = entry.get("values")
    if not isinstance(raw_values, dict):
        raise ValueError("historical_segment values must be an object")
    raw_operations = entry.get("bridge_operations")
    if not isinstance(raw_operations, dict):
        raise ValueError("historical_segment bridge_operations must be an object")
    period = _parse_segment_period(entry["period"])
    return HistoricalSegmentPeriod(
        period=period,
        presentation_family=str(entry.get("presentation_family") or ""),
        values={str(identity): value for identity, value in raw_values.items()},
        bridge_operations={
            str(identity): str(operation)
            for identity, operation in raw_operations.items()
        },
    )


def _deserialize_historical_segment(payload: object) -> HistoricalSegmentData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_segment must be an object or null")
    raw_periods = payload.get("periods")
    if not isinstance(raw_periods, list):
        raise ValueError("historical_segment.periods must be a list")
    return HistoricalSegmentData(
        namespace=str(payload.get("namespace") or ""),
        periods=[
            _deserialize_historical_segment_period(entry) for entry in raw_periods
        ],
    )


def standardized_to_payload(fin: StandardizedFinancials) -> dict:
    """Serialize model-relevant fields only (no source paths, provenance, or hints)."""
    validate_historical_segment(fin)
    payload = {
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
        "historical_lease": _serialize_historical_lease(fin.historical_lease),
    }
    serialized = _serialize_historical_segment(fin.historical_segment)
    if serialized is not None:
        payload["historical_segment"] = serialized
    return payload


def standardized_from_payload(payload: dict) -> StandardizedFinancials:
    """Reconstruct StandardizedFinancials from a model-only payload."""
    if not isinstance(payload, dict):
        raise ValueError("standardized payload must be an object")
    periods = [
        FinancialPeriod(
            end_date=_parse_date(entry["end_date"]),
            label=str(entry.get("label") or ""),
            is_interim=bool(entry.get("is_interim", False)),
        )
        for entry in payload.get("periods") or []
    ]
    fin = StandardizedFinancials(
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
        historical_lease=_deserialize_historical_lease(
            payload.get("historical_lease")
        ),
        historical_segment=_deserialize_historical_segment(
            payload["historical_segment"]
            if "historical_segment" in payload
            else None
        ),
    )
    validate_historical_segment(fin)
    return fin
