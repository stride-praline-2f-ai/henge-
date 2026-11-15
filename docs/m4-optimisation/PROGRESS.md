# Physical114 interruption and Safari follow-up

Runtime checkpoint25ef1f0; source validation pending. New supplied logs fully analysed in PHYSICAL-114-INTERRUPTION-SAFARI.md. No proven iPadOS reset cause; both runs configured16GiB RAM and issued system pressure warnings. Previous end restored at60Hz; later cold boot120Hz.

Implemented off-main bounded diagnostic sampling/report coalescing, separate Metal4 GPU/allocation accounting, contact-aware idle touch watchdog and physical-RAM clarity. Local native touch ASan/UBSan passed. New production Swift worker/stale completion tests are in both focused GPU and full host checks. Full native/app CI next; release_requested=false. Do not package or reuse115 validation as proof of the new source.

Next: inspect focused worker test and full native/app results, fix actual failures, record exact-source cloud evidence. Larger code-cache pool/unbounded GPU jobs and unsafe TLB shortcuts are not justified by these logs. Keep current MetalFX and all earlier input/snapshot improvements.

Latest physical115 MetalFX logs fully analysed: real1280x960 ->2560x1920 effect active;16GiB guest,3warnings,3433pressure-associated fallbacks,4.219median process CPU cores. Normal cold-boot/save lifecycle. Added transition-only FX admission/trim and split fallback attribution with regression coverage. Runtime1c337dd; patch8361270. Prior65deb worker ASan tests and both SDK typechecks passed; final combined source requires repeated exact-source gates. IPA remains off.

User extended pressure request: moderate warnings now cap FX at two leases rather than disabling it, critical/low-headroom fallback retained. Raw HOST_VM_INFO64 accounting and mixed-lifecycle process-memory capture added. Prior source79fc181 fully passed native/app + focused validation; this extension requires fresh exact-source checks. No IPA requested. See PRESSURE-AND-FX.md.
