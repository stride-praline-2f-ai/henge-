#!/usr/bin/env python3
"""Foreground DuoSDK heartbeat and conservative local-state self-repair.

Action 4 only touches DuoSDK's sandboxed recovery journal. It NEVER opens
the privileged LaunchServices path and NEVER performs a system-cache write.
Automatic repair archives journal bytes first and only deactivates records with
missing/unverifiable local snapshots. Ambiguous active records are warned about,
never guessed. Users may still explicitly inspect and apply system changes.
"""
from pathlib import Path
import sys
src=Path(sys.argv[1]).resolve()/"Sources"

p=src/"XCacheTransaction.m"
s=p.read_text()

anchor="static NSString *duoHistoryReview(NSString *support) {"
assert s.count(anchor)==1
helper=r'''
// Foreground-only self-check. Runs before any sandbox-extension request.
// Repair is limited to app-owned bookkeeping, never iOS LaunchServices.
static BOOL duoSessionBackupLooksValid(NSString *support, NSDictionary *record) {
    NSString *id = record[@"id"], *session = record[@"session"];
    NSArray *before = record[@"before"], *after = record[@"after"];
    NSNumber *offsetNumber = record[@"offset"];
    if (![id isKindOfClass:NSString.class] || id.length == 0 ||
        ![session isKindOfClass:NSString.class] ||
        ![[NSUUID alloc] initWithUUIDString:session] ||
        ![offsetNumber isKindOfClass:NSNumber.class] ||
        ![before isKindOfClass:NSArray.class] || before.count != 3 ||
        ![after isKindOfClass:NSArray.class] || after.count != 3) return NO;
    NSString *folder = [support stringByAppendingPathComponent:session];
    NSString *basePath = [folder stringByAppendingPathComponent:@"duo-upgrade-original.csstore"];
    NSString *candidatePath = [folder stringByAppendingPathComponent:@"duo-upgrade-candidate.csstore"];
    NSString *planPath = [folder stringByAppendingPathComponent:@"duo-upgrade-plan.json"];
    NSFileManager *fm = NSFileManager.defaultManager;
    NSDictionary *attributes = [fm attributesOfItemAtPath:basePath error:nil];
    NSDictionary *candidateAttributes = [fm attributesOfItemAtPath:candidatePath error:nil];
    unsigned long long originalLength = [attributes[NSFileSize] unsignedLongLongValue];
    unsigned long long candidateLength = [candidateAttributes[NSFileSize] unsignedLongLongValue];
    NSUInteger off = offsetNumber.unsignedIntegerValue;
    if (![attributes[NSFileType] isEqualToString:NSFileTypeRegular] ||
        ![candidateAttributes[NSFileType] isEqualToString:NSFileTypeRegular] ||
        originalLength < 64 || originalLength > LSMaximumSize ||
        candidateLength != originalLength ||
        off > originalLength || originalLength - off < 24) return NO;
    NSData *manifest = [NSData dataWithContentsOfFile:planPath options:0 error:nil];
    if (!manifest || manifest.length > 1024 * 1024) return NO;
    NSDictionary *plan = [NSJSONSerialization JSONObjectWithData:manifest options:0 error:nil];
    NSArray *rows = [plan isKindOfClass:NSDictionary.class] ? plan[@"changes"] : nil;
    BOOL found = NO;
    for (NSDictionary *row in rows) {
        if (![row isKindOfClass:NSDictionary.class]) return NO;
        if ([row[@"id"] isEqual:id] && [row[@"offset"] isEqual:offsetNumber] &&
            [row[@"before"] isEqual:before] && [row[@"after"] isEqual:after])
            found = YES;
    }
    if (!found) return NO;
    // Targeted 24-byte validation, without loading a potentially huge store.
    int oldFD = open(basePath.fileSystemRepresentation, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    int newFD = open(candidatePath.fileSystemRepresentation, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    uint8_t oldSDK[24], newSDK[24];
    BOOL verified = oldFD >= 0 && newFD >= 0 &&
        pread(oldFD, oldSDK, 24, (off_t)off) == 24 &&
        pread(newFD, newSDK, 24, (off_t)off) == 24 &&
        lsSDKMatches(oldSDK, before) && lsSDKMatches(newSDK, after);
    if (oldFD >= 0) close(oldFD);
    if (newFD >= 0) close(newFD);
    return verified;
}

static BOOL duoArchiveHistoryBytes(NSString *support) {
    NSString *historyPath = duoHistoryPath(support);
    NSData *raw = [NSData dataWithContentsOfFile:historyPath options:0 error:nil];
    if (!raw || raw.length > 1024 * 1024) return NO;
    NSString *archiveDir = [support stringByAppendingPathComponent:@"RecoveryJournalArchives"];
    if (![NSFileManager.defaultManager createDirectoryAtPath:archiveDir
          withIntermediateDirectories:YES
          attributes:@{NSFilePosixPermissions:@0700} error:nil]) return NO;
    NSString *archivePath = [archiveDir stringByAppendingPathComponent:
       [NSString stringWithFormat:@"%@.json", NSUUID.UUID.UUIDString]];
    return [raw writeToFile:archivePath options:NSDataWritingAtomic error:nil];
}

static NSString *duoHeartbeatAndRepair(void) {
    NSString *support = [NSHomeDirectory()
        stringByAppendingPathComponent:@"Library/Application Support/Duo SDK"];
    NSArray<NSDictionary *> *history = duoReadHistory(support);
    if (!history)
        return @"Heartbeat: restore history is unreadable or malformed. "
               @"No automatic repair attempted; keep the app installed and preserve its data.";
    NSMutableArray<NSDictionary *> *updated = [NSMutableArray arrayWithCapacity:history.count];
    NSMutableSet<NSString *> *badIDs = [NSMutableSet set];
    NSMutableDictionary<NSString *, NSNumber *> *activeCounts = [NSMutableDictionary dictionary];
    NSUInteger invalid = 0, valid = 0, active = 0;
    for (NSDictionary *row in history) {
        if (![row[@"active"] boolValue]) {
            [updated addObject:row];
            continue;
        }
        ++active;
        NSString *appID = row[@"id"];
        if (duoSessionBackupLooksValid(support,row)) {
            ++valid;
            activeCounts[appID] = @([activeCounts[appID] unsignedIntegerValue] + 1);
            [updated addObject:row];
        } else {
            ++invalid;
            [badIDs addObject:appID];
            NSMutableDictionary *disabled = [row mutableCopy];
            disabled[@"active"] = @NO;
            disabled[@"inactiveReason"] = @"Local backup missing or inconsistent at heartbeat";
            disabled[@"inactivatedAt"] = @(NSDate.date.timeIntervalSince1970);
            [updated addObject:disabled];
        }
    }

    NSUInteger ambiguous = 0;
    for (NSString *appID in activeCounts) {
        if ([activeCounts[appID] unsignedIntegerValue] > 1) ++ambiguous;
    }
    BOOL repaired = NO;
    BOOL repairFailed = NO;
    if (invalid) {
        // If the original file cannot be archived, preserve all original data
        // rather than overwrite it with a filtered history.
        if (duoArchiveHistoryBytes(support) && duoWriteHistory(support,updated))
            repaired = YES;
        else repairFailed = YES;
    }
    NSMutableString *report = [NSMutableString stringWithFormat:
        @"Heartbeat: %lu active recovery entry/entries checked. "
         @"%lu local backup(s) verified, %lu invalid, %lu ambiguous app(s).\n",
         (unsigned long)active, (unsigned long)valid,
         (unsigned long)invalid, (unsigned long)ambiguous];
    if (repaired) {
        [report appendFormat:
          @"Auto-repair: %lu unusable restore entry/entries deactivated. "
           @"The original journal was archived in app data. "
           @"No system data or SDK settings were changed.\n", (unsigned long)invalid];
    }
    if (repairFailed) {
        [report appendString:
          @"Auto-repair was not completed because the journal could not be "
           @"safely archived and rewritten. Original history retained.\n"];
    }
    if (ambiguous) {
        [report appendString:
          @"Conflict: multiple valid active restore entries exist for at least "
           @"one app. Not guessing which session is current. "
           @"Do not restore these entries until reviewed.\n"];
    }
    if (!active) {
        [report appendString:@"No recorded SDK restore sessions to check yet.\n"];
    }
    [report appendString:
       @"This checks DuoSDK's own recovery files, not a guarantee that the "
        @"system LaunchServices cache is healthy. A fresh app scan checks "
        @"currently recorded SDK values. No background cache edits occur.\n"];
    return report;
}

'''
s=s.replace(anchor,helper+anchor,1)

anchor='if (action < 0 || action > 3) return @"Unsupported action. No changes made.";'
assert s.count(anchor)==1
s=s.replace(anchor,'''if (action == 4) return duoHeartbeatAndRepair();
    if (action < 0 || action > 3) return @"Unsupported action. No changes made.";''',1)

# Serialize heartbeat, explicit app scans and cache modifications so a
# foreground timer cannot race an Apply/Restore operation.
name="NSString *DuoSDKMaintenanceForSelection(NSInteger action, NSString *selectedIDsJSON) {"
assert s.count(name)==1
s=s.replace(name,'''static NSString *DuoSDKMaintenanceForSelectionInternal(NSInteger action, NSString *selectedIDsJSON) {''',1)
anchor="// Legacy callers can only review or restore."
assert s.count(anchor)==1
serial=r'''
// A single serial gate for all caller paths, including the foreground heartbeat.
// A busy heartbeat is skipped rather than interfering with a live write.
NSString *DuoSDKMaintenanceForSelection(NSInteger action, NSString *selectedIDsJSON) {
    static NSLock *engineLock;
    static dispatch_once_t once;
    dispatch_once(&once, ^{ engineLock = [NSLock new]; });
    if (![engineLock tryLock]) return @"DuoSDK is busy with another operation; retry later.";
    @try {
        return DuoSDKMaintenanceForSelectionInternal(action, selectedIDsJSON);
    } @finally {
        [engineLock unlock];
    }
}

'''
s=s.replace(anchor,serial+anchor,1)
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
anchor='''    @State private var confirmRestore = false'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
    @Environment(\\.scenePhase) private var scenePhase
    @State private var heartbeatReport = "Checking saved restore sessions…"
    @State private var heartbeatChecking = false
    @State private var heartbeatTime: Date?''',1)

anchor='''                    Button("Choose apps to restore") { run(3) }'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
                    Button("Run heartbeat and self-repair") { checkHeartbeat() }''',1)

anchor='''                if !changedPreferences.isEmpty {'''
assert s.count(anchor)==1
s=s.replace(anchor,'''                Section("Recovery heartbeat") {
                    HStack {
                        Image(systemName: heartbeatChecking ? "arrow.triangle.2.circlepath" : "heart.text.square")
                            .foregroundStyle(.secondary)
                        Text(heartbeatChecking ? "Checking recoverability…" :
                             "Local recovery data health")
                    }
                    Text(heartbeatReport)
                        .font(.callout)
                        .textSelection(.enabled)
                    if let time = heartbeatTime {
                        Text("Last checked: \\(time, format: .dateTime.hour().minute().second())")
                            .font(.caption2).foregroundStyle(.secondary)
                    }
                } footer: {
                    Text("Checks and safely repairs DuoSDK's local journal on the foreground heartbeat. "
                         + "System-cache writes still require confirmation.")
                }
                if !changedPreferences.isEmpty {''',1)

anchor='''            .navigationTitle("Duo SDK")'''
assert s.count(anchor)==1
s=s.replace(anchor,'''            .navigationTitle("Duo SDK")
            .task(id: scenePhase) {
                guard scenePhase == .active else { return }
                checkHeartbeat()
                while !Task.isCancelled {
                    do {
                        try await Task.sleep(for: .seconds(180))
                    } catch { break }
                    guard !Task.isCancelled, scenePhase == .active else { break }
                    checkHeartbeat()
                }
            }''',1)

anchor='''    private func run(_ action: Int) {'''
assert s.count(anchor)==1
extra=r'''
    private func checkHeartbeat() {
        // Avoid racing a cache read or modification with a heartbeat.
        guard scenePhase == .active, !working, !heartbeatChecking else { return }
        heartbeatChecking = true
        Task {
            let value = await Task.detached(priority: .utility) {
                DuoSDKMaintenanceForSelection(4, "[]") ?? "Heartbeat returned no result."
            }.value
            heartbeatReport = value
            heartbeatTime = Date()
            heartbeatChecking = false
        }
    }

'''
s=s.replace(anchor,extra+anchor,1)

# Also refresh heartbeat after an operation finishes; once records change,
# the status should reflect the new state before the next three-minute tick.
anchor='''            working = false
        }
    }
}
'''
assert s.count(anchor)==1
s=s.replace(anchor,'''            working = false
            checkHeartbeat()
        }
    }
}
''',1)
p.write_text(s)
print("Foreground three-minute heartbeat and conservative journal self-repair enabled.")
