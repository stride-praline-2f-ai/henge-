# Current validation

Physical114 source follow-up is pending macOS CI. Local touch watchdog ASan/UBSan passes. Linux has no Swift/macOS SDK; no local Swift/native lifecycle pass is claimed. New source invalidates the prior115 release validation. Existing115 artifact remains delivered and unchanged.

Required checks: production NativeReportPump and SessionDiagnosticCapture worker/stale-result tests under ASan; native touch idle/held watchdog; real PVG lifecycle/allocation snapshot; complete native regressions and device/Simulator SDK plus full app compile. Packaging is disabled.
