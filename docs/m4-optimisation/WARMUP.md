# Warm-up follow-up — 12 November 2026

Evidence: user Duo iOS 27.2.1 log, custom source 02151cf, build 0.3.2(103).
Main log SHA256 2ffede340d3a33386f5189981d8c2fbaf3f622f697a483bb16d4697198f1ecb9.
Native log SHA256 fd1884a6bcf7e40ba743f88a258f66b33bf0c3f7b56054f879cb228706ab0205.
Low Power Mode is on before VM boot; all recorded thermal categories are Normal.
The 30-second capture begins about 777 seconds after VM start, so does not
establish the early desktop/Roblox bottleneck. It shows 3.51–3.71 aggregate CPU
core equivalents and five cumulative JIT resets, with no reset during capture.
Host presentation is not Roblox FPS; overlapping GPU durations are not utilization.
44 UIKit memory warnings arrive in a roughly 7.4-second burst before capture,
with about 1.2 GiB process headroom. System pressure can still be real. Each
notification previously purged all library cache ownership. This is evidence of
repeated purge requests, not proof that it caused initial loading delays.

Implemented against existing replay, not a second renderer:
- Exact-binary library cache uses LRU instead of FIFO, so repeated hits retain
  hot libraries within unchanged byte/entry limits.
- Reuse the same unspecialized first function for identical library bytes;
  no persisted GPU/JIT code, task-reference cache, pipeline changes or speculation.
- UIKit warnings use the same existing 8-entry/2 MiB warning budget as the
  dispatch pressure handler instead of unconditionally discarding every entry.
  Critical pressure or <128 MiB headroom still purges all cache ownership.
  Warning budget holds for 30 seconds after the last UIKit warning and recovers
  on later compilation misses; no new timer. Live guest owners remain valid.
- Existing optional GPU report includes function build/hit and warning counts.
  Redundant empty-purge logging is suppressed. No per-access instrumentation.

Validation: C budget boundary/recovery test passes locally. Real Metal cache and
renderer lifecycle regressions extended for LRU, function identity reuse,
zero-budget bypass, failed retries, repeated warnings and critical purge.
macOS ASan/UBSan/Metal and iOS app compile pending cloud validation.
CPU count/QoS, guest RAM/JIT size, graphics quality, refresh, LPM and thermal
policies unchanged. No IPA requested. Physical warm-up/cooling comparison pending
user early desktop, Roblox loading and settled-game captures on the old release.
