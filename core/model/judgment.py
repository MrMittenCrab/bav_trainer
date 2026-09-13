"""Company-specific guided accounting judgment cases (coordinate-free)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from ..data.line_identity import line_identity
from .classification import BALANCE_SHEET_CATEGORIES, BalanceSheetReformulation

CONSEQUENCE_PROMPT = (
    "Explain which reformulated balance(s) change under the alternative treatment "
    "and how that changes profitability/leverage interpretation."
)


@dataclass(frozen=True)
class ClassificationJudgmentTemplate:
    topic: str
    options: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str


@dataclass(frozen=True)
class JudgmentCase:
    id: str
    order: int
    line_identity: str
    override_selector: str
    label: str
    topic: str
    supplied_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str


CLASSIFICATION_JUDGMENT_TEMPLATES: dict[str, ClassificationJudgmentTemplate] = {
    "lease_liability_operating_vs_financing": ClassificationJudgmentTemplate(
        topic="Lease liability operating vs financing",
        options=("Operating Long-Term Liability", "Financial Liability"),
        model_rationale=(
            "The reference model keeps the liability in operating long-term liabilities "
            "under its current lease convention. Treating it as a financial liability is "
            "also defensible when the lease obligation is viewed as debt-like financing."
        ),
        consequence_prompt=CONSEQUENCE_PROMPT,
        model_consequence=(
            "Operating-liability treatment lowers NOLA/NOA; financial-liability treatment "
            "raises Net Debt by the same balance. Implied equity is unchanged from this "
            "classification switch alone, but RNOA versus FLEV/Spread interpretation changes."
        ),
    ),
    "pension_obligation_operating_vs_financing": ClassificationJudgmentTemplate(
        topic="Pension obligation operating vs financing",
        options=("Operating Long-Term Liability", "Financial Liability"),
        model_rationale=(
            "The reference model keeps the obligation in operating long-term liabilities "
            "under its current employee-benefit convention. A financial-liability treatment "
            "is also defensible when the obligation is analyzed as debt-like funding."
        ),
        consequence_prompt=CONSEQUENCE_PROMPT,
        model_consequence=(
            "Operating-liability treatment lowers NOLA/NOA; financial-liability treatment "
            "raises Net Debt by the same balance. Implied equity is unchanged from this "
            "classification switch alone, but RNOA versus FLEV/Spread interpretation changes."
        ),
    ),
    "short_term_investment_financial_vs_operating": ClassificationJudgmentTemplate(
        topic="Short-term investment operating vs financing",
        options=("Financial Asset", "Operating Working Capital Asset"),
        model_rationale=(
            "The reference model treats a generic short-term investment as a financial asset "
            "absent evidence that it is required for operations. Operating-WC treatment "
            "requires company-specific evidence that the balance is necessary for normal "
            "operations."
        ),
        consequence_prompt=CONSEQUENCE_PROMPT,
        model_consequence=(
            "Financial-asset treatment lowers Net Debt; operating-WC treatment raises "
            "NOWC/NOA by the same balance. Implied equity is unchanged from this "
            "classification switch alone, but operating-capital and leverage metrics change."
        ),
    ),
    "associate_investment_operating_vs_financial": ClassificationJudgmentTemplate(
        topic="Equity-method investment operating vs financing",
        options=("Operating Long-Term Asset", "Financial Asset"),
        model_rationale=(
            "The reference model treats the investment as an operating long-term asset when "
            "it is viewed as strategically tied to the operating business. Financial-asset "
            "treatment is defensible when the holding is primarily non-operating/investment "
            "in nature."
        ),
        consequence_prompt=CONSEQUENCE_PROMPT,
        model_consequence=(
            "Operating-asset treatment raises NOLA/NOA; financial-asset treatment lowers "
            "Net Debt by the same balance. Implied equity is unchanged from this "
            "classification switch alone, but RNOA and leverage interpretation change."
        ),
    ),
}


def _line_has_nonzero_value(item, periods: list[date]) -> bool:
    for period in periods:
        value = item.values.get(period)
        if value is None:
            continue
        if float(value) != 0.0:
            return True
    return False


def classification_judgment_cases(
    financials: StandardizedFinancials,
    periods: list[date],
    reformulation: BalanceSheetReformulation,
) -> tuple[JudgmentCase, ...]:
    """Derive guided classification cases from supported ambiguous supplied lines."""
    cases: list[JudgmentCase] = []
    order = 1
    for idx in reformulation.detail_indices:
        decision = reformulation.decisions[idx]
        if not decision.ambiguous:
            continue
        if decision.overridden:
            continue
        if decision.judgment_code is None:
            continue
        template = CLASSIFICATION_JUDGMENT_TEMPLATES.get(decision.judgment_code)
        if template is None:
            raise ValueError(
                f"Unsupported judgment_code {decision.judgment_code!r} on "
                f"{financials.balance_sheet[idx].label!r}; add a registry template "
                f"or clear the code"
            )
        if template.options[0] != decision.category:
            raise ValueError(
                f"judgment template for {decision.judgment_code!r} expects category "
                f"{template.options[0]!r} but classifier returned {decision.category!r}"
            )
        for option in template.options:
            if option not in BALANCE_SHEET_CATEGORIES:
                raise ValueError(
                    f"judgment template option {option!r} is not a balance-sheet category"
                )
        item = financials.balance_sheet[idx]
        if not _line_has_nonzero_value(item, periods):
            continue
        ident = line_identity(item)
        identity = ident.key()
        override_selector = f"identity:{identity}"
        cases.append(
            JudgmentCase(
                id=f"classification::{identity}",
                order=order,
                line_identity=identity,
                override_selector=override_selector,
                label=item.label,
                topic=template.topic,
                supplied_treatment=decision.category,
                alternatives=tuple(template.options[1:]),
                model_rationale=template.model_rationale,
                consequence_prompt=template.consequence_prompt,
                model_consequence=template.model_consequence,
            )
        )
        order += 1
    return tuple(cases)
