"""Read-only ARM9 touchscreen unpack/callback boundary verification for Sims 3 DS VS3E."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
ANCHORS={
0x020D74EC:0xE59F1108,0x020D74F0:0xE1D140B0,0x020D74F4:0xE1D110B2,
0x020D74F8:0xE1CD40B0,0x020D74FC:0xE1CD10B2,0x020D7500:0xE59D4000,
0x020D7504:0xE1A01A04,0x020D7508:0xE1A05A21,0x020D750C:0xE1A0E404,
0x020D7510:0xE1A01384,0x020D7514:0xE1A0CFA1,0x020D7518:0xE1A01284,
0x020D751C:0xE1A01F21,0x020D7520:0xE1C350B8,0x020D7524:0xE1A0EA2E,
0x020D7528:0xE1C3E0BA,0x020D752C:0xE20CC0FF,0x020D7530:0xE1C3C0BC,
0x020D7534:0xE20110FF,0x020D7538:0xE1C310BE,0x020D753C:0xE1C323B6,
0x020D7564:0xE5933004,0x020D7568:0xE3530000,0x020D756C:0x028DD008,
0x020D7570:0x08BD80F8,0x020D7574:0xE3A01000,0x020D7578:0xE1A02001,
0x020D757C:0xE12FFF33,0x020D7580:0xE28DD008,0x020D7584:0xE8BD80F8,
0x020D75FC:0x02FFFFAA}
def decode_fields(word):
 if type(word) is not int or not 0<=word<=0xffffffff:raise ValueError('unsigned 32-bit word required')
 return {'raw_x':word&4095,'raw_y':(word>>12)&4095,'pen_down':(word>>24)&1,
         'sample_status':(word>>25)&3,'high5':(word>>27)&31}
def branch_exchange_register(opcode):
 if opcode&0x0ffffff0!=0x012fff30:raise ValueError('not ARM BLX register')
 return opcode&15
def literal_address(opcode,address):
 if opcode&0x0f7f0000!=0x051f0000:raise ValueError('not PC-relative LDR')
 v=opcode&4095
 return address+8+(v if opcode&(1<<23) else -v)
def inspect(rom,check_sha=True):
 digest=hashlib.sha256(rom).hexdigest()
 if check_sha and digest!=SHA:raise ValueError('ROM SHA256 mismatch')
 if len(rom)<0x30:raise ValueError('invalid ROM header')
 off,base,size=(struct.unpack_from('<I',rom,x)[0] for x in (0x20,0x28,0x2c))
 if base!=0x02004000 or off+size>len(rom):raise ValueError('ARM9 region invalid')
 def read(addr):
  d=addr-base
  if d<0 or d+4>size or d%4:raise ValueError('ARM9 address outside range')
  return struct.unpack_from('<I',rom,off+d)[0]
 for addr,expected in ANCHORS.items():
  if read(addr)!=expected:raise ValueError(f'ARM9 anchor mismatch at {addr:#x}')
 if literal_address(read(0x020D74EC),0x020D74EC)!=0x020D75FC:raise ValueError('wrong shared-memory pointer')
 if branch_exchange_register(read(0x020D757C))!=3:raise ValueError('callback must use r3')
 return {'sha256':digest,'verified_anchors':len(ANCHORS),'shared_source':'0x02FFFFAA',
  'consumer':'0x020D74EC','destination_offsets':{'x':8,'y':10,'pen':12,'status':14,'message':6},
  'callback_pointer_offset':4,'callback_call':'0x020D757C',
  'callback_arguments':{'r1':0,'r2':0},
  'limitations':['Indirect callback destination is runtime-dependent.',
                 'Gameplay UI consumer and pixel calibration remain unverified.',
                 'Static check only; no patched ROM or emulator hook tested.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path)
 p.add_argument('--output',type=Path,default=Path('arm9_event_boundary.json'))
 a=p.parse_args();r=inspect(a.rom.read_bytes())
 a.output.write_text(json.dumps(r,indent=2)+'\n');print('Verified ARM9 unpack/callback boundary')
