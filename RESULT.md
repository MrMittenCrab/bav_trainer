# RESULT.md — Step 9M.2.3 Repair Common-Stock Liability and Movement Exclusions (G3)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity (build blocker; G4 remains deferred)

**Plan base (IMPLEMENTATION.md):** `b06b501860a6c148ab6e5319aa8293f0936d6ba5`  
**Workspace HEAD at completion:** `772c93b4d5217ae59a24797e687ec82d9620cba1`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G4–G7 implementation or forecasting/valuation work.

This supersedes the prior Step 9M.2.3 G3 PASS claim: ordinary common-stock Equity recognition is retained, but contradictory liabilities and cash-payment movements are now excluded / fail-closed.

---

## What changed

In `core/model/classification.py`:

1. Split instrument, movement, and liability-contradiction guards for ordinary common-stock recognition.
2. Reject liability wording on either label or concept so exact `common_stock` / whole-label `Common stock` cannot classify contradictory liabilities as Equity.
3. Detect payment movements via concept `paid` / label `paid for` and `cash paid` (preserving paid-in capital).
4. Raise `UnclassifiedBalanceSheetLineError` for common-stock movements before cash, liability, or equity-component fallbacks.
5. Preserve supported liability fallthrough (`Long-term debt`, payables, other liabilities), investment/redeemable controls, overrides, and G1/G2 behavior.

In `core/tests/test_classification.py`:

1. Supported liability-label + `common_stock` regressions with exact categories.
2. Unsupported liability contradictions raise.
3. `Cash paid for common stock` / `cash_paid_for_common_stock` / punctuation-normalization / fallback-wording movements raise.
4. Paid-in-capital and payment-override controls retained.

`core/tests/test_lululemon_benchmark.py`: no edits required; existing G3 / build-blocker assertions still hold.

---

## G3 repair evidence

| Check | Result |
|---|---|
| Exact `common_stock` / whole-label `Common stock` → Equity, non-ambiguous | **pass** |
| Liability labels + `common_stock` → supported liability categories (not Equity) | **pass** |
| Unsupported liability contradictions raise | **pass** |
| Cash-paid / payment movements raise (no cash/liability/equity fallback) | **pass** |
| Investment / redeemable / equity-component / G1 / G2 / override controls | **pass** |
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
→ 383 passed in 4.05s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 26.85s

PYTHONPATH=. pytest core/tests -q
→ 1001 passed in 85.76s
```

0 failures; no execution restrictions.

Temp-dir build probe:

```text
ReformulationIntegrityError
2023-01-29: liability-detail gap=-2.856e+04 (... envelope=5.5); equity gap=2.856e+04
2024-01-28: liability-detail gap=-1.586e+04 (... envelope=5.5); equity gap=1.586e+04
```

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to allowed files plus this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Both recognition routes exclude contradictory liabilities; supported liability behavior survives | **pass** |
| Common-stock payment movements fail closed unless explicitly overridden | **pass** |
| Valid common-stock balances and classification controls pass; source facts / committed artifacts unchanged | **pass** |
| Required checks measured and green | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none for this step’s scope. Measured build still blocks on `ReformulationIntegrityError` (missing liability detail vs Total Liabilities in earlier periods), so the next bounded plan should address that integrity gap before G4.

**Unresolved:** reformulation integrity gap, then G4–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity** (defer Generic Capex Concept Identity until the build probe advances).
