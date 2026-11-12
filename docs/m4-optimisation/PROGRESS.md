# Henge 0.3.5 (106) integrated source gate

Source `1336e6c5da6a4b5498b0705e77c4f6f8bfd11404`, patch `c09b2eb89d4851a04adfa05132afe140cdee42153a78af7086a3608068bb8a9e`.
Native and complete iOS Release compilation: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43308744375.
Production controller UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43308744339.

Shared M4/Duo source now includes demand-driven primary display cadence without
the commit-clock double gate, bounded existing frame-time capture, optional main
screen wireless video, portrait/tabletop controls, pointer pad and sensitivity,
opt-in gyro steering, automatic approved-pair reconnect, audio interruption
recovery, entitlement-free USB guest touchscreen and offline GPT disk expansion.
Existing Retina, ProMotion choices, MMU/JIT work, Instant Resume and CPU-only
runner integration remain. Experimental controls stay explicit.

The latest M4/Duo follow-up batches completed disk requests into one CPU0 wake,
skips outstanding DMA scans when nothing completed, and restores per-vCPU
identity reporting with regular statistics off. Existing disk/GPU worker reports
are available during explicit bounded captures; no new background timer.
Production concurrency regression:64 ready requests used1 wake versus64 on the
previous source.4096 raced completions, ring wrap, read/write, flush/barrier and
worker restart passed sanitizers. This is a wake-count result, not device FPS.

All required exact-source cloud checks passed. A metadata-only child requests
one final IPA; archive production, nested signatures and delivery are separate
gates. Physical limitations remain below; no interim IPA was packaged.
