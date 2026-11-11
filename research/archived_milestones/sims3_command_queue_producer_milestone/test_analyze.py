import unittest,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import analyze,bl_target,ANCHORS,EDGES,EXPECTED_PRODUCER_CALLERS
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=ROM.read_bytes()
 def test_original_rom(self):self.assertEqual(len(analyze(self.data)['producer_callers']),13)
 def test_anchors(self):self.assertEqual(len(ANCHORS),29)
 def test_edges(self):self.assertEqual(len(EDGES),3)
 def test_derived_callers(self):self.assertEqual(len(EXPECTED_PRODUCER_CALLERS),13)
 def test_capacity(self):self.assertEqual(analyze(self.data)['queue']['ring_capacity_slots'],16)
 def test_max_count(self):self.assertEqual(analyze(self.data)['queue']['record_words_max'],4)
 def test_broken_sha(self):
  x=bytearray(self.data);x[-1]^=1
  with self.assertRaisesRegex(ValueError,'SHA'):analyze(x)
 def test_broken_anchor(self):
  x=bytearray(self.data);off=struct.unpack_from('<I',x,0x30)[0];x[off+0xc4c0]^=1
  with self.assertRaisesRegex(ValueError,'Instruction'):analyze(x,False)
 def test_broken_edge(self):
  x=bytearray(self.data);off=struct.unpack_from('<I',x,0x30)[0];x[off+0xc570]^=1
  with self.assertRaisesRegex(ValueError,'BL'):analyze(x,False)
 def test_bad_bounds(self):
  x=bytearray(self.data);struct.pack_into('<I',x,0x38,0)
  with self.assertRaisesRegex(ValueError,'bounds'):analyze(x,False)
 def test_non_branch(self):self.assertIsNone(bl_target(0xe1a00000,0x2380000))
if __name__=='__main__':unittest.main()
