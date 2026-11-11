#!/usr/bin/env python3
"""Read-only ROM ARM9 GPU-register reference scanner. Does not modify ROM."""
import argparse,csv,hashlib,json,struct
from pathlib import Path
REGS={0x04000304:'POWCNT1 LCD/2D-engine routing',0x04000000:'DISPCNT main engine',0x04001000:'DISPCNT sub engine',0x04000064:'DISPCAPCNT display capture',0x04000240:'VRAMCNT_A',0x04000008:'BG0CNT main',0x04001008:'BG0CNT sub',0x0400006C:'DISP3DCNT 3D display control'}
def w(b,i): return struct.unpack_from('<I',b,i)[0]
def scan(path):
 with path.open('rb') as f:
  hdr=f.read(0x200); off=w(hdr,0x20); entry=w(hdr,0x24); base=w(hdr,0x28); size=w(hdr,0x2c)
  if not 0x200<=off<path.stat().st_size or off+size>path.stat().st_size:raise ValueError('invalid ARM9 layout')
  f.seek(off); data=f.read(size)
 literal_hits={a:[] for a in REGS}; instructions=[]
 for pos in range(0,len(data)-3,4):
  value=w(data,pos)
  if value in REGS:literal_hits[value].append(pos)
 # ARM-state PC-relative literal loads; not a full disassembler.
 for i in range(0,len(data)-3,4):
  instr=w(data,i)
  if ((instr>>26)&3)!=1 or ((instr>>25)&1) or not((instr>>20)&1) or ((instr>>16)&15)!=15 or ((instr>>22)&1):continue
  imm=instr&0xfff
  target=i+8+(imm if instr&(1<<23) else -imm)
  if target<0 or target+4>len(data) or target%4:continue
  value=w(data,target)
  if value in REGS:
   instructions.append(dict(register=REGS[value],register_address=f'0x{value:08X}',arm9_instruction=f'0x{base+i:08X}',rom_instruction=f'0x{off+i:08X}',instruction_word=f'0x{instr:08X}',literal_address=f'0x{base+target:08X}',destination_register=f'r{(instr>>12)&15}',confidence='ARM-state LDR-literal pattern; control flow unverified'))
 with path.open('rb') as checkfile: digest=hashlib.file_digest(checkfile,'sha256').hexdigest()
 result={'rom_sha256':digest,'arm9_offset':f'0x{off:X}','arm9_load':f'0x{base:X}','arm9_entry':f'0x{entry:X}','arm9_size':size,'registers':[{'name':name,'address':f'0x{addr:08X}','aligned_literal_count':len(literal_hits[addr]),'aligned_literal_addresses':[f'0x{base+p:08X}' for p in literal_hits[addr]],'matching_arm_ldr_count':sum(x['register_address']==f'0x{addr:08X}' for x in instructions)} for addr,name in REGS.items()],'candidate_arm_instructions':instructions,'limitations':['The scan handles ARM-state LDR PC-relative literal patterns only, not Thumb, computed register addresses, or control-flow reachability.','These results locate references to display hardware, NOT confirmed routines that move the UI.','Do not change a register literal without understanding all call sites and engine state.']}
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('-o','--output',type=Path,default=Path('display_report.json'));a=p.parse_args();r=scan(a.rom);a.output.write_text(json.dumps(r,indent=2)+'\n');
 with a.output.with_suffix('.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=['register','register_address','arm9_instruction','rom_instruction','instruction_word','literal_address','destination_register','confidence']);wr.writeheader();wr.writerows(r['candidate_arm_instructions'])
 print('Found',len(r['candidate_arm_instructions']),'potential ARM literal-load references; read-only')
if __name__=='__main__':main()
