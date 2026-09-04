"""Semantic trainer component definitions — no workbook coordinates.

Coordinates are resolved at build time by the reference workbook builder and
stored in the semantic component map (single source of truth).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComponentSpec:
    """Static definition of one learnable exercise."""

    id: str
    order: int
    title: str
    short_hint: str
    semantic_key: str
    category: str
    hints: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    tolerance: float = 0.01
    tab_template: str = ""  # e.g. "Condensed Financials", "Model_{scenario}"
    scenario: str = ""  # Bear | Base | Bull when tab_template uses Model_{scenario}


# Natural BAV dependency order — coordinates assigned at build time only.
COMPONENT_CATALOG: tuple[ComponentSpec, ...] = (
    ComponentSpec(
        id="effective_tax_rate_fy",
        order=1,
        title="Effective tax rate (latest fiscal year)",
        short_hint="Relate tax expense to pretax income using the model's sign convention.",
        semantic_key="condensed.effective_tax_rate.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Effective tax rate uses pretax income in the denominator.",
            "Preserve the model's sign convention for tax expense.",
        ),
    ),
    ComponentSpec(
        id="net_interest_fy",
        order=2,
        title="Net interest (latest fiscal year)",
        short_hint="Combine interest expense and interest income into the financing result.",
        semantic_key="condensed.net_interest.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Net interest consolidates interest expense and interest income.",
            "Missing optional interest lines are treated as zero.",
        ),
    ),
    ComponentSpec(
        id="net_interest_after_tax_fy",
        order=3,
        title="Net interest after tax",
        short_hint="Apply the effective tax rate once to net interest.",
        semantic_key="condensed.net_interest_after_tax.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("effective_tax_rate_fy", "net_interest_fy"),
        hints=(
            "After-tax net interest = Net Interest × (1 − Effective Tax Rate).",
            "Do not tax-adjust a rate that is already after tax.",
        ),
    ),
    ComponentSpec(
        id="nopat_fy",
        order=4,
        title="NOPAT (latest fiscal year)",
        short_hint="Reformulate net income to operating profit after tax.",
        semantic_key="condensed.nopat.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("net_interest_after_tax_fy",),
        hints=(
            "Start from Net Income on the Income Statement.",
            "Add back after-tax net interest: Net Interest × (1 − Tax Rate).",
            "NOPAT = Net Income + Net Interest After Tax.",
        ),
    ),
    ComponentSpec(
        id="owca_agg",
        order=5,
        title="Operating working capital assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.owca.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Working Capital Asset.",
        ),
    ),
    ComponentSpec(
        id="owcl_agg",
        order=6,
        title="Operating working capital liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.owcl.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Working Capital Liability.",
        ),
    ),
    ComponentSpec(
        id="nowc_agg",
        order=7,
        title="Net Operating Working Capital (NOWC)",
        short_hint="Sum operating WC assets minus operating WC liabilities.",
        semantic_key="condensed.nowc.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("owca_agg", "owcl_agg"),
        hints=(
            "Use SUMIF over the classification column for 'Operating Working Capital Asset'.",
            "Subtract SUMIF for 'Operating Working Capital Liability'.",
            "NOWC = Op. WC Assets − Op. WC Liabilities.",
        ),
    ),
    ComponentSpec(
        id="olta_agg",
        order=8,
        title="Operating long-term assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.olta.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Long-Term Asset.",
        ),
    ),
    ComponentSpec(
        id="oltl_agg",
        order=9,
        title="Operating long-term liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.oltl.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Long-Term Liability.",
        ),
    ),
    ComponentSpec(
        id="nola_agg",
        order=10,
        title="Net operating long-term assets (NOLA)",
        short_hint="Operating long-term assets less operating long-term liabilities.",
        semantic_key="condensed.nola.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("olta_agg", "oltl_agg"),
        hints=(
            "NOLA = Operating LT Assets − Operating LT Liabilities.",
        ),
    ),
    ComponentSpec(
        id="noa_agg",
        order=11,
        title="Net Operating Assets (NOA)",
        short_hint="NOWC plus net operating long-term assets.",
        semantic_key="condensed.noa.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("nowc_agg", "nola_agg"),
        hints=(
            "Net Operating LT Assets = Op. LT Assets − Op. LT Liabilities (SUMIF).",
            "NOA = NOWC + Net Operating LT Assets.",
        ),
    ),
    ComponentSpec(
        id="financial_assets_agg",
        order=12,
        title="Financial assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.financial_assets.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Financial Asset.",
        ),
    ),
    ComponentSpec(
        id="financial_liabilities_agg",
        order=13,
        title="Financial liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.financial_liabilities.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Financial Liability.",
        ),
    ),
    ComponentSpec(
        id="net_debt",
        order=14,
        title="Net Debt",
        short_hint="Financial liabilities minus financial assets.",
        semantic_key="condensed.net_debt.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("financial_assets_agg", "financial_liabilities_agg"),
        hints=(
            "Net Debt = SUMIF(Financial Liability) − SUMIF(Financial Asset).",
            "Positive net debt means the firm carries net financial obligations.",
        ),
    ),
    ComponentSpec(
        id="equity_reformulated_fy",
        order=15,
        title="Reformulated equity",
        short_hint="Use the operating/financing identity linking NOA, Net Debt, and Equity.",
        semantic_key="condensed.equity.latest_fy",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on=("noa_agg", "net_debt"),
        hints=(
            "Reformulated Equity = NOA − Net Debt.",
            "This identity must reconcile to reported equity within tolerance.",
        ),
    ),
    ComponentSpec(
        id="rnoa",
        order=16,
        title="Return on Net Operating Assets (RNOA)",
        short_hint="NOPAT divided by average NOA.",
        semantic_key="dupont.rnoa.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("nopat_fy", "noa_agg"),
        hints=(
            "RNOA = NOPAT / Average NOA.",
            "Average NOA = (Beginning NOA + Ending NOA) / 2.",
        ),
    ),
    ComponentSpec(
        id="after_tax_cod",
        order=17,
        title="After-tax cost of debt",
        short_hint="Relate net interest after tax to average net debt.",
        semantic_key="dupont.after_tax_cod.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("net_interest_after_tax_fy", "net_debt"),
        hints=(
            "After-tax CoD = Net Interest After Tax / Average Net Debt.",
            "Do not apply the tax rate a second time.",
        ),
    ),
    ComponentSpec(
        id="spread",
        order=18,
        title="Operating Spread (RNOA − After-tax CoD)",
        short_hint="Operating return minus after-tax cost of debt.",
        semantic_key="dupont.spread.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("rnoa", "after_tax_cod"),
        hints=(
            "After-tax CoD = Net Interest After Tax / Average Net Debt.",
            "Spread = RNOA − After-tax CoD.",
        ),
    ),
    ComponentSpec(
        id="flev",
        order=19,
        title="Financial leverage (FLEV)",
        short_hint="Relate average net debt to average reformulated equity.",
        semantic_key="dupont.flev.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("net_debt", "equity_reformulated_fy"),
        hints=(
            "FLEV = Average Net Debt / Average Equity.",
        ),
    ),
    ComponentSpec(
        id="roe_decomp",
        order=20,
        title="ROE decomposition",
        short_hint="ROE = RNOA + FLEV × Spread.",
        semantic_key="dupont.roe_decomposed.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("rnoa", "spread", "flev"),
        hints=(
            "Financial leverage (FLEV) = Average Net Debt / Average Equity.",
            "ROE (decomposed) = RNOA + FLEV × (RNOA − After-tax CoD).",
        ),
    ),
    ComponentSpec(
        id="actual_roe",
        order=21,
        title="Actual ROE",
        short_hint="Relate net income to average reformulated equity.",
        semantic_key="dupont.actual_roe.latest_comparable",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on=("equity_reformulated_fy",),
        hints=(
            "Actual ROE = Net Income / Average Equity.",
        ),
    ),
)


# Dormant forecast/valuation specs — not part of public COMPONENT_CATALOG / list / Check.
DEFERRED_COMPONENT_SPECS: tuple[ComponentSpec, ...] = (
    ComponentSpec(
        id="model_sales_y1",
        order=22,
        title="Base case Y1 revenue forecast",
        short_hint="Anchor revenue × (1 + Y1 growth).",
        semantic_key="model.sales.y1",
        category="forecasting",
        tab_template="Model_{scenario}",
        scenario="Base",
        depends_on=("nopat_fy",),
        hints=(
            "Y1 beginning sales = prior fiscal year revenue from Income Statement.",
            "Y1 Sales = Anchor Revenue × (1 + growthVector[0]).",
        ),
    ),
    ComponentSpec(
        id="model_nopat_y1",
        order=23,
        title="Base case Y1 NOPAT",
        short_hint="Forecast sales × NOPAT margin.",
        semantic_key="model.nopat.y1",
        category="forecasting",
        tab_template="Model_{scenario}",
        scenario="Base",
        depends_on=("model_sales_y1",),
        hints=(
            "NOPAT = Sales × marginVector[t].",
            "Margin vector is a blue forecast input.",
        ),
    ),
    ComponentSpec(
        id="model_ae_y1",
        order=24,
        title="Year 1 abnormal earnings",
        short_hint="Residual income: NI − Ke × Equity.",
        semantic_key="model.abnormal_earnings.y1",
        category="valuation",
        tab_template="Model_{scenario}",
        scenario="Base",
        depends_on=("model_nopat_y1",),
        hints=(
            "Net Income = NOPAT − Net Debt × after-tax cost of debt.",
            "Abnormal Earnings = Net Income − Cost of Equity × Book Equity.",
        ),
    ),
    ComponentSpec(
        id="model_tv",
        order=25,
        title="Terminal value (PV of abnormal earnings)",
        short_hint="Gordon growth on terminal-year abnormal earnings, discounted.",
        semantic_key="model.terminal_value.pv",
        category="valuation",
        tab_template="Model_{scenario}",
        scenario="Base",
        depends_on=("model_ae_y1",),
        hints=(
            "TV = AE₁₀ × (1 + g) / (Ke − g).",
            "Discount TV back 10 years at Ke.",
        ),
    ),
    ComponentSpec(
        id="model_ivps",
        order=26,
        title="Intrinsic value per share",
        short_hint="Book equity + PV(abnormal earnings) + PV(terminal value).",
        semantic_key="model.ivps",
        category="valuation",
        tab_template="Model_{scenario}",
        scenario="Base",
        depends_on=("model_tv",),
        hints=(
            "IV = Beginning Book Equity + Σ PV(AE) + PV(TV).",
            "IVPS = IV / Diluted Shares Outstanding.",
        ),
    ),
    ComponentSpec(
        id="scenario_weighted",
        order=27,
        title="Probability-weighted IVPS",
        short_hint="SUMPRODUCT of scenario IVPS and probabilities.",
        semantic_key="scenario.weighted_ivps",
        category="valuation",
        tab_template="Scenario_Summary",
        depends_on=("model_ivps",),
        hints=(
            "Weighted IVPS = Σ(probability × IVPS) across Bear, Base, Bull.",
            "Probabilities are blue input cells and must sum to 100%.",
        ),
    ),
)


def catalog_by_id() -> dict[str, ComponentSpec]:
    return {c.id: c for c in COMPONENT_CATALOG}


def catalog_ids() -> list[str]:
    return [c.id for c in COMPONENT_CATALOG]
