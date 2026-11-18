#!/usr/bin/env python3
"""Offer explicit per-app opt-in and include path-verified sideloaded app records.
Transactional cache validation, checksums and rollback are not modified.
"""
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve() / "Sources"

p = src / "DuoSDKPlan.m"
s = p.read_text()
a = '        if (!storeSigned && ![maintained containsObject:identifier]) continue;'
assert s.count(a)==1
s=s.replace(a, '''        // Include other signing identities (including sideloading), but still
        // require validated Bundle records and installed-app paths below.''', 1)
a = '        BOOL old = sdk[0] < 27 || (sdk[0] == 27 && (sdk[1] == 0 || (sdk[1] == 1 && [maintained containsObject:identifier])));'
assert s.count(a)==1
s=s.replace(a, '        BOOL old = sdk[0] < 27 || (sdk[0] == 27 && sdk[1] < 2);',1)
a = '            @"before": @[@(sdk[0]), @(sdk[1]), @(sdk[2])], @"after": @[@27, @2, @0]}];'
assert s.count(a)==1
s=s.replace(a, '''            @"before": @[@(sdk[0]), @(sdk[1]), @(sdk[2])], @"after": @[@27, @2, @0],
            @"source": storeSigned ? @"App Store/TestFlight" : @"Other signing (possibly sideloaded)"}];''',1)
p.write_text(s)

p=src/"Bridge.h"
s=p.read_text()
a='NSString *DuoSDKMaintenance(NSInteger action);'
assert s.count(a)==1
s=s.replace(a,a+'\nNSString *DuoSDKMaintenanceForSelection(NSInteger action, NSString *selectedIDsJSON);',1)
p.write_text(s)

p=src/"XCacheTransaction.m"
s=p.read_text()
a='NSString *DuoSDKMaintenance(NSInteger action) {'
assert s.count(a)==1
s=s.replace(a,'''// Always reparse the current validated cache before applying selected IDs.
NSString *DuoSDKMaintenanceForSelection(NSInteger action, NSString *selectedIDsJSON) {
    if (action < 0 || action > 2) return @"Unsupported action. No changes made.";
''',1)
a='''        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"];
            [report appendFormat:@"• %@ · %@.%@ → 27.2\\n", row[@"name"], before[0], before[1]];
        }
        if (action == 0) return report;'''
assert s.count(a)==1,("report anchor",s.count(a))
b='''        if (action == 1) {
            NSData *json = [selectedIDsJSON dataUsingEncoding:NSUTF8StringEncoding];
            NSArray *requested = json ? [NSJSONSerialization JSONObjectWithData:json options:0 error:nil] : nil;
            if (![requested isKindOfClass:NSArray.class] || requested.count == 0 || requested.count > 400)
                return @"No valid app selection. Review and select apps first. No changes made.";
            NSMutableSet<NSString *> *wanted = [NSMutableSet set];
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
            rows = filtered;
        }
        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"];
            [report appendFormat:@"• %@ · %@.%@ → 27.2\\n", row[@"name"], before[0], before[1]];
        }
        if (action == 0) {
            NSMutableArray *candidates = [NSMutableArray array];
            for (NSDictionary *row in rows)
                [candidates addObject:@{@"id":row[@"id"], @"name":row[@"name"],
                    @"before":row[@"before"], @"after":row[@"after"],
                    @"source":row[@"source"] ?: @"Unknown"}];
            NSData *json = [NSJSONSerialization dataWithJSONObject:candidates options:0 error:nil];
            if (!json) return @"Could not prepare app list. No changes made.";
            [report appendFormat:@"\\nDUOSDK_SELECTION_DATA=%@\\n",
                [json base64EncodedStringWithOptions:0]];
            return report;
        }'''
s=s.replace(a,b,1)
# The number reported after Apply must describe the selected apps, not the
# total candidate count from the broader review.
counter = '        [report appendFormat:rows.count == 1 ?'
begin = s.index(counter)
assert begin > 0
end = s.index(';\n', begin) + 2
count_report = s[begin:end]
s = s[:begin] + s[end:]
before_count = '            rows = filtered;\n        }\n        for (NSDictionary *row in rows)'
assert s.count(before_count) == 1
s = s.replace(before_count,
    '            rows = filtered;\n        }\n' + count_report +
    '\n        for (NSDictionary *row in rows)', 1)
s+='''

// Legacy callers can only review or restore. Never apply to all by default.
NSString *DuoSDKMaintenance(NSInteger action) {
    if (action == 1) return @"Select individual apps in DuoSDK first. Nothing changed.";
    return DuoSDKMaintenanceForSelection(action, @"");
}
'''
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
ix=s.index("private struct DuoSDKView: View {")
ui=r'''private struct DuoSDKCandidate: Decodable, Identifiable {
    let id: String
    let name: String
    let before: [Int]
    let after: [Int]
    let source: String

    var fromVersion: String { before.map { String($0) }.joined(separator: ".") }
    var toVersion: String { after.map { String($0) }.joined(separator: ".") }
}

private struct DuoSDKView: View {
    @State private var report = ""
    @State private var working = false
    @State private var candidates: [DuoSDKCandidate] = []
    @State private var selectedIDs: Set<String> = []
    @State private var confirmApply = false
    @State private var confirmRollback = false

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Button("Review eligible apps") { run(0) }
                    Button("Restore previous changes") { confirmRollback = true }
                } footer: {
                    Text("Read-only review. Back up your iPhone before attempting experimental system-cache changes.")
                }

                if !candidates.isEmpty {
                    Section {
                        ForEach(candidates) { item in
                            Toggle(isOn: Binding(
                                get: { selectedIDs.contains(item.id) },
                                set: { enabled in
                                    if enabled { selectedIDs.insert(item.id) }
                                    else { selectedIDs.remove(item.id) }
                                }
                            )) {
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(item.name)
                                    Text("SDK \(item.fromVersion) → \(item.toVersion)")
                                        .font(.caption).foregroundStyle(.secondary)
                                    Text(item.source)
                                        .font(.caption2).foregroundStyle(.secondary)
                                }
                            }
                        }
                        Button("Apply to \(selectedIDs.count) selected app(s)") {
                            confirmApply = true
                        }
                        .disabled(selectedIDs.isEmpty)
                    } header: {
                        Text("Choose apps to adjust")
                    } footer: {
                        Text("Nothing is selected by default. Only checked apps can be changed.")
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
            .disabled(working)
            .navigationTitle("Duo SDK")
            .confirmationDialog("Apply SDK metadata changes?", isPresented: $confirmApply) {
                Button("Apply to \(selectedIDs.count) selected app(s)") { run(1) }
            } message: {
                Text("This edits the iOS LaunchServices cache for selected apps. Successful recovery is not guaranteed.")
            }
            .confirmationDialog("Restore the last backup?", isPresented: $confirmRollback) {
                Button("Restore backup", role: .destructive) { run(2) }
            } message: {
                Text("The live cache must match the saved backup before restoration is allowed.")
            }
        }
    }

    private func run(_ action: Int) {
        if action == 1 && selectedIDs.isEmpty { return }
        let chosen = action == 1 ? selectedIDs.sorted() : []
        let encoded = try? JSONSerialization.data(withJSONObject: chosen)
        let selectionJSON = encoded.flatMap { String(data: $0, encoding: .utf8) } ?? "[]"
        if action == 0 {
            candidates = []
            selectedIDs = []
        }
        working = true
        Task {
            let result = await Task.detached(priority: .userInitiated) {
                DuoSDKMaintenanceForSelection(action, selectionJSON) ?? "No result."
            }.value
            if action == 0 {
                let marker = "\nDUOSDK_SELECTION_DATA="
                if let boundary = result.range(of: marker) {
                    let encoded = result[boundary.upperBound...]
                        .split(separator: "\n", maxSplits: 1).first.map(String.init) ?? ""
                    if let bytes = Data(base64Encoded: encoded),
                       let list = try? JSONDecoder().decode([DuoSDKCandidate].self, from: bytes) {
                        candidates = list
                    }
                    report = String(result[..<boundary.lowerBound])
                } else {
                    report = result
                }
            } else {
                report = result
                candidates = []
                selectedIDs = []
            }
            working = false
        }
    }
}
'''
p.write_text(s[:ix]+ui)
print("Per-app opt-in UI enabled; other-signed apps included only when records pass existing format and path checks.")
