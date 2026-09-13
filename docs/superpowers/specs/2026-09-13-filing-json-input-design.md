# Filing-JSON Input Architecture Design

## Purpose

Make source-grounded JSON the canonical handoff between document extraction and BAV analysis so future company projects can use LLM-assisted extraction without making the accounting engine responsible for interpreting arbitrary PDFs.

The stable boundary is:

```text
source documents
→ one extracted JSON per filing
→ deterministic validation/source binding
→ deterministic cross-filing reconciliation
→ StandardizedFinancials
→ BAV reference model
→ Answer Key + Trainer
```

The extraction layer answers **what the filing says**. BAV answers **how those reported facts should be analyzed**.

## Scope

This design covers the reusable input contract and reconciliation layer only.

In scope:
- one JSON file per annual/interim/results filing;
- page-level provenance and deterministic source-file hash binding;
- deterministic validation;
- deterministic cross-filing overlap/restatement handling;
- separate provenance/conflict artifacts;
- conversion into the existing `StandardizedFinancials` contract;
- migration of the Fast Retailing Step 9M.0 benchmark onto the generic flow;
- CLI entry points for validation and reconciliation.

Out of scope for this step:
- calling the OpenAI API automatically;
- PDF parsing inside the BAV engine;
- fixing Fast Retailing accounting-engine gaps G1–G7;
- forecasting, valuation, scenarios, or investment conclusions;
- inventing missing source facts;
- making LLM-suggested BAV classifications authoritative.

## Canonical project layout

```text
projects/<company>/
├── source/
│   └── <original filings>.pdf
├── extracted/
│   ├── FY2021.json
│   ├── FY2022.json
│   └── ...
├── reconciled/
│   ├── standardized.json
│   ├── provenance.json
│   └── conflicts.json
└── output/
    ├── <Company>_Trainer.xlsx
    └── <Company>_Answer_Key.xlsx
```

Benchmark fixtures may remain under `benchmark/<company>/`, but should follow the same `source/`, `extracted/`, and `reconciled/` concepts.

## Extracted filing JSON v1.0

Each source filing is extracted independently. The file is immutable documentary evidence, not a BAV model.

Top-level shape:

```json
{
  "schema_version": "1.0",
  "company": {
    "name": "FAST RETAILING CO., LTD.",
    "ticker": "6288.HK",
    "stock_code": "6288.HK",
    "jurisdiction": "JP"
  },
  "filing": {
    "document_type": "annual_report",
    "fiscal_year": 2025,
    "period_end": "2025-08-31",
    "currency": "JPY",
    "unit_scale": "millions",
    "source_file": "Fastretailing_CFS2025.pdf"
  },
  "statements": {
    "income_statement": [],
    "balance_sheet": [],
    "cash_flow": []
  },
  "note_facts": [],
  "share_facts": []
}
```

`source_file` is a portable filename/relative name, never an absolute local path.

The extractor is **not** responsible for computing a cryptographic hash. When the source file is available, BAV validation computes SHA-256 deterministically and records it in provenance. An optional `source_sha256` field may be accepted when a trusted upstream wrapper supplies one; if present it must match the computed hash.

Allowed `unit_scale` values in v1.0:

```text
ones
thousands
millions
billions
```

Allowed `document_type` values in v1.0:

```text
annual_report
interim_report
results_announcement
```

### Statement rows

A statement row preserves the filing's own label and section. `suggested_concept` is advisory only.

```json
{
  "label": "Lease liabilities",
  "section": "Current liabilities",
  "suggested_concept": "lease_liability_current",
  "values": {
    "2024-08-31": {
      "value": 130744,
      "presentation_role": "comparative"
    },
    "2025-08-31": {
      "value": 126830,
      "presentation_role": "current_period"
    }
  },
  "source": {
    "page": 2,
    "statement": "Consolidated Statement of Financial Position"
  }
}
```

Allowed `presentation_role` values:

```text
current_period
comparative
restated_comparative
prior_presentation
```

Missing periods are omitted rather than guessed. An explicit reported zero is represented by numeric `0`.

Statement rows are reported facts only. Derived values are not permitted in the three primary statement arrays.

### Note facts

Supplemental accounting disclosures are atomic facts rather than copied table blobs.

```json
{
  "fact_type": "lease_liability_total",
  "period": "2025-08-31",
  "value": 513501,
  "status": "reported",
  "source": {
    "page": 14,
    "note": "17 Leases",
    "label": "Total"
  }
}
```

`status` is `reported` or `derived`. A `derived` fact must include a non-empty `derivation` string and is never promoted automatically into `StandardizedFinancials`.

### Share facts

Share facts use the same atomic structure and must identify the share basis explicitly, for example `basic_weighted_average_shares`, `dilutive_incremental_shares`, or `diluted_weighted_average_shares`. Stock-split transformations are not inferred.

## Identity rules

Within one filing, a source row identity is based on:

```text
statement key + normalized section + normalized reported label + suggested_concept
```

This prevents current and non-current rows with the same display label from collapsing together.

`normalized` is used only for deterministic matching. The original label and section remain preserved verbatim in the extracted artifact.

Cross-filing reconciliation is conservative. Rows are merged only when their source identities match under the v1 rule. Similar-looking but non-matching rows remain separate rather than being guessed to be the same economic item.

## Validation and source binding

`validate_extracted_filing()` validates one filing before reconciliation.

Hard failures:
- unsupported `schema_version`;
- unsupported `document_type`;
- missing required metadata;
- malformed dates;
- unknown `unit_scale`;
- source file absent when a `source_root` is supplied;
- declared `source_sha256` mismatch when that optional field is supplied;
- page number missing/non-positive on numeric facts;
- duplicate indistinguishable source-row identities within one statement;
- invalid presentation role;
- non-numeric statement values;
- inconsistent current-period metadata versus filing period end.

When `source_root` is supplied, validation computes the actual SHA-256 and returns it in the validation report for downstream provenance. It does not rewrite the extracted filing JSON.

Warnings may be emitted for documentary issues that do not make the extracted file unusable. Validation never changes extracted values.

## Reconciliation

`reconcile_filings()` consumes multiple validated filing JSON objects belonging to the same company and currency/unit basis.

Company name/ticker/jurisdiction/currency/unit-scale contradictions are hard failures unless an explicit future conversion contract exists.

Every observation is retained in provenance. Selection never destroys evidence.

For the same reconciled row/period, precedence is:

1. `restated_comparative`;
2. `current_period` and `comparative` at equal role rank, with the later audited filing selected;
3. `prior_presentation`.

Within equal role rank, later filing fiscal year wins.

If two observations disagree numerically, write a conflict record even when precedence selects one value. Silent overwrites are forbidden.

A conflict record includes:
- statement;
- row identity;
- period;
- all observations with file/page/role/value;
- selected observation;
- deterministic selection reason.

Rows without a complete requested model-period axis remain in provenance with status `omitted_incomplete_axis`; they are not silently padded with invented values for the current BAV engine.

## Reconciliation warnings versus engine failures

The source/reconciliation layer distinguishes documentary warnings from malformed input.

Examples that are warnings, not invented fixes:
- one presentation-unit BS rounding residual;
- one-unit note total versus split-line sum difference;
- later audited comparative restatement;
- subtotal rounding.

The layer records these conditions but does not insert plugs or alter source numbers.

Existing BAV engine reconciliation may still reject a standardized dataset until a later engine step changes that accounting policy. Step 9M.1 must preserve that separation; it must not fix G1–G7 incidentally.

## Standardization boundary

`standardize_reconciled()` converts selected documentary facts into the existing model-facing `StandardizedFinancials`.

Rules:
- `suggested_concept` may populate `LineItem.concept` only after uniqueness/identity validation;
- original selected labels remain the model labels;
- selected statement values only; no derived note facts promoted automatically;
- missing full-axis statement rows are omitted from the current model payload and remain in provenance;
- historical diluted shares are included only when an explicit comparable diluted weighted-average series exists for the full model axis;
- stock splits are not mechanically restated without audited comparable data or a future explicit contract.

`StandardizedFinancials` remains model-only. Source paths, page references, conflicts, and discarded observations remain in sibling audit artifacts rather than being embedded into the model object.

Outputs:

```text
standardized.json
provenance.json
conflicts.json
```

`provenance.json` includes the computed SHA-256 for each bound source file.

## CLI contract

Step 9M.1 adds:

```bash
python -m core validate-source <extracted-json-or-directory> --source-root <source-dir>
python -m core reconcile <extracted-directory> --source-root <source-dir> -o <reconciled-directory>
```

`validate-source` validates all filing JSONs and reports hard errors/warnings.

`reconcile` first validates/binds sources, then writes the three deterministic outputs above.

Existing `build`, `check`, `list`, and current standardized-JSON support remain intact.

`extract` is deliberately deferred. A later step may call the OpenAI API to produce v1.0 filing JSON, but the API client must depend on this contract rather than the accounting engine depending on an AI provider.

## Fast Retailing migration

Step 9M.0 is the prototype, not discarded work.

The current bundled `benchmark/fast_retailing/source_facts.json` becomes five independent files under:

```text
benchmark/fast_retailing/extracted/
FY2021.json
FY2022.json
FY2023.json
FY2024.json
FY2025.json
```

The generic reconciler must reproduce the currently accepted five-year audited observations and conflict/restatement behavior before the company-specific builder is retired.

The migration must preserve the existing 9M.0 measured engine gaps. In particular, 9M.1 must not silently fix:
- the one-unit BS reconciliation residual;
- generic `Other financial assets` classification failure;
- split lease diagnostic omission;
- lease-interest treatment inconsistency;
- NCI model limitations;
- historical-share comparability limitations;
- the audited overlap conflicts.

Those belong to Step 9M.2.

## Test strategy

Four levels:

1. **Schema tests** — malformed extracted filing JSON fails closed.
2. **Source-binding tests** — filename/computed hash/page/unit/period validation.
3. **Reconciliation tests** — matching comparatives, restated comparatives, conflicts, duplicate rows, current/non-current same labels, stock-split share facts, rounding warnings.
4. **Fast Retailing acceptance** — five filing JSONs through the generic flow reproduce the accepted Step 9M.0 source facts and leave the same accounting-engine gap queue open.

Synthetic fixtures remain authoritative for unit/edge behavior. Fast Retailing remains the first real-company acceptance case.

## Future extraction automation

A future `extract` command may use OpenAI or another document-capable model:

```text
PDF → model → ExtractedFiling JSON v1.0
```

The model is instructed to transcribe, not infer:
- preserve labels, signs, units, sections, and reported distinctions;
- never aggregate current/non-current balances unless the filing itself reports an aggregate fact separately;
- never normalize earnings;
- never choose operating/financing classifications;
- never invent missing periods;
- attach page provenance to every numeric fact.

The deterministic BAV wrapper, not the model, computes/records source hashes.

The BAV engine remains provider-independent because it consumes validated JSON, not model responses or PDFs directly.
