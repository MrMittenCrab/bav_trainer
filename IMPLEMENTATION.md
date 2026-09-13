# Step 9M.2B — Residual Balance-Sheet Guided Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `01f3eb8cb40886db326dad9815381e2856bd0c4a` (`Step 9M.2A`). Implement only Step 9M.2B using red/green TDD. Do not begin G3–G7 accounting-policy work, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Remove the next measured Fast Retailing Stage-4 blocker by routing only explicit current/non-current `other_*` balance-sheet concepts into the existing guided Accounting Judgment workflow, while keeping vague `Other assets` / `Other liabilities` labels fail-closed.

**Architecture:** Extend the existing concept-first classifier rather than adding company rules or broad label heuristics. Four exact residual-balance concepts receive an operating default appropriate to their side/horizon plus a financial alternative through the existing judgment registry. Then rerun the real-company audit and stop at the next genuinely different blocker instead of widening the classifier speculatively.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, `core/model/classification.py`, `core/model/judgment.py`, `ReferenceModelBuilder`, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` historical accounting-judgment requirements plus the measured post-9M.2A blocker in `benchmark/fast_retailing/GAPS.md`. This is a bounded continuation of the existing classification architecture; no new design document is required.

## Why this is the next step

Step 9M.2A is complete: the one-unit balance-sheet reconciliation policy passes, the explicit generic financial-instrument family is routed through Accounting Judgment, and the first remaining builder failure is the generic label `Other assets`.

The reconciled Fast Retailing payload already contains stronger semantic evidence than the label alone:

```text
Other assets       / other_current_assets
Other assets       / other_noncurrent_assets
Other liabilities  / other_current_liabilities
Other liabilities  / other_noncurrent_liabilities
```

These concepts identify side and horizon but not economic nature. Therefore the engine should not silently declare them financial or operating with certainty. The appropriate product behavior is the same guided-judgment pattern already used for leases, associates, and generic financial instruments.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the Step 9M.1.1 filing-JSON schema, source binding, provenance, and conflict semantics.
- Preserve all Fast Retailing source and reconciled values; do not edit `benchmark/fast_retailing/reconciled/standardized.json` to make the builder pass.
- Preserve Step 9M.2A balance-sheet tolerance exactly: absolute residual `<= 1.0` reporting unit is accepted; larger residuals fail.
- Preserve the existing G2 explicit financial-instrument rules and four G2 judgment codes unchanged.
- Keep bare labels `Other assets` and `Other liabilities` fail-closed when the concept does not explicitly identify side and current/non-current horizon.
- Do not classify from the word `other` alone.
- Do not classify a generic `other_assets` / `other_liabilities` concept that lacks current/non-current horizon.
- Do not add ticker, company-name, or Fast Retailing-specific branches in production code.
- Preserve more-specific rules for cash, debt/borrowings, leases, deferred tax, associates, financial instruments, equity, and all currently supported categories.
- New residual-balance decisions must be `ambiguous=True` and enter the existing Accounting Judgment mechanism.
- Preserve the three Fast Retailing primary-statement overlap conflicts and three supplemental conflicts.
- Preserve G3–G7 behavior. In particular, do not aggregate split lease liabilities, restate share counts, change NCI policy, or alter overlap precedence in this checkpoint.
- No new forecast/valuation activation.
- No new historical formula families solely because this classifier blocker is removed.
- Cursor stops after implementation/tests, reports the exact next measured blocker, and lets the user run `checkpoint`.

---

### Task 1: Specify the exact residual-balance classification contract

**Files:**
- Modify: `core/tests/test_classification.py`
- Modify: `core/model/classification.py`

**Interfaces:**
- Existing entry point remains:

```python
classify_balance_sheet_line(
    item: LineItem,
    *,
    override: str | None = None,
) -> ClassificationDecision
```

- Add no public classifier API.
- Add one private concept helper only if it keeps `_classify_by_concept()` readable.

- [ ] **Step 1: Add the four exact positive classification cases**

Add a parameterized test for these exact contracts:

```python
@pytest.mark.parametrize(
    ("label", "concept", "category", "judgment_code"),
    [
        (
            "Other assets",
            "other_current_assets",
            "Operating Working Capital Asset",
            "other_current_asset_operating_vs_financial",
        ),
        (
            "Other assets",
            "other_noncurrent_assets",
            "Operating Long-Term Asset",
            "other_noncurrent_asset_operating_vs_financial",
        ),
        (
            "Other liabilities",
            "other_current_liabilities",
            "Operating Working Capital Liability",
            "other_current_liability_operating_vs_financial",
        ),
        (
            "Other liabilities",
            "other_noncurrent_liabilities",
            "Operating Long-Term Liability",
            "other_noncurrent_liability_operating_vs_financial",
        ),
    ],
)
def test_explicit_other_balance_concepts_become_guided_judgments(
    label, concept, category, judgment_code
):
    item = _li(label, concept=concept)
    decision = classify_balance_sheet_line(item)
    assert decision.category == category
    assert decision.ambiguous is True
    assert decision.judgment_code == judgment_code
    assert decision.reason
```

Use the repository's existing `_li()` helper signature rather than creating a duplicate fixture if it already accepts `concept`.

- [ ] **Step 2: Add fail-closed regressions**

Require `UnclassifiedBalanceSheetLineError` for each of these unsupported inputs:

```text
label="Other assets",      concept=""
label="Other liabilities", concept=""
label="Other assets",      concept="other_assets"
label="Other liabilities", concept="other_liabilities"
label="Other assets",      concept="miscellaneous_current_asset"
label="Other liabilities", concept="miscellaneous_noncurrent_liability"
```

Also require that an intentionally mismatched generic label does not activate the residual helper merely from the concept token:

```text
label="Cash and cash equivalents", concept="other_current_assets"
```

The existing specific cash rule must remain authoritative or the mismatch must fail closed; it must not become an `other_current_assets` judgment case.

- [ ] **Step 3: Run the focused classifier tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "other_balance or explicit_other" -v
```

Expected before implementation: the four positive cases raise `UnclassifiedBalanceSheetLineError`; all existing specificity/fail-closed behavior remains unchanged.

- [ ] **Step 4: Implement a narrow exact-concept helper**

Add a private helper called from `_classify_by_concept()` after the existing more-specific concept rules and after `_generic_financial_concept_decision()` has had the opportunity to recognize explicitly financial rows.

The helper contract should be equivalent to:

```python
def _generic_other_balance_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    mapping = {
        "othercurrentassets": (
            "asset",
            "Operating Working Capital Asset",
            "other_current_asset_operating_vs_financial",
        ),
        "othernoncurrentassets": (
            "asset",
            "Operating Long-Term Asset",
            "other_noncurrent_asset_operating_vs_financial",
        ),
        "othercurrentliabilities": (
            "liability",
            "Operating Working Capital Liability",
            "other_current_liability_operating_vs_financial",
        ),
        "othernoncurrentliabilities": (
            "liability",
            "Operating Long-Term Liability",
            "other_noncurrent_liability_operating_vs_financial",
        ),
    }
    spec = mapping.get(c)
    if spec is None:
        return None

    side, category, judgment_code = spec
    if side == "asset" and "other asset" not in low:
        return None
    if side == "liability" and "other liabil" not in low:
        return None

    return ClassificationDecision(
        category,
        ambiguous=True,
        reason=(
            "Explicit residual balance-sheet concept identifies side/horizon but "
            "not economic nature — operating vs financial judgment"
        ),
        judgment_code=judgment_code,
    )
```

Exact implementation may reuse existing private utilities, but keep these semantics:

```text
exact standardized concept required
side/horizon required
matching generic residual label required
operating default
financial alternative supplied later by judgment registry
no company-specific logic
```

Do not change `_generic_financial_concept_decision()` to recognize these rows: `other_current_assets` is not evidence that the item itself is a financial instrument.

- [ ] **Step 5: Run Task 1 green plus existing G2 classifier regressions**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "other_balance or explicit_other or generic_financial" -v
```

Expected: all selected tests pass.

---

### Task 2: Register the four guided Accounting Judgment templates

**Files:**
- Modify: `core/model/judgment.py`
- Modify: `core/tests/test_classification.py`
- Modify: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Keep `ClassificationJudgmentTemplate`, `JudgmentCase`, `CLASSIFICATION_JUDGMENT_TEMPLATES`, and `classification_judgment_cases()` unchanged.
- Add only four registry entries keyed by the four judgment codes from Task 1.

- [ ] **Step 1: Add the four exact registry contracts**

Add these option pairs, with the classifier default first:

```python
"other_current_asset_operating_vs_financial": (
    "Operating Working Capital Asset",
    "Financial Asset",
)
"other_noncurrent_asset_operating_vs_financial": (
    "Operating Long-Term Asset",
    "Financial Asset",
)
"other_current_liability_operating_vs_financial": (
    "Operating Working Capital Liability",
    "Financial Liability",
)
"other_noncurrent_liability_operating_vs_financial": (
    "Operating Long-Term Liability",
    "Financial Liability",
)
```

Rationale text must state that the source concept proves balance-sheet side and horizon but not whether the residual balance is operating or financing in economic substance.

Consequence text must use the existing BAV mechanics:

```text
current operating asset -> raises NOWC/NOA; financial asset -> lowers Net Debt
non-current operating asset -> raises NOLA/NOA; financial asset -> lowers Net Debt
current operating liability -> lowers NOWC/NOA; financial liability -> raises Net Debt
non-current operating liability -> lowers NOLA/NOA; financial liability -> raises Net Debt
```

For all four switches, state that implied equity is unchanged from classification alone.

- [ ] **Step 2: Add judgment-case generation tests**

Create a minimal balanced two-period `StandardizedFinancials` containing one non-zero row for each of the four concepts plus enough ordinary detail/equity to make reformulation valid. Require:

```python
cases = classification_judgment_cases(fin, periods, reformulation)
assert {case.label for case in cases} >= {
    "Other current assets",
    "Other non-current assets",
    "Other current liabilities",
    "Other non-current liabilities",
}
```

For each case require:

```text
supplied_treatment == classifier default
exactly one alternative
alternative == financial category for that side
non-empty model_rationale
non-empty consequence_prompt
non-empty model_consequence
override_selector starts with "identity:"
```

- [ ] **Step 3: Add consequence-direction assertions**

For each of the four judgment cases, apply the alternative using the existing classification override path and verify:

```text
implied_equity unchanged
current asset:       alternative lowers NOA and lowers Net Debt
non-current asset:   alternative lowers NOA and lowers Net Debt
current liability:   alternative raises NOA and raises Net Debt
non-current liability: alternative raises NOA and raises Net Debt
```

Use the repository's existing reformulation helpers rather than reimplementing BAV arithmetic in the test.

- [ ] **Step 4: Add a builder-level integration regression**

In `core/tests/test_reference_integrity.py`, build a minimal model containing the four exact concepts and require the resulting `builder.judgment_cases` to contain all four codes/treatments through the existing Accounting Judgment workflow. Do not create a second judgment surface or workbook mechanism.

- [ ] **Step 5: Run Task 2 tests red if templates are not yet registered, then green after the minimal registry change**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  -k "other_balance or other_current_asset or other_noncurrent_asset or other_current_liability or other_noncurrent_liability" \
  -v
```

Expected after implementation: all selected tests pass.

---

### Task 3: Prove the Fast Retailing blocker is removed without changing source data

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Read only during implementation: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only during implementation: `benchmark/fast_retailing/reconciled/provenance.json`
- Read only during implementation: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- Existing `run_audit()` remains the behavioral acceptance path.
- Do not add a Fast Retailing-specific classification API.

- [ ] **Step 1: Add exact Fast Retailing row assertions**

Load `reconciled/standardized.json` and locate rows by concept, not by position. Require these four concepts to exist and classify as follows:

```text
other_current_assets          -> Operating Working Capital Asset, ambiguous, other_current_asset_operating_vs_financial
other_noncurrent_assets       -> Operating Long-Term Asset, ambiguous, other_noncurrent_asset_operating_vs_financial
other_current_liabilities     -> Operating Working Capital Liability, ambiguous, other_current_liability_operating_vs_financial
other_noncurrent_liabilities  -> Operating Long-Term Liability, ambiguous, other_noncurrent_liability_operating_vs_financial
```

This test proves the production rule is generic concept-driven logic applied to a real company.

- [ ] **Step 2: Add an audit-stage regression**

Call `run_audit()` and require:

```python
stages = {stage.name: stage for stage in run_audit().stages}
assert stages["3_reconciliation"].status == "pass"
```

For Stage 4:

- if it passes, accept that and allow later stages to reveal the next blocker;
- if it fails with `UnclassifiedBalanceSheetLineError`, require the message not to name `Other assets` or `Other liabilities`;
- do not assert that the entire workbook already succeeds.

- [ ] **Step 3: Run Fast Retailing acceptance tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

Expected: the four residual rows are no longer the Stage-4 hard stop. Any newly exposed unrelated blocker is evidence for the next checkpoint, not permission to broaden Step 9M.2B.

- [ ] **Step 4: Run the real audit and capture the next exact blocker**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Record exactly:

```text
first failing stage
exception class
exception message
whether workbook generation was reached
whether blank/filled Check was reached
```

Do not fix the newly exposed blocker in this checkpoint unless it is one of the four exact concepts defined in Task 1 and the failure is demonstrably an implementation defect in this plan.

---

### Task 4: Update measured gap documentation only after the audit

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/BASELINE.md` only if the audit stage table changes
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line only after final verification

**Interfaces:**
- Documentation must report observed behavior, not forecast the next blocker.

- [ ] **Step 1: Add a Step 9M.2B resolution entry to `GAPS.md`**

Document the residual-balance rule separately from G2 financial instruments:

```text
exact current/non-current other-asset/liability concepts -> guided operating-vs-financial judgment
bare Other assets / Other liabilities labels -> still fail closed
no company-specific production rule
```

Keep G3–G7 descriptions unchanged except where the final audit proves a stage is now reachable; do not mark an accounting-policy gap closed merely because the builder progresses farther.

- [ ] **Step 2: Replace the “Post-9M.2A first remaining blocker” section with measured Step 9M.2B evidence**

Use the exact stage/exception/message from Task 3 Step 4. If Stage 4 passes, report the first later failing stage instead. If all stages pass, state that explicitly and record the reached workbook/Check stages.

- [ ] **Step 3: Update `RESULT.md` with actual verification evidence**

Record:

```text
Step 9M.2B status
focused test pass count
full core test pass count
Stage 3 status
Stage 4 status / exact next blocker
residual-balance judgment cases present
statement overlap conflicts
supplemental conflicts
standardized/provenance/conflict source artifacts unchanged
forecast/valuation isolation status
```

Use literal results from the final commands; do not estimate test counts.

---

### Task 5: Full regression, drift gate, and stop

**Files:**
- Test only except final status/doc updates listed in Task 4.
- Do not modify source/extracted/reconciled benchmark JSON in response to a model failure.

- [ ] **Step 1: Run the focused Step 9M.2B suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Expected: all pass. Record the actual pass count.

- [ ] **Step 2: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass. Record the actual pass count.

- [ ] **Step 3: Verify source/reconciliation artifacts did not drift**

```bash
git diff -- \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/source \
  benchmark/fast_retailing/reconciled/standardized.json \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

Then verify committed conflict counts without regenerating source artifacts:

```bash
python - <<'PY'
import json
from pathlib import Path
p = Path("benchmark/fast_retailing/reconciled/conflicts.json")
data = json.loads(p.read_text())
print("overlap", data["overlap_conflict_count"])
print("supplemental", data["supplemental_conflict_count"])
PY
```

Expected from the accepted Step 9M.2A base:

```text
overlap 3
supplemental 3
```

- [ ] **Step 4: Verify unrelated workbook surfaces did not drift**

```bash
git diff -- \
  example/DEMO_HK_Trainer.xlsx \
  example/DEMO_HK_Answer_Key.xlsx
```

Expected: no output.

Run the existing synthetic surface/family-order regressions already covered by the full suite. Do not update fixture workbooks in this step.

- [ ] **Step 5: Verify forecast/valuation isolation**

Use the repository's existing isolation tests/searches from Step 9M.2A. Normal Step 9 execution must not activate forecasting, scenario, or valuation code. Active historical family orders remain `1..90` unless an existing judgment-case row changes dynamically through the already-supported mechanism; do not add a new formula family here.

- [ ] **Step 6: Run the Fast Retailing audit as the final behavioral gate**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require the same measured next blocker as Task 3 Step 4. If the blocker changes between runs without code/data changes, stop and investigate nondeterminism instead of documenting either result.

- [ ] **Step 7: Mark Step 9M.2B complete only with evidence**

At the top of `IMPLEMENTATION.md`, add a compact status line containing the actual focused/full test counts and final Fast Retailing audit state. Update `RESULT.md` with the same evidence.

- [ ] **Step 8: Stop**

Do not implement the next blocker. Return the implementation/test summary to the user so they can run `checkpoint`. ChatGPT should review that checkpoint and decide whether the next step is another narrow classification family or one of the substantive accounting gaps G3–G7.
