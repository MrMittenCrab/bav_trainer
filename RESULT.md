# RESULT.md — Step 9M.2.4.1.1.1.19 Repair Partial-Period Interest Availability

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.19 — Repair Partial-Period Interest Availability  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
**Base (plan):** `a5336a7d3c6f88709d0e11f3ed5bac8e579a6b1a`  
**Workspace HEAD:** `6423e8d338af54c01dc5d9056c924f85e39c598d`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No invented interest. No 4% fallback for unavailable history. No issuer-specific rules. No commit / push / sync / checkpoint / branch change.

---

## Superseded child PASS (corrected)

A prior RESULT for this same step id treated generic all-or-nothing interest gating as child PASS. That assessment is superseded: condensed Interest Expense / Interest Income cells still linked blank source periods, and `hist_avg_after_tax_cod` metadata treated opening-period absence as blocking even when comparable CoD was numeric. This child repairs those remaining availability defects. Capex acceptance (G4; `ppe_capex` 638657 / 651865 / 689232 / 680802) is unchanged and is not a recovered-ownership/publication claim.

---

## Task 1 — Displays and shared aggregate eligibility

- Condensed Interest Expense / Interest Income cells are gated per concept/period in `core/engine/reference_model.py`. Missing or `None` period values display `Source unavailable` in both workbooks; reported zero keeps the source formula. Fully absent lines remain omitted. Source-statement blanks stay blank.
- `historical_average_after_tax_cod` / `comparable_interest_history_available` / `assess_aggregate_cod_availability` in `core/model/source_availability.py` are shared with `compute_anchor`. Opening-period interest absence does not block a numeric average supported by comparable periods. Any comparable CoD period lacking interest keeps the aggregate unavailable. Supported-history undefined ratios still fall back to 4%; unavailable history does not.

---

## Task 2 — Regressions (measured)

Formula inspection is separate from spreadsheet recalculation. This environment does not evaluate Excel with Excel.app; numeric agreement uses Python expected values, formula text, availability sidecars, semantic maps, and Check.

Commands and actual subprocess exits (`PYTHONPATH=.`):

| Command | Exit | Result |
|---|---:|---|
| `python -m pytest core/tests/test_source_availability.py -q --tb=short` | 0 | **33 passed** in 4.38s |
| `python -m pytest core/tests/test_source_availability.py core/tests/test_lululemon_benchmark.py core/tests/test_reference_integrity.py::test_required_core_income_period_completeness core/tests/test_reference_integrity.py::test_explicit_zero_interest_income_still_populates_net_interest_chain core/tests/test_reference_integrity.py::test_explicit_zero_interest_expense_income_only_case -q --tb=line` | 0 | **63 passed** in 7.57s |
| `python -m pytest` affected model/trainer/reference-integrity/both benchmarks (`test_reference_integrity`, `test_trainer`, `test_lululemon_benchmark`, `test_fast_retailing_benchmark`, `test_capex`, profitability, ROE, per-share, normalization, lease) | 0 | **398 passed** in 68.21s |
| `python -m pytest core/tests -q --tb=line` | 0 | **1132 passed** in 92.78s |

Focused coverage added: each interest concept missing independently or together in opening / interior / latest periods; omitted keys vs explicit `None`; reported zero; fully absent lines; condensed cells after export/reload in both workbooks; opening-only omission with independently calculated hist-avg CoD **0.374**; mixed numeric/undefined comparable CoD; missing comparable interest; no numeric comparable ratios; single-period history. Python values and availability metadata agree. Unavailable outputs remain excluded from semantic maps, hints, and Check.

---

## Task 3 — Releases

Staged via `scripts/build_lululemon_release.py` and `scripts/build_fast_retailing_release.py` (both exit 0) before replace. Repeat-build Lululemon semantic maps were byte-identical before replace.

### Lululemon

Unchanged reconciled facts (SHA-256 identical to `benchmark/lululemon/reconciled/`):

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| `supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `Lululemon_Trainer.xlsx` | `4cfc8217b7fa6f01e5cf141b5b4954cf0ed61cc5db9f26470afec73fee5ba1f1` | 29487 |
| `Lululemon_Answer_Key.xlsx` | `52187aa699f3ffa0c2b2b6d62d7ccb81c5463dbba81d82866b0de7170c38df25` | 79366 |
| `Lululemon_Answer_Key.component_map.json` | `5d6c7e811ad28a986503ba6a9a2fb840578c5014e6da3552f4e42896805a4586` | 265691 |
| `availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12427 |

| Metric | Result |
|---|---|
| `compute_anchor` / `ReferenceModelBuilder` / `build` | success (gated) |
| Active practice / Check | **248** blank `(0,0,248,248)` / filled `(248,0,0,248)` |
| Component map SHA-256 | **unchanged** `5d6c7e81…` |
| Condensed Interest Expense / Income rows | **absent** (no synthetic rows) |
| Visible `Source unavailable` cells (Trainer / Answer Key) | **74 / 74** (non-practice display; excluded from Check) |
| Independent revenue | 8110518 / 9619278 / 10588126 / 11102600 |
| Independent `ppe_capex` (G4, separate from this defect) | 638657 / 651865 / 689232 / 680802 |
| NCIT | 28555 / 15864 / 0 / `None` |
| Common stock | 611 / 606 / 581 / 557 |
| `hist_avg_after_tax_cod` | `Source unavailable`; sidecar reason now `absent_line` (comparable periods only); no 4% substitute |

### Fast Retailing

| Metric | Result |
|---|---|
| `expected_specs` / Check | **491** blank `(0,0,491,491)` |
| Component map SHA-256 | **unchanged** `dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34` |
| supporting standardized SHA-256 | **unchanged** `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` |
| `availability.json` SHA-256 | **unchanged** `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` |
| Unavailable cells | **0 / 0**; Interest Expense formulas `='Income Statement'!B10` … `F10` |
| Trainer / Answer Key SHA-256 | `0002bcd0…` / `500ace5c…` (openpyxl rewrite + condensed interest rowmap keys 48 / 49) |

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Partial-period displays never infer zero; Python / workbook / metadata agree | condensed source links; 0.374 opening-only CoD; sidecar | **PASS** |
| Lululemon matched pair from unchanged facts | supporting hashes match benchmark; 248 Check | **PASS** |
| Unavailable interest dependents excluded from grading | 248-cell surface omits nopat/net-interest/CoD/spread/ROE-decomp | **PASS** |
| Source-interest completeness unresolved | G9 still open; no invented amounts | **PASS** |
| Fast Retailing 491-cell contract | map hash unchanged; Check 491 | **PASS** |
| Pretax/tax/required facts/ambiguity/zero vs absence | focused + full `core/tests` | **PASS** |
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

**Required plan note (do not edit IMPLEMENTATION.md here):** none blocking. G9 source completeness remains a parent residual; this child only repairs partial-period interest availability and aggregate eligibility.
