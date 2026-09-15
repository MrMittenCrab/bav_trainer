"""Optional HistoricalSegmentData contract, serialization, and fail-closed validation."""

from __future__ import annotations

import copy
import math
from datetime import date

import pytest

from core.data.historical_segments import (
    FAMILY_CORPORATE,
    FAMILY_ITEMIZED,
    GEOGRAPHIC_SEGMENT_NAMESPACE,
    IFOP_CORPORATE,
    OP_ADD,
    OP_SUBTRACT,
    SEGMENT_BRIDGE_TOLERANCE,
)
from core.data.interface import (
    FinancialPeriod,
    HistoricalSegmentData,
    HistoricalSegmentPeriod,
    LineItem,
    StandardizedFinancials,
)
from core.data.standardized_io import standardized_from_payload, standardized_to_payload

P1 = date(2024, 12, 31)
P2 = date(2025, 12, 31)


def _corp_values(
    rev: tuple[float, float, float] = (80.0, 25.0, 15.0),
    ifop: tuple[float, float, float] = (50.0, 18.0, 7.0),
    corporate: float = -25.0,
) -> dict[str, float]:
    a, cm, row = rev
    ia, icm, irow = ifop
    return {
        "net_revenue.americas": float(a),
        "net_revenue.china_mainland": float(cm),
        "net_revenue.rest_of_world": float(row),
        "net_revenue.segment_total": float(a + cm + row),
        "net_revenue.consolidated": float(a + cm + row),
        "income_from_operations.americas": float(ia),
        "income_from_operations.china_mainland": float(icm),
        "income_from_operations.rest_of_world": float(irow),
        "income_from_operations.segment_total": float(ia + icm + irow),
        IFOP_CORPORATE: float(corporate),
        "income_from_operations.consolidated": float(ia + icm + irow + corporate),
    }


def _itemized_values() -> dict[str, float]:
    return {
        "net_revenue.americas": 50.0,
        "net_revenue.china_mainland": 30.0,
        "net_revenue.rest_of_world": 20.0,
        "net_revenue.consolidated": 100.0,
        "income_from_operations.americas": 40.0,
        "income_from_operations.china_mainland": 20.0,
        "income_from_operations.rest_of_world": 10.0,
        "income_from_operations.segment_total": 70.0,
        "income_from_operations.consolidated": 55.0,
        "ifop_reconciling.general_corporate_expenses": 12.0,
        "ifop_reconciling.amortization_of_intangible_assets": 3.0,
    }


def _snapshot(
    period: date,
    *,
    family: str = FAMILY_CORPORATE,
    values: dict[str, float] | None = None,
    operations: dict[str, str] | None = None,
) -> HistoricalSegmentPeriod:
    if values is None:
        values = _corp_values() if family == FAMILY_CORPORATE else _itemized_values()
    if operations is None:
        if family == FAMILY_CORPORATE:
            operations = {IFOP_CORPORATE: OP_ADD}
        else:
            operations = {
                "ifop_reconciling.amortization_of_intangible_assets": OP_SUBTRACT,
                "ifop_reconciling.general_corporate_expenses": OP_SUBTRACT,
            }
    return HistoricalSegmentPeriod(
        period=period,
        presentation_family=family,
        values=dict(values),
        bridge_operations=dict(operations),
    )


def _base_payload() -> dict:
    return {
        "ticker": "T",
        "company_name": "Co",
        "currency": "USD",
        "units": "USD in Thousands",
        "jurisdiction": "US",
        "stock_code": "",
        "periods": [
            {"end_date": P2.isoformat(), "label": "FY2025", "is_interim": False},
        ],
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
    }


def _fin_with_segment(
    *snapshots: HistoricalSegmentPeriod,
    extra_periods: list[date] | None = None,
) -> StandardizedFinancials:
    snaps = list(snapshots) or [_snapshot(P2)]
    dates = extra_periods or [snap.period for snap in snaps]
    revenue_values = {
        snap.period: snap.values["net_revenue.consolidated"] for snap in snaps
    }
    ifop_values = {
        snap.period: snap.values["income_from_operations.consolidated"]
        for snap in snaps
    }
    for period in dates:
        revenue_values.setdefault(period, 0.0)
        ifop_values.setdefault(period, 0.0)
    return StandardizedFinancials(
        ticker="T",
        company_name="Co",
        currency="USD",
        units="USD in Thousands",
        jurisdiction="US",
        periods=[
            FinancialPeriod(end_date=period, label=f"FY{period.year}")
            for period in dates
        ],
        income_statement=[
            LineItem(label="Net revenue", concept="revenue", values=revenue_values),
            LineItem(
                label="Income from operations",
                concept="operating_income",
                values=ifop_values,
            ),
        ],
        historical_segment=HistoricalSegmentData(
            namespace=GEOGRAPHIC_SEGMENT_NAMESPACE,
            periods=snaps,
        ),
    )


def test_absent_and_null_historical_segment_are_equivalent():
    payload = _base_payload()
    fin = standardized_from_payload(payload)
    assert fin.historical_segment is None
    out = standardized_to_payload(fin)
    assert "historical_segment" not in out

    payload["historical_segment"] = None
    assert standardized_from_payload(payload).historical_segment is None
    assert "historical_segment" not in standardized_to_payload(
        standardized_from_payload(payload)
    )


def test_corporate_and_itemized_round_trip_preserves_semantics():
    fin = _fin_with_segment(_snapshot(P1, family=FAMILY_ITEMIZED), _snapshot(P2))
    payload = standardized_to_payload(fin)
    assert payload["historical_segment"]["namespace"] == GEOGRAPHIC_SEGMENT_NAMESPACE
    restored = standardized_from_payload(payload)
    assert restored.historical_segment == fin.historical_segment
    itemized, corporate = restored.historical_segment.periods
    assert itemized.presentation_family == FAMILY_ITEMIZED
    assert itemized.bridge_operations == {
        "ifop_reconciling.amortization_of_intangible_assets": OP_SUBTRACT,
        "ifop_reconciling.general_corporate_expenses": OP_SUBTRACT,
    }
    assert corporate.presentation_family == FAMILY_CORPORATE
    assert corporate.bridge_operations == {IFOP_CORPORATE: OP_ADD}
    assert "net_revenue.china_mainland" in itemized.values
    assert "net_revenue.prc" not in itemized.values
    assert "source_file" not in payload["historical_segment"]
    assert "selection_reason" not in payload["historical_segment"]["periods"][0]


def test_legacy_export_without_segment_field_is_unchanged():
    payload = _base_payload()
    restored = standardized_from_payload(payload)
    assert list(standardized_to_payload(restored)) == [
        "ticker",
        "company_name",
        "currency",
        "units",
        "jurisdiction",
        "stock_code",
        "periods",
        "income_statement",
        "balance_sheet",
        "cash_flow",
        "historical_shares",
        "historical_lease",
    ]


def test_malformed_supplied_segment_fails_closed_without_mutating_payload():
    fin = _fin_with_segment()
    original = copy.deepcopy(standardized_to_payload(fin))
    payload = copy.deepcopy(original)

    payload["historical_segment"] = "bad"
    with pytest.raises(ValueError, match="historical_segment must be an object"):
        standardized_from_payload(payload)
    assert payload["historical_segment"] == "bad"

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"] = []
    with pytest.raises(ValueError, match="non-empty list"):
        standardized_from_payload(payload)
    assert original["historical_segment"]["periods"]

    payload = copy.deepcopy(original)
    payload["historical_segment"]["namespace"] = "segment.channel.retail"
    with pytest.raises(ValueError, match="unsupported geographic namespace"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"]["net_revenue.americas"] = math.inf
    with pytest.raises(ValueError, match="non-finite"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"]["channel.ecomm"] = 1.0
    with pytest.raises(ValueError, match="unknown"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"]["country.us"] = 1.0
    with pytest.raises(ValueError, match="unknown"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["period"] = "not-a-date"
    with pytest.raises(ValueError):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"].append(
        copy.deepcopy(payload["historical_segment"]["periods"][0])
    )
    with pytest.raises(ValueError, match="duplicate geographic period"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["period"] = "2020-01-01"
    with pytest.raises(ValueError, match="outside the model axis"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    del payload["historical_segment"]["periods"][0]["values"]["net_revenue.americas"]
    with pytest.raises(ValueError, match="incomplete geographic bridge group"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"][
        "ifop_reconciling.general_corporate_expenses"
    ] = 1.0
    with pytest.raises(ValueError, match="corporate double counting"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"]["net_revenue.americas"] += 10
    with pytest.raises(ValueError, match="revenue bridge mismatch"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["income_statement"][0]["values"][P2.isoformat()] += 1
    with pytest.raises(ValueError, match="disagrees with IS revenue"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["bridge_operations"] = {
        IFOP_CORPORATE: OP_SUBTRACT
    }
    with pytest.raises(ValueError, match="bridge operations contradict"):
        standardized_from_payload(payload)

    payload = copy.deepcopy(original)
    payload["historical_segment"]["periods"][0]["values"]["net_revenue.americas"] = None
    with pytest.raises(ValueError, match="non-numeric"):
        standardized_from_payload(payload)

    assert original == standardized_to_payload(fin)


def test_itemized_bridge_uses_reported_signs_and_subtract():
    snap = _snapshot(P2, family=FAMILY_ITEMIZED)
    fin = _fin_with_segment(snap)
    restored = standardized_from_payload(standardized_to_payload(fin))
    values = restored.historical_segment.periods[0].values
    assert (
        values["income_from_operations.segment_total"]
        - values["ifop_reconciling.general_corporate_expenses"]
        - values["ifop_reconciling.amortization_of_intangible_assets"]
        == values["income_from_operations.consolidated"]
    )
    assert SEGMENT_BRIDGE_TOLERANCE == 0.0


def test_missing_periods_are_not_filled():
    snap = _snapshot(P2)
    fin = _fin_with_segment(snap, extra_periods=[P1, P2])
    restored = standardized_from_payload(standardized_to_payload(fin))
    assert [item.period for item in restored.historical_segment.periods] == [P2]
    assert P1 not in restored.historical_segment.periods[0].values
