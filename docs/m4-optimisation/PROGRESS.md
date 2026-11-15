# Physical116 CPU, shader and network checkpoint

Authoritative tested source: `55d472b7a8ecfe87f1cc7288f7ae8964e193fd86`, branch `feature/metal4-pipeline-efficiency`, runtime commit `67cd3e9`, patch `ed92adf94c7ff4c161b3a64b054fd708c0bdaa347eee055bb7fe05b7fcada289`. Native/app run43673650998 and focused GPU run43673650970 passed. IPA generation was explicitly disabled. No push to main.

Implemented: checked stack writeback translation reuse; bounded utility Metal4 pipeline warmup; nonblocking pressure admission and bundled display archive lookup; sparse argument reset; exact compute219 no-op parity; rejection hotspot counts; previous-session log sharing; attributed PR176 network batching. Native, old-emitter and exact-fault comparisons passed. Full app compiles. Preserve Retina and chosen refresh settings.

See VALIDATION.md, PHYSICAL-116-COMPARISON.md, PERFORMANCE-RESEARCH-116.md, CPU-STACK-REUSE.md, SHADER-WARMUP.md and NETWORK-RX-BATCHING.md. Real M4/A20 FPS, latency and energy improvements remain unmeasured. iPad crash cannot be attributed from supplied startup-only current files and short prior tail. Do not restart historical log discovery.

Upstream preparation reference: e98920c + custom integration6043e87; focused engine candidate7f17934, network candidatece865b9. Stride is the selected owner. `stride-praline-2f-ai/Henge` still404; connector cannot create forks and CLI identity is aaULTra. Do not fork under the wrong owner or open duplicate third-party PRs. Engine overlaps PR186 and must be attributed/de-duplicated before publication; network adapts oliverames PR176. Other feature groups still need extraction/validation; the all-PR request is not complete.

Next: retain this exact source parent while preparing remaining upstream contributions and final requirements reconciliation. If runtime changes, regenerate the cumulative patch/receipts and run relevant checks; do not reuse this source receipt for a changed patch. Only enable IPA after the complete release gate. These documentation receipts live on a review branch so they do not invalidate the frozen source-parent rule.
