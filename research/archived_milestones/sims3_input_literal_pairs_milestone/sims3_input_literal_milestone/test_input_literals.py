import struct, unittest
from analyze_input_literals import extract_arm9,literal_at,scan_range,KEYINPUT,SHARED_BUTTON_STATE

class Tests(unittest.TestCase):
    def test_thumb_literal_address(self):
        self.assertEqual(literal_at(0x02095C1A,0x480C),0x02095C4C)
    def test_other_opcode_rejected(self):
        self.assertIsNone(literal_at(0x02095C1A,0x8802))
    def test_bounds(self):
        rom=bytearray(0x400)
        struct.pack_into('<IIII',rom,0x20,0x200,0x02004000,0x02004000,0x100)
        base,data=extract_arm9(rom)
        self.assertEqual((base,len(data)),(0x02004000,0x100))
        with self.assertRaises(ValueError):scan_range(data,base,base-2,base+10)
    def test_header_rejects_bad_size(self):
        rom=bytearray(0x400)
        struct.pack_into('<IIII',rom,0x20,0x200,0x02004000,0x02004000,0x300)
        with self.assertRaises(ValueError):extract_arm9(rom)
    def test_two_literals_from_synthetic_code(self):
        code=bytearray(128)
        struct.pack_into('<HH',code,0,0x4803,0x4903)
        # PC+4=4, +12=16 and PC+4=4,+12=16 for both; use distinct imm on second
        struct.pack_into('<H',code,2,0x4904)
        struct.pack_into('<II',code,16,KEYINPUT,SHARED_BUTTON_STATE)
        rows=scan_range(code,0x2004000,0x2004000,0x2004004)
        self.assertEqual([r['value'] for r in rows],[f'0x{KEYINPUT:08X}',f'0x{SHARED_BUTTON_STATE:08X}'])
if __name__=='__main__':unittest.main()
