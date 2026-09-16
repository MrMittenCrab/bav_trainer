"""Optional historical company-operated store-count analytical series."""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from core.data.historical_operating_kpis import (
    METRIC_STORE_COUNT,
    POPULATION_COMPANY_OPERATED,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import (
    reconciliation_provenance_payload,
    standardize_reconciled,
)
from core.model.line_resolver import MissingLineError
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.model.period_axis import canonical_fiscal_periods
from core.model.ratio_values import SOURCE_UNAVAILABLE, UNDEFINED_RATIO, ratio_or_na
from core.tests.test_historical_segment import _base_payload
from core.tests.test_operating_kpi_facts import (
    ADMIT_2022,
    INDEPENDENT_STORE_TOTALS,
    P2022,
    P2023,
    P2024,
    P2025,
    P2026,
    _fin_with_operating_kpis,
    _kpi_model_observation,
    _validated_augmented,
)

ROOT = Path(__file__).resolve().parents[2]
FR_JSON = ROOT / "benchmark" / "fast_retailing" / "reconciled" / "standardized.json"
P0 = date(2023, 12, 31)
P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _independent_from_counts(
    axis: list[date],
    counts: dict[date, float],
    units: dict[date, str] | None = None,
) -> dict[date, dict[str, float | str | None]]:
    """Recompute count, net change, and growth from period-end counts only."""
    expected: dict[date, dict[str, float | str | None]] = {}
    for index, period in enumerate(axis):
        opening = index == 0
        current = counts.get(period)
        if current is None:
            expected[period] = {
                "unit": SOURCE_UNAVAILABLE,
                "count": SOURCE_UNAVAILABLE,
                "change": None if opening else SOURCE_UNAVAILABLE,
                "growth": None if opening else SOURCE_UNAVAILABLE,
            }
            continue
        prior_period = None if opening else axis[index - 1]
        prior = None if prior_period is None else counts.get(prior_period)
        if opening:
            change: float | str | None = None
            growth: float | str | None = None
        elif prior is None:
            change = SOURCE_UNAVAILABLE
            growth = SOURCE_UNAVAILABLE
        else:
            change = float(current) - float(prior)
            growth = ratio_or_na(change, float(prior))
        expected[period] = {
            "unit": (units or {}).get(period, "stores"),
            "count": float(current),
            "change": change,
            "growth": growth,
        }
    return expected


def _assert_series_matches(series, expected) -> None:
    assert series.periods == tuple(expected)
    assert series.metric == METRIC_STORE_COUNT
    assert series.population == POPULATION_COMPANY_OPERATED
    for period, row in expected.items():
        assert series.unit[period] == row["unit"]
        assert series.period_end_count[period] == row["count"]
        assert series.net_count_change[period] == row["change"]
        growth = series.growth[period]
        expected_growth = row["growth"]
        if isinstance(growth, float) and isinstance(expected_growth, float):
            assert abs(growth - expected_growth) <= OPERATING_KPI_RATIO_TOLERANCE
        else:
            assert growth == expected_growth


def test_absent_and_null_payloads_make_module_absent():
    payload = _base_payload()
    absent = standardized_from_payload(payload)
    assert operating_kpi_applicable(absent) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(absent)

    payload["historical_operating_kpis"] = None
    null = standardized_from_payload(payload)
    assert operating_kpi_applicable(null) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(null)


def test_legacy_fast_retailing_payload_omits_operating_kpi_module():
    payload = json.loads(FR_JSON.read_text(encoding="utf-8"))
    assert "historical_operating_kpis" not in payload
    fin = standardized_from_payload(payload)
    assert fin.historical_operating_kpis is None
    assert operating_kpi_applicable(fin) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(fin)
    assert "historical_operating_kpis" not in standardized_to_payload(fin)


def test_shuffled_observations_and_reordered_inputs():
    fin = _fin_with_operating_kpis(
        _kpi_model_observation(P2, 767),
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P1, 711),
        extra_periods=[P0, P1, P2],
    )
    before = copy.deepcopy(fin.historical_operating_kpis)
    series = compute_operating_kpi_series(fin)
    expected = _independent_from_counts(
        canonical_fiscal_periods(fin),
        {item.period: float(item.value) for item in fin.historical_operating_kpis.observations},
    )
    _assert_series_matches(series, expected)
    assert series.net_count_change[P0] is None
    assert series.growth[P0] is None
    assert series.net_count_change[P1] == 56
    assert series.net_count_change[P2] == 56
    assert fin.historical_operating_kpis == before

    original_order = [item.period for item in fin.historical_operating_kpis.observations]
    fin.historical_operating_kpis.observations = list(
        reversed(list(fin.historical_operating_kpis.observations))
    )
    reordered = compute_operating_kpi_series(fin)
    assert reordered == series
    assert [item.period for item in fin.historical_operating_kpis.observations] == list(
        reversed(original_order)
    )


def test_monetary_scale_independence_and_both_count_units():
    stores_thousands = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 711, unit="stores"),
        _kpi_model_observation(P2, 767, unit="stores"),
        units="USD in Thousands",
    )
    ones_millions = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 711, unit="ones"),
        _kpi_model_observation(P2, 767, unit="ones"),
        units="USD in Millions",
    )
    mixed = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 711, unit="ones"),
        _kpi_model_observation(P2, 767, unit="stores"),
        units="USD in Thousands",
    )
    stores_series = compute_operating_kpi_series(stores_thousands)
    ones_series = compute_operating_kpi_series(ones_millions)
    mixed_series = compute_operating_kpi_series(mixed)
    assert stores_series.period_end_count == ones_series.period_end_count
    assert stores_series.net_count_change == ones_series.net_count_change
    assert stores_series.growth == ones_series.growth
    assert mixed_series.period_end_count == stores_series.period_end_count
    assert mixed_series.net_count_change == stores_series.net_count_change
    assert stores_series.unit[P1] == "stores"
    assert ones_series.unit[P1] == "ones"
    assert mixed_series.unit[P1] == "ones"
    assert mixed_series.unit[P2] == "stores"
    assert stores_thousands.units != ones_millions.units


def test_single_period_history_omits_opening_comparisons():
    fin = _fin_with_operating_kpis(_kpi_model_observation(P2, 811))
    series = compute_operating_kpi_series(fin)
    expected = _independent_from_counts([P2], {P2: 811})
    _assert_series_matches(series, expected)
    assert series.period_end_count[P2] == 811
    assert series.net_count_change[P2] is None
    assert series.growth[P2] is None


def test_sparse_histories_do_not_compress_or_substitute_periods():
    fin = _fin_with_operating_kpis(
        _kpi_model_observation(P0, 655),
        _kpi_model_observation(P2, 767),
        extra_periods=[P0, P1, P2],
    )
    series = compute_operating_kpi_series(fin)
    expected = _independent_from_counts(
        [P0, P1, P2],
        {P0: 655, P2: 767},
    )
    _assert_series_matches(series, expected)
    assert series.periods == (P0, P1, P2)
    assert series.net_count_change[P0] is None
    assert series.period_end_count[P1] == SOURCE_UNAVAILABLE
    assert series.unit[P1] == SOURCE_UNAVAILABLE
    assert series.net_count_change[P1] == SOURCE_UNAVAILABLE
    assert series.growth[P1] == SOURCE_UNAVAILABLE
    assert series.period_end_count[P2] == 767
    assert series.net_count_change[P2] == SOURCE_UNAVAILABLE
    assert series.growth[P2] == SOURCE_UNAVAILABLE
    skipped = ratio_or_na(767 - 655, 655)
    assert series.growth[P2] != skipped


def test_zero_denominators_zero_counts_and_declining_counts():
    zero_open = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 0),
        _kpi_model_observation(P2, 10),
    )
    zero_current = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 10),
        _kpi_model_observation(P2, 0),
    )
    declining = _fin_with_operating_kpis(
        _kpi_model_observation(P1, 711),
        _kpi_model_observation(P2, 655),
    )
    open_series = compute_operating_kpi_series(zero_open)
    current_series = compute_operating_kpi_series(zero_current)
    decline_series = compute_operating_kpi_series(declining)
    _assert_series_matches(
        open_series, _independent_from_counts([P1, P2], {P1: 0, P2: 10})
    )
    _assert_series_matches(
        current_series, _independent_from_counts([P1, P2], {P1: 10, P2: 0})
    )
    _assert_series_matches(
        decline_series, _independent_from_counts([P1, P2], {P1: 711, P2: 655})
    )
    assert open_series.period_end_count[P1] == 0
    assert open_series.net_count_change[P2] == 10
    assert open_series.growth[P2] == UNDEFINED_RATIO
    assert current_series.period_end_count[P2] == 0
    assert current_series.net_count_change[P2] == -10
    assert current_series.growth[P2] == -1.0
    assert decline_series.net_count_change[P2] == -56
    assert abs(decline_series.growth[P2] - (-56 / 711)) <= OPERATING_KPI_RATIO_TOLERANCE


def test_invalid_contracts_fail_closed_without_mutation():
    fin = _fin_with_operating_kpis(_kpi_model_observation(P1, 711), _kpi_model_observation(P2, 767))
    original = copy.deepcopy(fin.historical_operating_kpis)

    fin.historical_operating_kpis.observations[0].value = -1
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative integer"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations[0].value = 655.5
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative integer"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations[0].metric = "square_footage"
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="unknown"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations[0].population = "franchise"
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="unknown"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations[0].unit = "thousands"
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="unsupported unit"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations.append(
        _kpi_model_observation(P1, 711)
    )
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="duplicate operating-KPI identity"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    fin.historical_operating_kpis.observations[0].period = date(2020, 1, 1)
    mutated = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="outside the model axis"):
        compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == mutated

    fin.historical_operating_kpis = copy.deepcopy(original)
    with pytest.raises(ValueError, match="canonical fiscal axis"):
        compute_operating_kpi_series(fin, [P2, P1])
    assert fin.historical_operating_kpis == original

    success_before = copy.deepcopy(original)
    series = compute_operating_kpi_series(fin)
    assert fin.historical_operating_kpis == success_before
    assert series.period_end_count[P2] == 767


def _reload_admitted_store_histories(validated):
    outputs = []
    for order in (validated, list(reversed(validated))):
        reconciled = reconcile_filings(order, admit_periods=ADMIT_2022)
        fin = standardize_reconciled(reconciled)
        restored = standardized_from_payload(
            json.loads(json.dumps(standardized_to_payload(fin)))
        )
        outputs.append((reconciled, fin, restored))
    return outputs


def test_source_grounded_reload_matches_independent_count_arithmetic(tmp_path: Path):
    _dest, validated = _validated_augmented(tmp_path)
    reloads = _reload_admitted_store_histories(validated)
    series_by_order = []
    for reconciled, fin, restored in reloads:
        assert restored.historical_operating_kpis == fin.historical_operating_kpis
        model_counts = {
            item.period: float(item.value)
            for item in restored.historical_operating_kpis.observations
        }
        selected_on_axis = {
            item.period: float(item.value)
            for item in reconciled.selected_operating_kpi_facts
            if item.period in set(reconciled.periods)
        }
        assert model_counts == selected_on_axis
        assert model_counts == {period: float(value) for period, value in INDEPENDENT_STORE_TOTALS.items()}

        axis = canonical_fiscal_periods(restored)
        assert axis == [P2022, P2023, P2024, P2025, P2026]
        pre = compute_operating_kpi_series(fin)
        post = compute_operating_kpi_series(restored)
        assert pre == post
        expected = _independent_from_counts(axis, model_counts)
        _assert_series_matches(post, expected)
        series_by_order.append(post)

        assert post.period_end_count[P2022] == 574
        assert post.period_end_count[P2023] == 655
        assert post.period_end_count[P2024] == 711
        assert post.period_end_count[P2025] == 767
        assert post.period_end_count[P2026] == 811
        assert post.net_count_change[P2022] is None
        assert post.growth[P2022] is None
        assert post.net_count_change[P2023] == 81
        assert post.net_count_change[P2024] == 56
        assert post.net_count_change[P2025] == 56
        assert post.net_count_change[P2026] == 44
        assert abs(post.growth[P2023] - (81 / 574)) <= OPERATING_KPI_RATIO_TOLERANCE
        assert abs(post.growth[P2024] - (56 / 655)) <= OPERATING_KPI_RATIO_TOLERANCE
        assert abs(post.growth[P2025] - (56 / 711)) <= OPERATING_KPI_RATIO_TOLERANCE
        assert abs(post.growth[P2026] - (44 / 767)) <= OPERATING_KPI_RATIO_TOLERANCE
        assert all(post.unit[period] == "stores" for period in axis)

        assert len(reconciled.selected_geographic_facts) == 56
        assert restored.historical_segment == fin.historical_segment
        assert sum(len(snap.values) for snap in restored.historical_segment.periods) == 56
        americas = [
            item
            for item in reconciled.selected_geographic_facts
            if item.period == P2025 and item.fact_type.endswith("net_revenue.americas")
        ]
        assert len(americas) == 1
        assert americas[0].value == 7928156
        provenance = reconciliation_provenance_payload(reconciled)
        assert "selected_operating_kpi_facts" in provenance
        kpi_json = json.dumps(standardized_to_payload(restored)["historical_operating_kpis"])
        assert "source_label" not in kpi_json
        assert "source_note" not in kpi_json
        assert "pdf_page" not in kpi_json
        assert all(
            row["source_label"] and "source_note" in row
            for row in provenance["selected_operating_kpi_facts"]
        )

    assert series_by_order[0] == series_by_order[1]
