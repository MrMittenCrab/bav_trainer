# RESULT.md — Step 9 Repair Release Layout Contract Bypasses

**Review status:** PASS

**Implementation base (plan):** `4bd447678a726f77e48b8ef6742c4f145b5e5b39`
**HEAD at completion:** `f8468a4e4d90012b78ed0081facef578dd4f3631`

**Writable this step:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No commit / push / sync / checkpoint. No next implementation step.

---

## What shipped

- Judgment content exemptions no longer cover whole F:H columns. Only response cells on actual case rows (matching `_judgment_case_rows`) are content/Note-exempt; headers such as Accounting Judgment!F4 and other non-response cells compare normally. Matching case coordinates required in both workbooks.
- Visible formatting comparison is complete and workbook-theme-aware: font decorations, fill (pattern/gradient), all border sides/flags, alignment (wrap/shrink/rotation/indent), number format, protection. Colors dispatch on `Color.type` only; theme/indexed references resolve to effective RGB so identical indices with different theme/palette definitions fail. Style IDs are not compared.
- Bypass regressions: one-sided Trainer/Answer Key mutations for F4 text/Note, non-case F:H content, wrap_text (including response cells), theme color, tint, theme-definition divergence; omitted-component cases; positive controls for legitimate judgment-response diffs and equivalent formatting with different style IDs; audit-stage fail + nonzero CLI exit.

Forecasting / valuation remain dormant.

---

## Measured verification (fresh this step)

### Commands run

```text
python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q
→ 99 passed in 18.04s

python -m pytest core/tests -q
→ 666 passed in 72.82s

git diff --check
→ clean

python scripts/audit_fast_retailing_benchmark.py \
  --standardized-json release/fast_retailing/supporting/standardized.json \
  --provenance-json release/fast_retailing/supporting/provenance.json \
  --conflicts-json release/fast_retailing/supporting/conflicts.json \
  --trainer release/fast_retailing/FastRetailing_Trainer.xlsx \
  --answer-key release/fast_retailing/FastRetailing_Answer_Key.xlsx \
  --verify-release-pair --require-check-counts --no-baseline
→ exit 0
  5_workbook_generation: persisted release pair (not regenerated)
  6_blank_check: correct=0 incorrect=0 blank=491 total=491
  7_filled_check: correct=491 total=491
  8_release_pristine: release fingerprints unchanged
```

### Check counts

| Mode | (correct, incorrect, blank, total) |
|---|---|
| pristine | (0, 0, 491, 491) |
| filled | (491, 0, 0, 491) |

### Corruption coverage

- Judgment header F4 text / Note — Trainer or Answer Key.
- Non-case F:H content (G4) — Trainer or Answer Key.
- wrap_text on judgment response F5 — Trainer or Answer Key.
- Distinct theme color, tint, and changed theme definition behind identical theme index — Trainer or Answer Key.
- Omitted format components: shrink_to_fit, text_rotation, indent, underline, strikethrough, number_format, protection_hidden, border_left, fill_type.
- Positive: legitimate F5:H5 content/Note diffs pass; equivalent Aptos Narrow formatting with different workbook-local style IDs passes.
- Bypass fails stage `5_workbook_generation`, skips Check stages, CLI exit nonzero; release hashes unchanged after pass and fail paths.
- Explicit-pair no-generation regression preserved.

### Artifact SHA-256 (unchanged)

```text
4b657461757cfb43f6067636868df44541575d274b3a3025ccc6d397dac89536  FastRetailing_Trainer.xlsx
a1d397933971535cdba7f2c2076014462cc00c66ffe19a2a4651d2e192c9e089  FastRetailing_Answer_Key.xlsx
dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34  FastRetailing_Answer_Key.component_map.json
73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a  FastRetailing_Answer_Key.assumptions.json
5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1  supporting/standardized.json
fd5a1ec87b61c4835d3b7bfda79996afa6c5ed9bbf2082e35413fb18ee696f1f  supporting/provenance.json
12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5  supporting/conflicts.json
```

### Final changed-file list

```text
scripts/audit_fast_retailing_benchmark.py
core/tests/test_fast_retailing_benchmark.py
RESULT.md
```

Incidental touches to `benchmark/fast_retailing/BASELINE.md` and `example/DEMO_HK_Trainer.xlsx` were restored and are outside the final diff.

---

## Acceptance

| Criterion | Result |
|---|---|
| Judgment headers and non-response content cannot bypass parity checks | **pass** |
| Wrapping and effective theme-color mismatches fail, including on response cells | **pass** |
| Unchanged release verification passes with pristine `(0, 0, 491, 491)` and filled `(491, 0, 0, 491)` | **pass** |
| Required regressions pass; release artifacts remain unchanged | **pass** |
| Only writable files change; no commit or push | **pass** |

**Plan changes needed:** none.
