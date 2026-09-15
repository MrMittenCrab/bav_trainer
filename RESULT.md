# RESULT.md — Step 9M.2.4.1.1.1.17 Restore Source-Supported Capex Coverage and Regenerate Release

**Status:** COMPLETE (this child; measured G4 capex coverage + generic safeguards + Fast Retailing release contract)  
**Step:** 9M.2.4.1.1.1.17 — Restore Source-Supported Capex Coverage and Regenerate Release  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED** (Plan closure pending)  
**INPUT_STATUS:** PENDING  
**Base:** `04aa1c4a6864883062e4ccbe901d61d2e774a76c`  
**Workspace HEAD:** `0ce0d61a20eca1dc83c3a754430d19e275d0c7ef` (plan commit; production overlay uncommitted)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged by this run).  
No commit / push / sync / checkpoint. No branch create/switch. No interest-source invention. No forecasting/valuation.

Isolation base: `/tmp/bav_9m24111117_iso_nXG6`  
Verified overlay aggregate SHA-256 (221 tracked files excl. `RESULT.md`, after production overlay, before suites):  
`844b5163039f5c6670d8494f8963babd92ff9ada123eb9edbf9ab56e08040ffc`

---

## Task 1 — Benchmark baseline (HEAD `0ce0d61`, isolated `before/`)

Commands: `git archive HEAD` → `$ISO/before`; `cd $ISO/before && PYTHONPATH=. python3 $ISO/probes/probe_modules.py`

### Input hashes (unchanged throughout)

| Path | SHA-256 | Size |
|---|---|---:|
| `benchmark/lululemon/reconciled/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `benchmark/lululemon/reconciled/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `benchmark/fast_retailing/reconciled/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `extracted/LULU_FY2022.json` | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| `extracted/LULU_FY2023.json` | `745876dbac871a45b0bd9857c921529bf786f178cfc304af6c0fb12a12373b2e` | 60225 |
| `extracted/LULU_FY2024.json` | `a0bc4ccef0974b1ae08e5aa0c4601989476061e98afedd0f860655d0d75dc372` | 60984 |
| `extracted/LULU_FY2025.json` | `3887f0d452d9c8887133e25e5a9bad018918de66f0e50419afafab3f072892dd` | 58912 |
| `source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |

### Lululemon G4 — filing provenance and cash-flow meaning (accepted)

Stored row: concept `capital_expenditures`, label `Purchase of property and equipment`, statement cash flow, section `cash flows from investing activities`. Negative values are reported investing outflows for PPE purchases (equivalent in meaning to `payments_for_ppe`; stored concept/values/signs/provenance not rewritten).

| Period | status | selected amount | selected source |
|---|---|---:|---|
| 2023-01-29 | `selected` | −638657 | FY2024 comparative p54 `LULU_FY2024_Annual_Report.pdf` |
| 2024-01-28 | `selected` | −651865 | FY2025 comparative p53 `LULU_FY2025_Annual_Report.pdf` |
| 2025-02-02 | `selected` | −689232 | FY2025 comparative p53 `LULU_FY2025_Annual_Report.pdf` |
| 2026-02-01 | `selected` | −680802 | FY2025 current_period p53 `LULU_FY2025_Annual_Report.pdf` |

`payments_for_ppe` row absent from standardized cash flow. `interest_expense` unresolved. `Other income (expense), net` (`other_income_expense_net`) 4163 / 43059 / 70380 / 28352 — **not** treated as interest.

### Lululemon before (HEAD)

| Probe | Result |
|---|---|
| `capex_applicable` | **False** |
| `capex_availability` | `payments_for_ppe=False`, `ambiguous=False` |
| `resolve_line(..., "payments_for_ppe")` | no hit |
| `resolve_capex_source` | `None` |
| modules | capex False; fixed_asset True; lease_liability True; lease_rou False; lease_repayment False; deferred_tax False; goodwill_intangibles True |
| workbook `build_training_workbook` | `MissingLineError: Required concept 'interest_expense' not found in statement lines` |

Independent stored diagnostics (available as facts; module gated off):

| Period | payments_reported | ppe_capex (−reported) | revenue | ratio |
|---|---:|---:|---:|---:|
| 2023-01-29 | −638657.0 | 638657.0 | 8110518.0 | 0.07874429228811279 |
| 2024-01-28 | −651865.0 | 651865.0 | 9619278.0 | 0.06776652052264213 |
| 2025-02-02 | −689232.0 | 689232.0 | 10588126.0 | 0.0650948052563787 |
| 2026-02-01 | −680802.0 | 680802.0 | 11102600.0 | 0.061319150469259454 |

### Fast Retailing before (HEAD)

| Probe | Result |
|---|---|
| capex concept | `payments_for_ppe` / `Payments for property, plant and equipment` |
| `capex_applicable` | **True** |
| `ppe_capex` | 56500.0 / 51271.0 / 61764.0 / 73728.0 / 135535.0 |
| `expected_specs` | **491** (`capex_specs=10`, lease_liability=18, lease_rou=16, lease_repayment=10, fixed_asset=35, goodwill_intangibles=58, deferred_tax=17, ownership=34, per_share=18, per_share_attribution=16) |
| blank Check | **0 / 0 / 491 / 491** |
| filled Check | **491 / 0 / 0 / 491** |
| modules | all True (capex, fixed_asset, lease_liability, lease_rou, lease_repayment, deferred_tax, goodwill_intangibles) |

---

## Task 2 — Bounded generic capex support

Authorized production: `core/model/line_resolver.py` explicit-concept alias `capital_expenditures` → `payments_for_ppe` (canonical `payments for ppe` retained at P1). `core/model/capex.py` docstring/comments only; resolution already goes through `resolve_line`. `core/engine/reference_model.py` unchanged (`_resolved_source_row` already uses the shared resolver). Stored concepts, values, signs, and provenance are not rewritten. Label-only inputs remain unsupported (`_EXACT_ALIASES["payments_for_ppe"]` empty).

SHA-256 of overlay files:

| Path | SHA-256 | Size |
|---|---|---:|
| `core/model/line_resolver.py` | `d02fa65932612c5ffa985497189e7c17094e5945311f3f8b7f00ec55d40f19ca` | 9154 |
| `core/model/capex.py` | `00c5f822d6b599fa84d5ce415979e16fc6d96f4f96c8a940b5c6f588f6cf0531` | 3499 |
| `core/tests/test_line_resolver.py` | `39c34620229940fbe1991d6e774b35ef44d803e2532b3aad99fcd6f8a132c962` | 19172 |
| `core/tests/test_capex.py` | `2f47c1bbaa2402a63975c596f1ea6bde0ecb9e0b81ea4558ad66282d51849890` | 26324 |
| `core/tests/test_lululemon_benchmark.py` | `9eddf31a71efffdd840aa107430fe62ad9ee318ac7e439afa31ea12c47384d4c` | 26860 |

---

## Task 3 — After probes, suites, release

After copy: `$ISO/after_probe` (HEAD archive + overlay). Same probe command as before.

### Lululemon after (required coverage gain)

| Probe | Before | After |
|---|---|---|
| `capex_applicable` | False | **True** |
| `capex_availability.payments_for_ppe` | False | **True** |
| `ambiguous` | False | False |
| stored concept | `capital_expenditures` | `capital_expenditures` (unchanged) |
| stored values | four-period series above | identical |
| `resolve_capex_source` is stored row | no | **yes** (index 8) |
| export/reload concept | n/a | `capital_expenditures`; values unchanged |
| workbook | `interest_expense` MissingLineError | **same exception** (reported separately) |

Independent four-period diagnostics after match the before stored arithmetic (module now available). `compute_capex_series` via `compute_anchor` still raises `interest_expense` (anchor path; not a capex-resolution miss). Synthetic alias fixture covers `compute_capex_series` + Excel source identity.

### Fast Retailing after (no regression)

Identical to before: `expected_specs=491`, `capex_specs=10`, `ppe_capex` anchors unchanged, blank Check `0/0/491/491`, filled Check `491/0/0/491`.

### Isolated suites

Artifact-writing tests ran only in disposable copies. Authoritative workspace was not used as cwd.

| Suite | Root | Exact command | Exit | Counts | Overlay auth after vs before | Isolated tracked diffs vs pristine overlay |
|---|---|---|---:|---|---|---|
| resolver/capex/LULU | `…/after_probe` | `PYTHONPATH=. pytest core/tests/test_line_resolver.py core/tests/test_capex.py core/tests/test_lululemon_benchmark.py -q` | 0 | **76 passed in 5.56s** | same `844b5163…` | none |
| parent regression | `…/focused` | `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q` | 0 | **543 passed in 13.12s** | same | none |
| FR benchmark | `…/fr` | `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` | 0 | **132 passed in 29.97s** | changed | `benchmark/fast_retailing/BASELINE.md`; `benchmark/fast_retailing/reconciled/provenance.json` `fd5a1ec8…` → `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` (874954 → 875119) — **not copied back** |
| full | `…/full` | `PYTHONPATH=. pytest core/tests -q` | 0 | **1099 passed in 92.08s** | changed | FR BASELINE + provenance as above; `example/DEMO_HK_Trainer.xlsx` `2f3f771d…` → `840a023cd9bd…` (size 26790) — **not copied back** |

Prior isolated parent **537** / full **1089** at `590c73a` vs this overlay: +6 parent (5 resolver + 1 LULU G4 node), +10 full (those six + 4 capex alias nodes). FR count unchanged at **132**.

Logs: `$ISO/logs/capex_focused.log`, `focused.log`, `fr.log`, `full.log`.

### Fast Retailing release (two independent builds)

```text
cd $ISO/release_r{1,2} && PYTHONPATH=. python scripts/build_fast_retailing_release.py
→ exit 0 both; r1 file hashes == r2 file hashes
```

Build audit (`verify_release_pair=True`, `require_check_counts=True`) passed. Independent spot-check on r1: 491 Trainer practice cells blank, yellow, no comments; 491 Answer-Key formulas with non-empty Notes.

| Artifact | Committed SHA-256 | Regenerated r1=r2 | r1==committed |
|---|---|---|---|
| `FastRetailing_Trainer.xlsx` | `4b657461757cfb43…` (36764) | `115a46e535e0d7252b7292bfb7a5c63833ad4486de68ebe4e8ef7e5aeeaa86a9` (36765) | no (1-byte zip rebuild) |
| `FastRetailing_Answer_Key.xlsx` | `a1d397933971535c…` (123565) | `f0cd4ff5386090e6204b7988ad4fd54ddf04fd15fdedfca6a2b6617b8489e124` (123566) | no (1-byte zip rebuild) |
| `FastRetailing_Answer_Key.component_map.json` | `dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34` | same | **yes** |
| `FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | same | **yes** |
| `rowmap.json` | `90790f47917b161e5f291c332983539c3428f9beebb4e19df1bc39a437395a0b` | same | **yes** |
| `README.md` | `a7ee4b1c6a8e6a8acdff9cb1eea5654c0f21cc80ea6d8ee614e87b1f3f04384d` | same | **yes** |
| `supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | same | **yes** |
| `supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | same | **yes** |
| `supporting/provenance.json` | `fd5a1ec87b61c4835d3b7bfda79996afa6c5ed9bbf2082e35413fb18ee696f1f` (874954) | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` (875119) | no (known reconcile provenance refresh; not a capex semantic change) |

Release copies did not mutate non-release tracked files. Validated r1 outputs published to workspace `release/fast_retailing/`.

### GAPS.md

Updated **only** current-stage table (G4 pass; measured build exception `interest_expense`) and G4 entry → **CLOSED**. G1–G3/G5–G8 text not rewritten.

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Four-period Lululemon capex availability unavailable → available | before/after probes | **PASS** |
| Independently checked four-period diagnostics | stored payments negated; ratios vs `REVENUE_ANCHORS`; LULU test node | **PASS** |
| Stored concept/values/signs/provenance unchanged | `capital_expenditures`; values hash-stable standardized | **PASS** |
| Generic alias / ambiguity / missing / sign / zero / label-only / round-trip / Python↔Excel | `test_capex.py` + `test_line_resolver.py` | **PASS** |
| Lululemon workbook availability reported separately | still `interest_expense` MissingLineError | **PASS** (recorded; not repaired) |
| FR module/practice/Check unchanged | 491 / 10 capex specs / 0-0-491 and 491-0-0 | **PASS** |
| Isolated required suites | 76 / 543 / 132 / 1099 | **PASS** |
| Dual release determinism + pair contract | r1==r2; audit + yellow/blank/Notes spot-check | **PASS** |
| Failure-path immutability | parent focused suite; FR/full isolated writes not copied back | **PASS** |

Original parent technical acceptance retained (A2-ED / B7-MID Doc UNVERIFIED; A5 / B8 / E10 Plan UNVERIFIED; E11 NonReq UNVERIFIED/`interest_expense`). Interest not invented from `Other income (expense), net`.

---

## Remaining blockers (carried forward)

- Lululemon Trainer/Answer-Key build: `MissingLineError: Required concept 'interest_expense' not found in statement lines`
- Parent Plan closure (A5 / B8 / E10)
- Remaining source-supported Lululemon gaps G5+ (leases/deferred-tax aliases, etc.)

---

## Closure note (does not rewrite the plan)

Step **9M.2.4.1.1.1.17** measured acceptance **PASS**. G4 capex coverage restored generically. Fast Retailing release regenerated without practice-count regression. Keep **INPUT_STATUS: PENDING**. Parents stay **UNRESOLVED**. Return to Plan for original parent acceptance assessment and remaining Step 9 prioritization (interest-source/build completion is next Lululemon workbook blocker; do not invent interest).

**Required plan note (do not edit IMPLEMENTATION.md here):** child 9M.2.4.1.1.1.17 technically complete; G4 CLOSED; FR `expected_specs=491` unchanged; Lululemon workbook still `interest_expense`; Plan should assess parent closure and next Step 9 work.
