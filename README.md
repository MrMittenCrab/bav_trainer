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

From the repository root:

```bash
pip install -r requirements-trainer.txt
python -m bav build Lululemon
python -m bav check Lululemon
python -m bav list Lululemon
```

Company names are case-insensitive; `LULU` resolves to Lululemon. `FastRetailing`,
`Fast Retailing`, and `9983` resolve to the other benchmark company. Unknown or
ambiguous names fail with candidates. Check and List require an existing current
build and never guess a release workbook.

The canonical current pair is:

- `build/output/Lululemon/Lululemon_Trainer.xlsx`
- `build/output/Lululemon/Lululemon_Answer_Key.xlsx`

The same directory holds the Answer Key component map and assumptions,
`rowmap.json`, `build_status.json`, and source/reconciliation provenance under
`supporting/`. Keep the pair and sidecars together. `build/` is ignored by Git.

Each company build validates the current extracted filings against source PDFs
and reconciles them afresh. Project settings retain established comparative-period
admission and supported note-fact handoffs (including the vetted store-count
handoff); they do not change accounting or evidence rules. Committed benchmark
and release artifacts are read only. Invalid source binding aborts the build;
there is no fallback to a stale standardized model.

A build is a **development snapshot**, not parent-module completion or release
acceptance. Independently integrated, admitted families appear immediately.
Missing comparable-sales or SPSF admission does not hide valid store-count or
geographic work. The **Build Status** sheet shows active families, unavailable
sources/admission, and families not implemented. Partial availability can cover
only some periods; the analytical schedules show individual gaps. The existing
revenue/store growth comparison is not a revenue-per-store productivity ratio.

A rebuild generates and validates the pair in staging, including semantic maps,
required sidecars, learner formatting, and workbook-wide Check. Only then does a
single atomic directory exchange replace the current generation. A failed build
returns nonzero and preserves the previous pair. Replacement supports macOS and
Linux directory exchange; unsupported platforms fail closed. Successful builds
retire recognized old flat `Live`, `KPI`, `Preview`, and dated pairs for that company.
`release/` remains a separate publication/archive workflow.

Advanced explicit-path compatibility remains available:

```bash
python -m bav build build/input/company.json -o build/output/custom/Company
python -m bav check --workbook build/output/custom/Company_Trainer.xlsx
python -m bav list --workbook build/output/custom/Company_Answer_Key.xlsx
```

Explicit input accepts strict canonical StandardizedFinancials JSON or Excel;
`-o` is a filename stem, and `-a assumptions.json` remains supported. This legacy
path mode writes at the requested paths; the atomic current-directory contract
applies to company builds. Source-extraction JSON and legacy partial HK JSON are
not canonical build inputs. `python -m core` remains an internal compatibility
entry point; `bav` is the public interface. Existing internal `core` imports remain
supported.

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
  `standardized.json` + audit artifacts; company `build` runs this pipeline automatically
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
