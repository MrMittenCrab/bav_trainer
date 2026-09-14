# RESULT.md — Step 9M.2.4.1.1 Evidence-Grounded Sparse-Detail Reformulation Repair

**Status:** COMPLETE (child acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1 — Evidence-Grounded Sparse-Detail Reformulation Repair  
**Parents:** Step 9M.2.4.1 and Step 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `2e883227b4cb70f2a1d545c48234de29d8cf40fd`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.

---

## What was implemented (production scope)

`core/model/classification.py` only:

- Explicit nullable BS detail (`period in values` and `values[period] is None`) may be **non-contributing** for that period’s aggregate only.
- Evidence gate before usable reformulation results: require independent `total_assets`, `total_liabilities`, and `total_equity` for the affected period, then successful asset-/liability-/equity-gap reconciliations under the **unchanged** rounding envelope `max(1.0, 0.5 * (detail_count + 1))`.
- Missing keys, unavailable/null totals, and contradictory gaps fail closed via `MissingHistoricalValueError`.
- `LineItem.values` nulls are never rewritten; reported `0.0` remains a numeric contribution.
- Totals and other required historical inputs keep strict `required_period_value` semantics.

---

## Measured reformulation gaps (Lululemon committed standardized)

Tolerance **formula** unchanged: `max(1.0, 0.5 * (detail_count + 1))`.

NCIT retained series (unchanged source facts): **28555 / 15864 / 0.0 / `None`**.

| Period | asset-detail gap | liability-detail gap | equity gap | asset env | liab env | equity env |
|---|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 11.5 |

- Asset detail count = 11 → envelope 6.0  
- Liability detail count = **11** (NCIT included) → envelope **6.0**  
- Equity count = 22 → envelope **11.5**  
- Causal prior discrepancy: sparse NCIT absence at 2026-02-01; earlier years contributed 28555 / 15864; FY2025 reported zero; FY2026 explicit `None` non-contributing under gate.  
- `check_reformulation_integrity` → **PASS** for all four periods.

Pre-repair aggregates that raised `MissingHistoricalValueError` before this child are **unavailable as live post-repair failures**; the measured post-repair gaps above replace them.

---

## Anchors confirmed

- Common stock: **611 / 606 / 581 / 557** across the four periods.  
- Gift-card (G1) and PPE (G2) classification assertions pass.  
- Unclassified non-subtotal BS detail set remains empty.  
- NCIT `None` at 2026-02-01 and reported `0.0` at 2025-02-02 preserved after reformulation.

---

## Workbook probe (temporary directory)

```text
MissingLineError: Required concept 'pretax_income' not found in statement lines
```

Recorded only; **not repaired** (outside this child’s production scope). Parents stay UNRESOLVED pending that / other original acceptance criteria.

---

## Source / artifact hashes (before = after)

No generated refresh authorized; committed Lululemon artifacts unchanged.

| Artifact | SHA-256 | Size |
|---|---|---:|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

Source PDFs and extracted JSON untouched (verified present; digests match locked baseline tests). Stray FR/demo mutations from the full suite were reverted.

---

## Fresh verification counts

```text
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 499 passed in 9.34s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 26.81s

PYTHONPATH=. pytest core/tests -q
→ 1051 passed in 90.29s
```

Synthetic sparse coverage added in `test_classification.py` (leading/trailing/both/interior absence, reported zero vs `None`, missing keys, null/absent totals, contradictory gaps, complete-row neighbors). Equal asset/liability omission and rounding-envelope controls retained. Lululemon integrity test now asserts four-period PASS + G1/G2/G3 + next workbook exception.

---

## Diff scope (intentional)

- `core/model/classification.py`
- `core/tests/test_classification.py`
- `core/tests/test_lululemon_benchmark.py`
- `RESULT.md` (this file)

Committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1 acceptance for evidence-gated sparse reformulation is met. Keep **Step 9M.2.4.1 and Step 9M.2.4 — UNRESOLVED** until every original parent acceptance criterion passes (workbook generation still blocked by `pretax_income` / further scope). Return to Plan for parent closure assessment and next unused detailed ID. Step 9 remains incomplete.
