# Exact-source validation

Source `ac3f64c4eb5c75799531e12092bf8f11752956f7`, patch `1487d10f3da4e5af6b61a02e440fa0adb2c227fd96e3a7a81bdb7c8417984889`. Full run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43606861317. Focused GPU run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43606861368.

Passed: native JIT/MMU/VM/audio/input/network/storage/Link/snapshot/clipboard regressions, ASan/UBSan/targeted TSAN, production Swift/Metal SDK checks and complete iOS Release app compilation. The GPU checks compile real Metal4 fixtures, execute production queue/cache safety logic using recording objects, and execute the classic Metal binding/readback benchmark on the real cloud GPU. Two exact architecture offline archives compiled.

The xcode-27 cloud runner exposes an Apple Paravirtual Metal device without MTLGPUFamilyMetal4. Real Metal4 compute/interop and half-float/gamma/cursor pixel fixtures compile but return78 METAL4_UNAVAILABLE. Recording queues validate ordering/lifetime/cache logic; they do not execute GPU shaders.

The repeated-binding microbenchmark measures encoding CPU time only; it is not whole-app speed, Roblox FPS, power or cooling. Historical MMU benchmark evidence remains attributed to the earlier unchanged engine source. Existing physical touch/Pencil, Magic Keyboard, controller ergonomics, iCloud Handoff, real-game resume and iOS background save deadlines remain device validation.
