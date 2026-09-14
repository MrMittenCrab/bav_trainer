# RESULT.md — Step 9M.2.4.1 Preserve Sparse Liability Facts in Standardization

**Status:** BLOCKED (in-scope standardizer work done; parent integrity acceptance not met)  
**Step:** 9M.2.4.1 — Preserve Sparse Liability Facts in Standardization  
**Parent:** Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity — remains **UNRESOLVED**  
**Workspace HEAD:** `a370a02b52bc4ab93d514232e913685ba361c55c`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.

---

## What was implemented (in production scope)

`core/ingestion/filing_standardizer.py`:

- Balance-sheet rows with selected observations on only part of the model axis are **retained**.
- Supplied amounts preserved; unreported model periods use explicit `None` (nullable `LineItem.values` contract).
- Label/concept taken from the **latest available model-period** observation.
- Non-balance-sheet incomplete-axis rows remain **omitted** (`omitted_incomplete_axis`).
- Provenance adds `retained_sparse_axis` (row-level) and period status `missing_period` (no fabricated `selected` / observations); available periods stay `selected`; outside-axis observations unchanged.

Restored Lululemon NCIT row in regenerated `standardized.json`:

| Period | Value |
|---|---:|
| 2023-01-29 | 28555.0 |
| 2024-01-28 | 15864.0 |
| 2025-02-02 | 0.0 (reported zero) |
| 2026-02-01 | `null` / `None` (absent) |

Sparse absence remains distinguishable from reported zero through export/reload.

---

## Measured before / after reformulation gaps

Tolerance **formula** unchanged: `max(1.0, 0.5 * (detail_count + 1))`.

### Before (NCIT omitted from standardized — prior committed behavior)

| Period | asset-detail gap | liability-detail gap | equity gap | liability envelope | equity envelope |
|---|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | **−28555.0** | **+28555.0** | 5.5 | 11.0 |
| 2024-01-28 | 0.0 | **−15864.0** | **+15864.0** | 5.5 | 11.0 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 5.5 | 11.0 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 5.5 | 11.0 |

- Asset detail count = 11 → envelope 6.0  
- Liability detail count = 10 → envelope 5.5  
- Equity uses asset+liability count = 21 → envelope 11.0  

Causal row: omitted `non_current_income_taxes_payable` (28555 / 15864 / 0 / absent).

### After (NCIT retained with `None` at 2026-02-01)

`reformulate_balance_sheet` / workbook build raise:

```text
MissingHistoricalValueError: balance_sheet detail
concept=non_current_income_taxes_payable|label=non-current income taxes payable
line 'Non-current income taxes payable' has no supplied value for modeled period 2026-02-01
```

Parent `check_reformulation_integrity` for all four periods therefore **cannot run** inside current production scope.

### Probe-only (not applied): treat standardized `None` as non-contributing (0 to sum)

If detail summation skipped/`None`→non-contributing without writing invented zeros into standardized facts:

| Period | asset-detail gap | liability-detail gap | equity gap |
|---|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 |

- Asset detail count = 11 → envelope 6.0  
- Liability detail count = **11** → envelope **6.0** (formula unchanged; count +1)  
- Equity count = 22 → envelope **11.5**  
- Probe `check_reformulation_integrity` → **PASS**

---

## Deterministic regeneration

Two reconcile runs in separate temporary directories: all three artifacts byte-identical across runs.

| Artifact | Before SHA-256 | Before size | After SHA-256 | After size | Notes |
|---|---|---:|---|---:|---|
| standardized.json | `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45` | 22289 | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 | +NCIT sparse row |
| provenance.json | `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` | 698793 | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 | NCIT moved omitted→retained_sparse; +`missing_period` |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 | *(unchanged)* | 4718 | required stable |

Committed Lululemon `standardized.json` / `provenance.json` refreshed from verified regeneration only. Source PDFs and extracted JSON unchanged (hashes/sizes verified). Conflicts unchanged.

---

## Anchors confirmed

- Common stock: 611 / 606 / 581 / 557 across the four periods (existing G3 test).  
- Gift-card (G1) and PPE (G2) classification assertions pass.  
- Unclassified non-subtotal BS detail set remains empty.

---

## Fresh verification counts

```text
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 490 passed in 9.38s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.17s

PYTHONPATH=. pytest core/tests -q
→ 1042 passed in 93.81s
```

Lululemon workbook probe in a temporary directory: **failed** with the `MissingHistoricalValueError` quoted above (no unrelated blocker repaired).

Synthetic sparse BS regression added in `test_filing_reconciler.py` (leading / interior / trailing absence, explicit zero vs absence, complete rows, unchanged non-BS omission, export/reload, provenance grounding).

---

## Diff scope (intentional)

- `core/ingestion/filing_standardizer.py`
- `core/tests/test_filing_reconciler.py`
- `core/tests/test_lululemon_benchmark.py`
- `benchmark/lululemon/reconciled/standardized.json`
- `benchmark/lululemon/reconciled/provenance.json`
- `RESULT.md` (this file)

FR benchmark / demo workbook / source / extracted / conflicts: not part of authorized refresh (stray FR/demo mutations from test side-effects were reverted).

---

## Required plan change (do not edit IMPLEMENTATION.md here)

Parent acceptance still requires all four periods to pass `check_reformulation_integrity` within unchanged tolerance **rules**. Sparse retention with explicit `None` is correct and in-scope, but `reformulate_balance_sheet` still calls `required_period_value`, which fail-closes on `None`.

Next Plan revision must expand production scope beyond `filing_standardizer.py`, for example:

1. **`core/model/classification.py`** (detail summation in `reformulate_balance_sheet`): treat explicit standardized `None` on a retained sparse BS detail as **non-contributing for that period’s sum** (not an invented source zero; `LineItem.values` stays `None`; reported `0.0` remains distinct).
2. Preserve fail-closed behavior for genuinely required complete-axis lines / totals as existing tests require.
3. Then replace the current measured-next-exception Lululemon assertion with direct four-period integrity assertions and confirm workbook generation.

Until that scope exists, **retain Step 9M.2.4 — UNRESOLVED**. Do not invent zeros, carry-forward, or absent-after-zero inference to force PASS.

**BLOCKER:** Parent four-period `check_reformulation_integrity` blocked by `MissingHistoricalValueError` on retained sparse `None` at 2026-02-01; fixing requires Plan-authorized production scope outside `filing_standardizer.py` (classification / nullable detail summation).
