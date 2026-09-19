# Step 3.1 — Make the professional BAV workbook the default build product

AUTOCYCLE_PLAN: {"finding_key": "Make the professional BAV workbook the default build product", "inputs": [{"commitment": "Preserve accepted geographic, store-count, KPI, normalization, ingestion, workbook and regression work. After this BAV-first transition, prioritize real-source comparable-sales/SPSF admission and historical Revenue per Store production acceptance before further normalization expansion. Retain source-evidence blockers, formula/Notes, Trainer, Check, export/reload and required Excel verification obligations; the professional BAV replaces the former Answer Key.", "id": "20260918-165258-000000008"}, {"commitment": "Publish the BAV-first TARGET and historical Lululemon SESSION. Make the ordinary source-bound build produce Lululemon_BAV.xlsx without requiring Trainer generation, and preserve optional derivation of Lululemon_BAV_Trainer.xlsx. Subsequent work resolves KPI evidence, tests disclosure-led historical revenue drivers and connects results to strategy within the historical-only boundary.", "id": "20260919-093355-000000009"}, {"commitment": "Establish the professional BAV as the authoritative analytical workbook and the Trainer as its secondary derivative. Remove exercise framing from the primary deliverable while preserving the complete model and accepted work. Retain employer-ready driver-and-strategy analysis as the Session Endpoint, using generic methods, real evidence and explicit distinctions between disclosures, facts, identities, relationships and inference.", "id": "20260919-181505-000000010"}], "kind": "work", "objective": "Make the professional BAV workbook the default build product", "plan_id": "2177010956bf402e87ae2c1abe5015ad", "step_id": "3.1", "work_id": "381ee7bd9415433291c296292be312a6"}

## Completion

The ordinary source-bound command `python -m bav build Lululemon` produces and verifies a professionally presented `Lululemon_BAV.xlsx` without generating or requiring a Trainer, while the same completed model can still produce a working `Lululemon_BAV_Trainer.xlsx`.

## Bounded work

- Reuse the existing reference model, source validation, reconciliation, semantic mapping and current-snapshot publication path.
- Separate completed-model finalization from Trainer derivation in `core/trainer/workbook.py`; formulas, analytical Notes and required metadata must exist in the BAV without calling Trainer generation.
- Update company output routing, staged verification, CLI reporting and necessary consumers in `core/current_build.py`, `core/__main__.py` and directly affected modules to recognize `<Company>_BAV.xlsx` as the primary product.
- Preserve atomic publication, protected-path checks and rejection of invalid source inputs. Verify the primary artifact and supporting audit/semantic files independently of Trainer existence.
- Preserve optional Trainer derivation through the existing interface where practical; add no new CLI command solely to distinguish products. Use `<Company>_BAV_Trainer.xlsx` and resolve Check against its matching BAV.
- Give the BAV a professional opening identifying company, historical coverage, units, analytical structure, source basis and availability limitations. Remove visible Trainer, Answer Key, exercise, practice and learner-Check instructions from the BAV.
- Retain populated source facts, calculations, useful analytical Notes and reconciliation diagnostics. BAV cells must not contain yellow exercise formatting; blank practice cells and learning instructions belong only in the Trainer.
- Preserve Trainer sanitization, blank-yellow active practice cells without answers or hints, and non-disclosing workbook-wide Check. Derivation must not mutate the BAV.
- Update directly affected documentation and regressions for the new product contract. Apply generic behavior rather than Lululemon-specific analytical rules.

## Verification and evidence

- Run the ordinary Lululemon build from the normal supplied-source company pipeline; record the command, exit, generated paths and measured Build Status in `RESULT.md`.
- Demonstrate that the ordinary build succeeds with Trainer generation unused and produces a reloadable BAV with intact formulas, Notes, semantic identities, source values and provenance.
- Explicitly derive and verify the Trainer from the same model, including Check coverage, source preservation and absence of active answers/hints.
- Run focused build, current-snapshot, workbook, semantic-map and Check regressions, plus affected geographic/KPI and Fast Retailing checks.
- Preserve the 50 protected artifacts and eight source extracts under their existing authenticated baselines. New current-build outputs do not authorize replacing protected benchmarks.
- Use existing Excel recalculation acceptance practice where affected formulas, references or workbook behavior require it; distinguish actual recalculation from formula inspection and retained evidence.
- Record remaining defects or unavailable verification precisely. This step does not certify KPI production acceptance or the Session Endpoint.

## Retained boundaries and remaining scope

- Cursor must not edit `TARGET.md`, `SESSION.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Preserve accepted accounting, normalization, admission and documentary safeguards, including fail-closed evidence rules and `SEGMENT_BRIDGE_TOLERANCE = 0.0`. Do not activate provisional normalization judgments.
- Earlier unfinished normalization, source-workflow, normalized-per-share and real-company acceptance commitments remain deferred, not completed; their evidence and unresolved decisions remain in the historical ledger.
- Next priority is real Lululemon Comparable Sales, SPSF and Revenue per Store production acceptance as specified in SESSION.md. Do not reopen accepted mechanics without a demonstrated defect.
- No forecasting, valuation, scenarios, forward assumptions or investment conclusions; no unrelated infrastructure, abstraction or cosmetic expansion.
