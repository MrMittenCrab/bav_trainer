# Native Excel permission diagnosis (2026-09-20)

Status: permission boundary and repeated real native verification confirmed.
Reviewed source patch installed after all 27 AutoCycle regression scripts and
shell/JavaScript checks passed. Original BAV preserved.

## Measured boundaries

Excel 16.113.1 on this Mac has signed `com.apple.security.app-sandbox`,
`com.apple.security.files.user-selected.read-write`, and app/document-scoped
bookmark entitlements. This is distinct from macOS Automation authorization
for the calling process to send Apple events to Excel.

The installed `~/.autocycle/excel_verification.py::verify` calls `mkdtemp`
for every attempt and embeds that unique directory name in the workbook
basename. It copies the original with `shutil.copy2`, then passes only that new
copy to AppleScript. It never asks Excel to open the original. An existing
verifier command is required before the resume route reaches copy creation.

Probes used only the disposable workbook created by the existing native check,
not the BAV source. They reused the installed AppleScript with phase logging and
a 30-second Apple-event timeout. No dialogs were clicked by automation.

| Probe | Measured result |
| --- | --- |
| Activate Excel and read version, without workbook access | Exit 0, 0.160 seconds; version 16.113.1 |
| Reopen the exact previously saved disposable copy | Exit 0, 1.142 seconds; open identity confirmed, recalculated, saved, closed |
| Overwrite that copy in place from its uncached disposable source, reopen same path | Exit 0, 1.051 seconds; open identity confirmed, recalculated, saved, closed |
| New filename `new-sibling.xlsx` in the same directory | Exit 1 after 30.230 seconds; `OPEN_REQUESTED`, then `Excel open failed ... AppleEvent timed out. (-1712)`; no open-return, calculation, or save event |
| New file in another directory (`/private/tmp/excel-permission-diagnosis/elsewhere.xlsx`) | Exit 1 after 11.296 seconds: `Excel open failed ... Parameter error. (-50)`; recalculation and save not reached |

After the same-path content update, read-only inspection confirmed native
caches `Summary!A1=42`, `Summary!A2=43`, `Inputs!A1=21`. The external update
asserted the destination inode was preserved. Excel's own save changed the
inode, so stability means reusing the authorized path and updating it in place,
not assuming the inode stays constant through Excel saves.

Raw scripts and JSON results: `/private/tmp/excel-permission-diagnosis/`.
The authorized disposable path is recorded in each JSON result.

## Evidence limits and recommendation

The user reports a recurring Excel “Grant Access” prompt. Microsoft documents
Office sandbox file authorization and persistence for previously granted files:
https://learn.microsoft.com/en-us/office/vba/office-mac/grantaccesstomultiplefiles
Apple documents the separate file sandbox and bookmark mechanism:
https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox

The measured same-path success/new-file open timeout is consistent with that
mechanism. A timeout alone does not establish which dialog was displayed.
After the sibling probe, the user confirmed cancelling a Grant Access window.
This confirms a file-access dialog was pending at the measured open boundary.
The later elsewhere probe returned `-50`; that error code alone does not identify
a permission mechanism. No assertion of fully unattended operation across Excel
restarts is made.

The same-path reopen/update measurements support a stable, source-specific
verification path, updated in place, with separate per-attempt logs. Preserve
originals, avoid concurrent writes/open-workbook replacement, and retain an
immutable saved evidence snapshot for Review. Keep Automation denial distinct
from file-access denial and retain operation-specific timeout/error details.
Do not use UI clicks, disable sandboxing, or request Full Disk Access.

## Uncommitted work disposition

- Existing README addition, missing-verifier refusal test, and earlier verifier
  investigation: preserved as independent historical evidence. Their diagnosis
  concerns the resolver stopping before Excel, not the cause of file prompts.
- Interrupted-turn `scripts/verify_cached_workbook.py`, its six regression cases,
  and `docs/native-excel-kpi-references.json`: preserved and validated independently
  of the permission fix. After diagnosis, the read-only verifier passed on the
  real native-recalculated BAV twice. The exact invocation and results are now
  appended to `RESULT.md`; these changes supply acceptance, not a permission
  remedy.
- The fresh-Review provenance regression staged under
  `/private/tmp/excel-recovery-fix/runtime/test_excel_resume.py` reproduced a
  specific save failure being replaced with a stale manual-recalculation Action.
  It is now extended to permission cancellation and paired with a staged fix
  that carries matching recovery evidence into fresh Review.
- Existing substantial changes in the sibling AutoCycle repository predate this
  diagnostic. They were inspected and left intact. The installed helper and
  stage were not modified by this diagnostic.

## Validation

The BAV suite started before the interruption completed: 3,328 passed, five
warnings, 425.30 seconds. This includes the six new saved-cache tests and does
not prove permission-free native execution. Log:
`/private/tmp/bav-native-excel-full-tests.log`.

The unmodified baseline and final changed AutoCycle suites use fake providers
and mocked Excel: 25 and 27 Python scripts passed respectively, with shell and
JavaScript checks. Logs: `/private/tmp/autocycle-permission-baseline-tests.log`
and `/private/tmp/autocycle-stable-excel-install-tests.log`. The intermediate
`autocycle-stable-excel-full-tests.log` run was stopped for reviewed corrections
and is not used as final validation.

The original BAV SHA-256 remains
`27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67`.


## Staged implementation and its native verification limit

- Stable path: `<evidence-dir>/excel-workbooks/<SHA256-of-resolved-source-path[:24]>/autocycle-verification-<same-hash>.xlsx`.
- Update contents in place with `shutil.copyfile`; do not unlink/rename the
  authorized destination. Source identity is path-based, not content-based.
- Lock each source's stable slot through native calculation, verifier execution,
  and snapshot creation. Refuse aliases to the original and refuse to overwrite
  an already open verification copy.
- Native Excel still opens, calculates, saves and closes only the designated
  copy. The existing project verifier receives that same stable file path.
- Each completed verifier invocation retains an independent `saved-copy.xlsx`
  snapshot for Review, including nonzero verifier exit, alongside logs/hashes;
  later runs cannot overwrite that evidence.
- Resume results carry the reviewed revision and blocker key. A fresh Review
  receives matching evidence and retains its specific failure Action for the
  same unresolved blocker. Acceptance criteria and Review status are unchanged.

Before the initial access grant, the staged helper's first run against its new
disposable stable path returned
`Excel open failed ... Parameter error. (-50)` after 3.826 seconds. It did not
reach the verifier, and the planned second run was not executed. This is not
reported as successful native verification. Its exact result is preserved in
`/private/tmp/excel-permission-diagnosis/stable-run/excel-verification-e888sork/result.json`.
The user then clarified that access had not been granted during that attempt.

After rerunning for the initial grant, **both native runs passed**:

| Run | Elapsed | Native verifier | Evidence folder |
| --- | --- | --- | --- |
| First authorized run | 4.7909935 seconds | VERIFIED | `excel-verification-fikg5ox9` |
| Immediate second run | 1.7754353 seconds | VERIFIED | `excel-verification-0lrodpgv` |

Both used the same file:
`/private/tmp/excel-permission-diagnosis/stable-run/excel-workbooks/02c67849a424941f0855489f/autocycle-verification-02c67849a424941f0855489f.xlsx`.
Each native run recalculated/saved/closed it; the read-only verifier checked
`Summary!A1=42`, `Summary!A2=43`, `Inputs!A1=21` and the preserved formula.
The disposable source hash stayed
`6116f8f080e787ef269f9aedaa162e5bf4b9335fcd96718103191d0e8ccdef76`.
The runs retained distinct snapshots and result files. Their aggregate record:
`/private/tmp/excel-permission-diagnosis/stable-native-results.json`.
No security prompt was scripted. This demonstrates unattended reuse in the
current Excel session; permission persistence across application restart is
supported by Microsoft's documented bookmark behavior but was not separately
measured by quitting the user's Excel process.

## Final source patch and validation

The reviewed patch is archived at
`automation/autocycle-fixes/stable-excel-permissions.patch`. Only six files in
the sibling AutoCycle checkout were changed: helper, Review stage, README,
existing resume test, and two new regression scripts. Prior source versions are
backed up in `/private/tmp/autocycle-source-before-stable-excel-5ucskv0i`.
All unrelated runtime files were checked to match the installed versions before
invoking the existing installer. The installer preserves its own runtime backup.

Focused tests: 7 stable-path cases, 7 existing native-helper cases, 3 recovery
file/snapshot cases, and the existing missing-verifier refusal case all pass.
The provenance regression was observed failing on the stale Action before the
fix, then passing for save and verifier failure; final full suite additionally
covers permission cancellation. Code review found and verified fixes for failed
verifier snapshot retention and interrupted JSON records; unreadable newer
records cannot resurrect older successful verification.

Unmodified AutoCycle baseline: all **25 Python regression scripts** and shell/
JavaScript checks passed. Final modified suite now contains 27 Python scripts.
Installation/full-suite log:
`/private/tmp/autocycle-stable-excel-install-tests.log`. All 27 scripts passed,
including fresh Review preserving permission-cancellation, save, and verifier
failure Actions. Installer exit status: 0. Installed helper and stage hashes
match the reviewed manifest. Runtime backup:
`/Users/lizhiguo/.autocycle/backups/session-20260920-143857-918902`.



## Real BAV verification

The real source passed twice on its stable path after an expired access request
was cleared with a normal Excel restart (only after confirming zero workbooks).
The user reported no new Grant Access window on the successful attempts.
The prior normal macOS open request versus restart was not separately isolated;
no claim is made that either one alone granted file access. No force quit or
security-dialog automation was used, and automatic restart is not part of the
production helper.

First real success: `.git/autocycle/excel-verification-1a8_lsvq/result.json`.
Second real success: `.git/autocycle/excel-verification-kzg9a_ex/result.json`.
Both use the stable source-specific workbook with key
`5dc9d0038b5f6b7cfbc50b3c`. Both strict verifier reports check 50 independent
references and all affected/dependency caches, with formula/input preservation
across all sheets. The original BAV hash is unchanged. `RESULT.md` records exact
commands, snapshot hashes, and the retained limits of broader Completion.


The retained BAV verifier draft and its reference data also received independent
read-only code review: all 50 expectations recomputed from the cited anchors
matched, and all 33 affected formulas are covered; no important acceptance
weakness was found for this BAV surface. The original native blocker is being
re-adjudicated using the installed Review-only path and the immutable second
real-run result; its actual receipt remains in `.git/autocycle/current-review`
and the corresponding `review-*.log.answer`, rather than a fabricated Review
record. Broader Completion/Endpoint obligations remain for Review to judge.
