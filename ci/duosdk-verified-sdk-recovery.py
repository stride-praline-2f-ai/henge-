#!/usr/bin/env python3
"""Opt-in compatibility rollback sourced from the installed, signed app's Mach-O.

Adds action 5: selected app SDK tag in LaunchServices -> original SDK declared
in the installed executable's LC_BUILD_VERSION (or LC_VERSION_MIN_IPHONEOS).

This NEVER modifies executable, Info.plist, provisioning, or scene preferences.
It uses existing selected-app checksum-verified transactional writer and history.
If the installed app cannot be read/verified, refuses the operation.
"""
from pathlib import Path
import sys
src=Path(sys.argv[1]).resolve()/"Sources"

p=src/"DuoSDKPlan.m"
s=p.read_text()
anchor='''            @"source": storeSigned ? @"App Store/TestFlight" : @"Other signing (possibly sideloaded)"}];'''
assert s.count(anchor)==1
s=s.replace(anchor,'''            @"source": storeSigned ? @"App Store/TestFlight" : @"Other signing (possibly sideloaded)",
            @"bundlePath": [parent stringByAppendingPathComponent:bundleName]}];''',1)
p.write_text(s)

p=src/"XCacheTransaction.m"
s=p.read_text()
if '#include <mach-o/loader.h>' not in s:
    s=s.replace('#include <dlfcn.h>','#include <dlfcn.h>\n#include <mach-o/loader.h>',1)

anchor='''static NSString *DuoSDKMaintenanceForSelectionInternal(NSInteger action, NSString *selectedIDsJSON) {'''
assert s.count(anchor)==1
helper=r'''
// Inferred app bundle path is never trusted directly: the cache parser already
// validates UUID ownership and .app extension; we repeat that validation,
// validate the *installed* CFBundleIdentifier, and read only the signed binary
// header. We do not use the SDK number from the editable LaunchServices record
// as evidence of an application's original SDK.
static NSArray<NSNumber *> *duoInstalledSDKForRow(NSDictionary *row, NSString *group) {
    NSString *path = row[@"bundlePath"];
    NSString *appID = row[@"id"];
    if (![path isKindOfClass:NSString.class] || ![appID isKindOfClass:NSString.class] ||
        ![path.pathExtension isEqualToString:@"app"]) return nil;
    NSString *parent = path.stringByDeletingLastPathComponent;
    if (![[NSUUID alloc] initWithUUIDString:parent.lastPathComponent] ||
        ![parent.stringByDeletingLastPathComponent
              isEqualToString:@"/private/var/containers/Bundle/Application"] ||
        ![path isEqualToString:[parent stringByAppendingPathComponent:path.lastPathComponent]])
        return nil;

    int64_t token = worse_query(path, group, false, true);
    if (token < 0) return nil;
    int appDir = open(path.fileSystemRepresentation,
                      O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    NSArray<NSNumber *> *answer = nil;
    @try {
        if (appDir < 0) return nil;
        int plistFD = openat(appDir, "Info.plist", O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
        if (plistFD < 0) return nil;
        struct stat pStat;
        BOOL validPlist = !fstat(plistFD, &pStat) && S_ISREG(pStat.st_mode) &&
                          pStat.st_size > 0 && pStat.st_size <= 2 * 1024 * 1024;
        NSData *plistData = validPlist ? contentsAtMost(plistFD, 2 * 1024 * 1024) : nil;
        close(plistFD);
        NSDictionary *info = plistData ?
            [NSPropertyListSerialization propertyListWithData:plistData
                        options:NSPropertyListImmutable format:NULL error:nil] : nil;
        NSString *exe = [info isKindOfClass:NSDictionary.class] ? info[@"CFBundleExecutable"] : nil;
        if (![info[@"CFBundleIdentifier"] isEqualToString:appID] ||
            ![exe isKindOfClass:NSString.class] || !exe.length ||
            ![exe isEqualToString:exe.lastPathComponent] ||
            [exe isEqualToString:@"."] || [exe isEqualToString:@".."]) return nil;

        int exeFD = openat(appDir, exe.fileSystemRepresentation,
                           O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
        if (exeFD < 0) return nil;
        struct stat eStat;
        struct mach_header_64 h = {0};
        BOOL valid = !fstat(exeFD, &eStat) && S_ISREG(eStat.st_mode) &&
                     eStat.st_size > sizeof(h) && 
                     pread(exeFD, &h, sizeof(h), 0) == sizeof(h) &&
                     h.magic == MH_MAGIC_64 && h.ncmds > 0 && h.ncmds <= 4096 &&
                     h.sizeofcmds <= 1024 * 1024 &&
                     h.sizeofcmds <= (uint64_t)eStat.st_size - sizeof(h);
        NSMutableData *commands = valid ? [NSMutableData dataWithLength:h.sizeofcmds] : nil;
        if (valid && pread(exeFD, commands.mutableBytes, commands.length, sizeof(h)) != commands.length)
            valid = NO;
        close(exeFD);
        if (!valid) return nil;

        const uint8_t *bytes = commands.bytes;
        NSUInteger cursor = 0;
        uint32_t sdk = 0;
        uint32_t minimumSdk = 0;
        for (uint32_t n = 0; n < h.ncmds; ++n) {
            if (cursor > commands.length || commands.length - cursor < sizeof(struct load_command))
                return nil;
            struct load_command command;
            memcpy(&command, bytes + cursor, sizeof(command));
            if (command.cmdsize < sizeof(command) ||
                command.cmdsize > commands.length - cursor) return nil;
            if (command.cmd == LC_BUILD_VERSION &&
                command.cmdsize >= sizeof(struct build_version_command)) {
                struct build_version_command b;
                memcpy(&b, bytes + cursor, sizeof(b));
                if (b.platform == PLATFORM_IOS) sdk = b.sdk;
            } else if (command.cmd == LC_VERSION_MIN_IPHONEOS &&
                       command.cmdsize >= sizeof(struct version_min_command)) {
                struct version_min_command v;
                memcpy(&v, bytes + cursor, sizeof(v));
                minimumSdk = v.sdk;
            }
            cursor += command.cmdsize;
        }
        if (!sdk) sdk = minimumSdk;
        NSUInteger major = sdk >> 16, minor = (sdk >> 8) & 255, patch = sdk & 255;
        NSOperatingSystemVersion os = NSProcessInfo.processInfo.operatingSystemVersion;
        if (major < 1 || major > (NSUInteger)os.majorVersion || minor > 99 || patch > 99)
            return nil;
        if (major == (NSUInteger)os.majorVersion &&
            (minor > (NSUInteger)os.minorVersion ||
             (minor == (NSUInteger)os.minorVersion && patch > (NSUInteger)os.patchVersion)))
            return nil;
        answer = @[@(major), @(minor), @(patch)];
    } @finally {
        if (appDir >= 0) close(appDir);
        worse_query_release(token);
    }
    return answer;
}

'''
s=s.replace(anchor,helper+anchor,1)

anchor='''if (action < 0 || action > 3) return @"Unsupported action. No changes made.";'''
assert s.count(anchor)==1
s=s.replace(anchor,'''if (action < 0 || action > 5) return @"Unsupported action. No changes made.";''',1)

# Insert action 5 alongside action 1 selection; the target SDK is *always*
# overwritten with the value from the actual on-device executable.
needle='''        if (action == 1) {
            NSData *json = [selectedIDsJSON dataUsingEncoding:NSUTF8StringEncoding];'''
assert s.count(needle)==1
s=s.replace(needle,'''        if (action == 1 || action == 5) {
            BOOL recoverFromExecutable = action == 5;
            NSData *json = [selectedIDsJSON dataUsingEncoding:NSUTF8StringEncoding];''',1)

# Target version validation in user's string request is handled for recovery
# because the final target will be replaced with the trusted SDK.
needle='''                if ([target[0] integerValue] != os.majorVersion ||
                    [target[1] integerValue] > os.minorVersion ||
                    ([target[1] integerValue] == os.minorVersion &&
                     [target[2] integerValue] > os.patchVersion))'''
assert s.count(needle)==1
s=s.replace(needle,'''                if (!recoverFromExecutable &&
                    ([target[0] integerValue] != os.majorVersion ||
                     [target[1] integerValue] > os.minorVersion ||
                     ([target[1] integerValue] == os.minorVersion &&
                      [target[2] integerValue] > os.patchVersion)))''',1)

needle='''                    NSArray *target = targets[row[@"id"]];
                    if ([target isEqual:row[@"before"]])'''
assert s.count(needle)==1
s=s.replace(needle,'''                    NSArray *target = recoverFromExecutable ?
                        duoInstalledSDKForRow(row, group) : targets[row[@"id"]];
                    if (!target)
                        return @"Could not verify the installed app's original executable SDK. "
                               @"No changes made. Try ordinary recorded-history restore.";
                    if ([target isEqual:row[@"before"]])''',1)

# Show a clear label in the review log; don't claim a successful write until
# the existing checksum-verified transaction confirms it.
needle='''        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"], *after = row[@"after"];
            [report appendFormat:@"• %@ · %@.%@.%@ → %@.%@.%@\\n",'''
assert s.count(needle)==1
s=s.replace(needle,'''        if (action == 5)
            [report appendString:@"Verified installed executable SDK recovery: "
                                 @"no app binary or signature will be modified.\\n"];
        for (NSDictionary *row in rows) {
            NSArray *before = row[@"before"], *after = row[@"after"];
            [report appendFormat:@"• %@ · %@.%@.%@ → %@.%@.%@\\n",''',1)

p.write_text(s)

p=src/"App.swift"
s=p.read_text()
anchor='''    @State private var confirmRestore = false'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
    @State private var confirmInstalledSDKRecovery = false''',1)

anchor='''                        Button("Apply to \\(selectedIDs.count) selected app(s)") {
                            confirmApply = true
                        }
                        .disabled(!canApply)'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
                        Button("Stabilise selected: restore SDK from installed app") {
                            confirmInstalledSDKRecovery = true
                        }
                        .disabled(selectedIDs.isEmpty)
                        .foregroundStyle(.orange)''',1)

anchor='''            .confirmationDialog("Restore selected SDK changes?", isPresented: $confirmRestore) {'''
assert s.count(anchor)==1
s=s.replace(anchor,'''            .confirmationDialog("Restore SDK from installed executable?", 
                                isPresented: $confirmInstalledSDKRecovery) {
                Button("Restore verified SDK for \\(selectedIDs.count) app(s)",
                       role: .destructive) { run(5) }
            } message: {
                Text("For selected apps only, reads their actual signed executable's SDK and "
                     + "restores that SDK in the LaunchServices cache. May bring back "
                     + "compatibility black bars. Does NOT patch or re-sign apps. "
                     + "If source verification fails, nothing is changed. "
                     + "Restart your iPhone after a confirmed change.")
            }
            .confirmationDialog("Restore selected SDK changes?", isPresented: $confirmRestore) {''',1)

needle='''        if action == 1 && !canApply { return }'''
assert s.count(needle)==1
s=s.replace(needle,needle+'''
        if action == 5 && selectedIDs.isEmpty { return }''',1)
needle='''        let prepared = action == 1 ? changes :
            action == 2 ? restoreIDs.sorted().map { ["id": $0] } : []'''
assert s.count(needle)==1
s=s.replace(needle,'''        let prepared = action == 1 ? changes :
            action == 2 ? restoreIDs.sorted().map { ["id": $0] } : []''',1)
needle='''        if action == 2 {
            encoded = try? JSONSerialization.data(withJSONObject: restoreIDs.sorted())
        } else {'''
assert s.count(needle)==1
s=s.replace(needle,'''        if action == 2 || action == 5 {
            encoded = try? JSONSerialization.data(
                withJSONObject: action == 5 ? selectedIDs.sorted() : restoreIDs.sorted())
        } else {''',1)

needle='''                if action == 1 && value.contains("DUO_BATCH_APLICADO") {
                    for id in requestedIDs {
                        if let preferred = requestedTargets[id] { savedTargets[id] = preferred }
                    }
                    persistPreferences()
                }'''
assert s.count(needle)==1
s=s.replace(needle,'''                if action == 1 && value.contains("DUO_BATCH_APLICADO") {
                    for id in requestedIDs {
                        if let preferred = requestedTargets[id] { savedTargets[id] = preferred }
                    }
                    persistPreferences()
                }
                if action == 5 && value.contains("DUO_BATCH_APLICADO") {
                    for id in requestedIDs { savedTargets.removeValue(forKey: id) }
                    persistPreferences()
                }''',1)

p.write_text(s)
print("Added verified original-executable SDK recovery using signed app bundles. "
      "No app binary writes, transactional LaunchServices-only changes.")
