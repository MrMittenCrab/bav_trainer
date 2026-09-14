# Step 9 — Repair Release Layout Contract Bypasses

**Base:** `4bd447678a726f77e48b8ef6742c4f145b5e5b39`
**Incoming review:** PROBLEMS
**Goal:** Reject judgment-header corruption and visible formatting mismatches in persisted release pairs.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`; Cursor must never modify either file.
**Writable:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.

### Task 1: Restrict judgment-content exemptions

- Replace whole-column exemptions in `_verify_visible_layout_parity` with explicit response coordinates for actual cases on Accounting Judgment and Normalization Judgment.
- Follow the case-row conventions used by `_judgment_case_rows` in `core/trainer/workbook.py`; require matching case coordinates in both workbooks.
- Exempt only response cells in columns F:H and existing semantic practice cells from permitted content/Note comparisons.
- Compare headers, including Accounting Judgment!F4, and all other non-response cells normally.
- Continue comparing formatting at every visible cell, including exempt response and practice cells.

### Task 2: Compare complete effective formatting

- Replace partial `_format_signature` and border tokens with complete normalized font, fill, border, alignment, number-format, and protection comparisons.
- Include wrapping, shrink-to-fit, rotation, indentation, font decorations, pattern/gradient fills, and all border sides and flags.
- Dispatch color normalization on `Color.type`; preserve RGB, theme/indexed identity, tint, and automatic-color semantics without reading inactive descriptor values.
- Resolve workbook theme/palette references so identical color indices with different effective colors fail.
- Keep comparisons independent of workbook-local style IDs.
- Report sheet, cell, differing formatting component, and Trainer/Answer Key values through existing contract failures.

### Task 3: Add bypass regressions and verify

- Extend persisted-pair corruption tests using temporary workbook copies and existing sidecar helpers.
- Parameterize one-sided mutations across Trainer and Answer Key: Accounting Judgment!F4 text and Note, non-case F:H content, `wrap_text`, distinct theme colors, tint, and changed theme definitions behind identical references.
- Cover omitted formatting components with focused parameterized cases.
- Add positive controls for legitimate judgment-response differences and equivalent formatting with different style IDs.
- Assert specific contract failures; verify demonstrated bypasses fail `5_workbook_generation`, skip Check stages, and produce nonzero CLI exit.
- Preserve the explicit-pair no-generation regression; compare workbook and sidecar hashes before and after successful and failed verification.
- Run `python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q`.
- Run `python -m pytest core/tests -q` and `git diff --check`.
- Run `python scripts/audit_fast_retailing_benchmark.py --standardized-json release/fast_retailing/supporting/standardized.json --provenance-json release/fast_retailing/supporting/provenance.json --conflicts-json release/fast_retailing/supporting/conflicts.json --trainer release/fast_retailing/FastRetailing_Trainer.xlsx --answer-key release/fast_retailing/FastRetailing_Answer_Key.xlsx --verify-release-pair --require-check-counts --no-baseline`.
- Record completion revision, exact commands, measured results, corruption coverage, artifact hashes, and PASS/PROBLEMS/BLOCKED status in `RESULT.md`.

### Acceptance criteria

- Judgment headers and non-response content cannot bypass parity checks.
- Wrapping and effective theme-color mismatches fail, including on response cells.
- Unchanged release verification passes with pristine counts `(0, 0, 491, 491)` and filled counts `(491, 0, 0, 491)`.
- Required regressions pass; release artifacts remain unchanged.
- Only writable files change; no commit or push.
