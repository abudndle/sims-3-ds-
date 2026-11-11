import unittest,struct
from trace import thumb_call,load_arm9
class Tests(unittest.TestCase):
 def test_bl_forward(self):self.assertEqual(thumb_call(0x02095CEA,0xF7FF,0xFF8F),(0x02095C0C,'BL'))
 def test_second_bl(self):self.assertEqual(thumb_call(0x020A2712,0xF7FE,0xFEE7),(0x020A14E4,'BL'))
 def test_noncall(self):self.assertIsNone(thumb_call(0x2000000,0x4800,0xBD08))
 def test_valid_header(self):
  b=bytearray(0x400);struct.pack_into('<IIII',b,0x20,0x200,0x02004010,0x02004000,0x100)
  self.assertEqual(load_arm9(b)[0],0x02004000)
 def test_invalid_header(self):
  b=bytearray(0x400);struct.pack_into('<IIII',b,0x20,0x200,0x02004010,0x02004000,0x500)
  with self.assertRaises(ValueError):load_arm9(b)
if __name__=='__main__':unittest.main()
