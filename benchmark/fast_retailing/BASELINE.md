# Fast Retailing Benchmark Baseline (Step 9M.5)

- Accounting engine phase: Step 9M.5 (goodwill / intangible-asset diagnostics on 9M.3E base)
- Input path: generic `extracted/` → `validate-source` → `reconcile` → `reconciled/`
- Benchmark phase: measurement only — G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed
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
- G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed; G7 disagreements retained with verified deterministic selection and provenance.

## Stage results

| Stage | Status | Detail |
|---|---|---|
| 1_source_fixture_load | pass | loaded |
| 2_identity_validation | pass |  |
| 3_reconciliation | pass |  |
| 4_reference_model_builder | pass | expected_specs=438 lease_specs=18 ownership_specs=34 per_share_specs=18 per_share_attribution_specs=16 fixed_asset_specs=35 goodwill_intangibles_specs=58 |
| 5_workbook_generation | pass |  |
| 6_blank_check | pass | correct=0 incorrect=0 blank=438 total=438 |
| 7_filled_check | pass | correct=438 total=438 |

## First failure

None — all stages passed.

## Module applicability (source fixture)

- **earnings_quality**: applicable
- **working_capital**: applicable
- **fixed_asset**: applicable
- **lease_liability**: applicable
  - availability: lease_liability=True ambiguous=False
- **ownership_attribution**: applicable
  - availability: available=True partial=False ambiguous=False
- **goodwill_intangibles**: applicable
  - availability: goodwill=True intangible_assets=True goodwill_and_intangibles=True payments=True
- **per_share**: applicable
- **normalization**: omitted/not applicable

## Notes

- Temporary Trainer/Answer Key artifacts are not committed.
- Synthetic DEMO / cross-company surfaces remain unchanged.
- Forecasting / valuation remain deferred.
- Comparable diluted-WAS axis (financial-statement units): 306.871785, 306.969624, 307.13887, 307.231804, 307.247804 (basis=split_adjusted; FY2021 factor=3; FY2022–FY2025 factor=1).
- Raw extracted share facts and G7 conflicts preserved unchanged.
