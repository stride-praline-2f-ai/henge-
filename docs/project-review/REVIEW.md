# 0.3.8 project review — 13 November 2026

Review branch: `review/project-038`. Baseline delivered wrapper: `8f615e63`;
local reconstructed source: `8e54052`. No IPA requested or generated in this review.
The pinned Henge/Husk dependencies and previous custom integrations are retained.

## Findings corrected

- GPU cache and guest-RAM opt-out flags treated `=0` as enabled. A shared boolean
  parser preserves legacy empty flags while respecting explicit false values.
- Touch USB reports queued every movement. Coalesce only pending motion after
  contact membership is established; preserve initial hit positions, all down/lift/
  ID edges and genuine transition-overflow recovery. The guest-facing test sends
  1,000 movements through the real xHCI path, with and without pending transitions.
- Physical pointers shared one held-button set. Device ownership now prevents
  a second mouse/trackpad or disconnect from releasing another device's drag.
- Process headroom was labelled a memory limit and confused with guest RAM.
  A nonblocking native API reports the actual successful allocation mode and bytes.
  Settings distinguish launch/current-open process headroom, kernel-excluded RAM,
  file backing and anonymous fallback. The earlier Duo log explicitly confirmed
  8 GiB outside the footprint alongside roughly 6 GiB process headroom. That old
  result does not establish the mode of a different installed binary/current run. The ByteText file formatter uses decimal GB:16GiB is
  approximately17.18GB; these labels are not a physical RAM measurement.
- Optional file-RAM prefault allocation lacked a NULL check and teardown cancellation.
  It now checks allocation, stops on teardown and, on iOS, stops eager I/O below
  256 MiB process headroom. Untouched pages remain valid demand-backed RAM.
- CLI deferred network link callbacks used unguarded global board pointers. A serial
  event queue fences callbacks and generation tokens reject obsolete work. Pause
  restores a link lowered by that operation before snapshot capture. Native lifecycle
  tests apply current/stale events deterministically, without timer sleeps.
- GPU task walkers masked out-of-range address bits into low mappings. Scalar,
  read and batched paths now reject addresses outside the page-table depth. Shader
  source pages are validated before allocation and checked again on copy.
- The display-layout test was not part of routine host checks and relied on an
  implicit CoreGraphics import. Both layout and physical-button tests now run in CI.

## Architecture / interaction coverage

| Area | Review and retained authority |
| --- | --- |
| Integration/build | Manifest/patch digest, reconstruction/reconciliation, source inclusion, two IPA workflow gates/concurrency, metadata/entitlements; review validation cannot package. |
| JIT/MMU/cache | Existing TLB-first read cache, permission/PAN/ASID invalidation, restricted register groups, chain publication and segment eviction retained. No unvalidated cache-size or superblock default changes. |
| CPU/idle/power | Runtime M4/Duo detection, QoS roles, vCPU topology fixed per boot, one idle ticker and timer filtering, notification-based power/display policy retained. No physical core pinning claims. |
| Memory | Actual allocation/fallback tracing, bounded M4 library budget, dynamic process headroom, pressure trimming and prefault lifetime reviewed; launch allowance is not physical free RAM. |
| Graphics/display | Worker-confined replay/cache ownership, GPU quiescence and private-texture copy-back, two display ports, damage-driven presentation, cursor/Retina layout, system display scheduling retained. |
| Input | USB touch encoder/epoch/queue, Pencil tip contacts, direct/physical handoff, per-source keyboard/buttons, pointer-lock scene scoping and physical-device ownership reviewed. |
| Snapshot/lifecycle | Serialized bridge/coordinator transitions, cancellation, disk and GPU quiescence, schema/build/disk validation, atomic save publication and bounded background assertion retained. |
| Disk/network/audio | Raw/GPT/APFS expansion and backup guards, worker completion, NAT/DNS lifecycle, deferred network events, generation-scoped audio recovery reviewed. |
| Clipboard/Link | Complete-body ACK delivery/retry, Universal Clipboard platform integration, source input release, visibility epochs, three-frame decode credit and reconnect lifetime reviewed. |
| UI/config | Opening dashboard, settings activation and migrations, explicit environment override precedence, device-specific fitted Retina and saved display/CPU preferences retained. |
| MacApps/packaging | Separate user-mode translation path retained; its loader changes are not assumed to accelerate the full macOS VM. Runner mode remains removed; pairing helper and signing requirements retained. |

## Validation

Local: flag parser and direct host touch ASan/UBSan, clipboard concurrent delivery,
production disk/GPT/APFS expansion tests and cumulative patch application passed.
Cloud: final source `12db2dae87bde63df81f559a6185a51afdf25019`, run
`43444580204`, SUCCESS: native/ASan/UBSan/targeted TSan, complete Swift/native/Metal
SDK checks and full iOS application compile/link. IPA packaging was skipped.
The corrected test expectation and exact-source evidence are recorded in VALIDATION.md.

## Limits

This is a code/integration review, not proof of every possible guest workload or
physical-device behavior. Cloud macOS runners do not emulate M4/A20 thermals,
iPad touch/Pencil, ProMotion panel behavior or iOS memory accounting. Actual new
RAM mode is shown by the added status API after installing a future build; a 6 GiB
headroom value alone neither proves nor disproves footprint exclusion. File-backed
or excluded pages still consume physical memory; neither is unlimited RAM.
No new physical FPS, energy, startup-time or cooling result is claimed.

## Desktop diagnostic follow-up (0.3.9 / 110, validation pending)

Latest M4 run: 4 vCPUs, 12 GiB guest RAM, 2560×1920 Retina/60Hz;
normal thermal state and substantial process headroom. These logs do not prove
that memory pressure or overheating explains the lag. JIT segment eviction and
branch repair remain substantial; host presentation has long gaps.

- Large quiescent exit-repair batches now publish each modified RX cache line
  once with bounded bitmap scratch and the original barriers/fallback. Tests
  execute modified code through MAP_JIT and split aliases. No MMU shortcuts.
- Direct input preserves the initial contact location, rotates contact IDs,
  drains eligible reports together and ignores incidental trackpad motion during
  a stroke. Explicit clicks/scroll still transfer ownership. Replaced views cannot
  cancel the current surface. Finger/Pencil tip contacts share the USB path.
- Negotiated setup progress refreshes the helper watchdog without falsely declaring
  readiness. Each phase is bounded, with a 30s overall ceiling and legacy fallback.
- This diagnostic build enables Session Diagnostics once on first launch. It runs
  throughout the visible session, can be disabled in Settings, and uses the existing
  maintenance waiter. Logs include native phase timings, disk queue/service/flush
  totals, JIT publication work, presentation timing, input stages and 50Hz sampled
  hot host/JIT code. Top instruction words are included in ordinary logs even
  when the separate bounded word file is full. Instrumentation adds overhead.

Physical touch, Pencil, FPS and thermal gains still require device verification.
No claim that logging alone identifies every possible bottleneck with certainty.

## Final integrated cloud gate

Current source `ed4693c827c671efbf124b68c9d0161fe73ff778`, patch `20225ad181270cb36ff6b6e5b5fc860e046006eb863248db1525541da1cff8b7` passed https://github.com/stride-praline-2f-ai/henge-/actions/runs/43461735695, plus engine run `43461735627`. Includes the eight original review corrections and the desktop diagnostic/touch/JIT follow-up. This supersedes earlier pending-validation statements above. Final IPA inspection remains pending; physical performance is unmeasured.
