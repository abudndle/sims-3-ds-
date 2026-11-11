import unittest,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import analyze,bl_target,SITES,SOURCES
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.rom=ROM.read_bytes();cls.off=struct.unpack_from('<I',cls.rom,0x30)[0]
 def tamper(self,addr):
  b=bytearray(self.rom);b[self.off+addr-0x02380000]^=1;return b
 def test_rom_and_count(self):
  r=analyze(self.rom);self.assertEqual(r['count'],12)
 def test_fixed_commands(self):
  d={x['callsite']:x['transmitted_command'] for x in analyze(self.rom)['calls']}
  for addr,code in [(0x0238CCF0,0x80),(0x0238CD34,0x82),(0x0238CD9C,0x83),(0x0238CE00,0x83),(0x0238D224,0x80),(0x0238D31C,0)]:self.assertEqual(d[f'0x{addr:08X}'],code)
 def test_dynamic_unresolved(self):
  r=analyze(self.rom)['calls'];self.assertEqual(sum(x['transmitted_command'] is None for x in r),6)
 def test_wrong_rom_rejected(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):analyze(self.tamper(0x0238CCEC))
 def test_bad_arg_opcode_rejected(self):
  with self.assertRaisesRegex(ValueError,'Argument opcode'):analyze(self.tamper(0x0238CCEC),False)
 def test_bad_bl_rejected(self):
  with self.assertRaisesRegex(ValueError,'Call target'):analyze(self.tamper(0x0238CCF0),False)
 def test_bad_dispatch_constant_rejected(self):
  with self.assertRaisesRegex(ValueError,'Anchor opcode'):analyze(self.tamper(0x0238CB30),False)
 def test_bad_helper_instruction_rejected(self):
  with self.assertRaisesRegex(ValueError,'Anchor opcode'):analyze(self.tamper(0x0238CA6C),False)
 def test_bl_decoder(self):
  self.assertIsNone(bl_target(0xE1A00000,0x0238CCF0));self.assertEqual(bl_target(0xEB000000,0x1000),0x1008)
if __name__=='__main__':unittest.main()
