#!/usr/bin/env python3
"""Read-only, bounded Thumb literal-load analysis for two Sims 3 DS input routines."""
import argparse, hashlib, json, struct
from pathlib import Path

TARGETS = {'button_snapshot_a': (0x02095C0C, 0x02095C4C),
           'button_snapshot_b': (0x020A14E4, 0x020A1540)}
KEYINPUT = 0x04000130
SHARED_BUTTON_STATE = 0x02FFFFA8

def extract_arm9(rom):
    if len(rom) < 0x40: raise ValueError('ROM header truncated')
    offset, entry, base, size = struct.unpack_from('<IIII', rom, 0x20)
    if offset < 0x200 or size == 0 or offset + size > len(rom) or not (base <= entry < base + size):
        raise ValueError('ARM9 image invalid')
    return base, memoryview(rom)[offset:offset+size]

def read_u16(code, base, addr):
    if (addr-base) % 2 or not base <= addr <= base+len(code)-2: raise ValueError('halfword out of image')
    return struct.unpack_from('<H', code, addr-base)[0]

def read_u32(code, base, addr):
    if (addr-base) % 4 or not base <= addr <= base+len(code)-4: raise ValueError('word out of image')
    return struct.unpack_from('<I', code, addr-base)[0]

def literal_at(pc, op):
    # Thumb-1 LDR Rt, [PC,#imm8*4]; PC aligned to 4.
    if (op & 0xF800) != 0x4800: return None
    return ((pc+4) & ~3) + (op & 0xff)*4

def scan_range(code, base, start, end):
    if not(base <= start < end <= base + len(code)) or start%2 or end%2:
        raise ValueError('bad function candidate bounds')
    records=[]
    for pc in range(start,end,2):
        op=read_u16(code,base,pc)
        loc=literal_at(pc,op)
        if loc is not None:
            records.append({'instruction':f'0x{pc:08X}','opcode':f'0x{op:04X}',
                            'register':f'r{(op>>8)&7}', 'pool_address':f'0x{loc:08X}',
                            'value':f'0x{read_u32(code,base,loc):08X}'})
    return records

def analyze(rom):
    base,code=extract_arm9(rom)
    groups=[]
    for name,(start,end) in TARGETS.items():
        literals=scan_range(code,base,start,end)
        values={int(x['value'],16) for x in literals}
        groups.append({'name':name,'candidate_range':[f'0x{start:08X}',f'0x{end:08X}'],
                       'literals':literals,'has_keyinput':KEYINPUT in values,
                       'has_shared_button_state':SHARED_BUTTON_STATE in values})
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),
            'arm9_base':f'0x{base:08X}', 'arm9_end_exclusive':f'0x{base+len(code):08X}',
            'groups':groups,'limitations':[
              'Static literals do not show that routines run during gameplay.',
              '0x02FFFFA8 is an input-related shared-memory lead; its exact bit semantics are not established here.',
              'Neither input routine is proven to be the touchscreen-coordinate dispatcher.',
              'No ROM patch, display rerouting, or modified-ROM boot test was performed.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--output',default='input_literals.json');args=p.parse_args()
    result=analyze(Path(args.rom).read_bytes())
    if not all(x['has_keyinput'] and x['has_shared_button_state'] for x in result['groups']):
        raise SystemExit('Expected input-literal pairs missing; ROM or candidate addresses differ')
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    for group in result['groups']:
        print(group['name'], 'literal loads',len(group['literals']), 'two input leads present')
if __name__=='__main__':main()
