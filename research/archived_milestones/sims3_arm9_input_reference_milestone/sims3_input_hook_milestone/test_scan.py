import struct,unittest
from scan_input import scan
class ScannerTests(unittest.TestCase):
 def fake(self):
  rom=bytearray(0x400)
  struct.pack_into('<III',rom,0x20,0x200,0x02004000,0x200)
  return rom
 def test_keyinput_reference(self):
  r=self.fake();struct.pack_into('<I',r,0x220,0xE59F0000);struct.pack_into('<I',r,0x228,0x04000130)
  o=scan(r);self.assertEqual(o['references'][0]['register'],'KEYINPUT');self.assertEqual(o['references'][0]['instruction'],'0x02004020')
 def test_nonmatching_literal(self):
  r=self.fake();struct.pack_into('<I',r,0x228,0x04000130)
  self.assertEqual(scan(r)['references'],[])
 def test_oob_literal(self):
  r=self.fake();struct.pack_into('<I',r,0x3fc,0xE59F0FFF)
  self.assertEqual(scan(r)['references'],[])
 def test_bad_header(self):
  with self.assertRaises(ValueError):scan(b'hello')
 def test_negative_offset(self):
  r=self.fake();struct.pack_into('<I',r,0x240,0xE51F000C);struct.pack_into('<I',r,0x23c,0x04000180)
  self.assertEqual(scan(r)['references'][0]['register'],'IPCSYNC')
if __name__=='__main__':unittest.main()
