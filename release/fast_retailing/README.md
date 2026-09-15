# Fast Retailing historical release pair

Human-reviewable Trainer and Answer Key generated from checked-in Fast Retailing
source-grounded filings through the production pipeline.

## Dependencies

- Repository checkout with `benchmark/fast_retailing/source/` PDFs matching
  `benchmark/fast_retailing/source_manifest.json`
- Extracted filings under `benchmark/fast_retailing/extracted/FY2021.json` …
  `FY2025.json`
- Python environment with project dependencies installed

## Build

From the repository root:

```text
python scripts/build_fast_retailing_release.py
```

## Workbooks

- Trainer: `release/fast_retailing/FastRetailing_Trainer.xlsx`
- Answer Key: `release/fast_retailing/FastRetailing_Answer_Key.xlsx`
- Answer Key semantic map: `release/fast_retailing/FastRetailing_Answer_Key.component_map.json`
- Generated standardized / provenance / conflicts: `release/fast_retailing/supporting/`
- Interest availability: `release/fast_retailing/availability.json`

## Check usage

Keep the Trainer and matching Answer Key (plus Answer Key sidecars) in the same
directory. From the repository root:

```text
python -m core check --workbook release/fast_retailing/FastRetailing_Trainer.xlsx
```

Pristine Trainer practice cells should all be blank (yellow). Check never prints
or inserts answers. Open the Answer Key for formulas and Notes.

Forecasting and valuation remain dormant in this historical release.
