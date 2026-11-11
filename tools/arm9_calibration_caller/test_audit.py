import os,struct,unittest
from pathlib import Path
import audit
class Decode(unittest.TestCase):
 def test_call(self):self.assertEqual(audit.branch_target(0xEB000084,0x020D7924),0x020D7B3C)
 def test_wrapper_pre(self):self.assertEqual(audit.branch_target(0xEB0000C4,0x020D7940),0x020D7C58)
 def test_wrapper_sample(self):self.assertEqual(audit.branch_target(0xEBFFFFE6,0x020D7948),0x020D78E8)
 def test_literal(self):self.assertEqual(audit.literal_target(0xE59F203C,0x020D78EC),0x020D7930)
 def test_bad_branch(self):
  with self.assertRaises(ValueError):audit.branch_target(0,0)
 def test_bad_literal(self):
  with self.assertRaises(ValueError):audit.literal_target(0,0)
 def test_bad_word(self):
  with self.assertRaises(ValueError):audit.u32(b"123",0)
class ROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not os.getenv("SIMS3_DS_ROM"):raise unittest.SkipTest("Original ROM not in public CI")
  cls.rom=Path(os.environ["SIMS3_DS_ROM"]).read_bytes()
 def test_original(self):
  self.assertEqual(audit.inspect(self.rom)["verified_sites"],len(audit.ANCHORS))
 def test_hash(self):
  with self.assertRaisesRegex(ValueError,"SHA256"):audit.inspect(self.rom[:-1])
 def changed(self,addr):
  raw=bytearray(self.rom);off,base=(struct.unpack_from("<I",raw,p)[0] for p in (0x20,0x28))
  raw[off+addr-base]^=1
  return raw
 def test_bad_copy(self):
  with self.assertRaisesRegex(ValueError,"instruction"):audit.inspect(self.changed(0x020D7910),False)
 def test_bad_call(self):
  with self.assertRaisesRegex(ValueError,"instruction"):audit.inspect(self.changed(0x020D7924),False)
 def test_bad_flag(self):
  with self.assertRaisesRegex(ValueError,"instruction"):audit.inspect(self.changed(0x020D78F4),False)
 def test_bad_pointer(self):
  with self.assertRaisesRegex(ValueError,"instruction"):audit.inspect(self.changed(0x020D7930),False)
if __name__=="__main__":unittest.main()
