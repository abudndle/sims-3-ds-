"""Verify ARM9 touchscreen synchronization gate in original VS3E ROM."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02004000
ANCHORS={
0x020D7894:0xE92D4038,0x020D7898:0xE3A05001,0x020D78A0:0xE1A00005,
0x020D78A4:0xEB0000EB,0x020D78A8:0xE59F1034,0x020D78AC:0xE1D103B8,
0x020D78B0:0xE3100001,0x020D78B4:0x11A00005,0x020D78B8:0x18BD8038,
0x020D78E4:0x0224FCE4,0x020D7934:0xE92D4010,0x020D793C:0xE3A00001,
0x020D7940:0xEB0000C4,0x020D7944:0xE1A00004,0x020D7948:0xEBFFFFE6,
0x020D7C58:0xE59F100C,0x020D7C5C:0xE1D123BA,0x020D7C60:0xE1120000,
0x020D7C64:0x1AFFFFFC,0x020D7C68:0xE12FFF1E,0x020D7C6C:0x0224FCE4}
def u32(data,offset):
 if offset<0 or offset+4>len(data):raise ValueError('truncated word')
 return struct.unpack_from('<I',data,offset)[0]
def branch_target(insn,address):
 if insn&0x0e000000!=0x0a000000:raise ValueError('not an ARM branch')
 imm=insn&0xffffff
 if imm&0x800000:imm-=0x1000000
 return (address+8+4*imm)&0xffffffff
def literal_target(insn,address):
 if insn&0x0f7f0000!=0x051f0000:raise ValueError('not a PC-relative ARM literal load')
 imm=insn&0xfff
 return (address+8+(imm if insn&0x800000 else -imm))&0xffffffff
def scan_bl_to(rom,off,base,size,target):
 out=[]
 for delta in range(0,size-3,4):
  insn=u32(rom,off+delta)
  if insn&0x0f000000==0x0b000000 and branch_target(insn,base+delta)==target:out.append(base+delta)
 return out
def inspect(rom,require_sha=True):
 digest=hashlib.sha256(rom).hexdigest()
 if require_sha and digest!=SHA:raise ValueError('original ROM SHA256 mismatch')
 off,base,size=(u32(rom,p) for p in (0x20,0x28,0x2c))
 if base!=BASE or size<=0 or off+size>len(rom):raise ValueError('invalid ARM9 region')
 def at(addr):
  delta=addr-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('outside ARM9 section')
  return u32(rom,off+delta)
 for addr,opcode in ANCHORS.items():
  if at(addr)!=opcode:raise ValueError(f'anchor mismatch {addr:#x}')
 for load,literal in ((0x020D78A8,0x020D78E4),(0x020D7C58,0x020D7C6C)):
  if literal_target(at(load),load)!=literal:raise ValueError('input-state literal mismatch')
 for call in (0x020D78A4,0x020D7940):
  if branch_target(at(call),call)!=0x020D7C58:raise ValueError('gate call mismatch')
 if branch_target(at(0x020D7C64),0x020D7C64)!=0x020D7C5C:raise ValueError('gate retry mismatch')
 calls=scan_bl_to(rom,off,base,size,0x020D7C58)
 if calls!=[0x020D78A4,0x020D7940]:raise ValueError(f'gate caller inventory mismatch: {calls}')
 return {'sha256':digest,'gate':'0x020d7c58','state_block':'0x0224fce4',
 'state_halfword_offset':26,'mask':'supplied in r0 (1 at both callers)',
 'loop':'LDRH [state+0x1a]; TST r2,r0; BNE 0x020d7c5c',
 'call_sites':[hex(x) for x in calls],'anchor_count':len(ANCHORS),
 'scope':'Loaded ARM9 aligned direct BL scan only; indirect/Thumb/overlays excluded',
 'unresolved':['callback registration writer','gameplay UI dispatcher','modified ROM gameplay']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path)
 p.add_argument('--out',type=Path,default=Path('arm9_sync_gate.json'))
 a=p.parse_args();r=inspect(a.rom.read_bytes())
 a.out.write_text(json.dumps(r,indent=2)+'\n');print('Verified',len(r['call_sites']),'direct callers')
