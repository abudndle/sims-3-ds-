import os,struct,unittest
from pathlib import Path
import analyze
class DecoderTests(unittest.TestCase):
 def test_poll_branch(self):self.assertEqual(analyze.branch_target(0x0afffffa,0x020d7658),0x020d7648)
 def test_interrupt_state_check(self):self.assertEqual(analyze.branch_target(0xebfff85a,0x020d7650),0x020d57c0)
 def test_registration_call(self):self.assertEqual(analyze.branch_target(0xebfff842,0x020d7664),0x020d5774)
 def test_callback_literal(self):self.assertEqual(analyze.pc_literal_target(0xe59f100c,0x020d765c),0x020d7670)
 def test_table_literal(self):self.assertEqual(analyze.pc_literal_target(0xe59f102c,0x020d5784),0x020d57b8)
 def test_irq_table_slot(self):self.assertEqual(analyze.irq_table_address(0x0224e0d8,6),0x0224e0f0)
 def test_bad_branch(self):
  with self.assertRaises(ValueError):analyze.branch_target(0,0)
 def test_bad_literal(self):
  with self.assertRaises(ValueError):analyze.pc_literal_target(0,0)
 def test_bad_index(self):
  for index in (-1,32,True):
   with self.subTest(index=index),self.assertRaises(ValueError):analyze.irq_table_address(0x0224e0d8,index)
class OriginalROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.environ.get('SIMS3_DS_ROM')
  if not path:raise unittest.SkipTest('Original ROM unavailable to public CI')
  cls.rom=Path(path).read_bytes()
 def test_original(self):
  result=analyze.inspect(self.rom)
  self.assertEqual(result['verified_anchor_sites'],len(analyze.SITES))
  self.assertEqual(result['registered_handler'],'0x020d738c')
 def test_hash_guard(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):analyze.inspect(self.rom[:-1])
 def changed(self,address):
  raw=bytearray(self.rom)
  off,base=[struct.unpack_from('<I',raw,p)[0] for p in (0x20,0x28)]
  raw[off+address-base]^=1
  return raw
 def test_corrupt_handler_pointer(self):
  with self.assertRaisesRegex(ValueError,'mismatch'):analyze.inspect(self.changed(0x020d7670),False)
 def test_corrupt_table_store(self):
  with self.assertRaisesRegex(ValueError,'mismatch'):analyze.inspect(self.changed(0x020d578c),False)
 def test_corrupt_interrupt_index(self):
  with self.assertRaisesRegex(ValueError,'mismatch'):analyze.inspect(self.changed(0x020d7640),False)
 def test_corrupt_event_callback(self):
  with self.assertRaisesRegex(ValueError,'mismatch'):analyze.inspect(self.changed(0x020d757c),False)
if __name__=='__main__':unittest.main()
