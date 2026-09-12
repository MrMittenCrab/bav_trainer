# Step 8B2.2 — Trusted Workbook State Hardening

> **Status:** Complete (local verification recorded in `RESULT.md`). Do not commit/push from Cursor.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `77df6213ae042a1ece94ac20888336a4ea7b1e75` (`Step 8.2 Hardened`). Implement only Step 8B2.2 below using red/green TDD. Preserve all Step 8A, Step 8B1, Step 8B2, and Step 8B2.1 behavior except where this plan explicitly corrects treatment-whitespace semantics and strengthens trusted-workbook validation. Do not begin Step 9, earnings-quality diagnostics, accrual/cash-conversion analysis, forecasting, valuation, ROU/deferred-tax alternative modeling, or any new curriculum feature. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Guarantee that Formula Check and the visible workbook operate on the same trusted state. Invalid or padded judgment inputs must fail closed, and edits to system-supplied source/setup/model cells must be detected before learner formulas can receive green status.

**Architecture:** Keep exact-formula acceptance. Do not add a formula evaluator. Instead, establish a clear workbook boundary: semantic practice cells and designated judgment response cells are learner-controlled; source facts, supplied classifications, generated links, labels, and other active model cells are system-controlled. Before grading, compare those trusted cells against the matching Answer Key.

**Tech Stack:** Python, pytest, openpyxl, existing `SemanticMap`, `CheckContext`, `validate_live_model_structure`, `check_workbook`, and OOXML fill patching.

**Spec:** `TARGET.md`, especially supplied-source preservation, supplied setup judgments, semantic practice mapping, model auditability, professional-workbook preservation, Trainer/Answer-Key separation, and non-disclosing workbook-wide Check.

---

## Review of commit `77df6213`

Step 8B2.1 successfully added:

- duplicate normalization-candidate rejection;
- stable `line_identity` normalization computation;
- label-selector preservation;
- typographic-apostrophe normalization;
- protection of generated non-practice `Earnings Normalization` formulas;
- whitespace-only treatment rejection;
- no partial recoloring after structural failure.

Two integrity gaps remain.

### Gap 1 — padded valid treatments produce two different model states

Python currently strips:

```python
" Non-recurring " -> "Non-recurring"
```

while the workbook live formula returns the untrimmed value in F.

This can make:

```text
Python Check state != Excel workbook state
```

Do not solve this by making Excel silently normalize arbitrary pasted input. Fail closed instead.

### Gap 2 — supplied facts/setup remain outside the integrity boundary

Exact formulas are accepted structurally. Therefore the inputs feeding those formulas must be trustworthy.

Currently a learner can accidentally alter, among other things:

- historical source-statement numbers;
- supplied fixed balance-sheet classifications;
- non-practice generated/model cells outside the normalization-specific gate.

Check can still mark an exact formula green.

Step 8B2.2 establishes the system-controlled/learner-controlled cell boundary explicitly.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve five demo fiscal years.
- Preserve base build at 25 families / 118 practice cells.
- Preserve normalization build at 29 families / 138 practice cells.
- Practice cells remain learner-controlled.
- `Accounting Judgment` and `Normalization Judgment` F:G:H remain learner-controlled where case rows exist.
- F is the only live treatment input.
- G:H remain ungraded free-form responses.
- Source statements are supplied system facts, not learner practice.
- Fixed classifications are supplied system facts, not learner practice.
- Generated links/formulas outside semantic practice cells are system-controlled.
- Check must fail before any fill update when trusted workbook state has been modified.
- Check remains non-disclosing.
- Do not compare styles or comments as part of model-state integrity.
- Do not add a formula evaluator.
- Do not change economic formulas.
- Do not regenerate committed demo XLSX files unless workbook generation itself must change.
- No new public CLI command.
- No Step 9 work.
- Cursor must not commit, push, merge, reset, rebase, or delete branches.

---

## Task 1 — Reject all padded treatment input

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/tests/test_normalization.py`
- Modify classification-related tests only if needed

### Correct treatment semantics

Replace the current trimming-and-accepting behavior.

Required contract:

```python
None
    -> reference treatment

""
    -> reference treatment

"Recurring"
    -> "Recurring"

"Non-recurring"
    -> "Non-recurring"

" Recurring "
    -> ValueError

"Non-recurring "
    -> ValueError

" Financial Liability "
    -> ValueError

"   "
    -> ValueError

"Not A Treatment"
    -> ValueError
```

A nonblank treatment must exactly equal one of the allowed strings as stored in Excel.

Implement the equivalent of:

```python
def _validated_treatment_selection(
    selected,
    *,
    reference_treatment: str,
    allowed_treatments: tuple[str, ...],
    sheet_name: str,
    row: int,
) -> str:
    if selected is None or selected == "":
        return reference_treatment

    if not isinstance(selected, str):
        raise ValueError(
            f"Invalid treatment value on {sheet_name} row {row}: "
            f"expected one of {list(allowed_treatments)}"
        )

    if selected != selected.strip():
        raise ValueError(
            f"Treatment contains surrounding whitespace on "
            f"{sheet_name} row {row}"
        )

    if selected not in allowed_treatments:
        raise ValueError(
            f"Invalid treatment {selected!r} on {sheet_name} row {row}; "
            f"allowed: {list(allowed_treatments)}"
        )

    return selected
```

Do not change `live_classification_formula()` or `live_normalization_treatment_formula()` to use `TRIM()`.

### TDD

- [ ] Replace `test_padded_valid_treatments_are_accepted`.
- [ ] Add a normalization regression where `" Non-recurring "` raises.
- [ ] Add a normalization regression where `" Recurring "` raises.
- [ ] Add a classification regression where `" Financial Liability "` raises.
- [ ] Keep `None` and `""` reference-fallback tests.
- [ ] Keep exact valid-treatment tests.
- [ ] Prove failure leaves existing practice-cell fills unchanged.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py \
  -k "whitespace or padded or treatment" -v
```

---

## Task 2 — Define the trusted workbook-cell boundary

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/trainer/checker.py`
- Test: `core/tests/test_normalization.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py` if needed

Create a generic content-integrity helper.

Suggested interface:

```python
def _validate_trusted_sheet_cells(
    trainer_ws,
    answer_ws,
    *,
    sheet_name: str,
    editable_cells: set[str],
) -> None:
    ...
```

### Comparison rule

Use `data_only=False`.

Iterate through the union of the Trainer and Answer-Key used dimensions:

```python
max_row = max(trainer_ws.max_row or 0, answer_ws.max_row or 0)
max_col = max(trainer_ws.max_column or 0, answer_ws.max_column or 0)
```

For every coordinate not present in `editable_cells`:

```python
trainer_value == answer_value
```

must hold.

Compare contents only.

Do not compare:

- fill;
- font;
- border;
- number format;
- comment;
- data validation;
- worksheet view state.

If values differ:

```text
Trusted workbook cell was modified: <sheet>!<cell>
```

raise `ValueError`.

This must happen before grading or fill planning.

---

## Task 3 — Apply trusted-state validation to supplied source/model sheets

### A. Historical source sheets

The following sheets have no semantic practice cells and no learner judgment cells:

```text
Income Statement
Balance Sheet
Cash Flow Statement
```

Every populated/model cell on these sheets is trusted.

Validate their cell contents completely against the Answer Key.

This must catch changes to:

- historical numbers;
- labels;
- dates;
- units/source setup;
- concepts as represented in the workbook.

### B. `Condensed Financials`

All cells are trusted except semantic practice cells on that sheet.

Construct:

```python
editable_condensed = {
    cell
    for tab, cell in practice_cells
    if tab == "Condensed Financials"
}
```

Validate every other cell against the Answer Key.

This protects, among other things:

- supplied fixed balance-sheet classifications;
- generated live classification links;
- non-practice reconciliation/model formulas;
- labels and headers.

The existing per-binding live-classification validator may remain as a more specific error check, but behavior must not conflict with the generic integrity gate.

### C. `ALT DuPont`

All cells are trusted except semantic practice cells on that sheet.

Validate every other cell.

### D. `Earnings Normalization`

All cells are trusted except semantic practice cells.

The new generic mechanism may replace `_validate_generated_formula_cells()` if doing so reduces duplication.

Do not maintain two independent implementations of the same invariant unless the specific treatment-link check provides a clearer error message.

### E. Judgment sheets

For:

```text
Accounting Judgment
Normalization Judgment
```

columns A:E are trusted context.

On actual numbered case rows:

```text
F = learner treatment
G = learner rationale
H = learner consequence
```

are editable.

Do not compare F:G:H with the Answer Key.

Headers, instructions, row identity, scope/topic, reference treatment, and listed alternatives remain trusted.

Prefer constructing explicit editable coordinate sets from `context.judgment_bindings` and `context.normalization_bindings`.

Do not infer editable rows from worksheet labels.

---

## Task 4 — Close the exact-formula false-green regression

**Files:**
- Test: `core/tests/test_normalization.py`
- Test: `core/tests/test_reference_integrity.py`

Add end-to-end regressions proving trusted-state validation happens before the exact-formula shortcut.

### Source-value tamper

1. Build a Trainer/Answer-Key pair.
2. Put the exact correct formula into one historical practice cell.
3. Change one source-statement number in the Trainer.
4. Run Check.
5. Require `ValueError`.
6. Reopen Trainer.
7. Prove the practice cell remains yellow.

Use an upstream source value relevant to the selected practice formula.

### Fixed-classification tamper

1. Find one supplied, non-judgment balance-sheet classification in `Condensed Financials`.
2. Change it to another otherwise valid category.
3. Put an exact downstream formula into a practice cell.
4. Run Check.
5. Require structural failure before green recoloring.

Do not use a live judgment-driven classification row for this test.

### Non-practice formula tamper

Retain the Step 8B2.1 generated-normalization tamper regression.

### Learner edits still allowed

Prove all of these remain valid:

- alternate equivalent practice formula;
- valid exact F treatment;
- blank F reference fallback;
- free-form G rationale;
- free-form H consequence.

Free-form G/H content must never cause trusted-state validation failure.

---

## Task 5 — Preserve legacy/no-normalization behavior

The integrity gate must work with both:

```text
25-family / 118-cell base workbook
29-family / 138-cell normalization workbook
```

For a base workbook:

- no `Normalization Judgment` required;
- no `Earnings Normalization` required;
- source-sheet integrity still applies;
- fixed classification integrity still applies;
- `Accounting Judgment` F:G:H remain editable;
- existing schema-v1 Check-context compatibility remains intact.

Add at least one trusted-source-tamper regression using the no-normalization build.

---

## Task 6 — Verification

Run focused tests first:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Do not state the expected total test number in advance. Record the actual passing count.

Verify base build:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required:

```text
118 practice cells
0 correct / 0 incorrect / 118 blank
25 schedule groups
```

Verify normalization build:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o /tmp/DEMO_NORM_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_NORM_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_NORM_Trainer.xlsx
```

Required:

```text
138 practice cells
0 correct / 0 incorrect / 138 blank
29 schedule groups
```

Verify CLI:

```bash
PYTHONPATH=. python -m core --help
```

Public commands remain:

```text
ingest
build
check
list
```

---

## Task 7 — Update checkpoint documentation

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

`RESULT.md` must record:

- actual full-suite pass count;
- exact padded treatment rejected;
- blank treatment fallback preserved;
- source statements structurally protected;
- fixed supplied classifications structurally protected;
- non-practice model cells protected;
- learner practice formulas still editable/equivalent-formula eligible;
- F:G:H learner judgment surface preserved;
- no partial recoloring on integrity failure;
- base 25 / 118 preserved;
- normalization 29 / 138 preserved;
- no Step 9 functionality introduced.

Do not write `Unresolved: none` unless all regressions above pass.

---

## Definition of done

Step 8B2.2 is complete only when:

1. Python Check and Excel use exactly the same judgment-treatment string.
2. Any surrounding whitespace in nonblank treatment input fails closed.
3. Historical source facts cannot be edited while still receiving green formula checks.
4. Supplied fixed classifications cannot be edited while still receiving green formula checks.
5. Generated non-practice model formulas remain protected.
6. Practice cells remain learner-controlled.
7. Judgment F:G:H remain learner-controlled on case rows.
8. Equivalent formulas continue to pass based on current-state results.
9. Integrity failure occurs before any fill update.
10. Base surface remains 25 / 118.
11. Normalization surface remains 29 / 138.
12. Full test suite passes.
13. `TARGET.md` remains unchanged.
14. Step 9 has not begun.

After finishing, stop and report changed files and exact verification output. Do not commit or push.
