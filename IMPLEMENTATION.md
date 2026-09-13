# Step 9M.0 — Fast Retailing Real-Company Historical Benchmark Baseline

**Status: COMPLETE** — five-year source-grounded Fast Retailing fixture + provenance + stage audit; engine fails measured in BASELINE/GAPS; no production accounting fixes; synthetic surfaces unchanged. See `RESULT.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `docs/FAST_RETAILING_BENCHMARK.md`, then this plan in full. The accepted implementation base is commit `26f22b7e739045a176b9e63012001818a8823fb7` (`Step 9L.1`) plus commit `19c8aad9b10fcd4aea76fd6c86ff2522ed2d1fd0` containing the five Fast Retailing CFS PDFs. Implement only Step 9M.0. This is a **real-company benchmark baseline/audit**, not another historical feature expansion. Do not begin forecasting, valuation, scenarios, or Step 9M.1 fixes. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Replace synthetic-only confidence with a source-grounded FY2021–FY2025 Fast Retailing benchmark: build a reproducible audited-fact fixture with page-level provenance, verify overlapping filings and key source anchors, then run the current Step 9L.1 engine against it and record every real-company failure without hard-coding Fast Retailing-specific fixes.

**Architecture:** Treat the five committed PDFs as immutable evidence. Transcribe reported facts into a raw `source_facts.json`, generate the model-only `FastRetailing_Standardized.json` through a deterministic benchmark builder using a latest-audited-presentation precedence rule, and keep provenance in a separate machine-readable file because `standardized_io` intentionally strips source metadata. Add a benchmark audit script that runs identity validation, reconciliation, reference-model construction, workbook generation, and Check stage-by-stage and writes a baseline report. Step 9M.0 may legitimately finish with production-engine gaps; the output must make those gaps explicit and reproducible rather than patching them speculatively.

**Tech Stack:** Python, pytest, hashlib/json/pathlib from the standard library, existing `StandardizedFinancials` / `standardized_from_payload`, `validate_financials_identities`, `reconcile_financials`, `ReferenceModelBuilder`, `build_training_workbook`, `check_workbook`; optional local PDF text-search helper may use `pypdf` through a benchmark-only requirements file but must not become a Trainer runtime dependency.

**Spec:** `TARGET.md` Step 9 real-company validation requirement plus `docs/FAST_RETAILING_BENCHMARK.md`.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- The five PDFs under `benchmark/fast_retailing/source/` are immutable source evidence. Do not edit, rename, recompress, or replace them.
- Do not modify `example/DEMO_HK_Standardized.json` to resemble Fast Retailing.
- Do not use web data, analyst databases, GOOGL facts, or synthetic fixtures to fill Fast Retailing gaps.
- Preserve source signs and source units. Do not apply `ABS()` or convert missing facts to zero.
- Preserve source labels where practical. Use concepts/provenance to disambiguate; do not rename labels merely to satisfy current resolver aliases.
- No Fast Retailing-specific conditional logic in `core/`.
- No new historical formula families in Step 9M.0.
- No production-accounting fix merely to make the benchmark build. Engine fixes belong in Step 9M.1 after the baseline gaps are known.
- The synthetic DEMO and cross-company fixtures remain active and unchanged as controlled unit/edge-case tests.
- Forecasting, valuation, scenarios, guidance/consensus, and investment conclusions remain deferred.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

## Review of Step 9L.1 (`26f22b7`)

Step 9L.1 is accepted for its stated scope:

- generated Accounting Judgment cases now use exact `identity:` selectors while legacy/manual `concept:` and `label:` selectors remain supported;
- duplicate-concept split lease rows can be judged independently;
- lease-liability families 87–90 are gated on one uniquely resolvable aggregate source line;
- split current/non-current lease rows are deliberately not summed;
- Check recomputes lease expected values from trusted source facts;
- the commit reports `316 passed` locally and no attached GitHub CI status exists.

One important conceptual issue must be **measured in the real-company benchmark rather than silently ignored**: the current lease judgment changes balance-sheet classification but `compute_anchor()` still derives net interest from the reported finance-cost/income lines without conditioning lease interest on the lease treatment. Fast Retailing explicitly discloses lease interest (FY2025: JPY 8,464m). If lease liabilities are treated as operating, the income-side treatment may also require adjustment for internally consistent NOPAT/RNOA/Spread analysis. Step 9M.0 must record this as a benchmark gap; do not fix it yet.

A second expected real-company pressure point is intentional rather than a 9L.1 defect: Fast Retailing reports current and non-current lease liabilities separately on the primary statement while Note 17 reports an aggregate lease liability. The present 9L.1 diagnostic contract will omit the module from primary split rows. Record this outcome and the explicit note aggregate; do not manufacture an aggregate balance-sheet row in Step 9M.0.

---

### Task 1: Freeze and verify the five-file audited source set

**Files:**
- Create: `benchmark/fast_retailing/source_manifest.json`
- Create: `core/tests/test_fast_retailing_benchmark.py`
- Read only: `benchmark/fast_retailing/source/*.pdf`

**Interfaces:**
- `source_manifest.json` is the machine-readable identity of the canonical source set.
- Benchmark tests fail if a source PDF changes or disappears.

- [ ] **Step 1: Add a manifest with exactly five entries**

Use these exact relative paths:

```text
benchmark/fast_retailing/source/Fastretailing_CFS2021.pdf
benchmark/fast_retailing/source/Fastretailing_CFS2022.pdf
benchmark/fast_retailing/source/Fastretailing_CFS2023.pdf
benchmark/fast_retailing/source/Fastretailing_CFS2024.pdf
benchmark/fast_retailing/source/Fastretailing_CFS2025.pdf
```

Each entry must contain:

```json
{
  "fiscal_year": 2025,
  "period_end": "2025-08-31",
  "path": "benchmark/fast_retailing/source/Fastretailing_CFS2025.pdf",
  "sha256": "<actual lowercase sha256>",
  "bytes": 868396
}
```

Calculate SHA-256 from the committed bytes with `hashlib.sha256`; do not copy Git blob SHA values into the `sha256` field.

Known file sizes from the committed source checkpoint are:

```text
2021  635210
2022 1529815
2023 1260313
2024 1059695
2025  868396
```

- [ ] **Step 2: Add source-integrity tests**

The test must load the manifest and require:

```python
assert len(manifest["sources"]) == 5
assert {s["fiscal_year"] for s in manifest["sources"]} == {2021, 2022, 2023, 2024, 2025}
```

For every entry, require file existence, exact byte size, and recomputed SHA-256 equality.

- [ ] **Step 3: Run the source-integrity test**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -k source -v
```

Expected: PASS before any accounting extraction work begins.

---

### Task 2: Create a raw audited-fact layer with page-level provenance

**Files:**
- Create: `benchmark/fast_retailing/source_facts.json`
- Create: `benchmark/fast_retailing/PROVENANCE.md`
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Optional create: `requirements-benchmark.txt`
- Optional create: `scripts/extract_benchmark_pdf_text.py`

**Interfaces:**
- `source_facts.json` stores values as they are reported in each filing before cross-filing precedence is applied.
- `PROVENANCE.md` explains any presentation conflict, restatement, derived share count, or structural concept assignment.

- [ ] **Step 1: Use one filing object per PDF**

Use this top-level shape:

```json
{
  "company": "FAST RETAILING CO., LTD.",
  "hk_stock_code": "6288.HK",
  "currency": "JPY",
  "units": "JPY millions",
  "filings": {
    "2025": {
      "file": "benchmark/fast_retailing/source/Fastretailing_CFS2025.pdf",
      "periods": ["2024-08-31", "2025-08-31"],
      "income_statement": [],
      "balance_sheet": [],
      "cash_flow": [],
      "share_facts": [],
      "note_facts": []
    }
  }
}
```

Populate analogous objects for 2021–2024.

- [ ] **Step 2: Transcribe the primary statements, not a curated minimal subset**

For each filing capture the rows from:

```text
Consolidated Statement of Financial Position
Consolidated Statement of Profit or Loss
Consolidated Statement of Cash Flows
```

Each row must contain at minimum:

```json
{
  "label": "Revenue",
  "concept": "revenue",
  "pdf_page": 3,
  "statement": "Consolidated Statement of Profit or Loss",
  "values": {
    "2024-08-31": 3103836,
    "2025-08-31": 3400539
  }
}
```

Use positive/negative signs as economically presented in the standardized model contract. If a primary statement displays an expense as a parenthesized amount, store it as negative.

- [ ] **Step 3: Preserve duplicate source labels using concepts, not cosmetic renaming**

Fast Retailing may use the same display label in current and non-current sections. Keep the source label and assign a structural concept that distinguishes the rows, for example:

```text
other_current_assets
other_noncurrent_assets
lease_liability_current
lease_liability_noncurrent
```

The concept records source structure; it must not falsely assert a semantic treatment that the filing does not support.

- [ ] **Step 4: Capture benchmark note facts needed to diagnose existing modules**

At minimum capture, when disclosed by each filing:

```text
aggregate lease liability
lease interest expense
right-of-use assets
PP&E additions / capex or payments for PP&E
PP&E depreciation
combined D&A
profit attributable to owners
profit attributable to NCI
parent-attributable equity
NCI equity
basic weighted-average shares
incremental dilutive shares
reported diluted EPS
stock-split disclosure
```

These note facts remain separate from the primary-statement rows unless the current model contract explicitly supports them.

- [ ] **Step 5: Do not add a runtime PDF dependency**

If text search is needed, a benchmark-only helper may use `pypdf`. If so, create:

```text
requirements-benchmark.txt
```

with only the extra benchmark extraction dependency and keep `requirements-trainer.txt` unchanged. The helper is for locating text; numeric transcription still requires source-page verification.

- [ ] **Step 6: Add schema-level tests**

Require every numeric row/fact to carry:

```text
file via its filing object
pdf_page
statement or note name
period
reported/derived status where applicable
```

Reject facts without a page number or with a period outside FY2020–FY2025 comparatives represented by the source set.

---

### Task 3: Add deterministic cross-filing precedence and overlap validation

**Files:**
- Create: `scripts/build_fast_retailing_benchmark.py`
- Create: `benchmark/fast_retailing/FastRetailing_Standardized.json`
- Create: `benchmark/fast_retailing/provenance.json`
- Modify: `core/tests/test_fast_retailing_benchmark.py`

**Interfaces:**

```python
def build_benchmark(
    source_facts_path: Path,
) -> tuple[dict, dict]:
    """Return (model_payload, provenance_payload)."""
```

- [ ] **Step 1: Implement the precedence rule from the benchmark spec**

For each fiscal period and economic row, choose the latest supplied audited filing that presents that period. Before choosing, compare overlapping values from adjacent filings.

If two filings disagree, do not silently choose. Require an explicit conflict entry in `PROVENANCE.md` / `provenance.json` containing:

```text
period
line identity
older filing/value
newer filing/value
chosen filing/value
reason
```

- [ ] **Step 2: Generate a five-period model payload**

Require periods exactly:

```text
2021-08-31
2022-08-31
2023-08-31
2024-08-31
2025-08-31
```

Use:

```text
ticker = 6288.HK
company_name = FAST RETAILING CO., LTD.
currency = JPY
units = JPY in Millions
jurisdiction = JP
stock_code = 6288.HK
```

Do not set jurisdiction to HK merely because the company has an HK listing.

- [ ] **Step 3: Keep provenance outside the model-only JSON**

`core/data/standardized_io.py` intentionally excludes paths/provenance. Do not change that contract in Step 9M.0. Write `provenance.json` keyed by statement + line identity + period so each emitted model value has a trace back to filing/page/source label.

- [ ] **Step 4: Handle diluted weighted-average shares conservatively**

Use `historical_shares` only for periods whose audited EPS disclosures support a comparable diluted weighted-average share count.

When a filing gives basic average shares plus an incremental dilutive count, a derived total is allowed only as:

```text
diluted WAS = basic weighted-average shares + incremental dilutive shares
```

Mark that value `derived` in provenance.

Because Fast Retailing had a 3-for-1 split effective 1 March 2023, do not apply an undocumented multiplier to 2021/2022. If the supplied audited filings do not provide a clearly restated comparable share basis for all five years, omit the per-share module from the five-year benchmark rather than inventing comparability. Record the limitation.

- [ ] **Step 5: Make regeneration deterministic**

Running the builder twice without source changes must produce byte-identical JSON modulo a terminating newline. Use `json.dumps(..., indent=2, sort_keys=True)`.

- [ ] **Step 6: Add round-trip tests**

Load the generated JSON through `standardized_from_payload()` and require the five periods, company metadata, labels, concepts, and values to survive.

---

### Task 4: Add independent audited source-anchor tests

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Read: `docs/FAST_RETAILING_BENCHMARK.md`

**Interfaces:**
- These assertions are independent of current BAV formulas and catch transcription drift.

- [ ] **Step 1: Assert the FY2025 primary-statement anchors**

Require these exact values in the generated fixture/provenance:

```python
revenue_2025 = 3_400_539
profit_before_tax_2025 = 650_574
tax_expense_2025 = -191_421
finance_income_2025 = 99_143
finance_costs_2025 = -12_834
profit_for_year_2025 = 459_153
profit_attributable_parent_2025 = 433_009
cash_2025 = 893_239
ppe_2025 = 332_351
rou_assets_2025 = 477_111
goodwill_2025 = 8_092
intangible_assets_2025 = 91_606
current_lease_liability_2025 = 126_830
noncurrent_lease_liability_2025 = 386_670
total_assets_2025 = 3_859_353
total_liabilities_2025 = 1_531_852
parent_equity_2025 = 2_273_115
nci_equity_2025 = 54_385
total_equity_2025 = 2_327_501
operating_cash_flow_2025 = 580_618
depreciation_amortization_2025 = 216_492
ppe_cash_payment_2025 = -135_535
```

- [ ] **Step 2: Assert note-level lease anchors separately**

Require provenance to retain:

```text
reported aggregate lease liability = 513,501
lease interest expense = 8,464
```

Do not replace the reported `513,501` with `126,830 + 386,670 = 513,500`; record the one-unit difference as source presentation/rounding evidence.

- [ ] **Step 3: Assert the parent/NCI split explicitly**

Require:

```python
459_153 == 433_009 + 26_143 + 1
```

Do not “repair” the one-unit presentation difference. Record it as reported rounding.

Also require parent equity and total equity to remain distinct because NCI is non-zero.

- [ ] **Step 4: Assert PDF source references**

Every anchor above must point to the source PDF and page specified in `docs/FAST_RETAILING_BENCHMARK.md`.

- [ ] **Step 5: Run the benchmark fact tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -k 'anchor or provenance or round_trip' -v
```

---

### Task 5: Run the current Step 9L.1 engine as an audit, not a repair exercise

**Files:**
- Create: `scripts/audit_fast_retailing_benchmark.py`
- Create: `benchmark/fast_retailing/BASELINE.md`
- Create: `benchmark/fast_retailing/GAPS.md`
- Modify: `core/tests/test_fast_retailing_benchmark.py`

**Interfaces:**

The audit runs these stages in order:

```text
1 source fixture load
2 standardized identity validation
3 financial reconciliation
4 ReferenceModelBuilder construction
5 Trainer / Answer Key generation
6 blank Check
7 filled-formula Check, only if stage 5 succeeds
```

- [ ] **Step 1: Implement a stage-result record**

Use a small dataclass or plain dict with:

```text
stage
status = pass | fail | skipped
exception_type
message
```

The audit must continue to write a report after the first production failure by marking later dependent stages `skipped`.

- [ ] **Step 2: Keep audit artifacts isolated**

Generate temporary workbooks under a temporary directory. Do not commit a Fast Retailing Trainer/Answer Key in Step 9M.0.

- [ ] **Step 3: Record module applicability before/where possible**

Report whether the source fixture makes these current modules applicable:

```text
earnings quality
working capital
fixed asset
lease liability
per share
normalization
```

Do not force a module on by adding invented inputs.

- [ ] **Step 4: Produce `BASELINE.md` deterministically**

Include:

```text
source commit / source hashes
model commit audited: 26f22b7
five fiscal periods
stage table
first failure, if any
applicable/omitted modules
no production fixes applied
```

Do not call the benchmark “passing” unless every stage actually passes.

- [ ] **Step 5: Add a smoke test for the audit script**

The test must require that the audit completes and writes all stage records. It must **not** encode a production failure as desirable behavior. Step 9M.0 tests verify observability of the result, not that a particular current failure persists forever.

---

### Task 6: Turn the observed baseline into a precise Step 9M.1 gap queue

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/PROVENANCE.md`
- Do not modify production `core/` accounting logic in this task.

**Interfaces:**
- `GAPS.md` is the sole evidence basis for the next engine-fix plan.

- [ ] **Step 1: Classify every observed failure**

Use exactly these categories:

```text
A source-extraction / provenance defect
B generic line-identity / resolver / classifier gap
C accounting-model scope gap
D optional-module input-contract gap
E comparative/restatement/share-basis conflict
```

For each gap record:

```text
stage
exact exception or mismatch
source fact(s) that trigger it
whether synthetic tests currently cover it
why the issue is generalizable beyond Fast Retailing
```

- [ ] **Step 2: Explicitly probe the known 2025 pressure points**

Even if they are not the first thrown exception, record the current behavior for:

1. **NCI / attribution:** total profit `459,153` versus parent-attributable profit `433,009`; total equity `2,327,501` versus parent equity `2,273,115`.
2. **Split leases:** current `126,830` and non-current `386,670` versus Note 17 aggregate `513,501`.
3. **Lease income-side consistency:** Note 17 lease interest `8,464` versus the current treatment-conditioned balance-sheet judgment and treatment-independent `compute_anchor()` net-interest logic.
4. **Generic financial rows:** other financial assets/liabilities and derivatives.
5. **Duplicate/current-vs-non-current source labels:** confirm whether concepts are sufficient to preserve identity without cosmetic relabeling.
6. **Share basis:** verify how the 2023 3-for-1 split affects FY2021/FY2022 comparability before enabling five-year per-share analysis.

- [ ] **Step 3: Do not prescribe speculative fixes**

`GAPS.md` may state the required invariant (for example, “parent-attributable earnings and equity must be handled consistently”), but Step 9M.0 must not redesign NCI, lease accounting, or classification architecture. ChatGPT will use the measured gaps to write Step 9M.1.

---

### Task 7: Protect existing synthetic behavior while adding the benchmark infrastructure

**Files:**
- Test: `core/tests/test_fast_retailing_benchmark.py`
- Test: existing historical suite
- Production model files should remain unchanged in Step 9M.0 unless a non-accounting benchmark utility import path absolutely requires a trivial change; prefer no `core/` production changes.

**Interfaces:**
- The benchmark adds evidence and tests without replacing existing fixtures.

- [ ] **Step 1: Require the pre-existing Step 9L.1 surface to remain unchanged**

Before finalizing, verify the existing suite still reports the same current surfaces recorded by Step 9L.1:

```text
active family orders 1..90
base demo 74 / 312
normalization demo 78 / 332
shares only 82 / 346
shares + normalization 90 / 384
services 59 / 248
retail 78 / 331
manufacturer 74 / 311
CLI {ingest, build, check, list}
```

- [ ] **Step 2: Require benchmark tests to be additive**

No existing synthetic assertion should be weakened to accommodate Fast Retailing.

- [ ] **Step 3: Verify the five PDFs are unchanged after all work**

Re-run the manifest hash test at the end.

---

### Task 8: Final Step 9M.0 verification and status

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Do not modify: `TARGET.md`
- Do not modify: `docs/FAST_RETAILING_BENCHMARK.md` unless a source citation/page error is proven during implementation

- [ ] **Step 1: Run benchmark-focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

- [ ] **Step 2: Run the benchmark audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Review `benchmark/fast_retailing/BASELINE.md` and `GAPS.md`. The command may report production stages as failed; that is valid for Step 9M.0 only if the failures are fully captured and no source-integrity test failed.

- [ ] **Step 3: Run the full existing historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

The old 316-test baseline must not regress; record the actual new total including benchmark tests.

- [ ] **Step 4: Verify source immutability and product boundaries**

Require:

```text
all five Fast Retailing PDF SHA-256 values unchanged
GOOGL workbook unchanged
no forecast/valuation activation
no new historical formula family
no Fast Retailing-specific production branch
no committed Fast Retailing Trainer/Answer Key yet
```

- [ ] **Step 5: Record evidence in `RESULT.md`**

Record at minimum:

```text
Step 9L.1 review accepted / findings
five source hashes verified
five-period source-fact fixture created
latest-audited-presentation precedence applied
number of overlap conflicts/restatements
2025 anchor checks passed
current engine audit stage results
applicable/omitted modules
number and categories of gaps
full pytest count
forecasting/valuation still deferred
```

- [ ] **Step 6: Mark Step 9M.0 complete only after the benchmark baseline is reproducible**

Then stop. Do **not** implement the gaps. The next ChatGPT planning checkpoint is Step 9M.1, whose scope must be derived from `benchmark/fast_retailing/GAPS.md` rather than guessed in advance.

---

## Definition of Done

Step 9M.0 is complete only when:

1. All five committed Fast Retailing CFS PDFs are hash-locked and unchanged.
2. FY2021–FY2025 audited primary-statement facts are captured in `source_facts.json` with page-level provenance.
3. Overlapping comparative years are checked before precedence is applied; conflicts are explicit.
4. A deterministic five-period `FastRetailing_Standardized.json` and separate `provenance.json` are generated from source facts.
5. No missing value is invented and no source row is renamed merely to make the current engine resolve it.
6. The FY2025 independent anchors in `docs/FAST_RETAILING_BENCHMARK.md` pass.
7. NCI/parent attribution, split lease balances, reported aggregate lease balance, lease interest, and stock-split/share-basis issues are explicitly audited.
8. The current Step 9L.1 engine is run stage-by-stage against the benchmark and `BASELINE.md` records exactly what passes/fails/skips.
9. Every observed gap is classified in `GAPS.md` with source evidence and generalizability rationale.
10. No Fast Retailing-specific accounting logic is added to production code.
11. Existing Step 9L.1 synthetic surfaces and tests do not regress.
12. Forecasting and valuation remain dormant.
13. Step 9M.1 is not implemented in this checkpoint.
