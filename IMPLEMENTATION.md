# Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)

**Base:** `9c0a6aab0e9e7cc70bdb6c24d2f9cd90daee4d81`
**Goal:** Classify explicit customer-prepayment liabilities generically and remove Lululemon’s G1 build blocker.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source inputs, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards.
- No issuer-specific rules, source relabeling, benchmark overrides, G2–G7 implementation, or forecasting/valuation work.
- Generate test artifacts only in temporary directories.

## Task 1 — Add generic liability classification

- Extend the existing classifier with guarded, deterministic support for explicit gift-card, unearned-revenue, deferred-revenue, and contract-liability balance concepts and compatible labels.
- Classify `unredeemed_gift_card_liability` / `Unredeemed gift card liability` as `Operating Working Capital Liability`.
- Preserve the existing working-capital default for unqualified deferred-revenue / contract-liability balances; classify explicitly noncurrent variants as `Operating Long-Term Liability`, checking noncurrent before current.
- Use bounded concept aliases and compatible liability wording; do not infer liability classification from generic “gift”, “card”, “contract”, or “revenue” substrings.
- Prevent contradictory asset wording and movement/derecognition concepts from entering the new balance rule or slipping through its broad liability-label fallback.
- Preserve explicit override precedence and existing deferred-tax, lease, financial-instrument, and equity treatment.

## Task 2 — Verify classification and reformulation

- Add parameterized non-Lululemon tests covering gift-card spelling variants, supported concept/label pairs, label-only liability wording, and current/noncurrent treatment.
- Cover unsupported or contradictory pairs, contract assets, gift-card receivables, and movement/derecognition concepts; require safe existing classification or fail-closed behavior.
- Verify deterministic decisions create no guided-judgment case and explicit overrides still win.
- Add a balanced two-period synthetic reformulation case proving current balances reduce NOWC, noncurrent balances reduce NOLA, and neither increases Net Debt; equity reconciliation must remain intact.

## Task 3 — Advance benchmark expectations and record verification

- Assert the unchanged Lululemon gift-card row classifies correctly across all four periods.
- Update the blocker regression to require exactly `Property and equipment, net` and `Common stock` to remain unclassified.
- Re-run the temporary-directory build probe and assert the measured next blocker; do not weaken it to accept any exception.
- Retain deterministic reconciliation, committed-hash, failure-path guard, and no-issuer-branch assertions.

Run:

- `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_lululemon_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests -q`

Record completion and measured results in `RESULT.md`, including G1 closure evidence, remaining G2/G3 blockers, before/after reconciliation hashes, and repository diff scope. Distinguish newly executed checks from prior recorded results; report any restrictions or failures.

## Acceptance and next step

- Generic gift-card and deferred-revenue liability classification passes positive, negative, maturity, override, and reformulation tests.
- Lululemon G1 is resolved without changing source facts or committed reconciliation bytes; G2/G3 remain explicitly visible.
- Required checks pass and immutability guards remain effective.
- On failure, retain **Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)**.
- On PASS, propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**; Step 9 remains incomplete.
