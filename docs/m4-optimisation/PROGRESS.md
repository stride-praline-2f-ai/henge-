# Physical114 interruption and Safari follow-up

Runtime checkpoint25ef1f0; source validation pending. New supplied logs fully analysed in PHYSICAL-114-INTERRUPTION-SAFARI.md. No proven iPadOS reset cause; both runs configured16GiB RAM and issued system pressure warnings. Previous end restored at60Hz; later cold boot120Hz.

Implemented off-main bounded diagnostic sampling/report coalescing, separate Metal4 GPU/allocation accounting, contact-aware idle touch watchdog and physical-RAM clarity. Local native touch ASan/UBSan passed. New production Swift worker/stale completion tests are in both focused GPU and full host checks. Full native/app CI next; release_requested=false. Do not package or reuse115 validation as proof of the new source.

Next: inspect focused worker test and full native/app results, fix actual failures, record exact-source cloud evidence. Larger code-cache pool/unbounded GPU jobs and unsafe TLB shortcuts are not justified by these logs. Keep current MetalFX and all earlier input/snapshot improvements.
