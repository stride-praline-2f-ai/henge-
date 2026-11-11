# Current checkpoint

- Reconstructed source inherited at wrapper commit 343d2d84, patch 9ee35476;
  pinned Henge 3956a9fe, pinned Husk afe83d45 and reviewed upstream integrations
  preserved. Dedicated M4 development branch created.
- Added exact model + 10-core + high-memory profile selection, labelled topology
  fallback, no application to 8GB/9-core or simulator/Duo configurations.
- Retained 4-vCPU/8GB baseline; exposed native-supported eight-vCPU comparison.
- M4 preset preserves native Retina instead of applying the existing soft-image
  performance preset. User settings are not silently overwritten.
- Removed default M4 interval diagnostics and periodic thermal-state polling;
  notifications update the existing state. Warm/hot previews are deferred.
- Coalesce warmed ordinary-RAM helper reads within their validated 16KB TLB
  granule; all writes/misses retain the precise 4KB path and invalidation rules.

- Existing Metal library cache now responds to memory pressure and actual process
  headroom, including miss-driven recovery without a polling timer. Live owners
  retain their resources. GPU capability queries are runtime checks.
- M4 GPU encoding requests user-initiated QoS; presentation remains interactive.
  Default verbose GPU interval diagnostics follow the opt-in statistics switch.

Next: implement demand-driven display refresh coordination; finish dynamic memory
UI/budget integration and the remaining CPU/JIT/idle/input/gaming reconciliation. Native ARM64/MMU, Metal and full app validation are still
required. The complete M4 plan is NOT finished; packaging remains disabled.

- In progress: M4 CAMetalDisplayLink supplies damage-driven drawables to the one
  existing screen/cursor encoder, pauses between updates, uses runtime display
  maximum and requested presentation cap, and rejects retired target generations.
  Main-thread scene lifecycle disables inactive targets. VM pause now stops and
  drains presentation before GPU snapshot quiescence; Continue rearms it.
  This new display path is NOT yet SDK/runtime validated. Next action: add the
  controlled-queue regression, then compile against the real iPhoneOS SDK.

- First M4 cloud checkpoint 43104343753 passed JIT/MMU/superblock tests, VM
  lifecycle, graphics/concurrency diagnostics and complete production Swift SDK
  typechecking. Full application compilation was correctly withheld after a
  benchmark reference patch failed to apply. Updated that reference to remove
  the complete current helper-read shortcut; the comparator still exercises the
  old translation behavior, not a disabled benchmark.
- Guest-to-host clipboard delivery is now event-driven and coalesced; removed
  its 500ms polling task. ASan/UBSan passed 4000 concurrent guest updates,
  callback reentry, pending delivery and handler removal.
- Added controlled-queue tests of the production display-link methods and an
  explicit production iPhoneOS Metal syntax check. Await cloud execution.
- New Duo capture/user Low Power Mode observation is useful evidence about OS
  power policy, not proof of unchanged watts/workload. Added event-only launch
  and Low Power Mode transition records. No automatic refresh reduction added.

- Replaced the settled session's 1Hz UI heartbeat with coalesced native state
  notifications and cancellable maintenance deadlines. Startup/visible Details
  and Runner status retain timely polling; guest timers/interrupts are unchanged.
  Added cancellation, signal and timer-race tests for the production wait object.
- Native-touch and zoom-follow polling now stop when inactive/paused/external.
  Exact repeated primary cursor glyph bytes reuse the existing Metal texture;
  position/visibility changes still use the normal damage path.
- Explicit M4 Automatic now resets experimental/diagnostic switches coherently,
  preserves refresh/JIT choices and honours environment overrides. Memory UI
  distinguishes virtual guest RAM from dynamic process headroom.

Next source-level checkpoint: validate the new session wait/callback lifecycle,
M4 preset and cursor change in cloud; reconcile resource/gaming/Link coverage
against existing implementations. No IPA requested; complete integration and
application build remain mandatory.
- BootDisplay now stops its former 4Hz lifecycle polling after Metal takeover;
  native state notifications retain shutdown/restart handling. Together with the
  clipboard and session changes this removes seven scheduled checks/second on a
  settled desktop with diagnostics off (not a measurement of CPU watts saved).
- Checkpoint 6edf085a / run 43106141682 passed ALL native checks, sanitizers and
  full iPhoneOS Release app compile. No IPA produced. Later session/input/preset
  and cursor commits still require their own full validation.

Checkpoint a57898b0 / run43108150736 also passed native, sanitizer, SDK and full
app compilation. Both new session wait races and M4 default tests passed.
Cloud helper comparison (six samples each): small read12.3455→7.9685ns;
12KB span221.7045→194.52ns. These are component comparisons, not M4 energy/FPS.
Fastmem remained slower for several ordinary-hit microbenchmarks and faster for
conflict-heavy ones; grouped results also vary by code shape. Both remain
explicit experiments instead of being blindly enabled.

Final integration correction: restore archive failure now propagates and removes
partial output. Added a production-block failure regression. Exact iOS libzip
cache keys include host/toolchain, actual vendored sources and build script;
no app objects or executable JIT state are cached. Next: validate this final
patch, finish the recorded release gate, then produce the one final IPA.

Final default consistency finding: non-M4 hosts still inherited HV_STATS10 despite
release diagnostics being described as opt-in. Both the base environment and
statistics preference fallback now default off on every device, including Duo.
Explicit user preference/cache diagnostics/environment overrides still work.
This avoids hot-path timing/counter overhead; it is not a measured power result.
The production preference test now covers unset defaults on both host classes
and retained explicit opt-in. Validate the amended source before release.
