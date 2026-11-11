#!/usr/bin/env python3
"""Reconcile verified upstream main changes with the custom two-port Metal engine.

Never silently discard a new Henge feature or initialize two competing copies.
The upstream Instant Resume PVG state and optional VBLANK handler used the
single-display fields removed by custom Henge Link; preserve BOTH ports.
The former GPU shader-dump path referred to an iOS17 relabel stage removed
by the custom iOS27 exact-byte library cache. Keep explicit dump only.
Fail closed when upstream changes a source pattern unexpectedly.
"""
from pathlib import Path
import sys
import json
import subprocess

root=Path(sys.argv[1])
def replace_once(code, before, after, context):
    count=code.count(before)
    if count!=1:
        raise SystemExit(f"Source integration mismatch in {context}: expected 1 exact match, got {count}: {before!r}")
    return code.replace(before,after,1)

lite=root/"devices/pvg_lite.c"
s=lite.read_text()
s=replace_once(s,
    "if (!on || !p->display_pa) return;\n    uint8_t *d = hv_phys_ptr(p->m, p->display_pa, 0x4000);",
    "if (!on) return;\n    uint8_t *d = hv_pvg_lite_display_page_for_port(p, 0);",
    "optional 60Hz vblank timing uses primary display")
s=replace_once(s,
    "uint64_t display_pa, swaps;",
    "HvPvgDisplayState displays[HV_PVG_DISPLAY_PORTS];\n    uint32_t display_count, display_pending;",
    "Instant Resume snapshot includes both display ports")
s=replace_once(s,
    "s->display_pa = p->display_pa, s->swaps = p->swaps;",
    "memcpy(s->displays, p->displays, sizeof s->displays);\n    s->display_count = p->display_count;\n    s->display_pending = p->display_pending;",
    "Snapshot captures both display ports")
s=replace_once(s,
    "if (len != sizeof(PvgState)) return -1;\n    const PvgState *s = in;",
    "if (len != sizeof(PvgState)) return -1;\n    const PvgState *s = in;\n    if (!s->display_count || s->display_count > HV_PVG_DISPLAY_PORTS) return -1;",
    "Snapshot validates display counts")
s=replace_once(s,
    "p->display_pa = s->display_pa, p->swaps = s->swaps;",
    "memcpy(p->displays, s->displays, sizeof p->displays);\n    p->display_count = s->display_count;\n    p->display_pending = s->display_pending;\n    /* Never resurrect a stale network viewer after restoring guest RAM. */\n    if (p->display_count > 1) p->displays[1].connected = 0;",
    "Snapshot restores both display ports")
s=replace_once(s,
    "const uint8_t *d = p->display_pa ? hv_phys_ptr(p->m, p->display_pa, 0x4000) : NULL;",
    "const uint8_t *d = hv_pvg_lite_display_page_for_port(p, 0);",
    "Debug display page uses primary port")
s=replace_once(s,
    "(void *)atomic_load(&p->metal), (unsigned long long)p->swaps);",
    "(void *)atomic_load(&p->metal), (unsigned long long)p->displays[0].swaps);",
    "Debug swap count uses primary port")
for forbidden in ("p->display_pa","p->swaps","s->display_pa","s->swaps"):
    if forbidden in s: raise SystemExit("Stale single-display state: "+forbidden)
lite.write_text(s)

metal=root/"devices/pvg_metal.m"
s=metal.read_text()
s=replace_once(s,
    "        static int relabelled_kept = 0;\n",
    "",
    "Do not retain counters for the removed iOS17 relabel path")
s=replace_once(s,
    "int keep = sd ? atoi(sd) != 0 : loaded_at > 0 && relabelled_kept < 48;",
    "int keep = sd && atoi(sd) != 0;",
    "Only dump shaders on explicit request")
s=replace_once(s,
    "        if (keep && !sd) relabelled_kept++;\n",
    "",
    "No redundant iOS17 automatic shader dump")
for forbidden in ("loaded_at", "gpu_busy_ns", "gpu_last_end", "commit_time"):
    if forbidden in s: raise SystemExit("Stale GPU code from overlapping features: "+forbidden)
# Import only the three upstream GPU quiesce/display snapshot entrypoints.
# The custom renderer already owns Metal replay, cache, display and touch paths,
# so never import another renderer implementation or duplicate a symbol.
manifest = json.loads((Path(__file__).with_name("manifest.json")).read_text())
upstream = manifest["upstream_integration"]["main_sha"]
original = subprocess.check_output(
    ["git", "-C", str(root), "show", f"{upstream}:devices/pvg_metal.m"], text=True)
anchor = "@interface HvReplay (Resume)"
assert original.count(anchor) == 1, "unexpected upstream snapshot boundary"
resume = original[original.index(anchor):]
required = [
    "void hv_pvg_metal_quiesce(",
    "size_t hv_pvg_metal_display_state(",
    "void hv_pvg_metal_set_display_state(",
]
for name in required:
    if original.count(name) != 1: raise SystemExit("Unexpected upstream snapshot function count: " + name)
    if name in s: raise SystemExit("Duplicate snapshot implementation: " + name)
if "static void vblank(" in resume:
    raise SystemExit("Unexpected foreign GPU logic in upstream snapshot segment")
s += "\n/* Pinned upstream Instant Resume entrypoints, adapted by the custom engine without a second replay. */\n" + resume
metal.write_text(s)

# Integrate the upstream pause lifecycle with the fork's existing ticker,
# audio device and explicit CPU0 shutdown. Do not spawn duplicate workers.
vm=root/"host/vm.c"
t=vm.read_text()
t=replace_once(t,"void hv_vm_link_flap(void) {","int hv_vm_paused(void);\nvoid hv_vm_link_flap(void) {","forward-declare pause state before network callback")
t=replace_once(t,"int hv_vm_paused(void);\nstatic void set_pause_state(int v) {","static void set_pause_state(int v) {","remove now redundant pause declaration")
t=replace_once(t,"if (kicker_started) pthread_join(kicker, NULL);","hv_idle_ticker_advance(&kicker);\n    if (kicker_started) pthread_join(kicker_handle, NULL);","wake and join custom idle ticker during suspend")
t=replace_once(t,"if (sound_on) hv_audio_detach(); /* the host\u0027s player stops; the stream\u0027s state stays in the device */","/* hv_vm_run_cpu0 already detached board.snd under the device lock. */","do not double-detach audio at pause")
for dead in ("pthread_join(kicker, NULL)", "if (sound_on) hv_audio_detach();"):
    if dead in t: raise SystemExit("Unreconciled suspend lifecycle: "+dead)
# One-shot failure diagnostics for the upstream pause handshake.
# No new threads, polling loops or runtime options.
t=replace_once(t,
    "if (!all_saving()) return -1;",
    "if (!all_saving()) {\n        fprintf(stderr, \"hengevm: suspend rejected: non-SAVE halt; cpus=%d\\n\", ncpus);\n        for (int i=0;i<ncpus;i++) fprintf(stderr, \"hengevm: suspend cpu[%d] halted=%d pc=%llx\\n\", i, atomic_load(&cpus[i].halted), (unsigned long long)cpus[i].pc);\n        return -1;\n    }",
    "debug only the failed all-CPU-save handshake")
t=replace_once(t,
    "if (run_ended) {\n        pthread_mutex_unlock(&pause_mu);",
    "if (run_ended) {\n        fprintf(stderr, \"hengevm: suspend rejected: CPU0 run already ended\\n\");\n        pthread_mutex_unlock(&pause_mu);",
    "diagnose early stop before suspend")
# Diagnose the unexpected stop BEFORE the pause request is processed.
# Logging only; no control-flow or QoS changes.
t=replace_once(t,
    "int r = hv_vm_run_cpu0();",
    "int r = hv_vm_run_cpu0();\n    fprintf(stderr, \"hengevm: cpu0 exited: reason=%d halt=%d pc=0x%llx exit_req=%d\\n\", r, atomic_load(&cpus[0].halted), (unsigned long long)cpus[0].pc, __atomic_load_n(&cpus[0].exit_req, __ATOMIC_RELAXED));",
    "trace the VM CPU0 return preceding failed suspend")
# A new VM must clear the run_ended flag from any prior guest session.
# This flag is used by suspend() to reject a truly dead CPU 0.
start=t.index("int hv_vm_start(int cpu0, void (*on_exit)(int reason))")
end=t.find("\nfailed:",start)
if start<0 or end<0: raise SystemExit("Unexpected VM start function layout")
start_fn=t[start:end]
# The upstream VM's CPU0 owner flag was lost because the fork inserted
# its scheduler policy in the same merge hunk as the new upstream assignment.
# Without this, "Continue" restarts with cpu0=0, leaving the resumed Mac idle,
# and the next Suspend waits forever for a CPU0 thread that does not exist.
if "cpu0_ours = cpu0;" not in start_fn:
    t=replace_once(t,"    exit_cb = on_exit;\n",
        "    exit_cb = on_exit;\n    cpu0_ours = cpu0;\n",
        "retain CPU0 thread ownership across suspend/continue")
    start_fn=t[start:t.find("\nfailed:",start)]
if start_fn.count("cpu0_ours = cpu0;")!=1:
    raise SystemExit("Missing or duplicated CPU0 ownership assignment in merged VM")
if "run_ended = 0;" not in start_fn:
    t=replace_once(t, "    exit_cb = on_exit;\n",
                   "    exit_cb = on_exit;\n    pthread_mutex_lock(&pause_mu);\n    run_ended = 0;\n    pthread_mutex_unlock(&pause_mu);\n",
                   "reset prior-session CPU0 end marker on every new VM start")
t=replace_once(t, "    run_ended = 1;\n    if (pause_state == 1)",
               "    fprintf(stderr, \"hengevm: CPU0 exit before pause: reason=%d halt=%d pc=%llx pause_state=%d\\n\", r, atomic_load(&cpus[0].halted), (unsigned long long)cpus[0].pc, pause_state);\n    run_ended = 1;\n    if (pause_state == 1)",
               "diagnose genuine guest CPU exit before pause")
vm.write_text(t)

# The custom VM header adds ticker diagnostics exactly where upstream added
# Instant Resume declarations. The automatic 3-way merge retained the ticker
# declaration but lost the pause APIs. Install the complete upstream block,
# including snapshot counter and network helpers, not hand-written stubs.
header=root/"host/vm.h"
h=header.read_text()
upstream_header=subprocess.check_output(
    ["git","-C",str(root),"show",f"{upstream}:host/vm.h"],text=True)
start="/* Instant resume (see snapshot.h)."
end="void hv_vm_flush_disks(void);"
if upstream_header.count(start)!=1 or upstream_header.count(end)!=1:
    raise SystemExit("Unexpected pinned upstream VM header layout")
api=upstream_header[upstream_header.index(start):upstream_header.index(end)]
if "int hv_vm_pause(void);" not in h:
    h=replace_once(h,"void hv_vm_log_ticker(void);",
        "void hv_vm_log_ticker(void);\n"+api.rstrip(),
        "restore complete Instant Resume API on custom VM header")
for name in ("int hv_vm_pause(void);","int hv_vm_finish_pause(void);",
             "int hv_vm_paused(void);","int hv_vm_continue(void);",
             "int hv_vm_pause_clean(void);","void hv_vm_link_flap(void);"):
    if h.count(name)!=1: raise SystemExit("Missing or duplicate pause API: "+name)
header.write_text(h)
# Build upstream Instant Resume with one VM and one renderer in all targets.
makefile=root/"Makefile"
m=makefile.read_text()
m=replace_once(m,"host/scheduling.c host/vm.c host/net_slirp.c",
               "host/scheduling.c host/vm.c host/snapshot.c host/net_slirp.c",
               "include real snapshot module in iOS static archive")
assert m.count("$(B)/vm.o $(B)/usb_host.o")==2, "unexpected CLI targets"
m=m.replace("$(B)/vm.o $(B)/usb_host.o",
            "$(B)/vm.o $(B)/snapshot.o $(B)/usb_host.o")
m=replace_once(m,"$(B)/vm.o $(B)/audio_mac.o",
               "$(B)/vm.o $(B)/snapshot.o $(B)/audio_mac.o",
               "link snapshot implementation into lifecycle tests")
m=replace_once(m,"-lz -framework Foundation -framework CFNetwork",
               "-lz -lcompression -framework Foundation -framework CFNetwork",
               "include Compression in Henge CLI link")
m=replace_once(m,"$(METAL_LIBS) -framework AudioToolbox -o $@",
               "$(METAL_LIBS) -framework AudioToolbox -lcompression -o $@",
               "include Compression in lifecycle test link")
makefile.write_text(m)


# PR #108 (Duo inner screen / optional status strip) is adapted to the
# fork's better source-of-truth, GuestScreenSize and key-window viewport.
# Its default remains full-screen. No second screen-fit setting or boot
# path: the selected Fit preset already recomputes at launch.
hardware=root/"ios/Henge/Hardware.swift"
h=hardware.read_text()
constants=[]
if "static var largeScreen:" not in h:
    constants.append("    static var largeScreen: Bool { !isPad && min(displayViewport.width, displayViewport.height) >= 600 }")
for name,value in (("sideStrip","84"),("sideStripCentre","47.5"),("sideStripTop","114")):
    if f"static let {name}:" not in h:
        constants.append(f"    static let {name}: CGFloat = {value}")
if constants:
    h=replace_once(h,"enum Device {\n","enum Device {\n"+ "\n".join(constants)+"\n",
                   "one dynamic Duo-screen policy with status-strip geometry")
for name in ("largeScreen","sideStrip","sideStripCentre","sideStripTop"):
    if h.count(f"static var {name}:") + h.count(f"static let {name}:") != 1:
        raise SystemExit("Duplicate or missing Device member: "+name)
# Upstream PR108's fittedForStart API needs this name. Reuse the fork's
# dynamic GuestScreenSize calculation; do not add a second fixed-size fit.
if "static func fitting(for mac:" not in h:
    h=replace_once(h,"enum Device {\n",
        "enum Device {\n    static func fitting(for mac: VirtualMac) -> (width: Int, height: Int) {\n"
        "        let size = mac.displaySize(in: displayViewport)\n"
        "        return (size.width, size.height)\n"
        "    }\n",
        "map upstream fittedForStart to existing dynamic viewport source")
if h.count("static func fitting(for mac:")!=1:
    raise SystemExit("Duplicate or missing Duo fitting entrypoint")
hardware.write_text(h)

machines=root/"ios/Henge/Machines.swift"
mm=machines.read_text()
if "var fillScreen: Bool?" not in mm:
    mm=replace_once(mm,"    var fitScreen: Bool?\n",
        "    var fitScreen: Bool?\n    var fillScreen: Bool?\n",
        "optional Duo strip preference in saved Mac model")
mm=replace_once(mm,"if fitsDeviceScreen { return GuestScreenSize.fitting(in: viewport) }",
    "if fitsDeviceScreen {\n"
    "            var area = viewport\n"
    "            if Device.largeScreen && !(fillScreen ?? true) {\n"
    "                if area.width >= area.height { area.width -= Device.sideStrip }\n"
    "                else { area.height -= Device.sideStrip }\n"
    "            }\n"
    "            return GuestScreenSize.fitting(in: area)\n"
    "        }",
    "single dynamic Fit mode calculates optional Duo side strip at boot")
machines.write_text(mm)

session=root/"ios/Henge/SessionView.swift"
sv=session.read_text()
sv=replace_once(sv,
    "centre: zoomCentre, aspect: displayAspect)",
    "centre: zoomCentre, aspect: displayAspect,\n"
    "                                strip: Device.largeScreen && !(mac.fillScreen ?? true) ? Device.sideStrip : 0)",
    "Pass Duo strip to one source-of-truth layout for display and touch")
sv=replace_once(sv,
    "private var onLargeScreen: Bool { !Device.isPad && horizontalSize == .regular && verticalSize == .regular }",
    "private var onLargeScreen: Bool { Device.largeScreen }",
    "Observe physical window viewport rather than conflicting size-class state")
if "horizontalSize" in sv or "verticalSize" in sv:
    raise SystemExit("Stale size-class based Duo display activation")
session.write_text(sv)

settings=root/"ios/Henge/MacSettingsView.swift"
ms=settings.read_text()
if 'Toggle("Fill the whole screen"' not in ms:
    start=ms.find('Picker("Screen"')
    if start<0: raise SystemExit("Screen selection settings not found")
    pos=ms.find("                        .pickerStyle(.segmented)\n",start)
    if pos<0: raise SystemExit("Expected segmented Screen picker not found")
    pos+=len("                        .pickerStyle(.segmented)\n")
    option=(
        '                        if Device.largeScreen {\n'
        '                            Toggle("Fill the whole screen", isOn: Binding(get: { mac.fillScreen ?? true }, set: { value in\n'
        '                                mac.fillScreen = value\n'
        '                                save()\n'
        '                            }))\n'
        '                            Text("Off leaves room beside the Mac for the status bar and controls. Fit adapts to the current Duo screen when the Mac starts.")\n'
        '                                .font(.system(size: 13)).foregroundStyle(Desk.dim)\n'
        '                        }\n')
    ms=ms[:pos]+option+ms[pos:]
settings.write_text(ms)
print("PASS Duo PR #108 integrated into existing dynamic Fit and touch geometry; single activation toggle")

print("PASS custom/upstream reconciliation: dual-port GPU snapshots, VM pause APIs and lifecycle")
