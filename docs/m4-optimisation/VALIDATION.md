# Current development: validation pending

Desktop MetalFX source is newer than the historical proof below. No IPA is requested until new exact-source checks pass.

# Exact-source validation

Source `c3cb95e66b7a89756c54a961b0eb52734aa4f881`, patch `6588d7d46095820710e586c256378bcfcf07d3e4cae3cdc066879e70e4e5bbb9`. Full run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43640905062. Focused GPU run https://github.com/stride-praline-2f-ai/henge-/actions/runs/43640905054.

Passed: native JIT/MMU/VM/audio/input/network/storage/Link/snapshot/clipboard regressions, ASan/UBSan/targeted TSAN, production Swift/Metal SDK checks and complete iOS Release app compilation. The GPU checks compile real Metal4 fixtures, execute production queue/cache safety logic using recording objects, and execute the classic Metal binding/readback benchmark on the real cloud GPU. Two exact architecture offline archives compiled.

The xcode-27 cloud runner exposes an Apple Paravirtual Metal device without MTLGPUFamilyMetal4. Real Metal4 compute/interop and half-float/gamma/cursor pixel fixtures compile but return78 METAL4_UNAVAILABLE. Recording queues validate ordering/lifetime/cache logic; they do not execute GPU shaders.

Earlier cc2ab5f native paired far-branch medians:1.896ns inline versus10.332ns reference; emitted fallback code18 versus12words, with the compact format retained for small caches. Its random4MiB save packing medians:0.246ms adaptive versus3.700ms reference, identical raw bytes. Compressible/mixed results vary; all decode bit-exactly. These measure specific components on the cloud ARM CPU, not whole-app speed, Roblox FPS, power or cooling. Historical MMU measurements retain their original source. Reported113 letterboxing is reproduced mathematically and prevented for future iPad Desktop cold starts, without changing Fit/Duo or mutating snapshots. Snapshots remain build-bound: shut down macOS before updating; the virtual disk is retained. Physical114 layout/touch/Pencil, Magic Keyboard, controller ergonomics, iCloud Handoff, real-game resume and iOS background save deadlines remain device validation.
