"""Generic synthesis of admitted revenue-driver findings and strategy disclosures.

Issuer statements remain in company inputs. Methods do not special-case an
issuer. Management statements and objectives are never treated as achieved
outcomes. Arithmetic contributions remain accounting decompositions.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..data.historical_strategy import (
    ROLE_OBJECTIVE,
    ROLE_OPERATING_USE,
    ROLE_STRATEGY,
    THEME_COMPARABLE_SALES,
    THEME_GEOGRAPHIC_GROWTH,
    THEME_PRODUCTIVITY,
    THEME_STORE_EXPANSION,
    HistoricalStrategyDisclosure,
)
from ..data.interface import StandardizedFinancials
from ..engine.component_catalog import (
    COMPARABLE_SALES_SHEET_NAME,
    GEOGRAPHIC_SHEET_NAME,
    REVENUE_DRIVER_SHEET_NAME,
    REVENUE_PER_STORE_SHEET_NAME,
    SALES_PER_SQUARE_FOOT_SHEET_NAME,
    STORE_COUNT_SHEET_NAME,
)
from .revenue_driver import (
    VERDICT_CONTRADICTED,
    VERDICT_INSUFFICIENT,
    VERDICT_MIXED,
    VERDICT_SUPPORTED,
    RevenueDriverAnalysis,
    RevenueDriverHypothesisTest,
    compute_revenue_driver_analysis,
    revenue_driver_applicable,
)

THEME_LABELS = {
    THEME_STORE_EXPANSION: "Store expansion",
    THEME_COMPARABLE_SALES: "Comparable sales",
    THEME_PRODUCTIVITY: "Store productivity",
    THEME_GEOGRAPHIC_GROWTH: "Geographic expansion",
}
THEME_SCHEDULES = {
    THEME_STORE_EXPANSION: (
        REVENUE_DRIVER_SHEET_NAME,
        STORE_COUNT_SHEET_NAME,
        REVENUE_PER_STORE_SHEET_NAME,
    ),
    THEME_COMPARABLE_SALES: (
        REVENUE_DRIVER_SHEET_NAME,
        COMPARABLE_SALES_SHEET_NAME,
    ),
    THEME_PRODUCTIVITY: (
        REVENUE_DRIVER_SHEET_NAME,
        SALES_PER_SQUARE_FOOT_SHEET_NAME,
        REVENUE_PER_STORE_SHEET_NAME,
    ),
    THEME_GEOGRAPHIC_GROWTH: (
        REVENUE_DRIVER_SHEET_NAME,
        GEOGRAPHIC_SHEET_NAME,
    ),
}
_ROLE_PRIORITY = (ROLE_STRATEGY, ROLE_OPERATING_USE, ROLE_OBJECTIVE)
_COUNTEREXAMPLE_TOKENS = (
    "exceeded",
    "counterexample",
    "negatively",
    "declined",
    "did not",
)
UNTESTED_INITIATIVES = (
    "Disclosed initiatives that are not the subject of an admitted historical "
    "test remain untested. Consolidated revenue growth does not establish "
    "their success, and this opening does not claim comprehensive strategy "
    "execution."
)
WHAT_HISTORY_ESTABLISHES = (
    "The history establishes only the admitted descriptive coincidences, "
    "mixed geographic mix, and evidence gaps recorded below. It does not "
    "establish causal drivers, new-store contribution, organic growth, "
    "constant-currency performance, or comprehensive strategy execution. "
    "Strategic objectives remain plans rather than achieved outcomes."
)
DEFERRED_SPSF_LINK = (
    "The complete deferred sales-per-square-foot disagreement and detailed "
    "limitations remain on Revenue Driver Analysis; they stay audit-only and "
    "are not admitted observations in this opening."
)
PROFESSIONAL_FALLBACK = (
    "This workbook presents historical source-grounded financial analysis. "
    "Strategy and revenue-driver interpretation appear only when management "
    "disclosures and admitted operating evidence are supplied."
)


@dataclass(frozen=True)
class StrategyFindingInterpretation:
    """One theme: management statement, admitted finding, and qualified inference."""

    theme: str
    heading: str
    management_statement: str
    finding: str
    inference: str
    supporting_schedules: tuple[str, ...]
    counterexample: str


@dataclass(frozen=True)
class HistoricalStrategySynthesis:
    """Concise opening interpretation connecting findings to disclosed strategy."""

    lead: str
    interpretations: tuple[StrategyFindingInterpretation, ...]
    productivity_gap: str
    untested: str
    limits: str
    navigation: tuple[str, ...]


def strategy_synthesis_applicable(financials: StandardizedFinancials) -> bool:
    return revenue_driver_applicable(financials)


def disclosure_locator(item: HistoricalStrategyDisclosure) -> str:
    return (
        f"{item.source_file}; {item.page_reference}; {item.section}; "
        f"period-end {item.period.isoformat()}"
    )


def _featured_disclosure(
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> HistoricalStrategyDisclosure:
    for role in _ROLE_PRIORITY:
        for item in disclosures:
            if item.role == role:
                return item
    return disclosures[0]


def _format_statement(item: HistoricalStrategyDisclosure) -> str:
    role = item.role.replace("_", " ")
    return f'{item.text} [{disclosure_locator(item)}] ({role})'


def _management_statement(
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> str:
    featured = [
        item for item in disclosures if item.role in (ROLE_STRATEGY, ROLE_OPERATING_USE)
    ]
    if not featured:
        featured = [_featured_disclosure(disclosures)]
    parts = [_format_statement(item) for item in featured]
    objectives = tuple(
        item
        for item in disclosures
        if item.role == ROLE_OBJECTIVE and item not in featured
    )
    if objectives:
        additional = "; ".join(
            f"[{disclosure_locator(item)}] ({item.role.replace('_', ' ')})"
            for item in objectives
        )
        parts.append("Additional statements: " + additional + ".")
    return " ".join(parts)


def _schedule_clause(theme: str) -> str:
    names = THEME_SCHEDULES.get(theme, (REVENUE_DRIVER_SHEET_NAME,))
    return f"See {_join_labels(list(names))}."


def _counterexample_notes(test: RevenueDriverHypothesisTest) -> tuple[str, ...]:
    notes: list[str] = []
    for item in test.observations:
        if not item.note:
            continue
        lowered = item.note.lower()
        if any(token in lowered for token in _COUNTEREXAMPLE_TOKENS):
            notes.append(item.note)
    return tuple(dict.fromkeys(notes))


def _qualification(test: RevenueDriverHypothesisTest) -> str:
    bits: list[str] = []
    if test.theme == THEME_STORE_EXPANSION:
        bits.append(
            "The revenue-versus-store-count difference is descriptive and is not "
            "new-store contribution, organic growth, or causal evidence."
        )
    elif test.theme == THEME_COMPARABLE_SALES:
        bits.append(
            "The revenue-versus-comparable-sales difference is descriptive only. "
            "Reported and constant-currency series remain separate."
        )
        if any("ineligible" in item.lower() for item in test.limitations):
            bits.append(
                "Historical comparable-sales-to-comparable-sales comparison "
                "remains ineligible."
            )
    elif test.theme == THEME_PRODUCTIVITY:
        bits.append(
            "Total-company revenue divided by company-operated stores is not "
            "independent productivity evidence."
        )
    elif test.theme == THEME_GEOGRAPHIC_GROWTH:
        bits.append(
            "Geographic contributions are an arithmetic decomposition of "
            "reported revenue, not organic, constant-currency, or causal growth."
        )
    if any(item.role == ROLE_OBJECTIVE for item in test.disclosures):
        bits.append(
            "Strategic objectives and plans are management statements, not "
            "achieved historical outcomes."
        )
    return " ".join(bits)


def _verdict_inference(test: RevenueDriverHypothesisTest) -> str:
    label = THEME_LABELS.get(test.theme, test.theme.replace("_", " "))
    lowered = label[0].lower() + label[1:] if label else test.theme
    if test.verdict == VERDICT_SUPPORTED:
        base = (
            f"Admitted history is descriptively consistent with disclosed "
            f"{lowered} as a coincident of revenue growth over "
            f"{test.sample_size} aligned observation"
            f"{'' if test.sample_size == 1 else 's'}."
        )
    elif test.verdict == VERDICT_MIXED:
        base = (
            f"Admitted history is mixed for disclosed {lowered}: some aligned "
            "periods or segments coincide with revenue growth and others diverge."
        )
    elif test.verdict == VERDICT_CONTRADICTED:
        base = (
            f"Admitted history contradicts disclosed {lowered} as a coincident "
            "revenue descriptor over the tested periods."
        )
    else:
        failed = test.failed_requirement or "required admitted evidence"
        base = (
            f"Admitted history cannot test disclosed {lowered}. Failed "
            f"requirement: {failed}. The disclosure remains a management "
            "statement, not a demonstrated outcome."
        )
    extras = _counterexample_notes(test)
    qualification = _qualification(test)
    return " ".join(part for part in (base, *extras, qualification) if part)


def _has_deferred_spsf(test: RevenueDriverHypothesisTest) -> bool:
    return any(
        item.startswith("Deferred ") and "disagreement at period-end" in item
        for item in test.limitations
    )


def _productivity_gap(tests: tuple[RevenueDriverHypothesisTest, ...]) -> str:
    productivity = next(
        (test for test in tests if test.theme == THEME_PRODUCTIVITY),
        None,
    )
    if productivity is None:
        return ""
    parts: list[str] = []
    if productivity.verdict == VERDICT_INSUFFICIENT:
        parts.append(
            "Disclosed sales-per-square-foot use cannot support a productivity "
            "contribution in this synthesis. Adjacent SPSF growth is unavailable "
            f"on admitted history (sample size {productivity.sample_size})."
        )
    else:
        parts.append(
            f"Store-productivity verdict: {productivity.verdict.replace('_', ' ')} "
            f"(sample size {productivity.sample_size})."
        )
    parts.append(
        "Period-end Revenue per Store is an identity using total-company "
        "revenue divided by company-operated stores and is not independent "
        "productivity evidence."
    )
    if _has_deferred_spsf(productivity):
        parts.append(DEFERRED_SPSF_LINK)
    return " ".join(parts)


def _join_labels(labels: list[str]) -> str:
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _lead(tests: tuple[RevenueDriverHypothesisTest, ...]) -> str:
    by_verdict: dict[str, list[str]] = {
        VERDICT_SUPPORTED: [],
        VERDICT_MIXED: [],
        VERDICT_CONTRADICTED: [],
        VERDICT_INSUFFICIENT: [],
    }
    counterexamples: list[str] = []
    for test in tests:
        label = THEME_LABELS.get(test.theme, test.theme.replace("_", " "))
        lowered = label[0].lower() + label[1:]
        by_verdict.setdefault(test.verdict, []).append(lowered)
        counterexamples.extend(_counterexample_notes(test))
    sentences: list[str] = []
    supported = by_verdict.get(VERDICT_SUPPORTED) or []
    if supported:
        sentences.append(
            "Admitted history is descriptively consistent with "
            + _join_labels(supported)
            + " over aligned periods."
        )
    mixed = by_verdict.get(VERDICT_MIXED) or []
    if mixed:
        sentences.append(
            _join_labels(mixed).capitalize()
            + " "
            + ("is" if len(mixed) == 1 else "are")
            + " mixed across periods or segments."
        )
    contradicted = by_verdict.get(VERDICT_CONTRADICTED) or []
    if contradicted:
        sentences.append(
            "Admitted history contradicts "
            + _join_labels(contradicted)
            + " as a coincident revenue descriptor."
        )
    insufficient = by_verdict.get(VERDICT_INSUFFICIENT) or []
    if insufficient:
        sentences.append(
            _join_labels(insufficient).capitalize()
            + " cannot be treated as a demonstrated historical revenue driver "
            "because the required admitted test is missing."
        )
    if counterexamples:
        sentences.append(
            "Period-specific store and geographic counterexamples prevent "
            "reading the history as lockstep store growth or uniformly "
            "positive geographic contributions."
        )
    sentences.append(
        "Taken together, the tests describe a historical growth pattern; they "
        "do not establish causal drivers, comprehensive strategy execution, "
        "or the success of untested initiatives."
    )
    return " ".join(sentences)


def _interpretations(
    tests: tuple[RevenueDriverHypothesisTest, ...],
) -> tuple[StrategyFindingInterpretation, ...]:
    rows: list[StrategyFindingInterpretation] = []
    for test in tests:
        extras = _counterexample_notes(test)
        rows.append(
            StrategyFindingInterpretation(
                theme=test.theme,
                heading=THEME_LABELS.get(
                    test.theme, test.theme.replace("_", " ").title()
                ),
                management_statement=_management_statement(test.disclosures),
                finding=f"{test.finding} {_schedule_clause(test.theme)}",
                inference=_verdict_inference(test),
                supporting_schedules=THEME_SCHEDULES.get(
                    test.theme, (REVENUE_DRIVER_SHEET_NAME,)
                ),
                counterexample=" ".join(extras),
            )
        )
    return tuple(rows)


def _navigation(tests: tuple[RevenueDriverHypothesisTest, ...]) -> tuple[str, ...]:
    names: list[str] = []
    for test in tests:
        for name in THEME_SCHEDULES.get(test.theme, ()):
            if name not in names:
                names.append(name)
    if REVENUE_DRIVER_SHEET_NAME not in names:
        names.insert(0, REVENUE_DRIVER_SHEET_NAME)
    return tuple(names)


def compute_historical_strategy_synthesis(
    financials: StandardizedFinancials,
    analysis: RevenueDriverAnalysis | None = None,
) -> HistoricalStrategySynthesis:
    """Connect admitted driver findings to source-bound strategy disclosures."""
    if not strategy_synthesis_applicable(financials):
        raise ValueError("strategy synthesis requires admitted strategy disclosures")
    if analysis is None:
        analysis = compute_revenue_driver_analysis(financials)
    tests = analysis.tests
    if not tests:
        raise ValueError("strategy synthesis requires at least one driver test")
    return HistoricalStrategySynthesis(
        lead=_lead(tests),
        interpretations=_interpretations(tests),
        productivity_gap=_productivity_gap(tests),
        untested=UNTESTED_INITIATIVES,
        limits=WHAT_HISTORY_ESTABLISHES,
        navigation=_navigation(tests),
    )
