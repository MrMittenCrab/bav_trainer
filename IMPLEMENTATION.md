# Step 6 — Expand the Historical Reformulation + DuPont Formula Practice Surface

> **For Cursor:** Read `TARGET.md` first. Step 5 is accepted at implementation commit `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`). The previous dynamic-input/classification Step 6 plan is cancelled. Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Expand the Trainer from a sparse 13-cell sample into a coherent **historical reformulation + DuPont formula-building exercise**. Keep historical source numbers, classifications, market data, and assumptions populated. Blank only financially meaningful formula/link/ratio cells so the learner practises constructing the model rather than transcribing literal inputs.

**Architecture:** Keep the existing formula-only `ComponentSpec` / `SemanticMap` architecture. Do **not** add literal-input answer kinds or dynamic classification exercises. Expand the coordinate-free static component catalog with additional historical reformulation and DuPont formulas, then register those formulas at build time from the existing reference-model rows. The Answer Key remains the complete working model; the Trainer blanks only registered formula-practice cells; workbook-wide Check keeps the accepted yellow/green/red behavior.

**Tech Stack:** Python, pytest, openpyxl, existing OOXML cache-preserving Check fill patch.

**Spec:** `TARGET.md` as updated in planning commit `cd7a512` (`Refocus trainer on model-construction formulas`).

---

## Current checkpoint and design decision

Latest accepted implementation commit: `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`) on `chatgpt/reference-model-integrity`.

Step 5 already provides:

- matched Trainer / Answer Key workbooks;
- blank yellow formula-practice cells in Trainer;
- formula + legacy Note in Answer Key;
- workbook-wide Check: blank yellow / correct green / incorrect red;
- cache-safe OOXML recoloring;
- no Hint / Reveal surface;
- no answer-bearing Trainer metadata or sidecars;
- 81 reported passing core tests.

The product decision for the next phase is now explicit:

```text
Source data / classifications / assumptions = already provided.
Practice = constructing the formulas that connect those inputs into the model.
```

Do not make literal historical numbers, classification dropdowns, or scenario assumptions into practice cells merely to increase exercise count.

### Why this step starts with historical reformulation + DuPont

This is the first coherent BAV dependency chain:

```text
provided source statements + provided classifications
    -> effective tax / net interest
    -> NOPAT
    -> operating and financing aggregates
    -> NOWC / NOLA / NOA / Net Debt / Equity
    -> RNOA / after-tax CoD / Spread / FLEV / ROE
```

That chain teaches cross-model connections and calculations without requiring filing transcription. Forecasting and valuation remain for later expansion after this chain is accepted.

---

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve all accepted Step 3 accounting integrity, Step 4 concept-aware identity, and Step 5 Trainer / Answer Key / Check behavior.
- Keep the semantic component catalog coordinate-free; coordinates are resolved only by `ReferenceModelBuilder`.
- Practice cells in this step must be **formula-bearing model-construction cells**.
- Historical source statement values must remain populated in Trainer.
- Balance-sheet classification cells must remain populated in Trainer; do not turn them into exercises.
- Market data and scenario assumptions must remain populated in Trainer.
- Do not add `answer_kind`, input components, dynamic classification components, or an exercise DSL.
- Do not reintroduce Hint, Reveal, macros, Trainer answer metadata, or Trainer answer sidecars.
- Do not add HKEX/SEC ingestion or later BAVGEM feature chains.
- Do not redesign forecast or residual-income mathematics in this step.
- Do not weaken existing tests.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Target practice surface for this step

Keep all existing component IDs. Add these **14 formula components**:

```text
effective_tax_rate_fy
net_interest_fy
net_interest_after_tax_fy
owca_agg
owcl_agg
olta_agg
oltl_agg
nola_agg
financial_assets_agg
financial_liabilities_agg
equity_reformulated_fy
after_tax_cod
flev
actual_roe
```

Together with the existing historical components:

```text
nopat_fy
nowc_agg
noa_agg
net_debt
rnoa
spread
roe_decomp
```

the historical reformulation + DuPont chain becomes **21 practice cells**.

The existing six forecasting/valuation components remain registered and working for now:

```text
model_sales_y1
model_nopat_y1
model_ae_y1
model_tv
model_ivps
scenario_weighted
```

Therefore the expected total semantic practice count after this step is **27**.

Do not add additional cells beyond this list in this step.

---

## Task 1 — Expose authoritative expected values for the three missing historical calculations

**Files:**
- Modify: `core/model/financial_math.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- `ReferenceModelBuilder` already receives `self.anchor = compute_anchor(...)`.
- New anchor fields provide latest-fiscal-year expected values for formula Check metadata without duplicating accounting math in the workbook builder.

### Required change

Extend `AnchorMetrics` with:

```python
effective_tax_rate: float
net_interest: float
net_interest_after_tax: float
```

Populate them from the existing authoritative series already computed inside `compute_anchor()`:

```python
etr = ...
net_int = ...
niat = ...
```

At return time use the latest period:

```python
effective_tax_rate=etr[last]
net_interest=net_int[last]
net_interest_after_tax=niat[last]
```

Do not recompute these independently in `ReferenceModelBuilder`.

### TDD regression

Add a focused test using the demo financials that asserts:

```python
anchor.effective_tax_rate == pytest.approx(expected_from_source_tax_and_pretax)
anchor.net_interest == pytest.approx(expected_from_interest_income_and_expense)
anchor.net_interest_after_tax == pytest.approx(
    anchor.net_interest * (1 - anchor.effective_tax_rate)
)
anchor.nopat == pytest.approx(net_income_latest + anchor.net_interest_after_tax)
```

Use the same source-line resolver semantics as production; do not identify rows by fixed worksheet position.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "tax or interest or nopat" -v
```

---

## Task 2 — Expand the coordinate-free component catalog to the full 21-cell historical chain

**Files:**
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_trainer.py`

### Required catalog order

Reorder the fixed catalog into a dependency-coherent sequence. Use these IDs and conceptual dependencies:

```text
 1 effective_tax_rate_fy
 2 net_interest_fy
 3 net_interest_after_tax_fy       <- effective_tax_rate_fy, net_interest_fy
 4 nopat_fy                        <- net_interest_after_tax_fy

 5 owca_agg
 6 owcl_agg
 7 nowc_agg                        <- owca_agg, owcl_agg
 8 olta_agg
 9 oltl_agg
10 nola_agg                        <- olta_agg, oltl_agg
11 noa_agg                         <- nowc_agg, nola_agg
12 financial_assets_agg
13 financial_liabilities_agg
14 net_debt                        <- financial_assets_agg, financial_liabilities_agg
15 equity_reformulated_fy          <- noa_agg, net_debt

16 rnoa                            <- nopat_fy, noa_agg
17 after_tax_cod                   <- net_interest_after_tax_fy, net_debt
18 spread                          <- rnoa, after_tax_cod
19 flev                            <- net_debt, equity_reformulated_fy
20 roe_decomp                      <- rnoa, spread, flev
21 actual_roe                      <- equity_reformulated_fy

22 model_sales_y1
23 model_nopat_y1                  <- model_sales_y1
24 model_ae_y1                     <- model_nopat_y1
25 model_tv                        <- model_ae_y1
26 model_ivps                      <- model_tv
27 scenario_weighted               <- model_ivps
```

Keep the existing forecast/valuation component semantics and hints unless a dependency/order edit is required by the sequence above.

### New component definitions

Use concise finance-model hints. They should explain the relationship without revealing the exact cell formula. Examples of intended hint level:

```text
effective_tax_rate_fy:
    title: "Effective tax rate (latest fiscal year)"
    hint: "Relate tax expense to pretax income using the model's sign convention."

net_interest_fy:
    title: "Net interest (latest fiscal year)"
    hint: "Combine interest expense and interest income into the financing result."

net_interest_after_tax_fy:
    title: "Net interest after tax"
    hint: "Apply the effective tax rate once to net interest."

owca_agg / owcl_agg / olta_agg / oltl_agg / financial_assets_agg / financial_liabilities_agg:
    hint: "Aggregate the classified balance-sheet detail with the classification column."

nola_agg:
    title: "Net operating long-term assets (NOLA)"
    hint: "Operating long-term assets less operating long-term liabilities."

equity_reformulated_fy:
    title: "Reformulated equity"
    hint: "Use the operating/financing identity linking NOA, Net Debt, and Equity."

after_tax_cod:
    title: "After-tax cost of debt"
    hint: "Relate net interest after tax to average net debt."

flev:
    title: "Financial leverage (FLEV)"
    hint: "Relate average net debt to average reformulated equity."

actual_roe:
    title: "Actual ROE"
    hint: "Relate net income to average reformulated equity."
```

Do not add literal-input or classification components.

### TDD regression

Add a catalog test asserting:

```python
assert len(COMPONENT_CATALOG) == 27
assert [c.order for c in COMPONENT_CATALOG] == list(range(1, 28))
assert len({c.id for c in COMPONENT_CATALOG}) == 27
assert len({c.semantic_key for c in COMPONENT_CATALOG}) == 27
```

Also assert every dependency points to a lower-order component.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog" -v
```

---

## Task 3 — Register the expanded historical reformulation formulas from the existing reference workbook rows

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### General rule

Do not create new workbook coordinates or duplicate calculations merely to make exercises. Register the formulas that **already build the reference workbook**.

All new historical components use the latest fiscal-year column (`lc`) already used by the existing NOPAT/NOWC/NOA/Net Debt registrations.

### Register income-reformulation formulas

After their existing rows/formulas are constructed, register:

```text
effective_tax_rate_fy
    tab: Condensed Financials
    row: Effective Tax Rate
    formula: existing latest-FY cell formula
    expected: self.anchor.effective_tax_rate

net_interest_fy
    tab: Condensed Financials
    row: Net Interest
    formula: existing latest-FY cell formula
    expected: self.anchor.net_interest

net_interest_after_tax_fy
    tab: Condensed Financials
    row: Net Interest After Tax
    formula: existing latest-FY cell formula
    expected: self.anchor.net_interest_after_tax
```

Keep existing `nopat_fy` registration, with its dependency updated by Task 2.

### Register classified balance-sheet aggregate formulas

The classification choices themselves stay populated and are **not** practice.

Register the latest-FY formulas on the aggregate rows already generated by `_fill_sumif_row()`:

```text
owca_agg
    category total: Operating Working Capital Asset

owcl_agg
    category total: Operating Working Capital Liability

olta_agg
    category total: Operating Long-Term Asset

oltl_agg
    category total: Operating Long-Term Liability

financial_assets_agg
    category total: Financial Asset

financial_liabilities_agg
    category total: Financial Liability
```

Expected values must come from the authoritative reformulation:

```python
reform.category_totals[category][last_index]
```

Do not recompute category totals separately.

Register `nola_agg` from the existing `NOLA` formula row with:

```python
expected = self.anchor.nola
```

Keep existing `nowc_agg`, `noa_agg`, and `net_debt` registrations.

Register `equity_reformulated_fy` from the existing:

```text
Equity (NOA - Net Debt)
```

latest-FY formula cell, expected:

```python
self.anchor.equity
```

Do not make `Reported Equity`, the classification cells, or historical source values practice cells in this step.

### Preserve formula identity

Each registration must use the exact formula string already present in the Answer Key cell:

```python
formula = str(ws.cell(row=..., column=lc).value)
```

Do not construct a second semantically equivalent formula only for metadata.

### TDD — reference formula integrity

Add a test that builds the pair, loads the Answer Key semantic map, and for each of the 15 historical reformulation components through `equity_reformulated_fy` asserts:

```python
comp.formula.startswith("=")
answer_key_cell.value == comp.formula
comp.expected_value is not None
```

For aggregate components additionally assert the formula uses the existing classification-table aggregation mechanism (`SUMIF`) where appropriate.

Add a regression proving classification/setup remains supplied:

```python
trainer = load_workbook(trainer_path, data_only=False)
answer = load_workbook(answer_key_path, data_only=False)
# For every classification detail row:
assert trainer["Condensed Financials"].cell(row, 2).value == answer["Condensed Financials"].cell(row, 2).value
assert trainer["Condensed Financials"].cell(row, 2).value in BALANCE_SHEET_CATEGORIES
```

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "historical or classification" -v
```

---

## Task 4 — Register the complete latest-comparable DuPont calculation chain

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### Existing rows

`ALT DuPont` already calculates:

```text
RNOA
After-tax CoD
Spread
FLEV
ROE (decomposed)
Actual ROE
```

Currently only `rnoa`, `spread`, and `roe_decomp` are semantic practice components.

Register the other three formulas from their existing latest-comparable cells:

```text
after_tax_cod
    expected = dup["After-tax CoD"][j_last]

flev
    expected = dup["FLEV"][j_last]

actual_roe
    expected = dup["Actual ROE"][j_last]
```

Keep existing registrations for:

```text
rnoa
spread
roe_decomp
```

### Formula integrity requirements

The registered formulas must preserve the accounting logic already accepted in Step 3/4:

```text
RNOA       = NOPAT / average NOA
After-tax CoD = Net Interest After Tax / average Net Debt
Spread     = RNOA - After-tax CoD
FLEV       = average Net Debt / average Equity
ROE decomp = RNOA + FLEV * Spread
Actual ROE = Net Income / average Equity
```

Do not change the formulas merely to make registration easier.

### TDD

Extend the DuPont integrity regression so all six IDs exist and each Answer Key cell equals its semantic-map formula.

Assert the expected values match `self.anchor.dupont` results for the latest comparable period.

Also assert dependency order from the catalog is valid.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "dupont or cod or flev or roe" -v
```

---

## Task 5 — Prove the Trainer teaches formulas, not transcription

**Files:**
- Modify: `core/tests/test_trainer.py`
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`

### Practice-cell contract after expansion

For all 27 semantic components:

```text
Trainer:
    value = blank
    fill = FFFF00
    comment = none

Answer Key:
    value = working =formula
    fill = FFFF00
    legacy Note = non-empty
```

`test_trainer_and_answer_key_practice_contract` should now naturally cover all 27 components.

### Explicit non-practice input guardrails

Add a regression named equivalently to:

```python
def test_source_data_classifications_and_assumptions_remain_populated(tmp_path):
    ...
```

It must prove at least all of the following:

1. Raw `Income Statement`, `Balance Sheet`, and `Cash Flow Statement` source values are identical between Trainer and Answer Key for representative non-empty source cells.
2. Every balance-sheet classification choice in the Condensed Financials classification table remains populated and identical between Trainer and Answer Key.
3. Scenario/model hard-coded assumption cells that already exist (for example Cost of Equity, Tax rate, Terminal growth, Diluted Shares, probability inputs, and NOPAT margin inputs) remain populated and identical between Trainer and Answer Key.
4. None of those supplied input cells appears in the semantic practice map.

Do not require every blue assumption in the future model to be redesigned in this step. This test is a guardrail against accidentally blanking supplied inputs while expanding formula practice.

### Workbook-wide Check regression

Update count expectations from 13 to 27 where tests intentionally assert total component count.

Preserve the existing mixed correct/incorrect/blank test and cache-preservation regression. They should work without changes to Check architecture because all new components are formulas.

Add one expanded-chain test:

```text
- enter the correct formula for effective_tax_rate_fy -> green
- enter a wrong formula for owca_agg -> red
- leave after_tax_cod blank -> yellow
- run Check and verify the three states
```

No formula, expected value, or hint may appear in CLI output.

### Documentation wording

Update user-facing documentation to state the same product principle as `TARGET.md`:

```text
The Trainer supplies source financials, classifications, market data, and assumptions.
Yellow practice cells are model-construction formulas: links, reformulation, ratios,
forecast calculations, and valuation logic.
```

Do not describe classification or literal number entry as exercises.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

---

## Task 6 — Full regression, demo regeneration, and handoff evidence

**Files:**
- Modify: `RESULT.md`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Regenerate/update: `example/DEMO_HK_Answer_Key.xlsx`

### Required commands

Run at minimum:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core --help
```

Fresh demo Check should report:

```text
Checked 27 practice cells: 0 correct, 0 incorrect, 27 blank.
```

If the exact count differs, stop and reconcile it against the explicit 27-component catalog above; do not silently update the plan or test to match accidental extra/missing components.

### Artifact audit

Using openpyxl/test code, verify the generated pair:

**Trainer**
- exactly 27 registered practice cells;
- all 27 blank/yellow/no Notes immediately after build;
- no `_ComponentMap`, `_RefFormulas`, `_RefValues`, `_TrainerMeta`;
- no Trainer answer sidecars;
- source statements remain populated;
- classification choices remain populated;
- model/scenario assumptions remain populated.

**Answer Key**
- exactly 27 registered practice components;
- all 27 practice cells contain working formulas;
- all 27 practice cells are yellow and have non-empty legacy Notes;
- embedded Answer Key semantic map remains available to Check.

**Historical chain**
- 21 historical reformulation + DuPont components exist exactly as listed;
- formulas at semantic coordinates equal the workbook formulas;
- aggregate formula components use the established classification logic;
- DuPont formulas retain accepted NOPAT / NIAT / NOA / Net Debt / Equity relationships.

**Repository hygiene**
- no committed/generated `*_reference.xlsx`;
- generated Answer-Key JSON sidecars remain ignored rather than tracked;
- no Hint/Reveal/macro surfaces return.

### RESULT.md handoff

Record:

```text
Status: Step 6 complete

Implementation checkpoint used:
- 1db2b333 chat 5 corrected

Product decision implemented:
- source data / classifications / assumptions remain supplied
- formula-construction cells are the practice surface

Practice surface:
- total components: 27
- historical reformulation + DuPont: 21
- existing forecast/valuation: 6
- list all 14 newly added component IDs

Tests run:
- exact commands and pass counts

Artifact audit:
- Trainer 27 blank/yellow/no Notes
- Answer Key 27 formula/yellow/Notes
- supplied source/classification/assumption cells preserved
- Check fresh count 0/0/27
- no Trainer answer leakage

Unresolved:
- only real remaining issues; write `none` only if true
```

Stop after updating `RESULT.md`. Do not commit or push.

---

## Acceptance criteria

Step 6 is acceptable only if all are true:

1. Practice remains formula-only; no literal-input/classification exercise architecture is added.
2. `COMPONENT_CATALOG` has exactly 27 coordinate-free formula components in contiguous dependency order.
3. The historical reformulation + DuPont practice chain contains exactly 21 components.
4. `effective_tax_rate_fy`, `net_interest_fy`, and `net_interest_after_tax_fy` expected values come from authoritative `compute_anchor()` outputs.
5. OWCA, OWCL, OLTA, OLTL, Financial Assets, and Financial Liabilities aggregate formulas are registered from the existing classification-driven workbook rows.
6. `nola_agg` and `equity_reformulated_fy` are registered from their existing reference formulas.
7. All six latest-comparable DuPont formulas are practice components: RNOA, After-tax CoD, Spread, FLEV, ROE decomposition, Actual ROE.
8. Raw financial-statement numbers remain populated in Trainer.
9. Balance-sheet classification choices remain populated in Trainer.
10. Existing market/scenario assumption inputs remain populated in Trainer.
11. Trainer has 27 blank/yellow/no-Note practice cells and no answer-bearing metadata.
12. Answer Key has 27 corresponding working formulas/yellow/legacy Notes.
13. Workbook-wide Check still works across all 27 cells and remains cache-safe/non-disclosing.
14. Existing accounting, identity, line-resolution, visual-parity, and leakage tests remain green.
15. Demo pair is regenerated and repository hygiene remains clean.

---

## ChatGPT review protocol after the user pushes the implementation checkpoint

ChatGPT should inspect the pushed commit without rerunning Cursor's tests unless explicitly requested.

Review in this order:

1. Confirm `RESULT.md` reports the exact verification commands and 27-component artifact count.
2. Inspect `component_catalog.py`: exactly 27 formula components, no literal-input architecture, coherent dependencies.
3. Inspect `financial_math.py`: new expected metrics derive from existing authoritative series, not duplicated ad-hoc formulas.
4. Inspect `reference_model.py`: registrations point to existing workbook formulas rather than invented parallel formulas.
5. Verify classifications/source data/assumptions were not added to the semantic practice surface.
6. Verify Trainer still strips all registered formula answers and Answer Key retains formula + Note.
7. Verify Check architecture did not regress from cache-safe OOXML fill updates.
8. Inspect docs/examples for the formula-construction framing.
9. Only after acceptance, plan the next coherent chain: **forecast-construction practice with visibly supplied assumptions**, rather than random additional cells.
