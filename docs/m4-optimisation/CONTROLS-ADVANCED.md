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
