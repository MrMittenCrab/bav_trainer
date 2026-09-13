#!/usr/bin/env python3
"""Build Fast Retailing model-only standardized JSON + separate provenance.

Deterministic latest-audited-presentation precedence across FY2021–FY2025 filings.
No production accounting logic; benchmark-only.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_FACTS = ROOT / "benchmark" / "fast_retailing" / "source_facts.json"
DEFAULT_OUT_STD = ROOT / "benchmark" / "fast_retailing" / "FastRetailing_Standardized.json"
DEFAULT_OUT_PROV = ROOT / "benchmark" / "fast_retailing" / "provenance.json"

PERIODS = [
    date(2021, 8, 31),
    date(2022, 8, 31),
    date(2023, 8, 31),
    date(2024, 8, 31),
    date(2025, 8, 31),
]
PERIOD_KEYS = [p.isoformat() for p in PERIODS]

STATEMENT_KEYS = ("income_statement", "balance_sheet", "cash_flow")


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def _row_identity(row: dict[str, Any]) -> str:
    concept = str(row.get("concept") or "").strip()
    label = str(row.get("label") or "").strip()
    return f"concept={concept}|label={label.casefold()}"


def build_benchmark(
    source_facts_path: Path,
) -> tuple[dict, dict]:
    """Return (model_payload, provenance_payload)."""
    source = json.loads(source_facts_path.read_text(encoding="utf-8"))
    filings = source["filings"]

    # Map: statement -> identity -> period -> list of (filing_year, value, page, file, label, concept)
    observations: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {
        key: {} for key in STATEMENT_KEYS
    }
    note_observations: list[dict[str, Any]] = []
    share_observations: list[dict[str, Any]] = []

    for year_str, filing in sorted(filings.items(), key=lambda kv: int(kv[0])):
        year = int(year_str)
        file_path = filing["file"]
        for statement in STATEMENT_KEYS:
            for row in filing.get(statement, []):
                ident = _row_identity(row)
                bucket = observations[statement].setdefault(ident, {})
                for period_key, value in (row.get("values") or {}).items():
                    if period_key not in PERIOD_KEYS:
                        # Allow FY2020 comparative only as observation, not in model axis
                        if not (period_key.endswith("-08-31") and 2020 <= int(period_key[:4]) <= 2025):
                            continue
                    if period_key not in PERIOD_KEYS:
                        continue
                    bucket.setdefault(period_key, []).append(
                        {
                            "filing_year": year,
                            "value": value,
                            "pdf_page": row.get("pdf_page"),
                            "file": file_path,
                            "label": row.get("label"),
                            "concept": row.get("concept") or "",
                            "statement": row.get("statement") or statement,
                            "status": row.get("status") or "reported",
                        }
                    )
        for fact in filing.get("note_facts", []):
            note_observations.append(
                {
                    "filing_year": year,
                    "file": file_path,
                    **deepcopy(fact),
                }
            )
        for fact in filing.get("share_facts", []):
            share_observations.append(
                {
                    "filing_year": year,
                    "file": file_path,
                    **deepcopy(fact),
                }
            )

    conflicts: list[dict[str, Any]] = []
    chosen_lines: dict[str, list[dict[str, Any]]] = {key: [] for key in STATEMENT_KEYS}
    provenance_values: dict[str, Any] = {}

    for statement in STATEMENT_KEYS:
        # Preserve stable order by first appearance in latest filing, then earlier
        ordered_idents: list[str] = []
        seen: set[str] = set()
        for year_str in sorted(filings.keys(), key=lambda y: int(y), reverse=True):
            for row in filings[year_str].get(statement, []):
                ident = _row_identity(row)
                if ident not in seen:
                    seen.add(ident)
                    ordered_idents.append(ident)
        # Also include any remaining identities only in older filings
        for ident in observations[statement]:
            if ident not in seen:
                ordered_idents.append(ident)

        for ident in ordered_idents:
            period_map = observations[statement][ident]
            values: dict[str, float] = {}
            label = ""
            concept = ""
            for period_key in PERIOD_KEYS:
                obs = period_map.get(period_key) or []
                if not obs:
                    continue
                # Sort oldest->newest for conflict scan; choose latest
                obs_sorted = sorted(obs, key=lambda o: o["filing_year"])
                chosen = obs_sorted[-1]
                for older in obs_sorted[:-1]:
                    if older["value"] != chosen["value"]:
                        conflicts.append(
                            {
                                "period": period_key,
                                "line_identity": ident,
                                "statement": statement,
                                "older_filing": older["filing_year"],
                                "older_value": older["value"],
                                "newer_filing": chosen["filing_year"],
                                "newer_value": chosen["value"],
                                "chosen_filing": chosen["filing_year"],
                                "chosen_value": chosen["value"],
                                "reason": (
                                    "latest_audited_presentation_after_overlap_conflict"
                                ),
                            }
                        )
                values[period_key] = chosen["value"]
                label = str(chosen["label"] or label)
                concept = str(chosen["concept"] or concept)
                provenance_values[f"{statement}|{ident}|{period_key}"] = {
                    "statement": statement,
                    "line_identity": ident,
                    "period": period_key,
                    "label": chosen["label"],
                    "concept": chosen["concept"],
                    "value": chosen["value"],
                    "file": chosen["file"],
                    "pdf_page": chosen["pdf_page"],
                    "filing_year": chosen["filing_year"],
                    "status": chosen["status"],
                    "selection_rule": "latest_audited_presentation",
                }
            if not values:
                continue
            # Require full five-year coverage for model emission; partial rows stay in provenance only
            if set(values) != set(PERIOD_KEYS):
                provenance_values[f"{statement}|{ident}|__coverage__"] = {
                    "statement": statement,
                    "line_identity": ident,
                    "label": label,
                    "concept": concept,
                    "available_periods": sorted(values),
                    "status": "omitted_incomplete_five_year_axis",
                }
                continue
            chosen_lines[statement].append(
                {
                    "label": label,
                    "concept": concept,
                    "values": {k: float(values[k]) for k in PERIOD_KEYS},
                }
            )

    # Share module: omit five-year historical_shares — 2021/2022 not clearly
    # restated onto post 3-for-1 basis in the supplied audited extracts.
    share_provenance = {
        "decision": "omit_historical_shares_from_five_year_model",
        "reason": (
            "3-for-1 stock split effective 1 March 2023; FY2021/FY2022 audited "
            "share counts in the supplied filings are not treated as a clearly "
            "restated comparable five-year diluted WAS series without inventing "
            "an undocumented multiplier."
        ),
        "observations": share_observations,
        "fy2025_derived_diluted_was": 307_247_804,
        "fy2025_basic_was": 306_786_602,
        "fy2025_dilutive": 461_202,
    }

    note_provenance = {
        "observations": note_observations,
        "fy2025_anchors": {
            "aggregate_lease_liability": 513_501,
            "lease_interest_expense": 8_464,
            "parent_profit_plus_nci_vs_total": {
                "total_profit": 459_153,
                "parent": 433_009,
                "nci": 26_143,
                "sum": 433_009 + 26_143,
                "difference_units": 459_153 - (433_009 + 26_143),
            },
            "lease_current_plus_noncurrent_vs_note": {
                "current": 126_830,
                "noncurrent": 386_670,
                "sum": 126_830 + 386_670,
                "note_aggregate": 513_501,
                "difference_units": 513_501 - (126_830 + 386_670),
            },
        },
    }

    model_payload = {
        "ticker": "6288.HK",
        "company_name": "FAST RETAILING CO., LTD.",
        "stock_code": "6288.HK",
        "currency": "JPY",
        "units": "JPY in Millions",
        "jurisdiction": "JP",
        "periods": [
            {"end_date": key, "label": f"FY{key[:4]}"} for key in PERIOD_KEYS
        ],
        "income_statement": chosen_lines["income_statement"],
        "balance_sheet": chosen_lines["balance_sheet"],
        "cash_flow": chosen_lines["cash_flow"],
        "historical_shares": None,
        "metadata": {
            "benchmark": "fast_retailing",
            "step": "9M.0",
            "source_facts": str(source_facts_path.relative_to(ROOT)),
        },
    }

    provenance_payload = {
        "company": source.get("company"),
        "hk_stock_code": source.get("hk_stock_code"),
        "selection_rule": "latest_audited_presentation",
        "periods": PERIOD_KEYS,
        "conflicts": conflicts,
        "values": provenance_values,
        "notes": note_provenance,
        "shares": share_provenance,
        "overlap_conflict_count": len(conflicts),
    }
    return model_payload, provenance_payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-facts", type=Path, default=DEFAULT_SOURCE_FACTS)
    parser.add_argument("--out-standardized", type=Path, default=DEFAULT_OUT_STD)
    parser.add_argument("--out-provenance", type=Path, default=DEFAULT_OUT_PROV)
    args = parser.parse_args()

    model, provenance = build_benchmark(args.source_facts)
    args.out_standardized.write_text(_dump(model), encoding="utf-8")
    args.out_provenance.write_text(_dump(provenance), encoding="utf-8")
    print(f"wrote {args.out_standardized.relative_to(ROOT)}")
    print(f"wrote {args.out_provenance.relative_to(ROOT)}")
    print(f"overlap_conflicts={provenance['overlap_conflict_count']}")
    print(
        "rows",
        {
            "IS": len(model["income_statement"]),
            "BS": len(model["balance_sheet"]),
            "CF": len(model["cash_flow"]),
        },
    )


if __name__ == "__main__":
    main()
