import unittest,struct
from trace_touch_spi import extract_arm7,ldr_literal,strh_regs,trace
class Tests(unittest.TestCase):
 def test_arm7_bounds(self):
  raw=bytearray(1024);struct.pack_into('<IIII',raw,0x30,0x200,0x2380000,0x2380000,32)
  self.assertEqual(len(extract_arm7(raw)[1]),32)
 def test_reject_invalid_bounds(self):
  raw=bytearray(1024);struct.pack_into('<IIII',raw,0x30,0x400,0x2380000,0x2380000,0x1000)
  with self.assertRaises(ValueError):extract_arm7(raw)
 def test_literal_load(self):
  b=bytearray(24);struct.pack_into('<I',b,0,0xe59f4000);struct.pack_into('<I',b,8,0x8202)
  self.assertEqual(ldr_literal(b,0x2380000,0x2380000)['value'],0x8202)
 def test_strh_registers(self):
  self.assertEqual(strh_regs(0xe1c540b0),(5,4))
  self.assertIsNone(strh_regs(0xe1d540b0))
 def test_real_sequences(self):
  from pathlib import Path
  rom=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
  if not rom.exists():self.skipTest('ROM not mounted')
  rows=trace(rom.read_bytes())['touch_device_configurations']
  self.assertEqual([r['spi_write'] for r in rows],['0x0238C9F8','0x0238CA70'])
  self.assertTrue(all(r['device']==2 and r['enabled'] for r in rows))
if __name__=='__main__':unittest.main()
