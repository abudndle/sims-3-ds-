"""Read-only ARM7 shared-field producer trace for Sims 3 DS VS3E."""
import hashlib, struct, argparse, json
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
INSTRUCTIONS={
 0x0238E440:0xE5960008,0x0238E444:0xE2000001,0x0238E448:0xE3500001,
 0x0238E44C:0x1A000004,0x0238E450:0xEB000116,
 0x0238E454:0xE5961008,0x0238E458:0xE3110002,0x0238E45C:0x12200902,
 0x0238E460:0xEA000003,0x0238E464:0xEB0000C1,
 0x0238E468:0xE5961008,0x0238E46C:0xE3110002,0x0238E470:0x12200080,
 0x0238E474:0xE59F1138,0x0238E478:0xE1C100B0,0x0238E5B4:0x02FFFF94,
 0x0238E8D4:0xE3A010E4,0x0238E794:0xE3A010EC,
 0x0238E8BC:0xE1D200B0,0x0238E77C:0xE1D200B0,
 0x0238E9BC:0x040001C0,0x0238E86C:0x040001C0,
 0x0238E9C4:0x040001C2,0x0238E874:0x040001C2,
}
def branch_target(word,addr):
 if (word & 0x0e000000)!=0x0a000000:raise ValueError('not ARM B/BL')
 imm=word&0xffffff
 if imm & 0x800000:imm-=0x1000000
 return (addr+8+imm*4)&0xffffffff

def inspect(data,verify_hash=True):
 sha=hashlib.sha256(data).hexdigest()
 if verify_hash and sha!=SHA:raise ValueError('wrong VS3E SHA256')
 off,base,size=(struct.unpack_from('<I',data,0x30)[0],
                struct.unpack_from('<I',data,0x38)[0],
                struct.unpack_from('<I',data,0x3c)[0])
 if base!=BASE or off+size>len(data):raise ValueError('invalid ARM7 bounds')
 def word(addr):
  delta=addr-base
  if delta<0 or delta+4>size or delta%4:raise ValueError('out of ARM7 bounds')
  return struct.unpack_from('<I',data,off+delta)[0]
 for addr,opcode in INSTRUCTIONS.items():
  if word(addr)!=opcode:raise ValueError('instruction mismatch at '+hex(addr))
 for addr,target in [(0x0238E450,0x0238E8B0),(0x0238E464,0x0238E770),(0x0238E44C,0x0238E464)]:
  if branch_target(word(addr),addr)!=target:raise ValueError('branch mismatch')
 return {'rom_sha256':sha,'verified_instruction_sites':len(INSTRUCTIONS),
  'shared_field':'0x02FFFF94',
  'selection':'record +8 bit0 chooses 0x0238E8B0 or 0x0238E770',
  'helper_command_bytes':['0xE4','0xEC'],
  'flag':'record +8 bit1 XORs helper return with 0x8000 on first branch or 0x80 on second',
  'output':'low 16 bits of r0 stored to 0x02FFFF94',
  'hardware':'helpers reference SPICNT 0x040001C0 and SPIDATA 0x040001C2',
  'limitations':['Not confirmed touchscreen X/Y coordinates',
                 'Static instruction evidence; runtime dispatch not confirmed',
                 'No playable ROM patch created']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--out',default='sample_provenance.json');args=p.parse_args()
 result=inspect(Path(args.rom).read_bytes())
 Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
