from pathlib import Path
import subprocess
import tempfile
import sys

controller=Path(sys.argv[1]).read_text()
start=controller.index('pause_if_requested() {')
end=controller.index('\n}\n',start)+3
function=controller[start:end]
for stage,should_pause in [('implement_done',False),('plan_done',False),('checkpoint_pending',False),('checkpoint_done',True)]:
    with tempfile.TemporaryDirectory() as raw:
        request=Path(raw)/'stop-request';request.mkdir()
        result=subprocess.run(['bash','-c',function+'\nSTAGE="$1"\nSTOP_REQUEST="$2"\nMODE=run\npause_if_requested\necho CONTINUED', 'test', stage,str(request)],capture_output=True,text=True)
        paused='CONTINUED' not in result.stdout
        assert paused==should_pause,(stage,result.stdout)
print('4 stop-boundary cases passed')
# Exercise the actual checkpoint-boundary block, with bookkeeping recorded before exit.
start=controller.index('    if [[ "$STAGE" == checkpoint_done ]]; then',controller.index('while (( RUN_CYCLE'))
end=controller.index('    if [[ "$STAGE" == boundary_input ]]; then',start)
block=controller[start:end]
with tempfile.TemporaryDirectory() as raw:
    request=Path(raw)/'stop-request';request.mkdir()
    script=function+'\nprogress() { echo BOOKKEEPING; }\nfail() { exit 1; }\nSTAGE=checkpoint_done\nMODE=run\nRUN_CYCLE=109\nRUN_MAX=120\nSTOP_REQUEST="$1"\nwhile true; do\n'+block+'\nbreak\ndone'
    result=subprocess.run(['bash','-c',script,'test',str(request)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert result.stdout.index('BOOKKEEPING')<result.stdout.index('Paused.')
    assert not request.exists()
# Exercise the real pre-checkpoint recovery branch without touching a repository.
start=controller.index('        implement_done)')
end=controller.index('\n            if ! (assert_owned_docs',start)
branch=controller[start:end]+'\n            ;;\n'
for dirty_flag,ancestor,success in [(False,True,True),(True,True,False),(False,False,False)]:
    script='''fail() { echo "FAILED: $1"; exit 1; }
head_sha() { echo manual_commit; }
save_state() { echo "SAVED:$STAGE:$CHECKPOINT_UNSAFE"; }
PLAN_SHA=baseline
IMPLEMENT_BASE_SHA=baseline
STAGE=implement_done
'''+f'dirty() {{ return {0 if dirty_flag else 1}; }}\ngit() {{ return {0 if ancestor else 1}; }}\n'+'while [[ "$STAGE" == implement_done ]]; do\ncase "$STAGE" in\n'+branch+'esac\ndone\n'
    result=subprocess.run(['bash','-c',script],capture_output=True,text=True)
    assert (result.returncode==0)==success,(dirty_flag,ancestor,result.stdout,result.stderr)
    if success:assert 'SAVED:checkpoint_done:1' in result.stdout
    else:assert 'SAVED:' not in result.stdout
print('Checkpoint bookkeeping order and 3 manual-checkpoint recovery cases passed')
