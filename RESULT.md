# RESULT.md — Step 9 Repair Start/End Border and Hyperlink Theme Parity

**Review status:** PASS

**Implementation base (plan):** `cc805d39596399947a7ba9faecd68143f41d59f2`
**HEAD at completion:** `173aba2936a8b382fe742ceb18de97bae645f998`

**Writable this step:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No commit / push / sync / checkpoint. No next implementation step.

---

## What shipped

- `_border_components` now compares `border_start` and `border_end` (including the absent-border branch), normalized via `_side_token`.
- `_THEME_SCHEME_ORDER` extended with `hlink` (index 10) and `folHlink` (index 11); effective RGB + tint resolution unchanged and now covers those indices.
- Persisted-pair regressions: one-sided start/end absent-vs-present, style, and color mutations on ordinary and judgment-response cells; theme-definition divergence at indices 10–11 with matching cell theme references; positive matching start/end borders and hyperlink theme+tint; audit-stage fail + nonzero CLI for both border sides and both hyperlink indices; temp-pair and source-release hash checks.

Forecasting / valuation remain dormant.

---

## Measured verification (fresh this step)

### Commands run

```text
python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q
→ 139 passed in 28.47s

python -m pytest core/tests -q
→ 706 passed in 85.04s

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

- `border_start` / `border_end`: absent vs present, changed style, changed color (matching style) — Trainer or Answer Key; ordinary A6 and judgment-response F5.
- Theme indices 10 (`hlink`) / 11 (`folHlink`): identical cell theme refs, one workbook theme definition changed — Trainer or Answer Key; ordinary and judgment-response cells → `font_color`.
- Positive: matching start/end borders; matching hyperlink theme refs with tint=0.25.
- Audit/CLI: border_start, border_end, hlink, folHlink corruptions fail `5_workbook_generation`, skip Check stages, exit nonzero; temp-pair hashes unchanged; source-release fingerprints unchanged; explicit-pair no-generation regression retained.

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

Incidental touches to `benchmark/fast_retailing/BASELINE.md`, `example/DEMO_HK_Trainer.xlsx`, and `benchmark/lululemon/` from the full suite were restored/removed and are outside the final diff.

---

## Acceptance

| Criterion | Result |
|---|---|
| One-sided start/end border diffs and theme indices 10–11 effective-color diffs fail persisted-pair verification | **pass** |
| Matching formatting passes; judgment-content exemptions and existing formatting regressions intact | **pass** |
| Unchanged release verification passes with pristine `(0, 0, 491, 491)` and filled `(491, 0, 0, 491)` | **pass** |
| Required tests pass; verification leaves workbooks and sidecars unchanged | **pass** |
| Only writable files change; no commit or push | **pass** |

**Plan changes needed:** none.
