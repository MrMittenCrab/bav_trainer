"""Semantic trainer component definitions — no workbook coordinates.

Coordinates are resolved at build time by the reference workbook builder and
stored in the semantic component map (single source of truth).

COMPONENT_CATALOG holds conceptual schedule families. Concrete period-specific
ComponentSpec rows are produced by expand_historical_specs(periods).
"""

from __future__ import annotations

import hashlib
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
    ComponentFamily(
        id="sbc_to_revenue",
        order=126,
        title="SBC / Revenue",
        short_hint=(
            "Reported stock-based compensation divided by Revenue. "
            "Mechanical diagnostic only; does not restate reported CFO, "
            "estimate cash compensation or dilution, establish free cash flow, "
            "or quantify tax effects."
        ),
        semantic_key="quality.sbc_to_revenue",
        category="earnings_quality",
        tab_template="Earnings Quality",
        depends_on_current=("revenue_link",),
        hints=(
            "SBC / Revenue = reported cash-flow stock-based compensation / Revenue.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Does not restate reported CFO, estimate cash compensation or dilution, "
            "establish free cash flow, or quantify tax effects.",
        ),
    ),
    ComponentFamily(
        id="sbc_to_operating_cash_flow",
        order=127,
        title="SBC / Operating Cash Flow",
        short_hint=(
            "Reported stock-based compensation divided by reported operating "
            "cash flow. Mechanical diagnostic only; does not restate reported "
            "CFO, estimate cash compensation or dilution, establish free cash "
            "flow, or quantify tax effects."
        ),
        semantic_key="quality.sbc_to_operating_cash_flow",
        category="earnings_quality",
        tab_template="Earnings Quality",
        depends_on_current=("operating_cash_flow_link",),
        hints=(
            "SBC / Operating Cash Flow = reported SBC / reported CFO.",
            "A zero CFO denominator makes the ratio undefined (#N/A).",
            "Does not restate reported CFO, estimate cash compensation or dilution, "
            "establish free cash flow, or quantify tax effects.",
        ),
    ),
    ComponentFamily(
        id="operating_cash_flow_less_sbc",
        order=128,
        title="Reported CFO less SBC add-back",
        short_hint=(
            "Reported CFO less SBC add-back. Mechanical diagnostic only; does "
            "not restate reported CFO, estimate cash compensation or dilution, "
            "establish free cash flow, or quantify tax effects."
        ),
        semantic_key="quality.operating_cash_flow_less_sbc",
        category="earnings_quality",
        tab_template="Earnings Quality",
        depends_on_current=("operating_cash_flow_link",),
        hints=(
            "Reported CFO less SBC add-back = reported operating cash flow − "
            "reported cash-flow stock-based compensation.",
            "This mechanical diagnostic does not restate reported CFO, estimate "
            "cash compensation or dilution, establish free cash flow, or "
            "quantify tax effects.",
        ),
    ),
)


QUALITY_SBC_FAMILY_IDS = frozenset(
    {
        "sbc_to_revenue",
        "sbc_to_operating_cash_flow",
        "operating_cash_flow_less_sbc",
    }
)

_QUALITY_ASSET_SCALED_FAMILY_IDS = frozenset(
    {
        "average_total_assets",
        "accrual_ratio",
    }
)


def expand_quality_specs(
    periods: list[date],
    *,
    start_order: int,
    include_asset_scaled: bool,
    include_sbc: bool = False,
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

    excluded: set[str] = set()
    if not include_asset_scaled:
        excluded |= _QUALITY_ASSET_SCALED_FAMILY_IDS
    if not include_sbc:
        excluded |= QUALITY_SBC_FAMILY_IDS
    families = tuple(
        family
        for family in QUALITY_COMPONENT_CATALOG
        if family.id not in excluded
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
        title="Diluted EPS (Comparable Basis)",
        short_hint=(
            "Earnings numerator / diluted weighted-average shares on the "
            "supplied comparable share basis."
        ),
        semantic_key="per_share.reported_diluted_eps",
        category="per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("net_income_link",),
        hints=(
            "Diluted EPS = Per-Share Earnings Numerator / Diluted Weighted-Average Shares.",
            "Share count is a supplied historical input and remains populated.",
            "When the supplied basis is split-adjusted, this is an analytical "
            "comparable figure and may differ from the originally printed pre-split EPS.",
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
        short_hint="Current comparable-basis Diluted EPS minus prior EPS.",
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
        title="Change in Per-Share Earnings Numerator",
        short_hint=(
            "Current per-share earnings numerator minus prior per-share earnings numerator."
        ),
        semantic_key="per_share_attribution.reported_net_income_change",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("net_income_link",),
        depends_on_previous=("net_income_link",),
        hints=(
            "Change in Per-Share Earnings Numerator = Current Numerator - Prior Numerator.",
            "This is the earnings-numerator movement used in diluted-EPS attribution.",
        ),
    ),
    ComponentFamily(
        id="earnings_effect_on_diluted_eps_change",
        order=72,
        title="Earnings Effect on Change in Diluted EPS",
        short_hint=(
            "Change in per-share earnings numerator multiplied by midpoint inverse diluted shares."
        ),
        semantic_key="per_share_attribution.earnings_effect",
        category="per_share_attribution",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("reported_net_income_change",),
        hints=(
            "Earnings Effect = Change in Per-Share Earnings Numerator × average of current and prior inverse diluted shares.",
            "Inverse diluted shares means 1 / diluted weighted-average shares.",
            "This is an arithmetic numerator effect, not a causal explanation of why earnings changed.",
        ),
    ),
    ComponentFamily(
        id="share_count_effect_on_diluted_eps_change",
        order=73,
        title="Share-Count Effect on Change in Diluted EPS",
        short_hint=(
            "Change in inverse diluted shares multiplied by midpoint per-share earnings numerator."
        ),
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


LEASE_LIABILITY_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="lease_liability_source_link",
        order=87,
        title="Lease Liability",
        short_hint="Link the reported aggregate lease-liability balance.",
        semantic_key="lease_liability.lease_liability",
        category="lease_liability",
        tab_template="ALT DuPont",
        hints=(
            "Pull the reported aggregate lease-liability balance for the same fiscal period.",
            "Classification as operating vs financial liability is a separate Accounting Judgment.",
            "This is not an ROU asset, lease payment, commitment, or amortization schedule.",
        ),
    ),
    ComponentFamily(
        id="lease_liability_to_revenue",
        order=88,
        title="Lease Liability / Revenue",
        short_hint="Reported lease liability divided by Revenue.",
        semantic_key="lease_liability.lease_liability_to_revenue",
        category="lease_liability",
        tab_template="ALT DuPont",
        depends_on_current=("lease_liability_source_link", "revenue_link"),
        hints=(
            "Lease Liability / Revenue = reported lease liability / Revenue.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "The ratio uses the reported balance, not the reformulated classification treatment.",
        ),
    ),
    ComponentFamily(
        id="lease_liability_change",
        order=89,
        title="Change in Lease Liability",
        short_hint="Current lease liability minus prior lease liability.",
        semantic_key="lease_liability.lease_liability_change",
        category="lease_liability",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("lease_liability_source_link",),
        depends_on_previous=("lease_liability_source_link",),
        hints=(
            "Change in Lease Liability = Current − Prior reported lease liability.",
            "Balance change is not rent growth, lease cash payments, or ROU-asset growth.",
        ),
    ),
    ComponentFamily(
        id="lease_liability_growth",
        order=90,
        title="Lease Liability Growth",
        short_hint="Percentage change in reported lease liability.",
        semantic_key="lease_liability.lease_liability_growth",
        category="lease_liability",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("lease_liability_source_link",),
        depends_on_previous=("lease_liability_source_link",),
        hints=(
            "Lease Liability Growth = Current / Prior − 1.",
            "A zero prior lease-liability balance makes percentage growth undefined (#N/A).",
            "Balance growth is not rent growth, lease cash payments, commitments, or ROU-asset growth.",
        ),
    ),
)


def expand_lease_liability_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand lease-liability families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_lease_liability_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_lease_liability_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in LEASE_LIABILITY_COMPONENT_CATALOG:
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


OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="parent_profit_source_link",
        order=91,
        title="Parent Profit",
        short_hint="Link reported profit attributable to owners of the parent.",
        semantic_key="ownership.parent_profit",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        hints=(
            "Pull the reported parent-attributable profit for the same fiscal period.",
            "Do not derive parent profit as total profit minus NCI when the parent line is missing.",
        ),
    ),
    ComponentFamily(
        id="nci_profit_source_link",
        order=92,
        title="NCI Profit",
        short_hint="Link reported profit attributable to non-controlling interests.",
        semantic_key="ownership.nci_profit",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        hints=(
            "Pull the reported NCI profit for the same fiscal period.",
            "Do not invent NCI profit from the consolidated total.",
        ),
    ),
    ComponentFamily(
        id="profit_attribution_gap",
        order=93,
        title="Profit Attribution Gap",
        short_hint="Parent profit + NCI profit − total profit.",
        semantic_key="ownership.profit_attribution_gap",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        depends_on_current=(
            "parent_profit_source_link",
            "nci_profit_source_link",
        ),
        hints=(
            "Profit Attribution Gap = Parent Profit + NCI Profit − Total Profit.",
            "Small gaps can arise from independent reporting-unit rounding.",
        ),
    ),
    ComponentFamily(
        id="parent_equity_source_link",
        order=94,
        title="Parent Equity",
        short_hint="Link reported equity attributable to owners of the parent.",
        semantic_key="ownership.parent_equity",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        hints=(
            "Pull the reported parent equity for the same fiscal period.",
            "Parent equity is not consolidated total equity.",
        ),
    ),
    ComponentFamily(
        id="nci_equity_source_link",
        order=95,
        title="NCI Equity",
        short_hint="Link reported non-controlling interests equity.",
        semantic_key="ownership.nci_equity",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        hints=(
            "Pull the reported NCI equity balance for the same fiscal period.",
            "Do not invent NCI equity from the consolidated total.",
        ),
    ),
    ComponentFamily(
        id="equity_attribution_gap",
        order=96,
        title="Equity Attribution Gap",
        short_hint="Parent equity + NCI equity − total equity.",
        semantic_key="ownership.equity_attribution_gap",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        depends_on_current=(
            "parent_equity_source_link",
            "nci_equity_source_link",
        ),
        hints=(
            "Equity Attribution Gap = Parent Equity + NCI Equity − Total Equity.",
            "Small gaps can arise from independent reporting-unit rounding.",
        ),
    ),
    ComponentFamily(
        id="parent_roe",
        order=97,
        title="Parent ROE",
        short_hint="Parent profit divided by average parent equity.",
        semantic_key="ownership.parent_roe",
        category="ownership_attribution",
        tab_template="Ownership Attribution",
        period_scope="comparable",
        depends_on_current=("parent_profit_source_link", "parent_equity_source_link"),
        depends_on_previous=("parent_equity_source_link",),
        hints=(
            "Parent ROE = Parent Profit / average(current, prior Parent Equity).",
            "This is a shareholder-attribution diagnostic, not consolidated DuPont ROE.",
        ),
    ),
)


def expand_ownership_attribution_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand ownership-attribution families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_ownership_attribution_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_ownership_attribution_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG:
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


GOODWILL_INTANGIBLES_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="goodwill_change",
        order=98,
        title="Change in Goodwill",
        short_hint=(
            "Current goodwill − prior goodwill. Flat goodwill does not establish "
            "absence of impairment disclosed elsewhere."
        ),
        semantic_key="goodwill_intangibles.goodwill_change",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in Goodwill = Current Goodwill − Prior Goodwill.",
            "Flat goodwill does not establish absence of impairment disclosed elsewhere.",
        ),
    ),
    ComponentFamily(
        id="goodwill_growth",
        order=99,
        title="Goodwill Growth",
        short_hint="Percentage change in reported goodwill.",
        semantic_key="goodwill_intangibles.goodwill_growth",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("goodwill_change",),
        hints=(
            "Goodwill Growth = Change in Goodwill / Prior Goodwill.",
            "A zero prior goodwill balance makes percentage growth undefined (#N/A).",
            "Flat goodwill does not establish absence of impairment disclosed elsewhere.",
        ),
    ),
    ComponentFamily(
        id="average_goodwill",
        order=100,
        title="Average Goodwill",
        short_hint="Average beginning and ending goodwill.",
        semantic_key="goodwill_intangibles.average_goodwill",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Average Goodwill = (Prior Goodwill + Current Goodwill) / 2.",
        ),
    ),
    ComponentFamily(
        id="goodwill_to_revenue",
        order=101,
        title="Average Goodwill / Revenue",
        short_hint=(
            "Average goodwill divided by Revenue (average-balance intensity)."
        ),
        semantic_key="goodwill_intangibles.goodwill_to_revenue",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("average_goodwill", "revenue_link"),
        hints=(
            "Average Goodwill / Revenue uses the average balance, not the ending level alone.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="intangible_assets_change",
        order=102,
        title="Change in Intangible Assets",
        short_hint="Current intangible assets − prior intangible assets.",
        semantic_key="goodwill_intangibles.intangible_assets_change",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in Intangible Assets = Current − Prior reported intangible assets.",
        ),
    ),
    ComponentFamily(
        id="intangible_assets_growth",
        order=103,
        title="Intangible Assets Growth",
        short_hint="Percentage change in reported intangible assets.",
        semantic_key="goodwill_intangibles.intangible_assets_growth",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("intangible_assets_change",),
        hints=(
            "Intangible Assets Growth = Change / Prior intangible assets.",
            "A zero prior balance makes percentage growth undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="average_intangible_assets",
        order=104,
        title="Average Intangible Assets",
        short_hint="Average beginning and ending intangible assets.",
        semantic_key="goodwill_intangibles.average_intangible_assets",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Average Intangible Assets = (Prior + Current) / 2.",
        ),
    ),
    ComponentFamily(
        id="intangible_assets_to_revenue",
        order=105,
        title="Average Intangible Assets / Revenue",
        short_hint=(
            "Average intangible assets divided by Revenue (average-balance intensity)."
        ),
        semantic_key="goodwill_intangibles.intangible_assets_to_revenue",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("average_intangible_assets", "revenue_link"),
        hints=(
            "Average Intangible Assets / Revenue uses the average balance.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="goodwill_and_intangibles_change",
        order=106,
        title="Change in Goodwill & Intangibles",
        short_hint="Current combined total − prior combined total.",
        semantic_key="goodwill_intangibles.goodwill_and_intangibles_change",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Combined total is the sum of uniquely resolved goodwill and intangible assets only.",
        ),
    ),
    ComponentFamily(
        id="goodwill_and_intangibles_growth",
        order=107,
        title="Goodwill & Intangibles Growth",
        short_hint="Percentage change in the combined goodwill and intangibles total.",
        semantic_key="goodwill_intangibles.goodwill_and_intangibles_growth",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("goodwill_and_intangibles_change",),
        hints=(
            "Growth = Change / Prior combined total.",
            "A zero prior combined total makes percentage growth undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="average_goodwill_and_intangibles",
        order=108,
        title="Average Goodwill & Intangibles",
        short_hint="Average beginning and ending combined goodwill and intangibles.",
        semantic_key="goodwill_intangibles.average_goodwill_and_intangibles",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Average = (Prior combined + Current combined) / 2.",
        ),
    ),
    ComponentFamily(
        id="goodwill_and_intangibles_to_revenue",
        order=109,
        title="Average Goodwill & Intangibles / Revenue",
        short_hint=(
            "Average combined goodwill and intangibles divided by Revenue."
        ),
        semantic_key="goodwill_intangibles.goodwill_and_intangibles_to_revenue",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("average_goodwill_and_intangibles", "revenue_link"),
        hints=(
            "Uses the average combined balance (average-balance intensity).",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="intangible_payments",
        order=110,
        title="Intangible Payments",
        short_hint=(
            "Presented as −reported payments for intangible assets. "
            "Intangible payments are not business acquisitions."
        ),
        semantic_key="goodwill_intangibles.intangible_payments",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        hints=(
            "Intangible Payments = −(reported payments for intangible assets).",
            "Do not apply absolute value; keep the −reported sign convention consistently.",
            "Intangible payments are not business acquisitions.",
        ),
    ),
    ComponentFamily(
        id="intangible_payments_to_revenue",
        order=111,
        title="Intangible Payments / Revenue",
        short_hint=(
            "Presented intangible payments divided by Revenue. "
            "Intangible payments are not business acquisitions."
        ),
        semantic_key="goodwill_intangibles.intangible_payments_to_revenue",
        category="goodwill_intangibles",
        tab_template="ALT DuPont",
        depends_on_current=("intangible_payments", "revenue_link"),
        hints=(
            "Intangible Payments / Revenue uses the −reported payment presentation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Intangible payments are not business acquisitions.",
        ),
    ),
)


_GOODWILL_FAMILY_GROUPS: dict[str, frozenset[str]] = {
    "goodwill": frozenset(
        {
            "goodwill_change",
            "goodwill_growth",
            "average_goodwill",
            "goodwill_to_revenue",
        }
    ),
    "intangible_assets": frozenset(
        {
            "intangible_assets_change",
            "intangible_assets_growth",
            "average_intangible_assets",
            "intangible_assets_to_revenue",
        }
    ),
    "goodwill_and_intangibles": frozenset(
        {
            "goodwill_and_intangibles_change",
            "goodwill_and_intangibles_growth",
            "average_goodwill_and_intangibles",
            "goodwill_and_intangibles_to_revenue",
        }
    ),
    "payments_for_intangible_assets": frozenset(
        {
            "intangible_payments",
            "intangible_payments_to_revenue",
        }
    ),
}


def expand_goodwill_intangibles_specs(
    periods: list[date],
    *,
    start_order: int,
    availability: object,
) -> tuple[ComponentSpec, ...]:
    """Expand available goodwill/intangibles families into period-specific specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_goodwill_intangibles_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_goodwill_intangibles_specs requires strictly chronological "
                "(increasing) period dates"
            )

    enabled: set[str] = set()
    if getattr(availability, "goodwill", False):
        enabled |= _GOODWILL_FAMILY_GROUPS["goodwill"]
    if getattr(availability, "intangible_assets", False):
        enabled |= _GOODWILL_FAMILY_GROUPS["intangible_assets"]
    if getattr(availability, "goodwill_and_intangibles", False):
        enabled |= _GOODWILL_FAMILY_GROUPS["goodwill_and_intangibles"]
    if getattr(availability, "payments_for_intangible_assets", False):
        enabled |= _GOODWILL_FAMILY_GROUPS["payments_for_intangible_assets"]
    if not enabled:
        return ()

    specs: list[ComponentSpec] = []
    order = start_order
    for family in GOODWILL_INTANGIBLES_COMPONENT_CATALOG:
        if family.id not in enabled:
            continue
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


LEASE_ROU_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="rou_assets_change",
        order=112,
        title="Change in Right-of-use Assets",
        short_hint="Current ROU assets − prior ROU assets.",
        semantic_key="lease_rou.rou_assets_change",
        category="lease_rou",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in Right-of-use Assets = Current − Prior reported ROU assets.",
            "Balance change is not lease cash payments, amortization, or liability change.",
        ),
    ),
    ComponentFamily(
        id="rou_assets_growth",
        order=113,
        title="Right-of-use Assets Growth",
        short_hint="Percentage change in reported ROU assets.",
        semantic_key="lease_rou.rou_assets_growth",
        category="lease_rou",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("rou_assets_change",),
        hints=(
            "Right-of-use Assets Growth = Change in ROU assets / Prior ROU assets.",
            "A zero prior ROU-asset balance makes percentage growth undefined (#N/A).",
            "Balance growth is not rent growth, lease cash payments, or liability growth.",
        ),
    ),
    ComponentFamily(
        id="average_rou_assets",
        order=114,
        title="Average Right-of-use Assets",
        short_hint="Average beginning and ending ROU assets.",
        semantic_key="lease_rou.average_rou_assets",
        category="lease_rou",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Average Right-of-use Assets = (Prior ROU assets + Current ROU assets) / 2.",
        ),
    ),
    ComponentFamily(
        id="rou_assets_to_revenue",
        order=115,
        title="Average Right-of-use Assets / Revenue",
        short_hint=(
            "Average ROU assets divided by current Revenue (balance intensity)."
        ),
        semantic_key="lease_rou.rou_assets_to_revenue",
        category="lease_rou",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("average_rou_assets", "revenue_link"),
        hints=(
            "Average Right-of-use Assets / Revenue uses the average balance, not "
            "the ending level alone.",
            "Intensity is balance context only — not lease payments, discount rates, "
            "amortization, or liability reconciliation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
        ),
    ),
)


def expand_lease_rou_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand lease-ROU families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_lease_rou_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_lease_rou_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in LEASE_ROU_COMPONENT_CATALOG:
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


CAPEX_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="ppe_capex",
        order=120,
        title="PP&E Capex (−reported)",
        short_hint=(
            "Presented as −reported payments for property, plant and equipment."
        ),
        semantic_key="capex.ppe_capex",
        category="capex",
        tab_template="ALT DuPont",
        hints=(
            "PP&E Capex = −(reported payments for property, plant and equipment).",
            "Do not apply absolute value; keep the −reported sign convention consistently.",
            "Explicit zero reported payments remain valid (zero capex).",
        ),
    ),
    ComponentFamily(
        id="ppe_capex_to_revenue",
        order=121,
        title="PP&E Capex / Revenue",
        short_hint="Presented PP&E capex divided by same-period Revenue.",
        semantic_key="capex.ppe_capex_to_revenue",
        category="capex",
        tab_template="ALT DuPont",
        depends_on_current=("ppe_capex", "revenue_link"),
        hints=(
            "PP&E Capex / Revenue uses the −reported payment presentation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Revenue intensity only — not a reinvestment bridge or depreciation ratio.",
        ),
    ),
    ComponentFamily(
        id="cash_after_ppe_capex",
        order=124,
        title="Operating cash after PP&E capex",
        short_hint=(
            "Reported operating cash flow minus PP&E capex. "
            "Excludes other investing flows and is not comprehensive free cash "
            "flow or a maintenance/growth-capex estimate."
        ),
        semantic_key="capex.cash_after_ppe_capex",
        category="capex",
        tab_template="ALT DuPont",
        depends_on_current=("ppe_capex",),
        hints=(
            "Operating cash after PP&E capex = reported operating cash flow − PP&E capex.",
            "Excludes other investing flows and is not comprehensive free cash flow "
            "or a maintenance/growth-capex estimate.",
            "Uses the −reported PP&E payment presentation already on this schedule.",
        ),
    ),
    ComponentFamily(
        id="cash_after_ppe_capex_to_revenue",
        order=125,
        title="Operating cash after PP&E capex / Revenue",
        short_hint=(
            "Operating cash after PP&E capex divided by same-period Revenue. "
            "Excludes other investing flows; not comprehensive free cash flow "
            "or a maintenance/growth-capex estimate."
        ),
        semantic_key="capex.cash_after_ppe_capex_to_revenue",
        category="capex",
        tab_template="ALT DuPont",
        depends_on_current=("cash_after_ppe_capex", "revenue_link"),
        hints=(
            "Operating cash after PP&E capex / Revenue uses CFO minus PP&E capex.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Not comprehensive free cash flow or a maintenance/growth-capex estimate.",
        ),
    ),
)


_CAPEX_CASH_AFTER_FAMILY_IDS = frozenset(
    {
        "cash_after_ppe_capex",
        "cash_after_ppe_capex_to_revenue",
    }
)


def expand_capex_specs(
    periods: list[date],
    *,
    start_order: int,
    include_operating_cash: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand capex families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_capex_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_capex_specs requires strictly chronological "
                "(increasing) period dates"
            )

    families = CAPEX_COMPONENT_CATALOG
    if not include_operating_cash:
        families = tuple(
            family
            for family in CAPEX_COMPONENT_CATALOG
            if family.id not in _CAPEX_CASH_AFTER_FAMILY_IDS
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


LEASE_REPAYMENT_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="lease_repayments",
        order=122,
        title="Lease Repayments (−reported)",
        short_hint=(
            "Presented as −reported cash repayments of lease liabilities. "
            "Not total lease cost, ROU amortization, or liability movement."
        ),
        semantic_key="lease_repayment.lease_repayments",
        category="lease_repayment",
        tab_template="ALT DuPont",
        hints=(
            "Lease Repayments = −(reported repayments of lease liabilities).",
            "Do not apply absolute value; keep the −reported sign convention consistently.",
            "This is reported repayment cash only — not total lease cost, ROU "
            "amortization, or the change in lease liability.",
            "Explicit zero reported repayments remain valid (zero repayments).",
        ),
    ),
    ComponentFamily(
        id="lease_repayments_to_revenue",
        order=123,
        title="Lease Repayments / Revenue",
        short_hint=(
            "Presented lease repayments divided by same-period Revenue. "
            "Cash intensity only — not liability stock or ROU amortization."
        ),
        semantic_key="lease_repayment.lease_repayments_to_revenue",
        category="lease_repayment",
        tab_template="ALT DuPont",
        depends_on_current=("lease_repayments", "revenue_link"),
        hints=(
            "Lease Repayments / Revenue uses the −reported repayment presentation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Revenue intensity of repayment cash only — not total lease cost, "
            "ROU amortization, or liability movement.",
        ),
    ),
)


def expand_lease_repayment_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand lease-repayment families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_lease_repayment_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_lease_repayment_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in LEASE_REPAYMENT_COMPONENT_CATALOG:
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


ACQUISITION_CASH_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="acquisition_cash_outflow",
        order=129,
        title="Acquisition cash outflow (−reported)",
        short_hint=(
            "Presented as −reported acquisition cash, net of cash acquired. "
            "Mechanical cash-use diagnostic only; not comprehensive free cash "
            "flow, acquisition profitability, purchase-price allocation, or a "
            "goodwill roll-forward."
        ),
        semantic_key="acquisition_cash.acquisition_cash_outflow",
        category="acquisition_cash",
        tab_template="ALT DuPont",
        hints=(
            "Acquisition cash outflow = −(reported acquisition, net of cash acquired).",
            "Do not apply absolute value; keep the −reported sign convention consistently.",
            "Net-of-acquired-cash reporting is retained as filed; explicit zeros remain valid.",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow, "
            "acquisition profitability, purchase-price allocation, or a goodwill "
            "roll-forward.",
        ),
    ),
    ComponentFamily(
        id="acquisition_cash_to_revenue",
        order=130,
        title="Acquisition cash / Revenue",
        short_hint=(
            "Acquisition cash outflow divided by same-period Revenue. Reported "
            "net of cash acquired. Mechanical cash-use diagnostic only; not "
            "comprehensive free cash flow, acquisition profitability, "
            "purchase-price allocation, or a goodwill roll-forward."
        ),
        semantic_key="acquisition_cash.acquisition_cash_to_revenue",
        category="acquisition_cash",
        tab_template="ALT DuPont",
        depends_on_current=("acquisition_cash_outflow", "revenue_link"),
        hints=(
            "Acquisition cash / Revenue uses the −reported net-of-acquired-cash "
            "presentation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow, "
            "acquisition profitability, purchase-price allocation, or a goodwill "
            "roll-forward.",
        ),
    ),
    ComponentFamily(
        id="cash_after_ppe_capex_and_acquisitions",
        order=131,
        title="Operating cash after PP&E capex and acquisitions",
        short_hint=(
            "Reported CFO minus PP&E capex minus acquisition cash outflow "
            "(net of cash acquired). Mechanical cash-use diagnostic only; not "
            "comprehensive free cash flow, acquisition profitability, "
            "purchase-price allocation, or a goodwill roll-forward."
        ),
        semantic_key="acquisition_cash.cash_after_ppe_capex_and_acquisitions",
        category="acquisition_cash",
        tab_template="ALT DuPont",
        depends_on_current=("ppe_capex", "acquisition_cash_outflow"),
        hints=(
            "Operating cash after PP&E capex and acquisitions = reported CFO − "
            "PP&E capex − acquisition cash outflow.",
            "Acquisition cash is the −reported net-of-acquired-cash line; PP&E "
            "capex keeps its established −reported contract.",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow, "
            "acquisition profitability, purchase-price allocation, or a goodwill "
            "roll-forward.",
        ),
    ),
)


_ACQUISITION_CASH_RESIDUAL_FAMILY_IDS = frozenset(
    {
        "cash_after_ppe_capex_and_acquisitions",
    }
)


def expand_acquisition_cash_specs(
    periods: list[date],
    *,
    start_order: int,
    include_cash_after_capex: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand acquisition-cash families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_acquisition_cash_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_acquisition_cash_specs requires strictly chronological "
                "(increasing) period dates"
            )

    families = ACQUISITION_CASH_COMPONENT_CATALOG
    if not include_cash_after_capex:
        families = tuple(
            family
            for family in ACQUISITION_CASH_COMPONENT_CATALOG
            if family.id not in _ACQUISITION_CASH_RESIDUAL_FAMILY_IDS
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


SHARE_REPURCHASE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="share_repurchase_outflow",
        order=132,
        title="Share-repurchase outflow (−reported)",
        short_hint=(
            "Presented as −reported repurchase of common stock. Reported cash "
            "repurchase only — not total shareholder distributions, dividends, "
            "treasury-stock movements, share-count change, SBC, settlement "
            "proceeds, withholding, or dilution. Mechanical cash-use diagnostic "
            "only; not comprehensive free cash flow or a complete cash "
            "reconciliation."
        ),
        semantic_key="share_repurchase.share_repurchase_outflow",
        category="share_repurchase",
        tab_template="ALT DuPont",
        hints=(
            "Share-repurchase outflow = −(reported repurchase of common stock).",
            "Do not apply absolute value; keep the −reported sign convention consistently.",
            "This is the reported cash repurchase line only — not total shareholder "
            "distributions or dilution effects.",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow "
            "or a complete cash reconciliation.",
        ),
    ),
    ComponentFamily(
        id="share_repurchase_to_revenue",
        order=133,
        title="Share-repurchase / Revenue",
        short_hint=(
            "Share-repurchase outflow divided by same-period Revenue. Uses the "
            "reported repurchase-of-common-stock cash line, not total shareholder "
            "distributions or dilution. Mechanical cash-use diagnostic only; not "
            "comprehensive free cash flow or a complete cash reconciliation."
        ),
        semantic_key="share_repurchase.share_repurchase_to_revenue",
        category="share_repurchase",
        tab_template="ALT DuPont",
        depends_on_current=("share_repurchase_outflow", "revenue_link"),
        hints=(
            "Share-repurchase / Revenue uses the −reported repurchase-of-common-stock "
            "presentation.",
            "A zero Revenue denominator makes the ratio undefined (#N/A).",
            "Reported cash repurchase only — not total shareholder distributions or "
            "dilution.",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow "
            "or a complete cash reconciliation.",
        ),
    ),
    ComponentFamily(
        id="cash_after_ppe_capex_acquisitions_and_repurchases",
        order=134,
        title="Operating cash after PP&E capex, acquisitions and repurchases",
        short_hint=(
            "Reported CFO minus PP&E capex minus acquisition cash outflow minus "
            "share-repurchase outflow. A negative residual means these selected "
            "cash uses exceed reported CFO; it does not identify debt funding. "
            "Mechanical cash-use diagnostic only — not comprehensive free cash "
            "flow or a complete cash reconciliation."
        ),
        semantic_key=(
            "share_repurchase.cash_after_ppe_capex_acquisitions_and_repurchases"
        ),
        category="share_repurchase",
        tab_template="ALT DuPont",
        depends_on_current=(
            "ppe_capex",
            "acquisition_cash_outflow",
            "share_repurchase_outflow",
        ),
        hints=(
            "Operating cash after PP&E capex, acquisitions and repurchases = "
            "reported CFO − PP&E capex − acquisition cash outflow − "
            "share-repurchase outflow.",
            "A negative residual means these selected cash uses exceed reported "
            "CFO; it does not identify debt funding.",
            "Mechanical cash-use diagnostic only — not comprehensive free cash flow "
            "or a complete cash reconciliation.",
        ),
    ),
)


_SHARE_REPURCHASE_RESIDUAL_FAMILY_IDS = frozenset(
    {
        "cash_after_ppe_capex_acquisitions_and_repurchases",
    }
)


def expand_share_repurchase_specs(
    periods: list[date],
    *,
    start_order: int,
    include_residual: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand share-repurchase families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_share_repurchase_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_share_repurchase_specs requires strictly chronological "
                "(increasing) period dates"
            )

    families = SHARE_REPURCHASE_COMPONENT_CATALOG
    if not include_residual:
        families = tuple(
            family
            for family in SHARE_REPURCHASE_COMPONENT_CATALOG
            if family.id not in _SHARE_REPURCHASE_RESIDUAL_FAMILY_IDS
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


CASH_ROLLFORWARD_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="cash_movement_from_flows",
        order=135,
        title="Cash movement from flows",
        short_hint=(
            "CFO + CFI + CFF + FX using reported signed cash-flow totals in "
            "statement units, including the FX effect. Keep reported signs; do "
            "not reverse flows, omit FX, substitute balance-sheet cash, insert a "
            "balancing plug, or infer debt funding."
        ),
        semantic_key="cash_rollforward.cash_movement_from_flows",
        category="cash_rollforward",
        tab_template="ALT DuPont",
        hints=(
            "Cash movement from flows = reported CFO + CFI + CFF + FX.",
            "Use signed statement-unit totals, including FX.",
            "Do not substitute balance-sheet cash, insert a balancing plug, or "
            "infer debt funding.",
        ),
    ),
    ComponentFamily(
        id="cash_movement_difference",
        order=136,
        title="Cash movement difference",
        short_hint=(
            "Calculated cash movement from flows minus reported cash change, in "
            "statement units. A nonzero difference is a reported reconciliation "
            "gap; do not insert a balancing plug, assert a cause, substitute "
            "balance-sheet cash, or infer debt funding."
        ),
        semantic_key="cash_rollforward.cash_movement_difference",
        category="cash_rollforward",
        tab_template="ALT DuPont",
        depends_on_current=("cash_movement_from_flows",),
        hints=(
            "Cash movement difference = cash movement from flows − reported cash "
            "change.",
            "Preserve nonzero calculated-minus-reported gaps in statement units.",
            "Do not insert a balancing plug, assert a cause, substitute "
            "balance-sheet cash, or infer debt funding.",
        ),
    ),
    ComponentFamily(
        id="cash_ending_from_flows",
        order=137,
        title="Cash ending from flows",
        short_hint=(
            "Reported cash beginning plus cash movement from flows (CFO + CFI + "
            "CFF + FX), in statement units. Keep signed flows and FX as reported; "
            "do not substitute balance-sheet cash, insert a balancing plug, or "
            "infer debt funding."
        ),
        semantic_key="cash_rollforward.cash_ending_from_flows",
        category="cash_rollforward",
        tab_template="ALT DuPont",
        depends_on_current=("cash_movement_from_flows",),
        hints=(
            "Cash ending from flows = reported cash beginning + cash movement "
            "from flows.",
            "Movement includes signed CFO, CFI, CFF, and FX in statement units.",
            "Do not substitute balance-sheet cash, insert a balancing plug, or "
            "infer debt funding.",
        ),
    ),
    ComponentFamily(
        id="cash_ending_difference",
        order=138,
        title="Cash ending difference",
        short_hint=(
            "Cash ending from flows minus reported cash ending, in statement "
            "units. A nonzero difference is a reported reconciliation gap; do "
            "not insert a balancing plug, assert a cause, substitute "
            "balance-sheet cash, or infer debt funding."
        ),
        semantic_key="cash_rollforward.cash_ending_difference",
        category="cash_rollforward",
        tab_template="ALT DuPont",
        depends_on_current=("cash_ending_from_flows",),
        hints=(
            "Cash ending difference = cash ending from flows − reported cash "
            "ending.",
            "Preserve nonzero calculated-minus-reported gaps in statement units.",
            "Do not insert a balancing plug, assert a cause, substitute "
            "balance-sheet cash, or infer debt funding.",
        ),
    ),
)


def expand_cash_rollforward_specs(
    periods: list[date],
    *,
    start_order: int,
    include_movement_difference: bool = False,
    include_ending_from_flows: bool = False,
    include_ending_difference: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand cash-roll-forward families into period-specific concrete specs."""
    if include_ending_difference and not include_ending_from_flows:
        raise ValueError(
            "expand_cash_rollforward_specs ending difference requires "
            "cash_ending_from_flows"
        )
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_cash_rollforward_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_cash_rollforward_specs requires strictly chronological "
                "(increasing) period dates"
            )

    omit: set[str] = set()
    if not include_movement_difference:
        omit.add("cash_movement_difference")
    if not include_ending_from_flows:
        omit.add("cash_ending_from_flows")
    if not include_ending_difference:
        omit.add("cash_ending_difference")
    families = tuple(
        family
        for family in CASH_ROLLFORWARD_COMPONENT_CATALOG
        if family.id not in omit
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


REPORTED_MARGIN_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="gross_margin",
        order=139,
        title="Gross margin",
        short_hint=(
            "Gross margin = reported gross profit / revenue. Zero revenue is "
            "undefined (#N/A). Do not infer price, mix, or cost causes."
        ),
        semantic_key="reported_margin.gross_margin",
        category="reported_margin",
        tab_template="ALT DuPont",
        hints=(
            "Gross margin = reported gross profit / revenue.",
            "Zero revenue yields the undefined-ratio result.",
            "Do not infer price, mix, or cost causes.",
        ),
    ),
    ComponentFamily(
        id="reported_operating_margin",
        order=140,
        title="Reported operating margin",
        short_hint=(
            "Reported operating margin = reported operating profit / revenue. "
            "Distinct from BAV NOPAT margin; not normalized earnings. Zero "
            "revenue is undefined (#N/A)."
        ),
        semantic_key="reported_margin.reported_operating_margin",
        category="reported_margin",
        tab_template="ALT DuPont",
        hints=(
            "Reported operating margin = reported operating profit / revenue.",
            "Keep reported operating margin distinct from BAV NOPAT margin.",
            "Do not treat this as normalized earnings.",
        ),
    ),
    ComponentFamily(
        id="net_operating_expense_burden",
        order=141,
        title="Net operating expense burden",
        short_hint=(
            "Net operating expense burden = (gross profit − operating profit) / "
            "revenue. That difference includes net intervening operating items; "
            "it is not necessarily SG&A. Zero revenue is undefined (#N/A)."
        ),
        semantic_key="reported_margin.net_operating_expense_burden",
        category="reported_margin",
        tab_template="ALT DuPont",
        hints=(
            "Net operating expense burden = (gross profit − operating profit) / "
            "revenue.",
            "Gross profit minus operating profit includes net intervening "
            "operating items; it is not necessarily SG&A.",
            "Zero revenue yields the undefined-ratio result.",
        ),
    ),
    ComponentFamily(
        id="gross_margin_change",
        order=142,
        title="Change in gross margin",
        short_hint=(
            "Change in gross margin is a percentage-point movement: current "
            "gross margin minus prior gross margin. Do not infer price, mix, "
            "or cost causes."
        ),
        semantic_key="reported_margin.gross_margin_change",
        category="reported_margin",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("gross_margin",),
        depends_on_previous=("gross_margin",),
        hints=(
            "Change in gross margin = current gross margin − prior gross margin.",
            "This is a percentage-point movement, not a causal explanation.",
            "Do not infer price, mix, or cost causes.",
        ),
    ),
    ComponentFamily(
        id="net_operating_expense_burden_change",
        order=143,
        title="Change in net operating expense burden",
        short_hint=(
            "Change in net operating expense burden is a percentage-point "
            "movement: current burden minus prior burden. A positive burden "
            "change reduces reported operating margin. Intervening items are "
            "not necessarily SG&A."
        ),
        semantic_key="reported_margin.net_operating_expense_burden_change",
        category="reported_margin",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("net_operating_expense_burden",),
        depends_on_previous=("net_operating_expense_burden",),
        hints=(
            "Change in net operating expense burden = current burden − prior "
            "burden.",
            "A positive burden change reduces reported operating margin.",
            "Gross profit minus operating profit is not necessarily SG&A.",
        ),
    ),
    ComponentFamily(
        id="reconstructed_operating_margin_change",
        order=144,
        title="Reconstructed change in reported operating margin",
        short_hint=(
            "Reconstructed operating-margin change = gross-margin change − "
            "burden change, in percentage points. It reconciles to the adjacent "
            "reported operating-margin difference. Do not infer price, mix, "
            "cost causes, or normalized earnings; keep this distinct from BAV "
            "NOPAT margin."
        ),
        semantic_key="reported_margin.reconstructed_operating_margin_change",
        category="reported_margin",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=(
            "gross_margin_change",
            "net_operating_expense_burden_change",
        ),
        hints=(
            "Reconstructed operating-margin change = gross-margin change − "
            "burden change.",
            "When defined, this equals the adjacent reported operating-margin "
            "difference.",
            "Do not infer price, mix, cost causes, or normalized earnings.",
        ),
    ),
)


def expand_reported_margin_specs(
    periods: list[date],
    *,
    start_order: int,
    include_gross_margin: bool = False,
    include_operating_margin: bool = False,
    include_burden: bool = False,
    include_gross_margin_change: bool = False,
    include_burden_change: bool = False,
    include_reconstructed: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand reported-margin families into period-specific concrete specs."""
    if include_gross_margin_change and not include_gross_margin:
        raise ValueError(
            "expand_reported_margin_specs gross-margin change requires gross_margin"
        )
    if include_burden_change and not include_burden:
        raise ValueError(
            "expand_reported_margin_specs burden change requires "
            "net_operating_expense_burden"
        )
    if include_reconstructed and not (
        include_gross_margin_change and include_burden_change
    ):
        raise ValueError(
            "expand_reported_margin_specs reconstructed change requires "
            "gross_margin_change and net_operating_expense_burden_change"
        )
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_reported_margin_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_reported_margin_specs requires strictly chronological "
                "(increasing) period dates"
            )

    omit: set[str] = set()
    if not include_gross_margin:
        omit.add("gross_margin")
    if not include_operating_margin:
        omit.add("reported_operating_margin")
    if not include_burden:
        omit.add("net_operating_expense_burden")
    if not include_gross_margin_change:
        omit.add("gross_margin_change")
    if not include_burden_change:
        omit.add("net_operating_expense_burden_change")
    if not include_reconstructed:
        omit.add("reconstructed_operating_margin_change")
    families = tuple(
        family
        for family in REPORTED_MARGIN_COMPONENT_CATALOG
        if family.id not in omit
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


INVENTORY_ANALYSIS_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="inventory_intensity",
        order=145,
        title="Inventory intensity",
        short_hint=(
            "Inventory intensity = ending inventory / annual revenue. This is "
            "not inventory days or turnover. Zero revenue is undefined (#N/A)."
        ),
        semantic_key="inventory_analysis.inventory_intensity",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        hints=(
            "Inventory intensity = ending inventory / annual revenue.",
            "This is not inventory days or turnover.",
            "Zero revenue yields the undefined-ratio result.",
        ),
    ),
    ComponentFamily(
        id="inventory_change",
        order=146,
        title="Change in inventory",
        short_hint=(
            "Change in inventory = current inventory − prior inventory "
            "(signed). Opening-period change is not practiced. This is not "
            "proof of cash movement, markdowns, or management causes."
        ),
        semantic_key="inventory_analysis.inventory_change",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in inventory = current inventory − prior inventory.",
            "The movement is signed; it is not proof of cash movement.",
            "Do not infer markdowns or management causes.",
        ),
    ),
    ComponentFamily(
        id="inventory_revenue_scale_effect",
        order=147,
        title="Revenue-scale effect on inventory",
        short_hint=(
            "Revenue-scale effect = prior inventory intensity × (current "
            "revenue − prior revenue). Uses the prior-intensity / "
            "current-revenue attribution convention. Signed; not a "
            "cash-movement proof."
        ),
        semantic_key="inventory_analysis.inventory_revenue_scale_effect",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_previous=("inventory_intensity",),
        hints=(
            "Revenue-scale effect = prior inventory intensity × (current "
            "revenue − prior revenue).",
            "This uses the prior-intensity / current-revenue convention.",
            "Signed arithmetic only; not proof of cash movement.",
        ),
    ),
    ComponentFamily(
        id="inventory_intensity_effect",
        order=148,
        title="Intensity effect on inventory",
        short_hint=(
            "Intensity effect = current revenue × (current inventory "
            "intensity − prior inventory intensity). Uses the "
            "prior-intensity / current-revenue attribution convention. "
            "Signed; not proof of deterioration, seasonality, or markdowns."
        ),
        semantic_key="inventory_analysis.inventory_intensity_effect",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("inventory_intensity",),
        depends_on_previous=("inventory_intensity",),
        hints=(
            "Intensity effect = current revenue × (current intensity − "
            "prior intensity).",
            "This uses the prior-intensity / current-revenue convention.",
            "Signed arithmetic only; not proof of deterioration, seasonality, "
            "or markdowns.",
        ),
    ),
    ComponentFamily(
        id="reconstructed_inventory_change",
        order=149,
        title="Reconstructed change in inventory",
        short_hint=(
            "Reconstructed inventory change = revenue-scale effect + "
            "intensity effect. Arithmetic decomposition that reconciles to "
            "the inventory change when defined. Not inventory days/turnover "
            "and not proof of cash movement, deterioration, seasonality, "
            "markdowns, or management causes."
        ),
        semantic_key="inventory_analysis.reconstructed_inventory_change",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=(
            "inventory_revenue_scale_effect",
            "inventory_intensity_effect",
        ),
        hints=(
            "Reconstructed inventory change = revenue-scale effect + "
            "intensity effect.",
            "When defined, this reconciles to the adjacent inventory change.",
            "Arithmetic decomposition only; not cash movement, deterioration, "
            "seasonality, markdowns, or management causes.",
        ),
    ),
    ComponentFamily(
        id="inventory_balance_implied_cf_adjustment",
        order=150,
        title="Balance-implied inventory CF adjustment",
        short_hint=(
            "Balance-implied inventory CF adjustment = −(current inventory − "
            "prior inventory), the negative of the inventory balance movement. "
            "This is not the reported operating cash-flow reconciliation "
            "adjustment. Opening-period comparison is not practiced."
        ),
        semantic_key="inventory_analysis.inventory_balance_implied_cf_adjustment",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("inventory_change",),
        hints=(
            "Balance-implied inventory CF adjustment = −(current inventory − "
            "prior inventory).",
            "This is the negative of the inventory balance movement, not the "
            "reported operating cash-flow reconciliation adjustment.",
            "Do not treat this as cash paid for inventory.",
        ),
    ),
    ComponentFamily(
        id="inventory_cf_adjustment_difference",
        order=151,
        title="Unexplained inventory CF difference",
        short_hint=(
            "Unexplained inventory CF difference = reported operating CF "
            "inventory adjustment − balance-implied adjustment. A nonzero "
            "difference needs further evidence; it does not establish an "
            "error, cash paid for inventory, FX, acquisitions, write-downs, "
            "or another specific cause. Do not insert a balancing plug."
        ),
        semantic_key="inventory_analysis.inventory_cf_adjustment_difference",
        category="inventory_analysis",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("inventory_balance_implied_cf_adjustment",),
        hints=(
            "Unexplained inventory CF difference = reported operating CF "
            "inventory adjustment − balance-implied adjustment.",
            "A nonzero difference needs further evidence; it does not "
            "establish an error, cash paid for inventory, FX, acquisitions, "
            "write-downs, or another specific cause.",
            "Do not insert a balancing plug.",
        ),
    ),
)


def expand_inventory_analysis_specs(
    periods: list[date],
    *,
    start_order: int,
    include_intensity: bool = False,
    include_change: bool = False,
    include_revenue_scale: bool = False,
    include_intensity_effect: bool = False,
    include_reconstructed: bool = False,
    include_balance_implied: bool = False,
    include_cf_difference: bool = False,
) -> tuple[ComponentSpec, ...]:
    """Expand inventory-analysis families into period-specific concrete specs."""
    if include_revenue_scale and not include_intensity:
        raise ValueError(
            "expand_inventory_analysis_specs revenue-scale requires "
            "inventory_intensity"
        )
    if include_intensity_effect and not include_intensity:
        raise ValueError(
            "expand_inventory_analysis_specs intensity effect requires "
            "inventory_intensity"
        )
    if include_reconstructed and not (
        include_revenue_scale and include_intensity_effect
    ):
        raise ValueError(
            "expand_inventory_analysis_specs reconstructed change requires "
            "inventory_revenue_scale_effect and inventory_intensity_effect"
        )
    if include_balance_implied and not include_change:
        raise ValueError(
            "expand_inventory_analysis_specs balance-implied requires "
            "inventory_change"
        )
    if include_cf_difference and not include_balance_implied:
        raise ValueError(
            "expand_inventory_analysis_specs CF difference requires "
            "inventory_balance_implied_cf_adjustment"
        )
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in "
            "expand_inventory_analysis_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_inventory_analysis_specs requires strictly chronological "
                "(increasing) period dates"
            )

    omit: set[str] = set()
    if not include_intensity:
        omit.add("inventory_intensity")
    if not include_change:
        omit.add("inventory_change")
    if not include_revenue_scale:
        omit.add("inventory_revenue_scale_effect")
    if not include_intensity_effect:
        omit.add("inventory_intensity_effect")
    if not include_reconstructed:
        omit.add("reconstructed_inventory_change")
    if not include_balance_implied:
        omit.add("inventory_balance_implied_cf_adjustment")
    if not include_cf_difference:
        omit.add("inventory_cf_adjustment_difference")
    families = tuple(
        family
        for family in INVENTORY_ANALYSIS_COMPONENT_CATALOG
        if family.id not in omit
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


DEFERRED_TAX_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="net_deferred_tax_position",
        order=116,
        title="Net Deferred-Tax Asset Position (DTA − DTL)",
        short_hint="Analytical net position = Deferred tax assets − Deferred tax liabilities.",
        semantic_key="deferred_tax.net_deferred_tax_position",
        category="deferred_tax",
        tab_template="ALT DuPont",
        hints=(
            "Net Deferred-Tax Asset Position = Deferred tax assets − Deferred tax "
            "liabilities (same period).",
            "Analytical DTA less DTL only — not deferred-tax expense, cash taxes, "
            "recoverability, or legal offset eligibility.",
        ),
    ),
    ComponentFamily(
        id="deferred_tax_assets_change",
        order=117,
        title="Change in Deferred Tax Assets",
        short_hint="Current DTA − prior DTA.",
        semantic_key="deferred_tax.deferred_tax_assets_change",
        category="deferred_tax",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in Deferred Tax Assets = Current DTA − Prior DTA.",
            "Balance movement only — not deferred-tax expense or cash taxes.",
        ),
    ),
    ComponentFamily(
        id="deferred_tax_liabilities_change",
        order=118,
        title="Change in Deferred Tax Liabilities",
        short_hint="Current DTL − prior DTL.",
        semantic_key="deferred_tax.deferred_tax_liabilities_change",
        category="deferred_tax",
        tab_template="ALT DuPont",
        period_scope="comparable",
        hints=(
            "Change in Deferred Tax Liabilities = Current DTL − Prior DTL.",
            "Balance movement only — not deferred-tax expense or cash taxes.",
        ),
    ),
    ComponentFamily(
        id="net_deferred_tax_position_change",
        order=119,
        title="Change in Net Deferred-Tax Asset Position",
        short_hint="Current net position − prior net position.",
        semantic_key="deferred_tax.net_deferred_tax_position_change",
        category="deferred_tax",
        tab_template="ALT DuPont",
        period_scope="comparable",
        depends_on_current=("net_deferred_tax_position",),
        depends_on_previous=("net_deferred_tax_position",),
        hints=(
            "Change in Net Deferred-Tax Asset Position = Current net − Prior net.",
            "Net-position change is a balance movement — not deferred-tax expense "
            "or cash taxes.",
        ),
    ),
)


def expand_deferred_tax_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    """Expand deferred-tax families into period-specific concrete specs."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in expand_deferred_tax_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_deferred_tax_specs requires strictly chronological "
                "(increasing) period dates"
            )

    specs: list[ComponentSpec] = []
    order = start_order
    for family in DEFERRED_TAX_COMPONENT_CATALOG:
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


GEOGRAPHIC_SHEET_NAME = "Geographic Segment Analysis"
GEOGRAPHIC_SEGMENT_IDENTITIES = ("americas", "china_mainland", "rest_of_world")
GEOGRAPHIC_SEGMENT_LABELS = {
    "americas": "Americas",
    "china_mainland": "China Mainland",
    "rest_of_world": "Rest of World",
}


def geographic_component_id(
    family_id: str,
    period: date,
    identity: str = "",
) -> str:
    stamp = period.strftime("%Y%m%d")
    if identity:
        return f"{family_id}__{identity}__{stamp}"
    return f"{family_id}__{stamp}"


def geographic_spec_identity(spec: ComponentSpec) -> str:
    parts = spec.id.split("__")
    if len(parts) == 2:
        return ""
    if len(parts) != 3:
        raise ValueError(f"malformed geographic spec id {spec.id!r}")
    return parts[1]


def geographic_identity_label(identity: str) -> str:
    if identity in GEOGRAPHIC_SEGMENT_LABELS:
        return GEOGRAPHIC_SEGMENT_LABELS[identity]
    local = identity.rsplit(".", 1)[-1]
    return local.replace("_", " ").title()


GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="geographic_revenue_share",
        order=152,
        title="Geographic revenue mix",
        short_hint=(
            "Revenue mix = segment net revenue / reported consolidated net "
            "revenue. Zero consolidated revenue is undefined (#N/A). This is "
            "mix arithmetic, not a causal explanation of growth or margins."
        ),
        semantic_key="geographic.revenue_share",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Revenue mix = segment net revenue / reported consolidated net revenue.",
            "Zero consolidated revenue yields the undefined-ratio result.",
            "Mix arithmetic only; not a causal explanation.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_revenue_growth",
        order=153,
        title="Geographic adjacent-period revenue growth",
        short_hint=(
            "Adjacent-period revenue growth = (current − prior) / prior using "
            "the immediately preceding model period. Opening growth is absent. "
            "A missing adjacent snapshot makes growth unavailable. Zero prior "
            "revenue is undefined (#N/A). Not a causal explanation."
        ),
        semantic_key="geographic.revenue_growth",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        hints=(
            "Adjacent-period growth uses the immediately preceding model period.",
            "Opening growth is absent; a gap is unavailable, not compressed.",
            "Zero prior revenue yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_reported_operating_margin",
        order=154,
        title="Geographic reported operating margin",
        short_hint=(
            "Reported operating margin = segment income from operations / "
            "segment net revenue. This is not BAV NOPAT margin. Zero revenue "
            "is undefined (#N/A). Negative profit is preserved."
        ),
        semantic_key="geographic.reported_operating_margin",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Reported operating margin = income from operations / net revenue.",
            "Keep this distinct from BAV NOPAT margin.",
            "Zero revenue yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_calculated_segment_revenue_total",
        order=155,
        title="Calculated geographic segment revenue total",
        short_hint=(
            "Calculated segment revenue total = Americas + China Mainland + "
            "Rest of World. Distinct from any reported segment_total."
        ),
        semantic_key="geographic.calculated_segment_revenue_total",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Sum the three reported geographic segment revenues.",
            "This calculated total is distinct from any reported segment_total.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_calculated_segment_operating_profit_total",
        order=156,
        title="Calculated geographic segment operating-profit total",
        short_hint=(
            "Calculated segment operating-profit total = Americas + China "
            "Mainland + Rest of World income from operations. Distinct from "
            "any reported segment_total."
        ),
        semantic_key="geographic.calculated_segment_operating_profit_total",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Sum the three reported geographic segment operating profits.",
            "This calculated total is distinct from any reported segment_total.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_signed_reconciling_contribution",
        order=157,
        title="Signed geographic reconciling contribution",
        short_hint=(
            "Apply the explicit ADD or SUBTRACT operation to the reported "
            "reconciling amount. ADD keeps the reported sign; SUBTRACT "
            "negates it. Corporate-column and itemized items are not combined. "
            "Arithmetic only; not a causal explanation."
        ),
        semantic_key="geographic.signed_reconciling_contribution",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "ADD uses the reported sign; SUBTRACT negates the reported amount.",
            "Do not combine corporate-column ADD with itemized SUBTRACT items.",
            "Bridge arithmetic only; not a causal explanation.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_reconstructed_consolidated_operating_profit",
        order=158,
        title="Reconstructed consolidated operating profit",
        short_hint=(
            "Reconstructed consolidated operating profit = calculated segment "
            "operating-profit total plus signed reconciling contributions in "
            "stable identity order. Distinct from reported consolidated "
            "operating profit until the difference is taken."
        ),
        semantic_key="geographic.reconstructed_consolidated_operating_profit",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        depends_on_current=(
            "geographic_calculated_segment_operating_profit_total",
            "geographic_signed_reconciling_contribution",
        ),
        hints=(
            "Add signed reconciling contributions to the calculated segment total.",
            "Preserve identity order and ADD/SUBTRACT semantics.",
            "This reconstructed amount is not automatically the reported total.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_consolidated_revenue_difference",
        order=159,
        title="Geographic consolidated revenue difference",
        short_hint=(
            "Difference = calculated segment revenue total − reported "
            "consolidated revenue. A nonzero difference needs further "
            "evidence; it is not a plug and does not invent missing zeros."
        ),
        semantic_key="geographic.consolidated_revenue_difference",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        depends_on_current=("geographic_calculated_segment_revenue_total",),
        hints=(
            "Difference = calculated segment revenue total − reported consolidated revenue.",
            "A nonzero difference needs further evidence; do not insert a plug.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_consolidated_operating_profit_difference",
        order=160,
        title="Geographic consolidated operating-profit difference",
        short_hint=(
            "Difference = reconstructed consolidated operating profit − "
            "reported consolidated operating profit. A nonzero difference "
            "needs further evidence; it is not a plug."
        ),
        semantic_key="geographic.consolidated_operating_profit_difference",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        depends_on_current=(
            "geographic_reconstructed_consolidated_operating_profit",
        ),
        hints=(
            "Difference = reconstructed operating profit − reported consolidated operating profit.",
            "A nonzero difference needs further evidence; do not insert a plug.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="geographic_revenue_growth_contribution",
        order=161,
        title="Geographic contribution to consolidated revenue growth",
        short_hint=(
            "Contribution in percentage points = 100 × (current segment net "
            "revenue − prior segment net revenue) / prior consolidated net "
            "revenue. Arithmetic decomposition of reported geographic revenue "
            "changes only. Opening contribution is absent. A missing adjacent "
            "snapshot is unavailable. Zero prior consolidated revenue is "
            "undefined (#N/A). Zero prior segment revenue does not suppress "
            "the contribution. Not organic growth, constant-currency growth, "
            "or a causal explanation."
        ),
        semantic_key="geographic.revenue_growth_contribution",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        hints=(
            "Contribution uses prior consolidated revenue, not the segment's own prior revenue.",
            "Opening contribution is absent; a gap is unavailable, not compressed.",
            "Percentage-point arithmetic only; not organic, constant-currency, or causal growth.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_consolidated_revenue_growth",
        order=162,
        title="Consolidated revenue growth",
        short_hint=(
            "Consolidated revenue growth = (current − prior) / prior using "
            "reported consolidated net revenue and the immediately preceding "
            "model period. Opening growth is absent. A missing adjacent "
            "snapshot makes growth unavailable. Zero prior consolidated "
            "revenue is undefined (#N/A). Not organic, constant-currency, "
            "or causal growth."
        ),
        semantic_key="geographic.consolidated_revenue_growth",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        hints=(
            "Adjacent consolidated growth uses the immediately preceding model period.",
            "Opening growth is absent; a gap is unavailable, not compressed.",
            "Zero prior consolidated revenue yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_revenue_growth_contribution_residual",
        order=163,
        title="Geographic contribution residual",
        short_hint=(
            "Residual in percentage points = 100 × consolidated revenue "
            "growth − sum of Americas, China Mainland, and Rest of World "
            "contributions. Preserve the signed residual; do not force it "
            "to zero or divide by the consolidated revenue change. Opening "
            "residual is absent. A missing adjacent snapshot is unavailable. "
            "Zero prior consolidated revenue is undefined (#N/A). Arithmetic "
            "reconciliation only, not a causal explanation."
        ),
        semantic_key="geographic.revenue_growth_contribution_residual",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            "geographic_consolidated_revenue_growth",
            "geographic_revenue_growth_contribution",
        ),
        hints=(
            "Residual = 100 × consolidated revenue growth − the three segment contributions.",
            "Keep the signed residual; do not force reconciliation to zero.",
            "Do not divide by the consolidated revenue change.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_operating_margin_contribution",
        order=164,
        title="Geographic contribution to consolidated operating margin",
        short_hint=(
            "Contribution in percentage points = 100 × segment income from "
            "operations / reported consolidated net revenue. Arithmetic "
            "decomposition of reported operating margin only. Zero "
            "consolidated revenue is undefined (#N/A). Zero segment revenue "
            "does not suppress a valid contribution. Distinct from BAV NOPAT "
            "margin. Not mix, within-segment, normalization, or causal "
            "attribution."
        ),
        semantic_key="geographic.operating_margin_contribution",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Use consolidated net revenue as the denominator, not segment revenue.",
            "Zero segment revenue does not suppress a valid contribution.",
            "Percentage-point arithmetic only; not mix, within-segment, or causal.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_reconciling_operating_margin_contribution",
        order=165,
        title="Aggregate reconciling contribution to consolidated operating margin",
        short_hint=(
            "Aggregate reconciling contribution in percentage points = 100 × "
            "the sum of existing signed reconciling amounts / reported "
            "consolidated net revenue. Reuse explicit ADD/SUBTRACT bridge "
            "operations without combining corporate-column and itemized "
            "identities. Arithmetic reconciliation of reported operating "
            "margin only. Zero consolidated revenue is undefined (#N/A). "
            "Not mix, within-segment, normalization, or causal attribution."
        ),
        semantic_key="geographic.reconciling_operating_margin_contribution",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        depends_on_current=("geographic_signed_reconciling_contribution",),
        hints=(
            "Sum signed reconciling amounts, then divide by consolidated net revenue.",
            "Keep corporate-column and itemized identities separate; do not double count.",
            "Aggregate reconciliation only; not item-level equivalence across families.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_consolidated_operating_margin",
        order=166,
        title="Consolidated reported operating margin",
        short_hint=(
            "Consolidated reported operating margin in percentage points = "
            "100 × reported consolidated income from operations / reported "
            "consolidated net revenue. Distinct from BAV NOPAT margin. Zero "
            "consolidated revenue is undefined (#N/A). Arithmetic only; not "
            "normalization or a causal explanation."
        ),
        semantic_key="geographic.consolidated_operating_margin",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        hints=(
            "Consolidated reported operating margin uses consolidated profit and revenue.",
            "Keep this distinct from BAV NOPAT margin.",
            "Zero consolidated revenue yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_operating_margin_contribution_residual",
        order=167,
        title="Operating-margin contribution residual",
        short_hint=(
            "Residual in percentage points = consolidated reported operating "
            "margin − sum of Americas, China Mainland, and Rest of World "
            "contributions − the aggregate reconciling contribution. Preserve "
            "the signed residual; do not force it to zero. A missing snapshot "
            "is unavailable. Zero consolidated revenue is undefined (#N/A). "
            "Arithmetic reconciliation only, not mix, within-segment, "
            "normalization, or a causal explanation."
        ),
        semantic_key="geographic.operating_margin_contribution_residual",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        depends_on_current=(
            "geographic_consolidated_operating_margin",
            "geographic_operating_margin_contribution",
            "geographic_reconciling_operating_margin_contribution",
        ),
        hints=(
            "Residual = consolidated reported operating margin − segment contributions − reconciling contribution.",
            "Keep the signed residual; do not force reconciliation to zero.",
            "Arithmetic only; not mix, within-segment, or causal attribution.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_operating_margin_contribution_change",
        order=168,
        title="Change in geographic contribution to consolidated operating margin",
        short_hint=(
            "Adjacent change in percentage points = current segment "
            "contribution − immediately preceding contribution. Opening "
            "change is absent. A missing adjacent snapshot is unavailable. "
            "Zero consolidated revenue is undefined (#N/A). Arithmetic "
            "decomposition of the change in reported operating margin only. "
            "Not mix, within-segment, normalization, or causal attribution."
        ),
        semantic_key="geographic.operating_margin_contribution_change",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=("geographic_operating_margin_contribution",),
        depends_on_previous=("geographic_operating_margin_contribution",),
        hints=(
            "Change uses the immediately preceding model period's contribution.",
            "Opening change is absent; a gap is unavailable, not compressed.",
            "Percentage-point arithmetic only; not mix, within-segment, or causal.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_reconciling_operating_margin_contribution_change",
        order=169,
        title="Change in aggregate reconciling contribution to consolidated operating margin",
        short_hint=(
            "Adjacent change in percentage points = current aggregate "
            "reconciling contribution − immediately preceding aggregate. "
            "Opening change is absent. A missing adjacent snapshot is "
            "unavailable. Zero consolidated revenue is undefined (#N/A). "
            "Compare aggregates only; do not assert item-level equivalence "
            "across presentation families. Arithmetic only; not mix, "
            "within-segment, normalization, or causal attribution."
        ),
        semantic_key="geographic.reconciling_operating_margin_contribution_change",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            "geographic_reconciling_operating_margin_contribution",
        ),
        depends_on_previous=(
            "geographic_reconciling_operating_margin_contribution",
        ),
        hints=(
            "Change the aggregate reconciling contribution, not item-level identities.",
            "Opening change is absent; a gap is unavailable, not compressed.",
            "Do not assert corporate-column and itemized items are equivalent.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_consolidated_operating_margin_change",
        order=170,
        title="Change in consolidated reported operating margin",
        short_hint=(
            "Adjacent change in percentage points = current consolidated "
            "reported operating margin − immediately preceding margin. "
            "Opening change is absent. A missing adjacent snapshot is "
            "unavailable. Zero consolidated revenue is undefined (#N/A). "
            "Arithmetic decomposition of reported operating-margin change "
            "only. Distinct from BAV NOPAT margin. Not mix, within-segment, "
            "normalization, or causal attribution."
        ),
        semantic_key="geographic.consolidated_operating_margin_change",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=("geographic_consolidated_operating_margin",),
        depends_on_previous=("geographic_consolidated_operating_margin",),
        hints=(
            "Change uses the immediately preceding consolidated reported operating margin.",
            "Opening change is absent; a gap is unavailable, not compressed.",
            "Keep this distinct from BAV NOPAT margin.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id="geographic_operating_margin_contribution_change_residual",
        order=171,
        title="Operating-margin contribution change residual",
        short_hint=(
            "Change residual in percentage points = change in consolidated "
            "reported operating margin − sum of segment contribution changes "
            "− change in the aggregate reconciling contribution. Preserve the "
            "signed residual; do not force it to zero. Opening residual is "
            "absent. A missing adjacent snapshot is unavailable. Zero "
            "consolidated revenue is undefined (#N/A). Arithmetic "
            "reconciliation of the change only, not mix, within-segment, "
            "normalization, or a causal explanation."
        ),
        semantic_key="geographic.operating_margin_contribution_change_residual",
        category="geographic_segment",
        tab_template=GEOGRAPHIC_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            "geographic_consolidated_operating_margin_change",
            "geographic_operating_margin_contribution_change",
            "geographic_reconciling_operating_margin_contribution_change",
        ),
        hints=(
            "Change residual = Δ consolidated margin − Σ Δ segment contributions − Δ reconciling contribution.",
            "Keep the signed residual; do not force reconciliation to zero.",
            "Arithmetic only; not mix, within-segment, or causal attribution.",
        ),
        tolerance=1e-12,
    ),
)


def expand_geographic_segment_specs(
    periods: list[date],
    *,
    start_order: int,
    available_periods: tuple[date, ...],
    growth_identities: dict[date, tuple[str, ...]],
    bridge_identities: dict[date, tuple[str, ...]],
    contribution_identities: dict[date, tuple[str, ...]] | None = None,
    consolidated_growth_periods: tuple[date, ...] | None = None,
    margin_change_periods: tuple[date, ...] | None = None,
) -> tuple[ComponentSpec, ...]:
    """Expand geographic families by segment/bridge identity and fiscal period."""
    if len(periods) != len(set(periods)):
        raise ValueError(
            "duplicate fiscal periods are not allowed in "
            "expand_geographic_segment_specs"
        )
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                "expand_geographic_segment_specs requires strictly chronological "
                "(increasing) period dates"
            )

    available = set(available_periods)
    families = {family.id: family for family in GEOGRAPHIC_SEGMENT_COMPONENT_CATALOG}
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}

    def _append(
        family: ComponentFamily,
        period: date,
        *,
        identity: str = "",
        depends_on: tuple[str, ...] = (),
        title: str | None = None,
        semantic_key: str | None = None,
    ) -> None:
        nonlocal order
        period_end = period.isoformat()
        specs.append(
            ComponentSpec(
                id=geographic_component_id(family.id, period, identity),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=title or family.title,
                short_hint=family.short_hint,
                semantic_key=semantic_key
                or (
                    f"{family.semantic_key}.{identity}.{period_end}"
                    if identity
                    else f"{family.semantic_key}.{period_end}"
                ),
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=depends_on,
                hints=family.hints,
                tolerance=family.tolerance,
            )
        )
        order += 1

    share = families["geographic_revenue_share"]
    growth = families["geographic_revenue_growth"]
    margin = families["geographic_reported_operating_margin"]
    rev_total = families["geographic_calculated_segment_revenue_total"]
    ifop_total = families["geographic_calculated_segment_operating_profit_total"]
    signed = families["geographic_signed_reconciling_contribution"]
    reconstructed = families["geographic_reconstructed_consolidated_operating_profit"]
    rev_diff = families["geographic_consolidated_revenue_difference"]
    ifop_diff = families["geographic_consolidated_operating_profit_difference"]
    contribution = families["geographic_revenue_growth_contribution"]
    cons_growth = families["geographic_consolidated_revenue_growth"]
    residual = families["geographic_revenue_growth_contribution_residual"]
    margin_contrib = families["geographic_operating_margin_contribution"]
    reconciling_margin = families[
        "geographic_reconciling_operating_margin_contribution"
    ]
    cons_margin = families["geographic_consolidated_operating_margin"]
    margin_residual = families["geographic_operating_margin_contribution_residual"]
    margin_contrib_change = families["geographic_operating_margin_contribution_change"]
    reconciling_margin_change = families[
        "geographic_reconciling_operating_margin_contribution_change"
    ]
    cons_margin_change = families["geographic_consolidated_operating_margin_change"]
    margin_change_residual = families[
        "geographic_operating_margin_contribution_change_residual"
    ]
    contribution_ids = contribution_identities or {}
    cons_growth_periods = set(consolidated_growth_periods or ())
    margin_change_set = set(margin_change_periods or ())

    for period in periods:
        if period not in available:
            continue
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            label = geographic_identity_label(identity)
            _append(
                share,
                period,
                identity=identity,
                title=f"{label} revenue mix",
            )
        growth_ids = growth_identities.get(period, ())
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            if identity not in growth_ids:
                continue
            label = geographic_identity_label(identity)
            _append(
                growth,
                period,
                identity=identity,
                title=f"{label} adjacent-period revenue growth",
            )
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            label = geographic_identity_label(identity)
            _append(
                margin,
                period,
                identity=identity,
                title=f"{label} reported operating margin",
            )
        _append(rev_total, period)
        _append(ifop_total, period)
        period_bridges = bridge_identities.get(period, ())
        for identity in period_bridges:
            _append(
                signed,
                period,
                identity=identity,
                title=(
                    f"{geographic_identity_label(identity)} signed reconciling "
                    "contribution"
                ),
            )
        reconstructed_deps = [
            geographic_component_id(ifop_total.id, period),
            *(
                geographic_component_id(signed.id, period, identity)
                for identity in period_bridges
            ),
        ]
        _append(
            reconstructed,
            period,
            depends_on=tuple(reconstructed_deps),
        )
        _append(
            rev_diff,
            period,
            depends_on=(geographic_component_id(rev_total.id, period),),
        )
        _append(
            ifop_diff,
            period,
            depends_on=(geographic_component_id(reconstructed.id, period),),
        )
        contrib_ids = contribution_ids.get(period, ())
        contrib_deps: list[str] = []
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            if identity not in contrib_ids:
                continue
            label = geographic_identity_label(identity)
            contrib_id = geographic_component_id(contribution.id, period, identity)
            contrib_deps.append(contrib_id)
            _append(
                contribution,
                period,
                identity=identity,
                title=(
                    f"{label} contribution to consolidated revenue growth "
                    "(percentage points)"
                ),
            )
        if period in cons_growth_periods:
            _append(
                cons_growth,
                period,
                title="Consolidated revenue growth",
            )
            residual_deps = [
                geographic_component_id(cons_growth.id, period),
                *contrib_deps,
            ]
            _append(
                residual,
                period,
                depends_on=tuple(residual_deps),
                title="Contribution residual (percentage points)",
            )
        margin_contrib_deps: list[str] = []
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            label = geographic_identity_label(identity)
            contrib_id = geographic_component_id(margin_contrib.id, period, identity)
            margin_contrib_deps.append(contrib_id)
            _append(
                margin_contrib,
                period,
                identity=identity,
                title=(
                    f"{label} contribution to consolidated operating margin "
                    "(percentage points)"
                ),
            )
        _append(
            reconciling_margin,
            period,
            depends_on=tuple(
                geographic_component_id(signed.id, period, identity)
                for identity in period_bridges
            ),
            title=(
                "Aggregate reconciling contribution to consolidated operating "
                "margin (percentage points)"
            ),
        )
        _append(
            cons_margin,
            period,
            title="Consolidated reported operating margin (percentage points)",
        )
        _append(
            margin_residual,
            period,
            depends_on=(
                geographic_component_id(cons_margin.id, period),
                *margin_contrib_deps,
                geographic_component_id(reconciling_margin.id, period),
            ),
            title="Operating-margin contribution residual (percentage points)",
        )
        if period not in margin_change_set:
            continue
        index = period_index[period]
        if index == 0:
            raise ValueError(
                "opening geographic period has no immediately preceding "
                "operating-margin contribution"
            )
        prior = periods[index - 1]
        change_deps: list[str] = []
        for identity in GEOGRAPHIC_SEGMENT_IDENTITIES:
            label = geographic_identity_label(identity)
            change_id = geographic_component_id(
                margin_contrib_change.id, period, identity
            )
            change_deps.append(change_id)
            _append(
                margin_contrib_change,
                period,
                identity=identity,
                depends_on=(
                    geographic_component_id(margin_contrib.id, period, identity),
                    geographic_component_id(margin_contrib.id, prior, identity),
                ),
                title=(
                    f"{label} change in contribution to consolidated operating "
                    "margin (percentage points)"
                ),
            )
        _append(
            reconciling_margin_change,
            period,
            depends_on=(
                geographic_component_id(reconciling_margin.id, period),
                geographic_component_id(reconciling_margin.id, prior),
            ),
            title=(
                "Change in aggregate reconciling contribution to consolidated "
                "operating margin (percentage points)"
            ),
        )
        _append(
            cons_margin_change,
            period,
            depends_on=(
                geographic_component_id(cons_margin.id, period),
                geographic_component_id(cons_margin.id, prior),
            ),
            title=(
                "Change in consolidated reported operating margin "
                "(percentage points)"
            ),
        )
        _append(
            margin_change_residual,
            period,
            depends_on=(
                geographic_component_id(cons_margin_change.id, period),
                *change_deps,
                geographic_component_id(reconciling_margin_change.id, period),
            ),
            title=(
                "Operating-margin contribution change residual "
                "(percentage points)"
            ),
        )
    return tuple(specs)


STORE_COUNT_SHEET_NAME = "Store Count Analysis"
STORE_COUNT_POPULATION_LABEL = "company-operated"
STORE_COUNT_SOURCE_FAMILY_ID = "store_count_source"
STORE_COUNT_SOURCE_CATEGORY = "store_count_source"
STORE_COUNT_PRACTICE_CATEGORY = "store_count"


def store_count_component_id(family_id: str, period: date) -> str:
    return f"{family_id}__{period.strftime('%Y%m%d')}"


def store_count_source_component_id(period: date) -> str:
    return store_count_component_id(STORE_COUNT_SOURCE_FAMILY_ID, period)


def store_count_source_semantic_key(period: date) -> str:
    return f"operating_kpi.store_count.source.{period.isoformat()}"


def is_store_count_source_identity(component: object) -> bool:
    return getattr(component, "category", None) == STORE_COUNT_SOURCE_CATEGORY


def is_store_count_practice_identity(component: object) -> bool:
    return getattr(component, "category", None) == STORE_COUNT_PRACTICE_CATEGORY


@dataclass(frozen=True)
class StoreCountSourceRef:
    """Mapped coordinate for one validated period-end store-count source."""

    id: str
    semantic_key: str
    period_end: str
    cell: str
    unit: str = ""
    population: str = STORE_COUNT_POPULATION_LABEL


def store_count_source_map_formula(value: float) -> str:
    """Semantic-map formula for a populated source; the worksheet keeps the number."""
    number = float(value)
    if number.is_integer():
        return f"={int(number)}"
    return f"={number}"


def resolve_store_count_net_change_formula(
    current: StoreCountSourceRef,
    prior: StoreCountSourceRef,
) -> str:
    """Net change from mapped current/prior source cells, not column adjacency."""
    if not current.cell or not prior.cell:
        raise ValueError(
            "store-count net change requires current and prior source cells"
        )
    return f"={current.cell}-{prior.cell}"


def resolve_store_count_growth_formula(
    current: StoreCountSourceRef,
    prior: StoreCountSourceRef,
) -> str:
    """Adjacent growth from mapped current/prior source cells; zero prior is #N/A."""
    if not current.cell or not prior.cell:
        raise ValueError(
            "store-count growth requires current and prior source cells"
        )
    return (
        f"=IF({prior.cell}=0,NA(),({current.cell}-{prior.cell})/{prior.cell})"
    )


STORE_COUNT_SOURCE_FAMILY = ComponentFamily(
    id=STORE_COUNT_SOURCE_FAMILY_ID,
    order=160,
    title="Company-operated period-end store count",
    short_hint=(
        "Populated company-operated period-end store count. This is a "
        "reported source, not a practice cell. Count units are independent "
        "of monetary scale."
    ),
    semantic_key="operating_kpi.store_count.source",
    category=STORE_COUNT_SOURCE_CATEGORY,
    tab_template=STORE_COUNT_SHEET_NAME,
    period_scope="all",
    hints=(
        f"Population is {STORE_COUNT_POPULATION_LABEL}.",
        "Count units stay independent of monetary scale.",
        "This source is populated and is not practiced or Checked.",
    ),
    tolerance=0.0,
)


STORE_COUNT_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="store_count_net_change",
        order=161,
        title="Store-count net change",
        short_hint=(
            "Net count change = current period-end company-operated store "
            "count − the immediately preceding period-end count. This is a "
            "net change, not gross openings or closures. Opening change is "
            "absent. A missing adjacent snapshot is unavailable. Not "
            "productivity, same-store sales, geographic allocation, or "
            "causality."
        ),
        semantic_key="operating_kpi.store_count.net_change",
        category=STORE_COUNT_PRACTICE_CATEGORY,
        tab_template=STORE_COUNT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(STORE_COUNT_SOURCE_FAMILY_ID,),
        depends_on_previous=(STORE_COUNT_SOURCE_FAMILY_ID,),
        hints=(
            "Net count change uses the immediately preceding model period.",
            "This is a net change, not gross openings or closures.",
            "Opening change is absent; a gap is unavailable, not compressed.",
        ),
        tolerance=0.0,
    ),
    ComponentFamily(
        id="store_count_growth",
        order=162,
        title="Store-count growth",
        short_hint=(
            "Store-count growth = (current − prior) / prior using the "
            "immediately preceding model period. Opening growth is absent. "
            "A missing adjacent snapshot is unavailable. Zero prior count is "
            "undefined (#N/A). Not productivity, same-store sales, "
            "geographic allocation, or causality."
        ),
        semantic_key="operating_kpi.store_count.growth",
        category=STORE_COUNT_PRACTICE_CATEGORY,
        tab_template=STORE_COUNT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(STORE_COUNT_SOURCE_FAMILY_ID,),
        depends_on_previous=(STORE_COUNT_SOURCE_FAMILY_ID,),
        hints=(
            "Adjacent-period growth uses the immediately preceding model period.",
            "Opening growth is absent; a gap is unavailable, not compressed.",
            "Zero prior count yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
)


def _require_store_count_period_axis(periods: list[date], *, caller: str) -> None:
    if len(periods) != len(set(periods)):
        raise ValueError(f"duplicate fiscal periods are not allowed in {caller}")
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                f"{caller} requires strictly chronological (increasing) period dates"
            )


def expand_store_count_source_specs(
    periods: list[date],
    *,
    start_order: int,
    source_periods: tuple[date, ...],
    units: dict[date, str] | None = None,
) -> tuple[ComponentSpec, ...]:
    """Register populated period-end count sources; never practice identities."""
    _require_store_count_period_axis(periods, caller="expand_store_count_source_specs")
    period_index = {period: index for index, period in enumerate(periods)}
    unknown = [period for period in source_periods if period not in period_index]
    if unknown:
        raise ValueError(
            "expand_store_count_source_specs received periods outside the "
            f"canonical axis: {unknown}"
        )
    if len(source_periods) != len(set(source_periods)):
        raise ValueError(
            "duplicate source periods are not allowed in expand_store_count_source_specs"
        )
    family = STORE_COUNT_SOURCE_FAMILY
    specs: list[ComponentSpec] = []
    order = start_order
    unit_map = units or {}
    for period in periods:
        if period not in source_periods:
            continue
        period_end = period.isoformat()
        unit = unit_map.get(period, "")
        hints = family.hints
        if unit:
            hints = family.hints + (f"Count unit: {unit}.",)
        specs.append(
            ComponentSpec(
                id=store_count_source_component_id(period),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=family.title,
                short_hint=family.short_hint,
                semantic_key=store_count_source_semantic_key(period),
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=(),
                hints=hints,
                tolerance=family.tolerance,
            )
        )
        order += 1
    return tuple(specs)


def store_count_adjacent_source_ids(
    periods: list[date],
    period: date,
) -> tuple[str, str]:
    """Current then immediately preceding canonical-period count source identities."""
    period_index = {item: index for index, item in enumerate(periods)}
    if period not in period_index:
        raise ValueError(
            f"store-count practice period {period.isoformat()} is outside the "
            "canonical axis"
        )
    index = period_index[period]
    if index == 0:
        raise ValueError(
            "opening store-count period has no immediately preceding source"
        )
    prior = periods[index - 1]
    return (
        store_count_source_component_id(period),
        store_count_source_component_id(prior),
    )


def expand_store_count_specs(
    periods: list[date],
    *,
    start_order: int,
    change_periods: tuple[date, ...],
    growth_periods: tuple[date, ...],
) -> tuple[ComponentSpec, ...]:
    """Expand store-count practice families for available adjacent periods."""
    _require_store_count_period_axis(periods, caller="expand_store_count_specs")

    families = {family.id: family for family in STORE_COUNT_COMPONENT_CATALOG}
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}
    change_set = set(change_periods)
    growth_set = set(growth_periods)

    def _append(family: ComponentFamily, period: date) -> None:
        nonlocal order
        period_end = period.isoformat()
        specs.append(
            ComponentSpec(
                id=store_count_component_id(family.id, period),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=family.title,
                short_hint=family.short_hint,
                semantic_key=f"{family.semantic_key}.{period_end}",
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=store_count_adjacent_source_ids(periods, period),
                hints=family.hints,
                tolerance=family.tolerance,
            )
        )
        order += 1

    change_family = families["store_count_net_change"]
    growth_family = families["store_count_growth"]
    for period in periods:
        if period in change_set:
            _append(change_family, period)
        if period in growth_set:
            _append(growth_family, period)
    return tuple(specs)


REVENUE_STORE_SOURCE_FAMILY_ID = "operating_kpi_revenue_source"
REVENUE_STORE_SOURCE_CATEGORY = "operating_kpi_revenue_source"
REVENUE_STORE_PRACTICE_CATEGORY = "operating_kpi_revenue_store"
REVENUE_STORE_GROWTH_FAMILY_ID = "operating_kpi_revenue_growth"
REVENUE_STORE_DIFFERENCE_FAMILY_ID = "operating_kpi_revenue_store_growth_difference"


def revenue_store_component_id(family_id: str, period: date) -> str:
    return store_count_component_id(family_id, period)


def revenue_store_source_component_id(period: date) -> str:
    return revenue_store_component_id(REVENUE_STORE_SOURCE_FAMILY_ID, period)


def revenue_store_source_semantic_key(period: date) -> str:
    return f"operating_kpi.revenue_store.source.{period.isoformat()}"


def is_revenue_store_source_identity(component: object) -> bool:
    return getattr(component, "category", None) == REVENUE_STORE_SOURCE_CATEGORY


def is_revenue_store_practice_identity(component: object) -> bool:
    return getattr(component, "category", None) == REVENUE_STORE_PRACTICE_CATEGORY


def is_sales_per_square_foot_source_identity(component: object) -> bool:
    return getattr(component, "category", None) == SALES_PER_SQUARE_FOOT_SOURCE_CATEGORY


def is_sales_per_square_foot_practice_identity(component: object) -> bool:
    return (
        getattr(component, "category", None) == SALES_PER_SQUARE_FOOT_PRACTICE_CATEGORY
    )


def is_operating_kpi_source_identity(component: object) -> bool:
    return (
        is_store_count_source_identity(component)
        or is_revenue_store_source_identity(component)
        or is_comparable_sales_source_identity(component)
        or is_sales_per_square_foot_source_identity(component)
    )


@dataclass(frozen=True)
class SemanticCellRef:
    """Mapped workbook cell for a semantically identified source or practice."""

    id: str
    semantic_key: str
    period_end: str
    cell: str
    tab: str = STORE_COUNT_SHEET_NAME


def semantic_formula_cell(ref: SemanticCellRef, *, from_tab: str) -> str:
    """A1 (or cross-sheet) reference from a mapped identity, never column adjacency."""
    if not ref.cell:
        raise ValueError("semantic formula cell requires a mapped coordinate")
    if ref.tab == from_tab:
        return ref.cell
    escaped = ref.tab.replace("'", "''")
    return f"'{escaped}'!{ref.cell}"


def resolve_geographic_revenue_growth_contribution_formula(
    current_segment: SemanticCellRef,
    prior_segment: SemanticCellRef,
    prior_consolidated: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point contribution from mapped current/prior revenue sources."""
    current_cell = semantic_formula_cell(current_segment, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior_segment, from_tab=from_tab)
    prior_cons = semantic_formula_cell(prior_consolidated, from_tab=from_tab)
    return (
        f"=IF({prior_cons}=0,NA(),100*({current_cell}-{prior_cell})/{prior_cons})"
    )


def resolve_geographic_consolidated_revenue_growth_formula(
    current_consolidated: SemanticCellRef,
    prior_consolidated: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Adjacent consolidated revenue growth from mapped current/prior sources."""
    current_cell = semantic_formula_cell(current_consolidated, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior_consolidated, from_tab=from_tab)
    return (
        f"=IF({prior_cell}=0,NA(),({current_cell}-{prior_cell})/{prior_cell})"
    )


def resolve_geographic_revenue_growth_contribution_residual_formula(
    consolidated_growth: SemanticCellRef,
    contributions: tuple[SemanticCellRef, ...],
    *,
    from_tab: str,
) -> str:
    """Signed residual from mapped consolidated growth and segment contributions."""
    if not contributions:
        raise ValueError("contribution residual requires mapped segment contributions")
    growth_cell = semantic_formula_cell(consolidated_growth, from_tab=from_tab)
    contrib_cells = [
        semantic_formula_cell(item, from_tab=from_tab) for item in contributions
    ]
    return "=100*" + growth_cell + "".join(f"-{cell}" for cell in contrib_cells)


def resolve_geographic_operating_margin_contribution_formula(
    operating_profit: SemanticCellRef,
    consolidated_revenue: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point operating-margin contribution from mapped profit and revenue."""
    profit_cell = semantic_formula_cell(operating_profit, from_tab=from_tab)
    cons_cell = semantic_formula_cell(consolidated_revenue, from_tab=from_tab)
    return f"=IF({cons_cell}=0,NA(),100*{profit_cell}/{cons_cell})"


def resolve_geographic_reconciling_operating_margin_contribution_formula(
    signed_reconciling: tuple[SemanticCellRef, ...],
    consolidated_revenue: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Aggregate reconciling contribution from mapped signed amounts and revenue."""
    cons_cell = semantic_formula_cell(consolidated_revenue, from_tab=from_tab)
    if not signed_reconciling:
        return f"=IF({cons_cell}=0,NA(),0)"
    signed_cells = [
        semantic_formula_cell(item, from_tab=from_tab) for item in signed_reconciling
    ]
    total = "+".join(signed_cells)
    return f"=IF({cons_cell}=0,NA(),100*({total})/{cons_cell})"


def resolve_geographic_consolidated_operating_margin_formula(
    consolidated_operating_profit: SemanticCellRef,
    consolidated_revenue: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point consolidated reported operating margin from mapped sources."""
    return resolve_geographic_operating_margin_contribution_formula(
        consolidated_operating_profit,
        consolidated_revenue,
        from_tab=from_tab,
    )


def resolve_geographic_operating_margin_contribution_residual_formula(
    consolidated_margin: SemanticCellRef,
    contributions: tuple[SemanticCellRef, ...],
    reconciling: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Signed residual from mapped margin, segment contributions, and reconciling."""
    if not contributions:
        raise ValueError(
            "operating-margin contribution residual requires mapped segment "
            "contributions"
        )
    margin_cell = semantic_formula_cell(consolidated_margin, from_tab=from_tab)
    contrib_cells = [
        semantic_formula_cell(item, from_tab=from_tab) for item in contributions
    ]
    reconciling_cell = semantic_formula_cell(reconciling, from_tab=from_tab)
    return (
        "="
        + margin_cell
        + "".join(f"-{cell}" for cell in contrib_cells)
        + f"-{reconciling_cell}"
    )


def resolve_geographic_adjacent_change_formula(
    current: SemanticCellRef,
    prior: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Adjacent percentage-point change from mapped current and prior cells."""
    current_cell = semantic_formula_cell(current, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior, from_tab=from_tab)
    return f"={current_cell}-{prior_cell}"


def resolve_geographic_operating_margin_contribution_change_residual_formula(
    margin_change: SemanticCellRef,
    contribution_changes: tuple[SemanticCellRef, ...],
    reconciling_change: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Signed change residual from mapped margin and contribution changes."""
    return resolve_geographic_operating_margin_contribution_residual_formula(
        margin_change,
        contribution_changes,
        reconciling_change,
        from_tab=from_tab,
    )


def resolve_revenue_store_growth_formula(
    current: SemanticCellRef,
    prior: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Adjacent revenue growth from mapped current/prior revenue source cells."""
    current_cell = semantic_formula_cell(current, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior, from_tab=from_tab)
    return (
        f"=IF({prior_cell}=0,NA(),({current_cell}-{prior_cell})/{prior_cell})"
    )


def resolve_revenue_store_difference_formula(
    revenue_growth: SemanticCellRef,
    store_growth: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point difference from mapped revenue-growth and store-growth cells."""
    revenue_cell = semantic_formula_cell(revenue_growth, from_tab=from_tab)
    store_cell = semantic_formula_cell(store_growth, from_tab=from_tab)
    return f"=100*({revenue_cell}-{store_cell})"


REVENUE_STORE_SOURCE_FAMILY = ComponentFamily(
    id=REVENUE_STORE_SOURCE_FAMILY_ID,
    order=163,
    title="Consolidated revenue",
    short_hint=(
        "Populated consolidated revenue from the income-statement source. "
        "This is a reported source, not a practice cell. Distinct from "
        "company-operated period-end store counts."
    ),
    semantic_key="operating_kpi.revenue_store.source",
    category=REVENUE_STORE_SOURCE_CATEGORY,
    tab_template=STORE_COUNT_SHEET_NAME,
    period_scope="all",
    hints=(
        "Consolidated revenue is a reported source, not a practice cell.",
        "Company-operated store counts remain a distinct input.",
        "This source is populated and is not practiced or Checked.",
    ),
    tolerance=0.0,
)


REVENUE_STORE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id=REVENUE_STORE_GROWTH_FAMILY_ID,
        order=164,
        title="Consolidated revenue growth",
        short_hint=(
            "Statement-derived consolidated revenue growth = (current − prior) "
            "/ prior using the immediately preceding model period. Opening "
            "growth is absent. A missing adjacent revenue input is unavailable. "
            "Zero prior revenue is undefined (#N/A). Not same-store sales, "
            "store productivity, organic growth, or causality."
        ),
        semantic_key="operating_kpi.revenue_store.revenue_growth",
        category=REVENUE_STORE_PRACTICE_CATEGORY,
        tab_template=STORE_COUNT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(REVENUE_STORE_SOURCE_FAMILY_ID,),
        depends_on_previous=(REVENUE_STORE_SOURCE_FAMILY_ID,),
        hints=(
            "Adjacent-period revenue growth uses the immediately preceding model period.",
            "Opening growth is absent; a gap is unavailable, not compressed.",
            "Zero prior revenue yields the undefined-ratio result.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id=REVENUE_STORE_DIFFERENCE_FAMILY_ID,
        order=165,
        title="Revenue vs store-count growth difference",
        short_hint=(
            "Analyst-derived difference in percentage points = 100 × "
            "(consolidated revenue growth − company-operated store-count "
            "growth). Opening difference is absent. A missing growth input "
            "is unavailable and takes precedence over an undefined ratio. "
            "Not revenue attribution, same-store sales, productivity, "
            "organic growth, or causal evidence."
        ),
        semantic_key="operating_kpi.revenue_store.growth_difference_pp",
        category=REVENUE_STORE_PRACTICE_CATEGORY,
        tab_template=STORE_COUNT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            REVENUE_STORE_GROWTH_FAMILY_ID,
            "store_count_growth",
        ),
        hints=(
            "The difference uses the same-period revenue-growth and store-count-growth cells.",
            "Opening difference is absent; a missing input is unavailable, not compressed.",
            "The inputs have distinct scopes and do not imply causality.",
        ),
        tolerance=1e-12,
    ),
)


def expand_revenue_store_source_specs(
    periods: list[date],
    *,
    start_order: int,
    source_periods: tuple[date, ...],
) -> tuple[ComponentSpec, ...]:
    """Register populated consolidated-revenue sources; never practice identities."""
    _require_store_count_period_axis(periods, caller="expand_revenue_store_source_specs")
    period_index = {period: index for index, period in enumerate(periods)}
    unknown = [period for period in source_periods if period not in period_index]
    if unknown:
        raise ValueError(
            "expand_revenue_store_source_specs received periods outside the "
            f"canonical axis: {unknown}"
        )
    if len(source_periods) != len(set(source_periods)):
        raise ValueError(
            "duplicate source periods are not allowed in expand_revenue_store_source_specs"
        )
    family = REVENUE_STORE_SOURCE_FAMILY
    specs: list[ComponentSpec] = []
    order = start_order
    for period in periods:
        if period not in source_periods:
            continue
        period_end = period.isoformat()
        specs.append(
            ComponentSpec(
                id=revenue_store_source_component_id(period),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=family.title,
                short_hint=family.short_hint,
                semantic_key=revenue_store_source_semantic_key(period),
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=(),
                hints=family.hints,
                tolerance=family.tolerance,
            )
        )
        order += 1
    return tuple(specs)


def revenue_store_adjacent_source_ids(
    periods: list[date],
    period: date,
) -> tuple[str, str]:
    """Current then immediately preceding canonical-period revenue source identities."""
    period_index = {item: index for index, item in enumerate(periods)}
    if period not in period_index:
        raise ValueError(
            f"revenue/store practice period {period.isoformat()} is outside the "
            "canonical axis"
        )
    index = period_index[period]
    if index == 0:
        raise ValueError(
            "opening revenue/store period has no immediately preceding source"
        )
    prior = periods[index - 1]
    return (
        revenue_store_source_component_id(period),
        revenue_store_source_component_id(prior),
    )


def revenue_store_difference_dependency_ids(period: date) -> tuple[str, str]:
    """Same-period revenue-growth then store-count-growth practice identities."""
    return (
        revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, period),
        store_count_component_id("store_count_growth", period),
    )


def expand_revenue_store_specs(
    periods: list[date],
    *,
    start_order: int,
    growth_periods: tuple[date, ...],
    difference_periods: tuple[date, ...],
) -> tuple[ComponentSpec, ...]:
    """Expand revenue/store-growth practice families for available adjacent periods."""
    _require_store_count_period_axis(periods, caller="expand_revenue_store_specs")

    families = {family.id: family for family in REVENUE_STORE_COMPONENT_CATALOG}
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}
    growth_set = set(growth_periods)
    difference_set = set(difference_periods)

    def _append(
        family: ComponentFamily,
        period: date,
        depends_on: tuple[str, ...],
    ) -> None:
        nonlocal order
        period_end = period.isoformat()
        specs.append(
            ComponentSpec(
                id=revenue_store_component_id(family.id, period),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=family.title,
                short_hint=family.short_hint,
                semantic_key=f"{family.semantic_key}.{period_end}",
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=depends_on,
                hints=family.hints,
                tolerance=family.tolerance,
            )
        )
        order += 1

    growth_family = families[REVENUE_STORE_GROWTH_FAMILY_ID]
    difference_family = families[REVENUE_STORE_DIFFERENCE_FAMILY_ID]
    for period in periods:
        if period in growth_set:
            _append(
                growth_family,
                period,
                revenue_store_adjacent_source_ids(periods, period),
            )
        if period in difference_set:
            _append(
                difference_family,
                period,
                revenue_store_difference_dependency_ids(period),
            )
    return tuple(specs)


COMPARABLE_SALES_SHEET_NAME = "Comparable Sales Analysis"
COMPARABLE_SALES_SOURCE_FAMILY_ID = "operating_kpi_comparable_sales_source"
COMPARABLE_SALES_SOURCE_CATEGORY = "operating_kpi_comparable_sales_source"
COMPARABLE_SALES_PRACTICE_CATEGORY = "operating_kpi_comparable_sales"
COMPARABLE_SALES_DIFFERENCE_FAMILY_ID = (
    "operating_kpi_revenue_comparable_sales_difference"
)
COMPARABLE_SALES_CHANGE_FAMILY_ID = (
    "operating_kpi_comparable_sales_adjacent_change"
)
COMPARABLE_SALES_PCT_FORMAT = '0.00"%"'
SALES_PER_SQUARE_FOOT_SHEET_NAME = "Sales per Square Foot Analysis"
SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID = (
    "operating_kpi_sales_per_square_foot_source"
)
SALES_PER_SQUARE_FOOT_SOURCE_CATEGORY = (
    "operating_kpi_sales_per_square_foot_source"
)
SALES_PER_SQUARE_FOOT_PRACTICE_CATEGORY = (
    "operating_kpi_sales_per_square_foot"
)
SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID = (
    "operating_kpi_sales_per_square_foot_change"
)
SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID = (
    "operating_kpi_sales_per_square_foot_growth"
)
SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID = (
    "operating_kpi_revenue_sales_per_square_foot_difference"
)


def comparable_sales_identity_token(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def comparable_sales_component_id(
    family_id: str, period: date, identity: str
) -> str:
    return (
        f"{family_id}__{comparable_sales_identity_token(identity)}__"
        f"{period.strftime('%Y%m%d')}"
    )


def comparable_sales_source_component_id(period: date, identity: str) -> str:
    return comparable_sales_component_id(
        COMPARABLE_SALES_SOURCE_FAMILY_ID, period, identity
    )


def comparable_sales_source_semantic_key(period: date, identity: str) -> str:
    token = comparable_sales_identity_token(identity)
    return f"operating_kpi.comparable_sales.source.{token}.{period.isoformat()}"


def operating_kpi_spec_identity(spec: object) -> str:
    component_id = getattr(spec, "id", "")
    parts = str(component_id).split("__")
    if len(parts) == 2:
        return ""
    if len(parts) != 3:
        raise ValueError(f"malformed operating KPI spec id {component_id!r}")
    return parts[1]


def comparable_sales_identity_from_component(
    component: object, identities: tuple[str, ...]
) -> str:
    token = operating_kpi_spec_identity(component)
    matches = [
        identity
        for identity in identities
        if comparable_sales_identity_token(identity) == token
    ]
    if len(matches) != 1:
        raise ValueError(
            "operating KPI comparable-sales identity token "
            f"{token!r} is not unique"
        )
    return matches[0]


def is_comparable_sales_source_identity(component: object) -> bool:
    return getattr(component, "category", None) == COMPARABLE_SALES_SOURCE_CATEGORY


def is_comparable_sales_practice_identity(component: object) -> bool:
    return getattr(component, "category", None) == COMPARABLE_SALES_PRACTICE_CATEGORY


def resolve_revenue_comparable_sales_difference_formula(
    revenue_growth: SemanticCellRef,
    comparable_sales: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point difference from mapped growth and reported compsales cells."""
    revenue_cell = semantic_formula_cell(revenue_growth, from_tab=from_tab)
    compsales_cell = semantic_formula_cell(comparable_sales, from_tab=from_tab)
    return f"=100*{revenue_cell}-{compsales_cell}"


def comparable_sales_identity_label(
    *,
    entity_ticker: str,
    entity_company: str,
    geography: str,
    population: str,
    unit: str,
    basis: str,
    comparison: str,
) -> str:
    return (
        f"{entity_ticker} · {entity_company} · {geography} · {population} · "
        f"{unit} · {basis} · {comparison}"
    )


COMPARABLE_SALES_SOURCE_FAMILY = ComponentFamily(
    id=COMPARABLE_SALES_SOURCE_FAMILY_ID,
    order=166,
    title="Reported comparable-sales growth",
    short_hint=(
        "Populated reported global comparable-sales growth in percent units. "
        "This is a reported source, not a practice cell. Distinct from "
        "statement-derived consolidated revenue growth. A value of 2 means 2%."
    ),
    semantic_key="operating_kpi.comparable_sales.source",
    category=COMPARABLE_SALES_SOURCE_CATEGORY,
    tab_template=COMPARABLE_SALES_SHEET_NAME,
    period_scope="all",
    hints=(
        "Reported comparable-sales growth is a reported source, not a practice cell.",
        "The API unit is percent: 2 means 2%, not a 2.00 ratio.",
        "Identities stay isolated; they are not merged, averaged, or selected.",
        "This source is populated and is not practiced or Checked.",
    ),
    tolerance=0.0,
)


COMPARABLE_SALES_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id=COMPARABLE_SALES_DIFFERENCE_FAMILY_ID,
        order=167,
        title="Revenue vs comparable-sales growth difference",
        short_hint=(
            "Analyst-derived difference in percentage points = 100 × "
            "statement-derived consolidated revenue growth − the current "
            "reported comparable-sales percent. Opening difference is absent. "
            "A missing growth or current comparable-sales input is unavailable "
            "and takes precedence over an undefined ratio. Not growth of "
            "growth, adjacent percentage-point change, new-store contribution, "
            "revenue attribution, organic growth, productivity, or causality."
        ),
        semantic_key="operating_kpi.comparable_sales.growth_difference_pp",
        category=COMPARABLE_SALES_PRACTICE_CATEGORY,
        tab_template=COMPARABLE_SALES_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            REVENUE_STORE_GROWTH_FAMILY_ID,
            COMPARABLE_SALES_SOURCE_FAMILY_ID,
        ),
        hints=(
            "The difference uses the same-period revenue-growth cell and the "
            "current reported comparable-sales source.",
            "Opening difference is absent; a missing input is unavailable, not compressed.",
            "A missing prior comparable-sales observation does not suppress a current comparison.",
            "The inputs have distinct scopes and do not imply causality.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id=COMPARABLE_SALES_CHANGE_FAMILY_ID,
        order=168,
        title="Comparable-sales adjacent change",
        short_hint=(
            "Analyst-derived adjacent change in percentage points = current "
            "reported comparable-sales percent minus the immediately prior "
            "reported percent. This is not growth of growth, revenue "
            "attribution, or causality. Opening change is absent. A missing "
            "or semantically incompatible adjacent observation is unavailable."
        ),
        semantic_key="operating_kpi.comparable_sales.adjacent_change_pp",
        category=COMPARABLE_SALES_PRACTICE_CATEGORY,
        tab_template=COMPARABLE_SALES_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(COMPARABLE_SALES_SOURCE_FAMILY_ID,),
        depends_on_previous=(COMPARABLE_SALES_SOURCE_FAMILY_ID,),
        hints=(
            "Adjacent change uses the mapped current and immediately prior "
            "reported comparable-sales source cells.",
            "The result is in percentage points: 7 minus 2 is 5, not 2.5.",
            "Opening change is absent; a canonical gap or semantic discontinuity "
            "is unavailable and is not practiced.",
            "Reported values remain populated across discontinuities.",
        ),
        tolerance=1e-12,
    ),
)


def _require_comparable_sales_period_axis(periods: list[date], *, caller: str) -> None:
    if len(periods) != len(set(periods)):
        raise ValueError(f"duplicate fiscal periods are not allowed in {caller}")
    for previous, current in zip(periods, periods[1:]):
        if not (current > previous):
            raise ValueError(
                f"{caller} requires strictly chronological (increasing) period dates"
            )


def expand_comparable_sales_source_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    source_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Register populated reported comparable-sales sources; never practice identities."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_comparable_sales_source_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in expand_comparable_sales_source_specs"
        )
    period_index = {period: index for index, period in enumerate(periods)}
    family = COMPARABLE_SALES_SOURCE_FAMILY
    specs: list[ComponentSpec] = []
    order = start_order
    for identity in identities:
        source_periods = source_periods_by_identity.get(identity, ())
        unknown = [period for period in source_periods if period not in period_index]
        if unknown:
            raise ValueError(
                "expand_comparable_sales_source_specs received periods outside "
                f"the canonical axis: {unknown}"
            )
        if len(source_periods) != len(set(source_periods)):
            raise ValueError(
                "duplicate source periods are not allowed in "
                "expand_comparable_sales_source_specs"
            )
        for period in periods:
            if period not in source_periods:
                continue
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=comparable_sales_source_component_id(period, identity),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=comparable_sales_source_semantic_key(
                        period, identity
                    ),
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=period_index[period],
                    period_end=period_end,
                    depends_on=(),
                    hints=family.hints + (f"Management identity: {identity}.",),
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


def comparable_sales_difference_dependency_ids(
    period: date, identity: str
) -> tuple[str, str]:
    """Same-period revenue-growth then current reported comparable-sales source."""
    return (
        revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, period),
        comparable_sales_source_component_id(period, identity),
    )


def expand_comparable_sales_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    difference_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Expand comparable-sales difference practice families by isolated identity."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_comparable_sales_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in expand_comparable_sales_specs"
        )

    family = {item.id: item for item in COMPARABLE_SALES_COMPONENT_CATALOG}[
        COMPARABLE_SALES_DIFFERENCE_FAMILY_ID
    ]
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}
    for identity in identities:
        difference_periods = difference_periods_by_identity.get(identity, ())
        unknown = [
            period for period in difference_periods if period not in period_index
        ]
        if unknown:
            raise ValueError(
                "expand_comparable_sales_specs received periods outside the "
                f"canonical axis: {unknown}"
            )
        token = comparable_sales_identity_token(identity)
        for period in periods:
            if period not in difference_periods:
                continue
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=comparable_sales_component_id(family.id, period, identity),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=(
                        f"{family.semantic_key}.{token}.{period_end}"
                    ),
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=period_index[period],
                    period_end=period_end,
                    depends_on=comparable_sales_difference_dependency_ids(
                        period, identity
                    ),
                    hints=family.hints + (f"Management identity: {identity}.",),
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


def resolve_management_kpi_adjacent_change_formula(
    current: SemanticCellRef,
    prior: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Adjacent change from mapped current/prior reported source cells."""
    current_cell = semantic_formula_cell(current, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior, from_tab=from_tab)
    return f"={current_cell}-{prior_cell}"


def resolve_management_kpi_growth_formula(
    current: SemanticCellRef,
    prior: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Adjacent fractional growth from mapped current/prior reported source cells."""
    current_cell = semantic_formula_cell(current, from_tab=from_tab)
    prior_cell = semantic_formula_cell(prior, from_tab=from_tab)
    return (
        f"=IF({prior_cell}=0,NA(),({current_cell}-{prior_cell})/{prior_cell})"
    )


def comparable_sales_change_dependency_ids(
    periods: list[date], period: date, identity: str
) -> tuple[str, str]:
    """Current then immediately preceding comparable-sales source identities."""
    period_index = {item: index for index, item in enumerate(periods)}
    if period not in period_index:
        raise ValueError(
            f"comparable-sales change period {period.isoformat()} is outside "
            "the canonical axis"
        )
    index = period_index[period]
    if index == 0:
        raise ValueError(
            "opening comparable-sales period has no immediately preceding source"
        )
    prior = periods[index - 1]
    return (
        comparable_sales_source_component_id(period, identity),
        comparable_sales_source_component_id(prior, identity),
    )


def expand_comparable_sales_change_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    change_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Expand comparable-sales adjacent-change practice by isolated identity."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_comparable_sales_change_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in "
            "expand_comparable_sales_change_specs"
        )
    family = {item.id: item for item in COMPARABLE_SALES_COMPONENT_CATALOG}[
        COMPARABLE_SALES_CHANGE_FAMILY_ID
    ]
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}
    for identity in identities:
        change_periods = change_periods_by_identity.get(identity, ())
        unknown = [period for period in change_periods if period not in period_index]
        if unknown:
            raise ValueError(
                "expand_comparable_sales_change_specs received periods outside "
                f"the canonical axis: {unknown}"
            )
        if len(change_periods) != len(set(change_periods)):
            raise ValueError(
                "duplicate change periods are not allowed in "
                "expand_comparable_sales_change_specs"
            )
        token = comparable_sales_identity_token(identity)
        for period in periods:
            if period not in change_periods:
                continue
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=comparable_sales_component_id(family.id, period, identity),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{token}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=period_index[period],
                    period_end=period_end,
                    depends_on=comparable_sales_change_dependency_ids(
                        periods, period, identity
                    ),
                    hints=family.hints + (f"Management identity: {identity}.",),
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


def sales_per_square_foot_source_component_id(period: date, identity: str) -> str:
    return comparable_sales_component_id(
        SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID, period, identity
    )


def sales_per_square_foot_source_semantic_key(period: date, identity: str) -> str:
    token = comparable_sales_identity_token(identity)
    return (
        "operating_kpi.sales_per_square_foot.source."
        f"{token}.{period.isoformat()}"
    )


def sales_per_square_foot_adjacent_source_ids(
    periods: list[date], period: date, identity: str
) -> tuple[str, str]:
    """Current then immediately preceding sales-per-square-foot source identities."""
    period_index = {item: index for index, item in enumerate(periods)}
    if period not in period_index:
        raise ValueError(
            f"sales-per-square-foot practice period {period.isoformat()} is "
            "outside the canonical axis"
        )
    index = period_index[period]
    if index == 0:
        raise ValueError(
            "opening sales-per-square-foot period has no immediately preceding source"
        )
    prior = periods[index - 1]
    return (
        sales_per_square_foot_source_component_id(period, identity),
        sales_per_square_foot_source_component_id(prior, identity),
    )


SALES_PER_SQUARE_FOOT_SOURCE_FAMILY = ComponentFamily(
    id=SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID,
    order=169,
    title="Reported sales per square foot",
    short_hint=(
        "Populated reported sales per square foot in USD_per_square_foot. "
        "This is a reported source, not a practice cell. Financial-statement "
        "monetary scaling is not applied."
    ),
    semantic_key="operating_kpi.sales_per_square_foot.source",
    category=SALES_PER_SQUARE_FOOT_SOURCE_CATEGORY,
    tab_template=SALES_PER_SQUARE_FOOT_SHEET_NAME,
    period_scope="all",
    hints=(
        "Reported sales per square foot is a reported source, not a practice cell.",
        "The API unit is USD_per_square_foot and is not scaled to statement units.",
        "Identities stay isolated; they are not merged, averaged, or selected.",
        "This source is populated and is not practiced or Checked.",
    ),
    tolerance=0.0,
)


SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id=SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID,
        order=170,
        title="Sales-per-square-foot adjacent change",
        short_hint=(
            "Analyst-derived adjacent absolute change = current reported "
            "sales per square foot minus the immediately prior reported "
            "value. Opening change is absent. A missing or semantically "
            "incompatible adjacent observation is unavailable."
        ),
        semantic_key="operating_kpi.sales_per_square_foot.adjacent_change",
        category=SALES_PER_SQUARE_FOOT_PRACTICE_CATEGORY,
        tab_template=SALES_PER_SQUARE_FOOT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID,),
        depends_on_previous=(SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID,),
        hints=(
            "Adjacent change uses the mapped current and immediately prior "
            "reported sales-per-square-foot source cells.",
            "The unit remains USD_per_square_foot; statement monetary scaling "
            "is not applied.",
            "Opening change is absent; a canonical gap or semantic discontinuity "
            "is unavailable and is not practiced.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id=SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        order=171,
        title="Sales-per-square-foot growth",
        short_hint=(
            "Analyst-derived adjacent fractional growth = (current - prior) / "
            "prior from reported sales-per-square-foot sources. A zero prior "
            "is undefined. Opening growth is absent. A missing or semantically "
            "incompatible adjacent observation is unavailable."
        ),
        semantic_key="operating_kpi.sales_per_square_foot.growth",
        category=SALES_PER_SQUARE_FOOT_PRACTICE_CATEGORY,
        tab_template=SALES_PER_SQUARE_FOOT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID,),
        depends_on_previous=(SALES_PER_SQUARE_FOOT_SOURCE_FAMILY_ID,),
        hints=(
            "Growth uses the mapped current and immediately prior reported "
            "sales-per-square-foot source cells.",
            "A zero prior is undefined and uses NA().",
            "Opening growth is absent; a missing input is unavailable, not compressed.",
        ),
        tolerance=1e-12,
    ),
    ComponentFamily(
        id=SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID,
        order=172,
        title="Revenue vs sales-per-square-foot growth difference",
        short_hint=(
            "Analyst-derived difference in percentage points = 100 × "
            "(statement-derived consolidated revenue growth − disclosed "
            "sales-per-square-foot growth). Opening difference is absent. "
            "A missing growth input is unavailable and takes precedence over "
            "an undefined ratio. Consolidated revenue and the disclosed SPSF "
            "population have different scopes. Not revenue attribution, "
            "selling-area growth, or causality."
        ),
        semantic_key="operating_kpi.sales_per_square_foot.growth_difference_pp",
        category=SALES_PER_SQUARE_FOOT_PRACTICE_CATEGORY,
        tab_template=SALES_PER_SQUARE_FOOT_SHEET_NAME,
        period_scope="comparable",
        depends_on_current=(
            REVENUE_STORE_GROWTH_FAMILY_ID,
            SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID,
        ),
        hints=(
            "The difference uses the same-period revenue-growth and "
            "sales-per-square-foot-growth cells.",
            "Opening difference is absent; a missing or semantically "
            "unavailable input is not practiced.",
            "A zero prior remains undefined and stays practiced.",
            "The inputs have distinct scopes and do not imply causality.",
        ),
        tolerance=1e-12,
    ),
)


def expand_sales_per_square_foot_source_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    source_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Register populated reported sales-per-square-foot sources; never practice."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_sales_per_square_foot_source_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in "
            "expand_sales_per_square_foot_source_specs"
        )
    period_index = {period: index for index, period in enumerate(periods)}
    family = SALES_PER_SQUARE_FOOT_SOURCE_FAMILY
    specs: list[ComponentSpec] = []
    order = start_order
    for identity in identities:
        source_periods = source_periods_by_identity.get(identity, ())
        unknown = [period for period in source_periods if period not in period_index]
        if unknown:
            raise ValueError(
                "expand_sales_per_square_foot_source_specs received periods "
                f"outside the canonical axis: {unknown}"
            )
        if len(source_periods) != len(set(source_periods)):
            raise ValueError(
                "duplicate source periods are not allowed in "
                "expand_sales_per_square_foot_source_specs"
            )
        for period in periods:
            if period not in source_periods:
                continue
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=sales_per_square_foot_source_component_id(period, identity),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=sales_per_square_foot_source_semantic_key(
                        period, identity
                    ),
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=period_index[period],
                    period_end=period_end,
                    depends_on=(),
                    hints=family.hints + (f"Management identity: {identity}.",),
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


def expand_sales_per_square_foot_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    change_periods_by_identity: dict[str, tuple[date, ...]],
    growth_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Expand sales-per-square-foot change and growth practice by identity."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_sales_per_square_foot_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in expand_sales_per_square_foot_specs"
        )
    families = {item.id: item for item in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG}
    change_family = families[SALES_PER_SQUARE_FOOT_CHANGE_FAMILY_ID]
    growth_family = families[SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID]
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}

    def _append(family: ComponentFamily, period: date, identity: str) -> None:
        nonlocal order
        unknown_family_periods = [
            item
            for item in (period,)
            if item not in period_index
        ]
        if unknown_family_periods:
            raise ValueError(
                "expand_sales_per_square_foot_specs received periods outside "
                f"the canonical axis: {unknown_family_periods}"
            )
        token = comparable_sales_identity_token(identity)
        period_end = period.isoformat()
        specs.append(
            ComponentSpec(
                id=comparable_sales_component_id(family.id, period, identity),
                family_id=family.id,
                order=order,
                family_order=family.order,
                title=family.title,
                short_hint=family.short_hint,
                semantic_key=f"{family.semantic_key}.{token}.{period_end}",
                category=family.category,
                tab_template=family.tab_template,
                period_index=period_index[period],
                period_end=period_end,
                depends_on=sales_per_square_foot_adjacent_source_ids(
                    periods, period, identity
                ),
                hints=family.hints + (f"Management identity: {identity}.",),
                tolerance=family.tolerance,
            )
        )
        order += 1

    for identity in identities:
        change_periods = change_periods_by_identity.get(identity, ())
        growth_periods = growth_periods_by_identity.get(identity, ())
        for collection, label in (
            (change_periods, "change"),
            (growth_periods, "growth"),
        ):
            unknown = [period for period in collection if period not in period_index]
            if unknown:
                raise ValueError(
                    "expand_sales_per_square_foot_specs received periods outside "
                    f"the canonical axis: {unknown}"
                )
            if len(collection) != len(set(collection)):
                raise ValueError(
                    f"duplicate {label} periods are not allowed in "
                    "expand_sales_per_square_foot_specs"
                )
        for period in periods:
            if period in change_periods:
                _append(change_family, period, identity)
            if period in growth_periods:
                _append(growth_family, period, identity)
    return tuple(specs)


def sales_per_square_foot_difference_dependency_ids(
    period: date, identity: str
) -> tuple[str, str]:
    """Same-period revenue-growth then SPSF-growth practice identities."""
    return (
        revenue_store_component_id(REVENUE_STORE_GROWTH_FAMILY_ID, period),
        comparable_sales_component_id(
            SALES_PER_SQUARE_FOOT_GROWTH_FAMILY_ID, period, identity
        ),
    )


def resolve_revenue_sales_per_square_foot_difference_formula(
    revenue_growth: SemanticCellRef,
    spsf_growth: SemanticCellRef,
    *,
    from_tab: str,
) -> str:
    """Percentage-point difference from mapped revenue-growth and SPSF-growth cells."""
    return resolve_revenue_store_difference_formula(
        revenue_growth, spsf_growth, from_tab=from_tab
    )


def expand_sales_per_square_foot_difference_specs(
    periods: list[date],
    *,
    start_order: int,
    identities: tuple[str, ...],
    difference_periods_by_identity: dict[str, tuple[date, ...]],
) -> tuple[ComponentSpec, ...]:
    """Expand SPSF revenue-growth comparison practice by isolated identity."""
    _require_comparable_sales_period_axis(
        periods, caller="expand_sales_per_square_foot_difference_specs"
    )
    if len(identities) != len(set(identities)):
        raise ValueError(
            "duplicate identities are not allowed in "
            "expand_sales_per_square_foot_difference_specs"
        )
    family = {item.id: item for item in SALES_PER_SQUARE_FOOT_COMPONENT_CATALOG}[
        SALES_PER_SQUARE_FOOT_DIFFERENCE_FAMILY_ID
    ]
    specs: list[ComponentSpec] = []
    order = start_order
    period_index = {period: index for index, period in enumerate(periods)}
    for identity in identities:
        difference_periods = difference_periods_by_identity.get(identity, ())
        unknown = [
            period for period in difference_periods if period not in period_index
        ]
        if unknown:
            raise ValueError(
                "expand_sales_per_square_foot_difference_specs received periods "
                f"outside the canonical axis: {unknown}"
            )
        if len(difference_periods) != len(set(difference_periods)):
            raise ValueError(
                "duplicate difference periods are not allowed in "
                "expand_sales_per_square_foot_difference_specs"
            )
        token = comparable_sales_identity_token(identity)
        for period in periods:
            if period not in difference_periods:
                continue
            period_end = period.isoformat()
            specs.append(
                ComponentSpec(
                    id=comparable_sales_component_id(family.id, period, identity),
                    family_id=family.id,
                    order=order,
                    family_order=family.order,
                    title=family.title,
                    short_hint=family.short_hint,
                    semantic_key=f"{family.semantic_key}.{token}.{period_end}",
                    category=family.category,
                    tab_template=family.tab_template,
                    period_index=period_index[period],
                    period_end=period_end,
                    depends_on=sales_per_square_foot_difference_dependency_ids(
                        period, identity
                    ),
                    hints=family.hints + (f"Management identity: {identity}.",),
                    tolerance=family.tolerance,
                )
            )
            order += 1
    return tuple(specs)


