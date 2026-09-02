# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition**: a training system that takes manually supplied Hong Kong company financial materials, builds the full BAV model as a hidden reference answer, and gives the learner a professional Excel workbook in which they reconstruct the model themselves part by part.

The trainer is for learning the actual BAV modelling workflow, not for generating artificial exercises.

## Learner experience

1. Supply company financial data/documents manually.
2. Build a complete reference BAV model from those inputs.
3. Generate a training workbook with source data, structure, labels, and professional formatting already prepared, while substantive practice formulas are withheld.
4. Work through model components in dependency order.
5. Get a short feedback loop through **Check**, **Hint**, and **Reveal Answer**.
6. Preserve the ability to inspect and learn the real Excel formula when an answer is revealed.

## Hard requirements

- **Reference-model first.** The system must derive trainer answers from a complete model, not from hand-authored answer keys.
- **Answers remain hidden until requested.** The learner should be able to attempt each component before seeing the reference formula.
- **Short feedback loop.** Check, Hint, and Reveal must be available without manually comparing against a second workbook.
- **Semantic component mapping.** Trainer logic must resolve components by semantic identity at build time rather than depending on fragile hard-coded workbook coordinates.
- **Professional workbook preserved.** Training mode should remove only the substantive work the learner is meant to practise; non-essential formatting/setup work should already be done.
- **HK input is manual in v1.** Automatic HKEX scraping is not required for the first usable version. Manual filings or Excel/Bloomberg/Wind-style exports can feed a standardized interface.
- **Full BAV logic is the source of truth.** Accounting reformulation, DuPont analysis, forecasting, residual-income valuation, DCF/cross-check logic, and scenario analysis should remain aligned with the underlying BAV model rather than becoming a simplified toy model.

## Non-goals for v1

- Automatically inventing practice questions or exercises.
- Requiring the learner to reproduce decorative Excel formatting.
- Automatic HKEX ingestion when manual document input is sufficient.
- Giving the implementation agent freedom to redesign the product while implementing a bounded step.

## Definition of done

A real Hong Kong company can be supplied through the supported manual input path and the system can produce a usable trainer workbook backed by a hidden complete reference model. The learner can reconstruct the major BAV components in sequence and use Check, Hint, and Reveal reliably without the trainer depending on fixed cell coordinates or corrupting the workbook.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
