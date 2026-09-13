"""Shared helpers for filing-JSON CLI commands."""

from __future__ import annotations

from pathlib import Path

from ..data.filing import ExtractedFiling
from .filing_json import load_extracted_filing
from .filing_validator import FilingValidationReport, validate_extracted_filing


def list_extracted_json_files(path: Path) -> list[Path]:
    """Return lexical *.json files for a file or non-recursive directory."""
    target = Path(path)
    if target.is_file():
        if target.suffix.lower() != ".json":
            raise ValueError(f"expected a .json file: {target}")
        return [target]
    if not target.is_dir():
        raise ValueError(f"extracted path not found: {target}")
    files = sorted(
        p for p in target.iterdir() if p.is_file() and p.suffix.lower() == ".json"
    )
    if not files:
        raise ValueError(f"no extracted JSON files in {target}")
    return files


def load_and_validate_extracted_dir(
    extracted: Path,
    *,
    source_root: Path,
) -> list[tuple[ExtractedFiling, FilingValidationReport]]:
    """Load and validate all extracted filings under a directory/file."""
    results: list[tuple[ExtractedFiling, FilingValidationReport]] = []
    for path in list_extracted_json_files(extracted):
        filing = load_extracted_filing(path)
        report = validate_extracted_filing(filing, source_root=source_root)
        results.append((filing, report))
    return results
