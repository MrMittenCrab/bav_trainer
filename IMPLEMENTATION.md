# Step 4 Final Identity Safety Implementation Plan

> **For Cursor:** Implement only the active correction step below. Use red/green TDD, run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Close the remaining Step 4 identity/classification defects found in commit `ccd7d10` before expanding the trainer practice surface.

**Architecture:** Keep the existing `LineIdentity`, reconciliation, classification, semantic-map, and paired-workbook architecture. Make displayed-label identity case-insensitive while keeping concept identifiers exact, and remove one remaining unsafe concept shortcut that can force redeemable preferred stock into Equity. Do not redesign ingestion or valuation logic.

**Tech Stack:** Python, pytest, openpyxl, existing BAV Trainer modules.

**Spec:** `TARGET.md` plus the accepted Step 3/Step 4 behavior already implemented on `chatgpt/reference-model-integrity`.

## Global constraints

- `TARGET.md` is read-only.
- Do not expand `COMPONENT_CATALOG`; it remains at 13 representative exercises.
- Do not add HKEX/SEC/edgartools automation.
- Do not add quarterly, Core Earnings, Earnings Quality, Price Rationalization, ICC, DCF, or other later BAVGEM feature chains.
- Preserve the Trainer / Answer Key product contract, styling, semantic mapping, Hint/Reveal behavior, and residual-income mathematics.
- Preserve original `LineItem.label` text for worksheet display. Canonicalization is for comparison/metadata identity only.
- Keep concept identifiers exact apart from the existing whitespace/NBSP normalization. Do **not** case-fold concept IDs in this pass.
- Do not weaken existing tests.
- Do not introduce a second statement-identity algorithm.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Current checkpoint

Latest implementation commit: `ccd7d10` (`chat identity corrected 4`).

The first Step 4 correction pass successfully addressed the previous review findings:

- source lists are validated before identity-keyed merge;
- broad `debt` / `equity` / `cash` concept matching was narrowed;
- legacy bare-label and `label:` overrides are case-insensitive;
- `RESULT.md` reports 64 passing core tests and a successful 13-component Trainer / Answer Key demo build.

Those fixes should be preserved. Step 4 is still not accepted because the latest review found two remaining defects.

## Review findings from `ccd7d10`

### Finding 1 — statement label identity is still case-sensitive

`core/data/line_identity.py::line_identity()` currently applies `normalize_label()` but does not case-fold the displayed label. `validate_statement_identities()` therefore also groups labels case-sensitively.

This creates an end-to-end inconsistency: classification override labels are now correctly case-insensitive, but statement identity is not.

Concrete failure modes:

```text
existing document:  concept=Goodwill | label=Goodwill
incoming document:  concept=Goodwill | label=GOODWILL
```

These represent the same statement line but currently receive different `LineIdentity` values, so cross-document reconciliation can preserve both rows instead of merging them.

Likewise, a single source containing two conceptless rows named `Goodwill` and `GOODWILL` can evade duplicate-label rejection and be double-counted.

The correct rule for this project is:

- displayed labels: whitespace/NBSP normalized **and case-insensitive** for identity;
- concept IDs: whitespace/NBSP normalized but otherwise exact/case-sensitive;
- original labels remain untouched for workbook display.

### Finding 2 — `preferredstock` is not an unmistakable Equity signal

The corrected `_classify_by_concept()` still treats any concept containing `preferredstock` as Equity before label classification runs.

That is unsafe because redeemable / mandatorily redeemable preferred stock may be liability-like and cannot be classified as Equity from the generic token alone. A self-describing concept such as `PreferredStockSubjectToMandatoryRedemption` can therefore override a label such as `Long-term debt` and force the wrong category.

For this bounded correction, generic `preferredstock` must not be a high-priority Equity trigger. If no other clearly decisive concept signal applies, return `None` and let the existing label classifier or an explicit classification override decide.

Do not turn this into a general XBRL ontology project.

---

### Task 1: Make canonical displayed-label identity case-insensitive

**Files:**
- Modify: `core/data/line_identity.py`
- Modify only if required by resulting canonical keys: `core/engine/reference_model.py`
- Test: `core/tests/test_line_identity.py`

**Interfaces:**
- Consumes: `normalize_label(text: str) -> str`, `LineItem`, existing `LineIdentity`.
- Produces: `line_identity(item: LineItem) -> LineIdentity` whose `label` field is canonical case-insensitive comparison text while `concept` remains exact normalized identifier text.

- [ ] **Step 1: Add failing normalization tests**

Add focused tests equivalent to:

```python
def test_line_identity_label_is_case_insensitive_but_concept_is_exact():
    a = _li("Goodwill", 10, 12, "Goodwill")
    b = _li("  GOODWILL  ", 10, 12, "Goodwill")
    assert line_identity(a) == line_identity(b)

    # Concept IDs remain exact identifiers; case-only concept changes are not
    # silently assumed to be the same taxonomy concept.
    c = _li("Goodwill", 10, 12, "goodwill")
    assert line_identity(a) != line_identity(c)


def test_conceptless_duplicate_labels_differing_only_by_case_fail():
    items = [
        _li("Goodwill", 10, 12),
        _li("GOODWILL", 11, 13),
    ]
    with pytest.raises(AmbiguousStatementIdentityError):
        validate_statement_identities(items, "balance_sheet")
```

Also cover NBSP/extra-whitespace plus case in at least one assertion so the identity contract is tested as one canonicalization rule rather than separate accidents.

- [ ] **Step 2: Run the focused tests and confirm the intended failure**

Run:

```bash
pytest core/tests/test_line_identity.py -k "case_insensitive or differing_only_by_case" -v
```

Expected before implementation: FAIL because `line_identity()` currently preserves label case.

- [ ] **Step 3: Implement the minimum canonical-label change**

Use one focused normalization path inside `core/data/line_identity.py`, equivalent in behavior to:

```python
def _canonical_label(label: str) -> str:
    return normalize_label(label or "").casefold()


def line_identity(item: LineItem) -> LineIdentity:
    raw_concept = (item.concept or "").strip()
    concept = normalize_label(raw_concept) if raw_concept else ""
    return LineIdentity(
        concept=concept,
        label=_canonical_label(item.label or ""),
    )
```

Do not mutate `item.label`. Do not lower/case-fold `concept`.

Because `LineIdentity.key()` is the canonical key used by reconciliation and source-row metadata, its label portion may become case-folded. That is expected. If tests currently hard-code mixed-case rowmap keys, update them to assert the canonical identity contract rather than restoring case-sensitive identity merely to preserve the old string.

- [ ] **Step 4: Add and run cross-document reconciliation regression**

Add a regression equivalent to:

```python
def test_same_concept_and_case_variant_label_merge_as_one_identity():
    existing = [_li("Goodwill", 10, 12, "Goodwill")]
    incoming = [_li("GOODWILL", 10.1, 12.1, "Goodwill")]

    merged, _ = _merge_line_items(existing, incoming, "restatement")

    assert len(merged) == 1
    assert merged[0].label == "Goodwill"  # original display label preserved
```

Use values that exercise the existing non-blocking restatement path rather than introducing an unrelated large-conflict assertion.

Run:

```bash
pytest core/tests/test_line_identity.py -k "case_variant_label or case_insensitive or differing_only_by_case" -v
```

Expected after implementation: PASS.

- [ ] **Step 5: Verify rowmap identity and workbook display do not regress**

Update/extend `test_rowmap_preserves_both_duplicate_labels` so:

- two genuinely different concepts with the same displayed label still receive two distinct canonical rowmap keys;
- the visible Balance Sheet still shows the original source labels exactly as supplied;
- rowmap assertions derive the identity portion from `line_identity(...).key()` or otherwise explicitly expect canonical case-folded label identity.

Do not modify worksheet display labels to satisfy metadata tests.

---

### Task 2: Remove unsafe generic preferred-stock concept classification

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Interfaces:**
- Consumes: `_classify_by_concept(item)` and existing label fallback in `classify_balance_sheet_line()`.
- Produces: preferred-stock concepts fall through unless another independently decisive concept signal applies.

- [ ] **Step 1: Add the failing preferred-stock regression**

Add a test equivalent to:

```python
def test_redeemable_preferred_stock_concept_does_not_force_equity():
    item = LineItem(
        label="Long-term debt",
        concept="PreferredStockSubjectToMandatoryRedemption",
        values={P1: 10, P2: 12},
    )

    assert classify_balance_sheet_line(item).category == "Financial Liability"
```

This test is deliberately structured so the existing label classifier has an unambiguous safe fallback. The failure should therefore prove that the concept shortcut, not the label rules, is wrong.

- [ ] **Step 2: Run the focused test and confirm the intended failure**

Run:

```bash
pytest core/tests/test_classification.py -k "preferred_stock" -v
```

Expected before implementation: FAIL with category `Equity`.

- [ ] **Step 3: Make the concept classifier conservative**

Remove generic `preferredstock` from the set of unconditional Equity concept signals. Do not replace it with another broad preferred-stock rule.

The intended behavior is:

```text
clear retained-earnings/share-capital/AOCI/etc. concept
    -> concept may classify Equity

generic preferred-stock concept
    -> concept classifier returns None
    -> existing label classifier or explicit override decides
```

Do not disturb the positive concept tests for deferred taxes, lease/ROU, clear borrowing liabilities, clear cash/marketable-security assets, retained earnings, share capital, treasury stock, or AOCI.

- [ ] **Step 4: Run classification regressions**

Run:

```bash
pytest core/tests/test_classification.py -v
```

Expected: all classification tests pass, including the three regressions added in the previous correction pass.

---

### Task 3: Full Step 4 verification and handoff

**Files:**
- Modify: `RESULT.md`
- Modify `skills/bav-trainer/SKILL.md` only if canonical rowmap/identity behavior is user-facing and the existing wording becomes false.

**Interfaces:**
- Consumes: corrected identity + classification behavior.
- Produces: exact verification evidence for ChatGPT review.

- [ ] **Step 1: Run the full required suite**

Run exactly:

```bash
pytest core/tests/test_line_identity.py -v
pytest core/tests/test_classification.py -v
pytest core/tests/test_reference_integrity.py -v
pytest core/tests/test_line_resolver.py -v
pytest core/tests/test_trainer.py -v
pytest core/tests/ -q
python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
```

The Excel optional-Concept-column coverage is currently inside `test_line_identity.py`; verify it remains collected and passing.

- [ ] **Step 2: Inspect the generated pair structurally**

Using the existing openpyxl-based tests or one focused temporary inspection, verify:

- both `/tmp/DEMO_HK_Trainer.xlsx` and `/tmp/DEMO_HK_Answer_Key.xlsx` exist;
- the CLI still reports 13 semantic components;
- no third user-facing reference workbook is generated;
- Trainer practice cells remain blank yellow without Notes;
- Answer Key practice cells retain formulas/inputs, yellow fill, and Notes.

Do not add a new permanent output file to the repository.

- [ ] **Step 3: Overwrite `RESULT.md` with exact evidence**

Use this format:

```text
Status: Step 4 final correction pass complete | blocked

Files changed:
- ...

Tests run:
- <exact command> -> <exact result>
...

Final identity checks:
- case-insensitive displayed-label identity: ...
- concept identifiers remain exact: ...
- case-only conceptless duplicate rejection: ...
- case-variant cross-document label merge: ...
- rowmap canonical identity + original worksheet display: ...

Final classification checks:
- redeemable preferred stock no longer forced to Equity: ...
- previous debt-security / equity-method / cash-flow-hedge regressions: ...
- deferred-tax asset/liability concept behavior: ...

Preserved checks:
- Step 3 integrity: ...
- paired Trainer / Answer Key: ...
- semantic components: 13

Unresolved: none | <specific blocker>
```

Do not write `Unresolved: none` unless every command above passed.

---

## Preserve all already-correct behavior

Do not regress any of the following:

- distinct same-label rows with genuinely different non-empty concepts remain separate;
- concepted + conceptless same-label ambiguity fails;
- duplicate conceptless same-label ambiguity fails;
- duplicate same-identity rows within either source fail before dictionary merge;
- one same identity in each of two documents follows existing restatement/conflict behavior;
- optional Excel `Concept | Line Item | dates` and legacy `Line Item | dates` formats both ingest;
- `concept:` overrides remain exact concept selectors;
- unique bare-label and `label:` overrides remain case-insensitive;
- ambiguous label selectors still fail and require `concept:` selectors;
- concept-qualified source-row metadata remains coordinate-free;
- worksheet display labels remain original source text;
- Step 3 eight-category reformulation and reconciliation checks remain enforced;
- live Condensed Financials classification/SUMIF behavior remains intact;
- DuPont uses implied reformulated equity;
- Bear/Base/Bull ten-year residual-income chain remains intact;
- Trainer / Answer Key visual parity and Notes contract remain intact;
- existing 13 semantic components remain unchanged.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership/order.
- forecast or residual-income mathematics.
- workbook product naming or output count.
- Hint / Reveal behavior.
- automatic sourcing architecture.
- Git history.

## Acceptance criteria

Step 4 is accepted only when all of the following are true:

1. `Goodwill` and `GOODWILL` with the same exact concept resolve to the same canonical line identity.
2. Concept identifiers remain exact/case-sensitive after whitespace/NBSP normalization.
3. Two conceptless same-label rows differing only by case fail with `AmbiguousStatementIdentityError`.
4. Cross-document rows with the same exact concept and case-only label differences reconcile as one identity rather than becoming duplicate economic rows.
5. Source-row metadata uses the same canonical identity as reconciliation while visible worksheet labels retain original display text.
6. A preferred-stock concept that is not itself safely decisive cannot force an otherwise clear liability line into Equity.
7. The previous `DebtSecuritiesAvailableForSale`, `EquityMethodInvestments`, and `CashFlowHedgeReserve` regressions continue to pass.
8. Explicit deferred-tax asset/liability concepts still classify correctly.
9. Label override compatibility and ambiguity protection remain intact.
10. All Step 3 integrity tests pass.
11. Full core test suite passes.
12. Demo still builds exactly the matched 13-component Trainer / Answer Key pair.

## Cursor execution rules

1. Read this entire active step before editing.
2. Write the new regression test for each task before implementation and verify that it fails for the intended reason.
3. Make the smallest code change that satisfies the stated contract.
4. Run the focused test immediately after each fix.
5. Run the full suite only after both focused corrections pass.
6. Update `RESULT.md` with exact commands/results.
7. Report files changed and unresolved issues.
8. Do not start the next product step.
9. Do not modify this `IMPLEMENTATION.md` during execution.
10. Do not commit or push.

## ChatGPT verification protocol

After the user checkpoints and pushes Cursor's implementation, ChatGPT should verify the new commit against every acceptance criterion above. If all criteria are satisfied, Step 4 can be closed and the next implementation plan should expand the semantic practice surface beyond the current 13 representative components rather than add more identity architecture without a concrete failing case.
