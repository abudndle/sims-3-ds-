"""Trace 12-bit packed fields transferred from ARM7 to ARM9 in Sims 3 DS.

Static proof only: coordinate semantics, calibration and runtime path are unconfirmed.
"""
import argparse,hashlib,json,struct
from pathlib import Path
SHA="d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
ARM9={
 0x020D7418:0xE59F11DC,0x020D7420:0xE1D120B0,
 0x020D7424:0xE1D110B2,0x020D742C:0xE1CD20B4,
 0x020D7430:0xE1CD10B6,0x020D7434:0xE59D5004,
 0x020D7450:0xE1A05A2C,0x020D7454:0xE18750B6,
 0x020D7460:0xE1A04A24,0x020D7464:0xE1C540B2,
 0x020D746C:0xE1C520B4,0x020D7474:0xE1C510B6,
 0x020D74EC:0xE59F1108,0x020D74F0:0xE1D140B0,
 0x020D74F4:0xE1D110B2,0x020D7500:0xE59D4000,
 0x020D7504:0xE1A01A04,0x020D7508:0xE1A05A21,
 0x020D7510:0xE1A01384,0x020D7514:0xE1A0CFA1,
 0x020D7518:0xE1A01284,0x020D75FC:0x02FFFFAA}
ARM7={0x0238D9EC:0xE59F1138,0x0238D9F0:0xE1C100B0,
      0x0238D9F8:0xE1C100B2,0x0238DB2C:0x02FFFFAA}
def fields(value):
 if not isinstance(value,int) or not 0<=value<=0xffffffff:raise ValueError("unsigned 32-bit value required")
 return {"field0":value&4095,"field1":(value>>12)&4095,"upper8":(value>>24)&255}
def literal_target(word,addr):
 if (word&0x0f7f0000)!=0x051f0000:raise ValueError("not PC-relative LDR")
 imm=word&4095
 return (addr+8+(imm if word&(1<<23) else -imm))&0xffffffff
def inspect(rom,strict=True):
 sha=hashlib.sha256(rom).hexdigest()
 if strict and sha!=SHA:raise ValueError("ROM SHA-256 mismatch")
 def cpu(header,expected_base):
  if len(rom)<header+16:raise ValueError("truncated ROM header")
  off,base,size=[struct.unpack_from("<I",rom,header+n)[0] for n in (0,8,12)]
  if base!=expected_base or off+size>len(rom):raise ValueError("CPU bounds mismatch")
  def at(addr):
   delta=addr-base
   if delta<0 or delta+4>size or delta%4:raise ValueError("out of CPU bounds")
   return struct.unpack_from("<I",rom,off+delta)[0]
  return at
 a9=cpu(0x20,0x02004000);a7=cpu(0x30,0x02380000)
 for name,reader,anchors in (("ARM9",a9,ARM9),("ARM7",a7,ARM7)):
  for address,opcode in anchors.items():
   if reader(address)!=opcode:raise ValueError(f"{name} instruction mismatch at {address:#x}")
 for addr in (0x020D7418,0x020D74EC):
  if literal_target(a9(addr),addr)!=0x020D75FC:raise ValueError("ARM9 pointer mismatch")
 if literal_target(a7(0x0238D9EC),0x0238D9EC)!=0x0238DB2C:raise ValueError("ARM7 pointer mismatch")
 return {"sha256":sha,"shared_base":"0x02ffffaa","arm7_writes":["0x0238d9f0","0x0238d9f8"],
 "arm9_readers":["0x020d7418","0x020d74ec"],"verified_sites":len(ARM9)+len(ARM7),
 "result":"ARM9 combines shared halfwords and splits two 12-bit fields plus flags.",
 "unknown":["Field meaning and touchscreen X/Y correlation","Runtime call path",
            "Screen coordinate calibration","ARM9 gameplay UI dispatcher"]}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("rom",type=Path)
 p.add_argument("--output",type=Path,default=Path("packed_fields.json"))
 a=p.parse_args();result=inspect(a.rom.read_bytes())
 a.output.write_text(json.dumps(result,indent=2)+"\n");print(result["result"])
