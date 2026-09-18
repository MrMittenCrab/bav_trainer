"""Stage an existing source-note handoff for normal source validation.

No facts are inferred here. The resulting extracted filings must still pass the
filing validator, source binding, reconciliation and family admission contracts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

KPI_PREFIX = "kpi.operating."


def load_store_facts(path: Path) -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError("store-KPI fixture must be a non-empty object")
    facts: dict[str, list[dict[str, Any]]] = {}
    for name, items in payload.items():
        if not isinstance(items, list) or not items:
            raise ValueError(f"store-KPI fixture {name} must be a non-empty list")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"store-KPI fixture {name} entries must be objects")
            fact_type = item.get("fact_type")
            if not isinstance(fact_type, str) or not fact_type.startswith(KPI_PREFIX):
                raise ValueError(
                    f"store-KPI fixture {name} has a non-KPI fact_type: {fact_type!r}"
                )
        facts[str(name)] = items
    return facts


def augment_extracted_filings(
    extracted_dir: Path,
    dest_dir: Path,
    facts_path: Path,
) -> list[Path]:
    """Write temporary copies with store-KPI note_facts appended."""
    extracted = Path(extracted_dir)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    facts_by_name = load_store_facts(facts_path)
    written: list[Path] = []
    for name, additions in sorted(facts_by_name.items()):
        source = extracted / name
        if not source.is_file():
            raise ValueError(f"extracted filing missing: {source}")
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"extracted filing must be an object: {source}")
        notes = payload.get("note_facts") or []
        if not isinstance(notes, list):
            raise ValueError(f"{name} note_facts must be an array")
        existing = {
            (item.get("fact_type"), item.get("period"))
            for item in notes
            if isinstance(item, dict)
        }
        for item in additions:
            key = (item.get("fact_type"), item.get("period"))
            if key in existing:
                raise ValueError(
                    f"{name} already has {item.get('fact_type')} for {item.get('period')}"
                )
            existing.add(key)
        payload["note_facts"] = [*notes, *additions]
        out = dest / name
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        written.append(out)
    return written

