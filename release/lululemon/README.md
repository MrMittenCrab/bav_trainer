# Lululemon historical release pair

Human-reviewable Trainer and Answer Key generated from checked-in Lululemon
source-grounded filings. Standalone interest lines are not present in the
supplied statements; interest-dependent outputs are marked Source unavailable
and excluded from practice and Check. No interest amounts were invented.

## Dependencies

- Repository checkout with `benchmark/lululemon/source/` PDFs
- Extracted filings under `benchmark/lululemon/extracted/`
- Checked-in reconciled payload under `benchmark/lululemon/reconciled/`
- Python environment with project dependencies installed

## Build

From the repository root:

```text
python scripts/build_lululemon_release.py
```

## Workbooks

- Trainer: `release/lululemon/Lululemon_Trainer.xlsx`
- Answer Key: `release/lululemon/Lululemon_Answer_Key.xlsx`
- Answer Key semantic map: `release/lululemon/Lululemon_Answer_Key.component_map.json`
- Availability: `release/lululemon/availability.json`
- Generated standardized / provenance / conflicts: `release/lululemon/supporting/`

## Check usage

Keep the Trainer and matching Answer Key (plus Answer Key sidecars) in the same
directory. From the repository root:

```text
python -m core check --workbook release/lululemon/Lululemon_Trainer.xlsx
```

Pristine Trainer practice cells should all be blank (yellow). Unavailable
interest-dependent outputs are not practice cells. Check never prints or
inserts answers. Open the Answer Key for formulas and Notes.

Forecasting and valuation remain dormant in this historical release.
