# RESULT.md — Step 9M.1.1 Filing-JSON Hardening Acceptance and Closure

**Review status:** PASS
**Completion:** DONE
**Next step:** None

**Implementation base (plan):** `af02e2e575ab95e5ecd6b2047d395b4002098a07`
**HEAD at completion:** `1760bd37b9c32e9b1e9e87a6dcc1d206fc444bb4`
**Historical plan:** `d3b808b:IMPLEMENTATION.md`
**Historical completion claim:** `a707408:RESULT.md` (incomplete relative to plan; defects repaired this step)

**Writable this step:** filing hardening modules/tests + `RESULT.md`.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No commit / push / sync / checkpoint. No Step 9M.2.

---

## What shipped

Hardening defects remaining after `a707408` were repaired:

1. **Exact ISO dates** — `_parse_date` no longer truncates; rejects `…junk`, `T00:00:00`, `/` separators, and impossible calendar days.
2. **Windows absolute paths** — validator rejects `PureWindowsPath` absolutes (e.g. `C:\…`) before any source read/hash.
3. **Complete bound-source registry** — `BoundSourceFile` + `ReconciledCompanyData.source_files` populated from every validated filing/report pair; provenance serializes `filing_year` / `source_file` / `source_sha256` from that registry (not from selected statement observations).

Forecasting / valuation remain dormant. Committed benchmark/release artifacts were **not** overwritten.

---

## Acceptance mapping (original Step 9M.1.1 → current evidence)

| Requirement | Code | Named tests | Measured evidence | Remaining defect |
|---|---|---|---|---|
| Strict required metadata | `filing_json._required_nonempty_str` / `_required_positive_int` | `test_parser_rejects_missing_required_fields` | blank/missing company fields, bad `fiscal_year`, blank currency/source_file → `ValueError` | none |
| Exact ISO dates (no truncate) | `filing_json._parse_date` | `test_parser_rejects_non_exact_iso_dates`, `test_parser_accepts_exact_iso_date` | junk/`T`/`/`/Feb-30 rejected; `2025-08-31` accepted | none (fixed this step) |
| Portable source-root containment before access | `filing_validator.validate_extracted_filing` + `PureWindowsPath` | `test_validate_rejects_escaping_source_paths`, `test_validate_allows_nested_relative_source_path`, `test_validate_and_reconcile_reject_invalid_source_path` | abs/`..`/Windows abs → `invalid_source_path`, `computed_source_sha256 is None`; nested relative OK | none (Windows case fixed this step) |
| Complete bound-source registry | `BoundSourceFile`, `reconcile_filings` → `source_files` | `test_complete_bound_source_registry_retains_losers_and_supplemental_only`, FR live assert in `test_migration_reproduces_fy2025_anchors_and_conflict_parity` | loser filing with no selected statements still in registry; FR live = 5/5 with years | none (fixed this step) |
| Source-bound supplemental provenance | `SupplementalObservation` + `_supplemental_observation_payload` | `test_supplemental_observations_retain_source_binding` | filing_year, source_file, SHA-256, page, derivation retained | none |
| Deterministic supplemental conflicts | `_group_supplemental_conflicts`, conflicts payload | FR + reconciler share/note disagreement tests | overlap=3, supplemental=3; reason `cross_filing_supplemental_disagreement` | none |
| Fail-closed share promotion | `resolve_historical_share_basis` via `_historical_shares` | share-basis / FR share tests | disagreements retained; promotion only via explicit basis policy | none (policy evolved; see below) |
| Synthetic workbook drift (`DEMO_HK_Trainer.xlsx`) | n/a (historical) | historical blob evidence only | Pre-9M.1 `1f4bdfd6` blob ≠ `e5fa7b8` (9M.1 drift). Later intentional changes: `a707408` restore attempt, then `5510c1e` Step 9M.5 further change. Current HEAD blob matches `5510c1e`. **Not restored** to obsolete pre-9M.1 bytes. | none for this closure |
| G1–G7 / family counts | preserved outside this step | FR/GAPS docs + suite | historical evidence only; not reverted | n/a (out of scope) |
| Formatting-verification evidence | prior Step 9 RESULT | prior border/theme work | separately identified prior work; **not** used as hardening closure | n/a |

### Share-promotion discrepancy vs `a707408`

Historical record claimed Fast Retailing `historical_shares` omitted. Current measured behavior (accepted later share-basis policy): `basis=split_adjusted`, `split_factor=3.0`, `restatement_filing_year=2023`, diluted WAS axis present. Supplemental conflict count remains **3**. Statement overlap remains **3**. Explicit policies preserved; no silent order-based overwrite.

### Provenance artifact comparison (live vs committed)

Live reconcile adds `filing_year` on each `source_files[]` entry. Committed `benchmark/…/provenance.json` and `release/…/provenance.json` still lack that field (hash `fd5a1ec8…`). `standardized.json` and `conflicts.json` byte-identical to committed (`5a1d445c…`, `12b91048…`). Per plan: difference investigated; committed artifacts **not** overwritten to force a pass.

---

## Measured verification (fresh this step)

### Commands

```text
python -m pytest core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_fast_retailing_benchmark.py -q
→ 197 passed in 27.95s

python -m core reconcile benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source -o /tmp/fr-harden-1
python -m core reconcile benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source -o /tmp/fr-harden-2
diff -ru /tmp/fr-harden-1 /tmp/fr-harden-2
→ no differences (deterministic)

python -m pytest core/tests -q
→ 714 passed in 85.31s

python -m core --help
→ commands: ingest, validate-source, reconcile, build, check, list (no extract)

git diff --check
→ clean
```

### Source registry + hashes (live)

| FY | source_file | computed SHA-256 |
|---|---|---|
| 2021 | Fastretailing_CFS2021.pdf | `06b50e0ffbd9504953f0401613d7238fe1c66f95a280d134938570458da74798` |
| 2022 | Fastretailing_CFS2022.pdf | `9fb8d620d22bd0c679342a14ede59916207c08c6577ae96290aaa9e567593baa` |
| 2023 | Fastretailing_CFS2023.pdf | `2fe7a85584ed77323d2ce87b3d81dacfbb5907ac7eed878bae7c1985f00116b6` |
| 2024 | Fastretailing_CFS2024.pdf | `72f484268962546e84efc817f00c95ab993cbf8d2c7d532b5ef0e3a2cf26d1de` |
| 2025 | Fastretailing_CFS2025.pdf | `25a85db811fbb1c6c94af50f1ac5b1fa9ffea794753a143685dcf5191d06147f` |

- overlap_conflict_count: **3**
- supplemental_conflict_count: **3**
- bound source_files: **5/5** (with `filing_year` in live provenance)

### Committed artifacts unchanged by verification

```text
4b657461757cfb43f6067636868df44541575d274b3a6925ccc6d397dac89536  FastRetailing_Trainer.xlsx
a1d397933971535cdba7f2c2076014462cc00c66ffe19a2a4651d2e192c9e089  FastRetailing_Answer_Key.xlsx
5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1  standardized.json (benchmark + release)
fd5a1ec87b61c4835d3b7bfda79996afa6c5ed9bbf2082e35413fb18ee696f1f  provenance.json (committed; lacks filing_year on source_files)
12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5  conflicts.json
```

Incidental suite touches to `example/DEMO_HK_Trainer.xlsx` / benchmark provenance were restored; final diff excludes them.

### Final changed-file list

```text
core/ingestion/filing_json.py
core/ingestion/filing_validator.py
core/ingestion/filing_reconciler.py
core/ingestion/filing_standardizer.py
core/tests/test_filing_json.py
core/tests/test_filing_reconciler.py
core/tests/test_fast_retailing_benchmark.py
RESULT.md
```

---

## Acceptance

| Criterion | Result |
|---|---|
| Every 9M.1.1 requirement has explicit evidence (formatting not substituted) | **pass** |
| Required verification passes; no known remaining hardening defect | **pass** |
| Review status PASS; completion DONE; next step None | **pass** |
| Only writable files changed; no commit/push; no next stage started | **pass** |

**Unresolved issues:** none on Step 9M.1.1 hardening scope.

**Plan changes needed:** none. Optional follow-up outside this step: regenerate committed provenance JSON to include `filing_year` on `source_files` (live already emits it; committed bytes intentionally left unchanged here).
