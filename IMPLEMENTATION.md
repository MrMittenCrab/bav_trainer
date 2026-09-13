# Step 9M.1.1 — Filing-JSON Provenance + Validation Hardening

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `e5fa7b87110a3a03c06349a35af6d662a880f88f` (`Step 9M.1`). Implement only Step 9M.1.1 using red/green TDD. Do not begin Step 9M.2 accounting fixes, OpenAI/API extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Harden the new filing-JSON boundary so malformed source metadata fails closed, every reconciled documentary fact remains source-bound, repeated supplemental facts cannot silently overwrite each other, and Step 9M.1 introduces no unrelated workbook drift.

**Architecture:** Keep `ExtractedFiling` as the immutable documentary contract and `StandardizedFinancials` as the model-only contract. Harden the boundary in four places: strict parsing/path containment, explicit bound-source provenance, source-bound supplemental observations with deterministic conflict handling, and regression protection for unrelated synthetic workbook artifacts. Do not change BAV accounting formulas or the Fast Retailing G1–G7 engine gap queue.

**Tech Stack:** Python stdlib (`dataclasses`, `json`, `hashlib`, `pathlib`, `datetime`), pytest, existing filing JSON/validator/reconciler/standardizer modules, existing CLI, Fast Retailing benchmark fixtures.

**Spec:** `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`

## Review findings this step must close

1. `reconciliation_provenance_payload()` serializes `note_facts` / `share_facts` without filing year, source filename, or computed SHA-256, so supplemental evidence loses its source binding after reconciliation.
2. `_historical_shares()` writes repeated share facts into a dict keyed only by period. Conflicting cross-filing values can therefore be selected by iteration order without a conflict record.
3. Required metadata parsing is not fail-closed: company/ticker/jurisdiction/currency can become empty strings, `fiscal_year` uses a permissive cast, and `_parse_date()` truncates strings to the first 10 characters before parsing.
4. `source_file` is joined directly to `source_root`; an absolute path or `..` traversal can escape the intended source directory.
5. The top-level provenance `source_files` list is derived only from selected statement observations. A bound filing must remain represented even if all of its overlapping statement observations lose selection precedence or it contributes only supplemental evidence.
6. `example/DEMO_HK_Trainer.xlsx` changed in Step 9M.1 although the step was an input-pipeline migration and synthetic workbook surfaces were supposed to remain unchanged. Unless a reproducible reason is found, restore the pre-9M.1 workbook bytes.

## Global constraints

- `TARGET.md` is read-only for Cursor.
- Preserve one extracted JSON file per source filing.
- Preserve original documentary labels, sections, signs, units, page references, and numeric values.
- `suggested_concept` remains advisory only.
- `StandardizedFinancials` remains model-only; do not add source/provenance fields to it.
- No PDF parsing or AI/API calls in this step.
- Do not infer unit conversions, stock-split multipliers, balancing plugs, missing facts, or accounting classifications.
- Cross-filing numeric disagreements must never be silently overwritten.
- Preserve existing primary-statement precedence semantics and the three Fast Retailing statement overlap conflicts.
- Fast Retailing `historical_shares` remains omitted unless a complete, unambiguous reported diluted-WAS axis exists.
- Preserve Step 9M.0/9M.1 accounting gaps G1–G7 for Step 9M.2.
- Preserve CLI commands `{ingest, validate-source, reconcile, build, check, list}`; do not add `extract`.
- Preserve active family orders `1..90` and all synthetic workbook surfaces.
- Cursor stops after implementation/tests and reports results; the user runs `checkpoint`.

---

### Task 1: Make filing metadata parsing strict and exact

**Files:**
- Modify: `core/ingestion/filing_json.py`
- Test: `core/tests/test_filing_json.py`

**Interfaces:**
- `load_extracted_filing(path: Path) -> ExtractedFiling` remains unchanged.
- `extracted_filing_to_payload(filing: ExtractedFiling) -> dict` remains unchanged.

- [ ] **Step 1: Add failing tests for required metadata**

Create parameterized cases requiring clean `ValueError` rather than `KeyError`, raw `TypeError`, or permissive coercion for:

```text
missing company object
blank company.name
blank company.ticker
blank company.jurisdiction
missing filing.fiscal_year
filing.fiscal_year = true
filing.fiscal_year = "2025"
filing.fiscal_year = 0
blank filing.currency
blank filing.source_file
```

`stock_code` may remain empty because ticker-only identities are allowed.

- [ ] **Step 2: Add failing exact-date tests**

Require `ValueError` for all of:

```text
"2025-08-31junk"
"2025-08-31T00:00:00"
"2025/08/31"
"2025-02-30"
```

Require exact acceptance of:

```text
"2025-08-31"
```

The parser must not slice or truncate date strings before validation.

- [ ] **Step 3: Run the parser tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

Expected: the new strict-metadata/date cases fail on the Step 9M.1 implementation.

- [ ] **Step 4: Implement explicit required-field helpers**

Use helpers with strict types rather than `str(...)` / `int(...)` coercion:

```python
def _required_nonempty_str(payload: dict, key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} is required")
    return value


def _required_positive_int(payload: dict, key: str, *, context: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{context}.{key} must be a positive integer")
    return value
```

Required non-empty strings in v1.0:

```text
company.name
company.ticker
company.jurisdiction
filing.currency
filing.source_file
```

Keep existing enum validation for `document_type` and `unit_scale`.

Preserve accepted documentary strings verbatim; `.strip()` is only an emptiness test.

- [ ] **Step 5: Implement exact ISO date parsing**

Replace truncation logic with exact parsing:

```python
def _parse_date(value: object) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError(f"invalid date: {value!r}")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid date: {value!r}") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"invalid date: {value!r}")
    return parsed
```

- [ ] **Step 6: Run parser tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py -v
```

---

### Task 2: Enforce portable source paths before reading source bytes

**Files:**
- Modify: `core/ingestion/filing_validator.py`
- Test: `core/tests/test_filing_json.py`
- Test: `core/tests/test_filing_cli.py`

**Interfaces:**
- `validate_extracted_filing(filing, source_root=...) -> FilingValidationReport` remains unchanged.
- Add hard issue code `invalid_source_path`.

- [ ] **Step 1: Add validator traversal tests**

Reject with `invalid_source_path`:

```text
/Users/name/report.pdf
../report.pdf
subdir/../../report.pdf
```

Also reject Windows-style absolute input even when tests run on macOS/Linux:

```text
C:\Users\name\report.pdf
```

Allow a safe nested relative path:

```text
annual/FY2025.pdf
```

- [ ] **Step 2: Add a no-read escape regression**

Create a real file outside `source_root` and point the filing at `../outside.pdf`. Require:

```text
report.ok == False
issue code == invalid_source_path
report.computed_source_sha256 is None
```

The validator must reject containment before calling `is_file()`, `read_bytes()`, or hashing the escaped candidate.

- [ ] **Step 3: Add CLI regression**

For both commands:

```bash
python -m core validate-source <extracted> --source-root <root>
python -m core reconcile <extracted-dir> --source-root <root> -o <out>
```

require nonzero exit for an escaped path, visible `invalid_source_path`, and no reconciled artifacts written.

- [ ] **Step 4: Run focused tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_cli.py -v
```

- [ ] **Step 5: Implement cross-platform path validation**

Before source access:

```python
from pathlib import Path, PureWindowsPath

raw = filing.filing.source_file
if Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
    # invalid_source_path

root = Path(source_root).resolve()
candidate = (root / raw).resolve()
try:
    candidate.relative_to(root)
except ValueError:
    # invalid_source_path
```

Only after containment succeeds may the validator test file existence and compute SHA-256.

Do not use string-prefix containment checks.

- [ ] **Step 6: Run focused tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_cli.py -v
```

---

### Task 3: Preserve an explicit registry of every validated bound source

**Files:**
- Modify: `core/ingestion/filing_reconciler.py`
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`

**Interfaces:**

Add:

```python
@dataclass(frozen=True)
class BoundSourceFile:
    filing_year: int
    source_file: str
    source_sha256: str
```

Add to `ReconciledCompanyData`:

```python
source_files: tuple[BoundSourceFile, ...]
```

- [ ] **Step 1: Write a failing complete-source-registry test**

Create two validated filings for the same company where the later filing wins all overlapping statement selections. Require both source files to remain in `reconciled.source_files`.

- [ ] **Step 2: Write provenance payload regression**

Require `reconciliation_provenance_payload()` top-level `source_files` to contain every bound filing exactly once with:

```json
{
  "filing_year": 2025,
  "source_file": "FY2025.pdf",
  "source_sha256": "..."
}
```

The registry must not be reconstructed only from selected statement observations.

- [ ] **Step 3: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [ ] **Step 4: Populate source registry directly from validated filing/report pairs**

In `reconcile_filings()`, build one `BoundSourceFile` for each input pair using `report.computed_source_sha256`. Sort deterministically by:

```text
filing_year, source_file, source_sha256
```

Do not derive this registry from selected values.

- [ ] **Step 5: Serialize the explicit registry**

Make `reconciliation_provenance_payload()` use `reconciled.source_files` directly.

- [ ] **Step 6: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 4: Preserve source binding for every supplemental fact

**Files:**
- Modify: `core/ingestion/filing_reconciler.py`
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`

**Interfaces:**

Add a reconciled wrapper without changing the extraction schema:

```python
@dataclass(frozen=True)
class SupplementalObservation:
    kind: str  # "note" | "share"
    filing_year: int
    source_file: str
    source_sha256: str
    fact: SupplementalFact
```

Change:

```python
ReconciledCompanyData.note_facts: tuple[SupplementalObservation, ...]
ReconciledCompanyData.share_facts: tuple[SupplementalObservation, ...]
```

- [ ] **Step 1: Write source-provenance regression**

Create FY2024/FY2025 filings containing note/share facts. After reconciliation require every supplemental observation to retain:

```text
kind
filing_year
source_file
computed source SHA-256
fact source page
fact source note/label/statement where present
```

The SHA comes from `FilingValidationReport.computed_source_sha256`, never from the extracted JSON unless validation confirms that declaration.

- [ ] **Step 2: Write provenance serializer regression**

Require each `note_facts` / `share_facts` entry in `provenance.json` to include filing provenance and fact provenance:

```json
{
  "filing_year": 2025,
  "source_file": "FY2025.pdf",
  "source_sha256": "...",
  "fact_type": "lease_liability_total",
  "period": "2025-08-31",
  "value": 123,
  "status": "reported",
  "source": {"page": 10}
}
```

Derived facts retain their `derivation` string.

- [ ] **Step 3: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [ ] **Step 4: Wrap supplemental facts while filing/report context still exists**

Do not concatenate naked `SupplementalFact` objects after source context has been lost.

Sort supplemental observations deterministically by:

```text
kind, fact_type, period, filing_year, source_file, source.page
```

- [ ] **Step 5: Update supplemental provenance serialization**

Replace `_fact_payload(fact)` with a serializer consuming `SupplementalObservation`.

Do not promote note facts into statements.

- [ ] **Step 6: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 5: Eliminate silent cross-filing overwrite of supplemental facts

**Files:**
- Modify: `core/ingestion/filing_reconciler.py`
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`

**Interfaces:**

Add:

```python
@dataclass(frozen=True)
class SupplementalConflict:
    kind: str
    fact_type: str
    period: date
    observations: tuple[SupplementalObservation, ...]
    reason: str
```

Add:

```python
ReconciledCompanyData.supplemental_conflicts: tuple[SupplementalConflict, ...]
```

- [ ] **Step 1: Write agreeing repeated-share test**

FY2024 and FY2025 may both report the same FY2024 `diluted_weighted_average_shares`. Require:

```text
both observations retained
no supplemental conflict
one unambiguous numeric FY2024 value available for share-axis gating
```

- [ ] **Step 2: Write disagreeing repeated-share test**

If the two filings report different FY2024 diluted WAS values, require:

```text
both observations retained
one SupplementalConflict(kind="share", ...)
no iteration-order selection
historical_shares is None
```

Do not select the later filing: supplemental v1.0 facts have no `presentation_role`. Agreement is required until a future supplemental-restatement contract exists.

- [ ] **Step 3: Write complete-axis share promotion test**

For a two-period axis, emit `HistoricalShareData` only when each period has at least one `reported` `diluted_weighted_average_shares` observation and all reported observations for that period agree numerically.

Derived share facts do not satisfy the axis requirement.

- [ ] **Step 4: Write note-fact disagreement test**

Two reported `lease_liability_total` observations for the same period with different values must create one supplemental conflict and retain both source-bound observations. Neither value is promoted into `StandardizedFinancials`.

- [ ] **Step 5: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [ ] **Step 6: Implement deterministic supplemental conflict grouping**

Group only `reported` supplemental observations by:

```text
(kind, fact_type, period)
```

If the distinct numeric-value set has more than one member, create one conflict with:

```text
reason = cross_filing_supplemental_disagreement
```

Derived facts remain provenance but do not determine reported-value agreement.

- [ ] **Step 7: Make `_historical_shares()` agreement-based**

For each model period:

```text
collect reported share observations of fact_type diluted_weighted_average_shares
require at least one observation
compute distinct numeric values
require exactly one distinct value
use that value
```

If any model period is missing or disagreeing, return `None`.

- [ ] **Step 8: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 6: Extend `conflicts.json` without changing statement-conflict semantics

**Files:**
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`
- Test: `core/tests/test_fast_retailing_benchmark.py`

**Interfaces:**

Keep existing primary-statement fields and add:

```json
{
  "conflicts": [...],
  "overlap_conflict_count": 3,
  "supplemental_conflicts": [...],
  "supplemental_conflict_count": 0
}
```

`overlap_conflict_count` continues to mean primary-statement numeric overlap conflicts.

- [ ] **Step 1: Write supplemental-conflict payload test**

Require every supplemental-conflict observation to include:

```text
filing_year
source_file
source_sha256
source.page
fact_type
period
value
status
```

- [ ] **Step 2: Preserve Fast Retailing primary statement count**

Require:

```text
overlap_conflict_count == 3
```

Do not pre-state the Fast Retailing supplemental conflict count. Measure it from the source evidence after implementation.

- [ ] **Step 3: Run tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -v
```

- [ ] **Step 4: Implement deterministic serialization**

Sort supplemental conflicts by:

```text
kind, fact_type, period
```

Sort observations within each conflict by:

```text
filing_year, source_file, source.page, value
```

Agreeing duplicate observations remain in provenance and are not conflicts.

- [ ] **Step 5: Run tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 7: Remove unrelated synthetic workbook drift

**Files:**
- Restore if no justified reproducible change exists: `example/DEMO_HK_Trainer.xlsx`
- Test: existing synthetic trainer/workbook tests

**Baseline:** Step 9M.1 implementation commit `e5fa7b87` changed this binary workbook even though the accepted implementation base immediately before Step 9M.1 was `1f4bdfd6a39898d0f368e81318560cd0fe3d0c59` and Step 9M.1 did not intentionally alter trainer workbook behavior.

- [ ] **Step 1: Verify the workbook change is unrelated**

Run:

```bash
git diff --stat 1f4bdfd6a39898d0f368e81318560cd0fe3d0c59..e5fa7b87110a3a03c06349a35af6d662a880f88f -- example/DEMO_HK_Trainer.xlsx
git diff --name-only 1f4bdfd6a39898d0f368e81318560cd0fe3d0c59..e5fa7b87110a3a03c06349a35af6d662a880f88f -- example/DEMO_HK_Trainer.xlsx
```

Expected: the file is reported as changed even though Step 9M.1 added no intended workbook feature.

- [ ] **Step 2: Restore the pre-9M.1 workbook bytes**

Unless Cursor can identify and document a deterministic Step 9M.1 requirement for this binary change, restore only this file:

```bash
git restore --source=1f4bdfd6a39898d0f368e81318560cd0fe3d0c59 -- example/DEMO_HK_Trainer.xlsx
```

This restores one file only; it is not a branch reset.

- [ ] **Step 3: Verify no other example workbook changed in this hardening step**

```bash
git status --short example/
```

Expected: only the intentional restoration of `DEMO_HK_Trainer.xlsx` may appear as a working-tree change relative to the current branch head.

- [ ] **Step 4: Run existing synthetic workbook tests**

Use the existing relevant trainer/workbook tests already in `core/tests/`; do not regenerate example workbooks merely to make hashes change.

---

### Task 8: Regenerate and audit Fast Retailing artifacts

**Files:**
- Modify generated artifacts only as required:
  - `benchmark/fast_retailing/reconciled/provenance.json`
  - `benchmark/fast_retailing/reconciled/conflicts.json`
- `benchmark/fast_retailing/reconciled/standardized.json` should remain model-equivalent and normally byte-identical.
- Modify: `benchmark/fast_retailing/PROVENANCE.md`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Test: `core/tests/test_fast_retailing_benchmark.py`

- [ ] **Step 1: Add Fast Retailing provenance assertions**

For every reconciled `note_facts` and `share_facts` item require non-empty:

```text
source_file
source_sha256
filing_year
source.page
```

Require top-level `source_files` to contain all five Fast Retailing filings with non-empty computed hashes.

Continue to require FY2025 statement anchors and exactly three primary-statement overlap conflicts.

- [ ] **Step 2: Run generic reconciliation twice**

```bash
rm -rf /tmp/fr-hardening-1 /tmp/fr-hardening-2
PYTHONPATH=. python -m core reconcile benchmark/fast_retailing/extracted --source-root benchmark/fast_retailing/source -o /tmp/fr-hardening-1
PYTHONPATH=. python -m core reconcile benchmark/fast_retailing/extracted --source-root benchmark/fast_retailing/source -o /tmp/fr-hardening-2
diff -ru /tmp/fr-hardening-1 /tmp/fr-hardening-2
```

Expected: no differences.

- [ ] **Step 3: Compare standardized payload before replacement**

```bash
diff -u benchmark/fast_retailing/reconciled/standardized.json /tmp/fr-hardening-1/standardized.json
```

Expected: no model-payload difference. If a difference appears, stop and explain it before copying anything because Step 9M.1.1 must not fix G1–G7 through input manipulation.

- [ ] **Step 4: Copy canonical audit artifacts**

After deterministic equality is proven:

```bash
cp /tmp/fr-hardening-1/provenance.json benchmark/fast_retailing/reconciled/provenance.json
cp /tmp/fr-hardening-1/conflicts.json benchmark/fast_retailing/reconciled/conflicts.json
```

Do not replace `standardized.json` if it is already identical.

- [ ] **Step 5: Re-run Fast Retailing audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Expected: source/reconciliation stages remain valid; the documented downstream accounting-engine G1–G7 queue remains open.

- [ ] **Step 6: Update benchmark docs and RESULT with measured evidence**

Record actual results:

```text
strict metadata/date parsing: yes
portable source-path validation: yes
all 5 bound source files retained in provenance: yes
supplemental provenance source-bound: yes
silent repeated-share overwrite removed: yes
statement overlap conflicts: 3
supplemental conflict count: <actual deterministic count>
Fast Retailing historical_shares: omitted unless complete/unambiguous
G1–G7 preserved for 9M.2: yes
DEMO_HK_Trainer unrelated drift removed: yes
```

Replace `<actual deterministic count>` with the measured value; never guess it.

- [ ] **Step 7: Run benchmark tests green**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 9: Full regression gate and stop before Step 9M.2

**Files:**
- Modify: `IMPLEMENTATION.md` status line only after all verification succeeds.
- Modify: `RESULT.md` with final measured evidence.

- [ ] **Step 1: Run focused filing pipeline tests**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_fast_retailing_benchmark.py -q
```

Expected: all pass.

- [ ] **Step 2: Run the full core suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass.

- [ ] **Step 3: Verify CLI surface**

```bash
PYTHONPATH=. python -m core --help
```

Require the existing commands:

```text
ingest
validate-source
reconcile
build
check
list
```

Require no `extract` command.

- [ ] **Step 4: Verify no feature drift**

Require:

```text
active family orders remain 1..90
synthetic demo/component surfaces unchanged
Fast Retailing standardized model payload unchanged
Fast Retailing historical_shares omitted unless source evidence proves a complete unambiguous axis
no forecasting/valuation/scenario activation
G1–G7 remain queued for Step 9M.2
```

- [ ] **Step 5: Verify working-tree scope before handoff**

Run:

```bash
git status --short
git diff --stat
```

Expected changes are limited to Step 9M.1.1 source/validation/reconciliation code, tests, regenerated Fast Retailing provenance/conflict artifacts/docs, `RESULT.md`, `IMPLEMENTATION.md`, and the intentional restoration of `example/DEMO_HK_Trainer.xlsx`.

No other example workbook, source PDF, `TARGET.md`, forecasting module, valuation module, or scenario module should change.

- [ ] **Step 6: Mark Step 9M.1.1 complete only with actual evidence**

At the top of this file add one concise status line containing:

```text
focused test count
full core test count
Fast Retailing statement overlap conflict count
Fast Retailing supplemental conflict count
5/5 source files retained/bound
standardized payload unchanged
DEMO_HK_Trainer restored
G1–G7 still open
```

Do not prestate counts before running the commands.

- [ ] **Step 7: Stop**

Do not begin Step 9M.2. Return the implementation/test summary to the user so they can inspect the diff and run `checkpoint`.
