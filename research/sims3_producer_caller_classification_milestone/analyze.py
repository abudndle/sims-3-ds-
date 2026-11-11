#!/usr/bin/env python3
"""ROM-bound, read-only ARM7 record producer call-site classifier."""
import argparse,hashlib,json,struct,csv
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
PRODUCER=0x0238C4C0
# Exact instruction that writes r0 before each verified direct ARM BL.
SITES={
 0x0238C784:(0x0238C778,3),0x0238C7AC:(0x0238C7A0,3),
 0x0238D400:(0x0238D3F8,3),0x0238D43C:(0x0238D430,3),
 0x0238D4E4:(0x0238D4D8,3),0x0238D768:(0x0238D75C,0),
 0x0238D7D8:(0x0238D7CC,0),0x0238D820:(0x0238D814,0),
 0x0238DB5C:(0x0238DB54,0),0x0238E158:(0x0238E150,2),
 0x0238E214:(0x0238E20C,2),0x0238E25C:(0x0238E254,2),
 0x0238E724:(0x0238E718,2),
}

def word(buf,offset):return struct.unpack_from('<I',buf,offset)[0]
def bl_target(op,addr):
 if op&0x0f000000!=0x0b000000:return None
 v=op&0xffffff
 if v&0x800000:v-=1<<24
 return addr+8+v*4

def classify(data,check_sha=True):
 sha=hashlib.sha256(data).hexdigest()
 if check_sha and sha!=SHA:raise ValueError('Unsupported ROM SHA256')
 off,base,size=(word(data,x) for x in (0x30,0x38,0x3c))
 if base!=BASE or off+size>len(data):raise ValueError('ARM7 section bounds mismatch')
 def read(address):
  rel=address-base
  if rel<0 or rel+4>size or rel%4:raise ValueError('Address not valid ARM7 instruction')
  return word(data,off+rel)
 rows=[]
 for call,(setup,record_type) in SITES.items():
  op=read(setup)
  # ARM MOV r0, #small immediate, unconditional. This is not a general ARM decoder.
  expected=0xE3A00000|record_type
  if op!=expected:raise ValueError(f'Unexpected record-type setup at {setup:#010x}: {op:#010x}')
  call_opcode=read(call)
  if bl_target(call_opcode,call)!=PRODUCER:raise ValueError(f'Producer branch mismatch at {call:#010x}')
  rows.append({'call_address':f'0x{call:08X}','type_setup_address':f'0x{setup:08X}', 'record_type':record_type, 'setup_opcode':f'0x{op:08X}','branch_opcode':f'0x{call_opcode:08X}', 'producer':f'0x{PRODUCER:08X}'})
 # Verify that the list is exhaustive for direct ARM BL within the original ARM7 image.
 all_calls=[]
 for rel in range(0,size-3,4):
  addr=base+rel
  if bl_target(word(data,off+rel),addr)==PRODUCER:all_calls.append(addr)
 if all_calls!=list(SITES):raise ValueError('Unexpected producer caller set')
 counts={str(t):sum(x['record_type']==t for x in rows) for t in (0,2,3)}
 return {'rom_sha256':sha,'total_call_sites':len(rows),'record_type_counts':counts,'sites':rows,
 'limitations':['Record type is an immediate r0 argument at these call sites; downstream semantics require independent verification.', 'Record types do not establish touchscreen sampling or ARM9 UI events.','Static analysis only; ROM not patched or emulator-tested.']}

def main():
 a=argparse.ArgumentParser();a.add_argument('rom');a.add_argument('--out',default='results.json');a.add_argument('--csv',default='callers.csv');x=a.parse_args()
 result=classify(Path(x.rom).read_bytes());Path(x.out).write_text(json.dumps(result,indent=2)+'\n')
 with open(x.csv,'w',newline='') as fp:
  out=csv.DictWriter(fp,fieldnames=list(result['sites'][0]));out.writeheader();out.writerows(result['sites'])
 print('Verified',result['total_call_sites'],'calls:',result['record_type_counts'])
if __name__=='__main__':main()
