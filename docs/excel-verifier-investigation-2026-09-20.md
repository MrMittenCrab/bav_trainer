# Excel cached-value verifier investigation

Historical diagnosis before the interrupted verifier draft. See
[the subsequent permission diagnosis](excel-permission-diagnosis-2026-09-20.md)
for the separate file-access boundary and disposition of later uncommitted work.

## Diagnosis

No existing reusable verifier satisfies the requested acceptance semantics.
This is not evidence that AutoCycle lost a previously executable verifier
invocation. The requirement was established as plan/review prose; earlier
verification used one-off diagnostic Python commands, not a saved verifier.
Adding an alternate workbook argument to the existing Trainer Check or workbook
inventory would not supply the missing semantics.

Per the requested no-invented-verifier boundary, no production code, workbook,
Review cache, recovery state, or installed AutoCycle files were changed. The
blocker remains unresolved. The misleading implication in its Action is that
the human can supply an *existing* suitable verifier: this investigation found
none. A precise diagnosis is: **the project lacks an executable, read-only
saved-cache acceptance verifier that fails on independent-reference mismatches,
formula changes, and missing/error caches in affected formulas and dependencies.**

## Requirement and recovery trace

1. The Step 3.2 plan at commit `ca14d6d` (`git show
   ca14d6d:IMPLEMENTATION.md`, Verification) explicitly required actual Excel
   recalculation for new analytical formulas and affected dependencies,
   comparison with reference results, and unresolved blocking on unavailable
   access. This was an acceptance instruction, not a failure raised by a named
   command. The current plan retains the requirement at `IMPLEMENTATION.md:28`;
   `SESSION.md:31` also retains actual Excel acceptance.
2. `.git/autocycle/cursor-20260920-030117-18875.log` contains the earlier
   recalculation and read-only inspection commands. The Python was supplied
   through stdin, with a hardcoded temporary copy path. It counted formula
   differences, compared RPS results and source inputs with independent anchors,
   and printed RPS errors. It did **not** exit unsuccessfully for those
   differences/errors. Formula comparison skipped hidden sheets. It was not
   stored as a callable script or an argument-based verifier. Later commands
   varied their coverage; some merely printed caches, others scanned errors
   without asserting the reference comparisons. Replaying any such diagnostic
   as an exit-code verifier would permit false success.
3. `.git/autocycle/review-20260920-060220-42440.log.answer` records the current
   `excel-cached-value-verification` blocker after `-50` / `-128` Excel failures
   and unchanged copy bytes. Its structured `AUTOCYCLE_REVIEW` contains evidence
   paths/hashes and the acceptance reason, but no verifier invocation. The
   installed `~/.autocycle/stage:355` writes that structured record into
   `current-review`. There was no command in this Review record to carry forward.
   `resume-state` remains at `STAGE=review_done`.
4. `~/bin/autocycle:1044` invokes
   `excel_verification.py --resume-blocker current-review`. The installed helper
   at `~/.autocycle/excel_verification.py:110` first asks a read-only resolver for
   `{source, command}` with a separate literal `{workbook}` argument. Only after
   receiving that request does it call `verify()`.
5. The actual resolver output is
   `.git/autocycle/excel-resume-df_zvyq8/request.json`. It contains only the missing
   verifier Action. The helper rejects that result at line 146, before `verify`
   at line 151. Thus this recovery reached the Excel recovery *route*, but did
   **not** create/recalculate a new verification copy. Earlier implementation
   attempts did create copies. These are different events.
6. With a valid command, `verify()` at line 65 creates a uniquely named copy,
   recalculates/saves it, substitutes the copy for `{workbook}`, and checks the
   source hash. On success the controller exports `AUTOCYCLE_EXCEL_RECOVERY` and
   returns to fresh Review; Review still judges acceptance. Nonzero verifier
   status blocks with its current output. Successful helper execution alone
   does not complete the overall requirement.

## Closest existing paths

| Path | What it provides | Why it cannot implement this requirement |
| --- | --- | --- |
| `core/tests/test_revenue_per_store.py::test_lululemon_supported_periods_match_independent_anchors` | Independent revenue/store anchors, denominator calculations, reload and semantic-family checks | Tests Python calculations, not cached results in a supplied saved Excel copy; no formula-preservation or dependency-cache acceptance interface |
| `core/trainer/checker.py::check_workbook` | Workbook path input and historical expected calculations | Accepts matching formula text before examining caches (`:551–558`); recolors the input using `apply_fill_updates` (`:581`); not read-only saved-cache acceptance |
| `scripts/audit_reference_workbook.py` | Existing read-only CLI accepting a workbook path | Loads `data_only=False`, inventories sheets/formula counts; does not compare independent values, enforce formula identity, or inspect caches |
| Earlier inline commands in the Cursor log | Closest historical real-copy comparisons | No reusable entrypoint, hardcoded paths, incomplete enforcement/coverage, and exit status does not represent acceptance |

The inventory command can be run as `python
scripts/audit_reference_workbook.py COPY.xlsx`, but must **not** be registered as
the cached-value verifier. Likewise, successful pytest or Trainer Check results
cannot substitute for that verifier.

## Coverage and limitations

`automation/autocycle-fixes/test_excel_missing_verifier.py` adds focused coverage
for the actual missing-verifier refusal branch. It runs the real installed
recovery helper with a mocked read-only provider response in a temporary evidence
directory. It checks the concrete blocker, unchanged source and saved Review,
and that no recalculation starts. A mutation removing the resolver-action
rejection fails the concrete-reason assertion. This is characterization coverage
of the required refusal behavior, not a claim to have fixed or cleared the
missing capability.

Run it with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 automation/autocycle-fixes/test_excel_missing_verifier.py ~/.autocycle/excel_verification.py
```

AutoCycle's existing `test_excel_verification.py`, `test_excel_flow.py`, and
`test_excel_resume.py` cover copy substitution/source preservation, verification
failure, and automatic return to Review with a supplied mocked verifier. The
resume test resolves a command anew; it does **not** prove persistence of a
previously associated command. There is no suitable BAV verifier association to
test end to end in this case. Native Excel and real BAV cache acceptance were
not executed during this investigation.

The scope of this conclusion is semantic, not filename-specific: no company
matching, stale Action parsing, verifier-discovery framework, or configuration
system was introduced. No runtime fix is claimed in either project.

## Measured validation

- New missing-verifier harness against the installed helper: **1 passed**.
  A temporary mutant that ignored the resolver's missing-capability Action
  failed the concrete-reason assertion as intended.
- Existing AutoCycle `test_excel_verification.py`: **7 passed**.
- Focused BAV `python -m pytest core/tests/test_revenue_per_store.py
  core/tests/test_operating_kpi_workbook.py -q`: **50 passed**.
- Full BAV `python -m pytest core/tests -q`: **3,322 passed**, five SWIG-related
  deprecation warnings, 770.24 seconds. Interpreter:
  `/Users/lizhiguo/Documents/Developer/.venv/bin/python`.
- Full BAV log: `/private/tmp/bav-cached-verifier-full-tests.log`.
- Full AutoCycle `PYTHONDONTWRITEBYTECODE=1 python3 run_tests.py`, run from
  `/Users/lizhiguo/Documents/Developer/autocycle`: **all 25 Python regression
  scripts passed**, shell syntax checks and JavaScript response-parser tests
  passed. These use isolated repositories and mocked providers/Excel.
- Full AutoCycle log: `/private/tmp/autocycle-cached-verifier-full-tests.log`.
- The original workbook hash after the full BAV suite remains
  `27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67`, matching
  the pre-investigation Review/RESULT evidence.
