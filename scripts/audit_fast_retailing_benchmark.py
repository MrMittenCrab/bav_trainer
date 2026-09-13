#!/usr/bin/env python3
"""Stage-by-stage audit of the Fast Retailing benchmark against the current engine.

Writes BASELINE.md. Does not patch production accounting logic.
"""

from __future__ import annotations

import json
import tempfile
import traceback
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark" / "fast_retailing"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"
MANIFEST = BENCH / "source_manifest.json"
BASELINE = BENCH / "BASELINE.md"
MODEL_COMMIT = "26f22b7"


@dataclass
class StageResult:
    stage: str
    status: str  # pass | fail | skipped
    exception_type: str = ""
    message: str = ""


def _load_payload() -> dict[str, Any]:
    return json.loads(STD_JSON.read_text(encoding="utf-8"))


def _module_applicability(fin, anchor=None) -> dict[str, Any]:
    from core.model.earnings_quality import earnings_quality_availability
    from core.model.fixed_asset import fixed_asset_applicable
    from core.model.lease_liability import (
        lease_liability_applicable,
        lease_liability_availability,
    )
    from core.model.per_share import per_share_available
    from core.model.working_capital import working_capital_applicable

    lease_avail = lease_liability_availability(fin)
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
        "per_share": {"applicable": per_share_available(fin)},
        "normalization": {
            "applicable": False,
            "detail": "no normalization assumptions supplied for benchmark audit",
        },
    }


def run_audit() -> dict[str, Any]:
    stages: list[StageResult] = []
    context: dict[str, Any] = {
        "modules": {},
        "first_failure": None,
        "workbook_paths": {},
    }

    # Stage 1
    try:
        payload = _load_payload()
        assert payload["ticker"] == "6288.HK"
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
                    f"fixed_asset_specs={len(builder.fixed_asset_specs)}"
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

    # Stage 5
    try:
        from core.trainer.workbook import build_training_workbook

        with tempfile.TemporaryDirectory(prefix="fr_bench_") as tmp:
            trainer, answer = build_training_workbook(
                fin, Path(tmp) / "FastRetailing_Trainer.xlsx"
            )
            context["workbook_paths"] = {
                "trainer": str(trainer),
                "answer": str(answer),
                "note": "temporary only; not committed",
            }
            stages.append(StageResult("5_workbook_generation", "pass"))

            # Stage 6
            try:
                from core.trainer.checker import check_workbook

                summary = check_workbook(trainer)
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
                return {"stages": stages, "context": context}

            # Stage 7
            try:
                from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
                from openpyxl import load_workbook

                smap = load_semantic_map(answer)
                wb = load_workbook(trainer, data_only=False)
                for comp in smap.all_ordered():
                    row, col = parse_cell_ref(comp.cell)
                    wb[comp.tab].cell(row=row, column=col).value = comp.formula
                wb.save(trainer)
                wb.close()
                filled = check_workbook(trainer)
                if filled.incorrect or filled.blank:
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
    lines = [
        "# Fast Retailing Benchmark Baseline (Step 9M.1)",
        "",
        f"- Model commit audited: `{MODEL_COMMIT}` (Step 9L.1 accounting engine)",
        "- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/`",
        "- Benchmark phase: measurement only — no production accounting fixes applied",
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
            f"- Standardized payload: `{STD_JSON.relative_to(ROOT)}`",
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

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Temporary Trainer/Answer Key artifacts are not committed.",
            "- Synthetic DEMO / cross-company surfaces remain unchanged.",
            "- Forecasting / valuation remain deferred.",
            "",
        ]
    )
    BASELINE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = run_audit()
    write_baseline(result)
    print(f"wrote {BASELINE.relative_to(ROOT)}")
    for stage in result["stages"]:
        print(f"{stage.stage}: {stage.status}")
        if stage.message:
            print(f"  {stage.message[:300]}")


if __name__ == "__main__":
    main()
