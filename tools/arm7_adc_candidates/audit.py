#!/usr/bin/env python3
"""Read-only audit of possible TSC commands encoded as ARM7 immediate moves."""
import argparse, hashlib, json, struct
from pathlib import Path

ROM_SHA="d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
COMMANDS={0x90:"Y 12-bit differential",0x94:"Y 12-bit single-ended",0x98:"Y 8-bit differential",0x9c:"Y 8-bit single-ended",0xd0:"X 12-bit differential",0xd4:"X 12-bit single-ended",0xd8:"X 8-bit differential",0xdc:"X 8-bit single-ended",0xe4:"AUX 12-bit",0xec:"AUX 8-bit"}

def rotate(value,bits):
    return ((value>>bits)|(value<<(32-bits)))&0xffffffff if bits else value

def arm_immediate(word):
    if (word&0x0ff00000) not in (0x03a00000,0x03e00000):
        return None
    value=rotate(word&0xff,((word>>8)&15)*2)
    return (~value&0xffffffff) if word&0x00400000 else value

def inspect(rom,verify_hash=True):
    digest=hashlib.sha256(rom).hexdigest()
    if verify_hash and digest!=ROM_SHA:
        raise ValueError("original VS3E ROM SHA256 mismatch")
    if len(rom)<0x40:raise ValueError("ROM header missing")
    off=struct.unpack_from("<I",rom,0x30)[0]
    base=struct.unpack_from("<I",rom,0x38)[0]
    size=struct.unpack_from("<I",rom,0x3c)[0]
    if base!=0x02380000 or off+size>len(rom):
        raise ValueError("invalid ARM7 bounds")
    data=rom[off:off+size]
    hits=[]
    for pos in range(0,len(data)-3,4):
        word=struct.unpack_from("<I",data,pos)[0]
        value=arm_immediate(word)
        if value in COMMANDS:
            hits.append(dict(address=f"0x{base+pos:08X}",opcode=f"0x{word:08X}",value=f"0x{value:02X}",interpretation=COMMANDS[value],kind="ARM_MOV_IMMEDIATE"))
    for pos in range(0,len(data)-1,2):
        word=struct.unpack_from("<H",data,pos)[0]
        if word&0xf800==0x2000 and word&0xff in COMMANDS:
            value=word&0xff
            hits.append(dict(address=f"0x{base+pos:08X}",opcode=f"0x{word:04X}",value=f"0x{value:02X}",interpretation=COMMANDS[value],kind="THUMB_MOV_CANDIDATE"))
    hits.sort(key=lambda h:int(h["address"],16))
    return dict(rom_sha256=digest,arm7_size=size,hits=hits,
        warnings=["A matching immediate is not evidence of a touchscreen SPI transaction.",
                  "Thumb mode is not confirmed at candidate addresses.",
                  "Commands built with ORR, literals, memory or registers may be missed.",
                  "A command value can also be unrelated hardware data."])

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("rom",type=Path)
    p.add_argument("--output",type=Path,default=Path("adc_candidates.json"))
    a=p.parse_args();report=inspect(a.rom.read_bytes())
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(f"Found {len(report['hits'])} immediate-value candidates; no touchscreen path claimed.")
