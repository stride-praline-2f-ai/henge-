# Network receive batching

Adapted only the receive batching from [oliverames PR176](https://github.com/Leviidev/Henge/pull/176). The single existing slirp worker and CPU0 consumer remain authoritative. CPU0 snapshots up to32 queued frames per lock acquisition, publishes each real virtqueue completion and signals once for the batch. Only the consumed prefix is removed/freed. A short guest buffer is returned and counted as dropped; an absent buffer preserves the frame and all later frames for retry.

No frame is delayed to fill a batch. No timer, extra worker, socket-buffer expansion, new cache or UI setting is added. The compiler flags and display pacing remain unchanged. Retaining a bounded prefix under the existing queue mutex prevents the producer from recycling its owned slots before consumption. CPUs remain stopped before detach and queue destruction.

The real queue/device regression passed ASan/UBSan on Linux and macOS: 32 frames make1 interrupt API call versus32 single calls, with exact payloads and headers, partial completion, short buffers, suffix retry, empty queues and65536-index wrap. Existing level interrupts may already coalesce guest interrupts: the test measures fewer host API calls, not a32x reduction in actual guest IRQs or a measured network speedup.

Upstream-source cloud [43673171842](https://github.com/stride-praline-2f-ai/henge-/actions/runs/43673171842) also compiled the actual slirp consumer and passed141 device checks. Full custom VM lifecycle, iOS compile and final integration passed in43673650998.
