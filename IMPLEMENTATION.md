# Step 9M.6 — Workbook Acceptance Verification

**Base:** `5240f6b1b2cdd2cc0be017e401d4df6a527300b4`

**Goal:** Verify the lease ROU-asset implementation and workbook integration in a writable environment.

### Task 1: Run the acceptance suite

- [ ] Run in a writable checkout with writable temporary storage:
  `python -m pytest core/tests/test_lease_rou.py core/tests/test_lease_liability.py core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py core/tests/test_reference_workbook_audit.py core/tests/test_cross_company_robustness.py`
- [ ] Record the tested SHA, pass/fail/skip counts, and any failures.

### Task 2: Verify workbook and benchmark results

- [ ] Confirm semantic mapping survives source-row reordering and all four first-period ROU diagnostics have `.value is None` in both workbooks.
- [ ] Confirm ROU source balances remain populated; later-period Trainer practice cells are blank yellow without Notes, and matching Answer-Key cells contain formulas and non-empty Notes.
- [ ] Confirm blank/correct/incorrect Check behavior remains non-disclosing.
- [ ] Confirm Fast Retailing FY2025 ROU assets are `477111`, ROU practice count is `16`, and total `expected_specs` is `454`.
- [ ] Confirm Fast Retailing Check reports correct/incorrect/blank counts of `0/0/454` before filling and `454/0/0` after filling.
- [ ] Confirm existing DEMO, goodwill/intangibles, and lease-liability practice counts remain unchanged.

### Task 3: Record verified acceptance

**File:** `IMPLEMENTATION.md`

- [ ] Record actual suite results and unresolved failures or environment blockers.
- [ ] Run `git diff --check`.

### Acceptance criteria

- The complete acceptance suite passes, including workbook integration tests; required coverage is not skipped or blocked.
- Workbook parity, ROU source gating, practice counts, and Check assertions pass.
- `git diff --check` passes.
- Completion is recorded only after writable-environment verification succeeds.
