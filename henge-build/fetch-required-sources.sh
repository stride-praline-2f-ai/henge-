#!/bin/bash
# Henge needs Husk's libffi/glib/slirp sources, not its QEMU/pixman/ucontext
# emulator stages. Preserve the pinned source definitions and unpack stamps.
set -euo pipefail
task_husk="${1:?usage: fetch-required-sources.sh HUSK_CHECKOUT}"
source "$task_husk/scripts/sources.sh"
task_downloads="$task_husk/third_party/sources"
task_sources="$task_husk/third_party/build"
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
