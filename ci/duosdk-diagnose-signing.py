#!/usr/bin/env python3
"""Make iOS 27.2.1 DuoSDK cache discovery failures actionable and non-destructive."""
from pathlib import Path
import sys

p=Path(sys.argv[1])/"Sources"/"XCacheTransaction.m"
s=p.read_text()
before='''    NSString *group = @"group.dev.aritzmendez.gestaltx";
    int dir = -1;
    int64_t token = DuoSDKOpenCache(group, &dir);
    @try {
        if (dir < 0) return @"Could not locate an accessible, unambiguous LaunchServices v2 cache on iOS 27.2.1. No changes made. Check App Group signing and iOS permissions.";'''
assert before in s, "Expected iOS 27.2.1 code not present"
after='''    NSString *group = @"group.dev.aritzmendez.gestaltx";
    NSURL *groupRoot = [[NSFileManager defaultManager] containerURLForSecurityApplicationGroupIdentifier:group];
    if (!groupRoot) {
        return @"App Group unavailable: group.dev.aritzmendez.gestaltx. This is usually a signing/provisioning entitlement mismatch. The unsigned GitHub IPA cannot supply the entitlement by itself; your signed IPA and its provisioning profile must both authorise this exact group. No changes made.";
    }
    NSArray<NSString *> *candidates = DuoSDKCacheDirectories();
    if (candidates.count == 0) {
        return @"App Group is accessible, but LaunchServices cache discovery returned no candidates on iOS 27.2.1. No changes made. Do not use a cache path copied from another iOS installation.";
    }
    int dir = -1;
    int64_t token = DuoSDKOpenCache(group, &dir);
    @try {
        if (dir < 0) {
            return [NSString stringWithFormat:@"App Group is accessible; cache discovery found %lu candidate directory(s), but none passed the required access and single-store checks on iOS 27.2.1. No changes made. This is a cache access/layout issue, not the original iOS version warning.", (unsigned long)candidates.count];
        }'''
s=s.replace(before,after,1)
p.write_text(s)
print("Added separate App Group, cache discovery and access diagnostics; original rollback and validation unchanged.")
