# Step 9M.2.4.1.1.1.20 — Lululemon G5 Source-Supported Lease and Deferred-Tax Coverage

AUTOCYCLE_PLAN: {"baseline": "At 237c265b81e71ced0d323814fe7924850baaf147, Lululemon has 248 practice cells but supplied right_of_use_lease_asset, deferred_tax_asset and deferred_tax_liability concepts do not activate existing diagnostics; Fast Retailing retains 491 cells. RESULT Trainer hashes are stale.", "finding_key": "explicit-concept-aliases-block-supported-lease-and-deferred-tax-analysis", "kind": "work", "objective": "Enable source-supported lease ROU and deferred-tax diagnostics", "plan_id": "3ea52e796f8f4e8294c4d13918cbaaff", "step_id": "9M.2.4.1.1.1.20", "success": "Unchanged Lululemon facts activate both existing diagnostic modules through generic explicit-concept aliases, adding verified practice coverage while preserving interest gating, capex and Fast Retailing's 491-cell contract; RESULT records final artifact hashes and unresolved parent acceptance.", "verification": "Read RESULT.md; inspect alias resolution and regression evidence; independently compare supplied balances and derived values with workbook formulas, semantic maps and Check coverage; recompute final release hashes and verify unchanged source/provenance artifacts and retained parent criteria.", "work_id": "ed0d79edb1bc4f9bbe126a527dab85b9"}

**Base:** `237c265b81e71ced0d323814fe7924850baaf147`
**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; respect permissions and unavailable access. No commits or pushes.
- Numbering remains administratively frozen; the controller assigns identity for new work. Preserve prior recovery/work records without reopening verified ownership or rewriting historical approval.
- Preserve source PDFs, extracted/reconciled facts, provenance, accepted capex changes and hash-bound recovery evidence.
- No issuer-specific rules, invented interest, inferred zeros, cash-interest substitution, new note extraction, forecasting or valuation.
- Limit edits to `core/model/line_resolver.py`, directly affected lease/deferred-tax modules and `core/engine/reference_model.py`, relevant tests, necessary release-generator changes, generated issuer releases, benchmark `GAPS.md` and `RESULT.md`.

## Task 1 — Activate existing diagnostics through explicit concept aliases

- Extend the shared explicit-concept alias contract: `right_of_use_lease_asset` → `right_of_use_assets`, `deferred_tax_asset` → `deferred_tax_assets`, and `deferred_tax_liability` → `deferred_tax_liabilities`.
- Retain canonical concepts and stored identities; preserve explicit-concept precedence without adding label heuristics. Multiple canonical/alias candidates remain ambiguous, including equal-valued duplicates.
- Ensure applicability, Python calculations and workbook source links resolve the same original rows. Retain existing missing/ambiguous-source omission and strict required-period-value behavior.
- Activate existing ROU level/change/growth/average/intensity and deferred-tax level/net-position/change diagnostics only; preserve reported signs and existing opening-period conventions.

## Task 2 — Verify source identity, numerical results and learner coverage

- Extend resolver, lease-ROU, deferred-tax and Lululemon benchmark tests for canonical/alias equivalence, mixed aliases, duplicates, misleading labels, absent sources, missing periods, explicit `None`, reported zero and standardized-data round trips.
- Independently verify four-period ROU balances `969419 / 1265610 / 1416256 / 1630181`, DTA `6402 / 9176 / 17085 / 24037`, DTL `55084 / 29522 / 98188 / 52278`, and net positions `-48682 / -20346 / -81103 / -28241`.
- Verify derived changes, averages and revenue intensity against supplied facts; inspect source-linked formulas after export/reload in both workbooks. Never infer deferred-tax expense, cash-tax effects, recoverability, lease interest or repayment flows.
- Verify added semantic identities and expected answers, blank yellow Trainer cells without Notes, matching Answer-Key formulas/Notes, visible parity and non-disclosing blank/correct/incorrect Check behavior.
- Run focused resolver/module tests, availability and capex regressions, both benchmark suites, affected reference/trainer tests and `core/tests`; record actual commands and subprocess exits. Distinguish formula inspection from spreadsheet recalculation and disclose unavailable verification.

## Task 3 — Regenerate releases and record measured improvement

- Stage builds using both issuer release scripts; verify each matched pair and synchronized maps/availability/supporting artifacts before replacement. Retain exactly two user-facing workbooks per issuer.
- Measure Lululemon coverage above the 248-cell baseline by module and semantic identity; preserve every previously supported cell, all 74 interest-unavailable displays per workbook and Fast Retailing’s 491-cell contract.
- Verify repeat-build semantic determinism and source/provenance equality. Run mutating Check exercises on disposable copies; keep final Trainers blank.
- After every final write, compute full SHA-256 hashes for both workbook pairs and associated release artifacts; record final-byte hashes in `RESULT.md`, explicitly superseding stale hashes.
- Update Lululemon G5 with measured evidence. Record child acceptance separately from capex acceptance, recovery ownership/publication and unresolved parent acceptance.

## Acceptance and carried-forward requirements

- Both source-supported modules activate without source mutation; Python values, source links, formulas, semantic maps and Check agree. Missing or contradictory evidence never produces fabricated analytical inputs.
- Preserve successful gated Lululemon generation, partial-period interest displays and dependency closure, opening-only CoD `0.374`, supported-history undefined-ratio semantics and no unavailable-history 4% substitute.
- Preserve supplied pretax resolution, distinct tax expense, explicit-concept precedence, ambiguity errors and strict missing-required-value failures outside optional gated analysis.
- Preserve four-period capex `638657 / 651865 / 689232 / 680802`, reformulation tolerances, liability/equity discrepancy explanations, independent asset/liability/signed-equity detail gates, sparse omission handling and contradiction rejection.
- Preserve source identities and comparative provenance; NCIT remains `28555 / 15864 / reported 0 / None`, and Common stock remains `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all 12 pretax/ETR cases, mutation controls, deterministic comparisons and failure immutability requirements.
- Retain the original parent temporary-build criterion: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; this step must preserve successful gated generation.
- Carry forward A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending closure, E11 NonReq UNVERIFIED, G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
- Carry both frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` forward; keep INPUT_STATUS PENDING until all requests are satisfied. Child acceptance does not close parents or authorize blanket DONE.
