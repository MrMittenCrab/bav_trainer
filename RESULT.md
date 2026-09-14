# RESULT.md — Step 9M.2.1 Repair Plural Gift-Card Movement Detection and Liability Fallback Escapes (G1)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.2** — Generic Property-and-Equipment Classification and PPE Identity (G2)

**Plan base:** `44e7651968651e38715e08ef8692d7acffb46eb3`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G2–G7 or forecasting/valuation work.

Supersedes prior Step 9M.2.1 G1 PASS (recognition-movement exclusions) that left plural `gift card liabilities` wording able to escape through liability label fallbacks.

---

## What changed

In `core/model/classification.py`:

1. Extended customer-prepayment label phrases with plural liability forms: `gift card liabilities`, `gift-card liabilities`, `gift cards liabilities`, `gift-cards liabilities` (singular forms retained).
2. Added matching exact concept aliases (`giftcardliabilities`, `giftcardsliabilities`, current/noncurrent variants) so label and concept topic recognition stay aligned for balance classification and movement protection.
3. Unchanged movement gate still raises `UnclassifiedBalanceSheetLineError` before concept classification and current / noncurrent / other-liability / long-term fallbacks.

Tests: reported failing label with empty concept; parameterized plural/spaced/hyphenated wording; recognition/derecognition/change/increase/decrease/amortization/additions/reductions; fallback-context escapes; movement+balance concept and movement-concept+balance-label pairs; positive current/noncurrent plural balance controls; explicit override control. Prior asset / unrelated / judgment / reformulation / Lululemon guards retained.

---

## Regression evidence vs base

New plural-gift-card raise cases were run against `44e7651` `classification.py` before the repair:

- **7 failed** (DID NOT RAISE / override precondition), including the reported label `Recognition of gift card liabilities within other current liabilities` and other-current / noncurrent / long-term liability fallback escapes.
- After repair: those cases raise; valid plural balances still classify; override still wins.

---

## G1 plural repair closure evidence

| Check | Result |
|---|---|
| Reported plural recognition label raises | **pass** |
| Plural wording + liability fallbacks cannot re-admit movements | **pass** |
| Valid current/noncurrent plural gift-card balances | **pass** |
| Override precedence on reported row | **pass** |
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
→ 195 passed in 3.04s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.04s

PYTHONPATH=. pytest core/tests -q
→ 837 passed in 87.59s
```

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is `core/model/classification.py`, `core/tests/test_classification.py`, and this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Plural gift-card movements raise (incl. reported label) | **pass** |
| No liability fallback escapes unless explicitly overridden | **pass** |
| Valid balances + reformulation + Lululemon G1 retained | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G2–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**.
