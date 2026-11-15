# Build118 capture: M4 follow-up

Evidence: current iPad16,5 app0.3.17(118), source59176da, pid8471. The native log was analysed once; its mirror in henge.log was used for host lifecycle correlation, not counted twice. The109442-line word file contains eight process IDs: only29 dumps from8471 in the current session were admitted (26173 word samples). Earlier launches are excluded. Exact118 symbols were used for native offsets. Full-session diagnostics and50Hz sampling were on, so timings include instrumentation overhead.

## What actually executed

- GPU metadata reuse enabled:1354475 immutable-object hits,183256 page-check hits. Mutable resource metadata still requires14233478 reads; caching every object across records would weaken invalidation correctness.
-435620 empty classic pre-Metal4 submissions avoided. Metal4 completed437485 guest jobs,0 reported guest GPU errors;29680 fallback runs still execute through classic Metal. Pool/compatibility fallback is not CPU rendering. No presentation backpressure was reported. Summed GPU durations overlap and are not utilization.
-836 surface allocations mapped53846 pages with53846 calls; no coalescing hit, no surface over64MiB. Exact backing scan dedup also recorded0 hits. These two features are correct but cannot explain this capture's improvement. Task-buffer mapping lacked equivalent counters; this follow-up adds them.
- Pipeline archives worked:1233 hits /135 fresh builds, roughly90% of these creations were archive hits. Total reported pipeline creation4.28s, worst337ms. Shader first-use spikes remain possible; adding another pipeline cache is unjustified.
- MetalFX performed17020 upscales plus5566 cursor-cache reuses,0 fallbacks. Startup requested2x presentation from a1280x960 guest; this is applied output upscaling, not a native2560x1920 guest or proof of game internal resolution.

## Remaining costs and limits

- The profiler samples registered vCPU threads ONLY. Its weighted busy JIT share70.86% means execution in generated guest code; it does not mean70.86% compiling, and does not measure GPU/UI worker CPU use. Native reported hotspots are IJC resolution/dispatch, then translation helpers. No whole-process CPU bottleneck ranking can be inferred from that sampler alone. The scope is now labelled at startup.
- Running process CPU observations range0.055–4.735 core equivalents (median1.814), with4 guest CPUs. This does not identify P/E residency or prove8 vCPUs would improve responsiveness.
- Fast Memory is on in TLB-first tagged multiwindow mode. Last CPU1–3 hit rates are approximately87% among these fallback probes, not87% of all memory accesses. Keep permission/ASID invalidation and explicit user controls; the capture does not prove the cache is globally optimal.
-1.5GiB JIT ring reached capacity and safely reused59 segments without a full reset;35.6M blocks were evicted. Quiescent eviction cost reached6.55s cumulatively, while lost translations also require rebuilding. Existing measured-safe retention settings remain; increasing JIT reservation amid system compression is unjustified.
- Host presentation rates4.07–59.44/s include idle gaps and cursor work; their median33.365 is not game FPS. Commit-to-present median32.866ms is a real host queue/presentation observation, not complete input latency. Guest120Hz requested does not prove120 physical presentations. No frame-rate cap or quality reduction was introduced.
- All73 thermal readings were Normal, with Low Power Mode OFF. This supports the user's reported session improvement; it is not temperature/watt measurement or a sustained-gaming comparison.

## Memory, I/O and lifecycle

Guest16GiB exceeds reported physical15416MiB. Process headroom stayed over11GiB and there was no pressure event, but raw system free memory reached34MiB and the compressor grew from1373MiB to a6195MiB peak (5412MiB last). These overlapping system categories are not an allocatable-RAM sum or exact guest attribution. A high process allowance is not spare physical RAM. An8–10GiB guest is a useful controlled future comparison; never silently resize a saved16GiB machine.

Root I/O223465 requests: cumulative service29.16s, queue16.82s; averages130us/75us, worst service65ms. These overlapping worker durations are not browser end-to-end latency and do not show a sustained slow SSD. DNS387 answers,0 fallbacks/timeouts. Mouse32046 delivered,0 dropped,0 queued at end; one native-touch stall recovered. Direct USB touch was0 at the final observation, so direct multitouch is not verified by this capture.

The session ended cleanly: final16GiB snapshot5198MiB in23.07s, with22.70s compression and1.95s overlapping write time. Compression, not disk throughput, dominates that save. No app crash appears in these files.

## Implementation decisions

1. Share the checked mapping engine with ordinary GPU buffers. Reuse the already checked page vector on refresh; preserve old GPU-pinned mappings. Real Mach/GPU tests passed including failed refresh retry. Add actual task-buffer counters so fragmented mappings are visible.
2. Implement exact smaller copies and full/reference parity, including GPU-modified host rows. Native tests confirmed byte-identical flat/planar IOSurfaces and GPU pixels. Sparse copying reduced writes but measured CPU changes ranged+0.4% to+77%, and dense results varied−6.7% to+7.5%; retain full copying by default. HV_PVG_COPY_PARTIAL=1 is experimental. No incomplete dirty tracking or sampled pixel skipping is enabled.
3. Reuse bounded owned command snapshot arenas for batches of at least4KiB. Tiny batches retain independent snapshots: later alternating native runs measured a7.27% tiny-buffer regression, while larger buffers improved38.16%. NSData views retain immutable bytes; active views cannot be overwritten; cache<=16MiB/two owners; requests>8MiB remain transient; pressure trims cache ownership. Reference HV_GPU_COMMAND_POOL=0 retained. ASan/UBSan/TSan, failed reads, grown descriptors, asynchronous releases and pressure trimming passed. Five alternating native rounds measured larger-command fixture time−28.89%; this is not Safari FPS or energy.

Build118 remains the user-confirmed baseline. Final integration and physical119 comparisons remain separate gates. None of the native measurements claims the future iPad/Duo speedup or attributes the118 improvement to one isolated change.
