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
class ProducerTests(unittest.TestCase):
 def setUp(self):
  self.words = {**analyze.ARM7, **analyze.ARM7_PRODUCER}

 def test_axes_follow_spi_commands_and_packing(self):
  axes = analyze.inspect_arm7(self.words.__getitem__)["axes"]
  self.assertEqual((axes["x"]["command"], axes["x"]["bits"]), ("0xd1", [0, 11]))
  self.assertEqual((axes["y"]["command"], axes["y"]["bits"]), ("0x91", [12, 23]))

 def test_changed_provenance_is_rejected(self):
  changes = {
   0x0238DCC0: 0x03A09091,  # X selector changed to Y
   0x0238DE84: 0x040001A2,  # SPI data literal changed to game-card interface
   0x0238DF40: 0xE3A02000,  # Both calls select X
   0x0238DF84: 0xE1802221,  # Y is shifted into the wrong bit position
   0x0238D9F4: 0xE1DD00B8,  # Both shared writes read the low half
  }
  for address, replacement in changes.items():
   with self.subTest(address=hex(address)):
    words = {**self.words, address: replacement}
    with self.assertRaisesRegex(ValueError, hex(address)):
     analyze.inspect_arm7(words.__getitem__)

class ROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.getenv("SIMS3_DS_ROM")
  if not path:raise unittest.SkipTest("Provide original ROM via SIMS3_DS_ROM")
  cls.rom=Path(path).read_bytes()
 def test_original(self):self.assertEqual(analyze.inspect(self.rom)["verified_sites"],len(analyze.ARM9)+len(analyze.ARM7)+len(analyze.ARM7_PRODUCER))
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
