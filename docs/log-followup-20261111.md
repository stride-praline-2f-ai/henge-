# Device log follow-up (2026-11-11)

The three A4AF8415 attachments describe custom build 2839d40, not the later
ef56e3a release. Initial Hot state occurred about 84 seconds after VM startup,
before the user's later Roblox session. A long cooling pause lasted roughly
259–270 seconds; Warm was observed on return, followed by Hot about 87 seconds
later. App suspension can delay observation of thermal transitions. The exact
game start is not recorded. No Roblox FPS benchmark or energy comparison follows
from these observations.

Short uninterrupted foreground samples averaged about 336% process CPU. There
were nine capacity JIT resets and about 714 MiB of remaining process headroom
at the last footprint sample. Six in-memory pauses and five continues, with no
crash shown, do not verify persistent snapshot restoration. Fastmem was enabled
but counters were off. The instruction profile is byte-identical to an older
upload and cannot rank this session's hot functions.

## Confirmed defects repaired

* The native bridge now offers one lock-protected observation containing state,
  machine generation, run epoch and counters. Pause/Continue advances the epoch;
  the machine generation retains its original meaning for Link and lifecycle
  clients. Paused counters stay readable and final counters survive destruction.
* Swift counter sampling treats lifecycle changes, decreased counters and invalid
  timestamps as new baselines. It cannot wrap a temporary zero into a false
  2^64-frame interval or count the full cumulative total after Continue.
* Frame logs state the actual interval and rate, label session elapsed time as
  wall time (including pauses), and identify DNS answered/fallback/timed-out
  fields correctly. Paused sessions skip periodic performance/preview work.
* Native statistics use thread-local baselines reset for each hv_run. Both a
  recreated CPU0 thread and reuse of the same host thread start with fresh
  cumulative, wall-clock and thread-CPU-time observations.
* The full block-hash scan, previously traversing millions of entries on CPU0
  during ordinary statistics, now requires HV_STATS_HASH=1. Routine rate counters
  and default reporting remain available. This eliminates that diagnostic walk;
  its device power/latency effect has not been measured.
* An earlier session with HV_PROF_IOS=0 no longer permanently consumes profiler
  initialization. Actual initialization is serialized and logged with process
  and timestamp. Profiling remains opt-in and perturbs timing.
* Existing GPU report intervals now include device allocation size and constant
  time collection counts. These include in-flight work and are not a process
  footprint, unique allocation sum, or proof of a leak.

## Validation and delivery boundary

Both IPA workflows default to validation only, including on push. Packaging and
dependency compilation after regression testing require a manual dispatch with
the boolean build_ipa input explicitly true. Shared concurrency and latest-head
checks are retained. No IPA is requested by this follow-up.

Regression coverage includes real native VM pause/Continue/reboot and retained
counter totals, recreated CPU0 timing with deep scans off/on, Swift frame and
block sampling across observed and unobserved pauses, invalid clock readings,
counter resets, and profiler off-then-on initialization. The existing lifecycle,
Metal, input, networking and sanitizer checks remain mandatory.

Heat, memory ownership, cache pressure and optimal CPU count are still open.
This patch does not raise JIT size, trim live graphics resources, alter virtual
CPU count, change QoS, or reduce Retina, resolution or refresh settings. Those
choices need reproducible evidence from the latest source before alteration.
