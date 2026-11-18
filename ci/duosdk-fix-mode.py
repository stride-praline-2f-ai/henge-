#!/usr/bin/env python3
"""Dedicated reversible Fix Mode for fold/rotation compatibility experiments.

Three controlled SDK compatibility profiles use existing SDK Apply and verified
rollback. Fourth recovery route permits an *explicitly backed-up and verified*
original SDK without needing to read the installed binary, which previously
failed on device. Never bypasses parsing, changed-span, checksums, file
locking, snapshot, active-journal or cache structure validations.

This is experimental compatibility work, NOT a claim to force a different
app's rotation/scene via public iOS APIs.
"""
from pathlib import Path
import sys
src=Path(sys.argv[1]).resolve()/"Sources"

p=src/"XCacheTransaction.m"
s=p.read_text()
def once(old,new):
    global s
    assert s.count(old)==1,(old[:80],s.count(old))
    s=s.replace(old,new,1)

once('if (action < 0 || action > 5) return @"Unsupported action. No changes made.";',
     'if (action < 0 || action > 6) return @"Unsupported action. No changes made.";')

once('''if (action == 1 || action == 5) {
            BOOL recoverFromExecutable = action == 5;''',
     '''if (action == 1 || action == 5 || action == 6) {
            BOOL recoverFromExecutable = action == 5;
            BOOL userVerifiedBackup = action == 6;''')

once('''                NSString *identifier = [item isKindOfClass:NSString.class] ? item :
                    ([item isKindOfClass:NSDictionary.class] ? item[@"id"] : nil);
                NSArray *target = [item isKindOfClass:NSDictionary.class] ? item[@"after"] : @[@27,@2,@0];''',
     '''                if (userVerifiedBackup &&
                    (![item isKindOfClass:NSDictionary.class] ||
                     ![item[@"verifiedBackup"] isKindOfClass:NSNumber.class] ||
                     ![item[@"verifiedBackup"] boolValue]))
                    return @"Verified-backup recovery requires explicit confirmation "
                           @"and a SDK value obtained before the modification. No changes made.";
                NSString *identifier = [item isKindOfClass:NSString.class] ? item :
                    ([item isKindOfClass:NSDictionary.class] ? item[@"id"] : nil);
                NSArray *target = [item isKindOfClass:NSDictionary.class] ? item[@"after"] : @[@27,@2,@0];''')

once('''                if (!recoverFromExecutable &&
                    ([target[0] integerValue] != os.majorVersion ||
                     [target[1] integerValue] > os.minorVersion ||
                     ([target[1] integerValue] == os.minorVersion &&
                      [target[2] integerValue] > os.patchVersion)))''',
     '''                if (!recoverFromExecutable &&
                    ((!userVerifiedBackup && [target[0] integerValue] != os.majorVersion) ||
                     [target[0] integerValue] > os.majorVersion ||
                     ([target[0] integerValue] == os.majorVersion &&
                       ([target[1] integerValue] > os.minorVersion ||
                        ([target[1] integerValue] == os.minorVersion &&
                         [target[2] integerValue] > os.patchVersion)))))''')

once('''        if (action == 5)
            [report appendString:@"Verified installed executable SDK recovery: "
                                 @"no app binary or signature will be modified.\\n"];''',
     '''        if (action == 5)
            [report appendString:@"Verified installed executable SDK recovery: "
                                 @"no app binary or signature will be modified.\\n"];
        if (action == 6)
            [report appendString:@"Explicit user-verified prior SDK recovery. "
                                 @"The provided value has not been independently verified "
                                 @"by DuoSDK. This is a transactional cache adjustment, "
                                 @"not an executable patch.\\n"];''')

# Core binary-checksum transaction and validation untouched. Make this
# explicit in CI by asserting anchors still exist after patching.
assert 'lsRunBatch(dir,privateDir,folder,@"batch-upgrade-reverse"' in s
assert 'maintenanceCandidate(original, rows, folder, report, NO)' in s
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
def once(old,new):
    global s
    assert s.count(old)==1,(old[:80],s.count(old))
    s=s.replace(old,new,1)

once('''    @State private var showRawOutput = false''','''    @State private var showRawOutput = false
    @State private var showFixMode = false
    @State private var fixStrategy = "27.1.0"
    @State private var verifiedPriorSDK = ""
    @State private var verifiedBackupConfirmed = false
    @State private var confirmFixMode = false''')

ui=r'''
                Section {
                    DisclosureGroup("Fix Mode", isExpanded: $showFixMode) {
                        if let app = oneFixApp {
                            VStack(alignment: .leading, spacing: 3) {
                                Text(app.name).fontWeight(.semibold)
                                Text("LaunchServices currently records SDK \(app.fromVersion)")
                                    .font(.caption).foregroundStyle(.secondary)
                            }

                            Picker("Compatibility experiment", selection: $fixStrategy) {
                                Text("27.1: Full-display compatibility").tag("27.1.0")
                                Text("27.0: Reserved-edge compatibility").tag("27.0.0")
                                Text("Current iOS SDK").tag("system")
                                Text("Restore verified previous SDK").tag("prior")
                            }

                            if fixStrategy == "prior" {
                                TextField("SDK from pre-change backup, e.g. 26.5.0",
                                          text: $verifiedPriorSDK)
                                    .keyboardType(.numbersAndPunctuation)
                                    .textFieldStyle(.roundedBorder)
                                Toggle("I verified this SDK against a pre-change backup",
                                       isOn: $verifiedBackupConfirmed)
                                Text("DuoSDK cannot infer the original SDK from an already "
                                     + "overridden cache record. Do not guess this value.")
                                    .font(.caption).foregroundStyle(.secondary)
                            }

                            if let version = chosenFixVersion, version == app.before {
                                Text("This profile is already recorded. Writing identical "
                                     + "bytes cannot reliably refresh the app's scene.")
                                    .font(.caption).foregroundStyle(.secondary)
                            }

                            Button {
                                confirmFixMode = true
                            } label: {
                                Label(fixStrategy == "prior" ? "Restore verified SDK"
                                      : "Apply compatibility trial",
                                      systemImage: "wrench.adjustable")
                                    .fontWeight(.semibold)
                            }
                            .disabled(!fixIsValid)
                        } else {
                            Text("Select exactly one app above, then choose a recovery "
                                 + "strategy. Other apps will not be modified.")
                                .font(.callout).foregroundStyle(.secondary)
                        }
                        Text("Restart the whole iPhone after a successful change. "
                             + "Check outer landscape, inner direct launch, fold/unfold "
                             + "and returning from the app switcher. One change at a time.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                } footer: {
                    Text("Fix Mode tests compatibility strategies, not a guaranteed "
                         + "physical rotation override. Cache integrity checks stay on.")
                }

'''
once('''                if !selectedIDs.isEmpty {
                    Section {''',ui+'''                if !selectedIDs.isEmpty {
                    Section {''')

once('''            .confirmationDialog("Apply SDK changes?", isPresented: $confirmApply) {''',
     '''            .confirmationDialog("Apply this compatibility trial?",
                                isPresented: $confirmFixMode) {
                Button(fixStrategy == "prior" ? "Restore verified value" : "Apply trial",
                       role: .destructive) {
                    applyFixMode()
                }
            } message: {
                Text("Only the selected app's cached SDK metadata will be changed. "
                     + "This does not patch or rotate its executable. "
                     + "A full device restart is needed after a confirmed write.")
            }
            .confirmationDialog("Apply SDK changes?", isPresented: $confirmApply) {''')

needle='''    private func compactAppRow(_ item: DuoSDKCandidate) -> some View {'''
methods=r'''
    private var oneFixApp: DuoSDKCandidate? {
        guard selectedIDs.count == 1, let id = selectedIDs.first else { return nil }
        return candidates.first(where: { $0.id == id })
    }

    private func parseVerifiedSDK(_ raw: String) -> [Int]? {
        let fields = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            .split(separator: ".", omittingEmptySubsequences: false)
        guard (2...3).contains(fields.count),
              fields.allSatisfy({ !$0.isEmpty && $0.utf8.allSatisfy({ 48...57 ~= $0 }) }),
              let major = Int(fields[0]), let minor = Int(fields[1]),
              let patch = fields.count == 3 ? Int(fields[2]) : Optional(0),
              (1...99).contains(major), (0...99).contains(minor),
              (0...99).contains(patch)
        else { return nil }
        let os = ProcessInfo.processInfo.operatingSystemVersion
        guard major <= os.majorVersion,
              major < os.majorVersion ||
              (minor < os.minorVersion ||
               (minor == os.minorVersion && patch <= os.patchVersion))
        else { return nil }
        return [major, minor, patch]
    }

    private var chosenFixVersion: [Int]? {
        switch fixStrategy {
        case "prior":
            guard verifiedBackupConfirmed else { return nil }
            return parseVerifiedSDK(verifiedPriorSDK)
        case "system":
            let os = ProcessInfo.processInfo.operatingSystemVersion
            return [os.majorVersion, os.minorVersion, os.patchVersion]
        default:
            return parseSDK(fixStrategy)
        }
    }

    private var fixIsValid: Bool {
        guard let row = oneFixApp, let version = chosenFixVersion else { return false }
        return row.before != version
    }

    private func applyFixMode() {
        guard let app = oneFixApp, let version = chosenFixVersion,
              version != app.before, !working else {
            report = "Choose one app and a different verified SDK. Nothing changed."
            return
        }
        if fixStrategy != "prior" {
            targets[app.id] = version.map(String.init).joined(separator: ".")
            run(1)
            return
        }
        // The sandboxed app could not read the original executable on-device.
        // Explicit backup evidence replaces only that verification step, NOT
        // LaunchServices parsing, locking, checksum or transaction checks.
        guard verifiedBackupConfirmed else { return }
        let request: [[String: Any]] = [[
            "id": app.id,
            "after": version,
            "verifiedBackup": true
        ]]
        guard let json = try? JSONSerialization.data(withJSONObject: request),
              let payload = String(data: json, encoding: .utf8) else {
            report = "Could not encode verified recovery. Nothing changed."
            return
        }
        working = true
        Task {
            let value = await Task.detached(priority: .userInitiated) {
                DuoSDKMaintenanceForSelection(6, payload) ?? "No response from recovery engine."
            }.value
            report = value
            if value.contains("DUO_BATCH_APLICADO") {
                savedTargets.removeValue(forKey: app.id)
                persistPreferences()
            }
            candidates = []
            selectedIDs = []
            restoreCandidates = []
            restoreIDs = []
            working = false
            checkHeartbeat()
        }
    }

'''
once(needle,methods+needle)
assert '.confirmationDialog("Apply this compatibility trial?"' in s
assert 'private func applyFixMode()' in s
assert 'DuoSDKMaintenanceForSelection(6, payload)' in s
p.write_text(s)

print("Fix Mode: 27.0/27.1/current SDK trials plus explicit verified-backup recovery; "
      "existing transactional validators untouched.")
