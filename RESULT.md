# RESULT.md — Step 9M.2.4.1.1.1 Complete Criterion-Level Evidence Accounting

**Status:** COMPLETE (criterion-level evidence ledger complete; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `0f1d2c3af6a5a5895f04947bfdcb8b49d4dc4c5a` (plan commit; base `7303db2`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production changes. Diff scope: `RESULT.md` only.

---

## Withdrawal of unsupported prior COMPLETE claim

Prior `RESULT.md` (at `7303db2` / working copy) claimed **COMPLETE** for **Repair Coverage, Workbook Period Identity, and Acceptance Accounting** while:

1. deterministic dual-reconcile commands, exit codes, input hashes, and per-artifact r1/r2/committed byte comparisons were not freshly recorded for this evidence-accounting obligation;
2. `test_generic_reconcile_is_deterministic` and each subprocess-failure / comparison-failure / mutation-detection / drift-detection outcome were not listed as separate ledger entries;
3. historical before/after measurements bundled implied-equity “equity gap” with later equity-detail without stating that the equity-detail gate did not exist at `cdf0c9f`, and did not separately account for the sparse-`None` `MissingHistoricalValueError` stage (`c50912c`);
4. closure prose treated the ledger as establishing technical parent completion despite explicit UNVERIFIED parent-closure obligations.

Those COMPLETE / “acceptance met implies parents closable” claims are **withdrawn**. This RESULT replaces them with criterion-split PASS / PASS (historical) / UNVERIFIED accounting and freshly measured reconciliation evidence.

---

## Evidence classes (kept distinct)

| Class | Meaning |
|---|---|
| Fresh | Measured this run on current HEAD + committed artifacts |
| Historical | Traceable prior revision / RESULT with cited SHA |
| Diagnostic | Temporary reproduction under current code; not a substitute for historical gate semantics |
| Unavailable | Required measurement cannot be obtained without inventing facts or unauthorized scope |

---

## Task 2 — Deterministic reconciliation (fresh)

Revision under test: `0f1d2c3`. Inputs: unmodified `benchmark/lululemon/extracted` + `benchmark/lululemon/source`. Outputs: isolated temp dirs only (`/tmp/lulu_reconcile_uyIz2c/r1`, `.../r2`). No refresh of committed artifacts.

### Input hashes (unmodified)

| Path | SHA-256 | Size |
|---|---|---:|
| `extracted/LULU_FY2022.json` | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| `extracted/LULU_FY2023.json` | `745876dbac871a45b0bd9857c921529bf786f178cfc304af6c0fb12a12373b2e` | 60225 |
| `extracted/LULU_FY2024.json` | `a0bc4ccef0974b1ae08e5aa0c4601989476061e98afedd0f860655d0d75dc372` | 60984 |
| `extracted/LULU_FY2025.json` | `3887f0d452d9c8887133e25e5a9bad018918de66f0e50419afafab3f072892dd` | 58912 |
| `source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |

### Commands and exits

```text
PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o /tmp/lulu_reconcile_uyIz2c/r1
→ exit 0; stdout includes overlap_conflicts=3; wrote three artifacts

PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o /tmp/lulu_reconcile_uyIz2c/r2
→ exit 0; stdout includes overlap_conflicts=3; wrote three artifacts
```

### Generated vs committed artifact comparison

| Artifact | r1 SHA-256 | r2 SHA-256 | committed SHA-256 | Size | r1==r2 | r1==committed | Diff explanation |
|---|---|---|---|---:|---|---|---|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | same | same | 22548 | yes | yes | none |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | same | same | 699401 | yes | yes | none |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | same | same | 4718 | yes | yes | none |

Committed bytes before = after both runs (verified).

### Reconcile test nodes (separate outcomes; fresh)

| Node | Params | Outcome |
|---|---|---|
| `test_generic_reconcile_is_deterministic` | — | **PASS** |
| `test_reconcile_immutability_verified_after_subprocess_failure` | `fail_pass=1` | **PASS** |
| `test_reconcile_immutability_verified_after_subprocess_failure` | `fail_pass=2` | **PASS** |
| `test_reconcile_immutability_verified_after_comparison_failure` | `fail_at=inter_run` | **PASS** |
| `test_reconcile_immutability_verified_after_comparison_failure` | `fail_at=baseline` | **PASS** |
| `test_reconcile_immutability_guard_detects_temp_mutation` | 3 artifacts × {pass1, inter_run, baseline} = 9 | **PASS** (9/9) |
| `test_reconcile_drift_is_detected_without_rewriting_expected` | each of 3 artifacts | **PASS** (3/3) |

Collective: **17 passed in 3.21s**.

---

## Historical defect stages (distinct revisions)

| Stage | Code / RESULT revision | What changed | Integrity measurement available? |
|---|---|---|---|
| Original liability defect | `cdf0c9f` RESULT; standardized `ba1ba068…` size 22289 | NCIT omitted via `omitted_incomplete_axis` | Yes — liability + implied-equity gaps |
| Sparse-value exception | `c50912c` RESULT (HEAD then `a370a02`) | NCIT retained with `None` @ 2026-02-01 | **No** — `MissingHistoricalValueError` before usable reformulation |
| Sparse liability gate | `17114fc` / plan `2e88322` | `None` non-contributing under A/L/(then implied) evidence gate | Yes — gaps 0.0; equity-detail column not yet separate |
| Equity-omission regression repair | `8c0098c` / plan `88ce931` | Independent equity-detail gate added | Yes — A/L/E-detail/implied all measured |

---

## Historical before / after gap tables

Tolerance **formula** (all stages): `max(1.0, 0.5 * (detail_count + 1))` (`DEFAULT_TOLERANCE=1.0`).

### BEFORE — original liability defect (`cdf0c9f` RESULT on committed pre-sparse standardized)

Causal excluded row: `non_current_income_taxes_payable` / `Non-current income taxes payable`  
Selected source amounts: **28555 / 15864 / 0 / absent**; row absent from standardized (provenance `omitted_incomplete_axis`).

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---|---:|---:|---:|---|---:|
| 2023-01-29 | 0.0 | **−28555.0** | *gate did not exist* | **+28555.0** | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2024-01-28 | 0.0 | **−15864.0** | *gate did not exist* | **+15864.0** | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2025-02-02 | 0.0 | 0.0 | *gate did not exist* | 0.0 | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2026-02-01 | 0.0 | 0.0 | *gate did not exist* | 0.0 | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |

- Counts then: assets **11** → 6.0; liabilities **10** (NCIT excluded) → 5.5; implied uses A+L=21 → 11.0.  
- Resolved totals existed (`Total assets` / `Total liabilities` / `Total stockholders' equity`); classified liability sum short by exactly the NCIT amounts; implied-equity mirrored liability gaps.  
- Equity-detail aggregate: **UNVERIFIED** at this stage (independent equity-detail gate introduced only in `8c0098c` / `88ce931`). Do not infer historical equity-detail from current results.

**Diagnostic probe only** (temp copy of `ba1ba068…` under **current** code): liability-detail (−28555, −15864, 0, 0); implied-equity (+28555, +15864, 0, 0); equity-detail (0,0,0,0); envelopes L=5.5 / implied=11. Matches historical liability + implied measurements; **not** used as historical equity-detail evidence.

### Intermediate — sparse retention before nullable aggregation (`c50912c`)

After NCIT restored as **28555 / 15864 / 0.0 / `None`**, reformulation raised:

```text
MissingHistoricalValueError: ... Non-current income taxes payable ...
has no supplied value for modeled period 2026-02-01
```

Four-period before/after **gap aggregates for this stage: UNVERIFIED / unavailable** as live integrity measurements (gate/aggregation did not return usable reformulation). Exception text is the recorded historical outcome.

### AFTER — current committed standardized (fresh this run)

Included causal row NCIT: **28555 / 15864 / 0.0 / `None`** (FY2026 `None` non-contributing; FY2025 reported 0 contributing).  
Common stock: **611 / 606 / 581 / 557**.

Resolved totals (fresh):

| Period | total_assets | total_liabilities | total_equity |
|---|---:|---:|---:|
| 2023-01-29 | 5607038.0 | 2458239.0 | 3148799.0 |
| 2024-01-28 | 7091941.0 | 2859860.0 | 4232081.0 |
| 2025-02-02 | 7603292.0 | 3279245.0 | 4324047.0 |
| 2026-02-01 | 8456743.0 | 3494903.0 | 4961840.0 |

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts now: assets **11** → 6.0; liabilities **11** → 6.0; equity detail **4** → 2.5; implied A+L=22 → 11.5.  
- `check_reformulation_integrity` → **PASS** all four periods.  
- Node: `test_four_period_reformulation_integrity` **PASS**.

### Provenance observations (NCIT; committed)

- `retained_sparse_axis` for `non_current_income_taxes_payable`; `missing_periods=["2026-02-01"]`; available `2023-01-29`, `2024-01-28`, `2025-02-02`.  
- Not present in `omitted_incomplete_axis`.  
- Selected / superseded / outside-axis observations remain in provenance (committed hash unchanged).  
- Node: `test_non_current_income_taxes_payable_restored_sparse_axis` **PASS**.

### Non-balance-sheet completeness

Unchanged omission behavior for incomplete-axis non-BS rows retained by existing reconciler/standardizer tests (suite A **PASS**); no production change this step.

---

## Task 1 — Criterion-level acceptance ledger

Statuses: **PASS** = fresh this run; **PASS (historical)** = cited prior revision + reconfirmed where live; **UNVERIFIED** = missing measurement or Plan-only closure; **N/A** = not a success gate for this child.

### From `aa6adc1` (9M.2.4 — Lululemon Liability-Detail Reformulation Integrity)

| # | Criterion (retained wording) | Evidence | Status |
|---|---|---|---|
| A1 | All four periods pass `check_reformulation_integrity` within unchanged tolerance rules | Fresh gaps all 0.0; envelopes above; `test_four_period_reformulation_integrity` | **PASS** |
| A2 | Recorded liability and corresponding equity discrepancies explained and repaired with causal rows | Historical before `cdf0c9f`; after this run; causal NCIT 28555/15864; diagnostic temp reproduce of liability/implied gaps | **PASS (historical before + live after)** |
| A2-ED | Historical equity-**detail** gaps at original defect | Equity-detail gate did not exist at `cdf0c9f` | **UNVERIFIED** |
| A3 | Temp-dir Lululemon build: success or exact next exception | `MissingLineError: Required concept 'interest_expense' not found in statement lines` | **PASS** (recorded; not a success gate) |
| A4 | Genuine inconsistencies fail closed; artifacts unchanged | Equal-omission / rounding / immutability nodes; Lululemon hashes unchanged | **PASS** |
| A5 | Parent 9M.2.4 closed for Plan | Requires Plan assessment of every original criterion | **UNVERIFIED** |

### From `a370a02` (9M.2.4.1 — Preserve Sparse Liability Facts)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| B1 | NCIT sparse series 28555 / 15864 / reported 0 / `None` | Live standardized + `test_non_current_income_taxes_payable_restored_sparse_axis` | **PASS** |
| B2 | Sparse absence ≠ reported zero through standardization / export-reload | Sparse nodes + NCIT provenance `retained_sparse_axis` / `missing_period` | **PASS** |
| B3 | Provenance preserves selected/superseded/outside-axis; no invented facts | Committed provenance hash unchanged; sparse retention tests | **PASS** |
| B4 | Failure-path immutability | Subprocess / comparison / mutation / drift nodes above (17) | **PASS** |
| B5 | Common stock 611 / 606 / 581 / 557 | Live values + `test_common_stock_classifies_across_all_periods` | **PASS** |
| B6 | Dual reconcile identical to committed; conflicts stable | Fresh dual-run table | **PASS** |
| B7 | Four-period integrity after sparse retention (parent mandatory) | Blocked at `c50912c` by `MissingHistoricalValueError`; later restored at `17114fc`+ | **PASS (historical exception + live after)** |
| B7-MID | Gap aggregates during MissingHistoricalValueError stage | Unavailable — no usable reformulation | **UNVERIFIED** |
| B8 | Parent 9M.2.4.1 closed | Plan closure pending | **UNVERIFIED** |

### From `2e88322` (9M.2.4.1.1 — Evidence-Grounded Sparse-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| C1 | Independent asset/liability evidence gates before usable sparse results | `test_sparse_absence_fails_without_independent_totals`, `..._when_total_row_null`, `..._on_contradictory_gap` | **PASS** |
| C2 | Leading/interior/trailing absence, zero, complete-row coverage | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes[...]`, `test_sparse_interior_absence_with_neighboring_reported_zero`, `test_complete_rows_unchanged_with_sparse_neighbor` | **PASS** |
| C3 | Missing keys / contradictory / equal omissions / rounding boundaries | `test_sparse_missing_key_still_fails_closed`, `test_reformulation_detects_equal_asset_liability_omissions`, rounding accept/reject nodes | **PASS** |
| C4 | Four-period Lululemon integrity after sparse repair | Same as A1 | **PASS** |
| C5 | Synthetic before-failure / after-success for sparse eligibility | Sparse fail + reconcile-success nodes (28 selected sparse/rounding) | **PASS** |

### From `88ce931` (9M.2.4.1.1 — Repair Sparse Equity-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| D1 | Sparse equity omission fails despite zero implied-equity gaps | `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | **PASS** |
| D2 | Signed contra-equity; subtotal exclusion; override controls | `test_sparse_equity_signed_contra_equity_contributes`, `..._subtotal_excluded_from_detail`, `..._explicit_override_controls_detail` | **PASS** |
| D3 | Equity missing keys / unavailable totals / envelope boundaries | `test_sparse_equity_missing_key_fails_closed`, `..._unavailable_total_fails_closed`, at/beyond envelope nodes | **PASS** |
| D4 | Implied-equity remains separate from equity-detail gate | Test design + Lululemon implied env 11.5 vs E-detail env 2.5 | **PASS** |

### From `a62893f` / current step obligations (pretax matrix + this evidence step)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| E1 | All 12 pretax/ETR matrix cases | `test_pretax_etr_parity_coverage_matrix[...]` — 12/12 **PASS** (fresh) | **PASS** |
| E2 | Header corruption + link/arithmetic rejection (formula inspection, not Excel recalc) | `test_pretax_parity_rejects_corrupted_period_headers`, `..._corrupted_source_links_and_etr` | **PASS** |
| E3 | Zero-pretax + alias-removal retained | `test_pretax_parity_zero_denominator_emitted_arithmetic`, `test_pretax_parity_detects_alias_removal` | **PASS** |
| E4 | Four-period integrity + causal liability/equity explanation | A1–A2 | **PASS** |
| E5 | Asset/liability/signed equity-detail gates; fail-closed | C*/D* | **PASS** |
| E6 | Sparse ≠ zero; provenance preserved | B2–B3 | **PASS** |
| E7 | NCIT / Common stock / G1–G3 / empty unclassified | NCIT+CS live; gift-card/PPE/common-stock nodes; integrity asserts empty unclassified | **PASS** |
| E8 | Required suites; deterministic artifact comparisons; failure-path immutability | Suites below + reconcile 17 | **PASS** |
| E9 | Dual-reconcile criterion-level evidence supplied | Task 2 tables | **PASS** |
| E10 | Every parent original criterion closed | A5 / B8 | **UNVERIFIED** — parents stay UNRESOLVED |
| E11 | Full-company Python↔Excel pretax parity on unmodified Lululemon | Workbook blocked by `interest_expense` | **UNVERIFIED / unavailable** |

Matrix IDs (fresh): `alias|canon|label` × `natural|reorder` × `original|reload` — all **PASS**.

---

## Workbook probe (unmodified input, temporary directory)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Recorded only; **not repaired**. Workbook success is **not** an original parent acceptance requirement.

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
PYTHONPATH=. pytest \
  core/tests/test_lululemon_benchmark.py::test_generic_reconcile_is_deterministic \
  core/tests/test_lululemon_benchmark.py::test_reconcile_immutability_verified_after_subprocess_failure \
  core/tests/test_lululemon_benchmark.py::test_reconcile_immutability_verified_after_comparison_failure \
  core/tests/test_lululemon_benchmark.py::test_reconcile_immutability_guard_detects_temp_mutation \
  core/tests/test_lululemon_benchmark.py::test_reconcile_drift_is_detected_without_rewriting_expected -v
→ 17 passed in 3.21s

PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k 'pretax_etr_parity_coverage_matrix or pretax_parity_rejects_corrupted or pretax_parity_zero or pretax_parity_detects_alias' -v
→ 16 passed, 51 deselected in 1.71s

PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 537 passed in 11.19s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 28.46s

PYTHONPATH=. pytest core/tests -q
→ 1089 passed in 89.25s
```

Working tree after suite cleanup: **`RESULT.md` only**.

---

## Diff scope (intentional)

- `RESULT.md` (this file)

`core/tests/test_lululemon_benchmark.py`: no edit required (evidence captured from existing nodes).  
Production code, committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Closure note (does not rewrite the plan)

This child’s acceptance is **criterion-level evidence accounting**: every inventoried obligation now has PASS, PASS (historical), or explicit UNVERIFIED with the precise missing measurement.

Explicit UNVERIFIED retained (not invented):

- A2-ED — historical equity-detail at original liability defect (gate absent)
- B7-MID — gap aggregates during `MissingHistoricalValueError` stage
- A5 / B8 / E10 — parent Plan closure
- E11 — full-company workbook pretax parity (`interest_expense` blocker)

A complete ledger **does not** establish technical parent completion while those remain. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED**. Return to Plan for parent closure assessment. Any genuinely new child uses **9M.2.4.1.1.1.4**. Step 9 remains incomplete.
