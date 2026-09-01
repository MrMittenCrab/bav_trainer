"""Trainer component registry — natural BAV model dependency order."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrainerComponent:
    """One learnable formula cell or small group."""

    id: str
    order: int
    tab: str
    cell: str
    title: str
    short_hint: str
    hints: list[str] = field(default_factory=list)
    related_cells: list[str] = field(default_factory=list)
    tolerance: float = 0.01
    validate_mode: str = "value"  # value | ratio | text
    category: str = "accounting"


TRAINER_COMPONENTS: list[TrainerComponent] = [
    TrainerComponent(
        id="nopat_fy",
        order=1,
        tab="Condensed Financials",
        cell="B6",
        title="NOPAT (first forecast year)",
        short_hint="Reformulate net income to operating profit after tax.",
        hints=[
            "Start from Net Income on the Income Statement.",
            "Add back after-tax net interest expense: Net Interest × (1 − Tax Rate).",
            "NOPAT = Net Income + Net Interest After Tax.",
            "Net Interest After Tax = (Interest Expense − Interest Income) × (1 − ETR).",
        ],
        related_cells=["'Income Statement'!B13", "'Condensed Financials'!B10"],
        category="accounting",
    ),
    TrainerComponent(
        id="nowc_agg",
        order=2,
        tab="Condensed Financials",
        cell="B20",
        title="Net Operating Working Capital (NOWC)",
        short_hint="Sum operating WC assets minus operating WC liabilities.",
        hints=[
            "Use SUMIF over the classification column for 'Operating Working Capital Asset'.",
            "Subtract SUMIF for 'Operating Working Capital Liability'.",
            "NOWC = Op. WC Assets − Op. WC Liabilities.",
        ],
        related_cells=["Condensed Financials!G7:G30"],
        category="accounting",
    ),
    TrainerComponent(
        id="noa_agg",
        order=3,
        tab="Condensed Financials",
        cell="B24",
        title="Net Operating Assets (NOA)",
        short_hint="NOWC plus net operating long-term assets.",
        hints=[
            "Net Operating LT Assets = Op. LT Assets − Op. LT Liabilities (SUMIF).",
            "NOA = NOWC + Net Operating LT Assets.",
        ],
        category="accounting",
    ),
    TrainerComponent(
        id="net_debt",
        order=4,
        tab="Condensed Financials",
        cell="B28",
        title="Net Debt",
        short_hint="Financial liabilities minus financial assets.",
        hints=[
            "Net Debt = SUMIF(Financial Liability) − SUMIF(Financial Asset).",
            "Positive net debt means the firm carries net financial obligations.",
        ],
        category="accounting",
    ),
    TrainerComponent(
        id="rnoa",
        order=5,
        tab="ALT DuPont",
        cell="C8",
        title="Return on Net Operating Assets (RNOA)",
        short_hint="NOPAT divided by average NOA.",
        hints=[
            "RNOA = NOPAT / Average NOA.",
            "Average NOA = (Beginning NOA + Ending NOA) / 2.",
            "Use Condensed Financials for NOA and NOPAT.",
        ],
        related_cells=["Condensed Financials!B6", "Condensed Financials!B24"],
        category="dupont",
    ),
    TrainerComponent(
        id="spread",
        order=6,
        tab="ALT DuPont",
        cell="C12",
        title="Operating Spread (RNOA − After-tax CoD)",
        short_hint="Operating return minus after-tax cost of debt.",
        hints=[
            "After-tax CoD = Net Interest After Tax / Average Net Debt.",
            "Spread = RNOA − After-tax CoD.",
        ],
        category="dupont",
    ),
    TrainerComponent(
        id="roe_decomp",
        order=7,
        tab="ALT DuPont",
        cell="C16",
        title="ROE decomposition",
        short_hint="ROE = RNOA + FLEV × Spread.",
        hints=[
            "Financial leverage (FLEV) = Average Net Debt / Average Equity.",
            "ROE (decomposed) = RNOA + FLEV × (RNOA − After-tax CoD).",
            "Compare to Actual ROE = Net Income / Average Equity.",
        ],
        category="dupont",
    ),
    TrainerComponent(
        id="model_sales_y1",
        order=8,
        tab="Model_Base",
        cell="C11",
        title="Base case Y1 revenue forecast",
        short_hint="Anchor revenue × (1 + Y1 growth).",
        hints=[
            "Y1 beginning sales = prior fiscal year revenue from Income Statement.",
            "Y1 Sales = Anchor Revenue × (1 + growthVector[0]).",
            "Growth vector is a blue input cell in the assumption block.",
        ],
        category="forecasting",
    ),
    TrainerComponent(
        id="model_nopat_y1",
        order=9,
        tab="Model_Base",
        cell="C14",
        title="Base case Y1 NOPAT",
        short_hint="Forecast sales × NOPAT margin.",
        hints=[
            "NOPAT = Sales × marginVector[t].",
            "Margin vector is a blue forecast input.",
        ],
        category="forecasting",
    ),
    TrainerComponent(
        id="model_ae_y1",
        order=10,
        tab="Model_Base",
        cell="C20",
        title="Year 1 abnormal earnings",
        short_hint="Residual income: NI − Ke × Equity.",
        hints=[
            "Net Income = NOPAT − Net Debt × after-tax cost of debt.",
            "Abnormal Earnings = Net Income − Cost of Equity × Book Equity.",
            "Y1 equity comes from the anchor balance sheet.",
        ],
        category="valuation",
    ),
    TrainerComponent(
        id="model_tv",
        order=11,
        tab="Model_Base",
        cell="C35",
        title="Terminal value (abnormal earnings)",
        short_hint="Gordon growth on terminal-year abnormal earnings.",
        hints=[
            "TV = AE₁₀ × (1 + g) / (Ke − g).",
            "Terminal growth g links to terminal-year revenue growth.",
            "Discount TV back 10 years at Ke.",
        ],
        category="valuation",
    ),
    TrainerComponent(
        id="model_ivps",
        order=12,
        tab="Model_Base",
        cell="C38",
        title="Intrinsic value per share",
        short_hint="Book equity + PV(abnormal earnings) + PV(terminal value).",
        hints=[
            "IV = Beginning Book Equity + Σ PV(AE) + PV(TV).",
            "IVPS = IV / Diluted Shares Outstanding.",
        ],
        category="valuation",
    ),
    TrainerComponent(
        id="scenario_weighted",
        order=13,
        tab="Scenario_Summary",
        cell="E5",
        title="Probability-weighted IVPS",
        short_hint="SUMPRODUCT of scenario IVPS and probabilities.",
        hints=[
            "Weighted IVPS = Σ(probability × IVPS) across Bear, Base, Bull.",
            "Probabilities are blue input cells and must sum to 100%.",
        ],
        category="valuation",
    ),
]
