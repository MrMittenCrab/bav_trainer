# RESULT.md — Step 9 Release Source Fidelity and Structural Parity

**Review status:** PASS

**Implementation base (plan):** `68f90e5e85ec1e47a9cdb3a5b5c3067251262f98`
**HEAD at completion:** `16a628bcb8fb934ea401e6ee2f6d3a8b407ba184`

**Writable this step:** `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No commit / push / sync / checkpoint. No next implementation step.

---

## What shipped

- `_verify_release_pair_contract(trainer, answer, fin)` now takes loaded `StandardizedFinancials`.
- Exhaustive persisted source-fact comparison for Income Statement / Balance Sheet / Cash Flow Statement (and lease supplemental when present) plus diluted weighted-average shares on Per Share Analysis; rejects blanked facts, altered values, missing sheets/rows/periods, and formulas substituted for literals. Each workbook checked independently against inputs.
- Visibility from `sheet_state` (not name prefixes): required historical/practice sheets must be visible; metadata (`_*`) and dormant forecast placeholders remain intentionally hideable; jointly hidden historical sheets fail.
- Visible layout parity: sheet order/state, dimensions, labels/values (non-practice), merged ranges, row/column heights & hidden flags, freeze panes, and effective formatting. Practice content + Answer-Key Notes / judgment responses remain the only allowed content diffs; blank-yellow Trainer and formula+Note Answer Key checks retained.
- Corruption regressions covering Trainer / Answer Key / both, source mutations, hidden/`veryHidden` sheets, and layout mismatches; explicit-pair path proven not to call workbook generation; release hashes unchanged after pass and fail paths.

Forecasting / valuation remain dormant.

---

## Measured verification (fresh this step)

### Commands run

```text
python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q
→ 73 passed in 13.78s

python -m pytest core/tests -q
→ 640 passed in 68.18s

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

- Source: earlier-year fact, zero value, historical shares, deleted fact, missing source sheet, formula-for-literal — Trainer / Answer Key / both.
- Visibility: `hidden` and `veryHidden` on Income Statement — Trainer / Answer Key / both (including identical joint hide).
- Layout: label, merged ranges, dimensions, row/column hidden, freeze panes, formatting.
- Contract failures surface on stage `5_workbook_generation` with workbook/sheet/cell detail; Check stages skipped.
- Explicit-pair verification does not invoke `build_training_workbook`.
- On-disk release + sidecar hashes unchanged after successful and failed verification.

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
| Every required persisted source fact matches standardized input in both workbooks | **pass** |
| Hidden required historical sheets and visible structural mismatches fail release verification | **pass** |
| Pristine release verification and required regressions pass without modifying release artifacts | **pass** |
| Only writable files change; no commit/push | **pass** |

---

## Plan changes

None.
