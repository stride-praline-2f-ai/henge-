# Instant Resume and responsiveness — integrated source

Source `5701f45fcd7db0cdd19557b5a0f81924bead210c`, patch `a690fc757ab4d5638742a9aa442b92bac0a6ae605e552c5f05fe4d00b102a641`. Native, sanitizers and complete
iOS Release compile: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532298. Parallel coordinator/UI checks: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43176532244.

Implemented and cloud-validated: generation/intent/view ownership, immediate
cooperative save cancellation, worker draining, exact-once background assertions,
coalesced autosaves, foreground Save Mac & Leave, save progress, asynchronous
boot/restore and nonblocking firmware/lifecycle observations. Saved sessions
restore actual CPU/RAM/display/Retina/Hz independently of next-boot preferences.
Failed restores preserve the recovery file; interrupted consumption is recoverable.
Link reconnects only a matching saved monitor mode. Guest shutdown and failure
paths leave actionable states. CPU acknowledgements already published no longer
cause unnecessary park/wake publication; own invalidations remain serviced.

Enable Instant Resume in Settings. Return quickly for in-memory continuation;
returning cancels an unfinished autosave. To finish a persistent save reliably,
use three-finger controls → Save Mac & Leave and keep Henge visible until done.
If saving fails, Continue Mac or retry. Turning autosave off still allows an
existing compatible saved session to resume.

Older human-readable snapshot identities lack the complete display configuration
and are rejected clearly, with both snapshots and guest disks retained. Native
schema/layout/checksum/ROM/disk checks remain mandatory. Incompatible saves can
be explicitly discarded without deleting the Mac disk.

No physical-device startup/FPS/watts improvement is claimed. OS Low Power Mode
can still limit CPU clocks. iOS may deny/expire background time or terminate the
app; unfinished saves cannot survive termination. Real macOS application and
peripheral recovery, grants and sustained M4/Duo comparisons need device checks.
