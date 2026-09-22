# AutoCycle cycle-boundary stop fix

`cycle-stop.patch` records the bounded change installed in `~/bin/autocycle`.
It is not applied by BAV. It changes controller code, never repository runtime
state. The original installed script was backed up to
`/private/tmp/autocycle-before-current-build-fix` during this intervention.

Normal `--stop` requests are consumed after checkpoint bookkeeping, before cycle
increment/input rollover. Manual single-stage commands retain their explicit
single-stage boundaries. The original behavior consumed requests at the top of
every controller iteration, including `implement_done` before checkpoint.

A clean descendant commit already made by the user is preserved and routed to
the existing opening Review through `checkpoint_done` with `CHECKPOINT_UNSAFE=1`.
Dirty work and non-descendant commits fail closed. The subsequent normal Review
and publication, ancestry and protected-document guards still apply before Plan.
This is recovery routing, not acceptance of the implementation or manual edits.

Regression harness (extracts and executes the installed shell branches with
isolated stop directories and stubbed bookkeeping/Git; never launches AutoCycle):

```bash
python automation/autocycle-fixes/test_cycle_stop.py ~/bin/autocycle
bash -n ~/bin/autocycle
```

The harness tests four stage boundaries, bookkeeping-before-pause, clean manual
checkpoint recovery, and dirty/non-descendant rejection. Do not run the original
controller against production runtime state to reproduce the bug.

After the user checkpoints/publishes this BAV intervention normally, the fixed
controller can resume the saved cycle through opening Review. No controller
restart, runtime-state rewrite, cycle allocation, or checkpoint is performed by
this fix or by the BAV build workflow.

## Cached-value verifier investigation

See [the investigation](../../docs/excel-verifier-investigation-2026-09-20.md)
for why the current Excel recovery blocker has no suitable existing verifier.
No production workaround was installed. The isolated missing-verifier regression
uses the real helper with a mocked resolver and never invokes Excel:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 automation/autocycle-fixes/test_excel_missing_verifier.py ~/.autocycle/excel_verification.py
```


## Stable native-Excel permissions

See [the permission diagnosis](../../docs/excel-permission-diagnosis-2026-09-20.md)
for measured same-path reuse, per-file Grant Access, and prior-edit disposition.
[stable-excel-permissions.patch](stable-excel-permissions.patch) records the
reviewed AutoCycle source changes relative to the pre-diagnosis working tree;
it does not replace unrelated AutoCycle work. The existing installer runs the
full mocked suite and backs up the installed runtime before updating it.

## Active-document confirmation

All four Step 7.4 captures failed in `confirm_view` with
`Unexpected active document (-2700)` after a successful position of the owned
slot. The installed helper compares AppleScript object specifiers
(`active workbook is not targetDoc`). That comparison is not path identity and
can fail for the owned `excel-view.xlsx` slot.

[active-document-confirmation.patch](active-document-confirmation.patch)
replaces specifier equality with POSIX-path identity, records expected and
observed paths, and rejects blank, same-name/different-path and lost-ownership
cases. Worksheet, Word selection, open-return ownership and lock checks stay
unchanged. Isolated regressions (no Office, no capture):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 automation/autocycle-fixes/test_active_document_confirmation.py
```

The patch is a reviewable repair artifact. `install.py` refuses while a live
`autocycle --resume` process is running; this provider does not stop or
restart the controller. Subsequent production capture still requires Review
to authorize a recovery route.
