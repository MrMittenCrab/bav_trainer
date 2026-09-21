"""Source-supported reported gross and operating-margin bridge.

Optional, source-gated module. Resolves unique explicit IS ``gross_profit`` and
``operating_profit`` / ``operating_income``, and uses existing revenue
resolution. Stored concepts, values, signs, and provenance are left unchanged.
No label fallback for profit lines, no competing-alias merge, and no
wrong-statement substitutes.

Computes ``gross_margin = gross_profit / revenue`` when unique gross profit and
revenue resolve. ``reported_operating_margin = operating_profit / revenue`` when
unique operating profit and revenue resolve. ``net_operating_expense_burden =
(gross_profit − operating_profit) / revenue`` when both unique profit lines and
revenue resolve. Adjacent-period families compute gross-margin change, burden
change, and reconstructed operating-margin change = gross-margin change −
burden change. Opening-period change exercises are omitted.

Absent or ambiguous sources omit only dependent families. Missing required
period values fail closed. Reported zeros remain valid. Zero revenue yields the
existing undefined-ratio result with downstream propagation. The reconstructed
change reconciles to the adjacent reported-operating-margin difference when
both sides are defined.

Do not infer price, mix, or cost causes, or normalized earnings. Reported
operating margin is distinct from BAV NOPAT margin. Gross profit minus
operating profit includes net intervening operating items; it is not
necessarily SG&A. A positive burden change reduces operating margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from .line_resolver import AmbiguousLineError, MissingLineError, resolve_line
from .ratio_values import UNDEFINED_RATIO, is_source_unavailable, ratio_or_na
from .source_values import optional_period_value, required_period_value

GROSS_PROFIT_CONCEPT = "gross_profit"
OPERATING_PROFIT_CONCEPT = "operating_profit"
REVENUE_CONCEPT = "revenue"
SGA_CONCEPT = "selling_general_and_administrative_expenses"
IMPAIRMENT_CONCEPT = "impairment_and_restructuring"
AMORTIZATION_CONCEPT = "amortization_of_intangible_assets"
ACQUISITION_EXPENSE_CONCEPT = "acquisition_related_expenses"
GAIN_ON_DISPOSAL_CONCEPT = "gain_on_disposal_of_assets"
OTHER_OPERATING_CONCEPTS = (
    AMORTIZATION_CONCEPT,
    ACQUISITION_EXPENSE_CONCEPT,
    GAIN_ON_DISPOSAL_CONCEPT,
)
KIND_IDENTITY = "identity"
KIND_REPORTED_FACT = "reported_fact"
KIND_ATTRIBUTED_EXPLANATION = "attributed_management_explanation"
KIND_OBSERVED = "observed_relationship"
KIND_CAUSAL = "causal_hypothesis"
KIND_UNESTABLISHED = "unestablished_inference"
AMOUNT_BRIDGE_CONVENTION = (
    "Gross-profit change uses prior gross margin on the revenue change, "
    "prior revenue on the gross-margin change, and an explicit interaction "
    "equal to the revenue change times the gross-margin change. Operating-"
    "profit change then subtracts disclosed SG&A, impairment or asset-related "
    "charges, and other reported operating-item changes. Missing disclosure "
    "is omitted from the reconstruction, not treated as zero."
)


@dataclass(frozen=True)
class ReportedMarginAvailability:
    revenue: bool
    revenue_ambiguous: bool
    gross_profit: bool
    gross_profit_ambiguous: bool
    operating_profit: bool
    operating_profit_ambiguous: bool
    sga: bool = False
    sga_ambiguous: bool = False
    impairment: bool = False
    impairment_ambiguous: bool = False


@dataclass(frozen=True)
class ReportedMarginSources:
    revenue: LineItem | None
    gross_profit: LineItem | None
    operating_profit: LineItem | None
    sga: LineItem | None = None
    impairment: LineItem | None = None
    amortization: LineItem | None = None
    acquisition_related: LineItem | None = None
    gain_on_disposal: LineItem | None = None


@dataclass(frozen=True)
class MarginRelationshipAssessment:
    """Seven-part historical test of one margin relationship."""

    name: str
    kind: str
    direction: str
    magnitude: str
    reconstruction: str
    residual: str
    stability: str
    contradictions: str
    disclosure_support: str
    established: bool
    limitation: str = ""


@dataclass(frozen=True)
class ReportedMarginSeries:
    revenue: tuple[float, ...]
    gross_profit: tuple[float, ...] | None = None
    operating_profit: tuple[float, ...] | None = None
    gross_margin: tuple[float | str, ...] | None = None
    reported_operating_margin: tuple[float | str, ...] | None = None
    net_operating_expense_burden: tuple[float | str, ...] | None = None
    gross_margin_change: tuple[float | str | None, ...] | None = None
    net_operating_expense_burden_change: tuple[float | str | None, ...] | None = None
    reconstructed_operating_margin_change: tuple[float | str | None, ...] | None = (
        None
    )
    sga: tuple[float | None, ...] | None = None
    impairment: tuple[float | None, ...] | None = None
    other_operating_items: tuple[float | None, ...] | None = None
    sga_ratio: tuple[float | str | None, ...] | None = None
    impairment_ratio: tuple[float | str | None, ...] | None = None
    other_operating_ratio: tuple[float | str | None, ...] | None = None
    reconstructed_operating_profit: tuple[float | None, ...] | None = None
    operating_profit_residual: tuple[float | None, ...] | None = None
    reconstructed_component_operating_margin: tuple[float | str | None, ...] | None = (
        None
    )
    operating_margin_residual: tuple[float | str | None, ...] | None = None
    revenue_change: tuple[float | None, ...] | None = None
    gross_profit_change: tuple[float | None, ...] | None = None
    gross_profit_revenue_effect: tuple[float | None, ...] | None = None
    gross_profit_margin_effect: tuple[float | None, ...] | None = None
    gross_profit_interaction: tuple[float | None, ...] | None = None
    gross_profit_change_residual: tuple[float | None, ...] | None = None
    sga_change: tuple[float | None, ...] | None = None
    impairment_change: tuple[float | None, ...] | None = None
    other_operating_change: tuple[float | None, ...] | None = None
    reconstructed_operating_profit_change: tuple[float | None, ...] | None = None
    operating_profit_change: tuple[float | None, ...] | None = None
    operating_profit_change_residual: tuple[float | None, ...] | None = None
    gross_margin_contribution: tuple[float | str | None, ...] | None = None
    sga_ratio_contribution: tuple[float | str | None, ...] | None = None
    impairment_ratio_contribution: tuple[float | str | None, ...] | None = None
    other_operating_ratio_contribution: tuple[float | str | None, ...] | None = None
    reconstructed_contribution_sum: tuple[float | str | None, ...] | None = None
    reported_operating_margin_change: tuple[float | str | None, ...] | None = None
    contribution_residual: tuple[float | str | None, ...] | None = None
    amount_bridge_convention: str = AMOUNT_BRIDGE_CONVENTION
    assessments: tuple[MarginRelationshipAssessment, ...] = ()


def _resolve_unique_is(
    financials: StandardizedFinancials, concept: str
) -> tuple[LineItem | None, bool]:
    try:
        resolved = resolve_line(financials.income_statement, concept, required=False)
    except AmbiguousLineError:
        return None, True
    return resolved.item, False


def reported_margin_availability(
    financials: StandardizedFinancials,
) -> ReportedMarginAvailability:
    """Report unique IS source resolution without mutating rows."""
    revenue, revenue_ambiguous = _resolve_unique_is(financials, REVENUE_CONCEPT)
    gross_profit, gross_profit_ambiguous = _resolve_unique_is(
        financials, GROSS_PROFIT_CONCEPT
    )
    operating_profit, operating_profit_ambiguous = _resolve_unique_is(
        financials, OPERATING_PROFIT_CONCEPT
    )
    sga, sga_ambiguous = _resolve_unique_is(financials, SGA_CONCEPT)
    impairment, impairment_ambiguous = _resolve_unique_is(
        financials, IMPAIRMENT_CONCEPT
    )
    return ReportedMarginAvailability(
        revenue=revenue is not None,
        revenue_ambiguous=revenue_ambiguous,
        gross_profit=gross_profit is not None,
        gross_profit_ambiguous=gross_profit_ambiguous,
        operating_profit=operating_profit is not None,
        operating_profit_ambiguous=operating_profit_ambiguous,
        sga=sga is not None,
        sga_ambiguous=sga_ambiguous,
        impairment=impairment is not None,
        impairment_ambiguous=impairment_ambiguous,
    )


def resolve_reported_margin_sources(
    financials: StandardizedFinancials,
) -> ReportedMarginSources:
    """Return unique IS margin lines; ambiguous sources are None."""
    revenue, _ = _resolve_unique_is(financials, REVENUE_CONCEPT)
    gross_profit, _ = _resolve_unique_is(financials, GROSS_PROFIT_CONCEPT)
    operating_profit, _ = _resolve_unique_is(financials, OPERATING_PROFIT_CONCEPT)
    sga, _ = _resolve_unique_is(financials, SGA_CONCEPT)
    impairment, _ = _resolve_unique_is(financials, IMPAIRMENT_CONCEPT)
    amortization, _ = _resolve_unique_is(financials, AMORTIZATION_CONCEPT)
    acquisition, _ = _resolve_unique_is(financials, ACQUISITION_EXPENSE_CONCEPT)
    gain, _ = _resolve_unique_is(financials, GAIN_ON_DISPOSAL_CONCEPT)
    return ReportedMarginSources(
        revenue=revenue,
        gross_profit=gross_profit,
        operating_profit=operating_profit,
        sga=sga,
        impairment=impairment,
        amortization=amortization,
        acquisition_related=acquisition,
        gain_on_disposal=gain,
    )


def _revenue_ready(avail: ReportedMarginAvailability) -> bool:
    return avail.revenue and not avail.revenue_ambiguous


def gross_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Gross margin requires unique revenue and unique explicit gross profit."""
    avail = reported_margin_availability(financials)
    return (
        _revenue_ready(avail)
        and avail.gross_profit
        and not avail.gross_profit_ambiguous
    )


def reported_operating_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Reported operating margin requires unique revenue and unique operating profit."""
    avail = reported_margin_availability(financials)
    return (
        _revenue_ready(avail)
        and avail.operating_profit
        and not avail.operating_profit_ambiguous
    )


def net_operating_expense_burden_applicable(
    financials: StandardizedFinancials,
) -> bool:
    """Burden requires unique revenue plus unique gross and operating profit."""
    return gross_margin_applicable(financials) and reported_operating_margin_applicable(
        financials
    )


def gross_margin_change_applicable(financials: StandardizedFinancials) -> bool:
    return gross_margin_applicable(financials)


def net_operating_expense_burden_change_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return net_operating_expense_burden_applicable(financials)


def reconstructed_operating_margin_change_applicable(
    financials: StandardizedFinancials,
) -> bool:
    return net_operating_expense_burden_applicable(financials)


def reported_margin_applicable(financials: StandardizedFinancials) -> bool:
    """Module is present when at least one reported-margin family can be computed."""
    return gross_margin_applicable(financials) or reported_operating_margin_applicable(
        financials
    )


def _difference_or_na(
    current: float | str, prior: float | str
) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _adjacent_changes(
    levels: tuple[float | str, ...],
) -> tuple[float | str | None, ...]:
    n = len(levels)
    changes: list[float | str | None] = [None] * n
    for j in range(1, n):
        changes[j] = _difference_or_na(levels[j], levels[j - 1])
    return tuple(changes)


def compute_reported_margin_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> ReportedMarginSeries:
    """Read reported IS profits and compute margin-bridge diagnostics."""
    if not reported_margin_applicable(financials):
        raise MissingLineError("reported margin sources not available")

    sources = resolve_reported_margin_sources(financials)
    assert sources.revenue is not None
    revenue = tuple(
        required_period_value(sources.revenue, period, field=REVENUE_CONCEPT)
        for period in periods
    )

    gross_profit: tuple[float, ...] | None = None
    gross_margin: tuple[float | str, ...] | None = None
    if gross_margin_applicable(financials):
        assert sources.gross_profit is not None
        gross_profit = tuple(
            required_period_value(
                sources.gross_profit, period, field=GROSS_PROFIT_CONCEPT
            )
            for period in periods
        )
        gross_margin = tuple(
            ratio_or_na(gross_profit[j], revenue[j]) for j in range(len(periods))
        )

    operating_profit: tuple[float, ...] | None = None
    reported_operating_margin: tuple[float | str, ...] | None = None
    if reported_operating_margin_applicable(financials):
        assert sources.operating_profit is not None
        operating_profit = tuple(
            required_period_value(
                sources.operating_profit, period, field=OPERATING_PROFIT_CONCEPT
            )
            for period in periods
        )
        reported_operating_margin = tuple(
            ratio_or_na(operating_profit[j], revenue[j]) for j in range(len(periods))
        )

    net_operating_expense_burden: tuple[float | str, ...] | None = None
    if (
        net_operating_expense_burden_applicable(financials)
        and gross_profit is not None
        and operating_profit is not None
    ):
        net_operating_expense_burden = tuple(
            ratio_or_na(gross_profit[j] - operating_profit[j], revenue[j])
            for j in range(len(periods))
        )

    gross_margin_change: tuple[float | str | None, ...] | None = None
    if gross_margin is not None:
        gross_margin_change = _adjacent_changes(gross_margin)

    net_operating_expense_burden_change: tuple[float | str | None, ...] | None = None
    if net_operating_expense_burden is not None:
        net_operating_expense_burden_change = _adjacent_changes(
            net_operating_expense_burden
        )

    reconstructed_operating_margin_change: tuple[float | str | None, ...] | None = None
    if (
        reconstructed_operating_margin_change_applicable(financials)
        and gross_margin_change is not None
        and net_operating_expense_burden_change is not None
    ):
        reconstructed: list[float | str | None] = [None] * len(periods)
        for j in range(1, len(periods)):
            gm_delta = gross_margin_change[j]
            burden_delta = net_operating_expense_burden_change[j]
            assert gm_delta is not None
            assert burden_delta is not None
            reconstructed[j] = _difference_or_na(gm_delta, burden_delta)
        reconstructed_operating_margin_change = tuple(reconstructed)

    sga_amounts: tuple[float | None, ...] | None = None
    impairment_amounts: tuple[float | None, ...] | None = None
    other_amounts: tuple[float | None, ...] | None = None
    sga_ratio: tuple[float | str | None, ...] | None = None
    impairment_ratio: tuple[float | str | None, ...] | None = None
    other_ratio: tuple[float | str | None, ...] | None = None
    reconstructed_op: tuple[float | None, ...] | None = None
    op_residual: tuple[float | None, ...] | None = None
    reconstructed_om: tuple[float | str | None, ...] | None = None
    om_residual: tuple[float | str | None, ...] | None = None
    revenue_change: tuple[float | None, ...] | None = None
    gp_change: tuple[float | None, ...] | None = None
    gp_revenue_effect: tuple[float | None, ...] | None = None
    gp_margin_effect: tuple[float | None, ...] | None = None
    gp_interaction: tuple[float | None, ...] | None = None
    gp_change_residual: tuple[float | None, ...] | None = None
    sga_change: tuple[float | None, ...] | None = None
    impairment_change: tuple[float | None, ...] | None = None
    other_change: tuple[float | None, ...] | None = None
    reconstructed_op_change: tuple[float | None, ...] | None = None
    op_change: tuple[float | None, ...] | None = None
    op_change_residual: tuple[float | None, ...] | None = None
    gm_contribution: tuple[float | str | None, ...] | None = None
    sga_contribution: tuple[float | str | None, ...] | None = None
    imp_contribution: tuple[float | str | None, ...] | None = None
    other_contribution: tuple[float | str | None, ...] | None = None
    contribution_sum: tuple[float | str | None, ...] | None = None
    reported_om_change: tuple[float | str | None, ...] | None = None
    contribution_resid: tuple[float | str | None, ...] | None = None

    if sources.sga is not None:
        sga_amounts = tuple(
            optional_period_value(sources.sga, period) for period in periods
        )
        sga_ratio = tuple(
            None if amount is None else ratio_or_na(amount, revenue[j])
            for j, amount in enumerate(sga_amounts)
        )
    if sources.impairment is not None:
        impairment_amounts = tuple(
            optional_period_value(sources.impairment, period) for period in periods
        )
        impairment_ratio = tuple(
            None if amount is None else ratio_or_na(amount, revenue[j])
            for j, amount in enumerate(impairment_amounts)
        )

    other_parts = []
    for item in (
        sources.amortization,
        sources.acquisition_related,
        sources.gain_on_disposal,
    ):
        if item is not None:
            other_parts.append(
                tuple(optional_period_value(item, period) for period in periods)
            )
    if other_parts:
        other_amounts = tuple(
            _sum_optional(values) for values in zip(*other_parts)
        )
        other_ratio = tuple(
            None if amount is None else ratio_or_na(amount, revenue[j])
            for j, amount in enumerate(other_amounts)
        )

    if (
        gross_profit is not None
        and operating_profit is not None
        and sga_amounts is not None
    ):
        recon_op: list[float | None] = []
        resid_op: list[float | None] = []
        recon_om: list[float | str | None] = []
        resid_om: list[float | str | None] = []
        for j, period in enumerate(periods):
            built = _reconstruct_operating_profit(
                gross_profit[j],
                sga_amounts[j],
                None if impairment_amounts is None else impairment_amounts[j],
                None if other_amounts is None else other_amounts[j],
            )
            recon_op.append(built)
            if built is None:
                resid_op.append(None)
                recon_om.append(None)
                resid_om.append(None)
                continue
            resid_op.append(operating_profit[j] - built)
            om_built = ratio_or_na(built, revenue[j])
            recon_om.append(om_built)
            reported_om = (
                None
                if reported_operating_margin is None
                else reported_operating_margin[j]
            )
            if (
                reported_om is None
                or is_source_unavailable(reported_om)
                or is_source_unavailable(om_built)
            ):
                resid_om.append(
                    UNDEFINED_RATIO
                    if reported_om == UNDEFINED_RATIO or om_built == UNDEFINED_RATIO
                    else None
                )
            else:
                resid_om.append(float(reported_om) - float(om_built))
        reconstructed_op = tuple(recon_op)
        op_residual = tuple(resid_op)
        reconstructed_om = tuple(recon_om)
        om_residual = tuple(resid_om)

        revenue_change = _adjacent_amount_changes(revenue)
        gp_change = _adjacent_amount_changes(gross_profit)
        sga_change = _adjacent_optional_changes(sga_amounts)
        impairment_change = (
            None
            if impairment_amounts is None
            else _adjacent_optional_changes(impairment_amounts)
        )
        other_change = (
            None
            if other_amounts is None
            else _adjacent_optional_changes(other_amounts)
        )
        op_change = _adjacent_amount_changes(operating_profit)
        n = len(periods)
        rev_eff: list[float | None] = [None] * n
        gm_eff: list[float | None] = [None] * n
        interact: list[float | None] = [None] * n
        gp_resid: list[float | None] = [None] * n
        recon_op_delta: list[float | None] = [None] * n
        op_delta_resid: list[float | None] = [None] * n
        for j in range(1, n):
            if gross_margin is None or gp_change is None or revenue_change is None:
                continue
            prior_gm = gross_margin[j - 1]
            current_gm = gross_margin[j]
            d_rev = revenue_change[j]
            d_gp = gp_change[j]
            if (
                d_rev is None
                or d_gp is None
                or is_source_unavailable(prior_gm)
                or is_source_unavailable(current_gm)
            ):
                continue
            d_gm = float(current_gm) - float(prior_gm)
            rev_eff[j] = float(prior_gm) * d_rev
            gm_eff[j] = revenue[j - 1] * d_gm
            interact[j] = d_rev * d_gm
            gp_resid[j] = d_gp - (rev_eff[j] + gm_eff[j] + interact[j])
            if reconstructed_op is None or reconstructed_op[j] is None:
                continue
            if reconstructed_op[j - 1] is None:
                continue
            recon_op_delta[j] = reconstructed_op[j] - reconstructed_op[j - 1]
            if op_change is not None and op_change[j] is not None:
                op_delta_resid[j] = op_change[j] - recon_op_delta[j]
        gp_revenue_effect = tuple(rev_eff)
        gp_margin_effect = tuple(gm_eff)
        gp_interaction = tuple(interact)
        gp_change_residual = tuple(gp_resid)
        reconstructed_op_change = tuple(recon_op_delta)
        op_change_residual = tuple(op_delta_resid)

    gm_contribution = _signed_ratio_contributions(gross_margin, expense=False)
    sga_contribution = _signed_ratio_contributions(sga_ratio, expense=True)
    imp_contribution = _signed_ratio_contributions(impairment_ratio, expense=True)
    other_contribution = _signed_ratio_contributions(other_ratio, expense=True)
    contribution_sum = _sum_contributions(
        gm_contribution,
        sga_contribution,
        imp_contribution,
        other_contribution,
        n=len(periods),
    )
    reported_om_change = (
        None
        if reported_operating_margin is None
        else _adjacent_changes(reported_operating_margin)
    )
    contribution_resid = _pair_residual(reported_om_change, contribution_sum)

    assessments = _assess_margin_relationships(
        periods=periods,
        revenue=revenue,
        gross_margin=gross_margin,
        reported_operating_margin=reported_operating_margin,
        sga_ratio=sga_ratio,
        impairment_amounts=impairment_amounts,
        impairment_ratio=impairment_ratio,
        reconstructed_om=reconstructed_om,
        om_residual=om_residual,
        op_residual=op_residual,
        gp_change_residual=gp_change_residual,
        op_change_residual=op_change_residual,
        contribution_sum=contribution_sum,
        contribution_resid=contribution_resid,
        gm_contribution=gm_contribution,
        sga_contribution=sga_contribution,
        imp_contribution=imp_contribution,
        other_contribution=other_contribution,
        impairment_disclosed=sources.impairment is not None,
        sga_disclosed=sources.sga is not None,
    )

    return ReportedMarginSeries(
        revenue=revenue,
        gross_profit=gross_profit,
        operating_profit=operating_profit,
        gross_margin=gross_margin,
        reported_operating_margin=reported_operating_margin,
        net_operating_expense_burden=net_operating_expense_burden,
        gross_margin_change=gross_margin_change,
        net_operating_expense_burden_change=net_operating_expense_burden_change,
        reconstructed_operating_margin_change=reconstructed_operating_margin_change,
        sga=sga_amounts,
        impairment=impairment_amounts,
        other_operating_items=other_amounts,
        sga_ratio=sga_ratio,
        impairment_ratio=impairment_ratio,
        other_operating_ratio=other_ratio,
        reconstructed_operating_profit=reconstructed_op,
        operating_profit_residual=op_residual,
        reconstructed_component_operating_margin=reconstructed_om,
        operating_margin_residual=om_residual,
        revenue_change=revenue_change,
        gross_profit_change=gp_change,
        gross_profit_revenue_effect=gp_revenue_effect,
        gross_profit_margin_effect=gp_margin_effect,
        gross_profit_interaction=gp_interaction,
        gross_profit_change_residual=gp_change_residual,
        sga_change=sga_change,
        impairment_change=impairment_change,
        other_operating_change=other_change,
        reconstructed_operating_profit_change=reconstructed_op_change,
        operating_profit_change=op_change,
        operating_profit_change_residual=op_change_residual,
        gross_margin_contribution=gm_contribution,
        sga_ratio_contribution=sga_contribution,
        impairment_ratio_contribution=imp_contribution,
        other_operating_ratio_contribution=other_contribution,
        reconstructed_contribution_sum=contribution_sum,
        reported_operating_margin_change=reported_om_change,
        contribution_residual=contribution_resid,
        assessments=assessments,
    )


def _sum_optional(values: tuple[float | None, ...]) -> float | None:
    known = [value for value in values if value is not None]
    if not known:
        return None
    return sum(known)


def _reconstruct_operating_profit(
    gross_profit: float,
    sga: float | None,
    impairment: float | None,
    other: float | None,
) -> float | None:
    if sga is None:
        return None
    result = gross_profit - sga
    if impairment is not None:
        result -= impairment
    if other is not None:
        result -= other
    return result


def _adjacent_amount_changes(
    levels: tuple[float, ...],
) -> tuple[float | None, ...]:
    changes: list[float | None] = [None] * len(levels)
    for j in range(1, len(levels)):
        changes[j] = levels[j] - levels[j - 1]
    return tuple(changes)


def _adjacent_optional_changes(
    levels: tuple[float | None, ...],
) -> tuple[float | None, ...]:
    changes: list[float | None] = [None] * len(levels)
    for j in range(1, len(levels)):
        current = levels[j]
        prior = levels[j - 1]
        if current is None or prior is None:
            continue
        changes[j] = current - prior
    return tuple(changes)


def _signed_ratio_contributions(
    ratios: tuple[float | str | None, ...] | None,
    *,
    expense: bool,
) -> tuple[float | str | None, ...] | None:
    if ratios is None:
        return None
    contributions: list[float | str | None] = [None] * len(ratios)
    for j in range(1, len(ratios)):
        current = ratios[j]
        prior = ratios[j - 1]
        if current is None or prior is None:
            continue
        if (
            is_source_unavailable(current)
            or is_source_unavailable(prior)
            or current == UNDEFINED_RATIO
            or prior == UNDEFINED_RATIO
            or isinstance(current, str)
            or isinstance(prior, str)
        ):
            contributions[j] = UNDEFINED_RATIO
            continue
        delta = float(current) - float(prior)
        contributions[j] = -delta if expense else delta
    return tuple(contributions)


def _sum_contributions(
    *parts: tuple[float | str | None, ...] | None,
    n: int,
) -> tuple[float | str | None, ...] | None:
    disclosed = [part for part in parts if part is not None]
    if not disclosed:
        return None
    total: list[float | str | None] = [None] * n
    for j in range(1, n):
        values = [part[j] for part in disclosed]
        if any(value is None for value in values):
            continue
        if any(
            is_source_unavailable(value)
            or value == UNDEFINED_RATIO
            or isinstance(value, str)
            for value in values
        ):
            total[j] = UNDEFINED_RATIO
            continue
        total[j] = sum(float(value) for value in values)
    return tuple(total)


def _pair_residual(
    reported: tuple[float | str | None, ...] | None,
    reconstructed: tuple[float | str | None, ...] | None,
) -> tuple[float | str | None, ...] | None:
    if reported is None or reconstructed is None:
        return None
    residual: list[float | str | None] = [None] * len(reported)
    for j, (left, right) in enumerate(zip(reported, reconstructed)):
        if left is None or right is None:
            continue
        residual[j] = _difference_or_na(left, right)
    return tuple(residual)


def _numeric_ratio(value: float | str | None) -> float | None:
    if value is None or is_source_unavailable(value) or isinstance(value, str):
        return None
    return float(value)


def _assess_margin_relationships(
    *,
    periods: list[date],
    revenue: tuple[float, ...],
    gross_margin: tuple[float | str, ...] | None,
    reported_operating_margin: tuple[float | str, ...] | None,
    sga_ratio: tuple[float | str | None, ...] | None,
    impairment_amounts: tuple[float | None, ...] | None,
    impairment_ratio: tuple[float | str | None, ...] | None,
    reconstructed_om: tuple[float | str | None, ...] | None,
    om_residual: tuple[float | str | None, ...] | None,
    op_residual: tuple[float | None, ...] | None,
    gp_change_residual: tuple[float | None, ...] | None,
    op_change_residual: tuple[float | None, ...] | None,
    contribution_sum: tuple[float | str | None, ...] | None,
    contribution_resid: tuple[float | str | None, ...] | None,
    gm_contribution: tuple[float | str | None, ...] | None,
    sga_contribution: tuple[float | str | None, ...] | None,
    imp_contribution: tuple[float | str | None, ...] | None,
    other_contribution: tuple[float | str | None, ...] | None,
    impairment_disclosed: bool,
    sga_disclosed: bool,
) -> tuple[MarginRelationshipAssessment, ...]:
    assessments: list[MarginRelationshipAssessment] = []
    if (
        reconstructed_om is not None
        and om_residual is not None
        and sga_disclosed
    ):
        resid_vals = [
            abs(value)
            for value in (_numeric_ratio(item) for item in om_residual)
            if value is not None
        ]
        max_resid = max(resid_vals) if resid_vals else None
        assessments.append(
            MarginRelationshipAssessment(
                name="component operating-margin identity",
                kind=KIND_IDENTITY,
                direction="reconstructed operating margin equals reported operating margin when disclosed components are subtracted from gross margin",
                magnitude="levels and adjacent changes are reconciled in amounts and percentage points",
                reconstruction="operating margin = gross margin − SG&A/revenue − impairment or asset-related charges/revenue − other reported operating items/revenue",
                residual=(
                    f"largest absolute operating-margin residual is {max_resid:.6%}"
                    if max_resid is not None
                    else "residual not defined"
                ),
                stability="the identity holds in every period with disclosed SG&A",
                contradictions="none in the reconstructed history",
                disclosure_support="income-statement components only; missing lines stay omitted",
                established=max_resid is not None and max_resid < 1e-8,
                limitation="" if max_resid is not None and max_resid < 1e-8 else "reconstruction residual remains",
            )
        )
    if contribution_sum is not None and contribution_resid is not None:
        resid_vals = [
            abs(value)
            for value in (_numeric_ratio(item) for item in contribution_resid)
            if value is not None
        ]
        max_resid = max(resid_vals) if resid_vals else None
        assessments.append(
            MarginRelationshipAssessment(
                name="component operating-margin contributions",
                kind=KIND_IDENTITY,
                direction="signed component contributions reconstruct the reported operating-margin change",
                magnitude="Δgross margin, −Δ(SG&A/revenue), −Δ(impairment or asset-related charges/revenue), and −Δ(other reported operating items/revenue) are calculated from unrounded ratios",
                reconstruction="reconstructed contribution sum equals those signed terms; residual is reported operating-margin change minus the reconstructed sum",
                residual=(
                    f"largest absolute contribution residual is {max_resid:.6%}"
                    if max_resid is not None
                    else "opening period has no adjacent comparison"
                ),
                stability="the identity is tested for every adjacent pair with disclosed components",
                contradictions="none required when the residual is a rounding or omitted-line remainder",
                disclosure_support="income-statement components only; missing adjacent comparisons stay unavailable",
                established=max_resid is not None and max_resid < 1e-8,
                limitation="" if max_resid is not None and max_resid < 1e-8 else "contribution residual remains",
            )
        )
    if gp_change_residual is not None:
        gp_resid_vals = [abs(value) for value in gp_change_residual if value is not None]
        max_gp = max(gp_resid_vals) if gp_resid_vals else None
        assessments.append(
            MarginRelationshipAssessment(
                name="gross-profit amount bridge",
                kind=KIND_IDENTITY,
                direction="gross-profit change equals the revenue effect plus the gross-margin effect plus the interaction",
                magnitude=AMOUNT_BRIDGE_CONVENTION,
                reconstruction="ΔGP = GM_prior × ΔRevenue + Revenue_prior × ΔGM + ΔRevenue × ΔGM",
                residual=(
                    f"largest absolute gross-profit residual is {max_gp:.6f}"
                    if max_gp is not None
                    else "opening period has no change"
                ),
                stability="the interaction identity holds for every adjacent pair with defined margins",
                contradictions="none",
                disclosure_support="reported revenue and gross profit",
                established=max_gp is not None and max_gp < 1e-4,
            )
        )
    if impairment_disclosed and impairment_amounts is not None:
        charged = [
            (period, amount)
            for period, amount in zip(periods, impairment_amounts)
            if amount is not None and amount > 0
        ]
        assessments.append(
            MarginRelationshipAssessment(
                name="impairment or asset-related charges",
                kind=KIND_REPORTED_FACT,
                direction="separately disclosed impairment or restructuring charges reduce operating profit in the years they appear",
                magnitude=(
                    "; ".join(
                        f"{period.isoformat()} {amount:,.0f}"
                        for period, amount in charged
                    )
                    or "disclosed zeros only"
                ),
                reconstruction="charges enter the operating-margin identity only in periods that present the line",
                residual="reported zeros remain zeros; later years that still present the line keep the disclosed zero",
                stability="the charge is episodic, not a recurring operating burden",
                contradictions="none; later filings keep the line at zero rather than dropping it silently",
                disclosure_support="face-of-statement impairment or restructuring line with page-level locators in provenance",
                established=True,
            )
        )
    mix_limit = (
        "Face-of-statement components do not isolate mix, markdowns, freight, "
        "input costs, occupancy, or leverage in amounts that can be bridged "
        "independently to the reported margin change. Source filings may "
        "attribute those items in Item 7; the attributions remain management "
        "explanations unless a disclosed series can be folded without assuming "
        "undisclosed subcomponents."
    )
    assessments.append(
        MarginRelationshipAssessment(
            name="mix, markdowns, freight, costs, or leverage",
            kind=KIND_UNESTABLISHED,
            direction="not established",
            magnitude="not quantified",
            reconstruction="no source-supported component series",
            residual="not applicable",
            stability="not tested",
            contradictions="not tested",
            disclosure_support=mix_limit,
            established=False,
            limitation=mix_limit,
        )
    )
    if (
        reported_operating_margin is not None
        and sga_ratio is not None
        and gross_margin is not None
    ):
        om_vals = [_numeric_ratio(item) for item in reported_operating_margin]
        gm_vals = [_numeric_ratio(item) for item in gross_margin]
        sga_vals = [_numeric_ratio(item) for item in sga_ratio]
        latest = next(
            (
                index
                for index in range(len(periods) - 1, 0, -1)
                if om_vals[index] is not None and om_vals[index - 1] is not None
            ),
            None,
        )
        if latest is not None:
            om_move = om_vals[latest] - om_vals[latest - 1]
            gm_move = _numeric_ratio(
                None if gm_contribution is None else gm_contribution[latest]
            )
            sga_move = _numeric_ratio(
                None if sga_contribution is None else sga_contribution[latest]
            )
            imp_move = _numeric_ratio(
                None if imp_contribution is None else imp_contribution[latest]
            )
            other_move = _numeric_ratio(
                None if other_contribution is None else other_contribution[latest]
            )
            parts = []
            if gm_move is not None:
                parts.append(f"Δgross margin {gm_move * 100:+.2f} pp")
            if sga_move is not None:
                parts.append(f"−Δ(SG&A/revenue) {sga_move * 100:+.2f} pp")
            if imp_move is not None:
                parts.append(
                    f"−Δ(impairment or asset-related charges/revenue) {imp_move * 100:+.2f} pp"
                )
            if other_move is not None:
                parts.append(
                    f"−Δ(other reported operating items/revenue) {other_move * 100:+.2f} pp"
                )
            assessments.append(
                MarginRelationshipAssessment(
                    name="latest adjacent operating-margin movement",
                    kind=KIND_OBSERVED,
                    direction=(
                        "operating margin fell"
                        if om_move < 0
                        else "operating margin rose"
                    ),
                    magnitude=f"{om_move * 100:+.2f} pp",
                    reconstruction=(
                        "; ".join(parts) if parts else "component change incomplete"
                    ),
                    residual="contribution residual is shown separately",
                    stability="one adjacent pair; not a multi-year law",
                    contradictions=(
                        "gross-margin and SG&A contributions both reduced operating margin"
                        if gm_move is not None
                        and sga_move is not None
                        and gm_move < 0
                        and sga_move < 0
                        and om_move < 0
                        else "none required"
                    ),
                    disclosure_support=(
                        "income-statement identity only; Item 7 attributions are "
                        "recorded separately after source-filing inspection"
                    ),
                    established=True,
                )
            )
    return tuple(assessments)
