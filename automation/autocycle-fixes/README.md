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
