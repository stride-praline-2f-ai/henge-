# Screen Off and the JIT/MMU changes

In the Mac session, open Details and choose **Display → Turn Off Local Screen**. Tap the black screen, move a mouse, or click to wake it. **Black Screen During Link Video** waits for the viewer to consume a frame. A local wake keeps the host visible until the stream ends. An external monitor keeps its own presentation. The app remains in the foreground in this mode, which lets the guest run and Link keep encoding while the host drawable is detached. Pure black turns OLED pixels off. LCD backlight behavior is controlled by the device.

The MMU now shares a single checked RAM backing between the normal TLB and the kernel read cache. Instruction fetch passes its resolved backing to the dispatcher when it can preserve the address lookup priority. Overlapping regions keep the original lookup order. New translations enter the publishing vCPU's local cache immediately. Writable TLB stash restoration now retains the validated code flag address until the post-fence check. The write hint, full fence and live code protection check all still run.

The launcher starts one host worker per configured, guest-online vCPU. The guest scheduler assigns its runnable threads to those vCPUs. The Details label now says **Online guest CPUs** to distinguish the configured topology from utilization. Use the per-vCPU diagnostic samples to assess parallel workloads.

The release gate runs native JIT, MMU, synchronization, snapshot and Link checks, including the display router test and real Mach/Metal surface fixture. The x86-64 stash benchmark measures just the C restore operation. Physical iPad screen input, Link streaming while blacked out, and overall application speed require device testing.
