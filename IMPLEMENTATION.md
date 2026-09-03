# Step 5 — Enforce a Two-Workbook-Only Training Loop

> **For Cursor:** Read `TARGET.md` first. Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Enforce the final product contract: **Trainer = blank yellow practice cells with no hints, answers, validation, or hidden answer-bearing metadata; Answer Key = the corresponding formula/input plus one concise legacy Excel Note hint in the same yellow cell.** Remove Check, Hint, and Reveal entirely before expanding the practice surface.

**Architecture:** Keep the existing reference-model-first, semantic-map, concept-aware identity, and paired-workbook architecture. Use the full semantic map only while constructing the model and Answer Key and while deriving the Trainer. After the Trainer practice cells are blanked, strip answer-bearing internal sheets and sidecars from the Trainer. The Answer Key is the sole feedback mechanism. No runtime Trainer checking/reveal subsystem remains.

**Tech Stack:** Python, pytest, openpyxl, existing BAV Trainer modules.

**Spec:** `TARGET.md` as updated in planning commit `6a1fb46`.

## Current checkpoint

Base implementation commit: `5c3242f` (`chat identity corrected 4C`) on `chatgpt/reference-model-integrity`.

Step 4's concept-aware identity work is substantially correct. `RESULT.md` reports 68 passing core tests and a successful 13-component Trainer / Answer Key build. Review of that checkpoint found five concrete issues to resolve now:

1. `commonstock` remains an unsafe high-priority concept substring and can force redeemable/common-stock obligations into Equity.
2. The Trainer is currently derived by copying the Answer Key and retains answer-bearing hidden metadata and sidecars even though visible practice cells are blank.
3. Check, Hint, and Reveal Python/CLI/VBA surfaces still exist and conflict with the final two-workbook-only learning loop.
4. `python -m core ingest ... -o ...` drops `LineItem.concept`, breaking concept-aware identity on standardized JSON round trips.
5. `example/` still contains stale `*_reference.xlsx` artifacts and does not represent the current product.

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
- The Answer Key is the only feedback, hint, and answer surface.
- Do not preserve Check, Hint, or Reveal as compatibility APIs.
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

The new regression must fail for the intended reason before the implementation change and pass afterward.

---

## Task 2 — Make the Trainer a sanitized workbook, not a hidden Answer Key

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `core/engine/map_embed.py` only if needed for Answer-Key-only metadata
- Modify: `core/trainer/semantic_io.py` only if cleanup leaves obsolete Trainer-runtime helpers
- Test: `core/tests/test_trainer.py`

### Final artifact contract

#### Answer Key

The Answer Key remains the complete reference workbook:

- every practice cell contains its correct working formula/input;
- every practice cell is bright yellow;
- every practice cell has one non-empty legacy Excel Note with the concise hint;
- Answer-Key semantic metadata may retain formulas, expected values, and hint fields for build/test purposes.

#### Trainer

The Trainer contains only the learner-facing workbook:

- same visible model sheets, structure, formatting, source data, labels, and non-practice calculations as the Answer Key;
- every practice cell blank and bright yellow;
- no Note/comment on practice cells;
- no adjacent hint cells;
- a visible practice-index sheet may list non-answer information such as order, component title, tab, cell, and dependencies.

The Trainer must not contain withheld answers or hints in:

- practice cells;
- visible adjacent cells;
- Notes/comments;
- hidden worksheets;
- embedded component metadata;
- JSON sidecars associated with the Trainer.

### Remove obsolete hidden runtime stores

The current `_RefFormulas`, `_RefValues`, and `_TrainerMeta` sheets existed to support Check/Hint/Reveal and macros. Remove their generation entirely from the product. They are no longer needed in either workbook.

The full `_ComponentMap` is useful for the Answer Key/build pipeline but is answer-bearing. Do **not** leave it in the Trainer. After the Trainer is derived and practice cells are blanked, remove `_ComponentMap` from the Trainer.

Do not replace these sheets with a differently named hidden answer store.

### Remove Trainer sidecars that expose answers

Do not copy the Answer Key's `.component_map.json` to the Trainer.

Stop generating `*.trainer.json`.

A normal build must not leave any Trainer-associated JSON file that contains formulas, expected values, `short_hint`, or detailed hints.

If a non-answer locator sidecar is not required by any remaining product feature after Check/Hint/Reveal are deleted, do not create one. Prefer no Trainer sidecar at all.

### Simplify the visible Trainer index

Keep the visible `Trainer` index sheet if it helps the learner follow dependency order, but remove dead interactive/status concepts.

Recommended columns:

```text
Order | Component | Tab | Cell | Depends on
```

Recommended instruction:

```text
Complete yellow practice cells in dependency order. Open the matching Answer Key to inspect the formula/input and hover over its Note for the hint.
```

Remove:

- `Status` if nothing updates it;
- Check/Hint/Reveal references;
- macro-import instructions;
- `CheckActive`, `HintActive`, `RevealActive` references;
- progressive-hint language.

### TDD regressions

Update `core/tests/test_trainer.py` so tests do not rely on loading a full semantic map from the Trainer. Use the Answer Key semantic map to locate corresponding Trainer cells.

Add/strengthen tests equivalent to:

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
        trainer_cell = wb_t[comp.tab].cell(row=row, column=col)
        answer_cell = wb_a[comp.tab].cell(row=row, column=col)
        assert trainer_cell.value is None
        assert trainer_cell.comment is None
        assert _fill_rgb(trainer_cell) == "FFFF00"
        assert isinstance(answer_cell.value, str) and answer_cell.value.startswith("=")
        assert answer_cell.value == comp.formula
        assert answer_cell.comment is not None
        assert answer_cell.comment.text.strip()
        assert _fill_rgb(answer_cell) == "FFFF00"
    wb_t.close()
    wb_a.close()
```

Add a leakage scan that loads the full Answer Key map, collects every non-empty `short_hint`, detailed hint, practice formula, and stringified expected value, and verifies none are present in Trainer hidden sheets/sidecars. For worksheet formulas, distinguish withheld practice formulas from legitimate populated non-practice formulas: test the exact practice-component formulas/locations rather than banning all formulas from the Trainer.

### Verify

```bash
pytest core/tests/test_trainer.py -v
```

---

## Task 3 — Delete Check, Hint, Reveal, and macro feedback infrastructure

**Files:**
- Delete: `core/trainer/checker.py`
- Delete: `core/trainer/hints.py`
- Delete: `core/templates/TrainerMacros.bas`
- Modify: `core/trainer/__init__.py`
- Modify: `core/__main__.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_trainer.py`

### Required behavior

The trainer product has no runtime feedback commands. Do not keep the old APIs as deprecated or optional compatibility paths.

Remove all of the following:

- `CheckResult`;
- `check_component()`;
- `check_dependencies()`;
- `HintResult`;
- `show_hint()`;
- `reveal_answer()`;
- CLI `check` subcommand;
- CLI `hint` subcommand;
- CLI `reveal` subcommand;
- exports of those APIs from `core.trainer`;
- `TrainerMacros.bas` and all macro instructions;
- Trainer-sheet status syncing or reveal colors/constants used only by those features.

Do not replace Check with a new validation command. Do not replace Hint/Reveal with alternative buttons or hidden workbook mechanisms.

The only normal CLI commands relevant to the trainer remain build/ingest/list or other non-feedback project utilities that are independently useful.

### TDD regressions

Update tests so no test imports `checker` or `hints`.

Add a CLI surface regression:

```python
def test_cli_has_no_check_hint_or_reveal_commands(capsys):
    from core.__main__ import main
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out.lower()
    assert "check" not in out
    assert "hint" not in out
    assert "reveal" not in out
```

If argparse formatting or unrelated prose makes a bare-word assertion brittle, inspect the registered subcommand names directly or assert that invoking each removed command fails as an invalid choice.

Also add repository-level/import regressions as appropriate so deleted modules are not accidentally reintroduced through `core.trainer.__init__`.

### Verify

```bash
pytest core/tests/test_trainer.py -v
python -m core --help
```

The public CLI must not offer `check`, `hint`, or `reveal`.

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

## Task 5 — Align docs and committed examples with the final contract

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify other live trainer documentation only where repository search finds Check/Hint/Reveal instructions
- Delete: `example/DEMO_HK_Trainer_reference.xlsx`
- Delete: `example/DEMO_HK_Trainer_reference.assumptions.json`
- Delete: `example/DEMO_HK_Trainer.trainer.json`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Add/regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Delete `example/rowmap.json` if it is merely generated demo metadata and no runtime/test consumer requires the committed copy

### Documentation contract

All live trainer documentation must state the same simple loop:

```text
Trainer = blank yellow practice cells, no answers, no hints, no Check/Hint/Reveal tools.
Answer Key = same yellow cells with formula/input + one legacy Note hint.
```

Remove all instructions to:

- run `python -m core check`;
- run `python -m core hint`;
- run `python -m core reveal`;
- import `TrainerMacros.bas`;
- use `CheckActive`, `HintActive`, or `RevealActive`;
- expect progressive hints or reveal states.

Do not describe removed functionality as optional legacy behavior.

Run a local repository search and update live trainer-facing references:

```bash
rg -n "Check|Hint|Reveal|check_component|show_hint|reveal_answer|TrainerMacros|CheckActive|HintActive|RevealActive" \
  core README-HK-TRAINER.md skills/bav-trainer
```

After cleanup, remaining matches should be only legitimate statements such as tests asserting absence or the Answer Key's Excel Note **hint** wording. Review every remaining match rather than mechanically requiring zero uses of the English word `hint`, because the Answer Key still intentionally has hints.

### Example contract

The committed example must demonstrate the current product:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

It must not contain:

```text
*_reference.xlsx
*_Trainer.trainer.json
```

Do not commit Trainer-side answer metadata. If the Answer Key build emits implementation sidecars, they need not be committed as examples unless a runtime path actually requires them.

Inspect both generated workbooks with openpyxl before handoff; do not infer correctness from filenames alone.

---

## Task 6 — Full leakage audit, regression suite, and handoff evidence

**Files:**
- Modify: `RESULT.md`

### Required verification

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

Then perform a focused generated-artifact audit in Python/openpyxl or a test:

1. exactly two `.xlsx` outputs are produced for the `/tmp` demo pair;
2. no `*_reference.xlsx` is produced;
3. no Trainer `.trainer.json` or `.component_map.json` is produced;
4. Trainer has no `_ComponentMap`, `_RefFormulas`, `_RefValues`, or `_TrainerMeta` sheet;
5. every Trainer practice cell is blank yellow with no Note;
6. every Answer Key practice cell contains the correct formula/input, is yellow, and has a non-empty legacy Note;
7. every known Answer-Key practice formula/hint/expected-value token is absent from Trainer answer-bearing metadata locations;
8. visible structure/style parity still holds;
9. `python -m core --help` exposes no `check`, `hint`, or `reveal` subcommand;
10. the build still resolves all 13 current semantic components.

Do not claim a leakage check based only on visible worksheet cells. Inspect hidden sheets and generated sidecars as well.

### RESULT.md handoff format

Overwrite `RESULT.md` before stopping:

```text
Status: Step 5 complete | blocked

Files changed:
- ...

Files deleted:
- ...

Tests run:
- <exact command> -> <exact result>
...

Trainer contract:
- blank yellow practice cells/no Notes: ...
- answer-bearing hidden sheets absent: ...
- Trainer answer sidecars absent: ...
- Check/Hint/Reveal product surfaces absent: ...

Answer Key contract:
- formula/input in yellow practice cells: ...
- concise legacy Notes present: ...

Identity/export checks:
- concept round trip: ...
- common-stock concept regression: ...

Example cleanup:
- Trainer + Answer Key committed pair: ...
- stale reference artifacts removed: ...

Unresolved: ...
```

If any required condition is not met, write `Status: Step 5 blocked` and describe the exact blocker.

---

## Files expected to change

Primary implementation:

- `core/model/classification.py`
- `core/trainer/workbook.py`
- `core/__main__.py`
- `core/trainer/__init__.py`
- `core/tests/test_classification.py`
- `core/tests/test_line_identity.py`
- `core/tests/test_trainer.py`

Expected deletions:

- `core/trainer/checker.py`
- `core/trainer/hints.py`
- `core/templates/TrainerMacros.bas`
- stale `example/*_reference.xlsx` / old trainer sidecars

Documentation/example updates:

- `README-HK-TRAINER.md`
- `skills/bav-trainer/SKILL.md`
- `example/DEMO_HK_Trainer.xlsx`
- `example/DEMO_HK_Answer_Key.xlsx`
- `RESULT.md`

Only modify other files when a failing test or repository search demonstrates they are required.

## Preserve from Steps 3 and 4

Do not regress:

- eight BAVGEM balance-sheet categories;
- explicit ambiguity notes/defaults where already designed;
- source checksum blocking;
- asset-detail / liability-detail / implied-equity reconciliation;
- live Condensed Financials CHECK **worksheet formula** (this is an accounting-model reconciliation cell, not the removed trainer Check feature);
- classification SUMIF reactivity;
- DuPont using implied reformulated equity;
- shared line resolver for revenue / NI / tax / interest / totals;
- ten-year Bear/Base/Bull residual-income chain;
- concept-aware statement identity;
- case-insensitive displayed-label identity with exact concept IDs;
- same-label/different-concept preservation;
- duplicate/ambiguous identity rejection;
- concept-specific classification overrides;
- optional Excel Concept column;
- concept-qualified source row maps during model construction;
- paired Trainer / Answer Key styling and visible parity;
- current 13 semantic components.

The phrase `CHECK` inside the financial model may remain when it refers to accounting reconciliation. The removed feature is the trainer's runtime `check` command/API, not accounting control formulas inside the BAV workbook.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership or order.
- Trainer / Answer Key visible product structure beyond removing dead interactive/status UI.
- forecast / residual-income mathematics.
- automatic HKEX/SEC ingestion.
- later BAVGEM feature chains.
- Git history.

## Acceptance criteria

Step 5 is ready for ChatGPT review only when all are true:

1. Trainer practice cells are blank bright yellow with no Notes/comments.
2. Answer Key practice cells contain correct formulas/inputs, are bright yellow, and each has one non-empty concise legacy Excel Note.
3. Trainer contains no withheld practice formulas, expected answer values, or hint text in hidden worksheets or Trainer-associated sidecars.
4. Trainer has no `_ComponentMap`, `_RefFormulas`, `_RefValues`, or `_TrainerMeta` answer-bearing hidden sheet.
5. No Trainer `.component_map.json` or `.trainer.json` answer sidecar is generated.
6. Check, Hint, and Reveal trainer APIs/CLI commands/macros are removed, not merely hidden or deprecated.
7. Trainer UI/documentation contains no Check/Hint/Reveal workflow.
8. The Answer Key is the sole feedback mechanism.
9. `LineItem.concept` survives standardized JSON export/reload.
10. Generic redeemable common-stock concepts no longer force Equity.
11. The example directory represents the current Trainer + Answer Key pair and contains no stale reference workbook.
12. Step 3 accounting integrity and Step 4 identity behavior remain intact.
13. Full core test suite passes.
14. Demo build still resolves all 13 current semantic components.
15. No fixed-coordinate registry or second identity algorithm is introduced.

## Cursor execution rules

1. Read `TARGET.md` and this file before editing.
2. Do not reinterpret the feedback loop: there is only Trainer + Answer Key.
3. Write focused failing regressions before each behavioral change.
4. Delete obsolete Check/Hint/Reveal code rather than preserving compatibility shims.
5. Sanitize the Trainer after blanking practice cells and before saving/final handoff.
6. Use the Answer Key semantic map when tests need component coordinates.
7. Preserve accepted accounting/identity behavior.
8. Run focused tests after each coherent change, then the full suite and artifact audit.
9. Update `RESULT.md` with exact commands/results.
10. Do not propose or begin practice-surface expansion.
11. Do not commit or push; the user owns the checkpoint.

## ChatGPT verification protocol

After the user pushes the implementation checkpoint, ChatGPT should verify by code inspection:

- all Step 5 acceptance criteria;
- removal of Check/Hint/Reveal code and public surfaces;
- absence of answer-bearing Trainer hidden sheets/sidecars;
- Trainer vs Answer Key cell contract;
- concept-preserving standardized export;
- common-stock classification regression;
- example cleanup;
- preservation of Step 3/4 accounting and identity behavior;
- exact test evidence in `RESULT.md`.

If verified, the next product step may expand the semantic practice surface beyond the current 13 representative components.
