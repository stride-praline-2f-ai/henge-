# Henge 0.3.3 (104) — verified IPA

Source: `704ba172bbe48554335cf3bd0fdf6d0d2d86ef68` on feature/m4-ultra-efficiency.
Build: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43163915064
Artifact: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43163915064/artifacts/13919646442
Drive: https://drive.google.com/file/d/1xg90_q9on7qMwsWY01D_L89qF1E5rH37/view?usp=drivesdk

IPA bytes: 9851865. SHA-256:
`c424a79a3152b698b5ad556a553e6dbf33bba5904108202028d87b08a1846275`
Drive raw-byte download matches the inspected IPA SHA. Earlier releases retained.

Native regressions, sanitizers, full iOS Release app compile and archive checks
passed. App, JIT helper and StikJIT framework are arm64 iOS device executables;
helper versions/identifiers, required framework/resources, nested signatures,
entitlement values, background task metadata, source/patch identity and advanced
controller runtime markers were verified. This is ad hoc signing: the installation
tool must sign it with the user's own supported provisioning profile.

Includes existing integrated M4/Duo Low Power, MMU/JIT, damage-driven Retina/
ProMotion, idle, Link and CPU-only runner work plus exact library LRU/function
reuse, bounded repeated-warning retention, shared grouped-memory fallback code,
aligned effective JIT limits and redesigned local/wireless controls. No increase
to CPU/RAM/JIT defaults or reduction to image clarity was introduced for this
warm-up follow-up. Physical warm-up/FPS/power improvement is not yet measured.

Use the three-finger menu for gamepad visibility and settings; the old hide bar
is removed. Sensitivity/dead-zone/curve/inversion/size/opacity are configurable.
Generic HID remains default; optional PS4 compatibility needs a cold guest boot
and remains experimental pending Roblox/macOS driver recognition. Saved sessions
retain USB identity. Update both phones for wireless tuning.

Validation details: VALIDATION.md, WARMUP.md and CONTROLS-ADVANCED.md. The actual
M4 UI test passed, including a fresh-runner retry after a retained AX snapshot
timeout. Duo controls passed at 951x669 on an explicitly labelled M4 canvas. The
native Duo cloud runtime failed SpringBoard/XCTest launch; actual fold transitions,
real peripheral/network ergonomics and M4/Duo thermal/core-residency results remain
physical-device checks. iOS may deny/end CPU continued processing; no unlimited
background guarantee or entitlement bypass is supplied.

Frame generation was assessed separately (FRAME-GENERATION.md). CyPort uses
Cyberpunk's own FSR3 setting, and its README advises disabling it for heat/input
delay. This IPA does not claim interpolation or guaranteed 60 FPS.

Obsolete build queue: both IPA workflows retain shared henge-custom-ipa with
cancel-in-progress. Four stale 11-November Duo queue records were individually
checked for exact SHA/branch/workflow and ordinary/force cancellation attempted.
GitHub refused both endpoints with409 'Cannot cancel a workflow run that has not
been queued yet' for43097588939,43097137150,43096760096,43096402891. Evidence:
https://github.com/stride-praline-2f-ai/henge-/actions/runs/43164472319 .
Their old branch head is343d2d84caff07b2aeff6315c77108d39efbe823, so each old
workflow's current-head guard refuses those obsolete sources. They are not
reported as cancelled. The current release was the only active IPA build.
