#!/usr/bin/env python3
"""Read-only scan for ARM/Thumb PC-relative loads of DS shared IPC/touch candidates."""
import argparse, csv, hashlib, json, struct
from pathlib import Path

CANDIDATES={0x02FFFF90,0x02FFFF94,0x02FFFF98,0x02FFFF9C,0x02FFFFA0,0x02FFFFA4,0x02FFFFA8,0x02FFFFAA,0x02FFFFB0,0x02FFFFB8}

def images(rom):
    for name,hdr in [('ARM9',0x20),('ARM7',0x30)]:
        offset,entry,base,size=struct.unpack_from('<IIII',rom,hdr)
        if offset<0x200 or size<=0 or offset+size>len(rom) or not (base<=entry<base+size):
            raise ValueError(f'{name} header invalid')
        yield name,base,memoryview(rom)[offset:offset+size]

def scan_image(name,base,code):
    result=[];n=len(code)
    for i in range(0,n-1,2):
        ins=struct.unpack_from('<H',code,i)[0]
        if (ins&0xf800)!=0x4800:continue
        pc=base+i; pool=((pc+4)&~3)+4*(ins&255)
        ix=pool-base
        if ix<0 or ix+4>n or ix%4: continue
        v=struct.unpack_from('<I',code,ix)[0]
        if v in CANDIDATES:
            result.append(dict(cpu=name,mode='thumb_ldr_literal',instruction_address=f'0x{pc:08X}',opcode=f'0x{ins:04X}',pool_address=f'0x{pool:08X}',literal_value=f'0x{v:08X}',register=f'r{(ins>>8)&7}'))
    # ARM LDR Rd,[PC,#imm12] with positive/negative PC-relative offset.
    for i in range(0,n-3,4):
        ins=struct.unpack_from('<I',code,i)[0]
        if (ins&0x0e5f0000)!=0x041f0000:continue  # immediate word load, preindex, PC base
        if ins&(1<<22):continue # byte load excluded
        pc=base+i
        delta=(ins&0xfff)*(1 if ins&(1<<23) else -1)
        pool=pc+8+delta;ix=pool-base
        if ix<0 or ix+4>n or ix%4:continue
        v=struct.unpack_from('<I',code,ix)[0]
        if v in CANDIDATES:
            result.append(dict(cpu=name,mode='arm_ldr_literal',instruction_address=f'0x{pc:08X}',opcode=f'0x{ins:08X}',pool_address=f'0x{pool:08X}',literal_value=f'0x{v:08X}',register=f'r{(ins>>12)&15}'))
    return sorted(result,key=lambda x:int(x['instruction_address'],16))

def analyze(rom):
    rows=[]; spans={}
    for name,base,code in images(rom):
        spans[name]={'base':f'0x{base:08X}','end_exclusive':f'0x{base+len(code):08X}'}
        rows.extend(scan_image(name,base,code))
    return dict(sha256=hashlib.sha256(rom).hexdigest(),images=spans,results=rows,limitations=['PC-relative literal loads are candidates, not proven runtime touch data paths.','The ARM instruction scan cannot resolve indirection via register arithmetic or overlays.','No ROM changes or gameplay hook demonstrated.'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='.')
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    report=analyze(Path(a.rom).read_bytes());(out/'handoff.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'handoff.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['cpu','mode','instruction_address','opcode','pool_address','literal_value','register']);w.writeheader();w.writerows(report['results'])
    from collections import Counter
    print('SHA256',report['sha256']);print('counts',Counter((r['cpu'],r['literal_value']) for r in report['results']))
if __name__=='__main__':main()
