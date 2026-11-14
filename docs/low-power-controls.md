# Low Power sessions and controls

Use4 guest CPUs as the baseline. Six guests do not select efficiency cores; iOS controls physical placement. Compare4 and6 only with the same workload, OS Low Power Mode and display choices.

Enable OS Low Power Mode. With the Low Power guest-refresh setting enabled, a cold start requesting120Hz uses60Hz while OS LPM is active. The saved preference remains120Hz; leave LPM off and cold-start to restore it. Existing resumed machines retain their saved display state. Low Power Mode does not change Retina resolution. Desktop Retina is an explicit 1280-logical-point, 2x screen choice; Native Retina keeps every panel pixel. Expert henge-env overrides remain authoritative.

Three-finger controls → gamecontroller menu → Show Virtual Gamepad. Select native HID or the explicitly labelled keyboard mapping. Mapping provides WASD, Space, auxiliary keys and pointer look/trigger clicks. Native game recognition and camera behaviour require device checks. Hide releases the local controller; pause neutralizes/disconnects it.

For another phone: on the running Mac choose Wireless Keyboard / Gamepad and create a pairing key. On the other phone choose Use as wireless keyboard or gamepad, select the local host and enter its key. Touchpad, ASCII software/hardware keyboard and gamepad share the authenticated Link connection. Both devices need this version. Controls-only mode sends no video and adds no monitor. Keep keys private.

For a useful log: choose Capture Diagnostics (30 seconds) from the same menu; reproduce desktop or gaming work and share henge.log/henge-native.log. Per-access counters stay off. CPU values are aggregate process core equivalents, not P/E residency; GPU buffer-duration sums can overlap and are not utilization/watts/temperature/gameFPS.

App Runner mode has been removed, including continued VM background execution. Update an old Mac sharing companion from Details → Sharing to retire its old worker. Existing GitHub credentials and user repositories are not deleted. Instant Resume and its bounded iOS save assertion remain; completed compatible saves survive app closure. Cloud GitHub Actions builders are separate and remain supported.

For loading: Automatic scheduling,4guest CPUs as the baseline, kernel read cache on (TLB-first), and diagnostics off. Explicit saved cache-off choices remain off; enable Kernel read cache to use the new path. Keep chosen Retina and60/120Hz preferences. Low Power Mode still applies OS limits. Native microbenchmarks are not measured app-launch or game FPS gains.

This0.3.10(111) test build enables continuous Session Diagnostics once on first launch, for the entire visible session. Settings → Performance → Session Diagnostics can disable it. It adds counters and50Hz sampling; compare release speed with diagnostics disabled. Ordinary logs include hot instruction words, disk queue/flush timing and touch setup metrics. Old guest touch helpers should be updated from Details → Sharing to use setup progress heartbeats.
