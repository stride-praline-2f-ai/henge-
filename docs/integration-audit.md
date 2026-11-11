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

Physical macOS desktop/game compatibility, iOS background task duration for large saves, secondary display/cursor restoration across real viewer reconnect, unfolding/external monitor behavior and sustained thermals remain device validation requirements. Existing sampled surface hashing is not an exact dirty tracker. The separate Mac Apps translation layer is experimental; its embedded programs are macOS artifacts even though the host is iOS.
