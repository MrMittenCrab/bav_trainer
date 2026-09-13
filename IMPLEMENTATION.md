# Step 9M.1.1 — Filing-JSON Provenance + Validation Hardening

**Status: Step 9M.1.1 complete** — focused input suite 54 passed; full `core/tests/` 370 passed; portable source-path validation yes; supplemental provenance source-bound yes; silent repeated-share overwrite removed; statement overlap conflicts 3; supplemental conflicts 3; `standardized.json` unchanged; G1–G7 preserved for 9M.2; CLI `{ingest, validate-source, reconcile, build, check, list}` (no `extract`); family orders `1..90` unchanged.


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `e5fa7b87110a3a03c06349a35af6d662a880f88f` (`Step 9M.1`). Implement only Step 9M.1.1 using red/green TDD. Do not begin Step 9M.2 accounting fixes, OpenAI API extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close the review defects in the new filing-JSON boundary so every documentary fact remains source-bound after reconciliation, malformed source metadata cannot escape validation, and share facts cannot be silently overwritten across filings.

**Architecture:** Keep `ExtractedFiling` as the immutable documentary contract and `StandardizedFinancials` as the model-only contract. Harden the boundary in three places: (1) validate required metadata and relative source-file paths, (2) wrap reconciled supplemental facts with filing/year/hash provenance instead of dropping their origin, and (3) treat repeated share/note facts as cross-filing observations with explicit disagreement records rather than last-write-wins behavior. Do not change BAV accounting formulas or the Fast Retailing G1–G7 engine gap queue.

**Tech Stack:** Python stdlib (`dataclasses`, `json`, `hashlib`, `pathlib`, `datetime`), pytest, existing `ExtractedFiling`, filing validator/reconciler/standardizer, existing CLI, Fast Retailing benchmark fixtures.

**Spec:** `docs/superpowers/specs/2026-09-13-filing-json-input-design.md`

## Review findings that this step must close

1. `reconciliation_provenance_payload()` currently serializes `note_facts` / `share_facts` with page/note/label only. Their source filing, filing year, and computed SHA-256 are lost after `reconcile_filings()`, even though the architecture requires source-bound provenance for every extracted fact.
2. `_historical_shares()` currently iterates concatenated share facts into a dict keyed by period. Two filings can therefore report different diluted weighted-average share values for the same period and the later iteration silently overwrites the earlier value without a conflict record.
3. The v1 design requires non-empty required metadata and a portable relative `source_file`, but current parsing/validation allows blank company/currency/jurisdiction fields and allows an absolute or `..` source path to escape `source_root`.

## Global Constraints

- `TARGET.md` already records the stable source-data architecture; Cursor treats it as read-only.
- Preserve one JSON file per source filing.
- Preserve original documentary labels, sections, signs, units, page references, and values.
- `suggested_concept` remains advisory only.
- `StandardizedFinancials` remains model-only; do not add source/provenance fields to it.
- No PDF parsing or AI/API calls in this step.
- Do not infer unit conversions, stock-split multipliers, balancing plugs, missing facts, or accounting classifications.
- Cross-filing numeric disagreements must never be silently overwritten.
- Statement conflict behavior and the existing three Fast Retailing statement overlap conflicts must remain intact.
- Fast Retailing historical shares must remain omitted unless a complete, unambiguous reported diluted-WAS axis exists.
- Preserve Step 9M.0/9M.1 accounting gaps G1–G7 for Step 9M.2.
- Preserve CLI commands `{ingest, validate-source, reconcile, build, check, list}`; do not add `extract`.
- Preserve synthetic trainer family orders `1..90` and existing workbook surfaces.
- Cursor must stop after implementation/tests and let the user run `checkpoint`.

---

### Task 1: Enforce required filing metadata and portable source paths

**Files:**
- Modify: `core/ingestion/filing_json.py`
- Modify: `core/ingestion/filing_validator.py`
- Test: `core/tests/test_filing_json.py`
- Test: `core/tests/test_filing_cli.py`

**Interfaces:**
- `load_extracted_filing(path) -> ExtractedFiling` remains the loader.
- `validate_extracted_filing(filing, source_root=...) -> FilingValidationReport` remains the semantic/source-binding validator.
- Add no new public CLI command.

- [x] **Step 1: Add parser tests for required typed fields**

Require clean `ValueError` (not `KeyError` / raw `TypeError`) for missing or malformed:

```text
company object
company.name
ticker
jurisdiction
filing.fiscal_year
filing.period_end
filing.currency
filing.source_file
```

`stock_code` may remain empty because some future source projects may use ticker-only identity.

`fiscal_year` must be an integer value, not `bool`, and must be positive. Do not infer it from `period_end`.

- [x] **Step 2: Add validator tests for portable source-file paths**

Reject with hard validation issue code:

```text
invalid_source_path
```

for:

```text
/Users/name/report.pdf
../report.pdf
subdir/../../report.pdf
```

Allow a safe relative nested path such as:

```text
annual/FY2025.pdf
```

The resolved path must remain inside `source_root` after `.resolve()`.

- [x] **Step 3: Add CLI regression for invalid source path**

`python -m core validate-source ... --source-root ...` must exit nonzero and print `invalid_source_path` without reading the escaped file.

`reconcile` with the same invalid filing must exit nonzero before writing artifacts.

- [x] **Step 4: Run focused tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_cli.py -v
```

- [x] **Step 5: Implement strict required-field parsing**

Use small explicit helpers instead of direct casts that leak `KeyError`/`TypeError`, e.g.:

```python
def _required_nonempty_str(payload: dict, key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} is required")
    return value
```

For `fiscal_year`, require `isinstance(value, int) and not isinstance(value, bool) and value > 0`.

Preserve documentary strings; validation may test `.strip()` for emptiness but must not rewrite stored text.

- [x] **Step 6: Implement source-root containment validation**

Before reading bytes, reject absolute `source_file` paths. Resolve:

```python
root = Path(source_root).resolve()
candidate = (root / filing.filing.source_file).resolve()
```

Require `candidate` to be `root` itself or a descendant of `root`; because `source_file` names a file, normal valid inputs will be descendants. If containment fails, emit `invalid_source_path` and do not hash/read the escaped path.

Do not rely only on string-prefix checks.

- [x] **Step 7: Run focused tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_cli.py -v
```

---

### Task 2: Preserve source binding for every supplemental fact

**Files:**
- Modify: `core/ingestion/filing_reconciler.py`
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`

**Interfaces:**

Add a reconciled wrapper rather than changing the immutable extraction schema:

```python
@dataclass(frozen=True)
class SupplementalObservation:
    kind: str  # "note" | "share"
    filing_year: int
    source_file: str
    source_sha256: str
    fact: SupplementalFact
```

Change `ReconciledCompanyData.note_facts` and `.share_facts` to tuples of `SupplementalObservation`.

- [x] **Step 1: Write source-provenance regression**

Create FY2024 and FY2025 filings containing note/share facts. After reconciliation, require every supplemental observation to retain:

```text
filing_year
source_file
computed source SHA-256
fact source page/note/label
```

The SHA must come from `FilingValidationReport.computed_source_sha256`, never from a model-generated guess.

- [x] **Step 2: Write provenance-payload regression**

Require each item in `provenance.json` `note_facts` and `share_facts` to include:

```json
{
  "filing_year": 2025,
  "source_file": "FY2025.pdf",
  "source_sha256": "...",
  "fact_type": "...",
  "period": "...",
  "value": 123,
  "status": "reported",
  "source": {"page": 10}
}
```

Derived facts keep their `derivation` field and the same filing provenance.

- [x] **Step 3: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [x] **Step 4: Implement `SupplementalObservation` wrapping**

In `reconcile_filings()`, wrap note/share facts while the filing/report pair is still available. Do not concatenate naked `SupplementalFact` objects after source binding has been lost.

Sort supplemental observations deterministically by:

```text
kind, fact_type, period, filing_year, source_file, page
```

- [x] **Step 5: Update provenance serialization**

Replace `_fact_payload(fact)` with a serializer that consumes `SupplementalObservation` and emits both filing-level and fact-level provenance.

Do not promote note facts into statements.

- [x] **Step 6: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 3: Eliminate silent cross-filing overwrite of share facts

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

Add `supplemental_conflicts: tuple[SupplementalConflict, ...]` to `ReconciledCompanyData`.

- [x] **Step 1: Write equal repeated-share test**

FY2024 and FY2025 filings may both report the same FY2024 `diluted_weighted_average_shares`. Require:

```text
both observations retained in provenance
no supplemental conflict
one unambiguous FY2024 value available for share-axis gating
```

- [x] **Step 2: Write disagreeing repeated-share test**

If the two filings report different FY2024 diluted WAS values, require:

```text
both observations retained
one SupplementalConflict(kind="share", ...)
no silent selected share value
historical_shares is None
```

Do not choose the later filing because supplemental facts v1.0 do not carry `presentation_role`; conservatively require agreement until a future schema explicitly supports supplemental restatement precedence.

- [x] **Step 3: Write complete-axis share promotion test**

For a two-period model axis where every period has at least one `reported` diluted-WAS observation and all repeated observations agree, require `HistoricalShareData` to be emitted exactly once per period.

Derived share facts do not satisfy the reported-axis requirement.

- [x] **Step 4: Write generic note-fact disagreement test**

Two reported `lease_liability_total` facts for the same period with different values must produce a supplemental conflict and retain both source-bound observations. They remain audit evidence and are not promoted into `StandardizedFinancials`.

- [x] **Step 5: Run reconciler tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

- [x] **Step 6: Implement deterministic supplemental conflict grouping**

Group reported supplemental observations by:

```text
(kind, fact_type, period)
```

If the distinct numeric-value set has size > 1, create one `SupplementalConflict` with reason:

```text
cross_filing_supplemental_disagreement
```

Do not treat `derived` facts as authoritative observations for reported-value agreement.

- [x] **Step 7: Make historical-share gating conflict-aware**

For each model period:

1. collect only `kind="share"`, `status="reported"`, `fact_type="diluted_weighted_average_shares"`;
2. require at least one observation;
3. require exactly one distinct numeric value across observations;
4. use that value;
5. if any period is missing or disagreeing, return `None` for `historical_shares`.

Do not use iteration order to select a value.

- [x] **Step 8: Run reconciler tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py -v
```

---

### Task 4: Extend `conflicts.json` without changing statement-conflict semantics

**Files:**
- Modify: `core/ingestion/filing_standardizer.py`
- Test: `core/tests/test_filing_reconciler.py`
- Test: `core/tests/test_fast_retailing_benchmark.py`

**Interfaces:**

Keep existing statement fields and add:

```json
{
  "conflicts": [...],
  "overlap_conflict_count": 3,
  "supplemental_conflicts": [...],
  "supplemental_conflict_count": 0
}
```

`overlap_conflict_count` continues to mean primary-statement numeric overlap conflicts, preserving Step 9M.0/9M.1 semantics.

- [x] **Step 1: Write payload-shape test**

Require `reconciliation_conflicts_payload()` to serialize supplemental conflicts with all source-bound observations, including SHA/page/file/year, and a deterministic reason.

- [x] **Step 2: Preserve existing statement-count contract**

For the Fast Retailing benchmark, require:

```text
overlap_conflict_count == 3
```

Do not pre-state a Fast Retailing supplemental conflict count; compute and record what the source evidence actually produces.

- [x] **Step 3: Run tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -v
```

- [x] **Step 4: Implement deterministic supplemental-conflict serialization**

Sort by:

```text
kind, fact_type, period
```

Within each conflict, sort observations by filing year/source file/page. Do not discard agreeing duplicate observations from provenance.

- [x] **Step 5: Run tests green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 5: Regenerate and audit the Fast Retailing reconciled artifacts

**Files:**
- Modify generated artifacts only as required:
  - `benchmark/fast_retailing/reconciled/provenance.json`
  - `benchmark/fast_retailing/reconciled/conflicts.json`
- Modify: `benchmark/fast_retailing/PROVENANCE.md`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Test: `core/tests/test_fast_retailing_benchmark.py`

**Interfaces:**
- Generic pipeline remains the only reconciliation path.
- `standardized.json` should remain byte-identical unless a review fix legitimately changes only previously silent share promotion; Fast Retailing currently has no complete comparable diluted-share axis, so it should remain model-equivalent.

- [x] **Step 1: Add Fast Retailing provenance assertions**

For every reconciled `note_facts` and `share_facts` item require non-empty:

```text
source_file
source_sha256
filing_year
source.page
```

Continue to require the FY2025 primary-statement anchors and three statement overlap conflicts from Step 9M.1.

- [x] **Step 2: Run the generic pipeline twice**

```bash
rm -rf /tmp/fr-hardening-1 /tmp/fr-hardening-2
PYTHONPATH=. python -m core reconcile benchmark/fast_retailing/extracted --source-root benchmark/fast_retailing/source -o /tmp/fr-hardening-1
PYTHONPATH=. python -m core reconcile benchmark/fast_retailing/extracted --source-root benchmark/fast_retailing/source -o /tmp/fr-hardening-2
diff -ru /tmp/fr-hardening-1 /tmp/fr-hardening-2
```

Expected: no diff.

- [x] **Step 3: Copy only canonical generic artifacts back**

Copy `/tmp/fr-hardening-1/provenance.json` and `/tmp/fr-hardening-1/conflicts.json` into `benchmark/fast_retailing/reconciled/`.

Before replacing `standardized.json`, compare it against the committed file. Because this step must not fix G1–G7, investigate any model-payload difference before accepting it.

- [x] **Step 4: Re-run Fast Retailing audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

The first accounting-engine failures should remain the documented G1/G2 path rather than disappearing through input manipulation.

- [x] **Step 5: Update benchmark docs and RESULT**

Record:

```text
supplemental provenance source-bound: yes
portable source-path validation: yes
silent repeated-share overwrite removed: yes
statement overlap conflicts: 3
supplemental conflict count: <actual measured count>
G1–G7 accounting gaps preserved for 9M.2: yes
```

In the actual document, replace `<actual measured count>` with the number produced by the deterministic run; do not guess it beforehand.

- [x] **Step 6: Run benchmark tests green**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 6: Full regression gate and stop before Step 9M.2

**Files:**
- Modify: `IMPLEMENTATION.md` status line only after all verification succeeds.
- Modify: `RESULT.md` with final test evidence.

- [x] **Step 1: Run the focused input suite**

```bash
PYTHONPATH=. pytest core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_fast_retailing_benchmark.py -q
```

Expected: all pass.

- [x] **Step 2: Run the full core suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass.

- [x] **Step 3: Verify CLI surface**

```bash
PYTHONPATH=. python -m core --help
```

Require commands exactly include:

```text
ingest
validate-source
reconcile
build
check
list
```

and still no `extract` command.

- [x] **Step 4: Verify no accounting-feature drift**

Require:

```text
family orders remain 1..90
synthetic demo surfaces unchanged
Fast Retailing historical_shares remains omitted unless the source data now proves a complete unambiguous series
no forecasting/valuation activation
G1–G7 remain queued for Step 9M.2
```

- [x] **Step 5: Mark Step 9M.1.1 complete**

Only after the focused and full suites pass, add a concise status line to this file and update `RESULT.md` with actual counts/results.

Do not create or implement the Step 9M.2 plan. Stop and let the user run `checkpoint`, then ChatGPT reviews this hardening commit and prepares Step 9M.2.
