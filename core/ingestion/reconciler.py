"""Cross-document reconciliation for standardized financials."""

from __future__ import annotations

from datetime import date

from ..data.interface import LineItem, ReconciliationReport, StandardizedFinancials
from ..data.validators import (
    validate_balance_sheet,
    validate_cash_flow,
    validate_income_statement,
)


def _merge_line_items(
    existing: list[LineItem],
    incoming: list[LineItem],
    source: str,
) -> tuple[list[LineItem], list[dict]]:
    """Newest-wins merge keyed by normalized label."""
    by_label: dict[str, LineItem] = {i.label: i for i in existing}
    conflicts: list[dict] = []
    for item in incoming:
        key = item.label
        if key in by_label:
            for pd, val in item.values.items():
                old = by_label[key].values.get(pd)
                if old is not None and val is not None and abs(old - val) > 0.01:
                    if abs(old - val) / max(abs(old), 1) > 0.02:
                        conflicts.append(
                            {
                                "label": key,
                                "period": pd.isoformat(),
                                "kept": old,
                                "discarded": val,
                                "source": source,
                            }
                        )
                        continue
                by_label[key].values[pd] = val
                if source:
                    by_label[key].source_doc = source
        else:
            item.source_doc = source
            by_label[key] = item
    return list(by_label.values()), conflicts


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
