# RESULT.md — Step 9M.2.3 Generic Common-Stock Equity Classification (G3)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity (build blocker; higher priority than G4 Capex Concept Identity)

**Plan base (IMPLEMENTATION.md):** `a86b9368095880bc3ad018d8d55b5ad3b41514fe`  
**Workspace HEAD at completion:** `5ccd7255d96f4b67b219fddf710f3e57333f5206`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G4–G7 implementation or forecasting/valuation work.

---

## What changed

In `core/model/classification.py`:

1. Added guarded ordinary common-stock equity recognition for exact concept token `commonstock` and whole-label `common stock`.
2. Excluded redeemable/redemption, mandatory, preferred/preference, investment, and issuance/proceeds/repurchase/payment/purchase/sale/change movements from either recognition route.
3. Wired `_common_stock_balance_decision` into the concept chain and the label-only public path; overrides and existing equity-component / G1 / G2 behavior preserved.

In tests:

1. Public-classifier regressions for exact-concept + neutral label, whole-label + empty/unrelated concepts, and case/whitespace variants → `Equity`, `ambiguous=False`.
2. Cross-route exclusion coverage for redeemable, mandatory redemption, preferred, investments, issuance proceeds, and repurchase/payment movements.
3. Controls for liability/investment fallthrough, existing equity components, G1/G2, override precedence, and no judgment case.
4. Lululemon: Common stock classifies as Equity with original four-period values; unclassified set empty; temp-dir build asserts `ReformulationIntegrityError` (`liability-detail gap`).

---

## G3 evidence

| Check | Result |
|---|---|
| Exact `common_stock` / whole-label `Common stock` → Equity, non-ambiguous | **pass** |
| Excluded instruments/movements cannot bypass either route | **pass** |
| Liability / investment / equity-component / G1 / G2 / override controls | **pass** |
| Lululemon Common stock values/identity intact (611 / 606 / 581 / 557) | **pass** |
| Unclassified BS detail set | `{}` (empty) |
| Temp-dir build first exception | `ReformulationIntegrityError` (`liability-detail gap`) |
| Source facts / committed Lululemon reconcile bytes | **unchanged** |

**Remaining visible blockers:** reformulation liability-detail gap (FY2023 ≈ −28555; FY2024 ≈ −15864; FY2025–FY2026 OK). G4–G7 unchanged thereafter.

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
→ 355 passed in 4.38s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.36s

PYTHONPATH=. pytest core/tests -q
→ 973 passed in 89.17s
```

0 failures; no execution restrictions.

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to allowed files plus this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Ordinary common-stock balances classify deterministically as Equity | **pass** |
| Excluded instruments/movements cannot bypass guards | **pass** |
| Lululemon has no unclassified BS detail rows; build advances past G3 | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none for this step’s scope. Measured build now blocks on `ReformulationIntegrityError` (missing liability detail vs Total Liabilities in earlier periods), so the next bounded plan should address that integrity gap before G4.

**Unresolved:** reformulation integrity gap, then G4–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity** (defer Generic Capex Concept Identity until the build probe advances).
