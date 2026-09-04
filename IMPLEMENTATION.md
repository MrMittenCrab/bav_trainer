# Step 8A — Guided Classification Judgment With Consequences

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `9ddc60abb685d8d689b9f2c99983ea719e858d13` (`chat 7 correction`). Implement only this scoped Step 8A using red/green TDD. Run the exact verification commands, update `RESULT.md`, regenerate the demo pair, and stop. Do not begin normalization, earnings-quality diagnostics, forecasting, or valuation. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Move the trainer from purely supplied classifications toward guided analyst judgment by turning selected genuinely ambiguous balance-sheet classifications into explicit compare-and-defend exercises, while preserving the trusted Step 7 historical model, formula Check behavior, and Answer Key separation.

**Architecture:** Keep the canonical historical model on the existing supplied/reference classification so Step 7 formulas and cached-value Check remain stable. Add explicit ambiguity metadata to `ClassificationDecision`, derive company-specific `JudgmentCase` objects only from real classifier-flagged lines, and render a visible `Accounting Judgment` worksheet. The learner compares the supplied model treatment with defensible alternative treatment(s), chooses the treatment they would defend, writes a short rationale, and explains the expected economic consequence. The Answer Key contains the model treatment/rationale/consequence; the Trainer blanks only learner-response cells. Step 8A does **not** yet let alternative learner choices drive the main historical model; that live-model integration is deferred until Check can remain correct under alternative accounting treatments.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `ClassificationDecision`, `BalanceSheetReformulation`, `LineIdentity`, Trainer/Answer Key generation, and workbook-wide formula Check.

**Spec:** `TARGET.md`, especially `Level 2 — Analyst judgment`, the requirement that ambiguous accounting treatments be taught as alternatives with consequences rather than one universal answer, the material/applicable-topic constraint, and the statement that free-form essays need not yet be automatically graded.

## Current checkpoint review

Accepted base: `9ddc60ab`.

The Step 7 correction resolves the two blocking defects identified in the previous review:

- model-facing fiscal periods are canonicalized oldest -> newest before historical-series and DuPont construction;
- direct component expansion rejects non-chronological/duplicate axes;
- successful Trainer regeneration removes stale Trainer answer-bearing sidecars;
- recorded core suite: 103 passed;
- five-year demo remains 25 conceptual schedule families / 118 formula practice cells / fresh Check `0/0/118`.

No blocking regression was found in the changed production paths.

Two limitations remain but are **not Step 8A scope**:

1. irregular/stub/interim period comparability is not modeled robustly; the current correction intentionally deferred CAGR/stub/interim logic;
2. Step 7 `IMPLEMENTATION.md` remained a completed checklist rather than an active next-step handoff; this file replaces it.

Do not broaden period-axis behavior in Step 8A. Record period-cadence hardening for later cross-company robustness.

## Why Step 8 is split

The locked roadmap names classification, recurring/non-recurring treatment, normalization, leases, SBC, goodwill/intangibles, deferred taxes, minority interests, acquisitions, and other material accounting topics. Those are not one subsystem.

Step 8A implements one coherent first Level-2 capability:

```text
supplied reference classification
        ↓
identify real ambiguous classification
        ↓
show defensible alternative(s)
        ↓
learner chooses + defends treatment
        ↓
learner explains economic consequence
        ↓
compare with Answer Key model reasoning
```

Later Step 8 work can remove more scaffolding and add normalization/earnings-quality decisions after this interface is trustworthy.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve all Step 7 formula practice: 25 families and 118 formula cells for the revised five-year demo.
- Formula Check remains unchanged: yellow/green/red, workbook-wide, non-disclosing, cache-safe.
- Judgment response cells are **not** added to the formula `SemanticMap` or formula Check in Step 8A.
- Do not make ambiguous accounting appear to have one universally correct answer.
- Do not automatically invent questions from arbitrary labels. A Step 8A case must originate from an existing classifier decision explicitly marked `ambiguous=True` and must have explicitly encoded defensible options.
- Do not expose every ambiguous flag automatically if the category taxonomy cannot express a defensible alternative safely.
- Zero-valued lines across all modeled periods do not become judgment cases.
- Existing explicit classification overrides suppress the guided case for that line; an override is treated as a supplied setup decision in this step.
- Main `Condensed Financials` classifications remain populated and continue to drive the historical model. Step 8A is compare-and-defend, not live learner reclassification.
- No normalization, recurring/non-recurring adjustments, leases accounting mechanics beyond classification discussion, SBC dilution, acquisition accounting, minority-interest modeling, forecasting, valuation, Hint/Reveal, VBA, or free-form automated grading.
- Keep exactly two user-facing workbooks: Trainer and Answer Key.
- Trainer must contain no Answer-Key rationale/consequence text in hidden sheets, comments, or Trainer sidecars.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Encode defensible alternatives in the authoritative classifier

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Interfaces:**
- Extends: `ClassificationDecision`.
- Produces: explicit guided options and consequence teaching metadata for supported ambiguous classifications.
- Preserves: existing `category`, `ambiguous`, `reason`, and `overridden` behavior.

- [ ] **Step 1: Write failing metadata tests**

Extend the expected interface to:

```python
@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False
    guided_options: tuple[str, ...] = ()
    judgment_topic: str = ""
    consequence_note: str = ""
```

Add focused tests for these supported guided cases:

```text
Lease liability:
  supplied/reference = Operating Long-Term Liability
  guided options = Operating Long-Term Liability | Financial Liability

Deferred tax asset:
  supplied/reference = Operating Long-Term Asset
  guided options = Operating Long-Term Asset | Exclude

Deferred tax liability:
  supplied/reference = Operating Long-Term Liability
  guided options = Operating Long-Term Liability | Exclude

Pension obligation:
  supplied/reference = Operating Long-Term Liability
  guided options = Operating Long-Term Liability | Financial Liability

Short-term investment:
  supplied/reference = Financial Asset
  guided options = Financial Asset | Operating Working Capital Asset

Equity-method / associate / JV investment:
  supplied/reference = Operating Long-Term Asset
  guided options = Operating Long-Term Asset | Financial Asset
```

For each supported case assert:

```python
assert decision.ambiguous is True
assert decision.category == decision.guided_options[0]
assert len(decision.guided_options) >= 2
assert all(option in BALANCE_SHEET_CATEGORIES for option in decision.guided_options)
assert decision.judgment_topic
assert decision.consequence_note
```

- [ ] **Step 2: Explicitly protect unsupported ambiguity from becoming fake alternatives**

The current classifier flags a right-of-use / lease asset as ambiguous, but the current eight-category taxonomy does not contain an obviously defensible generic “financial asset” treatment for a ROU asset.

Add a regression asserting that the ROU-asset decision may remain:

```python
assert decision.ambiguous is True
assert decision.guided_options == ()
```

Do **not** invent `Financial Asset` or another category merely to create an exercise.

- [ ] **Step 3: Verify tests fail before implementation**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "guided or alternative or judgment" -v
```

- [ ] **Step 4: Implement the metadata at the classification source**

Populate `guided_options`, `judgment_topic`, and `consequence_note` in the existing ambiguous branches.

Use concise consequence language tied to BAV reformulation. Examples:

```text
Lease/pension liability:
Operating treatment lowers NOLA/NOA; financing treatment raises Net Debt.
The choice can shift RNOA versus FLEV/Spread interpretation while equity reconciliation should remain intact.

Deferred tax asset:
Including it as operating raises NOA; excluding it removes that balance from operating capital and can change RNOA.

Deferred tax liability:
Including it as operating lowers NOA; excluding it removes that balance from operating capital.

Short-term investment:
Financial-asset treatment reduces Net Debt; operating-WC treatment raises NOWC/NOA.

Equity-method investment:
Operating treatment raises NOA; financial-asset treatment reduces Net Debt.
```

Do not add company-specific claims that cannot be inferred from the supplied line.

- [ ] **Step 5: Preserve override behavior**

An explicit `classificationOverrides` choice must still return:

```python
overridden is True
ambiguous is False
```

and must not retain guided options from the default classifier.

- [ ] **Step 6: Run classification tests**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
```

Record the exact pass count.

---

## Task 2 — Derive stable company-specific JudgmentCase objects

**Files:**
- Create: `core/model/judgment.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `StandardizedFinancials` + `BalanceSheetReformulation`.
- Produces: `classification_judgment_cases(...) -> tuple[JudgmentCase, ...]`.
- `ReferenceModelBuilder.judgment_cases` becomes the build-time source for workbook rendering.

- [ ] **Step 1: Write failing case-construction tests**

Use this dataclass:

```python
@dataclass(frozen=True)
class JudgmentCase:
    id: str
    order: int
    line_identity: str
    label: str
    topic: str
    supplied_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str
```

And this constructor:

```python
def classification_judgment_cases(
    financials: StandardizedFinancials,
    reformulation: BalanceSheetReformulation,
) -> tuple[JudgmentCase, ...]:
    ...
```

Case rules:

1. iterate `reformulation.detail_indices` in source order;
2. use the authoritative `ClassificationDecision` for that exact index;
3. require `decision.ambiguous is True`;
4. require `len(decision.guided_options) >= 2`;
5. skip a line whose values are all `None`/zero across modeled source periods;
6. `supplied_treatment = decision.category`;
7. `alternatives` contains the remaining guided options, preserving order;
8. `line_identity` comes from `line_identity(item).key()`;
9. stable ID format:

```python
f"classification::{line_identity(item).key()}"
```

10. `model_rationale = decision.reason`;
11. `model_consequence = decision.consequence_note`;
12. `consequence_prompt` is a short non-answer prompt, e.g.:

```text
Explain which reformulated balance(s) and profitability/leverage interpretation change under the alternative treatment.
```

- [ ] **Step 2: Add suppression tests**

Assert:

- a supported ambiguous non-zero lease liability produces one case;
- an ambiguous ROU asset with no guided options produces no case;
- a zero-valued supported ambiguous line produces no case;
- an explicit override suppresses the case.

- [ ] **Step 3: Run and verify failure**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "judgment_case or guided_classification" -v
```

- [ ] **Step 4: Implement `core/model/judgment.py`**

Keep this module coordinate-free. It owns accounting-learning case identity/content, not workbook cell locations.

- [ ] **Step 5: Wire cases into `ReferenceModelBuilder`**

After `self.anchor = compute_anchor(...)`, set:

```python
self.judgment_cases = classification_judgment_cases(
    self.fin,
    self.anchor.reformulation,
)
```

Do not add these cases to `COMPONENT_CATALOG`, `ComponentSpec`, or `SemanticMap`.

- [ ] **Step 6: Run focused reference tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "judgment or classification" -v
```

---

## Task 3 — Add one real guided judgment case to the committed demo without changing model economics

**Files:**
- Modify: `example/DEMO_HK_Standardized.json`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Revised demo still has five fiscal years and exactly the same reported total liabilities/equity.
- Produces: exactly one Step 8A guided classification case.

- [ ] **Step 1: Split the existing `Other non-current liabilities` line**

Add a real ambiguous line:

```json
{
  "label": "Operating lease liabilities",
  "concept": "lease_liability",
  "values": {
    "2021-12-31": 300,
    "2022-12-31": 320,
    "2023-12-31": 340,
    "2024-12-31": 360,
    "2025-12-31": 380
  }
}
```

Reduce the existing `Other non-current liabilities` values from:

```text
1305, 1456, 1593, 1716, 1825
```

to:

```text
1005, 1136, 1253, 1356, 1445
```

Do not change `Total liabilities` or any other reported totals.

Because both lines use the current reference treatment `Operating Long-Term Liability`, the aggregate historical reference model should remain economically unchanged.

- [ ] **Step 2: Add demo-case assertions**

Assert:

```python
assert len(builder.judgment_cases) == 1
case = builder.judgment_cases[0]
assert case.label == "Operating lease liabilities"
assert case.supplied_treatment == "Operating Long-Term Liability"
assert case.alternatives == ("Financial Liability",)
```

Also assert the five-year build still resolves exactly 118 formula components.

- [ ] **Step 3: Verify reformulation preservation**

Build the revised demo and assert reported-equity/reformulation checks still pass for all periods.

Do not hard-code workbook coordinates.

---

## Task 4 — Render an `Accounting Judgment` worksheet in the Answer Key

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Visible sheet name: `Accounting Judgment`.
- One row per `JudgmentCase`.
- Answer Key contains the model response; Trainer sanitization happens in Task 5.

- [ ] **Step 1: Write a failing Answer-Key sheet test**

Required layout:

```text
A1  Accounting Judgment
A2  instruction text

row 4 headers:
Order
Line item
Topic
Supplied model treatment
Alternative(s) to evaluate
Your treatment
Your rationale
Your consequence explanation
```

For each case, row `5 + case.order - 1` contains:

```text
Order                     case.order
Line item                 case.label
Topic                     case.topic
Supplied model treatment  case.supplied_treatment
Alternative(s)            comma-separated case.alternatives
Your treatment            case.supplied_treatment
Your rationale            case.model_rationale
Your consequence          case.model_consequence
```

The instruction must explicitly say:

```text
The supplied treatment is the model's reference treatment, not a universal accounting truth. Compare it with the listed alternative(s), choose the treatment you would defend, and explain the economic consequence.
```

- [ ] **Step 2: Add treatment dropdown validation**

The `Your treatment` cell must use an Excel list validation containing exactly:

```text
case.supplied_treatment + case.alternatives
```

Do not expose unrelated classification categories merely to make the question harder.

- [ ] **Step 3: Handle zero-case companies cleanly**

If `judgment_cases` is empty, still create the visible sheet with headers and a message:

```text
No supported guided classification judgments were identified from the supplied company data.
```

Do not invent a case.

- [ ] **Step 4: Build the sheet after the historical model**

Add `_build_accounting_judgment(wb)` to `ReferenceModelBuilder.build()` after historical sheets are complete and before deferred placeholders / final save as appropriate.

The sheet must not participate in `SemanticMap.validate_complete()`.

- [ ] **Step 5: Run focused workbook tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "accounting_judgment or judgment_sheet" -v
```

---

## Task 5 — Derive a sanitized guided-judgment Trainer from the Answer Key

**Files:**
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- `TrainingWorkbookGenerator` receives the build-time judgment cases.
- Answer Key response cells remain populated/yellow.
- Trainer response cells become blank/yellow/no-Note.
- Prompt/context cells remain identical between pair.

- [ ] **Step 1: Pass judgment cases through the normal build path**

Change the generator constructor to:

```python
def __init__(
    self,
    answer_key_path: Path,
    semantic_map: SemanticMap | None = None,
    judgment_cases: tuple[JudgmentCase, ...] = (),
):
    ...
```

And in `build_training_workbook()`:

```python
builder = ReferenceModelBuilder(financials, assumptions)
semantic_map = builder.build(answer_key_path)
TrainingWorkbookGenerator(
    answer_key_path,
    semantic_map,
    judgment_cases=builder.judgment_cases,
).generate(trainer_path)
```

Do not persist `JudgmentCase.model_rationale` or `model_consequence` in a Trainer sidecar.

- [ ] **Step 2: Decorate Answer-Key response cells**

For each judgment row, columns F/G/H are bright yellow and contain the model response.

Use existing workbook styling conventions:

```text
Aptos Narrow
20-point sheet title
11-point body
bright-yellow response cells
thin restrained headers/borders
```

- [ ] **Step 3: Blank Trainer response cells**

After copying Answer Key -> Trainer, blank only columns F/G/H for each judgment row.

Trainer contract:

```text
F/G/H value: blank
F/G/H fill: bright yellow
F/G/H comment: none
```

Keep columns A-E identical to the Answer Key because they are intentional exercise context, not withheld answers.

- [ ] **Step 4: Preserve the main model classification scaffold**

The existing `Condensed Financials` classification column remains populated and pair-identical in Step 8A.

Do not make the learner judgment response drive SUMIF/reformulation formulas yet.

Reason: alternative live treatments would change cached expected values and could make equivalent-but-correct formulas fail the existing Check. Step 8A teaches comparison/defense without regressing the trusted formula feedback loop.

- [ ] **Step 5: Add leakage regression**

Build the revised demo. Collect:

```text
case.model_rationale
case.model_consequence
```

Scan Trainer hidden sheets, comments, and Trainer-associated sidecars and assert those texts do not appear.

The visible `Supplied model treatment` and `Alternative(s) to evaluate` are allowed because they are the guided exercise prompt.

- [ ] **Step 6: Add pair-contract assertions**

For revised demo assert:

```text
judgment cases: 1
Trainer judgment response cells: 3 blank/yellow/no-Note
Answer Key judgment response cells: 3 populated/yellow
formula SemanticMap: still 118
formula Check fresh: still 0 correct / 0 incorrect / 118 blank
```

- [ ] **Step 7: Run full Trainer tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record exact pass count.

---

## Task 6 — Preserve Step 7 behavior and document Step 8A accurately

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

- [ ] **Step 1: Update product wording without overclaiming**

Describe current capability as:

```text
Step 7 historical model construction:
- 25 historical schedule families across supplied fiscal years
- 118 formula practice cells in the five-year demo
- workbook-wide formula Check

Step 8A guided judgment:
- company-specific classification cases only when the authoritative classifier flags a supported ambiguity
- supplied reference treatment + explicit defensible alternative(s)
- learner treatment choice + short rationale + consequence explanation
- Answer Key shows model reasoning
- judgment responses are not automatically graded yet
- learner choices do not yet drive the main reformulated model
```

Explicitly state that this is a transition from supplied judgment to guided judgment, not independent analyst competence.

Do not claim normalization, earnings-quality analysis, or live alternative model reconciliation has been implemented.

- [ ] **Step 2: Regenerate the demo pair**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Expected formula output remains:

```text
Components resolved: 118
```

- [ ] **Step 3: Run full verification**

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

Expected end-to-end outcomes:

```text
Components resolved: 118
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
list --workbook: 25 historical schedule groups / 118 concrete formula cells
CLI surface remains {ingest,build,check,list}
Accounting Judgment sheet exists and contains exactly 1 guided case in the revised demo
```

- [ ] **Step 4: Perform final workbook audit**

Verify:

1. Trainer and Answer Key both contain `Accounting Judgment`.
2. Revised demo produces exactly one judgment case for `Operating lease liabilities`.
3. Supplied treatment is `Operating Long-Term Liability`.
4. Alternative is `Financial Liability`.
5. Trainer F/G/H response cells are blank/yellow/no-Note.
6. Answer Key F/G/H response cells are populated/yellow.
7. Answer Key rationale/consequence does not leak into Trainer hidden sheets/comments/sidecars.
8. `Condensed Financials` classifications remain populated and pair-identical.
9. Historical reformulation still reconciles for every period.
10. Formula SemanticMap remains 118 cells grouped into 25 families.
11. Fresh Check remains `0/0/118`.
12. Deferred forecast/valuation tabs remain four hidden placeholders.
13. Normal build still succeeds when `run_scenario()` is patched to fail.
14. No new public Hint/Reveal or judgment-grading CLI is introduced.

- [ ] **Step 5: Update `RESULT.md` with actual evidence**

Use this structure with observed values:

```text
Status: Step 8A complete — guided classification judgment with consequences

Implementation base:
- 9ddc60ab Step 7 correction

Historical model preservation:
- fiscal periods: 5
- conceptual formula families: 25
- concrete formula practice cells: 118
- fresh formula Check: 0 / 0 / 118

Guided judgment:
- demo judgment cases: 1
- case: Operating lease liabilities
- supplied treatment: Operating Long-Term Liability
- alternative: Financial Liability
- Trainer response cells blank/yellow/no Note: 3/3
- Answer Key response cells populated/yellow: 3/3
- judgment answer leakage: none
- judgment responses auto-graded: no
- learner judgment drives main model: no

Preservation:
- source values populated: yes
- main classifications populated: yes
- reformulation guardrails pass: yes
- forecast engine called by normal build: no
- deferred tabs: four hidden placeholders
- repeated cached formula Check: preserved

Tests:
- record every command above and exact pass count/result

Known deferred limitation:
- irregular/stub/interim period comparability still requires later robustness work

Unresolved:
- none OR exact blockers
```

- [ ] **Step 6: Stop**

Do not implement live learner reclassification, normalization, diagnostics, forecasting, or valuation in this checkpoint.

## Step 8A acceptance criteria

Step 8A is accepted only when all are true:

1. supported ambiguous classifier decisions encode explicit defensible category options and consequence teaching metadata;
2. unsupported ambiguity is not forced into a fake multiple-choice case;
3. guided cases are derived from actual company lines using stable `LineIdentity`, not hand-authored workbook coordinates;
4. zero-valued and explicitly overridden lines do not become cases;
5. revised demo exposes exactly one real lease-liability judgment case without changing aggregate historical economics;
6. both workbooks contain a visible `Accounting Judgment` sheet;
7. Trainer shows supplied treatment/alternatives but blanks learner-response cells;
8. Answer Key shows the model treatment, rationale, and consequence while acknowledging the treatment is not universal;
9. judgment answers/rationales do not leak into Trainer metadata/comments/sidecars;
10. main historical classifications remain supplied and continue to drive Step 7 formulas;
11. judgment responses are not falsely auto-graded as objectively correct/incorrect;
12. 25 historical formula families / 118 formula cells / formula Check behavior remain unchanged;
13. full suite, demo rebuild, leakage audit, forecast quarantine, and cached Check regressions pass;
14. docs frame Step 8A as guided judgment only, not independent accounting analysis.

---

# Locked follow-on roadmap — do not implement in Step 8A

## Step 8B — Live classification and normalization decisions

Design how learner-selected treatments can drive the reformulated model **without breaking equivalent-formula Check under alternative defensible inputs**. Add recurring/non-recurring treatment and earnings normalization only after that feedback-loop design is separately approved.

## Step 9 — Historical research diagnostics

Teach margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality signals.

## Step 10 — Cross-company and period-cadence robustness

Validate on materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad input robustness.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after the forecast layer is separately trusted.
