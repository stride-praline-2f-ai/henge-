#!/usr/bin/env python3
"""Validate the actual packaged IPA contains pinned merged upstream and selected PRs."""
import hashlib
import json
import os
import plistlib
import subprocess
import zipfile
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
with zipfile.ZipFile(ipa) as z:
    assert b"hv_snapshot_test_fail_after" not in z.read("Payload/Henge.app/Henge"), "Test-only failure hook in release"
assert plist.get("HengeMergedUpstreamCommit")==integration["main_sha"], "Incorrect upstream source"
assert plist.get("HengeIntegratedPullRequests")==[p["number"] for p in integration["pull_requests"]], "Incorrect merged PR IDs"
assert plist.get("HengeIntegratedPullRequestHeads")==[p["sha"] for p in integration["pull_requests"]], "Incorrect merged PR heads"
result=Path("Henge-output/Henge-build-verification.json")
data=json.loads(result.read_text())
data["audit_repairs"]={"sha256":manifest["audit_repairs_sha256"],"snapshot_schema":3,"test_allocation_hook_absent":True}
data["upstream_integration"]={
  **integration,
  "verified_in_packaged_ipa": True,
  "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
  "device_thermal_or_battery_gain_verified": False
}
result.write_text(json.dumps(data,indent=2)+"\n")
print("Verified packaged source markers:",integration["main_sha"],integration["pull_requests"])
