#!/usr/bin/env python3
"""Development export: update the cumulative patch and both integrity receipts.
Version plists are owned by integrate-upstream.sh, not context-sensitive hunks.
"""
import argparse
import hashlib
import json
import plistlib
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True, type=Path)
parser.add_argument('--base', help='Reviewed reconciled source commit before audit repairs')
args = parser.parse_args()
root = Path(__file__).resolve().parent
state = json.loads((root / 'optimization-state.json').read_text())
base = args.base or state['upstream_reconciled_baseline']
source = args.source.resolve()
managed = ['ios/Henge/Info.plist', 'ios/HengeJITHelper/Info.plist']
for name in managed:
    before = plistlib.loads(subprocess.check_output(['git', 'show', base + ':' + name], cwd=source))
    after = plistlib.loads((source / name).read_bytes())
    differences = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
    assert differences <= {'CFBundleVersion', 'CFBundleShortVersionString', 'NSMotionUsageDescription'}, 'Review metadata integration for: ' + name
patch = subprocess.check_output(['git', 'diff', '--binary', base, '--', '.', *[':(exclude)' + p for p in managed]], cwd=source)
(root / 'audit-repairs.patch').write_bytes(patch)
digest = hashlib.sha256(patch).hexdigest()
manifest = json.loads((root / 'manifest.json').read_text())
manifest['audit_repairs_sha256'] = digest
state['integrated_patch_sha256'] = digest
state['release_requested'] = False
state['final_reconciliation_complete'] = False
state['final_validation'] = {'patch_sha256': digest, 'native_regressions': 'pending', 'sanitizers': 'pending', 'ios_app_compile': 'pending'}
for name, data in [('manifest.json', manifest), ('optimization-state.json', state)]:
    (root / name).write_text(json.dumps(data, indent=2) + '\n')
print('Updated cumulative patch:', digest)
