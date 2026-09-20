# BAV — Hong Kong Edition

Professional historical Business Analysis and Valuation for Hong Kong-listed **non-financial** companies. The ordinary company build produces a source-grounded `<Company>_BAV.xlsx`. A matching `<Company>_BAV_Trainer.xlsx` can still be derived from that completed model.

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
- Professional BAV as the default company build product
- Optional derivative Trainer and one workbook-wide Check

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
`Fast Retailing`, and `9983` resolve to the other company. Unknown or
ambiguous names fail with candidates. Internal lookup uses lowercase slugs.
List reads the current BAV. Check resolves `build/output/<company>/` without
path arguments; a derived Trainer is still checked when present and remains
non-disclosing.

Persistent inputs live under `build/input/<company>/` (`source/`, `extracted/`,
`reconciled/`). Ordinary `python -m bav build Lululemon` consumes
`build/input/lululemon/reconciled/standardized.json` and writes only under
`build/output/lululemon/`:

- `build/output/lululemon/Lululemon_BAV.xlsx` — the analytical and source-traceability workbook
- `build/output/lululemon/research/*.md` — canonical human-readable research
- `build/output/lululemon/figures/` — reproducible figures
- `build/output/lululemon/supporting/{build_status,assumptions,component_map,rowmap}.json`

Research module order is Drivers → Forecast → Valuation → Overview. Drivers is
implemented. Forecast, Valuation and Overview remain reserved empty files.
Presentation and language follow root `STYLE.md`.

Keep the BAV, research, figures and generated sidecars together. Outputs are
not a second persistent input store. `build/` is ignored by Git.

Ordinary `python -m bav build Lululemon` does not generate a Trainer. The same
completed model can still produce `Lululemon_BAV_Trainer.xlsx`.

Company builds consume the accepted reconciled model plus source-grounded
issuer fiscal-year labels. Project settings retain established comparative-period
admission and supported note-fact handoffs (including the vetted store-count
handoff); they do not change accounting or evidence rules. Invalid or missing
canonical input aborts the build.

A build is a **development snapshot**, not parent-module completion or release
acceptance. Independently integrated, admitted families appear immediately.
Missing comparable-sales or SPSF admission does not hide valid store-count or
geographic work. The **Build Status** sheet shows active families, unavailable
sources/admission, and families not implemented. Partial availability can cover
only some periods; the analytical schedules show individual gaps. The existing
revenue/store growth comparison is not a revenue-per-store productivity ratio.

A rebuild generates and validates the BAV in staging, including semantic maps,
required sidecars, formulas, Notes, and professional opening. Only then does a
single atomic directory exchange replace the current generation. A failed build
returns nonzero and preserves the previous BAV. Replacement supports macOS and
Linux directory exchange; unsupported platforms fail closed. Successful builds
retire recognized old flat `Live`, `KPI`, `Preview`, dated, Trainer, and Answer Key
artifacts for that company. Historical benchmark and release trees are retained
through Git history, not a second live company data architecture.

Advanced explicit-path compatibility remains available and still derives a Trainer
from the completed BAV:

```bash
python -m bav build build/input/company.json -o build/output/custom/Company
python -m bav check --workbook build/output/custom/Company_BAV_Trainer.xlsx
python -m bav list --workbook build/output/custom/Company_BAV.xlsx
```

Explicit input accepts strict canonical StandardizedFinancials JSON or Excel;
`-o` is a filename stem, and `-a assumptions.json` remains supported. This legacy
path mode writes at the requested paths; the atomic current-directory contract
applies to company builds. Source-extraction JSON and legacy partial HK JSON are
not canonical build inputs. `python -m core` remains an internal compatibility
entry point; `bav` is the public interface. Existing internal `core` imports remain
supported.

## How to practice

1. Derive the Trainer from the completed BAV when you want a practice surface.
2. Open the Trainer.
3. Fill the yellow formula cells; supplied historical facts stay populated.
4. Run Check.
5. Yellow = blank, green = correct, red = incorrect.
6. If stuck, open the matching BAV for the working formula and its Note.
7. Repeat left-to-right in the Trainer index dependency order.

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
