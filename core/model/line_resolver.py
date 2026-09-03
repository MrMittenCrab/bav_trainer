"""Canonical financial statement line resolver.

Python expected-value math and Excel reference-model construction must resolve
the same ``LineItem`` for each concept through this module only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..data.interface import LineItem
from ..data.schema import normalize_label


class LineResolutionError(ValueError):
    """Base class for line-resolution failures."""


class MissingLineError(LineResolutionError):
    """Raised when a required concept cannot be resolved."""


class AmbiguousLineError(LineResolutionError):
    """Raised when two or more lines match at the same priority."""


@dataclass(frozen=True)
class ResolvedLine:
    item: LineItem | None
    index: int | None


def _norm_text(text: str) -> str:
    s = normalize_label(text).lower()
    for ch in ("'", "'", "`", "´"):
        s = s.replace(ch, "'")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return " ".join(s.split())


# Exact normalized label aliases (priority 2).
_EXACT_ALIASES: dict[str, frozenset[str]] = {
    "revenue": frozenset({"revenue", "turnover"}),
    "net_income": frozenset(
        {"profit for the year", "net income", "net profit", "profit for the period"}
    ),
    "pretax_income": frozenset(
        {
            "profit before tax",
            "profit before taxation",
            "pretax income",
            "pre tax income",
            "profit before income tax",
        }
    ),
    "tax_expense": frozenset(
        {
            "income tax expense",
            "tax expense",
            "taxation",
            "income tax",
            "taxation expense",
        }
    ),
    "interest_expense": frozenset(
        {"finance cost", "finance costs", "interest expense", "interest expenses"}
    ),
    "interest_income": frozenset({"finance income", "interest income"}),
    "total_equity": frozenset(
        {
            "total equity",
            "shareholders' equity",
            "shareholders equity",
            "shareholders' funds",
            "shareholders funds",
            "equity attributable to owners of the company",
            "owners' equity",
            "owners equity",
        }
    ),
    "total_assets": frozenset({"total assets"}),
    "total_liabilities": frozenset({"total liabilities"}),
}


def _safe_pattern_match(concept: str, label_norm: str) -> bool:
    """Narrow pattern aliases (priority 3). Avoid unrestricted substrings."""
    if concept == "revenue":
        # Allow bare "sales" / "net sales" but never "cost of sales".
        if "cost of sales" in label_norm or "cost of goods" in label_norm:
            return False
        return label_norm in {"sales", "net sales", "net revenue"}
    if concept == "tax_expense":
        # Do not match "profit before tax" / "pretax".
        if "before tax" in label_norm or "before taxation" in label_norm:
            return False
        if label_norm.startswith("pre tax") or label_norm.startswith("pretax"):
            return False
        return label_norm.endswith("tax expense") or label_norm.endswith("taxation")
    if concept == "total_equity":
        if "attributable to owners" in label_norm and "equity" in label_norm:
            return True
        if label_norm.startswith("total equity"):
            return True
        return False
    if concept == "total_assets":
        return label_norm == "total assets"
    if concept == "total_liabilities":
        return label_norm == "total liabilities"
    return False


def resolve_line(
    items: list[LineItem],
    concept: str,
    *,
    required: bool = False,
) -> ResolvedLine:
    """Resolve a canonical financial concept to a statement line.

    Priority:
      1. exact normalized ``LineItem.concept``
      2. exact normalized label aliases
      3. narrowly defined safe label patterns
    """
    if concept not in _EXACT_ALIASES:
        raise ValueError(f"Unknown financial concept: {concept!r}")

    concept_norm = _norm_text(concept)

    def _collect(predicate) -> list[tuple[int, LineItem]]:
        hits: list[tuple[int, LineItem]] = []
        for idx, item in enumerate(items):
            if predicate(item):
                hits.append((idx, item))
        return hits

    # Priority 1 — explicit concept field
    p1 = _collect(lambda it: bool(it.concept) and _norm_text(it.concept) == concept_norm)
    if len(p1) > 1:
        labels = ", ".join(repr(it.label) for _, it in p1)
        raise AmbiguousLineError(
            f"Ambiguous concept={concept!r} via LineItem.concept: {labels}"
        )
    if len(p1) == 1:
        idx, item = p1[0]
        return ResolvedLine(item=item, index=idx)

    aliases = _EXACT_ALIASES[concept]

    # Priority 2 — exact label aliases
    p2 = _collect(lambda it: _norm_text(it.label) in aliases)
    if len(p2) > 1:
        labels = ", ".join(repr(it.label) for _, it in p2)
        raise AmbiguousLineError(
            f"Ambiguous concept={concept!r} via exact label aliases: {labels}"
        )
    if len(p2) == 1:
        idx, item = p2[0]
        return ResolvedLine(item=item, index=idx)

    # Priority 3 — safe patterns
    p3 = _collect(lambda it: _safe_pattern_match(concept, _norm_text(it.label)))
    if len(p3) > 1:
        labels = ", ".join(repr(it.label) for _, it in p3)
        raise AmbiguousLineError(
            f"Ambiguous concept={concept!r} via safe patterns: {labels}"
        )
    if len(p3) == 1:
        idx, item = p3[0]
        return ResolvedLine(item=item, index=idx)

    if required:
        raise MissingLineError(f"Required concept {concept!r} not found in statement lines")
    return ResolvedLine(item=None, index=None)


def workbook_row_for(resolved: ResolvedLine, *, start_row: int = 7) -> int | None:
    """Convert a resolved statement index to the workbook source-sheet row."""
    if resolved.index is None:
        return None
    return start_row + resolved.index
