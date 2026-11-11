#!/usr/bin/env python3
"""Read-only, version-locked instruction analysis of Sims 3 DS ARM9 key snapshot code."""
import argparse, hashlib, json, struct
from pathlib import Path

ROUTINE_START = 0x021BE974
ROUTINE_END = 0x021BEA24
KEY_LOAD = 0x021BE9D8
KEY_READ = 0x021BEA04
LITERAL_ADDRESS = 0x021BEA30
KEYINPUT = 0x04000130

def word(data, off):
    return struct.unpack_from('<I', data, off)[0]

def signed24(n):
    return n-(1<<24) if n & (1<<23) else n

def branch_target(addr, opcode):
    if (opcode & 0x0E000000) != 0x0A000000 or opcode >> 28 == 15:
        return None
    return addr+8+(signed24(opcode & 0xFFFFFF)<<2)

def analyze(rom):
    if len(rom) < 0x200: raise ValueError('Invalid ROM')
    off, base, size = struct.unpack_from('<III',rom,0x20)
    if off < 0x200 or size <= 0 or off+size > len(rom): raise ValueError('Invalid ARM9 region')
    arm = rom[off:off+size]
    def at(addr):
        j=addr-base
        if not (0<=j<=len(arm)-4): raise ValueError('Target not in ARM9 binary')
        return word(arm,j)
    # Version lock plus local instruction verification: no speculative patch instructions.
    checks={
        'routine_push':at(ROUTINE_START)==0xE92D4070,
        'pc_relative_keyinput_literal':at(KEY_LOAD)==0xE59F2050,
        'keyinput_literal_value':at(LITERAL_ADDRESS)==KEYINPUT,
        'actual_keyinput_halfword_read':at(KEY_READ)==0xE1D220B0,
        'routine_pop':at(ROUTINE_END-8)==0xE8BD4070,
        'routine_return':at(ROUTINE_END-4)==0xE12FFF1E,
    }
    if not all(checks.values()): raise ValueError(f'Unexpected ROM instruction signature: {checks}')
    records=[]
    for a in range(ROUTINE_START, ROUTINE_END, 4):
        opcode=at(a)
        entry={'address':f'0x{a:08X}','opcode':f'0x{opcode:08X}', 'rom_offset':f'0x{off+a-base:X}'}
        target=branch_target(a,opcode)
        if target is not None: entry['branch_target']=f'0x{target:08X}'
        records.append(entry)
    callsites=[]
    for j in range(0,len(arm)-3,4):
        opcode=word(arm,j)
        if opcode & 0x0F000000 != 0x0B000000 or opcode>>28==15:continue
        target=branch_target(base+j,opcode)
        if target==ROUTINE_START: callsites.append(f'0x{base+j:08X}')
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'arm9_rom_offset':f'0x{off:X}', 'arm9_load_address':f'0x{base:08X}',
            'function_start':f'0x{ROUTINE_START:08X}','function_end_exclusive':f'0x{ROUTINE_END:08X}',
            'function_bytes':ROUTINE_END-ROUTINE_START,
            'keyinput_literal_load':f'0x{KEY_LOAD:08X}', 'keyinput_literal':f'0x{LITERAL_ADDRESS:08X}',
            'keyinput_halfword_read':f'0x{KEY_READ:08X}',
            'verified':checks,'direct_arm_bl_calls':callsites,'instructions':records,
            'limitations':['No direct ARM BL to entry found in static main ARM9 image; may be reached indirectly or from overlays',
                           'Instruction identity confirms hardware button sampling, not an actual gameplay touchscreen-dispatch hook',
                           'No ROM modifications performed; runtime use not yet verified']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('--output',type=Path,default=Path('input_function.json'))
    args=p.parse_args();data=analyze(args.rom.read_bytes());args.output.write_text(json.dumps(data,indent=2)+'\n')
    print('Verified low-level input routine',data['function_start'], 'instruction count',len(data['instructions']))
if __name__=='__main__':main()
