# RESULT.md — Step 9M.2.4.1.1.1 Repair Independent Pretax and ETR Parity Verification

**Status:** COMPLETE (this repair child’s acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Repair Independent Pretax and ETR Parity Verification  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `70da89edc8a8a2d11c11cae0fe4cc9dd32be6e48` (plan commit; base `8bd5f50`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production changes.

---

## Withdrawal of unsupported prior claims

Prior RESULT claimed COMPLETE for independent-expectation, emitted-arithmetic, and wrong-link-detection coverage while expectations were still derived through `resolve_line` / `ratio_or_na` and ETR checks were substring-only. Those claims are **withdrawn**.

This repair replaces them with fixture-owned expectations, a strict test-local ETR formula contract plus referenced-cell evaluation, and saved-copy corruption rejection.

---

## Task 1 — Independent expectations and emitted arithmetic

Fixture-owned default expect (not from production helpers):

| Field | Independent value |
|---|---|
| pretax label | `Income before income tax expense` |
| tax label | `Income tax expense` |
| periods | `2024-12-31`, `2025-12-31` |
| pretax | **400.0 / 500.0** |
| tax | **−60.0 / −80.0** |
| ETR (`-tax/pretax`, test-local) | **0.15 / 0.16** |

`compute_anchor` vs those expectations:

- `pretax_income` = `[400.0, 500.0]`
- `effective_tax_rate` = `[0.15, 0.16]`

Emitted Condensed Answer-Key formulas (build → copy/reload; formulas retained; **not** Excel recalculation):

| Period | Pretax formula | Source label / value | Tax formula | ETR formula (strict contract) |
|---|---|---|---|---|
| 0 | `='Income Statement'!B12` | `Income before income tax expense` / `400` | `='Income Statement'!B10` | `=IF(B15=0,NA(),-B16/B15)` |
| 1 | `='Income Statement'!C12` | same label / `500` | `='Income Statement'!C10` | `=IF(C15=0,NA(),-C16/C15)` |

Evaluated referenced-cell arithmetic matches independent ETR and Python outputs.

Also measured:

- canonical `pretax_income` concept (250/310, −40/−55);
- normalized label fallback (empty concept; 180/210, −27/−42);
- natural and reordered source-row orders;
- standardized export/reload;
- zero pretax period → independent `#N/A` and zero-guard contract (`pretax=0/500`, tax=`−60/−80`, ETR=`#N/A` / `0.16`).

---

## Task 2 — Corruption rejection (construction ≠ validation)

Passing baseline Answer Key built once; each negative control mutates a fresh saved copy (no regenerate):

| Mutation | Validator rejection |
|---|---|
| Pretax formula redirected to tax source row | `AssertionError` matching `pretax (source label mismatch\|link redirected)` |
| Pretax formula redirected to other period column | `AssertionError` matching `pretax (link wrong period\|source value mismatch)` |
| ETR minus sign removed (NA + row names retained) | `AssertionError` matching `etr formula contract mismatch` |
| ETR numerator/denominator reversed | same contract rejection |
| ETR zero-guard corrupted (`=0` → `=1`) | same contract rejection |

Retained regressions: alias-removal fail-closed; precedence / duplicate ambiguity / missing-required / tax-exclusion in `test_line_resolver.py`.

---

## Task 3 — Parent criteria reconciliation

| Plan | Criterion | Status |
|---|---|---|
| `aa6adc1` (9M.2.4) | Four-period `check_reformulation_integrity` under unchanged tolerances | **supported** (all gaps 0.0) |
| `aa6adc1` | Original liability/equity discrepancies explained and repaired | **supported** (prior children; NCIT/sparse equity) |
| `aa6adc1` | Temp-dir build probe: success **or** exact next exception recorded | **supported** (records `interest_expense`; not a success gate) |
| `a370a02` (9M.2.4.1) | Sparse NCIT 28555 / 15864 / reported 0 / `None` preserved | **supported** |
| `a370a02` | Sparse absence ≠ reported zero through export/reload | **supported** |
| `2e88322` / `88ce931` | Independent asset/liability/equity-detail evidence gates | **supported** (prior RESULT + remeasured gaps) |
| `88ce931` | Sparse equity omission fails closed independently of implied-equity | **supported** (prior child) |
| Parent closure | Every original parent acceptance criterion established for closure | **unverified / incomplete** — keep parents UNRESOLVED pending Plan assessment |

### Evidence classes (kept distinct)

| Class | Evidence | Status |
|---|---|---|
| Synthetic calculation / formula parity | Fixture-owned expect + strict ETR contract + cell evaluation + corruption rejection | **supported** |
| Real-company resolution | Lululemon `income_before_tax` / label / four-period values / tax distinct / export-reload | **supported** |
| Full-company Python↔Excel pretax parity on unmodified Lululemon | Requires successful workbook build | **unavailable** — blocked by `interest_expense` |

---

## Real-company Lululemon resolution (preserved)

| Check | Result |
|---|---|
| concept / label | `income_before_tax` / `Income before income tax expense` |
| values | 1332571 / 2175735 / 2576077 / 2238967 |
| tax | `Income tax expense` (index ≠ pretax) |
| export/reload | concept/label/values/index unchanged |

### Workbook probe (unmodified input, temporary directory)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Recorded only; **not repaired**. Full-company emitted-formula parity on Lululemon remains unavailable.

---

## Measured reformulation gaps (committed standardized)

Tolerance formula unchanged: `max(1.0, 0.5 * (detail_count + 1))` (`DEFAULT_TOLERANCE=1.0`).

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts: assets 11 → 6.0; liabilities 11 → 6.0; equity detail 4 → 2.5; implied uses A+L=22 → 11.5.  
- NCIT: **28555 / 15864 / 0.0 / `None`**.  
- Common stock: **611 / 606 / 581 / 557**.  
- `check_reformulation_integrity` → **PASS** all four periods.  
- G1/G2/G3 controls retained in benchmark tests.

---

## Source / artifact hashes (before = after)

No generated refresh authorized; committed Lululemon artifacts unchanged. Stray FR/demo suite mutations reverted.

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
→ 526 passed in 10.09s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.30s

PYTHONPATH=. pytest core/tests -q
→ 1078 passed in 88.76s
```

Working tree after suite cleanup: only intentional test + RESULT edits.

---

## Diff scope (intentional)

- `core/tests/test_reference_integrity.py` — fixture-owned pretax/ETR expectations; strict ETR contract + referenced-cell evaluation; separated build/validate; corruption rejection; zero-denominator case; alias-removal retained
- `RESULT.md` (this file)

`test_line_resolver.py` / `test_lululemon_benchmark.py`: no edit required this pass (regressions already present).  
Production code, committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1.1 acceptance for **repair independent pretax/ETR parity verification** is met. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED** for Plan’s evidence-based parent closure assessment. Any genuinely new child uses first unused ID **9M.2.4.1.1.1.2**. Step 9 remains incomplete.
