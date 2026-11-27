#!/usr/bin/env python3
"""DuoSDK: scan installed apps on launch; show/preselect recorded SDK < 27.2.0.

This is a SwiftUI-only presentation change, applied after the other UI patches.
The existing read-only scan (action 0), manual Apply confirmation, cache
integrity checks, and Undo behaviour are deliberately preserved.
"""
from pathlib import Path
import sys

source = Path(sys.argv[1]).resolve() / "Sources" / "App.swift"
s = source.read_text(encoding="utf-8")

def replace_once(before, after, label):
    global s
    occurrences = s.count(before)
    assert occurrences == 1, f"{label}: expected 1 match, got {occurrences}"
    s = s.replace(before, after, 1)

replace_once(
    '    @State private var showAdvanced = false',
    '''    @State private var showAdvanced = false
    @State private var startedInitialSDKScan = false
    @State private var completedSDKScan = false''',
    "Scan lifecycle state",
)

replace_once(
    '    private var filtered: [DuoSDKCandidate] {',
    '''    private func recordedSDKBelow272(_ item: DuoSDKCandidate) -> Bool {
        // Strict semantic comparison to 27.2.0. Equal / newer tags are hidden.
        let sdk = item.before
        guard sdk.count == 3 else { return false }
        return sdk[0] < 27 || (sdk[0] == 27 && sdk[1] < 2)
    }

    private var filtered: [DuoSDKCandidate] {''',
    "Recorded SDK filter",
)

replace_once(
    '''                        if action == 0, let items = try? JSONDecoder().decode([DuoSDKCandidate].self, from: bytes) {
                            candidates = items
                        } else if action == 3''',
    '''                        if action == 0, let items = try? JSONDecoder().decode([DuoSDKCandidate].self, from: bytes) {
                            // Only render apps carrying a pre-27.2 recorded SDK.
                            let eligible = items.filter { recordedSDKBelow272($0) }
                            candidates = eligible
                            // Auto-select for review; do not call Apply or change the OS.
                            selectedIDs = Set(eligible.map(\.id))
                            // Reset stale targets after an OS reinstall or app update.
                            // Existing saved preferences remain available separately.
                            targets = Dictionary(uniqueKeysWithValues:
                                eligible.map { ($0.id, "27.2.0") })
                            completedSDKScan = true
                        } else if action == 3''',
    "Decoded scan result",
)

replace_once(
    '''        if action == 0 {
            candidates = []; selectedIDs = []; restoreCandidates = []; restoreIDs = []
        }''',
    '''        if action == 0 {
            completedSDKScan = false
            candidates = []; selectedIDs = []; restoreCandidates = []; restoreIDs = []
        }''',
    "Fresh scan reset",
)

replace_once(
    '''            .onAppear {
                UIDevice.current.beginGeneratingDeviceOrientationNotifications()
                captureRotationSignal()
            }''',
    '''            .onAppear {
                UIDevice.current.beginGeneratingDeviceOrientationNotifications()
                captureRotationSignal()
                if !startedInitialSDKScan {
                    startedInitialSDKScan = true
                    run(0)  // Read-only installed-app scan; never Apply on launch.
                }
            }''',
    "One-time launch scan",
)

replace_once(
    '''Label(candidates.isEmpty ? "Find installed apps" : "Refresh apps",
                              systemImage: "arrow.clockwise")''',
    '''Label(completedSDKScan ? "Refresh eligible apps" : "Scan installed apps",
                              systemImage: "arrow.clockwise")''',
    "Scan button label",
)

replace_once(
    r'Text("\(candidates.count) apps found")',
    r'Text("\(candidates.count) apps below SDK 27.2")',
    "Eligible results count",
)

replace_once(
    'Text("Nothing changes on your phone until you select an app and confirm Apply.")',
    'Text("Older-SDK apps are preselected for review. Nothing changes until you confirm Apply.")',
    "Explicit confirmation notice",
)

replace_once(
    '''                if !candidates.isEmpty {
                    Section("Apps") {''',
    '''                if completedSDKScan && candidates.isEmpty {
                    Section {
                        Text("No recognised installed apps have a recorded SDK below 27.2.0.")
                            .font(.callout)
                            .foregroundStyle(.secondary)
                    }
                }

                if !candidates.isEmpty {
                    Section("SDK below 27.2") {''',
    "Eligible app list",
)

# Fail if this patch somehow wired automatic writes to the launch handler.
launch_handler = s[s.index('            .onAppear {'):s.index('            .onReceive(NotificationCenter.default.publisher(')]
assert 'run(0)' in launch_handler, "Startup must scan"
assert 'run(1)' not in launch_handler, "Startup must not apply SDK changes"
assert 'recordedSDKBelow272($0)' in s
assert 'selectedIDs = Set(eligible.map(\\.id))'.replace('\\\\', '\\') in s
assert 'confirmApply = true' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
assert 'Undo recorded changes' in s

source.write_text(s, encoding="utf-8")
print("DuoSDK auto-scan: only SDK <27.2.0 visible; matching rows preselected; target 27.2.0.")
print("Read-only launch scan, manual Apply confirmation, and Undo preserved.")
