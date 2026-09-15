# RESULT.md — Step 9M.2.4.1.1.1.20 Lululemon G5 Source-Supported Lease and Deferred-Tax Coverage

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.20 — Lululemon G5 Source-Supported Lease and Deferred-Tax Coverage  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
**Base (plan):** `237c265b81e71ced0d323814fe7924850baaf147`  
**Workspace HEAD:** `86bedae921225803fe3ec1c6c7bb6e76690213b5`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No invented interest, lease interest, deferred-tax expense, cash-tax effects, recoverability, or repayment flows. No issuer-specific rules. No commit / push / sync / checkpoint / branch change.

These final-byte hashes supersede stale Trainer/Answer-Key hashes from Step 9M.2.4.1.1.1.19.

---

## Task 1 — Explicit-concept aliases

Shared `_EXPLICIT_CONCEPT_ALIASES` in `core/model/line_resolver.py`:

- `right_of_use_lease_asset` → `right_of_use_assets`
- `deferred_tax_asset` → `deferred_tax_assets`
- `deferred_tax_liability` → `deferred_tax_liabilities`

Canonical concepts and stored identities are unchanged. Label heuristics were not added. Canonical+alias (including equal-valued) candidates remain `AmbiguousLineError`. Applicability, Python series, and workbook source links resolve the same original rows. Missing/ambiguous sources omit the module; explicit `None` and missing periods still raise `MissingHistoricalValueError`.

---

## Task 2 — Regressions (measured)

Formula inspection is separate from spreadsheet recalculation. This environment does not evaluate Excel with Excel.app; numeric agreement uses Python expected values, formula text, availability sidecars, semantic maps, and Check.

Commands and actual subprocess exits (`PYTHONPATH=.`):

| Command | Exit | Result |
|---|---:|---|
| `python -m pytest core/tests/test_line_resolver.py core/tests/test_lease_rou.py core/tests/test_deferred_tax.py -q --tb=line` | 0 | **70 passed** in 1.94s |
| `python -m pytest core/tests/test_source_availability.py core/tests/test_capex.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q --tb=line` | 0 | **210 passed** in 36.90s |
| `python -m pytest core/tests/test_reference_integrity.py core/tests/test_trainer.py -q --tb=line` | 0 | **120 passed** in 17.42s |
| `python -m pytest` affected model/trainer/reference-integrity/both benchmarks (`test_reference_integrity`, `test_trainer`, `test_lululemon_benchmark`, `test_fast_retailing_benchmark`, `test_capex`, profitability, ROE, per-share, normalization, lease) | 0 | **432 passed** in 73.39s |
| `python -m pytest core/tests -q --tb=line` | 0 | **1156 passed** in 93.23s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |

Independent Python vs supplied facts (four-period axis 2023-01-29 / 2024-01-28 / 2025-02-02 / 2026-02-01):

| Series | Values |
|---|---|
| ROU levels | 969419 / 1265610 / 1416256 / 1630181 |
| ROU change | `None` / 296191 / 150646 / 213925 |
| ROU average | `None` / 1117514.5 / 1340933.0 / 1523218.5 |
| ROU / revenue | `None` / 1117514.5÷9619278 / 1340933.0÷10588126 / 1523218.5÷11102600 |
| DTA | 6402 / 9176 / 17085 / 24037 |
| DTL | 55084 / 29522 / 98188 / 52278 |
| Net DTA−DTL | −48682 / −20346 / −81103 / −28241 |
| DTA change | `None` / 2774 / 7909 / 6952 |
| DTL change | `None` / −25562 / 68666 / −45910 |
| Net change | `None` / 28336 / −60757 / 52862 |

Answer-Key source links after export/reload: ROU `='Balance Sheet'!B26`, DTA `='Balance Sheet'!B21`, DTL `='Balance Sheet'!B27` (same original rows). Stored concepts remain `right_of_use_lease_asset` / `deferred_tax_asset` / `deferred_tax_liability`.

---

## Task 3 — Releases

Staged via `scripts/build_lululemon_release.py` and `scripts/build_fast_retailing_release.py` (both exit 0) before replace. Repeat-build Lululemon semantic maps were byte-identical before replace. Mutating Check used disposable copies; final Trainers remain blank.

### Lululemon

Unchanged reconciled facts (SHA-256 identical to `benchmark/lululemon/reconciled/`):

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| `supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `Lululemon_Trainer.xlsx` | `97fc521ad8d573cd1aa6432dd1bc1df726571e04b96414770dd3b3eaf8d4446d` | 30206 |
| `Lululemon_Answer_Key.xlsx` | `45ed925fff77084c11f0fa749f60ea50e296e8dcbeece0b5c8a00e597a489c8a` | 83576 |
| `Lululemon_Answer_Key.component_map.json` | `50a42c44e6e65040b42055825ff7f2af4eca5cb5adf584017d4555f17087672e` | 292228 |
| `availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `rowmap.json` | `ae3a6d9fa7dc2c48eb471c20ecd78f195d1f2f5c4bebfbce61af38f1459b1e43` | 61588 |

| Metric | Result |
|---|---|
| `compute_anchor` / `ReferenceModelBuilder` / `build` | success (gated) |
| Active practice / Check | **273** blank `(0,0,273,273)` / filled disposable `(273,0,0,273)` |
| Prior 248-cell surface | **preserved**; +12 `lease_rou` +13 `deferred_tax` |
| Component map SHA-256 | **changed** (new module identities) `50a42c44…` |
| Visible `Source unavailable` cells (Trainer / Answer Key) | **74 / 74** (non-practice display; excluded from Check) |
| Availability sidecar | **unchanged** `13bda245…`; `hist_avg_after_tax_cod` reason `absent_line`; no 4% substitute |
| Independent revenue | 8110518 / 9619278 / 10588126 / 11102600 |
| Independent `ppe_capex` (G4, separate from this defect) | 638657 / 651865 / 689232 / 680802 |
| NCIT | 28555 / 15864 / 0 / `None` |
| Common stock | 611 / 606 / 581 / 557 |

### Fast Retailing

| Metric | Result |
|---|---|
| `expected_specs` / Check | **491** blank `(0,0,491,491)` |
| Component map SHA-256 | **unchanged** `dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34` |
| supporting standardized SHA-256 | **unchanged** `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` |
| `availability.json` SHA-256 | **unchanged** `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` |
| Unavailable cells | **0 / 0** |
| Trainer / Answer Key SHA-256 | `15fd3cef…` / `ca5b57e5…` (openpyxl rewrite; 491-cell contract retained) |

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Both modules activate without source mutation | aliases; stored concepts unchanged; supporting hashes match benchmark | **PASS** |
| Python / source links / formulas / maps / Check agree | independent series; B26/B21/B27; 273 blank/filled Check | **PASS** |
| Coverage above 248 by module | lease_rou +12, deferred_tax +13; prior keys subset | **PASS** |
| 74 interest-unavailable displays and gating preserved | counts; availability hash unchanged; hist-avg `absent_line` | **PASS** |
| Fast Retailing 491-cell contract | map hash unchanged; Check 491 | **PASS** |
| Capex / NCIT / common stock / pretax-tax / ambiguity / zero vs absence | focused + full `core/tests` | **PASS** |
| Parents not closed; INPUT_STATUS PENDING | recorded below | **PASS** |

---

## Remaining blockers (carried forward)

- Source-interest completeness: standalone IS interest still **not found** (G9).
- Parent Plan closure (A5 / B8 / E10).
- A2-ED / B7-MID documentary UNVERIFIED; E11 NonReq UNVERIFIED.
- G6 period-axis assessment; G7 empty `note_facts`; G8 deferral; remaining TARGET Step 9 gates.
- Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain pending.

---

## Closure note (does not rewrite the plan)

Step **9M.2.4.1.1.1.20** measured acceptance **PASS**. Keep **INPUT_STATUS: PENDING**. Parents stay **UNRESOLVED**. Child success does not justify blanket DONE.

**Required plan note (do not edit IMPLEMENTATION.md here):** none blocking. G5 is closed on measured evidence; G9 source-interest completeness and parent acceptance remain residual.
