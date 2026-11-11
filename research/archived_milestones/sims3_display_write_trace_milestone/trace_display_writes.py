#!/usr/bin/env python3
"""Conservative ARM-state direct display-register use tracer, read-only.
Tracks a PC-relative LDR of a known MMIO address, then direct ARM LDR/STR and
LDRH/STRH accesses using the loaded base register until a branch/clobber.
Not a whole-program disassembler or dynamic execution proof.
"""
import argparse, csv, hashlib, json, struct
from pathlib import Path
REGS={0x04000304:'POWCNT1',0x04001000:'DISPCNT_SUB',0x04000240:'VRAMCNT_A'}
def word(data,pos):return struct.unpack_from('<I',data,pos)[0]
def decoded_access(inst,reg):
    # ARM mode single data transfer immediate offset, pre/post-index; base register matches
    if (inst>>26)&3 == 1 and not (inst&(1<<25)) and ((inst>>16)&15)==reg:
        off=inst&0xfff
        if not(inst&(1<<23)):off=-off
        if not(inst&(1<<24)):return None # post-index changes base; skip
        return ('read' if inst&(1<<20) else 'write','word',off)
    # ARM mode halfword register/data transfer, immediate offset only
    if (inst & 0x0E4000F0)==0x004000B0 and ((inst>>16)&15)==reg:
        # mask above requires P=1, I=1, bits7+4=1, S/H=01
        off=((inst>>8)&15)*16+(inst&15)
        if not(inst&(1<<23)):off=-off
        return ('read' if inst&(1<<20) else 'write','halfword',off)
    return None
def is_branch(inst):
    return (inst&0x0e000000)==0x0a000000 or (inst&0x0ffffff0)==0x012fff10

def analyze(path):
    with path.open('rb') as f:
        h=f.read(0x200); offset=word(h,0x20); base=word(h,0x28); size=word(h,0x2c)
        if offset<0x200 or offset+size>path.stat().st_size:raise ValueError('invalid ARM9 region')
        f.seek(offset); data=f.read(size)
    results=[]
    for i in range(0,len(data)-4,4):
        inst=word(data,i)
        if (inst&0x0F7F0000)!=0x051F0000:continue # LDR Rd,[PC,+/-imm], word only, preindexed
        imm=inst&0xfff
        target=i+8+(imm if inst&(1<<23) else -imm)
        if target%4 or target<0 or target+4>len(data):continue
        mmio=word(data,target)
        if mmio not in REGS:continue
        reg=(inst>>12)&15
        if reg==15:continue
        accesses=[]
        for j in range(i+4,min(i+4*25,len(data)-3),4):
            x=word(data,j)
            if is_branch(x):break
            act=decoded_access(x,reg)
            if act:
                operation,width,off=act
                accesses.append({'instruction':f'0x{base+j:08X}','opcode':f'0x{x:08X}','operation':operation,'width':width,'offset':off})
            # Stop if another unconditional word LDR or MOV writes the base register.
            if (x>>28)==14 and ((x>>12)&15)==reg and ((x&0x0c000000)==0x04000000 and x&(1<<20)):
                break
        if accesses:
            results.append({'register':REGS[mmio],'mmio':f'0x{mmio:08X}','literal_load':f'0x{base+i:08X}', 'literal_opcode':f'0x{inst:08X}','base_register':f'r{reg}','accesses':accesses})
    return {'rom_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'arm9_load':f'0x{base:08X}','arm9_rom_offset':f'0x{offset:X}','results':results,'limitations':['Static ARM-state pattern match only; conditional execution and function reachability not proven','Accesses with register offset, Thumb instructions, and cross-function flows excluded','No ROM modifications made']}
def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('-o','--out',type=Path,default=Path('display_writes.json'))
    a=p.parse_args(); result=analyze(a.rom);a.out.write_text(json.dumps(result,indent=2)+'\n')
    with a.out.with_suffix('.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['register','mmio','literal_load','instruction','opcode','operation','width','offset']);wr.writeheader()
        for x in result['results']:
            for y in x['accesses']:wr.writerow({**{k:x[k] for k in ['register','mmio','literal_load']},**y})
    print('MMIO load groups:',len(result['results']),'accesses:',sum(len(x['accesses']) for x in result['results']))
if __name__=='__main__':main()
