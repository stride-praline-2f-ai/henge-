# Henge 0.3.6 (107) integrated source gate

Source `7c308dbeeb70834359eb31dba62e3cf38511e150`, patch `65f08466111d7130c76e7c82bd541519fe56cd0069a6eb6de54c1d9826a6105a`.
Native and complete iOS Release compilation: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164304.
Production controller UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164315.

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

Desktop upstream integration: PR132/145 segmented JIT eviction preserves the
fork's physical-page chain indexes, full live-branch barriers and event-driven
quiescence. PR152 adds lazy, disposable OS/GPU-keyed persistent Metal archives,
bounded128MiB/2048single-PSO files,16lazy handles,64pending additions and4opaque
variants per stable hint. One save timer and pressure release retain one manager;
ordinary compilation remains the fallback.
PR133 fixes GPU task retirement and invalid pipeline/function records; PR137
accepts the final visible texture row with overflow-safe bounds. PR136 Auto
cursor density retains explicit fixed preferences. PR143 Safari b3a8 views choose
one immutable backend after Apple9/runtime format checks; texture ownership
preserves exact page identity. Other video formats retain IOSurface.

All four production PSOs reload cold after actual GPU use and their compute
outputs are checked; warm hits, corrupt/stale files and fragmentless fallback pass.
Independent public API controls record Paravirtual missing-function behavior and
execute the ordinary fallback; production cold-hit assertions remain required.
Archive reload/corruption/fragmentless, four-vCPU eviction/poison/split mapping,
real chain repairs, texture bounds, planar ownership and cached cursor settings
have exact-source cloud regressions. The cloud Metal adapter may use the Safari
reference branch; Apple9 shared-page performance and physical app launch,
Safari/Roblox frame-time and cooling comparisons remain unmeasured.

No forced lower resolution, QoS escalation, extra vCPUs or speculative direct
fault window is included. Latest main's AppKit additions concern Mac Apps mode,
not the full VM. Conflicting single-monitor mode/built-in UUID changes were not
blindly merged into the two-port/snapshot/touchscreen implementation.

Loading follow-up0.3.7: TLB-first secondary LUT, adjacent disk segment coalescing, warning-safe shader persistence, app Runner removal/settings migration. In development; native/SDK/UI validation pending and IPA gate closed. Details: runtime docs/m4-optimisation/LOADING-0.3.7.md.
