"""Semantic trainer component definitions — no workbook coordinates.

Coordinates are resolved at build time by the reference workbook builder and
stored in the semantic component map (single source of truth).

COMPONENT_CATALOG holds conceptual schedule families. Concrete period-specific
ComponentSpec rows are produced by expand_historical_specs(periods).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ComponentFamily:
    """One conceptual historical schedule (curriculum unit)."""

    id: str
    order: int
    title: str
    short_hint: str
    semantic_key: str
    category: str
    tab_template: str
    period_scope: str = "all"  # "all" | "comparable"
    depends_on_current: tuple[str, ...] = ()
    depends_on_previous: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    tolerance: float = 0.01


@dataclass(frozen=True)
class ComponentSpec:
    """Concrete practice cell for one family × one fiscal period (or deferred)."""

    id: str
    family_id: str
    order: int
    family_order: int
    title: str
    short_hint: str
    semantic_key: str
    category: str
    tab_template: str
    period_index: int | None = None
    period_end: str = ""
    depends_on: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    tolerance: float = 0.01
    scenario: str = ""


def concrete_component_id(family_id: str, period: date) -> str:
    return f"{family_id}__{period.strftime('%Y%m%d')}"


def expand_historical_specs(periods: list[date]) -> tuple[ComponentSpec, ...]:
    """Expand conceptual families into period-specific concrete specs.

    Callers must supply an already-canonical chronological period axis.
    This helper rejects non-increasing or duplicate dates rather than sorting.
    """
    if len(periods) != len(set(periods)):
        raise ValueError("duplicate fiscal periods are not allowed in expand_historical_specs")
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_historical_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = 1
    for family in COMPONENT_CATALOG:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            indices = range(len(periods))
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


# Natural BAV dependency order — coordinates assigned at build time only.
COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="revenue_link",
        order=1,
        title="Revenue historical source link",
        short_hint="Link Revenue from the Income Statement into Condensed Financials.",
        semantic_key="condensed.revenue_link",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Pull the Revenue line from the Income Statement for the same fiscal period.",
        ),
    ),
    ComponentFamily(
        id="net_income_link",
        order=2,
        title="Net Income historical source link",
        short_hint="Link Net Income from the Income Statement into Condensed Financials.",
        semantic_key="condensed.net_income_link",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Pull Net Income from the Income Statement for the same fiscal period.",
        ),
    ),
    ComponentFamily(
        id="effective_tax_rate_fy",
        order=3,
        title="Effective tax rate",
        short_hint="Relate tax expense to pretax income using the model's sign convention.",
        semantic_key="condensed.effective_tax_rate",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Effective tax rate uses pretax income in the denominator.",
            "Preserve the model's sign convention for tax expense.",
            "A zero Pretax Income makes Effective Tax Rate undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="net_interest_fy",
        order=4,
        title="Net interest",
        short_hint="Combine interest expense and interest income into the financing result.",
        semantic_key="condensed.net_interest",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Net interest consolidates interest expense and interest income.",
            "Use the explicitly supplied Interest Expense and Interest Income lines with the model's sign convention.",
        ),
    ),
    ComponentFamily(
        id="net_interest_after_tax_fy",
        order=5,
        title="Net interest after tax",
        short_hint="Apply the effective tax rate once to net interest.",
        semantic_key="condensed.net_interest_after_tax",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("effective_tax_rate_fy", "net_interest_fy"),
        hints=(
            "After-tax net interest = Net Interest × (1 − Effective Tax Rate).",
            "Do not tax-adjust a rate that is already after tax.",
            "A zero Net Interest amount remains zero even if ETR is undefined; otherwise undefined ETR propagates.",
        ),
    ),
    ComponentFamily(
        id="nopat_fy",
        order=6,
        title="NOPAT",
        short_hint="Reformulate net income to operating profit after tax.",
        semantic_key="condensed.nopat",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("net_income_link", "net_interest_after_tax_fy"),
        hints=(
            "Start from Net Income on the Income Statement.",
            "Add back after-tax net interest: Net Interest × (1 − Tax Rate).",
            "NOPAT = Net Income + Net Interest After Tax.",
            "Undefined tax-effected Net Interest propagates to NOPAT.",
        ),
    ),
    ComponentFamily(
        id="owca_agg",
        order=7,
        title="Operating working capital assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.owca",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Working Capital Asset.",
        ),
    ),
    ComponentFamily(
        id="owcl_agg",
        order=8,
        title="Operating working capital liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.owcl",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Working Capital Liability.",
        ),
    ),
    ComponentFamily(
        id="nowc_agg",
        order=9,
        title="Net Operating Working Capital (NOWC)",
        short_hint="Sum operating WC assets minus operating WC liabilities.",
        semantic_key="condensed.nowc",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("owca_agg", "owcl_agg"),
        hints=(
            "Use SUMIF over the classification column for 'Operating Working Capital Asset'.",
            "Subtract SUMIF for 'Operating Working Capital Liability'.",
            "NOWC = Op. WC Assets − Op. WC Liabilities.",
        ),
    ),
    ComponentFamily(
        id="olta_agg",
        order=10,
        title="Operating long-term assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.olta",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Long-Term Asset.",
        ),
    ),
    ComponentFamily(
        id="oltl_agg",
        order=11,
        title="Operating long-term liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.oltl",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Operating Long-Term Liability.",
        ),
    ),
    ComponentFamily(
        id="nola_agg",
        order=12,
        title="Net operating long-term assets (NOLA)",
        short_hint="Operating long-term assets less operating long-term liabilities.",
        semantic_key="condensed.nola",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("olta_agg", "oltl_agg"),
        hints=(
            "NOLA = Operating LT Assets − Operating LT Liabilities.",
        ),
    ),
    ComponentFamily(
        id="noa_agg",
        order=13,
        title="Net Operating Assets (NOA)",
        short_hint="NOWC plus net operating long-term assets.",
        semantic_key="condensed.noa",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("nowc_agg", "nola_agg"),
        hints=(
            "Net Operating LT Assets = Op. LT Assets − Op. LT Liabilities (SUMIF).",
            "NOA = NOWC + Net Operating LT Assets.",
        ),
    ),
    ComponentFamily(
        id="financial_assets_agg",
        order=14,
        title="Financial assets",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.financial_assets",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Financial Asset.",
        ),
    ),
    ComponentFamily(
        id="financial_liabilities_agg",
        order=15,
        title="Financial liabilities",
        short_hint="Aggregate the classified balance-sheet detail with the classification column.",
        semantic_key="condensed.financial_liabilities",
        category="accounting",
        tab_template="Condensed Financials",
        hints=(
            "Use SUMIF over the classification column for Financial Liability.",
        ),
    ),
    ComponentFamily(
        id="net_debt",
        order=16,
        title="Net Debt",
        short_hint="Financial liabilities minus financial assets.",
        semantic_key="condensed.net_debt",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("financial_assets_agg", "financial_liabilities_agg"),
        hints=(
            "Net Debt = SUMIF(Financial Liability) − SUMIF(Financial Asset).",
            "Positive net debt means the firm carries net financial obligations.",
        ),
    ),
    ComponentFamily(
        id="equity_reformulated_fy",
        order=17,
        title="Reformulated equity",
        short_hint="Use the operating/financing identity linking NOA, Net Debt, and Equity.",
        semantic_key="condensed.equity",
        category="accounting",
        tab_template="Condensed Financials",
        depends_on_current=("noa_agg", "net_debt"),
        hints=(
            "Reformulated Equity = NOA − Net Debt.",
            "This identity must reconcile to reported equity within tolerance.",
        ),
    ),
    ComponentFamily(
        id="sales_growth",
        order=18,
        title="Sales Growth",
        short_hint="Current Revenue relative to the immediately preceding fiscal year.",
        semantic_key="dupont.sales_growth",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("revenue_link",),
        depends_on_previous=("revenue_link",),
        hints=(
            "Sales Growth = Current Revenue / Prior Revenue − 1.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
    ComponentFamily(
        id="nopat_margin",
        order=19,
        title="NOPAT Margin",
        short_hint="NOPAT divided by Revenue for the same fiscal period.",
        semantic_key="dupont.nopat_margin",
        category="dupont",
        tab_template="ALT DuPont",
        depends_on_current=("nopat_fy", "revenue_link"),
        hints=(
            "NOPAT Margin = NOPAT / Revenue.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
    ComponentFamily(
        id="rnoa",
        order=20,
        title="Return on Net Operating Assets (RNOA)",
        short_hint="NOPAT divided by average NOA.",
        semantic_key="dupont.rnoa",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("nopat_fy", "noa_agg"),
        depends_on_previous=("noa_agg",),
        hints=(
            "RNOA = NOPAT / Average NOA.",
            "Average NOA = (Beginning NOA + Ending NOA) / 2.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
    ComponentFamily(
        id="after_tax_cod",
        order=21,
        title="After-tax cost of debt",
        short_hint="Relate net interest after tax to average net debt.",
        semantic_key="dupont.after_tax_cod",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("net_interest_after_tax_fy", "net_debt"),
        depends_on_previous=("net_debt",),
        hints=(
            "After-tax CoD = Net Interest After Tax / Average Net Debt.",
            "Do not apply the tax rate a second time.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
    ComponentFamily(
        id="spread",
        order=22,
        title="Operating Spread (RNOA − After-tax CoD)",
        short_hint="Operating return minus after-tax cost of debt.",
        semantic_key="dupont.spread",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("rnoa", "after_tax_cod"),
        hints=(
            "After-tax CoD = Net Interest After Tax / Average Net Debt.",
            "Spread = RNOA − After-tax CoD.",
            "An undefined required upstream ratio propagates into Spread.",
        ),
    ),
    ComponentFamily(
        id="flev",
        order=23,
        title="Financial leverage (FLEV)",
        short_hint="Relate average net debt to average reformulated equity.",
        semantic_key="dupont.flev",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("net_debt", "equity_reformulated_fy"),
        depends_on_previous=("net_debt", "equity_reformulated_fy"),
        hints=(
            "FLEV = Average Net Debt / Average Equity.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
    ComponentFamily(
        id="roe_decomp",
        order=24,
        title="ROE decomposition",
        short_hint="ROE = RNOA + FLEV × Spread.",
        semantic_key="dupont.roe_decomposed",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("rnoa", "spread", "flev"),
        hints=(
            "Financial leverage (FLEV) = Average Net Debt / Average Equity.",
            "ROE (decomposed) = RNOA + FLEV × (RNOA − After-tax CoD).",
            "An undefined required upstream ratio propagates into decomposed ROE.",
        ),
    ),
    ComponentFamily(
        id="actual_roe",
        order=25,
        title="Actual ROE",
        short_hint="Relate net income to average reformulated equity.",
        semantic_key="dupont.actual_roe",
        category="dupont",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("net_income_link", "equity_reformulated_fy"),
        depends_on_previous=("equity_reformulated_fy",),
        hints=(
            "Actual ROE = Net Income / Average Equity.",
            "A zero denominator makes this ratio undefined (#N/A), not 0%.",
        ),
    ),
)


NORMALIZATION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="pretax_normalization_adjustment",
        order=26,
        title="Pretax normalization adjustment",
        short_hint=(
            "Sum the signed pretax add-back for items marked Non-recurring on the "
            "Earnings Normalization detail block."
        ),
        semantic_key="normalization.pretax_adjustment",
        category="normalization",
        tab_template="Earnings Normalization",
        hints=(
            "Use SUMIF on the detail treatment column for Non-recurring items, "
            "then negate the sum so expense add-backs are positive.",
        ),
    ),
    ComponentFamily(
        id="after_tax_normalization_adjustment",
        order=27,
        title="After-tax normalization adjustment",
        short_hint="Apply the period effective tax rate to the pretax normalization adjustment.",
        semantic_key="normalization.after_tax_adjustment",
        category="normalization",
        tab_template="Earnings Normalization",
        depends_on_current=("pretax_normalization_adjustment",),
        hints=(
            "After-tax adjustment = pretax adjustment × (1 − effective tax rate).",
        ),
    ),
    ComponentFamily(
        id="normalized_nopat",
        order=28,
        title="Normalized NOPAT",
        short_hint="Add the after-tax normalization adjustment to reported NOPAT.",
        semantic_key="normalization.normalized_nopat",
        category="normalization",
        tab_template="Earnings Normalization",
        depends_on_current=("after_tax_normalization_adjustment",),
        hints=(
            "Normalized NOPAT = Reported NOPAT + after-tax normalization adjustment.",
        ),
    ),
    ComponentFamily(
        id="normalized_net_income",
        order=29,
        title="Normalized Net Income",
        short_hint="Add the after-tax normalization adjustment to reported Net Income.",
        semantic_key="normalization.normalized_net_income",
        category="normalization",
        tab_template="Earnings Normalization",
        depends_on_current=("after_tax_normalization_adjustment",),
        hints=(
            "Normalized Net Income = Reported Net Income + after-tax normalization adjustment.",
        ),
    ),
)


def expand_normalization_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand normalization families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError("duplicate fiscal periods are not allowed in expand_normalization_specs")
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_normalization_specs requires strictly chronological "
                "(increasing) period dates"
            )
    specs: list[ComponentSpec] = []
    order = start_order
    for family in NORMALIZATION_COMPONENT_CATALOG:
        for j, period in enumerate(periods):
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


QUALITY_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="operating_cash_flow_link",
        order=30,
        title="Operating cash flow historical source link",
        short_hint="Link net cash from operating activities for the same fiscal period.",
        semantic_key="quality.operating_cash_flow",
        category="earnings_quality",
        tab_template="Earnings Quality",
        hints=(
            "Pull final net cash from operating activities for the same period.",
        ),
    ),
    ComponentFamily(
        id="cash_conversion_ratio",
        order=31,
        title="Cash conversion ratio",
        short_hint="Compare operating cash flow with reported Net Income.",
        semantic_key="quality.cash_conversion_ratio",
        category="earnings_quality",
        tab_template="Earnings Quality",
        depends_on_current=("operating_cash_flow_link", "net_income_link"),
        hints=(
            "Cash conversion = CFO / Reported Net Income.",
        ),
    ),
    ComponentFamily(
        id="total_accruals",
        order=32,
        title="Total accruals",
        short_hint="Reported Net Income minus operating cash flow.",
        semantic_key="quality.total_accruals",
        category="earnings_quality",
        tab_template="Earnings Quality",
        depends_on_current=("operating_cash_flow_link", "net_income_link"),
        hints=(
            "Total accruals = Reported Net Income − CFO.",
        ),
    ),
    ComponentFamily(
        id="average_total_assets",
        order=33,
        title="Average total assets",
        short_hint="Average beginning and ending reported total assets.",
        semantic_key="quality.average_total_assets",
        category="earnings_quality",
        tab_template="Earnings Quality",
        period_scope="comparable",
        hints=(
            "Average Total Assets = (Beginning Total Assets + Ending Total Assets) / 2.",
        ),
    ),
    ComponentFamily(
        id="accrual_ratio",
        order=34,
        title="Accrual ratio",
        short_hint="Scale total accruals by average total assets.",
        semantic_key="quality.accrual_ratio",
        category="earnings_quality",
        tab_template="Earnings Quality",
        period_scope="comparable",
        depends_on_current=("total_accruals", "average_total_assets"),
        hints=(
            "Accrual ratio = Total Accruals / Average Total Assets.",
        ),
    ),
)


def expand_quality_specs(
    periods: list[date],
    *,
    start_order: int,
    include_asset_scaled: bool,
) -> tuple[ComponentSpec, ...]:
    """Expand earnings-quality families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError("duplicate fiscal periods are not allowed in expand_quality_specs")
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_quality_specs requires strictly chronological "
                "(increasing) period dates"
            )

    families = QUALITY_COMPONENT_CATALOG
    if not include_asset_scaled:
        families = tuple(
            family
            for family in QUALITY_COMPONENT_CATALOG
            if family.id
            not in {
                "average_total_assets",
                "accrual_ratio",
            }
        )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in families:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            indices = range(len(periods))
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


WORKING_CAPITAL_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="owca_to_revenue",
        order=35,
        title="Operating working capital assets / Revenue",
        short_hint="OWCA divided by Revenue for the same fiscal period.",
        semantic_key="working_capital.owca_to_revenue",
        category="working_capital",
        tab_template="Working Capital Analysis",
        hints=(
            "Operating Working Capital Assets / Revenue measures operating current assets tied up per sales dollar.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "A higher ratio is not automatically deterioration; diagnose the underlying operating balances before drawing a conclusion.",
        ),
    ),
    ComponentFamily(
        id="owcl_to_revenue",
        order=36,
        title="Operating working capital liabilities / Revenue",
        short_hint="OWCL divided by Revenue for the same fiscal period.",
        semantic_key="working_capital.owcl_to_revenue",
        category="working_capital",
        tab_template="Working Capital Analysis",
        hints=(
            "Operating Working Capital Liabilities / Revenue measures operating current liabilities financing each sales dollar.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "A higher ratio can finance growth but is not automatically positive; payment behavior and business model matter.",
        ),
    ),
    ComponentFamily(
        id="nowc_to_revenue",
        order=37,
        title="NOWC / Revenue",
        short_hint="NOWC divided by Revenue for the same fiscal period.",
        semantic_key="working_capital.nowc_to_revenue",
        category="working_capital",
        tab_template="Working Capital Analysis",
        hints=(
            "NOWC / Revenue measures net operating working capital tied up per sales dollar.",
            "NOWC = OWCA - OWCL.",
            "Rising intensity means more net working capital is tied up per sales dollar, but the cause must be diagnosed rather than labeled automatically.",
        ),
    ),
    ComponentFamily(
        id="revenue_change",
        order=38,
        title="Change in Revenue",
        short_hint="Absolute year-on-year change in Revenue.",
        semantic_key="working_capital.revenue_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        hints=(
            "Use the absolute year-on-year change in Revenue, not the percentage growth rate.",
        ),
    ),
    ComponentFamily(
        id="nowc_change",
        order=39,
        title="Change in NOWC",
        short_hint="Absolute year-on-year change in NOWC.",
        semantic_key="working_capital.nowc_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        hints=(
            "Positive Change in NOWC means additional operating working capital is tied up; negative Change in NOWC means a release.",
            "Do not call the movement good or bad without examining why it occurred.",
        ),
    ),
    ComponentFamily(
        id="incremental_nowc_to_revenue_change",
        order=40,
        title="Incremental NOWC / Change in Revenue",
        short_hint="Change in NOWC divided by Change in Revenue.",
        semantic_key="working_capital.incremental_nowc_to_revenue_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("nowc_change", "revenue_change"),
        hints=(
            "This ratio measures incremental working-capital investment per unit of incremental sales.",
            "A zero Change in Revenue denominator makes the ratio undefined (#N/A).",
            "Negative or unusually large values are diagnostic signals, not automatic quality labels.",
        ),
    ),
    ComponentFamily(
        id="owca_change",
        order=41,
        title="Change in Operating Working Capital Assets",
        short_hint="Absolute year-on-year change in OWCA.",
        semantic_key="working_capital.owca_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("owca_agg",),
        depends_on_previous=("owca_agg",),
        hints=(
            "Change in OWCA = Current OWCA - Prior OWCA.",
            "A positive change is additional operating-current-asset investment; a negative change is a release.",
            "Do not infer the underlying receivables/inventory cause from this aggregate alone.",
        ),
    ),
    ComponentFamily(
        id="owcl_change",
        order=42,
        title="Change in Operating Working Capital Liabilities",
        short_hint="Absolute year-on-year change in OWCL.",
        semantic_key="working_capital.owcl_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("owcl_agg",),
        depends_on_previous=("owcl_agg",),
        hints=(
            "Change in OWCL = Current OWCL - Prior OWCL.",
            "A positive change supplies additional operating-liability financing; a negative change reduces that financing.",
            "Do not infer payment quality or supplier pressure from this aggregate alone.",
        ),
    ),
    ComponentFamily(
        id="nowc_change_from_components",
        order=43,
        title="Change in NOWC from OWCA / OWCL bridge",
        short_hint="Change in OWCA minus Change in OWCL.",
        semantic_key="working_capital.nowc_change_from_components",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("owca_change", "owcl_change"),
        hints=(
            "Because NOWC = OWCA - OWCL, Change in NOWC = Change in OWCA - Change in OWCL.",
            "Use this bridge to separate asset investment from operating-liability financing.",
            "The bridge must reconcile to the direct Change in NOWC row.",
        ),
    ),
    ComponentFamily(
        id="incremental_owca_to_revenue_change",
        order=44,
        title="Incremental OWCA / Change in Revenue",
        short_hint="Change in OWCA divided by Change in Revenue.",
        semantic_key="working_capital.incremental_owca_to_revenue_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("owca_change", "revenue_change"),
        hints=(
            "This ratio measures incremental operating-current-asset investment per unit of incremental sales.",
            "A zero Change in Revenue denominator makes the ratio undefined (#N/A).",
            "Keep the signed denominator when Revenue falls; do not convert it to an absolute value.",
        ),
    ),
    ComponentFamily(
        id="incremental_owcl_to_revenue_change",
        order=45,
        title="Incremental OWCL / Change in Revenue",
        short_hint="Change in OWCL divided by Change in Revenue.",
        semantic_key="working_capital.incremental_owcl_to_revenue_change",
        category="working_capital",
        tab_template="Working Capital Analysis",
        period_scope="comparable",
        depends_on_current=("owcl_change", "revenue_change"),
        hints=(
            "This ratio measures incremental operating-liability financing per unit of incremental sales.",
            "A zero Change in Revenue denominator makes the ratio undefined (#N/A).",
            "A larger value is not automatically good; it only shows that more operating liabilities accompany the sales change.",
        ),
    ),
)


def expand_working_capital_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand working-capital diagnostic families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_working_capital_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_working_capital_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in WORKING_CAPITAL_COMPONENT_CATALOG:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            indices = range(len(periods))
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


PROFITABILITY_DRIVER_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="average_noa",
        order=46,
        title="Average Net Operating Assets",
        short_hint="Average beginning and ending NOA for the comparable period.",
        semantic_key="profitability.average_noa",
        category="profitability_driver",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("noa_agg",),
        depends_on_previous=("noa_agg",),
        hints=(
            "Average NOA = (Beginning NOA + Ending NOA) / 2.",
            "Use the same Average NOA denominator as direct RNOA.",
        ),
    ),
    ComponentFamily(
        id="noa_turnover",
        order=47,
        title="Net Operating Asset Turnover",
        short_hint="Revenue divided by Average NOA.",
        semantic_key="profitability.noa_turnover",
        category="profitability_driver",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("revenue_link", "average_noa"),
        hints=(
            "NOA Turnover = Revenue / Average NOA.",
            "Higher turnover means more Revenue is generated per unit of net operating assets, but the cause requires separate analysis.",
            "A zero Average NOA denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="noa_intensity",
        order=48,
        title="Net Operating Asset Intensity",
        short_hint="Average NOA divided by Revenue.",
        semantic_key="profitability.noa_intensity",
        category="profitability_driver",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("average_noa", "revenue_link"),
        hints=(
            "NOA Intensity = Average NOA / Revenue.",
            "It expresses how much net operating asset investment supports each unit of Revenue.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="rnoa_margin_turnover",
        order=49,
        title="RNOA from Margin × Turnover",
        short_hint="NOPAT Margin multiplied by NOA Turnover.",
        semantic_key="profitability.rnoa_margin_turnover",
        category="profitability_driver",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("nopat_margin", "noa_turnover"),
        hints=(
            "RNOA = NOPAT Margin × NOA Turnover when both terms are defined.",
            "This separates operating profitability per sales dollar from operating-asset efficiency.",
            "If either required driver is undefined, the decomposition is also undefined (#N/A).",
        ),
    ),
)


def expand_profitability_driver_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand profitability-driver families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_profitability_driver_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_profitability_driver_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in PROFITABILITY_DRIVER_COMPONENT_CATALOG:
        for j in range(1, len(periods)):
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            prev = periods[j - 1]
            for dep_fam in family.depends_on_previous:
                deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


PROFITABILITY_CHANGE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="nopat_margin_change",
        order=50,
        title="Change in NOPAT Margin",
        short_hint="Current NOPAT Margin minus prior comparable NOPAT Margin.",
        semantic_key="profitability_change.nopat_margin_change",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("nopat_margin",),
        depends_on_previous=("nopat_margin",),
        hints=(
            "Change in NOPAT Margin = Current Margin - Prior Margin.",
            "This is an arithmetic movement, not a causal explanation of pricing or costs.",
        ),
    ),
    ComponentFamily(
        id="noa_turnover_change",
        order=51,
        title="Change in NOA Turnover",
        short_hint="Current NOA Turnover minus prior comparable NOA Turnover.",
        semantic_key="profitability_change.noa_turnover_change",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("noa_turnover",),
        depends_on_previous=("noa_turnover",),
        hints=(
            "Change in NOA Turnover = Current Turnover - Prior Turnover.",
            "A lower turnover is mechanically consistent with greater NOA intensity when the reciprocal is defined, but the business cause requires separate analysis.",
        ),
    ),
    ComponentFamily(
        id="rnoa_change",
        order=52,
        title="Direct Change in RNOA",
        short_hint="Current direct RNOA minus prior comparable direct RNOA.",
        semantic_key="profitability_change.rnoa_change",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("rnoa",),
        depends_on_previous=("rnoa",),
        hints=(
            "Direct Change in RNOA = Current RNOA - Prior RNOA.",
        ),
    ),
    ComponentFamily(
        id="rnoa_margin_effect",
        order=53,
        title="Margin Effect on Change in RNOA",
        short_hint="Change in Margin multiplied by midpoint NOA Turnover.",
        semantic_key="profitability_change.rnoa_margin_effect",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("nopat_margin_change", "noa_turnover"),
        depends_on_previous=("noa_turnover",),
        hints=(
            "Margin Effect = Change in Margin × average of current and prior NOA Turnover.",
            "Midpoint weighting gives an exact order-neutral product-change attribution.",
        ),
    ),
    ComponentFamily(
        id="rnoa_turnover_effect",
        order=54,
        title="Turnover Effect on Change in RNOA",
        short_hint="Change in NOA Turnover multiplied by midpoint NOPAT Margin.",
        semantic_key="profitability_change.rnoa_turnover_effect",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("noa_turnover_change", "nopat_margin"),
        depends_on_previous=("nopat_margin",),
        hints=(
            "Turnover Effect = Change in NOA Turnover × average of current and prior NOPAT Margin.",
            "Do not reinterpret this aggregate effect as a specific asset-management cause without further evidence.",
        ),
    ),
    ComponentFamily(
        id="rnoa_change_from_drivers",
        order=55,
        title="Change in RNOA from Margin + Turnover Effects",
        short_hint="Margin Effect plus Turnover Effect.",
        semantic_key="profitability_change.rnoa_change_from_drivers",
        category="profitability_change",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("rnoa_margin_effect", "rnoa_turnover_effect"),
        hints=(
            "Driver Change in RNOA = Margin Effect + Turnover Effect.",
            "When both driver periods are defined, this must reconcile to Direct Change in RNOA.",
        ),
    ),
)


def expand_profitability_change_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand RNOA-change families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_profitability_change_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_profitability_change_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in PROFITABILITY_CHANGE_COMPONENT_CATALOG:
        for j in range(2, len(periods)):
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            prev = periods[j - 1]
            for dep_fam in family.depends_on_previous:
                deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


ROE_ATTRIBUTION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="financing_contribution_to_roe",
        order=56,
        title="Financing Contribution to ROE",
        short_hint="FLEV multiplied by Spread.",
        semantic_key="roe_attribution.financing_contribution",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("flev", "spread"),
        hints=(
            "Financing Contribution to ROE = FLEV × Spread.",
            "A positive contribution raises decomposed ROE above RNOA; a negative contribution lowers it.",
            "Do not call the contribution good or bad without understanding leverage and financing economics.",
        ),
    ),
    ComponentFamily(
        id="roe_change",
        order=57,
        title="Direct Change in Decomposed ROE",
        short_hint="Current decomposed ROE minus prior decomposed ROE.",
        semantic_key="roe_attribution.roe_change",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("roe_decomp",),
        depends_on_previous=("roe_decomp",),
        hints=(
            "Direct Change in ROE = Current decomposed ROE - Prior decomposed ROE.",
        ),
    ),
    ComponentFamily(
        id="operating_effect_on_roe_change",
        order=58,
        title="Operating Effect on Change in ROE",
        short_hint="The direct Change in RNOA from the prior diagnostic section.",
        semantic_key="roe_attribution.operating_effect",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("rnoa_change",),
        hints=(
            "Operating Effect on Change in ROE = Change in RNOA.",
            "Use the existing direct RNOA-change result; do not reassign financing effects into the operating term.",
        ),
    ),
    ComponentFamily(
        id="leverage_effect_on_roe_change",
        order=59,
        title="Leverage Effect on Change in ROE",
        short_hint="Change in FLEV multiplied by midpoint Spread.",
        semantic_key="roe_attribution.leverage_effect",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("flev", "spread"),
        depends_on_previous=("flev", "spread"),
        hints=(
            "Leverage Effect = Change in FLEV × average of current and prior Spread.",
            "Midpoint weighting gives an exact order-neutral attribution of the financing product change.",
        ),
    ),
    ComponentFamily(
        id="spread_effect_on_roe_change",
        order=60,
        title="Spread Effect on Change in ROE",
        short_hint="Change in Spread multiplied by midpoint FLEV.",
        semantic_key="roe_attribution.spread_effect",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=("spread", "flev"),
        depends_on_previous=("spread", "flev"),
        hints=(
            "Spread Effect = Change in Spread × average of current and prior FLEV.",
            "Do not interpret Spread movement as a specific financing-policy cause without additional evidence.",
        ),
    ),
    ComponentFamily(
        id="financing_effect_on_roe_change",
        order=61,
        title="Financing Effect on Change in ROE",
        short_hint="Leverage Effect plus Spread Effect.",
        semantic_key="roe_attribution.financing_effect",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=(
            "leverage_effect_on_roe_change",
            "spread_effect_on_roe_change",
        ),
        hints=(
            "Financing Effect = Leverage Effect + Spread Effect.",
            "This equals the change in FLEV × Spread when all required inputs are defined.",
        ),
    ),
    ComponentFamily(
        id="roe_change_from_drivers",
        order=62,
        title="Change in ROE from Operating + Financing Drivers",
        short_hint="Operating Effect plus Financing Effect.",
        semantic_key="roe_attribution.roe_change_from_drivers",
        category="roe_attribution",
        tab_template="ALT DuPont",
        period_scope="post_comparable",
        depends_on_current=(
            "operating_effect_on_roe_change",
            "financing_effect_on_roe_change",
        ),
        hints=(
            "Change in ROE from Drivers = Operating Effect + Financing Effect.",
            "When all required terms are defined, this must reconcile to Direct Change in Decomposed ROE.",
        ),
    ),
)


def expand_roe_attribution_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand ROE-attribution families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_roe_attribution_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_roe_attribution_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in ROE_ATTRIBUTION_COMPONENT_CATALOG:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        elif family.period_scope == "post_comparable":
            indices = range(2, len(periods))
        else:
            raise ValueError(
                f"unsupported ROE-attribution period_scope {family.period_scope!r}"
            )
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            prev = periods[j - 1]
            for dep_fam in family.depends_on_previous:
                deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


QUALITY_CHANGE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="operating_cash_flow_change",
        order=63,
        title="Change in Operating Cash Flow",
        short_hint="Current CFO minus prior CFO.",
        semantic_key="quality_change.operating_cash_flow_change",
        category="earnings_quality_change",
        tab_template="Earnings Quality",
        period_scope="comparable",
        depends_on_current=("operating_cash_flow_link",),
        depends_on_previous=("operating_cash_flow_link",),
        hints=(
            "Change in CFO = Current Operating Cash Flow - Prior Operating Cash Flow.",
            "A positive or negative movement is mechanical evidence only; interpret it alongside profitability and business conditions.",
        ),
    ),
    ComponentFamily(
        id="cash_conversion_ratio_change",
        order=64,
        title="Change in Cash Conversion Ratio",
        short_hint="Current cash conversion ratio minus prior ratio.",
        semantic_key="quality_change.cash_conversion_ratio_change",
        category="earnings_quality_change",
        tab_template="Earnings Quality",
        period_scope="comparable",
        depends_on_current=("cash_conversion_ratio",),
        depends_on_previous=("cash_conversion_ratio",),
        hints=(
            "Change in Cash Conversion Ratio = Current CFO/Net Income ratio - Prior ratio.",
            "If either period's ratio is undefined, the change is also undefined (#N/A).",
            "Do not automatically label a higher ratio as better quality without investigating why it changed.",
        ),
    ),
    ComponentFamily(
        id="total_accruals_change",
        order=65,
        title="Change in Total Accruals",
        short_hint="Current Total Accruals minus prior Total Accruals.",
        semantic_key="quality_change.total_accruals_change",
        category="earnings_quality_change",
        tab_template="Earnings Quality",
        period_scope="comparable",
        depends_on_current=("total_accruals",),
        depends_on_previous=("total_accruals",),
        hints=(
            "Change in Total Accruals = Current (Net Income - CFO) - Prior (Net Income - CFO).",
            "Retain the sign; do not convert accrual movements to absolute values.",
            "The direction alone is not an automatic earnings-quality verdict.",
        ),
    ),
    ComponentFamily(
        id="accrual_ratio_change",
        order=66,
        title="Change in Accrual Ratio",
        short_hint="Current accrual ratio minus prior comparable accrual ratio.",
        semantic_key="quality_change.accrual_ratio_change",
        category="earnings_quality_change",
        tab_template="Earnings Quality",
        period_scope="post_comparable",
        depends_on_current=("accrual_ratio",),
        depends_on_previous=("accrual_ratio",),
        hints=(
            "Change in Accrual Ratio = Current Accrual Ratio - Prior Accrual Ratio.",
            "This family is available only when reported Total Assets support the existing accrual-ratio schedule.",
            "Undefined current or prior ratios propagate to #N/A.",
        ),
    ),
)


def expand_quality_change_specs(
    periods: list[date],
    *,
    start_order: int,
    include_asset_scaled: bool,
) -> tuple[ComponentSpec, ...]:
    """Expand earnings-quality change families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_quality_change_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_quality_change_specs requires strictly chronological "
                "(increasing) period dates"
            )

    families = QUALITY_CHANGE_COMPONENT_CATALOG
    if not include_asset_scaled:
        families = tuple(
            family
            for family in QUALITY_CHANGE_COMPONENT_CATALOG
            if family.id != "accrual_ratio_change"
        )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in families:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        elif family.period_scope == "post_comparable":
            indices = range(2, len(periods))
        else:
            raise ValueError(
                f"unsupported quality-change period_scope {family.period_scope!r}"
            )
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            prev = periods[j - 1]
            for dep_fam in family.depends_on_previous:
                deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


PER_SHARE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="reported_diluted_eps",
        order=67,
        title="Reported Diluted EPS",
        short_hint="Reported Net Income divided by diluted weighted-average shares.",
        semantic_key="per_share.reported_diluted_eps",
        category="per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("net_income_link",),
        hints=(
            "Diluted EPS = Reported Net Income / Diluted Weighted-Average Shares.",
            "Share count is a supplied historical input and remains populated.",
        ),
    ),
    ComponentFamily(
        id="nopat_per_diluted_share",
        order=68,
        title="NOPAT per Diluted Share",
        short_hint="Historical NOPAT divided by diluted weighted-average shares.",
        semantic_key="per_share.nopat_per_diluted_share",
        category="per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("nopat_fy",),
        hints=(
            "NOPAT per Diluted Share = NOPAT / Diluted Weighted-Average Shares.",
            "If NOPAT is undefined, the per-share amount is also undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="diluted_eps_change",
        order=69,
        title="Change in Diluted EPS",
        short_hint="Current Reported Diluted EPS minus prior EPS.",
        semantic_key="per_share.diluted_eps_change",
        category="per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("reported_diluted_eps",),
        depends_on_previous=("reported_diluted_eps",),
        hints=(
            "Change in Diluted EPS = Current EPS - Prior EPS.",
            "Use an absolute per-share change here rather than a growth rate that can become misleading around zero or negative EPS.",
        ),
    ),
    ComponentFamily(
        id="diluted_share_count_change",
        order=70,
        title="Change in Diluted Weighted-Average Shares",
        short_hint="Current diluted weighted-average shares minus prior shares.",
        semantic_key="per_share.diluted_share_count_change",
        category="per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        hints=(
            "Change in Diluted Weighted-Average Shares = Current Shares - Prior Shares.",
            "A positive change is mechanical evidence of a larger diluted share denominator; do not infer the cause automatically.",
        ),
    ),
)


def expand_per_share_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand diluted per-share families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_per_share_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_per_share_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in PER_SHARE_COMPONENT_CATALOG:
        if family.period_scope == "all":
            indices = range(len(periods))
        elif family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            raise ValueError(
                f"unsupported per-share period_scope {family.period_scope!r}"
            )
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="reported_net_income_change",
        order=71,
        title="Change in Reported Net Income",
        short_hint="Current Reported Net Income minus prior Reported Net Income.",
        semantic_key="per_share_attribution.reported_net_income_change",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("net_income_link",),
        depends_on_previous=("net_income_link",),
        hints=(
            "Change in Reported Net Income = Current Net Income - Prior Net Income.",
            "This is the earnings-numerator movement used in diluted-EPS attribution.",
        ),
    ),
    ComponentFamily(
        id="earnings_effect_on_diluted_eps_change",
        order=72,
        title="Earnings Effect on Change in Diluted EPS",
        short_hint="Change in Net Income multiplied by midpoint inverse diluted shares.",
        semantic_key="per_share_attribution.earnings_effect",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("reported_net_income_change",),
        hints=(
            "Earnings Effect = Change in Net Income × average of current and prior inverse diluted shares.",
            "Inverse diluted shares means 1 / diluted weighted-average shares.",
            "This is an arithmetic numerator effect, not a causal explanation of why earnings changed.",
        ),
    ),
    ComponentFamily(
        id="share_count_effect_on_diluted_eps_change",
        order=73,
        title="Share-Count Effect on Change in Diluted EPS",
        short_hint="Change in inverse diluted shares multiplied by midpoint Reported Net Income.",
        semantic_key="per_share_attribution.share_count_effect",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("diluted_share_count_change", "net_income_link"),
        depends_on_previous=("net_income_link",),
        hints=(
            "Share-Count Effect = Change in (1 / diluted shares) × average current/prior Net Income.",
            "Rising share count is not forced to a negative effect; losses can reverse the sign mechanically.",
            "Do not infer whether the share-count movement came from issuance, SBC, options, M&A, or buybacks without separate evidence.",
        ),
    ),
    ComponentFamily(
        id="diluted_eps_change_from_drivers",
        order=74,
        title="Change in Diluted EPS from Earnings + Share-Count Effects",
        short_hint="Earnings Effect plus Share-Count Effect.",
        semantic_key="per_share_attribution.diluted_eps_change_from_drivers",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=(
            "earnings_effect_on_diluted_eps_change",
            "share_count_effect_on_diluted_eps_change",
        ),
        hints=(
            "Change in Diluted EPS from Drivers = Earnings Effect + Share-Count Effect.",
            "The driver total must reconcile exactly to the direct Change in Diluted EPS.",
        ),
    ),
)


def expand_per_share_attribution_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand diluted-EPS attribution families into comparable-period specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in "
            "expand_per_share_attribution_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_per_share_attribution_specs requires strictly "
                "chronological (increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG:
        if family.period_scope != "comparable":
            raise ValueError(
                f"unsupported per-share-attribution period_scope "
                f"{family.period_scope!r}"
            )
        for j in range(1, len(periods)):
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            prev = periods[j - 1]
            for dep_fam in family.depends_on_previous:
                deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


NORMALIZED_PER_SHARE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="normalization_adjustment_per_diluted_share",
        order=75,
        title="Normalization Adjustment per Diluted Share",
        short_hint=(
            "After-tax normalization adjustment divided by diluted "
            "weighted-average shares."
        ),
        semantic_key="normalized_per_share.adjustment_per_diluted_share",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("after_tax_normalization_adjustment",),
        hints=(
            "Normalization Adjustment per Diluted Share = After-Tax "
            "Normalization Adjustment / Diluted Weighted-Average Shares.",
            "The sign is preserved; a positive normalization adjustment raises "
            "normalized EPS relative to reported EPS.",
        ),
    ),
    ComponentFamily(
        id="normalized_diluted_eps",
        order=76,
        title="Normalized Diluted EPS",
        short_hint="Normalized Net Income divided by diluted weighted-average shares.",
        semantic_key="normalized_per_share.normalized_diluted_eps",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("normalized_net_income",),
        hints=(
            "Normalized Diluted EPS = Normalized Net Income / Diluted "
            "Weighted-Average Shares.",
            "Use the current Normalization Judgment treatment; do not create a "
            "second treatment assumption here.",
        ),
    ),
    ComponentFamily(
        id="normalized_diluted_eps_change",
        order=77,
        title="Change in Normalized Diluted EPS",
        short_hint="Current normalized diluted EPS minus prior normalized diluted EPS.",
        semantic_key="normalized_per_share.normalized_diluted_eps_change",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("normalized_diluted_eps",),
        depends_on_previous=("normalized_diluted_eps",),
        hints=(
            "Change in Normalized Diluted EPS = Current Normalized EPS - Prior "
            "Normalized EPS.",
            "Undefined normalized EPS in either period makes the change undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="normalization_effect_on_diluted_eps_change",
        order=78,
        title="Normalization Effect on Change in Diluted EPS",
        short_hint="Change in normalization adjustment per diluted share.",
        semantic_key="normalized_per_share.normalization_effect_on_diluted_eps_change",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("normalization_adjustment_per_diluted_share",),
        depends_on_previous=("normalization_adjustment_per_diluted_share",),
        hints=(
            "Normalization Effect on EPS Change = Current Adjustment per Share - "
            "Prior Adjustment per Share.",
            "Reported EPS Change + this normalization effect must reconcile to "
            "Change in Normalized Diluted EPS when defined.",
        ),
    ),
)


def expand_normalized_per_share_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand normalized diluted-EPS bridge families into concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in "
            "expand_normalized_per_share_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_normalized_per_share_specs requires strictly "
                "chronological (increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in NORMALIZED_PER_SHARE_COMPONENT_CATALOG:
        if family.period_scope == "all":
            indices = range(len(periods))
        elif family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            raise ValueError(
                f"unsupported normalized-per-share period_scope "
                f"{family.period_scope!r}"
            )
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


FIXED_ASSET_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="ppe_source_link",
        order=79,
        title="Property, Plant & Equipment",
        short_hint="Link reported PP&E for the same fiscal period.",
        semantic_key="fixed_asset.ppe",
        category="fixed_asset",
        tab_template="ALT DuPont",
        hints=(
            "Pull ending Property, Plant & Equipment for the same fiscal period.",
            "This is a source link, not an investment conclusion.",
        ),
    ),
    ComponentFamily(
        id="da_source_link",
        order=80,
        title="Depreciation & Amortisation",
        short_hint="Link reported combined D&A for the same fiscal period.",
        semantic_key="fixed_asset.depreciation_amortization",
        category="fixed_asset",
        tab_template="ALT DuPont",
        hints=(
            "Pull Depreciation & Amortisation for the same fiscal period.",
            "Combined D&A may include intangible amortisation; do not treat it as a pure PP&E depreciation charge.",
        ),
    ),
    ComponentFamily(
        id="average_ppe",
        order=81,
        title="Average PP&E",
        short_hint="Average beginning and ending PP&E.",
        semantic_key="fixed_asset.average_ppe",
        category="fixed_asset",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("ppe_source_link",),
        depends_on_previous=("ppe_source_link",),
        hints=(
            "Average PP&E = (Prior PP&E + Current PP&E) / 2.",
        ),
    ),
    ComponentFamily(
        id="ppe_turnover",
        order=82,
        title="PP&E Turnover",
        short_hint="Revenue divided by Average PP&E.",
        semantic_key="fixed_asset.ppe_turnover",
        category="fixed_asset",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("revenue_link", "average_ppe"),
        hints=(
            "PP&E Turnover = Revenue / Average PP&E.",
            "A zero Average PP&E denominator makes the ratio undefined (#N/A).",
            "The ratio alone does not imply under- or over-investment.",
        ),
    ),
    ComponentFamily(
        id="ppe_intensity",
        order=83,
        title="PP&E Intensity",
        short_hint="Average PP&E divided by Revenue.",
        semantic_key="fixed_asset.ppe_intensity",
        category="fixed_asset",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("revenue_link", "average_ppe"),
        hints=(
            "PP&E Intensity = Average PP&E / Revenue.",
            "When defined, PP&E Turnover × PP&E Intensity = 1.",
            "A higher intensity is not automatically bad; diagnose the asset mix first.",
        ),
    ),
    ComponentFamily(
        id="ppe_change",
        order=84,
        title="Change in PP&E",
        short_hint="Current PP&E minus prior PP&E.",
        semantic_key="fixed_asset.ppe_change",
        category="fixed_asset",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("ppe_source_link",),
        depends_on_previous=("ppe_source_link",),
        hints=(
            "Change in PP&E = Current PP&E − Prior PP&E.",
            "This is not a capex amount; do not infer purchases of PP&E from the change alone.",
        ),
    ),
    ComponentFamily(
        id="da_to_revenue",
        order=85,
        title="D&A / Revenue",
        short_hint="Combined D&A divided by Revenue.",
        semantic_key="fixed_asset.da_to_revenue",
        category="fixed_asset",
        tab_template="ALT DuPont",
        depends_on_current=("da_source_link", "revenue_link"),
        hints=(
            "D&A / Revenue = Depreciation & Amortisation / Revenue.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="da_to_average_ppe",
        order=86,
        title="D&A / Average PP&E",
        short_hint="Combined D&A divided by Average PP&E (context ratio only).",
        semantic_key="fixed_asset.da_to_average_ppe",
        category="fixed_asset",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("da_source_link", "average_ppe"),
        hints=(
            "D&A / Average PP&E = Depreciation & Amortisation / Average PP&E.",
            "This is a context ratio, not automatically a pure PP&E depreciation rate, because the supplied D&A line may include intangible amortisation.",
            "Do not treat the ratio as a good/bad investment conclusion by itself.",
        ),
    ),
)


def expand_fixed_asset_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand fixed-asset families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_fixed_asset_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_fixed_asset_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in FIXED_ASSET_COMPONENT_CATALOG:
        if family.period_scope == "comparable":
            indices = range(1, len(periods))
        else:
            indices = range(len(periods))
        for j in indices:
            period = periods[j]
            deps: list[str] = []
            for dep_fam in family.depends_on_current:
                deps.append(concrete_component_id(dep_fam, period))
            if j > 0:
                prev = periods[j - 1]
                for dep_fam in family.depends_on_previous:
                    deps.append(concrete_component_id(dep_fam, prev))
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=concrete_component_id(family.id, period),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=j,
                    period_end=period_end,
                    depends_on=tuple(deps),
                    hints=family.hints,
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


def _deferred(
    *,
    id: str,
    order: int,
    title: str,
    short_hint: str,
    semantic_key: str,
    category: str,
    tab_template: str,
    scenario: str = "",
    depends_on: tuple[str, ...] = (),
    hints: tuple[str, ...] = (),
) -> ComponentSpec:
    return ComponentSpec(
        id=id,
        family_id=id,
        order=order,
        family_order=order,
        title=title,
        short_hint=short_hint,
        semantic_key=semantic_key,
        category=category,
        tab_template=tab_template,
        period_index=None,
        period_end="",
        depends_on=depends_on,
        hints=hints,
        scenario=scenario,
    )


# Dormant forecast/valuation specs — not part of public COMPONENT_CATALOG / list / Check.
DEFERRED_COMPONENT_SPECS: tuple[ComponentSpec, ...] = (
    _deferred(
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
    _deferred(
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
    _deferred(
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
    _deferred(
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
    _deferred(
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
    _deferred(
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


def catalog_by_id() -> dict[str, ComponentFamily]:
    return {c.id: c for c in COMPONENT_CATALOG}


def catalog_ids() -> list[str]:
    return [c.id for c in COMPONENT_CATALOG]
