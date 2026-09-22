# Step 7.3.2 — Detect publication formatting and layout changes

AUTOCYCLE_PLAN: {"finding_key": "Reproducible Word/PDF publication from canonical research", "kind": "work", "minor": 2, "objective": "Detect publication formatting and layout changes", "plan_id": "a5064d910eb24c66bfb612fc16fbb185", "step_id": "7.3.2", "work_id": "7c1d2cba71024c21afc8becfcb40f6f2"}

## Completion

`python -m bav publish Lululemon` reproducibly generates readable, STYLE-compliant Word and PDF publications from canonical Drivers Markdown and referenced figures, preserving accepted historical analysis, failing clearly on invalid inputs or conversion failures, with successful end-to-end and visual verification.

## Implementation

- Repair `_word_payload`, `_pdf_payload`, `_content_equal` and associated diagnostics in `core/tests/test_publication.py`. Keep this continuation bounded to publication comparison and demonstrated failures preventing Completion.
- Compare the complete DOCX ZIP-member inventory and payloads, retaining document XML, styles, settings, relationships, headers, footers, numbering, table geometry, section properties and media. Ignore ZIP packaging timestamps; normalize only individually identified volatile metadata fields supported by measured differences. Do not discard whole metadata parts or formatting properties.
- Compare PDF content and layout, including page geometry, positioned text and typography, image placement and drawing geometry. Include deterministic all-page render comparison with fixed renderer, resolution and color settings so positioning and visible formatting changes cannot pass through text-only equality.
- Report differing Word members and PDF pages or layout features. Identify actual metadata differences explicitly; do not attribute unexplained byte differences to timestamps.
- Preserve immutable first-publication bytes before the second run overwrites output paths. Use the same repaired comparison functions for mutation regressions, real repeat-publication verification and visual-evidence applicability.
- Retain the existing publisher, canonical company-name interface, validated references, dependency diagnostics, installed-font resolution and staged publication-pair replacement. Change production rendering only if verification demonstrates a defect directly preventing Completion.

## Verification and evidence

- Demonstrate rejection through the actual comparison entry point of independent Word mutations: title changed to 30 pt, paragraph spacing, style typography, table column/cell geometry and section margins. Keep analytical text unchanged in these cases.
- Demonstrate rejection of independent PDF changes to text position, font size, image position and table-rule geometry while preserving extracted text, image content and page count where applicable.
- Retain deliberate analytical-content rejection. Add positive controls showing that specifically allowed volatile metadata or ZIP timestamp differences remain equivalent.
- Run two real `python -m bav publish Lululemon` publications from unchanged canonical inputs. Capture both output pairs independently, record their hashes, and require the repaired comparisons to pass for both formats.
- Verify publish leaves canonical Markdown, figures, workbook, upstream evidence and zero-byte placeholders unchanged and requires no Trainer.
- Run focused publication regressions, retaining reference, missing-dependency, conversion-failure and prior-output-preservation coverage. Run affected CLI, research, build-contract and optional Trainer regressions as warranted by changes.
- Carry forward completed Lululemon and Fast Retailing build/check evidence only after establishing applicability to unchanged code and inputs; rerun affected checks if those surfaces change. Preserve Fast Retailing's actionable absent-research diagnostic.
- Retain `.git/autocycle/step-7-3-1-word-inspect/manifest.json`, inspected DOCX, native Word-rendered PDF and all 15 Word/19 publication-PDF page images. Establish equivalence between inspected artifacts and final publications using the repaired comparisons.
- Reuse visual evidence only for unchanged verified surfaces. If rendering changes, inspect affected output and pagination at reading scale, completing coverage of every final page; Word inspection requires Microsoft Word rendering. Record unavailable required access as a blocker.
- Append commands, versions, mutation outcomes, repeat-comparison results, precise normalization rules, output hashes and visual-evidence applicability to RESULT.md. Correct the earlier layout-equivalence claim by appending measured findings; preserve historical records.

## Preservation and remaining scope

- Preserve canonical lowercase paths, output-only publication and accepted historical Drivers analysis, including tables, equations, captions, source notes, disclosure locators, fiscal labels, signed pp/bps bridges, residuals, seven-part assessments and evidence limits.
- Preserve STYLE typography, regular weights, spacing and grayscale; use installed Aptos and DengXian without silent substitution or distributing fonts. Keep publications BAV-first and free of debug material.
- Keep Forecast, Valuation and Overview zero-byte and omit empty publication sections. Do not recalculate analysis, regenerate workbooks through publish, invent research or use legacy fallback.
- Preserve `StandardizedFinancials`, protected fixtures/extracts, provenance, conflict history, accounting/normalization controls, atomic build behavior, semantic mappings, non-disclosing Check and `SEGMENT_BRIDGE_TOLERANCE = 0.0`.
- Preserve 24 Comparable Sales facts, three SPSF levels, five Revenue per Store periods, 39 pair assessments and five supported SPSF comparisons, including admission/comparison independence, fiscal distinctions, missing/zero behavior and audit-only disagreements.
- Preserve `.git/autocycle/excel-verification-vm1b3wsq/saved-copy.xlsx`, `.git/autocycle/excel-verification-hrj5h672/saved-copy.xlsx`, associated evidence and accepted human screenshots. No Excel recovery is authorized or established by this work.
- Carry native acceptance forward only for unchanged verified surfaces. Changed workbook formulas/dependencies require native recalculation and independent saved-cache verification; changed presentation requires readable native inspection. Preserve stable-copy protection, locking, timeouts, attempt accounting and the at-most-two-authorized-attempt limit; require diagnosed correction before a second attempt. Never force-quit Excel, close unrelated workbooks, overwrite open copies or automate security approval.
- Broader BAV-first CLI/documentation alignment, the concise workbook front page and final Session integration remain subsequent obligations. Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.
- Exclude forecasting, valuation, scenarios, deal recommendations, buyer-specific analysis, Fast Retailing strategy, PowerPoint and unrelated refactoring.
- Preserve authenticated Git baseline, ownership, recovery, protected-document and unrelated-dirty-work safeguards. Cursor must not modify TARGET.md, SESSION.md or IMPLEMENTATION.md. Do not rewrite historical RESULT records or reserve future IDs.
