import unittest,struct
from scan_handoff import scan_image,images
class ScannerTests(unittest.TestCase):
 def test_thumb_literal(self):
  buf=bytearray(64);struct.pack_into('<H',buf,0,0x4800);struct.pack_into('<I',buf,4,0x02FFFFA8)
  result=scan_image('TEST',0x02004000,buf)
  self.assertTrue(any(r['instruction_address']=='0x02004000' and r['literal_value']=='0x02FFFFA8' for r in result))
 def test_out_of_bounds_ignored(self):
  buf=bytearray(4);struct.pack_into('<H',buf,0,0x48ff)
  self.assertEqual(scan_image('TEST',0x02004000,buf),[])
 def test_non_candidate_ignored(self):
  buf=bytearray(64);struct.pack_into('<H',buf,0,0x4800);struct.pack_into('<I',buf,4,0xDEADBEEF)
  self.assertEqual(scan_image('TEST',0x02004000,buf),[])
 def test_arm_literal(self):
  buf=bytearray(32);struct.pack_into('<I',buf,0,0xE59F0000);struct.pack_into('<I',buf,8,0x02FFFF98)
  self.assertTrue(any(r['mode']=='arm_ldr_literal' for r in scan_image('TEST',0x02004000,buf)))
 def test_invalid_header(self):
  with self.assertRaises(Exception):list(images(bytes(80)))
if __name__=='__main__':unittest.main()
