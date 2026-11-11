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
