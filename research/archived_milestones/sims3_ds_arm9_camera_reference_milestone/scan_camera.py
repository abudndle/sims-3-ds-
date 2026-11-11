#!/usr/bin/env python3
"""Read-only Sims 3 DS ARM9 camera/UI string and literal-pointer locator."""
import argparse,csv,hashlib,json,struct
from pathlib import Path
TERMS=['camera','zoom','input plane','touch','cursor','button']
def u32(b,n):return struct.unpack_from('<I',b,n)[0]
def scan(path):
    with open(path,'rb') as f:
        hdr=f.read(0x200)
        arm9off,entry,load,size=(u32(hdr,i) for i in (0x20,0x24,0x28,0x2c))
        assert size>0 and arm9off+size<=path.stat().st_size
        f.seek(arm9off); data=f.read(size)
    rows=[];i=0
    while i<len(data):
        if not 32<=data[i]<=126:i+=1;continue
        start=i
        while i<len(data) and 32<=data[i]<=126:i+=1
        if i<len(data) and data[i]==0 and i-start>=5:
            s=data[start:i].decode('ascii')
            if any(t in s.lower() for t in TERMS):
                addr=load+start
                ptr=struct.pack('<I',addr)
                refs=[];p=0
                while (p:=data.find(ptr,p))!=-1:
                    if p%4==0:refs.append({'arm9_offset':f'0x{p:06X}','cpu_address':f'0x{load+p:08X}','rom_offset':f'0x{arm9off+p:08X}'})
                    p+=4
                rows.append({'string':s,'arm9_offset':f'0x{start:06X}','cpu_address':f'0x{addr:08X}','rom_offset':f'0x{arm9off+start:08X}','literal_pointer_count':len(refs),'literal_pointers':refs})
    return {'rom_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'arm9_rom_offset':f'0x{arm9off:X}','arm9_load':f'0x{load:X}','arm9_entry':f'0x{entry:X}','arm9_size':size,'matching_strings':rows}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('--output',type=Path,default=Path('camera_report.json'));args=ap.parse_args()
    result=scan(args.rom);args.output.write_text(json.dumps(result,indent=2)+'\n')
    with args.output.with_suffix('.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['string','arm9_offset','cpu_address','rom_offset','literal_pointer_count']);wr.writeheader();wr.writerows({k:r[k] for k in wr.fieldnames} for r in result['matching_strings'])
    print(f"{len(result['matching_strings'])} camera/input strings, {sum(x['literal_pointer_count'] for x in result['matching_strings'])} aligned literal references")
if __name__=='__main__':main()
