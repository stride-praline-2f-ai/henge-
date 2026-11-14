# Henge 0.3.11 (112) delivered

Release source: `5f19e54446d7dda03c3704709e57bf51775a0c72`.
Validated runtime source: `ac3f64c4eb5c75799531e12092bf8f11752956f7`.
Cumulative patch: `1487d10f3da4e5af6b61a02e440fa0adb2c227fd96e3a7a81bdb7c8417984889`.

[Verified final build and artifact](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43608611687).
[IPA in Google Drive](https://drive.google.com/file/d/1c7XBtBbYMye_ampCt4uGAgYDena50jXX/view).

IPA SHA-256: `c5f155cbbd2416d19414de2935c5d0c0acd46315d66f62c3d2d933d701024c07` (10,278,766 bytes). The Drive download was read back and matched this hash. The artifact contains the completed optimisation-state and packaging verification reports; those final artifact receipts supersede the pre-packaging request state in the repository.

Implemented applicable NX18 techniques: real Metal4 guest graphics and native display adapters; exact per-encoder binding reuse; M4/A20 architecture-specific display archives; persistent runtime pipeline reuse with nonblocking compiler/capture epochs; explicit residency and pressure-aware job reuse; fence/LOD preservation; bounded in-flight presentation; backend/fallback/cache diagnostics. CPU reporting now pairs CPU/wall samples before log output and uses the runtime clock conversion. Existing engine, touch/Pencil, controls, Link, storage, clipboard and Instant Resume code is retained.

Passed native regressions, ASan/UBSan/targeted concurrency checks, real APFS growth, production Swift/Metal SDK checks, complete iOS Release compilation, arm64/platform/nested-signature/entitlement checks, exact GPU-archive hashes and actual archive inspection. The controlled real-GPU repeated-binding test preserves output while skipping 98.4% of redundant setters; it is not a game FPS result.

Actual Metal4 compute/render execution, M4/Duo gameplay/FPS/energy and physical input remain device validation: the cloud GPU is Apple Paravirtual and does not expose Metal4. GPU fixtures compile and report this capability blocker. Unsupported guest commands use the complete existing classic GPU path. Mac CPU/JIT/MMU emulation remains on the CPU. No off-label audio scheduling, forced A20 ISA on M4, invented game shader corpus or quality reduction was added.

Settings: Graphics backend → Automatic uses Metal4 where supported; Compatibility retains classic GPU rendering. Apply on the next full Mac start. Turn Session Diagnostics off for normal performance comparisons. Installation still requires signing with a supported profile.

This receipt changes documentation only and does not request another IPA.
