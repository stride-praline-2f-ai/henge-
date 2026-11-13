"""Protect one-shot release requests and source freezing on a packaging retry."""
import copy
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('release',Path(__file__).with_name('read-release-request.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
source='a'*40;failed='b'*40;digest='c'*64
state=dict(release_requested=True,final_reconciliation_complete=True,integrated_patch_sha256=digest,final_validation={'source_commit':source})
manifest={key:key for key in m.FROZEN};manifest['audit_repairs_sha256']=digest
assert m.requested(state,[source],['henge-build/optimization-state.json'],manifest,manifest,digest)
assert not m.requested(state,[failed],['docs/low-power-controls.md'],manifest,manifest,digest)
retry=copy.deepcopy(state);retry['release_retry']={'parent_commit':failed,'failed_run_id':43351975042,'reason':'IPA verifier reads an expired temporary path after packaging; app source unchanged'}
assert m.requested(retry,[failed],['henge-build/verify-integrated-ipa.py'],manifest,manifest,digest)
for parents in [[],[source,failed],['d'*40]]:assert not m.requested(retry,parents,[],manifest,manifest,digest)
for path in ['henge-build/audit-repairs.patch','henge-build/henge.patch','ios/Henge/Native/henge-vm.c','henge-build/integrate-upstream.sh']:
    assert not m.requested(retry,[failed],[path],manifest,manifest,digest)
for key in m.FROZEN:
    changed=copy.deepcopy(manifest);changed[key]='changed';assert not m.requested(retry,[failed],[],changed,manifest,digest)
assert not m.requested(retry,[failed],[],manifest,manifest,'wrong')
retry['release_requested']=False;assert not m.requested(retry,[failed],[],manifest,manifest,digest)
print('PASS release request: one-shot parent, explicit failed packaging retry, frozen source/pins/version/patch and permitted paths')
