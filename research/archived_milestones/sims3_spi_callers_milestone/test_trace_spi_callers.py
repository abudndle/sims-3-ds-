import unittest,struct
from trace_spi_callers import arm7,bl_target,scan
class TestSpiCallers(unittest.TestCase):
 def test_arm_bl_forward(self):self.assertEqual(bl_target(0xEB000009,0x0238CA04),0x0238CA30)
 def test_arm_bl_backward(self):self.assertEqual(bl_target(0xEBFFFFDD,0x0238CAD8),0x0238CA54)
 def test_reject_branch_without_link(self):self.assertIsNone(bl_target(0xEAFFFFDD,0x0238CAD8))
 def test_invalid_header(self):
  with self.assertRaises(ValueError):arm7(bytes(0x200))
 def test_real_rom(self):
  from pathlib import Path
  p=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
  if not p.exists():self.skipTest('ROM unavailable')
  d=scan(p.read_bytes())
  self.assertEqual(d['total_edges'],23)
  self.assertEqual([r['direct_arm_bl_callers'] for r in d['functions']],[4,8,4,4,3])
if __name__=='__main__':unittest.main()
