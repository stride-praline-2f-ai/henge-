# Exact-source validation

Source `cc2ab5fc4d270273295a4066e03fa3b91259c8dc`, patch `8528f304143f3a95a657e980073b06d7d116d7c9ce3d9409f09327c5f5775053`. Full run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43635372451. Focused GPU run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43635372436.

Passed: native JIT/MMU/VM/audio/input/network/storage/Link/snapshot/clipboard regressions, ASan/UBSan/targeted TSAN, production Swift/Metal SDK checks and complete iOS Release app compilation. The GPU checks compile real Metal4 fixtures, execute production queue/cache safety logic using recording objects, and execute the classic Metal binding/readback benchmark on the real cloud GPU. Two exact architecture offline archives compiled.

The xcode-27 cloud runner exposes an Apple Paravirtual Metal device without MTLGPUFamilyMetal4. Real Metal4 compute/interop and half-float/gamma/cursor pixel fixtures compile but return78 METAL4_UNAVAILABLE. Recording queues validate ordering/lifetime/cache logic; they do not execute GPU shaders.

Current native paired far-branch medians:1.896ns inline versus10.332ns reference; emitted fallback code18 versus12words, with the compact format retained for small caches. Random4MiB save packing medians:0.246ms adaptive versus3.700ms reference, identical raw bytes. Compressible/mixed results vary; all decode bit-exactly. These measure specific components on the cloud ARM CPU, not whole-app speed, Roblox FPS, power or cooling. Historical MMU measurements retain their original source. Existing physical touch/Pencil, Magic Keyboard, controller ergonomics, iCloud Handoff, real-game resume and iOS background save deadlines remain device validation.
