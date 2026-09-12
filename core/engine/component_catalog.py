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
