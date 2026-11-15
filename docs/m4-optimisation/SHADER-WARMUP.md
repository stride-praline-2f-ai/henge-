# Bounded optional Metal4 pipeline warmup

The physical116 Duo run records Metal4 compiler calls up to 781.84 ms (9.743 s total); the iPad previous-run tail records up to 638.24 ms (12.838 s total). Both are host elapsed compiler times, not GPU execution or frame times. Required classic PSOs already exist before creating these optional variants.

Implementation: one utility compiler worker, at most two retained requests, coalesced per original pipeline. The guest render worker retains the complete classic replay until the Metal4 variant is ready. Compute threadgroup ABI checks remain mandatory. Ready/rejected metadata is immutable and atomically published; deferred or pressure-cancelled entries can be readmitted. Compiler failures preserve classic rendering. Pause and destruction stop queued optional work; admission recovery does not override pause.

The existing compiler/archive lock remains authoritative. Render-worker budget refresh uses tryLock and never waits behind a cold compiler. The compiler completion or archive queue consumes the latest pressure request. Exceptions release that mutex. Immutable bundled display archive hits bypass the guest compiler lock, preserving first-frame preparation during optional compilation. Required uncached display PSOs still need real compilation.

Diagnostics distinguish pipeline_warming from unsupported_stream, encoder_pipeline, pool_or_disabled and bridge_allocation. The warmup line reports admitted/completed/deferred/cancelled jobs and classic replay while warming. No new polling timer, extra guest CPU, resolution cap, unsafe command skip or independent pressure controller is introduced.

Validation pending for this checkpoint: production state machine with a deliberately blocked recording compiler; 1000 nonblocking requests; concurrent first-use coalescing; queue bound; pressure and pause interactions; object lifetime; compiler error/exception; compute ABI mismatch; ASan/UBSan and TSan; complete native and app checks. Real Metal4 GPU readback tests wait on the same compiler completion event. A paravirtual runner cannot establish physical A20/M4 performance or Metal4 pixels.

Research supporting the implementation:
- [Apple: Metal4 compilation scheduling](https://developer.apple.com/documentation/metal/using-the-metal-4-compilation-api): dedicated dispatch QoS, background work and explicit lifecycle synchronization.
- [Apple: asynchronous specialization](https://developer.apple.com/videos/play/wwdc2023/10127/): keep an existing correct pipeline while a more specialised pipeline compiles.
- [Apple: process memory allowance](https://developer.apple.com/documentation/os/os_proc_available_memory): dynamic advisory process headroom differs from physical RAM and should not be maximised blindly.
- [Apple: memory warnings](https://developer.apple.com/documentation/xcode/responding-to-low-memory-warnings): OS termination can occur before a warning arrives. Zero warning counters do not identify or exclude a memory-related termination.

This targets avoidable render submission stalls. It does not eliminate guest ARM64 software-MMU/JIT execution, the first required classic shader compilation, physical memory limits or iOS Low Power Mode policy. Device FPS, load-time and energy improvements remain unmeasured.
