# Validation

Passed locally: production scheduling policy/detection regression compiled with
GCC, AddressSanitizer and UndefinedBehaviorSanitizer; concurrent metadata reads,
M4 high-memory/low-memory/simulator/fallback selection and existing Duo policy.
This Linux result does not validate Apple QoS or physical core placement.
Resource-budget production policy also passed ASan/UBSan for dynamic headroom,
pressure precedence, exact thresholds and recovery.

Pending: ARM64 `test_mmu` coalesced read-span/PAN/remap boundaries, all native
lifecycle/snapshot regressions, native Metal detached-presentation regression,
Swift/profile/default tests and complete iPhoneOS app compilation.

Cloud infrastructure inherited five queued validation runs with no assigned
jobs; Actions cancellation and self-hosted inventory API calls returned 403.
Both original workflows retain shared cancellation. Do not claim a runnable
self-hosted Mac or launch packaging while unavailable.

Physical M4 comparisons: fixed workload, same Retina/refresh; compare 2/4/6/8
vCPUs and 6/8/10/12GB guest RAM separately, then 1GB/1.5GB JIT. Record sustained
task time, frame-time behaviour, process footprint/headroom and thermal category.
No whole-app speed, temperature, energy, battery or gaming gain is yet measured.

Update: cloud 43104343753 assigned a GitHub-hosted ARM64 Xcode27 runner.
JIT/MMU/superblocks, lifecycle/snapshots, concurrency/Metal diagnostics and actual
Swift/iPhoneOS typecheck passed. Failure was benchmark fixture patch drift,
now repaired; full app compilation remains pending. Existing self-hosted runner
mode remains supported but its availability is not established.
Local clipboard ASan/UBSan regression passed 4000 concurrent publications.
Display-pulse controlled-queue regression and explicit iPhoneOS Metal syntax
check are new and pending; do not infer a green M4 release from prior checks.

Green checkpoint: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43106141682
Source 6edf085a07b5df5164e5e35687f87087b82fe535, cumulative patch
6221e972bbd2dc01ec224fac70240830513c400e6db63a84f712366bd9381f35.
Native JIT/MMU, memory helpers, lifecycle/snapshots, display-pulse queue fixture,
clipboard concurrency, Metal/resource tests, Link/input/native checks, sanitizers,
actual iPhoneOS presenter syntax, production Swift typecheck and complete Release
app compile all passed. Packaging was skipped as required.
The newer event-driven session/boot-display waits, explicit M4 preset, optional
input ownership and repeated glyph reuse need the next exact-source checkpoint.

Checkpoint43108150736, sourcea57898b084e54f10527793a237985d41858c3549:
all native/sanitizer checks, new wait and M4 preset tests,64-source production
Swift SDK typecheck and complete iPhoneOS app compile passed. No IPA packaged.
The final restore-archive error-propagation change is newer and needs validation;
local production-block success/failure regression passed.
