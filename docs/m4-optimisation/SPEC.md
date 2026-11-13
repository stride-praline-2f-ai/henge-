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

Implementation decisions retained from actual resource ownership:
- Keep native buffer-backed scanout; guest CPU writes can change it outside GPU
  epochs. Do not suppress authoritative swaps by surface identity or hash the
  whole Retina framebuffer on the CPU. Damage pulses coalesce to the latest one.
- Borrowed guest memory and CAMetalDrawable ownership do not become reusable
  heap allocations. Copying into a heap would undo zero-copy; persistent screen
  textures cannot use memoryless storage. Preserve exact existing surface reuse.
- Guest serialized Metal pipelines and barriers remain authoritative. Adding
  argument buffers or merging passes without transforming that guest protocol
  would change shader bindings/order, not provide a safe M4-family shortcut.
- Live executable aliases cannot be recreated after debugger detachment. Reclaim
  retired metadata after quiescence, not live translations or RX mappings.
- No supported API pins vCPUs to P/E cores or sets CPU frequency. Low Power Mode
  evidence does not justify demoting arbitrary guest CPUs and delaying TLBI acks.
- Physical comparisons keep workload, Retina/refresh, brightness and diagnostics
  equal. Test CPU, RAM and JIT settings separately; record task time/frame times,
  headroom and thermal category over sustained runs. No optimum is invented.


## Integrated controls/power follow-up
Shared M4 and Duo changes: demand-driven presentation; notification-cached Low Power Mode policy with an user-selectable next-cold-boot60Hz guest option enabled when OS LPM is active, per the latest user preference; bounded 30s capture using existing session waits; native USB HID gamepad and separately labelled keyboard mapping; authenticated controls-only Link reusing pairing/transport/input gestures. No video codecs in controls-only mode.
Runner: optional experimental CPU-only continued processing, foreground pause/GPU drain, guest-owned ring backpressure, no fabricated completions, foreground replay, persistent-save rejection until graphics restored. Explicit iOS grant required; no PiP keepalive claim. Graphics/Simulator jobs and real guest driver timeout behaviour need device tests. Preserve GPU-granted mode as separate request identity.

Loading follow-up0.3.7: TLB-first secondary LUT, adjacent disk segment coalescing, warning-safe shader persistence, app Runner removal/settings migration. In development; native/SDK/UI validation pending and IPA gate closed. Details: runtime docs/m4-optimisation/LOADING-0.3.7.md.
