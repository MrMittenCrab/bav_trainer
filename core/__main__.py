#!/usr/bin/env python3
"""BAV Excel Trainer CLI for Hong Kong-listed companies.

Usage: python -m core <command> ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .data.interface import DocumentManifest, DocumentType
from .engine.component_catalog import COMPONENT_CATALOG
from .ingestion.manual_hk import HKManualDocumentAdapter
from .trainer.checker import check_workbook
from .trainer.semantic_io import answer_key_path_for, load_semantic_map
from .trainer.workbook import build_training_workbook


def _serialize_line_items(items) -> list[dict]:
    return [
        {
            "label": i.label,
            "concept": i.concept or "",
            "values": {_date_key(k): v for k, v in i.values.items()},
        }
        for i in items
    ]


def _date_key(d) -> str:
    """Serialize period keys as YYYY-MM-DD (Excel may yield datetime)."""
    if hasattr(d, "date") and callable(d.date) and not isinstance(d, type):
        try:
            # datetime → date; plain date has date() method that returns self-like attrs
            from datetime import date, datetime

            if isinstance(d, datetime):
                return d.date().isoformat()
            if isinstance(d, date):
                return d.isoformat()
        except Exception:
            pass
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def cmd_ingest(args: argparse.Namespace) -> int:
    manifest = []
    for p in args.documents:
        path = Path(p)
        suffix = path.suffix.lower()
        if suffix in (".xlsx", ".xls", ".xlsm"):
            dtype = DocumentType.EXCEL_EXPORT
        elif "bloomberg" in path.name.lower():
            dtype = DocumentType.BLOOMBERG_EXPORT
        elif "wind" in path.name.lower():
            dtype = DocumentType.WIND_EXPORT
        else:
            dtype = DocumentType.ANNUAL_REPORT
        manifest.append(DocumentManifest(path=str(path), doc_type=dtype))

    adapter = HKManualDocumentAdapter()
    data = adapter.ingest(manifest)
    report = adapter.reconcile(data)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "ticker": data.ticker,
            "company_name": data.company_name,
            "currency": data.currency,
            "units": data.units,
            "stock_code": data.stock_code,
            "periods": [
                {
                    "end_date": _date_key(p.end_date),
                    "label": p.label,
                    "is_interim": p.is_interim,
                }
                for p in data.periods
            ],
            "income_statement": _serialize_line_items(data.income_statement),
            "balance_sheet": _serialize_line_items(data.balance_sheet),
            "cash_flow": _serialize_line_items(data.cash_flow),
        }
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote standardized data: {out}")

    print(f"Ingested {data.company_name} ({data.ticker}) — {len(data.periods)} periods")
    for stmt, ok in report.checksums.items():
        status = "OK" if ok else "FAIL"
        print(f"  {stmt}: {status}")
    for w in report.warnings:
        print(f"  warning: {w}")
    return 0 if all(report.checksums.values()) else 1


def cmd_build(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if path.suffix.lower() == ".json":
        adapter = HKManualDocumentAdapter()
        data = adapter.ingest([DocumentManifest(path=str(path), doc_type=DocumentType.OTHER)])
    else:
        adapter = HKManualDocumentAdapter()
        data = adapter.ingest([DocumentManifest(path=str(path), doc_type=DocumentType.EXCEL_EXPORT)])

    assumptions = None
    if args.assumptions:
        assumptions = json.loads(Path(args.assumptions).read_text(encoding="utf-8"))

    out = Path(args.output)
    trainer_path, answer_key_path = build_training_workbook(data, out, assumptions)
    smap = load_semantic_map(answer_key_path)
    print(f"Trainer workbook: {trainer_path}")
    print(f"Answer Key workbook: {answer_key_path}")
    print(f"Components resolved: {len(smap.all_ordered())}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    summary = check_workbook(Path(args.workbook))
    print(
        f"Checked {summary.total} practice cells: "
        f"{summary.correct} correct, {summary.incorrect} incorrect, {summary.blank} blank."
    )
    return 0 if summary.incorrect == 0 else 1


def cmd_list(args: argparse.Namespace) -> int:
    wb = Path(args.workbook) if args.workbook else None
    if wb and wb.exists():
        try:
            smap = load_semantic_map(wb)
        except FileNotFoundError:
            ak = answer_key_path_for(wb)
            if not ak.exists():
                raise
            smap = load_semantic_map(ak)
        for comp in smap.all_ordered():
            print(
                f"{comp.order:2d}. [{comp.id}] {comp.title} — "
                f"{comp.tab}!{comp.cell} ({comp.category})"
            )
    else:
        for spec in COMPONENT_CATALOG:
            tab = (
                spec.tab_template.replace("{scenario}", spec.scenario)
                if spec.scenario
                else spec.tab_template
            )
            print(
                f"{spec.order:2d}. [{spec.id}] {spec.title} — "
                f"{tab} (semantic: {spec.semantic_key}, {spec.category})"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BAV Excel Trainer — Hong Kong edition")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest HK documents into standardized JSON")
    p_ingest.add_argument("documents", nargs="+", help="JSON, Excel, or document paths")
    p_ingest.add_argument("-o", "--output", help="Write standardized JSON")
    p_ingest.set_defaults(func=cmd_ingest)

    p_build = sub.add_parser(
        "build",
        help="Build matched Trainer + Answer Key workbooks from a complete BAV model",
    )
    p_build.add_argument("input", help="Standardized JSON or Excel workbook")
    p_build.add_argument(
        "-o",
        "--output",
        required=True,
        help=(
            "Output path (stem ending in _Trainer, or a company stem to which "
            "_Trainer/_Answer_Key are appended)"
        ),
    )
    p_build.add_argument(
        "-a",
        "--assumptions",
        help="Optional historical configuration JSON (e.g. classificationOverrides)",
    )
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser(
        "check",
        help="Validate every practice cell in a Trainer workbook (yellow/green/red)",
    )
    p_check.add_argument("--workbook", required=True)
    p_check.set_defaults(func=cmd_check)

    p_list = sub.add_parser("list", help="List trainer components")
    p_list.add_argument(
        "--workbook",
        help="Show resolved coordinates from a built Answer Key (or matching Trainer)",
    )
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
