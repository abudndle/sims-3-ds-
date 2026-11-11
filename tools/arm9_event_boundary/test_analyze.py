import os,struct,unittest
from pathlib import Path
import analyze
class DecoderTests(unittest.TestCase):
 def test_zero(self):self.assertEqual(analyze.decode_fields(0),{'raw_x':0,'raw_y':0,'pen_down':0,'sample_status':0,'high5':0})
 def test_all_ones(self):self.assertEqual(analyze.decode_fields(0xffffffff),{'raw_x':4095,'raw_y':4095,'pen_down':1,'sample_status':3,'high5':31})
 def test_known_word(self):self.assertEqual(analyze.decode_fields((17<<27)|(2<<25)|(1<<24)|(0xabc<<12)|0x123),{'raw_x':0x123,'raw_y':0xabc,'pen_down':1,'sample_status':2,'high5':17})
 def test_reject_out_of_range(self):
  for v in (-1,2**32,True,1.0):
   with self.subTest(value=v),self.assertRaises(ValueError):analyze.decode_fields(v)
 def test_callback_register(self):self.assertEqual(analyze.branch_exchange_register(0xe12fff33),3)
 def test_bad_callback(self):
  with self.assertRaises(ValueError):analyze.branch_exchange_register(0xe12fff13)
 def test_shared_literal(self):self.assertEqual(analyze.literal_address(0xe59f1108,0x020d74ec),0x020d75fc)
 def test_bad_literal(self):
  with self.assertRaises(ValueError):analyze.literal_address(0,0)
class ROMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=os.getenv('SIMS3_DS_ROM')
  if not path:raise unittest.SkipTest('original VS3E ROM not available')
  cls.rom=Path(path).read_bytes()
 def test_original(self):
  r=analyze.inspect(self.rom);self.assertEqual(r['callback_pointer_offset'],4)
  self.assertEqual(r['verified_anchors'],len(analyze.ANCHORS))
 def test_wrong_hash(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):analyze.inspect(self.rom[:-1])
 def mutated(self,address):
  b=bytearray(self.rom);off=struct.unpack_from('<I',b,0x20)[0]
  base=struct.unpack_from('<I',b,0x28)[0];b[off+address-base]^=1;return b
 def test_modified_callback(self):
  with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.mutated(0x020d757c),False)
 def test_modified_struct_store(self):
  with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.mutated(0x020d7528),False)
 def test_modified_shared_literal(self):
  with self.assertRaisesRegex(ValueError,'anchor'):analyze.inspect(self.mutated(0x020d75fc),False)
if __name__=='__main__':unittest.main()
