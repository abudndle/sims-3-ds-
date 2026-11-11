import struct,unittest
from analyze import arm9_region,thumb_literal_target,arm_literal_target
class Test(unittest.TestCase):
    def test_rom_header(self):
        b=bytearray(0x1400);struct.pack_into('<IIII',b,0x20,0x200,0x02004800,0x02004000,0x1000)
        off,entry,base,arm=arm9_region(b)
        self.assertEqual((off,entry,base,len(arm)),(0x200,0x02004800,0x02004000,0x1000))
    def test_bad_bounds(self):
        b=bytearray(0x400);struct.pack_into('<IIII',b,0x20,0x200,0x02004800,0x02004000,0x2000)
        with self.assertRaises(ValueError):arm9_region(b)
    def test_thumb_literal(self):
        self.assertEqual(thumb_literal_target(0x02095C1A,0x480C),0x02095C4C)
    def test_thumb_nonliteral(self):self.assertIsNone(thumb_literal_target(0,0xBD10))
    def test_arm_literal(self):self.assertEqual(arm_literal_target(0x02000000,0xE59F2050),0x02000058)
    def test_arm_nonliteral(self):self.assertIsNone(arm_literal_target(0x02000000,0xE12FFF1E))
if __name__=='__main__':unittest.main()
