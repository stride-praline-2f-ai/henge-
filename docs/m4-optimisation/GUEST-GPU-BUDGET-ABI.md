# CyPort memory-budget adaptation: verified boundary

The screenshots propose clamping a native Mac game's **in-process**
`MTLDevice.recommendedMaxWorkingSetSize`. This advisory getter can influence
an engine's up-front allocation choices; it is not an allocation limit or an
increase in iOS process/physical memory. Do not truncate requested heaps.

Henge hosts a complete macOS guest with its own IOGPU/Metal implementation.
A host Objective-C swizzle does not cross this boundary. No such ineffective
swizzle, invented PVG key, hard allocation cap or misleading setting is added.

## Actual API evidence

Read-only cloud macOS arm64 probes run on Xcode 27's real **AppleParavirtDevice**:

- Successful runs: 43704839305, 43705605615, 43705836406, 43706230300.
  Run 43705758728's probe completed, but artifact upload rejected a colon in
  an Objective-C selector filename. Portable filenames repaired that step;
  subsequent probe/upload runs passed. No app/IPA packaging was involved.
- `recommendedMaxWorkingSetSize` is implemented by **IOGPUMetalDevice in
  IOGPU.framework**, not the host GPU or AppleParavirtDevice's capabilities.
- Read-only method code and declared primitive ivars show it selects cached
  `_videoRam` when nonzero, otherwise `_sharedMemorySize` (offset 832 in this
  probe's OS ABI; this offset is NOT a production contract or patch target).
- On the probe VM: `_videoRam=0`, `_sharedMemorySize=5010800640`,
  `hw.memsize=7516192768`. The recommendation is approximately two thirds of
  guest RAM; max buffer length is 3758096384. It is not host device RAM.
- Initialization calls **IOGPUDeviceGetSharedMemorySize**; that copies a value
  cached in the guest IOGPU device reference. This is independent of the
  host's `recommendedMaxWorkingSetSize` getter.
- Runtime Objective-C type metadata enumerates the complete APV device-info
  struct: shader versions, GPU families, feature flags, alignment, layer,
  threadgroup and argument-table limits; there is no working-set budget field.
- The corresponding guest kernel `parseDeviceInfo` accepts the capability
  keys through 0x2d. Henge's existing 0x3a root reply supplies those capabilities.
  No verified protocol key carries a dynamic guest memory-budget recommendation.

This demonstrates why simply hooking the host API would not implement the
requested guest-visible feature. It does **not** prove every future guest
ABI/driver extension is impossible. An actual implementation would require a
verified guest driver protocol extension or per-process guest injection.
System-wide injection into macOS, signed browsers and anti-tamper games is not
an equivalent supported host policy. It is not shipped as a supposed fix.
Debug IOGPU boot arguments / wired limits are also not advisory Metal budgets;
do not enable kernel debug overrides or allocation failures under this label.

## Safe path retained and improved

- Existing single host cache controller receives real dispatch/UIKit pressure
  and dynamic process headroom; it bounds optional Metal4 compilation,
  archives, function libraries and spare MetalFX leases. It retains live
  guest surfaces/pipelines and restores admission when pressure recovers.
- Existing M4 automatic default is **4 vCPUs / 8 GiB guest RAM**. Explicit user
  memory and saved snapshots remain unchanged. Ledger accounting does not
  make guest pages free physical memory.
- New physical 116 capture shows observed Metal allocation up to 618.1 MiB, while a
  16 GiB guest exceeds whole-device physical capacity and system compression
  reaches 6.39 GiB. A copied 5 GiB cap would not address this capture's symptom.
- Implement bounded scattered disk I/O and failed-DMA invalidation based on
  the actual request workload; preserve host/guest ownership and flush order.
- Add opt-in commit-to-present timing, excluding idle no-work gaps and
  explicitly counting zero/invalid presentation timestamps. No new timer.

Guest-visible advisory budgeting is therefore **not implemented** in this
checkpoint: the required guest boundary is unverified, and the proposed host
hook is demonstrated to be ineffective. Do not claim GPU memory, hardware FPS,
heat, game load time or crash improvements from these cloud checks.
