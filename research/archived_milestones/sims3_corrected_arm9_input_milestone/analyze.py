#!/usr/bin/env python3
"""Bounded ARM9/Thumb input literal scan for Sims 3 DS; no ROM modifications."""
import argparse,hashlib,json,struct
from pathlib import Path
REGS={'KEYINPUT':0x04000130,'IPCSYNC':0x04000180,'IPCFIFOCNT':0x04000184}

def arm9_region(rom):
    if len(rom)<0x200: raise ValueError('Truncated ROM')
    off,entry,load,size=struct.unpack_from('<IIII',rom,0x20)
    if off<0x200 or size<=0 or off+size>len(rom) or not load<=entry<load+size:
        raise ValueError('Invalid ARM9 header')
    return off,entry,load,rom[off:off+size]

def thumb_literal_target(pc,halfword):
    if (halfword&0xf800)!=0x4800: return None
    return ((pc+4)&~3)+((halfword&0xff)<<2)

def arm_literal_target(pc,word):
    if word>>28==15 or (word&0x0f7f0000)!=0x051f0000:return None
    return pc+8+((word&0xfff) if word&(1<<23) else -(word&0xfff))

def analyze(rom):
    off,entry,base,arm=arm9_region(rom)
    byname=[]
    for label,reg in REGS.items():
        p=struct.pack('<I',reg);start=0
        while (idx:=arm.find(p,start))!=-1:
            if idx%4==0:
                refs=[]
                for pos in range(max(0,idx-0x400),idx,2):
                    ins=struct.unpack_from('<H',arm,pos)[0]
                    if thumb_literal_target(base+pos,ins)==base+idx:
                        refs.append({'address':f'0x{base+pos:08X}','instruction':f'0x{ins:04X}','mode':'Thumb LDR literal'})
                for pos in range(max(0,idx-0x1000),idx,4):
                    ins=struct.unpack_from('<I',arm,pos)[0]
                    if arm_literal_target(base+pos,ins)==base+idx:
                        refs.append({'address':f'0x{base+pos:08X}','instruction':f'0x{ins:08X}','mode':'ARM LDR literal'})
                byname.append({'register':label,'value':f'0x{reg:08X}','literal_address':f'0x{base+idx:08X}','rom_offset':f'0x{off+idx:X}','literal_loads':refs})
            start=idx+1
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),
            'arm9_rom_offset':f'0x{off:X}','arm9_entry':f'0x{entry:08X}',
            'arm9_load':f'0x{base:08X}','arm9_end_exclusive':f'0x{base+len(arm):08X}',
            'previous_routine_address':'0x021BE974',
            'previous_routine_claim_valid':False,
            'explanation':'Earlier analyzer treated ARM9 entry as load address and RAM load address as binary size, scanning outside ARM9; previous function claim withdrawn.',
            'register_literals':byname,
            'limitations':['Static PC-relative instruction matches, not verified runtime execution.','Cannot identify UI touchscreen event dispatcher from these references alone.','No in-game patch or control implementation performed.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('--out',type=Path,default=Path('report.json'))
    args=p.parse_args();report=analyze(args.rom.read_bytes())
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print('ARM9:',report['arm9_load'],'..',report['arm9_end_exclusive'])
    for row in report['register_literals']:
        print(row['register'],row['literal_address'],'references:',len(row['literal_loads']))
if __name__=='__main__':main()
