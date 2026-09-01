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
from .trainer.checker import check_component, check_dependencies
from .trainer.hints import reveal_answer, show_hint
from .trainer.semantic_io import load_semantic_map
from .trainer.workbook import build_training_workbook


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
                {"end_date": p.end_date.isoformat(), "label": p.label, "is_interim": p.is_interim}
                for p in data.periods
            ],
            "income_statement": [
                {"label": i.label, "values": {k.isoformat(): v for k, v in i.values.items()}}
                for i in data.income_statement
            ],
            "balance_sheet": [
                {"label": i.label, "values": {k.isoformat(): v for k, v in i.values.items()}}
                for i in data.balance_sheet
            ],
            "cash_flow": [
                {"label": i.label, "values": {k.isoformat(): v for k, v in i.values.items()}}
                for i in data.cash_flow
            ],
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
    build_training_workbook(data, out)
    ref = out.with_name(out.stem + "_reference.xlsx")
    smap = load_semantic_map(ref)
    print(f"Reference model: {ref}")
    print(f"Training workbook: {out}")
    print(f"Components resolved: {len(smap.all_ordered())}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    result = check_component(Path(args.workbook), args.component)
    print(result.message)
    if result.user_value is not None:
        print(f"  user value: {result.user_value}")
    if result.expected_value is not None:
        print(f"  expected:   {result.expected_value}")
    deps = check_dependencies(Path(args.workbook), args.component)
    for d in deps:
        print(f"  dependency: {d}")
    return 0 if result.passed else 1


def cmd_hint(args: argparse.Namespace) -> int:
    result = show_hint(Path(args.workbook), args.component)
    print(f"[{result.level}/{result.max_level}] {result.hint_text}")
    if result.related_cells:
        print("Related cells:", ", ".join(result.related_cells))
    return 0


def cmd_reveal(args: argparse.Namespace) -> int:
    formula = reveal_answer(Path(args.workbook), args.component)
    print(f"Revealed formula: {formula}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    wb = Path(args.workbook) if args.workbook else None
    if wb and wb.exists():
        smap = load_semantic_map(wb)
        for comp in smap.all_ordered():
            print(
                f"{comp.order:2d}. [{comp.id}] {comp.title} — "
                f"{comp.tab}!{comp.cell} ({comp.category})"
            )
    else:
        for spec in COMPONENT_CATALOG:
            tab = spec.tab_template.replace("{scenario}", spec.scenario) if spec.scenario else spec.tab_template
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

    p_build = sub.add_parser("build", help="Build reference model + training workbook")
    p_build.add_argument("input", help="Standardized JSON or Excel workbook")
    p_build.add_argument("-o", "--output", required=True, help="Training workbook output path")
    p_build.add_argument("-a", "--assumptions", help="assumptions.json for scenarios")
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser("check", help="Validate a practice cell formula")
    p_check.add_argument("--workbook", required=True)
    p_check.add_argument("--component", required=True)
    p_check.set_defaults(func=cmd_check)

    p_hint = sub.add_parser("hint", help="Show next progressive hint")
    p_hint.add_argument("--workbook", required=True)
    p_hint.add_argument("--component", required=True)
    p_hint.set_defaults(func=cmd_hint)

    p_reveal = sub.add_parser("reveal", help="Insert reference formula (Build/Reveal Answer)")
    p_reveal.add_argument("--workbook", required=True)
    p_reveal.add_argument("--component", required=True)
    p_reveal.set_defaults(func=cmd_reveal)

    p_list = sub.add_parser("list", help="List trainer components")
    p_list.add_argument("--workbook", help="Show resolved coordinates from a built workbook")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
