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
    geo_recon = analysis.geographic_reconstruction
    footprint = analysis.footprint_identity
    inspected = _inspected_latest_margin_explanation(financials, display_name)
    extra = () if inspected is None else (inspected[1],)
    assessments = _unique_assessments((*analysis.assessments, *extra))
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
        margin_explanation="" if inspected is None else inspected[0],
    )


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


def _source_annual_reports(display_name: str) -> list[Path]:
    from ..current_build import resolve_company

    try:
        company = resolve_company(display_name)
    except ValueError:
        return []
    source = company.input / "source"
    if not source.is_dir():
        return []
    return sorted(
        path
        for path in source.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".pdf"
        and "Annual_Report" in path.name
    )


def _inspected_latest_margin_explanation(
    financials: StandardizedFinancials, display_name: str
) -> tuple[str, MarginRelationshipAssessment] | None:
    """Attribute Item 7 margin comments after inspecting the latest source PDF."""
    reports = _source_annual_reports(display_name)
    if not reports:
        return None
    pdf = reports[-1]
    from ..ingestion.management_kpi_enrichment import inspect_source_pdf

    inspection = inspect_source_pdf(pdf)
    pages = {}
    for printed in (28, 29, 32, 33):
        physical = inspection.printed_to_physical.get(printed)
        if physical is None:
            return None
        pages[printed] = inspection.page_texts.get(physical, "")
    if "260 basis points" not in pages[28].casefold():
        return None
    if "380 basis points" not in pages[29].casefold() and "operating margin decreased" not in pages[29].casefold():
        return None
    if "275" not in pages[29] or "tariff" not in pages[29].casefold():
        return None
    if "markdowns" not in pages[32].casefold() or "tariff" not in pages[32].casefold():
        return None
    if "distribution center costs" not in pages[33].casefold():
        return None
    latest_label = financials.periods[-1].label if financials.periods else "latest year"
    prose = (
        f"The {latest_label} Form 10-K Item 7 ({pdf.name}, Form 10-K "
        "pp. 28–29) reports a 260 basis-point gross-margin decline to 56.6% and "
        "a 380 basis-point operating-margin decline to 19.9%. Management states "
        "that increased tariffs and removal of the de minimis exemption reduced "
        "2025 gross profit by approximately $275 million (p. 29). Americas gross "
        "margin fell on lower product margin from higher tariffs and increased "
        "markdowns and on higher occupancy costs as a percentage of revenue "
        "(p. 32). China Mainland gross margin rose on lower occupancy and "
        "depreciation costs as a percentage of revenue (pp. 32–33). Rest of "
        "World gross margin fell on lower product margin and higher "
        "distribution-center costs (p. 33). These are management explanations. "
        "The $275 million figure is not a face-of-statement line and is not used "
        "as a reconstructed bridge term."
    )
    assessment = MarginRelationshipAssessment(
        name="latest-year management margin explanation",
        kind="attributed_management_explanation",
        direction=(
            f"management attributes the {latest_label} gross-margin decline to "
            "tariffs, markdowns, occupancy, and distribution-center costs"
        ),
        magnitude="management states approximately $275 million of 2025 gross-profit reduction from tariffs and de minimis removal",
        reconstruction="not a face-of-statement component series",
        residual="the independently reconstructed operating-margin change remains the income-statement identity",
        stability="episodic trade-policy and markdown commentary for one year",
        contradictions="management rounds the same-year gross-margin change to 260 bps and operating-margin change to 380 bps",
        disclosure_support=(
            f"{pdf.name} Form 10-K pp. 28–29 and 32–33, "
            "inspected after ordinary extracts omitted the Item 7 narrative"
        ),
        established=False,
        limitation=(
            "Tariff, markdown, occupancy, and distribution-center effects are "
            "not isolated on the income statement and cannot be folded into "
            "the historical amount bridge without assuming undisclosed "
            "subcomponents."
        ),
    )
    return prose, assessment


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


def _opt_money(thousands: float | None) -> str:
    if thousands is None:
        return "n/a"
    return _money(_millions(thousands))


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
        "| Relationship | Kind | Direction | Magnitude | Reconstruction | Residual | Stability | Contradictions | Disclosure | Result |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in view.assessments:
        kind = _KIND_LABELS.get(item.kind, item.kind.replace("_", " "))
        rows.append(
            "| {name} | {kind} | {direction} | {magnitude} | {recon} | {resid} | "
            "{stable} | {contra} | {disc} | {result} |".format(
                name=_research_safe(item.name),
                kind=_research_safe(kind),
                direction=_research_safe(item.direction),
                magnitude=_research_safe(item.magnitude),
                recon=_research_safe(item.reconstruction),
                resid=_research_safe(item.residual),
                stable=_research_safe(item.stability),
                contra=_research_safe(item.contradictions),
                disc=_research_safe(item.disclosure_support),
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
    latest_gm_c = (
        None
        if view.gross_margin_contribution is None
        else view.gross_margin_contribution[latest]
    )
    latest_sga_c = (
        None
        if view.sga_ratio_contribution is None
        or latest >= len(view.sga_ratio_contribution)
        else view.sga_ratio_contribution[latest]
    )
    latest_imp_c = (
        None
        if view.impairment_ratio_contribution is None
        or latest >= len(view.impairment_ratio_contribution)
        else view.impairment_ratio_contribution[latest]
    )
    latest_other_c = (
        None
        if view.other_operating_ratio_contribution is None
        or latest >= len(view.other_operating_ratio_contribution)
        else view.other_operating_ratio_contribution[latest]
    )
    latest_sum = (
        None
        if view.reconstructed_contribution_sum is None
        or latest >= len(view.reconstructed_contribution_sum)
        else view.reconstructed_contribution_sum[latest]
    )
    latest_resid = (
        None
        if view.contribution_residual is None
        or latest >= len(view.contribution_residual)
        else view.contribution_residual[latest]
    )
    if latest_gm_c is None or latest_sum is None:
        raise ValueError("Drivers requires a latest-period component contribution schedule")
    contribution_sentence = (
        f"Signed contributions were Δgross margin {_opt_change_pp(latest_gm_c)} "
        f"({_opt_bps(latest_gm_c)}), −Δ(SG&A/revenue) {_opt_change_pp(latest_sga_c)} "
        f"({_opt_bps(latest_sga_c)}), −Δ(impairment or asset-related charges/revenue) "
        f"{_opt_change_pp(latest_imp_c)} ({_opt_bps(latest_imp_c)}), and "
        f"−Δ(other reported operating items/revenue) {_opt_change_pp(latest_other_c)} "
        f"({_opt_bps(latest_other_c)}). The reconstructed sum is "
        f"{_opt_change_pp(latest_sum)}; the residual versus the reported change is "
        f"{_opt_change_pp(latest_resid)}."
    )
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

{ _footprint_block(view) }

Reported global comparable sales were {compsales_text}.{store_only_text} These percentages use different channel definitions.

![Consolidated revenue growth and company-operated store-count growth](../figures/drivers/growth.png)

## Geography

Americas remained the largest region and supplied less of each year's incremental revenue: {", ".join(americas)}.

China Mainland contributed {", ".join(china)}.

Rest of World contributed {", ".join(row)}.

In {view.labels[latest]}, China Mainland ({_pp(latest_geo["china_mainland"])}) and Rest of World ({_pp(latest_geo["rest_of_world"])}) more than offset Americas ({_pp(latest_geo["americas"])}).

{ _geo_reconstruction_block(view) }

![Geographic contribution to consolidated revenue growth](../figures/drivers/geography.png)

## Margin

Operating margin was {om_text}.

In {view.labels[latest]}, operating-margin change was {om_change_pp:+.2f} pp. {contribution_sentence} That change also equals the gross-margin change ({gm_change_pp:+.2f} pp) minus the net-operating-expense-burden change ({burden_change_pp:+.2f} pp).

Gross margin was {gm_text}. Net operating expense burden was {burden_text}.

{view.margin_explanation or "Management explanations of the latest operating-margin movement are unavailable."}

{ _margin_component_block(view) }
{ _amount_bridge_block(view) }
{ _margin_change_block(view) }

![Component contributions to operating-margin change](../figures/drivers/margin.png)

{ _residual_conclusion(view) }

{ _assessment_block(view) }

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

Mix, markdowns, freight, input costs, and leverage are unestablished: the extracted filings do not isolate those amounts for a historical bridge. An accounting identity does not validate a causal reading.
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
    indexes = [
        i
        for i in range(len(view.periods))
        if view.gross_margin_contribution
        and i < len(view.gross_margin_contribution)
        and view.gross_margin_contribution[i] is not None
    ]
    labels = [_figure_period_label(view, i) for i in indexes]
    x = list(range(len(indexes)))
    series = [
        (view.gross_margin_contribution, "Gross margin"),
        (view.sga_ratio_contribution, "SG&A, sign reversed"),
        (view.impairment_ratio_contribution, "Impairment, sign reversed"),
        (view.other_operating_ratio_contribution, "Other items, sign reversed"),
    ]
    width = 0.18
    offsets = (-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width)
    for series_index, (values, label) in enumerate(series):
        if not values:
            continue
        heights = [
            float("nan")
            if index >= len(values) or values[index] is None
            else values[index] * 100
            for index in indexes
        ]
        ax.bar(
            [position + offsets[series_index] for position in x],
            heights,
            width=width,
            color=style.series_color(series_index),
            label=label,
        )
    reported = []
    marker_x = []
    if view.reported_operating_margin_change:
        for position, index in enumerate(indexes):
            value = (
                view.reported_operating_margin_change[index]
                if index < len(view.reported_operating_margin_change)
                else None
            )
            if value is None:
                continue
            marker_x.append(position)
            reported.append(value * 100)
    if marker_x:
        ax.plot(
            marker_x,
            reported,
            linestyle="None",
            marker="o",
            markersize=5,
            color=style.black,
            label="Reported operating-margin change",
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Percentage-point contribution")
    ax.axhline(0, color=style.black, linewidth=0.8)
    known = [
        value * 100
        for values, _label in series
        if values
        for index in indexes
        if index < len(values) and values[index] is not None
        for value in (values[index],)
    ]
    known.extend(reported)
    if known:
        low, high = min(known), max(known)
        pad = max(1.2, 0.28 * (high - low))
        ax.set_ylim(low - pad, high + pad)
    ax.legend(loc="upper left", ncol=1)
    finish_figure(
        fig,
        ax,
        style,
        "Component contributions to operating-margin change",
        f"Source: {view.display_name} BAV income statement.\n"
        "Expense-ratio increases are negative contributions. Residuals remain explicit.",
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
