"""Read-only ARM7 0xD0 candidate trace; original VS3E ROM only."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA="d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
BASE=0x02380000
ANCHORS={
0x02399850:0xE59010D8,0x02399854:0xE351007F,0x02399858:0x9A000006,
0x0239985C:0xE59F005C,0x02399860:0xE3A010D0,0x02399864:0xE3A0C002,
0x02399868:0xE59F3054,0x0239986C:0xE2812037,0x02399870:0xE58DC000,
0x02399874:0xEA000007,0x02399878:0xE3A02001,0x02399880:0xE3A01004,
0x02399894:0xE2622F42,0x02399898:0xEB205B91,0x0239989C:0xE8BD4038,
0x023998A0:0xE12FFF1E,0x023998C0:0x038096CC,0x023998C4:0x02FE7D5C}
def read32(data,o):
 if o<0 or o+4>len(data):raise ValueError("out-of-range word")
 return struct.unpack_from("<I",data,o)[0]
def branch_target(i,a):
 if i&0x0e000000!=0x0a000000:raise ValueError("not B/BL")
 v=i&0xffffff
 if v&0x800000:v-=0x1000000
 return (a+8+v*4)&0xffffffff
def literal_target(i,a):
 if i&0x0f7f0000!=0x051f0000:raise ValueError("not literal LDR")
 v=i&0xfff
 return (a+8+(v if i&(1<<23) else -v))&0xffffffff
def inspect(rom,verify_hash=True):
 digest=hashlib.sha256(rom).hexdigest()
 if verify_hash and digest!=SHA:raise ValueError("original ROM SHA mismatch")
 off,base,size=[read32(rom,x) for x in (0x30,0x38,0x3c)]
 if base!=BASE or off+size>len(rom):raise ValueError("ARM7 bounds mismatch")
 def word(a):
  d=a-base
  if d<0 or d%4 or d+4>size:raise ValueError("ARM7 bounds")
  return read32(rom,off+d)
 for a,expected in ANCHORS.items():
  if word(a)!=expected:raise ValueError(f"opcode/literal mismatch at {a:#x}")
 for a,dest in [(0x02399858,0x02399878),(0x02399874,0x02399898),(0x02399898,0x02BB06E4)]:
  if branch_target(word(a),a)!=dest:raise ValueError("branch mismatch")
 for a,dest in [(0x0239985C,0x023998C0),(0x02399868,0x023998C4)]:
  if literal_target(word(a),a)!=dest:raise ValueError("literal pointer mismatch")
 arg1=word(0x02399860)&255
 arg2=arg1+(word(0x0239986C)&255)
 if (arg1,arg2)!=(0xD0,0x107):raise ValueError("argument derivation mismatch")
 return {"rom_sha256":digest,"verified_sites":len(ANCHORS),
         "candidate":"0x02399860","r1":"0xD0","r2":"0x107",
         "branch":"0x02399898 -> 0x02BB06E4",
         "observation":"0xD0 is a call argument, not a direct SPIDATA write at this instruction",
         "uncertainty":"Call target lies outside loaded ARM7 image; runtime semantics and touchscreen X/Y sampling not established"}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("rom",type=Path);p.add_argument("--out",type=Path,default=Path("d0_path.json"))
 a=p.parse_args();r=inspect(a.rom.read_bytes());a.out.write_text(json.dumps(r,indent=2)+"\n");print(r["observation"])
