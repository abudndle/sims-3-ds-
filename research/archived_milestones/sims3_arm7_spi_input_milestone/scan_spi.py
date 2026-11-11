#!/usr/bin/env python3
"""Read-only ARM7 PC-relative literal analysis for DS SPI hardware, not a touch decoder."""
import argparse,csv,hashlib,json,struct
from pathlib import Path
SPI={0x040001C0:'SPICNT',0x040001C2:'SPIDATA'}
def extract_arm7(rom):
    offset,entry,base,size=struct.unpack_from('<IIII',rom,0x30)
    if offset < 0x200 or size==0 or offset+size>len(rom) or not base<=entry<base+size: raise ValueError('bad ARM7 image bounds')
    return base,memoryview(rom)[offset:offset+size]
def scan(base,data):
    matches=[]
    for i in range(0,len(data)-3,4):
        op=struct.unpack_from('<I',data,i)[0]
        # ARM single data transfer: immediate offset, P=1, L=1, Rn=PC, word load (B=0), W=0
        if ((op>>26)&3)!=1 or (op>>25)&1 or not ((op>>24)&1) or not ((op>>20)&1) or ((op>>16)&15)!=15 or (op>>22)&1 or (op>>21)&1:continue
        pool=base+i+8+(op&0xfff)*(1 if op&(1<<23) else -1)
        ix=pool-base
        if ix<0 or ix+4>len(data) or ix%4:continue
        target=struct.unpack_from('<I',data,ix)[0]
        if target not in SPI:continue
        matches.append({'instruction':f'0x{base+i:08X}','literal':f'0x{pool:08X}','register':f'r{(op>>12)&15}','hardware':SPI[target],'hardware_address':f'0x{target:08X}'})
    return matches
def group(rows,window=160):
    groups=[]
    for row in rows:
        address=int(row['instruction'],16)
        if not groups or address-int(groups[-1][-1]['instruction'],16)>window:groups.append([])
        groups[-1].append(row)
    return [{'start':g[0]['instruction'],'end':g[-1]['instruction'],'count':len(g),'registers':sorted(set(x['hardware'] for x in g)),'both_spi_registers':len(set(x['hardware'] for x in g))==2} for g in groups]
def analyze(rom):
    base,arm7=extract_arm7(rom)
    rows=scan(base,arm7);groups=group(rows)
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'arm7_base':f'0x{base:08X}','arm7_end':f'0x{base+len(arm7):08X}','literal_loads':rows,'groups':groups,'limitations':['SPICNT/SPIDATA are shared by touchscreen, firmware flash, and other peripherals; a reference does not prove touchscreen sampling.','Literal reference groups are not function boundaries.','No run-time ARM7/ARM9 communication or x/y coordinate fields are established.','Original ROM unchanged; no in-game patch.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--output',default='.');a=p.parse_args();dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    report=analyze(Path(a.rom).read_bytes());(dest/'spi_report.json').write_text(json.dumps(report,indent=2)+'\n')
    with (dest/'spi_references.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['instruction','literal','register','hardware','hardware_address']);w.writeheader();w.writerows(report['literal_loads'])
    with (dest/'spi_groups.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['start','end','count','registers','both_spi_registers']);w.writeheader();w.writerows({**r,'registers':';'.join(r['registers'])} for r in report['groups'])
    print('ARM7 SPI literal loads:',len(report['literal_loads']),'groups:',len(report['groups']),'groups with both:',sum(g['both_spi_registers'] for g in report['groups']))
if __name__=='__main__':main()
