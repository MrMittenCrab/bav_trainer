# Step 9I.1 — Learner-Ready Historical Workbook + Practical README

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first, then read this plan in full. The accepted implementation base is commit `80985ef4142b78563521438a90c9598c1f7eb51d` (`Step 9H1`, historical-v1 exit gate complete). Implement only Step 9I.1 below using red/green TDD. This remains **Step 9 historical work**. Do not begin forecasting, valuation, scenarios, or a Step 10-style forward model. Preserve all formula families, expected values, workbook logic, judgment behavior, Check behavior, optional-module gating, and cross-company robustness established through Step 9H.1. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make the completed historical trainer pleasant enough to use for actual learning now: simplify the visible Excel aesthetic to a strict white/yellow system with Aptos Narrow 11 throughout, remove decorative styling, and replace the repository’s legacy-heavy GitHub landing README with a short practical guide to the trainer’s current functions and planned future functions.

**Architecture:** Treat this as learner-readiness polish, not curriculum expansion. Keep the historical semantic surface frozen at family orders `1..78`. Simplify presentation centrally in `TrainingWorkbookGenerator` so every visible sheet follows one style contract, then regenerate the canonical demo pair. Replace root `README.md` as the repository front door; keep it focused on install/build/practice/check/current scope/future roadmap rather than project lineage. No model math or expected-value logic should change.

**Tech Stack:** Python, pytest, openpyxl, existing `TrainingWorkbookGenerator`, `build_training_workbook`, `check_workbook`, semantic map helpers, Step 9H.1 exit-gate tests, and the existing canonical demo inputs.

**Spec:** `TARGET.md` plus the user’s newer explicit presentation instruction in this checkpoint. **Important:** the existing `TARGET.md` sentence that mentions “20-point bold worksheet titles” and “thin borders” is now stale relative to the user’s explicit instruction. For Step 9I.1, the visual contract below is authoritative. Cursor must not edit `TARGET.md`; ChatGPT owns that planning document.

## Global Constraints

- `TARGET.md` is read-only in Cursor.
- Remain in Step 9. Do not implement forecasting or valuation next.
- Preserve non-financial-company scope.
- Preserve active family namespace exactly `1..78`; add no new semantic family or practice cell.
- Preserve current workbook surfaces exactly:
  - ordinary demo, no assumptions: `62 families / 259 practice cells`;
  - ordinary demo + normalization assumptions: `66 / 279`;
  - shares only: `70 / 293`;
  - shares + normalization: `78 / 331`;
  - services matrix: `59 / 248`;
  - retail matrix: `78 / 331`;
  - manufacturer matrix: `70 / 293`.
- Preserve CLI exactly `{ingest, build, check, list}`.
- Preserve Check semantics: blank yellow, correct green, incorrect red; Check changes fill only and remains non-disclosing.
- Green/red are a **functional Check-state exception** to the fresh-workbook white/yellow palette. A freshly built Trainer/Answer Key must use no decorative fill colors other than white and yellow.
- Preserve formulas, expected values, number formats, column widths, row heights, alignment, freeze panes, hidden-sheet state, validation lists, Notes, and worksheet order unless a change is strictly required for the presentation contract.
- Preserve deferred forecast/valuation tabs as hidden placeholders.
- Do not add logos, icons, charts, gradients, colored fonts, decorative separators, new borders, or additional fill colors.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `80985ef4`

Step 9H.1 is a valid historical integrity/release gate:

- `288 passed` locally;
- active historical family orders `1..78` are unique;
- normal builds do not execute dormant forecast/valuation code;
- canonical demo artifacts were regenerated from source;
- base/norm/share/cross-company surfaces are preserved;
- Check remains formula-preserving and non-disclosing.

Two learner-facing problems remain and are the entire scope of this checkpoint.

### Problem 1 — the workbook styling is more decorated than requested

`core/trainer/workbook.py` currently defines and applies:

```text
TITLE_FONT = Aptos Narrow 20 bold
BODY_BOLD_FONT = Aptos Narrow 11 bold
THIN_BORDER = black thin border
section/header/total-row border logic
```

`_apply_oshkosh_style()` also preserves title/header emphasis. This conflicts with the desired learning surface: **no decorative hierarchy beyond white vs yellow and one Aptos Narrow 11 font**.

### Problem 2 — GitHub’s root README is still the wrong product front door

Current root `README.md` still opens with `BAVGems — BAV Pipeline + HK Excel Trainer`, then describes a separate AI-maintained coverage system, lineage, Gemini/Claude workflow, sentinel automation, vault structure, valuation, etc. That is not the product a user of this repository should see first and it is inconsistent with the current historical trainer.

`README-HK-TRAINER.md` is much closer to the current implementation, but GitHub renders root `README.md` as the repository landing page. The root README must become the canonical practical introduction.

---

### Task 1: Add a strict fresh-workbook visual contract

**Files:**
- Create: `core/tests/test_learner_ready_presentation.py`
- Read: `core/tests/test_historical_v1_exit_gate.py`
- Read: `core/tests/test_trainer.py`

**Interfaces:**
- Consumes: public `build_training_workbook()` path and canonical demo inputs.
- Produces: regression tests that precisely define the new visible styling contract without changing workbook semantics.

- [ ] **Step 1: Build a canonical Trainer/Answer-Key pair in the new test module**

Use the same source and normalization assumptions as Step 9H.1:

```python
from core.tests.test_per_share import DEMO_ASSUMPTIONS, DEMO_JSON
from core.data.interface import DocumentManifest, DocumentType
from core.ingestion.manual_hk import HKManualDocumentAdapter
from core.trainer.workbook import build_training_workbook


def _build_canonical(tmp_path):
    data = HKManualDocumentAdapter().ingest(
        [DocumentManifest(path=str(DEMO_JSON), doc_type=DocumentType.OTHER)]
    )
    assumptions = json.loads(DEMO_ASSUMPTIONS.read_text(encoding="utf-8"))
    return build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
        assumptions,
    )
```

- [ ] **Step 2: Add a helper for cells that are actually part of the visible workbook surface**

Ignore truly unused cells. Inspect cells when at least one of these is true:

```python
cell.value is not None
cell.comment is not None
cell.has_style
```

Only inspect worksheets where:

```python
ws.sheet_state == "visible"
```

Hidden internal metadata sheets and hidden deferred forecast placeholders are not part of the fresh visible-style contract.

- [ ] **Step 3: Assert one font everywhere on the fresh visible surface**

For both Trainer and Answer Key require every inspected visible cell to use:

```text
font name: Aptos Narrow
font size: 11
font bold: False
font italic: False
font underline: none
font color: black
```

Titles, headers, section labels, totals, Trainer index headers, judgment sheets, source sheets, and analytical sheets all follow the same font rule.

Do not special-case row 1 or headers.

- [ ] **Step 4: Assert no visible decorative borders**

For each inspected visible cell, require every border side to have no style:

```python
for side in (
    cell.border.left,
    cell.border.right,
    cell.border.top,
    cell.border.bottom,
    cell.border.diagonal,
):
    assert side.style is None
```

- [ ] **Step 5: Assert the fresh visible fill palette is only white or yellow**

Use the existing fill-color normalization convention and require:

```text
FFFFFF = ordinary / populated workbook cell
FFFF00 = practice / learner-response cell
```

No orange, blue, gray, green, red, gradient, or section-header fill is allowed in a fresh build.

The semantic formula-practice cells must remain yellow in both workbooks. Judgment-response cells that are learner-editable remain yellow. Ordinary visible cells are white.

- [ ] **Step 6: Prove Check colors are a functional exception, not a new base style**

On a fresh Trainer:

1. enter one exact Answer-Key formula into one practice cell;
2. leave another practice cell blank;
3. run `check_workbook()`;
4. require the entered cell to become green `C8E6C9`;
5. require the blank cell to remain yellow `FFFF00`;
6. require non-practice visible cells to remain white;
7. require font and border rules to remain unchanged.

Do not alter Check’s existing red/green/yellow constants.

- [ ] **Step 7: Run the new tests red**

```bash
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
```

Expected before implementation: fail because current titles are 20-point bold and current section/header/total rows receive thin borders.

---

### Task 2: Replace the Oshkosh-style decoration layer with one minimal style

**Files:**
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_learner_ready_presentation.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Consumes: existing visible workbook structure and SemanticMap.
- Produces: a fresh workbook whose only intentional visible style distinctions are white vs yellow, plus functional Check green/red after validation.

- [ ] **Step 1: Collapse font constants to one base font**

Replace title/body/bold variants with one constant:

```python
FONT_NAME = "Aptos Narrow"
BASE_FONT = Font(
    name=FONT_NAME,
    size=11,
    bold=False,
    italic=False,
    color="000000",
)
```

Keep:

```python
WHITE_FILL = PatternFill("solid", start_color="FFFFFF")
PRACTICE_FILL = PatternFill("solid", start_color="FFFF00")
```

Remove unused decorative constants/imports:

```text
TITLE_FONT
BODY_FONT
BODY_BOLD_FONT
THIN_BORDER
Side
```

Use a plain `Border()` when clearing pre-existing borders.

- [ ] **Step 2: Rename `_apply_oshkosh_style()` to `_apply_minimal_style()`**

The old name encodes an irrelevant legacy aesthetic. The new method should describe the actual product contract.

- [ ] **Step 3: Create the Trainer index before applying the global minimal style**

Change the Answer-Key generation sequence from:

```python
self._apply_oshkosh_style(wb)
self._add_trainer_ui(wb)
```

to:

```python
self._add_trainer_ui(wb)
self._apply_minimal_style(wb)
```

This ensures the `Trainer` index sheet receives the same font/border/fill normalization as every other visible sheet.

- [ ] **Step 4: Implement `_apply_minimal_style()` as a normalization pass**

For every visible worksheet:

```python
ws.sheet_view.showGridLines = False
```

For every cell in its used range that has a value/comment/style, set:

```python
cell.font = BASE_FONT
cell.fill = WHITE_FILL
cell.border = Border()
```

Do **not** overwrite:

```text
cell.value
cell.comment
cell.number_format
cell.alignment
cell.protection
row height
column width
freeze panes
data validation
```

Do not create title/header/section/total special cases.

- [ ] **Step 5: Re-apply only functional yellow learner surfaces after white normalization**

Keep the existing semantic decoration functions responsible for yellow:

```text
_decorate_answer_key_practice_cells
_decorate_answer_key_judgment_cells
_decorate_answer_key_normalization_judgment_cells
_blank_trainer_practice_cells
_blank_trainer_judgment_cells
_blank_trainer_normalization_judgment_cells
```

They may change fill to `PRACTICE_FILL`, but must not introduce bold fonts, borders, or other fills.

- [ ] **Step 6: Simplify `_add_trainer_ui()` styling**

Remove direct title/header font or border assignment. It should set only content, widths, and other structural metadata; `_apply_minimal_style()` owns visible styling.

In particular remove logic equivalent to:

```python
ws["A1"].font = TITLE_FONT
cell.font = BODY_BOLD_FONT
cell.border = THIN_BORDER
```

- [ ] **Step 7: Remove unused header-border helpers only if no longer referenced**

If `was_header_row()` becomes unused after the minimal-style change, delete it and its dead support code. Do not remove helpers still used elsewhere.

- [ ] **Step 8: Run focused presentation and Trainer tests**

```bash
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
```

All must pass without changing any practice counts or formulas.

---

### Task 3: Replace root GitHub README with a minimal practical trainer guide

**Files:**
- Replace: `README.md`
- Modify only if needed for consistency: `README-HK-TRAINER.md`
- Test: `core/tests/test_learner_ready_presentation.py`

**Interfaces:**
- Root `README.md` becomes the canonical GitHub landing page for the BAV Excel Trainer.
- `README-HK-TRAINER.md`, if retained, is an optional deeper technical reference and must not be necessary to understand basic use.

- [ ] **Step 1: Delete the current root README content rather than incrementally editing it**

The current root README primarily documents another coverage/pipeline product. Replace it with a short trainer-specific document.

The new root README must **not** discuss project lineage/origin or the old pipeline system. Do not include:

```text
BAVGems
BAV Pipeline
Gemini
Gemini Gems
legacy/
coverage/
sentinel
EDGAR pipeline
/bav-pipeline
/bav-update
/bav-news
/bav-brief
Claude Code plugin installation
```

Also remove any old claim that this Trainer has `Hint` or `Reveal` commands. The Answer Key is the hint/answer surface.

- [ ] **Step 2: Use this compact section structure**

```markdown
# BAV Excel Trainer — Hong Kong Edition

One short paragraph: historical BAV Excel practice for non-financial companies; the system supplies source facts and the learner reconstructs analytical formulas.

## What works now
## Quick start
## How to practice
## Inputs and scope
## Planned
```

Do not add a lineage/history section, architecture essay, plugin installation guide, vault explanation, or long feature marketing copy.

- [ ] **Step 3: Make `What works now` describe only implemented functions**

Keep it concise. Include:

```text
multi-period historical reformulation and DuPont
classification judgment
recurring/non-recurring normalization
cash-conversion / accrual diagnostics and trends
working-capital diagnostics
RNOA margin/turnover and change attribution
ROE operating/financing attribution
optional diluted per-share analysis when historical diluted-share data is supplied
optional normalized diluted EPS when both shares and normalization are supplied
one workbook-wide Check
matched Trainer + Answer Key
```

State that forecasting, valuation, and investment conclusions are not active yet.

- [ ] **Step 4: Make `Quick start` executable and short**

Use only the current public workflow:

```bash
pip install -r requirements-trainer.txt

python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx

python -m core list --workbook example/DEMO_HK_Trainer.xlsx
python -m core check --workbook example/DEMO_HK_Trainer.xlsx
```

Explain in one sentence that build produces:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

Do not put obsolete component counts in the root README unless they materially help the user; prefer avoiding brittle counts in the landing page.

- [ ] **Step 5: Make `How to practice` describe the actual loop**

Use a short numbered sequence:

```text
1. Open the Trainer.
2. Fill the yellow formula cells; supplied historical facts stay populated.
3. Run Check.
4. Yellow = blank, green = correct, red = incorrect.
5. If stuck, open the matching Answer Key for the working formula and its Note.
6. Repeat left-to-right in the Trainer index dependency order.
```

Mention that Accounting Judgment / Normalization Judgment treatment choices can change downstream expected formulas where those sheets are present.

- [ ] **Step 6: Make `Inputs and scope` practical**

State:

```text
non-financial operating companies only
manual historical JSON or Excel/Bloomberg/Wind-style exports
actual historical share data is required for per-share modules
missing optional data omits the corresponding module rather than inventing facts
```

Do not describe automatic HKEX/SEC scraping as a current feature.

- [ ] **Step 7: Make `Planned` reflect the user’s requested roadmap order**

Separate the next Step 9 work from later forward modelling:

```text
Next Step 9 work:
- learner usability / real-company practice runs
- broader historical accounting judgments where source data supports them
- additional structured historical interpretation and diagnostics

Later:
- driver-based forecasting
- valuation
- scenario / sensitivity work
- concise investment conclusions
```

Do not imply forecasting is the next immediate implementation stage.

- [ ] **Step 8: Clean the secondary trainer README if it still exposes irrelevant lineage**

If `README-HK-TRAINER.md` still contains sections such as `Relationship to BAV Pipeline`, Claude/plugin setup, or project-origin discussion, remove those sections. Keep it only as a deeper technical trainer reference.

Do not expand it; this checkpoint is reducing documentation noise.

- [ ] **Step 9: Add README regression assertions**

In `test_learner_ready_presentation.py`, load root `README.md` and require the five section headings above. Assert the forbidden legacy/pipeline terms are absent case-insensitively.

Also require the current public commands to appear:

```text
python -m core build
python -m core list
python -m core check
```

- [ ] **Step 10: Run README/presentation tests**

```bash
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
```

---

### Task 4: Refresh canonical workbooks after the style change

**Files:**
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Do not modify: `example/DEMO_HK_Standardized.json`
- Do not modify: `example/DEMO_HK_Assumptions.json`

**Interfaces:**
- Produces the committed example pair users can open immediately to start learning.

- [ ] **Step 1: Regenerate through the public build path**

Run:

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Do not manually edit the `.xlsx` binaries.

- [ ] **Step 2: Verify canonical semantic and Check counts remain unchanged**

Require:

```text
66 families
279 practice cells
fresh Trainer Check = 0 correct / 0 incorrect / 279 blank
```

- [ ] **Step 3: Run the new minimal-style assertion against the committed pair**

Add or reuse a test that opens:

```text
example/DEMO_HK_Trainer.xlsx
example/DEMO_HK_Answer_Key.xlsx
```

and applies the same fresh visible-style contract as temporary builds.

- [ ] **Step 4: Verify Trainer answer separation remains intact**

Require no Trainer answer-bearing sidecars and preserve all Step 9H.1 practice-cell / Note / Check contracts.

---

### Task 5: Preserve the historical logic surface while changing presentation only

**Files:**
- Test: `core/tests/test_cross_company_robustness.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_historical_v1_exit_gate.py`
- Production model files should not change.

- [ ] **Step 1: Prove semantic-map identity is unchanged**

No family additions/removals/reordering. The Step 9H.1 namespace assertion must remain:

```text
active family orders = 1..78 exactly
```

- [ ] **Step 2: Prove all cross-company surfaces remain unchanged**

Require:

```text
services:      59 / 248
retail:        78 / 331
manufacturer:  70 / 293
```

- [ ] **Step 3: Prove live judgment behavior still works**

Run the existing cross-company tests for:

```text
retail Short-term investment classification
retail normalization -> normalized EPS
manufacturer lease liability treatment
```

Style changes must not affect dynamic expected values or trusted-cell validation.

- [ ] **Step 4: Prove Check recoloring still patches fill only**

Existing repeated-Check / cached-result tests must continue to pass. Do not replace OOXML fill patching with openpyxl workbook rewrites.

---

### Task 6: Final Step 9I.1 verification and status

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all checks pass
- Modify: `skills/bav-trainer/SKILL.md` only if it contains presentation/documentation claims that are now false
- Do not modify: `TARGET.md`

- [ ] **Step 1: Run focused learner-readiness tests**

```bash
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [ ] **Step 2: Run model-integrity and cross-company regressions**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
```

- [ ] **Step 3: Run the full suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual final passing count; do not prestate a new number.

- [ ] **Step 4: Verify public CLI remains exactly unchanged**

Require:

```text
ingest
build
check
list
```

No `forecast`, `value`, `hint`, or `reveal` command.

- [ ] **Step 5: Record learner-ready presentation evidence in `RESULT.md`**

Record at minimum:

```text
fresh visible workbook fonts: Aptos Narrow 11 everywhere
fresh visible workbook fills: white/yellow only
fresh visible workbook borders: none
Check green/red feedback preserved
canonical example pair regenerated
root README replaced with practical trainer guide
legacy/pipeline origin material absent from root README
family/cell counts unchanged
full pytest count
forecasting / valuation still deferred
TARGET.md unchanged
```

- [ ] **Step 6: Mark this plan complete only after every verification is green**

Add a concise status line at the top of `IMPLEMENTATION.md`.

Then stop. Do **not** prepare or implement forecasting. The next planning checkpoint should remain within Step 9 unless the user explicitly changes direction.

---

## Definition of Done

Step 9I.1 is complete only when all of the following are true:

1. The latest historical model math and semantic surface remain unchanged at family orders `1..78`.
2. Every fresh visible Trainer/Answer-Key cell that participates in the workbook surface uses Aptos Narrow 11, non-bold, non-italic, black text.
3. Fresh visible cells have no decorative borders.
4. Fresh visible fills are white or yellow only.
5. Yellow remains the learner/practice distinction.
6. Check still uses green/red/yellow as functional validation feedback without changing formulas.
7. Trainer and Answer Key remain structurally identical apart from practice contents/Notes and Trainer sanitization.
8. Root `README.md` is a concise practical guide to the BAV Excel Trainer, not a BAVGems/BAV Pipeline history page.
9. Root README explains current functions, Quick Start, the actual learning loop, supported inputs/scope, next Step 9 work, and later planned forecasting/valuation functions.
10. Root README contains no project-lineage / legacy-pipeline narrative and no obsolete Hint/Reveal workflow.
11. The committed canonical demo pair is regenerated from source under the new style.
12. Ordinary, share-enabled, and cross-company counts remain exactly unchanged.
13. Full historical test suite passes.
14. Forecasting and valuation remain deferred and dormant.
15. Cursor performs no Git commit/push operations.
