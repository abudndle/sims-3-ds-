#!/usr/bin/env python3
"""Verify ARM7 touchscreen-controller AUX-command evidence; never modify ROM."""
import argparse, hashlib, json, struct
from pathlib import Path

SHA256 = "d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
BASE = 0x02380000
SITES = {
    0x0238E794: 0xE3A010EC, 0x0238E798: 0xE1C010B0,
    0x0238E8D4: 0xE3A010E4, 0x0238E8D8: 0xE1C010B0,
    0x0238E464: 0xEB0000C1, 0x0238E450: 0xEB000116,
    0x0238E474: 0xE59F1138, 0x0238E478: 0xE1C100B0,
    0x0238E5B4: 0x02FFFF94,
    0x0238E86C: 0x040001C0, 0x0238E874: 0x040001C2,
    0x0238E9BC: 0x040001C0, 0x0238E9C4: 0x040001C2,
}
CHANNELS = ("TEMP0", "Y", "VBAT", "Z1", "Z2", "X", "AUX", "TEMP1")

def decode_command(value):
    if not isinstance(value, int) or not 0 <= value <= 255:
        raise ValueError("ADC command must be one byte")
    if not value & 0x80:
        raise ValueError("ADC command start bit absent")
    channel = (value >> 4) & 7
    return {
        "command": f"0x{value:02X}",
        "channel": channel, "channel_name": CHANNELS[channel],
        "mode_bits": 8 if value & 8 else 12,
        "single_ended": bool(value & 4),
        "power_down_mode": value & 3,
    }

def inspect(rom, require_hash=True):
    digest = hashlib.sha256(rom).hexdigest()
    if require_hash and digest != SHA256:
        raise ValueError("original VS3E ROM hash mismatch")
    if len(rom) < 0x40:
        raise ValueError("ROM header too short")
    offset, base, size = (struct.unpack_from("<I",rom,p)[0] for p in (0x30,0x38,0x3C))
    if base != BASE or offset + size > len(rom):
        raise ValueError("invalid ARM7 region")
    def read_word(address):
        delta=address-base
        if delta<0 or delta+4>size or delta%4:
            raise ValueError("address outside ARM7 region")
        return struct.unpack_from("<I",rom,offset+delta)[0]
    for address,word in SITES.items():
        if read_word(address)!=word:
            raise ValueError(f"ARM7 opcode/literal mismatch at {address:#x}")
    commands=[decode_command(read_word(address)&255) for address in (0x0238E8D4,0x0238E794)]
    if [c["command"] for c in commands] != ["0xE4","0xEC"]:
        raise ValueError("command mismatch")
    return {
        "rom_sha256":digest, "verified_sites":len(SITES),
        "commands":commands, "shared_field":"0x02FFFF94",
        "conclusion":"Both commands select AUX ADC channel 6, not X or Y.",
        "limitations":["This is static code evidence, not runtime execution proof.",
          "Command interpretation uses the TSC2046 command format; full device select context not established here.",
          "The shared field is not demonstrated to contain touchscreen X/Y coordinates."],
    }

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("rom",type=Path);p.add_argument("--out",type=Path,default=Path("aux_channel_report.json"))
    args=p.parse_args();result=inspect(args.rom.read_bytes())
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(result["conclusion"])
