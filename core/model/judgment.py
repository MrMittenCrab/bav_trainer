"""Company-specific guided accounting judgment cases (coordinate-free)."""

from __future__ import annotations

from dataclasses import dataclass

from ..data.interface import StandardizedFinancials
from ..data.line_identity import line_identity
from .classification import BalanceSheetReformulation

CONSEQUENCE_PROMPT = (
    "Explain which reformulated balance(s) and profitability/leverage interpretation "
    "change under the alternative treatment."
)


@dataclass(frozen=True)
class JudgmentCase:
    id: str
    order: int
    line_identity: str
    label: str
    topic: str
    supplied_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str


def _line_has_nonzero_value(item, periods) -> bool:
    for period in periods:
        value = item.values.get(period)
        if value is None:
            continue
        if float(value) != 0.0:
            return True
    return False


def classification_judgment_cases(
    financials: StandardizedFinancials,
    reformulation: BalanceSheetReformulation,
) -> tuple[JudgmentCase, ...]:
    """Derive guided classification cases from classifier-flagged ambiguous lines."""
    periods = [p.end_date for p in financials.periods]
    cases: list[JudgmentCase] = []
    order = 1
    for idx in reformulation.detail_indices:
        decision = reformulation.decisions[idx]
        if not decision.ambiguous:
            continue
        if len(decision.guided_options) < 2:
            continue
        item = financials.balance_sheet[idx]
        if not _line_has_nonzero_value(item, periods):
            continue
        identity = line_identity(item).key()
        alternatives = tuple(decision.guided_options[1:])
        cases.append(
            JudgmentCase(
                id=f"classification::{identity}",
                order=order,
                line_identity=identity,
                label=item.label,
                topic=decision.judgment_topic,
                supplied_treatment=decision.category,
                alternatives=alternatives,
                model_rationale=decision.reason,
                consequence_prompt=CONSEQUENCE_PROMPT,
                model_consequence=decision.consequence_note,
            )
        )
        order += 1
    return tuple(cases)
