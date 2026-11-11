#!/usr/bin/env python3
"""Fail public CI if an original game image, private binary or credential is tracked.

This is a path/extension guard, not a substitute for code review or secret scanning.
"""
from pathlib import PurePosixPath
import subprocess
import sys

ALLOWED_ARCHIVE = {"sims3-ds-PUBLIC-source.zip"}
BLOCKED_SUFFIXES = {
    ".nds", ".dsi", ".3ds", ".cci", ".cia", ".cxi", ".cfa",
    ".srl", ".sav", ".rom", ".iso", ".bin", ".app", ".tik",
    ".tmd", ".ncch", ".ncsd", ".key", ".pem", ".p12",
}
BLOCKED_PARTS = {"private_assets", "original_assets", "secrets", ".env"}
def find_unsafe(paths):
    unsafe = []
    for item in paths:
        p = PurePosixPath(item)
        if not p.parts:
            continue
        lower_parts = {part.lower() for part in p.parts}
        suffix = p.suffix.lower()
        if item in ALLOWED_ARCHIVE:
            continue  # Legacy source-only upload, already reviewed; not an exemption for other ZIPs.
        if suffix in BLOCKED_SUFFIXES or lower_parts & BLOCKED_PARTS:
            unsafe.append(item)
        elif suffix in {".zip", ".7z", ".rar"}:
            unsafe.append(item)
    return sorted(set(unsafe))

def main():
    listed = subprocess.check_output(["git", "ls-files", "-z"])
    paths = [p.decode("utf-8", "surrogateescape") for p in listed.split(b"\x00") if p]
    unsafe = find_unsafe(paths)
    if unsafe:
        print("Public repository contains potentially protected files:", file=sys.stderr)
        for path in unsafe:
            print(f" - {path}", file=sys.stderr)
        return 1
    print(f"PASS: {len(paths)} tracked public paths passed extension/path checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
