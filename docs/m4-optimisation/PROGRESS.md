# GPU integration checkpoint

0.3.11(112), branch `feature/metal4-pipeline-efficiency`, cumulative patch `5e46339e9a21d13bed8b445750064b5da194977857b8c7974d2017e4c0f8dd8d`.

NX18-derived binding reuse, real Metal4 guest/display paths, exact offline bundles, queue/resource/fence safety, pressure-aware residency, nonblocking persistent cache epochs, bounded presentation and backend diagnostics are implemented. Focused tests passed. Full native/sanitizer/Swift/Metal/iOS app validation is running; release is not yet requested.

Keep existing JIT/MMU, input/Pencil, controls, Link, clipboard, storage and Instant Resume features. Physical Metal4 execution is blocked by the cloud runner's Paravirtual GPU; do not claim device FPS or visual validation.
