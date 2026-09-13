# Fast Retailing extracted-filing provenance

Audited documentary facts live as five independent v1.0 filing JSON files under
`benchmark/fast_retailing/extracted/` (one file per CFS PDF). Values are
filing-local; cross-filing precedence is applied by the generic reconciler into
`benchmark/fast_retailing/reconciled/`.

## Units and signs

- Primary statement amounts are **JPY millions** (`unit_scale: millions`).
- Parenthesized amounts are stored as negatives.
- Table dashes (`—` / `-`) on cash-flow lines are stored as `0` (reported nil).
- Share / EPS supplemental facts may use yen or share units in their own fields;
  stock-split restatements are never invented.

## Presentation / rounding notes (FY2025)

1. **Parent profit attribution (1-unit rounding).**  
   Profit for the year `459,153` versus owners `433,009` + NCI `26,143` = `459,152`. The one-unit difference is left as reported; do not force the attribution lines to sum.

2. **Lease liability aggregate vs current + non-current.**  
   Lease note total present value `513,501` versus BS current `126,830` + non-current `386,670` = `513,500`. Keep the note total as a reported note fact (`513,501`); do not promote it into the Balance Sheet or replace splits with the recomputed sum.

3. **Finance costs.**  
   Use the primary Consolidated Statement of Profit or Loss finance-costs line. If a note extract appears to conflict, the primary statement wins.

4. **FY2023 / FY2024 published BS identity residual.**  
   Audited totals satisfy `Assets = Liabilities + Equity` except for a **1** unit difference in FY2023 and FY2024 statement totals. Recorded as published rounding; not plugged in the fixture.

5. **CFS2021 NCI USD misparse (corrected in Step 9M.0).**  
   The IS attribution line prints `Non-controlling interests 40 5,836 53,109` where `53,109` is USD thousands. Correct JPY amounts are `40` (FY2020) and `5,836` (FY2021).

## Cross-filing overlap conflicts

After the closed 2021 NCI transcription correction, generic `reconciled/conflicts.json`
records **3** explicit conflicts:

- FY2022 basic/diluted EPS restated in CFS2023 after the 3-for-1 split disclosure
  (`restated_comparative_precedence`).
- FY2024 cash-flow financing “Others, net” comparative differs between CFS2024 and
  CFS2025 (`later_audited_presentation`).

Each conflict retains all observations plus the selected value; no silent overwrite.

## Stock split

Common stock was split **3-for-1 effective 1 March 2023**. Filings from FY2023 onward disclose restated per-share metrics / WAS on a post-split basis where the note says so.

**Do not invent restated share counts for FY2021 / FY2022.** Those filings report pre-split weighted-average shares (~102 million). Capture them as reported; any post-split restatement belongs only where an audited filing explicitly provides it. The five-year model therefore keeps `historical_shares = null`.

## Duplicate labels

Current vs non-current rows that share a display label keep the source label and use distinguishing `suggested_concept` values (e.g. `lease_liability_current` / `lease_liability_noncurrent`). Identity matching normalizes text only for keys; documentary strings remain verbatim.

## Regeneration

```text
# optional: refresh page text extracts from PDFs
python scripts/extract_benchmark_pdf_text.py

# validate + reconcile through the generic CLI
PYTHONPATH=. python -m core validate-source \
  benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source

PYTHONPATH=. python -m core reconcile \
  benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source \
  -o benchmark/fast_retailing/reconciled
```

Benchmark PDF text extraction depends on `pypdf` (`requirements-benchmark.txt` only).
Automatic PDF/AI extraction is not part of the CLI yet; extracted JSON is authored/migrated as documentary input.
