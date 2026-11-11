#!/usr/bin/env python3
"""Read-only metadata inventory of decrypted Sims 3 Pets 3DS CCI. Standard NCSD/NCCH/IVFC/RomFS."""
from pathlib import Path
import struct,csv,json,collections,hashlib,sys
p=Path(sys.argv[1]); out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def u64(b,o):return struct.unpack_from('<Q',b,o)[0]
with p.open('rb') as f:
 f.seek(0x100);assert f.read(4)==b'NCSD','Not NCSD'
 f.seek(0x120);base,length=struct.unpack('<II',f.read(8));base*=512;length*=512
 f.seek(base+0x100);assert f.read(4)==b'NCCH','Not NCCH'
 f.seek(base+0x150);product=f.read(16).rstrip(b'\0').decode('ascii','replace')
 f.seek(base+0x1a0);exo,exl=struct.unpack('<II',f.read(8));f.seek(base+0x1b0);rmo,rml=struct.unpack('<II',f.read(8))
 exbase=base+exo*512; rombase=base+rmo*512
 f.seek(exbase);exehead=f.read(0x200)
 exefs=[]
 for n in range(10):
  e=exehead[n*16:(n+1)*16]; name=e[:8].split(b'\0')[0].decode('ascii','replace'); ofs,size=struct.unpack_from('<II',e,8)
  if name: exefs.append({'name':name,'offset_hex':hex(exbase+512+ofs),'size':size})
 f.seek(rombase);ivfc=f.read(0x60);assert ivfc[:4]==b'IVFC'
 lvl3offset=u64(ivfc,0x3c); lvl3size=u64(ivfc,0x44); lvl3base=rombase+0x1000 # Verified RomFS filesystem header at this location; IVFC level3 offset refers to hash layout
 f.seek(lvl3base);rh=f.read(0x28)
 hdr,dh,dhsize,dm,dmsize,fh,fhsize,fm,fmsize,dataoff=struct.unpack('<10I',rh)
 assert hdr==0x28 and dm+dmsize<lvl3size and fm+fmsize<lvl3size, f'RomFS metadata header absent at expected level3 offset: {rh[:16].hex()}; encrypted/unsupported layout likely'
 f.seek(lvl3base+dm); dirs=f.read(dmsize)
 f.seek(lvl3base+fm); files=f.read(fmsize)
 def dirent(off):
  if off==0xffffffff:return None
  if off+0x18>len(dirs):raise ValueError(('dir out of bounds',off))
  parent,sib,childdir,childfile,hashnext,namelen=struct.unpack_from('<6I',dirs,off)
  name=dirs[off+0x18:off+0x18+namelen].decode('utf-16le')
  return dict(parent=parent,sib=sib,childdir=childdir,childfile=childfile,name=name)
 def fileent(off):
  if off==0xffffffff:return None
  if off+0x20>len(files):raise ValueError(('file out of bounds',off))
  parent,sib,dataofs,size,hashnext,namelen=struct.unpack_from('<IIQQII',files,off)
  name=files[off+0x20:off+0x20+namelen].decode('utf-16le')
  return dict(parent=parent,sib=sib,dataofs=dataofs,size=size,name=name)
 records=[]; seen_dirs=set();seen_files=set()
 def walk(off,path):
  if off in seen_dirs:raise ValueError('directory reference cycle')
  seen_dirs.add(off); d=dirent(off)
  ch=d['childfile']
  while ch!=0xffffffff:
   if ch in seen_files:raise ValueError('file reference cycle')
   seen_files.add(ch); entry=fileent(ch)
   if entry['dataofs']+entry['size']>lvl3size-dataoff: raise ValueError('file past RomFS')
   records.append({'path':path+entry['name'],'size':entry['size'],'rom_offset_hex':hex(lvl3base+dataoff+entry['dataofs'])})
   ch=entry['sib']
  ch=d['childdir']
  while ch!=0xffffffff:
   d2=dirent(ch);walk(ch,path+d2['name']+'/');ch=d2['sib']
 walk(0,'/')
 counts=collections.Counter(Path(x['path']).suffix.lower() or '[no extension]' for x in records)
 keys=('ui','hud','cursor','camera','control','input','interaction','interact','menu','button','icon','build','buy','furniture','phone','mood','wish','overlay','navigation','map','world','texture','font','layout','pointer','select','target')
 focus=[r for r in records if any(k in r['path'].lower() for k in keys)]
 with (out/'romfs_inventory.csv').open('w',newline='') as o:
  w=csv.DictWriter(o,fieldnames=['path','size','rom_offset_hex']);w.writeheader();w.writerows(records)
 with (out/'reference_candidates.csv').open('w',newline='') as o:
  w=csv.DictWriter(o,fieldnames=['path','size','rom_offset_hex']);w.writeheader();w.writerows(focus)
 summary={'input_filename':p.name,'input_size_bytes':p.stat().st_size,'product_code':product,'ncch_partition_offset_hex':hex(base),'exe_fs':exefs,'romfs_offset_hex':hex(rombase),'romfs_level3_offset_hex':hex(lvl3base),'romfs_file_count':len(records),'romfs_directory_count':len(seen_dirs),'focused_filename_matches':len(focus),'top_extensions':counts.most_common(35)}
 (out/'summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary,indent=2))
 print('CANDIDATES:',*[x['path'] for x in focus[:35]],sep='\n')
