import struct, unittest
from analyze_input_function import signed24, branch_target, analyze, ROUTINE_START, ROUTINE_END,KEY_LOAD,KEY_READ,LITERAL_ADDRESS
class Tests(unittest.TestCase):
    def test_sign_extension(self):
        self.assertEqual(signed24(0xffffff),-1)
        self.assertEqual(signed24(0x7fffff),0x7fffff)
    def test_branch_forward(self):
        self.assertEqual(branch_target(0x2001000,0xea000000),0x2001008)
    def test_branch_backward(self):
        self.assertEqual(branch_target(0x2001000,0xeafffffe),0x2001000)
    def test_nonbranch(self):
        self.assertIsNone(branch_target(0x2001000,0xe59f2050))
    def test_fixture(self):
        base=0x02004800; offset=0x4000
        length=LITERAL_ADDRESS-base+4
        rom=bytearray(offset+length)
        struct.pack_into('<III',rom,0x20,offset,base,length)
        for a,op in [(ROUTINE_START,0xe92d4070),(KEY_LOAD,0xe59f2050),(KEY_READ,0xe1d220b0),
                     (ROUTINE_END-8,0xe8bd4070),(ROUTINE_END-4,0xe12fff1e),(LITERAL_ADDRESS,0x04000130)]:
            struct.pack_into('<I',rom,offset+a-base,op)
        result=analyze(bytes(rom));self.assertEqual(result['function_bytes'],176)
    def test_reject_changed_code(self):
        base=0x02004800;offset=0x4000
        rom=bytearray(offset+LITERAL_ADDRESS-base+4)
        struct.pack_into('<III',rom,0x20,offset,base,len(rom)-offset)
        with self.assertRaises(ValueError):analyze(bytes(rom))
if __name__=='__main__':unittest.main()
