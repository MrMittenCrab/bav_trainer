# Step 9M.4 — Historical Convergence Checkpoint

**Base:** `280599a0f25dcdf32cee6f928a595f3bc75cd7c4`

**Goal:** Refresh historical coverage and select one source-supported implementation candidate after Fast Retailing G1–G7 closure.

### Task 1: Refresh historical coverage

**File:** `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Update the Trainer inventory, gap matrix, and queue for implemented split lease-liability aggregation, treatment-conditioned lease interest, parent/NCI attribution, and split-adjusted per-share analysis.
- [x] Distinguish implemented capabilities from remaining ROU, lease-payment, SBC, goodwill/acquisition, deferred-tax, capex, and segment gaps.
- [x] Preserve GOOGL observations and distinguish demo practice counts from Fast Retailing’s 380-cell surface.

### Task 2: Select one bounded historical module

**File:** `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Evaluate the existing first-priority goodwill/intangibles/acquisition candidate against relevant resolvers and supplied Fast Retailing filing JSON; consult source PDFs only where provenance needs verification.
- [x] Record available concepts, periods, units, signs, and source references; distinguish reported balances and cash flows from unsupported acquisition or impairment explanations.
- [x] Name one next implementation candidate with its minimum input contract, missing/ambiguous-input behavior, proposed historical calculations, and Trainer/Answer Key/Check scope. If the first candidate lacks sufficient facts, select the next supported queue item.

### Acceptance

- [x] Coverage statements agree with current implementation and recorded benchmark evidence; historical evidence is not presented as a newly rerun audit.
- [x] Exactly one next implementation candidate is specified with source-supported inputs and concrete expected behavior.
- [x] G1–G7 remain closed with overlap/supplemental disagreements retained at `3/3`.
- [x] Only `docs/GOOGL_HISTORICAL_REFERENCE.md` changes; production code, fixtures, benchmark artifacts, and workbooks remain unchanged.
- [x] `git diff --check` passes; no workbook regeneration or full audit is required.
- [x] Forecasting and valuation remain deferred.
