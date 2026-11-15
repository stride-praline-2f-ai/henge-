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
