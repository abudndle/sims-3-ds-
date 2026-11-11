#!/usr/bin/env python3
"""Read-only, hash-verified scene-reference inventory for Sims 3 DS VS3E.
No copyrighted resource payload is exported.
"""
import argparse,csv,hashlib,json,re,sys
from pathlib import Path
NAME=re.compile(rb'(?<![A-Za-z0-9_./-])[A-Za-z0-9_][A-Za-z0-9_./-]{1,94}\.dst\x00',re.I)

def analyze(rom_path,manifest_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest=list(csv.DictReader(open(manifest_path,newline='',encoding='utf8')))
    records=[];scene_rows=[]; testbed=[]; fail=[]
    with open(rom_path,'rb') as rom:
        rom.seek(0,2);rom_size=rom.tell()
        for m in manifest:
            p=m['path']; terrain=p.startswith('DATA/BACKEND/LOTS/TERRAIN/') and p.endswith('.dsm')
            dev=p.startswith('DATA/LODTESTBED/')
            if not (terrain or dev):continue
            off,size=int(m['offset']),int(m['size'])
            if off<0 or size<0 or off+size>rom_size: raise ValueError('File outside ROM: '+p)
            rom.seek(off);data=rom.read(size)
            digest=hashlib.sha256(data).hexdigest()
            if digest!=m['sha256']:raise ValueError('SHA mismatch: '+p)
            matches=list(NAME.finditer(data))
            if terrain:
                positions=[x.start() for x in matches]
                # Observed layout: a byte immediately ahead of the first reference
                # equals the number of slots; names appear 64 bytes apart.
                count_byte=data[positions[0]-1] if positions and positions[0]>0 else None
                valid_count=count_byte==len(matches)
                valid_stride=all(y-x==64 for x,y in zip(positions,positions[1:]))
                # Within a 64-byte slot, a NUL-terminated resource name must fit.
                valid_slots=all((x.end()-x.start())<=64 for x in matches)
                if not (valid_count and valid_stride and valid_slots):fail.append(p)
                scene_rows.append({'path':p,'rom_offset_hex':hex(off),'size':size,'reference_count':len(matches),'observed_count_byte':count_byte,'first_name_offset_hex':hex(positions[0]) if positions else '', 'stride_64_valid':valid_stride,'sha256':digest})
                for i,x in enumerate(matches):
                    records.append({'path':p,'index':i,'name':x.group()[:-1].decode('ascii').lower(),'package_offset_hex':hex(x.start()),'rom_offset_hex':hex(off+x.start())})
            else:
                testbed.append({'path':p,'bytes':size,'sha256':digest,'references':';'.join(sorted(set(x.group()[:-1].decode('ascii').lower() for x in matches))),'magic_hex':data[:4].hex()})
    if fail:raise ValueError('Unexpected layout: '+', '.join(fail))
    for fn,rows in [('terrain_scenes.csv',scene_rows),('terrain_references.csv',records),('development_testbed.csv',testbed)]:
        with (out/fn).open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['path']);w.writeheader();w.writerows(rows)
    summary={'rom_sha256':hashlib.sha256(Path(rom_path).read_bytes()).hexdigest(),'terrain_scene_count':len(scene_rows),'terrain_reference_slots':len(records),'terrain_count_byte_matches':sum(x['reference_count']==x['observed_count_byte'] for x in scene_rows),'terrain_64_byte_stride_matches':sum(x['stride_64_valid'] for x in scene_rows),'development_testbed_files':len(testbed),'development_testbed_scene_files':sum(x['path'].lower().endswith('.dsm') for x in testbed),'development_testbed_resource_files':sum(x['path'].lower().endswith('.dst') for x in testbed),'confirmed_restored_features':0,'interpretation':'The LODTESTBED directory is a concrete development/test-named resource group; unused-at-runtime status is unproven. Terrain slot and count layout is observed, not a complete parser.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    return summary
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('manifest');ap.add_argument('--out',default='scene_reports');a=ap.parse_args()
    print(json.dumps(analyze(a.rom,a.manifest,a.out),indent=2))
