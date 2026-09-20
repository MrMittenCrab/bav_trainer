"""Source-grounded issuer fiscal-year labels; never calendar-year-of-end-date."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from core.data.interface import FinancialPeriod, StandardizedFinancials
from core.data.issuer_fiscal import (
    apply_issuer_fiscal_labels,
    issuer_fiscal_label,
    issuer_fiscal_years_from_extracted,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload

ROOT = Path(__file__).resolve().parents[2]
LULU_EXTRACTED = ROOT / "build" / "input" / "lululemon" / "extracted"
LULU_STD = ROOT / "build" / "input" / "lululemon" / "reconciled" / "standardized.json"
EXPECTED = {
    date(2022, 1, 30): 2021,
    date(2023, 1, 29): 2022,
    date(2024, 1, 28): 2023,
    date(2025, 2, 2): 2024,
    date(2026, 2, 1): 2025,
}


def test_lululemon_extracted_mapping_is_issuer_not_calendar_year():
    mapping = issuer_fiscal_years_from_extracted(LULU_EXTRACTED)
    for period, year in EXPECTED.items():
        assert mapping[period] == year
        assert year != period.year
    assert mapping[date(2025, 2, 2)] == 2024
    assert issuer_fiscal_label(2024) == "FY2024"


def test_apply_labels_survives_export_reload():
    from core.current_build import prepare_company_input, resolve_company

    payload = prepare_company_input(resolve_company("Lululemon"))
    mapping = issuer_fiscal_years_from_extracted(LULU_EXTRACTED)
    apply_issuer_fiscal_labels(payload, mapping, require_complete=True)
    assert [period.label for period in payload.periods] == [
        "FY2021",
        "FY2022",
        "FY2023",
        "FY2024",
        "FY2025",
    ]
    assert [period.end_date for period in payload.periods] == list(EXPECTED)
    exported = standardized_to_payload(payload)
    exported.pop("historical_strategy", None)
    reloaded = standardized_from_payload(exported, strict=True)
    assert [(period.end_date, period.label) for period in reloaded.periods] == [
        (period.end_date, period.label) for period in payload.periods
    ]


def test_apply_does_not_infer_missing_period():
    fin = StandardizedFinancials(
        ticker="X",
        company_name="X",
        currency="USD",
        units="USD",
        jurisdiction="US",
        periods=[FinancialPeriod(end_date=date(2025, 2, 2), label="FY2025")],
        income_statement=[],
        balance_sheet=[],
        cash_flow=[],
    )
    try:
        apply_issuer_fiscal_labels(fin, {}, require_complete=True)
    except ValueError as exc:
        assert "2025-02-02" in str(exc)
    else:
        raise AssertionError("missing mapping must fail closed")
