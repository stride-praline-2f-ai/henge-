# Post118 replay follow-up

- [x] Analyse all three supplied files; isolate current process and exact binary symbols.
- [x] Extend shared checked bulk mapping to task buffers; avoid duplicate page-table snapshots.
- [x] Implement and validate exact smaller copies; retain full-copy default after measured regressions.
- [x] Implement bounded command snapshot storage with explicit lifetime/pressure ownership.
- [x] Focused ASan/UBSan/TSan, actual Mach/Metal/IOSurface pixels and both SDK compiles pass43749109738.
- [ ] Final frozen-patch full native/app integration checks.
- [ ] Release gate and any subsequent119 IPA packaging.

Next: full workflow on perf/replay-mapping-sync, fix any independent failures, then record exact-source results. No runtime changes to baseline perf/safari-compositing. No IPA during implementation. Partial copy stays opt-in; no new UI switches, resolution reduction, CPU topology changes or refresh cap.
