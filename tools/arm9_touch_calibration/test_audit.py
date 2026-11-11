import os,struct,unittest
from pathlib import Path
import audit
class Helpers(unittest.TestCase):
 def test_input_literal(self):self.assertEqual(audit.literal_address(0xE59F2108,0x020D7B40),0x020D7C50)
 def test_calibration_literal(self):self.assertEqual(audit.literal_address(0xE59F20D0,0x020D7B7C),0x020D7C54)
 def test_bypass_branch(self):self.assertEqual(audit.branch_target(0x1A000008,0x020D7B4C),0x020D7B74)
 def test_nonload(self):
  with self.assertRaises(ValueError):audit.literal_address(0,0)
 def test_nonbranch(self):
  with self.assertRaises(ValueError):audit.branch_target(0,0)
 def test_clamps(self):
  self.assertEqual(audit.clamp_screen(-50,500),(0,191))
  self.assertEqual(audit.clamp_screen(500,-50),(255,0))
  self.assertEqual(audit.clamp_screen(101,90),(101,90))
 def test_bad_clamp_type(self):
  with self.assertRaises(ValueError):audit.clamp_screen(1.5,100)
class OriginalROM(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not os.getenv('SIMS3_DS_ROM'):raise unittest.SkipTest('Original ROM not available')
  cls.rom=Path(os.environ['SIMS3_DS_ROM']).read_bytes()
 def test_verified(self):
  r=audit.inspect(self.rom)
  self.assertEqual(r['verified_anchor_sites'],len(audit.ANCHORS))
  self.assertEqual(r['output_limits']['y'],[0,191])
 def test_wrong_hash(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):audit.inspect(self.rom[:-1])
 def mutated(self,addr):
  b=bytearray(self.rom)
  off,base=(struct.unpack_from('<I',b,p)[0] for p in (0x20,0x28))
  b[off+addr-base]^=1
  return b
 def test_bad_x_clamp(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutated(0x020D7BE8),False)
 def test_bad_y_clamp(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutated(0x020D7C40),False)
 def test_bad_calibration_literal(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutated(0x020D7C54),False)
 def test_bad_state_literal(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutated(0x020D7C50),False)
if __name__=='__main__':unittest.main()
