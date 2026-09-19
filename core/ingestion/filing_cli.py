"""Shared helpers for filing-JSON CLI commands."""

from __future__ import annotations

from pathlib import Path

from ..data.filing import ExtractedFiling
from .filing_json import load_extracted_filing, load_extracted_json_object
from .filing_validator import FilingValidationReport, validate_extracted_filing
from .management_kpi import (
    KIND_ANNUAL_FILING,
    KIND_MANAGEMENT_KPI,
    BoundManagementDocument,
    bind_management_documents,
    classify_extracted_payload,
    load_management_kpi_document,
)


class ValidatedExtractedDirectory(list):
    """Validated statement filings plus bound management-KPI documents."""

    def __init__(
        self,
        filings: list[tuple[ExtractedFiling, FilingValidationReport]],
        management_documents: tuple[BoundManagementDocument, ...] = (),
    ) -> None:
        super().__init__(filings)
        self.management_documents = tuple(management_documents)


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
) -> ValidatedExtractedDirectory:
    """Load and validate mixed extracted filings and management-KPI documents."""
    filings: list[tuple[ExtractedFiling, FilingValidationReport]] = []
    management_docs = []
    for path in list_extracted_json_files(extracted):
        payload = load_extracted_json_object(path)
        kind = classify_extracted_payload(payload, path=path)
        if kind == KIND_MANAGEMENT_KPI:
            management_docs.append(load_management_kpi_document(path))
            continue
        if kind != KIND_ANNUAL_FILING:
            raise ValueError(f"{path.name}: unknown extracted schema")
        try:
            filing = load_extracted_filing(path)
        except ValueError as exc:
            raise ValueError(f"{path.name}: {exc}") from exc
        report = validate_extracted_filing(filing, source_root=source_root)
        filings.append((filing, report))
    if not filings:
        raise ValueError(f"no extracted filing JSON files in {extracted}")
    bound = (
        bind_management_documents(
            management_docs, filings, source_root=source_root
        )
        if management_docs
        else ()
    )
    if bound and all(item.ok for item in bound):
        from .management_kpi import admit_management_documents

        admit_management_documents(bound, selected_store_facts=())
    return ValidatedExtractedDirectory(filings, bound)
