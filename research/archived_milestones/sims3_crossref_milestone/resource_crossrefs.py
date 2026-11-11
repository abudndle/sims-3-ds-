#!/usr/bin/env python3
"""Read-only Sims 3 DS DSM1 cross-reference inventory. No game assets exported."""
import argparse,csv,hashlib,json,re,struct
from collections import defaultdict,Counter
from pathlib import Path
REF=re.compile(rb'(?<![A-Za-z0-9_./-])[A-Za-z0-9_][A-Za-z0-9_./-]{1,94}\.dst(?![A-Za-z0-9_./-])',re.I)
MAGIC={b'DSM1':'DSM1',b'DST1':'DST1'}

def index(rom,manifest,out):
    records=list(csv.DictReader(open(manifest,newline='',encoding='utf8')))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    allpacks=[]; dsm=[]; names=defaultdict(list); matched=defaultdict(set)
    with open(rom,'rb') as f:
      f.seek(0,2);romlen=f.tell()
      # Every referenced region is bounds checked and its digest verified.
      for r in records:
        start,size=int(r['offset']),int(r['size'])
        if start<0 or size<0 or start+size>romlen:raise ValueError('Invalid ROM bounds '+r['path'])
        if not r['path'].endswith('.package'): continue
        f.seek(start); data=f.read(size)
        if hashlib.sha256(data).hexdigest()!=r['sha256']: raise ValueError('Hash mismatch '+r['path'])
        allpacks.append((r['path'],data))
        if data[:4]!=b'DSM1':continue
        if len(data)<32:raise ValueError('Short DSM1 header')
        hdr=[struct.unpack_from('<I',data,i)[0] for i in range(4,32,4)]
        dsm.append({'package':r['path'],'package_bytes':size,'version_hex':data[4:8].hex(), 'header_u32_0x08':hdr[1], 'header_u32_0x0c_hex':hex(hdr[2]), 'header_u32_0x10':hdr[3], 'header_u32_0x14':hdr[4], 'header_u32_0x18':hdr[5]})
        for m in REF.finditer(data):
          if m.end()<len(data) and data[m.end()] not in (0,1,2,3,4,8,16,32):continue
          name=m.group().decode('ascii').lower()
          names[name].append((r['path'],m.start()))
      # Distinct coverage in full ARM binaries and all other packages; no claims about execution use.
      for path,data in allpacks:
        lower=data.lower()
        for name in names:
          if name.encode('ascii') in lower: matched[name].add(path)
      for label,off,size in [('ARM9',0x20,0x2c),('ARM7',0x30,0x3c)]:
        f.seek(off); b=f.read(12)
        address,entry,romoff=struct.unpack('<III',b)
        f.seek(size); length=struct.unpack('<I',f.read(4))[0]
        if romoff+length>romlen:raise ValueError('Invalid '+label+' binary range')
        f.seek(romoff); data=f.read(length).lower()
        for name in names:
          if name.encode('ascii') in data:matched[name].add(label)
    nitro_names={r['path'].split('/')[-1].lower() for r in records}
    rows=[]
    for name,occ in sorted(names.items()):
      packnames=sorted(set(p for p,_ in occ))
      hits=sorted(matched[name]);other=sorted(set(hits)-set(packnames)-{'ARM9','ARM7'})
      rows.append({'reference':name,'reference_occurrences':len(occ),'dsm1_packages':';'.join(packnames),'other_package_hits':';'.join(other),'arm_binary_literal_hit':'yes' if any(h in ('ARM9','ARM7') for h in hits) else 'no','standalone_nitrofs_basename':'yes' if name in nitro_names else 'no','first_package_offset_hex':hex(occ[0][1])})
    with (out/'dsm1_header_observations.csv').open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=list(dsm[0]));w.writeheader();w.writerows(dsm)
    with (out/'resource_crossreferences.csv').open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'validated_packages':len(allpacks),'dsm1_packages':len(dsm),'unique_reference_names':len(rows),'total_reference_occurrences':sum(len(x) for x in names.values()),'names_in_multiple_dsm1_packages':sum(len(set(p for p,_ in x))>1 for x in names.values()),'names_literal_in_other_packages':sum(bool(r['other_package_hits']) for r in rows),'names_literal_in_arm_code':sum(r['arm_binary_literal_hit']=='yes' for r in rows),'names_with_standalone_nitrofs_basename':sum(r['standalone_nitrofs_basename']=='yes' for r in rows),'confirmed_cut_content':0,'limitations':['DSM1 header values are observations, not proven semantics.','Textual references do not establish game runtime usage or unused status.','Literal scans cannot detect hashed/compressed/indirect references.','No copyrighted game asset data exported.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('manifest');p.add_argument('--out',default='crossref_results');a=p.parse_args();print(json.dumps(index(a.rom,a.manifest,a.out),indent=2))
