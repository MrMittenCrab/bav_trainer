# RESULT.md — Step 9M.2.4.1.1.1 Repair Coverage, Workbook Period Identity, and Acceptance Accounting

**Status:** COMPLETE (this repair child’s acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Repair Coverage, Workbook Period Identity, and Acceptance Accounting  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `a62893ff0d6f095e029d510142074da39e5243cc` (plan commit; base `29fc582`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production changes.

---

## Withdrawal of unsupported prior claims

Prior `RESULT.md` claimed COMPLETE for **Repair Independent Pretax and ETR Parity Verification** while:

1. pretax/ETR coverage was **not** a complete 12-case concept × order × input-mode matrix with distinct IDs;
2. workbook period checks used `assert period == expect.period_ends[j]` (loop variable only) rather than actual saved/reloaded `Income Statement` / `Condensed Financials` headers;
3. parent-criterion inventory used aggregate “supported” labels without criterion-level PASS/FAIL/UNVERIFIED accounting against `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, and this step.

Those COMPLETE / matrix-complete / period-identity / parent-closure claims are **withdrawn**. This RESULT replaces them with measured matrix outcomes, header-mutation rejection, and criterion-level evidence statuses.

---

## Task 1 — Parity coverage matrix (12/12)

Parameter axes:

| Axis | Values |
|---|---|
| Concept mode | canonical `pretax_income` / alias `income_before_tax` / normalized label fallback (`concept=""`) |
| Source-row order | natural / reordered |
| Input mode | original fixture / standardized export→reload |

Alias fixture expectations (independent of production helpers): pretax **400 / 500**, tax **−60 / −80**, ETR **0.15 / 0.16**.  
Canonical: label `Carrying pretax amount`, pretax **250 / 310**, tax **−40 / −55**.  
Label fallback: pretax **180 / 210**, tax **−27 / −42**.  
Periods (all modes): `2024-12-31`, `2025-12-31`.

| Test ID | Measured outcome |
|---|---|
| `alias-natural-original` | **PASS** |
| `alias-reorder-original` | **PASS** |
| `alias-natural-reload` | **PASS** |
| `alias-reorder-reload` | **PASS** |
| `canon-natural-original` | **PASS** |
| `canon-reorder-original` | **PASS** |
| `canon-natural-reload` | **PASS** |
| `canon-reorder-reload` | **PASS** |
| `label-natural-original` | **PASS** |
| `label-reorder-original` | **PASS** |
| `label-natural-reload` | **PASS** |
| `label-reorder-reload` | **PASS** |

Node: `core/tests/test_reference_integrity.py::test_pretax_etr_parity_coverage_matrix[...]` — **12 passed**.

Each case verified fixture-owned labels/concepts/period identities/amounts/row ordering; Python `compute_anchor` pretax/ETR; saved/reloaded Answer-Key source links + strict ETR contract + referenced-cell evaluation (not Excel recalculation).

Retained non-matrix regressions:

| Node | Outcome |
|---|---|
| `test_pretax_parity_zero_denominator_emitted_arithmetic` | **PASS** (`#N/A` / 0.16; zero-guard contract) |
| `test_pretax_parity_detects_alias_removal` | **PASS** |
| `test_line_resolver.py` pretax precedence / duplicate ambiguity / missing-required / tax-exclusion | **PASS** (suite) |

---

## Task 2 — Workbook period identity

Validator now reads actual headers:

- `Income Statement` row `Line Item` → period columns 2..N
- `Condensed Financials` row `CONDENSED INCOME STATEMENT` → period columns 2..N

Checks header **count**, **order**, and **identity** against fixture-owned `period_ends`. Each pretax/tax source column and the ETR condensed column is bound to that independently expected period (column number alone is insufficient).

Baseline: clean saved/reloaded Answer Key **PASS**.

Header-only mutations (formulas/values unchanged; no regenerate before validate) — node `test_pretax_parity_rejects_corrupted_period_headers`:

| Mutation | Rejection |
|---|---|
| Swap IS period headers | `AssertionError` matching `period (header\|identity)` |
| Alter IS header to `2099-01-01` | same |
| Swap Condensed IS section headers | same |
| Alter Condensed header to `2099-06-15` | same |

Preserved link/arithmetic corruptions — node `test_pretax_parity_rejects_corrupted_source_links_and_etr`:

| Mutation | Rejection |
|---|---|
| Pretax → tax source row | `pretax (source label mismatch\|link redirected)` |
| Pretax → other period column | `pretax (link wrong period\|source value mismatch)` |
| ETR minus removed / reversed / bad zero-guard | `etr formula contract mismatch` |

Reported as formula inspection + referenced-cell evaluation, **not** Excel recalculation.

---

## Task 3 — Original-criteria inventory

Statuses: **PASS** = freshly measured this run; **PASS (historical)** = traceable prior-revision measurement cited, reconfirmed where live; **UNVERIFIED** = required evidence still missing; **N/A** = not a success gate for this child.

### From `aa6adc1` (9M.2.4)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| A1 | Four-period `check_reformulation_integrity` under unchanged tolerances | Remeasured committed standardized; all gaps 0.0; envelopes A/L=6.0, E-detail=2.5, implied=11.5; node `test_four_period_reformulation_integrity` | **PASS** |
| A2 | Original liability/equity discrepancies explained and repaired with causal rows | **Before** (traceable `cdf0c9f` RESULT on pre-sparse standardized): 2023 liability-detail **−28555** / equity **+28555**; 2024 **−15864** / **+15864**. Causal row: omitted `non_current_income_taxes_payable`. **After** (this run): gaps **0.0**; NCIT **28555 / 15864 / 0.0 / None** | **PASS (historical before + live after)** |
| A3 | Temp-dir Lululemon build: success **or** exact next exception | `MissingLineError: Required concept 'interest_expense' not found in statement lines` | **PASS** (recorded; not a success gate) |
| A4 | Genuine inconsistencies fail closed; artifacts unchanged | Equal-omission / rounding / immutability nodes below; Lululemon hashes unchanged | **PASS** |
| A5 | Parent 9M.2.4 closed for Plan | Requires Plan assessment of every original criterion | **UNVERIFIED** (keep UNRESOLVED) |

### From `a370a02` (9M.2.4.1)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| B1 | NCIT sparse series 28555 / 15864 / reported 0 / `None` | Live standardized + `test_non_current_income_taxes_payable_restored_sparse_axis` | **PASS** |
| B2 | Sparse absence ≠ reported zero through standardization / export-reload | Sparse liability/equity nodes + NCIT provenance `retained_sparse_axis` | **PASS** |
| B3 | Provenance preserves selected/superseded/outside-axis; no invented facts | Committed provenance hash unchanged; sparse retention tests | **PASS** |
| B4 | Failure-path immutability | `test_reconcile_immutability_verified_after_subprocess_failure`, `..._comparison_failure`, `..._guard_detects_temp_mutation` | **PASS** |
| B5 | Common stock 611 / 606 / 581 / 557 | Live values + `test_common_stock_classifies_across_all_periods` | **PASS** |
| B6 | Parent 9M.2.4.1 closed | Plan closure pending | **UNVERIFIED** |

### From `2e88322` (9M.2.4.1.1 evidence-grounded sparse-detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| C1 | Independent asset/liability evidence gates before usable sparse results | `test_sparse_absence_fails_without_independent_totals`, `test_sparse_absence_fails_when_total_row_null`, `test_sparse_absence_fails_on_contradictory_gap` | **PASS** |
| C2 | Leading/interior/trailing absence, zero, complete-row coverage | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes[...]`, `test_sparse_interior_absence_with_neighboring_reported_zero`, `test_complete_rows_unchanged_with_sparse_neighbor` | **PASS** |
| C3 | Missing keys / contradictory / equal omissions / rounding boundaries | `test_sparse_missing_key_still_fails_closed`, `test_reformulation_detects_equal_asset_liability_omissions`, rounding envelope accept/reject nodes | **PASS** |
| C4 | Four-period Lululemon integrity after sparse repair | Same as A1 | **PASS** |

### From `88ce931` (9M.2.4.1.1 equity-detail repair)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| D1 | Sparse equity omission fails despite zero implied-equity gaps | `test_sparse_equity_omission_fails_despite_zero_identity_gaps` (omit 100 → equity-detail rejects) | **PASS** |
| D2 | Signed contra-equity; subtotal exclusion; override controls | `test_sparse_equity_signed_contra_equity_contributes`, `test_sparse_equity_subtotal_excluded_from_detail`, `test_sparse_equity_explicit_override_controls_detail` | **PASS** |
| D3 | Equity missing keys / unavailable totals / envelope boundaries | `test_sparse_equity_missing_key_fails_closed`, `test_sparse_equity_unavailable_total_fails_closed`, at/beyond envelope nodes | **PASS** |
| D4 | Implied-equity remains separate from equity-detail gate | Documented in test design; Lululemon implied-equity gap 0.0 with separate env 11.5 | **PASS** |

### Current step `a62893f` / `29fc582` acceptance

| # | Criterion | Evidence | Status |
|---|---|---|---|
| E1 | All 12 matrix cases pass | Table above | **PASS** |
| E2 | Header corruption rejected as well as link/arithmetic defects | Period + link/ETR mutation tables | **PASS** |
| E3 | Four-period integrity + causal liability/equity explanation | A1–A2 | **PASS** |
| E4 | Asset/liability/signed equity-detail gates; fail-closed controls | C*/D* | **PASS** |
| E5 | Sparse ≠ zero; provenance preserved | B2–B3 | **PASS** |
| E6 | NCIT / Common stock / G1–G3 / empty unclassified | NCIT+CS live; `test_gift_card_liability_classifies_across_all_periods` (G1), `test_ppe_classifies_resolves_and_enables_fixed_asset` (G2), `test_common_stock_classifies_across_all_periods` (G3); `test_four_period_reformulation_integrity` asserts empty unclassified | **PASS** |
| E7 | Required suites pass; artifacts unchanged | Suite counts + hashes below | **PASS** |
| E8 | Every parent original criterion closed | A5 / B6 | **UNVERIFIED** — parents stay UNRESOLVED |

### Evidence classes (kept distinct)

| Class | Status |
|---|---|
| Synthetic pretax/ETR calculation + formula parity (12-matrix + mutations) | **PASS** |
| Real-company pretax resolution (concept/label/values/export-reload) | **PASS** — `income_before_tax` / `Income before income tax expense` / 1332571 / 2175735 / 2576077 / 2238967 |
| Full-company Python↔Excel pretax parity on unmodified Lululemon | **UNVERIFIED / unavailable** — workbook blocked by `interest_expense` (not repaired) |

---

## Measured reformulation gaps (committed standardized, this run)

Tolerance formula unchanged: `max(1.0, 0.5 * (detail_count + 1))` (`DEFAULT_TOLERANCE=1.0`).

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts: assets **11** → 6.0; liabilities **11** → 6.0; equity detail **4** → 2.5; implied A+L=22 → 11.5.  
- NCIT: **28555 / 15864 / 0.0 / `None`**.  
- Common stock: **611 / 606 / 581 / 557**.  
- `check_reformulation_integrity` → **PASS** all four periods.

### Workbook probe (unmodified input, temporary directory)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Recorded only; **not repaired**.

---

## Source / artifact hashes (before = after)

No generated refresh authorized. Stray FR/demo suite mutations reverted.

| Artifact | SHA-256 | Size |
|---|---|---:|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

---

## Fresh verification counts

```text
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 537 passed in 11.14s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.43s

PYTHONPATH=. pytest core/tests -q
→ 1089 passed in 87.89s
```

Working tree after suite cleanup: only intentional test + RESULT edits.

---

## Diff scope (intentional)

- `core/tests/test_reference_integrity.py` — 12-ID pretax/ETR coverage matrix; actual IS/Condensed period-header identity checks; header-corruption rejection; retained zero/alias/link/ETR controls
- `RESULT.md` (this file)

`test_line_resolver.py` / `test_lululemon_benchmark.py`: no edit required this pass (regressions already present).  
Production code, committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1.1 acceptance for **repair coverage, workbook period identity, and acceptance accounting** is met. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED** until Plan’s evidence-based parent closure. Any genuinely new child uses first unused ID **9M.2.4.1.1.1.3**. Step 9 remains incomplete.
