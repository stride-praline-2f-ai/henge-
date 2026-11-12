# Exact integrated validation

Source `5701f45fcd7db0cdd19557b5a0f81924bead210c`, patch `a690fc757ab4d5638742a9aa442b92bac0a6ae605e552c5f05fe4d00b102a641`.
Native/Release application: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532298. Controller previews: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532244.

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
