"""Cross-document reconciliation for standardized financials."""

from __future__ import annotations

from ..data.interface import LineItem, ReconciliationReport, StandardizedFinancials
from ..data.line_identity import line_identity, validate_statement_identities
from ..data.validators import (
    validate_balance_sheet,
    validate_cash_flow,
    validate_income_statement,
)


def _merge_line_items(
    existing: list[LineItem],
    incoming: list[LineItem],
    source: str,
    *,
    statement_name: str = "statement",
) -> tuple[list[LineItem], list[dict]]:
    """Newest-wins merge keyed by canonical line identity (concept + label).

    Duplicate identities within either source list fail before dictionary merge.
    Same identity across ``existing`` and ``incoming`` follows restatement rules.
    """
    validate_statement_identities(existing, f"{statement_name}.existing")
    validate_statement_identities(incoming, f"{statement_name}.incoming")

    by_id: dict[str, LineItem] = {}
    for item in existing:
        by_id[line_identity(item).key()] = item

    conflicts: list[dict] = []
    for item in incoming:
        ident = line_identity(item)
        key = ident.key()
        if key in by_id:
            for pd, val in item.values.items():
                old = by_id[key].values.get(pd)
                if old is not None and val is not None and abs(old - val) > 0.01:
                    if abs(old - val) / max(abs(old), 1) > 0.02:
                        conflicts.append(
                            {
                                "label": ident.label,
                                "concept": ident.concept,
                                "period": pd.isoformat(),
                                "kept": old,
                                "discarded": val,
                                "source": source,
                            }
                        )
                        continue
                by_id[key].values[pd] = val
                if source:
                    by_id[key].source_doc = source
        else:
            item.source_doc = source
            by_id[key] = item

    merged = list(by_id.values())
    validate_statement_identities(merged, statement_name)
    return merged, conflicts


def reconcile_financials(data: StandardizedFinancials) -> ReconciliationReport:
    report = ReconciliationReport()
    report.checksums["income_statement"] = all(validate_income_statement(data).values())
    report.checksums["balance_sheet"] = all(validate_balance_sheet(data).values())
    report.checksums["cash_flow"] = all(validate_cash_flow(data).values())
    if not report.checksums["balance_sheet"]:
        report.warnings.append("Balance sheet does not balance for one or more periods")
    if not report.checksums["cash_flow"]:
        report.warnings.append("Cash flow roll-forward failed for one or more periods")
    return report


def merge_documents(
    base: StandardizedFinancials,
    supplement: StandardizedFinancials,
    source_label: str,
) -> ReconciliationReport:
    """Merge a supplement document into base (newest-wins on overlaps)."""
    report = ReconciliationReport()
    for stmt in ("income_statement", "balance_sheet", "cash_flow"):
        merged, conflicts = _merge_line_items(
            getattr(base, stmt),
            getattr(supplement, stmt),
            source_label,
            statement_name=stmt,
        )
        setattr(base, stmt, merged)
        report.conflicts.extend(conflicts)
    for pd in supplement.period_dates():
        if pd not in base.period_dates():
            base.periods.append(
                next(p for p in supplement.periods if p.end_date == pd)
            )
    base.provenance.extend(supplement.provenance)
    rec = reconcile_financials(base)
    report.checksums = rec.checksums
    report.warnings.extend(rec.warnings)
    return report
