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
assert '#include "worse_query.h"' in s
s = s.replace('#include "worse_query.h"',
              '#import "worse_query.h"\n#import <Security/Security.h>\n#include <errno.h>', 1)

insertion = r'''
// Every caller uses a value from the app's *effective code-signature entitlements*.
// A group appearing in a provisioning profile alone is NOT enough.
static NSArray<NSString *> *DuoSDKSignedGroups(void) {
    // SecTask is intentionally not declared in the public iOS SDK headers.
    // Resolve it at runtime, and fail closed if iOS doesn't export it.
    typedef void *(*DuoTaskCreate)(CFAllocatorRef);
    typedef CFTypeRef (*DuoTaskEntitlement)(void *, CFStringRef, CFErrorRef *);
    void *security = dlopen("/System/Library/Frameworks/Security.framework/Security",
                            RTLD_LAZY | RTLD_LOCAL);
    DuoTaskCreate makeTask = (DuoTaskCreate)dlsym(security ?: RTLD_DEFAULT, "SecTaskCreateFromSelf");
    DuoTaskEntitlement lookup = (DuoTaskEntitlement)dlsym(security ?: RTLD_DEFAULT,
                                                         "SecTaskCopyValueForEntitlement");
    if (!makeTask || !lookup) {
        if (security) dlclose(security);
        return @[];
    }
    void *task = makeTask(kCFAllocatorDefault);
    if (!task) {
        if (security) dlclose(security);
        return @[];
    }
    CFTypeRef value = lookup(task, CFSTR("com.apple.security.application-groups"), NULL);
    CFRelease((CFTypeRef)task);
    if (security) dlclose(security);
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

// Limit checks to the directory the original PoC actually replaces.
// iOS may create unrelated App Group metadata outside Library/Caches.
// Never touch a populated cache, symlink, or unreadable directory.
static NSInteger DuoSDKCacheSafety(NSURL *rootURL) {
    if (!rootURL.isFileURL) return -1;
    NSString *root = rootURL.path;
    struct stat st;
    if (lstat(root.fileSystemRepresentation, &st) != 0 || !S_ISDIR(st.st_mode)) return -1;
    NSString *library = [root stringByAppendingPathComponent:@"Library"];
    if (lstat(library.fileSystemRepresentation, &st) != 0 || !S_ISDIR(st.st_mode)) return -2;
    NSString *caches = [library stringByAppendingPathComponent:@"Caches"];
    if (lstat(caches.fileSystemRepresentation, &st) != 0) {
        return errno == ENOENT ? 1 : -1;
    }
    if (!S_ISDIR(st.st_mode)) return 0;
    NSError *problem = nil;
    NSArray<NSString *> *contents = [NSFileManager.defaultManager
        contentsOfDirectoryAtPath:caches error:&problem];
    if (problem || !contents) return -1;
    return contents.count == 0 ? 1 : 0;
}

// Only select groups the installed IPA has actually been signed with.
// A group must have an accessible App Group root and an empty Library/Caches.
// No group identifiers are printed into logs or committed to GitHub.
static NSString *DuoSDKChooseSigningGroup(NSString **reason) {
    NSArray<NSString *> *signedGroups = DuoSDKSignedGroups();
    if (signedGroups.count == 0) {
        if (reason) *reason =
            @"No App Group entitlement exists in this installed app's signature. "
             @"The provisioning profile alone does not grant it. "
             @"Signulous must include an authorised App Group when signing the IPA. "
             @"No changes made.";
        return nil;
    }
    NSUInteger accessible = 0, populated = 0, missingLibrary = 0, unreadable = 0;
    for (NSString *identifier in signedGroups) {
        NSURL *container = [NSFileManager.defaultManager
            containerURLForSecurityApplicationGroupIdentifier:identifier];
        if (!container) continue;
        ++accessible;
        NSInteger condition = DuoSDKCacheSafety(container);
        if (condition == 1) return identifier;
        if (condition == 0) ++populated;
        else if (condition == -2) ++missingLibrary;
        else ++unreadable;
    }
    if (reason) {
        *reason = [NSString stringWithFormat:
            @"App Groups signed: %lu; accessible: %lu. Cache conditions: "
             @"%lu populated or symlinked, %lu without Library, %lu unreadable. "
             @"No group has an empty accessible cache. Existing data was not touched. "
             @"No changes made.",
             (unsigned long)signedGroups.count, (unsigned long)accessible,
             (unsigned long)populated, (unsigned long)missingLibrary,
             (unsigned long)unreadable];
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
print("DuoSDK now selects signed groups with an empty cache, classifies others; no group identifiers in output.")
