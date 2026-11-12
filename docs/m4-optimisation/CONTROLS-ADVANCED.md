# Advanced controls integration

One native UIKit multitouch surface and one PadInput model serve the local
overlay and the controls-only Link viewer. No second transport, rendering loop
or controller polling timer is added. The old Hide Gamepad bar is removed; the
three-finger menu owns show/hide and settings. Clear overlay areas pass through
to the Mac display. Geometry/tuning changes neutralize held fingers without
unplugging the controller; hiding, pausing and disconnecting release ownership.

Two circular sticks use radial dead zone/rescaling, response curves and separate
sensitivity. Add D-pad, analog trigger drags, L3/R3, View/Menu/Home; configure
size, opacity, inversion and keyboard-mapped mouse-look speed. Tuning persists
in a bounded value object. Complete state packets, bounded native queues and
existing TLS pairing remain authoritative. A whole stick belongs to one input
source; local and remote axes are not mixed independently. Optional mouseSpeed
is additive on protocol 2; old peers default to 900. Update both devices to use
new tuning across the wireless link. Keyboard mapping stays an explicit mode.

Native USB profile: Generic HID remains the existing default. The host settings
add PS4-compatible (experimental), applied on a cold guest boot. Its 507-byte
HID descriptor, 64-byte USB input reports, button/hat/stick/trigger layout,
calibration/address/firmware features and separate OUT completion path are
implemented. This is not Xbox/XInput, Bluetooth pairing or physical USB
passthrough. A/B/X/Y positions map to Cross/Circle/Square/Triangle. This profile
uses real protocol 8-bit sticks; Generic HID retains 16-bit sticks. Virtual
motion stays neutral and physical rumble/light-bar effects are not implemented.
Driver recognition and Roblox compatibility must still be verified in the guest.
References: Apple support https://support.apple.com/en-gb/111100 ; Linux
hid-playstation and hid-tools/device/sony_gamepad.py; SDL_hidapi_ps4.c.

Snapshot compatibility: profile occupies a formerly zero alignment byte before
gp_head, with a compile-time layout guard. Size and later offsets remain
unchanged. Old zero-filled snapshots restore Generic HID; saved sessions keep
their stored USB identity. No snapshot is silently reinterpreted as a new device.

Validation pending: full native xHCI EP0/IN/OUT and neutral/disconnect checks,
Swift response/geometry/multitouch tests and actual simulator UI. New independent
workflow runs packet/tuning checks and two parallel latest-installed-Xcode UI
fixtures: primary Duo unfolded 951x669, plus M4 13-inch 1376x1032. It records the
actual simulator model, runtime, host chip and Xcode. If no Duo simulator type
exists, a large iPad simulator renders the Duo viewport fixture; this is never
claimed to emulate A20 scheduling/GPU/thermals. M4 simulator type is preferred
when installed. Folded/rotation paths are additional lifecycle checks. Real
XCTest screenshots and logs are artifacts; no IPA is produced by this workflow.
Existing IPA workflows retain shared henge-custom-ipa cancellation. Each new
preview run cancels older previews on the same branch; native/simulator matrix
jobs may run in parallel. No unrelated workflows are cancelled.

Follow-up: CoreGraphics imports are explicit for native macOS geometry checks.
Simulator selection tries compatible installed device/runtime pairs and records
fallbacks/errors. Ordinary SwiftUI relayout preserves held fingers when bounds
are unchanged. The shipping Link keyboard/trackpad surface is extracted with
callback injection and shared by both production and previews, including real
software keyboard and pointer gesture checks; no placeholder input panel is
used. Transport ownership and the protocol remain unchanged.

M4 UI checkpoint: source 7d334542, preview run 43153708430, job
130968708030 passed actual stick travel/releases, sensitivity settings, wireless
pad, pointer pan and software-keyboard typing. Counter values now expose raw
accessibility values separately from localized display text. UIKeyInput is a
TextView in accessibility, so tests query its identifier across element kinds.
Duo selection must examine all compatible runtimes before fallback: the runner
has both generic 27.2 (without Duo) and a dedicated iPhone19,4 27.2 runtime.
The production selector has a regression for this exact inventory shape.
The next checkpoint attaches Simulator's display host before requesting inner
screen power, and uses a compact scrollable sidebar in short keyboard windows.
No native Duo unfolded or guest controller-recognition claim yet.

## Cloud Duo limitation and complete layout alternative

Native Duo probe b3bf5793, run 43158389557/job 130983663525, artifact
13917861161 failed before app UI tests: the dedicated iOS 27.2 (24B91016s)
Simulator could not launch the XCTest runner because SpringBoard crashed.
Earlier native attempts also timed out on the supported inner-display power RPC,
both before and after automation attached; the runner has no Simulator.app GUI.
These failures are retained, not reclassified as Henge passes.

The independent preview workflow now runs the complete, unchanged controls
interaction test at the unfolded 951x669 viewport on the working large M4
Simulator. An added assertion requires the actual 951-point surface width.
Artifacts record actual model/runtime and validation_mode=unfolded-viewport-fixture;
the gate distinguishes passed_layout_fixture from native Duo passed. Native
fold/hinge transitions remain unverified. Manual workflow input native_duo retries
the strict native-window test; no app release timer, feature or test is disabled.
M4 tests retain the actual M4 device type. Neither setup emulates physical chip
performance, P/E placement, watts or thermals.
