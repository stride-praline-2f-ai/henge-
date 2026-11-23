#!/usr/bin/env python3
"""Record validation from the same Actions job after every release check passes."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REQUIRED_STEPS = (
    "sdk", "verify_patch", "integration", "metal_probe", "native_compile",
    "stack_network", "jit_mmu", "memory_devices", "indices_input", "sanitizers",
    "jit_helper", "ios_compile",
)
PATCH_SHA = "f249154cad2513e5bbcb4ab8fb5e38b749c606956d3241929d8bd5b235e482e1"


def record(state, manifest, steps, source, run_id, patch_sha):
    missing = [step for step in REQUIRED_STEPS if steps.get(step, {}).get("outcome") != "success"]
    if missing:
        raise ValueError("Required validation steps did not pass: " + ", ".join(missing))
    if patch_sha != PATCH_SHA or patch_sha != manifest["audit_repairs_sha256"] or patch_sha != state["integrated_patch_sha256"]:
        raise ValueError("Build 125 source inputs do not match the frozen patch")
    if manifest["app_build"] != "125" or state["release_requested"] is not False:
        raise ValueError("Expected a fresh build 125 release request")
    if not re.fullmatch("[0-9a-f]{40}", source) or run_id <= 0:
        raise ValueError("Invalid Actions provenance")
    evidence = f"Exact-source ARM64 native, sanitizer, and complete iOS Release steps passed in Actions run {run_id}."
    for entry in state.values():
        if isinstance(entry, dict) and "source_commit" in entry:
            entry["source_commit"] = source
            if isinstance(entry.get("evidence"), list):
                entry["evidence"].append(evidence)
    state["final_validation"] = dict(
        patch_sha256=patch_sha, source_commit=source, run_id=run_id, native_regressions="passed",
        sanitizers="passed", ios_app_compile="passed",
    )
    state["final_reconciliation_complete"] = True
    state["release_requested"] = True
    state["workstreams"][-1]["state"] = "pending"
    state["release_reconciliation"].update(source_commit=source, native_run_id=run_id, runtime_changes_after_validation=False)
    state["safari_replay_followup"].update(
        patch_sha256=patch_sha, validated_source=source, native_validated_source=source,
        native_validation_run=run_id, validation_run=run_id,
    )
    for name in ("replay_followup", "desktop_interactivity", "cpu_heavy_followup", "sustained_cpu_pass"):
        state[name].update(patch_sha256=patch_sha, native_validation_run=run_id)
    for name in ("replay_followup", "desktop_interactivity", "sustained_cpu_pass"):
        state[name]["focused_validation_run"] = run_id
    state["build_125_recovery"] = dict(
        source_commit=source, patch_sha256=patch_sha, native_validation_run=run_id,
        jit_policy="passed", physical_ipados_helper_attach="pending_device_test",
    )


def main():
    source = os.environ["GITHUB_SHA"]
    branch = os.environ["GITHUB_REF_NAME"]
    if os.environ["GITHUB_RUN_ATTEMPT"] != "1" or branch != "fix/boot-recovery125-alt-mac":
        raise ValueError("Expected the first run on the dedicated release branch")
    manifest = json.loads((ROOT / "manifest.json").read_text())
    if manifest["release_branch"] != branch:
        raise ValueError("Release branch differs from manifest")
    refs = subprocess.check_output(
        ["git", "-C", str(ROOT.parent), "ls-remote", "origin", "refs/heads/" + branch], text=True,
    ).split()
    if refs[:1] != [source]:
        raise ValueError("Source was superseded during validation")
    path = ROOT / "optimization-state.json"
    state = json.loads(path.read_text())
    record(state, manifest, json.loads(os.environ["HENGE_RELEASE_STEPS"]), source,
           int(os.environ["GITHUB_RUN_ID"]), hashlib.sha256((ROOT / "audit-repairs.patch").read_bytes()).hexdigest())
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)
    subprocess.run(["python3", str(ROOT / "check-optimization-gate.py")], check=True)


if __name__ == "__main__":
    main()
