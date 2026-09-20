"""Disclosure-led historical revenue-driver tests from admitted evidence.

Generic methods. Issuer statements remain in source-bound company inputs.
Management statements are never treated as achieved outcomes. Revenue-growth
minus comparable-sales and revenue-growth minus store-growth results are
descriptive differences, not new-store contribution, organic growth, or
causal attribution. Total revenue divided by stores is an identity and cannot
independently demonstrate store productivity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.historical_operating_kpis import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
)
from ..data.interface import (
    HistoricalManagementKpiDeferredDisagreement,
    StandardizedFinancials,
)
from ..data.historical_strategy import (
    ROLE_OBJECTIVE,
    THEME_COMPARABLE_SALES,
    THEME_GEOGRAPHIC_GROWTH,
    THEME_PRODUCTIVITY,
    THEME_STORE_EXPANSION,
    HistoricalStrategyData,
    HistoricalStrategyDisclosure,
)
from .geographic_segment import (
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from .line_resolver import MissingLineError
from .management_kpi import (
    REASON_CALENDAR_REPORTING_MISMATCH,
    REASON_CALENDAR_WEEK_MISMATCH,
    REASON_DEFINITION_MISMATCH,
    REASON_MISSING_OBSERVATION,
    REASON_MISSING_PRIOR_OBSERVATION,
    REASON_PERIOD_KIND_MISMATCH,
    REASON_QUALIFIER_MISMATCH,
    compute_management_kpi_series,
    management_kpi_applicable,
)
from .operating_kpi import operating_kpi_applicable
from .operating_kpi_relationships import (
    compute_operating_kpi_revenue_comparable_sales_relationship,
    compute_operating_kpi_revenue_sales_per_square_foot_relationship,
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_comparable_sales_relationship_applicable,
    operating_kpi_revenue_sales_per_square_foot_relationship_applicable,
    operating_kpi_revenue_store_relationship_applicable,
)
from .period_axis import PeriodAxisError, canonical_fiscal_periods
from .ratio_values import SOURCE_UNAVAILABLE, is_source_unavailable
from .revenue_per_store import (
    SCOPE_NOTE as REVENUE_PER_STORE_SCOPE_NOTE,
    compute_revenue_per_store_series,
    revenue_per_store_applicable,
)

CALCULATION_KIND = "analyst-derived"
VERDICT_SUPPORTED = "supported_descriptively"
VERDICT_MIXED = "mixed"
VERDICT_CONTRADICTED = "contradicted"
VERDICT_INSUFFICIENT = "insufficiently_evidenced"
SUPPORTED_VERDICTS = (
    VERDICT_SUPPORTED,
    VERDICT_MIXED,
    VERDICT_CONTRADICTED,
    VERDICT_INSUFFICIENT,
)
HYPOTHESIS_STORE_EXPANSION = (
    "If disclosed store expansion was a material historical revenue driver, "
    "company-operated store counts and consolidated revenue should both "
    "increase over aligned periods."
)
HYPOTHESIS_COMPARABLE_SALES = (
    "If disclosed comparable sales were a material historical revenue driver, "
    "reported global comparable-sales percentages should be positive in "
    "periods when statement-derived consolidated revenue grew."
)
HYPOTHESIS_PRODUCTIVITY = (
    "If disclosed store productivity was a material historical revenue driver, "
    "adjacent sales-per-square-foot growth should be measurable on admitted "
    "company-operated-store observations."
)
HYPOTHESIS_GEOGRAPHIC = (
    "If disclosed geographic expansion was a material historical revenue "
    "driver, admitted geographic segments should show positive reported "
    "revenue-growth contributions to consolidated revenue over aligned periods."
)
MECHANISM_STORE_EXPANSION = (
    "Additional company-operated stores can add selling capacity. The test "
    "compares statement-derived consolidated revenue growth with company-"
    "operated period-end store-count growth."
)
MECHANISM_COMPARABLE_SALES = (
    "Continuing stores and disclosed comparable channels can grow revenue "
    "without a change in store count. The test compares statement-derived "
    "consolidated revenue growth with reported global comparable-sales "
    "percentages."
)
MECHANISM_PRODUCTIVITY = (
    "Higher sales per unit of store space can grow revenue independently of "
    "store count. The disclosed productivity metric is sales per square foot. "
    "Revenue per Store is retained only as an identity diagnostic."
)
MECHANISM_GEOGRAPHIC = (
    "Geographic mix can change consolidated revenue when some regions grow "
    "faster than others. The test uses admitted arithmetic revenue-growth "
    "contributions."
)
SCOPE_NOTE = (
    "Management statements are source facts, not achieved outcomes. Analyst "
    "hypotheses are tested separately. Revenue-growth-minus-comparable-sales "
    "and revenue-growth-minus-store-growth results are descriptive differences, "
    "never new-store contribution, organic growth, or causal attribution. "
    "Total-company revenue divided by company-operated stores is an accounting "
    "identity and cannot independently demonstrate store productivity or "
    "explain store expansion's causal contribution. Reported and constant-"
    "currency metrics, geographic and channel populations, fiscal-year labels "
    "and actual period-end dates remain distinct."
)
FAILED_STORE_GROWTH = (
    "adjacent admitted consolidated revenue growth and company-operated "
    "period-end store-count growth"
)
FAILED_COMPSALES = (
    "admitted global reported comparable-sales percentages aligned to "
    "statement-derived consolidated revenue growth"
)
FAILED_SPSF_GROWTH = (
    "immediately adjacent semantically compatible reported sales-per-square-"
    "foot observations"
)
FAILED_GEOGRAPHIC = (
    "admitted geographic revenue-growth contributions on immediately adjacent "
    "canonical periods"
)
ADDITIONAL_COMPSALES_HISTORY = (
    "calendar-compatible comparable-sales comparison windows and a single "
    "continuing identity across adjacent periods"
)
ADDITIONAL_SPSF = (
    "admitted adjacent SPSF observations with equivalent definition, "
    "population, calendar, and comparison-window evidence"
)
_SEGMENT_LABELS = {
    "americas": "Americas",
    "china_mainland": "China Mainland",
    "rest_of_world": "Rest of World",
}
_SPSF_REASON_LABELS = {
    REASON_DEFINITION_MISMATCH: "definition mismatch",
    REASON_PERIOD_KIND_MISMATCH: "period-kind mismatch",
    REASON_CALENDAR_WEEK_MISMATCH: "calendar week-adjustment mismatch",
    REASON_CALENDAR_REPORTING_MISMATCH: "calendar reporting-basis mismatch",
    REASON_QUALIFIER_MISMATCH: "qualifier mismatch",
    REASON_MISSING_OBSERVATION: "missing admitted observation",
    REASON_MISSING_PRIOR_OBSERVATION: "missing prior admitted observation",
}
_FAMILY_DISAGREEMENT_LABELS = {
    FAMILY_SALES_PER_SQUARE_FOOT: "sales-per-square-foot",
    FAMILY_COMPARABLE_SALES_GROWTH: "comparable-sales",
}
_QUALIFIER_FIELDS = (
    ("population", "population"),
    ("unit", "unit"),
    ("basis", "basis"),
    ("calendar_week_adjustment", "calendar week-adjustment"),
    ("calendar_reporting_basis", "calendar reporting-basis"),
)


@dataclass(frozen=True)
class RevenueDriverPeriodObservation:
    """One aligned-period observation used by a hypothesis test."""

    period: date
    inputs: dict[str, float | str | None]
    consistent: bool | None
    note: str


@dataclass(frozen=True)
class RevenueDriverHypothesisTest:
    """One disclosure-led hypothesis and its historical test result."""

    theme: str
    hypothesis: str
    mechanism: str
    disclosures: tuple[HistoricalStrategyDisclosure, ...]
    admitted_inputs: tuple[str, ...]
    periods_tested: tuple[date, ...]
    sample_size: int
    observations: tuple[RevenueDriverPeriodObservation, ...]
    verdict: str
    finding: str
    limitations: tuple[str, ...]
    failed_requirement: str
    additional_evidence: str
    identity_notes: tuple[str, ...]


@dataclass(frozen=True)
class RevenueDriverAnalysis:
    """Disclosure-led revenue-driver tests keyed by generic themes."""

    periods: tuple[date, ...]
    calculation_kind: str
    scope_note: str
    tests: tuple[RevenueDriverHypothesisTest, ...]


def revenue_driver_applicable(financials: StandardizedFinancials) -> bool:
    data = financials.historical_strategy
    return bool(data is not None and data.disclosures)


def _require_annual_axis(financials: StandardizedFinancials) -> None:
    if not any(not period.is_interim for period in financials.periods):
        raise PeriodAxisError("revenue-driver analysis requires annual fiscal periods")


def _numeric(value: float | str | None) -> float | None:
    if value is None or is_source_unavailable(value):
        return None
    if isinstance(value, str):
        return None
    return float(value)


def _verdict_from_consistency(flags: tuple[bool | None, ...]) -> str:
    known = tuple(flag for flag in flags if flag is not None)
    if not known:
        return VERDICT_INSUFFICIENT
    if all(known):
        return VERDICT_SUPPORTED
    if not any(known):
        return VERDICT_CONTRADICTED
    return VERDICT_MIXED


def _disclosures_for(
    data: HistoricalStrategyData, theme: str
) -> tuple[HistoricalStrategyDisclosure, ...]:
    return tuple(item for item in data.disclosures if item.theme == theme)


def _objective_limitation(
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> tuple[str, ...]:
    if any(item.role == ROLE_OBJECTIVE for item in disclosures):
        return (
            "Strategic objectives and plans are recorded as management statements "
            "and are not treated as achieved historical outcomes.",
        )
    return ()


def _format_ratio_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _format_pp(value: float) -> str:
    return f"{value:.3f} pp"


def _segment_label(identity: str) -> str:
    return _SEGMENT_LABELS.get(identity, identity.replace("_", " ").title())


def _is_counterexample_note(note: str) -> bool:
    lowered = note.lower()
    return any(
        token in lowered
        for token in (
            "exceeded",
            "counterexample",
            "negatively",
            "declined",
            "did not",
        )
    )


def _finding_with_counterexamples(base: str, observations: tuple[RevenueDriverPeriodObservation, ...]) -> str:
    extras = tuple(
        item.note
        for item in observations
        if item.note and _is_counterexample_note(item.note)
    )
    if not extras:
        return base
    return base + " " + " ".join(extras)


def _compsales_population_limitations(
    financials: StandardizedFinancials,
) -> tuple[str, ...]:
    data = financials.historical_operating_kpis
    if data is None:
        return ()
    by_population: dict[str, list[date]] = {}
    for item in data.management_observations:
        if item.family != FAMILY_COMPARABLE_SALES_GROWTH:
            continue
        if item.basis != "reported":
            continue
        periods = by_population.setdefault(item.population, [])
        if item.period not in periods:
            periods.append(item.period)
    if len(by_population) <= 1:
        return ()
    parts = []
    for population in sorted(by_population):
        dates = ", ".join(period.isoformat() for period in sorted(by_population[population]))
        parts.append(f"{population} at period-end {dates}")
    return (
        "Admitted comparable-sales identities remain distinct by population "
        "and are never merged: " + "; ".join(parts) + ".",
    )


def _compsales_adjacent_comparison_ineligible(
    financials: StandardizedFinancials, axis: list[date]
) -> bool:
    if not management_kpi_applicable(financials):
        return False
    series = compute_management_kpi_series(financials, axis)
    saw_identity = False
    for identity in series.identities:
        item = series.series[identity]
        if item.family != FAMILY_COMPARABLE_SALES_GROWTH:
            continue
        saw_identity = True
        for index, period in enumerate(axis):
            if index == 0:
                continue
            if _numeric(item.adjacent_change[period]) is not None:
                return False
    return saw_identity


def _deferred_member_locator(member) -> str:
    pages = []
    if member.page_reference:
        pages.append(member.page_reference)
    if member.physical_page_mapping:
        pages.append(f"physical {member.physical_page_mapping}")
    source = "; ".join(
        part
        for part in (member.extraction_document, *pages)
        if part
    )
    locator = member.locator
    if source:
        return f"{locator} [{source}]"
    return locator


def _conflicting_qualifier_labels(
    item: HistoricalManagementKpiDeferredDisagreement,
) -> tuple[str, ...]:
    labels: list[str] = []
    for field, label in _QUALIFIER_FIELDS:
        values = {getattr(member, field) for member in item.members}
        if len(values) > 1:
            labels.append(label)
    definitions = {member.definition_text for member in item.members}
    if len(definitions) > 1:
        labels.insert(0, "definition")
    return tuple(labels)


def _format_deferred_disagreement(
    item: HistoricalManagementKpiDeferredDisagreement,
) -> str:
    family_label = _FAMILY_DISAGREEMENT_LABELS.get(
        item.family, item.family.replace("_", "-")
    )
    conflict_labels = _conflicting_qualifier_labels(item)
    conflict_text = (
        ", ".join(conflict_labels) if conflict_labels else "definition or qualifier"
    )
    member_parts = []
    for member in item.members:
        role = member.presentation_role.replace("_", " ") or "unspecified role"
        member_parts.append(
            f'{role} occurrence {_deferred_member_locator(member)} '
            f'defines {family_label} as "{member.definition_text}"'
        )
    reasons = ", ".join(item.reasons)
    return (
        f"Deferred {family_label} disagreement at period-end "
        f"{item.period.isoformat()} is not admitted. Conflicting {conflict_text} "
        f"evidence: " + "; ".join(member_parts) + ". Deferral reasons: "
        f"{reasons}. The complete group remains audit-only; the disagreement is "
        "not bridged into the test and does not create an admitted observation."
    )


def _deferred_disagreement_limitations(
    financials: StandardizedFinancials,
    family: str,
) -> tuple[str, ...]:
    data = financials.historical_operating_kpis
    if data is None:
        return ()
    return tuple(
        _format_deferred_disagreement(item)
        for item in data.deferred_disagreements
        if item.family == family
    )


def _spsf_evidence_limitations(
    financials: StandardizedFinancials, axis: list[date]
) -> tuple[str, ...]:
    limits: list[str] = []
    data = financials.historical_operating_kpis
    observations = ()
    if data is not None:
        observations = tuple(
            item
            for item in data.management_observations
            if item.family == FAMILY_SALES_PER_SQUARE_FOOT
        )
    admitted_periods = {item.period for item in observations}
    if observations:
        missing = tuple(period for period in axis if period not in admitted_periods)
        if missing:
            dates = ", ".join(period.isoformat() for period in missing)
            limits.append(
                "No admitted sales-per-square-foot observation exists for "
                f"period-end {dates}; those period(s) are not bridged."
            )
    if not management_kpi_applicable(financials):
        return tuple(limits)
    series = compute_management_kpi_series(financials, axis)
    reason_parts: list[str] = []
    for identity in series.identities:
        item = series.series[identity]
        if item.family != FAMILY_SALES_PER_SQUARE_FOOT:
            continue
        for index, period in enumerate(axis):
            if index == 0:
                continue
            reasons = item.unavailable_reasons.get(period) or ()
            if not reasons:
                continue
            labels = tuple(
                _SPSF_REASON_LABELS.get(reason, reason.replace("_", " "))
                for reason in reasons
            )
            reason_parts.append(
                f"{period.isoformat()} ({', '.join(labels)})"
            )
    if reason_parts:
        limits.append(
            "Adjacent SPSF growth is unavailable on admitted evidence at "
            + "; ".join(reason_parts)
            + ". Those gaps are not bridged."
        )
    limits.extend(_deferred_disagreement_limitations(financials, FAMILY_SALES_PER_SQUARE_FOOT))
    return tuple(limits)


def _store_expansion_test(
    financials: StandardizedFinancials,
    axis: list[date],
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> RevenueDriverHypothesisTest:
    limitations = [
        "The growth difference is a descriptive comparison of distinct scopes: "
        "consolidated revenue versus company-operated period-end store counts.",
        "The difference is not new-store contribution, organic growth, store "
        "productivity, or causal evidence.",
        REVENUE_PER_STORE_SCOPE_NOTE,
        *_objective_limitation(disclosures),
    ]
    inputs = (
        "statement-derived consolidated revenue growth",
        "company-operated period-end store-count growth",
        "analyst-derived revenue-versus-store-count growth difference",
    )
    if not operating_kpi_revenue_store_relationship_applicable(financials):
        return RevenueDriverHypothesisTest(
            theme=THEME_STORE_EXPANSION,
            hypothesis=HYPOTHESIS_STORE_EXPANSION,
            mechanism=MECHANISM_STORE_EXPANSION,
            disclosures=disclosures,
            admitted_inputs=inputs,
            periods_tested=(),
            sample_size=0,
            observations=(),
            verdict=VERDICT_INSUFFICIENT,
            finding=(
                "Store-expansion cannot be tested: company-operated store-count "
                "history is not admitted."
            ),
            limitations=tuple(limitations),
            failed_requirement=FAILED_STORE_GROWTH,
            additional_evidence=FAILED_STORE_GROWTH,
            identity_notes=(REVENUE_PER_STORE_SCOPE_NOTE,),
        )
    relationship = compute_operating_kpi_revenue_store_relationship(financials, axis)
    rps = (
        compute_revenue_per_store_series(financials, axis)
        if revenue_per_store_applicable(financials)
        else None
    )
    observations: list[RevenueDriverPeriodObservation] = []
    for index, period in enumerate(axis):
        if index == 0:
            continue
        rev = _numeric(relationship.revenue_growth[period])
        stores = _numeric(relationship.store_count_growth[period])
        difference = relationship.growth_difference_pp[period]
        rps_change = None if rps is None else rps.period_end_change[period]
        payload: dict[str, float | str | None] = {
            "revenue_growth": relationship.revenue_growth[period],
            "store_count_growth": relationship.store_count_growth[period],
            "growth_difference_pp": difference,
            "period_end_revenue_per_store_change": rps_change,
        }
        if rev is None or stores is None:
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=payload,
                    consistent=None,
                    note="Missing adjacent revenue or store-count growth.",
                )
            )
            continue
        coincident = rev > 0 and stores > 0
        notes: list[str] = []
        if coincident:
            notes.append(
                "Both consolidated revenue and company-operated store counts grew."
            )
        elif stores > 0 and rev <= 0:
            notes.append(
                f"Period-end {period.isoformat()}: store count grew "
                f"{_format_ratio_pct(stores)} while consolidated revenue did not "
                f"({_format_ratio_pct(rev)}); this contradicts expansion as a "
                "coincident revenue driver in this period."
            )
        elif rev > 0 and stores <= 0:
            notes.append(
                f"Period-end {period.isoformat()}: consolidated revenue grew "
                f"{_format_ratio_pct(rev)} without store-count growth "
                f"({_format_ratio_pct(stores)})."
            )
        else:
            notes.append(
                f"Period-end {period.isoformat()}: neither revenue nor store "
                "count grew."
            )
        if stores > rev:
            difference_number = _numeric(difference)
            difference_text = (
                f" (descriptive difference {_format_pp(difference_number)})"
                if difference_number is not None
                else ""
            )
            notes.append(
                f"Period-end {period.isoformat()}: store-count growth "
                f"{_format_ratio_pct(stores)} exceeded revenue growth "
                f"{_format_ratio_pct(rev)}{difference_text}. This is a "
                "descriptive counterexample, not new-store contribution or "
                "proof that expansion reduced productivity."
            )
        rps_change_number = _numeric(rps_change)
        if rps_change_number is not None and rps_change_number < 0:
            notes.append(
                f"Period-end {period.isoformat()}: period-end Revenue per Store "
                "declined. That identity uses total-company revenue divided by "
                "company-operated stores and cannot independently demonstrate "
                "store productivity."
            )
        observations.append(
            RevenueDriverPeriodObservation(
                period=period,
                inputs=payload,
                consistent=coincident,
                note=" ".join(notes),
            )
        )
    flags = tuple(item.consistent for item in observations)
    tested = tuple(item.period for item in observations if item.consistent is not None)
    verdict = _verdict_from_consistency(flags)
    if verdict == VERDICT_INSUFFICIENT:
        finding = (
            "Store-expansion cannot be tested from the admitted series: no "
            "aligned adjacent revenue and store-count growth values exist."
        )
        failed = FAILED_STORE_GROWTH
        additional = FAILED_STORE_GROWTH
    else:
        failed = ""
        additional = ""
        finding = _finding_with_counterexamples(
            f"{len(tested)} aligned period(s) compare statement-derived "
            "consolidated revenue growth with company-operated store-count "
            f"growth. Verdict: {verdict.replace('_', ' ')}.",
            tuple(observations),
        )
    return RevenueDriverHypothesisTest(
        theme=THEME_STORE_EXPANSION,
        hypothesis=HYPOTHESIS_STORE_EXPANSION,
        mechanism=MECHANISM_STORE_EXPANSION,
        disclosures=disclosures,
        admitted_inputs=inputs,
        periods_tested=tested,
        sample_size=len(tested),
        observations=tuple(observations),
        verdict=verdict,
        finding=finding,
        limitations=tuple(limitations),
        failed_requirement=failed,
        additional_evidence=additional,
        identity_notes=(REVENUE_PER_STORE_SCOPE_NOTE,),
    )


def _comparable_sales_test(
    financials: StandardizedFinancials,
    axis: list[date],
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> RevenueDriverHypothesisTest:
    limitations = [
        "The revenue-versus-comparable-sales difference is not new-store "
        "contribution, organic growth, productivity, or causal evidence.",
        "Reported and constant-currency comparable-sales series remain separate.",
        *_compsales_population_limitations(financials),
        *(
            (
                "Historical comparable-sales-to-comparable-sales comparison remains "
                "ineligible on the admitted identities, periods, and calendar/"
                "comparison-window evidence.",
            )
            if _compsales_adjacent_comparison_ineligible(financials, axis)
            else ()
        ),
        *_deferred_disagreement_limitations(
            financials, FAMILY_COMPARABLE_SALES_GROWTH
        ),
        *_objective_limitation(disclosures),
    ]
    inputs = (
        "statement-derived consolidated revenue growth",
        "admitted global reported comparable-sales percentages",
        "analyst-derived revenue-versus-comparable-sales descriptive difference",
    )
    if not operating_kpi_revenue_comparable_sales_relationship_applicable(financials):
        return RevenueDriverHypothesisTest(
            theme=THEME_COMPARABLE_SALES,
            hypothesis=HYPOTHESIS_COMPARABLE_SALES,
            mechanism=MECHANISM_COMPARABLE_SALES,
            disclosures=disclosures,
            admitted_inputs=inputs,
            periods_tested=(),
            sample_size=0,
            observations=(),
            verdict=VERDICT_INSUFFICIENT,
            finding=(
                "Comparable-sales cannot be tested: no admitted global reported "
                "comparable-sales observations are available."
            ),
            limitations=tuple(limitations),
            failed_requirement=FAILED_COMPSALES,
            additional_evidence=ADDITIONAL_COMPSALES_HISTORY,
            identity_notes=(),
        )
    relationship = compute_operating_kpi_revenue_comparable_sales_relationship(
        financials, axis
    )
    observations: list[RevenueDriverPeriodObservation] = []
    tested: list[date] = []
    flags: list[bool | None] = []
    for identity in relationship.identities:
        series = relationship.series[identity]
        for index, period in enumerate(axis):
            if index == 0:
                continue
            rev = _numeric(series.revenue_growth[period])
            compsales = _numeric(series.comparable_sales_growth[period])
            payload: dict[str, float | str | None] = {
                "identity": identity,
                "revenue_growth": series.revenue_growth[period],
                "comparable_sales_percent": series.comparable_sales_growth[period],
                "growth_difference_pp": series.growth_difference_pp[period],
                "population": series.population,
                "basis": series.basis,
            }
            if rev is None or compsales is None:
                observations.append(
                    RevenueDriverPeriodObservation(
                        period=period,
                        inputs=payload,
                        consistent=None,
                        note="Missing aligned revenue growth or comparable-sales percent.",
                    )
                )
                continue
            consistent = rev > 0 and compsales > 0
            if consistent:
                note = (
                    f"Period-end {period.isoformat()}: consolidated revenue grew "
                    f"{_format_ratio_pct(rev)} and reported global comparable "
                    f"sales were {compsales:.2f}%. The difference is descriptive only."
                )
            elif rev > 0 and compsales <= 0:
                note = (
                    f"Period-end {period.isoformat()}: consolidated revenue grew "
                    f"{_format_ratio_pct(rev)} while reported comparable sales "
                    f"were {compsales:.2f}%."
                )
            elif rev <= 0 and compsales > 0:
                note = (
                    f"Period-end {period.isoformat()}: reported comparable sales "
                    f"were {compsales:.2f}% while consolidated revenue did not "
                    f"grow ({_format_ratio_pct(rev)})."
                )
            else:
                note = (
                    f"Period-end {period.isoformat()}: neither consolidated "
                    "revenue growth nor reported comparable sales were positive."
                )
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=payload,
                    consistent=consistent,
                    note=note,
                )
            )
            flags.append(consistent)
            tested.append(period)
    unique_tested = tuple(dict.fromkeys(tested))
    verdict = _verdict_from_consistency(tuple(flags))
    if verdict == VERDICT_INSUFFICIENT:
        finding = (
            "Comparable-sales cannot be tested: no aligned global reported "
            "percentages exist for statement-derived revenue growth."
        )
        failed = FAILED_COMPSALES
        additional = ADDITIONAL_COMPSALES_HISTORY
    else:
        failed = ""
        additional = ADDITIONAL_COMPSALES_HISTORY
        finding = _finding_with_counterexamples(
            f"{len(flags)} identity-period observation(s) across "
            f"{len(unique_tested)} period-end date(s). Verdict: "
            f"{verdict.replace('_', ' ')}.",
            tuple(observations),
        )
    return RevenueDriverHypothesisTest(
        theme=THEME_COMPARABLE_SALES,
        hypothesis=HYPOTHESIS_COMPARABLE_SALES,
        mechanism=MECHANISM_COMPARABLE_SALES,
        disclosures=disclosures,
        admitted_inputs=inputs,
        periods_tested=unique_tested,
        sample_size=len(flags),
        observations=tuple(observations),
        verdict=verdict,
        finding=finding,
        limitations=tuple(limitations),
        failed_requirement=failed,
        additional_evidence=additional,
        identity_notes=(),
    )


def _productivity_test(
    financials: StandardizedFinancials,
    axis: list[date],
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> RevenueDriverHypothesisTest:
    limitations = [
        REVENUE_PER_STORE_SCOPE_NOTE,
        "Adjacent SPSF change/growth remain unavailable unless immediately "
        "adjacent semantically compatible reported observations exist.",
        *_spsf_evidence_limitations(financials, axis),
        *_objective_limitation(disclosures),
    ]
    inputs = (
        "admitted company-operated-store sales per square foot",
        "adjacent SPSF growth when semantically compatible",
        "period-end Revenue per Store identity diagnostic",
    )
    spsf_growth_available = False
    spsf_observations: list[RevenueDriverPeriodObservation] = []
    if operating_kpi_revenue_sales_per_square_foot_relationship_applicable(financials):
        relationship = compute_operating_kpi_revenue_sales_per_square_foot_relationship(
            financials, axis
        )
        for identity in relationship.identities:
            series = relationship.series[identity]
            for index, period in enumerate(axis):
                if index == 0:
                    continue
                growth = _numeric(series.spsf_growth[period])
                payload = {
                    "identity": identity,
                    "spsf_growth": series.spsf_growth[period],
                    "revenue_growth": series.revenue_growth[period],
                    "growth_difference_pp": series.growth_difference_pp[period],
                }
                if growth is None:
                    spsf_observations.append(
                        RevenueDriverPeriodObservation(
                            period=period,
                            inputs=payload,
                            consistent=None,
                            note=(
                                "Adjacent SPSF growth is unavailable. Failed "
                                f"requirement: {FAILED_SPSF_GROWTH}."
                            ),
                        )
                    )
                    continue
                spsf_growth_available = True
                rev = _numeric(series.revenue_growth[period])
                consistent = None if rev is None else (rev > 0 and growth > 0)
                spsf_observations.append(
                    RevenueDriverPeriodObservation(
                        period=period,
                        inputs=payload,
                        consistent=consistent,
                        note=(
                            "SPSF growth is an admitted adjacent comparison and "
                            "is not store-only productivity from total-company "
                            "revenue divided by stores."
                        ),
                    )
                )
    elif management_kpi_applicable(financials):
        management = compute_management_kpi_series(financials, axis)
        for identity in management.identities:
            series = management.series[identity]
            if series.family != FAMILY_SALES_PER_SQUARE_FOOT:
                continue
            for index, period in enumerate(axis):
                if index == 0:
                    continue
                growth = _numeric(series.growth[period])
                payload = {
                    "identity": identity,
                    "spsf_growth": series.growth[period],
                    "reported_value": series.reported_value[period],
                }
                spsf_observations.append(
                    RevenueDriverPeriodObservation(
                        period=period,
                        inputs=payload,
                        consistent=None if growth is None else growth > 0,
                        note=(
                            "Adjacent SPSF growth is unavailable."
                            if growth is None
                            else "Admitted adjacent SPSF growth."
                        ),
                    )
                )
                if growth is not None:
                    spsf_growth_available = True
    rps_notes: list[str] = []
    if revenue_per_store_applicable(financials):
        rps = compute_revenue_per_store_series(financials, axis)
        declines = 0
        increases = 0
        for index, period in enumerate(axis):
            if index == 0:
                continue
            change = _numeric(rps.period_end_change[period])
            if change is None:
                continue
            if change < 0:
                declines += 1
            elif change > 0:
                increases += 1
        if increases or declines:
            rps_notes.append(
                f"Period-end Revenue per Store rose in {increases} aligned "
                f"period(s) and declined in {declines}. This identity cannot "
                "independently demonstrate store productivity."
            )
    if not spsf_growth_available:
        finding = (
            "Sales-per-square-foot growth cannot be tested from admitted "
            f"history. Failed requirement: {FAILED_SPSF_GROWTH}. "
            + (" ".join(rps_notes) if rps_notes else "")
        ).strip()
        return RevenueDriverHypothesisTest(
            theme=THEME_PRODUCTIVITY,
            hypothesis=HYPOTHESIS_PRODUCTIVITY,
            mechanism=MECHANISM_PRODUCTIVITY,
            disclosures=disclosures,
            admitted_inputs=inputs,
            periods_tested=(),
            sample_size=0,
            observations=tuple(spsf_observations),
            verdict=VERDICT_INSUFFICIENT,
            finding=finding,
            limitations=tuple(limitations),
            failed_requirement=FAILED_SPSF_GROWTH,
            additional_evidence=ADDITIONAL_SPSF,
            identity_notes=(REVENUE_PER_STORE_SCOPE_NOTE,),
        )
    flags = tuple(item.consistent for item in spsf_observations)
    tested = tuple(
        item.period for item in spsf_observations if item.consistent is not None
    )
    verdict = _verdict_from_consistency(flags)
    return RevenueDriverHypothesisTest(
        theme=THEME_PRODUCTIVITY,
        hypothesis=HYPOTHESIS_PRODUCTIVITY,
        mechanism=MECHANISM_PRODUCTIVITY,
        disclosures=disclosures,
        admitted_inputs=inputs,
        periods_tested=tested,
        sample_size=len(tested),
        observations=tuple(spsf_observations),
        verdict=verdict,
        finding=(
            f"{len(tested)} aligned SPSF-growth observation(s). "
            + (" ".join(rps_notes) if rps_notes else "")
            + f" Verdict: {verdict.replace('_', ' ')}."
        ).strip(),
        limitations=tuple(limitations),
        failed_requirement="",
        additional_evidence="",
        identity_notes=(REVENUE_PER_STORE_SCOPE_NOTE,),
    )


def _geographic_test(
    financials: StandardizedFinancials,
    axis: list[date],
    disclosures: tuple[HistoricalStrategyDisclosure, ...],
) -> RevenueDriverHypothesisTest:
    limitations = [
        "Revenue-growth contributions are an arithmetic decomposition of "
        "reported geographic revenue changes, not organic, constant-currency, "
        "or causal growth.",
        "Reported-currency geographic results are not substituted with "
        "constant-currency disclosures.",
        *_objective_limitation(disclosures),
    ]
    inputs = (
        "admitted geographic segment net revenue",
        "arithmetic contributions to consolidated revenue growth",
        "reported consolidated revenue growth",
    )
    if not geographic_segment_applicable(financials):
        return RevenueDriverHypothesisTest(
            theme=THEME_GEOGRAPHIC_GROWTH,
            hypothesis=HYPOTHESIS_GEOGRAPHIC,
            mechanism=MECHANISM_GEOGRAPHIC,
            disclosures=disclosures,
            admitted_inputs=inputs,
            periods_tested=(),
            sample_size=0,
            observations=(),
            verdict=VERDICT_INSUFFICIENT,
            finding=(
                "Geographic growth cannot be tested: no admitted geographic "
                "segment history is available."
            ),
            limitations=tuple(limitations),
            failed_requirement=FAILED_GEOGRAPHIC,
            additional_evidence=FAILED_GEOGRAPHIC,
            identity_notes=(),
        )
    series = compute_geographic_segment_series(financials, axis)
    observations: list[RevenueDriverPeriodObservation] = []
    flags: list[bool | None] = []
    tested: list[date] = []
    identities = series.identities
    for index, period in enumerate(axis):
        if index == 0:
            continue
        cons = _numeric(series.consolidated_revenue_growth[period])
        period_positive = False
        period_negative = False
        missing = False
        contribs: dict[str, float | str | None] = {
            "consolidated_revenue_growth": series.consolidated_revenue_growth[period]
        }
        for identity in identities:
            value = series.revenue_growth_contribution[period].get(
                identity, SOURCE_UNAVAILABLE
            )
            contribs[identity] = value
            number = _numeric(value)
            if number is None:
                missing = True
                continue
            if number > 0:
                period_positive = True
            elif number < 0:
                period_negative = True
        if cons is None or missing:
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=contribs,
                    consistent=None,
                    note="Missing adjacent geographic contribution or consolidated growth.",
                )
            )
            continue
        consistent = cons > 0 and period_positive
        negative_parts = []
        positive_parts = []
        for identity in identities:
            number = _numeric(contribs[identity])
            if number is None:
                continue
            label = _segment_label(identity)
            if number < 0:
                negative_parts.append(f"{label} {_format_pp(number)}")
            elif number > 0:
                positive_parts.append(f"{label} {_format_pp(number)}")
        if consistent and period_negative:
            note = (
                f"Period-end {period.isoformat()}: consolidated revenue grew "
                f"{_format_ratio_pct(cons)} while {', '.join(negative_parts)} "
                "contributed negatively"
                + (
                    f" and {', '.join(positive_parts)} contributed positively"
                    if positive_parts
                    else ""
                )
                + ". Mix is mixed, not a causal explanation."
            )
            # Mixed period: keep consistent True for "expansion present" but
            # record the counterexample; overall verdict uses mixed if any
            # period has a negative contributor while others are positive.
            flags.append(True)
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=contribs,
                    consistent=True,
                    note=note,
                )
            )
            # Represent mix conflict with an extra False flag so mixed wins
            # when some segments subtract.
            flags.append(False)
        elif consistent:
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=contribs,
                    consistent=True,
                    note=(
                        f"Period-end {period.isoformat()}: consolidated revenue "
                        f"grew {_format_ratio_pct(cons)} and admitted geographic "
                        "contributions were non-negative."
                    ),
                )
            )
            flags.append(True)
        else:
            observations.append(
                RevenueDriverPeriodObservation(
                    period=period,
                    inputs=contribs,
                    consistent=False,
                    note=(
                        f"Period-end {period.isoformat()}: consolidated revenue "
                        f"did not grow with a positive admitted geographic "
                        f"contribution ({_format_ratio_pct(cons)})."
                    ),
                )
            )
            flags.append(False)
        tested.append(period)
    unique_tested = tuple(dict.fromkeys(tested))
    verdict = _verdict_from_consistency(tuple(flags))
    if verdict == VERDICT_INSUFFICIENT:
        finding = (
            "Geographic growth cannot be tested: no aligned contribution "
            "observations exist."
        )
        failed = FAILED_GEOGRAPHIC
        additional = FAILED_GEOGRAPHIC
    else:
        failed = ""
        additional = ""
        finding = _finding_with_counterexamples(
            f"{len(unique_tested)} aligned period(s) and {len(identities)} "
            "admitted geographic identit"
            f"{'y' if len(identities) == 1 else 'ies'}. Findings use reported "
            "currency. Verdict: "
            f"{verdict.replace('_', ' ')}.",
            tuple(observations),
        )
    return RevenueDriverHypothesisTest(
        theme=THEME_GEOGRAPHIC_GROWTH,
        hypothesis=HYPOTHESIS_GEOGRAPHIC,
        mechanism=MECHANISM_GEOGRAPHIC,
        disclosures=disclosures,
        admitted_inputs=inputs,
        periods_tested=unique_tested,
        sample_size=len(unique_tested),
        observations=tuple(observations),
        verdict=verdict,
        finding=finding,
        limitations=tuple(limitations),
        failed_requirement=failed,
        additional_evidence=additional,
        identity_notes=(),
    )


_THEME_BUILDERS = {
    THEME_STORE_EXPANSION: _store_expansion_test,
    THEME_COMPARABLE_SALES: _comparable_sales_test,
    THEME_PRODUCTIVITY: _productivity_test,
    THEME_GEOGRAPHIC_GROWTH: _geographic_test,
}


def compute_revenue_driver_analysis(
    financials: StandardizedFinancials,
    periods: list[date] | None = None,
) -> RevenueDriverAnalysis:
    """Test disclosure-led revenue-driver hypotheses on admitted history."""
    if not revenue_driver_applicable(financials):
        raise MissingLineError("revenue-driver disclosures are not available")
    assert financials.historical_strategy is not None
    if operating_kpi_applicable(financials) or geographic_segment_applicable(financials):
        _require_annual_axis(financials)
    axis = canonical_fiscal_periods(financials)
    if periods is not None and list(periods) != axis:
        raise ValueError("revenue-driver analysis must use the canonical fiscal axis")
    tests: list[RevenueDriverHypothesisTest] = []
    for theme, builder in _THEME_BUILDERS.items():
        disclosures = _disclosures_for(financials.historical_strategy, theme)
        if not disclosures:
            continue
        tests.append(builder(financials, axis, disclosures))
    if not tests:
        raise MissingLineError("revenue-driver disclosures are not available")
    return RevenueDriverAnalysis(
        periods=tuple(axis),
        calculation_kind=CALCULATION_KIND,
        scope_note=SCOPE_NOTE,
        tests=tuple(tests),
    )
