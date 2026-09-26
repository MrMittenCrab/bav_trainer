"""Publish Drivers Markdown and figures from validated BAV outputs."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
import re

from ..data.historical_operating_kpis import FAMILY_COMPARABLE_SALES_GROWTH
from ..data.historical_strategy import ROLE_ATTRIBUTION
from ..data.interface import StandardizedFinancials
from ..model.geographic_segment import (
    compute_geographic_segment_series,
    geographic_segment_applicable,
)
from ..model.inventory_analysis import (
    compute_inventory_analysis_series,
    inventory_analysis_applicable,
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
    MarginRelationshipAssessment,
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
from .selection import ResearchSelection, select_driver_argument
from .style import ResearchStyle, apply_research_style, finish_figure, new_figure

RESERVED_MODULES = ("Forecast", "Valuation", "Overview")
APPENDIX_HEADING = "## Appendix"
OBSOLETE_SECTIONS = (
    "## Context",
    "## Growth",
    "## Geography",
    "## Margin",
    "## Conclusions",
    "## Limits",
)
WORKPAPER_FIELDS = (
    "Kind",
    "Reconstruction",
    "Residual",
    "Stability",
    "Contradictions",
    "Result",
)
_CFO_EXCLUDED_CONCEPTS = frozenset(
    {
        "net_cash_from_operating_activities",
        "net_cash_from_investing_activities",
        "net_cash_from_financing_activities",
        "cash_beginning",
        "cash_ending",
        "change_in_cash",
        "effect_of_fx_on_cash",
        "capital_expenditures",
        "acquisition_net_of_cash_acquired",
        "other_investing_activities",
        "other_financing_activities",
        "proceeds_from_stock_based_compensation",
        "repurchase_of_common_stock",
        "shares_withheld_for_stock_based_compensation",
        "settlement_of_net_investment_hedges",
    }
)
_CFO_COMPONENT_HINTS = (
    "change_in_",
    "cash_flow_net_income",
    "deferred_income",
    "depreciation",
    "stock_based_compensation",
    "studio_obsolescence",
    "derecognition",
    "settlement_of_derivatives",
)


def drivers_filename(company: str) -> str:
    return f"{company}_Drivers.md"


def placeholder_filenames(company: str) -> tuple[str, ...]:
    return tuple(f"{company}_{module}.md" for module in RESERVED_MODULES)


def drivers_heading(company: str) -> str:
    return f"# {company} — Drivers"


def expected_sections(company: str) -> tuple[str, ...]:
    return (drivers_heading(company), APPENDIX_HEADING)


FIGURE_NAMES = ("growth.png", "geography.png", "margin.png", "cash.png")
FIGURE_PLOTTERS = {
    "growth.png": "plot_growth",
    "geography.png": "plot_geography",
    "margin.png": "plot_margin",
    "cash.png": "plot_cash",
}
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


def _attribution_amount(text: str) -> str | None:
    match = re.search(
        r"approximately\s+\$[0-9]+(?:\.[0-9]+)?\s+million",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(0) if match else None


def _attributions_from_financials(
    financials: StandardizedFinancials,
) -> tuple[ManagementAttribution, ...]:
    data = financials.historical_strategy
    if data is None:
        return ()
    items: list[ManagementAttribution] = []
    for disclosure in data.disclosures:
        if disclosure.role != ROLE_ATTRIBUTION:
            continue
        items.append(
            ManagementAttribution(
                period=disclosure.period,
                theme=disclosure.theme,
                text=disclosure.text,
                source_file=disclosure.source_file,
                page_reference=disclosure.page_reference,
                section=disclosure.section,
                approximate_amount=_attribution_amount(disclosure.text),
            )
        )
    return tuple(items)


def _geo_amount_changes(
    levels: dict,
    axis: tuple[date, ...],
    identities: tuple[str, ...],
) -> tuple[dict[str, float | None], ...]:
    rows: list[dict[str, float | None]] = []
    for index, period in enumerate(axis):
        current = levels.get(period) or {}
        prior = levels.get(axis[index - 1]) if index else None
        row: dict[str, float | None] = {}
        for identity in identities:
            now = _numeric(current.get(identity))
            was = None if prior is None else _numeric(prior.get(identity))
            row[identity] = None if now is None or was is None else now - was
        rows.append(row)
    return tuple(rows)


def _mapped_numeric(mapping: dict, axis: tuple[date, ...]) -> tuple[float | None, ...]:
    return tuple(_numeric(mapping.get(period)) for period in axis)


def _is_cfo_component(concept: str) -> bool:
    if concept in _CFO_EXCLUDED_CONCEPTS:
        return False
    return any(hint in concept for hint in _CFO_COMPONENT_HINTS)


def _cash_series(
    financials: StandardizedFinancials, axis: tuple[date, ...]
) -> tuple[
    tuple[float | None, ...],
    tuple[float | None, ...],
    tuple[float | None, ...],
    tuple[float | None, ...],
    tuple[float | None, ...],
]:
    cfo_item = resolve_line(
        financials.cash_flow, "operating_cash_flow", required=False
    ).item
    ni_item = resolve_line(financials.income_statement, "net_income", required=False).item
    cfo = tuple(
        None if cfo_item is None else _numeric(cfo_item.values.get(period))
        for period in axis
    )
    ni = tuple(
        None if ni_item is None else _numeric(ni_item.values.get(period))
        for period in axis
    )
    component_sum: list[float | None] = [None]
    for index in range(1, len(axis)):
        total = 0.0
        known = False
        for item in financials.cash_flow:
            if not _is_cfo_component(item.concept):
                continue
            current = _numeric(item.values.get(axis[index]))
            prior = _numeric(item.values.get(axis[index - 1]))
            if current is None or prior is None:
                continue
            total += current - prior
            known = True
        component_sum.append(total if known else None)
    cfo_change = _adjacent_numeric_changes(cfo)
    remainder = tuple(
        None if change is None or summed is None else change - summed
        for change, summed in zip(cfo_change or (), tuple(component_sum))
    )
    return ni, cfo, cfo_change or tuple(None for _ in axis), tuple(component_sum), remainder


def _adjacent_numeric_changes(
    values: tuple[float | str | None, ...] | None,
) -> tuple[float | None, ...] | None:
    if values is None:
        return None
    changes: list[float | None] = [None]
    for index in range(1, len(values)):
        current = _numeric(values[index])
        prior = _numeric(values[index - 1])
        if current is None or prior is None:
            changes.append(None)
        else:
            changes.append(current - prior)
    return tuple(changes)


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


def _millions(thousands: float, digits: int = 1) -> float:
    return round(thousands / 1000.0, digits)


def _pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"


def _pp(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f} pp"


def _money(millions: float, digits: int = 1) -> str:
    sign = "−" if millions < 0 else ""
    return f"{sign}${abs(millions):,.{digits}f} million"


@dataclass(frozen=True)
class ComparableSalesPoint:
    period: date
    percent: float
    population: str
    basis: str


@dataclass(frozen=True)
class ManagementAttribution:
    period: date
    theme: str
    text: str
    source_file: str
    page_reference: str
    section: str
    approximate_amount: str | None = None


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
    sga: tuple[float | None, ...] | None = None
    impairment: tuple[float | None, ...] | None = None
    other_operating_items: tuple[float | None, ...] | None = None
    sga_ratio: tuple[float | None, ...] | None = None
    impairment_ratio: tuple[float | None, ...] | None = None
    other_operating_ratio: tuple[float | None, ...] | None = None
    operating_margin_residual: tuple[float | None, ...] | None = None
    operating_profit_residual: tuple[float | None, ...] | None = None
    gross_profit_change: tuple[float | None, ...] | None = None
    gross_profit_revenue_effect: tuple[float | None, ...] | None = None
    gross_profit_margin_effect: tuple[float | None, ...] | None = None
    gross_profit_interaction: tuple[float | None, ...] | None = None
    operating_profit_change: tuple[float | None, ...] | None = None
    reconstructed_operating_profit_change: tuple[float | None, ...] | None = None
    operating_profit_change_residual: tuple[float | None, ...] | None = None
    sga_change: tuple[float | None, ...] | None = None
    impairment_change: tuple[float | None, ...] | None = None
    other_operating_change: tuple[float | None, ...] | None = None
    reported_operating_margin_change: tuple[float | None, ...] | None = None
    reconstructed_component_operating_margin_change: tuple[float | None, ...] | None = None
    operating_margin_change_residual: tuple[float | None, ...] | None = None
    gross_margin_contribution: tuple[float | None, ...] | None = None
    sga_ratio_contribution: tuple[float | None, ...] | None = None
    impairment_ratio_contribution: tuple[float | None, ...] | None = None
    other_operating_ratio_contribution: tuple[float | None, ...] | None = None
    reconstructed_contribution_sum: tuple[float | None, ...] | None = None
    contribution_residual: tuple[float | None, ...] | None = None
    amount_bridge_convention: str = ""
    geo_component_revenue: tuple[dict[str, float | None], ...] | None = None
    geo_reconstructed_revenue: tuple[float | None, ...] | None = None
    geo_reported_revenue: tuple[float | None, ...] | None = None
    geo_residual: tuple[float | None, ...] | None = None
    geo_contribution_amounts: tuple[dict[str, float | None], ...] | None = None
    geo_contribution_residual: tuple[float | None, ...] | None = None
    footprint_store_effect: tuple[float | None, ...] | None = None
    footprint_intensity_effect: tuple[float | None, ...] | None = None
    footprint_interaction: tuple[float | None, ...] | None = None
    footprint_residual: tuple[float | None, ...] | None = None
    footprint_reconstructed_change: tuple[float | None, ...] | None = None
    relationship_findings: tuple[str, ...] = ()
    assessments: tuple[MarginRelationshipAssessment, ...] = ()
    margin_explanation: str = ""
    geo_profit_changes: tuple[dict[str, float | None], ...] | None = None
    geo_reconciling_profit_change: tuple[float | None, ...] | None = None
    geo_consolidated_profit_change: tuple[float | None, ...] | None = None
    geo_profit_change_residual: tuple[float | None, ...] | None = None
    geo_revenue_amount_changes: tuple[dict[str, float | None], ...] | None = None
    net_income: tuple[float | None, ...] | None = None
    net_income_change: tuple[float | None, ...] | None = None
    cfo: tuple[float | None, ...] | None = None
    cfo_change: tuple[float | None, ...] | None = None
    cfo_component_sum: tuple[float | None, ...] | None = None
    cfo_unexplained: tuple[float | None, ...] | None = None
    inventory: tuple[float | None, ...] | None = None
    inventory_change: tuple[float | None, ...] | None = None
    cf_inventory_adjustment: tuple[float | None, ...] | None = None
    attributions: tuple[ManagementAttribution, ...] = ()
    selection: ResearchSelection | None = None

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
    if store_test.sample_size < 1 or geo_test.sample_size < 1:
        raise ValueError("Drivers requires at least one aligned growth and geographic period")
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
    geo_recon = analysis.geographic_reconstruction
    footprint = analysis.footprint_identity
    assessments = _unique_assessments(analysis.assessments + margins.assessments)
    findings = tuple(_finding_sentence(item) for item in assessments)
    reported_om_change = _adjacent_numeric_changes(margins.reported_operating_margin)
    component_om = margins.reconstructed_component_operating_margin
    component_om_change = (
        None if component_om is None else _adjacent_numeric_changes(component_om)
    )
    om_change_residual = None
    if reported_om_change is not None and component_om_change is not None:
        om_change_residual = tuple(
            None
            if reported is None or rebuilt is None
            else reported - rebuilt
            for reported, rebuilt in zip(reported_om_change, component_om_change)
        )
    ni_series, cfo_series, cfo_change, cfo_sum, cfo_remainder = _cash_series(
        financials, tuple(axis)
    )
    inv_series = (
        compute_inventory_analysis_series(financials, list(axis))
        if inventory_analysis_applicable(financials)
        else None
    )
    footprint_reconstructed_change = None
    if footprint is not None:
        footprint_reconstructed_change = tuple(
            None
            if store is None or intensity is None or interaction is None
            else store + intensity + interaction
            for store, intensity, interaction in zip(
                footprint.store_effect,
                footprint.intensity_effect,
                footprint.interaction,
            )
        )
    view = DriversView(
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
        sga=margins.sga,
        impairment=margins.impairment,
        other_operating_items=margins.other_operating_items,
        sga_ratio=tuple(_numeric(value) for value in (margins.sga_ratio or ())),
        impairment_ratio=tuple(
            _numeric(value) for value in (margins.impairment_ratio or ())
        ),
        other_operating_ratio=tuple(
            _numeric(value) for value in (margins.other_operating_ratio or ())
        ),
        operating_margin_residual=tuple(
            _numeric(value) for value in (margins.operating_margin_residual or ())
        ),
        operating_profit_residual=margins.operating_profit_residual,
        gross_profit_change=margins.gross_profit_change,
        gross_profit_revenue_effect=margins.gross_profit_revenue_effect,
        gross_profit_margin_effect=margins.gross_profit_margin_effect,
        gross_profit_interaction=margins.gross_profit_interaction,
        operating_profit_change=margins.operating_profit_change,
        reconstructed_operating_profit_change=margins.reconstructed_operating_profit_change,
        operating_profit_change_residual=margins.operating_profit_change_residual,
        sga_change=margins.sga_change,
        impairment_change=margins.impairment_change,
        other_operating_change=margins.other_operating_change,
        reported_operating_margin_change=reported_om_change,
        reconstructed_component_operating_margin_change=component_om_change,
        operating_margin_change_residual=om_change_residual,
        gross_margin_contribution=tuple(
            _numeric(value) for value in (margins.gross_margin_contribution or ())
        ),
        sga_ratio_contribution=tuple(
            _numeric(value) for value in (margins.sga_ratio_contribution or ())
        ),
        impairment_ratio_contribution=tuple(
            _numeric(value) for value in (margins.impairment_ratio_contribution or ())
        ),
        other_operating_ratio_contribution=tuple(
            _numeric(value) for value in (margins.other_operating_ratio_contribution or ())
        ),
        reconstructed_contribution_sum=tuple(
            _numeric(value) for value in (margins.reconstructed_contribution_sum or ())
        ),
        contribution_residual=tuple(
            _numeric(value) for value in (margins.contribution_residual or ())
        ),
        amount_bridge_convention=margins.amount_bridge_convention,
        geo_component_revenue=None if geo_recon is None else geo_recon.component_revenue,
        geo_reconstructed_revenue=(
            None if geo_recon is None else geo_recon.reconstructed_revenue
        ),
        geo_reported_revenue=None if geo_recon is None else geo_recon.reported_revenue,
        geo_residual=None if geo_recon is None else geo_recon.residual,
        geo_contribution_amounts=(
            None if geo_recon is None else geo_recon.contribution_amounts
        ),
        geo_contribution_residual=(
            None if geo_recon is None else geo_recon.contribution_residual
        ),
        footprint_store_effect=None if footprint is None else footprint.store_effect,
        footprint_intensity_effect=(
            None if footprint is None else footprint.intensity_effect
        ),
        footprint_interaction=None if footprint is None else footprint.interaction,
        footprint_residual=None if footprint is None else footprint.change_residual,
        footprint_reconstructed_change=footprint_reconstructed_change,
        relationship_findings=findings,
        assessments=assessments,
        margin_explanation="",
        geo_profit_changes=tuple(
            {
                identity: _numeric(geo.operating_profit_amount_change[period][identity])
                for identity in geo.identities
            }
            for period in axis
        ),
        geo_reconciling_profit_change=_mapped_numeric(
            geo.reconciling_operating_profit_amount_change, tuple(axis)
        ),
        geo_consolidated_profit_change=_mapped_numeric(
            geo.consolidated_operating_profit_amount_change, tuple(axis)
        ),
        geo_profit_change_residual=_mapped_numeric(
            geo.operating_profit_amount_change_residual, tuple(axis)
        ),
        geo_revenue_amount_changes=_geo_amount_changes(
            geo.net_revenue, tuple(axis), geo.identities
        ),
        net_income=ni_series,
        net_income_change=_adjacent_numeric_changes(ni_series),
        cfo=cfo_series,
        cfo_change=cfo_change,
        cfo_component_sum=cfo_sum,
        cfo_unexplained=cfo_remainder,
        inventory=None if inv_series is None else tuple(_numeric(value) for value in inv_series.inventories),
        inventory_change=None if inv_series is None else tuple(_numeric(value) for value in inv_series.inventory_change),
        cf_inventory_adjustment=(
            None
            if inv_series is None
            else tuple(_numeric(value) for value in inv_series.change_in_inventories)
        ),
        attributions=_attributions_from_financials(financials),
    )
    return replace(view, selection=select_driver_argument(view))


_KIND_LABELS = {
    "identity": "identity",
    "reported_fact": "reported fact",
    "attributed_management_explanation": "management explanation",
    "observed_relationship": "observed relationship",
    "causal_hypothesis": "causal reading",
    "unestablished_inference": "unestablished",
}
_FORBIDDEN_RESEARCH = (
    "admitted",
    "fail-closed",
    "fail closed",
    "source unavailable",
    "standardizedfinancials",
    "hypothesis",
    "verdict",
    "audit-only",
    "audit only",
    "supported_descriptively",
    "segment_bridge",
    "provenance",
    "trainer",
    "answer key",
)


def _research_safe(text: str) -> str:
    cleaned = text
    for source, target in (
        ("supported_descriptively", "supported descriptively"),
        ("fail-closed", "closed"),
        ("fail closed", "closed"),
        ("source unavailable", "unavailable"),
        ("standardizedfinancials", "standardized financials"),
        ("causal_hypothesis", "causal reading"),
        ("hypothesis", "reading"),
        ("Verdict", "Result"),
        ("verdict", "result"),
        ("audit-only", "kept out of the comparison"),
        ("audit only", "kept out of the comparison"),
        ("segment_bridge", "segment bridge"),
        ("provenance", "source note"),
        ("answer key", "reference"),
        ("Admitted ", "Reported "),
        ("admitted ", "reported "),
        ("admitted", "reported"),
        ("trainer", "practice file"),
    ):
        cleaned = cleaned.replace(source, target)
    return cleaned


def _unique_assessments(
    items: tuple[MarginRelationshipAssessment, ...],
) -> tuple[MarginRelationshipAssessment, ...]:
    seen: set[str] = set()
    unique: list[MarginRelationshipAssessment] = []
    for item in items:
        if not item.name or item.name in seen:
            continue
        seen.add(item.name)
        unique.append(item)
    return tuple(unique)


def _finding_sentence(item) -> str:
    status = "established" if item.established else "unestablished"
    limit = f" {item.limitation}" if item.limitation and not item.established else ""
    return _research_safe(
        f"{item.name.capitalize()}: {item.direction}. Residual: {item.residual}. "
        f"{status.capitalize()}.{limit}"
    )


def _opt_money(thousands: float | None, digits: int = 1) -> str:
    if thousands is None:
        return "n/a"
    return _money(_millions(thousands, digits), digits=digits)


def _opt_pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return _pct(value, digits)


def _margin_component_block(view: DriversView) -> str:
    if not view.sga_ratio:
        return ""
    rows = [
        "| Fiscal year | Gross margin | SG&A / revenue | Impairment / revenue | Other operating items / revenue | Operating margin | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, label in enumerate(view.labels):
        imp = (
            "n/a"
            if view.impairment_ratio is None or index >= len(view.impairment_ratio)
            else _opt_pct(view.impairment_ratio[index], 2)
        )
        other = (
            "n/a"
            if view.other_operating_ratio is None
            or index >= len(view.other_operating_ratio)
            else _opt_pct(view.other_operating_ratio[index], 2)
        )
        residual = (
            "n/a"
            if view.operating_margin_residual is None
            or index >= len(view.operating_margin_residual)
            else _opt_pct(view.operating_margin_residual[index], 2)
        )
        sga = (
            "n/a"
            if index >= len(view.sga_ratio)
            else _opt_pct(view.sga_ratio[index], 1)
        )
        rows.append(
            f"| {label} | {_pct(view.gross_margin[index], 1)} | {sga} | {imp} | "
            f"{other} | {_pct(view.operating_margin[index], 1)} | {residual} |"
        )
    return (
        "Operating margin is reconstructed as gross margin less SG&A/revenue, "
        "impairment or asset-related charges/revenue, and other reported "
        "operating items/revenue. Missing lines stay blank; they are not filled "
        "with zero.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _opt_pp(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return _pp(value, digits)


def _opt_change_pp(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.{digits}f} pp"


def _opt_bps(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 10000:+.0f} bps"


def _amount_bridge_block(view: DriversView) -> str:
    if not view.gross_profit_change:
        return ""
    rows = [
        "| Fiscal year | Revenue effect | Gross-margin effect | Interaction | Gross-profit change | SG&A change | Impairment change | Other operating-item change | Reconstructed operating-profit change | Reported operating-profit change | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, label in enumerate(view.labels):
        if view.gross_profit_change[index] is None:
            continue
        rows.append(
            "| {label} | {rev} | {gm} | {ix} | {gp} | {sga} | {imp} | {other} | {recon} | {op} | {resid} |".format(
                label=label,
                rev=_opt_money(
                    None
                    if view.gross_profit_revenue_effect is None
                    else view.gross_profit_revenue_effect[index]
                ),
                gm=_opt_money(
                    None
                    if view.gross_profit_margin_effect is None
                    else view.gross_profit_margin_effect[index]
                ),
                ix=_opt_money(
                    None
                    if view.gross_profit_interaction is None
                    else view.gross_profit_interaction[index]
                ),
                gp=_opt_money(view.gross_profit_change[index]),
                sga=_opt_money(
                    None if view.sga_change is None else view.sga_change[index]
                ),
                imp=_opt_money(
                    None
                    if view.impairment_change is None
                    else view.impairment_change[index]
                ),
                other=_opt_money(
                    None
                    if view.other_operating_change is None
                    else view.other_operating_change[index]
                ),
                recon=_opt_money(
                    None
                    if view.reconstructed_operating_profit_change is None
                    else view.reconstructed_operating_profit_change[index]
                ),
                op=_opt_money(
                    None
                    if view.operating_profit_change is None
                    else view.operating_profit_change[index]
                ),
                resid=_opt_money(
                    None
                    if view.operating_profit_change_residual is None
                    else view.operating_profit_change_residual[index]
                ),
            )
        )
    convention = view.amount_bridge_convention or (
        "Gross-profit change uses prior gross margin on the revenue change, "
        "prior revenue on the gross-margin change, and an explicit interaction."
    )
    return (
        convention
        + " An expense increase reduces operating profit. Missing adjacent "
        "comparisons stay blank; they are not treated as zero.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _contrib_cell(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{_opt_change_pp(value)} ({_opt_bps(value)})"


def _margin_change_block(view: DriversView) -> str:
    if not view.gross_margin_contribution:
        return ""
    rows = [
        "| Fiscal year | Δgross margin | −Δ(SG&A/revenue) | −Δ(impairment/revenue) | −Δ(other operating items/revenue) | Reconstructed sum | Reported operating-margin change | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    present = False
    for index, label in enumerate(view.labels):
        gm = (
            None
            if view.gross_margin_contribution is None
            else view.gross_margin_contribution[index]
        )
        if gm is None and (
            view.reported_operating_margin_change is None
            or view.reported_operating_margin_change[index] is None
        ):
            continue
        present = True
        rows.append(
            "| {label} | {gm} | {sga} | {imp} | {other} | {recon} | {reported} | {resid} |".format(
                label=label,
                gm=_contrib_cell(gm),
                sga=_contrib_cell(
                    None
                    if view.sga_ratio_contribution is None
                    or index >= len(view.sga_ratio_contribution)
                    else view.sga_ratio_contribution[index]
                ),
                imp=_contrib_cell(
                    None
                    if view.impairment_ratio_contribution is None
                    or index >= len(view.impairment_ratio_contribution)
                    else view.impairment_ratio_contribution[index]
                ),
                other=_contrib_cell(
                    None
                    if view.other_operating_ratio_contribution is None
                    or index >= len(view.other_operating_ratio_contribution)
                    else view.other_operating_ratio_contribution[index]
                ),
                recon=_contrib_cell(
                    None
                    if view.reconstructed_contribution_sum is None
                    or index >= len(view.reconstructed_contribution_sum)
                    else view.reconstructed_contribution_sum[index]
                ),
                reported=_contrib_cell(
                    None
                    if view.reported_operating_margin_change is None
                    else view.reported_operating_margin_change[index]
                ),
                resid=_opt_change_pp(
                    None
                    if view.contribution_residual is None
                    or index >= len(view.contribution_residual)
                    else view.contribution_residual[index]
                ),
            )
        )
    if not present:
        return ""
    return (
        "Signed operating-margin contributions are Δgross margin, "
        "−Δ(SG&A/revenue), −Δ(impairment or asset-related charges/revenue), "
        "and −Δ(other reported operating items/revenue). Each term is "
        "calculated from unrounded ratios. Percentage points are the ratio "
        "change × 100; basis points are the same unrounded value × 10,000. "
        "Displayed figures are rounded after the calculation. A rise in an "
        "expense ratio is a negative contribution. Residual is reported "
        "operating-margin change minus the reconstructed contribution sum. "
        "Missing adjacent comparisons stay blank; they are not treated as "
        "zero.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _footprint_block(view: DriversView) -> str:
    if not view.footprint_store_effect:
        return ""
    rows = [
        "| Fiscal year | Store-count effect | Intensity effect | Interaction | Reconstructed revenue change | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    present = False
    for index, label in enumerate(view.labels):
        if view.footprint_store_effect[index] is None:
            continue
        present = True
        rows.append(
            "| {label} | {store} | {inten} | {ix} | {recon} | {resid} |".format(
                label=label,
                store=_opt_money(view.footprint_store_effect[index]),
                inten=_opt_money(
                    None
                    if view.footprint_intensity_effect is None
                    else view.footprint_intensity_effect[index]
                ),
                ix=_opt_money(
                    None
                    if view.footprint_interaction is None
                    else view.footprint_interaction[index]
                ),
                recon=_opt_money(
                    None
                    if view.footprint_reconstructed_change is None
                    else view.footprint_reconstructed_change[index]
                ),
                resid=_opt_money(
                    None
                    if view.footprint_residual is None
                    else view.footprint_residual[index]
                ),
            )
        )
    if not present:
        return ""
    return (
        "Company-wide revenue equals store count times company-wide revenue per "
        "store. The adjacent change uses prior intensity on the store-count "
        "change, prior store count on the intensity change, and an explicit "
        "interaction. Company-wide revenue per store includes non-store revenue "
        "and is an intensity proxy, not store productivity.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _geo_reconstruction_block(view: DriversView) -> str:
    if not view.geo_component_revenue or not view.geo_residual:
        return ""
    level_rows = [
        "| Fiscal year | Americas | China Mainland | Rest of World | Reconstructed | Reported | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, label in enumerate(view.labels):
        comps = view.geo_component_revenue[index]
        level_rows.append(
            "| {label} | {am} | {cn} | {rw} | {rec} | {rep} | {res} |".format(
                label=label,
                am=_opt_money(comps.get("americas")),
                cn=_opt_money(comps.get("china_mainland")),
                rw=_opt_money(comps.get("rest_of_world")),
                rec=_opt_money(
                    None
                    if view.geo_reconstructed_revenue is None
                    else view.geo_reconstructed_revenue[index]
                ),
                rep=_opt_money(
                    None
                    if view.geo_reported_revenue is None
                    else view.geo_reported_revenue[index]
                ),
                res=_opt_money(
                    None
                    if view.geo_residual is None
                    else view.geo_residual[index]
                ),
            )
        )
    change_rows = [
        "| Fiscal year | Americas change | China Mainland change | Rest of World change | Americas growth contribution | China Mainland growth contribution | Rest of World growth contribution | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    has_change = False
    if view.geo_contribution_amounts:
        for index, label in enumerate(view.labels):
            amounts = view.geo_contribution_amounts[index]
            if all(value is None for value in amounts.values()):
                continue
            has_change = True
            contrib = view.geo_contributions[index]
            change_rows.append(
                "| {label} | {am} | {cn} | {rw} | {amg} | {cng} | {rwg} | {res} |".format(
                    label=label,
                    am=_opt_money(amounts.get("americas")),
                    cn=_opt_money(amounts.get("china_mainland")),
                    rw=_opt_money(amounts.get("rest_of_world")),
                    amg=_opt_pp(contrib.get("americas")),
                    cng=_opt_pp(contrib.get("china_mainland")),
                    rwg=_opt_pp(contrib.get("rest_of_world")),
                    res=_opt_money(
                        None
                        if view.geo_contribution_residual is None
                        else view.geo_contribution_residual[index]
                    ),
                )
            )
    body = (
        "Consolidated revenue is reconstructed from the geographic components. "
        "Residuals are the reconstructed total minus reported revenue. Growth "
        "contributions are an arithmetic split of reported-currency revenue "
        "change and are not organic or constant-currency growth.\n\n"
        + "\n".join(level_rows)
        + "\n"
    )
    if has_change:
        body += "\n" + "\n".join(change_rows) + "\n"
    return body


def _max_abs(values: tuple[float | None, ...] | None) -> float | None:
    known = [abs(value) for value in (values or ()) if value is not None]
    if not known:
        return None
    return max(known)


def _residual_conclusion(view: DriversView) -> str:
    parts: list[str] = []
    for name, series, money in (
        ("component operating-margin identity", view.operating_margin_residual, False),
        ("component operating-margin contributions", view.contribution_residual, False),
        ("operating-profit amount bridge", view.operating_profit_change_residual, True),
        ("geographic reconstruction", view.geo_residual, True),
        ("geographic growth-contribution", view.geo_contribution_residual, True),
        ("store-count times company-wide revenue per store", view.footprint_residual, True),
    ):
        largest = _max_abs(series)
        if largest is None:
            parts.append(f"{name} has no adjacent comparison in the available history")
        elif largest < (1e-8 if not money else 1e-4):
            parts.append(f"{name} residual is {largest:.6g}")
        else:
            parts.append(f"{name} residual is {largest:.6g} and remains visible")
    return (
        "Residuals are computed from the validated reconstructions. "
        + "; ".join(parts)
        + ". Sales-per-square-foot productivity and mix, markdowns, freight, "
        "costs, or leverage remain unestablished."
    )


def _assessment_block(view: DriversView) -> str:
    if not view.assessments:
        return ""
    rows = [
        "| Relationship | Kind | Residual | Stability | Contradictions | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in view.assessments:
        kind = _KIND_LABELS.get(item.kind, item.kind.replace("_", " "))
        rows.append(
            "| {name} | {kind} | {resid} | {stable} | {contra} | {result} |".format(
                name=_research_safe(item.name),
                kind=_research_safe(kind),
                resid=_research_safe(item.residual),
                stable=_research_safe(item.stability),
                contra=_research_safe(item.contradictions),
                result="established" if item.established else "unestablished",
            )
        )
    body = "\n".join(rows) + "\n"
    lowered = body.lower()
    for term in _FORBIDDEN_RESEARCH:
        if term in lowered:
            raise ValueError(f"Drivers assessment prose contains {term!r}")
    return (
        "Each material relationship is tested for direction, magnitude, "
        "reconstruction, residual, stability across periods, contradictions, "
        "and disclosure support.\n\n"
        + body
    )


def _latest_growth_index(view: DriversView) -> int:
    for index in range(len(view.periods) - 1, -1, -1):
        if view.revenue_growth[index] is not None:
            return index
    return len(view.periods) - 1


def _opening_paragraphs(view: DriversView, selection: ResearchSelection) -> list[str]:
    latest = _latest_growth_index(view)
    label = view.labels[latest]
    parts: list[str] = []
    rev_g = view.revenue_growth[latest]
    store_g = view.store_growth[latest]
    op_change = (
        None
        if view.geo_consolidated_profit_change is None
        else view.geo_consolidated_profit_change[latest]
    )
    cfo_change = None if view.cfo_change is None else view.cfo_change[latest]
    ni_change = None if view.net_income_change is None else view.net_income_change[latest]
    first = (
        f"In {label}, {view.display_name} revenue grew {_pct(rev_g)} while "
        f"company-operated stores grew {_pct(store_g)}."
        if rev_g is not None and store_g is not None
        else f"{view.display_name} historical performance is reconstructed from the available BAV series."
    )
    if op_change is not None:
        first += (
            f" Operating profit changed by {_money(_millions(op_change))}, so "
            "growth did not preserve the prior profit level."
        )
    parts.append(first)
    if selection.selected("geographic_localization"):
        contrib = view.geo_contributions[latest]
        amounts = (
            {}
            if view.geo_revenue_amount_changes is None
            else view.geo_revenue_amount_changes[latest]
        )
        profit = (
            {}
            if view.geo_profit_changes is None
            else view.geo_profit_changes[latest]
        )
        reconciling = (
            None
            if view.geo_reconciling_profit_change is None
            else view.geo_reconciling_profit_change[latest]
        )
        parts.append(
            "International revenue more than offset the Americas decline "
            f"({_pp(contrib.get('americas'))} Americas, "
            f"{_pp(contrib.get('china_mainland'))} China Mainland, "
            f"{_pp(contrib.get('rest_of_world'))} Rest of World"
            + (
                f"; Americas revenue {_money(_millions(amounts['americas']))}"
                if amounts.get("americas") is not None
                else ""
            )
            + "), but Americas operating profit "
            + (
                f"{_money(_millions(profit['americas']))}"
                if profit.get("americas") is not None
                else "declined"
            )
            + (
                f" and corporate/unallocated items {_money(_millions(reconciling))}"
                if reconciling is not None
                else ""
            )
            + " left a weaker consolidated profit outcome. That localizes "
            "where dependence moved; it does not identify the regional mechanism."
        )
    if selection.selected("cash_conversion") and cfo_change is not None and ni_change is not None:
        remainder = (
            None if view.cfo_unexplained is None else view.cfo_unexplained[latest]
        )
        parts.append(
            f"Cash from operations changed by {_money(_millions(cfo_change))}, "
            f"a larger movement than net income ({_money(_millions(ni_change))}). "
            "The most consequential uncertainty is that the available cash-flow "
            "components do not explain the whole CFO movement"
            + (
                f" (signed remainder {_money(_millions(remainder, 3), 3)})"
                if remainder is not None
                else ""
            )
            + ", and the margin mechanism remains independently unresolved."
        )
    elif selection.selected("operating_margin_bridge"):
        parts.append(
            "The accounting margin bridge reconstructs the latest operating-margin "
            "change, but the economic mechanism remains unresolved."
        )
    return parts


def _growth_argument(view: DriversView, latest: int) -> list[str]:
    store_g = view.store_growth[latest]
    rev_g = view.revenue_growth[latest]
    intensity = None
    if latest > 0:
        prior = view.revenue_per_store[latest - 1]
        current = view.revenue_per_store[latest]
        intensity = current / prior - 1.0
    store_term = (
        None
        if view.footprint_store_effect is None
        else view.footprint_store_effect[latest]
    )
    week = _calendar_limitation(view).strip()
    paragraphs = [
        (
            f"Store expansion outpaced company-wide revenue in {view.labels[latest]}: "
            f"company-operated stores rose {_pct(store_g)} while consolidated revenue "
            f"rose {_pct(rev_g)}"
            + (
                f", so company-wide revenue per period-end store fell {_pct(abs(intensity))}"
                if intensity is not None and intensity < 0
                else ""
            )
            + ". Store count is an operating KPI. Revenue per store is a proxy that "
            "includes non-store revenue and is not store productivity. "
            + (
                f"The {_money(_millions(store_term))} store-count term in the "
                "footprint identity is an arithmetic allocation, not measured "
                "new-store revenue."
                if store_term is not None
                else ""
            )
        )
    ]
    latest_comp = next(
        (point for point in reversed(view.comparable_sales) if point.period == view.periods[latest]),
        view.comparable_sales[-1] if view.comparable_sales else None,
    )
    if latest_comp is not None:
        paragraphs.append(
            f"The latest reported comparable-sales observation is "
            f"{latest_comp.percent:.0f}% on a "
            f"{POPULATION_LABELS.get(latest_comp.population, latest_comp.population)} "
            "basis. Each period's observation is retained on its own definition "
            "and calendar; the observations are not one deceleration series, and "
            "revenue growth minus comparable sales is not new-store contribution."
        )
    if week:
        paragraphs.append(week)
    paragraphs.append(
        "![Did store-count growth outpace consolidated revenue growth?](../figures/drivers/growth.png)"
    )
    paragraphs.append(
        "The paired growth rates show the latest divergence without connecting "
        "comparable-sales observations. Weaker demand and slower maturation of "
        "added capacity remain open; opening dates, mix, digital revenue and the "
        "unequal-week comparison can produce the same pattern. Appendix Growth "
        "evidence keeps the count/intensity/interaction bridge and rejected joins."
    )
    return paragraphs


def _geography_argument(view: DriversView, latest: int) -> list[str]:
    contrib = view.geo_contributions[latest]
    amounts = (
        {}
        if view.geo_revenue_amount_changes is None
        else view.geo_revenue_amount_changes[latest]
    )
    profit = (
        {}
        if view.geo_profit_changes is None
        else view.geo_profit_changes[latest]
    )
    reconciling = (
        None
        if view.geo_reconciling_profit_change is None
        else view.geo_reconciling_profit_change[latest]
    )
    consolidated = (
        None
        if view.geo_consolidated_profit_change is None
        else view.geo_consolidated_profit_change[latest]
    )
    paragraphs = [
        (
            f"In {view.labels[latest]}, Americas revenue "
            f"{_opt_money(amounts.get('americas')) if amounts else 'n/a'} "
            f"while China Mainland {_opt_money(amounts.get('china_mainland')) if amounts else 'n/a'} "
            f"and Rest of World {_opt_money(amounts.get('rest_of_world')) if amounts else 'n/a'}. "
            f"Their contributions to consolidated revenue growth were "
            f"{_pp(contrib.get('americas'))}, {_pp(contrib.get('china_mainland'))} "
            f"and {_pp(contrib.get('rest_of_world'))}. International growth more "
            "than offset the Americas revenue decline."
        ),
        (
            "The profit localization is different. Americas operating profit "
            f"{_opt_money(profit.get('americas')) if profit else 'n/a'}; "
            f"China Mainland {_opt_money(profit.get('china_mainland')) if profit else 'n/a'} "
            f"and Rest of World {_opt_money(profit.get('rest_of_world')) if profit else 'n/a'}"
            + (
                f"; corporate/unallocated items {_opt_money(reconciling)}"
                if reconciling is not None
                else ""
            )
            + (
                f". Those changes reconcile to {_opt_money(consolidated, 3)} of "
                "consolidated operating profit."
                if consolidated is not None
                else "."
            )
            + " This is reported segment evidence and arithmetic localization, "
            "not a causal attribution or organic-growth claim."
        ),
        "![Did international revenue growth offset Americas profit deterioration?](../figures/drivers/geography.png)",
        (
            "The aligned panels keep revenue and profit on separate scales and "
            "retain the corporate reconciliation on the profit side. Lower "
            "Americas demand and cost pressure are plausible, but currency, mix, "
            "calendar effects and cost allocation remain alternatives. Appendix "
            "Geographic evidence keeps complete series, margins and residuals."
        ),
    ]
    return paragraphs


def _margin_argument(view: DriversView, latest: int) -> list[str]:
    om = (
        None
        if view.reported_operating_margin_change is None
        else view.reported_operating_margin_change[latest]
    )
    gm = (
        None
        if view.gross_margin_contribution is None
        else view.gross_margin_contribution[latest]
    )
    sga = (
        None
        if view.sga_ratio_contribution is None
        or latest >= len(view.sga_ratio_contribution)
        else view.sga_ratio_contribution[latest]
    )
    impairment = (
        None
        if view.impairment_ratio_contribution is None
        or latest >= len(view.impairment_ratio_contribution)
        else view.impairment_ratio_contribution[latest]
    )
    other = (
        None
        if view.other_operating_ratio_contribution is None
        or latest >= len(view.other_operating_ratio_contribution)
        else view.other_operating_ratio_contribution[latest]
    )
    residual = (
        None
        if view.contribution_residual is None
        or latest >= len(view.contribution_residual)
        else view.contribution_residual[latest]
    )
    paragraphs = [
        (
            f"{view.labels[latest]} operating margin moved from "
            f"{_pct(view.operating_margin[latest - 1], 1)} to "
            f"{_pct(view.operating_margin[latest], 1)}"
            + (f", {_opt_change_pp(om)}" if om is not None else "")
            + " using unrounded ratios. "
            f"Gross margin contributed {_opt_change_pp(gm)}, SG&A/revenue "
            f"{_opt_change_pp(sga)}, impairment {_opt_change_pp(impairment)}, "
            f"and other operating items {_opt_change_pp(other)}"
            + (
                f"; the residual versus the reported change is {_opt_change_pp(residual)}"
                if residual is not None
                else ""
            )
            + ". This is an identity and signed decomposition. It does not "
            "establish tariff, markdown, mix or absorption mechanisms."
        )
    ]
    latest_period = view.periods[latest]
    attrs = [item for item in view.attributions if item.period == latest_period]
    if attrs:
        quantified = next((item for item in attrs if item.approximate_amount), None)
        quotes = " ".join(item.text.rstrip(".") + "." for item in attrs)
        locators = "; ".join(
            f"{item.source_file}, {item.page_reference}" for item in attrs
        )
        paragraphs.append(
            "Management attributes the latest-year pressure in source-bound "
            f"commentary: {quotes} ({locators}). "
            + (
                f"{quantified.approximate_amount.capitalize()} is retained as "
                "management's attributed gross-profit reduction against a "
                "stated counterfactual; it is not an independently verified "
                "causal estimate and is not inserted into the accounting bridge."
                if quantified is not None
                else "The attribution is preserved with its locator and is not "
                "inserted into the accounting bridge."
            )
        )
    paragraphs.append(
        "![Which accounting components reconstruct the latest operating-margin change?](../figures/drivers/margin.png)"
    )
    paragraphs.append(
        "The latest-year bridge isolates the accounting movements next to that "
        "boundary. Cost pressure and mix remain credible alternatives. Earlier "
        "margin recovery included disappearing episodic charges and is not a "
        "pure operating-efficiency trend. Appendix Margin evidence keeps full "
        "ratios, amount bridges and residuals."
    )
    return paragraphs


def _cash_argument(view: DriversView, latest: int) -> list[str]:
    cfo = None if view.cfo is None else view.cfo[latest]
    ni = None if view.net_income is None else view.net_income[latest]
    prior_cfo = None if view.cfo is None or latest < 1 else view.cfo[latest - 1]
    prior_ni = None if view.net_income is None or latest < 1 else view.net_income[latest - 1]
    cfo_change = None if view.cfo_change is None else view.cfo_change[latest]
    remainder = None if view.cfo_unexplained is None else view.cfo_unexplained[latest]
    inventory = None if view.inventory is None else view.inventory[latest]
    prior_inv = None if view.inventory is None or latest < 1 else view.inventory[latest - 1]
    inv_change = None if view.inventory_change is None else view.inventory_change[latest]
    cf_inv = (
        None
        if view.cf_inventory_adjustment is None
        else view.cf_inventory_adjustment[latest]
    )
    conversion = None if cfo is None or ni in (None, 0) else cfo / ni
    prior_conversion = (
        None if prior_cfo is None or prior_ni in (None, 0) else prior_cfo / prior_ni
    )
    paragraphs = [
        (
            f"Reported CFO moved from {_opt_money(prior_cfo)} to {_opt_money(cfo)} "
            f"while net income moved from {_opt_money(prior_ni)} to {_opt_money(ni)}"
            + (
                f". CFO/net income moved from {prior_conversion:.2f} to {conversion:.2f}"
                if conversion is not None and prior_conversion is not None
                else ""
            )
            + (
                f". The cash change of {_opt_money(cfo_change)} is larger than "
                "the earnings change."
                if cfo_change is not None
                else "."
            )
            + " These are reported amounts and derived diagnostics, not an "
            "earnings-quality judgment or a finding of manipulation."
        )
    ]
    if inventory is not None and prior_inv is not None:
        inv_growth = inventory / prior_inv - 1.0
        paragraphs.append(
            f"Inventory increased from {_opt_money(prior_inv)} to {_opt_money(inventory)} "
            f"({_pct(inv_growth)}) against slower company revenue growth. "
            "Inventory accumulation can consume cash, but growth preparation, "
            "sourcing, currency, tax and other settlement timing compete with a "
            "weak-demand reading. The cash-flow inventory line "
            f"({_opt_money(cf_inv)}) is not substituted for the balance-sheet change "
            f"({_opt_money(inv_change)})."
        )
    if remainder is not None:
        paragraphs.append(
            "The available operating-section component changes do not explain "
            f"the whole CFO movement. The signed unexplained remainder is "
            f"{_opt_money(remainder, 3)}. That difference is retained without "
            "assigning a cause."
        )
    paragraphs.append(
        "![Did reported earnings continue to translate into operating cash flow?](../figures/drivers/cash.png)"
    )
    paragraphs.append(
        "The paired CFO and net-income comparison supplies the distinct cash "
        "perspective. It does not attribute the full decline to working capital, "
        "seasonality or manipulation. Appendix Cash evidence keeps the component "
        "sum, remainder, inventory movements and the distinction between "
        "balance-sheet and cash-flow inventory."
    )
    return paragraphs


def _history_table(view: DriversView) -> str:
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
    return (
        "Historical levels used by the selected claims. Amounts are "
        f"{view.units}, shown in millions of {view.currency}.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _geo_profit_block(view: DriversView) -> str:
    if not view.geo_profit_changes:
        return ""
    rows = [
        "| Fiscal year | Americas | China Mainland | Rest of World | Corporate / unallocated | Consolidated | Residual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    present = False
    for index, label in enumerate(view.labels):
        changes = view.geo_profit_changes[index]
        if all(value is None for value in changes.values()):
            continue
        present = True
        rows.append(
            "| {label} | {am} | {cn} | {rw} | {corp} | {cons} | {res} |".format(
                label=label,
                am=_opt_money(changes.get("americas")),
                cn=_opt_money(changes.get("china_mainland")),
                rw=_opt_money(changes.get("rest_of_world")),
                corp=_opt_money(
                    None
                    if view.geo_reconciling_profit_change is None
                    else view.geo_reconciling_profit_change[index]
                ),
                cons=_opt_money(
                    None
                    if view.geo_consolidated_profit_change is None
                    else view.geo_consolidated_profit_change[index],
                    3,
                ),
                res=_opt_money(
                    None
                    if view.geo_profit_change_residual is None
                    else view.geo_profit_change_residual[index]
                ),
            )
        )
    if not present:
        return ""
    return (
        "Geographic operating-profit amount changes include corporate/"
        "unallocated items and reconcile to the consolidated change. This "
        "localizes the profit movement; it does not identify causes.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _compsales_block(view: DriversView) -> str:
    if not view.comparable_sales:
        return ""
    rows = [
        "| Fiscal year | Reported comparable sales | Population | Basis |",
        "| --- | ---: | --- | --- |",
    ]
    for point in view.comparable_sales:
        if point.period not in view.periods:
            continue
        rows.append(
            "| {label} | {pct} | {pop} | {basis} |".format(
                label=view.labels[view.periods.index(point.period)],
                pct=f"{point.percent:.0f}%",
                pop=POPULATION_LABELS.get(point.population, point.population),
                basis=point.basis,
            )
        )
    if view.store_only_comparable_sales is not None:
        point = view.store_only_comparable_sales
        if point.period in view.periods:
            rows.append(
                "| {label} | {pct} | {pop} | {basis} |".format(
                    label=view.labels[view.periods.index(point.period)],
                    pct=f"{point.percent:.0f}%",
                    pop=POPULATION_LABELS.get(point.population, point.population),
                    basis=point.basis,
                )
            )
    return (
        "Comparable-sales observations are retained as period-specific reported "
        "KPIs. Changing channel definitions and calendars prevent a connected "
        "trend. Revenue growth minus comparable sales is not labeled new-store "
        "contribution.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _cash_block(view: DriversView) -> str:
    if view.cfo is None or view.net_income is None:
        return ""
    rows = [
        "| Fiscal year | CFO | Net income | CFO change | Component-change sum | Signed remainder | Inventory | Inventory change | CF inventory line |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    present = False
    for index, label in enumerate(view.labels):
        if view.cfo[index] is None and view.net_income[index] is None:
            continue
        present = True
        rows.append(
            "| {label} | {cfo} | {ni} | {chg} | {comp} | {rem} | {inv} | {ichg} | {cfinv} |".format(
                label=label,
                cfo=_opt_money(view.cfo[index]),
                ni=_opt_money(view.net_income[index]),
                chg=_opt_money(
                    None if view.cfo_change is None else view.cfo_change[index]
                ),
                comp=_opt_money(
                    None
                    if view.cfo_component_sum is None
                    else view.cfo_component_sum[index]
                ),
                rem=_opt_money(
                    None if view.cfo_unexplained is None else view.cfo_unexplained[index],
                    3,
                ),
                inv=_opt_money(None if view.inventory is None else view.inventory[index]),
                ichg=_opt_money(
                    None if view.inventory_change is None else view.inventory_change[index]
                ),
                cfinv=_opt_money(
                    None
                    if view.cf_inventory_adjustment is None
                    else view.cf_inventory_adjustment[index]
                ),
            )
        )
    if not present:
        return ""
    return (
        "CFO and net income are reported amounts. The component-change sum is "
        "the adjacent change in operating-section cash-flow lines excluding the "
        "CFO total. The signed remainder is reported CFO change minus that sum. "
        "Balance-sheet inventory change is not a cash-flow-statement "
        "reconciliation. An incomplete explanation does not block the reported "
        "CFO decline.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _attribution_block(view: DriversView) -> str:
    if not view.attributions:
        return ""
    rows = [
        "| Period | Theme | Attribution | Approximate amount | Source | Section |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in view.attributions:
        label = (
            view.labels[view.periods.index(item.period)]
            if item.period in view.periods
            else item.period.isoformat()
        )
        rows.append(
            "| {label} | {theme} | {text} | {amt} | {src} | {sec} |".format(
                label=label,
                theme=item.theme.replace("_", " "),
                text=item.text,
                amt=item.approximate_amount or "qualitative",
                src=f"{item.source_file}, {item.page_reference}",
                sec=item.section,
            )
        )
    return (
        "Management attributions are source-bound disclosures. Approximate "
        "wording, period, counterfactual scope and locators are retained. The "
        "amounts are not independently verified and are not mixed with "
        "reconciled accounting-bridge components.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def _selection_block(view: DriversView) -> str:
    if view.selection is None:
        return ""
    rows = [
        "| Question | Decision | Reason | Strongest supported conclusion | Unresolved requirement |",
        "| --- | --- | --- | --- | --- |",
    ]
    by_id = {item.identifier: item for item in view.selection.questions}
    for decision in view.selection.decisions:
        question = by_id.get(decision.identifier)
        rows.append(
            "| {qid} | {action} | {reason} | {conc} | {need} |".format(
                qid=decision.identifier.replace("_", " "),
                action=decision.action,
                reason=_research_safe(decision.reason),
                conc="" if question is None else _research_safe(question.strongest_conclusion),
                need="" if question is None else _research_safe(question.unresolved_requirement),
            )
        )
    return (
        "Selection records why candidates were selected, combined, retained, "
        "deferred or excluded. There is no factor quota or numerical confidence "
        "score.\n\n"
        + "\n".join(rows)
        + "\n"
    )


def render_drivers_markdown(view: DriversView) -> str:
    selection = view.selection or select_driver_argument(view)
    latest = _latest_growth_index(view)
    blocks = [drivers_heading(view.display_name), ""]
    blocks.extend(_opening_paragraphs(view, selection))
    if selection.selected("footprint_intensity"):
        blocks.append("")
        blocks.extend(_growth_argument(view, latest))
    if selection.selected("geographic_localization"):
        blocks.append("")
        blocks.extend(_geography_argument(view, latest))
    if selection.selected("operating_margin_bridge"):
        blocks.append("")
        blocks.extend(_margin_argument(view, latest))
    if selection.selected("cash_conversion"):
        blocks.append("")
        blocks.extend(_cash_argument(view, latest))
    blocks.append("")
    blocks.append(APPENDIX_HEADING)
    blocks.append("")
    blocks.append("### Selected claims")
    blocks.append("")
    blocks.append(_selection_block(view))
    if selection.selected("footprint_intensity") or selection.question("comparable_sales"):
        blocks.append("### Growth evidence")
        blocks.append("")
        blocks.append(_history_table(view))
        blocks.append(_footprint_block(view))
        blocks.append(_compsales_block(view))
    if selection.selected("geographic_localization"):
        blocks.append("### Geographic evidence")
        blocks.append("")
        blocks.append(_geo_reconstruction_block(view))
        blocks.append(_geo_profit_block(view))
    if selection.selected("operating_margin_bridge"):
        blocks.append("### Margin evidence")
        blocks.append("")
        blocks.append(_margin_component_block(view))
        blocks.append(_amount_bridge_block(view))
        blocks.append(_margin_change_block(view))
        blocks.append(_attribution_block(view))
    if selection.selected("cash_conversion"):
        blocks.append("### Cash evidence")
        blocks.append("")
        blocks.append(_cash_block(view))
    blocks.append("### Relationship records")
    blocks.append("")
    blocks.append(_assessment_block(view))
    blocks.append(_residual_conclusion(view))
    blocks.append("### Sources and methodology")
    blocks.append("")
    blocks.append(
        "Numbers come from the existing verified BAV calculation path. "
        "Reported facts, identities, proxies, localizations, management "
        "attributions and unresolved questions are kept distinct. Exact "
        "reconstruction does not establish causation. Missing observations "
        "stay unavailable; an explicit zero remains zero. Fiscal-year labels "
        "follow the issuer mapping and are not derived from the calendar year "
        "of the period-end date."
    )
    body = "\n".join(part for part in blocks if part is not None)
    lowered = body.lower()
    for term in _FORBIDDEN_RESEARCH:
        if term in lowered:
            raise ValueError(f"Drivers prose contains {term!r}")
    return body if body.endswith("\n") else body + "\n"


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
        i
        for i in range(len(view.periods))
        if view.revenue_growth[i] is not None and view.store_growth[i] is not None
    ]
    labels = []
    for index in indexes:
        label = _figure_period_label(view, index)
        if view.fifty_three_week_period == view.periods[index]:
            label = f"{label}\n53-week"
        labels.append(label)
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
    ax.set_xticks(x, labels)
    ax.set_ylabel("Percent")
    ax.axhline(0, color=style.black, linewidth=0.8)
    ax.legend(loc="upper right")
    finish_figure(
        fig,
        ax,
        style,
        "Revenue growth versus store-count growth",
        f"Source: {view.display_name} BAV income statement and company-operated store counts.\n"
        "Comparable-sales observations are kept separate and are not connected here.",
        path,
    )


def _style_axis(ax, style: ResearchStyle) -> None:
    ax.set_facecolor(style.white)
    ax.tick_params(colors=style.black, width=0.8)
    for spine in ax.spines.values():
        spine.set_color(style.black)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(0, color=style.black, linewidth=0.8)


def plot_geography(view: DriversView, path: Path, style: ResearchStyle) -> None:
    from matplotlib import pyplot as plt

    latest = _latest_growth_index(view)
    identities = list(view.geo_identities)
    labels = [SEGMENT_LABELS[identity] for identity in identities]
    revenue = []
    profit = []
    for identity in identities:
        amounts = (
            {}
            if view.geo_revenue_amount_changes is None
            else view.geo_revenue_amount_changes[latest]
        )
        profits = (
            {}
            if view.geo_profit_changes is None
            else view.geo_profit_changes[latest]
        )
        revenue.append(
            None if amounts.get(identity) is None else _millions(amounts[identity])
        )
        profit.append(
            None if profits.get(identity) is None else _millions(profits[identity])
        )
    reconciling = (
        None
        if view.geo_reconciling_profit_change is None
        else view.geo_reconciling_profit_change[latest]
    )
    if reconciling is not None:
        labels.append("Corporate / unallocated")
        revenue.append(None)
        profit.append(_millions(reconciling))
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4.8), dpi=150)
    fig.patch.set_facecolor(style.white)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.76, bottom=0.28, wspace=0.32)
    x = list(range(len(labels)))
    for ax, values, title, ylabel in (
        (axes[0], revenue, "Revenue change", "USD millions"),
        (axes[1], profit, "Operating-profit change", "USD millions"),
    ):
        _style_axis(ax, style)
        heights = [0.0 if value is None else value for value in values]
        colors = [
            style.white if value is None else style.series_color(index)
            for index, value in enumerate(values)
        ]
        edges = [
            style.white if value is None else style.black
            for value in values
        ]
        ax.bar(x, heights, color=colors, edgecolor=edges, linewidth=0.4)
        ax.set_xticks(x, labels, rotation=25, ha="right")
        ax.set_title(title, loc="left", color=style.black, fontsize=style.label_pt)
        ax.set_ylabel(ylabel)
    fig.suptitle(
        f"{view.labels[latest]} geographic revenue and operating-profit change",
        x=0.10,
        ha="left",
        color=style.black,
        fontsize=style.title_pt,
        fontweight="regular",
    )
    finish_figure(
        fig,
        axes[0],
        style,
        "Revenue change",
        f"Source: {view.display_name} BAV geographic segment analysis.\n"
        "Separate scales. Corporate/unallocated items appear only in the profit panel.",
        path,
    )


def plot_margin(view: DriversView, path: Path, style: ResearchStyle) -> None:
    latest = _latest_growth_index(view)
    series = [
        (view.gross_margin_contribution, "Gross margin"),
        (view.sga_ratio_contribution, "SG&A / revenue"),
        (view.impairment_ratio_contribution, "Impairment / revenue"),
        (view.other_operating_ratio_contribution, "Other operating items"),
    ]
    labels = []
    heights = []
    for values, label in series:
        if not values or latest >= len(values) or values[latest] is None:
            continue
        labels.append(label)
        heights.append(values[latest] * 100)
    reported = (
        None
        if view.reported_operating_margin_change is None
        or latest >= len(view.reported_operating_margin_change)
        else view.reported_operating_margin_change[latest]
    )
    fig, ax = new_figure(style)
    x = list(range(len(labels)))
    ax.bar(x, heights, color=[style.series_color(i) for i in x], width=0.6)
    if reported is not None:
        ax.axhline(
            reported * 100,
            color=style.black,
            linewidth=1.0,
            linestyle="--",
            label="Reported operating-margin change",
        )
        ax.legend(loc="best")
    ax.set_xticks(x, labels, rotation=15, ha="right")
    ax.set_ylabel("Percentage-point contribution")
    ax.axhline(0, color=style.black, linewidth=0.8)
    finish_figure(
        fig,
        ax,
        style,
        f"{view.labels[latest]} operating-margin bridge",
        f"Source: {view.display_name} BAV income statement.\n"
        "Signed identity only. Management estimates are not mixed into this bridge.",
        path,
    )


def plot_cash(view: DriversView, path: Path, style: ResearchStyle) -> None:
    indexes = [
        i
        for i in range(len(view.periods))
        if view.cfo is not None
        and view.net_income is not None
        and view.cfo[i] is not None
        and view.net_income[i] is not None
    ]
    if len(indexes) > 2:
        indexes = indexes[-2:]
    labels = [_figure_period_label(view, i) for i in indexes]
    x = list(range(len(indexes)))
    width = 0.36
    fig, ax = new_figure(style)
    ax.bar(
        [i - width / 2 for i in x],
        [_millions(view.cfo[i]) for i in indexes],
        width=width,
        color=style.series_color(0),
        label="Cash from operations",
    )
    ax.bar(
        [i + width / 2 for i in x],
        [_millions(view.net_income[i]) for i in indexes],
        width=width,
        color=style.series_color(1),
        label="Net income",
    )
    ax.set_xticks(x, labels)
    ax.set_ylabel(f"Millions of {view.currency}")
    ax.axhline(0, color=style.black, linewidth=0.8)
    ax.legend(loc="best")
    finish_figure(
        fig,
        ax,
        style,
        "Cash from operations versus net income",
        f"Source: {view.display_name} BAV cash-flow and income statements.\n"
        "Diagnostic comparison only; not a manipulation finding or complete CFO explanation.",
        path,
    )


def write_placeholders(research_dir: Path, company: str) -> None:
    research_dir.mkdir(parents=True, exist_ok=True)
    for name in placeholder_filenames(company):
        (research_dir / name).write_bytes(b"")


_PLOT_BY_ID = {
    "growth": plot_growth,
    "geography": plot_geography,
    "margin": plot_margin,
    "cash": plot_cash,
}


def selected_figure_names(view: DriversView) -> tuple[str, ...]:
    selection = view.selection or select_driver_argument(view)
    names = []
    for identifier in selection.figure_ids:
        if identifier in _PLOT_BY_ID:
            names.append(f"{identifier}.png")
    return tuple(names)


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
    for name in selected_figure_names(view):
        identifier = name.removesuffix(".png")
        _PLOT_BY_ID[identifier](view, figures_dir / name, style)
    return view
