# Step 7.3.1 — Finish publication reference handling, reproducibility and Word inspection

AUTOCYCLE_PLAN: {"finding_key": "Reproducible Word/PDF publication from canonical research", "kind": "work", "minor": 1, "objective": "Finish publication reference handling, reproducibility and Word inspection", "plan_id": "d153697303254940b7a1e91f5e0bddda", "step_id": "7.3.1", "work_id": "7c1d2cba71024c21afc8becfcb40f6f2"}

## Completion

`python -m bav publish Lululemon` reproducibly generates readable, STYLE-compliant Word and PDF publications from canonical Drivers Markdown and referenced figures, preserving accepted historical analysis, failing clearly on invalid inputs or conversion failures, with successful end-to-end and visual verification.

## Implementation

- Repair the existing publication pipeline in `core/research/document.py` and its focused regressions; retain the current canonical company-name interface and toolchain.
- Validate document Link targets before flattening inline content. Resolve local document paths relative to canonical research and validate referenced anchors where applicable. Preserve meaningful reference information in both publications; broken or unsupported targets must produce actionable nonzero diagnostics identifying the source and target.
- Move required publication-library loading behind effective dependency diagnostics, including import-time constants and classes. Missing `python-docx` or `reportlab` must reach the CLI error handler with installation guidance.
- Correct repeat-publication verification by capturing immutable first-run bytes or payloads before the second publication overwrites destinations. Compare independently captured Word content, tables, sections and media, and PDF text, images and pagination. Identify actual metadata differences without normalizing away analytical or layout changes.
- Complete reading-scale inspection of every generated Word page using Microsoft Word rendering, including all landscape tables, three figures, equations, captions, source notes and page transitions. Retain retrievable evidence tied to the inspected DOCX. First-page Quick Look and archive inspection are insufficient.
- Repair demonstrated publication layout defects without dropping content or shrinking below STYLE body size. Reinspect affected Word and PDF output after changes.
- Preserve staging and validation of both formats before replacement; reference, dependency and conversion failures must preserve the last successful publication pair and canonical inputs.
- Update README only where repaired dependency or publication behavior requires it; keep STYLE.md authoritative.

## Verification

- Add valid and broken document-reference regressions, including missing local files and invalid anchors, alongside existing figure coverage.
- Exercise each missing Python dependency from a fresh import context through the public CLI; verify an actionable nonzero diagnostic and preservation of existing publications.
- Ensure the corrected repeat comparison detects a deliberate content or structural difference, then verify independent equivalent outputs from two real publications of unchanged canonical inputs.
- Run normal Lululemon build, check and publish with the real toolchain. Verify publish leaves canonical Markdown, figures, workbook, upstream evidence and zero-byte placeholders unchanged and requires no Trainer.
- Run focused publication and affected CLI, research, build-contract and optional Trainer regressions; verify Fast Retailing build/check remains usable and publish still diagnoses absent canonical research.
- Verify both final formats visually at reading scale. Carry earlier PDF evidence forward only where it applies to unchanged output; complete all missing Word coverage.
- Append commands, toolchain versions, independent comparison results, output hashes, inspected page coverage, viewing conditions and retrievable visual evidence to RESULT.md. Unavailable Word rendering access remains an explicit blocker to Completion; do not substitute structural checks or claim Excel recovery.

## Preservation and remaining scope

- Preserve canonical lowercase paths and output-only publication, accepted historical Drivers analysis, headings, tables, equations, captions, source notes, disclosure locators, fiscal labels, signed pp/bps bridges, residuals, seven-part assessments and evidence limits.
- Preserve STYLE typography, regular weights, spacing and grayscale; resolve installed Aptos and DengXian without silent substitution or distributing fonts. Keep publication BAV-first and exclude debug material without removing analytical evidence.
- Keep Forecast, Valuation and Overview zero-byte and omit empty publication sections. Do not recalculate analysis or regenerate workbooks through publish; do not invent research or use legacy fallback.
- Preserve `StandardizedFinancials`, protected fixtures/extracts, provenance, conflict history, accounting/normalization controls, atomic build behavior, semantic mappings, non-disclosing Check and `SEGMENT_BRIDGE_TOLERANCE = 0.0`.
- Preserve 24 Comparable Sales facts, three SPSF levels, five Revenue per Store periods, 39 pair assessments and five supported SPSF comparisons; retain admission/comparison independence, fiscal distinctions, missing/zero behavior and audit-only disagreements.
- Preserve `.git/autocycle/excel-verification-vm1b3wsq/saved-copy.xlsx`, `.git/autocycle/excel-verification-hrj5h672/saved-copy.xlsx`, their verification evidence and accepted human screenshots. Do not replay accepted migration or historical-analysis work.
- Carry native acceptance forward only for unchanged verified surfaces. Changed workbook formulas/dependencies require native recalculation and independent saved-cache verification; changed presentation requires readable native inspection.
- Preserve stable-copy protection, locking, timeouts, native-attempt accounting and the at-most-two-authorized-attempt limit without resetting allowances. Require diagnosed correction before a second attempt; never force-quit Excel, close unrelated workbooks, overwrite open copies or automate security approval.
- Broader BAV-first CLI/documentation alignment, the concise workbook front page and final Session integration remain subsequent obligations. Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.
- Exclude forecasting, valuation, scenarios, deal recommendations, buyer-specific analysis, Fast Retailing strategy, PowerPoint and unrelated refactoring.
- Preserve authenticated baseline, ownership, recovery, protected-document and unrelated-dirty-work safeguards. Cursor must not modify TARGET.md, SESSION.md or IMPLEMENTATION.md. Append evidence without rewriting historical RESULT records or reserving future IDs.
