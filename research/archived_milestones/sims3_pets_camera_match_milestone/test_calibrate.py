import unittest,tempfile,pathlib
from calibrate_camera import analyze,write_header
class Tests(unittest.TestCase):
 def test_measured_ratio(self):
  rows=[{'game':g,'axis':a,'duration_seconds':'2','delta':str(v)} for a in ('pan','yaw','zoom') for g,v in [('ds',10),('pets3ds',15)]]
  r=analyze(rows)
  self.assertEqual(r['pan']['ds_to_pets_multiplier'],1.5)
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'match.h';write_header(r,p)
   self.assertIn('98304u',p.read_text())
 def test_missing_baseline(self):
  with self.assertRaises(ValueError): analyze([])
 def test_bad_timestamp(self):
  with self.assertRaises(ValueError): analyze([{'game':'ds','axis':'pan','duration_seconds':'0','delta':'1'}])
if __name__=='__main__':unittest.main()
