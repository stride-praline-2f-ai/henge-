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


# Two-tab dashboard redesign. Reuse the existing Tools controls and engine
# methods rather than rewriting any transaction, signing, or cache logic.
s = source.read_text(encoding="utf-8")
replace_once(
    '    @State private var operationLabel = "Checking…"',
    '''    @State private var operationLabel = "Checking…"
    @State private var selectedDashboardTab = 0''',
    "Dashboard tab state",
)

view_start = s.index('private struct DuoSDKView: View {')
body_start = s.index('    var body: some View {', view_start)
tools_start = s.index('                Section {\n                    DisclosureGroup("Fix Mode"', body_start)
tools_end = s.index('            }\n            .searchable(text: $search, prompt: "Search apps")', tools_start)
dialogs_start = s.index('            .confirmationDialog("Apply this compatibility trial?"', tools_end)
# Keep confirmation dialogs, orientation notifications and the foreground task
# attached to the shared parent, not a tab that disappears when switching.
body_end = s.index('    private var oneFixApp:', dialogs_start)
old_tools = s[tools_start:tools_end]
old_modifiers = s[dialogs_start:body_end]
assert 'run(3)' in old_tools and 'Advanced & diagnostics' in old_tools
assert 'run(0)  // Read-only installed-app scan' in old_modifiers
assert 'run(1)' in old_modifiers

new_body = r'''
    private var scanningApps: Bool {
        !startedInitialSDKScan || (working && operationLabel == "Scanning installed apps…")
    }

    var body: some View {
        ZStack {
            TabView(selection: $selectedDashboardTab) {
                NavigationStack {
                    appsDashboard
                        .navigationTitle("DuoSDK")
                        .navigationBarTitleDisplayMode(.large)
                        .toolbar {
                            ToolbarItem(placement: .topBarTrailing) {
                                Button {
                                    run(0)
                                } label: {
                                    Image(systemName: "arrow.clockwise")
                                }
                                .accessibilityLabel("Refresh installed apps")
                                .disabled(working || heartbeatChecking)
                            }
                        }
                }
                .tabItem { Label("Apps", systemImage: "square.grid.2x2") }
                .tag(0)

                NavigationStack {
                    toolsDashboard
                        .navigationTitle("Tools")
                        .navigationBarTitleDisplayMode(.large)
                }
                .tabItem { Label("Tools", systemImage: "slider.horizontal.3") }
                .tag(1)
            }
            .disabled(working || heartbeatChecking)
            .accessibilityHidden(scanningApps)

            if scanningApps {
                launchScanView
                    .zIndex(1)
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.22), value: scanningApps)
'''
# Old modifiers include the final NavigationStack closing brace and body brace.
# Strip the old NavigationStack close; modifiers now attach to ZStack.
tail = old_modifiers.rstrip()
assert tail.endswith('        }\n    }'), tail[-250:]
tail = tail[:-len('        }\n    }')] + '    }\n\n'
# Indentation is cosmetic in Swift; keep existing closure structure intact.
new_body += tail
new_body += r'''
    private var launchScanView: some View {
        ZStack {
            Color(uiColor: .systemGroupedBackground).ignoresSafeArea()
            VStack(spacing: 24) {
                Spacer()
                ZStack {
                    RoundedRectangle(cornerRadius: 30, style: .continuous)
                        .fill(Color.accentColor.opacity(0.12))
                        .frame(width: 108, height: 108)
                    Image(systemName: "square.grid.2x2.fill")
                        .font(.system(size: 44, weight: .medium))
                        .foregroundStyle(Color.accentColor)
                }
                VStack(spacing: 8) {
                    Text("DuoSDK")
                        .font(.system(.largeTitle, design: .rounded).weight(.bold))
                    Text("Searching installed apps")
                        .font(.headline)
                    Text("Checking recorded SDK versions below 27.2")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                ProgressView()
                    .controlSize(.large)
                    .tint(.accentColor)
                    .accessibilityLabel("Scanning installed apps")
                Spacer()
                Text("Read-only scan")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.bottom, 24)
            }
            .padding(.horizontal, 32)
            .frame(maxWidth: 480)
        }
        .accessibilityElement(children: .contain)
    }

    private var appsDashboard: some View {
        List {
            if completedSDKScan {
                Section {
                    VStack(alignment: .leading, spacing: 10) {
                        HStack(alignment: .center) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("\(candidates.count)")
                                    .font(.system(size: 52, weight: .bold, design: .rounded))
                                    .monospacedDigit()
                                    .foregroundStyle(Color.accentColor)
                                Text("Eligible apps")
                                    .font(.headline)
                            }
                            Spacer()
                            Image(systemName: "checkmark.circle")
                                .font(.system(size: 36, weight: .light))
                                .foregroundStyle(Color.accentColor)
                                .accessibilityHidden(true)
                        }
                        Text("Recorded SDK below 27.2")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        if !candidates.isEmpty {
                            Divider()
                            HStack {
                                Text("\(selectedIDs.count) selected")
                                    .font(.subheadline.weight(.medium))
                                Spacer()
                                Button(selectedIDs.count == candidates.count ? "Deselect all" : "Select all") {
                                    if selectedIDs.count == candidates.count {
                                        selectedIDs.removeAll()
                                    } else {
                                        selectedIDs = Set(candidates.map(\.id))
                                    }
                                }
                                .buttonStyle(.borderless)
                                .font(.subheadline.weight(.medium))
                            }
                        }
                    }
                    .padding(.vertical, 10)
                    if !scanNotice.isEmpty {
                        Label(scanNotice, systemImage: "exclamationmark.triangle")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                if candidates.isEmpty {
                    Section {
                        ContentUnavailableView("No eligible apps",
                            systemImage: "checkmark.seal",
                            description: Text("No recognised installed apps have a recorded SDK below 27.2.0."))
                    }
                } else {
                    Section("Installed apps") {
                        ForEach(candidates.sorted {
                            $0.name.localizedStandardCompare($1.name) == .orderedAscending
                        }) { item in
                            dashboardAppRow(item)
                        }
                    }
                }
            } else if !scanningApps {
                Section {
                    if scanFailed {
                        ContentUnavailableView("Scan unavailable",
                            systemImage: "exclamationmark.triangle",
                            description: Text("DuoSDK could not read or decode the app inventory. Open Tools for details."))
                        Button("View technical details") {
                            showRawOutput = true
                            selectedDashboardTab = 1
                        }
                    } else {
                        ContentUnavailableView("Refresh apps",
                            systemImage: "arrow.clockwise",
                            description: Text("A new scan is required before making another change."))
                    }
                    if !report.isEmpty {
                        Text(briefResult(report))
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .textSelection(.enabled)
                    }
                    Button("Scan installed apps") { run(0) }
                        .disabled(working || heartbeatChecking)
                }
            }
            if working && !scanningApps {
                Section { ProgressView(operationLabel) }
            }
        }
        .listStyle(.insetGrouped)
        .safeAreaInset(edge: .bottom, spacing: 0) {
            if completedSDKScan && !candidates.isEmpty {
                VStack(spacing: 8) {
                    Button {
                        confirmApply = true
                    } label: {
                        HStack {
                            Spacer()
                            Label("Apply to \(selectedIDs.count) apps", systemImage: "checkmark.circle.fill")
                                .font(.headline)
                            Spacer()
                        }
                        .padding(.vertical, 6)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .disabled(!canApply || working || heartbeatChecking)
                    if !selectedIDs.isEmpty && !canApply {
                        Text("Check SDK targets in Tools. SDK 27.3 requires one selected app.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                    } else {
                        Text("Changes require confirmation.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 12)
                .background(.regularMaterial)
            }
        }
    }

    private func dashboardAppRow(_ item: DuoSDKCandidate) -> some View {
        let selected = selectedIDs.contains(item.id)
        return Button {
            if selected { selectedIDs.remove(item.id) }
            else { selectedIDs.insert(item.id) }
        } label: {
            HStack(spacing: 12) {
                Image(systemName: "app.fill")
                    .font(.title2)
                    .foregroundStyle(Color.accentColor.opacity(0.75))
                    .frame(width: 42, height: 42)
                    .background(Color.accentColor.opacity(0.10),
                                in: RoundedRectangle(cornerRadius: 11))
                    .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 4) {
                    Text(item.name)
                        .font(.body.weight(.medium))
                        .foregroundStyle(.primary)
                    Text(selected ? "SDK \(item.fromVersion) → \(target(item))" :
                         "SDK \(item.fromVersion)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 8)
                Image(systemName: selected ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundStyle(selected ? Color.accentColor : Color.secondary)
                    .accessibilityHidden(true)
            }
            .padding(.vertical, 4)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityValue(selected ? "Selected" : "Not selected")
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private var toolsDashboard: some View {
        List {
            if completedSDKScan && !candidates.isEmpty {
                Section("SDK options") {
                    Button("Reset selected targets to SDK 27.2.0") {
                        for id in selectedIDs { targets[id] = "27.2.0" }
                    }
                    .disabled(selectedIDs.isEmpty)
                    DisclosureGroup("Edit individual SDK targets") {
                        ForEach(candidates.sorted {
                            $0.name.localizedStandardCompare($1.name) == .orderedAscending
                        }) { item in
                            compactAppRow(item)
                        }
                    }
                }
            }
'''
new_body += old_tools
new_body += r'''
        }
        .listStyle(.insetGrouped)
    }

'''
s = s[:body_start] + new_body + s[body_end:]
# The selection scope no longer involves search on the Apps tab.
replace_once(
    '''Text("Apply the displayed SDK targets to \(selectedIDs.count) selected apps, "
                     + "including selected apps hidden by search? Keep a device backup.")''',
    '''Text("Apply the displayed SDK targets to \(selectedIDs.count) selected apps? "
                     + "These changes are experimental. Keep a device backup.")''',
    "Dashboard confirmation",
)

assert 'TabView(selection: $selectedDashboardTab)' in s
assert 'launchScanView' in s and 'ProgressView()' in s
assert 'run(0)  // Read-only installed-app scan' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
assert 'confirmApply = true' in s
assert 'selectedIDs = Set(eligible.map(\\.id))' in s
assert 'Undo recorded changes' in s
source.write_text(s, encoding="utf-8")
print("DuoSDK dashboard: launch scanner, eligible app list, fixed Apply bar, separate Tools tab.")


# Installed-app artwork: request only the already-scanned app identifiers.
# This uses a best-effort UIKit icon lookup with no new permissions, network
# requests, app-container reads, or changes to the SDK transaction engine.
s = source.read_text(encoding="utf-8")
replace_once(
    '    @State private var selectedDashboardTab = 0',
    '''    @State private var selectedDashboardTab = 0
    @State private var dashboardIcons: [String: UIImage] = [:]
    @State private var attemptedDashboardIcons: Set<String> = []
    @Environment(\.displayScale) private var dashboardIconScale''',
    "App icon cache state",
)
replace_once(
    '''            expandedSDKIDs = []
            fixAppID = ""
            layoutAppID = ""
            verifiedPriorSDK = ""''',
    '''            expandedSDKIDs = []
            dashboardIcons.removeAll()
            attemptedDashboardIcons.removeAll()
            fixAppID = ""
            layoutAppID = ""
            verifiedPriorSDK = ""''',
    "Clear icon cache on explicit rescan",
)
replace_once(
    '''                Image(systemName: "app.fill")
                    .font(.title2)
                    .foregroundStyle(Color.accentColor.opacity(0.75))
                    .frame(width: 42, height: 42)
                    .background(Color.accentColor.opacity(0.10),
                                in: RoundedRectangle(cornerRadius: 11))
                    .accessibilityHidden(true)''',
    '''                dashboardAppIcon(item)''',
    "Replace generic app artwork",
)
replace_once(
    '''        .accessibilityValue(selected ? "Selected" : "Not selected")
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private var toolsDashboard: some View {''',
    '''        .accessibilityValue(selected ? "Selected" : "Not selected")
        .accessibilityAddTraits(selected ? .isSelected : [])
        .task(id: item.id) { @MainActor in
            // Lazy, local lookups; do not hold up the startup scan.
            guard !attemptedDashboardIcons.contains(item.id),
                  candidates.contains(where: { $0.id == item.id }) else { return }
            attemptedDashboardIcons.insert(item.id)
            if let icon = DuoSDKIconForBundleID(item.id, dashboardIconScale) {
                dashboardIcons[item.id] = icon
            }
        }
    }

    private func dashboardAppIcon(_ item: DuoSDKCandidate) -> some View {
        Group {
            if let icon = dashboardIcons[item.id] {
                Image(uiImage: icon)
                    .resizable()
                    .scaledToFit()
            } else {
                ZStack {
                    Color.accentColor.opacity(0.12)
                    Text(item.name.isEmpty ? "?" : String(item.name.prefix(1)).uppercased())
                        .font(.system(size: 19, weight: .semibold, design: .rounded))
                        .foregroundStyle(Color.accentColor)
                }
            }
        }
        .frame(width: 44, height: 44)
        .clipShape(RoundedRectangle(cornerRadius: 11, style: .continuous))
        .accessibilityHidden(true)
    }

    private var toolsDashboard: some View {''',
    "Lazy icon loading with monogram fallback",
)
# Existing bridge and compilation unit are already part of the Xcode target.
bridge = source.parent / "Bridge.h"
impl = source.parent / "XFlags.m"
bridge_text = bridge.read_text(encoding="utf-8")
impl_text = impl.read_text(encoding="utf-8")
assert "DuoSDKIconForBundleID" not in bridge_text
assert "DuoSDKIconForBundleID" not in impl_text
bridge.write_text(bridge_text + r'''

#import <UIKit/UIKit.h>
FOUNDATION_EXPORT UIImage * _Nullable DuoSDKIconForBundleID(
    NSString * _Nonnull identifier, CGFloat scale);
''', encoding="utf-8")
impl.write_text(impl_text + r'''

#import <UIKit/UIKit.h>
#import <string.h>

// Best effort: this private UIKit selector is not guaranteed on all releases.
// No fallback that attempts to cross the application's sandbox.
UIImage * _Nullable DuoSDKIconForBundleID(NSString * _Nonnull identifier, CGFloat scale) {
    if (!NSThread.isMainThread || !identifier.length || identifier.length > 255) return nil;
    @try {
        SEL selector = NSSelectorFromString(@"_applicationIconImageForBundleIdentifier:format:scale:");
        Class imageClass = UIImage.class;
        if (![imageClass respondsToSelector:selector]) return nil;
        NSMethodSignature *sig = [imageClass methodSignatureForSelector:selector];
        if (!sig || sig.numberOfArguments != 5 || sig.methodReturnType[0] != '@') return nil;
        const char *bundleType = [sig getArgumentTypeAtIndex:2];
        const char *formatType = [sig getArgumentTypeAtIndex:3];
        const char *scaleType = [sig getArgumentTypeAtIndex:4];
        if (bundleType[0] != '@' || strcmp(scaleType, @encode(CGFloat)) != 0) return nil;
        NSInvocation *invocation = [NSInvocation invocationWithMethodSignature:sig];
        invocation.target = imageClass;
        invocation.selector = selector;
        __unsafe_unretained NSString *bundleID = identifier;
        [invocation setArgument:&bundleID atIndex:2];
        NSInteger largeFormat = 2;
        int smallFormat = 2;
        if (strcmp(formatType, @encode(NSInteger)) == 0) {
            [invocation setArgument:&largeFormat atIndex:3];
        } else if (strcmp(formatType, @encode(int)) == 0) {
            [invocation setArgument:&smallFormat atIndex:3];
        } else {
            return nil;
        }
        CGFloat requestedScale = MAX(1.0, MIN(3.0, scale));
        [invocation setArgument:&requestedScale atIndex:4];
        [invocation invoke];
        __unsafe_unretained id value = nil;
        [invocation getReturnValue:&value];
        if (![value isKindOfClass:UIImage.class]) return nil;
        UIImage *icon = value;
        return icon.size.width > 0 && icon.size.height > 0 ? icon : nil;
    } @catch (NSException *exception) {
        return nil;
    }
}
''', encoding="utf-8")
assert 'dashboardAppIcon(item)' in s
assert 'DuoSDKIconForBundleID(item.id, dashboardIconScale)' in s
assert 'run(0)  // Read-only installed-app scan' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
source.write_text(s, encoding="utf-8")
print("Dashboard artwork: local UIKit icon lookup, lazy in-memory cache, initials fallback.")


# App Store artwork fallback: explicitly opt in before sending bundle IDs to Apple.
# Local lookup remains the default. No extra entitlements or cross-container reads.
s = source.read_text(encoding="utf-8")

replace_once(
    '    @State private var attemptedDashboardIcons: Set<String> = []',
    '''    @State private var attemptedDashboardIcons: Set<String> = []
    @AppStorage("duosdk.appStoreArtwork.v1") private var useStoreArtwork = false
    @State private var storeArtwork: [String: UIImage] = [:]
    @State private var storeArtworkAttempts: Set<String> = []
    @State private var artworkGeneration = 0
    @State private var artworkLoading = false''',
    "Opt-in artwork settings",
)
replace_once(
    '''            dashboardIcons.removeAll()
            attemptedDashboardIcons.removeAll()''',
    '''            dashboardIcons.removeAll()
            attemptedDashboardIcons.removeAll()
            storeArtwork.removeAll()
            storeArtworkAttempts.removeAll()
            artworkGeneration += 1''',
    "Invalidate artwork on refresh",
)
replace_once(
    '''            .accessibilityHidden(scanningApps)

            if scanningApps''',
    '''            .accessibilityHidden(scanningApps)
            .task(id: artworkTaskKey) {
                await loadAppStoreArtwork()
            }

            if scanningApps''',
    "Run artwork requests separately from scan",
)
replace_once(
    '''            if let icon = dashboardIcons[item.id] {
                Image(uiImage: icon)''',
    '''            if let icon = (useStoreArtwork ? storeArtwork[item.id] : nil) ?? dashboardIcons[item.id] {
                Image(uiImage: icon)''',
    "Prefer verified App Store artwork when enabled",
)
replace_once(
    '''    private var toolsDashboard: some View {
        List {
            if completedSDKScan''',
    '''    private var artworkTaskKey: String {
        "\(useStoreArtwork)-\(artworkGeneration)-" +
            candidates.map(\.id).sorted().joined(separator: ",")
    }

    private struct StoreArtworkResponse: Decodable {
        let results: [StoreArtworkRecord]
    }

    private struct StoreArtworkRecord: Decodable {
        let bundleId: String?
        let artworkUrl100: String?
        let artworkUrl512: String?
    }

    @MainActor
    private func loadAppStoreArtwork() async {
        guard useStoreArtwork, completedSDKScan, !candidates.isEmpty else {
            artworkLoading = false
            return
        }
        let generation = artworkGeneration
        let ids = candidates.sorted {
            $0.name.localizedStandardCompare($1.name) == .orderedAscending
        }.map(\.id)
        let pending = ids.filter { storeArtwork[$0] == nil && !storeArtworkAttempts.contains($0) }
        guard !pending.isEmpty else { artworkLoading = false; return }

        let config = URLSessionConfiguration.ephemeral
        config.httpShouldSetCookies = false
        config.urlCache = nil
        config.timeoutIntervalForRequest = 10
        config.timeoutIntervalForResource = 15
        let session = URLSession(configuration: config)
        artworkLoading = true
        defer {
            session.invalidateAndCancel()
            if artworkGeneration == generation && !Task.isCancelled {
                artworkLoading = false
            }
        }
        let region = Locale.current.region?.identifier.lowercased() ?? "gb"
        for (index, id) in pending.enumerated() {
            guard !Task.isCancelled, useStoreArtwork, artworkGeneration == generation else { return }
            // Apple asks clients to keep lookup traffic modest.
            if index > 0 {
                do { try await Task.sleep(for: .seconds(3)) } catch { return }
            }
            guard !Task.isCancelled, useStoreArtwork, artworkGeneration == generation else { return }
            let icon = await fetchStoreArtwork(id, country: region, session: session)
            guard !Task.isCancelled, useStoreArtwork, artworkGeneration == generation else { return }
            storeArtworkAttempts.insert(id)
            if let icon { storeArtwork[id] = icon }
        }
    }

    private func fetchStoreArtwork(_ id: String, country: String, session: URLSession) async -> UIImage? {
        guard !id.isEmpty, id.count <= 255,
              var components = URLComponents(string: "https://itunes.apple.com/lookup") else { return nil }
        components.queryItems = [
            URLQueryItem(name: "bundleId", value: id),
            URLQueryItem(name: "country", value: country),
            URLQueryItem(name: "entity", value: "software")
        ]
        guard let url = components.url else { return nil }
        do {
            let (data, response) = try await session.data(from: url)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200,
                  http.url?.host == "itunes.apple.com", data.count <= 4_000_000,
                  let payload = try? JSONDecoder().decode(StoreArtworkResponse.self, from: data),
                  let record = payload.results.first(where: { $0.bundleId == id }),
                  let address = record.artworkUrl100 ?? record.artworkUrl512,
                  let artworkURL = URL(string: address), artworkURL.scheme == "https",
                  let host = artworkURL.host?.lowercased(),
                  host == "mzstatic.com" || host.hasSuffix(".mzstatic.com") ||
                  host == "apple.com" || host.hasSuffix(".apple.com"),
                  !Task.isCancelled else { return nil }
            let (bytes, imageResponse) = try await session.data(from: artworkURL)
            guard let imageHTTP = imageResponse as? HTTPURLResponse, imageHTTP.statusCode == 200,
                  let finalHost = imageHTTP.url?.host?.lowercased(),
                  finalHost == "mzstatic.com" || finalHost.hasSuffix(".mzstatic.com") ||
                  finalHost == "apple.com" || finalHost.hasSuffix(".apple.com"),
                  bytes.count <= 2_000_000,
                  let image = UIImage(data: bytes), image.size.width > 0, image.size.height > 0
            else { return nil }
            return image
        } catch { return nil }
    }

    private var toolsDashboard: some View {
        List {
            Section {
                Toggle("Use App Store artwork", isOn: $useStoreArtwork)
                if useStoreArtwork {
                    if artworkLoading {
                        ProgressView("Loading App Store icons…")
                    }
                    Text("\(storeArtwork.count) App Store icons loaded")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Button("Retry missing icons") {
                        storeArtworkAttempts.removeAll()
                        artworkGeneration += 1
                    }
                    .disabled(artworkLoading || !completedSDKScan)
                }
            } header: {
                Text("App icons")
            } footer: {
                Text("Optional. Sends eligible app bundle identifiers and your storefront region to Apple to retrieve public App Store artwork. No account credentials are sent. Unlisted or sideloaded apps may still show initials.")
            }
            if completedSDKScan''',
    "Independent Apple artwork lookup and controls",
)
replace_once(
    '''                    .padding(.vertical, 10)
                    if !scanNotice.isEmpty''',
    '''                    .padding(.vertical, 10)
                    if !candidates.isEmpty && !useStoreArtwork &&
                       dashboardIcons.count < candidates.count {
                        Button {
                            selectedDashboardTab = 1
                        } label: {
                            Label("Missing icons? Use App Store artwork", systemImage: "photo.on.rectangle")
                                .font(.subheadline)
                        }
                    }
                    if !scanNotice.isEmpty''',
    "Discoverable artwork setting",
)
# Keep existing local method; accept unsigned integer formats where available.
impl_text = impl.read_text(encoding="utf-8")
old = '''        if (strcmp(formatType, @encode(NSInteger)) == 0) {
            [invocation setArgument:&largeFormat atIndex:3];
        } else if (strcmp(formatType, @encode(int)) == 0) {
            [invocation setArgument:&smallFormat atIndex:3];'''
new = '''        if (strcmp(formatType, @encode(NSInteger)) == 0 ||
            strcmp(formatType, @encode(NSUInteger)) == 0) {
            [invocation setArgument:&largeFormat atIndex:3];
        } else if (strcmp(formatType, @encode(int)) == 0 ||
                   strcmp(formatType, @encode(unsigned int)) == 0) {
            [invocation setArgument:&smallFormat atIndex:3];'''
assert impl_text.count(old) == 1
impl.write_text(impl_text.replace(old, new, 1), encoding="utf-8")
assert 'guard useStoreArtwork, completedSDKScan' in s
assert 'record.bundleId' not in s or 'payload.results.first(where:' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
source.write_text(s, encoding="utf-8")
print("Optional App Store artwork retrieval: exact bundle ID, HTTPS, cancellable async requests, no new permissions.")


# Fullscreen is a separate workspace. Do not imply that LaunchServices SDK
# metadata can control UIKit status bars in other applications.
s = source.read_text(encoding="utf-8")
replace_once(
    '    @State private var selectedDashboardTab = 0',
    '''    @State private var selectedDashboardTab = 0
    @State private var fullscreenPreviewHidden = false''',
    "Fullscreen preview state",
)
replace_once(
    '''                .tabItem { Label("Tools", systemImage: "slider.horizontal.3") }
                .tag(1)
            }''',
    '''                .tabItem { Label("Tools", systemImage: "slider.horizontal.3") }
                .tag(1)

                NavigationStack {
                    fullscreenDashboard
                        .navigationTitle("Fullscreen")
                        .navigationBarTitleDisplayMode(.large)
                }
                .tabItem {
                    Label("Fullscreen", systemImage: "arrow.up.left.and.arrow.down.right")
                }
                .tag(2)
            }''',
    "Separate Fullscreen tab",
)
replace_once(
    '        .animation(.easeInOut(duration: 0.22), value: scanningApps)',
    '''        .statusBarHidden(selectedDashboardTab == 2 && fullscreenPreviewHidden && !scanningApps)
        .animation(.easeInOut(duration: 0.22), value: scanningApps)''',
    "DuoSDK-only native status bar preview",
)
replace_once(
    '    private var toolsDashboard: some View {',
    r'''    private var fullscreenDashboard: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 12) {
                    Image(systemName: "arrow.up.left.and.arrow.down.right")
                        .font(.system(size: 32, weight: .medium))
                        .foregroundStyle(Color.accentColor)
                        .accessibilityHidden(true)
                    Text("Status bar & fullscreen")
                        .font(.title2.weight(.semibold))
                    Text("Preview the native status bar behaviour in DuoSDK without changing other apps.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 12)
            }
            Section {
                Toggle("Hide status bar in DuoSDK", isOn: $fullscreenPreviewHidden)
            } header: {
                Text("Live preview")
            } footer: {
                Text("Only the Fullscreen tab is affected. Switching tabs restores the status bar. No cache or app executable is modified.")
            }
            Section {
                HStack {
                    Label("Hide status bar in other apps", systemImage: "iphone")
                    Spacer()
                    Text("Unavailable")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                HStack {
                    Label("Remove reserved safe-area space", systemImage: "rectangle.expand.vertical")
                    Spacer()
                    Text("Unavailable")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            } header: {
                Text("Per-app controls")
            } footer: {
                Text("The existing SDK override does not provide a verified status bar or safe-area setting for other apps. These controls are not implemented.")
            }
            Section {
                Button {
                    sampleSelfScene()
                } label: {
                    Label("Inspect current display geometry", systemImage: "viewfinder")
                }
                Text(selfSceneReport)
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
                    .textSelection(.enabled)
            } header: {
                Text("Display diagnostics")
            } footer: {
                Text("Measurements describe DuoSDK's current scene, not other applications.")
            }
        }
        .listStyle(.insetGrouped)
    }

    private var toolsDashboard: some View {''',
    "Fullscreen preview and honest capability status",
)
assert '.tag(2)' in s and 'fullscreenDashboard' in s
assert '.statusBarHidden(selectedDashboardTab == 2 && fullscreenPreviewHidden && !scanningApps)' in s
assert 'DuoSDKMaintenanceForSelection(actualAction, payload)' in s
source.write_text(s, encoding="utf-8")
print("Fullscreen tab: native DuoSDK-only live preview and display diagnostics; no unverified cross-app changes.")
