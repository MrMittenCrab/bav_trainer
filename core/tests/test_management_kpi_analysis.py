"""Comparable management-KPI historical analytics."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.historical_operating_kpis import (
    UNIT_PERCENT,
    UNIT_USD_PER_SQUARE_FOOT,
    encode_metric_identity,
    management_identity_fields,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_standardizer import (
    reconciliation_conflicts_payload,
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.ingestion.management_kpi import management_admission_payload
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    POP_STORES_AND_ECOMMERCE,
)
from core.model.line_resolver import MissingLineError
from core.model.management_kpi import (
    MANAGEMENT_KPI_RATIO_TOLERANCE,
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
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.operating_kpi_relationships import (
    compute_operating_kpi_revenue_store_relationship,
    operating_kpi_revenue_store_relationship_applicable,
)
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, ratio_or_na
from core.tests.test_historical_segment import _base_payload
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    _bytes_by_name,
    _canonicalize,
    _copy_json,
    _statement_provenance,
)
from core.tests.test_management_kpi_history import (
    DEF_A,
    DEF_B,
    _assert_export_reload_export,
    _management_rows,
    _reconcile,
    _write_selected_on_docs,
)
from core.tests.test_management_kpi_identity import REPORTING_BASIS_52, REPORTING_BASIS_53
from core.tests.test_operating_kpi_analysis import _assert_series_matches, _independent_from_counts
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2023,
    P2024,
    P2025,
    _fin_with_operating_kpis,
    _kpi_model_observation,
    _prepare_augmented,
)
from core.tests.test_operating_kpi_management_history import (
    AXIS,
    DEF_COMPSALES_A,
    DEF_SPSF,
    _both_family_fin,
    _both_family_observations,
    _compsales,
    _spsf,
)

P0 = date(2023, 12, 31)
P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _identity_of(item) -> str:
    return encode_metric_identity(management_identity_fields(item))


def _series_for(result, item):
    return result.series[_identity_of(item)]


def _independent_identity(
    axis: list[date],
    observations: dict[date, object],
    *,
    family: str,
) -> dict[date, dict[str, object]]:
    compute_growth = family == FAMILY_SALES_PER_SQUARE_FOOT
    expected: dict[date, dict[str, object]] = {}
    for index, period in enumerate(axis):
        opening = index == 0
        current = observations.get(period)
        prior = None if opening else observations.get(axis[index - 1])
        if current is None:
            row = {
                "value": SOURCE_UNAVAILABLE,
                "unit": SOURCE_UNAVAILABLE,
                "definition_text": SOURCE_UNAVAILABLE,
                "change": None if opening else SOURCE_UNAVAILABLE,
                "growth": None if opening or not compute_growth else SOURCE_UNAVAILABLE,
                "reasons": None if opening else (REASON_MISSING_OBSERVATION,),
            }
            expected[period] = row
            continue
        value = float(current.value)
        if opening:
            change: float | str | None = None
            growth: float | str | None = None
            reasons: tuple[str, ...] | None = None
        elif prior is None:
            change = SOURCE_UNAVAILABLE
            growth = None if not compute_growth else SOURCE_UNAVAILABLE
            reasons = (REASON_MISSING_PRIOR_OBSERVATION,)
        else:
            mismatches: list[str] = []
            if current.definition_text != prior.definition_text:
                mismatches.append(REASON_DEFINITION_MISMATCH)
            if current.period_kind != prior.period_kind:
                mismatches.append(REASON_PERIOD_KIND_MISMATCH)
            if current.calendar_week_adjustment != prior.calendar_week_adjustment:
                mismatches.append(REASON_CALENDAR_WEEK_MISMATCH)
            if current.calendar_reporting_basis != prior.calendar_reporting_basis:
                mismatches.append(REASON_CALENDAR_REPORTING_MISMATCH)
            if dict(current.qualifiers) != dict(prior.qualifiers):
                mismatches.append(REASON_QUALIFIER_MISMATCH)
            if mismatches:
                change = SOURCE_UNAVAILABLE
                growth = None if not compute_growth else SOURCE_UNAVAILABLE
                reasons = tuple(mismatches)
            else:
                change = value - float(prior.value)
                growth = ratio_or_na(change, float(prior.value)) if compute_growth else None
                reasons = None
        expected[period] = {
            "value": value,
            "unit": current.unit,
            "definition_text": current.definition_text,
            "change": change,
            "growth": growth,
            "reasons": reasons,
        }
    return expected


def _assert_identity_matches(series, expected, *, family: str) -> None:
    assert series.family == family
    assert series.periods == tuple(expected)
    for period, row in expected.items():
        assert series.reported_value[period] == row["value"]
        assert series.reported_unit[period] == row["unit"]
        assert series.definition_text[period] == row["definition_text"]
        assert series.adjacent_change[period] == row["change"]
        growth = series.growth[period]
        expected_growth = row["growth"]
        if isinstance(growth, float) and isinstance(expected_growth, float):
            assert abs(growth - expected_growth) <= MANAGEMENT_KPI_RATIO_TOLERANCE
        else:
            assert growth == expected_growth
        assert series.unavailable_reasons[period] == row["reasons"]


def _fin_with_management(*items, extra_periods=None, units="USD in Thousands", stores=()):
    return _fin_with_operating_kpis(
        *stores,
        management=list(items),
        extra_periods=extra_periods,
        units=units,
    )


def test_absent_null_and_store_only_have_no_management_module():
    payload = _base_payload()
    absent = standardized_from_payload(payload)
    assert management_kpi_applicable(absent) is False
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(absent)

    payload["historical_operating_kpis"] = None
    null = standardized_from_payload(payload)
    assert management_kpi_applicable(null) is False
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(null)

    store = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    assert operating_kpi_applicable(store) is True
    assert management_kpi_applicable(store) is False
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(store)
    compute_operating_kpi_series(store)


def test_management_only_does_not_activate_store_module():
    fin = _both_family_fin()
    assert management_kpi_applicable(fin) is True
    assert operating_kpi_applicable(fin) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(fin)
    result = compute_management_kpi_series(fin)
    assert result.periods == tuple(AXIS)
    assert result.identities
    assert all(item.family in {FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT} for item in result.series.values())


def test_comparable_sales_retains_signed_percent_and_percentage_point_change():
    items = (
        _compsales(period=P0, value=-3.0),
        _compsales(period=P1, value=0.0),
        _compsales(period=P2, value=2.0),
    )
    fin = _fin_with_management(*items, extra_periods=[P0, P1, P2])
    before = copy.deepcopy(fin.historical_operating_kpis)
    result = compute_management_kpi_series(fin)
    series = _series_for(result, items[0])
    expected = _independent_identity(
        [P0, P1, P2],
        {item.period: item for item in items},
        family=FAMILY_COMPARABLE_SALES_GROWTH,
    )
    _assert_identity_matches(series, expected, family=FAMILY_COMPARABLE_SALES_GROWTH)
    assert series.reported_value[P0] == -3.0
    assert series.reported_unit[P0] == UNIT_PERCENT
    assert series.adjacent_change[P0] is None
    assert series.growth[P0] is None
    assert series.adjacent_change[P1] == 3.0
    assert series.adjacent_change[P2] == 2.0
    assert series.growth[P1] is None
    assert series.growth[P2] is None
    skipped = ratio_or_na(2.0 - (-3.0), -3.0)
    assert series.adjacent_change[P2] != skipped
    assert fin.historical_operating_kpis == before


def test_sales_per_square_foot_absolute_change_and_fractional_growth():
    items = (
        _spsf(period=P0, value=1407.5),
        _spsf(period=P1, value=0.0),
        _spsf(period=P2, value=1426.0),
    )
    declining = (
        _spsf(period=P1, value=1426.0),
        _spsf(period=P2, value=1400.0),
    )
    zero_prior = _fin_with_management(*items[1:], extra_periods=[P1, P2])
    mixed = _fin_with_management(*items, extra_periods=[P0, P1, P2])
    decline = _fin_with_management(*declining, extra_periods=[P1, P2])
    zero_series = _series_for(compute_management_kpi_series(zero_prior), items[1])
    mixed_series = _series_for(compute_management_kpi_series(mixed), items[0])
    decline_series = _series_for(compute_management_kpi_series(decline), declining[0])
    _assert_identity_matches(
        zero_series,
        _independent_identity(
            [P1, P2],
            {item.period: item for item in items[1:]},
            family=FAMILY_SALES_PER_SQUARE_FOOT,
        ),
        family=FAMILY_SALES_PER_SQUARE_FOOT,
    )
    _assert_identity_matches(
        mixed_series,
        _independent_identity(
            [P0, P1, P2],
            {item.period: item for item in items},
            family=FAMILY_SALES_PER_SQUARE_FOOT,
        ),
        family=FAMILY_SALES_PER_SQUARE_FOOT,
    )
    assert mixed_series.reported_unit[P0] == UNIT_USD_PER_SQUARE_FOOT
    assert mixed_series.adjacent_change[P1] == -1407.5
    assert mixed_series.growth[P1] == pytest.approx(-1407.5 / 1407.5)
    assert mixed_series.adjacent_change[P2] == 1426.0
    assert mixed_series.growth[P2] == UNDEFINED_RATIO
    assert decline_series.adjacent_change[P2] == -26.0
    assert decline_series.growth[P2] == pytest.approx(-26.0 / 1426.0)
    thousands = _fin_with_management(*declining, extra_periods=[P1, P2], units="USD in Thousands")
    millions = _fin_with_management(*declining, extra_periods=[P1, P2], units="USD in Millions")
    left = _series_for(compute_management_kpi_series(thousands), declining[0])
    right = _series_for(compute_management_kpi_series(millions), declining[0])
    assert left.reported_value == right.reported_value
    assert left.adjacent_change == right.adjacent_change
    assert left.growth == right.growth
    assert thousands.units != millions.units


def test_singleton_and_sparse_histories_do_not_compress_or_substitute():
    singleton = _fin_with_management(_compsales(period=P2, value=4.0), extra_periods=[P2])
    single = _series_for(compute_management_kpi_series(singleton), _compsales(period=P2, value=4.0))
    assert single.reported_value[P2] == 4.0
    assert single.adjacent_change[P2] is None
    assert single.growth[P2] is None
    assert single.unavailable_reasons[P2] is None

    items = (
        _spsf(period=P0, value=1400.0),
        _spsf(period=P2, value=1426.0),
    )
    sparse = _fin_with_management(*items, extra_periods=[P0, P1, P2])
    series = _series_for(compute_management_kpi_series(sparse), items[0])
    expected = _independent_identity(
        [P0, P1, P2],
        {item.period: item for item in items},
        family=FAMILY_SALES_PER_SQUARE_FOOT,
    )
    _assert_identity_matches(series, expected, family=FAMILY_SALES_PER_SQUARE_FOOT)
    assert series.reported_value[P0] == 1400.0
    assert series.reported_value[P1] == SOURCE_UNAVAILABLE
    assert series.adjacent_change[P1] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P1] == (REASON_MISSING_OBSERVATION,)
    assert series.reported_value[P2] == 1426.0
    assert series.adjacent_change[P2] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P2] == (REASON_MISSING_PRIOR_OBSERVATION,)
    skipped = 1426.0 - 1400.0
    assert series.adjacent_change[P2] != skipped


def test_multiple_identities_sharing_dates_remain_separate():
    global_reported = (
        _compsales(period=P1, value=-1.0, geography="global", basis="reported"),
        _compsales(period=P2, value=3.0, geography="global", basis="reported"),
    )
    americas = (
        _compsales(period=P1, value=4.0, geography="americas", basis="reported"),
        _compsales(period=P2, value=6.0, geography="americas", basis="reported"),
    )
    spsf = (
        _spsf(period=P1, value=100.0),
        _spsf(period=P2, value=125.0),
    )
    fin = _fin_with_management(*global_reported, *americas, *spsf, extra_periods=[P1, P2])
    result = compute_management_kpi_series(fin)
    assert len(result.identities) == 3
    global_series = _series_for(result, global_reported[0])
    americas_series = _series_for(result, americas[0])
    spsf_series = _series_for(result, spsf[0])
    assert global_series.adjacent_change[P2] == 4.0
    assert americas_series.adjacent_change[P2] == 2.0
    assert spsf_series.adjacent_change[P2] == 25.0
    assert spsf_series.growth[P2] == pytest.approx(0.25)
    assert global_series.growth[P2] is None
    assert global_series.identity != americas_series.identity != spsf_series.identity


def test_shuffled_observations_are_deterministic():
    items = _both_family_observations()
    fin = _fin_with_management(*items, extra_periods=AXIS)
    before = copy.deepcopy(fin.historical_operating_kpis)
    first = compute_management_kpi_series(fin)
    fin.historical_operating_kpis.management_observations = list(
        reversed(list(fin.historical_operating_kpis.management_observations))
    )
    second = compute_management_kpi_series(fin)
    assert first == second
    assert [item.period for item in fin.historical_operating_kpis.management_observations] == list(
        reversed([item.period for item in before.management_observations])
    )


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("definition_text", DEF_COMPSALES_A + " later", REASON_DEFINITION_MISMATCH),
        ("period_kind", "fiscal_year", REASON_PERIOD_KIND_MISMATCH),
        ("calendar_week_adjustment", "excluded", REASON_CALENDAR_WEEK_MISMATCH),
        ("calendar_reporting_basis", "53_week", REASON_CALENDAR_REPORTING_MISMATCH),
        ("qualifiers", {"note": "changed"}, REASON_QUALIFIER_MISMATCH),
    ],
)
def test_each_semantic_discontinuity_blocks_comparisons_independently(field, value, reason):
    prior = _compsales(period=P1, value=2.0)
    current = _compsales(period=P2, value=5.0, **{field: value})
    fin = _fin_with_management(prior, current, extra_periods=[P1, P2])
    if field == "period_kind":
        original = copy.deepcopy(fin.historical_operating_kpis)
        with pytest.raises(ValueError, match="period_kind must be"):
            compute_management_kpi_series(fin)
        assert fin.historical_operating_kpis == original
        return
    series = _series_for(compute_management_kpi_series(fin), prior)
    assert series.reported_value[P1] == 2.0
    assert series.reported_value[P2] == 5.0
    assert series.definition_text[P1] == DEF_COMPSALES_A
    assert series.adjacent_change[P2] == SOURCE_UNAVAILABLE
    assert series.growth[P2] is None
    assert series.unavailable_reasons[P2] == (reason,)


def test_qualifier_insertion_order_does_not_block_comparisons():
    prior = _spsf(period=P1, value=100.0, qualifiers={"channel": "stores", "note": "a"})
    current = _spsf(
        period=P2,
        value=110.0,
        qualifiers={"note": "a", "channel": "stores"},
    )
    fin = _fin_with_management(prior, current, extra_periods=[P1, P2])
    series = _series_for(compute_management_kpi_series(fin), prior)
    assert series.adjacent_change[P2] == 10.0
    assert series.growth[P2] == pytest.approx(0.1)
    assert series.unavailable_reasons[P2] is None
    assert dict(series.qualifiers[P1]) == dict(series.qualifiers[P2])


def test_invalid_contracts_and_noncanonical_axes_fail_closed_without_mutation():
    fin = _fin_with_management(
        _compsales(period=P1, value=2.0),
        _spsf(period=P1, value=1400.0),
        extra_periods=[P1, P2],
    )
    original = copy.deepcopy(fin.historical_operating_kpis)

    fin.historical_operating_kpis.management_observations[1].value = -1
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative"):
        compute_management_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.management_observations[0].definition_text = True  # type: ignore[assignment]
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="must be a string"):
        compute_management_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    with pytest.raises(ValueError, match="canonical fiscal axis"):
        compute_management_kpi_series(fin, [P2, P1])
    assert fin.historical_operating_kpis == original

    series = compute_management_kpi_series(fin)
    assert fin.historical_operating_kpis == original
    assert series.periods == (P1, P2)


def test_mixed_histories_preserve_store_analytics_within_tolerance():
    stores = (
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 767),
    )
    store_only = _fin_with_operating_kpis(*stores, extra_periods=[P0, P1, P2])
    mixed = _fin_with_operating_kpis(
        *stores,
        management=[
            _compsales(period=P2, value=-3.0),
            _spsf(period=P2, value=0.0),
        ],
        extra_periods=[P0, P1, P2],
    )
    assert operating_kpi_applicable(store_only) is True
    assert operating_kpi_applicable(mixed) is True
    assert operating_kpi_revenue_store_relationship_applicable(store_only) is True
    assert operating_kpi_revenue_store_relationship_applicable(mixed) is True
    assert management_kpi_applicable(store_only) is False
    assert management_kpi_applicable(mixed) is True
    left = compute_operating_kpi_series(store_only)
    right = compute_operating_kpi_series(mixed)
    expected = _independent_from_counts([P0, P1, P2], {P0: 655, P1: 711, P2: 767})
    _assert_series_matches(left, expected)
    _assert_series_matches(right, expected)
    for period in (P0, P1, P2):
        growth_left = left.growth[period]
        growth_right = right.growth[period]
        if isinstance(growth_left, float) and isinstance(growth_right, float):
            assert abs(growth_left - growth_right) <= OPERATING_KPI_RATIO_TOLERANCE
        else:
            assert growth_left == growth_right
    restored = standardized_from_payload(standardized_to_payload(mixed))
    reloaded = compute_management_kpi_series(restored)
    original = compute_management_kpi_series(mixed)
    assert reloaded == original


def test_ordinary_path_both_families_analytics_and_reload(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "ord")
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[0],
        MANAGEMENT_NAMES[1],
        period=P2023.isoformat(),
        values=(-3, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[2],
        MANAGEMENT_NAMES[3],
        period=P2024.isoformat(),
        values=(5, 7),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    _write_selected_on_docs(
        dest,
        FAMILY_SALES_PER_SQUARE_FOOT,
        MANAGEMENT_NAMES[0],
        MANAGEMENT_NAMES[1],
        period=P2023.isoformat(),
        values=(1400, 1410),
        definition=DEF_SPSF,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    _write_selected_on_docs(
        dest,
        FAMILY_SALES_PER_SQUARE_FOOT,
        MANAGEMENT_NAMES[2],
        MANAGEMENT_NAMES[3],
        period=P2024.isoformat(),
        values=(1410, 1430),
        definition=DEF_SPSF,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    reconciled = _reconcile(dest, admit=ADMIT_2022)
    before = copy.deepcopy(management_admission_payload(reconciled.management_admission))
    fin = standardize_reconciled(reconciled)
    assert management_admission_payload(reconciled.management_admission) == before
    payload = _assert_export_reload_export(fin)
    restored = standardized_from_payload(copy.deepcopy(payload))
    first = compute_management_kpi_series(fin)
    second = compute_management_kpi_series(restored)
    assert first == second
    compsales = [
        row
        for row in _management_rows(restored, family=FAMILY_COMPARABLE_SALES_GROWTH)
        if row["geography"] == "global" and row["basis"] == "reported"
    ]
    spsf = _management_rows(restored, family=FAMILY_SALES_PER_SQUARE_FOOT)
    assert {row["period"] for row in compsales} == {P2023.isoformat(), P2024.isoformat()}
    assert {row["period"] for row in spsf} == {P2023.isoformat(), P2024.isoformat()}
    compsales_series = next(
        item
        for item in first.series.values()
        if item.family == FAMILY_COMPARABLE_SALES_GROWTH
        and item.geography == "global"
        and item.basis == "reported"
        and item.population == POP_STORES_AND_ECOMMERCE
    )
    spsf_series = next(
        item for item in first.series.values() if item.family == FAMILY_SALES_PER_SQUARE_FOOT
    )
    assert compsales_series.reported_value[P2023] == 2
    assert compsales_series.reported_value[P2024] == 7
    assert compsales_series.adjacent_change[P2024] == 5
    assert compsales_series.growth[P2024] is None
    assert spsf_series.reported_value[P2023] == 1410
    assert spsf_series.reported_value[P2024] == 1430
    assert spsf_series.adjacent_change[P2024] == 20
    assert spsf_series.growth[P2024] == pytest.approx(20 / 1410)
    serialized = json.dumps(payload["historical_operating_kpis"])
    assert "source_file" not in serialized
    assert "assurance" not in serialized
    assert "revision" not in serialized


def test_ordinary_path_sparse_definition_change_preserves_reported_values(tmp_path: Path):
    dest = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "sparse")
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[0],
        MANAGEMENT_NAMES[1],
        period=P2023.isoformat(),
        values=(1, 2),
        definition=DEF_A,
        week=False,
        reporting_basis=REPORTING_BASIS_52,
    )
    _write_selected_on_docs(
        dest,
        FAMILY_COMPARABLE_SALES_GROWTH,
        MANAGEMENT_NAMES[2],
        MANAGEMENT_NAMES[3],
        period=P2025.isoformat(),
        values=(3, 4),
        definition=DEF_B,
        week=True,
        reporting_basis=REPORTING_BASIS_53,
    )
    fin = standardize_reconciled(_reconcile(dest, admit=ADMIT_2022))
    restored = standardized_from_payload(standardized_to_payload(fin))
    series = next(
        item
        for item in compute_management_kpi_series(restored).series.values()
        if item.family == FAMILY_COMPARABLE_SALES_GROWTH
        and item.geography == "global"
        and item.basis == "reported"
    )
    assert series.reported_value[P2023] == 2
    assert series.reported_value[P2024] == SOURCE_UNAVAILABLE
    assert series.reported_value[P2025] == 4
    assert series.definition_text[P2023] == DEF_A
    assert series.definition_text[P2025] == DEF_B
    assert series.adjacent_change[P2024] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P2024] == (REASON_MISSING_OBSERVATION,)
    assert series.adjacent_change[P2025] == SOURCE_UNAVAILABLE
    assert series.unavailable_reasons[P2025] == (REASON_MISSING_PRIOR_OBSERVATION,)


def test_supplied_documents_yield_no_management_analytics(tmp_path: Path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_rec = _reconcile(mixed, admit=ADMIT_2022)
    annual_rec = _reconcile(annual, admit=ADMIT_2022)
    mixed_fin = standardize_reconciled(mixed_rec)
    annual_fin = standardize_reconciled(annual_rec)
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None
    assert management_kpi_applicable(mixed_fin) is False
    assert management_kpi_applicable(annual_fin) is False
    assert operating_kpi_revenue_store_relationship_applicable(mixed_fin) is False
    assert operating_kpi_revenue_store_relationship_applicable(annual_fin) is False
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(mixed_fin)
    with pytest.raises(
        MissingLineError,
        match="operating KPI revenue/store relationship sources not available",
    ):
        compute_operating_kpi_revenue_store_relationship(mixed_fin)
    mixed_payload = standardized_to_payload(mixed_fin)
    annual_payload = standardized_to_payload(annual_fin)
    assert _canonicalize(mixed_payload) == _canonicalize(annual_payload)
    assert _statement_provenance(reconciliation_provenance_payload(mixed_rec)) == (
        _statement_provenance(reconciliation_provenance_payload(annual_rec))
    )
    assert reconciliation_conflicts_payload(mixed_rec) == reconciliation_conflicts_payload(
        annual_rec
    )
    admission = management_admission_payload(mixed_rec.management_admission)
    assert admission["reported_observation_count"] == 135
    assert admission["reconciliation"]["selected_count"] == 0
    assert admission["reconciliation"]["group_selection_counts"]["selected"] == 0
    assert _bytes_by_name(EXTRACTED) == before


def test_augmented_mixed_without_selection_keeps_store_analytics_only(tmp_path: Path):
    dest = _prepare_augmented(tmp_path)
    for name in MANAGEMENT_NAMES:
        Path(dest / name).write_bytes((EXTRACTED / name).read_bytes())
    reconciled = _reconcile(dest, admit=ADMIT_2022)
    fin = standardize_reconciled(reconciled)
    assert operating_kpi_applicable(fin) is True
    assert operating_kpi_revenue_store_relationship_applicable(fin) is True
    assert management_kpi_applicable(fin) is False
    series = compute_operating_kpi_series(fin)
    expected = _independent_from_counts(
        canonical_fiscal_periods(fin), INDEPENDENT_STORE_TOTALS
    )
    _assert_series_matches(series, expected)
    assert series.period_end_count[P2023] == 655
    assert series.net_count_change[P2023] == 81
    with pytest.raises(MissingLineError, match="management KPI sources not available"):
        compute_management_kpi_series(fin)
    payload = standardized_to_payload(fin)
    assert payload["historical_operating_kpis"]["observations"]
    assert "management_observations" not in payload["historical_operating_kpis"]
