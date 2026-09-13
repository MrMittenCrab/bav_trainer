"""Deterministic synthetic non-financial company fixtures for Step 9G.1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from core.data.interface import (
    FinancialPeriod,
    HistoricalShareData,
    LineItem,
    StandardizedFinancials,
)
from core.model.per_share import SUPPORTED_SHARE_SCALE_BASIS

PERIODS = tuple(date(y, 12, 31) for y in range(2021, 2026))


@dataclass(frozen=True)
class RobustCompanyCase:
    key: str
    financials: StandardizedFinancials
    assumptions: dict
    expected_families: int
    expected_cells: int
    expect_normalization: bool
    expect_per_share: bool
    expect_asset_scaled_quality: bool


def _series(*values: float) -> dict[date, float]:
    if len(values) != len(PERIODS):
        raise ValueError(f"expected {len(PERIODS)} values, got {len(values)}")
    return {period: float(value) for period, value in zip(PERIODS, values)}


def _li(label: str, *values: float, concept: str = "") -> LineItem:
    return LineItem(label=label, values=_series(*values), concept=concept)


def _periods() -> list[FinancialPeriod]:
    return [
        FinancialPeriod(end_date=period, label=f"FY{period.year}")
        for period in PERIODS
    ]


def asset_light_services_case() -> RobustCompanyCase:
    """Asset-light services: WC present, no Total Assets, no shares, no normalization."""
    financials = StandardizedFinancials(
        ticker="ALS",
        company_name="Asset Light Services Synthetic",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[
            _li("Revenue", 1000, 1200, 1400, 1600, 1800),
            _li("Finance costs", -5, -6, -7, -8, -9),
            _li("Finance income", 10, 12, 14, 16, 18),
            _li("Profit before tax", 120, 144, 168, 192, 216),
            _li("Income tax expense", -20, -24, -28, -32, -36),
            _li("Profit for the year", 100, 120, 140, 160, 180),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 300, 330, 360, 390, 420),
            _li("Trade receivables", 100, 120, 140, 160, 180),
            _li("Property, plant and equipment", 50, 55, 60, 65, 70),
            _li("Trade payables", 80, 96, 112, 128, 144),
            _li("Bank borrowings", 30, 25, 20, 15, 10),
            _li("Total equity", 340, 384, 428, 472, 516),
        ],
        cash_flow=[
            _li(
                "Net cash from operating activities",
                110,
                130,
                155,
                175,
                200,
            )
        ],
    )
    return RobustCompanyCase(
        key="asset_light_services",
        financials=financials,
        assumptions={},
        expected_families=59,
        expected_cells=248,
        expect_normalization=False,
        expect_per_share=False,
        expect_asset_scaled_quality=False,
    )


def inventory_retail_case() -> RobustCompanyCase:
    """Inventory-heavy retail: STI judgment, normalization, diluted shares."""
    financials = StandardizedFinancials(
        ticker="IRT",
        company_name="Inventory Retail Synthetic",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[
            _li("Revenue", 2000, 2300, 2600, 2400, 2800),
            _li("Finance costs", -20, -22, -25, -27, -30),
            _li("Finance income", 2, 2, 3, 3, 4),
            _li(
                "Restructuring expense",
                0,
                0,
                -30,
                0,
                0,
                concept="restructuring_expense",
            ),
            _li("Profit before tax", 180, 210, 240, 160, 250),
            _li("Income tax expense", -30, -35, -40, -26, -41),
            _li("Profit for the year", 150, 175, 200, 134, 209),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 100, 110, 120, 115, 130),
            _li("Trade receivables", 80, 92, 105, 98, 112),
            _li("Inventories", 400, 460, 520, 500, 580),
            _li("Property, plant and equipment", 300, 320, 340, 360, 380),
            _li("Short-term investments", 60, 65, 70, 75, 80),
            _li("Total assets", 940, 1047, 1155, 1148, 1282),
            _li("Trade payables", 250, 285, 320, 310, 350),
            _li("Accrued expenses", 100, 115, 130, 125, 140),
            _li("Bank borrowings", 200, 220, 240, 250, 260),
            _li("Total liabilities", 550, 620, 690, 685, 750),
            _li("Total equity", 390, 427, 465, 463, 532),
        ],
        cash_flow=[
            _li(
                "Net cash from operating activities",
                140,
                180,
                220,
                100,
                260,
            )
        ],
        historical_shares=HistoricalShareData(
            scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average=_series(500, 510, 520, 535, 540),
        ),
    )
    assumptions = {
        "classificationOverrides": {},
        "normalizationCandidates": [
            {
                "selector": "concept:restructuring_expense",
                "referenceTreatment": "Non-recurring",
                "scope": "operating_pretax_effective_tax",
                "topic": "Restructuring expense recurring vs non-recurring",
                "referenceRationale": (
                    "The synthetic robustness case treats the supplied restructuring "
                    "charge as a discrete non-recurring item for training purposes."
                ),
                "consequenceNote": (
                    "Recurring treatment leaves reported earnings unchanged; "
                    "non-recurring treatment bridges to normalized earnings."
                ),
            }
        ],
    }
    return RobustCompanyCase(
        key="inventory_retail",
        financials=financials,
        assumptions=assumptions,
        expected_families=78,
        expected_cells=331,
        expect_normalization=True,
        expect_per_share=True,
        expect_asset_scaled_quality=True,
    )


def capital_intensive_manufacturer_case() -> RobustCompanyCase:
    """Capital-intensive manufacturer: lease judgment, falling shares, no normalization."""
    financials = StandardizedFinancials(
        ticker="CIM",
        company_name="Capital Intensive Manufacturer Synthetic",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[
            _li("Revenue", 3000, 3200, 3400, 3600, 3900),
            _li("Finance costs", -60, -65, -70, -72, -75),
            _li("Finance income", 5, 5, 5, 6, 6),
            _li("Profit before tax", 260, 270, 280, 300, 330),
            _li("Income tax expense", -43, -45, -46, -50, -54),
            _li("Profit for the year", 217, 225, 234, 250, 276),
        ],
        balance_sheet=[
            _li("Cash and cash equivalents", 150, 145, 140, 155, 160),
            _li("Trade receivables", 300, 320, 340, 360, 390),
            _li("Inventories", 450, 470, 490, 510, 540),
            _li("Property, plant and equipment", 1800, 1900, 2000, 2100, 2200),
            _li("Goodwill", 200, 200, 200, 200, 200),
            _li("Total assets", 2900, 3035, 3170, 3325, 3490),
            _li("Trade payables", 350, 365, 380, 395, 420),
            _li("Bank borrowings", 900, 950, 1000, 1050, 1100),
            _li(
                "Operating lease liabilities",
                200,
                210,
                220,
                230,
                240,
                concept="lease_liability",
            ),
            _li("Total liabilities", 1450, 1525, 1600, 1675, 1760),
            _li("Total equity", 1450, 1510, 1570, 1650, 1730),
        ],
        cash_flow=[
            _li(
                "Net cash from operating activities",
                300,
                320,
                340,
                360,
                390,
            )
        ],
        historical_shares=HistoricalShareData(
            scale_basis=SUPPORTED_SHARE_SCALE_BASIS,
            diluted_weighted_average=_series(800, 800, 795, 790, 785),
        ),
    )
    return RobustCompanyCase(
        key="capital_intensive_manufacturer",
        financials=financials,
        assumptions={},
        expected_families=74,
        expected_cells=311,
        expect_normalization=False,
        expect_per_share=True,
        expect_asset_scaled_quality=True,
    )


ALL_ROBUST_CASES = (
    asset_light_services_case,
    inventory_retail_case,
    capital_intensive_manufacturer_case,
)
