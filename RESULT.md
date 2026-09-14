# RESULT.md — Step 9N.3 Source-Supported Lease-Repayment Diagnostics

**Status:** Step 9 exit gate **FAIL** — lease-repayment curriculum blocker cleared; do not declare Step 9 complete or advance to Step 10 from this module alone.

**Implementation base (plan):** `3eb729b26e21cc6d8bb8c41864296f8b35f739e8`
**HEAD at completion:** `7cf80133a03c9c585d1e1cb24db5f6e3b796c760`

Writable / required supporting edits:
- New: `core/model/lease_repayment.py`, `core/tests/test_lease_repayment.py`
- Catalog / model / Check / workbook: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`
- Verification: `core/tests/test_fast_retailing_benchmark.py`, `core/tests/test_historical_v1_exit_gate.py`, `core/tests/test_capex.py` (FR total specs), `core/model/line_resolver.py`, `core/tests/test_line_resolver.py`
- Records: `docs/GOOGL_HISTORICAL_REFERENCE.md`, `RESULT.md`

`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No forecasting / valuation / Step 10 work. No commit / push / sync / checkpoint.

---

## Task 1 — Source resolution and calculations

- Added `core/model/lease_repayment.py` following `capex.py` conventions.
- Unique exact-concept CF `repayments_of_lease_liabilities` only; absent / ambiguous / label-only / wrong-statement → module off.
- `lease_repayments = -reported_repayments`; `lease_repayments_to_revenue = ratio_or_na(...)`; never `abs()`; no inference from liability/ROU/interest or Δ balances.
- Missing/`None` required period values fail closed via `MissingHistoricalValueError`.

## Task 2 — Practice surface integration

- `LEASE_REPAYMENT_COMPONENT_CATALOG` families `lease_repayments` / `lease_repayments_to_revenue`, orders **122–123**, category/semantic prefix `lease_repayment`.
- Reference-model → expected values → semantic map → ALT DuPont `LEASE REPAYMENT CONTEXT` → Check.
- Reported CF links populated; practice cells negate source and compute revenue intensity.
- Answer-Key Notes distinguish signed repayment cash from total lease cost, ROU amortization, and liability movement.
- Historical catalog freeze extended to orders **1–123** with explicit ID/order assertions.

## Task 3 — Measured verification

### Commands run

```text
python -m pytest core/tests/test_lease_repayment.py core/tests/test_historical_v1_exit_gate.py core/tests/test_fast_retailing_benchmark.py -q
→ 48 passed in 7.57s

python -m pytest core/tests -q
→ 587 passed in 62.64s

git diff --check
→ pass (exit 0)

git diff --name-only
→ core/engine/component_catalog.py
→ core/engine/reference_model.py
→ core/model/historical_expected.py
→ core/model/line_resolver.py
→ core/tests/test_capex.py
→ core/tests/test_fast_retailing_benchmark.py
→ core/tests/test_historical_v1_exit_gate.py
→ core/tests/test_line_resolver.py
→ core/trainer/checker.py
→ core/trainer/workbook.py
(+ untracked core/model/lease_repayment.py, core/tests/test_lease_repayment.py; docs/RESULT updates)
```

### Fast Retailing anchors (measured)

- `lease_repayments` FY2021–FY2025: **148248 / 136889 / 140646 / 146403 / 140483** (JPY mn; −reported)
- Ratios vs revenue `(2132992, 2301122, 2766557, 3103836, 3400539)` independently asserted
- Specs: `lease_repayment_specs=10`, `capex_specs=10`, liability/ROU unchanged, `expected_specs=491`
- Conflicts preserved: overlap **3**, supplemental **3**
- DEMO unchanged (no repayment concept; 74/312 ordinary practice counts)

### Preserved deferrals

- Lease discount-rate analysis
- Complete lease roll-forward
- ROU acquisition-payment diagnostics (`payments_for_rou_assets`)

---

## Six-row exit-criteria reassessment

| # | Exit criterion (TARGET) | Disposition | Evidence |
|---|---|---|---|
| 1 | GOOGL historical reference audit has no unresolved high-value historical gap | **fail** *(improved)* | Repayment gap cleared; remaining deferred lease/tax/SBC/acquisition items stay deferred with documented reasons, but audit still tracks open curriculum queue / planner must select next highest-value Step 9 item. |
| 2 | Historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason | **pass** *(new)* | Material FR repayment CF facts now implemented+tested; remaining lease extensions explicitly deferred (rates / roll-forward / ROU acquisition). |
| 3 | Source-document → filing JSON → reconciliation → StandardizedFinancials → reference-model → Trainer/Answer-Key demonstrated on real-company data | **pass** | FR benchmark green; `expected_specs=491`; blank/filled Check 491. |
| 4 | Optional historical modules fail closed when required evidence is missing or contradictory | **pass** | Unit gating + full `core/tests` **587 passed**. |
| 5 | Historical schedules, practice surfaces, Check, provenance, workbook generation pass required regression and benchmark tests | **pass** | Required trio **48 passed**; full suite **587 passed**; `git diff --check` clean. |
| 6 | No known historical defect or missing module materially limits learner analysis of an unfamiliar non-financial company | **fail** *(improved)* | Repayment cash topic no longer untaught; other deferred modules remain intentionally out of scope and are not claimed as blockers here, but Step 9 exit still requires planner confirmation that no other high-value source-supported gap remains. |

**Gate decision:** Step 9 **not complete**. Do **not** advance to Step 10.

---

## Unresolved blockers (visible)

1. ~~Catalog-freeze regression~~ — cleared (9N.2).
2. ~~Lease repayment diagnostics gap~~ — **cleared** (9N.3).
3. **Step 9 exit still open** — criteria 1 and 6 remain fail pending next planner selection among remaining deferred/queue items; no automatic Step 10.

Preserved separate deferrals (not next by default): lease discount-rate; complete lease roll-forward; ROU acquisition-payment diagnostics.

---

## Plan changes required

1. **Writable-list omissions for 9N.3:** implementing exact-concept resolution required edits to `core/model/line_resolver.py` and `core/tests/test_line_resolver.py` (same pattern as prior `payments_for_ppe`). FR total-spec assertions in `core/tests/test_capex.py` also needed `481 → 491`. Record these as required writable paths for any similar module.
2. **`benchmark/fast_retailing/BASELINE.md`:** audit run during tests rewrote Stage 4/6/7 counts to 491; reverted because not listed writable. Committed BASELINE still shows 481 — schedule a documentation sync when baseline updates are authorized.
3. **Audit script message:** `scripts/audit_fast_retailing_benchmark.py` still omits `lease_repayment_specs=` from Stage 4 text (dynamic `expected_specs` count is correct). Optional follow-up to append the new module count for parity with capex.
4. No TARGET/IMPLEMENTATION ownership rewrite requested beyond scheduling the next Step 9 candidate after this clearance.

---

## Exactly one next implementation

**Name:** *(deferred to planner)* — repayment blocker cleared; select the highest-value remaining source-supported Step 9 gap from `docs/GOOGL_HISTORICAL_REFERENCE.md` without inventing polish or starting Step 10.
