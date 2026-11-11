import unittest,struct
from trace_callchain import decode_bl,arm9,callsites
class TestTrace(unittest.TestCase):
 def test_first_caller(self): self.assertEqual(decode_bl(0x02095CEA,0xF7FF,0xFF8F),(0x02095C0C,'BL'))
 def test_second_caller(self): self.assertEqual(decode_bl(0x020A2712,0xF7FE,0xFEE7),(0x020A14E4,'BL'))
 def test_reject_other(self): self.assertIsNone(decode_bl(0x02000000,0x4800,0xBD08))
 def test_bounds(self):
  b=bytearray(0x400);struct.pack_into('<IIII',b,0x20,0x200,0x02004000,0x02004000,0x100)
  self.assertEqual(arm9(b)[0],0x02004000)
  struct.pack_into('<I',b,0x2c,0x300)
  with self.assertRaises(ValueError):arm9(b)
 def test_scanner(self):
  a=struct.pack('<HH',0xF7FF,0xFF8F)
  self.assertEqual(callsites(0x02095CEA,a,{0x02095C0C})[0x02095C0C][0]['address'],0x02095CEA)
if __name__=='__main__':unittest.main()
