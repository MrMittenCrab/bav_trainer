# RESULT.md — Step 9M.2.4.1.1 Repair Sparse Equity-Detail Evidence Reconciliation

**Status:** COMPLETE (this repair’s acceptance met; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1 — Repair Sparse Equity-Detail Evidence Reconciliation  
**Parents:** Step 9M.2.4.1 and Step 9M.2.4 — remain **UNRESOLVED**  
**Workspace HEAD:** `88ce9311a8851c0373ee930435f7af083e21be2f` (plan commit; base of prior incomplete repair `17114fc`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No branch create/switch. No G4–G7 or forecasting/valuation work.

---

## Correction of prior unsupported completion claim

Prior `RESULT.md` claimed sparse equity evidence was gated because `equity_gap` (implied NOA−Net Debt vs reported equity) was zero. That claim was **incorrect for equity detail**: omitting 100 of classified equity via explicit `None` left asset-detail, liability-detail, and **implied-equity** gaps at **0.0**, so balanced assets/liabilities alone incorrectly authorized missing equity detail. This revision adds an independent **equity-detail** reconciliation used by the sparse evidence gate; implied-equity remains a separate integrity check with unchanged A+L tolerance rules.

---

## What was implemented (production scope)

`core/model/classification.py` only (plus focused tests):

- Compute `equity_detail_gap` = signed Equity-category detail − independent `total_equity` (subtotals excluded).
- Sparse evidence gate now requires independent `total_assets`, `total_liabilities`, and `total_equity`, and successful **asset-detail**, **liability-detail**, and **equity-detail** reconciliations under unchanged rounding `max(1.0, 0.5 * (detail_count + 1))` with **equity-detail count** for the equity-detail envelope.
- Implied-equity identity (`equity_gap`) retained separately in `check_reformulation_integrity` with unchanged asset+liability count tolerance.
- Missing keys, unavailable totals, unsupported absence, and contradictory equity detail fail closed; source `None` values are never rewritten.

---

## Reproduction (100 equity omission) — measured gaps

Fixture: assets 200 / liabilities 50 / reported equity 150 both periods; Common stock 50; Retained earnings `{P1: 100.0, P2: None}`.

| Gap (P2) | Pre-gate measured | Post-repair |
|---|---:|---|
| asset-detail | 0.0 | gate rejects (no usable reformulation) |
| liability-detail | 0.0 | gate rejects |
| **equity-detail** | **−100.0** | gate rejects |
| implied-equity | 0.0 | gate rejects |

- Causal row: `retained_earnings` explicit `None` at P2 while reported total still includes 100.  
- Detail counts: A=1, L=1, E=2 → envelopes 1.0 / 1.0 / **1.5** (equity-detail); implied envelope remains 1.5 (A+L).  
- Post-repair: `MissingHistoricalValueError` for modeled period `2025-12-31`.

---

## Measured reformulation gaps (Lululemon committed standardized)

Tolerance formula unchanged: `max(1.0, 0.5 * (detail_count + 1))`.

| Period | asset-detail | liability-detail | equity-detail | implied-equity | A env | L env | E-detail env | implied env |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-01-29 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2024-01-28 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2025-02-02 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |
| 2026-02-01 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | 6.0 | 2.5 | 11.5 |

- Counts: assets 11 → 6.0; liabilities 11 → 6.0; equity detail 4 → 2.5; implied uses A+L=22 → 11.5.  
- NCIT series unchanged: **28555 / 15864 / 0.0 / `None`**.  
- `check_reformulation_integrity` → **PASS** all four periods.

---

## Anchors confirmed

- Common stock: **611 / 606 / 581 / 557**.  
- Gift-card (G1) and PPE (G2) assertions pass.  
- Unclassified non-subtotal BS detail set empty (G3).  
- NCIT `None` @ 2026-02-01 and reported `0.0` @ 2025-02-02 preserved.

---

## Workbook probe (temporary directory)

```text
MissingLineError: Required concept 'pretax_income' not found in statement lines
```

Recorded only; **not repaired** (outside this child’s production scope). Parents stay UNRESOLVED.

---

## Source / artifact hashes (before = after)

No generated refresh authorized; committed Lululemon artifacts unchanged.

| Artifact | SHA-256 | Size |
|---|---|---:|
| standardized.json | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| provenance.json | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| conflicts.json | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

Stray FR/demo mutations from the full suite were reverted.

---

## Fresh verification counts

```text
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py \
  core/tests/test_classification.py core/tests/test_line_resolver.py \
  core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q
→ 514 passed in 9.27s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.20s

PYTHONPATH=. pytest core/tests -q
→ 1066 passed in 86.97s
```

New/extended coverage in `test_classification.py`: unsupported 100-equity omission regression; leading/trailing/both/interior equity absence; reported zero vs eligible absence; missing keys; unavailable totals; equity-detail gaps at/beyond envelope; incomplete equity when sparse liability activates gate; signed treasury contra-equity; subtotal exclusion; explicit Equity override. Existing liability sparse success, rounding controls, Lululemon integrity, G1/G2/G3, and pretax workbook blocker assertion retained.

---

## Diff scope (intentional)

- `core/model/classification.py`
- `core/tests/test_classification.py`
- `core/tests/test_lululemon_benchmark.py`
- `RESULT.md` (this file)

Committed standardized/provenance/conflicts, source PDFs, extracted JSON: **unchanged**.

---

## Parent / plan notes (do not edit IMPLEMENTATION.md here)

Child 9M.2.4.1.1 acceptance for **independent equity-detail** sparse gating is met. Keep **Step 9M.2.4.1 and Step 9M.2.4 — UNRESOLVED** until every original parent acceptance criterion passes (workbook generation still blocked by `pretax_income` / further scope). Return to Plan for parent closure assessment and next unused detailed ID. Step 9 remains incomplete.
