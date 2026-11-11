"""Bounded provenance hints for ARM9 callback-slot store candidates.

This deliberately does not claim that a store's base register points at the
touchscreen object or that a nearby assignment executes on the same path.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from scan import ARM9_BASE, ROM_SHA256, arm9_region, store_word_immediate

def arm_mov_immediate(word):
    """Decode ARM MOV Rd,#imm, including rotated immediate constants."""
    if type(word) is not int or not 0 <= word <= 0xffffffff:
        raise ValueError("word must be unsigned 32-bit integer")
    if word & 0x0FE00000 != 0x03A00000 or (word >> 28) == 15:
        return None
    amount = ((word >> 8) & 15) * 2
    immediate = word & 255
    value = immediate if amount == 0 else ((immediate >> amount) | (immediate << (32 - amount))) & 0xffffffff
    return {"register": (word >> 12) & 15, "value": value}

def arm_ldr_literal(word, address):
    """Decode immediate PC-relative ARM LDR Rt,[PC,+/-imm12]."""
    if word & 0x0f7f0000 != 0x051f0000 or (word >> 28) == 15:
        return None
    delta = word & 0xfff
    return {"register": (word >> 12) & 15,
            "literal_address": (address + 8 + (delta if word & (1 << 23) else -delta)) & 0xffffffff}

def provenance_hints(rom, candidates, lookback=8):
    """Add local immediate/literal writers to each STR source register.

    Scans at most 'lookback' ARM-sized words preceding the hit.
    The **last** direct assignment in the window is reported, but intervening
    branches, data words and aliasing may invalidate its connection.
    """
    if type(lookback) is not int or not 1 <= lookback <= 32:
        raise ValueError("lookback must be an integer between 1 and 32")
    off, base, size = arm9_region(rom)
    output = []
    for candidate in candidates:
        address = int(candidate["address"], 16)
        if address < base or address + 4 > base + size or (address - base) % 4:
            raise ValueError("candidate outside loaded ARM9")
        opcode = struct.unpack_from("<I", rom, off + address - base)[0]
        parsed = store_word_immediate(opcode)
        if parsed is None or parsed["source_register"] != candidate["source_register"] or parsed["base_register"] != candidate["base_register"]:
            raise ValueError("candidate does not match underlying STR instruction")
        writers = []
        low = max(base, address - 4 * lookback)
        for current in range(low, address, 4):
            word = struct.unpack_from("<I", rom, off + current - base)[0]
            mov = arm_mov_immediate(word)
            ldr = arm_ldr_literal(word, current)
            for kind, hint in (("mov_immediate", mov), ("ldr_pc_literal", ldr)):
                if hint is not None and hint["register"] == parsed["source_register"]:
                    writers.append({"address": f"0x{current:08X}", "type": kind,
                                    "detail": hint})
        output.append({**candidate, "recent_source_register_writers": writers,
                       "last_candidate_writer": writers[-1] if writers else None})
    return output

def report(rom, lookback=8):
    from scan import scan
    raw = scan(rom)
    raw["instruction_shaped_hits"] = provenance_hints(
        rom, raw["instruction_shaped_hits"], lookback)
    raw["context_lookback_instructions"] = lookback
    raw["limitations"].extend([
        "Source-register hints are syntactic and not control-flow/data-flow proof.",
        "Literals and MOV immediates may be unrelated or overwritten by a call.",
        "This tool does not identify the callback registration writer."])
    return raw

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path)
    p.add_argument("--lookback", type=int, default=8)
    p.add_argument("--output", type=Path, default=Path("callback_writer_hints.json"))
    args = p.parse_args()
    value = report(args.rom.read_bytes(), args.lookback)
    args.output.write_text(json.dumps(value, indent=2) + "\n")
    print(f"{value['hit_count']} unverified candidate stores with bounded writer hints")
