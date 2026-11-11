import os,struct,unittest
from pathlib import Path
import audit
class Decoder(unittest.TestCase):
    def test_arm_e4(self):self.assertEqual(audit.arm_immediate(0xe3a010e4),0xe4)
    def test_arm_d0(self):self.assertEqual(audit.arm_immediate(0xe3a010d0),0xd0)
    def test_non_mov(self):self.assertIsNone(audit.arm_immediate(0xe59f1000))
    def test_rotated_immediate(self):self.assertEqual(audit.arm_immediate(0xe3a00101),0x40000000)
class OriginalROM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.getenv("SIMS3_DS_ROM")
        if not path:raise unittest.SkipTest("SIMS3_DS_ROM unset")
        cls.rom=Path(path).read_bytes()
    def test_sites(self):
        h=audit.inspect(self.rom)["hits"]
        self.assertTrue(any(x["address"]=="0x0238E8D4" and x["value"]=="0xE4" for x in h))
        self.assertTrue(any(x["address"]=="0x0238E794" and x["value"]=="0xEC" for x in h))
    def test_reject_wrong_sha(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):audit.inspect(self.rom[:-1])
    def test_reject_bad_bounds(self):
        r=bytearray(self.rom);struct.pack_into("<I",r,0x38,0)
        with self.assertRaisesRegex(ValueError,"bounds"):audit.inspect(r,False)
    def test_corrupt_known_immediate(self):
        r=bytearray(self.rom);offset=struct.unpack_from("<I",r,0x30)[0]
        r[offset+0xE8D4]^=1
        h=audit.inspect(r,False)["hits"]
        self.assertFalse(any(x["address"]=="0x0238E8D4" and x["value"]=="0xE4" for x in h))
if __name__=="__main__":unittest.main()
