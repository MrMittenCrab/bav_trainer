# Fast Retailing Benchmark Baseline (Step 9M.2A)

- Accounting engine phase: Step 9M.2A (G1/G2 implementation on accepted Step 9M.1.1 base)
- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/`
- Benchmark phase: measurement only — G1/G2 closed; G3–G7 remain open
- Five fiscal periods: 2021-08-31 … 2025-08-31

## Source hashes

- FY2021: `06b50e0ffbd9504953f0401613d7238fe1c66f95a280d134938570458da74798` (635210 bytes)
- FY2022: `9fb8d620d22bd0c679342a14ede59916207c08c6577ae96290aaa9e567593baa` (1529815 bytes)
- FY2023: `2fe7a85584ed77323d2ce87b3d81dacfbb5907ac7eed878bae7c1985f00116b6` (1260313 bytes)
- FY2024: `72f484268962546e84efc817f00c95ab993cbf8d2c7d532b5ef0e3a2cf26d1de` (1059695 bytes)
- FY2025: `25a85db811fbb1c6c94af50f1ac5b1fa9ffea794753a143685dcf5191d06147f` (868396 bytes)

- Overlap conflicts recorded in conflicts.json: **3**
- Supplemental conflicts recorded in conflicts.json: **3**
- Standardized payload: `benchmark/fast_retailing/reconciled/standardized.json`
- Supplemental provenance source-bound: yes
- Portable source-path validation: yes
- Silent repeated-share overwrite removed: yes
- G1 closed in 9M.2A; G2 closed in 9M.2A; G3–G7 remain open

## Stage results

| Stage | Status | Detail |
|---|---|---|
| 1_source_fixture_load | pass | loaded |
| 2_identity_validation | pass |  |
| 3_reconciliation | pass |  |
| 4_reference_model_builder | fail | Cannot safely classify balance-sheet line 'Other assets'; provide classificationOverrides['Other assets'] |
| 5_workbook_generation | skipped | prior stage failed |
| 6_blank_check | skipped | prior stage failed |
| 7_filled_check | skipped | prior stage failed |

## First failure

- Stage: `4_reference_model_builder`
- Status: `fail`
- Exception: `UnclassifiedBalanceSheetLineError`
- Message: Cannot safely classify balance-sheet line 'Other assets'; provide classificationOverrides['Other assets']

## Module applicability (source fixture)

- **earnings_quality**: applicable
- **working_capital**: omitted/not applicable
- **fixed_asset**: applicable
- **lease_liability**: omitted/not applicable
  - availability: lease_liability=False ambiguous=True
- **per_share**: omitted/not applicable
- **normalization**: omitted/not applicable

## Notes

- Temporary Trainer/Answer Key artifacts are not committed.
- Synthetic DEMO / cross-company surfaces remain unchanged.
- Forecasting / valuation remain deferred.
