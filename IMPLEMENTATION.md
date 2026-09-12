# Step 8B1.1 — Live-Judgment Integrity Hardening

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `74d9867bbf76a94d8eeff1b4339ce31de37b1921` (`Step 8B1`). Implement only this hardening checkpoint using red/green TDD. Preserve the live Step 8B1 treatment-conditioned model and Check behavior. Do not begin normalization / recurring-vs-non-recurring treatment, earnings-quality diagnostics, forecasting, valuation, or Step 8B2. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make the Step 8B1 feedback loop trustworthy when workbook setup cells are accidentally edited: `Accounting Judgment!F` must remain the only learner classification input, generated live-classification links must be structurally validated before Check, and Check must leave no workbook handles or partial color updates behind when validation fails.

**Architecture:** Keep the Step 8B1 hidden `_CheckContext` and dynamic expected-value engine. Change the generated `Condensed Financials` classification formula so blank learner treatment falls back to a literal trusted reference treatment rather than the editable display cell in `Accounting Judgment!D`. Add one shared live-link formula builder and a pre-Check structural validator that compares the Trainer's generated live links and judgment prompt fields against the Answer Key / Check context. Refactor `check_workbook()` so every opened workbook closes through `finally` on all error paths and fill updates happen only after validation and expected-value computation succeed.

**Tech Stack:** Python, pytest, openpyxl, existing `CheckContext`, `JudgmentBinding`, `ReferenceModelBuilder`, `TrainingWorkbookGenerator`, `check_workbook`, and OOXML fill patching.

**Spec:** `TARGET.md`, especially Level 2 — Analyst judgment, model auditability/reconciliation, the requirement that the learner choose and defend treatments, and the non-disclosing workbook-wide Check contract.

## Review of commit `74d9867b`

The main Step 8B1 architecture is present:

- `Accounting Judgment!F` drives supported classifications;
- blank treatment falls back to the supplied reference treatment;
- `_CheckContext` is Answer-Key-only and contains model facts / judgment bindings rather than formula answers;
- dynamic expected values cover all 25 historical families;
- equivalent-formula Check can use treatment-conditioned expected values;
- the five-year demo remains 25 formula families / 118 formula cells;
- `RESULT.md` records 130 locally passing tests and successful build/check/list verification.

GitHub has no attached CI status, so the recorded test counts are local implementation evidence, not independent CI evidence.

Three issues must be hardened before Step 8B2:

1. **The visible reference-treatment display cell is accidentally part of the live model.** The current generated formula is equivalent to:

```excel
=IF('Accounting Judgment'!$F$5="",'Accounting Judgment'!$D$5,'Accounting Judgment'!$F$5)
```

But column D is intended as prompt/context, not a learner input. If D is edited while F is blank, the workbook model changes while dynamic Check still uses the reference treatment stored in `_CheckContext`. This violates the one-input-surface rule and can make workbook state diverge from Check state.

2. **Generated live-classification links are not validated by Check.** If a learner accidentally overwrites the linked classification formula in `Condensed Financials`, downstream exact formulas can still be marked structurally correct even though the workbook is no longer being driven by the selected judgment treatment. Check needs a fail-fast setup-integrity gate before grading formula cells.

3. **`check_workbook()` does not close all opened Trainer workbooks on every validation / recomputation exception.** Invalid pasted treatments and other dynamic-context failures can raise after workbooks are opened. The error path should close resources and must not partially recolor formula cells.

One test also contains a vacuous assertion of the form `... or True`; remove it and replace it with a treatment-sensitive assertion.

Do not add normalization until these invariants are enforced.

## Global constraints

- `TARGET.md` is read-only.
- Preserve exactly five demo fiscal years, 25 historical formula families, and 118 formula practice cells.
- Preserve the four supported live judgment templates: lease liability, pension obligation, short-term investment, associate/JV investment.
- ROU and deferred-tax balances remain unsupported guided alternatives.
- `Accounting Judgment!F` is the **only** live learner classification input.
- `Accounting Judgment!D:E` are display/context cells only and must not control model economics.
- Blank F still means the supplied reference treatment.
- Main practice formulas and formula coordinates remain unchanged.
- Formula Check remains non-disclosing and judgment rationale/consequence remain ungraded.
- `_CheckContext` remains Answer-Key-only and contains no formula answers, expected-value answer store, formula hints, or rationale/consequence answers.
- No normalization, recurring/non-recurring adjustment, earnings-quality diagnostics, forecasting, valuation, Hint/Reveal, VBA, or automated free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Make F the only live treatment input

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**

Create one shared generated-link helper in `core/trainer/check_context.py`:

```python
def live_classification_formula(
    judgment_row: int,
    reference_treatment: str,
) -> str:
    ...
```

For row 5 and reference treatment `Operating Long-Term Liability`, it must return the Excel formula semantically equivalent to:

```excel
=IF('Accounting Judgment'!$F$5="","Operating Long-Term Liability",'Accounting Judgment'!$F$5)
```

Requirements:

- blank F -> trusted literal reference treatment;
- nonblank F -> learner treatment;
- do **not** reference `Accounting Judgment!D`;
- escape any double quote in a future category string correctly;
- reject `judgment_row < 1` and blank `reference_treatment` with `ValueError`.

`ReferenceModelBuilder._build_condensed()` must call this shared helper for supported judgment rows instead of hand-authoring the current D-linked formula.

### TDD steps

- [ ] Add a failing unit test for `live_classification_formula(5, "Operating Long-Term Liability")` asserting:

```python
assert "$F$5" in formula
assert "$D$5" not in formula
assert '"Operating Long-Term Liability"' in formula
```

- [ ] Add validation tests for row `0` and an empty reference treatment.
- [ ] Build the demo and locate `Operating lease liabilities` in `Condensed Financials`. Assert its column-B formula is exactly `live_classification_formula(5, "Operating Long-Term Liability")` in both Trainer and Answer Key.
- [ ] Assert the classification-link cell remains non-yellow, non-practice, and absent from `SemanticMap`.
- [ ] Assert ordinary rows such as `Bank borrowings` remain literal classifications with their existing category data validation.
- [ ] Run the focused tests and verify red state against commit `74d9867b`:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "live_classification_formula or live_classification or judgment_link" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "judgment_link" -v
```

- [ ] Implement the helper and builder change.
- [ ] Rerun the focused tests until green.

---

## Task 2 — Add a fail-fast judgment-structure integrity gate

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**

Create:

```python
def validate_live_judgment_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
) -> None:
    ...
```

This validates generated/setup structure only. It must **not** grade learner rationale/consequence and must not reject an allowed F selection.

For every `JudgmentBinding`:

1. `Accounting Judgment` must exist in both workbooks.
2. `Condensed Financials` must exist in both workbooks.
3. Trainer and Answer Key column D at `binding.worksheet_row` must equal `binding.reference_treatment`.
4. Trainer and Answer Key column E must equal the display form of the allowed alternatives:

```python
", ".join(binding.allowed_treatments[1:])
```

5. Construct the expected system link with:

```python
expected_formula = live_classification_formula(
    binding.worksheet_row,
    binding.reference_treatment,
)
```

6. On the **Answer Key** `Condensed Financials` sheet, scan column B and require exactly one cell whose value equals `expected_formula`. Zero or multiple matches are a programming/build-integrity error.
7. At that exact coordinate in the **Trainer**, require the same `expected_formula`. A literal category, changed formula, or blank cell is a setup-integrity error.
8. Do not compare F between Trainer and Answer Key: F is intentionally learner-editable.
9. Do not compare G:H: they are free-form learner responses.

Raise concise `ValueError` messages that identify the affected judgment row and/or Condensed coordinate without disclosing formulas or model expected values in CLI output. Example concepts:

```text
Accounting Judgment reference prompt was modified on row 5
Accounting Judgment alternatives prompt was modified on row 5
Linked Condensed Financials classification was modified at B15
Answer Key live-classification binding is missing/ambiguous for judgment row 5
```

`check_workbook()` must call `validate_live_judgment_structure(...)` before reading learner treatments and before preparing any fill updates.

### TDD steps

- [ ] Build a fresh demo pair; structural validation must pass with F blank and again with F set to `Financial Liability`.
- [ ] Modify Trainer `Accounting Judgment!D5`; `check_workbook()` must raise `ValueError` before recoloring formula cells.
- [ ] Restore D5, then modify Trainer `Accounting Judgment!E5`; Check must fail before grading.
- [ ] Restore E5, then replace the live lease classification formula in `Condensed Financials!B...` with a literal category; Check must fail before grading.
- [ ] Add a synthetic two-case pair and prove each binding resolves to exactly one distinct generated Condensed link.
- [ ] Before each fail-fast test, leave a practice cell yellow; after the raised exception, reopen the Trainer and assert that cell is still yellow. Validation failure must cause **zero partial Check color updates**.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "judgment_structure or prompt_modified or classification_modified" -v
```

- [ ] Implement the validator and wire it before treatment extraction.
- [ ] Rerun until green.

---

## Task 3 — Make Check exception-safe and remove the vacuous regression

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**

Refactor `check_workbook()` so every workbook opened after `load_check_context()` is closed through one `try/finally` boundary.

Required structure:

```python
wb = load_workbook(trainer_path, data_only=False)
wb_cached = load_workbook(trainer_path, data_only=True)
answer_wb = load_workbook(answer_key_path, data_only=False) if context is not None else None
try:
    # structural validation
    # learner-treatment validation
    # dynamic anchor / expected computation
    # collect CellFillUpdate objects only
finally:
    wb.close()
    wb_cached.close()
    if answer_wb is not None:
        answer_wb.close()

# only after successful try block:
apply_fill_updates(trainer_path, updates)
return summary
```

Do not call `apply_fill_updates()` from inside the protected block. Any invalid treatment, malformed live link, model-integrity failure, or expected-value computation error must leave existing cell fills untouched.

### Tests

- [ ] Add an invalid-treatment test by bypassing Excel validation and writing an unsupported string into F5. Assert Check raises and a previously yellow practice cell remains yellow.
- [ ] Add a valid-alternative control immediately afterward to prove the same pair remains usable after the failed attempt.
- [ ] Remove every assertion ending in `or True` from the Step 8B1 regressions.
- [ ] For the exact-formula alternative-state test, explicitly select a treatment-sensitive family such as latest `financial_liabilities_agg`, `oltl_agg`, or `net_debt` and assert:

```python
assert alt_expected != pytest.approx(reference_expected)
```

before asserting the exact formula is accepted.
- [ ] Preserve the existing equivalent-formula stale-reference test: alternative cached expected -> green; stale reference cached value -> red.
- [ ] Preserve repeated-Check cache behavior.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "alternative_treatment or invalid_treatment or repeated or stale_reference" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record exact pass counts in `RESULT.md`.

---

## Task 4 — Re-audit Step 8B1 and stop before normalization

**Files:**
- Modify: `README-HK-TRAINER.md` only if wording needs correction
- Modify: `skills/bav-trainer/SKILL.md` only if wording needs correction
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

### Documentation wording

The current capability should be described as:

```text
Step 8B1 live supported classification
- Accounting Judgment column F is the only learner treatment input
- blank F uses the supplied reference treatment
- generated Condensed Financials links are system-controlled and validated by Check
- Formula Check recomputes expected historical values for the selected supported treatment
- rationale/consequence remain ungraded
```

Do not claim normalization, recurring/non-recurring adjustment, earnings-quality diagnostics, deferred-tax/ROU alternatives, forecasting, or valuation.

### Full verification

Run fresh:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core --help
```

Required end state:

```text
formula families: 25
formula practice cells: 118
fresh Check: 0 correct / 0 incorrect / 118 blank
one illustrative lease judgment case
Trainer has no _CheckContext
Answer Key has valid hidden _CheckContext
F is the only live judgment input
D/E prompt edits are rejected before grading
Condensed generated-link edits are rejected before grading
valid reference and valid alternative treatment both pass structural validation
exact and equivalent formula Check still work under the alternative
invalid treatment / structural failure causes no partial recoloring
normal build does not call run_scenario()
CLI remains {ingest,build,check,list}
```

Update `RESULT.md` with actual observed counts/results only. Do not copy expected counts into the result without running them.

## Step 8B1.1 acceptance criteria

This checkpoint is accepted only when all are true:

1. blank judgment treatment falls back to a literal trusted reference treatment, not editable column D;
2. F is the sole workbook cell whose learner value can change supported classification economics;
3. Check validates D/E prompt integrity before grading;
4. Check validates every generated live Condensed classification link before grading;
5. an overwritten linked classification cannot silently coexist with a successful Formula Check;
6. invalid treatment / structural failure produces zero partial fill changes;
7. every workbook opened by the dynamic Check path is closed on success and failure;
8. no vacuous `or True` regression remains;
9. treatment-sensitive expected-value tests prove the selected alternative actually changes the expected family being tested;
10. dynamic reference/alternative exact and equivalent formula Check behavior remains intact;
11. five periods / 25 families / 118 formula cells remain unchanged;
12. Step 8A reasoning cells remain free-form/ungraded and answer separation remains intact;
13. forecast quarantine and CLI surface remain unchanged.

---

# Locked next roadmap — do not implement in Step 8B1.1

## Step 8B2 — Recurring/non-recurring treatment and earnings normalization

After the live-classification feedback loop passes this structural integrity checkpoint, add a separately modeled normalization subsystem. It should introduce explicit supplied facts and guided decisions for material income-statement items, distinguish reported from normalized earnings, reconcile the normalization bridge, and extend treatment-conditioned Check without silently rewriting historical source statements.

## Step 9 — Historical research diagnostics

Teach the learner to diagnose margins, capital intensity/turnover, working-capital behavior, cash conversion/accruals, financing contribution to ROE, dilution, segment economics, and earnings-quality signals.

## Step 10 — Cross-company and period-cadence robustness

Validate materially different non-financial companies and harden annual/interim/stub handling before broad robustness claims.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, scenarios, and concise investment interpretation only after the forecast layer is independently trusted.
