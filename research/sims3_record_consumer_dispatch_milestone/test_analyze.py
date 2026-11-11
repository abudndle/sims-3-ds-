import sys,unittest,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import *
ROM=Path(os.environ.get('SIMS3_ROM','/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds'))
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=ROM.read_bytes();cls.offset=u32(cls.data,0x30)
 def test_original(self):self.assertEqual(inspect(self.data)['verified_opcode_anchors'],19)
 def test_type2(self):self.assertEqual(inspect(self.data)['type_2_secondary_selectors'],[64,65,66])
 def test_type0(self):self.assertEqual(inspect(self.data)['type_0_secondary_selectors'],[0,1,2,16])
 def test_jump_table(self):self.assertEqual(inspect(self.data)['record_type_jump_table']['2'],'0x0238C5FC')
 def test_anomalous_type1(self):self.assertFalse(inspect(self.data)['type_1_branch_within_arm7'])
 def test_bad_opcode(self):
  b=bytearray(self.data);b[self.offset+0xe3e8]^=1
  with self.assertRaisesRegex(ValueError,'Unexpected opcode'):inspect(b,False)
 def test_bad_branch(self):
  b=bytearray(self.data);b[self.offset+0xc5fc]^=1
  with self.assertRaisesRegex(ValueError,'Unexpected opcode'):inspect(b,False)
 def test_bad_table(self):
  b=bytearray(self.data);b[self.offset+0xc5ec]^=2
  with self.assertRaisesRegex(ValueError,'jump table mismatch'):inspect(b,False)
 def test_bad_sha(self):
  b=bytearray(self.data);b[-1]^=1
  with self.assertRaisesRegex(ValueError,'SHA-256'):inspect(b)
if __name__=='__main__':unittest.main()
