#!/usr/bin/env python3
"""Add an explicit SDK 27.3.0 trial to DuoSDK Fix Mode.

iOS 27.3 is in beta; an app's LaunchServices SDK tag is not an OS update.
Ordinary Apply and user-verified backup recovery keep their original bounds.
A dedicated action 7 permits ONLY SDK 27.3.0 and ONLY on iOS 27.2/27.3,
with a fresh validated single-app record and the existing transactional writer.
No other cache verification or signing logic is altered.
"""
from pathlib import Path
import sys
src = Path(sys.argv[1]).resolve() / "Sources"

p = src / "XCacheTransaction.m"
s = p.read_text()
def once(a,b):
    global s
    assert s.count(a)==1, (a[:80],s.count(a))
    s=s.replace(a,b,1)

once('if (action < 0 || action > 6) return @"Unsupported action. No changes made.";',
     'if (action < 0 || action > 7) return @"Unsupported action. No changes made.";')

once('''if (action == 1 || action == 5 || action == 6) {
            BOOL recoverFromExecutable = action == 5;
            BOOL userVerifiedBackup = action == 6;''',
     '''if (action == 1 || action == 5 || action == 6 || action == 7) {
            BOOL recoverFromExecutable = action == 5;
            BOOL userVerifiedBackup = action == 6;
            BOOL experimentalSDK273 = action == 7;''')

old='''                if (!recoverFromExecutable &&
                    ((!userVerifiedBackup && [target[0] integerValue] != os.majorVersion) ||
                     [target[0] integerValue] > os.majorVersion ||
                     ([target[0] integerValue] == os.majorVersion &&
                       ([target[1] integerValue] > os.minorVersion ||
                        ([target[1] integerValue] == os.minorVersion &&
                         [target[2] integerValue] > os.patchVersion)))))'''
new='''                // No broad higher-than-installed SDK exemption: action 7
                // accepts only exactly 27.3.0 on an iOS 27.2/27.3 device.
                if (experimentalSDK273 &&
                    !(os.majorVersion == 27 &&
                      (os.minorVersion == 2 || os.minorVersion == 3) &&
                      [target isEqual:@[@27,@3,@0]]))
                    return @"SDK 27.3 trial requires iOS 27.2/27.3 and exactly "
                           @"27.3.0 as its target. Nothing changed.";
                if (!experimentalSDK273 && !recoverFromExecutable &&
                    ((!userVerifiedBackup && [target[0] integerValue] != os.majorVersion) ||
                     [target[0] integerValue] > os.majorVersion ||
                     ([target[0] integerValue] == os.majorVersion &&
                       ([target[1] integerValue] > os.minorVersion ||
                        ([target[1] integerValue] == os.minorVersion &&
                         [target[2] integerValue] > os.patchVersion)))))'''
once(old,new)

# All writes still go through the existing per-app path and verified history.
marker='''        if (action == 6)
            [report appendString:@"Explicit user-verified prior SDK recovery. "
                                 @"The provided value has not been independently verified "
                                 @"by DuoSDK. This is a transactional cache adjustment, "
                                 @"not an executable patch.\\n"];'''
assert s.count(marker)==1
s=s.replace(marker,marker+'''
        if (action == 7)
            [report appendString:@"Experimental SDK 27.3.0 tag on installed iOS. "
                                 @"This does not install iOS 27.3, its APIs or "
                                 @"guarantee app rotation.\\n"];''',1)

assert 'maintenanceCandidate(original, rows, folder, report, NO)' in s
assert 'lsRunBatch(dir,privateDir,folder,@"batch-upgrade-reverse"' in s
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
def once(a,b):
    global s
    assert s.count(a)==1,(a[:80],s.count(a))
    s=s.replace(a,b,1)
once('''                                Text("27.1: Full-display compatibility").tag("27.1.0")''',
     '''                                Text("27.1: Full-display compatibility").tag("27.1.0")
                                Text("27.3 beta SDK tag (experimental)").tag("27.3.0")''')
once('''        case "system":
            let os = ProcessInfo.processInfo.operatingSystemVersion
            return [os.majorVersion, os.minorVersion, os.patchVersion]''',
     '''        case "system":
            let os = ProcessInfo.processInfo.operatingSystemVersion
            return [os.majorVersion, os.minorVersion, os.patchVersion]
        case "27.3.0":
            let os = ProcessInfo.processInfo.operatingSystemVersion
            guard os.majorVersion == 27 &&
                  (os.minorVersion == 2 || os.minorVersion == 3) else { return nil }
            return [27, 3, 0]''')
once('''        if fixStrategy != "prior" {
            selectedIDs = Set([app.id])
            targets[app.id] = version.map(String.init).joined(separator: ".")
            run(1)
            return
        }''',
     '''        if fixStrategy == "27.3.0" {
            apply273Trial(to: app, version: version)
            return
        }
        if fixStrategy != "prior" {
            selectedIDs = Set([app.id])
            targets[app.id] = version.map(String.init).joined(separator: ".")
            run(1)
            return
        }''')
needle='''    private func compactAppRow(_ item: DuoSDKCandidate) -> some View {'''
methods=r'''
    private func apply273Trial(to app: DuoSDKCandidate, version: [Int]) {
        // Action 7 is deliberately distinct from ordinary SDK editor Apply,
        // whose installed-OS upper limit remains in place.
        guard !working, version == [27, 3, 0] else { return }
        let request: [[String: Any]] = [[
            "id": app.id,
            "after": version
        ]]
        guard let bytes = try? JSONSerialization.data(withJSONObject: request),
              let payload = String(data: bytes, encoding: .utf8) else {
            report = "Unable to prepare 27.3 trial. Nothing changed."
            return
        }
        working = true
        Task {
            let value = await Task.detached(priority: .userInitiated) {
                DuoSDKMaintenanceForSelection(7, payload) ?? "No result from SDK 27.3 trial."
            }.value
            report = value
            if value.contains("DUO_BATCH_APLICADO") {
                savedTargets[app.id] = "27.3.0"
                persistPreferences()
                candidates = []
                selectedIDs = []
                restoreCandidates = []
                restoreIDs = []
            }
            working = false
            checkHeartbeat()
        }
    }

'''
assert s.count(needle)==1
s=s.replace(needle,methods+needle,1)
needle='''                            if fixStrategy == "prior" {
                                TextField("SDK from pre-change backup, e.g. 26.5.0",'''
assert s.count(needle)==1
s=s.replace(needle,'''                            if fixStrategy == "27.3.0" {
                                Text("On iOS 27.2.x this is a newer-than-installed "
                                     + "SDK tag experiment. It does not install iOS 27.3, "
                                     + "add APIs or guarantee a layout/rotation fix.")
                                    .font(.caption).foregroundStyle(.secondary)
                            }

                            if fixStrategy == "prior" {
                                TextField("SDK from pre-change backup, e.g. 26.5.0",''',1)

assert 'DuoSDKMaintenanceForSelection(7, payload)' in s
assert 'Text("27.3 beta SDK tag (experimental)")' in s
p.write_text(s)
print("SDK 27.3.0 single-app compatibility trial enabled, with original guards elsewhere unchanged.")
