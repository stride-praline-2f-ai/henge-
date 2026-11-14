# Final GPU source gate

Validated source `cc2ab5fc4d270273295a4066e03fa3b91259c8dc`, patch `8528f304143f3a95a657e980073b06d7d116d7c9ce3d9409f09327c5f5775053`. Run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43635372451.

All source changes are integrated. Exact binding reuse, GPU-specific bundles, Metal4 SDK compilation and production planning/ordering/lifetime fixtures, memory-pressure recovery, archive epochs and presentation checks passed. Real classic Metal pixels were tested; the cloud GPU cannot execute Metal4 shaders. SP folding, safe interrupted memory groups, immutable literal reuse, large-cache far slots, encoder-scoped Metal4 replay with depth/default-constant mappings, lossless snapshot admission and companion recovery are integrated. One metadata-only child requests the final IPA. Prior engine/input/Link/storage/clipboard/Instant Resume features remain.

Actual Metal4 shader execution and M4/Duo FPS/cooling remain physical validation; the cloud GPU is Paravirtual. See project-review/REVIEW.md for specific adaptations and safe rejections.
