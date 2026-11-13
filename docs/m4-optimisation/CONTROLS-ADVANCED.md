# Controls and new release features

Validated source `7c308dbeeb70834359eb31dba62e3cf38511e150`: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164304; https://github.com/stride-praline-2f-ai/henge-/actions/runs/43349164315.

Three-finger controls → virtual gamepad. Shared pointer touchpad supports movement
and scroll sensitivity. Wireless keyboard already includes its own touchpad.
Choose controller layout Automatic, Standard, Portrait or Tabletop. Duo uses
public active division geometry when available; manual Tabletop works without a
hardware fold signal. iPad Automatic is not treated as a folding phone.

Wireless controls → Video optionally mirrors the existing main display, without
adding a guest monitor. Landscape overlays controls; portrait separates video
above controls. Fit preserves the whole image; Fill crops explicitly. Controls-only
remains the default and starts no codec. Update both devices. The approved key and
host listener survive transient socket loss; bounded foreground retries stop on
explicit disconnect. Background releases inputs and does not promise continuous
video or VM execution.

Steering is opt-in in controller settings: enable, calibrate at neutral, choose
angle/invert. Tilt overrides only LX; throttle/brake, other stick and buttons
remain. Existing keyboard mapping converts steering to A/D. Sensor stops on
inactivity/settings/disconnect. Guest native HID recognition is not guaranteed;
Generic is default, PS4 compatibility remains explicitly experimental.

Touchscreen uses emulated USB port4, independently of gamepad port3. Update the
guest companion to this version and enable touchscreen on a compatible macOS27.2+
guest. No restricted CoreHID entitlement is required. Mapping failure or an older
guest falls back to pointer input; physical display UUID association still needs
hardware validation. This does not provide physical USB/iTunes passthrough.

Audio now rebuilds failed/interrupted output and preserves logical playback across
pause. Route/media-reset/foreground events trigger bounded recovery. The existing
manual Recover Sound action remains available.

Fully shut down the Mac and resolve/discard a saved session before disk expansion.
Storage → Expand Disk offers128/256/512GiB and custom up to2048GiB, grow only.
The original remains as disk.img.before-expansion. GPT tables are validated and
repaired for the new capacity atomically. Reopen storage settings to Finish macOS
volume expansion, including disks enlarged in an older release. The layout checker
can prepare a recognised trailing Recovery container on a clone: checksummed NXSB,
nonoverlapping aligned destination, verified copy, preserved UUID and both GPT CRCs.
The pre-preparation image remains as disk.img.before-apfs-expansion. Start macOS
and run the displayed diskutil command to grow the APFS container; unrecognised
layouts stay unchanged. Real disposable APFS filesystems, data preservation and
vendor container growth pass the cloud integration test. Booting a full Recovery
OS on a user's image remains physical validation. Export/remove the prior backup
before another capacity expansion; retain enough space for copy-on-write growth.

Use60Hz for a controlled smoothness baseline;120Hz remains available. The primary
presenter uses one display-link cadence while dirty and pauses when unchanged.
Wireless encoding uses negotiated60/120Hz limits and a bounded three-frame window.
Capture Diagnostics temporarily enables existing frame-time percentiles; idle and
cursor intervals are included, so host presentation rate is not game FPS.

Instant Resume: return quickly for in-memory continuation. For persistent saving,
use Save Mac & Leave and keep Henge visible until complete. Old native-layout
snapshots are clearly rejected with disks retained. iOS may deny background time
or terminate the process. CPU-only runner remains opt-in; GPU jobs can require
foreground. No entitlement bypass or unlimited background execution is claimed.

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
