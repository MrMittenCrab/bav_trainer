Status: Step 9M.1.1 complete — filing-JSON provenance + validation hardening

Implementation base:
- e5fa7b8 Step 9M.1 generic filing-JSON input + Fast Retailing migration
- Target/spec: TARGET.md source-data architecture + filing-JSON design

Final verification (Task 6):
- focused input suite: 54 passed
- full `core/tests/`: 370 passed
- CLI: `{ingest, validate-source, reconcile, build, check, list}` (no `extract`)
- family orders: 1..90 unchanged
- Fast Retailing `historical_shares`: omitted (no complete unambiguous diluted WAS axis)
- forecasting / valuation: still deferred
- TARGET.md unchanged by Cursor

Step 9M.1.1 evidence:
- supplemental provenance source-bound: yes
- portable source-path validation: yes
- silent repeated-share overwrite removed: yes
- statement overlap conflicts: 3
- supplemental conflict count: 3
- G1–G7 accounting gaps preserved for 9M.2: yes
- `standardized.json` byte-identical to Step 9M.1: yes
- reconcile deterministic across two temp dirs: yes

Review defects closed:
1. note/share facts retain filing_year + source_file + computed SHA-256 after reconcile
2. disagreeing repeated diluted WAS observations create supplemental conflicts and block promotion
3. blank required metadata and absolute/`..` source paths are rejected before hashing

Files touched:
- `core/ingestion/filing_json.py`
- `core/ingestion/filing_validator.py`
- `core/ingestion/filing_reconciler.py`
- `core/ingestion/filing_standardizer.py`
- `core/tests/test_filing_json.py`
- `core/tests/test_filing_cli.py`
- `core/tests/test_filing_reconciler.py`
- `core/tests/test_fast_retailing_benchmark.py`
- `scripts/audit_fast_retailing_benchmark.py`
- `benchmark/fast_retailing/reconciled/{provenance,conflicts}.json`
- `benchmark/fast_retailing/PROVENANCE.md` / `BASELINE.md`

Next checkpoint:
- Step 9M.2 accounting-engine gap queue from `benchmark/fast_retailing/GAPS.md`

Unresolved on 9M.1.1 scope: none — G1–G7 remain intentionally open for 9M.2
