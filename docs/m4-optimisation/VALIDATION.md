# Exact source validation

Source `ed4693c827c671efbf124b68c9d0161fe73ff778`, patch `20225ad181270cb36ff6b6e5b5fc860e046006eb863248db1525541da1cff8b7`, run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43461735695.

Required checks passed: native JIT/MMU/memory/input/VM lifecycle, sanitizer/concurrency/graphics checks, controls protocol and actual host/client TLS flow, owned releases/CPU gate, SDK typechecking and complete iPhoneOS Release app compile. Native PVG tests cover retained rings/read pointers/stamps/root IRQ, foreground replay and frozen teardown. Actual GPU tests verify late store actions preserve expected RGBA bytes.

Native input/GPU boundaries in the host/client service test are explicit spies; production services, pairing and TLS execute. Historical production controller UIKit touch, wireless pointer gestures and software keyboard executed in Simulator fixtures. New UI previews were explicitly waived by the user; current native/Swift/SDK and full app checks passed; actual guest Roblox controller recognition and physical multi-device behaviour remain unverified.

Existing16KB read-span baseline measurements remain host microbenchmarks, not device watts/FPS. New Low Power changes have no invented speed/thermal result.

Physical validation pending:
- Physical Duo/M4 app-loading latency, Roblox asset arrival/FPS, temperatures and watts remain unmeasured by cloud tests.
- Real controller/touch/gyro ergonomics, Link networks, audio interruptions and user APFS images need physical validation.
- iOS can suspend/terminate Henge; only completed compatible persistent saves survive app exit. No VM background Runner or PiP execution grant remains.
