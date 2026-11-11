# Final cloud validation

https://github.com/stride-praline-2f-ai/henge-/actions/runs/43110959717
Source `61fd5508a2431cce317546f46ae8acddf080c097`; cumulative patch `c847738eb8dd9433b25c6b13b9eeea6162ec8328f1dd3875e7d3659d6ddad191`.

Passed: native JIT/MMU/scalar/pair/vector/atomic/grouped tests; translation
publication/invalidation/cache-exhaustion barriers;64 deterministic CPU
acknowledgement notification races; VM creation/failure/stop/restart and repeated
pause/save/continue/restore; corrupt/incompatible/changed-disk/failed-save checks;
disk/audio/network/DNS lifetimes; both display snapshot ports and real queued
Metal completions; cache trim/live ownership; display-pulse queue/generation/scene
checks;4000 concurrent clipboard updates; Swift wait/signal/timer/cancellation
races; native-touch stale task ownership; M4 detection/defaults/Retina selection;
Link protocol/visibility/codec/input; ASan/UBSan and concurrency diagnostics;
production Swift/iPhoneOS Metal SDK checks; full iPhoneOS Release app compilation.
Restore archive error propagation has a production-block regression. Dependency
cache keys include actual source/script/toolchain identity. IPA checks remain a
required final pipeline stage, never inferred from compilation alone.

## Measured component results

Reference run43108150736, ARM64 cloud Mac, six sample medians:

| Complete helper operation | Before | After |
| --- | ---: | ---: |
| Small RAM read |12.3455ns|7.9685ns|
|12KB RAM read |221.7045ns|194.52ns|

The reference patches restore the old cache/emitter/helper path; this does not
isolate coalescing alone. This is not physical M4 energy or whole-app FPS.
Multiwindow cache and grouped-access benefits vary by memory/code shape; they
remain explicit experiments.4 CPUs and8GB are a retained safe baseline, not an
invented hardware optimum.1/1.5GB JIT and6/8/10/12GB RAM comparisons remain available.

## Physical limits

No cloud test measured watts, exact temperature, sustained Roblox/Safari FPS or
real Magic Keyboard/Pencil/external display experience. The new Duo capture was
an older0.3.0(101) binary: Normal/Warm thermal categories, roughly3.3–3.9 aggregate
CPU equivalents near the end, two sessions with different experiment settings,
and no Low Power Mode transition timestamp. Its reported cooling is a valuable
power-policy clue, not proof that guest workload is irrelevant or game FPS equal.
New logs record launch/power-state transitions without a polling timer.

Compare new/old source with equal workload, Retina, refresh, brightness and
instrumentation; vary CPU/RAM/JIT separately. iOS owns clock/core/thermal policy.
Actual runner registration needs user credentials in the guest; standard signing
has no guaranteed background GPU grant, and PiP does not provide one.


## Controls/power checkpoint
Run43118728860 passed native regressions, CPU-only runner pause/continue/save-refusal/foreground restoration, xHCI descriptor/IN transfers/coalescing/releases/ownership, production PVG ring gating/drain, ASan/UBSan and existing concurrency/graphics checks. Superseded before app compile by source cfb3d0d / run43119690219. This is partial evidence, not final release validation. Current later source also serializes runner transitions through InstantResume and adds real frozen-renderer destruction coverage; requires a fresh full source run.
Physical-only: iOS continued CPU grant/expiration, real macOS graphics-driver backpressure during Xcode, controller/GameController/Roblox recognition, multi-device gestures and actual LPM thermal/FPS comparisons. No physical test or temperature/power result claimed.
