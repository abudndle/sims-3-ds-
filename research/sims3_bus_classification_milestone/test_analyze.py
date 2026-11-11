import unittest,struct
from analyze import bl_target,literal_target,word,run,BASE
class Tests(unittest.TestCase):
 def test_word(self):self.assertEqual(word(struct.pack('<I',0x12345678),BASE),0x12345678)
 def test_bounds(self):
  with self.assertRaises(ValueError):word(b'abc',BASE)
 def test_branch(self):self.assertEqual(bl_target(0x0238FA6C,0xEBFFFFC1),0x0238F978)
 def test_reject_nonbranch(self):
  with self.assertRaises(ValueError):bl_target(BASE,0)
 def test_literal(self):
  # LDR r0,[pc,#0] followed by 0x040001A0
  data=struct.pack('<III',0xE59F0000,0,0x040001A0)
  self.assertEqual(literal_target(data,BASE),(BASE+8,0x040001A0))
 def test_reject_literal(self):
  with self.assertRaises(ValueError):literal_target(struct.pack('<I',0),BASE)
 def test_wrong_rom(self):
  import tempfile,pathlib
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'fake.nds';p.write_bytes(b'abc')
   with self.assertRaises(ValueError):run(p)
if __name__=='__main__':unittest.main()
