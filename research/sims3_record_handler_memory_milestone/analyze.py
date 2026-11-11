#!/usr/bin/env python3
"""Read-only ARM7 handler memory-write provenance for original Sims 3 DS VS3E."""
import argparse, hashlib, json, struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
# code site, literal load site, literal pool entry, expected literal, store opcode, register offset
PATHS=[
 dict(kind='type0_shared_low',load=0x0238D9EC,pool=0x0238DB2C,value=0x02FFFFAA,store=0x0238D9F0,opcode=0xE1C100B0,offset=0),
 dict(kind='type0_shared_high',load=0x0238D9EC,pool=0x0238DB2C,value=0x02FFFFAA,store=0x0238D9F8,opcode=0xE1C100B2,offset=2),
 dict(kind='type2_shared_flag',load=0x0238E474,pool=0x0238E5B4,value=0x02FFFF94,store=0x0238E478,opcode=0xE1C100B0,offset=0),
 dict(kind='type2_timer3_counter',load=0x0238E4DC,pool=0x0238E5BC,value=0x0400010C,store=0x0238E4E4,opcode=0xE1C210B0,offset=0),
 dict(kind='type2_timer3_control',load=0x0238E4DC,pool=0x0238E5BC,value=0x0400010C,store=0x0238E4F0,opcode=0xE1C210B2,offset=2),
]
# Correct register-specific LDR literal opcodes are determined by PC-relative decoding,
# and shared pools must match; avoid erroneously assuming literal site is an instruction.
def u32(data,at): return struct.unpack_from('<I',data,at)[0]
def literal_addr(inst, at):
 # LDR Rt,[PC,#imm12] with U positive and immediate offset; allows any Rt
 if (inst & 0x0F7F0000)!=0x051F0000: raise ValueError(f'Not PC-relative literal load at {at:#x}: {inst:#x}')
 signed=inst&0xfff
 return (at+8+(signed if inst & (1<<23) else -signed))&0xffffffff

def inspect(rom,check_sha=True):
 sha=hashlib.sha256(rom).hexdigest()
 if check_sha and sha!=SHA: raise ValueError('Wrong original ROM SHA-256')
 off,base,size=u32(rom,0x30),u32(rom,0x38),u32(rom,0x3c)
 if base!=BASE or off+size>len(rom):raise ValueError('ARM7 load information invalid')
 def at(addr):
  delta=addr-base
  if delta<0 or delta+4>size or delta%4:raise ValueError(f'Outside ARM7: {addr:#x}')
  return u32(rom,off+delta)
 records=[]
 for p in PATHS:
  load, pool,store=p['load'],p['pool'],p['store']
  if literal_addr(at(load),load)!=pool:raise ValueError(f'Wrong literal reference at {load:#x}')
  if at(pool)!=p['value']:raise ValueError(f'Unexpected literal at {pool:#x}')
  if at(store)!=p['opcode']:raise ValueError(f'Unexpected store at {store:#x}')
  records.append({'path':p['kind'],'load_instruction':f'{load:#010x}', 'literal_entry':f'{pool:#010x}',
                  'base_address':f'{p["value"]:#010x}','store_instruction':f'{store:#010x}',
                  'effective_address':f'{p["value"]+p["offset"]:#010x}', 'width_bits':16})
 # Verify selector reads and relevant data source operands for type0/2
 anchors={0x0238D928:0xE59A1004,0x0238D9E8:0xE1DD00B8,0x0238D9F4:0xE1DD00BA,
          0x0238E3E4:0xE5961004,0x0238E470:0x12200080,
          0x0238E4D8:0xE1D713B4,0x0238E4E8:0xE1D713B6,0x0238E4EC:0xE38110C0}
 for addr,opcode in anchors.items():
  if at(addr)!=opcode:raise ValueError(f'Bad selector/data opcode at {addr:#x}')
 return {'rom_sha256':sha,'paths':records,'verified_write_paths':len(records),'verified_other_opcodes':len(anchors),
  'interpretation':{'type0':'Two halfword stores to adjacent shared-memory locations 0x02FFFFAA/AC; value source stack offsets +8/+10.','type2':'One shared-memory halfword at 0x02FFFF94 and two Timer 3 MMIO halfword stores to 0x0400010C/0x0400010E.'},
  'limitations':['Static path and address provenance only; branching and runtime execution are unconfirmed.','Shared-memory writes do not prove touchscreen coordinates.','Timer 3 writes are peripheral timer control, not touchscreen ADC reads.','No original ROM modifications or emulator tests.']}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='results.json');args=ap.parse_args()
 result=inspect(Path(args.rom).read_bytes())
 Path(args.out).write_text(json.dumps(result,indent=2)+'\n');print('Verified',result['verified_write_paths'],'write paths')
if __name__=='__main__':main()
