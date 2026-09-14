# RESULT.md — Step 9N.2 Repair Historical Active-Catalog Freeze

**Status:** Step 9 exit gate **FAIL** — catalog-freeze regression cleared; material source-supported lease-repayment gap remains unresolved. Exactly one next Step 9 implementation selected.

**Implementation base:** `8ddee77790761659ec61fef4c3be884cfe42115a`
**HEAD at repair:** `acf840052f208ef30fe28938d41e4496e27eee26`

Writable files touched: `core/tests/test_historical_v1_exit_gate.py`, `docs/GOOGL_HISTORICAL_REFERENCE.md`, `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No production code, fixtures, or benchmark expectations modified.

---

## Task 1 — Catalog contract repair

- Extended `ACTIVE_CATALOGS` with `GOODWILL_INTANGIBLES_COMPONENT_CATALOG`, `DEFERRED_TAX_COMPONENT_CATALOG`, and `CAPEX_COMPONENT_CATALOG`; retained lease ROU and prior catalogs.
- Frozen complete active historical namespace: family orders **1–121**.
- Asserted explicit post–v1 family-ID/order mappings: goodwill/intangibles **98–111**, lease ROU **112–115**, deferred tax **116–119**, capex **120–121**.
- Preserved uniqueness checks and deferred-ID / forecasting-valuation category isolation.
- Clarified test description to cover the current Step 9 historical namespace; existing DEMO workbook assertions unchanged (78 families / 332 practice cells).

---

## Measured verification (this step — new)

### Commands run

```text
python -m pytest core/tests/test_historical_v1_exit_gate.py -q
→ 7 passed in 1.49s

python -m pytest core/tests -q
→ 571 passed in 61.78s

python -m pytest core/tests/test_fast_retailing_benchmark.py -q
→ 26 passed in 5.89s

git diff --check
→ pass (exit 0)

git diff --name-only
→ core/tests/test_historical_v1_exit_gate.py
→ RESULT.md
→ docs/GOOGL_HISTORICAL_REFERENCE.md
```

### Fast Retailing evidence (unchanged; asserted by benchmark)

- Practice specs: **481**
- Capex specs: **10**
- Overlap conflicts: **3**
- Supplemental conflicts: **3**

### Prior measurements (Step 9N.1 — superseded for criterion 5)

```text
python -m pytest core/tests -q
→ 1 failed, 570 passed  (catalog freeze; now green)

Lease liability / ROU unit tests: 34 passed (documentation step; not rerun here)
```

---

## Six-row exit-criteria reassessment

| # | Exit criterion (TARGET) | Disposition | Evidence |
|---|---|---|---|
| 1 | GOOGL historical reference audit has no unresolved high-value historical gap | **fail** | Material Fast Retailing lease-repayment CF facts still lack Trainer repayment diagnostics. |
| 2 | Historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason | **fail** | Repayment analysis remains source-supported and material, neither implemented nor validly deferred. Discount-rate / full roll-forward / ROU-acquisition-payment remain separately deferred. |
| 3 | Source-document → filing JSON → reconciliation → StandardizedFinancials → reference-model → Trainer/Answer-Key demonstrated on real-company data | **pass** *(FR benchmark reconfirmed this step)* | `test_fast_retailing_benchmark.py` **26 passed**; `expected_specs=481`. |
| 4 | Optional historical modules fail closed when required evidence is missing or contradictory | **pass** *(suite reconfirmed this step)* | Full `core/tests` green; FR conflicts 3+3 unchanged. |
| 5 | Historical schedules, practice surfaces, Check, provenance, workbook generation pass required regression and benchmark tests | **pass** *(new)* | Catalog freeze repaired: `core/tests` **571 passed**; exit-gate file **7 passed**; FR **26 passed**. |
| 6 | No known historical defect or missing module materially limits learner analysis of an unfamiliar non-financial company | **fail** | Missing repayment diagnostics leave a material financing cash-conversion / lease-cash topic untaught despite supplied CF facts. Catalog-freeze blocker cleared. |

**Gate decision:** Step 9 **not complete**. Do **not** advance to Step 10.

---

## Unresolved blockers (visible)

1. ~~Catalog-freeze regression~~ — **cleared** (criterion 5 green).
2. **Lease repayment diagnostics gap** — criteria 1, 2, 6 (curriculum). Remains the sole material exit-gate curriculum blocker.

Preserved separate deferrals (not next): lease discount-rate analysis; complete lease roll-forward; ROU acquisition-payment diagnostics.

---

## Exactly one next implementation

**Name:** Source-supported lease-repayment diagnostics

**Why:** Highest-value remaining Step 9 gap after catalog-freeze repair. Material CF `repayments_of_lease_liabilities` is supplied and selected on Fast Retailing; liability/ROU **balance** modules do not analyze repayment cash; ΔLL ≠ repayments.

**Distinct from:** discount-rate analysis, complete lease roll-forward, ROU acquisition-payment diagnostics (remain deferred).

**Plan changes required:** none to TARGET/IMPLEMENTATION ownership; schedule lease-repayment diagnostics as the next Step 9 implementation.
