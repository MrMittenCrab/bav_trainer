"""BAVGEM Stage-3 balance-sheet classification and reformulation.

Single authority for Python expected values and Excel Condensed Financials.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from ..data.interface import LineItem, StandardizedFinancials
from ..data.schema import normalize_label
from .line_resolver import resolve_line

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


class ClassificationError(ValueError):
    """Base classification/reformulation error."""


class UnclassifiedBalanceSheetLineError(ClassificationError):
    """A non-subtotal line cannot be safely classified without an override."""


class InvalidClassificationOverrideError(ClassificationError):
    """Override value is not one of the eight BAVGEM categories."""


class ReformulationIntegrityError(ClassificationError):
    """Classified detail does not reconcile to reported totals."""


@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False


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
    for ch in ("'", "'", "`"):
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

    low = _norm(item.label)

    # Ambiguous judgment calls — real default + flag
    if _match_any(low, ("right of use", "rou asset", "operating lease")) and "liab" not in low:
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
        )
    if "short-term investment" in low or "short term investment" in low:
        return ClassificationDecision(
            "Financial Asset",
            ambiguous=True,
            reason="Short-term investments — financial vs operating by purpose",
        )
    if "equity method" in low or "associate" in low or "joint venture" in low:
        return ClassificationDecision(
            "Operating Long-Term Asset",
            ambiguous=True,
            reason="Equity-method investment — operating vs financial judgment",
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
            "deferred revenue",
            "contract liability",
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


def _val(item: LineItem, period: date) -> float:
    v = item.values.get(period)
    return float(v) if v is not None else 0.0


def _optional_total(
    items: list[LineItem], concept: str, periods: list[date]
) -> tuple[float | None, ...]:
    resolved = resolve_line(items, concept, required=False)
    if resolved.item is None:
        return tuple(None for _ in periods)
    return tuple(_val(resolved.item, p) for p in periods)


def reformulate_balance_sheet(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    overrides: dict[str, str] | None = None,
) -> BalanceSheetReformulation:
    """Classify every non-subtotal BS line and compute reformulation aggregates."""
    overrides = overrides or {}
    override_by_norm = {_norm(k): v for k, v in overrides.items()}

    n = len(periods)
    decisions: dict[int, ClassificationDecision] = {}
    detail_indices: list[int] = []
    totals = {cat: [0.0] * n for cat in BALANCE_SHEET_CATEGORIES}

    for idx, item in enumerate(fin.balance_sheet):
        if is_balance_sheet_subtotal(item):
            continue
        detail_indices.append(idx)
        ov = override_by_norm.get(_norm(item.label))
        decision = classify_balance_sheet_line(item, override=ov)
        decisions[idx] = decision
        for j, pd in enumerate(periods):
            totals[decision.category][j] += _val(item, pd)

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


def check_reformulation_integrity(
    reform: BalanceSheetReformulation,
    periods: list[date],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> None:
    """Raise if any available asset/liability/equity gap exceeds tolerance."""
    failures: list[str] = []
    for i, pd in enumerate(periods):
        label = pd.isoformat()
        if reform.asset_detail_gap[i] is not None and abs(reform.asset_detail_gap[i]) > tolerance:
            failures.append(
                f"{label}: asset-detail gap={reform.asset_detail_gap[i]:.4g} "
                f"(classified assets vs Total Assets)"
            )
        if (
            reform.liability_detail_gap[i] is not None
            and abs(reform.liability_detail_gap[i]) > tolerance
        ):
            failures.append(
                f"{label}: liability-detail gap={reform.liability_detail_gap[i]:.4g} "
                f"(classified liabilities vs Total Liabilities)"
            )
        if reform.equity_gap[i] is not None and abs(reform.equity_gap[i]) > tolerance:
            failures.append(
                f"{label}: equity gap={reform.equity_gap[i]:.4g} "
                f"(NOA-Net Debt vs Reported Equity)"
            )
    if failures:
        raise ReformulationIntegrityError(
            "Balance-sheet reformulation does not reconcile:\n" + "\n".join(failures)
        )
