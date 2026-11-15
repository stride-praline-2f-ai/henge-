# M4 capture: release 116, 16 GiB guest (2026-11-15)

Complete input: `DF1F6DA8-978C-4CFB-B05E-55ACE377610B`, all three files.
The ordinary logs overlap; they are not independent sessions. The instruction
file is append-only: aggregate only PID 5314's 21 disjoint sample windows.
Original input identities:

- `1-henge-native.log`: 1026498 bytes, 8768 lines, SHA256 `bf319a7cde583b697e3dfc9bcf0bd6cb829e552b7f45e4078a89e8c7a5865936`.
- `2-henge.log`: 1185283 bytes, 9404 lines, SHA256 `48a9c0309e0e26a15d5ef29ce70b62abae2cb760a0f42a8f16a553ff9c557831`.
- `3-hvprof-words.txt`: 1345219 bytes, 89064 lines, SHA256 `d8c11dbc5f7bc215f80a996d4412252b6731e65e8c9a2e0cdfbe3e292101ea1f`.

## What actually ran

- iPad16,5 / M4, runtime 4P+6E, physical 15416 MiB; 4 guest CPUs.
- IPA 0.3.15 (116), wrapper `0deed08b16fffc73cdcdc3477793d3b28d87e96e`;
  includes `55d472b7`. JIT self-test passed. This is the delivered IPA.
- Guest allocation 16384 MiB, JIT 1536 MiB. Ledger-backed RAM state=1.
  Exclusion from process footprint changes accounting, not physical capacity.
- All 62 rate captures: Low Power Mode off, thermal category 0 (Normal).
  No wattage/temperature measurement or Low Power Mode A/B is present.
- Kernel read cache on, TLB-first tagged multiwindow; checked groups=2;
  superblocks off; addend preload off. Detailed counters and 50 Hz sampling on.
- Desktop MetalFX is **1280×960, non-Retina guest → 2560×1920 output (2×)**.
  It is not an 80% source dimension in this configuration. Native Retina is
  a different setting. Same output size does not establish native text fidelity.

## Memory: actual physical pressure despite process allowance

- Guest 16 GiB exceeds reported whole-device physical capacity (~15.05 GiB),
  before iPadOS, JIT and graphics. This is an explicit saved user setting;
  silently shrinking it or a running snapshot would be incorrect.
- System compressor peaks at **6.39 GiB**, ending at 5.33 GiB; free memory
  ranges about 22–612 MiB. These are system-wide categories, not exclusively
  attributable to Henge; categories must not be summed as independent memory.
- Henge footprint reaches 4.71 GiB; resident peaks 9.46 GiB. Dynamic process
  headroom remains 11.29–12.97 GiB because some guest pages are excluded.
  That value is neither free physical RAM nor a guarantee against pressure.
- UIKit warnings occur at app elapsed 189.373 and 531.562 seconds. Existing
  unified cache policy responds and later restores admission. Two GPU cache
  memory-warning events are recorded. Live guest allocations are retained.
- Metal allocations in rate captures are **166.5–571.5 MiB**, far below the
  CyPort screenshot's 6–7 GiB symptom. Resource accounting may overlap guest
  RAM/zero-copy mappings. A 5 GiB GPU cap would not constrain these observations.

Action: retain safe 8 GiB M4 automatic default, and compare this machine at
8 GiB after a full shutdown. Do not increase RAM/JIT as an assumed cure or
weaken iOS memory reporting. No live RAM resizing or snapshot incompatibility.

## CPU, MMU and code cache

- 46,220 registered-vCPU samples; ~74.95% of sampled **busy vCPU** time is JIT.
  This profiler does not sample arbitrary GPU/compiler/network threads and
  cannot attribute the whole process's CPU time by these percentages.
- 20,375 counted JIT instruction samples, no lost word samples. Three loads
  (`f942c0ef`, `f942c4ef`, `f942ccef`) contribute **24.70%** of JIT word samples:
  software-TLB read tag, write tag and host addend. These are sampled locations,
  not independently measured instruction costs or permission checks to remove.
- Final kernel-cache hit rates: CPU0 96.73%, CPU1 96.65%, CPU2 96.16%, CPU3
  96.02%. They count the TLB-miss kernel-cache probes, not all guest accesses
  or EL0/Roblox loads. The old 0–30% window coverage problem is absent here.
- Process CPU intervals range 0.227–4.494 core equivalents (median 2.014).
  This includes helper/graphics work; four vCPUs do not imply core pinning or
  four physical cores occupied continuously. No 6/8-vCPU comparison exists.
- 30,738,313 translations, ~20,564,312 approximate retranslations. Cache reaches
  capacity; **45 segment evictions, zero whole-cache resets**, repairing
  6,441,134 exits. Full=100% does not mean the cache stopped working. The
  retranslation estimator includes legitimate changed mappings/code identities.
- Exit-request polling (`ldr w15,[x28,#0x3c0]`) is another 3.47% of JIT samples.
  Removing checks could break stop/pause/TLBI latency; preserve correctness.

Action: preserve checked reuse, invalidation, cache and flush defaults. Do not
force all CPU work onto Metal, enable all experimental knobs or claim maximum
Fastmem efficiency from hit rate alone. Existing preload/native/reference
comparisons remain available; turning counters off is required for timing A/B.

## GPU and presentation

- Last replay report: 69,806 Metal4 submissions, 69,804 completed, zero guest
  GPU errors. The two in flight at that report are not lost-command evidence.
- 409 optional pipeline warmups admitted/completed; 771 deferrals, 0 cancellations;
  1,648 compatible classic submissions while warming. They execute real Metal,
  not CPU rendering. 351 Metal4 compiles total 11.085 s host elapsed, worst
  1.062 s on the Utility worker; these overlapping times are not frame stalls.
- Classic pipeline archives: 733 hits, 18 compiles, one bypass; cache hits can
  still incur driver creation cost (worst classic creation ~320.67 ms).
- 5,128 fallback runs: 1,750 unsupported-stream; 1,730 pool/unavailable; 1,648
  warming. Rejection hotspots: tile-size query 164 and tile textures 161,
  875 each. They remain correct classic GPU work. Do not pretend tile queries
  are no-ops or silently drop tile bindings to force Metal4 statistics.
- MetalFX: **5,758 encodes, 936 cursor cache reuses, 0 fallbacks**, including
  zero pressure/resource/geometry fallbacks. GPU replay and upscaling are active.
- Host submission cadence peaks at 52.82/s, but includes cursor redraws and
  static periods; it is not measured game FPS or proof of stable 60/120 Hz.
- A ~200.5 s no-presentation interval contaminates the lifetime histogram;
  its ~10.2 FPS average and zero estimated 1% low cannot describe interactive
  frame rate. Do not assume it is a 200 s GPU stall; windows show no GPU work
  during most of that interval. 535 invalid/non-presented timestamps also need
  separate accounting before drawing pacing conclusions.
- Classic queue latency mean ~0.910 ms, max 57.51 ms, peak 58 command-buffer
  lifetimes. Buffers are not frames; separate queues/timestamps overlap.

Action: retain fallback and bounded compilation. Add opt-in `frame-submit-latency` mean/p95/p99/max on the same Core Animation
media clock, with separate not-presented/invalid counts; its queued-drawable
latency excludes idle gaps. Keep the existing raw cadence histogram unchanged. No forced
60 Hz cap, reduced Retina resolution or inferred GPU utilization.

## Storage, network, input and lifecycle

- Root disk: 1,218,921 measured requests; accumulated service 240.94 s,
  queue 291.22 s (means ~197.7 / 238.9 µs). Service max 293.064 ms; 48 flushes
  total 0.777 s. Concurrent worker durations overlap and include host waits /
  memory faults; they are not exclusive CPU usage or pure SSD throughput.
- Existing descriptor coalescing combines contiguous buffers only. Implement
  bounded `preadv`/`pwritev` for fragmented request buffers: fewer system calls,
  direct guest DMA, no staging or merging across requests/flushes/barriers.
  Opt-in `block-io-shape` counters verify actual scatter-path use on devices;
  they do not mistake vector count for syscall count after short/chunked I/O.
- Also repair sector-byte multiplication overflow and invalidate translated
  code after partial failed DMA; add production-path regressions.
- DNS reaches 418 host answers, zero fallback/timeouts; network counters move.
  The logs do not identify DNS failure as the browser loading bottleneck.
- USB touch finishes status 2, direct USB, 1,794 reports, 0 failed, queue 0;
  two liveness stalls both recover, 47 rejected frames and 40 cancellations.
  Rejections/cancellations alone do not establish failed clicks. Preserve
  neutral-contact/ownership handling; no evidence to remove its safeguards.
- Session ends with host halt reason 3, CPUs joined, disks flushed, VM freed.
  No new crash, panic or jetsam termination is shown. Snapshot restore, games,
  Apple Pencil interaction and real-device energy still need targeted evidence.

## Validation limits

This is an observational capture, not a controlled old/new performance test.
Cooling is promising (all samples Normal), but does not prove a new improvement,
Low Power Mode equivalence, or a particular maximum vCPU/RAM configuration.
New I/O changes need focused sanitizers, native macOS/iOS SDK compilation and
paired warm-file measurements. Hardware app/game latency remains unmeasured.
