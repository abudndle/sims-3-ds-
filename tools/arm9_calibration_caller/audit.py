"""Verify VS3E ARM9 calibration caller, shared-state handling and wrapper."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA="d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
BASE=0x02004000
ANCHORS={
0x020D78E8:0xE92D4008,0x020D78EC:0xE59F203C,0x020D78F0:0xE1D213B8,
0x020D78F4:0xE3110001,0x020D78F8:0x13A00001,0x020D78FC:0x18BD8008,
0x020D7900:0xE1D2C0B8,0x020D7904:0xE1D230BA,0x020D7908:0xE1A01000,
0x020D790C:0xE1C0C0B0,0x020D7910:0xE1C030B2,0x020D7914:0xE1D230BC,
0x020D7918:0xE1D220BE,0x020D791C:0xE1C030B4,0x020D7920:0xE1C020B6,
0x020D7924:0xEB000084,0x020D7928:0xE3A00000,0x020D792C:0xE8BD8008,
0x020D7930:0x0224FCE4,0x020D7934:0xE92D4010,0x020D7938:0xE1A04000,
0x020D793C:0xE3A00001,0x020D7940:0xEB0000C4,0x020D7944:0xE1A00004,
0x020D7948:0xEBFFFFE6,0x020D794C:0xE8BD8010}
def u32(blob,pos):
 if pos<0 or pos+4>len(blob):raise ValueError("word outside bytes")
 return struct.unpack_from("<I",blob,pos)[0]
def branch_target(op,addr):
 if op&0x0e000000!=0x0a000000:raise ValueError("not ARM B/BL")
 d=op&0xffffff
 if d&0x800000:d-=0x1000000
 return (addr+8+d*4)&0xffffffff
def literal_target(op,addr):
 if op&0x0f7f0000!=0x051f0000:raise ValueError("not literal LDR")
 d=op&4095
 return (addr+8+(d if op&0x800000 else -d))&0xffffffff
def inspect(rom,check_hash=True):
 digest=hashlib.sha256(rom).hexdigest()
 if check_hash and digest!=SHA:raise ValueError("original ROM SHA256 mismatch")
 off,base,size=(u32(rom,p) for p in (0x20,0x28,0x2c))
 if base!=BASE or size<=0 or off+size>len(rom):raise ValueError("ARM9 bounds mismatch")
 def at(addr):
  d=addr-base
  if d<0 or d%4 or d+4>size:raise ValueError("outside ARM9")
  return u32(rom,off+d)
 for addr,opcode in ANCHORS.items():
  if at(addr)!=opcode:raise ValueError(f"instruction mismatch at {addr:#x}")
 if literal_target(at(0x020d78ec),0x020d78ec)!=0x020d7930:raise ValueError("state literal mismatch")
 for source,dest in [(0x020d7924,0x020d7b3c),(0x020d7940,0x020d7c58),(0x020d7948,0x020d78e8)]:
  if branch_target(at(source),source)!=dest:raise ValueError("branch mismatch")
 return {"sha256":digest,"verified_sites":len(ANCHORS),"state_pointer":"0x0224fce4",
 "state_flag_read":"0x020d78f0","state_flag_test":"0x020d78f4",
 "copy_four_halfwords":"0x020d7900..0x020d7920",
 "calibration_call":"0x020d7924 -> 0x020d7b3c",
 "wrapper_calls":["0x020d7940 -> 0x020d7c58","0x020d7948 -> 0x020d78e8"],
 "unknown":["runtime calibration use","callback setter","gameplay UI dispatcher","playable ROM conversion"]}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("rom",type=Path)
 ap.add_argument("--out",type=Path,default=Path("calibration_caller.json"))
 args=ap.parse_args();result=inspect(args.rom.read_bytes())
 args.out.write_text(json.dumps(result,indent=2)+"\n")
 print("Verified calibration caller")
