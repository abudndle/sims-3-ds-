#!/usr/bin/env python3
"""Read-only ARM7 SPI helper caller and constant provenance scanner (VS3E)."""
import argparse, csv, hashlib, json, struct
from pathlib import Path
HELPERS={0x0238C9D8:'spi_send',0x0238CA54:'spi_read'}

def u32(buf, i): return struct.unpack_from('<I',buf,i)[0]
def branch_target(word, addr):
    if (word & 0x0f000000)!=0x0b000000: return None
    off=word & 0xffffff
    if off & 0x800000: off-=0x1000000
    return addr+8+off*4

def mov_imm(word):
    # MOV immediate, unconditional. ARM rotate-right expanded 8-bit immediate.
    if (word & 0xffff0000)==0xe3a00000: pass
    if (word & 0x0fe00000)!=0x03a00000 or (word>>28)!=0xe: return None
    dest=(word>>12)&15
    imm=word&255
    r=2*((word>>8)&15)
    val=((imm>>r)|(imm<<(32-r)))&0xffffffff if r else imm
    return dest,val

def trace(rom):
    if len(rom)<0x40: raise ValueError('ROM too short')
    ofs=u32(rom,0x30); base=u32(rom,0x38); size=u32(rom,0x3c)
    if ofs+size>len(rom) or size%4: raise ValueError('Invalid ARM7 section')
    code=rom[ofs:ofs+size]; rows=[]
    for i in range(0,len(code)-3,4):
        w=u32(code,i); addr=base+i; target=branch_target(w,addr)
        if target not in HELPERS:continue
        preceding=[]
        # Look for nearby MOV r0,#imm before the call; not guaranteed to be the input value.
        for j in range(max(0,i-32),i,4):
            p=mov_imm(u32(code,j))
            if p and p[0]==0: preceding.append({'address':f'0x{base+j:08X}','value':f'0x{p[1]:X}'})
        rows.append({'callsite':f'0x{addr:08X}','helper':HELPERS[target], 'target':f'0x{target:08X}', 'nearby_mov_r0': preceding[-1] if preceding else None, 'nearby_candidates':preceding, 'confidence':'static-call-only'})
    return {'sha256':hashlib.sha256(rom).hexdigest(),'arm7_base':f'0x{base:X}','arm7_size':size,'calls':rows}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='results');args=ap.parse_args()
    r=trace(Path(args.rom).read_bytes());out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'spi_helper_calls.json').write_text(json.dumps(r,indent=2)+'\n')
    with (out/'spi_helper_calls.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['callsite','helper','target','nearby_mov_r0','confidence']);wr.writeheader()
        for x in r['calls']:
            wr.writerow({**{k:x[k] for k in ('callsite','helper','target','confidence')},'nearby_mov_r0':(x['nearby_mov_r0'] or {}).get('value','')})
    print('calls',len(r['calls']))
    for x in r['calls']: print(x['callsite'],x['helper'],x['nearby_mov_r0'])
if __name__=='__main__':main()
