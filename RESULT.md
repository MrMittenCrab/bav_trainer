# RESULT.md — Step 9M.2 Repair Failure-Path Artifact Immutability Verification

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.1** — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)

**Plan base:** `9bb3880dc75fbca5ff9c8f0b14585bb405818bd2`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No Step 9M.2.1 or forecasting/valuation work.

Supersedes prior Step 9M.2 PASS (artifact isolation).

---

## Repair

In `core/tests/test_lululemon_benchmark.py`:

1. Extracted `_guarded_deterministic_reconcile`: both reconcile passes, stdout checks, inter-run match, and committed-baseline comparisons run under `try`; committed-byte reread/equality runs in `finally`.
2. Unchanged committed bytes preserve the original failure; mutations raise `AssertionError` naming affected artifacts.
3. Failure-path coverage:
   - subprocess failure at pass 1 and pass 2;
   - comparison failure at inter-run and committed-baseline;
   - each path propagates the injected failure and still executes final verification.
4. Parameterized temp-mutation guard across `ARTIFACT_NAMES` × `{pass1, inter_run, baseline}`: mutation before injected failure is detected and named; altered temp copies are not restored.
5. Retained `test_reconcile_drift_is_detected_without_rewriting_expected`.

---

## Failure-path coverage

| Path | Propagates failure | Final reread runs | Mutation named |
|---|---|---|---|
| subprocess fail pass 1 / 2 | yes | yes | n/a (committed unchanged) |
| inter-run comparison fail | yes | yes | n/a |
| committed-baseline comparison fail | yes | yes | n/a |
| temp mutation + injected fail (3 artifacts × 3 sites) | immutability AssertionError | yes | yes; copy left altered |

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
→ 22 passed in 3.24s

PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py -q
→ 154 passed in 31.01s

PYTHONPATH=. pytest core/tests -q
→ 736 passed in 90.24s
```

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is `core/tests/test_lululemon_benchmark.py` (+ this `RESULT.md`).

---

## Acceptance

| Criterion | Result |
|---|---|
| Final committed-byte verification after success, subprocess failure, comparison failure | **pass** |
| Unchanged artifacts preserve original failure; temp mutations detected without rewrite | **pass** |
| Both successful reconcile runs match each other and all three committed artifacts | **pass** |
| Focused LULU + combined benchmark + full core regressions | **pass** (22 / 154 / 736) |
| Committed Lululemon artifact hashes unchanged | **pass** |

**Plan changes needed:** none.

**Unresolved:** G1–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)**.
