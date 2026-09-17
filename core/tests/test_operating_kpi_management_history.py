"""Validated management-KPI standardized-history contract and round trips."""

from __future__ import annotations

import copy
import json
import math
import shutil
from dataclasses import replace
from datetime import date

import pytest

from core.data.historical_operating_kpis import (
    MANAGEMENT_TEXT_FIELDS,
    UNIT_PERCENT,
    UNIT_USD_PER_SQUARE_FOOT,
    validate_historical_operating_kpi_data,
    validate_historical_operating_kpis,
)
from core.data.interface import HistoricalManagementKpiObservation
from core.data.standardized_io import standardized_from_payload, standardized_to_payload
from core.ingestion.filing_cli import load_and_validate_extracted_dir
from core.ingestion.filing_reconciler import reconcile_filings
from core.ingestion.filing_standardizer import standardize_reconciled
from core.ingestion.management_kpi import management_admission_payload
from core.ingestion.management_kpi_identity import (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
    POP_COMPANY_OPERATED_STORES,
    POP_STORES_AND_DTC,
    POP_STORES_AND_ECOMMERCE,
)
from core.model.line_resolver import MissingLineError
from core.model.operating_kpi import (
    OPERATING_KPI_RATIO_TOLERANCE,
    compute_operating_kpi_series,
    operating_kpi_applicable,
)
from core.tests.test_historical_segment import _base_payload
from core.tests.test_management_kpi_admission import (
    ANNUAL_NAMES,
    EXTRACTED,
    MANAGEMENT_NAMES,
    SOURCE,
    _bytes_by_name,
    _copy_json,
)
from core.tests.test_operating_kpi_analysis import _assert_series_matches, _independent_from_counts
from core.tests.test_operating_kpi_facts import (
    P2023,
    P2024,
    P2025,
    P2026,
    _fin_with_operating_kpis,
    _kpi_model_observation,
)
from core.model.period_axis import canonical_fiscal_periods

AXIS = [P2023, P2024, P2025, P2026]
DEF_COMPSALES_A = "Temporary comparable-sales definition A for contract fixtures."
DEF_COMPSALES_B = "Temporary comparable-sales definition B after a calendar change."
DEF_SPSF = "Temporary sales-per-square-foot definition for contract fixtures."
TICKER = "LULU"
COMPANY = "Example Co"
_NON_STRING_TEXT_VALUES = (
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param(None, id="null"),
    pytest.param(0, id="zero"),
    pytest.param(1, id="int"),
    pytest.param(1.5, id="float"),
    pytest.param([], id="empty-list"),
    pytest.param(["LULU"], id="list"),
    pytest.param({}, id="empty-dict"),
    pytest.param({"basis": "52_week"}, id="dict"),
)
_VALIDATION_MODES = (
    pytest.param("object", id="object"),
    pytest.param("default", id="reload-default"),
    pytest.param("strict-false", id="reload-strict-false"),
    pytest.param("strict-true", id="reload-strict-true"),
)
_REVIEW_PROBES = (
    pytest.param("definition_text", True, id="boolean-definition-text"),
    pytest.param("entity_ticker", ["LULU"], id="list-entity-ticker"),
    pytest.param("calendar_week_adjustment", False, id="boolean-calendar-adjustment"),
    pytest.param("calendar_reporting_basis", {"basis": "52_week"}, id="dict-calendar-basis"),
)


def _mgmt(
    *,
    family: str,
    period: date,
    value: float,
    geography: str = "",
    population: str = "",
    unit: str = "",
    basis: str = "reported",
    comparison: str = "",
    definition_text: str = DEF_COMPSALES_A,
    period_kind: str = "date",
    calendar_week_adjustment: str = "included",
    calendar_reporting_basis: str = "52_week",
    qualifiers: dict[str, str] | None = None,
    entity_ticker: str = TICKER,
    entity_company: str = COMPANY,
) -> HistoricalManagementKpiObservation:
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        unit = unit or UNIT_PERCENT
        comparison = comparison or "year_over_year"
        population = population or POP_STORES_AND_ECOMMERCE
        geography = geography if geography != "" or population == POP_COMPANY_OPERATED_STORES else (
            geography or "global"
        )
    else:
        unit = unit or UNIT_USD_PER_SQUARE_FOOT
        population = population or POP_COMPANY_OPERATED_STORES
        definition_text = definition_text if definition_text != DEF_COMPSALES_A else DEF_SPSF
    return HistoricalManagementKpiObservation(
        family=family,
        entity_ticker=entity_ticker,
        entity_company=entity_company,
        geography=geography,
        population=population,
        unit=unit,
        basis=basis,
        comparison=comparison,
        period=period,
        value=value,
        definition_text=definition_text,
        period_kind=period_kind,
        calendar_week_adjustment=calendar_week_adjustment,
        calendar_reporting_basis=calendar_reporting_basis,
        qualifiers=dict(qualifiers or {}),
    )


def _compsales(**kwargs) -> HistoricalManagementKpiObservation:
    return _mgmt(family=FAMILY_COMPARABLE_SALES_GROWTH, **kwargs)


def _spsf(**kwargs) -> HistoricalManagementKpiObservation:
    return _mgmt(family=FAMILY_SALES_PER_SQUARE_FOOT, **kwargs)


def _both_family_observations() -> list[HistoricalManagementKpiObservation]:
    return [
        _compsales(period=P2026, value=2.0, geography="global", basis="reported"),
        _compsales(period=P2025, value=0.0, geography="global", basis="reported"),
        _compsales(period=P2023, value=-3.0, geography="global", basis="reported"),
        _compsales(
            period=P2026,
            value=1.5,
            geography="global",
            basis="constant_dollar",
        ),
        _compsales(period=P2026, value=4.0, geography="americas", basis="reported"),
        _compsales(
            period=P2026,
            value=8.0,
            geography="china_mainland",
            basis="constant_dollar",
        ),
        _compsales(period=P2026, value=6.0, geography="rest_of_world", basis="reported"),
        _compsales(
            period=P2026,
            value=3.0,
            geography="global",
            population=POP_STORES_AND_DTC,
            basis="reported",
        ),
        _compsales(
            period=P2023,
            value=10.0,
            geography="",
            population=POP_COMPANY_OPERATED_STORES,
            definition_text=DEF_COMPSALES_A,
            calendar_week_adjustment="included",
            calendar_reporting_basis="52_week",
        ),
        _compsales(
            period=P2025,
            value=12.0,
            geography="",
            population=POP_COMPANY_OPERATED_STORES,
            definition_text=DEF_COMPSALES_B,
            calendar_week_adjustment="excluded",
            calendar_reporting_basis="53_week",
            qualifiers={"note": "calendar-discontinuity"},
        ),
        _spsf(period=P2026, value=1426),
        _spsf(period=P2025, value=0),
        _spsf(period=P2023, value=1407.5),
    ]


def _both_family_fin(**kwargs):
    return _fin_with_operating_kpis(
        management=_both_family_observations(),
        extra_periods=AXIS,
        **kwargs,
    )


def _reorder_payload(value):
    if isinstance(value, dict):
        items = list(value.items())
        items.reverse()
        return {key: _reorder_payload(item) for key, item in items}
    if isinstance(value, list):
        return [_reorder_payload(item) for item in reversed(value)]
    return value


def _family_item(family: str) -> HistoricalManagementKpiObservation:
    if family == FAMILY_COMPARABLE_SALES_GROWTH:
        return _compsales(period=P2026, value=2.0)
    return _spsf(period=P2026, value=1426)


def _from_payload(payload: dict, *, mode: str):
    if mode == "default":
        return standardized_from_payload(payload)
    if mode == "strict-false":
        return standardized_from_payload(payload, strict=False)
    if mode == "strict-true":
        return standardized_from_payload(payload, strict=True)
    raise AssertionError(f"unsupported reload mode: {mode}")


def _assert_rejects_non_string_management_text(
    family: str,
    field: str,
    value: object,
    mode: str,
) -> None:
    item = _family_item(family)
    if mode == "object":
        mutated = replace(item, **{field: value})
        fin = _fin_with_operating_kpis(management=[mutated], extra_periods=[P2026])
        original = copy.deepcopy(fin.historical_operating_kpis)
        with pytest.raises(ValueError, match="must be a string"):
            validate_historical_operating_kpis(fin)
        assert fin.historical_operating_kpis == original
        with pytest.raises(ValueError, match="must be a string"):
            validate_historical_operating_kpi_data(
                fin.historical_operating_kpis,
                model_periods=fin.period_dates(),
            )
        assert fin.historical_operating_kpis == original
        return
    payload = standardized_to_payload(
        _fin_with_operating_kpis(management=[item], extra_periods=[P2026])
    )
    payload["historical_operating_kpis"]["management_observations"][0][field] = value
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError):
        _from_payload(payload, mode=mode)
    assert payload == frozen


def _assert_export_reload_export(fin) -> dict:
    first = standardized_to_payload(fin)
    restored = standardized_from_payload(copy.deepcopy(first))
    second = standardized_to_payload(restored)
    third = standardized_to_payload(
        standardized_from_payload(copy.deepcopy(second))
    )
    assert first == second == third
    kpi = first["historical_operating_kpis"]
    assert "source_file" not in json.dumps(kpi)
    assert "source_path" not in json.dumps(kpi)
    assert "assurance" not in json.dumps(kpi)
    assert "revision" not in json.dumps(kpi)
    return first


def test_object_and_serialized_validation_are_independent():
    fin = _both_family_fin()
    original = copy.deepcopy(fin.historical_operating_kpis)
    validate_historical_operating_kpi_data(
        fin.historical_operating_kpis,
        model_periods=fin.period_dates(),
    )
    validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original
    payload = standardized_to_payload(fin)
    frozen = copy.deepcopy(payload)
    restored = standardized_from_payload(payload)
    assert payload == frozen
    assert restored.historical_operating_kpis is not None
    validate_historical_operating_kpi_data(
        restored.historical_operating_kpis,
        model_periods=restored.period_dates(),
    )


def test_both_family_round_trip_preserves_identity_and_discontinuities():
    fin = _both_family_fin()
    payload = _assert_export_reload_export(fin)
    kpi = payload["historical_operating_kpis"]
    assert kpi["observations"] == []
    rows = kpi["management_observations"]
    assert [row["family"] for row in rows] == sorted(row["family"] for row in rows)
    by_key = {
        (
            row["family"],
            row["geography"],
            row["population"],
            row["basis"],
            row["period"],
        ): row
        for row in rows
    }
    global_reported = [
        row
        for row in rows
        if row["family"] == FAMILY_COMPARABLE_SALES_GROWTH
        and row["geography"] == "global"
        and row["population"] == POP_STORES_AND_ECOMMERCE
        and row["basis"] == "reported"
    ]
    assert [row["period"] for row in global_reported] == [
        P2023.isoformat(),
        P2025.isoformat(),
        P2026.isoformat(),
    ]
    assert P2024.isoformat() not in {row["period"] for row in global_reported}
    assert by_key[
        (FAMILY_COMPARABLE_SALES_GROWTH, "global", POP_STORES_AND_ECOMMERCE, "reported", P2023.isoformat())
    ]["value"] == -3
    assert by_key[
        (FAMILY_COMPARABLE_SALES_GROWTH, "global", POP_STORES_AND_ECOMMERCE, "reported", P2025.isoformat())
    ]["value"] == 0
    store_a = by_key[
        (
            FAMILY_COMPARABLE_SALES_GROWTH,
            "",
            POP_COMPANY_OPERATED_STORES,
            "reported",
            P2023.isoformat(),
        )
    ]
    store_b = by_key[
        (
            FAMILY_COMPARABLE_SALES_GROWTH,
            "",
            POP_COMPANY_OPERATED_STORES,
            "reported",
            P2025.isoformat(),
        )
    ]
    assert store_a["definition_text"] == DEF_COMPSALES_A
    assert store_b["definition_text"] == DEF_COMPSALES_B
    assert store_a["calendar_week_adjustment"] != store_b["calendar_week_adjustment"]
    assert store_a["calendar_reporting_basis"] != store_b["calendar_reporting_basis"]
    assert store_b["qualifiers"] == {"note": "calendar-discontinuity"}
    assert any(row["geography"] == "americas" for row in rows)
    assert any(row["population"] == POP_STORES_AND_DTC for row in rows)
    assert any(row["basis"] == "constant_dollar" for row in rows)
    spsf = [row for row in rows if row["family"] == FAMILY_SALES_PER_SQUARE_FOOT]
    assert {row["period"] for row in spsf} == {
        P2023.isoformat(),
        P2025.isoformat(),
        P2026.isoformat(),
    }
    assert all(row["unit"] == UNIT_USD_PER_SQUARE_FOOT for row in spsf)
    assert all(row["unit"] == UNIT_PERCENT for row in rows if row["family"] == FAMILY_COMPARABLE_SALES_GROWTH)


def test_both_family_reload_modes_preserve_valid_histories():
    fin = _both_family_fin()
    payload = standardized_to_payload(fin)
    for mode in ("default", "strict-false", "strict-true"):
        restored = _from_payload(copy.deepcopy(payload), mode=mode)
        assert standardized_to_payload(restored) == payload


def test_reordered_collections_and_identity_fields_are_canonical():
    fin = _both_family_fin()
    fin.historical_operating_kpis.management_observations = list(
        reversed(fin.historical_operating_kpis.management_observations)
    )
    canonical = standardized_to_payload(fin)
    shuffled = copy.deepcopy(canonical)
    kpi = shuffled["historical_operating_kpis"]
    kpi["management_observations"] = _reorder_payload(kpi["management_observations"])
    assert kpi["management_observations"] != canonical["historical_operating_kpis"]["management_observations"]
    restored = standardized_from_payload(shuffled)
    assert standardized_to_payload(restored) == canonical
    again = standardized_to_payload(standardized_from_payload(standardized_to_payload(restored)))
    assert again == canonical


def test_distinct_supported_variants_may_share_a_period():
    fin = _fin_with_operating_kpis(
        management=[
            _compsales(period=P2026, value=2.0, geography="global", basis="reported"),
            _compsales(period=P2026, value=1.0, geography="global", basis="constant_dollar"),
            _spsf(period=P2026, value=1426),
        ],
        extra_periods=[P2026],
    )
    payload = _assert_export_reload_export(fin)
    rows = payload["historical_operating_kpis"]["management_observations"]
    assert len(rows) == 3
    assert {row["family"] for row in rows} == {
        FAMILY_COMPARABLE_SALES_GROWTH,
        FAMILY_SALES_PER_SQUARE_FOOT,
    }


def test_duplicate_identity_period_rejected_even_when_definition_differs():
    first = _compsales(period=P2026, value=2.0, definition_text=DEF_COMPSALES_A)
    second = _compsales(period=P2026, value=4.0, definition_text=DEF_COMPSALES_B)
    fin = _fin_with_operating_kpis(management=[first, second], extra_periods=[P2026])
    original = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="duplicate management-KPI identity-period"):
        validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original

    payload = standardized_to_payload(_both_family_fin())
    row = copy.deepcopy(payload["historical_operating_kpis"]["management_observations"][0])
    row["definition_text"] = DEF_COMPSALES_B
    payload["historical_operating_kpis"]["management_observations"].append(row)
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError, match="duplicate management-KPI identity-period"):
        standardized_from_payload(payload)
    assert payload == frozen


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda row: row.__setitem__("family", FAMILY_COMPARABLE_SALES_GROWTH) or row.__setitem__("unit", UNIT_USD_PER_SQUARE_FOOT), "unsupported unit"),
        (lambda row: row.__setitem__("geography", "europe"), "inconsistent management-KPI identity"),
        (lambda row: row.__setitem__("family", "digital_comparable_sales_growth"), "unsupported management-KPI family"),
        (lambda row: row.__setitem__("population", "franchise_stores"), "inconsistent management-KPI identity"),
        (lambda row: row.__setitem__("basis", "unknown_basis"), "inconsistent management-KPI identity"),
        (lambda row: row.__setitem__("unit", "thousands"), "unsupported unit"),
        (lambda row: row.__setitem__("period_kind", "fiscal_label"), "period_kind"),
        (lambda row: row.__setitem__("definition_text", ""), "missing definition_text"),
        (lambda row: row.__setitem__("value", True), "non-numeric"),
        (lambda row: row.__setitem__("value", math.inf), "non-finite"),
        (lambda row: row.__setitem__("period", "2020-01-01"), "outside the model axis"),
        (lambda row: row.__setitem__("period", "2025-02-30"), "canonical YYYY-MM-DD"),
        (lambda row: row.__setitem__("period", "2025-2-02"), "canonical YYYY-MM-DD"),
        (lambda row: row.__setitem__("source_file", "x.pdf"), "unsupported field"),
        (lambda row: row.__setitem__("assurance", "audited"), "unsupported field"),
    ],
)
def test_malformed_serialized_management_histories_fail_closed(mutate, match):
    payload = standardized_to_payload(_both_family_fin())
    mutate(payload["historical_operating_kpis"]["management_observations"][0])
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError, match=match):
        standardized_from_payload(payload)
    assert payload == frozen


@pytest.mark.parametrize(
    "family",
    [FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT],
    ids=["compsales", "spsf"],
)
@pytest.mark.parametrize("field", MANAGEMENT_TEXT_FIELDS)
@pytest.mark.parametrize("value", _NON_STRING_TEXT_VALUES)
@pytest.mark.parametrize("mode", _VALIDATION_MODES)
def test_non_string_management_text_fails_closed(family, field, value, mode):
    _assert_rejects_non_string_management_text(family, field, value, mode)


@pytest.mark.parametrize(
    "family",
    [FAMILY_COMPARABLE_SALES_GROWTH, FAMILY_SALES_PER_SQUARE_FOOT],
    ids=["compsales", "spsf"],
)
@pytest.mark.parametrize("field,value", _REVIEW_PROBES)
@pytest.mark.parametrize("mode", _VALIDATION_MODES)
def test_review_probes_reject_malformed_management_text(family, field, value, mode):
    _assert_rejects_non_string_management_text(family, field, value, mode)


@pytest.mark.parametrize("field,value", _REVIEW_PROBES)
def test_review_probes_reject_on_both_family_default_reload(field, value):
    payload = standardized_to_payload(_both_family_fin())
    payload["historical_operating_kpis"]["management_observations"][0][field] = value
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError):
        standardized_from_payload(payload)
    assert payload == frozen
    with pytest.raises(ValueError):
        standardized_from_payload(payload, strict=False)
    assert payload == frozen
    with pytest.raises(ValueError):
        standardized_from_payload(payload, strict=True)
    assert payload == frozen


def test_legitimate_empty_optional_management_text_is_preserved():
    fin = _fin_with_operating_kpis(
        management=[
            _compsales(
                period=P2026,
                value=2.0,
                geography="",
                population=POP_COMPANY_OPERATED_STORES,
                calendar_week_adjustment="",
                calendar_reporting_basis="",
            ),
            _spsf(
                period=P2026,
                value=1426,
                calendar_week_adjustment="",
                calendar_reporting_basis="",
            ),
        ],
        extra_periods=[P2026],
    )
    payload = _assert_export_reload_export(fin)
    rows = payload["historical_operating_kpis"]["management_observations"]
    compsales = next(
        row for row in rows if row["family"] == FAMILY_COMPARABLE_SALES_GROWTH
    )
    spsf = next(row for row in rows if row["family"] == FAMILY_SALES_PER_SQUARE_FOOT)
    assert compsales["geography"] == ""
    assert compsales["calendar_week_adjustment"] == ""
    assert compsales["calendar_reporting_basis"] == ""
    assert spsf["geography"] == ""
    assert spsf["comparison"] == ""
    assert spsf["calendar_week_adjustment"] == ""
    assert spsf["calendar_reporting_basis"] == ""
    assert compsales["definition_text"] == DEF_COMPSALES_A
    assert spsf["definition_text"] == DEF_SPSF
    assert compsales["period_kind"] == "date"
    assert spsf["qualifiers"] == {}


def test_malformed_management_qualifiers_fail_closed():
    item = _compsales(period=P2026, value=2.0)
    original_item = copy.deepcopy(item)
    fin = _fin_with_operating_kpis(
        management=[replace(item, qualifiers=["note"])],
        extra_periods=[P2026],
    )
    original = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="qualifiers must be an object"):
        validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original
    assert item == original_item

    keyed = replace(item, qualifiers={"": "blank"})
    fin = _fin_with_operating_kpis(management=[keyed], extra_periods=[P2026])
    original = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="qualifier keys must be strings"):
        validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original

    valued = replace(item, qualifiers={"note": False})
    fin = _fin_with_operating_kpis(management=[valued], extra_periods=[P2026])
    original = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="must be a string"):
        validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original

    payload = standardized_to_payload(
        _fin_with_operating_kpis(management=[item], extra_periods=[P2026])
    )
    for mutation, match in (
        (["note"], "qualifiers must be an object"),
        ({1: "x"}, "qualifier keys must be strings"),
        ({"note": False}, "must be a string"),
    ):
        mutated = copy.deepcopy(payload)
        mutated["historical_operating_kpis"]["management_observations"][0]["qualifiers"] = (
            mutation
        )
        frozen = copy.deepcopy(mutated)
        with pytest.raises(ValueError, match=match):
            standardized_from_payload(mutated)
        assert mutated == frozen


def test_negative_spsf_and_invalid_types_fail_closed():
    fin = _fin_with_operating_kpis(
        management=[_spsf(period=P2026, value=-1)],
        extra_periods=[P2026],
    )
    original = copy.deepcopy(fin.historical_operating_kpis)
    with pytest.raises(ValueError, match="non-negative"):
        validate_historical_operating_kpis(fin)
    assert fin.historical_operating_kpis == original

    payload = standardized_to_payload(_both_family_fin())
    payload["historical_operating_kpis"]["management_observations"] = {
        "family": FAMILY_SALES_PER_SQUARE_FOOT
    }
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError, match="management_observations must be a list"):
        standardized_from_payload(payload)
    assert payload == frozen


def test_empty_collections_fail_closed_and_do_not_fill_gaps():
    payload = _base_payload()
    payload["periods"] = [
        {"end_date": period.isoformat(), "label": period.isoformat(), "is_interim": False}
        for period in AXIS
    ]
    payload["historical_operating_kpis"] = {"observations": [], "management_observations": []}
    frozen = copy.deepcopy(payload)
    with pytest.raises(ValueError, match="at least one observation"):
        standardized_from_payload(payload)
    assert payload == frozen

    fin = _fin_with_operating_kpis(
        management=[_compsales(period=P2026, value=2.0)],
        extra_periods=AXIS,
    )
    restored = standardized_from_payload(standardized_to_payload(fin))
    periods = {
        item.period
        for item in restored.historical_operating_kpis.management_observations
    }
    assert periods == {P2026}
    assert P2023 not in periods
    assert P2024 not in periods
    assert P2025 not in periods


def test_legacy_absent_null_and_store_only_payloads_remain_compatible():
    payload = _base_payload()
    fin = standardized_from_payload(payload)
    assert fin.historical_operating_kpis is None
    assert "historical_operating_kpis" not in standardized_to_payload(fin)
    payload["historical_operating_kpis"] = None
    assert standardized_from_payload(payload).historical_operating_kpis is None

    store = _fin_with_operating_kpis(
        _kpi_model_observation(P2025, 767),
        _kpi_model_observation(P2026, 811),
        extra_periods=[P2025, P2026],
    )
    serialized = standardized_to_payload(store)
    assert "management_observations" not in serialized["historical_operating_kpis"]
    restored = standardized_from_payload(serialized)
    assert restored.historical_operating_kpis.management_observations == []
    assert restored.historical_operating_kpis.observations == store.historical_operating_kpis.observations
    again = standardized_to_payload(restored)
    assert "management_observations" not in again["historical_operating_kpis"]
    assert again["historical_operating_kpis"]["observations"] == serialized["historical_operating_kpis"]["observations"]


def test_mixed_store_and_management_round_trip_and_growth():
    stores = [
        _kpi_model_observation(P2023, 655),
        _kpi_model_observation(P2024, 711),
        _kpi_model_observation(P2025, 767),
        _kpi_model_observation(P2026, 811),
    ]
    store_only = _fin_with_operating_kpis(*stores, extra_periods=AXIS)
    mixed = _fin_with_operating_kpis(
        *stores,
        management=_both_family_observations(),
        extra_periods=AXIS,
    )
    store_series = compute_operating_kpi_series(store_only)
    mixed_series = compute_operating_kpi_series(mixed)
    assert operating_kpi_applicable(store_only) is True
    assert operating_kpi_applicable(mixed) is True
    for period in AXIS:
        assert mixed_series.period_end_count[period] == store_series.period_end_count[period]
        assert mixed_series.net_count_change[period] == store_series.net_count_change[period]
        left = mixed_series.growth[period]
        right = store_series.growth[period]
        if isinstance(left, float) and isinstance(right, float):
            assert abs(left - right) <= OPERATING_KPI_RATIO_TOLERANCE
        else:
            assert left == right
    payload = _assert_export_reload_export(mixed)
    kpi = payload["historical_operating_kpis"]
    assert [row["value"] for row in kpi["observations"]] == [655, 711, 767, 811]
    restored = standardized_from_payload(payload)
    reloaded = compute_operating_kpi_series(restored)
    expected = _independent_from_counts(
        canonical_fiscal_periods(restored),
        {P2023: 655, P2024: 711, P2025: 767, P2026: 811},
    )
    _assert_series_matches(reloaded, expected)
    assert mixed.units == "USD in Thousands"
    percents = [
        row["value"]
        for row in kpi["management_observations"]
        if row["unit"] == UNIT_PERCENT
    ]
    assert -3 in percents
    assert 0 in percents


def test_management_only_does_not_activate_store_module():
    fin = _both_family_fin()
    assert fin.historical_operating_kpis.observations == []
    assert operating_kpi_applicable(fin) is False
    with pytest.raises(MissingLineError, match="operating KPI sources not available"):
        compute_operating_kpi_series(fin)
    payload = standardized_to_payload(fin)
    assert payload["historical_operating_kpis"]["observations"] == []
    assert payload["historical_operating_kpis"]["management_observations"]


def test_automatic_admission_does_not_promote_management_histories(tmp_path):
    before = _bytes_by_name(EXTRACTED)
    mixed = _copy_json(ANNUAL_NAMES + MANAGEMENT_NAMES, tmp_path / "mixed")
    annual = _copy_json(ANNUAL_NAMES, tmp_path / "annual")
    mixed_validated = load_and_validate_extracted_dir(mixed, source_root=SOURCE)
    annual_validated = load_and_validate_extracted_dir(annual, source_root=SOURCE)
    mixed_reconciled = reconcile_filings(mixed_validated, admit_periods=(date(2022, 1, 30),))
    annual_reconciled = reconcile_filings(annual_validated, admit_periods=(date(2022, 1, 30),))
    mixed_fin = standardize_reconciled(mixed_reconciled)
    annual_fin = standardize_reconciled(annual_reconciled)
    assert mixed_fin.historical_operating_kpis is None
    assert annual_fin.historical_operating_kpis is None
    mixed_payload = standardized_to_payload(mixed_fin)
    annual_payload = standardized_to_payload(annual_fin)
    assert "historical_operating_kpis" not in mixed_payload
    assert "historical_operating_kpis" not in annual_payload
    admission = mixed_reconciled.management_admission
    assert admission is not None
    assert admission.status == "admitted_unreconciled"
    payload = management_admission_payload(admission)
    assert payload["canonical_selection"] == "deferred"
    assert payload["assessments"]["canonical_selection"] == "deferred"
    reported = [item for item in admission.observations if item.kind == "reported_kpi"]
    assert len(reported) == 135
    assert payload["reported_observation_count"] == 135
    assert _bytes_by_name(EXTRACTED) == before
    assert mixed_validated.management_documents
