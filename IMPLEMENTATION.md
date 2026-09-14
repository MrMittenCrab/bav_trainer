# Step 9 — Release Source Fidelity and Structural Parity

**Base:** `68f90e5e85ec1e47a9cdb3a5b5c3067251262f98`
**Incoming review:** PROBLEMS
**Goal:** Reject persisted Fast Retailing releases with corrupted historical source facts, hidden historical sheets, or mismatched visible layouts.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`; Cursor must never modify either file.
**Writable:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.

### Task 1: Verify persisted source fidelity

- Pass the loaded `StandardizedFinancials` into `_verify_release_pair_contract`.
- Replace the numeric-cell population heuristic with exhaustive comparison of persisted historical source cells in both workbooks against standardized inputs.
- Resolve source rows and periods using existing production naming/mapping conventions; cover statement facts and supplied historical share data, preserving units, signs, zeros, and missing-value semantics.
- Reject missing required source sheets, rows, periods, blanked facts, altered values, and formulas substituted for source literals.
- Check each workbook independently against inputs so identical corruption in both files fails.
- Report workbook, sheet, cell, source identity, period, expected value, and actual value on failure. Do not generate replacement workbooks.

### Task 2: Enforce visibility and layout parity

- Determine visibility from `sheet_state`, not sheet-name prefixes.
- Require historical source and active practice sheets to be visible in both workbooks; reject jointly hidden historical sheets as well as visibility mismatches.
- Preserve intentionally hidden metadata and dormant forecast placeholders.
- Compare sheet order/state and visible historical structure: cell coordinates, labels, dates, units, non-practice values/formulas, merged ranges, row heights, column widths, hidden rows/columns, freeze panes, and cell formatting.
- Compare effective formatting rather than workbook-local style IDs.
- Allow only the defined practice-content and Answer-Key Note differences; retain existing blank-yellow Trainer and formula-plus-Note Answer Key checks.
- Surface failures through existing audit stage reporting and nonzero CLI exit.

### Task 3: Add corruption regressions and verify

- Use temporary copies of the persisted pair and required sidecars for corruption tests.
- Parameterize source mutations across Trainer, Answer Key, and both together; cover earlier-year statement facts, zero values, historical shares, deleted facts, and missing source sheets.
- Cover `hidden` and `veryHidden` historical sheets, including both workbooks hidden identically.
- Cover mismatched labels, merged ranges, dimensions, row/column visibility, freeze panes, and formatting.
- Assert specific contract failures, not merely failed Check counts; prove explicit-pair verification does not invoke workbook generation.
- Verify the unchanged persisted pair passes all stages with pristine counts `(0, 0, 491, 491)` and filled counts `(491, 0, 0, 491)`.
- Assert workbook and sidecar hashes remain unchanged after successful and failed verification.
- Run `python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q`.
- Run `python -m pytest core/tests -q` and `git diff --check`.
- Run the explicit-pair audit CLI against `release/fast_retailing/` with its supporting inputs, `--verify-release-pair --require-check-counts --no-baseline`.
- Record revision, exact commands, measured results, artifact hashes, corruption coverage, and PASS/PROBLEMS/BLOCKED status in `RESULT.md`.

### Acceptance criteria

- Every required persisted source fact matches standardized input in both workbooks.
- Hidden required historical sheets and visible structural mismatches fail release verification.
- Pristine release verification and required regressions pass without modifying release artifacts.
- Only writable files change; no commit or push. Further stage work remains deferred.
