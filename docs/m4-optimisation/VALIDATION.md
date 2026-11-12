# Exact source validation

Source `f1f492f5ae935791859baa615aa01fe5c21e67bd`; patch `d1494f2e07873e3fb117d9a7b219f579ae9383dbbdda5520153e7436568b60e2`.
Native/SDK/Release: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43296777053. Production UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43296777073.

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
