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
assert runner.get('state') == 'removed_verified' and runner.get('evidence'), 'Runner removal needs executed migration/lifecycle proof'
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
    waiver=state.get('ui_preview_waiver',{})
    if waiver:
        assert waiver.get('source_commit')==validation.get('source_commit') and waiver.get('requested_by')=='user', 'UI waiver applies to another source'
        assert waiver.get('instruction')=='No need to do preview for ui as long as it’s working.', 'UI waiver needs the explicit user instruction'
        assert waiver.get('prior_visual_evidence'), 'Preserve the actual historical visual receipt separately'

session = state.get('session_responsiveness')
if manifest.get('session_responsiveness'):
    assert session and session.get('complete') is True, 'Reliable Instant Resume feature is incomplete'
    assert session.get('source_commit') == validation.get('source_commit'), 'Resume tests used another source'
    assert session.get('coordinator_tests') == 'passed' and session.get('native_lifecycle') == 'passed', 'Resume correctness checks incomplete'
    assert session.get('ios_integration') == 'passed' and session.get('evidence'), 'Resume application integration incomplete'
for feature in ('controller_posture', 'touchscreen_usb', 'disk_expansion'):
    if manifest.get(feature):
        proof=state.get(feature,{})
        assert proof.get('complete') is True and proof.get('evidence'), feature+' integration is incomplete'
        assert proof.get('source_commit') == validation.get('source_commit'), feature+' tests used another source'
core = state.get('core_efficiency_followup')
if core:
    assert core.get('state') == 'verified' and core.get('source_commit') == validation.get('source_commit'), 'Core efficiency follow-up needs exact-source regression proof'
    assert 'block completion: 64 ready requests / 1 wake;' in core.get('native_check_line',''), 'Missing executed block completion concurrency regression'
desktop=state.get('upstream_desktop')
if desktop:
    assert desktop.get('complete') and desktop.get('source_commit')==validation.get('source_commit'), 'Desktop PR integration requires exact-source native and graphics proof'
loading=state.get('loading_followup',{})
assert loading.get('complete') and loading.get('source_commit')==validation.get('source_commit'), 'Loading/Runner cleanup needs exact-source regression proof'
followup=state.get('ui_resume_clipboard_followup')
if followup:
    assert followup.get('complete') is True and followup.get('source_commit')==validation.get('source_commit'), 'UI/resume/clipboard follow-up needs exact-source proof'
    checks=('snapshot_pack','gpu_resource_copyback','clipboard_bridge','clipboard_companion','clipboard_delivery','coordinator','ios_integration')
    assert all(followup.get(k)=='passed' for k in checks), 'UI/resume/clipboard regression checks incomplete'
    assert followup.get('ui_previews')=='passed' or (followup.get('ui_previews')=='waived_by_user' and state.get('ui_preview_waiver',{}).get('source_commit')==validation.get('source_commit')), 'UI preview needs proof or explicit user waiver'
    assert followup.get('evidence'), 'UI/resume/clipboard evidence missing'
for name,checks in (
    ('engine_foundation_followup',('grouped_memory','faults','descriptor_reclamation','shader_budget')),
    ('input_resilience_followup',('host_encoder','transport','overflow','keyboard_ownership','pointer_model','desktop_layout','ios_sdk'))):
    feature=state.get(name,{})
    assert feature.get('complete') and feature.get('source_commit')==validation.get('source_commit'), name+' requires exact-source proof'
    assert all(feature.get(k)=='passed' for k in checks) and feature.get('evidence'), name+' correctness checks incomplete'

gpu=state.get('gpu_submission_followup',{})
if manifest.get('gpu_submission_followup'):
    assert gpu.get('complete') and gpu.get('source_commit')==validation.get('source_commit'), 'GPU follow-up requires exact-source integration proof'
    for key in ('state_reuse','pipeline_bundle','metal4_submission','memory_pressure','ordering_lifetime','settings'):
        assert gpu.get(key)=='passed_cloud', 'GPU follow-up incomplete: '+key
    hardware=gpu.get('hardware_validation',{})
    assert hardware.get('state') in ('passed','blocked'), 'Missing GPU execution verification state'
    if hardware.get('state')=='blocked':
        assert len(hardware.get('reason',''))>120 and isinstance(hardware.get('run_id'),int), 'Hardware execution blocker needs concrete runner evidence'
    assert gpu.get('evidence') and gpu.get('rejections'), 'NX18 adaptations and technical rejections need evidence'

print('PASS complete implementation gate:'  ,  manifest['audit_repairs_sha256'])
