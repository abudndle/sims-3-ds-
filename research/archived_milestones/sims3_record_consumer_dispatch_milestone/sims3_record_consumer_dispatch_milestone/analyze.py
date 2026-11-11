#!/usr/bin/env python3
"""Verify ARM7 record consumer dispatch and selectors in original Sims 3 DS ROM."""
import argparse, hashlib, json, struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
# key: address, value exact ARM opcode
ANCHORS={
 0x0238C5D4:0xE5901000, 0x0238C5D8:0xE3510003,
 0x0238C5E0:0xE08F1081,0x0238C5E4:0xE1D110B4,0x0238C5E8:0xE08FF001,
 0x0238C5F4:0xEB0004C9,0x0238C5FC:0xEB00076D,
 0x0238C604:0xEB000079,0x0238C60C:0xEBDF75AB,
 0x0238D928:0xE59A1004,0x0238D930:0xE3510002,
 0x0238D93C:0xE3510000,0x0238D944:0xE3510001,
 0x0238D94C:0xE3510002,0x0238D958:0xE3510010,
 0x0238E3E4:0xE5961004,0x0238E3E8:0xE3510040,
 0x0238E3F0:0xE3510041,0x0238E3F8:0xE3510042,
}
JUMP_CASE_TARGETS={0:0x0238C5F4,1:0x0238C60C,2:0x0238C5FC,3:0x0238C604}
CALL_TARGETS={0x0238C5F4:0x0238D920,0x0238C5FC:0x0238E3B8,0x0238C604:0x0238C7F0}

def u32(data, at): return struct.unpack_from('<I',data,at)[0]
def bl_target(op,at):
 if (op & 0x0F000000)!=0x0B000000:return None
 imm=op&0xffffff
 if imm&0x800000:imm-=1<<24
 return (at+8+imm*4)&0xffffffff

def inspect(data,check_sha=True):
 sha=hashlib.sha256(data).hexdigest()
 if check_sha and sha!=SHA:raise ValueError('Unsupported original ROM SHA-256')
 offset=u32(data,0x30); base=u32(data,0x38); size=u32(data,0x3c)
 if base!=BASE or offset+size>len(data):raise ValueError('ARM7 bounds invalid')
 def instruction(addr):
  relative=addr-base
  if relative<0 or relative+4>size or relative%4:raise ValueError('Invalid ARM7 address')
  return u32(data,offset+relative)
 for addr,expected in ANCHORS.items():
  actual=instruction(addr)
  if actual!=expected:raise ValueError(f'Unexpected opcode at {addr:#010x}: {actual:#010x}')
 # ARM PC-relative halfword jump-table offsets relative to base 0x0238C5F0
 table=[struct.unpack_from('<H',data,offset+(0x0238C5EC-base)+2*i)[0] for i in range(4)]
 destinations={i:0x0238C5F0+value for i,value in enumerate(table)}
 if destinations!=JUMP_CASE_TARGETS:raise ValueError('Consumer jump table mismatch')
 for addr,target in CALL_TARGETS.items():
  if bl_target(instruction(addr),addr)!=target:raise ValueError(f'Consumer branch mismatch at {addr:#x}')
 anomalous=bl_target(instruction(0x0238C60C),0x0238C60C)
 # Record this odd target rather than assuming it's executable code.
 return {'rom_sha256':sha,'consumer':'0x0238C5B0',
   'record_type_jump_table':{str(k):f'0x{v:08X}' for k,v in destinations.items()},
   'confirmed_consumer_handlers':{'0':'0x0238D920','2':'0x0238E3B8','3':'0x0238C7F0'},
   'type_0_secondary_selectors':[0,1,2,16],
   'type_2_secondary_selectors':[64,65,66],
   'type_1_branch_target_as_encoded':f'0x{anomalous:08X}',
   'type_1_branch_within_arm7':base<=anomalous<base+size,
   'verified_opcode_anchors':len(ANCHORS),'verified_branch_targets':len(CALL_TARGETS),
   'notes':['Type 1 points to an out-of-ARM7-image BL target as statically encoded; runtime interpretation is unresolved.',
    'Type 1 exists in consumer switch although the previously scanned 13 direct producer calls only created record types 0,2,3.',
    'Record type and selector values are not equivalent to touchscreen coordinate samples.',
    'Static ROM inspection only; no modified game or in-emulator test.']}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='results.json');a=ap.parse_args()
 result=inspect(Path(a.rom).read_bytes())
 Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
 print('Verified',result['verified_opcode_anchors'],'opcodes;',result['verified_branch_targets'],'handler edges')
if __name__=='__main__':main()
