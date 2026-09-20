"""Model-only StandardizedFinancials JSON round-trip (no provenance/paths/formulas)."""

from __future__ import annotations

from datetime import date, datetime
from dataclasses import MISSING, fields, is_dataclass
import math
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints

from .historical_operating_kpis import (
    MANAGEMENT_IDENTITY_FIELDS,
    management_identity_fields,
    require_management_observation_text_fields,
    validate_historical_operating_kpis,
)
from .historical_strategy import (
    deserialize_historical_strategy,
    serialize_historical_strategy,
    validate_historical_strategy,
)
from .historical_segments import validate_historical_segment
from .interface import (
    FinancialPeriod,
    HistoricalLeaseData,
    HistoricalManagementKpiObservation,
    HistoricalOperatingKpiData,
    HistoricalOperatingKpiObservation,
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


def _parse_kpi_period(value: object) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(
            "historical_operating_kpis period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "historical_operating_kpis period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        ) from exc
    if parsed.isoformat() != value:
        raise ValueError(
            "historical_operating_kpis period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    return parsed


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


_KPI_PAYLOAD_KEYS = frozenset({"observations", "management_observations"})
_MANAGEMENT_OBSERVATION_KEYS = frozenset(
    (
        *MANAGEMENT_IDENTITY_FIELDS,
        "period",
        "value",
        "definition_text",
        "period_kind",
        "calendar_week_adjustment",
        "calendar_reporting_basis",
        "qualifiers",
    )
)


def _json_number(value: object) -> int | float:
    amount = float(value)
    return int(amount) if amount.is_integer() else amount


def _serialize_management_qualifiers(qualifiers: dict[str, str]) -> dict[str, str]:
    return {str(key): str(value) for key, value in sorted(qualifiers.items())}


def _serialize_management_observation(
    item: HistoricalManagementKpiObservation,
) -> dict[str, Any]:
    fields = management_identity_fields(item)
    payload: dict[str, Any] = {key: fields[key] for key in MANAGEMENT_IDENTITY_FIELDS}
    payload.update(
        {
            "period": _date_key(item.period),
            "value": _json_number(item.value),
            "definition_text": item.definition_text,
            "period_kind": item.period_kind,
            "calendar_week_adjustment": item.calendar_week_adjustment,
            "calendar_reporting_basis": item.calendar_reporting_basis,
            "qualifiers": _serialize_management_qualifiers(item.qualifiers),
        }
    )
    return payload


def _management_sort_key(
    item: HistoricalManagementKpiObservation,
) -> tuple[str, ...]:
    fields = management_identity_fields(item)
    return tuple(fields[key] for key in MANAGEMENT_IDENTITY_FIELDS) + (
        _date_key(item.period),
    )


def _serialize_historical_operating_kpis(
    data: HistoricalOperatingKpiData | None,
) -> dict[str, Any] | None:
    if data is None:
        return None
    payload: dict[str, Any] = {
        "observations": [
            {
                "metric": item.metric,
                "population": item.population,
                "period": _date_key(item.period),
                "value": _json_number(item.value),
                "unit": item.unit,
            }
            for item in sorted(
                data.observations,
                key=lambda row: (row.metric, row.population, _date_key(row.period)),
            )
        ]
    }
    if data.management_observations:
        payload["management_observations"] = [
            _serialize_management_observation(item)
            for item in sorted(data.management_observations, key=_management_sort_key)
        ]
    return payload


def _deserialize_historical_operating_kpi_observation(
    entry: object,
) -> HistoricalOperatingKpiObservation:
    if not isinstance(entry, dict):
        raise ValueError("historical_operating_kpis.observations entries must be objects")
    if "period" not in entry:
        raise ValueError("historical_operating_kpis period is required")
    if "metric" not in entry:
        raise ValueError("historical_operating_kpis metric is required")
    if "population" not in entry:
        raise ValueError("historical_operating_kpis population is required")
    if "value" not in entry:
        raise ValueError("historical_operating_kpis value is required")
    if "unit" not in entry:
        raise ValueError("historical_operating_kpis unit is required")
    return HistoricalOperatingKpiObservation(
        metric=str(entry.get("metric") or ""),
        population=str(entry.get("population") or ""),
        period=_parse_kpi_period(entry["period"]),
        value=entry["value"],
        unit=str(entry.get("unit") or ""),
    )


def _deserialize_management_qualifiers(payload: object, *, identity: str) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise ValueError(
            f"historical_operating_kpis.management_observations {identity} "
            "qualifiers must be an object"
        )
    qualifiers: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not key:
            raise ValueError(
                "historical_operating_kpis.management_observations qualifier keys "
                "must be strings"
            )
        if not isinstance(value, str):
            raise ValueError(
                "historical_operating_kpis.management_observations qualifier "
                f"{key!r} must be a string"
            )
        qualifiers[key] = value
    return qualifiers


def _deserialize_management_observation(
    entry: object,
) -> HistoricalManagementKpiObservation:
    if not isinstance(entry, dict):
        raise ValueError(
            "historical_operating_kpis.management_observations entries must be objects"
        )
    unknown = entry.keys() - _MANAGEMENT_OBSERVATION_KEYS
    if unknown:
        raise ValueError(
            "historical_operating_kpis.management_observations unsupported field(s): "
            + ", ".join(sorted(unknown))
        )
    missing = _MANAGEMENT_OBSERVATION_KEYS - entry.keys()
    if missing:
        raise ValueError(
            "historical_operating_kpis.management_observations missing field(s): "
            + ", ".join(sorted(missing))
        )
    texts = require_management_observation_text_fields(entry)
    return HistoricalManagementKpiObservation(
        family=texts["family"],
        entity_ticker=texts["entity_ticker"],
        entity_company=texts["entity_company"],
        geography=texts["geography"],
        population=texts["population"],
        unit=texts["unit"],
        basis=texts["basis"],
        comparison=texts["comparison"],
        period=_parse_kpi_period(entry["period"]),
        value=entry["value"],
        definition_text=texts["definition_text"],
        period_kind=texts["period_kind"],
        calendar_week_adjustment=texts["calendar_week_adjustment"],
        calendar_reporting_basis=texts["calendar_reporting_basis"],
        qualifiers=_deserialize_management_qualifiers(
            entry.get("qualifiers"),
            identity=texts["family"] or "management",
        ),
    )


def _deserialize_observation_list(payload: dict[str, Any], *, field: str) -> list:
    if field not in payload:
        return []
    raw = payload[field]
    if not isinstance(raw, list):
        raise ValueError(f"historical_operating_kpis.{field} must be a list")
    return raw


def _deserialize_historical_operating_kpis(
    payload: object,
) -> HistoricalOperatingKpiData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_operating_kpis must be an object or null")
    unknown = payload.keys() - _KPI_PAYLOAD_KEYS
    if unknown:
        raise ValueError(
            "historical_operating_kpis: unsupported field(s): "
            + ", ".join(sorted(unknown))
        )
    raw_obs = _deserialize_observation_list(payload, field="observations")
    raw_mgmt = _deserialize_observation_list(payload, field="management_observations")
    return HistoricalOperatingKpiData(
        observations=[
            _deserialize_historical_operating_kpi_observation(entry) for entry in raw_obs
        ],
        management_observations=[
            _deserialize_management_observation(entry) for entry in raw_mgmt
        ],
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
    validate_historical_operating_kpis(fin)
    validate_historical_strategy(fin)
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
    serialized_kpis = _serialize_historical_operating_kpis(fin.historical_operating_kpis)
    if serialized_kpis is not None:
        payload["historical_operating_kpis"] = serialized_kpis
    serialized_strategy = serialize_historical_strategy(fin.historical_strategy)
    if serialized_strategy is not None:
        payload["historical_strategy"] = serialized_strategy
    return payload


def _jurisdiction_fallback_needed(payload: dict) -> bool:
    """True when top-level jurisdiction is missing or an empty string."""
    if "jurisdiction" not in payload:
        return True
    return payload.get("jurisdiction") == ""


def _fallback_jurisdiction_from_metadata(
    payload: dict, *, path: str = "standardized"
) -> str:
    """Return metadata.jurisdiction as a canonical string, or "".

    Validates the fallback against the jurisdiction string contract before
    coercion. Missing, null, and empty values yield "" so the existing
    required-field contract is unchanged.
    """
    raw_metadata = payload.get("metadata")
    if not isinstance(raw_metadata, dict) or "jurisdiction" not in raw_metadata:
        return ""
    fallback = raw_metadata["jurisdiction"]
    if fallback is None or fallback == "":
        return ""
    if type(fallback) is not str:
        raise ValueError(f"{path}.metadata.jurisdiction must be str")
    return fallback


def _validate_canonical_value(value: object, expected: object, path: str) -> None:
    """Validate JSON against the model types, without coercion or unknown fields.

    Deriving the shape from the canonical dataclasses keeps new historical
    modules on the same path. Source/audit metadata is deliberately outside
    the model-only serialization contract.
    """
    if expected is Any:
        return
    origin, args = get_origin(expected), get_args(expected)
    if origin is UnionType:
        if value is None and type(None) in args:
            return
        expected = next(item for item in args if item is not type(None))
        return _validate_canonical_value(value, expected, path)
    if is_dataclass(expected):
        if not isinstance(value, dict):
            raise ValueError(f"{path} must be an object")
        excluded = {"metadata", "provenance", "source_doc", "source_page"}
        model_fields = {f.name: f for f in fields(expected) if f.name not in excluded}
        unknown = value.keys() - model_fields.keys()
        if expected is StandardizedFinancials:
            # Top-level metadata is a supported identity-bearing model field.
            # Nested source/audit metadata on other objects remains excluded.
            unknown -= {"metadata"}
            raw_metadata = value.get("metadata")
            if raw_metadata is not None and not isinstance(raw_metadata, dict):
                raise ValueError(f"{path}.metadata must be an object")
        else:
            raw_metadata = None
        if unknown:
            raise ValueError(f"{path}: unsupported field(s): {', '.join(sorted(unknown))}")
        required = {name for name, f in model_fields.items()
                    if f.default is MISSING and f.default_factory is MISSING}
        if expected is StandardizedFinancials:
            required.update(("periods", "income_statement", "balance_sheet", "cash_flow"))
            if _jurisdiction_fallback_needed(value):
                fallback = _fallback_jurisdiction_from_metadata(value, path=path)
                if fallback:
                    required.discard("jurisdiction")
        missing = required - value.keys()
        if missing:
            raise ValueError(f"{path}: missing field(s): {', '.join(sorted(missing))}")
        hints = get_type_hints(expected)
        for key, item in value.items():
            _validate_canonical_value(item, hints[key], f"{path}.{key}")
        return
    if origin is list:
        if not isinstance(value, list):
            raise ValueError(f"{path} must be a list")
        for index, item in enumerate(value):
            _validate_canonical_value(item, args[0], f"{path}[{index}]")
        return
    if origin is dict:
        if not isinstance(value, dict):
            raise ValueError(f"{path} must be an object")
        for key, item in value.items():
            _validate_canonical_value(key, args[0], f"{path} key {key!r}")
            _validate_canonical_value(item, args[1], f"{path}.{key}")
        return
    if expected is date:
        try:
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError
        except ValueError as exc:
            raise ValueError(f"{path} must be a canonical YYYY-MM-DD date") from exc
    elif expected is float:
        try:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError
        except (ValueError, OverflowError) as exc:
            raise ValueError(f"{path} must be a finite number") from exc
    elif type(value) is not expected:
        raise ValueError(f"{path} must be {expected.__name__}")


def standardized_from_payload(payload: dict, *, strict: bool = False) -> StandardizedFinancials:
    """Reconstruct the complete model; strict mode rejects lossy JSON coercions.

    Existing internal round-trip callers retain their compatibility behavior.
    User-supplied manual builds use strict mode before any workbook writes.
    """
    if not isinstance(payload, dict):
        raise ValueError("standardized payload must be an object")
    if strict:
        _validate_canonical_value(payload, StandardizedFinancials, "standardized")
        if not payload["periods"]:
            raise ValueError("standardized.periods must not be empty")
        dates = [entry["end_date"] for entry in payload["periods"]]
        if len(dates) != len(set(dates)):
            raise ValueError("standardized.periods contains duplicate end_date values")
    periods = [
        FinancialPeriod(
            end_date=_parse_date(entry["end_date"]),
            label=str(entry.get("label") or ""),
            is_interim=bool(entry.get("is_interim", False)),
        )
        for entry in payload.get("periods") or []
    ]
    raw_metadata = payload.get("metadata")
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
    jurisdiction = str(payload.get("jurisdiction") or "")
    if not jurisdiction:
        jurisdiction = _fallback_jurisdiction_from_metadata(payload)
    fin = StandardizedFinancials(
        ticker=str(payload.get("ticker") or ""),
        company_name=str(payload.get("company_name") or ""),
        currency=str(payload.get("currency") or ""),
        units=str(payload.get("units") or ""),
        jurisdiction=jurisdiction,
        stock_code=str(payload.get("stock_code") or ""),
        metadata=dict(metadata),
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
        historical_operating_kpis=_deserialize_historical_operating_kpis(
            payload["historical_operating_kpis"]
            if "historical_operating_kpis" in payload
            else None
        ),
        historical_strategy=deserialize_historical_strategy(
            payload["historical_strategy"]
            if "historical_strategy" in payload
            else None
        ),
    )
    validate_historical_segment(fin)
    validate_historical_operating_kpis(fin)
    validate_historical_strategy(fin)
    return fin
