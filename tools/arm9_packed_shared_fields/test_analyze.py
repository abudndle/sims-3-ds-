import os,struct,unittest
from pathlib import Path
import analyze
class PureTests(unittest.TestCase):
 def test_fields(self):self.assertEqual(analyze.fields((0xa5<<24)|(0x789<<12)|0x123),{"field0":0x123,"field1":0x789,"upper8":0xa5})
 def test_max(self):self.assertEqual(analyze.fields(0xffffffff)["field1"],4095)
 def test_invalid(self):
  with self.assertRaises(ValueError):analyze.fields(-1)
 def test_arm9_first(self):self.assertEqual(analyze.literal_target(0xe59f11dc,0x020d7418),0x020d75fc)
 def test_arm9_second(self):self.assertEqual(analyze.literal_target(0xe59f1108,0x020d74ec),0x020d75fc)
 def test_arm7(self):self.assertEqual(analyze.literal_target(0xe59f1138,0x0238d9ec),0x0238db2c)
 def test_non_ldr(self):
  with self.assertRaises(ValueError):analyze.literal_target(0,0)
class ROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.getenv("SIMS3_DS_ROM")
  if not path:raise unittest.SkipTest("Provide original ROM via SIMS3_DS_ROM")
  cls.rom=Path(path).read_bytes()
 def test_original(self):self.assertEqual(analyze.inspect(self.rom)["verified_sites"],len(analyze.ARM9)+len(analyze.ARM7))
 def test_wrong_hash(self):
  with self.assertRaisesRegex(ValueError,"SHA-256"):analyze.inspect(self.rom[:-1])
 def changed(self,header,address):
  raw=bytearray(self.rom);offset=struct.unpack_from("<I",raw,header)[0];base=struct.unpack_from("<I",raw,header+8)[0]
  raw[offset+address-base]^=1;return raw
 def test_bad_arm9(self):
  with self.assertRaisesRegex(ValueError,"ARM9 instruction"):analyze.inspect(self.changed(0x20,0x020d7420),False)
 def test_bad_arm7(self):
  with self.assertRaisesRegex(ValueError,"ARM7 instruction"):analyze.inspect(self.changed(0x30,0x0238d9f8),False)
 def test_bad_literal(self):
  with self.assertRaisesRegex(ValueError,"ARM9 instruction"):analyze.inspect(self.changed(0x20,0x020d75fc),False)
if __name__=="__main__":unittest.main()
