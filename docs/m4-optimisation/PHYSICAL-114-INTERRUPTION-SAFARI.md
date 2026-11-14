# Henge 0.3.13 (114): interrupted Roblox launch and Safari smoothness

## Scope and limits

All five supplied files were scanned in full; aggregate captures were separated by launch PID, VM generation, timing epoch and pause/restore boundaries. Native files are completely mirrored in the corresponding app files (zero missing native lines); their counters are not added twice. The exact 114 symbol file was used for native PC attribution. These logs precede MetalFX build115 and do not test that upscaler.

Device: iPad16,5 M4, four performance/six efficiency cores, 15,416MiB reported physical RAM. Both runs use four guest vCPUs, **16,384MiB guest RAM**, a1,536MiB JIT cache and native Desktop Retina2560x1920. Low Power Mode is off in the captured samples.

## Interruption: what is and is not established

The previous app launch (PID11196) contains two VM generations. Generation1 starts cold, completes several pause/continue cycles and completes Save & Leave at app uptime3084.882s. Generation2 restores that snapshot at3145.141s and is running at3148.145s. Its30-second diagnostic capture ends3192.862s. It pauses at3224.018s, continues3235.900s and has a last stamped UI event3337.059s, followed by native output and an abrupt end. **At least144seconds at the end are outside detailed capture.**

There is no recorded native crash-handler signal, guest panic, GPU command error or normal shutdown at the final end. The user's description of a soft iPad shutdown is compatible with a system interruption, but these app logs cannot identify jetsam, a graphics-driver/system fault or an iPadOS restart. A low next-launch PID is not a crash diagnosis. No reset cause is asserted.

The later launch (PID560) cold-boots macOS at220.857s, and completes Save & Leave at671.609s. It does not crash in the supplied log. Therefore this is **restored vs cold boot**, not simply first vs second shader load. The restored previous guest runs at60Hz; the later cold boot uses120Hz. Different durations, state and workload prevent a controlled performance or stability comparison.

## Memory pressure is a concrete risk

Previous launch:10 system memory-pressure warnings, including one during generation2 at3152.228s. Current launch:4 warnings, two while running and two during snapshot saving. A16GiB guest exceeds the device's reported physical RAM before iPadOS, JIT and GPU allocations. Guest pages excluded from process footprint still occupy shared physical memory. The approximately17GiB process allowance is not additional physical memory.

This is evidence of pressure, not proof that pressure caused the final interruption. Keep saved state intact; test a fully shut-down guest at **8GiB RAM,4vCPUs,60Hz, native Retina unchanged** to create a lower-pressure comparison. RAM/guest refresh changes do not rewrite an existing snapshot's hardware configuration.120Hz remains available.

Current snapshot:16GiB address space,22.40s elapsed,22.13s compression,2.04s writing overlapped,20.35s waiting for compression, about5,614MB output. Eight compression workers were admitted from process headroom. This save is predominantly compression work, not evidence of slow SSD throughput. No unsafe live RAM shrink or forced guest memory reclaim is introduced.

## GPU is being used

Current guest Metal4 counters:293,691 submitted,293,676 completed, zero reported guest errors.51,738 fallback decisions include26,941 unsupported records and24,797 pool/admission fallbacks. These fallbacks preserve the classic Metal path; they do not imply software rasterization or unused GPU. Increasing the submission pool without bounds would risk more queued frames and resource retention.

The old capture's replay_gpu_ms field measured **classic Metal command buffers only**. Current cumulative classic time is13,838.34ms, while Metal4 reports1,136,817.50ms for guest replay plus presentation. Commands overlap; neither sum divided by wall time is GPU utilization. A misleadingly small classic capture value must not be read as evidence that Roblox is CPU-rendered.

Metal4 compiler calls:189 attempts,6,398ms total,822ms worst. Classic pipeline archives:687hits/45compiles,2,693ms compilation total. These are host compiler-call elapsed times, not GPU rendering duration or every asset's loading time. Warm caches can help later, but this pair does not prove why the second game launch succeeded.

Current queue commit-to-start samples average approximately5.29ms, maximum53.66ms. These are overlapping command lifetimes, not whole-display frame latency or utilization.

## CPU/JIT and interaction

Current capture median process CPU is4.20 core equivalents (includes every process thread, not4.20 guest vCPUs).77.18% of sampled busy vCPU PCs are generated JIT code. The current PID's21,742 JIT-word samples contain three software-TLB loads at23.36% combined (12.73%,5.74%,4.89%). That fraction is sampled JIT PCs, not whole-app time. Existing grouped accesses, permissions, invalidation and kernel-cache fallbacks remain essential; blindly enabling addend preload or bypassing checks is not justified.

Current:17.40million translations,8.98million approximate retranslations,22 segment evictions,zero full resets. Cumulative eviction time is2,925ms:1,012ms block maintenance,1,696ms exit repair,218ms instruction-cache work. About133ms per eviction on average is a credible hitch source. Previous generation1 has101evictions and12,511ms cumulative eviction time. The retained ring avoids complete flush storms but its global descriptor/exit maintenance is still costly. This follow-up does not claim those costs have been eliminated.

During current input-active intervals the host presents about45.62/s,53.64/s,29.15/s and18.74/s in selected10-second captures; the last is after serious thermal state. These are host updates including cursor, not game FPS. They confirm uneven interaction but cannot identify Safari's exact share: no foreground-app, URL or WebKit request/layout timing is logged. Whole-run frame histograms include idle/pause gaps and overflow buckets; zero histogram bounds are not0FPS.

Root disk:152,157measured requests, mean205us service and116us queue time;113flushes total766ms, maximum service54.7ms. Host DNS answered189requests, zero fallback/timeouts. Neither result measures remote HTTP transfer, JavaScript execution or guest asset decompression. There is no evidence here to disable flush safety, DNS handling or force an unbounded disk cache.

The current word file also retains an older PID9561; it is excluded. One previous-PID dump has180header samples but617word records and is excluded from exact previous-run ratios. The current PID's16windows agree exactly with their headers.

## Implemented source fixes

1. Native diagnostic reports share one coalescing utility worker. The previous maintenance path called native logging on the main actor while capture separately requested the same report. Native device locks, thread accounting and formatting must not block touch/display-link callbacks or run duplicate reports.
2. Native observation/resource sampling runs on one bounded utility queue. Main-actor admission allows one outstanding read; stop/restart revisions reject stale results. A delayed background result cannot re-enable timing or mix VM generations. No new statistics timer is introduced.
3. GPU snapshots expose existing Metal4 completion/duration counters separately from classic counters and include Metal allocated bytes plus physical RAM. No new GPU completion callbacks or per-frame instrumentation are added. Durations are explicitly scoped and never labelled utilization.
4. The native-touch watchdog checks sender age only with held, queued or encoded contacts. Idle UI heartbeat intentionally stops; treating it as a frozen UI generated127 false-stall messages in the previous log. Held-contact and helper-death cancellation remain bounded and tested.
5. Settings and session startup distinguish physical RAM from process allowance and warn when guest RAM meets/exceeds physical RAM. Saved configurations and user RAM preferences are not silently overwritten.

These address observed avoidable work and diagnostic correctness. They do not establish a fixed iPadOS interruption, steady60FPS, faster WebKit page loads or lower watts. Release packaging remains blocked until source validation completes; no new IPA is requested for this development checkpoint.

## Validation checkpoint

Local ASan/UBSan native-touch watchdog passes, including long idle with immediate next contact and retained held-contact timeout. Local Swift/native lifecycle execution is unavailable in this Linux workspace (no swiftc or macOS lifecycle binary); those checks are delegated to the existing macOS workflow. Cloud tests are required for production Swift asynchronous capture/coalescing, full native Metal lifecycle and device/Simulator SDK/app compilation. Their results are recorded in the repository continuation state after execution.
