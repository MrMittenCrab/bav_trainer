"""Validate ExtractedFiling and bind source-file SHA-256."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..data.filing import ExtractedFiling, ExtractedStatementRow, PresentationRole


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


def validate_extracted_filing(
    filing: ExtractedFiling,
    *,
    source_root: Path | None = None,
) -> FilingValidationReport:
    """Validate one filing without mutating documentary content."""
    issues: list[FilingValidationIssue] = []
    computed: str | None = None

    if source_root is not None:
        source_path = Path(source_root) / filing.filing.source_file
        if not source_path.is_file():
            issues.append(
                FilingValidationIssue(
                    "error",
                    "source_file_missing",
                    f"source file missing: {source_path}",
                )
            )
        else:
            computed = hashlib.sha256(source_path.read_bytes()).hexdigest()
            declared = filing.filing.source_sha256.strip()
            if declared and declared != computed:
                issues.append(
                    FilingValidationIssue(
                        "error",
                        "source_hash_mismatch",
                        f"declared source_sha256 {declared} != computed {computed}",
                    )
                )

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

    for fact in (*filing.note_facts, *filing.share_facts):
        if fact.source.page <= 0:
            issues.append(
                FilingValidationIssue(
                    "error",
                    "missing_source_page",
                    f"supplemental {fact.fact_type} missing positive source page",
                )
            )

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
