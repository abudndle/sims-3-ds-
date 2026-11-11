import os,subprocess,time,json,sys
from Xlib import display,X,XK
from Xlib.ext import xtest
from PIL import Image
out='/mnt/data/sims3_camera_tutorial_milestone'
rom='/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds'
exe='/mnt/data/melonds_test/squashfs-root/AppRun'
env=os.environ.copy();env.update({'DISPLAY':':88','LIBGL_ALWAYS_SOFTWARE':'1','QT_QPA_PLATFORM':'xcb','QT_X11_NO_MITSHM':'1','HOME':'/home/oai'})
env['XAUTHORITY']='/tmp/sims3-empty-Xauthority'
os.environ['XAUTHORITY']='/tmp/sims3-empty-Xauthority'
log=open(out+'/emulator.log','w')
p=subprocess.Popen([exe,rom],stdout=log,stderr=subprocess.STDOUT,env=env)
d=display.Display(':88')

def shot(name):
 path=f'{out}/{name}.png'
 subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-f','x11grab','-video_size','512x440','-i',':88+0,0','-frames:v','1','-y',path],timeout=12)
 print('SHOT',name,os.path.getsize(path),flush=True)
def click(x,y):
 xtest.fake_input(d,X.MotionNotify,x=x,y=y);d.sync();time.sleep(.18);xtest.fake_input(d,X.ButtonPress,1);d.sync();time.sleep(.17);xtest.fake_input(d,X.ButtonRelease,1);d.sync()
def key(symbol):
 kc=d.keysym_to_keycode(XK.string_to_keysym(symbol));print('KEY',symbol,kc,flush=True)
 xtest.fake_input(d,X.KeyPress,kc);d.sync();time.sleep(.35);xtest.fake_input(d,X.KeyRelease,kc);d.sync()
print('PID',p.pid,flush=True)
try:
 time.sleep(53);shot('title')
 click(127,394);time.sleep(5);shot('profile')
 click(56,301);time.sleep(3);shot('profile_selected')
 click(220,353);time.sleep(5);shot('after_confirm')
 click(110,325);time.sleep(6);shot('tutorial')
 click(210,345);time.sleep(3);shot('controls_x_prompt')
 key('x');time.sleep(3);shot('after_x')
 key('b');time.sleep(3);shot('after_b')
 for i in range(3):
  click(215,345);time.sleep(2);shot('advance_'+str(i))
 print('DONE',flush=True)
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except: p.kill()
 log.close()
