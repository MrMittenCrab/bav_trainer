"""Python-side financial computations — authoritative expected values for trainer Check."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .classification import (
    BalanceSheetReformulation,
    check_reformulation_integrity,
    reformulate_balance_sheet,
)
from .line_resolver import resolve_line
from .lease_liability import lease_liability_treatment
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
from .source_values import MissingHistoricalValueError, required_period_series


@dataclass(frozen=True)
class HistoricalSeries:
    """Full historical income-reformulation series (one value per fiscal period)."""

    revenue: list[float]
    net_income: list[float]
    pretax_income: list[float]
    tax_expense: list[float]
    effective_tax_rate: list[float | str]
    net_interest: list[float]
    net_interest_after_tax: list[float | str]
    nopat: list[float | str]


@dataclass
class AnchorMetrics:
    revenue: float
    nowc: float
    nola: float
    net_debt: float
    nopat: float | str
    equity: float
    noa: float
    leverage: float
    hist_avg_after_tax_cod: float  # already after-tax; do not multiply by (1 − tax) again
    effective_tax_rate: float | str
    net_interest: float
    net_interest_after_tax: float | str
    dupont: dict[str, list[float | str | None]]
    reformulation: BalanceSheetReformulation
    historical: HistoricalSeries


def compute_anchor(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    classification_overrides: dict[str, str] | None = None,
    enforce_integrity: bool = True,
    tolerance: float = 1.0,
) -> AnchorMetrics:
    """Compute anchor and historical metrics from standardized financials."""
    is_items = fin.income_statement
    n = len(periods)
    if n < 1:
        raise ValueError("At least one period required")

    reform = reformulate_balance_sheet(
        fin, periods, overrides=classification_overrides
    )
    if enforce_integrity:
        check_reformulation_integrity(reform, periods, tolerance=tolerance)

    rev_item = resolve_line(is_items, "revenue", required=True).item
    ni_item = resolve_line(is_items, "net_income", required=True).item
    pretax_item = resolve_line(is_items, "pretax_income", required=True).item
    tax_item = resolve_line(is_items, "tax_expense", required=True).item
    int_exp_item = resolve_line(is_items, "interest_expense", required=True).item
    int_inc_item = resolve_line(is_items, "interest_income", required=True).item
    assert rev_item is not None
    assert ni_item is not None
    assert pretax_item is not None
    assert tax_item is not None
    assert int_exp_item is not None
    assert int_inc_item is not None

    revenues = list(required_period_series(rev_item, periods, field="revenue"))
    ni = list(required_period_series(ni_item, periods, field="net_income"))
    pretax = list(required_period_series(pretax_item, periods, field="pretax_income"))
    tax = list(required_period_series(tax_item, periods, field="tax_expense"))
    int_exp = list(
        required_period_series(int_exp_item, periods, field="interest_expense")
    )
    int_inc = list(
        required_period_series(int_inc_item, periods, field="interest_income")
    )

    reported_net_int = [-(ie + ii) for ie, ii in zip(int_exp, int_inc)]
    if fin.historical_lease is None:
        net_int = list(reported_net_int)
    else:
        lease_interest: list[float] = []
        for period in periods:
            raw = fin.historical_lease.lease_interest_expense.get(period)
            if raw is None:
                raise MissingHistoricalValueError(
                    "historical_lease.lease_interest_expense has no supplied value "
                    f"for modeled period {period.isoformat()}"
                )
            lease_interest.append(float(raw))
        treatment = lease_liability_treatment(fin, reform)
        if treatment == "operating":
            net_int = [
                reported - lease
                for reported, lease in zip(reported_net_int, lease_interest)
            ]
        elif treatment == "financial":
            net_int = list(reported_net_int)
        else:
            # No usable lease source — leave reported financing net interest unchanged.
            net_int = list(reported_net_int)
    etr: list[float | str] = [ratio_or_na(-tax[i], pretax[i]) for i in range(n)]
    niat: list[float | str] = []
    nopat: list[float | str] = []
    for i in range(n):
        if net_int[i] == 0.0:
            niat_value: float | str = 0.0
        elif etr[i] == UNDEFINED_RATIO:
            niat_value = UNDEFINED_RATIO
        else:
            niat_value = net_int[i] * (1.0 - float(etr[i]))
        niat.append(niat_value)
        if niat_value == UNDEFINED_RATIO:
            nopat.append(UNDEFINED_RATIO)
        else:
            nopat.append(ni[i] + float(niat_value))

    nowc = list(reform.nowc)
    nola = list(reform.nola)
    noa = list(reform.noa)
    net_debt = list(reform.net_debt)
    equity = list(reform.implied_equity)

    def avg(series: list[float], i: int) -> float:
        if i == 0:
            return series[0]
        return (series[i] + series[i - 1]) / 2

    dupont: dict[str, list[float | str | None]] = {k: [] for k in [
        "Sales Growth", "NOPAT Margin", "RNOA", "After-tax CoD", "Spread",
        "FLEV", "ROE (decomposed)", "Actual ROE",
    ]}
    cod_series: list[float | str] = []
    for i in range(n):
        if i == 0:
            dupont["Sales Growth"].append(None)
            dupont["NOPAT Margin"].append(ratio_or_na(nopat[0], revenues[0]))
            dupont["RNOA"].append(None)
            dupont["After-tax CoD"].append(None)
            dupont["Spread"].append(None)
            dupont["FLEV"].append(None)
            dupont["ROE (decomposed)"].append(None)
            dupont["Actual ROE"].append(None)
            continue
        average_noa = avg(noa, i)
        average_net_debt = avg(net_debt, i)
        average_equity = avg(equity, i)
        rnoa = ratio_or_na(nopat[i], average_noa)
        cod = ratio_or_na(niat[i], average_net_debt)
        cod_series.append(cod)
        flev = ratio_or_na(average_net_debt, average_equity)
        if rnoa == UNDEFINED_RATIO or cod == UNDEFINED_RATIO:
            spread: float | str = UNDEFINED_RATIO
        else:
            spread = rnoa - cod
        if (
            rnoa == UNDEFINED_RATIO
            or flev == UNDEFINED_RATIO
            or spread == UNDEFINED_RATIO
        ):
            decomposed: float | str = UNDEFINED_RATIO
        else:
            decomposed = rnoa + flev * spread
        actual = ratio_or_na(ni[i], average_equity)
        base = ratio_or_na(revenues[i], revenues[i - 1])
        sales_growth = (
            UNDEFINED_RATIO if base == UNDEFINED_RATIO else base - 1.0
        )
        dupont["Sales Growth"].append(sales_growth)
        dupont["NOPAT Margin"].append(ratio_or_na(nopat[i], revenues[i]))
        dupont["RNOA"].append(rnoa)
        dupont["After-tax CoD"].append(cod)
        dupont["Spread"].append(spread)
        dupont["FLEV"].append(flev)
        dupont["ROE (decomposed)"].append(decomposed)
        dupont["Actual ROE"].append(actual)

    numeric_cod = [
        value for value in cod_series if isinstance(value, (int, float))
    ]
    hist_avg_cod = sum(numeric_cod) / len(numeric_cod) if numeric_cod else 0.04
    last = n - 1
    total_capital = net_debt[last] + equity[last]
    leverage = net_debt[last] / total_capital if total_capital else 0

    return AnchorMetrics(
        revenue=revenues[last],
        nowc=nowc[last],
        nola=nola[last],
        net_debt=net_debt[last],
        nopat=nopat[last],
        equity=equity[last],
        noa=noa[last],
        leverage=leverage,
        hist_avg_after_tax_cod=hist_avg_cod,
        effective_tax_rate=etr[last],
        net_interest=net_int[last],
        net_interest_after_tax=niat[last],
        dupont=dupont,
        reformulation=reform,
        historical=HistoricalSeries(
            revenue=list(revenues),
            net_income=list(ni),
            pretax_income=list(pretax),
            tax_expense=list(tax),
            effective_tax_rate=list(etr),
            net_interest=list(net_int),
            net_interest_after_tax=list(niat),
            nopat=list(nopat),
        ),
    )
