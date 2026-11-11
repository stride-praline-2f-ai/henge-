#!/usr/bin/env bash
# Integrate reviewed upstream source after the original 0.3-based custom patch.
# This is reproducible: all input commit hashes are pinned in manifest.json.
set -euo pipefail
root="${GITHUB_WORKSPACE:-$PWD}"
source_dir="$root/Henge"
manifest="$root/build-request/henge-build/manifest.json"
if [ ! -d "$source_dir/.git" ] || [ ! -f "$manifest" ]; then
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
echo "::group::Integrate 22 newer Henge main commits"
echo "Applying upstream: $upstream"
git -C "$source_dir" merge --no-edit --no-ff -X ours "$upstream"
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
python3 - "$source_dir/ios/Henge/Info.plist" "$manifest" <<'PY'
import json, plistlib, sys
from pathlib import Path
path=Path(sys.argv[1])
i=json.loads(Path(sys.argv[2]).read_text())["upstream_integration"]
with path.open("rb") as f: p=plistlib.load(f)
p["HengeMergedUpstreamCommit"]=i["main_sha"]
p["HengeIntegratedPullRequests"]=[int(x["number"]) for x in i["pull_requests"]]
p["HengeIntegratedPullRequestHeads"]=[str(x["sha"]) for x in i["pull_requests"]]
with path.open("wb") as f: plistlib.dump(p,f)
PY
echo "Integrated upstream and selected PR heads:"
git -C "$source_dir" --no-pager log -1 --oneline
git -C "$source_dir" --no-pager status --short
