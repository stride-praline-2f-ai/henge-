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
