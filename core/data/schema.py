"""Schema helpers for standardized financial statements."""

from __future__ import annotations

from datetime import date
from enum import Enum

from .interface import StandardizedFinancials


class StatementKind(str, Enum):
    INCOME = "income_statement"
    BALANCE = "balance_sheet"
    CASH_FLOW = "cash_flow"


def validate_standardized(data: StandardizedFinancials) -> list[str]:
    """Return blocking validation errors for standardized data."""
    errors: list[str] = []
    if not data.ticker:
        errors.append("ticker is required")
    if not data.periods:
        errors.append("at least one period is required")
    if not data.income_statement:
        errors.append("income statement is empty")
    if not data.balance_sheet:
        errors.append("balance sheet is empty")
    if not data.cash_flow:
        errors.append("cash flow statement is empty")
    for stmt_name, items in (
        ("income_statement", data.income_statement),
        ("balance_sheet", data.balance_sheet),
        ("cash_flow", data.cash_flow),
    ):
        for item in items:
            for pd in data.period_dates():
                if pd not in item.values:
                    errors.append(f"{stmt_name}/{item.label}: missing value for {pd}")
    return errors


def normalize_label(label: str) -> str:
    return " ".join(label.replace("\xa0", " ").split())
