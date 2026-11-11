"""Classify ROM literal pointer hints near ARM9 callback-slot stores.

Read-only, SHA-guarded through scan.scan(). A literal's contents can be a
function pointer, data pointer, or unrelated value; being near a STR does
not establish the registration path or runtime callback destination.
"""
import argparse
import json
import struct
from pathlib import Path
from explain import provenance_hints
from scan import arm9_region, scan


def classify_target(value, arm9_base, arm9_size):
    """Classify pointer shape without claiming callable code."""
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("literal value must be unsigned 32-bit")
    code_address = value & ~1
    inside = arm9_base <= code_address < arm9_base + arm9_size
    aligned = bool(value & 1) or value % 4 == 0
    return {
        "value": f"0x{value:08X}",
        "arm_state_hint": "Thumb" if value & 1 else "ARM",
        "inside_loaded_arm9": inside,
        "alignment_plausible": aligned,
        "possible_code_pointer": inside and aligned,
        "note": "Pointer-shape candidate only, not a verified callback target",
    }


def classify_literal(rom, literal_address):
    """Read one aligned literal word only if contained in loaded ARM9."""
    off, base, size = arm9_region(rom)
    if (type(literal_address) is not int
            or literal_address < base or literal_address + 4 > base + size
            or literal_address % 4):
        return {"literal_address": f"0x{literal_address:08X}",
                "status": "outside_or_unaligned_loaded_arm9"}
    value = struct.unpack_from("<I", rom, off + literal_address - base)[0]
    return {"literal_address": f"0x{literal_address:08X}",
            "status": "readable",
            "pointer_shape": classify_target(value, base, size)}


def enrich(rom, candidates, lookback=8):
    """Preserve every syntactic hit, decorating only LDR-literal hints."""
    enriched = provenance_hints(rom, candidates, lookback)
    for candidate in enriched:
        for writer in candidate["recent_source_register_writers"]:
            if writer["type"] == "ldr_pc_literal":
                writer["resolved_literal"] = classify_literal(
                    rom, writer["detail"]["literal_address"])
    return enriched


def report(rom, lookback=8):
    raw = scan(rom)
    raw["instruction_shaped_hits"] = enrich(
        rom, raw["instruction_shaped_hits"], lookback)
    raw["context_lookback_instructions"] = lookback
    raw["analysis"] = "literal_pointer_shape_inventory"
    raw["limitations"].extend([
        "A code-shaped pointer may refer to unrelated data or dead code.",
        "A nearby LDR does not establish def-use across branches, calls or aliases.",
        "No instruction-flow reconstruction, dynamic dispatch or emulator evidence.",
    ])
    return raw


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path)
    p.add_argument("--lookback", type=int, default=8)
    p.add_argument("--output", type=Path, default=Path("callback_literal_shapes.json"))
    a = p.parse_args()
    record = report(a.rom.read_bytes(), a.lookback)
    a.output.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{record['hit_count']} unverified STR candidates; literal shapes analyzed")
