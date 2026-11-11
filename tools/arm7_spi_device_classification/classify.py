#!/usr/bin/env python3
"""Verify ARM7 0x02393A98 D8 is firmware SPI, not touch ADC X."""
import argparse,hashlib,json,struct
from pathlib import Path
SHA='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
BASE=0x02380000
OPCODES={
 0x02393A8C:0xE59F1044, 0x02393A90:0xE3A02C89,
 0x02393A94:0xE1C320B0, 0x02393A98:0xE3A020D8,
 0x02393A9C:0xE1C120B0, 0x02393AD4:0x040001C0,
 0x02393AD8:0x040001C2,
}
def read32(rom,offset):
 if offset<0 or offset+4>len(rom):raise ValueError('truncated')
 return struct.unpack_from('<I',rom,offset)[0]
def decode_arm_literal(word,pc):
 if (word&0x0f7f0000)!=0x051f0000:raise ValueError('not PC-relative LDR')
 v=word&0xfff
 return (pc+8+(v if word&(1<<23) else -v))&0xffffffff
def decode_mov_imm(word):
 if (word&0x0fe00000)!=0x03a00000:raise ValueError('not ARM MOV immediate')
 rot=((word>>8)&0xf)*2;v=word&0xff
 return ((v>>rot)|(v<<(32-rot)))&0xffffffff if rot else v
def spi_device(spicnt):return (spicnt>>8)&3
def inspect(rom,strict=True):
 digest=hashlib.sha256(rom).hexdigest()
 if strict and digest!=SHA:raise ValueError('ROM hash mismatch')
 off,base,size=[read32(rom,x) for x in (0x30,0x38,0x3c)]
 if base!=BASE or off+size>len(rom):raise ValueError('ARM7 header invalid')
 def word(addr):
  delta=addr-base
  if delta<0 or delta+4>size or delta%4:raise ValueError('ARM7 bounds')
  return read32(rom,off+delta)
 for addr,val in OPCODES.items():
  if word(addr)!=val:raise ValueError(f'opcode/literal mismatch at {addr:#x}')
 if decode_arm_literal(word(0x02393A8C),0x02393A8C)!=0x02393AD8:
  raise ValueError('SPIDATA literal pointer mismatch')
 if word(0x02393AD8)!=0x040001C2 or word(0x02393AD4)!=0x040001C0:
  raise ValueError('SPI address mismatch')
 spicnt=decode_mov_imm(word(0x02393A90))
 command=decode_mov_imm(word(0x02393A98))
 if spi_device(spicnt)!=1:raise ValueError('expected firmware chip select')
 return {'rom_sha256':digest,'verified_sites':len(OPCODES),
 'spicnt_value':f'0x{spicnt:04X}','spi_device_select':spi_device(spicnt),
 'device':'firmware flash','spi_command_byte':f'0x{command:02X}',
 'spicnt_write':'0x02393A94','spidata_write':'0x02393A9C',
 'conclusion':'0xD8 at 0x02393A98 is sent on firmware SPI device 1, not touchscreen device 2',
 'remaining':['Other X/Y-like literal matches need bus-aware classification',
 'No touchscreen X/Y decoder or UI input path is proven']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path)
 p.add_argument('--output',type=Path,default=Path('device_classification.json'))
 args=p.parse_args();report=inspect(args.rom.read_bytes())
 args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(report['conclusion'])
