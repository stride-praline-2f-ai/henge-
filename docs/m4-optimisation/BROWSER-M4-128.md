# M4 browser and guest memory in build 128

## Source provenance

The build 126 IPA identifies its internal source as `e0846e2212ae` and its integration wrapper as `1a23c491a25dc49fdb7dea4864c476461d2a91ca`. The workflow starts at `3956a9fe0a641a77e75b10cb21a0ec8faac1fb69`, applies the primary patch with SHA-256 `096593cd7c172aef84de38696c2491632912e37d1a49a62a06ae52487b28f1d7`, and integrates upstream main `8048e4a91450e1aa40bf8e6972b76c73921e038b` and the pinned PRs. The IPA records audit and follow-up digests. The historical `upstream_update.sha` describes an earlier integration, so the old manifest excerpt alone is insufficient. Build 128 starts from the verified build 127 source, including its non-Retina Link fix, and adds the independently hashed `m4-browser-memory.patch`. [Build 126](https://github.com/stride-praline-2f-ai/henge-/actions/runs/45268592091) · [Build 127](https://github.com/stride-praline-2f-ai/henge-/actions/runs/45273565355)

## Execution path and measured scope

| Sampled word | Decoded AArch64 instruction | TLB field in the indexed scalar template |
| --- | --- | --- |
| `f942c0ef` | `ldr x15, [x7, #0x580]` | Read tag |
| `f942c4ef` | `ldr x15, [x7, #0x588]` | Write tag |
| `f942ccef` | `ldr x15, [x7, #0x598]` | Host address addend |

In `core/translate.c`, `put_tlb_slot` and `translate_mem` emit the indexed scalar lookup. The ordinary EL0, no-writeback, register-base load takes eight instructions through the actual load in the no-preload configuration. The table-major layout can emit the same sampled words after rebasing the pointer to the selected EL1 table. Sampling words alone cannot distinguish which guest process or table used a template, or establish the total cost of all its instructions. These samples show translated code accessing the software TLB. The sample, session-wide eviction counts and reported guest process CPU percentages cannot determine the largest contributor to Speedometer elapsed time.

The tagged-multiwindow Fast Memory cache covers eligible EL1 scalar reads. With the default TLB-first order, it is probed after the ordinary lookup misses. Its hit percentage is conditional on those probes. Safari's EL0 loads still use the software TLB. The segmented JIT ring reclaims nonmoving segments with a quiescent barrier and repairs incoming branches. Its optional heat-based victim selection remains off by default pending physical workload comparison. Approximate retranslation counts should be read alongside the measured translator time, JIT eviction durations and synchronization waits in the same workload window. Build 126 already includes an indexed-branch-retirement fix for a separate stall observed in build 125.

Eligible scalar literal loads now fold their known guest page index into an offset from the CPU pointer. Near entries use the immediate load displacements. Far entries form a base with one ADD. Tags and addends are reread every time and the existing permission, page-tail, refill, remote invalidation and code coherency paths still apply. The ARM64 fixture checks the emitted word counts, live data reads and warm paired latency over seven alternating pairs. This benchmark is a register-and-literal loop, so it cannot estimate the share of Safari instructions using this form. The comparison flag is `HV_TLB_LITERAL_SLOT=1`, default off. It is independent of the optional preload experiment. Native execution still requires software address translation, indirect dispatch and guest exception handling even with the same host ISA.

## RAM admission

The prior policy reduced a request above the device recommendation if it matched a previous pressure event. The 16 GB M4 iPad profile now recommends and requires 12 GiB for cold-booting an installed Mac. If the available mapping or storage cannot support the floor, the app reports that at boot. Saved sessions retain their original layout and the temporary Recovery installer retains its bounded allocation. The VM disk and stored RAM preferences survive. The app still responds when iPadOS reports real system pressure. A 12 GiB guest allocation cannot guarantee the absence of host warnings.

## Reproduce

On the ARM64 macOS runner, in the effective Henge source tree:

```sh
python3 tests/test_desktop_configuration.py
make -j4 build/test_literal_tlb build/test_mem build/test_tail_recheck
build/test_literal_tlb
HV_TLBT=0 HV_JIT_SPLIT=1 build/test_literal_tlb
HV_TLB_LITERAL_SLOT=1 HV_FASTMEM=1 build/test_mem
HV_TLB_LITERAL_SLOT=1 HV_TLBT=0 HV_JIT_SPLIT=1 build/test_mem
HV_TLB_LITERAL_SLOT=1 build/test_tail_recheck
HV_TLB_LITERAL_SLOT=1 HV_TLBT=0 HV_JIT_SPLIT=1 build/test_tail_recheck
```

The release workflow uploads `Henge.ipa`, the verification JSON and the native validation logs for the same source. On iPad, use the same macOS 27.2 and Safari builds, 4 vCPUs, a 12 GiB cold boot, 1,536 MiB JIT, 60 Hz and maximum Retina for both settings. Confirm the allocated RAM and flag in the launch log. Disable Session diagnostics and remove the active GPU trace marker for timing. Alternate reference and optimized configurations, allow boot work to settle, and record at least three Speedometer 3.1 trials per configuration, including spread and thermal category. Use a separate diagnostic capture covering the benchmark to calculate deltas for JIT compile time, segment eviction and TLBI waits. The roughly 40-point comparison lacks a confirmed device, OS and benchmark setup. The reported 5.75–6.00 scores alone cannot establish a native speed ratio.
