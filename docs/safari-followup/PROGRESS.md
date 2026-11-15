# Safari replay follow-up

Report on117: Safari page loading, scrolling/typing and moving its own window are slow; Notes, Settings and Roblox comparatively usable. Window movement points beyond network loading but does not prove an exclusive cause.

## Implementation

Runtime `458eb0ff26ae776fadf8090d0ec3a5cfa1c523b1`, exported patch `53b3f15acb3c4a75fa42f96ee0ddf7e78732852472dda92aeecb7e39ab4673ef` preserves all117 CPU/JIT code.

- Default on: existing command/task-scoped immutable GPU-object/page-metadata reuse. Mutable resource metadata still checked; HV_GPU_BATCH_CACHE=0 preserves reference mode. Rejected commands advance epochs; wrap saturates to uncached mode.
- Share a full-byte backing scan only across exact all-pages/layout aliases within one command. Independent allocations and new commands recheck. Backend ownership remains immutable.
- Omit empty classic submissions before successful Metal4 handoff. Real legacy/upload work, the runtime bidirectional signal/wait bridge and final guest completion remain.
- Adapt Oliver Ames upstream PR187 two-level surface tables above64MiB; flatten leaves once for mapping and exact registry identity. Invalid RAM and failed mappings reject incomplete allocations. Presence of such surfaces in the reported Safari workload is unproven.
- Coalesce contiguous physical pages only within a checked host RAM span; split RAM regions safely and fall back to individual pages after a host rejection. HV_PVG_REMAP_SINGLE=1 is the reference. Existing surface logs now show table level, page count and actual remap calls.
- Added reuse/epoch/real-Mach-mapping regressions to the existing final sanitizer gate. No extra runtime timers, UI settings, resolution reduction or refresh cap.

## Verification

[Focused run 43736645861](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43736645861) passed on exact wrapper `65bede48f3838d2c04a7fd11a3acb16a63ba8278`. Source reconstruction, ASan/UBSan metadata/alias/wrap checks, real GPU pixels/ownership, recorded Metal4 queue/fence lifetimes and production macOS/iOS renderer compilation passed. Host GPU: Apple Paravirtual device.

Fixture reductions:10000 repeated uses ->1 full320-page check;10001 immutable accesses ->1 metadata read;4097 contiguous pages ->1 real Mach call instead of4097, all67125248 bytes equal reference. Injected combined-remap rejection recovers correctly. These are work reductions, not measured Safari FPS or energy. Release-request policy tests also passed.

## Remaining boundary

Changes are on `perf/safari-compositing`, not installed117. No IPA generated. Full app/release validation remains pending before packaging. Physical M4/Duo Safari FPS, heat and actual Metal4 pixels have not been measured. Compare blank vs loaded Safari and Notes window movement under identical RAM/vCPUs/Retina/refresh/LPM/diagnostics. Do not infer a WebKit JavaScript speedup or guaranteed60Hz from native helper checks.

Next source action if device results remain poor: compare existing GPU resource-scan/submission/pipeline/queue and vCPU/JIT diagnostics during those separate workloads. Before a requested IPA, freeze the patch, run the comprehensive native/app release gate, then package a new version; never overwrite117 or use this focused gate as full release proof.

## Requested release118

User requested the latest fixed IPA. Version0.3.17(118), branch perf/safari-compositing. Full native/app validation runs before an explicit one-shot packaging request. Existing shared IPA concurrency/cancellation remains. Packaged-binary checks require Safari mapping/submission markers and focused/native receipts. Upstream contributions are outside this release task.
