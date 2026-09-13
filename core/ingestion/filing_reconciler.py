"""Deterministic cross-filing reconciliation for ExtractedFiling sets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.filing import (
    ExtractedFiling,
    PresentationRole,
    SupplementalFact,
)
from .filing_validator import FilingValidationReport, source_row_identity

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
    note_facts: tuple[SupplementalFact, ...]
    share_facts: tuple[SupplementalFact, ...]
    omitted_incomplete_axis: tuple[dict, ...] = ()


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


def reconcile_filings(
    filings: list[tuple[ExtractedFiling, FilingValidationReport]],
) -> ReconciledCompanyData:
    """Reconcile validated filings for one company into documentary selections."""
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

    note_facts: list[SupplementalFact] = []
    share_facts: list[SupplementalFact] = []
    for filing, _ in sorted(filings, key=lambda pair: pair[0].filing.fiscal_year):
        note_facts.extend(filing.note_facts)
        share_facts.extend(filing.share_facts)

    return ReconciledCompanyData(
        company_name=company_name,
        ticker=ticker,
        stock_code=stock_code,
        jurisdiction=jurisdiction,
        currency=currency,
        unit_scale=unit_scale,
        periods=model_periods,
        values=tuple(values),
        conflicts=tuple(conflicts),
        note_facts=tuple(note_facts),
        share_facts=tuple(share_facts),
    )
