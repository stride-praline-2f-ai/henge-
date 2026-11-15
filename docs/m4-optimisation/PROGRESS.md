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
