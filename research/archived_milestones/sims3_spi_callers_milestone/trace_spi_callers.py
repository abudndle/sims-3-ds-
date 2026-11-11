#!/usr/bin/env python3
"""Read-only ARM7 ARM-state BL call graph around the VS3E SPI routines.
Not an emulator trace. Does not claim that SPI commands are touchscreen XY samples.
"""
import argparse,csv,hashlib,json,struct
from pathlib import Path
TARGETS=[0x0238C9D8,0x0238CA54,0x0238CAC8,0x0238CAF0,0x0238CB20]

def arm7(rom):
    if len(rom)<0x40: raise ValueError('ROM too short')
    off,entry,base,size=struct.unpack_from('<IIII',rom,0x30)
    if off<0x200 or size==0 or off+size>len(rom) or not base<=entry<base+size: raise ValueError('invalid ARM7 header')
    return base,rom[off:off+size]

def bl_target(word,pc):
    # ARM B/BL immediate: bits [27:25] 101, link bit [24] 1.
    if (word&0x0F000000)!=0x0B000000:return None
    imm=word&0xFFFFFF
    if imm&0x800000:imm-=0x1000000
    return (pc+8+(imm<<2))&0xFFFFFFFF

def scan(rom):
    base,b=arm7(rom)
    callers={t:[] for t in TARGETS}
    for i in range(0,len(b)-3,4):
        a=base+i;t=bl_target(struct.unpack_from('<I',b,i)[0],a)
        if t in callers:callers[t].append(a)
    expected={0x0238CAC8:[0x0238CBB8],0x0238CAF0:[0x0238CBC4],0x0238CA54:[0x0238CAD8,0x0238CB00],0x0238C9D8:[0x0238CAE4,0x0238CB14]}
    for target,sources in expected.items():
        if not set(sources).issubset(callers[target]):raise ValueError(f'missing expected ARM BL call chain for {target:#x}')
    # Verify wrappers begin with the observed function prologue, and they are in-bounds.
    for a in (0x0238C9D8,0x0238CA54,0x0238CAC8,0x0238CAF0,0x0238CB20):
        ix=a-base
        if ix<0 or ix+4>len(b) or struct.unpack_from('<I',b,ix)[0]&0xFFFF0000!=0xE92D0000:
            raise ValueError(f'prologue mismatch at {a:#x}')
    edges=[{'caller':f'0x{source:08X}','callee':f'0x{t:08X}','kind':'ARM BL immediate'} for t,srcs in callers.items() for source in srcs]
    return {'sha256':hashlib.sha256(rom).hexdigest(),'arm7_start':f'0x{base:08X}','arm7_end':f'0x{base+len(b):08X}','functions':[{'address':f'0x{t:08X}','direct_arm_bl_callers':len(callers[t])} for t in TARGETS], 'edges':edges,'total_edges':len(edges),'limitations':['Only direct ARM-state BL calls to five selected addresses are enumerated. Thumb/BLX/indirect calls may be missed.','SPI helper calls do not by themselves identify X and Y coordinate handling.','Dispatch function 0x0238CB20 processes more than touchscreen operations.','No ROM changes or gameplay-control integration are performed.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--output',default='.');a=p.parse_args()
    data=scan(Path(a.rom).read_bytes());out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/'call_graph.json').write_text(json.dumps(data,indent=2)+'\n')
    with (out/'direct_callers.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,['caller','callee','kind']);w.writeheader();w.writerows(data['edges'])
    print('Verified direct BL edges:',data['total_edges'])
    for row in data['functions']:print(row['address'],row['direct_arm_bl_callers'])
if __name__=='__main__':main()
