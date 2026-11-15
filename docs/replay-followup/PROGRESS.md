# Post118 replay follow-up

- [x] Analyse all three supplied files; isolate current process and exact binary symbols.
- [x] Extend shared checked bulk mapping to task buffers; avoid duplicate page-table snapshots.
- [x] Implement and validate exact smaller copies; retain full-copy default after measured regressions.
- [x] Implement bounded command snapshot storage with explicit lifetime/pressure ownership.
- [x] Focused ASan/UBSan/TSan, actual Mach/Metal/IOSurface pixels and both SDK compiles pass43749109738.
- [ ] Final frozen-patch full native/app integration checks.
- [ ] Release gate and any subsequent119 IPA packaging.

Next: full workflow on perf/replay-mapping-sync, fix any independent failures, then record exact-source results. No runtime changes to baseline perf/safari-compositing. No IPA during implementation. Partial copy stays opt-in; no new UI switches, resolution reduction, CPU topology changes or refresh cap.

Final review correction: transient UIKit warning recovery now reuses the existing active-work budget deadline. No new timer or controller; a workload with no new shader libraries can recover command-cache admission. Final validation must use the patch containing this correction.

Pooled snapshots now align every individual segment to16 bytes, including odd-length input. Arena sizing includes padding; transient oversized streams retain the independent reference path. Final validation must include this correction.

The new mapper also rejects allocation+first-byte rounding overflow before making a host alias; actual production-method regression asserts no Mach remap occurs for that malformed descriptor. Implementation is now frozen for full validation.

Native comparison after alignment showed tiny-buffer pooling could regress7.27%; admission is now>=4KiB, retaining the existing independent path below that threshold. A boundary-size native comparison and correctness test cover the actual selection.
