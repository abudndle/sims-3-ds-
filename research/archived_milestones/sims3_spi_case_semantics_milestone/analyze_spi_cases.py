#!/usr/bin/env python3
"""Read-only ARM7 SPI dispatch case 4-9 analyzer for Sims3 DS VS3E.
Proof is based on exact ARM instruction words, without treating SPI use as proof of touch XY.
"""
import argparse,csv,hashlib,json,struct
from pathlib import Path
SWITCH=0x0238CB20
TABLE=0x0238CB4C
BASE_PC=0x0238CB50
SPI_WRITE=0x0238C9D8
SPI_READ=0x0238CA54
OR_WRAPPER=0x0238CAC8
AND_NOT_WRAPPER=0x0238CAF0
CASES={4:(0x0238CBB4,4,OR_WRAPPER),5:(0x0238CBC0,4,AND_NOT_WRAPPER),6:(0x0238CBCC,8,OR_WRAPPER),7:(0x0238CBD4,8,AND_NOT_WRAPPER),8:(0x0238CBDC,12,OR_WRAPPER),9:(0x0238CBE4,12,AND_NOT_WRAPPER)}
def layout(rom):
    if len(rom)<0x200:raise ValueError('header truncated')
    off,entry,base,size=struct.unpack_from('<IIII',rom,0x30)
    if off<0x200 or size<0x100 or off+size>len(rom) or not(base<=entry<base+size):raise ValueError('bad ARM7 bounds')
    return off,base,size

def branch(word,address):
    if word & 0x0e000000 != 0x0a000000: return None
    delta=word & 0xffffff
    if delta & 0x800000: delta-=0x1000000
    return (address+8+4*delta)&0xffffffff

def analyze_bytes(rom):
    off,base,size=layout(rom)
    def read32(a):
        q=a-base
        if q<0 or q+4>size:raise ValueError('ARM7 read outside range')
        return struct.unpack_from('<I',rom,off+q)[0]
    def read16(a):
        q=a-base
        if q<0 or q+2>size:raise ValueError('ARM7 read outside range')
        return struct.unpack_from('<H',rom,off+q)[0]
    if read32(SWITCH+0x0c)!=0xE3500019:raise ValueError('unexpected dispatcher')
    rows=[]
    for k,(entry,mask,callee) in CASES.items():
        if BASE_PC+read16(TABLE+2*k)!=entry:raise ValueError(f'bad case {k} target')
        first=read32(entry)
        expected=0xE3A00000|mask
        if first!=expected:raise ValueError(f'case {k} expected MOV r0,#mask')
        next_addr=entry+4
        next_op=read32(next_addr)
        reached=branch(next_op,next_addr)
        chain=[]
        if (next_op & 0x0F000000)==0x0B000000:
            if reached!=callee: raise ValueError(f'case {k}: BL does not reach expected wrapper')
            chain=[entry,next_addr,callee]
        elif (next_op & 0x0F000000)==0x0A000000:
            # branch into the shared BL instruction for cases 4,5
            expected_addr=0x0238CBB8 if k%2==0 else 0x0238CBC4
            if reached!=expected_addr or branch(read32(reached),reached)!=callee:
                raise ValueError(f'case {k}: shared branch does not reach wrapper')
            chain=[entry,next_addr,reached,callee]
        else:raise ValueError(f'case {k}: not a BL/B branch')
        rows.append({'case':k,'operation':'set bits (OR)' if k%2==0 else 'clear bits (AND NOT)',
          'mask':f'0x{mask:02X}','entry':f'0x{entry:08X}',
          'wrapper':f'0x{callee:08X}','call_path':' -> '.join(f'0x{x:08X}' for x in chain)})
    # Inspect wrappers exact critical instructions to ensure semantics
    if read32(OR_WRAPPER+0x0c)!=0xE1A00004 or read32(OR_WRAPPER+0x14)!=0xE1801005:
        raise ValueError('OR wrapper changed')
    if read32(AND_NOT_WRAPPER+0x14)!=0xE1E01005 or read32(AND_NOT_WRAPPER+0x1C)!=0xE0001001:
        raise ValueError('AND-NOT wrapper changed')
    # SPI helpers both use same 0x8202 base config, but are not necessarily touch-XY sampling
    if read32(SPI_WRITE+0x50)!=0x00008202 or read32(SPI_READ+0x6c)!=0x00008202:
        raise ValueError('SPI configuration literal differs')
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'arm7_load':f'0x{base:08X}',
      'dispatch':f'0x{SWITCH:08X}','decoded_cases':rows,
      'notes':['Cases 4-9 read a peripheral byte and set/clear bit masks via SPI wrappers.',
               'The wrappers call SPI transfer helpers; no X/Y ADC conversion was demonstrated.',
               'The SPI helpers configure multiple control values; device selection and command semantics require further validation.',
               'No ARM9 UI dispatcher or modified ROM is identified or produced.']}
def analyze(path):return analyze_bytes(Path(path).read_bytes())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',default='.');a=ap.parse_args()
    r=analyze(a.rom);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/'spi_case_report.json').write_text(json.dumps(r,indent=2)+'\n')
    with (out/'spi_case_map.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(r['decoded_cases'][0]));w.writeheader();w.writerows(r['decoded_cases'])
    print('Verified',len(r['decoded_cases']),'set/clear-bit cases')
if __name__=='__main__':main()
