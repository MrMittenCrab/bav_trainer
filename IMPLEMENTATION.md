**Status:** Step 9M.3A complete — G3 split lease aggregation; FR Stages 1–7 pass with lease_specs=18 / expected_specs=312. Stopped for user checkpoint.

# Step 9M.3A — Split Lease-Liability Aggregation Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `d4911261febcb88aa7d33503b1ef3d597367f98c` (`Step 9M.2D`). Implement only Step 9M.3A using red/green TDD. Do not begin G4 lease-interest reclassification, G5 NCI attribution, G6 share-basis/per-share work, G7 reconciliation-policy changes, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close G3 by making the existing lease-liability diagnostic work for companies that report lease liabilities as separate current and non-current balance-sheet lines, without inventing a source total or changing any accounting treatment.

**Architecture:** Keep `StandardizedFinancials` and filing/reconciliation artifacts unchanged. Add one lease-specific source resolver that prefers one explicit aggregate lease-liability line when it exists, otherwise accepts exactly one `lease_liability_current` plus one `lease_liability_noncurrent` line and treats their period-by-period sum as the analytical balance-sheet lease-liability total. Python expected values and workbook formulas must use the same resolved source rows. Duplicate/partial/unclear presentations remain fail-closed. Note 17's separately reported aggregate stays documentary evidence; this step does not promote note facts into the model or use the note total to overwrite the balance-sheet split.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, `LineItem`, lease-liability diagnostics, `ReferenceModelBuilder`, semantic component map, Trainer/Answer-Key/Check workflow, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` historical lease-analysis / no-invented-input requirements plus G3 in `benchmark/fast_retailing/GAPS.md`. This is a bounded extension of the existing Step 9L.1 lease-liability module; no new design document is required.

## Why this is the next step

Step 9M.2D leaves no execution blocker: Fast Retailing Stages 1–7 all pass, with 294 active historical components and no thrown exception. The remaining work is therefore substantive historical-product convergence rather than integration repair.

Among G3–G7, G3 is the narrowest next step with the clearest source contract:

```text
Fast Retailing FY2025 balance sheet
current lease liabilities      126,830
non-current lease liabilities  386,670
sum                            513,500

Note 17 reported aggregate      513,501
```

The one-unit difference is presentation rounding evidence, not a reason to insert a plug or rewrite either source. The lease diagnostic is a balance-sheet intensity/trend schedule, so its model-facing source should remain the balance sheet. For a valid split presentation, the analytical lease balance is therefore the sum of the two reported balance-sheet components. The note aggregate remains separate provenance and is not silently substituted.

The existing module intentionally omits split presentations because Step 9L.1 allowed only one uniquely resolvable aggregate line. The current Fast Retailing standardized payload already gives stronger semantic identities:

```text
lease_liability_current
lease_liability_noncurrent
```

This step teaches the module to consume that explicit split structure while preserving all existing ambiguity safeguards.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the Step 9M.1.1 filing-JSON schema, source binding, provenance, and conflict semantics.
- Preserve Step 9M.2A–9M.2D classification and rounding policies exactly.
- Do not edit Fast Retailing extracted/reconciled source numbers to make the lease module appear.
- Do not promote `note_facts` into `StandardizedFinancials` in this step.
- Do not replace the balance-sheet split sum with Note 17's aggregate.
- Do not add a balancing adjustment for the 513,500 vs 513,501 one-unit difference.
- One unique aggregate `lease_liability` source remains supported and is preferred when directly reported.
- A split source is valid only when exactly one current and exactly one non-current lease-liability component are explicitly identified.
- Partial split presentations do not imply zero for the missing side.
- Duplicate aggregate/current/non-current identities remain ambiguous and fail closed.
- Existing ambiguous duplicate generic `lease_liability` rows remain fail-closed; do not infer current/non-current solely from row order.
- Lease diagnostics remain raw historical balance-sheet diagnostics and do not change when the learner chooses operating vs financial classification.
- Preserve the existing two separate lease Accounting Judgment cases for Fast Retailing current/non-current rows.
- G4 remains open: do not reclassify lease interest or alter `compute_anchor()` net interest in this checkpoint.
- Preserve G5 NCI attribution behavior, G6 historical-share/per-share omission, and G7 conflict precedence.
- Preserve three primary-statement overlap conflicts and three supplemental conflicts.
- No company-specific `6288.HK`, Fast Retailing, or filename checks in production code.
- No forecasting/valuation activation.
- Cursor stops after implementation/tests and reports literal results; the user runs `checkpoint`.

---

### Task 1: Define one shared aggregate-or-split lease source resolver

**Files:**
- Modify: `core/model/lease_liability.py`
- Test: `core/tests/test_lease_liability.py`

**Interfaces:**

Add one source descriptor shared by Python calculation and workbook construction:

```python
@dataclass(frozen=True)
class LeaseLiabilitySource:
    mode: str  # "aggregate" | "split"
    items: tuple[LineItem, ...]
    indices: tuple[int, ...]


def resolve_lease_liability_source(
    financials: StandardizedFinancials,
) -> LeaseLiabilitySource | None:
    ...
```

Keep these existing public functions:

```python
lease_liability_availability(financials) -> LeaseLiabilityAvailability
lease_liability_applicable(financials) -> bool
compute_lease_liability_series(financials, periods, anchor) -> LeaseLiabilitySeries
```

`LeaseLiabilityAvailability` may keep its existing two fields; do not add workbook-specific state to it.

- [x] **Step 1: Preserve the existing aggregate-source contract**

Add/retain a focused test showing one direct aggregate source still resolves exactly as before:

```python
fin = _tiny(split=False)
source = resolve_lease_liability_source(fin)
assert source is not None
assert source.mode == "aggregate"
assert len(source.items) == 1
assert len(source.indices) == 1
assert lease_liability_applicable(fin)
```

The ordinary `Operating lease liabilities` demo path must remain model-equivalent.

- [x] **Step 2: Add a valid standardized split fixture**

Extend the test helper or add a small fixture whose two balance-sheet rows are explicitly:

```text
Current lease liabilities      concept=lease_liability_current
Non-current lease liabilities  concept=lease_liability_noncurrent
```

Use two periods with values:

```text
current:      40, 50
non-current:  60, 70
expected sum: 100, 120
```

Require:

```python
source = resolve_lease_liability_source(fin)
assert source is not None
assert source.mode == "split"
assert len(source.items) == 2
assert lease_liability_availability(fin).lease_liability is True
assert lease_liability_availability(fin).ambiguous is False
assert lease_liability_applicable(fin) is True
```

- [x] **Step 3: Add split fail-closed cases**

Require no usable lease source for each incomplete presentation:

```text
current only
non-current only
```

Require `ambiguous=True` and no applicable module for:

```text
two lease_liability_current rows + one non-current row
one current row + two lease_liability_noncurrent rows
multiple explicit aggregate lease_liability rows
```

Retain the existing Step 9L.1 regression in which two rows both use generic concept `lease_liability`: that remains ambiguous and omitted. Do not reinterpret duplicate generic concepts as a split pair.

- [x] **Step 4: Add aggregate-precedence regression**

Construct a fixture containing:

```text
one unique explicit aggregate lease_liability
one explicit lease_liability_current
one explicit lease_liability_noncurrent
```

Require the resolver to use the directly reported aggregate source only:

```python
assert source.mode == "aggregate"
assert len(source.items) == 1
```

Rationale: when the balance sheet already reports a unique aggregate, do not synthesize a second competing total.

- [x] **Step 5: Run the resolver tests red**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py \
  -k "aggregate_source or standardized_split or split_source or split_fail or aggregate_precedence" \
  -v
```

Expected before implementation: the standardized split pair remains unavailable/ambiguous because Step 9L.1 only resolves a single aggregate lease line.

- [x] **Step 6: Implement the minimal resolver**

Use concept identity before label fallback. The decision order must be:

```text
1. Count exact concept == lease_liability.
   - exactly 1 -> aggregate source
   - more than 1 -> ambiguous/fail closed

2. If no explicit aggregate, count exact:
   - lease_liability_current
   - lease_liability_noncurrent
   Exactly one of each -> split source.
   Duplicate either side -> ambiguous/fail closed.
   Only one side -> unavailable, not zero-filled.

3. If none of those explicit concepts exist, preserve the existing aggregate label-alias resolver path for legacy/manual inputs.
```

Do not add generic current/non-current word parsing to `line_resolver.py`. Split aggregation is a lease-module contract, not a new universal one-line resolver behavior.

Store the original balance-sheet indices in the descriptor so workbook formulas can use exactly the same sources as Python expected values.

- [x] **Step 7: Run Task 1 green**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py \
  -k "availability or aggregate_source or standardized_split or split_source or split_fail or aggregate_precedence" \
  -v
```

---

### Task 2: Compute lease diagnostics from one aggregate or the exact split sum

**Files:**
- Modify: `core/model/lease_liability.py`
- Test: `core/tests/test_lease_liability.py`

**Interfaces:**
- `compute_lease_liability_series()` consumes `resolve_lease_liability_source()`.
- `LeaseLiabilitySeries.lease_liability` remains one total series; do not change component-catalog IDs or public workbook semantics.

- [x] **Step 1: Add split-math regression**

For the valid split fixture from Task 1 require:

```python
periods = list(canonical_fiscal_periods(fin))
anchor = compute_anchor(fin, periods)
series = compute_lease_liability_series(fin, periods, anchor)
assert series.lease_liability == (100.0, 120.0)
assert series.lease_liability_change == (None, 20.0)
assert series.lease_liability_growth[0] is None
assert series.lease_liability_growth[1] == pytest.approx(0.20)
assert series.lease_liability_to_revenue[0] == pytest.approx(0.10)
```

- [x] **Step 2: Add period-completeness regression for each split side**

Delete the second period from only the current component, then only the non-current component. In both cases require `MissingHistoricalValueError` from `compute_lease_liability_series()`.

The missing side/period must never be treated as zero.

- [x] **Step 3: Run split math red**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py \
  -k "split_math or split_period or missing_period" \
  -v
```

- [x] **Step 4: Implement period-by-period source summation**

Use the resolver source:

```python
source = resolve_lease_liability_source(financials)
if source is None:
    raise MissingLineError("lease liability source not available")

lease_vals = tuple(
    sum(
        required_period_value(item, period, field="lease_liability")
        for item in source.items
    )
    for period in periods
)
```

Use the repository's existing line-resolution error class rather than inventing a second error hierarchy. Keep all existing ratio/change/growth logic unchanged.

- [x] **Step 5: Prove aggregate behavior is unchanged**

Run the existing ordinary, zero-denominator, sign-preservation, and canonical-demo tests together with the new split tests:

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py \
  -k "ordinary_two_period_math or zero_denominator or sign_preservation or canonical_demo or split_math or split_period" \
  -v
```

Expected: aggregate fixtures produce the same numbers as before; standardized split fixtures now produce the component sum.

---

### Task 3: Make workbook lease source-link formulas use the same resolved source rows

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_lease_liability.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- `ReferenceModelBuilder` must import and use `resolve_lease_liability_source()`.
- Do not change the lease component catalog or semantic component IDs.
- `lease_liability_source_link` remains the learner-facing total lease-liability source-link family.

- [x] **Step 1: Add split-builder applicability regression**

Build a workbook from the valid standardized split fixture and require lease components to exist:

```python
builder = ReferenceModelBuilder(fin)
assert builder.lease_liability_series is not None
assert builder.lease_liability_specs
```

For a two-period fixture, require all four existing lease families to be present in the semantic map; do not create current/non-current learner families in this step.

- [x] **Step 2: Add exact split source-link formula regression**

Open the Answer Key/semantic map and locate `lease_liability_source_link` for each modeled period. Require its formula to reference both exact Balance Sheet source rows and add them, for example semantically:

```text
='Balance Sheet'!B<current_row>+'Balance Sheet'!B<noncurrent_row>
```

Do not hard-code row numbers in the production implementation; derive them from `LeaseLiabilitySource.indices` using the existing Balance Sheet start-row convention / workbook-row helper.

For a direct aggregate source, retain the existing one-cell link formula.

- [x] **Step 3: Add split trusted-source tamper regression**

For a split-source Trainer:

1. fill one lease diagnostic practice formula correctly;
2. modify the current lease source cell and require Check to fail trusted-source validation;
3. rebuild, modify the non-current lease source cell and require the same failure.

Both balance-sheet components are trusted source cells. The aggregate diagnostic formula is derived from them; no hidden pasted total is allowed.

- [x] **Step 4: Run builder tests red**

```bash
PYTHONPATH=. pytest \
  core/tests/test_lease_liability.py \
  core/tests/test_reference_integrity.py \
  -k "split_builder or split_source_link or split_trusted or lease_liability" \
  -v
```

Expected before implementation: Python may resolve the split after Task 2, but workbook construction still assumes one `_resolved_source_row(..., "lease_liability")` and cannot emit the correct two-row formula.

- [x] **Step 5: Implement one formula path for one-or-many lease source rows**

Replace the single-row lease source lookup in the lease-context builder with the shared resolver.

Equivalent behavior:

```python
source = resolve_lease_liability_source(self.fin)
assert source is not None
source_rows = [SOURCE_START_ROW + idx for idx in source.indices]

if len(source_rows) == 1:
    lease_f = f"='Balance Sheet'!{src_col}{source_rows[0]}"
else:
    refs = [f"'Balance Sheet'!{src_col}{row}" for row in source_rows]
    lease_f = "=" + "+".join(refs)
```

Prefer the existing `workbook_row_for()` helper if it can be reused cleanly with the source descriptor; do not duplicate row-coordinate logic unnecessarily.

The Python series and Excel formula must be based on the same source descriptor so they cannot diverge.

- [x] **Step 6: Run Task 3 green**

```bash
PYTHONPATH=. pytest \
  core/tests/test_lease_liability.py \
  core/tests/test_reference_integrity.py \
  -k "split_builder or split_source_link or split_trusted or lease_liability" \
  -v
```

---

### Task 4: Prove the aggregation contract on Fast Retailing without changing source facts

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Modify: `core/tests/test_lease_liability.py`
- Read only: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/reconciled/provenance.json`
- Read only: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- Use the canonical Fast Retailing standardized payload already committed.
- Do not add a Fast Retailing-specific source resolver.

- [x] **Step 1: Assert the canonical split identities and FY2025 values**

Locate by `LineItem.concept`, not row order, and require:

```text
lease_liability_current     FY2025 = 126830
lease_liability_noncurrent  FY2025 = 386670
```

Then require:

```python
assert lease_liability_applicable(fin) is True
series = compute_lease_liability_series(fin, periods, compute_anchor(fin, periods))
assert series.lease_liability[-1] == pytest.approx(513500.0)
```

Do not alter standardized.json to make this pass.

- [x] **Step 2: Assert Note 17 remains separate evidence**

Read the committed Fast Retailing provenance artifact in the acceptance test and locate the FY2025 reported `lease_liability_total` note fact. Require its value to remain `513501` and require the standardized balance-sheet diagnostic total to remain `513500`.

The test must state the contract explicitly:

```text
balance-sheet diagnostic source = current + non-current BS components
note aggregate = independent documentary fact
one-unit difference is preserved, not plugged or silently substituted
```

Do not add provenance-reading behavior to production `ReferenceModelBuilder` in this step; this comparison is benchmark/audit evidence only.

- [x] **Step 3: Assert Fast Retailing workbook lease module activation**

Build `ReferenceModelBuilder(fin)` and require:

```python
assert builder.lease_liability_series is not None
assert len(builder.lease_liability_specs) == 18
```

Because Step 9M.2D has 294 active specs with lease specs omitted and the five-period lease catalog contributes 18 components, the expected post-G3 active total is 312 **if no unrelated family changes**. Add an assertion only if the implementation makes no other intended surface change:

```python
assert len(builder.expected_specs) == 312
```

If this arithmetic does not hold, stop and inspect the family inventory rather than updating the number blindly.

- [x] **Step 4: Preserve separate lease judgment cases**

Require Fast Retailing still produces two distinct lease classification judgment cases, one for the current row and one for the non-current row, with different identity selectors.

The raw diagnostic total must remain `513500` regardless of whether the learner later classifies either row as operating or financial; the diagnostic reports the obligation amount, not its reformulation category.

- [x] **Step 5: Run Fast Retailing acceptance tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_fast_retailing_benchmark.py \
  core/tests/test_lease_liability.py \
  -v
```

Expected after Tasks 1–3: the Fast Retailing lease module is now present, source evidence remains unchanged, and G4 behavior is still untouched.

---

### Task 5: Run the full workbook/Check acceptance gate and capture the new measured state

**Files:**
- Modify tests only if required to assert the intended G3 behavior.
- Read: `scripts/audit_fast_retailing_benchmark.py`
- Do not change G4–G7 production behavior.

**Interfaces:**
- Existing `run_audit()` remains the integration acceptance path.
- The Step 9M.2D audit already proves Stages 1–7 pass with 294 components and no lease module.

- [x] **Step 1: Update the Fast Retailing audit regression for G3 activation**

Require Stages 1–7 to continue passing. At Stage 4 require lease specs to be present. At blank/filled Check require totals to include the newly active lease components.

Do not hard-code counts before confirming the builder inventory from Task 4. If no unrelated surface changed, expected values are:

```text
expected_specs = 312
lease_specs = 18
blank Check:  correct=0 incorrect=0 blank=312 total=312
filled Check: correct=312 incorrect=0 blank=0 total=312
```

- [x] **Step 2: Run the staged audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Record literally:

```text
all stage statuses
expected_specs
lease_specs
blank Check counts
filled Check counts
first failing stage/exception, if any
```

- [x] **Step 3: Stop on any newly exposed execution defect**

If the newly active lease formulas expose a workbook/Check bug, fix it only if it is directly caused by the aggregate-or-split source contract in this checkpoint.

Do not use this checkpoint to begin G4 lease-interest accounting, G5 parent/NCI attribution, G6 share restatement, or G7 conflict-policy changes.

---

### Task 6: Update gap evidence and run final regression gates

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line only after final verification

**Interfaces:**
- Documentation reports literal measured results only.
- Source/reconciliation artifacts remain read-only.

- [x] **Step 1: Update G3 from measured evidence**

If all Task 4/5 acceptance criteria pass, mark G3 closed and document:

```text
unique aggregate source still supported
exact current + non-current standardized split supported
split analytical total = sum of BS components
Fast Retailing FY2025 diagnostic total = 513500
Note 17 aggregate remains 513501 independent provenance
no plug / no note substitution / no source mutation
```

Keep G4 explicitly open. State that this step changes only the historical liability diagnostic source contract; it does not condition interest expense/income on lease classification treatment.

- [x] **Step 2: Update BASELINE.md from the real audit**

Record the actual Stage 1–7 state, active component counts, and lease module applicability after the change. Do not copy expected counts from this plan unless the final command output confirms them.

- [x] **Step 3: Update RESULT.md with literal verification evidence**

Record:

```text
focused tests: actual pass count
full core tests: actual pass count
Fast Retailing lease source mode: split
FY2025 computed BS lease total: 513500
FY2025 reported Note 17 total: 513501
lease specs: actual count
full expected specs: actual count
blank/filled Check: actual counts
G3: closed or still open based on evidence
G4–G7: open
forecast/valuation isolation: pass/fail
```

- [x] **Step 4: Run the focused G3 suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_lease_liability.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Expected: all pass. Record the actual count.

- [x] **Step 5: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass. Record the actual count.

- [x] **Step 6: Verify source/reconciliation artifacts did not drift**

```bash
git diff -- \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/reconciled/standardized.json \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

Also verify the committed conflict counts remain:

```text
primary-statement overlap conflicts = 3
supplemental conflicts = 3
```

- [x] **Step 7: Verify no unrelated workbook fixture drift**

```bash
git diff -- \
  example/DEMO_HK_Trainer.xlsx \
  example/DEMO_HK_Answer_Key.xlsx \
  example/DEMO_HK_Standardized.json
```

Expected: no output. Do not regenerate committed demo workbooks merely because the real-company active component count increases.

- [x] **Step 8: Verify forecasting/valuation isolation**

Run the existing historical isolation regression used in prior checkpoints. Normal Step 9 builds must not call scenario/forecast/valuation paths.

- [x] **Step 9: Run the Fast Retailing audit as the final behavioral gate**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require deterministic agreement with Task 5. If stage/count behavior changes without code/data changes, stop and investigate rather than documenting either run.

- [x] **Step 10: Mark Step 9M.3A complete only with fresh evidence**

Only after Steps 4–9 succeed:

```text
add a compact status line at the top of IMPLEMENTATION.md
update RESULT.md / GAPS.md / BASELINE.md with literal results
```

- [x] **Step 11: Stop**

Do not implement G4 in this checkpoint. Return the implementation/test summary to the user so they can run `checkpoint`. ChatGPT should then review the checkpoint and decide whether G4 lease-interest consistency or G5 NCI attribution is the next highest-value historical step.
