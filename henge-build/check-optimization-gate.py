#!/usr/bin/env python3
"""Release-only gate. Compilation and focused validation do not require it."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
state = json.loads((root / 'optimization-state.json').read_text())
manifest = json.loads((root / 'manifest.json').read_text())
assert manifest['audit_repairs_sha256'] == hashlib.sha256((root / 'audit-repairs.patch').read_bytes()).hexdigest()
assert state.get('integrated_patch_sha256') == manifest['audit_repairs_sha256'], 'Requirements reconciled against a different implementation'
assert len(state['workstreams']) == 17, 'Missing required workstream'
pending = []
for item in state['workstreams'][:-1]:
    if item['state'] not in ('verified', 'verified_with_safe_alternative') or not item['changes'] or not item['evidence']:
        pending.append(item['name'])
    if item['state'] == 'verified_with_safe_alternative':
        assert item['exceptions'] and all(len(reason) > 80 for reason in item['exceptions']), item['name']
assert not pending, 'IPA blocked: incomplete workstreams: ' + '; '.join(pending)
assert state.get('final_reconciliation_complete') is True, 'Final requirements reconciliation has not been completed'
print('PASS complete implementation gate:', manifest['audit_repairs_sha256'])
