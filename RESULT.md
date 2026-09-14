# RESULT.md — Step 9M.2.1 Generic Gift-Card / Deferred-Revenue Liability Classification (G1)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.2** — Generic Property-and-Equipment Classification and PPE Identity (G2)

**Plan base:** `9c0a6aab0e9e7cc70bdb6c24d2f9cd90daee4d81`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G2–G7 or forecasting/valuation work.

Supersedes prior Step 9M.2 PASS (failure-path immutability).

---

## What changed

In `core/model/classification.py`:

1. Added guarded deterministic `_customer_prepayment_liability_decision` for explicit gift-card, unearned-revenue, deferred-revenue, and contract-liability balances.
2. Bounded concept aliases + compatible liability label phrases; rejects generic “gift”/“card”/“contract”/“revenue”, asset/receivable wording, and movement/derecognition concepts/labels.
3. Unqualified balances → `Operating Working Capital Liability`; explicitly noncurrent/long-term → `Operating Long-Term Liability` (noncurrent checked first).
4. Wired into the concept chain and label path; removed deferred-revenue/contract-liability from the broad payable WC substring list so maturity handling stays consistent.
5. Overrides and existing deferred-tax / lease / financial / equity rules retain precedence.

Tests: parameterized positive/negative/maturity coverage, no guided-judgment cases, override wins, synthetic two-period reformulation (NOWC/NOLA down; Net Debt unchanged). Lululemon: gift-card classifies all four periods; blockers now exactly PPE + Common stock; build probe first-raises `Property and equipment, net`.

---

## G1 closure evidence

| Check | Result |
|---|---|
| `unredeemed_gift_card_liability` / `Unredeemed gift card liability` → OWCL | **pass** (all four LULU periods) |
| Build unclassified set | `{Property and equipment, net, Common stock}` only |
| Temp-dir build first exception | `Property and equipment, net` (G2) |
| Source facts / committed reconcile bytes | **unchanged** |

**Remaining visible blockers:** G2 (PPE wording/identity), G3 (Common stock). G4–G7 unchanged.

---

## Artifact hashes (before / after verification)

| Artifact | SHA-256 | Size | Unchanged |
|---|---|---|---|
| standardized.json | `ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45` | 22289 | yes |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 | yes |
| provenance.json | `2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269` | 698793 | yes |

Before and after digests are identical for all three committed Lululemon artifacts.

---

## Measured verification (this step)

```text
PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_lululemon_benchmark.py -q
→ 126 passed in 3.13s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.77s

PYTHONPATH=. pytest core/tests -q
→ 768 passed in 86.87s
```

Prior Step 9M.2 recorded 736 core passes; this run is newly executed (+32 from G1 coverage and related additions).

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py`, and this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Positive / negative / maturity / override / reformulation tests | **pass** |
| Lululemon G1 resolved; G2/G3 still explicit | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G2–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**.
