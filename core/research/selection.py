"""Compact question-centered Driver selection.

Investigation, qualification and selection precede prose or figures.
Production logic consumes evidence generically; it does not branch on
company name or slug or emit fixture conclusions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


PUBLICATION_MAIN = "main_body"
PUBLICATION_APPENDIX = "appendix"
PUBLICATION_RETAINED = "retained"
PUBLICATION_EXCLUDED = "excluded"

CLAIM_IDENTITY = "accounting_identity"
CLAIM_REPORTED = "reported_fact"
CLAIM_PROXY = "proxy"
CLAIM_LOCALIZATION = "geographic_localization"
CLAIM_ASSOCIATION = "historical_association"
CLAIM_ATTRIBUTION = "management_attribution"
CLAIM_INFERENCE = "system_inference"
CLAIM_INTERPRETATION = "supported_interpretation"
CLAIM_UNRESOLVED = "unresolved_material_question"


@dataclass(frozen=True)
class ResearchClaim:
    identifier: str
    wording: str
    claim_type: str
    measurement_role: str
    evidence_refs: tuple[str, ...]
    transformation: str
    qualifiers: tuple[str, ...]
    dependencies: tuple[str, ...]
    mechanism_support: str
    counterevidence: str
    status: str


@dataclass(frozen=True)
class ResearchQuestion:
    identifier: str
    question: str
    entity: str
    population: str
    periods: tuple[str, ...]
    outcome: str
    materiality_rationale: str
    temporal_character: str
    magnitude: str
    mechanisms: tuple[str, ...]
    alternative: str
    discriminating_evidence: str
    claims: tuple[ResearchClaim, ...]
    strongest_conclusion: str
    unresolved_requirement: str
    reopening_condition: str
    publication: str
    publication_reason: str
    overlap: tuple[str, ...] = ()
    figure_purpose: str | None = None
    figure_question: str | None = None
    main_body_table_reason: str | None = None


@dataclass(frozen=True)
class SelectionDecision:
    identifier: str
    action: str
    reason: str


@dataclass(frozen=True)
class ResearchSelection:
    questions: tuple[ResearchQuestion, ...]
    decisions: tuple[SelectionDecision, ...]
    main_body_ids: tuple[str, ...]
    figure_ids: tuple[str, ...]
    main_body_table_reasons: tuple[str, ...] = ()

    def question(self, identifier: str) -> ResearchQuestion | None:
        for item in self.questions:
            if item.identifier == identifier:
                return item
        return None

    def selected(self, identifier: str) -> bool:
        return identifier in self.main_body_ids


def _present(value) -> bool:
    return value is not None and not isinstance(value, str)


def _latest_index(view) -> int | None:
    for index in range(len(view.periods) - 1, -1, -1):
        return index
    return None


def _label(view, index: int) -> str:
    return view.labels[index]


def _period_labels(view, indexes: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(_label(view, index) for index in indexes if 0 <= index < len(view.labels))


def investigate_driver_questions(view) -> tuple[ResearchQuestion, ...]:
    """Build candidate questions from available verified series only."""
    latest = _latest_index(view)
    if latest is None:
        return ()
    questions: list[ResearchQuestion] = []
    questions.extend(_growth_questions(view, latest))
    questions.extend(_geography_questions(view, latest))
    questions.extend(_margin_questions(view, latest))
    questions.extend(_cash_questions(view, latest))
    return tuple(questions)


def _growth_questions(view, latest: int) -> list[ResearchQuestion]:
    questions: list[ResearchQuestion] = []
    rev_g = view.revenue_growth[latest] if latest < len(view.revenue_growth) else None
    store_g = view.store_growth[latest] if latest < len(view.store_growth) else None
    intensity = None
    if latest > 0 and latest < len(view.revenue_per_store):
        prior = view.revenue_per_store[latest - 1]
        current = view.revenue_per_store[latest]
        if _present(prior) and _present(current) and prior:
            intensity = current / prior - 1.0
    store_term = (
        None
        if view.footprint_store_effect is None
        else view.footprint_store_effect[latest]
    )
    if _present(rev_g) and _present(store_g):
        diverged = store_g > rev_g
        questions.append(
            ResearchQuestion(
                identifier="footprint_intensity",
                question=(
                    "Whether continued store expansion is accompanied by stronger "
                    "company-wide revenue generation"
                ),
                entity=view.display_name,
                population="company-operated stores and consolidated revenue",
                periods=_period_labels(view, (latest - 1, latest) if latest else (latest,)),
                outcome="consolidated revenue versus store-count growth",
                materiality_rationale=(
                    "Continuing footprint investment coinciding with slower company "
                    "revenue growth changes the expansion-economics question."
                    if diverged
                    else "Store-count and revenue growth are both observed and remain eligible."
                ),
                temporal_character=(
                    "latest-year divergence; persistence is indeterminate"
                    if diverged
                    else "latest-year comparison; persistence is indeterminate"
                ),
                magnitude=(
                    f"store-count growth {store_g:.4%} versus revenue growth {rev_g:.4%}"
                    + (
                        f"; company-wide revenue per store {intensity:.4%}"
                        if intensity is not None
                        else ""
                    )
                ),
                mechanisms=(
                    "weaker demand",
                    "slower maturation of added capacity",
                    "channel mix",
                    "unequal-week comparison",
                ),
                alternative=(
                    "Opening dates, regional mix, digital revenue and calendar length "
                    "can produce the same divergence without weaker store productivity."
                ),
                discriminating_evidence=(
                    "Compatible store-only revenue, intra-year exposure, cohort "
                    "maturation, space and channel evidence."
                ),
                claims=(
                    ResearchClaim(
                        identifier="store_count_growth",
                        wording="Period-end company-operated store count changed as reported.",
                        claim_type=CLAIM_REPORTED,
                        measurement_role="operating KPI",
                        evidence_refs=("operating_kpi.period_end_count",),
                        transformation="adjacent growth of period-end count",
                        qualifiers=("period-end count is not average operating exposure",),
                        dependencies=("store_count",),
                        mechanism_support="none; count is an activity observation",
                        counterevidence="",
                        status="supported",
                    ),
                    ResearchClaim(
                        identifier="revenue_store_intensity",
                        wording=(
                            "Company-wide revenue per period-end store is a derived "
                            "intensity proxy, not store productivity."
                        ),
                        claim_type=CLAIM_PROXY,
                        measurement_role="proxy",
                        evidence_refs=("revenue_per_store.period_end_revenue_per_store",),
                        transformation="consolidated revenue / period-end store count",
                        qualifiers=(
                            "includes non-store revenue",
                            "period-end denominator",
                        ),
                        dependencies=("revenue", "store_count"),
                        mechanism_support="not established",
                        counterevidence="digital and other channels contribute to the numerator",
                        status="supported",
                    ),
                    ResearchClaim(
                        identifier="store_count_term",
                        wording=(
                            "The store-count term in the footprint identity is an "
                            "arithmetic allocation, not measured new-store revenue."
                        ),
                        claim_type=CLAIM_IDENTITY,
                        measurement_role="mathematical decomposition",
                        evidence_refs=("revenue_driver.footprint_identity",),
                        transformation="prior intensity × store-count change",
                        qualifiers=("allocation convention is not unique",),
                        dependencies=("revenue", "store_count"),
                        mechanism_support="identity only; exact reconstruction is not causation",
                        counterevidence="",
                        status="supported" if _present(store_term) else "unavailable",
                    ),
                ),
                strongest_conclusion=(
                    "Footprint grew faster than total-company revenue, warranting "
                    "investigation of expansion economics."
                    if diverged
                    else "Store-count and revenue growth are both observed on their stated bases."
                ),
                unresolved_requirement=(
                    "Store-only revenue, exposure through the year, cohort "
                    "maturation, space and channel evidence."
                ),
                reopening_condition=(
                    "A compatible store-only revenue series or intra-year exposure "
                    "measure becomes available."
                ),
                publication=PUBLICATION_MAIN if diverged else PUBLICATION_APPENDIX,
                publication_reason=(
                    "Latest-year growth/intensity divergence is a material selected claim."
                    if diverged
                    else "The comparison is available but does not currently change the argument."
                ),
                overlap=("comparable_sales",),
                figure_purpose="growth" if diverged else None,
                figure_question=(
                    "Did store-count growth outpace consolidated revenue growth?"
                    if diverged
                    else None
                ),
            )
        )
    compsales = tuple(view.comparable_sales)
    populations = {point.population for point in compsales}
    bases = {point.basis for point in compsales}
    compatible = len(populations) <= 1 and len(bases) <= 1 and view.fifty_three_week_period is None
    if compsales:
        latest_comp = next(
            (point for point in reversed(compsales) if point.period == view.periods[latest]),
            compsales[-1],
        )
        questions.append(
            ResearchQuestion(
                identifier="comparable_sales",
                question="How much the existing business supports growth on its stated basis",
                entity=view.display_name,
                population=latest_comp.population,
                periods=tuple(
                    view.labels[view.periods.index(point.period)]
                    for point in compsales
                    if point.period in view.periods
                ),
                outcome="reported comparable sales",
                materiality_rationale=(
                    "Positive comparable sales on the latest stated basis qualify "
                    "the expansion discussion; they do not measure contribution "
                    "to consolidated growth."
                ),
                temporal_character="period-specific reported KPI; not a continuous series",
                magnitude=f"{latest_comp.percent:.0f}% on the latest stated population and basis",
                mechanisms=("price", "units", "channel mix", "measured-population change"),
                alternative=(
                    "Price, units, mix and population changes can produce the same "
                    "reported comparable-sales observation."
                ),
                discriminating_evidence=(
                    "Documented equivalent populations and calendars, revenue weights, "
                    "and evidence separating price and volume."
                ),
                claims=(
                    ResearchClaim(
                        identifier="compsales_period",
                        wording=(
                            "Each period's selected comparable-sales observation is "
                            "positive on its stated basis."
                        ),
                        claim_type=CLAIM_REPORTED,
                        measurement_role="operating KPI",
                        evidence_refs=("management_kpi.comparable_sales_growth",),
                        transformation="reported percent; no cross-period join",
                        qualifiers=(
                            "definitions and comparison windows differ",
                            "53-week years are not equal-week measures",
                        ),
                        dependencies=("comparable_sales_population", "calendar_basis"),
                        mechanism_support="none",
                        counterevidence=(
                            ""
                            if compatible
                            else "Changing channel definitions and calendars block a continuous trend."
                        ),
                        status="supported",
                    ),
                    ResearchClaim(
                        identifier="compsales_trend",
                        wording="A continuous deceleration claim across all observations is not supported.",
                        claim_type=CLAIM_UNRESOLVED,
                        measurement_role="rejected comparison",
                        evidence_refs=("management_kpi.comparable_sales_growth",),
                        transformation="blocked join of incompatible observations",
                        qualifiers=("definition", "calendar", "population"),
                        dependencies=("comparable_sales_population", "calendar_basis"),
                        mechanism_support="not available",
                        counterevidence="incompatible series",
                        status="blocked" if not compatible else "unsupported",
                    ),
                ),
                strongest_conclusion=(
                    "The latest comparable-sales observation is positive on its "
                    "stated basis and cannot be joined to earlier observations "
                    "as one trend."
                ),
                unresolved_requirement=(
                    "Equivalent populations, calendars and revenue weights before "
                    "any contribution or trend claim."
                ),
                reopening_condition=(
                    "Comparable-sales observations share population, "
                    "definition and calendar."
                ),
                publication=PUBLICATION_MAIN,
                publication_reason=(
                    "Combined with footprint evidence to qualify growth; not a "
                    "separate argument or figure."
                ),
                overlap=("footprint_intensity",),
            )
        )
    questions.append(
        ResearchQuestion(
            identifier="sales_per_square_foot",
            question="Whether space productivity can be measured from available SPSF disclosures",
            entity=view.display_name,
            population="company-operated stores",
            periods=(),
            outcome="sales per square foot",
            materiality_rationale=(
                "A productivity reading would change expansion economics, but "
                "available SPSF observations are definition- and calendar-incompatible."
            ),
            temporal_character="incompatible historical observations",
            magnitude="unavailable as a comparable series",
            mechanisms=(),
            alternative="Company-wide revenue per store remains an intensity proxy only.",
            discriminating_evidence="Aligned SPSF definitions, calendars and store-only revenue.",
            claims=(
                ResearchClaim(
                    identifier="spsf_blocked",
                    wording="Sales per square foot cannot support a productivity reading.",
                    claim_type=CLAIM_UNRESOLVED,
                    measurement_role="rejected comparison",
                    evidence_refs=("management_kpi.sales_per_square_foot",),
                    transformation="blocked",
                    qualifiers=("definition disagreement", "calendar misalignment"),
                    dependencies=("spsf_definition", "spsf_calendar"),
                    mechanism_support="not available",
                    counterevidence="filings disagree on definition and later years do not line up",
                    status="blocked",
                ),
            ),
            strongest_conclusion="No productivity series is available on a comparable basis.",
            unresolved_requirement="Compatible SPSF observations and store-only revenue.",
            reopening_condition="SPSF observations share definition and calendar.",
            publication=PUBLICATION_EXCLUDED,
            publication_reason=(
                "The blocked comparison adds no argument value beyond the "
                "already-selected intensity-proxy boundary."
            ),
        )
    )
    return questions


def _geography_questions(view, latest: int) -> list[ResearchQuestion]:
    contrib = view.geo_contributions[latest] if latest < len(view.geo_contributions) else {}
    amounts = (
        view.geo_contribution_amounts[latest]
        if view.geo_contribution_amounts and latest < len(view.geo_contribution_amounts)
        else {}
    )
    profit = (
        view.geo_profit_changes[latest]
        if view.geo_profit_changes and latest < len(view.geo_profit_changes)
        else {}
    )
    reconciling = (
        None
        if view.geo_reconciling_profit_change is None
        or latest >= len(view.geo_reconciling_profit_change)
        else view.geo_reconciling_profit_change[latest]
    )
    consolidated_profit = (
        None
        if view.geo_consolidated_profit_change is None
        or latest >= len(view.geo_consolidated_profit_change)
        else view.geo_consolidated_profit_change[latest]
    )
    if not any(_present(value) for value in contrib.values()) and not any(
        _present(value) for value in profit.values()
    ):
        return []
    intl_rev = 0.0
    am_rev = amounts.get("americas") if amounts else None
    for identity in ("china_mainland", "rest_of_world"):
        value = amounts.get(identity) if amounts else None
        if _present(value):
            intl_rev += value
    am_profit = profit.get("americas")
    intl_profit = 0.0
    for identity in ("china_mainland", "rest_of_world"):
        value = profit.get(identity)
        if _present(value):
            intl_profit += value
    offset = (
        _present(am_rev)
        and am_rev < 0
        and intl_rev > abs(am_rev)
        and _present(am_profit)
        and _present(consolidated_profit)
        and consolidated_profit < 0
    )
    return [
        ResearchQuestion(
            identifier="geographic_localization",
            question=(
                "Whether international growth offsets weaker Americas performance "
                "at both the revenue and profit levels"
            ),
            entity=view.display_name,
            population="reported geographic segments plus corporate/unallocated items",
            periods=_period_labels(view, (latest - 1, latest) if latest else (latest,)),
            outcome="consolidated revenue and operating profit",
            materiality_rationale=(
                "The location of dependence changed: international revenue offset "
                "did not prevent consolidated profit deterioration."
                if offset
                else "Geographic contributions localize where revenue and profit changed."
            ),
            temporal_character="latest adjacent year; persistence is not established",
            magnitude=(
                f"consolidated operating-profit change {consolidated_profit}"
                if _present(consolidated_profit)
                else "geographic revenue contributions available"
            ),
            mechanisms=(
                "lower Americas demand",
                "cost pressure",
                "currency",
                "product or channel mix",
                "calendar",
                "cost allocation",
            ),
            alternative=(
                "Currency, mix, calendar effects and cost allocation can produce "
                "the same geographic pattern without identifying a regional mechanism."
            ),
            discriminating_evidence=(
                "Compatible regional price/volume, currency and cost evidence."
            ),
            claims=(
                ResearchClaim(
                    identifier="geo_revenue_localization",
                    wording="Reported geographic revenue changes localize where growth occurred.",
                    claim_type=CLAIM_LOCALIZATION,
                    measurement_role="segment localization",
                    evidence_refs=("geographic_segment.revenue_growth_contribution",),
                    transformation="arithmetic split of reported-currency revenue change",
                    qualifiers=(
                        "not organic growth",
                        "not constant-currency",
                        "not a cause",
                    ),
                    dependencies=("historical_segment.net_revenue",),
                    mechanism_support="none; localization is not attribution",
                    counterevidence="",
                    status="supported",
                ),
                ResearchClaim(
                    identifier="geo_profit_localization",
                    wording=(
                        "Reported geographic operating-profit changes, including "
                        "corporate/unallocated items, localize the profit movement."
                    ),
                    claim_type=CLAIM_LOCALIZATION,
                    measurement_role="segment localization",
                    evidence_refs=(
                        "geographic_segment.operating_profit_amount_change",
                        "geographic_segment.reconciling_operating_profit_amount_change",
                    ),
                    transformation="adjacent amount change; reconciling items retained",
                    qualifiers=("not a standalone return", "not a combination-benefit claim"),
                    dependencies=("historical_segment.income_from_operations",),
                    mechanism_support="none",
                    counterevidence="",
                    status="supported" if _present(consolidated_profit) else "unavailable",
                ),
            ),
            strongest_conclusion=(
                "International revenue offset was insufficient to offset the "
                "Americas profit decline and higher corporate/unallocated burden."
                if offset
                else "Geographic evidence localizes revenue and profit changes without identifying causes."
            ),
            unresolved_requirement=(
                "Regional price/volume, currency and cost evidence before any "
                "organic-growth or mechanism claim."
            ),
            reopening_condition=(
                "Compatible regional volume, currency and allocated-cost series appear."
            ),
            publication=PUBLICATION_MAIN if offset or _present(consolidated_profit) else PUBLICATION_APPENDIX,
            publication_reason=(
                "Aligned revenue/profit contrast adds distinct information about "
                "where growth and profit changed."
            ),
            figure_purpose="geography" if offset or _present(consolidated_profit) else None,
            figure_question=(
                "Did international revenue growth offset Americas profit deterioration, "
                "including corporate/unallocated items?"
            ),
        )
    ]


def _margin_questions(view, latest: int) -> list[ResearchQuestion]:
    om = (
        None
        if view.reported_operating_margin_change is None
        else view.reported_operating_margin_change[latest]
    )
    gm = (
        None
        if view.gross_margin_contribution is None
        else view.gross_margin_contribution[latest]
    )
    sga = (
        None
        if view.sga_ratio_contribution is None
        or latest >= len(view.sga_ratio_contribution)
        else view.sga_ratio_contribution[latest]
    )
    if not _present(om) and not _present(gm):
        return []
    attributions = tuple(view.attributions)
    latest_period = view.periods[latest]
    latest_attr = tuple(item for item in attributions if item.period == latest_period)
    questions = [
        ResearchQuestion(
            identifier="operating_margin_bridge",
            question="Which accounting movements explain the latest operating-margin change",
            entity=view.display_name,
            population="consolidated income statement",
            periods=_period_labels(view, (latest - 1, latest) if latest else (latest,)),
            outcome="reported operating margin",
            materiality_rationale=(
                "The latest operating-margin movement is material to the "
                "consolidated operating-profit change."
            ),
            temporal_character=(
                "latest-year accounting identity; earlier recovery includes "
                "disappearing episodic charges"
            ),
            magnitude=(
                f"operating-margin change {om:.4%}"
                if _present(om)
                else "component contributions available"
            ),
            mechanisms=(
                "lower pricing realization",
                "higher merchandise or distribution costs",
                "reduced cost absorption",
                "mix",
            ),
            alternative=(
                "Cost pressure and mix changes are credible alternatives; the "
                "decomposition cannot identify their separate effects."
            ),
            discriminating_evidence=(
                "Economic quantities linked to the relevant cost or revenue base; "
                "no residual renamed as mix or execution."
            ),
            claims=(
                ResearchClaim(
                    identifier="margin_identity",
                    wording=(
                        "Gross-margin and SG&A-ratio movements account for the "
                        "reported operating-margin change as an identity."
                    ),
                    claim_type=CLAIM_IDENTITY,
                    measurement_role="accounting identity",
                    evidence_refs=("reported_margin.contribution",),
                    transformation="signed unrounded ratio contributions",
                    qualifiers=("identity is not a mechanism",),
                    dependencies=("gross_margin", "sga", "impairment", "other_operating_items"),
                    mechanism_support="none",
                    counterevidence="",
                    status="supported",
                ),
            ),
            strongest_conclusion=(
                "Gross-margin contraction and a higher SG&A ratio account for "
                "nearly all the reported operating-margin decline."
                if _present(om) and om < 0
                else "The latest operating-margin change is reconstructed from disclosed components."
            ),
            unresolved_requirement=(
                "Evidence linking specific economic quantities to the relevant "
                "cost or revenue base."
            ),
            reopening_condition=(
                "A disclosed subcomponent series isolates tariff, markdown, mix "
                "or absorption effects."
            ),
            publication=PUBLICATION_MAIN,
            publication_reason="The latest-year accounting bridge is a selected claim.",
            overlap=("management_margin_attribution",),
            figure_purpose="margin",
            figure_question="Which accounting components reconstruct the latest operating-margin change?",
        )
    ]
    if latest_attr:
        quantified = tuple(item for item in latest_attr if item.approximate_amount is not None)
        questions.append(
            ResearchQuestion(
                identifier="management_margin_attribution",
                question="Whether available management explanation resolves the margin mechanism",
                entity=view.display_name,
                population="management commentary on gross profit and margins",
                periods=tuple(view.labels[view.periods.index(item.period)] for item in latest_attr if item.period in view.periods),
                outcome="gross profit and operating margin",
                materiality_rationale=(
                    "A quantified attribution is material relative to the profit "
                    "movement, but it remains management's counterfactual estimate."
                    if quantified
                    else "Management attributes the latest-year margin movement; the mechanism is unresolved."
                ),
                temporal_character="episodic attributed commentary for the latest year",
                magnitude=(
                    f"approximately {quantified[0].approximate_amount}"
                    if quantified
                    else "qualitative attribution only"
                ),
                mechanisms=tuple(item.theme for item in latest_attr),
                alternative=(
                    "Demand-related markdowns, product mix, offsetting measures "
                    "and overlapping cost effects could alter the interpretation."
                ),
                discriminating_evidence=(
                    "The counterfactual, timing, overlap, offsets and corroborating "
                    "operational evidence."
                ),
                claims=(
                    ResearchClaim(
                        identifier="attributed_gross_profit_pressure",
                        wording="Management's attributed explanation is preserved with its locator and scope.",
                        claim_type=CLAIM_ATTRIBUTION,
                        measurement_role="management attribution",
                        evidence_refs=tuple(
                            f"{item.source_file}:{item.page_reference}" for item in latest_attr
                        ),
                        transformation="source-bound disclosure; not a reconstructed bridge term",
                        qualifiers=(
                            "not independently verified",
                            "counterfactual scope",
                            "outside the accounting bridge",
                        ),
                        dependencies=tuple(item.source_file for item in latest_attr),
                        mechanism_support="not independently established",
                        counterevidence=(
                            "Year-on-year gross-profit change need not equal the "
                            "attributed counterfactual reduction."
                        ),
                        status="supported_as_attribution",
                    ),
                ),
                strongest_conclusion=(
                    "Management attributes latest-year pressure; the attribution "
                    "is documented and the mechanism remains independently unresolved."
                ),
                unresolved_requirement=(
                    "Counterfactual construction, timing, overlap, offsets and "
                    "corroborating operational evidence."
                ),
                reopening_condition=(
                    "An independently reconstructed causal series appears for the "
                    "attributed items."
                ),
                publication=PUBLICATION_MAIN,
                publication_reason=(
                    "Combined with the accounting margin finding; no additional figure."
                ),
                overlap=("operating_margin_bridge",),
            )
        )
    else:
        questions.append(
            ResearchQuestion(
                identifier="management_margin_attribution",
                question="Whether a source-bound management explanation of the margin movement is available",
                entity=view.display_name,
                population="management commentary",
                periods=_period_labels(view, (latest,)),
                outcome="gross profit and operating margin",
                materiality_rationale="An unresolved mechanism can remain consequential without a point estimate.",
                temporal_character="unavailable for the latest year",
                magnitude="unavailable",
                mechanisms=(),
                alternative="The accounting identity stands without a mechanism.",
                discriminating_evidence="A source-bound attribution with period, scope and locator.",
                claims=(),
                strongest_conclusion="No source-bound management attribution is available.",
                unresolved_requirement="Attributed commentary with locator and stated scope.",
                reopening_condition="A management attribution disclosure is available for the latest period.",
                publication=PUBLICATION_EXCLUDED,
                publication_reason="Absent attribution is a research limitation, not a published finding.",
            )
        )
    return questions


def _cash_questions(view, latest: int) -> list[ResearchQuestion]:
    cfo = None if view.cfo is None or latest >= len(view.cfo) else view.cfo[latest]
    ni = None if view.net_income is None or latest >= len(view.net_income) else view.net_income[latest]
    cfo_change = (
        None
        if view.cfo_change is None or latest >= len(view.cfo_change)
        else view.cfo_change[latest]
    )
    ni_change = (
        None
        if view.net_income_change is None or latest >= len(view.net_income_change)
        else view.net_income_change[latest]
    )
    remainder = (
        None
        if view.cfo_unexplained is None or latest >= len(view.cfo_unexplained)
        else view.cfo_unexplained[latest]
    )
    inventory = (
        None
        if view.inventory is None or latest >= len(view.inventory)
        else view.inventory[latest]
    )
    if not _present(cfo) or not _present(ni):
        return []
    weaker = _present(cfo_change) and _present(ni_change) and cfo_change < ni_change
    return [
        ResearchQuestion(
            identifier="cash_conversion",
            question=(
                "Whether reported earnings continue to translate into cash and "
                "whether working-capital behavior explains the change"
            ),
            entity=view.display_name,
            population="consolidated cash flow and income statement",
            periods=_period_labels(view, (latest - 1, latest) if latest else (latest,)),
            outcome="operating cash flow versus net income",
            materiality_rationale=(
                "The cash movement is material and larger than the earnings movement."
                if weaker
                else "CFO and net income are both observed and remain eligible."
            ),
            temporal_character="latest adjacent year; not a manipulation finding",
            magnitude=(
                f"CFO change {cfo_change}; net-income change {ni_change}"
                if _present(cfo_change) and _present(ni_change)
                else f"CFO {cfo}; net income {ni}"
            ),
            mechanisms=(
                "inventory accumulation",
                "growth preparation",
                "sourcing timing",
                "currency",
                "tax movements",
                "other settlement timing",
            ),
            alternative=(
                "Inventory, tax timing and other settlement items compete with a "
                "weak-demand explanation; the available CFO components need not "
                "explain the whole movement."
            ),
            discriminating_evidence=(
                "Missing reconciliation basis, inventory composition and turnover, "
                "tax timing and, if seasonality is asserted, intra-year observations."
            ),
            claims=(
                ResearchClaim(
                    identifier="cfo_versus_ni",
                    wording="Reported CFO and net income are compared as diagnostics, not as an earnings-quality judgment.",
                    claim_type=CLAIM_REPORTED,
                    measurement_role="derived diagnostic",
                    evidence_refs=("earnings_quality.operating_cash_flow", "net_income"),
                    transformation="adjacent change and CFO/net income",
                    qualifiers=("not manipulation", "not a complete explanation"),
                    dependencies=("operating_cash_flow", "net_income"),
                    mechanism_support="none",
                    counterevidence="",
                    status="supported",
                ),
                ResearchClaim(
                    identifier="cfo_remainder",
                    wording="An incomplete CFO reconciliation retains its signed unexplained remainder.",
                    claim_type=CLAIM_UNRESOLVED,
                    measurement_role="signed residual",
                    evidence_refs=("cash_flow.operating_components",),
                    transformation="reported CFO change minus summed adjacent operating-component changes",
                    qualifiers=("omitted disclosure is not a zero",),
                    dependencies=("cash_flow.component_lines",),
                    mechanism_support="not assigned",
                    counterevidence="",
                    status="supported" if _present(remainder) else "unavailable",
                ),
                ResearchClaim(
                    identifier="inventory_observation",
                    wording="Balance-sheet inventory change is observed and is not substituted for the cash-flow inventory line.",
                    claim_type=CLAIM_REPORTED,
                    measurement_role="reported fact",
                    evidence_refs=("inventory_analysis.inventories",),
                    transformation="adjacent balance-sheet change",
                    qualifiers=("not automatically a cash-flow reconciliation",),
                    dependencies=("inventories",),
                    mechanism_support="not established",
                    counterevidence="",
                    status="supported" if _present(inventory) else "unavailable",
                ),
            ),
            strongest_conclusion=(
                "Cash conversion weakened relative to earnings; the inventory "
                "question is open and the CFO remainder remains unexplained."
                if weaker
                else "CFO and net income are both observed on their stated bases."
            ),
            unresolved_requirement=(
                "The missing reconciliation basis, inventory composition and "
                "turnover evidence, and tax timing."
            ),
            reopening_condition=(
                "A complete CFO bridge or intra-year inventory observations appear."
            ),
            publication=PUBLICATION_MAIN if weaker or _present(cfo_change) else PUBLICATION_APPENDIX,
            publication_reason=(
                "Cash conversion adds a distinct perspective from growth and margin."
            ),
            figure_purpose="cash" if weaker or _present(cfo) else None,
            figure_question="Did reported earnings continue to translate into operating cash flow?",
        )
    ]


def select_driver_argument(view) -> ResearchSelection:
    """Qualify candidates, resolve overlap, and assign publication roles."""
    investigated = investigate_driver_questions(view)
    decisions: list[SelectionDecision] = []
    selected: list[ResearchQuestion] = []
    figures: list[str] = []
    by_id = {item.identifier: item for item in investigated}

    footprint = by_id.get("footprint_intensity")
    compsales = by_id.get("comparable_sales")
    spsf = by_id.get("sales_per_square_foot")
    geo = by_id.get("geographic_localization")
    margin = by_id.get("operating_margin_bridge")
    attribution = by_id.get("management_margin_attribution")
    cash = by_id.get("cash_conversion")

    if footprint and footprint.publication == PUBLICATION_MAIN:
        selected.append(footprint)
        decisions.append(
            SelectionDecision(
                footprint.identifier,
                "selected",
                footprint.publication_reason,
            )
        )
        if footprint.figure_purpose:
            figures.append(footprint.figure_purpose)
    elif footprint:
        decisions.append(
            SelectionDecision(footprint.identifier, "deferred", footprint.publication_reason)
        )

    if compsales and footprint and footprint.identifier in {item.identifier for item in selected}:
        selected.append(compsales)
        decisions.append(
            SelectionDecision(
                compsales.identifier,
                "combined",
                "Combined with footprint evidence; incompatible observations are not trended or figured.",
            )
        )
    elif compsales:
        decisions.append(
            SelectionDecision(
                compsales.identifier,
                "retained",
                "Period-specific observations remain available without a growth-divergence host.",
            )
        )

    if spsf:
        decisions.append(
            SelectionDecision(spsf.identifier, "excluded", spsf.publication_reason)
        )

    if geo and geo.publication == PUBLICATION_MAIN:
        selected.append(geo)
        decisions.append(SelectionDecision(geo.identifier, "selected", geo.publication_reason))
        if geo.figure_purpose:
            figures.append(geo.figure_purpose)
    elif geo:
        decisions.append(SelectionDecision(geo.identifier, "deferred", geo.publication_reason))

    if margin:
        selected.append(margin)
        decisions.append(SelectionDecision(margin.identifier, "selected", margin.publication_reason))
        if margin.figure_purpose:
            figures.append(margin.figure_purpose)
    if attribution and attribution.publication == PUBLICATION_MAIN and margin:
        selected.append(attribution)
        decisions.append(
            SelectionDecision(
                attribution.identifier,
                "combined",
                attribution.publication_reason,
            )
        )
    elif attribution:
        decisions.append(
            SelectionDecision(attribution.identifier, attribution.publication, attribution.publication_reason)
        )

    if cash and cash.publication == PUBLICATION_MAIN:
        selected.append(cash)
        decisions.append(SelectionDecision(cash.identifier, "selected", cash.publication_reason))
        if cash.figure_purpose:
            figures.append(cash.figure_purpose)
    elif cash:
        decisions.append(SelectionDecision(cash.identifier, "deferred", cash.publication_reason))

    ordered = []
    seen = set()
    for item in investigated:
        replacement = next((sel for sel in selected if sel.identifier == item.identifier), item)
        if replacement.identifier in seen:
            continue
        seen.add(replacement.identifier)
        ordered.append(replacement)
    return ResearchSelection(
        questions=tuple(ordered),
        decisions=tuple(decisions),
        main_body_ids=tuple(item.identifier for item in selected),
        figure_ids=tuple(dict.fromkeys(figures)),
    )
