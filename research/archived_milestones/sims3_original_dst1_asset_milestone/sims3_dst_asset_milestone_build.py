#!/usr/bin/env python3
"""Original The Sims 3 DS DST1 format investigation: decode verified linear 4bpp sprites."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv, json, hashlib, zipfile, shutil, subprocess
ROOT=Path('/mnt/data')
SRC=ROOT/'sims3_analysis/nitrofs/DATA/BACKEND/HUD'
OUT=ROOT/'sims3_dst_asset_milestone'; OUT.mkdir(exist_ok=True)
ASSETS=['button_left.dst','button_right.dst','button_tutorial.dst','button_house.dst','button_people.dst','button_career.dst','button_opportunity.dst','button_relationship.dst','button_skills.dst','button_building.dst','button_lifetimehappiness.dst','COMPOSITES/Tutorial.dst','COMPOSITES/TimeControl.dst','COMPOSITES/PieMenu.dst','COMPOSITES/MenuBlue.dst','COMPOSITES/InfoIcons.dst']

def decode_dst1(blob):
 if blob[:4]!=b'DST1': raise ValueError('not DST1')
 if len(blob)<18: raise ValueError('truncated')
 width=int.from_bytes(blob[12:14],'little');height=int.from_bytes(blob[14:16],'little');n=int.from_bytes(blob[16:18],'little')
 if not (1<=width<=1024 and 1<=height<=1024 and 1<=n<=16):raise ValueError('invalid dimensions/palette')
 if width*height%2:raise ValueError('odd pixel count unsupported')
 off=18+2*n
 if len(blob)!=off+width*height//2:raise ValueError(f'Unexpected length {len(blob)} vs {off+width*height//2}')
 colors=[]
 for i in range(n):
  v=int.from_bytes(blob[18+i*2:20+i*2],'little')
  colors.append(((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31, 0 if i==0 else 255))
 im=Image.new('RGBA',(width,height)); pixels=im.load();p=blob[off:]
 for y in range(height):
  for x in range(width):
   idx=y*width+x;ci=(p[idx//2]>>(4*(idx%2)))&15
   pixels[x,y]=colors[ci] if ci<n else (255,0,255,255)
 return im,{'width':width,'height':height,'palette_entries':n,'data_offset':off,'bytes':len(blob)}

def main():
 records=[]; decoded={};errors=[]
 for asset in ASSETS:
  b=(SRC/asset).read_bytes()
  try:
   im,info=decode_dst1(b); decoded[asset]=im
   records.append({'asset':asset,**info,'sha256':hashlib.sha256(b).hexdigest(),'status':'decoded'})
  except ValueError as e:
   errors.append({'asset':asset,'reason':str(e)}); records.append({'asset':asset,'status':'unsupported','reason':str(e)})
 # Sprite atlas of real icons, 1:1 pixels; references to exact ROM filenames
 tilew,tileh=170,118
 atlas=Image.new('RGB',(tilew*4,tileh*4),(31,57,91));d=ImageDraw.Draw(atlas)
 for i,(name,im) in enumerate(decoded.items()):
  x=(i%4)*tilew;y=(i//4)*tileh
  d.rectangle((x+3,y+3,x+tilew-4,y+tileh-4),outline=(113,159,205),width=2)
  mini=im.copy(); mini.thumbnail((112,78),Image.Resampling.NEAREST)
  bg=Image.new('RGBA',mini.size,(230,236,247,255));bg.alpha_composite(mini)
  atlas.paste(bg.convert('RGB'),(x+(tilew-mini.width)//2,y+8))
  label=name.split('/')[-1].replace('.dst','')
  d.text((x+6,y+91),label,fill='white')
 atlas.save(OUT/'original_ui_dst_atlas.png')
 # actual screen compositing uses original button art; text and background are layout placeholders.
 screen=Image.new('RGB',(256,192),(37,70,108));s=ImageDraw.Draw(screen)
 s.rectangle((4,4,251,27),fill=(72,106,154),outline=(164,205,229))
 s.text((12,10),'TUTORIAL',fill='white')
 s.rounded_rectangle((5,32,250,137),radius=6,fill=(201,218,235),outline=(147,185,215),width=2)
 s.text((18,45),'Move the blue cursor',fill=(21,49,83));s.text((18,61),'with the D-Pad.',fill=(21,49,83))
 s.text((18,80),'Press A on a green target.',fill=(21,49,83))
 # verify two original 64x64 art icons are positioned in screen bounds at 32px (scaled preview only)
 items=[('button_left.dst',(6,143,40,183)),('button_right.dst',(51,143,85,183)),('button_tutorial.dst',(205,90,245,130))]
 for name,(l,t,r,b) in items:
  art=decoded[name].resize((r-l,b-t),Image.Resampling.NEAREST)
  screen.paste(art,(l,t),art)
 s.rounded_rectangle((130,151,247,185),radius=5,fill=(101,145,187),outline=(182,218,235))
 s.text((155,163),'Continue',fill='white')
 screen.save(OUT/'actual_rom_asset_tutorial_preview_256x192.png')
 # machine-readable metadata and standalone reproduction script
 with (OUT/'dst1_inventory.csv').open('w',newline='') as fp:
  writer=csv.DictWriter(fp,fieldnames=['asset','status','width','height','palette_entries','data_offset','bytes','sha256','reason'],extrasaction='ignore');writer.writeheader();writer.writerows(records)
 (OUT/'summary.json').write_text(json.dumps({'decoded':len(decoded),'unsupported':errors,'preview_size':list(screen.size),'sprite_mapping':{k:v for k,v in items}},indent=2))
 (OUT/'README.md').write_text('''# Original Sims 3 DS DST1 UI assets — verified decode milestone

- Input: supplied `VS3E` Nintendo DS ROM extraction (`DATA/BACKEND/HUD`). Original ROM unchanged.
- New verified format subset: `DST1` header, width/height at offsets `0x0c`/`0x0e`, palette count at `0x10`, palette BGR555 from `0x12`, linear 4-bit pixels after palette; first palette entry rendered transparent for the visual preview.
- The original button sprites decode to recognizable graphics; the atlas was generated directly from original DST1 bytes, not generative art.
- `actual_rom_asset_tutorial_preview_256x192.png` is a **layout preview using real extracted sprites**. Backgrounds and text are placeholders, not game graphics or a melonDS capture.
- A decoded sprite is not proof that the game uses that sprite for the proposed purpose; it remains to hook the game's original resource loader, scene renderer and touch input.
- The 3D view/top-screen reassignment, camera-speed matching and task UI are not yet integrated in the ROM.
- To reproduce in this environment: `python sims3_dst_asset_milestone_build.py`. Input files must come from your own game dump.

Tests: every successful asset has an exact predicted length; preview is exactly 256x192; all its asset placements lie within bounds.
''')
 # Copy script but references user-owned extracts, avoids including raw copyrighted sprite assets in code archive
 shutil.copy(__file__,OUT/'sims3_dst_asset_milestone_build.py')
 assert screen.size==(256,192)
 for _,coords in items: assert 0<=coords[0]<coords[2]<=256 and 0<=coords[1]<coords[3]<=192
 assert 'button_left.dst' in decoded and 'button_right.dst' in decoded
 print('Decoded',len(decoded),'of',len(ASSETS),'unsupported',errors)
 print('Sprite atlas',OUT/'original_ui_dst_atlas.png')
 zipname=ROOT/'sims3_original_dst1_asset_milestone.zip'
 with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for f in OUT.iterdir(): z.write(f,f.name)
 print('Archive',zipname,zipname.stat().st_size,'zip test',zipfile.ZipFile(zipname).testzip())
if __name__=='__main__': main()
