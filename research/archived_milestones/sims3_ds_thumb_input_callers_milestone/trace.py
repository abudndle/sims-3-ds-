#!/usr/bin/env python3
"""Read-only bounded ARM9 Thumb BL/BLX static callsite analysis."""
import json,struct,hashlib,argparse
from pathlib import Path

def load_arm9(rom):
    if len(rom)<0x40:raise ValueError('short ROM')
    off,entry,base,size=struct.unpack_from('<IIII',rom,0x20)
    if off<0x200 or not (base<=entry<base+size) or off+size>len(rom):raise ValueError('invalid ARM9 header')
    return base,rom[off:off+size]

def thumb_call(pc,h1,h2):
    if (h1&0xf800)!=0xf000 or (h2&0xe800)!=0xe800:return None
    # Thumb-1 BL=11111xxxxxxxxxxx, BLX=11101xxxxxxxxxxx
    if (h2&0xf800) not in (0xf800,0xe800):return None
    high=h1&0x7ff
    offset=((high<<12)|(h2&0x7ff)<<1)
    if offset&(1<<22):offset-=1<<23
    target=pc+4+offset
    if (h2&0xf800)==0xe800:target&=~3
    return target,'BL' if (h2&0xf800)==0xf800 else 'BLX'

def analyze(data):
    base,arm=load_arm9(data)
    targets=[0x02095C0C,0x020A14E4]
    found={f'0x{target:08X}':[] for target in targets}
    for pos in range(0,len(arm)-3,2):
        h1,h2=struct.unpack_from('<HH',arm,pos)
        d=thumb_call(base+pos,h1,h2)
        if d and d[0] in targets:
            found[f'0x{d[0]:08X}'].append({'callsite':f'0x{base+pos:08X}','mode':d[1],'bytes':arm[pos:pos+4].hex()})
    return {'sha256':hashlib.sha256(data).hexdigest(),'arm9_start':f'0x{base:08X}','arm9_end':f'0x{base+len(arm):08X}','candidate_functions':{'0x02095C0C':{'purpose':'Reads KEYINPUT after calling a helper; observed Thumb push/pop, register reads and bit masking','callsites':found['0x02095C0C']},'0x020A14E4':{'purpose':'Reads KEYINPUT and another input register; state update nearby','callsites':found['0x020A14E4']}},'limitations':['Static BL/BLX matches may be data; callers need control-flow confirmation','No touchscreen UI dispatcher identified','No ROM modified']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='report.json');args=ap.parse_args();r=analyze(Path(args.rom).read_bytes());Path(args.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
