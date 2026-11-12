# Advanced controls — integrated source

Validated source `5701f45fcd7db0cdd19557b5a0f81924bead210c`; https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532298; https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532244.

One multitouch UIKit surface/input model serves the local overlay and controls-only
Link. The Hide Gamepad bar is removed; use the three-finger menu for visibility
and settings. Two circular sticks, radial dead zone, response curves, sensitivity,
inversion, D-pad, analog triggers, L3/R3 and View/Menu/Home are integrated. Size,
opacity and mapped mouse-look speed persist. Clear overlay areas pass through.
Ordinary relayout retains held fingers; actual geometry/tuning changes release
them. Hiding, pause and disconnect release owned inputs. No idle polling timer.

Wireless keyboard, touchpad and pad use the existing authenticated TLS transport
without a video codec or extra display. Short keyboard windows use a compact
scrollable sidebar; narrow layouts retain the segmented selector. Whole sticks
have one source owner. The additive protocol2 mouseSpeed field preserves old-peer
default900; update both devices for new tuning. Keyboard mapping remains explicit.

Generic USB HID stays default. The optional PS4-compatible profile is experimental
and applies on a cold Mac boot. It implements a 507-byte report descriptor, 64-byte
USB input, calibrated/address/firmware feature replies and bounded output reports.
It is not Xbox/XInput, physical USB passthrough, Bluetooth or real rumble/light-bar
output. A/B/X/Y positions map to Cross/Circle/Square/Triangle. Generic retains
16-bit axes, PS4 uses its real 8-bit report format. Guest Roblox recognition is
unverified. Snapshot size/later offsets are guarded; profile uses formerly zero
alignment bytes, and a saved session keeps its USB identity.

Native packet/xHCI and Swift ownership/tuning/geometry tests pass. Actual controller
touch, settings, pointer and software keyboard UI tests pass on M4 and at unfolded
951x669 on a labelled M4 canvas. Native Duo cloud SpringBoard/XCTest launch failed
in run43158389557/job130983663525; artifact13917861161 retains evidence. Earlier
public inner-display power requests timed out. Native folding is not validated.
Manual preview workflow native_duo=true preserves the strict native-window test.
Both IPA workflows retain henge-custom-ipa/cancel-in-progress; preview runs cancel
only older previews on the same branch. No IPA is produced by the preview workflow.
