# Henge 0.3.4 (105): Instant Resume and responsiveness

Release commit: `83b25224a23fc55daf54cf1f9f98ac278cfcf239`. Validated source parent: `5701f45fcd7db0cdd19557b5a0f81924bead210c`.
Build: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43179038972
IPA artifact: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43179038972/artifacts/13926505575
Drive: https://drive.google.com/file/d/12ex5VsQBP-gjIwxEk2EH-TiSF5zF_Vx9/view?usp=drivesdk

IPA bytes: 9,930,387.
SHA-256: `10b2f2c199dbfac649f82a53d15ee2d2f8dcfb7e2de0228b0c69624a146e58b6`.
The Drive download was fetched again and its SHA-256 and byte count matched.
Prior releases are preserved. Installation requires the installation tool's signing profile.

## Changes

- One generation/intent/view owner coordinates pause, save, continue, shutdown and asynchronous boot/restore.
- Returning cancels unfinished snapshot work immediately; compression workers drain safely before continuation. Background assertion expiry and duplicate notifications are handled explicitly.
- Foreground **Save Mac & Leave**, progress, retry and in-memory Continue controls.
- Actual saved CPU/RAM/display/Retina/refresh configuration is restored independently of changed next-boot preferences.
- Failed restores preserve recovery files; interrupted consumption uses a recoverable staged file. Existing compatible saves remain resumable with autosave off.
- Link reconnects only a matching saved second-monitor mode. Lifecycle observation, firmware display and pressure notifications avoid blocking the UI on the VM writer.
- Already published CPU acknowledgements avoid redundant park/wake notifications while retaining own pending invalidations.

Enable **Settings → Instant Resume**, then **three-finger controls → Save Mac & Leave** for a persistent save. Keep Henge visible until completion.

## Verification

Exact source validation43176532298 passed native JIT/MMU/device/lifecycle tests, sanitizer/concurrency/real Metal tests, actual production Swift coordinator tests, real Link TLS service tests, iPhoneOS SDK checks and the full Release app compile. Final release43179038972 repeated required checks and passed packaging.

UI run43176532244 passed M4 controls and the exact951×669 unfolded Duo viewport fixture; display screenshots were inspected. This is an explicitly labelled M4 canvas, not a native Duo folding pass. Native Duo cloud SpringBoard failure remains documented.

The IPA was independently inspected for source/version/patch, ARM64 device executables, helper/framework metadata, nested signing/entitlements, shaders/helper hashes and new Instant Resume runtime markers. Test-only lifecycle hooks are absent.

## Limits

iOS can deny/expire background time or terminate Henge. An unfinished save is not persistent recovery. Foreground Save & Leave provides time to finish; no unlimited background claim.

Earlier human-readable snapshots lack full immutable display configuration and are rejected clearly with snapshot and Mac disk retained. Other build/native-layout/disk incompatibilities remain guarded.

Real macOS application/peripheral recovery, physical M4/Duo timing/thermal/FPS comparisons and actual continued-processing grants need device validation. No device speed or cooling improvement is inferred from compilation or synthetic tests. Existing SwiftUI deprecated-onChange warnings remain technical debt; this release is not claimed warning-free.
