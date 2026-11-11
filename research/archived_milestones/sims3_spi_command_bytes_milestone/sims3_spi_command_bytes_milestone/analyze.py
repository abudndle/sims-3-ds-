#!/usr/bin/env python3
"""Read-only instruction-anchored analysis of ARM7 SPI command arguments.
No ROM modifications; known signatures checked before reporting classifications.
"""
import argparse, csv, hashlib, json, struct
from pathlib import Path
EXPECTED='d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a'
SEND=0x0238C9D8
READ=0x0238CA54
# Callsite, target, r0 precursor, exact opcode, symbolic provenance.
SITES=[
 (0x0238CAD8,READ,0x0238CAD4,0xE1A00004,'r4',None),
 (0x0238CAE4,SEND,0x0238CAE0,0xE1A00004,'r4',None),
 (0x0238CB00,READ,0x0238CAFC,0xE1A00004,'r4',None),
 (0x0238CB14,SEND,0x0238CB10,0xE1A00004,'r4',None),
 (0x0238CCF0,READ,0x0238CCEC,0xE3A00000,'immediate',0),
 (0x0238CD34,READ,0x0238CD30,0xE1A00005,'r5',2),
 (0x0238CD9C,READ,0x0238CD98,0xE1A00006,'r6',3),
 (0x0238CE00,READ,0x0238CDFC,0xE1A00006,'r6',3),
 (0x0238CEFC,READ,0x0238CEF8,0xE1A00008,'r8',None),
 (0x0238CF10,SEND,0x0238CF08,0xE20000FF,'masked-r0',None),
 (0x0238D224,READ,0x0238D220,0xE3A00000,'immediate',0),
 (0x0238D31C,SEND,0x0238D318,0xE3A00000,'immediate',0),
]
SOURCES={0x0238CB28:0xE1A08001,0x0238CB30:0xE3A05002,0x0238CB34:0xE3A06003,
         0x0238CA6C:0xE3800080}

def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def bl_target(w,pc):
    if (w&0x0F000000)!=0x0B000000:return None
    imm=w&0xffffff
    if imm&0x800000:imm-=0x1000000
    return pc+8+imm*4

def analyze(data,verify_digest=True):
    sha=hashlib.sha256(data).hexdigest()
    if verify_digest and sha!=EXPECTED:raise ValueError('ROM SHA256 mismatch: wrong ROM revision')
    off,base,size=(u32(data,p) for p in (0x30,0x38,0x3c))
    if base!=0x02380000 or off+size>len(data):raise ValueError('Unexpected ARM7 layout')
    def op(addr):
        i=addr-base
        if i<0 or i+4>size or i%4:raise ValueError(f'ARM7 address out of range: {addr:08X}')
        return u32(data,off+i)
    for addr,expected in SOURCES.items():
        if op(addr)!=expected:raise ValueError(f'Anchor opcode mismatch {addr:08X}')
    rows=[]
    for pc,target,source,expected,origin,constant in SITES:
        if op(source)!=expected:raise ValueError(f'Argument opcode mismatch {source:08X}')
        if bl_target(op(pc),pc)!=target:raise ValueError(f'Call target mismatch {pc:08X}')
        wire=(constant|0x80) if constant is not None and target==READ else (constant if constant is not None else None)
        rows.append(dict(callsite=f'0x{pc:08X}',helper=('read' if target==READ else 'send'),
                         argument_instruction=f'0x{source:08X}',r0_origin=origin,
                         r0_value=constant,transmitted_command=wire,
                         confidence=('fixed' if origin=='immediate' else 'inferred-from-dispatcher-constant' if constant is not None else 'dynamic-or-unresolved')))
    return dict(rom_sha256=sha,arm7_base=f'0x{base:08X}',read_helper=f'0x{READ:08X}',
                read_helper_sets_bit7_at='0x0238CA6C',
                dispatcher_preserved_constants={'r5':{'value':2,'address':'0x0238CB30'},'r6':{'value':3,'address':'0x0238CB34'},'r8':{'source':'entry r1','address':'0x0238CB28'}},
                count=len(rows),calls=rows)

def main():
    a=argparse.ArgumentParser();a.add_argument('rom');a.add_argument('--out',default='results');args=a.parse_args()
    result=analyze(Path(args.rom).read_bytes());out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'commands.json').write_text(json.dumps(result,indent=2)+'\n')
    with (out/'commands.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=result['calls'][0].keys());w.writeheader();w.writerows(result['calls'])
    print(f"Verified {result['count']} SPI calls; fixed-wire commands: "+', '.join(f"{r['callsite']}=0x{r['transmitted_command']:02X}" for r in result['calls'] if r['transmitted_command'] is not None))
if __name__=='__main__':main()
