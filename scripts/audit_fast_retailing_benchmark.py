#!/usr/bin/env python3
"""Stage-by-stage audit of the Fast Retailing benchmark against the current engine.

Writes BASELINE.md. Does not patch production accounting logic.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
BENCH = ROOT / "benchmark" / "fast_retailing"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"
MANIFEST = BENCH / "source_manifest.json"
BASELINE = BENCH / "BASELINE.md"
EXPECTED_PRACTICE_TOTAL = 491
EXPECTED_BLANK_CHECK = (0, 0, EXPECTED_PRACTICE_TOTAL, EXPECTED_PRACTICE_TOTAL)
EXPECTED_FILLED_CHECK = (EXPECTED_PRACTICE_TOTAL, 0, 0, EXPECTED_PRACTICE_TOTAL)


@dataclass
class StageResult:
    stage: str
    status: str  # pass | fail | skipped
    exception_type: str = ""
    message: str = ""


def _load_payload(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or STD_JSON).read_text(encoding="utf-8"))


def _fill_rgb(cell) -> str:
    fill = cell.fill
    if not fill or fill.fill_type != "solid":
        return ""
    color = fill.fgColor.rgb or fill.start_color.rgb or ""
    return str(color).upper().lstrip("0")[-6:] if color else ""


def _copy_release_pair_to_temp(
    trainer_path: Path,
    answer_key_path: Path,
    tmp: Path,
) -> tuple[Path, Path]:
    """Copy Trainer/Answer Key and Answer Key sidecars for mutating Check ops."""
    trainer_copy = tmp / trainer_path.name
    answer_copy = tmp / answer_key_path.name
    shutil.copy2(trainer_path, trainer_copy)
    shutil.copy2(answer_key_path, answer_copy)
    for suffix in (".component_map.json", ".assumptions.json", ".trainer.json"):
        sidecar = answer_key_path.with_suffix(suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, tmp / sidecar.name)
    return trainer_copy, answer_copy


def _verify_release_pair_contract(trainer_path: Path, answer_key_path: Path) -> str:
    """Semantic match, practice contract, and visible structural parity."""
    from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
    from openpyxl import load_workbook

    smap = load_semantic_map(answer_key_path)
    comps = smap.all_ordered()
    if len(comps) != EXPECTED_PRACTICE_TOTAL:
        raise ValueError(
            f"semantic practice cells={len(comps)} != {EXPECTED_PRACTICE_TOTAL}"
        )

    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    try:
        visible_t = [s for s in wb_t.sheetnames if not s.startswith("_")]
        visible_a = [s for s in wb_a.sheetnames if not s.startswith("_")]
        if visible_t != visible_a:
            raise ValueError(
                f"visible sheet mismatch: trainer={visible_t} answer={visible_a}"
            )

        source_tabs = ("Condensed Financials",)
        for tab in source_tabs:
            if tab not in wb_t.sheetnames:
                continue
            ws = wb_t[tab]
            populated = 0
            for row in ws.iter_rows(
                min_row=1,
                max_row=min(ws.max_row or 1, 80),
                max_col=min(ws.max_column or 1, 12),
            ):
                for cell in row:
                    if isinstance(cell.value, (int, float)) and cell.value != 0:
                        populated += 1
            if populated < 10:
                raise ValueError(f"historical source facts look empty on {tab}")

        for comp in comps:
            row, col = parse_cell_ref(comp.cell)
            tc = wb_t[comp.tab].cell(row=row, column=col)
            ac = wb_a[comp.tab].cell(row=row, column=col)
            if tc.value is not None:
                raise ValueError(f"Trainer practice cell {comp.tab}!{comp.cell} not blank")
            if tc.comment is not None:
                raise ValueError(f"Trainer practice cell {comp.tab}!{comp.cell} has Note")
            if _fill_rgb(tc) != "FFFF00":
                raise ValueError(
                    f"Trainer practice cell {comp.tab}!{comp.cell} not yellow"
                )
            if not (isinstance(ac.value, str) and ac.value.startswith("=")):
                raise ValueError(
                    f"Answer Key {comp.tab}!{comp.cell} missing formula"
                )
            if ac.value != comp.formula:
                raise ValueError(
                    f"Answer Key {comp.tab}!{comp.cell} formula != semantic map"
                )
            if ac.comment is None or not str(ac.comment.text or "").strip():
                raise ValueError(
                    f"Answer Key {comp.tab}!{comp.cell} missing non-empty Note"
                )
            if _fill_rgb(ac) != "FFFF00":
                raise ValueError(
                    f"Answer Key practice cell {comp.tab}!{comp.cell} not yellow"
                )
    finally:
        wb_t.close()
        wb_a.close()
    return f"practice_cells={len(comps)} visible_parity=ok"


def _module_applicability(fin, anchor=None) -> dict[str, Any]:
    from core.model.earnings_quality import earnings_quality_availability
    from core.model.deferred_tax import (
        deferred_tax_applicable,
        deferred_tax_availability,
    )
    from core.model.fixed_asset import fixed_asset_applicable
    from core.model.goodwill_intangibles import (
        goodwill_intangibles_applicable,
        goodwill_intangibles_availability,
    )
    from core.model.lease_liability import (
        lease_liability_applicable,
        lease_liability_availability,
    )
    from core.model.lease_rou import (
        lease_rou_applicable,
        lease_rou_availability,
    )
    from core.model.ownership_attribution import (
        ownership_attribution_applicable,
        ownership_attribution_availability,
    )
    from core.model.per_share import per_share_available
    from core.model.working_capital import working_capital_applicable

    lease_avail = lease_liability_availability(fin)
    lease_rou_avail = lease_rou_availability(fin)
    ownership_avail = ownership_attribution_availability(fin)
    gi_avail = goodwill_intangibles_availability(fin)
    deferred_tax_avail = deferred_tax_availability(fin)
    eq = earnings_quality_availability(fin)
    wc_applicable: bool | None
    if anchor is None:
        wc_applicable = None
    else:
        wc_applicable = working_capital_applicable(anchor)
    return {
        "earnings_quality": {
            "applicable": bool(eq.operating_cash_flow),
            "detail": asdict(eq),
        },
        "working_capital": {
            "applicable": wc_applicable,
            "detail": "requires AnchorMetrics; filled after successful builder"
            if anchor is None
            else "",
        },
        "fixed_asset": {"applicable": fixed_asset_applicable(fin)},
        "lease_liability": {
            "applicable": lease_liability_applicable(fin),
            "availability": asdict(lease_avail),
        },
        "lease_rou": {
            "applicable": lease_rou_applicable(fin),
            "availability": asdict(lease_rou_avail),
        },
        "ownership_attribution": {
            "applicable": ownership_attribution_applicable(fin),
            "availability": asdict(ownership_avail),
        },
        "goodwill_intangibles": {
            "applicable": goodwill_intangibles_applicable(fin),
            "availability": asdict(gi_avail),
        },
        "deferred_tax": {
            "applicable": deferred_tax_applicable(fin),
            "availability": asdict(deferred_tax_avail),
        },
        "per_share": {"applicable": per_share_available(fin)},
        "normalization": {
            "applicable": False,
            "detail": "no normalization assumptions supplied for benchmark audit",
        },
    }


def run_audit(
    *,
    standardized_json: Path | None = None,
    provenance_json: Path | None = None,
    conflicts_json: Path | None = None,
    trainer_path: Path | None = None,
    answer_key_path: Path | None = None,
    require_check_counts: bool | None = None,
    verify_release_pair: bool = False,
) -> dict[str, Any]:
    """Run the Fast Retailing stage audit.

    Default call with no arguments preserves the historical temporary-workbook
    interface used by existing tests. Pass explicit release workbook paths and
    generated standardized JSON to verify a persisted pair without regenerating
    substitute workbooks.
    """
    std_path = Path(standardized_json) if standardized_json else STD_JSON
    explicit_pair = trainer_path is not None or answer_key_path is not None
    if explicit_pair:
        if trainer_path is None or answer_key_path is None:
            raise ValueError("trainer_path and answer_key_path must be provided together")
        trainer_path = Path(trainer_path)
        answer_key_path = Path(answer_key_path)
        if require_check_counts is None:
            require_check_counts = True
    elif require_check_counts is None:
        require_check_counts = False

    stages: list[StageResult] = []
    context: dict[str, Any] = {
        "modules": {},
        "first_failure": None,
        "workbook_paths": {},
        "release_fingerprints_before": {},
        "release_fingerprints_after": {},
        "standardized_json": str(std_path),
        "provenance_json": str(provenance_json or PROV_JSON),
        "conflicts_json": str(conflicts_json or CONFLICTS_JSON),
    }

    def _fingerprint(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    release_files: list[Path] = []
    if explicit_pair:
        release_files = [
            trainer_path,
            answer_key_path,
            answer_key_path.with_suffix(".component_map.json"),
        ]
        for path in (trainer_path, answer_key_path):
            if not path.is_file():
                stages.append(
                    StageResult(
                        "1_source_fixture_load",
                        "fail",
                        "FileNotFoundError",
                        f"missing release artifact: {path}",
                    )
                )
                context["first_failure"] = stages[-1]
                for name in (
                    "2_identity_validation",
                    "3_reconciliation",
                    "4_reference_model_builder",
                    "5_workbook_generation",
                    "6_blank_check",
                    "7_filled_check",
                ):
                    stages.append(
                        StageResult(name, "skipped", message="prior stage failed")
                    )
                return {"stages": stages, "context": context}
        context["release_fingerprints_before"] = {
            str(p): _fingerprint(p) for p in release_files if p.is_file()
        }

    # Stage 1
    try:
        if not std_path.is_file():
            raise FileNotFoundError(f"missing standardized input: {std_path}")
        payload = _load_payload(std_path)
        assert payload["ticker"] == "6288.HK"
        assert payload.get("company_name") == "FAST RETAILING CO., LTD."
        assert [p["end_date"] for p in payload["periods"]] == [
            "2021-08-31",
            "2022-08-31",
            "2023-08-31",
            "2024-08-31",
            "2025-08-31",
        ]
        stages.append(StageResult("1_source_fixture_load", "pass", message="loaded"))
    except Exception as exc:  # noqa: BLE001 — audit must capture all failures
        stages.append(
            StageResult(
                "1_source_fixture_load",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        context["first_failure"] = stages[-1]
        for name in (
            "2_identity_validation",
            "3_reconciliation",
            "4_reference_model_builder",
            "5_workbook_generation",
            "6_blank_check",
            "7_filled_check",
        ):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        return {"stages": stages, "context": context}

    from core.data.standardized_io import standardized_from_payload

    fin = standardized_from_payload(payload)

    # Stage 2
    try:
        from core.data.line_identity import validate_financials_identities

        validate_financials_identities(fin)
        stages.append(StageResult("2_identity_validation", "pass"))
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult("2_identity_validation", "fail", type(exc).__name__, str(exc))
        )
        context["first_failure"] = stages[-1]
        for name in (
            "3_reconciliation",
            "4_reference_model_builder",
            "5_workbook_generation",
            "6_blank_check",
            "7_filled_check",
        ):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        context["modules"] = _module_applicability(fin)
        return {"stages": stages, "context": context}

    # Stage 3
    try:
        from core.ingestion.reconciler import reconcile_financials

        report = reconcile_financials(fin)
        if not all(report.checksums.values()):
            raise ValueError(
                f"reconciliation checksums={report.checksums} warnings={report.warnings}"
            )
        stages.append(StageResult("3_reconciliation", "pass"))
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult("3_reconciliation", "fail", type(exc).__name__, str(exc))
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        # Continue measuring later stages where possible — identity already passed.
        # But workbook generation may still be attempted; mark dependent skips only
        # if builder cannot run. We still try builder for gap visibility.

    context["modules"] = _module_applicability(fin)

    # Stage 4
    builder = None
    try:
        from core.engine.reference_model import ReferenceModelBuilder

        builder = ReferenceModelBuilder(fin)
        stages.append(
            StageResult(
                "4_reference_model_builder",
                "pass",
                message=(
                    f"expected_specs={len(builder.expected_specs)} "
                    f"lease_specs={len(builder.lease_liability_specs)} "
                    f"lease_rou_specs={len(builder.lease_rou_specs)} "
                    f"ownership_specs={len(builder.ownership_attribution_specs)} "
                    f"per_share_specs={len(builder.per_share_specs)} "
                    f"per_share_attribution_specs={len(builder.per_share_attribution_specs)} "
                    f"fixed_asset_specs={len(builder.fixed_asset_specs)} "
                    f"goodwill_intangibles_specs={len(builder.goodwill_intangibles_specs)} "
                    f"deferred_tax_specs={len(builder.deferred_tax_specs)} "
                    f"capex_specs={len(builder.capex_specs)}"
                ),
            )
        )
        context["modules"] = _module_applicability(fin, builder.anchor)
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult(
                "4_reference_model_builder",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        for name in ("5_workbook_generation", "6_blank_check", "7_filled_check"):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))
        return {"stages": stages, "context": context}

    # Stage 5–7: either use persisted release pair or generate temporary workbooks.
    try:
        from core.trainer.checker import check_workbook
        from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
        from openpyxl import load_workbook

        with tempfile.TemporaryDirectory(prefix="fr_bench_") as tmp:
            tmp_path = Path(tmp)
            if explicit_pair:
                assert trainer_path is not None and answer_key_path is not None
                if verify_release_pair:
                    contract_msg = _verify_release_pair_contract(
                        trainer_path, answer_key_path
                    )
                else:
                    contract_msg = "release pair supplied"
                # Mutating Check / fill on copies only.
                trainer, answer = _copy_release_pair_to_temp(
                    trainer_path, answer_key_path, tmp_path
                )
                context["workbook_paths"] = {
                    "trainer": str(trainer_path),
                    "answer": str(answer_key_path),
                    "check_copies": str(tmp_path),
                    "note": "persisted release pair; Check used temporary copies",
                    "contract": contract_msg,
                }
                stages.append(
                    StageResult(
                        "5_workbook_generation",
                        "pass",
                        message="persisted release pair (not regenerated)",
                    )
                )
            else:
                from core.trainer.workbook import build_training_workbook

                trainer, answer = build_training_workbook(
                    fin, tmp_path / "FastRetailing_Trainer.xlsx"
                )
                context["workbook_paths"] = {
                    "trainer": str(trainer),
                    "answer": str(answer),
                    "note": "temporary only; not committed",
                }
                stages.append(StageResult("5_workbook_generation", "pass"))

            # Stage 6
            try:
                summary = check_workbook(trainer)
                blank_tuple = (
                    summary.correct,
                    summary.incorrect,
                    summary.blank,
                    summary.total,
                )
                if require_check_counts and blank_tuple != EXPECTED_BLANK_CHECK:
                    raise ValueError(
                        f"pristine Check counts {blank_tuple} != {EXPECTED_BLANK_CHECK}"
                    )
                stages.append(
                    StageResult(
                        "6_blank_check",
                        "pass",
                        message=(
                            f"correct={summary.correct} incorrect={summary.incorrect} "
                            f"blank={summary.blank} total={summary.total}"
                        ),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                stages.append(
                    StageResult("6_blank_check", "fail", type(exc).__name__, str(exc))
                )
                if context["first_failure"] is None:
                    context["first_failure"] = stages[-1]
                stages.append(
                    StageResult("7_filled_check", "skipped", message="prior stage failed")
                )
                if explicit_pair:
                    context["release_fingerprints_after"] = {
                        str(p): _fingerprint(p)
                        for p in release_files
                        if p.is_file()
                    }
                return {"stages": stages, "context": context}

            # Stage 7
            try:
                smap = load_semantic_map(answer)
                wb = load_workbook(trainer, data_only=False)
                for comp in smap.all_ordered():
                    row, col = parse_cell_ref(comp.cell)
                    wb[comp.tab].cell(row=row, column=col).value = comp.formula
                wb.save(trainer)
                wb.close()
                filled = check_workbook(trainer)
                filled_tuple = (
                    filled.correct,
                    filled.incorrect,
                    filled.blank,
                    filled.total,
                )
                if require_check_counts:
                    if filled_tuple != EXPECTED_FILLED_CHECK:
                        raise ValueError(
                            f"filled Check counts {filled_tuple} != {EXPECTED_FILLED_CHECK}"
                        )
                elif filled.incorrect or filled.blank:
                    raise ValueError(
                        f"filled check incomplete: correct={filled.correct} "
                        f"incorrect={filled.incorrect} blank={filled.blank}"
                    )
                stages.append(
                    StageResult(
                        "7_filled_check",
                        "pass",
                        message=f"correct={filled.correct} total={filled.total}",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                stages.append(
                    StageResult("7_filled_check", "fail", type(exc).__name__, str(exc))
                )
                if context["first_failure"] is None:
                    context["first_failure"] = stages[-1]
    except Exception as exc:  # noqa: BLE001
        stages.append(
            StageResult(
                "5_workbook_generation",
                "fail",
                type(exc).__name__,
                str(exc),
            )
        )
        if context["first_failure"] is None:
            context["first_failure"] = stages[-1]
        for name in ("6_blank_check", "7_filled_check"):
            stages.append(StageResult(name, "skipped", message="prior stage failed"))

    if explicit_pair:
        context["release_fingerprints_after"] = {
            str(p): _fingerprint(p) for p in release_files if p.is_file()
        }
        before = context["release_fingerprints_before"]
        after = context["release_fingerprints_after"]
        if before and after and before != after:
            stages.append(
                StageResult(
                    "8_release_pristine",
                    "fail",
                    "AssertionError",
                    "release artifacts mutated during verification",
                )
            )
            if context["first_failure"] is None:
                context["first_failure"] = stages[-1]
        elif before:
            stages.append(
                StageResult(
                    "8_release_pristine",
                    "pass",
                    message="release fingerprints unchanged",
                )
            )

    return {"stages": stages, "context": context}


def write_baseline(result: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    provenance = json.loads(PROV_JSON.read_text(encoding="utf-8"))
    conflicts = (
        json.loads(CONFLICTS_JSON.read_text(encoding="utf-8"))
        if CONFLICTS_JSON.is_file()
        else {}
    )
    stages: list[StageResult] = result["stages"]
    ctx = result["context"]
    overlap = conflicts.get(
        "overlap_conflict_count", provenance.get("overlap_conflict_count", 0)
    )
    supplemental = conflicts.get(
        "supplemental_conflict_count",
        provenance.get("supplemental_conflict_count", 0),
    )
    lines = [
        "# Fast Retailing Benchmark Baseline (Step 9M.7)",
        "",
        "- Accounting engine phase: Step 9M.7 (deferred-tax balance diagnostics on 9M.6 base)",
        "- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/`",
        "- Benchmark phase: measurement only — G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed",
        "- Five fiscal periods: 2021-08-31 … 2025-08-31",
        "",
        "## Source hashes",
        "",
    ]
    for src in manifest["sources"]:
        lines.append(
            f"- FY{src['fiscal_year']}: `{src['sha256']}` ({src['bytes']} bytes)"
        )
    lines.extend(
        [
            "",
            f"- Overlap conflicts recorded in conflicts.json: **{overlap}**",
            f"- Supplemental conflicts recorded in conflicts.json: **{supplemental}**",
            f"- Standardized payload: `{STD_JSON.relative_to(ROOT)}`",
            "- Supplemental provenance source-bound: yes",
            "- Portable source-path validation: yes",
            "- Silent repeated-share overwrite removed: yes",
            "- G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed; G7 disagreements retained with verified deterministic selection and provenance.",
            "",
            "## Stage results",
            "",
            "| Stage | Status | Detail |",
            "|---|---|---|",
        ]
    )
    for stage in stages:
        detail = stage.message or stage.exception_type
        detail = detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {stage.stage} | {stage.status} | {detail} |")

    first = ctx.get("first_failure")
    lines.extend(["", "## First failure", ""])
    if first is None:
        lines.append("None — all stages passed.")
    else:
        lines.append(f"- Stage: `{first.stage}`")
        lines.append(f"- Status: `{first.status}`")
        lines.append(f"- Exception: `{first.exception_type}`")
        lines.append(f"- Message: {first.message}")

    lines.extend(["", "## Module applicability (source fixture)", ""])
    for name, info in (ctx.get("modules") or {}).items():
        applicable = info.get("applicable")
        lines.append(f"- **{name}**: {'applicable' if applicable else 'omitted/not applicable'}")
        if name == "lease_liability":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: lease_liability={avail.get('lease_liability')} "
                f"ambiguous={avail.get('ambiguous')}"
            )
        if name == "lease_rou":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: right_of_use_assets={avail.get('right_of_use_assets')} "
                f"ambiguous={avail.get('ambiguous')}"
            )
        if name == "ownership_attribution":
            avail = info.get("availability") or {}
            lines.append(
                f"  - availability: available={avail.get('available')} "
                f"partial={avail.get('partial')} ambiguous={avail.get('ambiguous')}"
            )
        if name == "goodwill_intangibles":
            avail = info.get("availability") or {}
            lines.append(
                "  - availability: "
                f"goodwill={avail.get('goodwill')} "
                f"intangible_assets={avail.get('intangible_assets')} "
                f"goodwill_and_intangibles={avail.get('goodwill_and_intangibles')} "
                f"payments={avail.get('payments_for_intangible_assets')}"
            )
        if name == "deferred_tax":
            avail = info.get("availability") or {}
            lines.append(
                "  - availability: "
                f"deferred_tax_assets={avail.get('deferred_tax_assets')} "
                f"deferred_tax_liabilities={avail.get('deferred_tax_liabilities')} "
                f"ambiguous={avail.get('ambiguous')}"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Temporary Trainer/Answer Key artifacts are not committed.",
            "- Synthetic DEMO / cross-company surfaces remain unchanged.",
            "- Forecasting / valuation remain deferred.",
            "- Comparable diluted-WAS axis (financial-statement units): "
            "306.871785, 306.969624, 307.13887, 307.231804, 307.247804 "
            "(basis=split_adjusted; FY2021 factor=3; FY2022–FY2025 factor=1).",
            "- Raw extracted share facts and G7 conflicts preserved unchanged.",
            "",
        ]
    )
    BASELINE.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--standardized-json",
        type=Path,
        help="Generated standardized.json (default: benchmark reconciled fixture)",
    )
    parser.add_argument("--provenance-json", type=Path)
    parser.add_argument("--conflicts-json", type=Path)
    parser.add_argument("--trainer", type=Path, help="Persisted Trainer workbook")
    parser.add_argument("--answer-key", type=Path, help="Persisted Answer Key workbook")
    parser.add_argument(
        "--require-check-counts",
        action="store_true",
        help="Require pristine (0,0,491,491) and filled (491,0,0,491) Check counts",
    )
    parser.add_argument(
        "--verify-release-pair",
        action="store_true",
        help="Verify practice contract and structural parity on the persisted pair",
    )
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="Skip writing benchmark/fast_retailing/BASELINE.md",
    )
    args = parser.parse_args(argv)

    result = run_audit(
        standardized_json=args.standardized_json,
        provenance_json=args.provenance_json,
        conflicts_json=args.conflicts_json,
        trainer_path=args.trainer,
        answer_key_path=args.answer_key,
        require_check_counts=True if args.require_check_counts else None,
        verify_release_pair=args.verify_release_pair,
    )
    if not args.no_baseline:
        write_baseline(result)
        print(f"wrote {BASELINE.relative_to(ROOT)}")
    for stage in result["stages"]:
        print(f"{stage.stage}: {stage.status}")
        if stage.message:
            print(f"  {stage.message[:300]}")
        if stage.exception_type and stage.status == "fail":
            print(f"  {stage.exception_type}: {stage.message[:300]}")
    failed = any(s.status == "fail" for s in result["stages"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
