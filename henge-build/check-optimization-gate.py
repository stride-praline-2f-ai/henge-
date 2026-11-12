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
controls = state.get('controls_power')
if controls is not None:
    assert controls.get('complete') is True and all(x.get('state') in ('verified', 'verified_with_safe_alternative') and x.get('evidence') for x in controls.get('workstreams', [])), 'Controls/power engineering gate incomplete'
advanced = state.get('advanced_controls')
if manifest.get('advanced_controls'):
    assert advanced and advanced.get('complete') is True, 'Advanced controls integration is incomplete'
    assert advanced.get('source_commit') == validation.get('source_commit'), 'Controller tests used another source'
    assert advanced.get('native_protocol') == 'passed' and advanced.get('swift_input') == 'passed', 'Controller correctness checks incomplete'
    profiles=advanced.get('simulator_profiles')
    assert profiles in ({'duo-unfolded':'passed','m4-13':'passed'}, {'duo-unfolded':'passed_layout_fixture','m4-13':'passed'}), 'Required controller layout tests incomplete'
    if profiles['duo-unfolded']=='passed_layout_fixture':
        blocked=advanced.get('native_duo_validation',{})
        assert blocked.get('state')=='blocked' and len(blocked.get('reason',''))>120, 'Native Duo limitation must be concrete'
        assert all(isinstance(blocked.get(k),int) for k in ('run_id','job_id','artifact_id')), 'Missing failed native Duo evidence'
        assert advanced.get('screenshots_inspected') is True, 'Unfolded viewport needs visual verification'
    assert isinstance(advanced.get('preview_run_id'), int), 'Missing traceable controller preview run'
session = state.get('session_responsiveness')
if manifest.get('session_responsiveness'):
    assert session and session.get('complete') is True, 'Reliable Instant Resume feature is incomplete'
    assert session.get('source_commit') == validation.get('source_commit'), 'Resume tests used another source'
    assert session.get('coordinator_tests') == 'passed' and session.get('native_lifecycle') == 'passed', 'Resume correctness checks incomplete'
    assert session.get('ios_integration') == 'passed' and session.get('evidence'), 'Resume application integration incomplete'
print('PASS complete implementation gate:' ,  manifest['audit_repairs_sha256'])
