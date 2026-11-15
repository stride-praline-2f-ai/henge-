# Engine implementation: completed and packaged

Henge0.3.16(117), release commit `c7a115cfa93f8650a8e61144a19280096b82d5f1`.
Runtime milestone `ebeaad535d05120a1df4b03f4f3ea6192bdefc9f`; pinned patch and
manifest delivery retained. No unmodified upstream replacement.

- [x] Broader checked reuse across interleaved independent bases, ordinary
  loads/stores and existing stack/writeback groups. Bounded slots/ranges,
  pruning across unselected accesses and complete overlapping fallback spans.
- [x] Lookup latency work: normal IJC table load overlaps hash arithmetic;
  guarded scalar/group addend preload and paired-entry trials implemented.
- [x] Selective IJC eviction preserves unaffected targets and salts using
  owner-written per-segment indexes; overwritten bits are pruned. Stale targets
  outside the victim are removed exactly. Allocation/shape failure safely
  resets; return/descriptor caches retain necessary clears.
- [x] Nonmoving recent-use retention: real lookup hits and decimated helpers
  feed aged segment heat under the original global barrier. No new timer or
  moving live code. Unordered host-PC lookup uses sparse page heads; HvBlock
  remains80bytes and allocation failure retains the diagnostic linear path.
- [x] Targeted branch-site hints: bounded cold-path history admits sites on
  retranslation. Hints reference the authoritative per-CPU, flag-specific IJC
  and always check current target tag/ASID salt. No independent trusted target
  cache, weaker invalidation or guest ordering shortcut.
- [x] Native/reference differential memory, precise load/store fault order,
  exhausted slots, ASID/TLBI/SMC/reset, real two-way collisions, all guest SIMD
  registers, dual aliases, poisoned four-vCPU eviction and low-memory fallbacks.
- [x] ASan/UBSan new engine + VM/PVG/JIT/memory and TSan concurrency checks;
  full input/Link/USB/APFS/Swift/Metal regressions and Release-iphoneos app build.
- [x] Final archive architecture, nested signatures, entitlements, source SHA,
  original capabilities and new engine markers inspected. Drive readback SHA
  matches the exact verified IPA.

Defaults: wider checked reuse, normal lookup scheduling and selective IJC
preservation execute in Automatic. Existing Retina/refresh/CPU topology remain.
Preload, paired IJC and site hints stay opt-in because timings did not establish
an overall win; site hints penalised changing targets. Recent-use retention
saved256 translations/one eviction in the helper-heavy fixture, but elapsed
trials were slower, so FIFO remains the default without activity sampling.
Developer controls: `HV_TLB_PRELOAD=1`, `HV_IJC_PAIR=1`,
`HV_BRANCH_SITE_HINTS=1`, `HV_JIT_RETAIN_REFERENCE=0` (opt-in recent-use trial).

Concrete trade-off: one interleaved emitter fixture reduces inline62->44 words
but grows total208->246 due to bounded fallback code. The default8-segment
index reserves4MiB virtual metadata per active CPU with demand-touched pages;
it does not enlarge the JIT executable reservation. No universal speedup claim.

Final five-round six-load median:3.300->2.218ns (32.8% less time) on Apple M1
(Virtual), Xcode27.2. This is a focused CPU pattern, not M4/Duo FPS, startup,
thermals or energy. Those require controlled physical-device comparisons.
A real pre-existing signed BRK-syndrome shift found by UBSan is fixed using
unsigned architectural EC constants. No failing tests were disabled.

Full117 validation: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43719589751
Final IPA verification: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43720699793
Artifact: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43720699793/artifacts/14164727662
Drive: https://drive.google.com/file/d/1qEIw8-XVb9isbwdNA4_2Xy-_rLseTaqU/view?usp=drivesdk

SHA256:`b095704c5793751600e6b8d72204bcbe9a53b835beeadf59a0234edd6a397c9c`.
Ad hoc archive: install with the user's supported signing/profile method.
Implementation/release complete; next work is physical comparison, not an
unfinished source workstream. Prior GPU-budget ABI rejection and iOS background
restrictions remain documented in their existing reports.
