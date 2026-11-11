import hashlib,struct,unittest
from pathlib import Path
from analyze import analyze,branch_target,ANCHORS,CALLS,SHA
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class TestRecordHandoff(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.b=ROM.read_bytes();cls.off=struct.unpack_from('<I',cls.b,0x30)[0]
 def test_sha(self):self.assertEqual(hashlib.sha256(self.b).hexdigest(),SHA)
 def test_all_opcode_anchors(self):self.assertEqual(analyze(self.b)['verified_opcodes'],len(ANCHORS))
 def test_all_direct_calls(self):self.assertEqual(analyze(self.b)['verified_calls'],3)
 def test_branch_decoder(self):
  self.assertEqual(branch_target(0xEB000079,0x0238C604),0x0238C7F0)
  self.assertIsNone(branch_target(0xE1A04000,0x0238C7F4))
 def test_record_fields(self):
  r=analyze(self.b);self.assertEqual(r['selected_case']['selector'],'[r4+8] at 0x0238C8BC');self.assertEqual(r['producer']['read_target'],'0x02385C68')
 def test_corrupt_instruction_rejected(self):
  b=bytearray(self.b);i=self.off+0x0238C5D0-0x02380000;b[i]^=1
  with self.assertRaisesRegex(ValueError,'Opcode differs'):analyze(b,strict=False)
 def test_corrupt_branch_rejected(self):
  b=bytearray(self.b);i=self.off+0x0238C604-0x02380000;b[i]^=1
  with self.assertRaisesRegex(ValueError,'Call differs'):analyze(b,strict=False)
 def test_wrong_rom_rejected(self):
  b=bytearray(self.b);b[-1]^=1
  with self.assertRaisesRegex(ValueError,'Unsupported ROM'):analyze(b)
if __name__=='__main__':unittest.main()
