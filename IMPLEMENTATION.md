# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a pushed checkpoint matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes implementation commits.
- ChatGPT verifies pushed implementation commits by code inspection. ChatGPT does not treat Cursor's reported tests as independently rerun evidence.
- Cursor must update `RESULT.md` before handoff so the exact commands/results are visible in the checkpoint.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

Cursor should treat `TARGET.md` and this file as read-only during implementation unless the active step explicitly requires documentation changes.

---

## Current architecture checkpoint

Commit `138b26d` (`chat identity 4`) implements most of Step 4 on branch `chatgpt/reference-model-integrity`.

The implementation now has:

- a canonical `LineIdentity` / `line_identity()` helper;
- concept-aware cross-document reconciliation;
- preservation of same-label rows with distinct concepts;
- build-time rejection of conceptless duplicate labels;
- optional Excel `Concept | Line Item | dates` ingestion;
- concept-aware balance-sheet classification;
- `concept:` / `label:` classification override selectors;
- concept-qualified source-row keys in `rowmap.json`;
- the existing paired Trainer / Answer Key output and 13 semantic components.

`RESULT.md` for `138b26d` reports 58 passing core tests and a successful demo Trainer / Answer Key build.

**Step 4 is not accepted yet.** ChatGPT review found three remaining defects in the implementation. Cursor should make a narrow correction pass against the existing Step 4 code. Do not rerun or redesign Step 4 from scratch.

## Review findings from commit `138b26d`

### Finding 1 — concept classification is too permissive

`core/model/classification.py::_classify_by_concept()` currently uses broad substring checks such as `debt`, `equity`, and `cash` as high-priority category signals.

That can override a correct label classification with the wrong accounting side. Examples:

- `DebtSecuritiesAvailableForSale` is an asset concept but contains `debt`;
- `EquityMethodInvestments` is an investment asset concept but contains `equity`;
- `CashFlowHedgeReserve` can represent an equity/OCI reserve but contains `cash`.

The Step 4 contract was intentionally narrower: concept metadata may override label logic only when the concept **clearly determines** asset/liability/equity nature. It must not become a fuzzy XBRL ontology.

### Finding 2 — duplicate identities can still be erased before validation

`core/ingestion/reconciler.py::_merge_line_items()` builds an identity-keyed dictionary before validating the individual source lists.

Therefore:

- two duplicate identities already present in `existing` can be collapsed by dictionary construction;
- two duplicate identities inside `incoming` can be treated as versions of the same row;
- validating only the merged result is too late because the duplicate may already have disappeared.

Same-identity rows from **different documents** should still reconcile/restatement-merge. Duplicate identities **within one source statement** must fail before the dictionary merge starts.

### Finding 3 — legacy label overrides lost case-insensitive compatibility

Before Step 4, bare-label overrides were normalized through `_norm()`, which made matching case-insensitive. The new selector path uses `normalize_label()` directly, which preserves case.

As a result, a legacy unique override such as:

```json
{
  "classificationOverrides": {
    "goodwill": "Operating Long-Term Asset"
  }
}
```

can silently fail to match a source row displayed as `Goodwill`.

Unique `label:` selectors and legacy bare-label selectors must remain case-insensitive while retaining the new ambiguity protections.

---

## Active implementation step

# Step 4 correction pass — close review findings before acceptance

**Goal:** Fix the three review defects above without changing the Step 4 architecture, expanding the trainer exercise surface, or modifying valuation/reformulation behavior unrelated to the defects.

**Architecture:** Keep the existing canonical line-identity, reconciliation, classification, and override structures. Tighten the concept classifier to an explicit safe set of signals, validate each source statement before identity-keyed merging, and restore case-insensitive unique-label override matching. Add regression tests first, then make the minimum implementation changes required for them to pass.

**Tech stack:** Python, pytest, openpyxl, existing BAV Trainer modules.

**Spec:** `TARGET.md` plus the accepted portions of Step 4 already present in commit `138b26d`.

## Global constraints

- Do not expand `COMPONENT_CATALOG`; it remains at the current 13 representative exercises.
- Do not redesign ingestion or add automatic HKEX/SEC/edgartools sourcing.
- Do not add BAVGEM quarterly, Core Earnings, Earnings Quality, Price Rationalization, ICC, or DCF feature chains.
- Preserve Step 3 accounting integrity and all already-correct Step 4 identity behavior.
- Do not weaken an existing test to make a regression pass.
- Do not add workbook coordinates to domain logic or overrides.
- Do not introduce a second line-identity algorithm.
- Do not commit or push. The user owns the implementation checkpoint commit.

---

## Task 1 — Make concept classification conservative

**Files:**

- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py` and/or `core/tests/test_line_identity.py`

### Required behavior

`_classify_by_concept()` should return a classification only when the concept itself gives a sufficiently clear accounting-side/category signal.

Retain narrow support for the Step 4 cases already required:

- deferred-tax asset vs deferred-tax liability;
- lease / ROU asset vs lease liability when side is explicit;
- unmistakable borrowing/debt **liability** concepts;
- unmistakable cash / marketable-security **asset** concepts;
- unmistakable equity-component concepts.

Do not use a generic token merely because it appears somewhere in the concept name. In particular, generic occurrences of `debt`, `equity`, or `cash` are insufficient by themselves.

When a concept is not safely decisive, `_classify_by_concept()` must return `None` so the existing label classifier gets the next opportunity. If the label rules also cannot classify safely, retain the existing `UnclassifiedBalanceSheetLineError` behavior.

Do not create a broad external-XBRL mapping table in this correction pass.

### Regression tests — write these first

Add tests equivalent in intent to:

```python
def test_debt_security_concept_does_not_become_financial_liability():
    item = LineItem(
        label="Marketable securities",
        concept="DebtSecuritiesAvailableForSale",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Financial Asset"


def test_equity_method_concept_does_not_become_equity():
    item = LineItem(
        label="Investment in associate",
        concept="EquityMethodInvestments",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Operating Long-Term Asset"


def test_cash_flow_hedge_reserve_concept_does_not_become_financial_asset():
    item = LineItem(
        label="Other comprehensive income reserve",
        concept="CashFlowHedgeReserve",
        values={P1: 10, P2: 12},
    )
    assert classify_balance_sheet_line(item).category == "Equity"
```

If the existing label classifier does not currently recognize one of those exact labels, use the closest existing safely classified label while preserving the misleading concept. The test must demonstrate that the concept no longer overrides a correct economic category merely because it contains a generic token.

Also retain positive tests showing that genuinely explicit concepts still work, including the deferred-tax asset/liability pair already covered by Step 4.

### Verification

Run the new focused tests and verify they fail on the current `138b26d` implementation for the intended reason before editing classification logic. Then implement the minimum safe change and rerun them.

---

## Task 2 — Validate each source statement before identity-keyed merge

**Files:**

- Modify: `core/ingestion/reconciler.py`
- Test: `core/tests/test_line_identity.py`

### Required behavior

Before `_merge_line_items()` constructs `by_id` or otherwise deduplicates by canonical identity:

1. validate the `existing` list as one source statement;
2. validate the `incoming` list as one source statement;
3. only then reconcile rows across the two sources by canonical identity;
4. validate the merged result afterward as a final invariant check.

The critical distinction is:

```text
same identity twice within one source statement
    -> AmbiguousStatementIdentityError

same identity once in old document + once in new document
    -> legitimate cross-document reconciliation/restatement path
```

If useful for clear error messages, extend `_merge_line_items()` with a focused optional statement-name/context argument. Do not introduce a second validation implementation.

### Regression tests — write these first

Add both cases:

```python
def test_duplicate_identity_inside_existing_fails_before_merge():
    existing = [
        _li("Deferred income taxes", 40, 45, "DeferredIncomeTaxAssetsNet"),
        _li("Deferred income taxes", 41, 46, "DeferredIncomeTaxAssetsNet"),
    ]
    incoming = []
    with pytest.raises(AmbiguousStatementIdentityError):
        _merge_line_items(existing, incoming, "source")


def test_duplicate_identity_inside_incoming_fails_before_merge():
    existing = []
    incoming = [
        _li("Deferred income taxes", 40, 45, "DeferredIncomeTaxAssetsNet"),
        _li("Deferred income taxes", 41, 46, "DeferredIncomeTaxAssetsNet"),
    ]
    with pytest.raises(AmbiguousStatementIdentityError):
        _merge_line_items(existing, incoming, "source")
```

Keep the existing regression proving that one matching identity in each of two different documents still merges/restates correctly and retains conflict logging.

### Verification

The two new duplicate-within-source tests must fail on the current implementation before the fix and pass afterward. Re-run the existing cross-document restatement test to prove the correction did not accidentally forbid legitimate merging.

---

## Task 3 — Restore case-insensitive legacy label overrides

**Files:**

- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py` and/or `core/tests/test_line_identity.py`

### Required behavior

For classification override selector resolution:

- `label:<value>` matching is case-insensitive and whitespace/NBSP normalized;
- legacy bare-label matching is case-insensitive and whitespace/NBSP normalized;
- both remain valid only when the normalized label is unique among detail rows;
- ambiguous duplicate-label matches still raise `AmbiguousClassificationOverrideError` and instruct the user to use `concept:` selectors;
- `concept:<value>` retains the Step 4 concept-specific behavior and ambiguity protection;
- invalid categories still raise `InvalidClassificationOverrideError`;
- zero-match behavior should remain consistent with the current implementation unless a test/spec already requires an error.

Use one shared normalization path for selector-label comparison. Do not reintroduce the old global `label -> category` map.

### Regression test — write this first

Add a case equivalent to:

```python
def test_legacy_unique_label_override_is_case_insensitive():
    item = _li("Goodwill", 10, 12)
    fin = _minimal_financials_with_balance_sheet([item])

    reform = reformulate_balance_sheet(
        fin,
        [P1, P2],
        overrides={"goodwill": "Operating Long-Term Asset"},
    )

    assert reform.decisions[0].category == "Operating Long-Term Asset"
    assert reform.decisions[0].overridden is True
```

Also add or retain an explicit `label:` version with different case, e.g. `label:GOODWILL`, if it can be done without duplicating test setup unnecessarily.

Re-run the existing ambiguous `label:Deferred income taxes` regression to prove case-insensitive matching does not weaken ambiguity detection.

---

## Task 4 — Run the Step 4 regression suite and update handoff evidence

**Files:**

- Modify: `RESULT.md`
- Modify `skills/bav-trainer/SKILL.md` only if the correction materially changes user-facing identity/override instructions. Do not edit it merely to record implementation details.

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

If the Excel Concept-column test is not included by one of those commands, also run the exact focused Excel-import test node/module that covers both supported shapes:

```text
Line Item | dates
Concept | Line Item | dates
```

Do not report Step 4 complete if any focused regression, existing Step 3 integrity test, full core suite, or demo build fails.

---

## Preserve all already-correct Step 4 behavior

The correction pass must not regress:

- canonical concept+label line identity;
- preservation of same-label rows with distinct non-empty concepts;
- rejection of concepted + conceptless same-label ambiguity;
- rejection of duplicate conceptless same-label rows;
- same-identity cross-document restatement/conflict handling;
- optional Excel Concept column plus legacy Excel shape;
- concept-specific classification overrides;
- ambiguous label-selector rejection;
- concept-qualified `rowmap.json` source-row keys;
- original worksheet display labels;
- paired Trainer / Answer Key generation;
- existing 13 semantic components.

## Preserve all Step 3 accounting integrity behavior

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
- paired Trainer / Answer Key styling.

---

## Expected files to change in this correction pass

Primary:

- `core/model/classification.py`
- `core/ingestion/reconciler.py`
- `core/tests/test_line_identity.py`
- `core/tests/test_classification.py` if that is the cleaner home for concept/override regressions
- `RESULT.md`

Only modify other files when a failing test demonstrates they are actually required. In particular, do not rewrite `core/data/line_identity.py`, `core/engine/reference_model.py`, `core/trainer/workbook.py`, or Excel ingestion merely because they were part of the original Step 4 implementation.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership or order.
- Trainer / Answer Key product contract.
- forecast / residual-income mathematics.
- Hint / Reveal behavior.
- automatic HKEX/SEC ingestion.
- BAVGEM quarterly / Core Earnings / Earnings Quality / Price Rationalization / ICC / DCF feature chain.
- Git history.

---

## Acceptance criteria for Step 4 correction pass

Step 4 is ready for ChatGPT re-review only when all of the following are true:

1. Misleading concept names such as debt-security assets, equity-method investments, and cash-flow-hedge reserves do not get misclassified merely because they contain `debt`, `equity`, or `cash`.
2. Explicit deferred-tax asset/liability concepts still classify correctly.
3. Duplicate canonical identities inside the `existing` source list fail before dictionary construction.
4. Duplicate canonical identities inside the `incoming` source list fail before dictionary construction.
5. A matching identity appearing once in each of two separate documents still follows the existing restatement/conflict path.
6. Legacy bare-label overrides are case-insensitive for unique labels.
7. Explicit `label:` overrides are case-insensitive for unique labels.
8. Ambiguous duplicate-label selectors still fail and require `concept:` selectors.
9. Concept-specific overrides still work independently on duplicate displayed labels.
10. All Step 3 accounting integrity behavior remains enforced.
11. Existing demo still builds the matched 13-component Trainer / Answer Key pair.
12. Full core test suite passes.

---

## RESULT.md handoff format

Before stopping, overwrite `RESULT.md` with evidence in this form:

```text
Status: Step 4 correction pass complete | blocked

Files changed:
- ...

Tests run:
- <exact command> -> <exact result>
...

Correction checks:
- conservative concept classification: <what was tested/result>
- duplicate identity inside existing source: <result>
- duplicate identity inside incoming source: <result>
- cross-document same-identity restatement: <result>
- case-insensitive bare-label override: <result>
- case-insensitive label: override: <result>
- ambiguous duplicate-label override rejection: <result>

Preserved checks:
- Step 3 accounting integrity: ...
- paired Trainer / Answer Key build: ...
- 13 semantic components: ...

Unresolved: none | <specific blocker>
```

Do not write `Status: Step 4 complete` unless every acceptance criterion above is satisfied.

---

## Cursor execution rules

1. Read this correction pass before editing.
2. Inspect the current `138b26d` implementations of `classification.py`, `reconciler.py`, and the relevant tests.
3. Do not redo already-working Step 4 architecture.
4. For each of the three findings, write the regression test first and run it to demonstrate the current failure.
5. Fix one finding at a time with the smallest coherent implementation change.
6. Run the focused test immediately after each fix.
7. After all three fixes, run the complete testing block above.
8. Update `RESULT.md` with exact commands/results and the correction checks.
9. Report files changed and unresolved issues.
10. Do not propose or begin Step 5.
11. Do not commit or push; the user owns the implementation checkpoint commit.

---

## ChatGPT verification protocol

After the user reviews, commits, and pushes Cursor's correction pass, ChatGPT should inspect the newest commit and verify:

- all three review findings are actually fixed in code rather than only covered by superficial tests;
- the concept classifier uses conservative, accounting-safe signals rather than a renamed broad substring heuristic;
- duplicate identities cannot disappear before per-source validation;
- case-insensitive label override compatibility is restored without weakening ambiguity detection;
- previously accepted Step 4 identity behavior is preserved;
- Step 3 accounting/reformulation behavior is unchanged;
- `RESULT.md` records the exact focused and full-suite evidence.

Only after that verification should Step 4 be considered accepted. The next planned product step can then expand the semantic practice surface beyond the current 13 representative components.
