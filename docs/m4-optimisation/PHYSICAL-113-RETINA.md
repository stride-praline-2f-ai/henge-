# Physical113 M4 follow-up

Build0.3.12(113), sourcea59ac18, iPad16,5,4 vCPUs,16GiB guest RAM,60Hz. All three files were scanned; henge.log mirrors native output, so their counters are not added. Machine generations are separated: the short restored generation must not replace the long first session's totals.

The guest started in an1181x756.5-point window with2560x1640 Retina. Instant Resume preserved that geometry. Restoring in a1376x1032-point full-screen window draws881.5 points high, leaving75.25-point bars above/below—70 pixels in the1280x960 screenshot. This is aspect preservation, not a black-texture/GPU failure.

Implemented: Desktop Retina uses the iPad panel shape even at windowed startup; Fit stays window-aware; Duo follows the actual viewport. Existing saved/live state is preserved. Details shows current guest pixels and explains mismatches and cold-start application. New direct Metal4 compiler timing fills the missing cold-shader timing measurement without a draw-time sampler.

Confirmed physical guest Metal4:319065 completed runs, zero guest errors;70239 compatibility runs (55783 unsupported-tag units,14456 pool/admission misses). The82% run share is neither a draw share nor GPU utilisation. Tags161,164 and219 are observed; their individual frequencies are not logged. Tile API mapping is technically feasible and needs semantic/ordering tests; unsupported units continue using the actual classic GPU. Do not discard these operations or enlarge the queue blindly.

Thermal category stayed0 (Normal), including the long later LPM-off period. This is encouraging observational evidence, not a controlled watts/FPS comparison. At16GiB guest RAM, system memory warnings occurred at841.07s and918.96s despite ample process headroom: excluded guest pages still occupy unified memory. Recommend comparing4 vCPUs/8GiB after a real shutdown; do not resize live/saved RAM automatically.

CPU:46822 vCPU sampler observations;76.2% of busy samples in generated code.30626 JIT word samples,27 dumps, zero lost. Three ordinary TLB loads account for22.09%. MOV x6,SP fell from5.20% to0.137%; the selected LR spill fell from3.77% to0.320%. Expected folded-address/slot-load words appear. Different workloads prevent treating those sample-share changes as whole-app speedup percentages. Kernel fastmem's eligible hit rate is90.40%; it does not replace EL0 TLB checks.

The long generation generated31.48M translations with68.43% approximate retranslations;46 partial evictions, zero full resets. Evictions took4.486s total. CPU/dispatch/MMU reuse remains relevant; blocks/s is not an FPS counter.

Classic pipeline cache started with zero indexed persisted PSOs:591 hits,955 compiles,29.03s total compiling,worst1.412s. Metal4 compiled809 pipelines,74 archive hits,44 archive writes; direct compile latency was missing and is now instrumented. The cause of the initially empty cache is not established. Retaining a warmed installation matters; do not clear caches as a performance fix.

Host presentation intervals average30.70/s across all recorded image epochs, including idle/cursor activity. The long epochs have p95 around50ms,p99 around133–150ms. This is not game FPS or proof of uniform60Hz. Long unchanged-image gaps can be legitimate; the31s maximum alone does not prove a frozen guest. Presentation backpressure remained zero. Classic queue-start latency averages2.74ms,worst305.61ms; peak65 overlapping in-flight buffers. Overlapping durations are not GPU utilisation.

Persistent save:16GiB,5935MB output,28.49s total;28.47s compression alongside1.60s writing. Only seven high-entropy chunks (28.7MB) skipped full compression, so the new fast admission path cannot materially shorten this particular mostly compressible save. Restore completed in3.73s. Do not compare its total save time directly with the earlier12GiB capture.

Root disk209255 requests:224us average service,177us average queue,1.18s total flush time; no general flush bottleneck demonstrated. No reported GPU command error, native exception, audio failure or crash; stop was by host. Native USB touch was disabled with no companion polls, so this run cannot validate Pencil/touch recovery. Henge Link was disconnected.

Cloud geometry, SDK and app checks remain required before the next IPA. Physical full-screen layout, active-interaction60Hz and Duo/Pencil remain device validation.
