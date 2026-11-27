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


# Workspace polish / review repairs. All changes remain in SwiftUI.
s = source.read_text(encoding="utf-8")

replace_once(
    '    @State private var completedSDKScan = false',
    '''    @State private var completedSDKScan = false
    @State private var scanFailed = false
    @State private var scanNotice = ""
    @State private var expandedSDKIDs: Set<String> = []
    @State private var operationLabel = "Checking…"''',
    "Workspace status",
)

replace_once(
    'guard sdk.count == 3 else { return false }',
    '''guard sdk.count == 3, (1...99).contains(sdk[0]),
              (0...99).contains(sdk[1]), (0...99).contains(sdk[2]) else { return false }''',
    "Validate SDK triple before filtering",
)

replace_once(
    '''                            let eligible = items.filter { recordedSDKBelow272($0) }
                            candidates = eligible''',
    '''                            // Ambiguous duplicate bundle IDs must never enter selection.
                            let counts = Dictionary(grouping: items, by: { $0.id })
                            let eligible = items.filter {
                                !$0.id.isEmpty && counts[$0.id]?.count == 1 &&
                                recordedSDKBelow272($0)
                            }
                            let duplicateCount = counts.values.filter { $0.count > 1 }.count
                            scanNotice = duplicateCount == 0 ? "" :
                                "Some ambiguous duplicate app records were excluded."
                            candidates = eligible''',
    "Reject ambiguous duplicate IDs",
)

# The scanner must start before the foreground heartbeat. Both use the existing
# serial engine gate. Do not alter that gate or perform any automatic writes.
replace_once(
    '''                if !startedInitialSDKScan {
                    startedInitialSDKScan = true
                    run(0)  // Read-only installed-app scan; never Apply on launch.
                }
''',
    '',
    "Remove competing onAppear scan",
)
replace_once(
    '''                guard scenePhase == .active else { return }
                checkHeartbeat()
                while !Task.isCancelled {''',
    '''                guard scenePhase == .active else { return }
                if !startedInitialSDKScan {
                    startedInitialSDKScan = true
                    run(0)  // Read-only installed-app scan; never Apply on launch.
                } else {
                    checkHeartbeat()
                }
                while !Task.isCancelled {''',
    "Ordered foreground startup",
)

replace_once(
    'guard scenePhase == .active, !working, !heartbeatChecking else { return }',
    '''guard scenePhase == .active, startedInitialSDKScan, !working, !heartbeatChecking,
              !confirmApply, !confirmRestore, !confirmFixMode else { return }''',
    "Avoid heartbeat during confirmation",
)
replace_once(
    '    private func run(_ action: Int) {',
    '''    private func run(_ action: Int) {
        guard !working, !heartbeatChecking else { return }
        if action == 0 {
            operationLabel = "Scanning installed apps…"
            scanFailed = false
            scanNotice = ""
            expandedSDKIDs = []
            fixAppID = ""
            layoutAppID = ""
            verifiedPriorSDK = ""
            verifiedBackupConfirmed = false
        } else if action == 3 {
            operationLabel = "Reading Undo history…"
        } else {
            operationLabel = action == 2 ? "Restoring selected changes…" : "Applying confirmed changes…"
        }''',
    "Prevent overlapping UI operations",
)
replace_once(
    '''        if action == 3 {
            restoreCandidates = []; restoreIDs = []; candidates = []; selectedIDs = []
        }''',
    '''        if action == 3 {
            // Opening local recovery history must not discard the scan or selection.
            restoreCandidates = []; restoreIDs = []
        }''',
    "Keep app selection while viewing Undo",
)
replace_once(
    '''            if action == 0 || action == 3 {
                let marker''',
    '''            if action == 0 || action == 3 {
                if action == 0 { scanFailed = true }
                let marker''',
    "Mark scan failure until decoded",
)
replace_once(
    '                            completedSDKScan = true',
    '''                            completedSDKScan = true
                            scanFailed = false''',
    "Successful scan state",
)
replace_once(
    '''                candidates = []; selectedIDs = []
                restoreCandidates = []; restoreIDs = []
            }
            working = false
            checkHeartbeat()''',
    '''                // A write attempt may leave the previous inventory stale.
                // Keep the result visible and require a new read-only scan.
                completedSDKScan = false
                scanFailed = false
                scanNotice = ""
                candidates = []; selectedIDs = []; expandedSDKIDs = []
                restoreCandidates = []; restoreIDs = []
                fixAppID = ""; layoutAppID = ""
            }
            working = false
            checkHeartbeat()''',
    "Invalidate inventory after write attempt",
)

# Both dedicated Fix Mode actions also invalidate scan state when clearing rows.
replace_once(
    '''            candidates = []
            selectedIDs = []
            restoreCandidates = []
            restoreIDs = []
            working = false
            checkHeartbeat()''',
    '''            completedSDKScan = false
            scanFailed = false
            scanNotice = ""
            expandedSDKIDs = []
            fixAppID = ""; layoutAppID = ""
            candidates = []
            selectedIDs = []
            restoreCandidates = []
            restoreIDs = []
            working = false
            checkHeartbeat()''',
    "Verified-prior recovery invalidation",
)
replace_once(
    '''                savedTargets[app.id] = "27.3.0"
                persistPreferences()
                candidates = []''',
    '''                savedTargets[app.id] = "27.3.0"
                persistPreferences()
                completedSDKScan = false
                scanFailed = false
                scanNotice = ""
                expandedSDKIDs = []
                fixAppID = ""; layoutAppID = ""
                candidates = []''',
    "Trial invalidation",
)

# Clear any saved target for restored apps when a confirmed restore succeeds.
replace_once(
    '        let requestedIDs = selectedIDs',
    '''        let requestedIDs = selectedIDs
        let requestedRestoreIDs = restoreIDs''',
    "Capture confirmed restore selection",
)
replace_once(
    '''                if action == 5 && value.contains("DUO_BATCH_APLICADO") {''',
    '''                if action == 2 && value.contains("DUO_BATCH_REVERTIDO") {
                    for id in requestedRestoreIDs { savedTargets.removeValue(forKey: id) }
                    persistPreferences()
                }
                if action == 5 && value.contains("DUO_BATCH_APLICADO") {''',
    "Remove stale preferred SDK after Undo",
)

# Compact controls and search feedback. All bulk actions are UI selections only.
replace_once(
    '''                    if !candidates.isEmpty {
                        HStack {
                            Text("\(candidates.count) apps below SDK 27.2")
                            Spacer()
                            Text("\(selectedIDs.count) selected")
                                .foregroundStyle(.secondary)
                        }
                        .font(.caption)
                    }''',
    '''                    if completedSDKScan {
                        HStack {
                            VStack(alignment: .leading, spacing: 3) {
                                Text("\(candidates.count) eligible").font(.title2.weight(.semibold))
                                Text("Recorded SDK below 27.2").font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()
                            VStack(alignment: .trailing, spacing: 3) {
                                Text("\(selectedIDs.count)").font(.title2.weight(.semibold))
                                Text("Selected").font(.caption).foregroundStyle(.secondary)
                            }
                        }
                        if !candidates.isEmpty {
                            HStack {
                                Button("Select all") {
                                    selectedIDs = Set(candidates.map(\.id))
                                }
                                Spacer()
                                Button("Clear selection") {
                                    selectedIDs.removeAll()
                                }
                            }
                            .buttonStyle(.borderless)
                            .font(.subheadline)
                            Button("Set selected to SDK 27.2.0") {
                                for id in selectedIDs { targets[id] = "27.2.0" }
                            }
                            .disabled(selectedIDs.isEmpty)
                            .font(.subheadline)
                            if !search.isEmpty {
                                Text("\(filtered.count) matching search · \(selectedIDs.count) selected across all apps")
                                    .font(.caption).foregroundStyle(.secondary)
                            }
                        }
                        if !scanNotice.isEmpty {
                            Label(scanNotice, systemImage: "exclamationmark.triangle")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    } else if scanFailed {
                        Label("Scan failed. Refresh and check technical details.",
                              systemImage: "exclamationmark.triangle")
                            .font(.subheadline).foregroundStyle(.orange)
                    } else if startedInitialSDKScan && !working {
                        Text("Refresh to get the current app list.")
                            .font(.caption).foregroundStyle(.secondary)
                    }''',
    "Compact summary and selection controls",
)
replace_once(
    '''                if !candidates.isEmpty {
                    Section("SDK below 27.2") {''',
    '''                if !search.isEmpty && !candidates.isEmpty && filtered.isEmpty {
                    Section {
                        Text("No apps match your search.")
                            .foregroundStyle(.secondary)
                    }
                }

                if !candidates.isEmpty {
                    Section("SDK below 27.2") {''',
    "Search empty state",
)
# Move Fix Mode after the main app list and Apply section.
fix_start = s.index('                Section {\n                    DisclosureGroup("Fix Mode"')
fix_end = s.index('                if completedSDKScan && candidates.isEmpty', fix_start)
fix_section = s[fix_start:fix_end]
s = s[:fix_start] + s[fix_end:]
undo_section = '''                Section {
                    Button {
                        run(3)
                    } label: {'''
assert s.count(undo_section) == 1
s = s.replace(undo_section, fix_section + undo_section, 1)

replace_once(
    '            .disabled(working)\n            .navigationTitle("DuoSDK")',
    '            .disabled(working || heartbeatChecking)\n            .navigationTitle("DuoSDK")',
    "Disable overlapping operations",
)
replace_once('ProgressView("Checking…")', 'ProgressView(operationLabel)', "Operation progress label")
replace_once(
    '''        guard !selectedIDs.isEmpty && changes.count == selectedIDs.count''',
    '''        guard completedSDKScan, !selectedIDs.isEmpty && changes.count == selectedIDs.count''',
    "Require a current successful scan for Apply",
)
replace_once(
    '''        guard let row = oneFixApp, let version = chosenFixVersion else { return false }''',
    '''        guard completedSDKScan, let row = oneFixApp, let version = chosenFixVersion else { return false }''',
    "Require valid scan for Fix Mode",
)
replace_once(
    '''        guard let app = oneFixApp, let version = chosenFixVersion,
              version != app.before, !working else {''',
    '''        guard completedSDKScan, let app = oneFixApp, let version = chosenFixVersion,
              version != app.before, !working, !heartbeatChecking else {''',
    "Guard Fix Mode UI operations",
)

# Only expand the SDK editor when specifically requested; target visible at all times.
replace_once(
    '''                    Text("Recorded SDK: \(item.fromVersion)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            if selectedIDs.contains(item.id) {
                HStack(spacing: 10) {''',
    '''                    Text("SDK \(item.fromVersion) → \(target(item))")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            if selectedIDs.contains(item.id) {
                Button {
                    if expandedSDKIDs.contains(item.id) {
                        expandedSDKIDs.remove(item.id)
                    } else {
                        expandedSDKIDs.insert(item.id)
                    }
                } label: {
                    Label(expandedSDKIDs.contains(item.id) ? "Hide SDK options" : "Edit SDK",
                          systemImage: expandedSDKIDs.contains(item.id) ? "chevron.up" : "slider.horizontal.3")
                        .font(.caption)
                }
                .buttonStyle(.borderless)
            }
            if selectedIDs.contains(item.id) && expandedSDKIDs.contains(item.id) {
                HStack(spacing: 10) {''',
    "Collapsed per-app target editor",
)
replace_once(
    '''                        Text("SDK 27.3.0 is experimental on iOS 27.2.x. "
                             + "It does not install iOS 27.3 or guarantee a rotation fix.")''',
    '''                        Text("Review selected apps and targets before applying. "
                             + "SDK changes are experimental; restart the iPhone after a confirmed write.")''',
    "Clarify Apply and restart instructions",
)
replace_once(
    '''Text("Changes are experimental and affect the selected apps' "
                     + "LaunchServices metadata. Keep a device backup.")''',
    '''Text("Apply the displayed SDK targets to \(selectedIDs.count) selected apps, "
                     + "including selected apps hidden by search? Keep a device backup.")''',
    "Explicit confirmation scope",
)

assert 'run(0)  // Read-only installed-app scan' in s
assert 'selectedIDs = Set(eligible.map(\\.id))' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
assert 'confirmApply = true' in s
source.write_text(s, encoding="utf-8")
print("Workspace review: compact editors, bulk selection, ordered launch, scan/error states and recovery UI repaired.")
