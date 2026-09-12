# Step 8B1 — Live Classification Choices With Judgment-Aware Check

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `79d2357f073272015a63572537f13a84ae08e754` (`8A corrected`). Implement only Step 8B1 below using red/green TDD. Preserve the Step 7 formula surface, Step 8A guided reasoning, workbook-wide Check, and Trainer/Answer-Key separation. Do not implement normalization, earnings-quality diagnostics, forecasting, valuation, or Step 8B2. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make each supported Step 8A classification choice drive the historical reformulated model while keeping exact-formula and equivalent-formula Check correct under either defensible treatment.

**Architecture:** `Accounting Judgment` remains the only learner classification-input surface. A supported case's `Condensed Financials` classification cell becomes a non-practice formula that uses the learner selection when present and otherwise falls back to the supplied reference treatment. The Answer Key stores a hidden `_CheckContext` containing only model source facts, setup overrides, and judgment bindings. During Check, reconstruct the Python historical model from that context plus the learner's current treatment selections, then compare equivalent-formula cached results with treatment-conditioned expected values. Judgment rationale/consequence remain free-form and ungraded.

**Tech Stack:** Python, dataclasses, JSON, pytest, openpyxl, `StandardizedFinancials`, `ReferenceModelBuilder`, `JudgmentCase`, `compute_anchor`, `SemanticMap`, `TrainingWorkbookGenerator`, and the existing OOXML-preserving checker.

**Spec:** `TARGET.md`, especially Level 2 — Analyst judgment: selected classification decisions become explicit exercises, the learner must choose and defend treatments and reconcile the resulting model, and ambiguous treatments must be taught as alternatives with consequences rather than one universal answer.

## Latest checkpoint review

Commit `79d2357e` repairs Step 8A as intended. Code review confirms the previously identified blockers are addressed: classification/pedagogy are separated, deferred-tax/ROU are not guided cases, canonical periods gate cases, structural sanitization works without transient case objects, and learner instructions distinguish judgment from Formula Check. `RESULT.md` records 115 passing local tests and successful build/check/list verification. GitHub has no attached CI status, so those are recorded local results rather than independent CI evidence.

No blocking Step 8A code defect remains. The missing Level-2 behavior is now explicit: the learner can choose and defend an alternative, but the choice does not yet alter the model or the expected values used by Check.

## Scope decision

Do **not** combine live classification and earnings normalization in one checkpoint. They affect different parts of the accounting model and need different reconciliation logic. Step 8B1 implements live supported balance-sheet classification only. Step 8B2 will add recurring/non-recurring and normalization judgments after the judgment-conditioned feedback loop is trusted.

## Global constraints

- `TARGET.md` is read-only.
- Preserve five demo fiscal years, 25 historical formula families, and 118 formula practice cells.
- Preserve exactly the four Step 8A guided templates: lease liability, pension obligation, short-term investment, associate/JV investment.
- ROU and deferred-tax balances remain ambiguous but unsupported as guided alternatives.
- Learner treatment is entered only in `Accounting Judgment` column F.
- Blank treatment means supplied reference treatment.
- Supported alternatives remain same-side only: asset ↔ asset or liability ↔ liability.
- `Accounting Judgment` rationale/consequence remain ungraded.
- Formula Check remains one workbook-wide action across the same 118 formula cells.
- Exact Answer-Key formulas and equivalent formulas with the same **current-state** result must both pass.
- Check remains non-disclosing.
- `_CheckContext` exists only in Answer Key and is removed from Trainer.
- `_CheckContext` must contain no formula answers, expected values, formula hints, model rationale, or model consequence text.
- Normal build must not run the dormant forecast/scenario engine.
- No normalization, recurring/non-recurring adjustments, earnings-quality diagnostics, forecasting, valuation, Hint/Reveal, VBA, or automated free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Persist model source/setup context safely in the Answer Key

**Files:**
- Create: `core/data/standardized_io.py`
- Create: `core/trainer/check_context.py`
- Modify: `core/model/judgment.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### Interfaces

Create a model-only round-trip serializer:

```python
def standardized_to_payload(fin: StandardizedFinancials) -> dict:
    ...


def standardized_from_payload(payload: dict) -> StandardizedFinancials:
    ...
```

The payload must preserve only model-relevant data:

```text
ticker
company_name
currency
units
jurisdiction
stock_code
periods: end_date, label, is_interim
income_statement: label, concept, values
balance_sheet: label, concept, values
cash_flow: label, concept, values
```

Use ISO `YYYY-MM-DD` date keys. Do not serialize `source_doc` absolute paths, provenance, workbook coordinates, formulas, expected values, or hints.

Extend `JudgmentCase` with a stable override selector:

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

Build it from the supplied line:

```python
ident = line_identity(item)
override_selector = (
    f"concept:{ident.concept}"
    if ident.concept
    else f"label:{item.label}"
)
```

Create:

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

and:

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

`embed_check_context_sheet()` must delete any prior `_CheckContext`, create a hidden sheet, write `BAV_CHECK_CONTEXT_V1` in `A1`, deterministic JSON in chunks of at most 30,000 characters down `A2:A...`, and save no answer-bearing fields.

Bindings use:

```python
worksheet_row = 4 + case.order
allowed_treatments = (case.supplied_treatment,) + case.alternatives
```

`load_check_context()` returns `None` when the sheet does not exist so older workbooks keep the old fixed-expected behavior. If the sheet exists but is malformed or has a wrong version/magic, raise `ValueError`; do not silently fall back.

### TDD steps

- [ ] Add a demo source round-trip test and assert period dates, every statement value, and every `line_identity()` are preserved.
- [ ] Add a demo Check-context test. It must return one binding with:

```python
binding.worksheet_row == 5
binding.override_selector == "concept:lease_liability"
binding.reference_treatment == "Operating Long-Term Liability"
binding.allowed_treatments == (
    "Operating Long-Term Liability",
    "Financial Liability",
)
```

- [ ] Scan serialized context and assert it contains none of the demo case's rationale/consequence text and none of the SemanticMap formula/hint fields.
- [ ] Add `_CheckContext` to Trainer sanitization and assert it is absent from Trainer but hidden in Answer Key.
- [ ] Run red-state tests:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "standardized_payload or check_context or judgment_selector" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "check_context" -v
```

- [ ] Implement the serializer/context layer and rerun until green.

---

## Task 2 — Make the judgment treatment drive `Condensed Financials`

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py`

### Interface

After `self.judgment_cases` is built:

```python
self._judgment_row_by_identity = {
    case.line_identity: 4 + case.order
    for case in self.judgment_cases
}
```

For an ordinary classification row, preserve the current literal classification and eight-category data validation.

For a supported judgment row, column B becomes a **non-practice** formula:

```excel
=IF('Accounting Judgment'!$F$5="",'Accounting Judgment'!$D$5,'Accounting Judgment'!$F$5)
```

Use the actual judgment row; never hard-code row 5 in production. Do not add the ordinary category data validation to this formula-driven B cell. The only learner input is the restricted dropdown in `Accounting Judgment!F`.

State behavior:

```text
F blank      -> B uses supplied reference treatment
F reference  -> B uses reference treatment
F alternative -> B uses alternative treatment
F cleared    -> B returns to reference treatment
```

The existing category `SUMIF` formulas therefore remain unchanged and become live automatically.

Replace the Step 8A A3 instruction with this substance:

```text
Choose a treatment in column F. That choice drives the matching Condensed Financials classification and downstream historical schedules; leaving it blank uses the supplied reference treatment. Enter your rationale and economic consequence in G:H. Formula Check grades formula cells against the treatment currently selected here; it does not grade the judgment response itself. Do not edit the linked Condensed Financials classification cell directly.
```

Update `TRAINER_INDEX_INSTRUCTION` consistently.

### TDD steps

- [ ] Locate the demo lease row in `Condensed Financials`; assert B contains a formula referencing `Accounting Judgment!F5` and `Accounting Judgment!D5`.
- [ ] Assert `Bank borrowings` remains a literal classification with ordinary category data validation.
- [ ] Assert the judgment-driven B cell is not a SemanticMap practice cell, is not yellow practice, and is pair-identical between Trainer and Answer Key.
- [ ] Assert F5 dropdown survives in both workbooks and contains exactly the two allowed treatments.
- [ ] Add a synthetic two-case build and assert each classification row links to its own judgment row without collisions.
- [ ] Run red-state tests:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "live_classification or judgment_link" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "judgment_link or treatment_dropdown" -v
```

- [ ] Implement the live links and revised learner instructions. Do not change any of the 118 formula-practice coordinates.

---

## Task 3 — Centralize dynamic expected values for all 25 historical families

**Files:**
- Create: `core/model/historical_expected.py`
- Test: `core/tests/test_reference_integrity.py`

### Interfaces

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

The mapping must cover exactly these 25 family IDs:

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

`expected_value_for_component()` requires a known family and non-null historical `period_index`, then returns the series value at that index. Unknown families/invalid indices raise clear programming errors.

### Accounting invariants to test

Under the demo alternative:

```python
classification_overrides={
    "concept:lease_liability": "Financial Liability",
}
```

the direct classification/reformulation series must change:

```text
oltl_agg
financial_liabilities_agg
nola_agg
noa_agg
net_debt
```

and the interpretation ratios must change for the demo:

```text
rnoa
after_tax_cod
spread
flev
```

But a same-side reclassification moves the same balance between operating and financing presentation, so the accounting identity implies these remain invariant (within tolerance):

```text
equity_reformulated_fy
roe_decomp
actual_roe
revenue_link
net_income_link
nopat_fy
sales_growth
nopat_margin
```

The `roe_decomp` invariance is important: the components of ROE change, but `RNOA + FLEV × Spread` still collapses to the same total ROE when NOA = Equity + Net Debt and income treatment is held constant.

### TDD steps

- [ ] In the reference state, assert all 118 resolved components match the new resolver's expected value (numeric `pytest.approx`, otherwise exact equality).
- [ ] Assert:

```python
set(historical_expected_series(anchor)) == {f.id for f in COMPONENT_CATALOG}
```

- [ ] Build reference and alternative demo anchors and assert the changed/invariant families above.
- [ ] Explicitly run `check_reformulation_integrity()` on the alternative anchor and assert reformulated equity remains reported equity within tolerance.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "historical_expected or alternative_classification" -v
```

- [ ] Implement the resolver and rerun until green.

---

## Task 4 — Make Formula Check judgment-aware

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/check_context.py`
- Test: `core/tests/test_trainer.py`

### Interfaces

Create:

```python
def classification_overrides_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    ...
```

Start from a copy of `context.base_classification_overrides`. For each binding read:

```python
selected = trainer_wb["Accounting Judgment"].cell(
    row=binding.worksheet_row,
    column=6,
).value
```

Interpret exactly:

```text
blank/whitespace -> reference_treatment
allowed treatment -> selected treatment
anything else -> ValueError before any fill update
```

Then:

```python
overrides[binding.override_selector] = selected_treatment
```

When `_CheckContext` exists, `check_workbook()` must:

1. load the normal Answer-Key SemanticMap;
2. load `CheckContext` from the matching Answer Key;
3. reconstruct `StandardizedFinancials` from `source_payload`;
4. parse `modeled_periods` into dates and assert they equal `canonical_fiscal_periods(financials)`;
5. read current learner treatment selections from Trainer;
6. call `compute_anchor(..., classification_overrides=current_overrides)`;
7. compute dynamic expected values with `expected_value_for_component()`;
8. keep the current exact-formula fast path unchanged;
9. compare a non-exact formula's cached value against the dynamic expected value.

If `_CheckContext` is absent, preserve the existing legacy behavior:

```python
expected = comp.expected_value
```

Do not add treatment state to CLI output or `CheckSummary`.

### TDD steps

- [ ] **Fresh/reference parity:** fresh Trainer remains `0/0/118`; existing exact/equivalent reference-state Check tests remain unchanged.
- [ ] **Alternative exact formula:** set demo F5 to `Financial Liability`, enter an exact affected formula, and assert green.
- [ ] **Alternative equivalent formula:** choose latest-period `net_debt`, prove alternative expected value differs from `comp.expected_value`, inject a different formula with the alternative cached value using the existing OOXML helper, and assert green.
- [ ] **Stale reference value:** under the alternative treatment, inject a non-exact formula whose cached value equals the old reference expected value; assert red.
- [ ] **Repeated alternative Check:** run Check twice and assert the equivalent formula remains green and its cached value survives.
- [ ] **Two-case combined state:** synthetic workbook with two guided cases, select both alternatives, recompute the combined Python anchor, and prove equivalent-formula Check uses the combined state rather than one-case deltas.
- [ ] **Invalid treatment:** put a value outside `allowed_treatments` in F; Check raises before applying any fill updates. Error text may name the row and invalid value but must disclose no formula, expected value, rationale, or consequence answer.
- [ ] **Legacy compatibility:** copy an Answer Key without `_CheckContext`; Check retains fixed `comp.expected_value` behavior.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "dynamic_check or alternative_treatment or legacy_check_context" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [ ] Implement and record exact pass counts.

---

## Task 5 — Documentation, artifact regeneration, and full verification

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

### Required product wording

Describe capability as:

```text
Step 7 — historical model construction
- 25 historical formula families / 118 cells in the five-year illustrative demo
- workbook-wide Formula Check

Step 8A — guided classification reasoning
- supported supplied ambiguities become compare-and-defend exercises
- rationale/consequence are ungraded

Step 8B1 — live supported classification
- treatment selected in Accounting Judgment drives the linked Condensed Financials classification
- blank treatment falls back to the supplied reference treatment
- downstream reformulation and DuPont schedules respond to the selected treatment
- Formula Check recomputes expected historical values under the current treatment state
- exact and equivalent formulas remain checkable under either supported treatment
```

Explicitly state that normalization/recurring-vs-non-recurring treatment, ROU/deferred-tax alternatives, forecasting, and valuation remain deferred. The demo remains illustrative/synthetic.

### Verification commands

Run all of these fresh:

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

Fresh-workbook outcomes must remain:

```text
Components resolved: 118
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
list --workbook: 25 historical schedule groups / 118 formula cells
CLI surface: {ingest,build,check,list}
illustrative Accounting Judgment cases: 1
```

Also verify an explicit alternative state:

```text
F5 treatment: Financial Liability
linked Condensed Financials classification: driven by F5
reformulated equity reconciliation: preserved
RNOA / CoD / Spread / FLEV interpretation: changed
ROE decomposed total / Actual ROE: unchanged within tolerance
exact affected formula: correct
equivalent affected formula with alternative cached value: correct
same equivalent formula after second Check: correct
old reference cached value under alternative: incorrect
judgment F:G:H: not recolored or altered by Check
```

### Security/workbook audit

Verify all:

1. `_CheckContext` exists hidden in Answer Key only.
2. Trainer contains no `_CheckContext`.
3. Check context contains source/setup/binding facts but no formulas, expected values, hints, model rationale, or model consequence answers.
4. Fresh Trainer F5:G5:H5 are blank/yellow; Answer Key contains the reference response.
5. The matching `Condensed Financials` classification cell is formula-driven and falls back to the reference treatment when F is blank.
6. Ordinary classification rows remain literal supplied judgments.
7. Formula SemanticMap remains 25 families / 118 cells.
8. Judgment cells and linked classification cells remain outside SemanticMap.
9. Deferred forecast/valuation tabs remain four hidden placeholders.
10. Normal build still succeeds when `run_scenario()` is patched to fail.
11. Existing cached-value and repeated-Check regressions remain green.
12. No public Hint/Reveal, judgment-grading, forecast, or valuation CLI is introduced.

### `RESULT.md` evidence structure

```text
Status: Step 8B1 complete — live classification with judgment-aware Check

Implementation base:
- 79d2357e Step 8A corrected

Historical formula surface:
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118

Live judgment:
- supported templates: 4
- illustrative demo cases: 1
- treatment drives Condensed Financials: yes
- blank treatment fallback: yes
- rationale/consequence graded: no
- ROU/deferred-tax alternatives: no

Dynamic Check:
- reference-state expected parity: 118/118
- alternative exact formula: pass
- alternative equivalent formula: pass
- repeated alternative Check: pass
- stale reference value under alternative: rejected
- two-case combined state: pass
- legacy no-context fallback: pass

Accounting invariants under demo alternative:
- reformulated equity reconciliation: pass
- RNOA/CoD/Spread/FLEV change: yes
- ROE decomposed total unchanged: yes
- Actual ROE unchanged: yes

Security/separation:
- Answer-Key hidden Check context: present
- Trainer Check context: absent
- Check context formula/expected/hint answers: none
- Trainer formula/hint leakage: none
- Trainer rationale/consequence leakage: none

Preservation:
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}

Tests:
- exact command/pass evidence

Known deferred limitations:
- normalization / recurring-vs-non-recurring treatment is Step 8B2
- ROU/deferred-tax alternative modeling remains deferred
- irregular/stub/interim comparative modeling remains deferred

Unresolved:
- none OR exact blockers
```

- [ ] Update docs from actual behavior, regenerate both committed demo workbooks, run every verification command, update `RESULT.md`, and stop. Do not begin Step 8B2.

## Step 8B1 acceptance criteria

Step 8B1 is accepted only when all are true:

1. Step 8A's four supported templates remain intact.
2. Each guided case has a stable override selector derived from supplied identity.
3. `Accounting Judgment` treatment drives the matching `Condensed Financials` classification.
4. Blank treatment preserves the reference classification.
5. Linked classification cells are not learner-editable practice cells.
6. Same-side alternatives preserve reformulated equity reconciliation.
7. Answer Key contains a hidden versioned Check context sufficient to reconstruct historical expected values.
8. Trainer contains no Check context and Check context contains no answer-bearing formula/expected/hint/rationale/consequence data.
9. Standardized model-data round-trip preserves periods, values, labels, and concepts.
10. Dynamic expected resolver covers exactly 25 families and matches all 118 reference expected values.
11. Check recomputes the Python anchor from current allowed treatment selections.
12. Exact formulas pass under supported alternatives.
13. Equivalent formulas compare to current-state expected values and pass when economically correct.
14. Old reference-state cached values are rejected after a treatment changes the relevant expected value.
15. Multiple simultaneous choices combine correctly.
16. Repeated Check preserves cached values under alternative states.
17. Judgment responses remain ungraded and unchanged by Check.
18. Legacy Answer Keys without `_CheckContext` retain fixed expected-value behavior.
19. Formula surface remains 25 families / 118 cells and fresh Check remains `0/0/118`.
20. Trainer/Answer-Key separation, forecast quarantine, and deferred hidden tabs remain intact.
21. Full suite and end-to-end build/check/list/CLI verification pass with fresh evidence.
22. Documentation does not claim normalization, independent accounting competence, forecasting, or valuation.

---

# Locked follow-on roadmap — do not implement in Step 8B1

## Step 8B2 — Guided earnings normalization

Add recurring/non-recurring treatment and normalization adjustments as a separate subsystem. Its design must specify how source income-statement items, normalized NOPAT/net income, reconciliation bridges, and dynamic Check interact before implementation.

## Step 9 — Historical research diagnostics

Teach margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality signals.

## Step 10 — Cross-company and period-cadence robustness

Validate materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad robustness.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after the forecast layer is trusted.
