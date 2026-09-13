"""Historical Step 9M.0 helper — OBSOLETE after Step 9M.1.

Formerly built benchmark/fast_retailing/source_facts.json from CFS text extracts.
Canonical documentary input is now benchmark/fast_retailing/extracted/FY*.json
via the generic validate-source / reconcile CLI. Kept only as migration history;
do not use for normal benchmark execution.

Benchmark-only transcription helper. Not used by Trainer runtime.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "benchmark" / "fast_retailing" / "_extract"
OUT = ROOT / "benchmark" / "fast_retailing" / "source_facts.json"

STMT_BS = "Consolidated Statement of Financial Position"
STMT_IS = "Consolidated Statement of Profit or Loss"
STMT_CF = "Consolidated Statement of Cash Flows"

# Ordered primary-statement rows: (label, concept). Concepts distinguish
# duplicate source labels across current / non-current sections.
BS_ROWS: list[tuple[str, str]] = [
    ("Cash and cash equivalents", "cash"),
    ("Trade and other receivables", "trade_and_other_receivables"),
    ("Other financial assets", "other_financial_assets_current"),
    ("Inventories", "inventories"),
    ("Derivative financial assets", "derivative_financial_assets_current"),
    ("Income taxes receivable", "income_taxes_receivable"),
    ("Other assets", "other_current_assets"),
    ("Total current assets", "total_current_assets"),
    ("Property, plant and equipment", "property_plant_equipment"),
    ("Right-of-use assets", "right_of_use_assets"),
    ("Goodwill", "goodwill"),
    ("Intangible assets", "intangible_assets"),
    ("Financial assets", "financial_assets_noncurrent"),
    (
        "Investments in associates accounted for using the equity method",
        "investments_in_associates",
    ),
    ("Deferred tax assets", "deferred_tax_assets"),
    ("Derivative financial assets", "derivative_financial_assets_noncurrent"),
    ("Other assets", "other_noncurrent_assets"),
    ("Total non-current assets", "total_noncurrent_assets"),
    ("Total assets", "total_assets"),
    ("Trade and other payables", "trade_and_other_payables"),
    ("Other financial liabilities", "other_financial_liabilities_current"),
    ("Derivative financial liabilities", "derivative_financial_liabilities_current"),
    ("Lease liabilities", "lease_liability_current"),
    ("Current tax liabilities", "current_tax_liabilities"),
    ("Provisions", "provisions_current"),
    ("Other liabilities", "other_current_liabilities"),
    ("Total current liabilities", "total_current_liabilities"),
    ("Financial liabilities", "financial_liabilities_noncurrent"),
    ("Lease liabilities", "lease_liability_noncurrent"),
    ("Provisions", "provisions_noncurrent"),
    ("Deferred tax liabilities", "deferred_tax_liabilities"),
    ("Derivative financial liabilities", "derivative_financial_liabilities_noncurrent"),
    ("Other liabilities", "other_noncurrent_liabilities"),
    ("Total non-current liabilities", "total_noncurrent_liabilities"),
    ("Total liabilities", "total_liabilities"),
    ("Capital stock", "capital_stock"),
    ("Capital surplus", "capital_surplus"),
    ("Retained earnings", "retained_earnings"),
    ("Treasury stock, at cost", "treasury_stock"),
    ("Other components of equity", "other_components_of_equity"),
    ("Equity attributable to owners of the Parent", "equity_attributable_to_owners"),
    ("Non-controlling interests", "noncontrolling_interests"),
    ("Total equity", "total_equity"),
    ("Total liabilities and equity", "total_liabilities_and_equity"),
]

IS_ROWS: list[tuple[str, str]] = [
    ("Revenue", "revenue"),
    ("Cost of sales", "cost_of_sales"),
    ("Gross profit", "gross_profit"),
    ("Selling, general and administrative expenses", "selling_general_administrative"),
    ("Other income", "other_income"),
    ("Other expenses", "other_expenses"),
    (
        "Share of profit of associates accounted for using the equity method",
        "share_of_profit_of_associates",
    ),
    ("Operating profit", "operating_profit"),
    ("Finance income", "interest_income"),
    ("Finance costs", "interest_expense"),
    ("Profit before income taxes", "pretax_income"),
    ("Income tax expense", "tax_expense"),
    ("Profit for the year", "net_income"),
    ("Owners of the Parent", "profit_attributable_to_owners"),
    ("Non-controlling interests", "profit_attributable_to_nci"),
    ("Basic (yen, dollar)", "basic_eps"),
    ("Diluted (yen, dollar)", "diluted_eps"),
]

# IS share-of-profit label varies slightly by year.
IS_LABEL_ALIASES: dict[str, list[str]] = {
    "Share of profit of associates accounted for using the equity method": [
        "Share of profit of associates accounted for using the equity method",
        "Share of profit and loss of associates accounted for using the equity method",
    ],
}

CF_ROWS: list[tuple[str, str]] = [
    ("Profit before income taxes", "pretax_income"),
    ("Depreciation and amortization", "depreciation_amortization"),
    (
        "Impairment losses/(Reversal of impairment losses)",
        "impairment_losses",
    ),
    ("Interest and dividends income", "interest_and_dividends_income"),
    ("Interest expenses", "interest_expenses_cf"),
    ("Foreign exchange losses/(gains)", "foreign_exchange_losses_gains"),
    (
        "Share of (profit)/loss of associates accounted for using the equity method",
        "share_of_associates_cf",
    ),
    (
        "Losses on disposal of property, plant and equipment",
        "losses_on_disposal_ppe",
    ),
    (
        "(Increase)/decrease in trade and other receivables",
        "change_in_trade_and_other_receivables",
    ),
    ("(Increase)/decrease in inventories", "change_in_inventories"),
    (
        "Increase/(decrease) in trade and other payables",
        "change_in_trade_and_other_payables",
    ),
    ("(Increase)/decrease in other assets", "change_in_other_assets"),
    ("Increase/(decrease) in other liabilities", "change_in_other_liabilities"),
    ("Others, net", "others_net_operating"),
    ("Cash generated from operations", "cash_generated_from_operations"),
    ("Interest and dividends income received", "interest_dividends_received"),
    ("Interest paid", "interest_paid"),
    ("Income taxes paid", "income_taxes_paid"),
    ("Income taxes refunded", "income_taxes_refunded"),
    ("Net cash generated by operating activities", "operating_cash_flow"),
    (
        "Amounts deposited into bank deposits with original maturities of three months or longer",
        "bank_deposits_placed",
    ),
    (
        "Amounts withdrawn from bank deposits with original maturities of three months or longer",
        "bank_deposits_withdrawn",
    ),
    (
        "Payments for property, plant and equipment",
        "payments_for_ppe",
    ),
    ("Payments for intangible assets", "payments_for_intangible_assets"),
    (
        "Payments for acquisition of right-of-use assets",
        "payments_for_rou_assets",
    ),
    ("Payments for investment securities", "payments_for_investment_securities"),
    (
        "Proceeds from sale and redemption of investment securities",
        "proceeds_from_investment_securities",
    ),
    (
        "Payments for lease and guarantee deposits",
        "payments_for_lease_guarantee_deposits",
    ),
    (
        "Proceeds from collection of lease and guarantee deposits",
        "proceeds_from_lease_guarantee_deposits",
    ),
    (
        "Investments in associates accounted for using the equity method",
        "investments_in_associates_cf",
    ),
    ("Others, net", "others_net_investing"),
    ("Net cash used in investing activities", "investing_cash_flow"),
    ("Proceeds from short-term loans payable", "proceeds_from_short_term_loans"),
    ("Repayment of short-term loans payable", "repayment_of_short_term_loans"),
    (
        "Repayment of redemption of corporate bonds",
        "repayment_of_bonds",
    ),
    ("Dividends paid to owners of the Parent", "dividends_paid_to_owners"),
    ("Dividends paid to non-controlling interests", "dividends_paid_to_nci"),
    ("Repayments of lease liabilities", "repayments_of_lease_liabilities"),
    ("Others, net", "others_net_financing"),
    ("Net cash used in financing activities", "financing_cash_flow"),
    (
        "Effect of exchange rate changes on the balance of cash held in foreign currencies",
        "effect_of_exchange_rate_on_cash",
    ),
    (
        "Net increase/(decrease) in cash and cash equivalents",
        "net_change_in_cash",
    ),
    (
        "Cash and cash equivalents at the beginning of year",
        "cash_beginning",
    ),
    (
        "Cash and cash equivalents at the end of year",
        "cash_ending",
    ),
]

# Year-specific CF label variants (matched in order of appearance).
CF_OPTIONAL: dict[str, list[tuple[str, str]]] = {
    # inserted relative to nearest following known concept when present
}

CF_LABEL_ALIASES: dict[str, list[str]] = {
    "Interest and dividends income": [
        "Interest and dividends income",
        "Interest and dividend income",
    ],
    "Interest and dividends income received": [
        "Interest and dividends income received",
        "Interest and dividend income received",
    ],
    "Impairment losses/(Reversal of impairment losses)": [
        "Impairment losses/(Reversal of impairment losses)",
        "Impairment losses",
    ],
    "Share of (profit)/loss of associates accounted for using the equity method": [
        "Share of (profit)/loss of associates accounted for using the equity method",
        "Share of profit and loss of associates accounted for using the equity method",
    ],
    "Repayment of redemption of corporate bonds": [
        "Repayment of redemption of corporate bonds",
        "Repayment of redemption of bonds",
    ],
    "Net cash used in investing activities": [
        "Net cash used in investing activities",
        "Net cash generated by/(used in) investing activities",
    ],
    "Net cash used in financing activities": [
        "Net cash used in financing activities",
        "Net cash generated by/(used in) financing activities",
    ],
    "Net increase/(decrease) in cash and cash equivalents": [
        "Net increase/(decrease) in cash and cash equivalents",
        "Net increase in cash and cash equivalents",
    ],
    "Investments in associates accounted for using the equity method": [
        "Investments in associates accounted for using the equity method",
        "Payments for acquisition of investments in associates",
    ],
}

NOTE_REF = re.compile(r"^(?:\d{1,2}(?:\s*,\s+\d{1,2})*)\s+")
AMOUNT_TOKEN = re.compile(
    r"¥\s*(\(?[\d,]+(?:\.\d+)?\)?)"
    r"|(\([\d,]+(?:\.\d+)?\))"
    r"|(\d{1,3}(?:,\d{3})+(?:\.\d+)?)"
    r"|(\d+\.\d+)"
    r"|(?<![¥\d,])(\d{1,3})(?![\d,.])"
    r"|(—)|(?<![-\d])(-)(?![-\d])"
)
PAGE_SPLIT = re.compile(r"===== PAGE (\d+) =====")


def parse_amount(token: str) -> float | int | None:
    if token in {"—", "-", "–", "－"}:
        return 0  # table dash = reported nil
    neg = False
    t = token.strip()
    if t.startswith("(") and t.endswith(")"):
        neg = True
        t = t[1:-1]
    t = t.replace(",", "").replace("¥", "").strip()
    if not t:
        return None
    if "." in t:
        val: float | int = float(t)
    else:
        val = int(t)
    return -val if neg else val


def extract_amounts(remainder: str) -> list[float | int | None]:
    rest = remainder.strip()
    rest = NOTE_REF.sub("", rest, count=1)
    # Drop trailing USD column marker clutter
    rest = re.sub(r"\$\s*[\d,]+", "", rest)
    vals: list[float | int | None] = []
    for m in AMOUNT_TOKEN.finditer(rest):
        raw = next(g for g in m.groups() if g is not None)
        vals.append(parse_amount(raw))
    return vals


def load_pages(year: int) -> dict[int, str]:
    path = EXTRACT / f"CFS{year}_p1-30.txt"
    text = path.read_text(encoding="utf-8")
    parts = PAGE_SPLIT.split(text)
    pages: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = parts[i + 1]
    return pages


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def collapse_continuations(lines: list[str]) -> list[str]:
    """Join indented continuation fragments onto the previous line."""
    out: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        if out and (line.startswith("   ") or line.startswith("\t")):
            # continuation of previous label / value line
            out[-1] = out[-1].rstrip() + " " + line.strip()
        else:
            out.append(line.rstrip())
    return out


def find_row_line(lines: list[str], labels: list[str], start: int) -> tuple[int, str, str] | None:
    for i in range(start, len(lines)):
        norm = normalize_ws(lines[i])
        for label in labels:
            if norm.startswith(label) or norm.startswith(label + " "):
                # Avoid matching longer unrelated lines incorrectly when label is prefix
                rem = norm[len(label) :].lstrip()
                return i, label, rem
            # Multi-line already collapsed; also allow label embedded after notes? no
    return None


def parse_statement(
    page_text: str,
    rows: list[tuple[str, str]],
    *,
    statement: str,
    pdf_page: int,
    periods: list[str],
    aliases: dict[str, list[str]] | None = None,
    skip_concepts: set[str] | None = None,
) -> list[dict[str, Any]]:
    aliases = aliases or {}
    skip_concepts = skip_concepts or set()
    lines = collapse_continuations(page_text.splitlines())
    cursor = 0
    facts: list[dict[str, Any]] = []
    others_net_seen = 0

    for label, concept in rows:
        if concept in skip_concepts:
            continue
        label_opts = aliases.get(label, [label])
        # Disambiguate repeated "Others, net" by occurrence index
        found = find_row_line(lines, label_opts, cursor)
        if found is None:
            # Optional investing associates / bonds rows may be absent some years
            if concept in {
                "payments_for_investment_securities",
                "proceeds_from_investment_securities",
                "investments_in_associates_cf",
                "repayment_of_bonds",
                "repayment_of_long_term_loans",
            }:
                continue
            raise ValueError(f"Missing row {label!r} ({concept}) on page {pdf_page}")
        idx, matched_label, rem = found
        amounts = extract_amounts(rem)
        # Some multi-line labels put amounts on the same collapsed line; need >=2
        if len(amounts) < 2:
            # try next line for amounts only
            if idx + 1 < len(lines):
                amounts = extract_amounts(normalize_ws(lines[idx + 1]))
        if len(amounts) < 2:
            raise ValueError(
                f"Need 2 amounts for {matched_label!r} got {amounts!r} from {lines[idx]!r}"
            )
        prior, current = amounts[0], amounts[1]
        values = {periods[0]: prior, periods[1]: current}
        # Drop None values keys? keep as null in JSON
        status = "reported"
        # EPS is yen (not millions) — still reported from primary statement
        fact = {
            "label": matched_label if matched_label in label_opts else label,
            "concept": concept,
            "pdf_page": pdf_page,
            "statement": statement,
            "values": values,
            "status": status,
        }
        # Prefer canonical label from rows table
        fact["label"] = label if label in label_opts else matched_label
        # For Owners / NCI under attribution, keep source labels from extract
        if concept == "profit_attributable_to_owners":
            fact["label"] = "Owners of the Parent"
        elif concept == "profit_attributable_to_nci":
            fact["label"] = "Non-controlling interests"
        if concept in {"basic_eps", "diluted_eps"}:
            fact["units"] = "yen"
        facts.append(fact)
        cursor = idx + 1
        if concept.startswith("others_net"):
            others_net_seen += 1
    return facts


def parse_cf_extra_rows(year: int, lines: list[str], periods: list[str], pdf_page: int) -> list[dict[str, Any]]:
    """Capture year-specific CF rows not in the common template."""
    extras: list[dict[str, Any]] = []
    # 2021 has Repayment of long-term loans payable
    for label, concept in [
        ("Repayment of long-term loans payable", "repayment_of_long_term_loans"),
        ("Proceeds from long-term loans payable", "proceeds_from_long_term_loans"),
    ]:
        found = find_row_line(lines, [label], 0)
        if found:
            idx, matched, rem = found
            amounts = extract_amounts(rem)
            if len(amounts) >= 2:
                extras.append(
                    {
                        "label": matched,
                        "concept": concept,
                        "pdf_page": pdf_page,
                        "statement": STMT_CF,
                        "values": {periods[0]: amounts[0], periods[1]: amounts[1]},
                        "status": "reported",
                    }
                )
    return extras


def parse_primary(year: int) -> dict[str, Any]:
    pages = load_pages(year)
    periods = [f"{year - 1}-08-31", f"{year}-08-31"]
    # Pages: BS=2, IS=3, CF=5 consistently across extracts
    bs = parse_statement(
        pages[2], BS_ROWS, statement=STMT_BS, pdf_page=2, periods=periods
    )
    # IS: share-of-profit alias; stop before OCI (page 3 also has OCI after IS)
    # Truncate page 3 at CONSOLIDATED STATEMENT OF COMPREHENSIVE or second Millions header after IS footer
    is_text = pages[3]
    cut = is_text.find("CONSOLIDATED STATEMENT OF COMPREHENSIVE INCOME")
    if cut == -1:
        cut = is_text.find("Other comprehensive income")
    if cut != -1:
        # Keep attribution rows which appear before OCI starts on same page... 
        # Actually attribution is before "Earnings per share", and OCI is a new statement block.
        # Find "Earnings per share" block end: after Diluted line, then "See accompanying"
        pass
    # Safer: cut at "CONSOLIDATED STATEMENT OF COMPREHENSIVE" if present in footer after IS,
    # or at second "Profit for the year" that starts OCI section.
    # Structure: IS ends with Diluted EPS, then footer, then OCI starts with Profit for the year again.
    m = re.search(
        r"Diluted \(yen, dollar\).*?(?=See accompanying|Millions of yen\nThousands|\Z)",
        is_text,
        re.S,
    )
    if m:
        is_text = is_text[: m.end()]

    # Fix share label for older years before parse
    is_rows = []
    for label, concept in IS_ROWS:
        if concept == "share_of_profit_of_associates":
            is_rows.append((label, concept))
        else:
            is_rows.append((label, concept))

    income = parse_statement(
        is_text,
        is_rows,
        statement=STMT_IS,
        pdf_page=3,
        periods=periods,
        aliases=IS_LABEL_ALIASES,
    )

    cf_text = pages[5]
    # CF page may include notes start after statement
    cut = cf_text.find("1   Reporting Entity")
    if cut == -1:
        cut = cf_text.find("Reporting Entity")
    if cut != -1:
        cf_text = cf_text[:cut]

    # Build CF rows dynamically: common template may miss year-specific rows.
    # Parse by walking CF_ROWS but allow optional misses for investing securities etc.
    cf_lines = collapse_continuations(cf_text.splitlines())
    cash_flow: list[dict[str, Any]] = []
    cursor = 0
    for label, concept in CF_ROWS:
        label_opts = CF_LABEL_ALIASES.get(label, [label])
        found = find_row_line(cf_lines, label_opts, cursor)
        if found is None:
            if concept in {
                "payments_for_investment_securities",
                "proceeds_from_investment_securities",
                "investments_in_associates_cf",
                "repayment_of_bonds",
            }:
                continue
            raise ValueError(f"CF{year}: missing {label!r} ({concept})")
        idx, matched_label, rem = found
        amounts = extract_amounts(rem)
        if len(amounts) < 2 and idx + 1 < len(cf_lines):
            amounts = extract_amounts(normalize_ws(cf_lines[idx + 1]))
        if len(amounts) < 2:
            raise ValueError(f"CF{year}: amounts for {label}: {amounts} line={cf_lines[idx]!r}")
        cash_flow.append(
            {
                "label": label,
                "concept": concept,
                "pdf_page": 5,
                "statement": STMT_CF,
                "values": {periods[0]: amounts[0], periods[1]: amounts[1]},
                "status": "reported",
            }
        )
        cursor = idx + 1

    # Insert year-specific extras in document order by re-scan
    extras = parse_cf_extra_rows(year, cf_lines, periods, 5)
    if extras:
        # Place long-term loan repayment before bond repayment / dividends if present
        concepts = {f["concept"] for f in cash_flow}
        for ex in extras:
            if ex["concept"] not in concepts:
                # insert before dividends_paid_to_owners
                insert_at = next(
                    (
                        i
                        for i, f in enumerate(cash_flow)
                        if f["concept"] == "dividends_paid_to_owners"
                    ),
                    len(cash_flow),
                )
                cash_flow.insert(insert_at, ex)

    return {
        "file": f"benchmark/fast_retailing/source/Fastretailing_CFS{year}.pdf",
        "periods": periods,
        "income_statement": income,
        "balance_sheet": bs,
        "cash_flow": cash_flow,
        "share_facts": [],
        "note_facts": [],
    }


def find_page_for_snippet(pages: dict[int, str], snippet: str) -> int | None:
    for p, text in pages.items():
        if snippet in text:
            return p
    return None


def parse_notes(year: int, filing: dict[str, Any]) -> None:
    pages = load_pages(year)
    periods = filing["periods"]
    prior, current = periods
    notes: list[dict[str, Any]] = []
    shares: list[dict[str, Any]] = []

    # --- Lease note: aggregate PV total & interest ---
    lease_page = find_page_for_snippet(pages, "(a) Lease liabilities")
    if lease_page is None:
        lease_page = find_page_for_snippet(pages, "Interest expenses on lease liabilities")
    lease_text = pages.get(lease_page or -1, "")

    # Total line: Total ¥... ¥... ¥... ¥...  (four columns) — take present-value columns (2nd and 4th)
    total_m = re.search(
        r"Total\s+¥?\s*([\d,]+)\s+¥?\s*([\d,]+)\s+¥?\s*([\d,]+)\s+¥?\s*([\d,]+)",
        lease_text,
    )
    if total_m:
        # cols: remaining prior, PV prior, remaining current, PV current
        pv_prior = parse_amount(total_m.group(2))
        pv_current = parse_amount(total_m.group(4))
        notes.append(
            {
                "label": "Total present value of lease liabilities",
                "concept": "lease_liability_aggregate",
                "pdf_page": lease_page,
                "note": "17 Leases",
                "values": {prior: pv_prior, current: pv_current},
                "status": "reported",
            }
        )

    int_m = re.search(
        r"Interest expenses on lease liabilities\s+¥?\s*([\d,]+)\s+¥?\s*([\d,]+)",
        lease_text,
    )
    if int_m:
        notes.append(
            {
                "label": "Interest expenses on lease liabilities",
                "concept": "lease_interest_expense",
                "pdf_page": lease_page,
                "note": "17 Leases",
                "values": {
                    prior: parse_amount(int_m.group(1)),
                    current: parse_amount(int_m.group(2)),
                },
                "status": "reported",
            }
        )

    # ROU ending balances from lease note roll-forward "At 31 August YEAR"
    rou_m = re.search(
        rf"At 31 August {year}\s+[^\n]*?([\d,]+)\s*$",
        lease_text,
        re.M,
    )
    # The Total column is last number on the At 31 August line
    rou_lines = re.findall(
        rf"At 31 August ({year - 1}|{year})\s+(.+)",
        lease_text,
    )
    rou_vals: dict[str, int | float | None] = {}
    for y_str, rest in rou_lines:
        nums = re.findall(r"\(?[\d,]+\)?", rest)
        if nums:
            # last numeric token is Total
            rou_vals[f"{y_str}-08-31"] = parse_amount(nums[-1])
    if rou_vals:
        # ensure both periods if available
        values = {k: rou_vals[k] for k in periods if k in rou_vals}
        if len(values) == 1:
            # sometimes only current year line uses year; prior year line is At 31 August prior
            pass
        if values:
            notes.append(
                {
                    "label": "Right-of-use assets",
                    "concept": "right_of_use_assets",
                    "pdf_page": lease_page,
                    "note": "17 Leases",
                    "values": values if len(values) == 2 else {
                        **{p: rou_vals.get(p) for p in periods},
                    },
                    "status": "reported",
                }
            )
    # Prefer BS values mirrored into note_facts when roll-forward parse incomplete
    if not any(n["concept"] == "right_of_use_assets" for n in notes):
        bs_rou = next(
            r for r in filing["balance_sheet"] if r["concept"] == "right_of_use_assets"
        )
        notes.append(
            {
                "label": "Right-of-use assets",
                "concept": "right_of_use_assets",
                "pdf_page": 2,
                "note": "Consolidated Statement of Financial Position",
                "values": dict(bs_rou["values"]),
                "status": "reported",
            }
        )
    else:
        # Fill missing period from BS if needed
        for n in notes:
            if n["concept"] == "right_of_use_assets":
                bs_rou = next(
                    r
                    for r in filing["balance_sheet"]
                    if r["concept"] == "right_of_use_assets"
                )
                for p in periods:
                    if n["values"].get(p) is None:
                        n["values"][p] = bs_rou["values"][p]

    # PP&E payments from CF (also as note_fact for module diagnostics)
    ppe_pay = next(
        r for r in filing["cash_flow"] if r["concept"] == "payments_for_ppe"
    )
    notes.append(
        {
            "label": "Payments for property, plant and equipment",
            "concept": "ppe_capex_payments",
            "pdf_page": 5,
            "note": "Consolidated Statement of Cash Flows",
            "values": dict(ppe_pay["values"]),
            "status": "reported",
        }
    )

    da = next(
        r for r in filing["cash_flow"] if r["concept"] == "depreciation_amortization"
    )
    notes.append(
        {
            "label": "Depreciation and amortization",
            "concept": "depreciation_amortization",
            "pdf_page": 5,
            "note": "Consolidated Statement of Cash Flows",
            "values": dict(da["values"]),
            "status": "reported",
        }
    )

    # Parent / NCI profit from IS
    parent_profit = next(
        r
        for r in filing["income_statement"]
        if r["concept"] == "profit_attributable_to_owners"
    )
    nci_profit = next(
        r
        for r in filing["income_statement"]
        if r["concept"] == "profit_attributable_to_nci"
    )
    notes.append(
        {
            "label": "Profit attributable to owners of the Parent",
            "concept": "profit_attributable_to_owners",
            "pdf_page": 3,
            "note": "Consolidated Statement of Profit or Loss",
            "values": dict(parent_profit["values"]),
            "status": "reported",
        }
    )
    notes.append(
        {
            "label": "Profit attributable to non-controlling interests",
            "concept": "profit_attributable_to_nci",
            "pdf_page": 3,
            "note": "Consolidated Statement of Profit or Loss",
            "values": dict(nci_profit["values"]),
            "status": "reported",
        }
    )

    parent_eq = next(
        r
        for r in filing["balance_sheet"]
        if r["concept"] == "equity_attributable_to_owners"
    )
    nci_eq = next(
        r for r in filing["balance_sheet"] if r["concept"] == "noncontrolling_interests"
    )
    notes.append(
        {
            "label": "Equity attributable to owners of the Parent",
            "concept": "equity_attributable_to_owners",
            "pdf_page": 2,
            "note": "Consolidated Statement of Financial Position",
            "values": dict(parent_eq["values"]),
            "status": "reported",
        }
    )
    notes.append(
        {
            "label": "Non-controlling interests",
            "concept": "noncontrolling_interests_equity",
            "pdf_page": 2,
            "note": "Consolidated Statement of Financial Position",
            "values": dict(nci_eq["values"]),
            "status": "reported",
        }
    )

    # --- EPS note ---
    eps_page = find_page_for_snippet(pages, "Average number of common stock during the year")
    if eps_page is None:
        eps_page = find_page_for_snippet(pages, "Earnings per Share")
    eps_text = pages.get(eps_page or -1, "")

    was_m = re.search(
        r"Average number of common stock during the year \(Shares\)\s+([\d,]+)\s+([\d,]+)",
        eps_text,
    )
    if was_m:
        shares.append(
            {
                "label": "Average number of common stock during the year",
                "concept": "basic_weighted_average_shares",
                "pdf_page": eps_page,
                "note": "27 Earnings per Share",
                "values": {
                    prior: parse_amount(was_m.group(1)),
                    current: parse_amount(was_m.group(2)),
                },
                "status": "reported",
                "units": "shares",
            }
        )

    dil_m = re.search(
        r"Increase in number of common stock \(Shares\)\s+([\d,]+)\s+([\d,]+)",
        eps_text,
    )
    if dil_m:
        shares.append(
            {
                "label": "Increase in number of common stock (share subscription rights)",
                "concept": "dilutive_shares",
                "pdf_page": eps_page,
                "note": "27 Earnings per Share",
                "values": {
                    prior: parse_amount(dil_m.group(1)),
                    current: parse_amount(dil_m.group(2)),
                },
                "status": "reported",
                "units": "shares",
            }
        )

    # Diluted EPS from primary IS
    diluted = next(
        (r for r in filing["income_statement"] if r["concept"] == "diluted_eps"),
        None,
    )
    if diluted:
        shares.append(
            {
                "label": "Diluted earnings per share for the year",
                "concept": "diluted_eps",
                "pdf_page": 3,
                "note": "Consolidated Statement of Profit or Loss",
                "values": dict(diluted["values"]),
                "status": "reported",
                "units": "yen",
            }
        )
        # Also mirror from EPS note if present
        note_dil = re.search(
            r"Diluted earnings per share for the year \(Yen\)\s+([\d,.]+)\s+Diluted earnings per share for the year \(Yen\)\s+([\d,.]+)",
            eps_text,
        )
        if note_dil:
            shares.append(
                {
                    "label": "Diluted earnings per share for the year",
                    "concept": "diluted_eps_note",
                    "pdf_page": eps_page,
                    "note": "27 Earnings per Share",
                    "values": {
                        prior: float(note_dil.group(1).replace(",", "")),
                        current: float(note_dil.group(2).replace(",", "")),
                    },
                    "status": "reported",
                    "units": "yen",
                }
            )

    # Derived diluted WAS when both components present
    was = next(
        (s for s in shares if s["concept"] == "basic_weighted_average_shares"), None
    )
    dil = next((s for s in shares if s["concept"] == "dilutive_shares"), None)
    if was and dil:
        derived = {
            p: (was["values"][p] or 0) + (dil["values"][p] or 0) for p in periods
        }
        shares.append(
            {
                "label": "Diluted weighted-average shares (basic + dilutive)",
                "concept": "diluted_weighted_average_shares",
                "pdf_page": eps_page,
                "note": "27 Earnings per Share",
                "values": derived,
                "status": "derived",
                "units": "shares",
                "derivation": "basic_weighted_average_shares + dilutive_shares",
            }
        )

    # Stock split disclosure
    split_page = find_page_for_snippet(pages, "3-to-1")
    if split_page is None:
        split_page = find_page_for_snippet(pages, "stock split")
    if split_page is not None:
        split_text = pages[split_page]
        if "3-to-1" in split_text or "3-for-1" in split_text or "split on a 3" in split_text:
            notes.append(
                {
                    "label": "Common stock split 3-to-1 effective 1 March 2023",
                    "concept": "stock_split",
                    "pdf_page": split_page,
                    "note": "27 Earnings per Share / Capital stock notes",
                    "values": {
                        "ratio": "3-for-1",
                        "effective_date": "2023-03-01",
                    },
                    "status": "reported",
                }
            )

    # Finance costs note vs primary: record primary as authoritative pointer
    notes.append(
        {
            "label": "Finance costs (primary statement)",
            "concept": "interest_expense",
            "pdf_page": 3,
            "note": "Consolidated Statement of Profit or Loss",
            "values": dict(
                next(
                    r
                    for r in filing["income_statement"]
                    if r["concept"] == "interest_expense"
                )["values"]
            ),
            "status": "reported",
        }
    )

    filing["note_facts"] = notes
    filing["share_facts"] = shares


def build() -> dict[str, Any]:
    filings: dict[str, Any] = {}
    for year in range(2021, 2026):
        filing = parse_primary(year)
        parse_notes(year, filing)
        filings[str(year)] = filing
    return {
        "company": "FAST RETAILING CO., LTD.",
        "hk_stock_code": "6288.HK",
        "currency": "JPY",
        "units": "JPY millions",
        "filings": filings,
    }


FY2025_ANCHORS = {
    ("income_statement", "revenue", "2025-08-31"): 3400539,
    ("income_statement", "pretax_income", "2025-08-31"): 650574,
    ("income_statement", "tax_expense", "2025-08-31"): -191421,
    ("income_statement", "interest_income", "2025-08-31"): 99143,
    ("income_statement", "interest_expense", "2025-08-31"): -12834,
    ("income_statement", "net_income", "2025-08-31"): 459153,
    ("income_statement", "profit_attributable_to_owners", "2025-08-31"): 433009,
    ("balance_sheet", "cash", "2025-08-31"): 893239,
    ("balance_sheet", "property_plant_equipment", "2025-08-31"): 332351,
    ("balance_sheet", "right_of_use_assets", "2025-08-31"): 477111,
    ("balance_sheet", "goodwill", "2025-08-31"): 8092,
    ("balance_sheet", "intangible_assets", "2025-08-31"): 91606,
    ("balance_sheet", "lease_liability_current", "2025-08-31"): 126830,
    ("balance_sheet", "lease_liability_noncurrent", "2025-08-31"): 386670,
    ("balance_sheet", "total_assets", "2025-08-31"): 3859353,
    ("balance_sheet", "total_liabilities", "2025-08-31"): 1531852,
    ("balance_sheet", "equity_attributable_to_owners", "2025-08-31"): 2273115,
    ("balance_sheet", "noncontrolling_interests", "2025-08-31"): 54385,
    ("balance_sheet", "total_equity", "2025-08-31"): 2327501,
    ("cash_flow", "operating_cash_flow", "2025-08-31"): 580618,
    ("cash_flow", "depreciation_amortization", "2025-08-31"): 216492,
    ("cash_flow", "payments_for_ppe", "2025-08-31"): -135535,
}


def verify_anchors(doc: dict[str, Any]) -> list[str]:
    f = doc["filings"]["2025"]
    errors: list[str] = []
    for (section, concept, period), expected in FY2025_ANCHORS.items():
        row = next((r for r in f[section] if r["concept"] == concept), None)
        if row is None:
            errors.append(f"missing {section}.{concept}")
            continue
        got = row["values"].get(period)
        if got != expected:
            errors.append(f"{section}.{concept}[{period}] expected {expected} got {got}")
    # note anchors
    notes = f["note_facts"]
    lease_agg = next(n for n in notes if n["concept"] == "lease_liability_aggregate")
    if lease_agg["values"]["2025-08-31"] != 513501:
        errors.append(f"lease aggregate got {lease_agg['values']}")
    lease_int = next(n for n in notes if n["concept"] == "lease_interest_expense")
    if lease_int["values"]["2025-08-31"] != 8464:
        errors.append(f"lease interest got {lease_int['values']}")
    shares = f["share_facts"]
    was = next(s for s in shares if s["concept"] == "basic_weighted_average_shares")
    if was["values"]["2025-08-31"] != 306786602:
        errors.append(f"WAS got {was['values']}")
    dil = next(s for s in shares if s["concept"] == "dilutive_shares")
    if dil["values"]["2025-08-31"] != 461202:
        errors.append(f"dilutive got {dil['values']}")
    return errors


def main() -> None:
    doc = build()
    errors = verify_anchors(doc)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for year, filing in doc["filings"].items():
        print(
            f"  {year}: IS={len(filing['income_statement'])} "
            f"BS={len(filing['balance_sheet'])} CF={len(filing['cash_flow'])} "
            f"share={len(filing['share_facts'])} note={len(filing['note_facts'])}"
        )
    if errors:
        print("ANCHOR FAILURES:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)
    print("FY2025 anchors: OK")


if __name__ == "__main__":
    main()
