**Status:** Step 9M.2C complete — seven deterministic tax/provision/equity concepts; Stage 4 now fails on ReformulationIntegrityError (classified detail vs totals). Stopped for user checkpoint.

# Step 9M.2C — Deterministic Balance-Sheet Concept Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `894c525cd81689c27b08cc0f05e1a3eb5d5efa20` (`Step 9M.2B`). Implement only Step 9M.2C using red/green TDD. Do not begin G3–G7 accounting-policy work, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Finish the remaining structurally deterministic Fast Retailing balance-sheet classifications so Stage 4 is no longer blocked by ordinary standardized concepts, while preserving fail-closed behavior for genuinely ambiguous or unknown rows and leaving G3–G7 substantive accounting work untouched.

**Architecture:** Extend the existing concept-first classifier with one narrow exact-concept mapping for standard tax/provision/equity presentation rows already present in the reconciled Fast Retailing payload. These rows receive deterministic BAV categories and no new Accounting Judgment cases because their balance-sheet nature is already encoded by the standardized concept. Add one real-company inventory test that requires every Fast Retailing non-subtotal balance-sheet row to be classifiable, then rerun the staged audit and stop at the first genuinely new blocker or substantive gap.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, `core/model/classification.py`, `ReferenceModelBuilder`, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` historical reformulation/accounting-judgment requirements plus the measured post-9M.2B blocker in `benchmark/fast_retailing/GAPS.md`. This is a bounded continuation of the existing classification architecture; no new design document is required.

## Why this is the next step

Step 9M.2B is complete. The committed audit reports:

```text
Stage 3: pass
Stage 4: fail
UnclassifiedBalanceSheetLineError: Current tax liabilities
```

A review of the committed Fast Retailing standardized balance sheet shows that the remaining ordinary rows that the current classifier cannot classify from either exact concept or existing label rules are a small, explicit set:

```text
current_tax_liabilities
provisions_current
provisions_noncurrent
capital_stock
capital_surplus
other_components_of_equity
noncontrolling_interests
```

These are not another “other” family and should not be turned into broad label heuristics. Their standardized concepts already encode enough accounting identity to assign a structural BAV category:

```text
current tax liabilities      -> Operating Working Capital Liability
current provisions           -> Operating Working Capital Liability
non-current provisions       -> Operating Long-Term Liability
capital stock                -> Equity
capital surplus              -> Equity
other components of equity   -> Equity
non-controlling interests    -> Equity
```

Classifying `noncontrolling_interests` as Equity is only a balance-sheet classification decision. It does **not** solve G5 parent-vs-NCI attribution, parent ROE, per-share attribution, or income-statement ownership logic; those remain separate substantive work.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the Step 9M.1.1 filing-JSON schema, source binding, provenance, and conflict semantics.
- Preserve all Fast Retailing source and reconciled values; do not edit `benchmark/fast_retailing/reconciled/standardized.json` to make the builder pass.
- Preserve Step 9M.2A balance-sheet tolerance exactly: absolute residual `<= 1.0` reporting unit is accepted; larger residuals fail.
- Preserve all Step 9M.2A G2 financial-instrument judgments and Step 9M.2B residual `other_*` judgments unchanged.
- Add no broad rule based only on words such as `tax`, `provision`, `capital`, `equity`, or `interest`.
- New recognition in this checkpoint must require one of the exact standardized concepts listed in this plan plus a compatible label-family guard.
- The seven concepts in this step are deterministic classifications: `ambiguous=False`, `judgment_code=None`, and no new Accounting Judgment template.
- Do not create company/ticker/Fast Retailing branches in production code.
- Do not change lease classification or aggregation behavior (G3/G4).
- Do not change parent/NCI attribution logic (G5); NCI may classify as Equity only for consolidated balance-sheet reformulation.
- Do not restate or synthesize share history (G6).
- Do not alter reconciliation/restatement precedence or the three statement + three supplemental conflicts (G7/input boundary).
- Do not add forecast/valuation/scenario activation.
- Do not add a new historical formula family merely because Stage 4 progresses farther.
- Cursor stops after the final audit, reports the exact next blocker/stage, and lets the user run `checkpoint`.

---

### Task 1: Lock the exact deterministic concept contract with red tests

**Files:**
- Modify: `core/tests/test_classification.py`
- Modify later in this task: `core/model/classification.py`

**Interfaces:**
- Existing public entry point remains:

```python
classify_balance_sheet_line(
    item: LineItem,
    *,
    override: str | None = None,
) -> ClassificationDecision
```

- Add no public classifier API.
- Prefer one small private helper called from `_classify_by_concept()` if it keeps the existing function readable.

- [x] **Step 1: Add the seven exact positive classification cases**

Add a parameterized test equivalent to:

```python
@pytest.mark.parametrize(
    ("label", "concept", "expected_category"),
    [
        (
            "Current tax liabilities",
            "current_tax_liabilities",
            "Operating Working Capital Liability",
        ),
        (
            "Provisions",
            "provisions_current",
            "Operating Working Capital Liability",
        ),
        (
            "Provisions",
            "provisions_noncurrent",
            "Operating Long-Term Liability",
        ),
        (
            "Capital stock",
            "capital_stock",
            "Equity",
        ),
        (
            "Capital surplus",
            "capital_surplus",
            "Equity",
        ),
        (
            "Other components of equity",
            "other_components_of_equity",
            "Equity",
        ),
        (
            "Non-controlling interests",
            "noncontrolling_interests",
            "Equity",
        ),
    ],
)
def test_exact_standard_accounting_concepts_classify_deterministically(
    label, concept, expected_category
):
    decision = classify_balance_sheet_line(_li(label, concept=concept))
    assert decision.category == expected_category
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.reason
```

Use the existing `_li()` helper rather than adding a duplicate `LineItem` fixture.

- [x] **Step 2: Add concept/label mismatch fail-closed tests**

Require the new helper not to activate when the concept and documentary label family contradict each other. Use neutral labels that are not independently handled by another existing rule:

```python
@pytest.mark.parametrize(
    ("label", "concept"),
    [
        ("Miscellaneous balance", "current_tax_liabilities"),
        ("Miscellaneous balance", "provisions_current"),
        ("Miscellaneous balance", "provisions_noncurrent"),
        ("Miscellaneous balance", "capital_stock"),
        ("Miscellaneous balance", "capital_surplus"),
        ("Miscellaneous balance", "other_components_of_equity"),
        ("Miscellaneous balance", "noncontrolling_interests"),
    ],
)
def test_exact_standard_accounting_concepts_require_compatible_labels(label, concept):
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(_li(label, concept=concept))
```

Also keep existing rules authoritative. Add at least these regressions:

```text
Cash and cash equivalents / cash -> Financial Asset
Trade and other payables / trade_and_other_payables -> Operating Working Capital Liability
Deferred tax liabilities / deferred_tax_liabilities -> existing deferred-tax treatment
Lease liabilities / lease_liability_current -> existing lease judgment
```

- [x] **Step 3: Run the focused tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py \
  -k "standard_accounting_concepts or current_tax_liabilities or provisions or capital_surplus or noncontrolling" \
  -v
```

Expected before implementation: the seven new positive cases are unsupported by the Step 9M.2B classifier; the existing specificity regressions remain green.

- [x] **Step 4: Implement one exact-concept helper**

Add a private helper with an explicit mapping. Equivalent contract:

```python
def _deterministic_accounting_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    mapping = {
        "currenttaxliabilities": (
            "Operating Working Capital Liability",
            lambda text: "tax" in text and "liab" in text,
        ),
        "provisionscurrent": (
            "Operating Working Capital Liability",
            lambda text: "provision" in text,
        ),
        "provisionsnoncurrent": (
            "Operating Long-Term Liability",
            lambda text: "provision" in text,
        ),
        "capitalstock": (
            "Equity",
            lambda text: "capital stock" in text,
        ),
        "capitalsurplus": (
            "Equity",
            lambda text: "capital surplus" in text,
        ),
        "othercomponentsofequity": (
            "Equity",
            lambda text: "component" in text and "equity" in text,
        ),
        "noncontrollinginterests": (
            "Equity",
            lambda text: (
                ("non-controlling" in text or "noncontrolling" in text)
                and "interest" in text
            ),
        ),
    }

    spec = mapping.get(c)
    if spec is None:
        return None
    category, label_ok = spec
    if not label_ok(low):
        return None
    return ClassificationDecision(
        category,
        ambiguous=False,
        reason="Exact standardized accounting concept",
    )
```

The exact implementation may avoid lambdas if a clearer structure is preferable, but preserve these semantics exactly:

```text
exact concept required
compatible label family required
deterministic category
ambiguous=False
judgment_code=None
no company-specific checks
```

Call this helper from `_classify_by_concept()` **after** more-specific existing concept policies (deferred tax, lease, associate, cash/debt/equity specifics) and before falling through to label heuristics. Do not weaken the existing G2/G2B helpers.

- [x] **Step 5: Run Task 1 green plus prior classifier regressions**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py \
  -k "standard_accounting_concepts or current_tax_liabilities or provisions or capital_surplus or noncontrolling or generic_financial or other_balance" \
  -v
```

Expected: all selected tests pass.

---

### Task 2: Prove the complete Fast Retailing balance-sheet classification inventory

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Read only: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/reconciled/provenance.json`
- Read only: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- Use existing `standardized_from_payload()` and `classify_balance_sheet_line()`.
- Use existing `is_balance_sheet_subtotal()` to exclude subtotal/total rows.
- Do not add Fast Retailing-specific production behavior.

- [x] **Step 1: Add one real-company inventory acceptance test**

Add a test that classifies every non-subtotal Fast Retailing balance-sheet row and reports all unsupported rows together rather than stopping on the first:

```python
def test_fast_retailing_all_balance_sheet_detail_rows_are_classifiable():
    fin = standardized_from_payload(
        json.loads(STANDARDIZED.read_text(encoding="utf-8"))
    )
    unsupported = []
    for item in fin.balance_sheet:
        if is_balance_sheet_subtotal(item):
            continue
        try:
            classify_balance_sheet_line(item)
        except UnclassifiedBalanceSheetLineError as exc:
            unsupported.append((item.label, item.concept, str(exc)))
    assert unsupported == []
```

Import the existing classifier exception and subtotal helper rather than duplicating their logic.

Before production implementation, this test should expose the current committed residual set. Based on the Step 9M.2B code + committed standardized payload, the expected unsupported concepts are:

```text
current_tax_liabilities
provisions_current
provisions_noncurrent
capital_stock
capital_surplus
other_components_of_equity
noncontrolling_interests
```

If the red test shows an additional concept not in that list, stop before widening production rules and report the discrepancy to the user. Do not silently add another mapping.

- [x] **Step 2: Add exact Fast Retailing category assertions for the seven rows**

Locate by `item.concept`, not row position, and require:

```text
current_tax_liabilities    -> Operating Working Capital Liability
provisions_current         -> Operating Working Capital Liability
provisions_noncurrent      -> Operating Long-Term Liability
capital_stock              -> Equity
capital_surplus            -> Equity
other_components_of_equity -> Equity
noncontrolling_interests   -> Equity
```

For each require:

```text
ambiguous == False
judgment_code is None
```

- [x] **Step 3: Add NCI boundary regression**

The test should make explicit that NCI balance-sheet classification does not close G5. Require only the structural classification:

```python
decision = classify_balance_sheet_line(nci_item)
assert decision.category == "Equity"
```

Do **not** add or alter assertions for parent-attributable ROE, parent earnings, per-share attribution, or NCI profit allocation in this task.

- [x] **Step 4: Run Fast Retailing acceptance tests green**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

Expected after Task 1 implementation: the full balance-sheet detail inventory is classifiable; existing source/provenance/conflict checks still pass.

---

### Task 3: Re-run Stage 4 and capture the next real blocker without widening scope

**Files:**
- Modify tests only if required for the acceptance assertion: `core/tests/test_fast_retailing_benchmark.py`
- Read/execute: `scripts/audit_fast_retailing_benchmark.py`
- Do not modify source or reconciled benchmark JSON.

**Interfaces:**
- Existing `run_audit()` remains the behavioral acceptance path.
- `ReferenceModelBuilder` remains the real integration gate.

- [x] **Step 1: Add/update the audit-stage regression**

Require:

```python
stages = {stage.name: stage for stage in run_audit().stages}
assert stages["3_reconciliation"].status == "pass"
```

For Stage 4:

```text
- it must no longer fail on Current tax liabilities;
- it must no longer fail on any of the seven concepts closed in this step;
- if it fails on a different row or exception, accept that as the next measured blocker;
- if Stage 4 passes, allow Stage 5+ to reveal the next blocker.
```

Do not assert complete workbook success in advance.

- [x] **Step 2: Run the staged audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Record exactly:

```text
first failing stage
exception class
exception message
whether ReferenceModelBuilder completed
whether workbook generation was reached
whether blank Check was reached
whether filled Check was reached
```

- [x] **Step 3: Stop on the first new blocker**

Do not fix the newly exposed issue in Step 9M.2C unless the audit shows that one of the seven exact mappings above was implemented incorrectly. In particular, do not use this checkpoint to begin:

```text
G3 split-lease aggregation
G4 lease-interest treatment conditioning
G5 parent/NCI attribution
G6 split-adjusted share history
G7 reconciliation/restatement changes
```

The purpose of this task is to finish deterministic Stage-4 classification convergence and measure what comes next.

---

### Task 4: Preserve model semantics and source artifacts

**Files:**
- Test: `core/tests/test_classification.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_fast_retailing_benchmark.py`
- Read only: benchmark source/extracted/reconciled artifacts

- [x] **Step 1: Prove no new Accounting Judgment cases are created by the seven deterministic rows**

Add a minimal integration assertion using the existing builder/judgment machinery. For a fixture containing the seven new exact concepts, require that none of their identities appears as a new `JudgmentCase` solely because of Step 9M.2C:

```text
current tax liability: no new judgment case
provisions current/non-current: no new judgment case
capital stock/surplus/components: no new judgment case
NCI: no new judgment case in this step
```

Existing lease, G2 financial-instrument, and G2B residual-other judgment cases must remain unchanged.

- [x] **Step 2: Prove source/reconciliation artifacts are unchanged**

Run:

```bash
git diff -- \
  benchmark/fast_retailing/source \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/reconciled/standardized.json \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

Also retain the existing benchmark assertions:

```text
primary-statement overlap conflicts == 3
supplemental conflicts == 3
```

- [x] **Step 3: Prove workbook fixtures did not drift**

```bash
git diff -- \
  example/DEMO_HK_Trainer.xlsx \
  example/DEMO_HK_Answer_Key.xlsx
```

Expected: no output.

Do not regenerate example workbooks in this step.

---

### Task 5: Update measured gap documentation only after the audit

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/BASELINE.md` only if its stage table is regenerated by the existing audit workflow
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line only after final verification

- [x] **Step 1: Add a Step 9M.2C classifier-resolution entry to `GAPS.md`**

Record a new classifier subsection (for example `G2C`) stating exactly:

```text
exact standardized concepts covered:
- current_tax_liabilities
- provisions_current
- provisions_noncurrent
- capital_stock
- capital_surplus
- other_components_of_equity
- noncontrolling_interests

classification is concept-driven, not company-driven
no broad label fallback added
no new judgment templates added
G5 remains open despite NCI -> Equity structural classification
```

Do not rename or mark G3–G7 closed unless the audit independently proves their underlying product problem no longer exists.

- [x] **Step 2: Replace the post-9M.2B blocker section with literal Step 9M.2C audit evidence**

Use the exact Stage/exception/message from Task 3. If all stages pass, state that explicitly and list the workbook/Check stages reached. Do not speculate about the next implementation.

- [x] **Step 3: Update `RESULT.md` from literal command output**

Record:

```text
Step 9M.2C status
focused test pass count
full core test pass count
Fast Retailing Stage 3 status
Fast Retailing Stage 4 status
first next blocker, if any
all Fast Retailing BS detail rows classifiable: yes/no
new Step 9M.2C judgment cases: 0
statement conflicts: 3
supplemental conflicts: 3
standardized/source artifact drift: no
forecast/valuation isolation: pass/fail
```

Do not pre-fill test counts before running them.

---

### Task 6: Full regression gate and stop

**Files:**
- Modify only final status/docs listed in Task 5 after all checks pass.

- [x] **Step 1: Run the focused Step 9M.2C suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Expected: all pass. Record the literal pass count.

- [x] **Step 2: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass. Record the literal pass count.

- [x] **Step 3: Verify forecast/valuation isolation**

Run the existing isolation regression used in Step 9M.2A/9M.2B. Normal historical execution must not call scenario, forecast, DCF, residual-income, or valuation paths. Active historical family orders remain `1..90`; this checkpoint adds no formula family.

- [x] **Step 4: Re-run the source/workbook no-drift commands from Task 4**

Expected: no output for source/reconciled/example-workbook paths.

- [x] **Step 5: Run the Fast Retailing audit as the final behavioral gate**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require the same stage/result measured in Task 3. If the first blocker changes without code/data changes, stop and investigate nondeterminism rather than documenting either run.

- [x] **Step 6: Mark Step 9M.2C complete only with fresh evidence**

Only after Steps 1–5 succeed:

```text
- add a compact status line at the top of IMPLEMENTATION.md;
- update RESULT.md with literal counts/results;
- update GAPS.md with the measured next blocker/stage.
```

- [x] **Step 7: Stop**

Do not implement the next blocker. Return the implementation/test summary to the user so they can run `checkpoint`. ChatGPT should then review that checkpoint and decide whether the next step is a substantive G3/G4/G5 accounting-policy step or another measured integration defect.
