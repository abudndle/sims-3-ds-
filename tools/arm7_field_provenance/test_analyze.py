import unittest, os, struct
from pathlib import Path
import analyze
class Decoder(unittest.TestCase):
 def test_bl_plus(self):self.assertEqual(analyze.branch_target(0xEB000116,0x0238E450),0x0238E8B0)
 def test_bl_other(self):self.assertEqual(analyze.branch_target(0xEB0000C1,0x0238E464),0x0238E770)
 def test_branch_conditional(self):self.assertEqual(analyze.branch_target(0x1A000004,0x0238E44C),0x0238E464)
 def test_reject_other(self):
  with self.assertRaises(ValueError):analyze.branch_target(0,0)
class WithROM(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not os.environ.get('SIMS3_DS_ROM'):raise unittest.SkipTest('SIMS3_DS_ROM unset')
  cls.rom=Path(os.environ['SIMS3_DS_ROM']).read_bytes()
 def test_valid(self):self.assertEqual(analyze.inspect(self.rom)['verified_instruction_sites'],len(analyze.INSTRUCTIONS))
 def test_bad_hash(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):analyze.inspect(self.rom[:-1])
 def test_corrupt_instruction(self):
  b=bytearray(self.rom);off=struct.unpack_from('<I',b,0x30)[0]
  b[off+0x0238E470-analyze.BASE]^=1
  with self.assertRaisesRegex(ValueError,'instruction mismatch'):analyze.inspect(b,False)
 def test_wrong_load_address(self):
  b=bytearray(self.rom);struct.pack_into('<I',b,0x38,0x02390000)
  with self.assertRaisesRegex(ValueError,'invalid ARM7 bounds'):analyze.inspect(b,False)
  # New regression test
  with self.assertRaisesRegex(ValueError,'invalid ARM7 load address'):analyze.inspect(b,True)
if __name__=='__main__':unittest.main()
