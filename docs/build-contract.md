# Current Build and release contracts

`python -m bav build Company` and both company release builders use
`build_training_workbook → ReferenceModelBuilder → BUILD_MODULES` in
`core/engine/build_contract.py`. There is no discovery of Python files.

Release/explicit-input builds retain the `status="complete"`,
`workbook_capable=True`, `complete_analysis=True` selection gate. Company current
builds additionally select workbook-capable entries explicitly marked
`current_ready=True`, even if parent completion is incomplete. Deferred entries
remain excluded. `current_ready` declares that preparation emits independently
valid families; it does not admit source data or assert parent acceptance.

Eligible entries must have a preparation hook
returning concrete `ComponentSpec` objects and workbook writers that register
those objects in the semantic map. Missing integration is a build error.

The current registry includes all existing integrated workbook modules.
Geographic and Operating KPI adapters prepare families independently, using
existing metric-level admission and availability. Missing comparable-sales/SPSF
admission does not suppress valid store-count families. Forecast remains deferred.
Python code alone does not establish workbook readiness.

## Adding a completed module

Implement the module's calculation/spec preparation and workbook writer, then
add one `BuildModule` entry to `BUILD_MODULES`. Hooks may live with the module;
they do not require new dispatch in `ReferenceModelBuilder`, the CLI, or release
scripts. Existing modules retain their preparation methods and shared sheet
writers to avoid changing analytical formulas and workbook layouts.

The preparation hook receives `(builder, start_order)` and returns a tuple of
specs. The writer receives `(builder, workbook)`, reads the final specs from
`builder.module_specs[module_id]`, and registers their formulas and calculated
expected values in `builder.semantic_map`. Use the final specs, whose order is
assigned centrally after applicability filtering. Shared `WorkbookWriter`
objects execute once, in stable writer order, after all preparation completes.
New analytical families must also have their normal deterministic BAV
formulas/Notes and optional Trainer Check integration before being declared
complete; this contract does not replace the analytical evaluator.

Declare module dependencies in `depends_on` and register prerequisites first.
Missing, excluded, or later prerequisites are errors. Semantic component
dependencies are checked by the existing semantic-map validator. Registry
order determines component order; writer priority determines sheet creation
order. Source-unavailable filtering cannot leave overlapping component orders.

## Required input versus source unavailability

Use `RequiredInput(name, supplied)` for a required input class. The predicate
receives standardized financials and checks package presence, not whether a
desired metric or value exists. All eligible modules' requirements are checked
before module applicability or computation. Errors name the module and missing
input. For example, a completed Operating KPI workbook adapter requiring the
KPI package would register:

```python
required_inputs=(RequiredInput(
    "management-KPI (historical_operating_kpis)",
    lambda fin: fin.historical_operating_kpis is not None,
),)
```

Do not use an absent required package as an applicability predicate. Once the
package is supplied and validated, retain the analytical module's existing
company/metric applicability and `SOURCE_UNAVAILABLE` behavior. Registration
does not manufacture an empty source package or infer undisclosed values.

## Verification

Generic Build and release verification compare the actual ordered component
identities with the runtime contract, including IDs, semantic keys, family,
period, order, and dependencies. Equal counts alone cannot pass a substituted,
missing, or stale component set. Release blank/filled Check totals come from
the same expected specs. Historical benchmark assertions may still describe
fixed fixtures, but production completeness checks have no fixed total.

Company routing and staged reconciliation live in `core/current_build.py`.
The public `bav` package delegates to the compatible internal `core` CLI.
Company builds verify the professional `<Company>_BAV.xlsx` and sidecars before
atomically exchanging the canonical `build/output/<Company>/` directory. Trainer
generation is unused on the ordinary company path. Build Status uses emitted
semantic identities; visibility is not release acceptance. Build never writes
AutoCycle state, control documents, benchmark artifacts, or release artifacts,
and never starts AutoCycle.

Run focused checks with `python -m pytest core/tests/test_build_contract.py -q`
and regressions with `python -m pytest core/tests -q` in the project environment.
