#!/usr/bin/env python3
"""DuoSDK per-app reversible history for future successful Apply sessions.
Restoration never trusts UI-provided offsets or versions; it re-parses the live
store, checks the corresponding saved candidate record, and runs the existing
locked, checksum-verified batch writer in reverse mode.
"""
from pathlib import Path
import sys

src=Path(sys.argv[1]).resolve()/"Sources"

# The cache parser also needs a read-only view of *current* SDK records,
# including 27.2 records that were already changed in earlier sessions.
p=src/"DuoSDKPlan.h"
s=p.read_text()
assert "DuoSDKPlanAll" not in s
s+="\n// Includes 27.2+ records for verified selective restore checks.\nNSArray<NSDictionary *> *DuoSDKPlanAll(NSData *store, NSSet<NSString *> *maintained, NSUInteger *matched);\n"
p.write_text(s)

p=src/"DuoSDKPlan.m"
s=p.read_text()
old="NSArray<NSDictionary *> *DuoSDKPlan(NSData *store, NSSet<NSString *> *maintained, NSUInteger *matched) {"
assert s.count(old)==1
s=s.replace(old, "static NSArray<NSDictionary *> *DuoSDKPlanInternal(NSData *store, NSSet<NSString *> *maintained, NSUInteger *matched, BOOL includeCurrent) {",1)
old="        if (!old) continue;"
assert s.count(old)==1
s=s.replace(old,"        if (!old && !includeCurrent) continue;",1)
s+="""

NSArray<NSDictionary *> *DuoSDKPlan(NSData *store, NSSet<NSString *> *maintained, NSUInteger *matched) {
    return DuoSDKPlanInternal(store, maintained, matched, NO);
}

NSArray<NSDictionary *> *DuoSDKPlanAll(NSData *store, NSSet<NSString *> *maintained, NSUInteger *matched) {
    return DuoSDKPlanInternal(store, maintained, matched, YES);
}
"""
p.write_text(s)

p=src/"XCacheTransaction.m"
s=p.read_text()

# Existing candidate writer is reused, including checksum recalculation and
# the parser's byte-for-byte changed-span validation. Reverse mode changes only
# values in the selected rows, never entire app records.
old="""static BOOL maintenanceCandidate(NSData *original, NSArray<NSDictionary *> *rows, NSString *folder,
                                 NSMutableString *report) {"""
new="""static BOOL maintenanceCandidate(NSData *original, NSArray<NSDictionary *> *rows, NSString *folder,
                                 NSMutableString *report, BOOL reverse) {"""
assert s.count(old)==1
s=s.replace(old,new,1)
old="""    const uint64_t sdk[3] = {27, 2, 0};
    for (NSDictionary *row in rows) {
        memcpy((uint8_t *)candidate.mutableBytes + [row[@"offset"] unsignedIntegerValue], sdk, sizeof(sdk));
    }"""
new="""    for (NSDictionary *row in rows) {
        NSArray *target = row[@"after"];
        if (![target isKindOfClass:NSArray.class] || target.count != 3) return NO;
        uint64_t sdk[3] = {0, 0, 0};
        for (NSUInteger i = 0; i < 3; i++) {
            if (![target[i] isKindOfClass:NSNumber.class] || [target[i] unsignedLongLongValue] > 99) return NO;
            sdk[i] = [target[i] unsignedLongLongValue];
        }
        NSUInteger offset = [row[@"offset"] unsignedIntegerValue];
        if (offset > candidate.length || candidate.length - offset < sizeof(sdk)) return NO;
        memcpy((uint8_t *)candidate.mutableBytes + offset, sdk, sizeof(sdk));
    }"""
assert s.count(old)==1
s=s.replace(old,new,1)
old="return lsBatchValidate(original, candidate, rows, NO, @2, 2).count &&"
assert s.count(old)==1
s=s.replace(old,"return lsBatchValidate(original, candidate, rows, reverse, @2, 2).count &&",1)
old="maintenanceCandidate(original, rows, folder, report)"
assert s.count(old)==1
s=s.replace(old,"maintenanceCandidate(original, rows, folder, report, NO)",1)

# Persistent history, kept privately in this app's Application Support. A
# session only enters the history after the writer explicitly verifies success.
helpers=r'''
static NSString *duoHistoryPath(NSString *support) {
    return [support stringByAppendingPathComponent:@"AppRestoreHistory.json"];
}

static NSArray<NSDictionary *> *duoReadHistory(NSString *support) {
    NSString *path = duoHistoryPath(support);
    if (![NSFileManager.defaultManager fileExistsAtPath:path]) return @[];
    NSData *bytes = [NSData dataWithContentsOfFile:path options:0 error:nil];
    if (!bytes || bytes.length > 1024 * 1024) return nil;
    id parsed = [NSJSONSerialization JSONObjectWithData:bytes options:0 error:nil];
    if (![parsed isKindOfClass:NSArray.class] || [parsed count] > 4000) return nil;
    for (id row in parsed) {
        if (![row isKindOfClass:NSDictionary.class] ||
            ![row[@"id"] isKindOfClass:NSString.class] ||
            ![row[@"session"] isKindOfClass:NSString.class] ||
            ![row[@"before"] isKindOfClass:NSArray.class] ||
            ![row[@"after"] isKindOfClass:NSArray.class] ||
            ![row[@"offset"] isKindOfClass:NSNumber.class] ||
            ![row[@"active"] isKindOfClass:NSNumber.class]) return nil;
    }
    return parsed;
}

static BOOL duoWriteHistory(NSString *support, NSArray *history) {
    if (history.count > 4000) return NO;
    NSData *bytes = [NSJSONSerialization dataWithJSONObject:history options:0 error:nil];
    return bytes && bytes.length <= 1024 * 1024 &&
        [bytes writeToFile:duoHistoryPath(support) options:NSDataWritingAtomic error:nil];
}

static BOOL duoSaveAppliedSession(NSString *support, NSString *session, NSArray<NSDictionary *> *rows) {
    NSArray *old = duoReadHistory(support);
    if (!old || ![[NSUUID alloc] initWithUUIDString:session]) return NO;
    NSMutableArray *history = [old mutableCopy];
    NSNumber *time = @(NSDate.date.timeIntervalSince1970);
    for (NSDictionary *row in rows) {
        if (![row[@"id"] isKindOfClass:NSString.class]) return NO;
        for (NSDictionary *previous in history) {
            if ([previous[@"active"] boolValue] && [previous[@"id"] isEqualToString:row[@"id"]])
                return NO; // Never allow ambiguous active histories for one app.
        }
        [history addObject:@{@"id":row[@"id"], @"name":row[@"name"] ?: row[@"id"],
            @"session":session, @"offset":row[@"offset"], @"before":row[@"before"],
            @"after":row[@"after"], @"active":@YES, @"time":time}];
    }
    return duoWriteHistory(support,history);
}

static NSString *duoHistoryReview(NSString *support) {
    NSArray *history = duoReadHistory(support);
    if (!history) return @"Restore history could not be verified. No changes made.";
    NSMutableArray *active = [NSMutableArray array];
    for (NSDictionary *entry in history) {
        if (![entry[@"active"] boolValue]) continue;
        [active addObject:@{@"id":entry[@"id"], @"name":entry[@"name"],
            @"before":entry[@"before"], @"after":entry[@"after"],
            @"session":entry[@"session"], @"time":entry[@"time"] ?: @0}];
    }
    [active sortUsingComparator:^NSComparisonResult(NSDictionary *a, NSDictionary *b) {
        return [b[@"time"] compare:a[@"time"]];
    }];
    NSData *data = [NSJSONSerialization dataWithJSONObject:active options:0 error:nil];
    if (!data) return @"Restore history encoding failed. No changes made.";
    return [NSString stringWithFormat:
        @"%lu app(s) with recorded changes available for review. "
         @"Only successful Apply sessions created by this version are in history. "
         @"Restore may refuse if an app was updated, reinstalled or its cache record changed. "
         @"No changes made.\nDUOSDK_RESTORE_DATA=%@\n",
         (unsigned long)active.count,[data base64EncodedStringWithOptions:0]];
}

// Parse only a list of unique bundle identifiers; IDs from the UI are never
// permitted to influence cache file offsets or proposed SDK bytes.
static NSSet<NSString *> *duoRequestedIDs(NSString *selectedJSON) {
    NSData *bytes = [selectedJSON dataUsingEncoding:NSUTF8StringEncoding];
    id parsed = bytes ? [NSJSONSerialization JSONObjectWithData:bytes options:0 error:nil] : nil;
    if (![parsed isKindOfClass:NSArray.class] || [parsed count] == 0 || [parsed count] > 400)
        return nil;
    NSMutableSet<NSString *> *ids = [NSMutableSet set];
    for (id item in parsed) {
        if (![item isKindOfClass:NSString.class] || [item length] == 0 ||
            [item length] > 255 || [ids containsObject:item]) return nil;
        [ids addObject:item];
    }
    return ids;
}

// A saved candidate's 604-byte Bundle record must still be the same record,
// apart from the 24 SDK bytes. This refuses cache record relocations and app
// updates instead of writing to a guessed byte offset.
static BOOL duoSameRecordExceptSDK(NSData *live, NSData *saved, NSUInteger offset) {
    const NSUInteger prefix = 0x50, total = 612, sdkLength = 24;
    if (!live || !saved || live.length != saved.length ||
        live.length < total || offset < prefix ||
        offset > live.length - (total - prefix)) return NO;
    const uint8_t *a = live.bytes, *b = saved.bytes;
    NSUInteger start = offset - prefix;
    return memcmp(a + start, b + start, prefix) == 0 &&
        memcmp(a + offset + sdkLength, b + offset + sdkLength,
               total - prefix - sdkLength) == 0;
}

static NSString *duoRestoreSelected(int dir, NSString *support, NSString *selectedJSON) {
    NSSet<NSString *> *wanted = duoRequestedIDs(selectedJSON);
    if (!wanted) return @"Choose one or more apps to restore first. No changes made.";
    NSArray<NSDictionary *> *history = duoReadHistory(support);
    if (!history) return @"Restore history is invalid. No changes made.";

    struct stat st;
    NSData *live = lsFile(dir, LSActiveStore, &st);
    NSString *livePath = [LSExactDirectory stringByAppendingPathComponent:LSActiveStore];
    NSMutableString *report = [NSMutableString string];
    if (!live || !validCSStore(livePath, report))
        return @"Live cache validation failed. No changes made.";

    NSUInteger matched = 0;
    NSArray<NSDictionary *> *parsed = DuoSDKPlanAll(live, [NSSet set], &matched);
    if (!parsed || matched == 0) return @"Current app record parser rejected the cache. No changes made.";
    NSMutableDictionary *byID = [NSMutableDictionary dictionary];
    for (NSDictionary *app in parsed) byID[app[@"id"]] = app;

    NSMutableArray<NSDictionary *> *reverseRows = [NSMutableArray array];
    for (NSString *appID in wanted) {
        NSDictionary *entry = nil;
        for (NSDictionary *candidate in history) {
            if ([candidate[@"active"] boolValue] && [candidate[@"id"] isEqualToString:appID]) {
                if (entry) return @"Ambiguous restore history for an app. No changes made.";
                entry = candidate;
            }
        }
        NSDictionary *current = byID[appID];
        if (!entry || !current || ![[NSUUID alloc] initWithUUIDString:entry[@"session"]] ||
            ![entry[@"after"] isEqual:current[@"before"]] ||
            ![entry[@"offset"] isEqual:current[@"offset"]] ||
            ![entry[@"after"] isEqual:@[@27,@2,@0]])
            return @"An app changed or was reinstalled since Apply. Review again; nothing restored.";
        NSUInteger offset = [entry[@"offset"] unsignedIntegerValue];
        NSString *folder = [support stringByAppendingPathComponent:entry[@"session"]];
        NSData *saved = [NSData dataWithContentsOfFile:
            [folder stringByAppendingPathComponent:@"duo-upgrade-candidate.csstore"]
            options:0 error:nil];
        if (!duoSameRecordExceptSDK(live,saved,offset) ||
            !lsSDKMatches((const uint8_t *)saved.bytes + offset,entry[@"after"]))
            return @"A saved app record no longer matches the live cache. Nothing restored.";
        if (![entry[@"before"] isKindOfClass:NSArray.class] ||
            [entry[@"before"] count] != 3) return @"Invalid restore version. Nothing changed.";
        [reverseRows addObject:@{@"id":appID, @"name":entry[@"name"],
            @"offset":current[@"offset"], @"before":current[@"before"],
            @"after":entry[@"before"]}];
    }
    if (reverseRows.count != wanted.count) return @"Restore selection mismatch. Nothing changed.";
    [reverseRows sortUsingDescriptors:@[[NSSortDescriptor sortDescriptorWithKey:@"offset" ascending:YES]]];

    NSString *session = NSUUID.UUID.UUIDString;
    NSString *folder = [support stringByAppendingPathComponent:session];
    if (![NSFileManager.defaultManager createDirectoryAtPath:folder
        withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:nil] ||
        !maintenanceCandidate(live, reverseRows, folder, report, YES))
        return @"Could not prepare a checksum-verified selected-app restore. Nothing changed.";

    int privateDir = open(folder.fileSystemRepresentation,
                          O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (privateDir < 0) return @"Could not open selected-app restore backup. Nothing changed.";
    lsRunBatch(dir,privateDir,folder,@"batch-upgrade-reverse",report);
    close(privateDir);
    if ([report containsString:@"DUO_BATCH_REVERTIDO"]) {
        NSMutableArray *updated = [NSMutableArray array];
        for (NSDictionary *item in history) {
            if ([item[@"active"] boolValue] && [wanted containsObject:item[@"id"]]) {
                NSMutableDictionary *restored = [item mutableCopy];
                restored[@"active"] = @NO;
                restored[@"restoredAt"] = @(NSDate.date.timeIntervalSince1970);
                [updated addObject:restored];
            } else [updated addObject:item];
        }
        if (duoWriteHistory(support,updated)) {
            [report appendFormat:@"Restored SDK metadata for %lu selected app(s). "
                "Other recorded changes are retained. Restart affected apps if needed.\n",
                (unsigned long)wanted.count];
        } else {
            [report appendString:@"Cache change was verified, but history could not be updated. "
                "Do not repeat the restore without reviewing the live cache.\n"];
        }
    }
    return report.length ? report : @"Selected restore was refused. No changes made.";
}

'''
anchor="// Selection is checked against a freshly parsed live cache, never against"
assert s.count(anchor)==1
s=s.replace(anchor,helpers+anchor,1)

# Action 3 lists history without opening the private cache.
old='if (action < 0 || action > 2) return @"Unsupported action. No changes made.";'
assert s.count(old)==1
s=s.replace(old,'if (action < 0 || action > 3) return @"Unsupported action. No changes made.";')
function_start=s.index('NSString *DuoSDKMaintenanceForSelection(NSInteger action, NSString *selectedIDsJSON) {')
group=s.index('    NSString *groupReason = nil;', function_start)
s=s[:group]+'''    if (action == 3) {
        NSString *support = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Application Support/Duo SDK"];
        return duoHistoryReview(support);
    }
'''+s[group:]

start=s.index('        if (action == 2) {',function_start)
end=s.index('        struct stat baseline;',start)
s=s[:start]+'''        if (action == 2) return duoRestoreSelected(dir,support,selectedIDsJSON);

'''+s[end:]

# Verify a pre-existing active history entry does not conflict before applying.
anchor='''        NSString *identifier = NSUUID.UUID.UUIDString;
        NSString *folder = [support stringByAppendingPathComponent:identifier];'''
assert s.count(anchor)==1
check='''        NSArray *known = duoReadHistory(support);
        if (!known) return @"Restore history is unreadable; refusing Apply to protect previous changes.";
        for (NSDictionary *row in rows) for (NSDictionary *previous in known) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]])
                return @"This app already has an active restore record. Review restore history first.";
        }
'''
s=s.replace(anchor,check+anchor,1)

# "Latest" should not advance on failed Apply. A failed run must not destroy
# the user's previous recovery pointer.
old='''            !maintenanceCandidate(original, rows, folder, report, NO) ||
            ![identifier writeToFile:latest atomically:YES encoding:NSUTF8StringEncoding error:nil]) {'''
assert s.count(old)==1
s=s.replace(old,'''            !maintenanceCandidate(original, rows, folder, report, NO)) {''',1)
anchor='''        if ([report containsString:@"DUO_BATCH_APLICADO"]) {'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
            BOOL recorded = duoSaveAppliedSession(support,identifier,rows);
            BOOL latestSaved = [identifier writeToFile:latest atomically:YES
                encoding:NSUTF8StringEncoding error:nil];
            if (!recorded || !latestSaved)
                [report appendString:@"Warning: Apply succeeded but restore history "
                    "could not be saved completely. Preserve the app and its backup folder.\\n"];
''',1)
p.write_text(s)

# Replace only the interactive SwiftUI view. Everything is opt-in.
p=src/"App.swift"
s=p.read_text()
ix=s.index("private struct DuoSDKView: View {")
ui=r'''
private struct DuoSDKRestoreCandidate: Decodable, Identifiable {
    let id: String
    let name: String
    let before: [Int]
    let after: [Int]
    let session: String
    let time: Double
    var originalVersion: String { before.map(String.init).joined(separator: ".") }
    var adjustedVersion: String { after.map(String.init).joined(separator: ".") }
}

private struct DuoSDKView: View {
    @State private var report = ""
    @State private var working = false
    @State private var candidates: [DuoSDKCandidate] = []
    @State private var selectedIDs: Set<String> = []
    @State private var restoreCandidates: [DuoSDKRestoreCandidate] = []
    @State private var restoreIDs: Set<String> = []
    @State private var confirmApply = false
    @State private var confirmRestore = false

    private var older: [DuoSDKCandidate] {
        candidates.filter { item in
            item.before.count >= 2 &&
            (item.before[0] < 27 || (item.before[0] == 27 && item.before[1] < 1))
        }.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
    }

    private var remaining: [DuoSDKCandidate] {
        candidates.filter { item in
            item.before.count >= 2 &&
            !(item.before[0] < 27 || (item.before[0] == 27 && item.before[1] < 1))
        }.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Button("Review eligible apps") { run(0) }
                    Button("Choose apps to restore") { run(3) }
                } footer: {
                    Text("Review is read-only. Each app must be explicitly selected before Apply or Restore.")
                }
                if !older.isEmpty {
                    Section("SDK below 27.1") {
                        ForEach(older) { candidateToggle($0) }
                    }
                }
                if !remaining.isEmpty {
                    Section("SDK 27.1 and other eligible apps") {
                        ForEach(remaining) { candidateToggle($0) }
                    }
                }
                if !candidates.isEmpty {
                    Section {
                        Button("Apply to \(selectedIDs.count) selected app(s)") {
                            confirmApply = true
                        }.disabled(selectedIDs.isEmpty)
                    } footer: {
                        Text("No apps are selected by default. Recheck the list after installing or updating apps.")
                    }
                }
                if !restoreCandidates.isEmpty {
                    Section("Recorded changes to restore") {
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
                    } footer: {
                        Text("Only changes recorded by this version are listed. Restore checks each app's live cache record before writing.")
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
                Text("Only the selected apps will change. This edits the iOS LaunchServices cache; create an encrypted iPhone backup first.")
            }
            .confirmationDialog("Restore selected SDK changes?", isPresented: $confirmRestore) {
                Button("Restore \(restoreIDs.count) selected app(s)", role: .destructive) { run(2) }
            } message: {
                Text("Only your selected apps will be restored. Updated or relocated cache records will be refused rather than guessed.")
            }
        }
    }

    private func candidateToggle(_ item: DuoSDKCandidate) -> some View {
        Toggle(isOn: Binding(
            get: { selectedIDs.contains(item.id) },
            set: { on in
                if on { selectedIDs.insert(item.id) }
                else { selectedIDs.remove(item.id) }
            }
        )) {
            VStack(alignment: .leading, spacing: 3) {
                Text(item.name)
                Text("SDK \(item.fromVersion) → \(item.toVersion)")
                    .font(.caption).foregroundStyle(.secondary)
                Text(item.source).font(.caption2).foregroundStyle(.secondary)
            }
        }
    }

    private func run(_ action: Int) {
        if action == 1 && selectedIDs.isEmpty { return }
        if action == 2 && restoreIDs.isEmpty { return }
        let requested = action == 1 ? selectedIDs.sorted() :
            action == 2 ? restoreIDs.sorted() : []
        let data = try? JSONSerialization.data(withJSONObject: requested)
        let selectionJSON = data.flatMap { String(data: $0, encoding: .utf8) } ?? "[]"
        if action == 0 { candidates = []; selectedIDs = []; restoreCandidates = []; restoreIDs = [] }
        if action == 3 { restoreCandidates = []; restoreIDs = []; candidates = []; selectedIDs = [] }
        working = true
        Task {
            let value = await Task.detached(priority: .userInitiated) {
                DuoSDKMaintenanceForSelection(action, selectionJSON) ?? "No result."
            }.value
            if action == 0 || action == 3 {
                let marker = action == 0 ? "\nDUOSDK_SELECTION_DATA=" : "\nDUOSDK_RESTORE_DATA="
                if let boundary = value.range(of: marker) {
                    let raw = value[boundary.upperBound...].split(separator: "\n", maxSplits: 1).first.map(String.init) ?? ""
                    if let bytes = Data(base64Encoded: raw) {
                        if action == 0, let list = try? JSONDecoder().decode([DuoSDKCandidate].self, from: bytes) {
                            candidates = list
                        } else if action == 3, let list = try? JSONDecoder().decode([DuoSDKRestoreCandidate].self, from: bytes) {
                            restoreCandidates = list
                        }
                    }
                    report = String(value[..<boundary.lowerBound])
                } else { report = value }
            } else {
                report = value
                candidates = []; selectedIDs = []
                restoreCandidates = []; restoreIDs = []
            }
            working = false
        }
    }
}
'''
s=s[:ix]+ui
p.write_text(s)
print("DuoSDK app-level restore history + grouped SDK list enabled; no implicit apply or restore.")
