#!/bin/bash
# Henge needs Husk's libffi/glib/slirp sources, not its QEMU/pixman/ucontext
# emulator stages. Preserve the pinned source definitions and unpack stamps.
set -euo pipefail
task_husk="${1:?usage: fetch-required-sources.sh HUSK_CHECKOUT [SOURCE_CACHE]}"
task_source_cache="${2:-$task_husk/third_party}"
source "$task_husk/scripts/sources.sh"
task_downloads="$task_source_cache/sources"
task_sources="$task_source_cache/build"
mkdir -p "$task_downloads" "$task_sources"
for task_url in "$FFI_SRC" "$ICONV_SRC" "$GETTEXT_SRC" "$GLIB_SRC" "$SLIRP_SRC"; do
    task_name="${task_url##*/}"
    task_archive="$task_downloads/$task_name"
    task_stamp="$task_sources/.unpacked-$task_name"
    if [[ -f "$task_stamp" ]]; then continue; fi
    if [[ ! -s "$task_archive" ]]; then
        echo "[get] $task_name"
        curl --proto '=https' --tlsv1.2 -fL --retry 3 --retry-delay 5 \
            --connect-timeout 20 --max-time 600 -o "$task_archive.part" "$task_url"
        mv "$task_archive.part" "$task_archive"
    fi
    echo "[tar] $task_name"
    tar -xf "$task_archive" -C "$task_sources"
    touch "$task_stamp"
done

# Seed Meson's package cache with the same archives pinned by GLib's wraps.
# GitHub serves these files even when the runner cannot resolve wrapdb.mesonbuild.com.
task_glib_wraps="$task_sources/glib-2.83.0/subprojects"
task_meson_cache="$task_glib_wraps/packagecache"
mkdir -p "$task_meson_cache"
task_cache_wrap_asset() {
    local wrap="$1" kind="$2" url="$3" name checksum target
    name="$(awk -F ' = ' -v key="${kind}_filename" '$1==key {print $2}' "$wrap")"
    checksum="$(awk -F ' = ' -v key="${kind}_hash" '$1==key {print $2}' "$wrap")"
    [[ -n "$name" && "$url" == */"$name" && "$checksum" =~ ^[0-9a-f]{64}$ ]]
    target="$task_meson_cache/$name"
    if [[ -s "$target" && "$(shasum -a 256 "$target" | cut -d ' ' -f1)" == "$checksum" ]]; then
        return
    fi
    curl --proto '=https' --tlsv1.2 -fL --retry 3 --connect-timeout 20 \
        --max-time 600 -o "$target.part" "$url"
    echo "$checksum  $target.part" | shasum -a 256 -c -
    mv "$target.part" "$target"
}
task_wrapdb=https://github.com/mesonbuild/wrapdb/releases/download
task_cache_wrap_asset "$task_glib_wraps/pcre2.wrap" source "$task_wrapdb/pcre2_10.44-2/pcre2-10.44.tar.bz2"
task_cache_wrap_asset "$task_glib_wraps/pcre2.wrap" patch "$task_wrapdb/pcre2_10.44-2/pcre2_10.44-2_patch.zip"
task_cache_wrap_asset "$task_glib_wraps/zlib.wrap" source "$task_wrapdb/zlib_1.3.1-1/zlib-1.3.1.tar.gz"
task_cache_wrap_asset "$task_glib_wraps/zlib.wrap" patch "$task_wrapdb/zlib_1.3.1-1/zlib_1.3.1-1_patch.zip"
