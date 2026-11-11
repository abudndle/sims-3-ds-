import unittest,struct
from scan_spi import scan,group,extract_arm7
class Tests(unittest.TestCase):
 def test_positive_literal(self):
  x=bytearray(32);struct.pack_into('<I',x,0,0xE59F0000);struct.pack_into('<I',x,8,0x040001C0)
  self.assertEqual(scan(0x02380000,x)[0]['hardware'],'SPICNT')
 def test_negative_literal(self):
  x=bytearray(32);struct.pack_into('<I',x,12,0xE51F100C);struct.pack_into('<I',x,8,0x040001C2)
  self.assertTrue(any(r['hardware']=='SPIDATA' for r in scan(0x02380000,x)))
 def test_reject_store(self):
  x=bytearray(32);struct.pack_into('<I',x,0,0xE58F0000);struct.pack_into('<I',x,8,0x040001C0)
  self.assertEqual(scan(0x02380000,x),[])
 def test_group(self):
  r=[{'instruction':'0x02380000','hardware':'SPICNT'},{'instruction':'0x02380040','hardware':'SPIDATA'},{'instruction':'0x02380200','hardware':'SPIDATA'}]
  self.assertEqual(len(group(r)),2);self.assertTrue(group(r)[0]['both_spi_registers'])
 def test_bad_header(self):
  with self.assertRaises(Exception):extract_arm7(bytes(128))
if __name__=='__main__':unittest.main()
