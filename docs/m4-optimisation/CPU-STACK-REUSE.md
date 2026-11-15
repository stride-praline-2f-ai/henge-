# Checked stack translation reuse

Physical116 profiles put roughly a quarter of JIT instruction samples in three software-TLB loads. A fast kernel-cache lookup after a regular TLB miss does not eliminate these generated instructions. Grouped access already checks permissions and a complete same-page range. Mode2 previously lost that reuse around pre/post-indexed function stack frames.

The planner now keeps a bounded (16 guest instructions, 256 bytes) candidate across matching-base writeback. Three or more accesses use the existing cached-addend path; fixed-base groups keep their cheaper register path. Page, store permission, PAN, ASID, MMIO, scratch clobber, barriers and original-instruction fallback remain authoritative. No extra cache or settings switch is added. HV_GROUPS=0 remains the plain reference, and compile-time HV_GROUP_WRITEBACK=0 reconstructs the previous mode2 policy for testing.

Cloud source check [43672136703](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43672136703) passed native comparison for20 programs in4 execution modes, explicit groups0/2 and the old-policy build,128 MMU checks, JIT/inline/tail/ring tests. Independent stack resets detect missing stores; native capture scratch is excluded.

The synthetic six-memory-operation stack loop emits30 inline words instead of43 (30.2% smaller hot code). Six alternating paired runs all favoured the new policy: 1.856–2.013 vs1.992–2.111 ns/frame. Each timed loop is short and cloud scheduling is uncontrolled; this is supporting microbenchmark evidence, not a physical M4/A20, app-load, FPS or energy result.

Additional exact-fault coverage verifies completed loads/stores, the first failing PC/address, one exception and no faulting pre-index writeback against the previous emitter. The exact-fault extension passed in upstream-source check [43672638299](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43672638299). The final combined app build remains pending.

Metal compatibility diagnostics also retain32 exact reason/type/tag buckets and report the top3 at existing checkpoints, including payload size range and overflow. This replaces inference from the last rejected opcode. Counters neither change command admission nor suppress classic GPU replay; no new timer or resource-content logging.
