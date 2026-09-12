# Step 8A Repair — Conform Guided Judgment to the Approved Architecture

> **For Cursor:** Read `TARGET.md` first. The implementation base is commit `5904379e34db0932170ab06188246e4d4ca3ccd5` (`Step 8A guided classification judgment`). That commit implemented the superseded Step 8A design instead of the corrected architecture. Repair Step 8A only. Use red/green TDD, run the exact verification commands below, update `RESULT.md`, regenerate the demo pair, and stop. Do not begin Step 8B, normalization, research diagnostics, forecasting, or valuation. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Keep the useful Step 8A workbook surface from `5904379e` while removing the stale-design defects: pedagogical copy in the classifier, unsafe deferred-tax `Exclude` cases, non-rationale Answer-Key text, transient-object-dependent Trainer sanitization, modeled-period drift, and misleading learner instructions.

**Architecture:** `ClassificationDecision` owns only classification state plus an optional stable `judgment_code`. `core/model/judgment.py` owns all teaching templates and constructs `JudgmentCase` objects from supported supplied lines using the canonical model period axis. The Answer Key renders complete judgment responses; the Trainer sanitizes judgment response rows by reading workbook structure, never by relying on in-memory case objects. Formula Check remains unchanged and does not grade judgment responses.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `ClassificationDecision`, `BalanceSheetReformulation`, `LineIdentity`, `ReferenceModelBuilder`, `TrainingWorkbookGenerator`, and workbook-wide formula Check.

**Spec:** `TARGET.md`, especially Level 2 — Analyst judgment, ambiguous treatments as alternatives with consequences, material/applicable-topic gating, auditable/reconcilable models, and the requirement that free-form responses need not yet be automatically graded.

---

## Review of commit `5904379e`

The commit adds the visible `Accounting Judgment` sheet and preserves the Step 7 formula surface, but it is **not accepted as Step 8A complete** because it implements instructions that the prior corrected plan explicitly superseded.

Blocking problems:

1. `ClassificationDecision` contains `guided_options`, `judgment_topic`, and `consequence_note`; pedagogical content is duplicated in concept and label classifier branches instead of being centralized.
2. Deferred-tax assets/liabilities are exposed as `Operating ... | Exclude` guided cases. `Exclude` removes one side of the current reformulation and is not a safe generic Step 8A reclassification.
3. `JudgmentCase.model_rationale` is populated from `ClassificationDecision.reason`; strings such as `Lease liability — operating vs financial judgment` identify ambiguity but do not explain why the reference model chose its treatment.
4. `TrainingWorkbookGenerator(..., judgment_cases=...)` is required to blank judgment answers. A caller using the existing two-argument constructor can copy Answer-Key judgment responses into the Trainer.
5. `classification_judgment_cases()` derives its non-zero test from all `financials.periods`, while the historical model uses `canonical_fiscal_periods()`. An interim-only non-zero value can therefore create a case even when all modeled annual values are zero.
6. `TRAINER_INDEX_INSTRUCTION` still says Check validates every yellow cell even though yellow judgment response cells are intentionally excluded from Check. The workbook also fails to tell the learner not to edit the supplied `Condensed Financials` classification during Step 8A.
7. Tests encode the stale design, including deferred-tax guided alternatives, so the recorded `109 passed` result does not establish conformance to the approved Step 8A architecture.

Do not move to Step 8B until every repair below is complete.

---

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve five demo fiscal years, 25 historical formula families, and 118 concrete formula practice cells.
- Formula Check remains workbook-wide for formula cells only: blank yellow, correct green, incorrect red, non-disclosing, cache-safe.
- Judgment responses remain outside `ComponentSpec`, `COMPONENT_CATALOG`, `SemanticMap`, and formula Check.
- Main `Condensed Financials` classifications remain populated and continue to drive the historical model.
- Step 8A learner choices do not yet drive SUMIF/reformulation formulas.
- Guided alternatives must preserve accounting side under the current taxonomy: asset ↔ asset or liability ↔ liability.
- ROU assets and deferred-tax balances may remain `ambiguous=True`, but they are not Step 8A guided cases.
- Zero-valued lines across the **modeled canonical periods** do not become cases.
- Explicit classification overrides suppress the guided case.
- Production code never invents a company line or judgment case.
- Keep exactly two user-facing workbooks: Trainer and Answer Key.
- Trainer must contain no Answer-Key rationale/consequence response text in visible response cells, hidden sheets, comments, or Trainer-associated sidecars.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Repair the classifier boundary

**Files:**
- Modify: `core/model/classification.py`
- Modify: `core/tests/test_classification.py`

**Interfaces:**

Replace the current Step 8A fields with exactly one new semantic field:

```python
@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False
    judgment_code: str | None = None
```

Delete `_guided_decision()`, `guided_options`, `judgment_topic`, and `consequence_note` from the classifier.

Supported Step 8A codes:

```text
lease_liability_operating_vs_financing
pension_obligation_operating_vs_financing
short_term_investment_financial_vs_operating
associate_investment_operating_vs_financial
```

Exact mappings:

```text
Operating lease liability
  category: Operating Long-Term Liability
  ambiguous: True
  judgment_code: lease_liability_operating_vs_financing

Pension / retirement-benefit obligation
  category: Operating Long-Term Liability
  ambiguous: True
  judgment_code: pension_obligation_operating_vs_financing

Short-term investment
  category: Financial Asset
  ambiguous: True
  judgment_code: short_term_investment_financial_vs_operating

Equity-method / associate / JV investment
  category: Operating Long-Term Asset
  ambiguous: True
  judgment_code: associate_investment_operating_vs_financial
```

Unsupported Step 8A ambiguities:

```text
ROU / right-of-use asset
Deferred tax asset
Deferred tax liability
```

They must satisfy:

```python
assert decision.ambiguous is True
assert decision.judgment_code is None
```

Explicit overrides must satisfy:

```python
assert decision.overridden is True
assert decision.ambiguous is False
assert decision.judgment_code is None
```

### TDD steps

- [ ] Replace the stale guided-option tests with failing `judgment_code` tests covering both label and concept paths for lease liability and associate/JV investment.
- [ ] Add failing tests proving deferred-tax and ROU decisions remain ambiguous but have `judgment_code is None`.
- [ ] Add/retain the override suppression regression.
- [ ] Run the focused tests and confirm they fail against `5904379e`:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "judgment_code or deferred_tax or rou or override" -v
```

- [ ] Implement the minimal classifier change. Do not put topic, options, rationale, or consequence prose in `classification.py`.
- [ ] Run all classification tests:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
```

Record the exact pass count in `RESULT.md`.

---

## Task 2 — Centralize judgment templates and use the canonical modeled periods

**Files:**
- Replace/modify: `core/model/judgment.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`

**Interfaces:**

Use:

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

Create exactly one registry:

```python
CLASSIFICATION_JUDGMENT_TEMPLATES: dict[str, ClassificationJudgmentTemplate]
```

with exactly four entries, keyed by the four supported `judgment_code` values.

Options:

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

Reference rationale text must explain the convention rather than merely name the ambiguity:

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

Use the common learner prompt:

```text
Explain which reformulated balance(s) change under the alternative treatment and how that changes profitability/leverage interpretation.
```

Directional consequence text, explicitly holding all other accounting treatment constant:

```text
Lease / pension liability:
Operating-liability treatment lowers NOLA/NOA; financial-liability treatment raises Net Debt by the same balance. Implied equity is unchanged from this classification switch alone, but RNOA versus FLEV/Spread interpretation changes.

Short-term investment:
Financial-asset treatment lowers Net Debt; operating-WC treatment raises NOWC/NOA by the same balance. Implied equity is unchanged from this classification switch alone, but operating-capital and leverage metrics change.

Associate/JV investment:
Operating-asset treatment raises NOLA/NOA; financial-asset treatment lowers Net Debt by the same balance. Implied equity is unchanged from this classification switch alone, but RNOA and leverage interpretation change.
```

Change the constructor signature to:

```python
def classification_judgment_cases(
    financials: StandardizedFinancials,
    periods: list[date],
    reformulation: BalanceSheetReformulation,
) -> tuple[JudgmentCase, ...]:
    ...
```

Case rules:

1. iterate `reformulation.detail_indices` in source order;
2. require `decision.ambiguous is True`;
3. require `decision.overridden is False`;
4. require `decision.judgment_code is not None`;
5. if a non-null code is absent from the registry, raise a clear programming error;
6. require at least one non-zero/non-`None` value across the supplied **canonical `periods` argument**;
7. require `template.options[0] == decision.category`, otherwise raise a clear programming error;
8. assign dense `order = 1, 2, ...` only after filtering;
9. use `line_identity(item).key()` for stable identity;
10. `supplied_treatment = decision.category` and `alternatives = template.options[1:]`.

Wire from `ReferenceModelBuilder` exactly as:

```python
self.judgment_cases = classification_judgment_cases(
    self.fin,
    self.periods,
    self.anchor.reformulation,
)
```

### TDD steps

- [ ] Add registry invariants: exactly four entries, unique options, all options in `BALANCE_SHEET_CATEGORIES`, first option matches the reference category.
- [ ] Add case tests for supported lease, unsupported ROU, unsupported deferred tax, explicit override, zero-valued supported line, and dense ordering after filtering.
- [ ] Add a period-axis regression: construct annual periods whose supported line is zero plus an interim period where it is non-zero; `ReferenceModelBuilder` must produce no case because the interim period is outside the modeled annual axis.
- [ ] Run focused tests and verify red state:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "judgment or interim or canonical" -v
```

- [ ] Implement the registry/constructor and builder wiring.
- [ ] Run focused reference tests again and record results.

---

## Task 3 — Make Trainer sanitization structural and correct the learner workflow

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/tests/test_trainer.py`

**Required Answer-Key sheet layout:**

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

For each case row F:G:H contain the Answer-Key reference response and are bright yellow. F keeps the exact dropdown `(case.supplied_treatment,) + case.alternatives`. Long text cells use wrap-text formatting.

### Remove the transient sanitization dependency

Restore constructor compatibility:

```python
TrainingWorkbookGenerator(answer_key_path, semantic_map=None)
```

Remove the `judgment_cases` constructor argument and `self.judgment_cases`.

Use workbook structure instead:

```python
JUDGMENT_FIRST_DATA_ROW = 5
JUDGMENT_RESPONSE_COLS = (6, 7, 8)


def _judgment_case_rows(ws):
    for row in range(JUDGMENT_FIRST_DATA_ROW, (ws.max_row or 0) + 1):
        order = ws.cell(row=row, column=1).value
        label = ws.cell(row=row, column=2).value
        if isinstance(order, int) and order >= 1 and label not in (None, ""):
            yield row
```

`_decorate_answer_key_judgment_cells()` and `_blank_trainer_judgment_cells()` must iterate this helper, not in-memory cases.

Zero-case message rows must not be treated as response rows.

### Correct the Trainer instructions

Replace the misleading instruction that Check validates every yellow cell. The Trainer must explicitly communicate both workflows. Use this substance:

```text
Complete each historical formula schedule left-to-right in dependency order. Run Check to validate the yellow formula cells. Also complete Accounting Judgment when cases are present; those responses are not graded by Check. Compare them with the matching Answer Key. Do not edit the supplied Condensed Financials classification for this Step 8A exercise.
```

Do not count `Accounting Judgment` as a 26th formula-family row.

### TDD steps

- [ ] Add the regression that exposes the current leak: build an Answer Key with one case, then call `TrainingWorkbookGenerator(answer_key_path, semantic_map).generate(trainer_path)` without case objects. Against `5904379e`, Trainer F:G:H must incorrectly remain populated, proving the test is red.
- [ ] Add assertions for A2/A3 wording and the revised row-4 headers.
- [ ] Add assertions that the Trainer instruction says judgment responses are not graded by Check and not to edit `Condensed Financials` classifications.
- [ ] Add zero-case structural-sanitization coverage.
- [ ] Implement the structural row helper, remove the constructor dependency, and preserve dropdown validation on Trainer F cells.
- [ ] Add leakage scanning for Answer-Key rationale/consequence across Trainer visible response cells, hidden sheets, comments, and Trainer sidecars.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "judgment or leakage or instruction" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record exact pass counts.

---

## Task 4 — Correct tests/docs, regenerate artifacts, and verify Step 8A before moving on

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

### Documentation corrections

State the current capability as:

```text
Step 7 historical model construction
- 25 historical schedule families across supplied fiscal years
- 118 formula practice cells in the five-year illustrative demo
- workbook-wide formula Check

Step 8A guided classification judgment
- only supplied lines whose ambiguity has one of four supported judgment codes become cases
- supplied reference treatment + one defensible same-side alternative
- learner chooses a treatment, rationale, and consequence explanation
- Answer Key presents the reference convention and reasoning, not a universal truth
- judgment responses are not graded by Check
- learner choices do not yet drive the main reformulated model
- deferred-tax and ROU ambiguities are not Step 8A guided cases
```

Fix any sentence implying all yellow cells are formula-checked. Keep the demo described as illustrative/synthetic.

### Full verification

Run all commands fresh:

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

Required end-state evidence:

```text
five modeled fiscal years
25 historical formula families
118 concrete formula practice cells
fresh Check = 0 correct / 0 incorrect / 118 blank
exactly 4 supported judgment templates
illustrative demo judgment cases = 1
case = Operating lease liabilities
reference treatment = Operating Long-Term Liability
alternative = Financial Liability
Trainer F:G:H = 3 blank/yellow/no Note
Answer Key F:G:H = 3 populated/yellow
Trainer direct-constructor sanitization regression = pass
judgment rationale/consequence leakage = none
deferred-tax Step 8A cases = 0
ROU Step 8A cases = 0
Accounting Judgment excluded from formula Check/list family count
CLI remains {ingest,build,check,list}
normal build does not execute deferred forecast engine
```

Update `RESULT.md` only with the values actually observed from these fresh commands. Do not retain `Unresolved: none` if any command or audit is incomplete.

### Stop condition

Step 8A is accepted only after all above evidence is recorded. Then stop. Do not implement Step 8B in the same checkpoint.

---

## Locked follow-on roadmap — do not implement now

### Step 8B — Live classification and normalization decisions

Design how learner-selected treatments can drive the reformulated model while preserving reconciliation and equivalent-formula Check. Revisit deferred taxes, ROU/lease treatment, recurring/non-recurring treatment, and earnings normalization only after Step 8A is separately accepted.

### Step 9 — Historical research diagnostics

Teach margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality signals.

### Step 10 — Cross-company and period-cadence robustness

Validate on materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad input robustness.

### Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

### Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after the forecast layer is separately trusted.
