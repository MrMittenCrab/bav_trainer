"""Optional source-bound management strategy and operating-use disclosures.

Issuer statements live in company inputs. Analytical methods stay generic.
Missing payloads keep the revenue-driver module absent. This is not an
extraction or research framework.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

THEME_STORE_EXPANSION = "store_expansion"
THEME_COMPARABLE_SALES = "comparable_sales"
THEME_PRODUCTIVITY = "productivity"
THEME_GEOGRAPHIC_GROWTH = "geographic_growth"
SUPPORTED_THEMES = (
    THEME_STORE_EXPANSION,
    THEME_COMPARABLE_SALES,
    THEME_PRODUCTIVITY,
    THEME_GEOGRAPHIC_GROWTH,
)
ROLE_STRATEGY = "strategy"
ROLE_OBJECTIVE = "objective"
ROLE_OPERATING_USE = "operating_use"
SUPPORTED_ROLES = (ROLE_STRATEGY, ROLE_OBJECTIVE, ROLE_OPERATING_USE)
_REQUIRED_FIELDS = (
    "theme",
    "role",
    "text",
    "period",
    "source_file",
    "page_reference",
    "section",
)


@dataclass(frozen=True)
class HistoricalStrategyDisclosure:
    """One source-bound management statement with a documentary locator."""

    theme: str
    role: str
    text: str
    period: date
    source_file: str
    page_reference: str
    section: str


@dataclass(frozen=True)
class HistoricalStrategyData:
    """Optional strategy/operating-use disclosures used by revenue-driver tests."""

    disclosures: tuple[HistoricalStrategyDisclosure, ...] = ()


def _require_text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"historical_strategy.{field} must be non-empty text")
    return value.strip()


def _parse_period(value: object) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(
            "historical_strategy period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "historical_strategy period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        ) from exc
    if parsed.isoformat() != value:
        raise ValueError(
            "historical_strategy period must be a canonical YYYY-MM-DD date: "
            f"{value!r}"
        )
    return parsed


def _deserialize_disclosure(payload: object) -> HistoricalStrategyDisclosure:
    if not isinstance(payload, dict):
        raise ValueError("historical_strategy.disclosures entries must be objects")
    unknown = payload.keys() - set(_REQUIRED_FIELDS)
    if unknown:
        raise ValueError(
            "historical_strategy.disclosures unsupported field(s): "
            + ", ".join(sorted(unknown))
        )
    missing = [field for field in _REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(
            "historical_strategy.disclosures missing field(s): "
            + ", ".join(missing)
        )
    theme = _require_text(payload["theme"], field="theme")
    role = _require_text(payload["role"], field="role")
    if theme not in SUPPORTED_THEMES:
        raise ValueError(f"historical_strategy.theme is not supported: {theme!r}")
    if role not in SUPPORTED_ROLES:
        raise ValueError(f"historical_strategy.role is not supported: {role!r}")
    return HistoricalStrategyDisclosure(
        theme=theme,
        role=role,
        text=_require_text(payload["text"], field="text"),
        period=_parse_period(payload["period"]),
        source_file=_require_text(payload["source_file"], field="source_file"),
        page_reference=_require_text(payload["page_reference"], field="page_reference"),
        section=_require_text(payload["section"], field="section"),
    )


def deserialize_historical_strategy(payload: object) -> HistoricalStrategyData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_strategy must be an object or null")
    unknown = payload.keys() - {"disclosures"}
    if unknown:
        raise ValueError(
            "historical_strategy: unsupported field(s): "
            + ", ".join(sorted(unknown))
        )
    raw = payload.get("disclosures")
    if not isinstance(raw, list) or not raw:
        raise ValueError("historical_strategy.disclosures must be a non-empty list")
    return HistoricalStrategyData(
        disclosures=tuple(_deserialize_disclosure(entry) for entry in raw)
    )


def serialize_historical_strategy(
    data: HistoricalStrategyData | None,
) -> dict[str, Any] | None:
    if data is None:
        return None
    if not data.disclosures:
        return None
    return {
        "disclosures": [
            {
                "theme": item.theme,
                "role": item.role,
                "text": item.text,
                "period": item.period.isoformat(),
                "source_file": item.source_file,
                "page_reference": item.page_reference,
                "section": item.section,
            }
            for item in data.disclosures
        ]
    }


def load_strategy_disclosures(path: Path) -> HistoricalStrategyData:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    loaded = deserialize_historical_strategy(payload)
    if loaded is None:
        raise ValueError(f"strategy disclosure file is empty: {path}")
    return loaded


def validate_historical_strategy(financials) -> None:
    data = getattr(financials, "historical_strategy", None)
    if data is None:
        return
    if not isinstance(data, HistoricalStrategyData):
        raise ValueError("historical_strategy must be HistoricalStrategyData or null")
    if not data.disclosures:
        raise ValueError("historical_strategy.disclosures must be a non-empty list")
    serialized = serialize_historical_strategy(data)
    restored = deserialize_historical_strategy(serialized)
    if restored != data:
        raise ValueError("historical_strategy round-trip identity failed")
