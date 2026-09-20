#!/usr/bin/env python3
"""Build the persistent Fast Retailing Trainer / Answer Key release pair.

Uses production validate → reconcile → standardize → workbook-generation entry
points. Forecasting and valuation remain dormant.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BENCH = ROOT / "build" / "input" / "fast_retailing"
MANIFEST = BENCH / "source_manifest.json"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RELEASE = ROOT / "release" / "fast_retailing"
SUPPORTING = RELEASE / "supporting"
TRAINER_NAME = "FastRetailing_Trainer.xlsx"
ANSWER_NAME = "FastRetailing_Answer_Key.xlsx"
README = RELEASE / "README.md"

EXPECTED_YEARS = (2021, 2022, 2023, 2024, 2025)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest.get("sources") or []
    years = {entry["fiscal_year"] for entry in sources}
    if years != set(EXPECTED_YEARS):
        raise ValueError(f"manifest years {sorted(years)} != {list(EXPECTED_YEARS)}")
    for entry in sources:
        path = ROOT / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(f"missing source PDF: {path}")
        data = path.read_bytes()
        if len(data) != entry["bytes"]:
            raise ValueError(
                f"{path.name}: bytes {len(data)} != manifest {entry['bytes']}"
            )
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"{path.name}: sha256 mismatch")


def validate_extracted_filings() -> None:
    from core.ingestion.filing_cli import load_and_validate_extracted_dir

    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    years = set()
    for filing, report in validated:
        if not report.ok:
            errors = "; ".join(f"{i.code}: {i.message}" for i in report.errors)
            raise ValueError(
                f"filing validation failed for {filing.filing.source_file}: {errors}"
            )
        years.add(int(filing.filing.fiscal_year))
    file_years = {int(p.stem.replace("FY", "")) for p in EXTRACTED.glob("FY*.json")}
    if file_years != set(EXPECTED_YEARS):
        raise ValueError(
            f"extracted FY files {sorted(file_years)} != {list(EXPECTED_YEARS)}"
        )
    if years != set(EXPECTED_YEARS):
        raise ValueError(f"validated filing years {sorted(years)} != {list(EXPECTED_YEARS)}")
    if len(validated) != len(EXPECTED_YEARS):
        raise ValueError(f"expected {len(EXPECTED_YEARS)} filings, got {len(validated)}")


def reconcile_to_supporting() -> Path:
    from core.data.standardized_io import standardized_to_payload
    from core.ingestion.filing_cli import load_and_validate_extracted_dir
    from core.ingestion.filing_reconciler import reconcile_filings
    from core.ingestion.filing_standardizer import (
        reconciliation_conflicts_payload,
        reconciliation_provenance_payload,
        standardize_reconciled,
    )

    validated = load_and_validate_extracted_dir(EXTRACTED, source_root=SOURCE)
    if any(not report.ok for _, report in validated):
        raise ValueError("reconcile aborted: validation errors present")
    reconciled = reconcile_filings(validated)
    fin = standardize_reconciled(reconciled)
    provenance = reconciliation_provenance_payload(reconciled)
    conflicts = reconciliation_conflicts_payload(reconciled)

    SUPPORTING.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "standardized.json": standardized_to_payload(fin),
        "provenance.json": provenance,
        "conflicts.json": conflicts,
    }
    for name, payload in artifacts.items():
        (SUPPORTING / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return SUPPORTING / "standardized.json"


def build_workbooks(standardized_json: Path) -> tuple[Path, Path]:
    from core.data.standardized_io import standardized_from_payload
    from core.trainer.workbook import build_training_workbook

    payload = json.loads(standardized_json.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    RELEASE.mkdir(parents=True, exist_ok=True)
    trainer, answer = build_training_workbook(
        fin, RELEASE / TRAINER_NAME
    )
    return trainer, answer


def write_readme(trainer: Path, answer: Path) -> None:
    text = f"""# Fast Retailing historical release pair

Human-reviewable Trainer and Answer Key generated from checked-in Fast Retailing
source-grounded filings through the production pipeline.

## Dependencies

- Repository checkout with `build/input/fast_retailing/source/` PDFs matching
  `build/input/fast_retailing/source_manifest.json`
- Extracted filings under `build/input/fast_retailing/extracted/FY2021.json` …
  `FY2025.json`
- Python environment with project dependencies installed

## Build

From the repository root:

```text
python scripts/build_fast_retailing_release.py
```

## Workbooks

- Trainer: `{trainer.relative_to(ROOT)}`
- Answer Key: `{answer.relative_to(ROOT)}`
- Answer Key semantic map: `{answer.with_suffix('.component_map.json').relative_to(ROOT)}`
- Generated standardized / provenance / conflicts: `{SUPPORTING.relative_to(ROOT)}/`
- Interest availability: `{RELEASE.relative_to(ROOT)}/availability.json`

## Check usage

Keep the Trainer and matching Answer Key (plus Answer Key sidecars) in the same
directory. From the repository root:

```text
python -m core check --workbook {trainer.relative_to(ROOT)}
```

Pristine Trainer practice cells should all be blank (yellow). Check never prints
or inserts answers. Open the Answer Key for formulas and Notes.

Forecasting and valuation remain dormant in this historical release.
"""
    README.write_text(text, encoding="utf-8")


def write_availability(standardized_json: Path) -> Path:
    from core.data.standardized_io import standardized_from_payload
    from core.model.period_axis import canonical_fiscal_periods
    from core.model.source_availability import (
        assess_interest_availability,
        availability_payload,
    )

    payload = json.loads(standardized_json.read_text(encoding="utf-8"))
    fin = standardized_from_payload(payload)
    dest = RELEASE / "availability.json"
    dest.write_text(
        json.dumps(
            availability_payload(
                assess_interest_availability(fin, canonical_fiscal_periods(fin))
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return dest


def verify_release(trainer: Path, answer: Path) -> None:
    from scripts.audit_fast_retailing_benchmark import run_audit

    result = run_audit(
        standardized_json=SUPPORTING / "standardized.json",
        provenance_json=SUPPORTING / "provenance.json",
        conflicts_json=SUPPORTING / "conflicts.json",
        trainer_path=trainer,
        answer_key_path=answer,
        require_check_counts=True,
        verify_release_pair=True,
    )
    failed = [s for s in result["stages"] if s.status == "fail"]
    if failed:
        detail = "; ".join(f"{s.stage}: {s.message or s.exception_type}" for s in failed)
        raise RuntimeError(f"release audit failed: {detail}")
    if result["context"].get("first_failure") is not None:
        first = result["context"]["first_failure"]
        raise RuntimeError(
            f"release audit first_failure={first.stage}: {first.message}"
        )


def main() -> int:
    try:
        validate_source_manifest()
        validate_extracted_filings()
        standardized = reconcile_to_supporting()
        trainer, answer = build_workbooks(standardized)
        write_readme(trainer, answer)
        write_availability(standardized)
        verify_release(trainer, answer)
    except Exception as exc:  # noqa: BLE001 — CLI must fail nonzero with message
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Trainer: {trainer.relative_to(ROOT)}")
    print(f"Answer Key: {answer.relative_to(ROOT)}")
    print(f"Supporting: {SUPPORTING.relative_to(ROOT)}")
    for path in (trainer, answer, answer.with_suffix(".component_map.json"), RELEASE / "availability.json"):
        if path.is_file():
            print(f"  sha256 {path.name}={_sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
