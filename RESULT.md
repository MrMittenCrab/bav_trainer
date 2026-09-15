# RESULT.md — Step 9M.2.4.1.1.1.20 Lululemon G5 Final-Artifact Acceptance

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.20 — Lululemon G5 Final-Artifact Acceptance  
**Work / attempt:** `ed0d79edb1bc4f9bbe126a527dab85b9` / `1e2e9169e8874f86a26f1974a4aede94`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged by this run).  
No commit / push / sync / checkpoint / branch change. No release regeneration. No production, test, source, provenance, or workbook byte changes.

This file supersedes stale and truncated Trainer/Answer-Key hash claims from the reviewed checkpoint RESULT at `ad3365fd2a8696a1ec087c49f329ee0652edf8f8`. No abbreviated digest is final acceptance evidence.

---

## Revisions (kept distinct)

| Layer | SHA-1 | Role |
|---|---|---|
| Original implementation baseline | `237c265b81e71ced0d323814fe7924850baaf147` | Step 9M.2.4.1.1.1.19; G5 work plan base (248-cell Lululemon) |
| Historical execution HEAD | `86bedae921225803fe3ec1c6c7bb6e76690213b5` | G5 work-plan commit (`Autocycle-Input-Batch: 7c02b8a159ee476797287e2e3aba94d1`) |
| Reviewed checkpoint | `ad3365fd2a8696a1ec087c49f329ee0652edf8f8` | G5 implementation bytes under review |
| Workspace HEAD (this plan) | `0552e14d50fba7004791e7a674aee5dd95909789` | Final-artifact acceptance plan (`Autocycle-Input-Batch: bafa189414944a4396f8851d852047f2`) |

Capex progress remains a separate reviewed child (`cbecd085c9f6b9305b3272ba65c5aca210875871`; plan batch `8e08870dbd2544239e99741a85fa3f19`). This child's acceptance is final-artifact hash repair only. Reviewed ownership is not reopened. Publication is not claimed.

---

## Task 1 — Final release bytes (computed this run)

Working-tree SHA-256 and sizes were computed with Python `hashlib.sha256` over file bytes. Checkpoint bytes were taken from `git show ad3365fd2a8696a1ec087c49f329ee0652edf8f8:<path>` and hashed independently. Every path below is **MATCH** (identical digest and size).

Confirmed by computation, not transcription:

- `release/lululemon/Lululemon_Trainer.xlsx` = `0fc9d5295adc00c3674f7e82d1a71bebd1a0715d19de039275774b7cb4ed8caf` (30206 bytes)
- `release/fast_retailing/FastRetailing_Trainer.xlsx` = `8bc7d7ccfb2cc75b55fd250c17188e27348d504c804a48fac719ce413c803fb9` (37015 bytes)

### Lululemon inventory

| Path | SHA-256 | Bytes | vs checkpoint |
|---|---|---:|---|
| `release/lululemon/Lululemon_Trainer.xlsx` | `0fc9d5295adc00c3674f7e82d1a71bebd1a0715d19de039275774b7cb4ed8caf` | 30206 | MATCH |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `45ed925fff77084c11f0fa749f60ea50e296e8dcbeece0b5c8a00e597a489c8a` | 83576 | MATCH |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `50a42c44e6e65040b42055825ff7f2af4eca5cb5adf584017d4555f17087672e` | 292228 | MATCH |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 | MATCH |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 | MATCH |
| `release/lululemon/rowmap.json` | `ae3a6d9fa7dc2c48eb471c20ecd78f195d1f2f5c4bebfbce61af38f1459b1e43` | 61588 | MATCH |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 | MATCH |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 | MATCH |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 | MATCH |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 | MATCH |

Lululemon supporting standardized/provenance/conflicts are SHA-256-identical to `benchmark/lululemon/reconciled/`.

### Fast Retailing inventory

| Path | SHA-256 | Bytes | vs checkpoint |
|---|---|---:|---|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `8bc7d7ccfb2cc75b55fd250c17188e27348d504c804a48fac719ce413c803fb9` | 37015 | MATCH |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `ca5b57e53d6c1893a2e6baa9c37f09c4365121618704fddf11dd18de002b2909` | 123565 | MATCH |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `dbdf3bb3388073321e0b80b566a4e5c9e69d4dfac4de177ca8873163f5ff5a34` | 531630 | MATCH |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 | MATCH |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 | MATCH |
| `release/fast_retailing/rowmap.json` | `5e3218358b7a2b9a6a1a77cb61787ff0ba6dc035016498fdcb9a947c36ac4e38` | 80710 | MATCH |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 | MATCH |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 | MATCH |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 | MATCH |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 | MATCH |

Fast Retailing supporting standardized/provenance/conflicts are SHA-256-identical to `benchmark/fast_retailing/reconciled/`. Component map and availability match the 491-cell contract retained since baseline `237c265`.

### Superseded incorrect claims (checkpoint RESULT)

| Claim in `ad3365f` RESULT | Computed bytes | Disposition |
|---|---|---|
| `Lululemon_Trainer.xlsx` = `97fc521ad8d573cd1aa6432dd1bc1df726571e04b96414770dd3b3eaf8d4446d` (30206) | `0fc9d5295adc00c3674f7e82d1a71bebd1a0715d19de039275774b7cb4ed8caf` (30206) | **SUPERSEDED** — digest does not match working-tree, checkpoint, baseline `237c265`, or execution HEAD `86bedae` |
| Fast Retailing Trainer = `15fd3cef…` | `8bc7d7ccfb2cc75b55fd250c17188e27348d504c804a48fac719ce413c803fb9` (37015) | **SUPERSEDED** — truncated prefix does not match computed digest |
| Fast Retailing Answer Key = `ca5b57e5…` | `ca5b57e53d6c1893a2e6baa9c37f09c4365121618704fddf11dd18de002b2909` (123565) | **SUPERSEDED as evidence** — prefix is consistent but truncated; full digest required |

`Lululemon_Answer_Key.xlsx` `45ed925fff77084c11f0fa749f60ea50e296e8dcbeece0b5c8a00e597a489c8a` (83576) was already full and matches.

---

## Task 2 — Completion evidence (no fresh test runs)

Formula inspection remains separate from spreadsheet recalculation. This environment does not evaluate Excel with Excel.app. Spreadsheet recalculation was **not performed**.

`git diff --name-only ad3365fd2a8696a1ec087c49f329ee0652edf8f8 -- core/ scripts/ benchmark/ release/` is empty. Production, tests, source PDFs, extracted/reconciled facts, provenance, capex edits, and release bytes are unchanged versus the reviewed checkpoint. `TARGET.md` SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552) is unchanged.

### Coverage retained from reviewed G5 work

- Prior 248-cell Lululemon surface preserved; **+12** `lease_rou` + **+13** `deferred_tax` → **273** practice/Check cells.
- Fast Retailing **491**-cell contract retained (component map unchanged).
- 74 Lululemon `Source unavailable` displays per workbook; Fast Retailing 0 / 0.
- Availability sidecar unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3`; `hist_avg_after_tax_cod` reason `absent_line`; no 4% substitute.
- Independent `ppe_capex` 638657 / 651865 / 689232 / 680802; NCIT 28555 / 15864 / 0 / `None`; Common stock 611 / 606 / 581 / 557.

### Reviewed G5 regressions (not re-run this step)

Historical subprocess exits recorded at checkpoint RESULT (`PYTHONPATH=.`):

| Command | Exit | Result |
|---|---:|---|
| `python -m pytest core/tests/test_line_resolver.py core/tests/test_lease_rou.py core/tests/test_deferred_tax.py -q --tb=line` | 0 | **70 passed** in 1.94s |
| `python -m pytest core/tests/test_source_availability.py core/tests/test_capex.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q --tb=line` | 0 | **210 passed** in 36.90s |
| `python -m pytest core/tests/test_reference_integrity.py core/tests/test_trainer.py -q --tb=line` | 0 | **120 passed** in 17.42s |
| `python -m pytest` affected model/trainer/reference-integrity/both benchmarks (`test_reference_integrity`, `test_trainer`, `test_lululemon_benchmark`, `test_fast_retailing_benchmark`, `test_capex`, profitability, ROE, per-share, normalization, lease) | 0 | **432 passed** in 73.39s |
| `python -m pytest core/tests -q --tb=line` | 0 | **1156 passed** in 93.23s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |

Independent Python series (four-period axis 2023-01-29 / 2024-01-28 / 2025-02-02 / 2026-02-01), retained:

| Series | Values |
|---|---|
| ROU levels | 969419 / 1265610 / 1416256 / 1630181 |
| ROU change | `None` / 296191 / 150646 / 213925 |
| ROU average | `None` / 1117514.5 / 1340933.0 / 1523218.5 |
| ROU / revenue | `None` / 1117514.5÷9619278 / 1340933.0÷10588126 / 1523218.5÷11102600 |
| DTA | 6402 / 9176 / 17085 / 24037 |
| DTL | 55084 / 29522 / 98188 / 52278 |
| Net DTA−DTL | −48682 / −20346 / −81103 / −28241 |
| DTA change | `None` / 2774 / 7909 / 6952 |
| DTL change | `None` / −25562 / 68666 / −45910 |
| Net change | `None` / 28336 / −60757 / 52862 |

Answer-Key source links after export/reload: ROU `='Balance Sheet'!B26`, DTA `='Balance Sheet'!B21`, DTL `='Balance Sheet'!B27`. Stored concepts remain `right_of_use_lease_asset` / `deferred_tax_asset` / `deferred_tax_liability`. Blank Check `(0,0,273,273)`; filled disposable `(273,0,0,273)`. Fast Retailing blank Check `(0,0,491,491)`.

### Hash-bound recovery evidence (capex; not this child's publication)

Original isolation `/tmp/bav_9m24111117_iso_nXG6` (RESULT at `cbecd085c9f6b9305b3272ba65c5aca210875871`):

- Isolation HEAD `0ce0d61a20eca1dc83c3a754430d19e275d0c7ef`; implementation base `04aa1c4a6864883062e4ccbe901d61d2e774a76c`.
- Snapshot-limited overlay authorization: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`.
- Verified overlay aggregate SHA-256 (221 tracked files excl. `RESULT.md`): `844b5163039f5c6670d8494f8963babd92ff9ada123eb9edbf9ab56e08040ffc`.
- Original successful subprocess exits support capex progress: focused **76 passed** exit 0 (5.56s); parent **543 passed** exit 0 (13.12s); FR **132 passed** exit 0 (29.97s); full **1099 passed** exit 0 (92.08s).

Resumed focused wrappers exited 1 despite passing summaries. That finding is preserved and is **not** treated as a capex-progress failure, a publication claim, or a reason to reopen reviewed ownership. Capex progress is assessed separately from this child's final-artifact acceptance.

Historical batch identity for this acceptance plan: `bafa189414944a4396f8851d852047f2`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Task 3 — Read-only verification (this run)

Measured after RESULT correction; inventory recomputed and every current full digest in RESULT was checked against those bytes.

| Command | Exit | Result |
|---|---:|---|
| Python SHA-256 of every `release/{lululemon,fast_retailing}` file vs `git show ad3365fd2a8696a1ec087c49f329ee0652edf8f8:<path>` | 0 | 20/20 MATCH (digests and sizes); `ALL_MATCH True` |
| Confirm Lululemon Trainer digest `0fc9d5295adc00c3674f7e82d1a71bebd1a0715d19de039275774b7cb4ed8caf` | 0 | True |
| Confirm Fast Retailing Trainer digest `8bc7d7ccfb2cc75b55fd250c17188e27348d504c804a48fac719ce413c803fb9` | 0 | True |
| Read-back: every current 64-hex digest in RESULT equals the recomputed inventory or TARGET.md (`3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2`); stale `97fc521ad8d573cd1aa6432dd1bc1df726571e04b96414770dd3b3eaf8d4446d` listed only as SUPERSEDED | 0 | pass |
| `git diff --name-only ad3365fd2a8696a1ec087c49f329ee0652edf8f8 -- core/ scripts/ benchmark/ release/` | 0 | empty |
| `git diff --name-only ad3365fd2a8696a1ec087c49f329ee0652edf8f8 -- TARGET.md` | 0 | empty |
| `git diff --name-only HEAD` / `git status --short` | 0 | `RESULT.md` only (` M RESULT.md`) |
| `git diff --name-only -- TARGET.md IMPLEMENTATION.md release/` | 0 | empty (plan `IMPLEMENTATION.md` already at HEAD; not this edit) |

Artifact-writing suites and pytest were **not** rerun. Reviewed checkpoint regression evidence is reused because production/tests/release bytes are unchanged. Abbreviated `15fd3cef…` / `ca5b57e5…` / `97fc521a…` appear only as superseded incorrect claims, not as current evidence.

---

## Original G5 acceptance retained

Shared `_EXPLICIT_CONCEPT_ALIASES` in `core/model/line_resolver.py`: `right_of_use_lease_asset` → `right_of_use_assets`; `deferred_tax_asset` → `deferred_tax_assets`; `deferred_tax_liability` → `deferred_tax_liabilities`. Canonical identities, explicit-concept precedence, ambiguity rejection, and strict required-period values preserved. No issuer-specific heuristics or source mutation.

Python values, original-row source links, derived formulas, semantic maps, and Check agree. Repeat-build semantic determinism, visual parity, and non-disclosing blank/correct/incorrect Check behavior retained. Trainers have blank yellow practice cells without Notes; matching Answer Keys have formulas and Notes; exactly two user-facing workbooks per issuer.

Parent temporary-build criterion retained: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; current gated generation is successful. No invented interest, inferred zeros, cash-interest substitution, lease repayment flows, deferred-tax expense/recoverability, new note extraction, forecasting, or valuation.

---

## Child acceptance

| Criterion | Evidence | Status |
|---|---|---|
| Working-tree release bytes match checkpoint `ad3365fd` | 20/20 full SHA-256 + size MATCH via `git show` | **PASS** |
| Specified Trainer digests confirmed by computation | Lululemon `0fc9d5295adc00c3674f7e82d1a71bebd1a0715d19de039275774b7cb4ed8caf`; Fast Retailing `8bc7d7ccfb2cc75b55fd250c17188e27348d504c804a48fac719ce413c803fb9` | **PASS** |
| Stale/truncated hash claims superseded | incorrect `97fc521a…` and `15fd3cef…` replaced; truncated `ca5b57e5…` expanded | **PASS** |
| Production/tests/source/provenance unchanged | empty `git diff` vs checkpoint on `core/ scripts/ benchmark/ release/`; supporting hashes match benchmark | **PASS** |
| +12 lease-ROU / +13 deferred-tax and 491-cell FR contract retained | reviewed G5 RESULT; maps/availability hashes above | **PASS** |
| Capex progress separate from this acceptance / publication | original isolation exits 0; resumed wrappers exit 1 preserved; ownership not reopened | **PASS** |
| Spreadsheet recalculation not performed | recorded | **PASS** |
| Parents not closed; INPUT_STATUS PENDING; frozen requests pending | recorded below | **PASS** |

---

## Remaining blockers (carried forward)

- Source-interest completeness: standalone IS interest still **not found** (G9).
- Parent Plan closure (A5 / B8 / E10).
- A2-ED / B7-MID documentary UNVERIFIED; E11 NonReq UNVERIFIED.
- G6 period-axis assessment; G7 empty `note_facts`; G8 deferral; remaining TARGET Step 9 gates.
- Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Closure note (does not rewrite the plan)

Step **9M.2.4.1.1.1.20** final-artifact acceptance **PASS**. Keep **INPUT_STATUS: PENDING**. Parents stay **UNRESOLVED**. Child success does not satisfy frozen requests or justify blanket DONE.

**Required plan note (do not edit IMPLEMENTATION.md here):** none blocking. Hash-repair closed on measured inventory; G9 source-interest completeness and parent acceptance remain residual. Continue highest-priority benchmark-improving Step 9 work through the normal five stages after this acceptance defect is verified closed.
