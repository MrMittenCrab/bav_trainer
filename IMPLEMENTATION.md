# Step 8A Correction — Guided Classification Judgment Without Answer Leakage

> **For Cursor:** Read `TARGET.md` first. The current branch tip before this plan is `818558688c53e44ed7e50cce9952bc118fc73524`, but that commit changed only `IMPLEMENTATION.md`; the accepted production implementation remains `9ddc60abb685d8d689b9f2c99983ea719e858d13` (`chat 7 correction`). Implement only the corrected Step 8A below using red/green TDD. Run the exact verification commands, update `RESULT.md`, regenerate the demo pair, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Add the first Level-2 accounting-judgment exercise without weakening the trusted Step 7 historical model, formula Check, reformulation identity, or Trainer/Answer-Key separation.

**Architecture:** Keep the authoritative historical model on the supplied reference classification. Add only a stable `judgment_code` to supported ambiguous classifier decisions; keep pedagogical alternatives/rationale/consequence text in a separate judgment-template registry. Derive company-specific `JudgmentCase` objects from real supplied lines, render them on a visible `Accounting Judgment` worksheet, and sanitize Trainer response cells structurally from the worksheet itself so answer removal never depends on transient in-memory case objects. Step 8A records and teaches a learner judgment; it does not yet drive the main reformulated model or formula Check.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `ClassificationDecision`, `BalanceSheetReformulation`, `LineIdentity`, `ReferenceModelBuilder`, `TrainingWorkbookGenerator`, and workbook-wide formula Check.

**Spec:** `TARGET.md`, especially `Level 2 — Analyst judgment`, the requirement to teach ambiguous treatments as alternatives with consequences, the material/applicable-topic constraint, and the requirement that resulting models remain auditable and reconcilable.

---

## Latest-commit review and corrections

Commit `81855868` is a planning-only commit: it modifies only `IMPLEMENTATION.md`. No production code or tests changed relative to `9ddc60ab`.

The prior Step 8A plan has six design problems that must be corrected before implementation:

1. **Deferred-tax `Exclude` was incorrectly treated as a safe guided alternative.** Moving a deferred-tax asset/liability from an asset/liability category to `Exclude` removes one side of the reformulation and can break `NOA - Net Debt = Equity`. Step 8A must only expose category alternatives that preserve the balance-sheet side and reformulation identity. Deferred-tax lines may remain `ambiguous=True`, but they are not guided cases yet.
2. **`ClassificationDecision.reason` is not an Answer-Key rationale.** Existing reasons such as `Lease liability — operating vs financial judgment` identify the ambiguity but do not explain why the reference model uses one treatment or what facts would justify the alternative.
3. **Pedagogical copy was placed in the classifier.** Adding `guided_options`, `judgment_topic`, and `consequence_note` directly to every `ClassificationDecision` duplicates teaching logic across concept and label branches and mixes accounting classification with workbook pedagogy. Use one semantic `judgment_code` in the classifier and a separate registry for teaching content.
4. **Trainer sanitization depended on a transient `judgment_cases` constructor argument.** Existing callers can instantiate `TrainingWorkbookGenerator(answer_key_path, semantic_map)` directly. If answer removal requires an extra in-memory argument, that path can copy Answer-Key judgment answers into the Trainer. Sanitization must derive response rows from the workbook structure itself.
5. **Case ordering and learner navigation were under-specified.** `JudgmentCase.order` must be dense after filtering, and the Trainer index must explicitly tell the learner that `Accounting Judgment` is separate from formula Check.
6. **The demo was described as containing a “real” case even though `DEMO_HK_Standardized.json` explicitly identifies itself as illustrative.** It is valid to add a representative synthetic lease line to the demo fixture, but production code must never synthesize a judgment line or claim that the demo is real company data.

### Superseded instructions from commit `81855868`

Do **not** implement any of the following from the previous plan:

- `guided_options`, `judgment_topic`, or `consequence_note` fields on `ClassificationDecision`;
- deferred-tax asset/liability `Operating ... | Exclude` guided exercises;
- `model_rationale = decision.reason`;
- a `judgment_cases` argument on `TrainingWorkbookGenerator` that is required for sanitization;
- wording that calls the illustrative demo judgment case “real”.

---

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve all accepted Step 7 behavior: five demo fiscal years, 25 conceptual historical formula families, and 118 concrete formula practice cells.
- Formula Check remains workbook-wide, yellow/green/red, non-disclosing, and cache-safe.
- Judgment response cells are not added to `ComponentSpec`, `COMPONENT_CATALOG`, `SemanticMap`, or formula Check.
- Main `Condensed Financials` classifications remain populated and continue to drive the historical model.
- Step 8A learner choices do not yet drive SUMIF/reformulation formulas.
- The learner must be told not to edit the supplied `Condensed Financials` classification column as part of this Step 8A exercise, because formula expected values still use the supplied reference classification.
- Only classifier decisions that are both `ambiguous=True` and carry a supported `judgment_code` may become guided cases.
- Guided alternatives must remain on the same accounting side as the reference treatment so the balance-sheet identity is preserved when the live-model step is added later: asset ↔ asset or liability ↔ liability.
- Zero-valued lines across all modeled periods do not become judgment cases.
- Explicit classification overrides suppress the guided case for that line in Step 8A.
- Do not invent cases from arbitrary labels, missing facts, or unsupported ambiguities.
- No normalization, recurring/non-recurring adjustments, earnings-quality diagnostics, lease accounting mechanics beyond classification discussion, SBC dilution, acquisition accounting, minority-interest modeling, forecasting, valuation, Hint/Reveal, VBA, or free-form automated grading.
- Keep exactly two user-facing workbooks: Trainer and Answer Key.
- Trainer must contain no Answer-Key rationale/consequence response text in visible response cells, hidden sheets, comments, or Trainer-associated sidecars.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Mark only supported classifier ambiguities with stable judgment codes

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Interfaces:**
- Extend `ClassificationDecision` with one field only:

```python
@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False
    judgment_code: str | None = None
```

- Existing `category`, `ambiguous`, `reason`, and `overridden` behavior remains unchanged.
- `judgment_code is not None` means the ambiguity is intentionally supported by the Step 8A teaching registry.

- [ ] **Step 1: Write failing supported-code tests**

Add exact tests for the following supported ambiguous decisions:

```text
Operating lease liability
  category: Operating Long-Term Liability
  judgment_code: lease_liability_operating_vs_financing

Pension / retirement-benefit obligation
  category: Operating Long-Term Liability
  judgment_code: pension_obligation_operating_vs_financing

Short-term investment
  category: Financial Asset
  judgment_code: short_term_investment_financial_vs_operating

Equity-method / associate / joint-venture investment
  category: Operating Long-Term Asset
  judgment_code: associate_investment_operating_vs_financial
```

For lease liability, cover both the label path and a concept path such as:

```python
LineItem(
    label="Operating lease liabilities",
    concept="lease_liability",
    values={P1: 50, P2: 60},
)
```

Assert each decision remains `ambiguous is True`.

- [ ] **Step 2: Write failing unsupported-ambiguity tests**

These decisions remain visibly ambiguous but must not become Step 8A cases:

```text
ROU / right-of-use asset
Deferred tax asset
Deferred tax liability
```

Assert:

```python
assert decision.ambiguous is True
assert decision.judgment_code is None
```

Reason: the current category taxonomy does not provide a safe generic alternative for the ROU asset, and `Exclude` is not an identity-preserving deferred-tax reclassification.

- [ ] **Step 3: Preserve override behavior**

An explicit `classificationOverrides` result must still satisfy:

```python
assert decision.overridden is True
assert decision.ambiguous is False
assert decision.judgment_code is None
```

- [ ] **Step 4: Run the failing tests**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "judgment_code or supported_ambiguity or unsupported_ambiguity" -v
```

Expected before implementation: FAIL because `judgment_code` does not exist.

- [ ] **Step 5: Implement the minimal classifier changes**

Set the four supported codes in both concept/label branches where applicable. Do not add pedagogical rationale/consequence text to `classification.py`.

- [ ] **Step 6: Run all classification tests**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
```

Record the exact pass count in `RESULT.md`.

---

## Task 2 — Centralize guided judgment teaching content and derive stable cases

**Files:**
- Create: `core/model/judgment.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**

Create:

```python
@dataclass(frozen=True)
class ClassificationJudgmentTemplate:
    topic: str
    options: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str


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

Create one registry:

```python
CLASSIFICATION_JUDGMENT_TEMPLATES: dict[str, ClassificationJudgmentTemplate]
```

and one constructor:

```python
def classification_judgment_cases(
    financials: StandardizedFinancials,
    periods: list[date],
    reformulation: BalanceSheetReformulation,
) -> tuple[JudgmentCase, ...]:
    ...
```

- [ ] **Step 1: Write failing registry tests**

The registry must contain exactly the four Step 8A codes from Task 1.

Every template must satisfy:

```python
assert len(template.options) >= 2
assert len(set(template.options)) == len(template.options)
assert all(option in BALANCE_SHEET_CATEGORIES for option in template.options)
```

The first option is always the current model/reference category.

Use these option pairs:

```text
lease_liability_operating_vs_financing
  Operating Long-Term Liability | Financial Liability

pension_obligation_operating_vs_financing
  Operating Long-Term Liability | Financial Liability

short_term_investment_financial_vs_operating
  Financial Asset | Operating Working Capital Asset

associate_investment_operating_vs_financial
  Operating Long-Term Asset | Financial Asset
```

- [ ] **Step 2: Encode actual model rationale, not the classifier reason**

Use concise, conditional language that explains the reference convention without presenting it as universal truth.

Required substance:

```text
Lease liability:
The reference model keeps the liability in operating long-term liabilities under its current lease convention. Treating it as a financial liability is also defensible when the lease obligation is viewed as debt-like financing.

Pension obligation:
The reference model keeps the obligation in operating long-term liabilities under its current employee-benefit convention. A financial-liability treatment is also defensible when the obligation is analyzed as debt-like funding.

Short-term investment:
The reference model treats a generic short-term investment as a financial asset absent evidence that it is required for operations. Operating-WC treatment requires company-specific evidence that the balance is necessary for normal operations.

Associate/JV investment:
The reference model treats the investment as an operating long-term asset when it is viewed as strategically tied to the operating business. Financial-asset treatment is defensible when the holding is primarily non-operating/investment in nature.
```

Do not state that one treatment is universally correct.

- [ ] **Step 3: Encode directional economic consequences**

The consequence text must explicitly say it is holding all other accounting treatment constant.

Required substance:

```text
Lease / pension liability:
Operating-liability treatment lowers NOLA/NOA; financial-liability treatment raises Net Debt by the same balance. Implied equity is unchanged from this classification switch alone, but RNOA versus FLEV/Spread interpretation changes.

Short-term investment:
Financial-asset treatment lowers Net Debt; operating-WC treatment raises NOWC/NOA by the same balance. Implied equity is unchanged from this classification switch alone, but operating-capital and leverage metrics change.

Associate/JV investment:
Operating-asset treatment raises NOLA/NOA; financial-asset treatment lowers Net Debt by the same balance. Implied equity is unchanged from this classification switch alone, but RNOA and leverage interpretation change.
```

Use one common non-answer learner prompt:

```text
Explain which reformulated balance(s) change under the alternative treatment and how that changes profitability/leverage interpretation.
```

- [ ] **Step 4: Write failing case-construction tests**

Case construction rules:

1. iterate `reformulation.detail_indices` in source order;
2. use the authoritative `ClassificationDecision` for that exact index;
3. require `decision.ambiguous is True`;
4. require `decision.overridden is False`;
5. require `decision.judgment_code is not None`;
6. if a non-null code is missing from the registry, raise a clear programming error instead of silently dropping it;
7. require at least one non-zero/non-`None` value across the supplied `periods`;
8. require `template.options[0] == decision.category`; fail fast if the registry and classifier drift;
9. `supplied_treatment = decision.category`;
10. `alternatives = template.options[1:]`;
11. `line_identity = line_identity(item).key()`;
12. stable ID:

```python
f"classification::{line_identity(item).key()}"
```

13. assign `order` densely **after filtering**, starting at 1.

Add tests proving:

- supported non-zero lease liability -> one case;
- unsupported ROU asset -> no case;
- unsupported deferred-tax line -> no case;
- supported zero-valued line -> no case;
- explicit override -> no case;
- if an earlier candidate is filtered out, remaining cases are ordered `1, 2, ...` with no gaps.

- [ ] **Step 5: Run the failing reference tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "judgment_case or judgment_template or guided_classification" -v
```

- [ ] **Step 6: Implement `core/model/judgment.py`**

Keep it coordinate-free. It owns pedagogical judgment semantics, not workbook row/column locations.

- [ ] **Step 7: Wire cases into `ReferenceModelBuilder`**

Immediately after `self.anchor = compute_anchor(...)`, set:

```python
self.judgment_cases = classification_judgment_cases(
    self.fin,
    self.periods,
    self.anchor.reformulation,
)
```

Do not add judgment cases to the formula component catalog or semantic map.

- [ ] **Step 8: Run focused reference tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "judgment or classification" -v
```

---

## Task 3 — Add one representative guided case to the illustrative demo fixture

**Files:**
- Modify: `example/DEMO_HK_Standardized.json`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- The demo remains explicitly illustrative/synthetic.
- Five fiscal years remain unchanged.
- Reported total assets, total liabilities, and total equity remain unchanged.
- The revised demo produces exactly one supported Step 8A case.

- [ ] **Step 1: Split the existing illustrative liability line**

Add:

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

Reduce `Other non-current liabilities` from:

```text
1305, 1456, 1593, 1716, 1825
```

to:

```text
1005, 1136, 1253, 1356, 1445
```

Do not change reported totals or any other line.

Both lines use the current reference category `Operating Long-Term Liability`, so Step 7 aggregate reference economics remain unchanged.

- [ ] **Step 2: Add exact demo assertions**

```python
assert len(builder.judgment_cases) == 1
case = builder.judgment_cases[0]
assert case.order == 1
assert case.label == "Operating lease liabilities"
assert case.supplied_treatment == "Operating Long-Term Liability"
assert case.alternatives == ("Financial Liability",)
```

Also assert the five-year build still resolves exactly 118 formula components.

- [ ] **Step 3: Re-run reformulation integrity on every demo period**

The same reported-equity, asset-detail, and liability-detail guardrails must pass for all five periods.

Production code must not contain logic that manufactures this lease line for companies whose supplied data do not contain it.

---

## Task 4 — Render one visible `Accounting Judgment` worksheet in the Answer Key

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Visible sheet name: `Accounting Judgment`.
- One row per `JudgmentCase`.
- The builder creates the complete Answer-Key version; Trainer sanitization is separate in Task 5.

- [ ] **Step 1: Write a failing sheet-layout test**

Required layout:

```text
A1  Accounting Judgment
A2  The supplied treatment is the model's reference treatment, not a universal accounting truth. Compare it with the listed alternative(s), choose the treatment you would defend, and explain the economic consequence.
A3  Record the judgment on this sheet. Do not edit the supplied classification in Condensed Financials for this Step 8A exercise. Formula Check does not grade these judgment responses.

row 4 headers:
Order
Line item
Topic
Supplied reference treatment
Alternative(s) to evaluate
Treatment to defend
Rationale
Economic consequence
```

For each case, row `5 + case.order - 1` contains:

```text
A  case.order
B  case.label
C  case.topic
D  case.supplied_treatment
E  comma-separated case.alternatives
F  case.supplied_treatment
G  case.model_rationale
H  case.model_consequence
```

The Answer Key contains the reference response in F:H but the A2 wording must make clear that it is not a universal truth.

- [ ] **Step 2: Add treatment dropdown validation**

Cell F on every case row uses an Excel list validation containing exactly:

```text
(case.supplied_treatment,) + case.alternatives
```

Do not expose unrelated BAV categories.

- [ ] **Step 3: Handle zero-case companies without inventing work**

Still create the visible sheet with title/instructions/headers and add this message below the header:

```text
No supported guided classification judgments were identified from the supplied company data.
```

The message row must not look like a numbered case row.

- [ ] **Step 4: Build the sheet in normal workbook order**

Call `_build_accounting_judgment(wb)` after the historical model sheets and before the four deferred hidden placeholders are created.

The sheet must not participate in `SemanticMap.validate_complete()`.

- [ ] **Step 5: Add readable column widths/wrapping**

Use existing workbook style conventions; do not create a separate visual design system. Long rationale/consequence columns must be wide enough and use wrapped text.

- [ ] **Step 6: Run focused sheet tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "accounting_judgment or judgment_sheet" -v
```

---

## Task 5 — Sanitize judgment answers structurally, independent of in-memory cases

**Files:**
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Keep the existing constructor compatible:

```python
TrainingWorkbookGenerator(answer_key_path, semantic_map=None)
```

Do **not** require a `judgment_cases` argument.

- [ ] **Step 1: Add a structural case-row helper**

Use fixed worksheet semantics, not transient model objects:

```python
JUDGMENT_SHEET = "Accounting Judgment"
JUDGMENT_FIRST_DATA_ROW = 5
JUDGMENT_RESPONSE_COLS = (6, 7, 8)


def _judgment_case_rows(ws):
    for row in range(JUDGMENT_FIRST_DATA_ROW, (ws.max_row or 0) + 1):
        order = ws.cell(row=row, column=1).value
        label = ws.cell(row=row, column=2).value
        if isinstance(order, int) and order >= 1 and label not in (None, ""):
            yield row
```

The zero-case message is therefore never treated as a response row.

- [ ] **Step 2: Decorate Answer-Key judgment responses after base styling**

In `generate()` call a new `_decorate_answer_key_judgment_cells(wb)` after `_apply_oshkosh_style(wb)`.

For each structural case row, F:G:H must be bright yellow and retain the populated reference response. Do not add formula-practice legacy Notes to these free-form judgment cells.

- [ ] **Step 3: Blank Trainer judgment responses after copying**

Call `_blank_trainer_judgment_cells(wb)` on the Trainer copy.

For each structural case row:

```text
F/G/H value: blank
F/G/H fill: bright yellow
F/G/H comment: none
```

All prompt/context columns A:E remain pair-identical.

Excel data validation in F must survive the copy/sanitization.

- [ ] **Step 4: Add the judgment workflow to the Trainer index**

Keep the existing formula schedule table unchanged. Add a concise instruction near the top of the `Trainer` sheet, separate from the 25 formula-family rows:

```text
Also complete Accounting Judgment when cases are present. These responses are not graded by Check; compare your reasoning with the matching Answer Key. Do not change the supplied Condensed Financials classification for this exercise.
```

Do not count the judgment sheet as a 26th formula schedule family.

- [ ] **Step 5: Write the regression that catches the previous leakage design**

Build an Answer Key containing one judgment case, then instantiate the generator using the old-compatible call with no case object:

```python
TrainingWorkbookGenerator(answer_key_path, semantic_map).generate(trainer_path)
```

Assert Trainer F:G:H are blank/yellow/no-comment. This test proves sanitization cannot be skipped because a caller forgot to pass `JudgmentCase` objects.

- [ ] **Step 6: Add leakage scanning**

Collect the Answer-Key `model_rationale` and `model_consequence` strings for the demo case. Assert those exact texts do not appear in:

- Trainer visible response cells;
- Trainer hidden sheets;
- Trainer comments/Notes;
- Trainer-associated `.component_map.json`, `.trainer.json`, or `.assumptions.json` sidecars.

The visible supplied treatment and alternative categories are intentional prompt content and are allowed.

- [ ] **Step 7: Add pair-contract assertions**

For the revised demo:

```text
judgment cases: 1
Trainer judgment response cells: 3 blank / yellow / no Note
Answer Key judgment response cells: 3 populated / yellow
Trainer treatment dropdown: present and contains exactly 2 allowed treatments
formula SemanticMap: 118
formula families: 25
fresh formula Check: 0 correct / 0 incorrect / 118 blank
```

- [ ] **Step 8: Run full Trainer tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record the exact pass count.

---

## Task 6 — Documentation, demo regeneration, and full verification

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

- [ ] **Step 1: Update product wording without overclaiming**

Describe current capability as:

```text
Step 7 historical model construction
- 25 historical schedule families across supplied fiscal years
- 118 formula practice cells in the five-year illustrative demo
- workbook-wide formula Check

Step 8A guided classification judgment
- cases only for supplied company lines that the classifier marks as both ambiguous and supported
- supplied reference treatment plus a defensible same-side alternative
- learner treatment choice, short rationale, and economic-consequence explanation
- Answer Key shows the reference model's reasoning, explicitly not a universal truth
- judgment responses are not automatically graded
- learner judgment does not yet drive the main reformulated model
```

Explicitly say the committed demo is illustrative/synthetic.

Do not claim deferred-tax judgment, normalization, earnings-quality analysis, live alternative-model reconciliation, forecasting, or valuation has been implemented.

- [ ] **Step 2: Regenerate the committed demo pair**

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
Accounting Judgment exists and contains exactly 1 guided demo case
```

- [ ] **Step 4: Perform the final workbook audit**

Verify all of the following:

1. Trainer and Answer Key both contain visible `Accounting Judgment`.
2. The illustrative demo produces exactly one case for `Operating lease liabilities`.
3. Supplied treatment is `Operating Long-Term Liability`.
4. Alternative is `Financial Liability`.
5. Trainer F:G:H are blank/yellow/no-Note.
6. Answer Key F:G:H contain the reference response and are yellow.
7. F treatment dropdown exists in both files and contains exactly the two allowed treatments.
8. Answer-Key rationale/consequence text does not leak into Trainer hidden sheets/comments/sidecars.
9. `Condensed Financials` classifications remain populated and pair-identical.
10. Historical reformulation reconciles for every period.
11. Formula SemanticMap remains 118 cells grouped into 25 families.
12. Fresh formula Check remains `0/0/118`.
13. `Accounting Judgment` is not counted as a formula schedule family and is not graded by Check.
14. Deferred forecast/valuation tabs remain four hidden placeholders.
15. Normal build still succeeds when `run_scenario()` is patched to fail.
16. No public Hint/Reveal or judgment-grading CLI is introduced.

- [ ] **Step 5: Update `RESULT.md` with observed evidence**

Use this structure with actual values:

```text
Status: Step 8A complete — guided classification judgment

Implementation base:
- 9ddc60ab Step 7 correction

Historical model preservation:
- fiscal periods: 5
- conceptual formula families: 25
- concrete formula practice cells: 118
- fresh formula Check: 0 / 0 / 118

Guided judgment:
- supported classifier templates: 4
- demo judgment cases: 1
- demo case: Operating lease liabilities
- supplied treatment: Operating Long-Term Liability
- alternative: Financial Liability
- Trainer response cells blank/yellow/no Note: 3/3
- Answer Key response cells populated/yellow: 3/3
- judgment answer leakage: none
- judgment responses auto-graded: no
- learner judgment drives main model: no
- deferred-tax lines exposed as Step 8A cases: no

Preservation:
- source values populated: yes
- main classifications populated: yes
- reformulation guardrails pass: yes
- forecast engine called by normal build: no
- deferred tabs: four hidden placeholders
- repeated cached formula Check: preserved

Tests:
- record each verification command and exact pass count/result

Known deferred limitations:
- deferred-tax/ROU alternatives require a later model design that preserves reconciliation
- irregular/stub/interim period comparability still requires later robustness work

Unresolved:
- none OR exact blockers
```

- [ ] **Step 6: Stop**

Do not begin live learner reclassification, normalization, diagnostics, forecasting, or valuation in this checkpoint.

---

## Step 8A acceptance criteria

Step 8A is accepted only when all are true:

1. `ClassificationDecision` adds only a stable optional `judgment_code` for Step 8A support; teaching copy stays outside the classifier.
2. Exactly four identity-preserving guided templates exist: lease liability, pension obligation, short-term investment, and associate/JV investment.
3. ROU and deferred-tax ambiguities remain visible to the classifier but are not exposed as Step 8A guided cases.
4. Case construction fails fast if classifier code and template registry drift.
5. Guided cases come only from supplied non-zero company lines using stable `LineIdentity`; production never invents a line.
6. Explicit overrides and unsupported ambiguities do not become cases.
7. Case order is dense after filtering.
8. Both workbooks contain a visible `Accounting Judgment` sheet.
9. Trainer shows prompt/context and allowed alternatives but blanks F:G:H.
10. Answer Key shows a reference treatment/rationale/consequence while stating that the treatment is not universal.
11. Trainer answer removal works through the existing two-argument `TrainingWorkbookGenerator` path and does not depend on in-memory `JudgmentCase` objects.
12. Judgment rationale/consequence text does not leak into Trainer metadata, hidden sheets, or comments.
13. Learner is explicitly told that judgment responses are not graded by Check and should not be applied by editing `Condensed Financials` in Step 8A.
14. The illustrative demo contains exactly one representative lease-liability case without changing aggregate historical economics.
15. Main historical classifications remain supplied and continue to drive the Step 7 model.
16. 25 historical formula families / 118 formula cells / fresh `0/0/118` Check behavior remain unchanged.
17. Full suite, demo rebuild, reformulation integrity, cached Check, sidecar hygiene, and forecast-quarantine regressions pass.
18. Documentation frames Step 8A as guided judgment only, not independent accounting competence.

---

# Locked follow-on roadmap — do not implement in Step 8A

## Step 8B — Live classification and normalization decisions

Design how learner-selected treatments can drive the reformulated model while preserving reconciliation and equivalent-formula Check. Revisit deferred taxes, ROU/lease treatment, recurring/non-recurring treatment, and earnings normalization only after that feedback-loop design is separately approved.

## Step 9 — Historical research diagnostics

Teach margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality signals.

## Step 10 — Cross-company and period-cadence robustness

Validate on materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad input robustness.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after the forecast layer is separately trusted.
