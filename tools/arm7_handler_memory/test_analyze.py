"""Regression tests for ARM7 memory references. Set SIMS3_DS_ROM to run ROM-dependent checks."""
import os, struct, unittest
from pathlib import Path
import analyze as a

class TestRecords(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.environ.get("SIMS3_DS_ROM")
  if not path: raise unittest.SkipTest("SIMS3_DS_ROM not set; copyrighted ROM must be supplied locally")
  cls.rom=Path(path).read_bytes()
  cls.result=a.inspect(cls.rom)
 def test_five_paths(self): self.assertEqual(self.result['verified_write_paths'],5)
 def test_shared_targets(self):
  self.assertEqual([v['effective_address'] for v in self.result['paths'][:3]],['0x02ffffaa','0x02ffffac','0x02ffff94'])
 def test_timer_targets(self):
  self.assertEqual([v['effective_address'] for v in self.result['paths'][3:]],['0x0400010c','0x0400010e'])
 def test_literal_offsets(self):
  off=struct.unpack_from('<I',self.rom,0x30)[0]
  for x in a.PATHS:
   inst=struct.unpack_from('<I',self.rom,off+x['load']-a.BASE)[0]
   self.assertEqual(a.literal_addr(inst,x['load']),x['pool'])
 def test_reject_wrong_rom(self):
  with self.assertRaisesRegex(ValueError,'SHA'):a.inspect(self.rom[:-1])
 def _mutate(self,where):
  raw=bytearray(self.rom);off=struct.unpack_from('<I',raw,0x30)[0]
  raw[off+where-a.BASE]^=1
  return raw
 def test_reject_corrupt_store(self):
  with self.assertRaisesRegex(ValueError,'Unexpected store'):a.inspect(self._mutate(a.PATHS[0]['store']),False)
 def test_reject_corrupt_literal(self):
  with self.assertRaisesRegex(ValueError,'Unexpected literal'):a.inspect(self._mutate(a.PATHS[0]['pool']),False)
 def test_reject_corrupt_ldr(self):
  with self.assertRaisesRegex(ValueError,'Wrong literal reference'):a.inspect(self._mutate(a.PATHS[0]['load']),False)
 def test_reject_corrupt_data_source(self):
  with self.assertRaisesRegex(ValueError,'Bad selector/data opcode'):a.inspect(self._mutate(0x0238D9E8),False)
 def test_out_of_bounds(self):
  with self.assertRaises(ValueError):a.literal_addr(0,0x238D9EC)

class TestDecoderWithoutROM(unittest.TestCase):
 def test_literal_bad_opcode(self):
  with self.assertRaises(ValueError):a.literal_addr(0,0x238D9EC)
 def test_pc_relative_positive(self):
  self.assertEqual(a.literal_addr(0xE59F0004,0x1000),0x100C)

if __name__=='__main__':unittest.main()
