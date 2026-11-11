import unittest,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import classify,SITES,bl_target,BASE
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class AnalyzerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rom=ROM.read_bytes();cls.off=struct.unpack_from('<I',cls.rom,0x30)[0]
 def mutate(cls,addr):
  data=bytearray(cls.rom);pos=cls.off+(addr-BASE);data[pos]^=1;return bytes(data)
 def test_total(self):self.assertEqual(classify(self.rom)['total_call_sites'],13)
 def test_groups(self):self.assertEqual(classify(self.rom)['record_type_counts'],{'0':4,'2':4,'3':5})
 def test_sites_have_unique_setup(self):self.assertEqual(len({x[0] for x in SITES.values()}),13)
 def test_first_branch(self):self.assertEqual(bl_target(0xebffff4d,0x0238C784),0x0238C4C0)
 def test_non_call(self):self.assertIsNone(bl_target(0xe3a00003,0x0238C778))
 def test_instruction_mutation(self):
  with self.assertRaisesRegex(ValueError,'setup'):classify(self.mutate(0x0238C778),False)
 def test_branch_mutation(self):
  with self.assertRaisesRegex(ValueError,'branch'):classify(self.mutate(0x0238C784),False)
 def test_hash_rejection(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):classify(self.mutate(0x0238C778))
 def test_known_types(self):self.assertEqual(set(x['record_type'] for x in classify(self.rom)['sites']),{0,2,3})
if __name__=='__main__':unittest.main()
