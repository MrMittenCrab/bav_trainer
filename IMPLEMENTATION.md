# Step 9M.4 — Resolver Capability Documentation Repair

**Base:** `d6b44989b4fd9fd04940d3f885e536980f540215`

**Goal:** Correct current resolver capabilities and document explicit concept resolution as required work for the proposed goodwill/intangibles module.

### Task 1: Correct the capability statement

**File:** `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Replace the claim that `resolve_line` supports `goodwill`, `intangible_assets`, and `payments_for_intangible_assets`.
- [x] State that all three currently raise `ValueError("Unknown financial concept: ...")` because `core/model/line_resolver.py` rejects unregistered concepts before matching `LineItem.concept`, including when `required=False`.
- [x] Distinguish supplied concept-tagged facts and operating long-term asset classification from implemented resolver support.

### Task 2: Record the candidate’s resolution prerequisite

**File:** `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Identify explicit concept resolution for BS `goodwill` / `intangible_assets` and optional CF `payments_for_intangible_assets` as required future implementation work.
- [x] Specify unique explicit concept matching without label fallback, with missing or ambiguous inputs following the candidate’s existing omission rules.
- [x] Clarify that the minimum input contract and omission behavior are proposed requirements, not current resolver behavior.
- [x] Retain the single source-supported candidate, reported facts, proposed calculations, and Trainer/Answer Key/Check scope.

### Validation and acceptance

- [x] Capability statements agree with the registration guard and matching order in `core/model/line_resolver.py`.
- [x] No statement implies these three concepts currently resolve through `resolve_line`.
- [x] Only `docs/GOOGL_HISTORICAL_REFERENCE.md` changes; resolver and module implementation remain deferred.
- [x] `git diff --check` passes; no new tests, workbook regeneration, or benchmark audit is required.
