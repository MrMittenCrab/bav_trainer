# RESULT.md — Step 9M.2.4.1.1.1.28 Inventory balance movement versus reported operating cash-flow adjustment

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.28 — Inventory balance movement versus reported operating cash-flow adjustment  
**Work:** `04fefb0cc5274857b2b79a0ad9096974`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `067315121f93ee4147a9f2d046137422632dfff284062c739fac7e6cdddd9df9` (7756).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/inventory_analysis.py`, `core/model/line_resolver.py` (explicit-concept `change_in_inventories`), `core/engine/component_catalog.py` (families 145–151 with independent gating), `core/model/historical_expected.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 376), `scripts/audit_fast_retailing_benchmark.py` (`EXPECTED_PRACTICE_TOTAL` 577). Plan not rewritten.

---

## Task 1 — Inventory balance-to-cash-flow comparison

Registered unique explicit CF `change_in_inventories` on the cash-flow statement only, retaining original-row links and signed reported values. Duplicate concepts, label-only matches, and wrong-statement substitutes do not resolve.

Extended the existing inventory section with populated reported CF adjustment links for every modeled period, including the opening period when the value is available. Adjacent-period practice: `B_t = -(inventory_t - inventory_(t−1))` reusing the inventory-change result; `D_t = reported_CF_adjustment_t - B_t`. Opening-period comparison cells are empty; no opening inventory is inferred.

`B_t` gates on unique BS inventory alone. `D_t` additionally requires unique CF adjustment. Neither family requires revenue, CFO, or interest. Absent or ambiguous sources omit only dependent families. Missing required-period values fail closed. Reported zeros remain valid. No balancing plug is inserted.

Answer-Key Notes distinguish the negative balance movement from the reported operating CF reconciliation adjustment. A nonzero difference needs further evidence; it does not establish an error, cash paid for inventory, FX, acquisitions, write-downs, or another specific cause.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Latest `B_t` | Latest reported CF | Latest `D_t` | Adjacent `D_t` |
|---|---|---|---|---|
| Lululemon | `-258672` | `-188710` | `69962` | `-57181 / -37606 / 69962` |
| Fast Retailing | `-36498` | `-29855` | `6643` | `40164 / 10234 / 1666 / 6643` |

`B_t + D_t = reported_CF_adjustment_t` within `1e-8` on every adjacent period of both issuers. Stored identities unchanged. Lululemon CF: `change_in_inventories` / `Inventories`; Answer-Key source link `='Cash Flow Statement'!B25`. Fast Retailing CF: `change_in_inventories` / `(Increase)/decrease in inventories`; `='Cash Flow Statement'!B7`. Latest Lululemon formulas `=-E129` / `=E133-E134`. Latest Fast Retailing formulas `=-F118` / `=F122-F123`. Opening-period `B_t`/`D_t` cells are empty; opening CF facts remain populated.

Practice surface:

- Lululemon: preserved **370** identities + **6** comparison exercises → **376**
- Fast Retailing: preserved **569** identities + **8** comparison exercises → **577**

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,376,376)`, filled `(376,0,0,376)`; Fast Retailing blank `(0,0,577,577)`, filled `(577,0,0,577)`. Incorrect injection did not disclose formulas or hints. Trainers: 376/577 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_inventory_analysis.py core/tests/test_line_resolver.py::test_inventories_explicit_concept_and_label_only_rejection core/tests/test_line_resolver.py::test_inventories_competing_concepts_are_ambiguous core/tests/test_line_resolver.py::test_inventories_explicit_concept_outranks_label core/tests/test_line_resolver.py::test_change_in_inventories_explicit_concept_and_label_only_rejection core/tests/test_line_resolver.py::test_change_in_inventories_competing_concepts_are_ambiguous core/tests/test_line_resolver.py::test_change_in_inventories_explicit_concept_outranks_label core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen core/tests/test_lululemon_benchmark.py::test_source_supported_inventory_analysis_four_period_diagnostics core/tests/test_fast_retailing_benchmark.py::test_fast_retailing_inventory_analysis_five_period_diagnostics -q --tb=short` | 0 | **18 passed** in 1.15s |
| `PYTHONPATH=. python -m pytest` inventory, line-resolver, catalog freeze, source-availability, reported-margin, cash-rollforward, capex, lease-repayment, acquisition, share-repurchase, reference-integrity, reference-workbook-audit, Lululemon benchmark | 0 | **34** Lululemon passed after `PRIOR_LULULEMON_SPECS` 345→351; included in full suite |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1243 passed** in 101.44s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced (repeat-build map identical) |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |
| `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py --require-check-counts --verify-release-pair` | 0 | expected_specs=577; blank `(0,0,577,577)`; filled `(577,0,0,577)` |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `e92429b9ba77d0abd156e28eedcb1f8b4a9fe8ebf4484be4380e44fe4dd7bb1c` | 33232 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `e951e23d6031d57f2133a2aa50e1a2bf2c8ffcac481a56122361adb61d54261d` | 104190 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `fec1cc9ca587730593ea92fbd1f04483d06064cf74ff9ba3fedd59fcf24e3e84` | 434346 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `ba391eef7a52c953ebbc5699100946447af1f53537bf45e922e892aa66054ab7` | 78133 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `d4cd026560e7cc83ab260b2becdf3ce5cddc9991f6632e2fb12ef19bd2bcf754` | 94294 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified.

---

## Task 3 — Recorded disposition and pending obligations

Inventory disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md` now records source-gated inventory `B_t`/`D_t` comparison when unique explicit BS `inventories` and unique explicit CF `change_in_inventories` resolve (Lululemon and Fast Retailing). DEMO omits (no explicit inventory concept). Notes keep a nonzero difference as unexplained residual needing further evidence; it is not an error, cash paid for inventory, FX, acquisitions, write-downs, or another specific cause, and no balancing plug is inserted.

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery does not establish parent acceptance. No NEW_EVIDENCE claimed for those recovered logs.

Hash-bound logs (retained, not re-executed as this child's proof):

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

**Original** isolation subprocess (explicit `exit=0`; pytest duration vs wrapper elapsed kept distinct):

| Suite | Pytest | Wrapper elapsed | Exit |
|---|---|---|---:|
| focused 76 passed | 6.34s | 6.63s | 0 |
| parent 543 passed | 14.51s | 14.81s | 0 |
| Fast Retailing 132 passed | 30.51s | 30.77s | 0 |
| full 1099 passed | 95.38s | 95.66s | 0 |

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1243-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/reported-margin/inventory-intensity exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
