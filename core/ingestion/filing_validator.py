"""Validate ExtractedFiling and bind source-file SHA-256."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from ..data.filing import ExtractedFiling, ExtractedStatementRow, PresentationRole
from ..data.historical_operating_kpis import (
    is_operating_kpi_fact_type,
    validate_operating_kpi_fact,
)


def _match_text(value: str) -> str:
    return " ".join(value.casefold().split())


def source_row_identity(statement: str, row: ExtractedStatementRow) -> str:
    """Deterministic documentary identity for one statement row."""
    return "|".join(
        [
            statement,
            _match_text(row.section),
            _match_text(row.label),
            _match_text(row.suggested_concept),
        ]
    )


@dataclass(frozen=True)
class FilingValidationIssue:
    severity: str  # "error" | "warning"
    code: str
    message: str


@dataclass(frozen=True)
class FilingValidationReport:
    issues: tuple[FilingValidationIssue, ...]
    computed_source_sha256: str | None

    @property
    def errors(self) -> tuple[FilingValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "error")

    @property
    def warnings(self) -> tuple[FilingValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "warning")

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_within_source_root(root: Path, candidate: Path) -> bool:
    """Return True when candidate resolves inside root (or equals root)."""
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def bind_source_file(
    source_file: str,
    *,
    source_root: Path,
    declared_sha256: str = "",
) -> tuple[tuple[FilingValidationIssue, ...], str | None]:
    """Contain a portable source_file and optionally verify its SHA-256."""
    issues: list[FilingValidationIssue] = []
    root = Path(source_root).resolve()
    raw = Path(source_file)
    # Reject POSIX/Windows absolute paths and any ".." segment before
    # existence checks or hashing so escaped candidates are never read.
    if (
        raw.is_absolute()
        or PureWindowsPath(source_file).is_absolute()
        or ".." in raw.parts
    ):
        issues.append(
            FilingValidationIssue(
                "error",
                "invalid_source_path",
                f"source_file must be a portable relative path inside "
                f"source_root: {source_file!r}",
            )
        )
        return tuple(issues), None
    candidate = (root / source_file).resolve()
    if not _is_within_source_root(root, candidate):
        issues.append(
            FilingValidationIssue(
                "error",
                "invalid_source_path",
                f"source_file escapes source_root: {source_file!r}",
            )
        )
        return tuple(issues), None
    if not candidate.is_file():
        issues.append(
            FilingValidationIssue(
                "error",
                "source_file_missing",
                f"source file missing: {candidate}",
            )
        )
        return tuple(issues), None
    computed = hashlib.sha256(candidate.read_bytes()).hexdigest()
    declared = declared_sha256.strip()
    if declared and declared != computed:
        issues.append(
            FilingValidationIssue(
                "error",
                "source_hash_mismatch",
                f"declared source_sha256 {declared} != computed {computed}",
            )
        )
    return tuple(issues), computed


def validate_extracted_filing(
    filing: ExtractedFiling,
    *,
    source_root: Path | None = None,
) -> FilingValidationReport:
    """Validate one filing without mutating documentary content."""
    issues: list[FilingValidationIssue] = []
    computed: str | None = None

    if source_root is not None:
        bind_issues, computed = bind_source_file(
            filing.filing.source_file,
            source_root=source_root,
            declared_sha256=filing.filing.source_sha256,
        )
        issues.extend(bind_issues)

    statements = {
        "income_statement": filing.income_statement,
        "balance_sheet": filing.balance_sheet,
        "cash_flow": filing.cash_flow,
    }
    saw_current = False
    for statement, rows in statements.items():
        seen: set[str] = set()
        for row in rows:
            ident = source_row_identity(statement, row)
            if ident in seen:
                issues.append(
                    FilingValidationIssue(
                        "error",
                        "duplicate_source_row_identity",
                        f"duplicate identity {ident}",
                    )
                )
            seen.add(ident)
            if row.source.page <= 0:
                issues.append(
                    FilingValidationIssue(
                        "error",
                        "missing_source_page",
                        f"{ident} missing positive source page",
                    )
                )
            for period, value in row.values.items():
                if value.presentation_role == PresentationRole.CURRENT_PERIOD:
                    if period != filing.filing.period_end:
                        issues.append(
                            FilingValidationIssue(
                                "error",
                                "current_period_mismatch",
                                f"{ident} current_period {period.isoformat()} "
                                f"!= filing period_end "
                                f"{filing.filing.period_end.isoformat()}",
                            )
                        )
                    else:
                        saw_current = True

    kpi_seen: set[tuple[str, str]] = set()
    for fact in (*filing.note_facts, *filing.share_facts):
        if fact.source.page <= 0:
            issues.append(
                FilingValidationIssue(
                    "error",
                    "missing_source_page",
                    f"supplemental {fact.fact_type} missing positive source page",
                )
            )
        if is_operating_kpi_fact_type(fact.fact_type):
            try:
                validate_operating_kpi_fact(fact)
            except ValueError as exc:
                issues.append(
                    FilingValidationIssue(
                        "error",
                        "invalid_operating_kpi",
                        str(exc),
                    )
                )
            key = (fact.fact_type, fact.period.isoformat())
            if key in kpi_seen:
                issues.append(
                    FilingValidationIssue(
                        "error",
                        "duplicate_operating_kpi_identity",
                        f"duplicate operating-KPI identity {fact.fact_type} "
                        f"for {fact.period.isoformat()}",
                    )
                )
            kpi_seen.add(key)

    if not saw_current:
        issues.append(
            FilingValidationIssue(
                "error",
                "current_period_missing",
                "filing must contain at least one current_period observation "
                "equal to filing.period_end",
            )
        )

    return FilingValidationReport(issues=tuple(issues), computed_source_sha256=computed)
