# Exact source validation

Source `7c308dbeeb70834359eb31dba62e3cf38511e150`; patch `65f08466111d7130c76e7c82bd541519fe56cd0069a6eb6de54c1d9826a6105a`.
Native/SDK/Release: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164304. Production UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164315.

Passed: pinned reconstruction; native JIT/MMU/ASID/permission/page-boundary
regressions; grouped-memory differential tests; code publication/invalidation;
VM lifecycle/snapshot/teardown; sanitizers and concurrency; real Metal resource,
store-action and pipeline reuse; native audio interruption/pause/failure recovery;
xHCI gamepad and USB touchscreen coexistence; real hardware video encode/decode
and TLS flow, paced refresh and credit backpressure; controls-only host/client
services, owned input release and reconnect; production display-link callback
fixture; GPT cloning/CRC/payload/backup preservation; Swift6 guest helper and
safe two-bundle archive validation; complete iOS SDK and Release app compilation.

UI checks use production controller surfaces, pointer gestures, software keyboard,
sensitivity, portrait/tabletop/video controls. M4 is the installed M4 Simulator.
Duo uses an explicitly labelled exact 951x669 unfolded viewport on an M4 canvas.
Native Duo runtime failed before UI launch in run43158389557/job130983663525;
artifact13917861161 retains that evidence. This is not native folding validation.

Cloud is not M4/A20 performance emulation. Physical checks remain: sustained
60/120Hz frame times, equivalent-work cooling/power, gyro ergonomics, Roblox HID
recognition, real-network recovery, host audio routing, actual guest USB display
association, APFS enlargement on user disks, and real background grants/expiry.
No measured whole-VM FPS, temperature or efficiency-core residency claim.

M4 logsACBA used 14GiB guest RAM with experimental grouped/superblocks enabled.
Host presentation samples were14.12..29.60/s (median24.98), not game FPS. The
production double-cadence bug is fixed; use the existing M4 Automatic4CPU/8GiB
baseline for comparison. Saved VM settings are not silently overwritten.

The newer76B logs also contain8CPU/11GiB cold boot. Both4CPU/14GiB and8CPU/11GiB
reachedHot before LPM andNormal after LPM. DifferentRAM/flags/workloads prevent
an A/B inference. Active capture host-present medians4CPU27.55/21.70 and
8CPU15.73/24.36/8.30/15.66/24.71/22.37 do not establish8CPU as faster.
A full JIT reset occurs in one capture; later slow captures have little translation
work. New bounded CPU/disk/GPU cache reports help separate the remaining causes.

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
