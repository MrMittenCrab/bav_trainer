"""Tests for deterministic historical diluted-WAS share-basis resolution."""

from __future__ import annotations

from datetime import date

import pytest

from core.data.filing import PresentationRole, SourceRef, SupplementalFact
from core.ingestion.filing_reconciler import (
    FilingObservation,
    ReconciledCompanyData,
    ReconciledValue,
    SupplementalObservation,
)
from core.ingestion.share_basis import (
    resolve_historical_share_basis,
    unit_scale_divisor,
)

P1 = date(2021, 12, 31)
P2 = date(2022, 12, 31)
P3 = date(2023, 12, 31)


def _share(
    fact_type: str,
    period: date,
    value: float,
    *,
    filing_year: int,
    status: str = "reported",
    derivation: str = "",
) -> SupplementalObservation:
    return SupplementalObservation(
        kind="share",
        filing_year=filing_year,
        source_file=f"f{filing_year}.pdf",
        source_sha256="x",
        fact=SupplementalFact(
            fact_type=fact_type,
            period=period,
            value=value,
            status=status,
            source=SourceRef(page=1, note="EPS"),
            derivation=derivation,
        ),
    )


def _obs(
    *,
    filing_year: int,
    value: float,
    role: PresentationRole,
) -> FilingObservation:
    return FilingObservation(
        filing_year=filing_year,
        source_file=f"f{filing_year}.pdf",
        source_sha256="x",
        pdf_page=1,
        presentation_role=role,
        value=value,
    )


def _reconciled(
    *,
    periods: tuple[date, ...] = (P1, P2),
    share_facts: tuple[SupplementalObservation, ...] = (),
    values: tuple[ReconciledValue, ...] = (),
    unit_scale: str = "ones",
) -> ReconciledCompanyData:
    return ReconciledCompanyData(
        company_name="ACME",
        ticker="ACME",
        stock_code="ACME",
        jurisdiction="HK",
        currency="HKD",
        unit_scale=unit_scale,
        periods=periods,
        values=values,
        conflicts=(),
        note_facts=(),
        share_facts=share_facts,
    )


def test_reported_axis_no_split():
    facts = (
        _share("diluted_weighted_average_shares", P1, 100.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
    )
    result = resolve_historical_share_basis(_reconciled(share_facts=facts))
    assert result is not None
    assert result.basis == "reported"
    assert result.split_factor is None
    assert result.restatement_anchor_period is None
    assert result.restatement_filing_year is None
    assert result.applied_adjustment_factors == {P1: 1.0, P2: 1.0}
    assert result.diluted_weighted_average_actual_shares == {P1: 100.0, P2: 110.0}


def test_valid_derived_diluted_was_accepted():
    facts = (
        _share("basic_weighted_average_shares", P1, 100.0, filing_year=2021),
        _share("dilutive_shares", P1, 5.0, filing_year=2021),
        _share(
            "diluted_weighted_average_shares",
            P1,
            105.0,
            filing_year=2021,
            status="derived",
            derivation="basic_weighted_average_shares + dilutive_shares",
        ),
        _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
    )
    result = resolve_historical_share_basis(_reconciled(share_facts=facts))
    assert result is not None
    assert result.diluted_weighted_average_actual_shares[P1] == 105.0
    assert result.basis == "reported"


@pytest.mark.parametrize(
    "bad_facts",
    [
        # wrong derivation string
        (
            _share("basic_weighted_average_shares", P1, 100.0, filing_year=2021),
            _share("dilutive_shares", P1, 5.0, filing_year=2021),
            _share(
                "diluted_weighted_average_shares",
                P1,
                105.0,
                filing_year=2021,
                status="derived",
                derivation="invented",
            ),
            _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
        ),
        # missing basic
        (
            _share("dilutive_shares", P1, 5.0, filing_year=2021),
            _share(
                "diluted_weighted_average_shares",
                P1,
                105.0,
                filing_year=2021,
                status="derived",
                derivation="basic_weighted_average_shares + dilutive_shares",
            ),
            _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
        ),
        # missing dilutive
        (
            _share("basic_weighted_average_shares", P1, 100.0, filing_year=2021),
            _share(
                "diluted_weighted_average_shares",
                P1,
                105.0,
                filing_year=2021,
                status="derived",
                derivation="basic_weighted_average_shares + dilutive_shares",
            ),
            _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
        ),
        # component status != reported
        (
            _share(
                "basic_weighted_average_shares",
                P1,
                100.0,
                filing_year=2021,
                status="derived",
            ),
            _share("dilutive_shares", P1, 5.0, filing_year=2021),
            _share(
                "diluted_weighted_average_shares",
                P1,
                105.0,
                filing_year=2021,
                status="derived",
                derivation="basic_weighted_average_shares + dilutive_shares",
            ),
            _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
        ),
        # derived total != basic + dilutive
        (
            _share("basic_weighted_average_shares", P1, 100.0, filing_year=2021),
            _share("dilutive_shares", P1, 5.0, filing_year=2021),
            _share(
                "diluted_weighted_average_shares",
                P1,
                999.0,
                filing_year=2021,
                status="derived",
                derivation="basic_weighted_average_shares + dilutive_shares",
            ),
            _share("diluted_weighted_average_shares", P2, 110.0, filing_year=2022),
        ),
    ],
)
def test_invalid_derived_diluted_was_fails_closed(bad_facts):
    assert resolve_historical_share_basis(_reconciled(share_facts=bad_facts)) is None


def _restatement_values(
    *,
    old_eps: float = 30.0,
    new_eps: float = 10.0,
    period: date = P2,
) -> tuple[ReconciledValue, ...]:
    old = _obs(
        filing_year=2022,
        value=old_eps,
        role=PresentationRole.CURRENT_PERIOD,
    )
    new = _obs(
        filing_year=2023,
        value=new_eps,
        role=PresentationRole.RESTATED_COMPARATIVE,
    )
    return (
        ReconciledValue(
            statement="income_statement",
            row_identity="income_statement||diluted|diluted_eps",
            period=period,
            label="Diluted EPS",
            section="",
            suggested_concept="diluted_eps",
            selected=new,
            observations=(old, new),
        ),
    )


def test_audited_restatement_anchor_infers_integer_split():
    facts = (
        _share("diluted_weighted_average_shares", P1, 90.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("basic_weighted_average_shares", P2, 95.0, filing_year=2022),
        _share("basic_weighted_average_shares", P2, 285.0, filing_year=2023),
        _share("dilutive_shares", P2, 5.0, filing_year=2022),
        _share("dilutive_shares", P2, 15.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    result = resolve_historical_share_basis(
        _reconciled(
            periods=(P1, P2, P3),
            share_facts=facts,
            values=_restatement_values(),
        )
    )
    assert result is not None
    assert result.basis == "split_adjusted"
    assert result.split_factor == 3.0
    assert result.restatement_anchor_period == P2
    assert result.restatement_filing_year == 2023
    assert result.diluted_weighted_average_actual_shares == {
        P1: 270.0,
        P2: 300.0,
        P3: 330.0,
    }
    assert result.applied_adjustment_factors == {P1: 3.0, P2: 1.0, P3: 1.0}


def test_disagreement_without_restated_eps_fails():
    facts = (
        _share("diluted_weighted_average_shares", P1, 90.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(periods=(P1, P2, P3), share_facts=facts, values=())
        )
        is None
    )


def test_non_integer_share_ratio_fails():
    facts = (
        _share("diluted_weighted_average_shares", P1, 90.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 270.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(
                periods=(P1, P2, P3),
                share_facts=facts,
                values=_restatement_values(old_eps=27.0, new_eps=10.0),
            )
        )
        is None
    )


def test_eps_ratio_does_not_support_factor_fails():
    facts = (
        _share("diluted_weighted_average_shares", P1, 90.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("basic_weighted_average_shares", P2, 95.0, filing_year=2022),
        _share("basic_weighted_average_shares", P2, 285.0, filing_year=2023),
        _share("dilutive_shares", P2, 5.0, filing_year=2022),
        _share("dilutive_shares", P2, 15.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(
                periods=(P1, P2, P3),
                share_facts=facts,
                # 30 / 20 = 1.5, not 3
                values=_restatement_values(old_eps=30.0, new_eps=20.0),
            )
        )
        is None
    )


def test_component_evidence_contradicts_factor_fails():
    facts = (
        _share("diluted_weighted_average_shares", P1, 90.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("basic_weighted_average_shares", P2, 95.0, filing_year=2022),
        _share("basic_weighted_average_shares", P2, 200.0, filing_year=2023),  # not ×3
        _share("dilutive_shares", P2, 5.0, filing_year=2022),
        _share("dilutive_shares", P2, 15.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(
                periods=(P1, P2, P3),
                share_facts=facts,
                values=_restatement_values(),
            )
        )
        is None
    )


def test_multiple_distinct_split_factors_fail():
    p4 = date(2024, 12, 31)
    facts = (
        _share("diluted_weighted_average_shares", P1, 50.0, filing_year=2020),
        _share("diluted_weighted_average_shares", P1, 100.0, filing_year=2021),
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("basic_weighted_average_shares", P1, 48.0, filing_year=2020),
        _share("basic_weighted_average_shares", P1, 96.0, filing_year=2021),
        _share("dilutive_shares", P1, 2.0, filing_year=2020),
        _share("dilutive_shares", P1, 4.0, filing_year=2021),
        _share("basic_weighted_average_shares", P2, 95.0, filing_year=2022),
        _share("basic_weighted_average_shares", P2, 285.0, filing_year=2023),
        _share("dilutive_shares", P2, 5.0, filing_year=2022),
        _share("dilutive_shares", P2, 15.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
        _share("diluted_weighted_average_shares", p4, 340.0, filing_year=2024),
    )
    p1_old = _obs(filing_year=2020, value=20.0, role=PresentationRole.CURRENT_PERIOD)
    p1_new = _obs(
        filing_year=2021, value=10.0, role=PresentationRole.RESTATED_COMPARATIVE
    )
    values = (
        ReconciledValue(
            statement="income_statement",
            row_identity="income_statement||diluted|diluted_eps",
            period=P1,
            label="Diluted EPS",
            section="",
            suggested_concept="diluted_eps",
            selected=p1_new,
            observations=(p1_old, p1_new),
        ),
        *_restatement_values(),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(
                periods=(P1, P2, P3, p4),
                share_facts=facts,
                values=values,
            )
        )
        is None
    )


def test_missing_period_share_observation_fails():
    facts = (
        _share("diluted_weighted_average_shares", P2, 100.0, filing_year=2022),
        _share("diluted_weighted_average_shares", P2, 300.0, filing_year=2023),
        _share("diluted_weighted_average_shares", P3, 330.0, filing_year=2023),
    )
    assert (
        resolve_historical_share_basis(
            _reconciled(
                periods=(P1, P2, P3),
                share_facts=facts,
                values=_restatement_values(),
            )
        )
        is None
    )


@pytest.mark.parametrize(
    "unit_scale,divisor",
    [
        ("ones", 1.0),
        ("thousands", 1_000.0),
        ("millions", 1_000_000.0),
        ("billions", 1_000_000_000.0),
    ],
)
def test_unit_scale_divisors(unit_scale, divisor):
    assert unit_scale_divisor(unit_scale) == divisor
    assert 307_247_804 / unit_scale_divisor("millions") == pytest.approx(307.247804)
