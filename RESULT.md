# RESULT.md — Step 9M.2.1 Repair Customer-Prepayment Movement Exclusions and Liability Fallbacks (G1)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.2** — Generic Property-and-Equipment Classification and PPE Identity (G2)

**Plan base:** `da4b3e1b7b6ffc4c987ad5a0ec21ea893f595703`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G2–G7 or forecasting/valuation work.

Supersedes premature Step 9M.2.1 G1 PASS (gift-card / deferred-revenue balance classification) that left recognition movements and liability-fallback escapes unrepaired.

---

## What changed

In `core/model/classification.py`:

1. Added missing recognition movement markers (`recognition of` / `recognitionof`) alongside existing change / increase / decrease / amortization / additions / reductions / derecognition markers.
2. Detect customer-prepayment *movements* via bounded movement markers plus prepayment label phrases, exact balance concepts, or prepayment concept stems.
3. Raise `UnclassifiedBalanceSheetLineError` for those movements **before** current / noncurrent / other-liability / long-term label fallbacks can reclassify them.
4. Preserve valid balance classification, noncurrent-before-current maturity, asset/receivable exclusions, override precedence, and deferred-tax / lease / financial / equity treatment.

Tests: parameterized movement regressions (label-only, movement+balance concept, movement concept+balance label, noncurrent/long-term/other-liability fallback escapes) assert hard raises; movement override still wins; prior positive / soft-negative / judgment / reformulation / Lululemon guards retained.

---

## Regression evidence vs base

New movement-raise cases were run against `da4b3e1` `classification.py` before the repair:

- **12 failed** (DID NOT RAISE), including `Recognition of deferred revenue` (empty and balance concept), noncurrent contract recognition, and other-current / noncurrent / long-term liability fallback escapes.
- After repair: those cases raise; valid balances still classify.

---

## G1 repair closure evidence

| Check | Result |
|---|---|
| Recognition / other excluded movements raise | **pass** |
| Liability fallbacks cannot re-admit excluded movements | **pass** |
| Valid current/noncurrent prepayment balances | **pass** |
| Override precedence on movement rows | **pass** |
| Lululemon gift-card all four periods → OWCL | **pass** |
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
→ 161 passed in 3.30s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.86s

PYTHONPATH=. pytest core/tests -q
→ 803 passed in 89.71s
```

Prior premature G1 PASS recorded 768 core passes; this run is newly executed (+35 from movement-raise coverage and related additions).

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is `core/model/classification.py`, `core/tests/test_classification.py`, and this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Movement exclusions consistent; recognition covered | **pass** |
| Excluded movements cannot regain liability via fallbacks | **pass** |
| Hard `UnclassifiedBalanceSheetLineError` for unsupported movements | **pass** |
| Valid balances + reformulation + Lululemon G1 retained | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G2–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**.
