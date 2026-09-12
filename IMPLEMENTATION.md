# Step 9G.1 — Cross-Company Historical Robustness Matrix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `f1cc147c59a4ca04070140eec89981dcb8723548` (`Step 9F3`, Step 9F.3 complete). Implement only Step 9G.1 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, Step 9B working-capital diagnostics, Step 9C profitability drivers/change attribution, Step 9D ROE attribution, Step 9E cash-conversion trends, and the complete Step 9F per-share / normalized-per-share surface. Do not add forecasting, valuation, new accounting topics, segment analysis, ROU/deferred-tax alternatives, automatic investment conclusions, or new public CLI commands. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Prove that the completed historical curriculum works end-to-end on multiple materially different non-financial company shapes rather than only the illustrative demo, before any forecasting or valuation work begins.

**Architecture:** This is a robustness checkpoint, not a new user-facing feature. Add three deterministic synthetic non-financial company archetypes and a parameterized full-stack test matrix that exercises standardized serialization, manual HK ingestion, reference build, Trainer sanitization, workbook-wide Check, optional-module gating, judgment-aware dynamic expecteds, and trusted-cell tamper protection. Add no new semantic families, worksheets, CLI commands, or historical inputs. Production code should remain unchanged unless a fixture exposes a genuine generalized defect; any such fix must be minimal, fixture-agnostic, and covered by a focused regression test in the owning module.

**Tech Stack:** Python, pytest, openpyxl, existing `StandardizedFinancials`, `HistoricalShareData`, `standardized_to_payload`, `HKManualDocumentAdapter`, `ReferenceModelBuilder`, `build_training_workbook`, `load_semantic_map`, `group_components_by_family`, `check_workbook`, and existing cached-formula injection helpers.

**Spec:** `TARGET.md`, especially the historical practice-surface expansion sequence: accounting analysis -> research diagnostics -> **cross-company robustness** -> forecasting, plus the non-financial-company scope, no-invented-historical-input rule, optional-topic gating, workbook-wide Check, and trusted historical-model requirements.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Do not add a new user-facing worksheet, formula family, practice cell, CLI command, hint/reveal mechanism, forecast, scenario, or valuation output.
- Preserve current ordinary-demo surfaces exactly:
  - no assumptions / no share history: `62 families / 259 practice cells`;
  - normalization assumptions / no share history: `66 / 279`.
- Preserve current share-enabled surfaces exactly:
  - shares / no normalization: `70 / 293`;
  - shares + normalization: `78 / 331`.
- Preserve every existing family order through `NORMALIZED_PER_SHARE_COMPONENT_CATALOG` order `78`.
- Synthetic robustness companies are test fixtures only. Do not present them as real listed companies or as product examples containing factual market data.
- Every modeled source value in a fixture must be explicit. Do not use forecast defaults, generated balancing plugs, random values, or runtime fabrication.
- Every fixture must have five strictly chronological fiscal years: FY2021–FY2025 ending December 31.
- Every fixture must satisfy existing source/reformulation integrity rather than weakening validators.
- Preserve sign conventions and current `#N/A` behavior.
- Do not special-case fixture names in production code.
- If a new matrix test exposes a production defect, first add a focused failing regression test in the owning module, then make the smallest generalized fix. Do not relax the fixture or assertion merely to fit current behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Accepted Step 9F.3 baseline

Commit `f1cc147c5` records:

- `266 passed` locally;
- ordinary demo unchanged at `62/259` and `66/279`;
- share-only fixture at `70/293`;
- share + normalization at `78/331`;
- normalized diluted EPS bridge active only when both normalization and historical diluted-share inputs exist;
- live Normalization Judgment recomputes normalized EPS while reported EPS remains reported;
- no forecasting or valuation has begun.

The next dependency in `TARGET.md` is cross-company robustness. This checkpoint therefore validates breadth without expanding curriculum scope.

---

### Task 1: Add three materially different deterministic company fixtures

**Files:**
- Create: `core/tests/cross_company_fixtures.py`
- Test: `core/tests/test_cross_company_robustness.py`

**Interfaces:**
- Produces: `RobustCompanyCase` plus exactly three fixture factories:
  - `asset_light_services_case()`
  - `inventory_retail_case()`
  - `capital_intensive_manufacturer_case()`
- Each case returns explicit `StandardizedFinancials`, an assumptions dict, expected family/cell counts, and expected optional-sheet presence.

Use:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RobustCompanyCase:
    key: str
    financials: StandardizedFinancials
    assumptions: dict
    expected_families: int
    expected_cells: int
    expect_normalization: bool
    expect_per_share: bool
    expect_asset_scaled_quality: bool
```

Use one shared period axis:

```python
PERIODS = tuple(date(y, 12, 31) for y in range(2021, 2026))
```

Add helpers that map five explicit values to the five periods. No randomization.

#### Fixture A — `asset_light_services_case()`

Purpose: asset-light, net-cash-leaning service profile, working capital present, no Total Assets line, no share history, no normalization.

Use exactly these five-year series:

```text
Revenue                 1000, 1200, 1400, 1600, 1800
Profit before tax        120,  144,  168,  192,  216
Income tax expense       -20,  -24,  -28,  -32,  -36
Finance costs             -5,   -6,   -7,   -8,   -9
Finance income            10,   12,   14,   16,   18
Profit for the year      100,  120,  140,  160,  180
Operating cash flow      110,  130,  155,  175,  200

Cash                     300,  330,  360,  390,  420
Trade receivables        100,  120,  140,  160,  180
PPE                       50,   55,   60,   65,   70
Trade payables            80,   96,  112,  128,  144
Bank borrowings           30,   25,   20,   15,   10
Total equity             340,  384,  428,  472,  516
```

Do **not** supply `Total assets` or `Total liabilities`. This is intentional: core earnings-quality diagnostics should exist, but `average_total_assets`, `accrual_ratio`, and `accrual_ratio_change` must be absent.

Expected surface:

```text
59 families / 248 practice cells
Earnings Quality: present
Working Capital Analysis: present
Earnings Normalization: absent
Per Share Analysis: absent
```

#### Fixture B — `inventory_retail_case()`

Purpose: inventory-heavy retailer, declining revenue in one period, explicit short-term-investment judgment, normalization candidate, and diluted-share history.

Use exactly:

```text
Revenue                 2000, 2300, 2600, 2400, 2800
Profit before tax        180,  210,  240,  160,  250
Income tax expense       -30,  -35,  -40,  -26,  -41
Finance costs            -20,  -22,  -25,  -27,  -30
Finance income             2,    2,    3,    3,    4
Profit for the year      150,  175,  200,  134,  209
Restructuring expense      0,    0,  -30,    0,    0
Operating cash flow      140,  180,  220,  100,  260

Cash                     100,  110,  120,  115,  130
Trade receivables         80,   92,  105,   98,  112
Inventories              400,  460,  520,  500,  580
PPE                      300,  320,  340,  360,  380
Short-term investment     60,   65,   70,   75,   80
Total assets             940, 1047, 1155, 1148, 1282
Trade payables           250,  285,  320,  310,  350
Accrued expenses         100,  115,  130,  125,  140
Bank borrowings          200,  220,  240,  250,  260
Total liabilities        550,  620,  690,  685,  750
Total equity             390,  427,  465,  463,  532

Diluted weighted-average shares
                         500,  510,  520,  535,  540
```

Set `Restructuring expense` concept to `restructuring_expense`.
Set historical share `scale_basis="financial_statement_units"`.

Use exactly this assumptions dict:

```python
{
    "classificationOverrides": {},
    "normalizationCandidates": [
        {
            "selector": "concept:restructuring_expense",
            "referenceTreatment": "Non-recurring",
            "scope": "operating_pretax_effective_tax",
            "topic": "Restructuring expense recurring vs non-recurring",
            "referenceRationale": (
                "The synthetic robustness case treats the supplied restructuring "
                "charge as a discrete non-recurring item for training purposes."
            ),
            "consequenceNote": (
                "Recurring treatment leaves reported earnings unchanged; "
                "non-recurring treatment bridges to normalized earnings."
            ),
        }
    ],
}
```

Expected surface:

```text
78 families / 331 practice cells
Earnings Quality: present, including asset-scaled families
Working Capital Analysis: present
Earnings Normalization: present
Per Share Analysis: present, including normalized-per-share families
Accounting Judgment: includes Short-term investment Financial Asset vs OWCA case
```

The FY2024 revenue decline is deliberate. It must preserve signed working-capital change / incremental-ratio arithmetic.

#### Fixture C — `capital_intensive_manufacturer_case()`

Purpose: capital-intensive manufacturer with heavy PP&E, debt, lease-liability judgment, falling diluted share count, no normalization.

Use exactly:

```text
Revenue                 3000, 3200, 3400, 3600, 3900
Profit before tax        260,  270,  280,  300,  330
Income tax expense       -43,  -45,  -46,  -50,  -54
Finance costs            -60,  -65,  -70,  -72,  -75
Finance income             5,    5,    5,    6,    6
Profit for the year      217,  225,  234,  250,  276
Operating cash flow      300,  320,  340,  360,  390

Cash                     150,  145,  140,  155,  160
Trade receivables        300,  320,  340,  360,  390
Inventories              450,  470,  490,  510,  540
PPE                     1800, 1900, 2000, 2100, 2200
Goodwill                  200,  200,  200,  200,  200
Total assets             2900, 3035, 3170, 3325, 3490
Trade payables           350,  365,  380,  395,  420
Bank borrowings          900,  950, 1000, 1050, 1100
Operating lease liabilities
                         200,  210,  220,  230,  240
Total liabilities       1450, 1525, 1600, 1675, 1760
Total equity            1450, 1510, 1570, 1650, 1730

Diluted weighted-average shares
                         800,  800,  795,  790,  785
```

Set the lease-liability concept to `lease_liability`.
Set historical share `scale_basis="financial_statement_units"`.
Use no normalization candidates.

Expected surface:

```text
70 families / 293 practice cells
Earnings Quality: present, including asset-scaled families
Working Capital Analysis: present
Earnings Normalization: absent
Per Share Analysis: present, normalized-per-share families absent
Accounting Judgment: includes lease liability Operating LT Liability vs Financial Liability case
```

- [x] **Step 1: Write fixture-construction tests**

Assert each fixture has five periods, complete required historical series, unique line identities, and the expected share/normalization presence.

- [x] **Step 2: Run fixture tests red, then implement the factories**

Run:

```bash
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -k fixture -v
```

Expected before implementation: fail because the fixture module does not exist.

- [x] **Step 3: Verify all three fixtures pass existing source/reformulation integrity without validator relaxation**

For each case:

```python
validate_financials_identities(case.financials)
report = reconcile_financials(case.financials)
assert all(report.checksums.values())
ReferenceModelBuilder(case.financials, case.assumptions)
```

Do not modify validators merely because a fixture is inconvenient. Correct fixture arithmetic first.

---

### Task 2: Add full-stack build / Check matrix

**Files:**
- Create/Modify: `core/tests/test_cross_company_robustness.py`

**Interfaces:**
- Consumes: all three `RobustCompanyCase` fixtures.
- Produces: one parameterized end-to-end robustness matrix.

- [x] **Step 1: Round-trip each case through the public standardized/manual-ingestion path**

For each case:

```python
payload = standardized_to_payload(case.financials)
json_path.write_text(json.dumps(payload), encoding="utf-8")
ingested = HKManualDocumentAdapter().ingest(
    [DocumentManifest(path=str(json_path), doc_type=DocumentType.OTHER)]
)
```

Assert ticker, five modeled periods, line identities, and historical shares (when present) survive the round-trip.

- [x] **Step 2: Build matched Trainer / Answer Key pairs and assert exact surfaces**

For each case call:

```python
trainer, answer = build_training_workbook(
    ingested,
    tmp_path / f"{case.key}_Trainer.xlsx",
    case.assumptions,
)
smap = load_semantic_map(answer)
assert len(group_components_by_family(smap)) == case.expected_families
assert len(smap.all_ordered()) == case.expected_cells
```

Assert exact case counts:

```text
asset_light_services              59 / 248
inventory_retail                  78 / 331
capital_intensive_manufacturer    70 / 293
```

Also assert expected sheet gating from Task 1.

- [x] **Step 3: Assert every fresh Trainer is entirely blank on the semantic practice surface**

```python
summary = check_workbook(trainer)
assert summary.total == case.expected_cells
assert summary.blank == case.expected_cells
assert summary.correct == 0
assert summary.incorrect == 0
```

- [x] **Step 4: Fill every semantic practice cell with its Answer-Key formula and require workbook-wide green**

Add a test helper:

```python
def _fill_all_practice_formulas(trainer: Path, answer: Path) -> None:
    smap = load_semantic_map(answer)
    wb = load_workbook(trainer, data_only=False)
    for comp in smap.all_ordered():
        row, col = parse_cell_ref(comp.cell)
        wb[comp.tab].cell(row=row, column=col).value = comp.formula
    wb.save(trainer)
    wb.close()
```

Then require:

```python
summary = check_workbook(trainer)
assert summary.correct == case.expected_cells
assert summary.blank == 0
assert summary.incorrect == 0
```

This test is the core cross-company acceptance test: every active formula family must build, sanitize, and Check correctly on each materially different company shape.

- [x] **Step 5: Assert deferred forecast/valuation tabs remain hidden placeholders for all three cases**

For `Model_Bear`, `Model_Base`, `Model_Bull`, and `Scenario_Summary`, require hidden state and the existing deferred-placeholder content. No case may activate the forecast engine.

---

### Task 3: Prove optional gating and live judgment behavior across the matrix

**Files:**
- Modify: `core/tests/test_cross_company_robustness.py`
- Modify production code only if a generalized defect is exposed, with a focused regression in the owning test module.

- [x] **Step 1: Prove asset-scaled quality gating on the services fixture**

Require:

```python
families = {c.family_id for c in smap.all_ordered()}
assert "operating_cash_flow_link" in families
assert "cash_conversion_ratio" in families
assert "total_accruals" in families
assert "average_total_assets" not in families
assert "accrual_ratio" not in families
assert "accrual_ratio_change" not in families
```

This fixture must still retain Working Capital Analysis because receivables/payables are present.

- [x] **Step 2: Prove declining-revenue working-capital arithmetic on the retail fixture**

Identify FY2024 (`period_end == "2024-12-31"`) components for:

```text
revenue_change
nowc_change
incremental_nowc_to_revenue_change
incremental_owca_to_revenue_change
incremental_owcl_to_revenue_change
```

Require `revenue_change.expected_value < 0` and confirm the three incremental-ratio formulas contain no `ABS(` and no `IFERROR`.

- [x] **Step 3: Prove the retail Short-term investment judgment changes live downstream expecteds**

Locate the `Accounting Judgment` row whose line item is `Short-term investment`. The supplied treatment must be `Financial Asset`; change column F to `Operating Working Capital Asset`.

Use a FY2025 working-capital component such as `nowc_to_revenue` or `incremental_owca_to_revenue_change`.

1. Inject a semantic formula with a cached numeric value equal to the original reference-treatment expected value.
2. Run Check after changing the judgment treatment.
3. Require that stale cached value to be rejected as incorrect.
4. Inject the treatment-conditioned alternative expected value and require correct.

Reuse the existing cached-formula injection helper; do not add a second checker path.

- [x] **Step 4: Prove retail normalization changes normalized per-share values but not reported EPS**

On the share+normalization retail case:

- capture the reference expected values for FY2023 `reported_diluted_eps` and `normalized_diluted_eps`;
- change `Normalization Judgment!F` for the restructuring case from `Non-recurring` to `Recurring`;
- require treatment-conditioned `reported_diluted_eps` to remain unchanged;
- require treatment-conditioned `normalized_diluted_eps` to move to the reported EPS level when the normalization adjustment becomes zero;
- require an old cached normalized-EPS value from the reference treatment to be rejected.

Do not add another normalized-EPS formula family.

- [x] **Step 5: Prove manufacturer lease judgment changes financing diagnostics without breaking per-share analysis**

Locate the lease-liability judgment row. Change column F from `Operating Long-Term Liability` to `Financial Liability`.

Require a treatment-conditioned financing component such as `net_debt`, `flev`, or `financing_contribution_to_roe` to change, while `reported_diluted_eps` remains unchanged because reported Net Income and supplied share count are unchanged.

- [x] **Step 6: Prove falling share count has the mechanically correct sign**

For the manufacturer fixture, require the FY2023–FY2025 `share_count_effect_on_diluted_eps_change` expected values to be positive while Net Income is positive and diluted shares fall. Do not label this automatically as “accretion from buybacks”; the fixture supplies no causal source for the share-count movement.

---

### Task 4: Cross-company trusted-boundary and regression verification

**Files:**
- Modify: `core/tests/test_cross_company_robustness.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Do not modify: `TARGET.md`

- [x] **Step 1: Parameterize trusted-source tamper protection across all three cases**

For a fresh Trainer in each case:

1. populate one valid practice formula;
2. overwrite one populated source-statement cell (for example first-period Revenue on `Income Statement`);
3. run Check;
4. require `ValueError` from trusted workbook validation before recoloring;
5. reopen the Trainer and require the valid practice cell still bright yellow.

Do not duplicate trusted validation logic; this test must exercise the existing generic mechanism.

- [x] **Step 2: Preserve ordinary demo regression counts**

Rebuild the existing demo with and without `DEMO_HK_Assumptions.json` and require exactly:

```text
base:          62 families / 259 cells / 0-0-259 blank
normalization: 66 families / 279 cells / 0-0-279 blank
```

- [x] **Step 3: Preserve share-enabled regression counts**

Reuse existing Step 9F fixtures and require:

```text
shares only:              70 / 293
shares + normalization:   78 / 331
```

- [x] **Step 4: Update documentation without claiming real-company validation**

In `skills/bav-trainer/SKILL.md`, add a short `Step 9G.1 — cross-company robustness` note stating that the historical engine is now regression-tested against three deterministic non-financial archetypes: asset-light services, inventory-heavy retail, and capital-intensive manufacturing. Explicitly say they are synthetic robustness fixtures, not empirical company data.

In `RESULT.md`, record:

```text
Status: Step 9G.1 complete — cross-company historical robustness matrix
implementation base: f1cc147 Step 9F.3 complete
matrix cases: 3/3 build + fresh Check + fully-filled Check pass
asset-light services: 59 families / 248 cells
inventory retail: 78 / 331
capital-intensive manufacturer: 70 / 293
ordinary demo preserved: 62/259 and 66/279
share-enabled regressions preserved: 70/293 and 78/331
TARGET.md unchanged
default CLI unchanged
forecasting / valuation not begun
```

Record the actual final pytest count; do not prestate it.

- [x] **Step 5: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality_change.py -v
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
PYTHONPATH=. pytest core/tests/test_profitability_drivers.py -v
PYTHONPATH=. pytest core/tests/test_profitability_change.py -v
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [x] **Step 6: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count in `RESULT.md`.

- [x] **Step 7: Verify public CLI remains exactly unchanged**

Require the public command set to remain:

```text
{ingest, build, check, list}
```

---

## Defect Policy

This checkpoint may reveal a generalized production bug because it intentionally broadens company shapes. If that happens:

1. keep the fixture unchanged unless its arithmetic is objectively inconsistent;
2. add a minimal focused regression test in the owning module (`classification`, `line_resolver`, `financial_math`, `working_capital`, `per_share`, `checker`, etc.);
3. fix the generalized semantic rule, not the fixture name;
4. rerun the full cross-company matrix and the entire test suite;
5. document the defect and fix in `RESULT.md`.

Do not use this checkpoint as permission to redesign the engine or introduce a new curriculum topic.

---

## Definition of Done

Step 9G.1 is complete only when all of the following are true:

1. three deterministic five-year non-financial archetypes exist: asset-light services, inventory-heavy retail, capital-intensive manufacturing;
2. each fixture passes current source and reformulation integrity without validator relaxation;
3. each fixture survives standardized payload -> manual HK adapter round-trip;
4. services builds exactly `59 families / 248 cells`;
5. retail builds exactly `78 / 331`;
6. manufacturer builds exactly `70 / 293`;
7. fresh Check is entirely blank/yellow for every fixture;
8. copying every Answer-Key formula into every practice cell produces an all-green Check for every fixture;
9. services omits only the Total-Assets-dependent quality families as designed;
10. retail declining-revenue working-capital diagnostics preserve signed arithmetic;
11. retail live Short-term-investment classification changes downstream expected values and rejects stale cached results;
12. retail live Normalization Judgment changes normalized EPS without changing reported EPS;
13. manufacturer lease classification changes financing diagnostics without changing reported EPS;
14. manufacturer falling share count produces the mathematically correct share-count effect without causal labeling;
15. trusted source-cell tampering fails before recolor on all three fixtures;
16. ordinary demo remains `62/259` and `66/279`;
17. existing share-enabled regressions remain `70/293` and `78/331`;
18. no new semantic family, user-facing worksheet, CLI command, forecast, or valuation output is added;
19. the full `core/tests/` suite passes;
20. `TARGET.md` remains unchanged;
21. `RESULT.md` records the actual final test count and matrix results;
22. Cursor performs no Git operations.

Stop after Step 9G.1 and report the implementation results. Do not begin forecasting or valuation in the same checkpoint.
