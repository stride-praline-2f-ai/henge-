# DuoSceneRepair (experimental host-app module)

An actual app-level scene/rotation utility for iPhone Duo. Uses public UIKit
interfaces **inside the app that links it**. It does NOT patch LaunchServices,
override SpringBoard or reach into other applications.

## What it does

1. Observes host-app foreground, physical orientation and scene activation.
2. Detects changes in the active `UIWindowScene.coordinateSpace.bounds`.
3. Calls `setNeedsUpdateOfSupportedInterfaceOrientations` and relayout of
   the scene's own root view controller, and posts
   `DuoSceneRepairGeometryDidChange` with width/height.
4. Optional explicit opt-in mode requests a geometry orientation from UIKit via
   `UIWindowScene.requestGeometryUpdate`. UIKit may decline this, especially
   when the inner display can freely resize. It is NOT a guaranteed force-rotate.

For native/UIKit apps, call `DuoSceneRepairStart()` after scene connection.
In Unity or another engine, subscribe to
`DuoSceneRepairGeometryDidChange` inside your app and update the renderer's
viewport, resolution and UI constraints. Without that engine integration,
UIKit relayout cannot magically fix a renderer caching its original size.

## Critical limits

- **Cannot fix installed App Store Roblox or Ring in place**. A normal iOS app
  cannot operate on a different process's scene.
- Modifying a third-party IPA requires injecting and **re-signing** it, which
  can break login, associated domains, keychain and other entitlements. This
  was already observed when testing a modified Ring IPA.
- The system's compatibility window may be narrower than the actual device
  screen. This module does not enlarge that system-managed window.
- Test on an iPhone Duo; build success is not device validation.
- Not affiliated with Apple, Roblox or Ring.

## Build

Run GitHub Actions `Build Duo Scene Repair prototype`.
The workflow compiles an arm64 iOS dynamic library and builds a minimal
signed-by-you scene-probe app (unsigned IPA). Use Signulous or another proper
signer for the IPA. The module itself is only for developers or consented
app-level experiments.

## Evidence

- Apple: https://developer.apple.com/iphone-duo/prepare/
- Unity: https://discussions.unity.com/t/info-ipados-27-sdk-27-adaptability-changes-iphone-duo-updates/1737980
