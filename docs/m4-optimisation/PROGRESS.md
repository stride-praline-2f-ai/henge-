# Integrated 0.3.3 source gate

Source `d3926d0cb1d05067a7d4525f2c0068afda9b29a7`, cumulative patch `1e321ed52bee7d1e5a9370512a182ce7e908b2834508c0b6a69001c0cdd5a3e4`.
Native/full iOS Release compile: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43160398405. Controls UI: https://github.com/stride-praline-2f-ai/henge-/actions/runs/43160398386.

All feasible source workstreams are integrated. Retained safe alternatives and
physical-device limits are recorded in henge-build/optimization-state.json.
The final metadata-only child requests one IPA; archive inspection remains a
separate gate. No interim IPA was packaged during these changes.

New follow-up: exact-binary LRU/function reuse, bounded repeated-warning cache
retention, shared grouped-memory fallback suffixes, aligned effective JIT limit,
advanced local/wireless controls with sensitivity/dead-zone/response tuning and
optional experimental PS4 USB compatibility. Existing Low Power policy, Retina,
ProMotion choice, idle waits, two-port Link and CPU-only runner paths retained.

Duo UI passes at the exact unfolded 951x669 viewport on a labelled M4 canvas.
The native Duo cloud runtime failed SpringBoard/XCTest startup; native fold
transitions remain unverified. No P/E placement, watts, thermal improvement,
Roblox driver-recognition or game FPS result is claimed from Simulator.
