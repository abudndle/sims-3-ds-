"""ROM-guarded ARM9 callback slot initialization and static reference inventory.

Does not claim that literal references exhaust runtime pointer aliases or that
a gameplay callback is registered in the statically loaded ARM9 binary.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_SHA = "d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
ARM9_BASE = 0x02004000
STATE_BLOCK = 0x0224FCE4
CALLBACK_OFFSET = 4
REFERENCES = {
    0x020D73B0: 0x020D75F8,
    0x020D7604: 0x020D766C,
    0x020D770C: 0x020D77EC,
    0x020D7830: 0x020D788C,
    0x020D7860: 0x020D788C,
    0x020D78A8: 0x020D78E4,
    0x020D78EC: 0x020D7930,
    0x020D7B40: 0x020D7C50,
    0x020D7C58: 0x020D7C6C,
}
ANCHORS = {
    0x020D7604: 0xE59F4060,
    0x020D7620: 0xE3A00000,
    0x020D7628: 0xE5840004,
    0x020D762C: 0xE5840014,
    0x020D73B0: 0xE59F3240,
    0x020D73D0: 0xE5933004,
    0x020D73D4: 0xE3530000,
    0x020D73E8: 0xE12FFF33,
    0x020D7564: 0xE5933004,
    0x020D7568: 0xE3530000,
    0x020D757C: 0xE12FFF33,
    0x020D766C: STATE_BLOCK,
    0x020D75F8: STATE_BLOCK,
}

def word(raw, offset):
    if offset < 0 or offset + 4 > len(raw):
        raise ValueError("truncated ROM or invalid offset")
    return struct.unpack_from("<I", raw, offset)[0]

def literal_target(op, address):
    if (op & 0x0F7F0000) != 0x051F0000:
        raise ValueError("instruction is not a PC-relative LDR")
    d = op & 0xFFF
    return (address + 8 + (d if op & (1 << 23) else -d)) & 0xFFFFFFFF

def scan_references(data, base=ARM9_BASE):
    """Find direct PC-relative ARM loads of words holding the state-block address."""
    literals = {base + i for i in range(0, len(data) - 3, 4)
                if word(data, i) == STATE_BLOCK}
    matches = {}
    for off in range(0, len(data) - 3, 4):
        instr = word(data, off)
        if (instr & 0x0F7F0000) == 0x051F0000:
            target = literal_target(instr, base + off)
            if target in literals:
                matches[base + off] = target
    return matches

def inspect(rom, strict=True):
    sha = hashlib.sha256(rom).hexdigest()
    if strict and sha != EXPECTED_SHA:
        raise ValueError("original ROM SHA-256 mismatch")
    if len(rom) < 0x30:
        raise ValueError("truncated ROM header")
    off, base, size = (word(rom, at) for at in (0x20, 0x28, 0x2C))
    if base != ARM9_BASE or size <= 0 or off + size > len(rom):
        raise ValueError("ARM9 header/section bounds invalid")
    data = rom[off:off + size]
    def arm_word(addr):
        delta = addr - base
        if delta % 4 or not 0 <= delta <= size - 4:
            raise ValueError("ARM9 code address out of bounds")
        return word(data, delta)
    for addr, expected in ANCHORS.items():
        if arm_word(addr) != expected:
            raise ValueError(f"ARM9 anchor mismatch at {addr:#x}")
    matches = scan_references(data, base)
    if matches != REFERENCES:
        missing = sorted(set(REFERENCES.items()) - set(matches.items()))
        extra = sorted(set(matches.items()) - set(REFERENCES.items()))
        raise ValueError(f"static state-block reference inventory changed: missing={missing}; extra={extra}")
    for addr, target in REFERENCES.items():
        if literal_target(arm_word(addr), addr) != target or arm_word(target) != STATE_BLOCK:
            raise ValueError(f"invalid input-state literal at {addr:#x}")
    return {
        "original_rom_sha256": sha,
        "input_state_block": hex(STATE_BLOCK),
        "callback_field_address": hex(STATE_BLOCK + CALLBACK_OFFSET),
        "init_callback_clear": "0x020d7628",
        "callback_indirect_call_sites": ["0x020d73e8", "0x020d757c"],
        "direct_pc_relative_references": {hex(k): hex(v) for k, v in sorted(matches.items())},
        "reference_count": len(matches),
        "limitations": [
            "Only direct ARM PC-relative word loads in the loaded ARM9 binary are enumerated.",
            "This cannot rule out computed pointers, overlays, aliases or runtime writes.",
            "Callback registration destination and gameplay UI dispatcher remain unknown.",
        ],
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("rom", type=Path)
    p.add_argument("--out", type=Path, default=Path("callback_inventory.json"))
    args = p.parse_args()
    result = inspect(args.rom.read_bytes())
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Verified callback clear and {result['reference_count']} static input-state references")
