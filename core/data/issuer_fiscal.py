"""Source-grounded issuer fiscal-year labels at the data/presentation boundary.

Period-end dates stay as reported dates. Display labels use the issuer fiscal
year from extracted filings or reconciled current-period evidence. Never derive
the issuer year from the calendar year of the period-end date alone.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from .filing import PresentationRole
from .interface import FinancialPeriod, StandardizedFinancials


def issuer_fiscal_label(year: int) -> str:
    if year <= 0:
        raise ValueError(f"issuer fiscal year must be a positive integer: {year}")
    return f"FY{year}"


def _add(proposed: dict[date, set[int]], period: date, year: int) -> None:
    if not isinstance(year, int) or isinstance(year, bool) or year <= 0:
        raise ValueError(f"invalid issuer fiscal year {year!r} for {period}")
    proposed.setdefault(period, set()).add(year)


def _finalize(proposed: dict[date, set[int]]) -> dict[date, int]:
    mapping: dict[date, int] = {}
    for period, years in proposed.items():
        if len(years) != 1:
            raise ValueError(
                f"conflicting issuer fiscal years for {period.isoformat()}: "
                f"{sorted(years)}"
            )
        mapping[period] = next(iter(years))
    return mapping


def issuer_fiscal_years_from_extracted(extracted_dir: Path) -> dict[date, int]:
    """Map period-end dates to issuer fiscal years from extracted filing JSON."""
    if not extracted_dir.is_dir():
        raise ValueError(f"extracted directory is required: {extracted_dir}")
    proposed: dict[date, set[int]] = {}
    found = False
    for path in sorted(extracted_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        filing = payload.get("filing")
        report = payload.get("report")
        if isinstance(filing, dict) and filing.get("fiscal_year") and filing.get("period_end"):
            found = True
            year = int(filing["fiscal_year"])
            current = date.fromisoformat(str(filing["period_end"]))
            _add(proposed, current, year)
            comparatives: set[date] = set()
            statements = payload.get("statements") or {}
            if isinstance(statements, dict):
                for rows in statements.values():
                    if not isinstance(rows, list):
                        continue
                    for item in rows:
                        values = item.get("values") if isinstance(item, dict) else None
                        if not isinstance(values, dict):
                            continue
                        for raw_period, cell in values.items():
                            period = date.fromisoformat(str(raw_period))
                            role = cell.get("presentation_role") if isinstance(cell, dict) else None
                            if role == PresentationRole.CURRENT_PERIOD.value:
                                _add(proposed, period, year)
                            elif role == PresentationRole.COMPARATIVE.value:
                                comparatives.add(period)
            for index, period in enumerate(sorted(
                (item for item in comparatives if item != current), reverse=True
            )):
                _add(proposed, period, year - 1 - index)
        elif isinstance(report, dict) and report.get("fiscal_year") and report.get("fiscal_year_end"):
            found = True
            _add(
                proposed,
                date.fromisoformat(str(report["fiscal_year_end"])),
                int(report["fiscal_year"]),
            )
    if not found:
        raise ValueError(f"no issuer fiscal-year evidence in {extracted_dir}")
    return _finalize(proposed)


def issuer_fiscal_years_from_reconciled(reconciled) -> dict[date, int]:
    """Map period-end dates from reconciled current-period / comparative evidence."""
    proposed: dict[date, set[int]] = {}
    current_by_filing: dict[int, date] = {}
    comparatives_by_filing: dict[int, set[date]] = defaultdict(set)
    for value in reconciled.values:
        role = value.selected.presentation_role
        year = value.selected.filing_year
        if role == PresentationRole.CURRENT_PERIOD:
            _add(proposed, value.period, year)
            current_by_filing[year] = value.period
        elif role in (PresentationRole.COMPARATIVE, PresentationRole.RESTATED_COMPARATIVE):
            comparatives_by_filing[year].add(value.period)
    for year, periods in comparatives_by_filing.items():
        current = current_by_filing.get(year)
        extras = sorted((item for item in periods if item != current), reverse=True)
        for index, period in enumerate(extras):
            _add(proposed, period, year - 1 - index)
    return _finalize(proposed)


def apply_issuer_fiscal_labels(
    financials: StandardizedFinancials,
    mapping: dict[date, int],
    *,
    require_complete: bool = True,
) -> StandardizedFinancials:
    """Replace presentation labels with issuer FY labels; keep period-end dates."""
    missing = [
        period.end_date
        for period in financials.periods
        if period.end_date not in mapping
    ]
    if missing and require_complete:
        raise ValueError(
            "issuer fiscal-year mapping missing period-end "
            + ", ".join(item.isoformat() for item in missing)
        )
    financials.periods = [
        FinancialPeriod(
            end_date=period.end_date,
            label=(
                issuer_fiscal_label(mapping[period.end_date])
                if period.end_date in mapping
                else period.label
            ),
            is_interim=period.is_interim,
        )
        for period in financials.periods
    ]
    return financials
