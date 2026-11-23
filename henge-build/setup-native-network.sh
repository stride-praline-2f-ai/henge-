#!/bin/bash
# Build pinned Husk dependencies for native validation on a Mac without Homebrew.
set -euo pipefail
husk="${1:?usage: setup-native-network.sh HUSK_CHECKOUT}"
if pkg-config --exists slirp; then
    pkg-config --cflags --libs slirp
    exit 0
fi

build_dir="$husk/build/henge-native-network"
prefix="$build_dir/sysroot"
export PKG_CONFIG_PATH="$prefix/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

# Check both linkage and dylib loading before using or saving this sysroot.
verify_sysroot() {
    local check_dir compile_options
    local flags=()
    if [[ "$(pkg-config --variable=prefix slirp)" != "$prefix" ]]; then return 1; fi
    compile_options="$(pkg-config --cflags --libs slirp)" || return 1
    read -r -a flags <<< "$compile_options"
    check_dir="$(mktemp -d)" || return 1
    if printf '%s\n' '#include <libslirp.h>' \
        'int main(void) { return slirp_version_string() == 0; }' |
        xcrun --sdk macosx clang -x c - -x none "${flags[@]}" -o "$check_dir/slirp-probe" &&
        "$check_dir/slirp-probe"; then
        rm "$check_dir/slirp-probe"
        rmdir "$check_dir"
        return 0
    fi
    if [[ -f "$check_dir/slirp-probe" ]]; then rm "$check_dir/slirp-probe"; fi
    rmdir "$check_dir"
    return 1
}

if verify_sysroot; then
    echo 'Reusing validated native libslirp sysroot'
    echo "PKG_CONFIG_PATH=$PKG_CONFIG_PATH" >> "$GITHUB_ENV"
    exit 0
fi

# Husk's iOS build uses separate Meson build directories and a separate sysroot.
bash "$(dirname "$0")/fetch-required-sources.sh" "$husk"
source_dir="$husk/third_party/build"
export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
export CC="$(xcrun --sdk macosx --find clang)"
export CXX="$(xcrun --sdk macosx --find clang++)"
mkdir -p "$build_dir"

build_dependency() {
    local name="$1"
    shift
    meson setup "$build_dir/$name" "$source_dir/$name" --prefix "$prefix" \
        --libdir lib --buildtype release --default-library shared "$@"
    meson compile -C "$build_dir/$name" -j 4
    meson install -C "$build_dir/$name"
}

build_dependency glib-2.83.0 -Dtests=false -Dnls=disabled -Dintrospection=disabled \
    -Dselinux=disabled -Dlibmount=disabled -Ddtrace=disabled -Dlibelf=disabled \
    -Dman-pages=disabled -Dglib_debug=disabled -Dxattr=false
build_dependency libslirp-v4.9.1
verify_sysroot
pkg-config --cflags --libs slirp
echo "PKG_CONFIG_PATH=$PKG_CONFIG_PATH" >> "$GITHUB_ENV"
