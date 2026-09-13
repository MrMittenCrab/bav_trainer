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
- One workbook-wide Check
- Matched Trainer + Answer Key

Forecasting, valuation, and investment conclusions are not active yet.

## Quick start

```bash
pip install -r requirements-trainer.txt

python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx

python -m core list --workbook example/DEMO_HK_Trainer.xlsx
python -m core check --workbook example/DEMO_HK_Trainer.xlsx
```

Build produces `example/DEMO_HK_Trainer.xlsx` and `example/DEMO_HK_Answer_Key.xlsx`.

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
- Manual historical JSON or Excel / Bloomberg / Wind-style exports
- Actual historical share data is required for per-share modules
- Missing optional data omits the corresponding module rather than inventing facts

No automatic HKEX/SEC scraping in this product.

## Planned

Next:

- Continue Step 9 historical convergence; next candidate is lease intensity / lease-liability diagnostics (see `docs/GOOGL_HISTORICAL_REFERENCE.md`). Capex/reinvestment remains deferred until an explicit source/sign contract exists.

Later:

- Driver-based forecasting
- Valuation
- Scenario / sensitivity work
- Concise investment conclusions
