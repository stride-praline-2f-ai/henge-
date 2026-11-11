# M4 integration contract

Target: iPad16,5, 10 host cores (4P/6E), observed high-memory configuration.
Runtime capabilities and `os_proc_available_memory()` govern host resources;
physical 16GB is never an application memory entitlement.

Keep baseline 4 guest CPUs / 8GB guest RAM / existing 1–1.5GB JIT choice.
Provide 2/4/6/8 CPU and 6/8/10/12GB comparisons without inventing winners.
Preserve full Retina, user-selected 60/120Hz, input, audio, network, Link,
snapshot lifecycle, guest timing and all architectural memory permissions.

Implement against the reconstructed pinned patch tree; update cumulative
audit patch and SHA-256 manifest together. Work only on
`feature/m4-ultra-efficiency`. No interim IPA; full integration gate before one
final artifact. Keep self-hosted workflow selection compatible; do not claim
an available Mac runner without observing it.

Workstreams: profile/CPU; TLB/JIT; memory; Metal/resource ownership; demand-driven
ProMotion; idle/device work; sustained gaming; input/external display; thermal
maintenance; optional diagnostics; defaults/integration; correctness/release.
