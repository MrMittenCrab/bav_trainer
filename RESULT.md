# RESULT.md — Step 9M.2.2 Repair PPE Balance Boundaries and Liability Preservation (G2)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.3** — Generic Common-Stock Equity Classification (G3)

**Plan base:** `ba110d4283616b3f336292d0cad35befe60569a8`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G3–G7 or forecasting/valuation work.

This RESULT supersedes the prior unsupported G2 closure that admitted payable/PPE-substring and trailing-movement fallthroughs.

---

## What changed

In `core/model/classification.py`:

1. Replaced PPE phrase-substring matching with punctuation-folded **whole-label** balance identity (`_ppe_label_key` + `_PPE_BALANCE_LABELS`), including plant wording and leading/trailing `net` variants.
2. Preserved exact balance concepts `property_plant_equipment` / `property_plant_and_equipment`, neutral-label concept recognition, and override precedence.
3. Expanded movement markers to position-independent singular/plural forms (additions, disposals, payments, sales, changes, and prior leading forms).
4. Added early `_is_ppe_movement` fail-closed before concept/label fallbacks so rejected movements cannot reach legacy plant/PPE asset matching.
5. Payable/liability labels containing PPE wording no longer match the PPE balancer; they fall through to existing payable classification.

In tests:

1. Payable regressions for `Accounts payable for property and equipment` / `Property and equipment payable` (empty, unrelated, `accounts_payable`).
2. Trailing and plant-wording movement fail-closed coverage; balance labels with movement concepts; movements with empty/unrelated/exact PPE concepts.
3. Replaced legacy expectation that `Purchases of property, plant and equipment` classifies as an asset with fail-closed.
4. Override still wins for rejected movements; positive balance / concept-only / no-judgment retained.
5. Resolver near-match list extended for reported movement and payable variants (no resolver code change).

---

## G2 repair evidence

| Check | Result |
|---|---|
| Whole-label PPE balances → OLTA | **pass** |
| Concept-only + punctuation/`net` variants | **pass** |
| Payable labels stay OWCL (empty/unrelated/payable concept) | **pass** |
| Trailing/leading/plant movements fail closed | **pass** |
| No legacy plant/PPE fallthrough for movements | **pass** |
| Override wins on balances and rejected movements | **pass** |
| Lululemon PPE resolves; all four values; `fixed_asset_applicable` | **pass** |
| Build unclassified set | `{Common stock}` only |
| Temp-dir build first exception | `Common stock` (G3) |
| Source facts / committed Lululemon reconcile bytes | **unchanged** |

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
→ 276 passed in 4.44s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 28.87s

PYTHONPATH=. pytest core/tests -q
→ 894 passed in 87.01s
```

0 failures; no execution restrictions.

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to allowed files plus this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| PPE whole-label matching; payables preserved | **pass** |
| Movement variants fail closed through public classifier + legacy path | **pass** |
| Valid PPE / resolver / fixed-asset / Lululemon G3 blocker intact | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G3–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**.
