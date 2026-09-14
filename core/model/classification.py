"""BAVGEM Stage-3 balance-sheet classification and reformulation.

Single authority for Python expected values and Excel Condensed Financials.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from ..data.interface import LineItem, StandardizedFinancials
from ..data.line_identity import LineIdentity, line_identity
from ..data.schema import normalize_label
from .line_resolver import resolve_line
from .source_values import required_period_value

BALANCE_SHEET_CATEGORIES = (
    "Operating Working Capital Asset",
    "Operating Working Capital Liability",
    "Operating Long-Term Asset",
    "Operating Long-Term Liability",
    "Financial Asset",
    "Financial Liability",
    "Equity",
    "Exclude",
)

DEFAULT_TOLERANCE = 1.0

_ASSET_REFORMULATION_CATEGORIES = frozenset(
    {
        "Operating Working Capital Asset",
        "Operating Long-Term Asset",
        "Financial Asset",
    }
)

_LIABILITY_REFORMULATION_CATEGORIES = frozenset(
    {
        "Operating Working Capital Liability",
        "Operating Long-Term Liability",
        "Financial Liability",
    }
)


class ClassificationError(ValueError):
    """Base classification/reformulation error."""


class UnclassifiedBalanceSheetLineError(ClassificationError):
    """A non-subtotal line cannot be safely classified without an override."""


class InvalidClassificationOverrideError(ClassificationError):
    """Override value is not one of the eight BAVGEM categories."""


class ReformulationIntegrityError(ClassificationError):
    """Classified detail does not reconcile to reported totals."""


class AmbiguousClassificationOverrideError(ClassificationError):
    """Override selector matches zero or multiple detail rows unsafely."""


@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False
    judgment_code: str | None = None


@dataclass(frozen=True)
class BalanceSheetReformulation:
    decisions: dict[int, ClassificationDecision]
    category_totals: dict[str, tuple[float, ...]]
    nowc: tuple[float, ...]
    nola: tuple[float, ...]
    noa: tuple[float, ...]
    net_debt: tuple[float, ...]
    implied_equity: tuple[float, ...]
    reported_equity: tuple[float | None, ...]
    total_assets: tuple[float | None, ...]
    total_liabilities: tuple[float | None, ...]
    asset_detail_gap: tuple[float | None, ...]
    liability_detail_gap: tuple[float | None, ...]
    equity_gap: tuple[float | None, ...]
    detail_indices: tuple[int, ...] = ()


def _norm(label: str) -> str:
    s = normalize_label(label).lower()
    for ch in ("\u2018", "\u2019", "`", "´"):
        s = s.replace(ch, "'")
    return " ".join(s.split())


def is_balance_sheet_subtotal(item: LineItem) -> bool:
    low = _norm(item.label)
    if low.startswith("total "):
        return True
    if low in {"total assets", "total liabilities", "total equity"}:
        return True
    if "total assets" in low or "total liabilities" in low:
        return True
    if low.startswith("total equity") or low == "total shareholders equity":
        return True
    return False


def _match_any(low: str, needles: Iterable[str]) -> bool:
    return any(n in low for n in needles)


def _concept_token(concept: str) -> str:
    """Lowercase concept with separators removed for coarse side/category signals."""
    return "".join(ch for ch in normalize_label(concept).lower() if ch.isalnum())


def _classify_by_concept(item: LineItem) -> ClassificationDecision | None:
    """High-priority concept signals only when the concept clearly encodes side/nature.

    Generic substrings such as ``debt``, ``equity``, or ``cash`` alone are not
    decisive — they appear in asset, liability, and equity-component concepts.
    """
    if not (item.concept or "").strip():
        return None
    c = _concept_token(item.concept)

    if "deferred" in c and "tax" in c:
        if "asset" in c:
            return ClassificationDecision(
                "Operating Long-Term Asset",
                ambiguous=True,
                reason="Deferred tax asset concept — operating vs exclude judgment",
            )
        if "liab" in c:
            return ClassificationDecision(
                "Operating Long-Term Liability",
                ambiguous=True,
                reason="Deferred tax liability concept — operating vs exclude judgment",
            )

    if ("lease" in c or "rightofuse" in c or c.startswith("rou")) and "liab" not in c:
        if "asset" in c or "rightofuse" in c or "rou" in c:
            return ClassificationDecision(
                "Operating Long-Term Asset",
                ambiguous=True,
                reason="Lease/ROU asset concept — operating vs financial judgment",
            )
    if "lease" in c and "liab" in c:
        return ClassificationDecision(
            "Operating Long-Term Liability",
            ambiguous=True,
            reason="Lease liability concept — operating vs financial judgment",
            judgment_code="lease_liability_operating_vs_financing",
        )

    if "equitymethod" in c or (
        ("associate" in c or "jointventure" in c) and "investment" in c
    ):
        return ClassificationDecision(
            "Operating Long-Term Asset",
            ambiguous=True,
            reason="Equity-method investment concept — operating vs financial judgment",
            judgment_code="associate_investment_operating_vs_financial",
        )

    # Unmistakable borrowing / debt *liability* concepts (not debt securities).
    if _match_any(
        c,
        (
            "bankborrow",
            "borrowings",
            "longtermdebt",
            "shorttermdebt",
            "notespayable",
            "bondspayable",
            "loanpayable",
            "loanspayable",
            "commercialpaper",
        ),
    ):
        return ClassificationDecision("Financial Liability")

    # Unmistakable cash / marketable-security *asset* holdings (not cash-flow hedges).
    if _match_any(
        c,
        (
            "cashandcashequivalent",
            "cashequivalent",
            "cashonhand",
            "marketablesecurit",
            "tradingsecurit",
            "moneymarket",
        ),
    ) or c in {"cash", "cashandcashequivalents"}:
        return ClassificationDecision("Financial Asset")

    # Unmistakable equity-component concepts (not equity-method investments).
    # Do not use a generic "commonstock" substring: redeemable / mandatorily
    # redeemable common stock can be liability-like and must follow label rules.
    if _match_any(
        c,
        (
            "retainedearnings",
            "sharecapital",
            "additionalpaid",
            "treasurystock",
            "treasuryshare",
            "accumulatedothercomprehensive",
            "aoci",
        ),
    ) or (
        "othercomprehensive" in c
        and "method" not in c
        and "investment" not in c
    ):
        return ClassificationDecision("Equity")

    return (
        _generic_financial_concept_decision(item)
        or _generic_other_balance_concept_decision(item)
        or _deterministic_accounting_concept_decision(item)
        or _customer_prepayment_liability_decision(item)
        or _ppe_balance_decision(item)
        or _common_stock_balance_decision(item)
    )


# Exact concept tokens for customer-prepayment / deferred-revenue liability balances.
# Movement, asset, and unbound substrings are intentionally excluded.
_CUSTOMER_PREPAYMENT_LIABILITY_CONCEPTS = frozenset(
    {
        "unredeemedgiftcardliability",
        "giftcardliability",
        "giftcardsliability",
        "giftcardliabilities",
        "giftcardsliabilities",
        "unearnedrevenue",
        "unearnedrevenueliability",
        "deferredrevenue",
        "deferredrevenues",
        "deferredrevenueliability",
        "contractliability",
        "contractliabilities",
        "currentdeferredrevenue",
        "currentdeferredrevenueliability",
        "noncurrentdeferredrevenue",
        "noncurrentdeferredrevenueliability",
        "longtermdeferredrevenue",
        "longtermdeferredrevenueliability",
        "currentcontractliability",
        "currentcontractliabilities",
        "noncurrentcontractliability",
        "noncurrentcontractliabilities",
        "longtermcontractliability",
        "longtermcontractliabilities",
        "currentunearnedrevenue",
        "currentunearnedrevenueliability",
        "noncurrentunearnedrevenue",
        "noncurrentunearnedrevenueliability",
        "currentgiftcardliability",
        "noncurrentgiftcardliability",
        "currentgiftcardliabilities",
        "noncurrentgiftcardliabilities",
        "currentunredeemedgiftcardliability",
        "noncurrentunredeemedgiftcardliability",
    }
)

_CUSTOMER_PREPAYMENT_LABEL_PHRASES = (
    "gift card liability",
    "gift-card liability",
    "gift cards liability",
    "gift-cards liability",
    "gift card liabilities",
    "gift-card liabilities",
    "gift cards liabilities",
    "gift-cards liabilities",
    "unredeemed gift card",
    "unredeemed gift-card",
    "unearned revenue",
    "deferred revenue",
    "contract liability",
    "contract liabilities",
)

_CUSTOMER_PREPAYMENT_MOVEMENT_CONCEPT_MARKERS = (
    "changein",
    "derecognition",
    "increasein",
    "decreasein",
    "amortizationof",
    "recognitionof",
    "additionsto",
    "reductionsin",
)

_CUSTOMER_PREPAYMENT_MOVEMENT_LABEL_MARKERS = (
    "derecognition",
    "recognition of",
    "change in",
    "increase in",
    "decrease in",
    "amortization of",
    "additions to",
    "reductions in",
)

# Stems that identify prepayment-related concepts even when wrapped in movement
# prefixes (e.g. change_in_deferred_revenue) or non-alias tokens.
_CUSTOMER_PREPAYMENT_CONCEPT_STEMS = (
    "unredeemedgiftcard",
    "giftcardliab",
    "giftcardsliab",
    "unearnedrevenue",
    "deferredrevenue",
    "contractliab",
)


def _customer_prepayment_has_movement(concept_token: str, low: str) -> bool:
    """True when concept or label uses a bounded movement/derecognition marker."""
    if concept_token and any(
        marker in concept_token for marker in _CUSTOMER_PREPAYMENT_MOVEMENT_CONCEPT_MARKERS
    ):
        return True
    return any(marker in low for marker in _CUSTOMER_PREPAYMENT_MOVEMENT_LABEL_MARKERS)


def _customer_prepayment_content(concept_token: str, low: str) -> bool:
    """True when concept or label identifies a customer-prepayment liability topic."""
    if any(phrase in low for phrase in _CUSTOMER_PREPAYMENT_LABEL_PHRASES):
        return True
    if concept_token in _CUSTOMER_PREPAYMENT_LIABILITY_CONCEPTS:
        return True
    if concept_token and any(
        stem in concept_token for stem in _CUSTOMER_PREPAYMENT_CONCEPT_STEMS
    ):
        return True
    return False


def _is_customer_prepayment_movement(concept_token: str, low: str) -> bool:
    """Movement rows for prepayment topics must fail closed (no liability fallback)."""
    return _customer_prepayment_has_movement(concept_token, low) and (
        _customer_prepayment_content(concept_token, low)
    )


def _customer_prepayment_label_hit(low: str) -> bool:
    """True when the label uses explicit prepayment-liability wording."""
    if any(marker in low for marker in _CUSTOMER_PREPAYMENT_MOVEMENT_LABEL_MARKERS):
        return False
    if "asset" in low or "receivable" in low:
        return False
    return any(phrase in low for phrase in _CUSTOMER_PREPAYMENT_LABEL_PHRASES)


def _customer_prepayment_excluded(concept_token: str, low: str) -> bool:
    """Reject movement/derecognition concepts and contradictory asset wording."""
    if _customer_prepayment_has_movement(concept_token, low):
        return True
    if "asset" in concept_token and "liab" not in concept_token:
        return True
    if "receivable" in concept_token:
        return True
    if "asset" in low or "receivable" in low:
        return True
    return False


def _explicitly_noncurrent_prepayment(concept_token: str, low: str) -> bool:
    """Noncurrent / long-term markers win over unqualified WC default."""
    if any(tok in concept_token for tok in ("noncurrent", "longterm")):
        return True
    if any(
        tok in low
        for tok in ("non-current", "noncurrent", "long-term", "long term")
    ):
        return True
    return False


def _customer_prepayment_liability_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    """Classify explicit gift-card / unearned / deferred-revenue / contract liabilities.

    Deterministic operating liability; no guided-judgment case. Unqualified balances
    default to working capital; explicitly noncurrent variants are long-term.
    Movement rows are rejected here and must already have failed closed upstream.
    """
    concept_token = _concept_token(item.concept or "")
    low = _norm(item.label)

    if _customer_prepayment_excluded(concept_token, low):
        return None

    concept_hit = concept_token in _CUSTOMER_PREPAYMENT_LIABILITY_CONCEPTS
    label_hit = _customer_prepayment_label_hit(low)

    # Exact concept aliases require compatible liability wording; label-only
    # wording remains supported for unqualified deferred-revenue presentations.
    if concept_hit and not label_hit:
        return None
    if not concept_hit and not label_hit:
        return None

    category = (
        "Operating Long-Term Liability"
        if _explicitly_noncurrent_prepayment(concept_token, low)
        else "Operating Working Capital Liability"
    )
    return ClassificationDecision(
        category,
        ambiguous=False,
        reason="Customer prepayment / deferred-revenue liability",
    )


# Exact concept tokens for net property-and-equipment balance rows only.
# Movement, purchase, proceeds, depreciation, and impairment concepts are excluded.
_PPE_BALANCE_CONCEPTS = frozenset(
    {
        "propertyplantequipment",
        "propertyplantandequipment",
    }
)

# Whole-label identity keys after punctuation folding (& → and, other punct → space).
_PPE_BALANCE_LABELS = frozenset(
    {
        "property and equipment",
        "property and equipment net",
        "net property and equipment",
        "property plant and equipment",
        "property plant and equipment net",
        "net property plant and equipment",
    }
)

# Topic phrases used only to gate movement fail-closed (substring OK here).
# Stored as punctuation-folded keys so comma / Oxford-comma / ampersand /
# whitespace variants share one vocabulary with `_ppe_label_key`.
_PPE_CONTENT_LABEL_PHRASES = (
    "property and equipment",
    "property plant and equipment",
    "plant and equipment",
)

_PPE_MOVEMENT_CONCEPT_MARKERS = (
    "purchase",
    "purchases",
    "proceed",
    "proceeds",
    "depreciation",
    "impairment",
    "addition",
    "additions",
    "disposal",
    "disposals",
    "payment",
    "payments",
    "saleof",
    "salesof",
    "sale",
    "sales",
    "changein",
    "changesin",
    "change",
    "changes",
    "increasein",
    "decreasein",
)

# Position-independent markers (leading or trailing singular/plural forms).
_PPE_MOVEMENT_LABEL_MARKERS = (
    "purchase",
    "purchases",
    "proceeds",
    "depreciation",
    "impairment",
    "addition",
    "additions",
    "disposal",
    "disposals",
    "payment",
    "payments",
    "sale of",
    "sales of",
    "sale",
    "sales",
    "change in",
    "changes in",
    "change",
    "changes",
    "increase in",
    "decrease in",
)


def _ppe_label_key(low: str) -> str:
    """Fold punctuation so whole-label PPE identity ignores commas/ampersands."""
    s = low.replace("&", " and ")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return " ".join(s.split())


def _ppe_has_movement(concept_token: str, low: str) -> bool:
    """True when concept or label uses a PPE movement / activity marker."""
    if concept_token and any(
        marker in concept_token for marker in _PPE_MOVEMENT_CONCEPT_MARKERS
    ):
        return True
    return any(marker in low for marker in _PPE_MOVEMENT_LABEL_MARKERS)


def _ppe_content(concept_token: str, low: str) -> bool:
    """True when concept or label identifies a PPE topic (balance or movement).

    Label topic detection uses `_ppe_label_key` so punctuation variants
    (commas, Oxford commas, ampersands, extra whitespace) share identity with
    the phrase vocabulary. This is substring topic matching only — whole-label
    balance recognition remains separate in `_ppe_balance_label_hit`.
    """
    if concept_token in _PPE_BALANCE_CONCEPTS:
        return True
    if concept_token and (
        "propertyplant" in concept_token
        or "propertyandequipment" in concept_token
        or "plantequipment" in concept_token
        or concept_token == "ppe"
        or concept_token.startswith("ppe")
        or concept_token.endswith("ppe")
    ):
        return True
    key = _ppe_label_key(low)
    if any(phrase in key for phrase in _PPE_CONTENT_LABEL_PHRASES):
        return True
    if key == "ppe" or re.search(r"\bppe\b", key):
        return True
    return False


def _is_ppe_movement(concept_token: str, low: str) -> bool:
    """PPE movement rows must fail closed (no legacy plant/PPE asset fallback)."""
    return _ppe_has_movement(concept_token, low) and _ppe_content(concept_token, low)


def _ppe_balance_label_hit(low: str) -> bool:
    """True when the entire label is a supported PPE net-balance identity."""
    if _ppe_has_movement("", low):
        return False
    return _ppe_label_key(low) in _PPE_BALANCE_LABELS


def _ppe_balance_decision(item: LineItem) -> ClassificationDecision | None:
    """Classify generic net PPE balances as operating long-term assets.

    Deterministic; no guided-judgment case. Exact balance concepts and
    whole-label balance identities are supported. Movement rows are rejected
    here so the matcher cannot admit purchases, proceeds, depreciation,
    impairment, or trailing addition/disposal/payment/sale/change variants.
    """
    concept_token = _concept_token(item.concept or "")
    low = _norm(item.label)

    if _ppe_has_movement(concept_token, low):
        return None

    concept_hit = concept_token in _PPE_BALANCE_CONCEPTS
    label_hit = _ppe_balance_label_hit(low)
    if not concept_hit and not label_hit:
        return None

    return ClassificationDecision(
        "Operating Long-Term Asset",
        ambiguous=False,
        reason="Property and equipment net balance",
    )


# Exact concept token for ordinary common-stock equity balances only.
# Redeemable, preferred, investment, and movement concepts are excluded.
_COMMON_STOCK_BALANCE_CONCEPTS = frozenset(
    {
        "commonstock",
    }
)

# Whole-label identity after normalize/case fold (no unrestricted substring).
_COMMON_STOCK_BALANCE_LABELS = frozenset(
    {
        "common stock",
    }
)

# Redeemable / preferred / investment instruments — not ordinary common stock.
_COMMON_STOCK_INSTRUMENT_CONCEPT_MARKERS = (
    "redeem",
    "redemption",
    "mandatory",
    "preferred",
    "preference",
    "investment",
)

_COMMON_STOCK_INSTRUMENT_LABEL_MARKERS = (
    "redeem",
    "redemption",
    "mandatory",
    "preferred",
    "preference",
    "investment",
)

# Issuance / repurchase / payment / purchase / sale / change movements.
# Concept payment detection is payment-sensitive (see
# ``_common_stock_concept_has_payment``) so paid-in-capital balances survive.
# Label payment phrases are matched on punctuation-folded keys.
_COMMON_STOCK_MOVEMENT_CONCEPT_MARKERS = (
    "issuance",
    "issue",
    "proceed",
    "proceeds",
    "repurchase",
    "payment",
    "payments",
    "purchase",
    "purchases",
    "saleof",
    "salesof",
    "changein",
    "increasein",
    "decreasein",
)

# Payment stems that remain movements even when paid-in-capital wording co-occurs.
_COMMON_STOCK_PAYMENT_CONCEPT_STEMS = (
    "cashpaid",
    "paidfor",
)

_COMMON_STOCK_MOVEMENT_LABEL_MARKERS = (
    "issuance",
    "issue of",
    "issued",
    "proceeds",
    "repurchase",
    "payment",
    "payments",
    "paid for",
    "cash paid",
    "purchase",
    "sale of",
    "sales of",
    "change in",
    "increase in",
    "decrease in",
)

# Liability wording that contradicts ordinary common-stock equity recognition.
# Label-side accrued / pension / retirement / post-employment evidence must fall
# through to supported liability rules. Concept-side accrued-expense / pension /
# retirement-benefit / post-employment identities contradict ordinary Common stock
# balances and must fail closed (no Equity override).
_COMMON_STOCK_LIABILITY_LABEL_MARKERS = (
    "liab",
    "payable",
    "bank borrow",
    "borrowing",
    "long-term debt",
    "long term debt",
    "notes payable",
    "commercial paper",
    "bonds payable",
    "loan payable",
    "accrued",
    "pension",
    "retirement benefit",
    "post-employment",
    "post employment",
)

_COMMON_STOCK_LIABILITY_CONCEPT_MARKERS = (
    "liab",
    "payable",
    "borrow",
    "bond",
    "loan",
    "debt",
    "commercialpaper",
    "accrued",
    "pension",
    "retirementbenefit",
    "postemployment",
)


def _common_stock_label_key(low: str) -> str:
    """Fold punctuation so common-stock topic/payment phrases ignore hyphens/dashes."""
    s = low.replace("&", " and ")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return " ".join(s.split())


def _common_stock_concept_has_payment(concept_token: str) -> bool:
    """True for payment-sensitive concept stems; preserves paid-in-capital balances.

    Genuine payment stems (``cashpaid``, ``paidfor``) remain movements even when
    paid-in-capital wording co-occurs. ``paidincapital`` exempts only that
    balance phrase itself — stripping it must not suppress separate payment
    wording (e.g. ``paidincash``) elsewhere in the normalized concept. Bare
    ``paidin`` alone (e.g. ``paid_in_cash``) is still payment-sensitive.
    """
    if not concept_token:
        return False
    if any(stem in concept_token for stem in _COMMON_STOCK_PAYMENT_CONCEPT_STEMS):
        return True
    # Exempt only the paid-in-capital balance phrase; residual ``paid`` is payment.
    remainder = concept_token.replace("paidincapital", "")
    if "paid" in remainder:
        return True
    return False


def _common_stock_has_movement(concept_token: str, low: str) -> bool:
    """True when concept or label uses a common-stock movement / activity marker."""
    if concept_token and (
        any(
            marker in concept_token for marker in _COMMON_STOCK_MOVEMENT_CONCEPT_MARKERS
        )
        or _common_stock_concept_has_payment(concept_token)
    ):
        return True
    key = _common_stock_label_key(low)
    return any(marker in key for marker in _COMMON_STOCK_MOVEMENT_LABEL_MARKERS)


def _common_stock_content(concept_token: str, low: str) -> bool:
    """True when concept or label identifies a common-stock topic."""
    if concept_token in _COMMON_STOCK_BALANCE_CONCEPTS:
        return True
    if concept_token and "commonstock" in concept_token:
        return True
    return "common stock" in _common_stock_label_key(low)


def _is_common_stock_movement(concept_token: str, low: str) -> bool:
    """Common-stock movements must fail closed (no cash/liability/equity fallback)."""
    return _common_stock_has_movement(concept_token, low) and _common_stock_content(
        concept_token, low
    )


def _common_stock_instrument_excluded(concept_token: str, low: str) -> bool:
    """Reject redeemable / preferred / investment common-stock instruments."""
    if concept_token and any(
        marker in concept_token for marker in _COMMON_STOCK_INSTRUMENT_CONCEPT_MARKERS
    ):
        return True
    key = _common_stock_label_key(low)
    return any(marker in key for marker in _COMMON_STOCK_INSTRUMENT_LABEL_MARKERS)


def _common_stock_label_has_liability(low: str) -> bool:
    """True when the label uses liability / debt / payable wording."""
    key = _common_stock_label_key(low)
    if any(marker in key for marker in _COMMON_STOCK_LIABILITY_LABEL_MARKERS):
        return True
    return key.endswith(" debt") or " debt " in f" {key} "


def _common_stock_concept_has_liability(concept_token: str) -> bool:
    """True when the concept encodes liability / debt / payable identity."""
    if not concept_token:
        return False
    return any(
        marker in concept_token for marker in _COMMON_STOCK_LIABILITY_CONCEPT_MARKERS
    )


def _common_stock_has_liability_contradiction(concept_token: str, low: str) -> bool:
    """Liability wording on either field blocks ordinary common-stock equity."""
    return _common_stock_label_has_liability(low) or _common_stock_concept_has_liability(
        concept_token
    )


def _common_stock_excluded(concept_token: str, low: str) -> bool:
    """Reject instrument, movement, or liability-contradiction common-stock rows."""
    if _common_stock_instrument_excluded(concept_token, low):
        return True
    if _common_stock_has_movement(concept_token, low):
        return True
    return _common_stock_has_liability_contradiction(concept_token, low)


def _common_stock_balance_label_hit(low: str) -> bool:
    """True when the entire label is ordinary common-stock balance identity."""
    if _common_stock_instrument_excluded("", low):
        return False
    if _common_stock_has_movement("", low):
        return False
    if _common_stock_label_has_liability(low):
        return False
    return _common_stock_label_key(low) in _COMMON_STOCK_BALANCE_LABELS


def _common_stock_balance_decision(item: LineItem) -> ClassificationDecision | None:
    """Classify ordinary common-stock balances as Equity.

    Deterministic; no guided-judgment case. Exact ``common_stock`` concepts and
    whole-label ``Common stock`` identities are supported. Redeemable,
    preferred, investment, issuance/repurchase/payment movements, and
    contradictory liability pairings are rejected so neither recognition route
    can bypass the guards. Supported accrued / pension liability evidence and
    paid-in-capital balances are preserved.
    """
    concept_token = _concept_token(item.concept or "")
    low = _norm(item.label)

    if _common_stock_excluded(concept_token, low):
        return None

    concept_hit = concept_token in _COMMON_STOCK_BALANCE_CONCEPTS
    label_hit = _common_stock_balance_label_hit(low)
    if not concept_hit and not label_hit:
        return None

    return ClassificationDecision(
        "Equity",
        ambiguous=False,
        reason="Ordinary common-stock equity balance",
    )


def _generic_financial_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    # Concept is authoritative for nature/side/currentness; label is only a gate
    # that this is genuinely a generic financial/derivative presentation row.
    if "financial" not in c:
        return None
    if not _match_any(
        low,
        (
            "financial asset",
            "financial liab",
            "derivative financial",
        ),
    ):
        return None

    if "noncurrent" in c:
        horizon = "noncurrent"
    elif "current" in c:
        horizon = "current"
    else:
        return None

    if "asset" in c and "liab" not in c:
        code = (
            "financial_asset_noncurrent_financial_vs_operating"
            if horizon == "noncurrent"
            else "financial_asset_current_financial_vs_operating"
        )
        return ClassificationDecision(
            "Financial Asset",
            ambiguous=True,
            reason=(
                "Generic financial-asset concept — financial vs operating "
                "purpose/hedging judgment"
            ),
            judgment_code=code,
        )

    if "liab" in c:
        code = (
            "financial_liability_noncurrent_financial_vs_operating"
            if horizon == "noncurrent"
            else "financial_liability_current_financial_vs_operating"
        )
        return ClassificationDecision(
            "Financial Liability",
            ambiguous=True,
            reason=(
                "Generic financial-liability concept — financial vs operating "
                "purpose/hedging judgment"
            ),
            judgment_code=code,
        )

    return None


def _generic_other_balance_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    mapping = {
        "othercurrentassets": (
            "asset",
            "Operating Working Capital Asset",
            "other_current_asset_operating_vs_financial",
        ),
        "othernoncurrentassets": (
            "asset",
            "Operating Long-Term Asset",
            "other_noncurrent_asset_operating_vs_financial",
        ),
        "othercurrentliabilities": (
            "liability",
            "Operating Working Capital Liability",
            "other_current_liability_operating_vs_financial",
        ),
        "othernoncurrentliabilities": (
            "liability",
            "Operating Long-Term Liability",
            "other_noncurrent_liability_operating_vs_financial",
        ),
    }
    spec = mapping.get(c)
    if spec is None:
        return None

    side, category, judgment_code = spec
    if side == "asset":
        if "other" not in low or "asset" not in low or "liab" in low:
            return None
    else:
        if "other" not in low or "liabil" not in low:
            return None

    return ClassificationDecision(
        category,
        ambiguous=True,
        reason=(
            "Explicit residual balance-sheet concept identifies side/horizon but "
            "not economic nature — operating vs financial judgment"
        ),
        judgment_code=judgment_code,
    )


def _deterministic_accounting_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    mapping: dict[str, tuple[str, tuple[str, ...]]] = {
        "currenttaxliabilities": (
            "Operating Working Capital Liability",
            ("tax", "liab"),
        ),
        "provisionscurrent": (
            "Operating Working Capital Liability",
            ("provision",),
        ),
        "provisionsnoncurrent": (
            "Operating Long-Term Liability",
            ("provision",),
        ),
        "capitalstock": (
            "Equity",
            ("capital stock",),
        ),
        "capitalsurplus": (
            "Equity",
            ("capital surplus",),
        ),
        "othercomponentsofequity": (
            "Equity",
            ("component", "equity"),
        ),
        "noncontrollinginterests": (
            "Equity",
            ("interest",),
        ),
    }
    spec = mapping.get(c)
    if spec is None:
        return None
    category, required_tokens = spec
    if not all(token in low for token in required_tokens):
        return None
    if c == "noncontrollinginterests":
        if not ("non-controlling" in low or "noncontrolling" in low):
            return None
    return ClassificationDecision(
        category,
        ambiguous=False,
        reason="Exact standardized accounting concept",
    )


def _label_match_key(label: str) -> str:
    """Case-insensitive label key for unique label: / bare override selectors."""
    return _norm(label)


def _parse_override_selector(key: str) -> tuple[str, str]:
    """Return (kind, value) where kind is identity|concept|label."""
    raw = key.strip()
    low = raw.lower()
    if low.startswith("identity:"):
        return "identity", raw.split(":", 1)[1].strip()
    if low.startswith("concept:"):
        return "concept", normalize_label(raw.split(":", 1)[1])
    if low.startswith("label:"):
        return "label", _label_match_key(raw.split(":", 1)[1])
    return "label", _label_match_key(raw)


def resolve_classification_overrides(
    detail_items: list[LineItem],
    overrides: dict[str, str],
) -> dict[LineIdentity, str]:
    """Map detail-line identities to override categories; reject ambiguous selectors."""
    resolved: dict[LineIdentity, str] = {}
    for key, category in overrides.items():
        if category not in BALANCE_SHEET_CATEGORIES:
            raise InvalidClassificationOverrideError(
                f"Invalid classification override {category!r} for selector {key!r}"
            )
        kind, value = _parse_override_selector(key)
        if kind == "identity":
            matches = [
                item
                for item in detail_items
                if line_identity(item).key() == value
            ]
            if len(matches) == 0:
                continue
            if len(matches) > 1:
                raise AmbiguousClassificationOverrideError(
                    f"identity:{value!r} matches {len(matches)} detail rows; "
                    f"duplicate full identities are not allowed"
                )
            resolved[line_identity(matches[0])] = category
            continue
        if kind == "concept":
            matches = [
                i
                for i in detail_items
                if line_identity(i).concept == value
            ]
            if len(matches) == 0:
                continue
            if len(matches) > 1:
                raise AmbiguousClassificationOverrideError(
                    f"concept:{value!r} matches {len(matches)} detail rows; "
                    f"use a more specific concept or disambiguate source rows"
                )
            resolved[line_identity(matches[0])] = category
            continue

        # label: or bare legacy label — case-insensitive, unique among detail rows
        matches = [
            i for i in detail_items if _label_match_key(line_identity(i).label) == value
        ]
        if len(matches) == 0:
            continue
        if len(matches) > 1:
            concepts = [line_identity(i).concept or "(none)" for i in matches]
            raise AmbiguousClassificationOverrideError(
                f"label:{value!r} matches {len(matches)} detail rows with concepts "
                f"{concepts}; use concept:<id> selectors instead"
            )
        resolved[line_identity(matches[0])] = category
    return resolved


def classify_balance_sheet_line(
    item: LineItem,
    *,
    override: str | None = None,
) -> ClassificationDecision:
    """Return one of the eight BAVGEM categories for a non-subtotal BS line."""
    if override is not None:
        if override not in BALANCE_SHEET_CATEGORIES:
            raise InvalidClassificationOverrideError(
                f"Invalid classification override {override!r} for {item.label!r}"
            )
        return ClassificationDecision(
            category=override,
            ambiguous=False,
            reason="User override",
            overridden=True,
        )

    concept_token = _concept_token(item.concept or "")
    low = _norm(item.label)

    # Prepayment movements must fail closed before liability label fallbacks.
    if _is_customer_prepayment_movement(concept_token, low):
        raise UnclassifiedBalanceSheetLineError(
            f"Cannot safely classify balance-sheet line {item.label!r}; "
            f"provide classificationOverrides[{item.label!r}]"
        )

    # PPE movements must fail closed before legacy plant/PPE asset matching.
    if _is_ppe_movement(concept_token, low):
        raise UnclassifiedBalanceSheetLineError(
            f"Cannot safely classify balance-sheet line {item.label!r}; "
            f"provide classificationOverrides[{item.label!r}]"
        )

    # Common-stock movements must fail closed before cash/liability/equity fallbacks.
    if _is_common_stock_movement(concept_token, low):
        raise UnclassifiedBalanceSheetLineError(
            f"Cannot safely classify balance-sheet line {item.label!r}; "
            f"provide classificationOverrides[{item.label!r}]"
        )

    by_concept = _classify_by_concept(item)
    if by_concept is not None:
        return by_concept

    # Label-only customer prepayments (empty / non-alias concepts).
    prepayment = _customer_prepayment_liability_decision(item)
    if prepayment is not None:
        return prepayment

    # Label-only generic PPE net balances (empty / non-alias concepts).
    ppe = _ppe_balance_decision(item)
    if ppe is not None:
        return ppe

    # Label-only ordinary common-stock balances (empty / non-alias concepts).
    common_stock = _common_stock_balance_decision(item)
    if common_stock is not None:
        return common_stock

    # Ambiguous judgment calls — real default + flag
    if (
        _match_any(
            low,
            (
                "right of use",
                "right-of-use",
                "rou asset",
                "operating lease asset",
                "operating lease",
            ),
        )
        and "liab" not in low
    ):
        return ClassificationDecision(
            "Operating Long-Term Asset",
            ambiguous=True,
            reason="Operating lease ROU — operating vs financial judgment",
        )
    if _match_any(low, ("lease liability", "lease liabilities", "operating lease")):
        return ClassificationDecision(
            "Operating Long-Term Liability",
            ambiguous=True,
            reason="Lease liability — operating vs financial judgment",
            judgment_code="lease_liability_operating_vs_financing",
        )
    if "deferred tax" in low and ("asset" in low or low.endswith("assets")):
        return ClassificationDecision(
            "Operating Long-Term Asset",
            ambiguous=True,
            reason="Deferred tax asset — operating vs exclude judgment",
        )
    if "deferred tax" in low:
        return ClassificationDecision(
            "Operating Long-Term Liability",
            ambiguous=True,
            reason="Deferred tax liability — operating vs exclude judgment",
        )
    if _match_any(low, ("pension", "retirement benefit", "post-employment")):
        return ClassificationDecision(
            "Operating Long-Term Liability",
            ambiguous=True,
            reason="Pension obligation — operating LT vs financial judgment",
            judgment_code="pension_obligation_operating_vs_financing",
        )
    if "short-term investment" in low or "short term investment" in low:
        return ClassificationDecision(
            "Financial Asset",
            ambiguous=True,
            reason="Short-term investments — financial vs operating by purpose",
            judgment_code="short_term_investment_financial_vs_operating",
        )
    if "equity method" in low or "associate" in low or "joint venture" in low:
        return ClassificationDecision(
            "Operating Long-Term Asset",
            ambiguous=True,
            reason="Equity-method investment — operating vs financial judgment",
            judgment_code="associate_investment_operating_vs_financial",
        )

    # Financial assets / liabilities
    if _match_any(
        low,
        (
            "cash",
            "cash equivalent",
            "marketable securit",
            "trading securit",
            "money market",
        ),
    ):
        return ClassificationDecision("Financial Asset")
    if "investment" in low and "propert" not in low:
        return ClassificationDecision("Financial Asset")
    if _match_any(
        low,
        (
            "bank borrow",
            "borrowing",
            "long-term debt",
            "long term debt",
            "notes payable",
            "commercial paper",
            "bonds payable",
            "loan payable",
        ),
    ) or (low.endswith(" debt") or " debt " in f" {low} "):
        return ClassificationDecision("Financial Liability")

    # Equity components
    if _match_any(
        low,
        (
            "share capital",
            "paid-in capital",
            "paid in capital",
            "additional paid",
            "share premium",
            "retained earnings",
            "treasury stock",
            "treasury share",
            "aoci",
            "other comprehensive",
            "reserves",
            "owners' equity",
            "owners equity",
            "shareholders' equity",
            "shareholders equity",
            "equity attributable",
            "attributable to owners",
            "attributable to equity holders",
        ),
    ) or low == "equity":
        return ClassificationDecision("Equity")

    # Operating WC
    if _match_any(
        low,
        (
            "accounts receivable",
            "trade receivable",
            "receivable",
            "inventory",
            "inventories",
            "prepaid",
        ),
    ):
        return ClassificationDecision("Operating Working Capital Asset")
    if _match_any(
        low,
        (
            "accounts payable",
            "trade payable",
            "payable",
            "accrued",
        ),
    ):
        return ClassificationDecision("Operating Working Capital Liability")
    if "other current asset" in low:
        return ClassificationDecision("Operating Working Capital Asset")
    if "other current liab" in low:
        return ClassificationDecision("Operating Working Capital Liability")

    # Operating long-term
    if _match_any(
        low,
        (
            "property, plant",
            "property plant",
            "ppe",
            "plant and equipment",
            "goodwill",
            "intangible",
            "right-of-use",
        ),
    ):
        return ClassificationDecision("Operating Long-Term Asset")
    if "other non-current asset" in low or "other noncurrent asset" in low:
        return ClassificationDecision("Operating Long-Term Asset")
    if "other non-current liab" in low or "other noncurrent liab" in low:
        return ClassificationDecision("Operating Long-Term Liability")
    if "non-current liab" in low or "noncurrent liab" in low or "long-term liab" in low:
        return ClassificationDecision("Operating Long-Term Liability")
    if "non-current asset" in low or "noncurrent asset" in low:
        return ClassificationDecision("Operating Long-Term Asset")

    raise UnclassifiedBalanceSheetLineError(
        f"Cannot safely classify balance-sheet line {item.label!r}; "
        f"provide classificationOverrides[{item.label!r}]"
    )


def _optional_total(
    items: list[LineItem], concept: str, periods: list[date]
) -> tuple[float | None, ...]:
    resolved = resolve_line(items, concept, required=False)
    if resolved.item is None:
        return tuple(None for _ in periods)
    return tuple(
        required_period_value(resolved.item, p, field=concept) for p in periods
    )


def reformulate_balance_sheet(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    overrides: dict[str, str] | None = None,
) -> BalanceSheetReformulation:
    """Classify every non-subtotal BS line and compute reformulation aggregates."""
    overrides = overrides or {}

    detail_items = [item for item in fin.balance_sheet if not is_balance_sheet_subtotal(item)]
    override_by_identity = resolve_classification_overrides(detail_items, overrides)

    n = len(periods)
    decisions: dict[int, ClassificationDecision] = {}
    detail_indices: list[int] = []
    totals = {cat: [0.0] * n for cat in BALANCE_SHEET_CATEGORIES}

    for idx, item in enumerate(fin.balance_sheet):
        if is_balance_sheet_subtotal(item):
            continue
        detail_indices.append(idx)
        ov = override_by_identity.get(line_identity(item))
        decision = classify_balance_sheet_line(item, override=ov)
        decisions[idx] = decision
        for j, pd in enumerate(periods):
            totals[decision.category][j] += required_period_value(
                item,
                pd,
                field=f"balance_sheet detail {line_identity(item).key()}",
            )

    owca = totals["Operating Working Capital Asset"]
    owcl = totals["Operating Working Capital Liability"]
    olta = totals["Operating Long-Term Asset"]
    oltl = totals["Operating Long-Term Liability"]
    fa = totals["Financial Asset"]
    fl = totals["Financial Liability"]

    nowc = tuple(owca[i] - owcl[i] for i in range(n))
    nola = tuple(olta[i] - oltl[i] for i in range(n))
    noa = tuple(nowc[i] + nola[i] for i in range(n))
    net_debt = tuple(fl[i] - fa[i] for i in range(n))
    implied = tuple(noa[i] - net_debt[i] for i in range(n))

    reported_equity = _optional_total(fin.balance_sheet, "total_equity", periods)
    total_assets = _optional_total(fin.balance_sheet, "total_assets", periods)
    total_liabilities = _optional_total(fin.balance_sheet, "total_liabilities", periods)

    asset_detail = tuple(owca[i] + olta[i] + fa[i] for i in range(n))
    liability_detail = tuple(owcl[i] + oltl[i] + fl[i] for i in range(n))

    def _gap(reported: float | None, detail: float) -> float | None:
        if reported is None:
            return None
        return detail - reported

    asset_gap = tuple(_gap(total_assets[i], asset_detail[i]) for i in range(n))
    liability_gap = tuple(_gap(total_liabilities[i], liability_detail[i]) for i in range(n))
    equity_gap = tuple(
        None if reported_equity[i] is None else implied[i] - reported_equity[i]
        for i in range(n)
    )

    return BalanceSheetReformulation(
        decisions=decisions,
        category_totals={k: tuple(v) for k, v in totals.items()},
        nowc=nowc,
        nola=nola,
        noa=noa,
        net_debt=net_debt,
        implied_equity=implied,
        reported_equity=reported_equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        asset_detail_gap=asset_gap,
        liability_detail_gap=liability_gap,
        equity_gap=equity_gap,
        detail_indices=tuple(detail_indices),
    )


def _reporting_rounding_tolerance(
    detail_count: int,
    *,
    base_tolerance: float,
) -> float:
    """Worst-case reporting-unit rounding for sum(detail) vs reported total.

    Each of ``detail_count`` displayed detail values and the independently
    displayed total may round by at most half a reporting unit, so the
    legitimate absolute gap reaches ``0.5 * (detail_count + 1)``. Explicit
    ``base_tolerance`` remains a floor.
    """
    if detail_count < 0:
        raise ValueError("detail_count must be non-negative")
    if base_tolerance < 0:
        raise ValueError("base_tolerance must be non-negative")
    return max(base_tolerance, 0.5 * (detail_count + 1))


def check_reformulation_integrity(
    reform: BalanceSheetReformulation,
    periods: list[date],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> None:
    """Raise if any available asset/liability/equity gap exceeds tolerance."""
    asset_detail_count = sum(
        1
        for decision in reform.decisions.values()
        if decision.category in _ASSET_REFORMULATION_CATEGORIES
    )
    liability_detail_count = sum(
        1
        for decision in reform.decisions.values()
        if decision.category in _LIABILITY_REFORMULATION_CATEGORIES
    )
    asset_tolerance = _reporting_rounding_tolerance(
        asset_detail_count,
        base_tolerance=tolerance,
    )
    liability_tolerance = _reporting_rounding_tolerance(
        liability_detail_count,
        base_tolerance=tolerance,
    )
    equity_tolerance = _reporting_rounding_tolerance(
        asset_detail_count + liability_detail_count,
        base_tolerance=tolerance,
    )

    failures: list[str] = []
    for i, pd in enumerate(periods):
        label = pd.isoformat()
        if (
            reform.asset_detail_gap[i] is not None
            and abs(reform.asset_detail_gap[i]) > asset_tolerance
        ):
            failures.append(
                f"{label}: asset-detail gap={reform.asset_detail_gap[i]:.4g} "
                f"(classified assets vs Total Assets; "
                f"allowed rounding envelope={asset_tolerance:g})"
            )
        if (
            reform.liability_detail_gap[i] is not None
            and abs(reform.liability_detail_gap[i]) > liability_tolerance
        ):
            failures.append(
                f"{label}: liability-detail gap={reform.liability_detail_gap[i]:.4g} "
                f"(classified liabilities vs Total Liabilities; "
                f"allowed rounding envelope={liability_tolerance:g})"
            )
        if (
            reform.equity_gap[i] is not None
            and abs(reform.equity_gap[i]) > equity_tolerance
        ):
            failures.append(
                f"{label}: equity gap={reform.equity_gap[i]:.4g} "
                f"(NOA-Net Debt vs Reported Equity; "
                f"allowed rounding envelope={equity_tolerance:g})"
            )
    if failures:
        raise ReformulationIntegrityError(
            "Balance-sheet reformulation does not reconcile:\n" + "\n".join(failures)
        )
