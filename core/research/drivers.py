"""Publish Drivers Markdown and figures from validated BAV outputs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..data.historical_operating_kpis import FAMILY_COMPARABLE_SALES_GROWTH
from ..data.interface import StandardizedFinancials
from ..model.geographic_segment import (
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from ..model.line_resolver import resolve_line
from ..model.management_kpi import compute_management_kpi_series, management_kpi_applicable
from ..model.operating_kpi import compute_operating_kpi_series, operating_kpi_applicable
from ..model.operating_kpi_relationships import (
    compute_operating_kpi_revenue_store_relationship,
)
from ..model.period_axis import canonical_fiscal_periods
from ..model.ratio_values import is_source_unavailable
from ..model.reported_margin import (
    compute_reported_margin_series,
    reported_operating_margin_applicable,
)
from ..model.revenue_driver import (
    THEME_COMPARABLE_SALES,
    THEME_GEOGRAPHIC_GROWTH,
    THEME_STORE_EXPANSION,
    compute_revenue_driver_analysis,
    revenue_driver_applicable,
)
from ..model.revenue_per_store import compute_revenue_per_store_series
from .style import ResearchStyle, apply_research_style, finish_figure, new_figure

RESERVED_MODULES = ("Forecast", "Valuation", "Overview")
PEER_SECTIONS = (
    "## Context",
    "## Growth",
    "## Geography",
    "## Margin",
    "## Conclusions",
    "## Limits",
)


def drivers_filename(company: str) -> str:
    return f"{company}_Drivers.md"


def placeholder_filenames(company: str) -> tuple[str, ...]:
    return tuple(f"{company}_{module}.md" for module in RESERVED_MODULES)


def drivers_heading(company: str) -> str:
    return f"# {company} — Drivers"


def expected_sections(company: str) -> tuple[str, ...]:
    return (drivers_heading(company),) + PEER_SECTIONS
FIGURE_NAMES = ("growth.png", "geography.png", "margin.png")
SEGMENT_LABELS = {
    "americas": "Americas",
    "china_mainland": "China Mainland",
    "rest_of_world": "Rest of World",
}
POPULATION_LABELS = {
    "company_operated_stores": "company-operated stores",
    "company_operated_stores_and_direct_to_consumer": (
        "company-operated stores and direct-to-consumer"
    ),
    "company_operated_stores_and_ecommerce": (
        "company-operated stores and e-commerce"
    ),
}


def _numeric(value) -> float | None:
    if value is None or is_source_unavailable(value) or isinstance(value, str):
        return None
    return float(value)


_JAN31_FOLLOWING_YEAR = "Sunday closest to January 31 of the following year"
_EXCLUDED_EXTRA_WEEK = "excluded"


def _label_for(financials: StandardizedFinancials, period: date) -> str:
    for item in financials.periods:
        if item.end_date == period:
            return item.label
    return period.isoformat()


def _fifty_three_week_period(
    financials: StandardizedFinancials, axis: tuple[date, ...]
) -> date | None:
    data = financials.historical_operating_kpis
    if data is None:
        return None
    found = {
        item.period
        for item in data.management_observations
        if item.period in axis and item.calendar_week_adjustment == _EXCLUDED_EXTRA_WEEK
    }
    if len(found) != 1:
        return None
    return next(iter(found))


def _issuer_fiscal_name(
    financials: StandardizedFinancials, period: date
) -> str | None:
    data = financials.historical_operating_kpis
    if data is None:
        return None
    for item in data.management_observations:
        if item.period != period:
            continue
        if _JAN31_FOLLOWING_YEAR not in item.calendar_reporting_basis:
            continue
        label = _label_for(financials, period)
        token = _fiscal_year_token(label)
        if not token.isdigit():
            return None
        return f"fiscal {token}"
    return None


def _calendar_limitation(view: "DriversView") -> str:
    period = view.fifty_three_week_period
    if period is None or period not in view.periods:
        return ""
    label = view.labels[view.periods.index(period)]
    naming = ""
    issuer = view.issuer_fiscal_name
    if issuer and _fiscal_year_token(issuer) != _fiscal_year_token(label):
        naming = f"; the issuer names it {issuer}"
    return (
        f"{label}, the year ended {_date_text(period)}, is a 53-week year{naming}. "
        "Some later comparable-sales presentations exclude or realign that extra "
        "week and cannot be joined to the earlier observations."
    )


def _calendar_limit_block(view: "DriversView") -> str:
    text = _calendar_limitation(view)
    if not text:
        return ""
    return f"\n{text}\n"


def _fiscal_year_token(label: str) -> str:
    text = label.casefold().replace("fiscal ", "").replace("fy", "").strip()
    return text


def _date_text(period: date) -> str:
    return period.strftime("%-d %B %Y")


def _millions(thousands: float) -> float:
    return round(thousands / 1000.0, 1)


def _pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"


def _pp(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f} pp"


def _money(millions: float) -> str:
    return f"${millions:,.1f} million"


@dataclass(frozen=True)
class ComparableSalesPoint:
    period: date
    percent: float
    population: str
    basis: str


@dataclass(frozen=True)
class DriversView:
    """Numbers for Markdown and figures; all from the same BAV compute path."""

    company_name: str
    display_name: str
    currency: str
    units: str
    periods: tuple[date, ...]
    labels: tuple[str, ...]
    revenue: tuple[float, ...]
    operating_profit: tuple[float, ...]
    operating_margin: tuple[float, ...]
    gross_margin: tuple[float, ...]
    net_operating_expense_burden: tuple[float, ...]
    gross_margin_change: tuple[float | None, ...]
    net_operating_expense_burden_change: tuple[float | None, ...]
    operating_margin_change: tuple[float | None, ...]
    stores: tuple[float, ...]
    revenue_growth: tuple[float | None, ...]
    store_growth: tuple[float | None, ...]
    revenue_per_store: tuple[float, ...]
    comparable_sales: tuple[ComparableSalesPoint, ...]
    store_only_comparable_sales: ComparableSalesPoint | None
    geo_identities: tuple[str, ...]
    geo_contributions: tuple[dict[str, float | None], ...]
    consolidated_revenue_growth: tuple[float | None, ...]
    fifty_three_week_period: date | None = None
    issuer_fiscal_name: str | None = None

    def period_ended(self, period: date) -> str:
        return _date_text(period)


def assemble_drivers_view(
    financials: StandardizedFinancials, display_name: str
) -> DriversView:
    if not revenue_driver_applicable(financials):
        raise ValueError("Drivers requires historical strategy and driver analysis")
    if not operating_kpi_applicable(financials):
        raise ValueError("Drivers requires company-operated store history")
    if not geographic_segment_applicable(financials):
        raise ValueError("Drivers requires geographic segment history")
    if not reported_operating_margin_applicable(financials):
        raise ValueError("Drivers requires reported operating margin")
    axis = canonical_fiscal_periods(financials)
    revenue_item = resolve_line(financials.income_statement, "revenue", required=True).item
    operating_item = resolve_line(
        financials.income_statement, "operating_profit", required=True
    ).item
    stores = compute_operating_kpi_series(financials, list(axis))
    relationship = compute_operating_kpi_revenue_store_relationship(financials, list(axis))
    margins = compute_reported_margin_series(financials, list(axis))
    rps = compute_revenue_per_store_series(financials, list(axis))
    geo = compute_geographic_segment_series(financials)
    analysis = compute_revenue_driver_analysis(financials)
    compsales_test = next(
        item for item in analysis.tests if item.theme == THEME_COMPARABLE_SALES
    )
    points: list[ComparableSalesPoint] = []
    seen: set[date] = set()
    for observation in compsales_test.observations:
        percent = _numeric(observation.inputs.get("comparable_sales_percent"))
        if percent is None or observation.period in seen:
            continue
        if observation.inputs.get("basis") != "reported":
            continue
        seen.add(observation.period)
        points.append(
            ComparableSalesPoint(
                observation.period,
                percent,
                str(observation.inputs.get("population") or ""),
                "reported",
            )
        )
    store_only = None
    if management_kpi_applicable(financials):
        series = compute_management_kpi_series(financials, list(axis))
        for identity in series.identities:
            item = series.series[identity]
            if item.family != FAMILY_COMPARABLE_SALES_GROWTH:
                continue
            if item.population != "company_operated_stores" or item.basis != "reported":
                continue
            for period in axis:
                value = _numeric(item.reported_value.get(period))
                if value is None:
                    continue
                store_only = ComparableSalesPoint(
                    period, value, item.population, item.basis
                )
                break
    store_test = next(item for item in analysis.tests if item.theme == THEME_STORE_EXPANSION)
    geo_test = next(item for item in analysis.tests if item.theme == THEME_GEOGRAPHIC_GROWTH)
    if store_test.sample_size != 4 or geo_test.sample_size != 4:
        raise ValueError("Drivers expected four aligned growth and geographic periods")
    week_period = _fifty_three_week_period(financials, tuple(axis))
    issuer_name = (
        _issuer_fiscal_name(financials, week_period) if week_period is not None else None
    )
    if (
        margins.gross_margin is None
        or margins.net_operating_expense_burden is None
        or margins.gross_margin_change is None
        or margins.net_operating_expense_burden_change is None
        or margins.reconstructed_operating_margin_change is None
    ):
        raise ValueError("Drivers requires the validated three-component margin bridge")
    return DriversView(
        company_name=financials.company_name,
        display_name=display_name,
        currency=financials.currency,
        units=financials.units,
        periods=tuple(axis),
        labels=tuple(_label_for(financials, period) for period in axis),
        revenue=tuple(float(revenue_item.values[period]) for period in axis),
        operating_profit=tuple(float(operating_item.values[period]) for period in axis),
        operating_margin=tuple(float(value) for value in margins.reported_operating_margin),
        gross_margin=tuple(float(value) for value in margins.gross_margin),
        net_operating_expense_burden=tuple(
            float(value) for value in margins.net_operating_expense_burden
        ),
        gross_margin_change=tuple(
            _numeric(value) for value in margins.gross_margin_change
        ),
        net_operating_expense_burden_change=tuple(
            _numeric(value) for value in margins.net_operating_expense_burden_change
        ),
        operating_margin_change=tuple(
            _numeric(value) for value in margins.reconstructed_operating_margin_change
        ),
        stores=tuple(float(stores.period_end_count[period]) for period in axis),
        revenue_growth=tuple(
            _numeric(relationship.revenue_growth[period]) for period in axis
        ),
        store_growth=tuple(
            _numeric(relationship.store_count_growth[period]) for period in axis
        ),
        revenue_per_store=tuple(
            float(rps.period_end_revenue_per_store[period]) for period in axis
        ),
        comparable_sales=tuple(points),
        store_only_comparable_sales=store_only,
        geo_identities=geo.identities,
        geo_contributions=tuple(
            {
                identity: _numeric(geo.revenue_growth_contribution[period][identity])
                for identity in geo.identities
            }
            for period in axis
        ),
        consolidated_revenue_growth=tuple(
            _numeric(geo.consolidated_revenue_growth[period]) for period in axis
        ),
        fifty_three_week_period=week_period,
        issuer_fiscal_name=issuer_name,
    )


def render_drivers_markdown(view: DriversView) -> str:
    rows = [
        "| Fiscal year | Period ended | Revenue | Operating profit | Operating margin | Company-operated stores |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for index, period in enumerate(view.periods):
        rows.append(
            "| {label} | {ended} | {rev} | {op} | {om} | {stores} |".format(
                label=view.labels[index],
                ended=_date_text(period),
                rev=_money(_millions(view.revenue[index])),
                op=_money(_millions(view.operating_profit[index])),
                om=_pct(view.operating_margin[index], 1),
                stores=f"{view.stores[index]:.0f}",
            )
        )
    growth_periods = [
        (view.labels[i], view.revenue_growth[i], view.store_growth[i])
        for i in range(len(view.periods))
        if view.revenue_growth[i] is not None and view.store_growth[i] is not None
    ]
    rev_growth_text = ", ".join(_pct(item[1]) for item in growth_periods)
    store_growth_text = ", ".join(_pct(item[2]) for item in growth_periods)
    latest = next(
        i
        for i in range(len(view.periods) - 1, -1, -1)
        if view.revenue_growth[i] is not None
    )
    compsales_parts = []
    for point in view.comparable_sales:
        label = view.labels[view.periods.index(point.period)]
        compsales_parts.append(
            f"{point.percent:.0f}% in {label} on a "
            f"{POPULATION_LABELS.get(point.population, point.population)} basis"
        )
    compsales_text = "; ".join(compsales_parts)
    store_only_text = ""
    if view.store_only_comparable_sales is not None:
        point = view.store_only_comparable_sales
        store_only_text = (
            f" {view.labels[view.periods.index(point.period)]} also reported "
            f"{point.percent:.0f}% on a store-only basis."
        )
    geo_years = [
        i
        for i in range(len(view.periods))
        if any(value is not None for value in view.geo_contributions[i].values())
    ]
    americas = [
        _pp(view.geo_contributions[i]["americas"])
        for i in geo_years
        if view.geo_contributions[i]["americas"] is not None
    ]
    china = [
        _pp(view.geo_contributions[i]["china_mainland"])
        for i in geo_years
        if view.geo_contributions[i]["china_mainland"] is not None
    ]
    row = [
        _pp(view.geo_contributions[i]["rest_of_world"])
        for i in geo_years
        if view.geo_contributions[i]["rest_of_world"] is not None
    ]
    latest_geo = view.geo_contributions[latest]
    om_text = ", ".join(
        f"{_pct(view.operating_margin[i], 1)} in {view.labels[i]}"
        for i in range(len(view.periods))
    )
    gm_text = ", ".join(
        f"{_pct(view.gross_margin[i], 1)} in {view.labels[i]}"
        for i in range(len(view.periods))
    )
    burden_text = ", ".join(
        f"{_pct(view.net_operating_expense_burden[i], 1)} in {view.labels[i]}"
        for i in range(len(view.periods))
    )
    gm_change = view.gross_margin_change[latest]
    burden_change = view.net_operating_expense_burden_change[latest]
    om_change = view.operating_margin_change[latest]
    if gm_change is None or burden_change is None or om_change is None:
        raise ValueError("Drivers requires a latest-period margin decomposition")
    om_change_pp = om_change * 100
    gm_change_pp = gm_change * 100
    burden_change_pp = burden_change * 100
    if abs(om_change_pp - (gm_change_pp - burden_change_pp)) > 1e-9:
        raise ValueError("latest operating-margin change does not equal GM change minus burden change")
    definition_period = (
        view.store_only_comparable_sales.period
        if view.store_only_comparable_sales is not None
        else view.comparable_sales[0].period
    )
    body = f"""{drivers_heading(view.display_name)}

## Context

{view.display_name} designs and sells athletic apparel through company-operated stores and digital channels. The history covers five fiscal years ended {_date_text(view.periods[0])} through {_date_text(view.periods[-1])}.

Amounts are {view.units}, shown in millions of {view.currency}.

{chr(10).join(rows)}

## Growth

Consolidated revenue rose from {_money(_millions(view.revenue[0]))} to {_money(_millions(view.revenue[-1]))}. Year-on-year growth was {rev_growth_text}.

Company-operated stores increased from {view.stores[0]:.0f} to {view.stores[-1]:.0f}. Store-count growth was {store_growth_text}.

In {view.labels[latest]}, store-count growth ({_pct(view.store_growth[latest])}) exceeded revenue growth ({_pct(view.revenue_growth[latest])}).

Reported global comparable sales were {compsales_text}.{store_only_text} These percentages use different channel definitions.

![Consolidated revenue growth and company-operated store-count growth](../figures/drivers/growth.png)

## Geography

Americas remained the largest region and supplied less of each year's incremental revenue: {", ".join(americas)}.

China Mainland contributed {", ".join(china)}.

Rest of World contributed {", ".join(row)}.

In {view.labels[latest]}, China Mainland ({_pp(latest_geo["china_mainland"])}) and Rest of World ({_pp(latest_geo["rest_of_world"])}) more than offset Americas ({_pp(latest_geo["americas"])}).

![Geographic contribution to consolidated revenue growth](../figures/drivers/geography.png)

## Margin

Operating margin was {om_text}.

In {view.labels[latest]}, operating-margin change was {om_change_pp:+.2f} pp, equal to the gross-margin change ({gm_change_pp:+.2f} pp) minus the net-operating-expense-burden change ({burden_change_pp:+.2f} pp).

Gross margin was {gm_text}. Net operating expense burden was {burden_text}.

Management explanations of the latest operating-margin movement are unavailable.

![Gross margin, net operating expense burden, and operating margin](../figures/drivers/margin.png)

## Conclusions

1. Revenue grew in every year and slowed from {_pct(growth_periods[0][1])} to {_pct(growth_periods[-1][1])} as stores rose from {view.stores[0]:.0f} to {view.stores[-1]:.0f}.
2. In {view.labels[latest]}, stores grew faster than revenue ({_pct(view.store_growth[latest])} versus {_pct(view.revenue_growth[latest])}).
3. Incremental revenue shifted toward China Mainland and Rest of World; Americas contributed {_pp(latest_geo["americas"])} in {view.labels[latest]}.
4. Operating margin recovered from {_pct(view.operating_margin[1], 1)} in {view.labels[1]} to {_pct(view.operating_margin[-2], 1)} in {view.labels[-2]}, then fell to {_pct(view.operating_margin[-1], 1)} in {view.labels[-1]}.
5. Reported comparable sales were positive in each observed year, on changing definitions.

## Limits

Comparable sales cannot be read as a continuous series. The year ended {_date_text(definition_period)} reports both a store-only series and a stores-plus-direct-to-consumer series; later years report stores plus e-commerce. Reported and constant-currency figures are separate.

Geographic contributions split reported-currency revenue change. They are not organic growth, constant-currency growth, or a causal explanation.

Sales per square foot cannot support a productivity reading. The {_date_text(definition_period)} filings disagree on the definition, later years do not line up on calendar and definition, and year-to-year sales-per-square-foot growth is not available. Revenue divided by stores is not store productivity.
{_calendar_limit_block(view)}"""
    return body


def _figure_period_label(view: DriversView, index: int) -> str:
    return f"{view.labels[index]}\n{view.periods[index].strftime('%-d %b %Y')}"


def _growth_labels(view: DriversView) -> list[str]:
    return [
        _figure_period_label(view, i)
        for i in range(len(view.periods))
        if view.revenue_growth[i] is not None
    ]


def plot_growth(view: DriversView, path: Path, style: ResearchStyle) -> None:
    fig, ax = new_figure(style)
    indexes = [
        i for i in range(len(view.periods)) if view.revenue_growth[i] is not None
    ]
    labels = _growth_labels(view)
    x = list(range(len(indexes)))
    width = 0.36
    revenue = [view.revenue_growth[i] * 100 for i in indexes]
    stores = [view.store_growth[i] * 100 for i in indexes]
    ax.bar(
        [i - width / 2 for i in x],
        revenue,
        width=width,
        color=style.series_color(0),
        label="Consolidated revenue growth",
    )
    ax.bar(
        [i + width / 2 for i in x],
        stores,
        width=width,
        color=style.series_color(1),
        label="Company-operated store-count growth",
    )
    compsales = {point.period: point for point in view.comparable_sales}
    marker_x = []
    marker_y = []
    for position, index in enumerate(indexes):
        point = compsales.get(view.periods[index])
        if point is None:
            continue
        marker_x.append(position)
        marker_y.append(point.percent)
    if marker_x:
        ax.plot(
            marker_x,
            marker_y,
            linestyle="None",
            marker="o",
            markersize=5,
            color=style.series_color(2),
            label="Reported comparable sales, period-specific definition",
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Percent")
    ax.axhline(0, color=style.black, linewidth=0.8)
    ax.legend(loc="upper right")
    finish_figure(
        fig,
        ax,
        style,
        "Revenue growth, store-count growth, and reported comparable sales",
        f"Source: {view.display_name} BAV income statement and company-operated store counts.\n"
        "Comparable sales use the reported global definition of each year and are not one series.",
        path,
    )


def plot_geography(view: DriversView, path: Path, style: ResearchStyle) -> None:
    fig, ax = new_figure(style)
    indexes = [
        i
        for i in range(len(view.periods))
        if any(value is not None for value in view.geo_contributions[i].values())
    ]
    labels = _growth_labels(view)
    x = list(range(len(indexes)))
    width = 0.24
    for series_index, identity in enumerate(view.geo_identities):
        values = [view.geo_contributions[i][identity] for i in indexes]
        offset = (series_index - 1) * width
        ax.bar(
            [position + offset for position in x],
            values,
            width=width,
            color=style.series_color(series_index),
            label=SEGMENT_LABELS[identity],
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Percentage-point contribution")
    ax.axhline(0, color=style.black, linewidth=0.8)
    ax.legend(loc="upper right")
    finish_figure(
        fig,
        ax,
        style,
        "Geographic contribution to consolidated revenue growth",
        f"Source: {view.display_name} BAV geographic segment analysis.\n"
        "Contributions are an arithmetic split of reported-currency revenue change.",
        path,
    )


def plot_margin(view: DriversView, path: Path, style: ResearchStyle) -> None:
    fig, ax = new_figure(style)
    labels = [_figure_period_label(view, i) for i in range(len(view.periods))]
    x = list(range(len(view.periods)))
    series = (
        (view.gross_margin, "Gross margin"),
        (view.net_operating_expense_burden, "Net operating expense burden"),
        (view.operating_margin, "Operating margin"),
    )
    for series_index, (values, label) in enumerate(series):
        ax.plot(
            x,
            [value * 100 for value in values],
            color=style.series_color(series_index),
            marker="o",
            markersize=5,
            linewidth=1.2,
            label=label,
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Percent of revenue")
    ax.legend(loc="upper right")
    finish_figure(
        fig,
        ax,
        style,
        "Gross margin, net operating expense burden, and operating margin",
        f"Source: {view.display_name} BAV income statement.\n"
        "Operating-margin change equals gross-margin change minus net-operating-expense-burden change.",
        path,
    )


def write_placeholders(research_dir: Path, company: str) -> None:
    research_dir.mkdir(parents=True, exist_ok=True)
    for name in placeholder_filenames(company):
        (research_dir / name).write_bytes(b"")


def publish_drivers(
    financials: StandardizedFinancials,
    output: Path,
    *,
    display_name: str,
    accent: str | None = None,
) -> DriversView:
    view = assemble_drivers_view(financials, display_name)
    style = apply_research_style(accent=accent)
    research_dir = output / "research"
    figures_dir = output / "figures" / "drivers"
    write_placeholders(research_dir, display_name)
    (research_dir / drivers_filename(display_name)).write_text(
        render_drivers_markdown(view), encoding="utf-8"
    )
    plot_growth(view, figures_dir / "growth.png", style)
    plot_geography(view, figures_dir / "geography.png", style)
    plot_margin(view, figures_dir / "margin.png", style)
    return view
