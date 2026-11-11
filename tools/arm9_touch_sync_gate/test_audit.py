import os,struct,unittest
from pathlib import Path
import audit
class PureTests(unittest.TestCase):
 def test_first_caller(self):self.assertEqual(audit.branch_target(0xEB0000EB,0x020D78A4),0x020D7C58)
 def test_second_caller(self):self.assertEqual(audit.branch_target(0xEB0000C4,0x020D7940),0x020D7C58)
 def test_retry_branch(self):self.assertEqual(audit.branch_target(0x1AFFFFFC,0x020D7C64),0x020D7C5C)
 def test_pc_load(self):self.assertEqual(audit.literal_target(0xE59F100C,0x020D7C58),0x020D7C6C)
 def test_reject_nonbranch(self):
  with self.assertRaises(ValueError):audit.branch_target(0,0)
 def test_reject_nonliteral(self):
  with self.assertRaises(ValueError):audit.literal_target(0,0)
 def test_reject_short_word(self):
  with self.assertRaises(ValueError):audit.u32(b'123',0)
class OriginalROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.getenv('SIMS3_DS_ROM')
  if not path:raise unittest.SkipTest('Original ROM unavailable in public CI')
  cls.rom=Path(path).read_bytes()
 def test_original(self):
  r=audit.inspect(self.rom)
  self.assertEqual(r['call_sites'],['0x20d78a4','0x20d7940'])
 def test_hash_check(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):audit.inspect(self.rom[:-1])
 def mutation(self,addr):
  b=bytearray(self.rom);off,base=(struct.unpack_from('<I',b,p)[0] for p in (0x20,0x28))
  b[off+addr-base]^=1
  return b
 def test_bad_gate_load(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutation(0x020D7C5C),False)
 def test_bad_retry_branch(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutation(0x020D7C64),False)
 def test_bad_first_call(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutation(0x020D78A4),False)
 def test_bad_second_call(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutation(0x020D7940),False)
 def test_bad_state_literal(self):
  with self.assertRaisesRegex(ValueError,'anchor'):audit.inspect(self.mutation(0x020D7C6C),False)
if __name__=='__main__':unittest.main()
