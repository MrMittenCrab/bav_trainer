# Step 5 — Enforce Trainer / Answer Key Separation

> **For Cursor:** Read `TARGET.md` first. Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Make the built artifacts obey the strict product contract: **Trainer = blank yellow practice cells with no hints or answers anywhere; Answer Key = the corresponding formula/input plus one concise legacy Excel Note hint in the same yellow cell.** Close the remaining classification and standardized-export defects found during review before expanding the practice surface.

**Architecture:** Keep the existing reference-model-first, semantic-map, concept-aware identity, and paired-workbook architecture. The Answer Key remains the complete reference model and may carry full semantic answer metadata. The Trainer receives only the visible model structure plus locator/status metadata needed for navigation/checking; answer formulas, expected values, and hint text must be stripped from all Trainer workbook metadata and Trainer-associated sidecars. Remove the legacy Hint/Reveal product surfaces instead of preserving two competing feedback systems.

**Tech Stack:** Python, pytest, openpyxl, existing BAV Trainer modules.

**Spec:** `TARGET.md` as updated in planning commit `f88f94f`.

## Current checkpoint

Base implementation commit: `5c3242f` (`chat identity corrected 4C`) on `chatgpt/reference-model-integrity`.

Step 4's concept-aware identity work is substantially correct. `RESULT.md` reports 68 passing core tests and a successful 13-component Trainer / Answer Key build. Review of that checkpoint found five concrete issues to resolve now:

1. `commonstock` remains an unsafe high-priority concept substring and can force redeemable/common-stock obligations into Equity.
2. The Trainer is copied from the Answer Key with answer-bearing hidden metadata: `_RefFormulas`, `_RefValues`, `_TrainerMeta`, full `_ComponentMap`, and full semantic sidecars can expose formulas, expected values, and hints even though the visible yellow cell is blank.
3. Python/VBA Hint and Reveal still write hints or answers into the Trainer and are still advertised in UI/docs, directly contradicting `TARGET.md`.
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
- Do not weaken tests to make this step pass.
- Do not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Remove the remaining unsafe `commonstock` concept shortcut

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

### Required behavior

Concept metadata remains a high-priority signal only when the concept itself clearly determines economic side/category. Generic `commonstock` is not sufficiently decisive because redeemable or mandatorily redeemable stock can be liability-like.

Remove `commonstock` as a generic automatic Equity trigger. Do not replace it with another broad substring heuristic. Ordinary common/share capital must still classify through explicit safe concept signals or existing label rules.

### TDD regression

Add first:

```python
def test_redeemable_common_stock_concept_does_not_force_equity():
    item = LineItem(
        label="Long-term debt",
        concept="CommonStockSubjectToRedemption",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Liability"
```

Also retain the existing preferred-stock, debt-security, equity-method, cash-flow-hedge, and deferred-tax concept regressions.

### Verify

```bash
pytest core/tests/test_classification.py -k "common_stock or preferred_stock or debt_security or equity_method or cash_flow_hedge" -v
```

The new common-stock regression must fail for the intended reason before the implementation change and pass afterward.

---

## Task 2 — Make the Trainer artifact non-answer-bearing

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `core/engine/semantic_map.py` only if a focused locator-only copy helper is cleaner
- Modify: `core/engine/map_embed.py` only as needed to embed the sanitized Trainer map
- Modify: `core/trainer/semantic_io.py` only if needed to keep locator loading clean
- Test: `core/tests/test_trainer.py`

### Required artifact contract

#### Answer Key

The Answer Key remains the complete reference workbook:

- every practice cell contains its working formula/input;
- every practice cell is bright yellow;
- every practice cell has a non-empty legacy Excel Note with the concise hint;
- its embedded `_ComponentMap` and Answer-Key sidecar may contain full formulas, expected values, and hint metadata.

#### Trainer

The Trainer must contain:

- the same visible workbook structure and formatting;
- blank bright-yellow practice cells;
- no Note/comment on practice cells;
- semantic locator information sufficient to identify component ID/order/title/category/tab/cell/dependencies as needed.

The Trainer must **not** contain withheld answers or hints in any of these places:

- practice cells;
- adjacent visible cells;
- cell Notes/comments;
- hidden worksheets;
- embedded semantic metadata;
- Trainer-associated JSON sidecars.

### Remove obsolete hidden answer stores

The current `_RefFormulas`, `_RefValues`, and `_TrainerMeta` sheets exist to support the old Hint/Reveal/macro system. They are redundant once the Answer Key is the answer/hint surface.

Remove their generation entirely unless a failing test proves one is still required for a non-disclosing feature. Do not keep hidden answer copies merely for backwards compatibility.

### Define one sanitized Trainer semantic map

Add one focused transformation, for example:

```python
def trainer_locator_map(full_map: SemanticMap) -> SemanticMap:
    ...
```

or an equivalent method on `SemanticMap`.

For each Trainer component preserve only non-answer fields required for navigation/runtime identity, such as:

```text
id
order
title
semantic_key
category
tab
cell
depends_on
related_cells
status
```

Strip or blank all answer/hint fields:

```text
short_hint = ""
formula = ""
expected_value = None
hints = []
```

Use this same sanitized map for both:

1. the Trainer's embedded `_ComponentMap`; and
2. the Trainer's `.component_map.json` sidecar, if that sidecar continues to be emitted.

Do not copy the full Answer-Key component-map sidecar to the Trainer and then rely on workbook visibility to hide it.

### Remove the obsolete `.trainer.json`

`TrainingWorkbookGenerator.generate()` currently writes `*.trainer.json` containing the full resolved component dictionaries, including answer/hint fields. This is not used by `load_semantic_map()` and violates the strict Trainer contract.

Stop generating `*.trainer.json`. Add a regression asserting that a normal build does not create it.

### Trainer index copy

Keep the visible `Trainer`/practice-index sheet if useful, but change its instructions so they describe only the intended workflow:

```text
Complete yellow practice cells in dependency order. Open the matching Answer Key to inspect the formula/input and hover over its Note for the hint. Optional Check reports only whether your entry is correct.
```

The sheet must contain no `Hint`, `Reveal`, `HintActive`, `RevealActive`, macro-import, or progressive-hint instructions.

### TDD regressions

Extend `core/tests/test_trainer.py` with focused assertions equivalent to:

```python
def test_trainer_has_no_answer_bearing_hidden_sheets(tmp_path):
    ...
    assert "_RefFormulas" not in wb_t.sheetnames
    assert "_RefValues" not in wb_t.sheetnames
    assert "_TrainerMeta" not in wb_t.sheetnames


def test_trainer_component_map_is_locator_only(tmp_path):
    ...
    for comp in load_semantic_map(trainer_path).all_ordered():
        assert comp.formula in ("", None)
        assert comp.expected_value is None
        assert not comp.short_hint
        assert comp.hints == []
        assert comp.tab and comp.cell and comp.semantic_key


def test_answer_key_component_map_retains_answers(tmp_path):
    ...
    for comp in load_semantic_map(answer_key_path).all_ordered():
        assert isinstance(comp.formula, str) and comp.formula.startswith("=")
        assert comp.expected_value is not None
        assert comp.short_hint or comp.hints


def test_no_trainer_json_answer_sidecar(tmp_path):
    ...
    assert not (tmp_path / "DEMO_HK_Trainer.trainer.json").exists()
```

Also strengthen the existing practice-cell tests so every semantic practice component satisfies:

```text
Trainer:    value is None; fill == FFFF00; comment is None
Answer Key: formula/input present; fill == FFFF00; non-empty legacy Note
```

Scan Trainer worksheet cell values/comments for every known `short_hint` and detailed hint string from the full Answer-Key map and assert those hint strings are absent.

Do not scan ordinary non-practice model formulas as if they were leaks; the contract forbids withheld answer metadata, not legitimate populated non-practice calculations.

### Verify

```bash
pytest core/tests/test_trainer.py -v
```

---

## Task 3 — Remove Hint/Reveal; keep Check binary and non-disclosing

**Files:**
- Delete: `core/trainer/hints.py`
- Modify: `core/trainer/__init__.py`
- Modify: `core/__main__.py`
- Modify: `core/trainer/checker.py`
- Delete: `core/templates/TrainerMacros.bas`
- Test: `core/tests/test_trainer.py`

### Remove Hint and Reveal product surfaces

Delete the progressive Hint and Reveal Answer implementations rather than leaving dead product paths that mutate the Trainer.

Remove:

- `show_hint` / `HintResult`;
- `reveal_answer`;
- `hint` CLI subcommand;
- `reveal` CLI subcommand;
- Hint/Reveal exports from `core.trainer`;
- Hint/Reveal references from the Trainer index sheet;
- `TrainerMacros.bas`, because its Hint/Reveal paths violate the contract and its local Check depends on answer-bearing Trainer metadata that is being removed.

Do not replace them with a different hidden reveal mechanism. Opening the Answer Key is the reveal/hint action.

### Redesign optional Check around the paired Answer Key

`check_component(trainer_path, component_id)` must obtain the full reference component from the matching `*_Answer_Key.xlsx`, not from answer-bearing Trainer metadata.

Use the current naming contract (`answer_key_path_for(trainer_path)`) and fail clearly if the matching Answer Key does not exist.

Check may internally use:

- the Answer Key formula;
- the Answer Key expected value;
- dependency coordinates from the Answer Key semantic map.

But it must not expose those answers in its returned/public result.

Refactor `CheckResult` so it does **not** carry `expected_value` as user-facing state. Keep only non-answer result data such as:

```python
@dataclass
class CheckResult:
    component_id: str
    passed: bool
    message: str
    user_value: float | str | None = None
    formula_present: bool = False
```

Mismatch messages must be non-disclosing, e.g.:

```text
Incorrect: the result does not match the Answer Key.
```

Do not print the expected numeric value or expected formula.

`check_dependencies()` may report missing expected dependency references by component/address, but must not return the answer formula or hint text.

Check must not modify the Trainer workbook.

### TDD regressions

Replace the old Reveal test with tests equivalent to:

```python
def test_check_uses_paired_answer_key_without_trainer_answers(tmp_path):
    ...
    full = load_semantic_map(answer_key_path).get("nopat_fy")
    wb = load_workbook(trainer_path)
    row, col = parse_cell_ref(full.cell)
    wb[full.tab].cell(row=row, column=col, value=full.formula)
    wb.save(trainer_path)
    wb.close()

    result = check_component(trainer_path, "nopat_fy")
    assert result.passed


def test_check_mismatch_does_not_disclose_expected_answer(tmp_path):
    ...
    result = check_component(trainer_path, "nopat_fy")
    full = load_semantic_map(answer_key_path).get("nopat_fy")
    assert not result.passed
    assert full.formula not in result.message
    assert str(full.expected_value) not in result.message
    assert "expected" not in result.message.lower()


def test_check_requires_matching_answer_key(tmp_path):
    ...
    answer_key_path.unlink()
    with pytest.raises(FileNotFoundError, match="Answer Key"):
        check_component(trainer_path, "nopat_fy")
```

Add a CLI/help regression proving `hint` and `reveal` are no longer public subcommands and that `check` remains.

### Verify

```bash
pytest core/tests/test_trainer.py -v
python -m core --help
```

The help output must include `check` and must not include `hint` or `reveal`.

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

Use `"concept": ""` for conceptless rows so the schema is explicit and stable.

Do not change the current date/value representation in this task.

### TDD regression

Build a temporary Excel source using:

```text
Concept | Line Item | 2024-12-31 | 2025-12-31
```

Run the CLI ingest path to JSON, then reload that JSON through `HKManualDocumentAdapter`. Assert that both deferred-tax concepts survive exactly and remain separately identifiable.

### Verify

```bash
pytest core/tests/test_line_identity.py -v
```

---

## Task 5 — Align docs and committed examples with the contract

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `.gitignore` only for narrowly scoped generated demo sidecars if needed
- Delete: `example/DEMO_HK_Trainer_reference.xlsx`
- Delete: `example/DEMO_HK_Trainer_reference.assumptions.json`
- Delete: `example/DEMO_HK_Trainer.trainer.json`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Add/regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Delete `example/rowmap.json` if it is merely generated demo metadata and no test/runtime consumer requires the committed copy

### Documentation contract

Rewrite all user-facing trainer documentation so the workflow is unambiguous:

```text
Trainer = blank yellow practice cells, no answers, no hints.
Answer Key = same yellow cells with formula/input + legacy Note hint.
Optional Check = correct/incorrect only.
```

Remove all instructions to import macros or run `hint` / `reveal` commands.

Do not describe removed functionality as "optional legacy" behavior.

### Example contract

The committed example should demonstrate the current product, not historical intermediate output.

After regeneration, `example/` must contain the current matched pair:

```text
DEMO_HK_Trainer.xlsx
DEMO_HK_Answer_Key.xlsx
```

and must not contain any `*_reference.xlsx`.

Internal generated JSON sidecars do not need to be committed as examples. If building in `example/` creates untracked implementation sidecars, either delete them after verification or add **narrowly scoped** ignore rules for those generated demo files. Do not add a broad ignore rule that would hide legitimate assumptions JSON elsewhere in the repository.

Inspect both generated workbooks with openpyxl before handoff; do not infer correctness only from file names.

---

## Task 6 — Full regression and leakage audit

**Files:**
- Modify: `RESULT.md`

Run at minimum:

```bash
pytest core/tests/test_classification.py -v
pytest core/tests/test_line_identity.py -v
pytest core/tests/test_reference_integrity.py -v
pytest core/tests/test_line_resolver.py -v
pytest core/tests/test_trainer.py -v
pytest core/tests/ -q
python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
python -m core --help
```

Then run one explicit artifact audit with Python/openpyxl against the `/tmp` pair that verifies all of the following:

### Trainer

- every semantic practice cell is blank;
- every semantic practice cell is bright yellow;
- every semantic practice cell has no Note/comment;
- `_RefFormulas`, `_RefValues`, and `_TrainerMeta` do not exist;
- Trainer `_ComponentMap` contains coordinates/identity but no formulas, expected values, `short_hint`, or detailed hints;
- Trainer `.component_map.json`, if emitted, is equally sanitized;
- no `*.trainer.json` is emitted;
- no worksheet value/comment contains any known hint string from the Answer Key map;
- visible Trainer instructions contain no Hint/Reveal/macro workflow.

### Answer Key

- every semantic practice cell contains its working formula/input;
- every semantic practice cell is bright yellow;
- every semantic practice cell has a non-empty legacy Note authored consistently;
- full semantic formulas/expected values remain available to internal Check logic.

### Pair/repository

- visible sheet structure and formatting parity still pass the existing tests;
- exactly 13 semantic components remain;
- no `*_reference.xlsx` is produced by the new build;
- committed `example/` contains the Trainer + Answer Key pair and no stale reference workbook;
- standardized JSON round-trip retains `LineItem.concept`.

Do not report complete if any leakage test fails even if the general test suite is green.

---

## Preserve accepted accounting / identity behavior

Do not regress:

- eight BAVGEM balance-sheet categories;
- explicit ambiguity notes rather than fake categories;
- source checksum blocking;
- asset-detail / liability-detail / implied-equity reconciliation;
- live Condensed Financials CHECK formulas;
- classification SUMIF reactivity;
- DuPont using implied reformulated equity;
- shared line resolver for revenue / NI / tax / interest / totals;
- ten-year Bear/Base/Bull residual-income chain;
- canonical concept+label statement identity;
- case-insensitive displayed-label identity with exact concept IDs;
- same-label/different-concept preservation;
- conceptless ambiguity rejection;
- same-identity cross-document restatement handling;
- optional Excel Concept column;
- case-insensitive unique-label overrides and concept-specific overrides;
- concept-qualified source row maps;
- semantic component registration at build time;
- current 13-component catalog.

## Expected implementation files

Primary expected changes:

```text
core/model/classification.py
core/trainer/workbook.py
core/engine/semantic_map.py          (only if used for sanitized locator copy)
core/engine/map_embed.py             (only if needed)
core/trainer/semantic_io.py          (only if needed)
core/trainer/checker.py
core/trainer/__init__.py
core/__main__.py
core/tests/test_classification.py
core/tests/test_line_identity.py
core/tests/test_trainer.py
README-HK-TRAINER.md
skills/bav-trainer/SKILL.md
RESULT.md
```

Expected deletions:

```text
core/trainer/hints.py
core/templates/TrainerMacros.bas
example/DEMO_HK_Trainer_reference.xlsx
example/DEMO_HK_Trainer_reference.assumptions.json
example/DEMO_HK_Trainer.trainer.json
```

Expected example output:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

Only touch other files when a failing regression demonstrates they are required.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership/order.
- forecast/residual-income/scenario mathematics.
- manual-HK-v1 sourcing boundary.
- Git history.

---

## Acceptance criteria

This step is ready for ChatGPT review only when all are true:

1. `CommonStockSubjectToRedemption` no longer gets forced into Equity by generic concept matching.
2. Trainer practice cells are blank yellow with no Notes/comments.
3. Answer Key practice cells contain the correct formula/input, stay yellow, and carry one non-empty legacy Note hint.
4. Trainer contains no `_RefFormulas`, `_RefValues`, or `_TrainerMeta` answer stores.
5. Trainer embedded/sidecar semantic metadata contains no practice formulas, expected values, `short_hint`, or detailed hint text.
6. No `.trainer.json` full-answer sidecar is produced.
7. No progressive Hint or Reveal Answer command/API/macro/user instruction remains in the target trainer product.
8. Optional Check uses the paired Answer Key internally, returns only non-disclosing validation, and does not modify the Trainer.
9. CLI help exposes `check` but not `hint` or `reveal`.
10. `cmd_ingest -o` preserves `LineItem.concept`, demonstrated by an Excel → JSON → reload regression.
11. Committed examples contain the current Trainer + Answer Key and no `*_reference.xlsx`.
12. Visual parity, semantic mapping, Step 3 integrity, Step 4 identity, and the 13-component catalog remain intact.
13. Full core test suite passes and the demo build succeeds.

## RESULT.md handoff format

Before stopping, overwrite `RESULT.md` with:

```text
Status: Step 5 complete | blocked

Files changed:
- ...

Files deleted:
- ...

Tests run:
- <exact command> -> <exact result>
...

Artifact contract checks:
- Trainer blank/yellow/no Notes: ...
- Trainer hidden answer stores absent: ...
- Trainer semantic metadata sanitized: ...
- Answer Key formula/yellow/legacy Note: ...
- Hint/Reveal public surfaces removed: ...
- Check binary/non-disclosing: ...
- no *.trainer.json: ...

Identity/export checks:
- concept round-trip: ...
- common-stock classification regression: ...

Example checks:
- Trainer + Answer Key committed: ...
- no *_reference.xlsx: ...

Unresolved: ...
```

## Cursor execution rules

1. Read `TARGET.md` and this file before editing.
2. Write each new regression before the code change it protects and verify the intended failure.
3. Make the minimum coherent implementation change for that regression.
4. Do not preserve legacy Hint/Reveal behavior; it is explicitly outside the target contract now.
5. Do not solve Trainer leakage by merely hiding answer-bearing sheets more deeply. Remove or sanitize the answer data.
6. Keep full answer/hint metadata only with the Answer Key/reference side of the pair.
7. Run focused tests after each task, then the complete suite and artifact audit.
8. Update `RESULT.md` with exact evidence.
9. Report unresolved issues rather than weakening the contract.
10. Do not propose or start component-catalog expansion.
11. Do not commit or push; the user owns the checkpoint commit.

## ChatGPT verification protocol

After the user pushes the implementation checkpoint, ChatGPT should verify by code inspection:

- all 13 acceptance criteria above;
- that Trainer leakage is removed from hidden worksheets **and** sidecars, not only visible cells;
- that Hint/Reveal are actually absent from runtime/docs/macros;
- that Check cannot disclose expected values/formulas/hints;
- that concept metadata survives standardized JSON export/reload;
- that the example pair matches the current product contract;
- the exact test/audit evidence recorded in `RESULT.md`.

Only after this step is accepted should planning move to expanding the semantic practice surface beyond the current 13 representative components.
