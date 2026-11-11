#!/usr/bin/env python3
"""Classify an apparent 0x90 touch-command lead in Sims 3 DS ARM7.
No game assets or executable code are emitted.
"""
import argparse, hashlib, json, struct
from pathlib import Path
BASE=0x02380000
ROM_MD5='7cdf32d02eeeff592a0a4ab6bec7b5c1'

def word(data, addr):
    pos=addr-BASE
    if pos<0 or pos+4>len(data): raise ValueError('ARM7 address out of range')
    return struct.unpack_from('<I',data,pos)[0]

def bl_target(addr, instr):
    if (instr & 0x0f000000)!=0x0b000000: raise ValueError('not ARM BL')
    signed=instr&0xffffff
    if signed&(1<<23): signed-=1<<24
    return addr+8+signed*4

def literal_target(data, addr):
    ins=word(data,addr)
    if (ins & 0x0f7f0000)!=0x051f0000: raise ValueError('not ARM PC-relative LDR literal')
    imm=ins&0xfff
    place=addr+8+(imm if (ins & (1<<23)) else -imm)
    return place,word(data,place)

def run(rom):
    raw=Path(rom).read_bytes()
    if hashlib.md5(raw).hexdigest()!=ROM_MD5: raise ValueError('wrong ROM variant / checksum')
    off,entry,load,size=struct.unpack_from('<4I',raw,0x30)
    if load!=BASE or size<=0 or off+size>len(raw): raise ValueError('invalid ARM7 header')
    data=raw[off:off+size]
    # Constant MOV r5,#0xB8 and MOVNE r5,#0x90 at a candidate command site.
    assert word(data,0x0238FA50)==0xE3A050B8
    assert word(data,0x0238FA5C)==0x13A05090
    assert bl_target(0x0238FA6C,word(data,0x0238FA6C))==0x0238F978
    a,b=literal_target(data,0x0238F97C)
    c,d=literal_target(data,0x0238F998)
    assert (b,d)==(0x040001A4,0x040001A0), (hex(b),hex(d))
    return {
      'source_md5':hashlib.md5(raw).hexdigest(),
      'source_sha256':hashlib.sha256(raw).hexdigest(),
      'arm7_load':hex(load),'arm7_size':hex(size),
      'candidate_command_addr':'0x0238FA5C',
      'candidate_command':'0x90 (conditional); 0xB8 (default)',
      'transfer_call':'0x0238FA6C',
      'transfer_target':'0x0238F978',
      'control_literal_instruction':'0x0238F97C',
      'control_literal_slot':hex(a), 'control_bus_register':hex(b),
      'data_literal_instruction':'0x0238F998',
      'data_literal_slot':hex(c), 'data_bus_register':hex(d),
      'classification':'game-card bus, NOT touchscreen SPI',
      'touch_spi_registers':['0x040001C0','0x040001C2'],
      'confirmed_touch_x_y':'no',
      'rom_modified':False,
    }

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('rom');parser.add_argument('--output',default='results.json')
    args=parser.parse_args();res=run(args.rom);Path(args.output).write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
