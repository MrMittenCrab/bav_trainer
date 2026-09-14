# RESULT.md — Step 9M.2.4 Lululemon Liability-Detail Reformulation Integrity

**Status:** INCOMPLETE (not PASS)  
**Completion:** STOPPED — upstream reconciler/standardizer defect; no in-scope repair  
**Retained step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity  
**Next step:** Do not advance. Plan must expand allowed production surface before retry.

**Plan base (IMPLEMENTATION.md):** `7358db04098fce5014abe23a74806be14c0ef986`  
**Workspace HEAD at stop:** `aa6adc16c64ba5850d2a6d90f0cf4aa32495922d`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No classification/line_resolver edits. No G4–G7 or forecasting/valuation work. No source-fact or committed-artifact mutation.

---

## Diagnosis (Task 1)

Measured four-period reformulation gaps on committed `benchmark/lululemon/reconciled/standardized.json`:

| Period | asset-detail gap | liability-detail gap | equity gap | liability envelope | equity envelope |
|---|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | **−28555.0** | **+28555.0** | 5.5 | 11.0 |
| 2024-01-28 | 0.0 | **−15864.0** | **+15864.0** | 5.5 | 11.0 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 5.5 | 11.0 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 5.5 | 11.0 |

- Asset detail count = 11 → rounding envelope `max(1.0, 0.5*(11+1)) = 6.0`.
- Liability detail count = 10 → envelope `5.5`.
- Equity uses asset+liability detail count = 21 → envelope `11.0`.
- Reported totals resolve correctly: `Total assets`, `Total liabilities`, `Total stockholders' equity`.
- All non-subtotal standardized BS rows classify; unclassified detail set = `{}`.
- Classified liability sum is short of reported Total Liabilities by exactly the gaps above; equity gap is the mirror (`implied − reported = −liability gap`) because assets and equity details already reconcile.

### Causal row (exact identity)

Extracted filings contain **`Non-current income taxes payable`** / suggested concept `non_current_income_taxes_payable` under non-current liabilities:

| Period | Selected value | Source |
|---|---:|---|
| 2023-01-29 | **28555** | FY2023 comparative / FY2022 current (agreeing) |
| 2024-01-28 | **15864** | FY2024 comparative / FY2023 current (agreeing) |
| 2025-02-02 | **0** | FY2024 current |
| 2026-02-01 | *(absent from FY2025 filing)* | — |

Those non-zero values equal the measured liability-detail gaps exactly.

Committed provenance records the entire row as **`omitted_incomplete_axis`**:

- `row_identity`: `balance_sheet|non-current liabilities|non-current income taxes payable|non_current_income_taxes_payable`
- `available_periods`: `2023-01-29`, `2024-01-28`, `2025-02-02` (missing model-axis `2026-02-01`)
- Period-level provenance statuses: `omitted_incomplete_axis` for 2023/2024/2025; `outside_model_axis` for 2022-01-30 comparative (38074)

The row is therefore **absent from `standardized.json`**, so classification/aggregation never sees it. This is not a misclassification, subtotal false-positive, or total-resolution bug in `classification.py` / `line_resolver.py`.

Omission is produced by `core/ingestion/filing_standardizer.py`: when a row’s available periods ≠ full model axis, it is appended to `omitted_incomplete_axis` and skipped from standardized output (`continue` after audit recording).

---

## Why Task 2 was not applied

IMPLEMENTATION limits production changes to `core/model/classification.py` or `core/model/line_resolver.py`, and forbids altering source facts / committed reconciliation artifacts / baseline hashes.

No smallest generic correction exists inside that surface that can restore an omitted liability detail without inventing values or relaxing integrity checks. Per plan: *If evidence establishes an upstream source defect, record it and retain this step as incomplete rather than altering source facts.*

No synthetic classification regression was added (would not reproduce the demonstrated defect). The obsolete Lululemon `liability-detail gap` build-blocker assertion was left unchanged because the blocker remains.

---

## Required plan change (do not edit IMPLEMENTATION.md here)

Retry of Step 9M.2.4 needs an expanded production scope, for example:

1. **`core/ingestion/filing_standardizer.py`** (and covered reconciler/standardizer tests): retain incomplete-axis **balance-sheet detail** rows on the model axis instead of omitting them—e.g. carry forward available period values and use explicit reported `0` / absent-after-zero policy for missing terminal periods—while keeping provenance of sparse coverage.
2. Regenerate or surgically refresh Lululemon reconciled artifacts only after that generic fix, then replace the build-blocker assertion with four-period `check_reformulation_integrity` assertions as originally specified.
3. Keep classification/line_resolver unchanged unless a separate classification defect appears after the row is present.

G4 remains deferred until this integrity blocker clears.

---

## Artifact hashes (before / after; unchanged)

| Artifact | SHA-256 | Size | Unchanged |
|---|---|---:|---|
| standardized.json | `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45` | 22289 | yes |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 | yes |
| provenance.json | `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` | 698793 | yes |

---

## Measured verification

```text
PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 462 passed in 8.44s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 26.63s

PYTHONPATH=. pytest core/tests -q
→ 1040 passed in 85.06s
```

0 failures on the required suites; suites do not establish Step PASS because acceptance (four-period integrity) still fails.

Temp-dir Lululemon build probe:

```text
ReformulationIntegrityError
2023-01-29: liability-detail gap=-2.856e+04 (... envelope=5.5); equity gap=2.856e+04 (... envelope=11)
2024-01-28: liability-detail gap=-1.586e+04 (... envelope=5.5); equity gap=1.586e+04 (... envelope=11)
```

Controls still hold on committed standardized input:

- Common stock values: **611 / 606 / 581 / 557**
- Gift-card → Operating Working Capital Liability
- PPE → Operating Long-Term Asset
- Unclassified BS detail set: `{}`

Incidental FR/DEMO refreshes from the suite were restored; final working-tree diff for this step is **`RESULT.md` only**.

---

## Acceptance

| Criterion | Result |
|---|---|
| All four periods pass `check_reformulation_integrity` within unchanged tolerance | **fail** (FY2023/FY2024) |
| Liability/equity discrepancies explained with exact row identities | **pass** (diagnosis) |
| Discrepancies repaired | **fail** (upstream omission; out of allowed edit scope) |
| Required tests pass; source facts / committed artifacts unchanged | **pass** (tests green; hashes unchanged) |
| Genuine inconsistencies still fail closed | **pass** (existing suite) |

**Incomplete verification does not establish PASS.** Retain Step 9M.2.4. Step 9 remains incomplete.
