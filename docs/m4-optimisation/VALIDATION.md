# Exact integrated validation

Source `d3926d0cb1d05067a7d4525f2c0068afda9b29a7`, patch `1e321ed52bee7d1e5a9370512a182ce7e908b2834508c0b6a69001c0cdd5a3e4`.
Native/Release application: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43160398405. Controller previews: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43160398386.

Passed: pinned source reconstruction; native JIT/MMU/ASID/page-crossing/permission
differentials including interleaved memory groups; shared-copy emitter graph;
concurrent JIT allocation/tail/limit checks; VM lifecycle/snapshot/teardown;
ASan/UBSan/concurrency; actual Metal resource/LRU/function/store-action checks;
input, network/audio lifecycle and real Link host/client TLS; production Swift
SDK checks and complete iPhoneOS Release application compilation.

Controller checks exercise actual xHCI EP0 setup/data/status, 507-byte descriptor,
Generic/PS4 packets, IN/OUT/features, neutral release and disconnection. Swift
checks cover bounded tuning, geometry, ownership, multi-touch and wire compatibility.
Production UIKit/SwiftUI UI tests exercise a real stick drag/button release, sensitivity,
wireless pad, pointer pan, software keyboard and compact layout controls.
M4 uses the installed M4 16GB simulator; Duo uses a separately labelled 951x669
viewport on that working simulator, including narrow/wide layout transitions.
Xcode 27.2 is recorded; host VirtualMac2,1 is not A20/M4 performance emulation.

Failures retained: native Duo run43158389557/job130983663525/artifact13917861161
failed before UI launch with SpringBoard/test-runner failure; earlier supported
inner-display power RPCs timed out. This is not a native Duo pass.
M4 attempt1 in run43160398386 timed out in XCTest's AX snapshot query at the
wireless touchpad (artifact13918028386); retained spindump shows the app main
thread idle. Only that job was retried on a fresh runner, with assertions and
source unchanged. The final preview receipt records the successful attempt.

Measured host fixtures: 100 identical Metal library requests reuse one first
function; a three-overlap grouped fallback fixture emits 7 rather than 15 words.
These are not whole-emulator speed, game FPS, watts or temperature measurements.
JIT/RAM defaults were not enlarged and display clarity was not reduced.

Physical validation pending: native Duo fold/foreground/peripheral behaviour,
Roblox PS4 recognition and sustained FPS, M4/Duo cold-start and thermal/power
comparison, cross-device real-network ergonomics, and actual iOS continued CPU
processing grants/expiry. Runner mode remains experimental; iOS may suspend or
terminate Henge. GPU-dependent guest jobs may need foreground.
