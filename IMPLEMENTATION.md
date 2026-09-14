# Step 9 — Repair Start/End Border and Hyperlink Theme Parity

**Base:** `cc805d39596399947a7ba9faecd68143f41d59f2`
**Incoming review:** PROBLEMS
**Goal:** Reject persisted-pair start/end border mismatches and changed effective colors behind theme indices 10–11.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`; Cursor must never modify either file.
**Writable:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.

### Task 1: Complete the affected formatting comparisons

- Add `border_start` and `border_end` to `_border_components`, including its absent-border branch; normalize each side through `_side_token`.
- Extend `_THEME_SCHEME_ORDER` with `hlink` and `folHlink` at indices 10 and 11, preserving indices 0–9.
- Resolve both hyperlink theme colors through the existing effective-color and tint normalization.
- Preserve component-specific failures containing sheet, cell, and Trainer/Answer Key values.

### Task 2: Add persisted-pair regressions

- Reuse temporary release-pair copies, sidecar helpers, and save/reload mutation helpers.
- Parameterize Trainer/Answer Key mutations for both `start` and `end`: absent versus present side, changed style, and changed color with matching style.
- For each theme index 10 and 11, assign identical references to matching visible cells in both workbooks, then change only the corresponding theme definition in one workbook.
- Cover formatting on content-exempt judgment-response cells as well as ordinary visible cells.
- Assert `border_start`, `border_end`, or `font_color` failures with the expected sheet and coordinate.
- Add positive controls for matching start/end borders and matching hyperlink theme references, including nonzero tint.
- Extend audit/CLI regressions to cover both border sides and both hyperlink theme indices: fail `5_workbook_generation`, skip both Check stages, and exit nonzero.
- Compare copied workbook and sidecar hashes immediately before and after verification on successful and failing paths; retain source-release fingerprint checks and the explicit-pair no-generation regression.

### Task 3: Verify and record

- Run `python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q`.
- Run `python -m pytest core/tests -q`.
- Run `git diff --check`.
- Run `python scripts/audit_fast_retailing_benchmark.py --standardized-json release/fast_retailing/supporting/standardized.json --provenance-json release/fast_retailing/supporting/provenance.json --conflicts-json release/fast_retailing/supporting/conflicts.json --trainer release/fast_retailing/FastRetailing_Trainer.xlsx --answer-key release/fast_retailing/FastRetailing_Answer_Key.xlsx --verify-release-pair --require-check-counts --no-baseline`.
- Update `RESULT.md` with completion revision, exact commands, measured results, new regression coverage, artifact hashes, changed files, and PASS/PROBLEMS/BLOCKED status.

### Acceptance criteria

- One-sided start/end border differences and changed effective theme colors at indices 10–11 fail persisted-pair verification.
- Matching formatting passes; existing judgment-content exemptions and formatting regressions remain intact.
- Unchanged release verification passes with pristine counts `(0, 0, 491, 491)` and filled counts `(491, 0, 0, 491)`.
- Required tests pass; verification leaves workbooks and sidecars unchanged.
- Only writable files change; no commit or push.
