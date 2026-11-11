import unittest
from trace import branch_target, mov_imm, trace

class TestTrace(unittest.TestCase):
    def test_forward_bl(self):
        self.assertEqual(branch_target(0xEB000000,0x100),0x108)
    def test_backward_bl(self):
        self.assertEqual(branch_target(0xEBFFFFFE,0x100),0x100)
    def test_non_bl(self):
        self.assertIsNone(branch_target(0xEA000000,0x100))
    def test_mov_r0(self):
        self.assertEqual(mov_imm(0xE3A00003),(0,3))
    def test_rotated_mov(self):
        self.assertEqual(mov_imm(0xE3A00C81),(0,0x8100))
    def test_mov_other_register(self):
        self.assertEqual(mov_imm(0xE3A01003),(1,3))
    def test_invalid_header(self):
        with self.assertRaises(ValueError):trace(b'abc')

if __name__=='__main__':unittest.main()
