#!/usr/bin/env python3
"""Validate the actual packaged IPA contains pinned merged upstream and selected PRs."""
import hashlib
import json
import os
import plistlib
import subprocess
import zipfile
import tempfile
from pathlib import Path
release_manifest=json.loads(Path("build-request/henge-build/manifest.json").read_text())
release_branch=release_manifest.get("release_branch", "feature/duo-efficiency")
latest=subprocess.check_output(["git","-C","build-request","ls-remote","origin","refs/heads/"+release_branch],text=True).split()[0]
assert latest==os.environ["GITHUB_SHA"], "Superseded source must not publish a release artifact"
manifest=json.loads(Path("build-request/henge-build/manifest.json").read_text())
integration=manifest["upstream_integration"]
ipa=Path(os.environ["HENGE_IPA_OUTPUT"])
assert ipa.is_file(), "IPA was not produced"
with zipfile.ZipFile(ipa) as z:
    assert z.testzip() is None, "Corrupt IPA archive"
    plist=plistlib.loads(z.read("Payload/Henge.app/Info.plist"))
    app_executable=z.read("Payload/Henge.app/"+plist["CFBundleExecutable"])
assert plist.get("HengeAuditRepairsSHA256")==manifest["audit_repairs_sha256"], "Incorrect audit repairs"
assert plist.get("HengeSnapshotSchema")==3, "Incorrect snapshot schema"
assert plist['CFBundleShortVersionString'] == manifest['app_version'], 'Unexpected app version'
assert plist['CFBundleVersion'] == manifest['app_build'], 'Unexpected app build'
if manifest.get('m4_optimisation'):
    with zipfile.ZipFile(ipa) as archive:
        binary = archive.read('Payload/Henge.app/Henge')
    for marker in (b'M4 iPad16,5 ten-core/16GB', b'CAMetalDisplayLink', b'power-state-changed'):
        assert marker in binary, 'Missing integrated M4 runtime marker: ' + repr(marker)
if manifest.get('controls_power'):
    with zipfile.ZipFile(ipa) as archive:
        binary=archive.read('Payload/Henge.app/Henge')
    for marker in (b'controls-only peer authenticated; no encoder, decoder or second display',
                   b'BEGIN 30s; aggregate process CPU', b'invalid store action tag %u (%u bytes)'):
        assert marker in binary, 'Missing controls/power runtime marker: '+repr(marker)
    assert b'runner CPU background=%d; GPU rings retained' not in binary, 'Removed Runner gate remains linked'
    assert 'processing' in plist.get('UIBackgroundModes', []), 'Existing JIT pairing requires processing capability'
    permitted=plist.get('BGTaskSchedulerPermittedIdentifiers', [])
    assert permitted == [plist['CFBundleIdentifier']+'.pairing.*'], 'Only JIT pairing background tasks are permitted'
if manifest.get('loading_followup'):
    for marker in (b'kernel read cache order=', b'gpu-pipeline-archives:',
                   b'Removed Runner mode and retired experimental UI overrides'):
        assert marker in app_executable, 'Missing loading follow-up: '+repr(marker)
if manifest.get('controller_posture'):
    assert plist.get('NSMotionUsageDescription'), 'Motion usage description missing'
    # Swift strings of <=15 UTF-8 bytes can be encoded in ARM64 immediates.
    # Verify the real sensor API selectors and long runtime data instead.
    markers=(b'startDeviceMotionUpdatesToQueue:withHandler:', b'stopDeviceMotionUpdates',
             b'Motion unavailable; joystick steering restored', b'Henge Link primary mirror snapshot',
             b'Controller layout', b'Safe filesystem cloning failed', b'Touchpad movement speed')
    missing=[repr(marker) for marker in markers if marker not in binary]
    assert not missing, 'Missing new release runtime markers: '+', '.join(missing)
    assert manifest['native_touch']['ad_hoc_guest_launch_supported'] is True
    assert 'CoreHID' in manifest['native_touch']['signing_requirement']
sdk=plist.get('DTSDKName', '')
assert sdk.startswith('iphoneos') and tuple(int(x) for x in sdk[8:].split('.')) >= (27, 1), 'Duo fullscreen requires iOS 27.1+ SDK'

with zipfile.ZipFile(ipa) as z:
    assert b"hv_snapshot_test_fail_after" not in z.read("Payload/Henge.app/Henge"), "Test-only failure hook in release"
assert plist.get("HengeMergedUpstreamCommit")==integration["main_sha"], "Incorrect upstream source"
assert plist.get("HengeIntegratedPullRequests")==[p["number"] for p in integration["pull_requests"]], "Incorrect merged PR IDs"
assert plist.get("HengeIntegratedPullRequestHeads")==[p["sha"] for p in integration["pull_requests"]], "Incorrect merged PR heads"
# Inspect what was actually archived, including the embedded extension/framework.
with zipfile.ZipFile(ipa) as z:
    for name in z.namelist():
        assert not name.startswith('/') and '..' not in Path(name).parts, 'Unsafe archive member'
with tempfile.TemporaryDirectory(prefix='henge-ipa-check-') as directory:
    subprocess.run(['ditto', '-x', '-k', str(ipa.resolve()), directory], check=True)
    app = Path(directory) / 'Payload/Henge.app'
    helper = app / 'PlugIns/HengeJITHelper.appex'
    framework = app / 'Frameworks/StikJIT.framework'
    helper_info = plistlib.loads((helper / 'Info.plist').read_bytes())
    framework_info = plistlib.loads((framework / 'Info.plist').read_bytes())
    assert helper_info['CFBundleIdentifier'] == plist['CFBundleIdentifier'] + '.JITHelper'
    assert helper_info['CFBundleVersion'] == plist['CFBundleVersion'], 'JIT helper build version mismatch'
    assert helper_info['CFBundleShortVersionString'] == plist['CFBundleShortVersionString'], 'JIT helper version mismatch'
    assert helper_info.get('NSExtension'), 'Missing JIT extension registration'
    assert framework_info.get('CFBundleIdentifier') and framework_info['CFBundlePackageType'] == 'FMWK'
    assert int(helper_info['MinimumOSVersion'].split('.')[0]) >= 26
    architectures = {}
    for binary in (app / 'Henge', helper / 'HengeJITHelper', framework / 'StikJIT'):
        arch = subprocess.check_output(['lipo', '-archs', str(binary)], text=True).split()
        assert 'arm64' in arch and all(a in ('arm64', 'arm64e') for a in arch), (binary.name, arch)
        commands = subprocess.check_output(['otool', '-l', str(binary)], text=True)
        # LC_BUILD_VERSION platform 2 is an iOS device, not simulator (7) or macOS (1).
        import re
        platforms = re.findall(r'cmd LC_BUILD_VERSION\s+cmdsize \d+\s+platform (\S+)', commands)
        assert [x.upper() for x in platforms] in (['2'], ['IOS']) or ('cmd LC_VERSION_MIN_IPHONEOS' in commands and not platforms), binary.name
        architectures[str(binary.relative_to(app))] = arch
    linked=subprocess.check_output(['otool','-L',str(app/'Henge')],text=True)
    assert '/CoreMotion.framework/' in linked, 'Gyro framework not linked in actual application'
    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
    guest_helpers=json.loads(subprocess.check_output(['python3','Henge/tools/verify_native_touch_package.py',str(app/'henge-touch-agent.tar.gz')],text=True))
    signed = subprocess.run(['codesign', '-d', '--entitlements', ':-', str(app)], check=True, capture_output=True)
    entitlements = plistlib.loads(signed.stdout)
    requested = plistlib.loads(Path('Henge/ios/Henge/Henge.entitlements').read_bytes())
    for key, value in requested.items():
        assert entitlements.get(key) == value, 'Incorrect embedded entitlement: ' + key
    assert plist['HengeCustomSourceCommit'] == os.environ['GITHUB_SHA'], 'Wrong final implementation commit'
result=Path("Henge-output/Henge-build-verification.json")
data=json.loads(result.read_text())
data['guest_usb_companions']=guest_helpers
data['packaging_validation'] = dict(architectures=architectures, ios_device_platform=True,
    nested_signature_verified=True, entitlement_values_verified=True, core_motion_linked=True,
    distribution_signing='ad hoc; installation tool must sign with its own supported profile')
state=json.loads(Path('build-request/henge-build/optimization-state.json').read_text())
data['optimization_validation'] = state.get('final_validation')
# New engine/input code must be present in the actual device archive, beyond
# the native source test receipt. Keep physical-device claims separate.
for feature in ('engine_foundation_followup','input_resilience_followup'):
    proof=state.get(feature,{})
    assert proof.get('complete') and proof.get('source_commit')==state['final_validation']['source_commit'], feature+' is not validated'
    data[feature]=dict(proof,runtime_markers_verified=True,physical_performance_verified=False)
for marker in (b'hostEncoding',b'ignored_button_edges=',b'mouse_delivered=',b'Apply M4 Automatic (Desktop Retina)',b'Touchscreen connecting'):
    assert marker in app_executable, 'Missing engine/input/layout runtime: '+repr(marker)
followup=state['ui_resume_clipboard_followup']
assert followup['complete'] and followup['source_commit']==state['final_validation']['source_commit']
assert followup['ui_previews'] in ('passed','waived_by_user')
for marker in (b'A Mac when you need it. Your devices, connected.',b'Universal Clipboard also works',b'not confirmed the clipboard',b'snapshot: memory allocation reduced workers'):
    assert marker in app_executable, 'Missing resume/clipboard runtime: '+repr(marker)
data['ui_resume_clipboard_followup']=dict(followup,runtime_markers_verified=True)
if manifest.get('m4_optimisation'):
    data['m4_optimisation'] = dict(manifest['m4_optimisation'],
        runtime_markers_verified=True, physical_energy_verified=False,
        physical_gaming_verified=False, implementation=state['m4_implementation'])
if manifest.get('controls_power'):
    data['controls_power']=dict(manifest['controls_power'], runtime_markers_verified=True, background_metadata_verified=True, physical_controller_verified=False, app_runner_removed=True)
if manifest.get('loading_followup'):
    data['loading_followup']=dict(manifest['loading_followup'],runtime_markers_verified=True,
        source_validation=state['final_validation']['source_commit'],physical_performance_verified=False)
if manifest.get('upstream_desktop'):
    desktop=state['upstream_desktop']
    assert desktop.get('complete') and desktop.get('source_commit')==state['final_validation']['source_commit']
    executable=app_executable
    for marker in (b'jit-ring:',b'saved pipelines:',b'v3-pipelines-',b'henge.planar.owner',b'pipeline archive bypass',b'Recovery copy verification failed; original disk preserved',b'Finish macOS volume expansion'):
        assert marker in executable,'Missing desktop optimisation runtime: '+repr(marker)
    data['upstream_desktop']=dict(manifest['upstream_desktop'],runtime_markers_verified=True,
        source_validation=desktop['source_commit'],physical_performance_verified=False)
# The final diagnostic archive must contain this review, not an earlier IPA.
review=state.get('project_review',{})
assert review.get('complete') and review.get('source_commit')==state['final_validation']['source_commit']
markers=(b'Process headroom when opened',b'hengevm.network-events',b'jit-publication:',
         b'native-touch-metrics:',b'hvprof-jit-word:',b'Continuous test diagnostics: entire visible session',
         b'cumulative measured I/O; worker durations can overlap',b'setupHeartbeat')
missing=[repr(marker) for marker in markers if marker not in app_executable]
assert not missing,'Missing review runtime markers: '+', '.join(missing)
hooks=(b'_hv_vm_test_network_token',b'_hv_vm_test_network_apply')
assert all(hook not in app_executable for hook in hooks),'Network test hooks leaked into production'
assert plist.get('HengeTestDiagnostics') is manifest.get('test_diagnostics') is True
for marker in review['required_markers']:
    assert any(marker in line for line in review['native_check_lines']),marker
# Keep the actual iOS image's symbols outside the distributable IPA. They turn
# ASLR-independent profiler offsets into exact functions for this source build.
product=Path('Henge/ios/build/DerivedData/Build/Products/Release-iphoneos')
image=product/'Henge.app/Henge'
import re
image_uuid=subprocess.check_output(['xcrun','dwarfdump','--uuid',str(image)],text=True)
image_ids=re.findall(r'UUID: ([0-9A-Fa-f-]+) \(arm64\)',image_uuid)
with tempfile.TemporaryDirectory(prefix='henge-symbols-') as directory:
    packaged=Path(directory)/'Henge'
    packaged.write_bytes(app_executable)
    packaged_uuid=subprocess.check_output(['xcrun','dwarfdump','--uuid',str(packaged)],text=True)
    packaged_ids=re.findall(r'UUID: ([0-9A-Fa-f-]+) \(arm64\)',packaged_uuid)
    assert image_ids and image_ids==packaged_ids,'Packaged image differs from compiled image'
    # This build retains the native symbol table. Read directly from the
    # archived executable so code offsets cannot refer to a stale dSYM.
    symbols=subprocess.check_output(['xcrun','nm','-arch','arm64','-n',str(packaged)],text=True)
assert len(symbols.splitlines())>100 and '_hv_helper' in symbols,'No actionable native symbols'
symbol_file=ipa.parent/'Henge-symbols.txt'
symbol_file.write_text('Source '+os.environ['GITHUB_SHA']+'\n'+image_uuid+'\n'+symbols)
data['diagnostic_symbols']={'uuid_matched':True,'uuid':image_ids[0],
    'file':symbol_file.name,'sha256':hashlib.sha256(symbol_file.read_bytes()).hexdigest()}
data['project_review']=dict(review,runtime_markers_verified=True,test_hooks_absent=True,
    physical_touch_fps_energy_verified=False)
follow=state.get('desktop_memory_touch_followup',{})
assert follow.get('complete') and follow.get('source_commit')==state['final_validation']['source_commit']
for marker in (b'native-touch-recovery:',b'native-touch-guest-error:',b'gpu-cache-budget:',b'henge: memory-layout:',b'Process headroom excludes some guest pages'):
    assert marker in app_executable,'Desktop follow-up runtime missing: '+repr(marker)
assert b'_hv_native_touch_test_time' not in app_executable,'Test clock leaked into production'
data['desktop_memory_touch_followup']=dict(follow,runtime_markers_verified=True,test_clock_absent=True)
gpu=state.get('gpu_submission_followup',{})
assert gpu.get('complete') and gpu.get('source_commit')==state['final_validation']['source_commit']
for marker in (b'metal4-first-guest:',b'metal4-fallback-counts:',b'metal4-runtime:',b'gpu-binding-cache:',b'setArgumentTable:atStages:',b'newMTL4CommandQueueWithDescriptor:error:'):
    assert marker in app_executable,'Missing real Metal4 runtime: '+repr(marker)
with zipfile.ZipFile(ipa) as archive:
    base='Payload/Henge.app/HengePipelines/'
    bundle=json.loads(archive.read(base+'index.json'))
    assert bundle['schema']==1
    assert {e['gpu'] for e in bundle['archives']}==set(manifest['gpu_submission_followup']['bundle_gpus'])
    for entry in [bundle['screen_library'],*bundle['archives']]:
        assert Path(entry['file']).name==entry['file']
        content=archive.read(base+entry['file'])
        assert hashlib.sha256(content).hexdigest()==entry['sha256'],'Incorrect bundled pipeline hash'
    assert all(e['platform']=='ios' and e['os_major']==27 for e in bundle['archives'])
data['gpu_submission_followup']=dict(gpu,runtime_markers_verified=True,pipeline_bundle_verified=True,physical_performance_verified=False)
# Correct legacy metadata: verify the real configured default in the reconstructed source.
assert 'as? Bool ?? true' in Path('Henge/ios/Henge/EngineTuning.swift').read_text()
data['fastmem_default']=True
data["audit_repairs"]={"sha256":manifest["audit_repairs_sha256"],"snapshot_schema":3,"test_allocation_hook_absent":True}
data["upstream_integration"]={
  **integration,
  "verified_in_packaged_ipa": True,
  "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
  "device_thermal_or_battery_gain_verified": False
}
state['workstreams'][-1].update(state='verified', changes=['Final integrated device IPA archive inspected'],
    evidence=['Actions run ' + os.environ['GITHUB_RUN_ID'], 'Source ' + os.environ['GITHUB_SHA'],
              'arm64 iOS platform, bundle metadata, nested signatures, entitlement values and cumulative patch markers verified'])
state['final_artifact'] = dict(source_commit=os.environ['GITHUB_SHA'], run_id=int(os.environ['GITHUB_RUN_ID']),
    ipa_sha256=data['upstream_integration']['ipa_sha256'], filename=ipa.name)
state['release_requested'] = False
(ipa.parent / 'Henge-optimization-completion.json').write_text(json.dumps(state,indent=2)+'\n')
result.write_text(json.dumps(data,indent=2)+"\n")
print("Verified packaged source markers:",integration["main_sha"],integration["pull_requests"])
