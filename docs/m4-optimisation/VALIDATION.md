# Exact source validation

Source `82f33a651f50658e449e3671496628ce0a724b29`, patch `06781355a3b0782e0c1a5c444793230e8583546c6d23bdf1611257ff216990a2`, run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43123278423.

Required checks passed: native JIT/MMU/memory/input/VM lifecycle, sanitizer/concurrency/graphics checks, controls protocol and actual host/client TLS flow, owned releases/CPU gate, SDK typechecking and complete iPhoneOS Release app compile. Native PVG tests cover retained rings/read pointers/stamps/root IRQ, foreground replay and frozen teardown. Actual GPU tests verify late store actions preserve expected RGBA bytes.

Native input/GPU boundaries in the host/client service test are explicit spies; production services, pairing and TLS execute. UIKit touch events and actual Roblox controller recognition remain hardware-only.

Existing16KB read-span baseline measurements remain host microbenchmarks, not device watts/FPS. New Low Power changes have no invented speed/thermal result.

Physical validation pending:
- iOS continued CPU grant/expiration under actual signing and Low Power Mode, and real macOS graphics-driver backpressure during long Xcode jobs need device validation. CPU mode is experimental and opt-in; GUI/Simulator/GPU jobs may wait for foreground.
- Virtual HID controller recognition in macOS/GameController/Roblox, physical multitouch/trackpad/keyboard/controller ergonomics and cross-device real-network use need hardware checks. Keyboard mapping is an explicit alternative, not a native controller guarantee.
- Actual M4/Duo temperatures, watts, P/E-core residency, Low Power Mode frame rates and4-vs6-vCPU performance have not been measured in cloud. Compilation/native host tests do not establish thermal gains.
- Instant Resume old-build/native-layout snapshots are rejected; user disks are retained for cold boot. CPU-runner in-memory pause is not a persistent-save guarantee; iOS may terminate the process.
