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

All four original Step 7.4 captures failed in `confirm_view` with
`Unexpected active document (-2700)` after a successful position of the owned
slot. The pre-repair helper compared AppleScript object specifiers
(`active workbook is not targetDoc`). That comparison is not path identity and
can fail for the owned `excel-view.xlsx` slot.

[active-document-confirmation.patch](active-document-confirmation.patch)
replaces specifier equality with POSIX-path identity, records expected and
observed paths, and rejects blank, same-name/different-path and lost-ownership
cases. That specifier repair is already installed in the authenticated
runtime (SHA-256 `0db3faee…`). Worksheet, Word selection, open-return
ownership and lock checks stay unchanged.

## Identity-reply serialization

The four Step 7.4.2 replacements then failed with
`Active document identity unavailable: malformed identity reply` and produced
no images. The installed producer returns
`expectedId & tab & observedId & tab & bounds` from inside
`tell application "Microsoft Excel"`. Excel.sdef defines class `tab`
(code `Xtab`, sheet tab). Application terminology takes precedence inside
that tell block, so `tab` is not AppleScript ASCII 9. An Office-free
`«class Xtab»` concatenation survives osascript/`stdout.strip()` as a single
field and the consumer's `split('\\t')` raises the receipt error. Unshadowed
AppleScript `tab` does survive the same transport; the defect is the Excel
tell-block identifier, not generic osascript tab stripping.

[identity-reply-serialization.patch](identity-reply-serialization.patch)
keeps POSIX-path identity and changes only the producer/consumer delimiter to
the quoted sentinel `<<AC>>`. Missing, malformed, ambiguous, legacy
tab-separated and `Xtab` replies fail closed. Isolated regressions apply the
serialization patch to a temporary copy of the authenticated runtime and
cover the real osascript boundary (no Office, no capture):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 automation/autocycle-fixes/test_active_document_confirmation.py
```

Prior 21 passing isolated tests validated specifier identity against mocked
replies; they do not validate this serialization repair. The patches remain
reviewable artifacts. `install.py` refuses while a live `autocycle --resume`
process is running; this provider does not stop or restart the controller
and does not modify the installed or maintained helpers. Subsequent
production capture still requires Review to authorize a recovery route.
