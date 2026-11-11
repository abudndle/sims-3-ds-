#!/usr/bin/env python3
"""Read-only ARM9 input/IPC literal-reference scanner for Sims 3 DS.
No speculative hooks or ROM writes. ARM-state PC-relative LDR only.
"""
import argparse, csv, hashlib, json, struct
from pathlib import Path
REGS={0x04000130:'KEYINPUT',0x04000136:'EXTKEYIN',0x04000180:'IPCSYNC',0x04000184:'IPCFIFOCNT',0x04000188:'IPCFIFOSEND',0x04100000:'IPCFIFORECV'}
def u32(b,i): return struct.unpack_from('<I',b,i)[0]
def arm9(rom):
    if len(rom)<0x200:raise ValueError('short ROM')
    off, base, size=struct.unpack_from('<III',rom,0x20)
    if not (off>=0x200 and base>=0x02000000 and size>=4 and off+size<=len(rom)):raise ValueError('invalid ARM9 region')
    return off,base,rom[off:off+size]
def scan(rom):
    off,base,b=arm9(rom)
    rows=[]
    literals={v:[] for v in REGS}
    for i in range(0,len(b)-3,4):
        val=u32(b,i)
        if val in REGS:literals[val].append(i)
    for i in range(0,len(b)-3,4):
        op=u32(b,i)
        # ARM LDR Rd, [pc, +/- 12bit immediate]; pre-indexed, word aligned,
        # omit conditional NV; values need verification as actual code not data.
        if (op&0x0f7f0000)!=0x051f0000 or (op>>28)==15:continue
        t=i+8+(op&0xfff)*(1 if op&(1<<23) else -1)
        if t<0 or t+4>len(b) or t%4:continue
        val=u32(b,t)
        if val not in REGS:continue
        rows.append(dict(register=REGS[val],mmio=f'0x{val:08X}',instruction=f'0x{base+i:08X}',opcode=f'0x{op:08X}',literal=f'0x{base+t:08X}',destination=f'r{(op>>12)&15}',condition=f'{op>>28:X}',rom_offset=f'0x{off+i:X}',context=[f'0x{base+j:08X}:0x{u32(b,j):08X}' for j in range(max(0,i-16),min(len(b)-3,i+20),4)]))
    return {'sha256':hashlib.sha256(rom).hexdigest(),'arm9_base':f'0x{base:08X}','arm9_rom_offset':f'0x{off:X}','arm9_size':len(b),'references':rows,'literal_counts':{REGS[k]:len(v) for k,v in literals.items()},'caveats':['Static ARM opcode pattern only; literal references are not proven executed code','Does not decode ARM7, Thumb or instructions accessing indirect touch state','No function boundaries or safe code-injection hook established']}
def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('--output',type=Path,default=Path('input_references.json')); a=p.parse_args()
    obj=scan(a.rom.read_bytes());a.output.write_text(json.dumps(obj,indent=2)+'\n')
    with a.output.with_suffix('.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['register','mmio','instruction','opcode','literal','destination','condition','rom_offset']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in obj['references'])
    print({r:sum(x['register']==r for x in obj['references']) for r in REGS.values()})
if __name__=='__main__':main()
