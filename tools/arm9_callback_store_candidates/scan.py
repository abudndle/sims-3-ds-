"""Conservative ARM9 callback-offset writer candidate inventory (read-only).

Scans ARM-state word STR instructions with immediate offset +4. A hit is
instruction-shaped data, NOT proof of callback registration or execution.
Uses the exact user-authorized VS3E ROM; never exports game bytes.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROM_SHA256 = "d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
ARM9_BASE = 0x02004000
ARM9_HEADER = 0x20


def store_word_immediate(opcode):
    """Return registers for ARM STR Rt,[Rn,#4]; reject writes and addressing variants.

    Accept conditional and unconditional ARM-state encoding with P=1,U=1,
    B=0,W=0,L=0,I=0 and imm12=4; reject PC as base, since this is not a
    plausible writable callback object.
    """
    if type(opcode) is not int or opcode < 0 or opcode > 0xffffffff:
        raise ValueError("opcode must be unsigned 32-bit integer")
    # Bits 27:26=01; I=0 P=1 U=1 B=0 W=0 L=0.
    if (opcode & 0x0ff00000) != 0x05800000:
        return None
    if (opcode & 0xfff) != 4:
        return None
    cond = (opcode >> 28) & 15
    base = (opcode >> 16) & 15
    src = (opcode >> 12) & 15
    if cond == 15 or base == 15 or src == 15:
        return None
    return {"condition": cond, "base_register": base, "source_register": src}


def arm9_region(rom):
    if len(rom) < 0x40:
        raise ValueError("truncated NDS header")
    off, load, size = struct.unpack_from("<III", rom, ARM9_HEADER)[0], struct.unpack_from("<I",rom,0x28)[0], struct.unpack_from("<I",rom,0x2c)[0]
    if load != ARM9_BASE or not size or size & 3 or off & 3 or off + size > len(rom):
        raise ValueError("invalid ARM9 file offset, load address or bounds")
    return off, load, size


def scan(rom, require_exact_sha=True, start=None, end=None):
    digest = hashlib.sha256(rom).hexdigest()
    if require_exact_sha and digest != ROM_SHA256:
        raise ValueError("ROM SHA256 mismatch; refusing other revision")
    off, base, size = arm9_region(rom)
    lower = base if start is None else start
    upper = base + size if end is None else end
    if (type(lower) is not int or type(upper) is not int or lower < base
            or upper > base + size or lower >= upper or (lower | upper) & 3):
        raise ValueError("scan window must be aligned and inside ARM9")
    matches = []
    for address in range(lower, upper, 4):
        opcode = struct.unpack_from("<I", rom, off + address - base)[0]
        parsed = store_word_immediate(opcode)
        if parsed is None:
            continue
        matches.append({"address": f"0x{address:08X}",
                        "opcode": f"0x{opcode:08X}", **parsed})
    return {"rom_sha256": digest, "region": "loaded ARM9",
            "scan_start": f"0x{lower:08X}", "scan_end_exclusive": f"0x{upper:08X}",
            "instruction_shaped_hits": matches,
            "hit_count": len(matches),
            "known_callback_read": "0x020D7564: LDR r3,[r3,#4]",
            "known_callback_call": "0x020D757C: BLX r3",
            "limitations": [
                "A STR [Rn,#4] hit does not prove Rn points to a touch input object.",
                "Includes possible literal/data false positives and conditional instructions.",
                "Does not decode Thumb, overlays, register-offset writes or multi-register stores.",
                "Callback target and Sims gameplay UI dispatcher still unverified."]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path, help="Original authorized VS3E .nds only")
    p.add_argument("--start", type=lambda x: int(x, 0))
    p.add_argument("--end", type=lambda x: int(x, 0))
    p.add_argument("--output", type=Path, default=Path("callback_store_candidates.json"))
    args = p.parse_args()
    report = scan(args.rom.read_bytes(), start=args.start, end=args.end)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{report['hit_count']} ARM STR [Rn,#4] candidates (not verified registrations)")
