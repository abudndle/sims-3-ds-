import unittest,struct
from analyze import decode_arg,branch_target,analyze
class Tests(unittest.TestCase):
 def test_mov_constant(self):self.assertEqual(decode_arg(0xe3a00003,0),{'kind':'constant','value':3})
 def test_mov_zero(self):self.assertEqual(decode_arg(0xe3a00000,0)['value'],0)
 def test_mov_other_register(self):self.assertIsNone(decode_arg(0xe3a00003,1))
 def test_mov_register(self):self.assertEqual(decode_arg(0xe1a00005,0)['source'],'r5')
 def test_and_immediate(self):self.assertEqual(decode_arg(0xe20000ff,0)['mask'],255)
 def test_condition_rejection(self):self.assertIsNone(decode_arg(0x13a00003,0))
 def test_branch(self):self.assertEqual(branch_target(0xebffff57,0x0238ccf0),0x0238ca54)
 def test_wrong_branch(self):self.assertIsNone(branch_target(0xe3a00003,0))
 def test_bounds(self):
  data=bytearray(128);struct.pack_into('<III',data,0x30,100,0x02380000,400)
  with self.assertRaises(ValueError):analyze(data)
if __name__=='__main__':unittest.main()
