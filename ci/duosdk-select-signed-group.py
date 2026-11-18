#!/usr/bin/env python3
"""Choose a safely unused App Group from the *installed signature*, never the provisioning profile.
The profile is an allowance list, not evidence of the application's effective entitlements.
No personal profile, certificate, device identifiers, or App Group names are embedded here.
"""
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve() / "Sources"
p = src / "XCacheTransaction.m"
s = p.read_text(encoding="utf-8")
assert '#import "worse_query.h"' in s
s = s.replace('#import "worse_query.h"',
              '#import "worse_query.h"\n#import <Security/Security.h>', 1)

insertion = r'''
// Every caller uses a value from the app's *effective code-signature entitlements*.
// A group appearing in a provisioning profile alone is NOT enough.
static NSArray<NSString *> *DuoSDKSignedGroups(void) {
    SecTaskRef task = SecTaskCreateFromSelf(kCFAllocatorDefault);
    if (!task) return @[];
    CFTypeRef value = SecTaskCopyValueForEntitlement(
        task, CFSTR("com.apple.security.application-groups"), NULL);
    CFRelease(task);
    if (!value) return @[];
    if (CFGetTypeID(value) != CFArrayGetTypeID()) {
        CFRelease(value);
        return @[];
    }
    NSArray *declared = CFBridgingRelease(value);
    NSMutableArray<NSString *> *groups = [NSMutableArray array];
    for (id item in declared) {
        if ([item isKindOfClass:NSString.class] &&
            [item hasPrefix:@"group."] && [item length] > 6) {
            [groups addObject:item];
        }
    }
    return [groups sortedArrayUsingSelector:@selector(compare:)];
}

// worse_query temporarily replaces Library/Caches with a symlink. Never do
// that to an App Group with any existing data or symlinks, even for a read-only
// check. A provisioning profile may contain groups shared with other apps.
static BOOL DuoSDKIsUnusedGroup(NSURL *rootURL) {
    if (!rootURL.isFileURL) return NO;
    NSString *root = rootURL.path;
    struct stat rootStat;
    if (lstat(root.fileSystemRepresentation, &rootStat) != 0 ||
        !S_ISDIR(rootStat.st_mode)) return NO;
    NSFileManager *fm = NSFileManager.defaultManager;
    NSMutableArray<NSString *> *pending = [NSMutableArray arrayWithObject:root];
    NSUInteger visited = 0;
    while (pending.count) {
        NSString *folder = pending.lastObject;
        [pending removeLastObject];
        NSArray<NSString *> *entries = [fm contentsOfDirectoryAtPath:folder error:nil];
        if (!entries) return NO;
        for (NSString *name in entries) {
            if (++visited > 96) return NO;
            NSString *path = [folder stringByAppendingPathComponent:name];
            struct stat info;
            if (lstat(path.fileSystemRepresentation, &info) != 0 ||
                !S_ISDIR(info.st_mode)) return NO;  // no files or symlinks
            [pending addObject:path];
        }
    }
    return YES;
}

// Only select groups the installed IPA has actually been signed with.
// A group must also have an accessible and completely unused container.
// No group identifiers are printed into logs or committed to GitHub.
static NSString *DuoSDKChooseSigningGroup(NSString **reason) {
    NSArray<NSString *> *signedGroups = DuoSDKSignedGroups();
    if (signedGroups.count == 0) {
        if (reason) *reason =
            @"No App Group entitlement exists in this installed app's signature. "
             "The provisioning profile alone does not grant it. "
             "Signulous must include an authorised App Group when signing the IPA. "
             "No changes made.";
        return nil;
    }
    NSUInteger accessible = 0, unused = 0;
    for (NSString *identifier in signedGroups) {
        NSURL *container = [NSFileManager.defaultManager
            containerURLForSecurityApplicationGroupIdentifier:identifier];
        if (!container) continue;
        ++accessible;
        if (!DuoSDKIsUnusedGroup(container)) continue;
        ++unused;
        return identifier;
    }
    if (reason) {
        *reason = [NSString stringWithFormat:
            @"The signature declares %lu App Group(s); %lu container(s) were accessible. "
             "None is safely unused, so DuoSDK will not replace an existing "
             "App Group cache. No changes made.",
             (unsigned long)signedGroups.count, (unsigned long)accessible];
    }
    return nil;
}

// Shared with older debug-only entry points; never fall back to the
// original developer's hard-coded group.
NSString *DuoSDKSigningGroup(void) {
    return DuoSDKChooseSigningGroup(NULL);
}

'''
mark="NSString *DuoSDKMaintenance(NSInteger action) {"
assert s.count(mark) == 1
s=s.replace(mark,insertion+mark,1)
before = '''    NSString *group = @"group.dev.aritzmendez.gestaltx";
    NSURL *groupRoot = [[NSFileManager defaultManager] containerURLForSecurityApplicationGroupIdentifier:group];
    if (!groupRoot) {
        return @"App Group unavailable: group.dev.aritzmendez.gestaltx. This is usually a signing/provisioning entitlement mismatch. The unsigned GitHub IPA cannot supply the entitlement by itself; your signed IPA and its provisioning profile must both authorise this exact group. No changes made.";
    }'''
after = '''    NSString *groupReason = nil;
    NSString *group = DuoSDKChooseSigningGroup(&groupReason);
    if (!group) return groupReason ?: @"No usable signed App Group found. No changes made.";
    // The group was selected from actual signed entitlements, and its cache
    // directory was checked for existing files/symlinks above.'''
assert s.count(before) == 1, "Expected prior signing diagnostic was not found"
s=s.replace(before,after,1)
p.write_text(s,encoding="utf-8")

# Legacy debug-only entrypoints must use the same signed-group selection,
# rather than referencing the upstream author's group.
p=src/"XFlags.m"
s=p.read_text(encoding="utf-8")
a='static NSString *const Group = @"group.dev.aritzmendez.gestaltx";'
b='extern NSString *DuoSDKSigningGroup(void);\n#define Group (DuoSDKSigningGroup())'
assert s.count(a)==1
p.write_text(s.replace(a,b,1),encoding="utf-8")

# Do not leave the upstream author's incompatible App Group in the unsigned
# source entitlement template. Signulous will issue the final code signature;
# its effective signed entitlements are interrogated at runtime.
p=Path(sys.argv[1]).resolve()/"GestaltX.entitlements"
p.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict/></plist>
''',encoding="utf-8")
print("DuoSDK now selects only entitled, accessible, empty App Groups; no group identifiers in output.")
