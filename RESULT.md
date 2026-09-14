# RESULT.md — Step 9M.2.4.1.1.1 Verify Generic Pretax-Income Resolution and Correct Acceptance Accounting

**Status:** COMPLETE (this verification child’s acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Verify Generic Pretax-Income Resolution and Correct Acceptance Accounting  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `b9694347a238b00dcdfc1f3b588a237f8185f011` (plan commit; base `412922f`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.  
No production changes.

---

## Task 2 — Parent criteria vs evidence (corrected)

Prior RESULT invented **workbook-generation success** as an original `aa6adc1` acceptance criterion and treated its failure as parent-blocking evidence. Original plans require a temporary-directory probe that may **either** succeed **or** record the exact next exception — not unconditional workbook success.

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

Workbook probe outcome alone does **not** establish or deny parent acceptance.

### Evidence classes (kept distinct)

| Class | Evidence | Status |
|---|---|---|
| Synthetic calculation / formula parity | New `_pretax_parity_*` fixtures + Answer-Key formula inspection | **supported** |
| Real-company resolution | Lululemon `income_before_tax` / label / four-period values / tax distinct / export-reload | **supported** |
| Full-company Python↔Excel pretax parity on unmodified Lululemon | Requires successful workbook build | **unavailable** — blocked by `interest_expense` |

Prior COMPLETE claim that treated row-index arithmetic as sufficient Python/Excel parity is **withdrawn** for the repair narrative; this child supplies direct calculation + emitted-formula evidence on synthetic fixtures.

---

## Task 1 — Measured synthetic calculation and formula paths

Fixture (reordered IS; distinct pretax vs tax; separate from Lululemon):

- concept `income_before_tax`, label `Income before income tax expense`
- pretax inputs: **400.0 / 500.0**
- tax expense: **−60.0 / −80.0**
- independent ETR: **0.15 / 0.16** (`-tax/pretax`)

`compute_anchor` historical series:

- `pretax_income` = `[400.0, 500.0]`
- `effective_tax_rate` = `[0.15, 0.16]`

Emitted Condensed Answer-Key formulas (formulas retained; **not** Excel recalculation):

| Period | Pretax Income formula | Resolved source label / value | Tax Expense formula | ETR formula |
|---|---|---|---|---|
| 0 | `='Income Statement'!B12` | `Income before income tax expense` / `400` | `='Income Statement'!B10` | `=IF(B15=0,NA(),-B16/B15)` |
| 1 | `='Income Statement'!C12` | same label / `500` | `='Income Statement'!C10` | `=IF(C15=0,NA(),-C16/C15)` |

Source-resolved pretax values match Python outputs; tax source row ≠ pretax source row; ETR arithmetic from those source cells matches Python ETR.

Also covered: canonical `pretax_income` concept, normalized label fallback (empty concept), reordered rows, standardized export/reload, alias-removal fail-closed, wrong-link detection via distinct pretax/tax values. Precedence, duplicate ambiguity, missing-required, and tax-exclusion regressions retained.

---

## Real-company Lululemon resolution (preserved)

| Check | Result |
|---|---|
| concept / label | `income_before_tax` / `Income before income tax expense` |
| values | 1332571 / 2175735 / 2576077 / 2238967 |
| tax | `Income tax expense` at index 10 (pretax index 8) |
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

Causal liability/equity rows for the original NCIT discrepancy remain as documented in prior sparse-repair children (NCIT classification / sparse equity gate); current gaps are all zero under unchanged envelopes.

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
→ 524 passed in 9.71s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.39s

PYTHONPATH=. pytest core/tests -q
→ 1076 passed in 88.03s
```

Working tree after suite cleanup: only intentional test + RESULT edits.

---

## Diff scope (intentional)

- `core/tests/test_reference_integrity.py` — synthetic pretax/ETR arithmetic + emitted formula source-link parity (canonical / alias / label / reorder / reload / alias-removal detection)
- `core/tests/test_line_resolver.py` — alias-removal fail-closed regression
- `RESULT.md` (this file)

Production code, committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1.1 acceptance for **verify generic pretax calculation/formula parity and correct acceptance accounting** is met. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED** for Plan’s evidence-based parent closure assessment. Any genuinely new child uses first unused ID **9M.2.4.1.1.1.1**. Step 9 remains incomplete.
