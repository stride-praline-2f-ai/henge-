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
latest=subprocess.check_output(["git","-C","build-request","ls-remote","origin","refs/heads/feature/duo-efficiency"],text=True).split()[0]
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
    signed = subprocess.run(['codesign', '-d', '--entitlements', ':-', str(app)], check=True, capture_output=True)
    entitlements = plistlib.loads(signed.stdout)
    requested = plistlib.loads(Path('Henge/ios/Henge/Henge.entitlements').read_bytes())
    for key, value in requested.items():
        assert entitlements.get(key) == value, 'Incorrect embedded entitlement: ' + key
    assert plist['HengeCustomSourceCommit'] == os.environ['GITHUB_SHA'], 'Wrong final implementation commit'
result=Path("Henge-output/Henge-build-verification.json")
data=json.loads(result.read_text())
data['packaging_validation'] = dict(architectures=architectures, ios_device_platform=True,
    nested_signature_verified=True, entitlement_values_verified=True,
    distribution_signing='ad hoc; installation tool must sign with its own supported profile')
state=json.loads(Path('build-request/henge-build/optimization-state.json').read_text())
data['optimization_validation'] = state.get('final_validation')
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
