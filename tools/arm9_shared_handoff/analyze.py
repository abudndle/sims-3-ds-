#!/usr/bin/env python3
"""Verify ARM7->ARM9 halfword handoff without altering original Sims 3 DS ROM."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_SHA256 = "d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
SHARED = 0x02FFFF94

def read32(data, at):
    if at < 0 or at + 4 > len(data):
        raise ValueError("Out of range read")
    return struct.unpack_from("<I", data, at)[0]

def arm_literal_address(word, instruction_address):
    if (word & 0x0F7F0000) != 0x051F0000:
        raise ValueError("Not ARM PC-relative LDR literal")
    distance = word & 0xFFF
    return (instruction_address + 8 + (distance if word & (1 << 23) else -distance)) & 0xFFFFFFFF

def inspect(rom, verify_hash=True):
    digest = hashlib.sha256(rom).hexdigest()
    if verify_hash and digest != EXPECTED_SHA256:
        raise ValueError("ROM SHA-256 mismatch")
    def cpu_read(header, address):
        offset = read32(rom, header)
        base = read32(rom, header + 8)
        size = read32(rom, header + 12)
        delta = address - base
        if delta < 0 or delta % 4 or delta + 4 > size:
            raise ValueError("Address outside loaded CPU binary")
        if offset + size > len(rom):
            raise ValueError("CPU binary extends beyond ROM")
        return read32(rom, offset + delta)
    def a9(addr):
        return cpu_read(0x20, addr)
    def a7(addr):
        return cpu_read(0x30, addr)

    arm9 = {
        0x020D7DA4: 0xE595201C,  # load destination pointer
        0x020D7DA8: 0xE3520000,  # compare pointer to zero
        0x020D7DAC: 0x159F1030,  # LDRNE shared-address literal
        0x020D7DB0: 0x11D110B0,  # LDRHNE value from shared address
        0x020D7DB4: 0x11C210B0,  # STRHNE value to destination pointer
    }
    for addr, expected in arm9.items():
        if a9(addr) != expected:
            raise ValueError("Unexpected ARM9 instruction at %#x" % addr)
    if arm_literal_address(a9(0x020D7DAC), 0x020D7DAC) != 0x020D7DE4:
        raise ValueError("Wrong ARM9 literal target")
    if a9(0x020D7DE4) != SHARED:
        raise ValueError("Wrong ARM9 shared-memory literal")

    arm7 = {
        0x0238E474: 0xE59F1138,
        0x0238E478: 0xE1C100B0,
        0x0238E5B4: SHARED,
    }
    for addr, expected in arm7.items():
        if a7(addr) != expected:
            raise ValueError("Unexpected ARM7 instruction or literal at %#x" % addr)
    if arm_literal_address(a7(0x0238E474), 0x0238E474) != 0x0238E5B4:
        raise ValueError("Wrong ARM7 shared-memory literal target")

    return {
        "rom_sha256": digest,
        "shared_memory_address": "0x02ffff94",
        "arm7": {
            "shared_address_load": "0x0238e474",
            "halfword_store": "0x0238e478",
            "literal_entry": "0x0238e5b4",
        },
        "arm9": {
            "destination_pointer_load": "0x020d7da4",
            "destination_pointer_check": "0x020d7da8",
            "shared_address_load": "0x020d7dac",
            "halfword_read": "0x020d7db0",
            "destination_halfword_store": "0x020d7db4",
            "literal_entry": "0x020d7de4",
        },
        "conclusion": "Static ARM7 shared-memory halfword write and ARM9 conditional read/copy established.",
        "not_established": [
            "Whether the paths execute during gameplay",
            "Whether the field contains touchscreen X/Y data",
            "The origin of the ARM7 value",
            "The ARM9 destination pointer semantics",
            "A safe gameplay UI hook",
        ],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("--output", type=Path, default=Path("handoff.json"))
    args = parser.parse_args()
    result = inspect(args.rom.read_bytes())
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("Verified shared-memory halfword handoff:", result["shared_memory_address"])

if __name__ == "__main__":
    main()
