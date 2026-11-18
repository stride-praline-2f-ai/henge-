#!/usr/bin/env python3
"""Compact DuoSDK settings UI, applied after engine and diagnostic extensions.

The patch intentionally changes only SwiftUI presentation. It does not touch
cache-writing, restore, signing, the sensor reader, or existing recovery logic.
The unverified executable-recovery action is hidden pending diagnosis.
"""
from pathlib import Path
import sys
p = Path(sys.argv[1]).resolve() / "Sources/App.swift"
s = p.read_text()

anchor = '    @State private var confirmInstalledSDKRecovery = false'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + '''
    @State private var showAdvanced = false
    @State private var showRawOutput = false''', 1)

start = s.index('    var body: some View {', s.index('private struct DuoSDKView: View {'))
end = s.index('    private func appRow(_ item: DuoSDKCandidate) -> some View {', start)
body = r'''
    var body: some View {
        NavigationStack {
            List {
                Section {
                    Button {
                        run(0)
                    } label: {
                        Label(candidates.isEmpty ? "Find installed apps" : "Refresh apps",
                              systemImage: "arrow.clockwise")
                    }
                    if !candidates.isEmpty {
                        HStack {
                            Text("\(candidates.count) apps found")
                            Spacer()
                            Text("\(selectedIDs.count) selected")
                                .foregroundStyle(.secondary)
                        }
                        .font(.caption)
                    }
                } footer: {
                    Text("Nothing changes on your phone until you select an app and confirm Apply.")
                }

                if !candidates.isEmpty {
                    Section("Apps") {
                        ForEach(filtered.sorted {
                            $0.name.localizedStandardCompare($1.name) == .orderedAscending
                        }) { item in
                            compactAppRow(item)
                        }
                    }
                }

                if !selectedIDs.isEmpty {
                    Section {
                        Button {
                            confirmApply = true
                        } label: {
                            Label("Apply to \(selectedIDs.count) selected",
                                  systemImage: "checkmark.circle")
                                .fontWeight(.semibold)
                        }
                        .disabled(!canApply)
                        if !canApply {
                            Text("Choose a valid SDK that differs from the current value.")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    } footer: {
                        Text("An SDK adjustment can affect app compatibility. "
                             + "It does not guarantee working rotation or fullscreen.")
                    }
                }

                Section {
                    Button {
                        run(3)
                    } label: {
                        Label("Undo recorded changes", systemImage: "arrow.uturn.backward")
                    }
                } footer: {
                    Text("Undo is available only for changes recorded by this DuoSDK version "
                         + "and still matching the live cache.")
                }

                if !restoreCandidates.isEmpty {
                    Section("Choose changes to undo") {
                        ForEach(restoreCandidates) { item in
                            Toggle(isOn: Binding(
                                get: { restoreIDs.contains(item.id) },
                                set: { isOn in
                                    if isOn { restoreIDs.insert(item.id) }
                                    else { restoreIDs.remove(item.id) }
                                }
                            )) {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(item.name)
                                    Text("\(item.adjustedVersion) → \(item.originalVersion)")
                                        .font(.caption).foregroundStyle(.secondary)
                                }
                            }
                        }
                        Button("Undo \(restoreIDs.count) selected", role: .destructive) {
                            confirmRestore = true
                        }
                        .disabled(restoreIDs.isEmpty)
                    }
                }

                if working {
                    Section {
                        ProgressView("Checking…")
                    }
                } else if !report.isEmpty {
                    Section("Result") {
                        Text(briefResult(report))
                            .font(.callout)
                            .textSelection(.enabled)
                        DisclosureGroup("Technical details", isExpanded: $showRawOutput) {
                            Text(report)
                                .font(.caption.monospaced())
                                .foregroundStyle(.secondary)
                                .textSelection(.enabled)
                        }
                    }
                }

                Section {
                    DisclosureGroup("Advanced & diagnostics", isExpanded: $showAdvanced) {
                        Text("Physical orientation: \(sensorReport)")
                            .font(.caption)
                        Text(selfSceneReport)
                            .font(.caption.monospaced())
                            .textSelection(.enabled)
                        Button("Refresh scene reading") { sampleSelfScene() }
                        Divider()
                        Text("Saved recovery check")
                            .font(.subheadline).fontWeight(.medium)
                        Text(briefResult(heartbeatReport))
                            .font(.caption).foregroundStyle(.secondary)
                        Button("Check recovery records") { checkHeartbeat() }
                        Divider()
                        Text("Test an app's rotation")
                            .font(.subheadline).fontWeight(.medium)
                        if !candidates.isEmpty {
                            Picker("App", selection: $layoutAppID) {
                                Text("Select").tag("")
                                ForEach(candidates.sorted {
                                    $0.name.localizedStandardCompare($1.name) == .orderedAscending
                                }) { item in
                                    Text(item.name).tag(item.id)
                                }
                            }
                            Picker("How it was opened", selection: $layoutPath) {
                                Text("Direct inner launch").tag("Inner display: direct launch")
                                Text("Outer → unfold").tag("Outer landscape: unfold while app open")
                                Text("Return to app").tag("Leave app: return from background")
                                Text("Inner → fold").tag("Inner display: fold closed while app open")
                            }
                            Picker("Result", selection: $layoutResult) {
                                Text("Half-width").tag("Left-half window")
                                Text("Centred bars").tag("Centred portrait bars")
                                Text("Full-width").tag("Full-width correct")
                                Text("Smooth & full-width").tag("Full-width and smooth rotation")
                                Text("Forced portrait").tag("Unexpected forced portrait")
                                Text("Crash").tag("App crashed")
                            }
                            Picker("Rotation Lock", selection: $layoutLock) {
                                Text("Unknown").tag("Unknown")
                                Text("Off").tag("Off")
                                Text("On").tag("On")
                            }
                            Picker("Rotation animation", selection: $rotationAnimation) {
                                Text("Unknown").tag("Unknown")
                                Text("Smooth").tag("Smooth")
                                Text("Abrupt").tag("Abrupt jump")
                                Text("Flicker").tag("Flicker")
                            }
                            Button("Save test") { saveLayoutTrial() }
                                .disabled(layoutAppID.isEmpty)
                        } else {
                            Text("Scan apps to choose one.")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                        if let latest = layoutTrials.first {
                            Text("Latest: \(latest.appName) · \(latest.result)")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                        if !layoutTrials.isEmpty {
                            Button("Clear test notes", role: .destructive) {
                                layoutTrials = []
                                UserDefaults.standard.removeObject(
                                    forKey: "duosdk.layoutTrials.v1")
                            }
                        }
                        Text("Rotation readings cover DuoSDK only. It cannot read "
                             + "or force another app's window orientation.")
                            .font(.caption2).foregroundStyle(.secondary)
                    }
                }
            }
            .searchable(text: $search, prompt: "Search apps")
            .disabled(working)
            .navigationTitle("DuoSDK")
            .confirmationDialog("Apply SDK changes?", isPresented: $confirmApply) {
                Button("Apply to \(selectedIDs.count) selected") { run(1) }
            } message: {
                Text("Changes are experimental and affect the selected apps' "
                     + "LaunchServices metadata. Keep a device backup.")
            }
            .confirmationDialog("Undo selected changes?", isPresented: $confirmRestore) {
                Button("Undo \(restoreIDs.count) selected", role: .destructive) { run(2) }
            } message: {
                Text("The live cache will be revalidated. Changes that cannot "
                     + "be verified will be refused.")
            }
            .onAppear {
                UIDevice.current.beginGeneratingDeviceOrientationNotifications()
                captureRotationSignal()
            }
            .onReceive(NotificationCenter.default.publisher(
                for: UIDevice.orientationDidChangeNotification)) { _ in
                captureRotationSignal()
            }
            .onDisappear {
                UIDevice.current.endGeneratingDeviceOrientationNotifications()
            }
            .task(id: scenePhase) {
                guard scenePhase == .active else { return }
                checkHeartbeat()
                while !Task.isCancelled {
                    do {
                        try await Task.sleep(for: .seconds(180))
                    } catch { break }
                    guard !Task.isCancelled, scenePhase == .active else { break }
                    checkHeartbeat()
                }
            }
        }
    }

    private func compactAppRow(_ item: DuoSDKCandidate) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Toggle(isOn: Binding(
                get: { selectedIDs.contains(item.id) },
                set: { isOn in
                    if isOn { selectedIDs.insert(item.id) }
                    else { selectedIDs.remove(item.id) }
                }
            )) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(item.name)
                        .fontWeight(.medium)
                    Text("Recorded SDK: \(item.fromVersion)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            if selectedIDs.contains(item.id) {
                HStack(spacing: 10) {
                    Text("Set SDK").font(.caption)
                    TextField("27.2.0", text: Binding(
                        get: { target(item) },
                        set: { targets[item.id] = $0 }
                    ))
                    .keyboardType(.numbersAndPunctuation)
                    .textFieldStyle(.roundedBorder)
                    .frame(maxWidth: 110)
                    Spacer()
                    if let saved = savedTargets[item.id] {
                        Text("Saved: \(saved)")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.leading, 4)
            }
        }
        .padding(.vertical, 3)
    }

    private func briefResult(_ raw: String) -> String {
        if raw.contains("Could not verify the installed app's original executable SDK") {
            return "Unable to verify the installed app. Nothing changed. "
                 + "Use Undo recorded changes if available."
        }
        if raw.contains("DUO_BATCH_APLICADO") {
            return "SDK change applied. Restart the affected app to test."
        }
        if raw.contains("DUO_BATCH_REVERTIDO") {
            return "Recorded SDK changes restored."
        }
        if raw.contains("DUOSDK_SELECTION_DATA=") {
            return "App scan complete."
        }
        let first = raw.split(separator: "\n", omittingEmptySubsequences: true).first
        return first.map(String.init) ?? "No result."
    }

'''
s = s[:start] + body + s[end:]

# A dedicated private recovery operation was compiled previously but is
# not advertised while installed-binary validation remains unreliable.
assert 'Stabilise selected:' not in s[start:start+len(body)]
assert 'private func run(_ action: Int)' in s
assert 'private func checkHeartbeat()' in s
assert 'private func captureRotationSignal()' in s
assert 'private func saveLayoutTrial()' in s
p.write_text(s)
print("DuoSDK compact UI: apps, Apply, Undo, compact Result; diagnostics collapsed.")
