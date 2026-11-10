#!/bin/bash
# User-local tools: no Homebrew, sudo, system PATH edits, or other app builds.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.cargo/bin:$PATH"
export HOMEBREW_NO_AUTO_UPDATE=1
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
    echo 'Henge IPA builds require arm64 macOS with full Xcode installed.' >&2
    exit 1
fi
task_tools="$HOME/Library/Caches/HengeCI/tools-v1"
mkdir -p "$task_tools/bin" "$task_tools/downloads"
export PATH="$task_tools/bin:$task_tools/python/bin:$PATH"
# Reuse existing tools; otherwise use pinned Python-distributed tool binaries.
if ! command -v cmake >/dev/null || ! command -v meson >/dev/null || ! command -v ninja >/dev/null; then
    python3 -m venv "$task_tools/python"
    "$task_tools/python/bin/python3" -m pip install --disable-pip-version-check --only-binary=:all: \
        cmake==3.31.6 meson==1.7.2 ninja==1.11.1.4
fi
task_fetch() {
    local task_url="$1" task_file="$2" task_sha="$3"
    if [[ ! -s "$task_file" ]] || [[ "$(shasum -a 256 "$task_file" | cut -d ' ' -f1)" != "$task_sha" ]]; then
        curl --proto '=https' --tlsv1.2 -fL --retry 3 --connect-timeout 30 --max-time 600 "$task_url" -o "$task_file.part"
        echo "$task_sha  $task_file.part" | shasum -a 256 -c -
        mv "$task_file.part" "$task_file"
    fi
}
if ! command -v xcodegen >/dev/null; then
    task_fetch https://github.com/yonaskolb/XcodeGen/releases/download/2.44.1/xcodegen.zip \
        "$task_tools/downloads/xcodegen-2.44.1.zip" a2e905fb68446e9bb4008cdfe2e13e3f176d0cbcca828b71770f8e53fca91b73
    ditto -x -k "$task_tools/downloads/xcodegen-2.44.1.zip" "$task_tools/downloads/xcodegen-2.44.1"
    ditto "$task_tools/downloads/xcodegen-2.44.1/xcodegen/bin" "$task_tools/bin"
    ditto "$task_tools/downloads/xcodegen-2.44.1/xcodegen/share" "$task_tools/share"
    chmod +x "$task_tools/bin/xcodegen"
fi
if ! command -v pkg-config >/dev/null; then
    task_fetch https://distfiles.dereferenced.org/pkgconf/pkgconf-2.3.0.tar.xz \
        "$task_tools/downloads/pkgconf-2.3.0.tar.xz" 3a9080ac51d03615e7c1910a0a2a8df08424892b5f13b0628a204d3fcce0ea8b
    tar -xf "$task_tools/downloads/pkgconf-2.3.0.tar.xz" -C "$task_tools/downloads"
    ( cd "$task_tools/downloads/pkgconf-2.3.0"
      ./configure --prefix="$task_tools" --disable-shared --disable-tests
      make -j4
      make install )
    ln -sf pkgconf "$task_tools/bin/pkg-config"
fi
if ! command -v rustup >/dev/null; then
    task_rust_installer="$(mktemp -t henge-rustup)"
    trap 'rm -f "$task_rust_installer"' EXIT
    curl --proto '=https' --tlsv1.2 -fL --retry 3 https://sh.rustup.rs -o "$task_rust_installer"
    sh "$task_rust_installer" -y --profile minimal --no-modify-path
    rm -f "$task_rust_installer"
    trap - EXIT
fi
if ! rustup show active-toolchain; then rustup default stable; fi
rustup target add aarch64-apple-ios
xcodebuild -version
xcrun --sdk iphoneos --show-sdk-path
xcrun --sdk iphoneos --find clang
xcrun --sdk iphoneos --find swiftc
if ! xcrun --sdk iphoneos metal --version; then xcodebuild -downloadComponent MetalToolchain; fi
xcrun --sdk iphoneos metal --version
for task_tool in codesign zip rsync python3 cmake xcodegen meson ninja pkg-config cargo; do
    command -v "$task_tool"
done
cmake --version
xcodegen --version
meson --version
ninja --version
pkg-config --version
if [[ -n "${GITHUB_PATH:-}" ]]; then
    echo "$task_tools/bin" >> "$GITHUB_PATH"
    echo "$task_tools/python/bin" >> "$GITHUB_PATH"
    echo '/opt/homebrew/bin' >> "$GITHUB_PATH"
    echo '/usr/local/bin' >> "$GITHUB_PATH"
    echo "$HOME/.cargo/bin" >> "$GITHUB_PATH"
fi
df -h .
echo 'Henge runner prerequisites passed. Pinned libraries are built by the workflow.'
