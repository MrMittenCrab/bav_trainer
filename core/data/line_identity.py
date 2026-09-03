"""Canonical statement-line identity for ingestion, merge, and classification."""

from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict

from .interface import LineItem
from .schema import normalize_label


class AmbiguousStatementIdentityError(ValueError):
    """Statement rows cannot be distinguished safely by concept+label identity."""


@dataclass(frozen=True)
class LineIdentity:
    concept: str
    label: str

    def key(self) -> str:
        return f"concept={self.concept}|label={self.label}"

    def __str__(self) -> str:
        return self.key()


def _canonical_label(label: str) -> str:
    """Whitespace/NBSP-normalized, case-insensitive comparison text for labels."""
    return normalize_label(label or "").casefold()


def line_identity(item: LineItem) -> LineIdentity:
    """Stable identity for a statement row. Does not infer concepts from labels.

    Displayed labels are case-insensitive for identity; concept IDs stay exact
    after whitespace/NBSP normalization. ``item.label`` is never mutated.
    """
    raw_concept = (item.concept or "").strip()
    concept = normalize_label(raw_concept) if raw_concept else ""
    return LineIdentity(
        concept=concept,
        label=_canonical_label(item.label or ""),
    )


def validate_statement_identities(items: list[LineItem], statement_name: str) -> None:
    """Reject duplicate or ambiguous identities within one statement."""
    by_identity: dict[LineIdentity, list[LineItem]] = defaultdict(list)
    by_label: dict[str, list[LineItem]] = defaultdict(list)

    for item in items:
        ident = line_identity(item)
        by_identity[ident].append(item)
        by_label[ident.label].append(item)

    for ident, group in by_identity.items():
        if len(group) > 1:
            raise AmbiguousStatementIdentityError(
                f"{statement_name}: duplicate identity {ident} "
                f"(label={ident.label!r}, concept={ident.concept!r}) appears {len(group)} times"
            )

    for label, group in by_label.items():
        if len(group) < 2:
            continue
        concepts = [line_identity(i).concept for i in group]
        nonempty = [c for c in concepts if c]
        empty = [c for c in concepts if not c]
        # Distinct non-empty concepts with same label are allowed (caught above only if
        # identity fully collides). Ambiguous when any row lacks concept, or when
        # multiple rows share the empty-concept identity (already raised above).
        if empty and nonempty:
            raise AmbiguousStatementIdentityError(
                f"{statement_name}: ambiguous label {label!r} — "
                f"concepted rows {nonempty!r} mixed with conceptless duplicate(s); "
                f"disambiguate with concepts on every same-label row"
            )
        if len(empty) >= 2:
            raise AmbiguousStatementIdentityError(
                f"{statement_name}: ambiguous label {label!r} — "
                f"{len(empty)} rows lack concept metadata; "
                f"provide distinct concepts or remove the duplicate"
            )


def validate_financials_identities(financials) -> None:
    """Validate IS / BS / CF identities on a StandardizedFinancials object."""
    validate_statement_identities(financials.income_statement, "income_statement")
    validate_statement_identities(financials.balance_sheet, "balance_sheet")
    validate_statement_identities(financials.cash_flow, "cash_flow")
