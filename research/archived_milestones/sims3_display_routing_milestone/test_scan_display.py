import tempfile,struct,unittest
from pathlib import Path
from scan_display import scan
class ScanTests(unittest.TestCase):
 def test_arm_literal_load(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fixture.nds';rom=bytearray(0x400)
   struct.pack_into('<IIII',rom,0x20,0x200,0x02000000,0x02000000,0x100)
   struct.pack_into('<I',rom,0x200,0xE59F0000) # LDR r0,[pc,#0]
   struct.pack_into('<I',rom,0x208,0x04000304) # literal at pc+8
   p.write_bytes(rom)
   r=scan(p)
   self.assertEqual(len(r['candidate_arm_instructions']),1)
   self.assertEqual(r['candidate_arm_instructions'][0]['arm9_instruction'],'0x02000000')
 def test_out_of_bounds(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'bad.nds';rom=bytearray(0x200)
   struct.pack_into('<IIII',rom,0x20,0x400,0,0,0x100)
   p.write_bytes(rom)
   with self.assertRaises(ValueError):scan(p)
if __name__=='__main__':unittest.main()
