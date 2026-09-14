# RESULT.md — Step 9M.2.4.1.1.1 Restore Criterion-Specific Evidence and Original Acceptance

**Status:** COMPLETE (criterion-specific evidence restored; isolated verification preserved; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Restore Criterion-Specific Evidence and Original Acceptance  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Base:** `470aa43533c32bbf696aad254a03f155dc2ea6a8`  
**Verified code revision (isolated runs):** `590c73a4eba8ee2901687f8f2d03e63aacc865bd`  
**Workspace HEAD:** `d80d03a3ad83b8a854ae0785d79c136744be3c4d` (plan-only delta vs base: `IMPLEMENTATION.md`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged by this run).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production or test changes. Authoritative diff scope: `RESULT.md` only.

Technical acceptance, evidence availability, and Plan-owned closure remain separate. A complete ledger does **not** close parents while A5 / B8 / E10 (and other explicit UNVERIFIED items) remain.

---

## Withdrawal / restore scope

Compared `470aa435^:RESULT.md` (Complete Criterion-Level Evidence Accounting; also at `590c73a`) with the reviewed abbreviated RESULT after `470aa435`.

**Restored** (deleted criterion-specific evidence; retained as historical/overlay/isolated as classified below — not relabeled as fresh):

- four-period before/after resolved totals, A/L/E-detail/implied gaps, detail counts, tolerance formulas/envelopes, causal NCIT identities/amounts;
- NCIT row/period/amount/source/page/disposition records; sparse-position / zero / complete-row / export-reload locations; non-BS assertion locations;
- synthetic before/after overlay exits; reconcile failure-path node table; 12 pretax/ETR individual IDs; exact safeguard node names;
- exact criterion wording mapped from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, `a62893f`, `0f1d2c3`, `b5a33cd`.

**Not reinstated:**

- unsupported COMPLETE claims that treated non-isolated suite runs or restore-after-write as immutability proof;
- any claim that gate-absent historical equity-detail or MissingHistoricalValueError-stage aggregates are now measured.

**Preserved** from the isolation repair RESULT: protected disposable-copy suite/probe measurements, auth aggregate hash guards, dual-reconcile isolated hashes, and withdrawal of non-isolated suite counts as immutability proof.

### Numbering

- Retain detailed step ID: **9M.2.4.1.1.1**.
- Do **not** renumber historical work.
- Proposed exhausted children through **`9M.2.4.1.1.1.6`** are withdrawn for new work.
- First available ID for genuinely new bounded work: **`9M.2.4.1.1.1.7`** (only after original acceptance passes and Plan assesses closure).

---

## Evidence classes (kept distinct)

| Class | Meaning |
|---|---|
| Isolated / fresh | Measured under protected disposable copies at revision `590c73a` (Task 2–3 of isolation repair); authoritative files hash-guarded |
| Historical | Traceable prior revision / RESULT with cited SHA; verified against cited record this restore — **not** a fresh re-measurement |
| Diagnostic | Temporary reproduction under later code; not a substitute for historical gate semantics |
| Overlay | Same fixture/assertion run against identified production revision in isolated worktree (cited RESULT) |
| Unavailable | Required measurement cannot be obtained without inventing facts or unauthorized scope |

---

## Task 2–3 — Artifact-protecting isolation (preserved; not re-run)

| Field | Value |
|---|---|
| Verified revision copied | `590c73a4eba8ee2901687f8f2d03e63aacc865bd` |
| Copy method | `git archive <rev> \| tar -x` into three independent temp roots; symlink count 0; shared-inode hardlink break check ran (0 rewrites needed) |
| Isolation base | `/var/folders/m2/14fn3yz12j3f6yknz7_3cmw80000gn/T/bav_9m241111_iso_5qp50x15` |
| Suite roots | `…/focused`, `…/fr`, `…/full` (separate disposable trees) |
| Probe root | `…/probes/probe_copy` (fourth independent archive extract) |
| Protection | Suites execute only under isolated `cwd` + `PYTHONPATH=<iso root>`; authoritative tracked files (all except authorized `RESULT.md` update) SHA-256 hashed before and after **each** suite; immutability judged by hash equality, **not** restoration |

### Baseline input/artifact manifests (each iso copy, pre-execution)

| Path | SHA-256 | Size |
|---|---|---:|
| `benchmark/lululemon/reconciled/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `benchmark/lululemon/reconciled/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `benchmark/fast_retailing/reconciled/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `benchmark/fast_retailing/reconciled/provenance.json` | `fd5a1ec87b61c4835d3b7bfda79996afa6c5ed9bbf2082e35413fb18ee696f1f` | 874954 |
| `benchmark/fast_retailing/reconciled/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |
| `example/DEMO_HK_Trainer.xlsx` | `2f3f771d13c9b143961adf7f892d085b0dda4f1a9aae71cfbb50e2e42bd099ef` | 26790 |
| `example/DEMO_HK_Answer_Key.xlsx` | `ae6df2406b7a40082d1ea8f73a73f6f6a05c12a7281a5077bda453f71dd98309` | 84370 |

Authoritative aggregate SHA-256 over 221 tracked files excluding `RESULT.md` (stable across all suite boundaries):  
`b1123a35b87a25e8c1552502fbe17e3628c183037c919c3e1c9f540e4825f0a1`

### Required suites (isolated) — preserved measurements

Prior non-isolated suite counts are **withdrawn** as immutability proof (historical observation only):

```text
(historical, non-isolated) focused → 537 passed in 11.40s
(historical, non-isolated) FR      → 132 passed in 28.33s
(historical, non-isolated) full     → 1089 passed in 90.26s
```

| Suite | Execution root | Exact command | Exit | Counts | Auth immutable? | Isolated artifact changes |
|---|---|---|---:|---|---|---|
| focused | `…/focused` | `cd <focused> && PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q` | 0 | **537 passed in 11.47s** | yes (agg unchanged) | none |
| FR | `…/fr` | `cd <fr> && PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` | 0 | **132 passed in 28.15s** | yes | `benchmark/fast_retailing/reconciled/provenance.json` `fd5a1ec8…` → `26d9a170…` (size 874954 → 875119) |
| full | `…/full` | `cd <full> && PYTHONPATH=. pytest core/tests -q` | 0 | **1089 passed in 90.64s** | yes | FR provenance same refresh; `example/DEMO_HK_Trainer.xlsx` `2f3f771d…` → `e7448153…` (size unchanged 26790) |

### Dual reconciliation (isolated probe copy) — preserved

Inputs unmodified under `…/probes/probe_copy`. Outputs only under `…/probes/reconcile_r{1,2}`.

```text
cd <probe_copy> && PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o <probes>/reconcile_r1
→ exit 0; overlap_conflicts=3

cd <probe_copy> && PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o <probes>/reconcile_r2
→ exit 0; overlap_conflicts=3
```

| Artifact | r1 SHA-256 | r2 | committed | Size | r1==r2 | r1==committed | Diff |
|---|---|---|---|---:|---|---|---|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | same | same | 22548 | yes | yes | none |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | same | same | 699401 | yes | yes | none |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | same | same | 4718 | yes | yes | none |

### Reconcile / integrity / pretax nodes (isolated) — preserved + restored itemization

```text
cd <probe_copy> && PYTHONPATH=. pytest \
  core/tests/test_lululemon_benchmark.py::test_generic_reconcile_is_deterministic \
  …::test_reconcile_immutability_verified_after_subprocess_failure \
  …::test_reconcile_immutability_verified_after_comparison_failure \
  …::test_reconcile_immutability_guard_detects_temp_mutation \
  …::test_reconcile_drift_is_detected_without_rewriting_expected \
  …::test_four_period_reformulation_integrity -v
→ 18 passed in 3.06s

cd <probe_copy> && PYTHONPATH=. pytest \
  core/tests/test_reference_integrity.py::test_pretax_etr_parity_coverage_matrix \
  …::test_pretax_parity_rejects_corrupted_period_headers \
  …::test_pretax_parity_rejects_corrupted_source_links_and_etr \
  …::test_pretax_parity_zero_denominator_emitted_arithmetic \
  …::test_pretax_parity_detects_alias_removal -v
→ 16 passed in 1.70s
  (formula inspection / reference evaluation — not Excel recalculation)
```

| Node | Params | Outcome (isolated group) |
|---|---|---|
| `test_generic_reconcile_is_deterministic` | — | **PASS** |
| `test_reconcile_immutability_verified_after_subprocess_failure` | `fail_pass=1` | **PASS** |
| `test_reconcile_immutability_verified_after_subprocess_failure` | `fail_pass=2` | **PASS** |
| `test_reconcile_immutability_verified_after_comparison_failure` | `fail_at=inter_run` | **PASS** |
| `test_reconcile_immutability_verified_after_comparison_failure` | `fail_at=baseline` | **PASS** |
| `test_reconcile_immutability_guard_detects_temp_mutation` | 3 artifacts × {pass1, inter_run, baseline} = 9 | **PASS** (9/9) |
| `test_reconcile_drift_is_detected_without_rewriting_expected` | each of 3 artifacts | **PASS** (3/3) |
| `test_four_period_reformulation_integrity` | — | **PASS** |

Collective: **18** = 17 reconcile/immutability + integrity.

### Live integrity + preserved series (isolated, committed standardized)

`check_reformulation_integrity(reform, EXPECTED_PERIODS)` → **PASS**.  
Gaps: asset/liability/equity_detail all `(0,0,0,0)`; `equity_gap` `(0,0,0,0)`.

| Period | total_assets | total_liabilities | reported_equity / implied_equity |
|---|---:|---:|---:|
| 2023-01-29 | 5607038.0 | 2458239.0 | 3148799.0 |
| 2024-01-28 | 7091941.0 | 2859860.0 | 4232081.0 |
| 2025-02-02 | 7603292.0 | 3279245.0 | 4324047.0 |
| 2026-02-01 | 8456743.0 | 3494903.0 | 4961840.0 |

NCIT (committed standardized, reconfirmed this restore): **28555 / 15864 / 0.0 / `None`**.  
Common stock: **611 / 606 / 581 / 557**.

Artifact hashes reconfirmed this restore (read-only): standardized / provenance / conflicts match the baseline table above.

### Lululemon workbook probe (unmodified input, isolated)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Recorded only; not repaired. Synthetic parity / real-company resolution / unavailable full-company Python↔Excel pretax parity kept separate (E11).

### Lululemon source input hashes (probe copy)

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

---

## Historical defect stages (distinct revisions)

| Stage | Code / RESULT revision | What changed | Integrity measurement available? |
|---|---|---|---|
| Original liability defect | `cdf0c9f` RESULT; standardized `ba1ba068…` size 22289 | NCIT omitted via `omitted_incomplete_axis` | Yes — liability + **implied-equity** gaps (equity-detail gate absent) |
| Sparse-value exception | `c50912c` RESULT (HEAD then `a370a02`) | NCIT retained with `None` @ 2026-02-01 | **No** — `MissingHistoricalValueError` before usable reformulation |
| Sparse liability gate | `17114fc` / plan `2e88322` | `None` non-contributing under A/L/(then implied) evidence gate | Yes — gaps 0.0; equity-detail column not yet separate |
| Equity-omission regression repair | `8c0098c` / plan `88ce931` | Independent equity-detail gate added | Yes — A/L/E-detail/implied all measured |

Keep original liability defect, sparse-value exception, and equity-omission regression **distinct**.

---

## Historical before / after gap tables (restored; not fresh)

Tolerance **formula** (all stages): `max(1.0, 0.5 * (detail_count + 1))` (`DEFAULT_TOLERANCE=1.0`).

Verified against cited records: pre-repair A/L counts **11/10** → envelopes **6.0/5.5**, implied **11.0**; repaired A/L/E-detail counts **11/11/4** → envelopes **6.0/6.0/2.5**, implied **11.5** (`cdf0c9f`, `c50912c`, `17114fc`, `8c0098c`, `470aa435^` RESULT).

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
- Equity-detail aggregate: **UNVERIFIED** at this stage (independent equity-detail gate introduced only in `8c0098c` / `88ce931`). Do not infer historical equity-detail from current diagnostics.

**Diagnostic probe only** (temp copy of `ba1ba068…` under later code): liability-detail (−28555, −15864, 0, 0); implied-equity (+28555, +15864, 0, 0); equity-detail (0,0,0,0); envelopes L=5.5 / implied=11. Matches historical liability + implied measurements; **not** used as historical equity-detail evidence.

### Intermediate — sparse retention before nullable aggregation (`c50912c`)

After NCIT restored as **28555 / 15864 / 0.0 / `None`**, reformulation raised:

```text
MissingHistoricalValueError: ... Non-current income taxes payable ...
has no supplied value for modeled period 2026-02-01
```

Four-period before/after **gap aggregates for this stage: UNVERIFIED / unavailable** as live integrity measurements (gate/aggregation did not return usable reformulation). Exception text is the recorded historical outcome. Current diagnostics cannot replace them.

### AFTER — repaired committed standardized (isolated live; envelopes historical+live)

Included causal row NCIT: **28555 / 15864 / 0.0 / `None`** (FY2026 `None` non-contributing; FY2025 reported 0 contributing).  
Common stock: **611 / 606 / 581 / 557**.

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts now: assets **11** → 6.0; liabilities **11** → 6.0; equity detail **4** → 2.5; implied A+L=22 → 11.5.  
- `check_reformulation_integrity` → **PASS** all four periods (isolated).  
- Node: `test_four_period_reformulation_integrity` **PASS**.

---

## Synthetic before / after on identified revisions (overlay; restored)

Same fixture + acceptance assertion; production code from cited revision; tests overlaid from the repaired revision in isolated `git worktree` (temp only). Source: `470aa435^` / `590c73a` RESULT.

| Regression | Fixture / assertion | Pre-repair prod | Observed before | Repaired prod | Observed after |
|---|---|---|---|---|---|
| Sparse standardization | `test_standardize_retains_sparse_balance_sheet_facts` (`core/tests/test_filing_reconciler.py`) | `cdf0c9f` | **FAIL** `KeyError: 'sparse_trailing'` (row omitted) exit 1 | `c50912c` | **PASS** exit 0 |
| Eligible sparse aggregation | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes` (3 params) | `c50912c` | **FAIL** `MissingHistoricalValueError` for modeled period with `None` (3/3) exit 1 | `17114fc` | **PASS** 3/3 exit 0 |
| Equity omission despite zero identity gaps | `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | `17114fc` | **FAIL** `DID NOT RAISE MissingHistoricalValueError` (omission accepted) exit 1 | `8c0098c` | **PASS** exit 0 |

Unrelated setup failures were not used as before-failure proof.

---

## Provenance observations (NCIT; committed `provenance.json`) — restored itemization

Artifact: `benchmark/lululemon/reconciled/provenance.json` SHA-256 `a31f7b05…` (reconfirmed this restore).

**Row-level retained sparse**

- `retained_sparse_axis`: concept `non_current_income_taxes_payable`; label `Non-current income taxes payable`; `available_periods=["2023-01-29","2024-01-28","2025-02-02"]`; `missing_periods=["2026-02-01"]`; not in `omitted_incomplete_axis`.

**Period-level BS NCIT (selection disposition)**

Committed provenance has **no** value-level `status="superseded"` keys. Global **values** status counts (reconfirmed): selected 327, outside_model_axis 141, omitted_incomplete_axis 22, missing_period 1. Non-selected agreeing observations remain in `observations[]` beside the `selected` payload — **retained observations**, not an actual `superseded` status.

| Period | status | selected amount | selected source | non-selected (agreeing) obs |
|---|---|---:|---|---|
| 2022-01-30 | `outside_model_axis` | 38074 | FY2022 comparative p49 `LULU_FY2022_Annual_Report.pdf` | (single obs) |
| 2023-01-29 | `selected` | 28555 | FY2023 comparative p55 `LULU_FY2023…` | FY2022 current_period p49 value 28555 `LULU_FY2022…` |
| 2024-01-28 | `selected` | 15864 | FY2024 comparative p50 `LULU_FY2024…` | FY2023 current_period p55 value 15864 `LULU_FY2023…` |
| 2025-02-02 | `selected` | 0 | FY2024 current_period p50 `LULU_FY2024…` | (single obs) |
| 2026-02-01 | `missing_period` | — | — | n_obs=0 |

Node: `test_non_current_income_taxes_payable_restored_sparse_axis` **PASS** (in isolated focused suite).  
Synthetic sparse provenance: `test_standardize_retains_sparse_balance_sheet_facts` asserts `missing_period` vs `selected` zero, retained_sparse set, IS omission.

---

## Sparse position / zero / complete-row / export-reload (criterion-specific)

| Case | Node | Outcome |
|---|---|---|
| Leading / trailing / both eligible absence | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes[...]` | **PASS** (isolated focused) |
| Interior absence + neighboring reported zero | `test_sparse_interior_absence_with_neighboring_reported_zero` | **PASS** |
| Complete rows with sparse neighbor | `test_complete_rows_unchanged_with_sparse_neighbor` | **PASS** |
| Latest-available label/concept + export/reload identity | `test_standardize_retains_sparse_balance_sheet_facts` (assert label/concept; `standardized_to_payload` / `from_payload`) | **PASS** |
| Reported zero ≠ `None` (Lululemon) | `test_four_period_reformulation_integrity` NCIT 0.0 @ 2025-02-02 / `None` @ 2026-02-01 | **PASS** |
| Nullable export/reload contract | same standardize fixture + payload round-trip asserts | **PASS** |

---

## Inherited safeguard nodes (exact locations)

| Obligation | Exact node(s) | Outcome |
|---|---|---|
| Independent totals missing | `test_sparse_absence_fails_without_independent_totals`, `test_sparse_absence_fails_when_total_row_null` | **PASS** |
| Contradictory gap | `test_sparse_absence_fails_on_contradictory_gap` | **PASS** |
| Missing keys | `test_sparse_missing_key_still_fails_closed`, `test_sparse_equity_missing_key_fails_closed` | **PASS** |
| Equal asset/liability omissions | `test_reformulation_detects_equal_asset_liability_omissions` | **PASS** |
| Rounding boundaries (A/L/E) | `test_reformulation_integrity_accepts_count_bounded_{asset,liability,equity}_rounding_envelope`; `…_rejects_…_gap_above_rounding_envelope` | **PASS** |
| Equity envelope at/beyond | `test_sparse_equity_detail_gap_at_rounding_envelope_passes`, `test_sparse_equity_detail_gap_beyond_rounding_envelope_fails` | **PASS** |
| Unavailable equity total | `test_sparse_equity_unavailable_total_fails_closed` | **PASS** |
| Contra-equity | `test_sparse_equity_signed_contra_equity_contributes` | **PASS** |
| Subtotal exclusion | `test_sparse_equity_subtotal_excluded_from_detail` | **PASS** |
| Explicit override | `test_sparse_equity_explicit_override_controls_detail` | **PASS** |
| Empty unclassified detail (G3 path) | `test_four_period_reformulation_integrity` asserts empty unclassified non-subtotal BS detail | **PASS** |
| G1 gift-card | `test_gift_card_liability_classifies_across_all_periods` | **PASS** |
| G2 PPE | `test_ppe_classifies_resolves_and_enables_fixed_asset` | **PASS** |
| G3 common stock | `test_common_stock_classifies_across_all_periods` | **PASS** |

All covered by isolated focused suite **537 passed**.

---

## Non-balance-sheet incompleteness (itemized; restored)

| Fixture | Omitted row | Reason | Assertion location |
|---|---|---|---|
| `test_standardize_complete_axis_and_omission` | IS `only_2025` (concept in `row_identity`) | incomplete model axis → `omitted_incomplete_axis` | provenance assert `status==omitted_incomplete_axis` and `"only_2025" in row_identity`; IS retains only complete `revenue` |
| `test_standardize_retains_sparse_balance_sheet_facts` | IS `only_is_2025` | incomplete axis non-BS omitted while sparse BS retained | `assert all(item.concept != "only_is_2025" for item in fin.income_statement)` + provenance `omitted_incomplete_axis` contains `only_is_2025` |

---

## Pretax / ETR matrix and mutation controls (restored individual outcomes)

Parameter axes (historical `7303db2` RESULT; reconfirmed by isolated 16-pass pretax group — not Excel recalculation):

| Axis | Values |
|---|---|
| Concept mode | canonical `pretax_income` / alias `income_before_tax` / normalized label fallback (`concept=""`) |
| Source-row order | natural / reordered |
| Input mode | original fixture / standardized export→reload |

| Test ID | Outcome |
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

Node: `core/tests/test_reference_integrity.py::test_pretax_etr_parity_coverage_matrix[...]` — **12/12**.

| Mutation control | Node | Outcome |
|---|---|---|
| Saved/reloaded header mutations | `test_pretax_parity_rejects_corrupted_period_headers` | **PASS** |
| Source-link / arithmetic mutations | `test_pretax_parity_rejects_corrupted_source_links_and_etr` | **PASS** |
| Zero-pretax behavior | `test_pretax_parity_zero_denominator_emitted_arithmetic` | **PASS** |
| Alias-removal / resolver safeguard | `test_pretax_parity_detects_alias_removal` | **PASS** |

---

## Task 1 — Criterion-level acceptance ledger (restored wording + reassessment)

Statuses: **PASS** = isolated measurement on `590c73a` and/or reconfirmed committed artifacts this restore; **PASS (historical|overlay)** = cited prior revision; **UNVERIFIED** = missing measurement or Plan-only closure.  
Reassessed especially A2, B2–B3, C2–C5, D2–D4, E4–E7, E12–E14 after restoring criterion-specific evidence. Bundled obligations remain split where evidence differs.

### From `aa6adc1` (9M.2.4 — Lululemon Liability-Detail Reformulation Integrity)

| # | Criterion (retained wording) | Evidence | Status |
|---|---|---|---|
| A1 | All four periods pass `check_reformulation_integrity` within unchanged tolerance rules | Isolated gaps all 0.0; envelopes above; `test_four_period_reformulation_integrity` | **PASS** |
| A2 | Recorded liability and corresponding equity discrepancies explained and repaired with causal rows | Historical before `cdf0c9f`: liability −28555/−15864 and **implied-equity** +28555/+15864; causal NCIT; live after all 0.0 | **PASS (historical before + live after)** — equity here = implied-equity |
| A2-ED | Historical equity-**detail** gaps at original defect | Equity-detail gate did not exist at `cdf0c9f` | **UNVERIFIED** |
| A3 | Temp-dir Lululemon build: success or exact next exception | `MissingLineError: Required concept 'interest_expense' not found in statement lines` (isolated probe) | **PASS** (recorded; not a success gate) |
| A4 | Genuine inconsistencies fail closed; artifacts unchanged | Isolated immutability nodes + auth aggregate unchanged across suites (not restore-based) | **PASS** |
| A5 | Parent 9M.2.4 closed for Plan | Requires Plan assessment of every original criterion | **UNVERIFIED** |

### From `a370a02` (9M.2.4.1 — Preserve Sparse Liability Facts)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| B1 | NCIT sparse series 28555 / 15864 / reported 0 / `None` | Isolated live + committed standardized reconfirm + `test_non_current_income_taxes_payable_restored_sparse_axis` | **PASS** |
| B2 | Sparse absence ≠ reported zero through standardization / export-reload | Sparse position table + NCIT provenance `retained_sparse_axis` / `missing_period` vs reported 0 | **PASS** |
| B3 | Provenance preserves selected/superseded/outside-axis; no invented facts | Concrete NCIT table; no `superseded` status keys — agreeing obs retained in `observations[]`; hash unchanged | **PASS** |
| B4 | Failure-path immutability | Isolated subprocess / comparison / mutation / drift nodes (17) | **PASS** |
| B5 | Common stock 611 / 606 / 581 / 557 | Isolated live + `test_common_stock_classifies_across_all_periods` | **PASS** |
| B6 | Dual reconcile identical to committed; conflicts stable | Isolated dual-run full hash table | **PASS** |
| B7 | Four-period integrity after sparse retention (parent mandatory) | Blocked at `c50912c` by `MissingHistoricalValueError`; later restored at `17114fc`+; live PASS | **PASS (historical exception + live after)** |
| B7-MID | Gap aggregates during MissingHistoricalValueError stage | Unavailable — no usable reformulation | **UNVERIFIED** |
| B8 | Parent 9M.2.4.1 closed | Plan closure pending | **UNVERIFIED** |

### From `2e88322` (9M.2.4.1.1 — Evidence-Grounded Sparse-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| C1 | Independent asset/liability evidence gates before usable sparse results | `test_sparse_absence_fails_without_independent_totals`, `…_when_total_row_null`, `…_on_contradictory_gap` | **PASS** |
| C2 | Leading/interior/trailing absence, zero, complete-row coverage | Sparse position table above | **PASS** |
| C3 | Missing keys / contradictory / equal omissions / rounding boundaries | Missing-key + equal-omission + A/L/E rounding accept/reject nodes (safeguard table) | **PASS** |
| C4 | Four-period Lululemon integrity after sparse repair | Same as A1 | **PASS** |
| C5 | Synthetic before-failure / after-success for sparse eligibility | Overlay table: sparse_std + sparse_agg before FAIL / after PASS | **PASS (overlay)** |

### From `88ce931` (9M.2.4.1.1 — Repair Sparse Equity-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| D1 | Sparse equity omission fails despite zero implied-equity gaps | Overlay: before `17114fc` DID NOT RAISE; after `8c0098c` PASS; live `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | **PASS (overlay + live)** |
| D2 | Signed contra-equity; subtotal exclusion; override controls | Exact nodes in safeguard table | **PASS** |
| D3 | Equity missing keys / unavailable totals / envelope boundaries | Exact nodes in safeguard table | **PASS** |
| D4 | Implied-equity remains separate from equity-detail gate | Test design + Lululemon implied env 11.5 vs E-detail env 2.5; live `equity_gap` vs equity_detail_gap | **PASS** |

### From `a62893f` / `0f1d2c3` / `b5a33cd` / current step obligations

| # | Criterion | Evidence | Status |
|---|---|---|---|
| E1 | All 12 pretax/ETR matrix cases | Individual 12-ID table; isolated matrix group | **PASS** |
| E2 | Header corruption + link/arithmetic rejection (formula inspection, not Excel recalc) | Header + source-link mutation nodes | **PASS** |
| E3 | Zero-pretax + alias-removal retained | Zero-denominator + alias-removal nodes | **PASS** |
| E4 | Four-period integrity + causal liability/equity explanation | A1 + A2 (implied-equity); A2-ED remains UNVERIFIED | **PASS** with A2-ED caveat |
| E5 | Asset/liability/signed equity-detail gates; fail-closed | C*/D* + safeguard table | **PASS** |
| E6 | Sparse ≠ zero; provenance preserved | B2–B3 concrete table | **PASS** |
| E7 | NCIT / Common stock / G1–G2–G3 / empty unclassified | Live NCIT+CS; gift-card/PPE/common-stock + integrity empty-unclassified nodes | **PASS** |
| E8 | Required suites; deterministic artifact comparisons; failure-path immutability | Isolated suites + dual-reconcile + auth hash guards | **PASS** |
| E9 | Dual-reconcile criterion-level evidence supplied | Dual table with both output hashes and committed comparisons | **PASS** |
| E10 | Every parent original criterion closed | A5 / B8 | **UNVERIFIED** — parents stay UNRESOLVED |
| E11 | Full-company Python↔Excel pretax parity on unmodified Lululemon | Workbook blocked by `interest_expense` | **UNVERIFIED / unavailable** |
| E12 (`0f1d2c3`) | Criterion-split ledger with revision/artifact/command/outcome | This RESULT (restored) | **PASS** |
| E13 (`0f1d2c3`) | Synthetic before/after + historical stages distinguished from diagnostics | Overlay + stage tables | **PASS** |
| E14 (`0f1d2c3`) | Itemized non-BS omission evidence | Non-BS table with assertion locations | **PASS** |

Dependent PASS note: prior A4/E8 PASS that relied on non-isolated suite runs + restore-after-write remains **withdrawn**; current A4/E8 PASS rests only on isolated evidence above.

---

## Final authoritative scope

- Authoritative tracked aggregate excl. `RESULT.md` from isolation run: `b1123a35…0a1` (221 files).  
- This restore: read-only reconfirm of Lululemon reconciled artifact hashes; **no** suite re-execution; **no** copy-back.  
- Diff scope: `RESULT.md` only.  
- `interest_expense` build exception preserved separately from synthetic parity and unavailable full-company parity (E11).

---

## Closure note (does not rewrite the plan)

Criterion-specific evidence deleted after `470aa435` is restored; protected isolated verification is preserved; every original obligation has supported PASS or explicit FAIL/UNVERIFIED accounting with original wording and source revisions.

Explicit UNVERIFIED retained (not invented):

- A2-ED — historical equity-detail at original liability defect (gate absent)
- B7-MID — gap aggregates during `MissingHistoricalValueError` stage
- A5 / B8 / E10 — parent Plan closure
- E11 — full-company workbook pretax parity (`interest_expense` blocker)

Complete accounting does **not** establish technical parent completion. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED**. Return to Plan for parent closure assessment only after original acceptance is judged complete. Genuinely new bounded work first uses **9M.2.4.1.1.1.7**. Step 9 remains incomplete.
