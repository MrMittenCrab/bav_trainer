"""Deterministic cross-filing reconciliation for ExtractedFiling sets."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from ..data.filing import (
    ExtractedFiling,
    PresentationRole,
    SupplementalFact,
)
from .filing_validator import FilingValidationReport, source_row_identity

_REQUIRED_STATEMENTS = ("income_statement", "balance_sheet", "cash_flow")

ROLE_RANK = {
    PresentationRole.RESTATED_COMPARATIVE: 3,
    PresentationRole.CURRENT_PERIOD: 2,
    PresentationRole.COMPARATIVE: 2,
    PresentationRole.PRIOR_PRESENTATION: 1,
}


@dataclass(frozen=True)
class FilingObservation:
    filing_year: int
    source_file: str
    source_sha256: str
    pdf_page: int
    presentation_role: PresentationRole
    value: float


@dataclass(frozen=True)
class ReconciledValue:
    statement: str
    row_identity: str
    period: date
    label: str
    section: str
    suggested_concept: str
    selected: FilingObservation
    observations: tuple[FilingObservation, ...]


@dataclass(frozen=True)
class ReconciliationConflict:
    statement: str
    row_identity: str
    period: date
    observations: tuple[FilingObservation, ...]
    selected: FilingObservation
    reason: str


@dataclass(frozen=True)
class SupplementalObservation:
    kind: str  # "note" | "share"
    filing_year: int
    source_file: str
    source_sha256: str
    fact: SupplementalFact


@dataclass(frozen=True)
class SupplementalConflict:
    kind: str
    fact_type: str
    period: date
    observations: tuple[SupplementalObservation, ...]
    reason: str


@dataclass(frozen=True)
class SelectedOperatingKpiFact:
    fact_type: str
    metric: str
    population: str
    period: date
    value: float
    unit: str
    filing_year: int
    source_file: str
    source_sha256: str
    pdf_page: int
    presentation_basis: str
    selection_reason: str
    source_note: str = ""
    source_label: str = ""


@dataclass(frozen=True)
class SelectedGeographicFact:
    fact_type: str
    period: date
    value: float
    filing_year: int
    source_file: str
    source_sha256: str
    pdf_page: int
    presentation_basis: str
    selection_reason: str
    presentation_family: str = ""
    source_note: str = ""
    source_label: str = ""


@dataclass(frozen=True)
class BoundSourceFile:
    filing_year: int
    source_file: str
    source_sha256: str


@dataclass(frozen=True)
class ReconciledCompanyData:
    company_name: str
    ticker: str
    stock_code: str
    jurisdiction: str
    currency: str
    unit_scale: str
    periods: tuple[date, ...]
    values: tuple[ReconciledValue, ...]
    conflicts: tuple[ReconciliationConflict, ...]
    note_facts: tuple[SupplementalObservation, ...]
    share_facts: tuple[SupplementalObservation, ...]
    supplemental_conflicts: tuple[SupplementalConflict, ...] = ()
    selected_geographic_facts: tuple[SelectedGeographicFact, ...] = ()
    selected_operating_kpi_facts: tuple[SelectedOperatingKpiFact, ...] = ()
    source_files: tuple[BoundSourceFile, ...] = ()
    omitted_incomplete_axis: tuple[dict, ...] = ()
    requested_admit_periods: tuple[date, ...] = ()
    admitted_comparative_periods: tuple[date, ...] = ()
    excluded_comparative_periods: tuple[date, ...] = ()
    management_admission: object | None = None


def _select_observation(
    observations: list[FilingObservation],
) -> tuple[FilingObservation, str]:
    ranked = sorted(
        observations,
        key=lambda o: (ROLE_RANK[o.presentation_role], o.filing_year),
        reverse=True,
    )
    selected = ranked[0]
    # Determine reason among disagreeing observations
    values = {o.value for o in observations}
    if len(values) == 1:
        return selected, "agreeing_observations"
    if selected.presentation_role == PresentationRole.RESTATED_COMPARATIVE:
        return selected, "restated_comparative_precedence"
    if any(o.presentation_role == PresentationRole.PRIOR_PRESENTATION for o in observations):
        # selected should still be non-prior if available
        return selected, "later_audited_presentation"
    return selected, "later_audited_presentation"


def _supplemental_sort_key(obs: SupplementalObservation) -> tuple:
    return (
        obs.kind,
        obs.fact.fact_type,
        obs.fact.period.isoformat(),
        obs.filing_year,
        obs.source_file,
        obs.fact.source.page,
    )


def _group_supplemental_conflicts(
    observations: tuple[SupplementalObservation, ...],
) -> tuple[SupplementalConflict, ...]:
    buckets: dict[tuple[str, str, date], list[SupplementalObservation]] = defaultdict(list)
    for obs in observations:
        if obs.fact.status != "reported":
            continue
        buckets[(obs.kind, obs.fact.fact_type, obs.fact.period)].append(obs)

    conflicts: list[SupplementalConflict] = []
    for (kind, fact_type, period), items in sorted(
        buckets.items(),
        key=lambda item: (item[0][0], item[0][1], item[0][2].isoformat()),
    ):
        distinct = {float(item.fact.value) for item in items}
        if len(distinct) <= 1:
            continue
        ordered = tuple(sorted(items, key=_supplemental_sort_key))
        conflicts.append(
            SupplementalConflict(
                kind=kind,
                fact_type=fact_type,
                period=period,
                observations=ordered,
                reason="cross_filing_supplemental_disagreement",
            )
        )
    return tuple(conflicts)


def _parse_admit_periods(
    admit_periods: Iterable[date] | None,
) -> tuple[date, ...]:
    if not admit_periods:
        return ()
    return tuple(sorted(set(admit_periods)))


def _statement_coverage(
    buckets: dict[tuple[str, str, date], list],
) -> dict[date, set[str]]:
    coverage: dict[date, set[str]] = defaultdict(set)
    for statement, _ident, period in buckets:
        coverage[period].add(statement)
    return coverage


def _validate_comparative_admission(
    *,
    requested: tuple[date, ...],
    filing_year_ends: set[date],
    coverage: dict[date, set[str]],
) -> tuple[date, ...]:
    """Return comparative dates to add; reject missing-statement or unknown dates."""
    observed = set(coverage)
    admitted: list[date] = []
    for period in requested:
        if period in filing_year_ends:
            continue
        if period not in observed:
            raise ValueError(
                f"unsupported comparative period {period.isoformat()}: "
                "not present in documentary observations"
            )
        missing = [
            statement
            for statement in _REQUIRED_STATEMENTS
            if statement not in coverage.get(period, set())
        ]
        if missing:
            raise ValueError(
                f"cannot admit comparative period {period.isoformat()}: "
                f"missing selected {'/'.join(missing)} coverage"
            )
        admitted.append(period)
    return tuple(admitted)


def reconcile_filings(
    filings: list[tuple[ExtractedFiling, FilingValidationReport]],
    *,
    admit_periods: Iterable[date] | None = None,
    management_documents: tuple | None = None,
) -> ReconciledCompanyData:
    """Reconcile validated filings for one company into documentary selections.

    Default model periods are filing year-ends. ``admit_periods`` may add
    comparative dates that already have selected IS, BS, and CF coverage.
    """
    if not filings:
        raise ValueError("reconcile_filings requires at least one filing")
    for filing, report in filings:
        if not report.ok:
            raise ValueError("cannot reconcile filings with validation errors")
        if report.computed_source_sha256 is None:
            raise ValueError(
                "reconcile_filings requires computed_source_sha256 from validation "
                "with source_root"
            )

    base_filing = filings[0][0]
    company_name = base_filing.company_name
    ticker = base_filing.ticker
    stock_code = base_filing.stock_code
    jurisdiction = base_filing.jurisdiction
    currency = base_filing.filing.currency
    unit_scale = base_filing.filing.unit_scale

    for filing, _ in filings[1:]:
        if (
            filing.company_name != company_name
            or filing.ticker != ticker
            or filing.stock_code != stock_code
        ):
            raise ValueError("filings disagree on company/ticker identity")
        if filing.filing.currency != currency:
            raise ValueError("filings disagree on currency")
        if filing.filing.unit_scale != unit_scale:
            raise ValueError("filings disagree on unit_scale")
        if filing.jurisdiction != jurisdiction:
            raise ValueError("filings disagree on jurisdiction")

    # Collect observations keyed by (statement, identity, period)
    buckets: dict[tuple[str, str, date], list[tuple[FilingObservation, str, str, str]]] = {}
    meta_by_key: dict[tuple[str, str], tuple[str, str, str]] = {}

    for filing, report in filings:
        sha = report.computed_source_sha256 or ""
        year = filing.filing.fiscal_year
        source_file = filing.filing.source_file
        for statement, rows in (
            ("income_statement", filing.income_statement),
            ("balance_sheet", filing.balance_sheet),
            ("cash_flow", filing.cash_flow),
        ):
            for row in rows:
                ident = source_row_identity(statement, row)
                meta_by_key[(statement, ident)] = (
                    row.label,
                    row.section,
                    row.suggested_concept,
                )
                for period, fval in row.values.items():
                    obs = FilingObservation(
                        filing_year=year,
                        source_file=source_file,
                        source_sha256=sha,
                        pdf_page=row.source.page,
                        presentation_role=fval.presentation_role,
                        value=float(fval.value),
                    )
                    key = (statement, ident, period)
                    buckets.setdefault(key, []).append(
                        (obs, row.label, row.section, row.suggested_concept)
                    )

    model_periods = tuple(
        sorted({filing.filing.period_end for filing, _ in filings})
    )
    requested_admit = _parse_admit_periods(admit_periods)
    coverage = _statement_coverage(buckets)
    admitted = _validate_comparative_admission(
        requested=requested_admit,
        filing_year_ends=set(model_periods),
        coverage=coverage,
    )
    if admitted:
        model_periods = tuple(sorted({*model_periods, *admitted}))
    excluded = tuple(sorted(set(coverage) - set(model_periods)))
    values: list[ReconciledValue] = []
    conflicts: list[ReconciliationConflict] = []

    for key in sorted(buckets, key=lambda k: (k[0], k[1], k[2].isoformat())):
        statement, ident, period = key
        entries = buckets[key]
        observations = tuple(
            sorted(entries, key=lambda e: (e[0].filing_year, e[0].source_file))
        )
        obs_only = [e[0] for e in observations]
        # prior_presentation must never override current/comparative/restated
        non_prior = [
            o
            for o in obs_only
            if o.presentation_role != PresentationRole.PRIOR_PRESENTATION
        ]
        candidates = non_prior if non_prior else list(obs_only)
        selected, reason = _select_observation(candidates)
        label, section, concept = meta_by_key[(statement, ident)]
        # Prefer label/section from selected filing observation's entry
        for obs, lab, sec, conc in observations:
            if obs == selected:
                label, section, concept = lab, sec, conc
                break
        values.append(
            ReconciledValue(
                statement=statement,
                row_identity=ident,
                period=period,
                label=label,
                section=section,
                suggested_concept=concept,
                selected=selected,
                observations=tuple(obs_only),
            )
        )
        distinct = {o.value for o in obs_only}
        if len(distinct) > 1:
            conflicts.append(
                ReconciliationConflict(
                    statement=statement,
                    row_identity=ident,
                    period=period,
                    observations=tuple(obs_only),
                    selected=selected,
                    reason=reason
                    if reason != "agreeing_observations"
                    else "later_audited_presentation",
                )
            )

    note_facts: list[SupplementalObservation] = []
    share_facts: list[SupplementalObservation] = []
    for filing, report in sorted(filings, key=lambda pair: pair[0].filing.fiscal_year):
        sha = report.computed_source_sha256 or ""
        year = filing.filing.fiscal_year
        source_file = filing.filing.source_file
        for fact in filing.note_facts:
            note_facts.append(
                SupplementalObservation(
                    kind="note",
                    filing_year=year,
                    source_file=source_file,
                    source_sha256=sha,
                    fact=fact,
                )
            )
        for fact in filing.share_facts:
            share_facts.append(
                SupplementalObservation(
                    kind="share",
                    filing_year=year,
                    source_file=source_file,
                    source_sha256=sha,
                    fact=fact,
                )
            )

    note_facts_t = tuple(sorted(note_facts, key=_supplemental_sort_key))
    share_facts_t = tuple(sorted(share_facts, key=_supplemental_sort_key))
    supplemental_conflicts = _group_supplemental_conflicts(
        (*note_facts_t, *share_facts_t)
    )
    from .geographic_segment import select_geographic_segment_facts
    from .operating_kpi import select_operating_kpi_facts

    values_t = tuple(values)
    selected_geographic_facts = select_geographic_segment_facts(
        note_facts_t,
        reconciled_values=values_t,
        model_periods=model_periods,
    )
    selected_operating_kpi_facts = select_operating_kpi_facts(note_facts_t)
    if management_documents is None:
        management_documents = tuple(
            getattr(filings, "management_documents", ()) or ()
        )
    management_admission = None
    if management_documents:
        from .management_kpi import admit_management_documents

        management_admission = admit_management_documents(
            tuple(management_documents),
            selected_store_facts=selected_operating_kpi_facts,
        )
    # Explicit registry of every validated bound source — not derived from
    # selected statement observations (losers and supplemental-only stay).
    source_files = tuple(
        sorted(
            (
                BoundSourceFile(
                    filing_year=filing.filing.fiscal_year,
                    source_file=filing.filing.source_file,
                    source_sha256=report.computed_source_sha256 or "",
                )
                for filing, report in filings
            ),
            key=lambda s: (s.filing_year, s.source_file, s.source_sha256),
        )
    )

    return ReconciledCompanyData(
        company_name=company_name,
        ticker=ticker,
        stock_code=stock_code,
        jurisdiction=jurisdiction,
        currency=currency,
        unit_scale=unit_scale,
        periods=model_periods,
        values=values_t,
        conflicts=tuple(conflicts),
        note_facts=note_facts_t,
        share_facts=share_facts_t,
        supplemental_conflicts=supplemental_conflicts,
        selected_geographic_facts=selected_geographic_facts,
        selected_operating_kpi_facts=selected_operating_kpi_facts,
        source_files=source_files,
        requested_admit_periods=requested_admit,
        admitted_comparative_periods=admitted,
        excluded_comparative_periods=excluded,
        management_admission=management_admission,
    )
