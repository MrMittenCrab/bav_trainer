#!/usr/bin/env python3
"""BAV Excel Trainer CLI for Hong Kong-listed companies.

Usage: python -m bav <command> ...
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .data.interface import DocumentManifest, DocumentType
from .data.standardized_io import standardized_from_payload, standardized_to_payload
from .engine.component_catalog import COMPONENT_CATALOG
from .ingestion.filing_cli import load_and_validate_extracted_dir
from .ingestion.filing_reconciler import reconcile_filings
from .ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_management_admission_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from .ingestion.manual_hk import HKManualDocumentAdapter
from .trainer.checker import check_workbook
from .trainer.semantic_io import bav_path_for, load_semantic_map, resolve_pair_paths
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


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _load_build_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_json_object,
                      parse_constant=_reject_json_constant)


def _validate_build_output(output: Path, inputs: list[Path]) -> None:
    trainer, answer = resolve_pair_paths(output)
    if trainer.suffix.lower() != ".xlsx":
        raise ValueError("build output must be a company stem or .xlsx path")
    roots = {Path.cwd().resolve(), Path(__file__).resolve().parents[1]}
    protected = [root / name for root in roots for name in ("benchmark", "release", ".git", ".codex", ".agents")]
    protected_files = {p.resolve() for p in inputs}
    protected_files.update((root / name).resolve() for root in roots
                           for name in ("TARGET.md", "IMPLEMENTATION.md", "RESULT.md"))
    destinations = [trainer, answer, answer.parent / "rowmap.json"]
    for workbook in (trainer, answer):
        destinations.extend(workbook.with_suffix(suffix) for suffix in
                            (".component_map.json", ".assumptions.json", ".trainer.json"))
    for destination in destinations:
        resolved = destination.resolve()
        if (destination.is_symlink() or resolved in protected_files
                or any(resolved.is_relative_to(p.resolve()) for p in protected)
                or resolved.suffix.lower() == ".pdf"):
            raise ValueError(f"protected build destination: {destination}; use a path under build/")


def cmd_build(args: argparse.Namespace) -> int:
    from .current_build import resolve_company, build_company
    path = Path(args.input)
    if path.suffix.lower() not in {".json", ".xlsx", ".xls", ".xlsm"} and not path.is_file():
        try:
            company = resolve_company(args.input)
            if args.output:
                raise ValueError('Company builds use their canonical directory; use explicit JSON input with -o for advanced output')
            assumptions = _load_build_json(Path(args.assumptions)) if args.assumptions else None
            if assumptions is not None and not isinstance(assumptions, dict):
                raise ValueError('assumptions must be a JSON object')
            rows = build_company(company, assumptions)
        except (OSError, ValueError, RuntimeError) as exc:
            print(f'error: build failed: {exc}', file=sys.stderr)
            return 1
        print(f'Built {company.name}\nOutput: {company.output}/\n')
        print(f'BAV: {company.bav.name}')
        print('\nActive:')
        for group in dict.fromkeys(c.tab for c in load_semantic_map(company.bav).all_ordered()):
            print(f'  {group}')
        print('\nUnavailable / not yet active:')
        for row in rows:
            if not row['cells']:
                print(f"  {row['family']} — {row['status']}")
        return 0
    if not args.output:
        print('error: explicit input requires -o; normal usage: python -m bav build <Company>', file=sys.stderr)
        return 1
    out = Path(args.output)
    try:
        inputs = [path] + ([Path(args.assumptions)] if args.assumptions else [])
        _validate_build_output(out, inputs)
        if path.suffix.lower() == ".json":
            data = standardized_from_payload(_load_build_json(path), strict=True)
        else:
            adapter = HKManualDocumentAdapter()
            data = adapter.ingest([DocumentManifest(path=str(path), doc_type=DocumentType.EXCEL_EXPORT)])

        assumptions = None
        if args.assumptions:
            assumptions = _load_build_json(Path(args.assumptions))
            if not isinstance(assumptions, dict):
                raise ValueError("assumptions must be a JSON object")

        trainer_path, bav_path = build_training_workbook(data, out, assumptions)
    except (OSError, ValueError) as exc:
        print(f"error: build failed: {exc}", file=sys.stderr)
        return 1
    smap = load_semantic_map(bav_path)
    print(f"Trainer workbook: {trainer_path}")
    print(f"BAV workbook: {bav_path}")
    print(f"Components resolved: {len(smap.all_ordered())}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    from .current_build import check_company_output
    if bool(args.company) == bool(args.workbook):
        raise ValueError('Specify a company or --workbook')
    if args.company:
        return check_company_output(args.company)
    workbook = Path(args.workbook)
    summary = check_workbook(workbook)
    print(
        f"Checked {summary.total} practice cells: "
        f"{summary.correct} correct, {summary.incorrect} incorrect, {summary.blank} blank."
    )
    return 0 if summary.incorrect == 0 else 1


def cmd_validate_source(args: argparse.Namespace) -> int:
    source_root = Path(args.source_root)
    try:
        validated = load_and_validate_extracted_dir(
            Path(args.extracted), source_root=source_root
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 1

    hard_errors = 0
    warnings = 0
    for filing, report in validated:
        label = filing.filing.source_file
        if report.ok:
            print(
                f"OK {label} sha256={report.computed_source_sha256} "
                f"warnings={len(report.warnings)}"
            )
        else:
            hard_errors += len(report.errors)
            for issue in report.errors:
                print(f"ERROR {label}: {issue.code}: {issue.message}")
        for issue in report.warnings:
            warnings += 1
            print(f"WARN {label}: {issue.code}: {issue.message}")

    management_docs = getattr(validated, "management_documents", ())
    for bound in management_docs:
        label = bound.document.extraction_document
        if bound.ok:
            print(
                f"OK management-kpi {label} "
                f"sha256={bound.bound_source_sha256} "
                f"status=admitted_unreconciled"
            )
        else:
            hard_errors += len(bound.issues)
            for issue in bound.issues:
                print(f"ERROR {label}: {issue.code}: {issue.message}")

    print(
        f"validated {len(validated)} filing(s): "
        f"{hard_errors} error(s), {warnings} warning(s)"
    )
    if management_docs:
        print(f"management-kpi documents: {len(management_docs)}")
    return 0 if hard_errors == 0 else 1


def cmd_reconcile(args: argparse.Namespace) -> int:
    source_root = Path(args.source_root)
    out_dir = Path(args.output)
    try:
        validated = load_and_validate_extracted_dir(
            Path(args.extracted), source_root=source_root
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 1

    if any(not report.ok for _, report in validated) or any(
        not bound.ok
        for bound in getattr(validated, "management_documents", ())
    ):
        for filing, report in validated:
            for issue in report.errors:
                print(
                    f"ERROR {filing.filing.source_file}: "
                    f"{issue.code}: {issue.message}"
                )
        for bound in getattr(validated, "management_documents", ()):
            for issue in bound.issues:
                print(
                    f"ERROR {bound.document.extraction_document}: "
                    f"{issue.code}: {issue.message}"
                )
        print("reconcile aborted: validation errors present; wrote no artifacts")
        return 1

    try:
        admit_periods: tuple[date, ...] = ()
        if args.admit_period:
            parsed: list[date] = []
            for raw in args.admit_period:
                try:
                    parsed.append(date.fromisoformat(raw))
                except ValueError:
                    print(
                        f"error: invalid --admit-period {raw!r}; expected YYYY-MM-DD"
                    )
                    return 1
            admit_periods = tuple(parsed)
        reconciled = reconcile_filings(
            validated,
            admit_periods=admit_periods or None,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 1

    fin = standardize_reconciled(reconciled)
    provenance = reconciliation_provenance_payload(reconciled)
    conflicts = reconciliation_conflicts_payload(reconciled)

    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "standardized.json": standardized_to_payload(fin),
        "provenance.json": provenance,
        "conflicts.json": conflicts,
    }
    management_payload = reconciliation_management_admission_payload(reconciled)
    if management_payload is not None:
        artifacts["management_kpi_admission.json"] = management_payload
    for name, payload in artifacts.items():
        (out_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_dir / name}")
    print(f"overlap_conflicts={conflicts['overlap_conflict_count']}")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    from .research.document import publish_company_documents
    published = publish_company_documents(args.company)
    print(f"Published {published.word.name} and {published.pdf.name}")
    print(f"Word: {published.word}")
    print(f"PDF: {published.pdf}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    from .trainer.workbook import group_components_by_family

    from .current_build import current_workbook
    if args.company and args.workbook:
        raise ValueError('Specify a company or --workbook, not both')
    wb = current_workbook(args.company, answer=True) if args.company else (Path(args.workbook) if args.workbook else None)
    if wb and not wb.is_file():
        raise ValueError(f'Workbook not found: {wb}')
    if wb and wb.exists():
        try:
            smap = load_semantic_map(wb)
        except FileNotFoundError:
            matched = bav_path_for(wb)
            if not matched.exists():
                raise
            smap = load_semantic_map(matched)
        for group in group_components_by_family(smap):
            print(
                f"{group['family_order']:2d}. [{group['family_id']}] {group['title']} — "
                f"{group['tab']}!{group['practice_cells']} "
                f"({group['count']} cells, {group['period_scope']})"
            )
    else:
        for family in COMPONENT_CATALOG:
            scope = (
                "[second period onward]"
                if family.period_scope == "comparable"
                else "[all periods]"
            )
            tab = family.tab_template
            print(
                f"{family.order:2d}. [{family.id}] {family.title} — "
                f"{tab} {scope} (semantic: {family.semantic_key}, {family.category})"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BAV Excel Trainer — Hong Kong edition")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest HK documents into standardized JSON")
    p_ingest.add_argument("documents", nargs="+", help="JSON, Excel, or document paths")
    p_ingest.add_argument("-o", "--output", help="Write standardized JSON")
    p_ingest.set_defaults(func=cmd_ingest)

    p_validate = sub.add_parser(
        "validate-source",
        help="Validate extracted filing JSON and bind source-file SHA-256",
    )
    p_validate.add_argument(
        "extracted",
        help="Extracted filing JSON file or directory of *.json filings",
    )
    p_validate.add_argument(
        "--source-root",
        required=True,
        help="Directory containing the original source files named in each filing",
    )
    p_validate.set_defaults(func=cmd_validate_source)

    p_reconcile = sub.add_parser(
        "reconcile",
        help="Validate, reconcile, and standardize extracted filing JSON",
    )
    p_reconcile.add_argument(
        "extracted",
        help="Directory of extracted filing JSON files (or a single file)",
    )
    p_reconcile.add_argument(
        "--source-root",
        required=True,
        help="Directory containing the original source files named in each filing",
    )
    p_reconcile.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory for standardized.json / provenance.json / conflicts.json",
    )
    p_reconcile.add_argument(
        "--admit-period",
        action="append",
        default=None,
        metavar="YYYY-MM-DD",
        help=(
            "Admit an additional comparative period that has selected "
            "income-statement, balance-sheet, and cash-flow coverage. "
            "Repeatable. Default keeps filing year-ends only."
        ),
    )
    p_reconcile.set_defaults(func=cmd_reconcile)

    p_build = sub.add_parser(
        "build",
        help="Build the current company professional BAV workbook",
    )
    p_build.add_argument("input", help="Company name/ticker, or explicit standardized JSON/Excel")
    p_build.add_argument(
        "-o",
        "--output",
        help=(
            "Output path (stem ending in _BAV or _BAV_Trainer, or a company stem "
            "to which _BAV/_BAV_Trainer are appended)"
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
    p_check.add_argument("company", nargs="?")
    p_check.add_argument("--workbook")
    p_check.set_defaults(func=cmd_check)

    p_publish = sub.add_parser(
        "publish",
        help="Publish BAV Word and PDF from canonical research",
        description=(
            "Publish BAV Word and PDF from canonical Drivers research and figures. "
            "Does not rebuild analysis."
        ),
    )
    p_publish.add_argument("company", help="Company name or ticker")
    p_publish.set_defaults(func=cmd_publish)

    p_list = sub.add_parser("list", help="List trainer components")
    p_list.add_argument("company", nargs="?")
    p_list.add_argument(
        "--workbook",
        help="Show resolved coordinates from a built BAV (or matching Trainer)",
    )
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
