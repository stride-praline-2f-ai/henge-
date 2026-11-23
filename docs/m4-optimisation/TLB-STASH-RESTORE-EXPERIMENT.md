# TLB stash restore experiment

The build 128 Speedometer score stayed near 6 in the reported test. The literal-load experiment covers a restricted instruction form. This patch evaluates a separate cost in the MMU path that resumes cached user mappings on TTBR0 switches.

Earlier device logs included busy windows with 5,803 to 9,314 stash restores per second, averaging 100 to 124 entries per restore. Those counters include reads and writes and lack benchmark boundaries. The existing restore path resolves a writable entry's host RAM region to publish the write hint, fences once for the batch, then resolves the same backing again before examining the code-page flag.

The candidate keeps the validated code-page pointer and destination TLB entry until the post-fence check. The flag is still read live after the same sequentially consistent fence. Missing RAM drops write access, stale stash generations are discarded, and invalidated entries are skipped. The scratch array grows from 2 KiB to 16 KiB per active invocation. Both the stash and pending guards are bounded by the original 1,024-entry cap.

## Linux x86-64 proxy results

Seven alternating pairs were pinned to one logical CPU. The fixture links the production `core/mmu.c` from build 128 and from the candidate in separate binaries, with the same compiler flags. The workload restores previously stashed writable entries and clears the previous batch between iterations.

| Layout | Entries | Build 128 median ns/entry | Candidate median ns/entry | Median paired reduction |
| --- | ---: | ---: | ---: | ---: |
| Existing interleaved | 128 | 5.928 | 5.214 | 12.2% |
| Existing interleaved | 1,024 | 6.418 | 6.088 | 5.0% |
| Default table-major | 128 | 5.879 | 5.566 | 5.3% |
| Default table-major | 1,024 | 6.015 | 5.384 | 11.0% |

The fixture also passed under AddressSanitizer and UndefinedBehaviorSanitizer. It covers maximum stash size, protected code pages, invalidated entries, missing RAM, read-only mappings and stale generations. The timing is for the C restore path on Linux x86-64. ARM64 timings, the duration of the restore path during Speedometer, and the on-device effect remain unmeasured.

This patch is for review. It is outside the IPA manifest. The next performance decision needs a capture bounded by one reproducible benchmark run so translation, dispatch, memory helpers and eviction costs can be attributed to that workload.
