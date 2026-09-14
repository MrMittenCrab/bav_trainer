# RESULT.md — Step 9M.2.2 Generic Property-and-Equipment Classification and PPE Identity (G2)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.3** — Generic Common-Stock Equity Classification (G3)

**Plan base:** `f718ef4d90a8c6a0ab22766c8b2b9ba73be3634a`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G3–G7 or forecasting/valuation work.

---

## What changed

In `core/model/classification.py`:

1. Added deterministic PPE net-balance classification (`_ppe_balance_decision`) as `Operating Long-Term Asset` with no judgment case.
2. Exact balance concepts: `property_plant_equipment`, `property_plant_and_equipment`.
3. Bounded balance label phrases including `property and equipment` / plant wording variants.
4. Movement markers (purchase/proceeds/depreciation/impairment/additions/payments/sale/change) reject the new matcher; legacy plant-wording behavior preserved.
5. Override precedence unchanged.

In `core/model/line_resolver.py`:

1. Explicit concept alias `property_plant_and_equipment` → canonical `property_plant_equipment` at priority 1; stored `LineItem.concept` unchanged.
2. Canonical + alias share P1; duplicate rows raise `AmbiguousLineError`.
3. Exact net-balance label aliases: `property and equipment net`, `property plant and equipment net` (plus prior aliases retained).

Tests: public classifier regressions; resolver alias/label/precedence/ambiguity/movement rejection; synthetic fixed-asset averages/turnover/intensity; Lululemon PPE classify/resolve/fixed-asset unlock and Common-stock-only build blocker. G1 gift-card coverage retained.

---

## G2 closure evidence

| Check | Result |
|---|---|
| Reported `Property and equipment, net` → OLTA | **pass** |
| Concept-only + label-only PPE recognition | **pass** |
| Movement labels/concepts not admitted by new matcher | **pass** |
| Override precedence | **pass** |
| Alias concept resolves; stored concept unchanged | **pass** |
| Lululemon PPE all four periods classify + resolve to original index | **pass** |
| `fixed_asset_applicable` becomes true | **pass** |
| Build unclassified set | `{Common stock}` only |
| Temp-dir build first exception | `Common stock` (G3) |
| Source facts / committed reconcile bytes | **unchanged** |

**Remaining visible blockers:** G3 (Common stock). G4–G7 unchanged.

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
PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q
→ 253 passed in 4.84s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 28.61s

PYTHONPATH=. pytest core/tests -q
→ 871 passed in 87.28s
```

Prior-review note (per plan): do not equate this run with the excluded mismatched log that cited 177 passing tests and seven reproduced base failures; this step’s measured suite is the three commands above, with **0 failures** and no execution restrictions.

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to allowed files plus this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Generic PPE classify + canonical resolve without source mutation | **pass** |
| No unsafe new movement matches; no silent ambiguity | **pass** |
| Lululemon fixed-asset availability restored; build → G3 Common stock | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G3–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**.
