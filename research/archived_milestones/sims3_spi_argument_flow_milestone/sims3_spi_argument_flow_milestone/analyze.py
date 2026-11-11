#!/usr/bin/env python3
"""Static, conservative ARM argument provenance for direct SPI helper calls."""
import argparse,csv,hashlib,json,struct
from pathlib import Path
HELPERS={0x0238C9D8:'spi_send',0x0238CA54:'spi_read'}
def word(buf,pos):return struct.unpack_from('<I',buf,pos)[0]
def branch_target(w,pc):
    if (w&0x0f000000)!=0x0b000000:return None
    disp=w&0xffffff
    if disp&0x800000: disp-=0x1000000
    return pc+8+disp*4

def decode_arg(w,register):
    """Identify directly preceding unconditional assignments to rN, not arbitrary data flow."""
    if w>>28!=14:return None
    rd=(w>>12)&15
    if rd!=register:return None
    # MOV rN, #imm (rotated immediate)
    if w&0x0fe00000==0x03a00000:
        imm=w&255; shift=((w>>8)&15)*2
        n=((imm>>shift)|(imm<<(32-shift)))&0xffffffff if shift else imm
        return {'kind':'constant','value':n}
    # MOV rN, rM, with no shift
    if (w&0x0fe00ff0)==0x01a00000:
        return {'kind':'register','source':f'r{w&15}'}
    # AND rN,rM,#imm
    if w&0x0fe00000==0x02000000:
        imm=w&255;shift=((w>>8)&15)*2
        n=((imm>>shift)|(imm<<(32-shift)))&0xffffffff if shift else imm
        return {'kind':'masked-register','source':f'r{(w>>16)&15}', 'mask':n}
    return {'kind':'other-write','word':f'0x{w:08X}'}

def analyze(rom):
    off=word(rom,0x30);base=word(rom,0x38);size=word(rom,0x3c)
    if size==0 or off+size>len(rom) or size%4:raise ValueError('ARM7 bounds invalid')
    arm7=rom[off:off+size];found=[]
    for i in range(0,len(arm7)-3,4):
        pc=base+i;dest=branch_target(word(arm7,i),pc)
        if dest not in HELPERS:continue
        args={}
        for reg in (0,1):
            history=[]
            # Inspect 4 preceding instructions only, never crossing a branch.
            for back in range(4,0,-1):
                j=i-back*4
                if j<0:continue
                w=word(arm7,j);a=base+j
                history.append((a,w))
            # Only claim a direct predecessor assignment if nearest instruction writes that register.
            a=pc-4;w=word(arm7,i-4)
            direct=decode_arg(w,reg)
            # A branch, call, or condition prevents a strong claim without CFG.
            if direct is not None:
                args[f'r{reg}']={'provenance':direct,'address':f'0x{a:08X}', 'confidence':'immediate-predecessor'}
            else:
                # Find most recent simple assignment as a *lead*, not a confirmed value
                lead=None
                for a,w in reversed(history):
                    d=decode_arg(w,reg)
                    if d is not None:
                        lead={'provenance':d,'address':f'0x{a:08X}'};break
                    if w&0x0e000000==0x0a000000 or (w&0x0f000000)==0x0b000000:break
                args[f'r{reg}']={'provenance':lead,'confidence':'unverified-backward-lead' if lead else 'unknown'}
        found.append({'callsite':f'0x{pc:08X}','callee':HELPERS[dest],**args})
    return {'sha256':hashlib.sha256(rom).hexdigest(),'arm7_load':f'0x{base:08X}','arm7_size':size,'calls':found}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='results');args=ap.parse_args()
    result=analyze(Path(args.rom).read_bytes());out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
    (out/'argument_flow.json').write_text(json.dumps(result,indent=2)+'\n')
    with (out/'argument_flow.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['callsite','callee','r0_confidence','r0_provenance','r1_confidence','r1_provenance'])
        for c in result['calls']:
            wr.writerow([c['callsite'],c['callee'],c['r0']['confidence'],json.dumps(c['r0']['provenance']),c['r1']['confidence'],json.dumps(c['r1']['provenance'])])
    print(f"{len(result['calls'])} SPI helper callsites mapped")
    for c in result['calls']:print(c['callsite'],c['callee'],'r0=',c['r0'],'r1=',c['r1'])
if __name__=='__main__':main()
