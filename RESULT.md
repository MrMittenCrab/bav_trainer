# RESULT.md — Step 9M.2.4.1.1.1 Complete Criterion-Level Evidence Accounting

**Status:** COMPLETE (criterion-level evidence ledger complete; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `43d45b2f13e0891a94ae4f2fffbf160a6d5153c0` (plan commit; base `c4a09ed`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production changes. Diff scope: `RESULT.md` only.

---

## Withdrawal of unsupported prior COMPLETE claim

Prior `RESULT.md` at `c4a09ed` claimed **COMPLETE** for this evidence-accounting step while:

1. C5 “synthetic before/after” cited only current-code sparse nodes, not identified pre-repair vs repaired revision runs on the same fixture/assertion;
2. B3/E6 provenance lacked concrete selected / superseded / outside-axis row–period–amount–source records (hash-unchanged + suite green only);
3. non-balance-sheet omission safeguards were unitemized (“suite PASS”) without fixture/row/reason/assertion locations;
4. A2/E4 bundled implied-equity historical explanation with equity-detail without keeping gate-absent periods explicitly UNVERIFIED in dependent summaries;
5. suite totals / unchanged hashes / “prior child” references were treated as sufficient for obligations that require criterion-specific proof.

Those unsupported PASS/COMPLETE implications are **withdrawn**. This RESULT replaces them with criterion-split PASS / PASS (historical) / UNVERIFIED accounting, including freshly measured dual-reconcile, revision-overlay synthetic before/after, and itemized provenance / non-BS evidence.

Technical acceptance, evidence availability, and Plan-owned parent closure remain separate. A complete ledger does **not** close parents.

---

## Evidence classes (kept distinct)

| Class | Meaning |
|---|---|
| Fresh | Measured this run on HEAD `43d45b2` + committed artifacts |
| Historical | Traceable prior revision / RESULT with cited SHA |
| Diagnostic | Temporary reproduction under current code; not a substitute for historical gate semantics |
| Overlay | Same fixture/assertion run against identified production revision in isolated worktree |
| Unavailable | Required measurement cannot be obtained without inventing facts or unauthorized scope |

---

## Task 2 — Deterministic reconciliation (fresh)

Revision under test: `43d45b2`. Inputs: unmodified `benchmark/lululemon/extracted` + `benchmark/lululemon/source`. Outputs: isolated temp dirs only (`/tmp/lulu_reconcile_d5ommdw0/r1`, `.../r2`). No refresh of committed artifacts.

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
  --source-root benchmark/lululemon/source -o /tmp/lulu_reconcile_d5ommdw0/r1
→ exit 0; stdout: wrote three artifacts; overlap_conflicts=3

PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o /tmp/lulu_reconcile_d5ommdw0/r2
→ exit 0; stdout: wrote three artifacts; overlap_conflicts=3
```

### Generated vs committed artifact comparison

| Artifact | r1 SHA-256 | r2 SHA-256 | committed SHA-256 | Size | r1==r2 | r1==committed | Diff |
|---|---|---|---|---:|---|---|---|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | same | same | 22548 | yes | yes | none |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | same | same | 699401 | yes | yes | none |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | same | same | 4718 | yes | yes | none |

Committed bytes before = after both runs (verified). Suite-induced FR/DEMO mutations were reverted; final tree `RESULT.md` only.

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

Collective with integrity node: **18 passed in 3.31s** (17 reconcile + `test_four_period_reformulation_integrity`).

---

## Historical defect stages (distinct revisions)

| Stage | Code / RESULT revision | What changed | Integrity measurement available? |
|---|---|---|---|
| Original liability defect | `cdf0c9f` RESULT; standardized `ba1ba068…` size 22289 | NCIT omitted via `omitted_incomplete_axis` | Yes — liability + **implied-equity** gaps (equity-detail gate absent) |
| Sparse-value exception | `c50912c` RESULT (HEAD then `a370a02`) | NCIT retained with `None` @ 2026-02-01 | **No** — `MissingHistoricalValueError` before usable reformulation |
| Sparse liability gate | `17114fc` / plan `2e88322` | `None` non-contributing under A/L/(then implied) evidence gate | Yes — gaps 0.0; equity-detail column not yet separate |
| Equity-omission regression repair | `8c0098c` / plan `88ce931` | Independent equity-detail gate added | Yes — A/L/E-detail/implied all measured |

---

## Historical before / after gap tables

Tolerance **formula** (all stages): `max(1.0, 0.5 * (detail_count + 1))` (`DEFAULT_TOLERANCE=1.0`).

### BEFORE — original liability defect (`cdf0c9f` RESULT on committed pre-sparse standardized `ba1ba068…`)

Causal excluded row: `non_current_income_taxes_payable` / `Non-current income taxes payable`  
Selected source amounts: **28555 / 15864 / 0 / absent**; row absent from standardized (provenance `omitted_incomplete_axis`).

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---|---:|---:|---:|---|---:|
| 2023-01-29 | 0.0 | **−28555.0** | *gate did not exist* | **+28555.0** | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2024-01-28 | 0.0 | **−15864.0** | *gate did not exist* | **+15864.0** | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2025-02-02 | 0.0 | 0.0 | *gate did not exist* | 0.0 | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |
| 2026-02-01 | 0.0 | 0.0 | *gate did not exist* | 0.0 | 6.0 | 5.5 | **UNVERIFIED** | 11.0 |

- Counts then: assets **11** → 6.0; liabilities **10** (NCIT excluded) → 5.5; implied uses A+L=21 → 11.0.  
- Resolved totals existed (`Total assets` / `Total liabilities` / `Total stockholders' equity`); classified liability sum short by exactly the NCIT amounts; **cdf0c9f “equity gap” = implied-equity**, not equity-detail.  
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

Resolved totals (fresh via `reformulate_balance_sheet`):

| Period | total_assets | total_liabilities | total_equity (category Equity) |
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

---

## Synthetic before / after on identified revisions (overlay)

Same fixture + acceptance assertion; production code from cited revision; tests overlaid from the repaired revision in isolated `git worktree` (temp only).

| Regression | Fixture / assertion | Pre-repair prod | Observed before | Repaired prod | Observed after |
|---|---|---|---|---|---|
| Sparse standardization | `test_standardize_retains_sparse_balance_sheet_facts` | `cdf0c9f` | **FAIL** `KeyError: 'sparse_trailing'` (row omitted) exit 1 | `c50912c` | **PASS** exit 0 |
| Eligible sparse aggregation | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes` (3 params) | `c50912c` | **FAIL** `MissingHistoricalValueError` for modeled period with `None` (3/3) exit 1 | `17114fc` | **PASS** 3/3 exit 0 |
| 100 equity omission despite zero identity gaps | `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | `17114fc` | **FAIL** `DID NOT RAISE MissingHistoricalValueError` (omission accepted) exit 1 | `8c0098c` | **PASS** exit 0 |

Unrelated setup failures were not used as before-failure proof.

---

## Provenance observations (NCIT; committed `provenance.json`)

Artifact: `benchmark/lululemon/reconciled/provenance.json` SHA-256 `a31f7b05…` (unchanged).

**Row-level retained sparse**

- `retained_sparse_axis`: concept `non_current_income_taxes_payable`; label `Non-current income taxes payable`; `available_periods=["2023-01-29","2024-01-28","2025-02-02"]`; `missing_periods=["2026-02-01"]`; not in `omitted_incomplete_axis`.

**Period-level BS NCIT (selection disposition)**

Committed provenance has **no** value-level `status="superseded"` keys (global status counts: selected 327, outside_model_axis 141, omitted_incomplete_axis 22, missing_period 1). Non-selected agreeing observations remain in `observations[]` beside the `selected` payload.

| Period | status | selected amount | selected source | non-selected (superseded-agreeing) obs |
|---|---|---:|---|---|
| 2022-01-30 | `outside_model_axis` | 38074 | FY2022 comparative p49 `LULU_FY2022_Annual_Report.pdf` | (single obs) |
| 2023-01-29 | `selected` | 28555 | FY2023 comparative p55 `LULU_FY2023…` | FY2022 current_period p49 value 28555 `LULU_FY2022…` |
| 2024-01-28 | `selected` | 15864 | FY2024 comparative p50 `LULU_FY2024…` | FY2023 current_period p55 value 15864 `LULU_FY2023…` |
| 2025-02-02 | `selected` | 0 | FY2024 current_period p50 `LULU_FY2024…` | (single obs) |
| 2026-02-01 | `missing_period` | — | — | n_obs=0 |

Node: `test_non_current_income_taxes_payable_restored_sparse_axis` **PASS**.  
Synthetic sparse provenance: `test_standardize_retains_sparse_balance_sheet_facts` asserts `missing_period` vs `selected` zero, retained_sparse set, IS omission.

---

## Sparse position / zero / complete-row / export-reload (criterion-specific)

| Case | Node | Outcome |
|---|---|---|
| Leading / trailing / both eligible absence | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes[...]` | **PASS** |
| Interior absence + neighboring reported zero | `test_sparse_interior_absence_with_neighboring_reported_zero` | **PASS** |
| Complete rows with sparse neighbor | `test_complete_rows_unchanged_with_sparse_neighbor` | **PASS** |
| Latest-available label/concept + export/reload identity | `test_standardize_retains_sparse_balance_sheet_facts` (assert label/concept; `standardized_to_payload` / `from_payload`) | **PASS** |
| Reported zero ≠ `None` (Lululemon) | `test_four_period_reformulation_integrity` NCIT 0.0 @ 2025-02-02 / `None` @ 2026-02-01 | **PASS** |

---

## Non-balance-sheet incompleteness (itemized; unchanged)

| Fixture | Omitted row | Reason | Assertion location |
|---|---|---|---|
| `test_standardize_complete_axis_and_omission` | IS `only_2025` (concept in `row_identity`) | incomplete model axis → `omitted_incomplete_axis` | provenance assert `status==omitted_incomplete_axis` and `"only_2025" in row_identity`; IS retains only complete `revenue` |
| `test_standardize_retains_sparse_balance_sheet_facts` | IS `only_is_2025` | incomplete axis non-BS omitted while sparse BS retained | `assert all(item.concept != "only_is_2025" for item in fin.income_statement)` + provenance `omitted_incomplete_axis` contains `only_is_2025` |

No production change; focused coverage already present — no new test required.

---

## Task 1 — Criterion-level acceptance ledger

Statuses: **PASS** = fresh this run; **PASS (historical)** = cited prior revision + reconfirmed where live; **PASS (overlay)** = revision-overlay before/after; **UNVERIFIED** = missing measurement or Plan-only closure.

### From `aa6adc1` (9M.2.4 — Lululemon Liability-Detail Reformulation Integrity)

| # | Criterion (retained wording) | Evidence | Status |
|---|---|---|---|
| A1 | All four periods pass `check_reformulation_integrity` within unchanged tolerance rules | Fresh gaps all 0.0; envelopes above; `test_four_period_reformulation_integrity` | **PASS** |
| A2 | Recorded liability and corresponding equity discrepancies explained and repaired with causal rows | Historical before `cdf0c9f`: liability −28555/−15864 and **implied-equity** +28555/+15864; causal NCIT; live after all 0.0 | **PASS (historical before + live after)** — equity here = implied-equity |
| A2-ED | Historical equity-**detail** gaps at original defect | Equity-detail gate did not exist at `cdf0c9f` | **UNVERIFIED** |
| A3 | Temp-dir Lululemon build: success or exact next exception | `MissingLineError: Required concept 'interest_expense' not found in statement lines` (`test_four_period_reformulation_integrity`) | **PASS** (recorded; not a success gate) |
| A4 | Genuine inconsistencies fail closed; artifacts unchanged | Equal-omission / rounding / immutability nodes; Lululemon hashes unchanged | **PASS** |
| A5 | Parent 9M.2.4 closed for Plan | Requires Plan assessment of every original criterion | **UNVERIFIED** |

### From `a370a02` (9M.2.4.1 — Preserve Sparse Liability Facts)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| B1 | NCIT sparse series 28555 / 15864 / reported 0 / `None` | Live standardized + `test_non_current_income_taxes_payable_restored_sparse_axis` | **PASS** |
| B2 | Sparse absence ≠ reported zero through standardization / export-reload | Sparse nodes + NCIT provenance `retained_sparse_axis` / `missing_period` | **PASS** |
| B3 | Provenance preserves selected/superseded/outside-axis; no invented facts | Concrete NCIT table above; no fabricated values; hash unchanged | **PASS** |
| B4 | Failure-path immutability | Subprocess / comparison / mutation / drift nodes above (17) | **PASS** |
| B5 | Common stock 611 / 606 / 581 / 557 | Live values + `test_common_stock_classifies_across_all_periods` / integrity test | **PASS** |
| B6 | Dual reconcile identical to committed; conflicts stable | Fresh dual-run table | **PASS** |
| B7 | Four-period integrity after sparse retention (parent mandatory) | Blocked at `c50912c` by `MissingHistoricalValueError`; later restored at `17114fc`+ | **PASS (historical exception + live after)** |
| B7-MID | Gap aggregates during MissingHistoricalValueError stage | Unavailable — no usable reformulation | **UNVERIFIED** |
| B8 | Parent 9M.2.4.1 closed | Plan closure pending | **UNVERIFIED** |

### From `2e88322` (9M.2.4.1.1 — Evidence-Grounded Sparse-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| C1 | Independent asset/liability evidence gates before usable sparse results | `test_sparse_absence_fails_without_independent_totals`, `..._when_total_row_null`, `..._on_contradictory_gap` | **PASS** |
| C2 | Leading/interior/trailing absence, zero, complete-row coverage | Sparse position nodes above | **PASS** |
| C3 | Missing keys / contradictory / equal omissions / rounding boundaries | `test_sparse_missing_key_still_fails_closed`, `test_reformulation_detects_equal_asset_liability_omissions`, rounding accept/reject nodes | **PASS** |
| C4 | Four-period Lululemon integrity after sparse repair | Same as A1 | **PASS** |
| C5 | Synthetic before-failure / after-success for sparse eligibility | Overlay table: sparse_std + sparse_agg before FAIL / after PASS | **PASS (overlay)** |

### From `88ce931` (9M.2.4.1.1 — Repair Sparse Equity-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| D1 | Sparse equity omission fails despite zero implied-equity gaps | Overlay: before `17114fc` DID NOT RAISE; after `8c0098c` PASS; live `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | **PASS (overlay + live)** |
| D2 | Signed contra-equity; subtotal exclusion; override controls | `test_sparse_equity_signed_contra_equity_contributes`, `..._subtotal_excluded_from_detail`, `..._explicit_override_controls_detail` | **PASS** |
| D3 | Equity missing keys / unavailable totals / envelope boundaries | `test_sparse_equity_missing_key_fails_closed`, `..._unavailable_total_fails_closed`, at/beyond envelope nodes | **PASS** |
| D4 | Implied-equity remains separate from equity-detail gate | Test design + Lululemon implied env 11.5 vs E-detail env 2.5 | **PASS** |

### From `a62893f` / `0f1d2c3` / current step obligations

| # | Criterion | Evidence | Status |
|---|---|---|---|
| E1 | All 12 pretax/ETR matrix cases | `test_pretax_etr_parity_coverage_matrix[...]` — 12/12 **PASS** (fresh) | **PASS** |
| E2 | Header corruption + link/arithmetic rejection (formula inspection, not Excel recalc) | `test_pretax_parity_rejects_corrupted_period_headers`, `..._corrupted_source_links_and_etr` | **PASS** |
| E3 | Zero-pretax + alias-removal retained | `test_pretax_parity_zero_denominator_emitted_arithmetic`, `test_pretax_parity_detects_alias_removal` | **PASS** |
| E4 | Four-period integrity + causal liability/equity explanation | A1 + A2 (implied-equity); A2-ED remains UNVERIFIED | **PASS** with A2-ED caveat |
| E5 | Asset/liability/signed equity-detail gates; fail-closed | C*/D* | **PASS** |
| E6 | Sparse ≠ zero; provenance preserved | B2–B3 concrete table | **PASS** |
| E7 | NCIT / Common stock / G1–G2–G3 / empty unclassified | NCIT+CS live; gift-card/PPE/common-stock nodes; integrity asserts empty unclassified | **PASS** |
| E8 | Required suites; deterministic artifact comparisons; failure-path immutability | Suites below + reconcile 17 | **PASS** |
| E9 | Dual-reconcile criterion-level evidence supplied | Task 2 tables | **PASS** |
| E10 | Every parent original criterion closed | A5 / B8 | **UNVERIFIED** — parents stay UNRESOLVED |
| E11 | Full-company Python↔Excel pretax parity on unmodified Lululemon | Workbook blocked by `interest_expense` | **UNVERIFIED / unavailable** |
| E12 (`0f1d2c3`) | Criterion-split ledger with revision/artifact/command/outcome | This RESULT | **PASS** |
| E13 (`0f1d2c3`) | Synthetic before/after + historical stages distinguished from diagnostics | Overlay + stage tables | **PASS** |
| E14 (`0f1d2c3`) | Itemized non-BS omission evidence | Non-BS table | **PASS** |

Matrix IDs (fresh): `alias|canon|label` × `natural|reorder` × `original|reload` — all **PASS**.

---

## Workbook probe (unmodified input, temporary directory)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Recorded only; **not repaired**. Workbook success is **not** an original parent acceptance requirement. Synthetic parity / real-company resolution / unavailable full-company parity kept separate (E11).

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
  core/tests/test_lululemon_benchmark.py::test_reconcile_drift_is_detected_without_rewriting_expected \
  core/tests/test_lululemon_benchmark.py::test_four_period_reformulation_integrity -v
→ 18 passed in 3.31s

PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k 'pretax_etr_parity_coverage_matrix or pretax_parity_rejects_corrupted or pretax_parity_zero or pretax_parity_detects_alias' -v
→ 16 passed, 51 deselected in 1.67s

PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 537 passed in 11.40s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 28.33s

PYTHONPATH=. pytest core/tests -q
→ 1089 passed in 90.26s
```

Working tree after suite cleanup: **`RESULT.md` only**.

---

## Diff scope (intentional)

- `RESULT.md` (this file)

No edits to `core/tests/test_filing_reconciler.py`, `core/tests/test_classification.py`, or `core/tests/test_lululemon_benchmark.py` (existing nodes suffice).  
Production code, committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Closure note (does not rewrite the plan)

This child’s acceptance is **criterion-level evidence accounting**: inventoried obligations from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, `a62893f`, and `0f1d2c3` now have supported PASS / PASS (historical|overlay) or explicit UNVERIFIED with the precise missing measurement.

Explicit UNVERIFIED retained (not invented):

- A2-ED — historical equity-detail at original liability defect (gate absent)
- B7-MID — gap aggregates during `MissingHistoricalValueError` stage
- A5 / B8 / E10 — parent Plan closure
- E11 — full-company workbook pretax parity (`interest_expense` blocker)

A complete ledger **does not** establish technical parent completion while those remain. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED**. Return to Plan for parent closure assessment. Any genuinely new child uses **9M.2.4.1.1.1.5**. Step 9 remains incomplete.
