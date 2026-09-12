# Step 8B2 — Guided Recurring/Non-Recurring Earnings Normalization

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `39c0db46c04a66f3958ab3062d6bf57546badde1` (`SStep 8.1 Corrected`). Implement only Step 8B2 below using red/green TDD. Preserve the Step 8B1 live-classification feedback loop, structural integrity gate, treatment-conditioned Check, and Trainer/Answer-Key separation. Do not begin earnings-quality diagnostics, accrual/cash-conversion analysis, ROU/deferred-tax alternative modeling, forecasting, valuation, or Step 9. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add a separately modeled earnings-normalization layer in which explicitly supplied material income-statement candidates can be judged as recurring or non-recurring, the learner's treatment drives a transparent normalization bridge, and Formula Check remains correct under either defensible treatment without rewriting reported historical statements.

**Architecture:** Do not infer normalization candidates from labels. Company-specific candidates are supplied explicitly through `normalizationCandidates` in assumptions and resolve to real income-statement lines by stable selector. Render a visible `Normalization Judgment` sheet for treatment/rationale/consequence and a visible `Earnings Normalization` schedule that links reported NOPAT / Net Income to normalized NOPAT / Net Income through a signed pretax and after-tax adjustment. Add four conditional formula families only when at least one supported normalization candidate exists. Extend `_CheckContext` to carry non-answer-bearing normalization bindings, and extend dynamic Check so equivalent formulas are validated against the learner's current recurring/non-recurring choices.

**Tech Stack:** Python, dataclasses, JSON, pytest, openpyxl, existing `StandardizedFinancials`, `LineIdentity`, `ReferenceModelBuilder`, `SemanticMap`, `CheckContext`, `compute_anchor`, `historical_expected`, `TrainingWorkbookGenerator`, and OOXML-preserving Check.

**Spec:** `TARGET.md`, especially Level 2 — Analyst judgment; recurring versus transitory/non-recurring items; earnings normalization; material/applicable-topic gating; reported-source preservation; auditable reconciliation; and the rule that free-form explanations need not yet be automatically graded.

---

## Review of commit `39c0db46`

The Step 8B1.1 hardening addresses the blocking live-classification defects identified in the previous review:

- `Accounting Judgment!F` is now the sole live classification input;
- blank F falls back to a literal trusted reference treatment rather than editable prompt cell D;
- D/E prompt integrity and generated Condensed classification links are validated before grading;
- invalid treatment / structural failures do not apply partial fill updates;
- dynamic Check closes opened workbooks through `finally`;
- treatment-sensitive exact/equivalent-formula regressions replace the vacuous assertion;
- the base five-year surface remains 25 historical families / 118 formula cells.

`RESULT.md` records 136 passing local tests plus successful build/check/list verification. GitHub has no attached CI status, so treat these as recorded local verification rather than independent CI evidence.

No blocking Step 8B1.1 code defect remains from this review. The next locked dependency in `TARGET.md` is earnings normalization. Keep it separate from Step 9 diagnostics: Step 8B2 builds the normalization decision and reconciliation bridge only; interpretation of quality-of-earnings, accruals, cash conversion, and driver diagnosis remains later work.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve all existing builds with no `normalizationCandidates`: five demo fiscal years, 25 historical families, 118 formula practice cells, and current Step 8B1 behavior.
- Normalization candidates must be explicitly supplied in assumptions. Do not create cases from arbitrary labels, keywords, or model guesses.
- Explicit candidate inclusion is the Step 8B2 materiality/applicability gate; zero-valued candidates across modeled periods are suppressed.
- Step 8B2 supports exactly one normalization scope: `operating_pretax_effective_tax`.
- For this scope, the source item's reported signed pretax amount remains untouched; `Non-recurring` means normalize that item out of earnings and `Recurring` means leave it in reported earnings.
- The after-tax normalization effect uses the model's period effective tax rate as an explicit Step 8B2 convention. Special tax deductibility, item-specific tax rates, deferred-tax effects, and below-the-line/non-operating normalization are deferred.
- Reported `Income Statement`, `Condensed Financials`, reported NOPAT, reported Net Income, and the existing 118 historical formula cells are never rewritten by normalization choices.
- Normalization has its own visible judgment and schedule surfaces.
- Learner treatment is entered only in `Normalization Judgment` column F. Blank F uses the supplied reference treatment.
- Normalization rationale/consequence remain free-form and ungraded.
- Formula Check remains one workbook-wide action. With a normalization case, it checks the existing historical cells plus the new normalization formula cells.
- Exact formulas and equivalent formulas with the same current-state result must both pass under either allowed normalization treatment.
- `_CheckContext` remains Answer-Key-only and must contain no formula answers, expected values, formula hints, normalization rationale, or normalization consequence answer text.
- Preserve Step 8B1 classification bindings and integrity validation unchanged.
- Normal build must not execute the dormant forecast/scenario engine.
- No automatic free-form grading, Hint/Reveal, VBA, earnings-quality diagnostics, accrual/cash-conversion diagnostics, forecasting, or valuation.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Define explicit normalization candidates and cases

**Files:**
- Create: `core/model/normalization.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`

**Interfaces:**

Assumptions may contain:

```json
{
  "normalizationCandidates": [
    {
      "selector": "concept:restructuring_expense",
      "referenceTreatment": "Non-recurring",
      "scope": "operating_pretax_effective_tax",
      "topic": "Restructuring expense recurring vs non-recurring",
      "referenceRationale": "The reference model treats the supplied restructuring charge as non-recurring because the case setup identifies it as a discrete restructuring event rather than normal ongoing operations.",
      "consequenceNote": "Treating the item as non-recurring removes its signed after-tax effect from normalized earnings; treating it as recurring leaves reported earnings unchanged."
    }
  ]
}
```

Do not support any additional scope in this checkpoint.

Create:

```python
NORMALIZATION_TREATMENTS = ("Recurring", "Non-recurring")
SUPPORTED_NORMALIZATION_SCOPE = "operating_pretax_effective_tax"

@dataclass(frozen=True)
class NormalizationCandidateSpec:
    selector: str
    reference_treatment: str
    scope: str
    topic: str
    reference_rationale: str
    consequence_note: str

@dataclass(frozen=True)
class NormalizationCase:
    id: str
    order: int
    line_identity: str
    override_selector: str
    label: str
    scope: str
    topic: str
    reference_treatment: str
    alternatives: tuple[str, ...]
    model_rationale: str
    consequence_prompt: str
    model_consequence: str
```

Create:

```python
def normalization_cases(
    financials: StandardizedFinancials,
    periods: list[date],
    assumptions: dict,
) -> tuple[NormalizationCase, ...]:
    ...
```

### Candidate rules

For each entry in `assumptions.get("normalizationCandidates") or []`:

1. require an object with all six fields shown above;
2. `scope` must equal `operating_pretax_effective_tax`;
3. `referenceTreatment` must be exactly `Recurring` or `Non-recurring`;
4. resolve `selector` against **income-statement detail lines** using the same selector semantics as classification overrides: `concept:<id>` or unique `label:<text>` / bare label;
5. zero matches -> raise a clear `ValueError`; do not silently skip a configured candidate;
6. multiple matches -> raise a clear `ValueError` and require a concept selector;
7. if all candidate values are zero/`None` across canonical modeled `periods`, suppress the case;
8. assign order densely after zero-value filtering;
9. `line_identity = line_identity(item).key()`;
10. `id = f"normalization::{line_identity(item).key()}"`;
11. `override_selector` is the supplied normalized selector (`concept:...` when concept exists; otherwise `label:<original label>`);
12. allowed choices are exactly the reference treatment first, then the other member of `NORMALIZATION_TREATMENTS`;
13. no model values are invented.

Use the common non-answer prompt:

```text
Explain why you would treat this item as recurring or non-recurring and how that treatment changes normalized earnings.
```

`ReferenceModelBuilder.__init__` must set:

```python
self.normalization_cases = normalization_cases(
    self.fin,
    self.periods,
    self.assumptions,
)
```

and default:

```python
self.assumptions.setdefault("normalizationCandidates", [])
```

### TDD steps

- [ ] Write failing parser/case tests for concept selector, unique label selector, unknown selector, ambiguous label selector, unsupported scope, invalid treatment, and all-zero suppression.
- [ ] Prove there is no label heuristic by supplying a line called `One-off restructuring expense` with no configured candidate and asserting `normalization_cases(...) == ()`.
- [ ] Prove order becomes dense after filtering an earlier zero-valued configured candidate.
- [ ] Run red-state tests:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "normalization_case or normalization_candidate" -v
```

- [ ] Implement `core/model/normalization.py` and builder wiring.
- [ ] Rerun until green.

---

## Task 2 — Add one coherent illustrative normalization candidate without changing reported totals

**Files:**
- Modify: `example/DEMO_HK_Standardized.json`
- Create: `example/DEMO_HK_Assumptions.json`
- Modify: `core/tests/test_reference_integrity.py`

The demo remains explicitly illustrative/synthetic.

Split the FY2023 restructuring amount out of the existing administrative-expense line while preserving the combined reported expense:

```text
Current Administrative expenses:
2021 -1700
2022 -1840
2023 -2020
2024 -2240
2025 -2500

Revised Administrative expenses:
2021 -1700
2022 -1840
2023 -1820
2024 -2240
2025 -2500

New Restructuring expense:
2021     0
2022     0
2023  -200
2024     0
2025     0
concept: restructuring_expense
```

Do not change Revenue, Operating profit, Pretax Income, Tax Expense, Net Income, or any balance-sheet/cash-flow total. The new line is a detail split of the illustrative reported expenses, not a new economic event added on top of totals.

Create `example/DEMO_HK_Assumptions.json`:

```json
{
  "classificationOverrides": {},
  "normalizationCandidates": [
    {
      "selector": "concept:restructuring_expense",
      "referenceTreatment": "Non-recurring",
      "scope": "operating_pretax_effective_tax",
      "topic": "Restructuring expense recurring vs non-recurring",
      "referenceRationale": "The reference model treats the supplied restructuring charge as non-recurring because the illustrative case identifies it as a discrete restructuring event rather than normal ongoing operations.",
      "consequenceNote": "Non-recurring treatment removes the signed after-tax effect from normalized earnings; recurring treatment leaves reported earnings unchanged."
    }
  ]
}
```

### Tests

- [ ] Assert the revised administrative expense plus restructuring expense equals the prior administrative expense in every year.
- [ ] Assert `ReferenceModelBuilder(data, assumptions).normalization_cases` contains exactly one case with label `Restructuring expense`, reference `Non-recurring`, alternative `Recurring`, and order 1.
- [ ] Assert the no-assumptions build produces zero normalization cases and retains the old 25-family / 118-cell surface.
- [ ] Assert all existing reported model expected values remain unchanged by merely splitting the detail line when normalization assumptions are absent.

---

## Task 3 — Compute one authoritative normalization bridge

**Files:**
- Modify: `core/model/normalization.py`
- Test: `core/tests/test_reference_integrity.py`

Create:

```python
@dataclass(frozen=True)
class NormalizationSeries:
    pretax_adjustment: tuple[float, ...]
    after_tax_adjustment: tuple[float, ...]
    normalized_nopat: tuple[float, ...]
    normalized_net_income: tuple[float, ...]


def compute_normalization_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
    cases: tuple[NormalizationCase, ...],
    treatments: dict[str, str] | None = None,
) -> NormalizationSeries:
    ...
```

`treatments` is keyed by `case.id`. Missing entries use `case.reference_treatment`.

For every period `j` and case:

```text
Recurring     -> candidate adjustment = 0
Non-recurring -> candidate pretax add-back = -reported_signed_item_value
```

Aggregate across all cases:

```python
pretax_adjustment[j] = sum(candidate_pretax_addbacks)
after_tax_adjustment[j] = pretax_adjustment[j] * (1 - anchor.historical.effective_tax_rate[j])
normalized_nopat[j] = anchor.historical.nopat[j] + after_tax_adjustment[j]
normalized_net_income[j] = anchor.historical.net_income[j] + after_tax_adjustment[j]
```

This sign rule handles both expense and gain candidates:

```text
one-off expense -200 -> pretax adjustment +200
one-off gain    +200 -> pretax adjustment -200
```

Validation:

- unknown case id in `treatments` -> `ValueError`;
- treatment outside `Recurring|Non-recurring` -> `ValueError`;
- only supported scope accepted;
- period axis must match the anchor historical-series length.

### Accounting invariants

For the one operating pretax normalization bridge:

```python
(normalized_nopat - reported_nopat)
==
(normalized_net_income - reported_net_income)
== after_tax_adjustment
```

within numerical tolerance for every period.

For the demo reference treatment:

```text
2021 adjustment = 0
2022 adjustment = 0
2023 pretax adjustment = +200
2024 adjustment = 0
2025 adjustment = 0
```

and the FY2023 after-tax adjustment uses the FY2023 historical effective tax rate.

Switching the demo case to `Recurring` must make all four series collapse to zero-adjustment / reported values.

### TDD steps

- [ ] Add signed expense and signed gain unit tests.
- [ ] Add the demo reference-treatment series test.
- [ ] Add the recurring-alternative test.
- [ ] Add multi-case aggregation test using one expense and one gain in the same period.
- [ ] Add invalid-treatment and unknown-case-id tests.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "normalization_series or normalized_earnings" -v
```

- [ ] Implement and rerun until green.

---

## Task 4 — Render `Normalization Judgment` and `Earnings Normalization`

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_trainer.py`

### `Normalization Judgment` sheet

Create the visible sheet only when at least one normalization case exists.

Required layout:

```text
A1  Normalization Judgment
A2  The supplied treatment is the model's reference convention, not a universal truth. Decide whether each supplied candidate should remain in recurring earnings or be normalized out.
A3  Choose the treatment in column F. Blank F uses the supplied reference treatment. G:H are ungraded reasoning. Do not edit the generated Earnings Normalization treatment link directly.

row 4 headers:
Order
Line item
Scope
Supplied reference treatment
Alternative to evaluate
Treatment to defend
Rationale
Economic consequence
```

For each case row:

```text
A order
B label
C scope
D reference_treatment
E comma-separated alternatives
F reference_treatment in Answer Key / blank in Trainer
G model_rationale in Answer Key / blank in Trainer
H model_consequence in Answer Key / blank in Trainer
```

F has a dropdown containing exactly `(reference_treatment,) + alternatives`.

Use structural sanitization based on numbered case rows, exactly as Step 8A does. Trainer must contain no rationale/consequence answer text.

### `Earnings Normalization` sheet

Create the visible sheet only when normalization cases exist.

Use one detail block plus one bridge block. Do not hard-code demo coordinates outside the builder.

Detail block:

```text
Line item | Treatment | FY1 | FY2 | ...
```

One row per case:

- column A = case label;
- column B = generated, non-practice treatment formula driven only by the matching `Normalization Judgment!F` and literal fallback reference treatment;
- period cells link to the actual supplied income-statement line for that period;
- treatment/link cells are not yellow and not SemanticMap practice cells.

Create a shared helper analogous to classification:

```python
def live_normalization_treatment_formula(
    judgment_row: int,
    reference_treatment: str,
) -> str:
    ...
```

For a reference `Non-recurring`, blank F must return literal `"Non-recurring"`; the formula must not reference prompt D.

Bridge block rows:

```text
Reported NOPAT
Reported Net Income
Pretax Normalization Adjustment
Effective Tax Rate
After-tax Normalization Adjustment
Normalized NOPAT
Normalized Net Income
NORMALIZATION CHECK
```

Formula semantics by period:

```text
Reported NOPAT                 -> link populated from Condensed Financials
Reported Net Income            -> link populated from Condensed Financials
Pretax Normalization Adjustment -> -SUMIF(detail treatment range, "Non-recurring", detail value range)
Effective Tax Rate             -> populated link from Condensed Financials
After-tax Normalization Adjustment -> Pretax Adjustment * (1 - ETR)
Normalized NOPAT               -> Reported NOPAT + After-tax Adjustment
Normalized Net Income          -> Reported Net Income + After-tax Adjustment
NORMALIZATION CHECK            -> compare the two normalization deltas; OK within tolerance
```

Only these four rows become formula practice:

```text
Pretax Normalization Adjustment
After-tax Normalization Adjustment
Normalized NOPAT
Normalized Net Income
```

Reported links, ETR link, detail source links, treatment links, and guardrail CHECK stay populated.

### TDD steps

- [ ] Add Answer-Key/Trainer sheet-structure tests and exact header/instruction assertions.
- [ ] Assert F/G/H are populated/yellow in Answer Key and blank/yellow/no-Note in Trainer.
- [ ] Assert the F dropdown survives in Trainer.
- [ ] Assert detail treatment formula uses F plus literal reference and never D.
- [ ] Assert detail source-value formulas resolve the configured line identity, not label-only guessed coordinates.
- [ ] Assert NORMALIZATION CHECK is `OK` in the reference workbook logic and is not a practice cell.
- [ ] Add leakage scan for model rationale/consequence across Trainer visible/hidden cells/comments/sidecars.

---

## Task 5 — Add four conditional normalization formula families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/engine/semantic_map.py` only if required for combined expected specs
- Modify: `core/trainer/workbook.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

Do **not** add normalization families to the existing `COMPONENT_CATALOG`; keep the accepted 25 historical families stable.

Create:

```python
NORMALIZATION_COMPONENT_CATALOG: tuple[ComponentFamily, ...]
```

with exactly four families:

```text
pretax_normalization_adjustment   family_order 26   period_scope all
after_tax_normalization_adjustment family_order 27  period_scope all
normalized_nopat                 family_order 28   period_scope all
normalized_net_income            family_order 29   period_scope all
```

Use semantic keys under `normalization.*` and clear hints that teach the bridge formulas without disclosing case-specific treatment answers.

Create:

```python
def expand_normalization_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    ...
```

It must use the same canonical-period validation rules as `expand_historical_specs()` and assign concrete component order continuously from `start_order`.

`ReferenceModelBuilder` behavior:

```text
no normalization cases -> expected_specs = 118 historical specs only
>=1 normalization case -> expected_specs = historical specs + 20 normalization specs for five-year demo
```

The demo with `DEMO_HK_Assumptions.json` therefore has:

```text
29 conceptual formula families
138 concrete formula practice cells
```

A build without normalization assumptions remains:

```text
25 families
118 cells
```

Extend family grouping metadata so built-workbook `list --workbook` can render normalization families in order 26-29. Do not treat judgment rows as formula families.

### Expected values

Add to `core/model/historical_expected.py`:

```python
def normalization_expected_series(
    normalization: NormalizationSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    ...
```

mapping the four family IDs directly to the four `NormalizationSeries` fields.

Extend:

```python
def expected_value_for_component(
    anchor: AnchorMetrics,
    component: ResolvedComponent,
    *,
    normalization: NormalizationSeries | None = None,
) -> float | str | None:
    ...
```

Rules:

- existing 25 families use `historical_expected_series(anchor)` unchanged;
- four normalization families require `normalization is not None`;
- unknown families still fail clearly;
- base historical reference parity for all existing 118 cells must remain exact.

### TDD steps

- [ ] Assert no-assumptions build remains exactly 25 / 118.
- [ ] Assert demo-with-normalization assumptions produces exactly 29 / 138.
- [ ] Assert all 138 Answer-Key components have formula + expected value + Note.
- [ ] Assert all 138 Trainer practice cells start blank/yellow/no Note.
- [ ] Assert the normalization expected resolver matches all 20 new Answer-Key expected values under reference treatment.
- [ ] Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "normalization_component or normalization_expected or practice_surface" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "normalization or practice_contract" -v
```

---

## Task 6 — Extend Check context and dynamic Check to normalization treatments

**Files:**
- Modify: `core/trainer/check_context.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/model/normalization.py`
- Test: `core/tests/test_trainer.py`

### Check-context schema

Bump new Answer Keys to:

```python
CHECK_CONTEXT_SCHEMA_VERSION = 2
```

Add:

```python
@dataclass(frozen=True)
class NormalizationBinding:
    order: int
    worksheet_row: int
    case_id: str
    line_identity: str
    source_selector: str
    scope: str
    reference_treatment: str
    allowed_treatments: tuple[str, ...]
```

Extend `CheckContext` with:

```python
normalization_bindings: tuple[NormalizationBinding, ...] = ()
```

Compatibility:

- load schema v1 from existing Step 8B1 workbooks with `normalization_bindings=()`;
- load schema v2 with classification + normalization bindings;
- reject unknown future schema versions;
- new builds write schema v2.

Do not put normalization rationale/consequence or normalization expected values in `_CheckContext`.

Create:

```python
def normalization_treatments_for_check(
    trainer_wb,
    context: CheckContext,
) -> dict[str, str]:
    ...
```

It reads `Normalization Judgment` column F:

```text
blank -> reference treatment
allowed treatment -> selected treatment
anything else -> ValueError before recoloring
```

### Structural integrity

Generalize the current structure gate to validate both live subsystems. Prefer:

```python
def validate_live_model_structure(
    trainer_wb,
    answer_key_wb,
    context: CheckContext,
) -> None:
    ...
```

Keep `validate_live_judgment_structure()` as a compatibility wrapper if tests/imports still use it.

For every normalization binding validate before grading:

1. `Normalization Judgment` D/E in Trainer and Answer Key match the binding;
2. Answer Key has exactly one expected generated treatment-link formula in `Earnings Normalization` column B;
3. Trainer has the identical formula at that coordinate;
4. learner-editable F is not compared;
5. G:H are not compared/graded.

Structural/invalid-treatment errors must retain Step 8B1 atomic behavior: close workbooks and apply zero fill changes.

### Dynamic expected computation

When schema v2 has normalization bindings:

1. reconstruct financials from context;
2. validate modeled periods;
3. derive classification overrides from current `Accounting Judgment` exactly as Step 8B1;
4. build the current `anchor` with classification overrides;
5. read normalization treatments from Trainer;
6. reconstruct minimal normalization cases from bindings + source lines, or expose a helper that computes `NormalizationSeries` directly from bindings without pedagogical answer text;
7. compute current `NormalizationSeries`;
8. call `expected_value_for_component(anchor, comp, normalization=series)` for every component.

Classification changes and normalization changes must compose: normalization uses the same current anchor after live classification overrides.

### Dynamic Check tests

Use the demo normalization case and at least one treatment-sensitive normalization family, preferably latest `normalized_nopat` or FY2023 `after_tax_normalization_adjustment`.

- [ ] Reference `Non-recurring`: exact formula -> green.
- [ ] Reference `Non-recurring`: equivalent formula with cached reference-normalized value -> green.
- [ ] Switch F to `Recurring`: exact formula -> green.
- [ ] Switch F to `Recurring`: equivalent formula with cached reported/current-state value -> green.
- [ ] Under `Recurring`, stale cached `Non-recurring` normalized value -> red.
- [ ] Repeated Check preserves equivalent-formula cache behavior.
- [ ] Invalid normalization treatment causes `ValueError` and zero partial recoloring.
- [ ] Tampered normalization D/E or generated Earnings Normalization treatment link fails before grading.
- [ ] Combined state test: use the classification lease alternative **and** normalization `Recurring` simultaneously; expected values for both subsystems must be computed from the same current state.
- [ ] Legacy schema-v1 Step 8B1 workbook still uses classification-only dynamic Check.

---

## Task 7 — Documentation, demo regeneration, and full verification

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

Update the main demo build command to:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Documentation must say:

```text
Step 8B2 normalization
- normalization candidates are explicitly supplied; they are not inferred from labels
- learner chooses Recurring vs Non-recurring
- reported statements and reported historical model remain unchanged
- Earnings Normalization bridges reported to normalized NOPAT / Net Income
- Step 8B2 supports operating pretax items using period effective tax rate as the supplied training convention
- Check conditions normalization formulas on the current treatment
- rationale/consequence are ungraded
```

Do not claim special-tax normalization, below-the-line normalization, automatic unusual-item detection, earnings-quality diagnostics, accrual/cash-conversion analysis, forecasting, or valuation.

### Full verification

Run fresh:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q

# Compatibility: no normalization candidates
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_BASE_Trainer.xlsx

# Step 8B2 demo
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o /tmp/DEMO_NORM_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_NORM_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_NORM_Trainer.xlsx
PYTHONPATH=. python -m core --help
```

Required end states:

```text
No-assumptions compatibility build:
- 25 families
- 118 formula cells
- fresh Check 0 / 0 / 118
- no Normalization Judgment sheet
- no Earnings Normalization sheet

Step 8B2 illustrative demo:
- 1 explicit normalization case: Restructuring expense
- reference treatment: Non-recurring
- alternative: Recurring
- 29 formula families
- 138 formula cells
- fresh Check 0 / 0 / 138
- reported historical values unchanged
- FY2023 pretax adjustment +200 under reference treatment
- FY2023 after-tax adjustment uses FY2023 effective tax rate
- switching to Recurring collapses normalized NOPAT / Net Income to reported values
- classification lease judgment and normalization judgment can coexist
- Trainer has no _CheckContext
- Answer Key has hidden schema-v2 _CheckContext
- no rationale/consequence answer leakage
- invalid/tampered live normalization state causes zero partial recoloring
- normal build does not call run_scenario()
- CLI subcommands remain {ingest,build,check,list}
```

Update `RESULT.md` with actual observed counts and results only.

---

## Step 8B2 acceptance criteria

Step 8B2 is accepted only when all are true:

1. normalization candidates come only from explicit assumptions, never arbitrary label inference;
2. configured candidate selectors resolve deterministically to real income-statement lines;
3. only `operating_pretax_effective_tax` scope exists in this checkpoint;
4. zero-valued candidates are suppressed and invalid/ambiguous configured selectors fail clearly;
5. reported source statements and existing 118 historical formulas remain unchanged by normalization treatment;
6. `Normalization Judgment!F` is the sole learner normalization input and blank means reference treatment;
7. `Earnings Normalization` exposes a transparent reported-to-normalized bridge;
8. signed expense/gain adjustment logic is correct;
9. normalized NOPAT and normalized Net Income reconcile to the same after-tax operating adjustment;
10. no-candidate builds remain exactly 25 families / 118 cells;
11. normalization builds add exactly four families / 20 cells for five periods, yielding 29 / 138 in the illustrative demo;
12. dynamic Check validates exact and equivalent normalization formulas against current treatment state;
13. classification and normalization treatment states compose in one Check run;
14. schema-v1 Check context remains readable; new schema-v2 context carries no answer-bearing rationale/consequence/formula data;
15. normalization setup tampering / invalid treatment fails before grading with zero partial recoloring;
16. Trainer sanitization removes normalization answer text and `_CheckContext`;
17. Step 8B1 classification behavior, forecast quarantine, and CLI surface remain intact;
18. docs accurately limit Step 8B2 to explicit recurring/non-recurring operating pretax normalization.

---

# Locked next roadmap — do not implement in Step 8B2

## Step 9 — Historical research diagnostics

After the normalization bridge is trusted, teach interpretation rather than adding more setup mechanics. Priorities: margin versus capital-intensity drivers, working-capital behavior, cash conversion/accruals, operating versus financing sources of ROE change, dilution where supplied, segment economics where supplied, and earnings-quality signals. Step 9 should consume reported and normalized outputs rather than redefine them.

## Step 10 — Cross-company and period-cadence robustness

Validate the curriculum on materially different non-financial companies and harden annual/interim/stub-period handling before claiming broad robustness.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit traceable analyst assumptions and BAVGEM-style business drivers.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, cross-checks, sensitivities, and concise investment interpretation only after forecasting is separately trusted.
