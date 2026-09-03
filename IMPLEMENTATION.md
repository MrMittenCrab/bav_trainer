# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.
- Cursor must update `RESULT.md` before handoff so the exact test commands/results are visible in the committed checkpoint.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

Commit `dbcaf27` (`chat balancesheet 3`) substantially implements Step 3. The annual build now uses the BAVGEM eight-category balance-sheet contract, shared Python/Excel reformulation, explicit asset/liability/equity reconciliation gaps, a live Condensed Financials CHECK, build-time source checksum blocking, and corrected synthetic demo data. `RESULT.md` reports 48 passing core tests plus a successful demo Trainer / Answer Key build.

The next blocker is narrower but important for real-company use: **statement rows still do not have a stable concept-aware identity end-to-end**.

### Review findings from commit `dbcaf27`

1. **Cross-document reconciliation is still label-keyed.** `core/ingestion/reconciler.py::_merge_line_items()` builds `by_label = {i.label: i ...}`. Two economically different lines with the same displayed label are therefore collapsed. BAVGEM Stage 2 explicitly identifies this as a real failure mode: the same label can legitimately occur on both sides of the balance sheet and must be keyed by `(concept, label)` when concepts are available.
2. **`LineItem.concept` exists but is underused after ingestion.** The canonical line resolver uses it for a handful of major concepts, but classification and merge identity still mostly operate on label text. The project therefore has the information needed to disambiguate many rows but does not consistently use it.
3. **Classification overrides are label-only.** `reformulate_balance_sheet()` normalizes `classificationOverrides` into a `label -> category` map. If two detail rows share a label, one override necessarily applies to both even when their concepts differ.
4. **Concept can determine asset/liability side when the label cannot.** A common example is two rows both displayed as `Deferred income taxes`, one with an asset concept and one with a liability concept. The current classifier sees the same label twice and can classify both the same way because it does not use concept metadata as a higher-priority signal.
5. **Duplicate labels also collide in the build row map.** `ReferenceModelBuilder._fill_statement()` writes source rows under `sheet!normalized_label`; the later duplicate overwrites the earlier one in `rowmap.json`, even though the physical workbook still contains both rows.
6. **Unconcepted duplicate labels are inherently unsafe.** When an Excel/manual source supplies two same-label rows without concept metadata, silently picking or merging one is worse than failing. The build should demand disambiguation instead of guessing.
7. **This is the last Stage-2 identity issue worth fixing before expanding the training surface.** The current `COMPONENT_CATALOG` still contains only 13 representative exercises. Expanding it now would multiply semantic mappings on top of an input identity contract that can still collapse real rows.

## BAVGEM integration decision for this step

Continue **selective integration** of the parent BAVGEM Stage-2 contract.

Reuse now:

- `(concept, label)` line identity where concept metadata exists;
- preserve duplicate displayed labels when they are distinct concepts;
- fail loudly on unresolved same-label ambiguity;
- keep newest-source-wins/restatement handling only within the same stable line identity.

Do not add SEC/edgartools sourcing, coverage-vault orchestration, quarterly extraction, or the Stage-4 analytics feature chain in this step.

---

## Active implementation step

### Step 4 — Make statement identity concept-aware before expanding trainer exercises

**Goal**

Preserve distinct financial statement rows across ingestion, reconciliation, source-row mapping, and balance-sheet classification by giving every `LineItem` a deterministic stable identity. Use explicit concepts when available, retain safe backwards compatibility for unique label-only inputs, and reject ambiguous duplicate label-only rows rather than silently merging or classifying them together.

Do **not** expand `COMPONENT_CATALOG` in this step. The next product step after this one can expand the learner practice surface.

## Required changes

### 1. Create one canonical statement-line identity helper

Create `core/data/line_identity.py` (or an equivalently focused module under `core/data/`).

Provide a small immutable identity type or tuple-based helper equivalent to:

```python
@dataclass(frozen=True)
class LineIdentity:
    concept: str
    label: str


def line_identity(item: LineItem) -> LineIdentity:
    ...
```

Rules:

- normalize whitespace / NBSP and case consistently with existing schema helpers;
- preserve the original `LineItem.label` for display; normalization is only for identity comparison;
- when `LineItem.concept` is non-empty, identity is `(normalized concept, normalized label)`;
- when concept is empty, identity is `("", normalized label)`;
- do not infer a fake concept from label text inside this helper;
- expose a readable string form for logs / rowmap keys, for example `concept=<...>|label=<...>`.

Add an explicit `AmbiguousStatementIdentityError` for cases where a statement contains multiple same-normalized-label rows without enough concept information to distinguish them safely.

### 2. Validate statement identities before model construction

Add a helper equivalent to:

```python
def validate_statement_identities(items: list[LineItem], statement_name: str) -> None:
    ...
```

Required behavior:

- two rows with different non-empty concepts and the same displayed label are valid and remain distinct;
- two rows with the same normalized concept + same normalized label are duplicate identities and must fail unless they are being reconciled as versions of the same row from different documents;
- two rows with the same normalized label and **both lacking concept metadata** must fail as ambiguous;
- one concepted row plus one conceptless same-label row must fail as ambiguous rather than guessing they are the same;
- error messages identify statement + label + concepts involved.

Run this validation on the final `StandardizedFinancials` consumed by `build_training_workbook()` before reconciliation/model construction.

Do not forbid ordinary unique label-only inputs; the existing demo and simple manual Excel flow must remain supported.

### 3. Make cross-document reconciliation identity-aware

Refactor `core/ingestion/reconciler.py::_merge_line_items()` so it no longer merges by raw label.

Required semantics:

- merge overlapping periods only when `line_identity(existing) == line_identity(incoming)`;
- preserve two rows that share a display label but have different concepts;
- keep the existing conflict/restatement logging behavior for true same-identity overlaps;
- conflict records must include both `label` and `concept` so later review can distinguish rows;
- normalize labels/concepts through the shared identity helper rather than inventing a second normalization rule;
- after merging each statement, validate the resulting identities.

Do not change newest-source-wins policy beyond fixing row identity.

### 4. Preserve concept metadata through supported ingestion paths

#### Structured JSON

`HKManualDocumentAdapter` already reads `row.get("concept", "")`; retain and test that behavior.

#### Excel exports

Extend `ExcelExportAdapter` only enough to support an **optional concept column** without breaking the existing simple format.

Support both shapes:

```text
Line Item | 2024-12-31 | 2025-12-31 | ...
```

and

```text
Concept | Line Item | 2024-12-31 | 2025-12-31 | ...
```

Accept case-insensitive header aliases `Concept` and `Line Item` / `Label`. If no Concept column exists, preserve current behavior with `concept=""`.

Do not redesign the Excel ingestion format beyond this compatibility addition.

### 5. Make classification use concept as a high-priority disambiguation signal

Update `core/model/classification.py` so `classify_balance_sheet_line()` considers normalized `item.concept` before ambiguous label-only rules where the concept clearly communicates asset/liability/equity nature.

Keep this deliberately narrow. At minimum support concept signals for:

- deferred-tax asset vs deferred-tax liability;
- lease / ROU asset vs lease liability where the concept clearly indicates side;
- debt / borrowing liability concepts;
- cash / marketable-security asset concepts;
- equity component concepts.

Do not create a general XBRL ontology. Concept metadata should resolve side/category only when it is clear; otherwise continue to the existing safe label rules or raise `UnclassifiedBalanceSheetLineError`.

A concept must never cause a line labelled as a subtotal (`Total Assets`, etc.) to enter the detail classification table.

### 6. Make classification overrides target stable identities

Replace the current implicit label-only lookup with an explicit selector parser while preserving backwards compatibility for unique labels.

Support these override keys:

```json
{
  "classificationOverrides": {
    "label:Operating lease liabilities": "Financial Liability",
    "concept:DeferredIncomeTaxAssetsNet": "Operating Long-Term Asset",
    "concept:DeferredIncomeTaxLiabilitiesNet": "Operating Long-Term Liability"
  }
}
```

Rules:

- `concept:<value>` matches exact normalized `LineItem.concept`;
- `label:<value>` matches exact normalized label only when that label is unique in the detail statement;
- legacy bare-label keys remain accepted only when the normalized label is unique;
- if a label selector matches multiple rows, raise a clear ambiguity error instructing the user to use `concept:` selectors;
- if a concept selector matches multiple rows, fail rather than applying it indiscriminately;
- invalid categories still raise `InvalidClassificationOverrideError`;
- the same resolved override decisions drive Python expected values and workbook defaults.

Do not put workbook coordinates into overrides.

### 7. Make source row maps preserve duplicate display labels

Update `ReferenceModelBuilder._fill_statement()` so source-row metadata no longer uses only `sheet!normalized_label` as its key.

Use the canonical stable identity string, e.g.:

```text
Balance Sheet!concept=DeferredIncomeTaxAssetsNet|label=Deferred income taxes
Balance Sheet!concept=DeferredIncomeTaxLiabilitiesNet|label=Deferred income taxes
```

For unique conceptless rows, use the same identity format with an empty concept.

The actual worksheet layout remains unchanged: duplicate labels may appear in column A exactly as supplied.

Do not change semantic component keys (`condensed.nopat.latest_fy`, etc.); this step only fixes source-line identity metadata.

### 8. Strengthen tests with the exact BAVGEM duplicate-label failure mode

Create `core/tests/test_line_identity.py` and extend classification / ingestion tests as needed.

Add focused tests for all of these cases:

1. **Distinct concepts, same label survive merge.** Two Balance Sheet rows both named `Deferred income taxes`, one concept `DeferredIncomeTaxAssetsNet`, one `DeferredIncomeTaxLiabilitiesNet`, remain two rows after reconciliation.
2. **Correct classification by concept.** The asset concept classifies to an asset category and the liability concept to a liability category even though labels are identical.
3. **Concept-specific overrides.** `concept:` selectors can override those two rows independently.
4. **Ambiguous label override rejected.** `label:Deferred income taxes` must fail when both rows exist.
5. **Legacy unique-label override still works.** Existing assumptions such as bare `Goodwill` remain accepted when unique.
6. **Unconcepted duplicate labels fail.** Two same-label rows with no concepts cause `AmbiguousStatementIdentityError` before the model is built.
7. **Concepted + conceptless duplicate label fails.** Do not silently merge them.
8. **Same identity across documents still merges/restates.** A newer document with the same concept+label updates overlapping periods and records conflicts under that identity.
9. **Rowmap preserves both duplicate labels.** A generated Answer Key / `rowmap.json` contains distinct source-row entries for both concept-qualified identities.
10. **Optional Excel Concept column.** A small temporary workbook using `Concept | Line Item | dates` ingests concepts correctly; the old `Line Item | dates` shape still works.

Use synthetic in-memory `LineItem` / temporary workbook fixtures. Do not add a large permanent company fixture merely to test duplicate labels.

### 9. Preserve all Step 3 accounting integrity behavior

Do not regress:

- eight BAVGEM balance-sheet categories;
- explicit ambiguity notes rather than fake categories;
- source checksum blocking;
- asset-detail / liability-detail / implied-equity reconciliation;
- live Condensed Financials CHECK;
- classification SUMIF reactivity;
- DuPont using implied reformulated equity;
- shared line resolver for revenue / NI / tax / interest / totals;
- ten-year Bear/Base/Bull residual-income chain;
- paired Trainer / Answer Key output and styling;
- existing 13 semantic components.

### 10. Update docs and handoff narrowly

Update `skills/bav-trainer/SKILL.md` only as needed to state that real-company standardized rows use concept-aware identity when available and duplicate label-only rows must be disambiguated.

Before handoff, overwrite `RESULT.md` with Step 4 status and exact commands/results.

## Files expected to change

- Create: `core/data/line_identity.py`
- Modify: `core/ingestion/reconciler.py`
- Modify: `core/ingestion/excel_import.py`
- Modify: `core/trainer/workbook.py` or one focused build-readiness helper
- Modify: `core/model/classification.py`
- Modify: `core/engine/reference_model.py`
- Create: `core/tests/test_line_identity.py`
- Modify: `core/tests/test_classification.py`
- Modify: ingestion/reference-integrity tests only where needed
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`

Only modify `core/data/interface.py` if a small helper/property is clearly cleaner than keeping identity logic in `line_identity.py`. Do not add new fields solely to satisfy this step; `LineItem.concept` already exists.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership or order.
- Trainer / Answer Key product contract.
- forecast / residual-income mathematics.
- Hint / Reveal behavior.
- automatic HKEX/SEC ingestion.
- BAVGEM quarterly / Core Earnings / Earnings Quality / Price Rationalization / ICC / DCF feature chain.
- Git history. Cursor must not commit, push, reset, rebase, merge, or delete branches.

## Acceptance criteria

- Distinct same-label statement rows with different concepts survive ingestion/reconciliation and remain separately addressable.
- Same-identity rows across documents still merge with existing restatement/conflict semantics.
- Duplicate same-label rows without sufficient concept metadata fail clearly rather than being silently merged.
- Balance-sheet classification can use concept metadata to distinguish asset vs liability rows whose displayed labels are identical.
- Classification overrides can target duplicate-label rows independently with `concept:` selectors; ambiguous label selectors fail.
- Existing unique bare-label overrides remain backwards compatible.
- Source row metadata preserves both concept-qualified duplicate rows.
- Both supported Excel shapes (with and without a Concept column) ingest successfully.
- Step 3 source/reformulation integrity checks remain enforced.
- Existing demo still builds the matched 13-component Trainer / Answer Key pair.
- No coordinate registry, duplicate line-identity algorithm, or runtime markdown dependency is introduced.

## Testing

Use red/green TDD. The first failing regression should demonstrate that the current label-keyed reconciler collapses two `Deferred income taxes` rows with distinct concepts.

Run at minimum:

```bash
pytest core/tests/test_line_identity.py -v
pytest core/tests/test_classification.py -v
pytest core/tests/test_reference_integrity.py -v
pytest core/tests/test_line_resolver.py -v
pytest core/tests/test_trainer.py -v
pytest core/tests/ -q
python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
```

Also run the focused Excel-import test module/node that covers both supported header shapes.

Do not weaken existing tests to make them pass. Do not count two physical rows as preserved merely because both labels can be reconstructed from separate fixtures; inspect the merged `StandardizedFinancials` and generated source sheet directly.

## RESULT.md handoff format

Before completion, write:

```text
Status: Step 4 complete | blocked
Files changed:
- ...
Tests run:
- <exact command> -> <exact result>
...
Identity checks:
- duplicate concept-qualified label preservation: ...
- ambiguous conceptless duplicate rejection: ...
- concept-specific override: ...
Unresolved: ...
```

## Cursor execution rules

1. Read this active step before editing.
2. Inspect current ingestion/reconciliation/classification code before changing it.
3. Write the duplicate-label merge regression test first and verify it fails for the intended reason.
4. Implement one canonical identity helper and route all new identity comparisons through it.
5. Do not solve ambiguity by adding more fuzzy label matching.
6. Preserve Step 3 accounting/reformulation behavior.
7. Run focused tests after each coherent change, then the full suite.
8. Update `RESULT.md` with exact evidence.
9. Report files changed, tests run, and unresolved issues.
10. Do not propose the next product step.
11. Do not commit or push; the user owns the checkpoint commit.

## ChatGPT verification protocol

After the user pushes the next checkpoint, ChatGPT should verify:

- the latest commit against every Step 4 acceptance criterion;
- that same-label/different-concept rows truly remain distinct through merge and workbook output;
- that conceptless ambiguity fails rather than being silently resolved;
- that classification and overrides use the same canonical identity rules;
- that Step 3 reconciliation and paired-workbook behavior did not regress;
- the exact test evidence recorded in `RESULT.md`.

If verified, the next planned product step should be **expanding the semantic practice surface beyond the current 13 representative components**, rather than adding more ingestion architecture unless the real-company identity tests expose another concrete blocker.
