# RESULT.md — Step 9M.2.3 Repair Punctuation Movements, Liability Preservation, and Paid-In-Capital Balances (G3)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity (build blocker; G4 remains deferred)

**Plan base (IMPLEMENTATION.md):** `901a4b2df4a16d2469344e5d38b3e264a834a808`  
**Workspace HEAD at completion:** `e0eac83de22130d9fb4614dd8e3d099b3243effc`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G4–G7 implementation or forecasting/valuation work.

This supersedes the previous Step 9M.2.3 G3 PASS claim: punctuation-normalized payment movements now fail closed, supported accrued/pension liabilities are preserved against common-stock Equity override, and paid-in-capital balances remain Equity.

---

## What changed

In `core/model/classification.py`:

1. Added `_common_stock_label_key` punctuation folding for common-stock topic detection and payment-phrase matching (hyphens, em dashes, other punct → spaces).
2. Replaced unrestricted concept `paid` matching with payment-sensitive detection (`cashpaid` / `paidfor` / non-`paidin` `paid`) so `paid_in_capital` and `additional_paid_in_capital` balances are preserved; genuine payment stems still reject rows that also contain paid-in-capital wording.
3. Extended liability evidence markers with accrued / pension / retirement-benefit / post-employment so both ordinary common-stock recognition routes fall through to supported liability classification.
4. Kept movement guards scoped to common-stock identity and preserved explicit override precedence.

In `core/tests/test_classification.py`:

1. Expanded supported-liability regressions for Accrued expenses and pension / retirement / post-employment labels paired with `common_stock` (exact category, ambiguity, judgment codes).
2. Expanded payment-movement punctuation cases (`Cash-paid-for common-stock`, `Cash paid—for common stock`, `Paid-for common stock`, exact/empty/unrelated/fallback concepts).
3. Added paid-in-capital Equity regressions for `Common stock` + PIC concepts and PIC labels + PIC/`common_stock` concepts.
4. Retained ordinary common-stock, genuine-payment, override, investment, redeemable/preferred, other equity-component, and G1/G2 controls.

`core/tests/test_lululemon_benchmark.py`: no edits required.

---

## G3 repair evidence

| Check | Result |
|---|---|
| Exact `common_stock` / whole-label `Common stock` → Equity, non-ambiguous | **pass** |
| Punctuation-normalized payment movements raise (no cash/liability/equity fallback) | **pass** |
| Accrued expenses / `common_stock` → Operating Working Capital Liability | **pass** |
| Pension / retirement / post-employment + `common_stock` → ambiguous OLT L + `pension_obligation_operating_vs_financing` | **pass** |
| `Common stock` + `paid_in_capital` / `additional_paid_in_capital` → non-ambiguous Equity | **pass** |
| PIC labels + PIC/`common_stock` concepts → non-ambiguous Equity | **pass** |
| Unsupported liability contradictions raise | **pass** |
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
→ 401 passed in 4.02s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.10s

PYTHONPATH=. pytest core/tests -q
→ 1019 passed in 86.85s
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
| Punctuation-normalized common-stock payments fail closed unless explicitly overridden | **pass** |
| Supported accrued-expense and pension liabilities preserve classification/judgment; paid-in-capital remains Equity | **pass** |
| Existing classification controls pass; source facts / committed artifacts unchanged | **pass** |
| Required verification passes | **pass** |

**Proposed next (on PASS):** Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity. G4 remains deferred; Step 9 remains incomplete.
