# Step 5 correction pass — generated metadata hygiene + cache-safe workbook-wide Check

> **For Cursor:** Read `TARGET.md` first. Step 5 is implemented in commit `9a8a706` (`chat 5 new design`) but is **not accepted yet**. Implement only the correction pass below using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Preserve the accepted Step 5 product behavior while fixing two remaining implementation defects: generated Answer-Key metadata should not dirty the committed demo, and workbook-wide Check must not destroy Excel formula cached results when it recolors cells.

**Architecture:** Keep the current sanitized Trainer / full Answer Key / workbook-wide Check architecture. The Answer Key remains the source of semantic answers and hints. Runtime Answer-Key sidecars may still be generated when building a pair, but demo-side generated metadata is not a committed product artifact. Check must continue to validate exact formulas or equivalent cached results, but its color-only write must operate at the XLSX package/style level so formula text and cached `<v>` results survive unchanged.

**Tech Stack:** Python, pytest, openpyxl for workbook reads, Python `zipfile` + XML parsing for cache-preserving XLSX fill updates.

**Spec:** `TARGET.md` at the current branch head. Do not change `TARGET.md` in this correction pass.

## Current checkpoint

Base implementation commit: `9a8a7065a2789beff8fe4c7ddb14ad46c3a1d93d` (`chat 5 new design`) on `chatgpt/reference-model-integrity`.

The implementation already has the intended Step 5 product loop:

```text
Trainer = blank yellow practice cells, no answers or hints.
Check = scans all practice cells; blank yellow, correct green, incorrect red.
Answer Key = formula/input + one legacy Excel Note hint.
```

`RESULT.md` reports 80 passing core tests, a successful 13-component pair build, workbook-wide Check, no Trainer answer-bearing metadata, and no Hint/Reveal surface.

### Review finding 1 — committed generated metadata dirties the demo

The latest checkpoint committed generated files:

```text
example/DEMO_HK_Answer_Key.component_map.json
example/DEMO_HK_Answer_Key.assumptions.json
```

`ReferenceModelBuilder` also generates `rowmap.json` beside a build. These are implementation/build metadata rather than the two user-facing workbook examples. Rebuilding the demo should not repeatedly modify or recreate tracked generated metadata.

ChatGPT has already added narrow `.gitignore` rules for only these generated demo/build artifacts:

```gitignore
# Generated BAV trainer demo/build metadata
example/rowmap.json
example/*_Answer_Key.component_map.json
example/*_Answer_Key.assumptions.json
example/*_Trainer.component_map.json
example/*_Trainer.trainer.json
```

Do not broaden those rules to ignore arbitrary assumptions files or arbitrary JSON elsewhere in the repository.

### Review finding 2 — Check can destroy cached results needed for repeated equivalent-formula validation

`core/trainer/checker.py::check_workbook()` correctly accepts either:

1. an exact normalized formula match; or
2. a different formula whose cached Excel result matches the Answer Key expected value within tolerance.

However, it currently recolors cells and then saves the Trainer through openpyxl. An openpyxl rewrite does not reliably preserve formula cached results. Therefore an equivalent non-identical formula can pass by cached value on the first Check, lose its cached result during the color save, and become red on the next Check unless Excel recalculates and saves again.

This violates the `TARGET.md` requirement that re-running Check recompute states from the current workbook without changing learner cell contents. The Check operation itself must not make a previously valid workbook less checkable.

Do not solve this by narrowing correctness to exact-formula equality. Equivalent formulas with valid cached results must continue to be accepted.

---

## Global constraints

- `TARGET.md` is read-only.
- Keep the current 13 semantic components and their order.
- Preserve all accepted Step 3 accounting-integrity and Step 4 identity behavior.
- Preserve the Step 5 Trainer / Answer Key separation and leakage protections.
- Preserve workbook-wide Check: all cells in one pass, yellow/green/red, non-disclosing.
- Preserve Hint/Reveal removal.
- Do not add macros.
- Do not move answer-bearing metadata back into the Trainer.
- Do not change forecasting, residual-income, or scenario mathematics.
- Do not introduce fixed workbook coordinates into `COMPONENT_CATALOG`.
- Do not weaken existing tests.
- Do not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Stop committing generated Answer-Key metadata and make tests independent of it

**Files:**
- Delete from the committed example: `example/DEMO_HK_Answer_Key.component_map.json`
- Delete from the committed example: `example/DEMO_HK_Answer_Key.assumptions.json`
- Modify: `core/tests/test_reference_integrity.py`
- Keep: `example/DEMO_HK_Trainer.xlsx`
- Keep: `example/DEMO_HK_Answer_Key.xlsx`
- `.gitignore` has already been updated by ChatGPT; modify it only if a failing test demonstrates the narrow rules are wrong.

### Required behavior

The committed example product is the workbook pair:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

Generated Answer-Key `.component_map.json`, `.assumptions.json`, and `rowmap.json` may still be produced at runtime because the builder currently uses them internally. They should simply remain generated/ignored files rather than committed demo artifacts.

Do **not** remove the embedded `_ComponentMap` from the Answer Key. Check and `load_semantic_map()` can use the embedded map when the sidecar is absent.

Do **not** redesign `ReferenceModelBuilder` merely to stop it generating sidecars in arbitrary user output directories; this correction is about repository/demo hygiene, not changing the runtime build contract.

### Fix the assumptions-dependent test

`core/tests/test_reference_integrity.py::test_cli_assumptions_propagate` currently reads the committed demo assumptions sidecar. Make the test self-contained instead.

Use this pattern:

```python
# Build a temporary default pair first.
_, default_answer = build_training_workbook(
    data,
    tmp_path / "Default_Trainer.xlsx",
)

# The builder generated the assumptions next to the temporary Answer Key.
default_assumptions_path = default_answer.with_suffix(".assumptions.json")
assumptions = json.loads(default_assumptions_path.read_text(encoding="utf-8"))

# Modify only the values the test intends to exercise.
assumptions["marketData"]["dilutedShares"] = 2500.0
assumptions["scenarios"]["Base"]["growthVector"] = [0.25] + [0.10] * 9
```

Then write that modified object to `tmp_path / "custom.assumptions.json"` and keep the existing CLI propagation assertions.

The test must not depend on any committed `example/*_Answer_Key.assumptions.json` file.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
```

Then inspect:

```bash
git status --short
```

After a demo rebuild, generated sidecars may exist locally but must be ignored rather than shown as untracked changes.

---

## Task 2 — Make Check color writes preserve formula cached results

**Files:**
- Modify: `core/trainer/checker.py`
- Create: `core/trainer/xlsx_fill_patch.py` (preferred focused helper; use an equivalently focused name only if clearly better)
- Test: `core/tests/test_trainer.py`

### Required behavior

Keep the current validation decision logic in `check_workbook()`:

```text
blank                         -> yellow
exact normalized formula      -> green
non-identical formula with cached expected result -> green
otherwise                     -> red
```

Change only how the resulting fills are written.

`check_workbook()` must **not** save the Trainer through openpyxl after determining the states. Read with openpyxl, close both workbook instances, then apply the desired fill changes directly to the XLSX OOXML package.

The color writer must preserve, byte-for-byte where practical and semantically in all cases:

- formula `<f>` contents;
- formula cached `<v>` contents;
- user-entered constants;
- comments/Notes;
- number formats;
- fonts;
- borders;
- alignment;
- protection;
- worksheet structure.

Only practice-cell style references and the minimum required style-table entries may change.

### Focused OOXML fill-patch interface

Provide a small helper equivalent to:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CellFillUpdate:
    sheet: str
    cell: str
    rgb: str


def apply_fill_updates(
    workbook_path: Path,
    updates: list[CellFillUpdate],
) -> None:
    ...
```

`check_workbook()` should collect one update for every practice component and call this helper exactly once after closing its read-only/openpyxl workbook handles.

### OOXML implementation rules

Use Python's standard library (`zipfile`, XML parsing) rather than introducing a new workbook dependency.

1. Open the XLSX as a ZIP package.
2. Resolve worksheet names to worksheet XML paths from `xl/workbook.xml` and `xl/_rels/workbook.xml.rels`; do not assume `sheet1.xml` ordering from workbook sheet order.
3. Parse `xl/styles.xml`.
4. Ensure solid fills exist for exactly these RGB values:

```text
FFFF00
C8E6C9
FFC7CE
```

Excel styles may encode RGB as ARGB (for example `00FFFF00` or `FFFFFF00`). Normalize consistently when detecting/reusing an existing fill.

5. For each `(original cell style index, target RGB)` pair, clone/reuse a `cellXfs/xf` style that changes only `fillId`/`applyFill` while preserving the original font, border, number format, alignment, protection and other style attributes/elements.
6. In each target worksheet XML, find the `<c r="A1">` node for the requested address and update only its `s` style index.
7. Do not alter the cell's `<f>`, `<v>`, type, or value nodes.
8. Write a replacement XLSX package to a temporary path in the same directory and atomically replace the original only after the full ZIP is written successfully.
9. Preserve all unrelated ZIP members unchanged.

If a practice cell has no explicit style index, treat its original style as index `0` and create/reuse the target clone from that style.

If a target sheet or cell cannot be resolved, raise a clear error and do not leave a partially rewritten workbook.

### Update `check_workbook()`

Refactor the current end of `check_workbook()` from the conceptual pattern:

```python
cell.fill = ...
...
wb.save(trainer_path)
```

to:

```python
updates: list[CellFillUpdate] = []
...
updates.append(CellFillUpdate(comp.tab, comp.cell, target_rgb))
...
wb.close()
wb_cached.close()
apply_fill_updates(trainer_path, updates)
```

Do not write answers, expected values, formulas, or hints into the Trainer.

---

## Task 3 — Add the repeated equivalent-formula cached-result regression

**Files:**
- Modify: `core/tests/test_trainer.py`

### Why the existing tests are insufficient

The current correct-formula tests enter `comp.formula` exactly. Exact reference formulas remain green without needing a cached value, so those tests cannot detect cache loss.

Add a regression using a formula that is **not** equal to `comp.formula` but has a valid cached result equal to `comp.expected_value`.

### Test fixture strategy

Do not depend on Excel automation being installed in CI.

Create a focused test helper that patches one Trainer practice cell directly in the XLSX worksheet XML before Check:

- choose a component whose `expected_value` is numeric;
- set the cell formula `<f>` to a different but valid formula such as the numeric constant expression for the expected result (for example `=123.45`, stored in OOXML `<f>` as `123.45`);
- set its cached `<v>` to the same expected numeric value;
- preserve the existing cell style/address.

This creates a deterministic workbook that openpyxl reads as:

```text
data_only=False -> a formula different from comp.formula
data_only=True  -> comp.expected_value
```

### Required regression

Add a test equivalent in behavior to:

```python
def test_equivalent_cached_formula_stays_correct_across_repeated_checks(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    smap = load_semantic_map(answer_key_path)
    comp = next(
        c for c in smap.all_ordered()
        if isinstance(c.expected_value, (int, float))
    )

    _inject_formula_and_cached_value(
        trainer_path,
        comp.tab,
        comp.cell,
        formula=f"={float(comp.expected_value)}",
        cached_value=float(comp.expected_value),
    )

    # Confirm this is testing the cached-value path, not exact formula equality.
    wb_formula = load_workbook(trainer_path, data_only=False)
    row, col = parse_cell_ref(comp.cell)
    entered_formula = wb_formula[comp.tab].cell(row, col).value
    wb_formula.close()
    assert entered_formula != comp.formula

    first = check_workbook(trainer_path)
    assert first.correct >= 1

    # Check itself must not destroy the cached Excel result.
    wb_cached = load_workbook(trainer_path, data_only=True)
    cached_after_first_check = wb_cached[comp.tab].cell(row, col).value
    wb_cached.close()
    assert cached_after_first_check == pytest.approx(float(comp.expected_value))

    second = check_workbook(trainer_path)
    assert second.correct >= 1

    wb = load_workbook(trainer_path, data_only=False)
    assert _fill_rgb(wb[comp.tab].cell(row, col)) == "C8E6C9"
    assert wb[comp.tab].cell(row, col).value == entered_formula
    wb.close()
```

The test must fail against commit `9a8a706` for the intended reason before implementing the OOXML fill patch.

### Preserve existing Check regressions

All existing Step 5 Check tests must remain:

- all practice cells scanned in one pass;
- blank yellow / correct green / incorrect red;
- wrong -> corrected -> green;
- cleared -> yellow;
- Check changes no practice contents or Notes;
- missing Answer Key fails clearly;
- CLI output discloses no formula/value/hint;
- no Hint/Reveal CLI.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

---

## Task 4 — Full regression and repository-hygiene handoff

**Files:**
- Modify: `RESULT.md`

Run at minimum:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core --help
```

Then explicitly verify repository/demo hygiene:

```bash
git status --short
```

The working tree may show the intentional source/test/example-workbook changes for this correction pass, but regenerating demo metadata must not leave new untracked `example/*_Answer_Key.component_map.json`, `example/*_Answer_Key.assumptions.json`, `example/*_Trainer.component_map.json`, `example/*_Trainer.trainer.json`, or `example/rowmap.json` entries.

### RESULT.md handoff

Overwrite `RESULT.md` with:

```text
Status: Step 5 correction pass complete | blocked

Files changed:
- ...

Tests run:
- <exact command> -> <exact result>
...

Generated-metadata hygiene:
- committed Answer-Key sidecars removed: ...
- demo rebuild ignored sidecars cleanly: ...

Check cache preservation:
- equivalent non-reference formula + valid cached result first Check: ...
- cached value after first Check: ...
- second Check without Excel recalculation: ...
- learner formula unchanged: ...

Preserved Step 5 contract:
- Trainer leakage audit: ...
- Answer Key formula + Note contract: ...
- workbook-wide yellow/green/red Check: ...
- Hint/Reveal absent: ...

Unresolved: ...
```

Do not report `complete` if the repeated cached-result regression fails or if demo rebuilds still dirty the repository with generated metadata.

---

## Acceptance criteria

This correction pass is ready for ChatGPT re-review only when all are true:

1. `example/DEMO_HK_Answer_Key.component_map.json` is no longer a committed demo artifact.
2. `example/DEMO_HK_Answer_Key.assumptions.json` is no longer a committed demo artifact.
3. The assumptions propagation test is self-contained and uses a temporary generated assumptions file.
4. The narrow `.gitignore` rules prevent generated demo metadata from reappearing as untracked changes.
5. Exact Answer Key formulas still validate green.
6. An equivalent non-identical formula with a valid cached expected result validates green.
7. Check preserves that cached result while recoloring the workbook.
8. The same equivalent formula remains green on a second Check without an intervening Excel recalculation/save.
9. Check still changes only practice-cell fill state and does not alter learner contents, Notes, formulas, expected values, or hints.
10. Blank/correct/incorrect colors remain `FFFF00` / `C8E6C9` / `FFC7CE`.
11. Trainer remains free of answer-bearing hidden sheets/sidecars.
12. Answer Key still contains working formulas plus one legacy Note hint per yellow practice cell.
13. Hint and Reveal remain removed.
14. Full core suite passes and the demo pair still builds.

## Cursor execution rules

1. Pull/read the current `TARGET.md`, `IMPLEMENTATION.md`, and `.gitignore` before editing.
2. Do not redo accepted Step 5 work.
3. Write the repeated cached-result regression before changing Check's write path and confirm it fails for the intended reason.
4. Keep validation semantics unchanged; fix the XLSX color-write mechanism rather than redefining correctness.
5. Keep the OOXML writer narrowly focused on practice-cell fills.
6. Delete the two tracked generated Answer-Key JSON demo files after the test no longer depends on them.
7. Run focused tests after each coherent change, then the full suite.
8. Update `RESULT.md` with exact evidence.
9. Do not propose Step 6.
10. Do not commit or push; the user owns the checkpoint commit.

## ChatGPT verification protocol

After the user pushes the next checkpoint, verify:

- the generated sidecars are no longer tracked and the `.gitignore` is narrow;
- no reference-integrity test depends on committed generated assumptions metadata;
- Check no longer saves the workbook through openpyxl merely to recolor cells;
- the OOXML fill writer touches styles/cell style references without removing formula cached `<v>` values;
- the new non-identical-formula repeated-Check regression is meaningful rather than accidentally exercising exact formula equality;
- all existing Step 5 leakage, color-state, and non-disclosure behavior remains intact;
- the exact test evidence in `RESULT.md`.

Do not advance to practice-surface expansion until this correction pass is accepted.
