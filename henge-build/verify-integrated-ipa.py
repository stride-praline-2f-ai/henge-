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
    for marker in (b'runner CPU background=%d; GPU rings retained',
                   b'controls-only peer authenticated; no encoder, decoder or second display',
                   b'BEGIN 30s; aggregate process CPU', b'invalid store action tag %u (%u bytes)'):
        assert marker in binary, 'Missing controls/power runtime marker: '+repr(marker)
    assert 'processing' in plist.get('UIBackgroundModes', []), 'CPU continued-processing background mode missing'
    permitted=plist.get('BGTaskSchedulerPermittedIdentifiers', [])
    bundle=plist['CFBundleIdentifier']
    for suffix in ('.runner.cpu','.runner.session'):
        assert any(value==bundle+suffix or (value.endswith('.*') and (bundle+suffix).startswith(value[:-1])) for value in permitted), 'Runner task ID not permitted: '+suffix
if manifest.get('controller_posture'):
    assert plist.get('NSMotionUsageDescription'), 'Motion usage description missing'
    for marker in (b'henge.gyro.lock', b'Henge Link primary mirror snapshot', b'Controller layout',
                   b'Safe filesystem cloning failed', b'Touchpad movement speed'):
        assert marker in binary, 'Missing new release runtime: '+repr(marker)
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
    nested_signature_verified=True, entitlement_values_verified=True,
    distribution_signing='ad hoc; installation tool must sign with its own supported profile')
state=json.loads(Path('build-request/henge-build/optimization-state.json').read_text())
data['optimization_validation'] = state.get('final_validation')
if manifest.get('m4_optimisation'):
    data['m4_optimisation'] = dict(manifest['m4_optimisation'],
        runtime_markers_verified=True, physical_energy_verified=False,
        physical_gaming_verified=False, implementation=state['m4_implementation'])
if manifest.get('controls_power'):
    data['controls_power']=dict(manifest['controls_power'], runtime_markers_verified=True, background_metadata_verified=True, physical_controller_verified=False, physical_cpu_background_verified=False)
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
