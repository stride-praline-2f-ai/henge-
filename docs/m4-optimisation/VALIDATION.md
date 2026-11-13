# Exact source validation

Source `2d12dd8710beb44296623df924776d74ef884d1d`, patch `e37d3d951c7249215736aad03ccd2f0c511b7f92de7892a93e0158c2f535851d`, run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43421862115.

Required checks passed: native JIT/MMU/memory/input/VM lifecycle, sanitizer/concurrency/graphics checks, controls protocol and actual host/client TLS flow, owned releases/CPU gate, SDK typechecking and complete iPhoneOS Release app compile. Native PVG tests cover retained rings/read pointers/stamps/root IRQ, foreground replay and frozen teardown. Actual GPU tests verify late store actions preserve expected RGBA bytes.

Native input/GPU boundaries in the host/client service test are explicit spies; production services, pairing and TLS execute. Historical production controller UIKit touch, wireless pointer gestures and software keyboard executed in Simulator fixtures. New UI previews were explicitly waived by the user; current native/Swift/SDK and full app checks passed; actual guest Roblox controller recognition and physical multi-device behaviour remain unverified.

Existing16KB read-span baseline measurements remain host microbenchmarks, not device watts/FPS. New Low Power changes have no invented speed/thermal result.

Physical validation pending:
- Physical Duo/M4 app-loading latency, Roblox asset arrival/FPS, temperatures and watts remain unmeasured by cloud tests.
- Real controller/touch/gyro ergonomics, Link networks, audio interruptions and user APFS images need physical validation.
- iOS can suspend/terminate Henge; only completed compatible persistent saves survive app exit. No VM background Runner or PiP execution grant remains.


Focused sizing/pointer model run43424369258 reconstructs the exact frozen source
2d12dd8710beb44296623df924776d74ef884d1d and verifies the cumulative patch digest.
The standalone macOS fixture explicitly imports CoreGraphics; every production
model assertion is retained. Engine comparison run43421862196 passed groups0/1/2
memory, MMU, first-fault, register emission and ring tests. Full native/app proof
is run43421862115. UI preview waiver applies only to new images, not these tests.
