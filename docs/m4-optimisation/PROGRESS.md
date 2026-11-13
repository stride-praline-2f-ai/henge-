# Integrated source release gate

Validated source: `3e5b8a725885d7131bfc7c247a644e9173f3e74f`. Patch: `47321e5c844cd68a891694c2d81dcd9394d4bddba605a2d604be6184e41415c7`.
Cloud run: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43392018361.

M4 workstreams, shared Duo improvements, controls, Low Power policy and CPU-only runner source are integrated. Native regressions, sanitizers, actual Link host/client TLS negotiation, production Swift/Metal SDK checks, real Metal store-action tests and the complete iOS Release application compile passed.

The next metadata-only child requests one final IPA. Archive production and verification remain pending. Physical-device limitations are recorded in optimization-state.json; no measured cooling, core residency or Roblox-recognition claim.

Final loading/cleanup release gate,0.3.7(108):
Validated source3e5b8a725885d7131bfc7c247a644e9173f3e74f,
patch47321e5c844cd68a891694c2d81dcd9394d4bddba605a2d604be6184e41415c7.
Native/ASan/UBSan/Swift/Metal/full iOS Release app: run43392018361,job131773967687.
Production controller UI/native input/Resume: run43392018314; all four jobs passed.
Inspected10Duo+5M4 direct UIKit captures. Duo is an explicit951x669 unfolded
viewport on an M4 Simulator canvas, not A20/chip/fold hardware emulation.
Previous canceled Duo job retained separately; the final-source retry passed.

Implemented: TLB-first kernel secondary cache (no extra hot-hit instructions),
zero-copy contiguous block segment coalescing, moderate-warning shader archive
retention and first-pending save deadline, useful archive diagnostics. App Runner
UI, guest launcher/downloader, command queues and CPU/GPU background gates removed.
Settings simplified with explanations; retired experimental preferences backed
up once, environment overrides remain authoritative, explicit cache-off retained.
Update an old Mac sharing companion from Details → Sharing to retire its old
Runner worker. Cloud GitHub Actions builders remain available.

Cloud measurements: seven paired rounds show ordinary warmed TLB-hit overhead
removed vs cache-first, while a collision-heavy kernel loop retains~28x vs cache
off. Four contiguous disk pages use1I/O vs4 in the production descriptor fixture.
Neither result is a measured app-launch, Roblox FPS, temperature or watt gain.
No forced Retina reduction or permanent60Hz restriction was added. Instant
Resume, storage expansion, touch/gamepad/Link/audio/native Metal paths passed.
One metadata-only child opens final IPA packaging after this complete gate.
