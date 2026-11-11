#!/usr/bin/env python3
"""Read-only, instruction-validated analysis of the Sims 3 DS ARM7 SPI transfer helpers."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x02380000
EXPECTED_SHA256 = 'd42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
# Exact instructions used by the original ROM. Do not interpret data literals as instructions.
CHECKS = {
    # Send helper: command in r0, data in r1; includes wait and SPICNT writes.
    0x0238C9DC: (0xE59F5040, 'SPICNT address literal load'),
    0x0238C9F0: (0xE59F4030, 'SPI control value literal load'),
    0x0238C9F4: (0xE20000FF, 'mask command to one byte'),
    0x0238C9F8: (0xE1C540B0, 'write SPICNT'),
    0x0238C9FC: (0xE2841C06, 'enable continuous transfer for command'),
    0x0238CA00: (0xE1C510B0, 'write updated SPICNT'),
    0x0238CA04: (0xEB000009, 'call byte-send helper'),
    0x0238CA08: (0xE2441C02, 'adjust SPI control flags'),
    0x0238CA10: (0xE1C510B0, 'write SPICNT for payload'),
    0x0238CA14: (0xE20610FF, 'mask payload to byte'),
    0x0238CA18: (0xE1C010B0, 'write payload SPIDATA'),
    0x0238CA24: (0x040001C0, 'SPICNT literal'),
    0x0238CA28: (0x00008202, 'SPI control value'),
    0x0238CA2C: (0x040001C2, 'SPIDATA literal'),
    # Byte send/wait helper
    0x0238CA34: (0xE20000FF, 'mask byte for SPI'),
    0x0238CA38: (0xE1C100B0, 'write SPIDATA'),
    0x0238CA40: (0xE1D100B0, 'read SPICNT busy state'),
    0x0238CA50: (0x040001C2, 'SPIDATA literal'),
    # Read helper: command in r0, receive one byte
    0x0238CA58: (0xE59F505C, 'SPICNT address literal load'),
    0x0238CA68: (0xE59F4050, 'SPI control value literal load'),
    0x0238CA6C: (0xE3800080, 'set command high bit'),
    0x0238CA70: (0xE1C540B0, 'write SPICNT'),
    0x0238CA78: (0xE20000FF, 'mask command to one byte'),
    0x0238CA7C: (0xE1C510B0, 'write updated SPICNT'),
    0x0238CA80: (0xEBFFFFEA, 'call byte-send helper'),
    0x0238CA84: (0xE2441C02, 'adjust SPI control flags'),
    0x0238CA8C: (0xE1C510B0, 'write SPICNT for response'),
    0x0238CA90: (0xE3A01000, 'zero response clock byte'),
    0x0238CA94: (0xE1C010B0, 'write dummy SPIDATA byte'),
    0x0238CAA8: (0xE59F0014, 'reload SPIDATA address'),
    0x0238CAAC: (0xE1D000B0, 'read SPIDATA halfword'),
    0x0238CAB0: (0xE20000FF, 'truncate returned value to 8 bits'),
    0x0238CABC: (0x040001C0, 'SPICNT literal'),
    0x0238CAC0: (0x00008202, 'SPI control value'),
    0x0238CAC4: (0x040001C2, 'SPIDATA literal'),
}

def word(data, address):
    offset = address - BASE
    if offset < 0 or offset + 4 > len(data) or offset % 4:
        raise ValueError('ARM7 address outside mapped image or unaligned')
    return struct.unpack_from('<I', data, offset)[0]

def arm_bl_target(address, opcode):
    if opcode & 0x0f000000 != 0x0b000000:
        raise ValueError(f'{address:#x} is not an ARM BL')
    offset = opcode & 0xffffff
    if offset & 0x800000:
        offset -= 0x1000000
    return address + 8 + offset * 4

def check_arm7(data):
    mismatches = []
    for addr, (expected, description) in CHECKS.items():
        found = word(data, addr)
        if found != expected:
            mismatches.append({'address': hex(addr), 'expected': hex(expected), 'actual': hex(found), 'description': description})
    if mismatches:
        raise ValueError(f'{len(mismatches)} unexpected ARM7 instruction/literal(s): {mismatches}')
    for site, target in [(0x0238CA04, 0x0238CA30), (0x0238CA80, 0x0238CA30)]:
        found = arm_bl_target(site, word(data, site))
        if found != target:
            raise ValueError(f'Unexpected BL target at {site:#x}: {found:#x}')
    return {'validated_opcode_and_literal_sites': len(CHECKS),
            'validated_helper_calls': 2,
            'spi_control_word': '0x8202',
            'spi_registers': {'control': '0x040001C0', 'data': '0x040001C2'},
            'send_helper': {'entry': '0x0238C9D8', 'argument_command_register': 'r0', 'argument_payload_register': 'r1', 'payload_width_bits': 8},
            'read_helper': {'entry': '0x0238CA54', 'argument_command_register': 'r0', 'command_high_bit_forced': True, 'dummy_transfer_byte': 0, 'returned_width_bits': 8},
            'limitations': ['No proof of a 12-bit touchscreen ADC coordinate decoder', 'No runtime proof of touch input usage', 'No ARM9 UI dispatcher traced'],
            'rom_modified': False}

def run(rom):
    blob = Path(rom).read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError('Unexpected ROM SHA-256; analysis requires the original verified VS3E ROM')
    arm7_offset, arm7_entry, arm7_load, arm7_size = struct.unpack_from('<4I', blob, 0x30)
    if arm7_load != BASE or arm7_offset + arm7_size > len(blob):
        raise ValueError('ARM7 load address or file bounds invalid')
    result = check_arm7(blob[arm7_offset:arm7_offset + arm7_size])
    result.update({'source_sha256': digest, 'arm7_load': hex(BASE), 'arm7_size': arm7_size})
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=Path)
    parser.add_argument('--output', type=Path, default=Path('results.json'))
    args = parser.parse_args()
    report = run(args.rom)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"Verified {report['validated_opcode_and_literal_sites']} opcode/literal sites and two BL targets")
