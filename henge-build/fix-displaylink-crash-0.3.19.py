#!/usr/bin/env python3
"""Fail-closed display-link presentation workaround for Henge 0.3.19 (120).

This applies only to the unsigned executable from custom source df4b4fbe.
It rewrites two Objective-C selector names in __objc_methname, leaves Mach-O
code and layout unchanged, and bumps the IPA build to 121. It does NOT make
an executable/source-level fix and requires re-signing and real-device testing.
"""
import argparse
import hashlib
import plistlib
import struct
import zipfile
from pathlib import Path

ORIGINAL_SHA256 = "4f77a22b4adf6063f64a816e840d8de88596ac66ee4abc7e2ab27645b300de74"
SELECTORS = ((b"presentAtTime:", b"present"),
             (b"presentDrawable:atTime:", b"presentDrawable:"))


def method_name_region(executable):
    if len(executable) < 32 or struct.unpack_from("<I", executable)[0] != 0xFEEDFACF:
        raise ValueError("Not the expected little-endian arm64 Mach-O executable")
    command_count = struct.unpack_from("<I", executable, 16)[0]
    offset = 32
    for _ in range(command_count):
        cmd, length = struct.unpack_from("<II", executable, offset)
        if length < 8 or offset + length > len(executable):
            raise ValueError("Malformed Mach-O load command")
        if cmd == 0x19:  # LC_SEGMENT_64
            section_count = struct.unpack_from("<I", executable, offset + 64)[0]
            for index in range(section_count):
                base = offset + 72 + 80 * index
                if base + 80 > offset + length:
                    raise ValueError("Malformed Mach-O section table")
                name = executable[base:base+16].split(b"\0")[0]
                segment = executable[base+16:base+32].split(b"\0")[0]
                if name == b"__objc_methname" and segment == b"__TEXT":
                    size = struct.unpack_from("<Q", executable, base + 40)[0]
                    file_offset = struct.unpack_from("<I", executable, base + 48)[0]
                    if file_offset + size > len(executable):
                        raise ValueError("Method-name section exceeds executable")
                    return file_offset, file_offset + size
        offset += length
    raise ValueError("ObjC method-name section not found")


def patch(executable):
    if hashlib.sha256(executable).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Wrong Henge executable: aborting rather than patching unknown code")
    start, end = method_name_region(executable)
    output = bytearray(executable)
    for old, new in SELECTORS:
        match = b"\0" + old + b"\0"
        names = output[start:end]
        if names.count(match) != 1:
            raise ValueError("Expected one precise ObjC selector: " + repr(old))
        position = start + names.index(match) + 1
        output[position:position+len(old)] = new + bytes(len(old)-len(new))
        assert output[position:position+len(new)] == new
    assert len(output) == len(executable)
    return bytes(output)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original_ipa", type=Path)
    ap.add_argument("output_ipa", type=Path)
    args = ap.parse_args()
    with zipfile.ZipFile(args.original_ipa) as source, zipfile.ZipFile(args.output_ipa, "w") as target:
        if source.testzip() is not None:
            raise ValueError("Original IPA ZIP failed integrity check")
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "Payload/Henge.app/Henge":
                data = patch(data)
            elif entry.filename in (
                "Payload/Henge.app/Info.plist",
                "Payload/Henge.app/PlugIns/HengeJITHelper.appex/Info.plist",
            ):
                info = plistlib.loads(data)
                if entry.filename == "Payload/Henge.app/Info.plist":
                    if info.get("CFBundleShortVersionString") != "0.3.19" or str(info.get("CFBundleVersion")) != "120":
                        raise ValueError("Unexpected app version")
                    info["HengeDisplayLinkPresentationHotfix"] = "non-timed-objc-selectors-2026-11-21"
                info["CFBundleVersion"] = "121"
                data = plistlib.dumps(info, fmt=plistlib.FMT_BINARY)
            target.writestr(entry, data)
    with zipfile.ZipFile(args.output_ipa) as check:
        if check.testzip() is not None:
            raise ValueError("Patched IPA ZIP failed integrity check")
        info = plistlib.loads(check.read("Payload/Henge.app/Info.plist"))
        assert info["CFBundleVersion"] == "121"
        assert info["HengeDisplayLinkPresentationHotfix"].startswith("non-timed")
    print("Unsigned hotfix IPA:", args.output_ipa)
    print("SHA-256:", hashlib.sha256(args.output_ipa.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
