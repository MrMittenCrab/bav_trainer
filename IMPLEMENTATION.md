# Step 9M.2 — Repair Lululemon Benchmark Artifact Isolation

**Base:** `32df12b1c253005575a76db5c768094f87c43489`
**Status:** PROBLEMS
**Goal:** Detect reconciliation fixture drift without modifying committed benchmark evidence.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/tests/test_lululemon_benchmark.py` and `RESULT.md`.
- Keep committed reconciliation artifacts, baseline hashes, source inputs, and production behavior unchanged.
- Preserve existing source-binding, financial-anchor, conflict, and build-blocker assertions.
- Do not begin Step 9M.2.1 or forecasting/valuation work.

## Task 1 — Isolate reconciliation outputs

In `core/tests/test_lululemon_benchmark.py`:

- Remove the reconciliation subprocess targeting `RECONCILED`.
- Run both reconciliation passes exclusively into separate `tmp_path` directories.
- Read the committed `standardized.json`, `provenance.json`, and `conflicts.json` bytes before either run.
- Assert both generated artifact sets match each other and the untouched committed bytes exactly.
- Verify committed bytes remain unchanged after execution, including when comparison fails; never refresh or restore fixtures inside tests.

## Task 2 — Prove drift is detected

- Add a regression using a temporary copy of the expected artifacts and the same comparison path as the benchmark test.
- Parameterize drift across all three artifact names; alter only temporary expected copies.
- Require each mismatch to fail comparison and identify the affected artifact.
- Confirm the altered expected copy remains unchanged by the comparison.
- Keep generated workbooks and other test outputs in temporary directories.

## Task 3 — Verify and record

Run:

- `PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests -q`

Capture reconciliation artifact hashes before and after verification and inspect repository changes. Do not regenerate committed evidence to make a comparison pass.

Update `RESULT.md` with the repair, actual test results, before/after artifact hashes, and any remaining failures. Supersede the previous PASS assessment with measured repair status.

## Acceptance and next step

- Reconciliation tests write exclusively to temporary directories.
- Two generated runs match all three untouched committed artifacts byte-for-byte.
- Drift in any expected artifact fails comparison without rewriting evidence.
- Focused Lululemon, combined benchmark, and full core regressions pass.
- Committed Lululemon artifact hashes remain unchanged.
- On failure, retain **Step 9M.2 — Repair Lululemon Benchmark Artifact Isolation**.
- On PASS, propose **Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)**; Step 9 remains incomplete.
