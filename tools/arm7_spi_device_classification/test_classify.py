import os,struct,unittest
from pathlib import Path
import classify
class UnitTests(unittest.TestCase):
 def test_firmware(self):self.assertEqual(classify.spi_device(0x8900),1)
 def test_touch(self):self.assertEqual(classify.spi_device(0x8202),2)
 def test_d8(self):self.assertEqual(classify.decode_mov_imm(0xe3a020d8),0xd8)
 def test_8900(self):self.assertEqual(classify.decode_mov_imm(0xe3a02c89),0x8900)
 def test_literal(self):self.assertEqual(classify.decode_arm_literal(0xe59f1044,0x02393a8c),0x02393ad8)
 def test_bad_literal(self):
  with self.assertRaises(ValueError):classify.decode_arm_literal(0,0)
class ROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not os.getenv('SIMS3_DS_ROM'):raise unittest.SkipTest('provide original ROM with SIMS3_DS_ROM')
  cls.rom=Path(os.environ['SIMS3_DS_ROM']).read_bytes()
 def test_original(self):
  r=classify.inspect(self.rom);self.assertEqual(r['verified_sites'],7);self.assertEqual(r['spi_device_select'],1)
 def test_wrong_sha(self):
  with self.assertRaisesRegex(ValueError,'hash'):classify.inspect(self.rom[:-1])
 def test_corrupt_chip_select(self):
  r=bytearray(self.rom);off=struct.unpack_from('<I',r,0x30)[0]
  r[off+0x02393a90-classify.BASE]^=1
  with self.assertRaisesRegex(ValueError,'mismatch'):classify.inspect(r,False)
 def test_corrupt_transfer(self):
  r=bytearray(self.rom);off=struct.unpack_from('<I',r,0x30)[0]
  r[off+0x02393a9c-classify.BASE]^=1
  with self.assertRaisesRegex(ValueError,'mismatch'):classify.inspect(r,False)
if __name__=='__main__':unittest.main()
