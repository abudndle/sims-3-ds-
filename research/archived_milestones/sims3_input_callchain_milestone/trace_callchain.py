#!/usr/bin/env python3
"""Read-only bounded Sims 3 DS ARM9 Thumb direct-call graph with conservative provenance."""
from pathlib import Path
import argparse,struct,json,hashlib,csv

def arm9(rom):
    if len(rom)<0x40: raise ValueError('short ROM')
    off,entry,base,size=struct.unpack_from('<IIII',rom,0x20)
    if off<0x200 or off+size>len(rom) or size==0 or not(base<=entry<base+size):
        raise ValueError('invalid ARM9 bounds')
    return base,memoryview(rom)[off:off+size]

def decode_bl(pc,first,second):
    if first&0xf800!=0xf000 or second&0xf800 not in (0xf800,0xe800):return None
    off=((first&0x7ff)<<12)|((second&0x7ff)<<1)
    if off & 0x400000:off-=0x800000
    addr=pc+4+off
    mode='BLX' if second&0xf800==0xe800 else 'BL'
    if mode=='BLX':addr&=~3
    return addr,mode

def callsites(base,code,targets):
    result={x:[] for x in targets}
    for pos in range(0,len(code)-3,2):
        h1,h2=struct.unpack_from('<HH',code,pos)
        d=decode_bl(base+pos,h1,h2)
        if d and d[0] in result:
            result[d[0]].append(dict(address=base+pos,mode=d[1],opcode=bytes(code[pos:pos+4]).hex()))
    return result

def analyze(rom):
    base,code=arm9(rom)
    # Function entries independently supported by a Thumb PUSH at each address;
    # these are candidates, not independently proven function limits.
    funcs={'read_buttons_1':0x02095C0C,'consumer_1':0x02095CBC,
           'read_buttons_2':0x020A14E4,'consumer_2':0x020A2690}
    for name,addr in funcs.items():
        if not base<=addr<base+len(code):raise ValueError('candidate out of image')
        halfword=struct.unpack_from('<H',code,addr-base)[0]
        if halfword&0xff00 not in (0xb400,0xb500):raise ValueError(f'{name} has no Thumb PUSH at entry: {halfword:04x}')
    found=callsites(base,code,set(funcs.values()))
    entries=[]
    for name,addr in funcs.items():
        entries.append({'name':name,'address':f'0x{addr:08X}', 'entry_opcode':f'0x{struct.unpack_from("<H",code,addr-base)[0]:04X}',
            'direct_static_calls':[{'at':f'0x{x["address"]:08X}','opcode':x['opcode'],'mode':x['mode']} for x in found[addr]]})
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'arm9_range':[f'0x{base:08X}',f'0x{base+len(code):08X}'],
        'entries':entries,'limitations':['A matching Thumb halfword sequence is not proof of an executed code path: some may be embedded data.',
        'PUSH instructions are candidate entries, not full recovered function boundaries.',
        'Touch coordinate dispatch and UI event mapping remain unconfirmed.',
        'No ROM writes or game behavior changes were performed.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('--output',default='callchain.json');a=p.parse_args()
    obj=analyze(Path(a.rom).read_bytes())
    Path(a.output).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'results':[(x['name'],len(x['direct_static_calls'])) for x in obj['entries']]},indent=2))
if __name__=='__main__':main()
