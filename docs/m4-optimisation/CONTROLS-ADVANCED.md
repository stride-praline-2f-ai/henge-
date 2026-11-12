# Controls and new release features

Validated source `f1f492f5ae935791859baa615aa01fe5c21e67bd`: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43296777053; https://github.com/stride-praline-2f-ai/henge-/actions/runs/43296777073.

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
repaired for the new capacity atomically; no APFS/recovery contents are moved.
After a cold boot enlarge APFS using the displayed macOS command or Disk Utility.
A following recovery partition may require manual layout work; extra raw capacity
is not automatically usable filesystem capacity. Export/remove the prior backup
before another expansion; retain enough space for copy-on-write growth.

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
