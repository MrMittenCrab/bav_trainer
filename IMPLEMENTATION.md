# Step 5 — Enforce Trainer / Answer Key Separation + Workbook-Wide Check

> **For Cursor:** Read `TARGET.md` first. Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Enforce the final product contract: **Trainer = blank yellow practice cells with no answers or hints; Answer Key = corresponding formula/input + one concise legacy Excel Note hint; Check = one workbook-wide validation pass that colors every Trainer practice cell yellow/green/red without disclosing answers.**

**Architecture:** Keep the existing reference-model-first, semantic-map, concept-aware identity, and paired-workbook architecture. The full semantic answer map remains with the Answer Key, not the Trainer. The Trainer is sanitized after derivation. `Check` reads the matching Answer Key externally, scans every semantic practice component in the Trainer, recolors cells based on current content, and never writes or reports reference answers. Remove Hint and Reveal entirely.

**Tech Stack:** Python, pytest, openpyxl, existing BAV Trainer modules.

**Spec:** `TARGET.md` as updated in planning commit `29fe778`.

## Current checkpoint

Base implementation commit: `5c3242f` (`chat identity corrected 4C`) on `chatgpt/reference-model-integrity`.

Step 4's concept-aware identity work is substantially correct. `RESULT.md` reports 68 passing core tests and a successful 13-component Trainer / Answer Key build. Review of that checkpoint found five issues that this step must close:

1. `commonstock` remains an unsafe high-priority concept substring and can force redeemable/common-stock obligations into Equity.
2. The Trainer is currently derived by copying the Answer Key and retains answer-bearing hidden metadata and sidecars even though visible practice cells are blank.
3. Existing Check is per-component and discloses expected values; Hint and Reveal still exist and mutate the Trainer.
4. `python -m core ingest ... -o ...` drops `LineItem.concept`, breaking concept-aware identity on standardized JSON round trips.
5. `example/` still contains stale `*_reference.xlsx` artifacts and does not represent the current two-workbook product.

Do not expand `COMPONENT_CATALOG` until this step is accepted.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Keep the current 13 semantic components and their order.
- Preserve all accepted Step 3 accounting integrity and Step 4 identity behavior.
- Do not redesign forecasting, residual-income mathematics, or scenario logic.
- Do not add automatic HKEX/SEC/edgartools ingestion.
- Do not add quarterly/Core Earnings/Earnings Quality/Price Rationalization/ICC/DCF feature chains.
- Preserve original source/display labels in worksheets.
- Do not introduce fixed workbook coordinates into the static component catalog.
- Do not weaken existing accounting/identity tests.
- The Answer Key is the only hint/answer surface.
- Check must scan all practice cells in one pass and disclose no answer data.
- Hint and Reveal must not remain as compatibility APIs.
- Do not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Remove the remaining unsafe `commonstock` concept shortcut

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Required behavior:** Generic `commonstock` is not sufficiently decisive to force Equity because redeemable or mandatorily redeemable common stock can be liability-like. Remove it as an automatic Equity trigger. Do not replace it with another broad substring heuristic. Ordinary common/share capital must still classify through explicit safe concept signals or existing label rules.

- [ ] **Write the failing regression first**

```python
def test_redeemable_common_stock_concept_does_not_force_equity():
    item = LineItem(
        label="Long-term debt",
        concept="CommonStockSubjectToRedemption",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Liability"
```

- [ ] **Run focused regression and verify intended failure**

```bash
pytest core/tests/test_classification.py -k "common_stock or preferred_stock or debt_security or equity_method or cash_flow_hedge" -v
```

- [ ] **Remove only the unsafe `commonstock` shortcut and rerun the focused tests.**

Retain existing preferred-stock, debt-security, equity-method, cash-flow-hedge, deferred-tax, lease, and borrowing/cash regressions.

---

## Task 2 — Make the Trainer a sanitized workbook, not a hidden Answer Key

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `core/engine/map_embed.py` only if needed for Answer-Key-only metadata
- Modify: `core/trainer/semantic_io.py` only where current Trainer-map assumptions must change
- Test: `core/tests/test_trainer.py`

### Required Answer Key artifact

The Answer Key remains the complete reference workbook:

- each practice cell contains the correct working formula/input;
- each practice cell is `#FFFF00` yellow;
- each practice cell has one non-empty legacy Excel Note with the concise hint;
- `_ComponentMap` and the Answer-Key `.component_map.json` may retain formula, expected value, tolerance, dependencies, and hint metadata because the Answer Key is intentionally the answer surface.

### Required Trainer artifact

The Trainer must contain:

- the same visible model sheets, source data, labels, non-practice calculations, formatting, and practice coordinates;
- every practice cell blank and `#FFFF00` yellow immediately after build;
- no Note/comment on practice cells;
- no adjacent hint cells;
- a visible practice index may list non-answer information such as order, component title, tab, cell, and dependencies.

The Trainer must not contain withheld formulas, expected values, or hints in:

- practice cells;
- adjacent visible cells;
- Notes/comments;
- hidden worksheets;
- embedded component metadata;
- Trainer-associated JSON sidecars.

### Remove obsolete answer stores

`_RefFormulas`, `_RefValues`, and `_TrainerMeta` existed for the old per-cell Check/Hint/Reveal/macro workflow. Remove their generation entirely from both workbooks.

Keep `_ComponentMap` only in the Answer Key. Remove it from the Trainer after the Trainer is derived and practice cells are blanked.

Do not create a differently named hidden answer store.

### Remove Trainer answer sidecars

- Do not copy the Answer Key `.component_map.json` to the Trainer.
- Stop generating `*.trainer.json`.
- Prefer no Trainer semantic sidecar at all; workbook-wide Check will resolve the matching Answer Key by filename and use its semantic map.

### Simplify the visible Trainer index

Keep the visible `Trainer` index sheet if useful, with columns equivalent to:

```text
Order | Component | Tab | Cell | Depends on
```

Instruction text should state:

```text
Complete yellow practice cells in dependency order. Run Check to validate the whole workbook: blank cells stay yellow, correct cells turn green, and incorrect cells turn red. Open the matching Answer Key for the formula/input and Note hint.
```

Remove:

- per-component `Status` tracking if it is no longer needed;
- Hint/Reveal references;
- macro-import instructions;
- `HintActive` / `RevealActive` references;
- progressive-hint language.

### TDD regressions

Update `core/tests/test_trainer.py` so tests locate Trainer practice cells using the **Answer Key semantic map**, not a full semantic map embedded in the Trainer.

Add/strengthen tests:

```python
def test_trainer_has_no_answer_bearing_hidden_sheets(tmp_path):
    trainer_path, answer_key_path = ...
    wb_t = load_workbook(trainer_path, data_only=False)
    assert "_RefFormulas" not in wb_t.sheetnames
    assert "_RefValues" not in wb_t.sheetnames
    assert "_TrainerMeta" not in wb_t.sheetnames
    assert "_ComponentMap" not in wb_t.sheetnames
    wb_t.close()


def test_trainer_has_no_answer_sidecars(tmp_path):
    ...
    assert not trainer_path.with_suffix(".component_map.json").exists()
    assert not trainer_path.with_suffix(".trainer.json").exists()


def test_trainer_and_answer_key_practice_contract(tmp_path):
    trainer_path, answer_key_path = ...
    smap = load_semantic_map(answer_key_path)
    wb_t = load_workbook(trainer_path, data_only=False)
    wb_a = load_workbook(answer_key_path, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        tc = wb_t[comp.tab].cell(row=row, column=col)
        ac = wb_a[comp.tab].cell(row=row, column=col)
        assert tc.value is None
        assert tc.comment is None
        assert _fill_rgb(tc) == "FFFF00"
        assert isinstance(ac.value, str) and ac.value.startswith("=")
        assert ac.value == comp.formula
        assert ac.comment is not None and ac.comment.text.strip()
        assert _fill_rgb(ac) == "FFFF00"
    wb_t.close()
    wb_a.close()
```

Add a leakage scan using the full Answer Key map. Verify every non-empty `short_hint`, detailed hint, and exact practice formula is absent from Trainer answer-bearing locations/metadata. Do not ban legitimate non-practice formulas from the Trainer.

- [ ] **Run:**

```bash
pytest core/tests/test_trainer.py -v
```

---

## Task 3 — Replace per-component Check with one workbook-wide color check; delete Hint/Reveal

**Files:**
- Modify: `core/trainer/checker.py`
- Delete: `core/trainer/hints.py`
- Modify: `core/trainer/__init__.py`
- Modify: `core/__main__.py`
- Delete: `core/templates/TrainerMacros.bas`
- Modify: `core/trainer/workbook.py` for shared fill/instruction cleanup as needed
- Test: `core/tests/test_trainer.py`

### Public Check contract

The public action is:

```bash
python -m core check --workbook path/to/Company_Trainer.xlsx
```

There is **no `--component` argument**. One invocation checks every semantic practice component in the workbook.

Define a non-disclosing summary result, for example:

```python
@dataclass(frozen=True)
class CheckSummary:
    total: int
    correct: int
    incorrect: int
    blank: int
```

`CheckSummary` must not contain formulas, expected values, hints, or per-cell answer data.

### Exact color states

Use these fill colors consistently:

```text
blank / unentered = FFFF00  (yellow)
correct           = C8E6C9  (green)
incorrect         = FFC7CE  (red)
```

A Check pass must overwrite the previous practice-cell validation fill based on **current** cell contents. Therefore:

- wrong → corrected → rerun Check → green;
- correct → cleared → rerun Check → yellow;
- blank → entered wrong → rerun Check → red.

Do not change the cell's value/formula, Note/comment, number format, border, font, or alignment.

### Reference source

`check_workbook(trainer_path)` must:

1. infer the matching `*_Answer_Key.xlsx` using `answer_key_path_for(trainer_path)`;
2. fail clearly if that Answer Key is missing;
3. load the full semantic component map from the Answer Key;
4. use that map to locate all practice cells in the Trainer;
5. never require answer-bearing metadata inside the Trainer.

### Validation algorithm

Use deterministic validation compatible with the current Excel/openpyxl workflow:

For every component:

1. Read the Trainer cell with `data_only=False` to inspect whether it is blank and to preserve/write the workbook.
2. If the cell is `None` or an empty string after trimming, mark yellow and count blank.
3. If the Trainer formula, normalized by the existing formula-normalization rules, exactly matches the Answer Key formula, mark green and count correct. This allows correct formulas to validate even when no cached calculation value exists.
4. Otherwise read the same Trainer cell from a second `data_only=True` workbook instance. If a cached value exists, compare it with the Answer Key `expected_value` using the component tolerance:
   - numeric: existing absolute-or-relative tolerance semantics;
   - text: normalized case-insensitive equality.
5. If the cached value matches, mark green; otherwise mark red.
6. If the cell is nonblank, formula differs from the reference formula, and no usable cached value exists, mark red rather than guessing it is correct.

Save only the color changes back to the Trainer workbook.

### Non-disclosure

CLI output may be only aggregate information equivalent to:

```text
Checked 13 practice cells: 7 correct, 3 incorrect, 3 blank.
```

Do not print or return:

- expected formulas;
- expected values;
- hints;
- answer explanations;
- per-component reference data.

Do not insert an answer into the Trainer.

### Delete Hint and Reveal

Remove entirely:

- `HintResult`;
- `show_hint()`;
- `reveal_answer()`;
- CLI `hint`;
- CLI `reveal`;
- Hint/Reveal exports from `core.trainer`;
- Hint/Reveal macros/instructions;
- reveal-status syncing and reveal-specific fills.

Delete `TrainerMacros.bas`; do not retain a macro bundle solely for the old feedback architecture. Check remains a Python/CLI workbook action for this step.

### TDD regressions

Add tests equivalent to the following.

```python
def test_check_scans_all_practice_cells_and_colors_three_states(tmp_path):
    trainer_path, answer_key_path = ...
    smap = load_semantic_map(answer_key_path)
    comps = smap.all_ordered()

    wb = load_workbook(trainer_path, data_only=False)
    # one exact-correct formula
    c0 = comps[0]
    r, c = parse_cell_ref(c0.cell)
    wb[c0.tab].cell(r, c).value = c0.formula

    # one deliberately wrong entry
    c1 = comps[1]
    r, c = parse_cell_ref(c1.cell)
    wb[c1.tab].cell(r, c).value = "=1+1"

    # every remaining practice cell stays blank
    wb.save(trainer_path)
    wb.close()

    summary = check_workbook(trainer_path)
    assert summary.total == len(comps)
    assert summary.correct == 1
    assert summary.incorrect == 1
    assert summary.blank == len(comps) - 2

    wb = load_workbook(trainer_path, data_only=False)
    r, c = parse_cell_ref(c0.cell)
    assert _fill_rgb(wb[c0.tab].cell(r, c)) == "C8E6C9"
    r, c = parse_cell_ref(c1.cell)
    assert _fill_rgb(wb[c1.tab].cell(r, c)) == "FFC7CE"
    for comp in comps[2:]:
        r, c = parse_cell_ref(comp.cell)
        assert _fill_rgb(wb[comp.tab].cell(r, c)) == "FFFF00"
    wb.close()
```

```python
def test_recheck_refreshes_colors_from_current_contents(tmp_path):
    ...
    # wrong -> red
    # replace with exact reference formula -> rerun -> green
    # clear cell -> rerun -> yellow
```

```python
def test_check_does_not_change_practice_contents_or_add_notes(tmp_path):
    ...
    before_values = ...
    check_workbook(trainer_path)
    after_values = ...
    assert after_values == before_values
    assert all(practice_cell.comment is None for ...)
```

```python
def test_check_requires_matching_answer_key(tmp_path):
    ...
    answer_key_path.unlink()
    with pytest.raises(FileNotFoundError, match="Answer Key"):
        check_workbook(trainer_path)
```

```python
def test_cli_check_is_workbook_wide_and_hint_reveal_are_removed(...):
    # `check --workbook ...` succeeds with no component argument.
    # parser/help exposes check but not hint or reveal.
```

Add a CLI-output regression that ensures none of the Answer Key formulas, expected values, or hint strings appear in Check output.

- [ ] **Run:**

```bash
pytest core/tests/test_trainer.py -v
python -m core --help
```

The public CLI must contain `check` and must not contain `hint` or `reveal`.

---

## Task 4 — Preserve `LineItem.concept` in standardized JSON export/reload

**Files:**
- Modify: `core/__main__.py`
- Test: `core/tests/test_line_identity.py` or a focused ingestion test module if cleaner

### Problem

The current `cmd_ingest(... -o ...)` serializer writes statement rows with `label` and `values` but omits `concept`. An Excel workbook can therefore ingest concept-aware rows correctly and then lose their identity metadata when exported to standardized JSON.

### Required behavior

Every exported statement row must include:

```json
{
  "label": "Deferred income taxes",
  "concept": "DeferredIncomeTaxAssetsNet",
  "values": {...}
}
```

Use `"concept": ""` for conceptless rows so the standardized schema is explicit and stable. Do not change the current date/value representation in this task.

### TDD regression

Create a temporary Excel source using:

```text
Concept | Line Item | 2024-12-31 | 2025-12-31
```

Run the CLI ingest path to JSON, reload that JSON through `HKManualDocumentAdapter`, and assert that both deferred-tax concepts survive exactly and remain separately identifiable.

- [ ] **Run:**

```bash
pytest core/tests/test_line_identity.py -v
```

---

## Task 5 — Align docs and committed examples with the final contract

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify other live trainer documentation only where repository search finds stale Check/Hint/Reveal behavior
- Delete: `example/DEMO_HK_Trainer_reference.xlsx`
- Delete: `example/DEMO_HK_Trainer_reference.assumptions.json`
- Delete: `example/DEMO_HK_Trainer.trainer.json`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Add/regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Delete `example/rowmap.json` if it is merely generated demo metadata and no runtime/test consumer requires the committed copy

### Documentation contract

All live trainer documentation must state the same loop:

```text
Trainer = blank yellow practice cells, no answers, no hints.
Check = scans every practice cell; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = same practice cells with formula/input + one legacy Note hint.
```

Document the Check command as workbook-wide:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

Do not document a component selector for Check.

Remove all instructions to:

- run `python -m core hint`;
- run `python -m core reveal`;
- import `TrainerMacros.bas`;
- use `HintActive` or `RevealActive`;
- expect progressive hints or reveal states.

Do not describe removed Hint/Reveal behavior as optional legacy functionality.

Run a local repository search:

```bash
rg -n "HintActive|RevealActive|show_hint|reveal_answer|TrainerMacros|python -m core hint|python -m core reveal|--component" \
  core README-HK-TRAINER.md skills/bav-trainer
```

Review every remaining match. `--component` may legitimately remain for unrelated commands only if such a command still exists and is useful; it must not remain on public Check.

### Example contract

The committed example must contain the current matched pair:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

It must not contain `*_reference.xlsx` or `*_Trainer.trainer.json`.

Commit the example Trainer in its fresh **unchecked** state: all practice cells yellow/blank. Do not commit a demo Trainer that has been colored by a Check run.

Inspect both generated workbooks with openpyxl before handoff; do not infer correctness from filenames alone.

---

## Task 6 — Full leakage audit, Check audit, regression suite, and handoff evidence

**Files:**
- Modify: `RESULT.md`

### Required verification commands

Run at minimum:

```bash
pytest core/tests/test_classification.py -v
pytest core/tests/test_line_identity.py -v
pytest core/tests/test_reference_integrity.py -v
pytest core/tests/test_line_resolver.py -v
pytest core/tests/test_trainer.py -v
pytest core/tests/ -q
python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
python -m core --help
```

The initial demo Check on a freshly built Trainer should report all practice cells blank and must leave all of them yellow.

### Generated-artifact audit

Verify explicitly:

1. exactly two `.xlsx` outputs are produced for the `/tmp` demo pair;
2. no `*_reference.xlsx` is produced;
3. no Trainer `.trainer.json` or `.component_map.json` is produced;
4. Trainer has no `_ComponentMap`, `_RefFormulas`, `_RefValues`, or `_TrainerMeta`;
5. every Trainer practice cell starts blank yellow with no comment;
6. every Answer Key practice cell contains its working formula/input, stays yellow, and has a non-empty legacy Note;
7. Answer Key remains the only location containing semantic answer/hint metadata;
8. one mixed-state Check regression produces green/red/yellow exactly as specified across all practice cells;
9. Check does not modify practice-cell contents;
10. Check output contains no expected formula, expected value, or hint text;
11. public CLI contains `check` but no `hint` or `reveal`;
12. exported standardized JSON preserves `LineItem.concept` through reload;
13. existing 13 semantic components remain unchanged.

Do not report success based only on the test count; record the explicit artifact and Check observations in `RESULT.md`.

### RESULT.md handoff format

```text
Status: Step 5 complete | blocked

Files changed:
- ...

Tests run:
- <exact command> -> <exact result>
...

Trainer / Answer Key contract:
- Trainer practice cells: ...
- Trainer answer-bearing hidden sheets/sidecars: ...
- Answer Key formulas + Notes: ...

Workbook-wide Check:
- fresh blank workbook: ...
- mixed correct/incorrect/blank color test: ...
- recheck refresh behavior: ...
- content preservation: ...
- answer/hint disclosure scan: ...

Removed surfaces:
- Hint API/CLI: ...
- Reveal API/CLI: ...
- Trainer macros: ...

Identity round trip:
- concept preservation: ...

Examples:
- Trainer: ...
- Answer Key: ...
- stale reference artifacts: ...

Unresolved: ...
```

---

## Acceptance criteria

Step 5 is ready for ChatGPT review only when all of the following are true:

1. Generic `commonstock` no longer forces redeemable common stock into Equity.
2. Trainer practice cells are blank/yellow/no-Note immediately after build.
3. Trainer contains no hidden/sidecar copy of practice formulas, expected values, or hints.
4. Answer Key practice cells contain the correct formula/input and one non-empty legacy Note hint in the same yellow cell.
5. `Check` scans **every** practice cell with one workbook-level action; it has no component selector.
6. Blank practice cells are yellow, correct cells green (`C8E6C9`), incorrect cells red (`FFC7CE`).
7. Re-running Check recomputes every practice cell from current contents and refreshes colors accordingly.
8. Check never changes learner-entered contents or inserts comments/answers.
9. Check output/result contains no expected formula, expected value, or hint.
10. Check obtains reference semantics from the matching Answer Key, not from answer-bearing Trainer metadata.
11. Hint and Reveal Python/CLI/macro surfaces are removed.
12. `LineItem.concept` survives standardized JSON export/reload.
13. Committed demo represents `*_Trainer.xlsx` + `*_Answer_Key.xlsx` only, with no stale `*_reference.xlsx`.
14. Existing Step 3 accounting integrity and Step 4 identity tests remain passing.
15. Existing 13 semantic components remain unchanged.
16. Full core test suite passes and the demo pair builds successfully.

## Cursor execution rules

1. Read `TARGET.md` and this file before editing.
2. Do not expand the practice catalog.
3. Write the focused failing regression before each behavior change.
4. Keep Answer Key metadata complete; sanitize only the Trainer artifact.
5. Implement one workbook-wide Check, not a loop exposed as per-cell user actions.
6. Never put expected values/formulas/hints back into Trainer metadata to make Check easier.
7. Remove Hint/Reveal rather than hiding them.
8. Run focused tests after each coherent change, then the full suite.
9. Update `RESULT.md` with exact commands and artifact evidence.
10. Do not propose the next product step.
11. Do not commit or push; the user owns the checkpoint commit.

## ChatGPT verification protocol

After the user pushes the implementation checkpoint, verify by code inspection:

- every acceptance criterion above;
- that Check truly iterates the full Answer Key semantic map and colors all Trainer practice cells;
- that the three-state color semantics are exactly yellow/green/red and refresh on rerun;
- that Check cannot disclose or insert answers/hints;
- that Trainer answer-bearing hidden sheets/sidecars are absent;
- that Answer Key formula + Note behavior remains correct;
- that Hint/Reveal surfaces are actually gone;
- that concept identity still survives ingestion/export;
- the exact evidence recorded in `RESULT.md`.

Do not move to practice-surface expansion until this checkpoint is accepted.
