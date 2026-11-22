# Current source checkpoint: physical 116 M4 follow-up

- Validated source wrapper: bb3c4666; runtime code0179a1a.
- Exact patch / run / test details: [guest-budget-validation.json](guest-budget-validation.json).
- All focused native sanitizer and changed-production iOS SDK checks passed43707970393.
- New code: scattered per-request disk I/O; overflow and failed-DMA coherence fixes;
  opt-in activation counts and idle-independent presentation latency.
- Full log findings: [PHYSICAL-116-M4-16GB.md](PHYSICAL-116-M4-16GB.md).
- Guest budget adaptation is NOT implemented: demonstrated guest IOGPU boundary;
  no verified PVG budget key. See [GUEST-GPU-BUDGET-ABI.md](GUEST-GPU-BUDGET-ABI.md).
- Retain4vCPU/8GiB automatic profile; explicit user RAM / existing snapshots unchanged.
- Hardware gains remain unverified. No new IPA; release flags remain false.

Next source action if continuing: preserve this validated patch; use actual device
`block-io-shape` and `frame-submit-latency` evidence before claiming app/frame gains.
If releasing, run the complete integration/IPA gate against this exact patch;
do not substitute the old116 artifact as a newly built implementation.


## Engine117 final integration

Exact frozen engine patch e2f786d5a5b1c8c495654c612d807f4586d466b6957c94f59ffcf2bbde7486b2; source e431b3a4f2bdf2ad480a068fb3408f064b857c88; full native/JIT/MMU/VM/Metal, ASan/UBSan/TSan, input/Link/USB/APFS, latest-SDK and Release-iphoneos app compilation passed https://github.com/stride-praline-2f-ai/henge-/actions/runs/43719589751. Physical M4/Duo FPS, energy and temperature remain unverified.

Wider checked interleaved memory reuse and selective IJC preservation are enabled. Preload, recent-use retention, paired loads and site hints remain functional developer trials with measured trade-offs; they are not forced into the default. Undefined signed BRK exception encoding is fixed. One final117 IPA is requested; do not substitute the earlier116.


## Engine117 shipped

All implementation, native/sanitizer/app and final IPA gates passed. Release c7a115cfa93f8650a8e61144a19280096b82d5f1; run43720699793; artifact14164727662. Drive upload and full-byte SHA256 readback passed. See ENGINE-IMPLEMENTATION.md and ENGINE-117-VALIDATION.json. No source changes after validation; remaining FPS/energy comparisons require physical M4/Duo.

## CPU-heavy work and Xcode extraction

Build 122 booted the iPad16,5 with eight vCPUs and an 8 GiB guest. The Xcode
extraction capture reported Serious at 977.139 s, about 236 s after the second
boot, with Low Power Mode off and a 1280×960 guest scaled to 2560×1920.
Normal returned about 14 minutes later. The capture had diagnostics off.
The logs contain no stage boundaries or CPU/disk service rates, and the later
background save began after that thermal recovery.

CPU changes: coalesce local range-TLBI housekeeping, reuse decoded memory
operands in grouping, and admit ADR/ADRP across checked memory spans when it
preserves the base. The indexed JIT trial uses stable descriptor slots and
existing executable-page lists under the stop-the-world barrier. Enable it
with `HV_JIT_INDEXED_BLOCKS=1` in henge-env.txt. The initial native fixture on
cloud ARM64 with 400,000 descriptors measured medians of 14.311 ms (reference)
and 7.684 ms (indexed), with correct hashes, survivor addresses and reused slots.
Duo and baseline settings do not opt into the experiment.

On the ten-core/16 GB M4, Automatic scheduling with more than four vCPUs
requests Default QoS for all vCPUs at Serious or Critical, retains that choice
through Fair, then restores User Initiated at Nominal. The guest topology,
virtual clock and presentation settings stay fixed. `HV_M4_THERMAL_CPU=0`
restores the reference for comparison. Background snapshot packing is capped
at four workers at Serious and two at Critical on this M4, with lower existing
memory caps applied first. These changes are not a measured reduction in heat.

Capture reports now separate incoming scanouts from commits. Initial planar
sync can count toward the current exact command epoch; failed copies retry.
Cross-command dirty tracking needs authoritative write coverage for both the
guest CPU and DMA. The current 1.5 GiB executable mapping is backed by the
existing static low-address reserve, so a larger limit is not a safe setting
change. Full tiered translation and indexed branch-exit retirement are pending.

Device comparison: re-run the same extraction and an equivalent port build
at 8 GiB with the same display and power settings. Compare 6/8 vCPUs, default
versus indexed eviction, and thermal policy on/off independently. Use elapsed
extraction/compile/pack time, duration at Serious/Critical, and Safari
input-active frame times. Run timing passes with session diagnostics off.

The cold emitter also omits the exact-tail slow-path check for PC-relative
literals whose address is known to be outside the tail. The exact check stays
for true tail literals, with native tests for emitted words and guest results.
Thermal event logs include one resource snapshot when continuous diagnostics
are disabled. They record cumulative CPU time and resource accounting, not the
guest process that caused a thermal transition.

Build 123 candidate: indexed descriptor eviction is now automatic on the
detected ten-core/16 GB iPad M4. Set `HV_JIT_INDEXED_BLOCKS=0` for a reference
run. Other models retain the previous default. The stable hash and executable
page index avoid rebuilding survivor metadata. The last cloud comparison
measured 11.008 ms versus 6.806 ms for the same 400,000 descriptors.

Virtio disk admission parses the command header once and publishes up to
16 requests per mutex acquisition. Contiguous guest spans reuse one validated
RAM region lookup per span. Flush and barrier ordering, media error handling,
sector validation, and zero-copy scatter/gather stay intact. Native completion
fixtures additionally change a guest header between admission and execution to
check that workers honor the admitted opcode and sector.
