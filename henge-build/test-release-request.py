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

# Reproduce the real Actions depth-1 checkout. Ancestor pretty-printing and
# merge-base do not work here; exact frozen-tree comparison still must work.
import os
import shutil
import subprocess
import tempfile
with tempfile.TemporaryDirectory(prefix='henge-release-git-') as folder:
    root=Path(folder);origin=root/'origin';origin.mkdir()
    def git(where,*args):return subprocess.check_output(['git','-C',str(where),*args],text=True,stderr=subprocess.DEVNULL).strip()
    git(origin,'init');git(origin,'config','user.name','Henge test');git(origin,'config','user.email','test@example.invalid')
    build=origin/'henge-build';build.mkdir()
    shutil.copyfile(Path(__file__).with_name('read-release-request.py'),build/'read-release-request.py')
    import hashlib
    code=b'unchanged verified runtime patch';(build/'audit-repairs.patch').write_bytes(code)
    frozen=copy.deepcopy(manifest);frozen['audit_repairs_sha256']=hashlib.sha256(code).hexdigest()
    (build/'manifest.json').write_text(__import__('json').dumps(frozen));(origin/'engine.c').write_text('unchanged runtime')
    git(origin,'add','.');git(origin,'commit','-m','validated source');source_sha=git(origin,'rev-parse','HEAD')
    request=dict(release_requested=True,final_reconciliation_complete=True,integrated_patch_sha256=frozen['audit_repairs_sha256'],final_validation={'source_commit':source_sha})
    (build/'optimization-state.json').write_text(__import__('json').dumps(request));git(origin,'add','.');git(origin,'commit','-m','release metadata');release_sha=git(origin,'rev-parse','HEAD')
    request['release_retry']={'parent_commit':release_sha,'failed_run_id':43351975042,'reason':'Packaging-only repair with all validated runtime files unchanged; test the shallow checkout'}
    (build/'optimization-state.json').write_text(__import__('json').dumps(request));git(origin,'add','.');git(origin,'commit','-m','packaging retry')
    clone=root/'checkout';subprocess.run(['git','clone','--depth=1',origin.as_uri(),str(clone)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    output=root/'output';env={**os.environ,'GITHUB_OUTPUT':str(output)}
    subprocess.run(['python3',str(clone/'henge-build/read-release-request.py')],check=True,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    assert output.read_text().strip()=='requested=true'
    git(clone,'config','user.name','Henge test');git(clone,'config','user.email','test@example.invalid')
    (clone/'docs').mkdir();(clone/'docs/low-power-controls.md').write_text('Later documentation must not package again')
    git(clone,'add','.');git(clone,'commit','-m','later documentation');output.write_text('')
    subprocess.run(['python3',str(clone/'henge-build/read-release-request.py')],check=True,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    assert output.read_text().strip()=='requested=false'
print('PASS release request actual shallow Git checkout: missing validation tree fetched, raw parent accepted once, later documentation refused')
