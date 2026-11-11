import unittest,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import analyze,SHA,BASE,ANCHORS,CALLS,bl_target
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class TestAnalysis(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rom=ROM.read_bytes();cls.report=analyze(cls.rom)
 def test_hash(self):self.assertEqual(self.report['rom_sha256'],SHA)
 def test_anchor_count(self):self.assertEqual(self.report['anchor_count'],len(ANCHORS))
 def test_branch_count(self):self.assertEqual(self.report['branch_count'],5)
 def test_paths(self):self.assertEqual(len(self.report['proven_chains']),3)
 def test_case_24(self):self.assertEqual(self.report['dispatcher']['read_case_24']['argument'],'r8')
 def test_case_25(self):self.assertEqual(self.report['dispatcher']['send_case_25']['payload'],'r8 & 0xFF')
 def test_selector_limit(self):self.assertEqual(self.report['dispatcher']['max_selector'],25)
 def test_reject_wrong_rom(self):
  b=bytearray(self.rom);b[0x100]^=1
  with self.assertRaises(ValueError):analyze(b)
 def test_reject_modified_opcode_without_hash_guard(self):
  b=bytearray(self.rom);off=struct.unpack_from('<I',b,0x30)[0];struct.pack_into('<I',b,off+0xC8C0,0)
  with self.assertRaisesRegex(ValueError,'Opcode mismatch'):analyze(b,strict=False)
 def test_reject_modified_branch_without_hash_guard(self):
  b=bytearray(self.rom);off=struct.unpack_from('<I',b,0x30)[0];struct.pack_into('<I',b,off+0xC904,0)
  with self.assertRaisesRegex(ValueError,'Branch mismatch'):analyze(b,strict=False)
 def test_bl_target(self):self.assertEqual(bl_target(0xEB000085,0x0238C904),0x0238CB20)
if __name__=='__main__':unittest.main()
