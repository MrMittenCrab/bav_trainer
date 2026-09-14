# RESULT.md — Step 9M.2.3 Restrict Paid-In-Capital Exemptions to Balance Wording (G3)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity (build blocker; G4 remains deferred)

**Plan base (IMPLEMENTATION.md):** `4f2dcc1bfe5b41a836f15507a186adc93e8c861d`  
**Workspace HEAD at completion:** `7487d298380ebd1818b0c3f619fafd6c76ea68ca`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G4–G7 implementation or forecasting/valuation work.

This supersedes the previous Step 9M.2.3 G3 PASS claim: `paidincapital` now exempts only the balance phrase itself and no longer suppresses separate payment wording (e.g. `paidincash`) co-occurring in the same normalized concept. The reported pair `Common stock` / `common_stock_paid_in_cash_from_paid_in_capital` raises through the public classifier; genuine PIC balances remain Equity.

---

## What changed

In `core/model/classification.py`:

1. Repaired `_common_stock_concept_has_payment` to strip `paidincapital` and then test residual `paid` wording, instead of returning False whenever `paidincapital` appears anywhere.
2. Preserved payment-stem (`cashpaid` / `paidfor`) precedence, movement scoping, supported liability routing, contradictory-liability rejection, and override precedence.

In `core/tests/test_classification.py`:

1. Added the exact reported pair `Common stock` / `common_stock_paid_in_cash_from_paid_in_capital` to `test_common_stock_payment_movements_raise_unclassified` (failed closed before the repair; passes afterward).
2. Parameterized co-occurring paid-in-cash + paid-in-capital wording across snake_case, CamelCase, hyphen/punctuation, reversed phrase order, and additional-paid-in-capital variants.
3. Retained `paid_in_capital` / `additional_paid_in_capital` Equity balance controls and existing cash-paid/paid-for, ordinary common-stock, liability, investment, redeemable, override, and G1/G2 controls.

---

## G3 repair evidence

| Check | Result |
|---|---|
| Exact `Common stock` / `common_stock_paid_in_cash_from_paid_in_capital` → `UnclassifiedBalanceSheetLineError` | **pass** (raised incorrectly as Equity before repair) |
| Normalized co-occurrence variants (snake/Camel/punct/reversed/APIC) raise | **pass** |
| `Common stock` / `paid_in_capital` / `additional_paid_in_capital` → Equity, `ambiguous is False`, `judgment_code is None` | **pass** |
| Existing cash-paid / paid-for + PIC co-occurrence still raises | **pass** |
| Ordinary common-stock / liability / investment / redeemable / override / G1 / G2 controls | **pass** |
| Lululemon Common stock identity/values intact (611 / 606 / 581 / 557) | **pass** |
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
→ 422 passed in 4.09s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 26.45s

PYTHONPATH=. pytest core/tests -q
→ 1040 passed in 84.64s
```

0 failures; no execution restrictions.

Temp-dir build probe:

```text
ReformulationIntegrityError
2023-01-29: liability-detail gap=-2.856e+04 (... envelope=5.5); equity gap=2.856e+04
2024-01-28: liability-detail gap=-1.586e+04 (... envelope=5.5); equity gap=1.586e+04
```

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to `core/model/classification.py`, `core/tests/test_classification.py`, and this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Reported pair and normalized co-occurrence regressions raise through `classify_balance_sheet_line` | **pass** |
| Genuine paid-in-capital balances retain exact Equity metadata | **pass** |
| Required verification passes; source facts / committed artifacts unchanged | **pass** |

**Proposed next (on PASS):** Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity. G4 remains deferred; Step 9 remains incomplete.
