# Step 8B2.1 — Normalization Integrity Hardening

> **Status:** Complete (local verification recorded in `RESULT.md`). Do not commit/push from Cursor.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `3c02649c7fc00272297c557fba9d88a007bf289d` (`Step 8.2`). Implement only the Step 8B2.1 hardening below using red/green TDD. Preserve the existing Step 8A/8B1 classification workflow and Step 8B2 normalization workflow. Do not begin Step 9, earnings-quality diagnostics, accrual/cash-conversion analysis, ROU/deferred-tax alternative modeling, forecasting, or valuation. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make Step 8B2 trustworthy under workbook tampering and edge-case configuration: a green Check must not survive broken system-controlled normalization links, duplicate candidates must not double-count earnings adjustments, normalization source identity must remain stable, and invalid treatment input must fail closed.

**Architecture:** Keep the existing normalization model and workbook surface. Harden the boundary around it rather than redesigning it. Formula practice cells remain learner-editable and may contain any equivalent formula; generated non-practice formulas in `Earnings Normalization` are system-controlled and must exactly match the Answer Key before grading. Normalization candidates resolve once to stable line identity, and later computation must use that identity rather than re-resolving through a potentially ambiguous selector.

**Tech Stack:** Python, pytest, openpyxl, existing `NormalizationCase`, `CheckContext`, `SemanticMap`, `ReferenceModelBuilder`, `check_workbook`, and OOXML-preserving fill patching.

**Spec:** `TARGET.md`, especially Level 2 analyst judgment, earnings normalization, auditability/reconciliation, reported-source preservation, Trainer/Answer-Key separation, and non-disclosing workbook-wide Check.

---

## Review of commit `3c02649c`

Step 8B2 is substantially implemented:

- explicit normalization candidates;
- `Recurring` / `Non-recurring` guided judgment;
- separate `Normalization Judgment` and `Earnings Normalization` sheets;
- four normalization formula families;
- treatment-conditioned Formula Check;
- schema-v2 `_CheckContext`;
- no-assumptions build preserved at 25 families / 118 practice cells;
- demo normalization build at 29 families / 138 practice cells;
- Step 8B1 classification and Step 8B2 normalization compose in one Check.

Before Step 9, harden these defects:

1. Exact learner formulas can currently be marked correct even if a generated non-practice dependency in `Earnings Normalization` has been overwritten.
2. The same source line can be configured as a normalization candidate more than once, allowing duplicate adjustment rows and potential double-counting.
3. A uniquely resolved label candidate may later be converted to a concept selector that is ambiguous across multiple differently labeled lines.
4. Whitespace-only judgment values are treated as blank by Python Check but not by the generated Excel live-link formula.
5. Typographic apostrophe normalization in label selectors contains an implementation typo.

This checkpoint fixes only those defects.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve the current five-year demo.
- Preserve the no-normalization surface: 25 families / 118 practice cells.
- Preserve the normalization demo surface: 29 families / 138 practice cells.
- Preserve all existing Step 8B1 classification behavior.
- Preserve Step 8B2 economics and the `operating_pretax_effective_tax` convention.
- Reported source statements and reported historical formulas remain unchanged by normalization choices.
- Formula practice cells remain learner-editable and may use equivalent formulas.
- Generated non-practice model links are not learner inputs.
- Check must fail before applying any fill changes when structural validation fails.
- Check remains non-disclosing.
- `_CheckContext` remains Answer-Key-only.
- No formula answers, expected values, hints, rationale answers, or consequence answers may leak into the Trainer.
- No new public CLI command.
- No forecasting, valuation, Step 9 diagnostics, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Protect every generated formula feeding `Earnings Normalization`

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/trainer/checker.py`
- Test: `core/tests/test_normalization.py`

### Problem

`check_workbook()` accepts an exact practice formula before evaluating its result.

That is correct for learner formula grading only if all non-practice inputs to that formula are still trustworthy.

Step 8B2 currently structurally protects the generated treatment link, but `Earnings Normalization` also contains generated formulas linking:

- normalization treatment;
- source income-statement amounts;
- reported NOPAT;
- reported Net Income;
- effective tax rate;
- `NORMALIZATION CHECK`.

If one of these is overwritten, an untouched learner formula must not still receive green.

### Interface

Extend:

```python
def validate_live_model_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
    *,
    practice_cells: set[tuple[str, str]] | None = None,
) -> None:
    ...
```

Existing three-argument callers must continue to work by treating `practice_cells=None` as an empty set.

In `check_workbook()` construct:

```python
practice_cells = {
    (comp.tab, comp.cell)
    for comp in comps
}
```

and call:

```python
validate_live_model_structure(
    wb,
    answer_wb,
    context,
    practice_cells=practice_cells,
)
```

### Structural rule

When `context.normalization_bindings` is non-empty:

1. `Normalization Judgment` and `Earnings Normalization` must exist in both Trainer and Answer Key.
2. Preserve the existing D/E prompt validation and generated treatment-link validation.
3. Inspect the trusted Answer Key `Earnings Normalization` sheet.
4. For every cell whose Answer-Key value is an Excel formula beginning with `=`:
   - if `(EARNINGS_NORMALIZATION_SHEET, cell.coordinate)` is a semantic practice cell, ignore it;
   - otherwise the Trainer cell at the same coordinate must contain the exact same formula.
5. Any mismatch raises `ValueError` before treatment recomputation and before any fill updates.

Do not compare learner practice formulas structurally. They must remain eligible for equivalent-formula grading.

A focused helper is preferred:

```python
def _validate_generated_formula_cells(
    trainer_ws,
    answer_ws,
    *,
    sheet_name: str,
    excluded_cells: set[str],
) -> None:
    ...
```

`excluded_cells` should contain the practice coordinates for that sheet only.

### TDD

- [ ] Build a normalization Trainer/Answer-Key pair.
- [ ] Parameterize tampering cases covering at least:
  - detail source-link formula;
  - reported NOPAT link;
  - reported Net Income link;
  - effective-tax-rate link;
  - `NORMALIZATION CHECK` formula.
- [ ] For each case, overwrite the Trainer formula and assert `check_workbook()` raises `ValueError`.
- [ ] Before calling Check, put a valid learner formula in one practice cell.
- [ ] After the structural failure, reopen the workbook and prove that practice cell retained its previous yellow fill: no partial recoloring occurred.
- [ ] Preserve the existing treatment-link tamper regression.
- [ ] Add a regression proving a learner practice cell may differ from the Answer Key formula and still reach normal grading rather than structural rejection.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py -k "tamper or generated or structural" -v
```

This command runs only the new setup-integrity regressions.

Implement the minimal validation and rerun until green.

---

## Task 2 — Make normalization candidates unique and source identity stable

**Files:**
- Modify: `core/model/normalization.py`
- Test: `core/tests/test_normalization.py`

### Part A — Reject duplicate configured candidates

`normalization_cases()` must never produce two cases for the same resolved income-statement line.

Track resolved:

```python
identity = line_identity(item).key()
```

while parsing configured candidates.

If the same identity appears more than once, raise:

```text
duplicate normalization candidate for income-statement line ...
```

Reject duplicates after selector resolution but before case construction.

Do not silently deduplicate. A duplicate assumptions file is a configuration error.

### Tests

- [ ] Configure the same `concept:` candidate twice -> `ValueError`.
- [ ] Configure the same line once by concept and once by label -> `ValueError`.
- [ ] Assert the error occurs rather than producing two cases.

### Part B — Compute using `line_identity`, not a re-resolved selector

Create:

```python
def resolve_income_statement_identity(
    financials: StandardizedFinancials,
    identity_key: str,
) -> LineItem:
    ...
```

Implementation contract:

```python
matches = [
    item
    for item in financials.income_statement
    if line_identity(item).key() == identity_key
]
```

Exactly one match is required.

- zero matches -> `ValueError`;
- more than one match -> `ValueError`.

Change `compute_normalization_series()` so:

```python
items_by_case[case.id]
```

is resolved from:

```python
case.line_identity
```

rather than `case.override_selector`.

The candidate selector is used to choose the line when creating the case. Once chosen, stable line identity is authoritative.

### Part C — Preserve selector semantics

Fix `_stable_override_selector()`.

If the supplied selector is a concept selector:

```text
concept:<normalized concept>
```

may remain the stored selector.

If the supplied selector is a label selector or bare label:

```text
label:<original resolved line label>
```

must remain label-based even when the selected row also has a concept.

Do not silently convert a unique label selection into a possibly non-unique concept selection.

### Regression test

Construct two income-statement rows such as:

```text
concept = "special_item"
label   = "Restructuring charge"

concept = "special_item"
label   = "Litigation charge"
```

Then:

```python
selector = "label:Restructuring charge"
```

must:

1. resolve exactly one normalization case;
2. retain a label-based stable selector;
3. compute normalization using only `Restructuring charge`;
4. not raise concept ambiguity;
5. not include `Litigation charge` in the adjustment.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py -k "duplicate or identity or selector" -v
```

Implement until green.

---

## Task 3 — Make invalid judgment input fail closed

**Files:**
- Modify: `core/trainer/check_context.py`
- Test: `core/tests/test_normalization.py`
- Test existing classification tests if needed

### Problem

The generated workbook live link treats only a genuinely empty F cell as blank:

```excel
F5=""
```

Python currently strips whitespace and can interpret `"   "` as blank/reference treatment.

That creates two different model states.

Do not broaden Excel formula behavior in this checkpoint. Instead make Check reject whitespace-only and other non-option input.

### Required behavior

For both:

```python
classification_overrides_for_check(...)
normalization_treatments_for_check(...)
```

use this semantic distinction:

```python
selected is None or selected == ""
    -> use reference treatment

selected contains non-empty text
    -> strip surrounding whitespace
    -> resulting treatment must be one of allowed_treatments

selected contains only whitespace
    -> ValueError
```

A helper may be introduced to remove duplication:

```python
def _validated_treatment_selection(
    selected,
    *,
    reference_treatment: str,
    allowed_treatments: tuple[str, ...],
    sheet_name: str,
    row: int,
) -> str:
    ...
```

Required cases:

```text
None                  -> reference
""                    -> reference
"Recurring"           -> Recurring
" Recurring "         -> Recurring
"   "                 -> ValueError
"Not A Treatment"     -> ValueError
```

### Tests

- [ ] `Normalization Judgment!F = "   "` -> Check raises before recoloring.
- [ ] `Accounting Judgment!F = "   "` -> Check raises before recoloring.
- [ ] Leading/trailing spaces around a valid treatment are accepted after stripping.
- [ ] Exact blank behavior remains unchanged.
- [ ] Existing invalid-treatment tests remain green.

Run the normalization test plus the relevant classification integrity tests.

---

## Task 4 — Fix typographic-apostrophe label matching

**Files:**
- Modify: `core/model/normalization.py`
- Test: `core/tests/test_normalization.py`

Current `_label_match_key()` must normalize common typographic apostrophes deliberately.

Use:

```python
for ch in ("\u2018", "\u2019", "`"):
    s = s.replace(ch, "'")
```

Do not include ASCII `'` in the replacement tuple because replacing it with itself is meaningless.

Add a regression such as:

```text
statement label: Director’s fee
selector:        label:Director's fee
```

and prove it resolves the intended line.

Also test the reverse spelling direction if useful.

Do not add broader fuzzy matching, keyword matching, punctuation stripping, or normalization heuristics.

---

## Task 5 — Full regression and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` only to record completion/status after implementation
- Modify: `README-HK-TRAINER.md` only if user-facing behavior requires clarification
- Do not modify: `TARGET.md`

Run the focused normalization suite first:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py -v
```

Then the existing integrity suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

Then the complete suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Rebuild the original no-normalization product:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx
```

Required:

```text
Components resolved: 118
```

Check it:

```bash
PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required fresh result:

```text
0 correct
0 incorrect
118 blank
```

Build the Step 8B2 normalization product:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o /tmp/DEMO_NORM_Trainer.xlsx
```

Required:

```text
Components resolved: 138
```

Check it:

```bash
PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_NORM_Trainer.xlsx
```

Required fresh result:

```text
0 correct
0 incorrect
138 blank
```

List both curriculum surfaces and confirm:

```text
base build:          25 schedule groups
normalization build: 29 schedule groups
```

Also verify:

```bash
PYTHONPATH=. python -m core --help
```

Public commands must remain:

```text
ingest
build
check
list
```

Do not regenerate committed demo XLSX files unless implementation changes their serialized workbook contents. This checkpoint should primarily alter validation/model-resolution code rather than workbook design.

Update `RESULT.md` with:

- final test count;
- base 25 / 118 preservation;
- normalization 29 / 138 preservation;
- generated normalization dependencies structurally protected;
- duplicate normalization candidates rejected;
- normalization computation uses stable line identity;
- label selector semantics preserved;
- whitespace-only treatment rejected;
- typographic apostrophe selector regression passing;
- no Step 9 functionality introduced.

---

## Definition of done

Step 8B2.1 is complete only when all of the following are true:

1. Overwriting any generated non-practice formula in `Earnings Normalization` makes Check fail before coloring learner cells.
2. Learner practice formulas remain free to differ structurally from the Answer Key and can still pass by equivalent value.
3. One income-statement line cannot appear as two normalization cases.
4. Normalization calculation uses the case's stable `line_identity`.
5. A label-selected row is not silently converted into an ambiguous concept-selected row.
6. Whitespace-only judgment input fails closed instead of producing a Check/workbook state disagreement.
7. Curly-versus-straight apostrophes work in explicit label selectors.
8. Base build remains 25 families / 118 practice cells.
9. Normalization build remains 29 families / 138 practice cells.
10. All tests pass.
11. `TARGET.md` is unchanged.
12. No Step 9, diagnostics, forecasting, or valuation work has begun.

After completing this checkpoint, stop and report the changed files, test outputs, and any unresolved issue. Do not proceed to Step 9 and do not commit or push.
