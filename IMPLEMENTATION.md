# Step 7.3 — Reproducible Word/PDF publication from canonical research
AUTOCYCLE_PLAN: {"finding_key": "Reproducible Word/PDF publication from canonical research", "kind": "work", "objective": "Reproducible Word/PDF publication from canonical research", "plan_id": "03301885c75b4572881345d1d7500ec4", "step_id": "7.3", "work_id": "7c1d2cba71024c21afc8becfcb40f6f2"}

INPUT_STATUS: COMPLETE

## Completion

`python -m bav publish Lululemon` reproducibly generates readable, STYLE-compliant Word and PDF publications from canonical Drivers Markdown and referenced figures, preserving accepted historical analysis, failing clearly on invalid inputs or conversion failures, with successful end-to-end and visual verification.

## Implementation

- Add the company-name `publish` command through the existing public `bav` interface and company-path resolution. Write publications only under `build/output/<company>/`.
- Reuse `core/research` and existing artifact validation. Publication consumes canonical Markdown and figures without recalculating analysis, regenerating the workbook or requiring Trainer generation.
- Use a standard maintainable Markdown-to-document toolchain. Document required converters, fonts, installation and the CLI workflow in README; keep STYLE.md authoritative.
- Publish Drivers now. Forecast, Valuation and Overview remain zero-byte placeholders and contribute no empty report sections.
- Preserve headings, tables, equations, captions, source notes, disclosure locators, fiscal labels, historical bridges, signed pp/bps contributions, residuals, seven-part assessments and evidence limits.
- Apply STYLE typography, regular weights, spacing and grayscale presentation. Resolve installed Aptos and DengXian without silent substitution or distributing font files.
- Make wide historical and assessment tables readable through appropriate wrapping, pagination, repeated headers or landscape sections without dropping content or shrinking below established body size.
- Resolve figure and document references relative to canonical research. Missing Markdown, missing figures, broken references, unavailable required dependencies/fonts and conversion failures return actionable nonzero errors.
- Companies without publishable canonical research receive a clear diagnostic; do not invent research or fall back to legacy paths.
- Stage and validate both formats before replacing published outputs; failed conversion must preserve the last successful publication and canonical inputs.
- Use BAV-first wording in the new command, publication and publication documentation. Exclude internal debug material without removing analytical evidence or limitations.

## Verification

- Run normal Lululemon company-name build, check and publish with the real conversion toolchain.
- Repeat publication from unchanged canonical inputs; verify equivalent content, structure and figures, identifying any unavoidable container metadata differences.
- Verify that publishing does not mutate canonical Markdown, figures, workbook, upstream evidence or placeholders.
- Cover reference resolution, missing assets/dependencies, converter failure, preservation of prior publications and optional-Trainer independence with focused regressions.
- Visually inspect both Word and PDF at reading scale, including every wide table, all three figures, equations, captions, source notes and page transitions. Structural extraction alone does not establish readability.
- Record toolchain versions, commands, measured results, output paths, inspected pages, viewing conditions and retrievable visual evidence in RESULT.md. Unavailable rendering access or missing evidence remains explicit.
- Run affected CLI, research, build-contract and optional Trainer regressions; verify Fast Retailing build/check remains usable.

## Preservation and remaining scope

- Historical Drivers acceptance is closed by Review, including human-provided native Excel readability evidence. Preserve accepted analytical behavior and evidence; do not replay completed migration or historical-analysis work.
- Preserve `StandardizedFinancials`, canonical lowercase paths, protected fixtures/extracts, provenance, conflict history, accounting/normalization controls, atomic build behavior and `SEGMENT_BRIDGE_TOLERANCE = 0.0`.
- Preserve 24 Comparable Sales facts, three SPSF levels, five Revenue per Store periods, 39 pair assessments and five supported SPSF comparisons; retain admission/comparison independence, fiscal distinctions, missing/zero behavior and audit-only disagreements.
- Preserve both `.git/autocycle/excel-verification-vm1b3wsq/saved-copy.xlsx` and `.git/autocycle/excel-verification-hrj5h672/saved-copy.xlsx`, their verification evidence and the accepted human screenshots.
- Carry native acceptance forward only for unchanged verified surfaces. Changed workbook formulas/dependencies require native recalculation and independent saved-cache verification; changed presentation requires readable native inspection.
- Preserve stable-copy protection, locking, timeouts, native-attempt accounting and the at-most-two-authorized-attempt limit; do not reset allowances. Require diagnosed correction before a second attempt. Do not force-quit Excel, close unrelated workbooks, overwrite open copies or automate security approval.
- Broader BAV-first CLI/documentation alignment, the concise workbook front page and final Session integration remain subsequent obligations. Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.
- Exclude forecasting, valuation, scenarios, deal recommendations, buyer-specific analysis, Fast Retailing strategy, PowerPoint and unrelated refactoring. Preserve semantic mappings and non-disclosing Check.
- Preserve authenticated baseline, ownership, recovery, protected-document and unrelated-dirty-work safeguards. Cursor must not modify TARGET.md, SESSION.md or IMPLEMENTATION.md.
- Append completion evidence and unresolved obligations to RESULT.md without rewriting history or reserving future IDs.
