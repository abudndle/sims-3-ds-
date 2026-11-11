#!/usr/bin/env python3
"""Reproducible, read-only Sims 3 DS NitroFS package classifier.
Prints metadata only; never exports proprietary game bytes.
"""
import argparse,csv,hashlib,json,struct
from collections import Counter
from pathlib import Path

def classify(data):
    lead=data[:4]
    if lead in (b'DSM1',b'DST1',b'NPCS'):
        return lead.decode('ascii'), 'recognized four-byte signature'
    if lead==b'BML\x08':return 'BML-08', 'BML-prefixed binary; layout unverified'
    if lead[:2]==b'BM':return 'BM*', 'BM-prefixed binary (subtype unverified)'
    if lead==b'\x01\x00\xff\x00':return 'CAS-0100FF00','CAS-like binary prefix; format unverified'
    return 'unknown', 'binary format not identified'

def run(rom,manifest,out):
    items=list(csv.DictReader(manifest.open(newline='')))
    records=[];summary=Counter();issues=[]
    with rom.open('rb') as f:
        f.seek(0,2);romlen=f.tell()
        for item in items:
            name=item['path']
            if not name.endswith('.package'):continue
            off,size=int(item['offset']),int(item['size'])
            if off<0 or size<0 or off+size>romlen:
                issues.append(f'Out-of-bounds: {name}');continue
            f.seek(off);block=f.read(size)
            actual=hashlib.sha256(block).hexdigest()
            if actual!=item['sha256']:
                issues.append(f'Hash mismatch: {name}');continue
            kind,note=classify(block)
            summary[kind]+=1
            records.append({'path':name,'size_bytes':size,'signature_hex':block[:8].hex(),
                'format_group':kind,'classification_note':note,'header_u32_le_08':
                struct.unpack_from('<I',block,8)[0] if len(block)>=12 else '',
                'header_u32_le_0c':struct.unpack_from('<I',block,12)[0] if len(block)>=16 else '',
                'sha256':actual})
    out.mkdir(parents=True,exist_ok=True)
    with (out/'package_signatures.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    result={'packages_checked':len(records),'format_groups':dict(summary),'issues':issues,
        'interpretation':'Signature groups are not full decoders; header integers are raw observations, not interpreted counts.',
        'cut_content_confirmed':0}
    (out/'package_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('manifest',type=Path);p.add_argument('--out',type=Path,default=Path('metadata'))
    a=p.parse_args();print(json.dumps(run(a.rom,a.manifest,a.out),indent=2))
