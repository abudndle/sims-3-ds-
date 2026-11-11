"""Static proof of ARM9 Timer-3 IRQ callback registration in Sims 3 DS VS3E.

Exact ROM-instruction checks. No original game bytes are distributed.
"""
import argparse, hashlib, json, struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02004000
SITES={
0x020D7600:0xE92D4038,0x020D7604:0xE59F4060,
0x020D7640:0xE3A05006,0x020D7644:0xE3A04001,
0x020D7648:0xE1A00005,0x020D764C:0xE1A01004,
0x020D7650:0xEBFFF85A,0x020D7654:0xE3500000,
0x020D7658:0x0AFFFFFA,0x020D765C:0xE59F100C,
0x020D7660:0xE1A00005,0x020D7664:0xEBFFF842,
0x020D7668:0xE8BD8038,0x020D766C:0x0224FCE4,
0x020D7670:0x020D738C,
0x020D5774:0xE92D4038,0x020D5778:0xE1A04000,
0x020D577C:0xE1A05001,0x020D5784:0xE59F102C,
0x020D578C:0xE7815104,0x020D57B8:0x0224E0D8,
0x020D738C:0xE92D40F8,0x020D7418:0xE59F11DC,
0x020D7564:0xE5933004,0x020D7568:0xE3530000,
0x020D757C:0xE12FFF33,0x020D75FC:0x02FFFFAA,
}
def u32(data,offset):
 if offset<0 or offset+4>len(data):raise ValueError('truncated input')
 return struct.unpack_from('<I',data,offset)[0]
def branch_target(opcode,address):
 if (opcode&0x0e000000)!=0x0a000000:raise ValueError('not ARM B/BL')
 disp=opcode&0xffffff
 if disp&0x800000:disp-=0x1000000
 return (address+8+disp*4)&0xffffffff
def pc_literal_target(opcode,address):
 if opcode&0x0f7f0000!=0x051f0000:raise ValueError('not ARM PC-relative LDR')
 disp=opcode&0xfff
 return (address+8+(disp if opcode&(1<<23) else -disp))&0xffffffff
def irq_table_address(base,index):
 if type(base) is not int or type(index) is not int or not 0<=index<32:
  raise ValueError('invalid IRQ table address/index')
 return base+index*4
def inspect(rom,check_hash=True):
 digest=hashlib.sha256(rom).hexdigest()
 if check_hash and digest!=SHA:raise ValueError('unexpected original ROM SHA256')
 off,base,size=(u32(rom,p) for p in (0x20,0x28,0x2c))
 if base!=BASE or off+size>len(rom):raise ValueError('invalid ARM9 region')
 def at(address):
  delta=address-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('ARM9 address outside binary')
  return u32(rom,off+delta)
 for address,expected in SITES.items():
  if at(address)!=expected:raise ValueError(f'ARM9 instruction/literal mismatch at {address:#x}')
 for address,target in {0x020D7650:0x020D57C0,0x020D7658:0x020D7648,0x020D7664:0x020D5774}.items():
  if branch_target(at(address),address)!=target:raise ValueError(f'IRQ registration branch mismatch at {address:#x}')
 for address,target in {0x020D765C:0x020D7670,0x020D5784:0x020D57B8,0x020D7418:0x020D75FC}.items():
  if pc_literal_target(at(address),address)!=target:raise ValueError(f'IRQ registration literal mismatch at {address:#x}')
 if irq_table_address(at(0x020D57B8),6)!=0x0224E0F0:raise ValueError('unexpected IRQ slot address')
 return {'original_rom_sha256':digest,'verified_anchor_sites':len(SITES),
 'interrupt_index':6,'interrupt_name':'Timer 3 overflow (Nintendo DS IRQ bit 6)',
 'irq_table_base':'0x0224e0d8','irq_handler_slot':'0x0224e0f0',
 'registration_function':'0x020d5774','registration_call':'0x020d7664',
 'registered_handler':'0x020d738c','sample_shared_memory':'0x02ffffaa',
 'later_indirect_callback':'0x020d757c',
 'limitations':['Static registration does not prove actual interrupt firing.',
 'Runtime destination of the input-structure +4 callback is unknown.',
 'Pixel calibration and gameplay UI dispatcher are unverified.',
 'No gameplay patch or emulator run was performed.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path)
 p.add_argument('--out',type=Path,default=Path('irq_registration.json'))
 a=p.parse_args();result=inspect(a.rom.read_bytes())
 a.out.write_text(json.dumps(result,indent=2)+'\n')
 print('Verified IRQ6 static registration ->',result['registered_handler'])
