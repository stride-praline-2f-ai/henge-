# Physical MetalFX115 follow-up

All three newly supplied files were read in full. Build **0.3.14 (115)**, source8f8e8020cdd411ff422e759d2c65faa5d1ab3cd0, PID1400. The native file is fully mirrored in henge.log; zero native lines are missing, and counters are not added twice. Exact115 symbols were used. The word file includes prior PIDs9561/11196/560; only PID1400 belongs to this run.

## Actual configuration and lifecycle

M4 iPad16,5,15,416MiB physical RAM, **4 guest vCPUs,16,384MiB guest RAM,1,536MiB JIT**, guest120Hz. Low Power Mode is off in all capture samples. This is a cold boot (`saved_configuration=false`) at50.016s, not a snapshot restore. The guest boots1280x960 non-Retina for the optional same-logical-workspace MetalFX mode; the final host canvas is2560x1920. It completes host-requested pause/save/shutdown at761.015s. No recorded crash, guest panic or native GPU error in this run.

## MetalFX is executing on the physical M4

The log explicitly reports Metal4 spatial/perceptual upscaling active with1280x960 input and2560x1920 output. Last effect counters: **13,079 encodes,5,357 cached cursor/image reuses,3,433 linear fallbacks**. The reuse path avoids rerunning MetalFX for an unchanged desktop image and composites the cursor afterward. These counters establish the real device execution path, not pixel-quality equivalence, stable60FPS or measured speedup.

There are **three system memory warnings** at196.020s,363.176s and407.309s. During pressure the effect encode/reuse counters stop increasing while fallback counts grow. The existing safe policy temporarily releases optional MetalFX resources and uses the linear compositor, preserving the output size and guest workspace. Admission recovers later. A pressure warning still matters even while process headroom exceeds10GiB: excluded guest pages consume shared physical RAM. Do not interpret this fallback as unsupported M4 hardware or fix it by disabling pressure protection.

1280x960 has one quarter as many backing pixels as2560x1920, with reconstructed output detail. It does not reduce Safari JavaScript/layout work or guest CPU translation by75%, and must not be described as a4x emulator speedup. The current data does not isolate Safari from other guest apps or distinguish every GPU effect's execution time.

## Remaining costs, with scope preserved

- Median running capture process CPU: **4.219 core equivalents**, mean4.043; all process threads included.75.63% of sampled busy vCPU PCs are generated JIT code. PID1400 has23 consistent word windows/39,763samples with zero lost samples. The same three software-TLB loads occupy21.68% of JIT-word PCs, not21.68% of whole-app time.
- **32.47million translations**,22.30million approximate retranslations (68.7%).47 ring evictions,zero full resets; the latest stage report covers46 evictions and **4,140ms total** (1,856block maintenance,2,015exit repairs,269instruction publication). Roughly90ms per reported eviction can cause visible hitches. There is no justification to remove invalidation/publication barriers or exceed JIT memory budgets.
- Metal4 guest replay:506,012submitted,506,011completed,zero reported guest errors.109,466fallback decisions:75,275unsupported streams,34,191pool/admission,zero encoder/pipeline and allocation rejection. The fallback still uses native classic Metal; it is not proof of CPU rasterization.
- Metal4 synchronous compiler calls:862attempts, **19.856s total,903.62ms maximum**. Classic archive counts:1,317hits/61compiles,3.650s hit handling and1.615s compilation. CPU elapsed compiler calls and overlapping GPU execution are distinct. Existing exact persistent archives remain; arbitrary guest shaders cannot be compiled before the guest supplies them.
- Classic queue commit-to-start: approximately3.25ms mean,402.11ms maximum across1,173,963samples. The maximum can hitch; the aggregate is not a per-frame bottleneck attribution or utilization metric.
- Final presentation histogram:22,049host updates over664.592s,average33.175/s,p95 upper66.75ms,p99133.5ms,maximum4,366.53ms. It includes cursor, idle and initialisation intervals.19 input-active capture windows have median36.17host updates/s. Selected scrolling windows show46.84,36.17,26.68,21.14 and24.29/s. These demonstrate uneven interaction, not Roblox FPS or a controlled comparison against114.
- Serious thermal category appears at453.277s, about403s after guest startup. It is a category, not a temperature. Full diagnostics, including generated fastmem counters and50Hz PC sampling, are enabled and impose overhead; normal use should disable continuous diagnostics after testing.
- Kernel-cache fallback probe hits are90.52-90.93% per CPU. This describes eligible fallback probes, not all guest memory operations or an overallMMU hit rate.
- Root I/O:189,995requests,195us mean service,102.64us mean queue,132flushes/888ms total,72.77ms maximum service. DNS260answered,zero fallback/timeouts. RemoteHTTP,WebKitJS and asset decompression are not measured. Disabling storage durability is not justified.
- Native touch:524accepted/zero rejected,37sender-stall messages and6helper-stall/recovery pairs. Idle false sender expiry is corrected by this follow-up; real helper stalls remain separately observable and safely bounded. The logs do not prove all touch transitions or Pencil input (zero Pencil begins here).
- Save completes with992,130data pages/about5,936MB output in31.45s. Compression31.43s overlaps1.56s writing,29.88s waiting for compression. The UI stays in saving state; this is not another crash. No claim that saving16GiB fits a guaranteed iOS background interval.

## Integrated response

The114 follow-up's bounded off-main diagnostic workers, lifecycle fencing, complete Metal4 scope/allocation reporting, physical-memory distinction and idle-touch watchdog fix all apply here too. The production Swift worker tests now pass under cloud ASan after correcting a test's polling-admission race; production behavior was not weakened to pass it.

The new MetalFX-specific fix makes disabled admission idempotent. Previously each fallback frame retrimmed the pool and advanced its generation, even though no resources had been re-admitted. Now trimming happens once per transition. The cache worker sends presenter admission changes only on transitions. New low-overhead counters split pressure, capability/resource and incompatible-geometry fallbacks; pressure transitions log once with the existing memory source. No new timer, callback, render path, topology change or mandatory quality reduction.

Recording-object tests exercise pressure fallback,100 repeated disabled calls without another trim, in-flight lease retention, recovery, geometry fallback and resource-allocation failure. Real GPU visual quality/performance remains physical-device validation; the supplied logs verify that the115 Metal4FX path actually activates on this M4.

For a controlled next comparison use a fully shut-down **8GiB guest,4vCPUs,60Hz**, keeping the chosen native Retina or optional MetalFX mode explicit and constant. Existing16GiB saved state remains compatible and is not resized silently. This is a lower-pressure comparison, not a claim that more RAM or120Hz can never help.

Cloud validation for the final combined patch must pass before any IPA. This follow-up does not claim the prior iPadOS interruption's cause or steady60FPS has been established.

A failed initial MetalFX compiler/pool creation previously latched the unavailable flag permanently. Recovery now permits one new attempt when pressure admission returns, without per-frame compiler retries. The regression injects initial compiler failure, checks that repeated frames do not recreate it, and verifies successful recovery.

## Hardware scroll detail

Hardware scroll speed is0.02, the configured minimum (default0.15). The end counters show247hardware callbacks and46delivered batches, maximum2axis units. The production accumulator deliberately retains fractions until integer guest wheel units are available. Tiny deltas therefore arrive as accumulated steps; this can contribute to scrolling feel, but does not explain page-loading delay or all frame-time spikes. The scroll preference is preserved. Reset hardware scroll speed is an existing control for a separate comparison. Captured native mouse drop/queue counters are zero; Pencil has no begins in this test, so Pencil hardware behavior is not validated by this log.
