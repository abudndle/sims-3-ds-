"""Verify ARM9 touch callback reset and shared event-reader provenance (VS3E)."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_SHA256 = 'd42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE = 0x02004000
STATE_OBJECT = 0x0224FCE4
ANCHORS = {
    0x020D738C: 0xE92D40F8,
    0x020D73B0: 0xE59F3240,
    0x020D73D0: 0xE5933004,
    0x020D73D4: 0xE3530000,
    0x020D73E8: 0xE12FFF33,
    0x020D7564: 0xE5933004,
    0x020D757C: 0xE12FFF33,
    0x020D75F8: STATE_OBJECT,
    0x020D7600: 0xE92D4038,
    0x020D7604: 0xE59F4060,
    0x020D7620: 0xE3A00000,
    0x020D7624: 0xE1C401B0,
    0x020D7628: 0xE5840004,
    0x020D762C: 0xE5840014,
    0x020D766C: STATE_OBJECT,
}

def pc_literal_address(opcode, address):
    if type(opcode) is not int or type(address) is not int:
        raise ValueError('integer opcode/address required')
    if (opcode & 0x0F7F0000) != 0x051F0000:
        raise ValueError('not an ARM PC-relative LDR')
    offset = opcode & 0xFFF
    return (address + 8 + (offset if opcode & (1 << 23) else -offset)) & 0xFFFFFFFF

def arm9_reader(rom):
    if len(rom) < 0x40:
        raise ValueError('truncated NDS header')
    off = struct.unpack_from('<I', rom, 0x20)[0]
    base = struct.unpack_from('<I', rom, 0x28)[0]
    size = struct.unpack_from('<I', rom, 0x2C)[0]
    if base != BASE or off & 3 or size & 3 or size == 0 or off + size > len(rom):
        raise ValueError('ARM9 header invalid')
    def read(address):
        d = address - base
        if d < 0 or d % 4 or d + 4 > size:
            raise ValueError('ARM9 word out of bounds')
        return struct.unpack_from('<I', rom, off+d)[0]
    return read

def inspect(rom, verify_sha=True):
    digest = hashlib.sha256(rom).hexdigest()
    if verify_sha and digest != EXPECTED_SHA256:
        raise ValueError('original VS3E SHA256 mismatch')
    read = arm9_reader(rom)
    for address, opcode in ANCHORS.items():
        if read(address) != opcode:
            raise ValueError(f'ARM9 anchor mismatch at {address:#010x}')
    for ldr, literal in ((0x020D73B0,0x020D75F8),(0x020D7604,0x020D766C)):
        if pc_literal_address(read(ldr),ldr) != literal:
            raise ValueError('literal resolution mismatch')
        if read(literal) != STATE_OBJECT:
            raise ValueError('state object mismatch')
    return {
        'original_rom_sha256': digest,
        'verified_instruction_and_literal_anchors': len(ANCHORS),
        'touch_state_runtime_address': f'0x{STATE_OBJECT:08X}',
        'initialization': {
            'entry': '0x020D7600', 'pointer_load': '0x020D7604',
            'zero_assignment': '0x020D7620',
            'callback_slot_clear': '0x020D7628', 'callback_slot_offset': 4,
        },
        'event_readers': [
            {'entry':'0x020D738C', 'state_pointer_load':'0x020D73B0',
             'callback_slot_read':'0x020D73D0', 'call':'0x020D73E8'},
            {'callback_slot_read':'0x020D7564', 'call':'0x020D757C'},
        ],
        'classification': 'initialization clears same +4 callback slot used by event dispatcher',
        'limitations': [
            'ARM9 runtime object lies beyond the loaded ARM9 binary and is not dereferenced.',
            'The reset instruction does not identify who subsequently registers a callback.',
            'The second reader is within the same event routine but runtime execution is untested.',
            'Gameplay UI callback destination, pixel calibration and ROM patch remain unverified.',
        ],
    }

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--output', type=Path, default=Path('touch_callback_reset.json'))
    args=p.parse_args()
    result=inspect(args.rom.read_bytes())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['classification'])
