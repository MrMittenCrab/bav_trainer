# Step 9M.3E — Repair G7 Closure Reporting

**Base:** `fbc50c790d8333e88340b01d7918cab4b01b8311`

**Goal:** Consistently record G7 closed with disagreements retained in the audit generator and generated baseline.

### Task 1: Correct generated closure text

**File:** `scripts/audit_fast_retailing_benchmark.py`

- [x] Replace “G1/G1B/G2/G2B/G2C/G3/G4/G5/G6 closed; G7 remains open” in `write_baseline()` with “G1/G1B/G2/G2B/G2C/G3/G4/G5/G6/G7 closed; G7 disagreements retained with verified deterministic selection and provenance.”

### Task 2: Regenerate and verify the baseline

**File:** `benchmark/fast_retailing/BASELINE.md`

- [x] Run `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py` to regenerate the baseline with the corrected closure statement.
- [x] Require Stages 1–7 passing, `expected_specs=380`, blank Check `0 correct / 0 incorrect / 380 blank`, and filled Check `380 correct / 0 incorrect / 0 blank`.
- [x] Verify both files contain no “G7 remains open” claim and consistently report G7 closed with disagreements retained.
- [x] Verify overlap/supplemental conflict counts remain `3/3`, extracted facts and reconciled artifacts are unchanged, and the diff contains only the two closure-text replacements.
