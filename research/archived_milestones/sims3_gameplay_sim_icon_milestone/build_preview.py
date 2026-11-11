#!/usr/bin/env python3
"""Recreate a layout preview from the user's own extracted original Sims 3 DS DST1 sprites."""
from pathlib import Path
from PIL import Image,ImageDraw
import sys,csv
ROOT=Path(__file__).resolve().parent
ASSET=Path('/mnt/data/sims3_analysis/nitrofs/DATA/BACKEND/HUD')
sys.path.insert(0,'/mnt/data')
from sims3_dst_asset_milestone_build import decode_dst1

def original(name, size):
    img,_=decode_dst1((ASSET/name).read_bytes())
    return img.resize(size,Image.Resampling.NEAREST)

im=Image.new('RGBA',(256,192),(45,79,125,255))
d=ImageDraw.Draw(im)
d.rectangle((0,0,255,43),fill=(31,60,107),outline=(154,193,218))
d.rounded_rectangle((5,47,250,157),radius=6,fill=(173,197,225),outline=(225,238,248),width=2)
d.text((53,11),'Sim information',fill='white')
d.text((16,55),'Mood / Needs / Wishes',fill=(24,43,74))
d.text((16,78),'Job / Traits / Happiness',fill=(24,43,74))
d.text((16,106),'Tap Sims icon to return',fill=(24,43,74))
d.text((16,121),'from another gameplay panel',fill=(24,43,74))
# Real original game sprites (not redrawn icons). Do not claim button_people is necessarily
# the original in-game Sim-info icon; this is a candidate placeholder for layout binding.
for name, pos, size in [('button_people.dst',(4,4),(40,36)),('button_left.dst',(8,160),(28,28)),('button_right.dst',(37,160),(28,28)),('button_career.dst',(215,160),(32,28))]:
    spr=original(name,size);im.alpha_composite(spr,pos)
d.text((90,167),'Gameplay UI',fill='white')
im.convert('RGB').save(ROOT/'previews/normal_gameplay_sim_icon_256x192.png')
assert im.size==(256,192)
with (ROOT/'asset_mapping.csv').open('w',newline='') as f:
    wr=csv.writer(f);wr.writerow(['purpose','original_dst_path','binding_status'])
    wr.writerows([['Sim icon candidate','DATA/BACKEND/HUD/button_people.dst','visual candidate only; not confirmed original Sims navigation icon'],['Arrow left','DATA/BACKEND/HUD/button_left.dst','decoded'],['Arrow right','DATA/BACKEND/HUD/button_right.dst','decoded'],['Career icon','DATA/BACKEND/HUD/button_career.dst','decoded']])
print('PASS actual extracted DST1 sprites rendered to 256x192 preview')
