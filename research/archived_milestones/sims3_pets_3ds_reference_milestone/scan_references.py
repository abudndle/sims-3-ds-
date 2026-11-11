#!/usr/bin/env python3
"""Read-only lexical search over named archives and ExeFS .code; matches are leads, not decoded structures."""
import csv,glob,re,json,collections
from pathlib import Path
cci=Path(glob.glob('/mnt/data/*decrypted.cci')[0]);out=Path('/mnt/data/sims3_pets_reference')
terms=('camera','cursor','pointer','highlight','select','interact','build','buy','furniture','menu','hud','touch','move','lot','object','sim','phone','mood','wish','control','view','zoom','target','location','career','inventory','texture')
rows=list(csv.DictReader((out/'romfs_inventory.csv').open()))
hits=[];counts={}
with cci.open('rb') as f:
 for item in rows:
  size=int(item['size']);name=item['path']
  if size>55_000_000:continue
  f.seek(int(item['rom_offset_hex'],16));blob=f.read(size)
  matches=[]
  for m in re.finditer(rb'[ -~]{5,110}',blob):
   string=m.group().decode('ascii','replace').strip()
   if any(t in string.lower() for t in terms):
    matches.append({'source':name,'offset_hex':hex(m.start()),'text':string[:110]})
  counts[name]=len(matches);hits.extend(matches[:1500])
 with (out/'keyword_leads.csv').open('w',newline='') as w:
  dw=csv.DictWriter(w,fieldnames=['source','offset_hex','text']);dw.writeheader();dw.writerows(hits)
 f.seek(0x4e00);blob=f.read(2154468)
 codehits=[]
 for m in re.finditer(rb'[ -~]{5,100}',blob):
  s=m.group().decode('ascii','replace').strip()
  if any(t in s.lower() for t in terms):codehits.append({'source':'ExeFS/.code','offset_hex':hex(m.start()),'text':s[:100]})
 with (out/'code_keyword_leads.csv').open('w',newline='') as w:
  dw=csv.DictWriter(w,fieldnames=['source','offset_hex','text']);dw.writeheader();dw.writerows(codehits)
 (out/'keyword_summary.json').write_text(json.dumps({'romfs_archives_scanned_under_55mb':len(counts),'romfs_keyword_hits_saved':len(hits),'code_keyword_hits':len(codehits),'top_sources':sorted(counts.items(),key=lambda x:-x[1])[:16]},indent=2))
 print((out/'keyword_summary.json').read_text());print('EXECUTABLE HITS:',*[x['text'] for x in codehits[:45]],sep='\n')
