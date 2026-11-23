#!/usr/bin/env python3
"""Verify the additional build 125 source and fixture patches before applying them."""
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def verified_patches():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    hashes = manifest["release_followups"]
    paths = []
    for name, expected in hashes.items():
        if Path(name).name != name or not name.endswith(".patch"):
            raise ValueError(f"Invalid release follow-up path {name}")
        path = ROOT / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Release follow-up digest mismatch: {name}")
        paths.append(path)
    return paths, hashes


if __name__ == "__main__":
    tree = Path(sys.argv[1]).resolve()
    patches, hashes = verified_patches()
    for patch in patches:
        subprocess.run(["git", "-C", str(tree), "apply", "--check", str(patch)], check=True)
        subprocess.run(["git", "-C", str(tree), "apply", str(patch)], check=True)
    plist = tree / "ios/Henge/Info.plist"
    info = plistlib.loads(plist.read_bytes())
    info["HengeReleaseFollowupsSHA256"] = hashes
    plist.write_bytes(plistlib.dumps(info))
