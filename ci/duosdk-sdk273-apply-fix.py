#!/usr/bin/env python3
"""Fix SDK 27.3 entrypoint and safe chained restore point on iOS 27.2.x.

This runs AFTER SDK273 Fix Mode is installed. Treating 27.3 as an experimental
cached SDK tag is distinct from installing a newer OS or patching the app.
Ordinary editing may submit only one 27.3 app at a time and is routed through
the action-7 whitelist. Other target checks are not weakened.

If a previous active DuoSDK adjustment matches the live cache, action 7 can
supersede it ONLY when the older saved candidate's app record still matches
the live record, except for SDK bytes. The new restore entry retains the
original-before-the-first-override value.
"""
from pathlib import Path
import sys
src = Path(sys.argv[1]).resolve() / "Sources"

def repl(s,old,new):
    assert s.count(old) == 1,(old[:120],s.count(old))
    return s.replace(old,new,1)

p=src/"XCacheTransaction.m"
s=p.read_text()
guard=r'''        for (NSDictionary *row in rows) for (NSDictionary *previous in known) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]] &&
                [previous[@"after"] isEqual:row[@"before"]])
                return @"This app still has an active restore record. Restore or choose another app first.";
        }'''
replacement=r'''        // For the single-app SDK 27.3 experiment, permit a previously
        // adjusted app only when the earlier recovery record has been checked
        // against THIS live cache and THIS installed app's Bundle record.
        // For ordinary Apply, preserve the existing history lock.
        for (NSDictionary *row in rows) {
            NSUInteger activeMatches = 0;
            for (NSDictionary *previous in known) {
                if (![previous[@"active"] boolValue] ||
                    ![previous[@"id"] isEqualToString:row[@"id"]] ||
                    ![previous[@"after"] isEqual:row[@"before"]]) continue;
                ++activeMatches;
                if (action != 7)
                    return @"This app still has an active restore record. "
                           @"Undo the previous change first. Nothing changed.";
                if (activeMatches > 1 ||
                    ![previous[@"offset"] isEqual:row[@"offset"]] ||
                    ![[NSUUID alloc] initWithUUIDString:previous[@"session"]] ||
                    ![previous[@"before"] isKindOfClass:NSArray.class] ||
                    [previous[@"before"] count] != 3)
                    return @"Conflicting or invalid prior recovery record. Nothing changed.";
                NSString *earlierFolder = [support
                    stringByAppendingPathComponent:previous[@"session"]];
                NSData *earlierCandidate = [NSData dataWithContentsOfFile:
                    [earlierFolder stringByAppendingPathComponent:
                     @"duo-upgrade-candidate.csstore"]
                    options:0 error:nil];
                NSUInteger sdkOffset = [row[@"offset"] unsignedIntegerValue];
                if (!duoSameRecordExceptSDK(original, earlierCandidate, sdkOffset) ||
                    !lsSDKMatches((const uint8_t *)earlierCandidate.bytes + sdkOffset,
                                  previous[@"after"]))
                    return @"Previous SDK recovery snapshot no longer matches "
                           @"this installed app. No changes made.";
            }
        }'''
s=repl(s,guard,replacement)

# Preserve the original baseline so Undo restores original SDK, not just
# the most recent experimental intermediate value.
old=r'''        // Supersede only after Apply succeeded. Older records remain in the
        // journal, but are no longer offered as if they still match the cache.
        for (NSUInteger idx = 0; idx < history.count; ++idx) {'''
new=r'''        // Chain a verified previous adjustment into the new recovery entry.
        // The action-7 preflight above has verified prior candidate identity.
        NSArray *originalRollbackSDK = row[@"before"];
        for (NSDictionary *previous in history) {
            if ([previous[@"active"] boolValue] &&
                [previous[@"id"] isEqualToString:row[@"id"]] &&
                [previous[@"after"] isEqual:row[@"before"]] &&
                [previous[@"offset"] isEqual:row[@"offset"]] &&
                [previous[@"before"] isKindOfClass:NSArray.class] &&
                [previous[@"before"] count] == 3) {
                originalRollbackSDK = previous[@"before"];
            }
        }
        // Supersede only after Apply succeeded. Older records remain in the
        // journal, but are no longer offered as if they still match the cache.
        for (NSUInteger idx = 0; idx < history.count; ++idx) {'''
s=repl(s,old,new)
old=r'''@"session":session, @"offset":row[@"offset"], @"before":row[@"before"],
            @"after":row[@"after"], @"active":@YES, @"time":time}];'''
new=r'''@"session":session, @"offset":row[@"offset"], @"before":originalRollbackSDK,
            @"after":row[@"after"], @"active":@YES, @"time":time}];'''
s=repl(s,old,new)
assert 'duoSameRecordExceptSDK(original, earlierCandidate, sdkOffset)' in s
assert 'maintenanceCandidate(original, rows, folder, report, NO)' in s
assert 'lsRunBatch(dir,privateDir,folder,@"batch-upgrade-reverse"' in s
p.write_text(s)

p=src/"App.swift"
s=p.read_text()
old=r'''        guard major == os.majorVersion,
              minor <= os.minorVersion,
              minor != os.minorVersion || patch <= os.patchVersion
        else { return nil }
        return [major, minor, patch]'''
new=r'''        let installedVersion = major == os.majorVersion &&
            minor <= os.minorVersion &&
            (minor != os.minorVersion || patch <= os.patchVersion)
        let experimental273 = major == 27 && minor == 3 && patch == 0 &&
            os.majorVersion == 27 && (os.minorVersion == 2 || os.minorVersion == 3)
        guard installedVersion || experimental273 else { return nil }
        return [major, minor, patch]'''
s=repl(s,old,new)
old=r'''    private var canApply: Bool {
        !selectedIDs.isEmpty && changes.count == selectedIDs.count
    }'''
new=r'''    private var canApply: Bool {
        guard !selectedIDs.isEmpty && changes.count == selectedIDs.count
        else { return false }
        let experimental = changes.contains {
            ($0["after"] as? [Int]) == [27, 3, 0]
        }
        return !experimental || changes.count == 1
    }'''
s=repl(s,old,new)

old=r'''        if action == 1 && !canApply { return }
        if action == 2 && restoreIDs.isEmpty { return }'''
new=r'''        if action == 1 && !canApply { return }
        if action == 2 && restoreIDs.isEmpty { return }
        // The main editor must use the same action-7 backend as Fix Mode,
        // rather than passing 27.3 to normal action 1, which rejects it.
        let actualAction = action == 1 && changes.count == 1 &&
            (changes.first?["after"] as? [Int]) == [27, 3, 0] ? 7 : action'''
s=repl(s,old,new)
s=repl(s,'DuoSDKMaintenanceForSelection(action, payload) ?? "No result."',
       'DuoSDKMaintenanceForSelection(actualAction, payload) ?? "No result."')
# If 27.3 experimental is queued among multiple selected apps, explicitly
# explain why the action is unavailable instead of a generic version error.
s=repl(s,'Text("Choose a valid SDK that differs from the current value.")',
         'Text("Use a different SDK value, or select only one app for 27.3.")')
p.write_text(s)
print("SDK 27.3 trial: main editor route repaired; validated prior restore "
      "record can be safely superseded while retaining original rollback SDK.")
