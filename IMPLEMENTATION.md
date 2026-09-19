# Step 3.1.1 — Make the professional BAV workbook the default build product

AUTOCYCLE_PLAN: {"finding_key": "Make the professional BAV workbook the default build product", "kind": "work", "minor": 1, "objective": "Make the professional BAV workbook the default build product", "plan_id": "edcdd462269247a9a8d852e33a9086d0", "step_id": "3.1.1", "work_id": "381ee7bd9415433291c296292be312a6"}

## Completion

The ordinary source-bound command `python -m bav build Lululemon` produces and verifies a professionally presented `Lululemon_BAV.xlsx` without generating or requiring a Trainer, while the same completed model can still produce a working `Lululemon_BAV_Trainer.xlsx`.

## Bounded continuation — Remove practice framing and preserve primary metadata

- Remove remaining exercise-oriented wording from BAV schedules and analytical Notes, including `Per Share Analysis!A2` and other “not practiced” instructions. Preserve substantive explanations of source facts, unavailable comparisons, period alignment and analytical limitations.
- Inspect the entire visible BAV presentation, including optional schedules exercised by relevant fixtures. Keep Trainer, Answer Key, exercise, practice and learner-Check instructions confined to the Trainer; preserve legitimate analytical reconciliation language.
- Repair cleanup in `core/trainer/workbook.py` so `build_training_workbook(..., Company_BAV.xlsx)` preserves the generated BAV component-map and assumptions sidecars. Cleanup must target only secondary Trainer artifacts and never the resolved primary BAV.
- Preserve supported output naming and the existing paired interface, including its `(trainer_path, bav_path)` return contract. Retain removal of stale answer-bearing Trainer sidecars.
- Preserve independent BAV finalization, ordinary BAV-only routing and optional Trainer derivation. Deriving a Trainer must leave the BAV workbook and its primary sidecars unchanged.
- Apply generic repairs in directly affected code and documentation; do not redesign working build or analytical subsystems.

## Verification

- Add regressions for professional wording across visible BAV schedules and Notes, including Per Share Analysis and affected optional schedules.
- Exercise paired builds with the documented `_BAV.xlsx` output and existing supported Trainer/default output forms. Reload both products and confirm primary component-map and assumptions sidecars survive, match the BAV, and remain usable; Trainer-only answer-bearing sidecars must be absent.
- Run `python -m bav build Lululemon` through the normal supplied-source pipeline. Verify it succeeds without invoking Trainer generation and publishes a reloadable professional BAV with intact formulas, Notes, semantic identities, source facts, provenance and no yellow fills.
- Explicitly derive the matching Trainer from that BAV. Verify primary workbook and sidecar hashes remain unchanged, active practices are blank yellow without comments or answer leakage, source facts remain populated, and workbook-wide Check resolves the matching BAV.
- Run focused workbook, presentation, build, current-snapshot, semantic-map and Check regressions, plus affected geographic/KPI and Fast Retailing checks.
- Preserve atomic publication, protected-path checks and invalid-source rejection. Verify the 50 protected artifacts and eight source extracts against their existing authenticated baselines; do not replace protected benchmarks with current outputs.
- Apply existing Excel recalculation acceptance practice where affected formulas, references or workbook behavior require it. Record actual recalculation separately from formula inspection or retained evidence.
- Record commands, measured results, generated paths, Build Status and any unavailable verification in `RESULT.md`. Do not infer acceptance from prior counts or certify the Session Endpoint.

## Retained commitments and boundaries

- Preserve accepted accounting, ingestion, geographic, store-count, KPI, normalization, provenance and workbook behavior, including fail-closed admission, `SEGMENT_BRIDGE_TOLERANCE = 0.0`, and inactive provisional normalization judgments.
- Preserve the professional opening, complete analytical model, useful Notes, source-evidence limitations, Trainer sanitization and non-disclosing Check.
- TARGET and SESSION publication is already complete. Cursor must not modify `TARGET.md`, `SESSION.md` or `IMPLEMENTATION.md`.
- Real-source Comparable Sales/SPSF admission and historical Revenue per Store production acceptance remain the next priority before further normalization expansion. Retain their source-evidence, formula/Notes, Trainer, Check, export/reload and required Excel verification obligations.
- Disclosure-led historical driver testing and evidence-backed strategy interpretation remain subsequent Session work, with explicit distinctions between disclosures, facts, identities, relationships and inference.
- Earlier unfinished normalization, source-workflow, normalized-per-share and real-company acceptance commitments remain deferred, with evidence and unresolved decisions preserved in the historical ledger.
- No forecasting, valuation, scenarios, forward assumptions, investment conclusions or unrelated infrastructure and cosmetic expansion.
