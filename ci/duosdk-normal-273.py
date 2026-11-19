#!/usr/bin/env python3
"""Permit the experimental 27.3.0 tag via normal per-app SDK Apply.

Runs after the separate action-7 27.3 trial patch. Preserves the normal
UI selection, standard Apply action (1), backup journal, verified transactional
cache writer and per-app Undo. Allow only *exactly* 27.3.0 as a future SDK tag
on installed iOS 27.2.x. No blanket forward-SDK bypass.

Also remove the contradictory artificial journal guard that blocked updating
an already-adjusted app from e.g. 27.2 to 27.3; an existing valid previous
session is superseded ONLY after Apply succeeds, as already implemented by
duosdk-workspace-v2.py.
"""
from pathlib import Path
import sys
src=Path(sys.argv[1]).resolve()/"Sources"

p=src/"XCacheTransaction.m"
s=p.read_text()
old='''                if (!experimentalSDK273 && !recoverFromExecutable &&
                    ((!userVerifiedBackup && [target[0] integerValue] != os.majorVersion) ||'''
new='''                BOOL normalApply273 =
                    action == 1 && os.majorVersion == 27 && os.minorVersion == 2 &&
                    [target isEqual:@[@27,@3,@0]];
                if (!experimentalSDK273 && !normalApply273 && !recoverFromExecutable &&
                    ((!userVerifiedBackup && [target[0] integerValue] != os.majorVersion) ||'''
assert s.count(old)==1, ("Engine SDK guard anchor",s.count(old))
s=s.replace(old,new,1)

old='''        for (NSDictionary *row in rows) for (NSDictionary *previous in known) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]] &&
                [previous[@"after"] isEqual:row[@"before"]])
                return @"This app still has an active restore record. Restore or choose another app first.";
        }'''
new='''        // A previous successful SDK adjustment is not a reason to refuse
        // another selected SDK change. The candidate still uses a fresh
        // database snapshot, byte/offset/checksum verification and locked
        // transaction. duoSaveAppliedSession supersedes the former active
        // journal entry ONLY after a confirmed write.
        // An unreadable journal is already rejected immediately above.'''
assert s.count(old)==1, ("Sequential journal guard",s.count(old))
s=s.replace(old,new,1)

# Keep proof that the original record validation, batch transaction and
# confirmed-success journal write are still in the built source.
for token in ('maintenanceCandidate(original, rows, folder, report, NO)',
              'lsRunBatch(dir,privateDir,folder,@"batch-upgrade-reverse"',
              'duoSaveAppliedSession(support,identifier,rows)'):
    assert token in s, token
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
old='''        guard major == os.majorVersion,
              minor <= os.minorVersion,
              minor != os.minorVersion || patch <= os.patchVersion
        else { return nil }
        return [major, minor, patch]'''
new='''        // Ordinary Apply accepts one tightly scoped future SDK experiment.
        // The tag does not install the SDK or enable missing iOS APIs.
        let normalInstalledVersion =
            major == os.majorVersion &&
            minor <= os.minorVersion &&
            (minor != os.minorVersion || patch <= os.patchVersion)
        let beta273Trial =
            major == 27 && minor == 3 && patch == 0 &&
            os.majorVersion == 27 && os.minorVersion == 2
        guard normalInstalledVersion || beta273Trial else { return nil }
        return [major, minor, patch]'''
assert s.count(old)==1, ("Swift SDK parse anchor",s.count(old))
s=s.replace(old,new,1)

old='''                    Text("Set SDK").font(.caption)
                    TextField("27.2.0", text: Binding('''
new='''                    Text("Set SDK").font(.caption)
                    TextField("27.3.0", text: Binding('''
assert s.count(old)==1, ("SDK row input",s.count(old))
s=s.replace(old,new,1)

old='''                    .frame(maxWidth: 110)
                    Spacer()
                    if let saved = savedTargets[item.id] {'''
new='''                    .frame(maxWidth: 110)
                    if ProcessInfo.processInfo.operatingSystemVersion.majorVersion == 27 &&
                        ProcessInfo.processInfo.operatingSystemVersion.minorVersion == 2 {
                        Button("Use 27.3") {
                            targets[item.id] = "27.3.0"
                        }
                        .font(.caption)
                    }
                    Spacer()
                    if let saved = savedTargets[item.id] {'''
assert s.count(old)==1, ("Quick preset SDK UI",s.count(old))
s=s.replace(old,new,1)

old='''                        Text("An SDK adjustment can affect app compatibility. "
                             + "It does not guarantee working rotation or fullscreen.")'''
new='''                        Text("An SDK adjustment can affect app compatibility. "
                             + "27.3.0 is an experimental SDK tag on iOS 27.2, not "
                             + "an OS update or a guaranteed rotation fix.")'''
assert s.count(old)==1, ("Normal Apply UI footer",s.count(old))
s=s.replace(old,new,1)
assert 'private var canApply: Bool' in s
assert 'if action == 1 && !canApply { return }' in s
assert 'DuoSDKMaintenanceForSelection(action, payload)' in s
p.write_text(s)
print("Normal app editor / Apply / Undo now supports 27.3.0 on iOS 27.2.x. "
      "Sequential verified SDK adjustments remain reversible; integrity checks unchanged.")
