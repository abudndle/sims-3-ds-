import os,struct,unittest
from pathlib import Path
import analyze
class Decode(unittest.TestCase):
    def test_branch1(self): self.assertEqual(analyze.branch_target(0xEBFFFF12,0x0238F7AC),0x0238F3FC)
    def test_branch2(self): self.assertEqual(analyze.branch_target(0xEBFFFF3D,0x0238F47C),0x0238F178)
    def test_ldr(self): self.assertEqual(analyze.literal_target(0xE59F50D8,0x0238F19C),0x0238F27C)
    def test_reject_not_branch(self):
        with self.assertRaises(ValueError):analyze.branch_target(0,0)
    def test_reject_not_ldr(self):
        with self.assertRaises(ValueError):analyze.literal_target(0,0)
class ROM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('SIMS3_DS_ROM'):raise unittest.SkipTest('SIMS3_DS_ROM unset')
        cls.rom=Path(os.environ['SIMS3_DS_ROM']).read_bytes()
    def test_original(self):self.assertEqual(analyze.inspect(self.rom)['verified_instruction_and_literal_anchors'],len(analyze.ANCHORS))
    def test_wrong_hash(self):
        with self.assertRaisesRegex(ValueError,'hash'):analyze.inspect(self.rom[:-1])
    def modified(self,address):
        r=bytearray(self.rom);off=struct.unpack_from('<I',r,0x30)[0];r[off+address-analyze.BASE]^=1;return r
    def test_bad_d8(self):
        with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.modified(0x0238F78C),False)
    def test_bad_bus(self):
        with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.modified(0x0238F27C),False)
    def test_bad_call(self):
        with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.modified(0x0238F47C),False)
if __name__=='__main__':unittest.main()
