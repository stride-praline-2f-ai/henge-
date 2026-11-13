# Project review validation

Final source: `12db2dae87bde63df81f559a6185a51afdf25019` on `review/project-038`.
Cumulative patch SHA-256: `4ac02f10ab89c6a396e242ac951a3cbd0009628000b0c79f7c0df27a6a19c373`.
[Final cloud run](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43444580204),
job131950566863: SUCCESS. Native, sanitizer and SDK checks passed; the complete
iOS application compiled and linked successfully (**BUILD SUCCEEDED**). Both IPA
packaging/verification steps were explicitly skipped.

## Confirmed checks

- Pinned source reconstruction and exact cumulative patch application.
- JIT publication, MMU/PAN/permissions, translation invalidation, fastmem and grouped memory references.
- VM startup/shutdown, pause/save/continue/restore, invalid snapshots, cleanup and repeated cycles.
- New actual RAM backing status, nonblocking lifecycle observation and deferred-network lifetime fencing.
- Metal resource lifetime/quiescence, private texture preservation, two display ports and GPU task address bounds.
- Actual xHCI touch reports: 1,000 motion updates, preserved initial hit/contact transitions,
  last-position cancellation, watchdog, overflow recovery and reconnect.
- Physical-button device ownership, display fitting, Retina geometry and settings defaults.
- Networking/DNS, audio recovery, clipboard ACK/retry, input and Link controls/video lifecycle.
- AddressSanitizer/UndefinedBehaviorSanitizer for native paths; ThreadSanitizer for DNS/idle notification paths.
  This is not a claim of whole-app ThreadSanitizer coverage for arbitrary generated guest instructions.
- Complete SDK typecheck of all 88 production Swift sources and native/Metal sources.

## Resolved test failure

Run43443089095 validated the same production runtime, but the new touch test
incorrectly expected cancellation at the original position after 1,000 movements.
Localdc2d4a8 changed onlytests/test_usb_touchscreen.c to assert the final delivered
position. Final run43444580204 passed that corrected guest-facing test. No assertion
was removed, and no production path was disabled. Its independent diagnostic pass
also completed with zero failed checks.

## Additional local evidence

Flag parser, host touch, fastmem walker/invalidation, RAM overflow bounds, translation
races, GPU copy bounds/surface sync, clipboard concurrency and production GPT/APFS
resize checks passed. Temporary Linux boundary checks executed the actual xHCI/PCI/
physical-memory code and GPU task-walker assertions, substituting CPU/IRQ/JIT setup;
the subsequent macOS native tests provide full runtime integration evidence.

## Release/device boundaries

IPA packaging is disabled. The released0.3.8(109) IPA is unchanged by this review.
No physical M4/Duo FPS, energy, iOS resident-memory accounting, Pencil/trackpad,
ProMotion panel or background-save completion result is claimed. Guest RAM can be
outside the process footprint while still using real physical memory. The old Duo
log confirms8GiB exclusion despite roughly6GiB headroom; the installed binary's
current allocation mode cannot be inferred from the headroom number alone.

Unit check: Theme.swift ByteText uses ByteCountFormatter.countStyle.file (decimal
GB);16GiB equals17.179869184GB. This can explain an approximately17GB iPad label
without implying additional physical RAM. Process headroom and guest allocation
remain separate quantities.
