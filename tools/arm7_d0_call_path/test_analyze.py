import os,struct,unittest
from pathlib import Path
import analyze
class Decoder(unittest.TestCase):
 def test_branch_conditional(self):self.assertEqual(analyze.branch_target(0x9A000006,0x02399858),0x02399878)
 def test_branch_unconditional(self):self.assertEqual(analyze.branch_target(0xEA000007,0x02399874),0x02399898)
 def test_branch_external(self):self.assertEqual(analyze.branch_target(0xEB205B91,0x02399898),0x02BB06E4)
 def test_literal_r0(self):self.assertEqual(analyze.literal_target(0xE59F005C,0x0239985C),0x023998C0)
 def test_literal_r3(self):self.assertEqual(analyze.literal_target(0xE59F3054,0x02399868),0x023998C4)
 def test_bad_branch(self):
  with self.assertRaises(ValueError):analyze.branch_target(0,0)
 def test_bad_literal(self):
  with self.assertRaises(ValueError):analyze.literal_target(0,0)
class WithROM(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not os.getenv("SIMS3_DS_ROM"):raise unittest.SkipTest("SIMS3_DS_ROM not set")
  cls.rom=Path(os.environ["SIMS3_DS_ROM"]).read_bytes()
 def test_valid(self):
  r=analyze.inspect(self.rom);self.assertEqual(r["verified_sites"],len(analyze.ANCHORS));self.assertEqual(r["r2"],"0x107")
 def test_sha_guard(self):
  with self.assertRaisesRegex(ValueError,"SHA"):analyze.inspect(self.rom[:-1])
 def modified(self,addr):
  b=bytearray(self.rom);off=struct.unpack_from("<I",b,0x30)[0];b[off+addr-analyze.BASE]^=1;return b
 def test_corrupt_immediate(self):
  with self.assertRaisesRegex(ValueError,"mismatch"):analyze.inspect(self.modified(0x02399860),False)
 def test_corrupt_branch(self):
  with self.assertRaisesRegex(ValueError,"mismatch"):analyze.inspect(self.modified(0x02399898),False)
 def test_corrupt_literal(self):
  with self.assertRaisesRegex(ValueError,"mismatch"):analyze.inspect(self.modified(0x023998C0),False)
if __name__=="__main__":unittest.main()
