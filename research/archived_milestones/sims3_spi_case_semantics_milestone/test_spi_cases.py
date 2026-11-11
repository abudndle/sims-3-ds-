import hashlib,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import analyze_spi_cases as m
ROM=Path('/mnt/data/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds')
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=ROM.read_bytes()
        cls.off,cls.base,_=m.layout(cls.raw)
        cls.report=m.analyze_bytes(cls.raw)
    def patch_at(self,address,op):
        b=bytearray(self.raw)
        struct.pack_into('<I',b,self.off+address-self.base,op)
        return b
    def test_cases_six(self):
        self.assertEqual([r['case'] for r in self.report['decoded_cases']],list(range(4,10)))
    def test_set_and_clear_pairs(self):
        rows=self.report['decoded_cases']
        self.assertEqual([r['mask'] for r in rows],['0x04','0x04','0x08','0x08','0x0C','0x0C'])
        self.assertEqual([r['operation'] for r in rows],['set bits (OR)','clear bits (AND NOT)']*3)
    def test_wrappers(self):
        d={r['case']:r['wrapper'] for r in self.report['decoded_cases']}
        self.assertEqual([d[k] for k in (4,6,8)],['0x0238CAC8']*3)
        self.assertEqual([d[k] for k in (5,7,9)],['0x0238CAF0']*3)
    def test_changed_opcode_rejected(self):
        with self.assertRaises(ValueError):m.analyze_bytes(self.patch_at(0x0238CBB4,0xE3A00001))
    def test_changed_wrapper_rejected(self):
        with self.assertRaises(ValueError):m.analyze_bytes(self.patch_at(0x0238CADC,0))
    def test_changed_branch_rejected(self):
        with self.assertRaises(ValueError):m.analyze_bytes(self.patch_at(0x0238CBD0,0xEA000000))
    def test_invalid_header_rejected(self):
        with self.assertRaises(ValueError):m.analyze_bytes(b'bad')
    def test_hash(self):
        self.assertEqual(self.report['rom_sha256'],hashlib.sha256(self.raw).hexdigest())
if __name__=='__main__':unittest.main()
