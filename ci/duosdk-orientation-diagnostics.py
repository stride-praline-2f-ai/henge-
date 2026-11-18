#!/usr/bin/env python3
"""DuoSDK orientation / scene regression diagnosis.

Does not edit LaunchServices, force system rotation, or claim access to the
foreground UIWindowScene of other apps. Records user-observed launch states
against already-read SDK values. Shows DuoSDK's own scene/screen geometry to
make the difference between orientation and window shape explicit.
"""
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve() / "Sources"
p = root / "App.swift"
s = p.read_text()

anchor="private struct DuoSDKView: View {"
assert s.count(anchor)==1
types=r'''
private struct DuoLayoutTrial: Codable, Identifiable {
    var id: UUID = UUID()
    var appID: String
    var appName: String
    var recordedSDK: String
    var path: String
    var result: String
    var rotationLock: String
    var rotationAnimation: String?
    var recordedAt: Date
}

'''
s=s.replace(anchor,types+anchor,1)

anchor='''    @State private var heartbeatTime: Date?'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
    @State private var layoutAppID = ""
    @State private var layoutPath = "Inner display: direct launch"
    @State private var layoutResult = "Left-half window"
    @State private var layoutLock = "Unknown"
    @State private var rotationAnimation = "Unknown"
    @State private var selfSceneReport = "No scene geometry sample recorded."
    @State private var layoutTrials: [DuoLayoutTrial] = {
        guard let data = UserDefaults.standard.data(forKey: "duosdk.layoutTrials.v1"),
              let trials = try? JSONDecoder().decode([DuoLayoutTrial].self, from: data)
        else { return [] }
        return Array(trials.prefix(60))
    }()''',1)

anchor='''                if !changedPreferences.isEmpty {'''
assert s.count(anchor)==1
ui=r'''
                Section {
                    Text("A fold transition can resize a running app even when opening "
                         + "that app directly on the inner display gives a narrow window. "
                         + "These tests log what you observe; they cannot read or rotate "
                         + "another app's protected window.")
                        .font(.callout)
                        .foregroundStyle(.secondary)

                    Button("Sample DuoSDK window and orientation") {
                        sampleSelfScene()
                    }
                    Text(selfSceneReport)
                        .font(.caption.monospaced())
                        .textSelection(.enabled)

                    if !candidates.isEmpty {
                        Picker("App to test", selection: $layoutAppID) {
                            Text("Choose app").tag("")
                            ForEach(candidates.sorted { $0.name < $1.name }) { item in
                                Text(item.name).tag(item.id)
                            }
                        }
                        Picker("Launch / transition", selection: $layoutPath) {
                            Text("Inner: direct launch").tag("Inner display: direct launch")
                            Text("Outer landscape → unfold").tag("Outer landscape: unfold while app open")
                            Text("Leave app → return").tag("Leave app: return from background")
                            Text("Inner → fold closed").tag("Inner display: fold closed while app open")
                        }
                        Picker("Window result", selection: $layoutResult) {
                            Text("Left-half window").tag("Left-half window")
                            Text("Centred portrait bars").tag("Centred portrait bars")
                            Text("Full-width correct").tag("Full-width correct")
                            Text("Full-width and smooth rotation").tag("Full-width and smooth rotation")
                            Text("Unexpected forced portrait").tag("Unexpected forced portrait")
                            Text("App crashed").tag("App crashed")
                        }
                        Picker("Rotation Lock", selection: $layoutLock) {
                            Text("Unknown").tag("Unknown")
                            Text("Off in Control Centre").tag("Off")
                            Text("On in Control Centre").tag("On")
                        }
                        Picker("Rotation animation", selection: $rotationAnimation) {
                            Text("Unknown").tag("Unknown")
                            Text("Smooth animated rotation").tag("Smooth")
                            Text("Abrupt jump / no animation").tag("Abrupt jump")
                            Text("Flicker / multiple resizes").tag("Flicker")
                        }
                        Button("Save this observation") { saveLayoutTrial() }
                            .disabled(layoutAppID.isEmpty)
                    } else {
                        Text("Scan recognised apps first to select Roblox, Ring or another app.")
                            .font(.caption).foregroundStyle(.secondary)
                    }

                    if !layoutTrials.isEmpty {
                        ForEach(Array(layoutTrials.prefix(6))) { trial in
                            VStack(alignment: .leading, spacing: 3) {
                                Text(trial.appName).fontWeight(.medium)
                                Text("\(trial.path) · \(trial.result)")
                                    .font(.caption)
                                Text("Recorded SDK \(trial.recordedSDK), rotation lock \(trial.rotationLock), animation \(trial.rotationAnimation ?? "not recorded")")
                                    .font(.caption2).foregroundStyle(.secondary)
                            }
                        }
                        Button("Clear saved orientation observations", role: .destructive) {
                            layoutTrials = []
                            UserDefaults.standard.removeObject(forKey: "duosdk.layoutTrials.v1")
                        }
                    }

                    if layoutTrials.contains(where: { good in
                        good.path == "Outer landscape: unfold while app open" &&
                        (good.result == "Full-width correct" ||
                         good.result == "Full-width and smooth rotation") &&
                        layoutTrials.contains(where: { bad in
                            bad.appID == good.appID &&
                            bad.path == "Inner display: direct launch" &&
                            bad.result != "Full-width correct" &&
                            bad.result != "Full-width and smooth rotation"
                        })
                    }) {
                        Text("A fold-transition success alongside a direct-launch failure "
                             + "is evidence of a scene/window-initialisation difference, "
                             + "not evidence that the saved SDK value reverted. "
                             + "Do not reapply an unchanged SDK.")
                            .font(.callout)
                    }

                    if layoutTrials.contains(where: {
                        $0.result == "Full-width and smooth rotation"
                    }) && layoutTrials.contains(where: {
                        $0.result == "Left-half window" ||
                        $0.result == "Centred portrait bars" ||
                        $0.result == "Unexpected forced portrait"
                    }) {
                        Text("Some apps rotate normally while others do not. " +
                             "Compare the same rotation-lock setting and launch path " +
                             "before blaming global Rotation Lock. App-specific " +
                             "scene handling is a stronger hypothesis.")
                            .font(.callout)
                    }

                    if layoutTrials.contains(where: { $0.rotationAnimation == "Abrupt jump" }) &&
                       layoutTrials.contains(where: { $0.rotationAnimation == "Smooth" }) {
                        Text("Some apps rotate smoothly and others abruptly. This supports an " +
                             "app-specific scene/compatibility difference, not a proven " +
                             "system-wide Rotation Lock failure.")
                            .font(.callout)
                    }
                    Text("Rotation Lock is user-reported: iOS does not offer a public API "
                         + "for third-party apps to read the global Control Centre lock. "
                         + "On the inner display, orientation and window aspect ratio "
                         + "are not interchangeable.")
                        .font(.caption).foregroundStyle(.secondary)
                } header: {
                    Text("Fold and rotation diagnostics")
                } footer: {
                    Text("Read-only system measurements and local test notes. "
                         + "No background monitoring of other apps, app relaunch, "
                         + "rotation override, or cache modification.")
                }
'''
s=s.replace(anchor,ui+anchor,1)

anchor='''    private func checkHeartbeat() {'''
assert s.count(anchor)==1
methods=r'''
    private func sampleSelfScene() {
        guard let scene = UIApplication.shared.connectedScenes
            .compactMap({ $0 as? UIWindowScene })
            .first(where: { $0.activationState == .foregroundActive })
        else {
            selfSceneReport = "No active DuoSDK UIWindowScene. No change made."
            return
        }
        let bounds = scene.coordinateSpace.bounds
        let screen = scene.screen.bounds
        let appOrientation: String
        switch scene.interfaceOrientation {
        case .portrait: appOrientation = "portrait"
        case .portraitUpsideDown: appOrientation = "portrait upside down"
        case .landscapeLeft: appOrientation = "landscape left"
        case .landscapeRight: appOrientation = "landscape right"
        default: appOrientation = "unknown"
        }
        // Layout dimensions are the truth for an app's visible UI. The window
        // can be tall even when the device's physical orientation is landscape.
        selfSceneReport = String(format:
            "DuoSDK scene: %.0f × %.0f pt\nScene screen: %.0f × %.0f pt\nScene orientation: %@\nNo other app's scene is accessible.",
            bounds.width, bounds.height, screen.width, screen.height, appOrientation)
    }

    private func saveLayoutTrial() {
        guard let candidate = candidates.first(where: { $0.id == layoutAppID }) else { return }
        layoutTrials.insert(DuoLayoutTrial(
            appID: candidate.id, appName: candidate.name,
            recordedSDK: candidate.fromVersion,
            path: layoutPath, result: layoutResult,
            rotationLock: layoutLock, rotationAnimation: rotationAnimation, recordedAt: Date()), at: 0)
        layoutTrials = Array(layoutTrials.prefix(60))
        if let data = try? JSONEncoder().encode(layoutTrials) {
            UserDefaults.standard.set(data, forKey: "duosdk.layoutTrials.v1")
        }
    }

'''
s=s.replace(anchor,methods+anchor,1)

# Diagnosis must not force an SDK re-apply. The existing user-confirmed manual
# Apply operation is unchanged and must continue to reject unchanged targets.
assert 'if action == 1 && !canApply' in s
assert 'DuoSDKMaintenanceForSelection(4, "[]")' in s
p.write_text(s)
print("Read-only fold/scene geometry and user-observed rotation diagnostics added; no system writes.")
