#!/usr/bin/env python3
"""Read-only verified ARM7 dispatcher argument provenance for Sims 3 DS VS3E."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
# Exact opcode anchors independently checked with llvm-objdump, ARM mode.
ANCHORS={
 0x0238C8BC:0xE5947008, 0x0238C8C0:0xE594800C,
 0x0238C8F8:0xE1A01808,0x0238C8FC:0xE1A00007,0x0238C900:0xE1A01821,
 0x0238CB28:0xE1A08001,0x0238CB2C:0xE3500019,
 0x0238CEF8:0xE1A00008,0x0238CF04:0xE1A00448,
 0x0238CF08:0xE20000FF,0x0238CF0C:0xE20810FF,
 0x0238D220:0xE3A00000,0x0238D318:0xE3A00000,
 0x0238D320:0xE3180040,0x0238D324:0x13A00006,
 0x0238D328:0x03A00007,0x0238D32C:0xE3180080,
 0x0238D330:0x13A08004,0x0238D334:0x03A08005,
 0x0238D338:0xE3A01000,0x0238D340:0xE1A00008,
 0x0238D344:0xE3A01000,
}
CALLS={0x0238C904:0x0238CB20,0x0238CEFC:0x0238CA54,
       0x0238CF10:0x0238C9D8,0x0238D33C:0x0238CB20,
       0x0238D348:0x0238CB20}
def word(data,offset):return struct.unpack_from('<I',data,offset)[0]
def bl_target(op,pc):
 if (op&0x0F000000)!=0x0B000000:return None
 imm=op&0xFFFFFF
 if imm&0x800000:imm-=0x1000000
 return pc+8+(imm<<2)
def analyze(data,strict=True):
 digest=hashlib.sha256(data).hexdigest()
 if strict and digest!=SHA:raise ValueError('Unsupported ROM SHA-256')
 off,base,size=(word(data,p) for p in (0x30,0x38,0x3C))
 if base!=BASE or off+size>len(data):raise ValueError('Bad ARM7 layout')
 def at(addr):
  delta=addr-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('ARM7 range error')
  return word(data,off+delta)
 for addr,opcode in ANCHORS.items():
  if at(addr)!=opcode:raise ValueError(f'Opcode mismatch at {addr:#x}')
 for addr,target in CALLS.items():
  if bl_target(at(addr),addr)!=target:raise ValueError(f'Branch mismatch at {addr:#x}')
 return {'rom_sha256':digest,'anchor_count':len(ANCHORS),'branch_count':len(CALLS),
  'proven_chains':[
   {'call':'0x0238C904','destination':'0x0238CB20','selector_r0':'word at [r4+8] from 0x0238C8BC, stored in r7','parameter_r1':'low 16 bits of word at [r4+12] from 0x0238C8C0, via shifts at 0x0238C8F8/0x0238C900','scope':'this call path only'},
   {'call':'0x0238D33C','destination':'0x0238CB20','selector_r0':'6 if r8 bit 6 set, else 7','parameter_r1':'zero'},
   {'call':'0x0238D348','destination':'0x0238CB20','selector_r0':'4 if original r8 bit 7 set, else 5','parameter_r1':'zero'},
  ],'dispatcher':{'entry':'0x0238CB20','parameter_saved_to_r8':'0x0238CB28','max_selector':25,
    'read_case_24':{'argument':'r8','load':'0x0238CEF8','call':'0x0238CEFC','helper':'0x0238CA54','conclusion':'command value supplied by dispatcher caller; unknown for all contexts'},
    'send_case_25':{'command':'(r8 >> 8) & 0xFF','payload':'r8 & 0xFF','instructions':['0x0238CF04','0x0238CF08','0x0238CF0C'],'call':'0x0238CF10','helper':'0x0238C9D8'}},
   'interpretation':'Command-structure and bit-control dispatch are confirmed. Touch X/Y decoder and runtime SPI device are not confirmed.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--out',default='results.json');a=p.parse_args()
 result=analyze(Path(a.rom).read_bytes());Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print('Verified',result['anchor_count'],'opcodes and',result['branch_count'],'calls')
if __name__=='__main__':main()
