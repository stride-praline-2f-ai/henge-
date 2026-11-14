# Physical 112 follow-up

The physical M4 run of0.3.11 used4 vCPUs,12GiB RAM and2560x1920 Retina. All453297 guest submissions fell back before Metal4 encoding; display completion was incorrectly easy to confuse with guest execution. Busy vCPU samples were about77% generated code; three ordinary software-TLB loads accounted for19.78% of JIT PC samples. Kernel fastmem hit91.31%; it did not replace user memory checks. The1.5GiB ring had49 partial evictions, zero full resets. Persistent saving took21.41s, dominated by compression. Native touch never received a helper handshake.

Implemented changes:

- Fold immediate SP address calculation into one host ADD/SUB; keep permission, PAN, page and writeback checks.
- End interrupted register-group candidates instead of losing valid field pairs on both sides; each new span retains its checked-range guard and plain fallback.
- Inline far-chain slot reads, preserving exit requests, cross-page mapping checks, guest LR and flags. The former thunk encoding remains a private native differential fixture; no user setting is added.
- Reuse recent immutable block literals, excluding mutable helper-info pairs. Bound pool/fixup writes and retain existing code publication and invalidation barriers.
- Use one bounded GPU stream parser for both backends, including protected/inclusive envelopes and zero allocation padding. Attribute exact rejecting type/tag/offset without storing shader or resource contents.
- Map final store options onto actual Metal4 attachment descriptors and verify replayed setters; support capability queries, GPU-address indirect draws and native mipmap generation.
- Partition only at closed encoder boundaries, preserve continuations and coalesce adjacent supported units into one job. An opaque encoder keeps compatibility without diverting unrelated supported encoders. Two-way GPU ordering, original bytes, resource residency and copyback remain authoritative.
- Distinguish guest completion from display completion. Add opt-in commit-to-GPU-start and callback lifetimes; overlapping GPU durations remain unsuitable as utilisation percentages.
- Trial four spread-out16KiB LZ4 samples before fully compressing large high-entropy chunks. Raw chunks retain every byte and full integrity checking in the existing snapshot schema. This may trade output size for CPU time on an unusual unsampled distribution.
- Distinguish absent USB companion from sharing/clipboard presence, provide actionable recovery, supervise companion crashes, and fix installer selection of an obsolete bundle after a failed bundle update.
- Run touch contact heartbeats only with active contacts; preserve a final lift and host-side mapping recovery. Native USB touch and Pencil still need an installed compatible guest helper.

Validation checkpoint:

- Linux:2154 actual emitted ARM64 memory cases (Unicorn), far-chain linked/empty/exit-request/forward execution and literal isolation, GPU parser/store-option sanitizers, touch transport/watchdog sanitizers.
- Cloud required: macOS/iOS production Metal SDK compile; production Metal4 plan/adapter fixture; native JIT/MMU/grouping/eviction/lifecycle tests; paired far-chain and snapshot admission benchmarks; app typecheck/build.
- A Paravirtual cloud GPU cannot prove physical Metal4 pixel execution. Device thermal/FPS and real guest-command coverage remain physical checks. No speedup percentage or stable60Hz claim is inferred from compilation or a microbenchmark.
- No IPA is requested at this development checkpoint.

Second checkpoint: the compact chain stub remains for caches within direct-branch reach; large-cache inline slots are forced in native MMU and ring-eviction regression fixtures. SP folding includes split high/low immediates; grouping stops across SP/base changes. Metal4 preserves unspecialized default constants and valid depth-only pipelines, while actual legacy compute stage-input layouts retain compatibility with a specific reason. Missing-helper recovery now distinguishes an initial absent companion from an interrupted previously ready companion; the existing timeout/retry test remains mandatory.

The first cloud source5217932 passed focused SDK/plan/adapter checks. Its broader run caught the companion retry regression above; it is not a release proof. Native paired component medians were1.94ns vs11.24ns per deliberately far chained branch, and0.26ms vs4.39ms per4MiB high-entropy snapshot chunk with identical raw bytes. These are component timings on the cloud arm64 runner, not whole-guest speed, GPU execution, FPS, cooling or energy results. Mixed/compressible snapshot timings varied. The second checkpoint still needs exact-source cloud checks.
