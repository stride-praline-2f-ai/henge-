# Safari replay follow-up

User report on117: Safari page loading, scrolling/typing and moving its own window are slow; Notes, Settings and Roblox are comparatively usable. This narrows the investigation but is not foreground-app profiling or proof of a specific bottleneck.

Implemented against frozen117 runtime ebeaad5, preserving CPU/JIT work:
- Admit the existing command/task-scoped immutable object and page-mapping reuse by default; mutable resource entries still checked. HV_GPU_BATCH_CACHE=0 selects the reference path.
- One full guest-byte hash per exact planar backing per command, sharing only validated all-pages/layout aliases. Independent allocations and new commands recheck all bytes. Command numbers advance even after rejection and saturate safely to uncached mode at wrap.
- Omit the redundant empty classic command buffer immediately before a successful Metal4 handoff. Real staging/legacy work, the runtime's bidirectional signal/wait bridge and final guest completion remain. HV_PVG_SYNC retains diagnostic synchronization.

Local ASan/UBSan production helper tests passed:10000 page uses ->1 full320-page metadata comparison; alias dedup, distinct allocations, changed last page, failed remap retry, task/command boundaries, wrap and explicit reference. This is fixture work reduction, not measured Safari FPS or heat.

Next: inspect the focused source job, fix all independent failures, then record native GPU pixels/ordering and macOS/iOS production compile results. No IPA is requested or generated. Physical Safari performance still needs the same RAM/vCPUs/Retina/refresh/LPM configuration, blank page vs loaded page, and comparable Notes-window movement. Do not overwrite117 or claim this fixes WebKit JavaScript performance.


## Large-surface mapping

Found actual missing support when comparing Oliver Ames upstream PR187: surfaces over64MiB use a second table level. The old path read the root as a flat leaf array. Adapted only this checked mapping fix; retain the custom immutable planar backend and all-leaf-page identity. Invalid/non-RAM leaves and failed vm_remap now reject the incomplete allocation. Tests cover boundaries, flags/holes, changed final leaf and actual production newSurface through real Mach aliases/Metal buffer reads. No evidence yet that the user current Safari workload allocated such a surface. Native logs now identify flat vs two-level mapping. This is a concrete correctness fix, not a proven Safari root cause.

## Verified checkpoint

Focused native/SDK run [43735267109](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43735267109) passed on exact wrapper `3a18919c8dd79b07221d51a5be154ce0ca4b1d1c`, runtime `1ff0e31a058ac20f80d8e4843c39db1f9f60dea6`, cumulative patch `cf3a7f5e66d71ab1aecc05383bd5694d3870c3ec9820157f5e649e767d472291`. The real production surface mapping passed CPU/GPU first+last byte checks on a >64MiB allocation, flat compatibility, changed leaf, old mapping retention, malformed-tag holes and outside-RAM rejection. Metadata, alias, epoch-wrap, all display pixels, queue/fence/lifetime, warmup and resource ownership checks passed. Production renderer compiled for macOS and iOS. Core CPU/JIT files are unchanged from117.

Next action: if an updated IPA is requested, run the full final native/app release gate on this frozen patch before packaging build118; do not call the focused renderer compile a full app/release gate. Physical comparison: Safari blank page and moving its window, loaded page/scrolling, and equivalent Notes movement with identical guest RAM/vCPUs/resolution/refresh/LPM/diagnostics. Existing diagnostic counters now expose actual resource-reuse and skipped-empty-submission counts; initial surface logs identify two-level allocations. No visible Safari FPS or energy gain is claimed yet. No user-facing setting or resolution reduction was added.

## Contiguous remap follow-up

Runtime1757ecb coalesces physically adjacent leaf pages only when a single checked guest RAM region backs the full host span. Crossing RAM regions uses a checked valid prefix; Mach rejection switches this allocation to individual-page mappings. HV_PVG_REMAP_SINGLE=1 keeps the reference path for comparisons. Source logs include page count and actual remap calls. No pixels, resolution, refresh or frame cap change.

Local surface-table/helper ASan/UBSan checks passed. Current cloud gate must check the actual production mapper:4097 contiguous pages in one real Mach remap vs4097 reference calls, full-byte equality, real GPU reads and injected large-remap rejection with individual-page recovery. Prior green receipt above predates this change; do not present it as validation of the new patch. Next: run focused source workflow, fix any failures and update VALIDATION.json before release consideration.

Contiguous remap checkpoint passed43736408228 on763cf5ce:4097 ->1 actual Mach calls, all67125248 bytes match the single-page reference, real GPU edge reads pass, and a rejected combined remap recovers using4097 single-page remaps. Production iOS/macOS compile and all other focused checks passed. Runtime458eb0f adds these checks to the existing release sanitizer gate; it makes no further production changes. Next: confirm the frozen exported patch in the focused source workflow, record its exact receipt, then leave full app/release validation pending for a requested IPA.
