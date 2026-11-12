# Responsiveness and reliable Instant Resume

Baseline: released0.3.3(104), source704ba172, wrapperhead856f901. User reports
Low Power desktop loading remains slow; previous host fixtures did not prove a
device startup improvement. Automatic scheduling already preserves all4vCPU
priorities. Do not bypass OS clocks, add universal boosts or claim cooling gains.

Found: foreground returns wait behind uncancellable whole-memory saves; stale
queued lifecycle requests lack generation ownership; expiration ends background
time without cancelling work; failed native restore deletes recovery files;
mutable CPU preferences can mislabel saved state; sync-ready waits publish
unnecessary park/wake events.

In progress: cooperative per-save cancellation/progress, generation-safe native
transitions and consume-on-success restore; deterministic native regressions;
already-acknowledged sync fast path retaining own invalidations.
Next: production Swift coordinator with stale-intent cancellation, exact-once
background assertions, explicit foreground save-and-leave/recovery/progress,
self-describing saved configuration; focused Swift/native tests, then cloud
integration. No IPA or release request until the whole feature gate passes.

Hardware: OS Low Power Mode can reduce CPU performance and display refresh.
Software changes cannot guarantee normal-mode speed under that OS policy.
