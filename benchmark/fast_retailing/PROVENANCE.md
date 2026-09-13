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
records **3** explicit primary-statement conflicts (Step 9M.3E accepted policy):

- FY2022 basic EPS selected `891.77` over CFS2022 `2675.30`
  (`restated_comparative_precedence`).
- FY2022 diluted EPS selected `890.43` over CFS2022 `2671.29`
  (`restated_comparative_precedence`).
- FY2024 cash-flow financing “Others, net” selected `63` over CFS2024 `85`
  (`later_audited_presentation`). No cause is inferred for the cash-flow difference
  beyond the recorded later audited comparative presentation.

Each conflict retains all observations plus the selected value; no silent overwrite.
Closure of G7 means these selections and retained disagreements are verified — not that
source values agree or that conflict records disappear.

Step 9M.1.1 also records **3** supplemental share-fact conflicts for FY2022
(`basic_weighted_average_shares`, `diluted_eps`, `dilutive_shares`) where pre-split
and post-split reported values disagree across filings
(`cross_filing_supplemental_disagreement`). Both observations remain source-bound in
provenance. Share-basis resolution (G6 / Step 9M.3D) does not erase these records.

Every reconciled `note_facts` / `share_facts` item carries `filing_year`,
`source_file`, computed `source_sha256`, and page-level `source` metadata.

## Stock split

Common stock was split **3-for-1 effective 1 March 2023**. Filings from FY2023 onward disclose restated per-share metrics / WAS on a post-split basis where the note says so.

**Reported share facts are unchanged.** Pre-split FY2021 / FY2022 weighted-average
shares (~102 million) remain as reported in extracted filings and provenance.
Analytical model axis `historical_shares` is populated only after validated
split-adjusted resolution (`basis=split_adjusted`, financial-statement units):
`306.871785, 306.969624, 307.138870, 307.231804, 307.247804` with adjustment factors
`3, 1, 1, 1, 1`. That model contract is distinct from the unchanged reported facts and
retained supplemental conflicts.
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
