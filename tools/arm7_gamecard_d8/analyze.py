#!/usr/bin/env python3
"""Verify 0xD8 at ARM7 0x0238F78C belongs to game-card command flow.

Static instruction-level proof only; does not trace runtime execution.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

SHA = 'd42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE = 0x02380000
ANCHORS = {
    0x0238F78C: 0xE3A090D8,  # mov r9, #0xD8
    0x0238F7A8: 0xE1A01009,  # mov r1, r9
    0x0238F7AC: 0xEBFFFF12,  # bl 0x0238F3FC
    0x0238F3FC: 0xE92D4008,  # push {r3, lr}
    0x0238F47C: 0xEBFFFF3D,  # bl 0x0238F178
    0x0238F178: 0xE92D4FF8,  # downstream bus helper
    0x0238F19C: 0xE59F50D8,  # LDR R5, literal at 0x0238F27C
    0x0238F1B8: 0xE1C560B0,  # STRH r6, [r5]
    0x0238F27C: 0x040001A0,  # game-card AUXSPICNT register
    0x0238F978: 0xE92D4038,  # other game-card helper
    0x0238F9F4: 0x040001A4,  # ROMCTRL
    0x0238F9F8: 0x040001A0,  # game-card AUXSPICNT
}

def read_u32(data, offset):
    if offset < 0 or offset + 4 > len(data):
        raise ValueError('out-of-range word read')
    return struct.unpack_from('<I', data, offset)[0]

def branch_target(inst, address):
    if (inst & 0x0E000000) != 0x0A000000:
        raise ValueError('not ARM B/BL')
    imm = inst & 0xFFFFFF
    if imm & 0x800000:
        imm -= 0x1000000
    return (address + 8 + imm*4) & 0xFFFFFFFF

def literal_target(inst, address):
    if inst & 0x0F7F0000 != 0x051F0000:
        raise ValueError('not ARM PC-relative literal LDR')
    delta = inst & 0xFFF
    return (address + 8 + (delta if inst & (1<<23) else -delta)) & 0xFFFFFFFF

def inspect(rom, verify_hash=True):
    digest = hashlib.sha256(rom).hexdigest()
    if verify_hash and digest != SHA:
        raise ValueError('unexpected original ROM hash')
    off,base,size = [read_u32(rom,x) for x in (0x30,0x38,0x3C)]
    if base != BASE or off + size > len(rom):
        raise ValueError('ARM7 header bounds mismatch')
    def word(address):
        delta = address-base
        if delta < 0 or delta+4 > size or delta%4:
            raise ValueError('address outside ARM7')
        return read_u32(rom, off+delta)
    for address,expected in ANCHORS.items():
        if word(address) != expected:
            raise ValueError(f'anchor mismatch at {address:#x}')
    for source,dest in [(0x0238F7AC,0x0238F3FC),(0x0238F47C,0x0238F178)]:
        if branch_target(word(source),source) != dest:
            raise ValueError('invalid call target')
    if literal_target(word(0x0238F19C),0x0238F19C) != 0x0238F27C:
        raise ValueError('wrong card-bus literal pointer')
    return {'original_rom_sha256':digest,'verified_instruction_and_literal_anchors':len(ANCHORS),
            'immediate': '0xD8', 'immediate_load': '0x0238F78C',
            'argument_move': '0x0238F7A8',
            'call_chain': ['0x0238F7AC -> 0x0238F3FC', '0x0238F47C -> 0x0238F178'],
            'downstream_bus_register': '0x040001A0',
            'classification':'game-card command path, not verified touch ADC X',
            'limitations':['Static code-only classification; runtime execution not established.',
                           'Other D8 instructions must be evaluated independently.',
                           'Neither X/Y touchscreen capture nor UI dispatch is identified.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('rom',type=Path)
    parser.add_argument('--out',type=Path,default=Path('gamecard_d8.json'))
    args=parser.parse_args()
    out=inspect(args.rom.read_bytes());args.out.write_text(json.dumps(out,indent=2)+'\n')
    print(out['classification'])
