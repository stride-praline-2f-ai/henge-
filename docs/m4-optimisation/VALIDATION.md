# Exact source validation

Source `3e5b8a725885d7131bfc7c247a644e9173f3e74f`, patch `47321e5c844cd68a891694c2d81dcd9394d4bddba605a2d604be6184e41415c7`, run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43392018361.

Required checks passed: native JIT/MMU/memory/input/VM lifecycle, sanitizer/concurrency/graphics checks, controls protocol and actual host/client TLS flow, owned releases/CPU gate, SDK typechecking and complete iPhoneOS Release app compile. Native PVG tests cover retained rings/read pointers/stamps/root IRQ, foreground replay and frozen teardown. Actual GPU tests verify late store actions preserve expected RGBA bytes.

Native input/GPU boundaries in the host/client service test are explicit spies; production services, pairing and TLS execute. Production controller UIKit touch, wireless pointer gestures and software keyboard execute in Simulator fixtures; actual guest Roblox controller recognition and physical multi-device behaviour remain unverified.

Existing16KB read-span baseline measurements remain host microbenchmarks, not device watts/FPS. New Low Power changes have no invented speed/thermal result.

Physical validation pending:
- Physical Duo/M4 app-loading latency, Roblox asset arrival/FPS, temperatures and watts remain unmeasured by cloud tests.
- Real controller/touch/gyro ergonomics, Link networks, audio interruptions and user APFS images need physical validation.
- iOS can suspend/terminate Henge; only completed compatible persistent saves survive app exit. No VM background Runner or PiP execution grant remains.

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

Delivered0.3.7(108), source5c3a565e4f93dd0198f7aafe28a897ac981dc444:
https://github.com/stride-praline-2f-ai/henge-/actions/runs/43397695154
Job131792570458 passed native/ASan/UBSan, actual JIT metadata writer, frozen retry
guard, full iOS app, IPA signing/framework/entitlement/runtime-marker checks.
Independent archive inspection also passed, including processing for JIT pairing,
pairing-only BG IDs, Runner absence in app AND sharing companion, and preserved
controller/Link/Instant Resume/audio/disk expansion paths. Previousfaed artifact
was rejected before delivery; it was never uploaded to Drive.

Artifact14023504290; IPA10091659bytes; SHA-256:
e4b055e694aff98f4106ff669fcf6e37e1fbf502987ff8758aaf4ddd595d5ebb
Drive (new file, previous0.3.6 retained):
https://drive.google.com/file/d/1Y9HO6D-b8bVBLWB-Y95mF9ECu6-yDNMQ/view?usp=drivesdk
Drive metadata and full byte-download SHA roundtrip verified. Ad hoc archive
requires the installation tool's supported signing/provisioning as usual.
Runtime source3e5b8a and patch47321e5... are unchanged in the metadata-only release
children.15controller captures inspected; physical Duo/M4 FPS, app-launch latency,
power and cooling gains remain unmeasured. Source engineering and artifact
production/delivery are complete; these hardware measurements are a separate gate.
