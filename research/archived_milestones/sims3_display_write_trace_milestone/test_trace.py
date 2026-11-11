import unittest
from trace_display_writes import decoded_access,is_branch
class DecodeTests(unittest.TestCase):
 def test_halfword_read_write(self):
  self.assertEqual(decoded_access(0xE1D100B0,1),('read','halfword',0))
  self.assertEqual(decoded_access(0xE1C100B0,1),('write','halfword',0))
 def test_word_read_write(self):
  self.assertEqual(decoded_access(0xE5921000,2),('read','word',0))
  self.assertEqual(decoded_access(0xE5820000,2),('write','word',0))
 def test_other_base(self):self.assertIsNone(decoded_access(0xE5820000,1))
 def test_branch(self):self.assertTrue(is_branch(0xEB000AFA))
if __name__=='__main__':unittest.main()
