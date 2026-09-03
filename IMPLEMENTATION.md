# Step 6 — Support Dynamic Input Practice and Balance-Sheet Classification

> **For Cursor:** Read `TARGET.md` first. Step 5 is accepted at commit `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`). Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Generalize the semantic practice system from **13 fixed formula-only exercises** to a mixed formula/input model that can register real-company-dependent practice rows at build time. Use that capability first to make **every balance-sheet classification decision** a real Trainer exercise while preserving the Step 5 Trainer / Answer Key / workbook-wide Check contract.

**Architecture:** Keep the existing reference-model-first architecture and static coordinate-free `COMPONENT_CATALOG` for fixed formula exercises. Extend `ComponentSpec` / `ResolvedComponent` with an explicit answer kind (`formula` or `input`) and allow the reference builder to create runtime `ComponentSpec` instances for variable rows. Register each non-subtotal balance-sheet classification row by canonical `LineIdentity`, so duplicate displayed labels with distinct concepts remain separate. The Answer Key keeps the correct category and Note; the Trainer blanks the dropdown cell; Check validates the learner's selected category without exposing the answer.

**Tech Stack:** Python, pytest, openpyxl, existing OOXML cache-preserving fill patch.

**Spec:** `TARGET.md` at the current branch head. Do not modify `TARGET.md` in this step.

---

## Current checkpoint and review

Latest implementation commit: `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`) on `chatgpt/reference-model-integrity`.

### Step 5 review result

Step 5 is accepted by code inspection.

The correction pass now:

- keeps generated Answer-Key metadata out of the committed demo;
- preserves formula cached `<v>` values when Check recolors cells by patching only OOXML style references;
- keeps repeated value-based Check stable without requiring another Excel recalculation;
- preserves the sanitized Trainer / full Answer Key split;
- retains workbook-wide yellow/green/red Check;
- keeps Hint / Reveal removed;
- reports 81 passing core tests in `RESULT.md`.

GitHub still has no independent status checks attached to this commit, so Cursor's recorded test evidence remains the handoff evidence rather than independently rerun CI.

### Non-blocking hardening gap from the Step 5 review

`core/trainer/xlsx_fill_patch.py` now edits `styles.xml` and worksheet XML directly. The current suite proves cache preservation and fill changes, but it does not explicitly prove that a Check pass leaves **non-fill style properties and data validation** unchanged. Add that regression in this step because classification practice relies on Excel dropdown validation. Do not refactor the OOXML writer unless that regression fails.

### Main product blocker

The current semantic component contract is still formula-only:

```python
if not formula or not str(formula).startswith("="):
    raise ValueError(... requires a formula ...)
```

and `COMPONENT_CATALOG` contains only 13 fixed components. That means the trainer cannot represent an exercise whose answer is a literal input, and it cannot represent a variable number of rows such as balance-sheet classifications for a real company.

This is now the next architecture blocker before expanding the rest of the accounting / DuPont / forecasting / valuation practice surface.

Do **not** expand all model formulas in this step. Prove the new component contract with balance-sheet classification first; later steps can use the same mechanism for forecast assumptions and the remaining formulas.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve all accepted Step 3 accounting integrity, Step 4 concept-aware identity, and Step 5 Trainer / Answer Key / Check behavior.
- Keep the existing 13 fixed formula exercises working.
- Do not reintroduce Hint, Reveal, macros, Trainer answer metadata, or Trainer answer sidecars.
- Do not add fixed workbook coordinates to static component definitions.
- Dynamic component identity must derive from domain identity (`LineIdentity` / semantic identity), never row number.
- Preserve same-label / different-concept balance-sheet rows as separate practice components.
- Do not add HKEX/SEC automation or later BAVGEM quarterly / Core Earnings / Earnings Quality / Price Rationalization / ICC / DCF feature chains.
- Do not redesign forecasting or residual-income mathematics.
- Do not weaken existing tests.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Generalize semantic components to formula or input answers

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/semantic_map.py`
- Modify: `core/engine/map_embed.py`
- Test: create `core/tests/test_semantic_map.py` if a focused module is cleaner; otherwise extend `core/tests/test_trainer.py`

**Interfaces:**
- Existing fixed components remain `answer_kind="formula"` by default.
- New runtime classification components use `answer_kind="input"`.
- `ResolvedComponent.expected_value` remains the canonical correct result for both kinds.
- Formula components retain `formula="=..."`; input components use `formula=""`.

### Required data contract

Extend `ComponentSpec` with:

```python
answer_kind: str = "formula"  # "formula" | "input"
```

Extend `ResolvedComponent` with the same field.

Do not replace `expected_value`; it is still needed by Check:

```text
formula component:
    formula        = reference Excel formula
    expected_value = reference calculated value

input component:
    formula        = ""
    expected_value = correct literal input (string or number)
```

Keep this deliberately small. Do not introduce a generic exercise DSL.

### Registration validation

Update `SemanticMap.register()` so it validates by `spec.answer_kind`:

```python
if spec.answer_kind == "formula":
    require formula starts with "="
elif spec.answer_kind == "input":
    require formula in ("", None)
    require expected_value is not None
else:
    fail with a clear unsupported-answer-kind error
```

`validate_complete()` must continue checking the 13 fixed catalog components and must additionally validate **every registered component**, including runtime components:

- unique `id`;
- unique `semantic_key`;
- supported `answer_kind`;
- formula rule for formula components;
- no reference formula for input components;
- non-`None` expected value;
- dependency order when dependencies exist.

### Serialization

Add `answer_kind` to the embedded `_ComponentMap` and JSON sidecar representation.

For backward parsing of an older map that has no `answer_kind` column/key, infer:

```python
"formula" if formula starts with "=" else "input"
```

Do not require migration of old files merely to read them.

### TDD — write these first

Add focused tests equivalent to:

```python
def test_semantic_map_accepts_formula_component():
    spec = ComponentSpec(
        id="f",
        order=1,
        title="Formula",
        short_hint="hint",
        semantic_key="test.formula",
        category="test",
    )
    smap = SemanticMap()
    smap.register(spec, "Sheet1", 1, 1, "=1+1", 2)
    comp = smap.get("f")
    assert comp.answer_kind == "formula"
    assert comp.formula == "=1+1"


def test_semantic_map_accepts_input_component():
    spec = ComponentSpec(
        id="i",
        order=1,
        title="Input",
        short_hint="hint",
        semantic_key="test.input",
        category="classification",
        answer_kind="input",
    )
    smap = SemanticMap()
    smap.register(spec, "Sheet1", 2, 2, "", "Financial Asset")
    comp = smap.get("i")
    assert comp.answer_kind == "input"
    assert comp.formula == ""
    assert comp.expected_value == "Financial Asset"
```

Also add rejection tests:

```text
formula kind + empty formula -> fail
input kind + =formula -> fail
unsupported kind -> fail
input kind + None expected value -> fail
```

Add round-trip tests for both JSON and embedded workbook maps so `answer_kind` survives.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_semantic_map.py -v
```

If no new module is created, run the exact focused nodes added to the existing test module.

---

## Task 2 — Give runtime components deterministic build-order numbering

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/engine/component_catalog.py` only if a tiny helper is clearly cleaner
- Test: `core/tests/test_semantic_map.py` / `core/tests/test_trainer.py`

### Problem

Static `ComponentSpec.order` values are sufficient for 13 fixed exercises, but dynamic classification rows must appear in natural workbook/dependency order and their count varies by company.

Do not encode dynamic row numbers into static catalog order values.

### Required approach

Add one builder-level sequential practice-order counter, for example:

```python
self._practice_order = 0


def _next_practice_order(self) -> int:
    self._practice_order += 1
    return self._practice_order
```

When registering a fixed catalog component, make a runtime copy with the next resolved order rather than mutating the frozen catalog object. `dataclasses.replace()` is appropriate:

```python
runtime_spec = replace(spec, order=self._next_practice_order())
```

Dynamic components receive the same next resolved order.

This makes the runtime index order reflect actual build/dependency order while leaving the static catalog coordinate-free and reusable.

### Required invariant

For a built workbook:

```python
orders = [c.order for c in smap.all_ordered()]
assert orders == list(range(1, len(orders) + 1))
```

The fixed catalog's existing conceptual order may remain unchanged for `python -m core list` when no workbook is supplied.

### TDD

Add a regression proving:

- runtime orders are contiguous `1..N`;
- dynamic rows registered before NOPAT appear before `nopat_fy`;
- existing dependency-order validation still passes.

---

## Task 3 — Register every balance-sheet classification row as a dynamic input component

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`
- Test: `core/tests/test_line_identity.py` only if identity-specific coverage belongs there

### Scope

In `ReferenceModelBuilder._build_condensed()`, the balance-sheet classification table is already built dynamically from:

```python
for idx in reform.detail_indices:
    item = self.fin.balance_sheet[idx]
    decision = reform.decisions[idx]
```

Register the classification cell (`column B` of that dynamic row) immediately when it is created.

### Stable component identity

Use the existing canonical line identity. Do not use row numbers.

For example:

```python
ident = line_identity(item)
identity_key = ident.key()
component_id = f"bs_class::{identity_key}"
semantic_key = f"condensed.classification.{identity_key}"
```

The exact prefix may differ, but the following must hold:

- same concept + normalized label => same semantic identity;
- same displayed label + different concepts => distinct component IDs / semantic keys;
- unique conceptless line => stable identity from its normalized label;
- row reordering must not change the component ID or semantic key.

### Dynamic `ComponentSpec`

Create a runtime `ComponentSpec` equivalent to:

```python
ComponentSpec(
    id=component_id,
    order=0,  # replaced by runtime build order
    title=title,
    short_hint=(
        "Classify this balance-sheet line by economic role: operating working "
        "capital, operating long-term, financial, equity, or exclude."
    ),
    semantic_key=semantic_key,
    category="classification",
    answer_kind="input",
    hints=(
        "Use concept metadata and economic role; do not classify from the display label alone.",
        "Distinguish operating assets/liabilities from financing items before choosing the category.",
    ),
)
```

The hints must guide judgment without simply stating the correct category.

For an item with non-empty concept metadata, make the Trainer index title unambiguous, e.g.:

```text
Classify: Deferred income taxes — DeferredIncomeTaxAssetsNet
```

For a conceptless unique line, the display label alone is sufficient.

### Expected answer

Register:

```text
formula = ""
expected_value = decision.category
```

The Answer Key cell already contains `decision.category`; do not create a second answer source.

### Data validation

The existing eight-category Excel dropdown on the classification cell must remain attached in both workbooks.

After generation:

```text
Answer Key classification cell:
    value = correct category
    fill = FFFF00
    Note = non-empty hint
    data validation = eight-category dropdown

Trainer classification cell:
    value = blank
    fill = FFFF00
    Note = none
    data validation = same eight-category dropdown
```

### TDD — dynamic coverage

Add tests proving:

```python
def test_every_bs_detail_row_becomes_input_component(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    classification = [c for c in smap.all_ordered() if c.category == "classification"]

    data = _ingest_demo()
    reform = compute_anchor(data, data.fiscal_years() or data.period_dates()).reformulation
    assert len(classification) == len(reform.detail_indices)
    assert all(c.answer_kind == "input" for c in classification)
    assert all(c.formula == "" for c in classification)
    assert all(c.expected_value in BALANCE_SHEET_CATEGORIES for c in classification)
```

Add a duplicate-label regression using the existing deferred-tax asset/liability fixture:

```text
Deferred income taxes / DeferredIncomeTaxAssetsNet
Deferred income taxes / DeferredIncomeTaxLiabilitiesNet
```

Both must produce separate classification component IDs and semantic keys.

Add an identity-stability regression that constructs the same two rows in reversed source order and proves the **set of component IDs / semantic keys** is unchanged.

---

## Task 4 — Make Trainer / Answer Key generation and Check support input components

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/workbook.py` only if current decoration/blanking assumes formula-only components
- Test: `core/tests/test_trainer.py`

### Workbook generation

`TrainingWorkbookGenerator` already iterates the semantic map to decorate Answer Key cells and blank Trainer cells. Keep that single mechanism; do not special-case classification coordinates outside the semantic map.

Verify that it works for both answer kinds:

```text
formula component -> Answer Key formula; Trainer blank
input component   -> Answer Key literal category/input; Trainer blank
```

Both receive the same yellow practice fill and Answer Key Note contract.

### Check algorithm for input components

Update `check_workbook()` to branch explicitly on `comp.answer_kind`.

For `formula` components, preserve the accepted Step 5 behavior:

1. blank -> yellow;
2. normalized exact formula -> green;
3. otherwise compare cached value to expected value;
4. no matching cache -> red.

For `input` components:

1. blank -> yellow;
2. compare the literal Trainer cell value directly with `comp.expected_value` using `_values_match()`;
3. match -> green;
4. mismatch -> red.

Do **not** require or inspect an Excel formula cache for literal inputs.

Check output remains aggregate-only and non-disclosing.

### TDD — mixed workbook-wide Check

Add a test that selects three classification components:

```text
classification A: enter exact expected category -> green
classification B: enter a different valid category -> red
classification C: leave blank -> yellow
```

Run Check and assert the counts include those states plus all other practice cells.

Then correct B and rerun; it must turn green. Clear A and rerun; it must return to yellow.

Do not expose the expected category in CLI output.

### Hardening regression for the Step 5 OOXML writer

Because classification cells use Excel data validation, add a regression proving a Check pass changes **only the fill state** of a representative practice cell.

Before Check, capture:

```text
font
border
alignment
number_format
protection
data-validation membership / formula1
```

After Check, assert all are unchanged while the fill changes to the expected yellow/green/red state.

For a classification component specifically, assert the eight-category dropdown still exists after one Check and after a second Check.

Do not modify `xlsx_fill_patch.py` unless this test exposes an actual defect.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

---

## Task 5 — Update catalog/listing expectations, docs, and example pair

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify tests that hard-code `13 components` as the **total** runtime component count
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

### Runtime component-count contract

After this step there are still **13 fixed catalog formula components**, but the total runtime component count is:

```text
13 fixed components
+ one dynamic classification component per non-subtotal BS detail row
```

Do not hard-code one demo-specific total in architecture code.

Tests may compute the expected demo count from `reform.detail_indices`.

### CLI listing

`python -m core list` without a workbook may continue listing the 13 fixed catalog templates only.

`python -m core list --workbook <Trainer-or-Answer-Key>` must list the full **runtime** practice sequence, including dynamic classification rows, by resolving the matching Answer Key map where needed.

### Documentation

Update live trainer docs to explain that:

- classification decisions are now actual practice cells;
- the Trainer classification cells retain dropdowns but start blank;
- the Answer Key shows the reference category plus a Note hint;
- Check validates classification inputs with the same yellow/green/red states;
- the fixed formula catalog remains the existing 13 exercises for now;
- later steps will expand the remaining formula/input practice surface.

Do not claim the entire BAV workbook is fully blanked for practice yet.

### Example build

Regenerate the committed demo pair from the current code. Generated Answer-Key sidecars / `rowmap.json` remain ignored and untracked under the existing `.gitignore` rules.

Inspect the generated pair with openpyxl:

- classification Answer Key cells populated/yellow/Notes/dropdowns;
- corresponding Trainer cells blank/yellow/no Notes/dropdowns;
- existing fixed formula practice cells unchanged;
- Trainer remains free of answer-bearing hidden sheets/sidecars.

---

## Task 6 — Full regression and handoff evidence

**Files:**
- Modify: `RESULT.md`

Run at minimum:

```bash
PYTHONPATH=. pytest core/tests/test_semantic_map.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx
```

If `core/tests/test_semantic_map.py` is not created, omit that command and record the exact focused alternative.

### Required artifact audit

After the `/tmp` build verify programmatically:

1. Trainer / Answer Key pair exists.
2. No user-facing `*_reference.xlsx` exists.
3. Trainer has no `_ComponentMap`, `_RefFormulas`, `_RefValues`, `_TrainerMeta`, `.trainer.json`, or Trainer `.component_map.json`.
4. Answer Key retains `_ComponentMap` and can be loaded without its sidecar.
5. All fixed formula components still satisfy the formula contract.
6. Every BS detail classification row has exactly one runtime input component.
7. Same-label/different-concept classification rows remain distinct.
8. Trainer classification cells are blank yellow and retain dropdown validation.
9. Answer Key classification cells contain the expected category, yellow fill, and non-empty Note.
10. Check gives correct yellow/green/red states for formula and input components without modifying values or non-fill formatting.
11. Repeated Check still preserves formula cached values.
12. Generated demo metadata remains ignored/untracked.

### `RESULT.md` format

Overwrite `RESULT.md` with:

```text
Status: Step 6 complete | blocked

Files changed:
- ...

Tests run:
- <exact command> -> <exact result>
...

Semantic component contract:
- formula components: ...
- input components: ...
- runtime order: ...

Dynamic classification practice:
- BS detail rows: <count>
- classification components: <count>
- duplicate-label/concept identity: ...
- Trainer dropdown preservation: ...

Workbook-wide Check:
- formula states: ...
- input states: ...
- non-fill style/DV preservation: ...
- repeated cached-formula Check: ...

Trainer / Answer Key contract:
- leakage audit: ...
- Answer Key formula/input + Notes: ...

Unresolved: ...
```

Do not report `complete` while any runtime component is missing an expected value, any classification row is not separately addressable, or the Trainer contains answer-bearing metadata.

---

## Acceptance criteria

Step 6 is ready for ChatGPT re-review only when all of the following are true:

1. `ComponentSpec` / `ResolvedComponent` explicitly distinguish `formula` and `input` answers.
2. Existing 13 fixed formula components still build and validate unchanged in meaning.
3. Input components can be serialized/deserialized through JSON and embedded `_ComponentMap`.
4. Runtime component orders are contiguous and reflect actual build/dependency order.
5. Every non-subtotal balance-sheet classification row becomes exactly one dynamic input practice component.
6. Dynamic classification identity is based on canonical `LineIdentity`, never worksheet coordinates.
7. Same-label rows with different concepts become separate classification components.
8. Classification component IDs/semantic keys remain stable if source row order changes.
9. Answer Key classification cells contain the correct category + yellow fill + non-empty legacy Note + category dropdown.
10. Trainer classification cells are blank yellow with no Note and retain the same category dropdown.
11. Workbook-wide Check validates input components directly and preserves the existing formula validation behavior.
12. Blank/correct/incorrect classification inputs become yellow/green/red and refresh correctly on recheck.
13. Check preserves values, formulas, cached results, font, border, alignment, number format, protection, and data validation; only practice fill changes.
14. Trainer remains sanitized of answers/hints and Hint/Reveal remain absent.
15. Full core test suite passes and the demo pair builds successfully.
16. Generated Answer-Key metadata remains ignored/untracked.

---

## Do not do in Step 6

- Do not make every forecast/model cell a practice component yet.
- Do not register all ten years / all three scenarios merely because the component model now supports it.
- Do not create a generic exercise authoring language.
- Do not infer dynamic identity from worksheet rows or cell coordinates.
- Do not put reference categories, expected values, formulas, or hints into Trainer metadata.
- Do not reintroduce macros, Hint, or Reveal.
- Do not advance to the next product step in `RESULT.md`.

## Cursor execution rules

1. Read `TARGET.md` and this active step before editing.
2. Write failing tests for the mixed formula/input semantic contract first.
3. Generalize the semantic map minimally; keep existing formula components working before adding dynamic rows.
4. Add runtime ordering before registering classification components.
5. Register classification cells through the semantic map, not ad-hoc workbook blanking.
6. Extend Check by answer kind without weakening non-disclosure or cache preservation.
7. Add the non-fill style/data-validation preservation regression before touching the OOXML writer.
8. Run focused tests after each coherent change, then the full suite.
9. Regenerate and inspect the demo pair.
10. Update `RESULT.md` with exact evidence.
11. Do not commit or push.

## ChatGPT verification protocol

After the user pushes the next checkpoint, ChatGPT should verify:

- the actual branch head and diff, not only `RESULT.md`;
- mixed formula/input map validation and serialization;
- canonical dynamic classification IDs for duplicate-label concept-qualified rows;
- Trainer / Answer Key classification-cell parity and dropdown preservation;
- workbook-wide Check for input and formula components;
- OOXML color patch preserving non-fill formatting/data validation/cached formula values;
- no Trainer leakage or generated-metadata regression;
- full test evidence recorded in `RESULT.md`.

If verified, the next product step should expand the **fixed accounting and DuPont formula practice surface**, then forecast/model inputs and repeated scenario formulas, using this same dynamic/mixed component contract.