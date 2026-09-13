# Fast Retailing source_facts provenance

Raw audited facts in `source_facts.json` are transcribed from
`benchmark/fast_retailing/_extract/CFS{YEAR}_p1-30.txt` (pages 1–30 of each CFS PDF).
Values are filing-local; cross-filing precedence is applied later by the standardized builder.

## Units and signs

- Primary statement amounts are **JPY millions** unless a row sets `"units": "yen"` (EPS) or `"units": "shares"`.
- Parenthesized amounts are stored as negatives.
- Table dashes (`—` / `-`) on cash-flow lines are stored as `0` (reported nil).

## Presentation / rounding notes (FY2025)

1. **Parent profit attribution (1-unit rounding).**  
   Profit for the year `459,153` versus owners `433,009` + NCI `26,143` = `459,152`. The one-unit difference is left as reported; do not force the attribution lines to sum.

2. **Lease liability aggregate vs current + non-current.**  
   Lease note total present value `513,501` versus BS current `126,830` + non-current `386,670` = `513,500`. Keep the note total as reported (`513,501`); do not replace it with the recomputed sum.

3. **Finance costs.**  
   Use the primary Consolidated Statement of Profit or Loss finance-costs line. If a note extract appears to conflict, the primary statement wins.

4. **FY2023 / FY2024 published BS identity residual.**  
   Audited totals satisfy `Assets = Liabilities + Equity` except for a **1** unit difference in FY2023 and FY2024 statement totals. Recorded as published rounding; not plugged in the fixture.

5. **CFS2021 NCI USD misparse (corrected).**  
   The IS attribution line prints `Non-controlling interests 40 5,836 53,109` where `53,109` is USD thousands. Correct JPY amounts are `40` (FY2020) and `5,836` (FY2021).

## Cross-filing overlap conflicts

After NCI correction, `provenance.json` records **3** explicit conflicts under latest-audited-presentation:

- FY2022 basic/diluted EPS restated in CFS2023 after the 3-for-1 split disclosure.
- FY2024 cash-flow financing “Others, net” comparative differs between CFS2024 and CFS2025.

Each conflict retains older/newer/chosen filing values; no silent overwrite.

## Stock split

Common stock was split **3-for-1 effective 1 March 2023**. Filings from FY2023 onward disclose restated per-share metrics / WAS on a post-split basis where the note says so.

**Do not invent restated share counts for FY2021 / FY2022.** Those filings report pre-split weighted-average shares (~102 million). Capture them as reported; any post-split restatement belongs only where an audited filing explicitly provides it.

## Duplicate labels

Current vs non-current rows that share a display label keep the source label and use distinguishing concepts (e.g. `lease_liability_current` / `lease_liability_noncurrent`, `other_current_assets` / `other_noncurrent_assets`, derivative and financial asset/liability pairs, provisions, other liabilities).

## Regeneration

```text
python scripts/extract_benchmark_pdf_text.py          # optional: refresh _extract from PDFs
python scripts/build_fast_retailing_source_facts.py   # rebuild source_facts.json
```

Benchmark PDF text extraction depends on `pypdf` (`requirements-benchmark.txt` only).
