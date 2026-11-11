# Integration audit — 2026-11-11

Reference failure 43027845388 is superseded by branch head 1fc2392: run43032012136 passed the native lifecycle and complete SDK checks but failed packaging. This repair builds on the actual head, rather than reapplying obsolete fixes.

## Root causes

* Suspend's `run_ended` flag persisted across guest lifetimes. A new machine could be rejected as already stopped. Reset it under pause_mu at start.
* Automatic integration lost `cpu0_ours = cpu0`: Continue could restart secondary CPUs without CPU0. Preserve explicit CPU0 ownership.
* The subsequent test segfault was separate: after a failed suspend, the test dereferenced board.ram while the normal exit callback could free it. Fail the regression immediately before accessing released memory; do not suppress the suspend failure.
* Xcode exported an iPhone SDK while the nested tl Makefile compiled bundled macOS guest programs. Scope SDKROOT and clang to macOS for those programs. The regression invokes that target with an iPhone SDK explicitly inherited.
* Pending Control-click work could mutate guest keyboard/button state during pause. Pause now stops/drains the single input queue and releases its owned modifier/button before halting guest CPUs. A real pending right-click regression checks the paused keyboard state.

## Ownership and activation map

| Responsibility | Authority / activation | Cooperation rule |
| --- | --- | --- |
| Executable memory | JITBootstrap / one borrowed RX/RW region | VM cleanup releases translation metadata, not the app-owned region; translation-layer use excludes later VM start in the same launch |
| vCPU lifecycle | host/vm.c, bridge api_lock, pause_mu | SAVE differs from shutdown/reset/host stop; join before destruction; preserve CPU0 ownership on Continue |
| Scheduling | custom host scheduling plan | QoS hints, never core affinity; no automatic count/quality reduction |
| Wakeups | one HvIdleTicker and explicit device/timer requests | advance generation to wake/join custom kicker_handle during pause/stop; no parallel upstream ticker |
| GPU replay | custom HvReplay serial worker + completion group | upstream real quiesce copies GPU-only content; no placeholder routines or second renderer |
| Display | per-port HvPvgDisplayState + GuestScreenSize | PR108 uses existing viewport fit and optional saved fillScreen; both protocol ports serialized; viewer disconnected after restore |
| Cursor / scaled modes | existing PR106/109 code | do not duplicate identical PR109 |
| Touch and scroll | custom NativeTouch and HardwareScroll | one fractional/coalescing delivery path; PR98's overlapping slider not independently activated |
| GPU diagnostics | existing opt-in atomic timestamps | PR112's overlapping last-end calculation not introduced; timings are not watts/utilization |
| Shader compatibility | iOS27 custom exact-byte library cache | old iOS17 relabel stage intentionally absent; do not claim iOS17 rendering compatibility |
| Persistent resume | snapshot.c + serial InstantResume queue | paused CPUs, drained disk/GPU, identity/layout/disk validation, write-part-then-rename, single-use restore |
| Snapshot schema | native header/version/fingerprint plus app ident | incompatible builds/settings/disk identities refused; no unsafe automatic struct migration |
| Audio | one AudioUnit backend | detach once under device lock on CPU0 exit; attach/resume on Continue; dispose before RAM release |
| Network / DNS | one slirp worker, bounded queues, DNS lifecycle | callback drain before teardown; system lookup failures retain original-query fallback; no duplicate resolver |
| Input | one ordered pointer queue and key ownership | exclude new input and drain before snapshot; no delayed key/button mutation after save |
| Backgrounding | inactive pause; bounded OS background save task | no unlimited iOS background execution promise; interrupted .part is not a complete save |
| Logging | HengeLog mirror + opt-in profiling | mirrored output is not a second run; stale word dumps excluded; no default GPU/profiler overhead |
| Packaging | shared henge-custom-ipa concurrency | latest push supersedes older IPA workflows; validate before package/artifact upload; pinned dependencies cached |
| Installation | original entitlements and helper identity | unsigned/ad-hoc IPA still requires user's installation-method signing |

## PR / upstream decisions

Main fetched for review is newer than the pinned integration input. The next experimental translation-layer symbol-loading change is not silently imported into a stabilization build. PR108 remains integrated. PR109 duplicates PR106. PR98 overlaps stronger custom scroll accumulation. PR112 overlaps atomic opt-in GPU timestamps and introduces shared completion ordering state. PR111 is experimental older-iOS rendering work; PR103 is an optional alternate layout. PR80,81,78 do not justify automatically changing QoS, superblocks or memory budgets. New external-drive and keyboard-layout PRs are unrelated to the failing lifecycle and are not automatic release additions.

## Evidence and practical limits

Run43032012136 passed twelve power cycles, failed-start cleanup, actual pause/continue/persistent restore, invalid identity and changed-disk rejection; six Metal cleanup cycles; JIT/MMU/memory/CPU synchronization; DNS/audio; Link/codec and complete production Swift SDK typechecking. Current repairs must pass those gates again, including pending-input and inherited-SDK regressions. Successful packaging alone is insufficient.

The supplied normal-use logs show ~312% process CPU, three capacity JIT resets, Hot at226s, zero reported GPU replay failures; the word-profile upload is stale. These establish activity, not a matched thermal improvement. Retain current four vCPUs, Retina/resolution/refresh choices. Synthetic microbenchmarks cannot establish Duo/M4 energy gains.

Physical macOS desktop/game compatibility, iOS background task duration for large saves, secondary display/cursor restoration across real viewer reconnect, unfolding/external monitor behavior and sustained thermals remain device validation requirements. Surface signatures now scan every byte, with per-batch duplicate scans still coalesced; signatures remain hashes rather than collision-free dirty tracking. Native bandwidth costs are reported separately. The separate Mac Apps translation layer is experimental; its embedded programs are macOS artifacts even though the host is iOS.


## Follow-up correctness repairs

The renderer previously sampled one word per 64-byte span, missing byte 9 and most other pixel changes. Full-byte parallel-lane signatures replace that sampling; exhaustive small-buffer/tail/alignment mutation regressions run with ASan/UBSan. This costs bandwidth and is a correctness repair, not a thermal improvement claim.

Metal snapshot schema 2 preserves both display mappings and both cursor glyphs, dimensions, hotspots and visibility. Input lengths, port counts, dimensions and strides are validated before allocation; both textures are prepared before changing live state. Empty glyph restoration clears stale images. Secondary transport connectivity still requires a new handshake, and is never resurrected from stale network state. Real Metal tests roundtrip both glyph textures, reject malformed/truncated state, and exercise six create/quiesce/destroy cycles.

Snapshot format version 3 rejects older incompatible files. Device-state allocation failure and renderer restoration failure now propagate instead of producing a successful incomplete save. RAM chunks validate bitmap counts, bounds and encoding flags, including empty chunks. Native saves serialize their temporary-file and compression state without changing UI reader ownership. The allocation-failure injection hook exists only in the native regression object; release builds contain no hook or allocation counter.

Lifecycle coverage adds eight immediate pause/continue cycles, save failure with an existing valid snapshot, seven controlled allocation failures, partial-file cleanup, continue after failure, old-format rejection and truncated-file rejection. Existing restart/host-stop, wrong identity, changed disk, correct restore, clock/counter and input-release tests remain required. These tests use synthetic guest code and real native device workers, not a complete macOS game workload. Physical Duo/M4 visuals, late viewer reconnect, background deadline expiry and sustained thermals still require device validation.

GPU quiescence now propagates failure to the pause-clean flag. Unmappable/unsupported GPU-only content, encoder allocation failure or a failed command buffer prevents a persistent save; dirty flags clear only after completed readback. In-memory Continue remains available. Native tests also submit two saves concurrently and require both to complete as valid serialized replacements. A deliberately delayed paused interval verifies the counter remains frozen.

Sanitizer gates rebuild the full native lifecycle and Metal dependencies in separate ASan/UBSan objects, and resolver/idle-ticker concurrency with ThreadSanitizer. Release objects are built separately. Native leak checks explicitly count file descriptors, workers and Mach ports; AddressSanitizer is not presented as a complete system-framework leak detector.

The instrumented lifecycle exposed an actual signal-stack ownership defect: guest CPU preparation replaced a runtime-owned alternate signal stack, then runtime teardown attempted to unmap Henge's malloc-backed stack. CPU preparation now retains an already installed runtime stack. A foreign-stack regression covers this ownership rule. Snapshot schema 3 additionally checks full header/section contents and decompressed RAM plus chunk metadata, so a same-length corrupt CPU payload is refused before execution; these checks detect corruption, not malicious tampering.

Pause now publishes authoritative released keyboard/modifier/touch/button reports, including when a physical release arrives while input is excluded. This prevents held keys or touches surviving interruption. Snapshot tests retain the original data on failed replacement and overwrite an interrupted partial file on a subsequent successful save. The Instant Resume setting explains the actual OS background-time constraint.

The Apple runner also rejects disabling a signal stack with zero size (ENOMEM). Cleanup now supplies the owned stack address/size when disabling before freeing it. The regression verifies this teardown rather than ignoring the error. Both build entry points reject a superseded development head before compilation, and packaging rechecks it immediately before artifact publication.
