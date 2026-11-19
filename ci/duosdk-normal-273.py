#!/usr/bin/env python3
"""Expose SDK 27.3.0 clearly in the NORMAL app list and Apply UI.

The prior ci/duosdk-sdk273-apply-fix.py has already:
* enabled 27.3.0 parsing in the regular SDK editor;
* routed single-app normal Apply to narrowly scoped action 7;
* checked the prior active recovery record against the live cache;
* preserved original rollback SDK for verified chained adjustments.

Do not modify or bypass that code here. This patch only makes the regular
editor faster and clearer for the user's requested 27.3 experiment.
"""
from pathlib import Path
import sys

src=Path(sys.argv[1]).resolve()/"Sources"
p=src/"XCacheTransaction.m"
engine=p.read_text()
for marker in (
    'experimentalSDK273',
    'duoSameRecordExceptSDK(original, earlierCandidate, sdkOffset)',
    'maintenanceCandidate(original, rows, folder, report, NO)',
    'duoSaveAppliedSession(support,identifier,rows)',
):
    assert marker in engine, ("Missing integrity/history anchor", marker)
# The normal UI routes 27.3 to the existing guarded action-7 writer.
p=src/"App.swift"
s=p.read_text()
for marker in ('let experimental273 =', 'let actualAction =',
               'DuoSDKMaintenanceForSelection(actualAction, payload)'):
    assert marker in s, ("Missing normal Apply integration", marker)

old='''                    Text("Set SDK").font(.caption)
                    TextField("27.2.0", text: Binding('''
new='''                    Text("Set SDK").font(.caption)
                    TextField("27.3.0", text: Binding('''
assert s.count(old)==1, "SDK target text field has changed"
s=s.replace(old,new,1)

old='''                    .frame(maxWidth: 110)
                    Spacer()
                    if let saved = savedTargets[item.id] {'''
new='''                    .frame(maxWidth: 110)
                    if ProcessInfo.processInfo.operatingSystemVersion.majorVersion == 27 &&
                       ProcessInfo.processInfo.operatingSystemVersion.minorVersion == 2 {
                        Button("Use 27.3") { targets[item.id] = "27.3.0" }
                            .font(.caption)
                    }
                    Spacer()
                    if let saved = savedTargets[item.id] {'''
assert s.count(old)==1, "SDK quick target insert has changed"
s=s.replace(old,new,1)

old='''                        Text("An SDK adjustment can affect app compatibility. "
                             + "It does not guarantee working rotation or fullscreen.")'''
new='''                        Text("SDK 27.3.0 is experimental on iOS 27.2.x. "
                             + "It does not install iOS 27.3 or guarantee a rotation fix.")'''
assert s.count(old)==1, "Regular Apply footer has changed"
s=s.replace(old,new,1)

assert 'private var canApply: Bool' in s
assert 'Undo recorded changes' in s
assert 'DuoSDKMaintenanceForSelection(7, payload)' in s
p.write_text(s)
print("Normal app list exposes a one-tap 27.3.0 SDK target. "
      "Existing single-app Apply and verified history checks are unchanged.")
