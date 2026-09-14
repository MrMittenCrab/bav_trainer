# RESULT.md — Step 9M.2 Repair Lululemon Benchmark Artifact Isolation

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.1** — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)

**Plan base:** `32df12b1c253005575a76db5c768094f87c43489`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No Step 9M.2.1 or forecasting/valuation work.

Supersedes prior Step 9M.2 PASS (baseline + gap map).

---

## Repair

In `core/tests/test_lululemon_benchmark.py`:

1. Removed the reconciliation subprocess that wrote into committed `benchmark/lululemon/reconciled/`.
2. Both reconcile passes now write only under `tmp_path`.
3. Committed `standardized.json` / `provenance.json` / `conflicts.json` bytes are read before either run and compared byte-for-byte to both generated sets.
4. Post-run re-read asserts committed bytes are unchanged.
5. Added parameterized drift regression (`test_reconcile_drift_is_detected_without_rewriting_expected`) that alters only temporary expected copies for each of the three artifacts; comparison fails naming the drifted file and leaves the altered copy untouched.

Shared comparison helper: `_assert_artifact_sets_match` (read-only; never refreshes or restores fixtures).

---

## Artifact hashes (before / after verification)

| Artifact | SHA-256 | Size | Unchanged |
|---|---|---|---|
| standardized.json | `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45` | 22289 | yes |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 | yes |
| provenance.json | `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` | 698793 | yes |

Before and after digests are identical for all three committed artifacts.

---

## Measured verification

```text
PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py -q
→ 9 passed in 0.91s

PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py -q
→ 141 passed in 28.17s

PYTHONPATH=. pytest core/tests -q
→ 723 passed in 84.55s
```

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is `core/tests/test_lululemon_benchmark.py` (+ this `RESULT.md`).

---

## Acceptance

| Criterion | Result |
|---|---|
| Reconciliation tests write only to temporary directories | **pass** |
| Two generated runs match all three untouched committed artifacts | **pass** |
| Drift in any expected artifact fails comparison without rewriting evidence | **pass** |
| Focused LULU + combined benchmark + full core regressions | **pass** (9 / 141 / 723) |
| Committed Lululemon artifact hashes unchanged | **pass** |

**Plan changes needed:** none.

**Unresolved:** G1–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)**.
