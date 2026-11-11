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
# Carry the pinned upstream GPU quiesce and display-snapshot implementation
# forward. These methods must actually copy GPU-owned objects to guest RAM:
# placeholder implementations would corrupt Instant Resume after a save.
resume=Path(__file__).with_name("metal-resume-integration.m").read_text()
for symbol in ("void hv_pvg_metal_quiesce(", "size_t hv_pvg_metal_display_state(", "void hv_pvg_metal_set_display_state("):
    if symbol in s or resume.count(symbol)!=1:
        raise SystemExit("Conflicting or missing Metal Instant Resume implementation: "+symbol)
s += "\n" + resume
metal.write_text(s)
print("PASS custom/upstream reconciliation: two-port PVG state, one GPU timing path, upstream resume methods")
