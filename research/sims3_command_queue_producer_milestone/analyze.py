#!/usr/bin/env python3
"""Verify ARM7 record producer, pointer queue, and consumer on original VS3E ROM."""
import argparse, hashlib, json, struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
ANCHORS={
 0x0238C4C0:0xE92D000F, 0x0238C4C8:0xE1DD21B8,
 0x0238C4D0:0xE3520004, 0x0238C4EC:0xE59FC090,
 0x0238C500:0xE782500E, 0x0238C510:0xE78C400E,
 0x0238C514:0xE1DD11B8, 0x0238C534:0xE5154004,
 0x0238C53C:0xE5824314, 0x0238C550:0xE2842001,
 0x0238C554:0xE202200F,0x0238C558:0xE581248C,
 0x0238C560:0xE59F0020,0x0238C56C:0xE59F0018,
 0x0238C588:0x0380B5A8,0x0238C58C:0x0380B548,
 0x02385BDC:0xE92D40F8,0x02385C40:0xE7825101,
 0x02385C44:0xE596101C,0x02385C48:0xE2811001,
 0x02385C68:0xE92D40F8,0x02385CB8:0x15961010,
 0x02385CBC:0x15960018,0x02385CC0:0x17910100,
 0x02385CC4:0x15850000,0x02385CEC:0xEBFFFE2A,
 0x0238C5D0:0xE59D0000,0x0238C5D4:0xE5901000,
 0x0238C614:0x0380B548,
}
EDGES={0x0238C570:0x02385BDC,0x0238C5CC:0x02385C68,0x0238C604:0x0238C7F0}
PRODUCER=0x0238C4C0
EXPECTED_PRODUCER_CALLERS=[0x0238C784,0x0238C7AC,0x0238D400,0x0238D43C,0x0238D4E4,0x0238D768,0x0238D7D8,0x0238D820,0x0238DB5C,0x0238E158,0x0238E214,0x0238E25C,0x0238E724]
def word(data,offset): return struct.unpack_from('<I',data,offset)[0]
def bl_target(op,pc):
 if (op&0x0f000000)!=0x0b000000: return None
 delta=op&0xffffff
 if delta&0x800000:delta-=1<<24
 return pc+8+delta*4

def analyze(data,verify_sha=True):
 sha=hashlib.sha256(data).hexdigest()
 if verify_sha and sha!=SHA: raise ValueError('Unsupported ROM SHA-256')
 if len(data)<0x40:raise ValueError('Truncated ROM')
 off,base,size=[word(data,x) for x in (0x30,0x38,0x3c)]
 if base!=BASE or off+size>len(data):raise ValueError('ARM7 bounds incorrect')
 def at(address):
  delta=address-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('ARM7 address outside code')
  return word(data,off+delta)
 for addr,opcode in ANCHORS.items():
  if at(addr)!=opcode:raise ValueError(f'Instruction mismatch at {addr:#010x}')
 for site,target in EDGES.items():
  if bl_target(at(site),site)!=target:raise ValueError(f'BL mismatch at {site:#010x}')
 callers=[]
 for delta in range(0,size-3,4):
  address=base+delta
  if bl_target(word(data,off+delta),address)==PRODUCER:callers.append(address)
 if callers!=EXPECTED_PRODUCER_CALLERS:raise ValueError('Producer caller set mismatch')
 return {'rom_sha256':sha, 'arm7_base':hex(base),'arm7_rom_offset':hex(off),'checked_instruction_anchors':len(ANCHORS),'checked_queue_edges':len(EDGES), 'producer':hex(PRODUCER), 'producer_callers':[hex(x) for x in callers], 'queue':{'entry':'0x02385BDC','consumer':'0x02385C68','producer_enqueue_call':'0x0238C570','consumer_dequeue_call':'0x0238C5CC','pointer_queue_context_literal':'0x0380B548','consumer_context_literal':'0x0380B548','ring_index_mask':'0xF','ring_capacity_slots':16,'record_words_max':4,'record_parameter_count':'halfword at entry stack+24, <=4','record_copy_instruction':'0x0238C53C','producer_count_increment':'0x02385C48','consumer_pointer_load':'0x02385CC0'}, 'limitations':['Static structural inference; runtime execution unverified','Shared record type versus hardware touchscreen cannot be inferred from this path','ARM9 handoff and X/Y coordinate decoder not found']}
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--out',default='results.json');a=p.parse_args()
 r=analyze(Path(a.rom).read_bytes());Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print('Verified',len(r['producer_callers']),'producer callers,',r['checked_instruction_anchors'],'anchors and',r['checked_queue_edges'],'edges')
if __name__=='__main__':main()
