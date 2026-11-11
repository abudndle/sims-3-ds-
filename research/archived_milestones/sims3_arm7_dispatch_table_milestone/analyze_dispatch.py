#!/usr/bin/env python3
"""Read-only inventory of a bounded ARM7 26-way halfword PC dispatch in VS3E.
Does not identify touch X/Y data or modify executable data.
"""
import argparse,csv,hashlib,json,struct
from pathlib import Path
SWITCH=0x0238CB20
TABLE=0x0238CB4C
PC_BASE=0x0238CB50
COUNT=26
KNOWN_HELPERS={0x0238C9D8:'SPI write helper',0x0238CA54:'SPI read helper',0x0238CAC8:'transfer wrapper A',0x0238CAF0:'transfer wrapper B'}

def read_rom(path):
    b=Path(path).read_bytes()
    if len(b)<0x40: raise ValueError('truncated NDS header')
    off, entry,base,size=struct.unpack_from('<IIII',b,0x30)
    if not (off>=0x200 and size>0 and off+size<=len(b) and base<=entry<base+size):
        raise ValueError('invalid ARM7 layout')
    return b,base,b[off:off+size]

def branch_target(insn,pc):
    if insn&0x0F000000 not in (0x0A000000,0x0B000000): return None
    imm=insn&0xFFFFFF
    if imm & 0x800000: imm-=0x1000000
    return (pc+8+(imm<<2))&0xffffffff

def decode(base,arm7):
    def word(a):
        at=a-base
        if at<0 or at+4>len(arm7): raise ValueError('address outside ARM7 range')
        return struct.unpack_from('<I',arm7,at)[0]
    def half(a):
        at=a-base
        if at<0 or at+2>len(arm7): raise ValueError('address outside ARM7 range')
        return struct.unpack_from('<H',arm7,at)[0]
    expected=(0xE3500019,0xE08F0080,0xE1D000B4,0xE08FF000)
    actual=(word(SWITCH+0x0c),word(SWITCH+0x20),word(SWITCH+0x24),word(SWITCH+0x28))
    if actual!=expected: raise ValueError('dispatch instruction pattern mismatch')
    entries=[]
    for i in range(COUNT):
        offset=half(TABLE+2*i)
        target=PC_BASE+offset
        if target%4 or not (base<=target<=base+len(arm7)-4):
            raise ValueError(f'invalid dispatch target for case {i}')
        w=word(target)
        callee=branch_target(w,target) if (w&0x0F000000)==0x0B000000 else None
        imm=w&0xff if (w&0xFFFFF000)==0xE3A00000 else None
        entries.append({'case':i,'table_address':f'0x{TABLE+2*i:08X}',
            'relative_offset':offset,'target':f'0x{target:08X}',
            'first_arm_instruction':f'0x{w:08X}',
            'first_instruction_BL_target':f'0x{callee:08X}' if callee is not None else '',
            'first_instruction_mov_r0_imm':imm if imm is not None else '',
            'first_instruction_target_description':KNOWN_HELPERS.get(callee,'')})
    if len({e['target'] for e in entries})!=COUNT: raise ValueError('duplicate switch case target')
    return entries

def analyze(path):
    rom,base,arm7=read_rom(path)
    entries=decode(base,arm7)
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'arm7_base':f'0x{base:08X}',
        'dispatcher':f'0x{SWITCH:08X}','case_count':len(entries), 'cases':entries,
        'limitations':['Static ARM7 jump-table decoding only; not proof the dispatcher is a touchscreen XY decoder.',
                       'The table includes non-touch peripheral commands.','Only the first instruction of each case is annotated.',
                       'No modified ROM, runtime hook, or emulator-tested gameplay UI is produced.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--out',default='.');args=p.parse_args()
    report=analyze(args.rom)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'dispatch_report.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'dispatch_cases.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(report['cases'][0]));w.writeheader();w.writerows(report['cases'])
    print(f"Verified {report['case_count']} dispatch cases at {report['dispatcher']}")
if __name__=='__main__': main()
