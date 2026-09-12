"""Explicit recurring/non-recurring earnings normalization (Step 8B2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import LineItem, StandardizedFinancials
from ..data.line_identity import line_identity
from ..data.schema import normalize_label
from .financial_math import AnchorMetrics

NORMALIZATION_TREATMENTS = ("Recurring", "Non-recurring")
SUPPORTED_NORMALIZATION_SCOPE = "operating_pretax_effective_tax"

CONSEQUENCE_PROMPT = (
    "Explain why you would treat this item as recurring or non-recurring and how "
    "that treatment changes normalized earnings."
)


@dataclass(frozen=True)
class NormalizationCandidateSpec:
    selector: str
    reference_treatment: str
    scope: str
    topic: str
    reference_rationale: str
    consequence_note: str


@dataclass(frozen=True)
class NormalizationCase:
    id: str
    order: int
    line_identity: str
    override_selector: str
    label: str
    scope: str
    topic: str
    reference_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str


@dataclass(frozen=True)
class NormalizationSeries:
    pretax_adjustment: tuple[float, ...]
    after_tax_adjustment: tuple[float, ...]
    normalized_nopat: tuple[float, ...]
    normalized_net_income: tuple[float, ...]


def _label_match_key(label: str) -> str:
    s = normalize_label(label).lower()
    for ch in ("'", "'", "`"):
        s = s.replace(ch, "'")
    return " ".join(s.split())


def _parse_selector(key: str) -> tuple[str, str]:
    raw = key.strip()
    low = raw.lower()
    if low.startswith("concept:"):
        return "concept", normalize_label(raw.split(":", 1)[1])
    if low.startswith("label:"):
        return "label", _label_match_key(raw.split(":", 1)[1])
    return "label", _label_match_key(raw)


def resolve_income_statement_selector(
    financials: StandardizedFinancials,
    selector: str,
) -> LineItem:
    """Resolve a normalization selector to exactly one income-statement line."""
    kind, value = _parse_selector(selector)
    items = financials.income_statement
    if kind == "concept":
        matches = [item for item in items if line_identity(item).concept == value]
    else:
        matches = [
            item for item in items if _label_match_key(line_identity(item).label) == value
        ]
    if len(matches) == 0:
        raise ValueError(
            f"normalization candidate selector {selector!r} matched no income-statement line"
        )
    if len(matches) > 1:
        labels = [item.label for item in matches]
        raise ValueError(
            f"normalization candidate selector {selector!r} matched {len(matches)} "
            f"income-statement lines {labels}; use a unique concept:<id> selector"
        )
    return matches[0]


def _parse_candidate(raw: object, index: int) -> NormalizationCandidateSpec:
    if not isinstance(raw, dict):
        raise ValueError(f"normalizationCandidates[{index}] must be an object")
    required = (
        "selector",
        "referenceTreatment",
        "scope",
        "topic",
        "referenceRationale",
        "consequenceNote",
    )
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(
            f"normalizationCandidates[{index}] missing required fields: {missing}"
        )
    scope = str(raw["scope"])
    if scope != SUPPORTED_NORMALIZATION_SCOPE:
        raise ValueError(
            f"normalizationCandidates[{index}] unsupported scope {scope!r}; "
            f"only {SUPPORTED_NORMALIZATION_SCOPE!r} is supported"
        )
    treatment = str(raw["referenceTreatment"])
    if treatment not in NORMALIZATION_TREATMENTS:
        raise ValueError(
            f"normalizationCandidates[{index}] referenceTreatment must be one of "
            f"{list(NORMALIZATION_TREATMENTS)}, got {treatment!r}"
        )
    return NormalizationCandidateSpec(
        selector=str(raw["selector"]).strip(),
        reference_treatment=treatment,
        scope=scope,
        topic=str(raw["topic"]),
        reference_rationale=str(raw["referenceRationale"]),
        consequence_note=str(raw["consequenceNote"]),
    )


def _line_has_nonzero_value(item: LineItem, periods: list[date]) -> bool:
    for period in periods:
        value = item.values.get(period)
        if value is None:
            continue
        if float(value) != 0.0:
            return True
    return False


def _stable_override_selector(item: LineItem, supplied_selector: str) -> str:
    ident = line_identity(item)
    if ident.concept:
        return f"concept:{ident.concept}"
    # Preserve a label: prefix when supplied; otherwise use original label.
    kind, _ = _parse_selector(supplied_selector)
    if kind == "label" and supplied_selector.strip().lower().startswith("label:"):
        return f"label:{item.label}"
    return f"label:{item.label}"


def normalization_cases(
    financials: StandardizedFinancials,
    periods: list[date],
    assumptions: dict,
) -> tuple[NormalizationCase, ...]:
    """Derive normalization cases from explicitly supplied assumption candidates."""
    raw_candidates = assumptions.get("normalizationCandidates") or []
    if not isinstance(raw_candidates, list):
        raise ValueError("normalizationCandidates must be a list")

    staged: list[tuple[NormalizationCandidateSpec, LineItem]] = []
    for index, raw in enumerate(raw_candidates):
        spec = _parse_candidate(raw, index)
        item = resolve_income_statement_selector(financials, spec.selector)
        if not _line_has_nonzero_value(item, periods):
            continue
        staged.append((spec, item))

    cases: list[NormalizationCase] = []
    for order, (spec, item) in enumerate(staged, start=1):
        ident = line_identity(item)
        identity = ident.key()
        alternatives = tuple(
            treatment
            for treatment in NORMALIZATION_TREATMENTS
            if treatment != spec.reference_treatment
        )
        # Reference first, then the other allowed treatment.
        ordered_alts = (spec.reference_treatment,) + alternatives
        cases.append(
            NormalizationCase(
                id=f"normalization::{identity}",
                order=order,
                line_identity=identity,
                override_selector=_stable_override_selector(item, spec.selector),
                label=item.label,
                scope=spec.scope,
                topic=spec.topic,
                reference_treatment=spec.reference_treatment,
                alternatives=ordered_alts[1:],
                model_rationale=spec.reference_rationale,
                consequence_prompt=CONSEQUENCE_PROMPT,
                model_consequence=spec.consequence_note,
            )
        )
    return tuple(cases)


def _case_by_id(cases: tuple[NormalizationCase, ...]) -> dict[str, NormalizationCase]:
    return {case.id: case for case in cases}


def compute_normalization_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
    cases: tuple[NormalizationCase, ...],
    treatments: dict[str, str] | None = None,
) -> NormalizationSeries:
    """Compute the operating pretax effective-tax normalization bridge."""
    treatments = dict(treatments or {})
    known = _case_by_id(cases)
    for case_id in treatments:
        if case_id not in known:
            raise ValueError(f"Unknown normalization case id {case_id!r}")
    for case_id, treatment in treatments.items():
        if treatment not in NORMALIZATION_TREATMENTS:
            raise ValueError(
                f"Invalid normalization treatment {treatment!r} for case {case_id!r}"
            )
    for case in cases:
        if case.scope != SUPPORTED_NORMALIZATION_SCOPE:
            raise ValueError(f"Unsupported normalization scope {case.scope!r}")

    n = len(periods)
    hist = anchor.historical
    if not (
        len(hist.nopat) == n
        and len(hist.net_income) == n
        and len(hist.effective_tax_rate) == n
    ):
        raise ValueError(
            "normalization period axis must match AnchorMetrics historical series length"
        )

    # Resolve each case to its income-statement item once.
    items_by_case: dict[str, LineItem] = {}
    for case in cases:
        items_by_case[case.id] = resolve_income_statement_selector(
            financials, case.override_selector
        )

    pretax: list[float] = []
    after_tax: list[float] = []
    norm_nopat: list[float] = []
    norm_ni: list[float] = []
    for j, period in enumerate(periods):
        pretax_adj = 0.0
        for case in cases:
            treatment = treatments.get(case.id, case.reference_treatment)
            if treatment == "Recurring":
                continue
            reported = items_by_case[case.id].values.get(period)
            signed = 0.0 if reported is None else float(reported)
            pretax_adj += -signed
        etr = float(hist.effective_tax_rate[j] or 0.0)
        after = pretax_adj * (1.0 - etr)
        pretax.append(pretax_adj)
        after_tax.append(after)
        norm_nopat.append(float(hist.nopat[j]) + after)
        norm_ni.append(float(hist.net_income[j]) + after)

    return NormalizationSeries(
        pretax_adjustment=tuple(pretax),
        after_tax_adjustment=tuple(after_tax),
        normalized_nopat=tuple(norm_nopat),
        normalized_net_income=tuple(norm_ni),
    )


def zero_normalization_series(n: int) -> NormalizationSeries:
    zeros = tuple(0.0 for _ in range(n))
    return NormalizationSeries(
        pretax_adjustment=zeros,
        after_tax_adjustment=zeros,
        normalized_nopat=zeros,
        normalized_net_income=zeros,
    )
