# RESULT.md — Step 9M.2.4.1.1.1.18 Assess Lululemon Interest Source Evidence

**Status:** COMPLETE (this child; documentary four-period interest assessment only)  
**Step:** 9M.2.4.1.1.1.18 — Assess Lululemon Interest Source Evidence  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
**Base (plan):** `cbecd085c9f6b9305b3272ba65c5aca210875871`  
**Workspace HEAD:** `db97498ca48ac57fae1fed71d922ea12ca61f5ea`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No production/test edits. No invented interest. No forecasting/valuation. No commit / push / sync / checkpoint / branch change.

---

## Task 1 — Missing-input contract (inspected vs executed)

### Inspected code (not mutated)

| Path | SHA-256 | Size | Role |
|---|---|---:|---|
| `core/model/line_resolver.py` | `d02fa65932612c5ffa985497189e7c17094e5945311f3f8b7f00ec55d40f19ca` | 9154 | P1 exact concept; P2 label aliases; P3 none for interest |
| `core/model/financial_math.py` | `5ee2243feaff734cc08aefc69c8f4f3b0e48da9a5e97f48e40e559268e396733` | 8454 | `compute_anchor` requires both interest lines |
| `core/engine/reference_model.py` | `ac11b3445d10b62b0fdba3c7fbbdd8e94339b9d851dfea0108e9637442b20fbb` | 203399 | Excel condensed IS requires both source rows |
| `core/tests/test_lululemon_benchmark.py` | `9eddf31a71efffdd840aa107430fe62ad9ee318ac7e439afa31ea12c47384d4c` | 26860 | expects `interest_expense` MissingLineError |
| `core/tests/test_reference_integrity.py` | `8262bd625d0b0c7ff204c59c5534edd39661f72f83a46dfed1b8ff3b21c78b77` | 130966 | explicit zero still requires the line; absent line fails |

**Required concepts:** `interest_expense` and `interest_income`. Both are mandatory on the income statement for Python and Excel.

**Resolution precedence** (`resolve_line`):

1. P1 exact normalized `LineItem.concept` (`interest_expense` / `interest_income`). No `_EXPLICIT_CONCEPT_ALIASES` for either.
2. P2 exact normalized labels: expense `{finance cost, finance costs, interest expense, interest expenses}`; income `{finance income, interest income}`.
3. P3 safe patterns: none for interest.

`other_income_expense_net` is not a resolver concept (`ValueError: Unknown financial concept`). Label `Other income (expense), net` matches neither alias set.

**Python path** (`compute_anchor`): `resolve_line(..., required=True)` then `required_period_series` for every modeled period. Missing line → `MissingLineError`. Present line with a missing/None period → `MissingHistoricalValueError`. Net interest is `-(interest_expense + interest_income)` (demo sign: expense typically negative, income positive). `historical_lease.lease_interest_expense` is an optional adjustment only when `fin.historical_lease` is supplied.

**Excel path** (`ReferenceModelBuilder` / `build_training_workbook`): `_resolved_source_row(..., required=True)` for both concepts before Condensed Financials Interest Expense / Interest Income formulas. Same resolver. First raise when both are absent is `interest_expense`.

**Existing tests (inspected):** `test_lululemon_benchmark.py` asserts workbook `MissingLineError` matching `interest_expense`. `test_reference_integrity.py` shows explicit **reported zero** still requires the line; a missing `interest_income` line fails closed. Absence ≠ reported zero.

### Input hashes (re-measured)

| Path | SHA-256 | Size |
|---|---|---:|
| `source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |
| `extracted/LULU_FY2022.json` | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| `extracted/LULU_FY2023.json` | `745876dbac871a45b0bd9857c921529bf786f178cfc304af6c0fb12a12373b2e` | 60225 |
| `extracted/LULU_FY2024.json` | `a0bc4ccef0974b1ae08e5aa0c4601989476061e98afedd0f860655d0d75dc372` | 60984 |
| `extracted/LULU_FY2025.json` | `3887f0d452d9c8887133e25e5a9bad018918de66f0e50419afafab3f072892dd` | 58912 |
| `reconciled/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `reconciled/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

Canonical periods: `2023-01-29`, `2024-01-28`, `2025-02-02`, `2026-02-01`. Units: USD thousands. `historical_lease`: `null`.

### Extracted / reconciled interest trace (executed)

All four extracted filings: **zero** income-statement, cash-flow, or `note_facts` rows whose label/concept contains `interest`, `finance cost`, or `finance income`. `note_facts: []` on all four.

Reconciled IS has 16 rows. The only non-operating P&L bridge line is `other_income_expense_net` / `Other income (expense), net`. No `interest_expense` or `interest_income` row. Cash-flow 34 rows: no interest/finance labels. `conflicts.json` has 3 overlap conflicts, all cash-flow WC restatements — **none** interest-related. `supplemental_conflict_count=0`.

Selected `other_income_expense_net` (agreeing observations; not treated as interest):

| Period | Amount | Selected source |
|---|---:|---|
| 2023-01-29 | 4163 | FY2024 comparative p51 |
| 2024-01-28 | 43059 | FY2025 comparative p51 |
| 2025-02-02 | 70380 | FY2025 comparative p51 |
| 2026-02-01 | 28352 | FY2025 current p51 |

Off-axis extracted comparatives (not on reconciled axis): FY2022 IS other income `2022-01-30=514`, `2021-01-31=-636` (`outside_model_axis` in provenance).

### Executed code-path verification

```text
PYTHONPATH=. python3 <probe on reconciled standardized.json>
resolve_line(IS, interest_expense, required=True) → MissingLineError: Required concept 'interest_expense' not found in statement lines
resolve_line(IS, interest_income, required=True) → MissingLineError: Required concept 'interest_income' not found in statement lines
resolve_line(..., required=False) → item=None, index=None for both
compute_anchor → MissingLineError interest_expense
ReferenceModelBuilder → MissingLineError interest_expense
build_training_workbook(/tmp/lulu_interest_probe) → MissingLineError interest_expense
resolve_line(..., "other_income_expense_net") → ValueError: Unknown financial concept
```

```text
PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py -q
→ 27 passed in 3.32s
```

---

## Task 2 — Filing evidence

### Search coverage

Terms: `interest`, `interest expense`, `interest income`, `interest paid`, `interest received`, `finance cost(s)`, `finance income`, `other income (expense)`, `revolving credit`, `credit facility`, `borrowings outstanding`, `lease interest`, `operating lease expense`, `supplemental cash flow`, `cash paid`.

Sections: IS; CF body; MD&A Other income (expense), net; Interest Rate Risk; Note Revolving Credit Facilities; Note Leases; income-tax policy (interest/penalties); Note Supplemental Cash Flow Information.

FY2022/FY2023: `pypdf` text readable. FY2024/FY2025: custom font encoding; text decoded and **page images** inspected for IS (both), FY2025 MD&A p39, and supplemental CF (both p79).

### Income statement — required concepts

No filing presents a standalone `Interest expense` / `Finance costs` or `Interest income` / `Finance income` line.

After `Income from operations` every filing presents only `Other income (expense), net`, then `Income before income tax expense`.

| Period | IS label present | Amount | Sign | Currency/unit | PDF page / hash | Extraction |
|---|---|---:|---|---|---|---|
| 2023-01-29 | Other income (expense), net | 4163 | + (net other income) | USD thousands | FY2022 p50 `b344d1e7…`; FY2023 p56; FY2024 p51 | extracted + selected |
| 2024-01-28 | Other income (expense), net | 43059 | + | USD thousands | FY2023 p56; FY2024 p51; FY2025 p51 | extracted + selected |
| 2025-02-02 | Other income (expense), net | 70380 | + | USD thousands | FY2024 p51; FY2025 p51 | extracted + selected |
| 2026-02-01 | Other income (expense), net | 28352 | + | USD thousands | FY2025 p51 `82e00f90…` | extracted + selected |

**Not equivalent** to `interest_expense` or `interest_income`. Mixed line. Resolver aliases do not match.

### MD&A — qualitative interest income (not a usable amount)

| Filing | Page | Wording | Quantified interest income? |
|---|---|---|---|
| FY2022 | 35 | Increase in other income, net “primarily due to an increase in interest income from higher interest rates, partially offset by an increase in other expenses.” Other income 4,163 / 514. | No |
| FY2023 | 39 | Increase “primarily due to an increase in interest income as a result of higher cash balances and higher interest rates.” Other income 43,059 / 4,163. | No |
| FY2024 | 39 (decoded) | Increase “primarily due to an increase in interest income as a result of higher average cash balances.” Other income 70,380 / 43,059. | No |
| FY2025 | 39 (image) | Decrease “primarily due to a decrease in interest income as a result of lower average cash balances and lower interest rates.” Other income 28,352 / 70,380. | No |

Primary-cause language does not isolate a gross interest-income amount. FY2022 explicitly mentions offsetting other expenses.

### Cash interest paid — supplemental CF note (not IS interest_expense)

Cross-filing overlapping years **agree**. Not in extracted JSON (`note_facts` empty). Not on the CF statement body.

| Period | Interest paid | Unit | Pages | Meaning |
|---|---:|---|---|---|
| 2023-01-29 | 116 | USD thousands | FY2022 p77; FY2023 p83; FY2024 p79 | cash paid, not accrual IS expense |
| 2024-01-28 | 234 | USD thousands | FY2023 p83; FY2024 p79; FY2025 p79 | cash paid |
| 2025-02-02 | 478 | USD thousands | FY2024 p79; FY2025 p79 | cash paid |
| 2026-02-01 | 1028 | USD thousands | FY2025 p79 | cash paid |

**Not equivalent** to `interest_expense`. No disclosure that cash interest paid equals IS interest expense.

### Credit facilities — no outstanding borrowings (≠ reported zero interest)

| Period-end | Facility outstanding | Page |
|---|---|---|
| 2023-01-29 | No borrowings besides letters of credit $6.5m | FY2022 p66–67 |
| 2024-01-28 | No borrowings besides letters of credit $6.3m | FY2023 p72–73 |
| 2025-02-02 | No borrowings besides letters of credit $6.1m | FY2024 p68 (decoded) |
| 2026-02-01 | No borrowings besides letters of credit $6.4m | FY2025 p61/68 (decoded) |

Unused facility + commitment-fee language is **not** a reported `interest_expense` of 0. Do not infer zero.

### Lease interest — not separately disclosed

Lease notes report a single **operating lease expense** (plus short-term/variable). No discrete lease-interest amount.

- FY2022 p72: operating lease expense 245,767 / 215,549 / 193,498 (thousands).
- FY2023 p79: 282,888 / 245,767 / 215,549.
- `historical_lease` remains `null`. Not `lease_interest_expense`.

### Tax-related interest policy (no amount)

- FY2022 p60: tax interest/penalties recognized in **other income (expense), net**.
- FY2023 p65 / FY2024 p60 / FY2025 p59: recognized in **income tax expense**.

No quantified tax-interest amount. Not a standalone `interest_expense`.

---

## Task 3 — Four-period disposition

| Required concept | 2023-01-29 | 2024-01-28 | 2025-02-02 | 2026-02-01 |
|---|---|---|---|---|
| `interest_expense` | **not found** in inspected IS | **not found** | **not found** | **not found** |
| `interest_income` | **not found** as a standalone quantified amount | **not found** | **not found** | **not found** |

Related disclosures (recorded, **not usable** as the required inputs):

| Related item | Classification | Why not usable |
|---|---|---|
| Other income (expense), net 4163 / 43059 / 70380 / 28352 | source-supported mixed IS line | not gross interest; no equivalence; not a resolver concept |
| MD&A “primarily interest income” | qualitative only | no isolated amount |
| Cash interest paid 116 / 234 / 478 / 1028 | source-supported but omitted from extracted `note_facts` | cash ≠ IS expense; equivalence not established |
| Unused revolvers | narrative | absence of borrowings ≠ reported zero interest |
| Operating lease expense | source-supported lease cost | not lease interest; `historical_lease` null |
| Tax interest/penalties policy | policy only | no amount; booked in other income or tax |

No comparative conflict on interest: the required lines were never extracted. Other-income selected values agree across overlapping filings.

### Next bounded change (no production in this step)

Evidence does **not** support a production alias, inferred zero, or weakening of `required=True`.

**Accounting / product decision required (Plan):** whether the historical engine may proceed when a non-financial issuer presents only `Other income (expense), net` and never reports standalone interest lines. That decision is out of this assessment. Do not invent defaults.

**Smallest later extraction-only change (does not unblock the workbook):** add supplemental `Interest paid` 116 / 234 / 478 / 1028 to `note_facts` with the page/hash citations above (touches G7). Independent expected values are those four cash amounts. Regression: existing interest MissingLineError must still fire; no alias of cash paid or other-income into `interest_expense` / `interest_income`. No release regeneration from extraction-only notes.

Workbook availability and parent closure are **not** claimed here.

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Four-period disposition for both required concepts | matrix above; not found / not equivalent | **PASS** |
| Usable amounts have verified meaning | **none proposed** as required-input amounts | **PASS** |
| Absence / ambiguity / reported zero kept distinct | unused facility ≠ zero; cash paid ≠ expense; other-income ≠ interest income | **PASS** |
| Independently verifiable citations + hashes | PDF pages + SHA-256 + JSON provenance | **PASS** |
| Both code paths compared to assessment | executed MissingLineError on both concepts; first raise `interest_expense` | **PASS** |
| No production / workbook / release / parent closure claimed | none performed | **PASS** |

Original parent technical acceptance retained (A2-ED / B7-MID Doc UNVERIFIED; A5 / B8 / E10 Plan UNVERIFIED; E11 NonReq UNVERIFIED/`interest_expense`). Capex G4 and Fast Retailing 491-cell contract untouched.

---

## Remaining blockers (carried forward)

- Lululemon Trainer/Answer-Key: `MissingLineError: Required concept 'interest_expense' not found in statement lines` — **source-supported standalone interest lines are not present**; next step is a Plan accounting-policy decision, not an inferred input.
- Parent Plan closure (A5 / B8 / E10).
- G5+ remaining Lululemon gaps; G7 empty `note_facts` (cash interest paid is one unextracted note fact).

---

## Closure note (does not rewrite the plan)

Step **9M.2.4.1.1.1.18** measured acceptance **PASS**. Four-period interest assessment complete. Keep **INPUT_STATUS: PENDING**. Parents stay **UNRESOLVED**.

**Required plan note (do not edit IMPLEMENTATION.md here):** both required interest concepts are **not found** as standalone IS facts in the four supplied filings. Other income (expense), net and cash interest paid are present but not equivalent. Do not invent zeros. Plan must decide the generic missing-interest contract before any production/test change; optional later `note_facts` capture of Interest paid 116 / 234 / 478 / 1028 would not satisfy the current required-input paths.
