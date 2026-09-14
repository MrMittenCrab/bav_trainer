# RESULT.md — Step 9M.2.3 Narrow Paid-In-Capital Exemptions and Reject Contradictory Liability Concepts (G3)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.4** — Lululemon Liability-Detail Reformulation Integrity (build blocker; G4 remains deferred)

**Plan base (IMPLEMENTATION.md):** `b142604cd183d3f1c3c6c0abb6e67aa7137ce242`  
**Workspace HEAD at completion:** `07b000c0254789046d01c03cf94c6a2ef6733c4f`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G4–G7 implementation or forecasting/valuation work.

This supersedes the previous Step 9M.2.3 G3 PASS claim: payment detection no longer treats bare `paidin` as a paid-in-capital exemption, and contradictory liability concepts on ordinary Common stock fail closed while supported liability labels and genuine PIC balances remain classified.

---

## What changed

In `core/model/classification.py`:

1. Narrowed `_common_stock_concept_has_payment` so only genuine `paidincapital` balance wording is exempt; `common_stock_paid_in_cash` / `paid_in_cash` now raise as payment movements. Payment stems (`cashpaid` / `paidfor`) still reject when paid-in-capital wording co-occurs.
2. Extended `_COMMON_STOCK_LIABILITY_CONCEPT_MARKERS` with accrued / pension / retirement-benefit / post-employment identities so both ordinary common-stock recognition routes reject contradictory concepts (`pension_obligation`, `accrued_expenses`, etc.).
3. Preserved label-side supported liability fall-through, movement scoping, and override precedence.

In `core/tests/test_classification.py`:

1. Added the three reported public-classifier failures plus retirement/post-employment concept contradictions.
2. Added normalized `paid_in_cash` / `common_stock_paid_in_cash` variants and payment+PIC co-occurrence cases.
3. Retained PIC Equity, Accrued expenses / pension-label + `common_stock` supported-liability, debt-concept, override, investment, redeemable, and G1/G2 controls.

`core/tests/test_lululemon_benchmark.py`: no edits required.

---

## G3 repair evidence

| Check | Result |
|---|---|
| Exact `common_stock` / whole-label `Common stock` → Equity, non-ambiguous | **pass** |
| `Common stock` + `common_stock_paid_in_cash` / `paid_in_cash` → `UnclassifiedBalanceSheetLineError` | **pass** |
| Payment stems co-occurring with paid-in-capital wording still raise | **pass** |
| `Common stock` + `pension_obligation` / `accrued_expenses` / retirement / post-employment concepts raise | **pass** |
| Accrued expenses / `common_stock` → Operating Working Capital Liability | **pass** |
| Pension / retirement / post-employment labels + `common_stock` → ambiguous OLT L + `pension_obligation_operating_vs_financing` | **pass** |
| `Common stock` + `paid_in_capital` / `additional_paid_in_capital` → non-ambiguous Equity | **pass** |
| PIC labels + PIC/`common_stock` concepts → non-ambiguous Equity | **pass** |
| Decisive debt-concept / override / investment / redeemable / G1 / G2 controls | **pass** |
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
→ 414 passed in 4.11s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 26.63s

PYTHONPATH=. pytest core/tests -q
→ 1032 passed in 85.00s
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
| All three reported pairs raise through the public classifier; genuine PIC balances remain Equity | **pass** |
| Supported liabilities retain exact categories and judgment behavior; existing classification controls pass | **pass** |
| Required verification passes; source facts / committed artifacts unchanged | **pass** |

**Proposed next (on PASS):** Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity. G4 remains deferred; Step 9 remains incomplete.
