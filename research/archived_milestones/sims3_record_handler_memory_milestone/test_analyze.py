import sys, unittest, struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import analyze as a
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class TestRecords(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rom=ROM.read_bytes();cls.result=a.inspect(cls.rom)
 def test_five_paths(self):self.assertEqual(self.result['verified_write_paths'],5)
 def test_shared_targets(self):
  self.assertEqual([v['effective_address'] for v in self.result['paths'][:3]],['0x02ffffaa','0x02ffffac','0x02ffff94'])
 def test_timer_targets(self):
  self.assertEqual([v['effective_address'] for v in self.result['paths'][3:]],['0x0400010c','0x0400010e'])
 def test_literal_offsets(self):
  for x in a.PATHS:
   base=0x2380000;off=struct.unpack_from('<I',self.rom,0x30)[0]
   inst=struct.unpack_from('<I',self.rom,off+x['load']-base)[0]
   self.assertEqual(a.literal_addr(inst,x['load']),x['pool'])
 def test_reject_wrong_rom(self):
  with self.assertRaisesRegex(ValueError,'SHA'):a.inspect(self.rom[:-1])
 def test_reject_corrupt_store(self):
  raw=bytearray(self.rom);off=struct.unpack_from('<I',raw,0x30)[0]
  raw[off+(a.PATHS[0]['store']-a.BASE)]^=1
  with self.assertRaisesRegex(ValueError,'Unexpected store'):a.inspect(raw,False)
 def test_reject_corrupt_literal(self):
  raw=bytearray(self.rom);off=struct.unpack_from('<I',raw,0x30)[0]
  raw[off+(a.PATHS[0]['pool']-a.BASE)]^=1
  with self.assertRaisesRegex(ValueError,'Unexpected literal'):a.inspect(raw,False)
 def test_reject_corrupt_ldr(self):
  raw=bytearray(self.rom);off=struct.unpack_from('<I',raw,0x30)[0]
  raw[off+(a.PATHS[0]['load']-a.BASE)]^=1
  with self.assertRaisesRegex(ValueError,'Wrong literal reference'):a.inspect(raw,False)
 def test_reject_corrupt_data_source(self):
  raw=bytearray(self.rom);off=struct.unpack_from('<I',raw,0x30)[0]
  raw[off+(0x0238D9E8-a.BASE)]^=1
  with self.assertRaisesRegex(ValueError,'Bad selector/data opcode'):a.inspect(raw,False)
 def test_out_of_bounds(self):
  with self.assertRaises(ValueError):a.literal_addr(0,0x238D9EC)
if __name__=='__main__':unittest.main()
