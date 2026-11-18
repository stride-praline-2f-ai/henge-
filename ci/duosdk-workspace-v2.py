#!/usr/bin/env python3
"""DuoSDK workspace v2: editable per-app SDK tags, full validated app inventory,
saved opt-in preferences, stale preference detection and selective restoration.
Applied after the existing historical backup patch. No automatic system writes.
"""
from pathlib import Path
import sys

src=Path(sys.argv[1]).resolve()/"Sources"

p=src/"XCacheTransaction.m"
s=p.read_text()

# Current version hardcodes 27.2 and accepts only old records. Treat per-app
# versions as untrusted until matched against the parser's fresh live cache.
needle='if (action < 0 || action > 3) return @"Unsupported action. No changes made.";'
assert s.count(needle)==1
s=s.replace(needle,'if (action < 0 || action > 3) return @"Unsupported action. No changes made.";')

needle='NSArray *rows = DuoSDKPlan(original, [NSSet setWithArray:tracked], &matched);'
assert s.count(needle)==1
s=s.replace(needle,'NSArray *rows = DuoSDKPlanAll(original, [NSSet setWithArray:tracked], &matched);')

needle='''            NSMutableSet<NSString *> *wanted = [NSMutableSet set];
            for (id item in requested) {
                if (![item isKindOfClass:NSString.class] || [item length] == 0 ||
                    [item length] > 255 || [wanted containsObject:item])
                    return @"Invalid or duplicate app selection. No changes made.";
                [wanted addObject:item];
            }
            NSMutableArray<NSDictionary *> *filtered = [NSMutableArray array];
            for (NSDictionary *row in rows)
                if ([wanted containsObject:row[@"id"]]) [filtered addObject:row];
            if (filtered.count != wanted.count)
                return @"Selected apps no longer qualify. Review again. No changes made.";
            rows = filtered;'''
assert s.count(needle)==1
replacement='''            NSMutableSet<NSString *> *wanted = [NSMutableSet set];
            NSMutableDictionary<NSString *, NSArray *> *targets = [NSMutableDictionary dictionary];
            for (id item in requested) {
                NSString *identifier = [item isKindOfClass:NSString.class] ? item :
                    ([item isKindOfClass:NSDictionary.class] ? item[@"id"] : nil);
                NSArray *target = [item isKindOfClass:NSDictionary.class] ? item[@"after"] : @[@27,@2,@0];
                if (![identifier isKindOfClass:NSString.class] || identifier.length == 0 ||
                    identifier.length > 255 || [wanted containsObject:identifier] ||
                    ![target isKindOfClass:NSArray.class] || target.count != 3)
                    return @"Invalid or duplicate app selection. Nothing changed.";
                for (NSUInteger i = 0; i < 3; ++i) {
                    if (![target[i] isKindOfClass:NSNumber.class] ||
                        [target[i] unsignedLongLongValue] > 99 ||
                        (i == 0 && [target[i] unsignedLongLongValue] == 0))
                        return @"Invalid target SDK. No changes made.";
                }
                if ([target[0] integerValue] != os.majorVersion ||
                    [target[1] integerValue] > os.minorVersion ||
                    ([target[1] integerValue] == os.minorVersion &&
                     [target[2] integerValue] > os.patchVersion))
                    return @"Target SDK must use an installed iOS SDK release. Nothing changed.";
                [wanted addObject:identifier];
                targets[identifier] = target;
            }
            NSMutableArray<NSDictionary *> *filtered = [NSMutableArray array];
            for (NSDictionary *row in rows) {
                if ([wanted containsObject:row[@"id"]]) {
                    NSArray *target = targets[row[@"id"]];
                    if ([target isEqual:row[@"before"]])
                        return @"An app is already using the chosen SDK. Review again. No changes made.";
                    NSMutableDictionary *adjusted = [row mutableCopy];
                    adjusted[@"after"] = target;
                    [filtered addObject:adjusted];
                }
            }
            if (filtered.count != wanted.count)
                return @"Selected apps are no longer available. Review again. No changes made.";
            rows = filtered;'''
s=s.replace(needle,replacement,1)

needle='''        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"];
            [report appendFormat:@"• %@ · %@.%@ → 27.2\\n", row[@"name"], before[0], before[1]];
        }'''
assert s.count(needle)==1
s=s.replace(needle,'''        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"], *after = row[@"after"];
            [report appendFormat:@"• %@ · %@.%@.%@ → %@.%@.%@\\n",
                row[@"name"], before[0], before[1], before[2],
                after[0], after[1], after[2]];
        }''')

# The batch validator is still strict about byte differences, offsets and the
# cached plan; only upgrade-path permitted SDK triples are now configurable.
needle='''        if (!lsSDKMatches(newSDK, @[@27, targetMinor, @0]) ||
            oldSDK[0] == 0 || oldSDK[0] > 27 || (oldSDK[0] == 27 && oldSDK[8] >= maximumOldMinor)) return nil;'''
assert s.count(needle)==1
s=s.replace(needle,'''        BOOL configurable = targetMinor.unsignedIntegerValue == 2 && maximumOldMinor == 2;
        if (configurable) {
            // Both complete SDK triples already matched the live/target records
            // above. Never permit a no-op transaction or arbitrary bytes.
            if ([row[@"before"] isEqual:row[@"after"]]) return nil;
        } else if (!lsSDKMatches(newSDK, @[@27, targetMinor, @0]) ||
                   oldSDK[0] == 0 || oldSDK[0] > 27 ||
                   (oldSDK[0] == 27 && oldSDK[8] >= maximumOldMinor)) return nil;''')

# The restore history should be capable of returning user-defined SDK targets.
needle='''            ![entry[@"offset"] isEqual:current[@"offset"]] ||
            ![entry[@"after"] isEqual:@[@27,@2,@0]])'''
assert s.count(needle)==1
s=s.replace(needle,'''            ![entry[@"offset"] isEqual:current[@"offset"]])''')

# Allow an app that was updated/reinstalled to receive a fresh saved adjustment,
# without treating its now-stale previous state as a recoverable original.
needle='''        for (NSDictionary *row in rows) for (NSDictionary *previous in known) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]])
                return @"This app already has an active restore record. Review restore history first.";
        }'''
assert s.count(needle)==1
s=s.replace(needle,'''        for (NSDictionary *row in rows) for (NSDictionary *previous in known) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]] &&
                [previous[@"after"] isEqual:row[@"before"]])
                return @"This app still has an active restore record. Restore or choose another app first.";
        }''')

needle='''        for (NSDictionary *previous in history) {
            if ([previous[@"active"] boolValue] && [previous[@"id"] isEqualToString:row[@"id"]])
                return NO; // Never allow ambiguous active histories for one app.
        }
        [history addObject:@{@"id":row[@"id"], @"name":row[@"name"] ?: row[@"id"],'''
assert s.count(needle)==1
s=s.replace(needle,'''        // Supersede only after Apply succeeded. Older records remain in the
        // journal, but are no longer offered as if they still match the cache.
        for (NSUInteger idx = 0; idx < history.count; ++idx) {
            NSDictionary *previous = history[idx];
            if ([previous[@"active"] boolValue] && [previous[@"id"] isEqualToString:row[@"id"]]) {
                NSMutableDictionary *past = [previous mutableCopy];
                past[@"active"] = @NO;
                past[@"supersededAt"] = time;
                history[idx] = past;
            }
        }
        [history addObject:@{@"id":row[@"id"], @"name":row[@"name"] ?: row[@"id"],''')

# Older SDK default targets are still the original 27.2.0, but the user's
# individual target is now copied from each validated row.
assert 'maintenanceCandidate(live, reverseRows, folder, report, YES)' in s

p.write_text(s)

# SwiftUI. No background reapplication; user opt-in is mandatory every time.
p=src/"App.swift"
s=p.read_text()
start=s.index("private struct DuoSDKView: View {")
ui=r'''
private struct DuoSDKView: View {
    @State private var report = ""
    @State private var working = false
    @State private var candidates: [DuoSDKCandidate] = []
    @State private var selectedIDs: Set<String> = []
    @State private var restoreCandidates: [DuoSDKRestoreCandidate] = []
    @State private var restoreIDs: Set<String> = []
    @State private var search = ""
    @State private var targets: [String: String] = [:]
    @State private var savedTargets: [String: String] =
        UserDefaults.standard.dictionary(forKey: "duosdk.preferredSDK.v1") as? [String: String] ?? [:]
    @State private var confirmApply = false
    @State private var confirmRestore = false

    private var filtered: [DuoSDKCandidate] {
        candidates.filter {
            search.isEmpty ||
            $0.name.localizedStandardContains(search) ||
            $0.id.localizedStandardContains(search)
        }
    }
    private var older: [DuoSDKCandidate] {
        filtered.filter { $0.before.count == 3 &&
            ($0.before[0] < 27 || ($0.before[0] == 27 && $0.before[1] < 1))
        }.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
    }
    private var remaining: [DuoSDKCandidate] {
        filtered.filter { $0.before.count == 3 &&
            !($0.before[0] < 27 || ($0.before[0] == 27 && $0.before[1] < 1))
        }.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
    }
    private var changedPreferences: [DuoSDKCandidate] {
        candidates.filter { item in
            guard let chosen = savedTargets[item.id],
                  let version = parseSDK(chosen) else { return false }
            return version != item.before
        }.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
    }

    private func parseSDK(_ value: String) -> [Int]? {
        let raw = value.trimmingCharacters(in: .whitespacesAndNewlines)
        let pieces = raw.split(separator: ".", omittingEmptySubsequences: false)
        guard (2...3).contains(pieces.count),
              pieces.allSatisfy({ !$0.isEmpty && $0.utf8.allSatisfy({ 48...57 ~= $0 }) }),
              let major = Int(pieces[0]), let minor = Int(pieces[1]),
              let patch = pieces.count == 3 ? Int(pieces[2]) : Optional(0),
              (1...99).contains(major), (0...99).contains(minor),
              (0...99).contains(patch) else { return nil }
        let os = ProcessInfo.processInfo.operatingSystemVersion
        guard major == os.majorVersion,
              minor <= os.minorVersion,
              minor != os.minorVersion || patch <= os.patchVersion
        else { return nil }
        return [major, minor, patch]
    }
    private func target(_ item: DuoSDKCandidate) -> String {
        targets[item.id] ?? savedTargets[item.id] ?? "27.2.0"
    }
    private var changes: [[String: Any]] {
        selectedIDs.sorted().compactMap { id -> [String: Any]? in
            guard let item = candidates.first(where: { $0.id == id }),
                  let version = parseSDK(target(item)),
                  version != item.before else { return nil }
            return ["id": id, "after": version]
        }
    }
    private var canApply: Bool {
        !selectedIDs.isEmpty && changes.count == selectedIDs.count
    }
    private func persistPreferences() {
        UserDefaults.standard.set(savedTargets, forKey: "duosdk.preferredSDK.v1")
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Button("Scan recognised apps") { run(0) }
                    Button("Choose apps to restore") { run(3) }
                } footer: {
                    Text("Scanning is read-only. Applying changes to the system cache always requires an explicit selection and confirmation.")
                }

                if !changedPreferences.isEmpty {
                    Section {
                        ForEach(changedPreferences) { item in
                            Button {
                                targets[item.id] = savedTargets[item.id] ?? "27.2.0"
                                selectedIDs.insert(item.id)
                            } label: {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(item.name).fontWeight(.medium)
                                    Text("Current \(item.fromVersion) · preferred \(savedTargets[item.id] ?? "")")
                                        .font(.caption).foregroundStyle(.secondary)
                                    Text("Select to queue your previously preferred SDK")
                                        .font(.caption2).foregroundStyle(.secondary)
                                }
                            }
                        }
                    } header: {
                        Text("Saved adjustments needing review")
                    } footer: {
                        Text("App or iOS updates may reset cached SDK tags. DuoSDK will never silently reapply them.")
                    }
                }
                if !older.isEmpty {
                    Section("SDK below 27.1") {
                        ForEach(older) { appRow($0) }
                    }
                }
                if !remaining.isEmpty {
                    Section("SDK 27.1 and newer") {
                        ForEach(remaining) { appRow($0) }
                    }
                }
                if !candidates.isEmpty {
                    Section {
                        Button("Apply to \(selectedIDs.count) selected app(s)") {
                            confirmApply = true
                        }
                        .disabled(!canApply)
                    } footer: {
                        Text("Enter a target such as 27.1 or 27.2.1, up to your installed iOS version. An invalid or unchanged target cannot be applied.")
                    }
                }
                if !restoreCandidates.isEmpty {
                    Section {
                        ForEach(restoreCandidates) { item in
                            Toggle(isOn: Binding(
                                get: { restoreIDs.contains(item.id) },
                                set: { on in
                                    if on { restoreIDs.insert(item.id) }
                                    else { restoreIDs.remove(item.id) }
                                }
                            )) {
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(item.name)
                                    Text("Restore SDK \(item.adjustedVersion) → \(item.originalVersion)")
                                        .font(.caption).foregroundStyle(.secondary)
                                    Text("Recorded \(Date(timeIntervalSince1970: item.time), format: .dateTime.day().month().year())")
                                        .font(.caption2).foregroundStyle(.secondary)
                                }
                            }
                        }
                        Button("Restore \(restoreIDs.count) selected app(s)", role: .destructive) {
                            confirmRestore = true
                        }.disabled(restoreIDs.isEmpty)
                    } header: {
                        Text("Recorded changes to restore")
                    } footer: {
                        Text("Only adjustments made by this app version appear here. Cache records must still match before restoration.")
                    }
                }
                if working {
                    ProgressView("Checking iPhone Duo…")
                } else if !report.isEmpty {
                    Section("Results") {
                        Text(report).font(.callout).textSelection(.enabled)
                    }
                }
            }
            .searchable(text: $search, prompt: "Search apps or bundle identifiers")
            .disabled(working)
            .navigationTitle("Duo SDK")
            .confirmationDialog("Apply selected SDK changes?", isPresented: $confirmApply) {
                Button("Apply to \(selectedIDs.count) selected app(s)") { run(1) }
            } message: {
                Text("Only selected apps are changed. Values above your installed SDK are experimental. Keep an encrypted iPhone backup.")
            }
            .confirmationDialog("Restore selected SDK changes?", isPresented: $confirmRestore) {
                Button("Restore \(restoreIDs.count) selected app(s)", role: .destructive) { run(2) }
            } message: {
                Text("Restore checks the current cache record; it will refuse a changed or relocated record rather than guess.")
            }
        }
    }

    private func appRow(_ item: DuoSDKCandidate) -> some View {
        VStack(alignment: .leading, spacing: 7) {
            Toggle(isOn: Binding(
                get: { selectedIDs.contains(item.id) },
                set: { on in
                    if on { selectedIDs.insert(item.id) }
                    else { selectedIDs.remove(item.id) }
                }
            )) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(item.name)
                    Text("Current SDK \(item.fromVersion)")
                        .font(.caption).foregroundStyle(.secondary)
                    Text(item.source)
                        .font(.caption2).foregroundStyle(.secondary)
                }
            }
            HStack {
                Text("Target SDK").font(.caption).foregroundStyle(.secondary)
                TextField("27.2.0", text: Binding(
                    get: { target(item) },
                    set: { targets[item.id] = $0 }
                ))
                .keyboardType(.numbersAndPunctuation)
                .textFieldStyle(.roundedBorder)
                .frame(maxWidth: 125)
                Spacer()
                Button("Remember current") {
                    savedTargets[item.id] = item.fromVersion
                    persistPreferences()
                }.font(.caption)
            }
            if let saved = savedTargets[item.id] {
                Text("Saved preference: \(saved)")
                    .font(.caption2).foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 3)
    }

    private func run(_ action: Int) {
        if action == 1 && !canApply { return }
        if action == 2 && restoreIDs.isEmpty { return }
        let prepared = action == 1 ? changes :
            action == 2 ? restoreIDs.sorted().map { ["id": $0] } : []
        // The legacy restore operation accepts only identifier strings.
        let encoded: Data?
        if action == 2 {
            encoded = try? JSONSerialization.data(withJSONObject: restoreIDs.sorted())
        } else {
            encoded = try? JSONSerialization.data(withJSONObject: prepared)
        }
        let payload = encoded.flatMap { String(data: $0, encoding: .utf8) } ?? "[]"
        let requestedIDs = selectedIDs
        let requestedTargets = changes.reduce(into: [String: String]()) { result, entry in
            if let id = entry["id"] as? String,
               let version = entry["after"] as? [Int] {
                result[id] = version.map(String.init).joined(separator: ".")
            }
        }
        if action == 0 {
            candidates = []; selectedIDs = []; restoreCandidates = []; restoreIDs = []
        }
        if action == 3 {
            restoreCandidates = []; restoreIDs = []; candidates = []; selectedIDs = []
        }
        working = true
        Task {
            let value = await Task.detached(priority: .userInitiated) {
                DuoSDKMaintenanceForSelection(action, payload) ?? "No result."
            }.value
            if action == 0 || action == 3 {
                let marker = action == 0 ? "\nDUOSDK_SELECTION_DATA=" : "\nDUOSDK_RESTORE_DATA="
                if let boundary = value.range(of: marker) {
                    let raw = value[boundary.upperBound...].split(separator: "\n", maxSplits: 1).first.map(String.init) ?? ""
                    if let bytes = Data(base64Encoded: raw) {
                        if action == 0, let items = try? JSONDecoder().decode([DuoSDKCandidate].self, from: bytes) {
                            candidates = items
                        } else if action == 3, let items = try? JSONDecoder().decode([DuoSDKRestoreCandidate].self, from: bytes) {
                            restoreCandidates = items
                        }
                    }
                    report = String(value[..<boundary.lowerBound])
                } else { report = value }
            } else {
                report = value
                if action == 1 && value.contains("DUO_BATCH_APLICADO") {
                    for id in requestedIDs {
                        if let preferred = requestedTargets[id] { savedTargets[id] = preferred }
                    }
                    persistPreferences()
                }
                candidates = []; selectedIDs = []
                restoreCandidates = []; restoreIDs = []
            }
            working = false
        }
    }
}
'''
s=s[:start]+ui
p.write_text(s)
print("DuoSDK v2 workspace: all validated apps, searchable, editable SDK targets, saved opt-in preferences.")
