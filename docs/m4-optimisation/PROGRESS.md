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
