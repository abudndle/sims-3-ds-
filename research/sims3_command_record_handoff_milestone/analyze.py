#!/usr/bin/env python3
"""Read-only ARM7 command record handoff checks, original Sims 3 DS VS3E."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
ANCHORS={
 0x0238C5B0:0xE92D407C, # entry
 0x0238C5B4:0xE59F6058, # r6 <- pool constant
 0x0238C5B8:0xE28D5000, # r5 <- sp, output pointer
 0x0238C5C0:0xE1A00006, # queue context r0
 0x0238C5C4:0xE1A01005, # r1 <- output pointer
 0x0238C5C8:0xE1A02004, # r2 <- 1
 0x0238C5D0:0xE59D0000, # r0 <- [sp] record pointer
 0x0238C5D4:0xE5901000, # r1 <- [r0] type
 0x0238C5D8:0xE3510003, # dispatch bound
 0x0238C5E0:0xE08F1081, # jump table indexing
 0x0238C5E4:0xE1D110B4, # load jump offset
 0x0238C5E8:0xE08FF001, # calculated PC
 0x0238C5EC:0x001C0004, # jump table data
 0x0238C5F0:0x0014000C,
 0x0238C614:0x0380B548, # queue/context literal
 0x0238C7F0:0xE92D41F0,
 0x0238C7F4:0xE1A04000, # r4 retains record pointer
 0x0238C8BC:0xE5947008, # selector [record+8]
 0x0238C8C0:0xE594800C, # parameter [record+12]
 0x0238C8F8:0xE1A01808,
 0x0238C900:0xE1A01821,
}
CALLS={0x0238C5CC:0x02385C68,0x0238C604:0x0238C7F0,0x0238C904:0x0238CB20}
def word(b,i):return struct.unpack_from('<I',b,i)[0]
def branch_target(op,pc):
 if op & 0x0F000000 != 0x0B000000:return None
 n=op&0xFFFFFF
 if n&0x800000:n-=1<<24
 return pc+8+4*n
def analyze(data,strict=True):
 sha=hashlib.sha256(data).hexdigest()
 if strict and sha!=SHA:raise ValueError('Unsupported ROM revision')
 off,base,size=[word(data,x) for x in (0x30,0x38,0x3c)]
 if base!=BASE or off+size>len(data):raise ValueError('Invalid ARM7 bounds')
 def at(addr):
  delta=addr-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('Address outside ARM7')
  return word(data,off+delta)
 for addr,op in ANCHORS.items():
  if at(addr)!=op:raise ValueError(f'Opcode differs at {addr:08X}')
 for addr,target in CALLS.items():
  if branch_target(at(addr),addr)!=target:raise ValueError(f'Call differs at {addr:08X}')
 return {'sha256':sha,'verified_opcodes':len(ANCHORS),'verified_calls':len(CALLS),
 'producer':{'entry':'0x0238C5B0','context_literal':'0x0380B548','read_call':'0x0238C5CC','read_target':'0x02385C68','out_pointer':'sp','returned_record_load':'0x0238C5D0','record_type_load':'0x0238C5D4','record_type_bound':'3','dispatch':'4-way PC-relative halfword branch table','table_offsets':[4,28,12,20],'record_type_3_handler':'0x0238C604 (branch-table base 0x0238C5F0 + 0x14)'},
 'selected_case':{'call':'0x0238C604','destination':'0x0238C7F0','record_pointer_passed':'r0','record_pointer_preserved':'r4 at 0x0238C7F4','selector':'[r4+8] at 0x0238C8BC','parameter':'[r4+12] at 0x0238C8C0','downstream_call':'0x0238C904 to 0x0238CB20'},
 'limitations':['Static ARM-state instruction analysis only','Producer is a record dequeue/receive-like helper; IPC or hardware source not established','No touch X/Y decoder, ARM9 event bridge, runtime execution, or mod ROM demonstrated']}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='results.json');args=ap.parse_args()
 result=analyze(Path(args.rom).read_bytes());Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
 print(f"Verified {result['verified_opcodes']} ARM instructions/data anchors, {result['verified_calls']} call targets")
if __name__=='__main__':main()
