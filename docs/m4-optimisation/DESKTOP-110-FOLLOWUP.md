# Desktop follow-up to diagnostic build110

Baseline evidence:104-minute M4 run; software-TLB/dispatch dominates sampled vCPU work, kernel fallback87.18%, segment eviction23.855s,349touch timeouts and3late pressure notifications.

The table-major TLB is ALREADY the core default. Retain it; benchmark both layouts and the separately opt-in preload path. New bounded two-access grouping retains permission/page guards and plain fallback.

Direct touch: neutralize contacts after missed liveness; preserve an established mapping for at most30s; require neutral input boundary and current epoch on recovery. Explicit guest errors, teardown and pause still disconnect. Initial USB setup is bounded30s; repeated failures back off2/4/8/16/30s(timeout) or5/10/20/30s(device). Guest transport preserves only confirmed direct mappings for transient errors, with the same30s bound. Numeric phase/error diagnostics are negotiated.

Memory: keep one resource policy and its OS-pressure precedence. Log actual budget changes and every UIKit pressure notification, including outside optional UI captures. Excluded pages still consume physical RAM.4CPUs/8GiB remains the explicit comparison baseline; do not silently resize existing12GiB guests or alter Retina.

Validation pending: native/Swift/SDK/app, actual emitter sizes, threshold2vs3 timing, both TLB layouts and MAP_JIT/split-alias memory tests. No IPA until gates pass. Physical M4/Duo latency, cooling and8/12GiB workload comparisons remain device work.
