# RESULT.md — Step 9M.2 Lululemon Benchmark Baseline and Gap Map

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.1** — generic gift-card / deferred-revenue liability classification (G1)

**Plan base:** `fe17dd9` (`Add Lululemon historical benchmark inputs`)  
**Verification revision:** `446219d07f0a0d10e5b6b5c0d96301e24f13dfaa` (working tree adds LULU baseline artifacts + test; not committed)

`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No Step 10/11 work. No issuer-specific production logic.

---

## What shipped

1. Validated all four LULU FY2022–FY2025 extracted filings against bound PDFs.
2. Ran generic reconcile → `benchmark/lululemon/reconciled/{standardized,provenance,conflicts}.json` (deterministic).
3. Attempted untouched generic build → **blocked** by `UnclassifiedBalanceSheetLineError` on `Unredeemed gift card liability` (no Trainer/Answer Key produced).
4. Added permanent regression `core/tests/test_lululemon_benchmark.py`.
5. Recorded `benchmark/lululemon/BASELINE.md` + `benchmark/lululemon/GAPS.md`.

---

## Measured verification

### Task 1 — validate-source

```text
PYTHONPATH=. python -m core validate-source benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source
→ validated 4 filing(s): 0 error(s), 0 warning(s)
```

| FY | PDF | SHA-256 |
|---|---|---|
| 2022 | LULU_FY2022_Annual_Report.pdf | `b344d1e7…275e4e` (4913067 bytes) |
| 2023 | LULU_FY2023_Annual_Report.pdf | `cd47ea25…13c0f1` (5848446 bytes) |
| 2024 | LULU_FY2024_Annual_Report.pdf | `9268fd53…0ca7ec` (5953217 bytes) |
| 2025 | LULU_FY2025_Annual_Report.pdf | `82e00f90…3c71cc` (6590658 bytes) |

### Task 2 — reconcile + build

```text
PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o benchmark/lululemon/reconciled
→ overlap_conflicts=3
```

| Metric | Value |
|---|---|
| periods | 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01 |
| IS/BS/CF rows | 16 / 31 / 34 |
| overlap / supplemental conflicts | 3 / 0 |
| bound sources | 4/4 |
| diluted WAS (thousands) | 128017, 127060, 123935, 119068 |
| standardized.json | `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45` |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` |
| provenance.json | `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` |

```text
PYTHONPATH=. python -m core build benchmark/lululemon/reconciled/standardized.json \
  -o release/lululemon/Lululemon
→ UnclassifiedBalanceSheetLineError:
  Cannot safely classify balance-sheet line 'Unredeemed gift card liability'
```

Component count: **n/a** (blocked before workbook generation).  
Also unclassified behind first raise: `Property and equipment, net`, `Common stock`.

### Task 3 — regressions

```text
PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py -q
→ 6 passed

PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py -q
→ 138 passed

PYTHONPATH=. pytest core/tests -q
→ 720 passed in 84.12s
```

Incidental FR/DEMO workbook refreshes from the suite were restored; final diff is LULU-only.

### Task 4 — gap map

See `benchmark/lululemon/GAPS.md`. Highest-value open gap:

- **G1** generic gift-card / deferred-revenue liability classification (build blocker)
- Then G2 PPE wording/concept identity, G3 `common_stock`, G4 capex concept alias, G5 ROU/DTA aliases, G6 comparative FY2021 axis, G7 empty note_facts

---

## Acceptance

| Criterion | Result |
|---|---|
| Four filings validate or source defect isolated | **pass** (all validate) |
| Deterministic generic reconciliation artifacts | **pass** |
| Trainer/Answer-Key baseline or precise general blocker proven by test | **pass** (blocker proven) |
| LULU regression + gap map | **pass** |
| Fast Retailing + synthetic suite valid | **pass** (720) |
| No forecasting/valuation; no issuer-specific production logic | **pass** |

**Plan changes needed:** none.

**Unresolved:** G1–G7 as recorded; Step 9 **not** complete.
