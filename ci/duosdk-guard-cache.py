#!/usr/bin/env python3
"""Guard App Group Caches against deletion, preserve failures as diagnostics.
Runs after the other DuoSDK adaptation scripts.
"""
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve() / "Sources"
p = src / "worse_query.m"
s = p.read_text(encoding="utf-8")

before = '''// Remove symlink and recreate Caches directory
static void clean_symlink(NSString *group) {
    if (group != NULL) {
        NSFileManager *files = [NSFileManager defaultManager];
        NSURL *groupRoot = [files containerURLForSecurityApplicationGroupIdentifier: group];
        if (groupRoot) {
            NSURL *caches = [groupRoot URLByAppendingPathComponent: @"Library/Caches"];
            [files removeItemAtURL: caches error: nil];
            [files createDirectoryAtURL: caches withIntermediateDirectories: false attributes: nil error: nil];
        }
    }
    return;
}'''
after = '''// Restore only the precise symlink created by this operation.
// Never delete a populated directory or an unrelated symlink.
static BOOL clean_symlink(NSString *group, NSString *expectedTarget) {
    if (!group || !expectedTarget) return NO;
    NSURL *root = [[NSFileManager defaultManager]
        containerURLForSecurityApplicationGroupIdentifier:group];
    if (!root) return NO;
    NSString *path = [[root URLByAppendingPathComponent:@"Library/Caches"] path];
    struct stat a, b;
    if (lstat(path.fileSystemRepresentation, &a) != 0 || !S_ISLNK(a.st_mode)) return NO;
    char actual[PATH_MAX];
    ssize_t n = readlink(path.fileSystemRepresentation, actual, sizeof(actual) - 1);
    if (n < 0 || n >= sizeof(actual) - 1) return NO;
    actual[n] = '\\0';
    if (strcmp(actual, expectedTarget.fileSystemRepresentation) != 0 ||
        lstat(path.fileSystemRepresentation, &b) != 0 ||
        a.st_dev != b.st_dev || a.st_ino != b.st_ino) return NO;
    if (unlink(path.fileSystemRepresentation) != 0) return NO;
    return mkdir(path.fileSystemRepresentation, 0700) == 0;
}'''
assert s.count(before) == 1, "Original cleanup implementation changed"
s = s.replace(before, after, 1)
s = s.replace('#include <sys/stat.h>', '#include <sys/stat.h>\n#include <unistd.h>\n#include <errno.h>\n#include <limits.h>\n#include <string.h>', 1)

before = '''    [files removeItemAtPath: caches error: nil];
    if ([files createSymbolicLinkAtPath: caches withDestinationPath: target error: nil] == false) {
        dlclose(mgr);
        return -4; // Failed to create symlink
    }'''
after = '''    // rmdir is intentionally used instead of recursive removeItemAtPath:
    // it can only remove an empty directory, even if another app raced us.
    struct stat cacheState;
    if (lstat(caches.fileSystemRepresentation, &cacheState) == 0) {
        if (!S_ISDIR(cacheState.st_mode) ||
            rmdir(caches.fileSystemRepresentation) != 0) {
            query_free(query);
            dlclose(mgr);
            return -7; // Populated cache, symlink, or failed safe removal
        }
    } else if (errno != ENOENT) {
        query_free(query);
        dlclose(mgr);
        return -7;
    }
    if (symlink(target.fileSystemRepresentation, caches.fileSystemRepresentation) != 0) {
        // Re-create the empty directory we removed, without removing any new data.
        if (lstat(caches.fileSystemRepresentation, &cacheState) != 0 && errno == ENOENT)
            mkdir(caches.fileSystemRepresentation, 0700);
        query_free(query);
        dlclose(mgr);
        return -4;
    }'''
assert s.count(before) == 1, "Original symlink installation changed"
s = s.replace(before, after, 1)

assert s.count("clean_symlink(group);") == 3
s = s.replace("        clean_symlink(group);\n        return -5;",
              "        BOOL cleaned = clean_symlink(group, target);\n        return cleaned ? -5 : -8;", 1)
s = s.replace("        clean_symlink(group);\n        return -6;",
              "        BOOL cleaned = clean_symlink(group, target);\n        return cleaned ? -6 : -8;", 1)
s = s.replace("    clean_symlink(group);\n    \n    return handle;",
              "    if (!clean_symlink(group, target)) {\n        worse_query_release(handle);\n        return -8;\n    }\n    \n    return handle;", 1)
assert "clean_symlink(group);" not in s
p.write_text(s, encoding="utf-8")

# Retain the last sandbox error, and pass it back to the user without private
# cache paths or App Group names.
p = src / "XCacheTransaction.m"
s = p.read_text(encoding="utf-8")
header = 'NSData *XBuildPatchedArchive(NSData *input, NSMutableString *report);'
assert s.count(header) == 1
s = s.replace(header, header + '\nstatic int64_t DuoSDKLastCacheError = 0;', 1)
call = '''        int64_t token = worse_query(directory, group, false, true);
        if (token < 0) continue;'''
replaced = '''        int64_t token = worse_query(directory, group, false, true);
        if (token < 0) {
            DuoSDKLastCacheError = token;
            continue;
        }'''
assert s.count(call) == 1
s = s.replace(call, replaced, 1)
note = '''            return [NSString stringWithFormat:@"App Group is accessible; cache discovery found %lu candidate directory(s), but none passed the required access and single-store checks on iOS 27.2.1. No changes made. This is a cache access/layout issue, not the original iOS version warning.", (unsigned long)candidates.count];'''
newNote = '''            return [NSString stringWithFormat:@"App Group cache is available, but %lu LaunchServices directory candidate(s) failed accessibility or store validation. Last sandbox-extension error: %lld (0 means directory/store validation rather than a sandbox error). Nothing changed.", (unsigned long)candidates.count, (long long)DuoSDKLastCacheError];'''
assert s.count(note) == 1
s = s.replace(note, newNote, 1)
p.write_text(s, encoding="utf-8")
print("Guarded App Group cache symlink; rmdir cannot erase populated caches; exposed failure categories.")
