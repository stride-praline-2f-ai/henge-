# Validation

Passed locally: production scheduling policy/detection regression compiled with
GCC, AddressSanitizer and UndefinedBehaviorSanitizer; concurrent metadata reads,
M4 high-memory/low-memory/simulator/fallback selection and existing Duo policy.
This Linux result does not validate Apple QoS or physical core placement.
Resource-budget production policy also passed ASan/UBSan for dynamic headroom,
pressure precedence, exact thresholds and recovery.

Pending: ARM64 `test_mmu` coalesced read-span/PAN/remap boundaries, all native
lifecycle/snapshot regressions, native Metal detached-presentation regression,
Swift/profile/default tests and complete iPhoneOS app compilation.

Cloud infrastructure inherited five queued validation runs with no assigned
jobs; Actions cancellation and self-hosted inventory API calls returned 403.
Both original workflows retain shared cancellation. Do not claim a runnable
self-hosted Mac or launch packaging while unavailable.

Physical M4 comparisons: fixed workload, same Retina/refresh; compare 2/4/6/8
vCPUs and 6/8/10/12GB guest RAM separately, then 1GB/1.5GB JIT. Record sustained
task time, frame-time behaviour, process footprint/headroom and thermal category.
No whole-app speed, temperature, energy, battery or gaming gain is yet measured.

Update: cloud 43104343753 assigned a GitHub-hosted ARM64 Xcode27 runner.
JIT/MMU/superblocks, lifecycle/snapshots, concurrency/Metal diagnostics and actual
Swift/iPhoneOS typecheck passed. Failure was benchmark fixture patch drift,
now repaired; full app compilation remains pending. Existing self-hosted runner
mode remains supported but its availability is not established.
Local clipboard ASan/UBSan regression passed 4000 concurrent publications.
Display-pulse controlled-queue regression and explicit iPhoneOS Metal syntax
check are new and pending; do not infer a green M4 release from prior checks.

Green checkpoint: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43106141682
Source 6edf085a07b5df5164e5e35687f87087b82fe535, cumulative patch
6221e972bbd2dc01ec224fac70240830513c400e6db63a84f712366bd9381f35.
Native JIT/MMU, memory helpers, lifecycle/snapshots, display-pulse queue fixture,
clipboard concurrency, Metal/resource tests, Link/input/native checks, sanitizers,
actual iPhoneOS presenter syntax, production Swift typecheck and complete Release
app compile all passed. Packaging was skipped as required.
The newer event-driven session/boot-display waits, explicit M4 preset, optional
input ownership and repeated glyph reuse need the next exact-source checkpoint.

## Latest supplied M4 sessions (76B)

Read both logs completely; the app mirror and native log are not independent
samples. Binary 0.3.4(105), iPad16,5, 2752x2064 Retina, requested60Hz, 1.5GiB JIT.
4-vCPU runs use14GiB RAM/restored snapshots; 8-vCPU run uses11GiB/cold boot and
different fastmem/group/superblock settings. Both reached Hot before LPM and
returned Normal after LPM. Thus neither core-count nor thermal causality is a
controlled comparison. All bounded captures are LPM/Normal.

Excluding paused states and sub-second epoch-transition samples, median host
presentations/s by capture: 4CPU 27.55,21.70; 8CPU 15.73,24.36,8.30,15.66,24.71,
22.37. These are host presents, not Roblox FPS. The old binary includes the
double-pacing defect removed in current source. One capture includes a full
JIT reset; later slower captures have little translation work, so recompilation
is not the sole cause. Repeated memory warnings accompany11/14GiB guest RAM.
Virtual RAM and process footprint/headroom do not establish resident working set
or actual page-fault costs. Existing per-vCPU diagnostics all fail unavailable=4
with stats off; fixed at thread publication rather than enabling costly stats.

No data establishes8CPU as faster, individual P/E residency, shader compilation
as the asset bottleneck, or stable60FPS. Keep4CPU/8GiB as the reference, preserve
user choices and Retina/60/120Hz options. New bounded existing-worker reports
make disk, shader/pipeline reuse and per-vCPU work visible in the next capture.

## Resume/clipboard follow-up validation boundary

Local ASan/UBSan clipboard bridge test passes with4000 concurrent updates, acknowledgement
validation and old-companion negotiation. First cloud checkpoint passed actual snapshot
chunk round-trips, companion UTF-8/framing/retry, bounded Swift delivery, coordinator and
full application SDK typecheck. Its lifecycle allocation assertions expected even transient
packing failures to abort; tests now distinguish recoverable packing failures from essential
and persistent failures. Final exact-source results are required.

Not yet device-proven: multi-GB save duration within iOS background allowance, Roblox/Safari
resume on physical hardware, remote game-server session retention, Apple Universal Clipboard
transport/account/radio availability. iOS can suspend/kill the app; only completed compatible
snapshots survive termination. No JIT pointers or host Metal objects are persisted.


## Physical 116 follow-up: scattered disk I/O and causal presentation timing

Local ASan/UBSan: original disk chunk loop, new vector partial/EINTR/EOF/error
cursor, 128MiB ceiling, immutable iovecs, bounds/read-only/overflow, segment
validation, partial failed-DMA invalidation, 4096 raced real queue completions,
restart/flush/barrier and presentation clock/epoch/idle tests passed.

Cloud43707512216 (source0573a4ff) reconstructed the cumulative pinned patch,
passed native sanitizer targets and iOS SDK compilation of disk/virtio/renderer.
Cloud CPU reports **Apple M1 (Virtual)**; do not call it M4/Duo hardware testing.
Paired warm-file microbenchmark: 32 scattered 4KiB spans, same bytes, 2000
requests × five alternating rounds: scalar median19810.5ns versus vector
median4682.0ns per128KiB request (32 syscalls versus1). This measures a host I/O
component only, not app loading, cold storage, guest FPS, heat or energy.

Final enhanced real queue scatter test and diagnostic activation counters are
subject to the next exact-patch native/iOS run. No new IPA or hardware claim.

## Engine memory/dispatch follow-up

Native checks43714528667 cover mixed-base loads/stores, slot exhaustion, page
crossings, precise read/write faults, real two-way branch collisions, ASID/TLBI/
SMC/reset/eviction, CPU-owned hint isolation, MMU, poisoned four-vCPU eviction and
reference paths. The new runtime retains HvCpu assembly offsets and80-byte
HvBlock descriptors. Local source-extracted ASan/UBSan and emitted-memory checks
also pass:2166 Unicorn cases, concurrent allocation, chain index, publication
race, walk logs and shared fallback suffixes. Unicorn is not device execution.
Integration validation found a missing extracted-fixture dependency; fixed with
the production allocator. Full lifecycle/sanitizers and iOS app compilation need
the next combined result. No physical M4/Duo speed or thermal result is claimed.


## Engine117 final integration

Exact frozen engine patch e2f786d5a5b1c8c495654c612d807f4586d466b6957c94f59ffcf2bbde7486b2; source e431b3a4f2bdf2ad480a068fb3408f064b857c88; full native/JIT/MMU/VM/Metal, ASan/UBSan/TSan, input/Link/USB/APFS, latest-SDK and Release-iphoneos app compilation passed https://github.com/stride-praline-2f-ai/henge-/actions/runs/43719589751. Physical M4/Duo FPS, energy and temperature remain unverified.

Wider checked interleaved memory reuse and selective IJC preservation are enabled. Preload, recent-use retention, paired loads and site hints remain functional developer trials with measured trade-offs; they are not forced into the default. Undefined signed BRK exception encoding is fixed. One final117 IPA is requested; do not substitute the earlier116.


## Engine117 shipped

All implementation, native/sanitizer/app and final IPA gates passed. Release c7a115cfa93f8650a8e61144a19280096b82d5f1; run43720699793; artifact14164727662. Drive upload and full-byte SHA256 readback passed. See ENGINE-IMPLEMENTATION.md and ENGINE-117-VALIDATION.json. No source changes after validation; remaining FPS/energy comparisons require physical M4/Duo.


Build118 Safari follow-up: source `763e02fd4b114737af093f683b01d5ecd421df3a`, patch `53b3f15acb3c4a75fa42f96ee0ddf7e78732852472dda92aeecb7e39ab4673ef`, full native/app validation [43741006562](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43741006562) passed. Focused GPU proof43736645861 includes exact pixels,4097->1 Mach remaps and full-byte reference equality. Existing CPU/JIT unchanged from117. Version0.3.17(118); final IPA is still subject to packaging and artifact inspection. Device Safari FPS/heat unmeasured.


Build119 replay follow-up: source `49a1c6a23c56f093a1b6fb2f4d195c31df4fe2dc`, patch `629ce4011fc1fcf8390c9a88a1e097901f1b206f89aad269c1537fce1f9b534c`, full native/app validation [43752798689](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43752798689) passed. Exact GPU/IOSurface/Mach and command-storage correctness proof is attached in replay_followup. Full-copy default retained after measured partial-copy regressions; pooled command fixture improved, physical FPS/energy remain unmeasured. Existing CPU/JIT unchanged from118; profiling scope is labelled. Version0.3.18(119); final IPA is still subject to packaging and artifact inspection. Device Safari FPS/heat unmeasured.


Build120 replay follow-up: source `c147294bba935d6fc6153aa7bad9f962d5942c4d`, patch `0bc2b87ee134b2fa44c195508716232ac93312f83ab1089f770939d85d8c4d99`, full native/app validation [44822381680](https://github.com/stride-praline-2f-ai/henge-/actions/runs/44822381680) passed. Exact GPU/IOSurface/Mach and command-storage correctness proof is attached in replay_followup. Full-copy default retained after measured partial-copy regressions; pooled command fixture improved, physical FPS/energy remain unmeasured. Expanded checked register groups verified alongside existing CPU/JIT differential coverage; profiling scope is labelled. Version0.3.19(120); final IPA is still subject to packaging and artifact inspection. Device Safari FPS/heat unmeasured.


Build 122 starts from build 120. It restores immediate drawable presentation, retains display-link cadence, and lowers an oversized cold-boot RAM request without modifying saved sessions. Diagnostics are opt-in. Native, sanitizer and full app validation passed in [44937838375](https://github.com/stride-praline-2f-ai/henge-/actions/runs/44937838375). GPU and CPU component checks passed in [44937838353](https://github.com/stride-praline-2f-ai/henge-/actions/runs/44937838353). An iPadOS crash or termination report was unavailable. Physical startup remains to be verified.


Build 123 passed exact-source native, sanitizer and iOS Release checks in [45003021668](https://github.com/stride-praline-2f-ai/henge-/actions/runs/45003021668). The native disk tests include 4096 raced completions, ordering, partial DMA, and stability of the captured request header. The ARM64 JIT component check [45003021661](https://github.com/stride-praline-2f-ai/henge-/actions/runs/45003021661) retired a 400,000-descriptor fixture in 10.396 ms reference and 7.466 ms indexed median across three alternating rounds per configuration and verified survivor indexes. Physical Xcode extraction, install, sustained build, and thermal performance are unmeasured.
