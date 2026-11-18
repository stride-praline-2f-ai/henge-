#!/usr/bin/env python3
"""Add read-only structural detail when iOS 27.2.1 cache format verification fails.
Do not weaken the original validation or alter the target cache.
"""
from pathlib import Path
import sys

src=Path(sys.argv[1])/"Sources"
h=src/"DuoSDKPlan.h"
s=h.read_text()
declaration="NSString *DuoSDKPlanLayoutReport(NSData *store);"
assert declaration not in s
s+="\n// Diagnostic only: returns aggregate record counts, no installed-app identifiers.\n"+declaration+"\n"
h.write_text(s)

p=src/"DuoSDKPlan.m"
s=p.read_text()
addition=r'''

// Diagnostic intentionally uses the existing checked table parser and reads
// no private record fields unless their boundaries are known. It never writes.
NSString *DuoSDKPlanLayoutReport(NSData *store) {
    const uint8_t *bytes = store.bytes;
    NSUInteger length = store.length;
    if (length < 0x64) return @"Store header is shorter than 0x64 bytes";
    if (memcmp(bytes, "bdsl\x02", 5) != 0)
        return @"CoreServicesStore magic or major version differs";
    if (!(read32(bytes, 20) & 0x40000000))
        return @"CoreServicesStore expected catalog flag is absent";
    NSDictionary *catalog = tableUnits(store, 20);
    if (!catalog) return @"Catalog hash table could not be verified";
    NSDictionary *bundles = nil, *strings = nil;
    for (NSNumber *entry in catalog.allValues) {
        NSUInteger unit = entry.unsignedIntegerValue;
        NSString *name = unitString(store, unit, 0x30);
        if ([name isEqualToString:@"Bundle"]) bundles = tableUnits(store, unit);
        if ([name isEqualToString:@"<string>"]) strings = tableUnits(store, unit);
    }
    if (!bundles) return @"Catalog has no verified Bundle table";
    if (!strings) return @"Catalog has no verified string table";

    NSUInteger expectedSize = 0, fieldPattern = 0, signerCount = 0;
    NSUInteger placeholderCount = 0, otherSize = 0;
    NSMutableDictionary<NSNumber *, NSNumber *> *sizes = [NSMutableDictionary dictionary];
    for (NSNumber *entry in bundles.allValues) {
        NSUInteger unit = entry.unsignedIntegerValue;
        if (unit > length || length - unit < 8) continue;
        NSUInteger size = read32(bytes, unit + 4);
        if (size > length - unit - 8) continue;
        if (size != 604) {
            ++otherSize;
            if (sizes.count < 12 || sizes[@(size)])
                sizes[@(size)] = @([sizes[@(size)] unsignedIntegerValue] + 1);
            continue;
        }
        ++expectedSize;
        NSUInteger body = unit + 8;
        uint32_t key = read32(bytes, body + 0x0c);
        if (read32(bytes, body + 0x18) != key ||
            read32(bytes, body + 0x1c) != 2) continue;
        ++fieldPattern;
        NSString *signer = recordString(store, strings, body, 0x88);
        if ([signer isEqualToString:@"Apple iPhone OS Application Signing"] ||
            [signer isEqualToString:@"TestFlight Beta Distribution"])
            ++signerCount;
        NSString *bundleName = recordString(store, strings, body, 0x144);
        NSString *placeholder = recordString(store, strings, body, 0x244);
        if ([bundleName hasSuffix:@".app"] &&
            [placeholder.lastPathComponent isEqualToString:@"SerializedPlaceholder.ipa"])
            ++placeholderCount;
    }
    NSArray *orderedSizes = [[sizes allKeys] sortedArrayUsingSelector:@selector(compare:)];
    NSMutableArray<NSString *> *sizeCounts = [NSMutableArray array];
    for (NSNumber *key in orderedSizes)
        [sizeCounts addObject:[NSString stringWithFormat:@"%@:%@", key, sizes[key]]];
    return [NSString stringWithFormat:
        @"Catalog entries %lu; Bundle entries %lu; string entries %lu. "
         @"Bundle record sizes: 604=%lu, other=%lu (%@). "
         @"Expected field pattern=%lu, Apple/TestFlight signer=%lu, "
         @"placeholder pattern=%lu. No private bundle IDs collected.",
         (unsigned long)catalog.count,
         (unsigned long)bundles.count, (unsigned long)strings.count,
         (unsigned long)expectedSize, (unsigned long)otherSize,
         [sizeCounts componentsJoinedByString:@", "],
         (unsigned long)fieldPattern, (unsigned long)signerCount,
         (unsigned long)placeholderCount];
}
'''
assert "DuoSDKPlanLayoutReport(" not in s
p.write_text(s+addition)

p=src/"XCacheTransaction.m"
s=p.read_text()
old='if (!rows || matched < 10 || rows.count > 400) return @"This cache layout could not be verified. No changes made.";'
assert s.count(old)==1,(s.count(old),"Layout validation anchor changed")
new='''if (!rows || matched == 0 || rows.count > matched || rows.count > 400) {
            NSString *why = !rows ? @"Parser rejected one or more structural checks" :
                matched == 0 ? @"No verified eligible app records" :
                rows.count > matched ? @"Proposed changes exceed verified eligible records" :
                @"More than 400 proposed modifications";
            NSString *details = DuoSDKPlanLayoutReport(original);
            return [NSString stringWithFormat:
                @"Read-only layout diagnosis: %@. Recognised apps: %lu, proposed changes: %lu. %@. No changes made.",
                why, (unsigned long)matched,
                (unsigned long)(rows ? rows.count : 0), details];
        }'''
s=s.replace(old,new,1)
p.write_text(s)
print("Added aggregate layout diagnostics and replaced arbitrary ten-app floor with consistency limits.")
