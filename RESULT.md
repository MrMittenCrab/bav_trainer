# RESULT.md — Step 9M.2.4.1.1.1 Correct Completion Accounting and Isolated Verification

**Status:** PROBLEMS — UNRESOLVED  
**Step:** 9M.2.4.1.1.1 — Correct Completion Accounting and Isolated Verification  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Verified code revision:** `590c73a4eba8ee2901687f8f2d03e63aacc865bd`  
**Workspace HEAD:** `b5a33cda8af0458cccd28304ee402f1d5b18544a` (plan-only delta vs base: `IMPLEMENTATION.md`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged by this run).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production or test changes. Authoritative diff scope: `RESULT.md` only.

Technical acceptance, evidence availability, and Plan-owned closure remain separate. A complete ledger does **not** close parents while A5 / B8 / E10 (and other explicit UNVERIFIED items) remain.

---

## Task 1 — Corrected accounting and numbering

### Withdrawal of unsupported COMPLETE

Prior operative `RESULT.md` (at `590c73a` / ledger work under `43d45b2`) claimed **COMPLETE** for criterion-level evidence accounting while required-suite proof ran in the authoritative workspace. Those runs mutated Fast Retailing reconciled `provenance.json` and/or `example/DEMO_HK_Trainer.xlsx`, then relied on **reversion** afterward. Reverting FR/demo mutations does **not** satisfy protection during execution.

Prior suite counts below are retained only as **historical observations** and are **withdrawn** as proof of isolated execution or artifact immutability:

```text
(historical, non-isolated) focused → 537 passed in 11.40s
(historical, non-isolated) FR      → 132 passed in 28.33s
(historical, non-isolated) full     → 1089 passed in 90.26s
```

### Numbering

- Retain current detailed step ID: **9M.2.4.1.1.1**.
- Do **not** renumber historical work.
- Proposed exhausted child **`9M.2.4.1.1.1.5` is withdrawn**.
- First available ID for genuinely new bounded work: **`9M.2.4.1.1.1.6`** (only after original acceptance passes and Plan assesses closure).

### Dependent PASS reassessment (pre-isolation → post-isolation)

| ID | Prior claim | Reassessment |
|---|---|---|
| A4 | PASS (suites + hashes; restore after FR/demo writes) | Supporting non-isolated runs do **not** establish “artifacts unchanged throughout execution.” After protected isolation (Task 2–3): **PASS**. |
| E8 | PASS (same) | Same defect; prior PASS withdrawn, then restored as **PASS** only on isolated evidence below. |
| Other ledger PASS/UNVERIFIED rows | Kept | Criterion wording and source revisions preserved; see Task 1 ledger. |

---

## Task 2 — Artifact-protecting isolation (established before execution)

| Field | Value |
|---|---|
| Verified revision copied | `590c73a4eba8ee2901687f8f2d03e63aacc865bd` |
| Copy method | `git archive <rev> \| tar -x` into three independent temp roots; symlink count 0; shared-inode hardlink break check ran (0 rewrites needed) |
| Isolation base | `/var/folders/m2/14fn3yz12j3f6yknz7_3cmw80000gn/T/bav_9m241111_iso_5qp50x15` |
| Suite roots | `…/focused`, `…/fr`, `…/full` (separate disposable trees) |
| Probe root | `…/probes/probe_copy` (fourth independent archive extract) |
| Protection | Suites execute only under isolated `cwd` + `PYTHONPATH=<iso root>`; authoritative tracked files (all except authorized `RESULT.md` update) SHA-256 hashed before and after **each** suite; immutability judged by hash equality, **not** restoration |
| Temporary pytest dirs | Insufficient alone — FR refresh writes `benchmark/fast_retailing/reconciled/*` via repo-relative `ROOT`; isolation requires full disposable trees |

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

Machine manifests: `…/manifests/isolation_setup.json`, `auth_before_*.json`, `auth_after_*.json`, `suite_runs.json`.

Authoritative aggregate SHA-256 over 221 tracked files excluding `RESULT.md` (stable across all suite boundaries):  
`b1123a35b87a25e8c1552502fbe17e3628c183037c919c3e1c9f540e4825f0a1`

---

## Task 3 — Rerun and measured evidence

### Required suites (isolated)

| Suite | Execution root | Exact command | Exit | Counts | Auth immutable? | Isolated artifact changes |
|---|---|---|---:|---|---|---|
| focused | `…/focused` | `cd <focused> && PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q` | 0 | **537 passed in 11.47s** | yes (agg unchanged) | none |
| FR | `…/fr` | `cd <fr> && PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` | 0 | **132 passed in 28.15s** | yes | `benchmark/fast_retailing/reconciled/provenance.json` `fd5a1ec8…` → `26d9a170…` (size 874954 → 875119) |
| full | `…/full` | `cd <full> && PYTHONPATH=. pytest core/tests -q` | 0 | **1089 passed in 90.64s** | yes | FR provenance same refresh; `example/DEMO_HK_Trainer.xlsx` `2f3f771d…` → `e7448153…` (size unchanged 26790) |

Logs: `…/logs/focused.log`, `fr.log`, `full.log`.  
Code/input revision for all suite copies: `590c73a`.  
Authoritative workspace: `git status` clean of tracked mutations throughout; no generated artifacts copied back.

**Observation:** Isolated FR/full trees absorb the known repo-relative writes. That confirms prior authoritative runs were mutable during execution; hash-guarded isolation is the valid immutability proof.

### Dual reconciliation (isolated probe copy)

Inputs unmodified under `…/probes/probe_copy` (hashes below). Outputs only under `…/probes/reconcile_r{1,2}`.

```text
cd <probe_copy> && PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o <probes>/reconcile_r1
→ exit 0; overlap_conflicts=3

cd <probe_copy> && PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o <probes>/reconcile_r2
→ exit 0; overlap_conflicts=3
```

| Artifact | r1 SHA-256 | r2 | committed | r1==r2 | r1==committed |
|---|---|---|---|---|---|
| standardized.json | `29852347…0b361` | same | same | yes | yes |
| provenance.json | `a31f7b05…33075` | same | same | yes | yes |
| conflicts.json | `d8a33012…978e0` | same | same | yes | yes |

### Reconcile / integrity / pretax nodes (isolated)

```text
cd <probe_copy> && PYTHONPATH=. pytest \
  core/tests/test_lululemon_benchmark.py::test_generic_reconcile_is_deterministic \
  …::test_reconcile_immutability_verified_after_subprocess_failure \
  …::test_reconcile_immutability_verified_after_comparison_failure \
  …::test_reconcile_immutability_guard_detects_temp_mutation \
  …::test_reconcile_drift_is_detected_without_rewriting_expected \
  …::test_four_period_reformulation_integrity -v
→ 18 passed in 3.06s
  (includes subprocess-failure, comparison-failure, mutation-detection, drift-detection outcomes)

cd <probe_copy> && PYTHONPATH=. pytest \
  core/tests/test_reference_integrity.py::test_pretax_etr_parity_coverage_matrix \
  …::test_pretax_parity_rejects_corrupted_period_headers \
  …::test_pretax_parity_rejects_corrupted_source_links_and_etr \
  …::test_pretax_parity_zero_denominator_emitted_arithmetic \
  …::test_pretax_parity_detects_alias_removal -v
→ 16 passed in 1.70s
  (12 pretax/ETR matrix cases + header / source-link-arithmetic / zero-pretax / alias-removal;
   formula inspection / reference evaluation — not Excel recalculation)
```

### Live integrity + preserved series (isolated, committed standardized)

`check_reformulation_integrity(reform, EXPECTED_PERIODS)` → **PASS**.  
Gaps: asset/liability/equity_detail all `(0,0,0,0)`; `equity_gap` `(0,0,0,0)`.

| Period | total_assets | total_liabilities | reported_equity / implied_equity |
|---|---:|---:|---:|
| 2023-01-29 | 5607038.0 | 2458239.0 | 3148799.0 |
| 2024-01-28 | 7091941.0 | 2859860.0 | 4232081.0 |
| 2025-02-02 | 7603292.0 | 3279245.0 | 4324047.0 |
| 2026-02-01 | 8456743.0 | 3494903.0 | 4961840.0 |

NCIT: **28555 / 15864 / 0.0 / `None`**.  
Common stock: **611 / 606 / 581 / 557**.

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

## Historical evidence retained (not re-litigated)

The following remain criterion-supporting **historical / overlay** evidence from the prior ledger (citations unchanged). Fresh isolation does not replace them; it replaces only suite/immutability proof.

### Historical defect stages

| Stage | Code / RESULT revision | What changed | Integrity measurement available? |
|---|---|---|---|
| Original liability defect | `cdf0c9f` RESULT; standardized `ba1ba068…` size 22289 | NCIT omitted via `omitted_incomplete_axis` | Yes — liability + **implied-equity** gaps (equity-detail gate absent) |
| Sparse-value exception | `c50912c` RESULT (HEAD then `a370a02`) | NCIT retained with `None` @ 2026-02-01 | **No** — `MissingHistoricalValueError` before usable reformulation |
| Sparse liability gate | `17114fc` / plan `2e88322` | `None` non-contributing under evidence gate | Yes — gaps 0.0; equity-detail column not yet separate |
| Equity-omission regression repair | `8c0098c` / plan `88ce931` | Independent equity-detail gate added | Yes — A/L/E-detail/implied all measured |

### BEFORE — original liability defect (`cdf0c9f`)

Causal row: `non_current_income_taxes_payable` / selected **28555 / 15864 / 0 / absent**; omitted from standardized.

| Period | asset-detail | liability-detail | equity-detail | implied-equity |
|---|---:|---:|---|---:|
| 2023-01-29 | 0.0 | **−28555.0** | *gate did not exist* → **UNVERIFIED** | **+28555.0** |
| 2024-01-28 | 0.0 | **−15864.0** | *gate did not exist* → **UNVERIFIED** | **+15864.0** |
| 2025-02-02 | 0.0 | 0.0 | **UNVERIFIED** | 0.0 |
| 2026-02-01 | 0.0 | 0.0 | **UNVERIFIED** | 0.0 |

Tolerance formula (all stages): `max(1.0, 0.5 * (detail_count + 1))`.

### Synthetic before/after overlays (identified revisions)

| Regression | Fixture | Pre-repair | Before | Repaired | After |
|---|---|---|---|---|---|
| Sparse standardization | `test_standardize_retains_sparse_balance_sheet_facts` | `cdf0c9f` | FAIL `KeyError: 'sparse_trailing'` | `c50912c` | PASS |
| Eligible sparse aggregation | `test_sparse_explicit_absence_reconciles_when_evidence_gate_passes` | `c50912c` | FAIL `MissingHistoricalValueError` 3/3 | `17114fc` | PASS 3/3 |
| Equity omission | `test_sparse_equity_omission_fails_despite_zero_identity_gaps` | `17114fc` | FAIL DID NOT RAISE | `8c0098c` | PASS |

### Provenance NCIT (committed `provenance.json` `a31f7b05…`)

- `retained_sparse_axis`: NCIT; missing `2026-02-01`; available FY23–FY25.
- Period dispositions include `outside_model_axis` / `selected` / `missing_period`; non-selected agreeing observations remain in `observations[]` (no fabricated values). Global status counts unchanged from prior ledger: selected 327, outside_model_axis 141, omitted_incomplete_axis 22, missing_period 1.

### Non-balance-sheet incompleteness (itemized)

| Fixture | Omitted row | Reason |
|---|---|---|
| `test_standardize_complete_axis_and_omission` | IS `only_2025` | `omitted_incomplete_axis` |
| `test_standardize_retains_sparse_balance_sheet_facts` | IS `only_is_2025` | incomplete axis non-BS omitted while sparse BS retained |

---

## Task 1 — Criterion-level acceptance ledger

Statuses: **PASS** = fresh isolated measurement on `590c73a`; **PASS (historical|overlay)** = cited prior revision; **UNVERIFIED** = missing measurement or Plan-only closure.

### From `aa6adc1` (9M.2.4)

| # | Criterion (retained wording) | Evidence | Status |
|---|---|---|---|
| A1 | All four periods pass `check_reformulation_integrity` within unchanged tolerance rules | Isolated gaps all 0; integrity PASS; `test_four_period_reformulation_integrity` | **PASS** |
| A2 | Recorded liability and corresponding equity discrepancies explained and repaired with causal rows | Historical before `cdf0c9f`: liability + **implied-equity**; causal NCIT; live after all 0 | **PASS (historical before + live after)** — equity = implied-equity |
| A2-ED | Historical equity-**detail** gaps at original defect | Equity-detail gate did not exist at `cdf0c9f` | **UNVERIFIED** |
| A3 | Temp-dir Lululemon build: success or exact next exception | `MissingLineError: … 'interest_expense' …` (isolated probe) | **PASS** (recorded; not a success gate) |
| A4 | Genuine inconsistencies fail closed; artifacts unchanged | Isolated immutability nodes + auth aggregate unchanged across suites (not restore-based) | **PASS** |
| A5 | Parent 9M.2.4 closed for Plan | Requires Plan assessment | **UNVERIFIED** |

### From `a370a02` (9M.2.4.1)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| B1 | NCIT sparse series 28555 / 15864 / reported 0 / `None` | Isolated live values | **PASS** |
| B2 | Sparse absence ≠ reported zero through standardization / export-reload | Sparse nodes + NCIT provenance | **PASS** |
| B3 | Provenance preserves selected/superseded/outside-axis; no invented facts | NCIT provenance retained | **PASS** |
| B4 | Failure-path immutability | Isolated reconcile failure-path nodes (18-group) | **PASS** |
| B5 | Common stock 611 / 606 / 581 / 557 | Isolated live values | **PASS** |
| B6 | Dual reconcile identical to committed; conflicts stable | Isolated dual-run table | **PASS** |
| B7 | Four-period integrity after sparse retention | Historical exception at `c50912c`; live PASS | **PASS (historical exception + live after)** |
| B7-MID | Gap aggregates during MissingHistoricalValueError stage | Unavailable | **UNVERIFIED** |
| B8 | Parent 9M.2.4.1 closed | Plan closure pending | **UNVERIFIED** |

### From `2e88322` (9M.2.4.1.1)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| C1 | Independent asset/liability evidence gates | Sparse gate nodes in focused suite | **PASS** |
| C2 | Leading/interior/trailing absence, zero, complete-row coverage | Sparse position nodes | **PASS** |
| C3 | Missing keys / contradictory / equal omissions / rounding boundaries | Focused suite nodes | **PASS** |
| C4 | Four-period Lululemon integrity after sparse repair | Same as A1 | **PASS** |
| C5 | Synthetic before-failure / after-success for sparse eligibility | Overlay table | **PASS (overlay)** |

### From `88ce931` (Repair Sparse Equity-Detail)

| # | Criterion | Evidence | Status |
|---|---|---|---|
| D1 | Sparse equity omission fails despite zero implied-equity gaps | Overlay + live node | **PASS (overlay + live)** |
| D2 | Signed contra-equity; subtotal exclusion; override controls | Equity sparse control nodes | **PASS** |
| D3 | Equity missing keys / unavailable totals / envelope boundaries | Equity fail-closed nodes | **PASS** |
| D4 | Implied-equity remains separate from equity-detail gate | Design + live `equity_gap` vs equity_detail_gap | **PASS** |

### From `a62893f` / `0f1d2c3` / current step obligations

| # | Criterion | Evidence | Status |
|---|---|---|---|
| E1 | All 12 pretax/ETR matrix cases | Isolated 12/12 in 16-pass pretax group | **PASS** |
| E2 | Header corruption + link/arithmetic rejection (formula inspection, not Excel recalc) | Isolated corrupted-header / source-link nodes | **PASS** |
| E3 | Zero-pretax + alias-removal retained | Isolated zero-denominator + alias-removal nodes | **PASS** |
| E4 | Four-period integrity + causal liability/equity explanation | A1 + A2; A2-ED remains UNVERIFIED | **PASS** with A2-ED caveat |
| E5 | Asset/liability/signed equity-detail gates; fail-closed | C*/D* | **PASS** |
| E6 | Sparse ≠ zero; provenance preserved | B2–B3 | **PASS** |
| E7 | NCIT / Common stock / G1–G2–G3 / empty unclassified | Live NCIT+CS; gift-card/PPE/common-stock / integrity nodes in suites | **PASS** |
| E8 | Required suites; deterministic artifact comparisons; failure-path immutability | Isolated suites + dual-reconcile + auth hash guards | **PASS** |
| E9 | Dual-reconcile criterion-level evidence supplied | Task 3 dual table | **PASS** |
| E10 | Every parent original criterion closed | A5 / B8 | **UNVERIFIED** — parents stay UNRESOLVED |
| E11 | Full-company Python↔Excel pretax parity on unmodified Lululemon | Workbook blocked by `interest_expense` | **UNVERIFIED / unavailable** |
| E12 (`0f1d2c3`) | Criterion-split ledger with revision/artifact/command/outcome | This RESULT | **PASS** |
| E13 (`0f1d2c3`) | Synthetic before/after + historical stages distinguished from diagnostics | Overlay + stage tables | **PASS** |
| E14 (`0f1d2c3`) | Itemized non-BS omission evidence | Non-BS table | **PASS** |

---

## Final authoritative scope

- Authoritative tracked aggregate excl. `RESULT.md` before first suite = after last suite = after probes: `b1123a35…0a1` (221 files).
- `git status` (tracked): clean aside from this `RESULT.md` update.
- No production/test edits; no copy-back from disposable roots.
- Disposable roots may be discarded; evidence paths recorded above.

---

## Closure note (does not rewrite the plan)

Completion accounting is corrected: operative status is **PROBLEMS — UNRESOLVED** (not an unsupported COMPLETE). Protected isolated verification for the three required suites is measured; authoritative artifacts stayed immutable by hash during execution while isolated copies absorbed FR/demo writes.

Explicit UNVERIFIED retained:

- A2-ED — historical equity-detail at original liability defect (gate absent)
- B7-MID — gap aggregates during `MissingHistoricalValueError` stage
- A5 / B8 / E10 — parent Plan closure
- E11 — full-company workbook pretax parity (`interest_expense` blocker)

Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED**. Return to Plan for parent closure assessment only after original acceptance is judged complete. Genuinely new bounded work first uses **9M.2.4.1.1.1.6**. Step 9 remains incomplete.
