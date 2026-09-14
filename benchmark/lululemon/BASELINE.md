# Lululemon Benchmark Baseline (Step 9M.2)

- Accounting engine phase: Step 9M.2 (baseline + gap map only; no analytical fixes)
- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/` → `build`
- Benchmark role: primary real-company development driver; Fast Retailing remains regression
- Filing coverage: FY2022–FY2025 annual reports (four independent extracted JSON files)

## Source hashes

- FY2022: `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` (4913067 bytes) — `LULU_FY2022_Annual_Report.pdf`
- FY2023: `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` (5848446 bytes) — `LULU_FY2023_Annual_Report.pdf`
- FY2024: `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` (5953217 bytes) — `LULU_FY2024_Annual_Report.pdf`
- FY2025: `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` (6590658 bytes) — `LULU_FY2025_Annual_Report.pdf`

## Validation

```text
PYTHONPATH=. python -m core validate-source benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source
→ validated 4 filing(s): 0 error(s), 0 warning(s)
```

All four filings bind to their PDFs with matching SHA-256.

## Reconciliation

```text
PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted \
  --source-root benchmark/lululemon/source -o benchmark/lululemon/reconciled
→ overlap_conflicts=3
```

| Field | Measured |
|---|---|
| ticker | LULU |
| company | lululemon athletica inc. |
| currency / units | USD / USD in Thousands |
| jurisdiction | US |
| period axis | 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01 |
| IS / BS / CF rows | 16 / 31 / 34 |
| overlap conflicts | 3 |
| supplemental conflicts | 0 |
| bound source_files | 4/4 (with filing_year) |
| diluted WAS (statement units) | 128017, 127060, 123935, 119068 (`basis=reported`) |

### Artifact digests

- `standardized.json`: `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45`
- `conflicts.json`: `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0`
- `provenance.json`: `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` (698793 bytes)

Two independent reconcile runs into temporary directories were byte-identical; refreshing `benchmark/lululemon/reconciled/` matched those bytes.

### Selected revenue anchors (USD thousands)

| Period | Revenue |
|---|---|
| 2023-01-29 | 8,110,518 |
| 2024-01-28 | 9,619,278 |
| 2025-02-02 | 10,588,126 |
| 2026-02-01 | 11,102,600 |

### Overlap conflicts (retained)

All three are cash-flow working-capital line restatements under `later_audited_presentation`:

1. `change_in_inventories` @ 2023-01-29 — FY2022 current −510,510 vs later −573,438
2. `change_in_prepaid_expenses_and_other_current_assets` @ 2023-01-29 — −113,820 vs later −54,833
3. `change_in_prepaid_expenses_and_other_current_assets` @ 2024-01-28 — 47,167 vs later 40,587

## Build (untouched baseline)

```text
PYTHONPATH=. python -m core build benchmark/lululemon/reconciled/standardized.json \
  -o release/lululemon/Lululemon
→ UnclassifiedBalanceSheetLineError:
  Cannot safely classify balance-sheet line 'Unredeemed gift card liability'
```

No Trainer / Answer Key artifacts were produced. Component count: **n/a** (blocked before `ReferenceModelBuilder` completes).

### Full unclassified BS set (same classifier)

| Label | Concept |
|---|---|
| Unredeemed gift card liability | `unredeemed_gift_card_liability` |
| Property and equipment, net | `property_plant_and_equipment` |
| Common stock | `common_stock` |

First raise is gift-card liability; PPE and common stock fail closed behind it.

## Module applicability probes (pre-build)

Measured against reconciled standardized payload without forcing a workbook:

| Module | Applicable? | Note |
|---|---|---|
| balance-sheet checksum | pass | income/BS/CF checksums True |
| lease_liability | yes | split current + non-current |
| lease_rou | no | concept/label identity gap (`right_of_use_lease_asset` present) |
| fixed_asset (PPE/D&A) | no | PPE label/concept identity gap; D&A resolves |
| capex | no | CF concept is `capital_expenditures`, resolver expects `payments_for_ppe` |
| goodwill_intangibles | yes | goodwill + intangibles present |
| deferred_tax | no | concept names `deferred_tax_asset(s)` / `_liability(ies)` mismatch |
| note_facts / segments | none | extracted `note_facts` count = 0 on all four filings |

## Notes

- Production code contains no LULU / lululemon ticker branches.
- Forecasting / valuation remain deferred.
- Temporary Trainer/Answer Key artifacts are not committed (build did not succeed).
- Comparative IS dates 2021-01-31 / 2022-01-30 appear inside FY2022 extracted filings but are not on the reconciled canonical period axis.
