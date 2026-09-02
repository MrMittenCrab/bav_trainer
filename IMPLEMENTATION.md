# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.
- Cursor must update `RESULT.md` before handoff so the exact test commands/results are visible in the committed checkpoint.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

Commit `d327347` (`chat reference 2B`) substantially completes Step 2B. The trainer now has one canonical `resolve_line()` used by both Python expected-value math and Excel source-row construction; the supplied demo tax line resolves correctly; optional interest-income / interest-expense cases remain populated; the workbook and Python share the same equity alias/fallback behavior; and `RESULT.md` reports 34 passing core tests.

The next blocker is no longer source-line lookup. It is **balance-sheet classification and source-data integrity**.

### Review findings from commit `d327347`

1. **The model can still be internally consistent while economically wrong because classification is not reconciled.** `financial_math.guess_classification()` recognizes only a small keyword set and returns `Ambiguous — Operating` for everything else. `compute_anchor()` then ignores that ambiguous category entirely because it only sums the six operating/financial categories. A balance-sheet line can therefore disappear from NOA / Net Debt without any error.
2. **The classification contract has drifted from the parent BAVGEM model.** The trainer dropdown currently offers six operating/financial categories plus `Ambiguous — Operating` and `Ambiguous — Financial`. The BAVGEM Stage-3 contract instead uses eight real accounting destinations: the six operating/financial categories plus `Equity` and `Exclude`; genuinely ambiguous items receive a review flag while still carrying a real default category.
3. **The supplied demo exposes the problem.** For FY2025, the currently classified detail produces implied equity of approximately `7,025` while reported Total Equity is `8,700`, a gap of `1,675`. Earlier years also have gaps. The source totals balance, but the detail supplied to the reformulation is incomplete, so current tests can pass while the BAV reformulation does not tie.
4. **The workbook currently hides that gap.** Its `Equity` row links reported equity when a total-equity line exists. It does not show `Equity = NOA - Net Debt`, `Reported Equity`, and a reconciliation `CHECK` as separate rows. DuPont can therefore consume reported equity even when the classified NOA / Net Debt system does not reconcile to it.
5. **`build` does not enforce the existing ingestion reconciliation report.** `cmd_ingest()` reports checksum failures, but `build_training_workbook()` proceeds directly to model construction. The current demo cash-flow data is arithmetically inconsistent (`CFO + CFI + CFF != Net change in cash`) yet a Trainer / Answer Key can still be generated.
6. **Existing validators are too weak to detect detail completeness.** `validate_balance_sheet()` checks only `Total Assets = Total Liabilities + Total Equity`; it does not prove that the non-subtotal detail being classified sums to those totals. Equal omissions on the asset and liability sides could therefore evade even an implied-equity check.
7. **The parent BAVGEM already contains the right domain contract.** `skills/bav-pipeline/references/stage2_assembler.md` makes source checksums blocking, and `stage3_analyst.md` requires complete classification, the eight-category dropdown, implied Equity = NOA − Net Debt, Reported Equity, and an explicit reconciliation CHECK. Reimplementing a different trainer-specific accounting convention creates avoidable drift.
8. **The trainer skill itself is stale.** `skills/bav-trainer/SKILL.md` still describes a hidden `*_reference.xlsx`, visible adjacent hints, and the older workflow even though `TARGET.md` and runtime now use a paired Trainer / Answer Key with Notes.
9. **One small resolver drift remains.** `_default_assumptions()` still derives its metadata `anchorRevenue` from `income_statement[0]` instead of the canonical revenue resolver. It does not drive the current scenario engine, but it should not be allowed to become a second revenue-selection rule.

## BAVGEM integration decision

Use **selective integration**, not full runtime coupling.

### Reuse now

Treat these existing BAVGEM documents as the canonical domain contracts for the corresponding trainer logic:

- `skills/bav-pipeline/references/stage2_assembler.md` — source-statement sign conventions and blocking arithmetic checks;
- `skills/bav-pipeline/references/stage3_analyst.md` — balance-sheet classification categories, reformulation identities, and DuPont accounting definitions;
- `skills/bav-pipeline/references/stage4_modeler.md` — later, when the trainer expands the valuation / DCF layer.

The implementation should extract reusable **pure Python domain logic into `core/`** and have the Trainer / Answer Key build use it. Do **not** import markdown skill files at runtime.

### Do not integrate yet

Do not wire the trainer to BAVGEM's SEC/edgartools sourcing, coverage-vault orchestration, subagent gates, quarterly sections, Core Earnings Bridge, earnings-quality screens, Price Rationalization, ICC, sensitivity grids, or DCF feature chain in this step. Those are useful parent capabilities, but they would obscure the immediate problem: the trainer's annual accounting base must first reconcile.

The intended long-run direction is one shared accounting/valuation engine with different front ends. This step only moves the Stage-2/3 accounting core in that direction.

---

## Active implementation step

### Step 3 — Adopt the BAVGEM Stage-2/3 accounting integrity contract

**Goal**

Make the annual source data and balance-sheet reformulation trustworthy before expanding the trainer exercise catalog: every non-subtotal balance-sheet line must receive a real BAVGEM classification, the classified detail must reconcile to reported totals when those totals are available, `Equity = NOA - Net Debt` must tie Reported Equity, and a build must refuse source data whose evaluatable statement checks fail.

Do **not** add new trainer practice components in this step.

## Required changes

### 1. Create a canonical balance-sheet classification / reformulation module

Create `core/model/classification.py`. This becomes the sole authority for balance-sheet classification used by both Python expected-value math and the workbook builder.

Use these category strings exactly:

```python
BALANCE_SHEET_CATEGORIES = (
    "Operating Working Capital Asset",
    "Operating Working Capital Liability",
    "Operating Long-Term Asset",
    "Operating Long-Term Liability",
    "Financial Asset",
    "Financial Liability",
    "Equity",
    "Exclude",
)
```

Use focused types equivalent to:

```python
@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    ambiguous: bool = False
    reason: str = ""
    overridden: bool = False


@dataclass(frozen=True)
class BalanceSheetReformulation:
    decisions: dict[int, ClassificationDecision]
    category_totals: dict[str, tuple[float, ...]]
    nowc: tuple[float, ...]
    nola: tuple[float, ...]
    noa: tuple[float, ...]
    net_debt: tuple[float, ...]
    implied_equity: tuple[float, ...]
    reported_equity: tuple[float | None, ...]
    total_assets: tuple[float | None, ...]
    total_liabilities: tuple[float | None, ...]
    asset_detail_gap: tuple[float | None, ...]
    liability_detail_gap: tuple[float | None, ...]
    equity_gap: tuple[float | None, ...]
```

Public behavior should be exposed through functions equivalent to:

```python
def classify_balance_sheet_line(
    item: LineItem,
    *,
    override: str | None = None,
) -> ClassificationDecision:
    ...


def reformulate_balance_sheet(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    overrides: dict[str, str] | None = None,
) -> BalanceSheetReformulation:
    ...
```

Add explicit exception types for an unclassifiable line and an invalid override. Never silently drop an unrecognized non-subtotal line.

### 2. Implement the Stage-3 classification defaults, with ambiguity as metadata rather than a fake accounting category

The classifier should use safe normalized-label rules and always return one of the eight real categories.

At minimum implement these deterministic defaults:

- cash / cash equivalents / marketable securities / generic investments → `Financial Asset`;
- debt / borrowings / notes payable / commercial paper → `Financial Liability`;
- trade/accounts receivables, inventory, prepaid items, and clearly labelled other **current assets** → `Operating Working Capital Asset`;
- trade/accounts payables, accrued operating liabilities, deferred revenue, and clearly labelled other **current liabilities** → `Operating Working Capital Liability`;
- PP&E, goodwill, intangibles, and clearly labelled other **non-current assets** → `Operating Long-Term Asset`;
- clearly labelled other **non-current liabilities** → `Operating Long-Term Liability`;
- share capital, paid-in capital, reserves, AOCI, retained earnings, treasury-stock/equity lines → `Equity`.

Items that BAVGEM explicitly treats as judgment calls should receive a valid default **plus** `ambiguous=True` and a concise reason, rather than `Ambiguous — Operating` / `Ambiguous — Financial`. At minimum cover:

- operating lease ROU assets / lease liabilities;
- deferred-tax assets / liabilities;
- pension obligations;
- short-term investments;
- equity-method investments.

Keep the default conservative and documented; the exact default matters less than making the uncertainty visible and overridable.

A non-subtotal line that cannot be safely classified must raise an `UnclassifiedBalanceSheetLineError` naming the line. Do not default unknown items to operating and do not default them to `Exclude`.

### 3. Support explicit classification overrides without creating a second registry

Add an optional top-level assumptions mapping:

```json
{
  "classificationOverrides": {
    "Operating lease liabilities": "Financial Liability"
  }
}
```

Requirements:

- keys are matched by normalized exact balance-sheet label;
- values must be one of `BALANCE_SHEET_CATEGORIES`;
- overrides are applied before default classification;
- the resulting `ClassificationDecision` sets `overridden=True`;
- the same override map drives both `compute_anchor()` and the Excel classification table;
- do not store workbook coordinates in the override map.

`_default_assumptions()` should include an empty `classificationOverrides` object. Custom assumptions files that omit it remain valid.

### 4. Make Python `compute_anchor()` consume the shared reformulation

Remove `CLASSIFICATIONS`, `CAT_NAMES`, and `guess_classification()` from `core/model/financial_math.py` once the new module replaces them.

Change `compute_anchor()` so it calls `reformulate_balance_sheet()` exactly once and uses that result for:

- NOWC;
- NOLA;
- NOA;
- Net Debt;
- Equity used in DuPont / leverage.

`AnchorMetrics.equity` must be the **implied reformulated equity** (`NOA - Net Debt`), not a separate reported-equity series. When reported equity exists and the reformulation reconciles, the values are equal; when it does not reconcile, the build should fail rather than silently switching definitions.

Expose the reformulation diagnostics on `AnchorMetrics` (for example `reformulation: BalanceSheetReformulation`) so `ReferenceModelBuilder` can reuse the same classification decisions rather than classifying the lines a second time.

Extend `core/model/line_resolver.py` with canonical `total_assets` and `total_liabilities` concepts using narrow exact aliases. Do not reintroduce fuzzy substring matching.

Also change `_default_assumptions()` in `ReferenceModelBuilder` so `meta.anchorRevenue` is obtained through `resolve_line(..., "revenue", required=True)` rather than `income_statement[0]`.

### 5. Add the BAVGEM detail-completeness checks

`reformulate_balance_sheet()` must calculate three independent diagnostics when the corresponding reported totals are available:

```text
classified asset detail
  = OWCA + OLTA + Financial Assets

classified liability detail
  = OWCL + OLTL + Financial Liabilities

implied equity
  = NOA - Net Debt
```

Compare against:

```text
reported Total Assets
reported Total Liabilities
reported Total Equity
```

Use a small absolute tolerance appropriate for the workbook units (default `1.0`, configurable only if an existing tolerance convention requires it).

This is deliberately stronger than checking only `Assets = Liabilities + Equity`: if both asset and liability detail omit the same amount, the accounting equation can still balance while the model is incomplete.

If a reported total is unavailable, return `None` for that gap and mark it unverified; do not fabricate a total.

Before the reference workbook is finalized, fail with a clear `ReformulationIntegrityError` when any available asset-detail, liability-detail, or implied-equity gap exceeds tolerance. The error must report period + gap + which check failed.

### 6. Enforce existing source-statement reconciliation before building the Answer Key

The build path itself must honor the ingestion checks.

In `core/trainer/workbook.py` (or one focused build-readiness helper called from it), call the existing reconciliation layer before `ReferenceModelBuilder.build()`.

If an evaluatable checksum is `False`, refuse to create the Trainer / Answer Key and report which statement failed. Do not make users run `python -m core ingest` separately to discover that the same input is invalid.

Do not broaden this step into a full new filing parser. Reuse the current `reconcile_financials()` / validator stack and improve only what is required for deterministic build blocking.

Where validators currently resolve concepts independently, migrate the overlapping concepts to `line_resolver.py` rather than adding new fuzzy rules.

### 7. Rebuild the Condensed Financials balance-sheet block around the Stage-3 contract

`ReferenceModelBuilder` must use `self.anchor.reformulation.decisions` (or the equivalent shared result) to populate the classification table. It must not call a separate workbook-only classifier.

#### Classification table

- keep every non-subtotal balance-sheet line exactly once;
- dropdown choices are the eight `BALANCE_SHEET_CATEGORIES`, no `Ambiguous — ...` values;
- set `allow_blank=False`;
- use the shared decision's category as the default;
- add a visible `Notes` column (after the period values is acceptable) that shows concise `⚠ Review: ...` text for `ambiguous=True` decisions and an override note for overridden decisions;
- preserve the current formula-driven SUMIF behavior when the user changes a dropdown.

#### Compact aggregates / reconciliation block

Add these labelled rows with formula-driven period columns:

```text
Operating Working Capital Assets
Operating Working Capital Liabilities
NOWC
Operating Long-Term Assets
Operating Long-Term Liabilities
NOLA
NOA
Financial Assets
Financial Liabilities
Net Debt
Equity (NOA - Net Debt)
Reported Equity
Total Capital
CHECK
```

Definitions:

```text
NOWC = OWCA - OWCL
NOLA = OLTA - OLTL
NOA = NOWC + NOLA
Net Debt = Financial Liabilities - Financial Assets
Equity = NOA - Net Debt
Total Capital = Net Debt + Equity
```

`Reported Equity` links to the canonical raw balance-sheet total when present. If absent, leave it visibly unverified rather than inventing a value.

`CHECK` must be a live formula that returns `OK` when implied and reported equity tie within tolerance, `CHECK` when they do not, and `UNVERIFIED` when no reported-equity total exists.

Keep the existing semantic registrations for `nowc_agg`, `noa_agg`, and `net_debt`, but resolve them to the new rows at build time. Do not put coordinates into `COMPONENT_CATALOG`.

DuPont FLEV / Actual ROE must continue using the reformulated `Equity (NOA - Net Debt)` row.

### 8. Repair the illustrative demo instead of weakening the integrity checks

`example/DEMO_HK_Standardized.json` is synthetic and currently incomplete. Make it internally coherent so it remains a valid demo for the stricter build.

Add these non-subtotal balance-sheet lines:

```text
Other non-current assets
FY2021 1670
FY2022 1894
FY2023 2282
FY2024 2804
FY2025 3500

Other non-current liabilities
FY2021 1305
FY2022 1456
FY2023 1593
FY2024 1716
FY2025 1825
```

These values make the supplied detailed assets/liabilities reconcile to the existing reported totals without changing Total Assets, Total Liabilities, or Total Equity.

Also correct `Net cash from operating activities` so the existing three cash-flow sections add to the existing `Net change in cash and cash equivalents`:

```text
FY2021 1450
FY2022 1600
FY2023 1750
FY2024 1930
FY2025 2070
```

Do not change the reported net-change row or balance-sheet cash series; FY2022–FY2025 net changes already match the year-over-year cash movement.

The new classifier must classify the two added lines as Operating Long-Term Asset / Liability.

### 9. Add tests that fail on the current commit for the actual remaining defects

Create `core/tests/test_classification.py` for pure classification/reformulation tests and extend `core/tests/test_reference_integrity.py` for workbook/build behavior.

At minimum add these tests:

1. `test_bav_categories_are_exact_eight` — exact category strings, including Equity / Exclude and no `Ambiguous — ...` category.
2. `test_equity_components_classify_as_equity` — `Share capital and reserves` resolves to `Equity`.
3. `test_other_noncurrent_defaults` — the two new demo labels resolve to OLTA / OLTL.
4. `test_ambiguous_item_has_real_default_and_flag` — e.g. an operating-lease liability receives a real category with `ambiguous=True`.
5. `test_unknown_line_requires_override` — an unrecognized non-subtotal line raises and then succeeds with an exact valid override.
6. `test_invalid_override_rejected` — fake category string raises clearly.
7. `test_reformulation_detects_equal_asset_liability_omissions` — synthetic BS totals satisfy `A=L+E` but classified asset/liability detail each omit the same amount; the asset/liability detail gaps must still fail. This proves the new check is stronger than the old balance-sheet checksum.
8. `test_demo_reformulation_reconciles_all_years` — after repairing the fixture, asset-detail, liability-detail, and equity gaps are zero (within tolerance) for every fiscal year.
9. `test_demo_reconciliation_report_passes` — the repaired demo's currently evaluatable IS / BS / CF checks all pass.
10. `test_build_rejects_failed_source_checksum` — a synthetic input with an evaluatable broken cash-flow roll-up cannot produce an Answer Key.
11. `test_build_rejects_reformulation_gap` — balanced reported totals plus incomplete classified detail cannot produce an Answer Key.
12. `test_condensed_has_live_reconciliation_rows` — Answer Key contains the required aggregate, implied Equity, Reported Equity, Total Capital, and CHECK rows; CHECK is a formula.
13. `test_classification_table_uses_shared_decisions` — workbook defaults match `anchor.reformulation.decisions`, the dropdown contains only the eight categories, and ambiguous/override notes are visible.
14. `test_duPont_uses_implied_equity` — FLEV / Actual ROE reference the `Equity (NOA - Net Debt)` row, not a raw reported-equity row.
15. Existing line-resolver, reference-integrity, paired-workbook, and ten-year forecast tests remain unchanged and passing unless a row lookup in a test needs to become label-driven because of the expanded Condensed block.

Do not weaken a current assertion merely because row numbers move. Tests should locate semantic/labelled rows rather than pinning the old layout.

### 10. Synchronize the `bav-trainer` skill with the actual product

Update `skills/bav-trainer/SKILL.md` after the runtime work passes.

It must describe:

- paired `*_Trainer.xlsx` / `*_Answer_Key.xlsx` outputs, not a user-facing `*_reference.xlsx`;
- blank yellow/no-Note Trainer practice cells;
- yellow formula/input cells with legacy Notes in the Answer Key;
- static Answer Key as the primary feedback loop, with Check/Hint/Reveal optional;
- no adjacent visible hint-cell behavior as the normal generated UX;
- Stage 2 / Stage 3 / Stage 4 BAVGEM references as the canonical domain rubrics, while HK ingestion and trainer generation remain `core/` responsibilities;
- the selective-integration boundary: do not run the full BAVGEM coverage pipeline merely to create a trainer workbook.

Do not rewrite unrelated BAVGEM skills.

### 11. Update the handoff report

Before completion, overwrite `RESULT.md` with:

```text
Status: Step 3 complete | blocked
Files changed: ...
Tests run:
- <exact command> -> <exact pass/fail count>
- ...
Reconciliation:
- source statement checks: ...
- demo reformulation gaps: ...
Unresolved: ...
```

Cursor must not commit or push; the user checkpoints the working tree.

## Files expected to change

- Create: `core/model/classification.py`
- Modify: `core/model/financial_math.py`
- Modify: `core/model/line_resolver.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/data/validators.py` only where needed to reuse canonical concept resolution / expose reliable blocking failures
- Modify: `example/DEMO_HK_Standardized.json`
- Create: `core/tests/test_classification.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`

Only modify other files when a concrete dependency requires it.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership/order in this step.
- the paired Trainer / Answer Key contract.
- HK automatic scraping / SEC sourcing.
- BAVGEM's coverage-vault layout, agent orchestration, gates, quarterly model, Core Earnings Bridge, Earnings Quality, Price Rationalization, ICC, sensitivity, or DCF feature chain.
- the learner-facing Hint/Reveal commands except where a moved semantic row requires a compatibility fix.
- Git history. Do not commit, push, reset, rebase, merge, or delete branches.

## Acceptance criteria

- The Python model and workbook classification table use one shared classification/reformulation result.
- No non-subtotal balance-sheet line can silently disappear from the model because of an `Ambiguous — ...` pseudo-category or an unknown label.
- The only dropdown choices are the eight BAVGEM Stage-3 categories.
- Ambiguous judgment items remain visibly flagged while carrying a real default category; exact classification overrides are supported without coordinates.
- When reported totals exist, classified asset detail ties Total Assets, classified liability detail ties Total Liabilities, and `NOA - Net Debt` ties Reported Equity within tolerance for every modeled year.
- Equal asset/liability omissions are detected even when `Assets = Liabilities + Equity` still holds.
- `Condensed Financials` exposes live implied Equity, Reported Equity, Total Capital, and CHECK rows.
- DuPont uses reformulated implied equity.
- A build refuses an input with an evaluatable failed source checksum or a failed reformulation integrity check.
- The repaired demo passes its source checks and reformulation checks and still generates the matched pair.
- `_default_assumptions().meta.anchorRevenue` uses the canonical revenue resolver.
- `skills/bav-trainer/SKILL.md` matches the current paired-workbook product and documents the selective BAVGEM integration boundary.
- All existing Step 1 / Step 2 / Step 2B tests remain passing according to the committed `RESULT.md`, plus the new Step-3 tests.

## Testing

Use red/green TDD. Start with a failing test that demonstrates the current model can accept a balance sheet whose reported totals balance but whose classified detail is incomplete.

Run focused tests first:

```bash
python -m pytest core/tests/test_classification.py -v --tb=short
python -m pytest core/tests/test_reference_integrity.py -v --tb=short
```

Then run the existing regression modules:

```bash
python -m pytest core/tests/test_line_resolver.py -v --tb=short
python -m pytest core/tests/test_trainer.py -v --tb=short
python -m pytest core/tests/ -q --tb=line
```

Also run the CLI demo build after the JSON fixture is repaired:

```bash
python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
```

Expected: exit code `0`, both `/tmp/DEMO_HK_Trainer.xlsx` and `/tmp/DEMO_HK_Answer_Key.xlsx` created.

Do not use formula presence alone as evidence of accounting correctness. Do not weaken the new reconciliation checks to keep the old incomplete demo passing.

## Git boundary

Do not commit, push, reset, rebase, merge, or otherwise change Git history.

## Cursor execution rules

1. Read this active step completely before editing.
2. Read `skills/bav-pipeline/references/stage2_assembler.md` sections **Assembly rules / Checksums** and `stage3_analyst.md` sections **Classification table / Condensed Balance Sheet / ALT DuPont** before implementing. Treat those domain definitions as authoritative unless this step explicitly narrows them.
3. Write the failing detail-completeness regression test before production code.
4. Implement the shared classification/reformulation domain logic before changing workbook layout.
5. Make Python and Excel consume the same reformulation decisions; do not duplicate classifier rules in `ReferenceModelBuilder`.
6. Repair the demo data to satisfy the integrity contract; do not bypass or lower the checks.
7. Preserve semantic component mapping and paired-workbook behavior.
8. Run focused tests after each coherent change, then the full core suite and CLI demo build.
9. Update `skills/bav-trainer/SKILL.md` only after runtime/tests are correct.
10. Update `RESULT.md` with exact commands/results and reconciliation outcomes.
11. At completion report files changed, what was implemented, tests/checks run, and anything unresolved.
12. Do not propose the next product step.

## ChatGPT verification protocol

After the user pushes the checkpoint, ChatGPT should inspect the commit against this step and verify:

- classification/reformulation is genuinely single-source between Python and Excel;
- no balance-sheet detail can disappear silently;
- the eight BAVGEM categories and ambiguity/override behavior are implemented as specified;
- demo/source reconciliation is mathematically real, not merely a formula-string check;
- the repaired demo values actually foot to the stated totals and cash-flow net changes;
- implied and reported equity reconcile before DuPont / valuation use them;
- build blocking occurs on failed checks;
- the BAVGEM integration remained selective rather than pulling unrelated parent-pipeline machinery into the trainer;
- `RESULT.md` contains current test evidence.

ChatGPT should not rerun the test suite. Cursor owns test execution; ChatGPT owns independent inspection of the committed implementation.
