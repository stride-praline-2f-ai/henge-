#!/usr/bin/env bash
# Integrate reviewed upstream source after the original 0.3-based custom patch.
# This is reproducible: all input commit hashes are pinned in manifest.json.
set -euo pipefail
root="${GITHUB_WORKSPACE:-$PWD}"
source_dir="$root/Henge"
manifest="$root/build-request/henge-build/manifest.json"
if [ ! -e "$source_dir/.git" ] || [ ! -f "$manifest" ]; then
  echo "Missing checked-out Henge or manifest" >&2
  exit 1
fi
export GIT_AUTHOR_NAME='Henge CI'
export GIT_AUTHOR_EMAIL='henge-ci@users.noreply.github.com'
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
pins=()
while IFS= read -r entry; do pins+=("$entry"); done < <(python3 - "$manifest" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
i = m["upstream_integration"]
print(i["source_base_sha"])
print(i["main_sha"])
for pr in i["pull_requests"]:
    print(f'{pr["number"]}:{pr["sha"]}')
PY
)
base="${pins[0]}"
upstream="${pins[1]}"
git -C "$source_dir" cat-file -e "$base^{commit}"
if [ -f "$source_dir/.git/shallow" ]; then
  git -C "$source_dir" fetch --no-tags --unshallow origin main
else
  git -C "$source_dir" fetch --no-tags origin main
fi
git -C "$source_dir" cat-file -e "$upstream^{commit}"
git -C "$source_dir" merge-base --is-ancestor "$base" "$upstream" || {
  echo "Pinned source is not an ancestor of upstream main" >&2
  exit 1
}
echo "::group::Integrate pinned Henge main commits"
echo "Applying upstream: $upstream"
# The custom iOS 27 Metal replay intentionally removed the old iOS-17-only
# relabel hook. Upstream now modifies those two files; a modify/delete conflict
# is expected. Resolve ONLY that exact, reviewed conflict by keeping the custom
# removal. Any additional unresolved path aborts the build rather than guessing.
if ! git -C "$source_dir" merge --no-edit --no-ff -X ours "$upstream"; then
  unresolved="$(git -C "$source_dir" diff --name-only --diff-filter=U)"
  expected_unresolved="$(printf 'devices/metallib.c\ndevices/metallib.h')"
  if [ "$unresolved" != "$expected_unresolved" ]; then
    echo "Unreviewed upstream merge conflicts:" >&2
    printf '%s\n' "$unresolved" >&2
    exit 1
  fi
  git -C "$source_dir" rm -- devices/metallib.c devices/metallib.h
  test -z "$(git -C "$source_dir" diff --name-only --diff-filter=U)"
  git -C "$source_dir" -c user.name="$GIT_AUTHOR_NAME" -c user.email="$GIT_AUTHOR_EMAIL" commit --no-edit
  echo "Intentional iOS 27 renderer choice: old iOS-17 relabel files remain removed."
fi
git -C "$source_dir" merge-base --is-ancestor "$upstream" HEAD
echo "::endgroup::"
for entry in "${pins[@]:2}"; do
  no="${entry%%:*}"
  expected="${entry#*:}"
  echo "::group::Integrate reviewed PR #$no at $expected"
  git -C "$source_dir" fetch --no-tags origin "refs/pull/$no/head"
  found="$(git -C "$source_dir" rev-parse FETCH_HEAD)"
  if [ "$found" != "$expected" ]; then
    echo "PR #$no moved after review: expected $expected, got $found" >&2
    exit 1
  fi
  git -C "$source_dir" merge --no-edit --no-ff -X ours "$expected"
  git -C "$source_dir" merge-base --is-ancestor "$expected" HEAD
  echo "::endgroup::"
done
python3 "$root/build-request/henge-build/reconcile-source.py" "$source_dir"
python3 - "$root/build-request/henge-build/audit-repairs.patch" "$manifest" "$source_dir" <<'PYREPAIR'
import hashlib, json, subprocess, sys
from pathlib import Path
patch=Path(sys.argv[1]); manifest=json.loads(Path(sys.argv[2]).read_text())
assert hashlib.sha256(patch.read_bytes()).hexdigest() == manifest['audit_repairs_sha256'], 'Unreviewed audit repair patch'
subprocess.run(['git','-C',sys.argv[3],'apply','--check',str(patch)],check=True)
subprocess.run(['git','-C',sys.argv[3],'apply',str(patch)],check=True)
PYREPAIR
python3 - "$source_dir/ios/Henge/Info.plist" "$manifest" <<'PY'
import json, plistlib, sys
from pathlib import Path
path=Path(sys.argv[1])
i=json.loads(Path(sys.argv[2]).read_text())["upstream_integration"]
with path.open("rb") as f: p=plistlib.load(f)
p["HengeAuditRepairsSHA256"]=json.loads(Path(sys.argv[2]).read_text())["audit_repairs_sha256"]
p["HengeSnapshotSchema"]=3
p["HengeMergedUpstreamCommit"]=i["main_sha"]
p["HengeIntegratedPullRequests"]=[int(x["number"]) for x in i["pull_requests"]]
p["HengeIntegratedPullRequestHeads"]=[str(x["sha"]) for x in i["pull_requests"]]
with path.open("wb") as f: plistlib.dump(p,f)
PY
echo "Integrated upstream and selected PR heads:"
git -C "$source_dir" --no-pager log -1 --oneline
git -C "$source_dir" --no-pager status --short
