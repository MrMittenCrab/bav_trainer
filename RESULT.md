# RESULT.md — Step 9M.2.2 Normalize PPE Topic Detection and Reject Punctuation Movements (G2)

**Status:** PASS  
**Completion:** DONE  
**Next step:** Step **9M.2.3** — Generic Common-Stock Equity Classification (G3)

**Plan base (IMPLEMENTATION.md):** `ab19f79ba93ce5eca0b59a92644ec0ece2d06476`  
**Workspace HEAD at completion:** `01eb2d805cb141df7d3ccf660649c72a4ae9eb00`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged).  
No commit / push / sync / checkpoint. No G3–G7 or forecasting/valuation work.

This RESULT supersedes the prior G2 PASS that closed whole-label/payable/trailing-movement boundaries but still admitted ampersand and Oxford-comma movement fallthroughs.

---

## What changed

In `core/model/classification.py`:

1. Folded `_PPE_CONTENT_LABEL_PHRASES` to punctuation-normalized keys (`property and equipment`, `property plant and equipment`, `plant and equipment`).
2. Applied `_ppe_label_key` to label topic detection so comma, Oxford-comma, ampersand, and whitespace variants share that vocabulary.
3. Kept whole-label balance matching exact (`_ppe_balance_label_hit`); topic substring matching remains movement-gate only.
4. Existing early `_is_ppe_movement` fail-closed and override precedence unchanged.

In tests:

1. Public-path regressions for `Property plant & equipment additions` and `Property, plant, and equipment disposals` with empty / unrelated / both exact PPE balance concepts.
2. Normalized topic variants with leading/trailing additions, disposals, payments, sales, and changes.
3. Matching punctuation balance controls remain `Operating Long-Term Asset`; payable, movement-concept, no-judgment, and override coverage retained/extended.
4. Resolver near-match list extended with both reported punctuation movement labels (no resolver code change).

---

## G2 punctuation-repair evidence

| Check | Result |
|---|---|
| Ampersand / Oxford-comma movements fail closed (public classifier) | **pass** |
| Exact PPE concepts cannot mask those label-topic failures | **pass** |
| Leading/trailing singular/plural punctuation topic variants fail closed | **pass** |
| Matching punctuation balances remain OLTA | **pass** |
| Payable / override / G1 / whole-label / plant-wording coverage retained | **pass** |
| Resolver near-match rejects both reported labels | **pass** |
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
→ 314 passed in 4.17s

PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q
→ 132 passed in 27.00s

PYTHONPATH=. pytest core/tests -q
→ 932 passed in 86.01s
```

0 failures; no execution restrictions.

Incidental FR/DEMO workbook/provenance refreshes from the suite were restored; final working-tree diff is scoped to allowed files plus this `RESULT.md`.

---

## Acceptance

| Criterion | Result |
|---|---|
| Reported punctuation movements + variants fail closed through public classifier | **pass** |
| Valid PPE balances / payables / overrides / resolver / fixed-asset intact | **pass** |
| Exact Lululemon G3 blocker (`{Common stock}`) intact | **pass** |
| Required checks + immutability / hash / no-issuer guards | **pass** |
| Diff scoped to allowed files | **pass** |

**Plan changes needed:** none.

**Unresolved:** G3–G7 as previously recorded; Step 9 **not** complete. Propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**.
