# RESULT.md — Step 9 Persistent Fast Retailing Release Pair

**Review status:** PASS

**Implementation base (plan):** `1547e262e68229e93b51d5fe0dbb8f4b6db04cce`
**HEAD at completion:** `3ade89371d974b7ce9199e3d76997ee81e66c5c5`

**Writable this step:** `scripts/build_fast_retailing_release.py` (new), `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `release/fast_retailing/` (new), `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No commit / push / sync / checkpoint. No next implementation step.

---

## What shipped

- Reproducible release builder `scripts/build_fast_retailing_release.py`: validates source-manifest hashes + FY2021–FY2025 extracted filings, runs production reconcile/standardize, builds Trainer/Answer Key via `build_training_workbook`, writes supporting artifacts + README, verifies with nonzero exit on failure.
- Persistent pair under `release/fast_retailing/`:
  - `FastRetailing_Trainer.xlsx`
  - `FastRetailing_Answer_Key.xlsx`
  - Answer Key sidecars (`component_map.json`, `assumptions.json`), `rowmap.json`, `README.md`
  - `supporting/{standardized,provenance,conflicts}.json`
- Audit extension: `run_audit(...)` accepts explicit standardized JSON + release workbook paths; default no-arg interface preserved. Release verification uses temporary copies for Check/fill; asserts `(0,0,491,491)` pristine and `(491,0,0,491)` filled; confirms practice contract + fingerprint pristine stage.
- Regression tests for explicit-pair verification, missing/mismatched artifacts, failed counts, and on-disk release verification.

Forecasting / valuation remain dormant.

---

## Measured verification (fresh this step)

### Commands run

```text
python scripts/build_fast_retailing_release.py
→ exit 0
  Trainer: release/fast_retailing/FastRetailing_Trainer.xlsx
  Answer Key: release/fast_retailing/FastRetailing_Answer_Key.xlsx

# rebuild + compare (exclude docProps packaging timestamps)
→ component_map / assumptions / standardized / provenance / conflicts: byte-identical
→ Trainer / Answer Key zip payloads excl docProps/: identical
→ rebuild exit 0

python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q
→ 39 passed in 8.80s

python -m pytest core/tests -q
→ 606 passed in 64.41s

git diff --check
→ clean
```

### Release audit (persisted pair)

All stages pass, including `8_release_pristine`. Check counts:

| Mode | (correct, incorrect, blank, total) |
|---|---|
| pristine Trainer (temp copy) | (0, 0, 491, 491) |
| answer-filled copy | (491, 0, 0, 491) |

Release workbooks unchanged after verification (SHA-256 fingerprints equal before/after).

### Artifact SHA-256 (post-rebuild)

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
scripts/build_fast_retailing_release.py          (new)
scripts/audit_fast_retailing_benchmark.py
core/tests/test_fast_retailing_benchmark.py
release/fast_retailing/                          (new tree)
RESULT.md                                        (this record)
```

Incidental test touches to `benchmark/fast_retailing/BASELINE.md` and `example/DEMO_HK_Trainer.xlsx` were restored and are outside the final diff.

---

## Acceptance

| Criterion | Result |
|---|---|
| Exactly two user-facing release workbooks under `release/fast_retailing/`, reproducible from checked-in inputs | **pass** |
| Existing FR benchmark checks verify the persisted pair | **pass** |
| Release Trainer pristine; Answer Key usable for human review | **pass** |
| Required checks pass; only writable files change; no commit/push | **pass** |

---

## Plan changes

**No plan changes required.**

Further forecasting work remains deferred. Normal Step 9 work may resume after human review of this release pair.
