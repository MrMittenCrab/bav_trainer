# Step 9M.2.4.1.1.1.66 — Real-company normalization: source-to-selector qualification

AUTOCYCLE_PLAN: {"baseline": "At 4a1f827a1b8a7abd7218e6b9331349dcea4678a1, illustrative normalization Excel verification is accepted. Supplied Lululemon filing JSON contains income-statement impairment_and_restructuring observations, but build/input/lululemon-live/standardized.json has no corresponding income-statement candidate and current company assumptions contain no normalization candidates.", "finding_key": "real-company-normalization-source-to-selector-gap", "inputs": [{"commitment": "Continue the unfinished five-stage workflow through real-company normalization source qualification; retain original parent acceptance, documentary obligations and remaining source, implementation and spreadsheet work beyond this increment.", "id": "20260914-193338-000000004"}, {"commitment": "Apply TARGET's three-area analytical focus gate within the existing 120-cycle budget; qualify the missing real-company normalization dependency while preserving accepted geographic/KPI work, source binding, protected artifacts and deferred scope.", "id": "20260915-042248-000000005"}], "kind": "verification", "objective": "Qualify Lululemon impairment and restructuring evidence for normalization", "plan_id": "512736ff019643588afc95abb61cab90", "step_id": "9M.2.4.1.1.1.66", "success": "An independently source-checked five-period qualification ledger establishes supported candidate amounts, identity, signs and limitations, and a reproducible read-only trace identifies where the ordinary handoff loses or rejects them. Unsupported periods and judgments remain explicitly unresolved; real-company workbook and parent acceptance are not claimed.", "verification": "Read-only Review checks the ledger against supplied PDFs and immutable filing JSON, reproduces the ordinary reconciliation/standardization and selector trace, and authenticates recorded hashes, rejection evidence and protected-artifact parity.", "work_id": "9a9bf001dea84a868ef326d8ef5126ea"}

## Scope and constraints

- One bounded source-qualification objective; the controller assigns the new detailed step and work IDs. Accepted illustrative normalization and geographic/KPI Excel verification remain complete.
- Persist only `RESULT.md`; diagnostic scripts and derived evidence belong in permitted temporary storage. No production changes, extraction reruns, source amendments, live artifact replacement, publication, commits or pushes.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. Unavailable source, storage or execution access is a blocker; respect permissions.
- Preserve supplied PDFs/JSON, reconciliations, examples, releases, Fast Retailing data, APIs, semantic identities and `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

## Task 1 — Authenticate one real-company candidate history

- Inspect only the impairment/restructuring statement rows and directly supporting notes in `benchmark/lululemon/source/LULU_FY202{2,3,4,5}_Annual_Report.pdf`, the four corresponding `build/input/lululemon/extracted/` files and relevant retained provenance/conflicts.
- Produce a ledger for `2022-01-30`, `2023-01-29`, `2024-01-28`, `2025-02-02`, `2026-02-01`: document/hash, printed and physical PDF page, statement/section, exact label, reported amount, currency/unit, presentation role and proposed signed analytical amount.
- Distinguish income-statement expense from cash-flow add-back and geographic reconciliation observations. Establish overlapping-period agreement or document conflicts; do not combine changing labels solely because they share a suggested concept.
- Distinguish explicit reported zero from missing evidence. Inspect the directly relevant notes for composition and recurrence; do not infer deductibility, non-recurring treatment or documentary precedence from labels.

## Task 2 — Locate the source-to-selector acceptance gap

- Using `/Users/lizhiguo/Documents/Developer/.venv/bin/python`, trace the ordinary filing validation, reconciliation and standardization path through `core/ingestion/filing_reconciler.py`, `core/ingestion/filing_standardizer.py` and `core/model/normalization.py`; retain temporary intermediate outputs.
- Compare the candidate's statement-specific identities and values at each boundary with `build/input/lululemon-live/{standardized,provenance,conflicts}.json` and current company assumptions. Identify the exact rule or missing handoff responsible for its absence; distinguish deliberate rejection from data loss.
- Reproduce candidate selector resolution against unmodified ordinary output. Record the actual rejection or resolution, complete-history requirements and signed-value convention; do not insert a candidate or patch derived inputs to make the probe pass.
- Document whether `operating_pretax_effective_tax` can represent this disclosed aggregate without double counting. Separate source facts, a proposed analyst reference treatment and the effective-tax convention; leave unsupported treatment/composition questions open.

## Task 3 — Record reviewable qualification evidence

- Record generating SHA, commands/exits, source and intermediate hashes, inspectable evidence paths, period ledger and minimal reproducer in `RESULT.md`.
- Identify the smallest evidenced downstream correction or missing human/source decision, with the affected boundary and expected behavior. Record blockers without claiming that diagnosis repairs the handoff.
- Authenticate 50 protected artifacts against `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`, and eight extracts against `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`.

## Acceptance and retained commitments

- Every ledger period has inspectable supporting evidence or an explicit unresolved status. The missing candidate is explained by a reproducible ordinary-path trace; no invented amounts, zeros, dates, chronology or accounting judgments.
- Source qualification does not establish real-company normalization workbook acceptance. Candidate admission, any necessary implementation repair, treatment-dependent Excel verification and normalized per-share acceptance remain open where applicable.
- Preserve totals `766/768/760`, Fast Retailing `577`, 486 underlying identities, 101 unavailable displays, 56 geographic sources, 264 geographic practices and 15 segment-margin formulas.
- Preserve stores `574/655/711/767/811`, changes `None/81/56/56/44`, five revenue sources/eight revenue-store practices and accepted source authentication.
- Preserve management evidence: 135 observations (`29/36/37/33`), nine definitions, 107 market observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons and zero selections/revision links; real-source comparable-sales/SPSF admission remains closed.
- Preserve unique compatible uncontradicted documentary direction, occurrence-specific nonmissing reviser audit, complete-group membership, ambiguous incoming-candidate blocking and superseded evidence; infer no transitive precedence or assurance.
- Preserve 110 accepted additions, G1/G2/G3/G5 aliases, provenance/ambiguity/reformulation/causal-evidence gates, twelve pretax/ETR cases, sparse histories, partial interest closure and opening-only CoD `0.374`; invent no interest, lease repayments or deferred-tax interpretations.
- Preserve selected Americas `7928156`, audit-only `7928256`, signed bridges, capex `638657/651865/689232/680802`, repurchase residuals `-116195/1085647/-207544/-256674`, NCIT `28555/15864/0/None`, Common stock `611/606/581/557`, and retained discrepancy explanations.
- Retain `20260916-075534-000000006` extraction/source binding without restarting recovery or inventing `2021-01-31`; retain `20260918-115651-000000007` admitted reconciliation, production rejection and separately labeled synthetic signed-residual coverage.
- Both workflow commitments remain unfinished. Additional identities, larger-group selection, general evidenced later-audited precedence, broader physical-page mapping, unavailable supplied evidence and other analytical relationships remain unresolved.
- G6 opening BS, G7 lease maturity/notes, G8 deferral, G9 standalone interest completeness, segment assets/capex/significant expenses/D&A and benchmark publication remain outside this increment. Preserve parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`.
- Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED. Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4`, Step 9 and TARGET exit gates remain unresolved; independent M&A Net Debt, Complete NOPAT/RNOA, forecasting and valuation remain deferred.
