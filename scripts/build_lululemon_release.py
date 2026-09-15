#!/usr/bin/env python3
"""Build the persistent Lululemon Trainer / Answer Key release pair.

Uses existing validated extracted filings and the checked-in reconciled
standardized payload. Does not invent interest. Forecasting remains dormant.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RECONCILED = BENCH / "reconciled"
RELEASE = ROOT / "release" / "lululemon"
SUPPORTING = RELEASE / "supporting"
TRAINER_NAME = "Lululemon_Trainer.xlsx"
ANSWER_NAME = "Lululemon_Answer_Key.xlsx"
README = RELEASE / "README.md"
AVAILABILITY = RELEASE / "availability.json"

EXPECTED_SPECS = 293


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_extracted_filings() -> None:
    from core.ingestion.filing_cli import load_and_validate_extracted_dir

    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    if len(validated) != 4:
        raise ValueError(f"expected 4 filings, got {len(validated)}")
    for filing, report in validated:
        if not report.ok:
            errors = "; ".join(f"{i.code}: {i.message}" for i in report.errors)
            raise ValueError(
                f"filing validation failed for {filing.filing.source_file}: {errors}"
            )


def copy_reconciled_supporting(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("standardized.json", "provenance.json", "conflicts.json"):
        src = RECONCILED / name
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, dest / name)
    return dest / "standardized.json"


def build_workbooks(standardized_json: Path, out_dir: Path) -> tuple[Path, Path]:
    from core.data.standardized_io import standardized_from_payload
    from core.trainer.workbook import build_training_workbook

    payload = json.loads(standardized_json.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    trainer, answer = build_training_workbook(fin, out_dir / TRAINER_NAME)
    return trainer, answer


def write_availability(standardized_json: Path, dest: Path) -> None:
    from core.data.standardized_io import standardized_from_payload
    from core.model.period_axis import canonical_fiscal_periods
    from core.model.source_availability import (
        assess_interest_availability,
        availability_payload,
    )

    payload = json.loads(standardized_json.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    periods = canonical_fiscal_periods(fin)
    availability = assess_interest_availability(fin, periods)
    dest.write_text(
        json.dumps(availability_payload(availability), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_readme(trainer: Path, answer: Path) -> None:
    text = f"""# Lululemon historical release pair

Human-reviewable Trainer and Answer Key generated from checked-in Lululemon
source-grounded filings. Standalone interest lines are not present in the
supplied statements; interest-dependent outputs are marked Source unavailable
and excluded from practice and Check. No interest amounts were invented.

## Dependencies

- Repository checkout with `benchmark/lululemon/source/` PDFs
- Extracted filings under `benchmark/lululemon/extracted/`
- Checked-in reconciled payload under `benchmark/lululemon/reconciled/`
- Python environment with project dependencies installed

## Build

From the repository root:

```text
python scripts/build_lululemon_release.py
```

## Workbooks

- Trainer: `{trainer.relative_to(ROOT)}`
- Answer Key: `{answer.relative_to(ROOT)}`
- Answer Key semantic map: `{answer.with_suffix('.component_map.json').relative_to(ROOT)}`
- Availability: `{AVAILABILITY.relative_to(ROOT)}`
- Generated standardized / provenance / conflicts: `{SUPPORTING.relative_to(ROOT)}/`

## Check usage

Keep the Trainer and matching Answer Key (plus Answer Key sidecars) in the same
directory. From the repository root:

```text
python -m core check --workbook {trainer.relative_to(ROOT)}
```

Pristine Trainer practice cells should all be blank (yellow). Unavailable
interest-dependent outputs are not practice cells. Check never prints or
inserts answers. Open the Answer Key for formulas and Notes.

Forecasting and valuation remain dormant in this historical release.
"""
    README.write_text(text, encoding="utf-8")


def verify_staged(trainer: Path, answer: Path, standardized_json: Path) -> None:
    from core.data.standardized_io import standardized_from_payload
    from core.engine.reference_model import ReferenceModelBuilder
    from core.trainer.checker import check_workbook
    from core.trainer.semantic_io import load_semantic_map, parse_cell_ref
    from openpyxl import load_workbook

    payload = json.loads(standardized_json.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    builder = ReferenceModelBuilder(fin)
    if len(builder.expected_specs) != EXPECTED_SPECS:
        raise RuntimeError(
            f"Lululemon expected_specs={len(builder.expected_specs)} != {EXPECTED_SPECS}"
        )
    smap = load_semantic_map(answer)
    if len(smap.all_ordered()) != EXPECTED_SPECS:
        raise RuntimeError(
            f"Lululemon registered components={len(smap.all_ordered())} != {EXPECTED_SPECS}"
        )
    blank = check_workbook(trainer)
    if (blank.blank, blank.correct, blank.incorrect, blank.total) != (
        EXPECTED_SPECS,
        0,
        0,
        EXPECTED_SPECS,
    ):
        raise RuntimeError(
            f"blank Check {blank.correct}/{blank.incorrect}/{blank.blank}/{blank.total}"
        )
    wb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    filled_dir = trainer.parent / "_filled_check"
    filled_dir.mkdir(exist_ok=True)
    filled_trainer = filled_dir / trainer.name
    filled_answer = filled_dir / answer.name
    shutil.copy2(answer, filled_answer)
    answer_map = answer.with_suffix(".component_map.json")
    if answer_map.is_file():
        shutil.copy2(answer_map, filled_dir / answer_map.name)
    answer_assumptions = answer.with_suffix(".assumptions.json")
    if answer_assumptions.is_file():
        shutil.copy2(answer_assumptions, filled_dir / answer_assumptions.name)
    wb.save(filled_trainer)
    wb.close()
    try:
        filled = check_workbook(filled_trainer)
    finally:
        shutil.rmtree(filled_dir, ignore_errors=True)
    if (filled.correct, filled.incorrect, filled.blank, filled.total) != (
        EXPECTED_SPECS,
        0,
        0,
        EXPECTED_SPECS,
    ):
        raise RuntimeError(
            f"filled Check {filled.correct}/{filled.incorrect}/{filled.blank}/{filled.total}"
        )


def _replace_release(staged_dir: Path, staged_trainer: Path, staged_answer: Path) -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    for src in staged_dir.iterdir():
        dest = RELEASE / src.name
        if src.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
    write_readme(RELEASE / staged_trainer.name, RELEASE / staged_answer.name)


def main() -> int:
    try:
        validate_extracted_filings()
        with tempfile.TemporaryDirectory(prefix="lulu_release_") as raw:
            staged = Path(raw)
            supporting = staged / "supporting"
            standardized = copy_reconciled_supporting(supporting)
            trainer, answer = build_workbooks(standardized, staged)
            write_availability(standardized, staged / "availability.json")
            verify_staged(trainer, answer, standardized)
            repeat_trainer, repeat_answer = build_workbooks(
                standardized, staged / "repeat"
            )
            first_map = (answer.with_suffix(".component_map.json")).read_text(
                encoding="utf-8"
            )
            repeat_map = (repeat_answer.with_suffix(".component_map.json")).read_text(
                encoding="utf-8"
            )
            if first_map != repeat_map:
                raise RuntimeError("Lululemon repeat-build semantic map is not deterministic")
            shutil.rmtree(staged / "repeat")
            _replace_release(staged, trainer, answer)
    except Exception as exc:  # noqa: BLE001 — CLI must fail nonzero with message
        print(f"error: {exc}", file=sys.stderr)
        return 1

    trainer = RELEASE / TRAINER_NAME
    answer = RELEASE / ANSWER_NAME
    print(f"Trainer: {trainer.relative_to(ROOT)}")
    print(f"Answer Key: {answer.relative_to(ROOT)}")
    print(f"Supporting: {SUPPORTING.relative_to(ROOT)}")
    for path in (
        trainer,
        answer,
        answer.with_suffix(".component_map.json"),
        AVAILABILITY,
    ):
        if path.is_file():
            print(f"  sha256 {path.name}={_sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
