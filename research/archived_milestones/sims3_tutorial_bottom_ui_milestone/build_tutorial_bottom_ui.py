from pathlib import Path
import struct, hashlib,zlib,json,zipfile,importlib.util
root=Path('/mnt/data'); rom=next(root.glob('Sims 3, The (USA)*.nds')); base=rom.read_bytes()
asset=root/'sims3_analysis/nitrofs/DATA/LOCALIZATION/text_db_dynamic.arc';original=asset.read_bytes()
assert len(base)==134217728 and hashlib.md5(base).hexdigest()=='7cdf32d02eeeff592a0a4ab6bec7b5c1'
manifest=__import__('csv').DictReader((root/'sims3_analysis/file_manifest.csv').open());entry=next(x for x in manifest if x['path']=='DATA/LOCALIZATION/text_db_dynamic.arc');off=int(entry['offset']);size=int(entry['size']);assert size==len(original) and base[off:off+size]==original
changes=[
('Welcome to The Sims 3 Tutorial! Here you will learn the basic gameplay of The Sims 3. When you are ready to proceed touch the Tutorial icon in the right hand corner.', '3D stays on the top screen with only the blue/green cursor. Read the tutorial and touch Continue on the bottom screen. All game UI also belongs on the bottom.'),
('Touch where in the world you would like to move your Sim with the stylus. Depending on what you touch, there might be multiple options that appear - select the one you wish your Sim to perform.', 'Move the blue cursor with the D-Pad. Usable targets turn green. Press A and choose actions on the bottom screen. B cancels. The top screen shows only 3D.'),
('Summary pages on the top screen contain critical information about your Sim and his life.  The L Button and R Button cycle through them. ', 'Tutorial and Sim details go below. Touch arrows to switch pages. The top screen only shows 3D and cursor.'),
]
updated=bytearray(original);report=[]
for old,new in changes:
 oldb=old.encode();newb=new.encode();assert len(newb)<=len(oldb),(len(newb),len(oldb))
 assert original.count(oldb+b'\0')==1,old[:20]
 idx=original.index(oldb+b'\0');updated[idx:idx+len(oldb)]=newb+b'\0'*(len(oldb)-len(newb))
 assert updated[idx+len(oldb)]==0
 report.append({'archive_offset':idx,'rom_offset':off+idx,'original':old,'replacement':new,'original_bytes':len(oldb),'replacement_bytes':len(newb)})
target=bytearray(base);target[off:off+size]=updated
assert len(target)==len(base)
# Build efficient BPS with unmodified blocks and target-read replacements (same length)
def enc(n):
 b=bytearray()
 while True:
  x=n&127;n>>=7
  if n==0:b.append(x|128);return b
  b.append(x);n-=1
chunks=[]
for e in report:
 start=e['rom_offset'];n=e['original_bytes'];chunks.append((start,n,bytes(target[start:start+n])))
chunks.sort();patch=bytearray(b'BPS1');patch+=enc(len(base))+enc(len(target))+enc(0);pos=0
for start,n,dat in chunks:
 if start>pos:patch+=enc(((start-pos-1)<<2)|0)
 patch+=enc(((n-1)<<2)|1)+dat;pos=start+n
if pos<len(base):patch+=enc(((len(base)-pos-1)<<2)|0)
patch+=struct.pack('<II',zlib.crc32(base),zlib.crc32(target));patch+=struct.pack('<I',zlib.crc32(patch))
out=root/'sims3_tutorial_bottom_ui_milestone';out.mkdir(exist_ok=True)
(out/'Sims3_DS_Bottom_UI_Tutorial_Preview.bps').write_bytes(patch)
# reuse BPS implementation and verify full output
spec=importlib.util.spec_from_file_location('bps',root/'sims3_japanese_logo_mod/apply_bps.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert mod.apply_bps(base,bytes(patch))==bytes(target)
(out/'apply_bps.py').write_text((root/'sims3_japanese_logo_mod/apply_bps.py').read_text())
(out/'tutorial_changes.json').write_text(json.dumps(report,indent=2))
metadata={'source_md5':hashlib.md5(base).hexdigest(),'source_sha256':hashlib.sha256(base).hexdigest(),'target_sha256':hashlib.sha256(target).hexdigest(),'patch_size':len(patch),'changes':len(report),'file':'DATA/LOCALIZATION/text_db_dynamic.arc','rom_length_preserved':True,'original_not_modified':True,'patch_roundtrip_passed':True}
(out/'verification.json').write_text(json.dumps(metadata,indent=2))
(out/'README.md').write_text('''# The Sims 3 DS — reworked-controls tutorial TEXT PREVIEW

This is a **real BPS patch to the original USA VS3E Rev 0 ROM localization asset**, built from the user-supplied ROM and verified by reapplying it. It replaces three tutorial/help messages describing the *planned* control and screen configuration.

## Critical limitation

**The new controls and screen routing are NOT implemented in this ROM.** This remains a **text-only proof-of-concept**, not a finished or playable controls conversion. Some prompts in the original tutorial still expect the original inputs, including X/B for zoom and L/R for page navigation. The tutorial may be inconsistent until the gameplay/input code is integrated. Do not treat this as the finished control mod.

## Use

```bash
python3 apply_bps.py 'Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' Sims3_DS_Bottom_UI_Tutorial_Preview.bps Sims3_Bottom_UI_Tutorial_Preview.nds
```

Only the English tutorial strings in `DATA/LOCALIZATION/text_db_dynamic.arc` are modified. CRC32 validates the source and output. The original ROM remains unchanged.

## Next engineering milestones

1. Identify in-game tutorial state/input gates and remap them from stylus/X/B/L/R actions to the new controller behavior.
2. Implement the D-Pad blue/green ground cursor and A/B interactions with original DS resources.
3. Move gameplay 3D to the top screen and UI to bottom while preserving touch interactions.
4. Update all English tutorial pages and localization consistency, then validate gameplay in melonDS.

No full ROM or proprietary game assets are included in this patch package.
''')
with zipfile.ZipFile(root/'sims3_tutorial_bottom_ui_milestone.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in out.iterdir():z.write(f,arcname=f.name)
print(json.dumps(metadata,indent=2))
