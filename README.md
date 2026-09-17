# BAV Excel Trainer — Hong Kong Edition

Historical BAV Excel practice for Hong Kong-listed **non-financial** companies: the system supplies source facts and classifications; you reconstruct the analytical formulas in a matched Trainer / Answer Key pair.

## What works now

- Multi-period historical reformulation and DuPont
- Classification judgment
- Recurring / non-recurring earnings normalization
- Cash-conversion / accrual diagnostics and trends
- Working-capital diagnostics
- RNOA margin/turnover and change attribution
- ROE operating/financing attribution
- Optional diluted per-share analysis when historical diluted-share data is supplied
- Optional normalized diluted EPS when both shares and normalization are supplied
- PP&E / D&A fixed-asset intensity diagnostics when both source lines are supplied
- Optional lease-liability intensity and trend diagnostics when one aggregate historical lease-liability line is supplied
- One workbook-wide Check
- Matched Trainer + Answer Key

Forecasting, valuation, and investment conclusions are not active yet.

## Quick start

Use `build/input/` for complete canonical BAV / `StandardizedFinancials` JSON
and `build/output/` for generated workbooks. The entire `build/` directory is
local and ignored by Git. From the repository root:

```bash
pip install -r requirements-trainer.txt
mkdir -p build/input build/output

# Place your complete canonical model at build/input/LULU.json, then:
python -m core build build/input/LULU.json -o build/output/Lululemon

python -m core list --workbook build/output/Lululemon_Trainer.xlsx
python -m core check --workbook build/output/Lululemon_Trainer.xlsx
```

The output argument is a **filename stem**, not a directory. This produces:

- `build/output/Lululemon_Trainer.xlsx`
- `build/output/Lululemon_Answer_Key.xlsx`
- `build/output/Lululemon_Answer_Key.component_map.json`
- `build/output/Lululemon_Answer_Key.assumptions.json`
- `build/output/rowmap.json`

Use separate output subdirectories for builds whose `rowmap.json` files must
coexist. The existing `_Trainer.xlsx` output spelling and optional
`-a path/to/assumptions.json` remain supported, as does Excel input.

JSON input uses `core.data.standardized_io.standardized_from_payload`, with
strict validation. Supply the model-only canonical format produced by
`standardized_to_payload` / `reconcile`: company fields (including jurisdiction),
periods, and all three statements, plus any supported historical modules.
Historical shares, leases, geographic segments, and operating KPIs pass intact
to the current workbook engine and its embedded Check context. The engine
determines which schedules it currently supports; the CLI does not add modules
or derive missing facts. Absent optional modules remain absent.

Malformed JSON, duplicate keys, unknown fields (including nested fields),
invalid types/dates, and unsupported model values fail with a nonzero exit and
an error on stderr. Source-extraction JSON, provenance/audit wrappers, and the
legacy partial HK JSON format are not canonical build inputs. Numeric strings
and booleans are not accepted as financial amounts.

Manual builds read their inputs and write the workbook pair and sidecars only
at the requested output location. They do not reconcile filings, update plans,
or run benchmark/release workflows. Destinations in `benchmark/` or `release/`
are rejected; those workflows remain separate.

## How to practice

1. Open the Trainer.
2. Fill the yellow formula cells; supplied historical facts stay populated.
3. Run Check.
4. Yellow = blank, green = correct, red = incorrect.
5. If stuck, open the matching Answer Key for the working formula and its Note.
6. Repeat left-to-right in the Trainer index dependency order.

Accounting Judgment / Normalization Judgment treatment choices can change downstream expected formulas where those sheets are present.

## Inputs and scope

- Non-financial operating companies only
- Filing-based handoff:

```text
PDF/filing → extracted JSON per filing → validate-source → reconcile → build
```

- `validate-source` / `reconcile` consume one extracted JSON per filing and write
  `standardized.json` + audit artifacts; `build` still takes standardized JSON
- Manual standardized JSON or Excel / Bloomberg / Wind-style exports remain supported
- Automatic PDF/AI extraction is not part of the CLI yet
- Actual historical share data is required for per-share modules
- Missing optional data omits the corresponding module rather than inventing facts

No automatic HKEX/SEC scraping in this product.

## Planned

Next:

- Continue Step 9 historical convergence; next candidate is goodwill / acquired intangibles / acquisition-cash diagnostics (see `docs/GOOGL_HISTORICAL_REFERENCE.md`). Capex/reinvestment and split lease-liability aggregation remain deferred until explicit contracts exist.

Later:

- Driver-based forecasting
- Valuation
- Scenario / sensitivity work
- Concise investment conclusions
