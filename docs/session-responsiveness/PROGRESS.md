# Responsiveness and reliable Instant Resume

Baseline: released0.3.3(104), source704ba172. Low Power loading remains slow on
user hardware. Automatic scheduling already keeps4 responsive vCPUs. No OS clock
bypass, extra CPU boost, reduced Retina resolution or invented thermal result.

Implemented: one production generation-owned transition coordinator; immediate
per-save cancellation with drained compression workers; exact-once background
assertion expiry; coalesced saves; progress from existing foreground wakeups;
foreground Save Mac & Leave; asynchronous boot/restore; immutable actual saved
CPU/RAM/display/Retina/Hz configuration; retryable in-memory pause and errors;
failed restoration preserves complete snapshots; interrupted consumption uses a
recoverable .using file; stopped/stale views cannot control a replacement Mac.
Link reconnects only a saved compatible monitor mode, with no topology changes.
UI observations and pressure notifications no longer wait on lifecycle writers.
CPU sync skips false park/wake publication for already acknowledged requests,
while still servicing own pending invalidations.

Validation: native checkpointa2afdba passed full native/sanitizer/iOS build in
run43168784106. Complete Swift integration and additional lifecycle/Link tests
are under validation; not release-ready. No IPA until the final source gate.

Compatibility: earlier human-readable snapshot identities lack saved Hz/mm and
cannot safely reconstruct the exact session independent of changed preferences.
They are clearly rejected and retained for rollback; disk data is never deleted.
Native snapshots also enforce schema/layout fingerprint, ROM/disk identity and
checksums. New self-describing identities use the existing bounded header.

Limits: UIKit may deny/expire background time or terminate Henge. An unfinished
save cannot survive termination; use foreground Save Mac & Leave for completion.
Device startup speed, OS grants, thermal/FPS behaviour and real guest peripherals
still require physical comparison. No claim of unlimited background execution.
