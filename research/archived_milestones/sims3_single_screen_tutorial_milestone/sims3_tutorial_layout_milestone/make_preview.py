from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
root=Path(__file__).parent
out=root/'preview';out.mkdir(exist_ok=True)
font=ImageFont.load_default()
source=Path('/mnt/data/sims3_analysis/nitrofs/DATA/BACKEND/CallButton.bmp')
for scenario in ('instruction','interaction','task_complete','build'):
 im=Image.new('RGB',(256,192),(24,48,83));d=ImageDraw.Draw(im)
 d.rounded_rectangle((4,4,251,27),5,fill=(55,96,143),outline=(153,190,218),width=1)
 d.text((12,11),'THE SIMS 3  |  TUTORIAL',font=font,fill='white')
 if scenario=='build':
  d.rectangle((4,32,251,143),fill=(54,82,72),outline=(177,211,188))
  d.rectangle((26,52,226,122),outline=(177,203,168),width=3)
  d.line([(26,70),(120,95),(226,70)],fill=(177,203,168),width=2)
  d.text((45,81),'3D EDIT VIEW',font=font,fill='white')
  d.text((8,149),'Touch to place furniture',font=font,fill='white')
 else:
  d.rounded_rectangle((8,32,247,115),5,fill=(231,238,243),outline=(155,183,202))
  texts={'instruction':['Move the blue cursor','with the D-Pad.','Press A on a green target.'], 'interaction':['Choose an available action','on the bottom touchscreen.'], 'task_complete':['Task finished!','Tap Continue to proceed.']}
  for i,line in enumerate(texts[scenario]):d.text((17,46+15*i),line,font=font,fill=(19,44,72))
  d.text((10,125),'Tutorial status',font=font,fill=(227,236,246))
  d.rectangle((8,168,95,187), fill=(70,107,143),outline=(145,191,218));d.text((27,174),'Back',font=font,fill='white')
 d.rounded_rectangle((137,164,247,187),5,fill=(64,124,173) if scenario in ('instruction','task_complete','build') else (56,76,100),outline=(165,210,236))
 d.text((159,172),'Continue',font=font,fill='white')
 if scenario=='interaction':
  # Show interaction menu variant with original icon in left corner
  im=Image.new('RGB',(256,192),(24,48,83));d=ImageDraw.Draw(im)
  d.rectangle((4,4,251,27),fill=(55,96,143));d.text((12,11),'THE SIMS 3 | INTERACT',font=font,fill='white')
  d.rectangle((8,32,247,63),fill=(231,238,243));d.text((18,42),'Choose an action:',font=font,fill=(19,44,72))
  for j,txt in enumerate(('Talk','Use','Inspect','Cancel')):
   y=65+j*25;d.rectangle((8,y,247,y+23),fill=(99,142,179),outline=(175,204,228));d.text((18,y+7),txt,font=font,fill='white')
 if scenario=='instruction':
  try:
   ico=Image.open(source).convert('RGBA')
   im.paste(ico,(210,74),ico)
  except Exception:pass
 im.save(out/(scenario+'.png'))
print('Generated 4 accurately sized 256x192 wireframe previews; instruction uses original DS CallButton bitmap')
