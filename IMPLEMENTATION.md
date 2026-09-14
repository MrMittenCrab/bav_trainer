# Step 9N.4 — Completion-Record and Scope Reconciliation

**Base:** `6a90c81a6fe0fbb439cfb9a1733dbfab167ec0ce`

**Goal:** Repair the Step 9 exit assessment and account explicitly for the prior step’s three supporting edits.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`. Cursor must never modify either file.

**Writable files:** `RESULT.md`, `docs/GOOGL_HISTORICAL_REFERENCE.md`.

### Task 1: Account for supporting edits

- Read `RESULT.md` and inspect the base commit against its parent.
- Explicitly accept and retain these necessary supporting changes as exceptions to Step 9N.3’s writable list:
  - `core/model/line_resolver.py`: register `repayments_of_lease_liabilities` for exact-concept-only resolution.
  - `core/tests/test_line_resolver.py`: cover that concept in the explicit-concept-only regression.
  - `core/tests/test_capex.py`: update Fast Retailing total specs from 481 to 491 while retaining 10 capex specs.
- Record their exact scope and verification in `RESULT.md`; distinguish accepted prior changes from this step’s writable files.

### Task 2: Reconcile the evidence-based exit gate

- Reassess all six TARGET exit criteria against the existing gap matrix, documented deferrals, real-company benchmark, and regression evidence.
- For criteria 1 and 6, identify any remaining concrete material gap with its repository evidence, learner impact, and available source facts. Deferred topics or pending planner confirmation alone do not establish failure.
- If no such gap remains and verification supports the other criteria, mark all six criteria PASS and Step 9 complete.
- Otherwise record the specific failed criterion and bounded unresolved defect; do not manufacture additional historical work.
- Synchronize the audit’s coverage summary, blocking queue, candidate section, and current gate statements with `RESULT.md`. Remove stale instructions requiring another Step 9 candidate regardless of evidence.
- Preserve documented source-availability and materiality deferrals.
- Record Step 10 driver-based forecasting as the next stage if the gate passes; implement no forecasting in this repair.

### Task 3: Verify and record

- Run `python -m pytest core/tests/test_line_resolver.py core/tests/test_capex.py core/tests/test_lease_repayment.py core/tests/test_historical_v1_exit_gate.py core/tests/test_fast_retailing_benchmark.py -q`.
- Run `python -m pytest core/tests -q`.
- Keep test-generated benchmark artifacts outside the final diff; preserve any pre-existing user changes.
- Run `git diff --check` and inspect `git status --short` plus `git diff --name-only`.
- Record actual commands, measured results, revision, limitations, the six-row gate decision, and next-stage disposition in `RESULT.md`; distinguish prior recorded passes from fresh verification.

### Acceptance criteria

- Criteria 1 and 6 pass unless a concrete remaining material gap is evidenced.
- All six dispositions and the resulting stage decision agree across both writable records.
- The three supporting edits are explicitly accepted, explained, and verified without changing their implementation.
- Required verification passes; only the two writable records remain changed.
- No new historical module, forecasting, valuation, commit, or push.
