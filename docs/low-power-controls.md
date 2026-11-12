# Low Power sessions and controls

Use4 guest CPUs as the baseline. Six guests do not select efficiency cores; iOS controls physical placement. Compare4 and6 only with the same workload, OS Low Power Mode and display choices.

Enable OS Low Power Mode. With the Low Power guest-refresh setting enabled, a cold start requesting120Hz uses60Hz while OS LPM is active. The saved preference remains120Hz; leave LPM off and cold-start to restore it. Existing resumed machines retain their saved display state. Retina resolution stays unchanged. Expert henge-env overrides remain authoritative.

Three-finger controls → gamecontroller menu → Show Virtual Gamepad. Select native HID or the explicitly labelled keyboard mapping. Mapping provides WASD, Space, auxiliary keys and pointer look/trigger clicks. Native game recognition and camera behaviour require device checks. Hide releases the local controller; pause neutralizes/disconnects it.

For another phone: on the running Mac choose Wireless Keyboard / Gamepad and create a pairing key. On the other phone choose Use as wireless keyboard or gamepad, select the local host and enter its key. Touchpad, ASCII software/hardware keyboard and gamepad share the authenticated Link connection. Both devices need this version. Controls-only mode sends no video and adds no monitor. One Link peer is supported; disconnect an extended-display session before switching to controls-only pairing. Keep keys private.

For a useful log: choose Capture Diagnostics (30 seconds) from the same menu; reproduce desktop or gaming work and share henge.log/henge-native.log. Per-access counters stay off. CPU values are aggregate process core equivalents, not P/E residency; GPU buffer-duration sums can overlap and are not utilization/watts/temperature/gameFPS.

For CPU-only Runner: enable experimental CPU background jobs and background processing before starting. Install/update the guest companion once; use the existing automatic Start Mac and Runner flow. Wait for Listener running, then Prepare CPU Background while Henge is visible and without an extended-display video session. A real iOS CPU continued-processing grant is required. New graphics wait in guest queues; GUI/Simulator/GPU-dependent jobs may stall. Returning or Show Mac Desktop restores graphics. Persistent saving requires foreground restoration first. iOS may deny/end the task or terminate Henge. PiP is not an always-on grant. Xcode still runs inside the Mac VM; experimental Mac-app translation is not verified as an Xcode/ActionsRunner replacement.
