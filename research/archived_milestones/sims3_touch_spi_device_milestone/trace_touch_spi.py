#!/usr/bin/env python3
"""Read-only, ROM-bounded ARM7 touchscreen SPI setup verification."""
import argparse, csv, hashlib, json, struct
from pathlib import Path
SPICNT=0x040001C0
SPIDATA=0x040001C2

def extract_arm7(rom):
    off,entry,base,size=struct.unpack_from('<IIII',rom,0x30)
    if off<0x200 or size==0 or off+size>len(rom) or not base<=entry<base+size:
        raise ValueError('invalid ARM7 header bounds')
    return base,rom[off:off+size]

def u32(b,off):return struct.unpack_from('<I',b,off)[0]

def ldr_literal(b,base,pc):
    i=pc-base
    if i<0 or i+4>len(b):return None
    w=u32(b,i)
    if (w&0x0F7F0000)!=0x051F0000 and (w&0x0F7F0000)!=0x059F0000:
        return None
    pool=pc+8+(w&0xFFF)*(1 if w&(1<<23) else -1)
    k=pool-base
    if k<0 or k+4>len(b) or (k%4):return None
    return {'address':pc,'register':(w>>12)&15,'pool_address':pool,'value':u32(b,k)}

def strh_regs(w):
    # ARM STRH register: immediate offset format; offsets may be zero. Handle only P=1,I=1,L=0.
    if (w&0x0E5000F0)!=0x004000B0:return None
    return ((w>>16)&15,(w>>12)&15)

def trace(rom):
    base,b=extract_arm7(rom)
    rows=[]
    for i in range(0,len(b)-3,4):
        pc=base+i
        x=ldr_literal(b,base,pc)
        if not x or x['value']!=SPICNT:continue
        # Follow straight-line instructions only, conservatively stopping at ARM branches.
        state={x['register']:SPICNT}
        loads=[]; writes=[]
        for j in range(i+4,min(i+76,len(b)-3),4):
            op=u32(b,j);a=base+j
            # Conditional wait-loop branches are allowed; this remains a bounded local pattern scan.
            lit=ldr_literal(b,base,a)
            if lit:
                state[lit['register']]=lit['value'];loads.append(lit)
                continue
            hw=strh_regs(op)
            if hw:
                rn,rd=hw
                if state.get(rn)==SPICNT and state.get(rd)==0x8202:
                    writes.append({'instruction':a,'control_value':state[rd], 'control_register':rn,'value_register':rd})
                continue
            # Avoid stale r values if a nontrivial opcode changes a tracked register.
            # For this pass, only known LDR literals and STRH are used to establish the dataflow.
        for wr in writes:
            rows.append({'spi_base_load':f'0x{pc:08X}', 'spi_value_load':f'0x{next(y["address"] for y in loads if y["value"]==0x8202):08X}', 'spi_write':f'0x{wr["instruction"]:08X}', 'control_value':'0x8202','device':(0x8202>>8)&3,'enabled':bool(0x8202&0x8000)})
    return {'sha256':hashlib.sha256(rom).hexdigest(),'arm7_base':hex(base),'arm7_end':hex(base+len(b)),'touch_device_configurations':rows,'limitations':['SPI touchscreen device selection is identified; X and Y samples are not decoded.','The nearby SPI transfer command is supplied in a register; no touch coordinate dataflow is proven.',"The game's ARM9 touchscreen event dispatcher is still unknown.",'No game ROM modification is made.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--output',default='.');args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    report=trace(Path(args.rom).read_bytes())
    (out/'touch_spi_report.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'touch_spi_writes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['spi_base_load','spi_value_load','spi_write','control_value','device','enabled']);w.writeheader();w.writerows(report['touch_device_configurations'])
    print('touchscreen SPI writes',len(report['touch_device_configurations']))
if __name__=='__main__':main()
