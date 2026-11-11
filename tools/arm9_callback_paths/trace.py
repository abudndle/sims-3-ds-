"""Verify three ARM9 input callback paths against the original VS3E ROM.

Static instruction evidence only: no runtime callback target or gameplay hook.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROM_SHA256 = 'd42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
ARM9_BASE = 0x02004000
STATE_BLOCK = 0x0224FCE4

PATHS = (
    {'name': 'timer_handler_early', 'state_load': 0x020D73B0,
     'literal': 0x020D75F8, 'read': 0x020D73D0,
     'compare': 0x020D73D4, 'call': 0x020D73E8},
    {'name': 'timer_handler_after_decode', 'state_load': None,
     'literal': 0x020D75FC, 'read': 0x020D7564,
     'compare': 0x020D7568, 'call': 0x020D757C},
    {'name': 'input_state_update', 'state_load': 0x020D7830,
     'literal': 0x020D788C, 'read': 0x020D7840,
     'compare': 0x020D7844, 'call': 0x020D7858},
)
# The second path reads the packed shared field at 0x020D74EC, not
# a new input-state pointer. Its state pointer survives from earlier code.
SITES = {
    0x020D73B0: 0xE59F3240,
    0x020D73D0: 0xE5933004,
    0x020D73D4: 0xE3530000,
    0x020D73E0: 0xE3A01004,
    0x020D73E4: 0xE3A02000,
    0x020D73E8: 0xE12FFF33,
    0x020D7564: 0xE5933004,
    0x020D7568: 0xE3530000,
    0x020D7574: 0xE3A01000,
    0x020D7578: 0xE1A02001,
    0x020D757C: 0xE12FFF33,
    0x020D7830: 0xE59F0054,
    0x020D7834: 0xE1D013B8,
    0x020D7838: 0xE3811001,
    0x020D783C: 0xE1C013B8,
    0x020D7840: 0xE5903004,
    0x020D7844: 0xE3530000,
    0x020D7848: 0x08BD8038,
    0x020D784C: 0xE3A00000,
    0x020D7850: 0xE1A02000,
    0x020D7854: 0xE3A01004,
    0x020D7858: 0xE12FFF33,
    0x020D75F8: STATE_BLOCK,
    0x020D788C: STATE_BLOCK,
}

def read32(data, off):
    if off < 0 or off + 4 > len(data):
        raise ValueError('truncated ROM')
    return struct.unpack_from('<I', data, off)[0]

def decode_ldr_literal(opcode, address):
    if (opcode & 0x0F7F0000) != 0x051F0000:
        raise ValueError('not ARM PC-relative literal LDR')
    d = opcode & 0xFFF
    return (address + 8 + (d if opcode & (1 << 23) else -d)) & 0xFFFFFFFF

def decode_blx_register(opcode):
    if opcode & 0x0FFFFFF0 != 0x012FFF30:
        raise ValueError('not ARM BLX-register')
    return opcode & 15

def inspect(rom, check_sha=True):
    digest = hashlib.sha256(rom).hexdigest()
    if check_sha and digest != ROM_SHA256:
        raise ValueError('VS3E original SHA-256 mismatch')
    off, base, size = (read32(rom, p) for p in (0x20, 0x28, 0x2C))
    if base != ARM9_BASE or size <= 0 or off + size > len(rom):
        raise ValueError('invalid ARM9 region')
    def at(address):
        offset = address - base
        if offset < 0 or offset % 4 or offset + 4 > size:
            raise ValueError(f'address outside ARM9: {address:#x}')
        return read32(rom, off + offset)
    for address, expected in SITES.items():
        if at(address) != expected:
            raise ValueError(f'anchor mismatch at {address:#x}')
    if at(0x020D74EC) != 0xE59F1108 or at(0x020D75FC) != 0x02FFFFAA:
        raise ValueError('shared input provenance mismatch')
    paths = []
    for path in PATHS:
        if path['state_load'] is not None and decode_ldr_literal(at(path['state_load']), path['state_load']) != path['literal']:
            raise ValueError('unexpected literal target')
        target = at(path['literal'])
        if path['name'] == 'timer_handler_after_decode':
            if target != 0x02FFFFAA:
                raise ValueError('wrong packed input literal')
        elif target != STATE_BLOCK:
            raise ValueError('wrong state block literal')
        if decode_blx_register(at(path['call'])) != 3:
            raise ValueError('callback not via r3')
        paths.append({'name': path['name'], 'callback_read': hex(path['read']),
                      'callback_call': hex(path['call']), 'callback_field_offset': 4})
    return {
        'original_rom_sha256': digest,
        'verified_instruction_and_literal_sites': len(SITES) + 2,
        'state_block': hex(STATE_BLOCK),
        'callback_field_address': hex(STATE_BLOCK + 4),
        'callback_invocation_paths': paths,
        'new_third_path': {'function_area': '0x020D7828',
            'state_load': '0x020D7830', 'callback_load': '0x020D7840',
            'null_check': '0x020D7844', 'call': '0x020d7858',
            'argument_setup': {'r0': 0, 'r1': 4, 'r2': 0}},
        'limitations': [
            'Only instruction-level code evidence, not runtime execution',
            'No callback registration writer identified',
            'No gameplay UI receiver or screen calibration proved',
        ],
    }

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', type=Path)
    ap.add_argument('--out', type=Path, default=Path('callback_paths.json'))
    args = ap.parse_args()
    report = inspect(args.rom.read_bytes())
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print('Verified', len(report['callback_invocation_paths']), 'callback call paths')
