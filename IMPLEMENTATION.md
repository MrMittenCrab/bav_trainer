# Step 9M.1 — Generic Filing-JSON Input + Reconciliation Contract

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `3c3949fc64d06c3286acdeeae42dbf7ea05d9a31` (`Step 9M.0`). Implement only Step 9M.1. Use red/green TDD. Do not begin OpenAI API automation, forecasting, valuation, scenarios, or Step 9M.2 accounting fixes. Do not commit, push, reset, rebase, merge, or delete branches; the user owns checkpoint commits.

**Goal:** Generalize the Fast Retailing Step 9M.0 prototype into a reusable company-agnostic filing-JSON input pipeline: one source-grounded JSON per filing → validation/source binding → deterministic reconciliation → model-only `StandardizedFinancials` plus separate provenance/conflict artifacts.

**Architecture:** Introduce a small documentary data layer for `ExtractedFiling` that is deliberately upstream of BAV accounting logic. Validation binds each filing JSON to its source file by computing SHA-256 deterministically and rejects malformed/ambiguous evidence. Reconciliation retains every observation, deterministically selects later/restated audited presentations, emits conflicts/provenance, then standardizes only accepted reported facts into the existing model contract. Existing `build` continues to consume standardized JSON unchanged.

**Tech Stack:** Python stdlib (`dataclasses`, `enum`, `json`, `hashlib`, `pathlib`, `datetime`), pytest, existing `StandardizedFinancials` / `standardized_io`, existing CLI in `core/__main__.py`, existing Fast Retailing benchmark fixtures.

**Spec:** `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`

## Global Constraints

- `TARGET.md` already records the stable source-data architecture; Cursor treats it as read-only.
- Remain in Step 9 historical validation. Forecasting, valuation, scenarios, and investment conclusions remain deferred.
- Do **not** call OpenAI or any other AI API in Step 9M.1.
- Do **not** parse PDFs inside the BAV accounting engine.
- One extracted JSON file represents exactly one source filing.
- Extracted statement facts are documentary facts only; no BAV classification/normalization decisions belong in the extracted artifact.
- The LLM/extractor is not responsible for computing SHA-256. BAV computes source hashes deterministically during validation.
- `suggested_concept` is advisory and must never override an identity conflict silently.
- Missing facts are omitted, never invented.
- Source signs and units are preserved exactly; no `ABS()`, balancing plugs, unit conversions, or stock-split multipliers are inferred.
- Cross-filing disagreements must be recorded in `conflicts.json`; silent overwrites are forbidden.
- `StandardizedFinancials` remains model-only; provenance/conflicts remain sibling artifacts.
- Preserve existing `build`, `check`, `list`, and standardized-JSON behavior.
- Preserve Step 9M.0 measured accounting gaps G1–G7. This step builds the input architecture only.
- Synthetic demo/component surfaces and family orders `1..90` must remain unchanged.
- Cursor must not commit or push; stop after implementation/tests and let the user run `checkpoint`.

---

### Task 1: Add the generic documentary filing data contract and JSON loader

**Files:**
- Create: `core/data/filing.py`
- Create: `core/ingestion/filing_json.py`
- Create: `core/tests/test_filing_json.py`

**Interfaces:**

```python
class PresentationRole(str, Enum):
    CURRENT_PERIOD = "current_period"
    COMPARATIVE = "comparative"
    RESTATED_COMPARATIVE = "restated_comparative"
    PRIOR_PRESENTATION = "prior_presentation"

@dataclass(frozen=True)
class FilingValue:
    value: float
    presentation_role: PresentationRole

@dataclass(frozen=True)
class SourceRef:
    page: int
    statement: str = ""
    note: str = ""
    label: str = ""

@dataclass(frozen=True)
class ExtractedStatementRow:
    label: str
    section: str
    suggested_concept: str
    values: dict[date, FilingValue]
    source: SourceRef

@dataclass(frozen=True)
class SupplementalFact:
    fact_type: str
    period: date
    value: float
    status: str
    source: SourceRef
    derivation: str = ""

@dataclass(frozen=True)
class FilingMetadata:
    document_type: str
    fiscal_year: int
    period_end: date
    currency: str
    unit_scale: str
    source_file: str
    source_sha256: str = ""  # optional trusted upstream declaration

@dataclass(frozen=True)
class ExtractedFiling:
    schema_version: str
    company_name: str
    ticker: str
    stock_code: str
    jurisdiction: str
    filing: FilingMetadata
    income_statement: tuple[ExtractedStatementRow, ...]
    balance_sheet: tuple[ExtractedStatementRow, ...]
    cash_flow: tuple[ExtractedStatementRow, ...]
    note_facts: tuple[SupplementalFact, ...]
    share_facts: tuple[SupplementalFact, ...]


def load_extracted_filing(path: Path) -> ExtractedFiling:
    ...


def extracted_filing_to_payload(filing: ExtractedFiling) -> dict:
    ...
```

- [ ] **Step 1: Write a minimal valid-filing round-trip test**

Create a temporary FY2025 JSON fixture matching spec v1.0 with Revenue and one current lease-liability row. Require:

```python
filing = load_extracted_filing(path)
assert filing.schema_version == "1.0"
assert filing.filing.period_end == date(2025, 8, 31)
assert filing.income_statement[0].values[date(2025, 8, 31)].value == 3_400_539
assert filing.balance_sheet[0].section == "Current liabilities"
assert extracted_filing_to_payload(filing) == json.loads(path.read_text())
```

The fixture should omit `source_sha256` to prove the extractor does not need to invent it.

- [ ] **Step 2: Write parser rejection tests**

Require `ValueError` for:

```text
schema_version != 1.0
unknown document_type
unknown unit_scale
invalid date
unknown presentation_role
statement value that is a string
statement row with no source page
supplemental status outside reported/derived
derived supplemental fact without derivation
```

- [ ] **Step 3: Run the new tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

Expected: import/module failures because the contract does not exist yet.

- [ ] **Step 4: Implement the dataclasses/enums**

Use exact enum values from the spec. `ALLOWED_UNIT_SCALES` is exactly:

```python
{"ones", "thousands", "millions", "billions"}
```

`ALLOWED_DOCUMENT_TYPES` is exactly:

```python
{"annual_report", "interim_report", "results_announcement"}
```

Statement arrays accept reported numeric values only. Missing periods are absent keys, not implicit zeroes.

- [ ] **Step 5: Implement strict loader/serializer**

Preserve original `label` and `section` strings. Convert only dates/enums/numeric values into typed representations. Do not call `normalize_label()` on stored documentary text.

If optional `source_sha256` is absent, keep it empty internally and omit it again on serialization so round-trip shape is stable.

- [ ] **Step 6: Run the focused tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

---

### Task 2: Add source binding and filing validation

**Files:**
- Create: `core/ingestion/filing_validator.py`
- Modify: `core/tests/test_filing_json.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class FilingValidationIssue:
    severity: str  # "error" | "warning"
    code: str
    message: str

@dataclass(frozen=True)
class FilingValidationReport:
    issues: tuple[FilingValidationIssue, ...]
    computed_source_sha256: str | None

    @property
    def errors(self) -> tuple[FilingValidationIssue, ...]: ...

    @property
    def warnings(self) -> tuple[FilingValidationIssue, ...]: ...

    @property
    def ok(self) -> bool: ...


def source_row_identity(statement: str, row: ExtractedStatementRow) -> str:
    ...


def validate_extracted_filing(
    filing: ExtractedFiling,
    *,
    source_root: Path | None = None,
) -> FilingValidationReport:
    ...
```

- [ ] **Step 1: Write computed source-hash tests**

Create a small fake source file and require:

```python
report = validate_extracted_filing(filing, source_root=tmp_path)
assert report.ok
assert report.computed_source_sha256 == hashlib.sha256(source_bytes).hexdigest()
```

Do not mutate or rewrite the extracted JSON.

If the optional trusted `source_sha256` is declared, change one byte in the source and require error code:

```text
source_hash_mismatch
```

An absent source file must produce:

```text
source_file_missing
```

- [ ] **Step 2: Write duplicate-identity tests**

The identity must distinguish:

```text
balance_sheet | Current liabilities | Lease liabilities | lease_liability_current
balance_sheet | Non-current liabilities | Lease liabilities | lease_liability_noncurrent
```

but two rows with the same statement/section/label/suggested-concept must produce hard error:

```text
duplicate_source_row_identity
```

- [ ] **Step 3: Write filing-period consistency tests**

Every filing must contain at least one `current_period` observation equal to `filing.period_end`. A `current_period` observation for a different date is an error:

```text
current_period_mismatch
```

- [ ] **Step 4: Run focused tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

- [ ] **Step 5: Implement identity normalization**

Normalize only for matching:

```python
def _match_text(value: str) -> str:
    return " ".join(value.casefold().split())
```

Identity format:

```text
{statement}|{normalized section}|{normalized label}|{normalized suggested_concept}
```

Original documentary strings remain unchanged in `ExtractedFiling`.

- [ ] **Step 6: Implement validation without mutation**

When `source_root` is provided, compute SHA-256 from `source_root / filing.source_file`. Compare it with `source_sha256` only when a declaration exists. Return the computed hash in the report for provenance.

Validation reports issues; it never rewrites values, labels, units, hashes, or presentation roles.

- [ ] **Step 7: Run focused tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

---

### Task 3: Add deterministic cross-filing reconciliation and conflict recording

**Files:**
- Create: `core/ingestion/filing_reconciler.py`
- Create: `core/tests/test_filing_reconciler.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class FilingObservation:
    filing_year: int
    source_file: str
    source_sha256: str
    pdf_page: int
    presentation_role: PresentationRole
    value: float

@dataclass(frozen=True)
class ReconciledValue:
    statement: str
    row_identity: str
    period: date
    label: str
    section: str
    suggested_concept: str
    selected: FilingObservation
    observations: tuple[FilingObservation, ...]

@dataclass(frozen=True)
class ReconciliationConflict:
    statement: str
    row_identity: str
    period: date
    observations: tuple[FilingObservation, ...]
    selected: FilingObservation
    reason: str

@dataclass(frozen=True)
class ReconciledCompanyData:
    company_name: str
    ticker: str
    stock_code: str
    jurisdiction: str
    currency: str
    unit_scale: str
    periods: tuple[date, ...]
    values: tuple[ReconciledValue, ...]
    conflicts: tuple[ReconciliationConflict, ...]
    note_facts: tuple[SupplementalFact, ...]
    share_facts: tuple[SupplementalFact, ...]


def reconcile_filings(
    filings: list[tuple[ExtractedFiling, FilingValidationReport]],
) -> ReconciledCompanyData:
    ...
```

- [ ] **Step 1: Write matching-comparative test**

FY2024 current-period Revenue `100` and FY2025 comparative FY2024 Revenue `100` must produce one reconciled FY2024 value, retain two observations, and produce no conflict.

- [ ] **Step 2: Write later-comparative conflict test**

FY2024 current-period Revenue `100` and FY2025 comparative Revenue `101` must select the FY2025 observation and create exactly one conflict with reason:

```text
later_audited_presentation
```

- [ ] **Step 3: Write restated-comparative precedence test**

Given:

```text
FY2024 current_period = 100
FY2025 comparative = 101
FY2025 restated_comparative = 99
```

require selection of `99` and conflict reason:

```text
restated_comparative_precedence
```

- [ ] **Step 4: Write `prior_presentation` precedence test**

A `prior_presentation` observation must never override an otherwise valid current/comparative observation, even when it comes from a later filing.

- [ ] **Step 5: Write metadata incompatibility tests**

Require hard `ValueError` before value selection when filings disagree on:

```text
company/ticker identity
currency
unit_scale
jurisdiction
```

No currency/unit conversion exists in Step 9M.1.

- [ ] **Step 6: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [ ] **Step 7: Implement deterministic ranking**

Use:

```python
ROLE_RANK = {
    PresentationRole.RESTATED_COMPARATIVE: 3,
    PresentationRole.CURRENT_PERIOD: 2,
    PresentationRole.COMPARATIVE: 2,
    PresentationRole.PRIOR_PRESENTATION: 1,
}
```

Select by `(ROLE_RANK[role], filing_year)`. Equal-value observations remain provenance but do not create a conflict. Different values always create a conflict.

Carry `computed_source_sha256` from each validation report into every `FilingObservation`; reconciliation must not ask the extractor to supply it.

- [ ] **Step 8: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 4: Convert reconciled documentary facts into model-only standardized data + audit artifacts

**Files:**
- Create: `core/ingestion/filing_standardizer.py`
- Modify: `core/tests/test_filing_reconciler.py`

**Interfaces:**

```python
def standardize_reconciled(
    reconciled: ReconciledCompanyData,
) -> StandardizedFinancials:
    ...


def reconciliation_provenance_payload(
    reconciled: ReconciledCompanyData,
) -> dict:
    ...


def reconciliation_conflicts_payload(
    reconciled: ReconciledCompanyData,
) -> dict:
    ...
```

- [ ] **Step 1: Write complete-axis emission test**

For model periods FY2024/FY2025, a Revenue row observed for both periods must emit one `LineItem` with both values.

A row observed only for FY2025 must **not** enter `StandardizedFinancials`; it must appear in provenance with:

```text
status = omitted_incomplete_axis
```

- [ ] **Step 2: Write concept-preservation test**

A unique reconciled `suggested_concept="revenue"` must become `LineItem.concept == "revenue"`.

The standardizer must not normalize/change the selected display label.

- [ ] **Step 3: Write supplemental non-promotion test**

A reported note fact such as `lease_liability_total` remains provenance/supplemental evidence and is not automatically inserted into the Balance Sheet.

A `derived` supplemental fact is likewise never promoted.

- [ ] **Step 4: Write historical-share gating test**

Only a full-axis explicit reported series of `diluted_weighted_average_shares` with a single consistent scale basis may produce `HistoricalShareData`.

If FY2021/FY2022 are missing or only basic/dilutive components exist, `historical_shares` must remain `None`.

- [ ] **Step 5: Run tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [ ] **Step 6: Implement standardization**

Use the existing `StandardizedFinancials`, `FinancialPeriod`, `LineItem`, `HistoricalShareData`, and `standardized_to_payload()` without adding source/provenance fields to the model-only serializer.

- [ ] **Step 7: Implement deterministic audit payloads**

`provenance.json` must include every observation, computed source SHA-256, selected observation, selection rule, omitted incomplete-axis rows, note facts, and share facts.

`conflicts.json` must contain only actual numeric disagreements plus selection reason.

Sort output deterministically by statement, row identity, period, and filing year.

- [ ] **Step 8: Run tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 5: Add generic CLI commands without changing the existing build contract

**Files:**
- Modify: `core/__main__.py`
- Create: `core/tests/test_filing_cli.py`

**Interfaces:**

Add commands:

```text
validate-source
reconcile
```

Do not add `extract` in Step 9M.1.

- [ ] **Step 1: Write CLI parser/help tests**

Require `python -m core --help` to contain:

```text
validate-source
reconcile
build
check
list
```

Existing commands remain available.

- [ ] **Step 2: Write `validate-source` success/failure tests**

For a directory of valid extracted JSON files:

```bash
python -m core validate-source <dir> --source-root <source-dir>
```

must exit `0`, compute source hashes, and print one compact summary.

A declared-hash mismatch must exit nonzero and identify `source_hash_mismatch` without rewriting files.

- [ ] **Step 3: Write `reconcile` artifact test**

```bash
python -m core reconcile <extracted-dir> --source-root <source-dir> -o <out-dir>
```

must create exactly:

```text
standardized.json
provenance.json
conflicts.json
```

for the reconciliation outputs.

- [ ] **Step 4: Run CLI tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_cli.py -v
```

- [ ] **Step 5: Implement shared directory loading**

Only load `*.json` regular files in lexical order. Reject an empty directory. Do not recursively search arbitrary directories in v1.

- [ ] **Step 6: Implement `validate-source`**

Require `--source-root` for CLI validation so hashes are actually bound. Validation is all-or-nothing for hard errors. Warnings print but do not change source JSON.

- [ ] **Step 7: Implement `reconcile`**

Require `--source-root`. Validate/bind first. If any hard error exists, write no reconciled artifacts. Otherwise reconcile and write deterministic JSON using `standardized_to_payload()`, `reconciliation_provenance_payload()`, and `reconciliation_conflicts_payload()`.

- [ ] **Step 8: Run CLI tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_cli.py -v
```

---

### Task 6: Migrate the Fast Retailing benchmark onto five independent extracted filing JSON files

**Files:**
- Create directory: `benchmark/fast_retailing/extracted/`
- Create: `benchmark/fast_retailing/extracted/FY2021.json`
- Create: `benchmark/fast_retailing/extracted/FY2022.json`
- Create: `benchmark/fast_retailing/extracted/FY2023.json`
- Create: `benchmark/fast_retailing/extracted/FY2024.json`
- Create: `benchmark/fast_retailing/extracted/FY2025.json`
- Create directory: `benchmark/fast_retailing/reconciled/`
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Modify: `scripts/audit_fast_retailing_benchmark.py`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `benchmark/fast_retailing/PROVENANCE.md`

**Interfaces:**
- The five JSON files are the first canonical real-company `ExtractedFiling` fixtures.
- Generic reconciliation writes benchmark outputs under `benchmark/fast_retailing/reconciled/`.

- [ ] **Step 1: Add a migration acceptance test before changing fixtures**

From existing Step 9M.0 evidence, record the expected FY2025 anchors:

```text
Revenue                         3,400,539
Profit before income taxes        650,574
Income tax expense               -191,421
Cash and cash equivalents          893,239
PP&E                               332,351
Current lease liabilities          126,830
Non-current lease liabilities      386,670
Operating cash flow                580,618
D&A                                216,492
PP&E cash payments                -135,535
```

Require the new generic pipeline to reproduce those exact selected values and page provenance.

- [ ] **Step 2: Split `source_facts.json` into five v1.0 filing artifacts**

Use `source_manifest.json` only as migration evidence for filenames/hashes; the new extracted JSON does not need the LLM to restate hashes.

Convert each old statement row into the new row/value shape with explicit `presentation_role`:

```text
period == filing period_end -> current_period
older comparative period   -> comparative
```

Where Step 9M.0 already documented an audited restatement, mark the later observation `restated_comparative` rather than hiding the conflict.

Do not re-read/reinterpret the PDFs in this migration task; preserve the already-audited 9M.0 facts exactly.

- [ ] **Step 3: Run generic validation over all five files**

```bash
PYTHONPATH=. python -m core validate-source \
  benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source
```

Expected: zero hard validation errors and five computed source hashes matching `source_manifest.json`.

- [ ] **Step 4: Reconcile through the generic command**

```bash
PYTHONPATH=. python -m core reconcile \
  benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source \
  -o benchmark/fast_retailing/reconciled
```

- [ ] **Step 5: Assert conflict parity**

The generic `conflicts.json` must preserve the three open audited overlap conflicts recorded by Step 9M.0 after the closed 2021 NCI transcription correction. Do not silently reduce the count by choosing one value without conflict evidence.

- [ ] **Step 6: Assert source/provenance parity**

Every selected Fast Retailing model value must retain filing filename + PDF page + computed PDF hash. The FY2025 Revenue selection must point to `Fastretailing_CFS2025.pdf`, page `3`.

- [ ] **Step 7: Update the benchmark audit script to load `reconciled/standardized.json`**

Remove dependence on `scripts/build_fast_retailing_benchmark.py` for normal benchmark execution. The audit still measures Step 9M.0/9M.1 engine stages and must continue to expose the same downstream accounting gaps until Step 9M.2.

- [ ] **Step 8: Run benchmark tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 7: Retire the company-specific reconciliation path after parity is proven

**Files:**
- Delete: `scripts/build_fast_retailing_benchmark.py`
- Delete: `benchmark/fast_retailing/source_facts.json`
- Modify: `README.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes

**Interfaces:**
- There is one generic filing-JSON reconciliation path for future projects.
- Fast Retailing uses the same path as any future company.

- [ ] **Step 1: Search for legacy references before deletion**

```bash
grep -R "source_facts.json\|build_fast_retailing_benchmark" -n . \
  --exclude-dir=.git \
  --exclude='*.pdf'
```

Update all active tests/docs/scripts so the only remaining references, if any, are clearly historical descriptions.

- [ ] **Step 2: Delete the legacy bundle/builder only after Tasks 1–6 pass**

Do not delete the five original PDFs, `source_manifest.json`, Step 9M.0 `GAPS.md`, or historical benchmark documentation.

- [ ] **Step 3: Update README with the new normal handoff**

Keep it concise. Document:

```text
PDF/filing → extracted JSON per filing → validate-source → reconcile → build
```

State that automatic PDF/AI extraction is not yet part of the CLI.

- [ ] **Step 4: Update the skill instructions**

Require future LLM-assisted extraction to produce v1.0 filing JSON, not directly fill `StandardizedFinancials` or Excel. Preserve the rule that BAV accounting judgments occur after documentary extraction and that BAV computes source hashes.

- [ ] **Step 5: Update RESULT.md**

Record:

```text
Step 9M.1 complete
five Fast Retailing extracted filings validated
reconciliation artifacts deterministic
generic pipeline reproduces accepted benchmark facts/conflicts
existing Step 9M.0 accounting gaps intentionally remain for 9M.2
OpenAI API extraction not implemented
```

- [ ] **Step 6: Run the legacy-reference search again**

```bash
grep -R "source_facts.json\|build_fast_retailing_benchmark" -n . \
  --exclude-dir=.git \
  --exclude='*.pdf'
```

Expected: no active runtime/test dependency on the deleted files.

---

### Task 8: Final Step 9M.1 verification and stop gate

**Files:**
- Modify: `IMPLEMENTATION.md` status line only after all checks below pass
- Do not modify production accounting modules to make Fast Retailing build farther than the measured gap queue permits.

- [ ] **Step 1: Run focused input-pipeline tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_filing_json.py \
  core/tests/test_filing_reconciler.py \
  core/tests/test_filing_cli.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Expected: all pass.

- [ ] **Step 2: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass; no synthetic surface regressions.

- [ ] **Step 3: Verify CLI surface**

```bash
PYTHONPATH=. python -m core --help
```

Expected command set includes:

```text
ingest
validate-source
reconcile
build
check
list
```

No `extract` command yet.

- [ ] **Step 4: Verify deterministic reconciliation**

Run `reconcile` twice into two temporary directories and compare:

```bash
diff -u /tmp/fr1/standardized.json /tmp/fr2/standardized.json
diff -u /tmp/fr1/provenance.json /tmp/fr2/provenance.json
diff -u /tmp/fr1/conflicts.json /tmp/fr2/conflicts.json
```

Expected: no differences.

- [ ] **Step 5: Re-run the Fast Retailing engine audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

The source/reconciliation pipeline should pass. Downstream accounting-engine gaps from `benchmark/fast_retailing/GAPS.md` remain explicitly open for Step 9M.2; do not repair them in this checkpoint merely to make the audit greener.

- [ ] **Step 6: Confirm no new formula families or forecasting activation**

Existing active family orders remain `1..90`; deferred model/scenario tabs remain inactive; no valuation or forecasting code becomes part of normal build execution.

- [ ] **Step 7: Mark Step 9M.1 complete only with evidence**

At the top of `IMPLEMENTATION.md`, add a compact status line containing the actual final test counts and generic Fast Retailing reconciliation result. Do not prestate counts before running the suite.

- [ ] **Step 8: Stop**

Do not begin Step 9M.2. Return implementation/test summary to the user so they can run `checkpoint`.
