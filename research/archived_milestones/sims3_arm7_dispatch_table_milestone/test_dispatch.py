import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyze_dispatch import decode,branch_target,SWITCH,TABLE,PC_BASE,COUNT
class Tests(unittest.TestCase):
 def test_bl_sign(self): self.assertEqual(branch_target(0xEBFFFFFE,0x1000),0x1000)
 def test_branch_to_helper(self):
  pc=0x0238CAD8;target=0x0238CA54; off=(target-(pc+8))//4
  self.assertEqual(branch_target(0xEB000000|(off&0xffffff),pc),target)
 def test_invalid_layout(self):
  with self.assertRaises(ValueError):decode(0x0238C000,b'\0'*0x1000)
 def test_valid_synthetic_table(self):
  base=0x0238C000; b=bytearray(0x2000)
  for addr,w in [(SWITCH+0x0c,0xE3500019),(SWITCH+0x20,0xE08F0080),(SWITCH+0x24,0xE1D000B4),(SWITCH+0x28,0xE08FF000)]:struct.pack_into('<I',b,addr-base,w)
  for i in range(COUNT):
   off=0x400+i*4;struct.pack_into('<H',b,TABLE+2*i-base,off);struct.pack_into('<I',b,PC_BASE+off-base,0xE1A00000)
  self.assertEqual(len(decode(base,b)),26)
 def test_reject_odd_target(self):
  base=0x0238C000;b=bytearray(0x2000)
  for addr,w in [(SWITCH+0x0c,0xE3500019),(SWITCH+0x20,0xE08F0080),(SWITCH+0x24,0xE1D000B4),(SWITCH+0x28,0xE08FF000)]:struct.pack_into('<I',b,addr-base,w)
  struct.pack_into('<H',b,TABLE-base,0x401)
  with self.assertRaises(ValueError):decode(base,b)
if __name__=='__main__':unittest.main()
