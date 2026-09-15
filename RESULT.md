# RESULT.md — Step 9M.2.4.1.1.1.19 Generic Source-Availability Gating for Interest-Dependent Analysis

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.19 — Generic Source-Availability Gating for Interest-Dependent Analysis  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
**Base (plan):** `94db2b04e5915d7326de71e2b62bc772032d155e`  
**Workspace HEAD:** `333d599ac6fc6ab6e34549bcb28d9646415d1f1e`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No invented interest. No 4% fallback for unavailable history. No issuer-specific rules. No commit / push / sync / checkpoint / branch change.

---

## Task 1 — Shared availability contract

Added `core/model/source_availability.py` beside `financial_math.py`.

- Generic `assess_concept_availability` uses `resolve_line` precedence and source-value validation.
- Distinguishes **absent line**, **missing period value**, and **reported zero**.
- Ambiguity (`AmbiguousLineError`) and malformed/non-finite values still raise.
- `assess_interest_availability` applies the contract to interest, after-tax interest, NOPAT, NOPAT margin, RNOA, After-tax CoD, Spread, ROE decomposed, and `hist_avg_after_tax_cod`.
- A dependent cell is available only when every required concept/period exists.
- `compute_anchor` no longer requires interest lines; unavailable branches return `Source unavailable` (distinct from `#N/A`).
- Empty numeric CoD **with missing interest** does **not** use the 4% fallback. Fast Retailing still uses numeric history (`hist_avg_after_tax_cod=0.040400173264287284`).
- `resolve_line(..., required=True)` still raises for explicit interest requests.

---

## Task 2 — Python, Excel, training surfaces

- `ReferenceModelBuilder` filters expected specs whose series value is `Source unavailable`.
- Condensed Interest Expense / Interest Income rows are created only when a source line resolves (no synthetic rows).
- Unavailable Net Interest / NIAT / NOPAT / DuPont interest dependents / ROE financing attribution / NOPAT-per-share display `Source unavailable` in both workbooks and are excluded from practice, hints, and Check.
- Independent schedules remain: reformulation, ETR, sales growth, FLEV, actual ROE, working capital, earnings quality, capex, etc.
- Undefined-ratio `#N/A` semantics unchanged when interest **is** present (zero net debt still yields `#N/A` CoD and the existing 4% aggregate fallback).

---

## Task 3 — Verification (measured)

Commands and actual subprocess exits (`PYTHONPATH=.`, venv pytest):

| Command | Exit | Result |
|---|---:|---|
| `pytest core/tests/test_source_availability.py core/tests/test_lululemon_benchmark.py core/tests/test_reference_integrity.py::test_required_core_income_period_completeness core/tests/test_reference_integrity.py::test_explicit_zero_interest_*` | 0 | 40 passed in 5.01s |
| `pytest` affected model/trainer/reference-integrity/both benchmarks (`test_reference_integrity`, `test_trainer`, `test_lululemon_benchmark`, `test_fast_retailing_benchmark`, `test_capex`, profitability, ROE, per-share, normalization, lease) | 0 | 401 passed in 67.67s |
| `pytest core/tests` | 0 | **1109 passed** in 90.37s |
| Repeat after lazy-import fix: `pytest core/tests/test_source_availability.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py` | 0 | 169 passed in 31.49s |
| `python scripts/build_lululemon_release.py` | 0 | staged, repeat-map deterministic, Check 248/248 |
| `python scripts/build_fast_retailing_release.py` | 0 | 491-cell audit pass |

Focused coverage: each interest concept missing independently; both absent; partial-period absence; reported zero; alias/explicit precedence; ambiguity; malformed; adjacent-period dependencies; failure-path immutability for revenue/NI/pretax/tax; Lululemon unchanged facts; Python/Excel/export-reload/Check.

Limitation: Excel numeric agreement uses formula text + Python expected values + Check (formula/cached-value path). This environment does not evaluate Excel with Excel.app.

---

## Task 4 — Releases

### Lululemon (new)

Unchanged reconciled facts (SHA-256 identical to `benchmark/lululemon/reconciled/`):

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| `supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `Lululemon_Trainer.xlsx` | `c458d5df28cfbb6ee4110ef5d0bdbeca82d149d63906e3c8648bd78bc2f37fb1` | 29488 |
| `Lululemon_Answer_Key.xlsx` | `d833ace00a89af8d5a7069f74a57cd1d74ceed7c5cba723b3ff3d2339e1446a5` | 79367 |
| `Lululemon_Answer_Key.component_map.json` | `5d6c7e811ad28a986503ba6a9a2fb840578c5014e6da3552f4e42896805a4586` | 265691 |
| `availability.json` | `416d9c331e479ada4474bdf54fd2b958d8aa8de8f9b0a6bd25ccc4776582e31c` | 12432 |

Workbook access gain (source completeness unchanged):

| Metric | Baseline (pre-step) | Result |
|---|---|---|
| `compute_anchor` / `ReferenceModelBuilder` / `build` | `MissingLineError: Required concept 'interest_expense' not found in statement lines` | success |
| Active practice / Check total | n/a (no pair) | **248** blank `(0,0,248,248)` / filled `(248,0,0,248)` |
| Unfiltered historical specs | 93 | 65 kept (28 interest-dependent historical cells excluded) |
| Interest lines on condensed IS | n/a | **absent** (no synthetic rows) |
| Interest-dependent outputs (all 4 periods) | failed closed | `Source unavailable`; excluded from Check |
| Independent revenue | 8110518 / 9619278 / 10588126 / 11102600 | unchanged |
| Independent `ppe_capex` | 638657 / 651865 / 689232 / 680802 | unchanged |
| NCIT | 28555 / 15864 / 0 / `None` | unchanged |
| Common stock | 611 / 606 / 581 / 557 | unchanged |
| `hist_avg_after_tax_cod` | n/a (failed) | `Source unavailable` (no 4% substitute) |

### Fast Retailing (regenerated)

| Metric | Before | After |
|---|---|---|
| `expected_specs` / Check | 491 | **491** |
| Component map SHA-256 | `dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34` | **unchanged** |
| supporting standardized SHA-256 | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | **unchanged** |
| Interest lines | present | present; `unavailable=0` |
| Workbook xlsx SHA-256 | changed (openpyxl rewrite + rowmap availability sidecar) | Trainer `d9012bc3…`; Answer Key `073baa7c…` |

Repeat-build Lululemon component maps were byte-identical before replace.

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Lululemon matched pair from unchanged facts | release pair; supporting hashes match benchmark | **PASS** |
| Unavailable interest dependents visible and excluded from grading | `Source unavailable`; 248 Check cells omit nopat/net-interest/CoD/spread/ROE-decomp | **PASS** |
| Source-interest completeness unresolved | G9 still open; no invented amounts | **PASS** |
| Python and Excel agree; no synthetic source rows | condensed Interest Expense/Income omitted; formulas only when available | **PASS** |
| Fast Retailing 491-cell contract | map hash unchanged; audit Check 491 | **PASS** |
| Pretax/tax/required facts/ambiguity/zero vs absence | focused tests | **PASS** |
| Four-period reformulation + NCIT/common stock | Lululemon benchmark + release | **PASS** |
| Parents not closed; INPUT_STATUS PENDING | recorded below | **PASS** |

---

## Remaining blockers (carried forward)

- Source-interest completeness: standalone IS interest still **not found**.
- Parent Plan closure (A5 / B8 / E10).
- A2-ED / B7-MID documentary UNVERIFIED; E11 NonReq UNVERIFIED.
- G5 lease/deferred-tax coverage; G6 period-axis; G7 empty `note_facts`; G8 deferral; remaining TARGET Step 9 gates.

---

## Closure note (does not rewrite the plan)

Step **9M.2.4.1.1.1.19** measured acceptance **PASS**. Keep **INPUT_STATUS: PENDING**. Parents stay **UNRESOLVED**. Child success does not justify blanket DONE.

**Required plan note (do not edit IMPLEMENTATION.md here):** none blocking. G9 source completeness remains a parent residual; this child only gates unavailable interest-dependent analysis.
