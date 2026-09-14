# RESULT.md — Step 9M.2.4.1.1.1 Repair Generic Pretax-Income Resolution

**Status:** COMPLETE (this repair’s acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1 — Repair Generic Pretax-Income Resolution  
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `da07d28ca924ad40946561eec346e3ea9ad6e842` (plan commit; base `8c0098c`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.

---

## Task 1 — Parent criteria vs evidence

| Plan | Criterion | Status |
|---|---|---|
| `aa6adc1` (9M.2.4) | Four-period `check_reformulation_integrity` under unchanged tolerances | **supported** (all gaps 0.0) |
| `aa6adc1` | Original liability/equity discrepancies explained and repaired | **supported** (prior children; NCIT/sparse equity) |
| `aa6adc1` | Workbook generation success | **failed** — build still blocked (next: `interest_expense`) |
| `a370a02` (9M.2.4.1) | Sparse NCIT 28555 / 15864 / reported 0 / `None` preserved | **supported** |
| `a370a02` | Sparse absence ≠ reported zero through export/reload | **supported** |
| `2e88322` / `88ce931` | Independent asset/liability/equity-detail evidence gates | **supported** (prior RESULT + remeasured gaps) |
| `88ce931` | Sparse equity omission fails closed independently of implied-equity | **supported** (prior child) |
| Parent closure | Every original parent acceptance criterion | **unverified / incomplete** — workbook probe still fails closed on next required line |

Sparse-equity repair remains satisfied and is distinct from parent closure. Workbook probes record the next exception; they are not rewritten as unconditional workbook-success criteria.

---

## Blocker trace (pre-repair)

Supplied Lululemon IS row:

- concept: `income_before_tax`
- label: `Income before income tax expense`
- values: 1332571 / 2175735 / 2576077 / 2238967

Resolver required `pretax_income` (canonical concept + prior aliases such as “profit before tax”). Neither the explicit concept alias nor the exact normalized label was registered, yielding:

```text
MissingLineError: Required concept 'pretax_income' not found in statement lines
```

Additionally, tax-expense safe-pattern P3 matched `income before income tax expense` (`endswith("tax expense")`) before the exclusion for `before income tax` was added. Legitimate `Income tax expense` resolution was already exact-alias P2 and remains distinct.

---

## What was implemented (production scope)

`core/model/line_resolver.py` only:

- Explicit-concept alias `income_before_tax` → `pretax_income` (canonical `pretax_income` retained).
- Exact label alias `income before income tax expense` for `pretax_income`.
- Tax-expense safe-pattern exclusion for `before income tax` so the supplied pretax label cannot resolve as `tax_expense`.

---

## Measured post-repair resolution

| Check | Result |
|---|---|
| `resolve_line(..., "pretax_income")` | index 8, concept `income_before_tax`, label unchanged |
| Workbook source row | `SOURCE_START_ROW + index` = 15 |
| `resolve_line(..., "tax_expense")` | index 10, label `Income tax expense` (≠ pretax) |
| Export/reload | concept/label/values/index unchanged |
| Pre-repair required pretax | MissingLineError (reproduced before alias) |
| Post-repair required pretax | resolves |

---

## Measured reformulation gaps (Lululemon committed standardized)

Tolerance formula unchanged: `max(1.0, 0.5 * (detail_count + 1))`.

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts: assets 11 → 6.0; liabilities 11 → 6.0; equity detail 4 → 2.5; implied uses A+L=22 → 11.5.  
- NCIT series unchanged: **28555 / 15864 / 0.0 / `None`**.  
- Common stock unchanged: **611 / 606 / 581 / 557**.  
- `check_reformulation_integrity` → **PASS** all four periods.  
- Gift-card (G1), PPE (G2), empty unclassified non-subtotal BS detail (G3) retained.

---

## Workbook probe (temporary directory)

```text
MissingLineError: Required concept 'interest_expense' not found in statement lines
```

Pretax blocker cleared. Next exception recorded only; **not repaired** (outside this child’s production scope). Parents stay UNRESOLVED.

---

## Source / artifact hashes (before = after)

No generated refresh authorized; committed Lululemon artifacts unchanged.

| Artifact | SHA-256 | Size |
|---|---|---:|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

Stray FR/demo mutations from the full suite were reverted.

---

## Fresh verification counts

```text
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 520 passed in 9.39s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.50s

PYTHONPATH=. pytest core/tests -q
→ 1072 passed in 87.83s
```

New coverage in `test_line_resolver.py`: canonical + `income_before_tax` alias; normalized label fallback; explicit-concept precedence; duplicate ambiguity; missing required; nearby nonmatching labels; pretax label excluded from `tax_expense`. Lululemon benchmark replaces obsolete pretax exception with direct resolution/source-link/export-reload assertions and records the `interest_expense` workbook probe.

---

## Diff scope (intentional)

- `core/model/line_resolver.py`
- `core/tests/test_line_resolver.py`
- `core/tests/test_lululemon_benchmark.py`
- `RESULT.md` (this file)

Committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1.1 acceptance for **generic pretax-income resolution** is met. Keep **Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED** until every original parent acceptance criterion passes (workbook generation still blocked by `interest_expense` / further scope). Return to Plan for evidence-based parent closure and selection of an unused detailed ID for any remaining blocker; Step 9 remains incomplete.
