# Memory pressure, physical accounting and MetalFX continuity

This extends the fully validated79fc181 source after the user's request to counter unnecessary MetalFX deactivation during warnings. It does not assume process allowance equals free physical RAM, suppress OS warnings, shrink live guest RAM or replace the memory controller.

- Normal: the existing MetalFX pool retains at most three resource sets.
- Moderate warning, with at least512MiB process headroom: cap the pool at two sets. Drop spare idle allocations and retire surplus sets after GPU completion. Preserve the current upscaled image, cursor reuse and new-image upscaling when a lease is available.
- Critical system pressure or less than512MiB process allowance: release optional idle/cached FX resources and use the existing linear compositor. Output geometry and guest workspace stay fixed; live GPU jobs keep their resources until completion.
- Recovery: restore the normal budget on the existing pressure/cache events and permit one retry of failed initial compiler creation. No timer, per-frame compiler retry, second cache manager or new render path.

The pool counts distinct leased frames, not command buffers. A cached image may be retained by several reads. Reducing the cap cannot overwrite an in-flight texture; surplus leases are discarded only when their last owner releases them. Tests exercise3->2->3, live retirement, two-set new-image encoding/cursor reuse, critical fallback, allocation failure and compiler recovery.

Existing capture now reads raw public HOST_VM_INFO64 categories on its utility worker: free, speculative, purgeable, compressor, wired, active, inactive, external and internal bytes. Some categories overlap; they are not added into an invented physical-available number. Process headroom, physical RAM, footprint, resident bytes and Metal allocation remain separately labelled. If the OS restricts the system read, system_vm_available=false is explicit. Mach send rights are balanced and tested against real macOS accounting.

System/process memory is still recorded while a VM lifecycle writer prevents VM statistics access. Generation-fenced VM rates remain discarded during mixed transitions. Memory rows carry the worker's sample uptime to distinguish sample time from UI/log-delivery delay. The existing warning notification advances the same capture deadline and wakeup; no high-frequency memory poll is added.

The prior115 logs establish real1280x960 ->2560x1920 Metal4FX execution and pressure-associated linear fallbacks. They do not measure actual free physical memory or prove an iPadOS reset cause. The new counters address that missing distinction on the next device capture. A16GiB guest still competes with iPadOS/JIT/Metal for physical memory even when it is excluded from the process footprint.8GiB remains a comparison option after full shutdown, not a silent change to saved sessions.

Validation required for this extension: real system-memory/read-right test, restricted/mixed-lifecycle capture fixture, resource budget boundaries, production FX pool/routing ASan/UBSan checks, both app SDKs and complete native/app compilation. Packaging remains disabled until completed validation and final release reconciliation.
