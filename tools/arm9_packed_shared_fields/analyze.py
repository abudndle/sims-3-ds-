"""Trace 12-bit packed fields transferred from ARM7 to ARM9 in Sims 3 DS.

Static trace of filtered touchscreen ADC samples. Pixel calibration and runtime use are open.
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
ARM7_PRODUCER = {
    # Handler passes the stack result to the producer and publishes both halves.
    0x0238d9c8: 0xe28d5008, 0x0238d9d4: 0xe1a00005, 0x0238d9d8: 0xeb00012c,
    0x0238d9e0: 0xe1a00005, 0x0238d9e4: 0xebffff9c, 0x0238d9e8: 0xe1dd00b8,
    0x0238d9f4: 0xe1dd00ba,
    # Sampler selects X/Y, configures SPI and writes the ADC command.
    0x0238dcb8: 0xe59f31bc,
    0x0238dccc: 0xe1a07000,
    0x0238dd3c: 0xe1a0c809,
    0x0238dd44: 0xe7889103,
    0x0238dd5c: 0xe7989103,
    0x0238dd64: 0xe1a0c80c,
    0x0238dcbc: 0xe3520000, 0x0238dcc0: 0x03a090d1, 0x0238dcd8: 0x13a09091,
    0x0238dce0: 0xe1d300b0, 0x0238dcec: 0xe59f118c, 0x0238dcf0: 0xe59f018c,
    0x0238dcf4: 0xe1c310b0, 0x0238dcf8: 0xe20990ff, 0x0238dcfc: 0xe1c090b0,
    0x0238dd10: 0xe59f1164, 0x0238de7c: 0x040001c0, 0x0238de80: 0x00008a01,
    0x0238de84: 0x040001c2,
    # Receive two bytes, extract the 12-bit conversion and filter five samples.
    0x0238dd18: 0xe59fe168, 0x0238dd34: 0xe1d190b2, 0x0238dd38: 0xe20990ff,
    0x0238dd40: 0xe1a0942c, 0x0238dd58: 0xe1d1c0b2, 0x0238dd60: 0xe20cc0ff,
    0x0238dd68: 0xe189982c, 0x0238dd6c: 0xe009c00e, 0x0238dd70: 0xe1a0c1cc,
    0x0238dd74: 0xe788c103, 0x0238dd7c: 0xe3530005, 0x0238dd80: 0xbaffffe7,
    0x0238de20: 0xd3c00007, 0x0238de24: 0xd1c700b0, 0x0238de68: 0xe3c11007,
    0x0238de6c: 0xe1c710b0, 0x0238de88: 0x00007ff8,
    # Producer selects each axis and packs the returned halfword.
    0x0238de9c: 0xe3a06000,
    0x0238deb0: 0xebffff3b,
    0x0238de98: 0xe1a08002, 0x0238dea4: 0xe1a0a000, 0x0238deb8: 0x1a00000b,
    0x0238dee0: 0xe58a0000, 0x0238deec: 0xe28d5004, 0x0238def4: 0xe1a00005,
    0x0238defc: 0xe1a02006, 0x0238df00: 0xebffff69, 0x0238df18: 0xe2460a01,
    0x0238df1c: 0xe0013000, 0x0238df20: 0xe1dd20b4, 0x0238df24: 0xe59f1124,
    0x0238df2c: 0xe0021001, 0x0238df30: 0xe1835001, 0x0238df34: 0xe58a5000,
    0x0238df40: 0xe3a02001, 0x0238df44: 0xebffff58, 0x0238df70: 0xe1dd10b4,
    0x0238df74: 0xe59a2000, 0x0238df78: 0xe59f00cc, 0x0238df7c: 0xe1a01a01,
    0x0238df80: 0xe0020000, 0x0238df84: 0xe1802421, 0x0238df90: 0xe58a2000,
    0x0238e04c: 0xff000fff, 0x0238e050: 0x00000fff,
}

def verify_sites(reader, anchors, cpu):
    for address, opcode in anchors.items():
        if reader(address) != opcode:
            raise ValueError(f"{cpu} instruction mismatch at {address:#x}")

def inspect_arm7(reader):
    verify_sites(reader, ARM7, "ARM7")
    verify_sites(reader, ARM7_PRODUCER, "ARM7")
    return {
        "producer": "0x0238de90",
        "sampler": "0x0238dcac",
        "command_write": "0x0238dcfc",
        "spi_control": "0x040001c0",
        "spi_data": "0x040001c2",
        "adc_bits": 12,
        "reference": "differential",
        "axes": {
            "x": {"command": "0xd1", "call": "0x0238df00", "bits": [0, 11]},
            "y": {"command": "0x91", "call": "0x0238df44", "bits": [12, 23]},
        },
        "scope": "Filtered ADC samples on the sampling path",
        "verified_sites": len(ARM7) + len(ARM7_PRODUCER),
    }

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
 verify_sites(a9, ARM9, "ARM9")
 producer = inspect_arm7(a7)
 for addr in (0x020D7418,0x020D74EC):
  if literal_target(a9(addr),addr)!=0x020D75FC:raise ValueError("ARM9 pointer mismatch")
 if literal_target(a7(0x0238D9EC),0x0238D9EC)!=0x0238DB2C:raise ValueError("ARM7 pointer mismatch")
 return {"sha256":sha,"shared_base":"0x02ffffaa","arm7_writes":["0x0238d9f0","0x0238d9f8"],
 "arm9_readers":["0x020d7418","0x020d74ec"],"verified_sites":len(ARM9)+producer["verified_sites"],
 "arm7_producer":producer,
 "result":"ARM7 packs filtered touchscreen X/Y ADC samples for ARM9.",
 "unknown":["Runtime touchscreen X/Y correlation and full upper-byte semantics","Runtime call path",
            "Screen coordinate calibration","ARM9 gameplay UI dispatcher"]}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("rom",type=Path)
 p.add_argument("--output",type=Path,default=Path("packed_fields.json"))
 a=p.parse_args();result=inspect(a.rom.read_bytes())
 a.output.write_text(json.dumps(result,indent=2)+"\n");print(result["result"])
