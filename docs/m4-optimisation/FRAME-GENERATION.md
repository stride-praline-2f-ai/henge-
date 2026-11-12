# Frame generation assessment

Reviewed Thijs2004/CyPort README and shim/MacShim.m at 65e2e57a95263f60516f567e274780d8ebd97072 on 12 November 2026.
The shim reads Cyberpunk's FrameGeneration and FSR3_FrameGeneration settings,
and leaves pacing to the game when generation is enabled. It is not a universal
interpolator for arbitrary desktop/Roblox output. The README recommends leaving
frame generation off because it adds GPU work and input delay.

Henge's final display image does not provide game-engine depth/motion-vector
integration. A generic image-based interpolator would need separate motion
estimation, history textures, scene-cut handling and safe cursor/UI composition.
A frame blend or duplicate presentation must not be labelled generated real FPS.
Generation cannot increase guest simulation/input update rate or recover missing
game asset detail. It needs GPU and memory headroom and device latency/quality/
power comparison before being worthwhile.

Decision for 0.3.3: preserve demand-driven pixel-accurate presentation and the
cooled defaults. Do not enable interpolation universally or promise 60 FPS. An
optional gaming experiment can be evaluated separately after this validated IPA,
with separate real/rendered/generated/presented counts and automatic bypass for
unchanged content, discontinuities and pressure. No speculative implementation
or hardware performance claim is included in this release.

Sources: https://github.com/Thijs2004/CyPort/blob/65e2e57a95263f60516f567e274780d8ebd97072/README.md and
https://github.com/Thijs2004/CyPort/blob/65e2e57a95263f60516f567e274780d8ebd97072/shim/MacShim.m
