# Exact source validation

Source `1336e6c5da6a4b5498b0705e77c4f6f8bfd11404`; patch `c09b2eb89d4851a04adfa05132afe140cdee42153a78af7086a3608068bb8a9e`.
Native/SDK/Release: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43308744375. Production UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43308744339.

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
