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
validation = state.get('final_validation', {})
assert validation.get('patch_sha256') == manifest['audit_repairs_sha256'], 'Final checks used another patch'
assert validation.get('native_regressions') == 'passed' and validation.get('sanitizers') == 'passed', 'Native correctness checks incomplete'
assert validation.get('ios_app_compile') == 'passed', 'Full iOS app compilation incomplete'
assert isinstance(validation.get('run_id'), int) and len(validation.get('source_commit', '')) == 40, 'Missing traceable validation source'
runner = state.get('runner_mode', {})
assert runner.get('state') == 'verified' and runner.get('evidence'), 'Runner-mode validation incomplete'
m4 = state.get('m4_implementation')
if m4 is not None:
    assert m4.get('complete') is True and all(x.get('state') in ('verified', 'verified_with_safe_alternative') and x.get('evidence') for x in m4['workstreams']), 'M4 engineering gate incomplete'
print('PASS complete implementation gate:',  manifest['audit_repairs_sha256'])
