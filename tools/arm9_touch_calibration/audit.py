"""ROM-guarded static audit of ARM9 touchscreen coordinate calibration."""
import argparse, hashlib, json, struct
from pathlib import Path
SHA256='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02004000
ANCHORS={
0x020D7B3C:0xE92D4070,0x020D7B40:0xE59F2108,0x020D7B44:0xE1D223B4,
0x020D7B48:0xE3520000,0x020D7B4C:0x1A000008,0x020D7B50:0xE1D140B0,
0x020D7B54:0xE1D130B2,0x020D7B58:0xE1D120B4,0x020D7B5C:0xE1D110B6,
0x020D7B60:0xE1C030B2,0x020D7B64:0xE1C020B4,0x020D7B68:0xE1C010B6,
0x020D7B6C:0xE1C040B0,0x020D7B70:0xE8BD8070,0x020D7B74:0xE1D140B4,
0x020D7B78:0xE1D130B6,0x020D7B7C:0xE59F20D0,0x020D7B9C:0xE1D140B0,
0x020D7BA0:0xE5923000,0x020D7BA4:0xE592E008,0x020D7BC8:0xE1A03B26,
0x020D7BCC:0xE1833505,0x020D7BD0:0xE1C030B0,0x020D7BD4:0xE1D030F0,
0x020D7BD8:0xE3530000,0x020D7BDC:0xB3A03000,0x020D7BE0:0xB1C030B0,
0x020D7BE8:0xE35300FF,0x020D7BEC:0xC3A030FF,0x020D7BF0:0xC1C030B0,
0x020D7BF4:0xE1D130B2,0x020D7BF8:0xE592100C,0x020D7BFC:0xE592C014,
0x020D7C28:0xE1C010B2,0x020D7C2C:0xE1D010F2,0x020D7C30:0xE3510000,
0x020D7C34:0xB3A01000,0x020D7C38:0xB1C010B2,0x020D7C40:0xE35100BF,
0x020D7C44:0xC3A010BF,0x020D7C48:0xC1C010B2,0x020D7C4C:0xE8BD8070,
0x020D7C50:0x0224FCE4,0x020D7C54:0x0224FD00}
def u32(blob,pos):
 if pos<0 or pos+4>len(blob):raise ValueError('out of bounds word')
 return struct.unpack_from('<I',blob,pos)[0]
def literal_address(opcode,address):
 if opcode&0x0f7f0000!=0x051f0000:raise ValueError('not ARM literal load')
 d=opcode&0xfff
 return (address+8+(d if opcode&(1<<23) else -d))&0xffffffff
def branch_target(opcode,address):
 if opcode&0x0e000000!=0x0a000000:raise ValueError('not ARM branch')
 d=opcode&0xffffff
 if d&0x800000:d-=0x1000000
 return (address+8+d*4)&0xffffffff
def clamp_screen(x,y):
 if type(x) is not int or type(y) is not int:raise ValueError('integer coordinates required')
 return max(0,min(255,x)),max(0,min(191,y))
def inspect(rom,require_hash=True):
 digest=hashlib.sha256(rom).hexdigest()
 if require_hash and digest!=SHA256:raise ValueError('original ROM SHA256 mismatch')
 off,base,size=(u32(rom,p) for p in (0x20,0x28,0x2c))
 if base!=BASE or not size or off+size>len(rom):raise ValueError('invalid ARM9 region')
 def at(addr):
  delta=addr-base
  if delta<0 or delta%4 or delta+4>size:raise ValueError('outside ARM9')
  return u32(rom,off+delta)
 for addr,opcode in ANCHORS.items():
  if at(addr)!=opcode:raise ValueError(f'ARM9 anchor mismatch at {addr:#x}')
 for source,target in ((0x020D7B40,0x020D7C50),(0x020D7B7C,0x020D7C54)):
  if literal_address(at(source),source)!=target:raise ValueError('calibration pointer mismatch')
 if branch_target(at(0x020D7B4C),0x020D7B4C)!=0x020D7B74:raise ValueError('bypass branch mismatch')
 return {'rom_sha256':digest,'verified_anchor_sites':len(ANCHORS),
 'routine':'0x020d7b3c','input_state_literal':'0x0224fce4',
 'calibration_literal':'0x0224fd00','output_offsets':[0,2],
 'output_limits':{'x':[0,255],'y':[0,191]},
 'observations':['Nonzero state flag enters calibrated arithmetic path',
 'Zero state flag enters four-halfword copy/reorder path',
 'Calibrated X and Y are clamped before return'],
 'limitations':['Static code path only; runtime execution not confirmed',
 'Calibration parameters and orientation not fully established',
 'No gameplay callback registration or playable patched ROM']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path)
 p.add_argument('--out',type=Path,default=Path('touch_calibration.json'))
 a=p.parse_args();r=inspect(a.rom.read_bytes())
 a.out.write_text(json.dumps(r,indent=2)+'\n')
 print('Verified ARM9 coordinate calibration boundary')
