# Optional desktop MetalFX upscaling

Native Desktop Retina remains the default. The optional Desktop MetalFX screen
choice renders the same default 1280-point workspace at 1x, then spatially
upscales the completed primary desktop to 2x (iPad:1280x960 ->2560x1920;
Duo:its current proportional shape). MetalFX only processes the final image;
the existing guest Metal4 rendering/replay architecture is unchanged. It is not
frame generation, a CPU-emulation replacement, or guaranteed60FPS.

Exact-layout decision:80% of2560x1920 is2048x1536. A default2x Retina guest
would then have1024x768 workspace. Choosing a larger "looks like" mode may keep
a full-resolution backing and downsample, eliminating the proposed saving.
The1x workspace option avoids claiming unsupported fractional macOS UI scaling.
It has75% fewer source pixels, not75% less total work. Upscaling cannot recreate
native Retina text detail. Native remains available unchanged.

One display pipeline:low-size existing colour conversion ->MTL4FXSpatialScaler
in the same Metal4 job ->final existing compositor and sharp cursor. No CPU
readback, extra timer or full-size downsample. Three bounded leased scaler/texture
sets cover two in-flight presentations plus cached image. Leases survive GPU
completion; discarded jobs cannot populate cache. The last queued image can be
reused on cursor-only movement through existing two-way queue ordering. Actual
image epochs invalidate it even if WindowServer reuses the same texture.

The existing memory-pressure owner trims idle effects/cached images on the
presenter and temporarily uses existing linear composition without changing guest
geometry. Runtime capability/creation/admission failures fall back explicitly.
Native guest geometry is selected at cold boot on unsupported hardware or the
Compatibility backend. Link's independent secondary port is unchanged; a primary
mirror receives the original smaller scanout, avoiding full-size streaming work.
Capture/probe mode uses the existing compositor at the same output canvas.

Saved identities include the output scale and exact guest geometry. Old identities
retain native1x presentation; changing a preference cannot rewrite a saved guest.
Switch modes after a full macOS shutdown and fresh start, not Save & Leave.
macOS may remember a previous user-selected scaled mode: choose its default
resolution if the layout differs. No custom display override is installed.

Validation:portable geometry passed GCC ASan/UBSan locally. Cloud checks execute
the production pool/compositor with recording objects (routing, cache, texture
usage, bounded leases, allocation failure and pressure recovery), snapshot
identity/legacy defaults, presentation pulses, full iOS SDK/app compilation and
native regressions. A real GPU readback fixture is compiled and runs only when
Metal4FX is actually supported; otherwise returns78 explicitly. Visual quality,
MetalFX internal GPU synchronization/residency, cursor accuracy and actual power/
frame-time benefits require a supported physical GPU. Do not mark these measured
from compilation or recording fixtures.

Continuation:read current CI failures, fix source, re-export pinned patch, rerun
focused checks. No IPA until exact-source tests and full app compile pass.
