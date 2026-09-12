# Step 8B1 — Live Classification Choices With Judgment-Aware Check

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `79d2357f073272015a63572537f13a84ae08e754` (`8A corrected`). Implement only Step 8B1 below using red/green TDD. Preserve Step 8A guided reasoning, the Step 7 formula surface, workbook-wide Check behavior, and Trainer/Answer-Key separation. Do not implement normalization, earnings-quality diagnostics, forecasting, valuation, or Step 8B2. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make a learner's supported Step 8A classification choice actually drive the historical reformulated model while keeping equivalent-formula Check correct under either defensible treatment.

**Architecture:** Keep `Accounting Judgment` as the learner's only classification-input surface. For supported cases, the corresponding `Condensed Financials` classification cell becomes a formula that uses the learner treatment when entered and otherwise falls back to the supplied reference treatment. Add an Answer-Key-only hidden `_CheckContext` containing only model source facts, setup overrides, and judgment bindings; it must not contain formulas, expected values, hints, or rationale/consequence answers. During Check, reconstruct the historical Python model from that context plus the learner's current treatment selections and compute judgment-conditioned expected values for all 25 historical formula families. Exact-formula Check remains unchanged; cached-value Check uses the dynamic expected value so equivalent formulas remain valid under alternative defensible classifications.

**Tech Stack:** Python, dataclasses, JSON, pytest, openpyxl, existing `StandardizedFinancials`, `ReferenceModelBuilder`, `JudgmentCase`, `compute_anchor`, `SemanticMap`, `TrainingWorkbookGenerator`, and OOXML-preserving Check.

**Spec:** `TARGET.md`, especially Level 2 — Analyst judgment: selected classification decisions become exercises, the learner must choose and defend treatments **and reconcile the resulting model**, ambiguous treatments are alternatives with consequences rather than one universal answer, and Check must remain non-disclosing and trustworthy.

## Review of commit `79d2357e`

The Step 8A repair now matches the approved architecture at code level:

- `ClassificationDecision` contains only classification state plus `judgment_code`;
- teaching content is centralized in a four-template registry;
- ROU and deferred-tax lines remain ambiguous but are not Step 8A guided cases;
- case construction uses the canonical modeled period axis;
- Trainer judgment sanitization is structural and works through the two-argument generator path;
- Trainer instructions distinguish formula Check from ungraded judgment responses;
- the illustrative demo still exposes one lease-liability case and 118 formula cells.

`RESULT.md` records 115 passing tests plus successful build/check/list verification. GitHub has no attached CI status for this commit, so treat those recorded local test results as implementation evidence rather than independent CI evidence.

No blocking code-review defect remains from Step 8A. The next dependency is live model reconciliation: today the learner can choose and explain an alternative, but the choice deliberately does not affect `Condensed Financials` or the expected values used by Check.

## Why Step 8B is split

The roadmap previously grouped live classification and normalization together, but they are separate accounting subsystems. Live balance-sheet classification changes category aggregates and DuPont denominators; earnings normalization changes income-statement economics and potentially NOPAT. Combining both would make Check-context design, reconciliation, and failure diagnosis unnecessarily broad.

Step 8B1 therefore implements **live supported classification only**. Step 8B2 will add recurring/non-recurring and normalization judgments after the judgment-conditioned feedback loop is trusted.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve five illustrative demo fiscal years, 25 historical formula families, and 118 concrete historical formula practice cells.
- Preserve the four Step 8A supported judgment templates exactly: lease liability, pension obligation, short-term investment, associate/JV investment.
- ROU and deferred-tax balances remain unsupported guided ambiguities in Step 8B1.
- Learner treatment is entered only in `Accounting Judgment` column F; do not turn the `Condensed Financials` classification column itself into an editable quiz surface.
- Blank treatment means "use the supplied reference treatment" so a fresh Trainer remains a coherent Step 7/8A model.
- A supported alternative may only be same-side: asset ↔ asset or liability ↔ liability. Do not introduce `Exclude` alternatives.
- Judgment rationale and consequence text remain free-form and ungraded.
- Formula Check remains one workbook-wide action across the same 118 formula cells.
- Check must still accept both the exact Answer-Key formula and an equivalent formula whose cached result matches the **current learner treatment state**.
- Check remains non-disclosing: no formulas, expected values, hints, rationales, or answer text are printed or inserted into the Trainer.
- The hidden Check context is stored only in the Answer Key and removed from the Trainer copy.
- The Check context must not contain formula answers, expected values, formula hints, or Step 8A rationale/consequence answer text.
- Normal build must not execute the dormant forecast/scenario engine.
- No normalization, recurring/non-recurring adjustments, earnings-quality diagnostics, forecasting, valuation, Hint/Reveal, VBA, or automated free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Add one shared model-data serialization contract and an Answer-Key Check context

**Files:**
- Create: `core/data/standardized_io.py`
- Create: `core/trainer/check_context.py`
- Modify: `core/model/judgment.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/__main__.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**

Create model-relevant StandardizedFinancials serialization:

```python
def standardized_to_payload(fin: StandardizedFinancials) -> dict:
    ...


def standardized_from_payload(payload: dict) -> StandardizedFinancials:
    ...
```

The payload must preserve:

```text
ticker
company_name
currency
units
jurisdiction
stock_code
periods: end_date, label, is_interim
income_statement: label, concept, period values
balance_sheet: label, concept, period values
cash_flow: label, concept, period values
metadata
```

Do not serialize `source_doc` absolute paths into the Check context. They are not needed for model recomputation and can contain machine-specific information.

Use ISO `YYYY-MM-DD` keys for every date. `standardized_from_payload(standardized_to_payload(fin))` must preserve every modeled line identity and numeric value.

Extend `JudgmentCase` with one stable override selector:

```python
@dataclass(frozen=True)
class JudgmentCase:
    id: str
    order: int
    line_identity: str
    override_selector: str
    label: str
    topic: str
    supplied_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str
```

Construct the selector from the actual supplied line:

```python
ident = line_identity(item)
override_selector = (
    f"concept:{ident.concept}"
    if ident.concept
    else f"label:{item.label}"
)
```

Create Check-context types:

```python
CHECK_CONTEXT_SHEET = "_CheckContext"
CHECK_CONTEXT_MAGIC = "BAV_CHECK_CONTEXT_V1"
CHECK_CONTEXT_CHUNK_SIZE = 30000

@dataclass(frozen=True)
class JudgmentBinding:
    order: int
    worksheet_row: int
    case_id: str
    line_identity: str
    override_selector: str
    reference_treatment: str
    allowed_treatments: tuple[str, ...]

@dataclass(frozen=True)
class CheckContext:
    schema_version: int
    source_payload: dict
    modeled_periods: tuple[str, ...]
    base_classification_overrides: dict[str, str]
    judgment_bindings: tuple[JudgmentBinding, ...]
```

Create:

```python
def build_check_context(
    financials: StandardizedFinancials,
    periods: list[date],
    assumptions: dict,
    judgment_cases: tuple[JudgmentCase, ...],
) -> CheckContext:
    ...


def embed_check_context_sheet(wb, context: CheckContext) -> None:
    ...


def load_check_context(answer_key_path: Path) -> CheckContext | None:
    ...
```

`embed_check_context_sheet()` must:

1. delete any pre-existing `_CheckContext` sheet;
2. create a hidden `_CheckContext` sheet;
3. put `BAV_CHECK_CONTEXT_V1` in `A1`;
4. JSON-serialize the context with deterministic key ordering;
5. split the JSON into chunks of at most 30,000 characters and write them down column A starting at `A2`.

`load_check_context()` must return `None` when the sheet does not exist so pre-Step-8B workbooks keep the old fixed-expected Check behavior. If the sheet exists with a wrong magic/version or malformed JSON, raise a clear `ValueError` rather than silently falling back.

`build_check_context()` judgment bindings must use:

```python
worksheet_row = 4 + case.order
allowed_treatments = (case.supplied_treatment,) + case.alternatives
```

and must not serialize:

```text
model_rationale
model_consequence
consequence_prompt
SemanticMap formulas
SemanticMap expected values
formula hints
```

### TDD steps

- [ ] Add a round-trip test using the illustrative demo:

```python
payload = standardized_to_payload(data)
round_tripped = standardized_from_payload(payload)
assert [line_identity(x) for x in round_tripped.balance_sheet] == [
    line_identity(x) for x in data.balance_sheet
]
assert round_tripped.period_dates() == data.period_dates()
```

Also assert every statement value survives exactly.

- [ ] Add a Check-context contract test that builds the demo Answer Key and asserts `_CheckContext` is hidden, the magic is present, and `load_check_context()` returns one binding for `Operating lease liabilities` with:

```python
binding.worksheet_row == 5
binding.reference_treatment == "Operating Long-Term Liability"
binding.allowed_treatments == (
    "Operating Long-Term Liability",
    "Financial Liability",
)
binding.override_selector == "concept:lease_liability"
```

- [ ] Scan the raw loaded context JSON and assert it contains none of the demo case's `model_rationale`, `model_consequence`, formula strings, expected values serialized as component fields, or formula hints.

- [ ] Add `_CheckContext` to Trainer sanitization and assert the Trainer workbook does not contain that sheet.

- [ ] Replace the private CLI ingestion serialization helpers with `standardized_to_payload()` without changing CLI JSON behavior. Add/retain an ingest round-trip regression proving `concept` survives export/reload.

- [ ] Run the new tests before implementation and verify failure:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "standardized_payload or check_context or judgment_selector" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "check_context" -v
```

- [ ] Implement the serialization/context layer and rerun those tests until green.

---

## Task 2 — Make the learner treatment drive `Condensed Financials`

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**

Build one mapping in `ReferenceModelBuilder.__init__` after `self.judgment_cases` exists:

```python
self._judgment_row_by_identity = {
    case.line_identity: 4 + case.order
    for case in self.judgment_cases
}
```

When `_build_condensed()` renders each balance-sheet detail row, keep ordinary classifications literal and validated as before. For a supported judgment-case line, make column B a non-practice formula driven by `Accounting Judgment`:

```excel
=IF('Accounting Judgment'!$F$5="",'Accounting Judgment'!$D$5,'Accounting Judgment'!$F$5)
```

Use the actual case row instead of hard-coding `5`.

Do not add the ordinary eight-category data validation to these formula-driven classification cells. The only learner input is the restricted dropdown in `Accounting Judgment!F`.

Because the formula falls back to column D when F is blank:

```text
fresh Trainer -> supplied reference classification
learner selects alternative -> alternative classification
learner clears F -> supplied reference classification again
```

The existing category `SUMIF` formulas then become live automatically without changing their formula text.

Update the Step 8B1 instructions shown on both workbooks. Use this substance in `Accounting Judgment!A3`:

```text
Choose a treatment in column F. That choice drives the matching Condensed Financials classification and downstream historical schedules; leaving it blank uses the supplied reference treatment. Enter your rationale and economic consequence in G:H. Formula Check grades formula cells against the treatment currently selected here; it does not grade the judgment response itself. Do not edit the linked Condensed Financials classification cell directly.
```

Update `TRAINER_INDEX_INSTRUCTION` consistently. Do not imply that every yellow cell is graded.

### TDD steps

- [ ] Add a test that locates the demo lease line in `Condensed Financials` and asserts its column-B cell contains a formula referencing both `Accounting Judgment!F5` and `Accounting Judgment!D5`.

- [ ] Assert an ordinary non-judgment line, such as `Bank borrowings`, still contains a literal classification and retains normal category data validation.

- [ ] Assert the judgment-driven column-B cell itself is not in `SemanticMap`, is not yellow practice, and is pair-identical between Trainer and Answer Key.

- [ ] Assert the treatment dropdown remains on `Accounting Judgment!F5` in both workbooks and contains exactly the two allowed treatments.

- [ ] Add a synthetic two-case workbook (for example lease liability plus short-term investment) and assert each classification row links to the correct judgment row with no coordinate collision.

- [ ] Run focused tests before implementation:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "live_classification or judgment_link" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "judgment_link or treatment_dropdown" -v
```

- [ ] Implement the live links and revised instructions. Do not change the 118 formula-practice coordinates.

---

## Task 3 — Add one authoritative dynamic expected-value resolver for all 25 historical families

**Files:**
- Create: `core/model/historical_expected.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**

Create:

```python
def historical_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    ...


def expected_value_for_component(
    anchor: AnchorMetrics,
    component: ResolvedComponent,
) -> float | str | None:
    ...
```

`historical_expected_series()` must define all 25 current family IDs exactly:

```python
{
    "revenue_link": tuple(anchor.historical.revenue),
    "net_income_link": tuple(anchor.historical.net_income),
    "effective_tax_rate_fy": tuple(anchor.historical.effective_tax_rate),
    "net_interest_fy": tuple(anchor.historical.net_interest),
    "net_interest_after_tax_fy": tuple(anchor.historical.net_interest_after_tax),
    "nopat_fy": tuple(anchor.historical.nopat),
    "owca_agg": anchor.reformulation.category_totals["Operating Working Capital Asset"],
    "owcl_agg": anchor.reformulation.category_totals["Operating Working Capital Liability"],
    "nowc_agg": anchor.reformulation.nowc,
    "olta_agg": anchor.reformulation.category_totals["Operating Long-Term Asset"],
    "oltl_agg": anchor.reformulation.category_totals["Operating Long-Term Liability"],
    "nola_agg": anchor.reformulation.nola,
    "noa_agg": anchor.reformulation.noa,
    "financial_assets_agg": anchor.reformulation.category_totals["Financial Asset"],
    "financial_liabilities_agg": anchor.reformulation.category_totals["Financial Liability"],
    "net_debt": anchor.reformulation.net_debt,
    "equity_reformulated_fy": anchor.reformulation.implied_equity,
    "sales_growth": tuple(anchor.dupont["Sales Growth"]),
    "nopat_margin": tuple(anchor.dupont["NOPAT Margin"]),
    "rnoa": tuple(anchor.dupont["RNOA"]),
    "after_tax_cod": tuple(anchor.dupont["After-tax CoD"]),
    "spread": tuple(anchor.dupont["Spread"]),
    "flev": tuple(anchor.dupont["FLEV"]),
    "roe_decomp": tuple(anchor.dupont["ROE (decomposed)"]),
    "actual_roe": tuple(anchor.dupont["Actual ROE"]),
}
```

`expected_value_for_component()` must:

1. require `component.family_id` to exist in the mapping;
2. require `component.period_index` to be non-null for historical components;
3. return `series[component.period_index]`;
4. raise a clear programming error for an unknown family or invalid index instead of silently returning the fixed semantic-map expected value.

This module is the dynamic expected-value bridge for Check. Do not put workbook coordinates or formula strings in it.

### TDD steps

- [ ] Build the demo under its reference treatment and assert for **all 118 components**:

```python
anchor = ReferenceModelBuilder(data).anchor
for comp in smap.all_ordered():
    assert expected_value_for_component(anchor, comp) == pytest.approx(comp.expected_value)
```

Handle non-float values with exact equality; current historical components should remain numeric.

- [ ] Assert `set(historical_expected_series(anchor)) == {f.id for f in COMPONENT_CATALOG}` so catalog additions cannot silently bypass dynamic Check.

- [ ] Recompute the demo anchor with:

```python
classification_overrides={
    "concept:lease_liability": "Financial Liability",
}
```

and assert at least these families change versus the reference state:

```text
oltl_agg
financial_liabilities_agg
nola_agg
noa_agg
net_debt
rnoa
after_tax_cod
spread
flev
roe_decomp
```

while reformulated equity remains reconciled to reported equity.

- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "historical_expected or alternative_classification" -v
```

- [ ] Implement the resolver and rerun until green.

---

## Task 4 — Make Check judgment-aware without weakening exact/equivalent formula behavior

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/check_context.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**

Add a helper that reads the learner's current treatment state from the Trainer:

```python
def classification_overrides_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    ...
```

Start from a copy of:

```python
context.base_classification_overrides
```

For each `JudgmentBinding`:

```python
cell_value = trainer_wb["Accounting Judgment"].cell(
    row=binding.worksheet_row,
    column=6,
).value
```

Interpret:

```text
blank / whitespace -> binding.reference_treatment
one of binding.allowed_treatments -> that treatment
anything else -> ValueError naming only the judgment row and invalid treatment
```

Then set:

```python
overrides[binding.override_selector] = selected_treatment
```

Do not infer a treatment from rationale text or from `Condensed Financials` formulas.

When `_CheckContext` exists, `check_workbook()` must:

1. load the normal Answer-Key `SemanticMap`;
2. load `CheckContext` from the matching Answer Key;
3. reconstruct `StandardizedFinancials` from `context.source_payload`;
4. parse `context.modeled_periods` into `date` objects;
5. assert those periods equal `canonical_fiscal_periods(financials)`;
6. read the current learner treatment selections from the Trainer workbook;
7. compute:

```python
anchor = compute_anchor(
    financials,
    periods,
    classification_overrides=current_overrides,
)
```

8. compute one dynamic expected value per `ResolvedComponent` with `expected_value_for_component()`;
9. keep the current exact-formula fast path unchanged;
10. for a non-exact formula with a cached value, compare against the dynamic expected value rather than `comp.expected_value`.

For a legacy Answer Key without `_CheckContext`, preserve the current fixed behavior exactly:

```python
expected = comp.expected_value
```

Do not add treatment choices to `CheckSummary` or CLI output.

### TDD steps

- [ ] **Reference-state parity:** build a fresh demo Trainer with F5 blank. Fill a sample of exact and equivalent formulas. Assert Check outcomes match pre-Step-8B behavior and fresh workbook remains `0 correct / 0 incorrect / 118 blank`.

- [ ] **Alternative exact-formula regression:** set `Accounting Judgment!F5 = "Financial Liability"`, enter the exact Answer-Key formula for an affected aggregate, and assert it is correct. This confirms the live choice does not break the exact-formula path.

- [ ] **Alternative equivalent-formula regression:** choose an affected component such as latest-period `net_debt`. Compute its alternative expected value from the Python anchor and prove it differs from `comp.expected_value`. Inject a different formula plus that alternative cached value using the existing OOXML helper. Assert Check marks it green. This test must fail against the fixed expected-value checker.

- [ ] **Wrong-reference-value regression:** under the alternative treatment, inject a non-exact formula whose cached value equals the old reference `comp.expected_value` rather than the alternative value. Assert Check marks it red.

- [ ] **Repeated Check regression:** the equivalent alternative formula remains green on two consecutive Checks and its cached value survives both runs.

- [ ] **Two-case combination regression:** build synthetic data with two supported cases, choose both alternatives, compute the combined Python anchor, and verify an equivalent formula is graded against the combined state rather than either single-case state.

- [ ] **Invalid treatment regression:** replace an F-cell value with a category not in that binding's allowed treatments. Assert Check raises `ValueError` before applying any fill updates. The error may name the row and invalid value but must not disclose an expected formula/value/rationale.

- [ ] **Legacy compatibility:** remove `_CheckContext` from a copied pre-Step-8B-style Answer Key and assert Check uses the existing fixed semantic-map expected values.

- [ ] Run focused checker tests:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "dynamic_check or alternative_treatment or legacy_check_context" -v
```

- [ ] Implement the judgment-aware checker and rerun the complete Trainer tests:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record exact pass counts in `RESULT.md`.

---

## Task 5 — Preserve answer separation, document Step 8B1, regenerate artifacts, and verify

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

### Documentation wording

Describe the current product as:

```text
Step 7 — historical model construction
- 25 historical formula families / 118 cells in the five-year illustrative demo
- workbook-wide formula Check

Step 8A — guided classification reasoning
- supported ambiguous supplied lines become compare-and-defend exercises
- rationale/consequence remain ungraded

Step 8B1 — live supported classification
- treatment selected in Accounting Judgment drives the linked Condensed Financials classification
- blank treatment uses the reference treatment
- downstream reformulation and DuPont formulas therefore respond to the selected treatment
- formula Check recomputes expected historical values under the current treatment state
- exact and equivalent formulas remain valid under either supported treatment
```

Explicitly state:

```text
Normalization / recurring-vs-non-recurring judgment is not implemented yet.
ROU/deferred-tax alternative treatment remains deferred.
The committed demo is illustrative/synthetic.
```

Do not claim the free-form rationale is graded.

### Full verification

Run all of the following after implementation:

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

Expected fresh-workbook outcomes remain:

```text
Components resolved: 118
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
list --workbook: 25 historical schedule groups / 118 formula cells
CLI surface: {ingest,build,check,list}
Accounting Judgment cases in illustrative demo: 1
```

Then perform one explicit alternative-state verification using Python/test tooling:

```text
Accounting Judgment treatment: Financial Liability
linked Condensed Financials classification: formula-driven from the judgment row
recomputed reference state: lease balance moves from Operating LT Liability to Financial Liability
reformulated equity reconciliation: preserved
an exact affected formula: correct
an equivalent affected formula with alternative cached value: correct
same equivalent formula after second Check: still correct
old reference cached value under alternative treatment: incorrect
judgment cells F:G:H: unchanged by Check
```

### Final workbook/security audit

Verify:

1. `_CheckContext` exists hidden in Answer Key only.
2. Trainer contains no `_CheckContext` sheet.
3. Check context contains source facts/setup bindings but no formulas, expected values, hints, rationale answers, or consequence answers.
4. `Accounting Judgment!F5` remains blank/yellow in fresh Trainer and populated with the reference treatment in Answer Key.
5. `Accounting Judgment!G5:H5` remain blank/yellow in Trainer and populated in Answer Key.
6. The corresponding `Condensed Financials` classification row is formula-linked in both files and falls back to the reference treatment when F is blank.
7. Ordinary classification rows remain populated literal setup judgments.
8. Formula SemanticMap remains exactly 118 cells / 25 families.
9. Judgment cells remain outside SemanticMap and are not recolored by Check.
10. Deferred forecast/valuation tabs remain four hidden placeholders.
11. Normal build still succeeds when `run_scenario()` is patched to fail.
12. No Trainer sidecar/hidden sheet contains withheld formulas/expected values/hints.
13. Existing cached-value preservation and repeated-Check regressions remain green.
14. No public Hint/Reveal, judgment-grading, forecast, or valuation CLI is introduced.

### `RESULT.md` structure

Record observed evidence using this structure:

```text
Status: Step 8B1 complete — live classification with judgment-aware Check

Implementation base:
- 79d2357e Step 8A corrected

Historical formula surface:
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118

Guided/live judgment:
- supported templates: 4
- illustrative demo cases: 1
- treatment input drives Condensed Financials: yes
- blank treatment falls back to reference: yes
- rationale/consequence auto-graded: no
- ROU/deferred-tax alternative cases: no

Dynamic Check:
- Answer-Key hidden Check context: present
- Trainer Check context: absent
- reference-state expected parity: 118/118
- alternative exact formula: pass
- alternative equivalent formula: pass
- repeated alternative Check: pass
- stale reference value under alternative: rejected
- two-case combined state: pass
- legacy workbook fixed-expected fallback: pass

Security/separation:
- Check context formula answers: none
- Check context expected values: none
- Trainer formula/hint leakage: none
- Trainer rationale/consequence leakage: none

Preservation:
- reformulation identity under supported alternative: pass
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}

Tests:
- record each command and exact pass count/result

Known deferred limitations:
- normalization / recurring-vs-non-recurring treatment is Step 8B2
- ROU/deferred-tax alternative modeling remains deferred
- irregular/stub/interim comparative modeling still requires later robustness work

Unresolved:
- none OR exact blockers
```

- [ ] Update the three docs from actual behavior, regenerate both committed demo workbooks, run every verification command, update `RESULT.md` with observed values, and stop.

Do not begin Step 8B2 in this checkpoint.

## Step 8B1 acceptance criteria

Step 8B1 is accepted only when all are true:

1. Step 8A's four supported judgment templates and one illustrative demo case remain intact.
2. Each supported case has a stable classification override selector derived from supplied line identity.
3. A learner treatment entered in `Accounting Judgment` drives the matching `Condensed Financials` classification through a formula link.
4. Blank learner treatment preserves the reference treatment and therefore fresh-workbook coherence.
5. Learners are not asked to edit formula-driven classification cells directly.
6. Same-side supported alternatives preserve `NOA - Net Debt = Equity` reconciliation.
7. A hidden Answer-Key `_CheckContext` preserves enough source/setup information to recompute historical expected values.
8. `_CheckContext` is removed from Trainer and contains no formulas, expected values, hints, rationale answers, or consequence answers.
9. Shared StandardizedFinancials serialization preserves period dates, values, and `LineItem.concept` identity.
10. Dynamic expected-value resolution covers exactly all 25 historical families and matches all 118 fixed expected values in the reference state.
11. Check reads the current allowed treatment state and recomputes the Python historical anchor with corresponding classification overrides.
12. Exact formulas remain correct under supported alternative treatments.
13. Equivalent formulas are validated against judgment-conditioned expected values, not stale reference expected values.
14. A formula/value that is only correct under the old reference treatment is rejected after the learner selects the alternative.
15. Multiple simultaneous supported choices are combined correctly rather than handled as independent one-case deltas.
16. Repeated Check preserves cached results under alternative treatment just as it does under the reference treatment.
17. Judgment response cells remain ungraded and unchanged by Check.
18. Pre-Step-8B Answer Keys without `_CheckContext` retain the existing fixed-expected Check path.
19. Formula surface remains 25 families / 118 cells and fresh Check remains `0/0/118`.
20. Trainer/Answer-Key separation, sidecar hygiene, forecast quarantine, and deferred hidden tabs remain intact.
21. Full core suite and end-to-end build/check/list/CLI verification pass with fresh evidence.
22. Documentation states Step 8B1 accurately and does not claim normalization, independent accounting competence, forecasting, or valuation.

---

# Locked follow-on roadmap — do not implement in Step 8B1

## Step 8B2 — Guided earnings normalization

Add recurring/non-recurring treatment and normalization adjustments as a separate subsystem. Its design must specify how source income-statement items, normalized NOPAT/net income, reconciliation bridges, and dynamic Check interact before implementation begins.

## Step 9 — Historical research diagnostics

Teach margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality signals.

## Step 10 — Cross-company and period-cadence robustness

Validate on materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad input robustness.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after the forecast layer is separately trusted.
