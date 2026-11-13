#!/usr/bin/env python3
"""One-shot release and explicit packaging-only retry; runtime inputs stay frozen."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess

ALLOWED={
    'henge-build/manifest.json','henge-build/optimization-state.json',
    'docs/m4-optimisation/PROGRESS.md','docs/m4-optimisation/VALIDATION.md',
    'docs/m4-optimisation/CONTROLS-ADVANCED.md','docs/low-power-controls.md',
    'henge-build/verify-integrated-ipa.py','henge-build/read-release-request.py',
    'henge-build/test-release-request.py','henge-build/test-pairing-metadata.py','henge-build/integrate-upstream.sh',
    '.github/workflows/henge-ipa.yml','.github/workflows/henge-duo-checks.yml',
}
FROZEN=('henge_sha','husk_sha','patch_sha256','audit_repairs_sha256',
        'upstream_integration','app_version','app_build','m4_target')
def requested(state,parents,changed,manifest,validated,digest,metadata_safe=False):
    source=state.get('final_validation',{}).get('source_commit')
    if state.get('release_requested') is not True or state.get('final_reconciliation_complete') is not True or len(parents)!=1:return False
    retry=state.get('release_retry',{})
    normal=parents==[source]
    explicit_retry=(parents==[retry.get('parent_commit')] and isinstance(retry.get('failed_run_id'),int)
                    and len(retry.get('reason',''))>40)
    return bool((normal or explicit_retry) and set(changed)<=ALLOWED
                and ('henge-build/integrate-upstream.sh' not in changed or metadata_safe)
                and all(manifest.get(k)==validated.get(k) for k in FROZEN)
                and digest==manifest.get('audit_repairs_sha256')==state.get('integrated_patch_sha256'))

def pairing_metadata_only(before,after):
    # The sole permitted integration-script change on a frozen-source retry:
    # restore the existing JIT pairing capability, not any engine code.
    anchor='p["BGTaskSchedulerPermittedIdentifiers"]=["$(PRODUCT_BUNDLE_IDENTIFIER).pairing.*"]\n'
    repair='modes=list(p.get("UIBackgroundModes", []))\np["UIBackgroundModes"]=list(dict.fromkeys([*modes,"processing"]))\n'
    return before.count(anchor)==1 and after==before.replace(anchor,anchor+repair)

def main():
    root=Path(__file__).resolve().parent;repo=root.parent
    state=json.loads((root/'optimization-state.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
    source=state.get('final_validation',{}).get('source_commit');answer=False
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    if state.get('release_requested') and source:
        assert re.fullmatch(r'[0-9a-f]{40}',source), 'Invalid validation source'
        # Pretty-format %P hides parents at a shallow boundary. Raw commit
        # objects retain them; fetch just the validated tree for a frozen diff.
        parents=re.findall(r'^parent ([0-9a-f]{40})$',git('cat-file','-p','HEAD'),re.M)
        available=subprocess.run(['git','-C',str(repo),'cat-file','-e',source+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not available:subprocess.run(['git','-C',str(repo),'fetch','--no-tags','--depth=1','origin',source],check=True)
        changed=git('diff','--name-only',source,'HEAD').splitlines()
        validated=json.loads(git('show',source+':henge-build/manifest.json'))
        digest=hashlib.sha256((root/'audit-repairs.patch').read_bytes()).hexdigest()
        metadata_ok=True
        script='henge-build/integrate-upstream.sh'
        if script in changed:
            metadata_ok=pairing_metadata_only(git('show',source+':'+script),(repo/script).read_text().strip())
        answer=metadata_ok and requested(state,parents,changed,manifest,validated,digest,metadata_safe=metadata_ok)
    with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('requested='+str(answer).lower()+'\n')
    print('Explicit integrated IPA request:',answer,'validated source:',source)
if __name__=='__main__':main()
